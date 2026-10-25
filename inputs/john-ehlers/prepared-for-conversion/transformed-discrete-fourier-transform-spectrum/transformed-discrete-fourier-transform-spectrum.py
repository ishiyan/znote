"""Streaming master: Ehlers' January 2007 transformed DFT spectrum.

The 2007 article and matching MESA paper are the numerical authority.
Returns a transformed-dB heatmap and dominant period in bars. This is not
the later 2013 book's roofed, dilation-compensated, AGC-normalized DFT.
Standard library only. See description.md for every equation and convention.
"""

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class Heatmap(NamedTuple):
    """One owned column, matching the supplied zpano Heatmap field layout.

    values[j] corresponds to parameter_first+j*parameter_resolution.
    Values are the source's transformed dB attenuation, LOWER is hotter.
    Extrema describe the actual column; time is optional caller metadata.
    """

    time: object
    parameter_first: float
    parameter_last: float
    parameter_resolution: float
    value_min: float
    value_max: float
    values: list[float]

    def is_empty(self) -> bool:
        return len(self.values) == 0

    @staticmethod
    def empty(time, first, last, resolution=1.0):
        return Heatmap(time, float(first), float(last), float(resolution),
                       math.nan, math.nan, [])


class TransformedDiscreteFourierTransformSpectrumOutput(NamedTuple):
    """Requested outputs; the real-valued dominant cycle is measured in bars."""

    heatmap: Heatmap
    dominant_cycle: float


class Parameters(NamedTuple):
    min_period: int = 8
    max_period: int = 50
    window_length: int = 50
    highpass_period: float = 40.0


class SpectrumState(NamedTuple):
    """Immutable diagnostics for port verification, including hidden startup.

    cosine_parts and sine_parts are Fourier sums, not oscillator outputs.
    Their histories are recomputed each bar; only DB and DC retain guarded
    values. Raw powers are not normalized or spectrally compensated.
    """

    high_pass: float
    cleaned_data: float
    maximum_power: float
    dominant_cycle: float
    cosine_parts: tuple[float, ...]
    sine_parts: tuple[float, ...]
    powers: tuple[float, ...]
    decibels: tuple[float, ...]


def _integer(value, name, minimum):
    # Python bool is an int subclass; reject it as a configuration accident.
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return value


