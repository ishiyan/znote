"""Self-contained streaming research prototype master for Ehlers' FRAMA.

Read description.md before porting. Returns both FRAMA and the raw range-based
fractal-dimension estimate used to adapt it. The October 2005 article/MESA
listing defines the calculation; the June 2010 article and Chapter 6 of Cycle
Analytics for Traders describe related, differently smoothed estimators.

Only Python's standard library is used. Default coefficient_mode=1 replaces
the article's rounded -4.6 with log(slowest_smoothing_factor), honoring the
requested full precision. coefficient_mode=0 reproduces the printed -4.6
and requires the article's fixed slowest_smoothing_factor=0.01.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class Parameters(NamedTuple):
    """Immutable settings; a new indicator is needed to change them."""

    length: int
    slowest_smoothing_factor: float
    coefficient_mode: int


class FractalAdaptiveMovingAverageOutput(NamedTuple):
    """Two outputs, with NaNs until the full length window is available.

    value has price units. fractal_dimension is dimensionless and deliberately
    reports the raw source estimate, including values below one. It is NOT
    the separately smoothed dimension sensor in the June 2010 article.
    """

    value: float
    fractal_dimension: float


OUTPUT_SUFFIXES = ("VALUE", "FDIM")
LOG_TWO = math.log(2.0)  # Full-precision logarithm, not a decimal approximation.


def _real(value, name: str, allow_nan: bool = False) -> float:
    # Python bool is an integer subclass; accept actual numerical samples.
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a real number")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be a real number") from error
    if math.isinf(result) or (math.isnan(result) and not allow_nan):
        raise ValueError(f"{name} must be finite" + (" or NaN" if allow_nan else ""))
    return result


def _box_range(highs: list[float], lows: list[float], start: int, end: int) -> float:
    """Highest high minus lowest low on a nonempty half-open interval."""
    # Seed extrema from a REAL sample, never sys.float_info.min. The latter
    # is a tiny POSITIVE value, not the most negative representable number,
    # and would corrupt zero/negative price series in the copied zpano code.
    highest = highs[start]
    lowest = lows[start]
    for index in range(start + 1, end):
        if highs[index] > highest:
            highest = highs[index]
        if lows[index] < lowest:
            lowest = lows[index]
    result = highest - lowest
    if not math.isfinite(result):
        raise ValueError("price-range arithmetic overflowed")
    return result


class FractalAdaptiveMovingAverage:
    """2005 FRAMA recurrence with an explicit scalar and optional high/low API.

    update(price) uses the same scalar for price, high, and low, as needed for
    INPUT_CLOSE reference data. update(price, high, low) reproduces the source
    range calculation on actual bars while letting the caller choose Price.
    Supply price=(high+low)/2 to follow the article's original midpoint input.

    length must be even and >=2. The first length accepted prices seed the
    internal filter directly; the first adaptive update is observation L+1,
    matching the source's one-based CurrentBar < N+1 condition. Both public
    outputs become available at observation L. Invalid/flat boxes retain
    the previous raw dimension, initially zero, exactly as the source guard.
    """

    def __init__(self, length: int = 16, slowest_smoothing_factor: float = 0.01,
                 coefficient_mode: int = 1):
        # The article divides the entire window into TWO equal, disjoint
        # halves. Reject odd values rather than silently changing the length.
        if type(length) is not int or length < 2 or length % 2:
            raise ValueError("length must be an even integer >= 2")
        slowest = _real(slowest_smoothing_factor, "slowest_smoothing_factor")
        # Zero cannot define log(A). The copied params claim [0,1] but their
        # factory unconditionally evaluates log(A); this master excludes zero.
        if not 0.0 < slowest <= 1.0:
            raise ValueError("slowest_smoothing_factor must satisfy 0 < A <= 1")
        if type(coefficient_mode) is not int or coefficient_mode not in (0, 1):
            raise ValueError("coefficient_mode must be 0 (article) or 1 (full precision)")
        if coefficient_mode == 0 and slowest != 0.01:
            raise ValueError("literal article mode requires slowest_smoothing_factor=0.01")
        self._parameters = Parameters(length, slowest, coefficient_mode)
        self._half = length // 2
        # The rounded -4.6 is confined to the explicit compatibility mode.
        # Full precision uses log(.01)=-4.605170185988091... by default and
        # generalizes naturally to any allowed slowest smoothing factor.
        self._exponent_scale = math.log(slowest) if coefficient_mode == 1 else -4.6
        self.reset()

    @property
    def parameters(self) -> Parameters:
        return self._parameters

    @property
    def samples_seen(self) -> int:
        return self._count

    @property
    def warmup_bars(self) -> int:
        # Number of accepted observations producing public NaNs.
        return self.parameters.length - 1

    @property
    def is_primed(self) -> bool:
        return self.samples_seen >= self.parameters.length

    @property
    def output(self) -> FractalAdaptiveMovingAverageOutput:
        return self._output

    @property
    def fractal_dimension(self) -> float:
        return self.output.fractal_dimension

    @property
    def alpha(self) -> float:
        # Diagnostic coefficient; it is not an extra expected output array.
        return self._alpha if self.is_primed else math.nan

    def reset(self) -> None:
        """Restore a cold start while retaining the settings."""
        self._count = 0
        # Newest-FIRST history translates source X[j] into history[j] after
        # committing the current bar. Capacity is exactly the window length.
        self._highs: list[float] = []
        self._lows: list[float] = []
        # Keep internal seeds finite. NaNs belong only at the public boundary.
        self._dimension = 0.0
        self._value = 0.0
        self._alpha = 1.0
        self._output = FractalAdaptiveMovingAverageOutput(math.nan, math.nan)

    def update(self, price: float, high: float | None = None,
               low: float | None = None) -> FractalAdaptiveMovingAverageOutput:
        """Consume one finite observation and return (value, dimension).

        Supply either both high/low or neither. Any NaN skips the entire bar
        without changing histories, count, filter, or saved output. Infinity,
        invalid numeric inputs, reversed high/low, and arithmetic overflow
        raise ValueError without changing state. The articles assume dense,
        finite data; these missing-value rules are explicit API conventions.
        """
        price = _real(price, "price", allow_nan=True)
        if (high is None) != (low is None):
            raise ValueError("supply both high and low, or neither")
        if high is None:
            high = low = price
        else:
            high = _real(high, "high", allow_nan=True)
            low = _real(low, "low", allow_nan=True)
        if any(math.isnan(value) for value in (price, high, low)):
            return FractalAdaptiveMovingAverageOutput(math.nan, math.nan)
        if high < low:
            raise ValueError("high must be >= low")

        length = self.parameters.length
        # Prepare prospective state first: failure must leave the previous
        # accepted output usable. Lists are deliberately simple to port.
        highs = [high] + self._highs[:length - 1]
        lows = [low] + self._lows[:length - 1]
        count = self._count + 1
        dimension = self._dimension
        alpha = self._alpha
        if count >= length:
            # Half one is offsets 0..L/2-1; half two is L/2..L-1.
            # No duplicated endpoint or gap is introduced between the halves.
            n1 = _box_range(highs, lows, 0, self._half) / self._half
            n2 = _box_range(highs, lows, self._half, length) / self._half
            n3 = _box_range(highs, lows, 0, length) / length
            # Preserve the original guard. A flat whole box OR flat half box
            # leaves Dimen unchanged, initially 0. Do not log(0), inject an
            # epsilon, reset D to 1, or clamp the public dimension to [1,2].
            if n1 > 0.0 and n2 > 0.0 and n3 > 0.0:
                combined = n1 + n2
                if not math.isfinite(combined):
                    raise ValueError("combined box-range arithmetic overflowed")
                dimension = (math.log(combined) - math.log(n3)) / LOG_TWO
                if not math.isfinite(dimension):
                    raise ValueError("dimension arithmetic overflowed")
            # This is algebraically the source's exp-then-clamp operation.
            # For D<=1 the result must clamp to 1; choosing 1 directly avoids
            # exponential overflow on a large gap producing a negative D.
            if dimension <= 1.0:
                alpha = 1.0
            else:
                alpha = math.exp(self._exponent_scale * (dimension - 1.0))
                alpha = min(1.0, max(self.parameters.slowest_smoothing_factor, alpha))

        if count <= length:
            # Article: Filt=Price while one-based CurrentBar < N+1.
            # Thus the Lth observation is BOTH the first public result and
            # the FINAL unfiltered seed. The copied zpano code adapts at L.
            value = price
        else:
            # Preserve the printed arithmetic order rather than rewriting as
            # previous + alpha*(price-previous), which rounds differently.
            value = alpha * price + (1.0 - alpha) * self._value
            if not math.isfinite(value):
                raise ValueError("FRAMA arithmetic overflowed")
        result = (FractalAdaptiveMovingAverageOutput(value, dimension)
                  if count >= length else FractalAdaptiveMovingAverageOutput(math.nan, math.nan))

        # Commit only after all computations succeed. A skipped bar never
        # reaches this section, so its absence does not age the lookback.
        self._highs, self._lows = highs, lows
        self._count = count
        self._dimension, self._alpha, self._value = dimension, alpha, value
        self._output = result
        return result


class ReferenceCase(NamedTuple):
    length: int
    slowest_smoothing_factor: float
    coefficient_mode: int
    what_it_tests: str


# All 16 proposed combinations were explicitly confirmed on 2026-10-25.
REFERENCE_CASES_CONFIRMED = True
REFERENCE_CASES = (
    ReferenceCase(16, 0.01, 1, "Full-precision default."),
    ReferenceCase(2, 0.01, 1, "Minimum length; scalar half-ranges are zero, so the source retains dimension zero."),
    ReferenceCase(4, 0.01, 1, "Short window and rapid adaptation."),
    ReferenceCase(8, 0.01, 1, "Half the default lookback."),
    ReferenceCase(20, 0.01, 1, "One-month daily lookback."),
    ReferenceCase(30, 0.01, 1, "Lookback used by the related 2010 dimension sensor."),
    ReferenceCase(64, 0.01, 1, "Longer window and slower changes in the estimate."),
    ReferenceCase(128, 0.01, 1, "Long lookback with 125 finite outputs."),
    ReferenceCase(250, 0.01, 1, "Only three finite outputs: one seed and two adaptive updates."),
    ReferenceCase(252, 0.01, 1, "Only the final bar is primed; FRAMA is the final price seed."),
    ReferenceCase(254, 0.01, 1, "Insufficient history; both outputs are entirely NaN."),
    ReferenceCase(16, 0.001, 1, "Slower congestion response."),
    ReferenceCase(16, 0.1, 1, "Faster congestion response."),
    ReferenceCase(16, 1.0, 1, "Unit smoothing factor makes FRAMA track price."),
    ReferenceCase(16, 0.01, 0, "Literal 2005 article coefficient for direct source comparison."),
    ReferenceCase(30, 0.01, 0, "Literal article coefficient with a longer lookback."),
)


def _suffix(case: ReferenceCase) -> str:
    alpha = format(case.slowest_smoothing_factor, ".15g").replace(".", "_")
    return f"L{case.length}_A{alpha}_C{case.coefficient_mode}"


# Serialization and the self-contained five-language generator follow below.


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


_MARKER = "FRACTAL-ADAPTIVE-MOVING-AVERAGE EXPECTED DATA"


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
    """Generate Python expectations, verify them, then export four languages.

    Each case runs independently from a cold start. The expected literals
    reread from the Python file are the canonical values for all exports.
    Only marked generated blocks are replaced on repeated runs; copied
    close/high/low/open inputs remain intact in all five fixture files.
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

    expected, comments = {}, {}
    for case in REFERENCE_CASES:
        stream = FractalAdaptiveMovingAverage(*case[:3])
        # Scalar input intentionally supplies identical price/high/low. This
        # matches the requested close-only reference convention, not the
        # article's default midpoint price with actual bar high/low ranges.
        outputs = [stream.update(close) for close in inputs]
        parameters = (f"length={case.length}, slowest_smoothing_factor={case.slowest_smoothing_factor}, "
                      f"coefficient_mode={case.coefficient_mode}; input=INPUT_CLOSE; high=low=close")
        for index, suffix in enumerate(OUTPUT_SUFFIXES):
            name = f"EXPECTED_{_suffix(case)}_{suffix}"
            if name in expected:
                raise ValueError("duplicate reference parameter/output name")
            expected[name] = [output[index] for output in outputs]
            comments[name] = (case.what_it_tests, parameters)

    sections = ["# NaN marks an incomplete length window.\nNaN = math.nan"]
    for name, values in expected.items():
        what, parameters = comments[name]
        sections.append(f"# {what}\n# {parameters}\n{name} = [\n"
                        + _array_body(values, "    ", "NaN") + "\n]")
    text = _with_generated_block(python_path.read_text(encoding="utf-8"),
                                 "\n\n".join(sections), "#")
    python_path.write_text(text, encoding="utf-8")

    # Verify the actual written arrays before converting them. Compare with
    # the rounded 15-significant-digit values, while keeping NaN masks exact.
    written = _read_python_arrays(python_path)
    if {name for name in written if name.startswith("EXPECTED_")} != set(expected):
        raise ValueError("missing or unexpected Python expected arrays")
    for name, unrounded in expected.items():
        if len(written[name]) != 252:
            raise ValueError(f"expected array must have 252 values: {name}")
        for source, literal in zip(unrounded, written[name]):
            if math.isnan(source):
                if not math.isnan(literal):
                    raise ValueError(f"incorrect NaN mask: {name}")
            elif literal != float(_number(source)):
                raise ValueError(f"incorrect 15-digit reference literal: {name}")

    go, typescript, rust, zig = [], [], [], []
    for name in expected:
        # All target values come from the just-reopened Python arrays, not
        # a second indicator run that might use different defaults or seeds.
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

    # Assemble complete exports before committing any of these four files.
    texts = {}
    for filename, sections in (("testdata_test.go", go), ("testdata.ts", typescript),
                               ("testdata.rs", rust), ("testdata.zig", zig)):
        text = (directory / filename).read_text(encoding="utf-8")
        if filename == "testdata_test.go":
            text = text.replace("package xxxx", "package fractaladaptivemovingaverage", 1)
            if 'import "math"' not in text:
                text = text.replace("package fractaladaptivemovingaverage\n",
                                    'package fractaladaptivemovingaverage\n\nimport "math"\n', 1)
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
                        help="append confirmed reference output arrays in five languages")
    args = parser.parse_args()

    # Embed the shared close array verbatim, so the master demonstration needs
    # no sibling module. Generation checks it against the copied fixture.
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

    # Intended streaming use: create once and update for each completed bar.
    stream = FractalAdaptiveMovingAverage(length=16, slowest_smoothing_factor=0.01)
    outputs = [stream.update(close) for close in INPUT_CLOSE]
    print(f"Accepted {stream.samples_seen} bars; primed: {stream.is_primed}")
    print("Default final output:", outputs[-1]._asdict())
    if args.generate_reference:
        count = generate_reference_data(Path(__file__).resolve().parent, INPUT_CLOSE)
        print(f"Verified and exported {count} arrays of 252 values to each of five languages.")
    else:
        print("Use --generate-reference to regenerate the 16 confirmed parameter combinations.")


if __name__ == "__main__":
    main()
