"""RSIH: RSI with Hann windowing, John F. Ehlers, January 2022.

Streaming, standard-library research master of the article/Mesa/TradeStation
listing. The scalar output is in [-1, +1]. The first length returned values
are NaN: length differences require length+1 actual input observations.
For an all-flat complete window, retain the preceding output, initially 0,
exactly as the source's guarded assignment to MyRSI does.

Read description.md before porting: inclusive indexing, interior Hann taps,
degree/radian conversion, accumulation order, and flat-window persistence
are essential. This is not Wilder's recursively smoothed RSI.

Run this file for a demonstration using the embedded 252 INPUT_CLOSE values.
The twelve REFERENCE_CASES were confirmed by the user on 2026-10-19.
--generate-reference-data writes 15-significant-digit expected arrays to all
five copied fixture files.
The streaming class itself has no file I/O or third-party dependencies.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class RsiHann:
    """Consume chronological scalar observations with update(value) -> float.

    length is the source RSILength: a positive integer, default 14. Changing
    length requires constructing a new instance; booleans are not lengths.
    Finite zero and negative observations are valid. Reject nonfinite inputs
    and overflow before changing state. Missing bars are not silently filled.

    A bounded newest-first list holds length+1 prices. This deliberately
    transparent layout maps prices[k] directly to EasyLanguage Close[k].
    Memory and per-observation work are O(length), with no infinite history.
    """

    def __init__(self, length: int = 14) -> None:
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError("length must be a positive integer")
        self._length = length
        self._weights = []
        for count in range(1, length + 1):
            # Source Cosine() accepts DEGREES. Python math.cos() accepts
            # RADIANS. Preserve source arithmetic before converting units.
            # Make division floating-point in Rust, Zig, Go, and C ports.
            angle_degrees = 360.0 * count / (length + 1)
            weight = 1.0 - math.cos(math.radians(angle_degrees))
            self._weights.append(weight)
        # Both stored endpoints have positive weight. Do not substitute a
        # library's length-point Hann with zero endpoints and length-1 divisor.
        # Common weight scaling cancels in the RSI ratio, so no normalization
        # coefficient or additional smoothing stage is needed.
        self.reset()

    @property
    def length(self) -> int:
        """Read-only RSILength configuration, measured in price differences."""
        return self._length

    @property
    def warmup_bars(self) -> int:
        """Number of NaN outputs before the first complete observation window."""
        return self._length

    @property
    def is_primed(self) -> bool:
        """True after length+1 accepted observations, including a flat window."""
        return len(self._prices) == self._length + 1

    def reset(self) -> None:
        """Forget every observation; restore the original MyRSI(0) seed."""
        self._prices = []
        # Availability NaNs are only returned; they never replace the source
        # variable's zero initial value or enter a history calculation.
        self._last_output = 0.0

    def update(self, value: float) -> float:
        """Accept one completed observation and return RSIH or a warmup NaN.

        On t=length (zero-based), Close[length] finally exists. NaN denotes
        unavailable history, not an undefined flat-window value after priming.
        Calling twice consumes two observations; there is no intrabar rewrite.
        """
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("input value must be finite")
        # Validate the new consecutive difference even during warmup, so an
        # overflowing accepted pair cannot poison the eventual full window.
        if self._prices and not math.isfinite(value - self._prices[0]):
            raise ValueError("price differences must be finite")

        # Prepare a candidate window. Commit only after all required arithmetic
        # succeeds, so an invalid update cannot corrupt a subsequent replay.
        prices = [value] + self._prices[:self._length]
        if len(prices) < self._length + 1:
            self._prices = prices
            return math.nan

        # Source CU and CD are RESET and accumulated afresh on EVERY bar.
        # These are weighted sums of positive/negative consecutive changes,
        # not EMA/RMA recurrences and not differences of smoothed prices.
        cu = 0.0
        cd = 0.0
        for count in range(1, self._length + 1):
            weight = self._weights[count - 1]
            # count=1 means the newest difference; count=length is INCLUDED.
            # Use separate up/down subtractions as in the original listing.
            up_change = prices[count - 1] - prices[count]
            down_change = prices[count] - prices[count - 1]
            if not math.isfinite(up_change) or not math.isfinite(down_change):
                raise ValueError("price differences must be finite")
            if up_change > 0.0:
                cu = cu + weight * up_change
            if down_change > 0.0:
                cd = cd + weight * down_change
        total = cu + cd
        if not math.isfinite(total):
            raise ValueError("weighted price-change sums must be finite")

        # The source says `If CU + CD <> 0 Then MyRSI = ...`, with no Else.
        # A flat complete window therefore keeps MyRSI, seeded to zero. Do not
        # replace it with zero on every flat window or divide zero by zero.
        result = self._last_output
        if total != 0.0:
            result = (cu - cd) / total

        # Preserve sequential binary64 summation and the exact source ratio.
        # No fsum, rolling-sum shortcut, epsilon guard, output clamp, or rounding
        # belongs in the streaming state. Round only when rendering fixtures.
        self._prices = prices
        self._last_output = result
        return result


class ReferenceCase(NamedTuple):
    """One confirmed RSILength and its portable 'What it tests' comment."""

    length: int
    what_it_tests: str


# All twelve cases were confirmed by the user on 2026-10-19.
# Only the source length varies.
# There are twelve cases, below the requested maximum of sixty-four.
REFERENCE_CASES = (
    ReferenceCase(14, "Article, Mesa and TradeStation default length."),
    ReferenceCase(1, "Minimum length; signed one-bar change and flat-bar persistence."),
    ReferenceCase(2, "Smallest multi-tap window; equal two-tap Hann weights."),
    ReferenceCase(3, "Short odd-length symmetric Hann window."),
    ReferenceCase(5, "Fast response to reversals with a short odd-length window."),
    ReferenceCase(8, "Short even-length window and smoothing of price-change spikes."),
    ReferenceCase(10, "Intermediate even-length window between fast and default settings."),
    ReferenceCase(20, "Slower response over a monthly-scale window."),
    ReferenceCase(30, "Longer cycle-scale window and stronger smoothing."),
    ReferenceCase(126, "Half-record window with extended history collection."),
    ReferenceCase(251, "Largest length with one primed value in the 252-price record."),
    ReferenceCase(252, "Insufficient history; all 252 outputs remain NaN."),
)


def _float_literal(value: float, nan_literal: str) -> str:
    """Emit fifteen significant digits; preserve explicit float literal types."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("expected values cannot be infinite")
    literal = format(value, ".15g")
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _array_lines(values: list[float], indent: str, nan_literal: str) -> str:
    """Render six comma-separated values per line in every language fixture."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return "\n".join(indent + ", ".join(literals[i:i + 6]) + ","
                     for i in range(0, len(literals), 6))


def _load_literal_arrays(path: Path) -> dict[str, list[float]]:
    """Parse Python fixture lists without importing or executing their code."""
    arrays = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.List):
            continue
        values = []
        for element in node.value.elts:
            if (isinstance(element, ast.Attribute) and isinstance(element.value, ast.Name)
                    and element.value.id == "math" and element.attr == "nan"):
                values.append(math.nan)
            else:
                values.append(float(ast.literal_eval(element)))
        for target in node.targets:
            if isinstance(target, ast.Name):
                arrays[target.id] = values
    return arrays


def _write_generated_section(path: Path, section: str, comment: str) -> None:
    """Append outputs or replace their marked section; preserve existing inputs.

    Do not duplicate expected arrays on reruns. Malformed markers are rejected
    instead of truncating an input file or guessing which text to overwrite.
    """
    begin = f"{comment} BEGIN GENERATED RSI HANN EXPECTED DATA"
    end = f"{comment} END GENERATED RSI HANN EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    generated = begin + "\n\n" + section.rstrip() + "\n\n" + end + "\n"
    if begin in original or end in original:
        if original.count(begin) != 1 or original.count(end) != 1:
            raise ValueError(f"malformed generated markers in {path.name}")
        start = original.index(begin)
        finish = original.index(end)
        if finish < start:
            raise ValueError(f"reversed generated markers in {path.name}")
        result = original[:start] + generated.rstrip("\n") + original[finish + len(end):]
    else:
        result = original.rstrip() + "\n\n" + generated
    path.write_text(result, encoding="utf-8")


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Generate confirmed cases in Python, verify, then translate that data.

    Tooling only: other repositories port RsiHann, not this file renderer.
    All finite calculations stay binary64 until the final .15g serialization.
    The case table has been confirmed by the user.
    """
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 prices and between one and 64 cases")
    if len({case.length for case in REFERENCE_CASES}) != len(REFERENCE_CASES):
        raise ValueError("reference lengths must be unique")
    python_path = directory / "test_testdata.py"
    original_inputs = {name: values for name, values in _load_literal_arrays(python_path).items()
                       if name.startswith("INPUT_")}
    if original_inputs.get("INPUT_CLOSE") != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from the copied input fixture")

    raw_outputs = {}
    python_sections = []
    for case in REFERENCE_CASES:
        indicator = RsiHann(case.length)
        values = [indicator.update(value) for value in input_close]
        name = f"EXPECTED_L{case.length}"
        raw_outputs[name] = (values, case.length)
        python_sections.append(
            f"# {case.what_it_tests}\n# length={case.length}\n{name} = [\n"
            + _array_lines(values, "    ", "math.nan") + "\n]")
    _write_generated_section(python_path, "\n\n".join(python_sections), "#")

    # Reopen the actual written Python file before exporting to other languages.
    # Verify the preserved inputs, expected names, lengths, NaNs, and precision.
    written = _load_literal_arrays(python_path)
    if {name: written[name] for name in original_inputs} != original_inputs:
        raise ValueError("input arrays changed during output generation")
    if {name for name in written if name.startswith("EXPECTED_")} != set(raw_outputs):
        raise ValueError("missing or unexpected Python expected arrays")
    for name, (raw, warmup) in raw_outputs.items():
        values = written[name]
        if len(values) != 252:
            raise ValueError(f"{name} must contain exactly 252 values")
        for index, (before, after) in enumerate(zip(raw, values)):
            if index < warmup:
                if not math.isnan(before) or not math.isnan(after):
                    raise ValueError(f"{name} has an incorrect NaN prefix")
            elif (not math.isfinite(after) or after != float(_float_literal(before, "nan"))):
                raise ValueError(f"{name} failed fifteen-digit serialization verification")

    # Go's name is the folder name with punctuation removed, in lowercase.
    # The helper import is used by startup NaNs in every confirmed output array.
    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8").replace("package xxxx", "package rsihann", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package rsihann\n", 'package rsihann\n\nimport "math"\n', 1)
    go_path.write_text(go_text, encoding="utf-8")
    zig_path = directory / "testdata.zig"
    zig_text = zig_path.read_text(encoding="utf-8")
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n' + zig_text
    if "const nan = math.nan(f64);" not in zig_text:
        zig_text = zig_text.replace('const math = @import("std").math;\n',
                                   'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(zig_text, encoding="utf-8")

    translated = {"go": [], "ts": [], "rs": [], "zig": []}
    for case in REFERENCE_CASES:
        suffix = f"L{case.length}"
        values = written[f"EXPECTED_{suffix}"]  # Export verified PYTHON values.
        comments = f"// {case.what_it_tests}\n// length={case.length}\n"
        translated["go"].append(comments + f"var expected{suffix} = []float64{{\n"
                                + _array_lines(values, "\t", "math.NaN()") + "\n}")
        translated["ts"].append(comments + f"export const expected{suffix}: number[] = [\n"
                                + _array_lines(values, "    ", "NaN") + "\n];")
        translated["rs"].append(comments + f"pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n"
                                + _array_lines(values, "        ", "f64::NAN") + "\n    ]\n}")
        translated["zig"].append(comments + f"pub fn expected{suffix}() [252]f64 {{\n    return .{{\n"
                                 + _array_lines(values, "        ", "nan") + "\n    };\n}")
    for language, filename in (("go", "testdata_test.go"), ("ts", "testdata.ts"),
                               ("rs", "testdata.rs"), ("zig", "testdata.zig")):
        # Rust's original inputs are inside #[cfg(test)] pub mod testdata.
        # Put expected functions in the SAME module, after its inputs, so a
        # downstream port can import testdata::{test_input, expected_l14}.
        path = directory / filename
        if language == "rs" and "BEGIN GENERATED RSI HANN EXPECTED DATA" not in path.read_text():
            rust_text = path.read_text(encoding="utf-8")
            final_brace = rust_text.rfind("}")
            if final_brace < 0 or rust_text[final_brace + 1:].strip():
                raise ValueError("Rust fixture must end with its testdata module brace")
            path.write_text(rust_text[:final_brace], encoding="utf-8")
            _write_generated_section(path, "\n\n".join(translated[language]), "//")
            path.write_text(path.read_text(encoding="utf-8") + "}\n", encoding="utf-8")
        else:
            _write_generated_section(path, "\n\n".join(translated[language]), "//")
    print(f"Verified {len(raw_outputs)} arrays of 252 values; wrote all five language fixtures.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true",
                        help="regenerate all twelve confirmed reference cases")
    arguments = parser.parse_args()

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

    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
    else:
        # Example: independent instances consume the same chronological prices.
        # No rounded output is ever reused as an input observation or state.
        indicator = RsiHann()  # Source RSILength=14.
        output = [indicator.update(close) for close in INPUT_CLOSE]
        print(f"RSIH length={indicator.length}; {len(INPUT_CLOSE)} input observations")
        print(f"First {indicator.warmup_bars} outputs: NaN (history unavailable)")
        print(f"First primed output [{indicator.length}]: {output[indicator.length]:.15g}")
        print("Last five outputs:", ", ".join(format(value, ".15g") for value in output[-5:]))
        print("Reset and replay with a different window:")
        indicator.reset()
        print("Primed after reset:", indicator.is_primed)
        fast_indicator = RsiHann(length=5)
        for close in INPUT_CLOSE:
            fast_value = fast_indicator.update(close)
        print(f"Final length=5 output: {fast_value:.15g}")
