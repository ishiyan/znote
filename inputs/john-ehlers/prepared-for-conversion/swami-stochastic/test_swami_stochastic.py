"""Independent batch source checks, synthetic semantics, and streaming contract.

The oracle does not call master numerical helpers. It evaluates chronological
whole-series filters from the published equations, then each source bin with
its standalone startup policy. No expected fixture arrays are generated here.
"""

import copy
import importlib.util
import math
from pathlib import Path
import unittest


DIRECTORY = Path(__file__).resolve().parent
SLUG = DIRECTORY.name
SPEC = importlib.util.spec_from_file_location('master_'+SLUG.replace('-', '_'), DIRECTORY/(SLUG+'.py'))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_arrays(DIRECTORY/'test_testdata.py')


def _coefficients(period):
    a = math.exp(-math.sqrt(2)*math.pi/period)
    c2 = 2*a*math.cos(math.sqrt(2)*math.pi/period)
    c3 = -a*a
    return 1-c2-c3, c2, c3


def _roof_series(prices, shortest, longest, doubled=False):
    # Direct source alpha, independently checking the master's half-angle form.
    theta = (2 if doubled else 1)*math.sqrt(2)*math.pi/longest
    alpha = (math.cos(theta)+math.sin(theta)-1)/math.cos(theta)
    h, f = [0.0, 0.0], [0.0, 0.0]
    c1, c2, c3 = _coefficients(shortest)
    for t in range(2, len(prices)):
        h.append((1-alpha/2)*(1-alpha/2)*(prices[t]-2*prices[t-1]+prices[t-2])
                 +2*(1-alpha)*h[t-1]-(1-alpha)*(1-alpha)*h[t-2])
        f.append(c1*(h[t]+h[t-1])/2+c2*f[t-1]+c3*f[t-2])
    return f[2:]


def _bandpass_series(prices, period, delta):
    beta = math.cos(2*math.pi/period)
    gamma = 1/math.cos(4*math.pi*delta/period)
    alpha = gamma-math.sqrt(gamma*gamma-1)
    result = [0.0, 0.0]
    for t in range(2, len(prices)):
        result.append(.5*(1-alpha)*(prices[t]-prices[t-2])
                      + beta*(1+alpha)*result[t-1]-alpha*result[t-2])
    return result[2:]


def _parameters(case):
    return {name: value for name, value in case.items() if name != 'what_it_tests'}


def _assert_matrix(test, actual, expected, tolerance=2e-10):
    test.assertEqual(len(actual), len(expected))
    for i, (left, right) in enumerate(zip(actual, expected)):
        if isinstance(left, list):
            _assert_matrix(test, left, right, tolerance)
        elif math.isnan(right):
            test.assertTrue(math.isnan(left), f'NaN expected at {i}')
        else:
            test.assertTrue(math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance),
                            f'{i}: {left!r} != {right!r}')


def _collect(indicator, inputs):
    outputs = []
    for t, close in enumerate(inputs['INPUT_CLOSE']):
        if MASTER.REFERENCE_INPUT == 'ohlc':
            outputs.append(indicator.update(close, inputs['INPUT_HIGH'][t], inputs['INPUT_LOW'][t]))
        elif MASTER.REFERENCE_INPUT == 'hl2':
            outputs.append(indicator.update((inputs['INPUT_HIGH'][t]+inputs['INPUT_LOW'][t])/2))
        else:
            outputs.append(indicator.update(close))
    return outputs


def _map(output):
    return output.heatmap if hasattr(output, 'heatmap') else output


def _state(instance):
    # Compare nested numerical state rather than a helper object's identity.
    return {key: _state(value) if hasattr(value, '__dict__') else copy.deepcopy(value)
            for key, value in instance.__dict__.items()}


