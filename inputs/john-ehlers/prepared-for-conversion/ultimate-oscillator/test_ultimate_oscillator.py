"""Independent source-expression, analytic and fixture verification."""

import ast
import cmath
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
ARTICLE = DIRECTORY.parent.parent/'tasc/2025-04-the-ultimate-oscillator/content.md'
SPEC = importlib.util.spec_from_file_location('uo_master',DIRECTORY/'ultimate-oscillator.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
ARRAYS = MASTER._load_literal_arrays(DIRECTORY/'test_testdata.py')
CLOSE = ARRAYS['INPUT_CLOSE']


def article_highpass(prices, period, full_precision=True):
    """Independent batch evaluation of the actual article's expressions.

    The article is not imported or executed as a program. Only its coefficient
    assignments and US recurrence are extracted. The selected precision policy
    explicitly substitutes sqrt(2) and pi, and converts the cosine to radians.
    full_precision=False evaluates the original printed coefficients instead.
    """
    blocks = re.findall(r"```easylanguage\n(.*?)```", ARTICLE.read_text(), flags=re.DOTALL)
    block = next(block for block in blocks if "Highpass Function" in block)
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
    recurrence = re.search(r"If CurrentBar >= 4 Then\s+\$HighPass = (.*?);", block, flags=re.DOTALL).group(1)
    recurrence = recurrence.replace("Price[1]", "price1").replace("Price[2]", "price2")
    recurrence = recurrence.replace("$HighPass[1]", "us1").replace("$HighPass[2]", "us2")
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
            outputs.append(0.0)
        else:
            values.update(Price=price, price1=prices[t-1], price2=prices[t-2],
                          us1=outputs[t-1], us2=outputs[t-2])
            outputs.append(eval(recurrence, {"__builtins__": {}}, values))
    return outputs


def article_oscillator(prices,edge,width):
    """Independent batch execution of the three article definitions.

    The oracle explicitly uses a full-window-only standalone RMS. Filter
    constants are substituted as documented; the extracted recurrence and
    newest-first RMS expression otherwise remain those in the source.
    """
    hp1 = article_highpass(prices,width*edge)
    hp2 = article_highpass(prices,edge)
    signal = [a-b for a,b in zip(hp1,hp2)]
    blocks = re.findall(r'```easylanguage\n(.*?)```',ARTICLE.read_text(),re.DOTALL)
    rms_block = next(block for block in blocks if 'RMS Function' in block)
    term = re.search(r'SumSq = SumSq \+ (.*?);',rms_block).group(1)
    term = term.replace('Price[count]','value')
    squares = [eval(term,{'__builtins__':{}},{'value':value}) for value in signal]
    rms_expression = re.search(r'If SumSq <> 0 Then \$RMS = (.*?);',rms_block).group(1)
    oscillator_block = next(block for block in blocks if 'Ultimate Oscillator Indicator' in block)
    ratio = re.search(r'If RMS <> 0 Then UltimateOsc = (.*?);',oscillator_block).group(1)
    outputs = []
    rms,previous = 0.0,0.0
    for t,value in enumerate(signal):
        if t < 99:
            outputs.append(math.nan)
            continue
        total = 0.0
        for lag in range(100):
            total = total + squares[t-lag]
        if total != 0:
            rms = eval(rms_expression,{'__builtins__':{}},
                       {'SquareRoot':math.sqrt,'SumSq':total,'Length':100})
        if rms != 0:
            previous = eval(ratio,{'__builtins__':{}},{'Signal':value,'RMS':rms})
        outputs.append(previous)
    return outputs


def assert_values(test,actual,expected,tolerance=5e-13):
    test.assertEqual(len(actual),len(expected))
    for index,(a,e) in enumerate(zip(actual,expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a),(index,a,e))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a,e,rel_tol=tolerance,
                                                            abs_tol=tolerance),(index,a,e))


