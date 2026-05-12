"""
JAVEL — Jurik Adaptive Zero-Lag Velocity

Combines adaptive depth selection (volatility regime detection) with JXVEL
(two-stage: per-bar WLS slope + adaptive smoother with velocity/position dynamics).

Reference: Decompiled from WealthScript implementation by Mark Jurik (Starlight).
"""

import math
import numpy as np


EPS = 0.001


def jxvel_slope(prices: np.ndarray, depth_series: np.ndarray) -> np.ndarray:
    """
    Stage 1 — Per-bar weighted least-squares slope.

    On each bar, reads ceil(depth_series[bar]) as the lookback depth and computes
    the WLS slope with that bar-specific window size.
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
    Stage 2 — Adaptive smoother with explicit Period parameter.

    Uses 1001-element circular buffer, linear regression, MAD-based response,
    and velocity/position dynamics with Period-dependent damping.
    """
    n_bars = len(series)
    output = np.full(n_bars, np.nan)

    epsilon = 0.0001
    jrc03 = min(500.0, max(epsilon, period))
    jrc06 = max(31, int(np.ceil(2 * period)))
    jrc07 = min(30, int(np.ceil(period)))
    ema_factor = 1.0 - np.exp(-np.log(4.0) / (period / 2.0))
    damping = 0.86 - 0.55 / np.sqrt(jrc03)
    buffer_size = 1001

    value_buffer = np.zeros(buffer_size)
    buffer_head = 0
    current_length = 0
    velocity = 0.0
    output_position = 0.0
    smoothed_mad = 0.0
    initialized = False
    bar_count = 0

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

        old_index = buffer_head % buffer_size
        value_buffer[old_index] = value
        buffer_head += 1

        if current_length < jrc06:
            current_length += 1

        length = current_length
        sum_values = 0.0
        sum_weighted = 0.0
        for k in range(length):
            idx = (buffer_head - length + k) % buffer_size
            sum_values += value_buffer[idx]
            sum_weighted += value_buffer[idx] * k

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

        sum_abs_dev = 0.0
        for k in range(length):
            idx = (buffer_head - length + k) % buffer_size
            predicted = intercept + regression_slope * k
            sum_abs_dev += abs(value_buffer[idx] - predicted)

        raw_mad = sum_abs_dev / length
        scale = 1.2 * (jrc06 / length) ** 0.25
        raw_mad *= scale

        if bar_count <= jrc07 + 1:
            smoothed_mad = raw_mad
        else:
            smoothed_mad += ema_factor * (raw_mad - smoothed_mad)

        if not initialized:
            output_position = value
            initialized = True

        prediction_error = value - output_position

        if smoothed_mad * jrc03 < epsilon:
            response_factor = 1.0
        else:
            response_factor = 1.0 - np.exp(-abs(prediction_error) / (smoothed_mad * jrc03))

        velocity = response_factor * prediction_error + velocity * damping
        output_position += velocity

        output[bar] = output_position

    return output


def javel(
    prices: np.ndarray,
    lo_len: int = 5,
    hi_len: int = 30,
    sensitivity: float = 1.0,
    period: float = 3.0,
) -> np.ndarray:
    """
    Compute the Jurik Adaptive Zero-Lag Velocity.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values (e.g. close prices).
    lo_len : int
        Minimum adaptive depth. Default: 5.
    hi_len : int
        Maximum adaptive depth. Default: 30.
    sensitivity : float
        Controls how aggressively depth adapts. Default: 1.0.
    period : float
        Stage 2 smoother period. Default: 3.0.

    Returns
    -------
    np.ndarray
        Array of same length as `prices` with JAVEL velocity values.
        Warmup bars are NaN.
    """
    n = len(prices)
    value1 = np.zeros(n)
    adaptive_depth = np.zeros(n)

    for bar in range(1, n):
        value1[bar] = abs(prices[bar] - prices[bar - 1])

    for bar in range(n):
        len1 = min(bar, 99) + 1
        len2 = min(bar, 9) + 1

        avg1 = np.mean(value1[max(0, bar - len1 + 1): bar + 1])
        avg2 = np.mean(value1[max(0, bar - len2 + 1): bar + 1])

        value2 = sensitivity * math.log((EPS + avg1) / (EPS + avg2))
        value3 = value2 / (1.0 + abs(value2))
        adaptive_depth[bar] = lo_len + (hi_len - lo_len) * (1.0 + value3) / 2.0

    slope = jxvel_slope(prices, adaptive_depth)
    return jxvel_smooth(slope, period)


