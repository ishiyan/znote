"""
Generate test data for Lee-Oscillator indicator.
Produces test_testdata.py, testdata_test.go, testdata.ts, testdata.rs, testdata.zig
"""
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
qpl_mod = __import__('lee-oscillator')
LeeOscillatorCell = qpl_mod.LeeOscillatorCell
LORSCell = qpl_mod.LORSCell
compute_lee_oscillator = qpl_mod.compute_lee_oscillator
compute_bifurcation = qpl_mod.compute_bifurcation

# =============================================================================
# Input data: sweep of S values
# =============================================================================

INPUT_S = [i * 0.01 for i in range(-100, 101)]  # -1.0 to 1.0 in 0.01 steps (201 values)

# Smaller input for quick combos
INPUT_S_SMALL = [i * 0.1 for i in range(-10, 11)]  # 21 values

# =============================================================================
# Test combinations
# =============================================================================

# (description, params_comment, inputs, e1, e2, i1, i2, k, xi_e, xi_i, n_steps, suffix)
COMBOS = [
    ("Default parameters, 201 inputs, n_steps=100",
     "e1=20, e2=5, i1=1, i2=5, k=5, xi_e=0, xi_i=0, n_steps=100",
     INPUT_S, 20.0, 5.0, 1.0, 5.0, 5.0, 0.0, 0.0, 100, ""),

    ("Default parameters, n_steps=50",
     "e1=20, e2=5, i1=1, i2=5, k=5, n_steps=50",
     INPUT_S_SMALL, 20.0, 5.0, 1.0, 5.0, 5.0, 0.0, 0.0, 50, "_N50"),

    ("Default parameters, n_steps=51 (odd, other period-2 phase)",
     "e1=20, e2=5, i1=1, i2=5, k=5, n_steps=51",
     INPUT_S_SMALL, 20.0, 5.0, 1.0, 5.0, 5.0, 0.0, 0.0, 51, "_N51"),

    ("Low damping (k=1), wider bifurcation",
     "e1=20, e2=5, i1=1, i2=5, k=1, n_steps=100",
     INPUT_S_SMALL, 20.0, 5.0, 1.0, 5.0, 1.0, 0.0, 0.0, 100, "_K1"),

    ("High damping (k=10), narrow bifurcation",
     "e1=20, e2=5, i1=1, i2=5, k=10, n_steps=100",
     INPUT_S_SMALL, 20.0, 5.0, 1.0, 5.0, 10.0, 0.0, 0.0, 100, "_K10"),

    ("Weaker oscillation (e1=12, i2=3)",
     "e1=12, e2=5, i1=1, i2=3, k=5, n_steps=100",
     INPUT_S_SMALL, 12.0, 5.0, 1.0, 3.0, 5.0, 0.0, 0.0, 100, "_WEAK"),

    ("With thresholds",
     "e1=20, e2=5, i1=1, i2=5, k=5, xi_e=0.5, xi_i=0.2, n_steps=100",
     INPUT_S_SMALL, 20.0, 5.0, 1.0, 5.0, 5.0, 0.5, 0.2, 100, "_THR"),

    ("Short iteration (n_steps=10)",
     "e1=20, e2=5, i1=1, i2=5, k=5, n_steps=10",
     INPUT_S_SMALL, 20.0, 5.0, 1.0, 5.0, 5.0, 0.0, 0.0, 10, "_N10"),
]

# =============================================================================
# Run all combos
# =============================================================================

results = []
for desc, params, inputs, e1, e2, i1, i2, k, xi_e, xi_i, n_steps, suffix in COMBOS:
    outputs = compute_lee_oscillator(inputs, n_steps=n_steps,
                                     e1=e1, e2=e2, i1=i1, i2=i2,
                                     k=k, xi_e=xi_e, xi_i=xi_i)
    results.append((desc, params, inputs, outputs, suffix))
    print(f"  {suffix or '(default)'}: {len(outputs)} outputs, "
          f"range=[{min(outputs):.6f}, {max(outputs):.6f}]")

# =============================================================================
# Formatting helpers
# =============================================================================

def fmt(v):
    return f"{v:.15e}"

def fmt_array_py(arr, per_line=10):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("    " + ", ".join(fmt(v) for v in chunk) + ",")
    return "[\n" + "\n".join(lines) + "\n]"

