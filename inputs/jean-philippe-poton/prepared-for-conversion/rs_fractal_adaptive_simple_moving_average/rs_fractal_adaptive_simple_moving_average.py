"""
Rescaled Fractal Adaptive Simple Moving Average (RS-FRASMA)
Mnemonic: rsfrasma

Computes an adaptive simple moving average whose period is derived from the
Hurst exponent estimated via Rescaled Range (R/S) analysis. When the market
is trending (H > 0.5), the SMA speeds up (shorter period). When the market
is erratic (H < 0.5), the SMA slows down (longer period).

The R/S analysis partitions a window of `period` prices into blocks at
multiple scales, computes the rescaled range for each block, and performs
log-log linear regression to estimate the Hurst exponent H. The adaptive
speed is then: speed = round(normal_speed / (2*H)).

Author: Jean-Philippe Poton (jppoton@yahoo.com), v1.0 October 2009
Reference: https://www.mql5.com/ru/code/9272
Blog: http://fractalfinance.blogspot.com/2009/10/rescaled-range-analysis.html

Note: The original MQ4 parameter `PIP_Convertor` has been renamed to
`price_scale` with a default of 1.0 for generality.

Parameters:
    close : list[float]
        1D array of close prices. Index 0 = oldest.
    period : int, default 64
        Lookback window for R/S analysis. Must be a power of 2, >= 4.
    normal_speed : int, default 30
        Base SMA period before fractal adaptation (>= 1).
    price_scale : float, default 1.0
        Multiplier applied to prices before R/S calculation. Originally
        named PIP_Convertor (e.g. 10000 for forex). Use 1.0 for prices
        that need no scaling.

Output:
    list[float] of length len(close).
    First `period - 1` values are NaN (insufficient data for R/S analysis).
    Starting at index `period - 1`, the RS-FRASMA is computed. Note: the
    MQ4 original uses `period` as the first valid index (0-based), which
    corresponds to needing `period` bars of history. We follow that
    convention: first valid output is at index `period`.
"""

import math


