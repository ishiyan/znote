"""
Fractal Bands Hybride Adaptive
Mnemonic: fbanha

Hybrid variant of Fractal Bands that replaces fixed normal_speed with
Ehlers' CyclePeriod indicator output multiplied by a Nyquist factor,
making the FRASMA doubly adaptive to both fractal dimension and
dominant market cycle.

Original author: Jean-Philippe Poton, Copyright 2008
Source: Unpublished

Parameters
----------
prices : list[float]
    1D array of prices (index 0 = oldest).
period : int
    Lookback period for FDI computation. Default 30. Range [2, len(prices)].
normal_speed_fallback : int
    Fallback SMA period when CyclePeriod is unavailable. Default 30. Range [1, len(prices)].
alpha : float
    Band width multiplier raised to power H. Default 2.0. Range (0, inf).
nyquist : float
    Nyquist multiplier applied to estimated cycle period. Default 0.5. Range (0, inf).
alpha_hp : float
    High-pass filter alpha for Ehlers CyclePeriod. Default 0.07. Range (0, 1).

Returns
-------
tuple of three list[float]: (frasma, upper_band, lower_band)
    Each list has the same length as prices. Unprimed values are float('nan').

Algorithm
---------
1. Compute FDI (Fractal Dimension Index) over a rolling window of `period`.
2. Compute Ehlers CyclePeriod to estimate the dominant cycle.
3. For each bar: derive Hurst exponent H = 2 - FDI, adaptive speed from
   CyclePeriod * nyquist * (1/(2H)), compute FRASMA as SMA of that speed,
   deviation over the FDI window, and bands = frasma +/- deviation * alpha^H.
"""

import math


def _fdi(prices, period):
    """Fractal Dimension Index with ln(2*(period-1)) denominator."""
    n = len(prices)
    fdi = [float('nan')] * n
    ln2 = math.log(2.0)
    log_denom = math.log(2.0 * (period - 1))
    inv_n_sq = 1.0 / (period * period)

    for pos in range(period, n):
        window = prices[pos - period: pos + 1]
        price_max = max(window)
        price_min = min(window)
        price_range = price_max - price_min

        if price_range < 1e-10:
            fdi[pos] = 1.0
            continue

        length = 0.0
        for i in range(1, period + 1):
            norm_cur = (window[i] - price_min) / price_range
            norm_prev = (window[i - 1] - price_min) / price_range
            diff = norm_cur - norm_prev
            length += math.sqrt(diff * diff + inv_n_sq)

        fdi[pos] = 1.0 + (math.log(length) + ln2) / log_denom

    return fdi


def _ehlers_cycle_period(prices, alpha_hp):
    """
    Ehlers' CyclePeriod indicator -- estimates dominant cycle period using
    high-pass filter, quadrature oscillator, and adaptive period measurement.

    Reference: Ehlers, J.F. (2004). Cybernetic Analysis for Stocks and Futures.
    """
    n = len(prices)
    smooth = [0.0] * n
    cycle = [0.0] * n
    q1 = [0.0] * n
    i1 = [0.0] * n
    delta_phase = [0.0] * n
    inst_period = [6.0] * n
    period_out = [float('nan')] * n

    for t in range(6, n):
        # 4-bar weighted smoother
        smooth[t] = (prices[t] + 2.0 * prices[t - 1] + 2.0 * prices[t - 2] + prices[t - 3]) / 6.0

        # High-pass filter
        hp_coeff = (1.0 - 0.5 * alpha_hp) ** 2
        cycle[t] = (
            hp_coeff * (smooth[t] - 2.0 * smooth[t - 1] + smooth[t - 2])
            + 2.0 * (1.0 - alpha_hp) * cycle[t - 1]
            - (1.0 - alpha_hp) ** 2 * cycle[t - 2]
        )

        # Quadrature component (Hilbert transform approximation)
        q1[t] = (
            0.0962 * cycle[t]
            + 0.5769 * cycle[t - 2]
            - 0.5769 * cycle[t - 4]
            - 0.0962 * cycle[t - 6]
        ) * (0.5 + 0.08 * inst_period[t - 1])

        # In-phase component
        i1[t] = cycle[t - 3]

        # Smooth I and Q with EMA
        if t > 6:
            i1[t] = 0.15 * i1[t] + 0.85 * i1[t - 1]
            q1[t] = 0.15 * q1[t] + 0.85 * q1[t - 1]

        # Compute delta phase
        if abs(i1[t]) > 1e-10:
            dp = math.atan(q1[t] / i1[t])
        else:
            dp = delta_phase[t - 1]

        # Clamp delta phase
        if dp < 0.1:
            dp = 0.1
        if dp > 1.1:
            dp = 1.1
        delta_phase[t] = dp

        # Median delta phase over 5 bars
        if t >= 10:
            window5 = [delta_phase[t - 4], delta_phase[t - 3], delta_phase[t - 2],
                        delta_phase[t - 1], delta_phase[t]]
            window5.sort()
            median_dp = window5[2]
        else:
            median_dp = dp

        # Instantaneous period
        if abs(median_dp) > 1e-10:
            dc = 6.2832 / median_dp + 0.5
        else:
            dc = inst_period[t - 1]

        # Clamp and smooth
        if dc < 6.0:
            dc = 6.0
        if dc > 50.0:
            dc = 50.0
        inst_period[t] = 0.33 * dc + 0.67 * inst_period[t - 1]
        period_out[t] = inst_period[t]

    return period_out


