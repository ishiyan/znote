"""Center of Gravity Oscillator: streaming research prototype master.

The default matches Ehlers' May 2002 article. centered=True matches Figure
5.1 in Cybernetic Analysis for Stocks and Futures (2004). Both outputs are
returned separately because the trigger requires one extra observed sample.

Only Python's standard library is used. Read description.md before porting;
in particular, preserve newest-first weights and the zero-denominator guard.
Run this file for an example. All 24 REFERENCE_CASES are confirmed; run
with --generate-reference-data to update all five language fixture files.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import re
import runpy
from typing import NamedTuple


class CenterOfGravityOutput(NamedTuple):
    """The two source plots: value is CG; trigger is the preceding valid CG."""

    value: float
    trigger: float


class CenterOfGravityOscillator:
    """Price-weighted position, with source-compatible sign and optional offset.

    length is an integer >= 1 (default 10). centered=False gives -Num/Denom;
    centered=True gives -Num/Denom + (length+1)/2, the book's convention.

    After length finite observations, value is available. The trigger first
    becomes available on observation length+1. Earlier fields return NaN.
    An input NaN returns (NaN, NaN) without changing any state; infinity is
    rejected. If a full window has Denom==0, keep the previous CG, initially
    zero, exactly as the conditional assignment in EasyLanguage specifies.
    """

    def __init__(self, length: int = 10, *, centered: bool = False) -> None:
        # Reject bool explicitly: Python considers it an int, other languages
        # do not. Fractional lengths cannot describe a finite sample window.
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError('length must be an integer of at least 1')
        if not isinstance(centered, bool):
            raise ValueError('centered must be a bool')
        self._length = length
        self._centered = centered
        # This is an exact half-integer, not an approximation to pi or sqrt(2).
        # The indicator has no transcendental constants to round or replace.
        self._offset = (length + 1) / 2.0 if centered else 0.0
        self.reset()

    @property
    def length(self) -> int:
        """Read-only configuration; change a period by constructing a new object."""
        return self._length

    @property
    def centered(self) -> bool:
        return self._centered

    @property
    def is_primed(self) -> bool:
        """Whether at least length finite observations have filled the window."""
        return self._count >= self._length

    @property
    def is_trigger_primed(self) -> bool:
        """Whether a preceding full-window result exists for the delayed plot."""
        return self._count > self._length

    def reset(self) -> None:
        """Restore startup, including the source's persistent CG(0) variable."""
        # A fixed ring is readily translated into Rust, Zig, Go or TypeScript.
        # Unobserved slots are never used for calculation: no zero padding.
        self._window = [0.0] * self._length
        self._next = 0
        # Clamp the count at length+1; only the two priming thresholds matter.
        self._count = 0
        self._last_value = 0.0

    def update(self, price: float) -> CenterOfGravityOutput:
        """Accept one chronological scalar price and return both plot values."""
        price = float(price)
        # The sources do not define missing-input semantics. Skipping NaN is
        # an explicit streaming convention consistent with the supplied repo.
        # The delay therefore counts accepted observations, not skipped calls.
        if math.isnan(price):
            return CenterOfGravityOutput(math.nan, math.nan)
        if not math.isfinite(price):
            raise ValueError('price must be finite or NaN')

        # Capture OLD CG before inserting or calculating the current sample.
        # On the first full window its predecessor is unavailable, not CG(0).
        trigger = self._last_value if self.is_primed else math.nan

        # _next points to the oldest slot once full, and to an empty slot during
        # startup. Advancing modulo length also works at the boundary length=1.
        self._window[self._next] = price
        self._next = (self._next + 1) % self._length
        self._count = min(self._count + 1, self._length + 1)
        if not self.is_primed:
            return CenterOfGravityOutput(math.nan, math.nan)

        numerator = 0.0
        denominator = 0.0
        # Match the source's count=0..Length-1 loop, including addition order.
        # Lag 0 is the newest price and has weight 1, NOT weight length.
        # Recompute BOTH sums: a rolling denominator drifts in the last bits.
        for lag in range(self._length):
            index = (self._next - 1 - lag) % self._length
            sample = self._window[index]
            numerator = numerator + (1 + lag) * sample
            denominator = denominator + sample

        # Keep the exact != 0 guard. Do not use an epsilon, smallest normal
        # float, return-zero fallback, or an unconditional centered offset.
        if denominator != 0.0:
            self._last_value = -numerator / denominator + self._offset
        return CenterOfGravityOutput(self._last_value, trigger)


