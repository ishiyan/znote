"""Double-Smoothed Stochastic (DS-Stochastic) -- William Blau.

A classic double-smoothed stochastic oscillator bounded to [0, 100], with a
short simple-moving-average signal line:

    HH_k  = max(High over last q bars)
    LL_k  = min(Low  over last q bars)
    st_k  = Close_k - LL_k                 (raw stochastic: close above the low)
    rng_k = HH_k - LL_k                    (q-bar range)

    ds_k     = 100 * EMA(EMA(st, r), s) / EMA(EMA(rng, r), s)
    signal_k = SMA(ds, g)

It is a TWO-output indicator: each update() returns a named tuple (ds, signal).

DS-Stochastic is exactly the MQL5 Blau_TStochI reference with its third EMA
period u = 1 (a passthrough): DS(q,r,s) = TStochI(q,r,s,1).

Unlike the TSI/Ergodic (close only), the DS-Stochastic consumes HIGH, LOW and
CLOSE.

Two primitives are **embedded** below (inlined, not imported) so this file is a
self-contained porting unit:
    * ExponentialMovingAverage -- the Blau EMA (verbatim copy).
    * SimpleMovingAverage      -- expanding-then-rolling mean for the signal.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * Oscillator: st/rng valid once q bars of High/Low exist (bar q-1); all four
      EMA stages seed there. ds is NaN for bars 0..q-2, finite from bar q-1.
      For q == 1 there is no NaN warm-up.
    * Signal SMA: finite wherever ds is finite (same NaN region). It seeds on the
      first finite ds and returns the mean of the ds values seen so far
      (expanding window <= g), then the full g-bar rolling mean.
    * g == 1 -> signal is a passthrough -> signal == ds for every bar.

Division guard: EMA(EMA(rng)) <= 0 -> ds = 0.0 (matches Blau_TStochI.mq5's
``value2>0 ? value1/value2 : 0``).

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
# EMBEDDED BUILDING BLOCK: simple moving average (signal line).          #
# Expanding-then-rolling mean (see description.md §2.2): the first g-1    #
# outputs are the mean of however many values have been seen, then it     #
# becomes a full g-bar rolling mean. period == 1 -> passthrough.          #
# ====================================================================== #
class SimpleMovingAverage:
    """Stateful streaming SMA over the last ``period`` inputs.

    Returns the mean of the buffer's current contents on every update: an
    expanding window while fewer than ``period`` values have arrived, then a
    rolling ``period``-bar window. No NaN warm-up (finite from the first input).
    """

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period!r}")
        self._buf: deque[float] = deque(maxlen=period)

    def update(self, x: float) -> float:
        # deque(maxlen=period) drops the oldest automatically once full, so the
        # buffer always holds the last <=period inputs.
        self._buf.append(x)
        # Naive left-to-right sum (oldest -> newest), NOT a compensated sum, so
        # that a straightforward port (acc=0; for v in buf: acc+=v) reproduces
        # these values bit-for-bit. Order matters for IEEE-754 reproducibility.
        total = 0.0
        for v in self._buf:
            total += v
        return total / len(self._buf)


# ====================================================================== #
# INDICATOR: Double-Smoothed Stochastic.                                 #
# ====================================================================== #

# Two-output result. ``ds`` is the oscillator; ``signal`` is its g-bar SMA.
# Both share the same NaN warm-up region.
DSResult = namedtuple("DSResult", ["ds", "signal"])


class DoubleSmoothedStochastic:
    """Stateful, streaming DS-Stochastic (oscillator + SMA signal line).

    Feed one bar (high, low, close) at a time to :meth:`update`; it returns a
    :class:`DSResult` ``(ds, signal)``. Both fields are NaN while the q-bar
    look-back is unmet (bars 0..q-2), then finite in [0, 100].

    Example (q=1 one-bar HLC index, all stages passthrough, g=1 -> signal==ds):
    >>> d = DoubleSmoothedStochastic(q=1, r=1, s=1, g=1)
    >>> d.update(high=12.0, low=10.0, close=12.0)   # close at high -> 100
    DSResult(ds=100.0, signal=100.0)
    >>> d.update(high=12.0, low=10.0, close=10.0)   # close at low -> 0
    DSResult(ds=0.0, signal=0.0)
    >>> d.update(high=12.0, low=10.0, close=11.0)   # midpoint -> 50
    DSResult(ds=50.0, signal=50.0)
    """

    def __init__(self, q: int = 5, r: int = 7, s: int = 3, g: int = 3) -> None:
        """Create a DS-Stochastic with look-back ``q``, EMA periods ``r,s`` and signal ``g``.

        Defaults are the book defaults (q=5, r=7, s=3) with a 3-bar SMA signal.
        """
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        # r, s, g are validated by the EMA/SMA constructors below.
        self._q = q

        # Rolling windows of the last q highs and lows.
        self._highs: deque[float] = deque(maxlen=q)
        self._lows: deque[float] = deque(maxlen=q)

        # Two independent 2-stage EMA cascades (double smoothing): one for the
        # raw stochastic (numerator), one for the range (denominator).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)

        # Signal line: g-bar SMA of the oscillator.
        self._sig = SimpleMovingAverage(g)

    def update(self, high: float, low: float, close: float) -> DSResult:
        """Feed one bar (``high``, ``low``, ``close``); return (ds, signal) for this bar."""
        self._highs.append(high)
        self._lows.append(low)

        # Need q bars of High/Low before the stochastic is defined. While the
        # oscillator is unprimed the signal is undefined too, and we must NOT
        # advance the SMA (it should seed on the first finite ds, bar q-1).
        if len(self._highs) < self._q:
            return DSResult(float("nan"), float("nan"))

        # Rolling extremes over the last q bars.
        hh = max(self._highs)
        ll = min(self._lows)

        # Raw stochastic (>= 0) and range (>= 0).
        st = close - ll
        rng = hh - ll

        # Double-smooth each separately, then divide.
        num = self._num_s.update(self._num_r.update(st))
        den = self._den_s.update(self._den_r.update(rng))

        # Division guard (Blau_TStochI.mq5): denominator <= 0 -> ds = 0.0.
        ds = 0.0 if den <= 0.0 else 100.0 * num / den

        signal = self._sig.update(ds)
        return DSResult(ds, signal)


def ds_series(highs, lows, closes, q=5, r=7, s=3, g=3):
    """Convenience: run aligned High/Low/Close lists through a fresh DS-Stochastic.

    Returns two parallel lists: (ds_values, signal_values).
    """
    d = DoubleSmoothedStochastic(q=q, r=r, s=s, g=g)
    out = [d.update(h, l, c) for h, l, c in zip(highs, lows, closes)]
    return [o.ds for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_DS_* / _SIG_*    #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory. The DS-Stochastic has TWO outputs (oscillator + signal) and  #
    # consumes HIGH, LOW and CLOSE, so all three input series are embedded    #
    # below (identical to INPUT_HIGH / INPUT_LOW / INPUT_CLOSE in the         #
    # fixtures). Each language gets the same numbers in its own idiomatic     #
    # literal form, preceded by two comment lines (what-it-tests + params).   #
    # NaN appears in the look-back warm-up region (bars 0..q-2) for BOTH      #
    # outputs and is emitted with each language's NaN token.                  #
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

    # Parameter combinations (q, r, s, g, what-it-tests). 14 combos x 2
    # outputs = 28 arrays, within the <=64 budget.
    COMBOS = [
        (5, 7, 3, 3, "Book default DS(5,7,3) with 3-bar signal."),
        (2, 3, 15, 3, "Book alternative DS(2,3,15), 3-bar signal."),
        (5, 20, 5, 3, "MQL5 look-back DS(5,20,5), 3-bar signal."),
        (5, 7, 3, 1, "g=1 invariant: signal MUST equal ds exactly."),
        (2, 3, 15, 1, "g=1 invariant on alt params."),
        (1, 1, 1, 1, "Raw one-bar HLC index; division guard when H==L."),
        (1, 5, 5, 3, "One-bar HLC index, double-smoothed, 3-bar signal."),
        (8, 5, 3, 3, "Fast DS, longer look-back q=8."),
        (21, 13, 4, 3, "Longer look-back q=21."),
        (5, 1, 1, 3, "Raw double-pass (r=s=1 passthrough), 3-bar signal."),
        (3, 10, 10, 5, "Equal double smoothing, 5-bar signal."),
        (34, 5, 5, 3, "Long look-back q=34; NaN bars 0..32."),
        (2, 3, 15, 5, "Alt params with 5-bar signal."),
        (10, 7, 3, 3, "Medium look-back q=10."),
    ]

    def name(q, r, s, g):
        """Param shortcut, e.g. (5,7,3,3) -> 'Q5_R7_S3_G3' (signal -> G)."""
        return f"Q{q}_R{r}_S{s}_G{g}"

    def params(q, r, s, g):
        return f"q={q}, r={r}, s={s}, g={g}"

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

    # Compute both series once per combo. ``outputs`` is a flat list of records:
    #   (kind_upper, kind_camel, kind_snake, label, shortcut, paramline, vals)
    outputs = []
    for q, r, s, g, desc in COMBOS:
        ds_vals, sig_vals = ds_series(INPUT_HIGH, INPUT_LOW, INPUT_CLOSE, q=q, r=r, s=s, g=g)
        sc = name(q, r, s, g)
        pl = params(q, r, s, g)
        outputs.append(("DS", "Ds", "ds", f"DS-Stochastic oscillator: {desc}", sc, pl, ds_vals))
        outputs.append(("SIG", "Sig", "sig", f"Signal line: {desc}", sc, pl, sig_vals))

    # ---- Python: EXPECTED_DS_<name> / EXPECTED_SIG_<name> = [ ... ] ------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"# {label}\n# {pl}\n")
            f.write(f"EXPECTED_{ku}_{sc} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expectedDs<Name> / expectedSig<Name> = []float64{ ... } -- #
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"var expected{kc}{sc} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expectedDs<Name> / expectedSig<Name> ---- #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"export const expected{kc}{sc}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_ds_<name>() / expected_sig_<name>() -------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"pub fn expected_{ks}_{sc.lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expectedDs<Name>() / expectedSig<Name>() [252]f64 ---- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"pub fn expected{kc}{sc}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(outputs)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each, {len(COMBOS)} combos x 2 outputs).")
