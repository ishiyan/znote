"""Streaming master reference for John F. Ehlers' December 2025 One Euro Filter.

Numeric authority: calc_one_euro_filter in the supplied Traders' Tips Python
file, tips/Python_OneEuroFilter.py. This selects full-precision math.pi and an
explicit first-sample seed. EasyLanguage uses 3.14159 and does not return after
its initialization block; those differences are explained in description.md.

Only the standard library is used. The indicator itself needs three persistent
scalars, runs in O(1) time per sample, and stores no price history. File handling
below the indicator is fixture-generation tooling, not part of the port.

Usage:
    python3 one-euro-filter.py
    python3 one-euro-filter.py --generate-reference-data

The second command regenerates the user-confirmed parameter cases documented
in description.md. Repeated generation replaces a marked generated section
without duplicating expected arrays.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# This is a fixed internal variable in the article and the Python Traders' Tip,
# not a third configuration parameter. Keep it fixed in every language port.
PERIOD_DX = 10.0


class OneEuroFilter:
    """Consume one finite price and return one filtered float per update.

    period_min is a finite positive period in bars (default 10). beta is a
    finite multiplier (default 0.2); negative beta is the sharpening mode
    mentioned in the article. Every resulting adaptive cutoff must stay > 0.

    The first finite value primes the filter immediately and is returned as-is.
    Thus no leading NaN is required in the 252-bar reference arrays. A NaN or
    infinity input raises ValueError without advancing the stream. A fresh
    instance or reset() starts a new independent stream.
    """

    def __init__(self, period_min: float = 10.0, beta: float = 0.2) -> None:
        # Convert to the binary64 arithmetic used in the source and target
        # languages. Periods need not be integers for these algebraic equations.
        self._period_min = float(period_min)
        self._beta = float(beta)
        if not math.isfinite(self._period_min) or self._period_min <= 0.0:
            raise ValueError("period_min must be finite and greater than zero")
        if not math.isfinite(self._beta):
            raise ValueError("beta must be finite")

        # Preserve source operation order rather than substituting an EMA span
        # formula such as 2/(N+1). math.pi is deliberate: it matches the Python
        # Traders' Tip, whose np.pi has this same binary64 value.
        self._alpha_dx = 2.0 * math.pi / (4.0 * math.pi + PERIOD_DX)
        self.reset()

    @property
    def period_min(self) -> float:
        """Read-only configuration; construct a new filter to change it."""
        return self._period_min

    @property
    def beta(self) -> float:
        """Read-only configuration, including a possible negative beta."""
        return self._beta

    @property
    def is_primed(self) -> bool:
        """True after the first successful update; there is no window to fill."""
        return self._previous_price is not None

    @property
    def warmup_bars(self) -> int:
        """Number of leading NaN outputs: zero for the published Python seed."""
        return 0

    def reset(self) -> None:
        """Clear the three state values without changing configuration."""
        # None is an initialization sentinel, never a numerical zero-price
        # substitute. Zero is a legitimate price, particularly for oscillators.
        self._previous_price: float | None = None
        self._smoothed_dx = 0.0
        self._smoothed = math.nan

    def update(self, price: float) -> float:
        """Update the derivative EMA, then the adaptive price EMA, in that order."""
        price = float(price)
        if not math.isfinite(price):
            raise ValueError("price must be finite")

        # The published Python routine explicitly seeds array element zero and
        # starts its recursive loop at element one. Do exactly that here: do
        # not invent a previous zero price or run either recurrence on bar zero.
        if self._previous_price is None:
            self._previous_price = price
            self._smoothed_dx = 0.0
            self._smoothed = price
            return price

        # 1. One-bar difference of RAW input prices, not filtered outputs.
        # 2. EMA of that SIGNED difference. Taking abs before this EMA would
        #    change the algorithm and prevent opposite movements cancelling.
        delta = price - self._previous_price
        smoothed_dx = (
            self._alpha_dx * delta
            + (1.0 - self._alpha_dx) * self._smoothed_dx
        )

        # 3. Use this bar's derivative estimate immediately. Positive beta
        #    increases the PERIOD and therefore decreases the final alpha.
        #    "cutoff" is the source variable name; its units are bars, not Hz.
        cutoff = self._period_min + self._beta * abs(smoothed_dx)

        # The source has no clamps. Reject inadmissible research settings rather
        # than silently changing their recurrence. Calculate in locals so a
        # rejected sample leaves all persistent state unchanged.
        if not math.isfinite(smoothed_dx) or not math.isfinite(cutoff) or cutoff <= 0.0:
            raise ValueError("adaptive cutoff must be finite and greater than zero")

        # 4. Recompute the adaptive alpha using exactly the source equation.
        alpha = 2.0 * math.pi / (4.0 * math.pi + cutoff)

        # 5. Weighted sum with the PRIOR output. Keep the two multiplies and
        #    addition, rather than rewriting as y += alpha*(price-y). Such an
        #    algebraic rewrite can change the last few bits in reference data.
        smoothed = alpha * price + (1.0 - alpha) * self._smoothed
        if not math.isfinite(smoothed):
            raise ValueError("filtered output must be finite")

        # Commit only after the whole update succeeds. The derivative and price
        # EMA each use their prior state exactly once. Return the current output.
        self._previous_price = price
        self._smoothed_dx = smoothed_dx
        self._smoothed = smoothed
        return smoothed


class ReferenceCase(NamedTuple):
    """One confirmed reference case and the two required fixture comments."""

    period_min: float
    beta: float
    what_it_tests: str


# Twelve cases: three baseline periods times four adaptation modes. The
# derivative period is always PERIOD_DX=10. All negative-beta cutoffs have been
# checked to stay positive on the supplied INPUT_CLOSE sequence.
REFERENCE_CASES = (
    ReferenceCase(2.0, 0.0, "Short-period fixed EMA; adaptation disabled."),
    ReferenceCase(2.0, 0.2, "Short baseline with the article's positive beta."),
    ReferenceCase(2.0, 2.0, "Short baseline with strong positive adaptation."),
    ReferenceCase(2.0, -0.2, "Short-period sharpening near the positive-cutoff boundary."),
    ReferenceCase(10.0, 0.0, "Default-period fixed EMA; adaptation disabled."),
    ReferenceCase(10.0, 0.2, "Published article and Traders' Tips Python defaults."),
    ReferenceCase(10.0, 2.0, "Default baseline with strong positive adaptation."),
    ReferenceCase(10.0, -0.2, "Article's negative-beta sharpening at the default period."),
    ReferenceCase(30.0, 0.0, "Long-period fixed EMA; sustained lag and seed decay."),
    ReferenceCase(30.0, 0.2, "Long baseline with the article's positive beta."),
    ReferenceCase(30.0, 2.0, "Long baseline with strong positive adaptation."),
    ReferenceCase(30.0, -0.2, "Long-period sharpening with a conservative cutoff margin."),
)


def _parameter_token(value: float) -> str:
    """Make portable names: 0.2 -> 0_2, -0.2 -> m0_2, 10.0 -> 10."""
    # A minus sign is invalid in an identifier, so 'm' denotes minus. Keep
    # integral parameter values compact; fixtures themselves always use floats.
    return format(value, "g").replace("-", "m").replace(".", "_")


def _case_suffix(case: ReferenceCase) -> str:
    """PM = period_min, B = beta; the fixed derivative period is not named."""
    return f"PM{_parameter_token(case.period_min)}_B{_parameter_token(case.beta)}"


def _float_literal(value: float, nan_literal: str) -> str:
    """Emit 15 significant digits, ensuring an explicit floating-point literal."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("infinite reference output")
    # Rounding happens only here, after the entire binary64 stream calculation.
    # Do not feed these decimal-rounded values back into the filter state.
    literal = format(value, ".15g")
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _array_lines(values: list[float], indent: str, nan_literal: str) -> str:
    """Wrap an array at six values per row for reviewable fixture files."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return "\n".join(
        indent + ", ".join(literals[i:i + 6]) + ","
        for i in range(0, len(literals), 6)
    )


def _write_generated_section(path: Path, section: str, comment: str) -> None:
    """Preserve copied input data; append or replace only the marked outputs."""
    begin = f"{comment} BEGIN GENERATED ONE EURO FILTER EXPECTED DATA"
    end = f"{comment} END GENERATED ONE EURO FILTER EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    generated = begin + "\n\n" + section.rstrip() + "\n\n" + end + "\n"
    if begin in original:
        # Never truncate a malformed existing file after a lone start marker.
        start = original.index(begin)
        finish = original.index(end, start) + len(end)
        result = original[:start] + generated.rstrip("\n") + original[finish:]
    else:
        result = original.rstrip() + "\n\n" + generated
    path.write_text(result, encoding="utf-8")


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Generate Python first, verify it, then translate its decimal literals.

    Only file syntax and names change across languages. Other-language expected
    data is loaded back from test_testdata.py, rather than being independently
    calculated or rounded from some other implementation.
    """
    if len(input_close) != 252:
        raise ValueError("the reference input must contain exactly 252 closes")
    if not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("reference case count must be between 1 and 64")

    # Check that the embedded main array equals the copied Python input. AST
    # parsing avoids executing any fixture file while loading numeric literals.
    python_path = directory / "test_testdata.py"
    copied_input = _load_literal_arrays(python_path)["INPUT_CLOSE"]
    if copied_input != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from test_testdata.py")

    python_sections = []
    raw_outputs = {}
    for case in REFERENCE_CASES:
        indicator = OneEuroFilter(case.period_min, case.beta)
        values = [indicator.update(price) for price in input_close]
        name = "EXPECTED_" + _case_suffix(case)
        raw_outputs[name] = values
        python_sections.append(
            f"# {case.what_it_tests}\n"
            f"# period_min={case.period_min:g}, beta={case.beta:g}, period_dx=10 (fixed)\n"
            f"{name} = [\n{_array_lines(values, '    ', 'math.nan')}\n]"
        )
    _write_generated_section(python_path, "\n\n".join(python_sections), "#")

    # Read the written Python arrays back and check count, length, and precision
    # before appending them to other languages. Current cases prime immediately;
    # the renderer still supports each language's NaN syntax for future fixtures.
    written_arrays = _load_literal_arrays(python_path)
    expected_names = {name for name in written_arrays if name.startswith("EXPECTED_")}
    if expected_names != set(raw_outputs):
        raise ValueError("unexpected or missing Python expected array names")
    for name, raw in raw_outputs.items():
        written = written_arrays[name]
        if len(written) != 252:
            raise ValueError(f"{name} does not contain 252 outputs")
        for before, after in zip(raw, written):
            if math.isnan(before) and math.isnan(after):
                continue
            if not math.isclose(before, after, rel_tol=5e-14, abs_tol=5e-14):
                raise ValueError(f"{name} did not retain 15-digit precision")

    # Go requires a used import. There are no warm-up NaNs in this indicator,
    # so a blank reference keeps the specifically requested math import valid.
    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8").replace(
        "package xxxx", "package theoneeurofilter", 1
    )
    if 'import "math"' not in go_text:
        go_text = go_text.replace(
            "package theoneeurofilter\n",
            'package theoneeurofilter\n\nimport "math"\n\n'
            '// Keep the NaN helper available even though this filter primes immediately.\n'
            'var _ = math.NaN\n', 1,
        )
    go_path.write_text(go_text, encoding="utf-8")

    zig_path = directory / "testdata.zig"
    zig_text = zig_path.read_text(encoding="utf-8")
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n' + zig_text
    if 'const nan = math.nan(f64);' not in zig_text:
        zig_text = zig_text.replace(
            'const math = @import("std").math;\n',
            'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1,
        )
    zig_path.write_text(zig_text, encoding="utf-8")

    sections = {"go": [], "ts": [], "rs": [], "zig": []}
    for case in REFERENCE_CASES:
        suffix = _case_suffix(case)
        # This list is explicitly the data read from the Python fixture above.
        values = written_arrays["EXPECTED_" + suffix]
        comments = (
            f"// {case.what_it_tests}\n"
            f"// period_min={case.period_min:g}, beta={case.beta:g}, period_dx=10 (fixed)\n"
        )
        sections["go"].append(
            comments + f"var expected{suffix} = []float64{{\n"
            + _array_lines(values, "\t", "math.NaN()") + "\n}"
        )
        # Follow the existing valid TypeScript array syntax. The sample syntax
        # in the request contains a typo; export const name: number[] is valid.
        sections["ts"].append(
            comments + f"export const expected{suffix}: number[] = [\n"
            + _array_lines(values, "    ", "NaN") + "\n];"
        )
        sections["rs"].append(
            comments + f"pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n"
            + _array_lines(values, "        ", "f64::NAN") + "\n    ]\n}"
        )
        sections["zig"].append(
            comments + f"pub fn expected{suffix}() [252]f64 {{\n    return .{{\n"
            + _array_lines(values, "        ", "nan") + "\n    };\n}"
        )

    # Rust's copied input functions stay inside their existing cfg(test)
    # module. Expected functions are appended at file scope for direct access
    # from a port's tests, with no rename or reorganization of copied inputs.
    for language, filename in (
        ("go", "testdata_test.go"), ("ts", "testdata.ts"),
        ("rs", "testdata.rs"), ("zig", "testdata.zig"),
    ):
        _write_generated_section(directory / filename, "\n\n".join(sections[language]), "//")
    print(f"Verified {len(REFERENCE_CASES)} arrays of 252 outputs in Python; wrote all five languages.")


def _load_literal_arrays(path: Path) -> dict[str, list[float]]:
    """Read fixture list assignments without imports or arbitrary execution."""
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--generate-reference-data", action="store_true",
        help="regenerate the confirmed parameter table's reference fixtures",
    )
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

    # Example streaming usage on all 252 supplied closes, with the published
    # defaults. Each update returns one float, including the very first update.
    example = OneEuroFilter(period_min=10.0, beta=0.2)
    example_outputs = [example.update(close) for close in INPUT_CLOSE]
    print("Default output, first five values:",
          ", ".join(_float_literal(value, "NaN") for value in example_outputs[:5]))
    print("Confirmed reference cases (period_dx=10 is fixed):")
    for reference_case in REFERENCE_CASES:
        print(f"  EXPECTED_{_case_suffix(reference_case)}: {reference_case.what_it_tests}")

    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
