"""Directional Trend Index (DTI) -- William Blau.

A double-/triple-smoothed High-Low Momentum oscillator bounded to [-100, +100],
paired with an EMA signal line (the Ergodic form, Blau ch.7.3):

    dti_k    = 100 * TEMA(HLM, r, s, u) / TEMA(|HLM|, r, s, u)   (the oscillator)
    signal_k = EMA(dti, ul)_k                                    (ul-period EMA)

where the High-Low Momentum is built from how far the high rose and the low
fell relative to q-1 bars ago:

    HMU_k = max(High_k - High_(k-(q-1)), 0)      (upward high movement)
    LMD_k = max(Low_(k-(q-1)) - Low_k,  0)       (downward low movement)
    HLM_k = HMU_k - LMD_k                         (composite high-low momentum)
    TEMA(x, r, s, u) = EMA(EMA(EMA(x, r), s), u)  (triple EMA cascade)

This is the True Strength Index structure (see ../true-strength-index) applied
to HLM instead of price momentum. **Inputs are High and Low only** (no close).

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(dti, signal)`` and :func:`dti_series` returns two parallel lists.

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * Each EMA stage seeds on its first received value.
    * HLM is valid from bar q-1 (it needs a High/Low from q-1 bars ago), so all
      stages seed at bar q-1 together; DTI is NaN for bars 0..q-2 and finite
      from bar q-1 onward. For q=2 only bar 0 is NaN.
    * The signal EMA seeds on the first finite DTI (bar q-1), so the signal is
      ALSO NaN for bars 0..q-2; ul == 1 -> signal == dti (passthrough).
    * NOT the MQL5 begin-offset convention (which blanks more early bars).

Degenerate q=1: HLM == 0 on every bar (High_k - High_k = 0), so the denominator
is always 0 and the division guard yields DTI == 0.0 for all bars (no NaN).

Division guard: denominator == 0  ->  output 0.0 (matches Blau_DTI.mq5).

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math
from collections import deque, namedtuple


# ====================================================================== #
# EMBEDDED BUILDING BLOCK: Blau exponential moving average.               #
# Copied verbatim from core/exponential-moving-average. Inlined on        #
# purpose so each indicator is a standalone porting unit. Do NOT change   #
# its numerics -- see core/exponential-moving-average/description.md.     #
# ====================================================================== #
class ExponentialMovingAverage:
    """Stateful streaming EMA: alpha = 2/(period+1), seeds e_0 = x_0.

    period == 1 -> alpha == 1 -> pure passthrough (output == input).
    period  < 1 -> invalid.
    """

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period!r}")
        # Smoothing factor alpha = 2/(n+1); for n == 1 this is exactly 1.0.
        self._alpha: float = 2.0 / (float(period) + 1.0)
        self._prev: float = 0.0      # previous output e_(k-1); valid once primed
        self._primed: bool = False   # has the seed been applied yet?

    def update(self, x: float) -> float:
        if not self._primed:
            # Seed: first output equals first input (no NaN warm-up).
            self._prev = x
            self._primed = True
            return self._prev
        # Blend recursion (matches MQL5 FP op order): e = a*x + (1-a)*prev.
        e = self._alpha * x + (1.0 - self._alpha) * self._prev
        self._prev = e
        return e


# ====================================================================== #
# INDICATOR: Directional Trend Index (two-output: oscillator + signal).   #
# ====================================================================== #

# Two-output result. ``dti`` is the oscillator; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both share the same NaN warm-up region.
DtiResult = namedtuple("DtiResult", ["dti", "signal"])


class DirectionalTrendIndex:
    """Stateful, streaming Directional Trend Index with an EMA signal line.

    Feed one (high, low) pair at a time to :meth:`update`, which returns a
    :class:`DtiResult` ``(dti, signal)`` for that bar. Both fields are
    ``float('nan')`` while the q-bar look-back is not yet satisfied
    (bars 0..q-2), then finite -- ``dti`` in [-100, +100], ``signal`` its EMA.

    Example (q=2 one-bar HLM, all stages passthrough, ul=1 passthrough):
    >>> dti = DirectionalTrendIndex(q=2, r=1, s=1, u=1, ul=1)
    >>> import math
    >>> r0 = dti.update(10.0, 9.0); (math.isnan(r0.dti), math.isnan(r0.signal))
    (True, True)
    >>> r1 = dti.update(12.0, 11.0); (r1.dti, r1.signal)  # HMU=+2, LMD=0 -> +100
    (100.0, 100.0)
    >>> r2 = dti.update(11.0, 8.0); (r2.dti, r2.signal)   # HMU=0, LMD=3 -> -100
    (-100.0, -100.0)
    """

    def __init__(self, q: int = 2, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create a DTI with momentum look-back ``q``, EMA periods ``r,s,u`` and
        signal-line period ``ul``.

        Defaults are the MQL5 reference defaults (q=2, r=20, s=5, u=3) plus the
        Ergodic signal default ul=3. Set ``u=1`` for a double-smoothed DTI;
        set ``ul=1`` for a passthrough signal (signal == dti every bar).
        """
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        # r, s, u, ul are validated by the EMA constructors below.
        self._q = q

        # Rolling windows of recent highs and lows, just large enough to reach
        # back q-1 bars: holding q values means the oldest is *_(k-(q-1)).
        self._highs: deque[float] = deque(maxlen=q)
        self._lows: deque[float] = deque(maxlen=q)

        # Two independent 3-stage EMA cascades: one for signed HLM (numerator),
        # one for absolute HLM (denominator). Each is wired output -> input:
        # TEMA(x) = stage_u(stage_s(stage_r(x))).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the oscillator. Advanced ONLY on finite
        # oscillator values, so it seeds on the first finite DTI (bar q-1) and
        # shares the oscillator's NaN warm-up region.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, high: float, low: float) -> DtiResult:
        """Feed one bar's ``high``/``low``; return (dti, signal) for this bar."""
        self._highs.append(high)
        self._lows.append(low)

        # HLM needs a High/Low from q-1 bars ago. That is available only once
        # the windows hold q values; before then neither output is defined --
        # do NOT advance the signal EMA.
        if len(self._highs) < self._q:
            return DtiResult(float("nan"), float("nan"))

        # With a deque of maxlen q, the leftmost element is exactly the value
        # q-1 bars ago: High_(k-(q-1)) and Low_(k-(q-1)).
        prev_high = self._highs[0]
        prev_low = self._lows[0]

        # Upward high movement and downward low movement, each floored at 0.
        hmu = high - prev_high
        if hmu < 0.0:
            hmu = 0.0
        lmd = prev_low - low
        if lmd < 0.0:
            lmd = 0.0

        # Composite high-low momentum and its magnitude.
        hlm = hmu - lmd
        abs_hlm = abs(hlm)

        # Numerator cascade: TEMA(HLM, r, s, u).
        n = self._num_u.update(self._num_s.update(self._num_r.update(hlm)))
        # Denominator cascade: TEMA(|HLM|, r, s, u).
        d = self._den_u.update(self._den_s.update(self._den_r.update(abs_hlm)))

        # Division guard (Blau_DTI.mq5): denominator 0 -> oscillator 0.0.
        dti = 0.0 if d == 0.0 else 100.0 * n / d

        # Signal line = EMA(dti, ul); seeds here on the first finite oscillator.
        signal = self._signal_ema.update(dti)
        return DtiResult(dti, signal)


