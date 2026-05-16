"""
Hurst Difference
Mnemonic: hurdif

Computes the first difference of the Fractal Dimension Index (FDI) over time.
Positive values indicate rising volatility (potential trade entry); negative
values indicate declining volatility.

The FDI is computed using the corrected FGDI formula with (period-1) segments
and denominator ln(2*(period-1)).

Author: Jean-Philippe Poton
Source: https://www.mql5.com/en/code/9676
Blog:   http://fractalfinance.blogspot.com/2010/05/variation-of-hurst-exponent.html

Parameters:
    prices : list[float]
        1D array of prices (e.g., close prices). Index 0 = oldest.
    period : int, default 30
        Lookback period N for FDI computation. Valid range: >= 2.

Output:
    tuple of two list[float], each of length len(prices):
        hurst_diff : First difference of FDI (fdi[pos] - fdi[pos-1]).
            First (period + 1) values are NaN.
        fdi : Raw FDI values from the corrected FGDI formula.
            First `period` values are NaN.
"""

import math


def hurst_difference(
    prices: list,
    period: int = 30,
) -> tuple:
    """
    Compute the Hurst Difference (first difference of corrected FDI).

    Parameters
    ----------
    prices : list[float]
        1D array of prices (e.g., close prices). Index 0 = oldest.
    period : int
        Lookback period N for FDI computation (>= 2). Default: 30.

    Returns
    -------
    (hurst_diff, fdi) : tuple[list[float], list[float]]
        hurst_diff : First difference of FDI. Positive = increasing volatility.
            First (period + 1) values are NaN.
        fdi : Raw FDI values (corrected FGDI formula).
            First `period` values are NaN.
    """
    if period < 2:
        raise ValueError("period must be >= 2")

    n = len(prices)
    nan = math.nan
    fdi = [nan] * n
    hurst_diff = [nan] * n

    ln2 = math.log(2.0)
    log_2pm1 = math.log(2.0 * (period - 1))
    inv_n_sq = 1.0 / (period * period)

    # Step 1: Compute FDI using corrected FGDI formula
    for pos in range(period, n):
        # Window of `period` elements: [pos - period + 1, pos] inclusive
        w_start = pos - period + 1
        w_end = pos + 1

        price_max = prices[w_start]
        price_min = prices[w_start]
        for k in range(w_start + 1, w_end):
            if prices[k] > price_max:
                price_max = prices[k]
            if prices[k] < price_min:
                price_min = prices[k]

        price_range = price_max - price_min

        if price_range <= 0.0:
            fdi[pos] = 0.0
            continue

        length = 0.0
        prior_diff = (prices[w_start] - price_min) / price_range
        for i in range(w_start + 1, w_end):
            diff = (prices[i] - price_min) / price_range
            delta = diff - prior_diff
            length += math.sqrt(delta * delta + inv_n_sq)
            prior_diff = diff

        if length > 0.0:
            fdi[pos] = 1.0 + (math.log(length) + ln2) / log_2pm1
        else:
            fdi[pos] = 0.0

    # Step 2: First difference
    for pos in range(period + 1, n):
        if math.isnan(fdi[pos]) or math.isnan(fdi[pos - 1]):
            continue
        hurst_diff[pos] = fdi[pos] - fdi[pos - 1]

    return hurst_diff, fdi


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

    # Parameter combinations: vary period only (single parameter)
    # 8 periods covering small, medium, large lookback windows
    # Each produces 2 outputs (hurst_diff, fdi) = 16 total arrays
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

    results = []
    for params in test_params:
        p = params["period"]
        hdiff, fdi = hurst_difference(INPUT_CLOSE, period=p)
        results.append((p, hdiff, fdi))

    # --- Write to test_testdata.py ---
    with open("test_testdata.py", "w") as f:
        f.write("import math\n\n")

        # Write INPUT_CLOSE
        f.write("INPUT_CLOSE = [\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = ", ".join(f"{v:.6f}" for v in chunk)
            f.write(f"    {line},\n")
        f.write("]\n")

        # Write expected outputs
        for (p, hdiff, fdi) in results:
            # FDI output
            f.write(f"\n# FDI output from hurst_difference with period={p}\n")
            f.write(f"# hurst_difference(INPUT_CLOSE, period={p}) -> fdi\n")
            f.write(f"EXPECTED_FDI_P{p}: list[float] = [\n")
            for i in range(0, len(fdi), 6):
                chunk = fdi[i:i+6]
                formatted = []
                for v in chunk:
                    if math.isnan(v):
                        formatted.append("math.nan")
                    else:
                        formatted.append(f"{v:.15f}")
                line = ", ".join(formatted)
                f.write(f"    {line},\n")
            f.write("]\n")

            # Hurst Diff output
            f.write(f"\n# Hurst Difference output with period={p}\n")
            f.write(f"# hurst_difference(INPUT_CLOSE, period={p}) -> hurst_diff\n")
            f.write(f"EXPECTED_HDIFF_P{p}: list[float] = [\n")
            for i in range(0, len(hdiff), 6):
                chunk = hdiff[i:i+6]
                formatted = []
                for v in chunk:
                    if math.isnan(v):
                        formatted.append("math.nan")
                    else:
                        formatted.append(f"{v:.15f}")
                line = ", ".join(formatted)
                f.write(f"    {line},\n")
            f.write("]\n")

    print(f"Generated {len(results)} parameter sets to test_testdata.py")
    for (p, hdiff, fdi) in results:
        valid_fdi = sum(1 for v in fdi if not math.isnan(v))
        valid_hd = sum(1 for v in hdiff if not math.isnan(v))
        print(f"  period={p:3d}: fdi={valid_fdi} valid, hdiff={valid_hd} valid")
