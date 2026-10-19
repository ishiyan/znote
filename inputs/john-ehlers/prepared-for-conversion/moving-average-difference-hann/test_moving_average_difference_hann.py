"""Independent published-expression and analytical checks of the MADH master."""

import ast
import cmath
import contextlib
import importlib.util
import io
import math
from pathlib import Path
import re
import tempfile
import unittest

DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('madh_master', DIRECTORY / 'moving-average-difference-hann.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
CLOSE = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')['INPUT_CLOSE']
SOURCE = (DIRECTORY.parent.parent / 'tasc/2021-11-the-mad--indicator-enhanced/tips/code/MADH.els').read_text()


def assignment(name):
    return ' '.join(re.search(r'\b' + name + r'\s*=\s*(.*?);', SOURCE, re.DOTALL).group(1).split())


def source_batch(prices, short, cycle):
    """Evaluate primary source assignments with batch full-window histories.

    No master weights, circular ring or streaming update is used. Before both
    windows exist, output availability is masked and persistent MADH is zero.
    """
    functions = {'IntPortion': math.trunc, 'Cosine': lambda angle: math.cos(math.radians(angle))}
    lengths = {'ShortLength': short, 'DominantCycle': cycle}
    long = eval(assignment('LongLength'), {'__builtins__': {}}, functions | lengths)
    lengths['LongLength'] = long
    blocks = [SOURCE.split('for count = 1 to ShortLength', 1)[1].split('Filt2 = 0;', 1)[0],
              SOURCE.split('for count = 1 to LongLength', 1)[1].split('// Computed', 1)[0]]
    weights = []
    for block, n in zip(blocks, (short, long)):
        expression = ' '.join(re.search(r'coef = coef \+ (.*?);', block, re.DOTALL).group(1).split())
        weights.append([eval(expression, {'__builtins__': {}}, functions | lengths | {'count': c})
                        for c in range(1, n+1)])
    outputs, details = [], []
    madh = 0.0
    for t in range(len(prices)):
        filters = []
        for kernel in weights:
            if t < len(kernel)-1:
                filters.append(math.nan)
                continue
            total = coefficient = 0.0
            for lag, weight in enumerate(kernel):
                total += weight * prices[t-lag]
                coefficient += weight
            filters.append(total / coefficient if coefficient != 0 else total)
        if t >= long-1 and filters[1] != 0:
            madh = eval(assignment('MADH'), {'__builtins__': {}}, {'Filt1': filters[0], 'Filt2': filters[1]})
        details.append((filters[0], filters[1], madh))
        outputs.append(madh if t >= long-1 else math.nan)
    return outputs, details


def compare(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for t, (a, b) in enumerate(zip(actual, expected)):
        if math.isnan(b):
            test.assertTrue(math.isnan(a), (t, a, b))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance), (t, a, b))


