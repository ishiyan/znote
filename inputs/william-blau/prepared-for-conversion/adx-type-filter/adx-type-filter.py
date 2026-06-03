"""ADX-Type Filter (ATF) -- William Blau (book Figure B-24).

A non-negative "trend-strength" filter, analogous to Wilder's ADX, built by
rectifying and double-smoothing a *bipolar momentum* series:

    ATF(Price, r, s) = EMA( |EMA(Price, r)| , s )

(in Blau's EasyLanguage: ``XAverage(AbsValue(XAverage(Price, r)), s)``).

``Price`` is any *bipolar* (signed) momentum/oscillator. The inner EMA(r)
smooths it, the absolute value rectifies it (discarding direction, keeping
amplitude), and the outer EMA(s) smooths the amplitude. A rising ATF means a
strengthening trend; a falling ATF means a weakening / ranging market -- exactly
the ADX interpretation (LeBeau & Lucas: the *slope* matters more than the level).

The canonical bipolar inputs Blau lists (Fig B-24) are:
    * ``C - C[q-1]``                      -- the TSI numerator (price momentum)
    * ``HMU - LMD``                       -- the DTI numerator (high-low momentum)
    * ``Upticks - Downticks``             -- TVI
    * ``C - 0.5*(HH(q) + LL(q))``         -- the SMI raw stochastic momentum
A *single-smoothed normalized* indicator (e.g. ``TSI(price, r, 1, 1)``) may also
be used as ``Price``; it then *replaces* the inner ``EMA(Price, r)`` -- which is
exactly :class:`AdxTypeFilter` with ``r = 1`` (inner EMA passthrough),
``ATF = EMA(|Price|, s)``.

This module provides:
    * :class:`AdxTypeFilter`  -- the generic book function, on any bipolar series.
    * :class:`TsiAtf`         -- TSI_ATF: ATF on the TSI numerator ``C - C[q-1]``.
    * :class:`SmiAtf`         -- SMI_ATF: ATF on ``C - 0.5*(HH(q) + LL(q))``.

The EMA primitive is **embedded** below (inlined, not imported) so this file is a
self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * Each EMA stage seeds on its first received (finite) value.
    * A leading NaN in ``Price`` (e.g. the TSI/SMI momentum during its look-back
      warm-up) is **propagated**: ATF returns NaN and the EMAs do not advance
      until the first finite input, at which point both stages seed.
    * Output is always **>= 0** (it is a smoothed absolute value).

There is NO division in this indicator, hence no division guard.

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
# GENERIC INDICATOR: ADX-Type Filter (book Fig B-24).                     #
# ====================================================================== #
class AdxTypeFilter:
    """Stateful, streaming generic ATF: ``EMA(|EMA(x, r)|, s)``.

    Feed one *bipolar momentum* value ``x`` at a time to :meth:`update`. Leading
    NaNs are propagated (returned as NaN; the internal EMAs wait to seed). The
    output is always ``>= 0``.

    ``r = 1`` makes the inner EMA a passthrough, giving the normalized-indicator
    form ``EMA(|x|, s)`` (Blau's note: feed a single-smoothed normalized
    oscillator such as TSI(price, r, 1, 1)).

    Example (r = s = 1: both EMAs passthrough -> ATF == |x|):
    >>> f = AdxTypeFilter(r=1, s=1)
    >>> f.update(2.0)
    2.0
    >>> f.update(-3.0)
    3.0
    >>> f.update(-1.5)
    1.5
    """

    def __init__(self, r: int = 32, s: int = 32) -> None:
        """Create an ATF with inner EMA period ``r`` and outer EMA period ``s``."""
        # r, s are validated by the EMA constructors.
        self._inner = ExponentialMovingAverage(r)
        self._outer = ExponentialMovingAverage(s)

    def update(self, x: float) -> float:
        """Feed one bipolar momentum ``x`` and return this bar's ATF (or NaN)."""
        # Propagate a leading NaN: do NOT advance the EMAs until the first finite
        # input, so both stages seed on the first real momentum value.
        if math.isnan(x):
            return float("nan")
        # Inner smooth -> rectify -> outer smooth.
        return self._outer.update(abs(self._inner.update(x)))


