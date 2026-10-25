"""Streaming research prototype master: zero-lag error-correcting EMA.

Numerical authority is Ehlers and Way's November 2010 EasyLanguage listing,
also reproduced in the MESA paper and TradeStation tip. Read description.md:
the CODE corrects a newly computed EMA, whereas the introductory prose writes
Price in that position. These are different filters; this master follows CODE.

Standard library only. Zero initial EMA/EC states; calculation and public
outputs start on the first accepted observation. GainLimit uses the article's
integer tenths convention, not the copied zpano implementation's actual-gain
units. The source's strict tie rule and finite LeastError sentinel are retained.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class Parameters(NamedTuple):
    """The source's two settings, immutable through the public interface."""

    length: int
    gain_limit: int


class ZeroLagErrorCorrectingExponentialMovingAverageOutput(NamedTuple):
    """Both plotted source lines; value is the selected EC, ema is baseline.

    Before any accepted observation both fields are NaN. A skipped NaN input
    returns a NaN tuple and preserves the previously accepted saved output.
    Dense finite input has no leading warmup NaNs: this is a recursive filter
    with explicit zero seeds rather than a finite-window statistic.
    """

    value: float
    ema: float


OUTPUT_SUFFIXES = ("EC", "EMA")
LEAST_ERROR_SENTINEL = 1_000_000.0  # Exact literal in the source, not infinity.


def _sample(value) -> float:
    # bool is a Python integer subclass; it is not a meaningful price sample.
    if isinstance(value, bool):
        raise ValueError("price must be a finite real or NaN")
    try:
        price = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("price must be a finite real or NaN") from error
    if math.isinf(price):
        raise ValueError("price must be a finite real or NaN")
    return price


class ZeroLagErrorCorrectingExponentialMovingAverage:
    """Source-faithful gain search with length=20 and integer GainLimit=50.

    update(price) returns (EC, EMA). best_gain and least_error expose the
    search diagnostics without adding extra expected output arrays. The
    article's strategy threshold is documented but is not an indicator setting.

    Gain candidates are i/10 for inclusive integers -gain_limit..gain_limit.
    Every candidate reads the SAME previous-bar EC, not the preceding trial.
    Only the best candidate is committed after the entire loop finishes.
    State/storage are O(1); work is O(2*gain_limit+1) per accepted sample.
    """

    def __init__(self, length: int = 20, gain_limit: int = 50):
        if type(length) is not int or length < 1:
            raise ValueError("length must be an integer >= 1")
        if type(gain_limit) is not int or gain_limit < 0:
            raise ValueError("gain_limit must be a nonnegative integer in tenths")
        self._parameters = Parameters(length, gain_limit)
        # Use the full rational expression from the article. In particular,
        # length=20 gives 2/21, not the copied implementation's rounded .095.
        try:
            self._alpha = 2.0 / (length + 1)
        except OverflowError as error:
            raise ValueError("length must yield representable coefficients") from error
        self._complement = 1.0 - self._alpha
        if not 0.0 < self._alpha <= 1.0 or not 0.0 <= self._complement < 1.0:
            raise ValueError("length must yield representably stable EMA coefficients")
        self.reset()

    @property
    def parameters(self) -> Parameters:
        return self._parameters

    @property
    def alpha(self) -> float:
        return self._alpha

    @property
    def samples_seen(self) -> int:
        return self._count

    @property
    def warmup_bars(self) -> int:
        # The article has no fixed-window requirement or three-sample branch.
        return 0

    @property
    def is_primed(self) -> bool:
        return self._count > 0

    @property
    def output(self) -> ZeroLagErrorCorrectingExponentialMovingAverageOutput:
        return self._output

    @property
    def best_gain(self) -> float:
        return self._best_gain if self.is_primed else math.nan

    @property
    def least_error(self) -> float:
        # This is the literal source variable, including its finite sentinel
        # if no trial improves upon it. It need not equal abs(price-EC) then.
        return self._least_error if self.is_primed else math.nan

    def reset(self) -> None:
        """Restore the source's zero declarations and empty public state."""
        self._count = 0
        self._ema = 0.0
        self._ec = 0.0
        self._best_gain = 0.0  # Source BestGain persists unless a trial wins.
        self._least_error = 0.0
        self._output = ZeroLagErrorCorrectingExponentialMovingAverageOutput(math.nan, math.nan)

    def update(self, price: float) -> ZeroLagErrorCorrectingExponentialMovingAverageOutput:
        """Accept one price, search the source grid, return EC and EMA.

        NaN skips an observation without aging state. Invalid/infinite input
        and arithmetic overflow raise ValueError without committing state.
        These are explicit prototype conventions; source data are dense and
        finite. There is no initial SMA, first-price seed, or extra smoothing.
        """
        price = _sample(price)
        if math.isnan(price):
            return ZeroLagErrorCorrectingExponentialMovingAverageOutput(math.nan, math.nan)

        alpha, complement = self._alpha, self._complement
        previous_ec = self._ec
        # The baseline EMA is updated ONCE, before evaluating any gain.
        ema = alpha * price + complement * self._ema
        if not math.isfinite(ema):
            raise ValueError("baseline EMA arithmetic overflowed")
        least_error = LEAST_ERROR_SENTINEL
        best_gain = self._best_gain
        for index in range(-self.parameters.gain_limit, self.parameters.gain_limit + 1):
            # Division of each integer separately preserves both endpoints
            # without drift from repeatedly adding a binary64 approximation
            # to .1. This is exactly the article's Value1 / 10 grid.
            gain = index / 10.0
            # IMPORTANT: EMA here is the NEW baseline, not raw Price. Keep
            # the printed evaluation order; never mutate previous_ec here.
            candidate = (alpha * (ema + gain * (price - previous_ec))
                         + complement * previous_ec)
            error = abs(price - candidate)
            if not math.isfinite(candidate) or not math.isfinite(error):
                raise ValueError("gain-search arithmetic overflowed")
            # Strict improvement preserves the FIRST winning gain on ties.
            # Search order is negative to positive, including both limits.
            # Do not change '<' to '<=' or add an epsilon tie comparison.
            if error < least_error:
                least_error = error
                best_gain = gain

        # Recompute the final output with BestGain, exactly as the article.
        # Returning the last trial would silently use +GainLimit every bar;
        # the supplied NinjaTrader tip has that bug and is not our authority.
        ec = (alpha * (ema + best_gain * (price - previous_ec))
              + complement * previous_ec)
        if not math.isfinite(ec):
            raise ValueError("selected EC arithmetic overflowed")
        result = ZeroLagErrorCorrectingExponentialMovingAverageOutput(ec, ema)

        # Commit after all candidates and the selected result succeed. In the
        # rare all-errors>=1e6 case, source BestGain carries over from the prior
        # bar while LeastError stays exactly at its sentinel; retain that rule.
        self._ema, self._ec = ema, ec
        self._best_gain, self._least_error = best_gain, least_error
        self._count += 1
        self._output = result
        return result


