"""October 2021 Moving Average Difference (MAD): streaming Python master.

Authority: Ehlers' article and matching TradeStation/Pine/AIQ listings.
Only standard Python is used. See description.md for the source equations,
SMA/phase theory, explicit startup, percentage scale and platform differences.

update(close) returns a scalar percent: 100*(short SMA-long SMA)/long SMA.
It returns NaN until both complete SMA windows exist, and on any bar whose
complete long SMA is zero. The latter is an undefined ratio, not a new warmup.
No zero-padding, partial windows, EMA, signal line or clipping is added.

Run without flags to demonstrate the embedded 252 closes. The option
--generate-reference-data regenerates all sixteen confirmed parameter pairs
in the five copied language fixtures. Indicator updates do no I/O.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


OUTPUT_FIELDS = ('mad',)


def _length(value: int, name: str) -> int:
    """SMA windows are positive integer observation counts, not real periods."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f'{name} must be a positive integer')
    return value


class MovingAverageDifferenceState(NamedTuple):
    """Current complete SMA values and unscaled difference for port inspection."""

    short_average: float
    long_average: float
    difference: float
    mad: float


class MovingAverageDifference:
    """Difference of two simple moving averages normalized by the long SMA.

    Defaults short_length=8, long_length=23 reproduce the article inputs.
    Both lengths are independent positive integers. Equal and reversed lengths
    are allowed by the source formula, although the trend interpretation uses
    short_length<long_length. The parameter order is never silently swapped.

    The first max(short_length,long_length)-1 scalar outputs are unavailable.
    A zero long average returns NaN while leaving a primed instance primed.
    Finite negative and zero prices are accepted; positive prices are the
    usual domain for the article's bullish/bearish percentage interpretation.
    """

    def __init__(self, short_length: int = 8, long_length: int = 23) -> None:
        self._short_length = _length(short_length, 'short_length')
        self._long_length = _length(long_length, 'long_length')
        self._capacity = max(self._short_length, self._long_length)
        self.reset()

    @property
    def short_length(self) -> int:
        return self._short_length

    @property
    def long_length(self) -> int:
        return self._long_length

    @property
    def warmup_bars(self) -> int:
        """Leading NaN count due to missing history, not denominator validity."""
        return self._capacity - 1

    @property
    def is_primed(self) -> bool:
        """True when both full windows exist, even on an undefined-ratio bar."""
        return len(self._prices) == self._capacity

    @property
    def state(self) -> MovingAverageDifferenceState:
        """A shorter complete SMA can be inspected before the scalar primes."""
        return self._state

    def reset(self) -> None:
        """Forget all observed prices; parameters remain fixed."""
        self._prices = []
        self._next = 0
        self._state = MovingAverageDifferenceState(math.nan, math.nan, math.nan, math.nan)

    def _average(self, length: int) -> float:
        """Re-sum an actual complete window from newest price to oldest."""
        if len(self._prices) < length:
            return math.nan
        total = 0.0
        for lag in range(length):
            # _next identifies the NEXT slot to replace, so _next-1 is today's
            # close. During initial fill it is also the next insertion slot.
            index = (self._next - 1 - lag) % len(self._prices)
            total = total + self._prices[index]
        if not math.isfinite(total):
            raise ValueError('SMA sum must be finite')
        return total / length

    def update(self, close: float) -> float:
        """Consume one chronological close; return this bar's percentage MAD."""
        close = float(close)
        if not math.isfinite(close):
            # Reject missing/infinite values BEFORE altering the ring. A caller
            # must supply bars explicitly; missing observations do not count.
            raise ValueError('close must be finite')

        # One shared circular history holds max(S,L) prices; no full-stream
        # arrays and no dependency on another indicator implementation exist.
        if len(self._prices) < self._capacity:
            self._prices.append(close)
            self._next = len(self._prices) % self._capacity
        else:
            self._prices[self._next] = close
            self._next = (self._next + 1) % self._capacity

        # The article calls Average, not AverageFC, and supplies no internal
        # summation implementation. This master explicitly defines fresh,
        # ordinary newest-to-oldest sums. Do not use a rolling accumulator or
        # compensated sum when matching these fixtures: last bits can differ.
        short_average = self._average(self._short_length)
        long_average = self._average(self._long_length)
        difference = mad = math.nan
        if self.is_primed:
            # Keep the displayed operation order: subtract averages, multiply
            # by 100, THEN divide. The algebraic 100*(short/long-1) used by
            # Zorro has different floating-point cancellation/rounding.
            difference = short_average - long_average
            if long_average != 0.0:
                mad = 100.0 * difference / long_average
                if not math.isfinite(mad):
                    raise ValueError('MAD output must be finite')
            # Exact zero denominator is undefined even if difference is zero.
            # Return NaN without resetting, retaining an old output, applying
            # an epsilon, or inserting NaN into stored price history.

        self._state = MovingAverageDifferenceState(short_average, long_average, difference, mad)
        return mad


