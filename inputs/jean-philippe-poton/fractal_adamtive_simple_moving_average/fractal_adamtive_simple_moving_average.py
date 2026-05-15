"""
Fractal Adaptive Simple Moving Average (FRASMA)
Mnemonic: frasma

Uses the Fractal Dimension Index (FDI) to adaptively modify an SMA's period.
When the market is trending (H > 0.5), the SMA speeds up; when erratic
(H < 0.5), the SMA slows down; at random walk (H = 0.5), the SMA period
is unchanged.

Author: Jean-Philippe Poton (jppoton@yahoo.com), Copyright 2008
Source: https://www.mql5.com/en/code/8718
Blog:   http://fractalfinance.blogspot.com/2009/02/speed-of-frama-part-2-frasma.html
"""

import numpy as np


def _compute_fdi_original(
    prices: np.ndarray,
    period: int,
) -> np.ndarray:
    """
    Compute FDI using iliko's original formula: ln(2*period) denominator.

    This is the version used in FRASMA v1 (NOT the corrected FGDI formula).

    Parameters
    ----------
    prices : np.ndarray
        1-D price array. Index 0 = oldest bar.
    period : int
        Lookback period N.

    Returns
    -------
    np.ndarray
        FDI value per bar; first ``period`` values are NaN.
    """
    n = len(prices)
    fdi = np.full(n, np.nan)
    ln2 = np.log(2.0)
    log_2n = np.log(2.0 * period)
    inv_n_sq = 1.0 / (period * period)
    period_m1 = period - 1

    for pos in range(period, n):
        # Window: period bars starting at (pos - period + 1) .. pos
        # In MQ4 the window is pos .. pos+period (descending time).
        # Here index 0 = oldest, so the window is [pos - period_m1, pos+1).
        window = prices[pos - period_m1 : pos + 1]  # period elements
        price_max = np.max(window)
        price_min = np.min(window)
        price_range = price_max - price_min

        if price_range <= 0.0:
            fdi[pos] = 0.0
            continue

        length = 0.0
        prior_diff = (window[0] - price_min) / price_range
        for i in range(1, period_m1):
            diff = (window[i] - price_min) / price_range
            delta = diff - prior_diff
            length += np.sqrt(delta * delta + inv_n_sq)
            prior_diff = diff

        if length > 0.0:
            fdi[pos] = 1.0 + (np.log(length) + ln2) / log_2n
        else:
            fdi[pos] = 0.0

    return fdi


def fractal_adamtive_simple_moving_average(
    prices: np.ndarray,
    period: int = 30,
    normal_speed: int = 20,
) -> np.ndarray:
    """
    Compute the Fractal Adaptive Simple Moving Average (FRASMA).

    Parameters
    ----------
    prices : np.ndarray
        1-D array of prices (e.g., close). Index 0 = oldest bar.
    period : int
        Lookback period for FDI computation (>= 2).
    normal_speed : int
        Base SMA period before fractal adaptation (>= 1).

    Returns
    -------
    np.ndarray
        FRASMA values. Early bars without sufficient data are NaN.
    """
    if period < 2:
        raise ValueError("period must be >= 2")
    if normal_speed < 1:
        raise ValueError("normal_speed must be >= 1")

    n = len(prices)
    output = np.full(n, np.nan)

    fdi = _compute_fdi_original(prices, period)

    for pos in range(period, n):
        d = fdi[pos]
        if np.isnan(d) or d == 0.0:
            continue

        # Hurst = 2 - fdi
        # trail_dim = 1 / Hurst = 1 / (2 - fdi)
        denom = 2.0 - d
        if abs(denom) < 1e-10:
            continue
        trail_dim = 1.0 / denom
        alpha = trail_dim / 2.0
        speed = max(1, int(round(normal_speed * alpha)))

        # SMA of length `speed` ending at `pos`
        if pos - speed + 1 < 0:
            continue
        output[pos] = np.mean(prices[pos - speed + 1 : pos + 1])

    return output


if __name__ == "__main__":
    np.random.seed(42)

    # Synthetic data: trending then random
    trend = np.cumsum(np.ones(60) * 0.01) + 1.3000
    random_walk = 1.3000 + np.cumsum(np.random.randn(60) * 0.001)
    prices = np.concatenate([trend, random_walk])

    frasma = fractal_adamtive_simple_moving_average(prices, period=20, normal_speed=15)
    fdi = _compute_fdi_original(prices, period=20)

    print("Fractal Adaptive Simple Moving Average (FRASMA)")
    print("=" * 55)
    print(f"Period: 20, Normal speed: 15, Data length: {len(prices)}")
    print()

    print("Sample values (trending section, bars 30-39):")
    for i in range(30, 40):
        d = fdi[i]
        h = 2.0 - d if not np.isnan(d) else float("nan")
        print(f"  Bar {i}: price={prices[i]:.4f}  FDI={d:.4f}  H={h:.4f}  FRASMA={frasma[i]:.4f}")

    print()
    print("Sample values (random section, bars 80-89):")
    for i in range(80, 90):
        d = fdi[i]
        h = 2.0 - d if not np.isnan(d) else float("nan")
        val = frasma[i]
        print(f"  Bar {i}: price={prices[i]:.4f}  FDI={d:.4f}  H={h:.4f}  FRASMA={val:.4f}")