def fractal_bands_hybride_adaptive(prices, period=30, normal_speed_fallback=30,
                                    alpha=2.0, nyquist=0.5, alpha_hp=0.07):
    """
    Compute Fractal Bands Hybride Adaptive.

    Like Fractal Bands, but normal_speed is replaced by
    CyclePeriod(price) * nyquist at each bar.

    Parameters
    ----------
    prices : list[float]
        1D array of prices (index 0 = oldest).
    period : int
        Lookback period for FDI computation. Default 30. Range [2, len(prices)].
    normal_speed_fallback : int
        Fallback SMA period if CyclePeriod is not available. Default 30. Range [1, len(prices)].
    alpha : float
        Band width multiplier (raised to power H). Default 2.0. Range (0, inf).
    nyquist : float
        Nyquist multiplier applied to the estimated cycle period. Default 0.5. Range (0, inf).
    alpha_hp : float
        High-pass filter alpha for Ehlers CyclePeriod. Default 0.07. Range (0, 1).

    Returns
    -------
    tuple of (frasma, upper, lower) : each list[float] of length len(prices).
        frasma : Fractal Adaptive SMA center line.
        upper  : Upper band.
        lower  : Lower band.
    """
    n = len(prices)
    fdi_vals = _fdi(prices, period)
    cycle_periods = _ehlers_cycle_period(prices, alpha_hp)

    nan = float('nan')
    frasma = [nan] * n
    upper = [nan] * n
    lower = [nan] * n

    for pos in range(period, n):
        fdi_val = fdi_vals[pos]
        if math.isnan(fdi_val):
            continue

        # Hurst exponent and adaptive speed
        hurst = 2.0 - fdi_val
        if hurst < 0.01:
            hurst = 0.01
        trail_dim = 1.0 / hurst
        beta = trail_dim / 2.0

        # Adaptive normal_speed from CyclePeriod
        cp = cycle_periods[pos]
        if math.isnan(cp) or cp < 1.0:
            ns = float(normal_speed_fallback)
        else:
            ns = cp * nyquist

        speed = max(int(round(ns * beta)), 1)

        # FRASMA
        if pos + 1 < speed:
            continue
        window = prices[pos + 1 - speed: pos + 1]
        frasma_val = sum(window) / len(window)
        frasma[pos] = frasma_val

        # Deviation over the FDI lookback window
        if pos + 1 >= period:
            dev_window = prices[pos + 1 - period: pos + 1]
        else:
            dev_window = prices[:pos + 1]
        sq_sum = 0.0
        for v in dev_window:
            d = v - frasma_val
            sq_sum += d * d
        deviation = 2.0 * math.sqrt(sq_sum / period)

        # Fractal bands
        band_mult = deviation * (alpha ** hurst)
        upper[pos] = frasma_val + band_mult
        lower[pos] = frasma_val - band_mult

    return frasma, upper, lower


