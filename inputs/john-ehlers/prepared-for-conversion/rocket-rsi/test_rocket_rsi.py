"""Independent source and behavioral tests; Python standard library only."""

import ast
import math
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


DIRECTORY = Path(__file__).resolve().parent
MASTER_PATH = DIRECTORY / "rocket-rsi.py"
MASTER = runpy.run_path(str(MASTER_PATH))
RocketRSI = MASTER["RocketRSI"]
CASES = MASTER["REFERENCE_CASES"]
DATA = runpy.run_path(str(DIRECTORY / "test_testdata.py"))
INPUT_CLOSE = DATA["INPUT_CLOSE"]
FISHER_LIMIT = 0.5 * math.log((1.0 + 0.999) / (1.0 - 0.999))


def article_reference(prices, smooth, length):
    """Independent batch translation with absolute-index source lags.

    The real-data contract waits for the momentum lag, the previous actual
    momentum, and R actual filtered changes. Only private recursive filter
    lags start at zero. Full-precision constants replace the article's printed
    approximations, with degree conversion independently written below.
    """
    a = math.exp(-math.sqrt(2.0) * math.pi / smooth)
    c2 = 2.0 * a * math.cos(math.radians(math.sqrt(2.0) * 180.0 / smooth))
    c3 = -a * a
    c1 = 1.0 - c2 - c3
    momentum = [math.nan] * len(prices)
    filtered = [math.nan] * len(prices)
    ratios = [math.nan] * len(prices)
    outputs = [math.nan] * len(prices)
    held = 0.0
    for t in range(length - 1, len(prices)):
        momentum[t] = prices[t] - prices[t - (length - 1)]
    for t in range(length, len(prices)):
        prev1 = filtered[t - 1] if t > length else 0.0
        prev2 = filtered[t - 2] if t > length + 1 else 0.0
        filtered[t] = (c1 * (momentum[t] + momentum[t - 1]) / 2.0
                       + c2 * prev1 + c3 * prev2)
        if t < 2 * length:
            continue
        cu = 0.0
        cd = 0.0
        for count in range(length):
            newer = filtered[t - count]
            older = filtered[t - count - 1]
            if newer - older > 0.0:
                cu = cu + newer - older
            if newer - older < 0.0:
                cd = cd + older - newer
        if cu + cd != 0.0:
            held = (cu - cd) / (cu + cd)
        if held > 0.999:
            held = 0.999
        if held < -0.999:
            held = -0.999
        ratios[t] = held
        outputs[t] = 0.5 * math.log((1.0 + held) / (1.0 - held))
    return momentum, filtered, ratios, outputs


