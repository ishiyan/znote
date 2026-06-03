"""Candlestick Index (CSI) -- William Blau ("CandleStick Indicator").

A double-/triple-smoothed candle-body-vs-range oscillator bounded to [-100, +100],
paired with an EMA signal line (the Ergodic form, Blau ch. 6.4):

    csi_k    = 100 * TEMA(close - open, r, s, u) / TEMA(high - low, r, s, u)
    signal_k = EMA(csi, ul)_k                                  (ul-period EMA)

where the two intra-bar quantities are

    co_k             = close_k - open_k                  (signed candle body)
    hl_k             = high_k  - low_k                    (the bar's range >= 0)
    TEMA(x, r, s, u) = EMA(EMA(EMA(x, r), s), u)          (triple EMA cascade)

This is Blau's CandleStick Indicator (book, ch. 6; Appendix B, Figure B-15;
MQL5 Blau_CSI.mq5). The numerator is the *signed* candle body (close minus
open): positive for bullish bars, negative for bearish bars. The denominator is
the smoothed bar range. Because every bar has |close - open| <= high - low, the
ratio is bounded to [-100, +100]: +100 when closes pin the high while opens pin
the low (relentless bullish bodies), -100 in the mirror-image bearish case, and
0 when bodies net out. **Inputs are Open, High, Low and Close.**

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(csi, signal)`` and :func:`csi_series` returns two parallel lists.

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Both intra-bar series are defined from bar 0, so there is NO NaN warm-up region;
the signal line is likewise finite from bar 0 (its EMA seeds on bar 0's
oscillator). The signal, being an EMA of a [-100, 100] series, also stays in
[-100, 100].

Division guard: denominator <= 0  ->  output 0.0 (zero-range market).

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
# INDICATOR: Candlestick Index (two-output: oscillator + signal).         #
# ====================================================================== #

# Two-output result. ``csi`` is the oscillator; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both are finite from bar 0 (no NaN warm-up)
# and both lie in [-100, 100].
CsiResult = namedtuple("CsiResult", ["csi", "signal"])


class CandlestickStrengthIndex:
    """Stateful, streaming Candlestick Index with an EMA signal line.

    Feed one (open, high, low, close) bar at a time to :meth:`update`, which
    returns a :class:`CsiResult` ``(csi, signal)`` for that bar. Both fields are
    finite from bar 0 and lie in [-100, 100] -- ``csi`` the candle-body
    oscillator, ``signal`` its ul-period EMA. There is no NaN warm-up region
    (both intra-bar series are defined from bar 0).

    Example (all stages passthrough, ul=1 passthrough -> raw body/range*100):
    >>> csi = CandlestickStrengthIndex(r=1, s=1, u=1, ul=1)
    >>> o0 = csi.update(10.0, 12.0, 10.0, 12.0); (o0.csi, o0.signal)  # body=range -> +100
    (100.0, 100.0)
    >>> o1 = csi.update(12.0, 12.0, 10.0, 10.0); (o1.csi, o1.signal)  # full bearish -> -100
    (-100.0, -100.0)
    >>> o2 = csi.update(11.0, 11.0, 11.0, 11.0); (o2.csi, o2.signal)  # zero range -> 0
    (0.0, 0.0)
    """

    def __init__(self, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create a CSI with EMA periods ``r, s, u`` (MQL5 defaults 20,5,3) and
        signal-line period ``ul`` (Ergodic default 3). Set ``ul=1`` for a
        passthrough signal (signal == csi every bar).
        """
        # r, s, u, ul are validated by the EMA constructors below.

        # Two independent 3-stage EMA cascades: one for the signed candle body
        # (numerator), one for the high-low range (denominator). Each is wired
        # output -> input: TEMA(x) = stage_u(stage_s(stage_r(x))).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the oscillator. The oscillator is
        # finite from bar 0, so this seeds on bar 0 -- no NaN warm-up.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, open_: float, high: float, low: float,
               close: float) -> CsiResult:
        """Feed one bar's ``open``/``high``/``low``/``close``; return (csi, signal)."""
        # Two intra-bar quantities: signed candle body and (non-negative) range.
        co = close - open_  # signed candle body (bullish > 0, bearish < 0)
        hl = high - low     # full bar range (>= 0)

        # Numerator cascade: TEMA(close-open, r, s, u).
        n = self._num_u.update(self._num_s.update(self._num_r.update(co)))
        # Denominator cascade: TEMA(high-low, r, s, u).
        d = self._den_u.update(self._den_s.update(self._den_r.update(hl)))

        # Division guard: zero range so far -> oscillator 0.0.
        csi = 0.0 if d <= 0.0 else 100.0 * n / d

        # Signal line = EMA(csi, ul); seeds on bar 0's oscillator value.
        signal = self._signal_ema.update(csi)
        return CsiResult(csi, signal)


