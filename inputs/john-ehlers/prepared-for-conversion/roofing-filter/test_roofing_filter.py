"""Independent source, behavior, and cross-language fixture checks.

The classes are porting references, so tests cover actual source expressions,
startup contracts, missing observations, and the exported decimal fixtures.
No numpy, pandas, or original application framework is required.
"""
import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
SLUG = DIRECTORY.name
SOURCE_DIRECTORY = DIRECTORY.parent.parent / 'tasc/2014-01-predictive-and-successful-indicators'
BOOK_DIRECTORY = DIRECTORY.parent.parent / '2013-cycle-analytics-for-traders'
SPEC = importlib.util.spec_from_file_location(SLUG.replace('-', '_') + '_master', DIRECTORY / (SLUG + '.py'))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
FIXTURES = MASTER._read_arrays(DIRECTORY / 'test_testdata.py')
INPUT = FIXTURES['INPUT_CLOSE']


def source_block(path, heading):
    """Extract the actual published code rather than rewriting its formulas."""
    text = path.read_text() if path.exists() else (DIRECTORY / 'description.md').read_text()
    section = text.split(heading, 1)[1]
    return re.search(r'```easylanguage\s*\n(.*?)```', section, re.S).group(1)


def expression(block, name):
    return ' '.join(re.search(r'\b' + name + r'\s*=\s*(.*?);', block, re.S).group(1).split())


def source_eval(text, values, full_precision=True):
    if full_precision:
        text = text.replace('1.414', 'SQRT2').replace('3.14159', 'PI').replace('.707', 'INV_SQRT2')
    functions = dict(expvalue=math.exp, Cosine=lambda degrees: math.cos(degrees * math.pi / 180.0),
                     Sine=lambda degrees: math.sin(degrees * math.pi / 180.0),
                     SQRT2=math.sqrt(2.0), INV_SQRT2=1.0/math.sqrt(2.0), PI=math.pi)
    return eval(text, {'__builtins__': {}}, functions | values)


def source_ss(data, period, full_precision=True):
    block = source_block(SOURCE_DIRECTORY / 'content.md', '## EasyLanguage Code To Compute The SuperSmoother Filter')
    values = {}
    for name in ('a1', 'b1', 'c2', 'c3', 'c1'):
        values[name] = source_eval(expression(block, name).replace('/ 10', '/ Period'),
                                   values | dict(Period=period), full_precision)
    recurrence = expression(block, 'Filt').replace('Close[1]', 'price1').replace('Filt[1]', 'f1').replace('Filt[2]', 'f2')
    outputs = []
    for index, price in enumerate(data):
        # Declared constant-price prehistory, no fabricated zero price input.
        state = dict(Close=price, price1=data[index-1] if index else price,
                     f1=outputs[-1] if outputs else price,
                     f2=outputs[-2] if len(outputs) >= 2 else data[0])
        outputs.append(source_eval(recurrence, values | state, full_precision))
    return [math.nan, math.nan] + outputs[2:]


def source_rf(data, shortest=10, longest=48, poles=2, zero=False, full_precision=True):
    listing = '7-3' if poles == 2 else ('7-2' if zero else '7-1')
    block = source_block(BOOK_DIRECTORY / 'ch7.md', '**Code Listing ' + listing + '.')
    values = dict(LPPeriod=shortest, HPPeriod=longest)
    for name in ('alpha1', 'a1', 'b1', 'c2', 'c3', 'c1'):
        formula = expression(block, name).replace('/ 10', '/ LPPeriod').replace('/ 48', '/ HPPeriod')
        if not full_precision and name == 'alpha1' and poles == 1 and longest == 4:
            raise ValueError('literal source is undefined at one-pole period 4')
        values[name] = source_eval(formula, values, full_precision)
    if poles == 1 and longest == 4 and full_precision:
        # Continuous extension of the source formula, independently specified.
        values['alpha1'] = 1.0
    formulas = {}
    for name in ('HP', 'Filt') + (('Filt2',) if zero else ()):
        formula = expression(block, name)
        for old, new in [('Close[1]', 'price1'), ('Close[2]', 'price2'),
                         ('HP[1]', 'hp1'), ('HP[2]', 'hp2'),
                         ('Filt[1]', 'f1'), ('Filt[2]', 'f2'), ('Filt2[1]', 'z1')]:
            formula = formula.replace(old, new)
        formulas[name] = formula
    hp, filt, final = [], [], []
    for index, price in enumerate(data):
        if index < poles:
            h = f = z = 0.0
        else:
            state = values | dict(Close=price, price1=data[index-1], price2=data[index-2],
                                  hp1=hp[-1], hp2=hp[-2] if len(hp) >= 2 else 0.0,
                                  f1=filt[-1], f2=filt[-2] if len(filt) >= 2 else 0.0,
                                  z1=final[-1])
            h = source_eval(formulas['HP'], state, full_precision)
            f = source_eval(formulas['Filt'], state | dict(HP=h), full_precision)
            z = source_eval(formulas['Filt2'], state | dict(Filt=f), full_precision) if zero else f
        hp.append(h)
        filt.append(f)
        final.append(z)
    warmup = 4 if poles == 2 or zero else 3
    return [math.nan] * warmup + final[warmup:]


