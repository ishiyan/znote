"""Independent article calculation and five-language fixture validation."""

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
ARTICLE = DIRECTORY.parent.parent / 'tasc/2024-11-ultimate-strength-index-(usi)/content.md'
SPEC = importlib.util.spec_from_file_location('usi_master',DIRECTORY/'ultimate-strength-index.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
ARRAYS = MASTER._load_literal_arrays(DIRECTORY/'test_testdata.py')
CLOSE = ARRAYS['INPUT_CLOSE']


def article_batch(prices, period, full_precision=True):
    """Independent batch evaluation of the actual article's expressions.

    The article is not imported or executed as a program. Only its coefficient
    assignments and US recurrence are extracted. The selected precision policy
    explicitly substitutes sqrt(2) and pi, and converts the cosine to radians.
    full_precision=False evaluates the original printed coefficients instead.
    """
    blocks = re.findall(r"```easylanguage\n(.*?)```", ARTICLE.read_text(), flags=re.DOTALL)
    block = next(block for block in blocks if "$UltimateSmoother = US;" in block)
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


def article_usi(prices, length):
    """Batch oracle from source expressions, not from the streaming classes.

    Explicitly align standalone seed choices: no first-bar movement, prior
    strengths zero, averages divided by four from startup, initial USI zero.
    """
    up, down = [0.0], [0.0]
    for t in range(1,len(prices)):
        up.append(prices[t]-prices[t-1] if prices[t]>prices[t-1] else 0.0)
        down.append(prices[t-1]-prices[t] if prices[t]<prices[t-1] else 0.0)
    def averages(strengths):
        result = []
        for t in range(len(strengths)):
            total = 0.0
            for lag in range(4):
                total = total + (strengths[t-lag] if t-lag>=0 else 0.0)
            result.append(total/4)
        return result
    usu,usd = article_batch(averages(up),length),article_batch(averages(down),length)
    blocks = re.findall(r'```easylanguage\n(.*?)```',ARTICLE.read_text(),re.DOTALL)
    block = next(block for block in blocks if 'Ultimate Strength Index (USI)' in block)
    guard,ratio = re.search(r'If \((.*?)\) Then\s+USI = (.*?);',block,re.DOTALL).groups()
    guard = guard.replace('<>','!=')
    outputs = []
    previous = 0.0
    for u,d in zip(usu,usd):
        context = {'USU':u,'USD':d}
        if eval(guard,{'__builtins__':{}},context):
            previous = eval(ratio,{'__builtins__':{}},context)
        outputs.append(previous)
    return outputs


class USITests(unittest.TestCase):
    def test_every_case_matches_independent_source_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.UltimateStrengthIndex(case.length)
            self.assertEqual([indicator.update(c) for c in CLOSE],article_usi(CLOSE,case.length))

    def test_defined_startup_and_first_acceptance(self):
        indicator = MASTER.UltimateStrengthIndex()
        self.assertFalse(indicator.is_primed)
        self.assertEqual(indicator.warmup_bars,0)
        first,second,third = [indicator.update(c) for c in CLOSE[:3]]
        self.assertEqual((first,second),(0.0,0.0))
        self.assertTrue(indicator.is_primed)
        self.assertAlmostEqual(third,(3.315-0.44)/(3.315+0.44),places=12)
        # The seed is zero movement, not a gain measured from zero price.
        self.assertEqual(indicator._up_history[0],0)

    def test_fixed_divisor_preaverage_and_filter_startup(self):
        indicator = MASTER.UltimateStrengthIndex(14)
        for index,close in enumerate([10,14,12,16]):
            indicator.update(close)
            self.assertEqual(indicator._up_filter._count,index+1)
            self.assertEqual(indicator._down_filter._count,index+1)
        self.assertEqual(indicator._up_filter._price1,2.0)
        self.assertEqual(indicator._down_filter._price1,0.5)
        # The prior inputs are 4/4 and 2/4, not partial-window divisors.
        self.assertEqual(indicator._up_filter._price2,1.0)
        self.assertEqual(indicator._down_filter._price2,0.5)
        self.assertNotEqual(indicator._up_filter._output1,indicator._up_filter._price1)

    def test_strict_thresholds_and_all_failed_guards_hold(self):
        class ControlledFilter:
            def __init__(self,values):
                self.values = iter(values)
                self.count = 0
            def update(self,value):
                self.count += 1
                return next(self.values)
        indicator = MASTER.UltimateStrengthIndex()
        # Accepted ratio, equality in each threshold, zero sum, negative path,
        # then accepted ratio again. Control isolates exact boundary conditions.
        up = ControlledFilter([0.03,0.01,0.02,1.0,-0.2,0.04])
        down = ControlledFilter([0.02,0.02,0.01,-1.0,0.1,0.02])
        indicator._up_filter,indicator._down_filter = up,down
        values = [indicator.update(100+i) for i in range(6)]
        self.assertAlmostEqual(values[0],0.2)
        self.assertEqual(values[:5],[values[0]]*5)
        self.assertAlmostEqual(values[5],1/3)
        self.assertEqual((up.count,down.count),(6,6))
        self.assertEqual(indicator._previous_close,105)

    def test_flat_and_one_direction_records_hold_zero(self):
        for prices in ([5.0]*200,list(range(200)),list(range(200,0,-1))):
            indicator = MASTER.UltimateStrengthIndex()
            self.assertEqual([indicator.update(c) for c in prices],[0.0]*len(prices))

    def test_output_range_and_ring_storage_for_all_cases(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.UltimateStrengthIndex(case.length)
            for close in CLOSE:
                value = indicator.update(close)
                self.assertTrue(math.isfinite(value) and -1<=value<=1)
                self.assertEqual(len(indicator._up_history),4)
                self.assertEqual(len(indicator._down_history),4)

    def test_scale_threshold_changes_update_behavior(self):
        # A tiny record stays below the absolute 0.01 strength thresholds.
        tiny = MASTER.UltimateStrengthIndex()
        values = [tiny.update(c*1e-8) for c in CLOSE]
        self.assertEqual(values,[0.0]*252)
        normal = MASTER.UltimateStrengthIndex()
        self.assertTrue(any(normal.update(c)!=0 for c in CLOSE))

    def test_price_translation_preserves_changes(self):
        # Integer-valued synthetic prices preserve the exact subtraction on
        # translation, avoiding the unrelated decimal binary64 subtraction.
        prices = [100+(t%7)-(t%3) for t in range(200)]
        a,b = MASTER.UltimateStrengthIndex(),MASTER.UltimateStrengthIndex()
        self.assertEqual([a.update(c) for c in prices],[b.update(c+1000) for c in prices])

    def test_causal_prefix_and_reset(self):
        full = MASTER.UltimateStrengthIndex()
        values = [full.update(c) for c in CLOSE]
        prefix = MASTER.UltimateStrengthIndex()
        self.assertEqual([prefix.update(c) for c in CLOSE[:70]],values[:70])
        changed = MASTER.UltimateStrengthIndex()
        changed_values = [changed.update(c) for c in CLOSE[:70]+[1000.0]*182]
        self.assertEqual(changed_values[:70],values[:70])
        full.reset()
        self.assertFalse(full.is_primed)
        self.assertEqual([full.update(c) for c in CLOSE],values)

    def test_invalid_parameters_and_input_preserve_state(self):
        for length in (0,0.5,-1,math.nan,math.inf,-math.inf):
            with self.assertRaises(ValueError):
                MASTER.UltimateStrengthIndex(length)
        a,b = MASTER.UltimateStrengthIndex(),MASTER.UltimateStrengthIndex()
        for close in CLOSE[:30]:
            self.assertEqual(a.update(close),b.update(close))
        for close in (math.nan,math.inf,-math.inf):
            with self.assertRaises(ValueError):
                a.update(close)
        self.assertEqual([a.update(c) for c in CLOSE[30:]],[b.update(c) for c in CLOSE[30:]])

    def test_fractional_length_and_full_precision(self):
        a,b = MASTER.UltimateStrengthIndex(28.5),MASTER.UltimateStrengthIndex(28)
        self.assertNotEqual([a.update(c) for c in CLOSE],[b.update(c) for c in CLOSE])
        full = article_batch(CLOSE,14)
        printed = article_batch(CLOSE,14,False)
        self.assertNotEqual(full[3:],printed[3:])
        self.assertEqual(MASTER.PI,math.pi)
        self.assertEqual(MASTER.SQRT_TWO,math.sqrt(2))

    def test_copied_input_and_embedded_close_integrity(self):
        shared = MASTER._load_literal_arrays(DIRECTORY.parent/'test_testdata.py')
        for name,values in shared.items():
            self.assertEqual(ARRAYS[name],values)
            self.assertEqual(len(values),252)
        tree = ast.parse((DIRECTORY/'ultimate-strength-index.py').read_text())
        assignment = next(node for node in ast.walk(tree) if isinstance(node,ast.Assign)
                          and any(isinstance(target,ast.Name) and target.id=='INPUT_CLOSE' for target in node.targets))
        self.assertEqual(ast.literal_eval(assignment.value),CLOSE)

    def test_all_python_reference_arrays(self):
        names = {'EXPECTED_'+MASTER._case_suffix(case) for case in MASTER.REFERENCE_CASES}
        self.assertEqual(names,{name for name in ARRAYS if name.startswith('EXPECTED_')})
        for case in MASTER.REFERENCE_CASES:
            name = 'EXPECTED_'+MASTER._case_suffix(case)
            expected = ARRAYS[name]
            self.assertEqual(len(expected),252)
            comments = f'# {case.what_it_tests}\n# length={case.length:g}\n{name} = ['
            self.assertIn(comments,(DIRECTORY/'test_testdata.py').read_text())
            indicator = MASTER.UltimateStrengthIndex(case.length)
            for c,value in zip(CLOSE,expected):
                self.assertTrue(math.isfinite(value))
                self.assertTrue(math.isclose(indicator.update(c),value,rel_tol=5e-13,abs_tol=5e-13))

    def test_every_translated_literal_and_comment(self):
        patterns = {
            'testdata_test.go':r'var expected(\w+) = \[\]float64\{\s*(.*?)\n\}',
            'testdata.ts':r'export const expected(\w+): number\[\] = \[\s*(.*?)\n\];',
            'testdata.rs':r'pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[\s*(.*?)\n\s*\]\s*\}',
            'testdata.zig':r'pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{\s*(.*?)\n\s*\};\s*\}',
        }
        for filename,pattern in patterns.items():
            text = (DIRECTORY/filename).read_text()
            matches = list(re.finditer(pattern,text,re.DOTALL))
            self.assertEqual(len(matches),12)
            for match in matches:
                suffix,body = match.groups()
                self.assertEqual([float(token.strip()) for token in body.split(',') if token.strip()],ARRAYS['EXPECTED_'+suffix.upper()])
                case = next(case for case in MASTER.REFERENCE_CASES if MASTER._case_suffix(case)==suffix.upper())
                comments = f'// {case.what_it_tests}\n// length={case.length:g}\n'
                self.assertTrue(text[:match.start()].endswith(comments))
        self.assertIn('package ultimatestrengthindex',(DIRECTORY/'testdata_test.go').read_text())
        self.assertIn('import "math"',(DIRECTORY/'testdata_test.go').read_text())
        self.assertIn('const nan = math.nan(f64);',(DIRECTORY/'testdata.zig').read_text())


if __name__ == '__main__':
    unittest.main()
