"""Article expressions, independent EMA identity, RMS, startup, and fixtures.

The original article code is included in description.md for isolated-folder use.
All numeric and fixture validation uses Python's standard library.
"""
import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
ARTICLE = DIRECTORY.parent.parent / 'tasc/2016-07-the-super-passband-filter/content.md'
SPEC = importlib.util.spec_from_file_location('super_passband_master', DIRECTORY / 'super-passband-filter.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
FIXTURES = MASTER._read_arrays(DIRECTORY / 'test_testdata.py')
INPUT = FIXTURES['INPUT_CLOSE']


def article_block():
    source = ARTICLE.read_text() if ARTICLE.exists() else (DIRECTORY / 'description.md').read_text()
    section = source.split('## EasyLanguage Code for Super Passband Filter', 1)[1]
    return re.search(r'```easylanguage\s*\n(.*?)```', section, re.S).group(1)


def expression(block, name):
    return ' '.join(re.search(r'\b' + name + r'\s*=\s*(.*?);', block, re.S).group(1).split())


def article_batch(prices, period1, period2, rms_window):
    """Extract the actual PB formula and RMS loop, with declared master seeds."""
    block = article_block()
    parameters = dict(Period1=period1, Period2=period2)
    for name in ('a1', 'a2'):
        parameters[name] = eval(expression(block, name), {'__builtins__': {}}, parameters)
    formula = expression(block, 'PB')
    formula = formula.replace('Close[1]', 'price1').replace('PB[1]', 'pb1').replace('PB[2]', 'pb2')
    rms_step = re.search(r'RMS = RMS \+ (.*?);', block).group(1).replace('PB[count]', 'value')
    raw, outputs = [], []
    for i, price in enumerate(prices):
        if i == 0:
            pb = 0.0
        else:
            state = parameters | dict(Close=price, price1=prices[i-1],
                                      pb1=raw[-1], pb2=raw[-2] if i >= 2 else 0.0)
            pb = eval(formula, {'__builtins__': {}}, state)
        raw.append(pb)
        rms = math.nan
        if i + 1 >= max(2, rms_window):
            total = 0.0
            for lag in range(rms_window):
                total = total + eval(rms_step, {'__builtins__': {}}, {'value': raw[i-lag]})
            rms = math.sqrt(total / rms_window)
        outputs.append((pb if i >= 1 else math.nan, rms, -rms))
    return outputs, raw


def ema_difference(prices, period1, period2):
    """Independent two first-order EMAs, both seeded at the first actual price."""
    a1, a2 = 5 / period1, 5 / period2
    first = second = prices[0]
    outputs = [0.0]
    for price in prices[1:]:
        first = a1 * price + (1-a1) * first
        second = a2 * price + (1-a2) * second
        outputs.append(first-second)
    return outputs


def assert_series(test, actual, expected, tolerance=1e-11):
    test.assertEqual(len(actual), len(expected))
    for i, (a, e) in enumerate(zip(actual, expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a), f'bar {i+1}: expected NaN')
        else:
            test.assertTrue(math.isclose(a, e, abs_tol=tolerance, rel_tol=tolerance),
                            f'bar {i+1}: {a} versus {e}')


class SuperPassbandTests(unittest.TestCase):
    def test_all_confirmed_cases_against_article(self):
        self.assertEqual(len(INPUT), 252)
        self.assertEqual(len(MASTER.REFERENCE_CASES), 20)
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(parameters=MASTER._parameters(case)):
                expected, raw = article_batch(INPUT, **MASTER._parameters(case))
                indicator = MASTER.SuperPassbandFilter(**MASTER._parameters(case))
                outputs = [indicator.update(price) for price in INPUT]
                for i in range(3):
                    assert_series(self, [value[i] for value in outputs], [value[i] for value in expected])
                assert_series(self, raw, ema_difference(INPUT, case['period1'], case['period2']))

    def test_startup_and_each_output_availability(self):
        for window in (1, 2, 10, 50, 252, 300):
            indicator = MASTER.SuperPassbandFilter(rms_window=window)
            for i, price in enumerate(INPUT):
                output = indicator.update(price)
                self.assertEqual(indicator.is_passband_primed, i >= 1)
                self.assertEqual(indicator.is_primed, i >= max(1, window-1))
                self.assertEqual(math.isnan(output.passband), i == 0)
                self.assertEqual(math.isnan(output.rms), i < max(1, window-1))
                self.assertEqual(math.isnan(output.negative_rms), i < max(1, window-1))
            self.assertEqual(indicator.warmup_bars, max(1, window-1))
        indicator = MASTER.SuperPassbandFilter()
        self.assertTrue(all(math.isnan(x) for x in indicator.update(INPUT[0])))
        output = indicator.update(INPUT[1])
        self.assertAlmostEqual(output.passband, (5/40-5/60)*(INPUT[1]-INPUT[0]), delta=1e-14)
        self.assertTrue(math.isnan(output.rms))

    def test_rms_current_sample_window_and_summation_order(self):
        for window in (1, 2, 10, 50, 100, 252, 300):
            indicator = MASTER.SuperPassbandFilter(rms_window=window)
            raw = []
            for price in INPUT:
                output = indicator.update(price)
                raw.append(indicator._pb1)
                if indicator.is_primed:
                    total = 0.0
                    for value in reversed(raw[-window:]):
                        total = total + value*value
                    self.assertEqual(output.rms, math.sqrt(total/window))
                    self.assertEqual(output.negative_rms, -output.rms)
                    self.assertGreaterEqual(output.rms, 0)
                    if window == 1:
                        self.assertAlmostEqual(output.rms, abs(output.passband), delta=1e-15)

    def test_period_reversal_and_equal_periods(self):
        for p1, p2 in ((3, 4), (40, 60), (40.5, 60.5)):
            first = MASTER.SuperPassbandFilter(p1, p2)
            second = MASTER.SuperPassbandFilter(p2, p1)
            for price in INPUT:
                a, b = first.update(price), second.update(price)
                if first.is_passband_primed:
                    self.assertEqual(a.passband, -b.passband)
                if first.is_primed:
                    self.assertEqual(a.rms, b.rms)
        for period in (3, 5, 40, 40.5, 252):
            indicator = MASTER.SuperPassbandFilter(period, period, 1)
            for price in INPUT:
                output = indicator.update(price)
                if indicator.is_primed:
                    self.assertEqual(output, (0, 0, 0))

    def test_constant_step_and_ramp(self):
        indicator = MASTER.SuperPassbandFilter()
        outputs = [indicator.update(7) for _ in range(100)]
        assert_series(self, [x.passband for x in outputs[1:]], [0]*99)
        assert_series(self, [x.rms for x in outputs[49:]], [0]*51)
        indicator = MASTER.SuperPassbandFilter()
        values = [indicator.update(x).passband for x in [0]+[1]*100]
        q1, q2 = 1-5/40, 1-5/60
        assert_series(self, values[1:], [q2**n-q1**n for n in range(1,101)])
        rising = MASTER.SuperPassbandFilter()
        for price in range(1000):
            result = rising.update(price)
        # Unit-ramp difference equals the difference of EMA static lags.
        expected = (60-40)/5
        self.assertAlmostEqual(result.passband, expected, delta=1e-10)

    def test_frequency_response_including_nonzero_nyquist_gain(self):
        period1, period2 = 40, 60
        a1, a2 = 5/period1, 5/period2
        indicator = MASTER.SuperPassbandFilter(period1, period2)
        result = [indicator.update((-1.0)**i).passband for i in range(1000)]
        gain = a1/(2-a1)-a2/(2-a2)
        self.assertGreater(abs(gain), 0)
        for i in range(990,1000):
            self.assertAlmostEqual(result[i], gain*((-1.0)**i), delta=1e-14)

    def test_nan_skip_reset_and_configuration_validation(self):
        for case in MASTER.REFERENCE_CASES:
            first = MASTER.SuperPassbandFilter(**MASTER._parameters(case))
            second = MASTER.SuperPassbandFilter(**MASTER._parameters(case))
            for price in INPUT:
                old = vars(first).copy()
                old['_ring'] = first._ring.copy()
                self.assertTrue(all(math.isnan(x) for x in first.update(math.nan)))
                self.assertEqual(vars(first), old)
                assert_series(self, first.update(price), second.update(price), 1e-15)
            first.reset()
            second.reset()
            for price in INPUT:
                assert_series(self, first.update(price), second.update(price), 1e-15)
        for period in (0, -1, 1, 2.5, math.inf, -math.inf, math.nan):
            for name in ('period1', 'period2'):
                with self.assertRaises(ValueError):
                    MASTER.SuperPassbandFilter(**{name: period})
        for window in (0, -1, True, 1.0, 2.5, math.nan):
            with self.assertRaises(ValueError):
                MASTER.SuperPassbandFilter(rms_window=window)
        indicator = MASTER.SuperPassbandFilter()
        for invalid in (math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(invalid)
        self.assertEqual(indicator._count, 0)
        for name in ('period1', 'period2', 'rms_window'):
            with self.assertRaises(AttributeError):
                setattr(indicator, name, 10)

    def test_preserved_input_arrays_and_embedded_closes(self):
        tree = ast.parse((DIRECTORY / 'super-passband-filter.py').read_text())
        main = next(node for node in tree.body if isinstance(node, ast.If))
        self.assertEqual(ast.literal_eval(main.body[0].value), INPUT)
        for key in ('INPUT_CLOSE', 'INPUT_HIGH', 'INPUT_LOW', 'INPUT_OPEN'):
            self.assertEqual(len(FIXTURES[key]), 252)
        formats = (
            ('testdata_test.go', r'var test(\w+) = \[\]float64\{(.*?)\}'),
            ('testdata.ts', r'export const test(\w+): number\[\] = \[(.*?)\];'),
            ('testdata.rs', r'pub fn test_(\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]'),
            ('testdata.zig', r'pub fn test(\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\}'),
        )
        for filename, pattern in formats:
            sections = dict(re.findall(pattern, (DIRECTORY / filename).read_text(), re.S))
            self.assertEqual(len(sections), 4)
            for suffix, body in sections.items():
                key = 'INPUT_CLOSE' if suffix.lower() == 'input' else 'INPUT_' + suffix.upper()
                self.assertEqual([float(x.strip()) for x in body.split(',') if x.strip()], FIXTURES[key])

    def test_python_reference_precision(self):
        if not any(key.startswith('EXPECTED_') for key in FIXTURES):
            self.skipTest('expected fixtures have not yet been generated')
        self.assertEqual(len([key for key in FIXTURES if key.startswith('EXPECTED_')]), 60)
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.SuperPassbandFilter(**MASTER._parameters(case))
            outputs = [indicator.update(x) for x in INPUT]
            for field, token in zip(MASTER.OUTPUT_FIELDS, MASTER.OUTPUT_TOKENS):
                saved = FIXTURES['EXPECTED_' + MASTER._case_suffix(case) + '_' + token]
                self.assertEqual(len(saved), 252)
                for output, value in zip(outputs, saved):
                    actual = getattr(output, field)
                    if math.isnan(actual):
                        self.assertTrue(math.isnan(value))
                    else:
                        self.assertEqual(value, float(format(actual, '.15g')))

    def test_other_language_expected_values_and_comments(self):
        if not any(key.startswith('EXPECTED_') for key in FIXTURES):
            self.skipTest('expected fixtures have not yet been generated')
        formats = (
            ('testdata_test.go', r'var expected(\w+) = \[\]float64\{(.*?)\}', 'math.NaN()'),
            ('testdata.ts', r'export const expected(\w+): number\[\] = \[(.*?)\];', 'NaN'),
            ('testdata.rs', r'pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]', 'f64::NAN'),
            ('testdata.zig', r'pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\}', 'nan'),
        )
        for filename, pattern, nan in formats:
            text = (DIRECTORY / filename).read_text()
            sections = dict(re.findall(pattern, text, re.S))
            self.assertEqual(len(sections), 60)
            for case in MASTER.REFERENCE_CASES:
                for token in MASTER.OUTPUT_TOKENS:
                    suffix = MASTER._case_suffix(case) + '_' + token
                    key = suffix.lower() if filename.endswith('.rs') else suffix
                    tokens = [x.strip() for x in sections[key].split(',') if x.strip()]
                    self.assertEqual(tokens, [MASTER._literal(x, nan) for x in FIXTURES['EXPECTED_' + suffix]])
                    self.assertIn('// ' + case['what_it_tests'] + '\n// ' + MASTER._parameter_comment(case), text)


if __name__ == '__main__':
    unittest.main()
