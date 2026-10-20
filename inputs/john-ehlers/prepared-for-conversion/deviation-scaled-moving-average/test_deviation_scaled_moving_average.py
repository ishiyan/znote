"""Source-index and behavioral verification for the standalone DSMA master."""

import ast
import contextlib
import io
import math
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest
from unittest.mock import patch


DIRECTORY = Path(__file__).resolve().parent
MASTER_PATH = DIRECTORY / 'deviation-scaled-moving-average.py'
MASTER = runpy.run_path(str(MASTER_PATH))
DSMA = MASTER['DeviationScaledMovingAverage']
CASES = MASTER['REFERENCE_CASES']
DATA = runpy.run_path(str(DIRECTORY / 'test_testdata.py'))
INPUT_CLOSE = DATA['INPUT_CLOSE']
FIXTURES = ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')


def source_reference(prices, period):
    """Absolute-index batch listing based on Mesa/TradeStation and NinjaTrader.

    Filt/Zeros/DSMA prehistory is zero, and Close[2] is first valid at t=2.
    Use explicit P terms (including initialized zeros during window fill),
    degree-to-radian coefficient conversion, and literal source arithmetic.
    Mask only the final output until P actual Filt values have been computed.
    This oracle uses whole-record arrays rather than streaming list shifts.
    """
    a = math.exp(-math.sqrt(2.0) * math.pi / (0.5 * period))
    c2 = 2.0 * a * math.cos(math.radians(math.sqrt(2.0) * 180.0 / (0.5 * period)))
    c3 = -a * a
    c1 = 1.0 - c2 - c3
    zeros = [0.0] * len(prices)
    filt = [0.0] * len(prices)
    recursive = [0.0] * len(prices)
    observations = [[math.nan] * len(prices) for _ in range(7)]
    held = 0.0
    for t in range(2, len(prices)):
        zeros[t] = prices[t] - prices[t - 2]
        filt[t] = (c1 * (zeros[t] + zeros[t - 1]) / 2.0
                   + c2 * filt[t - 1] + c3 * filt[t - 2])
        power = 0.0
        for count in range(period):
            value = filt[t - count] if t - count >= 2 else 0.0
            power = power + value * value
        rms = math.sqrt(power / period)
        if rms != 0.0:
            held = filt[t] / rms
        alpha = abs(held) * 5.0 / period
        recursive[t] = alpha * prices[t] + (1.0 - alpha) * recursive[t - 1]
        current = (zeros[t], filt[t], rms, held, alpha, recursive[t],
                   recursive[t] if t >= period + 1 else math.nan)
        for series, value in zip(observations, current):
            series[t] = value
    return observations


