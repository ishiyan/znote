"""True Strength Index (TSI) -- William Blau.

A double-/triple-smoothed momentum oscillator bounded to [-100, +100], paired
with an EMA signal line (the Ergodic form, Blau ch.1.4):

    tsi_k    = 100 * TEMA(mtm, r, s, u) / TEMA(|mtm|, r, s, u)   (the oscillator)
    signal_k = EMA(tsi, ul)_k                                    (ul-period EMA)

where
    mtm_k             = C_k - C_(k-(q-1))                  (q-period momentum)
    TEMA(x, r, s, u)  = EMA(EMA(EMA(x, r), s), u)          (triple EMA cascade)

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(tsi, signal)`` and :func:`tsi_series` returns two parallel lists.

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * Each EMA stage seeds on its first received value.
    * Momentum is valid from bar q-1, so all stages seed at bar q-1 together;
      TSI is NaN for bars 0..q-2 and finite from bar q-1 onward.
    * The signal EMA seeds on the first finite TSI (bar q-1), so the signal is
      ALSO NaN for bars 0..q-2 and finite from bar q-1; ul == 1 -> signal is a
      passthrough -> signal == tsi for every bar.
    * Order-independent: TSI(q,r,s,u) == TSI(q,s,r,u) == ... (Blau, ch.2).
    * NOT the MQL5 begin-offset convention (which blanks more early bars).

Division guard: denominator == 0  ->  output 0.0 (matches Blau_TSI.mq5).

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
# INDICATOR: True Strength Index (two-output: oscillator + signal line).  #
# ====================================================================== #

# Two-output result. ``tsi`` is the oscillator; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both share the same NaN warm-up region.
TsiResult = namedtuple("TsiResult", ["tsi", "signal"])


class TrueStrengthIndex:
    """Stateful, streaming True Strength Index with an EMA signal line.

    Feed one price (close) at a time to :meth:`update`, which returns a
    :class:`TsiResult` ``(tsi, signal)`` for that bar. Both fields are
    ``float('nan')`` while the momentum look-back is not yet satisfied
    (bars 0..q-2), then finite -- ``tsi`` in [-100, +100], ``signal`` its EMA.

    Example (q=2 one-bar momentum, all stages passthrough, ul=1 passthrough):
    >>> tsi = TrueStrengthIndex(q=2, r=1, s=1, u=1, ul=1)
    >>> import math
    >>> r0 = tsi.update(10.0); (math.isnan(r0.tsi), math.isnan(r0.signal))
    (True, True)
    >>> r1 = tsi.update(12.0); (r1.tsi, r1.signal)   # mtm=+2 -> +100, ul=1
    (100.0, 100.0)
    >>> r2 = tsi.update(11.0); (r2.tsi, r2.signal)   # mtm=-1 -> -100, ul=1
    (-100.0, -100.0)
    """

    def __init__(self, q: int = 2, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create a TSI with momentum period ``q``, EMA periods ``r,s,u`` and
        signal-line period ``ul``.

        Defaults are the MQL5 reference defaults (q=2, r=20, s=5, u=3) plus the
        Ergodic signal default ul=3. Set ``u=1`` for the book's classic
        double-smoothed TSI(close, r, s); set ``ul=1`` for a passthrough signal
        (signal == tsi every bar).
        """
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        # r, s, u, ul are validated by the EMA constructors below.
        self._q = q

        # Rolling window of recent prices, just large enough to reach back
        # q-1 bars: holding q prices means the oldest is C_(k-(q-1)).
        self._history: deque[float] = deque(maxlen=q)

        # Two independent 3-stage EMA cascades: one for signed momentum
        # (numerator), one for absolute momentum (denominator). Each is wired
        # output -> input: TEMA(x) = stage_u(stage_s(stage_r(x))).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the oscillator. It is advanced ONLY on
        # finite oscillator values, so it seeds on the first finite TSI (bar
        # q-1) and shares the oscillator's NaN warm-up region.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, price: float) -> TsiResult:
        """Feed one close ``price``; return (tsi, signal) for this bar."""
        self._history.append(price)

        # Momentum needs a price from q-1 bars ago. That is available only once
        # the window holds q prices; before then the indicator is not primed
        # and neither output is defined -- do NOT advance the signal EMA.
        if len(self._history) < self._q:
            return TsiResult(float("nan"), float("nan"))

        # mtm_k = C_k - C_(k-(q-1)). With a deque of maxlen q, the leftmost
        # element is exactly C_(k-(q-1)).
        mtm = price - self._history[0]
        abs_mtm = abs(mtm)

        # Numerator cascade: TEMA(mtm, r, s, u).
        n = self._num_u.update(self._num_s.update(self._num_r.update(mtm)))
        # Denominator cascade: TEMA(|mtm|, r, s, u).
        d = self._den_u.update(self._den_s.update(self._den_r.update(abs_mtm)))

        # Division guard (Blau_TSI.mq5): denominator 0 -> oscillator 0.0.
        tsi = 0.0 if d == 0.0 else 100.0 * n / d

        # Signal line = EMA(tsi, ul); seeds here on the first finite oscillator.
        signal = self._signal_ema.update(tsi)
        return TsiResult(tsi, signal)


