"""RSI-NET: MyRSI with Noise Elimination Technology, Ehlers, December 2020.

Standard-library streaming research master of the article/Mesa/TradeStation
calculation. update(close) returns RSIOutput(myrsi, net), both dimensionless.
MyRSI needs rsi_length+1 actual closes; NET needs net_length VALID MyRSIs.
Therefore first numeric indices are rsi_length and rsi_length+net_length-1.
Unavailable fields are NaN; unavailable MyRSIs NEVER enter the NET window.

Preserve the article's flat-window rule: retain the previous MyRSI if CU+CD
is zero, using an initial numeric seed of zero. Exact ties contribute zero
to Kendall tau-a. No Wilder smoothing, SuperSmoother or tie correction is used.
See description.md for full theory, source differences and porting guidance.

Run without arguments for the embedded 252-close example. All twenty cases
were confirmed by the user on 2026-10-19. --generate-reference-data writes
and verifies both outputs in all five language fixture files.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class RSIOutput(NamedTuple):
    """The article's two plots, with independent availability for each field.

    myrsi is the unsmoothed normalized gain/loss imbalance (Plot1).
    net is the Kendall rank correlation of recent MyRSI with time (Plot2).
    A positive NET means MyRSI tends to RISE, not that MyRSI is positive.
    """

    myrsi: float
    net: float


class RSINet:
    """Finite-window MyRSI followed by nonlinear Kendall tau-a against time.

    rsi_length: integer >=1; number of one-bar price changes; default 14.
    net_length: integer 2..100; number of valid MyRSI observations; default 14.

    Configuration is read-only. reset() keeps it but discards all observations.
    Each update uses O(rsi_length + net_length**2) work once fully primed and
    O(rsi_length + net_length) storage. Plain bounded lists, scalar arithmetic
    and nested loops make this a transparent master for other languages.
    """

    def __init__(self, rsi_length: int = 14, net_length: int = 14) -> None:
        # Python bool is an int subclass; exclude it from numeric parameters.
        if (isinstance(rsi_length, bool) or not isinstance(rsi_length, int)
                or rsi_length < 1):
            raise ValueError("rsi_length must be an integer of at least 1")
        # The source NET denominator is zero for length 1. Its one-based
        # EasyLanguage arrays X[100] and Y[100] have indices 0 through 100.
        if (isinstance(net_length, bool) or not isinstance(net_length, int)
                or not 2 <= net_length <= 100):
            raise ValueError("net_length must be an integer from 2 through 100")
        self._rsi_length = rsi_length
        self._net_length = net_length
        self._denominator = 0.5 * net_length * (net_length - 1)
        self.reset()

    @property
    def rsi_length(self) -> int:
        """Number of price changes; a full calculation needs one extra close."""
        return self._rsi_length

    @property
    def net_length(self) -> int:
        """Number of valid MyRSIs compared pairwise against chronological time."""
        return self._net_length

    @property
    def rsi_warmup_bars(self) -> int:
        """MyRSI NaN-prefix length; its first numeric zero-based index."""
        return self._rsi_length

    @property
    def net_warmup_bars(self) -> int:
        """NET NaN-prefix length; its first numeric zero-based index."""
        return self._rsi_length + self._net_length - 1

    @property
    def warmup_bars(self) -> int:
        """Prefix before both components are available; equal to NET warmup."""
        return self.net_warmup_bars

    @property
    def is_primed(self) -> bool:
        """True after the first full NET window; a flat valid window is primed."""
        return self._bars > self.warmup_bars

    @property
    def output(self) -> RSIOutput:
        """Last accepted pair; reading it does not advance the indicator."""
        return self._output

    def reset(self) -> None:
        """Clear both input windows and restore the source's MyRSI zero seed."""
        self._bars = 0
        self._prices = []        # Newest first; no fabricated price prehistory.
        self._rsi_history = []   # Newest first; contains VALID values only.
        self._myrsi = 0.0        # Persistent source variable, not a public NaN.
        self._output = RSIOutput(math.nan, math.nan)

    def update(self, value: float) -> RSIOutput:
        """Consume one finite chronological close and return MyRSI plus NET.

        Candidate state stays local until ALL arithmetic succeeds. Rejected
        inputs/overflow consume no bar and cannot contaminate a valid window.
        Finite input prices may be negative; no high/low/open values are needed.
        """
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("input value must be finite")
        prices = [value] + self._prices[:self._rsi_length]
        myrsi = self._myrsi
        history = self._rsi_history
        public_myrsi = math.nan
        net = math.nan

        if len(prices) == self._rsi_length + 1:
            cu = 0.0
            cd = 0.0
            # Source count=0..RSILength-1 is NEWEST to OLDEST. Recompute
            # totals each bar. Rolling sums or math.fsum change rounding,
            # which can even change NET ranks of nearly equal MyRSI values.
            for count in range(self._rsi_length):
                newer = prices[count]
                older = prices[count + 1]
                difference = newer - older
                if not math.isfinite(difference):
                    raise ValueError("price-difference arithmetic must remain finite")
                if difference > 0.0:
                    # Preserve literal source LEFT association:
                    # CU = CU + Close[count] - Close[count+1].
                    # CU + (newer-older) is algebraically equal but may round
                    # differently. Keep intermediate addition finite as well.
                    intermediate = cu + newer
                    cu = intermediate - older
                    if not math.isfinite(intermediate) or not math.isfinite(cu):
                        raise ValueError("closes-up accumulation must remain finite")
                if difference < 0.0:
                    # CD stores a POSITIVE magnitude. Source also uses left
                    # association: CD + Close[count+1] - Close[count].
                    intermediate = cd + older
                    cd = intermediate - newer
                    if not math.isfinite(intermediate) or not math.isfinite(cd):
                        raise ValueError("closes-down accumulation must remain finite")

            total = cu + cd
            imbalance = cu - cd
            if not math.isfinite(total) or not math.isfinite(imbalance):
                raise ValueError("MyRSI numerator and denominator must remain finite")
            if total != 0.0:
                myrsi = imbalance / total
                if not math.isfinite(myrsi):
                    raise ValueError("MyRSI arithmetic must remain finite")
            # No ELSE assignment: when total=0, source MyRSI retains its
            # previous value. At the first full all-flat window it is zero.
            # Such a retained zero/nonzero value IS a valid NET observation.
            public_myrsi = myrsi
            history = [myrsi] + self._rsi_history[:self._net_length - 1]

            if len(history) == self._net_length:
                numerator = 0  # Integer pair count, exactly representable here.
                # Source X[count]=MyRSI[count-1], Y[count]=-count. Y need
                # not be allocated because its pairwise direction is fixed.
                # Source count=2..M maps to zero-based older_index=1..M-1.
                for older_index in range(1, self._net_length):
                    for newer_index in range(older_index):
                        difference = history[older_index] - history[newer_index]
                        if not math.isfinite(difference):
                            raise ValueError("NET comparison arithmetic must remain finite")
                        # Num -= Sign(older-newer). Rising chronologically
                        # gives a NEGATIVE difference and hence POSITIVE NET.
                        if difference > 0.0:
                            numerator -= 1
                        elif difference < 0.0:
                            numerator += 1
                        # Exact equality contributes ZERO. Do not use an
                        # epsilon, round MyRSI or apply tau-b tie correction.
                net = numerator / self._denominator

        # Commit exactly one accepted bar. NaNs express PUBLIC availability
        # only and never replace _myrsi or enter its rank-history window.
        self._prices = prices
        self._rsi_history = history
        self._myrsi = myrsi
        self._bars += 1
        self._output = RSIOutput(public_myrsi, net)
        return self._output


