"""JAVEL — Adaptive VEL (wraps JXVEL with automatic depth selection)."""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from py_JXVEL.JXVEL import jxvel  # noqa: E402


EPS = 0.001


def javel(
    prices: np.ndarray,
    lo_len: int = 5,
    hi_len: int = 30,
    sensitivity: float = 1.0,
    period: float = 3.0,
) -> np.ndarray:
    """Adaptive VEL — same volatility-regime adaptation as JARSX applied to VEL's depth.

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    lo_len : int
        Minimum adaptive depth.
    hi_len : int
        Maximum adaptive depth.
    sensitivity : float
        Regime detection sensitivity.
    period : float
        JXVEL smoothing period.

    Returns
    -------
    np.ndarray
        JAVEL output series.
    """
    n = len(prices)
    value1 = np.zeros(n)
    adaptive_depth = np.zeros(n)

    for bar in range(1, n):
        value1[bar] = abs(prices[bar] - prices[bar - 1])

    for bar in range(n):
        len1 = min(bar, 99) + 1
        len2 = min(bar, 9) + 1

        avg1 = np.mean(value1[bar - len1 + 1 : bar + 1])
        avg2 = np.mean(value1[bar - len2 + 1 : bar + 1])

        value2 = sensitivity * np.log((EPS + avg1) / (EPS + avg2))
        value3 = value2 / (1.0 + abs(value2))
        adaptive_depth[bar] = lo_len + (hi_len - lo_len) * (1.0 + value3) / 2.0

    return jxvel(prices, depth=adaptive_depth, period=period)
