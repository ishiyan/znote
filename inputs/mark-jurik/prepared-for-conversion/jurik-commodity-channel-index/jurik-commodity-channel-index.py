"""
JCCX — Jurik Commodity Channel Index

A JMA-based CCI replacement. Uses fast JMA(4) and slow JMA(Len), normalizes
their difference by 1.5× MAD of the difference series.

Reference: Decompiled from WealthScript implementation by Mark Jurik (Starlight).
"""

import math
import numpy as np


def jjma(prices: np.ndarray, length: int = 7, phase: int = 0) -> np.ndarray:
    """
    Jurik Moving Average (JMA) — Triple-stage adaptive filter.

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    length : int
        Smoothing length (period). Default 7.
    phase : int
        Phase parameter (-100 to +100). Default 0.

    Returns
    -------
    np.ndarray
        JMA values. First ~30 bars are NaN (warmup).
    """
    n = len(prices)
    result = np.full(n, np.nan)

    half_length_init = max((length - 1) / 2.0, 1e-10)
    phase_factor = phase / 100.0 + 1.5
    phase_factor = max(0.5, min(2.5, phase_factor))

    v1 = math.log(math.sqrt(half_length_init))
    log_power_exponent = max(0.0, v1 / math.log(2.0) + 2.0)
    vol_ratio_exponent = max(0.5, log_power_exponent - 2.0)

    bandwidth_param = math.sqrt(half_length_init) * log_power_exponent
    band_tracking_factor = bandwidth_param / (bandwidth_param + 1.0)

    half_length = half_length_init * 0.9
    base_ema_factor = half_length / (half_length + 2.0)

    sorted_volatility_list = np.zeros(128)
    circular_buffer = np.zeros(128)
    small_ring = np.zeros(10)
    ring_index = 0
    ring2_index = 0
    total_samples = 0
    smoothed_volatility = 0.0

    upper_band = 0.0
    lower_band = 0.0

    adaptive_ema = 0.0
    momentum_estimate = 0.0
    iir_velocity = 0.0
    output = 0.0

    init_buffer = np.zeros(62)
    warmup_counter = 0
    buffer_count = 0
    initialized = False

    bw_floor = max(0, int(math.floor(bandwidth_param)))
    bw_ceil = bw_floor + 1

    for bar in range(n):
        price = prices[bar]

        if buffer_count < 62:
            init_buffer[buffer_count] = price
            buffer_count += 1

        if warmup_counter < 61:
            warmup_counter += 1
        counter_power = max(1.0, (61 - warmup_counter) / 10.0 + 1.0)
        if warmup_counter <= 30:
            counter_power = 1.0

        if price > upper_band or not initialized:
            upper_band = price
        else:
            upper_band = price + (upper_band - price) * band_tracking_factor ** counter_power

        if price < lower_band or not initialized:
            lower_band = price
        else:
            lower_band = price + (lower_band - price) * band_tracking_factor ** counter_power

        current_volatility = max(abs(price - upper_band), abs(price - lower_band)) + 1e-10

        old_ring2_val = small_ring[ring2_index]
        small_ring[ring2_index] = current_volatility
        ring2_index = (ring2_index + 1) % 10
        smoothed_volatility += (current_volatility - old_ring2_val) / 10.0

        if total_samples < 128:
            total_samples += 1

        old_sorted_value = circular_buffer[ring_index]
        circular_buffer[ring_index] = smoothed_volatility
        ring_index = (ring_index + 1) % 128

        if total_samples > 1:
            old_position = 0
            binary_search_step = 64
            while binary_search_step > 0:
                mid = old_position + binary_search_step
                if mid < total_samples and sorted_volatility_list[mid] < old_sorted_value:
                    old_position = mid
                binary_search_step //= 2
            if old_position < total_samples and sorted_volatility_list[old_position] == old_sorted_value:
                pass
            elif old_position + 1 < total_samples and sorted_volatility_list[old_position + 1] == old_sorted_value:
                old_position += 1

            new_position = 0
            binary_search_step = 64
            while binary_search_step > 0:
                mid = new_position + binary_search_step
                if mid < total_samples and sorted_volatility_list[mid] < smoothed_volatility:
                    new_position = mid
                binary_search_step //= 2

            if old_position < new_position:
                for i in range(old_position, new_position):
                    if i + 1 < 128:
                        sorted_volatility_list[i] = sorted_volatility_list[i + 1]
                sorted_volatility_list[new_position] = smoothed_volatility
            elif old_position > new_position:
                for i in range(old_position, new_position + 1, -1):
                    if i < 128:
                        sorted_volatility_list[i] = sorted_volatility_list[i - 1]
                sorted_volatility_list[new_position + 1] = smoothed_volatility
            else:
                sorted_volatility_list[old_position] = smoothed_volatility
        else:
            sorted_volatility_list[0] = smoothed_volatility

        if total_samples >= 2:
            percentile_lower = int(math.ceil(0.25 * (total_samples - 1)))
            percentile_upper = int(math.ceil(0.75 * (total_samples - 1)))
            percentile_sum = 0.0
            for i in range(percentile_lower, percentile_upper + 1):
                percentile_sum += sorted_volatility_list[i]
            reference_volatility = percentile_sum / (percentile_upper - percentile_lower + 1)
        else:
            reference_volatility = current_volatility

        if reference_volatility < 1e-10:
            reference_volatility = 1e-10

        if warmup_counter <= 30:
            adaptive_ema = price
            momentum_estimate = 0.0
            output = price
            iir_velocity = 0.0

            if warmup_counter == 30 and buffer_count >= 30:
                initialized = True
                if bw_floor >= 1 and bw_floor < buffer_count:
                    diff1 = init_buffer[buffer_count - 1] - init_buffer[buffer_count - 1 - bw_floor]
                    diff2 = init_buffer[buffer_count - 1] - init_buffer[buffer_count - 1 - bw_ceil] if bw_ceil < buffer_count else diff1
                    frac = bandwidth_param - bw_floor
                    init_velocity = diff1 + (diff2 - diff1) * frac
                    adaptive_ema = price
                    momentum_estimate = init_velocity * (1.0 - base_ema_factor)

            result[bar] = np.nan
            continue

        vol_ratio = current_volatility / reference_volatility
        adaptive_power = vol_ratio ** vol_ratio_exponent
        adaptive_power = max(1.0, min(log_power_exponent, adaptive_power))

        adaptive_factor = base_ema_factor ** adaptive_power
        adaptive_ema = (1.0 - adaptive_factor) * price + adaptive_factor * adaptive_ema
        momentum_estimate = (price - adaptive_ema) * (1.0 - base_ema_factor) + base_ema_factor * momentum_estimate
        phase_shifted_value = phase_factor * momentum_estimate + adaptive_ema

        f20 = -2.0 * adaptive_factor
        f40 = adaptive_factor * adaptive_factor
        iir_gain = 1.0 + f20 + f40

        iir_velocity = (phase_shifted_value - output) * iir_gain + f40 * iir_velocity
        output = output + iir_velocity

        result[bar] = output

    return result


