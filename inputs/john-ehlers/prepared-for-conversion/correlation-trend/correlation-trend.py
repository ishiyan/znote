"""Streaming research master for Ehlers' May 2020 Correlation Trend Indicator.

The article and Mesa paper call the calculation "Spearman", but their actual
code correlates raw prices with a time ramp: it is Pearson correlation.
This master follows that executable code, including its retained Corr when
either variance term is nonpositive. It does NOT rank or smooth prices.

A complete length-price trailing window produces the first output, so exactly
length-1 leading outputs are NaN. There is no artificial price prehistory.
Only standard Python is used. __main__ embeds the original 252 INPUT_CLOSE
values, demonstrates the default, and generates the confirmed fixture table.
See description.md for equations and source details.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class CorrelationTrendState(NamedTuple):
    """Read-only source sums and diagnostics for the most recent accepted bar.

    Diagnostic numeric fields are NaN before a full price window exists.
    variance_valid indicates whether the source correlation assignment ran.
    A full but flat/degenerate window is primed, yet variance_valid is False;
    correlation then holds the prior assigned value, initialized to zero.
    These fields are diagnostics; update() returns only the correlation float.
    """

    sum_x: float
    sum_y: float
    sum_xx: float
    sum_xy: float
    sum_yy: float
    numerator: float
    price_variance_term: float
    time_variance_term: float
    correlation: float
    variance_valid: bool


class CorrelationTrend:
    """Pearson correlation of a trailing price window with increasing time.

    length is a positive integer, excluding bool; default is the source's 20.
    Length 1 is supported literally: its time variance is zero, so every
    complete-window output retains the zero-initialized correlation. Use >=2
    for a meaningful correlation; at 2, unequal prices give approximately +/-1.

    Each update accepts one chronological finite float-convertible price.
    Zero and negative prices are valid. Invalid/nonfinite input and arithmetic
    outside the finite binary64 domain are rejected without advancing state.
    Construct a new instance to change length. Storage and update work are
    O(length), with no future observations and no accumulated running-sum drift.
    """

    def __init__(self, length: int = 20) -> None:
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError("length must be a positive integer")
        self._length = length
        self.reset()

    @property
    def length(self) -> int:
        """Read-only number of observed prices in each correlation window."""
        return self._length

    @property
    def warmup_bars(self) -> int:
        """Exact count of leading NaNs: no recursive smoother warmup is needed."""
        return self._length - 1

    @property
    def is_primed(self) -> bool:
        """Full window availability, independent of its price/time variance."""
        return len(self._prices) == self._length

    @property
    def state(self) -> CorrelationTrendState:
        """Expose source quantities without exposing mutable price history."""
        return self._state

    def reset(self) -> None:
        """Drop all prices and restore the article's initial Corr(0)."""
        self._prices = []
        self._corr = 0.0
        self._state = CorrelationTrendState(
            math.nan, math.nan, math.nan, math.nan, math.nan,
            math.nan, math.nan, math.nan, math.nan, False,
        )

    def update(self, value: float) -> float:
        """Consume one observation, returning Corr or unavailable-history NaN.

        Build a candidate window before calculation. Commit it only after all
        necessary arithmetic is checked, so a rejected bar changes no state.
        The current price is at lag zero; older prices are at increasing lags.
        """
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("input value must be finite")

        history = [value] + self._prices[:self._length - 1]
        if len(history) < self._length:
            # Incomplete history is unavailable, not a zero-padded window.
            # Public NaN never becomes the persistent source Corr variable.
            self._prices = history
            return math.nan

        # The source explicitly resets ALL FIVE sums on EVERY bar. Recompute
        # them from newest to oldest even though some time sums have closed
        # forms. This fixes operation order for reference conversion data.
        sx = 0.0
        sy = 0.0
        sxx = 0.0
        sxy = 0.0
        syy = 0.0
        for count in range(self._length):
            x = history[count]
            # Lag increases backward in time, so a negative lag represents a
            # line with positive chronological slope. Do not reverse its sign.
            y = -float(count)
            sx = sx + x
            sy = sy + y
            sxx = sxx + x * x
            sxy = sxy + x * y
            syy = syy + y * y

        # These are unnormalized variance/covariance terms; all common
        # population or sample divisors cancel out of Pearson's ratio.
        # Preserve the source multiplication/subtraction order. Centering first,
        # compensated sums, or running sums change floating-point reference data.
        price_variance = self._length * sxx - sx * sx
        time_variance = self._length * syy - sy * sy
        numerator = self._length * sxy - sx * sy
        if not all(math.isfinite(v) for v in (
                sx, sy, sxx, sxy, syy,
                price_variance, time_variance, numerator)):
            raise ValueError("correlation sums and variance terms must remain finite")

        correlation = self._corr
        variance_valid = price_variance > 0.0 and time_variance > 0.0
        if variance_valid:
            # Article/Mesa guard BOTH factors separately before sqrt.
            # The TradeStation function only tests its resulting denominator;
            # this master follows the safer literal article predicate.
            product = price_variance * time_variance
            if not math.isfinite(product) or product <= 0.0:
                raise ValueError("positive variance product must be finite and resolvable")
            correlation = numerator / math.sqrt(product)
            if not math.isfinite(correlation):
                raise ValueError("normalized correlation must remain finite")
            # No clamp: the original does not clamp near +/-1. Floating-point
            # cancellation can exceed the ideal range, especially at tiny price
            # variance or a very large price offset.
        # No Else assignment: a nonpositive factor retains the preceding Corr.
        # A first flat window and length 1 therefore yield 0, not a new NaN.

        self._prices = history
        self._corr = correlation
        self._state = CorrelationTrendState(
            sx, sy, sxx, sxy, syy, numerator,
            price_variance, time_variance, correlation, variance_valid,
        )
        return correlation


