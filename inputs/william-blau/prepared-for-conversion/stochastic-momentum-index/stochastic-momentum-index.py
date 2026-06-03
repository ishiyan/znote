"""Stochastic Momentum Index (SMI) -- William Blau.

A double-/triple-smoothed stochastic oscillator bounded to [-100, +100], paired
with an EMA signal line (the Ergodic form, Blau ch.3.4):

    HH_k = max(High over last q bars)
    LL_k = min(Low  over last q bars)
    sm_k = Close_k - 0.5*(HH_k + LL_k)         (distance from range midpoint)
    hr_k = 0.5*(HH_k - LL_k)                    (half of the q-bar range)

    smi_k    = 100 * TEMA(sm, r, s, u) / TEMA(hr, r, s, u)   (the oscillator)
    signal_k = EMA(smi, ul)_k                                (ul-period EMA)

where TEMA(x, r, s, u) = EMA(EMA(EMA(x, r), s), u) -- the same triple EMA
cascade used by the TSI.

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(smi, signal)`` and :func:`smi_series` returns two parallel lists.

Unlike the TSI/Ergodic (close only), the SMI consumes HIGH, LOW and CLOSE.

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * sm and hr become valid once q bars of High/Low exist, i.e. at bar q-1.
    * All six EMA stages seed at bar q-1 together; SMI is NaN for bars 0..q-2
      and finite from bar q-1. For q == 1 there is no NaN warm-up.
    * The signal EMA seeds on the first finite SMI (bar q-1), so the signal is
      ALSO NaN for bars 0..q-2; ul == 1 -> signal == smi (passthrough).
    * NOT the MQL5 begin-offset convention (which blanks more early bars).

Division guard: TEMA(hr) <= 0 -> output 0.0 (matches Blau_SMI.mq5's
``value2>0 ? value1/value2 : 0``). Because hr >= 0 and the EMA of non-negatives
is non-negative, this only triggers on a fully-flat HH==LL window.

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
# INDICATOR: Stochastic Momentum Index (two-output: oscillator + signal). #
# ====================================================================== #

# Two-output result. ``smi`` is the oscillator; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both share the same NaN warm-up region.
SmiResult = namedtuple("SmiResult", ["smi", "signal"])


class StochasticMomentumIndex:
    """Stateful, streaming Stochastic Momentum Index with an EMA signal line.

    Feed one bar (high, low, close) at a time to :meth:`update`, which returns a
    :class:`SmiResult` ``(smi, signal)`` for that bar. Both fields are
    ``float('nan')`` while the q-bar look-back is not yet satisfied
    (bars 0..q-2), then finite -- ``smi`` in [-100, +100], ``signal`` its EMA.

    Example (q=1 one-day stochastic, all stages passthrough, ul=1 passthrough):
    >>> smi = StochasticMomentumIndex(q=1, r=1, s=1, u=1, ul=1)
    >>> smi.update(high=12.0, low=10.0, close=12.0)   # close at high -> +100
    SmiResult(smi=100.0, signal=100.0)
    >>> smi.update(high=12.0, low=10.0, close=10.0)   # close at low -> -100
    SmiResult(smi=-100.0, signal=-100.0)
    >>> smi.update(high=12.0, low=10.0, close=11.0)   # exact midpoint -> 0
    SmiResult(smi=0.0, signal=0.0)
    """

    def __init__(self, q: int = 5, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create an SMI with stochastic look-back ``q``, EMA periods ``r,s,u``
        and signal-line period ``ul``.

        Defaults are the MQL5 reference defaults (q=5, r=20, s=5, u=3) plus the
        Ergodic signal default ul=3. Set ``ul=1`` for a passthrough signal
        (signal == smi every bar).
        """
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        # r, s, u, ul are validated by the EMA constructors below.
        self._q = q

        # Rolling windows of the last q highs and lows. With maxlen == q the
        # buffers hold exactly the bars [k-(q-1) .. k] once primed.
        self._highs: deque[float] = deque(maxlen=q)
        self._lows: deque[float] = deque(maxlen=q)

        # Two independent 3-stage EMA cascades: one for the stochastic momentum
        # (numerator), one for the half-range (denominator). Each is wired
        # output -> input: TEMA(x) = stage_u(stage_s(stage_r(x))).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the oscillator. Advanced ONLY on finite
        # oscillator values, so it seeds on the first finite SMI (bar q-1) and
        # shares the oscillator's NaN warm-up region.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, high: float, low: float, close: float) -> SmiResult:
        """Feed one bar (``high``, ``low``, ``close``); return (smi, signal)."""
        self._highs.append(high)
        self._lows.append(low)

        # Need q bars of High/Low before the stochastic is defined. Until then
        # neither output exists -- do NOT advance the signal EMA.
        if len(self._highs) < self._q:
            return SmiResult(float("nan"), float("nan"))

        # Rolling extremes over the last q bars.
        hh = max(self._highs)
        ll = min(self._lows)

        # Stochastic momentum (signed) and half-range (non-negative).
        sm = close - 0.5 * (hh + ll)
        hr = 0.5 * (hh - ll)

        # Numerator cascade: TEMA(sm, r, s, u).
        num = self._num_u.update(self._num_s.update(self._num_r.update(sm)))
        # Denominator cascade: TEMA(hr, r, s, u).
        den = self._den_u.update(self._den_s.update(self._den_r.update(hr)))

        # Division guard (Blau_SMI.mq5): denominator <= 0 -> oscillator 0.0.
        smi = 0.0 if den <= 0.0 else 100.0 * num / den

        # Signal line = EMA(smi, ul); seeds here on the first finite oscillator.
        signal = self._signal_ema.update(smi)
        return SmiResult(smi, signal)