def _oracle(case, inputs):
    p = _parameters(case)
    periods = range(p['min_period'], p['max_period']+1)
    roofed = p['variant'] == 'roofed_2013'
    prices = inputs['INPUT_CLOSE']
    shortest, longest = p.get('shortest_cycle_period', 10), p.get('longest_cycle_period', 48)
    filtered = _roof_series(prices, shortest, longest) if roofed else prices
    c1, c2, c3 = _coefficients(shortest)
    result = [[math.nan]*len(periods) for _ in prices]
    for col, period in enumerate(periods):
        numerator = denominator = output = output2 = ratio1 = 0.0
        updates = 0
        for t in range(period-1, len(filtered)):
            window = filtered[t-period+1:t+1]
            high, low = max(window), min(window)
            if roofed:
                ratio = (filtered[t]-low)/(high-low) if high != low else .5
                value = c1*(ratio+ratio1)/2+c2*output+c3*output2
                output2, output = output, min(1, max(0, value))
                ratio1 = ratio
            else:
                ra, oa = p.get('range_alpha', .5), p.get('output_alpha', .2)
                numerator = ra*(filtered[t]-low)+(1-ra)*numerator
                denominator = ra*(high-low)+(1-ra)*denominator
                if denominator != 0:
                    output = oa*numerator/denominator+(1-oa)*output
            updates += 1
            bar = t+2 if roofed else t
            if bar >= (p['max_period']+3 if roofed else p['max_period']-1):
                result[bar][col] = output
    return {'HEATMAP': result}

