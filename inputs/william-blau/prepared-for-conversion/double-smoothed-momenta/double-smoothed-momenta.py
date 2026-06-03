"""Double-Smoothed Momenta (DM) / Double-Smoothed RSI (DRSI) -- William Blau.

A close-based, double-smoothed momentum oscillator bounded to [0, 100]:

    LCa_k = min(Close over the last a bars)          (lowest close)
    HCa_k = max(Close over the last a bars)          (highest close)
    st_k  = Close_k - LCa_k                           (close above the low close)
    rng_k = HCa_k - LCa_k                             (a-bar close range)

    DM(a, y, z) = 100 * EMA(EMA(st, y), z) / EMA(EMA(rng, y), z)

i.e. each of the numerator (st) and denominator (rng) series is double-smoothed
by an inner EMA of period ``y`` then an outer EMA of period ``z`` (Blau's
Ez(Ey(.)) ), and the ratio is scaled by 100.

This is structurally the Double-Smoothed Stochastic (DS-Stochastic) computed on
the CLOSE -- it uses the highest/lowest *close* over ``a`` bars instead of the
high/low of the bar -- and it has NO signal line (single output per bar).

Two named instances (catalog Group 10):
    * RSI equivalence:  DM(2, 1, z) == RSI(z), the EMA-form RSI (see below).
    * Double-smoothed RSI:  DRSI(y, z) = DM(2, y, z).

> **RSI convention.** The equivalence DM(2,1,z) == RSI(z) holds for the *EMA-form*
> RSI built from this library's EMA (alpha = 2/(z+1)), NOT Wilder's classic RSI
> (which uses RMA smoothing, alpha = 1/z). Proof: with a = 2, st = Close -
> min(Close, Close[1]) = max(0, Close - Close[1]) = the up-move, and rng = |Close
> - Close[1]| = up-move + down-move. With y = 1 the inner EMA is a passthrough, so
> DM(2,1,z) = 100*EMA(up, z)/EMA(up+dn, z). Because the EMA is linear,
> EMA(up)+EMA(dn) = EMA(up+dn), hence this equals 100*EMA(up,z)/(EMA(up,z)+
> EMA(dn,z)) = the EMA-form RSI(z).

The EMA primitive is **embedded** below (inlined, not imported) so this file is a
self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * st/rng are valid once a closes exist (bar a-1); all four EMA stages seed
      there. DM is NaN for bars 0..a-2, finite from bar a-1.
    * For a == 1 there is no NaN warm-up (but the a-bar close range is then always
      0, so DM is 0.0 on every bar via the guard -- a degenerate setting).

Division guard: EMA(EMA(rng)) <= 0 -> DM = 0.0 (mirrors the DS-Stochastic guard).

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math
from collections import deque


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
# INDICATOR: Double-Smoothed Momenta.                                     #
# ====================================================================== #
class DoubleSmoothedMomenta:
    """Stateful, streaming Double-Smoothed Momenta (DM).

    Feed one ``close`` at a time to :meth:`update`, which returns the DM value
    for that bar -- ``float('nan')`` while the a-bar look-back is unmet
    (bars 0..a-2), then a finite value in [0, 100].

    Example (a=2, y=1, z=1 -> DM is 100 when the close rose, else 0 -- the
    one-bar up/flat/down indicator; note DM(2,1,z) == EMA-form RSI(z)):
    >>> dm = DoubleSmoothedMomenta(a=2, y=1, z=1)
    >>> import math
    >>> math.isnan(dm.update(10.0))   # bar 0: a-bar window not yet full -> NaN
    True
    >>> dm.update(12.0)               # rose 10->12: up-move -> 100
    100.0
    >>> dm.update(11.0)               # fell 12->11: no up-move -> 0
    0.0
    >>> dm.update(11.0)               # flat: range 0 -> guard -> 0
    0.0
    """

    def __init__(self, a: int = 2, y: int = 2, z: int = 14) -> None:
        """Create a DM with close look-back ``a`` and EMA periods ``y`` (inner), ``z`` (outer).

        Defaults a=2, y=2, z=14 (a mildly double-smoothed RSI-14). The special
        case ``a=2, y=1`` reproduces the EMA-form RSI(z); ``DRSI(y, z)`` is
        ``DM(2, y, z)`` (see :func:`drsi_series`).
        """
        if a < 1:
            raise ValueError(f"a must be >= 1, got {a!r}")
        # y, z are validated by the EMA constructors below.
        self._a = a

        # Rolling window of the last a closes (for highest/lowest close).
        self._closes: deque[float] = deque(maxlen=a)

        # Two independent 2-stage EMA cascades (double smoothing), each wired
        # inner(y) -> outer(z): EMA(EMA(x, y), z).
        self._num_y = ExponentialMovingAverage(y)
        self._num_z = ExponentialMovingAverage(z)
        self._den_y = ExponentialMovingAverage(y)
        self._den_z = ExponentialMovingAverage(z)

    def update(self, close: float) -> float:
        """Feed one ``close`` and return this bar's DM (or NaN during warm-up)."""
        self._closes.append(close)

        # Need a closes before the highest/lowest close is defined. While
        # unprimed, the EMA cascades must NOT advance (they seed at bar a-1).
        if len(self._closes) < self._a:
            return float("nan")

        # Highest/lowest close over the last a bars.
        hc = max(self._closes)
        lc = min(self._closes)

        # Raw close-above-low (>= 0) and a-bar close range (>= 0).
        st = close - lc
        rng = hc - lc

        # Double-smooth each separately (inner y, then outer z), then divide.
        num = self._num_z.update(self._num_y.update(st))
        den = self._den_z.update(self._den_y.update(rng))

        # Division guard: smoothed range <= 0 -> DM = 0.0.
        return 0.0 if den <= 0.0 else 100.0 * num / den


