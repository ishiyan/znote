"""
Rescaled Fractal Adaptive Simple Moving Average (RS-FRASMA)
Mnemonic: rsfrasma

Fractal adaptive SMA using Rescaled Range (R/S) analysis to estimate the
Hurst exponent. The Hurst exponent adapts the SMA period: trending markets
get a faster MA, erratic markets get a slower MA.

Author: Jean-Philippe Poton (jppoton@yahoo.com), v1.0 October 2009
Reference: https://www.mql5.com/ru/code/9272
"""

import numpy as np
from typing import NamedTuple


class RSFRASMAResult(NamedTuple):
    """Result of RS-FRASMA computation."""
    sma: np.ndarray    # Adaptive SMA values
    hurst: np.ndarray  # Hurst exponent at each bar
    speed: np.ndarray  # Adapted SMA period at each bar


def rescaled_fractal_adamtive_simple_moving_average(
    prices: np.ndarray,
    period: int = 64,
    normal_speed: int = 30,
    pip_convertor: int = 10000,
) -> RSFRASMAResult:
    """
    Compute the Rescaled Fractal Adaptive Simple Moving Average.

    Uses Rescaled Range (R/S) analysis to estimate the Hurst exponent,
    then adapts the SMA period accordingly.

    Parameters
    ----------
    prices : np.ndarray
        1D array of prices. Index 0 = oldest.
    period : int
        Lookback window for R/S analysis. Must be a power of 2, >= 4.
    normal_speed : int
        Base SMA period before fractal adaptation (>= 1).
    pip_convertor : int
        Multiplier to convert prices to PIPs for R/S calculation.

    Returns
    -------
    RSFRASMAResult
        Named tuple with sma, hurst, and speed arrays.
    """
    if period < 4:
        raise ValueError("period must be >= 4")
    if normal_speed < 1:
        raise ValueError("normal_speed must be >= 1")

    n = len(prices)
    sma_out = np.full(n, np.nan)
    hurst_out = np.full(n, np.nan)
    speed_out = np.full(n, np.nan)

    # Precompute R/S parameters (matching MQ4 logic)
    k0 = int(period // 4)
    if k0 < 2:
        raise ValueError("period too small: period/4 must be >= 2")
    n_iter = int(np.floor(np.log(k0) / np.log(2)))

    # Block sizes and counts for each scale
    d = np.zeros(n_iter + 1, dtype=int)
    k_blocks = np.zeros(n_iter + 1, dtype=int)
    for u in range(1, n_iter + 1):
        d[u] = int(2 ** (u + 1))
        k_blocks[u] = int(period // d[u])

    pip_prices = prices * pip_convertor

    for pos in range(period, n):
        # R/S analysis on the window starting at pos
        # MQ4 uses reverse indexing; here we use forward indexing
        # Window: prices[pos - period + 1 : pos + 1] but MQ4 reads
        # pos+t+j with t advancing, so effectively prices[pos .. pos+period]
        # in MQ4's reverse order. We replicate by taking a window of
        # `period` values ending at `pos`.
        window = pip_prices[pos - period + 1 : pos + 1]  # length = period

        sumx = 0.0
        sumy = 0.0
        sumx2 = 0.0
        sumxy = 0.0

        valid_scales = 0
        for u in range(1, n_iter + 1):
            block_size = d[u]
            n_blocks_u = k_blocks[u]
            if n_blocks_u < 1:
                continue

            rs_sum = 0.0
            t = 0
            block_count = 0
            while t <= period - block_size:
                block = window[t : t + block_size]

                # Block mean
                mu = np.mean(block)

                # Block std (population std, matching MQ4: sqrt(sum_sq/d))
                std = np.sqrt(np.mean((block - mu) ** 2))
                if std <= 0.0:
                    std = 0.1

                # Cumulative deviations from mean
                cum_dev = np.cumsum(block - mu)

                # Range
                r_val = np.max(cum_dev) - np.min(cum_dev)

                # Rescaled range
                rs_sum += r_val / std
                t += block_size
                block_count += 1

            if block_count > 0:
                rs_avg = rs_sum / block_count
            else:
                rs_avg = 1.0

            # Guard against log of non-positive
            if rs_avg <= 0.0:
                rs_avg = 1e-10

            log2_d = np.log2(block_size)
            log2_rs = np.log2(rs_avg)

            sumx += log2_d
            sumy += log2_rs
            sumx2 += log2_d * log2_d
            sumxy += log2_d * log2_rs
            valid_scales += 1

        # Linear regression slope = Hurst exponent
        if valid_scales < 2:
            h = 0.5  # default to random walk
        else:
            h2 = valid_scales * sumx2 - sumx * sumx
            if h2 <= 0.0:
                h2 = 0.1
            h = (valid_scales * sumxy - sumx * sumy) / h2

        # Guard H
        if 2.0 * h <= 0.0:
            h = 0.001

        alpha = 1.0 / (2.0 * h)
        spd = max(1, int(round(normal_speed * alpha)))

        hurst_out[pos] = h
        speed_out[pos] = spd

        # Compute SMA with adapted speed
        sma_start = pos - spd + 1
        if sma_start >= 0:
            sma_out[pos] = np.mean(prices[sma_start : pos + 1])
        else:
            sma_out[pos] = np.mean(prices[0 : pos + 1])

    return RSFRASMAResult(sma=sma_out, hurst=hurst_out, speed=speed_out)


if __name__ == "__main__":
    np.random.seed(42)

    # Synthetic: trending then random
    trend = np.cumsum(np.ones(80) * 0.0010) + 1.3000
    random_walk = trend[-1] + np.cumsum(np.random.randn(80) * 0.0005)
    prices = np.concatenate([trend, random_walk])

    result = rescaled_fractal_adamtive_simple_moving_average(
        prices, period=64, normal_speed=30, pip_convertor=10000
    )

    print("Rescaled Fractal Adaptive SMA (RS-FRASMA)")
    print("=" * 55)
    print(f"Period: 64, Normal speed: 30, Data length: {len(prices)}")
    print(f"\nTrending section (bars 64-79):")
    print(f"  Mean Hurst: {np.nanmean(result.hurst[64:80]):.4f}")
    print(f"  Mean Speed: {np.nanmean(result.speed[64:80]):.1f}")
    print(f"  (Expected: H > 0.5, speed < 30)")
    print(f"\nRandom section (bars 120-159):")
    print(f"  Mean Hurst: {np.nanmean(result.hurst[120:160]):.4f}")
    print(f"  Mean Speed: {np.nanmean(result.speed[120:160]):.1f}")
    print(f"  (Expected: H ~ 0.5, speed ~ 30)")
    print(f"\nSample values (bars 70-80):")
    for i in range(70, 80):
        print(f"  Bar {i}: SMA={result.sma[i]:.5f} "
              f"H={result.hurst[i]:.4f} speed={result.speed[i]:.0f}")
