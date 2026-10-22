"""Streaming research prototype master: discrete-fourier-transform-spectrum, Ehlers 2013.

Standard library only; numerical helpers above fixture tooling are what to port.
See description.md for source reconstruction, equations, warmup and limitations.
__main__ embeds the shared 252 closes. Expected fixture generation is gated on
confirmation of the parameter proposal, separately from this working demo.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import math
from pathlib import Path
from typing import NamedTuple


# These are mathematical constants. Source .707 means 1/sqrt(2), and 1.414
# means sqrt(2); preserve the design decimals .995 and .5 as printed.
TWO_PI = 2.0 * math.pi
SQRT_TWO = math.sqrt(2.0)


class Heatmap(NamedTuple):
    """One owned vertical column, with the same fields as zpano's Heatmap.

    values[i] is the value at parameter_first+i*parameter_resolution.
    time is metadata only. An unavailable column has [] values and NaN extrema.
    Returning a new list prevents a subsequent update from changing an old plot.
    """
    time: datetime.datetime | None
    parameter_first: float
    parameter_last: float
    parameter_resolution: float
    value_min: float
    value_max: float
    values: list[float]

    def is_empty(self) -> bool:
        return len(self.values) == 0

    @staticmethod
    def empty(time, first, last):
        return Heatmap(time, float(first), float(last), 1.0, math.nan, math.nan, [])


def _column(time, first, last, values):
    # Actual column extrema, NOT constant palette endpoints. Renderer may use
    # fixed [0,1] palette limits regardless of the observed min/max.
    return Heatmap(time, float(first), float(last), 1.0,
                   min(values), max(values), list(values))


def _integer(value, name, minimum):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return value


def _real(value, name, minimum):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a finite real >= {minimum}')
    value = float(value)
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f'{name} must be a finite real >= {minimum}')
    return value


def _boolean(value, name):
    if not isinstance(value, bool):
        raise ValueError(f'{name} must be a boolean')
    return value


def _sample(value):
    # A missing sample is skipped. Infinity is invalid. Neither contaminates
    # the feedback or ages the accepted-bar counter.
    if isinstance(value, bool):
        raise ValueError('price must be a real number')
    value = float(value)
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

AGC_DECAY = 0.995  # Source design setting, not sqrt(.991) recomputed.
CENTROID_THRESHOLD = 0.5


class SpectrumOutput(NamedTuple):
    """Spectrum heatmap and dominant period, available independently.

    dominant_cycle is NaN until a primed result has a nonempty selected
    centroid (possibly retained from an earlier internal calculation).
    """
    heatmap: Heatmap
    dominant_cycle: float


class SpectrumState(NamedTuple):
    high_pass: float
    filtered: float
    raw_power: tuple[float, ...]
    normalization_maximum: float
    internal_dominant_cycle: float


def _normalize_and_centroid(periods, raw, previous_max, previous_dc, has_dc,
                            enhance):
    # Fast attack, slow decay is on POWER. Do not subtract the minimum. This
    # normalization differs from zpano's default floating intensity scaling.
    maximum = AGC_DECAY * previous_max
    for power in raw:
        if not math.isfinite(power) or power < 0.0:
            raise ValueError('spectral power arithmetic overflowed')
        if power > maximum:
            maximum = power
    normalized = [power/maximum if maximum > 0.0 else 0.0 for power in raw]
    sp = spx = 0.0
    for period, power in zip(periods, normalized):
        if power >= CENTROID_THRESHOLD:
            spx = spx + period*power
            sp = sp + power
    dominant = previous_dc
    if sp != 0.0:
        dominant = spx/sp
        has_dc = True
    if not math.isfinite(dominant):
        raise ValueError('centroid arithmetic overflowed')
    # Optional source display block is AFTER centroid extraction. Preserve
    # the raw and normalized powers; cube only the outgoing color intensity.
    values = [v*v*v for v in normalized] if enhance else normalized
    return maximum, dominant, has_dc, values

class Parameters(NamedTuple):
    min_period: int
    max_period: int
    window_length: int
    highpass_period: float
    smoothing_period: float
    spectral_dilation_compensation: bool
    enhance_resolution: bool


class DiscreteFourierTransformSpectrum:
    """Book listing 9-1: roofed window -> Fourier sums -> power -> AGC -> CG.

    Defaults: periods 10..48, window 48, HP 48, SS 10, compensation on,
    optional cubic display off. Integer period bins may include one bin.
    window_length>=2 is independent from max_period. HP>=5, SS>=2.
    No mean subtraction, FFT, numpy, floating min normalization or period
    smoothing is introduced. Each update returns SpectrumOutput.
    """
    def __init__(self, min_period=10, max_period=48, window_length=48,
                 highpass_period=48.0, smoothing_period=10.0,
                 spectral_dilation_compensation=True, enhance_resolution=False):
        first = _integer(min_period, 'min_period', 3)
        last = _integer(max_period, 'max_period', first)
        length = _integer(window_length, 'window_length', 2)
        hp = _real(highpass_period, 'highpass_period', 5.0)
        lp = _real(smoothing_period, 'smoothing_period', 2.0)
        comp = _boolean(spectral_dilation_compensation, 'spectral_dilation_compensation')
        enhance = _boolean(enhance_resolution, 'enhance_resolution')
        self._parameters = Parameters(first, last, length, hp, lp, comp, enhance)
        self._roof = _Roof(hp, lp)
        self._periods = tuple(range(first, last+1))
        # Precompute ordinary sin/cos tables; ports can compute in each update
        # instead, provided they use the identical angle and sum order.
        self._cosines = [tuple(math.cos(TWO_PI*n/period) for n in range(length))
                         for period in self._periods]
        self._sines = [tuple(math.sin(TWO_PI*n/period) for n in range(length))
                       for period in self._periods]
        self.reset()

    @property
    def parameters(self):
        return self._parameters

    @property
    def min_period(self):
        return self.parameters.min_period

    @property
    def max_period(self):
        return self.parameters.max_period

    @property
    def warmup_bars(self):
        return self.parameters.window_length-1

    @property
    def is_primed(self):
        return self._count >= self.parameters.window_length

    @property
    def samples_seen(self):
        return self._count

    @property
    def state(self):
        return SpectrumState(self._roof.h1, self._roof.f1, tuple(self._raw),
                             self._maximum, self._dominant)

    @property
    def output(self):
        return self._output

    def reset(self):
        self._roof.reset()
        self._count = 0
        self._history = [0.0]*self.parameters.window_length
        self._raw = [0.0]*len(self._periods)
        self._maximum = self._dominant = 0.0
        self._has_dominant = False
        self._output = SpectrumOutput(Heatmap.empty(None, self.min_period, self.max_period), math.nan)

    def update(self, close, time=None):
        price = _sample(close)
        p = self.parameters
        if math.isnan(price):
            return SpectrumOutput(Heatmap.empty(time, p.min_period, p.max_period), math.nan)
        high, filtered = self._roof.candidate(price)
        history = [filtered]+self._history[:-1]
        raw = []
        for i, period in enumerate(self._periods):
            comp = float(period) if p.spectral_dilation_compensation else 1.0
            cosine_part = sine_part = 0.0
            for n in range(p.window_length):
                # Divide EACH amplitude contribution by period BEFORE summing
                # and squaring. Book compensation thus scales power by 1/P^2,
                # not 1/P. Moving the division outside the sum changes rounding.
                cosine_part = cosine_part + history[n]*self._cosines[i][n]/comp
                sine_part = sine_part + history[n]*self._sines[i][n]/comp
            raw.append(cosine_part*cosine_part+sine_part*sine_part)
        maximum, dominant, has_dc, values = _normalize_and_centroid(
            self._periods, raw, self._maximum, self._dominant, self._has_dominant,
            p.enhance_resolution)
        # Internal state evolves from bar 1 using zero prehistory, even though
        # public output waits for the first completely real observation window.
        self._roof.commit(price, high, filtered)
        self._history, self._raw = history, raw
        self._maximum, self._dominant, self._has_dominant = maximum, dominant, has_dc
        self._count += 1
        if self.is_primed:
            self._output = SpectrumOutput(_column(time, p.min_period, p.max_period, values),
                                          dominant if has_dc else math.nan)
        else:
            self._output = SpectrumOutput(Heatmap.empty(time, p.min_period, p.max_period), math.nan)
        return self._output


# Fixture tooling below is not part of the streaming indicator.
INDICATOR_SLUG = 'discrete-fourier-transform-spectrum'
MASTER_CLASS = DiscreteFourierTransformSpectrum
REFERENCE_INPUT = 'close'
PARAMETER_SHORTCUTS = {'min_lag': 'L0', 'max_lag': 'L1', 'averaging_length': 'A', 'min_period': 'P0', 'max_period': 'P1', 'window_length': 'W', 'highpass_period': 'HP', 'smoothing_period': 'LP', 'spectral_dilation_compensation': 'SDC', 'enhance_resolution': 'E', 'bandwidth': 'B'}
REFERENCE_CASES = (
    {'min_period': 10, 'max_period': 48, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'spectral_dilation_compensation': True, 'enhance_resolution': False, 'window_length': 48, 'what_it_tests': 'Published compensated DFT, fixed maximum normalization, and dominant period.'},
    {'min_period': 10, 'max_period': 48, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'spectral_dilation_compensation': False, 'enhance_resolution': False, 'window_length': 48, 'what_it_tests': 'Uncompensated amplitude spectrum.'},
    {'min_period': 10, 'max_period': 48, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'spectral_dilation_compensation': True, 'enhance_resolution': True, 'window_length': 48, 'what_it_tests': 'Cubic display contrast after the unchanged dominant-period calculation.'},
    {'min_period': 10, 'max_period': 48, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'spectral_dilation_compensation': False, 'enhance_resolution': True, 'window_length': 48, 'what_it_tests': 'Uncompensated spectrum with cubic display contrast.'},
    {'min_period': 10, 'max_period': 48, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'spectral_dilation_compensation': True, 'enhance_resolution': False, 'window_length': 24, 'what_it_tests': 'Short Fourier observation window and end effects.'},
    {'min_period': 10, 'max_period': 48, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'spectral_dilation_compensation': True, 'enhance_resolution': False, 'window_length': 96, 'what_it_tests': 'Long Fourier observation window.'},
    {'min_period': 10, 'max_period': 48, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'spectral_dilation_compensation': True, 'enhance_resolution': False, 'window_length': 252, 'what_it_tests': 'Record-length boundary: first complete DFT at the final shared close.'},
    {'min_period': 10, 'max_period': 48, 'highpass_period': 48.0, 'smoothing_period': 10.5, 'spectral_dilation_compensation': True, 'enhance_resolution': False, 'window_length': 48, 'what_it_tests': 'Fractional SuperSmoother cutoff.'},
    {'min_period': 10, 'max_period': 48, 'highpass_period': 80.0, 'smoothing_period': 20.0, 'spectral_dilation_compensation': True, 'enhance_resolution': False, 'window_length': 48, 'what_it_tests': 'Slower independent roofing band.'},
    {'min_period': 6, 'max_period': 24, 'highpass_period': 24.0, 'smoothing_period': 6.0, 'spectral_dilation_compensation': True, 'enhance_resolution': False, 'window_length': 24, 'what_it_tests': 'Compact spectrum including shorter cycles.'},
    {'min_period': 20, 'max_period': 20, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'spectral_dilation_compensation': True, 'enhance_resolution': False, 'window_length': 48, 'what_it_tests': 'Single-period spectrum and exact centroid when selected.'},
    {'min_period': 24, 'max_period': 60, 'highpass_period': 60.0, 'smoothing_period': 12.0, 'spectral_dilation_compensation': True, 'enhance_resolution': False, 'window_length': 60, 'what_it_tests': 'Shifted longer-cycle spectrum.'},
)
# All 36 cases across the three masters confirmed by the user, 2026-10-22.
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


def _array_body(values, indent, nan, language):
    if values and isinstance(values[0], list):
        opening, closing = {'py': ('[', ']'), 'go': ('{', '}'),
                            'ts': ('[', ']'), 'rs': ('vec![', ']'),
                            'zig': ('.{', '}')}[language]
        return '\n'.join(indent+opening+', '.join(_float_literal(v, nan) for v in row)
                          + closing+',' for row in values)
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


def _run_reference(case, inputs):
    indicator = MASTER_CLASS(**{k:v for k,v in case.items() if k != 'what_it_tests'})
    output = [indicator.update(close) for close in inputs['INPUT_CLOSE']]
    maps = [r.heatmap for r in output] if hasattr(output[0], 'heatmap') else output
    bins = indicator.max_period-indicator.min_period+1
    arrays = {
        'HEATMAP': [list(r.values) if r.values else [math.nan]*bins for r in maps],
        'MIN': [r.value_min for r in maps],
        'MAX': [r.value_max for r in maps],
    }
    if hasattr(output[0], 'dominant_cycle'):
        arrays['DOMINANT_CYCLE'] = [r.dominant_cycle for r in output]
    return arrays


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
                            +f'{name} = [\n'+_array_body(values, '    ', 'NaN', 'py')+'\n]')
    _write_section(python_path, '\n\n'.join(sections), '#')
    # Reopen Python literals and verify dimensions, values, and every NaN.
    # All other languages translate this authoritative rounded Python data.
    written = _load_arrays(python_path)
    if {n for n in written if n.startswith('EXPECTED_')} != set(arrays):
        raise ValueError('missing or unexpected Python reference arrays')
    for name, (case, raw) in arrays.items():
        actual = written[name]
        axis = MASTER_CLASS(**{k:v for k,v in case.items() if k != 'what_it_tests'})
        bins = axis.max_period-axis.min_period+1
        matrix = isinstance(raw[0], list)
        if len(actual) != 252 or (matrix and any(len(row) != bins for row in actual)):
            raise ValueError(f'incorrect dimensions: {name}')
        flat = [v for row in actual for v in row] if matrix else actual
        raw_flat = [v for row in raw for v in row] if matrix else raw
        for source, literal in zip(raw_flat, flat):
            if math.isnan(source):
                if not math.isnan(literal):
                    raise ValueError(f'incorrect NaN mask: {name}')
            elif literal != float(_float_literal(source, 'NaN')):
                raise ValueError(f'incorrect 15-digit value: {name}')
    translated = {language: [] for language in ('go', 'ts', 'rs', 'zig')}
    for name, (case, raw) in arrays.items():
        suffix = name.removeprefix('EXPECTED_')
        values = written[name]
        matrix = isinstance(raw[0], list)
        axis = MASTER_CLASS(**{k:v for k,v in case.items() if k != 'what_it_tests'})
        bins = axis.max_period-axis.min_period+1
        comments = f"// {case['what_it_tests']}\n// {_parameter_comment(case)}\n"
        go_type = '[][]float64' if matrix else '[]float64'
        ts_type = 'number[][]' if matrix else 'number[]'
        rs_type = 'Vec<Vec<f64>>' if matrix else 'Vec<f64>'
        zig_type = f'[252][{bins}]f64' if matrix else '[252]f64'
        translated['go'].append(comments+f'var expected{suffix} = {go_type}{{\n'
                                +_array_body(values, '\t', 'math.NaN()', 'go')+'\n}')
        translated['ts'].append(comments+f'export const expected{suffix}: {ts_type} = [\n'
                                +_array_body(values, '    ', 'NaN', 'ts')+'\n];')
        translated['rs'].append(comments+f'pub fn expected_{suffix.lower()}() -> {rs_type} {{\n    vec![\n'
                                +_array_body(values, '        ', 'f64::NAN', 'rs')+'\n    ]\n}')
        translated['zig'].append(comments+f'pub fn expected{suffix}() {zig_type} {{\n    return .{{\n'
                                 +_array_body(values, '        ', 'nan', 'zig')+'\n    };\n}')
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
    # Exact original INPUT_CLOSE copied here so the demo also runs standalone.
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
        output = [indicator.update(close) for close in INPUT_CLOSE]
        print(f'{INDICATOR_SLUG}: {len(output)} accepted closes; warmup={indicator.warmup_bars}')
        print('Last output:', output[-1])
        print(f'Reference cases={len(REFERENCE_CASES)}; confirmed={REFERENCE_CASES_CONFIRMED}')
