"""Streaming research master for Ehlers' two-pole SuperSmoother.

The full-precision recurrence is equation 3-3 in Cycle Analytics for Traders
and the SuperSmoother sidebar in the January 2014 TASC article. The first price
seeds both output histories, as in the copied zpano implementation. Two startup
outputs are hidden with NaN; filtering continues internally during those bars.
All numeric code uses only Python's standard library and scalar binary64 math.
"""

from __future__ import annotations

import math


def _smoother_coefficients(period: float) -> tuple[float, float, float]:
    """Full-precision radian form of the source's degree-based coefficients.

    Do not replace sqrt(2) with 1.414 or pi with 3.14159 in a port. c1 includes
    the DC normalization; the two-input average's division by 2 stays in update.
    The last coefficient is negative; the recurrence adds c3 times old output.
    """
    angle = math.sqrt(2.0) * math.pi / period
    a1 = math.exp(-angle)
    c2 = 2.0 * a1 * math.cos(angle)
    c3 = -a1 * a1
    c1 = 1.0 - c2 - c3
    return c1, c2, c3


class SuperSmoother:
    """Two-pole low-pass filter with a zero at the two-bar Nyquist period.

    period is a finite real coefficient-setting period >= 2 bars, default 10.
    It can be fractional: it is not an integer window or a warmup count.
    update consumes one scalar chronologically and returns one float. The
    first two accepted samples return NaN, and sample 3 exposes a result.
    A NaN sample is skipped without advancing state; infinity is rejected.
    """

    def __init__(self, period: float = 10.0) -> None:
        self._period = float(period)
        if not math.isfinite(self._period) or self._period < 2.0:
            raise ValueError("period must be finite and at least 2 bars")
        self._c1, self._c2, self._c3 = _smoother_coefficients(self._period)
        self.reset()

    @property
    def period(self) -> float:
        return self._period

    @property
    def is_primed(self) -> bool:
        """Output availability; this does not promise a settled IIR transient."""
        return self._count >= 3

    @property
    def warmup_bars(self) -> int:
        """Number of leading NaNs for a sequence of finite input samples."""
        return 2

    def reset(self) -> None:
        """Clear all histories; the next finite price supplies the new seed."""
        self._count = 0
        self._input1 = 0.0
        self._output1 = self._output2 = 0.0

    def update(self, sample: float) -> float:
        """Consume a scalar; internal startup values are not public outputs."""
        sample = float(sample)
        if math.isnan(sample):
            # A missing observation is not a fabricated bar. Ports must also
            # avoid moving the counter or any history when skipping this NaN.
            return math.nan
        if not math.isfinite(sample):
            raise ValueError("sample must be finite or NaN")

        if self._count == 0:
            # Constant-price extension before the first observation avoids a
            # price-scale jump from zero. This matches the copied zpano seed.
            # Still evaluate the equation on this bar: do not round the seed.
            self._input1 = sample
            self._output1 = self._output2 = sample

        # All terms read PRIOR state. Keep the source's operation order: apply
        # c1 to the input sum before dividing by 2; do not pre-round any term.
        output = (
            self._c1 * (sample + self._input1) / 2.0
            + self._c2 * self._output1
            + self._c3 * self._output2
        )

        # Shift the older output before writing today's output. The state is
        # updated even when the public output is still masked with NaN.
        self._input1 = sample
        self._output2, self._output1 = self._output1, output
        self._count += 1
        return output if self.is_primed else math.nan

