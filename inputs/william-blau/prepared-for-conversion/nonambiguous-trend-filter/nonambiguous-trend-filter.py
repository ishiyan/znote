"""Nonambiguous Trend Filter (`_Trade`) -- William Blau (book Ch. 8 / Appendix B).

A generic post-processing transform applied to any normalized, signed oscillator
X (TSI, SMI, DTI, MDI, CMI, CSI, ...). It keeps X only where its sign and slope
agree, and zeroes every ambiguous bar:

    X_Trade[k] = X[k]   if  X[k] > 0  AND  X[k] - X[k-1] > 0    (positive & rising)
               = X[k]   if  X[k] < 0  AND  X[k] - X[k-1] < 0    (negative & falling)
               = 0      otherwise                               (ambiguous)

The nonzero stretches of X_Trade correspond one-to-one with genuine up/down
trends; congestion and flat regions are blanked to zero. This is Blau's
EasyLanguage user function (Appendix B, Figures B-20..B-23); there is no MQL5
version.

The filter holds NO embedded moving averages -- it operates purely on the value
stream of a base indicator (which it does not need to know anything about). It is
therefore a tiny, base-agnostic, self-contained porting unit: a porting agent
needs only this file and ``description.md``.

Conventions (Option B, consistent with the rest of the library):
  * First finite bar  -> no prior slope -> output 0.0 (cannot confirm trend).
  * NaN base value    -> output NaN, and state is NOT updated (the base is still
                         in its own look-back warm-up; e.g. SMI/DTI bars 0..q-2).
  * Strict slope: a flat step (delta == 0) is neither rising nor falling -> 0.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math


# ====================================================================== #
# FILTER: Nonambiguous Trend Filter (the `_Trade` transform).             #
# ====================================================================== #
class NonambiguousTrendFilter:
    """Stateful, streaming `_Trade` filter over a base oscillator's values.

    Feed one base indicator value at a time to :meth:`update`. The filter returns
    the value unchanged where it is positive-and-rising or negative-and-falling,
    and 0.0 otherwise. A NaN input (base still warming up) yields NaN and leaves
    the filter state untouched.

    Example (a small signed ramp): seed bar -> 0.0, then keep rising-positive and
    falling-negative, zero the ambiguous bars.
    >>> f = NonambiguousTrendFilter()
    >>> [f.update(x) for x in (10.0, 20.0, 15.0, -5.0, -12.0, -3.0)]
    [0.0, 20.0, 0.0, -5.0, -12.0, 0.0]

    Example (NaN warm-up is propagated, then the first finite bar seeds at 0.0):
    >>> import math
    >>> f = NonambiguousTrendFilter()
    >>> out = [f.update(x) for x in (float('nan'), float('nan'), 5.0, 9.0)]
    >>> math.isnan(out[0]) and math.isnan(out[1])
    True
    >>> out[2:]
    [0.0, 9.0]
    """

    def __init__(self) -> None:
        # Last finite base value seen, and whether we have seen one yet. Using a
        # (prev, primed) pair (rather than None) keeps the port to Go/Rust/Zig
        # trivial -- there is no nullable float to model.
        self._prev: float = 0.0
        self._primed: bool = False

    def update(self, x: float) -> float:
        """Feed one base indicator value ``x``; return the filtered value."""
        # NaN test via the portable idiom ``x != x`` (true only for NaN). The
        # base is undefined here (still in its look-back warm-up): emit NaN and
        # do NOT advance the slope state, so the first finite bar afterwards is
        # treated as the seed.
        if x != x:
            return float("nan")

        if not self._primed:
            # First finite value: there is no prior bar, so the slope is
            # undefined -> cannot confirm a trend -> 0.0. Seed the state.
            self._prev = x
            self._primed = True
            return 0.0

        # Slope of the base relative to the previous finite bar.
        delta = x - self._prev
        self._prev = x

        # Retain only the two unambiguous cases; zero everything else.
        if x > 0.0 and delta > 0.0:
            return x          # positive and rising
        if x < 0.0 and delta < 0.0:
            return x          # negative and falling
        return 0.0            # ambiguous / flat / congestion


def trade_filter_series(values):
    """Convenience: run a whole list of base indicator values through a filter."""
    f = NonambiguousTrendFilter()
    return [f.update(v) for v in values]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_<BASE>_<PARAMS>  #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig).                                            #
    #                                                                         #
    # The `_Trade` filter is base-agnostic, so to produce realistic test     #
    # data we COMPOSE it with six real base indicators (TSI, SMI, DTI, MDI,   #
    # CMI, CSI). Rather than re-type those indicators here, we dynamically    #
    # import their already-prepared implementations from the sibling folders  #
    # and reuse their `*_series` functions verbatim -- guaranteeing the       #
    # composed expected values match exactly what a porting agent gets by     #
    # feeding the ported base indicator's output through the ported filter.   #
    #                                                                         #
    # Inputs: Open/High/Low/Close (all four series are embedded below,        #
    # identical to INPUT_OPEN/INPUT_HIGH/INPUT_LOW/INPUT_CLOSE in the         #
    # fixtures). NaN DOES appear (SMI's q=32 and DTI's q=2 look-back warm-up  #
    # regions are propagated by the filter), so the Go fixture carries        #
    # `import "math"`.                                                        #
    # ====================================================================== #
    import importlib.util
    import os

    HERE = os.path.dirname(os.path.abspath(__file__))
    SIB = os.path.dirname(HERE)  # prepared-for-conversion/

    def _load(folder, modname):
        """Import a sibling prepared indicator module by file path."""
        path = os.path.join(SIB, folder, folder + ".py")
        spec = importlib.util.spec_from_file_location(modname, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    tsi_mod = _load("true-strength-index", "base_tsi")
    smi_mod = _load("stochastic-momentum-index", "base_smi")
    dti_mod = _load("directional-trend-index", "base_dti")
    mdi_mod = _load("mean-deviation-index", "base_mdi")
    cmi_mod = _load("candlestick-momentum-index", "base_cmi")
    csi_mod = _load("candlestick-strength-index", "base_csi")
    tvi_mod = _load("tick-volume-indicator", "base_tvi")

    INPUT_OPEN = [
        92.500000, 91.500000, 95.155000, 93.970000, 95.500000, 94.500000, 95.000000, 91.500000, 91.815000, 91.125000,
        93.875000, 97.500000, 98.815000, 92.000000, 91.125000, 91.875000, 93.405000, 89.750000, 89.345000, 92.250000,
        89.780000, 87.940000, 87.595000, 85.220000, 83.500000, 83.500000, 81.250000, 85.125000, 88.125000, 87.500000,
        85.250000, 86.000000, 87.190000, 86.125000, 89.000000, 88.625000, 86.000000, 85.500000, 84.750000, 85.250000,
        84.250000, 86.750000, 86.940000, 89.315000, 89.940000, 90.815000, 91.190000, 91.345000, 89.595000, 91.000000,
        89.750000, 88.750000, 88.315000, 84.345000, 83.500000, 84.000000, 86.000000, 85.530000, 87.500000, 88.500000,
        90.000000, 88.655000, 89.500000, 91.565000, 92.000000, 93.000000, 92.815000, 91.750000, 92.000000, 91.375000,
        89.750000, 88.750000, 85.440000, 83.500000, 84.875000, 98.625000, 96.690000, 102.375000, 106.000000, 104.625000,
        102.500000, 104.250000, 104.000000, 106.125000, 106.065000, 105.940000, 105.625000, 108.625000, 110.250000, 110.565000,
        117.000000, 120.750000, 118.000000, 119.125000, 119.125000, 117.815000, 116.375000, 115.155000, 111.250000, 111.500000,
        116.690000, 116.000000, 113.620000, 111.750000, 114.560000, 113.620000, 118.120000, 119.870000, 116.620000, 115.870000,
        115.060000, 115.870000, 117.500000, 119.870000, 119.250000, 120.190000, 122.870000, 123.870000, 122.250000, 123.120000,
        123.310000, 124.000000, 123.000000, 124.810000, 130.000000, 130.880000, 132.500000, 131.000000, 132.500000, 134.000000,
        137.440000, 135.750000, 138.310000, 138.000000, 136.380000, 136.500000, 132.000000, 127.500000, 127.620000, 124.000000,
        123.620000, 125.000000, 126.370000, 126.250000, 125.940000, 124.000000, 122.750000, 120.000000, 120.000000, 122.000000,
        123.620000, 121.500000, 120.120000, 123.750000, 122.750000, 125.000000, 128.500000, 128.380000, 123.870000, 124.370000,
        122.750000, 123.370000, 122.000000, 122.620000, 125.000000, 124.250000, 124.370000, 125.620000, 126.500000, 128.380000,
        128.880000, 131.500000, 132.500000, 137.500000, 134.630000, 132.000000, 134.000000, 132.000000, 131.380000, 126.500000,
        128.750000, 127.190000, 127.500000, 120.500000, 126.620000, 123.000000, 122.060000, 121.000000, 121.000000, 118.000000,
        122.000000, 122.250000, 119.120000, 115.000000, 113.500000, 114.000000, 110.810000, 106.500000, 106.440000, 108.000000,
        107.000000, 108.620000, 93.000000, 93.750000, 94.250000, 94.870000, 95.500000, 94.500000, 97.000000, 98.500000,
        96.750000, 95.870000, 94.440000, 92.750000, 90.500000, 95.060000, 94.620000, 97.500000, 96.000000, 96.000000,
        94.620000, 94.870000, 94.000000, 99.000000, 105.500000, 108.810000, 105.000000, 105.940000, 104.940000, 103.690000,
        102.560000, 103.440000, 109.810000, 113.000000, 117.000000, 116.250000, 120.500000, 111.620000, 108.120000, 110.190000,
        107.750000, 108.000000, 110.690000, 109.060000, 108.500000, 109.870000, 109.120000, 109.690000, 109.560000, 110.440000,
        109.690000, 109.190000,
    ]

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

    # Each entry: (array_name, description, params_str, filtered_values).
    # The base series is computed by the imported reference implementation, then
    # passed through THIS file's NonambiguousTrendFilter.
    results = []

    def add(name, desc, params, base_vals):
        results.append((name, desc, params, trade_filter_series(base_vals)))

    # ---- TSI_Trade (base TSI on Close; book momentum q=2) ----------------- #
    for (r, s, u) in [(32, 13, 3), (20, 5, 3), (40, 20, 5)]:
        add(f"TSI_R{r}_S{s}_U{u}",
            f"TSI_Trade: filter over TSI(close,q2,r{r},s{s},u{u}).",
            f"base=TSI q=2, r={r}, s={s}, u={u}",
            tsi_mod.tsi_series(INPUT_CLOSE, q=2, r=r, s=s, u=u)[0])

    # ---- SMI_Trade (base SMI on H/L/C) ------------------------------------ #
    for (q, r, s, u) in [(32, 64, 7, 1), (5, 20, 5, 3), (13, 25, 2, 1)]:
        add(f"SMI_Q{q}_R{r}_S{s}_U{u}",
            f"SMI_Trade: filter over SMI(q{q},r{r},s{s},u{u}); NaN warm-up 0..{q-2}.",
            f"base=SMI q={q}, r={r}, s={s}, u={u}",
            smi_mod.smi_series(INPUT_HIGH, INPUT_LOW, INPUT_CLOSE, q=q, r=r, s=s, u=u)[0])

    # ---- DTI_Trade (base DTI on H/L; book momentum q=2) ------------------- #
    for (q, r, s, u) in [(2, 28, 28, 5), (2, 20, 5, 3), (4, 14, 14, 3)]:
        add(f"DTI_Q{q}_R{r}_S{s}_U{u}",
            f"DTI_Trade: filter over DTI(q{q},r{r},s{s},u{u}); NaN warm-up 0..{q-2}.",
            f"base=DTI q={q}, r={r}, s={s}, u={u}",
            dti_mod.dti_series(INPUT_HIGH, INPUT_LOW, q=q, r=r, s=s, u=u)[0])

    # ---- MDI_Trade (base MDI on Close; raw price units, no NaN warm-up) --- #
    for (r, s, u) in [(20, 5, 3), (40, 5, 3)]:
        add(f"MDI_R{r}_S{s}_U{u}",
            f"MDI_Trade: filter over MDI(close,r{r},s{s},u{u}); raw price units.",
            f"base=MDI r={r}, s={s}, u={u}",
            mdi_mod.mdi_series(INPUT_CLOSE, r=r, s=s, u=u)[0])

    # ---- CMI_Trade (base CMI on Open/Close; no NaN warm-up) --------------- #
    for (r, s, u) in [(20, 5, 3), (10, 5, 3)]:
        add(f"CMI_R{r}_S{s}_U{u}",
            f"CMI_Trade: filter over CMI(r{r},s{s},u{u}).",
            f"base=CMI r={r}, s={s}, u={u}",
            cmi_mod.cmi_series(INPUT_OPEN, INPUT_CLOSE, r=r, s=s, u=u)[0])

    # ---- CSI_Trade (base CSI on O/H/L/C; CSI in [-100,100] -> two-sided) -- #
    for (r, s, u) in [(32, 32, 1), (20, 5, 3), (1, 1, 1)]:
        add(f"CSI_R{r}_S{s}_U{u}",
            f"CSI_Trade: filter over CSI(r{r},s{s},u{u}); +rising and -falling kept.",
            f"base=CSI r={r}, s={s}, u={u}",
            csi_mod.csi_series(INPUT_OPEN, INPUT_HIGH, INPUT_LOW, INPUT_CLOSE, r=r, s=s, u=u)[0])

    # ---- TVI_Trade (base TVI on synthetic upticks/downticks; no NaN) ------ #
    # Tick proxy from the bar range: up = close - low, down = high - close.
    # TVI is bounded [-100,100] with no warm-up NaN region.
    INPUT_UPTICKS = [c - l for c, l in zip(INPUT_CLOSE, INPUT_LOW)]
    INPUT_DOWNTICKS = [h - c for h, c in zip(INPUT_HIGH, INPUT_CLOSE)]
    for (r, s, u) in [(32, 32, 5), (12, 12, 1), (25, 13, 1)]:
        add(f"TVI_R{r}_S{s}_U{u}",
            f"TVI_Trade: filter over TVI(up,down,r{r},s{s},u{u}); no NaN warm-up.",
            f"base=TVI r={r}, s={s}, u={u}",
            tvi_mod.tvi_series(INPUT_UPTICKS, INPUT_DOWNTICKS, r=r, s=s, u=u))

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

    # ---- Python: EXPECTED_<name> = [ ... ] -------------------------------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for name, desc, params, vals in results:
            f.write(f"# {desc}\n# {params}\n")
            f.write(f"EXPECTED_{name} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expected<Name> = []float64{ ... } ----------------------- #
    # (NaN appears via SMI/DTI warm-up, so the fixture imports "math".)
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for name, desc, params, vals in results:
            f.write(f"// {desc}\n// {params}\n")
            f.write(f"var expected{name} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expected<Name>: number[] = [ ... ] ------ #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for name, desc, params, vals in results:
            f.write(f"// {desc}\n// {params}\n")
            f.write(f"export const expected{name}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_<name>() -> Vec<f64> { vec![ ... ] } ------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for name, desc, params, vals in results:
            f.write(f"// {desc}\n// {params}\n")
            f.write(f"pub fn expected_{name.lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expected<Name>() [252]f64 { return .{ ... }; } ------- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for name, desc, params, vals in results:
            f.write(f"// {desc}\n// {params}\n")
            f.write(f"pub fn expected{name}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(results)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each).")
