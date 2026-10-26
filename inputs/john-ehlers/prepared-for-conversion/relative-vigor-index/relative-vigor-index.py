"""Relative Vigor Index: portable streaming research prototype master.

The default length=10, trigger_mode='fir' matches Ehlers' January 2002
article. trigger_mode='lag' matches the book's EasyLanguage trigger; choose
length=8 with it for the book's prose/EFS default. Read description.md for
the complete theory, source differences and per-output startup conventions.

RVI requires an OHLC bar, not a single close price. No framework, NumPy or
pandas is needed. The example embeds the 252 shared close prices and uses
their matching open/high/low arrays in the copied local test_testdata.py.
All 28 combinations are confirmed. Run with --generate-reference-data to
regenerate the expected arrays in all five language fixture files.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import re
import runpy
from typing import NamedTuple


class PriceBar(NamedTuple):
    """One completed OHLC observation; fields use conventional OHLC order."""

    open: float
    high: float
    low: float
    close: float


class RelativeVigorOutput(NamedTuple):
    """The published plots, with separate availability for each field."""

    value: float
    signal: float


def _fir4(window: list[float], next_index: int) -> float:
    """Apply the exact source [1,2,2,1]/6 expression to a complete four-ring.

    next_index is the next insertion slot, hence next_index-1 is newest.
    Retain the written addition order and divide by 6 after adding all terms.
    A double SMA is equivalent algebraically, but can round differently.
    """
    newest = window[(next_index - 1) % 4]
    previous = window[(next_index - 2) % 4]
    older = window[(next_index - 3) % 4]
    oldest = window[(next_index - 4) % 4]
    return (newest + 2.0 * previous + 2.0 * older + oldest) / 6.0


class RelativeVigorIndex:
    """Independently filter and sum candle bodies/ranges, then divide.

    update(PriceBar(open, high, low, close)) returns (value, signal). length
    is an integer >=1. trigger_mode is 'fir' (article) or 'lag' (book).

    The first length+2 values are NaN: a length-window of filtered components
    requires length+3 raw bars. The article signal needs three more RVI
    values, and the book signal needs one more. Missing history is not padded.

    Any NaN field skips the whole bar without changing state; infinity is
    rejected. A zero denominator retains the previous RVI, initially zero,
    exactly like the published EasyLanguage conditional assignment.
    """

    def __init__(self, length: int = 10, *, trigger_mode: str = 'fir') -> None:
        # Python bool is an int subclass, but is not a meaningful window size.
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError('length must be an integer of at least 1')
        if trigger_mode not in ('fir', 'lag'):
            raise ValueError('trigger_mode must be "fir" or "lag"')
        self._length = length
        self._trigger_mode = trigger_mode
        self.reset()

    @property
    def length(self) -> int:
        """Read-only period; construct another object to change configuration."""
        return self._length

    @property
    def trigger_mode(self) -> str:
        return self._trigger_mode

    @property
    def is_primed(self) -> bool:
        """Whether the main RVI has a complete length-window of components."""
        return self._filtered_count == self._length

    @property
    def is_signal_primed(self) -> bool:
        """Whether enough fully calculated RVI values exist for the signal."""
        required = 4 if self._trigger_mode == 'fir' else 2
        return self._rvi_count >= required

    def reset(self) -> None:
        """Restore every stage, including persistent source variable RVI(0)."""
        # Two raw four-rings implement the identical FIRs on body and range.
        self._changes = [0.0] * 4
        self._ranges = [0.0] * 4
        self._raw_next = 0
        self._raw_count = 0
        # The summation rings store independently FILTERED values. Averaging
        # raw per-bar ratios would be a different indicator.
        self._filtered_changes = [0.0] * self._length
        self._filtered_ranges = [0.0] * self._length
        self._filtered_next = 0
        self._filtered_count = 0
        # Keep complete RVI values only, not NaN startup placeholders.
        self._rvi_history = [0.0] * 4
        self._rvi_next = 0
        self._rvi_count = 0
        self._last_value = 0.0

    def update(self, bar: PriceBar) -> RelativeVigorOutput:
        """Accept one OHLC input value, in chronological order, without padding."""
        # Convert and validate all fields BEFORE modifying any stage. We do
        # not invent open/high/low from the close: they are independent data.
        open_price, high, low, close = (float(value) for value in bar)
        prices = (open_price, high, low, close)
        if any(math.isnan(value) for value in prices):
            return RelativeVigorOutput(math.nan, math.nan)
        if not all(math.isfinite(value) for value in prices):
            raise ValueError('OHLC fields must be finite or NaN')

        # Stage 1: differences, which encode candle direction and its scale.
        self._changes[self._raw_next] = close - open_price
        self._ranges[self._raw_next] = high - low
        self._raw_next = (self._raw_next + 1) % 4
        self._raw_count = min(self._raw_count + 1, 4)
        if self._raw_count < 4:
            return RelativeVigorOutput(math.nan, math.nan)

        # Stage 2: eliminate two-bar and three-bar components before summing.
        filtered_change = _fir4(self._changes, self._raw_next)
        filtered_range = _fir4(self._ranges, self._raw_next)
        self._filtered_changes[self._filtered_next] = filtered_change
        self._filtered_ranges[self._filtered_next] = filtered_range
        self._filtered_next = (self._filtered_next + 1) % self._length
        self._filtered_count = min(self._filtered_count + 1, self._length)
        if not self.is_primed:
            return RelativeVigorOutput(math.nan, math.nan)

        # Stage 3: preserve the article's newest-first, plain summation order.
        # Recomputing both sums avoids rolling-total drift. The sums are NOT
        # sums of individual ratios and NOT true ranges with overnight gaps.
        numerator = 0.0
        denominator = 0.0
        for lag in range(self._length):
            index = (self._filtered_next - 1 - lag) % self._length
            numerator = numerator + self._filtered_changes[index]
            denominator = denominator + self._filtered_ranges[index]

        # Capture the old value before assigning the current result. A value
        # held across a zero denominator still counts as an available RVI.
        previous = self._last_value if self._rvi_count else math.nan
        if denominator != 0.0:
            self._last_value = numerator / denominator

        # Stage 4: signal-specific history. Both modes share the same RVI.
        self._rvi_history[self._rvi_next] = self._last_value
        self._rvi_next = (self._rvi_next + 1) % 4
        self._rvi_count = min(self._rvi_count + 1, 4)
        if self._trigger_mode == 'lag':
            signal = previous
        elif self.is_signal_primed:
            signal = _fir4(self._rvi_history, self._rvi_next)
        else:
            signal = math.nan
        return RelativeVigorOutput(self._last_value, signal)


class ReferenceCase(NamedTuple):
    """One confirmed parameter combination and its exact fixture comment."""

    length: int
    trigger_mode: str
    what_it_tests: str


# The user confirmed all 28 RVI combinations on 2026-10-26. Record that
# confirmation so regeneration does not introduce a second approval.
REFERENCE_CASES_CONFIRMED = True

_LENGTH_CASES = (
    (1, 'Minimum summation window; the four-bar input FIR remains active.'),
    (2, 'Shortest even summation window and early startup.'),
    (3, 'Shortest nontrivial odd summation window.'),
    (5, 'Short period used in the Wave Wise example.'),
    (8, 'Default suggested by the book prose and EFS.'),
    (9, 'Odd period discussed in the article frequency-response comparison.'),
    (10, 'Default in the article, TradeStation Tips and book EasyLanguage.'),
    (14, 'Intermediate even window and moderate smoothing.'),
    (20, 'Longer smoothing; upper length offered by the MetaStock example.'),
    (64, 'Long window over the shared OHLC record.'),
    (246, 'Article FIR signal first becomes available on the final input bar.'),
    (248, 'Book delayed signal first becomes available on the final input bar.'),
    (249, 'Only one RVI value is available and neither signal is primed.'),
    (252, 'Entire record remains unprimed because three extra raw bars are needed.'),
)

# Fourteen lengths x two published signal modes = 28 combinations, 56 arrays.
REFERENCE_CASES = tuple(
    ReferenceCase(length, mode,
                  ('Article FIR signal. ' if mode == 'fir' else 'Book delayed signal. ') + purpose)
    for length, purpose in _LENGTH_CASES
    for mode in ('fir', 'lag')
)

# Mode names are descriptive in the API and numeric in portable array names.
TRIGGER_MODE_CODES = {'fir': 0, 'lag': 1}


def _float_literal(value: float, nan_literal: str) -> str:
    """Round only serialized data, to 15 significant decimal digits."""
    if math.isnan(value):
        return nan_literal
    literal = format(value, '.15g')
    # Rust and Zig need real literals in explicitly f64 arrays, even for zero.
    if '.' not in literal and 'e' not in literal.lower():
        literal += '.0'
    return literal


def _array_body(values: list[float], nan_literal: str, indent: str) -> str:
    """Ten entries per line for readable diffs and consistent language copies."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return '\n'.join(indent + ', '.join(literals[i:i + 10]) + ','
                     for i in range(0, len(literals), 10))


