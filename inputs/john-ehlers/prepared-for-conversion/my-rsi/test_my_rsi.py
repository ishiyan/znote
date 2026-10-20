"""Independent source and behavioral verification; Python standard library only."""

import ast
import math
from pathlib import Path
import runpy
import tempfile
import unittest


DIRECTORY = Path(__file__).resolve().parent
MASTER_PATH = DIRECTORY / "my-rsi.py"
MASTER = runpy.run_path(str(MASTER_PATH))
MyRSI = MASTER["MyRSI"]
CASES = MASTER["REFERENCE_CASES"]
DATA = runpy.run_path(str(DIRECTORY / "test_testdata.py"))
INPUT_CLOSE = DATA["INPUT_CLOSE"]


def article_reference(prices, smooth, length):
    """Independent batch translation using absolute indices and zero lags.

    Full-precision replacements follow the article's exp/degree-cosine setup.
    Only actual filtered observations enter the RSI; source accumulation uses
    literal left association and newest-to-oldest traversal.
    """
    a = math.exp(-math.sqrt(2.0) * math.pi / smooth)
    c2 = 2.0 * a * math.cos(math.radians(math.sqrt(2.0) * 180.0 / smooth))
    c3 = -a * a
    c1 = 1.0 - c2 - c3
    filtered = [math.nan]
    outputs = [math.nan]
    held = 0.0
    for t in range(1, len(prices)):
        old1 = filtered[t - 1] if t >= 2 else 0.0
        old2 = filtered[t - 2] if t >= 3 else 0.0
        current = c1 * (prices[t] + prices[t - 1]) / 2.0 + c2 * old1 + c3 * old2
        filtered.append(current)
        if t < length + 1:
            outputs.append(math.nan)
            continue
        cu = 0.0
        cd = 0.0
        for k in range(length):
            newer = filtered[t - k]
            older = filtered[t - k - 1]
            if newer - older > 0.0:
                cu = cu + newer - older
            if newer - older < 0.0:
                cd = cd + older - newer
        if cu + cd != 0.0:
            held = (cu - cd) / (cu + cd)
        outputs.append(held)
    return filtered, outputs