def dm_series(closes, a=2, y=2, z=14):
    """Convenience: run a whole list of closes through a fresh DM."""
    dm = DoubleSmoothedMomenta(a=a, y=y, z=z)
    return [dm.update(c) for c in closes]


def drsi_series(closes, y=2, z=14):
    """Double-Smoothed RSI: DRSI(y, z) = DM(2, y, z) (fixes the look-back a=2)."""
    return dm_series(closes, a=2, y=y, z=z)


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_A*_Y*_Z*         #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig).                                            #
    #                                                                         #
    # DM is close-only. We embed the Close series below (identical to         #
    # INPUT_CLOSE / testInput in the fixtures, bit-for-bit). For any a >= 2   #
    # there is a NaN warm-up region of bars 0..a-2 (a single NaN at bar 0     #
    # for the headline a=2), so the Go fixture DOES need an `import "math"`.   #
    # All finite values are bounded to [0, 100].                              #
    # ====================================================================== #

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

    # Parameter combinations (a, y, z, what-it-tests). 16 arrays, <=64 budget.
    # a = highest/lowest close look-back; y = inner EMA; z = outer EMA.
    COMBOS = [
        (2, 2, 14, "DRSI(2,14) default = DM(2,2,14): double-smoothed RSI-14."),
        (2, 1, 14, "DM(2,1,14) = EMA-form RSI(14) (RSI-equivalence invariant)."),
        (2, 1, 9, "DM(2,1,9) = EMA-form RSI(9)."),
        (2, 1, 2, "DM(2,1,2) = fast EMA-form RSI(2)."),
        (2, 3, 9, "DRSI(3,9): inner-3 outer-9 double-smoothed RSI."),
        (2, 5, 5, "DRSI(5,5): equal inner/outer smoothing."),
        (2, 2, 5, "DRSI(2,5): light, faster double-smoothed RSI."),
        (2, 1, 1, "DM(2,1,1): one-bar up/flat passthrough (100 if rose else 0)."),
        (1, 1, 1, "a=1 degenerate: 1-bar close range is 0 -> guard -> all 0.0."),
        (5, 2, 14, "DM(5,2,14): double-smoothed stochastic of the close, a=5."),
        (10, 3, 5, "DM(10,3,5): stochastic of the close, a=10."),
        (14, 2, 9, "DM(14,2,9): stochastic of the close, a=14."),
        (20, 5, 3, "DM(20,5,3): slow stochastic of the close, a=20."),
        (3, 3, 3, "DM(3,3,3): tiny triple-ish look-back/smoothing."),
        (7, 4, 2, "DM(7,4,2): fast small look-back."),
        (32, 2, 7, "DM(32,2,7): long look-back, lightly double-smoothed."),
    ]

    def name(a, y, z):
        """Param shortcut, e.g. (2,2,14) -> 'A2_Y2_Z14'."""
        return f"A{a}_Y{y}_Z{z}"

    def params(a, y, z):
        return f"a={a}, y={y}, z={z}"

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

    # Compute all series once.
    results = [
        (a, y, z, desc, dm_series(INPUT_CLOSE, a=a, y=y, z=z))
        for (a, y, z, desc) in COMBOS
    ]

    # ---- Python: EXPECTED_<name> = [ ... ] -------------------------------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for a, y, z, desc, vals in results:
            f.write(f"# {desc}\n# {params(a,y,z)}\n")
            f.write(f"EXPECTED_{name(a,y,z)} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expected<Name> = []float64{ ... } ----------------------- #
    # (a>=2 produces NaN, so the Go fixture imports "math".)
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for a, y, z, desc, vals in results:
            f.write(f"// {desc}\n// {params(a,y,z)}\n")
            f.write(f"var expected{name(a,y,z)} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expected<Name>: number[] = [ ... ] ------ #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for a, y, z, desc, vals in results:
            f.write(f"// {desc}\n// {params(a,y,z)}\n")
            f.write(f"export const expected{name(a,y,z)}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_<name>() -> Vec<f64> { vec![ ... ] } ------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for a, y, z, desc, vals in results:
            f.write(f"// {desc}\n// {params(a,y,z)}\n")
            f.write(f"pub fn expected_{name(a,y,z).lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expected<Name>() [252]f64 { return .{ ... }; } ------- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for a, y, z, desc, vals in results:
            f.write(f"// {desc}\n// {params(a,y,z)}\n")
            f.write(f"pub fn expected{name(a,y,z)}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(results)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each).")
