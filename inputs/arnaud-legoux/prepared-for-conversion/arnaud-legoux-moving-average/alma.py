"""ALMA — Arnaud Legoux Moving Average.

Reference implementation faithful to the original NinjaTrader code released by
Arnaud Legoux, Dimitrios Kouzis-Loukas, and Anthony Cascino (2009).

Weight convention: weight[i] applies to the bar at position (oldest + i) within
the window, so weight[0] → oldest bar, weight[N-1] → newest bar.  With the
default offset of 0.85, the Gaussian peak falls near the newest bars.
"""

from __future__ import annotations

import math
from typing import Sequence


def alma_weights(window: int, sigma: float, offset: float) -> list[float]:
    """Compute the Gaussian weights for the ALMA filter.

    Args:
        window: Number of bars in the lookback window (N).
        sigma:  Controls Gaussian width; larger → smoother.
        offset: Shifts the Gaussian peak; 0 → centered, 1 → newest bar.

    Returns:
        List of *window* weights, index 0 = oldest bar in the window.
    """
    m = offset * (window - 1)
    s = window / sigma
    return [math.exp(-((i - m) ** 2) / (2.0 * s * s)) for i in range(window)]


def alma(
    close: Sequence[float],
    window: int = 9,
    sigma: float = 6.0,
    offset: float = 0.85,
) -> list[float | None]:
    """Compute the Arnaud Legoux Moving Average.

    Args:
        close:  Sequence of closing prices.
        window: Lookback period (default 9).
        sigma:  Gaussian width parameter (default 6.0).
        offset: Gaussian peak position 0–1 (default 0.85).

    Returns:
        List the same length as *close*.  The first (window − 1) entries are
        ``None`` (insufficient data); subsequent entries are ALMA values.
    """
    weights = alma_weights(window, sigma, offset)
    norm = sum(weights)
    n = len(close)
    result: list[float | None] = [None] * (window - 1)
    for t in range(window - 1, n):
        val = sum(weights[i] * close[t - window + 1 + i] for i in range(window))
        result.append(val / norm)
    return result
