"""True Strength Index (TSI) -- William Blau.

A double-/triple-smoothed momentum oscillator bounded to [-100, +100], paired
with an EMA signal line (the Ergodic form, Blau ch.1.4):

    tsi_k    = 100 * TEMA(mtm, r, s, u) / TEMA(|mtm|, r, s, u)   (the oscillator)
    signal_k = EMA(tsi, ul)_k                                    (ul-period EMA)

where
    mtm_k             = C_k - C_(k-(q-1))                  (q-period momentum)
    TEMA(x, r, s, u)  = EMA(EMA(EMA(x, r), s), u)          (triple EMA cascade)

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(tsi, signal)`` and :func:`tsi_series` returns two parallel lists.

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * Each EMA stage seeds on its first received value.
    * Momentum is valid from bar q-1, so all stages seed at bar q-1 together;
      TSI is NaN for bars 0..q-2 and finite from bar q-1 onward.
    * The signal EMA seeds on the first finite TSI (bar q-1), so the signal is
      ALSO NaN for bars 0..q-2 and finite from bar q-1; ul == 1 -> signal is a
      passthrough -> signal == tsi for every bar.
    * Order-independent: TSI(q,r,s,u) == TSI(q,s,r,u) == ... (Blau, ch.2).
    * NOT the MQL5 begin-offset convention (which blanks more early bars).

Division guard: denominator == 0  ->  output 0.0 (matches Blau_TSI.mq5).

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
# INDICATOR: True Strength Index (two-output: oscillator + signal line).  #
# ====================================================================== #

# Two-output result. ``tsi`` is the oscillator; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both share the same NaN warm-up region.
TsiResult = namedtuple("TsiResult", ["tsi", "signal"])


class TrueStrengthIndex:
    """Stateful, streaming True Strength Index with an EMA signal line.

    Feed one price (close) at a time to :meth:`update`, which returns a
    :class:`TsiResult` ``(tsi, signal)`` for that bar. Both fields are
    ``float('nan')`` while the momentum look-back is not yet satisfied
    (bars 0..q-2), then finite -- ``tsi`` in [-100, +100], ``signal`` its EMA.

    Example (q=2 one-bar momentum, all stages passthrough, ul=1 passthrough):
    >>> tsi = TrueStrengthIndex(q=2, r=1, s=1, u=1, ul=1)
    >>> import math
    >>> r0 = tsi.update(10.0); (math.isnan(r0.tsi), math.isnan(r0.signal))
    (True, True)
    >>> r1 = tsi.update(12.0); (r1.tsi, r1.signal)   # mtm=+2 -> +100, ul=1
    (100.0, 100.0)
    >>> r2 = tsi.update(11.0); (r2.tsi, r2.signal)   # mtm=-1 -> -100, ul=1
    (-100.0, -100.0)
    """

    def __init__(self, q: int = 2, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create a TSI with momentum period ``q``, EMA periods ``r,s,u`` and
        signal-line period ``ul``.

        Defaults are the MQL5 reference defaults (q=2, r=20, s=5, u=3) plus the
        Ergodic signal default ul=3. Set ``u=1`` for the book's classic
        double-smoothed TSI(close, r, s); set ``ul=1`` for a passthrough signal
        (signal == tsi every bar).
        """
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        # r, s, u, ul are validated by the EMA constructors below.
        self._q = q

        # Rolling window of recent prices, just large enough to reach back
        # q-1 bars: holding q prices means the oldest is C_(k-(q-1)).
        self._history: deque[float] = deque(maxlen=q)

        # Two independent 3-stage EMA cascades: one for signed momentum
        # (numerator), one for absolute momentum (denominator). Each is wired
        # output -> input: TEMA(x) = stage_u(stage_s(stage_r(x))).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the oscillator. It is advanced ONLY on
        # finite oscillator values, so it seeds on the first finite TSI (bar
        # q-1) and shares the oscillator's NaN warm-up region.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, price: float) -> TsiResult:
        """Feed one close ``price``; return (tsi, signal) for this bar."""
        self._history.append(price)

        # Momentum needs a price from q-1 bars ago. That is available only once
        # the window holds q prices; before then the indicator is not primed
        # and neither output is defined -- do NOT advance the signal EMA.
        if len(self._history) < self._q:
            return TsiResult(float("nan"), float("nan"))

        # mtm_k = C_k - C_(k-(q-1)). With a deque of maxlen q, the leftmost
        # element is exactly C_(k-(q-1)).
        mtm = price - self._history[0]
        abs_mtm = abs(mtm)

        # Numerator cascade: TEMA(mtm, r, s, u).
        n = self._num_u.update(self._num_s.update(self._num_r.update(mtm)))
        # Denominator cascade: TEMA(|mtm|, r, s, u).
        d = self._den_u.update(self._den_s.update(self._den_r.update(abs_mtm)))

        # Division guard (Blau_TSI.mq5): denominator 0 -> oscillator 0.0.
        tsi = 0.0 if d == 0.0 else 100.0 * n / d

        # Signal line = EMA(tsi, ul); seeds here on the first finite oscillator.
        signal = self._signal_ema.update(tsi)
        return TsiResult(tsi, signal)