def fmt_array_go(arr, per_line=10):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("\t" + ", ".join(fmt(v) for v in chunk) + ",")
    return "[]float64{\n" + "\n".join(lines) + "\n}"

def fmt_array_ts(arr, per_line=10):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("    " + ", ".join(fmt(v) for v in chunk) + ",")
    return "[\n" + "\n".join(lines) + "\n]"

def fmt_array_rs(arr, per_line=10):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("            " + ", ".join(fmt(v) for v in chunk) + ",")
    return "vec![\n" + "\n".join(lines) + "\n        ]"

def fmt_array_zig(arr, per_line=10):
    lines = []
    for i in range(0, len(arr), per_line):
        chunk = arr[i:i+per_line]
        lines.append("        " + ", ".join(fmt(v) for v in chunk) + ",")
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
    f.write(fmt_input_py("INPUT_S", INPUT_S))
    f.write("\n")
    f.write(fmt_input_py("INPUT_S_SMALL", INPUT_S_SMALL))
    f.write("\n")

    for desc, params, inputs, outputs, suffix in results:
        f.write(f"# {desc}\n")
        f.write(f"# {params}\n")
        f.write(f"EXPECTED{suffix} = {fmt_array_py(outputs)}\n\n")

print("Generated test_testdata.py")

# =============================================================================
# Generate testdata_test.go
# =============================================================================

with open(os.path.join(out_dir, "testdata_test.go"), "w") as f:
    f.write("//nolint:testpackage\npackage leeoscillator\n\n")
    f.write(fmt_input_go("testInputS", INPUT_S))
    f.write("\n")
    f.write(fmt_input_go("testInputSSmall", INPUT_S_SMALL))
    f.write("\n")

    for desc, params, inputs, outputs, suffix in results:
        f.write(f"// {desc}\n")
        f.write(f"// {params}\n")
        f.write(f"var expected{suffix} = {fmt_array_go(outputs)}\n\n")

print("Generated testdata_test.go")

# =============================================================================
# Generate testdata.ts
# =============================================================================

with open(os.path.join(out_dir, "testdata.ts"), "w") as f:
    f.write(fmt_input_ts("testInputS", INPUT_S))
    f.write("\n")
    f.write(fmt_input_ts("testInputSSmall", INPUT_S_SMALL))
    f.write("\n")

    for desc, params, inputs, outputs, suffix in results:
        f.write(f"// {desc}\n")
        f.write(f"// {params}\n")
        f.write(f"export const expected{suffix}: number[] = {fmt_array_ts(outputs)};\n\n")

print("Generated testdata.ts")

# =============================================================================
# Generate testdata.rs
# =============================================================================

with open(os.path.join(out_dir, "testdata.rs"), "w") as f:
    f.write("#[cfg(test)]\npub mod testdata {\n")
    f.write(fmt_input_rs("test_input_s", INPUT_S))
    f.write("\n")
    f.write(fmt_input_rs("test_input_s_small", INPUT_S_SMALL))
    f.write("\n")

    for desc, params, inputs, outputs, suffix in results:
        f.write(f"    // {desc}\n")
        f.write(f"    // {params}\n")
        rs_suffix = suffix.lower()
        f.write(f"    pub fn expected{rs_suffix}() -> Vec<f64> {{\n        {fmt_array_rs(outputs)}\n    }}\n\n")

    f.write("}\n")

print("Generated testdata.rs")

# =============================================================================
# Generate testdata.zig
# =============================================================================

with open(os.path.join(out_dir, "testdata.zig"), "w") as f:
    f.write('const math = @import("std").math;\n\n')
    f.write(fmt_input_zig("testInputS", INPUT_S))
    f.write("\n")
    f.write(fmt_input_zig("testInputSSmall", INPUT_S_SMALL))
    f.write("\n")

    for desc, params, inputs, outputs, suffix in results:
        f.write(f"// {desc}\n")
        f.write(f"// {params}\n")
        n = len(outputs)
        f.write(f"pub fn expected{suffix}() [{n}]f64 {{\n    return {fmt_array_zig(outputs)};\n}}\n\n")

print("Generated testdata.zig")
print(f"\nDone! All 5 test data files generated. ({len(COMBOS)} combos)")