class ReferenceCase(NamedTuple):
    """One confirmed length and the exact portable 'What it tests' comment."""

    length: int
    what_it_tests: str


# User-confirmed coverage table for all five conversion fixture files.
# One scalar output per case; no trigger or strategy threshold is a parameter.
REFERENCE_CASES = (
    ReferenceCase(20, "Article and Mesa default twenty-bar trend horizon."),
    ReferenceCase(1, "Degenerate one-bar time ramp; source guard retains initial zero."),
    ReferenceCase(2, "Shortest nondegenerate window; direction saturates near plus or minus one."),
    ReferenceCase(3, "Shortest multi-point window and odd-length time indexing."),
    ReferenceCase(5, "Fast trend changes and short-window price ties."),
    ReferenceCase(10, "Article short-window example for trend onset and failure."),
    ReferenceCase(40, "Article smoother example and TradeStation slow strategy length."),
    ReferenceCase(60, "Article upper quarterly holding-period example."),
    ReferenceCase(126, "Half-record window for long-horizon trend shape."),
    ReferenceCase(251, "Nearly full-record window with exactly two primed outputs."),
    ReferenceCase(252, "Full-record window with exactly one primed output."),
    ReferenceCase(253, "Window exceeds the record; all 252 outputs remain NaN."),
)


def _float_literal(value: float, nan_literal: str) -> str:
    """Fifteen significant digits in fixture text; no state rounding."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("reference values cannot be infinite")
    literal = format(value, ".15g")
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _array_lines(values: list[float], indent: str, nan_literal: str) -> str:
    """Six floating-point values per row, with native NaN syntax."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return "\n".join(indent + ", ".join(literals[i:i + 6]) + ","
                     for i in range(0, len(literals), 6))


