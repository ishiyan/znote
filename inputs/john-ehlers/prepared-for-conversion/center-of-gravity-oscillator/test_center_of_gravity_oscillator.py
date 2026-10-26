"""Focused numeric and state-contract checks for the portable CG master.

The decimal rational oracle is independent of floating-point summation and
uses chronological windows instead of the implementation's ring indexing.
The second oracle is the published EasyLanguage loop translated literally.
"""

import importlib.util
import math
from pathlib import Path
import re
import runpy
import tempfile
import unittest
from fractions import Fraction
from unittest.mock import patch


DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    'cg_master', DIRECTORY / 'center-of-gravity-oscillator.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
CG = MASTER.CenterOfGravityOscillator
INPUT_CLOSE = runpy.run_path(str(DIRECTORY / 'test_testdata.py'))['INPUT_CLOSE']


def source_outputs(prices, length, centered):
    """Translate the source loop; mask only genuinely unavailable history."""
    previous = 0.0
    results = []
    for t in range(len(prices)):
        if t < length - 1:
            results.append((math.nan, math.nan))
            continue
        trigger = previous if t >= length else math.nan
        num = 0.0
        denom = 0.0
        for count in range(length):
            num = num + (1 + count) * prices[t - count]
            denom = denom + prices[t - count]
        if denom != 0.0:
            previous = -num / denom
            if centered:
                previous = previous + (length + 1) / 2.0
        results.append((previous, trigger))
    return results


