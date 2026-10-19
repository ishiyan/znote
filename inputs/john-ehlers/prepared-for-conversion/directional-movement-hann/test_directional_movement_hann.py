"""Independent source-expression and analytical checks of the DMH master.

These use the supplied primary EasyLanguage expressions with batch histories,
plus hand-calculated edge cases. No test requires third-party Python packages.
"""

import ast
import cmath
import contextlib
import importlib.util
import io
import math
from pathlib import Path
import re
import tempfile
import unittest

DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('dmh_master', DIRECTORY / 'directional-movement-hann.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
HIGH, LOW = INPUTS['INPUT_HIGH'], INPUTS['INPUT_LOW']
SOURCE = (DIRECTORY.parent.parent / 'tasc/2021-12-the-dmh-an-improved-directional-movement-indicator/tips/code/DMH.els').read_text()


def assignment(name):
    """Read the first assignment to a source variable, excluding declarations."""
    match = re.search(r'\b' + name + r'\s*=\s*(.*?);', SOURCE, re.DOTALL)
    return ' '.join(match.group(1).split())


def source_batch(highs, lows, length):
    """Evaluate supplied expressions against chronological batch EMA history.

    First bar supplies prior prices, with EMA seed zero. There is no padded
    EMA observation at that bar. The published code relies on platform history;
    this master explicitly masks output until all required actual bars exist.
    """
    functions = {'Cosine': lambda angle: math.cos(math.radians(angle))}
    environment = {'Length': length}
    environment['SF'] = eval(assignment('SF'), {'__builtins__': {}}, environment)
    upper_condition = re.search(r'if (.*?) then\s+PlusDM', SOURCE, re.DOTALL).group(1)
    lower_condition = re.search(r'else if (.*?) then\s+MinusDM', SOURCE, re.DOTALL).group(1)
    upper_condition = ' '.join(upper_condition.split())
    lower_condition = ' '.join(lower_condition.split())
    # The first DMSum assignment is the reset; find the actual accumulation.
    numerator = ' '.join(re.search(r'DMSum = DMSum \+ (.*?);', SOURCE, re.DOTALL).group(0).split())
    numerator = numerator.split('=', 1)[1].rstrip(';').strip().replace('EMA[count - 1]', 'tap')
    coefficient_expression = ' '.join(re.search(r'coef = coef \+ (.*?);', SOURCE, re.DOTALL).group(1).split())
    ema_expression = assignment('EMA').replace('EMA[1]', 'previous_ema')
    ema_history = [0.0]  # Seed at index zero; never used as a Hann sample.
    output, details = [math.nan], [None]
    for t in range(1, len(highs)):
        env = environment | functions | {
            'High': highs[t], 'previous_high': highs[t-1],
            'Low': lows[t], 'previous_low': lows[t-1],
        }
        env['UpperMove'] = eval(assignment('UpperMove').replace('High[1]', 'previous_high'), {'__builtins__': {}}, env)
        env['LowerMove'] = eval(assignment('LowerMove').replace('Low[1]', 'previous_low'), {'__builtins__': {}}, env)
        env['PlusDM'] = env['MinusDM'] = 0.0
        if eval(upper_condition, {'__builtins__': {}}, env):
            env['PlusDM'] = env['UpperMove']
        elif eval(lower_condition, {'__builtins__': {}}, env):
            env['MinusDM'] = env['LowerMove']
        env['previous_ema'] = ema_history[-1]
        ema = eval(ema_expression, {'__builtins__': {}}, env)
        ema_history.append(ema)
        dmh = math.nan
        if t >= length:
            env['DMSum'] = env['coef'] = 0.0
            for count in range(1, length+1):
                env['count'] = count
                env['tap'] = ema_history[t-count+1]
                env['DMSum'] = eval(numerator, {'__builtins__': {}}, env)
                env['coef'] += eval(coefficient_expression, {'__builtins__': {}}, env)
            dmh = eval(assignment('DMH'), {'__builtins__': {}}, env)
        output.append(dmh)
        details.append((env['UpperMove'], env['LowerMove'], env['PlusDM'], env['MinusDM'], ema, dmh))
    return output, details


def compare(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for t, (a, b) in enumerate(zip(actual, expected)):
        if math.isnan(b):
            test.assertTrue(math.isnan(a), (t, a, b))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance), (t, a, b))


