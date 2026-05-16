"""
Fractal Dimension Index (FDI)
Mnemonic: fdi

Measures the fractal dimension of a price time series using normalized
path length (box-counting / graph-length method). The indicator quantifies
the "roughness" of the price curve, providing a volatility measure that is
independent of price direction.

Interpretation:
    Df = 1.5 → completely random market (Brownian motion)
    Df → 1.0 → smooth, trending market (low volatility)
    Df → 2.0 → highly volatile, space-filling curve (erratic)

Original author: iliko (arcsin5@netscape.net), v1.0 February 2007
Reference: https://www.mql5.com/en/code/7758

Parameters:
    prices : list[float]
        1D array of prices (e.g., close prices). Index 0 = oldest.
    period : int, default 30
        Lookback period N. Valid range: >= 2.
        The algorithm uses N bars (N segments) to compute path length.
Output:
    list[float] of length len(prices).
    First `period` values are NaN (insufficient data for computation).
    Subsequent values are the fractal dimension estimate for that bar.

Algorithm:
    For each bar at position `pos` (where pos >= period):
    1. Extract window of (period + 1) prices: [pos - period, pos] inclusive
    2. Normalize prices to [0, 1] using min/max of the window
    3. Compute path length:
       L = sum_{i=1}^{period} sqrt((norm[i] - norm[i-1])^2 + 1/period^2)
    4. Compute fractal dimension:
       FDI = 1 + (ln(L) + ln(2)) / ln(2 * period)

Note on MQ4 original vs this implementation:
    The original MQ4 by iliko iterates `period - 2` segments (loop from 0 to
    period-2, skipping iteration 0 for length). This implementation uses
    `period` segments from a window of `period + 1` points, which is the
    mathematically correct formulation per the FDI literature. The corrected
    version by Poton (FGDI) uses `period - 1` segments with denominator
    ln(2*(period-1)). This file implements the ORIGINAL iliko formula with
    the corrected loop bound (period segments, denominator ln(2*period)).
"""

import math


def fractal_dimension(
    prices: list,
    period: int = 30,
) -> list:
    """
    Compute the Fractal Dimension Index for each bar.

    Parameters
    ----------
    prices : list[float]
        1D array of prices (e.g., close prices). Index 0 = oldest.
    period : int
        Lookback period N (>= 2).

    Returns
    -------
    list[float]
        FDI values. First `period` values are NaN (insufficient data).
    """
    # --- Validate parameters ---
    if period < 2:
        raise ValueError("period must be >= 2")

    n = len(prices)
    fdi = [math.nan] * n

    # Precompute constants
    log_2n = math.log(2.0 * period)  # denominator: ln(2N)
    ln2 = math.log(2.0)              # numerator offset: ln(2)
    inv_n_sq = 1.0 / (period * period)  # horizontal step squared: (1/N)^2

    for pos in range(period, n):
        # --- Step 1: Extract window of (period + 1) prices ---
        # Window covers indices [pos - period, pos] inclusive
        window_start = pos - period
        window_end = pos + 1  # exclusive for slicing

        # --- Step 2: Find min/max for normalization ---
        price_max = prices[window_start]
        price_min = prices[window_start]
        for k in range(window_start + 1, window_end):
            if prices[k] > price_max:
                price_max = prices[k]
            if prices[k] < price_min:
                price_min = prices[k]

        price_range = price_max - price_min

        if price_range < 1e-10:
            # Flat price: dimension is 1.0 (straight line)
            fdi[pos] = 1.0
            continue

        # --- Step 3: Normalize to [0, 1] and compute path length ---
        # First normalized value
        prior_norm = (prices[window_start] - price_min) / price_range
        length = 0.0

        for k in range(window_start + 1, window_end):
            curr_norm = (prices[k] - price_min) / price_range
            diff = curr_norm - prior_norm
            # Path segment: sqrt(dy^2 + dx^2) where dx = 1/N
            length += math.sqrt(diff * diff + inv_n_sq)
            prior_norm = curr_norm

        # --- Step 4: Compute fractal dimension ---
        # FDI = 1 + (ln(L) + ln(2)) / ln(2N)
        fdi[pos] = 1.0 + (math.log(length) + ln2) / log_2n

    return fdi


if __name__ == "__main__":
    import sys

    # 252 INPUT_CLOSE values from test_testdata.py
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

    # --- Parameter combinations for reference output generation ---
    # We vary only `period` since `random_line` does not affect FDI values.
    test_params = [
        {"period": 5},
        {"period": 10},
        {"period": 15},
        {"period": 20},
        {"period": 30},
        {"period": 50},
        {"period": 80},
        {"period": 120},
    ]

    # --- Generate reference outputs ---
    results = []
    for params in test_params:
        p = params["period"]
        output = fractal_dimension(INPUT_CLOSE, period=p)
        results.append((p, output))

    # --- Write to test_testdata.py ---
    with open("test_testdata.py", "w") as f:
        f.write("import math\n\n")

        # Write INPUT_CLOSE
        f.write("INPUT_CLOSE = [\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = ", ".join(f"{v:.6f}" for v in chunk)
            f.write(f"    {line},\n")
        f.write("]\n\n")

        # Write expected outputs
        for (p, output) in results:
            f.write(f"# FDI with period={p}: tests fractal dimension computation with lookback {p}\n")
            f.write(f"# period={p}\n")
            f.write(f"EXPECTED_P{p} = [\n")
            for i in range(0, len(output), 6):
                chunk = output[i:i+6]
                formatted = []
                for v in chunk:
                    if math.isnan(v):
                        formatted.append("math.nan")
                    else:
                        formatted.append(f"{v:.15f}")
                line = ", ".join(formatted)
                f.write(f"    {line},\n")
            f.write("]\n\n")

    print(f"Generated {len(results)} reference outputs to test_testdata.py")
    print("Parameter combinations:")
    for (p, output) in results:
        # Count non-NaN values
        valid = sum(1 for v in output if not math.isnan(v))
        f_val = next((v for v in output if not math.isnan(v)), None)
        l_val = next((v for v in reversed(output) if not math.isnan(v)), None)
        print(f"  period={p:3d}: {valid} valid values, first={f_val:.6f}, last={l_val:.6f}")
