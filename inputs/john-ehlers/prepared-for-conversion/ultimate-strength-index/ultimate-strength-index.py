"""Ultimate Strength Index: streaming master reference using standard Python.

Authority: Ehlers' November 2024 article and matching TradeStation code.
The established full-precision pi and sqrt(2) policy is retained. See
description.md for the original equations, startup, and platform differences.

Run without flags to stream the embedded 252 closes and print sample values.
Run with --generate-reference-data after the parameter cases are confirmed to
write the Python arrays, verify them, and translate them into Go, TS, Rust, Zig.
The streaming classes need no external file, library, or sibling indicator.
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


# These are fixed details of the article, NOT extra user parameters. Turning
# them into optimized settings would change the indicator being referenced.
PREAVERAGE_LENGTH = 4
MINIMUM_STRENGTH = 0.01


class UltimateStrengthIndex:
    """Low-lag normalized balance of four-bar-averaged upward/downward changes.

    length is a finite real critical period >= 1, default 14.0. Fractional
    periods are valid because Length only sets UltimateSmoother coefficients;
    it does not count elements of the fixed four-bar pre-average.

    The first close establishes a previous-price reference, with SU=SD=0.
    Unobserved prior strengths are seeded to zero in the four-bar histories.
    Both smoothers return their inputs for the first three bars, then recurse.
    USI starts at zero and holds its previous value whenever the exact article
    guard fails. Thus initialization is defined and no leading NaNs are needed.
    """

    def __init__(self, length: float = 14.0) -> None:
        self._up_filter = UltimateSmoother(length)
        self._down_filter = UltimateSmoother(length)
        self._length = self._up_filter.period
        self.reset()

    @property
    def length(self) -> float:
        """Read-only configuration; construct a fresh object to change length."""
        return self._length

    @property
    def is_primed(self) -> bool:
        """The first observed bar has a defined initialized output of zero."""
        return self._previous_close is not None

    @property
    def warmup_bars(self) -> int:
        """Number of leading unavailable outputs under the zero-seeded policy."""
        return 0

    def reset(self) -> None:
        """Clear all histories and restore Vars: USI(0) from the source."""
        self._previous_close = None
        # Two independent filters must be reset together. Their startup count
        # advances on EVERY observed close, even if the final USI is held.
        self._up_filter.reset()
        self._down_filter.reset()
        self._up_history = [0.0] * PREAVERAGE_LENGTH
        self._down_history = [0.0] * PREAVERAGE_LENGTH
        self._next = 0
        self._last_output = 0.0

    def update(self, close: float) -> float:
        """Observe one chronological close; return this bar's scalar USI."""
        close = float(close)
        if not math.isfinite(close):
            # Rejected missing/infinite observations do not advance any state.
            raise ValueError('close must be finite')

        # With no preceding close supplied, do not interpret close-0 as a gain.
        # The first observation establishes a baseline, producing no movement.
        if self._previous_close is None:
            up, down = 0.0, 0.0
        elif close > self._previous_close:
            up, down = close - self._previous_close, 0.0
        elif close < self._previous_close:
            up, down = 0.0, self._previous_close - close
        else:
            up, down = 0.0, 0.0
        if not math.isfinite(up) or not math.isfinite(down):
            raise ValueError('one-bar price difference must be finite')

        # Replace the oldest strength in each four-slot circular history.
        # Every slot exists from startup; unobserved preceding changes are 0.
        self._up_history[self._next] = up
        self._down_history[self._next] = down
        self._next = (self._next + 1) % PREAVERAGE_LENGTH

        # Average(SU,4) and Average(SD,4) are ordinary four-bar SMAs. Sum the
        # exact four newest-to-oldest terms on each bar, then divide by FOUR,
        # including during initialization. Never use an EMA, partial divisor,
        # length-sized average, or a rolling total with accumulating roundoff.
        up_total, down_total = 0.0, 0.0
        for lag in range(PREAVERAGE_LENGTH):
            index = (self._next - 1 - lag) % PREAVERAGE_LENGTH
            up_total = up_total + self._up_history[index]
            down_total = down_total + self._down_history[index]
        averaged_up = up_total / PREAVERAGE_LENGTH
        averaged_down = down_total / PREAVERAGE_LENGTH

        # Each average feeds its own independent stateful UltimateSmoother.
        # Filter the strengths BEFORE normalization; smoothing a computed RSI
        # afterward is not equivalent because division is a nonlinear step.
        smoothed_up = self._up_filter.update(averaged_up)
        smoothed_down = self._down_filter.update(averaged_down)
        denominator = smoothed_up + smoothed_down

        # Preserve ALL source tests, including strict > .01 for BOTH paths.
        # A failed test means retain USI[1], not return 0, +/-1, NaN, or an
        # unguarded ratio. The guard is in price-change units, not relative
        # error units. Positive strengths permit a ratio between -1 and +1.
        if (denominator != 0.0 and smoothed_up > MINIMUM_STRENGTH
                and smoothed_down > MINIMUM_STRENGTH):
            self._last_output = (smoothed_up - smoothed_down) / denominator

        # Even a held output consumes the bar, the changes, and filter states.
        self._previous_close = close
        return self._last_output


