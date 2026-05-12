"""
New Moving Average (NMA) — Dürschner's Lag-Free Moving Average

Applies the Nyquist-Shannon sampling theorem to moving average design: by cascading
two moving averages whose period ratio satisfies the Nyquist criterion (λ = n1/n2 ≥ 2),
the resulting lag can be extrapolated away geometrically.

Formula: NMA = (1 + α) · MA1 - α · MA2
where: α = λ·(n1-1)/(n1-λ), λ = n1 // n2

Reference: Dr. Manfred G. Dürschner, "Moving Averages 3.0", IFTA Journal 2012.
MQL4 implementation by Juergen Moeck (simplex42fx@gmail.com), Copyright 2013.
"""

import math
import numpy as np
from enum import IntEnum


class MAType(IntEnum):
    SMA = 0
    EMA = 1
    SMMA = 2
    LWMA = 3


def sma(data: np.ndarray, period: int) -> np.ndarray:
    """Simple Moving Average (handles NaN-prefixed input)."""
    out = np.full_like(data, np.nan)
    for i in range(period - 1, len(data)):
        window = data[i - period + 1: i + 1]
        if np.any(np.isnan(window)):
            continue
        out[i] = np.mean(window)
    return out


def ema(data: np.ndarray, period: int) -> np.ndarray:
    """Exponential Moving Average (handles NaN-prefixed input)."""
    out = np.full_like(data, np.nan)
    multiplier = 2.0 / (period + 1)
    # Find first valid index
    first_valid = 0
    for i in range(len(data)):
        if not np.isnan(data[i]):
            first_valid = i
            break
    else:
        return out
    seed_end = first_valid + period
    if seed_end > len(data):
        return out
    out[seed_end - 1] = np.mean(data[first_valid:seed_end])
    for i in range(seed_end, len(data)):
        if np.isnan(data[i]):
            continue
        out[i] = (data[i] - out[i - 1]) * multiplier + out[i - 1]
    return out


def smma(data: np.ndarray, period: int) -> np.ndarray:
    """Smoothed Moving Average (handles NaN-prefixed input)."""
    out = np.full_like(data, np.nan)
    first_valid = 0
    for i in range(len(data)):
        if not np.isnan(data[i]):
            first_valid = i
            break
    else:
        return out
    seed_end = first_valid + period
    if seed_end > len(data):
        return out
    out[seed_end - 1] = np.mean(data[first_valid:seed_end])
    for i in range(seed_end, len(data)):
        if np.isnan(data[i]):
            continue
        out[i] = (out[i - 1] * (period - 1) + data[i]) / period
    return out


def lwma(data: np.ndarray, period: int) -> np.ndarray:
    """Linear Weighted Moving Average (handles NaN-prefixed input)."""
    out = np.full_like(data, np.nan)
    weights = np.arange(1, period + 1, dtype=float)
    weight_sum = weights.sum()
    for i in range(period - 1, len(data)):
        window = data[i - period + 1: i + 1]
        if np.any(np.isnan(window)):
            continue
        out[i] = np.dot(window, weights) / weight_sum
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


def nyquist_ma(
    prices: np.ndarray,
    primary_period: int = 0,
    secondary_period: int = 8,
    ma_type: MAType = MAType.LWMA,
) -> np.ndarray:
    """
    Compute the Nyquist Moving Average (NMA).

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values.
    primary_period : int
        n1, period of the first MA. 0 = auto-set to 4*secondary_period.
    secondary_period : int
        n2, period of the second MA. Default: 8.
    ma_type : MAType
        Type of moving average. Default: LWMA (recommended by Dürschner).

    Returns
    -------
    np.ndarray
        NMA values. NaN during warmup (n1 + n2 - 2 bars).
    """
    # Enforce Nyquist constraint
    if primary_period < 4:
        primary_period = 4
    if secondary_period < 2:
        secondary_period = 2
    if primary_period < secondary_period * 2:
        primary_period = secondary_period * 4

    # Compute alpha
    nyquist_ratio = primary_period // secondary_period
    alpha = nyquist_ratio * (primary_period - 1) / (primary_period - nyquist_ratio)

    # First filter: MA of raw price
    ma_primary = moving_average(prices, primary_period, ma_type)

    # Second filter: MA of MA1 output
    ma_secondary = moving_average(ma_primary, secondary_period, ma_type)

    # Geometric extrapolation
    nma = (1.0 + alpha) * ma_primary - alpha * ma_secondary

    return nma


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

    # Test grid:
    # 3x3 base: secondary_period x primary_period (LWMA)
    #   secondary: 4, 8, 16
    #   primary: auto (0), 2x secondary, 4x secondary
    # + MA type sweep: SMA, EMA, SMMA, LWMA with sec=8, pri=0
    test_cases = [
        # 3x3: secondary_period variations with auto primary
        (0, 4, MAType.LWMA, "EXPECTED_SEC_4_PRI_AUTO_LWMA"),
        (0, 8, MAType.LWMA, "EXPECTED_SEC_8_PRI_AUTO_LWMA"),
        (0, 16, MAType.LWMA, "EXPECTED_SEC_16_PRI_AUTO_LWMA"),
        # 3x3: explicit primary/secondary ratios (sec=8)
        (16, 8, MAType.LWMA, "EXPECTED_PRI_16_SEC_8_LWMA"),
        (32, 8, MAType.LWMA, "EXPECTED_PRI_32_SEC_8_LWMA"),
        (64, 8, MAType.LWMA, "EXPECTED_PRI_64_SEC_8_LWMA"),
        # Explicit primary/secondary ratios (sec=4)
        (8, 4, MAType.LWMA, "EXPECTED_PRI_8_SEC_4_LWMA"),
        (16, 4, MAType.LWMA, "EXPECTED_PRI_16_SEC_4_LWMA"),
        (32, 4, MAType.LWMA, "EXPECTED_PRI_32_SEC_4_LWMA"),
        # MA type sweep (sec=8, pri=auto)
        (0, 8, MAType.SMA, "EXPECTED_SEC_8_SMA"),
        (0, 8, MAType.EMA, "EXPECTED_SEC_8_EMA"),
        (0, 8, MAType.SMMA, "EXPECTED_SEC_8_SMMA"),
    ]

    # Generate reference outputs
    output_lines = []
    for pri, sec, mat, arr_name in test_cases:
        result = nyquist_ma(prices, primary_period=pri, secondary_period=sec, ma_type=mat)

        values = []
        for v in result:
            if np.isnan(v):
                values.append("math.nan")
            else:
                values.append(f"{v:.6f}")

        output_lines.append(f"# primary_period={pri}, secondary_period={sec}, ma_type={mat.name}")
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
    for pri, sec, mat, arr_name in test_cases:
        result = nyquist_ma(prices, primary_period=pri, secondary_period=sec, ma_type=mat)
        valid = result[~np.isnan(result)]
        print(f"  {arr_name}: {len(valid)} valid bars, range [{valid.min():.4f}, {valid.max():.4f}]")
