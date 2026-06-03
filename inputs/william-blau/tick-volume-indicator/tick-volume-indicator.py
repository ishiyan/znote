"""Tick Volume Indicator (TVI) -- William Blau (book Ch. 4 / Ch. 10).

A normalized, double-/triple-smoothed oscillator built from the balance of
upticks vs downticks inside each high-low bar, bounded to [-100, +100]:

    TVI(r, s, u) = 100 * (TEMA(up, r, s, u) - TEMA(down, r, s, u))
                       / (TEMA(up, r, s, u) + TEMA(down, r, s, u))

where
    TEMA(x, r, s, u) = EMA(EMA(EMA(x, r), s), u)          (triple EMA cascade)

The TVI is gap-immune: it is built from intra-bar tick direction, not from the
close vs a previous close, so opening gaps do not bias it.

  * u = 1 recovers Blau's book double-smoothed TVI(r, s), because EMA(.,1) is a
    passthrough so TEMA(x, r, s, 1) = DEMA(x, r, s) = EMA(EMA(x, r), s). The
    default is u = 1; Chapter 10's TVI_Trade uses TVI(32, 32, 5).
  * By linearity of the EMA, TEMA(up) +/- TEMA(down) = TEMA(up +/- down), so this
    separate-cascade form equals Blau's alternate "double EMA of the difference
    over double EMA of the sum" form.

INPUTS: two non-negative per-bar series, ``upticks`` and ``downticks`` (counts of
up/down ticks within the bar). The shared test fixtures supply a deterministic
SYNTHETIC proxy derived from the bar range -- up = close - low, down = high -
close -- because the 252-bar dataset has no real tick data. A production caller
passes genuine tick counts.

The EMA primitive is **embedded** below (inlined, not imported) so this file is
a self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

There is NO NaN warm-up region (the EMAs seed at bar 0). Division guard:
denominator == 0 (a fully flat market) -> output 0.0.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math


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
# INDICATOR: Tick Volume Indicator.                                       #
# ====================================================================== #
class TickVolumeIndicator:
    """Stateful, streaming Tick Volume Indicator.

    Feed one (upticks, downticks) pair at a time to :meth:`update`, which returns
    the TVI value for that bar -- a finite value in [-100, +100]. There is no NaN
    warm-up region (both cascades seed at bar 0).

    Example (all stages passthrough -> raw normalized tick balance):
    >>> tvi = TickVolumeIndicator(r=1, s=1, u=1)
    >>> tvi.update(8.0, 2.0)    # 8 up vs 2 down: 100*(8-2)/(8+2) = 60
    60.0
    >>> tvi.update(0.0, 5.0)    # all down: 100*(0-5)/(0+5) = -100
    -100.0
    >>> tvi.update(0.0, 0.0)    # flat market: denominator 0 -> guard -> 0.0
    0.0
    """

    def __init__(self, r: int = 12, s: int = 12, u: int = 1) -> None:
        """Create a TVI with EMA periods ``r, s, u`` (book defaults 12,12,1).

        ``u = 1`` (default) gives the book double-smoothed TVI(r, s); set
        ``u`` > 1 for the Chapter-10 triple-smoothed form, e.g. TVI(32, 32, 5).
        """
        # r, s, u are validated by the EMA constructors below.

        # Two independent 3-stage EMA cascades: one for upticks, one for
        # downticks. Each is wired output -> input:
        # TEMA(x) = stage_u(stage_s(stage_r(x))).
        self._up_r = ExponentialMovingAverage(r)
        self._up_s = ExponentialMovingAverage(s)
        self._up_u = ExponentialMovingAverage(u)
        self._dn_r = ExponentialMovingAverage(r)
        self._dn_s = ExponentialMovingAverage(s)
        self._dn_u = ExponentialMovingAverage(u)

    def update(self, upticks: float, downticks: float) -> float:
        """Feed this bar's ``upticks``/``downticks`` and return this bar's TVI."""
        # Smooth each tick stream through its own TEMA cascade.
        tu = self._up_u.update(self._up_s.update(self._up_r.update(upticks)))
        td = self._dn_u.update(self._dn_s.update(self._dn_r.update(downticks)))

        den = tu + td
        # Division guard (Appendix B): fully flat smoothed volume -> output 0.0.
        if den == 0.0:
            return 0.0
        return 100.0 * (tu - td) / den


def tvi_series(upticks, downticks, r=12, s=12, u=1):
    """Convenience: run aligned uptick/downtick lists through a fresh TVI."""
    tvi = TickVolumeIndicator(r=r, s=s, u=u)
    return [tvi.update(up, dn) for up, dn in zip(upticks, downticks)]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo of the behaviours that matter most when         #
    # porting. (The full 252-bar reference-data harness lives in the      #
    # prepared-for-conversion copy of this file.)                         #
    # ------------------------------------------------------------------ #
    # Synthetic tick proxy from a few OHLC bars: up = close-low, down = high-close.
    bars = [  # (high, low, close)
        (10.0, 8.0, 9.5), (11.0, 9.0, 9.2), (12.0, 10.0, 11.8),
        (11.5, 10.5, 10.6), (13.0, 11.0, 12.0),
    ]
    up = [c - l for (h, l, c) in bars]
    dn = [h - c for (h, l, c) in bars]

    # 1) Book double-smoothed default (u=1).
    print("TVI(12,12,1):", [round(v, 4) for v in tvi_series(up, dn, 12, 12, 1)])

    # 2) Chapter-10 triple-smoothed form.
    print("TVI(32,32,5):", [round(v, 4) for v in tvi_series(up, dn, 32, 32, 5)])

    # 3) Passthrough (r=s=u=1): raw normalized tick balance per bar.
    print("TVI(1,1,1)  :", [round(v, 4) for v in tvi_series(up, dn, 1, 1, 1)])
