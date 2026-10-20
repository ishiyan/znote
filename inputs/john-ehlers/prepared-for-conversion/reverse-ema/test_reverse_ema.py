"""Article extraction, independent FIR convolution, state, and fixture tests.

The oracle reads the original listing from description.md if the external
article is absent. All tests use scalar standard-library Python functionality.
"""
import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
ARTICLE = DIRECTORY.parent.parent / 'tasc/2017-09-the-reverse-ema-indicator/content.md'
SPEC = importlib.util.spec_from_file_location('reverse_ema_master', DIRECTORY / 'reverse-ema.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
FIXTURES = MASTER._read_arrays(DIRECTORY / 'test_testdata.py')
INPUT = FIXTURES['INPUT_CLOSE']


def article_block():
    source = ARTICLE.read_text() if ARTICLE.exists() else (DIRECTORY / 'description.md').read_text()
    section = source.split('## EasyLanguage Code for Reverse EMA Indicator', 1)[1]
    return re.search(r'```easylanguage\s*\n(.*?)```', section, re.S).group(1)


def expression(block, name):
    return ' '.join(re.search(r'\b' + name + r'\s*=\s*(.*?);', block, re.S).group(1).split())


def article_batch(prices, alpha):
    """Extract each actual stage expression, without borrowing class states."""
    block = article_block()
    formulas = {}
    names = ('EMA', 'RE1', 'RE2', 'RE3', 'RE4', 'RE5', 'RE6', 'RE7', 'RE8', 'Wave')
    for name in names:
        formula = expression(block, name)
        for old in names:
            formula = formula.replace(old + '[1]', old + '_old')
        formulas[name] = formula
    values = {'AA': alpha, 'Close': 0, 'Power': math.pow}
    values['CC'] = eval(expression(block, 'CC'), {'__builtins__': {}}, values)
    for name in names:
        values[name] = 0.0
    outputs = []
    emas = []
    for price in prices:
        for name in names:
            values[name + '_old'] = values[name]
        values['Close'] = price
        for name in names:
            values[name] = eval(formulas[name], {'__builtins__': {}}, values)
        outputs.append(values['Wave'])
        emas.append(values['EMA'])
    return [math.nan]*min(8,len(outputs)) + outputs[8:], outputs, emas


def fir_coefficients(alpha):
    """Independent polynomial product of eight (c^(2^k)+one-bar delay) factors."""
    c = 1-alpha
    coefficients = [1.0]
    for exponent in (1,2,4,8,16,32,64,128):
        gain = math.pow(c, exponent)
        result = [0.0] * (len(coefficients)+1)
        for lag, value in enumerate(coefficients):
            result[lag] += gain*value
            result[lag+1] += value
        coefficients = result
    return coefficients


def convolution_batch(prices, alpha):
    coefficients = fir_coefficients(alpha)
    emas = []
    outputs = []
    old = 0.0
    for price in prices:
        ema = alpha*price + (1-alpha)*old
        emas.append(ema)
        old = ema
        reverse = 0.0
        for lag, value in enumerate(coefficients):
            if lag < len(emas):
                reverse += value*emas[-1-lag]
        outputs.append(ema-alpha*reverse)
    return [math.nan]*min(8,len(outputs))+outputs[8:]


def assert_series(test, actual, expected, tolerance=1e-11):
    test.assertEqual(len(actual), len(expected))
    for i, (a,e) in enumerate(zip(actual,expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a), f'bar {i+1}: expected NaN')
        else:
            test.assertTrue(math.isclose(a,e,abs_tol=tolerance,rel_tol=tolerance),
                            f'bar {i+1}: {a} versus {e}')


class ReverseEMATests(unittest.TestCase):
    def test_all_cases_against_extracted_article(self):
        self.assertEqual(len(INPUT),252)
        self.assertEqual(len(MASTER.REFERENCE_CASES),14)
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(alpha=case['alpha']):
                indicator = MASTER.ReverseEMA(**MASTER._parameters(case))
                actual = [indicator.update(price) for price in INPUT]
                expected,raw,emas = article_batch(INPUT,case['alpha'])
                assert_series(self,actual,expected,0)
                self.assertEqual(indicator._ema,emas[-1])
                assert_series(self,actual,convolution_batch(INPUT,case['alpha']))

    def test_zero_seed_and_all_stages_execute_on_first_bar(self):
        indicator = MASTER.ReverseEMA()
        self.assertTrue(math.isnan(indicator.update(INPUT[0])))
        ema = 0.1*INPUT[0]
        self.assertEqual(indicator._ema,ema)
        stage = ema
        for exponent,value in zip(MASTER.REVERSE_EXPONENTS,indicator._stages):
            stage = math.pow(0.9,exponent)*stage
            self.assertEqual(value,stage)
        self.assertEqual(indicator._count,1)
        for price in INPUT[1:8]:
            self.assertTrue(math.isnan(indicator.update(price)))
        self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isfinite(indicator.update(INPUT[8])))
        self.assertTrue(indicator.is_primed)
        self.assertEqual(indicator.warmup_bars,8)

    def test_alpha_one_is_exact_eight_bar_difference(self):
        indicator = MASTER.ReverseEMA(1)
        actual = [indicator.update(price) for price in INPUT]
        self.assertTrue(all(math.isnan(x) for x in actual[:8]))
        self.assertEqual(actual[8:],[INPUT[i]-INPUT[i-8] for i in range(8,252)])
        coefficients = fir_coefficients(1)
        self.assertEqual(coefficients,[0]*8+[1])

    def test_stage_delay_is_one_not_theoretical_dyadic_delay(self):
        # With alpha=1, dyadic-delay factors would give delay 255. The printed
        # code MUST have delay 8 instead, a decisive synthetic regression case.
        indicator = MASTER.ReverseEMA(1)
        outputs = [indicator.update(price) for price in [1]+[0]*259]
        self.assertEqual(outputs[8],-1)
        self.assertEqual(outputs[255],0)
        self.assertEqual(len(fir_coefficients(0.1)),9)

    def test_constant_dc_residual_and_impulse_convolution(self):
        # Test a small alpha so c^256 is large enough to detect; default alpha
        # has a tiny residual easily obscured by near-zero floating rounding.
        for alpha in (0.01,0.05,0.1,0.3,1):
            indicator = MASTER.ReverseEMA(alpha)
            for _ in range(5000):
                value = indicator.update(7)
            self.assertAlmostEqual(value,7*math.pow(1-alpha,256),delta=2e-12)
        prices = [1]+[0]*299
        for alpha in (0.001,0.1,0.5,1):
            indicator = MASTER.ReverseEMA(alpha)
            outputs = [indicator.update(price) for price in prices]
            assert_series(self,outputs,convolution_batch(prices,alpha),1e-14)

    def test_nan_skip_reset_and_invalid_configuration(self):
        for case in MASTER.REFERENCE_CASES:
            first = MASTER.ReverseEMA(case['alpha'])
            second = MASTER.ReverseEMA(case['alpha'])
            for price in INPUT:
                old = vars(first).copy()
                old['_stages'] = first._stages.copy()
                self.assertTrue(math.isnan(first.update(math.nan)))
                self.assertEqual(vars(first),old)
                assert_series(self,[first.update(price)],[second.update(price)],0)
            first.reset()
            second.reset()
            assert_series(self,[first.update(x) for x in INPUT],[second.update(x) for x in INPUT],0)
        for invalid in (0,-0.1,1.001,2,math.inf,-math.inf,math.nan):
            with self.assertRaises(ValueError):
                MASTER.ReverseEMA(invalid)
        indicator = MASTER.ReverseEMA()
        with self.assertRaises(AttributeError):
            indicator.alpha = 0.3
        for invalid in (math.inf,-math.inf):
            with self.assertRaises(ValueError):
                indicator.update(invalid)
        self.assertEqual(indicator._count,0)

    def test_linearity_price_scale_and_sign(self):
        for alpha in (0.001,0.1,0.5,1):
            a,b = MASTER.ReverseEMA(alpha),MASTER.ReverseEMA(alpha)
            first = [a.update(x) for x in INPUT]
            second = [b.update(-2*x) for x in INPUT]
            assert_series(self,second,[-2*x for x in first],0)

    def test_preserved_inputs_and_embedded_closes(self):
        tree = ast.parse((DIRECTORY/'reverse-ema.py').read_text())
        main = next(node for node in tree.body if isinstance(node,ast.If))
        self.assertEqual(ast.literal_eval(main.body[0].value),INPUT)
        for key in ('INPUT_CLOSE','INPUT_HIGH','INPUT_LOW','INPUT_OPEN'):
            self.assertEqual(len(FIXTURES[key]),252)
        formats = (
            ('testdata_test.go',r'var test(\w+) = \[\]float64\{(.*?)\}'),
            ('testdata.ts',r'export const test(\w+): number\[\] = \[(.*?)\];'),
            ('testdata.rs',r'pub fn test_(\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]'),
            ('testdata.zig',r'pub fn test(\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\}'),
        )
        for filename,pattern in formats:
            sections = dict(re.findall(pattern,(DIRECTORY/filename).read_text(),re.S))
            self.assertEqual(len(sections),4)
            for suffix,body in sections.items():
                key = 'INPUT_CLOSE' if suffix.lower()=='input' else 'INPUT_'+suffix.upper()
                self.assertEqual([float(x.strip()) for x in body.split(',') if x.strip()],FIXTURES[key])

    def test_python_reference_precision(self):
        if not MASTER.REFERENCE_CASES_CONFIRMED:
            self.skipTest('parameter cases await confirmation')
        self.assertEqual(len([key for key in FIXTURES if key.startswith('EXPECTED_')]),14)
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.ReverseEMA(**MASTER._parameters(case))
            raw = [indicator.update(x) for x in INPUT]
            saved = FIXTURES['EXPECTED_'+MASTER._case_suffix(case)]
            self.assertEqual(len(saved),252)
            self.assertTrue(all(math.isnan(x) for x in saved[:8]))
            self.assertTrue(all(math.isfinite(x) for x in saved[8:]))
            for original,value in zip(raw[8:],saved[8:]):
                self.assertEqual(value,float(format(original,'.15g')))

    def test_other_language_expected_values_and_comments(self):
        if not MASTER.REFERENCE_CASES_CONFIRMED:
            self.skipTest('parameter cases await confirmation')
        formats = (
            ('testdata_test.go',r'var expected(\w+) = \[\]float64\{(.*?)\}','math.NaN()'),
            ('testdata.ts',r'export const expected(\w+): number\[\] = \[(.*?)\];','NaN'),
            ('testdata.rs',r'pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]','f64::NAN'),
            ('testdata.zig',r'pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\}','nan'),
        )
        for filename,pattern,nan in formats:
            text = (DIRECTORY/filename).read_text()
            sections = dict(re.findall(pattern,text,re.S))
            self.assertEqual(len(sections),14)
            for case in MASTER.REFERENCE_CASES:
                suffix = MASTER._case_suffix(case)
                key = suffix.lower() if filename.endswith('.rs') else suffix
                tokens = [x.strip() for x in sections[key].split(',') if x.strip()]
                self.assertEqual(tokens,[MASTER._literal(x,nan) for x in FIXTURES['EXPECTED_'+suffix]])
                self.assertIn('// '+case['what_it_tests']+'\n// '+MASTER._parameter_comment(case),text)


if __name__ == '__main__':
    unittest.main()
