"""Exponential Moving Average (Blau / EasyLanguage ``XAverage``).

This is the single most important *building block* in William Blau's
*Momentum, Direction, and Divergence* (1995) indicator family. Every Blau
indicator (TSI, SMI, DTI, Ergodic, CMI, ...) is constructed by **cascading**
this EMA two or three times. The code below is therefore meant to be **embedded
(inlined) verbatim** into each indicator implementation rather than imported as
a shared dependency -- so it is written to be trivially portable to Go, Rust,
TypeScript, and Zig.

Numerical contract (DO NOT change when porting -- see ``description.md`` §2):

    * Smoothing factor:  alpha = 2 / (period + 1)
    * Seed:              e_0 = x_0   (first output == first input; NO NaN warm-up)
    * Recursion (blend): e_k = alpha * x_k + (1 - alpha) * e_(k-1)
    * period == 1  =>  alpha == 1  =>  pure passthrough (e_k == x_k); this is a
      designed feature Blau uses to "switch off" a cascade stage, not an error.
    * period  < 1  =>  invalid (rejected at construction).

The recursion uses the *blend* form ``alpha*x + (1-alpha)*prev`` -- the literal
floating-point expression evaluated by the MQL5 reference port
(``WilliamBlau.mqh``) -- so that every language reproduces bit-identical values.

Standard library only: no numpy / pandas (keeps the port to Rust/Zig/Go 1:1).
"""

from __future__ import annotations


class ExponentialMovingAverage:
    """Stateful, streaming exponential moving average.

    One instance smooths exactly one series. Feed it one value at a time via
    :meth:`update`, which returns the EMA value for that bar. To build a
    cascade (e.g. ``EMA(EMA(x, r), s)``) create one instance per stage and wire
    each stage's output into the next stage's input.

    Example
    -------
    >>> ema = ExponentialMovingAverage(3)        # period 3 -> alpha = 0.5
    >>> [round(ema.update(x), 4) for x in (10.0, 12.0, 11.0)]
    [10.0, 11.0, 11.0]
    """

    # Instance attributes (declared here for readability / porting clarity):
    #   _alpha  : float  -- smoothing factor 2/(period+1), computed once.
    #   _prev   : float  -- the previous EMA output e_(k-1); valid once primed.
    #   _primed : bool   -- False until the first update() call seeds the state.

    def __init__(self, period: int) -> None:
        """Create an EMA of the given integer ``period`` (must be >= 1).

        ``period == 1`` is explicitly allowed and yields a pure passthrough.
        """
        if period < 1:
            # Matches the MQL5 reference guard ``if(period<1) return(0)``.
            raise ValueError(f"period must be >= 1, got {period!r}")

        # Smoothing factor alpha = 2 / (n + 1). For n == 1 this is exactly 1.0,
        # so the recursion collapses to e_k = x_k (passthrough). Computed once
        # and reused every bar.
        self._alpha: float = 2.0 / (float(period) + 1.0)

        # Previous EMA output. Meaningless until the first value primes it; we
        # initialise to 0.0 only so the attribute always exists.
        self._prev: float = 0.0

        # Whether the seed (e_0 = x_0) has been applied yet.
        self._primed: bool = False

    def update(self, x: float) -> float:
        """Feed one input value ``x`` and return this bar's EMA output.

        The first ever call seeds the EMA with ``x`` itself (``e_0 = x_0``) and
        returns it unchanged -- there is no NaN warm-up period. Every later
        call applies the blend recursion.
        """
        if not self._primed:
            # Seed: e_0 = x_0. First output equals first input.
            self._prev = x
            self._primed = True
            return self._prev

        # Recursion (blend form): e_k = alpha * x_k + (1 - alpha) * e_(k-1).
        # Written exactly like the MQL5 reference to preserve FP op order.
        e = self._alpha * x + (1.0 - self._alpha) * self._prev
        self._prev = e
        return e

    def reset(self) -> None:
        """Return the instance to its un-primed state (reuse on a new series)."""
        self._prev = 0.0
        self._primed = False


def ema_series(values, period):
    """Convenience: run a whole list through a fresh EMA and return the outputs.

    Not used by the indicators (they stream), but handy for demos / testing.
    """
    ema = ExponentialMovingAverage(period)
    return [ema.update(v) for v in values]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Small, human-readable demonstration of the three behaviours that    #
    # matter most when porting. (The full 252-bar reference-data harness  #
    # lives in the prepared-for-conversion copy of this file.)            #
    # ------------------------------------------------------------------ #
    sample = [10.0, 12.0, 11.0, 13.0, 12.0]

    # 1) Period 3 (alpha = 0.5): ordinary smoothing, primed from bar 0.
    print("period=3 :", [round(v, 4) for v in ema_series(sample, 3)])

    # 2) Period 1: pure passthrough -- output equals input exactly.
    passthrough = ema_series(sample, 1)
    print("period=1 :", passthrough, "(passthrough ==", sample == passthrough, ")")

    # 3) Double smoothing cascade EMA(EMA(x, 3), 2) via two wired instances.
    stage1 = ExponentialMovingAverage(3)
    stage2 = ExponentialMovingAverage(2)
    cascade = [stage2.update(stage1.update(v)) for v in sample]
    print("DEMA(3,2):", [round(v, 4) for v in cascade])