class ReferenceCase(NamedTuple):
    """One confirmed parameter pair and its exact 'What it tests' comment."""

    rsi_length: int
    net_length: int
    what_it_tests: str


# All twenty parameter pairs were confirmed by the user on 2026-10-19.
# Twenty parameter pairs yield forty arrays (MYRSI and NET per pair).
REFERENCE_CASES = (
    ReferenceCase(14, 14, "Article, Mesa and TradeStation defaults."),
    ReferenceCase(1, 2, "Minimum RSI and NET windows; direction changes and exact ties."),
    ReferenceCase(2, 2, "Two price changes and the minimum pairwise NET comparison."),
    ReferenceCase(3, 3, "Small windows with three Kendall pairs and coarse NET levels."),
    ReferenceCase(5, 5, "Short matched windows for fast oscillator movements."),
    ReferenceCase(7, 7, "One-week-scale matched windows and intermediate NET granularity."),
    ReferenceCase(10, 10, "Ten-change RSI associated with a nominal twenty-bar cycle."),
    ReferenceCase(20, 20, "Longer matched windows with more pairwise direction evidence."),
    ReferenceCase(30, 30, "Slow matched windows and extended composite warmup."),
    ReferenceCase(14, 2, "Default RSI with NET determined only by the latest direction."),
    ReferenceCase(14, 5, "Default RSI with short nonlinear direction memory."),
    ReferenceCase(14, 30, "Default RSI with a longer rank-correlation horizon."),
    ReferenceCase(14, 100, "Maximum source NET array index and 4950 pair comparisons."),
    ReferenceCase(1, 14, "Sign-only RSI input creates many exact ties in the default NET window."),
    ReferenceCase(5, 14, "Fast RSI with the default NET horizon."),
    ReferenceCase(30, 14, "Slow RSI with the default NET horizon."),
    ReferenceCase(100, 100, "Long matched windows with the first NET output at index 199."),
    ReferenceCase(251, 2, "Record-edge RSI yields one final MyRSI and an entirely unprimed NET."),
    ReferenceCase(252, 14, "More RSI changes than the record supplies; both outputs stay NaN."),
    ReferenceCase(152, 100, "Composite record boundary: the first NET output is the final observation."),
)

OUTPUT_FIELDS = ("myrsi", "net")
OUTPUT_TOKENS = ("MYRSI", "NET")