class SourceAndStreamingTests(unittest.TestCase):
    def test_every_proposed_case_against_independent_source(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(parameters=_parameters(case)):
                actual = MASTER._run_reference(case, INPUTS)
                expected = _oracle(case, INPUTS)
                for component in expected:
                    _assert_matrix(self, actual[component], expected[component])

    def test_dimensions_bounds_and_exact_warmup(self):
        for case in MASTER.REFERENCE_CASES:
            instance = MASTER.MASTER_CLASS(**_parameters(case))
            outputs = _collect(instance, INPUTS)
            bins = instance.max_period-instance.min_period+1
            for i, result in enumerate(outputs):
                column = _map(result)
                self.assertEqual(column.parameter_first, instance.min_period)
                self.assertEqual(column.parameter_last, instance.max_period)
                self.assertEqual(column.parameter_resolution, 1)
                if i < instance.warmup_bars:
                    self.assertTrue(column.is_empty(), f'{case}: bar {i+1}')
                    self.assertTrue(math.isnan(column.value_min))
                    for diagnostic in MASTER.DIAGNOSTIC_COMPONENTS:
                        self.assertEqual(getattr(result, diagnostic), [])
                else:
                    self.assertEqual(len(column.values), bins)
                    self.assertEqual(column.value_min, min(column.values))
                    self.assertEqual(column.value_max, max(column.values))
                    self.assertTrue(all(math.isfinite(x) for x in column.values))
                    for diagnostic in MASTER.DIAGNOSTIC_COMPONENTS:
                        self.assertEqual(len(getattr(result, diagnostic)), bins)

    def test_missing_input_reset_and_owned_outputs(self):
        instance = MASTER.MASTER_CLASS()
        original = _collect(instance, INPUTS)
        saved = copy.deepcopy(original)
        before = _state(instance)
        self.assertTrue(_map(instance.update(math.nan)).is_empty())
        self.assertEqual(_state(instance), before)
        with self.assertRaises(ValueError):
            instance.update(math.inf)
        self.assertEqual(_state(instance), before)
        self.assertEqual(original, saved)
        # Check state-preserving missing call with a control resumed stream.
        control = MASTER.MASTER_CLASS()
        _collect(control, INPUTS)
        self.assertEqual(instance.update(100.0), control.update(100.0))
        instance.reset()
        replayed = _collect(instance, INPUTS)
        for first, second in zip(original, replayed):
            _assert_matrix(self, _map(first).values, _map(second).values)

    def test_invalid_parameters(self):
        for parameters in ({'min_period': True}, {'max_period': 1}, {'min_period': 10, 'max_period': 9}):
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                MASTER.MASTER_CLASS(**parameters)

    def test_synthetic_negative_prices_reversals_and_plateaus(self):
        # Independent source checks on data unlike the financial fixture:
        # negatives, sharp jumps, symmetric reversals, exact repeated prices.
        values = [-20.0+3*math.sin(2*math.pi*t/18) for t in range(90)]
        values += [-15.0]*65
        values += [-40.0+t*.25 for t in range(97)]
        inputs = {'INPUT_CLOSE': values, 'INPUT_HIGH': [x+.5 for x in values],
                  'INPUT_LOW': [x-.5 for x in values]}
        # Default case and each source variant are sufficient here; full grid
        # was already independently compared on shared OHLC in another test.
        cases = [MASTER.REFERENCE_CASES[0]]
        if SLUG in ('swami-stochastic', 'swami-relative-strength-index'):
            cases.append(MASTER.REFERENCE_CASES[4])
        for case in cases:
            expected = _oracle(case, inputs)
            actual = MASTER._run_reference(case, inputs)
            for component in expected:
                _assert_matrix(self, actual[component], expected[component], 2e-8)

    def test_flat_input_source_branch(self):
        instance = MASTER.MASTER_CLASS()
        outputs = [instance.update(10.0) for _ in range(400)]
        column = _map(outputs[-1])
        self.assertFalse(column.is_empty())
        if SLUG in ('swami-swing-wave', 'swami-relative-strength-index'):
            self.assertEqual(column.values, [0.0]*len(column.values))
        elif SLUG == 'swami-convolution':
            self.assertEqual(column.values, [-0.5]*len(column.values))
            self.assertEqual(outputs[-1].correlation, [0.0]*len(column.values))
        elif SLUG == 'swami-aroon':
            self.assertEqual(column.values, [1.0]*len(column.values))
        else:
            for value in column.values:
                self.assertAlmostEqual(value, .5, places=11)

    def test_export_helpers_and_confirmation_gate(self):
        self.assertEqual(MASTER._float_literal(math.nan, 'nan'), 'nan')
        self.assertEqual(MASTER._float_literal(1/3, 'NaN'), '0.333333333333333')
        suffixes = [MASTER._case_suffix(case) for case in MASTER.REFERENCE_CASES]
        self.assertEqual(len(suffixes), len(set(suffixes)))
        self.assertTrue(all('.' not in suffix for suffix in suffixes))
        if not MASTER.REFERENCE_CASES_CONFIRMED:
            with self.assertRaisesRegex(ValueError, 'confirmation'):
                MASTER.generate_reference_data(DIRECTORY)

    def test_classic_zero_range_retains_zero(self):
        instance = MASTER.SwamiStochastic(variant='classic_2012')
        for _ in range(300):
            result = instance.update(10.0)
        self.assertEqual(result.values, [0.0]*len(result.values))

    def test_book_clipping_changes_future_smoothing_state(self):
        # Impulses drive the output stage to saturation; comparing the whole
        # sequence verifies that clipped values, not unclipped overshoots,
        # enter later recurrence history.
        inputs = {'INPUT_CLOSE': [1.0]*70+[100.0]*70+[-100.0]*112}
        case = MASTER.REFERENCE_CASES[4]
        _assert_matrix(self, MASTER._run_reference(case, inputs)['HEATMAP'],
                       _oracle(case, inputs)['HEATMAP'])



    def test_generated_five_language_reference_data(self):
        if not MASTER.REFERENCE_CASES_CONFIRMED:
            self.skipTest('reference generation is not confirmed yet')
        spec = importlib.util.spec_from_file_location('fixture_verifier', DIRECTORY/'verify_reference_data.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        count, values = verifier.verify()
        self.assertEqual(count, len(MASTER.REFERENCE_CASES)*(3+len(MASTER.DIAGNOSTIC_COMPONENTS)))
        self.assertGreater(values, 0)

if __name__ == '__main__':
    unittest.main()
