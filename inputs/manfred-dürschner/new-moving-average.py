"""
New Moving Average (NMA) — Python Implementation
================================================

Converted from MQL4 code by Juergen Moeck (Copyright 2013, simplex42fx@gmail.com).

Algorithm published in:
    Dr. Manfred G. Dürschner: "Moving Averages 3.0", IFTA Journal 2012 Edition, pp. 14-19.
    https://www.ifta.org/assets/docs/d_ifta_journal_12.pdf

Original German version (archived):
    https://web.archive.org/web/20200109020131/http://www.vtad.de/sites/files/forschung/
    M_Duerschner_Gleitende_Durchschnnitte_3.pdf

This module implements:
    1. NyquistMA — The core NMA indicator (lag-free double-smoothed moving average)
    2. Aroon Nyquist — Aroon Oscillator on NMA with Inverse Fisher Transform
    3. StochRSI on Nyquist — Stochastic RSI on NMA with Inverse Fisher Transform

Dependencies: numpy, pandas (optional for convenience)
"""

import numpy as np
from enum import IntEnum
from typing import Optional


# =============================================================================
# ENUMERATIONS
# =============================================================================

class MAType(IntEnum):
    """Moving average types matching MQL4 constants."""
    SMA = 0   # Simple Moving Average
    EMA = 1   # Exponential Moving Average
    SMMA = 2  # Smoothed Moving Average (recursive)
    LWMA = 3  # Linear Weighted Moving Average


class PriceField(IntEnum):
    """Price field selection matching MQL4 PRICE_* constants."""
    CLOSE = 0
    OPEN = 1
    HIGH = 2
    LOW = 3
    MEDIAN = 4    # (High + Low) / 2
    TYPICAL = 5   # (High + Low + Close) / 3
    WEIGHTED = 6  # (High + Low + Close + Close) / 4


# =============================================================================
# MOVING AVERAGE FUNCTIONS
# =============================================================================

def sma(data: np.ndarray, period: int) -> np.ndarray:
    """Simple Moving Average — arithmetic mean of last `period` values."""
    out = np.full_like(data, np.nan)
    for i in range(period - 1, len(data)):
        out[i] = np.mean(data[i - period + 1 : i + 1])
    return out


def ema(data: np.ndarray, period: int) -> np.ndarray:
    """Exponential Moving Average — recursive with multiplier 2/(period+1)."""
    out = np.full_like(data, np.nan)
    multiplier = 2.0 / (period + 1)
    # Seed with SMA of first `period` values
    out[period - 1] = np.mean(data[:period])
    for i in range(period, len(data)):
        out[i] = (data[i] - out[i - 1]) * multiplier + out[i - 1]
    return out


def smma(data: np.ndarray, period: int) -> np.ndarray:
    """Smoothed Moving Average (Wilder's smoothing) — EMA with multiplier 1/period."""
    out = np.full_like(data, np.nan)
    # Seed with SMA
    out[period - 1] = np.mean(data[:period])
    for i in range(period, len(data)):
        out[i] = (out[i - 1] * (period - 1) + data[i]) / period
    return out


def lwma(data: np.ndarray, period: int) -> np.ndarray:
    """Linear Weighted Moving Average — weights linearly from 1 (oldest) to period (newest)."""
    out = np.full_like(data, np.nan)
    weights = np.arange(1, period + 1, dtype=float)
    weight_sum = weights.sum()
    for i in range(period - 1, len(data)):
        out[i] = np.dot(data[i - period + 1 : i + 1], weights) / weight_sum
    return out


def moving_average(data: np.ndarray, period: int, ma_type: MAType = MAType.LWMA) -> np.ndarray:
    """Dispatch to the appropriate moving average function."""
    if ma_type == MAType.SMA:
        return sma(data, period)
    elif ma_type == MAType.EMA:
        return ema(data, period)
    elif ma_type == MAType.SMMA:
        return smma(data, period)
    elif ma_type == MAType.LWMA:
        return lwma(data, period)
    else:
        raise ValueError(f"Unknown MA type: {ma_type}")


# =============================================================================
# NYQUIST-SHANNON CORE FUNCTIONS
# Translated from _simplex_nyquist.mqh
# =============================================================================

