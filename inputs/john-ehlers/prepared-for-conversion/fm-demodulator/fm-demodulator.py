"""FM Demodulator, John F. Ehlers, TASC May 2021; streaming research master.

Compute Close-Open, multiply by the source's fixed gain 10, clamp to [-1,1],
then smooth with the two-pole SuperSmoother. Use full-precision sqrt(2) and pi,
as requested, rather than the printed 1.414 and 3.14159 approximations.
The first TWO derivative observations return RAW Deriv and seed recursive SS;
the third derivative observation starts the source recurrence. Those startup
outputs are valid initialization values, not unavailable values to replace by NaN.
input_mode='close_difference' supports update(close) instead of close/open bars;
its first close yields NaN because no previous close exists. See description.md.
The user confirmed all 14 reference periods; only standard library is used.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class FMDemodulator:
    """Hard-limited bar change followed by the article's initialized smoother.

    period: integer >=1, default 30; SuperSmoother critical period in bars.
    input_mode: 'close_open' (default) or 'close_difference'.
    Limiter gain remains the source constant 10; clipping levels are +/-1.
    The whole streaming algorithm needs O(1) work and O(1) state per bar.
    """

    def __init__(self, period: int = 30, input_mode: str = 'close_open') -> None:
        if isinstance(period, bool) or not isinstance(period, int) or period < 1:
            raise ValueError('period must be an integer of at least 1')
        if input_mode not in ('close_open', 'close_difference'):
            raise ValueError('input_mode must be close_open or close_difference')
        # Full-precision substitution requested by the user. Radian cosine
        # argument sqrt(2)*pi/Period equals sqrt(2)*180/Period in degrees.
        root_two = math.sqrt(2.0)
        a1 = math.exp(-root_two * math.pi / period)
        b1 = 2.0 * a1 * math.cos(root_two * math.pi / period)
        c2 = b1
        c3 = -a1 * a1
        c1 = 1.0 - c2 - c3
        # Pole radius a1 is strictly inside the unit circle. Very large
        # integer periods can round it to 1 or destroy the resolvable gain.
        if not 0.0 < a1 < 1.0 or not math.isfinite(c1) or c1 <= 0.0:
            raise ValueError('period must yield numerically resolvable stable coefficients')
        self._period = period
        self._input_mode = input_mode
        self._c1, self._c2, self._c3 = c1, c2, c3
        self.reset()

    @property
    def period(self) -> int:
        """Read-only smoother critical period; not a price-window requirement."""
        return self._period

    @property
    def input_mode(self) -> str:
        """Read-only bar-difference input contract."""
        return self._input_mode

    @property
    def warmup_bars(self) -> int:
        """NaN-prefix length: zero for close/open, one for close-only mode."""
        return 1 if self._input_mode == 'close_difference' else 0

    @property
    def is_primed(self) -> bool:
        """Availability after the first derivative; independent of IIR settling."""
        return self._samples > 0

    @property
    def output(self) -> float:
        """Latest accepted output; read without consuming another observation."""
        return self._output

    def reset(self) -> None:
        """Restore empty price history, zero feedback, and source bar numbering."""
        self._bars = 0
        self._samples = 0           # Valid derivative bars; source CurrentBar.
        self._previous_close = None
        self._hl1 = 0.0             # Prior LIMITED derivative, not raw Deriv.
        self._ss1 = 0.0             # Prior SS, raw derivative during first two bars.
        self._ss2 = 0.0
        self._output = math.nan

    def update(self, close: float, open_value: float | None = None) -> float:
        """Consume one completed close/open bar, or one close in close-only mode.

        All candidate arithmetic precedes mutation. Invalid input/overflow
        therefore cannot advance either the price-bar or derivative-bar counter.
        """
        close = float(close)
        if not math.isfinite(close):
            raise ValueError('close must be finite')
        if self._input_mode == 'close_open':
            if open_value is None:
                raise ValueError('open_value is required in close_open mode')
            reference = float(open_value)
            if not math.isfinite(reference):
                raise ValueError('open_value must be finite')
        else:
            if open_value is not None:
                raise ValueError('omit open_value in close_difference mode')
            reference = self._previous_close
        if reference is None:
            # A missing first close-to-close difference is unavailable, not zero.
            # Do not advance smoother startup or limited-input feedback here.
            self._previous_close = close
            self._bars += 1
            self._output = math.nan
            return self._output
        derivative = close - reference
        if not math.isfinite(derivative):
            raise ValueError('bar-difference arithmetic must remain finite')
        limited = 10.0 * derivative
        if not math.isfinite(limited):
            raise ValueError('limiter multiplication must remain finite')
        if limited > 1.0:
            limited = 1.0
        if limited < -1.0:
            limited = -1.0
        current_bar = self._samples + 1  # One-based VALID derivative observation.
        if current_bar < 3:
            # Exact source override SS=Deriv. Retain it for feedback even when
            # it exceeds the limiter range; do not seed with limited or zero.
            ss = derivative
        else:
            # Source order: c1*(HL+HL[1])/2 + c2*SS[1] + c3*SS[2].
            ss = (self._c1 * (limited + self._hl1) / 2.0
                  + self._c2 * self._ss1 + self._c3 * self._ss2)
            if not math.isfinite(ss):
                raise ValueError('SuperSmoother arithmetic must remain finite')
        # Keep limited-input and output histories distinct and commit together.
        self._hl1 = limited
        self._ss2 = self._ss1
        self._ss1 = ss
        self._previous_close = close
        self._samples = current_bar
        self._bars += 1
        self._output = ss
        return ss


class ReferenceCase(NamedTuple):
    """One confirmed SuperSmoother period and portable test description."""
    period: int
    what_it_tests: str


# All 14 periods were confirmed by the user on 2026-10-19.
REFERENCE_CASES = (
    ReferenceCase(30, 'Article and Mesa default critical period with full-precision constants.'),
    ReferenceCase(1, 'Minimum supported research period; very fast stable smoother.'),
    ReferenceCase(2, 'Nyquist-scale research period and source raw-derivative startup.'),
    ReferenceCase(3, 'Short smoother with a cutoff below the Nyquist frequency.'),
    ReferenceCase(5, 'Fast five-bar critical period and hard-limiter transitions.'),
    ReferenceCase(8, 'Short-cycle smoother near the book aliasing discussion.'),
    ReferenceCase(10, 'Book-recommended ten-bar SuperSmoother critical period.'),
    ReferenceCase(14, 'Intermediate smoothing with the common fourteen-bar setting.'),
    ReferenceCase(20, 'Twenty-bar critical period associated with a monthly trading cycle.'),
    ReferenceCase(48, 'Slower critical period near the book cycle and trend boundary.'),
    ReferenceCase(60, 'Long smoothing with persistent source initialization transients.'),
    ReferenceCase(100, 'Very slow smoother and unbounded startup-seeded transient behavior.'),
    ReferenceCase(126, 'Half-record critical period without postponing output availability.'),
    ReferenceCase(252, 'Full-record critical period; initialized outputs still start immediately.'),
)

REFERENCE_INPUT_MODE = 'close_open'


def _case_suffix(case: ReferenceCase) -> str:
    """P=period; full-precision coefficient mode and gain 10 are fixed."""
    return f'P{case.period}'


def _parameter_comment(case: ReferenceCase) -> str:
    """State period and the common input contract before every array."""
    return f'period={case.period}, input_mode={REFERENCE_INPUT_MODE}, limiter_gain=10'


def _float_literal(value: float, nan_literal: str) -> str:
    """Use 15 significant export digits; never round streaming state."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError('expected output cannot contain infinity')
    literal = format(value, '.15g')
    if '.' not in literal and 'e' not in literal.lower():
        literal += '.0'  # Rust requires floating literals for Vec<f64>.
    return literal


