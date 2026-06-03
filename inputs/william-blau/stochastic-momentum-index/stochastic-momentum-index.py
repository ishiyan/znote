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
    # ------------------------------------------------------------------ #
    # Human-readable demo. (The full 252-bar reference-data harness lives  #
    # in the prepared-for-conversion copy of this file.)                   #
    # ------------------------------------------------------------------ #
    highs = [12.0, 13.0, 12.5, 14.0, 13.5]
    lows = [10.0, 11.0, 11.0, 12.0, 12.0]
    closes = [11.0, 12.5, 11.5, 13.5, 12.5]

    def show(xs):
        return ["nan" if math.isnan(v) else round(v, 4) for v in xs]

    # 1) Default-ish SMI on the toy series (osc + signal).
    osc, sig = smi_series(highs, lows, closes, q=5, r=20, s=5, u=3, ul=3)
    print("SMI q5,r20,s5,u3 osc:", show(osc))
    print("SMI q5,r20,s5,u3 sig:", show(sig))

    # 2) One-day stochastic (q=1): no NaN warm-up, bounded [-100,100].
    osc, sig = smi_series(highs, lows, closes, q=1, r=1, s=1, u=1, ul=1)
    print("SMI q1,r1,s1,u1 osc:", show(osc))
    # ul=1 invariant: signal == oscillator exactly.
    same = all((math.isnan(a) and math.isnan(b)) or a == b for a, b in zip(osc, sig))
    print("ul=1 -> signal == smi exactly:", same)
