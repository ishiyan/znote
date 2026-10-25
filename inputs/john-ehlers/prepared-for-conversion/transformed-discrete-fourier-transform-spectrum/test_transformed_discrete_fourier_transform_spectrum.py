"""Independent article/MESA transcription and meaningful streaming tests.

The oracle uses full chronological histories and one-based source arrays,
not the master's numerical helpers or precomputed trig tables. Standard
library only. Run python3 -m unittest discover -s THIS_FOLDER -p
test_transformed_discrete_fourier_transform_spectrum.py -v.
"""

import importlib.util
import math
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('transformed_dft_master',
                                             HERE/(HERE.name+'.py'))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_arrays(HERE/'test_testdata.py')['INPUT_CLOSE']


def article_batch(prices, p):
    """Direct chronological translation of the 2007 article at full precision.

    Price[1] is represented by prices[t-1]; CleanedData[n] by cleaned[t-n].
    DB is a retained source array, while Fourier parts/powers reset each bar.
    Zero absent history is explicit. No master helper is called here.
    """
    price = [0.0] + list(prices)
    hp = [0.0] * len(price)
    cleaned = [0.0] * len(price)
    db = [0.0] * (p.max_period+1)
    dominant = 0.0
    results = []
    for t in range(1, len(price)):
        if t <= 5:
            hp[t] = cleaned[t] = price[t]
        else:
            alpha = ((1-math.sin(2*math.pi/p.highpass_period))
                     /math.cos(2*math.pi/p.highpass_period))
            hp[t] = .5*(1+alpha)*(price[t]-price[t-1])+alpha*hp[t-1]
            cleaned[t] = (hp[t]+2*hp[t-1]+3*hp[t-2]+3*hp[t-3]+2*hp[t-4]+hp[t-5])/12
        cosine = [0.0] * (p.max_period+1)
        sine = [0.0] * (p.max_period+1)
        power = [0.0] * (p.max_period+1)
        for period in range(p.min_period, p.max_period+1):
            for n in range(p.window_length):
                data = cleaned[t-n] if t-n >= 0 else 0.0
                cosine[period] += data*math.cos(2*math.pi*n/period)
                sine[period] += data*math.sin(2*math.pi*n/period)
            power[period] = cosine[period]*cosine[period]+sine[period]*sine[period]
        maximum = power[p.min_period]
        for period in range(p.min_period, p.max_period+1):
            if power[period] > maximum:
                maximum = power[period]
        for period in range(p.min_period, p.max_period+1):
            if maximum > 0 and power[period] > 0:
                db[period] = -10*math.log(.01/(1-.99*power[period]/maximum))/math.log(10)
            if db[period] > 20:
                db[period] = 20.0
        numerator = denominator = 0.0
        for period in range(p.min_period, p.max_period+1):
            if db[period] < 3:
                numerator += period*(3-db[period])
                denominator += 3-db[period]
        if denominator != 0:
            dominant = numerator/denominator
        results.append((hp[t], cleaned[t], maximum, dominant,
                        cosine[p.min_period:], sine[p.min_period:],
                        power[p.min_period:], db[p.min_period:].copy()))
    return results


