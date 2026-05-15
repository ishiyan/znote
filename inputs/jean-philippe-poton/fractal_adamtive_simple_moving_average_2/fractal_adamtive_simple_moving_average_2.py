"""
Fractal Adaptive Simple Moving Average v2 (FRASMAv2)
Mnemonic: frasma2

Same concept as FRASMA but uses the corrected FGDI formula (ln(2*(N-1))
denominator) and adds a shift parameter to offset the output.

Author: Jean-Philippe Poton (jppoton@yahoo.com), Copyright 2008
Source: https://www.mql5.com/en/code/8866
"""

import numpy as np


def _compute_fdi_corrected(
    prices: np.ndarray,
    period: int,
) -> np.ndarray:
    """
    Compute FDI using the corrected FGDI formula: ln(2*(period-1)) denominator.

    The loop iterates over N points (0..N-1 inclusive), yielding N-1 path
    segments -- one more segment than FRASMA v1.

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
    log_2pm1 = np.log(2.0 * (period - 1))
    inv_n_sq = 1.0 / (period * period)

    for pos in range(period, n):
        window = prices[pos - period + 1 : pos + 1]  # period elements
        price_max = np.max(window)
        price_min = np.min(window)
        price_range = price_max - price_min

        if price_range <= 0.0:
            fdi[pos] = 0.0
            continue

        length = 0.0
        prior_diff = (window[0] - price_min) / price_range
        # N-1 segments (iteration 1..period-1 inclusive)
        for i in range(1, period):
            diff = (window[i] - price_min) / price_range
            delta = diff - prior_diff
            length += np.sqrt(delta * delta + inv_n_sq)
            prior_diff = diff

        if length > 0.0:
            fdi[pos] = 1.0 + (np.log(length) + ln2) / log_2pm1
        else:
            fdi[pos] = 0.0

    return fdi


def fractal_adamtive_simple_moving_average_2(
    prices: np.ndarray,
    period: int = 30,
    normal_speed: int = 20,
    shift: int = 0,
) -> np.ndarray:
    """
    Compute the Fractal Adaptive Simple Moving Average v2 (FRASMAv2).

    Parameters
    ----------
    prices : np.ndarray
        1-D array of prices (e.g., close). Index 0 = oldest bar.
    period : int
        Lookback period for FDI computation (>= 2).
    normal_speed : int
        Base SMA period before fractal adaptation (>= 1).
    shift : int
        Output displacement. Positive shifts the output to the right (future).

    Returns
    -------
    np.ndarray
        FRASMAv2 values. Early bars and out-of-range shifted bars are NaN.
    """
    if period < 2:
        raise ValueError("period must be >= 2")
    if normal_speed < 1:
        raise ValueError("normal_speed must be >= 1")

    n = len(prices)
    output = np.full(n, np.nan)

    fdi = _compute_fdi_corrected(prices, period)

    for pos in range(period, n):
        d = fdi[pos]
        if np.isnan(d) or d == 0.0:
            continue

        denom = 2.0 - d
        if abs(denom) < 1e-10:
            continue
        trail_dim = 1.0 / denom
        alpha = trail_dim / 2.0
        speed = max(1, int(round(normal_speed * alpha)))

        # SMA of length `speed` ending at `pos`
        if pos - speed + 1 < 0:
            continue

        sma_val = np.mean(prices[pos - speed + 1 : pos + 1])

        # Apply shift (positive = future = higher index)
        out_idx = pos + shift
        if 0 <= out_idx < n:
            output[out_idx] = sma_val

    return output


if __name__ == "__main__":
    np.random.seed(42)

    # Synthetic data: trending then random
    trend = np.cumsum(np.ones(60) * 0.01) + 1.3000
    random_walk = 1.3000 + np.cumsum(np.random.randn(60) * 0.001)
    prices = np.concatenate([trend, random_walk])

    frasma2 = fractal_adamtive_simple_moving_average_2(
        prices, period=20, normal_speed=15, shift=0
    )
    fdi = _compute_fdi_corrected(prices, period=20)

    print("Fractal Adaptive Simple Moving Average v2 (FRASMAv2)")
    print("=" * 55)
    print(f"Period: 20, Normal speed: 15, Shift: 0, Data length: {len(prices)}")
    print()

    print("Sample values (trending section, bars 30-39):")
    for i in range(30, 40):
        d = fdi[i]
        h = 2.0 - d if not np.isnan(d) else float("nan")
        print(f"  Bar {i}: price={prices[i]:.4f}  FDI={d:.4f}  H={h:.4f}  FRASMAv2={frasma2[i]:.4f}")

    print()
    print("Sample values (random section, bars 80-89):")
    for i in range(80, 90):
        d = fdi[i]
        h = 2.0 - d if not np.isnan(d) else float("nan")
        val = frasma2[i]
        print(f"  Bar {i}: price={prices[i]:.4f}  FDI={d:.4f}  H={h:.4f}  FRASMAv2={val:.4f}")

    # Demonstrate shift
    frasma2_shifted = fractal_adamtive_simple_moving_average_2(
        prices, period=20, normal_speed=15, shift=3
    )
    print()
    print("With shift=3 (bars 50-55):")
    for i in range(50, 56):
        v0 = frasma2[i] if not np.isnan(frasma2[i]) else None
        vs = frasma2_shifted[i] if not np.isnan(frasma2_shifted[i]) else None
        print(f"  Bar {i}: shift=0 -> {v0}  shift=3 -> {vs}")
