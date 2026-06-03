"""Candlestick Momentum Index (CMI) -- William Blau.

A double-/triple-smoothed intra-bar momentum oscillator bounded to [-100, +100],
paired with an EMA signal line (the Ergodic form, Blau ch.6.4):

    cmi_k    = 100 * TEMA(cmtm, r, s, u) / TEMA(|cmtm|, r, s, u)   (oscillator)
    signal_k = EMA(cmi, ul)_k                                     (ul-period EMA)

where the candle momentum is the signed candle body

    cmtm_k           = close_k - open_k                   (intra-bar momentum)
    TEMA(x, r, s, u) = EMA(EMA(EMA(x, r), s), u)          (triple EMA cascade)

This is the True Strength Index structure (see ../true-strength-index) applied
to the candle body instead of price momentum. Because it only looks *inside*
each bar it is immune to inter-bar gaps. **Inputs are Open and Close only.**

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(cmi, signal)`` and :func:`cmi_series` returns two parallel lists.

The MQL5 reference Blau_CMI.mq5 generalizes the body as close - open[q-1] with a
period q (default 1); this port fixes q=1 (the classic close - open). With q=1
the candle momentum is defined from bar 0, so there is NO NaN warm-up region; the
signal line is likewise finite from bar 0 (its EMA seeds on bar 0's oscillator).

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Division guard: denominator == 0  ->  output 0.0 (matches Blau_CMI.mq5).

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
# INDICATOR: Candlestick Momentum Index (two-output: oscillator + signal).#
# ====================================================================== #

# Two-output result. ``cmi`` is the oscillator; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both are finite from bar 0 (no NaN warm-up).
CmiResult = namedtuple("CmiResult", ["cmi", "signal"])


class CandlestickMomentumIndex:
    """Stateful, streaming Candlestick Momentum Index with an EMA signal line.

    Feed one (open, close) pair at a time to :meth:`update`, which returns a
    :class:`CmiResult` ``(cmi, signal)`` for that bar. Both fields are finite
    from bar 0 -- ``cmi`` in [-100, +100], ``signal`` its ul-period EMA. There
    is no NaN warm-up region (candle momentum is defined from the first bar).

    Example (all stages passthrough, ul=1 passthrough -> sign of body * 100):
    >>> cmi = CandlestickMomentumIndex(r=1, s=1, u=1, ul=1)
    >>> o0 = cmi.update(10.0, 12.0); (o0.cmi, o0.signal)  # up candle +2 -> +100
    (100.0, 100.0)
    >>> o1 = cmi.update(12.0, 11.0); (o1.cmi, o1.signal)  # down candle -1 -> -100
    (-100.0, -100.0)
    >>> o2 = cmi.update(11.0, 11.0); (o2.cmi, o2.signal)  # doji 0 -> guard -> 0
    (0.0, 0.0)
    """

    def __init__(self, r: int = 20, s: int = 5, u: int = 3, ul: int = 3) -> None:
        """Create a CMI with EMA periods ``r, s, u`` (MQL5/book defaults) and
        signal-line period ``ul`` (Ergodic default 3). Set ``ul=1`` for a
        passthrough signal (signal == cmi every bar).
        """
        # r, s, u, ul are validated by the EMA constructors below.

        # Two independent 3-stage EMA cascades: one for signed candle momentum
        # (numerator), one for absolute candle momentum (denominator). Each is
        # wired output -> input: TEMA(x) = stage_u(stage_s(stage_r(x))).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the oscillator. The oscillator is
        # finite from bar 0, so this seeds on bar 0 -- no NaN warm-up.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, open_: float, close: float) -> CmiResult:
        """Feed one bar's ``open_``/``close``; return (cmi, signal) this bar."""
        # Candle momentum: the signed body of the candle.
        cmtm = close - open_
        abs_cmtm = abs(cmtm)

        # Numerator cascade: TEMA(cmtm, r, s, u).
        n = self._num_u.update(self._num_s.update(self._num_r.update(cmtm)))
        # Denominator cascade: TEMA(|cmtm|, r, s, u).
        d = self._den_u.update(self._den_s.update(self._den_r.update(abs_cmtm)))

        # Division guard (Blau_CMI.mq5): denominator 0 -> oscillator 0.0.
        cmi = 0.0 if d == 0.0 else 100.0 * n / d

        # Signal line = EMA(cmi, ul); seeds on bar 0's oscillator value.
        signal = self._signal_ema.update(cmi)
        return CmiResult(cmi, signal)


def cmi_series(opens, closes, r=20, s=5, u=3, ul=3):
    """Convenience: run aligned open/close lists through a fresh CMI.

    Returns two parallel lists: ``(cmi_values, signal_values)``.
    """
    cmi = CandlestickMomentumIndex(r=r, s=s, u=u, ul=ul)
    out = [cmi.update(o, c) for o, c in zip(opens, closes)]
    return [o.cmi for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo of the behaviours that matter most when         #
    # porting. (The full 252-bar reference-data harness lives in the      #
    # prepared-for-conversion copy of this file.)                         #
    # ------------------------------------------------------------------ #
    opens = [10.0, 12.0, 11.0, 11.0, 13.0, 12.0, 12.0]
    closes = [12.0, 11.0, 11.0, 13.0, 12.0, 12.0, 15.0]

    # 1) All-passthrough (r=s=u=1): CMI is sign(close-open)*100, 0.0 on a doji.
    osc, sig = cmi_series(opens, closes, r=1, s=1, u=1)
    print("r1,s1,u1 osc:", [round(v, 4) for v in osc])
    print("r1,s1,u1 sig:", [round(v, 4) for v in sig])

    # 2) MQL5 default triple smoothing (oscillator + ul=3 signal line).
    d_osc, d_sig = cmi_series(opens, closes, r=20, s=5, u=3)
    print("r20,s5,u3 osc:", [round(v, 4) for v in d_osc])
    print("r20,s5,u3 sig:", [round(v, 4) for v in d_sig])

    # 3) ul=1 passthrough: signal == oscillator on every bar.
    p_osc, p_sig = cmi_series(opens, closes, r=20, s=5, u=3, ul=1)
    print("ul=1 passthrough holds:", p_osc == p_sig)
