"""
Generate test data for Quantum Price Levels indicator.
Produces test_testdata.py, testdata_test.go, testdata.ts, testdata.rs, testdata.zig
"""
import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module
qpl_mod = __import__('quantum-price-levels')
compute_qpl = qpl_mod.compute_qpl
QuantumPriceLevels = qpl_mod.QuantumPriceLevels

# =============================================================================
# Input data
# =============================================================================

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

# Generate 2048-bar synthetic series (seeded random walk)
random.seed(42)
INPUT_PRICES_2048 = [100.0]
for _ in range(2047):
    INPUT_PRICES_2048.append(INPUT_PRICES_2048[-1] * math.exp(random.gauss(0.0, 0.005)))

# =============================================================================
# Test combinations
# =============================================================================

REF_PRICE_DEFAULT = 107.87  # last bar of INPUT_CLOSE

COMBOS = [
    # (description, comment_params, prices, ref_price, num_levels, num_bins, scale_factor, suffix)
    ("Default parameters, 252-bar input",
     "num_levels=21, num_bins=100, scale_factor=0.21, reference_price=107.87",
     INPUT_CLOSE, REF_PRICE_DEFAULT, 21, 100, 0.21, ""),
    ("Smaller scale factor",
     "num_levels=21, num_bins=100, scale_factor=0.10, reference_price=107.87",
     INPUT_CLOSE, REF_PRICE_DEFAULT, 21, 100, 0.10, "_F0_10"),
    ("Larger scale factor",
     "num_levels=21, num_bins=100, scale_factor=0.42, reference_price=107.87",
     INPUT_CLOSE, REF_PRICE_DEFAULT, 21, 100, 0.42, "_F0_42"),
    ("Fewer bins (coarser histogram)",
     "num_levels=21, num_bins=50, scale_factor=0.21, reference_price=107.87",
     INPUT_CLOSE, REF_PRICE_DEFAULT, 21, 50, 0.21, "_B50"),
    ("Fewer bins + small scale",
     "num_levels=21, num_bins=50, scale_factor=0.10, reference_price=107.87",
     INPUT_CLOSE, REF_PRICE_DEFAULT, 21, 50, 0.10, "_B50_F0_10"),
    ("Fewer bins + large scale",
     "num_levels=21, num_bins=50, scale_factor=0.42, reference_price=107.87",
     INPUT_CLOSE, REF_PRICE_DEFAULT, 21, 50, 0.42, "_B50_F0_42"),
    ("Fewer levels (5)",
     "num_levels=5, num_bins=100, scale_factor=0.21, reference_price=107.87",
     INPUT_CLOSE, REF_PRICE_DEFAULT, 5, 100, 0.21, "_L5"),
    ("Medium levels (10)",
     "num_levels=10, num_bins=100, scale_factor=0.21, reference_price=107.87",
     INPUT_CLOSE, REF_PRICE_DEFAULT, 10, 100, 0.21, "_L10"),
    ("Different reference price (50.0)",
     "num_levels=21, num_bins=100, scale_factor=0.21, reference_price=50.0",
     INPUT_CLOSE, 50.0, 21, 100, 0.21, "_R50_0"),
    ("Different reference price (1000.0)",
     "num_levels=21, num_bins=100, scale_factor=0.21, reference_price=1000.0",
     INPUT_CLOSE, 1000.0, 21, 100, 0.21, "_R1000_0"),
    ("Different reference price (1.2345)",
     "num_levels=21, num_bins=100, scale_factor=0.21, reference_price=1.2345",
     INPUT_CLOSE, 1.2345, 21, 100, 0.21, "_R1_2345"),
    ("All non-default parameters",
     "num_levels=10, num_bins=50, scale_factor=0.42, reference_price=107.87",
     INPUT_CLOSE, REF_PRICE_DEFAULT, 10, 50, 0.42, "_L10_B50_F0_42"),
    ("Long series validation (2048 bars, realistic lambda)",
     "num_levels=21, num_bins=100, scale_factor=0.21, reference_price=last_bar",
      INPUT_PRICES_2048, INPUT_PRICES_2048[-1], 21, 100, 0.21, "_2K"),
]

# Streaming combos: (description, comment_params, prices, lookback, num_levels, num_bins, scale_factor, suffix)
# These use the streaming class with explicit lookback < len(prices)-1
STREAMING_COMBOS = [
    ("Streaming lookback=100, 252-bar input",
     "lookback=100, num_levels=21, num_bins=100, scale_factor=0.21",
     INPUT_CLOSE, 100, 21, 100, 0.21, "_S100"),
    ("Streaming lookback=150, fewer bins",
     "lookback=150, num_levels=21, num_bins=50, scale_factor=0.21",
     INPUT_CLOSE, 150, 21, 50, 0.21, "_S150_B50"),
    ("Streaming lookback=200, large scale",
     "lookback=200, num_levels=21, num_bins=100, scale_factor=0.42",
     INPUT_CLOSE, 200, 21, 100, 0.42, "_S200_F0_42"),
]

# =============================================================================
# Run all combos
# =============================================================================

