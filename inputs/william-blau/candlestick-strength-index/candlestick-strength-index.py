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
    # ------------------------------------------------------------------ #
    # Human-readable demo of the behaviours that matter most when         #
    # porting. (The full 252-bar reference-data harness lives in the      #
    # prepared-for-conversion copy of this file.)                         #
    # ------------------------------------------------------------------ #
    opens = [10.0, 12.0, 11.0, 12.0, 13.0, 10.0, 13.0]
    highs = [12.0, 12.0, 11.0, 13.0, 13.0, 14.0, 15.0]
    lows = [10.0, 10.0, 11.0, 12.0, 10.0, 10.0, 13.0]
    closes = [12.0, 10.0, 11.0, 13.0, 10.0, 14.0, 15.0]

    # 1) All-passthrough (r=s=u=1, ul=1): CSI is raw body/range * 100, 0.0
    #    on a zero-range bar (high == low) via the division guard; with ul=1 the
    #    signal is a passthrough (signal == csi every bar).
    osc, sig = csi_series(opens, highs, lows, closes, r=1, s=1, u=1, ul=1)
    print("r1,s1,u1,ul1  osc:", [round(v, 4) for v in osc])
    print("r1,s1,u1,ul1  sig:", [round(v, 4) for v in sig])
    assert osc == sig, "ul=1 must make signal a passthrough of the oscillator"

    # 2) MQL5 default double/triple smoothing with the Ergodic signal line (ul=3).
    osc2, sig2 = csi_series(opens, highs, lows, closes, r=20, s=5, u=3, ul=3)
    print("r20,s5,u3,ul3 osc:", [round(v, 4) for v in osc2])
    print("r20,s5,u3,ul3 sig:", [round(v, 4) for v in sig2])
