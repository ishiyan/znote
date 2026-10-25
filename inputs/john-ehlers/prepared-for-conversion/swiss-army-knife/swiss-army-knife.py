"""Streaming master for Ehlers' January 2006 Swiss Army Knife indicator.

Nine executable modes share one recurrence. Article/MESA initialization is
preserved, including the price-seeded SMA's persistent offset. Mathematical
constants use full precision, including the two-pole cutoff factor 1+sqrt(2)
in place of printed 2.415. See description.md for equations/source differences.
The theoretical complex sliding DFT is omitted just as in the source code.
"""

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


FILTER_TYPES = ('EMA', 'SMA', 'Gauss', 'Butter', 'Smooth', 'HP', '2PHP', 'BP', 'BS')
TWO_POLE_FACTOR = 1.0 + math.sqrt(2.0)


class Parameters(NamedTuple):
    """N is both startup length and the SMA's averaging/delay length.

    Period is a frequency-coefficient period, not the usual EMA SMA-equivalent
    length. It is unused for SMA/Smooth; delta is used only by BP and BS.
    """

    filter_type: str = 'BP'
    n: int = 0
    period: float = 20.0
    delta: float = 0.1


class Coefficients(NamedTuple):
    """Exactly the article's shared recurrence coefficients, plus alpha.

    filtered = c0*(b0*x + b1*x[1] + b2*x[2])
               + a1*y[1] + a2*y[2] - c1*x[N].
    Feedback signs are already included in a1/a2. Alpha is diagnostic and
    is not a universally comparable smoothing parameter across modes.
    """

    c0: float
    c1: float
    b0: float
    b1: float
    b2: float
    a1: float
    a2: float
    alpha: float


class SwissArmyKnifeState(NamedTuple):
    """Owned diagnostic snapshot, including hidden startup assignments."""

    samples_seen: int
    filtered: float
    previous_filtered: float
    previous_inputs: tuple[float, ...]


def _integer(value, name, minimum):
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


def _coefficients(filter_type, n, period, delta):
    """Select one source coefficient set; do not blend or cascade modes.

    The defaults are the SOURCE CODE variable initializers, not the malformed
    'default' row in the MESA summary table. Configuration is fixed during a
    stream, so omitted coefficients cannot leak in from a different mode.
    """
    c0, c1, b0, b1, b2, a1, a2, alpha = 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0
    angle = 2.0 * math.pi / period
    if filter_type in ('EMA', 'HP'):
        # EL's Cosine(360/Period) becomes cos(2*pi/Period), using radians.
        alpha = (math.cos(angle) + math.sin(angle) - 1.0) / math.cos(angle)
        if filter_type == 'EMA':
            b0 = alpha
            a1 = 1.0 - alpha
        else:
            c0 = 1.0 - alpha / 2.0
            b1 = -1.0
            a1 = 1.0 - alpha
    elif filter_type == 'SMA':
        c1 = b0 = 1.0 / n
        a1 = 1.0
    elif filter_type in ('Gauss', 'Butter', '2PHP'):
        # 2.415 approximates the two-stage -3 dB factor 1/(sqrt(2)-1).
        # Restoring 1+sqrt(2) follows the user's full-precision requirement;
        # source-literal 2.415 outputs therefore differ slightly on these modes.
        beta = TWO_POLE_FACTOR * (1.0 - math.cos(angle))
        alpha = -beta + math.sqrt(beta * beta + 2.0 * beta)
        a1 = 2.0 * (1.0 - alpha)
        a2 = -(1.0 - alpha) * (1.0 - alpha)
        if filter_type == 'Gauss':
            c0 = alpha * alpha
        elif filter_type == 'Butter':
            c0 = alpha * alpha / 4.0
            b1, b2 = 2.0, 1.0
        else:
            c0 = (1.0 - alpha / 2.0) * (1.0 - alpha / 2.0)
            b1, b2 = -2.0, 1.0
    elif filter_type == 'Smooth':
        c0 = 1.0 / 4.0
        b1, b2 = 2.0, 1.0
    else:  # validated filter_type is BP or BS
        beta = math.cos(angle)
        # The printed prose uses 2*pi*delta/Period, but the executable article
        # and MESA code use 720 degrees = 4*pi. Preserve the CODE convention.
        gamma = 1.0 / math.cos(4.0 * math.pi * delta / period)
        alpha = gamma - math.sqrt(gamma * gamma - 1.0)
        a1, a2 = beta * (1.0 + alpha), -alpha
        if filter_type == 'BP':
            c0 = (1.0 - alpha) / 2.0
            b2 = -1.0
        else:
            c0 = (1.0 + alpha) / 2.0
            b1, b2 = -2.0 * beta, 1.0
    return Coefficients(c0, c1, b0, b1, b2, a1, a2, alpha)


