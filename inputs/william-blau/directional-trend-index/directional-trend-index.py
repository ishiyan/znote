"""Directional Trend Index (DTI) -- William Blau.

A double-/triple-smoothed High-Low Momentum oscillator bounded to [-100, +100],
paired with an EMA signal line (the Ergodic form, Blau ch.7.3):

    dti_k    = 100 * TEMA(HLM, r, s, u) / TEMA(|HLM|, r, s, u)   (the oscillator)
    signal_k = EMA(dti, ul)_k                                    (ul-period EMA)

where the High-Low Momentum is built from how far the high rose and the low
fell relative to q-1 bars ago:

    HMU_k = max(High_k - High_(k-(q-1)), 0)      (upward high movement)
    LMD_k = max(Low_(k-(q-1)) - Low_k,  0)       (downward low movement)
    HLM_k = HMU_k - LMD_k                         (composite high-low momentum)
    TEMA(x, r, s, u) = EMA(EMA(EMA(x, r), s), u)  (triple EMA cascade)

This is the True Strength Index structure (see ../true-strength-index) applied
to HLM instead of price momentum. **Inputs are High and Low only** (no close).

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(dti, signal)`` and :func:`dti_series` returns two parallel lists.

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * Each EMA stage seeds on its first received value.
    * HLM is valid from bar q-1 (it needs a High/Low from q-1 bars ago), so all
      stages seed at bar q-1 together; DTI is NaN for bars 0..q-2 and finite
      from bar q-1 onward. For q=2 only bar 0 is NaN.
    * The signal EMA seeds on the first finite DTI (bar q-1), so the signal is
      ALSO NaN for bars 0..q-2; ul == 1 -> signal == dti (passthrough).
    * NOT the MQL5 begin-offset convention (which blanks more early bars).

Degenerate q=1: HLM == 0 on every bar (High_k - High_k = 0), so the denominator
is always 0 and the division guard yields DTI == 0.0 for all bars (no NaN).

Division guard: denominator == 0  ->  output 0.0 (matches Blau_DTI.mq5).

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
# INDICATOR: Directional Trend Index (two-output: oscillator + signal).   #
# ====================================================================== #

# Two-output result. ``dti`` is the oscillator; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both share the same NaN warm-up region.
DtiResult = namedtuple("DtiResult", ["dti", "signal"])


class DirectionalTrendIndex:
    """Stateful, streaming Directional Trend Index with an EMA signal line.

    Feed one (high, low) pair at a time to :meth:`update`, which returns a
    :class:`DtiResult` ``(dti, signal)`` for that bar. Both fields are
    ``float('nan')`` while the q-bar look-back is not yet satisfied
    (bars 0..q-2), then finite -- ``dti`` in [-100, +100], ``signal`` its EMA.

    Example (q=2 one-bar HLM, all stages passthrough, ul=1 passthrough):
    >>> dti = DirectionalTrendIndex(q=2, r=1, s=1, u=1, ul=1)
    >>> import math
    >>> r0 = dti.update(10.0, 9.0); (math.isnan(r0.dti), math.isnan(r0.signal))
    (True, True)
    >>> r1 = dti.update(12.0, 11.0); (r1.dti, r1.signal)  # HMU=+2, LMD=0 -> +100
    (100.0, 100.0)
    >>> r2 = dti.update(11.0, 8.0); (r2.dti, r2.signal)   # HMU=0, LMD=3 -> -100
    (-100.0, -100.0)
    """

    def __init__(self, q: int = 2, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create a DTI with momentum look-back ``q``, EMA periods ``r,s,u`` and
        signal-line period ``ul``.

        Defaults are the MQL5 reference defaults (q=2, r=20, s=5, u=3) plus the
        Ergodic signal default ul=3. Set ``u=1`` for a double-smoothed DTI;
        set ``ul=1`` for a passthrough signal (signal == dti every bar).
        """
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        # r, s, u, ul are validated by the EMA constructors below.
        self._q = q

        # Rolling windows of recent highs and lows, just large enough to reach
        # back q-1 bars: holding q values means the oldest is *_(k-(q-1)).
        self._highs: deque[float] = deque(maxlen=q)
        self._lows: deque[float] = deque(maxlen=q)

        # Two independent 3-stage EMA cascades: one for signed HLM (numerator),
        # one for absolute HLM (denominator). Each is wired output -> input:
        # TEMA(x) = stage_u(stage_s(stage_r(x))).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the oscillator. Advanced ONLY on finite
        # oscillator values, so it seeds on the first finite DTI (bar q-1) and
        # shares the oscillator's NaN warm-up region.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, high: float, low: float) -> DtiResult:
        """Feed one bar's ``high``/``low``; return (dti, signal) for this bar."""
        self._highs.append(high)
        self._lows.append(low)

        # HLM needs a High/Low from q-1 bars ago. That is available only once
        # the windows hold q values; before then neither output is defined --
        # do NOT advance the signal EMA.
        if len(self._highs) < self._q:
            return DtiResult(float("nan"), float("nan"))

        # With a deque of maxlen q, the leftmost element is exactly the value
        # q-1 bars ago: High_(k-(q-1)) and Low_(k-(q-1)).
        prev_high = self._highs[0]
        prev_low = self._lows[0]

        # Upward high movement and downward low movement, each floored at 0.
        hmu = high - prev_high
        if hmu < 0.0:
            hmu = 0.0
        lmd = prev_low - low
        if lmd < 0.0:
            lmd = 0.0

        # Composite high-low momentum and its magnitude.
        hlm = hmu - lmd
        abs_hlm = abs(hlm)

        # Numerator cascade: TEMA(HLM, r, s, u).
        n = self._num_u.update(self._num_s.update(self._num_r.update(hlm)))
        # Denominator cascade: TEMA(|HLM|, r, s, u).
        d = self._den_u.update(self._den_s.update(self._den_r.update(abs_hlm)))

        # Division guard (Blau_DTI.mq5): denominator 0 -> oscillator 0.0.
        dti = 0.0 if d == 0.0 else 100.0 * n / d

        # Signal line = EMA(dti, ul); seeds here on the first finite oscillator.
        signal = self._signal_ema.update(dti)
        return DtiResult(dti, signal)