# The user confirmed all 34 cases across the three indicators on 2026-10-20.
INDICATOR_SLUG = 'super-smoother'
MASTER_CLASS = SuperSmoother
PARAMETER_SHORTCUTS = [('period', 'P')]
REFERENCE_CASES = (
    {'period': 2, 'what_it_tests': 'Nyquist-period lower boundary: valid coefficients and two hidden startup outputs.'},
    {'period': 3, 'what_it_tests': 'Very short period: fast damping and reversal response.'},
    {'period': 5, 'what_it_tests': 'Short-period smoothing: rapid response to price changes.'},
    {'period': 8, 'what_it_tests': 'Two octaves below Nyquist: short-cycle noise suppression.'},
    {'period': 10, 'what_it_tests': 'Article example and book recommendation: ten-bar SuperSmoother.'},
    {'period': 10.5, 'what_it_tests': 'Fractional period: preserve real-valued coefficients without integer truncation.'},
    {'period': 20, 'what_it_tests': 'Monthly-scale smoothing: stronger noise reduction and longer lag.'},
    {'period': 40, 'what_it_tests': 'Book Roofing low-pass example: longer smoothing memory.'},
    {'period': 80, 'what_it_tests': 'Long-period smoothing: sustained recursive memory.'},
    {'period': 252, 'what_it_tests': 'Full-record-length period: long transient with unchanged priming count.'},
)


# Everything below this line is fixture-generation tooling. Port the indicator
# classes and numeric helpers above; these file-formatting helpers are optional.
from pathlib import Path
import argparse
import ast


def _read_arrays(path: Path) -> dict[str, list[float]]:
    """Load numeric list assignments safely, including explicit math.nan."""
    arrays = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.List):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            values = []
            for element in node.value.elts:
                if (isinstance(element, ast.Attribute) and isinstance(element.value, ast.Name)
                        and element.value.id == "math" and element.attr == "nan"):
                    values.append(math.nan)
                else:
                    values.append(float(ast.literal_eval(element)))
            arrays[target.id] = values
    return arrays


def _parameter_token(value: float | int | bool) -> str:
    """10.0 -> 10; 10.5 -> 10_5; booleans -> 0/1. All tokens are identifiers."""
    return format(float(value), "g").replace(".", "_").replace("-", "m")


def _case_suffix(case: dict) -> str:
    # Case parameter order is fixed by the declared shortcut order, not sorted
    # alphabetically. That makes Python/Go/TS/Rust/Zig names easy to correlate.
    return "_".join(shortcut + _parameter_token(case[parameter])
                    for parameter, shortcut in PARAMETER_SHORTCUTS)


def _parameters(case: dict) -> dict:
    return {parameter: case[parameter] for parameter, _ in PARAMETER_SHORTCUTS}


def _parameter_comment(case: dict) -> str:
    return ", ".join(f"{parameter}={case[parameter]}" for parameter, _ in PARAMETER_SHORTCUTS)


