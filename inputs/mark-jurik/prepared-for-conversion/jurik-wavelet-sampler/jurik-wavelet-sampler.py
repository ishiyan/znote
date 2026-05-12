"""
WAV — Jurik Wavelet Sampler

Multi-resolution historical data sampler. Applies centered SMA filters at
geometrically-spaced lookback distances to compress a time series into a small
number of representative columns for forecasting.

Reverse-engineered from authentic DLL output (test_WAV.xlsx, Excel 97).
Only Standard Mode (Mode 1) is implemented.

Reference: Jurik Research (1994-2002), WAV 2.0 User's Guide.
"""

import math
import numpy as np


# The n-M table: (n, M) pairs for each scale
# n = lookback distance, M = additional filter points (filter width = M+1)
NM_TABLE = [
    (1, 0),
    (2, 0),
    (3, 0),
    (4, 0),
    (5, 0),
    (7, 2),
    (10, 2),
    (14, 4),
    (19, 4),
    (26, 8),
    (35, 8),
    (48, 16),
    (65, 16),
    (90, 32),
    (123, 32),
    (172, 64),
    (237, 64),
    (334, 128),
]


def wav(prices: np.ndarray, index: int = 12) -> np.ndarray:
    """
    Compute WAV Standard Mode (Mode 1) — multi-resolution wavelet sampler.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values.
    index : int
        Number of output columns (1–18). Selects first `index` rows from n-M table.

    Returns
    -------
    np.ndarray
        2-D array of shape (len(prices), index). NaN in dead zones.
    """
    n_bars = len(prices)
    index = max(1, min(18, index))

    output = np.full((n_bars, index), np.nan)

    for col in range(index):
        n, M = NM_TABLE[col]
        dead_zone = n + M // 2
        half_M = M // 2

        for i in range(dead_zone, n_bars):
            if M == 0:
                output[i, col] = prices[i - n]
            else:
                # Centered SMA of (M+1) points at lag n
                start = i - n - half_M
                end = i - n + half_M + 1  # exclusive
                output[i, col] = np.mean(prices[start:end])

    return output


def wav_cols(index: int, mode: int = 1) -> int:
    """Return the number of output columns for given INDEX and MODE."""
    if mode == 1:
        return index
    else:
        return index + 1


if __name__ == "__main__":
    import csv
    from pathlib import Path

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

    # Validate against authentic DLL output
    csv_path = Path(__file__).parent.parent.parent / "jrs-dll-distribution" / "reference-test-data-output" / "test_WAV.csv"

    if csv_path.exists():
        print("Validating against authentic DLL output (test_WAV.csv)...")
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)  # includes row with "n=X, M=Y" text in non-price cols

        # Parse reference data (text values like "n=1, M=0" become NaN)
        ref = np.full((len(rows), len(header)), np.nan)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                if val and not val.startswith("n="):
                    try:
                        ref[i, j] = float(val)
                    except:
                        pass

        # CSV columns: Close, Close_1, Close_2, ..., Close_5, Close_7, Close_10, Close_14,
        #              Close_19, Close_26, Close_35, Close_48, Close_65, Close_90, Close_172
        # = 15 output columns. Maps to NM_TABLE indices:
        #   0,1,2,3,4,5,6,7,8,9,10,11,12,13,15 (skips index 14 = n=123)
        csv_to_wav = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]

        result = wav(prices, index=16)

        errors = 0
        checks = 0
        for csv_col_idx, wav_col_idx in enumerate(csv_to_wav):
            ref_col = csv_col_idx + 1  # +1 to skip input Close column
            if ref_col >= ref.shape[1]:
                break
            for i in range(min(len(rows), result.shape[0])):
                ref_val = ref[i, ref_col]
                if np.isnan(ref_val):
                    continue
                our_val = result[i, wav_col_idx]
                if np.isnan(our_val) or abs(ref_val - our_val) > 1e-6:
                    if errors < 5:
                        print(f"  MISMATCH row={i}, col={wav_col_idx}(n={NM_TABLE[wav_col_idx][0]}): ref={ref_val}, ours={our_val}")
                    errors += 1
                checks += 1

        print(f"  Checked {checks} values, {errors} mismatches")
        if errors == 0:
            print("  ALL VALUES MATCH authentic DLL output!")
    else:
        print(f"CSV not found at {csv_path}, skipping validation")

    print()

    # Generate test_data.py with various INDEX values
    test_cases = [
        (6, "EXPECTED_INDEX_6"),
        (8, "EXPECTED_INDEX_8"),
        (10, "EXPECTED_INDEX_10"),
        (12, "EXPECTED_INDEX_12"),
        (14, "EXPECTED_INDEX_14"),
        (16, "EXPECTED_INDEX_16"),
    ]

    output_lines = []
    for idx, arr_name in test_cases:
        result = wav(prices, index=idx)

        output_lines.append(f"# index={idx}, columns={idx}")
        output_lines.append(f"# Columns correspond to n-M table rows 1..{idx}:")
        scales_desc = ", ".join(f"(n={NM_TABLE[c][0]},M={NM_TABLE[c][1]})" for c in range(idx))
        output_lines.append(f"#   {scales_desc}")
        output_lines.append(f"{arr_name} = [")

        for i in range(len(prices)):
            row_vals = []
            for c in range(idx):
                v = result[i, c]
                if np.isnan(v):
                    row_vals.append("math.nan")
                else:
                    row_vals.append(f"{v:.6f}")
            line = "    [" + ", ".join(row_vals) + "],"
            output_lines.append(line)

        output_lines.append("]")
        output_lines.append("")

    # Write test_data.py
    test_data_path = Path(__file__).parent / "test_data.py"

    with open(test_data_path, "w") as f:
        f.write("import math\n\n")
        f.write("INPUT_CLOSE = [\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i + 10]
            line = "    " + ", ".join(f"{v:.6f}" for v in chunk) + ","
            f.write(line + "\n")
        f.write("]\n\n")
        f.write("# n-M table used by WAV\n")
        f.write("NM_TABLE = [\n")
        for n, M in NM_TABLE:
            f.write(f"    ({n}, {M}),\n")
        f.write("]\n\n")
        f.write("\n".join(output_lines))
        f.write("\n")

    print(f"Generated {len(test_cases)} reference outputs in test_data.py")
    for idx, arr_name in test_cases:
        result = wav(prices, index=idx)
        # Count valid cells
        valid = np.sum(~np.isnan(result))
        print(f"  {arr_name}: index={idx}, {valid} valid cells across {idx} columns")
