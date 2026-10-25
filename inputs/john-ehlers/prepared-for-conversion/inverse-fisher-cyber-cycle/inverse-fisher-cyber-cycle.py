"""May 2004 Inverse Fisher Cyber Cycle, streaming research master reference.

The article, MESA paper and TradeStation tip share this exact Cyber Cycle
recurrence. Only standard Python is used. See description.md before porting:
the first SIX bars use raw-price second-difference seeds; Smooth still advances
on every bar; only the untransformed Cycle enters feedback. No RSI, extra WMA,
normalization, gain parameter or delayed trigger belongs to this indicator.

The source plots from its first bar. This standalone reference likewise uses
zero prehistory and returns a scalar from the FIRST accepted input. There is
no artificial warmup NaN mask. All twelve alpha cases are user-confirmed;
generation exports five-language fixtures from the 252 embedded shared closes.
"""

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


STARTUP_LAST_BAR = 6  # Source: if CurrentBar < 7, override Cycle.


class Coefficients(NamedTuple):
    """Fixed Cyber Cycle coefficients; feedback2 is SUBTRACTED, not added."""

    feedforward: float
    feedback1: float
    feedback2: float


class InverseFisherCyberCycleState(NamedTuple):
    """Owned diagnostics; all price and untransformed Cycle histories matter."""

    samples_seen: int
    previous_prices: tuple[float, float, float]
    smooth: float
    previous_smooth: float
    cycle: float
    previous_cycle: float
    transformed: float


def _alpha(value):
    """Validate the conventional nonnegative-pole Cyber Cycle domain.

    The source has no validation. 0<alpha<=1 gives 0<=pole<1, with alpha=1
    a valid memoryless second-difference boundary. Smaller positive values
    produce longer decay. Tiny values that round 1-alpha to 1 are rejected.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('alpha must be a finite real number in (0, 1]')
    try:
        number = float(value)
    except (ValueError, OverflowError) as error:
        raise ValueError('alpha must be a finite real number in (0, 1]') from error
    if not math.isfinite(number) or not 0.0 < number <= 1.0:
        raise ValueError('alpha must be a finite real number in (0, 1]')
    if 1.0 - number == 1.0:
        raise ValueError('alpha must produce a representable pole below one')
    return number


def inverse_fisher(cycle):
    """Article's (exp(2*Cycle)-1)/(exp(2*Cycle)+1), with safe saturation.

    Keep the literal exponential quotient on the ordinary source domain so
    its decimal rounding matches the article. tanh(Cycle) is mathematically
    equal but can differ in the last bits, especially close to zero.

    Beyond +/-350 the result is already indistinguishable from +/-1 in
    binary64. Return that limit BEFORE doubling or exponentiating, avoiding
    overflow for very large finite Cycle. This is a documented arithmetic
    extension of the source, which can otherwise form infinity/infinity.
    """
    if not math.isfinite(cycle):
        raise ValueError('Cycle must be finite before inverse Fisher transformation')
    if cycle > 350.0:
        return 1.0
    if cycle < -350.0:
        return -1.0
    exponential = math.exp(2.0*cycle)
    return (exponential - 1.0) / (exponential + 1.0)


class InverseFisherCyberCycle:
    """Standard-library streaming ICycle, default source alpha=0.07.

    update accepts the selected scalar price. The article defaults to (H+L)/2;
    the required reference fixtures use INPUT_CLOSE, selected by the caller.
    All absent price/Smooth/Cycle lags begin at zero. Startup Cycle assignments
    are real output values and enter later recursive history. Public NaNs are
    used only for omitted NaN observations, never as hidden feedback values.
    """

    def __init__(self, alpha=0.07):
        self._alpha = _alpha(alpha)
        pole = 1.0 - self._alpha
        self.coefficients = Coefficients(
            (1.0 - 0.5*self._alpha)*(1.0 - 0.5*self._alpha),
            2.0*pole, pole*pole)
        self.reset()

    @property
    def alpha(self):
        """Fixed source parameter; not an automatically estimated cycle period."""
        return self._alpha

    @property
    def warmup_bars(self):
        # Plot1 is unconditional in the source; its seed bars are not suppressed.
        return 0

    @property
    def is_primed(self):
        return self.samples_seen > 0

    @property
    def uses_recursive_cycle(self):
        """False during the six source seed bars; distinct from public priming."""
        return self.samples_seen > STARTUP_LAST_BAR

    @property
    def state(self):
        return InverseFisherCyberCycleState(
            self.samples_seen, tuple(self._prices), self._smooth,
            self._previous_smooth, self._cycle, self._previous_cycle, self.output)

    def reset(self):
        """Restore zero prehistory and restart CurrentBar at one next update."""
        self.samples_seen = 0
        # Prior raw Price[1], Price[2], Price[3], newest first.
        self._prices = [0.0, 0.0, 0.0]
        self._smooth = self._previous_smooth = 0.0
        self._cycle = self._previous_cycle = 0.0
        self.output = math.nan

    def update(self, value):
        """Consume one price and return the scalar transformed Cycle.

        NaN skips the observation without advancing state/count/last output.
        Invalid types, booleans, infinity and non-finite filter arithmetic raise
        ValueError before committing any state. This explicit input contract
        supplements the source, which assumes ordinary finite chart prices.
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

        # All arithmetic uses OLD histories. The smoother is evaluated even
        # during source startup, so its bar-5/6 values exist for bar-7 recursion.
        bar = self.samples_seen + 1
        smooth = (price + 2.0*self._prices[0] + 2.0*self._prices[1]
                  + self._prices[2]) / 6.0
        if not math.isfinite(smooth):
            raise ValueError('non-finite Smooth arithmetic; state was not changed')
        if bar <= STARTUP_LAST_BAR:
            # Source computes recursive Cycle and then overrides it on these
            # bars. Compute the surviving assignment directly; the discarded
            # candidate has no side effects and must not enter feedback.
            cycle = (price - 2.0*self._prices[0] + self._prices[1]) / 4.0
        else:
            c = self.coefficients
            cycle = (c.feedforward*(smooth - 2.0*self._smooth + self._previous_smooth)
                     + c.feedback1*self._cycle - c.feedback2*self._previous_cycle)
        if not math.isfinite(cycle):
            raise ValueError('non-finite Cycle arithmetic; state was not changed')
        transformed = inverse_fisher(cycle)

        # Commit only after the output succeeds. ICycle is a display transform;
        # NEVER feed it back in place of the raw price-unit Cycle histories.
        self._prices = [price, self._prices[0], self._prices[1]]
        self._previous_smooth, self._smooth = self._smooth, smooth
        self._previous_cycle, self._cycle = self._cycle, cycle
        self.samples_seen = bar
        self.output = transformed
        return transformed


