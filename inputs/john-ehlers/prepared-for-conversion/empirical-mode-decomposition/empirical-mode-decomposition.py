"""Streaming research prototype master for Ehlers and Way's March 2010 EMD.

Read description.md before porting this file. The indicator uses only Python's
standard library and has no imports from sibling indicator implementations.
The two-pole recurrence and the fixed 50-bar held-extremum averages follow
the article and TradeStation tip. The first two internal bars are zero, as
explicitly specified by the supplied NinjaTrader tip. Public incomplete
windows return NaN instead of a platform-specific partial moving average.

Run this file without arguments for a streaming demonstration. After the
reference parameter proposal is confirmed, --generate-reference appends the
five output series to the five copied language fixtures, reproducibly.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class Parameters(NamedTuple):
    """Immutable settings; changing a setting requires a new indicator."""

    period: int
    delta: float
    fraction: float


class EmpiricalModeDecompositionOutput(NamedTuple):
    """One bar's five outputs, in exactly the order requested by the user.

    FractalAbgPeak and FractalAvhValley intentionally retain the requested
    spelling. They mean Fraction * AvgPeak and Fraction * AvgValley; neither
    is a fractal-dimension estimator. Outputs have the same units as price.
    Each field has its own NaN warmup mask, described in description.md.
    """

    Trend: float
    AvgPeak: float
    FractalAbgPeak: float
    AvgValley: float
    FractalAvhValley: float


OUTPUT_FIELDS = EmpiricalModeDecompositionOutput._fields
PEAK_AVERAGE_LENGTH = 50  # Literal Average(Peak, 50) in the article.


def _real(value, name: str, allow_nan: bool = False) -> float:
    # Reject bool explicitly: Python otherwise treats True as the number 1.
    # A port should likewise accept numeric samples, not Boolean samples.
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a real number")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be a real number") from error
    if math.isinf(result) or (math.isnan(result) and not allow_nan):
        raise ValueError(f"{name} must be finite" + (" or NaN" if allow_nan else ""))
    return result


def _average_full_window(history: list[float], length: int) -> float:
    # Only complete windows are public. Internal startup zeros are legitimate
    # entries, whereas public NaNs must never enter recursive/window state.
    if len(history) < length:
        return math.nan
    # Deliberately sum newest to oldest with ordinary binary64 additions.
    # This matches a direct translation of Average's finite window. Replacing
    # this with fsum, a rolling sum, or another reduction order changes rounding.
    total = 0.0
    for index in range(length):
        total += history[index]
    if not math.isfinite(total):
        raise ValueError("moving-average arithmetic overflowed")
    return total / length


class EmpiricalModeDecomposition:
    """Causal scalar-input EMD with period=20, delta=.5, fraction=.1.

    update(price) consumes one completed bar and returns an immutable named
    tuple. To reproduce the article's price source, callers supply (H+L)/2.
    Reference fixtures deliberately supply INPUT_CLOSE, as requested.

    State is bounded: two price lags, a 2*period BP window, two 50-bar held
    extremum windows, and the two held extrema. This transparent master uses
    O(period + 50) work per bar. A port can use circular arrays while keeping
    the specified sum order. No batch lookahead or future sample is needed.
    """

    def __init__(self, period: int = 20, delta: float = 0.5,
                 fraction: float = 0.1):
        # P must exceed the Nyquist-period limit of two bars and must be an
        # integer, because 2*P is the exact moving-average window length.
        if type(period) is not int or period < 3:
            raise ValueError("period must be an integer >= 3")
        delta = _real(delta, "delta")
        fraction = _real(fraction, "fraction")
        # theta=4*pi*delta/P in (0, pi/2) selects the positive, stable branch
        # of sec(theta)-sqrt(sec(theta)^2-1), rather than a periodic alias.
        if not 0.0 < delta < period / 8.0:
            raise ValueError("delta must satisfy 0 < delta < period/8")
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("fraction must satisfy 0 <= fraction <= 1")
        self._parameters = Parameters(period, delta, fraction)
        # EasyLanguage Cosine takes DEGREES; Python math.cos takes RADIANS.
        # Use math.pi at full binary64 precision, never a truncated 3.14159.
        self._beta = math.cos(2.0 * math.pi / period)
        self._gamma = 1.0 / math.cos(4.0 * math.pi * delta / period)
        # Preserve the published subtraction and square-root ordering. A tan
        # identity would be equivalent mathematically but differ in rounding.
        self._alpha = self._gamma - math.sqrt(self._gamma * self._gamma - 1.0)
        # Extremely small delta can round alpha to 1 even inside the analytic
        # range. Reject numerically marginal coefficients, without clamping.
        if not 0.0 < self._alpha < 1.0:
            raise ValueError("delta must yield a representably stable coefficient")
        self._gain = 0.5 * (1.0 - self._alpha)
        self._feedback = self._beta * (1.0 + self._alpha)
        self.reset()

    @property
    def parameters(self) -> Parameters:
        return self._parameters

    @property
    def samples_seen(self) -> int:
        # Missing NaN observations do not increment this counter.
        return self._count

    @property
    def warmup_bars(self) -> int:
        # Number of accepted bars before ALL five fields can be finite.
        # The first all-finite output is at zero-based index warmup_bars.
        return max(2 * self.parameters.period, PEAK_AVERAGE_LENGTH) - 1

    @property
    def is_primed(self) -> bool:
        return self.samples_seen > self.warmup_bars

    @property
    def output(self) -> EmpiricalModeDecompositionOutput:
        # A skipped observation returns NaNs but preserves this last accepted
        # output, so the caller can distinguish skipping from resetting.
        return self._output

    def reset(self) -> None:
        """Return to a cold start while preserving coefficients/settings."""
        self._count = 0
        # All histories are NEWEST FIRST. After an accepted update, history[j]
        # is the current bar's X[j] in EasyLanguage notation.
        self._prices: list[float] = []
        self._bp: list[float] = []
        self._peak_history: list[float] = []
        self._valley_history: list[float] = []
        self._peak = 0.0
        self._valley = 0.0
        self._output = EmpiricalModeDecompositionOutput(*(math.nan,) * 5)

    def update(self, price: float) -> EmpiricalModeDecompositionOutput:
        """Accept one scalar bar; return the five current outputs.

        NaN is a missing observation: return five NaNs without advancing any
        state. Infinity/invalid values raise ValueError without advancing.
        These missing-value rules are explicit prototype API conventions;
        the article assumes a dense stream of finite prices.
        """
        price = _real(price, "price", allow_nan=True)
        if math.isnan(price):
            return EmpiricalModeDecompositionOutput(*(math.nan,) * 5)

        peak = self._peak
        valley = self._valley
        if self._count < 2:
            # There is no real Price[2] yet. Seed BP, Peak and Valley to zero
            # on each of the first two accepted bars, as in the supplied
            # NinjaTrader OnBarUpdate(CurrentBar < 2) branch. Do not subtract
            # an invented zero price: that would create a startup impulse.
            bp = 0.0
        else:
            bp1, bp2 = self._bp[0], self._bp[1]
            # BEFORE the current bar is committed, prices[1] is Price[2].
            # Keep the article's left-associated recurrence evaluation.
            bp = (self._gain * (price - self._prices[1])
                  + self._feedback * bp1 - self._alpha * bp2)
            if not math.isfinite(bp):
                raise ValueError("bandpass arithmetic overflowed")
            # Today's BP confirms yesterday's extremum. The strict tests
            # intentionally ignore flat plateaus and have one bar of delay.
            # There is no sign restriction: a peak may be negative, and a
            # valley may be positive. Do not clamp or take absolute values.
            if bp1 > bp and bp1 > bp2:
                peak = bp1
            if bp1 < bp and bp1 < bp2:
                valley = bp1

        # Prepare prospective windows so an arithmetic failure leaves the
        # last accepted state intact. These are finite, bounded lists that
        # are easy to translate to ordinary arrays in the target languages.
        trend_length = 2 * self.parameters.period
        bp_history = [bp] + self._bp[:trend_length - 1]
        peak_history = [peak] + self._peak_history[:PEAK_AVERAGE_LENGTH - 1]
        valley_history = [valley] + self._valley_history[:PEAK_AVERAGE_LENGTH - 1]
        trend = _average_full_window(bp_history, trend_length)
        avg_peak = _average_full_window(peak_history, PEAK_AVERAGE_LENGTH)
        avg_valley = _average_full_window(valley_history, PEAK_AVERAGE_LENGTH)
        # NaN multiplied by zero stays NaN: fraction=0 does NOT bypass warmup.
        result = EmpiricalModeDecompositionOutput(
            trend, avg_peak, self.parameters.fraction * avg_peak,
            avg_valley, self.parameters.fraction * avg_valley,
        )

        # Commit once all calculations succeed. Held extrema are inserted on
        # EVERY bar, not just when a new extremum is found: Average(Peak, 50)
        # averages a stepwise series, not the last 50 turning-point events.
        self._prices = [price] + self._prices[:1]
        self._bp = bp_history
        self._peak_history = peak_history
        self._valley_history = valley_history
        self._peak, self._valley = peak, valley
        self._count += 1
        self._output = result
        return result


class ReferenceCase(NamedTuple):
    period: int
    delta: float
    fraction: float
    what_it_tests: str


# This is the concrete proposal shown to the user, not an implicit approval.
# Update the confirmation flag only after an explicit confirmation arrives.
REFERENCE_CASES_CONFIRMED = True  # User confirmed all 16 cases on 2026-10-25.
REFERENCE_CASES = (
    ReferenceCase(20, 0.5, 0.1, "Article defaults."),
    ReferenceCase(20, 0.5, 0.25, "Thresholds used in the article's MSFT example."),
    ReferenceCase(20, 0.1, 0.1, "Narrow bandpass from the introductory listing."),
    ReferenceCase(20, 0.25, 0.1, "Intermediate bandwidth."),
    ReferenceCase(20, 1.0, 0.1, "Wider bandwidth and faster response."),
    ReferenceCase(3, 0.25, 0.1, "Shortest supported period."),
    ReferenceCase(10, 0.5, 0.1, "Short cycle; Trend primes before peak/valley averages."),
    ReferenceCase(21, 0.5, 0.1, "Odd period and a 42-bar Trend window."),
    ReferenceCase(25, 0.5, 0.1, "All five outputs prime together at 50 bars."),
    ReferenceCase(40, 0.5, 0.1, "Longer cycle; peak/valley averages prime before Trend."),
    ReferenceCase(126, 0.5, 0.1, "Trend becomes available only on the final input bar."),
    ReferenceCase(127, 0.5, 0.1, "Insufficient input for Trend; other outputs remain available."),
    ReferenceCase(20, 0.5, 0.0, "Zero fraction collapses both thresholds to zero."),
    ReferenceCase(20, 0.5, 1.0, "Unit fraction makes thresholds equal their raw averages."),
    ReferenceCase(20, 0.01, 0.1, "Very narrow bandwidth and long filter memory."),
    ReferenceCase(4, 0.49, 0.1, "Bandwidth close to the stability boundary D < P/8."),
)


def _number(value: float, nan_literal: str = "NaN") -> str:
    """Serialize with 15 significant decimal digits, in valid float syntax."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("cannot serialize an infinite expected value")
    text = format(value, ".15g")
    # Rust/Zig f64 arrays require floating literals for integral values too.
    if "." not in text and "e" not in text.lower():
        text += ".0"
    return text