results = []
for desc, params, prices, ref, nl, nb, sf, suffix in COMBOS:
    r = compute_qpl(prices, ref, num_levels=nl, num_bins=nb, scale_factor=sf)
    results.append((desc, params, r, suffix, ref, nl))
    print(f"  {suffix or '(default)'}: lambda={r['lambda_']:.15e}, sigma={r['sigma']:.15e}")

# Run streaming combos
for desc, params, prices, lookback, nl, nb, sf, suffix in STREAMING_COMBOS:
    qpl = QuantumPriceLevels(lookback=lookback, num_levels=nl, num_bins=nb, scale_factor=sf)
    last_result = None
    for p in prices:
        r = qpl.update(p)
        if r is not None:
            last_result = r
    if last_result is None:
        raise ValueError(f"Streaming combo {suffix} produced no output")
    # Conform to same result format as batch
    last_result['qfel'] = [0.0] * nl  # not exposed by streaming, placeholder
    last_result['qpr'] = [0.0] * nl
    last_result['mu'] = 0.0
    ref_price = prices[-1]
    results.append((desc, params, last_result, suffix, ref_price, nl))
    print(f"  {suffix}: lambda={last_result['lambda_']:.15e}, sigma={last_result['sigma']:.15e}")

# =============================================================================
# Formatting helpers
# =============================================================================

def fmt(v):
    """Format a float to 15-digit precision scientific notation."""
    if math.isnan(v):
        return None  # handled per-language
    return f"{v:.15e}"

def fmt_array_py(arr, per_line=5):
    """Format array as Python list literal."""
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("    " + ", ".join(fmt(v) for v in chunk) + ",")
    return "[\n" + "\n".join(lines) + "\n]"

def fmt_array_go(arr, per_line=5):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        parts = []
        for v in chunk:
            if math.isnan(v):
                parts.append("math.NaN()")
            else:
                parts.append(fmt(v))
        lines.append("\t" + ", ".join(parts) + ",")
    return "[]float64{\n" + "\n".join(lines) + "\n}"

def fmt_array_ts(arr, per_line=5):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        parts = []
        for v in chunk:
            if math.isnan(v):
                parts.append("NaN")
            else:
                parts.append(fmt(v))
        lines.append("    " + ", ".join(parts) + ",")
    return "[\n" + "\n".join(lines) + "\n]"

def fmt_array_rs(arr, per_line=5):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        parts = []
        for v in chunk:
            if math.isnan(v):
                parts.append("f64::NAN")
            else:
                parts.append(fmt(v))
        lines.append("            " + ", ".join(parts) + ",")
    return "vec![\n" + "\n".join(lines) + "\n        ]"

def fmt_array_zig(arr, per_line=5):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        parts = []
        for v in chunk:
            if math.isnan(v):
                parts.append("nan")
            else:
                parts.append(fmt(v))
        lines.append("        " + ", ".join(parts) + ",")
    return ".{\n" + "\n".join(lines) + "\n    }"

def fmt_input_py(name, arr, per_line=10):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("    " + ", ".join(f"{v:.6f}" for v in chunk) + ",")
    return f"{name} = [\n" + "\n".join(lines) + "\n]\n"

def fmt_input_go(name, arr, per_line=10):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("\t" + ", ".join(f"{v:.6f}" for v in chunk) + ",")
    return f"var {name} = []float64{{\n" + "\n".join(lines) + "\n}\n"

def fmt_input_ts(name, arr, per_line=10):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("    " + ", ".join(f"{v:.6f}" for v in chunk) + ",")
    return f"export const {name}: number[] = [\n" + "\n".join(lines) + "\n];\n"

def fmt_input_rs(name, arr, per_line=10):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("            " + ", ".join(f"{v:.6f}" for v in chunk) + ",")
    return f"    pub fn {name}() -> Vec<f64> {{\n        vec![\n" + "\n".join(lines) + "\n        ]\n    }\n"

def fmt_input_zig(name, arr, per_line=10):
    n = len(arr)
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("        " + ", ".join(f"{v:.6f}" for v in chunk) + ",")
    return f"pub fn {name}() [{n}]f64 {{\n    return .{{\n" + "\n".join(lines) + "\n    }};\n}\n"

# =============================================================================
# Generate test_testdata.py
# =============================================================================

out_dir = os.path.dirname(__file__)

with open(os.path.join(out_dir, "test_testdata.py"), "w") as f:
    f.write("import math\n\n")
    f.write(fmt_input_py("INPUT_CLOSE", INPUT_CLOSE))
    f.write("\n")
    f.write(fmt_input_py("INPUT_PRICES_2048", INPUT_PRICES_2048))
    f.write("\n")

    for desc, params, r, suffix, ref, nl in results:
        f.write(f"# {desc}\n")
        f.write(f"# {params}\n")
        f.write(f"# lambda={r['lambda_']:.15e}, sigma={r['sigma']:.15e}\n")

        f.write(f"EXPECTED_NQPR{suffix} = {fmt_array_py(r['nqpr'])}\n\n")
        f.write(f"EXPECTED_UPPER{suffix} = {fmt_array_py(r['qpl_upper'])}\n\n")
        f.write(f"EXPECTED_LOWER{suffix} = {fmt_array_py(r['qpl_lower'])}\n\n")

