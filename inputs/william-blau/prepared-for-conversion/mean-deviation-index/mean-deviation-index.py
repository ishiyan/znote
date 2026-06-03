"""Mean Deviation Index (MDI) -- William Blau (book ch. 5 / Appendix B-11).

A detrended, double-/triple-smoothed momentum line in **raw price units**,
paired with an EMA signal line (the Ergodic form, Blau ch. 5):

    md_k     = price_k - EMA(price, r)_k                  (deviation from trend)
    mdi_k    = EMA(EMA(md, s), u)_k                       (the MDI line)
    signal_k = EMA(mdi, ul)_k                             (ul-period EMA)

The price series is **detrended** by subtracting its own ``r``-period EMA, then
the deviation is smoothed by an ``s``-period EMA and an optional ``u``-period
EMA. This is Blau's Mean Deviation Index exactly as defined in the book
(ch. 5: ``MDI(close, r, s) = EMA(close - EMA(close, r), s)``) and the MQL5
``Blau_MDI.mq5`` code (which adds the third smoothing ``u``). Blau notes the MDI
**approximates the MACD** when ``r`` is long and ``s`` is short.

**It is NOT normalized.** There is no ``100 * TEMA/TEMA`` ratio and no fixed
range: the output is in the same price units as the input (like a MACD line),
and can take any sign or magnitude. **Input is a single price series (Close).**

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(mdi, signal)`` and :func:`mdi_series` returns two parallel lists.

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming: the detrending EMA is defined from bar 0, so there is NO NaN warm-up
region. Bar 0 is exactly ``0.0`` (``md_0 = price_0 - price_0 = 0``, and both
smoothing EMAs seed on that 0). The signal line likewise seeds on bar 0's MDI.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math
from collections import namedtuple


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
# INDICATOR: Mean Deviation Index (two-output: line + signal).            #
# ====================================================================== #

# Two-output result. ``mdi`` is the MDI line; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both are finite from bar 0 (no NaN warm-up)
# and both are in raw price units (NOT bounded to any range).
MdiResult = namedtuple("MdiResult", ["mdi", "signal"])


class MeanDeviationIndex:
    """Stateful, streaming Mean Deviation Index with an EMA signal line.

    Feed one price (close) at a time to :meth:`update`, which returns an
    :class:`MdiResult` ``(mdi, signal)`` for that bar. Both fields are finite
    from bar 0 and in **raw price units** -- ``mdi`` the detrended,
    double-smoothed deviation, ``signal`` its ul-period EMA. There is no NaN
    warm-up region (the detrending EMA is defined from bar 0).

    Example (baseline passthrough r=1 -> md == 0 every bar -> all 0.0):
    >>> mdi = MeanDeviationIndex(r=1, s=5, u=3, ul=3)
    >>> [round(mdi.update(p).mdi, 4) for p in (10.0, 12.0, 11.0)]
    [0.0, 0.0, 0.0]

    Example (r=2 baseline, smoothing passthrough s=u=1, ul=1 passthrough ->
    mdi == price - EMA(price, 2)):
    >>> mdi = MeanDeviationIndex(r=2, s=1, u=1, ul=1)
    >>> o0 = mdi.update(10.0); (round(o0.mdi, 4), round(o0.signal, 4))  # bar 0
    (0.0, 0.0)
    >>> o1 = mdi.update(13.0); (round(o1.mdi, 4), round(o1.signal, 4))  # 13-12
    (1.0, 1.0)
    """

    def __init__(self, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create an MDI with detrend/EMA periods ``r`` (baseline), ``s`` (1st
        deviation smoothing), ``u`` (2nd deviation smoothing) and signal-line
        period ``ul``.

        Defaults are the MQL5/book defaults (r=20, s=5, u=3) plus the Ergodic
        signal default ul=3. Set ``u=1`` for the book's pure double-smoothed
        form ``EMA(price - EMA(price, r), s)``; set ``ul=1`` for a passthrough
        signal (signal == mdi every bar).
        """
        # r, s, u, ul are validated by the EMA constructors below.

        # The detrending trend: a single EMA(r) applied to price. md = price - this.
        self._trend = ExponentialMovingAverage(r)

        # Two chained EMAs smoothing the deviation: EMA(EMA(md, s), u).
        self._smooth_s = ExponentialMovingAverage(s)
        self._smooth_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the MDI line. The line is finite from
        # bar 0, so this seeds on bar 0 -- no NaN warm-up.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, price: float) -> MdiResult:
        """Feed one close ``price``; return (mdi, signal) for this bar."""
        # Mean deviation: price minus its own r-period EMA trend.
        md = price - self._trend.update(price)

        # Smooth the deviation: EMA(EMA(md, s), u). No normalization, no guard.
        mdi = self._smooth_u.update(self._smooth_s.update(md))

        # Signal line = EMA(mdi, ul); seeds on bar 0's MDI value.
        signal = self._signal_ema.update(mdi)
        return MdiResult(mdi, signal)