def check_nyquist_periods(primary_period: int, secondary_period: int) -> tuple[int, int]:
    """
    Enforce Nyquist constraint on period parameters.

    Rules (from MQL: checkNyquistPeriods):
        - primary_period must be >= 4
        - secondary_period must be >= 2
        - primary_period must be >= 2 * secondary_period
        - If violated, primary is set to 4 * secondary (intentionally 4, not 2,
          as a safety margin chosen by the MQL author)

    Returns:
        (primary_period, secondary_period) — corrected values
    """
    if primary_period < 4:
        primary_period = 4
    if secondary_period < 2:
        secondary_period = 2
    if primary_period < secondary_period * 2:
        # Intentionally uses 4x (not 2x minimum) as default when auto-correcting
        primary_period = secondary_period * 4
    return primary_period, secondary_period


def get_nyquist_alpha(primary_period: int, secondary_period: int) -> float:
    """
    Compute the Nyquist lag-compensation factor alpha.

    Formula (Dürschner, eq. 4):
        lambda = n1 / n2  (integer division)
        alpha  = lambda * (n1 - 1) / (n1 - lambda)

    Args:
        primary_period:   n1 — period of the first MA (applied to price)
        secondary_period: n2 — period of the second MA (applied to MA1 output)

    Returns:
        alpha — the extrapolation weight
    """
    nyquist_ratio = primary_period // secondary_period  # integer division, as in MQL
    alpha = nyquist_ratio * (primary_period - 1) / (primary_period - nyquist_ratio)
    return alpha


def get_nyquist_ma(alpha: float, ma1_value: float, ma2_value: float) -> float:
    """
    Compute a single NMA value from the two filter outputs.

    Formula (Dürschner, eq. 3):
        NMA = (1 + alpha) * MA1 - alpha * MA2

    This is the geometric extrapolation that cancels the combined lag.
    """
    return (alpha + 1.0) * ma1_value - alpha * ma2_value


# =============================================================================
# INDICATOR 1: NyquistMA (Core NMA)
# Translated from NyquistMA_v1_0.mq4
# =============================================================================

