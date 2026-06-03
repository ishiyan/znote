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
    # ------------------------------------------------------------------ #
    # Human-readable demo. (The full 252-bar reference-data harness lives  #
    # in the prepared-for-conversion copy of this file.)                   #
    # ------------------------------------------------------------------ #
    highs = [12.0, 13.0, 12.5, 14.0, 13.5, 13.0, 15.0]
    lows = [10.0, 11.0, 11.0, 12.0, 12.0, 11.5, 13.0]
    closes = [11.0, 12.5, 11.5, 13.5, 12.5, 12.0, 14.5]

    def show(xs):
        return ["nan" if math.isnan(v) else round(v, 4) for v in xs]

    # 1) Book default DS-Stochastic + 3-bar signal.
    d, sig = ds_series(highs, lows, closes, q=5, r=7, s=3, g=3)
    print("ds     q5,r7,s3,g3:", show(d))
    print("signal q5,r7,s3,g3:", show(sig))

    # 2) g=1 invariant: signal must equal ds exactly (passthrough).
    d1, s1 = ds_series(highs, lows, closes, q=5, r=7, s=3, g=1)
    same = all((math.isnan(a) and math.isnan(b)) or a == b for a, b in zip(d1, s1))
    print("g=1 -> signal == ds exactly:", same)
