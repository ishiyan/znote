"""Double-Smoothed Momenta (DM) / Double-Smoothed RSI (DRSI) -- William Blau.

A close-based, double-smoothed momentum oscillator bounded to [0, 100]:

    LCa_k = min(Close over the last a bars)          (lowest close)
    HCa_k = max(Close over the last a bars)          (highest close)
    st_k  = Close_k - LCa_k                           (close above the low close)
    rng_k = HCa_k - LCa_k                             (a-bar close range)

    DM(a, y, z) = 100 * EMA(EMA(st, y), z) / EMA(EMA(rng, y), z)

i.e. each of the numerator (st) and denominator (rng) series is double-smoothed
by an inner EMA of period ``y`` then an outer EMA of period ``z`` (Blau's
Ez(Ey(.)) ), and the ratio is scaled by 100.

This is structurally the Double-Smoothed Stochastic (DS-Stochastic) computed on
the CLOSE -- it uses the highest/lowest *close* over ``a`` bars instead of the
high/low of the bar -- and it has NO signal line (single output per bar).

Two named instances (catalog Group 10):
    * RSI equivalence:  DM(2, 1, z) == RSI(z), the EMA-form RSI (see below).
    * Double-smoothed RSI:  DRSI(y, z) = DM(2, y, z).

> **RSI convention.** The equivalence DM(2,1,z) == RSI(z) holds for the *EMA-form*
> RSI built from this library's EMA (alpha = 2/(z+1)), NOT Wilder's classic RSI
> (which uses RMA smoothing, alpha = 1/z). Proof: with a = 2, st = Close -
> min(Close, Close[1]) = max(0, Close - Close[1]) = the up-move, and rng = |Close
> - Close[1]| = up-move + down-move. With y = 1 the inner EMA is a passthrough, so
> DM(2,1,z) = 100*EMA(up, z)/EMA(up+dn, z). Because the EMA is linear,
> EMA(up)+EMA(dn) = EMA(up+dn), hence this equals 100*EMA(up,z)/(EMA(up,z)+
> EMA(dn,z)) = the EMA-form RSI(z).

The EMA primitive is **embedded** below (inlined, not imported) so this file is a
self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming convention -- BOOK / EasyLanguage (Option B), see description.md §2:
    * st/rng are valid once a closes exist (bar a-1); all four EMA stages seed
      there. DM is NaN for bars 0..a-2, finite from bar a-1.
    * For a == 1 there is no NaN warm-up (but the a-bar close range is then always
      0, so DM is 0.0 on every bar via the guard -- a degenerate setting).

Division guard: EMA(EMA(rng)) <= 0 -> DM = 0.0 (mirrors the DS-Stochastic guard).

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
# INDICATOR: Double-Smoothed Momenta.                                     #
# ====================================================================== #
class DoubleSmoothedMomenta:
    """Stateful, streaming Double-Smoothed Momenta (DM).

    Feed one ``close`` at a time to :meth:`update`, which returns the DM value
    for that bar -- ``float('nan')`` while the a-bar look-back is unmet
    (bars 0..a-2), then a finite value in [0, 100].

    Example (a=2, y=1, z=1 -> DM is 100 when the close rose, else 0 -- the
    one-bar up/flat/down indicator; note DM(2,1,z) == EMA-form RSI(z)):
    >>> dm = DoubleSmoothedMomenta(a=2, y=1, z=1)
    >>> import math
    >>> math.isnan(dm.update(10.0))   # bar 0: a-bar window not yet full -> NaN
    True
    >>> dm.update(12.0)               # rose 10->12: up-move -> 100
    100.0
    >>> dm.update(11.0)               # fell 12->11: no up-move -> 0
    0.0
    >>> dm.update(11.0)               # flat: range 0 -> guard -> 0
    0.0
    """

    def __init__(self, a: int = 2, y: int = 2, z: int = 14) -> None:
        """Create a DM with close look-back ``a`` and EMA periods ``y`` (inner), ``z`` (outer).

        Defaults a=2, y=2, z=14 (a mildly double-smoothed RSI-14). The special
        case ``a=2, y=1`` reproduces the EMA-form RSI(z); ``DRSI(y, z)`` is
        ``DM(2, y, z)`` (see :func:`drsi_series`).
        """
        if a < 1:
            raise ValueError(f"a must be >= 1, got {a!r}")
        # y, z are validated by the EMA constructors below.
        self._a = a

        # Rolling window of the last a closes (for highest/lowest close).
        self._closes: deque[float] = deque(maxlen=a)

        # Two independent 2-stage EMA cascades (double smoothing), each wired
        # inner(y) -> outer(z): EMA(EMA(x, y), z).
        self._num_y = ExponentialMovingAverage(y)
        self._num_z = ExponentialMovingAverage(z)
        self._den_y = ExponentialMovingAverage(y)
        self._den_z = ExponentialMovingAverage(z)

    def update(self, close: float) -> float:
        """Feed one ``close`` and return this bar's DM (or NaN during warm-up)."""
        self._closes.append(close)

        # Need a closes before the highest/lowest close is defined. While
        # unprimed, the EMA cascades must NOT advance (they seed at bar a-1).
        if len(self._closes) < self._a:
            return float("nan")

        # Highest/lowest close over the last a bars.
        hc = max(self._closes)
        lc = min(self._closes)

        # Raw close-above-low (>= 0) and a-bar close range (>= 0).
        st = close - lc
        rng = hc - lc

        # Double-smooth each separately (inner y, then outer z), then divide.
        num = self._num_z.update(self._num_y.update(st))
        den = self._den_z.update(self._den_y.update(rng))

        # Division guard: smoothed range <= 0 -> DM = 0.0.
        return 0.0 if den <= 0.0 else 100.0 * num / den


