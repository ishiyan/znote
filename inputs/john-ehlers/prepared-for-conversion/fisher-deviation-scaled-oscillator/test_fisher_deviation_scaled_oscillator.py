"""Independent source-index and behavioral verification; standard library only."""

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
MASTER_PATH = DIRECTORY / 'fisher-deviation-scaled-oscillator.py'
MASTER = runpy.run_path(str(MASTER_PATH))
Indicator = MASTER['FisherDeviationScaledOscillator']
FISHER = True
CASES = MASTER['REFERENCE_CASES']
DATA = runpy.run_path(str(DIRECTORY / 'test_testdata.py'))
INPUT_CLOSE = DATA['INPUT_CLOSE']
FIXTURES = ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')


def article_reference(prices, period):
    """Independent whole-record transcription, with absolute-index lags.

    Source oscillator/filter variables before t=2 are zero. The whole-window
    RMS loop includes every P term even before actual observations fill it.
    Degree conversion is independently expressed. Persistent normalized and
    Fisher values update internally during warmup; only public output is masked.
    """
    a = math.exp(-math.sqrt(2.0) * math.pi / (period / 2.0))
    c2 = 2.0 * a * math.cos(math.radians(math.sqrt(2.0) * 180.0 / (period / 2.0)))
    c3 = -a * a
    c1 = 1.0 - c2 - c3
    z = [0.0] * len(prices)
    f = [0.0] * len(prices)
    width = 7 if FISHER else 5
    observations = [[math.nan] * len(prices) for _ in range(width)]
    if FISHER:
        observations[5] = [False] * len(prices)
    scaled = fisher = 0.0
    for t in range(2, len(prices)):
        z[t] = prices[t] - prices[t - 2]
        f[t] = c1 * (z[t] + z[t - 1]) / 2.0 + c2 * f[t - 1] + c3 * f[t - 2]
        power = 0.0
        for k in range(period):
            sample = f[t - k] if t - k >= 2 else 0.0
            power = power + sample * sample
        rms = math.sqrt(power / period)
        if rms != 0.0:
            scaled = f[t] / rms
        if FISHER:
            updated = abs(scaled) < 2.0
            if updated:
                fisher = 0.5 * math.log((1.0 + scaled / 2.0) / (1.0 - scaled / 2.0))
            output = fisher if t >= period + 1 else math.nan
            current = (z[t], f[t], rms, scaled, fisher, updated, output)
        else:
            output = scaled if t >= period + 1 else math.nan
            current = (z[t], f[t], rms, scaled, output)
        for series, value in zip(observations, current):
            series[t] = value
    return observations