def atf_series(values, r=32, s=32):
    """Convenience: run a whole bipolar-momentum list through a fresh ATF."""
    f = AdxTypeFilter(r=r, s=s)
    return [f.update(v) for v in values]


# ====================================================================== #
# NAMED INSTANCE: TSI_ATF -- ATF on the TSI numerator momentum.           #
# ====================================================================== #
class TsiAtf:
    """TSI_ATF: ATF applied to the TSI numerator ``mtm = C - C[q-1]``.

    ``TSI_ATF(close, q, r, s) = EMA(|EMA(C - C[q-1], r)|, s)``.

    update(close) -> NaN for bars 0..q-2 (momentum look-back), then a finite
    value >= 0. Defaults q=2, r=32, s=32 (catalog TSI_ATF example r=32).

    Example (q=2, r=s=1: ATF == |C - C[1]|):
    >>> import math
    >>> a = TsiAtf(q=2, r=1, s=1)
    >>> math.isnan(a.update(10.0))     # bar 0: momentum undefined
    True
    >>> a.update(12.0)                 # mtm = +2 -> |2| = 2
    2.0
    >>> a.update(11.0)                 # mtm = -1 -> |-1| = 1
    1.0
    """

    def __init__(self, q: int = 2, r: int = 32, s: int = 32) -> None:
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        self._q = q
        # Window of q closes so the leftmost element is C_(k-(q-1)).
        self._hist: deque[float] = deque(maxlen=q)
        self._atf = AdxTypeFilter(r=r, s=s)

    def update(self, close: float) -> float:
        self._hist.append(close)
        if len(self._hist) < self._q:
            return float("nan")
        mtm = close - self._hist[0]           # TSI numerator momentum
        return self._atf.update(mtm)


def tsi_atf_series(closes, q=2, r=32, s=32):
    """Convenience: run closes through a fresh TSI_ATF."""
    a = TsiAtf(q=q, r=r, s=s)
    return [a.update(c) for c in closes]


# ====================================================================== #
# NAMED INSTANCE: SMI_ATF -- ATF on the SMI raw stochastic momentum.      #
# ====================================================================== #
class SmiAtf:
    """SMI_ATF: ATF applied to ``sm = C - 0.5*(HH(q) + LL(q))``.

    where HH(q)/LL(q) are the highest high / lowest low over the last q bars:

        SMI_ATF(q, r, s) = EMA(|EMA(C - 0.5*(HH(q) + LL(q)), r)|, s).

    update(high, low, close) -> NaN for bars 0..q-2 (the q-bar HH/LL look-back),
    then a finite value >= 0. Defaults q=32, r=32, s=32 (catalog SMI_ATF example
    q=32, r=32).

    Example (q=1: HH=high, LL=low, so sm = C - 0.5*(H+L); r=s=1 -> ATF = |sm|):
    >>> a = SmiAtf(q=1, r=1, s=1)
    >>> a.update(11.0, 9.0, 10.5)      # sm = 10.5 - 0.5*(11+9) = 0.5
    0.5
    """

    def __init__(self, q: int = 32, r: int = 32, s: int = 32) -> None:
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        self._q = q
        self._highs: deque[float] = deque(maxlen=q)
        self._lows: deque[float] = deque(maxlen=q)
        self._atf = AdxTypeFilter(r=r, s=s)

    def update(self, high: float, low: float, close: float) -> float:
        self._highs.append(high)
        self._lows.append(low)
        if len(self._highs) < self._q:
            return float("nan")
        hh = max(self._highs)                 # highest high over q bars
        ll = min(self._lows)                  # lowest low over q bars
        sm = close - 0.5 * (hh + ll)          # SMI raw stochastic momentum
        return self._atf.update(sm)


