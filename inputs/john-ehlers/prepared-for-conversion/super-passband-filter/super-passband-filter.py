"""Streaming master of Ehlers' July 2016 Super Passband Filter.

Return raw passband, positive RMS, and negative RMS as a named tuple.
The numeric authority is the article's closed two-EMA difference recurrence,
including its newest-to-oldest RMS summation order. No numpy or pandas.
"""

from __future__ import annotations

import math
from typing import NamedTuple


class PassbandOutput(NamedTuple):
    """Price-unit outputs; RMS fields remain NaN until their window is full."""

    passband: float
    rms: float
    negative_rms: float


class SuperPassbandFilter:
    """Two-EMA difference plus RMS thresholds, consuming scalar raw prices.

    period1, period2: finite real values > 2.5, defaults 40 and 60.
    rms_window: positive integer, default 50. Current PB is in its window.
    Ordinary convex EMA behavior uses periods >= 5; smaller accepted periods
    have stable negative poles. Reversed/equal periods are explicitly valid.
    """

    def __init__(self, period1: float = 40.0, period2: float = 60.0,
                 rms_window: int = 50) -> None:
        self._period1 = float(period1)
        self._period2 = float(period2)
        for name, period in (("period1", self._period1), ("period2", self._period2)):
            # Exact stability: |1-5/P|<1 iff P>2.5 for positive finite P.
            # P=5 is the memoryless EMA boundary (alpha=1), not an error.
            if not math.isfinite(period) or period <= 2.5:
                raise ValueError(f"{name} must be finite and greater than 2.5")
        if isinstance(rms_window, bool) or not isinstance(rms_window, int) or rms_window < 1:
            raise ValueError("rms_window must be a positive integer")
        self._rms_window = rms_window

        # 5 is the author's HEURISTIC coefficient factor. It is not a rounded
        # spelling of 2*pi or another mathematical constant: retain exactly 5.
        a1 = 5.0 / self._period1
        a2 = 5.0 / self._period2
        self._q1 = 1.0 - a1
        self._q2 = 1.0 - a2
        self._input0 = a1 - a2
        self._input1 = a2 * self._q1 - a1 * self._q2
        self._feedback1 = self._q1 + self._q2
        self._feedback2 = self._q1 * self._q2
        self.reset()

    @property
    def period1(self) -> float:
        return self._period1

    @property
    def period2(self) -> float:
        return self._period2

    @property
    def rms_window(self) -> int:
        return self._rms_window

    @property
    def passband_warmup_bars(self) -> int:
        """Hide the initial PB seed; output PB from the second accepted bar."""
        return 1

    @property
    def rms_warmup_bars(self) -> int:
        """Need a full real window, including bar one's internally seeded PB."""
        return max(1, self._rms_window - 1)

    @property
    def warmup_bars(self) -> int:
        """Leading bars until ALL fields are visible; PB can appear earlier."""
        return self.rms_warmup_bars

    @property
    def is_passband_primed(self) -> bool:
        return self._count >= 2

    @property
    def is_primed(self) -> bool:
        """All fields available, not a claim that IIR transients have settled."""
        return self._count >= max(2, self._rms_window)

    def reset(self) -> None:
        """Reset price history, both PB states, the RMS ring, and bar count."""
        self._count = 0
        self._price1 = 0.0
        self._pb1 = self._pb2 = 0.0
        self._ring = [0.0] * self._rms_window
        self._next = 0

    def update(self, sample: float) -> PassbandOutput:
        """Consume a finite raw price, return PB/+RMS/-RMS with field priming."""
        sample = float(sample)
        if math.isnan(sample):
            # Omit this observation entirely. No shift, ring write, or count.
            return PassbandOutput(math.nan, math.nan, math.nan)
        if not math.isfinite(sample):
            raise ValueError("sample must be finite or NaN")

        if self._count == 0:
            # Seed both conceptual EMAs at the first real price; their PB
            # difference is zero. Store this initial PB in the RMS history.
            # Do not create a large artificial initial price-versus-zero jump.
            pb = 0.0
        else:
            # Preserve the article's four-term expression and order. Although
            # input1 algebraically equals -(a1-a2), that identity need not hold
            # at the last binary64 bit. Replacing this with delta*(price-old)
            # or computing two EMA values independently changes rounding.
            pb = (
                self._input0 * sample
                + self._input1 * self._price1
                + self._feedback1 * self._pb1
                - self._feedback2 * self._pb2
            )

        # Add CURRENT PB before calculating RMS. _next always points to the
        # oldest item to overwrite; after advancing it, _next-1 is newest.
        self._ring[self._next] = pb
        self._next = (self._next + 1) % self._rms_window
        self._price1 = sample
        self._pb2, self._pb1 = self._pb1, pb
        self._count += 1

        rms = math.nan
        if self.is_primed:
            # Recompute from zero every bar in EXACT article order, lag 0 to
            # W-1. Do not use a rolling total, compensated sum, fsum, or an
            # oldest-first traversal when matching these reference decimals.
            # Complexity is O(W) per update and O(W) storage, as in the source.
            total = 0.0
            index = (self._next - 1) % self._rms_window
            for _ in range(self._rms_window):
                value = self._ring[index]
                total = total + value * value
                index = (index - 1) % self._rms_window
            rms = math.sqrt(total / self._rms_window)

        # No normalization by RMS: PB and both threshold levels have price
        # units. Zero is a plot reference, not an additional calculated field.
        return PassbandOutput(pb if self.is_passband_primed else math.nan,
                              rms, -rms)


