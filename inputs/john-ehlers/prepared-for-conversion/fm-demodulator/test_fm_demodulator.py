"""Independent article, analytic and cross-language fixture checks.

Expected-data verification covers all confirmed cases in all five languages.
The original article is required only for the source-expression comparison.
"""
import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest

DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('master', DIRECTORY / 'fm-demodulator.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
CLOSES, OPENS = INPUTS['INPUT_CLOSE'], INPUTS['INPUT_OPEN']
ARTICLE = DIRECTORY.parent.parent / 'tasc/2021-05-a-technical-description-of-market-data-for-traders/content.md'

def translated_arrays(language):
    """Read each translated value with its array name and two comments."""
    patterns = {
        'go': ('testdata_test.go', r'// ([^\n]*)\n// ([^\n]*)\nvar (expected\w+) = \[\]float64\{(.*?)\n\}'),
        'ts': ('testdata.ts', r'// ([^\n]*)\n// ([^\n]*)\nexport const (expected\w+): number\[\] = \[(.*?)\n\];'),
        'rs': ('testdata.rs', r'// ([^\n]*)\n// ([^\n]*)\npub fn (expected_\w+)\(\) -> Vec<f64> \{\n\s*vec!\[(.*?)\n\s*\]\n\}'),
        'zig': ('testdata.zig', r'// ([^\n]*)\n// ([^\n]*)\npub fn (expected\w+)\(\) \[252\]f64 \{\n\s*return \.\{(.*?)\n\s*\};\n\}'),
    }
    filename, pattern = patterns[language]
    nan = {'go': 'math.NaN()', 'ts': 'NaN', 'rs': 'f64::NAN', 'zig': 'nan'}[language]
    found = {}
    for what, parameters, name, body in re.findall(pattern, (DIRECTORY / filename).read_text(), re.S):
        tokens = [token.strip() for token in body.split(',') if token.strip()]
        values = [math.nan if token == nan else float(token) for token in tokens]
        if name in found:
            raise AssertionError(f'duplicate name {name}')
        found[name] = (what, parameters, values, tokens)
    return found

class SharedChecks:
    def assert_scalar(self, actual, expected, exact=False):
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual))
        elif exact:
            self.assertEqual(actual, expected)
        else:
            self.assertTrue(math.isfinite(actual))
            self.assertTrue(math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12),
                            f'{actual!r} != {expected!r}')

    def test_embedded_and_copied_input_integrity(self):
        original = MASTER._load_literal_arrays(DIRECTORY.parent / 'test_testdata.py')
        for name, values in original.items():
            if name.startswith('INPUT_'):
                self.assertEqual(INPUTS[name], values)
                self.assertEqual(len(values), 252)
        module = ast.parse((DIRECTORY / 'fm-demodulator.py').read_text())
        for name in ('INPUT_CLOSE', 'INPUT_OPEN'):
            embedded = [node for node in ast.walk(module)
                        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                        and target.id == name for target in node.targets)]
            self.assertEqual(len(embedded), 1)
            self.assertEqual(ast.literal_eval(embedded[0].value), INPUTS[name])
        for filename in ('testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig'):
            original_text = (DIRECTORY.parent / filename).read_text()
            copied = (DIRECTORY / filename).read_text().split('BEGIN GENERATED')[0]
            self.assertEqual(re.findall(r'-?\d+\.\d{6}(?!\d)', copied),
                             re.findall(r'-?\d+\.\d{6}(?!\d)', original_text))

    def test_expected_data_in_all_five_languages(self):
        written = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
        names = {name for name in written if name.startswith('EXPECTED_')}
        wanted = {'EXPECTED_' + MASTER._case_suffix(case) for case in MASTER.REFERENCE_CASES}
        self.assertEqual(names, wanted)
        translated = {language: translated_arrays(language) for language in ('go', 'ts', 'rs', 'zig')}
        for language, arrays in translated.items():
            expected_names = {'expected_' + name[9:].lower() if language == 'rs'
                              else 'expected' + name[9:] for name in wanted}
            self.assertEqual(set(arrays), expected_names)
        python_text = (DIRECTORY / 'test_testdata.py').read_text()
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.FMDemodulator(case.period, MASTER.REFERENCE_INPUT_MODE)
            raw = [indicator.update(close, opening if MASTER.REFERENCE_INPUT_MODE == 'close_open' else None)
                   for close, opening in zip(CLOSES, OPENS)]
            suffix = MASTER._case_suffix(case)
            name = 'EXPECTED_' + suffix
            comments = f'# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\n{name} = ['
            self.assertIn(comments, python_text)
            expected = written[name]
            self.assertEqual(len(expected), 252)
            for index, value in enumerate(expected):
                self.assert_scalar(value, raw[index])
                if not math.isnan(raw[index]):
                    self.assertEqual(value, float(MASTER._float_literal(raw[index], 'nan')))
            for language, arrays in translated.items():
                other_name = 'expected_' + suffix.lower() if language == 'rs' else 'expected' + suffix
                what, parameters, values, tokens = arrays[other_name]
                self.assertEqual(what, case.what_it_tests)
                self.assertEqual(parameters, MASTER._parameter_comment(case))
                self.assertEqual(len(values), 252)
                nan = {'go': 'math.NaN()', 'ts': 'NaN', 'rs': 'f64::NAN', 'zig': 'nan'}[language]
                for value, reference, literal in zip(values, expected, tokens):
                    self.assert_scalar(value, reference, exact=True)
                    self.assertEqual(literal, MASTER._float_literal(reference, nan))

