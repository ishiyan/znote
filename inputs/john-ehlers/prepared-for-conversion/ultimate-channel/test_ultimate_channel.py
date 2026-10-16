"""Article-expression and cross-language fixture verification; standard Python."""

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
SLUG = 'ultimate-channel'
ARTICLE = DIRECTORY.parent.parent / 'tasc/2024-04-the-ultimate-smoother/content.md'
COMPOSITE_ARTICLE = DIRECTORY.parent.parent / 'tasc/2024-05-ultimate-channels-and-ultimate-bands/content.md'
SPEC = importlib.util.spec_from_file_location(SLUG.replace('-','_'), DIRECTORY / (SLUG+'.py'))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')


def article_batch(prices, period, full_precision=True):
    """Independent batch evaluation of the actual article's expressions.

    The article is not imported or executed as a program. Only its coefficient
    assignments and US recurrence are extracted. The selected precision policy
    explicitly substitutes sqrt(2) and pi, and converts the cosine to radians.
    full_precision=False evaluates the original printed coefficients instead.
    """
    blocks = re.findall(r"```easylanguage\n(.*?)```", ARTICLE.read_text(), flags=re.DOTALL)
    block = next(block for block in blocks if "UltimateSmoother Function" in block)
    coefficients = [
        (name, re.search(r"\b" + name + r"\s*=\s*(.*?);", block).group(1))
        for name in ("a1", "b1", "c2", "c3", "c1")
    ]
    if full_precision:
        # Only the coefficient constants and cosine units change. All arithmetic
        # in the recursively extracted source expression stays untouched.
        coefficients = [(name, expression.replace("1.414", "SQRT_TWO")
                         .replace("3.14159", "PI").replace("180", "PI"))
                        for name, expression in coefficients]
    recurrence = re.search(r"If CurrentBar >= 4 Then US = (.*?);", block, flags=re.DOTALL).group(1)
    recurrence = recurrence.replace("Price[1]", "price1").replace("Price[2]", "price2")
    recurrence = recurrence.replace("US[1]", "us1").replace("US[2]", "us2")
    recurrence = " ".join(recurrence.split())
    functions = {
        "expvalue": math.exp,
        "Cosine": math.cos if full_precision else lambda angle: math.cos(math.radians(angle)),
    }
    values = {"Period": period, "PI": math.pi, "SQRT_TWO": math.sqrt(2.0)}
    for name, expression in coefficients:
        values[name] = eval(expression, {"__builtins__": {}}, functions | values)
    outputs = []
    for t, price in enumerate(prices):
        if t < 3:
            outputs.append(price)
        else:
            values.update(Price=price, price1=prices[t-1], price2=prices[t-2],
                          us1=outputs[t-1], us2=outputs[t-2])
            outputs.append(eval(recurrence, {"__builtins__": {}}, values))
    return outputs


def composite_batch(case, arrays):
    # Reproduce TH/TL from the source's branch conditions, independently of
    # max/min in the streaming master. First-bar history policy is explicit.
    closes, highs, lows = (arrays[name] for name in MASTER.REQUIRED_INPUTS)
    true_ranges = []
    for t in range(len(closes)):
        th = closes[t-1] if t > 0 and closes[t-1] > highs[t] else highs[t]
        tl = closes[t-1] if t > 0 and closes[t-1] < lows[t] else lows[t]
        true_ranges.append(th-tl)
    centers = article_batch(closes, case.length)
    ranges = article_batch(true_ranges, case.str_length)
    text = COMPOSITE_ARTICLE.read_text()
    expressions = [re.search(name + r' = (.*?);', text).group(1)
                   .replace('$UltimateSmoother(Close, Length)', 'center')
                   for name in ('UpperChnl','LowerChnl')]
    return [(center, width, *(eval(expression, {'__builtins__': {}},
             {'center':center,'NumSTRs':case.num_strs,'STR':width}) for expression in expressions))
            for center, width in zip(centers,ranges)]


def instance():
    return MASTER.UltimateChannel()


def feed(indicator, index):
    return indicator.update(INPUTS['INPUT_CLOSE'][index], INPUTS['INPUT_HIGH'][index],
                            INPUTS['INPUT_LOW'][index])


