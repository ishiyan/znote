"""Source arithmetic, independent rational oracle and streaming-state tests."""

import ast
from fractions import Fraction
import importlib.util
import math
from pathlib import Path
import re
import runpy
import tempfile
import unittest
from unittest.mock import patch


DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('rvi_master', DIRECTORY / 'relative-vigor-index.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
RVI = MASTER.RelativeVigorIndex
BAR = MASTER.PriceBar
FIXTURE = runpy.run_path(str(DIRECTORY / 'test_testdata.py'))
BARS = MASTER._fixture_bars(FIXTURE['INPUT_CLOSE'], DIRECTORY)


def source_outputs(bars, length, mode):
    """Literal source FIR and sum expressions with complete-history masks."""
    first = length + 2  # Zero-based index of the first full main RVI.
    components = []
    rvi = []
    previous = 0.0
    outputs = []
    for index, bar in enumerate(bars):
        if index < 3:
            components.append((math.nan, math.nan))
        else:
            c0, c1, c2, c3 = bars[index], bars[index - 1], bars[index - 2], bars[index - 3]
            value1 = ((c0.close - c0.open) + 2 * (c1.close - c1.open)
                      + 2 * (c2.close - c2.open) + (c3.close - c3.open)) / 6
            value2 = ((c0.high - c0.low) + 2 * (c1.high - c1.low)
                      + 2 * (c2.high - c2.low) + (c3.high - c3.low)) / 6
            components.append((value1, value2))
        if index < first:
            rvi.append(math.nan)
            outputs.append((math.nan, math.nan))
            continue
        num = 0.0
        denom = 0.0
        for count in range(length):
            num = num + components[index - count][0]
            denom = denom + components[index - count][1]
        if denom != 0:
            previous = num / denom
        rvi.append(previous)
        if mode == 'lag':
            signal = rvi[index - 1] if index > first else math.nan
        elif index >= first + 3:
            signal = (rvi[index] + 2 * rvi[index - 1]
                      + 2 * rvi[index - 2] + rvi[index - 3]) / 6
        else:
            signal = math.nan
        outputs.append((previous, signal))
    return outputs


def rational_outputs(bars, length, mode):
    """Independent combined-kernel oracle using exact decimal rational inputs.

    Convolve the FIR integer taps with the summation window. The common /6
    cancels exactly in the ratio. This uses no ring, stage FIR or float sums.
    """
    taps = (1, 2, 2, 1)
    kernel = [sum(taps[j] for j in range(4) if 0 <= age - j < length)
              for age in range(length + 3)]
    bodies = [Fraction(str(bar.close)) - Fraction(str(bar.open)) for bar in bars]
    ranges = [Fraction(str(bar.high)) - Fraction(str(bar.low)) for bar in bars]
    history = []
    outputs = []
    for index in range(len(bars)):
        if index < length + 2:
            outputs.append((math.nan, math.nan))
            continue
        numerator = sum(weight * bodies[index - age] for age, weight in enumerate(kernel))
        denominator = sum(weight * ranges[index - age] for age, weight in enumerate(kernel))
        value = numerator / denominator if denominator else (history[-1] if history else Fraction(0))
        history.append(value)
        if mode == 'lag' and len(history) >= 2:
            signal = float(history[-2])
        elif mode == 'fir' and len(history) >= 4:
            signal = float(sum(taps[age] * history[-1 - age] for age in range(4)) / 6)
        else:
            signal = math.nan
        outputs.append((float(value), signal))
    return outputs


class TestRelativeVigorIndex(unittest.TestCase):
    def assertNumber(self, actual, expected, *, delta=1e-12):
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual))
        else:
            self.assertAlmostEqual(actual, expected, delta=delta)

    def test_all_cases_match_article_and_book_loops_exactly(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(length=case.length, mode=case.trigger_mode):
                indicator = RVI(case.length, trigger_mode=case.trigger_mode)
                references = source_outputs(BARS, case.length, case.trigger_mode)
                for bar, expected in zip(BARS, references):
                    for actual, reference in zip(indicator.update(bar), expected):
                        self.assertNumber(actual, reference, delta=0.0)

    def test_all_cases_match_independent_rational_convolution(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(length=case.length, mode=case.trigger_mode):
                indicator = RVI(case.length, trigger_mode=case.trigger_mode)
                references = rational_outputs(BARS, case.length, case.trigger_mode)
                for bar, expected in zip(BARS, references):
                    for actual, reference in zip(indicator.update(bar), expected):
                        self.assertNumber(actual, reference)

    def test_warmup_is_independent_for_the_two_outputs(self):
        for length in (1, 8, 10, 246, 248, 249, 252):
            for mode in ('fir', 'lag'):
                indicator = RVI(length, trigger_mode=mode)
                missing_value = length + 2
                missing_signal = length + (5 if mode == 'fir' else 3)
                for index, bar in enumerate(BARS):
                    result = indicator.update(bar)
                    self.assertEqual(math.isnan(result.value), index < missing_value)
                    self.assertEqual(math.isnan(result.signal), index < missing_signal)
                    self.assertEqual(indicator.is_primed, index >= missing_value)
                    self.assertEqual(indicator.is_signal_primed, index >= missing_signal)

    def test_signal_modes_share_main_value_but_differ_in_signal(self):
        article = RVI(1)
        book = RVI(1, trigger_mode='lag')
        for body in range(1, 8):
            a = article.update(BAR(0, 10, 0, body))
            b = book.update(BAR(0, 10, 0, body))
            self.assertNumber(a.value, b.value, delta=0.0)
        self.assertAlmostEqual(a.value, 0.55)
        self.assertAlmostEqual(a.signal, 0.4)
        self.assertAlmostEqual(b.signal, 0.45)

    def test_ratio_is_taken_after_smoothing_components(self):
        indicator = RVI(1)
        for range_value in (1, 2, 4, 8):
            result = indicator.update(BAR(0, range_value, 0, 1))
        self.assertAlmostEqual(result.value, 2.0 / 7.0)
        wrongly_filtered_ratios = (1 / 8 + 2 / 4 + 2 / 2 + 1) / 6
        self.assertNotAlmostEqual(result.value, wrongly_filtered_ratios)

    def test_fixed_fir_rejects_two_and_three_bar_components(self):
        self.assertEqual(MASTER._fir4([1, -1, 1, -1], 0), 0.0)
        self.assertEqual(MASTER._fir4([1, -0.5, -0.5, 1], 0), 0.0)

    def test_constant_direction_and_signal(self):
        for length in (1, 5, 10):
            for mode in ('fir', 'lag'):
                indicator = RVI(length, trigger_mode=mode)
                for _ in range(length + 6):
                    result = indicator.update(BAR(2, 10, 0, 7))
                self.assertEqual(result, (0.5, 0.5))

    def test_zero_range_holds_previous_rvi(self):
        for mode in ('fir', 'lag'):
            indicator = RVI(1, trigger_mode=mode)
            for _ in range(7):
                indicator.update(BAR(0, 2, 0, 1))
            for _ in range(4):
                result = indicator.update(BAR(5, 5, 5, 5))
                self.assertEqual(result, (0.5, 0.5))

    def test_initial_zero_range_is_available_zero_after_warmup(self):
        for mode in ('fir', 'lag'):
            indicator = RVI(1, trigger_mode=mode)
            for index in range(7):
                result = indicator.update(BAR(5, 5, 5, 5))
                self.assertNumber(result.value, math.nan if index < 3 else 0.0)
            self.assertEqual(result.signal, 0.0)

    def test_negative_range_uses_article_nonzero_guard(self):
        indicator = RVI(1)
        for _ in range(4):
            result = indicator.update(BAR(0, 0, 1, 1))
        self.assertEqual(result.value, -1.0)

    def test_subnormal_nonzero_range_is_not_replaced_by_epsilon(self):
        indicator = RVI(1)
        for _ in range(4):
            result = indicator.update(BAR(0.0, 1e-309, 0.0, 1e-309))
        self.assertEqual(result.value, 1.0)

    def test_missing_field_skips_the_entire_bar(self):
        skipped = RVI(3)
        uninterrupted = RVI(3)
        for index, bar in enumerate(BARS[:20]):
            fields = list(bar)
            fields[index % 4] = math.nan
            missing = skipped.update(BAR(*fields))
            self.assertTrue(math.isnan(missing.value) and math.isnan(missing.signal))
            for actual, expected in zip(skipped.update(bar), uninterrupted.update(bar)):
                self.assertNumber(actual, expected, delta=0.0)

    def test_infinity_rejected_before_mutation(self):
        indicator = RVI(1)
        pristine = RVI(1)
        for index in range(4):
            fields = list(BARS[0])
            fields[index] = math.inf if index % 2 else -math.inf
            with self.assertRaises(ValueError):
                indicator.update(BAR(*fields))
        for bar in BARS[:8]:
            for actual, expected in zip(indicator.update(bar), pristine.update(bar)):
                self.assertNumber(actual, expected, delta=0.0)

    def test_reset_restarts_every_filter_and_history(self):
        indicator = RVI(3, trigger_mode='lag')
        for bar in BARS[:20]:
            indicator.update(bar)
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertFalse(indicator.is_signal_primed)
        pristine = RVI(3, trigger_mode='lag')
        for bar in BARS[:12]:
            for actual, expected in zip(indicator.update(bar), pristine.update(bar)):
                self.assertNumber(actual, expected, delta=0.0)

    def test_common_scale_and_translation_preserve_rvi(self):
        indicator = RVI(10)
        transformed = RVI(10)
        for bar in BARS:
            adjusted = BAR(*(8.0 * field + 32.0 for field in bar))
            for actual, expected in zip(transformed.update(adjusted), indicator.update(bar)):
                self.assertNumber(actual, expected)

    def test_parameter_validation(self):
        for length in (0, -1, True, 1.5, 2.0, '10'):
            with self.assertRaises(ValueError):
                RVI(length)
        for mode in ('sma', 'book', None, 1):
            with self.assertRaises(ValueError):
                RVI(trigger_mode=mode)

    def test_embedded_closes_and_matching_ohlc_are_unmodified(self):
        root = ast.parse((DIRECTORY / 'relative-vigor-index.py').read_text())
        main = next(n for n in root.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        close = next(ast.literal_eval(n.value) for n in main.body
                     if isinstance(n, ast.Assign) and n.targets[0].id == 'input_close')
        self.assertEqual(close, FIXTURE['INPUT_CLOSE'])
        self.assertEqual(len(BARS), 252)
        self.assertEqual([bar.close for bar in BARS], close)

    def test_reference_generation_requires_its_own_confirmation(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(MASTER, 'REFERENCE_CASES_CONFIRMED', False):
            with self.assertRaises(RuntimeError):
                MASTER.generate_reference_data(FIXTURE['INPUT_CLOSE'], Path(folder))
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_saved_arrays_and_target_language_copies(self):
        saved = runpy.run_path(str(DIRECTORY / 'test_testdata.py'))
        expected_names = [name for name in saved if name.startswith('EXPECTED_')]
        if not MASTER.REFERENCE_CASES_CONFIRMED:
            self.assertEqual(expected_names, [])
            return
        self.assertEqual(len(expected_names), 2 * len(MASTER.REFERENCE_CASES))
        for case in MASTER.REFERENCE_CASES:
            suffix = f'L{case.length}_M{MASTER.TRIGGER_MODE_CODES[case.trigger_mode]}'
            indicator = RVI(case.length, trigger_mode=case.trigger_mode)
            values = saved[f'EXPECTED_{suffix}_RVI']
            signals = saved[f'EXPECTED_{suffix}_SIG']
            self.assertEqual(len(values), 252)
            self.assertEqual(len(signals), 252)
            for index, bar in enumerate(BARS):
                result = indicator.update(bar)
                self.assertNumber(result.value, values[index])
                self.assertNumber(result.signal, signals[index])

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
                                 (DIRECTORY / filename).read_text(), flags=re.MULTILINE | re.DOTALL)
            self.assertEqual(len(entries), len(python_comments), filename)
            for (purpose, parameters, name, body), py_entry in zip(entries, python_comments):
                py_purpose, py_parameters, py_name = py_entry
                suffix = py_name.removeprefix('EXPECTED_')
                target = ('expected_' + suffix.lower() if filename.endswith('.rs') else 'expected' + suffix)
                self.assertEqual((purpose, parameters, name), (py_purpose, py_parameters, target))
                tokens = [token.strip() for token in body.split(',') if token.strip()]
                self.assertEqual(len(tokens), 252, name)
                for index, token in enumerate(tokens):
                    actual = (math.nan if token in ('math.NaN()', 'NaN', 'f64::NAN', 'nan') else float(token))
                    self.assertNumber(actual, saved[py_name][index], delta=0.0)


if __name__ == '__main__':
    unittest.main()
