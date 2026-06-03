"""ADX-Type Filter (ATF) -- William Blau (book Figure B-24).

A non-negative "trend-strength" filter, analogous to Wilder's ADX, built by
rectifying and double-smoothing a *bipolar momentum* series:

    ATF(Price, r, s) = EMA( |EMA(Price, r)| , s )

(in Blau's EasyLanguage: ``XAverage(AbsValue(XAverage(Price, r)), s)``).

``Price`` is any *bipolar* (signed) momentum/oscillator. The inner EMA(r)
smooths it, the absolute value rectifies it (discarding direction, keeping
amplitude), and the outer EMA(s) smooths the amplitude. A rising ATF means a
strengthening trend; a falling ATF means a weakening / ranging market -- exactly
the ADX interpretation (LeBeau & Lucas: the *slope* matters more than the level).

The canonical bipolar inputs Blau lists (Fig B-24) are:
    * ``C - C[q-1]``                      -- the TSI numerator (price momentum)
    * ``HMU - LMD``                       -- the DTI numerator (high-low momentum)
    * ``Upticks - Downticks``             -- TVI
    * ``C - 0.5*(HH(q) + LL(q))``         -- the SMI raw stochastic momentum
A *single-smoothed normalized* indicator (e.g. ``TSI(price, r, 1, 1)``) may also
be used as ``Price``; it then *replaces* the inner ``EMA(Price, r)`` -- which is
exactly :class:`AdxTypeFilter` with ``r = 1`` (inner EMA passthrough),
``ATF = EMA(|Price|, s)``.

This module provides:
    * :class:`AdxTypeFilter`  -- the generic book function, on any bipolar series.
    * :class:`TsiAtf`         -- TSI_ATF: ATF on the TSI numerator ``C - C[q-1]``.
    * :class:`SmiAtf`         -- SMI_ATF: ATF on ``C - 0.5*(HH(q) + LL(q))``.

The EMA primitive is **embedded** below (inlined, not imported) so this file is a
self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * Each EMA stage seeds on its first received (finite) value.
    * A leading NaN in ``Price`` (e.g. the TSI/SMI momentum during its look-back
      warm-up) is **propagated**: ATF returns NaN and the EMAs do not advance
      until the first finite input, at which point both stages seed.
    * Output is always **>= 0** (it is a smoothed absolute value).

There is NO division in this indicator, hence no division guard.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math
from collections import deque


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
# GENERIC INDICATOR: ADX-Type Filter (book Fig B-24).                     #
# ====================================================================== #
class AdxTypeFilter:
    """Stateful, streaming generic ATF: ``EMA(|EMA(x, r)|, s)``.

    Feed one *bipolar momentum* value ``x`` at a time to :meth:`update`. Leading
    NaNs are propagated (returned as NaN; the internal EMAs wait to seed). The
    output is always ``>= 0``.

    ``r = 1`` makes the inner EMA a passthrough, giving the normalized-indicator
    form ``EMA(|x|, s)`` (Blau's note: feed a single-smoothed normalized
    oscillator such as TSI(price, r, 1, 1)).

    Example (r = s = 1: both EMAs passthrough -> ATF == |x|):
    >>> f = AdxTypeFilter(r=1, s=1)
    >>> f.update(2.0)
    2.0
    >>> f.update(-3.0)
    3.0
    >>> f.update(-1.5)
    1.5
    """

    def __init__(self, r: int = 32, s: int = 32) -> None:
        """Create an ATF with inner EMA period ``r`` and outer EMA period ``s``."""
        # r, s are validated by the EMA constructors.
        self._inner = ExponentialMovingAverage(r)
        self._outer = ExponentialMovingAverage(s)

    def update(self, x: float) -> float:
        """Feed one bipolar momentum ``x`` and return this bar's ATF (or NaN)."""
        # Propagate a leading NaN: do NOT advance the EMAs until the first finite
        # input, so both stages seed on the first real momentum value.
        if math.isnan(x):
            return float("nan")
        # Inner smooth -> rectify -> outer smooth.
        return self._outer.update(abs(self._inner.update(x)))


def atf_series(values, r=32, s=32):
    """Convenience: run a whole bipolar-momentum list through a fresh ATF."""
    f = AdxTypeFilter(r=r, s=s)
    return [f.update(v) for v in values]


