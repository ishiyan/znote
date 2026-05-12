"""Generate testdata files in Go, TypeScript, Zig, and Rust from test_testdata.py.

Reads INPUT_CLOSE and all EXPECTED_* arrays from test_testdata.py and writes
idiomatic testdata files for each target language.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from test_testdata import INPUT_CLOSE

# Re-import the module to introspect all EXPECTED_* arrays
import test_testdata as td

# Collect all expected arrays with their metadata
combos = [
    ("W9_S6_O0_85",   "EXPECTED_W9_S6_O0_85",   "Default (whitepaper)", "window=9, sigma=6.0, offset=0.85"),
    ("W9_S6_O0_5",    "EXPECTED_W9_S6_O0_5",     "NinjaTrader default (symmetric Gaussian)", "window=9, sigma=6.0, offset=0.5"),
    ("W10_S6_O0_85",  "EXPECTED_W10_S6_O0_85",   "pandas_ta default (even window)", "window=10, sigma=6.0, offset=0.85"),
    ("W5_S6_O0_9",    "EXPECTED_W5_S6_O0_9",     "bbgo test case", "window=5, sigma=6, offset=0.9"),
    ("W1_S6_O0_85",   "EXPECTED_W1_S6_O0_85",    "Edge: window=1, passthrough", "window=1, sigma=6.0, offset=0.85"),
    ("W3_S6_O0_85",   "EXPECTED_W3_S6_O0_85",    "Minimum useful odd window", "window=3, sigma=6.0, offset=0.85"),
    ("W21_S6_O0_85",  "EXPECTED_W21_S6_O0_85",   "Longer period, common in practice", "window=21, sigma=6.0, offset=0.85"),
    ("W50_S6_O0_85",  "EXPECTED_W50_S6_O0_85",   "Max window", "window=50, sigma=6.0, offset=0.85"),
    ("W9_S6_O0",      "EXPECTED_W9_S6_O0",       "Offset=0: peak on oldest bar (max smoothing)", "window=9, sigma=6.0, offset=0.0"),
    ("W9_S6_O1",      "EXPECTED_W9_S6_O1",       "Offset=1: peak on newest bar (max responsiveness)", "window=9, sigma=6.0, offset=1.0"),
    ("W9_S2_O0_85",   "EXPECTED_W9_S2_O0_85",    "Narrow Gaussian (sharp, few bars matter)", "window=9, sigma=2.0, offset=0.85"),
    ("W9_S20_O0_85",  "EXPECTED_W9_S20_O0_85",   "Wide Gaussian (nearly uniform, SMA-like)", "window=9, sigma=20.0, offset=0.85"),
    ("W9_S0_5_O0_85", "EXPECTED_W9_S0_5_O0_85",  "Very narrow Gaussian (nearly single-bar)", "window=9, sigma=0.5, offset=0.85"),
    ("W15_S4_O0_7",   "EXPECTED_W15_S4_O0_7",    "Mixed non-default, moderate settings", "window=15, sigma=4.0, offset=0.7"),
]


def fmt_val(v, nan_str):
    if v != v:  # NaN check
        return nan_str
    return f"{v:.15f}"


def fmt_array(arr, nan_str, per_line=10, indent="    "):
    lines = []
    vals = [fmt_val(v, nan_str) for v in arr]
    for i in range(0, len(vals), per_line):
        chunk = vals[i:i+per_line]
        lines.append(indent + ", ".join(chunk) + ",")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Go
# ---------------------------------------------------------------------------
def gen_go(outdir):
    lines = []
    lines.append("//nolint:testpackage")
    lines.append("package alma")
    lines.append("")
    lines.append('import "math"')
    lines.append("")
    lines.append("var testInput = []float64{")
    lines.append(fmt_array(INPUT_CLOSE, "math.NaN()", indent="\t"))
    lines.append("}")

    for suffix, pyname, rationale, params in combos:
        arr = getattr(td, pyname)
        # Go convention: camelCase, e.g. expectedW9S6O085
        go_name = "expected" + suffix
        lines.append("")
        lines.append(f"// {rationale}")
        lines.append(f"// {params}")
        lines.append(f"var {go_name} = []float64{{")
        lines.append(fmt_array(arr, "math.NaN()", indent="\t"))
        lines.append("}")

    with open(os.path.join(outdir, "testdata_test.go"), "w") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# TypeScript
# ---------------------------------------------------------------------------
def gen_ts(outdir):
    lines = []
    lines.append("export const testInput: number[] = [")
    lines.append(fmt_array(INPUT_CLOSE, "NaN"))
    lines.append("];")

    for suffix, pyname, rationale, params in combos:
        arr = getattr(td, pyname)
        # TS convention: camelCase
        ts_name = "expected" + suffix
        lines.append("")
        lines.append(f"// {rationale}")
        lines.append(f"// {params}")
        lines.append(f"export const {ts_name}: number[] = [")
        lines.append(fmt_array(arr, "NaN"))
        lines.append("];")

    with open(os.path.join(outdir, "testdata.ts"), "w") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Zig
# ---------------------------------------------------------------------------
def gen_zig(outdir):
    lines = []
    lines.append('const math = @import("std").math;')
    lines.append("const nan = math.nan(f64);")
    lines.append("")
    lines.append("pub fn testInput() [252]f64 {")
    lines.append("    return .{")
    lines.append(fmt_array(INPUT_CLOSE, "nan", indent="        "))
    lines.append("    };")
    lines.append("}")

    for suffix, pyname, rationale, params in combos:
        arr = getattr(td, pyname)
        # Zig convention: camelCase function
        zig_name = "expected" + suffix
        lines.append("")
        lines.append(f"// {rationale}")
        lines.append(f"// {params}")
        lines.append(f"pub fn {zig_name}() [252]f64 {{")
        lines.append("    return .{")
        lines.append(fmt_array(arr, "nan", indent="        "))
        lines.append("    };")
        lines.append("}")

    with open(os.path.join(outdir, "testdata.zig"), "w") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Rust
# ---------------------------------------------------------------------------
def gen_rs(outdir):
    lines = []
    lines.append("#[cfg(test)]")
    lines.append("pub mod testdata {")
    lines.append("    pub fn test_input() -> Vec<f64> {")
    lines.append("        vec![")
    lines.append(fmt_array(INPUT_CLOSE, "f64::NAN", indent="            "))
    lines.append("        ]")
    lines.append("    }")

    for suffix, pyname, rationale, params in combos:
        arr = getattr(td, pyname)
        # Rust convention: snake_case
        rs_name = "expected_" + suffix.lower()
        lines.append("")
        lines.append(f"    // {rationale}")
        lines.append(f"    // {params}")
        lines.append(f"    pub fn {rs_name}() -> Vec<f64> {{")
        lines.append("        vec![")
        lines.append(fmt_array(arr, "f64::NAN", indent="            "))
        lines.append("        ]")
        lines.append("    }")

    lines.append("}")

    with open(os.path.join(outdir, "testdata.rs"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    outdir = os.path.dirname(__file__)
    gen_go(outdir)
    gen_ts(outdir)
    gen_zig(outdir)
    gen_rs(outdir)
    print("Generated: testdata_test.go, testdata.ts, testdata.zig, testdata.rs")
