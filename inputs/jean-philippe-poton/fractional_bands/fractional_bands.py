"""
Fractional Bands
Mnemonic: fctban

Similar to Fractal Bands but operates in PIP space and uses
deviation^(2*hurst) following the FBM variance scaling law.

Original author: Jean-Philippe Poton, Copyright 2009
Source: https://www.mql5.com/en/code/8900
Blog: http://fractalfinance.blogspot.com/2009/05/fractional-bands.html
"""

import numpy as np


def _fdi(prices: np.ndarray, period: int) -> np.ndarray:
    """
    Compute the Fractal Dimension Index using the corrected formula
    with ln(2*(period-1)) in the denominator.
    """
    n = len(prices)
    fdi = np.full(n, np.nan)
    ln2 = np.log(2.0)
    log_denom = np.log(2.0 * (period - 1))

    for pos in range(period, n):
        window = prices[pos - period : pos + 1]
        price_max = np.max(window)
        price_min = np.min(window)
        price_range = price_max - price_min

        if price_range < 1e-10:
            fdi[pos] = 1.0
            continue

        norm = (window - price_min) / price_range
        length = 0.0
        inv_n_sq = 1.0 / (period * period)
        for i in range(1, period + 1):
            diff = norm[i] - norm[i - 1]
            length += np.sqrt(diff * diff + inv_n_sq)

        fdi[pos] = 1.0 + (np.log(length) + ln2) / log_denom

    return fdi


def fractional_bands(
    prices: np.ndarray,
    period: int = 30,
    normal_speed: int = 30,
    pip_convertor: int = 10000,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute Fractional Bands: FRASMA center with FBM-scaled bands in PIP space.

    Parameters
    ----------
    prices : np.ndarray
        1D array of prices (index 0 = oldest).
    period : int
        Lookback period for FDI computation.
    normal_speed : int
        Base SMA period before fractal adaptation.
    pip_convertor : int
        Multiplier to convert price to PIP space (e.g., 10000 for 4-digit FX).

    Returns
    -------
    frasma : np.ndarray
        Center line (Fractal Adaptive SMA).
    upper : np.ndarray
        Upper band.
    lower : np.ndarray
        Lower band.
    """
    n = len(prices)
    fdi_vals = _fdi(prices, period)
    p = float(pip_convertor)

    frasma = np.full(n, np.nan)
    upper = np.full(n, np.nan)
    lower = np.full(n, np.nan)

    for pos in range(period, n):
        fdi_val = fdi_vals[pos]
        if np.isnan(fdi_val):
            continue

        # Hurst exponent and adaptive speed
        hurst = max(2.0 - fdi_val, 0.01)
        trail_dim = 1.0 / hurst
        beta = trail_dim / 2.0
        speed = max(int(round(normal_speed * beta)), 1)

        # FRASMA
        if pos + 1 < speed:
            continue
        window = prices[pos + 1 - speed : pos + 1]
        frasma_val = np.mean(window)
        frasma[pos] = frasma_val

        # Convert to PIP space
        frasma_pips = p * frasma_val

        # Deviation in PIP space
        dev_window = prices[pos + 1 - period : pos + 1] if pos + 1 >= period else prices[: pos + 1]
        sq_sum = np.sum((p * dev_window - frasma_pips) ** 2)
        deviation = np.sqrt(sq_sum / period)

        # Fractional bands: sigma^(2H)
        two_h = 2.0 * hurst
        band_offset = 2.0 * (deviation ** two_h)
        upper[pos] = (frasma_pips + band_offset) / p
        lower[pos] = (frasma_pips - band_offset) / p

    return frasma, upper, lower


if __name__ == "__main__":
    np.random.seed(42)

    # Synthetic FX-like data around 1.3000
    trend = 1.3000 + np.cumsum(np.ones(60) * 0.0005)
    revert = trend[-1] + np.cumsum(np.random.randn(60) * 0.0003)
    prices = np.concatenate([trend, revert])

    frasma, upper, lower = fractional_bands(prices, period=20, normal_speed=20, pip_convertor=10000)

    print("Fractional Bands (fctban)")
    print("=" * 55)
    print(f"Period: 20, Normal speed: 20, PIP Convertor: 10000")
    print(f"Data length: {len(prices)}")
    print()
    print(f"{'Bar':>4}  {'Price':>10}  {'FRASMA':>10}  {'Upper':>10}  {'Lower':>10}")
    print("-" * 55)
    for i in range(20, len(prices), 10):
        if np.isnan(frasma[i]):
            continue
        print(f"{i:4d}  {prices[i]:10.5f}  {frasma[i]:10.5f}  {upper[i]:10.5f}  {lower[i]:10.5f}")
