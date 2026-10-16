"""Article-expression and cross-language fixture verification; standard Python."""

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
SLUG = 'ultimate-bands'
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
    closes = arrays['INPUT_CLOSE']
    centers = article_batch(closes, case.length)
    text = COMPOSITE_ARTICLE.read_text()
    term = re.search(r'Sum = Sum \+ (.*?);', text).group(1)
    term = term.replace('Close[count]', 'price').replace('Smooth[count]', 'smooth')
    terms = [eval(term, {'__builtins__':{}}, {'price':price, 'smooth':smooth})
             for price,smooth in zip(closes,centers)]
    formulas = [re.search(name+r' = (.*?);',text).group(1)
                for name in ('UpperBand','LowerBand')]
    results = []
    sd = 0.0
    for t,center in enumerate(centers):
        if t < case.length-1:
            results.append((center,math.nan,math.nan,math.nan))
            continue
        total = 0.0
        for offset in range(case.length):
            total = total + terms[t-offset]
        if total != 0:
            sd = math.sqrt(total/case.length)
        results.append((center,sd,*(eval(expression,{'__builtins__':{}},
               {'Smooth':center,'NumSDs':case.num_sds,'SD':sd}) for expression in formulas)))
    return results


def instance():
    return MASTER.UltimateBands()


def feed(indicator, index):
    return indicator.update(INPUTS['INPUT_CLOSE'][index])


def run(indicator, arrays, count):
    return [indicator.update(c) for c in arrays['INPUT_CLOSE'][:count]]


def reject(indicator, value):
    indicator.update(value)


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

    def test_exact_priming_for_all_confirmed_lengths(self):
        for case in MASTER.REFERENCE_CASES:
            i = MASTER.UltimateBands(case.length,case.num_sds)
            self.assertEqual(i.warmup_bars,case.length-1)
            for t,price in enumerate(INPUTS['INPUT_CLOSE']):
                row = i.update(price)
                self.assertTrue(math.isfinite(row.center))
                self.assertEqual(i.is_primed,t>=case.length-1)
                self.assertEqual(math.isnan(row.standard_deviation),t<case.length-1)
                self.assertEqual(math.isnan(row.upper),t<case.length-1)
                self.assertEqual(math.isnan(row.lower),t<case.length-1)

    def test_full_window_of_pass_through_residuals_is_zero(self):
        for length in (1,2,3):
            i = MASTER.UltimateBands(length)
            rows = [i.update(price) for price in (10,12,11)[:length]]
            self.assertEqual(rows[-1].standard_deviation,0)
            self.assertEqual(rows[-1].upper,rows[-1].center)
            self.assertEqual(rows[-1].lower,rows[-1].center)

    def test_nonzero_residual_mean_uses_rms_not_centered_stdev(self):
        length = 5
        # An abrupt step produces a pronounced nonzero residual mean, making
        # the RMS/centered-stdev distinction a meaningful regression oracle.
        prices = [0.0] * 3 + [100.0] * 10
        centers = article_batch(prices,length)
        indicator = MASTER.UltimateBands(length)
        rows = [indicator.update(price) for price in prices]
        t = 4
        residuals = [prices[k]-centers[k] for k in range(t-length+1,t+1)]
        mean = sum(residuals)/length
        rms = math.sqrt(sum(e*e for e in residuals)/length)
        stdev = math.sqrt(sum((e-mean)**2 for e in residuals)/length)
        self.assertGreater(abs(mean),0.01)
        self.assertAlmostEqual(rows[t].standard_deviation,rms,places=12)
        self.assertGreater(abs(rms-stdev),0.01)

    def test_conditional_zero_sum_retains_previous_sd(self):
        # Controlled centers make an exact all-zero window after nonzero RMS.
        # This isolates the source's conditional assignment from IIR roundoff.
        class ControlledCenter:
            def __init__(self):
                self.values = iter([10,9,10])
            def update(self,close):
                return next(self.values)
        i = MASTER.UltimateBands(1)
        i._center_filter = ControlledCenter()
        a,b,c = [i.update(10) for _ in range(3)]
        self.assertEqual(a.standard_deviation,0)
        self.assertEqual(b.standard_deviation,1)
        self.assertEqual(c.standard_deviation,1)
        self.assertEqual((c.upper,c.lower),(11,9))

    def test_multiplier_scaling_preserves_sd_and_warmup(self):
        rows = [run(MASTER.UltimateBands(20,m),INPUTS,252) for m in (0,0.5,1,2)]
        for t in range(252):
            if t < 19:
                self.assertTrue(all(math.isnan(r[t].upper) for r in rows))
            else:
                a,b,c,d = [r[t] for r in rows]
                self.assertEqual(a.standard_deviation,c.standard_deviation)
                self.assertEqual(a.upper,a.center)
                self.assertEqual(a.lower,a.center)
                self.assertAlmostEqual(b.upper-b.center,0.5*(c.upper-c.center),places=11)
                self.assertAlmostEqual(d.upper-d.center,2*(c.upper-c.center),places=11)

    def test_invalid_integer_windows_and_multipliers(self):
        for length in (0,-1,1.5,20.0,True,math.nan,math.inf):
            with self.assertRaises(ValueError):
                MASTER.UltimateBands(length)
        for multiplier in (-1,math.nan,math.inf):
            with self.assertRaises(ValueError):
                MASTER.UltimateBands(num_sds=multiplier)

    def test_zero_price_and_squares_ring_bound(self):
        i = MASTER.UltimateBands(5)
        for t in range(300):
            r = i.update(0)
            self.assertEqual(r.center,0)
            self.assertLessEqual(len(i._squares),5)
            if t >= 4:
                self.assertEqual(r,(0,0,0,0))


if __name__ == '__main__':
    unittest.main()
