"""Streaming master for Ehlers' March 2008 filter-bank spectrum.

Outputs: a period/dB heatmap column, dominant cycle, Sine (Value1), and
Cosine (Value2). See description.md for all equations and source differences.
Only Python's standard library is used. The numerical class is independent
of the fixture generation utilities at the bottom of this file.
"""

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class Heatmap(NamedTuple):
    """Standalone equivalent of zpano's heatmap column, with an owned list.

    Index j means period parameter_first + j * parameter_resolution.
    The values are the ARTICLE'S TRANSFORMED dB: lower means hotter.
    value_min/value_max describe this column, not a fixed display scale.
    time is optional metadata (datetime, integer, or any caller-owned token).
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


class FilterBankSpectrumOutput(NamedTuple):
    """One observation; sine/cosine retain price units, DC is in bars.

    Sine and Cosine are the published Value1 and Value2, not sin(phase)
    and cos(phase) with unit amplitude. They are not normalized oscillators.
    """

    heatmap: Heatmap
    dominant_cycle: float
    sine: float
    cosine: float


class Parameters(NamedTuple):
    min_period: int = 8
    max_period: int = 50
    centroid_min_period: int = 10
    highpass_period: float = 40.0
    median_length: int = 10
    bandwidth: float = 0.15


class FilterBankSpectrumState(NamedTuple):
    """Diagnostic snapshot, including hidden startup calculations.

    Immutable tuples keep callers from modifying numerical state. This is
    useful for porting/debugging; it is not an additional indicator output.
    """

    high_pass: float
    smoothed_high_pass: float
    delta: float
    centroid: float
    tuned_period: float
    sine: float
    cosine: float
    amplitudes: tuple[float, ...]
    decibels: tuple[float, ...]


def _integer(value, name, minimum):
    # Reject booleans despite bool being an int subclass in Python.
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return value


def _real(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{name} must be a finite real number')
    try:
        value = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f'{name} must be a finite real number') from error
    if not math.isfinite(value):
        raise ValueError(f'{name} must be a finite real number')
    return value


class FilterBankSpectrum:
    """Causal, bounded-state channelized receiver and tuned oscillator.

    Defaults reproduce the article's SECOND listing: bank 8..50, centroid
    10..50. Set centroid_min_period=8 for the FIRST listing's spectrum/DC.
    Neither preset imports the copied ACP algorithm; only its heatmap shape
    is reused. Generalized parameters are research extensions to the article.

    All prehistory is zero, INCLUDING the previous price before the first
    update. HP is still computed on bar one, though SmoothHP is forced to
    zero. The bank begins on accepted bar seven. The centroid and tuned
    oscillator run on EVERY accepted bar, even before public priming.
    """

    def __init__(self, min_period=8, max_period=50, centroid_min_period=10,
                 highpass_period=40.0, median_length=10, bandwidth=0.15):
        first = _integer(min_period, 'min_period', 8)
        last = _integer(max_period, 'max_period', first)
        centroid_first = _integer(centroid_min_period, 'centroid_min_period', first)
        if centroid_first > last:
            raise ValueError('centroid_min_period must not exceed max_period')
        median = _integer(median_length, 'median_length', 1)
        hp_period = _real(highpass_period, 'highpass_period')
        if hp_period <= 4.0:
            raise ValueError('highpass_period must exceed 4 bars')
        width = _real(bandwidth, 'bandwidth')
        if not 0.0 < width <= 0.5:
            raise ValueError('bandwidth must be in (0, 0.5]')
        self.parameters = Parameters(first, last, centroid_first, hp_period, median, width)
        self.min_period, self.max_period = first, last
        self.periods = tuple(range(first, last + 1))
        # EL trig uses degrees; 360/P becomes 2*pi/P in Python.
        angle = 2.0 * math.pi / hp_period
        self._hp_alpha = (1.0 - math.sin(angle)) / math.cos(angle)
        self._betas = [math.cos(2.0 * math.pi / period) for period in self.periods]
        # warmup_bars counts unavailable samples, not the first valid bar.
        # With defaults it is 9: output index 9 (one-based bar 10) is valid.
        self.warmup_bars = max(6, median - 1)
        self.reset()

    def reset(self):
        """Restore the exact deterministic zero-prehistory starting state."""
        size = len(self.periods)
        self.samples_seen = 0
        self._previous_price = 0.0
        self._hp = [0.0] * 6  # newest first: HP[1]..HP[6] before an update
        self._smooth = 0.0
        # These are explicit EL array histories, NOT price-indexed arrays.
        self._old_i, self._older_i = [0.0] * size, [0.0] * size
        self._old_q, self._older_q = [0.0] * size, [0.0] * size
        self._old_real, self._older_real = [0.0] * size, [0.0] * size
        self._old_imag, self._older_imag = [0.0] * size, [0.0] * size
        self._amplitudes, self._db = [0.0] * size, [0.0] * size
        self._dc = self._tuned_period = 0.0
        self._dc_history = [0.0] * self.parameters.median_length
        self._sine = self._older_sine = self._cosine = 0.0
        self._delta = 0.1  # published variable initializer; overwritten on bar 1
        self.output = self._unavailable(None)

    @property
    def is_primed(self):
        return self.samples_seen > self.warmup_bars

    @property
    def state(self):
        return FilterBankSpectrumState(
            self._hp[0], self._smooth, self._delta, self._dc, self._tuned_period,
            self._sine, self._cosine, tuple(self._amplitudes), tuple(self._db))

    def _unavailable(self, time):
        return FilterBankSpectrumOutput(
            Heatmap.empty(time, self.min_period, self.max_period),
            math.nan, math.nan, math.nan)

    @staticmethod
    def _alpha(period, delta):
        # Keep the source expression/order rather than algebraically
        # rationalizing it: cross-language numerical comparisons depend on it.
        gamma = 1.0 / math.cos(4.0 * math.pi * delta / period)
        return gamma - math.sqrt(gamma * gamma - 1.0)

    def update(self, value, time=None):
        """Consume one price and return an owned output snapshot.

        NaN returns an empty/NaN result without advancing or changing state.
        Infinite/non-numeric/overflowing inputs raise ValueError atomically.
        Missing observations therefore compress time; interpolate beforehand
        if that is inappropriate for the caller's sampling assumptions.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('input must be a real number; NaN may mark missing data')
        try:
            price = float(value)
        except (OverflowError, ValueError) as error:
            raise ValueError('input cannot be represented as a float') from error
        if math.isnan(price):
            return self._unavailable(time)
        if not math.isfinite(price):
            raise ValueError('input must not be infinite')
        p = self.parameters
        bar = self.samples_seen + 1  # EL CurrentBar is one-based.

        # Compute candidates before committing ANY state. Rejected large
        # inputs must not poison one channel's history or the HP recurrence.
        hp = (0.5 * (1.0 + self._hp_alpha) * (price - self._previous_price)
              + self._hp_alpha * self._hp[0])
        smooth = (hp + 2.0 * self._hp[0] + 3.0 * self._hp[1]
                  + 3.0 * self._hp[2] + 2.0 * self._hp[3] + self._hp[4]) / 12.0
        if bar < 7:
            smooth = price - self._previous_price
        if bar == 1:
            smooth = 0.0
        # Literal schedule reaches default 0.15 on bar 24, not about bar 50
        # as stated in the article's prose. Preserve the executable equation.
        delta = max(p.bandwidth, -0.015 * bar + 0.5)
        size = len(self.periods)
        current_i, current_q = [0.0] * size, [0.0] * size
        real, imag, power = [0.0] * size, [0.0] * size, [0.0] * size
        if bar > 6:
            for j, period in enumerate(self.periods):
                alpha = self._alpha(period, delta)
                beta = self._betas[j]
                current_i[j] = smooth
                current_q[j] = (period / (2.0 * math.pi)) * (smooth - self._smooth)
                # The bank has a TWO-bar input difference (OlderI/OlderQ).
                # Freeze all previous states until every channel is computed.
                real[j] = (0.5 * (1.0 - alpha) * (current_i[j] - self._older_i[j])
                           + beta * (1.0 + alpha) * self._old_real[j]
                           - alpha * self._older_real[j])
                imag[j] = (0.5 * (1.0 - alpha) * (current_q[j] - self._older_q[j])
                           + beta * (1.0 + alpha) * self._old_imag[j]
                           - alpha * self._older_imag[j])
                power[j] = real[j] * real[j] + imag[j] * imag[j]
        # MaxAmpl=Ampl[10] followed by a complete maximum scan is simply
        # max(power). This also works for research banks not containing 10.
        maximum = max(power)
        db = self._db.copy()
        for j in range(size):
            # Guard failure RETAINS the previous DB, including initial zero.
            # Replacing it with 20 or NaN would change published DC behavior.
            if maximum != 0.0 and power[j] / maximum > 0.0:
                db[j] = (-10.0 * math.log(0.01 / (1.0 - 0.99 * power[j] / maximum))
                         / math.log(10.0))
            if db[j] > 20.0:
                db[j] = 20.0

        numerator = denominator = 0.0
        dc = self._dc  # Also retained if no channel passes the threshold.
        for j, period in enumerate(self.periods):
            if period >= p.centroid_min_period:
                if db[j] <= 3.0:
                    numerator += period * (20.0 - db[j])
                    denominator += 20.0 - db[j]
                if denominator != 0.0:
                    dc = numerator / denominator
        history = [dc] + self._dc_history[:-1]
        ordered = sorted(history)
        middle = p.median_length // 2
        dominant = (ordered[middle] if p.median_length % 2 else
                    (ordered[middle - 1] + ordered[middle]) / 2.0)
        # Source safety fallback matters during hidden zero-padded startup.
        if dominant < 8.0:
            dominant = 20.0
        alpha = self._alpha(dominant, delta)
        beta = math.cos(2.0 * math.pi / dominant)
        # Value1 deliberately uses a ONE-bar input difference. The article's
        # tuned-filter equation differs from the bank; do not replace it.
        sine = (0.5 * (1.0 - alpha) * (smooth - self._smooth)
                + beta * (1.0 + alpha) * self._sine - alpha * self._older_sine)
        cosine = (dominant / (2.0 * math.pi)) * (sine - self._sine)
        candidates = [hp, smooth, dc, dominant, sine, cosine] + current_q + real + imag + power + db
        if not all(math.isfinite(number) for number in candidates):
            raise ValueError('input causes non-finite filter arithmetic; state was not changed')

        # The following assignments are exactly the end-of-bar EL shifts.
        self._older_i, self._old_i = self._old_i, current_i
        self._older_q, self._old_q = self._old_q, current_q
        self._older_real, self._old_real = self._old_real, real
        self._older_imag, self._old_imag = self._old_imag, imag
        # OldAmpl from the listing is unused, so no dead history is stored.
        self._amplitudes, self._db = power, db
        self._hp, self._smooth = [hp] + self._hp[:5], smooth
        self._previous_price = price
        self._dc, self._dc_history = dc, history
        self._tuned_period, self._delta = dominant, delta
        self._older_sine, self._sine, self._cosine = self._sine, sine, cosine
        self.samples_seen = bar
        if not self.is_primed:
            result = self._unavailable(time)
        else:
            # Own a COPY; editing the returned heatmap cannot change DB.
            column = Heatmap(time, float(p.min_period), float(p.max_period),
                             1.0, min(db), max(db), db.copy())
            result = FilterBankSpectrumOutput(column, dominant, sine, cosine)
        self.output = result
        return result


