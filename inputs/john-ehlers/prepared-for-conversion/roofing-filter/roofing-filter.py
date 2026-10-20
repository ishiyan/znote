"""Streaming research master for Ehlers' Roofing Filter.

Default: January 2014 article's two-pole HP followed by a SuperSmoother, 10/48.
Book chapter 7's earlier one-pole and one-pole-plus-zero-mean variants are also
available. Full-precision constants are used in BOTH stages. Unlike the copied
zpano two-pole startup, this master computes the first valid second difference
on bar 3; the first four public outputs remain NaN. See description.md.
"""

from __future__ import annotations

import math


def _smoother_coefficients(period: float) -> tuple[float, float, float]:
    """Equation 3-3 coefficients; angles in radians, never rounded constants."""
    angle = math.sqrt(2.0) * math.pi / period
    a1 = math.exp(-angle)
    c2 = 2.0 * a1 * math.cos(angle)
    c3 = -a1 * a1
    return 1.0 - c2 - c3, c2, c3


class RoofingFilter:
    """High-pass detrending followed by two-pole low-pass noise removal.

    shortest_cycle_period (L) is the SuperSmoother's critical period.
    longest_cycle_period (H) is the high-pass critical period. Both are finite
    real numbers, with L >= 2 and H > L. Fractional periods are supported.
    highpass_poles is integer 1 or 2. zero_mean adds a second one-pole HP after
    smoothing, and is valid only with highpass_poles=1. Default is 2, False.
    The output is in input units and is not normalized or clipped.
    """

    def __init__(self, shortest_cycle_period: float = 10.0,
                 longest_cycle_period: float = 48.0,
                 highpass_poles: int = 2, zero_mean: bool = False) -> None:
        self._shortest = float(shortest_cycle_period)
        self._longest = float(longest_cycle_period)
        if not math.isfinite(self._shortest) or self._shortest < 2.0:
            raise ValueError("shortest_cycle_period must be finite and at least 2 bars")
        if not math.isfinite(self._longest) or self._longest <= self._shortest:
            raise ValueError("longest_cycle_period must be finite and greater than shortest")
        if type(highpass_poles) is not int or highpass_poles not in (1, 2):
            raise ValueError("highpass_poles must be integer 1 or 2")
        if type(zero_mean) is not bool or (zero_mean and highpass_poles != 1):
            raise ValueError("zero_mean must be a bool and requires highpass_poles=1")
        self._poles = highpass_poles
        self._zero_mean = zero_mean

        # EasyLanguage angles: 360/H degrees for one pole, (.707*360/H)
        # for two. Replace .707 with 1/sqrt(2), then convert to radians.
        angle = (2.0 * math.pi / self._longest if self._poles == 1
                 else math.sqrt(2.0) * math.pi / self._longest)

        # The source alpha=(cos(angle)+sin(angle)-1)/cos(angle) has a removable
        # singularity at angle=pi/2 (one-pole H=4). Its algebraic half-angle
        # form has no 0/0 there and avoids small-angle cancellation at large H.
        # All admitted angles lie strictly between 0 and pi, so this form is
        # defined throughout this API's range. Use it in ports for consistency.
        tangent = math.tan(angle / 2.0)
        alpha = 2.0 * tangent / (1.0 + tangent)
        self._gain = 1.0 - alpha / 2.0
        self._decay = 1.0 - alpha
        self._c1, self._c2, self._c3 = _smoother_coefficients(self._shortest)
        self.reset()

    @property
    def shortest_cycle_period(self) -> float:
        return self._shortest

    @property
    def longest_cycle_period(self) -> float:
        return self._longest

    @property
    def highpass_poles(self) -> int:
        return self._poles

    @property
    def zero_mean(self) -> bool:
        return self._zero_mean

    @property
    def warmup_bars(self) -> int:
        """First 3 outputs are NaN for plain one-pole, first 4 otherwise."""
        return 4 if self._poles == 2 or self._zero_mean else 3

    @property
    def is_primed(self) -> bool:
        """Availability flag only; longer-period transients can still remain."""
        return self._count > self.warmup_bars

    def reset(self) -> None:
        """Zero both HP histories, both smoother histories, and optional HP2."""
        self._count = 0
        self._input1 = self._input2 = 0.0
        self._hp1 = self._hp2 = 0.0
        self._filt1 = self._filt2 = 0.0
        self._zero1 = 0.0

    def update(self, sample: float) -> float:
        """Consume one scalar and return the selected current Roofing value."""
        sample = float(sample)
        if math.isnan(sample):
            return math.nan  # Leave every history and priming count unchanged.
        if not math.isfinite(sample):
            raise ValueError("sample must be finite or NaN")

        needed_previous_inputs = self._poles
        if self._count < needed_previous_inputs:
            # Store raw inputs until a real first/second difference exists.
            # No fabricated raw prehistory is differenced against this price.
            hp = filt = zero = 0.0
        else:
            if self._poles == 2:
                # This first executes on bar 3. Do not discard that valid
                # difference just because public output remains unprimed.
                difference = sample - 2.0 * self._input1 + self._input2
                hp = (
                    self._gain * self._gain * difference
                    + 2.0 * self._decay * self._hp1
                    - self._decay * self._decay * self._hp2
                )
            else:
                # Book listing 7-1 and the first stage of listing 7-2.
                hp = self._gain * (sample - self._input1) + self._decay * self._hp1

            # Equation 3-3, applied to high-pass output, not directly to price.
            # hp is today's HP; self._hp1 is still yesterday's HP at this point.
            filt = (
                self._c1 * (hp + self._hp1) / 2.0
                + self._c2 * self._filt1
                + self._c3 * self._filt2
            )
            # In the book's zero-mean variant, HP2 follows the smoother and
            # uses the same one-pole coefficients as the first HP stage.
            zero = (self._gain * (filt - self._filt1) + self._decay * self._zero1
                    if self._zero_mean else 0.0)

        # Commit only after all formulas have consumed prior state. Hidden
        # startup bars DO update state; NaN input calls above do not.
        self._input2, self._input1 = self._input1, sample
        self._hp2, self._hp1 = self._hp1, hp
        self._filt2, self._filt1 = self._filt1, filt
        self._zero1 = zero
        self._count += 1
        output = zero if self._zero_mean else filt
        return output if self.is_primed else math.nan