# ====================================================================== #
# NAMED INSTANCE: TSI_ATF -- ATF on the TSI numerator momentum.           #
# ====================================================================== #
class TsiAtf:
    """TSI_ATF: ATF applied to the TSI numerator ``mtm = C - C[q-1]``.

    ``TSI_ATF(close, q, r, s) = EMA(|EMA(C - C[q-1], r)|, s)``.

    update(close) -> NaN for bars 0..q-2 (momentum look-back), then a finite
    value >= 0. Defaults q=2, r=32, s=32 (catalog TSI_ATF example r=32).

    Example (q=2, r=s=1: ATF == |C - C[1]|):
    >>> import math
    >>> a = TsiAtf(q=2, r=1, s=1)
    >>> math.isnan(a.update(10.0))     # bar 0: momentum undefined
    True
    >>> a.update(12.0)                 # mtm = +2 -> |2| = 2
    2.0
    >>> a.update(11.0)                 # mtm = -1 -> |-1| = 1
    1.0
    """

    def __init__(self, q: int = 2, r: int = 32, s: int = 32) -> None:
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        self._q = q
        # Window of q closes so the leftmost element is C_(k-(q-1)).
        self._hist: deque[float] = deque(maxlen=q)
        self._atf = AdxTypeFilter(r=r, s=s)

    def update(self, close: float) -> float:
        self._hist.append(close)
        if len(self._hist) < self._q:
            return float("nan")
        mtm = close - self._hist[0]           # TSI numerator momentum
        return self._atf.update(mtm)


def tsi_atf_series(closes, q=2, r=32, s=32):
    """Convenience: run closes through a fresh TSI_ATF."""
    a = TsiAtf(q=q, r=r, s=s)
    return [a.update(c) for c in closes]


# ====================================================================== #
# NAMED INSTANCE: SMI_ATF -- ATF on the SMI raw stochastic momentum.      #
# ====================================================================== #
class SmiAtf:
    """SMI_ATF: ATF applied to ``sm = C - 0.5*(HH(q) + LL(q))``.

    where HH(q)/LL(q) are the highest high / lowest low over the last q bars:

        SMI_ATF(q, r, s) = EMA(|EMA(C - 0.5*(HH(q) + LL(q)), r)|, s).

    update(high, low, close) -> NaN for bars 0..q-2 (the q-bar HH/LL look-back),
    then a finite value >= 0. Defaults q=32, r=32, s=32 (catalog SMI_ATF example
    q=32, r=32).

    Example (q=1: HH=high, LL=low, so sm = C - 0.5*(H+L); r=s=1 -> ATF = |sm|):
    >>> a = SmiAtf(q=1, r=1, s=1)
    >>> a.update(11.0, 9.0, 10.5)      # sm = 10.5 - 0.5*(11+9) = 0.5
    0.5
    """

    def __init__(self, q: int = 32, r: int = 32, s: int = 32) -> None:
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        self._q = q
        self._highs: deque[float] = deque(maxlen=q)
        self._lows: deque[float] = deque(maxlen=q)
        self._atf = AdxTypeFilter(r=r, s=s)

    def update(self, high: float, low: float, close: float) -> float:
        self._highs.append(high)
        self._lows.append(low)
        if len(self._highs) < self._q:
            return float("nan")
        hh = max(self._highs)                 # highest high over q bars
        ll = min(self._lows)                  # lowest low over q bars
        sm = close - 0.5 * (hh + ll)          # SMI raw stochastic momentum
        return self._atf.update(sm)


def smi_atf_series(highs, lows, closes, q=32, r=32, s=32):
    """Convenience: run H/L/C through a fresh SMI_ATF."""
    a = SmiAtf(q=q, r=r, s=s)
    return [a.update(h, l, c) for h, l, c in zip(highs, lows, closes)]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo of the behaviours that matter most when         #
    # porting. (The full 252-bar reference-data harness lives in the      #
    # prepared-for-conversion copy of this file.)                         #
    # ------------------------------------------------------------------ #
    closes = [10.0, 12.0, 11.0, 13.0, 12.0, 12.0, 15.0, 14.0, 16.0, 18.0]

    def show(xs):
        return ["nan" if math.isnan(v) else round(v, 4) for v in xs]

    # 1) Generic ATF on a raw bipolar momentum (C - C[1]), default smoothing.
    mtm = [float("nan")] + [closes[k] - closes[k - 1] for k in range(1, len(closes))]
    print("ATF(mtm,32,32) :", show(atf_series(mtm, r=32, s=32)))

    # 2) TSI_ATF default (q=2, r=32, s=32) -- equals (1) since mtm = C - C[1].
    print("TSI_ATF default:", show(tsi_atf_series(closes, q=2, r=32, s=32)))

    # 3) ATF is always non-negative (it is a smoothed absolute value).
    vals = [v for v in tsi_atf_series(closes, q=2, r=8, s=8) if not math.isnan(v)]
    print("all ATF >= 0   :", all(v >= 0.0 for v in vals))

    # 4) r = s = 1 -> ATF == |momentum| (both EMAs passthrough).
    a11 = tsi_atf_series(closes, q=2, r=1, s=1)
    ok = all(
        (math.isnan(v) and math.isnan(m)) or abs(v - abs(m)) < 1e-12
        for v, m in zip(a11, mtm)
    )
    print("r=s=1 -> |mtm| :", ok)
