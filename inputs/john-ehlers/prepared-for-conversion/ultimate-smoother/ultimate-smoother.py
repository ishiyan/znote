"""Streaming master reference for Ehlers' April 2024 Ultimate Smoother.

The algorithm and arithmetic order follow the article's UltimateSmoother
function. Full-precision math.pi and math.sqrt(2.0) replace its printed constant
approximations, carrying forward the user's preference from the Continuation
Index reference. See description.md for full theory and platform differences.

No third-party packages are required. The filter stores only two previous raw
prices, two previous outputs, and a startup count. A single update returns a
single float. The first three samples pass through, so no NaN prefix is needed.

Run without flags to process the embedded 252 INPUT_CLOSE values and display
the confirmed parameter cases. Run with
--generate-reference-data to append reference outputs to all five fixture files.
File-generation helpers below the class are tooling and need not be ported.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# Binary64 mathematical constants, rather than the printed 3.14159 and 1.414.
# A port should use its standard pi constant and sqrt(2.0), not rounded decimals.
PI = math.pi
SQRT_TWO = math.sqrt(2.0)


class UltimateSmoother:
    """Second-order lowpass formed by subtracting a highpass from raw input.

    period is a finite real number >= 1.0, measured in bars; default 20.0.
    Fractional periods are supported. This is a coefficient-setting parameter,
    not a rolling window length and not a required count of warm-up observations.

    The first three successful updates return their input unchanged. Thereafter
    the article's recurrence uses two previous raw prices and two previous
    outputs. All samples are consumed once, chronologically, without look-ahead.
    """

    def __init__(self, period: float = 20.0) -> None:
        self._period = float(period)
        # The supplied NinjaTrader UI uses a minimum period of one. The article
        # does not specify a minimum; this API accepts fractional periods >= 1.
        if not math.isfinite(self._period) or self._period < 1.0:
            raise ValueError("period must be finite and at least 1.0")

        # Full-precision radian form of the source's degree-based coefficients.
        # Compute this angle once; its negative sets the pole radius and its
        # cosine sets the pole rotation. Both child poles have radius a1 < 1.
        angle = SQRT_TWO * PI / self._period
        a1 = math.exp(-angle)
        b1 = 2.0 * a1 * math.cos(angle)

        # Keep the article's April 2024 names and signs. In particular c3 is
        # NEGATIVE, so the last recurrence term is +c3*previous_previous_output.
        self._c2 = b1
        self._c3 = -a1 * a1
        self._c1 = (1.0 + self._c2 - self._c3) / 4.0
        self.reset()

    @property
    def period(self) -> float:
        """Read-only configuration; construct another filter to change period."""
        return self._period

    @property
    def is_primed(self) -> bool:
        """True after the first update, since startup outputs are defined."""
        return self._count > 0

    @property
    def warmup_bars(self) -> int:
        """Number of leading NaN outputs: zero for the article's pass-through."""
        return 0

    def reset(self) -> None:
        """Clear histories; the next three observations will pass through."""
        self._count = 0
        # These initial zero histories are never read by the recursive formula:
        # the first three pass-through samples fill them before recursion starts.
        self._price1 = self._price2 = 0.0
        self._output1 = self._output2 = 0.0

    def update(self, price: float) -> float:
        """Consume one finite price and return this bar's smoothed price."""
        price = float(price)
        if not math.isfinite(price):
            # Check before any state changes. Do not silently fill missing bars.
            raise ValueError("price must be finite")

        if self._count < 3:
            # With standalone CurrentBar=count+1, the article's CurrentBar<4
            # branch applies to indices 0, 1, and 2. It assigns US=Price.
            output = price
        else:
            # Exactly the article's direct-form recurrence, with today's Price
            # and the two PRIOR raw inputs and outputs. Do not overwrite any of
            # those values until the entire expression has been evaluated.
            output = (
                (1.0 - self._c1) * price
                + (2.0 * self._c1 - self._c2) * self._price1
                - (self._c1 + self._c3) * self._price2
                + self._c2 * self._output1
                + self._c3 * self._output2
            )

        # Reject arithmetic overflow before committing. Ordinary finite prices
        # in the fixtures never take this branch. A rejected input does not
        # advance the successful-sample count or either history.
        if not math.isfinite(output):
            raise ValueError("filtered output must be finite")

        # Shift older values before assigning current values. Tuple assignment
        # makes simultaneous history updates explicit in this Python reference.
        self._price2, self._price1 = self._price1, price
        self._output2, self._output1 = self._output1, output
        self._count += 1
        return output