def smi_atf_series(highs, lows, closes, q=32, r=32, s=32):
    """Convenience: run H/L/C through a fresh SMI_ATF."""
    a = SmiAtf(q=q, r=r, s=s)
    return [a.update(h, l, c) for h, l, c in zip(highs, lows, closes)]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Regenerates the EXPECTED_<INPUT>_* reference arrays and APPENDS them to  #
    # the five fixtures (test_testdata.py, testdata_test.go, testdata.ts,     #
    # testdata.rs, testdata.zig).                                            #
    #                                                                         #
    # ATF is applied to the full book (Fig B-24) menu of BIPOLAR momenta,     #
    # composed here from the shared 252-bar H/L/C dataset (embedded below,    #
    # bit-identical to the fixtures):                                         #
    #   TSIMTM  : C - C[q-1]                 (TSI numerator)   -> tsi_atf      #
    #   SMIRAW  : C - 0.5*(HH(q)+LL(q))      (SMI raw)         -> smi_atf      #
    #   DTINUM  : max(H-H[q-1],0)-max(L[q-1]-L,0) (DTI num)    -> atf_series   #
    #   TVI     : 2C - H - L                 (up - down)       -> atf_series   #
    #   TSINORM : TSI(price,2,R,1,1) single-smoothed normalized -> atf r=1     #
    # The TSI/SMI/DTI momenta carry a NaN warm-up, so the Go fixture imports   #
    # "math". Outputs are all >= 0.                                           #
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

    # Synthetic TVI tick proxy: up = C - L, down = H - C ; balance = up - down.
    INPUT_TVI_MOM = [2.0 * c - h - l
                     for h, l, c in zip(INPUT_HIGH, INPUT_LOW, INPUT_CLOSE)]

    NaN = float("nan")

    def tsi_mtm(closes, q):
        """TSI numerator momentum C - C[q-1]; NaN for bars 0..q-2."""
        out = []
        for k in range(len(closes)):
            out.append(NaN if k < q - 1 else closes[k] - closes[k - (q - 1)])
        return out

    def dti_num(highs, lows, q):
        """DTI numerator HLM = max(H-H[q-1],0) - max(L[q-1]-L,0); NaN 0..q-2."""
        out = []
        for k in range(len(highs)):
            if k < q - 1:
                out.append(NaN)
                continue
            hmu = max(highs[k] - highs[k - (q - 1)], 0.0)
            lmd = max(lows[k - (q - 1)] - lows[k], 0.0)
            out.append(hmu - lmd)
        return out

    # Single-smoothed normalized TSI(price, q=2, r=R, s=1, u=1), loaded from the
    # sibling true-strength-index module (bit-identical reproduction).
    import importlib.util as _ilu
    import os as _os
    def _load(folder, modname):
        p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                          folder, folder + ".py")
        sp = _ilu.spec_from_file_location(modname, p)
        m = _ilu.module_from_spec(sp); sp.loader.exec_module(m); return m
    _tsi = _load("true-strength-index", "_btsi")

    def tsi_norm(closes, r):
        """Single-smoothed normalized TSI(price, q=2, r, s=1, u=1)."""
        return _tsi.tsi_series(closes, q=2, r=r, s=1, u=1)[0]

    # ------------------------------------------------------------------ #
    # Combos: (input_kind, q_or_r, r, s, name_suffix, what-it-tests).     #
    # For TSINORM the 2nd field is the inner normalized-TSI period R, and  #
    # the generic ATF uses inner r=1 (passthrough) + outer s.             #
    # ------------------------------------------------------------------ #
    COMBOS = [
        ("TSIMTM", 2, 32, 32, "Q2_R32_S32", "TSI_ATF default: ATF on C-C[1], r=s=32."),
        ("TSIMTM", 2, 20, 5, "Q2_R20_S5", "TSI_ATF on C-C[1], r=20,s=5."),
        ("TSIMTM", 2, 13, 1, "Q2_R13_S1", "TSI_ATF on C-C[1], r=13,s=1 (outer passthrough)."),
        ("TSIMTM", 2, 1, 1, "Q2_R1_S1", "TSI_ATF r=s=1 -> |C-C[1]| (invariant check)."),
        ("TSIMTM", 5, 32, 32, "Q5_R32_S32", "TSI_ATF on C-C[4], r=s=32."),
        ("SMIRAW", 32, 32, 32, "Q32_R32_S32", "SMI_ATF default: ATF on C-0.5(HH32+LL32)."),
        ("SMIRAW", 32, 20, 5, "Q32_R20_S5", "SMI_ATF q=32, r=20, s=5."),
        ("SMIRAW", 5, 32, 32, "Q5_R32_S32", "SMI_ATF q=5, r=s=32."),
        ("DTINUM", 2, 32, 32, "Q2_R32_S32", "ATF on DTI numerator, q=2, r=s=32."),
        ("DTINUM", 2, 28, 28, "Q2_R28_S28", "ATF on DTI numerator, q=2, r=s=28."),
        ("DTINUM", 5, 32, 32, "Q5_R32_S32", "ATF on DTI numerator, q=5, r=s=32."),
        ("TVI", 0, 32, 32, "R32_S32", "ATF on TVI balance 2C-H-L, r=s=32 (no NaN)."),
        ("TVI", 0, 12, 12, "R12_S12", "ATF on TVI balance, r=s=12."),
        ("TVI", 0, 1, 1, "R1_S1", "ATF on TVI balance, r=s=1 -> |2C-H-L|."),
        ("TSINORM", 32, 1, 32, "R32_S32", "ATF on single-smoothed TSI(32), outer s=32."),
        ("TSINORM", 20, 1, 20, "R20_S20", "ATF on single-smoothed TSI(20), outer s=20."),
    ]

    def build(kind, p, r, s):
        if kind == "TSIMTM":
            return tsi_atf_series(INPUT_CLOSE, q=p, r=r, s=s)
        if kind == "SMIRAW":
            return smi_atf_series(INPUT_HIGH, INPUT_LOW, INPUT_CLOSE, q=p, r=r, s=s)
        if kind == "DTINUM":
            return atf_series(dti_num(INPUT_HIGH, INPUT_LOW, p), r=r, s=s)
        if kind == "TVI":
            return atf_series(INPUT_TVI_MOM, r=r, s=s)
        if kind == "TSINORM":
            # inner normalized-TSI period = p (2nd field); generic ATF inner r=1.
            return atf_series(tsi_norm(INPUT_CLOSE, p), r=1, s=s)
        raise ValueError(kind)

    def fmt(x, nan_token):
        if math.isnan(x):
            return nan_token
        return repr(float(x))

    def wrap(values, indent, nan_token, per_line=4):
        lines = []
        for i in range(0, len(values), per_line):
            chunk = ", ".join(fmt(v, nan_token) for v in values[i:i + per_line])
            lines.append(f"{indent}{chunk},")
        return "\n".join(lines)

    results = []
    for (kind, p, r, s, suffix, desc) in COMBOS:
        name = f"{kind}_{suffix}"
        results.append((name, desc, build(kind, p, r, s)))

    # ---- Python ---------------------------------------------------------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for name, desc, vals in results:
            f.write(f"# {desc}\n")
            f.write(f"EXPECTED_{name} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go (NaN present -> imports math) -------------------------------- #
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for name, desc, vals in results:
            f.write(f"// {desc}\n")
            f.write(f"var expected{name} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript ------------------------------------------------------ #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for name, desc, vals in results:
            f.write(f"// {desc}\n")
            f.write(f"export const expected{name}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust ------------------------------------------------------------ #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for name, desc, vals in results:
            f.write(f"// {desc}\n")
            f.write(f"pub fn expected_{name.lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig ------------------------------------------------------------- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for name, desc, vals in results:
            f.write(f"// {desc}\n")
            f.write(f"pub fn expected{name}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(results)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each).")