def source_outputs(closes, opens, period, full_precision=True):
    """Evaluate extracted FM expressions with the requested constant replacement."""
    code = re.findall(r'```easylanguage\n(.*?)```', ARTICLE.read_text(), re.S)[1]
    expressions = {}
    for name in ('Deriv', 'HL', 'a1', 'b1', 'c1', 'c2', 'c3', 'SS'):
        expression = re.search(r'\b' + name + r'\s*=\s*(.*?);', code, re.S).group(1)
        expression = ' '.join(expression.split())
        if full_precision:
            expression = expression.replace('1.414', 'ROOT_TWO').replace('3.14159', 'PI')
        if name == 'SS':
            expression = re.sub(r'\bHL\b(?!\s*\[)', 'HL[0]', expression)
        expressions[name] = compile(expression, '<FM article>', 'eval')
    scope = {'Period': period, 'ROOT_TWO': math.sqrt(2.0), 'PI': math.pi,
             'expvalue': math.exp, 'Cosine': lambda degrees: math.cos(math.radians(degrees))}
    for name in ('a1', 'b1', 'c2', 'c3', 'c1'):
        scope[name] = eval(expressions[name], {'__builtins__': {}}, scope)
    limited_history, outputs = [], []
    for current_bar, (close, opening) in enumerate(zip(closes, opens), 1):
        scope.update(Close=close, Open=opening)
        scope['Deriv'] = eval(expressions['Deriv'], {'__builtins__': {}}, scope)
        limited = eval(expressions['HL'], {'__builtins__': {}}, scope)
        limited = min(1.0, max(-1.0, limited))
        if current_bar < 3:
            value = scope['Deriv']
        else:
            scope['HL'] = [limited, limited_history[-1]]
            scope['SS'] = [0.0, outputs[-1], outputs[-2]]
            value = eval(expressions['SS'], {'__builtins__': {}}, scope)
        outputs.append(value)
        limited_history.append(limited)
    return outputs