class ReferenceCase(NamedTuple):
    """One reference critical period and its exact What-it-tests comment."""

    length: float
    what_it_tests: str


REFERENCE_CASES = (
    ReferenceCase(1.0, 'Minimum period: four-bar pre-average dominates while the source guard remains active.'),
    ReferenceCase(2.0, 'Two-bar period: shortest Nyquist-scale smoother coefficients.'),
    ReferenceCase(3.0, 'Very short period: rapid strength smoothing after the three startup bars.'),
    ReferenceCase(4.0, 'Four-bar period: smoother critical period equals the fixed pre-average length.'),
    ReferenceCase(8.0, 'Short practical period: responsive zero crossings with four-bar pre-averaging.'),
    ReferenceCase(14.0, 'Article and TradeStation default: fourteen-bar strength smoothing.'),
    ReferenceCase(20.0, 'Intermediate period: comparison with the established twenty-bar UltimateSmoother.'),
    ReferenceCase(28.0, 'Article swing example: twenty-eight-bar USI compared with fourteen-bar MyRSIH.'),
    ReferenceCase(28.5, 'Fractional period: preserve real-valued coefficients without integer truncation.'),
    ReferenceCase(56.0, 'Longer intermediate period: twice the article swing setting.'),
    ReferenceCase(112.0, 'Article trend example: four times the twenty-eight-bar swing setting.'),
    ReferenceCase(252.0, 'Full-record period: long recursive memory with defined startup and guarded holds.'),
)


def _parameter_token(value: float) -> str:
    """Make portable names: 0.2 -> 0_2, -0.2 -> m0_2, 10.0 -> 10."""
    # A minus sign is invalid in an identifier, so 'm' denotes minus. Keep
    # integral parameter values compact; fixtures themselves always use floats.
    return format(value, "g").replace("-", "m").replace(".", "_")


def _case_suffix(case: ReferenceCase) -> str:
    """L = length; decimal points become underscores in portable identifiers."""
    return f"L{_parameter_token(case.length)}"


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
    begin = f"{comment} BEGIN GENERATED ULTIMATE STRENGTH INDEX EXPECTED DATA"
    end = f"{comment} END GENERATED ULTIMATE STRENGTH INDEX EXPECTED DATA"
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
        indicator = UltimateStrengthIndex(case.length)
        values = [indicator.update(price) for price in input_close]
        name = "EXPECTED_" + _case_suffix(case)
        raw_outputs[name] = values
        python_sections.append(
            f"# {case.what_it_tests}\n"
            f"# length={case.length:g}\n"
            f"{name} = [\n{_array_lines(values, '    ', 'math.nan')}\n]"
        )
    _write_generated_section(python_path, "\n\n".join(python_sections), "#")

    # Read the written Python arrays back and check count, length, and precision
    # before appending them to other languages. Current cases have defined seeded startup;
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
            raise ValueError(f"{name} must have no NaN prefix because the standalone seeded startup is defined")
        for before, after in zip(raw, written):
            if math.isnan(before) and math.isnan(after):
                continue
            if not math.isclose(before, after, rel_tol=5e-14, abs_tol=5e-14):
                raise ValueError(f"{name} did not retain 15-digit precision")

    # Go requires a used import. There are no warm-up NaNs in this indicator,
    # so a blank reference keeps the specifically requested math import valid.
    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8").replace(
        "package xxxx", "package ultimatestrengthindex", 1
    )
    if 'import "math"' not in go_text:
        go_text = go_text.replace(
            "package ultimatestrengthindex\n",
            'package ultimatestrengthindex\n\nimport "math"\n\n'
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
            f"// length={case.length:g}\n"
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
    # The first close establishes the baseline. Every bar advances the
    # fixed four-bar strength histories and both filters, even when USI is held.
    indicator = UltimateStrengthIndex(length=14.0)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print("Default first five outputs:", ", ".join(
        _float_literal(value, "NaN") for value in outputs[:5]
    ))
    print("Reference parameter cases:")
    for case in REFERENCE_CASES:
        print(f"  EXPECTED_{_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
