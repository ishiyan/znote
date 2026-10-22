"""Streaming research prototype master: hurst-coefficient.

Numerical authority is the indicator's own Cycle Analytics for Traders listing.
Standard library only. See description.md for complete math and source quirks.
Copy this whole folder to convert it: no sibling numerical masters are imported.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple

TWO_PI = 2.0 * math.pi
SQRT_TWO = math.sqrt(2.0)


def _real(value, name, minimum):
    # bool is a subclass of int in Python; reject it deliberately for ports.
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a finite real >= {minimum}')
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f'{name} must be a finite real >= {minimum}') from error
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f'{name} must be a finite real >= {minimum}')
    return value


def _sample(value):
    # Missing NaN observations do not age any filter or lookback. Infinity
    # is invalid. Coefficients and states are never fed either kind of value.
    if isinstance(value, bool):
        raise ValueError('close must be a real number')
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError('close must be finite or NaN') from error
    if math.isinf(value):
        raise ValueError('close must be finite or NaN')
    return value


def _finite(*values):
    # All downstream calculations finish before state mutation. A rejected
    # overflow must leave the indicator ready for the next ordinary sample.
    if not all(math.isfinite(value) for value in values):
        raise ValueError('indicator arithmetic overflowed')


class _Stream:
    """Common scalar stream protocol; no numerical dependencies or batch data.

    warmup_bars counts public leading NaNs, not settling time. Algorithms
    execute from accepted bar one using explicit zero prehistory.
    """
    @property
    def parameters(self):
        return self._parameters

    @property
    def samples_seen(self):
        return self._count

    @property
    def is_primed(self):
        return self._count > self.warmup_bars

    @property
    def output(self):
        return self._output

class Parameters(NamedTuple):
    length: int
    smoothing_period: float


class HurstState(NamedTuple):
    n1: float
    n2: float
    n3: float
    dimension: float
    hurst: float
    value: float
    dimension_updated: bool


class HurstCoefficient(_Stream):
    """Chapter 6 listing 6-1: half-window range dimension, then SuperSmoother.

    This finite-window estimator is not an R/S Hurst fit or FRAMA. length
    must be even and >=2; smoothing_period generalizes the printed fixed 20.
    The source's dimension seed is ZERO; neither Hurst nor output is clipped.
    """
    def __init__(self, length=30, smoothing_period=20.0):
        if isinstance(length, bool) or not isinstance(length, int) or length < 2 or length%2:
            raise ValueError('length must be an even integer >=2')
        smoothing = _real(smoothing_period, 'smoothing_period', 2.0)
        self._parameters = Parameters(length, smoothing)
        self._half = length//2
        a = math.exp(-SQRT_TWO*math.pi/smoothing)
        self._c2 = 2.0*a*math.cos(SQRT_TWO*math.pi/smoothing)
        self._c3 = -a*a
        self._c1 = 1.0-self._c2-self._c3
        if not (0.0 < a < 1.0 and self._c1 > 0.0):
            raise ValueError('smoothing period must yield resolvable stable coefficients')
        self.reset()

    @property
    def warmup_bars(self):
        # At length+1 both current AND previous raw Hurst have full windows.
        # Earlier feedback is computed, but public NaNs do not feed it.
        return self.parameters.length

    @property
    def state(self):
        return HurstState(self._n1,self._n2,self._n3,self._dimension,
                          self._hurst,self._y1,self._dimension_updated)

    def reset(self):
        self._history = [0.0]*self.parameters.length
        self._n1 = self._n2 = self._n3 = self._dimension = 0.0
        self._hurst = self._y1 = self._y2 = 0.0
        self._dimension_updated = False
        self._count = 0
        self._output = math.nan

    def update(self, close, time=None):
        price = _sample(close)
        if math.isnan(price):
            return math.nan
        history = [price] + self._history[:-1]  # Newest first, bounded storage.
        half = self._half
        # Independent half windows: [0,half) and [half,length). No overlap,
        # interpolation or typical-price substitution. N3 uses all closes.
        n3 = (max(history)-min(history))/self.parameters.length
        recent_high = recent_low = history[0]
        for index in range(half):
            if history[index] > recent_high:
                recent_high = history[index]
            if history[index] < recent_low:
                recent_low = history[index]
        n1 = (recent_high-recent_low)/half
        older_high = older_low = history[half]
        for index in range(half,self.parameters.length):
            if history[index] > older_high:
                older_high = history[index]
            if history[index] < older_low:
                older_low = history[index]
        n2 = (older_high-older_low)/half
        dimension = self._dimension
        updated = n1 > 0.0 and n2 > 0.0 and n3 > 0.0
        if updated:
            # Listing uses two natural logs and a fixed .5 blend with the
            # preceding dimension. Do not use log(n1+n2)/n3, clip to [1,2],
            # initialize dimension to 1.5, or change this blend with LP.
            dimension = .5*((math.log(n1+n2)-math.log(n3))/math.log(2.0)
                            + self._dimension)
        hurst = 2.0-dimension
        value = (self._c1*(hurst+self._hurst)/2.0
                 + self._c2*self._y1 + self._c3*self._y2)
        _finite(n1, n2, n3, dimension, hurst, value)
        self._history = history
        self._n1, self._n2, self._n3 = n1, n2, n3
        self._dimension, self._hurst = dimension, hurst
        self._dimension_updated = updated
        self._y2, self._y1 = self._y1, value
        self._count += 1
        self._output = value if self.is_primed else math.nan
        return self._output

# Fixture tooling below is not part of the streaming calculation.
INDICATOR_SLUG = 'hurst-coefficient'
MASTER_CLASS = HurstCoefficient
REFERENCE_INPUT = 'close'
PARAMETER_SHORTCUTS = {'cutoff': 'C', 'highpass_period1': 'HP1', 'highpass_period2': 'HP2', 'period': 'P', 'bandwidth': 'B', 'length': 'L', 'smoothing_period': 'LP'}
REFERENCE_CASES = (
    {'length': 30, 'smoothing_period': 20.0, 'what_it_tests': 'Published range length and SuperSmoother defaults.'},
    {'length': 20, 'smoothing_period': 20.0, 'what_it_tests': 'Shorter range length used in the chapter cycle example.'},
    {'length': 200, 'smoothing_period': 20.0, 'what_it_tests': 'Long range length used in the chapter trend example.'},
    {'length': 2, 'smoothing_period': 20.0, 'what_it_tests': 'Single-sample half windows: dimension guard always holds its zero seed.'},
    {'length': 4, 'smoothing_period': 20.0, 'what_it_tests': 'Shortest nondegenerate pair of half-window ranges.'},
    {'length': 10, 'smoothing_period': 20.0, 'what_it_tests': 'Fast finite-window structure estimate.'},
    {'length': 60, 'smoothing_period': 20.0, 'what_it_tests': 'Medium-long range measurement.'},
    {'length': 100, 'smoothing_period': 20.0, 'what_it_tests': 'Long range measurement.'},
    {'length': 250, 'smoothing_period': 20.0, 'what_it_tests': 'Current and previous full windows become available at bar 251.'},
    {'length': 252, 'smoothing_period': 20.0, 'what_it_tests': '253-observation history requirement: all 252 public rows remain NaN.'},
    {'length': 30, 'smoothing_period': 10.0, 'what_it_tests': 'Faster final SuperSmoother; dimension averaging stays fixed at one half.'},
    {'length': 30, 'smoothing_period': 20.5, 'what_it_tests': 'Fractional final smoothing coefficient period.'},
)
# All 48 cases confirmed by the user on 2026-10-22.
REFERENCE_CASES_CONFIRMED = True


def _parameter_token(value):
    if isinstance(value, bool):
        return '1' if value else '0'
    return format(value, '.15g').replace('.', '_').replace('-', 'm')


def _case_suffix(case):
    return '_'.join(PARAMETER_SHORTCUTS[name]+_parameter_token(value)
                    for name, value in case.items() if name != 'what_it_tests')


def _parameter_comment(case):
    return ', '.join(f'{key}={value}' for key, value in case.items()
                     if key != 'what_it_tests') + '; input=' + REFERENCE_INPUT


def _float_literal(value, nan):
    if math.isnan(value):
        return nan
    if not math.isfinite(value):
        raise ValueError('cannot serialize infinite reference output')
    literal = format(value, '.15g')  # 15 significant digits, only at export.
    if '.' not in literal and 'e' not in literal:
        literal += '.0'
    return literal


def _array_body(values, indent, nan):
    # These masters have scalar components. Keep six literals per line in
    # every language; NaN spelling is the only change to the numeric tokens.
    tokens = [_float_literal(v, nan) for v in values]
    return '\n'.join(indent+', '.join(tokens[i:i+6])+','
                      for i in range(0, len(tokens), 6))

def _load_arrays(path):
    def decode(node):
        if isinstance(node, ast.List):
            return [decode(child) for child in node.elts]
        if isinstance(node, ast.Name) and node.id == 'NaN':
            return math.nan
        return float(ast.literal_eval(node))
    arrays = {}
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    arrays[target.id] = decode(node.value)
    return arrays


def _write_section(path, content, comment):
    # Rerunning replaces this marked generated section, never the input arrays.
    begin = f'{comment} BEGIN GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA'
    end = f'{comment} END GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA'
    original = path.read_text(encoding='utf-8')
    block = begin+'\n\n'+content.rstrip()+'\n\n'+end
    if begin in original:
        start = original.index(begin)
        finish = original.index(end, start)+len(end)
        result = original[:start]+block+original[finish:]
    else:
        result = original.rstrip()+'\n\n'+block+'\n'
    path.write_text(result, encoding='utf-8')


def _run_reference(case,inputs):
    indicator = MASTER_CLASS(**{k:v for k,v in case.items() if k != 'what_it_tests'})
    outputs = [indicator.update(close) for close in inputs['INPUT_CLOSE']]
    if isinstance(outputs[0], float):
        return {'VALUE': outputs}
    return {field.upper(): [getattr(out, field) for out in outputs]
            for field in outputs[0]._fields}


def generate_reference_data(directory, embedded_inputs=None):
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError('reference combinations await user confirmation')
    if not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError('expected at most 64 combinations')
    python_path = directory/'test_testdata.py'
    inputs = _load_arrays(python_path)
    if len(inputs['INPUT_CLOSE']) != 252:
        raise ValueError('expected 252 closes')
    for name, values in (embedded_inputs or {}).items():
        if inputs[name] != values:
            raise ValueError(f'embedded {name} differs from copied fixture')
    arrays = {}
    sections = ['# NaN marks unavailable public output only.\nNaN = math.nan']
    for case in REFERENCE_CASES:
        for component, values in _run_reference(case, inputs).items():
            name = 'EXPECTED_'+_case_suffix(case)+'_'+component
            if name in arrays:
                raise ValueError('duplicate expected name')
            arrays[name] = (case, values)
            sections.append(f"# {case['what_it_tests']}\n# {_parameter_comment(case)}\n"
                            +f'{name} = [\n'+_array_body(values, '    ', 'NaN')+'\n]')
    _write_section(python_path, '\n\n'.join(sections), '#')
    # Reopen Python literals and verify dimensions, values, and every NaN.
    # All other languages translate this authoritative rounded Python data.
    written = _load_arrays(python_path)
    if {n for n in written if n.startswith('EXPECTED_')} != set(arrays):
        raise ValueError('missing or unexpected Python reference arrays')
    for name, (case, raw) in arrays.items():
        actual = written[name]
        if len(actual) != 252:
            raise ValueError(f'incorrect dimensions: {name}')
        for source, literal in zip(raw, actual):
            if math.isnan(source):
                if not math.isnan(literal):
                    raise ValueError(f'incorrect NaN mask: {name}')
            elif literal != float(_float_literal(source, 'NaN')):
                raise ValueError(f'incorrect 15-digit value: {name}')
    translated = {language: [] for language in ('go', 'ts', 'rs', 'zig')}
    for name, (case, raw) in arrays.items():
        suffix = name.removeprefix('EXPECTED_')
        values = written[name]
        comments = f"// {case['what_it_tests']}\n// {_parameter_comment(case)}\n"
        translated['go'].append(comments+f'var expected{suffix} = []float64{{\n'
                                +_array_body(values, '\t', 'math.NaN()')+'\n}')
        translated['ts'].append(comments+f'export const expected{suffix}: number[] = [\n'
                                +_array_body(values, '    ', 'NaN')+'\n];')
        translated['rs'].append(comments+f'pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n'
                                +_array_body(values, '        ', 'f64::NAN')+'\n    ]\n}')
        translated['zig'].append(comments+f'pub fn expected{suffix}() [252]f64 {{\n    return .{{\n'
                                 +_array_body(values, '        ', 'nan')+'\n    };\n}')
    # Add imports only when expected NaNs are actually generated, so copied
    # Go input-only fixtures compile before parameter approval as well.
    go_path = directory/'testdata_test.go'
    text = go_path.read_text(encoding='utf-8')
    package = INDICATOR_SLUG.replace('-', '').replace('_', '')
    if 'import "math"' not in text:
        text = text.replace(f'package {package}\n', f'package {package}\n\nimport "math"\n', 1)
        go_path.write_text(text, encoding='utf-8')
    for language, filename in [('go', 'testdata_test.go'), ('ts', 'testdata.ts'),
                               ('rs', 'testdata.rs'), ('zig', 'testdata.zig')]:
        _write_section(directory/filename, '\n\n'.join(translated[language]), '//')
    print(f'Verified {len(arrays)} expected arrays for {len(REFERENCE_CASES)} cases in Python; translated all five languages.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data', action='store_true')
    args = parser.parse_args()
    # Embed the exact original 252 closes: demonstration and fixture input
    # cross-check do not depend on an imported numerical/input package.
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
    if args.generate_reference_data:
        generate_reference_data(Path(__file__).resolve().parent, {'INPUT_CLOSE': INPUT_CLOSE})
    else:
        indicator = MASTER_CLASS()
        results = [indicator.update(close) for close in INPUT_CLOSE]
        print(f'{INDICATOR_SLUG}: {len(results)} closes; warmup={indicator.warmup_bars}')
        print('Last output:', results[-1])
        print(f'Reference cases={len(REFERENCE_CASES)}; confirmed={REFERENCE_CASES_CONFIRMED}')
