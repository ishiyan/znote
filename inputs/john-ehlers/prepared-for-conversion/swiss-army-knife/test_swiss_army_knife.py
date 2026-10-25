"""Independent article recurrences, filter identities and streaming tests.

The source oracle uses full chronological price/output histories and its own
coefficient calculations. It never calls the master's coefficient selector.
All mathematics is standard Python. Run python3 -m unittest discover -s
THIS_FOLDER -p test_swiss_army_knife.py -v.
"""

import importlib.util
import math
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('swiss_knife_master', HERE/'swiss-army-knife.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_arrays(HERE/'test_testdata.py')['INPUT_CLOSE']


def article_batch(prices, mode, n, period, delta, factor=None):
    """Full-history translation of article/MESA code with explicit precision.

    factor=None restores the exact two-pole cutoff factor. Passing 2.415
    separately demonstrates the requested difference from rounded source.
    Histories and source bar indexing are independent of the master's buffers.
    """
    price = [0.0] + list(prices)
    filt = [0.0] * len(price)
    result = []
    for t in range(1, len(price)):
        c0, c1, b0, b1, b2, a1, a2 = 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0
        omega = 2*math.pi/period
        if mode == 'EMA':
            alpha = (math.cos(omega)+math.sin(omega)-1)/math.cos(omega)
            b0, a1 = alpha, 1-alpha
        elif mode == 'SMA':
            c1, b0, a1 = 1/n, 1/n, 1.0
        elif mode in ('Gauss', 'Butter', '2PHP'):
            beta = ((1+math.sqrt(2)) if factor is None else factor)*(1-math.cos(omega))
            alpha = -beta+math.sqrt(beta*beta+2*beta)
            a1, a2 = 2*(1-alpha), -(1-alpha)*(1-alpha)
            if mode == 'Gauss':
                c0 = alpha*alpha
            elif mode == 'Butter':
                c0, b1, b2 = alpha*alpha/4, 2.0, 1.0
            else:
                c0, b1, b2 = (1-alpha/2)*(1-alpha/2), -2.0, 1.0
        elif mode == 'Smooth':
            c0, b1, b2 = .25, 2.0, 1.0
        elif mode == 'HP':
            alpha = (math.cos(omega)+math.sin(omega)-1)/math.cos(omega)
            c0, b1, a1 = 1-alpha/2, -1.0, 1-alpha
        elif mode in ('BP', 'BS'):
            beta = math.cos(omega)
            gamma = 1/math.cos(4*math.pi*delta/period)
            alpha = gamma-math.sqrt(gamma*gamma-1)
            a1, a2 = beta*(1+alpha), -alpha
            if mode == 'BP':
                c0, b2 = (1-alpha)/2, -1.0
            else:
                c0, b1, b2 = (1+alpha)/2, -2*beta, 1.0
        if t <= n:
            if mode in ('HP', '2PHP'):
                filt[t] = 0.0
            elif mode == 'Smooth':
                filt[t] = filt[t-1]
            else:
                filt[t] = price[t]
        else:
            x1 = price[t-1]
            x2 = price[t-2] if t >= 2 else 0.0
            x_n = price[t-n] if t-n >= 0 else 0.0
            f2 = filt[t-2] if t >= 2 else 0.0
            filt[t] = c0*(b0*price[t]+b1*x1+b2*x2)+a1*filt[t-1]+a2*f2-c1*x_n
        result.append((filt[t], filt[t] if t > n else math.nan))
    return result


class NumericalTests(unittest.TestCase):
    def number(self, actual, expected):
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual))
        else:
            self.assertTrue(math.isclose(actual, expected, rel_tol=3e-11, abs_tol=3e-11),
                            f'{actual!r} != {expected!r}')

    def test_all_36_cases_against_independent_source_transcription(self):
        self.assertEqual(len(MASTER.REFERENCE_CASES), 36)
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case):
                parameters = {k:v for k,v in case.items() if k != 'what_it_tests'}
                stream = MASTER.SwissArmyKnife(**parameters)
                expected = article_batch(INPUTS, parameters['filter_type'], parameters['n'],
                                         parameters['period'], parameters['delta'])
                for t, (price, (hidden, public)) in enumerate(zip(INPUTS, expected), 1):
                    output = stream.update(price)
                    self.number(output, public)
                    self.number(stream.state.filtered, hidden)
                    self.assertEqual(stream.is_primed, t > parameters['n'])
                    self.assertEqual(stream.samples_seen, t)

    def test_startup_assignments_and_source_plot_gate_for_every_mode(self):
        for mode in MASTER.FILTER_TYPES:
            stream = MASTER.SwissArmyKnife(mode, n=5)
            for t, price in enumerate(INPUTS[:5], 1):
                self.assertTrue(math.isnan(stream.update(price)))
                wanted = 0.0 if mode in ('HP', '2PHP', 'Smooth') else price
                self.assertEqual(stream.state.filtered, wanted)
                self.assertEqual(stream.state.previous_inputs[0], price)
                self.assertFalse(stream.is_primed)
            self.assertFalse(math.isnan(stream.update(INPUTS[5])))
            self.assertTrue(stream.is_primed)
        stream = MASTER.SwissArmyKnife()
        expected = stream.coefficients.c0*INPUTS[0]
        self.assertEqual(stream.update(INPUTS[0]), expected)
        self.assertTrue(stream.is_primed)

    def test_sma_source_seed_has_constant_offset_from_true_rolling_average(self):
        for n in (1, 5, 20, 50, 251):
            stream = MASTER.SwissArmyKnife('SMA', n=n)
            seed_bias = INPUTS[n-1]-sum(INPUTS[:n])/n
            for t, price in enumerate(INPUTS, 1):
                output = stream.update(price)
                if t > n:
                    conventional = sum(INPUTS[t-n:t])/n
                    self.number(output, conventional+seed_bias)
            if n > 1:
                self.assertNotAlmostEqual(seed_bias, 0.0)
        # N=1 is the special case where the source seed is a correct SMA seed.
        stream = MASTER.SwissArmyKnife('SMA', n=1)
        outputs = [stream.update(x) for x in INPUTS]
        for actual, price in zip(outputs[1:], INPUTS[1:]):
            self.number(actual, price)

    def test_record_boundary_and_fully_unprimed_case(self):
        for n in (251, 252):
            stream = MASTER.SwissArmyKnife('SMA', n=n)
            outputs = [stream.update(x) for x in INPUTS]
            self.assertTrue(all(math.isnan(x) for x in outputs[:n]))
            self.assertEqual(stream.is_primed, n == 251)
            self.assertEqual(math.isnan(outputs[-1]), n == 252)

    def test_restored_gaussian_constant_has_exact_two_pole_half_power_corner(self):
        stream = MASTER.SwissArmyKnife('Gauss')
        alpha = stream.coefficients.alpha
        q = 1-alpha
        omega = 2*math.pi/20
        denominator_power = 1+q*q-2*q*math.cos(omega)
        total_power_gain = alpha**4/denominator_power**2
        self.assertAlmostEqual(total_power_gain, .5, places=13)
        self.assertEqual(MASTER.TWO_POLE_FACTOR, 1+math.sqrt(2))
        self.assertNotEqual(MASTER.TWO_POLE_FACTOR, 2.415)
        full = article_batch(INPUTS, 'Gauss', 0, 20, .1)
        literal = article_batch(INPUTS, 'Gauss', 0, 20, .1, factor=2.415)
        self.assertNotEqual(full[-1][0], literal[-1][0])
        self.assertLess(abs(full[-1][0]-literal[-1][0]), .01)

    def test_gaussian_equals_two_emas_with_its_own_alpha(self):
        stream = MASTER.SwissArmyKnife('Gauss')
        alpha = stream.coefficients.alpha
        first = second = 0.0
        for price in INPUTS:
            first = alpha*price+(1-alpha)*first
            second = alpha*first+(1-alpha)*second
            self.number(stream.update(price), second)

    def test_butter_equals_gaussian_followed_by_three_tap_smooth(self):
        gaussian = MASTER.SwissArmyKnife('Gauss')
        smooth = MASTER.SwissArmyKnife('Smooth')
        butter = MASTER.SwissArmyKnife('Butter')
        for price in INPUTS:
            self.number(butter.update(price), smooth.update(gaussian.update(price)))

    def test_zero_state_bandpass_plus_bandstop_reconstructs_input(self):
        for period, delta in ((5, .1), (20, .05), (20.5, .1), (50, .5)):
            bp = MASTER.SwissArmyKnife('BP', period=period, delta=delta)
            bs = MASTER.SwissArmyKnife('BS', period=period, delta=delta)
            for price in INPUTS:
                self.number(bp.update(price)+bs.update(price), price)
            # This also detects the AmiBroker tip's erroneous BS b2=-1.
            self.assertEqual(bs.coefficients.b2, 1.0)

    def test_step_response_dc_behavior_of_all_modes(self):
        for mode in MASTER.FILTER_TYPES:
            stream = MASTER.SwissArmyKnife(mode, n=5 if mode == 'SMA' else 0)
            for _ in range(1000):
                value = stream.update(1.0)
            wanted = 0.0 if mode in ('HP', '2PHP', 'BP') else 1.0
            self.number(value, wanted)

    def test_smooth_uses_price_history_even_with_delayed_gate(self):
        stream = MASTER.SwissArmyKnife('Smooth', n=5)
        outputs = [stream.update(price) for price in INPUTS[:6]]
        self.assertTrue(all(math.isnan(x) for x in outputs[:5]))
        self.assertEqual(outputs[5], (INPUTS[5]+2*INPUTS[4]+INPUTS[3])/4)

    def test_missing_invalid_inputs_and_intermediate_overflow_are_atomic(self):
        stream, control = MASTER.SwissArmyKnife(), MASTER.SwissArmyKnife()
        for price in INPUTS[:80]:
            stream.update(price)
            control.update(price)
        before, last = stream.state, stream.output
        self.assertTrue(math.isnan(stream.update(math.nan)))
        for invalid in (math.inf, -math.inf, 10**400, True, None, '1'):
            with self.assertRaises(ValueError):
                stream.update(invalid)
            self.assertEqual(stream.state, before)
            self.assertEqual(stream.output, last)
        self.assertEqual(stream.update(INPUTS[80]), control.update(INPUTS[80]))
        smooth = MASTER.SwissArmyKnife('Smooth')
        smooth.update(1e308)
        before, last = smooth.state, smooth.output
        with self.assertRaises(ValueError):
            smooth.update(1e308)  # 2*previous price overflows before /4.
        self.assertEqual(smooth.state, before)
        self.assertEqual(smooth.output, last)

    def test_reset_replay_and_immutable_state_snapshots(self):
        stream = MASTER.SwissArmyKnife('Gauss', n=5)
        expected = [stream.update(price) for price in INPUTS]
        snapshot = stream.state
        stream.update(100.0)
        self.assertEqual(snapshot.samples_seen, 252)
        self.assertEqual(snapshot.previous_inputs[0], INPUTS[-1])
        stream.reset()
        for actual, wanted in zip([stream.update(price) for price in INPUTS], expected):
            self.number(actual, wanted)

    def test_unused_parameters_and_invalid_domains(self):
        for mode, n in (('SMA', 5), ('Smooth', 0)):
            short = MASTER.SwissArmyKnife(mode, n=n, period=5, delta=.05)
            long = MASTER.SwissArmyKnife(mode, n=n, period=50, delta=.5)
            for price in INPUTS:
                self.number(short.update(price), long.update(price))
        for parameters in ({'filter_type':'DFT'}, {'filter_type':'unknown'},
                           {'filter_type':'SMA'}, {'n':-1}, {'n':True}, {'n':2.0},
                           {'period':4}, {'period':math.nan}, {'period':math.inf},
                           {'delta':.049}, {'delta':.501}, {'delta':True}):
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                MASTER.SwissArmyKnife(**parameters)


if __name__ == '__main__':
    unittest.main()