class SwissArmyKnife:
    """Standard-library, bounded-state master for all nine source-code modes.

    Default is BP, N=0, Period=20, delta=0.1 (from the complete MESA code).
    SMA requires explicit N>=1. All other modes allow N>=0. Period is a finite
    real >4; delta lies in [0.05,0.5]. These conservative domains avoid cosine
    singularities and retain the source's recommended band-width region.

    The source plots ONLY when CurrentBar>N. Before then, price seeds EMA,
    SMA, Gauss, Butter, BP and BS; HP/2PHP seed zero; Smooth keeps its initialized
    zero. Hidden seeds are inserted into output history, while input history
    advances normally. This makes N independent from Period for non-SMA modes.
    """

    def __init__(self, filter_type='BP', n=0, period=20.0, delta=0.1):
        if not isinstance(filter_type, str) or filter_type not in FILTER_TYPES:
            raise ValueError(f'filter_type must be one of {FILTER_TYPES}; source code omits DFT')
        length = _integer(n, 'n', 0)
        if filter_type == 'SMA' and length == 0:
            raise ValueError('SMA requires n>=1; the source default N=0 divides by zero')
        frequency_period = _real(period, 'period')
        if frequency_period <= 4.0:
            raise ValueError('period must exceed 4 bars')
        width = _real(delta, 'delta')
        if not 0.05 <= width <= 0.5:
            raise ValueError('delta must be in [0.05, 0.5]')
        self.parameters = Parameters(filter_type, length, frequency_period, width)
        self.coefficients = _coefficients(filter_type, length, frequency_period, width)
        self.warmup_bars = length  # exact article Plot1 gate, not IIR settling
        self.reset()

    def reset(self):
        """Restore source zero prehistory and retain the chosen coefficients."""
        self.samples_seen = 0
        # Before update this holds input[1]..input[max(N,2)], newest first.
        # N=0 means input[N] is the CURRENT input, not the last element here.
        self._inputs = [0.0] * max(self.parameters.n, 2)
        self._filtered = self._previous_filtered = 0.0
        self.output = math.nan

    @property
    def is_primed(self):
        return self.samples_seen > self.warmup_bars

    @property
    def state(self):
        return SwissArmyKnifeState(self.samples_seen, self._filtered,
                                   self._previous_filtered, tuple(self._inputs))

    def update(self, value):
        """Consume one price and return the scalar Filt, or NaN during priming.

        NaN observations are skipped without changing state/count/last output.
        Invalid types, infinity and non-finite candidate arithmetic raise
        ValueError atomically. NaN outputs never enter the recurrence history.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('input must be a real number; NaN may mark missing data')
        try:
            price = float(value)
        except (ValueError, OverflowError) as error:
            raise ValueError('input cannot be represented as a float') from error
        if math.isnan(price):
            return math.nan
        if not math.isfinite(price):
            raise ValueError('input must not be infinite')
        p, c = self.parameters, self.coefficients
        bar = self.samples_seen + 1  # EasyLanguage CurrentBar is one-based.
        if bar <= p.n:
            if p.filter_type in ('HP', '2PHP'):
                filtered = 0.0
            elif p.filter_type == 'Smooth':
                # Smooth has NO startup assignment in the article. The
                # initialized Filt is retained while the common gate is shut.
                filtered = self._filtered
            else:
                filtered = price
        else:
            delayed = price if p.n == 0 else self._inputs[p.n - 1]
            # One shared recurrence, in source summation order. Do not negate
            # a2 again or move the delayed input subtraction outside feedback.
            filtered = (c.c0 * (c.b0 * price + c.b1 * self._inputs[0]
                                + c.b2 * self._inputs[1])
                        + c.a1 * self._filtered + c.a2 * self._previous_filtered
                        - c.c1 * delayed)
        if not math.isfinite(filtered):
            raise ValueError('input causes non-finite filter arithmetic; state was not changed')
        # Commit both price and hidden/visible filtered histories after the
        # candidate succeeds. Seeding is essential for later IIR behavior.
        self._inputs = [price] + self._inputs[:-1]
        self._previous_filtered, self._filtered = self._filtered, filtered
        self.samples_seen = bar
        self.output = filtered if self.is_primed else math.nan
        return self.output


# Everything below is fixture tooling, separate from the recurrence to port.
INDICATOR_SLUG = 'swiss-army-knife'
MASTER_CLASS = SwissArmyKnife
REFERENCE_INPUT = 'close'
PARAMETER_SHORTCUTS = {'filter_type': 'T', 'n': 'N', 'period': 'P', 'delta': 'D'}
REFERENCE_CASES_CONFIRMED = True


def _case(filter_type, n=0, period=20.0, delta=0.1, what=''):
    return dict(filter_type=filter_type, n=n, period=period, delta=delta, what_it_tests=what)


REFERENCE_CASES = tuple(
    [_case(mode, n=20 if mode == 'SMA' else 0,
           what=f'{mode} coefficient set at default period') for mode in FILTER_TYPES]
    + [_case(mode, period=period, what=f'{label}: {mode}')
       for period, label in ((5.0, 'Short-cycle coefficients'),
                             (50.0, 'Slow poles and longer transients'))
       for mode in ('EMA', 'Gauss', 'Butter', 'HP', '2PHP', 'BP', 'BS')]
    + [_case(mode, delta=delta, what=f'{label}: {mode}')
       for delta, label in ((0.05, 'Narrow resonator'), (0.5, 'Wide resonator'))
       for mode in ('BP', 'BS')]
    + [_case('SMA', n=n, what=what) for n, what in (
        (1, 'SMA minimum length'), (5, 'SMA startup bias'),
        (251, 'SMA first valid output at final input'), (252, 'SMA fully unprimed record'))]
    + [_case(mode, n=5, what=what) for mode, what in (
        ('Gauss', 'Price-seeded two-pole startup'), ('HP', 'Zero-seeded high-pass startup'),
        ('BP', 'Price-seeded resonator startup'), ('Smooth', 'Delayed three-tap FIR startup'))]
    + [_case('BP', period=20.5, what='Fractional coefficient period')]
)


def _parameter_token(value):
    if isinstance(value, str):
        return value.upper()
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
    # A single output needs no component suffix in its expected array name.
    return {'': [indicator.update(close) for close in inputs['INPUT_CLOSE']]}


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
            name = 'EXPECTED_'+_case_suffix(case)+('_'+component if component else '')
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
        matrix = isinstance(raw[0], list)
        bins = len(raw[0]) if matrix else 0
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
        bins = len(values[0]) if matrix else 0
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
        indicator = SwissArmyKnife()  # default BP, N=0, Period=20, delta=0.1
        results = [indicator.update(price) for price in INPUT_CLOSE]
        print(f'{len(results)} closes; first valid bar={indicator.warmup_bars + 1}')
        print('Default BP final output:', results[-1])
        print('Coefficients:', indicator.coefficients)
        print(f'{len(REFERENCE_CASES)} reference cases; confirmed={REFERENCE_CASES_CONFIRMED}')