class ReferenceCase(NamedTuple):
    """A confirmed parameter combination and the fixture's first comment line."""

    length: int
    centered: bool
    what_it_tests: str


# The user confirmed all 24 combinations on 2026-10-26. This gate records that
# confirmation so normal regeneration does not introduce a second approval.
REFERENCE_CASES_CONFIRMED = True

_LENGTH_CASES = (
    (1, 'Minimum window; constant value for nonzero prices and trigger startup.'),
    (2, 'Smallest moving balance point and earliest nonconstant crossover.'),
    (3, 'Short odd window; integer centering offset.'),
    (5, 'Short smoothed window and rapid response to price changes.'),
    (8, 'Eight-bar window used in the book example.'),
    (10, 'Default ten-bar window in the article and book listings.'),
    (14, 'Intermediate window between the default and twenty bars.'),
    (20, 'Longer window corresponding to half a forty-bar cycle.'),
    (32, 'Moderate smoothing and delayed warmup.'),
    (64, 'Long smoothing window over the shared price history.'),
    (126, 'Half-record window and substantial warmup.'),
    (252, 'Full-record window; one value and no primed trigger.'),
)

# Twelve lengths times two source conventions = 24 combinations, below 64.
# The two outputs yield 48 arrays, each aligned with all 252 INPUT_CLOSE bars.
REFERENCE_CASES = tuple(
    ReferenceCase(length, centered,
                  ('Book convention. ' if centered else 'Article convention. ') + purpose)
    for length, purpose in _LENGTH_CASES
    for centered in (False, True)
)


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
    start = comment + ' BEGIN GENERATED CENTER OF GRAVITY EXPECTED DATA'
    end = comment + ' END GENERATED CENTER OF GRAVITY EXPECTED DATA'
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


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write Python first, read it back, then transcribe its data to four peers.

    The input arrays in the copied files are preserved. This routine performs
    no indicator calculations in another language: Python is the sole master.
    """
    if not REFERENCE_CASES_CONFIRMED:
        raise RuntimeError('Reference parameter proposal awaits user confirmation')
    if len(input_close) != 252 or len(REFERENCE_CASES) > 64:
        raise ValueError('Expected 252 inputs and at most 64 reference combinations')

    python_blocks = ['NaN = math.nan\n']
    expected: dict[str, list[float]] = {}
    for case in REFERENCE_CASES:
        indicator = CenterOfGravityOscillator(case.length, centered=case.centered)
        results = [indicator.update(price) for price in input_close]
        # C is serialized as 0/1 to make names valid in every target language.
        suffix = f'L{case.length}_C{int(case.centered)}'
        for field, shortcut in (('value', 'CG'), ('trigger', 'TR')):
            name = f'EXPECTED_{suffix}_{shortcut}'
            values = [getattr(result, field) for result in results]
            expected[name] = values
            # Exactly two comments precede EACH expected array. The first is
            # the table's What it tests text; the second gives all parameters.
            python_blocks.append(
                f'# {case.what_it_tests}\n'
                f'# length={case.length}, centered={case.centered}; output={field}\n'
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
            text = re.sub(r'(?m)^package \w+$', 'package centerofgravityoscillator', text)
            if 'import "math"' not in text:
                text = text.replace('package centerofgravityoscillator\n',
                                    'package centerofgravityoscillator\n\nimport "math"\n', 1)
        path.write_text(_replace_generated(text, '\n'.join(blocks), '//',
                                           rust=(language == 'rs')), encoding='utf-8')
    print(f'Generated and verified {len(expected)} arrays of 252 values in five languages.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data', action='store_true',
                        help='generate the confirmed matrix in all five fixture files')
    args = parser.parse_args()

    # These are the 252 unmodified INPUT_CLOSE prices from the shared fixture.
    # Embed them here so the demonstration has no imports from another repo.
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

    # Example usage: use the close scalar specified for these fixtures. To use
    # the source's median price, instead call update((high + low) / 2.0).
    oscillator = CenterOfGravityOscillator(length=10)
    for index, price in enumerate(input_close):
        result = oscillator.update(price)
        if index in (8, 9, 10, 251):
            print(f'bar={index + 1}, value={result.value:.15g}, trigger={result.trigger:.15g}')

    if args.generate_reference_data:
        generate_reference_data(input_close, Path(__file__).resolve().parent)


if __name__ == '__main__':
    main()
