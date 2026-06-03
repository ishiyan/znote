"""Ergodic Oscillator -- William Blau.

The Ergodic oscillator is the True Strength Index together with a signal line:

    ergodic_k = TSI(q, r, s, u)_k                    (the TSI oscillator)
    signal_k  = EMA(ergodic, ul)_k                   (ul-period EMA of it)

It is a TWO-output indicator: each update() returns a named tuple
(ergodic, signal).

Both the TSI and the EMA primitive are **embedded** (inlined) below so this file
is a self-contained porting unit. Do NOT change their numerics -- see
../true-strength-index/description.md and
../core/exponential-moving-average/description.md.

Priming -- BOOK / EasyLanguage (Option B), see description.md §2:
    * Oscillator = TSI: NaN for bars 0..q-2, finite from bar q-1.
    * Signal EMA seeds on the first valid oscillator value (bar q-1), so the
      signal is ALSO NaN for bars 0..q-2 and finite from bar q-1.
    * ul == 1 -> signal is a passthrough -> signal == ergodic for every bar.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math
from collections import deque, namedtuple


# ====================================================================== #
# EMBEDDED BUILDING BLOCK: Blau exponential moving average.               #
# Copied verbatim from core/exponential-moving-average. Inlined so each   #
# indicator is a standalone porting unit. Do NOT change its numerics.     #
# ====================================================================== #
class ExponentialMovingAverage:
    """Stateful streaming EMA: alpha = 2/(period+1), seeds e_0 = x_0.

    period == 1 -> alpha == 1 -> pure passthrough (output == input).
    period  < 1 -> invalid.
    """

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period!r}")
        self._alpha: float = 2.0 / (float(period) + 1.0)
        self._prev: float = 0.0
        self._primed: bool = False

    def update(self, x: float) -> float:
        if not self._primed:
            self._prev = x
            self._primed = True
            return self._prev
        e = self._alpha * x + (1.0 - self._alpha) * self._prev
        self._prev = e
        return e


# ====================================================================== #
# EMBEDDED INDICATOR: True Strength Index (the Ergodic oscillator output). #
# Copied verbatim from true-strength-index. Do NOT change its numerics.    #
# ====================================================================== #
class TrueStrengthIndex:
    """Streaming TSI: 100 * TEMA(mtm, r,s,u) / TEMA(|mtm|, r,s,u).

    NaN for bars 0..q-2 (momentum look-back), finite from bar q-1.
    Denominator 0 -> output 0.0.
    """

    def __init__(self, q: int = 2, r: int = 20, s: int = 5, u: int = 3) -> None:
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        self._q = q
        self._history: deque[float] = deque(maxlen=q)
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

    def update(self, price: float) -> float:
        self._history.append(price)
        if len(self._history) < self._q:
            return float("nan")
        mtm = price - self._history[0]
        abs_mtm = abs(mtm)
        n = self._num_u.update(self._num_s.update(self._num_r.update(mtm)))
        d = self._den_u.update(self._den_s.update(self._den_r.update(abs_mtm)))
        if d == 0.0:
            return 0.0
        return 100.0 * n / d


# ====================================================================== #
# INDICATOR: Ergodic Oscillator.                                         #
# ====================================================================== #

# Two-output result. ``ergodic`` is the TSI oscillator; ``signal`` is its
# ul-period EMA. Both share the same NaN warm-up region.
ErgodicResult = namedtuple("ErgodicResult", ["ergodic", "signal"])


class ErgodicOscillator:
    """Stateful, streaming Ergodic oscillator (TSI + signal line).

    Feed one close at a time to :meth:`update`; it returns an
    :class:`ErgodicResult` ``(ergodic, signal)``. Both fields are NaN while the
    momentum look-back is unmet (bars 0..q-2), then finite.

    Example (q=2, all stages passthrough, signal passthrough -> +/-100 both):
    >>> erg = ErgodicOscillator(q=2, r=1, s=1, u=1, ul=1)
    >>> import math
    >>> r0 = erg.update(10.0); (math.isnan(r0.ergodic), math.isnan(r0.signal))
    (True, True)
    >>> r1 = erg.update(12.0); (r1.ergodic, r1.signal)   # mtm=+2 -> +100, ul=1
    (100.0, 100.0)
    """

    def __init__(self, q: int = 2, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create an Ergodic with TSI params ``q,r,s,u`` and signal period ``ul``."""
        # The oscillator is the TSI; the signal line is an EMA of it.
        self._tsi = TrueStrengthIndex(q=q, r=r, s=s, u=u)
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, price: float) -> ErgodicResult:
        """Feed one close ``price``; return (ergodic, signal) for this bar."""
        ergodic = self._tsi.update(price)

        # While the oscillator is not primed, the signal is undefined too, and
        # we must NOT advance the signal EMA (it should seed on the first valid
        # oscillator value, bar q-1).
        if math.isnan(ergodic):
            return ErgodicResult(float("nan"), float("nan"))

        signal = self._signal_ema.update(ergodic)
        return ErgodicResult(ergodic, signal)