class TestCenterOfGravityOscillator(unittest.TestCase):
    def assertNumber(self, actual, expected, *, delta=1e-12):
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual))
        else:
            self.assertAlmostEqual(actual, expected, delta=delta)

    def test_all_confirmed_cases_match_published_loop(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(length=case.length, centered=case.centered):
                indicator = CG(case.length, centered=case.centered)
                expected = source_outputs(INPUT_CLOSE, case.length, case.centered)
                for price, pair in zip(INPUT_CLOSE, expected):
                    result = indicator.update(price)
                    # Same arithmetic and order must agree exactly, not only
                    # within the serialized reference data's decimal tolerance.
                    for actual, reference in zip(result, pair):
                        if math.isnan(reference):
                            self.assertTrue(math.isnan(actual))
                        else:
                            self.assertEqual(actual, reference)

    def test_exact_decimal_oracle_and_per_output_availability(self):
        decimal_prices = [Fraction(str(price)) for price in INPUT_CLOSE]
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(length=case.length, centered=case.centered):
                indicator = CG(case.length, centered=case.centered)
                prior = math.nan
                for index, price in enumerate(INPUT_CLOSE):
                    result = indicator.update(price)
                    if index < case.length - 1:
                        self.assertTrue(math.isnan(result.value))
                        self.assertTrue(math.isnan(result.trigger))
                        self.assertFalse(indicator.is_primed)
                        continue
                    chronological = decimal_prices[index - case.length + 1:index + 1]
                    numerator = sum((case.length - age) * value
                                    for age, value in enumerate(chronological))
                    exact = -numerator / sum(chronological)
                    if case.centered:
                        exact += Fraction(case.length + 1, 2)
                    self.assertNumber(result.value, float(exact))
                    self.assertNumber(result.trigger, prior)
                    prior = float(exact)
                    self.assertTrue(indicator.is_primed)
                    self.assertEqual(indicator.is_trigger_primed, index >= case.length)

    def test_newest_price_has_weight_one_and_sign_is_negative(self):
        article = CG(3)
        book = CG(3, centered=True)
        for price in (1.0, 2.0, 3.0):
            result = article.update(price)
            centered = book.update(price)
        # Newest-first numerator = 1*3 + 2*2 + 3*1 = 10.
        self.assertEqual(result.value, -10.0 / 6.0)
        self.assertEqual(centered.value, -10.0 / 6.0 + 2.0)
        self.assertTrue(math.isnan(result.trigger))

    def test_constant_price_and_length_one(self):
        for length in (1, 2, 3, 10):
            for centered in (False, True):
                indicator = CG(length, centered=centered)
                baseline = 0.0 if centered else -(length + 1) / 2.0
                for index in range(length + 2):
                    result = indicator.update(8.0)
                    self.assertNumber(result.value, math.nan if index < length - 1 else baseline)
                    self.assertNumber(result.trigger, math.nan if index < length else baseline)

    def test_zero_sum_holds_previous_value_in_both_modes(self):
        for centered in (False, True):
            indicator = CG(2, centered=centered)
            indicator.update(1.0)
            previous = indicator.update(2.0).value
            held = indicator.update(-2.0)  # [2, -2], denominator exactly 0.
            self.assertEqual(held.value, previous)
            self.assertEqual(held.trigger, previous)
            resumed = indicator.update(4.0)
            self.assertEqual(resumed.trigger, previous)
            self.assertEqual(resumed.value, 1.5 if centered else 0.0)

    def test_initial_zero_sum_and_no_unconditional_offset(self):
        for centered in (False, True):
            indicator = CG(2, centered=centered)
            indicator.update(1.0)
            result = indicator.update(-1.0)
            self.assertEqual(result.value, 0.0)
            self.assertTrue(math.isnan(result.trigger))

    def test_subnormal_denominator_uses_exact_nonzero_guard(self):
        indicator = CG(2)
        indicator.update(1e-309)
        self.assertAlmostEqual(indicator.update(1e-309).value, -1.5, delta=1e-14)

    def test_nan_does_not_move_window_or_delay(self):
        skipped = CG(3)
        uninterrupted = CG(3)
        for price in (1.0, 2.0, 3.0, 4.0, 5.0):
            result = skipped.update(math.nan)
            self.assertTrue(math.isnan(result.value) and math.isnan(result.trigger))
            actual = skipped.update(price)
            reference = uninterrupted.update(price)
            for a, b in zip(actual, reference):
                self.assertNumber(a, b, delta=0.0)
        self.assertTrue(skipped.is_trigger_primed)

    def test_infinity_is_rejected_before_mutation(self):
        indicator = CG(1)
        indicator.update(4.0)
        for value in (math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(value)
        self.assertEqual(indicator.update(5.0), (-1.0, -1.0))

    def test_reset_restores_warmup_and_persistent_zero(self):
        indicator = CG(2, centered=True)
        for price in (1.0, 2.0, 3.0):
            indicator.update(price)
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertFalse(indicator.is_trigger_primed)
        self.assertTrue(math.isnan(indicator.update(1.0).value))
        self.assertEqual(indicator.update(-1.0).value, 0.0)

    def test_validation(self):
        for length in (0, -1, 1.5, 2.0, True, '10'):
            with self.subTest(length=length), self.assertRaises(ValueError):
                CG(length)
        for centered in (0, 1, None, 'book'):
            with self.subTest(centered=centered), self.assertRaises(ValueError):
                CG(centered=centered)

    def test_reference_generation_requires_confirmation(self):
        # Simulate an unconfirmed matrix without generating or writing data.
        with patch.object(MASTER, 'REFERENCE_CASES_CONFIRMED', False), tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(RuntimeError):
                MASTER.generate_reference_data(INPUT_CLOSE, Path(folder))
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_saved_reference_arrays_if_confirmed(self):
        saved = runpy.run_path(str(DIRECTORY / 'test_testdata.py'))
        names = [name for name in saved if name.startswith('EXPECTED_')]
        if not MASTER.REFERENCE_CASES_CONFIRMED:
            self.assertEqual(names, [])
            return
        self.assertEqual(len(names), 2 * len(MASTER.REFERENCE_CASES))
        for case in MASTER.REFERENCE_CASES:
            indicator = CG(case.length, centered=case.centered)
            suffix = f'L{case.length}_C{int(case.centered)}'
            value = saved[f'EXPECTED_{suffix}_CG']
            trigger = saved[f'EXPECTED_{suffix}_TR']
            self.assertEqual(len(value), 252)
            self.assertEqual(len(trigger), 252)
            for index, price in enumerate(INPUT_CLOSE):
                result = indicator.update(price)
                self.assertNumber(result.value, value[index])
                self.assertNumber(result.trigger, trigger[index])

    def test_other_language_arrays_and_comments_are_exact_copies(self):
        saved = runpy.run_path(str(DIRECTORY / 'test_testdata.py'))
        python_comments = re.findall(
            r'^# ([^\n]+)\n# ([^\n]+)\n(EXPECTED_[A-Z0-9_]+) = \[\n',
            (DIRECTORY / 'test_testdata.py').read_text(), flags=re.MULTILINE)
        patterns = {
            'testdata_test.go': r'var (expected\w+) = \[\]float64\{\n(.*?)\n\}',
            'testdata.ts': r'export const (expected\w+): number\[\] = \[\n(.*?)\n\];',
            'testdata.rs': r'    pub fn (expected_\w+)\(\) -> Vec<f64> \{\n        vec!\[\n(.*?)\n        \]',
            'testdata.zig': r'pub fn (expected\w+)\(\) \[252\]f64 \{\n    return \.\{\n(.*?)\n    \};',
        }
        for filename, declaration in patterns.items():
            entries = re.findall(r'^// ([^\n]+)\n// ([^\n]+)\n' + declaration,
                                 (DIRECTORY / filename).read_text(),
                                 flags=re.MULTILINE | re.DOTALL)
            self.assertEqual(len(entries), len(python_comments), filename)
            for (purpose, parameters, name, body), py_entry in zip(entries, python_comments):
                py_purpose, py_parameters, py_name = py_entry
                suffix = py_name.removeprefix('EXPECTED_')
                target = ('expected_' + suffix.lower() if filename.endswith('.rs')
                          else 'expected' + suffix)
                self.assertEqual((purpose, parameters, name), (py_purpose, py_parameters, target))
                tokens = [token.strip() for token in body.split(',') if token.strip()]
                self.assertEqual(len(tokens), 252, name)
                for index, token in enumerate(tokens):
                    actual = (math.nan if token in ('math.NaN()', 'NaN', 'f64::NAN', 'nan')
                              else float(token))
                    self.assertNumber(actual, saved[py_name][index], delta=0.0)


if __name__ == '__main__':
    unittest.main()
