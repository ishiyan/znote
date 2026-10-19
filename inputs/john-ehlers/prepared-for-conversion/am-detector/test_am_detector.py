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
SPEC = importlib.util.spec_from_file_location('master', DIRECTORY / 'am-detector.py')
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
        module = ast.parse((DIRECTORY / 'am-detector.py').read_text())
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
            indicator = MASTER.AMDetector(case.envelope_length, case.average_length, MASTER.REFERENCE_INPUT_MODE)
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

def source_outputs(closes, opens, envelope_length, average_length):
    """Evaluate the actual AM assignments with full observed windows."""
    code = re.findall(r'```easylanguage\n(.*?)```', ARTICLE.read_text(), re.S)[0]
    expressions = {}
    for name in ('Deriv', 'Envel', 'Volatil'):
        expression = re.search(name + r'\s*=\s*(.*?);', code, re.S).group(1)
        expressions[name] = compile(expression, '<AM article>', 'eval')
    derivatives, envelopes, result = [], [], []
    scope = {'AbsValue': abs,
             'Highest': lambda current, ignored: max(derivatives[-envelope_length:]),
             'Average': lambda current, ignored: math.fsum(envelopes[-average_length:]) / average_length}
    for close, opening in zip(closes, opens):
        scope.update(Close=close, Open=opening)
        scope['Deriv'] = eval(expressions['Deriv'], {'__builtins__': {}}, scope)
        derivatives.append(abs(scope['Deriv']))
        value = math.nan
        if len(derivatives) >= envelope_length:
            scope['Envel'] = eval(expressions['Envel'], {'__builtins__': {}}, scope)
            envelopes.append(scope['Envel'])
            if len(envelopes) >= average_length:
                value = eval(expressions['Volatil'], {'__builtins__': {}}, scope)
        result.append(value)
    return result

class TestAMDetector(SharedChecks, unittest.TestCase):
    def test_all_cases_against_article_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.AMDetector(case.envelope_length, case.average_length)
            actual = [indicator.update(c, o) for c, o in zip(CLOSES, OPENS)]
            expected = source_outputs(CLOSES, OPENS, *case[:2])
            for left, right in zip(actual, expected):
                # Source Average is a platform built-in; compare the same
                # mathematical sum without requiring its hidden rounding order.
                self.assert_scalar(left, right)

    def test_independent_direct_composite_windows(self):
        differences = [abs(c-o) for c, o in zip(CLOSES, OPENS)]
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.AMDetector(case.envelope_length, case.average_length)
            actual = [indicator.update(c, o) for c, o in zip(CLOSES, OPENS)]
            for t in range(indicator.warmup_bars, 252):
                maxima = [max(differences[t-j-case.envelope_length+1:t-j+1])
                          for j in range(case.average_length)]
                self.assert_scalar(actual[t], math.fsum(maxima) / case.average_length)

    def test_staged_full_window_priming_and_boundaries(self):
        for e, a in ((1, 1), (4, 8), (4, 249), (4, 250), (252, 1)):
            indicator = MASTER.AMDetector(e, a)
            self.assertTrue(math.isnan(indicator.output))
            for t, (c, o) in enumerate(zip(CLOSES, OPENS)):
                value = indicator.update(c, o)
                self.assertEqual(math.isnan(value), t < e+a-2)
                self.assertEqual(indicator.is_primed, t >= e+a-2)

    def test_constant_difference_and_sign_invariance(self):
        for direction in (0.0, 2.0, -2.0):
            indicator = MASTER.AMDetector()
            for t in range(20):
                value = indicator.update(100.0+direction, 100.0)
                if t >= indicator.warmup_bars:
                    self.assertEqual(value, abs(direction))

    def test_spike_envelope_and_average_finite_support(self):
        indicator = MASTER.AMDetector(4, 8)
        values = [indicator.update(8.0 if t == 20 else 0.0, 0.0) for t in range(45)]
        # The peak enters four consecutive envelopes. The SMA counts each
        # such envelope for eight bars, giving exactly eleven influenced bars.
        expected = [1, 2, 3, 4, 4, 4, 4, 4, 3, 2, 1]
        self.assertEqual(values[20:31], expected)
        self.assertEqual(values[31], 0.0)

    def test_close_only_mode_has_one_extra_missing_bar(self):
        direct = MASTER.AMDetector(2, 3)
        alternate = MASTER.AMDetector(2, 3, 'close_difference')
        self.assertTrue(math.isnan(alternate.update(CLOSES[0])))
        for t in range(1, len(CLOSES)):
            value = alternate.update(CLOSES[t])
            expected = direct.update(CLOSES[t], CLOSES[t-1])
            self.assert_scalar(value, expected, exact=True)
        self.assertEqual(alternate.warmup_bars, direct.warmup_bars+1)

    def test_opening_gaps_are_excluded(self):
        paired = MASTER.AMDetector(1, 1)
        close_only = MASTER.AMDetector(1, 1, 'close_difference')
        paired.update(100.0, 100.0)
        close_only.update(100.0)
        self.assertEqual(paired.update(150.0, 150.0), 0.0)
        self.assertEqual(close_only.update(150.0), 50.0)

    def test_reset_and_causality(self):
        indicator = MASTER.AMDetector()
        full = [indicator.update(c, o) for c, o in zip(CLOSES, OPENS)]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        for t, (c, o) in enumerate(zip(CLOSES, OPENS)):
            self.assert_scalar(indicator.update(c, o), full[t], exact=True)
        prefix = MASTER.AMDetector()
        for t in range(30):
            self.assert_scalar(prefix.update(CLOSES[t], OPENS[t]), full[t], exact=True)

    def test_validation_and_transactional_rejection(self):
        for args in ((0, 8), (4, 0), (True, 8), (4, 8.0)):
            with self.assertRaises(ValueError):
                MASTER.AMDetector(*args)
        with self.assertRaises(ValueError):
            MASTER.AMDetector(input_mode='invalid')
        indicator, reference = MASTER.AMDetector(), MASTER.AMDetector()
        for c, o in zip(CLOSES[:20], OPENS[:20]):
            indicator.update(c, o)
            reference.update(c, o)
        before = indicator.output
        for args in ((math.nan, 1.0), (1.0, math.inf), (1.0,), (1e308, -1e308)):
            with self.assertRaises(ValueError):
                indicator.update(*args)
            self.assertEqual(indicator.output, before)
        self.assertEqual(indicator.update(CLOSES[20], OPENS[20]), reference.update(CLOSES[20], OPENS[20]))

if __name__ == '__main__':
    unittest.main()
