"""Tick Volume Indicator (TVI) -- William Blau (book Ch. 4 / Ch. 10).

A normalized, double-/triple-smoothed oscillator built from the balance of
upticks vs downticks inside each high-low bar, bounded to [-100, +100]:

    TVI(r, s, u) = 100 * (TEMA(up, r, s, u) - TEMA(down, r, s, u))
                       / (TEMA(up, r, s, u) + TEMA(down, r, s, u))

where
    TEMA(x, r, s, u) = EMA(EMA(EMA(x, r), s), u)          (triple EMA cascade)

The TVI is gap-immune: it is built from intra-bar tick direction, not from the
close vs a previous close, so opening gaps do not bias it.

  * u = 1 recovers Blau's book double-smoothed TVI(r, s), because EMA(.,1) is a
    passthrough so TEMA(x, r, s, 1) = DEMA(x, r, s) = EMA(EMA(x, r), s). The
    default is u = 1; Chapter 10's TVI_Trade uses TVI(32, 32, 5).
  * By linearity of the EMA, TEMA(up) +/- TEMA(down) = TEMA(up +/- down), so this
    separate-cascade form equals Blau's alternate "double EMA of the difference
    over double EMA of the sum" form.

INPUTS: two non-negative per-bar series, ``upticks`` and ``downticks`` (counts of
up/down ticks within the bar). The shared test fixtures supply a deterministic
SYNTHETIC proxy derived from the bar range -- up = close - low, down = high -
close -- because the 252-bar dataset has no real tick data. A production caller
passes genuine tick counts.

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

There is NO NaN warm-up region (the EMAs seed at bar 0). Division guard:
denominator == 0 (a fully flat market) -> output 0.0.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math


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
# INDICATOR: Tick Volume Indicator.                                       #
# ====================================================================== #
class TickVolumeIndicator:
    """Stateful, streaming Tick Volume Indicator.

    Feed one (upticks, downticks) pair at a time to :meth:`update`, which returns
    the TVI value for that bar -- a finite value in [-100, +100]. There is no NaN
    warm-up region (both cascades seed at bar 0).

    Example (all stages passthrough -> raw normalized tick balance):
    >>> tvi = TickVolumeIndicator(r=1, s=1, u=1)
    >>> tvi.update(8.0, 2.0)    # 8 up vs 2 down: 100*(8-2)/(8+2) = 60
    60.0
    >>> tvi.update(0.0, 5.0)    # all down: 100*(0-5)/(0+5) = -100
    -100.0
    >>> tvi.update(0.0, 0.0)    # flat market: denominator 0 -> guard -> 0.0
    0.0
    """

    def __init__(self, r: int = 12, s: int = 12, u: int = 1) -> None:
        """Create a TVI with EMA periods ``r, s, u`` (book defaults 12,12,1).

        ``u = 1`` (default) gives the book double-smoothed TVI(r, s); set
        ``u`` > 1 for the Chapter-10 triple-smoothed form, e.g. TVI(32, 32, 5).
        """
        # r, s, u are validated by the EMA constructors below.

        # Two independent 3-stage EMA cascades: one for upticks, one for
        # downticks. Each is wired output -> input:
        # TEMA(x) = stage_u(stage_s(stage_r(x))).
        self._up_r = ExponentialMovingAverage(r)
        self._up_s = ExponentialMovingAverage(s)
        self._up_u = ExponentialMovingAverage(u)
        self._dn_r = ExponentialMovingAverage(r)
        self._dn_s = ExponentialMovingAverage(s)
        self._dn_u = ExponentialMovingAverage(u)

    def update(self, upticks: float, downticks: float) -> float:
        """Feed this bar's ``upticks``/``downticks`` and return this bar's TVI."""
        # Smooth each tick stream through its own TEMA cascade.
        tu = self._up_u.update(self._up_s.update(self._up_r.update(upticks)))
        td = self._dn_u.update(self._dn_s.update(self._dn_r.update(downticks)))

        den = tu + td
        # Division guard (Appendix B): fully flat smoothed volume -> output 0.0.
        if den == 0.0:
            return 0.0
        return 100.0 * (tu - td) / den


def tvi_series(upticks, downticks, r=12, s=12, u=1):
    """Convenience: run aligned uptick/downtick lists through a fresh TVI."""
    tvi = TickVolumeIndicator(r=r, s=s, u=u)
    return [tvi.update(up, dn) for up, dn in zip(upticks, downticks)]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_R*_S*_U*         #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig).                                            #
    #                                                                         #
    # The TVI consumes upticks/downticks. The shared 252-bar dataset has no   #
    # real tick data, so we use the documented SYNTHETIC proxy derived from   #
    # the bar range: up = close - low, down = high - close. We embed the      #
    # High/Low/Close series below (identical to INPUT_HIGH/INPUT_LOW/         #
    # INPUT_CLOSE in the fixtures) and derive up/down -- which reproduces      #
    # INPUT_UPTICKS / INPUT_DOWNTICKS in the fixtures bit-for-bit. There is    #
    # NO NaN warm-up region (the EMAs seed at bar 0) and no flat bars in this  #
    # dataset, so every value is finite and bounded to [-100, 100]; the Go    #
    # fixture needs no "math" import.                                          #
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

    # Synthetic tick proxy (documented): up = close - low, down = high - close.
    # This reproduces INPUT_UPTICKS / INPUT_DOWNTICKS in the fixtures bit-for-bit.
    INPUT_UPTICKS = [c - l for c, l in zip(INPUT_CLOSE, INPUT_LOW)]
    INPUT_DOWNTICKS = [h - c for h, c in zip(INPUT_HIGH, INPUT_CLOSE)]

    # Parameter combinations (r, s, u, what-it-tests). 16 arrays, <=64 budget.
    COMBOS = [
        (12, 12, 1, "Book double-smoothed default TVI(12,12) (u=1 -> DEMA)."),
        (25, 13, 1, "Alternate book double-smoothed TVI(25,13)."),
        (32, 32, 5, "Chapter-10 triple-smoothed TVI(32,32,5) (TVI_Trade base)."),
        (1, 1, 1, "All stages passthrough -> raw normalized tick balance."),
        (32, 5, 1, "Ergodic_TVI base TVI(32,5)."),
        (12, 12, 5, "Double 12,12 with triple noise-cleanup u=5."),
        (20, 5, 3, "Triple-smoothed TVI."),
        (5, 5, 5, "Equal short triple smoothing."),
        (32, 32, 1, "Double-smoothed slow TVI(32,32)."),
        (10, 10, 1, "Double-smoothed medium TVI(10,10)."),
        (50, 25, 1, "Very slow double smoothing."),
        (12, 26, 9, "MACD-style periods, triple."),
        (3, 3, 3, "Tiny triple smoothing."),
        (7, 4, 2, "Fast triple smoothing."),
        (64, 1, 1, "Long first EMA then passthrough."),
        (12, 12, 3, "Double 12,12 with triple u=3."),
    ]

    def name(r, s, u):
        """Param shortcut, e.g. (12,12,1) -> 'R12_S12_U1'."""
        return f"R{r}_S{s}_U{u}"

    def params(r, s, u):
        return f"r={r}, s={s}, u={u}"

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
        (r, s, u, desc, tvi_series(INPUT_UPTICKS, INPUT_DOWNTICKS, r=r, s=s, u=u))
        for (r, s, u, desc) in COMBOS
    ]

    # ---- Python: EXPECTED_<name> = [ ... ] -------------------------------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for r, s, u, desc, vals in results:
            f.write(f"# {desc}\n# {params(r,s,u)}\n")
            f.write(f"EXPECTED_{name(r,s,u)} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expected<Name> = []float64{ ... } ----------------------- #
    # (No NaN appears, so no "math" import is needed in the Go fixture.)
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for r, s, u, desc, vals in results:
            f.write(f"// {desc}\n// {params(r,s,u)}\n")
            f.write(f"var expected{name(r,s,u)} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expected<Name>: number[] = [ ... ] ------ #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for r, s, u, desc, vals in results:
            f.write(f"// {desc}\n// {params(r,s,u)}\n")
            f.write(f"export const expected{name(r,s,u)}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_<name>() -> Vec<f64> { vec![ ... ] } ------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for r, s, u, desc, vals in results:
            f.write(f"// {desc}\n// {params(r,s,u)}\n")
            f.write(f"pub fn expected_{name(r,s,u).lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expected<Name>() [252]f64 { return .{ ... }; } ------- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for r, s, u, desc, vals in results:
            f.write(f"// {desc}\n// {params(r,s,u)}\n")
            f.write(f"pub fn expected{name(r,s,u)}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(results)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each).")
