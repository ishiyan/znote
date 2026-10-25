"""Independent article transcription and analytic filter-identity tests.

The batch oracle evaluates every printed assignment chronologically, including
the discarded startup recurrence. It uses its own full histories and literal
coefficients; it does not call the master's update or coefficient selector.
"""

import importlib.util
import math
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('ifcc_master', HERE/(HERE.name+'.py'))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
CLOSES = MASTER._load_arrays(HERE/'test_testdata.py')['INPUT_CLOSE']


def article_batch(prices, alpha):
    """Literal article/MESA/TradeStation calculation with zero prehistory."""
    price = [0.0, 0.0, 0.0]+list(prices)
    smooth = [0.0]*len(price)
    cycle = [0.0]*len(price)
    result = []
    for t in range(3, len(price)):
        bar = t-2
        smooth[t] = (price[t]+2*price[t-1]+2*price[t-2]+price[t-3])/6
        cycle[t] = ((1-.5*alpha)*(1-.5*alpha)
                    *(smooth[t]-2*smooth[t-1]+smooth[t-2])
                    +2*(1-alpha)*cycle[t-1]-(1-alpha)*(1-alpha)*cycle[t-2])
        if bar < 7:
            cycle[t] = (price[t]-2*price[t-1]+price[t-2])/4
        exponential = math.exp(2*cycle[t])
        transformed = (exponential-1)/(exponential+1)
        result.append((smooth[t], cycle[t], transformed))
    return result