def ergodic_series(values, q=2, r=20, s=5, u=3, ul=3):
    """Convenience: run closes through a fresh Ergodic.

    Returns two parallel lists: (ergodic_values, signal_values).
    """
    erg = ErgodicOscillator(q=q, r=r, s=s, u=u, ul=ul)
    out = [erg.update(v) for v in values]
    return [o.ergodic for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_ERG_* / _SIG_*   #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig). The Ergodic has TWO outputs, so every       #
    # parameter combination yields two arrays: the oscillator (ERG) and its   #
    # signal line (SIG). Each language gets the same numbers in its own       #
    # idiomatic literal form, preceded by two comment lines (what-it-tests +  #
    # param values). NaN appears in the momentum warm-up region (bars         #
    # 0..q-2) for BOTH outputs and is emitted with each language's NaN token. #
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

    # Parameter combinations (q, r, s, u, ul, what-it-tests). 14 combos x 2
    # outputs = 28 arrays, within the <=64 budget.
    COMBOS = [
        (2, 20, 5, 3, 3, "MQL5 default Ergodic (q2,r20,s5,u3) with 3-bar signal."),
        (2, 32, 5, 1, 5, "Book Ergodic(close,32,5), Fig 2-14, 5-bar signal."),
        (2, 20, 5, 1, 5, "Ergodic base r=20 double-smoothed, 5-bar signal."),
        (2, 32, 5, 1, 7, "Ch-03 Deutsche mark variant: 7-bar signal line."),
        (2, 25, 13, 1, 5, "Book headline TSI(25,13) as Ergodic, 5-bar signal."),
        (2, 20, 5, 3, 1, "ul=1 invariant: signal MUST equal ergodic exactly."),
        (2, 1, 1, 1, 1, "All-passthrough: ergodic = sign(mtm)*100; signal == ergodic."),
        (2, 20, 5, 3, 9, "Long 9-bar signal smoothing."),
        (2, 64, 64, 1, 5, "Slow TSI(64,64) Ergodic, 5-bar signal."),
        (2, 9, 3, 1, 3, "Fast double smoothing, 3-bar signal."),
        (3, 20, 5, 3, 3, "Momentum q=3 (2-bar look-back); both outputs NaN bars 0..1."),
        (5, 20, 5, 3, 5, "Momentum q=5 (4-bar look-back); both outputs NaN bars 0..3."),
        (2, 13, 7, 1, 7, "Fast double smoothing with long 7-bar signal."),
        (2, 20, 5, 1, 3, "Double-smoothed Ergodic, 3-bar signal."),
    ]

    def name(q, r, s, u, ul):
        """Param shortcut, e.g. (2,20,5,3,3) -> 'Q2_R20_S5_U3_L3' (ul -> L)."""
        return f"Q{q}_R{r}_S{s}_U{u}_L{ul}"

    def params(q, r, s, u, ul):
        return f"q={q}, r={r}, s={s}, u={u}, ul={ul}"

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

    # Compute both series once per combo. ``outputs`` is a flat list of records
    # carrying everything each emitter needs:
    #   (kind_upper, kind_camel, kind_snake, label, shortcut, paramline, vals)
    # where kind is ERG (oscillator) or SIG (signal line).
    outputs = []
    for q, r, s, u, ul, desc in COMBOS:
        erg_vals, sig_vals = ergodic_series(INPUT_CLOSE, q=q, r=r, s=s, u=u, ul=ul)
        sc = name(q, r, s, u, ul)
        pl = params(q, r, s, u, ul)
        outputs.append(("ERG", "Erg", "erg", f"Ergodic oscillator: {desc}", sc, pl, erg_vals))
        outputs.append(("SIG", "Sig", "sig", f"Signal line: {desc}", sc, pl, sig_vals))

    # ---- Python: EXPECTED_ERG_<name> / EXPECTED_SIG_<name> = [ ... ] ------ #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"# {label}\n# {pl}\n")
            f.write(f"EXPECTED_{ku}_{sc} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expectedErg<Name> / expectedSig<Name> = []float64{ ... } - #
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"var expected{kc}{sc} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expectedErg<Name> / expectedSig<Name> --- #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"export const expected{kc}{sc}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_erg_<name>() / expected_sig_<name>() ------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"pub fn expected_{ks}_{sc.lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expectedErg<Name>() / expectedSig<Name>() [252]f64 --- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"pub fn expected{kc}{sc}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(outputs)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each, {len(COMBOS)} combos x 2 outputs).")