class ReferenceCase(NamedTuple):
    """A confirmed parameter pair with its portable What-it-tests comment."""

    short_length: int
    long_length: int
    what_it_tests: str


# All sixteen pairs were confirmed by the user on 2026-10-19. All prices in
# INPUT_CLOSE are positive, so post-warmup denominators are nonzero in fixtures.
REFERENCE_CASES = (
    ReferenceCase(8, 23, 'Article and TradeStation default; 15-bar length separation.'),
    ReferenceCase(5, 20, 'Article cycle example; 15-bar length separation.'),
    ReferenceCase(5, 30, 'Original cycle-display pair; 25-bar length separation.'),
    ReferenceCase(8, 16, 'Article fallback rule: long length is twice short length.'),
    ReferenceCase(1, 2, 'Minimum unequal windows and one-bar warmup.'),
    ReferenceCase(1, 23, 'Short average is the current close.'),
    ReferenceCase(2, 3, 'Adjacent small windows.'),
    ReferenceCase(23, 8, 'Reversed windows retain the designated normalization denominator.'),
    ReferenceCase(5, 10, 'Fast response with a two-to-one length ratio.'),
    ReferenceCase(10, 25, 'Longer smoothing with 15-bar length separation.'),
    ReferenceCase(15, 30, 'Monthly-scale two-to-one length ratio.'),
    ReferenceCase(20, 40, 'NeuroShell example lengths with article percentage scale.'),
    ReferenceCase(30, 60, 'Slower trend response.'),
    ReferenceCase(60, 120, 'Long-window trend response.'),
    ReferenceCase(126, 252, 'Long window equals the 252-bar record length.'),
    ReferenceCase(8, 8, 'Equal windows give exact zero after priming.'),
)


def _case_suffix(case: ReferenceCase) -> str:
    return f'SL{case.short_length}_LL{case.long_length}'


def _parameter_comment(case: ReferenceCase) -> str:
    return f'short_length={case.short_length}, long_length={case.long_length}'