class MovingAverageDifferenceHannTests(unittest.TestCase):
    def test_all_confirmed_cases_match_supplied_source_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.MovingAverageDifferenceHann(case.short_length, case.dominant_cycle)
            expected, details = source_batch(CLOSE, case.short_length, case.dominant_cycle)
            actual = []
            for t, price in enumerate(CLOSE):
                actual.append(indicator.update(price))
                if indicator.is_primed:
                    self.assertEqual(indicator.state.short_filter, details[t][0])
                    self.assertEqual(indicator.state.long_filter, details[t][1])
            compare(self, actual, expected, 0)

    def test_exact_warmup_full_windows_and_diagnostic_availability(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.MovingAverageDifferenceHann(case.short_length, case.dominant_cycle)
            long = math.trunc(case.short_length + case.dominant_cycle/2)
            self.assertEqual(indicator.long_length, long)
            self.assertEqual(indicator.warmup_bars, long-1)
            for t, price in enumerate(CLOSE):
                value = indicator.update(price)
                self.assertEqual(indicator.is_primed, t >= long-1)
                self.assertEqual(math.isnan(value), t < long-1)
                self.assertEqual(math.isnan(indicator.state.short_filter), t < case.short_length-1)
                self.assertEqual(math.isnan(indicator.state.long_filter), t < long-1)
                self.assertLessEqual(len(indicator._prices), long)
                if t < long-1: self.assertEqual(indicator.state.madh, 0)

    def test_interior_hann_weights_sums_symmetry_and_singleton(self):
        for n in (1, 2, 3, 8, 21, 252):
            weights, coefficient = MASTER.MovingAverageDifferenceHann._kernel(n)
            self.assertGreater(weights[0], 0)
            self.assertGreater(weights[-1], 0)
            self.assertAlmostEqual(coefficient, n+1, places=11)
            for a, b in zip(weights, reversed(weights)):
                self.assertAlmostEqual(a, b, places=13)
            self.assertAlmostEqual(sum(k*w for k,w in enumerate(weights))/coefficient, (n-1)/2, places=12)
        indicator = MASTER.MovingAverageDifferenceHann(1, 1)
        self.assertEqual(indicator.long_length, 1)
        self.assertEqual(indicator.update(12.5), 0)
        self.assertEqual(indicator.state.short_filter, 12.5)

    def test_truncation_boundaries_and_identical_effective_parameters(self):
        baseline = None
        for dc in (26, 27, 27.5, 27.999):
            indicator = MASTER.MovingAverageDifferenceHann(8, dc)
            self.assertEqual(indicator.long_length, 21)
            values = [indicator.update(p) for p in CLOSE]
            if baseline is None: baseline = values
            else: compare(self, values, baseline, 0)
        self.assertEqual(MASTER.MovingAverageDifferenceHann(8, 28).long_length, 22)
        equal = MASTER.MovingAverageDifferenceHann(8, 1)
        outputs = [equal.update(p) for p in CLOSE]
        self.assertEqual(outputs[7:], [0.0] * 245)

    def test_zero_denominator_holds_previous_madh_and_recovers(self):
        indicator = MASTER.MovingAverageDifferenceHann(1, 2)
        self.assertTrue(math.isnan(indicator.update(1)))
        previous = indicator.update(3)
        self.assertNotEqual(previous, 0)
        indicator.update(0)
        previous = indicator.state.madh
        self.assertEqual(indicator.update(0), previous)
        self.assertTrue(indicator.is_primed)
        self.assertEqual(indicator.state.long_filter, 0)
        self.assertEqual(indicator.state.difference, 0)
        self.assertNotEqual(indicator.update(2), previous)
        flat = MASTER.MovingAverageDifferenceHann()
        outputs = [flat.update(0) for _ in range(100)]
        self.assertTrue(all(math.isnan(v) for v in outputs[:20]))
        self.assertEqual(outputs[20:], [0.0]*80)
        self.assertEqual(flat.state.madh, 0)

    def test_linear_trend_constant_prices_and_scale_invariance(self):
        indicator = MASTER.MovingAverageDifferenceHann(8, 27)
        for t in range(100):
            x = 100 + 0.5*t
            output = indicator.update(x)
            if indicator.is_primed:
                short, long = x-0.5*7/2, x-0.5*20/2
                self.assertAlmostEqual(indicator.state.short_filter, short, places=12)
                self.assertAlmostEqual(indicator.state.long_filter, long, places=12)
                self.assertAlmostEqual(indicator.state.difference, 0.5*(21-8)/2, places=12)
                self.assertAlmostEqual(output, 100*(short-long)/long, places=12)
        constant = MASTER.MovingAverageDifferenceHann()
        for _ in range(100):
            value = constant.update(42)
            if constant.is_primed: self.assertAlmostEqual(value, 0, places=12)
        reference = MASTER.MovingAverageDifferenceHann()
        outputs = [reference.update(p) for p in CLOSE]
        for factor in (8, -1):
            scaled = MASTER.MovingAverageDifferenceHann()
            compare(self, [scaled.update(factor*p) for p in CLOSE], outputs, 0)

    def test_sinusoidal_fir_response_and_first_difference_noise_gain(self):
        omega = 2*math.pi/30
        def response(n):
            weights = [1-math.cos(math.radians(360*c/(n+1))) for c in range(1,n+1)]
            return sum(w*cmath.exp(-1j*omega*k) for k,w in enumerate(weights))/sum(weights)
        for s, dc in ((5,30),(8,27),(10,30)):
            indicator = MASTER.MovingAverageDifferenceHann(s,dc)
            gain = response(s)-response(indicator.long_length)
            for t in range(100):
                indicator.update(100+math.sin(omega*t))
                if indicator.is_primed:
                    expected = (gain*cmath.exp(1j*omega*t)).imag
                    self.assertAlmostEqual(indicator.state.difference, expected, places=12)
        # One-bar ROC emphasizes high-frequency changes compared with low
        # frequencies; it does not introduce a lowpass effect of its own.
        self.assertGreater(abs(1-cmath.exp(-1j*2.5)), abs(1-cmath.exp(-1j*0.1)))

    def test_reset_causal_prefix_nonfinite_inputs_and_parameter_validation(self):
        a = MASTER.MovingAverageDifferenceHann()
        outputs = [a.update(p) for p in CLOSE]
        b = MASTER.MovingAverageDifferenceHann()
        compare(self, [b.update(p) for p in CLOSE[:100]], outputs[:100], 0)
        a.reset()
        self.assertFalse(a.is_primed)
        compare(self, [a.update(p) for p in CLOSE], outputs, 0)
        a.reset()
        b.reset()
        for p in CLOSE[:100]:
            a.update(p)
            b.update(p)
        for p in (math.nan, math.inf, -math.inf):
            old = a.state
            with self.assertRaises(ValueError): a.update(p)
            self.assertEqual(a.state, old)
        compare(self, [a.update(p) for p in CLOSE[100:]], [b.update(p) for p in CLOSE[100:]], 0)
        for p in (0, -1, True, 8.0, 1.5):
            with self.assertRaises(ValueError): MASTER.MovingAverageDifferenceHann(p,27)
        for p in (0, -1, True, math.nan, math.inf):
            with self.assertRaises(ValueError): MASTER.MovingAverageDifferenceHann(8,p)

    def test_copied_inputs_and_embedded_close_are_preserved(self):
        before = MASTER._load_literal_arrays(DIRECTORY.parent / 'test_testdata.py')
        after = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
        for name, values in before.items():
            if name.startswith('INPUT_'):
                self.assertEqual(values, after[name])
                self.assertEqual(len(values), 252)
        module = ast.parse((DIRECTORY / 'moving-average-difference-hann.py').read_text())
        main = next(node for node in module.body if isinstance(node, ast.If))
        embedded = next(node for node in main.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'INPUT_CLOSE' for t in node.targets))
        self.assertEqual(ast.literal_eval(embedded.value), CLOSE)

    def test_every_expected_fixture_matches_source_comments_and_case_warmup(self):
        arrays = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
        names = {MASTER._expected_name(case, 'madh') for case in MASTER.REFERENCE_CASES}
        self.assertEqual({name for name in arrays if name.startswith('EXPECTED_')}, names)
        patterns = {
            'testdata_test.go': r'var (expected\w+) = \[\]float64\{(.*?)\n\}',
            'testdata.ts': r'export const (expected\w+): number\[\] = \[(.*?)\n\];',
            'testdata.rs': r'pub fn (expected_\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\n    \]',
            'testdata.zig': r'pub fn (expected\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\n    \};',
        }
        texts = {name: (DIRECTORY / name).read_text() for name in patterns}
        translated = {name: dict(re.findall(pattern, texts[name], re.DOTALL))
                      for name, pattern in patterns.items()}
        for language_arrays in translated.values():
            self.assertEqual(len(language_arrays), 16)
        python_text = (DIRECTORY / 'test_testdata.py').read_text()
        for case in MASTER.REFERENCE_CASES:
            name = MASTER._expected_name(case, 'madh')
            values = arrays[name]
            expected, _ = source_batch(CLOSE, case.short_length, case.dominant_cycle)
            compare(self, values, expected)
            warmup = math.trunc(case.short_length + case.dominant_cycle/2) - 1
            self.assertEqual(len(values), 252)
            self.assertTrue(all(math.isnan(v) for v in values[:warmup]))
            self.assertTrue(all(math.isfinite(v) for v in values[warmup:]))
            self.assertIn(f'# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\n{name}', python_text)
            suffix = name.removeprefix('EXPECTED_')
            for filename, language_arrays in translated.items():
                target = 'expected_' + suffix.lower() if filename.endswith('.rs') else 'expected' + suffix
                literals = [v.strip() for v in language_arrays[target].split(',') if v.strip()]
                floats = [math.nan if v in ('math.NaN()', 'NaN', 'f64::NAN', 'nan') else float(v) for v in literals]
                compare(self, floats, values, 0)
                self.assertIn(f'// {case.what_it_tests}\n// {MASTER._parameter_comment(case)}\n', texts[filename])
        # Identical effective kernels must retain identical serialized values;
        # these pairs also exercise integer truncation around a half period.
        compare(self, arrays['EXPECTED_SL8_DC26'], arrays['EXPECTED_SL8_DC27'], 0)
        compare(self, arrays['EXPECTED_SL8_DC27_5'], arrays['EXPECTED_SL8_DC27'], 0)
        self.assertEqual(sum(math.isfinite(v) for v in arrays['EXPECTED_SL126_DC252']), 1)
        self.assertEqual(arrays['EXPECTED_SL8_DC1'][7:], [0.0] * 245)
        self.assertEqual(arrays['EXPECTED_SL1_DC1'], [0.0] * 252)

    def test_regeneration_is_identical_and_preserves_copied_input_text(self):
        filenames = ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')
        before = {name: (DIRECTORY / name).read_bytes() for name in filenames}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name, content in before.items():
                (target / name).write_bytes(content)
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, target)
                MASTER.generate_reference_data(CLOSE, target)
            self.assertEqual(before, {name: (target / name).read_bytes() for name in filenames})
        for filename in filenames:
            original = (DIRECTORY.parent / filename).read_text().rstrip()
            marker = '# BEGIN GENERATED' if filename.endswith('.py') else '// BEGIN GENERATED'
            prefix = (DIRECTORY / filename).read_text().split(marker, 1)[0].rstrip()
            if filename.endswith('.go'):
                prefix = prefix.replace('package movingaveragedifferencehann\n\nimport "math"\n',
                                        'package xxxx\n', 1)
            if filename.endswith('.zig') and 'const nan = math.nan(f64);' not in original:
                prefix = prefix.replace('const nan = math.nan(f64);\n', '', 1)
            self.assertEqual(prefix, original)


if __name__ == '__main__':
    unittest.main()
