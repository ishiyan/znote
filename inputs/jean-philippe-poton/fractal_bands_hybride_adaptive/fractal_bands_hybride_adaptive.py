"""
Fractal Bands Hybride Adaptive
Mnemonic: fbanha

Hybrid variant of Fractal Bands that replaces fixed normal_speed with
Ehlers' CyclePeriod indicator output multiplied by a Nyquist factor,
making the FRASMA doubly adaptive to both fractal dimension and
dominant market cycle.

Original author: Jean-Philippe Poton, Copyright 2008
Source: Unpublished
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


def ehlers_cycle_period(
    prices: np.ndarray,
    alpha_hp: float = 0.07,
) -> np.ndarray:
    """
    Ehlers' CyclePeriod indicator -- estimates the dominant cycle period
    of the price series using a high-pass filter, quadrature oscillator,
    and adaptive period measurement.

    Parameters
    ----------
    prices : np.ndarray
        1D array of prices (index 0 = oldest).
    alpha_hp : float
        High-pass filter alpha (controls cutoff). Default 0.07.

    Returns
    -------
    np.ndarray
        Estimated dominant cycle period for each bar. First ~7 bars are NaN.

    Reference: Ehlers, J. F. (2004). Cybernetic Analysis for Stocks and Futures.
    """
    n = len(prices)
    smooth = np.zeros(n)
    cycle = np.zeros(n)
    q1 = np.zeros(n)
    i1 = np.zeros(n)
    delta_phase = np.zeros(n)
    inst_period = np.full(n, 6.0)
    period_out = np.full(n, np.nan)

    for t in range(6, n):
        # 6-bar supersmoother
        smooth[t] = (prices[t] + 2.0 * prices[t - 1] + 2.0 * prices[t - 2] + prices[t - 3]) / 6.0

        # High-pass filter
        hp_coeff = (1.0 - 0.5 * alpha_hp) ** 2
        cycle[t] = (
            hp_coeff * (smooth[t] - 2.0 * smooth[t - 1] + smooth[t - 2])
            + 2.0 * (1.0 - alpha_hp) * cycle[t - 1]
            - (1.0 - alpha_hp) ** 2 * cycle[t - 2]
        )

        # Quadrature component (Hilbert transform approximation)
        q1[t] = (
            0.0962 * cycle[t]
            + 0.5769 * cycle[t - 2]
            - 0.5769 * cycle[t - 4]
            - 0.0962 * cycle[t - 6]
        ) * (0.5 + 0.08 * inst_period[t - 1])

        # In-phase component
        i1[t] = cycle[t - 3]

        # Smooth I and Q with EMA
        if t > 6:
            i1[t] = 0.15 * i1[t] + 0.85 * i1[t - 1]
            q1[t] = 0.15 * q1[t] + 0.85 * q1[t - 1]

        # Compute delta phase
        if abs(i1[t]) > 1e-10:
            dp = np.arctan(q1[t] / i1[t])
        else:
            dp = delta_phase[t - 1]

        # Clamp delta phase
        dp = max(dp, 0.1)
        dp = min(dp, 1.1)
        delta_phase[t] = dp

        # Median delta phase over 5 bars for robustness
        if t >= 10:
            median_dp = np.median(delta_phase[t - 4 : t + 1])
        else:
            median_dp = dp

        # Instantaneous period
        if abs(median_dp) > 1e-10:
            dc = 6.2832 / median_dp + 0.5
        else:
            dc = inst_period[t - 1]

        # Clamp and smooth
        dc = max(dc, 6.0)
        dc = min(dc, 50.0)
        inst_period[t] = 0.33 * dc + 0.67 * inst_period[t - 1]
        period_out[t] = inst_period[t]

    return period_out


def fractal_bands_hybride_adaptive(
    prices: np.ndarray,
    period: int = 30,
    normal_speed_fallback: int = 30,
    alpha: float = 2.0,
    nyquist: float = 0.5,
    alpha_hp: float = 0.07,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute Fractal Bands Hybride Adaptive.

    Like Fractal Bands, but normal_speed is replaced by
    CyclePeriod(price) * Nyquist at each bar.

    Parameters
    ----------
    prices : np.ndarray
        1D array of prices (index 0 = oldest).
    period : int
        Lookback period for FDI computation.
    normal_speed_fallback : int
        Fallback SMA period if CyclePeriod is not available.
    alpha : float
        Band width multiplier (raised to power H).
    nyquist : float
        Nyquist multiplier applied to the estimated cycle period.
    alpha_hp : float
        High-pass filter alpha for Ehlers CyclePeriod.

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
    cycle_periods = ehlers_cycle_period(prices, alpha_hp)

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

        # Adaptive normal_speed from CyclePeriod
        cp = cycle_periods[pos]
        if np.isnan(cp) or cp < 1.0:
            ns = float(normal_speed_fallback)
        else:
            ns = cp * nyquist

        speed = max(int(round(ns * beta)), 1)

        # FRASMA
        if pos + 1 < speed:
            continue
        window = prices[pos + 1 - speed : pos + 1]
        frasma_val = np.mean(window)
        frasma[pos] = frasma_val

        # Deviation over the FDI lookback window
        dev_window = prices[pos + 1 - period : pos + 1] if pos + 1 >= period else prices[: pos + 1]
        sq_sum = np.sum((dev_window - frasma_val) ** 2)
        deviation = 2.0 * np.sqrt(sq_sum / period)

        # Fractal bands
        band_mult = deviation * (alpha ** hurst)
        upper[pos] = frasma_val + band_mult
        lower[pos] = frasma_val - band_mult

    return frasma, upper, lower


if __name__ == "__main__":
    np.random.seed(42)

    # Synthetic FX-like data with a cycle component
    t = np.arange(200)
    cycle_component = 0.005 * np.sin(2.0 * np.pi * t / 25.0)
    trend_component = np.cumsum(np.random.randn(200) * 0.0002)
    prices = 1.3000 + trend_component + cycle_component

    frasma, upper, lower = fractal_bands_hybride_adaptive(
        prices, period=20, normal_speed_fallback=20, alpha=2.0, nyquist=0.5,
    )

    # Also compute cycle periods for display
    cp = ehlers_cycle_period(prices)

    print("Fractal Bands Hybride Adaptive (fbanha)")
    print("=" * 65)
    print(f"Period: 20, Alpha: 2.0, Nyquist: 0.5")
    print(f"Data length: {len(prices)}")
    print()
    print(f"{'Bar':>4}  {'Price':>10}  {'FRASMA':>10}  {'Upper':>10}  {'Lower':>10}  {'CyclePd':>8}")
    print("-" * 65)
    for i in range(20, len(prices), 15):
        if np.isnan(frasma[i]):
            continue
        cp_val = cp[i] if not np.isnan(cp[i]) else 0.0
        print(
            f"{i:4d}  {prices[i]:10.5f}  {frasma[i]:10.5f}"
            f"  {upper[i]:10.5f}  {lower[i]:10.5f}  {cp_val:8.2f}"
        )