if __name__ == "__main__":
    INPUT_CLOSE = [
        91.500000, 94.815000, 94.375000, 95.095000, 93.780000, 94.625000, 92.530000, 92.750000, 90.315000, 92.470000,
        96.125000, 97.250000, 98.500000, 89.875000, 91.000000, 92.815000, 89.155000, 89.345000, 91.625000, 89.875000,
        88.375000, 87.625000, 84.780000, 83.000000, 83.500000, 81.375000, 84.440000, 89.250000, 86.375000, 86.250000,
        85.250000, 87.125000, 85.815000, 88.970000, 88.470000, 86.875000, 86.815000, 84.875000, 84.190000, 83.875000,
        83.375000, 85.500000, 89.190000, 89.440000, 91.095000, 90.750000, 91.440000, 89.000000, 91.000000, 90.500000,
        89.030000, 88.815000, 84.280000, 83.500000, 82.690000, 84.750000, 85.655000, 86.190000, 88.940000, 89.280000,
        88.625000, 88.500000, 91.970000, 91.500000, 93.250000, 93.500000, 93.155000, 91.720000, 90.000000, 89.690000,
        88.875000, 85.190000, 83.375000, 84.875000, 85.940000, 97.250000, 99.875000, 104.940000, 106.000000, 102.500000,
        102.405000, 104.595000, 106.125000, 106.000000, 106.065000, 104.625000, 108.625000, 109.315000, 110.500000, 112.750000,
        123.000000, 119.625000, 118.750000, 119.250000, 117.940000, 116.440000, 115.190000, 111.875000, 110.595000, 118.125000,
        116.000000, 116.000000, 112.000000, 113.750000, 112.940000, 116.000000, 120.500000, 116.620000, 117.000000, 115.250000,
        114.310000, 115.500000, 115.870000, 120.690000, 120.190000, 120.750000, 124.750000, 123.370000, 122.940000, 122.560000,
        123.120000, 122.560000, 124.620000, 129.250000, 131.000000, 132.250000, 131.000000, 132.810000, 134.000000, 137.380000,
        137.810000, 137.880000, 137.250000, 136.310000, 136.250000, 134.630000, 128.250000, 129.000000, 123.870000, 124.810000,
        123.000000, 126.250000, 128.380000, 125.370000, 125.690000, 122.250000, 119.370000, 118.500000, 123.190000, 123.500000,
        122.190000, 119.310000, 123.310000, 121.120000, 123.370000, 127.370000, 128.500000, 123.870000, 122.940000, 121.750000,
        124.440000, 122.000000, 122.370000, 122.940000, 124.000000, 123.190000, 124.560000, 127.250000, 125.870000, 128.860000,
        132.000000, 130.750000, 134.750000, 135.000000, 132.380000, 133.310000, 131.940000, 130.000000, 125.370000, 130.130000,
        127.120000, 125.190000, 122.000000, 125.000000, 123.000000, 123.500000, 120.060000, 121.000000, 117.750000, 119.870000,
        122.000000, 119.190000, 116.370000, 113.500000, 114.250000, 110.000000, 105.060000, 107.000000, 107.870000, 107.000000,
        107.120000, 107.000000, 91.000000, 93.940000, 93.870000, 95.500000, 93.000000, 94.940000, 98.250000, 96.750000,
        94.810000, 94.370000, 91.560000, 90.250000, 93.940000, 93.620000, 97.000000, 95.000000, 95.870000, 94.060000,
        94.620000, 93.750000, 98.000000, 103.940000, 107.870000, 106.060000, 104.500000, 105.000000, 104.190000, 103.060000,
        103.420000, 105.270000, 111.870000, 116.000000, 116.620000, 118.280000, 113.370000, 109.000000, 109.700000, 109.250000,
        107.000000, 109.190000, 110.000000, 109.200000, 110.120000, 108.000000, 108.620000, 109.750000, 109.810000, 109.000000,
        108.750000, 107.870000,
    ]

    prices = np.array(INPUT_CLOSE)

    # --- Test grid ---
    # Base: 3x3 lo_len x hi_len (sensitivity=1.0, period=3.0)
    # + Sensitivity sweep: sens in {0.5, 1.0, 2.5} with lo=5, hi=30, period=3.0
    # + Period sweep: period in {1.5, 3.0, 10.0} with lo=5, hi=30, sens=1.0

    test_cases = [
        # 3x3 base grid (sens=1.0, period=3.0)
        (2, 15, 1.0, 3.0, "EXPECTED_LO_2_HI_15"),
        (2, 30, 1.0, 3.0, "EXPECTED_LO_2_HI_30"),
        (2, 60, 1.0, 3.0, "EXPECTED_LO_2_HI_60"),
        (5, 15, 1.0, 3.0, "EXPECTED_LO_5_HI_15"),
        (5, 30, 1.0, 3.0, "EXPECTED_LO_5_HI_30"),
        (5, 60, 1.0, 3.0, "EXPECTED_LO_5_HI_60"),
        (10, 15, 1.0, 3.0, "EXPECTED_LO_10_HI_15"),
        (10, 30, 1.0, 3.0, "EXPECTED_LO_10_HI_30"),
        (10, 60, 1.0, 3.0, "EXPECTED_LO_10_HI_60"),
        # Sensitivity sweep (lo=5, hi=30, period=3.0)
        (5, 30, 0.5, 3.0, "EXPECTED_SENS_0_5"),
        (5, 30, 2.5, 3.0, "EXPECTED_SENS_2_5"),
        (5, 30, 5.0, 3.0, "EXPECTED_SENS_5_0"),
        # Period sweep (lo=5, hi=30, sens=1.0)
        (5, 30, 1.0, 1.5, "EXPECTED_PERIOD_1_5"),
        (5, 30, 1.0, 10.0, "EXPECTED_PERIOD_10_0"),
        (5, 30, 1.0, 30.0, "EXPECTED_PERIOD_30_0"),
    ]

    # Generate reference outputs
    output_lines = []
    for lo, hi, sens, per, arr_name in test_cases:
        result = javel(prices, lo_len=lo, hi_len=hi, sensitivity=sens, period=per)

        values = []
        for v in result:
            if np.isnan(v):
                values.append("math.nan")
            else:
                values.append(f"{v:.6f}")

        output_lines.append(f"# lo_len={lo}, hi_len={hi}, sensitivity={sens}, period={per}")
        output_lines.append(f"{arr_name} = [")

        for i in range(0, len(values), 10):
            chunk = values[i:i+10]
            line = "    " + ", ".join(chunk) + ","
            output_lines.append(line)

        output_lines.append("]")
        output_lines.append("")

    # Write test_data.py
    from pathlib import Path
    test_data_path = Path(__file__).parent / "test_data.py"

    with open(test_data_path, "w") as f:
        f.write("import math\n\n")
        f.write("INPUT_CLOSE = [\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = "    " + ", ".join(f"{v:.6f}" for v in chunk) + ","
            f.write(line + "\n")
        f.write("]\n\n")
        f.write("\n".join(output_lines))
        f.write("\n")

    print(f"Generated {len(test_cases)} reference outputs in test_data.py")
    for lo, hi, sens, per, arr_name in test_cases:
        result = javel(prices, lo_len=lo, hi_len=hi, sensitivity=sens, period=per)
        valid = result[~np.isnan(result)]
        print(f"  {arr_name}: {len(valid)} valid bars, range [{valid.min():.4f}, {valid.max():.4f}]")