# All 20 reference cases were confirmed by the user on 2026-10-20.
REFERENCE_CASES_CONFIRMED = True
INDICATOR_SLUG = 'super-passband-filter'
MASTER_CLASS = SuperPassbandFilter
PARAMETER_SHORTCUTS = [('period1', 'P1'), ('period2', 'P2'), ('rms_window', 'W')]
OUTPUT_FIELDS = ('passband', 'rms', 'negative_rms')
OUTPUT_TOKENS = ('PB', 'RMS', 'NEG_RMS')
REFERENCE_CASES = (
    {'period1': 2.6, 'period2': 10, 'rms_window': 50, 'what_it_tests': 'Stable setting near the lower period boundary: negative-pole transient behavior.'},
    {'period1': 3, 'period2': 4, 'rms_window': 50, 'what_it_tests': 'Two stable negative EMA poles: unusual short-period response.'},
    {'period1': 4, 'period2': 3, 'rms_window': 50, 'what_it_tests': 'Reversed negative-pole pair: passband sign reverses while RMS is unchanged.'},
    {'period1': 5, 'period2': 10, 'rms_window': 50, 'what_it_tests': 'Memoryless fast EMA boundary: alpha1 equals one.'},
    {'period1': 10, 'period2': 20, 'rms_window': 50, 'what_it_tests': 'Short critical periods: faster response and weaker high-frequency smoothing.'},
    {'period1': 20, 'period2': 40, 'rms_window': 50, 'what_it_tests': 'Intermediate pair with a two-to-one period ratio.'},
    {'period1': 40, 'period2': 60, 'rms_window': 50, 'what_it_tests': 'Article default: forty/sixty periods and fifty-bar RMS thresholds.'},
    {'period1': 60, 'period2': 40, 'rms_window': 50, 'what_it_tests': 'Reversed article periods: exact sign symmetry and unchanged RMS.'},
    {'period1': 40, 'period2': 40, 'rms_window': 50, 'what_it_tests': 'Equal periods: passband and both primed RMS levels collapse to zero.'},
    {'period1': 40, 'period2': 41, 'rms_window': 50, 'what_it_tests': 'Nearly equal periods: small difference output and coefficient cancellation.'},
    {'period1': 40.5, 'period2': 60.5, 'rms_window': 50, 'what_it_tests': 'Fractional critical periods: preserve real-valued coefficients.'},
    {'period1': 80, 'period2': 120, 'rms_window': 50, 'what_it_tests': 'Longer period pair: slower recursive response.'},
    {'period1': 150, 'period2': 200, 'rms_window': 50, 'what_it_tests': 'Long-term pair: long transient and slowly varying passband.'},
    {'period1': 200, 'period2': 252, 'rms_window': 50, 'what_it_tests': 'Periods approaching the full input-record length: extended memory.'},
    {'period1': 40, 'period2': 60, 'rms_window': 1, 'what_it_tests': 'One-bar RMS: threshold equals absolute current passband from bar two.'},
    {'period1': 40, 'period2': 60, 'rms_window': 2, 'what_it_tests': 'Two-bar RMS: first complete window includes the initial zero passband seed.'},
    {'period1': 40, 'period2': 60, 'rms_window': 10, 'what_it_tests': 'Short RMS window: threshold follows recent squared amplitude rapidly.'},
    {'period1': 40, 'period2': 60, 'rms_window': 100, 'what_it_tests': 'Long RMS window: later threshold priming and longer amplitude memory.'},
    {'period1': 40, 'period2': 60, 'rms_window': 252, 'what_it_tests': 'Full-record RMS window: only the last threshold value is primed.'},
    {'period1': 40, 'period2': 60, 'rms_window': 300, 'what_it_tests': 'RMS window exceeds the record: PB is available but both threshold arrays stay NaN.'},
)

