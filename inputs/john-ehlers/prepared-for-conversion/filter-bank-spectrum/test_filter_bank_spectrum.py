"""Independent article-equation, streaming-state and heatmap tests.

The oracle uses full chronological histories and source period indices.
It shares no numerical helper with the bounded-state master. Run with
python3 -m unittest discover -s THIS_FOLDER -p test_filter_bank_spectrum.py.
Fixture verification is separate: python3 verify_reference_data.py.
"""

import importlib.util
import math
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('fbs_master', HERE/'filter-bank-spectrum.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_arrays(HERE/'test_testdata.py')['INPUT_CLOSE']


def article_batch(prices, p):
    """Full-array transcription of BOTH article sidebars at full precision.

    p.centroid_min_period selects the sole centroid difference between the
    listings. Zero prehistory and arithmetic even medians are explicit here,
    rather than borrowed from the master. Array histories use bar and period
    indices; no old/older swaps or master parameter coefficients are reused.
    """
    count = len(prices)
    price = [0.0] + list(prices)
    hp, smooth, dc, dom, sine, cosine = ([0.0]*(count+1) for _ in range(6))
    i, q, real, imag, ampl, db = (
        [[0.0]*(p.max_period+1) for _ in range(count+1)] for _ in range(6))
    result = []
    for t in range(1, count+1):
        hp_alpha = ((1-math.sin(2*math.pi/p.highpass_period))
                    /math.cos(2*math.pi/p.highpass_period))
        hp[t] = .5*(1+hp_alpha)*(price[t]-price[t-1])+hp_alpha*hp[t-1]
        weights = [1, 2, 3, 3, 2, 1]
        smooth[t] = sum(weights[k]*hp[t-k] for k in range(6) if t-k >= 0)/12
        if t < 7:
            smooth[t] = price[t]-price[t-1]
        if t == 1:
            smooth[t] = 0.0
        delta = -.015*t+.5
        if delta < p.bandwidth:
            delta = p.bandwidth
        if t > 6:
            for n in range(p.min_period, p.max_period+1):
                beta = math.cos(2*math.pi/n)
                gamma = 1/math.cos(4*math.pi*delta/n)
                alpha = gamma-math.sqrt(gamma*gamma-1)
                q[t][n] = n/(2*math.pi)*(smooth[t]-smooth[t-1])
                i[t][n] = smooth[t]
                real[t][n] = (.5*(1-alpha)*(i[t][n]-i[t-2][n])
                              +beta*(1+alpha)*real[t-1][n]-alpha*real[t-2][n])
                imag[t][n] = (.5*(1-alpha)*(q[t][n]-q[t-2][n])
                              +beta*(1+alpha)*imag[t-1][n]-alpha*imag[t-2][n])
                ampl[t][n] = real[t][n]*real[t][n]+imag[t][n]*imag[t][n]
        maximum = 0.0
        for n in range(p.min_period, p.max_period+1):
            if ampl[t][n] > maximum:
                maximum = ampl[t][n]
        for n in range(p.min_period, p.max_period+1):
            db[t][n] = db[t-1][n]
            if maximum != 0 and ampl[t][n]/maximum > 0:
                db[t][n] = -10*math.log(.01/(1-.99*ampl[t][n]/maximum))/math.log(10)
            if db[t][n] > 20:
                db[t][n] = 20.0
        numerator = denominator = 0.0
        dc[t] = dc[t-1]
        for n in range(p.centroid_min_period, p.max_period+1):
            if db[t][n] <= 3:
                numerator += n*(20-db[t][n])
                denominator += 20-db[t][n]
            if denominator != 0:
                dc[t] = numerator/denominator
        ordered = sorted(dc[t-k] if t-k >= 0 else 0.0 for k in range(p.median_length))
        m = p.median_length
        dom[t] = ordered[m//2] if m % 2 else (ordered[m//2-1]+ordered[m//2])/2
        if dom[t] < 8:
            dom[t] = 20.0
        beta = math.cos(2*math.pi/dom[t])
        gamma = 1/math.cos(4*math.pi*delta/dom[t])
        alpha = gamma-math.sqrt(gamma*gamma-1)
        sine[t] = (.5*(1-alpha)*(smooth[t]-smooth[t-1])
                   +beta*(1+alpha)*sine[t-1] - alpha*(sine[t-2] if t >= 2 else 0.0))
        cosine[t] = dom[t]/(2*math.pi)*(sine[t]-sine[t-1])
        result.append((hp[t], smooth[t], delta, dc[t], dom[t], sine[t], cosine[t],
                       ampl[t][p.min_period:], db[t][p.min_period:]))
    return result


class NumericalTests(unittest.TestCase):
    def number(self, actual, expected):
        self.assertTrue(math.isclose(actual, expected, rel_tol=3e-11, abs_tol=3e-11),
                        f'{actual!r} != {expected!r}')

    def test_all_cases_match_independent_article_histories(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case):
                stream = MASTER.FilterBankSpectrum(**{k:v for k,v in case.items() if k != 'what_it_tests'})
                expected = article_batch(INPUTS, stream.parameters)
                for t, (price, reference) in enumerate(zip(INPUTS, expected), 1):
                    output = stream.update(price, t)
                    state = stream.state
                    for actual, wanted in zip(state[:7], reference[:7]):
                        self.number(actual, wanted)
                    for actuals, wanteds in zip(state[7:], reference[7:]):
                        for actual, wanted in zip(actuals, wanteds):
                            self.number(actual, wanted)
                    self.assertEqual(output.heatmap.is_empty(), t <= stream.warmup_bars)
                    if t <= stream.warmup_bars:
                        self.assertEqual(output.heatmap.values, [])
                        self.assertTrue(all(math.isnan(v) for v in output[1:]))
                        self.assertTrue(math.isnan(output.heatmap.value_min))
                        self.assertTrue(math.isnan(output.heatmap.value_max))
                    else:
                        for actual, wanted in zip(output[1:], reference[4:7]):
                            self.number(actual, wanted)
                        self.assertEqual(output.heatmap.time, t)
                        self.assertEqual(output.heatmap.parameter_first, stream.min_period)
                        self.assertEqual(output.heatmap.parameter_last, stream.max_period)
                        self.assertEqual(output.heatmap.parameter_resolution, 1.0)
                        self.assertEqual(output.heatmap.value_min, min(output.heatmap.values))
                        self.assertEqual(output.heatmap.value_max, max(output.heatmap.values))

    def test_bank_starts_at_seven_but_tuned_filter_runs_earlier(self):
        stream = MASTER.FilterBankSpectrum()
        for price in INPUTS[:6]:
            output = stream.update(price)
            self.assertEqual(stream.state.amplitudes, (0.0,)*43)
            self.assertTrue(output.heatmap.is_empty())
        # A port that delays Value1 until priming loses these early states.
        self.assertNotEqual(stream.state.sine, 0.0)
        stream.update(INPUTS[6])
        self.assertGreater(max(stream.state.amplitudes), 0.0)
        self.assertFalse(stream.is_primed)
        for price in INPUTS[7:10]:
            output = stream.update(price)
        self.assertTrue(stream.is_primed)
        self.assertFalse(output.heatmap.is_empty())

    def test_literal_delta_schedule_and_full_precision(self):
        stream = MASTER.FilterBankSpectrum()
        stream.update(0.0)
        self.assertEqual(stream.state.delta, .485)
        for _ in range(22):
            stream.update(0.0)
        self.assertAlmostEqual(stream.state.delta, .155, places=15)
        stream.update(0.0)
        self.assertEqual(stream.state.delta, .15)
        for price in INPUTS:
            old_sine = stream.state.sine
            output = stream.update(price)
            self.assertEqual(output.cosine, output.dominant_cycle/(2*math.pi)*(output.sine-old_sine))
        self.assertNotEqual(output.cosine, output.dominant_cycle/6.28*(output.sine-old_sine))

    def test_silence_preserves_source_hot_zero_db_and_nonzero_centroid(self):
        for cutoff, expected in ((10, 30.0), (8, 29.0)):
            stream = MASTER.FilterBankSpectrum(centroid_min_period=cutoff)
            for _ in range(40):
                output = stream.update(0.0)
            self.assertEqual(output.heatmap.values, [0.0]*43)
            self.assertEqual(output.dominant_cycle, expected)
            self.assertEqual(output.sine, 0.0)
            self.assertEqual(output.cosine, 0.0)
        # Establish a silent bank with nonzero retained DB and no qualifying
        # channel. This branch is difficult to reach naturally before numeric
        # underflow, so set up its exact reachable recurrence state directly.
        stream = MASTER.FilterBankSpectrum()
        for _ in range(40):
            stream.update(0.0)
        stream._db = [17.0]*43
        for _ in range(15):
            output = stream.update(0.0)
        self.assertEqual(output.heatmap.values, [17.0]*43)
        self.assertEqual(output.dominant_cycle, 30.0)

    def test_zero_padded_even_arithmetic_median_and_fallback(self):
        stream = MASTER.FilterBankSpectrum()
        expected = [20.0, 20.0, 20.0, 20.0, 15.0, 30.0]
        for period in expected:
            stream.update(0.0)
            self.assertEqual(stream.state.tuned_period, period)

    def test_one_channel_and_synthetic_period(self):
        stream = MASTER.FilterBankSpectrum(min_period=20, max_period=20, centroid_min_period=20)
        for price in INPUTS:
            result = stream.update(price)
            if stream.is_primed:
                self.number(result.dominant_cycle, 20.0)
                self.assertEqual(len(result.heatmap.values), 1)
                self.number(result.heatmap.values[0], 0.0)
        stream = MASTER.FilterBankSpectrum()
        periods = []
        for t in range(1600):
            result = stream.update(math.sin(2*math.pi*t/24))
            if t >= 1500:
                periods.append(result.dominant_cycle)
        self.assertLess(max(abs(p-24) for p in periods), 1.0)

    def test_nan_infinity_overflow_and_invalid_type_do_not_change_state(self):
        stream, control = MASTER.FilterBankSpectrum(), MASTER.FilterBankSpectrum()
        for price in INPUTS[:80]:
            stream.update(price)
            control.update(price)
        before, output, count = stream.state, stream.output, stream.samples_seen
        missing = stream.update(math.nan, 'missing')
        self.assertTrue(missing.heatmap.is_empty())
        self.assertEqual(missing.heatmap.time, 'missing')
        for invalid in (math.inf, -math.inf, True, '100', None, 1e308, 10**400):
            with self.assertRaises(ValueError):
                stream.update(invalid)
            self.assertEqual(stream.state, before)
            self.assertIs(stream.output, output)
            self.assertEqual(stream.samples_seen, count)
        self.assertEqual(stream.update(INPUTS[80]), control.update(INPUTS[80]))

    def test_heatmap_snapshots_and_reset(self):
        stream, control = MASTER.FilterBankSpectrum(), MASTER.FilterBankSpectrum()
        for price in INPUTS:
            last = stream.update(price)
            control.update(price)
        copied = last.heatmap.values.copy()
        stream.update(100.0)
        control.update(100.0)
        self.assertEqual(last.heatmap.values, copied)
        last.heatmap.values[0] = -999.0
        self.assertEqual(stream.update(101.0), control.update(101.0))
        stream.reset()
        control = MASTER.FilterBankSpectrum()
        for price in INPUTS:
            actual, expected = stream.update(price), control.update(price)
            if stream.is_primed:
                self.assertEqual(actual, expected)
            else:
                self.assertTrue(actual.heatmap.is_empty())

    def test_parameter_domains(self):
        for kwargs in ({'min_period':7}, {'max_period':7}, {'max_period':True},
                       {'centroid_min_period':7}, {'centroid_min_period':51},
                       {'highpass_period':4}, {'highpass_period':math.inf},
                       {'median_length':0}, {'median_length':3.0},
                       {'bandwidth':0}, {'bandwidth':.51}, {'bandwidth':math.nan}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                MASTER.FilterBankSpectrum(**kwargs)


if __name__ == '__main__':
    unittest.main()
