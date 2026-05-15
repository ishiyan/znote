"""
Fractal Dimension Index (FDI)
Mnemonic: fdi

Measures the fractal dimension of a price time series using normalized
path length. Values near 1.5 indicate random walk; near 1.0 indicate
trending; near 2.0 indicate erratic/volatile market.

Original author: iliko (arcsin5@netscape.net), v1.0 February 2007
Reference: https://www.mql5.com/en/code/7758
"""

import numpy as np
from typing import Optional


def fractal_dimension(
    prices: np.ndarray,
    period: int = 30,
    random_line: float = 1.5,
) -> np.ndarray:
    """
    Compute the Fractal Dimension Index for each bar.

    Parameters
    ----------
    prices : np.ndarray
        1D array of prices (e.g., close prices). Index 0 = oldest.
    period : int
        Lookback period N (>= 2).
    random_line : float
        Threshold for trending vs erratic (typically 1.5).

    Returns
    -------
    np.ndarray
        FDI values. First (period) values are NaN (insufficient data).
    """
    if period < 2:
        raise ValueError("period must be >= 2")

    n = len(prices)
    fdi = np.full(n, np.nan)

    log_2n = np.log(2.0 * period)
    ln2 = np.log(2.0)

    for pos in range(period, n):
        # Extract window [pos-period, pos] inclusive = period+1 points, period segments
        window = prices[pos - period : pos + 1]  # period+1 elements
        price_max = np.max(window)
        price_min = np.min(window)
        price_range = price_max - price_min

        if price_range < 1e-10:
            # Flat price: dimension is 1 (straight line)
            fdi[pos] = 1.0
            continue

        # Normalize to [0, 1]
        norm = (window - price_min) / price_range

        # Compute path length
        length = 0.0
        inv_n_sq = 1.0 / (period * period)
        for i in range(1, period + 1):
            diff = norm[i] - norm[i - 1]
            length += np.sqrt(diff * diff + inv_n_sq)

        # Fractal dimension
        fdi[pos] = 1.0 + (np.log(length) + ln2) / log_2n

    return fdi


def classify_regime(
    fdi_values: np.ndarray, random_line: float = 1.5
) -> np.ndarray:
    """
    Classify market regime from FDI values.

    Returns
    -------
    np.ndarray of str
        'trending', 'random', or 'erratic' for each bar.
    """
    result = np.full(len(fdi_values), "", dtype=object)
    for i, v in enumerate(fdi_values):
        if np.isnan(v):
            result[i] = "unknown"
        elif v < random_line - 0.05:
            result[i] = "trending"
        elif v > random_line + 0.05:
            result[i] = "erratic"
        else:
            result[i] = "random"
    return result


if __name__ == "__main__":
    # Example usage with synthetic data
    np.random.seed(42)

    # Generate trending data followed by random walk
    trend = np.cumsum(np.ones(50) * 0.01) + 1.3000
    random_walk = 1.3000 + np.cumsum(np.random.randn(50) * 0.001)
    prices = np.concatenate([trend, random_walk])

    fdi_values = fractal_dimension(prices, period=20)

    print("Fractal Dimension Index (FDI)")
    print("=" * 50)
    print(f"Period: 20, Data length: {len(prices)}")
    print(f"\nTrending section (bars 20-49):")
    print(f"  Mean FDI: {np.nanmean(fdi_values[20:50]):.4f}")
    print(f"  (Expected: < 1.5, indicating trend)")
    print(f"\nRandom section (bars 70-99):")
    print(f"  Mean FDI: {np.nanmean(fdi_values[70:100]):.4f}")
    print(f"  (Expected: ~1.5, indicating random walk)")

    regimes = classify_regime(fdi_values)
    print(f"\nRegime classification sample (bars 40-60):")
    for i in range(40, 60):
        print(f"  Bar {i}: FDI={fdi_values[i]:.4f} -> {regimes[i]}")