def _expected_name(case: ReferenceCase, field: str) -> str:
    return 'EXPECTED_' + _case_suffix(case)


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write Python reference arrays, verify them, then translate their values.

    All generation is binary64 with rounding only during text emission. Each
    rerun replaces its own marked section and preserves the copied input data.
    Rendering helpers and file I/O are tooling; only the indicator is ported.
    """
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError('expected 252 closes and between 1 and 64 parameter cases')
    python_path = directory / 'test_testdata.py'
    if _load_literal_arrays(python_path)['INPUT_CLOSE'] != input_close:
        raise ValueError('embedded INPUT_CLOSE differs from the copied fixture')
    raw_outputs = {}
    sections = []
    for case in REFERENCE_CASES:
        # Precision and any source-selection options deliberately use the
        # documented master defaults; only the two SMA lengths vary in these fixtures.
        indicator = MovingAverageDifference(case.short_length, case.long_length)
        outputs = [indicator.update(price) for price in input_close]
        for field in OUTPUT_FIELDS:
            values = outputs if len(OUTPUT_FIELDS) == 1 else [getattr(v, field) for v in outputs]
            name = _expected_name(case, field)
            raw_outputs[name] = (values, indicator.warmup_bars)
            sections.append(
                f'# {case.what_it_tests}\n# {_parameter_comment(case)}\n'
                f'{name} = [\n{_array_lines(values, "    ", "math.nan")}\n]'
            )
    _write_generated_section(python_path, '\n\n'.join(sections), '#')

    # Reopen the generated Python data before using it as the source for all
    # other languages. Counts, unavailable prefixes and rounding are checked.
    written = _load_literal_arrays(python_path)
    if {n for n in written if n.startswith('EXPECTED_')} != set(raw_outputs):
        raise ValueError('missing or unexpected Python expected arrays')
    for name, (raw, warmup) in raw_outputs.items():
        values = written[name]
        if len(values) != 252:
            raise ValueError(f'{name} must have 252 values')
        if not all(math.isnan(v) for v in values[:warmup]):
            raise ValueError(f'{name} has an incorrect NaN prefix')
        if not all(math.isfinite(v) for v in values[warmup:]):
            raise ValueError(f'{name} must be finite after priming')
        for before, after in zip(raw, values):
            if math.isnan(before) and math.isnan(after):
                continue
            if not math.isclose(before, after, rel_tol=5e-14, abs_tol=5e-14):
                raise ValueError(f'{name} did not retain 15-digit precision')

    go_path = directory / 'testdata_test.go'
    text = go_path.read_text().replace('package xxxx', 'package movingaveragedifference', 1)
    if 'import "math"' not in text:
        preamble = 'package movingaveragedifference\n\nimport "math"\n'
        if not any(math.isnan(v) for name in raw_outputs for v in written[name]):
            # Go rejects unused imports. Keep the requested NaN helper import
            # without inserting artificial NaNs into defined startup outputs.
            preamble += '\n// Keep the NaN helper available; startup outputs are defined.\nvar _ = math.NaN\n'
        text = text.replace('package movingaveragedifference\n', preamble, 1)
    go_path.write_text(text)
    zig_path = directory / 'testdata.zig'
    text = zig_path.read_text()
    if 'const math = @import("std").math;' not in text:
        text = 'const math = @import("std").math;\n' + text
    if 'const nan = math.nan(f64);' not in text:
        text = text.replace('const math = @import("std").math;\n',
                            'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(text)

    translated = {'go': [], 'ts': [], 'rs': [], 'zig': []}
    for case in REFERENCE_CASES:
        for field in OUTPUT_FIELDS:
            name = _expected_name(case, field)
            suffix = name.removeprefix('EXPECTED_')
            values = written[name]  # Values come from the verified PYTHON file.
            comments = f'// {case.what_it_tests}\n// {_parameter_comment(case)}\n'
            translated['go'].append(comments + f'var expected{suffix} = []float64{{\n'
                                    + _array_lines(values, '\t', 'math.NaN()') + '\n}')
            translated['ts'].append(comments + f'export const expected{suffix}: number[] = [\n'
                                    + _array_lines(values, '    ', 'NaN') + '\n];')
            translated['rs'].append(comments + f'pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n'
                                    + _array_lines(values, '        ', 'f64::NAN') + '\n    ]\n}')
            translated['zig'].append(comments + f'pub fn expected{suffix}() [252]f64 {{\n    return .{{\n'
                                     + _array_lines(values, '        ', 'nan') + '\n    };\n}')
    for language, filename in (('go', 'testdata_test.go'), ('ts', 'testdata.ts'),
                               ('rs', 'testdata.rs'), ('zig', 'testdata.zig')):
        _write_generated_section(directory / filename, '\n\n'.join(translated[language]), '//')
    print(f'Verified {len(raw_outputs)} arrays of 252 values for {len(REFERENCE_CASES)} cases; wrote all five languages.')


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
    begin = f"{comment} BEGIN GENERATED MOVING AVERAGE DIFFERENCE EXPECTED DATA"
    end = f"{comment} END GENERATED MOVING AVERAGE DIFFERENCE EXPECTED DATA"
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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data', action='store_true',
                        help='regenerate all sixteen confirmed reference pairs')
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

    # Embedded input equals the copied 252-close fixture exactly.
    indicator = MovingAverageDifference(short_length=8, long_length=23)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print('Default first five primed values (indices 22-26):', ', '.join(
        _float_literal(value, 'NaN') for value in outputs[22:27]))
    print('Confirmed reference cases:')
    for case in REFERENCE_CASES:
        print(f'  {_case_suffix(case)}: {case.what_it_tests}')
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
