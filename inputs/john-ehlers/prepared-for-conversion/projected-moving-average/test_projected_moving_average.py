"""Independent article-expression, analytic and cross-language PMA checks."""

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
ARTICLE = DIRECTORY.parent.parent/'tasc/2025-03-removing-moving-average-lag/content.md'
SPEC = importlib.util.spec_from_file_location('pma_master',DIRECTORY/'projected-moving-average.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
ARRAYS = MASTER._load_literal_arrays(DIRECTORY/'test_testdata.py')
CLOSE = ARRAYS['INPUT_CLOSE']


def article_batch(prices,length):
    """Execute independently extracted source expressions in batch form.

    Actual full windows and prior valid slopes define standalone availability;
    formulas are neither copied from nor calculated by the streaming class.
    """
    blocks = re.findall(r'```easylanguage\n(.*?)```',ARTICLE.read_text(),re.DOTALL)
    function = next(block for block in blocks if 'Projected Moving Average Function' in block)
    accumulator_expressions = {}
    for name in ('Sx','Sy','Sxx','Syy','Sxy'):
        expression = re.search(name+r' = '+name+r' \+ (.*?);',function).group(1)
        accumulator_expressions[name] = expression.replace('Price[count - 1]','price')
    formulas = {name:re.search(r'\b'+name+r' = (.*?);',function).group(1)
                for name in ('Slope','SMA','PMA')}
    pred_block = next(block for block in blocks if 'Predict = PMA +' in block)
    slope_block = next(block for block in blocks if 'Predict = 1.5*Slope' in block)
    prediction = re.search(r'Predict = (.*?);',pred_block).group(1).replace('Slope[2]','old_slope')
    slope_prediction = re.search(r'Predict = (.*?);',slope_block).group(1).replace('Slope[4]','old_slope')
    results = []
    for t in range(len(prices)):
        if t < length-1:
            results.append((math.nan,)*5)
            continue
        values = {'Sx':0.0,'Sy':0.0,'Sxx':0.0,'Syy':0.0,'Sxy':0.0,'Length':length}
        for count in range(1,length+1):
            values.update(count=count,price=prices[t-count+1])
            for name,expression in accumulator_expressions.items():
                values[name] = values[name] + eval(expression,{'__builtins__':{}},values)
        for name,expression in formulas.items():
            values[name] = eval(expression,{'__builtins__':{}},values)
        pred = math.nan
        spred = math.nan
        if t>=length+1:
            values['old_slope'] = results[t-2][1]
            pred = eval(prediction,{'__builtins__':{}},values)
        if t>=length+3:
            values['old_slope'] = results[t-4][1]
            spred = eval(slope_prediction,{'__builtins__':{}},values)
        results.append((values['PMA'],values['Slope'],pred,spred,values['SMA']))
    return results


def assert_values(test,actual,expected,tolerance=5e-13):
    test.assertEqual(len(actual),len(expected))
    for index,(a,e) in enumerate(zip(actual,expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a),(index,a,e))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a,e,rel_tol=tolerance,
                                                            abs_tol=tolerance),(index,a,e))