def _replace_generated(text: str, body: str, comment: str, *, rust: bool = False) -> str:
    """Append once; subsequent runs replace only our marked expected-data block."""
    start = comment + ' BEGIN GENERATED RELATIVE VIGOR INDEX EXPECTED DATA'
    end = comment + ' END GENERATED RELATIVE VIGOR INDEX EXPECTED DATA'
    # A blank before the closing marker also matches gofmt's separation of
    # a declaration from a following standalone comment.
    block = start + '\n' + body.rstrip() + '\n\n' + end + '\n'
    if start in text:
        begin = text.index(start)
        finish = text.index(end, begin) + len(end)
        return text[:begin] + block.rstrip('\n') + text[finish:]
    if rust:
        # The copied file puts its helpers in #[cfg(test)] pub mod testdata.
        # Add expected functions inside that module, before its final brace.
        closing = text.rfind('}')
        return text[:closing].rstrip() + '\n\n' + block + text[closing:]
    return text.rstrip() + '\n\n' + block


def _fixture_bars(input_close: list[float], directory: Path) -> list[PriceBar]:
    """Pair the requested close inputs with matching real OHLC fixture fields.

    A close-only surrogate cannot reproduce the published RVI. The shared
    test fixture already supplies all four fields, so no data is invented.
    """
    fixture = runpy.run_path(str(directory / 'test_testdata.py'))
    if input_close != fixture['INPUT_CLOSE']:
        raise ValueError('Embedded INPUT_CLOSE differs from the copied fixture')
    for name in ('INPUT_CLOSE', 'INPUT_OPEN', 'INPUT_HIGH', 'INPUT_LOW'):
        if len(fixture[name]) != 252:
            raise ValueError(f'{name} must contain 252 prices')
    return [PriceBar(open_price, high, low, close)
            for open_price, high, low, close in zip(
                fixture['INPUT_OPEN'], fixture['INPUT_HIGH'],
                fixture['INPUT_LOW'], input_close)]


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write Python first, read it back, then transcribe its data to four peers.

    The input arrays in the copied files are preserved. This routine performs
    no indicator calculations in another language: Python is the sole master.
    """
    if not REFERENCE_CASES_CONFIRMED:
        raise RuntimeError('Reference parameter proposal awaits user confirmation')
    if len(input_close) != 252 or len(REFERENCE_CASES) > 64:
        raise ValueError('Expected 252 inputs and at most 64 reference combinations')

    bars = _fixture_bars(input_close, directory)
    python_blocks = ['NaN = math.nan\n']
    expected: dict[str, list[float]] = {}
    for case in REFERENCE_CASES:
        indicator = RelativeVigorIndex(case.length, trigger_mode=case.trigger_mode)
        results = [indicator.update(bar) for bar in bars]
        # M is serialized as 0/1 for the article FIR / book delayed signal.
        suffix = f'L{case.length}_M{TRIGGER_MODE_CODES[case.trigger_mode]}'
        for field, shortcut in (('value', 'RVI'), ('signal', 'SIG')):
            name = f'EXPECTED_{suffix}_{shortcut}'
            values = [getattr(result, field) for result in results]
            expected[name] = values
            # Exactly two comments precede EACH expected array. The first is
            # the table's What it tests text; the second gives all parameters.
            python_blocks.append(
                f'# {case.what_it_tests}\n'
                f'# length={case.length}, trigger_mode={case.trigger_mode}; output={field}\n'
                f'{name} = [\n{_array_body(values, "NaN", "    ")}\n]\n')

    python_path = directory / 'test_testdata.py'
    original = python_path.read_text(encoding='utf-8')
    original_inputs = runpy.run_path(str(python_path))
    if original_inputs['INPUT_CLOSE'] != input_close:
        raise ValueError('Embedded INPUT_CLOSE differs from the copied fixture')
    python_path.write_text(_replace_generated(original, '\n'.join(python_blocks), '#'),
                           encoding='utf-8')

    # Verify actual persisted data, including the per-output warmup masks.
    persisted = runpy.run_path(str(python_path))
    for name, values in expected.items():
        actual = persisted[name]
        if len(actual) != 252:
            raise AssertionError(f'{name} must contain 252 outputs')
        for index, (before, after) in enumerate(zip(values, actual)):
            same = (math.isnan(before) and math.isnan(after)) or math.isclose(
                before, after, rel_tol=5e-14, abs_tol=1e-14)
            if not same:
                raise AssertionError(f'{name}[{index}] differs after serialization')
    for key in ('INPUT_CLOSE', 'INPUT_HIGH', 'INPUT_LOW', 'INPUT_OPEN'):
        if persisted[key] != original_inputs[key]:
            raise AssertionError(f'{key} was modified')

    # Read comments and names from the Python file, instead of inventing a
    # second set of target-language descriptions. Values also come from it.
    entries = re.findall(
        r'^# ([^\n]+)\n# ([^\n]+)\n(EXPECTED_[A-Z0-9_]+) = \[\n',
        python_path.read_text(encoding='utf-8'), flags=re.MULTILINE)
    if len(entries) != len(expected):
        raise AssertionError('Missing expected arrays or two-line comments')

    for language, filename, nan_literal, indent in (
        ('go', 'testdata_test.go', 'math.NaN()', '\t'),
        ('ts', 'testdata.ts', 'NaN', '    '),
        ('rs', 'testdata.rs', 'f64::NAN', '            '),
        ('zig', 'testdata.zig', 'nan', '        '),
    ):
        blocks = []
        for purpose, parameters, name in entries:
            suffix = name.removeprefix('EXPECTED_')
            target_name = 'expected' + suffix
            body = _array_body(persisted[name], nan_literal, indent)
            comments = f'// {purpose}\n// {parameters}\n'
            if language == 'go':
                block = f'{comments}var {target_name} = []float64{{\n{body}\n}}\n'
            elif language == 'ts':
                block = f'{comments}export const {target_name}: number[] = [\n{body}\n];\n'
            elif language == 'rs':
                target_name = 'expected_' + suffix.lower()
                block = (f'{comments}    pub fn {target_name}() -> Vec<f64> {{\n'
                         f'        vec![\n{body}\n        ]\n    }}\n')
            else:
                block = (f'{comments}pub fn {target_name}() [252]f64 {{\n'
                         f'    return .{{\n{body}\n    }};\n}}\n')
            blocks.append(block)

        path = directory / filename
        text = path.read_text(encoding='utf-8')
        if language == 'go':
            text = re.sub(r'(?m)^package \w+$', 'package relativevigorindex', text)
            if 'import "math"' not in text:
                text = text.replace('package relativevigorindex\n',
                                    'package relativevigorindex\n\nimport "math"\n', 1)
        path.write_text(_replace_generated(text, '\n'.join(blocks), '//',
                                           rust=(language == 'rs')), encoding='utf-8')
    print(f'Generated and verified {len(expected)} arrays of 252 values in five languages.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data', action='store_true',
                        help='generate the confirmed matrix in all five fixture files')
    args = parser.parse_args()

    # Embed all 252 requested closing prices. The local fixture supplies their
    # matching opens, highs and lows; the calculation always consumes OHLC.
    input_close = [
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
    directory = Path(__file__).resolve().parent
    bars = _fixture_bars(input_close, directory)

    # Example streaming usage: one PriceBar in, two named output fields out.
    indicator = RelativeVigorIndex(length=10, trigger_mode='fir')
    for index, bar in enumerate(bars):
        result = indicator.update(bar)
        if index in (11, 12, 13, 15, 251):
            print(f'bar={index + 1}, value={result.value:.15g}, signal={result.signal:.15g}')

    if args.generate_reference_data:
        generate_reference_data(input_close, directory)


if __name__ == '__main__':
    main()
