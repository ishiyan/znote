"""Source-equation, transform-invariant, and five-language fixture tests.

The independent batch oracle extracts the actual article expressions. It
declares zero startup histories separately from the streaming implementation.
The copied description contains that source block for isolated-folder use.
"""
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
ARTICLE = DIRECTORY.parent.parent / 'tasc/2014-08-the-quotient-transform/content.md'
SPEC = importlib.util.spec_from_file_location('quotient_transform_master', DIRECTORY / 'quotient-transform.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
FIXTURES = MASTER._read_arrays(DIRECTORY / 'test_testdata.py')
INPUT = FIXTURES['INPUT_CLOSE']


def article_block():
    text = ARTICLE.read_text() if ARTICLE.exists() else (DIRECTORY / 'description.md').read_text()
    text = text.split('## EasyLanguage Code To Compute The Early-Onset Trend Indicator', 1)[1]
    return re.search(r'```easylanguage\s*\n(.*?)```', text, re.S).group(1)


def expression(block, name):
    return ' '.join(re.search(r'\b' + name + r'\s*=\s*(.*?);', block, re.S).group(1).split())


def source_eval(text, values, precise=True):
    if precise:
        text = text.replace('1.414', 'SQRT2').replace('3.14159', 'PI').replace('.707', 'INV_SQRT2')
    functions = dict(expvalue=math.exp, Cosine=lambda x: math.cos(x*math.pi/180.0),
                     Sine=lambda x: math.sin(x*math.pi/180.0), AbsValue=abs,
                     PI=math.pi, SQRT2=math.sqrt(2.0), INV_SQRT2=1.0/math.sqrt(2.0))
    return eval(text, {'__builtins__': {}}, functions | values)


def article_batch(prices, period, k, precise=True):
    """Full article recurrence with declared finite-sequence initial states."""
    block = article_block()
    values = dict(LPPeriod=period, K=k)
    for name in ('alpha1', 'a1', 'b1', 'c2', 'c3', 'c1'):
        values[name] = source_eval(expression(block, name), values, precise)
    expressions = {}
    for name in ('HP', 'Filt', 'Peak', 'X', 'Quotient'):
        formula = expression(block, name)
        for old, new in (('Close[1]', 'price1'), ('Close[2]', 'price2'),
                         ('HP[1]', 'hp1'), ('HP[2]', 'hp2'),
                         ('Filt[1]', 'filt1'), ('Filt[2]', 'filt2'), ('Peak[1]', 'peak1')):
            formula = formula.replace(old, new)
        expressions[name] = formula
    peak_reset = re.search(r'If AbsValue\(Filt\) > Peak Then Peak = (.*?);', block).group(1)
    hp, filt, peaks, normalized, quotient = [], [], [], [], []
    for i, price in enumerate(prices):
        if i < 2:
            h = f = p = x = 0.0
            q = k
        else:
            state = values | dict(Close=price, price1=prices[i-1], price2=prices[i-2],
                                  hp1=hp[-1], hp2=hp[-2], filt1=filt[-1], filt2=filt[-2], peak1=peaks[-1])
            h = source_eval(expressions['HP'], state, precise)
            f = source_eval(expressions['Filt'], state | dict(HP=h), precise)
            p = source_eval(expressions['Peak'], state, precise)
            if abs(f) > p:
                p = source_eval(peak_reset, dict(Filt=f), precise)
            x = source_eval(expressions['X'], dict(Filt=f, Peak=p), precise) if p != 0 else normalized[-1]
            q = source_eval(expressions['Quotient'], values | dict(X=x), precise)
        hp.append(h)
        filt.append(f)
        peaks.append(p)
        normalized.append(x)
        quotient.append(q)
    return [math.nan]*4 + quotient[4:], normalized, filt, peaks


def assert_series(test, actual, expected, tolerance=1e-11):
    test.assertEqual(len(actual), len(expected))
    for i, (a, e) in enumerate(zip(actual, expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a), f'bar {i+1}: expected NaN')
        else:
            test.assertTrue(math.isclose(a, e, rel_tol=tolerance, abs_tol=tolerance),
                            f'bar {i+1}: {a} versus {e}')


class QuotientTransformTests(unittest.TestCase):
    def test_all_confirmed_cases_against_article(self):
        self.assertEqual(len(INPUT), 252)
        self.assertEqual(len(MASTER.REFERENCE_CASES), 24)
        for case in MASTER.REFERENCE_CASES:
            parameters = MASTER._parameters(case)
            with self.subTest(parameters=parameters):
                expected = article_batch(INPUT, parameters['lowpass_period'], parameters['k'])[0]
                indicator = MASTER.QuotientTransform(**parameters)
                actual = [indicator.update(x) for x in INPUT]
                assert_series(self, actual, expected)

    def test_15_digit_python_fixtures(self):
        self.assertEqual(len([name for name in FIXTURES if name.startswith('EXPECTED_')]), 24)
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.QuotientTransform(**MASTER._parameters(case))
            raw = [indicator.update(x) for x in INPUT]
            saved = FIXTURES['EXPECTED_' + MASTER._case_suffix(case)]
            self.assertEqual(len(saved), 252)
            self.assertTrue(all(math.isnan(x) for x in saved[:4]))
            self.assertTrue(all(math.isfinite(x) for x in saved[4:]))
            for value, written in zip(raw[4:], saved[4:]):
                self.assertEqual(written, float(format(value, '.15g')))

    def test_all_other_language_values_and_comments(self):
        formats = (
            ('testdata_test.go', r'var expected(\w+) = \[\]float64\{(.*?)\}', 'math.NaN()'),
            ('testdata.ts', r'export const expected(\w+): number\[\] = \[(.*?)\];', 'NaN'),
            ('testdata.rs', r'pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]', 'f64::NAN'),
            ('testdata.zig', r'pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\}', 'nan'),
        )
        for filename, pattern, nan in formats:
            text = (DIRECTORY / filename).read_text()
            sections = dict(re.findall(pattern, text, re.S))
            self.assertEqual(len(sections), 24)
            for case in MASTER.REFERENCE_CASES:
                suffix = MASTER._case_suffix(case)
                key = suffix.lower() if filename.endswith('.rs') else suffix
                tokens = [x.strip() for x in sections[key].split(',') if x.strip()]
                expected = FIXTURES['EXPECTED_' + suffix]
                self.assertEqual(tokens, [MASTER._literal(value, nan) for value in expected])
                comments = '// ' + case['what_it_tests'] + '\n// ' + MASTER._parameter_comment(case)
                self.assertIn(comments, text)
        self.assertIn('package quotienttransform', (DIRECTORY / 'testdata_test.go').read_text())

    def test_mapping_endpoints_identity_inverse_and_monotonicity(self):
        transform = MASTER.quotient_transform
        for k in (-0.999, -0.85, -0.4, 0, 0.4, 0.85, 0.999):
            self.assertEqual(transform(-1, k), -1)
            self.assertEqual(transform(1, k), 1)
            self.assertEqual(transform(0, k), k)
            previous = -math.inf
            for i in range(101):
                x = -1 + i / 50
                result = transform(x, k)
                self.assertGreater(result, previous)
                self.assertTrue(-1 <= result <= 1)
                self.assertAlmostEqual(transform(result, -k), x, delta=5e-12)
                self.assertEqual(transform(-x, -k), -result)
                previous = result
        for x in (-1, -0.2, 0, 0.3, 1):
            self.assertEqual(transform(x, 0), x)
        self.assertEqual(transform(-0.85, 0.85), 0)

    def test_agc_identity_case_and_decay_first_reset(self):
        indicator = MASTER.QuotientTransform(k=0)
        previous_peak = 0.0
        for price in INPUT:
            value = indicator.update(price)
            if indicator._count >= 3:
                self.assertEqual(indicator._peak, max(0.991*previous_peak, abs(indicator._filt1)))
                self.assertLessEqual(abs(indicator._normalized), 1)
            if indicator.is_primed:
                self.assertEqual(value, indicator._normalized)
            previous_peak = indicator._peak
        # Deliberately set a reachable numeric-stage situation: current Filt
        # magnitude lies below old peak but above decayed peak. The article
        # resets to 0.995; comparing the undecayed old peak would miss it.
        indicator = MASTER.QuotientTransform(k=0)
        indicator._count = 5
        indicator._c1, indicator._c2, indicator._c3 = 2, 0, 0
        indicator._hp_gain = 1
        indicator._hp_decay = 0
        indicator._peak = 1
        value = indicator.update(0.995)
        self.assertEqual(indicator._peak, 0.995)
        self.assertEqual(value, 1)

    def test_constant_zero_peak_and_priming(self):
        for price in (0, 7, -7):
            for k in (-0.85, 0, 0.85):
                indicator = MASTER.QuotientTransform(k=k)
                self.assertFalse(indicator.is_primed)
                for i in range(20):
                    value = indicator.update(price)
                    self.assertEqual(indicator.is_primed, i >= 4)
                    if i < 4:
                        self.assertTrue(math.isnan(value))
                    else:
                        self.assertEqual(value, k)
                    self.assertEqual(indicator._peak, 0)
        # Retain normalized X on zero peak as the article conditional states.
        indicator = MASTER.QuotientTransform(k=0)
        indicator._count = 5
        indicator._normalized = 0.25
        self.assertEqual(indicator.update(0), 0.25)

    def test_nan_skip_and_reset_replay(self):
        for case in MASTER.REFERENCE_CASES:
            first = MASTER.QuotientTransform(**MASTER._parameters(case))
            second = MASTER.QuotientTransform(**MASTER._parameters(case))
            for price in INPUT:
                old = vars(first).copy()
                self.assertTrue(math.isnan(first.update(math.nan)))
                self.assertEqual(vars(first), old)
                assert_series(self, [first.update(price)], [second.update(price)], 1e-15)
            first.reset()
            second.reset()
            assert_series(self, [first.update(x) for x in INPUT], [second.update(x) for x in INPUT], 1e-15)

    def test_invalid_configuration_and_inputs(self):
        for period in (0, 1, -10, math.inf, math.nan):
            with self.assertRaises(ValueError):
                MASTER.QuotientTransform(lowpass_period=period)
        for k in (-1, 1, 2, math.inf, math.nan):
            with self.assertRaises(ValueError):
                MASTER.QuotientTransform(k=k)
            with self.assertRaises(ValueError):
                MASTER.quotient_transform(0, k)
        for x in (-1.01, 1.01, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                MASTER.quotient_transform(x)
        self.assertTrue(math.isnan(MASTER.quotient_transform(math.nan)))
        indicator = MASTER.QuotientTransform()
        with self.assertRaises(ValueError):
            indicator.update(math.inf)
        self.assertEqual(indicator._count, 0)

    def test_positive_price_scaling_preserves_normalized_output(self):
        for period in (2, 30, 30.5, 252):
            first = MASTER.QuotientTransform(period, 0.4)
            second = MASTER.QuotientTransform(period, 0.4)
            a = [first.update(x) for x in INPUT]
            b = [second.update(2*x) for x in INPUT]
            assert_series(self, a, b, 1e-15)

    def test_full_precision_changes_literal_article_output(self):
        precise = article_batch(INPUT, 30, 0.85)[0]
        literal = article_batch(INPUT, 30, 0.85, precise=False)[0]
        maximum = max(abs(a-b) for a, b in zip(precise[4:], literal[4:]))
        self.assertGreater(maximum, 1e-6)


if __name__ == '__main__':
    unittest.main()
