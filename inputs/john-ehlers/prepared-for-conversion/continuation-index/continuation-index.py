"""Streaming master reference for Ehlers' September 2025 Continuation Index.

Algorithm: the article's EasyLanguage equations, also printed in its Mesa paper,
with full-precision pi and sqrt(2) constants as requested by the user.
The Python Traders' Tip uses centered convolution (future data), so it cannot
serve as the authority for the causal streaming normalization requested here.
See description.md for a complete definition of constants and startup history.

Only the standard library is used. Run without flags to demonstrate the default
indicator on the embedded 252 closes and print the confirmed reference cases.
Use --generate-reference-data to regenerate all five fixture files.
The file-rendering utilities are tooling; a language port only needs the filter
classes, inverse Fisher transform, and the documented constants.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# Use the binary64 values of the mathematical constants, as requested by the
# user. These replace the article's printed approximations 3.14159 and 1.414.
# All language ports and expected fixtures must use this full-precision policy.
EHLERS_PI = math.pi
EHLERS_SQRT_TWO = math.sqrt(2.0)


def _positive_integer(value: int, name: str) -> int:
    """Reject truncation of fractional window lengths or orders, and booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


class UltimateSmoother:
    """Two-pole UltimateSmoother with full-precision coefficient constants.

    The first three inputs pass through. Zero-based t=3 corresponds to the
    article's first recursive bar, CurrentBar=4. Both input and output history
    are populated by those pass-through samples. Period can be fractional.
    """

    def __init__(self, period: float) -> None:
        self.period = float(period)
        if not math.isfinite(self.period) or self.period <= 0.0:
            raise ValueError("period must be finite and positive")
        # One full-precision radian angle sets both pole damping and rotation.
        # This is the degree-based source formula expressed directly in radians.
        angle = EHLERS_SQRT_TWO * EHLERS_PI / self.period
        q = math.exp(-angle)
        self._c1 = 2.0 * q * math.cos(angle)
        self._c2 = q * q
        self._a0 = (1.0 + self._c1 + self._c2) / 4.0
        self.reset()

    def reset(self) -> None:
        """Only four historical scalars and a sample count are needed."""
        self._count = 0
        self._price1 = self._price2 = 0.0
        self._output1 = self._output2 = 0.0

    def update(self, price: float) -> float:
        """Consume one sample using prior input/output histories, then shift."""
        price = float(price)
        if not math.isfinite(price):
            raise ValueError("price must be finite")
        if self._count < 3:
            # No future or synthetic price history is used on the first bars.
            output = price
        else:
            # Source order matters for cross-language floating-point agreement.
            # Keep the recurrence's arithmetic order and avoid forced FMA.
            output = (
                (1.0 - self._a0) * price
                + (2.0 * self._a0 - self._c1) * self._price1
                + (self._c2 - self._a0) * self._price2
                + self._c1 * self._output1
                - self._c2 * self._output2
            )
        # Shift oldest first. A port must not overwrite yesterday's price or
        # output until today's recurrence has finished using both histories.
        self._price2, self._price1 = self._price1, price
        self._output2, self._output1 = self._output1, output
        self._count += 1
        return output


class LaguerreFilter:
    """The article's zero-seeded, delayed component bank, not a replacement.

    A conventional Laguerre allpass recurrence uses a CURRENT preceding stage
    in one term. This listing uses the PREVIOUS preceding stage in both terms.
    Preserve that published recurrence; see the discrepancy analysis in the
    documentation. order=1 reduces to the length-period UltimateSmoother.
    """

    def __init__(self, gama: float = 0.8, order: int = 8, length: int = 40) -> None:
        self.gama = float(gama)
        if not math.isfinite(self.gama) or not 0.0 <= self.gama < 1.0:
            raise ValueError("gama must be finite and in [0, 1)")
        self.order = _positive_integer(order, "order")
        if self.order > 10:
            raise ValueError("order must be at most 10")
        self.length = _positive_integer(length, "length")
        self._smoother = UltimateSmoother(self.length)
        self.reset()

    def reset(self) -> None:
        """The source LG array starts at zero, including all later components."""
        self._smoother.reset()
        self._components = [0.0] * self.order

    def update(self, price: float) -> float:
        """Create today's stages from a snapshot of yesterday's entire bank."""
        smoothed_price = self._smoother.update(price)
        previous = self._components
        current = [0.0] * self.order
        current[0] = smoothed_price
        for index in range(1, self.order):
            # Both occurrences of previous[index-1] are intentional. Keep the
            # two terms separate rather than rewriting as (1-gama)*previous.
            current[index] = (
                -self.gama * previous[index - 1]
                + previous[index - 1]
                + self.gama * previous[index]
            )
        # Sum in increasing stage order, as in the original FIR loop.
        total = 0.0
        for component in current:
            total += component
        self._components = current
        return total / self.order


