"""swami-relative-strength-index: self-contained streaming research prototype master.

Read description.md before conversion. Only standard-library Python is used.
__main__ embeds the shared OHLC inputs, demonstrates the default, and includes
the five-language generator. All 56 Swami reference cases were confirmed
by the user on 2026-10-21, including the eight cases in this folder.
"""

from __future__ import annotations
import argparse
import ast
import datetime
import math
from pathlib import Path
from typing import NamedTuple


class Heatmap(NamedTuple):
    """An independently owned column, with the requested zpano field names.

    values[i] belongs to parameter_first + i*parameter_resolution. time is
    optional caller metadata; it has no effect on calculations. Empty columns
    use an empty values list and NaN bounds. Do not put public NaNs into state.
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


def _column(time, first, last, values):
    # Bounds describe this column's actual values, not the palette's endpoints.
    # Allocate/copy at the API boundary so an old output survives later calls.
    owned = list(values)
    return Heatmap(time, float(first), float(last), 1.0,
                   min(owned) if owned else math.nan,
                   max(owned) if owned else math.nan, owned)


def _integer(value, name, minimum=1):
    # Python bool is an integer subclass; it is not a useful period setting.
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _real(value, name, minimum=None):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite real")
    value = float(value)
    if not math.isfinite(value) or (minimum is not None and value < minimum):
        raise ValueError(f"{name} must be finite and >= {minimum}")
    return value


def _range(first, last, minimum=2):
    first = _integer(first, 'min_period', minimum)
    last = _integer(last, 'max_period', first)
    return first, last


def _weight(value, name):
    value = _real(value, name)
    if not 0.0 < value <= 1.0:
        raise ValueError(f"{name} must be in (0, 1]")
    return value


def _complement(weight):
    # .33 and .67 are independently specified EasyLanguage literals. Preserve
    # both at the default; do not reinterpret them as rounded thirds.
    return 0.67 if weight == 0.33 else 1.0-weight


def _sample(value):
    # NaN means an omitted observation: no clock, history, or recursive state
    # advances. Infinity is an error. Each master returns an empty column on
    # a skipped call, even if it was already primed on the preceding call.
    value = float(value)
    if math.isinf(value):
        raise ValueError('input must be finite or NaN')
    return value


def _push(history, value, capacity):
    # Newest FIRST makes EasyLanguage X[j] translate directly to history[j].
    # Bounded lists are intentionally simple to port to fixed circular arrays.
    history.insert(0, value)
    if len(history) > capacity:
        history.pop()


def _smoother_coefficients(period):
    # EasyLanguage uses degrees; this common angle is in radians. Replace
    # printed 1.414 and 3.14159 with sqrt(2) and pi in BOTH exp and cosine.
    angle = math.sqrt(2.0) * math.pi / period
    decay = math.exp(-angle)
    c2 = 2.0 * decay * math.cos(angle)
    c3 = -decay * decay
    c1 = 1.0 - c2 - c3
    if not 0.0 < decay < 1.0 or c1 <= 0.0:
        raise ValueError('period exceeds representable stable coefficient range')
    return c1, c2, c3


class _Roof:
    """Private two-pole HP then SuperSmoother, with actual raw differences.

    First two prices are stored; the first filtered output exists on bar 3.
    This helper exposes that finite internal value, without applying the
    separate standalone Roofing master's public warm-up mask.
    """

    def __init__(self, shortest, longest, convolution=False):
        shortest = _real(shortest, 'shortest_cycle_period', 2.0)
        longest = _real(longest, 'longest_cycle_period', 2.0)
        if longest <= shortest:
            raise ValueError('longest_cycle_period must exceed shortest_cycle_period')
        # Listing 13-1 prints 1.414*360/H, while listing 16 prints .707*360/H.
        # Preserve this FACTOR OF TWO, rather than silently fixing the book.
        factor = 2.0 if convolution else 1.0
        angle = factor * math.sqrt(2.0) * math.pi / longest
        if not 0.0 < angle < math.pi:
            raise ValueError('high-pass angle must be strictly between 0 and pi')
        # Equivalent half-angle form avoids the direct expression's removable
        # cos(angle)==0 singularity. See the mathematical derivation in docs.
        tangent = math.tan(angle / 2.0)
        alpha = 2.0 * tangent / (1.0 + tangent)
        self.gain = 1.0 - alpha / 2.0
        self.decay = 1.0 - alpha
        if not abs(self.decay) < 1.0:
            raise ValueError('high-pass pole must be representably stable')
        self.coefficients = _smoother_coefficients(shortest)
        self.reset()

    def reset(self):
        self.count = 0
        self.x1 = self.x2 = 0.0
        self.h1 = self.h2 = self.f1 = self.f2 = 0.0

    def update(self, price):
        result = None
        if self.count >= 2:
            # Calculate using OLD lagged state, then shift every lag exactly
            # once. Public availability does not suppress filter updates.
            h = (self.gain * self.gain * (price - 2.0*self.x1 + self.x2)
                 + 2.0*self.decay*self.h1 - self.decay*self.decay*self.h2)
            c1, c2, c3 = self.coefficients
            f = c1*(h + self.h1)/2.0 + c2*self.f1 + c3*self.f2
            self.h2, self.h1 = self.h1, h
            self.f2, self.f1 = self.f1, f
            result = f
        self.x2, self.x1 = self.x1, price
        self.count += 1
        return result



class SwamiRelativeStrengthIndex:
    """2012 contrast-amplified RSI or 2013 roofed finite-window RSI bank.

    Defaults use roofed_2013, periods 5..48, and both SuperSmoothers at 10
    with HP period 48. Classic defaults are periods 12..48, alpha=.33,
    contrast=4. Parameters of an inactive variant must remain at defaults.
    """

    def __init__(self, min_period=None, max_period=48, variant='roofed_2013',
                 alpha=0.33, contrast=4.0, shortest_cycle_period=10.0,
                 longest_cycle_period=48.0):
        if variant not in ('classic_2012', 'roofed_2013'):
            raise ValueError('unknown RSI variant')
        self.variant = variant
        self.min_period, self.max_period = _range(
            (12 if variant == 'classic_2012' else 5) if min_period is None else min_period,
            max_period, 1)
        self.alpha = _weight(alpha, 'alpha')
        self.contrast = _real(contrast, 'contrast', 0.0)
        self.shortest_cycle_period = _real(shortest_cycle_period, 'shortest_cycle_period', 2)
        self.longest_cycle_period = _real(longest_cycle_period, 'longest_cycle_period', 2)
        if variant == 'classic_2012':
            if (self.shortest_cycle_period, self.longest_cycle_period) != (10.0, 48.0):
                raise ValueError('roof periods do not configure classic_2012')
            self._roof = None
        else:
            if (self.alpha, self.contrast) != (0.33, 4.0):
                raise ValueError('EMA contrast does not configure roofed_2013')
            self._roof = _Roof(self.shortest_cycle_period, self.longest_cycle_period)
        self.reset()

    @property
    def warmup_bars(self):
        return self.max_period if self._roof is None else self.max_period + 4

    @property
    def is_primed(self):
        return self._count > self.warmup_bars

    def reset(self):
        self._count = 0
        self._previous = None
        self._history = []
        size = self.max_period-self.min_period+1
        self._net = [0.0]*size
        self._total = [0.0]*size
        self._ratio = [0.0]*size
        self._out1 = [0.0]*size
        self._out2 = [0.0]*size
        if self._roof is not None:
            self._roof.reset()

    def update(self, close, time=None):
        price = _sample(close)
        if math.isnan(price):
            return _column(time, self.min_period, self.max_period, [])
        self._count += 1
        if self._roof is None:
            if self._previous is not None:
                difference = price-self._previous
                for i, period in enumerate(range(self.min_period, self.max_period+1)):
                    # The source uses Wilder-style 1/P recurrences, seeded at
                    # zero, NOT an SMA seed or finite-window sum of changes.
                    self._net[i] += (1.0/period)*(difference-self._net[i])
                    self._total[i] += (1.0/period)*(abs(difference)-self._total[i])
                    ratio = self._net[i]/self._total[i] if self._total[i] != 0.0 else 0.0
                    out = (self.alpha*(self.contrast*ratio+1.0)/2.0
                           + _complement(self.alpha)*self._out1[i])
                    self._out1[i] = min(1.0, max(0.0, out))
            self._previous = price
        else:
            filtered = self._roof.update(price)
            if filtered is not None:
                _push(self._history, filtered, self.max_period+1)
                for i, period in enumerate(range(self.min_period, self.max_period+1)):
                    if len(self._history) < period+1:
                        continue  # P changes require P+1 actual filtered prices.
                    up = down = 0.0
                    for j in range(period):
                        newer, older = self._history[j], self._history[j+1]
                        if newer > older:
                            up = up + (newer-older)
                        if newer < older:
                            down = down + (older-newer)
                    total = up+down
                    ratio = up/total if total != 0.0 else self._ratio[i]
                    c1, c2, c3 = self._roof.coefficients
                    out = (c1*(ratio+self._ratio[i])/2.0
                           + c2*self._out1[i] + c3*self._out2[i])
                    self._out2[i] = self._out1[i]
                    self._out1[i] = min(1.0, max(0.0, out))
                    self._ratio[i] = ratio  # Retain previous ratio on a flat window.
        return _column(time, self.min_period, self.max_period,
                       self._out1 if self.is_primed else [])

INDICATOR_SLUG = 'swami-relative-strength-index'
MASTER_CLASS = SwamiRelativeStrengthIndex
REFERENCE_INPUT = 'close'
DIAGNOSTIC_COMPONENTS = ()
PARAMETER_SHORTCUTS = {'min_period': 'P0', 'max_period': 'P1', 'variant': 'V', 'range_alpha': 'RA', 'output_alpha': 'OA', 'alpha': 'A', 'contrast': 'C', 'shortest_cycle_period': 'LP', 'longest_cycle_period': 'HP', 'delta': 'D', 'fraction': 'F', 'peak_average_length': 'PA'}
REFERENCE_CASES = (
    {'variant': 'classic_2012', 'min_period': 12, 'max_period': 48, 'what_it_tests': 'Original 2012 Wilder-style changes with fourfold contrast.'},
    {'variant': 'classic_2012', 'min_period': 12, 'max_period': 48, 'contrast': 1.0, 'what_it_tests': 'Classic ratio without amplified contrast.'},
    {'variant': 'classic_2012', 'min_period': 12, 'max_period': 24, 'alpha': 0.1, 'what_it_tests': 'Compact classic bank with slower output EMA.'},
    {'variant': 'classic_2012', 'min_period': 1, 'max_period': 1, 'what_it_tests': 'Single one-change classic RSI boundary.'},
    {'variant': 'roofed_2013', 'min_period': 5, 'max_period': 48, 'what_it_tests': 'Book 2013 roofed default bank of finite-window gain/loss ratios.'},
    {'variant': 'roofed_2013', 'min_period': 5, 'max_period': 24, 'what_it_tests': 'Compact book bank and correct extra price for P changes.'},
    {'variant': 'roofed_2013', 'min_period': 5, 'max_period': 48, 'shortest_cycle_period': 10.5, 'what_it_tests': 'Fractional book low-pass coefficient period without rounding.'},
    {'variant': 'roofed_2013', 'min_period': 5, 'max_period': 48, 'shortest_cycle_period': 20.0, 'longest_cycle_period': 80.0, 'what_it_tests': 'Slower book roofing band and output smoothing.'},
)

# ---- Fixture tooling: port the numerical classes above, not this section. ----
# The user confirmed all 56 Swami cases on 2026-10-21 (eight in this folder).
# This recorded authorization also permits reproducible regeneration.
REFERENCE_CASES_CONFIRMED = True


def _parameter_token(value):
    if isinstance(value, str):
        return '2012' if value == 'classic_2012' else '2013'
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
    parameters = {key: value for key, value in case.items() if key != 'what_it_tests'}
    indicator = MASTER_CLASS(**parameters)
    output = []
    for bar, close in enumerate(inputs['INPUT_CLOSE']):
        if REFERENCE_INPUT == 'ohlc':
            result = indicator.update(close, inputs['INPUT_HIGH'][bar], inputs['INPUT_LOW'][bar])
        elif REFERENCE_INPUT == 'hl2':
            result = indicator.update((inputs['INPUT_HIGH'][bar]+inputs['INPUT_LOW'][bar])/2.0)
        else:
            result = indicator.update(close)
        output.append(result)
    bins = indicator.max_period-indicator.min_period+1
    maps = [r.heatmap if hasattr(r, 'heatmap') else r for r in output]
    arrays = {
        'HEATMAP': [r.values if not r.is_empty() else [math.nan]*bins for r in maps],
        'MIN': [r.value_min for r in maps],
        'MAX': [r.value_max for r in maps],
    }
    for component in DIAGNOSTIC_COMPONENTS:
        arrays[component.upper()] = [list(getattr(r, component)) if getattr(r, component)
                                     else [math.nan]*bins for r in output]
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
        bins = case['max_period']-case['min_period']+1
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
        bins = case['max_period']-case['min_period']+1
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
    # Exact shared 252 closes, highs and lows; embedded for standalone use.
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
    INPUT_HIGH = [
        93.250000, 94.940000, 96.375000, 96.190000, 96.000000, 94.720000, 95.000000, 93.720000, 92.470000, 92.750000,
        96.250000, 99.625000, 99.125000, 92.750000, 91.315000, 93.250000, 93.405000, 90.655000, 91.970000, 92.250000,
        90.345000, 88.500000, 88.250000, 85.500000, 84.440000, 84.750000, 84.440000, 89.405000, 88.125000, 89.125000,
        87.155000, 87.250000, 87.375000, 88.970000, 90.000000, 89.845000, 86.970000, 85.940000, 84.750000, 85.470000,
        84.470000, 88.500000, 89.470000, 90.000000, 92.440000, 91.440000, 92.970000, 91.720000, 91.155000, 91.750000,
        90.000000, 88.875000, 89.000000, 85.250000, 83.815000, 85.250000, 86.625000, 87.940000, 89.375000, 90.625000,
        90.750000, 88.845000, 91.970000, 93.375000, 93.815000, 94.030000, 94.030000, 91.815000, 92.000000, 91.940000,
        89.750000, 88.750000, 86.155000, 84.875000, 85.940000, 99.375000, 103.280000, 105.375000, 107.625000, 105.250000,
        104.500000, 105.500000, 106.125000, 107.940000, 106.250000, 107.000000, 108.750000, 110.940000, 110.940000, 114.220000,
        123.000000, 121.750000, 119.815000, 120.315000, 119.375000, 118.190000, 116.690000, 115.345000, 113.000000, 118.315000,
        116.870000, 116.750000, 113.870000, 114.620000, 115.310000, 116.000000, 121.690000, 119.870000, 120.870000, 116.750000,
        116.500000, 116.000000, 118.310000, 121.500000, 122.000000, 121.440000, 125.750000, 127.750000, 124.190000, 124.440000,
        125.750000, 124.690000, 125.310000, 132.000000, 131.310000, 132.250000, 133.880000, 133.500000, 135.500000, 137.440000,
        138.690000, 139.190000, 138.500000, 138.130000, 137.500000, 138.880000, 132.130000, 129.750000, 128.500000, 125.440000,
        125.120000, 126.500000, 128.690000, 126.620000, 126.690000, 126.000000, 123.120000, 121.870000, 124.000000, 127.000000,
        124.440000, 122.500000, 123.750000, 123.810000, 124.500000, 127.870000, 128.560000, 129.630000, 124.870000, 124.370000,
        124.870000, 123.620000, 124.060000, 125.870000, 125.190000, 125.620000, 126.000000, 128.500000, 126.750000, 129.750000,
        132.690000, 133.940000, 136.500000, 137.690000, 135.560000, 133.560000, 135.000000, 132.380000, 131.440000, 130.880000,
        129.630000, 127.250000, 127.810000, 125.000000, 126.810000, 124.750000, 122.810000, 122.250000, 121.060000, 120.000000,
        123.250000, 122.750000, 119.190000, 115.060000, 116.690000, 114.870000, 110.870000, 107.250000, 108.870000, 109.000000,
        108.500000, 113.060000, 93.000000, 94.620000, 95.120000, 96.000000, 95.560000, 95.310000, 99.000000, 98.810000,
        96.810000, 95.940000, 94.440000, 92.940000, 93.940000, 95.500000, 97.060000, 97.500000, 96.250000, 96.370000,
        95.000000, 94.870000, 98.250000, 105.120000, 108.440000, 109.870000, 105.000000, 106.000000, 104.940000, 104.500000,
        104.440000, 106.310000, 112.870000, 116.500000, 119.190000, 121.000000, 122.120000, 111.940000, 112.750000, 110.190000,
        107.940000, 109.690000, 111.060000, 110.440000, 110.120000, 110.310000, 110.440000, 110.000000, 110.750000, 110.500000,
        110.500000, 109.500000,
    ]
    INPUT_LOW = [
        90.750000, 91.405000, 94.250000, 93.500000, 92.815000, 93.500000, 92.000000, 89.750000, 89.440000, 90.625000,
        92.750000, 96.315000, 96.030000, 88.815000, 86.750000, 90.940000, 88.905000, 88.780000, 89.250000, 89.750000,
        87.500000, 86.530000, 84.625000, 82.280000, 81.565000, 80.875000, 81.250000, 84.065000, 85.595000, 85.970000,
        84.405000, 85.095000, 85.500000, 85.530000, 87.875000, 86.565000, 84.655000, 83.250000, 82.565000, 83.440000,
        82.530000, 85.065000, 86.875000, 88.530000, 89.280000, 90.125000, 90.750000, 89.000000, 88.565000, 90.095000,
        89.000000, 86.470000, 84.000000, 83.315000, 82.000000, 83.250000, 84.750000, 85.280000, 87.190000, 88.440000,
        88.250000, 87.345000, 89.280000, 91.095000, 89.530000, 91.155000, 92.000000, 90.530000, 89.970000, 88.815000,
        86.750000, 85.065000, 82.030000, 81.500000, 82.565000, 96.345000, 96.470000, 101.155000, 104.250000, 101.750000,
        101.720000, 101.720000, 103.155000, 105.690000, 103.655000, 104.000000, 105.530000, 108.530000, 108.750000, 107.750000,
        117.000000, 118.000000, 116.000000, 118.500000, 116.530000, 116.250000, 114.595000, 110.875000, 110.500000, 110.720000,
        112.620000, 114.190000, 111.190000, 109.440000, 111.560000, 112.440000, 117.500000, 116.060000, 116.560000, 113.310000,
        112.560000, 114.000000, 114.750000, 118.870000, 119.000000, 119.750000, 122.620000, 123.000000, 121.750000, 121.560000,
        123.120000, 122.190000, 122.750000, 124.370000, 128.000000, 129.500000, 130.810000, 130.630000, 132.130000, 133.880000,
        135.380000, 135.750000, 136.190000, 134.500000, 135.380000, 133.690000, 126.060000, 126.870000, 123.500000, 122.620000,
        122.750000, 123.560000, 125.810000, 124.620000, 124.370000, 121.810000, 118.190000, 118.060000, 117.560000, 121.000000,
        121.120000, 118.940000, 119.810000, 121.000000, 122.000000, 124.500000, 126.560000, 123.500000, 121.250000, 121.060000,
        122.310000, 121.000000, 120.870000, 122.060000, 122.750000, 122.690000, 122.870000, 125.500000, 124.250000, 128.000000,
        128.380000, 130.690000, 131.630000, 134.380000, 132.000000, 131.940000, 131.940000, 129.560000, 123.750000, 126.000000,
        126.250000, 124.370000, 121.440000, 120.440000, 121.370000, 121.690000, 120.000000, 119.620000, 115.500000, 116.750000,
        119.060000, 119.060000, 115.060000, 111.060000, 113.120000, 110.000000, 105.000000, 104.690000, 103.870000, 104.690000,
        105.440000, 107.000000, 89.000000, 92.500000, 92.120000, 94.620000, 92.810000, 94.250000, 96.250000, 96.370000,
        93.690000, 93.500000, 90.000000, 90.190000, 90.500000, 92.120000, 94.120000, 94.870000, 93.000000, 93.870000,
        93.000000, 92.620000, 93.560000, 98.370000, 104.440000, 106.000000, 101.810000, 104.120000, 103.370000, 102.120000,
        102.250000, 103.370000, 107.940000, 112.500000, 115.440000, 115.500000, 112.250000, 107.560000, 106.560000, 106.870000,
        104.500000, 105.750000, 108.620000, 107.750000, 108.060000, 108.000000, 108.190000, 108.120000, 109.060000, 108.750000,
        108.560000, 106.620000,
    ]
    EMBEDDED_INPUTS = {'INPUT_CLOSE': INPUT_CLOSE, 'INPUT_HIGH': INPUT_HIGH, 'INPUT_LOW': INPUT_LOW}
    # Demonstrate the default, using its declared reference input convention.
    default = MASTER_CLASS()
    for bar, close in enumerate(INPUT_CLOSE):
        if REFERENCE_INPUT == 'ohlc':
            last = default.update(close, INPUT_HIGH[bar], INPUT_LOW[bar])
        elif REFERENCE_INPUT == 'hl2':
            last = default.update((INPUT_HIGH[bar]+INPUT_LOW[bar])/2.0)
        else:
            last = default.update(close)
    heatmap = last.heatmap if hasattr(last, 'heatmap') else last
    print(f'{INDICATOR_SLUG}: 252 bars; {len(heatmap.values)} bins; first five={heatmap.values[:5]}')
    print(f'Confirmed cases={len(REFERENCE_CASES)}; confirmed={REFERENCE_CASES_CONFIRMED}')
    if args.generate_reference_data:
        generate_reference_data(Path(__file__).resolve().parent, EMBEDDED_INPUTS)