class UltimateOscillatorTests(unittest.TestCase):
    def test_all_cases_match_independent_article_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.UltimateOscillator(case.band_edge,case.bandwidth)
            actual = [indicator.update(price) for price in CLOSE]
            assert_values(self,actual,article_oscillator(CLOSE,case.band_edge,case.bandwidth),0.0)

    def test_highpass_first_three_zeros_and_fourth_recursion(self):
        hp = MASTER.HighPass(20)
        actual = [hp.update(c) for c in CLOSE[:4]]
        self.assertEqual(actual[:3],[0,0,0])
        self.assertEqual(actual,article_highpass(CLOSE[:4],20))
        self.assertNotEqual(actual[3],0)
        self.assertEqual(hp._price1,CLOSE[3])
        self.assertEqual(hp._price2,CLOSE[2])

    def test_full_rms_warmup_for_every_confirmed_case(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.UltimateOscillator(case.band_edge,case.bandwidth)
            self.assertFalse(indicator.is_primed)
            self.assertEqual(indicator.warmup_bars,99)
            for t,price in enumerate(CLOSE):
                value = indicator.update(price)
                self.assertEqual(indicator.is_primed,t>=99)
                self.assertEqual(math.isnan(value),t<99)
                self.assertEqual(indicator._long_filter._count,t+1)
                self.assertEqual(indicator._short_filter._count,t+1)
            self.assertEqual(len(indicator._rms_filter._squares),100)

    def test_constant_and_linear_ramp_have_zero_primed_output(self):
        # Double DC zeros annihilate a ramp when initialized with zero HPs.
        for prices in ([25.0]*252,[10.0+0.5*t for t in range(252)]):
            indicator = MASTER.UltimateOscillator()
            values = [indicator.update(price) for price in prices]
            self.assertTrue(all(math.isnan(value) for value in values[:99]))
            self.assertEqual(values[99:],[0.0]*153)

    def test_parallel_highpass_sign_and_own_raw_inputs(self):
        indicator = MASTER.UltimateOscillator(20,3)
        hp1,hp2 = article_highpass(CLOSE,60),article_highpass(CLOSE,20)
        for t,price in enumerate(CLOSE):
            indicator.update(price)
            self.assertEqual(indicator._long_filter._price1,price)
            self.assertEqual(indicator._short_filter._price1,price)
            signal = hp1[t]-hp2[t]
            stored = indicator._rms_filter._squares[(indicator._rms_filter._next-1)%100]
            self.assertEqual(stored,signal*signal)

    def test_rms_uses_all_terms_and_retains_previous_on_zero_sum(self):
        rms = MASTER.RootMeanSquare(2)
        self.assertTrue(math.isnan(rms.update(3)))
        self.assertEqual(rms.update(4),math.sqrt((16+9)/2))
        self.assertEqual(rms.update(0),math.sqrt(16/2))
        self.assertEqual(rms.update(0),math.sqrt(16/2))
        rms.reset()
        self.assertFalse(rms.is_primed)
        self.assertTrue(math.isnan(rms.update(0)))
        self.assertEqual(rms.update(0),0)

    def test_final_zero_rms_condition_retains_previous_oscillator(self):
        # Controlled supporting paths isolate the source's final conditional.
        class FixedHP:
            def __init__(self,value): self.value=value
            def update(self,close): return self.value
        class ControlledRMS:
            is_primed = True
            def __init__(self): self.values=iter([2.0,0.0])
            def update(self,value): return next(self.values)
        indicator = MASTER.UltimateOscillator()
        indicator._long_filter,indicator._short_filter = FixedHP(4),FixedHP(0)
        indicator._rms_filter = ControlledRMS()
        self.assertEqual(indicator.update(10),2)
        self.assertEqual(indicator.update(11),2)

    def test_rms_is_not_centered_standard_deviation(self):
        rms = MASTER.RootMeanSquare(3)
        values = [rms.update(value) for value in (1,2,3)]
        self.assertEqual(values[-1],math.sqrt(14/3))
        self.assertNotEqual(values[-1],math.sqrt(2/3))

    def test_raw_nyquist_difference_is_rejected(self):
        long,short = MASTER.HighPass(40),MASTER.HighPass(20)
        signal = []
        for t in range(800):
            price = 1.0 if t%2==0 else -1.0
            signal.append(long.update(price)-short.update(price))
        self.assertLess(max(abs(value) for value in signal[-100:]),1e-12)
        # Normalization of a decaying signal need not also tend to zero.

    def test_raw_sine_matches_derived_frequency_response(self):
        omega = 2*math.pi/30
        q = cmath.exp(-1j*omega)
        def transfer(period):
            angle = math.sqrt(2)*math.pi/period
            a = math.exp(-angle)
            c2,c3 = 2*a*math.cos(angle),-a*a
            c1 = (1+c2-c3)/4
            return c1*(1-q)**2/(1-c2*q-c3*q*q)
        response = transfer(40)-transfer(20)
        long,short = MASTER.HighPass(40),MASTER.HighPass(20)
        for t in range(1200):
            actual = long.update(math.sin(omega*t))-short.update(math.sin(omega*t))
            if t>1000:
                expected = (response*cmath.exp(1j*omega*t)).imag
                self.assertAlmostEqual(actual,expected,places=11)

    def test_normalized_scale_translation_and_algebraic_bound(self):
        # Integer input values retain identical exact changes on translation.
        prices = [100+(t%11)-(t%7) for t in range(252)]
        a,b,c = (MASTER.UltimateOscillator() for _ in range(3))
        x = [a.update(p) for p in prices]
        y = [b.update(p+1000) for p in prices]
        z = [c.update(8*p) for p in prices]
        assert_values(self,x,y,1e-11)
        assert_values(self,x,z,1e-11)
        self.assertTrue(all(abs(value)<=10+1e-12 for value in x[99:]))
        self.assertTrue(any(abs(value)>1 for value in x[99:]))

    def test_causal_prefix_and_reset(self):
        indicator = MASTER.UltimateOscillator()
        full = [indicator.update(price) for price in CLOSE]
        prefix = MASTER.UltimateOscillator()
        assert_values(self,[prefix.update(price) for price in CLOSE[:170]],full[:170],0.0)
        other = MASTER.UltimateOscillator()
        changed = [other.update(price) for price in CLOSE[:170]+[1000.0]*82]
        assert_values(self,changed[:170],full[:170],0.0)
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        assert_values(self,[indicator.update(price) for price in CLOSE],full,0.0)

    def test_invalid_configuration_and_input_state_preservation(self):
        for edge in (0,0.5,-1,math.nan,math.inf):
            with self.assertRaises(ValueError): MASTER.UltimateOscillator(edge,2)
        for width in (0,1,1.399,math.nan,math.inf):
            with self.assertRaises(ValueError): MASTER.UltimateOscillator(20,width)
        with self.assertRaises(ValueError): MASTER.UltimateOscillator(1e308,2)
        for length in (0,1.5,True):
            with self.assertRaises(ValueError): MASTER.RootMeanSquare(length)
        a,b = MASTER.UltimateOscillator(),MASTER.UltimateOscillator()
        for price in CLOSE[:120]: a.update(price); b.update(price)
        for value in (math.nan,math.inf,-math.inf):
            with self.assertRaises(ValueError): a.update(value)
        assert_values(self,[a.update(p) for p in CLOSE[120:]],
                      [b.update(p) for p in CLOSE[120:]],0.0)

    def test_fractional_parameters_and_full_precision(self):
        a = article_oscillator(CLOSE,20.5,2)
        b = article_oscillator(CLOSE,20,2)
        self.assertNotEqual(a[99:],b[99:])
        c = article_oscillator(CLOSE,20,1.5)
        self.assertNotEqual(c[99:],b[99:])
        self.assertNotEqual(article_highpass(CLOSE,20),article_highpass(CLOSE,20,False))
        self.assertEqual(MASTER.PI,math.pi)
        self.assertEqual(MASTER.SQRT_TWO,math.sqrt(2))

    def test_copied_and_embedded_input_integrity(self):
        shared = MASTER._load_literal_arrays(DIRECTORY.parent/'test_testdata.py')
        for name,values in shared.items():
            self.assertEqual(ARRAYS[name],values)
            self.assertEqual(len(values),252)
        tree = ast.parse((DIRECTORY/'ultimate-oscillator.py').read_text())
        assignment = next(node for node in ast.walk(tree) if isinstance(node,ast.Assign)
                          and any(isinstance(target,ast.Name) and target.id=='INPUT_CLOSE' for target in node.targets))
        self.assertEqual(ast.literal_eval(assignment.value),CLOSE)

    def test_all_python_expected_values_and_comments(self):
        names = {'EXPECTED_'+MASTER._case_suffix(case) for case in MASTER.REFERENCE_CASES}
        self.assertEqual(names,{name for name in ARRAYS if name.startswith('EXPECTED_')})
        text = (DIRECTORY/'test_testdata.py').read_text()
        for case in MASTER.REFERENCE_CASES:
            name = 'EXPECTED_'+MASTER._case_suffix(case)
            comments = f'# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\n{name} = ['
            self.assertIn(comments,text)
            indicator = MASTER.UltimateOscillator(case.band_edge,case.bandwidth)
            assert_values(self,[indicator.update(p) for p in CLOSE],ARRAYS[name])
            self.assertTrue(all(math.isnan(value) for value in ARRAYS[name][:99]))
            self.assertTrue(all(math.isfinite(value) for value in ARRAYS[name][99:]))

    def test_every_translated_value_comment_and_nan_position(self):
        patterns = {
            'testdata_test.go':r'var expected(\w+) = \[\]float64\{\s*(.*?)\n\}',
            'testdata.ts':r'export const expected(\w+): number\[\] = \[\s*(.*?)\n\];',
            'testdata.rs':r'pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[\s*(.*?)\n\s*\]\s*\}',
            'testdata.zig':r'pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{\s*(.*?)\n\s*\};\s*\}',
        }
        nan_tokens = {'testdata_test.go':'math.NaN()','testdata.ts':'NaN',
                      'testdata.rs':'f64::NAN','testdata.zig':'nan'}
        for filename,pattern in patterns.items():
            text = (DIRECTORY/filename).read_text()
            matches = list(re.finditer(pattern,text,re.DOTALL))
            self.assertEqual(len(matches),16)
            for match in matches:
                suffix,body = match.groups()
                values = [math.nan if token.strip()==nan_tokens[filename] else float(token.strip())
                          for token in body.split(',') if token.strip()]
                assert_values(self,values,ARRAYS['EXPECTED_'+suffix.upper()],0.0)
                case = next(case for case in MASTER.REFERENCE_CASES if MASTER._case_suffix(case)==suffix.upper())
                comments = f'// {case.what_it_tests}\n// {MASTER._parameter_comment(case)}\n'
                self.assertTrue(text[:match.start()].endswith(comments))
        self.assertIn('package ultimateoscillator',(DIRECTORY/'testdata_test.go').read_text())
        self.assertIn('import "math"',(DIRECTORY/'testdata_test.go').read_text())
        self.assertIn('const nan = math.nan(f64);',(DIRECTORY/'testdata.zig').read_text())


if __name__=='__main__':
    unittest.main()