def smi_series(highs, lows, closes, q=5, r=20, s=5, u=3, ul=3):
    """Convenience: run aligned High/Low/Close lists through a fresh SMI.

    Returns two parallel lists: ``(smi_values, signal_values)``.
    """
    smi = StochasticMomentumIndex(q=q, r=r, s=s, u=u, ul=ul)
    out = [smi.update(h, l, c) for h, l, c in zip(highs, lows, closes)]
    return [o.smi for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_Q*_R*_S*_U*      #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig). The SMI consumes HIGH, LOW and CLOSE, so    #
    # all three input series are embedded below (identical to INPUT_HIGH /    #
    # INPUT_LOW / INPUT_CLOSE in the fixtures). Each language gets the same   #
    # numbers in its own idiomatic literal form, preceded by two comment      #
    # lines (what-it-tests + param values). NaN appears in the look-back      #
    # warm-up region (bars 0..q-2) and is emitted with each language's NaN    #
    # token.                                                                  #
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

    # Parameter combinations (q, r, s, u, what-it-tests). 16 combos; each yields
    # TWO arrays (oscillator + ul=3 signal line) -> 32 arrays, <=64 budget.
    COMBOS = [
        (5, 20, 5, 3, "MQL5 default SMI (q5,r20,s5,u3)."),
        (13, 25, 2, 1, "Book basic SMI(13,25,2) double smoothing."),
        (2, 20, 20, 1, "Book two-day SMI(2,20,20)."),
        (13, 25, 2, 3, "Basic look-back with triple smoothing."),
        (5, 20, 5, 1, "Default look-back, double smoothing."),
        (8, 5, 3, 1, "Fast SMI."),
        (21, 13, 4, 1, "Longer stochastic look-back q=21."),
        (1, 20, 5, 3, "One-day stochastic / sentiment (q=1, no NaN)."),
        (1, 40, 20, 1, "One-day faster trend (r=40,s=20)."),
        (1, 100, 20, 1, "One-day slow trend (r=100,s=20)."),
        (1, 1, 1, 1, "Raw one-day stochastic; division guard when H==L."),
        (5, 1, 1, 1, "Raw stochastic q=5, all EMA stages passthrough."),
        (3, 10, 10, 1, "Equal double smoothing, short look-back."),
        (34, 5, 5, 1, "Long look-back q=34; NaN bars 0..32."),
        (2, 2, 2, 2, "Equal triple smoothing, two-day look-back."),
        (50, 20, 5, 3, "Very long look-back q=50; NaN bars 0..48."),
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
        osc, sig = smi_series(INPUT_HIGH, INPUT_LOW, INPUT_CLOSE,
                              q=q, r=r, s=s, u=u, ul=UL)
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