def dti_series(highs, lows, q=2, r=20, s=5, u=3, ul=3):
    """Convenience: run whole lists of highs/lows through a fresh DTI.

    Returns two parallel lists: ``(dti_values, signal_values)``.
    """
    dti = DirectionalTrendIndex(q=q, r=r, s=s, u=u, ul=ul)
    out = [dti.update(h, l) for h, l in zip(highs, lows)]
    return [o.dti for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_Q*_R*_S*_U*      #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig). The DTI consumes HIGH and LOW only (no      #
    # close), so both input series are embedded below (identical to          #
    # INPUT_HIGH / INPUT_LOW in the fixtures). Each language gets the same    #
    # numbers in its own idiomatic literal form, preceded by two comment      #
    # lines (what-it-tests + param values). NaN appears in the look-back      #
    # warm-up region (bars 0..q-2) and is emitted with each language's NaN    #
    # token. q=1 is degenerate: HLM == 0 every bar -> guard -> all 0.0.       #
    # ====================================================================== #

    INPUT_HIGH = [
        93.250000, 94.940000, 96.375000, 96.190000, 96.000000, 94.720000, 95.000000, 93.720000, 92.470000, 92.750000,
        96.250000, 99.625000, 99.125000, 92.750000, 91.315000, 93.250000, 93.405000, 90.655000, 91.970000, 92.250000,
        90.345000, 88.500000, 88.250000, 85.500000, 84.440000, 84.750000, 84.440000, 89.405000, 88.125000, 89.125000,
        87.155000, 87.250000, 87.375000, 88.970000, 90.000000, 89.845000, 86.970000, 85.940000, 84.750000, 85.470000,
        84.470000, 88.500000, 89.470000, 90.000000, 92.440000, 91.440000, 92.970000, 91.720000, 91.155000, 91.750000,
        90.000000, 88.875000, 89.000000, 85.250000, 83.815000, 85.250000, 86.625000, 87.940000, 89.375000, 90.625000,
        90.750000, 88.845000, 91.970000, 93.375000, 93.815000, 94.030000, 94.030000, 91.815000, 92.000000, 91.940000,
        89.750000, 88.750000, 86.155000, 84.875000, 85.940000, 99.375000, 103.280000, 105.375000, 107.625000, 105.250000,
        104.500000, 105.500000, 106.125000, 107.940000, 106.250000, 107.000000, 108.750000, 110.940000, 110.940000, 114.220000,
        123.000000, 121.750000, 119.815000, 120.315000, 119.375000, 118.190000, 116.690000, 115.345000, 113.000000, 118.315000,
        116.870000, 116.750000, 113.870000, 114.620000, 115.310000, 116.000000, 121.690000, 119.870000, 120.870000, 116.750000,
        116.500000, 116.000000, 118.310000, 121.500000, 122.000000, 121.440000, 125.750000, 127.750000, 124.190000, 124.440000,
        125.750000, 124.690000, 125.310000, 132.000000, 131.310000, 132.250000, 133.880000, 133.500000, 135.500000, 137.440000,
        138.690000, 139.190000, 138.500000, 138.130000, 137.500000, 138.880000, 132.130000, 129.750000, 128.500000, 125.440000,
        125.120000, 126.500000, 128.690000, 126.620000, 126.690000, 126.000000, 123.120000, 121.870000, 124.000000, 127.000000,
        124.440000, 122.500000, 123.750000, 123.810000, 124.500000, 127.870000, 128.560000, 129.630000, 124.870000, 124.370000,
        124.870000, 123.620000, 124.060000, 125.870000, 125.190000, 125.620000, 126.000000, 128.500000, 126.750000, 129.750000,
        132.690000, 133.940000, 136.500000, 137.690000, 135.560000, 133.560000, 135.000000, 132.380000, 131.440000, 130.880000,
        129.630000, 127.250000, 127.810000, 125.000000, 126.810000, 124.750000, 122.810000, 122.250000, 121.060000, 120.000000,
        123.250000, 122.750000, 119.190000, 115.060000, 116.690000, 114.870000, 110.870000, 107.250000, 108.870000, 109.000000,
        108.500000, 113.060000, 93.000000, 94.620000, 95.120000, 96.000000, 95.560000, 95.310000, 99.000000, 98.810000,
        96.810000, 95.940000, 94.440000, 92.940000, 93.940000, 95.500000, 97.060000, 97.500000, 96.250000, 96.370000,
        95.000000, 94.870000, 98.250000, 105.120000, 108.440000, 109.870000, 105.000000, 106.000000, 104.940000, 104.500000,
        104.440000, 106.310000, 112.870000, 116.500000, 119.190000, 121.000000, 122.120000, 111.940000, 112.750000, 110.190000,
        107.940000, 109.690000, 111.060000, 110.440000, 110.120000, 110.310000, 110.440000, 110.000000, 110.750000, 110.500000,
        110.500000, 109.500000,
    ]

    INPUT_LOW = [
        90.750000, 91.405000, 94.250000, 93.500000, 92.815000, 93.500000, 92.000000, 89.750000, 89.440000, 90.625000,
        92.750000, 96.315000, 96.030000, 88.815000, 86.750000, 90.940000, 88.905000, 88.780000, 89.250000, 89.750000,
        87.500000, 86.530000, 84.625000, 82.280000, 81.565000, 80.875000, 81.250000, 84.065000, 85.595000, 85.970000,
        84.405000, 85.095000, 85.500000, 85.530000, 87.875000, 86.565000, 84.655000, 83.250000, 82.565000, 83.440000,
        82.530000, 85.065000, 86.875000, 88.530000, 89.280000, 90.125000, 90.750000, 89.000000, 88.565000, 90.095000,
        89.000000, 86.470000, 84.000000, 83.315000, 82.000000, 83.250000, 84.750000, 85.280000, 87.190000, 88.440000,
        88.250000, 87.345000, 89.280000, 91.095000, 89.530000, 91.155000, 92.000000, 90.530000, 89.970000, 88.815000,
        86.750000, 85.065000, 82.030000, 81.500000, 82.565000, 96.345000, 96.470000, 101.155000, 104.250000, 101.750000,
        101.720000, 101.720000, 103.155000, 105.690000, 103.655000, 104.000000, 105.530000, 108.530000, 108.750000, 107.750000,
        117.000000, 118.000000, 116.000000, 118.500000, 116.530000, 116.250000, 114.595000, 110.875000, 110.500000, 110.720000,
        112.620000, 114.190000, 111.190000, 109.440000, 111.560000, 112.440000, 117.500000, 116.060000, 116.560000, 113.310000,
        112.560000, 114.000000, 114.750000, 118.870000, 119.000000, 119.750000, 122.620000, 123.000000, 121.750000, 121.560000,
        123.120000, 122.190000, 122.750000, 124.370000, 128.000000, 129.500000, 130.810000, 130.630000, 132.130000, 133.880000,
        135.380000, 135.750000, 136.190000, 134.500000, 135.380000, 133.690000, 126.060000, 126.870000, 123.500000, 122.620000,
        122.750000, 123.560000, 125.810000, 124.620000, 124.370000, 121.810000, 118.190000, 118.060000, 117.560000, 121.000000,
        121.120000, 118.940000, 119.810000, 121.000000, 122.000000, 124.500000, 126.560000, 123.500000, 121.250000, 121.060000,
        122.310000, 121.000000, 120.870000, 122.060000, 122.750000, 122.690000, 122.870000, 125.500000, 124.250000, 128.000000,
        128.380000, 130.690000, 131.630000, 134.380000, 132.000000, 131.940000, 131.940000, 129.560000, 123.750000, 126.000000,
        126.250000, 124.370000, 121.440000, 120.440000, 121.370000, 121.690000, 120.000000, 119.620000, 115.500000, 116.750000,
        119.060000, 119.060000, 115.060000, 111.060000, 113.120000, 110.000000, 105.000000, 104.690000, 103.870000, 104.690000,
        105.440000, 107.000000, 89.000000, 92.500000, 92.120000, 94.620000, 92.810000, 94.250000, 96.250000, 96.370000,
        93.690000, 93.500000, 90.000000, 90.190000, 90.500000, 92.120000, 94.120000, 94.870000, 93.000000, 93.870000,
        93.000000, 92.620000, 93.560000, 98.370000, 104.440000, 106.000000, 101.810000, 104.120000, 103.370000, 102.120000,
        102.250000, 103.370000, 107.940000, 112.500000, 115.440000, 115.500000, 112.250000, 107.560000, 106.560000, 106.870000,
        104.500000, 105.750000, 108.620000, 107.750000, 108.060000, 108.000000, 108.190000, 108.120000, 109.060000, 108.750000,
        108.560000, 106.620000,
    ]

    # Parameter combinations (q, r, s, u, what-it-tests). 16 combos -> 32 arrays
    # (each combo emits an oscillator and its ul=3 signal line), <=64 budget.
    COMBOS = [
        (2, 20, 5, 3, "MQL5 default DTI (q2,r20,s5,u3)."),
        (2, 25, 13, 1, "Book alternative, double-smoothed DTI(2,25,13)."),
        (2, 20, 5, 1, "Default look-back, double smoothing."),
        (2, 28, 28, 5, "DTI_Trade slow-trend filter params."),
        (2, 1, 1, 1, "All EMA stages passthrough -> sign(HLM)*100, 0 on flat."),
        (3, 20, 5, 3, "Look-back q=3; NaN bars 0..1."),
        (5, 20, 5, 3, "Look-back q=5; NaN bars 0..3."),
        (2, 13, 13, 1, "Equal double smoothing."),
        (2, 40, 20, 1, "Long second smoothing (r=40,s=20)."),
        (2, 5, 5, 5, "Equal triple smoothing, short periods."),
        (1, 20, 5, 3, "Degenerate q=1: HLM==0 every bar -> all 0.0 (guard)."),
        (10, 20, 5, 1, "Long look-back q=10; NaN bars 0..8."),
        (2, 9, 3, 1, "Fast double-smoothed DTI."),
        (2, 64, 64, 1, "Very slow double smoothing."),
        (4, 28, 28, 5, "Trade params with q=4 look-back."),
        (2, 7, 4, 2, "Fast triple smoothing."),
    ]

    # Signal-line EMA period for every emitted signal array (Ergodic default).
    UL = 3

    def fmt(x, nan_token):
        """Shortest round-tripping literal, or the language's NaN token."""
        if math.isnan(x):
            return nan_token
        return repr(float(x))

    def wrap(values, indent, nan_token, per_line=4):
        lines = []
        for i in range(0, len(values), per_line):
            chunk = ", ".join(fmt(v, nan_token) for v in values[i:i + per_line])
            lines.append(f"{indent}{chunk},")
        return "\n".join(lines)

    # Compute every series once. Each combo yields two arrays:
    #   * oscillator:  name 'Q{q}_R{r}_S{s}_U{u}'
    #   * signal line: name 'Q{q}_R{r}_S{s}_U{u}_SIG_UL3' (EMA of the osc, ul=3)
    # Stored as flat (array_name, description, param_string, values) tuples so
    # the five language emitters stay uniform.
    arrays = []
    for q, r, s, u, desc in COMBOS:
        osc, sig = dti_series(INPUT_HIGH, INPUT_LOW, q=q, r=r, s=s, u=u, ul=UL)
        base = f"Q{q}_R{r}_S{s}_U{u}"
        arrays.append((base, desc, f"q={q}, r={r}, s={s}, u={u}", osc))
        arrays.append((
            f"{base}_SIG_UL3",
            f"Signal line: EMA(oscillator, ul={UL}) of {base}.",
            f"q={q}, r={r}, s={s}, u={u}, ul={UL}",
            sig,
        ))

    # ---- Python: EXPECTED_<name> = [ ... ] (NaN -> float('nan')) ---------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"# {desc}\n# {prm}\n")
            f.write(f"EXPECTED_{nm} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expected<Name> = []float64{ ... } (NaN -> math.NaN()) ---- #
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"// {desc}\n// {prm}\n")
            f.write(f"var expected{nm} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expected<Name>: number[] = [ ... ] ------ #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"// {desc}\n// {prm}\n")
            f.write(f"export const expected{nm}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_<name>() -> Vec<f64> { vec![ ... ] } ------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"// {desc}\n// {prm}\n")
            f.write(f"pub fn expected_{nm.lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expected<Name>() [252]f64 { return .{ ... }; } ------- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"// {desc}\n// {prm}\n")
            f.write(f"pub fn expected{nm}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(arrays)} arrays x 5 languages "
          f"({len(INPUT_HIGH)} values each).")
