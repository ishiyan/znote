"""
JARSX — Jurik Adaptive Relative Trend Strength Index

Combines adaptive length selection (based on volatility regime detection)
with the RSX core (triple-cascaded lag-reduced EMA oscillator).

Note: The Sensitivity parameter from the original WealthScript source has been
removed because it has no effect on the output. See the .md file for explanation.

Reference: Decompiled from WealthScript implementation by Mark Jurik (Starlight).
"""

import math
import numpy as np


def jarsx(
    prices: np.ndarray,
    lo_len: int = 5,
    hi_len: int = 30,
) -> np.ndarray:
    """
    Compute the Jurik Adaptive Relative Trend Strength Index.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values (e.g. close prices).
    lo_len : int
        Minimum adaptive length (fastest response). Default: 5.
    hi_len : int
        Maximum adaptive length (most smoothing). Default: 30.

    Returns
    -------
    np.ndarray
        Array of same length as `prices` with JARSX values in [0, 100].
        Warmup bars are set to NaN.
    """
    eps = 0.001
    n = len(prices)
    out = np.full(n, np.nan)

    if n < 2:
        return out

    # --- Step 1: Compute adaptive length series ---
    value1 = np.zeros(n)
    value1[1:] = np.abs(np.diff(prices))

    adaptive_length = np.zeros(n)
    for i in range(n):
        window_long = min(i, 99) + 1
        avg1 = np.mean(value1[max(0, i - window_long + 1): i + 1])

        window_short = min(i, 9) + 1
        avg2 = np.mean(value1[max(0, i - window_short + 1): i + 1])

        value2 = math.log((eps + avg1) / (eps + avg2))
        value3 = value2 / (1.0 + abs(value2))
        adaptive_length[i] = lo_len + (hi_len - lo_len) * (1.0 + value3) / 2.0

    # --- Step 2: RSX core using length from bar 0 ---
    length = int(adaptive_length[0])
    length = max(length, 2)

    kg = 3.0 / (length + 2)
    c = 1.0 - kg

    warmup = max(length - 1, 5)

    # Signal path accumulators (3 cascaded stages)
    sig1_a = sig1_b = 0.0
    sig2_a = sig2_b = 0.0
    sig3_a = sig3_b = 0.0

    # Denominator path accumulators (3 cascaded stages)
    den1_a = den1_b = 0.0
    den2_a = den2_b = 0.0
    den3_a = den3_b = 0.0

    for bar in range(1, n):
        mom = 100.0 * (prices[bar] - prices[bar - 1])
        abs_mom = abs(mom)

        # Signal path — Stage 1
        sig1_a = c * sig1_a + kg * mom
        sig1_b = kg * sig1_a + c * sig1_b
        s1 = 1.5 * sig1_a - 0.5 * sig1_b

        # Signal path — Stage 2
        sig2_a = c * sig2_a + kg * s1
        sig2_b = kg * sig2_a + c * sig2_b
        s2 = 1.5 * sig2_a - 0.5 * sig2_b

        # Signal path — Stage 3
        sig3_a = c * sig3_a + kg * s2
        sig3_b = kg * sig3_a + c * sig3_b
        numerator = 1.5 * sig3_a - 0.5 * sig3_b

        # Denominator path — Stage 1
        den1_a = c * den1_a + kg * abs_mom
        den1_b = kg * den1_a + c * den1_b
        d1 = 1.5 * den1_a - 0.5 * den1_b

        # Denominator path — Stage 2
        den2_a = c * den2_a + kg * d1
        den2_b = kg * den2_a + c * den2_b
        d2 = 1.5 * den2_a - 0.5 * den2_b

        # Denominator path — Stage 3
        den3_a = c * den3_a + kg * d2
        den3_b = kg * den3_a + c * den3_b
        denominator = 1.5 * den3_a - 0.5 * den3_b

        # Output after warmup
        if bar >= warmup:
            if denominator != 0.0:
                value = (numerator / denominator + 1.0) * 50.0
            else:
                value = 50.0
            out[bar] = max(0.0, min(100.0, value))

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

    # 3x3 grid: lo_len x hi_len
    # lo_len: 2 (fast), 5 (default), 10 (slow floor)
    # hi_len: 15 (short ceiling), 30 (default), 60 (long ceiling)
    test_cases = [
        # (lo_len, hi_len, description)
        (2, 15, "Fast floor, short ceiling (effective L0=8)"),
        (2, 30, "Fast floor, default ceiling (effective L0=16)"),
        (2, 60, "Fast floor, long ceiling (effective L0=31)"),
        (5, 15, "Default floor, short ceiling (effective L0=10)"),
        (5, 30, "Default floor, default ceiling (effective L0=17)"),
        (5, 60, "Default floor, long ceiling (effective L0=32)"),
        (10, 15, "Slow floor, short ceiling (effective L0=12)"),
        (10, 30, "Slow floor, default ceiling (effective L0=20)"),
        (10, 60, "Slow floor, long ceiling (effective L0=35)"),
    ]

    # Generate reference outputs
    output_lines = []
    for lo, hi, desc in test_cases:
        result = jarsx(prices, lo_len=lo, hi_len=hi)

        arr_name = f"EXPECTED_LO_{lo}_HI_{hi}"

        values = []
        for v in result:
            if np.isnan(v):
                values.append("math.nan")
            else:
                values.append(f"{v:.6f}")

        output_lines.append(f"# {desc}")
        output_lines.append(f"# lo_len={lo}, hi_len={hi}")
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

    # Rebuild with just INPUT_CLOSE + new outputs
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
    for lo, hi, desc in test_cases:
        arr_name = f"EXPECTED_LO_{lo}_HI_{hi}"
        result = jarsx(prices, lo_len=lo, hi_len=hi)
        valid = result[~np.isnan(result)]
        print(f"  {arr_name}: {len(valid)} valid bars, range [{valid.min():.2f}, {valid.max():.2f}]")
