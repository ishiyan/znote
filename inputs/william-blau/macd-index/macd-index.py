"""MACD Index (MACD_I) -- William Blau (book ch. 5 / Appendix B-13).

Blau's MACD line is the difference of two EMAs of the close, optionally smoothed
by a third EMA, paired with an EMA signal line (the Ergodic form, Blau ch. 5):

    macd_k   = EMA(close, s)_k - EMA(close, r)_k         (MACD line; s fast, r slow)
    macdi_k  = EMA(macd, u)_k                            (the MACD_I line)
    signal_k = EMA(macdi, ul)_k                          (ul-period EMA)

with the **fast** period ``s`` strictly shorter than the **slow** period ``r``
(``s < r``). The book (ch. 5) defines the pure form
``MACD(close, r, s) = EMA(close, s) - EMA(close, r)``; the MQL5 ``Blau_MACD.mq5``
code adds the third smoothing ``u``, giving the form above. Set ``u = 1`` to
recover the book's pure two-EMA MACD line. Blau notes the MACD and the MDI are
both double-smoothed momentum indicators with nearly interchangeable shapes
(within a scale factor).

**It is NOT normalized.** There is no ``100 * TEMA/TEMA`` ratio and no fixed
range: the output is in the same price units as the input (the classic MACD line)
and can take any sign or magnitude. **Input is a single price series (Close).**

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(macdi, signal)`` and :func:`macd_i_series` returns two parallel lists.

The EMA primitive is **embedded** below (inlined, not imported) so this file is a
self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming: both price EMAs are defined from bar 0 (they seed at ``close_0``), so the
MACD line is ``0.0`` at bar 0 and finite on every bar. There is therefore NO NaN
warm-up region. The ``u`` smoothing and the signal EMA likewise seed on bar 0.

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
# INDICATOR: MACD Index (two-output: line + signal).                      #
# ====================================================================== #

# Two-output result. ``macdi`` is the MACD_I line; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both are finite from bar 0 (no NaN warm-up)
# and both are in raw price units (NOT bounded to any range).
MacdiResult = namedtuple("MacdiResult", ["macdi", "signal"])


class MacdIndex:
    """Stateful, streaming Blau MACD (MACD_I) with an EMA signal line.

    Feed one ``close`` at a time to :meth:`update`, which returns a
    :class:`MacdiResult` ``(macdi, signal)`` for that bar. Both fields are finite
    on EVERY bar (there is no NaN warm-up; bar 0 is 0.0) and in **raw price
    units** (NOT bounded to any range).

    Example (r=2 slow, s=1 fast, u=1 -> book pure MACD line, ul=1 passthrough):
    >>> m = MacdIndex(r=2, s=1, u=1, ul=1)
    >>> o0 = m.update(10.0); (round(o0.macdi, 4), round(o0.signal, 4))  # bar 0
    (0.0, 0.0)
    >>> o1 = m.update(12.0); (round(o1.macdi, 4), round(o1.signal, 4))  # 12-11.3333
    (0.6667, 0.6667)

    Example (s >= r is rejected -- fast must be strictly shorter than slow):
    >>> MacdIndex(r=5, s=5)
    Traceback (most recent call last):
        ...
    ValueError: s (fast) must be < r (slow); got s=5, r=5
    """

    def __init__(self, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create a MACD_I with slow period ``r``, fast period ``s`` (``s < r``),
        smoothing period ``u`` and signal-line period ``ul``.

        Defaults are the MQL5/book defaults (r=20 slow, s=5 fast, u=3) plus the
        Ergodic signal default ul=3. Set ``u=1`` for the book's pure two-EMA
        MACD line ``EMA(close, s) - EMA(close, r)``; set ``ul=1`` for a
        passthrough signal (signal == macdi).

        Raises ``ValueError`` if ``s >= r`` -- the MACD line is fast minus slow,
        so the fast period must be strictly shorter than the slow period
        (``s == r`` gives an identically-zero line; ``s > r`` flips the sign).
        """
        if s >= r:
            raise ValueError(
                f"s (fast) must be < r (slow); got s={s!r}, r={r!r}"
            )
        # r, s, u, ul are validated by the EMA constructors below.

        # The two price EMAs forming the MACD line = EMA(close, s) - EMA(close, r).
        self._ema_fast = ExponentialMovingAverage(s)
        self._ema_slow = ExponentialMovingAverage(r)

        # Third smoothing EMA applied to the MACD line: EMA(macd, u).
        self._smooth_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the MACD_I line. The line is finite
        # from bar 0, so this seeds on bar 0 -- no NaN warm-up.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, close: float) -> MacdiResult:
        """Feed one ``close``; return (macdi, signal) for this bar."""
        # MACD line = fast EMA - slow EMA. Both seed at bar 0 (to close_0), so
        # the line is 0.0 on bar 0 and defined on every bar thereafter.
        macd = self._ema_fast.update(close) - self._ema_slow.update(close)

        # Smooth the MACD line: EMA(macd, u). No normalization, no guard.
        macdi = self._smooth_u.update(macd)

        # Signal line = EMA(macdi, ul); seeds on bar 0's line value.
        signal = self._signal_ema.update(macdi)
        return MacdiResult(macdi, signal)


def macd_i_series(values, r=20, s=5, u=3, ul=3):
    """Convenience: run a whole list of closes through a fresh MACD_I.

    Returns two parallel lists: ``(macdi_values, signal_values)``.
    """
    m = MacdIndex(r=r, s=s, u=u, ul=ul)
    out = [m.update(v) for v in values]
    return [o.macdi for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo of the behaviours that matter most when         #
    # porting. (The full 252-bar reference-data harness lives in the      #
    # prepared-for-conversion copy of this file.)                         #
    # ------------------------------------------------------------------ #
    closes = [10.0, 12.0, 11.0, 13.0, 12.0, 12.0, 15.0, 14.0, 16.0, 18.0]

    def show(xs):
        return ["nan" if math.isnan(v) else round(v, 4) for v in xs]

    # 1) Book pure MACD line (u=1): EMA(close, s) - EMA(close, r).
    osc, sig = macd_i_series(closes, r=20, s=5, u=1)
    print("r20,s5,u1  osc:", show(osc))
    print("r20,s5,u1  sig:", show(sig))

    # 2) MQL5/book default triple form (line + ul=3 signal line).
    d_osc, d_sig = macd_i_series(closes, r=20, s=5, u=3)
    print("r20,s5,u3  osc:", show(d_osc))
    print("r20,s5,u3  sig:", show(d_sig))

    # 3) No NaN warm-up: every bar is finite (the MACD line is defined from bar 0).
    print("all finite (no NaN warm-up):",
          all(not math.isnan(v) for v in d_osc + d_sig))

    # 4) ul=1 passthrough: signal == line on every bar.
    p_osc, p_sig = macd_i_series(closes, r=20, s=5, u=3, ul=1)
    print("ul=1 passthrough holds:", p_osc == p_sig)

    # 5) s >= r is rejected (fast must be strictly shorter than slow).
    try:
        MacdIndex(r=12, s=26)
        print("s>=r guard: FAILED to raise")
    except ValueError as e:
        print("s>=r guard raises:", e)
