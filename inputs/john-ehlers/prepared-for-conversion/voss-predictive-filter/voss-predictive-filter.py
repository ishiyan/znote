"""Voss Predictive Filter (VPF), Ehlers, TASC August 2019.

Standard-library streaming research master of the article/Mesa/TradeStation
calculation. update(value) returns VossOutput(bandpass, voss), in input units.
The first FIVE actual input bars establish zero filter/predictor state; the
public output masks those setup bars with NaNs. Index 5 is first available.
This gate is independent of Period and Order. Pre-start recursive state is
zero; do not postpone the bandpass until Period or Order prices exist.

Bandwidth defaults to the article's fixed 0.25. Configurability follows the
Excel Traders' Tip. Predict=0 is a documented empty-loop extension retaining
the source gain of 1.5; it is NOT an identity predictor. The usual settings
use Predict=1..3. See description.md for delay, stability and source details.

Run for a demonstration using the embedded 252 INPUT_CLOSE observations.
All twenty reference combinations were confirmed by the user on 2026-10-19.
--generate-reference-data writes all output components to five fixtures.
The class has no file I/O; fixture rendering is separate tooling in this file.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class VossOutput(NamedTuple):
    """One aligned pair of scalar outputs; both are NaN during setup.

    bandpass is the source Filt / Plot1. voss is Voss / Plot2. The two values
    have the same input units and are not clamped or gain-normalized.
    """

    bandpass: float
    voss: float


class VossPredictiveFilter:
    """Two-pole bandpass followed by multi-delay negative-feedback predictor.

    period: integer >=3, default 20, bandpass center period in bars.
    predict: integer >=0, default 3; the source Order is exactly 3*predict.
    bandwidth: finite positive float < period/4, default 0.25. Usually <=1.

    Booleans are not parameter values. Inputs must convert to finite floats.
    A bounded price list holds two preceding observations. A newest-first
    predictor list holds exactly Order past predictor values, zero seeded.
    Per-bar work and predictor storage are O(Order); price/BPF storage is O(1).
    Changing configuration requires a new instance. reset() replays the same
    configuration with the primary source's zero seeds and five-bar setup.
    """

    def __init__(self, period: int = 20, predict: int = 3,
                 bandwidth: float = 0.25) -> None:
        if isinstance(period, bool) or not isinstance(period, int) or period < 3:
            raise ValueError("period must be an integer of at least 3")
        if isinstance(predict, bool) or not isinstance(predict, int) or predict < 0:
            raise ValueError("predict must be a nonnegative integer")
        if isinstance(bandwidth, bool):
            raise ValueError("bandwidth must be a finite positive fraction")
        bandwidth = float(bandwidth)
        # Restrict the trigonometric principal branch: 0 < theta < pi/2
        # gives 0 < G1 < 1 and 0 < S1 < 1, the stable two-pole coefficient.
        if not math.isfinite(bandwidth) or not 0.0 < bandwidth < period / 4.0:
            raise ValueError("bandwidth must be finite with 0 < bandwidth < period/4")
        self._period = period
        self._predict = predict
        self._bandwidth = bandwidth
        self._order = 3 * predict

        # EasyLanguage Cosine accepts DEGREES, not radians. Compute the
        # source degree expressions before conversion, preserving their order.
        # In other languages the division must use floating-point operands.
        self._f1 = math.cos(math.radians(360.0 / period))
        self._g1 = math.cos(math.radians(bandwidth * 360.0 / period))
        # Preserve the exact source 1/(G1*G1) expression. Algebraic rewrites
        # such as sec(theta)-tan(theta) may change floating-point rounding.
        self._s1 = 1.0 / self._g1 - math.sqrt(1.0 / (self._g1 * self._g1) - 1.0)
        if not 0.0 < self._s1 < 1.0 or not -1.0 < self._f1 < 1.0:
            raise ValueError("parameters must produce numerically resolvable stable coefficients")

        # count increases from 0 to Order-1 in the source; this is OLDEST to
        # NEWEST Voss history, with weights 1/Order through 1. Do not reverse
        # the lag weights or use current Voss in its own delayed feedback sum.
        # For Order=0 there are no iterations and no division by Order.
        self._feedback_weights = [(count + 1.0) / self._order
                                  for count in range(self._order)]
        self._gain = (3.0 + self._order) / 2.0
        self.reset()

    @property
    def period(self) -> int:
        """Read-only bandpass center period in input-bar units."""
        return self._period

    @property
    def predict(self) -> int:
        """Read-only nominal forward prediction parameter; not a future index."""
        return self._predict

    @property
    def bandwidth(self) -> float:
        """Read-only bandwidth parameter; original source uses fixed 0.25."""
        return self._bandwidth

    @property
    def order(self) -> int:
        """Exactly three times predict, as in the supplied calculation."""
        return self._order

    @property
    def warmup_bars(self) -> int:
        """Five masked setup outputs, independent of period and predictor order."""
        return 5

    @property
    def is_primed(self) -> bool:
        """True after six accepted observations; IIR transients may still exist."""
        return self._bars > self.warmup_bars

    def reset(self) -> None:
        """Reset recursive state and bar numbering to the article's initialization."""
        self._bars = 0
        self._prices = []
        self._filt1 = 0.0
        self._filt2 = 0.0
        # These are recursive initial conditions, NOT fabricated input prices.
        # During the first five accepted bars they remain zero. Even if Order
        # exceeds five, Voss lags before the first observation are zero seeded.
        self._voss_history = [0.0] * self._order
        self._output = VossOutput(math.nan, math.nan)

    @property
    def output(self) -> VossOutput:
        """Most recent public output; inspecting it does not advance the filter."""
        return self._output

    def update(self, value: float) -> VossOutput:
        """Consume one completed chronological observation; return both plots.

        All arithmetic is local until checked, so rejected nonfinite input or
        overflow does not consume a bar or contaminate recursive state. NaNs
        mark public availability only and NEVER enter BPF/Voss histories.
        """
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("input value must be finite")
        current_bar = self._bars + 1  # EasyLanguage CurrentBar starts at ONE.

        if current_bar <= self.warmup_bars:
            # The source calculates then overrides Filt=0. The TradeStation
            # tip branches around that unused calculation; do the same here
            # to avoid accessing nonexistent Close[2] on the first two bars.
            bandpass = 0.0
        else:
            # _prices[0] = Close[1], _prices[1] = Close[2]. The source input
            # difference spans TWO bars, not one. No SMA seed or detrending
            # high-pass/AGC from the book chapter belongs in this recurrence.
            difference = value - self._prices[1]
            bandpass = (0.5 * (1.0 - self._s1) * difference
                        + self._f1 * (1.0 + self._s1) * self._filt1
                        - self._s1 * self._filt2)
            if not math.isfinite(difference) or not math.isfinite(bandpass):
                raise ValueError("bandpass arithmetic must remain finite")

        sum_c = 0.0
        for count in range(self._order):
            # At update entry history[0]=Voss[1], history[Order-1]=Voss[Order].
            # Source Voss[Order-count] maps to history[Order-count-1].
            sum_c = (sum_c + self._feedback_weights[count]
                     * self._voss_history[self._order - count - 1])
        voss = self._gain * bandpass - sum_c
        if not math.isfinite(sum_c) or not math.isfinite(voss):
            raise ValueError("predictor arithmetic must remain finite")

        # Commit exactly one accepted bar. Current output enters the delayed
        # history only AFTER the full feedback calculation has finished.
        self._prices = [value] + self._prices[:1]
        self._filt2 = self._filt1
        self._filt1 = bandpass
        if self._order:
            self._voss_history = [voss] + self._voss_history[:self._order - 1]
        self._bars = current_bar
        self._output = (VossOutput(bandpass, voss) if self.is_primed
                        else VossOutput(math.nan, math.nan))
        return self._output