class ReferenceCase(NamedTuple):
    length: int
    gain_limit: int
    what_it_tests: str


# All 16 proposed combinations were explicitly confirmed on 2026-10-25.
REFERENCE_CASES_CONFIRMED = True
REFERENCE_CASES = (
    ReferenceCase(20, 50, "Article defaults with full-precision alpha=2/21."),
    ReferenceCase(12, 50, "Parameters used for the article's step and wave-burst demonstrations."),
    ReferenceCase(32, 22, "Parameters used for the article's MSFT example."),
    ReferenceCase(20, 0, "Zero gain: EC is a second EMA of the first EMA."),
    ReferenceCase(20, 1, "Minimal nonzero gain range, from -0.1 to +0.1."),
    ReferenceCase(20, 10, "Gain range from -1.0 to +1.0."),
    ReferenceCase(20, 22, "Reduced correction range, isolating gain-limit effects."),
    ReferenceCase(20, 100, "Wider correction range, from -10.0 to +10.0."),
    ReferenceCase(1, 50, "Alpha=1: EC and EMA track the input."),
    ReferenceCase(2, 50, "Very fast baseline EMA."),
    ReferenceCase(5, 50, "Short lookback and fast response."),
    ReferenceCase(10, 50, "Intermediate baseline smoothing."),
    ReferenceCase(40, 50, "Longer baseline smoothing."),
    ReferenceCase(100, 50, "Slow EMA and substantial startup transient."),
    ReferenceCase(252, 50, "Long nominal length; recursive outputs are still available from the first bar."),
    ReferenceCase(20, 49, "Non-round gain endpoint and inclusive search from -4.9 to +4.9."),
)


def _suffix(case: ReferenceCase) -> str:
    return f"L{case.length}_G{case.gain_limit}"


# Self-contained serialization and fixture generation helpers follow.


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


