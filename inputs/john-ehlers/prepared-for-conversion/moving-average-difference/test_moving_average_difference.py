"""Independent published-expression and analytical tests of the MAD master."""

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
SPEC = importlib.util.spec_from_file_location('mad_master', DIRECTORY / 'moving-average-difference.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
CLOSE = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')['INPUT_CLOSE']
SOURCE = (DIRECTORY.parent.parent / 'tasc/2021-10-cycle-trend-analytics-and-the-mad-indicator/tips/code/CycleTrendAnalytics.els').read_text()
EXPRESSION = ' '.join(re.search(r'\bMAD\s*=\s*(.*?);', SOURCE, re.DOTALL).group(1).split())


def source_batch(prices, short, long):
    """Evaluate the actual source formula with full-window batch averages.

    No streaming ring, running accumulator or master update is used. Average
    internally sums newest first, as explicitly defined for this prototype.
    """
    outputs = []
    for t in range(len(prices)):
        if t < max(short, long) - 1:
            outputs.append(math.nan)
            continue
        def average(close, length):
            total = 0.0
            for value in reversed(close[t-length+1:t+1]):
                total += value
            return total / length
        if average(prices, long) == 0:
            outputs.append(math.nan)
        else:
            outputs.append(eval(EXPRESSION, {'__builtins__': {}},
                                {'Average': average, 'Close': prices, 'ShortLength': short, 'LongLength': long}))
    return outputs


def compare(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for t, (a, b) in enumerate(zip(actual, expected)):
        if math.isnan(b):
            test.assertTrue(math.isnan(a), (t, a, b))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance), (t, a, b))


