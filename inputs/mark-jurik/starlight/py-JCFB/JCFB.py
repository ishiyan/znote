"""JCFB — Composite Fractal Behavior indicator.

Estimates the dominant cycle period by analyzing trend efficiency at multiple scales.
"""

import numpy as np


SCALE_SETS = {
    1: [2, 3, 4, 6, 8, 12, 16, 24],
    2: [2, 3, 4, 6, 8, 12, 16, 24, 32, 48],
    3: [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96],
    4: [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192],
}


def jcfb_aux(prices: np.ndarray, depth: int) -> np.ndarray:
    """Compute single-scale efficiency ratio for a given depth.

    Parameters
    ----------
    prices : 1-D array of price values.
    depth : lookback window (scale).

    Returns
    -------
    1-D array (same length as prices) of efficiency ratios [0..1].
    """
    n = len(prices)
    output = np.zeros(n)

    for bar in range(depth, n):
        weighted_path = 0.0
        price_sum = 0.0
        for i in range(depth):
            diff = abs(prices[bar - i] - prices[bar - i - 1])
            weighted_path += (depth - i) * diff
            price_sum += prices[bar - i - 1]

        displacement = abs(depth * prices[bar] - price_sum)
        output[bar] = displacement / weighted_path if weighted_path != 0.0 else 0.0

    return output


def _sma(series: np.ndarray, window: int) -> np.ndarray:
    """Simple moving average with same-length output (zero-padded start)."""
    out = np.zeros_like(series)
    cumsum = np.cumsum(series)
    out[window - 1:] = (cumsum[window - 1:] - np.concatenate(([0.0], cumsum[:-window]))) / window
    return out


def jcfb(prices: np.ndarray, fractal_type: int = 1, smooth: int = 10) -> np.ndarray:
    """Compute JCFB composite dominant cycle period.

    Parameters
    ----------
    prices : 1-D array of price values.
    fractal_type : 1-4, selects max depth (24/48/96/192).
    smooth : SMA window applied to each scale's efficiency ratio.

    Returns
    -------
    1-D array of estimated dominant period for each bar.
    """
    prices = np.asarray(prices, dtype=float)
    n = len(prices)
    scales = SCALE_SETS[fractal_type]
    num_scales = len(scales)

    # Compute and smooth efficiency ratios for all scales
    er_smooth = np.zeros((num_scales, n))
    for idx, depth in enumerate(scales):
        er = jcfb_aux(prices, depth)
        er_smooth[idx] = _sma(er, smooth)

    # Cascading residual-probability weighting
    weights = np.zeros((num_scales, n))

    # Even-indexed scales (0,2,4,...) — process largest first
    even_indices = list(range(0, num_scales, 2))[::-1]
    residual = np.ones(n)
    for idx in even_indices:
        weights[idx] = residual * er_smooth[idx]
        residual *= (1.0 - weights[idx])

    # Odd-indexed scales (1,3,5,...) — process largest first
    odd_indices = list(range(1, num_scales, 2))[::-1]
    residual = np.ones(n)
    for idx in odd_indices:
        weights[idx] = residual * er_smooth[idx]
        residual *= (1.0 - weights[idx])

    # Weighted-mean dominant period
    w_sq = weights ** 2
    scale_arr = np.array(scales, dtype=float).reshape(-1, 1)
    numerator = np.sum(w_sq * scale_arr, axis=0)
    denominator = np.sum(w_sq, axis=0)

    output = np.where(denominator != 0.0, numerator / denominator, 0.0)
    return output