_MARKER = "ZERO-LAG-ERROR-CORRECTING-EXPONENTIAL-MOVING-AVERAGE EXPECTED DATA"


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
    """Write and verify canonical Python arrays, then export four languages."""
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError("reference parameter combinations await user confirmation")
    if not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("reference case count must be between 1 and 64")
    directory = Path(directory)
    python_path = directory / "test_testdata.py"
    if len(inputs) != 252 or _read_python_arrays(python_path).get("INPUT_CLOSE") != inputs:
        raise ValueError("embedded INPUT_CLOSE must match all 252 copied Python inputs")

    expected, comments = {}, {}
    for case in REFERENCE_CASES:
        # A fresh zero-seeded state for EACH case prevents parameters or
        # histories leaking between reference series.
        stream = ZeroLagErrorCorrectingExponentialMovingAverage(*case[:2])
        outputs = [stream.update(price) for price in inputs]
        parameters = (f"length={case.length}, gain_limit={case.gain_limit}; "
                      "gain_step=0.1; input=INPUT_CLOSE; initialization=zeros")
        for index, suffix in enumerate(OUTPUT_SUFFIXES):
            name = f"EXPECTED_{_suffix(case)}_{suffix}"
            if name in expected:
                raise ValueError("duplicate reference parameter/output name")
            expected[name] = [output[index] for output in outputs]
            comments[name] = (case.what_it_tests, parameters)

    sections = ["# NaN represents unavailable or skipped observations.\nNaN = math.nan"]
    for name, values in expected.items():
        what, parameters = comments[name]
        sections.append(f"# {what}\n# {parameters}\n{name} = [\n"
                        + _array_body(values, "    ", "NaN") + "\n]")
    python_path.write_text(_with_generated_block(python_path.read_text(encoding="utf-8"),
                                                 "\n\n".join(sections), "#"), encoding="utf-8")

    # Verify the ACTUAL Python literals before exporting their rounded values.
    # Internal calculations stay binary64; serialization alone rounds to .15g.
    written = _read_python_arrays(python_path)
    if {name for name in written if name.startswith("EXPECTED_")} != set(expected):
        raise ValueError("missing or unexpected Python expected arrays")
    for name, source in expected.items():
        if len(written[name]) != 252:
            raise ValueError(f"expected array must have 252 values: {name}")
        for unrounded, literal in zip(source, written[name]):
            if math.isnan(unrounded):
                if not math.isnan(literal):
                    raise ValueError(f"incorrect NaN mask: {name}")
            elif literal != float(_number(unrounded)):
                raise ValueError(f"incorrect 15-digit reference literal: {name}")

    go, typescript, rust, zig = [], [], [], []
    for name in expected:
        values = written[name]  # Export FROM canonical Python reference arrays.
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

    # This source has no dense-input warmup NaNs. Keep the requested Go math
    # import compilable even then: a blank reference to math.NaN is harmless
    # and allows future missing-input arrays to use the standard NaN function.
    go.insert(0, "// Keep math available even when the dense reference arrays have no NaNs.\nvar _ = math.NaN")
    texts = {}
    for filename, sections in (("testdata_test.go", go), ("testdata.ts", typescript),
                               ("testdata.rs", rust), ("testdata.zig", zig)):
        text = (directory / filename).read_text(encoding="utf-8")
        if filename == "testdata_test.go":
            package = "zerolagerrorcorrectingexponentialmovingaverage"
            text = text.replace("package xxxx", "package " + package, 1)
            if 'import "math"' not in text:
                text = text.replace("package " + package + "\n",
                                    "package " + package + '\n\nimport "math"\n', 1)
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
                        help="append the confirmed 16 cases as five-language expected arrays")
    args = parser.parse_args()

    # Embed all 252 shared closes verbatim for a self-contained demonstration.
    # Generation also compares them with this folder's copied input fixture.
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

    # Intended usage: instantiate once and update for each completed price bar.
    stream = ZeroLagErrorCorrectingExponentialMovingAverage(length=20, gain_limit=50)
    outputs = [stream.update(close) for close in INPUT_CLOSE]
    print(f"Accepted {stream.samples_seen} bars; primed: {stream.is_primed}")
    print("Default final output:", outputs[-1]._asdict())
    print("Final search diagnostics:", {"best_gain": stream.best_gain, "least_error": stream.least_error})
    if args.generate_reference:
        count = generate_reference_data(Path(__file__).resolve().parent, INPUT_CLOSE)
        print(f"Verified and exported {count} arrays of 252 values to each of five languages.")
    else:
        print("Use --generate-reference to regenerate the 16 confirmed parameter combinations.")


if __name__ == "__main__":
    main()