def dti_series(highs, lows, q=2, r=20, s=5, u=3, ul=3):
    """Convenience: run whole lists of highs/lows through a fresh DTI.

    Returns two parallel lists: ``(dti_values, signal_values)``.
    """
    dti = DirectionalTrendIndex(q=q, r=r, s=s, u=u, ul=ul)
    out = [dti.update(h, l) for h, l in zip(highs, lows)]
    return [o.dti for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo of the three behaviours that matter most when    #
    # porting. (The full 252-bar reference-data harness lives in the       #
    # prepared-for-conversion copy of this file.)                          #
    # ------------------------------------------------------------------ #
    highs = [10.0, 12.0, 11.0, 13.0, 12.0, 12.0, 15.0]
    lows = [9.0, 11.0, 8.0, 12.0, 10.0, 10.0, 13.0]

    def show(xs):
        return ["nan" if math.isnan(v) else round(v, 4) for v in xs]

    # 1) All-passthrough (r=s=u=1): DTI is the sign of HLM * 100, and exactly
    #    0.0 when HLM == 0 (HMU == LMD) via the division guard.
    osc, sig = dti_series(highs, lows, q=2, r=1, s=1, u=1, ul=1)
    print("q2,r1,s1,u1 osc:", show(osc))
    same = all((math.isnan(a) and math.isnan(b)) or a == b for a, b in zip(osc, sig))
    print("ul=1 -> signal == dti exactly:", same)

    # 2) MQL5 default triple smoothing with default signal ul=3.
    osc, sig = dti_series(highs, lows, q=2, r=20, s=5, u=3, ul=3)
    print("q2,r20,s5,u3 osc:", show(osc))
    print("q2,r20,s5,u3 sig:", show(sig))

    # 3) Degenerate q=1: HLM == 0 every bar -> division guard -> all 0.0.
    osc, sig = dti_series(highs, lows, q=1, r=20, s=5, u=3)
    print("q1 osc (all 0.0):", show(osc))