def run(indicator, arrays, count):
    return [indicator.update(c,h,l) for c,h,l in zip(arrays['INPUT_CLOSE'][:count],
            arrays['INPUT_HIGH'][:count], arrays['INPUT_LOW'][:count])]


def reject(indicator, value):
    indicator.update(value, value, value)


def assert_values(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for index, (a, e) in enumerate(zip(actual, expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a), (index, a, e))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a, e, rel_tol=tolerance,
                                                            abs_tol=tolerance), (index, a, e))


class ReferenceTests(unittest.TestCase):
    def test_all_cases_match_independent_article_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case):
                actual = MASTER._run_case(case, INPUTS)
                oracle = composite_batch(case, INPUTS)
                for column in range(4):
                    # Extracted recurrence, inclusive sum order and boundary
                    # expressions match exactly before fixture serialization.
                    assert_values(self, [row[column] for row in actual],
                                  [row[column] for row in oracle], tolerance=0.0)

    def test_generated_python_arrays(self):
        expected_names = set()
        for case in MASTER.REFERENCE_CASES:
            outputs = MASTER._run_case(case, INPUTS)
            for field, token in zip(MASTER.OUTPUT_FIELDS, MASTER.OUTPUT_TOKENS):
                name = 'EXPECTED_' + MASTER._case_suffix(case) + '_' + token
                expected_names.add(name)
                self.assertEqual(len(INPUTS[name]), 252)
                assert_values(self, [getattr(row, field) for row in outputs], INPUTS[name])
        self.assertEqual(expected_names, {name for name in INPUTS if name.startswith('EXPECTED_')})

    def test_translated_arrays_comments_and_nan_positions(self):
        patterns = {
            'testdata_test.go': r'var expected(\w+) = \[\]float64\{\s*(.*?)\n\}',
            'testdata.ts': r'export const expected(\w+): number\[\] = \[\s*(.*?)\n\];',
            'testdata.rs': r'pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[\s*(.*?)\n\s*\]\s*\}',
            'testdata.zig': r'pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{\s*(.*?)\n\s*\};\s*\}',
        }
        nans = {'testdata_test.go':'math.NaN()', 'testdata.ts':'NaN',
                'testdata.rs':'f64::NAN', 'testdata.zig':'nan'}
        for filename, pattern in patterns.items():
            text = (DIRECTORY / filename).read_text()
            matches = list(re.finditer(pattern, text, re.DOTALL))
            self.assertEqual(len(matches), 4 * len(MASTER.REFERENCE_CASES))
            for match in matches:
                suffix, body = match.groups()
                name = 'EXPECTED_' + suffix.upper()
                values = [math.nan if token.strip() == nans[filename] else float(token.strip())
                          for token in body.split(',') if token.strip()]
                assert_values(self, values, INPUTS[name], tolerance=0.0)
                case = next(case for case in MASTER.REFERENCE_CASES
                            if suffix.upper().rsplit('_', 1)[0] == MASTER._case_suffix(case))
                comments = f'// {case.what_it_tests}\n// {MASTER._parameter_comment(case)}\n'
                self.assertTrue(text[:match.start()].endswith(comments), name)
        go = (DIRECTORY / 'testdata_test.go').read_text()
        self.assertIn('package ' + SLUG.replace('-', ''), go)
        self.assertIn('import "math"', go)
        zig = (DIRECTORY / 'testdata.zig').read_text()
        self.assertIn('const math = @import("std").math;', zig)
        self.assertIn('const nan = math.nan(f64);', zig)

    def test_copied_and_embedded_input_integrity(self):
        shared = MASTER._load_literal_arrays(DIRECTORY.parent / 'test_testdata.py')
        for name, values in shared.items():
            self.assertEqual(INPUTS[name], values, name)
            self.assertEqual(len(values), 252)
        tree = ast.parse((DIRECTORY / (SLUG + '.py')).read_text())
        for name in MASTER.REQUIRED_INPUTS:
            assignment = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                              and any(isinstance(target, ast.Name) and target.id == name
                                      for target in node.targets))
            self.assertEqual(ast.literal_eval(assignment.value), shared[name])

    def test_causality_and_reset(self):
        first, second = instance(), instance()
        actual = run(first, INPUTS, 252)
        prefix = run(second, INPUTS, 90)
        for field in range(4):
            assert_values(self, [row[field] for row in prefix], [row[field] for row in actual[:90]], 0.0)
        first.reset()
        self.assertFalse(first.is_primed)
        repeated = run(first, INPUTS, 252)
        for field in range(4):
            assert_values(self, [row[field] for row in repeated], [row[field] for row in actual], 0.0)

    def test_rejected_nonfinite_input_does_not_advance_state(self):
        first, second = instance(), instance()
        run(first, INPUTS, 30)
        run(second, INPUTS, 30)
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                reject(first, value)
        a, b = feed(first, 31), feed(second, 31)
        assert_values(self, list(a), list(b), 0.0)

    def test_full_precision_smoother_policy(self):
        a = MASTER.UltimateSmoother(20)
        outputs = [a.update(price) for price in INPUTS['INPUT_CLOSE']]
        self.assertEqual(outputs, article_batch(INPUTS['INPUT_CLOSE'], 20))
        self.assertNotEqual(outputs[3:], article_batch(INPUTS['INPUT_CLOSE'],20,False)[3:])

    def test_first_bar_and_gaps_use_previous_close(self):
        i = MASTER.UltimateChannel()
        self.assertEqual(i.update(100,101,99), (100,2,102,98))
        self.assertEqual(i.update(111,112,110), (111,12,123,99))
        self.assertEqual(i.update(90,91,89), (90,22,112,68))
        self.assertEqual(i.warmup_bars, 0)
        self.assertTrue(i.is_primed)

    def test_channel_multiplier_and_independent_periods(self):
        a = MASTER._run_case(MASTER.ReferenceCase(20,5,1,''), INPUTS)
        b = MASTER._run_case(MASTER.ReferenceCase(20,5,2,''), INPUTS)
        c = MASTER._run_case(MASTER.ReferenceCase(20,5,0,''), INPUTS)
        d = MASTER._run_case(MASTER.ReferenceCase(20,20,1,''), INPUTS)
        self.assertEqual([r.center for r in a], [r.center for r in d])
        self.assertNotEqual([r.smoothed_true_range for r in a], [r.smoothed_true_range for r in d])
        for r,s,t in zip(a,b,c):
            self.assertEqual(r.center,s.center)
            self.assertEqual(r.smoothed_true_range,s.smoothed_true_range)
            self.assertAlmostEqual(s.upper-s.center, 2*(r.upper-r.center), places=11)
            self.assertEqual(t.upper,t.center)
            self.assertEqual(t.lower,t.center)

    def test_negative_str_is_not_clamped_or_sorted(self):
        i = MASTER.UltimateChannel(20,20,1)
        for _ in range(50):
            i.update(100,150,50)
        values = [i.update(100,100,100) for _ in range(80)]
        reversed_bounds = [row for row in values if row.smoothed_true_range < 0]
        self.assertTrue(reversed_bounds)
        self.assertTrue(all(row.upper < row.lower for row in reversed_bounds))

    def test_invalid_parameters_and_bars(self):
        for period in (0,0.5,math.inf,math.nan):
            with self.assertRaises(ValueError):
                MASTER.UltimateChannel(length=period)
            with self.assertRaises(ValueError):
                MASTER.UltimateChannel(str_length=period)
        for multiplier in (-1,math.nan,math.inf):
            with self.assertRaises(ValueError):
                MASTER.UltimateChannel(num_strs=multiplier)
        a,b = instance(),instance()
        run(a,INPUTS,30)
        run(b,INPUTS,30)
        for bar in ((100,99,98),(100,101,102),(100,math.nan,99)):
            with self.assertRaises(ValueError):
                a.update(*bar)
        assert_values(self,list(feed(a,30)),list(feed(b,30)),0.0)

    def test_constant_price_and_range_are_preserved(self):
        i = MASTER.UltimateChannel()
        for _ in range(252):
            result = i.update(-10,-9,-11)
            assert_values(self,list(result),[-10,2,-8,-12],1e-11)


if __name__ == '__main__':
    unittest.main()