INDICATOR_SLUG = 'filter-bank-spectrum'
MASTER_CLASS = FilterBankSpectrum
REFERENCE_INPUT = 'close'
PARAMETER_SHORTCUTS = {'min_period': 'P', 'max_period': 'Q',
                      'centroid_min_period': 'C', 'highpass_period': 'HP',
                      'median_length': 'M', 'bandwidth': 'B'}
# Confirmed explicitly by the user for this task; NOT inherited from other
# indicators' confirmations. This prevents accidental unapproved export.
REFERENCE_CASES_CONFIRMED = True


def _case(first=8, last=50, centroid=10, hp=40.0, median=10, width=0.15, what=''):
    return dict(min_period=first, max_period=last, centroid_min_period=centroid,
                highpass_period=hp, median_length=median, bandwidth=width,
                what_it_tests=what)


REFERENCE_CASES = (
    _case(what='Article sine/cosine default'),
    _case(centroid=8, what='Article spectrum-display centroid'),
    _case(median=1, what='Unsmooth dominant cycle'),
    _case(median=5, what='Short median smoothing'),
    _case(median=20, what='Long median smoothing'),
    _case(width=0.10, what='Narrower resonators and longer ringing'),
    _case(width=0.25, what='Wider resonators and faster decay'),
    _case(hp=20.0, what='Short high-pass cutoff'),
    _case(hp=80.0, what='Long high-pass cutoff'),
    _case(first=10, last=30, what='Compact period bank'),
    _case(last=80, what='Extended period bank'),
    _case(first=20, last=20, centroid=20, what='Single-channel normalization'),
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
    arrays['SINE'] = [r.sine for r in output]
    arrays['COSINE'] = [r.cosine for r in output]
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
    # Embedded exact 252 INPUT_CLOSE observations make the example standalone.
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
        indicator = FilterBankSpectrum()
        results = [indicator.update(price, time=i) for i, price in enumerate(INPUT_CLOSE)]
        print(f'{len(results)} closes; first valid bar={indicator.warmup_bars + 1}')
        print('Last output:', results[-1])
        print(f'{len(REFERENCE_CASES)} confirmed cases; generate with --generate-reference-data')
