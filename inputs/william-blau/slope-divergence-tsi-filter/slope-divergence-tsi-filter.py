"""Slope Divergence TSI Filter (SD_TSI) -- William Blau (book Ch. 12).

A trend/congestion prefilter built on the True Strength Index. It keeps the TSI
value ONLY when the slope of the TSI agrees in sign with the slope of a separate
double EMA of price; otherwise it outputs 0 (a "slope divergence" / congestion
zone). Self-contained:

    SD_TSI(close, r, s, u, x, y):
        ind = TSI(close, q, r, s, u)             # triple-smoothed bipolar TSI
        ref = DEMA(close, x, y) = EMA(EMA(close, x), y)   # double EMA on price
        keep = (ind rising  AND ref rising)  -> ind
               (ind falling AND ref falling) -> ind
               otherwise                     -> 0.0

This differs in spirit from the Chapter-8 `_Trade` filter (Nonambiguous Trend
Filter): `_Trade` compares an oscillator to ITS OWN slope (single series). SD_TSI
compares the slope of the oscillator against the slope of a SEPARATE price moving
average -- that is what isolates congestion, where the price moving-average keeps
rising while momentum rolls over (their slopes diverge).

Definition source -- EasyLanguage Appendix B Figure B-25 (verbatim logic):

    Value1 = TSI(Price,r,s,u) ;
    Value2 = DXAverage(Price,x,y) ;          { = EMA(EMA(Price,x),y) }
    if Value1 - Value1[1] > 0 AND Value2 - Value2[1] > 0 then Value3 = Value1 else Value3 = 0;
    if Value1 - Value1[1] < 0 AND Value2 - Value2[1] < 0 then Value4 = Value1 else Value4 = 0;
    SD_TSI = Value3 + Value4 ;

The gate is STRICT: a flat slope (delta == 0) on either series is NOT kept (the
two `if` tests use strict `> 0` / `< 0`), so a tie always yields 0.0.

The EMA primitive and the TSI/DEMA machinery are **embedded** (inlined, not
imported) so this file is a self-contained porting unit -- agents porting to
Go/Rust/TS/Zig need only this file and ``description.md``.

Priming / warm-up (Option B, matches the rest of the library):
    * The TSI momentum needs a price q-1 bars back, so the TSI (hence SD_TSI) is
      ``float('nan')`` for bars 0..q-2 and finite from bar q-1. With the book's
      q = 2 (one-bar momentum) that is a single NaN at bar 0.
    * The price DEMA seeds at bar 0 (no NaN) and advances every bar.
    * At the FIRST finite TSI bar there is no prior TSI value -> no slope -> the
      output is 0.0 (you need two finite TSI samples before a slope exists).

TSI division guard: denominator (TEMA of |momentum|) == 0 -> TSI 0.0.

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
# INDICATOR: Slope Divergence TSI Filter.                                 #
# ====================================================================== #
class SlopeDivergenceTsiFilter:
    """Stateful, streaming Slope Divergence TSI Filter (SD_TSI).

    Feed one ``close`` at a time to :meth:`update`, which returns the filtered
    value for that bar: ``float('nan')`` during the TSI momentum warm-up
    (bars 0..q-2), then either the live TSI value (trend retained) or ``0.0``
    (slope divergence / congestion). The output range is [-100, +100].

    Example (book q=2; full passthrough r=s=u=1, x=y=1 -> TSI is +/-100 = the
    sign of one-bar momentum, ref is the close itself):
    >>> sd = SlopeDivergenceTsiFilter(q=2, r=1, s=1, u=1, x=1, y=1)
    >>> import math
    >>> math.isnan(sd.update(10.0))   # bar 0: momentum undefined -> NaN
    True
    >>> sd.update(12.0)               # bar 1: first finite TSI, no slope yet -> 0.0
    0.0
    >>> sd.update(11.0)               # bar 2: TSI -100 falling, price falling -> keep -100
    -100.0
    >>> sd.update(13.0)               # bar 3: TSI +100 rising, price rising -> keep +100
    100.0
    """

    def __init__(self, q: int = 2, r: int = 32, s: int = 32, u: int = 7,
                 x: int = 32, y: int = 7) -> None:
        """Create an SD_TSI.

        ``q`` momentum look-back (book uses q=2, one-bar momentum); ``r,s,u`` are
        the TSI EMA periods; ``x,y`` are the price double-EMA periods. The book's
        recommended noise-cleaned setting is SD_TSI(close, 32, 32, 7, 32, 7)
        (Fig. 12-2); the raw form of Fig. 12-1 is SD_TSI(close, 32, 32, 1, 32, 1).
        """
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        # r, s, u, x, y are validated by the EMA constructors below.
        self._q = q

        # Rolling window of recent prices for the q-period momentum.
        self._history: deque[float] = deque(maxlen=q)

        # --- TSI machinery: two chained 3-stage EMA cascades (TEMA). --------- #
        # Numerator: TEMA(momentum, r, s, u); denominator: TEMA(|momentum|).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

        # --- Price reference: DEMA(close, x, y) = EMA(EMA(close, x), y). ----- #
        self._ref_x = ExponentialMovingAverage(x)
        self._ref_y = ExponentialMovingAverage(y)

        # --- Slope state (previous-bar samples for the two series). --------- #
        self._prev_tsi: float = 0.0      # previous finite TSI; valid once primed
        self._have_prev_tsi: bool = False
        self._prev_ref: float = 0.0      # previous-bar price DEMA
        self._have_prev_ref: bool = False

    def update(self, price: float) -> float:
        """Feed one close ``price`` and return this bar's SD_TSI value."""
        # 1) Advance the price DEMA every bar (it never has a NaN warm-up). ---- #
        ref = self._ref_y.update(self._ref_x.update(price))

        # 2) Compute the TSI for this bar (NaN during the momentum warm-up). --- #
        self._history.append(price)
        if len(self._history) < self._q:
            # TSI undefined: propagate NaN. The DEMA keeps advancing so we keep
            # its previous-bar value current for when the TSI comes online.
            self._prev_ref = ref
            self._have_prev_ref = True
            return float("nan")

        # mtm_k = C_k - C_(k-(q-1)); leftmost deque element is C_(k-(q-1)).
        mtm = price - self._history[0]
        abs_mtm = abs(mtm)
        n = self._num_u.update(self._num_s.update(self._num_r.update(mtm)))
        d = self._den_u.update(self._den_s.update(self._den_r.update(abs_mtm)))
        # TSI division guard (Blau_TSI): denominator 0 -> 0.0.
        tsi = 0.0 if d == 0.0 else 100.0 * n / d

        # 3) Slope-divergence gate (Fig. B-25, strict inequalities). ---------- #
        if not self._have_prev_tsi:
            # First finite TSI sample: no prior TSI -> no slope -> output 0.0.
            result = 0.0
        else:
            d_tsi = tsi - self._prev_tsi
            d_ref = ref - self._prev_ref
            # Keep the TSI only when BOTH slopes are strictly same-signed:
            # (rising, rising) or (falling, falling). Ties (delta == 0) -> 0.0.
            if (d_tsi > 0.0 and d_ref > 0.0) or (d_tsi < 0.0 and d_ref < 0.0):
                result = tsi
            else:
                result = 0.0

        # 4) Roll slope state forward (both series are finite from here on). -- #
        self._prev_tsi = tsi
        self._have_prev_tsi = True
        self._prev_ref = ref
        self._have_prev_ref = True
        return result