def csi_series(opens, highs, lows, closes, r=20, s=5, u=3, ul=3):
    """Convenience: run aligned open/high/low/close lists through a fresh CSI.

    Returns two parallel lists: ``(csi_values, signal_values)``.
    """
    csi = CandlestickStrengthIndex(r=r, s=s, u=u, ul=ul)
    out = [csi.update(o, h, l, c) for o, h, l, c in zip(opens, highs, lows, closes)]
    return [o.csi for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_R*_S*_U* (and the
    # paired EXPECTED_R*_S*_U*_SIG_UL3 signal-line) reference arrays and APPENDS
    # them to the five test fixtures in this directory (test_testdata.py,
    # testdata_test.go, testdata.ts, testdata.rs, testdata.zig). The CSI consumes
    # OPEN, HIGH, LOW and CLOSE, so all four input series are embedded below
    # (identical to INPUT_OPEN / INPUT_HIGH / INPUT_LOW / INPUT_CLOSE in the
    # fixtures). Each language gets the same numbers in its own idiomatic literal
    # form, preceded by two comment lines (what-it-tests + param values). There is
    # NO NaN warm-up region (both intra-bar series are defined from bar 0), so
    # every value -- oscillator and signal alike -- is finite and bounded to
    # [-100, 100].
    # ====================================================================== #

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

    # Parameter combinations (r, s, u, what-it-tests). 16 combos -> 32 arrays
    # (each combo yields a CSI oscillator + its UL=3 EMA signal line), <=64.
    COMBOS = [
        (20, 5, 3, "MQL5 default CSI (r20,s5,u3), triple smoothing."),
        (32, 32, 1, "Slow double-smoothed CSI (r32,s32,u1)."),
        (1, 1, 1, "All EMA stages passthrough -> body/range*100, 0 zero-range."),
        (25, 13, 1, "Double smoothing (r25,s13)."),
        (13, 13, 1, "Equal double smoothing."),
        (5, 5, 5, "Equal triple smoothing, short periods."),
        (9, 3, 1, "Fast double-smoothed CSI."),
        (64, 64, 1, "Very slow double smoothing."),
        (32, 32, 3, "Book default with triple smoothing."),
        (40, 20, 1, "Long second smoothing (r=40,s=20)."),
        (2, 2, 2, "Tiny triple smoothing."),
        (7, 4, 2, "Fast triple smoothing."),
        (12, 12, 12, "Equal triple smoothing, medium periods."),
        (3, 10, 10, "Short first, long second/third."),
        (50, 1, 1, "Long first EMA, then passthrough."),
        (32, 5, 3, "Long first, short second, triple."),
    ]

    UL = 3  # signal-line EMA period for the paired *_SIG_UL3 arrays.

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

    # Compute all series once, flattening each combo into TWO emitted arrays:
    # the CSI oscillator (R*_S*_U*) and its UL=3 EMA signal line (..._SIG_UL3).
    # Each entry: (NAME, desc, params_text, values).
    arrays = []
    for r, s, u, desc in COMBOS:
        osc, sig = csi_series(INPUT_OPEN, INPUT_HIGH, INPUT_LOW, INPUT_CLOSE,
                              r=r, s=s, u=u, ul=UL)
        base = f"R{r}_S{s}_U{u}"
        ptxt = f"r={r}, s={s}, u={u}"
        arrays.append((base, desc, ptxt, osc))
        arrays.append((base + "_SIG_UL3",
                       desc + " Signal line (EMA, ul=3) of that CSI.",
                       ptxt + f", ul={UL}", sig))

    # ---- Python: EXPECTED_<name> = [ ... ] -------------------------------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for nm, desc, ptxt, vals in arrays:
            f.write(f"# {desc}\n# {ptxt}\n")
            f.write(f"EXPECTED_{nm} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expected<Name> = []float64{ ... } ----------------------- #
    # (No NaN appears, so no "math" import is needed in the Go fixture.)
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for nm, desc, ptxt, vals in arrays:
            f.write(f"// {desc}\n// {ptxt}\n")
            f.write(f"var expected{nm} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expected<Name>: number[] = [ ... ] ------ #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for nm, desc, ptxt, vals in arrays:
            f.write(f"// {desc}\n// {ptxt}\n")
            f.write(f"export const expected{nm}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_<name>() -> Vec<f64> { vec![ ... ] } ------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for nm, desc, ptxt, vals in arrays:
            f.write(f"// {desc}\n// {ptxt}\n")
            f.write(f"pub fn expected_{nm.lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expected<Name>() [252]f64 { return .{ ... }; } ------- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for nm, desc, ptxt, vals in arrays:
            f.write(f"// {desc}\n// {ptxt}\n")
            f.write(f"pub fn expected{nm}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(arrays)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each).")