# Everything below is fixture tooling, separate from the recurrence to port.
INDICATOR_SLUG = 'inverse-fisher-cyber-cycle'
MASTER_CLASS = InverseFisherCyberCycle
REFERENCE_INPUT = 'close'
PARAMETER_SHORTCUTS = {'alpha': 'A'}
# The user explicitly confirmed all twelve alpha values on 2026-10-25.
# This authorizes generation and regeneration of these same reference cases.
REFERENCE_CASES_CONFIRMED = True


REFERENCE_CASES = tuple(dict(alpha=alpha, what_it_tests=what)
                        for alpha, what in (
    (0.001, 'Very slow pole decay and a transient longer than the record'),
    (0.005, 'Slow decay with long untransformed Cycle memory'),
    (0.01, 'Low-alpha filtering and sustained inverse Fisher saturation'),
    (0.03, 'Slower Cycle response than the article default'),
    (0.05, 'Moderately slow filtering near the default'),
    (0.07, 'Article MESA and TradeStation default alpha'),
    (0.1, 'Faster decay than the article default'),
    (0.15, 'Intermediate short-memory Cycle response'),
    (0.25, 'Reduced recursive memory and weaker cycle amplitudes'),
    (0.5, 'Short recursive memory with a pole of one half'),
    (0.9, 'Near-memoryless filtering and small recursive contribution'),
    (1.0, 'Valid memoryless boundary; zero feedback coefficients'),
))


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
    # The shared input fixture's package declaration can follow a file comment.
    # Find its declaration line explicitly instead of assuming it is first or
    # already has the indicator package name. Add math for generated NaNs.
    go_path = directory/'testdata_test.go'
    text = go_path.read_text(encoding='utf-8')
    package = INDICATOR_SLUG.replace('-', '').replace('_', '')
    lines = text.splitlines(keepends=True)
    declarations = [index for index, line in enumerate(lines)
                    if line.startswith('package ')]
    if len(declarations) != 1:
        raise ValueError('expected exactly one Go package declaration')
    lines[declarations[0]] = f'package {package}\n'
    text = ''.join(lines)
    if 'import "math"' not in text:
        text = text.replace(f'package {package}\n', f'package {package}\n\nimport "math"\n', 1)
    # This source has no warmup NaNs. Keep math available for the requested
    # fixture NaN convention without an unused Go import or a fake data value.
    if 'var _ = math.NaN' not in text:
        text = text.replace('import "math"\n', 'import "math"\n\nvar _ = math.NaN\n', 1)
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
        indicator = InverseFisherCyberCycle()  # article alpha=0.07
        results = [indicator.update(price) for price in INPUT_CLOSE]
        print(f'{len(results)} closes; first valid bar={indicator.warmup_bars + 1}')
        print('Default inverse Fisher Cycle final output:', results[-1])
        print('Raw Cycle:', indicator.state.cycle, 'alpha:', indicator.alpha)
        print(f'{len(REFERENCE_CASES)} reference cases; confirmed={REFERENCE_CASES_CONFIRMED}')