def jccx(prices: np.ndarray, length: int = 20) -> np.ndarray:
    """
    Compute the Jurik Commodity Channel Index (JCCX).

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values.
    length : int
        Period for the slow JMA. Default: 20.

    Returns
    -------
    np.ndarray
        JCCX values (unbounded oscillator).
    """
    fast_jma = jjma(prices, length=4, phase=0)
    slow_jma = jjma(prices, length=length, phase=0)
    diff = fast_jma - slow_jma

    n = len(prices)
    out = np.full(n, np.nan)

    for i in range(n):
        if np.isnan(diff[i]):
            continue
        w = min(i + 1, 3 * length)
        # Get window of diff values, skipping NaN
        window = diff[max(0, i - w + 1): i + 1]
        valid = window[~np.isnan(window)]
        if len(valid) == 0:
            out[i] = 0.0
            continue
        mad = np.mean(np.abs(valid))
        md = 1.5 * mad
        if md < 0.00001:
            out[i] = 0.0
        else:
            out[i] = diff[i] / md

    return out


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

    # 9 test cases: length in {10, 14, 20, 30, 40, 50, 60, 80, 100}
    test_cases = [
        (10, "EXPECTED_LEN_10"),
        (14, "EXPECTED_LEN_14"),
        (20, "EXPECTED_LEN_20"),
        (30, "EXPECTED_LEN_30"),
        (40, "EXPECTED_LEN_40"),
        (50, "EXPECTED_LEN_50"),
        (60, "EXPECTED_LEN_60"),
        (80, "EXPECTED_LEN_80"),
        (100, "EXPECTED_LEN_100"),
    ]

    # Generate reference outputs
    output_lines = []
    for length, arr_name in test_cases:
        result = jccx(prices, length=length)

        values = []
        for v in result:
            if np.isnan(v):
                values.append("math.nan")
            else:
                values.append(f"{v:.6f}")

        output_lines.append(f"# length={length}")
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
    for length, arr_name in test_cases:
        result = jccx(prices, length=length)
        valid = result[~np.isnan(result)]
        print(f"  {arr_name}: {len(valid)} valid bars, range [{valid.min():.4f}, {valid.max():.4f}]")