print("Generated test_testdata.py")

# =============================================================================
# Generate testdata_test.go
# =============================================================================

with open(os.path.join(out_dir, "testdata_test.go"), "w") as f:
    f.write("//nolint:testpackage\npackage quantumpricelevels\n\nimport \"math\"\n\n")
    f.write(fmt_input_go("testInput", INPUT_CLOSE))
    f.write("\n")
    f.write(fmt_input_go("testInput2K", INPUT_PRICES_2048))
    f.write("\n")

    for desc, params, r, suffix, ref, nl in results:
        f.write(f"// {desc}\n")
        f.write(f"// {params}\n")
        f.write(f"// lambda={r['lambda_']:.15e}, sigma={r['sigma']:.15e}\n")

        go_suffix = suffix  # keep underscores, Go var starts lowercase
        f.write(f"var expectedNQPR{go_suffix} = {fmt_array_go(r['nqpr'])}\n\n")
        f.write(f"var expectedUPPER{go_suffix} = {fmt_array_go(r['qpl_upper'])}\n\n")
        f.write(f"var expectedLOWER{go_suffix} = {fmt_array_go(r['qpl_lower'])}\n\n")

print("Generated testdata_test.go")

# =============================================================================
# Generate testdata.ts
# =============================================================================

with open(os.path.join(out_dir, "testdata.ts"), "w") as f:
    f.write(fmt_input_ts("testInput", INPUT_CLOSE))
    f.write("\n")
    f.write(fmt_input_ts("testInput2K", INPUT_PRICES_2048))
    f.write("\n")

    for desc, params, r, suffix, ref, nl in results:
        f.write(f"// {desc}\n")
        f.write(f"// {params}\n")
        f.write(f"// lambda={r['lambda_']:.15e}, sigma={r['sigma']:.15e}\n")

        f.write(f"export const expectedNQPR{suffix}: number[] = {fmt_array_ts(r['nqpr'])};\n\n")
        f.write(f"export const expectedUPPER{suffix}: number[] = {fmt_array_ts(r['qpl_upper'])};\n\n")
        f.write(f"export const expectedLOWER{suffix}: number[] = {fmt_array_ts(r['qpl_lower'])};\n\n")

print("Generated testdata.ts")

# =============================================================================
# Generate testdata.rs
# =============================================================================

with open(os.path.join(out_dir, "testdata.rs"), "w") as f:
    f.write("#[cfg(test)]\npub mod testdata {\n")
    f.write(fmt_input_rs("test_input", INPUT_CLOSE))
    f.write("\n")
    f.write(fmt_input_rs("test_input_2k", INPUT_PRICES_2048))
    f.write("\n")

    for desc, params, r, suffix, ref, nl in results:
        f.write(f"    // {desc}\n")
        f.write(f"    // {params}\n")
        f.write(f"    // lambda={r['lambda_']:.15e}, sigma={r['sigma']:.15e}\n")

        rs_suffix = suffix.lower()  # Rust uses lowercase
        f.write(f"    pub fn expected_nqpr{rs_suffix}() -> Vec<f64> {{\n        {fmt_array_rs(r['nqpr'])}\n    }}\n\n")
        f.write(f"    pub fn expected_upper{rs_suffix}() -> Vec<f64> {{\n        {fmt_array_rs(r['qpl_upper'])}\n    }}\n\n")
        f.write(f"    pub fn expected_lower{rs_suffix}() -> Vec<f64> {{\n        {fmt_array_rs(r['qpl_lower'])}\n    }}\n\n")

    f.write("}\n")

print("Generated testdata.rs")

# =============================================================================
# Generate testdata.zig
# =============================================================================

with open(os.path.join(out_dir, "testdata.zig"), "w") as f:
    f.write('const math = @import("std").math;\nconst nan = math.nan(f64);\n\n')
    f.write(fmt_input_zig("testInput", INPUT_CLOSE))
    f.write("\n")
    f.write(fmt_input_zig("testInput2K", INPUT_PRICES_2048))
    f.write("\n")

    for desc, params, r, suffix, ref, nl in results:
        f.write(f"// {desc}\n")
        f.write(f"// {params}\n")
        f.write(f"// lambda={r['lambda_']:.15e}, sigma={r['sigma']:.15e}\n")

        n = len(r['nqpr'])
        f.write(f"pub fn expectedNQPR{suffix}() [{n}]f64 {{\n    return {fmt_array_zig(r['nqpr'])};\n}}\n\n")
        f.write(f"pub fn expectedUPPER{suffix}() [{n}]f64 {{\n    return {fmt_array_zig(r['qpl_upper'])};\n}}\n\n")
        f.write(f"pub fn expectedLOWER{suffix}() [{n}]f64 {{\n    return {fmt_array_zig(r['qpl_lower'])};\n}}\n\n")

print("Generated testdata.zig")
print("\nDone! All 5 test data files generated.")