def _load_literal_arrays(path: Path) -> dict[str, list[float]]:
    """Read fixture lists with AST, without importing or executing data code."""
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
    """Append/replace only expected data; preserve the copied input section."""
    begin = f"{comment} BEGIN GENERATED CORRELATION TREND EXPECTED DATA"
    end = f"{comment} END GENERATED CORRELATION TREND EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    generated = begin + "\n\n" + section.rstrip() + "\n\n" + end + "\n"
    if begin in original or end in original:
        if original.count(begin) != 1 or original.count(end) != 1:
            raise ValueError(f"malformed generated markers in {path.name}")
        start, finish = original.index(begin), original.index(end)
        if finish < start:
            raise ValueError(f"reversed generated markers in {path.name}")
        result = original[:start] + generated.rstrip("\n") + original[finish + len(end):]
    else:
        result = original.rstrip() + "\n\n" + generated
    path.write_text(result, encoding="utf-8")


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Calculate/write/verify confirmed Python data, then export its values.

    Renderer tooling is separate from the scalar streaming class. Ports only
    need the class, initialization and arithmetic described above.
    """
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 prices and one through 64 parameter cases")
    if len({case.length for case in REFERENCE_CASES}) != len(REFERENCE_CASES):
        raise ValueError("reference lengths must be unique")
    python_path = directory / "test_testdata.py"
    original_inputs = {name: values for name, values in _load_literal_arrays(python_path).items()
                       if name.startswith("INPUT_")}
    if original_inputs.get("INPUT_CLOSE") != input_close:
        raise ValueError("embedded closes differ from the copied input fixture")
    raw = {}
    sections = []
    for case in REFERENCE_CASES:
        indicator = CorrelationTrend(case.length)
        values = [indicator.update(value) for value in input_close]
        name = f"EXPECTED_L{case.length}"
        raw[name] = (values, indicator.warmup_bars)
        sections.append(f"# {case.what_it_tests}\n# length={case.length}\n{name} = [\n"
                        + _array_lines(values, "    ", "math.nan") + "\n]")
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # Reopen and verify the actual Python output BEFORE translating it.
    written = _load_literal_arrays(python_path)
    if {name: written[name] for name in original_inputs} != original_inputs:
        raise ValueError("input arrays changed during generation")
    if {name for name in written if name.startswith("EXPECTED_")} != set(raw):
        raise ValueError("missing or unexpected expected arrays")
    for name, (values, warmup) in raw.items():
        if len(written[name]) != 252:
            raise ValueError(f"{name} must have exactly 252 values")
        for index, (before, after) in enumerate(zip(values, written[name])):
            if index < warmup:
                if not math.isnan(before) or not math.isnan(after):
                    raise ValueError(f"{name} has an incorrect NaN prefix")
            elif not math.isfinite(after) or after != float(_float_literal(before, "nan")):
                raise ValueError(f"{name} failed fifteen-digit precision verification")

    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text().replace("package xxxx", "package correlationtrend", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package correlationtrend\n", 'package correlationtrend\n\nimport "math"\n', 1)
    go_path.write_text(go_text)
    zig_path = directory / "testdata.zig"
    zig_text = zig_path.read_text()
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n' + zig_text
    if "const nan = math.nan(f64);" not in zig_text:
        zig_text = zig_text.replace('const math = @import("std").math;\n',
                                   'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(zig_text)

    native = {"go": [], "ts": [], "rs": [], "zig": []}
    for case in REFERENCE_CASES:
        suffix = f"L{case.length}"
        values = written["EXPECTED_" + suffix]
        comments = f"// {case.what_it_tests}\n// length={case.length}\n"
        native["go"].append(comments + f"var expected{suffix} = []float64{{\n"
                            + _array_lines(values, "\t", "math.NaN()") + "\n}")
        native["ts"].append(comments + f"export const expected{suffix}: number[] = [\n"
                            + _array_lines(values, "    ", "NaN") + "\n];")
        native["rs"].append(comments + f"pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n"
                            + _array_lines(values, "        ", "f64::NAN") + "\n    ]\n}")
        native["zig"].append(comments + f"pub fn expected{suffix}() [252]f64 {{\n    return .{{\n"
                             + _array_lines(values, "        ", "nan") + "\n    };\n}")
    for language, filename in (("go", "testdata_test.go"), ("ts", "testdata.ts"),
                               ("rs", "testdata.rs"), ("zig", "testdata.zig")):
        path = directory / filename
        if language == "rs" and "BEGIN GENERATED CORRELATION TREND EXPECTED DATA" not in path.read_text():
            # Insert functions inside the original #[cfg(test)] testdata module.
            rust_text = path.read_text()
            final_brace = rust_text.rfind("}")
            if final_brace < 0 or rust_text[final_brace + 1:].strip():
                raise ValueError("Rust fixture must end with its module brace")
            path.write_text(rust_text[:final_brace])
            _write_generated_section(path, "\n\n".join(native[language]), "//")
            path.write_text(path.read_text() + "}\n")
        else:
            _write_generated_section(path, "\n\n".join(native[language]), "//")
    print(f"Verified {len(raw)} CorrelationTrend arrays of 252 values; wrote all five language fixtures.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true",
                        help="regenerate the confirmed 12-case table in all five languages")
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
        indicator = CorrelationTrend()  # Published Length(20), one scalar output.
        outputs = [indicator.update(close) for close in INPUT_CLOSE]
        print(f"CorrelationTrend length={indicator.length}; {len(INPUT_CLOSE)} input observations")
        print(f"First {indicator.warmup_bars} outputs are NaN")
        print(f"First available [{indicator.warmup_bars}]: {outputs[indicator.warmup_bars]:.15g}")
        print(f"Final value: {outputs[-1]:.15g}")
        print("Latest diagnostics:", indicator.state)
        indicator.reset()
        print("Primed after reset:", indicator.is_primed)
        print(f"Confirmed lengths: {[case.length for case in REFERENCE_CASES]}")
