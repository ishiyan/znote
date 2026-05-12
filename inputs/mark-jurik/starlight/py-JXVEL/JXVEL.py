"""
JXVEL — Extended Jurik Velocity
Two-stage indicator with per-bar adaptive depth (Stage 1) and explicit Period parameter (Stage 2).
"""

import numpy as np


def jxvel_slope(prices: np.ndarray, depth_series: np.ndarray) -> np.ndarray:
    """
    Stage 1 — JXVELaux1: Per-bar weighted least-squares slope.

    On each bar, reads ceil(depth_series[bar]) as the lookback depth and computes
    the WLS slope with that bar-specific window size.

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    depth_series : np.ndarray
        Per-bar depth values (float). Ceiled to get integer window depth.

    Returns
    -------
    np.ndarray
        Slope (velocity) series. NaN for bars where insufficient history.
    """
    n_bars = len(prices)
    output = np.full(n_bars, np.nan)

    for bar in range(n_bars):
        depth = int(np.ceil(depth_series[bar]))
        if depth < 1:
            depth = 1
        if bar < depth:
            continue

        N = depth + 1
        S1 = N * (N + 1) / 2.0
        S2 = S1 * (2 * N + 1) / 3.0
        denom = S1 ** 3 - S2 ** 2

        if denom == 0:
            continue

        # Compute weighted sums over window [bar-depth, bar]
        sum_xw = 0.0
        sum_xw2 = 0.0
        for i in range(depth + 1):
            w = N - i
            val = prices[bar - i]
            sum_xw += val * w
            sum_xw2 += val * w * w

        output[bar] = (sum_xw2 * S1 - sum_xw * S2) / denom

    return output


def jxvel_smooth(series: np.ndarray, period: float = 3.0) -> np.ndarray:
    """
    Stage 2 — JXVELaux3: Adaptive smoother with explicit Period parameter.

    Key differences from JVEL's Stage 2:
    - 1001-element circular buffer (vs 100)
    - Period-dependent buffer length, damping, EMA factor
    - MAD scaled by 1.2
    - Full recomputation every bar (no incremental optimization)

    Parameters
    ----------
    series : np.ndarray
        Input series (typically slope output from Stage 1).
    period : float
        Smoother period parameter (default 3.0).

    Returns
    -------
    np.ndarray
        Adaptively smoothed output. NaN where input is NaN.
    """
    n_bars = len(series)
    output = np.full(n_bars, np.nan)

    # Constants
    epsilon = 0.0001
    jrc03 = min(500.0, max(epsilon, period))  # clamped period
    jrc06 = max(31, int(np.ceil(2 * period)))  # buffer usage length
    jrc07 = min(30, int(np.ceil(period)))  # initial slope lookback
    ema_factor = 1.0 - np.exp(-np.log(4.0) / (period / 2.0))  # note /2
    damping = 0.86 - 0.55 / np.sqrt(jrc03)
    buffer_size = 1001

    # State
    value_buffer = np.zeros(buffer_size)
    buffer_head = 0
    current_length = 0
    velocity = 0.0
    output_position = 0.0
    smoothed_mad = 0.0
    initialized = False
    bar_count = 0

    # Find first valid bar
    first_valid = -1
    for i in range(n_bars):
        if not np.isnan(series[i]):
            first_valid = i
            break

    if first_valid < 0:
        return output

    for bar in range(first_valid, n_bars):
        if np.isnan(series[bar]):
            continue

        value = series[bar]
        bar_count += 1

        # Insert into circular buffer
        old_index = buffer_head % buffer_size
        value_buffer[old_index] = value
        buffer_head += 1

        # Update current length
        if current_length < jrc06:
            current_length += 1

        # Full recomputation every bar
        length = current_length
        sum_values = 0.0
        sum_weighted = 0.0
        for k in range(length):
            idx = (buffer_head - length + k) % buffer_size
            sum_values += value_buffer[idx]
            sum_weighted += value_buffer[idx] * k

        # Linear regression over the buffer
        if length < 2:
            if not initialized:
                output_position = value
                initialized = True
            output[bar] = output_position
            continue

        midpoint = (length - 1) / 2.0
        sum_x_sq = length * (length - 1) * (2 * length - 1) / 6.0
        regression_denom = sum_x_sq - length * midpoint * midpoint

        if abs(regression_denom) < epsilon:
            regression_slope = 0.0
        else:
            regression_slope = (sum_weighted - midpoint * sum_values) / regression_denom

        intercept = sum_values / length - regression_slope * midpoint

        # Compute MAD from regression line
        sum_abs_dev = 0.0
        for k in range(length):
            idx = (buffer_head - length + k) % buffer_size
            predicted = intercept + regression_slope * k
            sum_abs_dev += abs(value_buffer[idx] - predicted)

        raw_mad = sum_abs_dev / length

        # Scale by 1.2 * (jrc06 / current_length)^0.25
        scale = 1.2 * (jrc06 / length) ** 0.25
        raw_mad *= scale

        # Smooth MAD via EMA
        if bar_count <= jrc07 + 1:
            smoothed_mad = raw_mad
        else:
            smoothed_mad += ema_factor * (raw_mad - smoothed_mad)

        # Initialize output position
        if not initialized:
            output_position = value
            initialized = True

        # Prediction error
        prediction_error = value - output_position

        # Response factor
        if smoothed_mad * jrc03 < epsilon:
            response_factor = 1.0
        else:
            response_factor = 1.0 - np.exp(-abs(prediction_error) / (smoothed_mad * jrc03))

        # Update velocity with damping
        velocity = response_factor * prediction_error + velocity * damping

        # Update position
        output_position += velocity

        output[bar] = output_position

    return output


def jxvel(prices: np.ndarray, depth_series: np.ndarray, period: float = 3.0) -> np.ndarray:
    """
    JXVEL — Extended Jurik Velocity.
    Combines Stage 1 (per-bar WLS slope) and Stage 2 (Period-parameterized adaptive smoother).

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    depth_series : np.ndarray
        Per-bar depth values (float). Must be same length as prices.
    period : float
        Smoother period parameter (default 3.0).

    Returns
    -------
    np.ndarray
        JXVEL output series.
    """
    slope = jxvel_slope(prices, depth_series)
    return jxvel_smooth(slope, period)


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    prices = np.cumsum(np.random.randn(500)) + 100.0
    # Varying depth between 5 and 15
    depth_series = 5.0 + 10.0 * np.random.rand(500)
    result = jxvel(prices, depth_series, period=10.0)
    valid = ~np.isnan(result)
    print(f"JXVEL computed for {valid.sum()} bars")
    print(f"Last 5 values: {result[-5:]}")
