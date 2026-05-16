"""
Fractal Adaptive Simple Moving Average v2 (FRASMAv2)
Mnemonic: frasma2

Computes an adaptive simple moving average whose window length is derived from
the Fractal Dimension Index (FDI) using the CORRECTED formula.  When the market
is trending (low FDI / high Hurst), the adaptive speed increases and the
average tracks price closely.  When the market is erratic (high FDI / low
Hurst), the speed decreases and the average smooths more aggressively.

Unlike FRASMA v1, this version uses the corrected FDI formula:
    - Denominator: ln(2*(N-1)) instead of ln(2*N)
    - N-1 path segments (loop iterates i=1..N-1 inclusive)
    - Horizontal step squared: 1/N^2

The adaptive alpha is:
    trail_dim = 1 / (2 - fdi)
    alpha     = trail_dim / 2
    speed     = round(normal_speed * alpha), clamped to >= 1

The output is: SMA(close, speed) at each bar.

Parameters:
    close : list[float]
        1D array of close prices. Index 0 = oldest.
    period : int, default 30
        Lookback period for FDI computation. Valid range: >= 2.

Output:
    list[float] of length len(close).
    First `period` values are NaN (insufficient data for FDI).
    Starting at index `period`, the adaptive SMA is computed.

Author: Jean-Philippe Poton (jppoton@yahoo.com), Copyright 2008
Source: https://www.mql5.com/en/code/8866
"""

import math


def fractal_adaptive_simple_moving_average_2(
    close: list[float],
    period: int = 30,
) -> list[float]:
    """
    Compute the Fractal Adaptive Simple Moving Average v2 (FRASMAv2).

    Uses the corrected FDI formula with ln(2*(period-1)) denominator and
    period-1 path segments.  The adaptive speed is derived from the fractal
    dimension via trail_dim = 1/(2 - FDI), alpha = trail_dim/2, and
    speed = round(20 * alpha).

    Parameters
    ----------
    close : list[float]
        1D array of close prices.  Index 0 = oldest bar.
    period : int
        Lookback period N for FDI computation (>= 2, default 30).

    Returns
    -------
    list[float]
        FRASMAv2 values.  First ``period`` values are NaN.
    """
    if period < 2:
        raise ValueError("period must be >= 2")

    n = len(close)
    result = [math.nan] * n

    normal_speed = 20
    ln2 = math.log(2.0)
    log_2pm1 = math.log(2.0 * (period - 1))
    inv_n_sq = 1.0 / (period * period)

    for pos in range(period, n):
        # --- Extract window of `period` prices ending at `pos` ---
        w_start = pos - period + 1
        # Find min/max
        price_max = close[w_start]
        price_min = close[w_start]
        for k in range(w_start + 1, pos + 1):
            if close[k] > price_max:
                price_max = close[k]
            if close[k] < price_min:
                price_min = close[k]

        price_range = price_max - price_min

        if price_range <= 0.0:
            # Flat window -> FDI undefined, skip
            continue

        # --- Compute FDI (corrected formula, N-1 segments) ---
        length = 0.0
        prior_diff = (close[w_start] - price_min) / price_range
        for i in range(1, period):
            diff = (close[w_start + i] - price_min) / price_range
            delta = diff - prior_diff
            length += math.sqrt(delta * delta + inv_n_sq)
            prior_diff = diff

        if length <= 0.0:
            continue

        fdi = 1.0 + (math.log(length) + ln2) / log_2pm1

        # --- Adaptive speed ---
        denom = 2.0 - fdi
        if abs(denom) < 1e-10:
            continue
        trail_dim = 1.0 / denom
        alpha = trail_dim / 2.0
        speed = max(1, int(round(normal_speed * alpha)))

        # --- SMA of length `speed` ending at `pos` ---
        if pos - speed + 1 < 0:
            continue

        sma_sum = 0.0
        for k in range(pos - speed + 1, pos + 1):
            sma_sum += close[k]
        result[pos] = sma_sum / speed

    return result