if __name__ == "__main__":
    from test_testdata import INPUT_CLOSE

    # Parameter combinations (16 total = 4 periods x 2 nyquist x 2 alpha_hp,
    # with fixed normal_speed_fallback=30 and alpha=2.0)
    #
    # Most impactful params:
    #   period: controls FDI window (10, 20, 30, 50)
    #   nyquist: scales cycle period (0.5, 1.0)
    #   alpha_hp: controls high-pass cutoff (0.07, 0.15)
    #
    # Fixed: normal_speed_fallback=30, alpha=2.0

    param_combos = []
    for p in [10, 20, 30, 50]:
        for ny in [0.5, 1.0]:
            for ahp in [0.07, 0.15]:
                param_combos.append((p, 30, 2.0, ny, ahp))

    assert len(param_combos) == 16

    def fmt(v):
        if math.isnan(v):
            return "math.nan"
        return f"{v:.15f}"

    def fmt_go(v):
        if math.isnan(v):
            return "math.NaN()"
        return f"{v:.15f}"

    def fmt_ts(v):
        if math.isnan(v):
            return "NaN"
        return f"{v:.15f}"

    def fmt_rs(v):
        if math.isnan(v):
            return "f64::NAN"
        return f"{v:.15f}"

    def fmt_zig(v):
        if math.isnan(v):
            return "nan"
        return f"{v:.15f}"

    def param_suffix(period, nsf, alpha, nyquist, alpha_hp):
        ahp_str = str(alpha_hp).replace('.', '')
        return f"P{period}_NY{str(nyquist).replace('.', '')}_AHP{ahp_str}"

    def write_array(f, values, formatter, per_line=6, indent="    ", trailing_comma=True):
        for i in range(0, len(values), per_line):
            chunk = values[i:i + per_line]
            line = ", ".join(formatter(v) for v in chunk)
            if i + per_line < len(values) or trailing_comma:
                line += ","
            f.write(f"{indent}{line}\n")

    # Compute all results
    results = []
    for (p, nsf, a, ny, ahp) in param_combos:
        frasma, upper_band, lower_band = fractal_bands_hybride_adaptive(
            INPUT_CLOSE, period=p, normal_speed_fallback=nsf,
            alpha=a, nyquist=ny, alpha_hp=ahp
        )
        results.append((p, nsf, a, ny, ahp, frasma, upper_band, lower_band))

    # === Write test_testdata.py ===
    with open("test_testdata.py", "w") as f:
        f.write("import math\n\n")
        f.write("INPUT_CLOSE = [\n")
        write_array(f, INPUT_CLOSE, lambda v: f"{v:.6f}", per_line=10)
        f.write("]\n")

        for (p, nsf, a, ny, ahp, frasma, upper_band, lower_band) in results:
            sfx = param_suffix(p, nsf, a, ny, ahp)
            call = f"fractal_bands_hybride_adaptive(INPUT_CLOSE, period={p}, normal_speed_fallback={nsf}, alpha={a}, nyquist={ny}, alpha_hp={ahp})"

            f.write(f"\n# Fractal Bands Hybride Adaptive - FRASMA output ({sfx})\n")
            f.write(f"# {call}\n")
            f.write(f"EXPECTED_FRASMA_{sfx}: list[float] = [\n")
            write_array(f, frasma, fmt)
            f.write("]\n")

            f.write(f"\n# Fractal Bands Hybride Adaptive - UPPER output ({sfx})\n")
            f.write(f"# {call}\n")
            f.write(f"EXPECTED_UPPER_{sfx}: list[float] = [\n")
            write_array(f, upper_band, fmt)
            f.write("]\n")

            f.write(f"\n# Fractal Bands Hybride Adaptive - LOWER output ({sfx})\n")
            f.write(f"# {call}\n")
            f.write(f"EXPECTED_LOWER_{sfx}: list[float] = [\n")
            write_array(f, lower_band, fmt)
            f.write("]\n")

    # === Write testdata_test.go ===
    with open("testdata_test.go", "w") as f:
        f.write('//nolint:testpackage\n')
        f.write('package fractalbandshybrideadaptive\n\n')
        f.write('import "math"\n\n')
        f.write('var testInput = []float64{\n')
        write_array(f, INPUT_CLOSE, lambda v: f"{v:.6f}", per_line=10, indent="\t")
        f.write("}\n")

        for (p, nsf, a, ny, ahp, frasma, upper_band, lower_band) in results:
            sfx = param_suffix(p, nsf, a, ny, ahp)
            call = f"fractal_bands_hybride_adaptive(INPUT_CLOSE, period={p}, normal_speed_fallback={nsf}, alpha={a}, nyquist={ny}, alpha_hp={ahp})"

            # camelCase var name
            def to_camel(name):
                parts = name.split("_")
                return parts[0].lower() + "".join(w.capitalize() for w in parts[1:])

            for output_name, data in [("Frasma", frasma), ("Upper", upper_band), ("Lower", lower_band)]:
                var_name = f"expected{output_name}{sfx.replace('_', '')}"
                # Make first letter lowercase for Go
                var_name = var_name[0].lower() + var_name[1:]
                f.write(f"\n// Fractal Bands Hybride Adaptive - {output_name} output ({sfx})\n")
                f.write(f"// {call}\n")
                f.write(f"var {var_name} = []float64{{\n")
                write_array(f, data, fmt_go, per_line=6, indent="\t")
                f.write("}\n")

    # === Write testdata.ts ===
    with open("testdata.ts", "w") as f:
        f.write("export const testInput: number[] = [\n")
        write_array(f, INPUT_CLOSE, lambda v: f"{v:.6f}", per_line=10)
        f.write("];\n")

        for (p, nsf, a, ny, ahp, frasma, upper_band, lower_band) in results:
            sfx = param_suffix(p, nsf, a, ny, ahp)
            call = f"fractal_bands_hybride_adaptive(INPUT_CLOSE, period={p}, normal_speed_fallback={nsf}, alpha={a}, nyquist={ny}, alpha_hp={ahp})"

            for output_name, data in [("Frasma", frasma), ("Upper", upper_band), ("Lower", lower_band)]:
                var_name = f"expected{output_name}{sfx.replace('_', '')}"
                # first letter lowercase
                var_name = var_name[0].lower() + var_name[1:]
                f.write(f"\n// Fractal Bands Hybride Adaptive - {output_name} output ({sfx})\n")
                f.write(f"// {call}\n")
                f.write(f"export const {var_name}: number[] = [\n")
                write_array(f, data, fmt_ts)
                f.write("];\n")

    # === Write testdata.rs ===
    with open("testdata.rs", "w") as f:
        f.write("#[cfg(test)]\npub mod testdata {\n")
        f.write("    pub fn test_input() -> Vec<f64> {\n")
        f.write("        vec![\n")
        write_array(f, INPUT_CLOSE, lambda v: f"{v:.6f}", per_line=10, indent="            ")
        f.write("        ]\n    }\n")

        for (p, nsf, a, ny, ahp, frasma, upper_band, lower_band) in results:
            sfx = param_suffix(p, nsf, a, ny, ahp)
            call = f"fractal_bands_hybride_adaptive(INPUT_CLOSE, period={p}, normal_speed_fallback={nsf}, alpha={a}, nyquist={ny}, alpha_hp={ahp})"

            for output_name, data in [("frasma", frasma), ("upper", upper_band), ("lower", lower_band)]:
                fn_name = f"expected_{output_name}_{sfx.lower()}"
                label = output_name.capitalize()
                f.write(f"\n    // Fractal Bands Hybride Adaptive - {label} output ({sfx})\n")
                f.write(f"    // {call}\n")
                f.write(f"    pub fn {fn_name}() -> Vec<f64> {{\n")
                f.write(f"        vec![\n")
                write_array(f, data, fmt_rs, per_line=6, indent="            ")
                f.write("        ]\n    }\n")

        f.write("}\n")

    # === Write testdata.zig ===
    with open("testdata.zig", "w") as f:
        f.write('const std = @import("std");\n')
        f.write("const math = std.math;\n")
        f.write("const nan = math.nan(f64);\n\n")
        f.write("pub fn testInput() [252]f64 {\n")
        f.write("    return .{\n")
        write_array(f, INPUT_CLOSE, lambda v: f"{v:.6f}", per_line=10, indent="        ")
        f.write("    };\n}\n")

        for (p, nsf, a, ny, ahp, frasma, upper_band, lower_band) in results:
            sfx = param_suffix(p, nsf, a, ny, ahp)
            call = f"fractal_bands_hybride_adaptive(INPUT_CLOSE, period={p}, normal_speed_fallback={nsf}, alpha={a}, nyquist={ny}, alpha_hp={ahp})"

            for output_name, data in [("Frasma", frasma), ("Upper", upper_band), ("Lower", lower_band)]:
                fn_name = f"expected{output_name}{sfx.replace('_', '')}"
                # first letter lowercase
                fn_name = fn_name[0].lower() + fn_name[1:]
                f.write(f"\n// Fractal Bands Hybride Adaptive - {output_name} output ({sfx})\n")
                f.write(f"// {call}\n")
                f.write(f"pub fn {fn_name}() [252]f64 {{\n")
                f.write("    return .{\n")
                write_array(f, data, fmt_zig, per_line=6, indent="        ")
                f.write("    };\n}\n")

    print(f"Generated test data for {len(param_combos)} parameter combinations.")
    print("Files written: test_testdata.py, testdata_test.go, testdata.ts, testdata.rs, testdata.zig")
    for (p, nsf, a, ny, ahp) in param_combos:
        print(f"  period={p}, normal_speed_fallback={nsf}, alpha={a}, nyquist={ny}, alpha_hp={ahp}")