class MovingAverageDifferenceTests(unittest.TestCase):
    def test_all_confirmed_pairs_against_actual_source_expression(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.MovingAverageDifference(case.short_length, case.long_length)
            actual = [indicator.update(price) for price in CLOSE]
            compare(self, actual, source_batch(CLOSE, case.short_length, case.long_length), 0)

    def test_exact_case_warmup_and_partial_diagnostic_availability(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.MovingAverageDifference(case.short_length, case.long_length)
            warmup = max(case.short_length, case.long_length) - 1
            self.assertEqual(indicator.warmup_bars, warmup)
            for t, price in enumerate(CLOSE):
                output = indicator.update(price)
                self.assertEqual(math.isnan(output), t < warmup)
                self.assertEqual(indicator.is_primed, t >= warmup)
                self.assertEqual(math.isnan(indicator.state.short_average), t < case.short_length - 1)
                self.assertEqual(math.isnan(indicator.state.long_average), t < case.long_length - 1)
                self.assertLessEqual(len(indicator._prices), max(case.short_length, case.long_length))

    def test_constant_prices_equal_windows_and_singleton(self):
        indicator = MASTER.MovingAverageDifference()
        values = [indicator.update(42.0) for _ in range(100)]
        self.assertTrue(all(math.isnan(v) for v in values[:22]))
        self.assertEqual(values[22:], [0.0] * 78)
        for length in (1, 8, 23):
            indicator = MASTER.MovingAverageDifference(length, length)
            values = [indicator.update(p) for p in CLOSE]
            self.assertEqual(values[length-1:], [0.0] * (253-length))
        indicator = MASTER.MovingAverageDifference(1, 1)
        self.assertEqual(indicator.update(42), 0)
        self.assertTrue(indicator.is_primed)

    def test_zero_denominator_does_not_reset_or_contaminate_price_history(self):
        indicator = MASTER.MovingAverageDifference(1, 2)
        self.assertTrue(math.isnan(indicator.update(1)))
        self.assertTrue(math.isnan(indicator.update(-1)))
        self.assertTrue(indicator.is_primed)
        self.assertEqual(indicator.state.long_average, 0)
        self.assertEqual(indicator.state.difference, -1)
        self.assertAlmostEqual(indicator.update(3), 200)
        flat = MASTER.MovingAverageDifference(2, 3)
        for _ in range(10):
            self.assertTrue(math.isnan(flat.update(0)))
        self.assertTrue(flat.is_primed)
        self.assertEqual(flat.state.difference, 0)
        self.assertAlmostEqual(flat.update(3), 50)

    def test_reversed_windows_use_designated_long_average(self):
        a, b = MASTER.MovingAverageDifference(8, 23), MASTER.MovingAverageDifference(23, 8)
        for t, p in enumerate(CLOSE):
            forward, reverse = a.update(p), b.update(p)
            if t >= 22:
                # Reversing lengths reverses the raw difference but also swaps
                # the denominator. Reverse percentage is not merely -forward.
                self.assertEqual(a.state.difference, -b.state.difference)
                self.assertEqual(a.state.short_average, b.state.long_average)
                self.assertAlmostEqual(reverse, -100 * forward / (100 + forward), places=12)

    def test_exact_linear_trend_and_positive_scale_invariance(self):
        step = 0.5
        indicator = MASTER.MovingAverageDifference(8, 23)
        for t in range(100):
            x = 100 + step*t
            value = indicator.update(x)
            if indicator.is_primed:
                short = x - step*(8-1)/2
                long = x - step*(23-1)/2
                self.assertEqual(indicator.state.short_average, short)
                self.assertEqual(indicator.state.long_average, long)
                self.assertEqual(indicator.state.difference, step*(23-8)/2)
                self.assertEqual(value, 100*(short-long)/long)
        reference = MASTER.MovingAverageDifference()
        expected = [reference.update(p) for p in CLOSE]
        scaled = MASTER.MovingAverageDifference()
        compare(self, [scaled.update(8*p) for p in CLOSE], expected, 0)
        negative_scale = MASTER.MovingAverageDifference()
        compare(self, [negative_scale.update(-p) for p in CLOSE], expected, 0)

    def test_fir_cycle_response_and_phase_alignment_limits(self):
        omega = 2*math.pi/30
        def response(length):
            return sum(cmath.exp(-1j*omega*k) for k in range(length))/length
        for short, long in ((5, 20), (8, 23), (5, 30)):
            indicator = MASTER.MovingAverageDifference(short, long)
            gain = response(short) - response(long)
            for t in range(100):
                indicator.update(100 + math.sin(omega*t))
                if indicator.is_primed:
                    expected = (gain*cmath.exp(1j*omega*t)).imag
                    self.assertAlmostEqual(indicator.state.difference, expected, places=12)
        # Both separations are 15, but their exact phases differ. The article's
        # half-cycle rule is a parameter heuristic, not a universal identity.
        phase5 = math.degrees(cmath.phase(response(5)-response(20)))
        phase8 = math.degrees(cmath.phase(response(8)-response(23)))
        self.assertGreater(abs(phase5), 0.1)
        self.assertGreater(abs(phase8-phase5), 10)

    def test_reset_causality_nonfinite_rejection_and_parameter_validation(self):
        a = MASTER.MovingAverageDifference()
        full = [a.update(p) for p in CLOSE]
        b = MASTER.MovingAverageDifference()
        compare(self, [b.update(p) for p in CLOSE[:100]], full[:100], 0)
        a.reset()
        self.assertFalse(a.is_primed)
        compare(self, [a.update(p) for p in CLOSE], full, 0)
        a.reset()
        b.reset()
        for p in CLOSE[:100]:
            a.update(p)
            b.update(p)
        for p in (math.nan, math.inf, -math.inf):
            old = a.state
            with self.assertRaises(ValueError):
                a.update(p)
            self.assertEqual(a.state, old)
        compare(self, [a.update(p) for p in CLOSE[100:]], [b.update(p) for p in CLOSE[100:]], 0)
        for value in (0, -1, True, 2.0, 1.5, math.nan, math.inf):
            with self.assertRaises(ValueError): MASTER.MovingAverageDifference(value, 23)
            with self.assertRaises(ValueError): MASTER.MovingAverageDifference(8, value)

    def test_all_copied_input_arrays_and_embedded_close_are_unchanged(self):
        before = MASTER._load_literal_arrays(DIRECTORY.parent / 'test_testdata.py')
        after = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
        for name, values in before.items():
            if name.startswith('INPUT_'):
                self.assertEqual(values, after[name])
                self.assertEqual(len(values), 252)
        module = ast.parse((DIRECTORY / 'moving-average-difference.py').read_text())
        main = next(node for node in module.body if isinstance(node, ast.If))
        embedded = next(node for node in main.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'INPUT_CLOSE' for t in node.targets))
        self.assertEqual(ast.literal_eval(embedded.value), CLOSE)

    def test_expected_data_in_every_language_matches_source_and_case_warmup(self):
        arrays = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
        names = {MASTER._expected_name(case, 'mad') for case in MASTER.REFERENCE_CASES}
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
            name = MASTER._expected_name(case, 'mad')
            values = arrays[name]
            expected = source_batch(CLOSE, case.short_length, case.long_length)
            compare(self, values, expected)
            warmup = max(case.short_length, case.long_length) - 1
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
        # Edge cases have specifically useful shapes, independent of values
        # at other parameter pairs: one available full-record output and an
        # exactly zero equal-window signal following seven unavailable bars.
        self.assertEqual(sum(math.isfinite(v) for v in arrays['EXPECTED_SL126_LL252']), 1)
        self.assertEqual(arrays['EXPECTED_SL8_LL8'][7:], [0.0] * 245)

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
        # Go changes its package and imports math; Zig adds a NaN constant.
        # Aside from those declarations, all five copied input sections retain
        # their exact text and the generator changes only its marked outputs.
        for filename in filenames:
            original = (DIRECTORY.parent / filename).read_text().rstrip()
            marker = '# BEGIN GENERATED' if filename.endswith('.py') else '// BEGIN GENERATED'
            prefix = (DIRECTORY / filename).read_text().split(marker, 1)[0].rstrip()
            if filename.endswith('.go'):
                prefix = prefix.replace('package movingaveragedifference\n\nimport "math"\n',
                                        'package xxxx\n', 1)
            if filename.endswith('.zig') and 'const nan = math.nan(f64);' not in original:
                prefix = prefix.replace('const nan = math.nan(f64);\n', '', 1)
            self.assertEqual(prefix, original)


if __name__ == '__main__':
    unittest.main()