def inverse_fisher(ref: float) -> float:
    """Evaluate the article's exponential ratio, with an overflow-safe fallback.

    The ordinary path preserves its exp/subtract/add/divide arithmetic. For an
    unusually large positive reference, the original exp could overflow; its
    inverse Fisher ratio is already 1 to binary64 precision. Only that overflow
    path uses an equivalent expression with a negative exponent.
    """
    exponent = 2.0 * ref
    try:
        exp_value = math.exp(exponent)
    except OverflowError:
        exp_value = math.exp(-exponent)
        return (1.0 - exp_value) / (1.0 + exp_value)
    return (exp_value - 1.0) / (exp_value + 1.0)


class ContinuationIndex:
    """Return one CI float per input; NaN until a full trailing window exists.

    Defaults are gama=0.8, order=8, length=40. The gamma spelling follows the
    source, where 'gamma' was a reserved word. length is a positive integer;
    order is an integer in [1,10]; gama is finite in [0,1).

    The first length-1 outputs are NaN. Filters and the absolute-difference ring
    still advance on those bars. The length-th sample produces the first CI.
    A zero denominator retains the previous normalized reference, initialized
    to zero, following the source's conditional assignment to Ref.
    """

    def __init__(self, gama: float = 0.8, order: int = 8, length: int = 40) -> None:
        # Validate through the component constructor and expose its exact
        # configuration. Construct a fresh object to change any parameters.
        self._laguerre = LaguerreFilter(gama, order, length)
        self.gama = self._laguerre.gama
        self.order = self._laguerre.order
        self.length = self._laguerre.length
        # True division is essential for odd lengths: 21 / 2 is 10.5, not 10.
        self._fast = UltimateSmoother(self.length / 2.0)
        self.reset()

    @property
    def warmup_bars(self) -> int:
        """Exact number of leading unprimed NaN values in fixture arrays."""
        return self.length - 1

    @property
    def is_primed(self) -> bool:
        """A full mean-absolute-difference window makes CI defined."""
        return self._count >= self.length

    def reset(self) -> None:
        """Reset every recursive component, ring element, and held Ref."""
        self._fast.reset()
        self._laguerre.reset()
        self._differences = [0.0] * self.length
        self._next_slot = 0
        self._count = 0
        self._ref = 0.0

    def update(self, price: float) -> float:
        """Run both filters, maintain the causal window, normalize and compress."""
        price = float(price)
        if not math.isfinite(price):
            # Reject before changing either child filter or the ring buffer.
            raise ValueError("price must be finite")
        fast = self._fast.update(price)
        slow = self._laguerre.update(price)
        difference = fast - slow

        # Store ALL observed differences, including startup values. Never place
        # the public NaN into a recursive filter or into the rolling window.
        self._differences[self._next_slot] = abs(difference)
        self._next_slot = (self._next_slot + 1) % self.length
        self._count += 1
        if not self.is_primed:
            return math.nan

        # A direct newest-to-oldest sum specifies the reference's exact order.
        # It avoids accumulated drift from subtracting the outgoing sample of
        # a running sum. Streaming does not require constant update time: this
        # scan is O(length), uses bounded storage, and reads no future inputs.
        total = 0.0
        for offset in range(self.length):
            index = (self._next_slot - 1 - offset) % self.length
            total += self._differences[index]
        variance = total / self.length

        # 'Variance' is the article's name, but the quantity is a MEAN ABSOLUTE
        # FILTER DIFFERENCE, not a squared statistical variance. Do not square
        # differences, apply a square root, or replace it with price volatility.
        if variance != 0.0:
            self._ref = 2.0 * difference / variance
        # No else: retain Ref exactly as the EasyLanguage series variable does.
        return inverse_fisher(self._ref)


class ReferenceCase(NamedTuple):
    """One confirmed case; its description becomes the first fixture comment."""

    gama: float
    order: int
    length: int
    what_it_tests: str


