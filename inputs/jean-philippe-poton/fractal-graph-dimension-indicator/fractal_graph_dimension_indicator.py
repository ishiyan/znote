"""
Fractal Graph Dimension Indicator (FGDI)
Mnemonic: fgdi

Corrected and enhanced fractal dimension with standard deviation bands.
Based on Poton's corrections to iliko's original FDI.

Author: Jean-Philippe Poton (jppoton@yahoo.com)
Reference: https://www.mql5.com/en/code/8844
"""

import numpy as np
from typing import NamedTuple


class FGDIResult(NamedTuple):
    """Result of FGDI computation."""
    fdi: np.ndarray        # Fractal dimension values
    upper_band: np.ndarray # FDI + stddev
    lower_band: np.ndarray # FDI - stddev
    stddev: np.ndarray     # Standard deviation of estimate


def fractal_graph_dimension_indicator(
    prices: np.ndarray,
    period: int = 30,
    random_line: float = 1.5,
) -> FGDIResult:
    """
    Compute the Fractal Graph Dimension Indicator with confidence bands.

    Key differences from the basic FDI (fractal_dimension.py):
    1. Loop includes the last segment (i <= period-1 vs i < period-1)
    2. Denominator uses ln(2*(period-1)) instead of ln(2*period)
    3. Adds standard deviation bands around the estimate

    Parameters
    ----------
    prices : np.ndarray
        1D array of prices. Index 0 = oldest.
    period : int
        Lookback period (>= 2).
    random_line : float
        Threshold (1.5 = random walk).

    Returns
    -------
    FGDIResult
        Named tuple with fdi, upper_band, lower_band, stddev arrays.
    """
    if period < 2:
        raise ValueError("period must be >= 2")

    n = len(prices)
    fdi = np.full(n, np.nan)
    upper_band = np.full(n, np.nan)
    lower_band = np.full(n, np.nan)
    stddev_arr = np.full(n, np.nan)

    period_minus_1 = period - 1
    log_denom = np.log(2.0 * period_minus_1)  # Key correction: 2*(N-1) not 2*N
    ln2 = np.log(2.0)
    inv_n_sq = 1.0 / (period * period)

    for pos in range(period, n):
        # Extract window: period+1 prices => period segments
        window = prices[pos - period : pos + 1]
        price_max = np.max(window)
        price_min = np.min(window)
        price_range = price_max - price_min

        if price_range < 1e-10:
            fdi[pos] = 1.0
            upper_band[pos] = 1.0
            lower_band[pos] = 1.0
            stddev_arr[pos] = 0.0
            continue

        # Normalize to [0, 1]
        norm = (window - price_min) / price_range

        # Compute individual path segments
        # Key correction: loop through ALL period_minus_1 segments (inclusive)
        segments = np.empty(period_minus_1)
        for i in range(period_minus_1):
            diff = norm[i + 1] - norm[i]
            segments[i] = np.sqrt(diff * diff + inv_n_sq)

        # Path length (sum of segments)
        length = np.sum(segments)

        # Fractal dimension
        if length > 0:
            fdi_val = 1.0 + (np.log(length) + ln2) / log_denom
        else:
            fdi_val = 1.0

        # Standard deviation of the estimate
        mean_delta = length / period_minus_1
        variance_sum = np.sum((segments - mean_delta) ** 2)
        variance = variance_sum / (length * length * log_denom * log_denom)
        sd = np.sqrt(variance)

        fdi[pos] = fdi_val
        upper_band[pos] = fdi_val + sd
        lower_band[pos] = fdi_val - sd
        stddev_arr[pos] = sd

    return FGDIResult(fdi=fdi, upper_band=upper_band,
                      lower_band=lower_band, stddev=stddev_arr)


if __name__ == "__main__":
    np.random.seed(42)

    # Synthetic: trending then random
    trend = np.cumsum(np.ones(60) * 0.0010) + 1.3000
    random_walk = trend[-1] + np.cumsum(np.random.randn(60) * 0.0005)
    prices = np.concatenate([trend, random_walk])

    result = fractal_graph_dimension_indicator(prices, period=20)

    print("Fractal Graph Dimension Indicator (FGDI)")
    print("=" * 50)
    print(f"Period: 20, Data length: {len(prices)}")
    print(f"\nTrending section (bars 20-55):")
    print(f"  Mean FDI:    {np.nanmean(result.fdi[20:56]):.4f}")
    print(f"  Mean StdDev: {np.nanmean(result.stddev[20:56]):.6f}")
    print(f"  (Expected: FDI < 1.5)")
    print(f"\nRandom section (bars 80-119):")
    print(f"  Mean FDI:    {np.nanmean(result.fdi[80:120]):.4f}")
    print(f"  Mean StdDev: {np.nanmean(result.stddev[80:120]):.6f}")
    print(f"  (Expected: FDI ~ 1.5)")
    print(f"\nSample values (bars 50-60):")
    for i in range(50, 60):
        print(f"  Bar {i}: FDI={result.fdi[i]:.4f} "
              f"[{result.lower_band[i]:.4f}, {result.upper_band[i]:.4f}]")