def source_mesa(data, length, shortest, longest):
    roofing = source_rf(data, shortest, longest)
    block = source_block(SOURCE_DIRECTORY / 'content.md', '## EasyLanguage Code To Compute MESA Stochastic Indicator')
    values = dict(Period=shortest)
    for name in ('a1', 'b1', 'c2', 'c3', 'c1'):
        values[name] = source_eval(expression(block, name).replace('/ 10', '/ Period'), values)
    stoc_formula = expression(block, 'Stoc')
    formula = expression(block, 'MESAStochastic')
    for old, new in [('Stoc[1]', 's1'), ('MESAStochastic[1]', 'm1'), ('MESAStochastic[2]', 'm2')]:
        formula = formula.replace(old, new)
    normalized, filtered, output = [], [], []
    for index, roof in enumerate(roofing):
        # Four hidden Roofing outputs are excluded from the normalization window.
        if index < length + 3:
            output.append(math.nan)
            continue
        window = roofing[index-length+1:index+1]
        highest, lowest = max(window), min(window)
        s = (source_eval(stoc_formula, dict(Filt=roof, HighestC=highest, LowestC=lowest))
             if highest != lowest else 0.5)
        m = source_eval(formula, values | dict(Stoc=s, s1=normalized[-1] if normalized else 0.0,
                                             m1=filtered[-1] if filtered else 0.0,
                                             m2=filtered[-2] if len(filtered) >= 2 else 0.0))
        normalized.append(s)
        filtered.append(m)
        output.append(m if len(filtered) >= 3 else math.nan)
    return output


def assert_series(test, actual, expected, tolerance=1e-11):
    test.assertEqual(len(actual), len(expected))
    for index, (left, right) in enumerate(zip(actual, expected)):
        if math.isnan(right):
            test.assertTrue(math.isnan(left), f'bar {index+1}: expected NaN')
        else:
            test.assertTrue(math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance),
                            f'bar {index+1}: {left} versus {right}')


