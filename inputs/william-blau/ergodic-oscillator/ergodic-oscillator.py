"""Ergodic Oscillator -- William Blau.

The Ergodic oscillator is the True Strength Index together with a signal line:

    ergodic_k = TSI(q, r, s, u)_k                    (the TSI oscillator)
    signal_k  = EMA(ergodic, ul)_k                   (ul-period EMA of it)

It is a TWO-output indicator: each update() returns a named tuple
(ergodic, signal).

Both the TSI and the EMA primitive are **embedded** (inlined) below so this file
is a self-contained porting unit. Do NOT change their numerics -- see
../true-strength-index/description.md and
../core/exponential-moving-average/description.md.

Priming -- BOOK / EasyLanguage (Option B), see description.md §2:
    * Oscillator = TSI: NaN for bars 0..q-2, finite from bar q-1.
    * Signal EMA seeds on the first valid oscillator value (bar q-1), so the
      signal is ALSO NaN for bars 0..q-2 and finite from bar q-1.
    * ul == 1 -> signal is a passthrough -> signal == ergodic for every bar.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math
from collections import deque, namedtuple


# ====================================================================== #
# EMBEDDED BUILDING BLOCK: Blau exponential moving average.               #
# Copied verbatim from core/exponential-moving-average. Inlined so each   #
# indicator is a standalone porting unit. Do NOT change its numerics.     #
# ====================================================================== #
class ExponentialMovingAverage:
    """Stateful streaming EMA: alpha = 2/(period+1), seeds e_0 = x_0.

    period == 1 -> alpha == 1 -> pure passthrough (output == input).
    period  < 1 -> invalid.
    """

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period!r}")
        self._alpha: float = 2.0 / (float(period) + 1.0)
        self._prev: float = 0.0
        self._primed: bool = False

    def update(self, x: float) -> float:
        if not self._primed:
            self._prev = x
            self._primed = True
            return self._prev
        e = self._alpha * x + (1.0 - self._alpha) * self._prev
        self._prev = e
        return e


# ====================================================================== #
# EMBEDDED INDICATOR: True Strength Index (the Ergodic oscillator output). #
# Copied verbatim from true-strength-index. Do NOT change its numerics.    #
# ====================================================================== #
class TrueStrengthIndex:
    """Streaming TSI: 100 * TEMA(mtm, r,s,u) / TEMA(|mtm|, r,s,u).

    NaN for bars 0..q-2 (momentum look-back), finite from bar q-1.
    Denominator 0 -> output 0.0.
    """

    def __init__(self, q: int = 2, r: int = 20, s: int = 5, u: int = 3) -> None:
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        self._q = q
        self._history: deque[float] = deque(maxlen=q)
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

    def update(self, price: float) -> float:
        self._history.append(price)
        if len(self._history) < self._q:
            return float("nan")
        mtm = price - self._history[0]
        abs_mtm = abs(mtm)
        n = self._num_u.update(self._num_s.update(self._num_r.update(mtm)))
        d = self._den_u.update(self._den_s.update(self._den_r.update(abs_mtm)))
        if d == 0.0:
            return 0.0
        return 100.0 * n / d


# ====================================================================== #
# INDICATOR: Ergodic Oscillator.                                         #
# ====================================================================== #

# Two-output result. ``ergodic`` is the TSI oscillator; ``signal`` is its
# ul-period EMA. Both share the same NaN warm-up region.
ErgodicResult = namedtuple("ErgodicResult", ["ergodic", "signal"])


class ErgodicOscillator:
    """Stateful, streaming Ergodic oscillator (TSI + signal line).

    Feed one close at a time to :meth:`update`; it returns an
    :class:`ErgodicResult` ``(ergodic, signal)``. Both fields are NaN while the
    momentum look-back is unmet (bars 0..q-2), then finite.

    Example (q=2, all stages passthrough, signal passthrough -> +/-100 both):
    >>> erg = ErgodicOscillator(q=2, r=1, s=1, u=1, ul=1)
    >>> import math
    >>> r0 = erg.update(10.0); (math.isnan(r0.ergodic), math.isnan(r0.signal))
    (True, True)
    >>> r1 = erg.update(12.0); (r1.ergodic, r1.signal)   # mtm=+2 -> +100, ul=1
    (100.0, 100.0)
    """

    def __init__(self, q: int = 2, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create an Ergodic with TSI params ``q,r,s,u`` and signal period ``ul``."""
        # The oscillator is the TSI; the signal line is an EMA of it.
        self._tsi = TrueStrengthIndex(q=q, r=r, s=s, u=u)
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, price: float) -> ErgodicResult:
        """Feed one close ``price``; return (ergodic, signal) for this bar."""
        ergodic = self._tsi.update(price)

        # While the oscillator is not primed, the signal is undefined too, and
        # we must NOT advance the signal EMA (it should seed on the first valid
        # oscillator value, bar q-1).
        if math.isnan(ergodic):
            return ErgodicResult(float("nan"), float("nan"))

        signal = self._signal_ema.update(ergodic)
        return ErgodicResult(ergodic, signal)


def ergodic_series(values, q=2, r=20, s=5, u=3, ul=3):
    """Convenience: run closes through a fresh Ergodic.

    Returns two parallel lists: (ergodic_values, signal_values).
    """
    erg = ErgodicOscillator(q=q, r=r, s=s, u=u, ul=ul)
    out = [erg.update(v) for v in values]
    return [o.ergodic for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Human-readable demo. (The full 252-bar reference-data harness lives  #
    # in the prepared-for-conversion copy of this file.)                   #
    # ------------------------------------------------------------------ #
    closes = [10.0, 12.0, 11.0, 13.0, 12.0, 12.0, 15.0]

    def show(xs):
        return ["nan" if math.isnan(v) else round(v, 4) for v in xs]

    # 1) Default Ergodic.
    e, sig = ergodic_series(closes, q=2, r=20, s=5, u=3, ul=3)
    print("ergodic q2,r20,s5,u3,ul3:", show(e))
    print("signal  q2,r20,s5,u3,ul3:", show(sig))

    # 2) ul=1 invariant: signal must equal ergodic exactly (passthrough).
    e1, s1 = ergodic_series(closes, q=2, r=20, s=5, u=3, ul=1)
    same = all((math.isnan(a) and math.isnan(b)) or a == b for a, b in zip(e1, s1))
    print("ul=1 -> signal == ergodic exactly:", same)