def _case_suffix(case: ReferenceCase) -> str:
    """R=RSILength, N=NETLength; both configuration parameters are integers."""
    return f"R{case.rsi_length}_N{case.net_length}"


def _parameter_comment(case: ReferenceCase) -> str:
    """Second comment line, identical in all five languages for this pair."""
    return f"rsi_length={case.rsi_length}, net_length={case.net_length}"


def _float_literal(value: float, nan_literal: str) -> str:
    """Fifteen significant export digits; internal values are never rounded."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("expected values cannot be infinite")
    literal = format(value, ".15g")
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"  # Portable floating literals for Rust Vec<f64>.
    return literal


def _array_lines(values: list[float], indent: str, nan_literal: str) -> str:
    """Render a readable six-value row layout shared across all languages."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return "\n".join(indent + ", ".join(literals[index:index + 6]) + ","
                     for index in range(0, len(literals), 6))


def _load_literal_arrays(path: Path) -> dict[str, list[float]]:
    """Read Python fixture lists using AST; do not execute/import the fixture."""
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
    """Append expected data; replace only its marked block on regeneration."""
    begin = f"{comment} BEGIN GENERATED RSI NET EXPECTED DATA"
    end = f"{comment} END GENERATED RSI NET EXPECTED DATA"
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
    """Write confirmed Python cases, verify the actual file, then export it.

    This is fixture tooling, not streaming algorithm code to port. The other
    four languages get values re-read from the verified Python fixture.
    """
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 closes and one through 64 parameter pairs")
    if len({_case_suffix(case) for case in REFERENCE_CASES}) != len(REFERENCE_CASES):
        raise ValueError("reference parameter suffixes must be unique")
    python_path = directory / "test_testdata.py"
    original_inputs = {name: values for name, values in _load_literal_arrays(python_path).items()
                       if name.startswith("INPUT_")}
    if original_inputs.get("INPUT_CLOSE") != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from the copied fixture")

    sections = []
    raw_outputs = {}
    for case in REFERENCE_CASES:
        indicator = RSINet(case.rsi_length, case.net_length)
        outputs = [indicator.update(close) for close in input_close]
        for field, token in zip(OUTPUT_FIELDS, OUTPUT_TOKENS):
            name = "EXPECTED_" + _case_suffix(case) + "_" + token
            values = [getattr(output, field) for output in outputs]
            raw_outputs[name] = values
            sections.append(f"# {case.what_it_tests}\n# {_parameter_comment(case)}\n{name} = [\n"
                            + _array_lines(values, "    ", "math.nan") + "\n]")
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # Reopen and VERIFY THE WRITTEN PYTHON DATA before translating it.
    written = _load_literal_arrays(python_path)
    if {name: written[name] for name in original_inputs} != original_inputs:
        raise ValueError("input data changed during expected-data generation")
    if {name for name in written if name.startswith("EXPECTED_")} != set(raw_outputs):
        raise ValueError("missing or unexpected expected array names")
    for case in REFERENCE_CASES:
        for token in OUTPUT_TOKENS:
            name = "EXPECTED_" + _case_suffix(case) + "_" + token
            values = written[name]
            warmup = case.rsi_length if token == "MYRSI" else case.rsi_length + case.net_length - 1
            if len(values) != 252:
                raise ValueError(f"{name} must contain 252 values")
            for index, (before, after) in enumerate(zip(raw_outputs[name], values)):
                if index < warmup:
                    if not math.isnan(before) or not math.isnan(after):
                        raise ValueError(f"{name} has an incorrect warmup NaN")
                elif not math.isfinite(after) or after != float(_float_literal(before, "nan")):
                    raise ValueError(f"{name} failed 15-digit serialization verification")

    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text().replace("package xxxx", "package rsinet", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package rsinet\n", 'package rsinet\n\nimport "math"\n', 1)
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
            values = written["EXPECTED_" + suffix]
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
        # Rust functions belong INSIDE the copied #[cfg(test)] testdata module.
        if language == "rs" and "BEGIN GENERATED RSI NET EXPECTED DATA" not in path.read_text():
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
        # Example: one close per update, inspect either named output.
        indicator = RSINet()  # rsi_length=14, net_length=14.
        outputs = [indicator.update(close) for close in INPUT_CLOSE]
        print(f"rsi_length={indicator.rsi_length}, net_length={indicator.net_length}")
        print(f"{len(INPUT_CLOSE)} observations; first MyRSI index={indicator.rsi_warmup_bars}, first NET index={indicator.net_warmup_bars}")
        first = outputs[indicator.warmup_bars]
        print(f"First complete pair [{indicator.warmup_bars}]: MyRSI={first.myrsi:.15g}, NET={first.net:.15g}")
        last = outputs[-1]
        print(f"Final: MyRSI={last.myrsi:.15g}, NET={last.net:.15g}")
        indicator.reset()
        print("Primed after reset:", indicator.is_primed)
        print(f"Confirmed parameter combinations: {len(REFERENCE_CASES)}")