if __name__ == "__main__":
    import sys

    # 252 INPUT_CLOSE values
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

    # --- Parameter combinations ---
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
        output = fractal_adaptive_simple_moving_average_2(INPUT_CLOSE, period=p)
        results.append((p, output))

    # --- Write to test_testdata.py ---
    with open("test_testdata.py", "w") as f:
        f.write("import math\n\n")

        # Write INPUT_CLOSE
        f.write("INPUT_CLOSE: list[float] = [\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = ", ".join(f"{v:.6f}" for v in chunk)
            f.write(f"    {line},\n")
        f.write("]\n\n")

        # Write expected outputs
        for (p, output) in results:
            f.write(f"# Fractal Adaptive Simple Moving Average 2 (period={p})\n")
            f.write(f"# fractal_adaptive_simple_moving_average_2(INPUT_CLOSE, period={p})\n")
            f.write(f"EXPECTED_P{p}: list[float] = [\n")
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

    # --- Write to testdata_test.go ---
    with open("testdata_test.go", "w") as f:
        f.write("//nolint:testpackage\n")
        f.write("package fractaladaptivesimplemovingaverage2\n\n")
        f.write("import \"math\"\n\n")

        # testInput
        f.write("var testInput = []float64{\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = ", ".join(f"{v:.6f}" for v in chunk)
            f.write(f"\t{line},\n")
        f.write("}\n\n")

        for (p, output) in results:
            f.write(f"// Fractal Adaptive Simple Moving Average 2 (period={p})\n")
            f.write(f"// fractal_adaptive_simple_moving_average_2(INPUT_CLOSE, period={p})\n")
            f.write(f"var expectedP{p} = []float64{{\n")
            for i in range(0, len(output), 6):
                chunk = output[i:i+6]
                formatted = []
                for v in chunk:
                    if math.isnan(v):
                        formatted.append("math.NaN()")
                    else:
                        formatted.append(f"{v:.15f}")
                line = ", ".join(formatted)
                f.write(f"\t{line},\n")
            f.write("}\n\n")

    # --- Write to testdata.ts ---
    with open("testdata.ts", "w") as f:
        f.write("export const testInput: number[] = [\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = ", ".join(f"{v:.6f}" for v in chunk)
            f.write(f"    {line},\n")
        f.write("];\n\n")

        for (p, output) in results:
            f.write(f"// Fractal Adaptive Simple Moving Average 2 (period={p})\n")
            f.write(f"// fractal_adaptive_simple_moving_average_2(INPUT_CLOSE, period={p})\n")
            f.write(f"export const expectedP{p}: number[] = [\n")
            for i in range(0, len(output), 6):
                chunk = output[i:i+6]
                formatted = []
                for v in chunk:
                    if math.isnan(v):
                        formatted.append("NaN")
                    else:
                        formatted.append(f"{v:.15f}")
                line = ", ".join(formatted)
                f.write(f"    {line},\n")
            f.write("];\n\n")

    # --- Write to testdata.rs ---
    with open("testdata.rs", "w") as f:
        f.write("#[cfg(test)]\n")
        f.write("pub mod testdata {\n")

        f.write("    pub fn test_input() -> Vec<f64> {\n")
        f.write("        vec![\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = ", ".join(f"{v:.6f}" for v in chunk)
            f.write(f"            {line},\n")
        f.write("        ]\n")
        f.write("    }\n\n")

        for (p, output) in results:
            f.write(f"    // Fractal Adaptive Simple Moving Average 2 (period={p})\n")
            f.write(f"    // fractal_adaptive_simple_moving_average_2(INPUT_CLOSE, period={p})\n")
            f.write(f"    pub fn expected_p{p}() -> Vec<f64> {{\n")
            f.write(f"        vec![\n")
            for i in range(0, len(output), 6):
                chunk = output[i:i+6]
                formatted = []
                for v in chunk:
                    if math.isnan(v):
                        formatted.append("f64::NAN")
                    else:
                        formatted.append(f"{v:.15f}")
                line = ", ".join(formatted)
                f.write(f"            {line},\n")
            f.write("        ]\n")
            f.write("    }\n\n")

        f.write("}\n")

    # --- Write to testdata.zig ---
    with open("testdata.zig", "w") as f:
        f.write("const std = @import(\"std\");\n")
        f.write("const math = std.math;\n")
        f.write("const nan = math.nan(f64);\n\n")

        f.write("pub fn testInput() [252]f64 {\n")
        f.write("    return .{\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = ", ".join(f"{v:.6f}" for v in chunk)
            f.write(f"        {line},\n")
        f.write("    };\n")
        f.write("}\n\n")

        for (p, output) in results:
            f.write(f"// Fractal Adaptive Simple Moving Average 2 (period={p})\n")
            f.write(f"// fractal_adaptive_simple_moving_average_2(INPUT_CLOSE, period={p})\n")
            f.write(f"pub fn expectedP{p}() [252]f64 {{\n")
            f.write(f"    return .{{\n")
            for i in range(0, len(output), 6):
                chunk = output[i:i+6]
                formatted = []
                for v in chunk:
                    if math.isnan(v):
                        formatted.append("nan")
                    else:
                        formatted.append(f"{v:.15f}")
                line = ", ".join(formatted)
                f.write(f"        {line},\n")
            f.write("    };\n")
            f.write("}\n\n")

    print(f"Generated {len(results)} reference outputs to all test data files")
    print("Parameter combinations:")
    for (p, output) in results:
        valid = sum(1 for v in output if not math.isnan(v))
        f_val = next((v for v in output if not math.isnan(v)), None)
        l_val = next((v for v in reversed(output) if not math.isnan(v)), None)
        print(f"  period={p:3d}: {valid} valid values, first={f_val:.15f}, last={l_val:.15f}")