class MasterTests(unittest.TestCase):
    def test_published_recurrence_for_every_confirmed_case(self):
        self.assertEqual(len(INPUT), 252)
        for case in MASTER.REFERENCE_CASES:
            parameters = MASTER._parameters(case)
            with self.subTest(parameters=parameters):
                indicator = MASTER.MASTER_CLASS(**parameters)
                actual = [indicator.update(value) for value in INPUT]
                if SLUG == 'super-smoother':
                    expected = source_ss(INPUT, parameters['period'])
                elif SLUG == 'roofing-filter':
                    expected = source_rf(INPUT, parameters['shortest_cycle_period'],
                                         parameters['longest_cycle_period'], parameters['highpass_poles'], parameters['zero_mean'])
                else:
                    expected = source_mesa(INPUT, parameters['length'], parameters['shortest_cycle_period'], parameters['longest_cycle_period'])
                # Source degree->radian conversion and equivalent HP alpha math
                # cause a few ulps of difference. Compare every bar, skip none.
                assert_series(self, actual, expected)

    def test_fifteen_digit_fixtures_for_every_case(self):
        names = {name for name in FIXTURES if name.startswith('EXPECTED_')}
        self.assertEqual(len(names), len(MASTER.REFERENCE_CASES))
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.MASTER_CLASS(**MASTER._parameters(case))
            values = [indicator.update(value) for value in INPUT]
            array = FIXTURES['EXPECTED_' + MASTER._case_suffix(case)]
            self.assertEqual(len(array), 252)
            self.assertTrue(all(math.isnan(x) for x in array[:indicator.warmup_bars]))
            for raw, written in zip(values, array):
                if math.isnan(raw):
                    self.assertTrue(math.isnan(written))
                else:
                    self.assertEqual(written, float(format(raw, '.15g')))

    def test_all_languages_preserve_values_and_comments(self):
        syntax = (
            ('testdata_test.go', r'var expected(\w+) = \[\]float64\{(.*?)\}', 'math.NaN()'),
            ('testdata.ts', r'export const expected(\w+): number\[\] = \[(.*?)\];', 'NaN'),
            ('testdata.rs', r'pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]', 'f64::NAN'),
            ('testdata.zig', r'pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\}', 'nan'),
        )
        for filename, pattern, nan in syntax:
            text = (DIRECTORY / filename).read_text()
            sections = dict(re.findall(pattern, text, re.S))
            self.assertEqual(len(sections), len(MASTER.REFERENCE_CASES), filename)
            for case in MASTER.REFERENCE_CASES:
                suffix = MASTER._case_suffix(case)
                key = suffix.lower() if filename.endswith('.rs') else suffix
                tokens = [token.strip() for token in sections[key].split(',') if token.strip()]
                self.assertEqual(len(tokens), 252)
                expected = FIXTURES['EXPECTED_' + suffix]
                self.assertEqual(tokens, [MASTER._literal(x, nan) for x in expected])
                comments = '// ' + case['what_it_tests'] + '\n// ' + MASTER._parameter_comment(case)
                self.assertIn(comments, text)
        self.assertIn('package ' + SLUG.replace('-', ''), (DIRECTORY / 'testdata_test.go').read_text())

    def test_nan_skips_all_state_and_reset_reproduces_start(self):
        for case in MASTER.REFERENCE_CASES:
            parameters = MASTER._parameters(case)
            with self.subTest(parameters=parameters):
                first = MASTER.MASTER_CLASS(**parameters)
                second = MASTER.MASTER_CLASS(**parameters)
                for value in INPUT:
                    self.assertTrue(math.isnan(first.update(math.nan)))
                    assert_series(self, [first.update(value)], [second.update(value)], 1e-15)
                    self.assertEqual(first.is_primed, second.is_primed)
                first.reset()
                third = MASTER.MASTER_CLASS(**parameters)
                assert_series(self, [first.update(x) for x in INPUT], [third.update(x) for x in INPUT], 1e-15)

    def test_invalid_configuration_and_infinite_sample(self):
        if SLUG == 'super-smoother':
            cases = [dict(period=x) for x in (1, 0, -1, math.nan, math.inf)]
        elif SLUG == 'roofing-filter':
            cases = [dict(shortest_cycle_period=1), dict(longest_cycle_period=10),
                     dict(highpass_poles=3), dict(highpass_poles=True), dict(zero_mean=True),
                     dict(longest_cycle_period=math.inf), dict(shortest_cycle_period=math.nan)]
        else:
            cases = [dict(length=x) for x in (1, 0, -1, 2.5, True)]
            cases += [dict(shortest_cycle_period=1), dict(longest_cycle_period=10)]
        for parameters in cases:
            with self.assertRaises(ValueError):
                MASTER.MASTER_CLASS(**parameters)
        indicator = MASTER.MASTER_CLASS()
        with self.assertRaises(ValueError):
            indicator.update(math.inf)
        self.assertFalse(indicator.is_primed)

    def test_constant_input_and_priming(self):
        indicator = MASTER.MASTER_CLASS()
        values = [indicator.update(7.0) for _ in range(500)]
        self.assertEqual(next(i for i, value in enumerate(values) if math.isfinite(value)), indicator.warmup_bars)
        target = 7.0 if SLUG == 'super-smoother' else (0.0 if SLUG == 'roofing-filter' else 0.5)
        self.assertAlmostEqual(values[-1], target, delta=1e-12)

    def test_filter_specific_behavior(self):
        if SLUG == 'super-smoother':
            data = [1.0 if i % 2 == 0 else -1.0 for i in range(500)]
            indicator = MASTER.MASTER_CLASS()
            output = [indicator.update(x) for x in data]
            self.assertLess(abs(output[-1]), 1e-12)  # Exact Nyquist numerator zero.
        elif SLUG == 'roofing-filter':
            # Two DC zeros reject a sustained linear ramp, not only a constant.
            indicator = MASTER.MASTER_CLASS()
            output = [indicator.update(float(i)) for i in range(1000)]
            self.assertLess(abs(output[-1]), 1e-12)
            boundary = MASTER.MASTER_CLASS(2, 4, 1)
            self.assertAlmostEqual(boundary._gain, 0.5, delta=1e-15)
            self.assertAlmostEqual(boundary._decay, 0.0, delta=1e-15)
        else:
            # The smoother must be allowed to exceed raw stochastic's bounds.
            found = any(any(x < 0.0 or x > 1.0 for x in FIXTURES['EXPECTED_' + MASTER._case_suffix(case)]
                            if math.isfinite(x)) for case in MASTER.REFERENCE_CASES)
            self.assertTrue(found, 'fixtures must exercise unclipped smoothing overshoot')


if __name__ == '__main__':
    unittest.main()