class FisherDSOTests(unittest.TestCase):
    def assertSeriesClose(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for t, (value, reference) in enumerate(zip(actual, expected)):
            if isinstance(reference, bool):
                self.assertIs(value, reference, f'index {t}')
            elif math.isnan(reference):
                self.assertTrue(math.isnan(value), f'index {t}')
            else:
                self.assertTrue(math.isclose(value, reference, rel_tol=5e-13, abs_tol=5e-13),
                                f'index {t}: {value} != {reference}')

    def test_all_cases_and_intermediates_match_independent_article(self):
        for case in CASES:
            with self.subTest(period=case.period):
                indicator = Indicator(case.period)
                actual = [[] for _ in range(7 if FISHER else 5)]
                for price in INPUT_CLOSE:
                    output = indicator.update(price)
                    if math.isnan(output):
                        self.assertTrue(math.isnan(indicator.output))
                    else:
                        self.assertEqual(output, indicator.output)
                    for series, value in zip(actual, indicator.state):
                        series.append(value)
                for series, reference in zip(actual, article_reference(INPUT_CLOSE, case.period)):
                    self.assertSeriesClose(series, reference)
                prefix = min(case.period + 1, 252)
                self.assertTrue(all(math.isnan(x) for x in actual[-1][:prefix]))
                self.assertTrue(all(math.isfinite(x) for x in actual[-1][prefix:]))
                self.assertEqual(indicator.is_primed, case.period + 1 < 252)
                self.assertEqual(indicator.warmup_bars, case.period + 1)

    def test_exact_seed_first_filter_and_complete_window_availability(self):
        indicator = Indicator(5)
        for price in (10.0, 12.0):
            self.assertTrue(math.isnan(indicator.update(price)))
            self.assertTrue(math.isnan(indicator.state.zeros))
        self.assertTrue(math.isnan(indicator.update(14.0)))
        self.assertEqual(indicator.state.zeros, 4.0)
        angle = math.sqrt(2.0) * math.pi / 2.5
        a = math.exp(-angle)
        c1 = 1.0 - 2.0 * a * math.cos(angle) + a * a
        self.assertAlmostEqual(indicator.state.filtered, c1 * 4.0 / 2.0, places=13)
        self.assertAlmostEqual(indicator.state.rms, abs(indicator.state.filtered) / math.sqrt(5.0))
        self.assertAlmostEqual(indicator.state.scaled_filtered, math.sqrt(5.0))
        if FISHER:
            self.assertFalse(indicator.state.fisher_updated)
            self.assertEqual(indicator.state.fisher_filtered, 0.0)
        for price in (15.0, 18.0, 19.0):
            self.assertTrue(math.isnan(indicator.update(price)))
            self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isfinite(indicator.update(20.0)))  # t=6=P+1.
        self.assertTrue(indicator.is_primed)

    def test_constant_and_nyquist_inputs_are_zero_after_warmup(self):
        for period in (1, 2, 4, 5, 40):
            for prices in ([100.0] * 100, [100.0 + (t % 2) * 10.0 for t in range(100)]):
                indicator = Indicator(period)
                values = [indicator.update(x) for x in prices]
                self.assertTrue(all(math.isnan(x) for x in values[:period + 1]))
                self.assertEqual(values[period + 1:], [0.0] * (99 - period))
                self.assertEqual(indicator.state.rms, 0.0)
                self.assertEqual(indicator.state.scaled_filtered, 0.0)

    def test_ramp_uses_rms_not_centered_standard_deviation(self):
        indicator = Indicator(40)
        for t in range(400):
            indicator.update(float(t))
        self.assertAlmostEqual(indicator.state.filtered, 2.0, places=12)
        self.assertAlmostEqual(indicator.state.rms, 2.0, places=12)
        self.assertAlmostEqual(indicator.state.scaled_filtered, 1.0, places=12)
        expected = 0.5 * math.log(3.0) if FISHER else 1.0
        self.assertAlmostEqual(indicator.output, expected, places=12)

    def test_scaled_bound_and_minimum_period(self):
        for period in (1, 2, 3, 4, 5, 9, 40):
            indicator = Indicator(period)
            for price in (0.0, 0.0, 1.0):
                indicator.update(price)
            self.assertAlmostEqual(indicator.state.scaled_filtered, math.sqrt(period), places=13)
            for price in INPUT_CLOSE:
                indicator.update(price)
                self.assertLessEqual(abs(indicator.state.scaled_filtered), math.sqrt(period) + 1e-13)
        indicator = Indicator(1)
        for price in (0.0, 0.0, 1.0):
            indicator.update(price)
        self.assertEqual(indicator.output, 0.5 * math.log(3.0) if FISHER else 1.0)

    def test_zero_rms_retains_scaled_state(self):
        # Isolate exact-zero retention, which a real active IIR rarely reaches
        # except through underflow. Controlled internal state is intentional.
        indicator = Indicator(2)
        for price in (10.0, 10.0, 10.0, 10.0):
            indicator.update(price)
        indicator._scaled = -0.25
        output = indicator.update(10.0)
        self.assertEqual(indicator.state.rms, 0.0)
        self.assertEqual(indicator.state.scaled_filtered, -0.25)
        expected = 0.5 * math.log((1.0 - 0.125) / (1.0 + 0.125)) if FISHER else -0.25
        self.assertEqual(output, expected)

    def test_offset_scaling_and_negation_invariance(self):
        prices = [float((t * 7) % 23 - 10) for t in range(120)]
        original = Indicator(40)
        baseline = [original.update(x) for x in prices]
        for scale, offset in ((1.0, 1000.0), (2.0, 0.0), (-1.0, 0.0)):
            indicator = Indicator(40)
            expected = [-x for x in baseline] if scale < 0.0 else baseline
            self.assertSeriesClose([indicator.update(scale * x + offset) for x in prices], expected)

    def test_nonfinite_and_overflow_inputs_do_not_advance_state(self):
        for prefix in (0, 1, 2, 10, 41, 100):
            indicator = Indicator()
            values = [indicator.update(x) for x in INPUT_CLOSE[:prefix]]
            for invalid in (math.nan, math.inf, -math.inf):
                with self.assertRaises(ValueError):
                    indicator.update(invalid)
            values += [indicator.update(x) for x in INPUT_CLOSE[prefix:]]
            self.assertSeriesClose(values, article_reference(INPUT_CLOSE, 40)[-1])
        indicator = Indicator(40)
        indicator.update(-1e308)
        indicator.update(0.0)
        with self.assertRaisesRegex(ValueError, 'difference'):
            indicator.update(1e308)
        self.assertTrue(math.isnan(indicator.state.zeros))
        indicator.update(-1e308)
        self.assertEqual(indicator.state.zeros, 0.0)
        indicator = Indicator(40)
        indicator.update(0.0)
        indicator.update(0.0)
        with self.assertRaisesRegex(ValueError, 'RMS'):
            indicator.update(1e200)
        indicator.update(1.0)
        self.assertEqual(indicator.state.zeros, 1.0)

    def test_reset_replay_parameters_and_fractional_half_period(self):
        for invalid in (True, False, 0, -1, 40.0, 8.5, math.nan, math.inf, 10**300):
            with self.assertRaises(ValueError):
                Indicator(invalid)
        indicator = Indicator(41)
        self.assertEqual(indicator.smooth_period, 20.5)
        first = [indicator.update(x) for x in INPUT_CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isnan(indicator.output))
        self.assertEqual(indicator.period, 41)
        self.assertSeriesClose([indicator.update(x) for x in INPUT_CLOSE], first)
        with self.assertRaises(AttributeError):
            indicator.period = 40

    def test_embedded_input_and_all_copied_arrays(self):
        node = next(node for node in ast.walk(ast.parse(MASTER_PATH.read_text()))
                    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                    and target.id == 'INPUT_CLOSE' for target in node.targets))
        self.assertEqual(len(INPUT_CLOSE), 252)
        self.assertEqual(ast.literal_eval(node.value), INPUT_CLOSE)
        original = runpy.run_path(str(DIRECTORY.parent / 'test_testdata.py'))
        for name in ('INPUT_CLOSE', 'INPUT_HIGH', 'INPUT_LOW', 'INPUT_OPEN'):
            self.assertEqual(DATA[name], original[name])

    def test_expected_arrays_match_source_when_confirmed(self):
        self.assertTrue(1 <= len(CASES) <= 64)
        names = {'EXPECTED_' + MASTER['_case_suffix'](case) for case in CASES}
        self.assertEqual(len(names), len(CASES))
        present = {name for name in DATA if name.startswith('EXPECTED_')}
        if MASTER['REFERENCE_CASES_CONFIRMED']:
            self.assertEqual(present, names)
            for case in CASES:
                self.assertSeriesClose(DATA['EXPECTED_' + MASTER['_case_suffix'](case)],
                                       article_reference(INPUT_CLOSE, case.period)[-1])
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
            # Temporary generation validates output formats and repeatability
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
                                       article_reference(INPUT_CLOSE, case.period)[-1])

    def test_strict_fisher_boundary_initial_hold_and_reentry(self):
        indicator = Indicator(4)
        for price in (0.0, 0.0):
            indicator.update(price)
        # One current Filt attains scaled=2; initial Fisher must remain zero.
        indicator.update(2.0 / indicator._c1)
        self.assertEqual(indicator.state.scaled_filtered, 2.0)
        self.assertFalse(indicator.state.fisher_updated)
        self.assertEqual(indicator.state.fisher_filtered, 0.0)
        # Seed a complete zero-energy window to control scaled amplitudes exactly.
        indicator = Indicator(4)
        for _ in range(6):
            indicator.update(10.0)
        indicator._fisher = 0.75
        for value in (2.0, -2.0, 3.0, -3.0, math.nextafter(2.0, math.inf)):
            indicator._scaled = value
            self.assertEqual(indicator.update(10.0), 0.75)
            self.assertFalse(indicator.state.fisher_updated)
        for value in (1.0, -1.0, math.nextafter(2.0, 0.0), math.nextafter(-2.0, 0.0)):
            indicator._scaled = value
            expected = 0.5 * math.log((1.0 + value / 2.0) / (1.0 - value / 2.0))
            self.assertEqual(indicator.update(10.0), expected)
            self.assertTrue(indicator.state.fisher_updated)

    def test_actual_default_holds_and_prepublic_fisher_state(self):
        indicator = Indicator(40)
        previous = 0.0
        held = 0
        for price in INPUT_CLOSE:
            value = indicator.update(price)
            if indicator.is_primed and not indicator.state.fisher_updated:
                self.assertEqual(value, previous)
                self.assertNotEqual(previous, 0.0)
                held += 1
            if math.isfinite(indicator.state.fisher_filtered):
                previous = indicator.state.fisher_filtered
        self.assertEqual(held, 7)
        # P80's first public bar is outside the gate; it must return the earlier
        # internal transformed value, not NaN, zero, or a fresh transform.
        indicator = Indicator(80)
        for price in INPUT_CLOSE[:81]:
            self.assertTrue(math.isnan(indicator.update(price)))
        previous = indicator.state.fisher_filtered
        self.assertNotEqual(previous, 0.0)
        self.assertEqual(indicator.update(INPUT_CLOSE[81]), previous)
        self.assertFalse(indicator.state.fisher_updated)


if __name__ == '__main__':
    unittest.main()