class TestFMDemodulator(SharedChecks, unittest.TestCase):
    def test_all_periods_against_full_precision_source(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.FMDemodulator(case.period)
            values = [indicator.update(c, o) for c, o in zip(CLOSES, OPENS)]
            expected = source_outputs(CLOSES, OPENS, case.period)
            for actual, reference in zip(values, expected):
                self.assert_scalar(actual, reference)

    def test_full_precision_differs_from_printed_approximations(self):
        indicator = MASTER.FMDemodulator()
        values = [indicator.update(c, o) for c, o in zip(CLOSES, OPENS)]
        rounded = source_outputs(CLOSES, OPENS, 30, full_precision=False)
        self.assertGreater(max(abs(a-b) for a, b in zip(values, rounded)), 1e-6)

    def test_raw_startup_and_distinct_limited_input_history(self):
        indicator = MASTER.FMDemodulator()
        self.assertEqual(indicator.update(10.0, 0.0), 10.0)
        self.assertEqual(indicator.update(-20.0, 0.0), -20.0)
        q = math.sqrt(2.0) * math.pi / 30
        radius = math.exp(-q)
        feedback1 = 2 * radius * math.cos(q)
        feedback2 = -radius**2
        gain = 1-feedback1-feedback2
        # Previous HL is -1 while prior output is raw -20. Third input HL=0.
        expected = gain*(0.0-1.0)/2.0 + feedback1*(-20.0) + feedback2*10.0
        self.assert_scalar(indicator.update(0.0, 0.0), expected)
        self.assertTrue(indicator.is_primed)
        self.assertEqual(indicator.warmup_bars, 0)

    def test_limiter_linear_region_and_saturation(self):
        indicator = MASTER.FMDemodulator()
        for derivative, expected_hl in ((0.05, 0.5), (-0.05, -0.5), (0.1, 1.0), (-0.1, -1.0), (10.0, 1.0), (-10.0, -1.0), (0.0, 0.0)):
            indicator.update(derivative, 0.0)
            self.assertEqual(indicator._hl1, expected_hl)

    def test_different_saturated_amplitudes_match_after_same_startup(self):
        small, large = MASTER.FMDemodulator(), MASTER.FMDemodulator()
        for _ in range(2):
            small.update(0.0, 0.0)
            large.update(0.0, 0.0)
        for t in range(60):
            sign = 1.0 if t % 3 else -1.0
            self.assertEqual(small.update(sign*0.2, 0.0), large.update(sign*100.0, 0.0))

    def test_zero_and_constant_limited_signal_steady_state(self):
        zero = MASTER.FMDemodulator()
        for _ in range(100):
            self.assertEqual(zero.update(100.0, 100.0), 0.0)
        for derivative, target in ((0.05, 0.5), (2.0, 1.0), (-2.0, -1.0)):
            indicator = MASTER.FMDemodulator(10)
            for _ in range(300):
                value = indicator.update(derivative, 0.0)
            self.assert_scalar(value, target)

    def test_close_only_alignment_and_opening_gaps(self):
        paired = MASTER.FMDemodulator()
        alternate = MASTER.FMDemodulator(input_mode='close_difference')
        self.assertTrue(math.isnan(alternate.update(CLOSES[0])))
        self.assertFalse(alternate.is_primed)
        for t in range(1, len(CLOSES)):
            self.assert_scalar(alternate.update(CLOSES[t]), paired.update(CLOSES[t], CLOSES[t-1]), exact=True)
        self.assertEqual(alternate.warmup_bars, 1)
        paired, alternate = MASTER.FMDemodulator(), MASTER.FMDemodulator(input_mode='close_difference')
        paired.update(100.0, 100.0)
        alternate.update(100.0)
        self.assertEqual(paired.update(150.0, 150.0), 0.0)
        self.assertEqual(alternate.update(150.0), 50.0)

    def test_reset_causality_and_period_independent_availability(self):
        for period in (1, 30, 252):
            indicator = MASTER.FMDemodulator(period)
            self.assertTrue(math.isnan(indicator.output))
            values = [indicator.update(c, o) for c, o in zip(CLOSES, OPENS)]
            self.assertTrue(all(math.isfinite(value) for value in values))
            indicator.reset()
            self.assertFalse(indicator.is_primed)
            for t in range(40):
                self.assertEqual(indicator.update(CLOSES[t], OPENS[t]), values[t])

    def test_validation_and_transactional_rejection(self):
        for period in (0, -1, 30.0, True, 10**20):
            with self.assertRaises(ValueError):
                MASTER.FMDemodulator(period)
        with self.assertRaises(ValueError):
            MASTER.FMDemodulator(input_mode='invalid')
        indicator, reference = MASTER.FMDemodulator(), MASTER.FMDemodulator()
        for c, o in zip(CLOSES[:20], OPENS[:20]):
            indicator.update(c, o)
            reference.update(c, o)
        before = indicator.output
        for args in ((math.nan, 1.0), (1.0, math.inf), (1.0,), (1e308, -1e308), (1e308, 0.0)):
            with self.assertRaises(ValueError):
                indicator.update(*args)
            self.assertEqual(indicator.output, before)
        self.assertEqual(indicator.update(CLOSES[20], OPENS[20]), reference.update(CLOSES[20], OPENS[20]))

if __name__ == '__main__':
    unittest.main()
