"""
JVELCFB — Jurik Fractal-Adaptive Zero-Lag Velocity

Combines CFB (Composite Fractal Behavior) cycle detection with VEL (two-stage
velocity). CFB estimates dominant cycle period, stochastic normalization maps it
to a depth range, then VEL computes adaptive velocity.

Reference: Decompiled from WealthScript implementation by Mark Jurik (Starlight).
"""

import math
import numpy as np


# =============================================================================
# JCFB — Composite Fractal Behavior
# =============================================================================

SCALE_SETS = {
    1: [2, 3, 4, 6, 8, 12, 16, 24],
    2: [2, 3, 4, 6, 8, 12, 16, 24, 32, 48],
    3: [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96],
    4: [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192],
}


def jcfb_aux(prices: np.ndarray, depth: int) -> np.ndarray:
    """Single-scale efficiency ratio."""
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
    """Simple moving average."""
    out = np.zeros_like(series)
    cumsum = np.cumsum(series)
    out[window - 1:] = (cumsum[window - 1:] - np.concatenate(([0.0], cumsum[:-window]))) / window
    return out


def jcfb(prices: np.ndarray, fractal_type: int = 1, smooth: int = 10) -> np.ndarray:
    """Compute JCFB composite dominant cycle period."""
    prices = np.asarray(prices, dtype=float)
    n = len(prices)
    scales = SCALE_SETS[fractal_type]
    num_scales = len(scales)

    er_smooth = np.zeros((num_scales, n))
    for idx, depth in enumerate(scales):
        er = jcfb_aux(prices, depth)
        er_smooth[idx] = _sma(er, smooth)

    weights = np.zeros((num_scales, n))

    even_indices = list(range(0, num_scales, 2))[::-1]
    residual = np.ones(n)
    for idx in even_indices:
        weights[idx] = residual * er_smooth[idx]
        residual *= (1.0 - weights[idx])

    odd_indices = list(range(1, num_scales, 2))[::-1]
    residual = np.ones(n)
    for idx in odd_indices:
        weights[idx] = residual * er_smooth[idx]
        residual *= (1.0 - weights[idx])

    w_sq = weights ** 2
    scale_arr = np.array(scales, dtype=float).reshape(-1, 1)
    numerator = np.sum(w_sq * scale_arr, axis=0)
    denominator = np.sum(w_sq, axis=0)

    output = np.where(denominator != 0.0, numerator / denominator, 0.0)
    return output


# =============================================================================
# JXVEL — Extended Jurik Velocity (Stage 1 + Stage 2)
# =============================================================================

def jxvel_slope(prices: np.ndarray, depth_series: np.ndarray) -> np.ndarray:
    """Stage 1 — Per-bar weighted least-squares slope."""
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
    """Stage 2 — Adaptive smoother with explicit Period parameter."""
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


# =============================================================================
# JVELCFB — Main entry point
# =============================================================================

def jvelcfb(
    prices: np.ndarray,
    lo_depth: int = 5,
    hi_depth: int = 30,
    fractal_type: int = 1,
    smooth: int = 10,
) -> np.ndarray:
    """
    Compute the Jurik Fractal-Adaptive Zero-Lag Velocity.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values.
    lo_depth : int
        Minimum VEL depth. Default: 5.
    hi_depth : int
        Maximum VEL depth. Default: 30.
    fractal_type : int
        CFB fractal type (1–4). Default: 1.
    smooth : int
        CFB smoothing window. Default: 10.

    Returns
    -------
    np.ndarray
        JVELCFB velocity values. NaN during warmup.
    """
    n = len(prices)
    cfb = jcfb(prices, fractal_type=fractal_type, smooth=smooth)

    # Stochastic normalization of CFB → depth series
    depth_series = np.zeros(n, dtype=np.float64)
    cfbmin = cfb[0]
    cfbmax = cfb[0]

    for i in range(n):
        cfbmin = min(cfbmin, cfb[i])
        cfbmax = max(cfbmax, cfb[i])
        if cfbmax == cfbmin:
            sr = 0.5
        else:
            sr = (cfb[i] - cfbmin) / (cfbmax - cfbmin)
        depth_series[i] = lo_depth + sr * (hi_depth - lo_depth)

    # Two-stage VEL
    slope = jxvel_slope(prices, depth_series)
    return jxvel_smooth(slope, period=3.0)


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

    # 3x3 base grid: lo_depth x hi_depth (fractal_type=1, smooth=10)
    # + fractal_type sweep (lo=5, hi=30, smooth=10)
    # + smooth sweep (lo=5, hi=30, fractal_type=1)
    test_cases = [
        # 3x3 base grid
        (2, 15, 1, 10, "EXPECTED_LO_2_HI_15"),
        (2, 30, 1, 10, "EXPECTED_LO_2_HI_30"),
        (2, 60, 1, 10, "EXPECTED_LO_2_HI_60"),
        (5, 15, 1, 10, "EXPECTED_LO_5_HI_15"),
        (5, 30, 1, 10, "EXPECTED_LO_5_HI_30"),
        (5, 60, 1, 10, "EXPECTED_LO_5_HI_60"),
        (10, 15, 1, 10, "EXPECTED_LO_10_HI_15"),
        (10, 30, 1, 10, "EXPECTED_LO_10_HI_30"),
        (10, 60, 1, 10, "EXPECTED_LO_10_HI_60"),
        # Fractal type sweep (lo=5, hi=30, smooth=10)
        (5, 30, 2, 10, "EXPECTED_FTYPE_2"),
        (5, 30, 3, 10, "EXPECTED_FTYPE_3"),
        (5, 30, 4, 10, "EXPECTED_FTYPE_4"),
        # Smooth sweep (lo=5, hi=30, fractal_type=1)
        (5, 30, 1, 5, "EXPECTED_SMOOTH_5"),
        (5, 30, 1, 20, "EXPECTED_SMOOTH_20"),
        (5, 30, 1, 40, "EXPECTED_SMOOTH_40"),
    ]

    # Generate reference outputs
    output_lines = []
    for lo, hi, ft, sm, arr_name in test_cases:
        result = jvelcfb(prices, lo_depth=lo, hi_depth=hi, fractal_type=ft, smooth=sm)

        values = []
        for v in result:
            if np.isnan(v):
                values.append("math.nan")
            else:
                values.append(f"{v:.6f}")

        output_lines.append(f"# lo_depth={lo}, hi_depth={hi}, fractal_type={ft}, smooth={sm}")
        output_lines.append(f"{arr_name} = [")

        for i in range(0, len(values), 10):
            chunk = values[i:i + 10]
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
            chunk = INPUT_CLOSE[i:i + 10]
            line = "    " + ", ".join(f"{v:.6f}" for v in chunk) + ","
            f.write(line + "\n")
        f.write("]\n\n")
        f.write("\n".join(output_lines))
        f.write("\n")

    print(f"Generated {len(test_cases)} reference outputs in test_data.py")
    for lo, hi, ft, sm, arr_name in test_cases:
        result = jvelcfb(prices, lo_depth=lo, hi_depth=hi, fractal_type=ft, smooth=sm)
        valid = result[~np.isnan(result)]
        print(f"  {arr_name}: {len(valid)} valid bars, range [{valid.min():.4f}, {valid.max():.4f}]")