class MyRSITests(unittest.TestCase):
    def assertSeriesClose(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for t, (value, reference) in enumerate(zip(actual, expected)):
            if math.isnan(reference):
                self.assertTrue(math.isnan(value), f"index {t}")
            else:
                self.assertTrue(math.isclose(value, reference, rel_tol=5e-13, abs_tol=5e-13),
                                f"index {t}: {value} != {reference}")

    def test_all_reference_cases_against_independent_article_translation(self):
        for case in CASES:
            with self.subTest(smooth=case.smooth_length, rsi=case.rsi_length):
                indicator = MyRSI(case.smooth_length, case.rsi_length)
                actual = []
                filters = []
                for close in INPUT_CLOSE:
                    actual.append(indicator.update(close))
                    filters.append(indicator.filtered_value)
                expected_filter, expected = article_reference(INPUT_CLOSE, case.smooth_length, case.rsi_length)
                self.assertSeriesClose(actual, expected)
                self.assertSeriesClose(filters, expected_filter)
                self.assertEqual(indicator.warmup_bars, case.rsi_length + 1)
                self.assertEqual(indicator.is_primed, 252 > indicator.warmup_bars)
                self.assertTrue(all(-1.0 - 1e-12 <= value <= 1.0 + 1e-12
                                    for value in actual if math.isfinite(value)))

    def test_startup_requires_raw_pair_and_full_actual_filtered_window(self):
        indicator = MyRSI()
        self.assertTrue(math.isnan(indicator.filtered_value))
        self.assertTrue(math.isnan(indicator.update(INPUT_CLOSE[0])))
        self.assertTrue(math.isnan(indicator.filtered_value))
        self.assertTrue(math.isnan(indicator.update(INPUT_CLOSE[1])))
        angle = math.sqrt(2.0) * math.pi / 8.0
        a = math.exp(-angle)
        c1 = 1.0 - 2.0 * a * math.cos(angle) + a * a
        self.assertAlmostEqual(indicator.filtered_value, c1 * sum(INPUT_CLOSE[:2]) / 2.0, places=13)
        for value in INPUT_CLOSE[2:11]:
            self.assertTrue(math.isnan(indicator.update(value)))
            self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isfinite(indicator.update(INPUT_CLOSE[11])))
        self.assertTrue(indicator.is_primed)

    def test_zero_input_produces_valid_neutral_flat_windows(self):
        for length in (1, 2, 10):
            indicator = MyRSI(8.0, length)
            values = [indicator.update(0.0) for _ in range(30)]
            self.assertTrue(all(math.isnan(value) for value in values[:length + 1]))
            self.assertEqual(values[length + 1:], [0.0] * (29 - length))

    def test_one_change_limit_retains_direction_for_flat_filtered_window(self):
        # Let a ramp become constant. The damped filter eventually reaches
        # exact binary64 ties; on those bars the source must retain the last
        # nonzero direction rather than resetting it or dividing by zero.
        indicator = MyRSI(3.0, 1)
        prices = [float(t) for t in range(21)] + [20.0] * 300
        previous_filter = previous_output = math.nan
        retained_ties = 0
        for price in prices:
            value = indicator.update(price)
            if indicator.is_primed and indicator.filtered_value == previous_filter:
                self.assertEqual(value, previous_output)
                self.assertIn(value, (-1.0, 1.0))
                retained_ties += 1
            previous_filter, previous_output = indicator.filtered_value, value
        self.assertGreater(retained_ties, 0)

    def test_increasing_and_decreasing_settled_ramps_reach_full_swing(self):
        for sign in (1.0, -1.0):
            indicator = MyRSI(8.0, 10)
            values = [indicator.update(sign * float(t)) for t in range(80)]
            self.assertEqual(values[-10:], [sign] * 10)

    def test_nonfinite_and_overflow_inputs_are_rejected_without_advancing(self):
        indicator = MyRSI()
        first = [indicator.update(price) for price in INPUT_CLOSE[:7]]
        for invalid in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(invalid)
        self.assertSeriesClose(first + [indicator.update(price) for price in INPUT_CLOSE[7:]],
                               article_reference(INPUT_CLOSE, 8.0, 10)[1])
        other = MyRSI()
        other.update(1e308)
        with self.assertRaises(ValueError):
            other.update(1e308)  # Pair addition overflows; stored first close remains.
        self.assertTrue(math.isnan(other.filtered_value))
        self.assertTrue(math.isnan(other.update(-1e308)))
        self.assertEqual(other.filtered_value, 0.0)

    def test_reset_preserves_configuration_and_replays_outputs(self):
        indicator = MyRSI(8.5, 14)
        first = [indicator.update(close) for close in INPUT_CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isnan(indicator.output))
        self.assertEqual((indicator.smooth_length, indicator.rsi_length), (8.5, 14))
        self.assertSeriesClose([indicator.update(close) for close in INPUT_CLOSE], first)

    def test_parameter_domains_and_read_only_properties(self):
        for smooth in (True, False, 0.0, -1.0, 2.9, math.nan, math.inf, -math.inf, 1e300):
            with self.assertRaises(ValueError):
                MyRSI(smooth, 10)
        for length in (True, False, 0, -1, 10.0, 3.5, math.nan):
            with self.assertRaises(ValueError):
                MyRSI(8.0, length)
        indicator = MyRSI(20.0, 1)
        with self.assertRaises(AttributeError):
            indicator.smooth_length = 10.0
        with self.assertRaises(AttributeError):
            indicator.rsi_length = 10

    def test_embedded_closes_and_original_input_arrays(self):
        tree = ast.parse(MASTER_PATH.read_text())
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "INPUT_CLOSE"
                            for target in node.targets))
        self.assertEqual(len(INPUT_CLOSE), 252)
        self.assertEqual(ast.literal_eval(node.value), INPUT_CLOSE)
        original = runpy.run_path(str(DIRECTORY.parent / "test_testdata.py"))
        for name in ("INPUT_CLOSE", "INPUT_HIGH", "INPUT_LOW", "INPUT_OPEN"):
            self.assertEqual(DATA[name], original[name])

    def test_reference_cases_unique_and_fixture_outputs_if_confirmed(self):
        self.assertTrue(1 <= len(CASES) <= 64)
        names = {"EXPECTED_" + MASTER["_case_suffix"](case) for case in CASES}
        self.assertEqual(len(names), len(CASES))
        present = {name for name in DATA if name.startswith("EXPECTED_")}
        if MASTER["REFERENCE_CASES_CONFIRMED"]:
            self.assertEqual(present, names)
            for case in CASES:
                self.assertSeriesClose(DATA["EXPECTED_" + MASTER["_case_suffix"](case)],
                                       article_reference(INPUT_CLOSE, case.smooth_length, case.rsi_length)[1])
        else:
            self.assertEqual(present, set())

    def test_generator_respects_pending_confirmation(self):
        if MASTER["REFERENCE_CASES_CONFIRMED"]:
            return
        with tempfile.TemporaryDirectory() as name:
            path = Path(name)
            with self.assertRaisesRegex(ValueError, "confirm"):
                MASTER["generate_reference_data"](INPUT_CLOSE, path)
            self.assertEqual(list(path.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