def dm_series(closes, a=2, y=2, z=14):
    """Convenience: run a whole list of closes through a fresh DM."""
    dm = DoubleSmoothedMomenta(a=a, y=y, z=z)
    return [dm.update(c) for c in closes]


def drsi_series(closes, y=2, z=14):
    """Double-Smoothed RSI: DRSI(y, z) = DM(2, y, z) (fixes the look-back a=2)."""
    return dm_series(closes, a=2, y=y, z=z)


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo of the behaviours that matter most when         #
    # porting. (The full 252-bar reference-data harness lives in the      #
    # prepared-for-conversion copy of this file.)                         #
    # ------------------------------------------------------------------ #
    closes = [44.0, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84]

    def show(xs):
        return ["nan" if math.isnan(v) else round(v, 4) for v in xs]

    # 1) Double-smoothed RSI default DRSI(2, 14) = DM(2, 2, 14).
    print("DRSI(2,14)   :", show(drsi_series(closes, y=2, z=14)))

    # 2) RSI(14) special case = DM(2, 1, 14) (EMA-form RSI).
    print("DM(2,1,14)   :", show(dm_series(closes, a=2, y=1, z=14)))

    # 3) RSI equivalence invariant: DM(2,1,z) == an independently-coded EMA-form
    #    RSI(z). up = max(0, dC), dn = max(0, -dC); RSI = 100*EMA(up)/EMA(up+dn).
    def ema_rsi(values, z):
        eu = ExponentialMovingAverage(z)
        ed = ExponentialMovingAverage(z)
        out = [float("nan")]            # bar 0: no momentum yet
        for k in range(1, len(values)):
            d = values[k] - values[k - 1]
            up = d if d > 0.0 else 0.0
            dn = -d if d < 0.0 else 0.0
            nu = eu.update(up)
            de = ed.update(up + dn)
            out.append(0.0 if de <= 0.0 else 100.0 * nu / de)
        return out

    dm21 = dm_series(closes, a=2, y=1, z=14)
    rsi = ema_rsi(closes, 14)
    same = all(
        (math.isnan(p) and math.isnan(q)) or math.isclose(p, q, rel_tol=0, abs_tol=0)
        for p, q in zip(dm21, rsi)
    )
    print("DM(2,1,14) == EMA-RSI(14) bit-for-bit:", same)