# Sixteen targeted cases rather than an unnecessarily large Cartesian grid.
# These cover the default, article figure comparisons, half-period division,
# slow memory, degenerate stages, and the exact full-window startup boundary.
REFERENCE_CASES = (
    ReferenceCase(0.8, 8, 40, "Article defaults: eighth-order trend reference and forty-bar normalization."),
    ReferenceCase(0.8, 8, 20, "One-month horizon: shorter smoothing and normalization window."),
    ReferenceCase(0.8, 8, 60, "Quarter-length horizon: longer smoothing and normalization window."),
    ReferenceCase(0.8, 8, 21, "Odd length: fast UltimateSmoother period must be 10.5 bars."),
    ReferenceCase(0.8, 8, 2, "Short two-bar window: early priming and strongly saturated output."),
    ReferenceCase(0.8, 8, 252, "Full-input window: 251 NaNs followed by exactly one primed output."),
    ReferenceCase(0.0, 8, 40, "Gamma zero: preserve the published delayed-component FIR behavior."),
    ReferenceCase(0.4, 8, 40, "Article gamma comparison: faster stage relaxation at gamma 0.4."),
    ReferenceCase(0.95, 8, 40, "High gamma: persistent component memory and a long startup transient."),
    ReferenceCase(0.999, 8, 40, "Gamma near one: slow component filling while remaining in the valid domain."),
    ReferenceCase(0.8, 1, 40, "Order one: slow filter reduces to the full-length UltimateSmoother."),
    ReferenceCase(0.8, 2, 40, "Order two: smallest nontrivial delayed component bank."),
    ReferenceCase(0.8, 4, 40, "Article order comparison: fourth-order rather than eighth-order trend reference."),
    ReferenceCase(0.8, 10, 40, "Maximum supported order: exercise all ten components."),
    ReferenceCase(0.0, 1, 40, "Gamma zero and order one: isolate the two different UltimateSmoother periods."),
    ReferenceCase(0.4, 4, 20, "Combined fast configuration: low gamma, lower order, and short length."),
)


def _parameter_token(value: float) -> str:
    """Make portable names: 0.2 -> 0_2, -0.2 -> m0_2, 10.0 -> 10."""
    # A minus sign is invalid in an identifier, so 'm' denotes minus. Keep
    # integral parameter values compact; fixtures themselves always use floats.
    return format(value, "g").replace("-", "m").replace(".", "_")


def _case_suffix(case: ReferenceCase) -> str:
    """G = gama, O = order, L = length; decimals use underscores."""
    return f"G{_parameter_token(case.gama)}_O{case.order}_L{case.length}"


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
    begin = f"{comment} BEGIN GENERATED CONTINUATION INDEX EXPECTED DATA"
    end = f"{comment} END GENERATED CONTINUATION INDEX EXPECTED DATA"
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
        indicator = ContinuationIndex(case.gama, case.order, case.length)
        values = [indicator.update(price) for price in input_close]
        name = "EXPECTED_" + _case_suffix(case)
        raw_outputs[name] = values
        python_sections.append(
            f"# {case.what_it_tests}\n"
            f"# gama={case.gama:g}, order={case.order}, length={case.length}\n"
            f"{name} = [\n{_array_lines(values, '    ', 'math.nan')}\n]"
        )
    _write_generated_section(python_path, "\n\n".join(python_sections), "#")

    # Read the written Python arrays back and check count, length, and precision
    # before appending them to other languages. Leading NaNs represent the
    # exact length-1 warm-up; each language must preserve their positions.
    written_arrays = _load_literal_arrays(python_path)
    expected_names = {name for name in written_arrays if name.startswith("EXPECTED_")}
    if expected_names != set(raw_outputs):
        raise ValueError("unexpected or missing Python expected array names")
    for name, raw in raw_outputs.items():
        written = written_arrays[name]
        if len(written) != 252:
            raise ValueError(f"{name} does not contain 252 outputs")
        case = next(case for case in REFERENCE_CASES if "EXPECTED_" + _case_suffix(case) == name)
        for index, value in enumerate(written):
            if math.isnan(value) != (index < case.length - 1):
                raise ValueError(f"{name} has an incorrect NaN warm-up at index {index}")
        for before, after in zip(raw, written):
            if math.isnan(before) and math.isnan(after):
                continue
            if not math.isclose(before, after, rel_tol=5e-14, abs_tol=5e-14):
                raise ValueError(f"{name} did not retain 15-digit precision")

    # Go fixtures use math.NaN() for every unprimed output. Ensure the import
    # exists even when generating directly from a pristine copied template.
    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8").replace(
        "package xxxx", "package thecontinuationindex", 1
    )
    if 'import "math"' not in go_text:
        go_text = go_text.replace(
            "package thecontinuationindex\n",
            'package thecontinuationindex\n\nimport "math"\n\n'
            '// Reference fixtures use this for unprimed outputs.\n'
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
            f"// gama={case.gama:g}, order={case.order}, length={case.length}\n"
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
        help="regenerate the confirmed reference arrays in all five languages",
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

    # Example: one update call per observed close. Even unprimed bars must be
    # submitted so the internal state is ready when the trailing window fills.
    example = ContinuationIndex(gama=0.8, order=8, length=40)
    example_outputs = [example.update(close) for close in INPUT_CLOSE]
    print("Default leading NaN count:", example.warmup_bars)
    print("First five primed outputs:", ", ".join(
        _float_literal(value, "NaN")
        for value in example_outputs[example.warmup_bars:example.warmup_bars + 5]
    ))
    print("Confirmed reference cases:")
    for case in REFERENCE_CASES:
        print(f"  EXPECTED_{_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
