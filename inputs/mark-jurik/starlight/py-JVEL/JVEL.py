"""
JVEL — Jurik Velocity
Two-stage indicator: weighted least-squares slope + adaptive smoother.
"""

import numpy as np


def jvel_slope(prices: np.ndarray, depth: int = 10) -> np.ndarray:
    """
    Stage 1 — JVELaux1: Weighted least-squares slope over a fixed window.

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    depth : int
        Lookback parameter. Window size = depth + 1.

    Returns
    -------
    np.ndarray
        Slope (velocity) series. NaN for bars < depth.
    """
    n_bars = len(prices)
    output = np.full(n_bars, np.nan)

    N = depth + 1
    S1 = N * (N + 1) / 2.0
    S2 = S1 * (2 * N + 1) / 3.0
    denom = S1 ** 3 - S2 ** 2

    if denom == 0:
        return output

    # Precompute weights
    weights = np.arange(N, 0, -1, dtype=np.float64)  # [N, N-1, ..., 1]
    weights_sq = weights ** 2

    for bar in range(depth, n_bars):
        window = prices[bar - depth: bar + 1]
        sum_xw = np.dot(window, weights)
        sum_xw2 = np.dot(window, weights_sq)
        output[bar] = (sum_xw2 * S1 - sum_xw * S2) / denom

    return output


def jvel_smooth(series: np.ndarray, period: int = 30) -> np.ndarray:
    """
    Stage 2 — JVELaux3: Novel adaptive smoother with circular buffer.

    Parameters
    ----------
    series : np.ndarray
        Input series (typically the slope output from Stage 1).
    period : int
        Internal smoothing period (default 30).

    Returns
    -------
    np.ndarray
        Adaptively smoothed output. NaN where input is NaN.
    """
    n_bars = len(series)
    output = np.full(n_bars, np.nan)

    # Constants
    epsilon = 0.0001
    damping = 0.86 - 0.55 / np.sqrt(3.0)
    ema_factor = 1.0 - np.exp(-np.log(4.0) / 3.0)
    buffer_length = 31  # JR06
    buffer_size = 100
    init_slope_lookback = 3  # JR07

    # State
    value_buffer = np.zeros(buffer_size)  # JR41 - circular buffer
    buffer_head = 0  # JR25
    current_length = 0  # JR11
    sum_values = 0.0  # JR09
    sum_weighted = 0.0  # JR10
    velocity = 0.0  # JR08
    output_position = 0.0  # JR21
    smoothed_mad = 0.0  # JR20
    initialized = False
    bar_count = 0  # JR27

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
        old_value = value_buffer[old_index]
        value_buffer[old_index] = value
        buffer_head += 1

        # Update current length
        if current_length < buffer_length:
            current_length += 1
            # Incremental sum update (growing phase)
            sum_values += value
            sum_weighted += value * (current_length - 1)
            # Reweight existing contributions
            # When adding a new element, all previous positions shift by +1 in weight
            # Actually: sum_weighted tracks Σ(val[i] * position_i) where newest = current_length-1
            # On growth we need to recompute
        else:
            # Steady state: remove oldest contribution, add newest
            sum_values += value - old_value
            sum_weighted += value * (current_length - 1)
            # Shift: all existing items' positions decrease by 1 effectively
            sum_weighted -= sum_values - value

        # Every 1000 bars or during init: full recomputation to avoid float drift
        if bar_count <= buffer_length or bar_count % 1000 == 0:
            # Full recomputation from buffer
            length = min(current_length, buffer_length)
            sum_values = 0.0
            sum_weighted = 0.0
            for k in range(length):
                idx = (buffer_head - length + k) % buffer_size
                sum_values += value_buffer[idx]
                sum_weighted += value_buffer[idx] * k

        # Linear regression over the buffer
        length = current_length
        if length < 2:
            if not initialized:
                output_position = value
                initialized = True
            output[bar] = output_position
            continue

        midpoint = (length - 1) / 2.0  # JR13
        regression_denom = length * (length * length - 1) / 12.0  # JR12

        if regression_denom < epsilon:
            regression_slope = 0.0
        else:
            regression_slope = (sum_weighted / length - midpoint * sum_values / length) / (
                (length - 1) / 6.0 * (length + 1)
            )
            # Simplified: slope = (sum_weighted - midpoint * sum_values) / (length * regression_denom)
            regression_slope = (sum_weighted - midpoint * sum_values) / (length * regression_denom / length)

        # Recompute slope properly
        # For linear regression y = a + b*x over positions 0..length-1:
        # b = (Σ(x_i * y_i) - n*x_mean*y_mean) / (Σ(x_i^2) - n*x_mean^2)
        # = (sum_weighted - length * midpoint * (sum_values/length)) / (Σx^2 - length*midpoint^2)
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

        # Scale by (buffer_length / current_length)^0.25
        scale = (buffer_length / length) ** 0.25
        raw_mad *= scale

        # Smooth MAD via EMA
        if bar_count <= init_slope_lookback + 1:
            smoothed_mad = raw_mad
        else:
            smoothed_mad += ema_factor * (raw_mad - smoothed_mad)

        # Initialize output position
        if not initialized:
            output_position = value
            initialized = True

        # Prediction error
        prediction_error = value - output_position  # JR22

        # Response factor
        if smoothed_mad * period < epsilon:
            response_factor = 1.0
        else:
            response_factor = 1.0 - np.exp(-abs(prediction_error) / (smoothed_mad * period))

        # Update velocity with damping
        velocity = response_factor * prediction_error + velocity * damping

        # Update position
        output_position += velocity

        output[bar] = output_position

    return output


def jvel(prices: np.ndarray, depth: int = 10) -> np.ndarray:
    """
    JVEL — Jurik Velocity. Combines Stage 1 (weighted LS slope) and Stage 2 (adaptive smoother).

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    depth : int
        Lookback for slope calculation (default 10).

    Returns
    -------
    np.ndarray
        JVEL output series.
    """
    slope = jvel_slope(prices, depth)
    return jvel_smooth(slope)


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    prices = np.cumsum(np.random.randn(500)) + 100.0
    result = jvel(prices, depth=10)
    valid = ~np.isnan(result)
    print(f"JVEL computed for {valid.sum()} bars")
    print(f"Last 5 values: {result[-5:]}")
