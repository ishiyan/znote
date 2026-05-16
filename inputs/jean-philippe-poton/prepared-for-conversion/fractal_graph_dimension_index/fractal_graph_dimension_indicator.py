"""
Fractal Graph Dimension Indicator (FGDI)
Mnemonic: fgdi

Corrected and enhanced fractal dimension with standard deviation bands.
This is Poton's rework of iliko's original FDI. It corrects the loop bound
and denominator, and adds a representation of the standard deviation of the
dimension estimate.

Key corrections from the original FDI:
    1. Loop boundary: uses iteration <= period-1 (inclusive), yielding
       period-1 path segments (vs period-2 in the original)
    2. Denominator: uses ln(2*(period-1)) instead of ln(2*period)

The standard deviation is NOT a rolling stddev of FDI values over time.
It is the dispersion of individual path segment lengths within one window,
propagated through the dimension formula. This measures how "uniform" the
price path is: a perfectly straight trend has zero segment variance.

Author: Jean-Philippe Poton (jppoton@yahoo.com)
Reference MQ4: fractal_graph_dimension_indicator.mq4
Source: https://www.mql5.com/en/code/8844
Blog: http://fractalfinance.blogspot.com/2009/04/fractal-dimensionsand-fractal-graph.html

Parameters:
    close : list[float]
        1D array of close prices. Index 0 = oldest.
    period : int, default 30
        Lookback period N. Valid range: >= 2.
        The algorithm uses a window of N prices (N-1 path segments).

Output:
    FGDIResult named tuple with four list[float] fields:
        fdi         - fractal graph dimension values
        upper_band  - fdi + stddev
        lower_band  - fdi - stddev
        stddev      - standard deviation of the dimension estimate

    First `period - 1` values are NaN (insufficient data).

Algorithm:
    For each bar at position `pos` (where pos >= period - 1):
    1. Extract window of N prices: [pos - period + 1, pos] inclusive
    2. Normalize prices to [0, 1] using min/max of the window
    3. Compute path segments:
       delta_i = sqrt((norm[i] - norm[i-1])^2 + 1/N^2) for i=1..N-1
    4. Path length: L = sum(delta_i)
    5. Fractal dimension:
       FDI = 1 + (ln(L) + ln(2)) / ln(2*(N-1))
    6. Segment variance (propagated through the formula):
       mean_delta = L / (N-1)
       variance = sum((delta_i - mean_delta)^2) / (L^2 * ln(2*(N-1))^2)
       stddev = sqrt(variance)
    7. Bands: upper = fdi + stddev, lower = fdi - stddev
"""

import math
from typing import NamedTuple


class FGDIResult(NamedTuple):
    """Result of FGDI computation.

    Conversion agents should map this to a Band-style struct/tuple:
        fdi        -> the primary indicator line
        upper_band -> upper confidence band
        lower_band -> lower confidence band
        stddev     -> band width (standard deviation of dimension estimate)
    """
    fdi: list[float]
    upper_band: list[float]
    lower_band: list[float]
    stddev: list[float]