class NumericalTests(unittest.TestCase):
    def number(self, actual, expected):
        self.assertTrue(math.isclose(actual, expected, rel_tol=3e-11, abs_tol=3e-11),
                        f'{actual!r} != {expected!r}')

    def test_all_cases_match_independent_article_and_mesa_equations(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case):
                stream = MASTER.MASTER_CLASS(**{k:v for k,v in case.items() if k != 'what_it_tests'})
                expected = article_batch(INPUTS, stream.parameters)
                for t, (price, reference) in enumerate(zip(INPUTS, expected), 1):
                    output = stream.update(price, t)
                    state = stream.state
                    for actual, wanted in zip(state[:4], reference[:4]):
                        self.number(actual, wanted)
                    for actuals, wanteds in zip(state[4:], reference[4:]):
                        for actual, wanted in zip(actuals, wanteds):
                            self.number(actual, wanted)
                    self.assertEqual(output.heatmap.is_empty(), t <= stream.warmup_bars)
                    self.assertEqual(output.heatmap.time, t)
                    self.assertEqual(output.heatmap.parameter_first, stream.min_period)
                    self.assertEqual(output.heatmap.parameter_last, stream.max_period)
                    self.assertEqual(output.heatmap.parameter_resolution, 1.0)
                    if output.heatmap.is_empty():
                        self.assertTrue(math.isnan(output.dominant_cycle))
                        self.assertTrue(math.isnan(output.heatmap.value_min))
                        self.assertTrue(math.isnan(output.heatmap.value_max))
                    else:
                        self.number(output.dominant_cycle, reference[3])
                        self.assertEqual(output.heatmap.values, list(state.decibels))
                        self.assertEqual(output.heatmap.value_min, min(output.heatmap.values))
                        self.assertEqual(output.heatmap.value_max, max(output.heatmap.values))

    def test_first_five_bars_passthrough_and_sixth_bar_fir(self):
        stream = MASTER.MASTER_CLASS(window_length=1)
        for price in INPUTS[:5]:
            output = stream.update(price)
            self.assertEqual(stream.state.high_pass, price)
            self.assertEqual(stream.state.cleaned_data, price)
            self.assertEqual(stream.state.powers, (price*price,)*43)
            self.assertTrue(output.heatmap.is_empty())
        alpha = (1-math.sin(2*math.pi/40))/math.cos(2*math.pi/40)
        hp6 = .5*(1+alpha)*(INPUTS[5]-INPUTS[4])+alpha*INPUTS[4]
        cleaned6 = (hp6+2*INPUTS[4]+3*INPUTS[3]+3*INPUTS[2]+2*INPUTS[1]+INPUTS[0])/12
        output = stream.update(INPUTS[5])
        self.number(stream.state.high_pass, hp6)
        self.number(stream.state.cleaned_data, cleaned6)
        self.assertFalse(output.heatmap.is_empty())
        self.assertTrue(stream.is_primed)

    def test_minimum_window_and_single_channel(self):
        stream = MASTER.MASTER_CLASS(window_length=1)
        for price in INPUTS:
            output = stream.update(price)
            if stream.is_primed:
                self.number(output.dominant_cycle, 29.0)
                for value in output.heatmap.values:
                    self.number(value, 0.0)
        stream = MASTER.MASTER_CLASS(min_period=20, max_period=20)
        for price in INPUTS:
            output = stream.update(price)
            if stream.is_primed:
                self.number(output.dominant_cycle, 20.0)
                self.assertEqual(len(output.heatmap.values), 1)
                self.number(output.heatmap.values[0], 0.0)

    def test_full_record_window_first_valid_output_is_final_sample(self):
        stream = MASTER.MASTER_CLASS(window_length=252)
        for price in INPUTS[:-1]:
            output = stream.update(price)
            self.assertTrue(output.heatmap.is_empty())
            self.assertTrue(math.isnan(output.dominant_cycle))
        self.assertFalse(stream.is_primed)
        self.assertFalse(stream.update(INPUTS[-1]).heatmap.is_empty())
        self.assertTrue(stream.is_primed)

    def test_silence_and_guarded_db_and_centroid_retention(self):
        stream = MASTER.MASTER_CLASS()
        for _ in range(70):
            output = stream.update(0.0)
        self.assertEqual(output.heatmap.values, [0.0]*43)
        self.assertEqual(output.dominant_cycle, 29.0)
        # Set up the silent retained-DB branch directly, avoiding an enormous
        # wait for floating-point underflow in a naturally decaying signal.
        stream._db = [17.0]*43
        stream._db[10-stream.min_period] = 1.0
        stream._db[20-stream.min_period] = 2.5
        output = stream.update(0.0)
        # Correct article weights are 2 and 0.5; 20-DB or raw-power weights
        # would give a different answer. This proves the centroid contract.
        self.assertEqual(output.dominant_cycle, 12.0)
        stream._db = [17.0]*43
        output = stream.update(0.0)
        self.assertEqual(output.dominant_cycle, 12.0)
        self.assertEqual(output.heatmap.values, [17.0]*43)

    def test_current_maximum_has_no_agc_and_transform_is_nonlinear(self):
        stream = MASTER.MASTER_CLASS()
        saw_decay = False
        previous_maximum = 0.0
        for price in INPUTS:
            stream.update(price)
            state = stream.state
            self.assertEqual(state.maximum_power, max(state.powers))
            saw_decay |= state.maximum_power < .995*previous_maximum
            previous_maximum = state.maximum_power
        self.assertTrue(saw_decay)
        r = .5
        transformed = -10*math.log(.01/(1-.99*r))/math.log(10)
        self.assertGreater(transformed, 17.0)
        self.assertNotAlmostEqual(transformed, -10*math.log10(r), places=6)
        threshold = (1-.01*10**.3)/.99
        self.assertGreater(threshold, .9899)
        self.assertLess(threshold, .9900)

    def test_synthetic_twenty_bar_cycle_after_filter_transients(self):
        stream = MASTER.MASTER_CLASS(window_length=120)
        for t in range(1000):
            output = stream.update(math.sin(2*math.pi*t/20))
            if t >= 900:
                self.number(output.dominant_cycle, 20.0)

    def test_missing_invalid_and_overflowing_inputs_preserve_all_state(self):
        stream, control = MASTER.MASTER_CLASS(), MASTER.MASTER_CLASS()
        for price in INPUTS[:80]:
            stream.update(price)
            control.update(price)
        before, output, count = stream.state, stream.output, stream.samples_seen
        missing = stream.update(math.nan, 'missing')
        self.assertTrue(missing.heatmap.is_empty())
        self.assertEqual(missing.heatmap.time, 'missing')
        for invalid in (math.inf, -math.inf, 1e308, 10**400, True, None, '1'):
            with self.assertRaises(ValueError):
                stream.update(invalid)
            self.assertEqual(stream.state, before)
            self.assertEqual(stream.samples_seen, count)
            self.assertIs(stream.output, output)
        self.assertEqual(stream.update(INPUTS[80]), control.update(INPUTS[80]))

    def test_owned_heatmap_snapshots_and_reset_replay(self):
        stream, control = MASTER.MASTER_CLASS(), MASTER.MASTER_CLASS()
        for price in INPUTS:
            snapshot = stream.update(price)
            control.update(price)
        saved = snapshot.heatmap.values.copy()
        stream.update(100.0)
        control.update(100.0)
        self.assertEqual(snapshot.heatmap.values, saved)
        snapshot.heatmap.values[0] = -999.0
        self.assertEqual(stream.update(101.0), control.update(101.0))
        stream.reset()
        control = MASTER.MASTER_CLASS()
        for price in INPUTS:
            actual, expected = stream.update(price), control.update(price)
            if stream.is_primed:
                self.assertEqual(actual, expected)
            else:
                self.assertTrue(actual.heatmap.is_empty())

    def test_parameter_domains(self):
        invalid = ({'min_period':7}, {'max_period':7}, {'max_period':True},
                   {'window_length':0}, {'window_length':3.0},
                   {'highpass_period':4.0}, {'highpass_period':math.inf},
                   {'highpass_period':math.nan}, {'highpass_period':True})
        for parameters in invalid:
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                MASTER.MASTER_CLASS(**parameters)


if __name__ == '__main__':
    unittest.main()