class PMATests(unittest.TestCase):
    def test_all_fields_match_independent_source_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            actual = MASTER._run_case(case,ARRAYS)
            oracle = article_batch(CLOSE,case.length)
            for field in range(5):
                assert_values(self,[row[field] for row in actual],[row[field] for row in oracle],0.0)

    def test_exact_field_priming_for_all_lengths(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.ProjectedMovingAverage(case.length)
            starts = [case.length-1,case.length-1,case.length+1,case.length+3,case.length-1]
            self.assertEqual(indicator.warmup_bars,case.length-1)
            self.assertEqual(indicator.prediction_warmup_bars,case.length+1)
            self.assertEqual(indicator.slope_prediction_warmup_bars,case.length+3)
            for t,price in enumerate(CLOSE):
                result = indicator.update(price)
                for field,start in enumerate(starts):
                    self.assertEqual(math.isnan(result[field]),t<start)
                self.assertEqual(indicator.is_primed,t>=case.length-1)
                self.assertEqual(indicator.is_prediction_primed,t>=case.length+1)
                self.assertEqual(indicator.is_slope_prediction_primed,t>=case.length+3)

    def test_constant_prices_preserve_mean_and_zero_slope(self):
        for length in (2,20,200):
            indicator = MASTER.ProjectedMovingAverage(length)
            for _ in range(length+5):
                result = indicator.update(-10.0)
            self.assertEqual(result,(-10,0,-10,0,-10))

    def test_linear_ramp_projects_a_half_bar_beyond_today(self):
        for length in (2,3,20,200):
            indicator = MASTER.ProjectedMovingAverage(length)
            for t in range(length+6):
                price = 10+1.5*t
                result = indicator.update(price)
                if t>=length-1:
                    self.assertEqual(result.slope,1.5)
                    self.assertEqual(result.pma,price+0.75)
                    self.assertEqual(result.sma,price-1.5*(length-1)/2)
                if t>=length+1:
                    self.assertEqual(result.prediction,result.pma)
                if t>=length+3:
                    self.assertEqual(result.slope_prediction,1.5)

    def test_two_point_endpoint_intercept_and_source_pma_differ(self):
        indicator = MASTER.ProjectedMovingAverage(2)
        indicator.update(1)
        result = indicator.update(3)
        self.assertEqual((result.pma,result.slope,result.sma),(4,2,2))
        fitted_latest = result.sma+result.slope*(2-1)/2
        fitted_intercept = result.sma+result.slope*(2+1)/2
        self.assertEqual(fitted_latest,3)
        self.assertEqual(fitted_intercept,5)
        self.assertNotEqual(result.pma,fitted_latest)
        self.assertNotEqual(result.pma,fitted_intercept)

    def test_quadratic_price_checks_two_and_four_bar_prediction_lags(self):
        length = 4
        indicator = MASTER.ProjectedMovingAverage(length)
        for t in range(30):
            result = indicator.update(t*t)
            if t>=length+3:
                self.assertEqual(result.slope,2*t-(length-1))
                self.assertEqual(result.prediction-result.pma,2*length)
                self.assertEqual(result.slope_prediction-result.slope,4)

    def test_derived_fir_weights_match_literal_pma(self):
        for length in (2,5,20,200):
            weights = [1/length+3*(length-1-2*j)/(length*length-1) for j in range(length)]
            self.assertAlmostEqual(sum(weights),1,places=12)
            self.assertAlmostEqual(sum(j*w for j,w in enumerate(weights)),-0.5,places=10)
            indicator = MASTER.ProjectedMovingAverage(length)
            for t,price in enumerate(CLOSE):
                result = indicator.update(price)
                if t>=length-1:
                    weighted = sum(w*CLOSE[t-j] for j,w in enumerate(weights))
                    self.assertTrue(math.isclose(result.pma,weighted,rel_tol=5e-12,abs_tol=5e-12))

    def test_causal_prefix_and_reset(self):
        full = MASTER._run_case(MASTER.ReferenceCase(20,''),ARRAYS)
        indicator = MASTER.ProjectedMovingAverage()
        changed = [indicator.update(p) for p in CLOSE[:120]+[1000]*132]
        for field in range(5):
            assert_values(self,[row[field] for row in full[:120]],[row[field] for row in changed[:120]],0.0)
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertFalse(indicator.is_prediction_primed)
        self.assertFalse(indicator.is_slope_prediction_primed)
        repeated = [indicator.update(p) for p in CLOSE]
        for field in range(5):
            assert_values(self,[row[field] for row in full],[row[field] for row in repeated],0.0)

    def test_invalid_window_and_price_preserve_state(self):
        for length in (0,1,-2,2.5,20.0,True,math.nan,math.inf):
            with self.assertRaises(ValueError): MASTER.ProjectedMovingAverage(length)
        a,b = MASTER.ProjectedMovingAverage(),MASTER.ProjectedMovingAverage()
        for p in CLOSE[:80]: a.update(p); b.update(p)
        for p in (math.nan,math.inf,-math.inf):
            with self.assertRaises(ValueError): a.update(p)
        actual,expected = [a.update(p) for p in CLOSE[80:]],[b.update(p) for p in CLOSE[80:]]
        for field in range(5):
            assert_values(self,[row[field] for row in actual],[row[field] for row in expected],0.0)

    def test_history_memory_is_bounded(self):
        indicator = MASTER.ProjectedMovingAverage(5)
        for t in range(500):
            indicator.update(t%11)
            self.assertLessEqual(len(indicator._prices),5)
            self.assertLessEqual(len(indicator._slopes),4)

    def test_copied_inputs_and_embedded_closes(self):
        shared = MASTER._load_literal_arrays(DIRECTORY.parent/'test_testdata.py')
        for name,values in shared.items():
            self.assertEqual(ARRAYS[name],values)
            self.assertEqual(len(values),252)
        tree = ast.parse((DIRECTORY/'projected-moving-average.py').read_text())
        assignment = next(node for node in ast.walk(tree) if isinstance(node,ast.Assign)
                          and any(isinstance(target,ast.Name) and target.id=='INPUT_CLOSE' for target in node.targets))
        self.assertEqual(ast.literal_eval(assignment.value),CLOSE)

    def test_every_python_expected_array_and_comment(self):
        names = set()
        text = (DIRECTORY/'test_testdata.py').read_text()
        for case in MASTER.REFERENCE_CASES:
            outputs = MASTER._run_case(case,ARRAYS)
            for field,token in zip(MASTER.OUTPUT_FIELDS,MASTER.OUTPUT_TOKENS):
                name = 'EXPECTED_'+MASTER._case_suffix(case)+'_'+token
                names.add(name)
                assert_values(self,[getattr(row,field) for row in outputs],ARRAYS[name])
                self.assertEqual(len(ARRAYS[name]),252)
                comments = f'# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\n{name} = ['
                self.assertIn(comments,text)
        self.assertEqual(names,{name for name in ARRAYS if name.startswith('EXPECTED_')})
        self.assertEqual(len(names),60)
        self.assertTrue(all(math.isnan(v) for v in ARRAYS['EXPECTED_L252_PREDICTION']))
        self.assertTrue(all(math.isnan(v) for v in ARRAYS['EXPECTED_L252_SLOPE_PREDICTION']))

    def test_every_translated_value_comment_and_nan_position(self):
        patterns = {
            'testdata_test.go':r'var expected(\w+) = \[\]float64\{\s*(.*?)\n\}',
            'testdata.ts':r'export const expected(\w+): number\[\] = \[\s*(.*?)\n\];',
            'testdata.rs':r'pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[\s*(.*?)\n\s*\]\s*\}',
            'testdata.zig':r'pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{\s*(.*?)\n\s*\};\s*\}',
        }
        nans = {'testdata_test.go':'math.NaN()','testdata.ts':'NaN',
                'testdata.rs':'f64::NAN','testdata.zig':'nan'}
        # Explicit mapping avoids confusing SLOPE and SLOPE_PREDICTION suffixes.
        cases = {MASTER._case_suffix(case)+'_'+token:case for case in MASTER.REFERENCE_CASES for token in MASTER.OUTPUT_TOKENS}
        for filename,pattern in patterns.items():
            text = (DIRECTORY/filename).read_text()
            matches = list(re.finditer(pattern,text,re.DOTALL))
            self.assertEqual(len(matches),60)
            for match in matches:
                suffix,body = match.groups()
                values = [math.nan if token.strip()==nans[filename] else float(token.strip())
                          for token in body.split(',') if token.strip()]
                assert_values(self,values,ARRAYS['EXPECTED_'+suffix.upper()],0.0)
                case = cases[suffix.upper()]
                comments = f'// {case.what_it_tests}\n// {MASTER._parameter_comment(case)}\n'
                self.assertTrue(text[:match.start()].endswith(comments))
        self.assertIn('package projectedmovingaverage',(DIRECTORY/'testdata_test.go').read_text())
        self.assertIn('import "math"',(DIRECTORY/'testdata_test.go').read_text())
        self.assertIn('const nan = math.nan(f64);',(DIRECTORY/'testdata.zig').read_text())


if __name__=='__main__':
    unittest.main()