def _literal(value: float, nan_literal: str) -> str:
    """Round only at serialization, to 15 significant decimal digits."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("infinite reference output cannot be serialized")
    literal = format(value, ".15g")
    # Rust and Zig arrays of f64 need float literals even for integral values.
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _rows(values: list[float], indent: str, nan_literal: str) -> str:
    literals = [_literal(value, nan_literal) for value in values]
    return "\n".join(indent + ", ".join(literals[index:index + 6]) + ","
                     for index in range(0, len(literals), 6))


def _replace_generated_section(path: Path, body: str, comment: str) -> None:
    """Append on first run; replace just the marked outputs on later runs."""
    begin = f"{comment} BEGIN GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA"
    end = f"{comment} END GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    section = begin + "\n\n" + body.rstrip() + "\n\n" + end
    if begin in original:
        start = original.index(begin)
        # A missing end marker raises instead of silently deleting file content.
        finish = original.index(end, start) + len(end)
        result = original[:start] + section + original[finish:]
    else:
        result = original.rstrip() + "\n\n" + section + "\n"
    path.write_text(result, encoding="utf-8")


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write Python first, verify it, then copy its decimal values to ports.

    No other-language implementation calculates or rounds expected data. Every
    expected array has the same 252 positions, NaN mask, and 15-digit literals.
    """
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("require 252 closes and between 1 and 64 confirmed cases")
    python_path = directory / "test_testdata.py"
    if _read_arrays(python_path)["INPUT_CLOSE"] != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from the copied fixture")

    raw_arrays = {}
    sections = []
    for case in REFERENCE_CASES:
        indicator = MASTER_CLASS(**_parameters(case))
        values = [indicator.update(sample) for sample in input_close]
        warmup = indicator.warmup_bars
        if not all(math.isnan(value) for value in values[:warmup]):
            raise ValueError("incorrect NaN prefix")
        if not all(math.isfinite(value) for value in values[warmup:]):
            raise ValueError("unexpected missing or infinite output after priming")
        name = "EXPECTED_" + _case_suffix(case)
        if name in raw_arrays:
            raise ValueError("duplicate reference case")
        raw_arrays[name] = values
        sections.append(
            f"# {case['what_it_tests']}\n# {_parameter_comment(case)}\n"
            f"{name} = [\n{_rows(values, '    ', 'math.nan')}\n]"
        )
    _replace_generated_section(python_path, "\n\n".join(sections), "#")

    # Verify the actual file, not just the in-memory arrays. Comparing each
    # parsed float with the correctly rounded original catches misplaced NaNs,
    # truncated arrays, and accidental extra rounding before propagation.
    written = _read_arrays(python_path)
    if {name for name in written if name.startswith("EXPECTED_")} != set(raw_arrays):
        raise ValueError("missing or unexpected expected arrays in Python")
    for name, raw in raw_arrays.items():
        if len(written[name]) != 252:
            raise ValueError(f"{name} must contain 252 values")
        for original, saved in zip(raw, written[name]):
            if math.isnan(original) and math.isnan(saved):
                continue
            if saved != float(_literal(original, "math.nan")):
                raise ValueError(f"{name} does not preserve 15-digit precision")

    other_sections = {filename: [] for filename in (
        "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig"
    )}
    for case in REFERENCE_CASES:
        suffix = _case_suffix(case)
        values = written["EXPECTED_" + suffix]
        comments = f"// {case['what_it_tests']}\n// {_parameter_comment(case)}\n"
        other_sections["testdata_test.go"].append(
            comments + f"var expected{suffix} = []float64{{\n"
            + _rows(values, "\t", "math.NaN()") + "\n}"
        )
        other_sections["testdata.ts"].append(
            comments + f"export const expected{suffix}: number[] = [\n"
            + _rows(values, "    ", "NaN") + "\n];"
        )
        other_sections["testdata.rs"].append(
            comments + f"pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n"
            + _rows(values, "        ", "f64::NAN") + "\n    ]\n}"
        )
        other_sections["testdata.zig"].append(
            comments + f"pub fn expected{suffix}() [252]f64 {{\n    return .{{\n"
            + _rows(values, "        ", "nan") + "\n    };\n}"
        )
    for filename, sections in other_sections.items():
        _replace_generated_section(directory / filename, "\n\n".join(sections), "//")
    print(f"Verified {len(raw_arrays)} arrays of 252 values; wrote Python, Go, TypeScript, Rust, Zig.")


def _run_main(input_close: list[float]) -> None:
    """A runnable example plus the confirmed reference-data generation CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true",
                        help="write all confirmed expected arrays in the five fixture files")
    arguments = parser.parse_args()
    if arguments.generate_reference_data:
        generate_reference_data(input_close, Path(__file__).resolve().parent)
    else:
        # Demonstrate normal streaming without overwriting fixture files.
        indicator = MASTER_CLASS()
        outputs = [indicator.update(sample) for sample in input_close]
        first = next(index for index, value in enumerate(outputs) if math.isfinite(value))
        print(f"{INDICATOR_SLUG}: {len(outputs)} closes; first valid output on bar {first + 1}")
        print("First five valid outputs:", [_literal(value, "NaN") for value in outputs[first:first + 5]])
        print(f"{len(REFERENCE_CASES)} parameter cases confirmed; use --generate-reference-data to regenerate.")


if __name__ == "__main__":
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
    _run_main(INPUT_CLOSE)
