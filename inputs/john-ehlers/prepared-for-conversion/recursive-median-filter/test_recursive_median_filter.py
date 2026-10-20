"""Focused standard-library checks for the article's nonlinear filter contract.

Run from this folder with: python3 -m unittest -v
These tests intentionally use independent order-statistic/analytic references,
not another instance of the streaming master as its own expected output.
"""

import ast
import math
from pathlib import Path
import runpy
import statistics
import tempfile
import unittest


DIRECTORY = Path(__file__).resolve().parent
MASTER_PATH = DIRECTORY / "recursive-median-filter.py"
MASTER = runpy.run_path(str(MASTER_PATH))
RecursiveMedianFilter = MASTER["RecursiveMedianFilter"]
CASES = MASTER["REFERENCE_CASES"]
DATA = runpy.run_path(str(DIRECTORY / "test_testdata.py"))
INPUT_CLOSE = DATA["INPUT_CLOSE"]


def article_reference(prices, period):
    """Batch evaluation of the literal article, with specified zero startup.

    Statistics.median provides an independent standard-library rank reference.
    Degree conversion below follows the source rather than sharing coefficients
    or internal histories with the implementation being tested.
    """
    degrees = 360.0 / period
    cosine = math.cos(math.radians(degrees))
    alpha = (cosine + math.sin(math.radians(degrees)) - 1.0) / cosine
    previous = 0.0
    values = [math.nan] * min(4, len(prices))
    for index in range(4, len(prices)):
        median = statistics.median(prices[index - 4:index + 1])
        previous = alpha * median + (1.0 - alpha) * previous
        values.append(previous)
    return values