def fractal_graph_dimension_indicator(
    close: list[float],
    period: int = 30,
) -> FGDIResult:
    """
    Compute the Fractal Graph Dimension Indicator with confidence bands.

    Uses Poton's corrected FDI formula (period-1 segments, ln(2*(period-1))
    denominator) and computes the standard deviation of the dimension estimate
    from the dispersion of individual path segment lengths.

    Parameters
    ----------
    close : list[float]
        1D array of close prices. Index 0 = oldest bar.
    period : int
        Lookback period N (>= 2, default 30). Window is N prices,
        yielding N-1 path segments.

    Returns
    -------
    FGDIResult
        Named tuple with (fdi, upper_band, lower_band, stddev).
        First `period - 1` values are NaN.
    """
    if period < 2:
        raise ValueError("period must be >= 2")

    n = len(close)
    fdi_out = [math.nan] * n
    upper_out = [math.nan] * n
    lower_out = [math.nan] * n
    stddev_out = [math.nan] * n

    period_m1 = period - 1
    log_denom = math.log(2.0 * period_m1)  # ln(2*(N-1))
    ln2 = math.log(2.0)
    inv_n_sq = 1.0 / (period * period)  # horizontal step squared: (1/N)^2

    for pos in range(period_m1, n):
        # --- Extract window of N prices ending at pos ---
        window_start = pos - period_m1

        # Find min/max for normalization
        price_max = close[window_start]
        price_min = close[window_start]
        for k in range(window_start + 1, pos + 1):
            if close[k] > price_max:
                price_max = close[k]
            if close[k] < price_min:
                price_min = close[k]

        price_range = price_max - price_min

        if price_range < 1e-10:
            fdi_out[pos] = 1.0
            upper_out[pos] = 1.0
            lower_out[pos] = 1.0
            stddev_out[pos] = 0.0
            continue

        # --- Compute path segments and length ---
        # First pass: compute segments and total length
        segments = [0.0] * period_m1
        prior_norm = (close[window_start] - price_min) / price_range
        length = 0.0

        for i in range(period_m1):
            curr_norm = (close[window_start + i + 1] - price_min) / price_range
            diff = curr_norm - prior_norm
            seg = math.sqrt(diff * diff + inv_n_sq)
            segments[i] = seg
            length += seg
            prior_norm = curr_norm

        if length <= 0.0:
            fdi_out[pos] = 0.0
            upper_out[pos] = 0.0
            lower_out[pos] = 0.0
            stddev_out[pos] = 0.0
            continue

        # --- Fractal dimension ---
        fdi_val = 1.0 + (math.log(length) + ln2) / log_denom

        # --- Standard deviation of the estimate ---
        # Variance of segment lengths propagated through the formula
        mean_delta = length / period_m1
        variance_sum = 0.0
        for i in range(period_m1):
            d = segments[i] - mean_delta
            variance_sum += d * d

        variance = variance_sum / (length * length * log_denom * log_denom)
        sd = math.sqrt(variance)

        fdi_out[pos] = fdi_val
        upper_out[pos] = fdi_val + sd
        lower_out[pos] = fdi_val - sd
        stddev_out[pos] = sd

    return FGDIResult(fdi=fdi_out, upper_band=upper_out,
                      lower_band=lower_out, stddev=stddev_out)


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

    # --- Parameter combinations ---
    # Only parameter is `period` (bands are always ± 1 stddev per MQ4)
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
        output = fractal_graph_dimension_indicator(INPUT_CLOSE, period=p)
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

        # Write expected outputs (4 arrays per combo)
        for (p, output) in results:
            for field_name, field_data, desc in [
                ("FDI", output.fdi, "FDI output"),
                ("UPPER", output.upper_band, "upper band (fdi + stddev)"),
                ("LOWER", output.lower_band, "lower band (fdi - stddev)"),
                ("STDDEV", output.stddev, "stddev of dimension estimate"),
            ]:
                f.write(f"# FGDI - {desc} (period={p})\n")
                f.write(f"# fractal_graph_dimension_indicator(INPUT_CLOSE, period={p}).{field_name.lower()}\n")
                f.write(f"EXPECTED_{field_name}_P{p}: list[float] = [\n")
                for i in range(0, len(field_data), 6):
                    chunk = field_data[i:i+6]
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
        f.write("package fractalgeneralizeddimensionindex\n\n")
        f.write("import \"math\"\n\n")

        f.write("var testInput = []float64{\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = ", ".join(f"{v:.6f}" for v in chunk)
            f.write(f"\t{line},\n")
        f.write("}\n\n")

        for (p, output) in results:
            for field_name, field_data, desc in [
                ("Fdi", output.fdi, "FDI output"),
                ("Upper", output.upper_band, "upper band (fdi + stddev)"),
                ("Lower", output.lower_band, "lower band (fdi - stddev)"),
                ("Stddev", output.stddev, "stddev of dimension estimate"),
            ]:
                f.write(f"// FGDI - {desc} (period={p})\n")
                f.write(f"// fractal_graph_dimension_indicator(INPUT_CLOSE, period={p}).{field_name.lower()}\n")
                f.write(f"var expected{field_name}P{p} = []float64{{\n")
                for i in range(0, len(field_data), 6):
                    chunk = field_data[i:i+6]
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
            for field_name, field_data, desc in [
                ("Fdi", output.fdi, "FDI output"),
                ("Upper", output.upper_band, "upper band (fdi + stddev)"),
                ("Lower", output.lower_band, "lower band (fdi - stddev)"),
                ("Stddev", output.stddev, "stddev of dimension estimate"),
            ]:
                f.write(f"// FGDI - {desc} (period={p})\n")
                f.write(f"// fractal_graph_dimension_indicator(INPUT_CLOSE, period={p}).{field_name.lower()}\n")
                f.write(f"export const expected{field_name}P{p}: number[] = [\n")
                for i in range(0, len(field_data), 6):
                    chunk = field_data[i:i+6]
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
            for field_name, field_data, desc in [
                ("fdi", output.fdi, "FDI output"),
                ("upper", output.upper_band, "upper band (fdi + stddev)"),
                ("lower", output.lower_band, "lower band (fdi - stddev)"),
                ("stddev", output.stddev, "stddev of dimension estimate"),
            ]:
                f.write(f"    // FGDI - {desc} (period={p})\n")
                f.write(f"    // fractal_graph_dimension_indicator(INPUT_CLOSE, period={p}).{field_name}\n")
                f.write(f"    pub fn expected_{field_name}_p{p}() -> Vec<f64> {{\n")
                f.write(f"        vec![\n")
                for i in range(0, len(field_data), 6):
                    chunk = field_data[i:i+6]
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
            for field_name, field_data, desc in [
                ("Fdi", output.fdi, "FDI output"),
                ("Upper", output.upper_band, "upper band (fdi + stddev)"),
                ("Lower", output.lower_band, "lower band (fdi - stddev)"),
                ("Stddev", output.stddev, "stddev of dimension estimate"),
            ]:
                f.write(f"// FGDI - {desc} (period={p})\n")
                f.write(f"// fractal_graph_dimension_indicator(INPUT_CLOSE, period={p}).{field_name.lower()}\n")
                f.write(f"pub fn expected{field_name}P{p}() [252]f64 {{\n")
                f.write(f"    return .{{\n")
                for i in range(0, len(field_data), 6):
                    chunk = field_data[i:i+6]
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

    print(f"Generated {len(results)} parameter combos x 4 outputs = {len(results)*4} arrays")
    print("Parameter combinations:")
    for (p, output) in results:
        valid_fdi = sum(1 for v in output.fdi if not math.isnan(v))
        f_val = next((v for v in output.fdi if not math.isnan(v)), None)
        l_val = next((v for v in reversed(output.fdi) if not math.isnan(v)), None)
        print(f"  period={p:3d}: {valid_fdi} valid FDI values, first={f_val:.15f}, last={l_val:.15f}")