class DSMATests(unittest.TestCase):
    def assertSeriesClose(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for index, (value, reference) in enumerate(zip(actual, expected)):
            if math.isnan(reference):
                self.assertTrue(math.isnan(value), f'index {index}')
            else:
                self.assertTrue(math.isclose(value, reference, rel_tol=5e-13, abs_tol=5e-13),
                                f'index {index}: {value} != {reference}')

    def test_all_reference_periods_and_intermediates_match_source_listing(self):
        for case in CASES:
            with self.subTest(period=case.period):
                indicator = DSMA(case.period)
                actual = [[] for _ in range(7)]
                for close in INPUT_CLOSE:
                    value = indicator.update(close)
                    if math.isnan(value):
                        self.assertTrue(math.isnan(indicator.output))
                    else:
                        self.assertEqual(value, indicator.output)
                    for series, current in zip(actual, indicator.state):
                        series.append(current)
                for series, reference in zip(actual, source_reference(INPUT_CLOSE, case.period)):
                    self.assertSeriesClose(series, reference)
                warmup = min(case.period + 1, 252)
                self.assertTrue(all(math.isnan(x) for x in actual[-1][:warmup]))
                self.assertTrue(all(math.isfinite(x) for x in actual[-1][warmup:]))
                self.assertEqual(indicator.is_primed, case.period + 1 < 252)

    def test_first_difference_uses_zero_seed_and_ema_advances_before_public_output(self):
        indicator = DSMA(5)
        for close in (10.0, 12.0):
            self.assertTrue(math.isnan(indicator.update(close)))
            self.assertTrue(all(math.isnan(x) for x in indicator.state))
        self.assertTrue(math.isnan(indicator.update(14.0)))
        self.assertEqual(indicator.state.zeros, 4.0)
        angle = math.sqrt(2.0) * math.pi / 2.5
        a = math.exp(-angle)
        c1 = 1.0 - 2.0 * a * math.cos(angle) + a * a
        self.assertAlmostEqual(indicator.state.filtered, c1 * 4.0 / 2.0, places=13)
        self.assertAlmostEqual(indicator.state.rms, abs(indicator.state.filtered) / math.sqrt(5.0))
        self.assertAlmostEqual(indicator.state.alpha, math.sqrt(5.0))
        self.assertAlmostEqual(indicator.state.recursive_dsma, math.sqrt(5.0) * 14.0)
        for close in (15.0, 18.0, 19.0):
            self.assertTrue(math.isnan(indicator.update(close)))
            self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isfinite(indicator.update(20.0)))  # t=6=P+1.
        self.assertTrue(indicator.is_primed)

    def test_constant_and_nyquist_prices_preserve_source_zero_seed(self):
        for period in (1, 2, 5, 40):
            for prices in ([100.0] * 100, [100.0 + (t % 2) * 10.0 for t in range(100)]):
                indicator = DSMA(period)
                values = [indicator.update(x) for x in prices]
                self.assertTrue(all(math.isnan(x) for x in values[:period + 1]))
                self.assertEqual(values[period + 1:], [0.0] * (99 - period))
                self.assertEqual(indicator.state.rms, 0.0)
                self.assertEqual(indicator.state.scaled_filtered, 0.0)
                self.assertEqual(indicator.state.alpha, 0.0)

    def test_unclamped_alpha_period_one_has_literal_growth(self):
        indicator = DSMA(1)
        values = [indicator.update(x) for x in (1.0, 2.0, 4.0, 8.0, 16.0)]
        self.assertTrue(all(math.isnan(x) for x in values[:2]))
        self.assertEqual(values[2:], [20.0, -40.0, 240.0])
        self.assertEqual(indicator.state.alpha, 5.0)

    def test_alpha_bound_and_period_twenty_five_boundary(self):
        for period in (3, 20, 24, 25, 26, 40, 100):
            indicator = DSMA(period)
            # The first nonzero Filt alone attains the bound, since startup
            # divides its squared amplitude by the full source Period.
            for close in (0.0, 0.0, 1.0):
                indicator.update(close)
            self.assertAlmostEqual(indicator.state.alpha, 5.0 / math.sqrt(period), places=13)
            self.assertEqual(indicator.state.alpha > 1.0, period < 25)
            for close in INPUT_CLOSE:
                indicator.update(close)
                self.assertLessEqual(indicator.state.alpha, 5.0 / math.sqrt(period) + 1e-13)

    def test_rms_is_uncentered_population_second_moment(self):
        # For a ramp, the two-bar difference converges to nonzero constant 2.
        # Its centered standard deviation would converge to zero; RMS -> 2.
        indicator = DSMA(40)
        for t in range(400):
            indicator.update(float(t))
        self.assertAlmostEqual(indicator.state.filtered, 2.0, places=12)
        self.assertAlmostEqual(indicator.state.rms, 2.0, places=12)
        self.assertAlmostEqual(indicator.state.scaled_filtered, 1.0, places=12)
        self.assertAlmostEqual(indicator.state.alpha, 5.0 / 40.0, places=12)

    def test_zero_rms_retains_previous_scaled_value(self):
        # White-box branch setup is deliberate: after real activity, an exact
        # zero-energy window is rarely reached without underflow or a reset.
        # Isolate the Mesa guard rather than test a numerically near-zero RMS.
        indicator = DSMA(2)
        for price in (10.0, 10.0, 10.0, 10.0):
            indicator.update(price)
        indicator._scaled = -0.25
        indicator._dsma = 8.0
        self.assertEqual(indicator.update(10.0), 9.25)
        self.assertEqual(indicator.state.rms, 0.0)
        self.assertEqual(indicator.state.scaled_filtered, -0.25)
        self.assertEqual(indicator.state.alpha, 0.625)

    def test_price_scaling_and_negation_preserve_adaptive_coefficients(self):
        prices = [float((t * 7) % 23 - 10) for t in range(120)]
        baseline = DSMA(40)
        scaled = DSMA(40)
        negated = DSMA(40)
        original = [baseline.update(x) for x in prices]
        self.assertSeriesClose([scaled.update(2.0 * x) for x in prices], [2.0 * x for x in original])
        self.assertSeriesClose([negated.update(-x) for x in prices], [-x for x in original])
        self.assertAlmostEqual(scaled.state.alpha, baseline.state.alpha, places=13)
        self.assertAlmostEqual(negated.state.alpha, baseline.state.alpha, places=13)

    def test_nonfinite_and_overflow_rejection_do_not_advance_history(self):
        for prefix in (0, 1, 2, 10, 41, 100):
            indicator = DSMA()
            values = [indicator.update(x) for x in INPUT_CLOSE[:prefix]]
            for invalid in (math.nan, math.inf, -math.inf):
                with self.assertRaises(ValueError):
                    indicator.update(invalid)
            values += [indicator.update(x) for x in INPUT_CLOSE[prefix:]]
            self.assertSeriesClose(values, source_reference(INPUT_CLOSE, 40)[-1])
        indicator = DSMA(40)
        indicator.update(-1e308)
        indicator.update(0.0)
        with self.assertRaisesRegex(ValueError, 'difference'):
            indicator.update(1e308)
        self.assertTrue(math.isnan(indicator.state.zeros))
        indicator.update(-1e308)
        self.assertEqual(indicator.state.zeros, 0.0)
        indicator = DSMA(40)
        indicator.update(0.0)
        indicator.update(0.0)
        with self.assertRaisesRegex(ValueError, 'RMS'):
            indicator.update(1e200)
        indicator.update(1.0)
        self.assertEqual(indicator.state.zeros, 1.0)

    def test_reset_replay_validation_and_fractional_half_period(self):
        for invalid in (True, False, 0, -1, 40.0, 8.5, math.nan, math.inf, 10**300):
            with self.assertRaises(ValueError):
                DSMA(invalid)
        indicator = DSMA(25)
        self.assertEqual(indicator.smooth_period, 12.5)
        first = [indicator.update(x) for x in INPUT_CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertTrue(all(math.isnan(x) for x in indicator.state))
        self.assertEqual(indicator.period, 25)
        self.assertSeriesClose([indicator.update(x) for x in INPUT_CLOSE], first)
        with self.assertRaises(AttributeError):
            indicator.period = 40

    def test_embedded_input_and_all_copied_arrays(self):
        node = next(node for node in ast.walk(ast.parse(MASTER_PATH.read_text()))
                    if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == 'INPUT_CLOSE' for target in node.targets))
        self.assertEqual(len(INPUT_CLOSE), 252)
        self.assertEqual(ast.literal_eval(node.value), INPUT_CLOSE)
        original = runpy.run_path(str(DIRECTORY.parent / 'test_testdata.py'))
        for name in ('INPUT_CLOSE', 'INPUT_HIGH', 'INPUT_LOW', 'INPUT_OPEN'):
            self.assertEqual(DATA[name], original[name])

    def test_expected_arrays_match_source_after_confirmation(self):
        self.assertTrue(1 <= len(CASES) <= 64)
        names = {'EXPECTED_' + MASTER['_case_suffix'](case) for case in CASES}
        self.assertEqual(len(names), len(CASES))
        present = {name for name in DATA if name.startswith('EXPECTED_')}
        if MASTER['REFERENCE_CASES_CONFIRMED']:
            self.assertEqual(present, names)
            for case in CASES:
                self.assertSeriesClose(DATA['EXPECTED_' + MASTER['_case_suffix'](case)],
                                       source_reference(INPUT_CLOSE, case.period)[-1])
        else:
            self.assertEqual(present, set())

    def test_confirmation_guard_and_generator_in_temporary_fixtures(self):
        generator = MASTER['generate_reference_data']
        with tempfile.TemporaryDirectory() as name:
            target = Path(name)
            with patch.dict(generator.__globals__, {'REFERENCE_CASES_CONFIRMED': False}):
                with self.assertRaisesRegex(ValueError, 'confirm'):
                    generator(INPUT_CLOSE, target)
            self.assertEqual(list(target.iterdir()), [])
            for filename in FIXTURES:
                shutil.copyfile(DIRECTORY.parent / filename, target / filename)
            # Test all generator paths and repeatability in a temporary copy,
            # without rewriting the confirmed production reference fixtures.
            with patch.dict(generator.__globals__, {'REFERENCE_CASES_CONFIRMED': True}):
                with contextlib.redirect_stdout(io.StringIO()):
                    generator(INPUT_CLOSE, target)
                    before = {filename: (target / filename).read_bytes() for filename in FIXTURES}
                    generator(INPUT_CLOSE, target)
                self.assertEqual(before, {filename: (target / filename).read_bytes() for filename in FIXTURES})
            written = runpy.run_path(str(target / 'test_testdata.py'))
            for case in CASES:
                self.assertSeriesClose(written['EXPECTED_' + MASTER['_case_suffix'](case)],
                                       source_reference(INPUT_CLOSE, case.period)[-1])


if __name__ == '__main__':
    unittest.main()