def _array_lines(values: list[float], indent: str, nan_literal: str) -> str:
    """Six portable values per row make reference data easy to review."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return '\n'.join(indent + ', '.join(literals[index:index + 6]) + ','
                     for index in range(0, len(literals), 6))


def _load_literal_arrays(path: Path) -> dict[str, list[float]]:
    """Parse Python data lists without executing/importing the fixture file."""
    arrays = {}
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.List):
            continue
        values = []
        for element in node.value.elts:
            if (isinstance(element, ast.Attribute) and isinstance(element.value, ast.Name)
                    and element.value.id == 'math' and element.attr == 'nan'):
                values.append(math.nan)
            else:
                values.append(float(ast.literal_eval(element)))
        for target in node.targets:
            if isinstance(target, ast.Name):
                arrays[target.id] = values
    return arrays


def _write_generated_section(path: Path, section: str, comment: str) -> None:
    """Append expected data, or replace only its marked block on regeneration."""
    begin = f'{comment} BEGIN GENERATED FM DEMODULATOR EXPECTED DATA'
    end = f'{comment} END GENERATED FM DEMODULATOR EXPECTED DATA'
    original = path.read_text(encoding='utf-8')
    generated = begin + '\n\n' + section.rstrip() + '\n\n' + end + '\n'
    if begin in original or end in original:
        if original.count(begin) != 1 or original.count(end) != 1:
            raise ValueError(f'malformed generated markers in {path.name}')
        start, finish = original.index(begin), original.index(end)
        if finish < start:
            raise ValueError(f'reversed generated markers in {path.name}')
        result = original[:start] + generated.rstrip('\n') + original[finish + len(end):]
    else:
        result = original.rstrip() + '\n\n' + generated
    path.write_text(result, encoding='utf-8')


def generate_reference_data(input_close: list[float], input_open: list[float],
                            directory: Path) -> None:
    """Write confirmed cases to Python, verify actual data, then translate it.

    The five language fixtures use the same selected input contract. This
    file-rendering code is tooling, separate from the streaming class to port.
    """
    if len(input_close) != 252 or len(input_open) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError('expected 252 closes/opens and one through 64 parameter combinations')
    if len({_case_suffix(case) for case in REFERENCE_CASES}) != len(REFERENCE_CASES):
        raise ValueError('parameter suffixes must be unique')
    python_path = directory / 'test_testdata.py'
    original_inputs = {name: values for name, values in _load_literal_arrays(python_path).items()
                       if name.startswith('INPUT_')}
    if original_inputs.get('INPUT_CLOSE') != input_close or original_inputs.get('INPUT_OPEN') != input_open:
        raise ValueError('embedded input arrays differ from the copied fixture')
    raw_outputs = {}
    warmups = {}
    sections = []
    for case in REFERENCE_CASES:
        indicator = FMDemodulator(case.period, REFERENCE_INPUT_MODE)
        values = [indicator.update(close, opening if REFERENCE_INPUT_MODE == 'close_open' else None)
                  for close, opening in zip(input_close, input_open)]
        name = 'EXPECTED_' + _case_suffix(case)
        raw_outputs[name] = values
        warmups[name] = indicator.warmup_bars
        sections.append(f'# {case.what_it_tests}\n# {_parameter_comment(case)}\n{name} = [\n'
                        + _array_lines(values, '    ', 'math.nan') + '\n]')
    _write_generated_section(python_path, '\n\n'.join(sections), '#')

    # Reopen and VERIFY the actual written Python data before translating.
    written = _load_literal_arrays(python_path)
    if {name: written[name] for name in original_inputs} != original_inputs:
        raise ValueError('generation changed original input data')
    if {name for name in written if name.startswith('EXPECTED_')} != set(raw_outputs):
        raise ValueError('missing or unexpected expected array names')
    for name, raw in raw_outputs.items():
        values = written[name]
        if len(values) != 252:
            raise ValueError(f'{name} must contain 252 values')
        for index, (before, after) in enumerate(zip(raw, values)):
            if index < warmups[name]:
                if not math.isnan(before) or not math.isnan(after):
                    raise ValueError(f'{name} has incorrect availability')
            elif not math.isfinite(after) or after != float(_float_literal(before, 'nan')):
                raise ValueError(f'{name} failed 15-digit serialization verification')

    go_path = directory / 'testdata_test.go'
    go_text = go_path.read_text().replace('package xxxx', 'package fmdemodulator', 1)
    # FM close/open has no NaN prefix, but the requested math import remains
    # available for shared fixture checks. A blank reference avoids an unused
    # import compilation error when every expected value is finite.
    if 'import "math"' not in go_text:
        go_text = go_text.replace('package fmdemodulator\n',
                                  'package fmdemodulator\n\nimport "math"\n', 1)
    if 'var _ = math.NaN' not in go_text:
        go_text = go_text.replace('import "math"\n', 'import "math"\n\nvar _ = math.NaN\n', 1)
    go_path.write_text(go_text)
    zig_path = directory / 'testdata.zig'
    zig_text = zig_path.read_text()
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n' + zig_text
    if 'const nan = math.nan(f64);' not in zig_text:
        zig_text = zig_text.replace('const math = @import("std").math;\n',
                                   'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(zig_text)

    translated = {'go': [], 'ts': [], 'rs': [], 'zig': []}
    for case in REFERENCE_CASES:
        suffix = _case_suffix(case)
        values = written['EXPECTED_' + suffix]  # Export the serialized Python values.
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
        path = directory / filename
        # Keep expected Rust functions inside its existing testdata module.
        if language == 'rs' and 'BEGIN GENERATED FM DEMODULATOR EXPECTED DATA' not in path.read_text():
            rust_text = path.read_text()
            final_brace = rust_text.rfind('}')
            if final_brace < 0 or rust_text[final_brace + 1:].strip():
                raise ValueError('Rust fixture must end with the testdata module brace')
            path.write_text(rust_text[:final_brace])
            _write_generated_section(path, '\n\n'.join(translated[language]), '//')
            path.write_text(path.read_text() + '}\n')
        else:
            _write_generated_section(path, '\n\n'.join(translated[language]), '//')
    print(f'Verified {len(raw_outputs)} arrays of 252 values; wrote all five languages.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data', action='store_true',
                        help='regenerate the confirmed reference periods in five languages')
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

    INPUT_OPEN = [
        92.500000, 91.500000, 95.155000, 93.970000, 95.500000, 94.500000, 95.000000, 91.500000, 91.815000, 91.125000,
        93.875000, 97.500000, 98.815000, 92.000000, 91.125000, 91.875000, 93.405000, 89.750000, 89.345000, 92.250000,
        89.780000, 87.940000, 87.595000, 85.220000, 83.500000, 83.500000, 81.250000, 85.125000, 88.125000, 87.500000,
        85.250000, 86.000000, 87.190000, 86.125000, 89.000000, 88.625000, 86.000000, 85.500000, 84.750000, 85.250000,
        84.250000, 86.750000, 86.940000, 89.315000, 89.940000, 90.815000, 91.190000, 91.345000, 89.595000, 91.000000,
        89.750000, 88.750000, 88.315000, 84.345000, 83.500000, 84.000000, 86.000000, 85.530000, 87.500000, 88.500000,
        90.000000, 88.655000, 89.500000, 91.565000, 92.000000, 93.000000, 92.815000, 91.750000, 92.000000, 91.375000,
        89.750000, 88.750000, 85.440000, 83.500000, 84.875000, 98.625000, 96.690000, 102.375000, 106.000000, 104.625000,
        102.500000, 104.250000, 104.000000, 106.125000, 106.065000, 105.940000, 105.625000, 108.625000, 110.250000, 110.565000,
        117.000000, 120.750000, 118.000000, 119.125000, 119.125000, 117.815000, 116.375000, 115.155000, 111.250000, 111.500000,
        116.690000, 116.000000, 113.620000, 111.750000, 114.560000, 113.620000, 118.120000, 119.870000, 116.620000, 115.870000,
        115.060000, 115.870000, 117.500000, 119.870000, 119.250000, 120.190000, 122.870000, 123.870000, 122.250000, 123.120000,
        123.310000, 124.000000, 123.000000, 124.810000, 130.000000, 130.880000, 132.500000, 131.000000, 132.500000, 134.000000,
        137.440000, 135.750000, 138.310000, 138.000000, 136.380000, 136.500000, 132.000000, 127.500000, 127.620000, 124.000000,
        123.620000, 125.000000, 126.370000, 126.250000, 125.940000, 124.000000, 122.750000, 120.000000, 120.000000, 122.000000,
        123.620000, 121.500000, 120.120000, 123.750000, 122.750000, 125.000000, 128.500000, 128.380000, 123.870000, 124.370000,
        122.750000, 123.370000, 122.000000, 122.620000, 125.000000, 124.250000, 124.370000, 125.620000, 126.500000, 128.380000,
        128.880000, 131.500000, 132.500000, 137.500000, 134.630000, 132.000000, 134.000000, 132.000000, 131.380000, 126.500000,
        128.750000, 127.190000, 127.500000, 120.500000, 126.620000, 123.000000, 122.060000, 121.000000, 121.000000, 118.000000,
        122.000000, 122.250000, 119.120000, 115.000000, 113.500000, 114.000000, 110.810000, 106.500000, 106.440000, 108.000000,
        107.000000, 108.620000, 93.000000, 93.750000, 94.250000, 94.870000, 95.500000, 94.500000, 97.000000, 98.500000,
        96.750000, 95.870000, 94.440000, 92.750000, 90.500000, 95.060000, 94.620000, 97.500000, 96.000000, 96.000000,
        94.620000, 94.870000, 94.000000, 99.000000, 105.500000, 108.810000, 105.000000, 105.940000, 104.940000, 103.690000,
        102.560000, 103.440000, 109.810000, 113.000000, 117.000000, 116.250000, 120.500000, 111.620000, 108.120000, 110.190000,
        107.750000, 108.000000, 110.690000, 109.060000, 108.500000, 109.870000, 109.120000, 109.690000, 109.560000, 110.440000,
        109.690000, 109.190000,
    ]

    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, INPUT_OPEN, Path(__file__).resolve().parent)
    else:
        demodulator = FMDemodulator(input_mode=REFERENCE_INPUT_MODE)
        outputs = [demodulator.update(close, opening if REFERENCE_INPUT_MODE == 'close_open' else None)
                   for close, opening in zip(INPUT_CLOSE, INPUT_OPEN)]
        print(f'FM Demodulator: period=30, full-precision constants, input_mode={REFERENCE_INPUT_MODE}')
        print(f'{len(outputs)} outputs; NaN prefix={demodulator.warmup_bars}')
        print(f'First two source initialization values: {outputs[demodulator.warmup_bars]:.15g}, {outputs[demodulator.warmup_bars + 1]:.15g}')
        print(f'Final FM: {outputs[-1]:.15g}')
        demodulator.reset()
        print('Primed after reset:', demodulator.is_primed)
        print(f'Confirmed reference combinations: {len(REFERENCE_CASES)}')