def tsi_series(values, q=2, r=20, s=5, u=3, ul=3):
    """Convenience: run a whole list of closes through a fresh TSI.

    Returns two parallel lists: ``(tsi_values, signal_values)``.
    """
    tsi = TrueStrengthIndex(q=q, r=r, s=s, u=u, ul=ul)
    out = [tsi.update(v) for v in values]
    return [o.tsi for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo of the three behaviours that matter most when    #
    # porting. (The full 252-bar reference-data harness lives in the       #
    # prepared-for-conversion copy of this file.)                          #
    # ------------------------------------------------------------------ #
    closes = [10.0, 12.0, 11.0, 13.0, 12.0, 12.0, 15.0]

    def show(xs):
        return ["nan" if math.isnan(v) else round(v, 4) for v in xs]

    # 1) All-passthrough (r=s=u=1): TSI is the sign of momentum * 100,
    #    and exactly 0.0 on a flat bar (mtm == 0) via the division guard.
    osc, sig = tsi_series(closes, q=2, r=1, s=1, u=1, ul=3)
    print("q2,r1,s1,u1 osc:", show(osc))
    print("q2,r1,s1,u1 sig:", show(sig))

    # 2) MQL5 default triple smoothing with default signal ul=3.
    osc, sig = tsi_series(closes, q=2, r=20, s=5, u=3, ul=3)
    print("q2,r20,s5,u3 osc:", show(osc))
    print("q2,r20,s5,u3 sig:", show(sig))

    # 3) ul=1 invariant: signal must equal the oscillator exactly (passthrough).
    o1, s1 = tsi_series(closes, q=2, r=20, s=5, u=3, ul=1)
    same = all((math.isnan(a) and math.isnan(b)) or a == b for a, b in zip(o1, s1))
    print("ul=1 -> signal == tsi exactly:", same)

    # 4) Order-independence invariant: TSI(r,s) ~= TSI(s,r) (Option B).
    #    The EMA stages commute in EXACT arithmetic, so the two orderings are
    #    equal up to IEEE-754 rounding (~1e-13) -- not bit-identical, because
    #    floating-point operations do not associate. Compare with a tolerance.
    a, _ = tsi_series(closes, q=2, r=20, s=5, u=1)
    b, _ = tsi_series(closes, q=2, r=5, s=20, u=1)
    same = all(
        (math.isnan(x) and math.isnan(y)) or math.isclose(x, y, abs_tol=1e-9)
        for x, y in zip(a, b)
    )
    print("order-independent (r,s)~=(s,r) within 1e-9:", same)