# The user confirmed all 34 cases across the three indicators on 2026-10-20.
INDICATOR_SLUG = 'roofing-filter'
MASTER_CLASS = RoofingFilter
PARAMETER_SHORTCUTS = [('shortest_cycle_period', 'LP'), ('longest_cycle_period', 'HP'), ('highpass_poles', 'PO'), ('zero_mean', 'ZM')]
REFERENCE_CASES = (
    {'shortest_cycle_period': 10, 'longest_cycle_period': 48, 'highpass_poles': 2, 'zero_mean': False, 'what_it_tests': 'Article default: two-pole detrending and ten-bar noise suppression.'},
    {'shortest_cycle_period': 40, 'longest_cycle_period': 80, 'highpass_poles': 2, 'zero_mean': False, 'what_it_tests': 'Book listing 7-3 example: forty/eighty-bar Roofing Filter.'},
    {'shortest_cycle_period': 2, 'longest_cycle_period': 3, 'highpass_poles': 2, 'zero_mean': False, 'what_it_tests': 'Shortest supported low-pass and short high-pass: coefficient boundary behavior.'},
    {'shortest_cycle_period': 5, 'longest_cycle_period': 24, 'highpass_poles': 2, 'zero_mean': False, 'what_it_tests': 'Short-cycle passband: rapid reversal response.'},
    {'shortest_cycle_period': 10.5, 'longest_cycle_period': 48, 'highpass_poles': 2, 'zero_mean': False, 'what_it_tests': 'Fractional low-pass period: preserve real coefficient arithmetic.'},
    {'shortest_cycle_period': 10, 'longest_cycle_period': 11, 'highpass_poles': 2, 'zero_mean': False, 'what_it_tests': 'Closely spaced nominal band edges: attenuation and recursive stability.'},
    {'shortest_cycle_period': 20, 'longest_cycle_period': 80, 'highpass_poles': 2, 'zero_mean': False, 'what_it_tests': 'Longer passband: stronger smoothing and slower detrending.'},
    {'shortest_cycle_period': 40, 'longest_cycle_period': 252, 'highpass_poles': 2, 'zero_mean': False, 'what_it_tests': 'Long high-pass memory: startup effects across the full input record.'},
    {'shortest_cycle_period': 10, 'longest_cycle_period': 48, 'highpass_poles': 1, 'zero_mean': False, 'what_it_tests': 'Book listing 7-1: preliminary one-pole Roofing without zero-mean correction.'},
    {'shortest_cycle_period': 2, 'longest_cycle_period': 4, 'highpass_poles': 1, 'zero_mean': False, 'what_it_tests': 'One-pole period-four boundary: resolve the source alpha removable singularity.'},
    {'shortest_cycle_period': 10, 'longest_cycle_period': 48, 'highpass_poles': 1, 'zero_mean': True, 'what_it_tests': 'Book listing 7-2 final output: second one-pole high-pass after smoothing.'},
    {'shortest_cycle_period': 2, 'longest_cycle_period': 4, 'highpass_poles': 1, 'zero_mean': True, 'what_it_tests': 'Period-four boundary in both one-pole stages with zero-mean correction.'},
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