class DirectionalMovementHannTests(unittest.TestCase):
    def test_all_confirmed_cases_match_supplied_source_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            expected, details = source_batch(HIGH, LOW, case.length)
            indicator = MASTER.DirectionalMovementHann(case.length)
            actual = []
            for t, (high, low) in enumerate(zip(HIGH, LOW)):
                actual.append(indicator.update(high, low))
                if t > 0:
                    compare(self, indicator.state, details[t], 0)
            compare(self, actual, expected, 0)

    def test_history_availability_including_singleton_and_record_boundary(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.DirectionalMovementHann(case.length)
            self.assertEqual(indicator.warmup_bars, case.length)
            for t, (high, low) in enumerate(zip(HIGH, LOW)):
                value = indicator.update(high, low)
                self.assertEqual(indicator.is_primed, t >= case.length)
                self.assertEqual(math.isnan(value), t < case.length)
                self.assertEqual(len(indicator._emas), min(t, case.length))
                self.assertTrue(math.isfinite(indicator.state.ema))
        long = MASTER.DirectionalMovementHann(252)
        self.assertTrue(all(math.isnan(long.update(h, l)) for h, l in zip(HIGH, LOW)))
        self.assertTrue(math.isfinite(long.update(HIGH[-1], LOW[-1])))

    def test_direction_selection_ties_inside_outside_and_flat_bars(self):
        # Each pair starts from the same previous bar H=10, L=5.
        cases = ((12, 6, 2, 0), (9, 3, 0, 2), (9, 6, 0, 0),
                 (10, 5, 0, 0), (12, 3, 0, 0), (13, 3, 3, 0),
                 (12, 2, 0, 3), (11, 5, 1, 0), (10, 4, 0, 1))
        for high, low, plus, minus in cases:
            indicator = MASTER.DirectionalMovementHann(1)
            self.assertTrue(math.isnan(indicator.update(10, 5)))
            self.assertEqual(indicator.update(high, low), plus-minus)
            self.assertEqual(indicator.state.plus_dm, plus)
            self.assertEqual(indicator.state.minus_dm, minus)
        # Close is not read: High/Low movement remains possible with flat Close.
        indicator = MASTER.DirectionalMovementHann(1)
        indicator.update(10, 5)
        self.assertEqual(indicator.update(12, 4), 2)

    def test_zero_seed_wilder_alpha_and_sparse_impulse_decay(self):
        n = 14
        indicator = MASTER.DirectionalMovementHann(n)
        self.assertEqual(indicator.state.ema, 0)
        indicator.update(10, 5)
        self.assertEqual(indicator.state.ema, 0)
        indicator.update(24, 5)  # A single positive signed movement of 14.
        self.assertEqual(indicator.state.ema, 1)
        self.assertNotEqual(indicator.state.ema, 2*14/(n+1))
        for t in range(2, 100):
            indicator.update(24, 5)
            self.assertAlmostEqual(indicator.state.ema, (1-1/n)**(t-1), places=14)
        # No SMA seeding or waiting N bars before beginning the EMA recurrence.
        short = MASTER.DirectionalMovementHann(2)
        short.update(10, 5)
        self.assertTrue(math.isnan(short.update(12, 5)))
        self.assertEqual(short.state.ema, 1)
        self.assertAlmostEqual(short.update(12, 5), 0.75, places=14)

    def test_interior_hann_weights_normalization_symmetry_and_delay(self):
        for n in (1, 2, 3, 14, 126, 252):
            weights, coefficient = MASTER.DirectionalMovementHann._kernel(n)
            self.assertEqual(len(weights), n)
            self.assertGreater(weights[0], 0)
            self.assertGreater(weights[-1], 0)
            self.assertAlmostEqual(coefficient, n+1, places=11)
            for a, b in zip(weights, reversed(weights)):
                self.assertAlmostEqual(a, b, places=13)
            self.assertAlmostEqual(sum(k*w for k,w in enumerate(weights))/coefficient, (n-1)/2, places=12)
        self.assertEqual(MASTER.DirectionalMovementHann._kernel(1), ([2.0], 2.0))

    def test_flat_prices_and_constant_signed_movement_closed_form(self):
        flat = MASTER.DirectionalMovementHann()
        for t in range(100):
            value = flat.update(42, 40)
            self.assertEqual(flat.state.ema, 0)
            if t >= 14: self.assertEqual(value, 0)
        for n in (1, 3, 14):
            for direction in (-1, 1):
                indicator = MASTER.DirectionalMovementHann(n)
                for t in range(300):
                    value = indicator.update(100+direction*2*t, 90+direction*2*t)
                    expected_ema = direction*2*(1-(1-1/n)**t)
                    self.assertAlmostEqual(indicator.state.ema, expected_ema, places=13)
                    if t >= n:
                        weights = [2*math.sin(math.pi*c/(n+1))**2 for c in range(1,n+1)]
                        expected = sum(w*direction*2*(1-(1-1/n)**(t-lag)) for lag,w in enumerate(weights))/(n+1)
                        self.assertAlmostEqual(value, expected, places=13)

    def test_translation_positive_scaling_and_price_reflection(self):
        reference = MASTER.DirectionalMovementHann()
        outputs = [reference.update(h,l) for h,l in zip(HIGH,LOW)]
        for offset, factor in ((1000, 1), (0, 8)):
            shifted = MASTER.DirectionalMovementHann()
            compare(self, [shifted.update(offset+factor*h, offset+factor*l) for h,l in zip(HIGH,LOW)],
                    [factor*v for v in outputs])
        reflected = MASTER.DirectionalMovementHann()
        compare(self, [reflected.update(-l,-h) for h,l in zip(HIGH,LOW)], [-v for v in outputs], 0)

    def test_cascade_frequency_response_for_signed_movement_input(self):
        # Raise highs only on positive movement and lower lows only on
        # negative movement: this realizes an exact signed sinusoidal input
        # without invoking a nonexistent linear price-to-DM transfer function.
        n, omega = 8, 2*math.pi/30
        alpha = 1/n
        weights = [2*math.sin(math.pi*c/(n+1))**2 for c in range(1,n+1)]
        fir = sum(w*cmath.exp(-1j*omega*k) for k,w in enumerate(weights))/(n+1)
        gain = alpha/(1-(1-alpha)*cmath.exp(-1j*omega))*fir
        indicator = MASTER.DirectionalMovementHann(n)
        high, low = 100.0, 0.0
        indicator.update(high, low)
        for t in range(1, 600):
            movement = math.sin(omega*t)
            if movement > 0: high += movement
            else: low += movement
            output = indicator.update(high, low)
            if t > 400:
                self.assertAlmostEqual(output, (gain*cmath.exp(1j*omega*t)).imag, places=12)

    def test_reset_causality_validation_and_rejected_bar_state(self):
        a, b = MASTER.DirectionalMovementHann(), MASTER.DirectionalMovementHann()
        outputs = [a.update(h,l) for h,l in zip(HIGH,LOW)]
        compare(self, [b.update(h,l) for h,l in zip(HIGH[:100],LOW[:100])], outputs[:100], 0)
        a.reset()
        self.assertFalse(a.is_primed)
        compare(self, [a.update(h,l) for h,l in zip(HIGH,LOW)], outputs, 0)
        a.reset()
        b.reset()
        for h,l in zip(HIGH[:100],LOW[:100]):
            a.update(h,l)
            b.update(h,l)
        for h,l in ((math.nan,1), (1,math.nan), (math.inf,1), (1,-math.inf), (1,2)):
            old = (a.state, a._previous_high, a._previous_low, a._emas[:])
            with self.assertRaises(ValueError): a.update(h,l)
            self.assertEqual((a.state, a._previous_high, a._previous_low, a._emas), old)
        compare(self, [a.update(h,l) for h,l in zip(HIGH[100:],LOW[100:])],
                [b.update(h,l) for h,l in zip(HIGH[100:],LOW[100:])], 0)
        for n in (0, -1, True, 14.0, 1.5, math.nan, math.inf):
            with self.assertRaises(ValueError): MASTER.DirectionalMovementHann(n)
        # Finite inputs can still overflow a subtraction; rejection is atomic.
        huge = MASTER.DirectionalMovementHann(1)
        huge.update(-1e308, -1e308)
        with self.assertRaises(ValueError): huge.update(1e308, 1e308)
        self.assertEqual(huge._previous_high, -1e308)

    def test_all_copied_inputs_and_three_embedded_arrays_are_preserved(self):
        parent = MASTER._load_literal_arrays(DIRECTORY.parent / 'test_testdata.py')
        for name, values in parent.items():
            if name.startswith('INPUT_'):
                self.assertEqual(INPUTS[name], values)
                self.assertEqual(len(values), 252)
        module = ast.parse((DIRECTORY / 'directional-movement-hann.py').read_text())
        main = next(node for node in module.body if isinstance(node, ast.If))
        for name in ('INPUT_CLOSE', 'INPUT_HIGH', 'INPUT_LOW'):
            embedded = next(node for node in main.body if isinstance(node, ast.Assign) and
                            any(isinstance(t, ast.Name) and t.id == name for t in node.targets))
            self.assertEqual(ast.literal_eval(embedded.value), INPUTS[name])
        for name in ('testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig'):
            copied = (DIRECTORY/name).read_text().split('// BEGIN GENERATED', 1)[0].rstrip()
            original = (DIRECTORY.parent/name).read_text().rstrip()
            if name.endswith('.go'):
                copied = copied.replace('package directionalmovementhann\n\nimport "math"\n', 'package xxxx\n', 1)
            self.assertEqual(copied, original)

    def test_all_five_expected_fixtures_match_source_values_comments_and_warmup(self):
        arrays = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
        names = {MASTER._expected_name(case, 'dmh') for case in MASTER.REFERENCE_CASES}
        self.assertEqual({name for name in arrays if name.startswith('EXPECTED_')}, names)
        patterns = {
            'testdata_test.go': r'var (expected\w+) = \[\]float64\{(.*?)\n\}',
            'testdata.ts': r'export const (expected\w+): number\[\] = \[(.*?)\n\];',
            'testdata.rs': r'pub fn (expected_\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\n    \]',
            'testdata.zig': r'pub fn (expected\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\n    \};',
        }
        texts = {name: (DIRECTORY/name).read_text() for name in patterns}
        translated = {name: dict(re.findall(pattern, texts[name], re.DOTALL))
                      for name, pattern in patterns.items()}
        python_text = (DIRECTORY/'test_testdata.py').read_text()
        for filename, data in translated.items():
            target_names = {'expected_' + n.removeprefix('EXPECTED_').lower() if filename.endswith('.rs')
                            else 'expected' + n.removeprefix('EXPECTED_') for n in names}
            self.assertEqual(set(data), target_names)
        for case in MASTER.REFERENCE_CASES:
            name = MASTER._expected_name(case, 'dmh')
            values = arrays[name]
            expected, _ = source_batch(HIGH, LOW, case.length)
            compare(self, values, expected, 5e-14)
            self.assertEqual(len(values), 252)
            self.assertTrue(all(math.isnan(v) for v in values[:case.length]))
            self.assertTrue(all(math.isfinite(v) for v in values[case.length:]))
            self.assertIn(f'# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\n{name}', python_text)
            suffix = name.removeprefix('EXPECTED_')
            for filename, data in translated.items():
                target = 'expected_' + suffix.lower() if filename.endswith('.rs') else 'expected' + suffix
                literals = [v.strip() for v in data[target].split(',') if v.strip()]
                floats = [math.nan if v in ('math.NaN()', 'NaN', 'f64::NAN', 'nan') else float(v)
                          for v in literals]
                compare(self, floats, values, 0)
                declaration = ('pub fn ' if filename.endswith(('.rs', '.zig')) else
                               'export const ' if filename.endswith('.ts') else 'var ')
                self.assertIn(f'// {case.what_it_tests}\n// {MASTER._parameter_comment(case)}\n'
                              + declaration + target, texts[filename])
        self.assertEqual(sum(math.isfinite(v) for v in arrays['EXPECTED_L251']), 1)
        self.assertTrue(all(math.isnan(v) for v in arrays['EXPECTED_L252']))
        self.assertIn('import "math"', texts['testdata_test.go'])
        self.assertIn('const math = @import("std").math;', texts['testdata.zig'])
        self.assertIn('const nan = math.nan(f64);', texts['testdata.zig'])

    def test_regeneration_is_identical_and_preserves_all_input_text(self):
        filenames = ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')
        before = {name: (DIRECTORY/name).read_bytes() for name in filenames}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name, data in before.items():
                (target/name).write_bytes(data)
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(INPUTS['INPUT_CLOSE'], HIGH, LOW, target)
                MASTER.generate_reference_data(INPUTS['INPUT_CLOSE'], HIGH, LOW, target)
            self.assertEqual(before, {name: (target/name).read_bytes() for name in filenames})
        for name in filenames:
            marker = '# BEGIN GENERATED' if name.endswith('.py') else '// BEGIN GENERATED'
            prefix = (DIRECTORY/name).read_text().split(marker, 1)[0].rstrip()
            if name.endswith('.go'):
                prefix = prefix.replace('package directionalmovementhann\n\nimport "math"\n',
                                        'package xxxx\n', 1)
            self.assertEqual(prefix, (DIRECTORY.parent/name).read_text().rstrip())

    def test_portable_names_parameter_comments_and_numeric_rendering(self):
        self.assertTrue(1 <= len(MASTER.REFERENCE_CASES) <= 64)
        self.assertEqual(len({c.length for c in MASTER.REFERENCE_CASES}), len(MASTER.REFERENCE_CASES))
        for case in MASTER.REFERENCE_CASES:
            self.assertEqual(MASTER._expected_name(case, 'dmh'), f'EXPECTED_L{case.length}')
            self.assertEqual(MASTER._parameter_comment(case), f'length={case.length}')
        self.assertEqual(MASTER._float_literal(math.nan, 'NaN'), 'NaN')
        self.assertEqual(MASTER._float_literal(1.2345678901234567, 'NaN'), '1.23456789012346')
        self.assertEqual(MASTER._float_literal(0, 'NaN'), '0.0')
        with self.assertRaises(ValueError): MASTER._float_literal(math.inf, 'NaN')


if __name__ == '__main__':
    unittest.main()