class ReferenceCase(NamedTuple):
    """One confirmed period and its required 'What it tests' fixture comment."""

    period: float
    what_it_tests: str


# Twelve targeted periods cover the lower boundary, short critical periods,
# fractional-period arithmetic, the article default, and long pole memory.
REFERENCE_CASES = (
    ReferenceCase(1.0, "Minimum supported period: valid coefficients and defined startup at one bar."),
    ReferenceCase(2.0, "Nyquist-period boundary: shortest two-bar critical period."),
    ReferenceCase(3.0, "Very short period: fast damping and strong direct-input contribution."),
    ReferenceCase(5.0, "Short-period smoothing: rapid response to price changes."),
    ReferenceCase(8.0, "Intermediate short period: transition between rapid and moderate damping."),
    ReferenceCase(10.5, "Fractional period: preserve real-valued coefficient calculation without truncation."),
    ReferenceCase(15.0, "Fifteen-bar period used as the fast band edge in the article's comparison."),
    ReferenceCase(20.0, "Article and Traders' Tips default: twenty-bar critical period."),
    ReferenceCase(30.0, "Thirty-bar period used in the Zorro smoother comparison."),
    ReferenceCase(40.0, "Longer smoothing horizon: slower pole damping and reversal response."),
    ReferenceCase(60.0, "Quarter-length horizon: sustained filter memory over daily bars."),
    ReferenceCase(252.0, "Full-record-length period: long memory while startup outputs remain immediately valid."),
)


def _parameter_token(value: float) -> str:
    """Make portable names: 0.2 -> 0_2, -0.2 -> m0_2, 10.0 -> 10."""
    # A minus sign is invalid in an identifier, so 'm' denotes minus. Keep
    # integral parameter values compact; fixtures themselves always use floats.
    return format(value, "g").replace("-", "m").replace(".", "_")


def _case_suffix(case: ReferenceCase) -> str:
    """P = period; decimal points become underscores in portable identifiers."""
    return f"P{_parameter_token(case.period)}"


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
    begin = f"{comment} BEGIN GENERATED ULTIMATE SMOOTHER EXPECTED DATA"
    end = f"{comment} END GENERATED ULTIMATE SMOOTHER EXPECTED DATA"
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
        indicator = UltimateSmoother(case.period)
        values = [indicator.update(price) for price in input_close]
        name = "EXPECTED_" + _case_suffix(case)
        raw_outputs[name] = values
        python_sections.append(
            f"# {case.what_it_tests}\n"
            f"# period={case.period:g}\n"
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
        if any(not math.isfinite(value) for value in written):
            raise ValueError(f"{name} must have no NaN prefix because startup outputs pass through")
        for before, after in zip(raw, written):
            if math.isnan(before) and math.isnan(after):
                continue
            if not math.isclose(before, after, rel_tol=5e-14, abs_tol=5e-14):
                raise ValueError(f"{name} did not retain 15-digit precision")

    # Go requires a used import. There are no warm-up NaNs in this indicator,
    # so a blank reference keeps the specifically requested math import valid.
    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8").replace(
        "package xxxx", "package ultimatesmoother", 1
    )
    if 'import "math"' not in go_text:
        go_text = go_text.replace(
            "package ultimatesmoother\n",
            'package ultimatesmoother\n\nimport "math"\n\n'
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
            f"// period={case.period:g}\n"
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
        help="regenerate the confirmed reference cases in all five languages",
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

    # Example streaming usage: feed all 252 closes, one call per observed bar.
    # The first three returned values are the source's explicit pass-through;
    # subsequent returned values come from the second-order recursive filter.
    indicator = UltimateSmoother(period=20.0)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print("Default first five outputs:", ", ".join(
        _float_literal(value, "NaN") for value in outputs[:5]
    ))
    print("Confirmed reference cases:")
    for case in REFERENCE_CASES:
        print(f"  EXPECTED_{_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