class ReferenceCase(NamedTuple):
    """One confirmed parameter triple and the portable 'What it tests' text."""

    period: int
    predict: int
    bandwidth: float
    what_it_tests: str


# All twenty combinations were confirmed by the user on 2026-10-19.
# Twenty combinations, two components
# per combination; the 64-combination limit counts parameter triples.
REFERENCE_CASES = (
    ReferenceCase(20, 3, 0.25, "Article, Mesa and TradeStation defaults."),
    ReferenceCase(20, 1, 0.25, "One-bar nominal prediction at the default center period."),
    ReferenceCase(20, 2, 0.25, "Two-bar nominal prediction at the default center period."),
    ReferenceCase(10, 1, 0.25, "Fast ten-bar cycle with short predictor feedback."),
    ReferenceCase(10, 3, 0.25, "Fast ten-bar cycle with the recommended maximum prediction."),
    ReferenceCase(14, 1, 0.25, "Intermediate cycle period with one-bar nominal prediction."),
    ReferenceCase(14, 3, 0.25, "Intermediate cycle period with nine delayed feedback taps."),
    ReferenceCase(30, 1, 0.25, "Slower thirty-bar cycle with short predictor feedback."),
    ReferenceCase(30, 3, 0.25, "Slower thirty-bar cycle with the default predictor order."),
    ReferenceCase(48, 1, 0.25, "Long cycle near the book's cycle/trend boundary."),
    ReferenceCase(48, 3, 0.25, "Long cycle with stronger anticipatory feedback."),
    ReferenceCase(3, 1, 0.25, "Minimum supported integer period near the Nyquist limit."),
    ReferenceCase(20, 3, 0.1, "Narrow bandwidth with longer bandpass ringing and startup transient."),
    ReferenceCase(20, 3, 0.5, "Wide bandwidth with faster bandpass response."),
    ReferenceCase(20, 3, 0.7, "Very wide bandwidth and greater high-frequency predictor exposure."),
    ReferenceCase(20, 0, 0.25, "Zero-order extension; empty feedback loop and source gain of 1.5."),
    ReferenceCase(20, 4, 0.25, "Research prediction beyond the recommended three-bar limit."),
    ReferenceCase(20, 8, 0.25, "Long research predictor with twenty-four delayed feedback taps."),
    ReferenceCase(126, 3, 0.25, "Half-record center period with a slowly settling bandpass."),
    ReferenceCase(252, 3, 0.25, "Full-record center period; five-bar setup still permits outputs."),
)