def nyquist_ma(
    prices: np.ndarray,
    primary_period: int = 0,
    secondary_period: int = 8,
    ma_type: MAType = MAType.LWMA,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute the Nyquist Moving Average.

    This is the core indicator: applies MA1 to price, MA2 to MA1's output,
    then extrapolates to cancel lag.

    Args:
        prices:           1-D array of price values
        primary_period:   n1 (0 = auto-set based on Nyquist constraint)
        secondary_period: n2
        ma_type:          type of moving average (default: LWMA, recommended by Dürschner)

    Returns:
        (nma, ma_primary, ma_secondary) — all as numpy arrays
    """
    # Enforce Nyquist constraint (auto-sets primary if 0)
    primary_period, secondary_period = check_nyquist_periods(primary_period, secondary_period)

    # Compute alpha (constant for the entire series)
    alpha = get_nyquist_alpha(primary_period, secondary_period)

    # First filter: MA of raw price series
    ma_primary = moving_average(prices, primary_period, ma_type)

    # Second filter: MA of the first filter's output
    # We need to handle NaN propagation — only compute where ma_primary is valid
    ma_secondary = moving_average(ma_primary, secondary_period, ma_type)

    # Nyquist extrapolation: cancel lag geometrically
    nma = (1.0 + alpha) * ma_primary - alpha * ma_secondary

    return nma, ma_primary, ma_secondary


# =============================================================================
# HELPER FUNCTIONS FOR TRADING SYSTEMS
# =============================================================================

def inverse_fisher_transform(x: float) -> float:
    """
    Inverse Fisher Transform: maps (-inf, +inf) to (-1, +1).

    Formula: IFT(x) = (e^(2x) - 1) / (e^(2x) + 1) = tanh(x)

    Used to sharpen oscillator signals into clear buy/sell zones.
    """
    y = np.exp(2.0 * x)
    # Guard against overflow (when y = -1, denominator = 0)
    if np.isscalar(y):
        return 0.0 if y == -1.0 else (y - 1.0) / (y + 1.0)
    # Vectorized version
    result = np.where(y == -1.0, 0.0, (y - 1.0) / (y + 1.0))
    return result


def inverse_fisher_transform_array(data: np.ndarray) -> np.ndarray:
    """Vectorized Inverse Fisher Transform for an entire array."""
    y = np.exp(2.0 * data)
    return np.where(np.isnan(data), np.nan, np.where(y == -1.0, 0.0, (y - 1.0) / (y + 1.0)))


def stochastic_fast_k(data: np.ndarray, period: int) -> np.ndarray:
    """
    Stochastic Fast %K on an arbitrary data array.

    Formula: %K = (value - lowest) / (highest - lowest) * 100

    Translated from getStochOnArray() in _simplex_nyquist.mqh.
    """
    out = np.full_like(data, np.nan)
    for i in range(period - 1, len(data)):
        window = data[i - period + 1 : i + 1]
        if np.any(np.isnan(window)):
            continue
        lowest = np.min(window)
        highest = np.max(window)
        denom = max(0.000001, highest - lowest)  # avoid division by zero
        out[i] = ((data[i] - lowest) / denom) * 100.0
    return out


def highest_index(data: np.ndarray, period: int, offset: int) -> int:
    """
    Find the index of the highest value within a lookback window.

    Translated from getHighestIndex() in _simplex_nyquist.mqh.
    """
    start = max(0, offset - period + 1)
    window = data[start : offset + 1]
    return start + int(np.argmax(window))


def lowest_index(data: np.ndarray, period: int, offset: int) -> int:
    """
    Find the index of the lowest value within a lookback window.

    Translated from getLowestIndex() in _simplex_nyquist.mqh.
    """
    start = max(0, offset - period + 1)
    window = data[start : offset + 1]
    return start + int(np.argmin(window))


def rsi(data: np.ndarray, period: int) -> np.ndarray:
    """
    Relative Strength Index (Wilder's RSI).

    Returns values in range [0, 100].
    """
    out = np.full_like(data, np.nan)
    deltas = np.diff(data)

    # Seed averages with SMA of first `period` changes
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    if len(gains) < period:
        return out

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    if avg_loss == 0:
        out[period] = 100.0
    else:
        out[period] = 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            out[i + 1] = 100.0
        else:
            out[i + 1] = 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)

    return out


# =============================================================================
# INDICATOR 2: Aroon Nyquist
# Translated from Aroon_Nyquist_v1_0.mq4
#
# Trading system: Aroon Oscillator applied to NMA output, then sharpened
# with Inverse Fisher Transform. Matches Figure 4 in Dürschner's paper.
# =============================================================================

def aroon_nyquist(
    prices: np.ndarray,
    aroon_period: int = 5,
    primary_period: int = 0,
    secondary_period: int = 8,
    ma_type: MAType = MAType.LWMA,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Aroon Oscillator on NMA with Inverse Fisher Transform.

    The Aroon Oscillator measures trend strength as the difference between
    bars since highest high and bars since lowest low. Applying it to the
    NMA (instead of raw price) reduces whipsaws. The Inverse Fisher Transform
    then compresses the result into clear +100/-100 signal zones.

    Args:
        prices:           1-D price array
        aroon_period:     lookback for Aroon high/low detection
        primary_period:   NMA primary period (0 = auto)
        secondary_period: NMA secondary period
        ma_type:          moving average type

    Returns:
        (ifisher_aroon_nma, aroon_nma) — IFT-sharpened signal and raw Aroon on NMA
    """
    # Compute NMA
    nma, _, _ = nyquist_ma(prices, primary_period, secondary_period, ma_type)

    n = len(nma)
    aroon_osc = np.full(n, np.nan)
    ifisher_aroon = np.full(n, np.nan)

    # Aroon Oscillator on NMA values
    for i in range(aroon_period, n):
        if np.isnan(nma[i]):
            continue
        hi_idx = highest_index(nma, aroon_period, i)
        lo_idx = lowest_index(nma, aroon_period, i)
        # Aroon oscillator = 100 * (bars_since_low - bars_since_high) / period
        aroon_osc[i] = 100.0 * ((i - lo_idx) - (i - hi_idx)) / aroon_period

    # Inverse Fisher Transform to sharpen signals
    for i in range(n):
        if not np.isnan(aroon_osc[i]):
            ifisher_aroon[i] = 100.0 * inverse_fisher_transform(aroon_osc[i])

    return ifisher_aroon, aroon_osc


# =============================================================================
# INDICATOR 3: StochRSI on Nyquist
# Translated from StochRSI_on_Nyquist_v1_0.mq4
#
# Trading system: Stochastic of RSI applied to NMA as price proxy,
# optionally sharpened with Inverse Fisher Transform.
# Matches Figure 5 in Dürschner's paper (intraday system).
# =============================================================================

def stoch_rsi_on_nyquist(
    prices: np.ndarray,
    rsi_period: int = 5,
    stoch_period: int = 3,
    primary_period: int = 0,
    secondary_period: int = 8,
    ma_type: MAType = MAType.LWMA,
    use_fisher: bool = True,
    use_proxy: bool = True,
) -> np.ndarray:
    """
    Stochastic RSI on NMA price proxy with optional Inverse Fisher Transform.

    Pipeline:
        1. Compute NMA as a smoothed price proxy (or use raw price if use_proxy=False)
        2. Compute RSI on the proxy, rescaled to [-100, +100]
        3. Compute Stochastic %K on the RSI values
        4. Optionally apply Inverse Fisher Transform to sharpen the signal

    Args:
        prices:           1-D price array
        rsi_period:       RSI calculation period
        stoch_period:     Stochastic %K lookback
        primary_period:   NMA primary period (0 = auto)
        secondary_period: NMA secondary period
        ma_type:          moving average type
        use_fisher:       apply Inverse Fisher Transform to final output
        use_proxy:        use NMA as price proxy (False = use raw price)

    Returns:
        stoch_rsi — the final oscillator values
    """
    # Step 1: Determine price proxy
    if use_proxy:
        proxy, _, _ = nyquist_ma(prices, primary_period, secondary_period, ma_type)
    else:
        proxy = prices.copy()

    # Step 2: RSI on proxy, rescaled to [-100, +100] range
    rsi_values = rsi(proxy, rsi_period)
    rsi_rescaled = 2.0 * rsi_values - 100.0  # shift from [0,100] to [-100,+100]

    # Step 3: Stochastic %K on rescaled RSI
    stoch_values = stochastic_fast_k(rsi_rescaled, stoch_period)

    # Step 4: Optional Inverse Fisher Transform
    if use_fisher:
        result = np.full_like(stoch_values, np.nan)
        for i in range(len(stoch_values)):
            if not np.isnan(stoch_values[i]):
                result[i] = 100.0 * inverse_fisher_transform(stoch_values[i])
        return result
    else:
        return stoch_values


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Generate a simple sine wave + trend for demonstration
    np.random.seed(42)
    t = np.arange(200)
    price = 100 + 0.05 * t + 5 * np.sin(2 * np.pi * t / 40) + np.random.randn(200) * 0.5

    # Compute NMA with default parameters (LWMA, secPeriod=8, priPeriod=auto=32)
    nma_values, ma1, ma2 = nyquist_ma(price, primary_period=0, secondary_period=8)

    print(f"Price[-1]:  {price[-1]:.4f}")
    print(f"MA1[-1]:    {ma1[-1]:.4f}")
    print(f"MA2[-1]:    {ma2[-1]:.4f}")
    print(f"NMA[-1]:    {nma_values[-1]:.4f}")
    print(f"NMA lag:    ~0 bars (by construction)")
    print()

    # Compute Aroon Nyquist trading signal
    ifisher_aroon, aroon_raw = aroon_nyquist(price, aroon_period=5)
    last_valid = ifisher_aroon[~np.isnan(ifisher_aroon)][-1]
    print(f"Aroon IFisher signal: {last_valid:.1f} (range: -100 to +100)")

    # Compute StochRSI on Nyquist
    stoch_signal = stoch_rsi_on_nyquist(price, rsi_period=5, stoch_period=3)
    last_valid = stoch_signal[~np.isnan(stoch_signal)][-1]
    print(f"StochRSI signal:      {last_valid:.1f} (range: -100 to +100)")
