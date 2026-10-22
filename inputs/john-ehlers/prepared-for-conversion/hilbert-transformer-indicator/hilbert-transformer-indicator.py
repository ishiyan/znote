"""Streaming research master of Chapter 14 listings 14-2 and 14-3.

Standard library only; see description.md for full standalone mathematics.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# These are mathematical constants. Source .707 means 1/sqrt(2), and 1.414
# means sqrt(2); preserve the design decimals .991 and .5 as printed.
TWO_PI = 2.0 * math.pi
SQRT_TWO = math.sqrt(2.0)


def _integer(value, name, minimum):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return value


def _real(value, name, minimum):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a finite real >= {minimum}')
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError('value must be representable as a real number') from error
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f'{name} must be a finite real >= {minimum}')
    return value


def _sample(value):
    # A missing sample is skipped. Infinity is invalid. Neither contaminates
    # the feedback or ages the accepted-bar counter.
    if isinstance(value, bool):
        raise ValueError('price must be a real number')
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError('value must be representable as a real number') from error
    if math.isinf(value):
        raise ValueError('price must be finite or NaN (missing)')
    return value


class _Roof:
    """Two-pole high-pass then two-pole SuperSmoother (book equation 3-3).

    State begins at zero, including the TWO absent raw closes. This is an
    explicit finite-record reference convention, shared with the existing
    periodogram master. A positive constant close creates a startup transient.
    candidate/commit separates arithmetic from mutation: an overflow rejected
    by a downstream stage cannot leave the roof one observation ahead.
    """
    def __init__(self, highpass_period, smoothing_period):
        hp = _real(highpass_period, 'highpass_period', 5.0)
        lp = _real(smoothing_period, 'smoothing_period', 2.0)
        angle = TWO_PI / (SQRT_TWO * hp)
        cosine = math.cos(angle)
        alpha = (cosine + math.sin(angle) - 1.0) / cosine
        pole = 1.0 - alpha
        a = math.exp(-SQRT_TWO * math.pi / lp)
        self.hp0 = (1.0 - alpha / 2.0) * (1.0 - alpha / 2.0)
        self.hp1 = 2.0 * pole
        self.hp2 = pole * pole  # recurrence SUBTRACTS this positive coefficient
        self.ss2 = 2.0 * a * math.cos(SQRT_TWO * math.pi / lp)
        self.ss3 = -a * a     # recurrence ADDS this negative coefficient
        self.ss1 = 1.0 - self.ss2 - self.ss3
        if not (0.0 < pole < 1.0 and 0.0 < a < 1.0 and self.ss1 > 0.0):
            raise ValueError('periods must produce finite resolvable stable coefficients')
        self.reset()

    def reset(self):
        self.x1 = self.x2 = self.h1 = self.h2 = self.f1 = self.f2 = 0.0

    def candidate(self, price):
        # All states in this expression are PREVIOUS accepted observations.
        high = (self.hp0 * (price - 2.0*self.x1 + self.x2)
                + self.hp1*self.h1 - self.hp2*self.h2)
        filtered = (self.ss1*(high+self.h1)/2.0
                    + self.ss2*self.f1 + self.ss3*self.f2)
        if not (math.isfinite(high) and math.isfinite(filtered)):
            raise ValueError('roofing arithmetic overflowed')
        return high, filtered

    def commit(self, price, high, filtered):
        self.x2, self.x1 = self.x1, price
        self.h2, self.h1 = self.h1, high
        self.f2, self.f1 = self.f1, filtered

PEAK_DECAY = 0.991  # Published AGC design constant, not a rounded radical.


class Parameters(NamedTuple):
    highpass_period: float
    smoothing_period: float
    quadrature_period: float
    smooth_imaginary: bool


class HilbertOutput(NamedTuple):
    """Normalized real component and optionally smoothed imaginary component."""
    real: float
    imaginary: float


class HilbertState(NamedTuple):
    """Immutable finite diagnostics; startup NaNs are never recursive state."""
    high_pass: float
    filtered: float
    in_phase_peak: float
    real: float
    raw_difference: float
    quadrature_peak: float
    normalized_quadrature: float
    imaginary: float


class HilbertTransformerIndicator:
    """Chapter 14 listing 14-3 (default) or unsmoothed listing 14-2.

    This is the book's normalized difference approximation to quadrature,
    not an ideal all-pass Hilbert FIR or the older seven-tap cycle estimator.
    Only smoothing_period is a printed input. HP and quadrature periods and
    disabling final smoothing are explicit, named research controls.
    """
    def __init__(self,highpass_period=48.0,smoothing_period=20.0,
                 quadrature_period=10.0,smooth_imaginary=True):
        hp = _real(highpass_period,'highpass_period',5.0)
        lp = _real(smoothing_period,'smoothing_period',2.0)
        qp = _real(quadrature_period,'quadrature_period',2.0)
        if not isinstance(smooth_imaginary,bool):
            raise ValueError('smooth_imaginary must be a boolean')
        self._parameters = Parameters(hp,lp,qp,smooth_imaginary)
        self._roof = _Roof(hp,lp)
        # A second independent SuperSmoother is applied AFTER normalization.
        # The source overwrites c1/c2/c3 here; do not accidentally replace the
        # roofing coefficients or feed the previous RAW difference into it.
        a = math.exp(-SQRT_TWO*math.pi/qp)
        self._q2 = 2.0*a*math.cos(SQRT_TWO*math.pi/qp)
        self._q3 = -a*a
        self._q1 = 1.0-self._q2-self._q3
        if not (0.0<a<1.0 and self._q1>0.0):
            raise ValueError('quadrature_period must produce resolvable stable coefficients')
        self.reset()

    @property
    def parameters(self):
        return self._parameters

    @property
    def warmup_bars(self):
        # Explicit lag dependencies: roof x[t-2], derivative Real[t-1], then
        # final smoother Quadrature[t-1]. Four or five real closes suffice to
        # populate those raw-input dependencies. This is NOT IIR settling.
        return 4 if self.parameters.smooth_imaginary else 3

    @property
    def samples_seen(self):
        return self._count

    @property
    def is_primed(self):
        return self._count>self.warmup_bars

    @property
    def state(self):
        return HilbertState(self._roof.h1,self._roof.f1,self._ipeak,self._real,
                            self._difference,self._qpeak,self._quadrature,self._imag1)

    @property
    def output(self):
        return self._output

    def reset(self):
        self._roof.reset()
        self._count = 0
        self._ipeak = self._real = self._difference = self._qpeak = 0.0
        self._quadrature = self._imag1 = self._imag2 = 0.0
        self._output = HilbertOutput(math.nan,math.nan)

    def update(self,close,time=None):
        # Optional time is accepted but has no numerical or storage role.
        price = _sample(close)
        if math.isnan(price):
            return HilbertOutput(math.nan,math.nan)
        high,filtered = self._roof.candidate(price)
        ipeak = PEAK_DECAY*self._ipeak
        if abs(filtered)>ipeak:
            ipeak = abs(filtered)  # Instant attack, exponential release.
        # Printed division is undefined at zero peak. Define a retained finite
        # normalized value (zero at reset) for an all-zero/underflowed record.
        real = filtered/ipeak if ipeak!=0.0 else self._real
        difference = real-self._real
        qpeak = PEAK_DECAY*self._qpeak
        if abs(difference)>qpeak:
            qpeak = abs(difference)
        quadrature = difference/qpeak if qpeak!=0.0 else self._quadrature
        if self.parameters.smooth_imaginary:
            imaginary = (self._q1*(quadrature+self._quadrature)/2.0
                         + self._q2*self._imag1+self._q3*self._imag2)
        else:
            imaginary = quadrature  # Listing 14-2, no additional smoothing.
        if not all(math.isfinite(v) for v in
                   (ipeak,real,difference,qpeak,quadrature,imaginary)):
            raise ValueError('Hilbert transformer arithmetic overflowed')
        # Commit every stage together only after all arithmetic succeeds.
        self._roof.commit(price,high,filtered)
        self._ipeak,self._real,self._difference = ipeak,real,difference
        self._qpeak,self._quadrature = qpeak,quadrature
        self._imag2,self._imag1 = self._imag1,imaginary
        self._count += 1
        self._output = (HilbertOutput(real,imaginary) if self.is_primed
                        else HilbertOutput(math.nan,math.nan))
        return self._output


# Fixture tooling below is not part of the streaming calculation.
INDICATOR_SLUG = 'hilbert-transformer-indicator'
MASTER_CLASS = HilbertTransformerIndicator
REFERENCE_INPUT = 'close'
PARAMETER_SHORTCUTS = {'min_period': 'P0', 'max_period': 'P1', 'averaging_length': 'A', 'highpass_period': 'HP', 'smoothing_period': 'LP', 'quadrature_period': 'QP', 'smooth_imaginary': 'SI'}
REFERENCE_CASES = (
    {'highpass_period': 48.0, 'smoothing_period': 20.0, 'quadrature_period': 10.0, 'smooth_imaginary': True, 'what_it_tests': 'Published listing 14-3 defaults; normalized quadrature is smoothed separately.'},
    {'highpass_period': 48.0, 'smoothing_period': 20.0, 'quadrature_period': 10.0, 'smooth_imaginary': False, 'what_it_tests': 'Listing 14-2 raw normalized quadrature; no final smoothing.'},
    {'highpass_period': 48.0, 'smoothing_period': 10.0, 'quadrature_period': 10.0, 'smooth_imaginary': True, 'what_it_tests': 'Faster input smoothing with the published output smoother.'},
    {'highpass_period': 48.0, 'smoothing_period': 40.0, 'quadrature_period': 10.0, 'smooth_imaginary': True, 'what_it_tests': 'Slower input smoothing with independent quadrature smoothing.'},
    {'highpass_period': 48.0, 'smoothing_period': 20.5, 'quadrature_period': 10.0, 'smooth_imaginary': True, 'what_it_tests': 'Fractional input SuperSmoother period.'},
    {'highpass_period': 48.0, 'smoothing_period': 20.0, 'quadrature_period': 10.5, 'smooth_imaginary': True, 'what_it_tests': 'Fractional quadrature SuperSmoother period.'},
    {'highpass_period': 48.0, 'smoothing_period': 20.0, 'quadrature_period': 2.0, 'smooth_imaginary': True, 'what_it_tests': 'Minimum supported quadrature smoothing period.'},
    {'highpass_period': 48.0, 'smoothing_period': 20.0, 'quadrature_period': 20.0, 'smooth_imaginary': True, 'what_it_tests': 'Slower quadrature smoothing and added phase delay.'},
    {'highpass_period': 24.0, 'smoothing_period': 6.0, 'quadrature_period': 6.0, 'smooth_imaginary': True, 'what_it_tests': 'Explicit research variant with shorter roofing and output smoothing.'},
    {'highpass_period': 80.0, 'smoothing_period': 20.0, 'quadrature_period': 10.0, 'smooth_imaginary': True, 'what_it_tests': 'Explicit research variant with longer high-pass cutoff.'},
    {'highpass_period': 48.0, 'smoothing_period': 2.0, 'quadrature_period': 10.0, 'smooth_imaginary': False, 'what_it_tests': 'Minimum input smoothing period and raw quadrature.'},
    {'highpass_period': 48.0, 'smoothing_period': 252.0, 'quadrature_period': 10.0, 'smooth_imaginary': True, 'what_it_tests': 'Input cutoff equals record length; IIR cutoff is not a history window.'},
)
# All 36 Chapter 14–15 cases confirmed on 2026-10-22.
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
    return {field.upper():[getattr(out,field) for out in outputs]
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
    parser.add_argument('--generate-reference-data',action='store_true')
    args = parser.parse_args()
    # Exact shared 252 closing prices embedded for an independent demo.
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
        generate_reference_data(Path(__file__).resolve().parent,{'INPUT_CLOSE':INPUT_CLOSE})
    else:
        indicator = MASTER_CLASS()
        outputs = [indicator.update(close) for close in INPUT_CLOSE]
        print(f'{INDICATOR_SLUG}: {len(outputs)} closes; warmup={indicator.warmup_bars}')
        print('Last output:',outputs[-1])
        print(f'Reference cases={len(REFERENCE_CASES)}; confirmed={REFERENCE_CASES_CONFIRMED}')