class RecursiveMedianFilterTests(unittest.TestCase):
    def assertSeriesClose(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for index, (value, reference) in enumerate(zip(actual, expected)):
            if math.isnan(reference):
                self.assertTrue(math.isnan(value), f"index {index}")
            else:
                self.assertTrue(math.isclose(value, reference, rel_tol=5e-14, abs_tol=5e-14),
                                f"index {index}: {value} != {reference}")

    def test_all_reference_cases_against_literal_article(self):
        for case in CASES:
            with self.subTest(lp_period=case.lp_period):
                indicator = RecursiveMedianFilter(case.lp_period)
                actual = [indicator.update(close) for close in INPUT_CLOSE]
                expected = article_reference(INPUT_CLOSE, case.lp_period)
                self.assertSeriesClose(actual, expected)
                self.assertTrue(indicator.is_primed)
                self.assertEqual(indicator.warmup_bars, 4)

    def test_default_coefficient_and_first_available_value(self):
        indicator = RecursiveMedianFilter()
        self.assertAlmostEqual(indicator.alpha, 1.0 - 1.0 / math.sqrt(3.0), places=15)
        for price in INPUT_CLOSE[:4]:
            self.assertTrue(math.isnan(indicator.update(price)))
            self.assertFalse(indicator.is_primed)
        first = indicator.update(INPUT_CLOSE[4])
        self.assertTrue(indicator.is_primed)
        self.assertAlmostEqual(first, indicator.alpha * 94.375, places=13)

    def test_constant_stream_matches_zero_seed_analytic_solution(self):
        for case in CASES:
            with self.subTest(lp_period=case.lp_period):
                indicator = RecursiveMedianFilter(case.lp_period)
                outputs = [indicator.update(100.0) for _ in range(104)]
                q = 1.0 - indicator.alpha
                for k, value in enumerate(outputs[4:], start=1):
                    expected = 100.0 * (1.0 - q ** k)
                    self.assertTrue(math.isclose(value, expected, rel_tol=2e-13, abs_tol=2e-13))

    def test_one_or_two_isolated_spikes_do_not_change_constant_median(self):
        baseline = [100.0] * 40
        for outliers in ({10: 1000.0}, {10: -1000.0}, {10: 1000.0, 11: 1000.0}):
            prices = baseline.copy()
            for index, value in outliers.items():
                prices[index] = value
            clean = RecursiveMedianFilter()
            noisy = RecursiveMedianFilter()
            self.assertSeriesClose([noisy.update(price) for price in prices],
                                   [clean.update(price) for price in baseline])

    def test_sustained_step_reaches_median_on_third_changed_observation(self):
        baseline = [100.0] * 15
        stepped = baseline + [200.0] * 8
        indicator = RecursiveMedianFilter()
        outputs = [indicator.update(price) for price in stepped]
        clean = article_reference([100.0] * len(stepped), 12.0)
        self.assertSeriesClose(outputs[:17], clean[:17])
        self.assertGreater(outputs[17], clean[17])
        self.assertSeriesClose(outputs, article_reference(stepped, 12.0))

    def test_window_stays_chronological_through_rank_changes_and_ties(self):
        prices = [4.0, 100.0, 1.0, -2.0, 4.0, 0.0, 9.0, -100.0, 9.0, 9.0,
                  2.0, 1.0, 50.0, -3.0, 5.0, 1.0]
        indicator = RecursiveMedianFilter(8.0)
        self.assertSeriesClose([indicator.update(price) for price in prices],
                               article_reference(prices, 8.0))

    def test_nonfinite_inputs_do_not_advance_any_state(self):
        indicator = RecursiveMedianFilter()
        first = [indicator.update(price) for price in INPUT_CLOSE[:3]]
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(value)
            self.assertFalse(indicator.is_primed)
        actual = first + [indicator.update(price) for price in INPUT_CLOSE[3:]]
        self.assertSeriesClose(actual, article_reference(INPUT_CLOSE, 12.0))
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(value)
        self.assertAlmostEqual(indicator.update(123.0),
                               article_reference(INPUT_CLOSE + [123.0], 12.0)[-1], places=12)

    def test_reset_replays_same_zero_seed_and_four_nan_prefix(self):
        indicator = RecursiveMedianFilter(16.0)
        original = [indicator.update(price) for price in INPUT_CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertEqual(indicator.lp_period, 16.0)
        replay = [indicator.update(price) for price in INPUT_CLOSE]
        self.assertSeriesClose(replay, original)

    def test_period_domain_and_read_only_configuration(self):
        for period in (True, False, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0,
                       math.nan, math.inf, -math.inf, 1e300):
            with self.subTest(lp_period=period):
                with self.assertRaises(ValueError):
                    RecursiveMedianFilter(period)
        indicator = RecursiveMedianFilter(4.5)
        self.assertGreater(indicator.alpha, 0.0)
        self.assertLess(indicator.alpha, 1.0)
        with self.assertRaises(AttributeError):
            indicator.lp_period = 24.0

    def test_embedded_inputs_match_all_original_python_input_arrays(self):
        tree = ast.parse(MASTER_PATH.read_text())
        assignment = next(node for node in ast.walk(tree)
                          if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == "INPUT_CLOSE"
                                  for target in node.targets))
        embedded = ast.literal_eval(assignment.value)
        self.assertEqual(len(embedded), 252)
        self.assertEqual(embedded, INPUT_CLOSE)
        original = runpy.run_path(str(DIRECTORY.parent / "test_testdata.py"))
        for name in ("INPUT_CLOSE", "INPUT_HIGH", "INPUT_LOW", "INPUT_OPEN"):
            self.assertEqual(DATA[name], original[name])

    def test_reference_cases_unique_and_generated_outputs_when_confirmed(self):
        self.assertTrue(1 <= len(CASES) <= 64)
        expected_names = {"EXPECTED_" + MASTER["_case_suffix"](case) for case in CASES}
        self.assertEqual(len(expected_names), len(CASES))
        present = {name for name in DATA if name.startswith("EXPECTED_")}
        if MASTER["REFERENCE_CASES_CONFIRMED"]:
            self.assertEqual(present, expected_names)
            for case in CASES:
                name = "EXPECTED_" + MASTER["_case_suffix"](case)
                self.assertEqual(len(DATA[name]), 252)
                self.assertSeriesClose(DATA[name], article_reference(INPUT_CLOSE, case.lp_period))
        else:
            self.assertEqual(present, set())

    def test_generation_refuses_unconfirmed_cases_before_touching_files(self):
        if MASTER["REFERENCE_CASES_CONFIRMED"]:
            return  # The confirmation guard has intentionally been cleared.
        with tempfile.TemporaryDirectory() as name:
            target = Path(name)
            with self.assertRaisesRegex(ValueError, "confirm"):
                MASTER["generate_reference_data"](INPUT_CLOSE, target)
            self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
