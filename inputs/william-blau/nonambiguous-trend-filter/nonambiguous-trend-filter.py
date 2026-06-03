"""Nonambiguous Trend Filter (`_Trade`) -- William Blau (book Ch. 8 / Appendix B).

A generic post-processing transform applied to any normalized, signed oscillator
X (TSI, SMI, DTI, MDI, CMI, CSI, ...). It keeps X only where its sign and slope
agree, and zeroes every ambiguous bar:

    X_Trade[k] = X[k]   if  X[k] > 0  AND  X[k] - X[k-1] > 0    (positive & rising)
               = X[k]   if  X[k] < 0  AND  X[k] - X[k-1] < 0    (negative & falling)
               = 0      otherwise                               (ambiguous)

The nonzero stretches of X_Trade correspond one-to-one with genuine up/down
trends; congestion and flat regions are blanked to zero. This is Blau's
EasyLanguage user function (Appendix B, Figures B-20..B-23); there is no MQL5
version.

The filter holds NO embedded moving averages -- it operates purely on the value
stream of a base indicator (which it does not need to know anything about). It is
therefore a tiny, base-agnostic, self-contained porting unit: a porting agent
needs only this file and ``description.md``.

Conventions (Option B, consistent with the rest of the library):
  * First finite bar  -> no prior slope -> output 0.0 (cannot confirm trend).
  * NaN base value    -> output NaN, and state is NOT updated (the base is still
                         in its own look-back warm-up; e.g. SMI/DTI bars 0..q-2).
  * Strict slope: a flat step (delta == 0) is neither rising nor falling -> 0.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math


# ====================================================================== #
# FILTER: Nonambiguous Trend Filter (the `_Trade` transform).             #
# ====================================================================== #
class NonambiguousTrendFilter:
    """Stateful, streaming `_Trade` filter over a base oscillator's values.

    Feed one base indicator value at a time to :meth:`update`. The filter returns
    the value unchanged where it is positive-and-rising or negative-and-falling,
    and 0.0 otherwise. A NaN input (base still warming up) yields NaN and leaves
    the filter state untouched.

    Example (a small signed ramp): seed bar -> 0.0, then keep rising-positive and
    falling-negative, zero the ambiguous bars.
    >>> f = NonambiguousTrendFilter()
    >>> [f.update(x) for x in (10.0, 20.0, 15.0, -5.0, -12.0, -3.0)]
    [0.0, 20.0, 0.0, -5.0, -12.0, 0.0]

    Example (NaN warm-up is propagated, then the first finite bar seeds at 0.0):
    >>> import math
    >>> f = NonambiguousTrendFilter()
    >>> out = [f.update(x) for x in (float('nan'), float('nan'), 5.0, 9.0)]
    >>> math.isnan(out[0]) and math.isnan(out[1])
    True
    >>> out[2:]
    [0.0, 9.0]
    """

    def __init__(self) -> None:
        # Last finite base value seen, and whether we have seen one yet. Using a
        # (prev, primed) pair (rather than None) keeps the port to Go/Rust/Zig
        # trivial -- there is no nullable float to model.
        self._prev: float = 0.0
        self._primed: bool = False

    def update(self, x: float) -> float:
        """Feed one base indicator value ``x``; return the filtered value."""
        # NaN test via the portable idiom ``x != x`` (true only for NaN). The
        # base is undefined here (still in its look-back warm-up): emit NaN and
        # do NOT advance the slope state, so the first finite bar afterwards is
        # treated as the seed.
        if x != x:
            return float("nan")

        if not self._primed:
            # First finite value: there is no prior bar, so the slope is
            # undefined -> cannot confirm a trend -> 0.0. Seed the state.
            self._prev = x
            self._primed = True
            return 0.0

        # Slope of the base relative to the previous finite bar.
        delta = x - self._prev
        self._prev = x

        # Retain only the two unambiguous cases; zero everything else.
        if x > 0.0 and delta > 0.0:
            return x          # positive and rising
        if x < 0.0 and delta < 0.0:
            return x          # negative and falling
        return 0.0            # ambiguous / flat / congestion


def trade_filter_series(values):
    """Convenience: run a whole list of base indicator values through a filter."""
    f = NonambiguousTrendFilter()
    return [f.update(v) for v in values]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo of the behaviours that matter most when         #
    # porting. (The full 252-bar reference-data harness -- which composes #
    # the filter with real TSI/SMI/DTI/MDI/CMI/CSI base indicators -- lives#
    # in the prepared-for-conversion copy of this file.)                  #
    # ------------------------------------------------------------------ #
    nan = float("nan")

    # 1) Signed ramp: bar0 seeds to 0.0; keep positive+rising and negative+falling.
    ramp = [10.0, 20.0, 15.0, 8.0, -5.0, -12.0, -3.0, -1.0, 4.0]
    print("ramp        :", trade_filter_series(ramp))

    # 2) Flat steps (delta == 0) are ambiguous -> zeroed.
    flat = [5.0, 5.0, 5.0, 6.0]
    print("flat steps  :", trade_filter_series(flat))

    # 3) NaN warm-up (e.g. SMI/DTI look-back) is propagated; first finite -> 0.0.
    warm = [nan, nan, nan, 7.0, 11.0, 9.0]
    out = trade_filter_series(warm)
    print("warm-up     :", ["nan" if math.isnan(v) else v for v in out])
