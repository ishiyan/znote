"""Independent article-equation, startup, synthetic-signal, and fixture tests.

When copied without the source tree, the oracle extracts the original article
listing reproduced in description.md. Only standard Python functionality is used.
"""
import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
ARTICLE = DIRECTORY.parent.parent / 'tasc/2015-01-whiter-is-brighter/content.md'
SPEC = importlib.util.spec_from_file_location('universal_oscillator_master', DIRECTORY / 'universal-oscillator.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
FIXTURES = MASTER._read_arrays(DIRECTORY / 'test_testdata.py')
INPUT = FIXTURES['INPUT_CLOSE']


def article_block():
    source = ARTICLE.read_text() if ARTICLE.exists() else (DIRECTORY / 'description.md').read_text()
    section = source.split('## EasyLanguage Code For Universal Oscillator', 1)[1]
    return re.search(r'```easylanguage\s*\n(.*?)```', section, re.S).group(1)


def expression(block, name):
    return ' '.join(re.search(r'\b' + name + r'\s*=\s*(.*?);', block, re.S).group(1).split())


def source_eval(formula, values, precise=True):
    if precise:
        formula = formula.replace('1.414', 'SQRT2').replace('3.14159', 'PI')
    functions = dict(expvalue=math.exp, Cosine=lambda angle: math.cos(angle * math.pi / 180),
                     AbsValue=abs, SQRT2=math.sqrt(2), PI=math.pi)
    return eval(formula, {'__builtins__': {}}, functions | values)


def article_batch(prices, band_edge, precise=True):
    """Batch recurrence extracted from the printed code, independent of class."""
    block = article_block()
    values = {'BandEdge': band_edge}
    for name in ('a1', 'b1', 'c2', 'c3', 'c1'):
        values[name] = source_eval(expression(block, name), values, precise)
    formulas = {}
    for name in ('WhiteNoise', 'Filt', 'Peak', 'Universal'):
        formula = expression(block, name)
        for old, new in (('Close[2]', 'price2'), ('WhiteNoise[1]', 'white1'),
                         ('Filt[1]', 'filt1'), ('Filt[2]', 'filt2'), ('Peak[1]', 'peak1')):
            formula = formula.replace(old, new)
        formulas[name] = formula
    first_peak = source_eval(re.search(r'If Currentbar = 1 Then Peak = (.*?);', block).group(1), {}, precise)
    reset_peak = re.search(r'If AbsValue\(Filt\) > Peak Then Peak = (.*?);', block).group(1)
    white, filt, peak, outputs = [], [], [], []
    for i, price in enumerate(prices):
        state = values | dict(Close=price, price2=prices[i-2] if i >= 2 else 0,
                              white1=white[-1] if i else 0,
                              filt1=filt[-1] if i else 0, filt2=filt[-2] if i >= 2 else 0,
                              peak1=peak[-1] if i else 0)
        w = source_eval(formulas['WhiteNoise'], state, precise) if i >= 2 else 0
        f = source_eval(formulas['Filt'], state | dict(WhiteNoise=w), precise)
        if i == 0:
            f = 0
        elif i == 1:
            f = values['c2'] * filt[-1]
        elif i == 2:
            f = values['c2'] * filt[-1] + values['c3'] * filt[-2]
        p = first_peak if i == 0 else source_eval(formulas['Peak'], state, precise)
        if abs(f) > p:
            p = source_eval(reset_peak, dict(Filt=f), precise)
        u = source_eval(formulas['Universal'], dict(Filt=f, Peak=p), precise) if p else (outputs[-1] if i else 0)
        white.append(w)
        filt.append(f)
        peak.append(p)
        outputs.append(u)
    return [math.nan] * min(3, len(outputs)) + outputs[3:], white, filt, peak


def assert_series(test, actual, expected, tolerance=1e-11):
    test.assertEqual(len(actual), len(expected))
    for i, (a, e) in enumerate(zip(actual, expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a), f'bar {i+1}: expected NaN')
        else:
            test.assertTrue(math.isclose(a, e, abs_tol=tolerance, rel_tol=tolerance),
                            f'bar {i+1}: {a} versus {e}')


class UniversalOscillatorTests(unittest.TestCase):
    def test_all_cases_against_article(self):
        self.assertEqual(len(INPUT), 252)
        self.assertEqual(len(MASTER.REFERENCE_CASES), 12)
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(band_edge=case['band_edge']):
                expected = article_batch(INPUT, case['band_edge'])[0]
                indicator = MASTER.UniversalOscillator(case['band_edge'])
                assert_series(self, [indicator.update(price) for price in INPUT], expected)

    def test_startup_preserves_bar_three_white_noise_and_seed(self):
        indicator = MASTER.UniversalOscillator()
        for i, price in enumerate(INPUT[:3]):
            self.assertTrue(math.isnan(indicator.update(price)))
            self.assertEqual(indicator._filt1, 0)
            self.assertEqual(indicator._peak, 1e-7 * (0.991 ** i))
            self.assertFalse(indicator.is_primed)
        self.assertEqual(indicator._white1, (INPUT[2] - INPUT[0]) / 2)
        w4 = (INPUT[3] - INPUT[1]) / 2
        f4 = indicator._c1 * (w4 + indicator._white1) / 2
        result = indicator.update(INPUT[3])
        self.assertEqual(indicator._filt1, f4)
        self.assertEqual(result, f4 / max(0.991 * 0.991 * 0.991 * 1e-7, abs(f4)))
        self.assertEqual(indicator.warmup_bars, 3)
        self.assertTrue(indicator.is_primed)

    def test_small_signal_respects_one_time_peak_seed(self):
        indicator = MASTER.UniversalOscillator()
        result = [indicator.update(x) for x in (0, 0, 1e-10, 0)][-1]
        self.assertAlmostEqual(result, indicator._c1 * 2.5e-11 / (1e-7 * 0.991 ** 3), delta=1e-18)
        self.assertGreater(result, 0)
        self.assertLess(result, 1)
        self.assertLess(indicator._peak, 1e-7)  # Seed is not a continuing floor.

    def test_constant_and_nyquist_signals_have_zero_output(self):
        for prices in ([7] * 50, [-7] * 50, [0] * 50, [1, -1] * 25):
            indicator = MASTER.UniversalOscillator()
            outputs = [indicator.update(x) for x in prices]
            self.assertTrue(all(math.isnan(x) for x in outputs[:3]))
            self.assertEqual(outputs[3:], [0] * 47)
            self.assertEqual(indicator._white1, 0)

    def test_step_is_two_white_pulses_and_ramp_is_sustained_momentum(self):
        prices = [0] * 8 + [4] * 50
        expected, white, _, _ = article_batch(prices, 20)
        self.assertEqual(white[8:12], [2, 2, 0, 0])
        indicator = MASTER.UniversalOscillator()
        assert_series(self, [indicator.update(x) for x in prices], expected)
        rising, falling = MASTER.UniversalOscillator(), MASTER.UniversalOscillator()
        up = [rising.update(x) for x in range(300)]
        down = [falling.update(-x) for x in range(300)]
        self.assertAlmostEqual(rising._filt1, 1, delta=1e-12)
        self.assertGreater(up[-1], 0.99)
        assert_series(self, up, [-x for x in down], 1e-15)

    def test_decay_first_reset_and_zero_peak_hold(self):
        indicator = MASTER.UniversalOscillator()
        indicator._count = 4
        indicator._c1, indicator._c2, indicator._c3 = 2, 0, 0
        indicator._white1 = 0.995
        indicator._peak = 1
        self.assertEqual(indicator.update(0), 1)
        self.assertEqual(indicator._peak, 0.995)
        indicator = MASTER.UniversalOscillator()
        indicator._count = 4
        indicator._universal = 0.25
        self.assertEqual(indicator.update(0), 0.25)

    def test_nan_skip_reset_validation_and_readonly_setting(self):
        for case in MASTER.REFERENCE_CASES:
            first = MASTER.UniversalOscillator(case['band_edge'])
            second = MASTER.UniversalOscillator(case['band_edge'])
            for price in INPUT:
                old = vars(first).copy()
                self.assertTrue(math.isnan(first.update(math.nan)))
                self.assertEqual(vars(first), old)
                assert_series(self, [first.update(price)], [second.update(price)], 1e-15)
            first.reset()
            second.reset()
            assert_series(self, [first.update(x) for x in INPUT], [second.update(x) for x in INPUT], 1e-15)
        for invalid in (0, 1, -10, math.inf, -math.inf, math.nan):
            with self.assertRaises(ValueError):
                MASTER.UniversalOscillator(invalid)
        indicator = MASTER.UniversalOscillator(20.5)
        with self.assertRaises(AttributeError):
            indicator.band_edge = 10
        for invalid in (math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(invalid)
        self.assertEqual(indicator._count, 0)

    def test_input_fixtures_and_embedded_closes_preserved(self):
        tree = ast.parse((DIRECTORY / 'universal-oscillator.py').read_text())
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
        if not MASTER.REFERENCE_CASES_CONFIRMED:
            self.skipTest('reference cases await user confirmation')
        self.assertEqual(len([key for key in FIXTURES if key.startswith('EXPECTED_')]), 12)
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.UniversalOscillator(**MASTER._parameters(case))
            raw = [indicator.update(x) for x in INPUT]
            saved = FIXTURES['EXPECTED_' + MASTER._case_suffix(case)]
            self.assertEqual(len(saved), 252)
            self.assertTrue(all(math.isnan(x) for x in saved[:3]))
            self.assertTrue(all(math.isfinite(x) for x in saved[3:]))
            self.assertTrue(all(-1 <= x <= 1 for x in saved[3:]))
            for a, b in zip(raw[3:], saved[3:]):
                self.assertEqual(float(format(a, '.15g')), b)

    def test_other_language_expected_values_and_comments(self):
        if not MASTER.REFERENCE_CASES_CONFIRMED:
            self.skipTest('reference cases await user confirmation')
        formats = (
            ('testdata_test.go', r'var expected(\w+) = \[\]float64\{(.*?)\}', 'math.NaN()'),
            ('testdata.ts', r'export const expected(\w+): number\[\] = \[(.*?)\];', 'NaN'),
            ('testdata.rs', r'pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]', 'f64::NAN'),
            ('testdata.zig', r'pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\}', 'nan'),
        )
        for filename, pattern, nan in formats:
            text = (DIRECTORY / filename).read_text()
            sections = dict(re.findall(pattern, text, re.S))
            self.assertEqual(len(sections), 12)
            for case in MASTER.REFERENCE_CASES:
                suffix = MASTER._case_suffix(case)
                key = suffix.lower() if filename.endswith('.rs') else suffix
                tokens = [x.strip() for x in sections[key].split(',') if x.strip()]
                self.assertEqual(tokens, [MASTER._literal(x, nan) for x in FIXTURES['EXPECTED_' + suffix]])
                self.assertIn('// ' + case['what_it_tests'] + '\n// ' + MASTER._parameter_comment(case), text)


if __name__ == '__main__':
    unittest.main()
