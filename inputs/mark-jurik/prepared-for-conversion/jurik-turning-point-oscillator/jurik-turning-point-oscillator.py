"""
JTPO — Jurik Turning Point Oscillator

Spearman rank correlation between price ranks and time positions over a rolling
window. Output in [-1, +1]: +1 = perfect uptrend, -1 = perfect downtrend.

Reference: Decompiled from WealthScript implementation by Mark Jurik (Starlight).
"""

import math
import numpy as np


def jtpo(prices: np.ndarray, length: int = 14) -> np.ndarray:
    """
    Compute the Jurik Turning Point Oscillator.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values.
    length : int
        Rolling window length (default 14).

    Returns
    -------
    np.ndarray
        JTPO values in [-1, +1]; NaN during warmup.
    """
    n = len(prices)
    out = np.full(n, np.nan)

    if length < 2:
        return out

    f18 = 12.0 / (length * (length - 1) * (length + 1))
    midpoint = (length + 1) / 2.0

    for bar in range(length - 1, n):
        window = prices[bar - length + 1: bar + 1]

        # Skip constant windows (rank correlation undefined)
        if np.all(window == window[0]):
            continue

        # Sort ascending, track original time positions (1-based)
        arr2 = np.arange(1, length + 1, dtype=np.float64)
        sorted_indices = np.argsort(window, kind="mergesort")
        sorted_prices = window[sorted_indices]
        arr2 = arr2[sorted_indices]

        # Assign price ranks with tied-rank averaging
        arr3 = np.empty(length, dtype=np.float64)
        i = 0
        while i < length:
            j = i
            while j < length - 1 and sorted_prices[j + 1] == sorted_prices[j]:
                j += 1
            avg_rank = (i + 1 + j + 1) / 2.0
            arr3[i: j + 1] = avg_rank
            i = j + 1

        # Spearman correlation
        correlation_sum = np.sum((arr3 - midpoint) * (arr2 - midpoint))
        out[bar] = f18 * correlation_sum

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

    # 3x3 grid: length in {7, 14, 28} (short, default, long)
    # Only one parameter, so use 9 values spanning the range
    test_cases = [
        (5, "EXPECTED_LEN_5"),
        (7, "EXPECTED_LEN_7"),
        (10, "EXPECTED_LEN_10"),
        (14, "EXPECTED_LEN_14"),
        (20, "EXPECTED_LEN_20"),
        (28, "EXPECTED_LEN_28"),
        (40, "EXPECTED_LEN_40"),
        (60, "EXPECTED_LEN_60"),
        (80, "EXPECTED_LEN_80"),
    ]

    # Generate reference outputs
    output_lines = []
    for length, arr_name in test_cases:
        result = jtpo(prices, length=length)

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
        result = jtpo(prices, length=length)
        valid = result[~np.isnan(result)]
        print(f"  {arr_name}: {len(valid)} valid bars, range [{valid.min():.4f}, {valid.max():.4f}]")