def _real(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{name} must be a finite real number')
    try:
        number = float(value)
    except (ValueError, OverflowError) as error:
        raise ValueError(f'{name} must be a finite real number') from error
    if not math.isfinite(number):
        raise ValueError(f'{name} must be a finite real number')
    return number


class TransformedDiscreteFourierTransformSpectrum:
    """Causal moving-window Fourier estimator with the article's transform.

    min_period/max_period/highpass_period generalize fixed article constants;
    window_length corresponds to its Window input. Price is supplied to each
    update, using the 252 closes for this reference (article default is HL2).
    No NumPy, FFT, autocorrelation, AGC, dilation correction or median is used.

    All absent historical values are zero. On accepted bars 1..5, BOTH HP
    and CleanedData are the input price. Bar 6 first applies the HP/FIR.
    The DFT, DB and DC are calculated on EVERY bar, using zero-padded early
    history. Public results are masked until max(6, window_length) bars.
    """

    def __init__(self, min_period=8, max_period=50, window_length=50,
                 highpass_period=40.0):
        first = _integer(min_period, 'min_period', 8)
        last = _integer(max_period, 'max_period', first)
        window = _integer(window_length, 'window_length', 1)
        hp_period = _real(highpass_period, 'highpass_period')
        if hp_period <= 4.0:
            raise ValueError('highpass_period must exceed 4 bars')
        self.parameters = Parameters(first, last, window, hp_period)
        self.min_period, self.max_period = first, last
        self.periods = tuple(range(first, last + 1))
        # EL uses degrees. Use full precision radians, not 3.14159/6.283185.
        omega = 2.0 * math.pi / hp_period
        self.highpass_alpha = (1.0 - math.sin(omega)) / math.cos(omega)
        # Tables are constant for a given configuration. Computing the same
        # ordinary trig functions inside the loops is also valid in a port.
        # Keep angle order 2*pi*n/period and sum newest samples first.
        self._cosines = [tuple(math.cos(2.0 * math.pi * n / period)
                               for n in range(window)) for period in self.periods]
        self._sines = [tuple(math.sin(2.0 * math.pi * n / period)
                             for n in range(window)) for period in self.periods]
        # This counts unavailable outputs, so defaults first publish index 49.
        self.warmup_bars = max(5, window - 1)
        self.reset()

    def reset(self):
        """Restore deterministic zero prehistory without changing parameters."""
        size = len(self.periods)
        self.samples_seen = 0
        self._previous_price = 0.0
        self._hp = [0.0] * 6  # newest first before update: HP[1]..HP[6]
        self._cleaned = 0.0
        self._window = [0.0] * self.parameters.window_length
        self._cosine_parts, self._sine_parts = [0.0] * size, [0.0] * size
        self._powers, self._db = [0.0] * size, [0.0] * size
        self._maximum = self._dc = 0.0
        self.output = self._unavailable(None)

    @property
    def is_primed(self):
        return self.samples_seen > self.warmup_bars

    @property
    def state(self):
        return SpectrumState(self._hp[0], self._cleaned, self._maximum, self._dc,
                             tuple(self._cosine_parts), tuple(self._sine_parts),
                             tuple(self._powers), tuple(self._db))

    def _unavailable(self, time):
        return TransformedDiscreteFourierTransformSpectrumOutput(
            Heatmap.empty(time, self.min_period, self.max_period), math.nan)

    def update(self, value, time=None):
        """Consume one price, returning a heatmap and dominant-cycle snapshot.

        NaN means omitted observation: no state/count/last-output changes.
        Infinity, invalid types and arithmetic overflow raise ValueError
        atomically. Accepted samples define the evenly spaced bar timeline.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('input must be a real number; NaN may mark missing data')
        try:
            price = float(value)
        except (ValueError, OverflowError) as error:
            raise ValueError('input cannot be represented as a float') from error
        if math.isnan(price):
            return self._unavailable(time)
        if not math.isfinite(price):
            raise ValueError('input must not be infinite')
        bar = self.samples_seen + 1  # EasyLanguage CurrentBar is one-based.
        if bar <= 5:
            # Do NOT substitute zero or a price difference during startup.
            # These prices also become the initial HP and DFT histories.
            hp = cleaned = price
        else:
            hp = (0.5 * (1.0 + self.highpass_alpha) * (price - self._previous_price)
                  + self.highpass_alpha * self._hp[0])
            cleaned = (hp + 2.0 * self._hp[0] + 3.0 * self._hp[1]
                       + 3.0 * self._hp[2] + 2.0 * self._hp[3] + self._hp[4]) / 12.0
        # Build candidates without modifying recursive state. Window length
        # is EXACTLY W, including the current value, offsets 0 through W-1.
        window = [cleaned] + self._window[:-1]
        cosine_parts, sine_parts, powers = [], [], []
        for j, period in enumerate(self.periods):
            cosine = sine = 0.0
            for n in range(self.parameters.window_length):
                cosine += window[n] * self._cosines[j][n]
                sine += window[n] * self._sines[j][n]
            cosine_parts.append(cosine)
            sine_parts.append(sine)
            powers.append(cosine * cosine + sine * sine)
        # The article uses MaxPwr=Pwr[8] then scans all periods. max() is
        # equivalent and remains valid when a research bank excludes 8.
        maximum = max(powers)
        db = self._db.copy()
        for j, power in enumerate(powers):
            # Guard failure RETAINS DB[j]. Its initial zero is deliberately
            # preserved, including the source's hot-looking silent spectrum.
            if maximum > 0.0 and power > 0.0:
                db[j] = (-10.0 * math.log(0.01 / (1.0 - 0.99 * power / maximum))
                         / math.log(10.0))
            if db[j] > 20.0:
                db[j] = 20.0
        numerator = denominator = 0.0
        for period, decibels in zip(self.periods, db):
            # This is STRICTLY <3 and weight (3-DB), unlike the 2008
            # filter-bank indicator's <=3 and (20-DB), or the 2013 power CG.
            if decibels < 3.0:
                numerator += period * (3.0 - decibels)
                denominator += 3.0 - decibels
        dominant = numerator / denominator if denominator != 0.0 else self._dc
        candidates = [hp, cleaned, maximum, dominant] + cosine_parts + sine_parts + powers + db
        if not all(math.isfinite(v) for v in candidates):
            raise ValueError('input causes non-finite filter arithmetic; state was not changed')

        # Commit only after ALL channels and the centroid are valid. Returned
        # heatmap lists must never share the mutable DB storage used next bar.
        self._previous_price = price
        self._hp, self._cleaned = [hp] + self._hp[:5], cleaned
        self._window = window
        self._cosine_parts, self._sine_parts = cosine_parts, sine_parts
        self._powers, self._db = powers, db
        self._maximum, self._dc = maximum, dominant
        self.samples_seen = bar
        if self.is_primed:
            column = Heatmap(time, float(self.min_period), float(self.max_period),
                             1.0, min(db), max(db), db.copy())
            result = TransformedDiscreteFourierTransformSpectrumOutput(column, dominant)
        else:
            result = self._unavailable(time)
        self.output = result
        return result


# Fixture tooling is intentionally separate from the streaming calculation.
INDICATOR_SLUG = 'transformed-discrete-fourier-transform-spectrum'
MASTER_CLASS = TransformedDiscreteFourierTransformSpectrum
REFERENCE_INPUT = 'close'
PARAMETER_SHORTCUTS = {'min_period': 'P', 'max_period': 'Q',
                      'window_length': 'W', 'highpass_period': 'HP'}
# Only this task's explicit confirmation can authorize reference generation.
REFERENCE_CASES_CONFIRMED = True


def _case(first=8, last=50, window=50, hp=40.0, what=''):
    return dict(min_period=first, max_period=last, window_length=window,
                highpass_period=hp, what_it_tests=what)


REFERENCE_CASES = (
    _case(what='Article defaults'),
    _case(window=1, what='Minimum window and equal-power channels'),
    _case(window=20, what='Short window and broad spectral peaks'),
    _case(window=48, what='Window matching the 2013 book'),
    _case(window=64, what='Longer observation window'),
    _case(window=252, what='First valid output at the final input'),
    _case(hp=20.0, what='Short high-pass cutoff'),
    _case(hp=80.0, what='Long high-pass cutoff'),
    _case(hp=40.5, what='Fractional high-pass coefficient period'),
    _case(first=10, last=30, what='Compact period bank'),
    _case(last=80, what='Extended period bank'),
    _case(first=20, last=20, what='Single-channel normalization and centroid'),
)


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
        if path.suffix == '.rs':
            # Keep expected functions INSIDE the original cfg(test) module.
            original = original.rstrip()
            if not original.endswith('}'):
                raise ValueError('expected a closing Rust testdata module')
            result = original[:-1].rstrip()+'\n\n'+block+'\n}\n'
        else:
            result = original.rstrip()+'\n\n'+block+'\n'
    path.write_text(result, encoding='utf-8')


def _run_reference(case, inputs):
    indicator = MASTER_CLASS(**{k:v for k,v in case.items() if k != 'what_it_tests'})
    output = [indicator.update(close) for close in inputs['INPUT_CLOSE']]
    maps = [r.heatmap for r in output]
    bins = indicator.max_period-indicator.min_period+1
    arrays = {
        'HEATMAP': [list(r.values) if r.values else [math.nan]*bins for r in maps],
        'MIN': [r.value_min for r in maps],
        'MAX': [r.value_max for r in maps],
    }
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
    parser.add_argument('--generate-reference-data', action='store_true',
                        help='write and verify all confirmed five-language fixtures')
    args = parser.parse_args()
    # Exact 252 INPUT_CLOSE values embedded for a standalone streaming demo.
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
        indicator = TransformedDiscreteFourierTransformSpectrum()
        results = [indicator.update(price, time=i) for i, price in enumerate(INPUT_CLOSE)]
        print(f'{len(results)} closes; first valid bar={indicator.warmup_bars + 1}')
        print('Last output:', results[-1])
        print(f'{len(REFERENCE_CASES)} reference cases; confirmed={REFERENCE_CASES_CONFIRMED}')