class NumericalTests(unittest.TestCase):
    def number(self, actual, expected):
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual))
        else:
            self.assertTrue(math.isclose(actual, expected, rel_tol=3e-12, abs_tol=3e-12),
                            f'{actual!r} != {expected!r}')

    def test_all_12_cases_against_literal_article_transcription(self):
        self.assertEqual(len(MASTER.REFERENCE_CASES), 12)
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(alpha=case['alpha']):
                stream = MASTER.InverseFisherCyberCycle(case['alpha'])
                reference = article_batch(CLOSES, case['alpha'])
                for bar, (price, (smooth, cycle, transformed)) in enumerate(zip(CLOSES, reference), 1):
                    self.assertEqual(stream.update(price), transformed)
                    self.assertEqual(stream.state.smooth, smooth)
                    self.assertEqual(stream.state.cycle, cycle)
                    self.assertEqual(stream.samples_seen, bar)

    def test_unconditional_source_plot_has_no_warmup_mask(self):
        stream = MASTER.InverseFisherCyberCycle()
        self.assertFalse(stream.is_primed)
        self.assertTrue(math.isnan(stream.output))
        self.assertEqual(stream.warmup_bars, 0)
        values = [stream.update(price) for price in CLOSES]
        self.assertTrue(all(math.isfinite(value) for value in values))
        self.assertEqual(values[0], 1.0)
        self.assertEqual(values[1], -1.0)
        self.assertEqual(stream.is_primed, True)

    def test_all_first_six_seed_outputs_are_independent_of_alpha(self):
        streams = [MASTER.InverseFisherCyberCycle(alpha) for alpha in (.001, .07, 1.0)]
        prices = [0.0, 0.0]+CLOSES[:6]
        for index, price in enumerate(CLOSES[:6]):
            expected_cycle = (price-2*prices[index+1]+prices[index])/4
            outputs = [stream.update(price) for stream in streams]
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(outputs[1], outputs[2])
            for stream in streams:
                self.assertEqual(stream.state.cycle, expected_cycle)
                self.assertFalse(stream.uses_recursive_cycle)
        for stream in streams:
            stream.update(CLOSES[6])
            self.assertTrue(stream.uses_recursive_cycle)
        self.assertNotEqual(streams[0].state.cycle, streams[-1].state.cycle)

    def test_smoother_and_seed_histories_are_available_for_bar_seven(self):
        stream = MASTER.InverseFisherCyberCycle()
        for price in CLOSES[:6]:
            stream.update(price)
        before = stream.state
        self.assertEqual(before.smooth, (CLOSES[5]+2*CLOSES[4]+2*CLOSES[3]+CLOSES[2])/6)
        self.assertEqual(before.previous_smooth, (CLOSES[4]+2*CLOSES[3]+2*CLOSES[2]+CLOSES[1])/6)
        self.assertEqual(before.cycle, (CLOSES[5]-2*CLOSES[4]+CLOSES[3])/4)
        self.assertEqual(before.previous_cycle, (CLOSES[4]-2*CLOSES[3]+CLOSES[2])/4)
        smooth7 = (CLOSES[6]+2*CLOSES[5]+2*CLOSES[4]+CLOSES[3])/6
        alpha = .07
        expected = ((1-.5*alpha)*(1-.5*alpha)
                    *(smooth7-2*before.smooth+before.previous_smooth)
                    +2*(1-alpha)*before.cycle-(1-alpha)*(1-alpha)*before.previous_cycle)
        stream.update(CLOSES[6])
        self.assertEqual(stream.state.cycle, expected)

    def test_linear_cycle_equals_two_cascaded_one_pole_highpass_stages(self):
        prices = [0.0]*6+[5*math.sin(2*math.pi*t/20) for t in range(200)]
        padded = [0.0]*3+prices
        for alpha in (.07, .5, 1.0):
            stream = MASTER.InverseFisherCyberCycle(alpha)
            gain, pole = 1-alpha/2, 1-alpha
            previous_smooth = stage1 = stage2 = 0.0
            for i, price in enumerate(prices, 3):
                smooth = (padded[i]+2*padded[i-1]+2*padded[i-2]+padded[i-3])/6
                current_stage1 = gain*(smooth-previous_smooth)+pole*stage1
                current_stage2 = gain*(current_stage1-stage1)+pole*stage2
                stream.update(price)
                self.number(stream.state.cycle, current_stage2)
                previous_smooth, stage1, stage2 = smooth, current_stage1, current_stage2

    def test_alpha_one_has_the_analytic_six_tap_impulse_response(self):
        stream = MASTER.InverseFisherCyberCycle(1.0)
        for _ in range(6):
            stream.update(0.0)
        expected = [1/24, 0.0, -1/24, -1/24, 0.0, 1/24, 0.0]
        for price, cycle in zip([1.0]+[0.0]*6, expected):
            stream.update(price)
            self.number(stream.state.cycle, cycle)
        self.assertEqual(stream.coefficients.feedback1, 0.0)
        self.assertEqual(stream.coefficients.feedback2, 0.0)

    def test_inverse_fisher_matches_tanh_and_half_level_preimage(self):
        for cycle in (-350, -5, -2, -.5, -.1, 0.0, .1, .5, 2, 5, 350):
            value = MASTER.inverse_fisher(cycle)
            self.assertTrue(-1.0 <= value <= 1.0)
            self.assertAlmostEqual(value, math.tanh(cycle), delta=3e-15)
        half_level = .5*math.log(3)
        self.assertAlmostEqual(MASTER.inverse_fisher(half_level), .5, places=15)
        self.assertAlmostEqual(MASTER.inverse_fisher(-half_level), -.5, places=15)

    def test_safe_transform_saturation_and_literal_near_zero_rounding(self):
        for cycle in (350.01, 1e308):
            self.assertEqual(MASTER.inverse_fisher(cycle), 1.0)
            self.assertEqual(MASTER.inverse_fisher(-cycle), -1.0)
        self.assertEqual(MASTER.inverse_fisher(1e-20), 0.0)
        for invalid in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                MASTER.inverse_fisher(invalid)

    def test_cycle_is_linear_but_transformed_output_depends_on_price_scale(self):
        normal = MASTER.InverseFisherCyberCycle()
        scaled = MASTER.InverseFisherCyberCycle()
        output_differences = 0
        for price in CLOSES:
            left, right = normal.update(price), scaled.update(.1*price)
            self.number(scaled.state.cycle, .1*normal.state.cycle)
            if abs(left-right) > .01:
                output_differences += 1
        self.assertGreater(output_differences, 0)

    def test_constant_and_linear_trend_are_rejected_after_source_startup(self):
        for alpha in (.01, .07, 1.0):
            constant = MASTER.InverseFisherCyberCycle(alpha)
            for _ in range(100):
                output = constant.update(100.0)
            self.assertEqual(constant.state.cycle, 0.0)
            self.assertEqual(output, 0.0)
            trend = MASTER.InverseFisherCyberCycle(alpha)
            for t in range(100):
                output = trend.update(float(t))
            self.number(trend.state.cycle, 0.0)
            self.number(output, 0.0)

    def test_missing_invalid_inputs_and_overflow_are_atomic(self):
        stream = MASTER.InverseFisherCyberCycle()
        control = MASTER.InverseFisherCyberCycle()
        for price in CLOSES[:80]:
            stream.update(price)
            control.update(price)
        before, last = stream.state, stream.output
        self.assertTrue(math.isnan(stream.update(math.nan)))
        self.assertEqual(stream.state, before)
        self.assertEqual(stream.output, last)
        for invalid in (True, None, '1', math.inf, -math.inf, 10**400):
            with self.assertRaises(ValueError):
                stream.update(invalid)
            self.assertEqual(stream.state, before)
            self.assertEqual(stream.output, last)
        self.assertEqual(stream.update(CLOSES[80]), control.update(CLOSES[80]))
        large = MASTER.InverseFisherCyberCycle()
        large.update(1e308)
        before = large.state
        with self.assertRaises(ValueError):
            large.update(1e308)
        self.assertEqual(large.state, before)

    def test_reset_replay_and_owned_bounded_history_snapshot(self):
        stream = MASTER.InverseFisherCyberCycle()
        expected = [stream.update(price) for price in CLOSES]
        snapshot = stream.state
        self.assertEqual(len(snapshot.previous_prices), 3)
        stream.update(10.0)
        self.assertEqual(snapshot.samples_seen, 252)
        self.assertEqual(snapshot.previous_prices[0], CLOSES[-1])
        stream.reset()
        self.assertFalse(stream.is_primed)
        for actual, wanted in zip([stream.update(price) for price in CLOSES], expected):
            self.assertEqual(actual, wanted)

    def test_parameter_domains_and_representable_poles(self):
        for invalid in (0.0, -.01, 1.01, math.inf, math.nan, True, '0.07', None, 10**400, 1e-300):
            with self.assertRaises(ValueError):
                MASTER.InverseFisherCyberCycle(invalid)
        self.assertEqual(MASTER.InverseFisherCyberCycle().alpha, .07)
        self.assertEqual(MASTER.InverseFisherCyberCycle(1).alpha, 1.0)


if __name__ == '__main__':
    unittest.main()