def tsi_series(values, q=2, r=20, s=5, u=3, ul=3):
    """Convenience: run a whole list of closes through a fresh TSI.

    Returns two parallel lists: ``(tsi_values, signal_values)``.
    """
    tsi = TrueStrengthIndex(q=q, r=r, s=s, u=u, ul=ul)
    out = [tsi.update(v) for v in values]
    return [o.tsi for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_Q*_R*_S*_U*      #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig). Each language gets the same numbers in its  #
    # own idiomatic literal form, preceded by two comment lines              #
    # (what-it-tests + param values). NaN appears in the momentum warm-up     #
    # region (bars 0..q-2) and is emitted with each language's NaN token.     #
    # ====================================================================== #

    # 252 daily closes -- identical to INPUT_CLOSE / testInput / test_input in
    # the fixtures. Embedded so the generator needs no imports.
    INPUT_CLOSE = [
        91.500000, 94.815000, 94.375000, 95.095000, 93.780000, 94.625000, 92.530000, 92.750000, 90.315000, 92.470000,
        96.125000, 97.250000, 98.500000, 89.875000, 91.000000, 92.815000, 89.155000, 89.345000, 91.625000, 89.875000,
        88.375000, 87.625000, 84.780000, 83.000000, 83.500000, 81.375000, 84.440000, 89.250000, 86.375000, 86.250000,
        85.250000, 87.125000, 85.815000, 88.970000, 88.470000, 86.875000, 86.815000, 84.875000, 84.190000, 83.875000,
        83.375000, 85.500000, 89.190000, 89.440000, 91.095000, 90.750000, 91.440000, 89.000000, 91.000000, 90.500000,
        89.030000, 88.815000, 84.280000, 83.500000, 82.690000, 84.750000, 85.655000, 86.190000, 88.940000, 89.280000,
        88.625000, 88.500000, 91.970000, 91.500000, 93.250000, 93.500000, 93.155000, 91.720000, 90.000000, 89.690000,
        88.875000, 85.190000, 83.375000, 84.875000, 85.940000, 97.250000, 99.875000, 104.940000, 106.000000, 102.500000,
        102.405000, 104.595000, 106.125000, 106.000000, 106.065000, 104.625000, 108.625000, 109.315000, 110.500000, 112.750000,
        123.000000, 119.625000, 118.750000, 119.250000, 117.940000, 116.440000, 115.190000, 111.875000, 110.595000, 118.125000,
        116.000000, 116.000000, 112.000000, 113.750000, 112.940000, 116.000000, 120.500000, 116.620000, 117.000000, 115.250000,
        114.310000, 115.500000, 115.870000, 120.690000, 120.190000, 120.750000, 124.750000, 123.370000, 122.940000, 122.560000,
        123.120000, 122.560000, 124.620000, 129.250000, 131.000000, 132.250000, 131.000000, 132.810000, 134.000000, 137.380000,
        137.810000, 137.880000, 137.250000, 136.310000, 136.250000, 134.630000, 128.250000, 129.000000, 123.870000, 124.810000,
        123.000000, 126.250000, 128.380000, 125.370000, 125.690000, 122.250000, 119.370000, 118.500000, 123.190000, 123.500000,
        122.190000, 119.310000, 123.310000, 121.120000, 123.370000, 127.370000, 128.500000, 123.870000, 122.940000, 121.750000,
        124.440000, 122.000000, 122.370000, 122.940000, 124.000000, 123.190000, 124.560000, 127.250000, 125.870000, 128.860000,
        132.000000, 130.750000, 134.750000, 135.000000, 132.380000, 133.310000, 131.940000, 130.000000, 125.370000, 130.130000,
        127.120000, 125.190000, 122.000000, 125.000000, 123.000000, 123.500000, 120.060000, 121.000000, 117.750000, 119.870000,
        122.000000, 119.190000, 116.370000, 113.500000, 114.250000, 110.000000, 105.060000, 107.000000, 107.870000, 107.000000,
        107.120000, 107.000000, 91.000000, 93.940000, 93.870000, 95.500000, 93.000000, 94.940000, 98.250000, 96.750000,
        94.810000, 94.370000, 91.560000, 90.250000, 93.940000, 93.620000, 97.000000, 95.000000, 95.870000, 94.060000,
        94.620000, 93.750000, 98.000000, 103.940000, 107.870000, 106.060000, 104.500000, 105.000000, 104.190000, 103.060000,
        103.420000, 105.270000, 111.870000, 116.000000, 116.620000, 118.280000, 113.370000, 109.000000, 109.700000, 109.250000,
        107.000000, 109.190000, 110.000000, 109.200000, 110.120000, 108.000000, 108.620000, 109.750000, 109.810000, 109.000000,
        108.750000, 107.870000,
    ]

    # Parameter combinations (q, r, s, u, what-it-tests). 18 combos; each yields
    # TWO arrays (oscillator + ul=3 signal line) -> 36 arrays, <=64 budget.
    COMBOS = [
        (2, 20, 5, 3, "MQL5 default triple smoothing."),
        (2, 25, 13, 1, "Book headline TSI(close,25,13), Fig 2-1 (double smoothing)."),
        (2, 20, 5, 1, "Double-smoothed; Ergodic base with r=20."),
        (2, 32, 5, 1, "Ergodic oscillator base TSI(close,32,5)."),
        (2, 13, 13, 1, "Equal double smoothing '13,13' (book)."),
        (2, 20, 40, 1, "Long second smoothing '20,40' (book)."),
        (2, 40, 20, 1, "Order-independence pair with (2,20,40,1); equal up to FP rounding."),
        (2, 64, 64, 1, "Slow TSI trend TSI(close,64,64), Fig 2-16."),
        (2, 100, 5, 1, "Long first smoothing (proxy-for-price)."),
        (2, 1, 1, 1, "All-passthrough: TSI = sign(mtm)*100, 0.0 at flat bars (division guard)."),
        (2, 1, 5, 3, "First-stage passthrough (r=1)."),
        (2, 20, 1, 1, "Single smoothing (s=u=1), the Divergence-Indicator shape."),
        (2, 5, 5, 5, "Equal triple smoothing."),
        (3, 20, 5, 3, "Momentum period q=3 (2-bar look-back); NaN bars 0..1."),
        (5, 20, 5, 3, "Momentum period q=5 (4-bar look-back); NaN bars 0..3."),
        (10, 20, 5, 1, "Momentum period q=10 (9-bar look-back); NaN bars 0..8."),
        (2, 9, 3, 1, "Fast double smoothing."),
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
        osc, sig = tsi_series(INPUT_CLOSE, q=q, r=r, s=s, u=u, ul=UL)
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
          f"({len(INPUT_CLOSE)} values each).")
