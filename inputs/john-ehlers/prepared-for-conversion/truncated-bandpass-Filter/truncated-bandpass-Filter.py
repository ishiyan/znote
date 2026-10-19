"""Streaming research master: Truncated Bandpass Filter, Ehlers, July 2020.

update(close) returns BandpassOutput(truncated_bandpass, bandpass), both in
input-price units. The source forces the standard BPF to zero for its first
three calculation bars; this standalone stream calls the first supplied bar
CurrentBar=1 and masks those three setup outputs with NaN. The truncated
filter needs Length+2 actual closes and has its own NaN prefix of Length+1.
Never delay the standard recursion until the truncated window is available.

Only the standard library is used. The streaming class has no file I/O.
The extensive source, initialization and porting discussion is in description.md.
Run without arguments for an example using the embedded 252 shared closes.
All twenty reference combinations were confirmed by the user on 2026-10-19.
--generate-reference-data writes and verifies all five fixture files.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class BandpassOutput(NamedTuple):
    """The requested two outputs; availability is independent for each field.

    truncated_bandpass corresponds to BPT / Plot2 in the article.
    bandpass corresponds to BP / Plot1. Neither is normalized or clamped.
    """

    truncated_bandpass: float
    bandpass: float


class TruncatedBandpassFilter:
    """Bounded-history replay of a two-pole BPF, alongside its standard IIR.

    period: integer >=3; center period in bars; default 20.
    bandwidth: finite fraction, 0 < bandwidth < period/4; default 0.1.
    length: integer 1..97; number of historical recurrence steps; default 10.

    Configuration is read-only; construct a new instance to change it.
    reset() discards all observations but preserves these coefficients.
    Persistent price storage and temporary replay storage are O(length).
    Each primed update does O(length) work. No third-party numeric operations,
    retrospective edits, future observations or platform bar buffers are used.
    """

    def __init__(self, period: int = 20, bandwidth: float = 0.1,
                 length: int = 10) -> None:
        # Reject booleans: Python's bool is an int subclass, but a switch is
        # not a meaningful cycle period or truncation length in a port.
        if isinstance(period, bool) or not isinstance(period, int) or period < 3:
            raise ValueError("period must be an integer of at least 3")
        if isinstance(length, bool) or not isinstance(length, int) or not 1 <= length <= 97:
            raise ValueError("length must be an integer from 1 through 97")
        if isinstance(bandwidth, bool):
            raise ValueError("bandwidth must be a finite positive fraction")
        bandwidth = float(bandwidth)
        # This selects the principal stable branch 0 < theta < pi/2.
        # Period>=3 puts the center frequency strictly below Nyquist.
        if not math.isfinite(bandwidth) or not 0.0 < bandwidth < period / 4.0:
            raise ValueError("bandwidth must be finite with 0 < bandwidth < period/4")

        # EasyLanguage Cosine uses DEGREES. Preserve the source expression
        # ordering, then convert to radians for standard-library math.cos.
        # Ports must perform floating-point division, even for integer period.
        l1 = math.cos(math.radians(360.0 / period))
        g1 = math.cos(math.radians(bandwidth * 360.0 / period))
        # Keep the printed secant-minus-square-root expression. Replacing it
        # with a cancellation-resistant identity can change the last digits.
        s1 = 1.0 / g1 - math.sqrt(1.0 / (g1 * g1) - 1.0)
        if not -1.0 < l1 < 1.0 or not 0.0 < s1 < 1.0:
            raise ValueError("parameters must yield numerically resolvable stable coefficients")
        self._period = period
        self._bandwidth = bandwidth
        self._length = length
        self._l1 = l1
        self._s1 = s1
        self.reset()

    @property
    def period(self) -> int:
        """Read-only center period, in input bars."""
        return self._period

    @property
    def bandwidth(self) -> float:
        """Read-only source Bandwidth; 0.1 means ten percent, not 10."""
        return self._bandwidth

    @property
    def length(self) -> int:
        """Read-only number of replay steps; requires length+2 input prices."""
        return self._length

    @property
    def bandpass_warmup_bars(self) -> int:
        """The three source-forced zero bars are public NaNs."""
        return 3

    @property
    def truncated_warmup_bars(self) -> int:
        """length+1 outputs precede the first complete replay window."""
        return self._length + 1

    @property
    def warmup_bars(self) -> int:
        """Number of bars before BOTH output components can be available."""
        return max(self.bandpass_warmup_bars, self.truncated_warmup_bars)

    @property
    def is_primed(self) -> bool:
        """True when both outputs are available; does not imply IIR settling."""
        return self._bars > self.warmup_bars

    @property
    def output(self) -> BandpassOutput:
        """Last accepted output; reading it never consumes an input bar."""
        return self._output

    def reset(self) -> None:
        """Restore source zero recursive seeds and discard actual price history."""
        self._bars = 0
        self._prices = []  # Newest first: no invented zeros before the stream.
        self._bp1 = 0.0    # BP[1] at entry to the next update.
        self._bp2 = 0.0    # BP[2] at entry to the next update.
        self._output = BandpassOutput(math.nan, math.nan)

    def update(self, value: float) -> BandpassOutput:
        """Consume exactly one chronological completed close and return both plots.

        The public NaNs express availability only. They never enter feedback.
        All candidate arithmetic is checked before committing any state, so
        nonfinite inputs or arithmetic overflow leave the instance unchanged.
        """
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("input value must be finite")
        current_bar = self._bars + 1  # Explicit one-based standalone CurrentBar.

        # Source: calculate BP, then override BP=0 for CurrentBar<=3.
        # Branching avoids nonexistent Close[2] without changing retained state.
        if current_bar <= 3:
            bp = 0.0
        else:
            # Before adding this bar, _prices[1] is exactly Close[2].
            # Do NOT substitute a one-bar difference or zero-fill this history.
            difference = value - self._prices[1]
            bp = (0.5 * (1.0 - self._s1) * difference
                  + self._l1 * (1.0 + self._s1) * self._bp1
                  - self._s1 * self._bp2)
            if not math.isfinite(difference) or not math.isfinite(bp):
                raise ValueError("bandpass arithmetic must remain finite")

        # Retain current Close[0] through Close[length+1], inclusive.
        # This simple list maps directly to a bounded array/ring in a port.
        prices = [value] + self._prices[:self._length + 1]
        bpt = math.nan
        if len(prices) == self._length + 2:
            # Match the article's ONE-BASED workspace. Slots length+1 and
            # length+2 are initialized to zero on EVERY bar, not just reset.
            # All lower slots are overwritten oldest-to-newest. Therefore
            # shifting yesterday's Trunc array has no effect on the answer;
            # the Mesa listing omits that redundant shift altogether.
            trunc = [0.0] * (self._length + 3)  # Includes unused slot zero.
            for count in range(self._length, 0, -1):
                # Close[count-1] = prices[count-1]; Close[count+1] likewise.
                # The first iteration uses the oldest difference; the last
                # iteration (count=1) computes the current bar's result.
                difference = prices[count - 1] - prices[count + 1]
                trunc[count] = (0.5 * (1.0 - self._s1) * difference
                                + self._l1 * (1.0 + self._s1) * trunc[count + 1]
                                - self._s1 * trunc[count + 2])
                if not math.isfinite(difference) or not math.isfinite(trunc[count]):
                    raise ValueError("truncated bandpass arithmetic must remain finite")
            bpt = trunc[1]  # Exactly BPT=Trunc[1]; no extra normalization.

        # Commit AFTER both computations. _bp1/_bp2 always contain numeric
        # source state, including the three setup zeros, never public NaNs.
        self._prices = prices
        self._bp2 = self._bp1
        self._bp1 = bp
        self._bars = current_bar
        self._output = BandpassOutput(bpt, bp if current_bar > 3 else math.nan)
        return self._output


class ReferenceCase(NamedTuple):
    """A confirmed parameter triple and its portable 'What it tests' comment."""

    period: int
    bandwidth: float
    length: int
    what_it_tests: str


# All twenty parameter combinations were confirmed by the user on 2026-10-19.
# Twenty triples produce forty separate 252-value arrays; the output fields
# are not extra parameter combinations.
REFERENCE_CASES = (
    ReferenceCase(20, 0.1, 10, "Article, Mesa and TradeStation defaults."),
    ReferenceCase(20, 0.1, 1, "Minimum replay length: one two-bar price difference."),
    ReferenceCase(20, 0.1, 2, "Two-step replay and independently staged output warmups."),
    ReferenceCase(20, 0.1, 5, "Short truncation at one quarter of the center period."),
    ReferenceCase(20, 0.1, 20, "Truncation spanning one full nominal center cycle."),
    ReferenceCase(20, 0.1, 40, "Two-cycle replay with a longer finite memory."),
    ReferenceCase(20, 0.1, 97, "Maximum documented replay length and 99-close input history."),
    ReferenceCase(3, 0.1, 10, "Minimum supported center period near the Nyquist limit."),
    ReferenceCase(5, 0.1, 10, "Fast five-bar center cycle with two-cycle truncation."),
    ReferenceCase(10, 0.1, 10, "Ten-bar center cycle with equal replay length."),
    ReferenceCase(14, 0.1, 10, "Intermediate center period with the default finite memory."),
    ReferenceCase(30, 0.1, 10, "Slower thirty-bar center cycle with short truncation."),
    ReferenceCase(48, 0.1, 10, "Long center cycle with strong finite-memory damping."),
    ReferenceCase(252, 0.1, 10, "Full-record center period does not postpone filter availability."),
    ReferenceCase(20, 0.01, 10, "Very narrow bandwidth with slowly decaying standard ringing."),
    ReferenceCase(20, 0.25, 10, "Moderate bandwidth used by the Voss-related Traders' Tip."),
    ReferenceCase(20, 0.5, 10, "Wide bandwidth with faster standard-filter decay."),
    ReferenceCase(20, 1.0, 10, "One-hundred-percent bandwidth on the stable coefficient branch."),
    ReferenceCase(10, 0.25, 5, "Coupled fast center, moderate bandwidth and half-cycle replay."),
    ReferenceCase(48, 0.25, 24, "Coupled slow center, moderate bandwidth and half-cycle replay."),
)

OUTPUT_FIELDS = ("truncated_bandpass", "bandpass")
OUTPUT_TOKENS = ("BPT", "BP")


def _case_suffix(case: ReferenceCase) -> str:
    """P=period, B=bandwidth, L=length; decimal points become underscores."""
    bandwidth = format(case.bandwidth, ".15g").replace(".", "_")
    return f"P{case.period}_B{bandwidth}_L{case.length}"


def _parameter_comment(case: ReferenceCase) -> str:
    """The same second comment line precedes both components in all languages."""
    return f"period={case.period}, bandwidth={case.bandwidth:.15g}, length={case.length}"


def _float_literal(value: float, nan_literal: str) -> str:
    """Serialize with 15 significant digits; never round recursive state."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("expected data cannot contain infinity")
    literal = format(value, ".15g")
    # Rust Vec<f64> needs floating-point literals even for exact integers.
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _array_lines(values: list[float], indent: str, nan_literal: str) -> str:
    """Six portable literals per line keep generated data easy to review."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return "\n".join(indent + ", ".join(literals[index:index + 6]) + ","
                     for index in range(0, len(literals), 6))


def _load_literal_arrays(path: Path) -> dict[str, list[float]]:
    """Parse fixture arrays without importing or executing a data file."""
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
    """Append expected data; on reruns replace only the marked generated block."""
    begin = f"{comment} BEGIN GENERATED TRUNCATED BANDPASS FILTER EXPECTED DATA"
    end = f"{comment} END GENERATED TRUNCATED BANDPASS FILTER EXPECTED DATA"
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
    """Write confirmed Python cases, verify the file, then translate its data.

    Fixture I/O is tooling only; another language needs to port the class,
    not this generator. Each parameter triple gets BPT and BP arrays.
    """
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 closes and between 1 and 64 parameter combinations")
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
        indicator = TruncatedBandpassFilter(case.period, case.bandwidth, case.length)
        outputs = [indicator.update(value) for value in input_close]
        for field, token in zip(OUTPUT_FIELDS, OUTPUT_TOKENS):
            name = "EXPECTED_" + _case_suffix(case) + "_" + token
            values = [getattr(output, field) for output in outputs]
            raw_outputs[name] = values
            sections.append(f"# {case.what_it_tests}\n# {_parameter_comment(case)}\n{name} = [\n"
                            + _array_lines(values, "    ", "math.nan") + "\n]")
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # Reload and verify the ACTUAL Python output file before other exports.
    written = _load_literal_arrays(python_path)
    if {name: written[name] for name in original_inputs} != original_inputs:
        raise ValueError("generation changed the original input arrays")
    if {name for name in written if name.startswith("EXPECTED_")} != set(raw_outputs):
        raise ValueError("missing or unexpected expected array names")
    for case in REFERENCE_CASES:
        for token in OUTPUT_TOKENS:
            name = "EXPECTED_" + _case_suffix(case) + "_" + token
            values = written[name]
            warmup = case.length + 1 if token == "BPT" else 3
            if len(values) != 252:
                raise ValueError(f"{name} must contain 252 values")
            for index, (before, after) in enumerate(zip(raw_outputs[name], values)):
                if index < warmup:
                    if not math.isnan(before) or not math.isnan(after):
                        raise ValueError(f"{name} has an incorrect warmup NaN")
                elif not math.isfinite(after) or after != float(_float_literal(before, "nan")):
                    raise ValueError(f"{name} failed 15-digit serialization verification")

    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text().replace("package xxxx", "package truncatedbandpassfilter", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package truncatedbandpassfilter\n",
                                  'package truncatedbandpassfilter\n\nimport "math"\n', 1)
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
            values = written["EXPECTED_" + suffix]  # Export serialized Python values.
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
        # Expected Rust functions belong inside the existing #[cfg(test)]
        # testdata module, at the same scope as its copied input functions.
        if language == "rs" and "BEGIN GENERATED TRUNCATED BANDPASS FILTER EXPECTED DATA" not in path.read_text():
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
                        help="regenerate all twenty confirmed parameter combinations")
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
        # Minimal usage: one completed close per update; two named scalars.
        indicator = TruncatedBandpassFilter()  # period=20, bandwidth=0.1, length=10.
        outputs = [indicator.update(close) for close in INPUT_CLOSE]
        print(f"period={indicator.period}, bandwidth={indicator.bandwidth}, length={indicator.length}")
        print(f"{len(INPUT_CLOSE)} observations; first BP index=3, first BPT index={indicator.length + 1}")
        first = outputs[indicator.warmup_bars]
        print(f"First complete pair [{indicator.warmup_bars}]: BPT={first.truncated_bandpass:.15g}, BP={first.bandpass:.15g}")
        last = outputs[-1]
        print(f"Final: BPT={last.truncated_bandpass:.15g}, BP={last.bandpass:.15g}")
        indicator.reset()
        print("Primed after reset:", indicator.is_primed)
        print(f"Confirmed combinations: {len(REFERENCE_CASES)}")