class RocketRSITests(unittest.TestCase):
    def assertSeriesClose(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for index, (value, reference) in enumerate(zip(actual, expected)):
            if math.isnan(reference):
                self.assertTrue(math.isnan(value), f"index {index}")
            else:
                self.assertTrue(math.isclose(value, reference, rel_tol=5e-13, abs_tol=5e-13),
                                f"index {index}: {value} != {reference}")

    def test_all_cases_and_intermediates_match_independent_article(self):
        for case in CASES:
            with self.subTest(smooth=case.smooth_length, rsi=case.rsi_length):
                indicator = RocketRSI(case.smooth_length, case.rsi_length)
                actual = [[], [], [], []]
                for price in INPUT_CLOSE:
                    value = indicator.update(price)
                    if math.isfinite(value):
                        self.assertEqual(value, indicator.output)
                    else:
                        self.assertTrue(math.isnan(indicator.output))
                    for values, current in zip(actual, indicator.state):
                        values.append(current)
                expected = article_reference(INPUT_CLOSE, case.smooth_length, case.rsi_length)
                for values, reference in zip(actual, expected):
                    self.assertSeriesClose(values, reference)
                self.assertEqual(indicator.warmup_bars, 2 * case.rsi_length)
                self.assertEqual(indicator.momentum_lag, case.rsi_length - 1)
                self.assertEqual(indicator.is_primed, 252 > indicator.warmup_bars)
                self.assertTrue(all(abs(value) <= FISHER_LIMIT + 1e-12
                                    for value in actual[3] if math.isfinite(value)))

    def test_exact_startup_and_momentum_lag(self):
        indicator = RocketRSI(8.0, 3)
        for price in (10.0, 12.0):
            self.assertTrue(math.isnan(indicator.update(price)))
            self.assertTrue(math.isnan(indicator.state.momentum))
        self.assertTrue(math.isnan(indicator.update(15.0)))
        self.assertEqual(indicator.state.momentum, 5.0)  # 15 - Close[2]=10.
        self.assertTrue(math.isnan(indicator.state.filtered))
        self.assertTrue(math.isnan(indicator.update(21.0)))
        self.assertEqual(indicator.state.momentum, 9.0)  # 21 - Close[2]=12.
        angle = math.sqrt(2.0) * math.pi / 8.0
        a = math.exp(-angle)
        c1 = 1.0 - 2.0 * a * math.cos(angle) + a * a
        self.assertAlmostEqual(indicator.state.filtered, c1 * (9.0 + 5.0) / 2.0, places=13)
        for price in (25.0, 30.0):
            self.assertTrue(math.isnan(indicator.update(price)))
            self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isfinite(indicator.update(40.0)))  # t=6=2*R.
        self.assertTrue(indicator.is_primed)

    def test_zero_lag_momentum_limit_is_zero_after_structural_warmup(self):
        for smooth in (3.0, 8.0, 8.5, 252.0):
            indicator = RocketRSI(smooth, 1)
            values = [indicator.update(price) for price in INPUT_CLOSE]
            self.assertTrue(all(math.isnan(value) for value in values[:2]))
            self.assertEqual(values[2:], [0.0] * 250)
            self.assertEqual(indicator.state.momentum, 0.0)
            self.assertEqual(indicator.state.filtered, 0.0)

    def test_constant_price_is_zero_momentum_and_neutral_output(self):
        for length in (1, 2, 10, 30):
            indicator = RocketRSI(8.0, length)
            values = [indicator.update(100.0) for _ in range(100)]
            self.assertTrue(all(math.isnan(value) for value in values[:2 * length]))
            self.assertEqual(values[2 * length:], [0.0] * (100 - 2 * length))

    def test_directional_filtered_momentum_clips_then_fisher_transforms(self):
        # Quadratic raw price gives linearly increasing momentum, unlike a
        # linear raw price whose momentum is constant. Its late R windows are
        # entirely one-directional, hence unclipped +/-1 and clipped +/-0.999.
        for sign in (1.0, -1.0):
            indicator = RocketRSI(3.0, 2)
            values = [indicator.update(sign * float(t * t)) for t in range(80)]
            self.assertEqual(indicator.state.myrsi, sign * 0.999)
            bound = 0.5 * math.log((1.0 + sign * 0.999) / (1.0 - sign * 0.999))
            self.assertEqual(values[-10:], [bound] * 10)
            self.assertGreater(abs(bound), 3.0)  # Printed comment is approximate.

    def test_flat_filtered_window_retains_previous_clipped_ratio(self):
        # A ramp's momentum becomes constant; eventually damped recursion
        # reaches exact binary64 ties. Verify holding on those exact windows.
        indicator = RocketRSI(3.0, 2)
        filters = []
        previous_ratio = math.nan
        held_count = 0
        for t in range(500):
            value = indicator.update(float(t))
            filters.append(indicator.state.filtered)
            if indicator.is_primed and filters[-1] == filters[-2] == filters[-3]:
                self.assertEqual(indicator.state.myrsi, previous_ratio)
                self.assertLessEqual(abs(indicator.state.myrsi), 0.999)
                expected = 0.5 * math.log((1.0 + previous_ratio) / (1.0 - previous_ratio))
                self.assertEqual(value, expected)
                held_count += 1
            previous_ratio = indicator.state.myrsi
        self.assertGreater(held_count, 0)

    def test_price_offset_invariance_and_negation_symmetry(self):
        prices = [float((t * 7) % 23 - 10) for t in range(100)]
        baseline = RocketRSI(8.0, 10)
        shifted = RocketRSI(8.0, 10)
        negated = RocketRSI(8.0, 10)
        original = [baseline.update(price) for price in prices]
        self.assertSeriesClose([shifted.update(price + 1000.0) for price in prices], original)
        self.assertSeriesClose([negated.update(-price) for price in prices],
                               [-value for value in original])

    def test_nonfinite_inputs_rejected_at_each_stage_without_advancing(self):
        for prefix_length in (0, 5, 10, 20, 100):
            with self.subTest(prefix_length=prefix_length):
                indicator = RocketRSI()
                values = [indicator.update(price) for price in INPUT_CLOSE[:prefix_length]]
                for invalid in (math.nan, math.inf, -math.inf):
                    with self.assertRaises(ValueError):
                        indicator.update(invalid)
                values += [indicator.update(price) for price in INPUT_CLOSE[prefix_length:]]
                self.assertSeriesClose(values, article_reference(INPUT_CLOSE, 8.0, 10)[3])

    def test_momentum_overflow_rejection_preserves_actual_raw_history(self):
        indicator = RocketRSI(8.0, 2)
        indicator.update(-1e308)
        with self.assertRaises(ValueError):
            indicator.update(1e308)
        self.assertTrue(math.isnan(indicator.state.momentum))
        self.assertTrue(math.isnan(indicator.update(-1e308)))
        self.assertEqual(indicator.state.momentum, 0.0)

    def test_reset_configuration_and_replay(self):
        indicator = RocketRSI(8.5, 14)
        first = [indicator.update(price) for price in INPUT_CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertTrue(all(math.isnan(value) for value in indicator.state))
        self.assertEqual((indicator.smooth_length, indicator.rsi_length), (8.5, 14))
        self.assertSeriesClose([indicator.update(price) for price in INPUT_CLOSE], first)

    def test_parameter_domains_and_read_only_properties(self):
        for smooth in (True, False, 0.0, -1.0, 2.9, math.nan, math.inf, -math.inf, 1e300):
            with self.assertRaises(ValueError):
                RocketRSI(smooth, 10)
        for length in (True, False, 0, -1, 10.0, 3.5, math.nan):
            with self.assertRaises(ValueError):
                RocketRSI(8.0, length)
        indicator = RocketRSI(20.0, 1)
        with self.assertRaises(AttributeError):
            indicator.smooth_length = 10.0
        with self.assertRaises(AttributeError):
            indicator.rsi_length = 10

    def test_embedded_closes_and_all_original_inputs(self):
        node = next(node for node in ast.walk(ast.parse(MASTER_PATH.read_text()))
                    if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "INPUT_CLOSE"
                            for target in node.targets))
        self.assertEqual(len(INPUT_CLOSE), 252)
        self.assertEqual(ast.literal_eval(node.value), INPUT_CLOSE)
        original = runpy.run_path(str(DIRECTORY.parent / "test_testdata.py"))
        for name in ("INPUT_CLOSE", "INPUT_HIGH", "INPUT_LOW", "INPUT_OPEN"):
            self.assertEqual(DATA[name], original[name])

    def test_reference_cases_and_written_expected_outputs_when_confirmed(self):
        self.assertTrue(1 <= len(CASES) <= 64)
        names = {"EXPECTED_" + MASTER["_case_suffix"](case) for case in CASES}
        self.assertEqual(len(names), len(CASES))
        present = {name for name in DATA if name.startswith("EXPECTED_")}
        if MASTER["REFERENCE_CASES_CONFIRMED"]:
            self.assertEqual(present, names)
            for case in CASES:
                self.assertSeriesClose(DATA["EXPECTED_" + MASTER["_case_suffix"](case)],
                                       article_reference(INPUT_CLOSE, case.smooth_length, case.rsi_length)[3])
        else:
            self.assertEqual(present, set())

    def test_reference_generation_requires_explicit_confirmation(self):
        # Exercise the guard even after this table has been authorized. Patch
        # only its temporary in-memory flag; retain recorded user confirmation.
        with tempfile.TemporaryDirectory() as name:
            target = Path(name)
            with patch.dict(MASTER["generate_reference_data"].__globals__,
                            {"REFERENCE_CASES_CONFIRMED": False}):
                with self.assertRaisesRegex(ValueError, "confirm"):
                    MASTER["generate_reference_data"](INPUT_CLOSE, target)
            self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