def rs_fractal_adaptive_simple_moving_average(
    close: list[float],
    period: int = 64,
    normal_speed: int = 30,
    price_scale: float = 1.0,
) -> list[float]:
    """
    Compute the Rescaled Fractal Adaptive Simple Moving Average.

    Uses Rescaled Range (R/S) analysis to estimate the Hurst exponent,
    then adapts the SMA period accordingly.

    Parameters
    ----------
    close : list[float]
        1D array of close prices. Index 0 = oldest.
    period : int
        Lookback window for R/S analysis. Must be a power of 2, >= 4.
    normal_speed : int
        Base SMA period before fractal adaptation (>= 1).
    price_scale : float
        Multiplier to scale prices for R/S calculation (default 1.0).
        Originally named PIP_Convertor in the MQ4 source.

    Returns
    -------
    list[float]
        RS-FRASMA values. First `period` values are NaN.
    """
    if period < 4:
        raise ValueError("period must be >= 4")
    if normal_speed < 1:
        raise ValueError("normal_speed must be >= 1")
    # Verify period is a power of 2
    if period & (period - 1) != 0:
        raise ValueError("period must be a power of 2")

    n = len(close)
    result = [math.nan] * n

    # Precompute R/S parameters (matching MQ4 logic)
    k0 = period // 4
    if k0 < 1:
        n_iter = 0
    else:
        n_iter = int(math.floor(math.log(k0) / math.log(2))) if k0 >= 2 else 0

    # Block sizes and counts for each scale
    d = [0] * (n_iter + 1)
    k_blocks = [0] * (n_iter + 1)
    for u in range(1, n_iter + 1):
        d[u] = int(2 ** (u + 1))
        k_blocks[u] = period // d[u]

    # MQ4 uses reverse indexing: pos counts down from lastBars to 0.
    # inputData[pos+t+j] reads forward from pos. In our forward-indexed
    # array where index 0 = oldest, this maps to: for each bar `pos`
    # (in MQ4 reverse order), the window starts at `pos` and extends
    # forward by `period`. In our forward array, MQ4's `pos` corresponds
    # to our `n - 1 - pos`, so the window is
    #   close[n-1-pos .. n-1-pos+period-1].
    # But since MQ4 iterates pos from lastBars down to 0, and we want
    # to compute for every bar that has enough history, we iterate
    # our_pos from period to n-1, and the MQ4-equivalent window is
    # close[our_pos - period + 1 .. our_pos].
    #
    # HOWEVER: the MQ4 code reads inputData[pos+t+j] where j goes from
    # 1 to d[i], meaning it reads indices pos+t+1 through pos+t+d[i].
    # This means it skips index pos+t+0 (the first element). The window
    # effectively starts at pos+1 and uses `period` values from pos+1
    # to pos+period. In our forward indexing, we need to replicate this.
    #
    # For our_pos mapping: MQ4 pos=0 is the most recent bar = our n-1.
    # MQ4 reads indices 1..period from that bar. In forward indexing,
    # this reads close[n-1-period .. n-2] (the period values before the
    # current bar). But the SMA output uses iMA at pos, which IS the
    # current bar.
    #
    # Actually, re-reading the MQ4 more carefully: the R/S window uses
    # j=1..d[i] with inputData[pos+t+j]. Since MQ4 arrays are
    # reverse-indexed (pos=0 is newest), pos+t+j moves BACKWARD in time.
    # So the window is `period` bars BEFORE and including the current bar.
    #
    # For simplicity and correctness, we replicate the MQ4 R/S exactly:
    # - Window of `period` values: the `period` most recent bars up to
    #   and including `our_pos`, scaled by price_scale.
    # - Within that window, blocks use 1-based indexing (skip index 0).

    for pos in range(period, n):
        # R/S analysis
        # MQ4 window: indices pos+1 to pos+period in reverse array
        # = period bars before current bar (not including current bar)
        # In forward indexing: close[pos-period .. pos-1]
        # But MQ4's j starts at 1, so we use 1-based indexing within window

        # Build scaled window (1-indexed: w[1]..w[period])
        # MQ4: PIP_Convertor * inputData[pos+t+j] where t starts at 0
        # and j goes 1..d[i], so first element accessed is inputData[pos+1]
        # In reverse indexing, pos+1 is one bar older than pos.
        # In forward indexing: close[pos-1], close[pos-2], ...
        # So w[j] = price_scale * close[pos - j] for j=1..period
        # This matches MQ4: inputData[pos+j] = bar j positions before pos

        sumx = 0.0
        sumy = 0.0
        sumx2 = 0.0
        sumxy = 0.0
        valid_scales = 0

        for u in range(1, n_iter + 1):
            block_size = d[u]
            n_blocks_u = k_blocks[u]
            if n_blocks_u < 1:
                continue

            rs_sum = 0.0
            t = 0
            block_count = 0

            while t <= period - block_size:
                # Block: indices t+1 to t+block_size (1-based in window)
                # w[t+j] = price_scale * close[pos - (t+j)]
                # Compute block mean
                mu = 0.0
                for j in range(1, block_size + 1):
                    mu += price_scale * close[pos - (t + j)]
                mu /= block_size

                # Compute block std (population std)
                sum_sq = 0.0
                for j in range(1, block_size + 1):
                    diff = price_scale * close[pos - (t + j)] - mu
                    sum_sq += diff * diff
                std = math.sqrt(sum_sq / block_size)
                if std <= 0.0:
                    std = 0.1

                # Cumulative deviations and range
                # MQ4 computes W[i,k+t] = sum_{z=1}^{k} (x[pos+t+z]*pip - mu)
                # Then finds max and min of W[*] for k=1..block_size
                # Note: MQ4 uses _highest which initializes highest=0
                # and _lowest which initializes lowest=9999999999
                # This means if all cumulative deviations are negative,
                # max will be 0 (not the actual max). Same for min > 0.
                cum_dev = 0.0
                # MQ4's _highest starts at 0, _lowest at 9999999999
                w_max = 0.0
                w_min = 9999999999.0
                for k in range(1, block_size + 1):
                    cum_dev += price_scale * close[pos - (t + k)] - mu
                    if cum_dev > w_max:
                        w_max = cum_dev
                    if cum_dev < w_min:
                        w_min = cum_dev

                # MQ4 clamps: if max < 0: max = 0; if min > 0: min = 0
                if w_max < 0.0:
                    w_max = 0.0
                if w_min > 0.0:
                    w_min = 0.0

                r_val = w_max - w_min
                rs_sum += r_val / std
                t += block_size
                block_count += 1

            # Average R/S for this scale
            if block_count > 0:
                rs_avg = rs_sum / block_count
            else:
                rs_avg = 1.0

            # Guard against log of non-positive
            if rs_avg <= 0.0:
                rs_avg = 1e-10

            log2_d = math.log(block_size) / math.log(2)
            log2_rs = math.log(rs_avg) / math.log(2)

            sumx += log2_d
            sumy += log2_rs
            sumx2 += log2_d * log2_d
            sumxy += log2_d * log2_rs
            valid_scales += 1

        # Linear regression slope = Hurst exponent
        if valid_scales < 2:
            h = 0.5  # default to random walk
        else:
            h1 = valid_scales * sumxy - sumx * sumy
            h2 = valid_scales * sumx2 - sumx * sumx
            if h2 <= 0.0:
                h2 = 0.1
            h = h1 / h2

        # Guard H (MQ4: if 2*H <= 0 then H = 0.001)
        if 2.0 * h <= 0.0:
            h = 0.001

        alpha = 1.0 / (2.0 * h)
        spd = max(1, round(normal_speed * alpha))

        # Compute SMA with adapted speed
        # MQ4 uses iMA(NULL, 0, speed, 0, 0, 0, pos) which is SMA of
        # `speed` bars ending at bar `pos` (inclusive).
        # In forward indexing: average of close[pos - spd + 1 .. pos]
        sma_start = pos - spd + 1
        if sma_start < 0:
            sma_start = 0
        total = 0.0
        count = pos - sma_start + 1
        for i in range(sma_start, pos + 1):
            total += close[i]
        result[pos] = total / count

    return result


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
    # period must be power of 2: 4, 8, 16, 32, 64, 128
    # price_scale variations: 1.0, 100.0, 10000.0
    test_params = [
        {"period": 4, "price_scale": 1.0},
        {"period": 8, "price_scale": 1.0},
        {"period": 16, "price_scale": 1.0},
        {"period": 32, "price_scale": 1.0},
        {"period": 64, "price_scale": 1.0},
        {"period": 128, "price_scale": 1.0},
        {"period": 32, "price_scale": 100.0},
        {"period": 32, "price_scale": 10000.0},
    ]

    # --- Generate reference outputs ---
    results = []
    for params in test_params:
        p = params["period"]
        s = params["price_scale"]
        output = rs_fractal_adaptive_simple_moving_average(
            INPUT_CLOSE, period=p, normal_speed=30, price_scale=s
        )
        results.append((p, s, output))

    def param_suffix(p, s):
        """Generate suffix like P4_S1, P32_S100, P32_S10000."""
        if s == 1.0:
            return f"P{p}_S1"
        elif s == 100.0:
            return f"P{p}_S100"
        elif s == 10000.0:
            return f"P{p}_S10000"
        else:
            return f"P{p}_S{int(s)}"

    def param_desc(p, s):
        if s == 1.0:
            return f"period={p}, price_scale=1.0"
        return f"period={p}, price_scale={s}"

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
        for (p, s, output) in results:
            sf = param_suffix(p, s)
            f.write(f"# RS Fractal Adaptive Simple Moving Average ({param_desc(p, s)})\n")
            f.write(f"# rs_fractal_adaptive_simple_moving_average(INPUT_CLOSE, {param_desc(p, s)}, normal_speed=30)\n")
            f.write(f"EXPECTED_{sf}: list[float] = [\n")
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
        f.write("package rsfractaladaptivesimplemovingaverage\n\n")
        f.write("import \"math\"\n\n")

        # testInput
        f.write("var testInput = []float64{\n")
        for i in range(0, len(INPUT_CLOSE), 10):
            chunk = INPUT_CLOSE[i:i+10]
            line = ", ".join(f"{v:.6f}" for v in chunk)
            f.write(f"\t{line},\n")
        f.write("}\n\n")

        for (p, s, output) in results:
            sf = param_suffix(p, s)
            # Go: camelCase with leading lowercase
            go_name = "expected" + sf
            f.write(f"// RS Fractal Adaptive Simple Moving Average ({param_desc(p, s)})\n")
            f.write(f"// rs_fractal_adaptive_simple_moving_average(INPUT_CLOSE, {param_desc(p, s)}, normal_speed=30)\n")
            f.write(f"var {go_name} = []float64{{\n")
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

        for (p, s, output) in results:
            sf = param_suffix(p, s)
            # TS: camelCase
            ts_name = "expected" + sf
            f.write(f"// RS Fractal Adaptive Simple Moving Average ({param_desc(p, s)})\n")
            f.write(f"// rs_fractal_adaptive_simple_moving_average(INPUT_CLOSE, {param_desc(p, s)}, normal_speed=30)\n")
            f.write(f"export const {ts_name}: number[] = [\n")
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

        for (p, s, output) in results:
            sf = param_suffix(p, s)
            # Rust: snake_case lowercase
            rs_name = "expected_" + sf.lower()
            f.write(f"    // RS Fractal Adaptive Simple Moving Average ({param_desc(p, s)})\n")
            f.write(f"    // rs_fractal_adaptive_simple_moving_average(INPUT_CLOSE, {param_desc(p, s)}, normal_speed=30)\n")
            f.write(f"    pub fn {rs_name}() -> Vec<f64> {{\n")
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

        for (p, s, output) in results:
            sf = param_suffix(p, s)
            # Zig: camelCase
            zig_name = "expected" + sf
            f.write(f"// RS Fractal Adaptive Simple Moving Average ({param_desc(p, s)})\n")
            f.write(f"// rs_fractal_adaptive_simple_moving_average(INPUT_CLOSE, {param_desc(p, s)}, normal_speed=30)\n")
            f.write(f"pub fn {zig_name}() [252]f64 {{\n")
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
    for (p, s, output) in results:
        valid = sum(1 for v in output if not math.isnan(v))
        f_val = next((v for v in output if not math.isnan(v)), None)
        l_val = next((v for v in reversed(output) if not math.isnan(v)), None)
        sf = param_suffix(p, s)
        if f_val is not None:
            print(f"  {sf}: {valid} valid values, first={f_val:.15f}, last={l_val:.15f}")
        else:
            print(f"  {sf}: {valid} valid values")