# Everything below this line is fixture-generation tooling. Port the indicator
# class above; these file-formatting helpers are optional.
from pathlib import Path
import argparse
import ast


def _read_arrays(path: Path) -> dict[str, list[float]]:
    """Load numeric list assignments safely, including explicit math.nan."""
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


def _parameter_token(value: float | int | bool) -> str:
    """10.0 -> 10; 10.5 -> 10_5; booleans -> 0/1. All tokens are identifiers."""
    return format(float(value), "g").replace(".", "_").replace("-", "m")


def _case_suffix(case: dict) -> str:
    # Case parameter order is fixed by the declared shortcut order, not sorted
    # alphabetically. That makes Python/Go/TS/Rust/Zig names easy to correlate.
    return "_".join(shortcut + _parameter_token(case[parameter])
                    for parameter, shortcut in PARAMETER_SHORTCUTS)


def _parameters(case: dict) -> dict:
    return {parameter: case[parameter] for parameter, _ in PARAMETER_SHORTCUTS}


def _parameter_comment(case: dict) -> str:
    return ", ".join(f"{parameter}={case[parameter]}" for parameter, _ in PARAMETER_SHORTCUTS)


def _literal(value: float, nan_literal: str) -> str:
    """Round only at serialization, to 15 significant decimal digits."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("infinite reference output cannot be serialized")
    literal = format(value, ".15g")
    # Rust and Zig arrays of f64 need float literals even for integral values.
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _rows(values: list[float], indent: str, nan_literal: str) -> str:
    literals = [_literal(value, nan_literal) for value in values]
    return "\n".join(indent + ", ".join(literals[index:index + 6]) + ","
                     for index in range(0, len(literals), 6))


def _replace_generated_section(path: Path, body: str, comment: str) -> None:
    """Append on first run; replace just the marked outputs on later runs."""
    begin = f"{comment} BEGIN GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA"
    end = f"{comment} END GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    section = begin + "\n\n" + body.rstrip() + "\n\n" + end
    if begin in original:
        start = original.index(begin)
        # A missing end marker raises instead of silently deleting file content.
        finish = original.index(end, start) + len(end)
        result = original[:start] + section + original[finish:]
    else:
        result = original.rstrip() + "\n\n" + section + "\n"
    path.write_text(result, encoding="utf-8")


def _output_warmup(indicator: SuperPassbandFilter, field: str) -> int:
    """Each output has its own availability: PB appears before RMS."""
    return indicator.passband_warmup_bars if field == 'passband' else indicator.rms_warmup_bars


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write/verify Python decimals, then copy them to the four port fixtures."""
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError("reference cases must be confirmed before generation")
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("require 252 closes and at most 64 confirmed cases")
    python_path = directory / 'test_testdata.py'
    if _read_arrays(python_path)['INPUT_CLOSE'] != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from copied fixture")

    raw_arrays = {}
    python_sections = []
    records = []
    for case in REFERENCE_CASES:
        indicator = MASTER_CLASS(**_parameters(case))
        outputs = [indicator.update(x) for x in input_close]
        for field, token in zip(OUTPUT_FIELDS, OUTPUT_TOKENS):
            values = [getattr(output, field) for output in outputs]
            warmup = _output_warmup(indicator, field)
            # warmup can exceed 252. In that case an entirely NaN RMS array
            # is deliberate: its configured real window never became full.
            if not all(math.isnan(value) for value in values[:warmup]):
                raise ValueError(f"{field}: incorrect NaN prefix")
            if not all(math.isfinite(value) for value in values[warmup:]):
                raise ValueError(f"{field}: nonfinite output after priming")
            suffix = _case_suffix(case) + '_' + token
            name = 'EXPECTED_' + suffix
            if name in raw_arrays:
                raise ValueError("duplicate reference name")
            raw_arrays[name] = values
            # Keep both comments exactly the same for every language. The
            # output field itself is unambiguously identified by the name.
            python_sections.append(
                f"# {case['what_it_tests']}\n# {_parameter_comment(case)}\n"
                f"{name} = [\n{_rows(values, '    ', 'math.nan')}\n]"
            )
            records.append((case, suffix))
    _replace_generated_section(python_path, '\n\n'.join(python_sections), '#')

    # Reread the file and check all 15-digit values, array lengths, and NaNs
    # before exporting its rounded decimals to any other language.
    written = _read_arrays(python_path)
    if {key for key in written if key.startswith('EXPECTED_')} != set(raw_arrays):
        raise ValueError("missing or extra Python expected arrays")
    for name, raw in raw_arrays.items():
        if len(written[name]) != 252:
            raise ValueError(f"{name}: incorrect length")
        for original, saved in zip(raw, written[name]):
            if math.isnan(original) and math.isnan(saved):
                continue
            if saved != float(_literal(original, 'math.nan')):
                raise ValueError(f"{name}: wrong 15-digit decimal")

    sections = {name: [] for name in ('testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')}
    for case, suffix in records:
        values = written['EXPECTED_' + suffix]
        comments = f"// {case['what_it_tests']}\n// {_parameter_comment(case)}\n"
        sections['testdata_test.go'].append(
            comments + f"var expected{suffix} = []float64{{\n"
            + _rows(values, '\t', 'math.NaN()') + '\n}'
        )
        sections['testdata.ts'].append(
            comments + f"export const expected{suffix}: number[] = [\n"
            + _rows(values, '    ', 'NaN') + '\n];'
        )
        sections['testdata.rs'].append(
            comments + f"pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n"
            + _rows(values, '        ', 'f64::NAN') + '\n    ]\n}'
        )
        sections['testdata.zig'].append(
            comments + f"pub fn expected{suffix}() [252]f64 {{\n    return .{{\n"
            + _rows(values, '        ', 'nan') + '\n    };\n}'
        )
    for filename, parts in sections.items():
        _replace_generated_section(directory / filename, '\n\n'.join(parts), '//')
    print(f"Verified {len(REFERENCE_CASES)} cases and {len(raw_arrays)} arrays of 252 values in all five languages.")


def _run_main(input_close: list[float]) -> None:
    """Demonstrate the three-field streaming API or generate confirmed data."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data', action='store_true',
                        help='write all confirmed expected arrays in the five fixture files')
    arguments = parser.parse_args()
    if arguments.generate_reference_data:
        generate_reference_data(input_close, Path(__file__).resolve().parent)
    else:
        indicator = SuperPassbandFilter()
        outputs = [indicator.update(x) for x in input_close]
        print(f'{INDICATOR_SLUG}: {len(outputs)} closes')
        for field in OUTPUT_FIELDS:
            first = next(index for index, value in enumerate(outputs)
                         if math.isfinite(getattr(value, field)))
            print(f'{field}: first valid bar {first+1}; value {_literal(getattr(outputs[first], field), "NaN")}')
        print(f'{len(REFERENCE_CASES)} parameter cases confirmed; use --generate-reference-data to regenerate.')


if __name__ == "__main__":
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
    _run_main(INPUT_CLOSE)