def _parameter_token(value: float) -> str:
    # Parameter identities omit a redundant .0 and replace decimal points.
    return format(value, ".15g").replace(".", "_")


def _suffix(case: ReferenceCase) -> str:
    return (f"P{case.period}_D{_parameter_token(case.delta)}"
            f"_F{_parameter_token(case.fraction)}")


def _read_python_arrays(path: Path) -> dict[str, list[float]]:
    """Read literal arrays without executing the fixture as arbitrary code."""
    arrays = {}
    for statement in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        if not isinstance(target, ast.Name) or not isinstance(statement.value, ast.List):
            continue
        values = []
        for node in statement.value.elts:
            if isinstance(node, ast.Name) and node.id == "NaN":
                values.append(math.nan)
            else:
                values.append(float(ast.literal_eval(node)))
        arrays[target.id] = values
    return arrays


def _array_body(values: list[float], indent: str, nan_literal: str) -> str:
    # Six numbers per row keeps even large-magnitude output readable.
    rows = []
    for start in range(0, len(values), 6):
        rows.append(indent + ", ".join(_number(v, nan_literal)
                                      for v in values[start:start + 6]) + ",")
    return "\n".join(rows)


_MARKER = "EMPIRICAL-MODE-DECOMPOSITION EXPECTED DATA"


