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
    # ------------------------------------------------------------------ #
    # Human-readable demo of the behaviours that matter most when         #
    # porting. (The full 252-bar reference-data harness lives in the      #
    # prepared-for-conversion copy of this file.)                         #
    # ------------------------------------------------------------------ #
    closes = [10.0, 12.0, 11.0, 13.0, 12.0, 12.0, 15.0]

    # 1) Baseline passthrough r=1: md == 0 every bar -> all 0.0.
    g_osc, _ = mdi_series(closes, r=1, s=5, u=3)
    print("r1 (all 0.0) :", [round(v, 4) for v in g_osc])

    # 2) Pure book double smoothing u=1: MDI = EMA(price - EMA(price, r), s).
    osc, sig = mdi_series(closes, r=20, s=5, u=1)
    print("r20,s5,u1  osc:", [round(v, 4) for v in osc])
    print("r20,s5,u1  sig:", [round(v, 4) for v in sig])

    # 3) MQL5/book default triple smoothing (line + ul=3 signal line).
    d_osc, d_sig = mdi_series(closes, r=20, s=5, u=3)
    print("r20,s5,u3  osc:", [round(v, 4) for v in d_osc])
    print("r20,s5,u3  sig:", [round(v, 4) for v in d_sig])

    # 4) ul=1 passthrough: signal == line on every bar.
    p_osc, p_sig = mdi_series(closes, r=20, s=5, u=3, ul=1)
    print("ul=1 passthrough holds:", p_osc == p_sig)