def sd_tsi_series(values, q=2, r=32, s=32, u=7, x=32, y=7):
    """Convenience: run a whole list of closes through a fresh SD_TSI."""
    sd = SlopeDivergenceTsiFilter(q=q, r=r, s=s, u=u, x=x, y=y)
    return [sd.update(v) for v in values]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo of the behaviours that matter most when         #
    # porting. (The full 252-bar reference-data harness lives in the      #
    # prepared-for-conversion copy of this file.)                         #
    # ------------------------------------------------------------------ #
    # A rally, then a congestion plateau, then a decline. During the trends
    # the TSI slope and the price-DEMA slope agree, so the TSI is retained.
    # Across the plateau the price DEMA keeps drifting while momentum rolls
    # over -> slopes diverge -> SD_TSI returns to 0 (congestion detected).
    # Moderate periods (r=s=4, x=4) so the smoothing responds within the demo.
    rally = [10.0, 10.8, 11.7, 12.9, 14.2, 15.6, 17.1]
    plateau = [17.2, 17.0, 17.3, 17.1, 17.2, 17.0]
    decline = [16.2, 15.0, 13.7, 12.4, 11.0, 9.7, 8.5]
    closes = rally + plateau + decline

    def show(label, series):
        print(label, ["nan" if math.isnan(v) else round(v, 2) for v in series])

    # 1) Book noise-cleaned default shape, scaled down: SD_TSI(4,4,2,4,2).
    show("SD_TSI(4,4,2,4,2):", sd_tsi_series(closes, q=2, r=4, s=4, u=2, x=4, y=2))

    # 2) Raw double-smoothed (u=1, y=1), faster response: SD_TSI(4,4,1,4,1).
    show("SD_TSI(4,4,1,4,1):", sd_tsi_series(closes, q=2, r=4, s=4, u=1, x=4, y=1))

    # 3) Passthrough (r=s=u=1, x=y=1): TSI = +/-100 (sign of one-bar momentum),
    #    ref = close. The gate keeps +/-100 only while the TSI slope (a momentum
    #    sign-flip) and the price slope agree.
    show("SD_TSI(1,1,1,1,1):", sd_tsi_series(closes, q=2, r=1, s=1, u=1, x=1, y=1))