def mdi_series(values, r=20, s=5, u=3, ul=3):
    """Convenience: run a whole list of prices through a fresh MDI.

    Returns two parallel lists: ``(mdi_values, signal_values)``.
    """
    mdi = MeanDeviationIndex(r=r, s=s, u=u, ul=ul)
    out = [mdi.update(v) for v in values]
    return [o.mdi for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_R*_S*_U*         #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig). The MDI consumes a single CLOSE series, so  #
    # only INPUT_CLOSE is embedded below (identical to INPUT_CLOSE in the     #
    # fixtures). Each language gets the same numbers in its own idiomatic      #
    # literal form, preceded by two comment lines (what-it-tests + params).   #
    # There is NO NaN warm-up region (the detrending EMA is defined from bar  #
    # 0), so every value is finite -- but the output is UNNORMALIZED (raw     #
    # price units, any sign/magnitude), so values may be negative. The Go     #
    # fixture still needs no "math" import (no NaN ever appears).             #
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

    # Parameter combinations (r, s, u, what-it-tests). 16 combos -> 32 arrays
    # (each combo emits an MDI line and its ul=3 signal line), <=64 budget.
    # r is the DETRENDING EMA (baseline); s, u smooth the deviation. There is
    # no separate momentum period q -- the book/MQL5 MDI has none.
    COMBOS = [
        (20, 5, 3, "Catalog/MQL5 default MDI (r20,s5,u3)."),
        (20, 5, 1, "Book pure double smoothing (u=1): EMA(price-EMA(price,r),s)."),
        (1, 5, 3, "Degenerate r=1: detrend passthrough -> md==0 -> all 0.0."),
        (40, 5, 3, "Long detrend (MACD-like), triple smoothing."),
        (10, 5, 3, "Short detrend, triple smoothing."),
        (5, 5, 5, "Short equal detrend/triple smoothing."),
        (20, 9, 1, "Default detrend, fast double smoothing."),
        (26, 12, 9, "MACD-style periods, triple smoothing."),
        (50, 13, 1, "Very long detrend, double smoothing."),
        (30, 5, 3, "Long detrend, triple smoothing."),
        (3, 3, 3, "Tiny everything."),
        (7, 4, 2, "Fast detrend + fast triple smoothing."),
        (2, 5, 3, "Minimal real detrend (r=2)."),
        (20, 1, 1, "Default detrend, single-EMA smoothing of md."),
        (20, 20, 5, "Equal detrend/first smoothing."),
        (60, 30, 10, "Very long everything (deep detrend)."),
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
    #   * MDI line:    name 'R{r}_S{s}_U{u}'
    #   * signal line: name 'R{r}_S{s}_U{u}_SIG_UL3' (EMA of the line, ul=3)
    # Stored as flat (array_name, description, param_string, values) tuples so
    # the five language emitters stay uniform. MDI has no NaN warm-up, so every
    # value (line and signal) is finite (though unnormalized / possibly < 0).
    arrays = []
    for r, s, u, desc in COMBOS:
        osc, sig = mdi_series(INPUT_CLOSE, r=r, s=s, u=u, ul=UL)
        base = f"R{r}_S{s}_U{u}"
        arrays.append((base, desc, f"r={r}, s={s}, u={u}", osc))
        arrays.append((
            f"{base}_SIG_UL3",
            f"Signal line: EMA(MDI line, ul={UL}) of {base}.",
            f"r={r}, s={s}, u={u}, ul={UL}",
            sig,
        ))

    # ---- Python: EXPECTED_<name> = [ ... ] -------------------------------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"# {desc}\n# {prm}\n")
            f.write(f"EXPECTED_{nm} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expected<Name> = []float64{ ... } ----------------------- #
    # (No NaN appears, so no "math" import is needed in the Go fixture.)
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
