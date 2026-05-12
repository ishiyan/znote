"""
JARSX — Adaptive RSX
Wraps JXRSX with automatic length selection based on volatility regime detection.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from py_JXRSX.JXRSX import jxrsx


def jarsx(
    prices: np.ndarray,
    lo_len: int = 5,
    hi_len: int = 30,
    sensitivity: float = 1.0,
) -> np.ndarray:
    """
    Adaptive RSX — wraps JXRSX with automatic length selection.

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    lo_len : int
        Minimum adaptive length (fastest response).
    hi_len : int
        Maximum adaptive length (most smoothing).
    sensitivity : float
        Controls how aggressively length adapts to volatility changes.

    Returns
    -------
    np.ndarray
        JARSX output array.
    """
    eps = 0.001
    n = len(prices)

    # Step 1: absolute price changes
    value1 = np.zeros(n)
    value1[1:] = np.abs(np.diff(prices))

    # Step 2: compute adaptive length for each bar
    adaptive_length = np.zeros(n)

    for i in range(n):
        # Long-term volatility: SMA over min(i, 99)+1 bars
        window_long = min(i, 99) + 1
        avg1 = np.mean(value1[i - window_long + 1 : i + 1])

        # Short-term volatility: SMA over min(i, 9)+1 bars
        window_short = min(i, 9) + 1
        avg2 = np.mean(value1[i - window_short + 1 : i + 1])

        # Log ratio of volatilities
        value2 = sensitivity * np.log((eps + avg1) / (eps + avg2))

        # Soft squash to (-1, +1)
        value3 = value2 / (1.0 + abs(value2))

        # Map to [lo_len, hi_len]
        adaptive_length[i] = lo_len + (hi_len - lo_len) * (1.0 + value3) / 2.0

    # Step 3: pass adaptive length series to JXRSX
    return jxrsx(prices, adaptive_length)


if __name__ == "__main__":
    # Quick test
    np.random.seed(42)
    test_prices = np.cumsum(np.random.randn(100)) + 100
    result = jarsx(test_prices, lo_len=5, hi_len=30, sensitivity=1.0)
    print(f"JARSX output (last 10): {result[-10:]}")
