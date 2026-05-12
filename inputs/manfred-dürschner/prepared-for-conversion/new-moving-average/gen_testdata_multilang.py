"""Generate testdata files in Go, TypeScript, Zig, and Rust from test_testdata.py.

Reads INPUT_CLOSE and all EXPECTED_* arrays from test_testdata.py and writes
idiomatic testdata files for each target language.

Usage: python gen_testdata_multilang.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import test_testdata as td

INPUT_CLOSE = td.INPUT_CLOSE
N = len(INPUT_CLOSE)

# Collect all expected arrays with their metadata
combos = [
    ("SEC_4_PRI_AUTO_LWMA",  "EXPECTED_SEC_4_PRI_AUTO_LWMA",  "sec=4, pri=auto(16), LWMA"),
    ("SEC_8_PRI_AUTO_LWMA",  "EXPECTED_SEC_8_PRI_AUTO_LWMA",  "sec=8, pri=auto(32), LWMA"),
    ("SEC_16_PRI_AUTO_LWMA", "EXPECTED_SEC_16_PRI_AUTO_LWMA", "sec=16, pri=auto(64), LWMA"),
    ("PRI_16_SEC_8_LWMA",    "EXPECTED_PRI_16_SEC_8_LWMA",    "pri=16, sec=8, LWMA"),
    ("PRI_32_SEC_8_LWMA",    "EXPECTED_PRI_32_SEC_8_LWMA",    "pri=32, sec=8, LWMA"),
    ("PRI_64_SEC_8_LWMA",    "EXPECTED_PRI_64_SEC_8_LWMA",    "pri=64, sec=8, LWMA"),
    ("PRI_8_SEC_4_LWMA",     "EXPECTED_PRI_8_SEC_4_LWMA",     "pri=8, sec=4, LWMA"),
    ("PRI_16_SEC_4_LWMA",    "EXPECTED_PRI_16_SEC_4_LWMA",    "pri=16, sec=4, LWMA"),
    ("PRI_32_SEC_4_LWMA",    "EXPECTED_PRI_32_SEC_4_LWMA",    "pri=32, sec=4, LWMA"),
    ("SEC_8_SMA",            "EXPECTED_SEC_8_SMA",            "sec=8, pri=auto(32), SMA"),
    ("SEC_8_EMA",            "EXPECTED_SEC_8_EMA",            "sec=8, pri=auto(32), EMA"),
    ("SEC_8_SMMA",           "EXPECTED_SEC_8_SMMA",           "sec=8, pri=auto(32), SMMA"),
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
    lines.append("package nma")
    lines.append("")
    lines.append('import "math"')
    lines.append("")
    lines.append("var testInput = []float64{")
    lines.append(fmt_array(INPUT_CLOSE, "math.NaN()", indent="\t"))
    lines.append("}")

    for suffix, pyname, rationale in combos:
        arr = getattr(td, pyname)
        go_name = "expected" + suffix
        lines.append("")
        lines.append(f"// {rationale}")
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

    for suffix, pyname, rationale in combos:
        arr = getattr(td, pyname)
        ts_name = "expected" + suffix
        lines.append("")
        lines.append(f"// {rationale}")
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
    lines.append(f"pub fn testInput() [{N}]f64 {{")
    lines.append("    return .{")
    lines.append(fmt_array(INPUT_CLOSE, "nan", indent="        "))
    lines.append("    };")
    lines.append("}")

    for suffix, pyname, rationale in combos:
        arr = getattr(td, pyname)
        zig_name = "expected" + suffix
        lines.append("")
        lines.append(f"// {rationale}")
        lines.append(f"pub fn {zig_name}() [{N}]f64 {{")
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

    for suffix, pyname, rationale in combos:
        arr = getattr(td, pyname)
        rs_name = "expected_" + suffix.lower()
        lines.append("")
        lines.append(f"    // {rationale}")
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
