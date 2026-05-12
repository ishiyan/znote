"""
JTPO — Jurik Turning Point Oscillator (Spearman Rank Correlation)

Computes Spearman's rank correlation between price rank and time rank
over a rolling window. Output is in [-1, +1].
"""

import numpy as np


def jtpo(prices: np.ndarray, length: int = 14) -> np.ndarray:
    """
    Compute the Jurik Turning Point Oscillator.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values.
    length : int
        Rolling window length (default 14).

    Returns
    -------
    np.ndarray
        JTPO values; NaN during warmup period.
    """
    n = len(prices)
    out = np.full(n, np.nan)

    if length < 2:
        return out

    f18 = 12.0 / (length * (length - 1) * (length + 1))
    midpoint = (length + 1) / 2.0

    for bar in range(length - 1, n):
        window = prices[bar - length + 1 : bar + 1]

        # Check for constant data (init pattern: skip if all values equal)
        if np.all(window == window[0]):
            continue

        # arr2: original positions (1-based), tracks through sort
        arr2 = np.arange(1, length + 1, dtype=np.float64)

        # Sort prices ascending, tracking original positions
        sorted_indices = np.argsort(window, kind="mergesort")
        sorted_prices = window[sorted_indices]
        arr2 = arr2[sorted_indices]

        # arr3: price ranks with tied-rank averaging
        arr3 = np.empty(length, dtype=np.float64)
        i = 0
        while i < length:
            j = i
            while j < length - 1 and sorted_prices[j + 1] == sorted_prices[j]:
                j += 1
            # Ranks are 1-based: positions i..j get average rank
            avg_rank = (i + 1 + j + 1) / 2.0
            arr3[i : j + 1] = avg_rank
            i = j + 1

        # Spearman correlation sum
        correlation_sum = np.sum((arr3 - midpoint) * (arr2 - midpoint))
        out[bar] = f18 * correlation_sum

    return out


if __name__ == "__main__":
    # Quick test with a simple ramp (should give +1)
    test_prices = np.arange(1.0, 21.0)
    result = jtpo(test_prices, length=14)
    print("Ramp test (expect +1 for full windows):")
    print(result)

    # Downtrend (should give -1)
    result_down = jtpo(test_prices[::-1].copy(), length=14)
    print("\nDown-ramp test (expect -1 for full windows):")
    print(result_down)
