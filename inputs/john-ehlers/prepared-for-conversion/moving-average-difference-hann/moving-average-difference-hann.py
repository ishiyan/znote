"""November 2021 MADH: Moving Average Difference with Hann windowing.

Self-contained standard-library streaming research master. The article and
matching TradeStation code are the authorities; see description.md for all
equations, window shape, truncation, startup and platform differences.

LongLength = trunc(ShortLength + DominantCycle/2). Defaults 8/27 give 21,
not the declared but overwritten LongLength(20). Two complete Hann averages
produce 100*(short-long)/long. If long is exactly zero, HOLD the preceding
MADH, initially zero, as the source conditional assignment requires.

The first LongLength-1 returned values are NaN: no partial windows or padding.
They are availability masks, never stored as the preceding MADH. Degree
cosines convert with full math.pi; no rounded Ehlers constants are needed.

Run without flags to stream the embedded 252 closes. The option
--generate-reference-data regenerates all sixteen confirmed cases in the fixtures.
The streaming class performs no file I/O and imports no third-party package.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple

PI = math.pi
OUTPUT_FIELDS = ('madh',)


class MovingAverageDifferenceHannState(NamedTuple):
    """Current complete filter values and the unmasked persisted MADH."""

    short_filter: float
    long_filter: float
    difference: float
    madh: float


class MovingAverageDifferenceHann:
    """Two normalized Hann FIR filters and the source percentage difference.

    short_length is a positive integer count, default 8. dominant_cycle is a
    finite real period >=1, default 27. Long length is integer truncation of
    their combined expression, with no rounding-to-nearest or adaptive cycle
    estimator. For all accepted values, long_length>=short_length.

    update(close) returns one float. It is unavailable until long_length actual
    closes exist; then zero denominators HOLD the source's previous finite
    result. Equal derived lengths give zero for nonzero denominators.
    """

    def __init__(self, short_length: int = 8, dominant_cycle: float = 27.0) -> None:
        if isinstance(short_length, bool) or not isinstance(short_length, int) or short_length < 1:
            raise ValueError('short_length must be a positive integer')
        if isinstance(dominant_cycle, bool):
            raise ValueError('dominant_cycle must be a finite real number >=1')
        dominant_cycle = float(dominant_cycle)
        if not math.isfinite(dominant_cycle) or dominant_cycle < 1.0:
            raise ValueError('dominant_cycle must be finite and at least 1')
        self._short_length = short_length
        self._dominant_cycle = dominant_cycle
        # IntPortion truncates toward zero. With positive values this is floor.
        # Preserve the complete source expression rather than rounding DC/2.
        combined = short_length + dominant_cycle / 2.0
        if not math.isfinite(combined):
            raise ValueError('derived long length must be finite')
        self._long_length = math.trunc(combined)
        self._short_weights, self._short_coefficient = self._kernel(short_length)
        self._long_weights, self._long_coefficient = self._kernel(self._long_length)
        self.reset()

    @staticmethod
    def _kernel(length: int) -> tuple[list[float], float]:
        """Precompute the source's 1-based interior Hann samples and sum."""
        weights = []
        coefficient = 0.0
        for count in range(1, length + 1):
            # Source Cosine takes degrees. The denominator is Length+1,
            # NOT Length-1; the stored endpoint weights are therefore nonzero.
            weight = 1.0 - math.cos(math.radians(360.0 * count / (length + 1)))
            weights.append(weight)
            coefficient = coefficient + weight
        # For valid finite integer lengths this is mathematically Length+1,
        # but preserve the actual sequential sum instead of that shortcut.
        return weights, coefficient

    @property
    def short_length(self) -> int:
        return self._short_length

    @property
    def dominant_cycle(self) -> float:
        return self._dominant_cycle

    @property
    def long_length(self) -> int:
        """Derived count, read-only: this is not an independent input."""
        return self._long_length

    @property
    def warmup_bars(self) -> int:
        return self._long_length - 1

    @property
    def is_primed(self) -> bool:
        """History availability is independent of whether the denominator is 0."""
        return len(self._prices) == self._long_length

    @property
    def state(self) -> MovingAverageDifferenceHannState:
        return self._state

    def reset(self) -> None:
        """Restart all price history and the source's initial MADH(0) state."""
        self._prices = []
        self._next = 0
        self._madh = 0.0
        self._state = MovingAverageDifferenceHannState(math.nan, math.nan, math.nan, 0.0)

    def _filter(self, weights: list[float], coefficient: float) -> float:
        """Compute a full-window FIR using newest-to-oldest source arithmetic."""
        if len(self._prices) < len(weights):
            return math.nan
        total = 0.0
        for lag, weight in enumerate(weights):
            index = (self._next - 1 - lag) % len(self._prices)
            total = total + weight * self._prices[index]
        if not math.isfinite(total):
            raise ValueError('weighted filter sum must be finite')
        # Source starts Filt=0, accumulates a numerator and normalizes only
        # when coef<>0. The valid interior Hann always has a positive coef.
        return total / coefficient if coefficient != 0.0 else total

    def update(self, close: float) -> float:
        """Consume one finite chronological close and return this bar's MADH."""
        close = float(close)
        if not math.isfinite(close):
            # Reject absent/nonfinite inputs BEFORE any history changes.
            raise ValueError('close must be finite')
        if len(self._prices) < self._long_length:
            self._prices.append(close)
            self._next = len(self._prices) % self._long_length
        else:
            self._prices[self._next] = close
            self._next = (self._next + 1) % self._long_length

        short_filter = self._filter(self._short_weights, self._short_coefficient)
        long_filter = self._filter(self._long_weights, self._long_coefficient)
        difference = math.nan
        if self.is_primed:
            difference = short_filter - long_filter
            if long_filter != 0.0:
                # Preserve source order: subtract, multiply by 100, divide.
                # Do not rewrite as 100*(short/long-1) or clip the result.
                madh = 100.0 * difference / long_filter
                if not math.isfinite(madh):
                    raise ValueError('MADH output must be finite')
                self._madh = madh
            # No else assignment: If Filt2<>0 THEN MADH=... intentionally
            # persists MADH. It initially equals zero, including flat inputs.
            # Do not copy the October MAD's undefined-ratio NaN policy here.

        self._state = MovingAverageDifferenceHannState(short_filter, long_filter, difference, self._madh)
        return self._madh if self.is_primed else math.nan


