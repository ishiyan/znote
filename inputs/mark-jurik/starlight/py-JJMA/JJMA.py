"""
JJMA — Jurik Moving Average (Triple-Stage Adaptive Filter)

A faithful Python/NumPy implementation of the Jurik Moving Average,
reverse-engineered from the obfuscated WealthScript source.

Three stages:
  1. Adaptive volatility estimation via 128-element sorted list
  2. Adaptive first-order EMA with bandwidth controlled by volatility
  3. Two-pole IIR filter with phase (overshoot) control
"""

import numpy as np
import math


def jjma(prices: np.ndarray, length: int = 7, phase: int = 0) -> np.ndarray:
    """
    Compute the Jurik Moving Average (JMA).

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    length : int
        Smoothing length (period). Default 7.
    phase : int
        Phase parameter (-100 to +100). Controls overshoot/undershoot.
        Positive = more overshoot, negative = more lag. Default 0.

    Returns
    -------
    np.ndarray
        JMA values. First ~30 bars are NaN (warmup period).
    """
    n = len(prices)
    result = np.full(n, np.nan)

    # ==================== PRE-COMPUTATION ====================

    # half_length (f80_init)
    half_length_init = max((length - 1) / 2.0, 1e-10)

    # phase_factor (f10): maps phase from [-100,+100] to [0.5, 2.5]
    phase_factor = phase / 100.0 + 1.5
    phase_factor = max(0.5, min(2.5, phase_factor))

    # log_power_exponent (f98)
    v1 = math.log(math.sqrt(half_length_init))
    log_power_exponent = max(0.0, v1 / math.log(2.0) + 2.0)

    # vol_ratio_exponent (f88)
    vol_ratio_exponent = max(0.5, log_power_exponent - 2.0)

    # bandwidth_param (f78)
    bandwidth_param = math.sqrt(half_length_init) * log_power_exponent

    # band_tracking_factor (f90)
    band_tracking_factor = bandwidth_param / (bandwidth_param + 1.0)

    # Adjusted half_length for base EMA (f80)
    half_length = half_length_init * 0.9

    # base_ema_factor (f50)
    base_ema_factor = half_length / (half_length + 2.0)

    # ==================== STATE VARIABLES ====================

    # Stage 1: Volatility estimation
    sorted_volatility_list = np.zeros(128)  # 128-element sorted list
    circular_buffer = np.zeros(128)         # 128-element ring buffer
    small_ring = np.zeros(10)               # 10-element ring for averaging
    ring_index = 0          # s48: index into circular_buffer
    ring2_index = 0         # s50: index into small_ring
    total_samples = 0       # s70: total samples inserted into sorted list
    ring_sum = 0.0          # s8: running sum for ring buffer average
    smoothed_volatility = 0.0  # s20

    # Bands
    upper_band = 0.0        # f18
    lower_band = 0.0        # f38

    # Stage 2: Adaptive EMA
    adaptive_ema = 0.0      # fC0
    momentum_estimate = 0.0 # fC8

    # Stage 3: Two-pole IIR
    iir_velocity = 0.0      # fA8
    output = 0.0            # fB8

    # Initialization
    init_buffer = np.zeros(62)  # 62-element init buffer
    warmup_counter = 0      # fF8: counts up to 30
    buffer_count = 0        # fF0
    initialized = False     # f0

    # bandwidth_param floor/ceil for init interpolation
    bw_floor = max(0, int(math.floor(bandwidth_param)))  # fE0
    bw_ceil = bw_floor + 1  # fE8 (not explicitly ceil, just floor+1)

    # ==================== PER-BAR PROCESSING ====================

    for bar in range(n):
        price = prices[bar]

        # --- Initialization buffer fill ---
        if buffer_count < 62:
            init_buffer[buffer_count] = price
            buffer_count += 1

        # === STAGE 1: Adaptive Volatility Estimation ===

        # Determine counter power for band tracking speed
        if warmup_counter < 61:
            warmup_counter += 1
        # counter_power controls how quickly bands adapt
        # During early bars, bands snap to price faster
        counter_power = max(1.0, (61 - warmup_counter) / 10.0 + 1.0)
        if warmup_counter <= 30:
            counter_power = 1.0

        # Update upper band (f18)
        if price > upper_band or not initialized:
            upper_band = price
        else:
            upper_band = price + (upper_band - price) * band_tracking_factor ** counter_power

        # Update lower band (f38)
        if price < lower_band or not initialized:
            lower_band = price
        else:
            lower_band = price + (lower_band - price) * band_tracking_factor ** counter_power

        # Current volatility (fA0): max distance from bands
        current_volatility = max(abs(price - upper_band), abs(price - lower_band)) + 1e-10

        # Smooth volatility via 10-element ring (small_ring / ring2)
        old_ring2_val = small_ring[ring2_index]
        small_ring[ring2_index] = current_volatility
        ring2_index = (ring2_index + 1) % 10
        smoothed_volatility += (current_volatility - old_ring2_val) / 10.0

        # --- 128-element sorted list maintenance ---
        if total_samples < 128:
            # Still filling: just insert
            total_samples += 1

        # Value being removed from the sorted list (oldest in circular buffer)
        old_sorted_value = circular_buffer[ring_index]  # s10

        # Store new smoothed_volatility in circular buffer
        circular_buffer[ring_index] = smoothed_volatility
        ring_index = (ring_index + 1) % 128

        # Remove old value from sorted list (binary search for position)
        if total_samples > 1:
            # Find old_sorted_value position via binary search
            old_position = 0  # s58
            sorted_lower = 0  # s28
            sorted_upper = total_samples - 1  # s30
            binary_search_step = 64  # s68

            while binary_search_step > 0:
                mid = old_position + binary_search_step
                if mid < total_samples and sorted_volatility_list[mid] < old_sorted_value:
                    old_position = mid
                binary_search_step //= 2

            if old_position < total_samples and sorted_volatility_list[old_position] == old_sorted_value:
                pass  # found exact position
            elif old_position + 1 < total_samples and sorted_volatility_list[old_position + 1] == old_sorted_value:
                old_position += 1

            # Find insertion position for new value (smoothed_volatility)
            new_position = 0  # s60
            binary_search_step = 64

            while binary_search_step > 0:
                mid = new_position + binary_search_step
                if mid < total_samples and sorted_volatility_list[mid] < smoothed_volatility:
                    new_position = mid
                binary_search_step //= 2

            # Shift elements to remove old and insert new
            if old_position < new_position:
                # Shift left: overwrite old_position, insert at new_position
                for i in range(old_position, new_position):
                    if i + 1 < 128:
                        sorted_volatility_list[i] = sorted_volatility_list[i + 1]
                sorted_volatility_list[new_position] = smoothed_volatility
            elif old_position > new_position:
                # Shift right: move elements from new_position+1 up to old_position
                for i in range(old_position, new_position + 1, -1):
                    if i < 128:
                        sorted_volatility_list[i] = sorted_volatility_list[i - 1]
                sorted_volatility_list[new_position + 1] = smoothed_volatility
            else:
                sorted_volatility_list[old_position] = smoothed_volatility
        else:
            # First sample
            sorted_volatility_list[0] = smoothed_volatility

        # Extract percentile from sorted list
        # Percentile window bounds depend on total_samples
        if total_samples >= 2:
            percentile_lower = int(math.ceil(0.25 * (total_samples - 1)))  # s40
            percentile_upper = int(math.ceil(0.75 * (total_samples - 1)))  # s38

            # Sum values in percentile window
            percentile_sum = 0.0  # s18
            for i in range(percentile_lower, percentile_upper + 1):
                percentile_sum += sorted_volatility_list[i]

            # reference_volatility (f60)
            reference_volatility = percentile_sum / (percentile_upper - percentile_lower + 1)
        else:
            reference_volatility = current_volatility

        # Ensure reference_volatility is not zero
        if reference_volatility < 1e-10:
            reference_volatility = 1e-10

        # === STAGE 2: Adaptive First-Order EMA ===

        if warmup_counter <= 30:
            # During warmup: just track price
            adaptive_ema = price
            momentum_estimate = 0.0
            output = price
            iir_velocity = 0.0

            if warmup_counter == 30 and buffer_count >= 30:
                initialized = True
                # Initial velocity estimate using init_buffer and bandwidth_param
                # Interpolate between buffer values separated by bw_floor/bw_ceil
                if bw_floor >= 1 and bw_floor < buffer_count:
                    diff1 = init_buffer[buffer_count - 1] - init_buffer[buffer_count - 1 - bw_floor]
                    diff2 = init_buffer[buffer_count - 1] - init_buffer[buffer_count - 1 - bw_ceil] if bw_ceil < buffer_count else diff1
                    frac = bandwidth_param - bw_floor
                    init_velocity = diff1 + (diff2 - diff1) * frac
                    adaptive_ema = price
                    momentum_estimate = init_velocity * (1.0 - base_ema_factor)

            result[bar] = np.nan
            continue

        # Compute adaptive power (f58)
        vol_ratio = current_volatility / reference_volatility
        adaptive_power = vol_ratio ** vol_ratio_exponent
        adaptive_power = max(1.0, min(log_power_exponent, adaptive_power))

        # Adaptive smoothing factor (f30)
        adaptive_factor = base_ema_factor ** adaptive_power

        # Adaptive EMA update (fC0)
        adaptive_ema = (1.0 - adaptive_factor) * price + adaptive_factor * adaptive_ema

        # Momentum estimate (fC8)
        momentum_estimate = (price - adaptive_ema) * (1.0 - base_ema_factor) + base_ema_factor * momentum_estimate

        # Phase-shifted value (fD0): adds overshoot via phase_factor
        phase_shifted_value = phase_factor * momentum_estimate + adaptive_ema

        # === STAGE 3: Two-Pole IIR Filter ===

        # Filter coefficients
        f20 = -2.0 * adaptive_factor
        f40 = adaptive_factor * adaptive_factor
        iir_gain = 1.0 + f20 + f40  # = (1 - adaptive_factor)^2

        # IIR difference equation
        iir_velocity = (phase_shifted_value - output) * iir_gain + f40 * iir_velocity

        # Output update
        output = output + iir_velocity

        result[bar] = output

    return result


if __name__ == "__main__":
    # Quick demonstration
    np.random.seed(42)
    # Generate a simple price series (random walk)
    prices = 100.0 + np.cumsum(np.random.randn(200) * 0.5)

    jma_values = jjma(prices, length=7, phase=0)

    print("Bar | Price     | JMA")
    print("-" * 40)
    for i in range(len(prices)):
        if not np.isnan(jma_values[i]):
            print(f"{i:3d} | {prices[i]:9.4f} | {jma_values[i]:9.4f}")
        elif i < 35:
            print(f"{i:3d} | {prices[i]:9.4f} | {'NaN':>9s}")
