"""Correlation Angle, Ehlers June 2020: streaming research master.

Two Pearson correlations (price/cosine and price/negative sine) feed the article's
literal degree-valued arctangent, 270-degree backward-step guard, and fixed
9-degree market-state test. No atan2 replacement or circular-difference rewrite.
Full-precision math.pi supplies the trigonometric arguments, as requested.

update(value) returns CorrelationAngleOutput(real, imag, angle, state).
Defaults period=20, input_period=20 reproduce the article's synthetic test mode.
input_period=0 consumes prices; positive input_period replaces each accepted
input with sin(2*pi*CurrentBar/input_period), starting CurrentBar at 1.
A full period-price window is required: period-1 leading output tuples are NaN.
See description.md for complete equations, startup, and source discrepancies.

Only standard Python is used. __main__ embeds the required 252 INPUT_CLOSE
values, demonstrates price and synthetic modes, and generates reference data
for the confirmed cases.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# The article expresses trigonometric arguments in degrees. Use this exact
# radian operation order in every port; never restore the NinjaTrader 6.28
# and 1.57 constants. sqrt(2) is not needed by this indicator.
PI = math.pi


class CorrelationAngleOutput(NamedTuple):
    """All four source series; angle is in degrees, state is -1, 0, or +1.

    Each field is NaN until a complete observed-price window exists. State is
    represented as float so it can share that availability convention; finite
    state outputs are exactly -1.0, 0.0, or 1.0.
    """

    real: float
    imag: float
    angle: float
    state: float


class CorrelationSums(NamedTuple):
    """Read-only source diagnostics for one template correlation."""

    sum_x: float
    sum_y: float
    sum_xx: float
    sum_xy: float
    sum_yy: float
    numerator: float
    price_variance_term: float
    template_variance_term: float
    variance_valid: bool


class CorrelationAngleDiagnostics(NamedTuple):
    """Diagnostics only; expected arrays cover the four output fields."""

    price: float
    real_sums: CorrelationSums
    imag_sums: CorrelationSums
    candidate_angle: float
    was_held: bool


def _phase_step(real: float, imag: float, previous: float) -> tuple[float, float, bool, float]:
    """Literal sequential EasyLanguage angle and state assignments.

    Imag=0 does not assign Angle: retain the preceding stored angle. The second
    conditional is independent. The final guard allows negative jumps >=270
    degrees (interpreted as wrap) and holds smaller backward steps.
    """
    angle = previous
    if imag != 0.0:
        angle = 90.0 + (180.0 / PI) * math.atan(real / imag)
    if imag > 0.0:
        angle = angle - 180.0
    candidate = angle
    held = previous - angle < 270.0 and angle < previous
    if held:
        angle = previous

    # Raw ABSOLUTE displayed difference, not a circularly unwrapped advance.
    # Equality at 9 degrees is cycle state, because the source uses strict <.
    state = 0.0
    if abs(angle - previous) < 9.0 and angle < 0.0:
        state = -1.0
    if abs(angle - previous) < 9.0 and angle >= 0.0:
        state = 1.0
    return angle, candidate, held, state


class CorrelationAngle:
    """Streaming four-series source master; O(period) work and bounded history.

    period is a positive integer, excluding bool. input_period is a finite
    nonnegative number: zero selects raw input, positive selects a synthetic
    sinusoid. Fractional synthetic periods are allowed by the article's numeric
    input. Periods >=3 are needed for meaningful sampled quadrature; 1 and 2
    preserve literal degeneracy/roundoff behavior rather than inventing data.

    Each call consumes one chronological finite float-convertible observation.
    Even synthetic mode validates the observation; it provides a stream clock.
    Invalid input and nonfinite calculation are rejected without advancing state.
    """

    def __init__(self, period: int = 20, input_period: float = 20.0) -> None:
        if isinstance(period, bool) or not isinstance(period, int) or period < 1:
            raise ValueError("period must be a positive integer")
        if isinstance(input_period, bool):
            raise ValueError("input_period must be finite and nonnegative")
        input_period = float(input_period)
        if not math.isfinite(input_period) or input_period < 0.0:
            raise ValueError("input_period must be finite and nonnegative")
        self._period = period
        self._input_period = input_period

        # Templates are fixed for this configuration. Compute each coefficient
        # once with the same expression the source evaluates on every bar.
        # Do not snap tiny sin(pi) residues to zero; that would change the source.
        self._cosine = []
        self._negative_sine = []
        for lag in range(period):
            argument = 2.0 * PI * lag / period
            self._cosine.append(math.cos(argument))
            self._negative_sine.append(-math.sin(argument))
        self.reset()

    @property
    def period(self) -> int:
        return self._period

    @property
    def input_period(self) -> float:
        return self._input_period

    @property
    def warmup_bars(self) -> int:
        """Count of leading all-NaN output tuples, not extra phase settling."""
        return self._period - 1

    @property
    def is_primed(self) -> bool:
        """Full window availability; correlation variance may still be zero."""
        return len(self._prices) == self._period

    @property
    def last_output(self) -> CorrelationAngleOutput:
        return self._last_output

    @property
    def diagnostics(self) -> CorrelationAngleDiagnostics:
        return self._diagnostics

    def reset(self) -> None:
        """Reset the entire stream and zero-seeded Real, Imag, and Angle."""
        self._prices = []
        self._count = 0
        self._real = 0.0
        self._imag = 0.0
        self._angle = 0.0
        self._last_output = CorrelationAngleOutput(*(math.nan,) * 4)
        unavailable = CorrelationSums(*(math.nan,) * 8, False)
        self._diagnostics = CorrelationAngleDiagnostics(
            math.nan, unavailable, unavailable, math.nan, False,
        )

    def _correlate(self, history: list[float], template: list[float],
                   previous: float) -> tuple[float, CorrelationSums]:
        """Recompute the complete five-sum Pearson loop in source lag order."""
        sx = 0.0
        sy = 0.0
        sxx = 0.0
        sxy = 0.0
        syy = 0.0
        for lag in range(self._period):
            x = history[lag]
            y = template[lag]
            sx = sx + x
            sy = sy + y
            sxx = sxx + x * x
            sxy = sxy + x * y
            syy = syy + y * y
        price_variance = self._period * sxx - sx * sx
        template_variance = self._period * syy - sy * sy
        numerator = self._period * sxy - sx * sy
        if not all(math.isfinite(v) for v in (
                sx, sy, sxx, sxy, syy, numerator, price_variance, template_variance)):
            raise ValueError("correlation sums must remain finite")
        valid = price_variance > 0.0 and template_variance > 0.0
        result = previous
        if valid:
            product = price_variance * template_variance
            if not math.isfinite(product) or product <= 0.0:
                raise ValueError("positive correlation variance product must be finite and resolvable")
            result = numerator / math.sqrt(product)
            if not math.isfinite(result):
                raise ValueError("correlation must remain finite")
        # No Else: a flat/nonpositive-variance window retains its preceding
        # component. The two components retain independently, as in the source.
        sums = CorrelationSums(sx, sy, sxx, sxy, syy, numerator,
                               price_variance, template_variance, valid)
        return result, sums

    def update(self, value: float) -> CorrelationAngleOutput:
        """Consume one accepted bar and atomically commit all four source series."""
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("input value must be finite")
        price = value
        if self._input_period != 0.0:
            # EasyLanguage CurrentBar is specified as one-based for this finite
            # record. Invalid/rejected updates do not advance this counter.
            argument = 2.0 * PI * (self._count + 1) / self._input_period
            if not math.isfinite(argument):
                raise ValueError("synthetic sinusoid argument must remain finite")
            price = math.sin(argument)
        history = [price] + self._prices[:self._period - 1]
        if len(history) < self._period:
            self._prices = history
            self._count += 1
            self._diagnostics = self._diagnostics._replace(price=price)
            return self._last_output

        # Use two separate loops and separate held states. Combining them or
        # replacing raw moments with centered/compensated sums changes rounding.
        real, real_sums = self._correlate(history, self._cosine, self._real)
        imag, imag_sums = self._correlate(history, self._negative_sine, self._imag)
        angle, candidate, held, state = _phase_step(real, imag, self._angle)
        if not math.isfinite(angle):
            raise ValueError("phase angle must remain finite")
        output = CorrelationAngleOutput(real, imag, angle, state)

        # Public NaNs never become recursive component or previous-angle state.
        # Commit only after BOTH correlations and the angle/state have succeeded.
        self._prices = history
        self._count += 1
        self._real = real
        self._imag = imag
        self._angle = angle
        self._last_output = output
        self._diagnostics = CorrelationAngleDiagnostics(
            price, real_sums, imag_sums, candidate, held,
        )
        return output


class ReferenceCase(NamedTuple):
    """One confirmed configuration; comment text is copied into every fixture."""

    period: int
    input_period: float
    what_it_tests: str


# All sixteen cases were confirmed by the user for four-output reference data.
REFERENCE_CASES = (
    ReferenceCase(20, 20.0, "Article default: matched twenty-bar synthetic sinusoid."),
    ReferenceCase(14, 0.0, "TradeStation default and article real-price fourteen-bar example."),
    ReferenceCase(20, 0.0, "Price-driven twenty-bar cycle, angle holds, and market states."),
    ReferenceCase(10, 0.0, "Fast price-driven ten-bar assumed cycle."),
    ReferenceCase(40, 0.0, "Forty-bar price cycle at the fixed nine-degree trend threshold."),
    ReferenceCase(60, 0.0, "Slow price cycle and long-window phase behavior."),
    ReferenceCase(3, 0.0, "Shortest meaningful sampled quadrature window."),
    ReferenceCase(4, 0.0, "Four-bar quadrature with near-axis trigonometric values."),
    ReferenceCase(5, 0.0, "Short odd cycle and nonsymmetric lag sampling."),
    ReferenceCase(252, 0.0, "Full-record price window with exactly one primed output."),
    ReferenceCase(253, 0.0, "Price window exceeds the record; all 252 outputs remain NaN."),
    ReferenceCase(20, 21.0, "Article near-match synthetic detuning from twenty to twenty-one bars."),
    ReferenceCase(20, 30.0, "Article stress test: actual cycle fifty percent longer than assumed."),
    ReferenceCase(20, 15.0, "Article stress test: actual cycle twenty-five percent shorter than assumed."),
    ReferenceCase(20, 40.0, "Slow synthetic cycle near the trend-versus-cycle boundary."),
    ReferenceCase(20, 20.5, "Fractional synthetic period and decimal parameter-name encoding."),
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
    begin = f"{comment} BEGIN GENERATED CORRELATION ANGLE EXPECTED DATA"
    end = f"{comment} END GENERATED CORRELATION ANGLE EXPECTED DATA"
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


def _case_suffix(case: ReferenceCase) -> str:
    """Encode configuration names with underscores instead of decimal points."""
    input_token = format(case.input_period, ".15g").replace(".", "_")
    return f"P{case.period}_IP{input_token}"


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Calculate, write/reopen/verify Python data, then export its decimal values.

    Renderers are independent tooling. A translated streaming indicator only
    needs the class, its four outputs, constants, and documented startup rules.
    """
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 prices and one through 64 parameter cases")
    if len({(c.period, c.input_period) for c in REFERENCE_CASES}) != len(REFERENCE_CASES):
        raise ValueError("reference configurations must be unique")
    python_path = directory / "test_testdata.py"
    original_inputs = {name: values for name, values in _load_literal_arrays(python_path).items()
                       if name.startswith("INPUT_")}
    if original_inputs.get("INPUT_CLOSE") != input_close:
        raise ValueError("embedded closes differ from the copied fixture")
    raw = {}
    sections = []
    fields = CorrelationAngleOutput._fields
    for case in REFERENCE_CASES:
        indicator = CorrelationAngle(case.period, case.input_period)
        outputs = [indicator.update(value) for value in input_close]
        suffix = _case_suffix(case)
        for field in fields:
            values = [getattr(output, field) for output in outputs]
            name = f"EXPECTED_{suffix}_{field.upper()}"
            raw[name] = (values, indicator.warmup_bars)
            sections.append(
                f"# {case.what_it_tests}\n"
                f"# period={case.period}, input_period={case.input_period:g}\n"
                f"{name} = [\n" + _array_lines(values, "    ", "math.nan") + "\n]"
            )
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # Python decimal literals are the master data. Verify the actual reopened
    # file before producing another language's version of those decimal values.
    written = _load_literal_arrays(python_path)
    if {name: written[name] for name in original_inputs} != original_inputs:
        raise ValueError("input arrays changed")
    if {name for name in written if name.startswith("EXPECTED_")} != set(raw):
        raise ValueError("missing or unexpected expected arrays")
    for name, (values, warmup) in raw.items():
        if len(written[name]) != 252:
            raise ValueError(f"{name} must contain 252 values")
        for i, (before, after) in enumerate(zip(values, written[name])):
            if i < warmup:
                if not math.isnan(before) or not math.isnan(after):
                    raise ValueError(f"{name} has an incorrect NaN prefix")
            elif not math.isfinite(after) or after != float(_float_literal(before, "nan")):
                raise ValueError(f"{name} failed fifteen-digit serialization verification")

    go_path = directory / "testdata_test.go"
    go = go_path.read_text().replace("package xxxx", "package correlationangle", 1)
    if 'import "math"' not in go:
        go = go.replace("package correlationangle\n", 'package correlationangle\n\nimport "math"\n', 1)
    go_path.write_text(go)
    zig_path = directory / "testdata.zig"
    zig = zig_path.read_text()
    if 'const math = @import("std").math;' not in zig:
        zig = 'const math = @import("std").math;\n' + zig
    if "const nan = math.nan(f64);" not in zig:
        zig = zig.replace('const math = @import("std").math;\n',
                          'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(zig)

    native = {"go": [], "ts": [], "rs": [], "zig": []}
    for case in REFERENCE_CASES:
        suffix = _case_suffix(case)
        comments = (f"// {case.what_it_tests}\n"
                    f"// period={case.period}, input_period={case.input_period:g}\n")
        for field in fields:
            ending = suffix + "_" + field.upper()
            values = written["EXPECTED_" + ending]
            native["go"].append(comments + f"var expected{ending} = []float64{{\n"
                                + _array_lines(values, "\t", "math.NaN()") + "\n}")
            native["ts"].append(comments + f"export const expected{ending}: number[] = [\n"
                                + _array_lines(values, "    ", "NaN") + "\n];")
            native["rs"].append(comments + f"pub fn expected_{ending.lower()}() -> Vec<f64> {{\n    vec![\n"
                                + _array_lines(values, "        ", "f64::NAN") + "\n    ]\n}")
            native["zig"].append(comments + f"pub fn expected{ending}() [252]f64 {{\n    return .{{\n"
                                 + _array_lines(values, "        ", "nan") + "\n    };\n}")
    for language, filename in (("go", "testdata_test.go"), ("ts", "testdata.ts"),
                               ("rs", "testdata.rs"), ("zig", "testdata.zig")):
        path = directory / filename
        if language == "rs" and "BEGIN GENERATED CORRELATION ANGLE EXPECTED DATA" not in path.read_text():
            # Preserve the copied Rust testdata module and put functions inside.
            rust = path.read_text()
            brace = rust.rfind("}")
            if brace < 0 or rust[brace + 1:].strip():
                raise ValueError("Rust fixture must end with the testdata module brace")
            path.write_text(rust[:brace])
            _write_generated_section(path, "\n\n".join(native[language]), "//")
            path.write_text(path.read_text() + "}\n")
        else:
            _write_generated_section(path, "\n\n".join(native[language]), "//")
    print(f"Verified {len(REFERENCE_CASES)} cases, {len(raw)} arrays of 252 values; wrote all five language fixtures.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true",
                        help="regenerate the confirmed 16 cases and four outputs in all five languages")
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
        # Article defaults demonstrate a deterministic matched sinusoid.
        # Set input_period=0 to consume the 252 supplied closes directly.
        for input_period in (20.0, 0.0):
            indicator = CorrelationAngle(period=20, input_period=input_period)
            outputs = [indicator.update(close) for close in INPUT_CLOSE]
            print(f"CorrelationAngle period=20, input_period={input_period:g}; 252 inputs")
            print(f"First {indicator.warmup_bars} outputs are NaN")
            print("First available:", outputs[indicator.warmup_bars])
            print("Final:", outputs[-1])
            print("Latest diagnostics:", indicator.diagnostics)
            indicator.reset()
            print("Primed after reset:", indicator.is_primed)
        print("Confirmed cases:", [(c.period, c.input_period) for c in REFERENCE_CASES])