class ReferenceCase(NamedTuple):
    """A confirmed source-input pair and the exact portable test comment."""

    short_length: int
    dominant_cycle: float
    what_it_tests: str


# All sixteen cases were confirmed on 2026-10-19; only these source inputs vary.
REFERENCE_CASES = (
    ReferenceCase(8, 27.0, 'Article and TradeStation default; derived long length 21.'),
    ReferenceCase(8, 26.0, 'Even cycle derives the same long length as the default.'),
    ReferenceCase(8, 28.0, 'Next truncation boundary increases the long length to 22.'),
    ReferenceCase(8, 27.5, 'Fractional cycle retains the default truncated long length.'),
    ReferenceCase(1, 1.0, 'Minimum inputs derive equal one-bar filters.'),
    ReferenceCase(1, 2.0, 'Current-close short filter and minimum unequal lengths.'),
    ReferenceCase(2, 4.0, 'TradingView minimum inputs and short Hann kernels.'),
    ReferenceCase(5, 30.0, 'Thirty-bar cycle with derived long length 20.'),
    ReferenceCase(8, 16.0, 'Unknown-cycle fallback yields a two-to-one length ratio.'),
    ReferenceCase(10, 30.0, 'Longer short filter with a 15-bar length separation.'),
    ReferenceCase(15, 30.0, 'Monthly-scale two-to-one length ratio.'),
    ReferenceCase(20, 40.0, 'Slower swing response.'),
    ReferenceCase(30, 60.0, 'Longer smoothing windows.'),
    ReferenceCase(60, 120.0, 'Long filter history.'),
    ReferenceCase(126, 252.0, 'Derived long window equals the 252-bar input record.'),
    ReferenceCase(8, 1.0, 'Positive cycle truncates to equal eight-bar filters.'),
)


def _case_suffix(case: ReferenceCase) -> str:
    token = format(case.dominant_cycle, 'g').replace('.', '_')
    return f'SL{case.short_length}_DC{token}'


def _parameter_comment(case: ReferenceCase) -> str:
    length = math.trunc(case.short_length + case.dominant_cycle / 2.0)
    return f'short_length={case.short_length}, dominant_cycle={case.dominant_cycle:g}, long_length={length}'


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
        # documented master defaults; only ShortLength and DominantCycle vary in these fixtures.
        indicator = MovingAverageDifferenceHann(case.short_length, case.dominant_cycle)
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
    text = go_path.read_text().replace('package xxxx', 'package movingaveragedifferencehann', 1)
    if 'import "math"' not in text:
        preamble = 'package movingaveragedifferencehann\n\nimport "math"\n'
        if not any(math.isnan(v) for name in raw_outputs for v in written[name]):
            # Go rejects unused imports. Keep the requested NaN helper import
            # without inserting artificial NaNs into defined startup outputs.
            preamble += '\n// Keep the NaN helper available; startup outputs are defined.\nvar _ = math.NaN\n'
        text = text.replace('package movingaveragedifferencehann\n', preamble, 1)
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
    begin = f"{comment} BEGIN GENERATED MOVING AVERAGE DIFFERENCE HANN EXPECTED DATA"
    end = f"{comment} END GENERATED MOVING AVERAGE DIFFERENCE HANN EXPECTED DATA"
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
                        help='regenerate all sixteen confirmed reference cases')
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

    # The demonstration consumes the exact copied 252 closes, once per bar.
    indicator = MovingAverageDifferenceHann(short_length=8, dominant_cycle=27)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print('Default derived long length:', indicator.long_length)
    print('Default first five primed values (indices 20-24):', ', '.join(
        _float_literal(value, 'NaN') for value in outputs[20:25]))
    print('Confirmed reference cases:')
    for case in REFERENCE_CASES:
        print(f'  {_case_suffix(case)}: {case.what_it_tests}')
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