OUTPUT_FIELDS = ("bandpass", "voss")
OUTPUT_TOKENS = ("BPF", "VOSS")


def _case_suffix(case: ReferenceCase) -> str:
    """Portable parameter name: P=period, PR=predict, B=bandwidth."""
    bandwidth = format(case.bandwidth, ".15g").replace(".", "_")
    return f"P{case.period}_PR{case.predict}_B{bandwidth}"


def _parameter_comment(case: ReferenceCase) -> str:
    """The identical second comment line preceding every component fixture."""
    return f"period={case.period}, predict={case.predict}, bandwidth={case.bandwidth:.15g}"


def _float_literal(value: float, nan_literal: str) -> str:
    """Format 15 significant decimal digits, never round internal state."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("expected output cannot be infinite")
    literal = format(value, ".15g")
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _array_lines(values: list[float], indent: str, nan_literal: str) -> str:
    """Reviewable six-value array rows shared by all language renderers."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return "\n".join(indent + ", ".join(literals[i:i + 6]) + ","
                     for i in range(0, len(literals), 6))


def _load_literal_arrays(path: Path) -> dict[str, list[float]]:
    """Read Python data assignments using AST, without importing the fixture."""
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
    """Append or replace only marked expected data; preserve the input text."""
    begin = f"{comment} BEGIN GENERATED VOSS PREDICTIVE FILTER EXPECTED DATA"
    end = f"{comment} END GENERATED VOSS PREDICTIVE FILTER EXPECTED DATA"
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
    """Generate confirmed cases, reopen/verify Python, then translate.

    This is fixture tooling, independent from the ported streaming class.
    Each case produces BPF and VOSS arrays; names distinguish both plots.
    """
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 inputs and one through 64 parameter combinations")
    if len({_case_suffix(case) for case in REFERENCE_CASES}) != len(REFERENCE_CASES):
        raise ValueError("parameter suffixes must be unique")
    python_path = directory / "test_testdata.py"
    original_inputs = {name: values for name, values in _load_literal_arrays(python_path).items()
                       if name.startswith("INPUT_")}
    if original_inputs.get("INPUT_CLOSE") != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from the copied fixture")

    raw_outputs = {}
    sections = []
    for case in REFERENCE_CASES:
        indicator = VossPredictiveFilter(case.period, case.predict, case.bandwidth)
        outputs = [indicator.update(value) for value in input_close]
        for field, token in zip(OUTPUT_FIELDS, OUTPUT_TOKENS):
            name = "EXPECTED_" + _case_suffix(case) + "_" + token
            values = [getattr(output, field) for output in outputs]
            raw_outputs[name] = values
            sections.append(f"# {case.what_it_tests}\n# {_parameter_comment(case)}\n{name} = [\n"
                            + _array_lines(values, "    ", "math.nan") + "\n]")
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # VERIFY THE ACTUAL WRITTEN PYTHON FILE before exporting any other language.
    written = _load_literal_arrays(python_path)
    if {name: written[name] for name in original_inputs} != original_inputs:
        raise ValueError("input arrays changed during generation")
    if {name for name in written if name.startswith("EXPECTED_")} != set(raw_outputs):
        raise ValueError("missing or unexpected expected array names")
    for name, raw in raw_outputs.items():
        values = written[name]
        if len(values) != 252:
            raise ValueError(f"{name} must contain 252 values")
        for index, (before, after) in enumerate(zip(raw, values)):
            if index < 5:
                if not math.isnan(before) or not math.isnan(after):
                    raise ValueError(f"{name} has an incorrect setup NaN")
            elif not math.isfinite(after) or after != float(_float_literal(before, "nan")):
                raise ValueError(f"{name} failed 15-digit serialization verification")

    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text().replace("package xxxx", "package vosspredictivefilter", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package vosspredictivefilter\n",
                                  'package vosspredictivefilter\n\nimport "math"\n', 1)
    go_path.write_text(go_text)
    zig_path = directory / "testdata.zig"
    zig_text = zig_path.read_text()
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n' + zig_text
    if "const nan = math.nan(f64);" not in zig_text:
        zig_text = zig_text.replace('const math = @import("std").math;\n',
                                   'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(zig_text)

    translated = {"go": [], "ts": [], "rs": [], "zig": []}
    for case in REFERENCE_CASES:
        for token in OUTPUT_TOKENS:
            suffix = _case_suffix(case) + "_" + token
            values = written["EXPECTED_" + suffix]  # Values from verified Python.
            comments = f"// {case.what_it_tests}\n// {_parameter_comment(case)}\n"
            translated["go"].append(comments + f"var expected{suffix} = []float64{{\n"
                                    + _array_lines(values, "\t", "math.NaN()") + "\n}")
            translated["ts"].append(comments + f"export const expected{suffix}: number[] = [\n"
                                    + _array_lines(values, "    ", "NaN") + "\n];")
            translated["rs"].append(comments + f"pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n"
                                    + _array_lines(values, "        ", "f64::NAN") + "\n    ]\n}")
            translated["zig"].append(comments + f"pub fn expected{suffix}() [252]f64 {{\n    return .{{\n"
                                     + _array_lines(values, "        ", "nan") + "\n    };\n}")
    for language, filename in (("go", "testdata_test.go"), ("ts", "testdata.ts"),
                               ("rs", "testdata.rs"), ("zig", "testdata.zig")):
        path = directory / filename
        # Keep Rust's expected functions INSIDE the original testdata module.
        # Its inputs use #[cfg(test)]; do not move outputs to a different scope.
        if language == "rs" and "BEGIN GENERATED VOSS PREDICTIVE FILTER EXPECTED DATA" not in path.read_text():
            rust_text = path.read_text()
            final_brace = rust_text.rfind("}")
            if final_brace < 0 or rust_text[final_brace + 1:].strip():
                raise ValueError("Rust fixture must end with its testdata module brace")
            path.write_text(rust_text[:final_brace])
            _write_generated_section(path, "\n\n".join(translated[language]), "//")
            path.write_text(path.read_text() + "}\n")
        else:
            _write_generated_section(path, "\n\n".join(translated[language]), "//")
    print(f"Verified {len(raw_outputs)} arrays of 252 values for {len(REFERENCE_CASES)} cases; wrote all five languages.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true",
                        help="regenerate all twenty confirmed reference combinations")
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
        # Example use: one scalar input per completed bar, two named outputs.
        indicator = VossPredictiveFilter()  # Period=20, Predict=3, Bandwidth=.25.
        outputs = [indicator.update(close) for close in INPUT_CLOSE]
        print(f"VPF: period={indicator.period}, predict={indicator.predict}, bandwidth={indicator.bandwidth}")
        print(f"{len(INPUT_CLOSE)} observations; first {indicator.warmup_bars} outputs are NaN")
        first = outputs[indicator.warmup_bars]
        print(f"First available [5]: bandpass={first.bandpass:.15g}, voss={first.voss:.15g}")
        last = outputs[-1]
        print(f"Final: bandpass={last.bandpass:.15g}, voss={last.voss:.15g}")
        indicator.reset()
        print("Primed after reset:", indicator.is_primed)
        print(f"Confirmed combinations: {len(REFERENCE_CASES)}")