def _with_generated_block(original: str, block: str, comment: str,
                          inside_rust_module: bool = False) -> str:
    # Only replace a block owned by THIS generator. Preserve all copied input
    # arrays and user content. First-time generation appends to the fixture.
    begin, end = f"{comment} BEGIN {_MARKER}", f"{comment} END {_MARKER}"
    if begin in original:
        start = original.index(begin)
        line_start = original.rfind("\n", 0, start) + 1
        finish = original.find(end, start)
        if finish < 0:
            raise ValueError("generated block is missing its end marker")
        finish += len(end)
        if original[finish:finish + 1] == "\n":
            finish += 1
        original = original[:line_start] + original[finish:]
    wrapped = begin + "\n" + block + "\n" + end
    if inside_rust_module:
        # The copied Rust fixture wraps its functions in #[cfg(test)] mod
        # testdata. Keep expected functions in that same existing module.
        close = original.rfind("}")
        if close < 0 or original[close + 1:].strip():
            raise ValueError("unexpected Rust fixture module layout")
        wrapped = "\n".join("    " + line if line else "" for line in wrapped.splitlines())
        return original[:close].rstrip() + "\n\n" + wrapped + "\n}\n"
    return original.rstrip() + "\n\n" + wrapped + "\n"


def generate_reference_data(directory: Path, inputs: list[float]) -> int:
    """Append canonical Python arrays, reread them, then export four languages.

    The expected literals in Python are the canonical serialized values.
    Other language arrays are generated FROM those reread Python values.
    Repeating this command replaces its marked blocks instead of duplicating
    arrays. The function returns the number of output arrays per language.
    """
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError("reference parameter combinations await user confirmation")
    if not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("reference case count must be between 1 and 64")
    directory = Path(directory)
    python_path = directory / "test_testdata.py"
    copied = _read_python_arrays(python_path)
    if len(inputs) != 252 or copied.get("INPUT_CLOSE") != inputs:
        raise ValueError("embedded INPUT_CLOSE must match all 252 copied Python inputs")

    # Calculate each independently cold-started case and split the named
    # tuple into five scalar arrays. Field suffixes make their roles explicit.
    expected = {}
    comments = {}
    for case in REFERENCE_CASES:
        stream = EmpiricalModeDecomposition(case.period, case.delta, case.fraction)
        outputs = [stream.update(price) for price in inputs]
        parameters = (f"period={case.period}, delta={case.delta}, fraction={case.fraction}; "
                      "peak_average_length=50; input=INPUT_CLOSE")
        for index, field in enumerate(OUTPUT_FIELDS):
            name = f"EXPECTED_{_suffix(case)}_{field.upper()}"
            if name in expected:
                raise ValueError("duplicate reference parameter/output name")
            expected[name] = [output[index] for output in outputs]
            comments[name] = (case.what_it_tests, parameters)

    sections = ["# NaN marks an incomplete output window.\nNaN = math.nan"]
    for name, values in expected.items():
        what, parameters = comments[name]
        sections.append(f"# {what}\n# {parameters}\n{name} = [\n"
                        + _array_body(values, "    ", "NaN") + "\n]")
    python_text = _with_generated_block(python_path.read_text(encoding="utf-8"),
                                        "\n\n".join(sections), "#")
    python_path.write_text(python_text, encoding="utf-8")

    # Reopen and verify the actual Python file BEFORE translating literals.
    # Compare against 15-digit serialization, not the unrounded binary64.
    written = _read_python_arrays(python_path)
    actual_names = {name for name in written if name.startswith("EXPECTED_")}
    if actual_names != set(expected):
        raise ValueError("missing or unexpected Python expected arrays")
    for name, original_values in expected.items():
        values = written[name]
        if len(values) != 252:
            raise ValueError(f"expected array must contain 252 values: {name}")
        for original, literal in zip(original_values, values):
            if math.isnan(original):
                if not math.isnan(literal):
                    raise ValueError(f"incorrect NaN mask: {name}")
            elif literal != float(_number(original)):
                raise ValueError(f"incorrect 15-digit literal: {name}")

    # Each target uses exactly the two comments that precede the Python array.
    go, typescript, rust, zig = [], [], [], []
    for name in expected:
        values = written[name]
        suffix = name.removeprefix("EXPECTED_")
        target_name = "expected" + suffix
        rust_name = "expected_" + suffix.lower()
        what, parameters = comments[name]
        header = f"// {what}\n// {parameters}\n"
        go.append(header + f"var {target_name} = []float64{{\n"
                  + _array_body(values, "\t", "math.NaN()") + "\n}")
        typescript.append(header + f"export const {target_name}: number[] = [\n"
                          + _array_body(values, "    ", "NaN") + "\n];")
        rust.append(header + f"pub fn {rust_name}() -> Vec<f64> {{\n    vec![\n"
                    + _array_body(values, "        ", "f64::NAN") + "\n    ]\n}")
        zig.append(header + f"pub fn {target_name}() [252]f64 {{\n    return .{{\n"
                   + _array_body(values, "        ", "nan") + "\n    };\n}")

    # Prepare the four exports before committing them. The original fixtures
    # already contain valid TypeScript, Rust, and Zig input declarations.
    texts = {}
    for filename, sections in (("testdata_test.go", go), ("testdata.ts", typescript),
                               ("testdata.rs", rust), ("testdata.zig", zig)):
        text = (directory / filename).read_text(encoding="utf-8")
        if filename == "testdata_test.go":
            text = text.replace("package xxxx", "package empiricalmodedecomposition", 1)
            if 'import "math"' not in text:
                text = text.replace("package empiricalmodedecomposition\n",
                                    'package empiricalmodedecomposition\n\nimport "math"\n', 1)
        if filename == "testdata.zig":
            if 'const math = @import("std").math;' not in text or "const nan = math.nan(f64);" not in text:
                raise ValueError("Zig fixture must declare math and nan")
        texts[filename] = _with_generated_block(text, "\n\n".join(sections), "//",
                                               inside_rust_module=filename == "testdata.rs")
    for filename, text in texts.items():
        (directory / filename).write_text(text, encoding="utf-8")
    return len(expected)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference", action="store_true",
                        help="append confirmed expected arrays to all five fixtures")
    args = parser.parse_args()

    # Embed all 252 INPUT_CLOSE observations so the master demonstration is
    # self-contained. These are copied verbatim from the parent fixture.
    # The generator also checks them against this folder's copied fixture.
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

    # This is the intended streaming usage: create once, then update per bar.
    indicator = EmpiricalModeDecomposition(period=20, delta=0.5, fraction=0.1)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print(f"Accepted {indicator.samples_seen} bars; all fields primed: {indicator.is_primed}")
    print("Default final output:", outputs[-1]._asdict())
    if args.generate_reference:
        count = generate_reference_data(Path(__file__).resolve().parent, INPUT_CLOSE)
        print(f"Verified and exported {count} arrays of 252 values to each of five languages.")
    else:
        print("Use --generate-reference to regenerate the 16 confirmed parameter combinations.")


if __name__ == "__main__":
    main()
