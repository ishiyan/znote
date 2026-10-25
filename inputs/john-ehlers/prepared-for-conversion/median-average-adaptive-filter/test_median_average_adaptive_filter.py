"""Independent chronological source oracle and numerical edge-case tests.

The oracle uses unbounded chronological history and explicit source indexing,
not the master's buffers or its search routine. It remains self-contained
when this preparation is transferred without the original article files.
"""

import importlib.util
import math
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('maaf_master', HERE/(HERE.name+'.py'))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
CLOSES = MASTER._load_arrays(HERE/'test_testdata.py')['INPUT_CLOSE']


def source_batch(prices, threshold):
    """Chronological transcription of article arithmetic/eSignal startup.

    EMA trial history is one shared previous-bar value. The guarded loop can
    evaluate length 1; the subsequent output length still has a floor of 3.
    Return the public output plus hidden trial, selected/evaluated lengths.
    """
    smooth = [0.0]*len(prices)
    trial_history = [0.0]*len(prices)
    filter_history = [0.0]*len(prices)
    result = []
    for t in range(len(prices)):
        if t >= 3:
            smooth[t] = (prices[t]+2*prices[t-1]+2*prices[t-2]+prices[t-3])/6
        if t < 38:
            result.append((math.nan, 0.0, None, None))
            continue
        previous_trial = trial_history[t-1]
        length, difference = 39, .2
        evaluated = None
        trial = previous_trial
        while difference > threshold:
            ordered = sorted(smooth[t-length+1:t+1])
            middle = ordered[(length-1)//2]
            trial = 2/(length+1)*smooth[t]+(1-2/(length+1))*previous_trial
            if middle != 0:
                difference = abs(middle-trial)/middle
            evaluated = length
            length -= 2
            if length <= 0:
                break
        length = max(3, length)
        filter_history[t] = 2/(length+1)*smooth[t]+(1-2/(length+1))*filter_history[t-1]
        trial_history[t] = trial
        result.append((filter_history[t], trial, length, evaluated))
    return result


class NumericalTests(unittest.TestCase):
    def number(self, actual, expected):
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual))
        else:
            self.assertTrue(math.isclose(actual, expected, rel_tol=3e-12, abs_tol=3e-12),
                            f'{actual!r} != {expected!r}')

    def test_all_proposed_cases_against_chronological_source_oracle(self):
        self.assertEqual(len(MASTER.REFERENCE_CASES), 14)
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(threshold=case['threshold']):
                stream = MASTER.MedianAverageAdaptiveFilter(case['threshold'])
                oracle = source_batch(CLOSES, case['threshold'])
                for t, (price, expected) in enumerate(zip(CLOSES, oracle), 1):
                    output, trial, selected, evaluated = expected
                    self.number(stream.update(price), output)
                    self.number(stream.state.candidate_ema, trial)
                    self.assertEqual(stream.selected_length, selected)
                    self.assertEqual(stream.evaluated_length, evaluated)
                    self.assertEqual(stream.samples_seen, t)
                    self.assertEqual(stream.is_primed, t >= 39)

    def test_exact_tip_startup_and_four_price_smoother(self):
        stream = MASTER.MedianAverageAdaptiveFilter()
        for t, price in enumerate(CLOSES[:38]):
            self.assertTrue(math.isnan(stream.update(price)))
            expected = 0.0 if t < 3 else (
                CLOSES[t]+2*CLOSES[t-1]+2*CLOSES[t-2]+CLOSES[t-3])/6
            self.assertEqual(stream.state.smoothed_history[0], expected)
            self.assertEqual(stream.state.candidate_ema, 0.0)
            self.assertEqual(stream.state.filtered, 0.0)
        output = stream.update(CLOSES[38])
        self.assertTrue(stream.is_primed)
        self.assertEqual(stream.warmup_bars, 38)
        self.assertEqual(stream.state.smoothed_history[-3:], (0.0, 0.0, 0.0))
        self.assertEqual(output, stream.state.smoothed_history[0]/2)
        self.assertEqual(stream.selected_length, 3)

    def test_successful_search_decrements_length_even_on_equality(self):
        stream = MASTER.MedianAverageAdaptiveFilter(0.0)
        for _ in range(39):
            first = stream.update(100.0)
        self.assertEqual(first, 50.0)
        self.assertEqual(stream.state.candidate_ema, 100.0)
        self.assertEqual(stream.evaluated_length, 1)
        self.assertEqual(stream.selected_length, 3)
        next_output = stream.update(100.0)
        self.assertEqual(stream.discrepancy, 0.0)
        self.assertEqual(stream.evaluated_length, 39)
        self.assertEqual(stream.selected_length, 37)
        self.assertEqual(stream.trial_count, 1)
        self.number(next_output, 2/38*100+(1-2/38)*50)

    def test_each_trial_uses_fixed_previous_bar_candidate(self):
        stream = MASTER.MedianAverageAdaptiveFilter()
        stopped_before_one = 0
        for price in CLOSES:
            previous = stream.state.candidate_ema
            stream.update(price)
            if stream.is_primed:
                trial_alpha = 2/(stream.evaluated_length+1)
                self.assertEqual(stream.state.candidate_ema,
                                 trial_alpha*stream.state.smoothed_history[0]
                                 +(1-trial_alpha)*previous)
                if 1 < stream.evaluated_length < 39:
                    stopped_before_one += 1
        self.assertGreater(stopped_before_one, 0)

    def test_zero_medians_terminate_with_guard_for_zero_and_default_thresholds(self):
        for threshold in (0.0, .002):
            stream = MASTER.MedianAverageAdaptiveFilter(threshold)
            for _ in range(45):
                output = stream.update(0.0)
                if stream.is_primed:
                    self.assertEqual(output, 0.0)
                    self.assertEqual(stream.trial_count, 20)
                    self.assertEqual(stream.evaluated_length, 1)
                    self.assertEqual(stream.selected_length, 3)
                    self.assertEqual(stream.discrepancy, .2)

    def test_signed_median_denominator_is_preserved(self):
        stream = MASTER.MedianAverageAdaptiveFilter()
        for _ in range(39):
            output = stream.update(-100.0)
        self.assertEqual(stream.evaluated_length, 39)
        self.assertEqual(stream.selected_length, 37)
        self.assertEqual(stream.discrepancy, -.95)
        self.number(output, -100/19)

    def test_sentinel_equality_and_larger_threshold_skip_search(self):
        streams = [MASTER.MedianAverageAdaptiveFilter(t) for t in (.2, .25)]
        conventional = 0.0
        for t, price in enumerate(CLOSES):
            outputs = [stream.update(price) for stream in streams]
            if t >= 38:
                smooth = (CLOSES[t]+2*CLOSES[t-1]+2*CLOSES[t-2]+CLOSES[t-3])/6
                conventional = .05*smooth+.95*conventional
                for stream, output in zip(streams, outputs):
                    self.number(output, conventional)
                    self.assertEqual(stream.selected_length, 39)
                    self.assertIsNone(stream.evaluated_length)
                    self.assertEqual(stream.trial_count, 0)
                    self.assertEqual(stream.state.candidate_ema, 0.0)

    def test_constant_input_converges_to_unity_dc_gain_for_all_cases(self):
        for case in MASTER.REFERENCE_CASES:
            stream = MASTER.MedianAverageAdaptiveFilter(case['threshold'])
            for _ in range(2000):
                output = stream.update(100.0)
            self.number(output, 100.0)

    def test_missing_invalid_inputs_and_overflow_are_atomic(self):
        stream = MASTER.MedianAverageAdaptiveFilter()
        control = MASTER.MedianAverageAdaptiveFilter()
        for price in CLOSES[:80]:
            stream.update(price)
            control.update(price)
        before, previous_output = stream.state, stream.output
        self.assertTrue(math.isnan(stream.update(math.nan)))
        self.assertEqual(stream.state, before)
        self.assertEqual(stream.output, previous_output)
        for invalid in (True, None, '1', math.inf, -math.inf, 10**400):
            with self.assertRaises(ValueError):
                stream.update(invalid)
            self.assertEqual(stream.state, before)
            self.assertEqual(stream.output, previous_output)
        self.assertEqual(stream.update(CLOSES[80]), control.update(CLOSES[80]))
        overflowing = MASTER.MedianAverageAdaptiveFilter()
        for _ in range(3):
            overflowing.update(1e308)
        before = overflowing.state
        with self.assertRaises(ValueError):
            overflowing.update(1e308)
        self.assertEqual(overflowing.state, before)

    def test_reset_replays_state_and_histories_are_bounded(self):
        stream = MASTER.MedianAverageAdaptiveFilter()
        expected = [stream.update(price) for price in CLOSES]
        snapshot = stream.state
        self.assertEqual(len(snapshot.previous_prices), 4)
        self.assertEqual(len(snapshot.smoothed_history), 39)
        stream.update(10.0)
        self.assertEqual(snapshot.samples_seen, 252)
        self.assertEqual(snapshot.previous_prices[0], CLOSES[-1])
        stream.reset()
        for actual, wanted in zip([stream.update(price) for price in CLOSES], expected):
            self.number(actual, wanted)

    def test_parameter_domains(self):
        for invalid in (-.01, math.inf, math.nan, True, '0.002', None, 10**400):
            with self.assertRaises(ValueError):
                MASTER.MedianAverageAdaptiveFilter(invalid)
        self.assertEqual(MASTER.MedianAverageAdaptiveFilter().threshold, .002)
        self.assertEqual(MASTER.MedianAverageAdaptiveFilter(0).threshold, 0.0)
        self.assertEqual(MASTER.MedianAverageAdaptiveFilter(1.0).threshold, 1.0)


if __name__ == '__main__':
    unittest.main()
