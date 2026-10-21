"""Independent source-equation, streaming-behavior and saved-fixture checks.

Run: python3 -m unittest discover -s . -p 'test_autocorrelation_heatmap.py' -v
The batch oracle uses full histories and the one-based source Corr indexing.
It never calls the master's smoothing or correlation calculation.
"""

import importlib.util
import math
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("autocorrelation_master", HERE / "autocorrelation-heatmap.py")
master = importlib.util.module_from_spec(spec)
spec.loader.exec_module(master)
FIXTURES = master._load_python_arrays(HERE / "test_testdata.py")
INPUT_CLOSE = FIXTURES["INPUT_CLOSE"]


def batch_source(closes, length, smoothing_period, max_lag):
    """Literal TASC/MESA loop with full-series indexing and zero prehistory."""
    filt = [0.0] * len(closes)
    corr = [0.0] * 101  # Literal one-based Corr[lag+1] with unused index zero.
    angle = math.sqrt(2.0) * math.pi / smoothing_period
    a = math.exp(-angle)
    c2 = 2.0 * a * math.cos(angle)
    c3 = -a * a
    c1 = (1.0 + c2 - c3) / 4.0
    outputs = []
    for t, price in enumerate(closes):
        if t < 3:
            filt[t] = price
        else:
            filt[t] = ((1.0-c1)*price + (2.0*c1-c2)*closes[t-1]
                       - (c1+c3)*closes[t-2] + c2*filt[t-1] + c3*filt[t-2])
        for lag in range(max_lag+1):
            sx = sy = sxx = sxy = syy = 0.0
            for j in range(length):
                x = filt[t-j] if t-j >= 0 else 0.0
                y = filt[t-lag-j] if t-lag-j >= 0 else 0.0
                sx += x
                sy += y
                sxx += x*x
                sxy += x*y
                syy += y*y
            vx = length*sxx-sx*sx
            vy = length*syy-sy*sy
            if vx > 0.0 and vy > 0.0:
                corr[lag+1] = (length*sxy-sx*sy) / math.sqrt(vx*vy)
        if t+1 < max(4, length+max_lag):
            outputs.append((filt[t], None))
        else:
            outputs.append((filt[t], corr[1:max_lag+2]))
    return outputs


class TestAutocorrelationHeatmap(unittest.TestCase):
    def assert_numbers(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            if math.isnan(b):
                self.assertTrue(math.isnan(a))
            else:
                self.assertTrue(math.isclose(a, b, rel_tol=1e-13, abs_tol=1e-13), (a, b))

    def test_all_reference_cases_against_independent_source(self):
        self.assertEqual(len(INPUT_CLOSE), 252)
        self.assertLessEqual(len(master.REFERENCE_CASES), 64)
        for case in master.REFERENCE_CASES:
            with self.subTest(case=case):
                indicator = master.AutocorrelationHeatmap(case.length, case.smoothing_period, case.max_lag)
                expected = batch_source(INPUT_CLOSE, case.length, case.smoothing_period, case.max_lag)
                for index, (price, (filtered, bins)) in enumerate(zip(INPUT_CLOSE, expected)):
                    actual = indicator.update(price)
                    self.assertEqual(indicator.state.filtered, filtered)
                    self.assertEqual(indicator.state.accepted_samples, index+1)
                    if bins is None:
                        self.assertTrue(actual.is_empty())
                        self.assertTrue(math.isnan(actual.value_min))
                        self.assertTrue(math.isnan(actual.value_max))
                    else:
                        self.assert_numbers(actual.values, bins)
                        self.assertEqual(actual.value_min, min(bins))
                        self.assertEqual(actual.value_max, max(bins))
                        self.assertEqual(actual.parameter_last, float(case.max_lag))

    def test_saved_fixtures_are_exact_15_digit_serializations(self):
        expected = {name: value for name, value in FIXTURES.items() if name.startswith("EXPECTED_")}
        if not master.REFERENCE_CASES_CONFIRMED:
            self.assertFalse(expected)
            self.skipTest("Parameter confirmation precedes fixture generation")
        names = {"EXPECTED_" + master._case_suffix(case) + "_" + component
                 for case in master.REFERENCE_CASES for component in ("HEATMAP", "MIN", "MAX")}
        self.assertEqual(set(expected), names)
        for case in master.REFERENCE_CASES:
            indicator = master.AutocorrelationHeatmap(case.length, case.smoothing_period, case.max_lag)
            prefix = "EXPECTED_" + master._case_suffix(case) + "_"
            for row, price in enumerate(INPUT_CLOSE):
                result = indicator.update(price)
                components = {"HEATMAP": result.values if not result.is_empty()
                              else [math.nan]*(case.max_lag+1),
                              "MIN": result.value_min, "MAX": result.value_max}
                for component, raw in components.items():
                    saved = expected[prefix+component]
                    self.assertEqual(len(saved), 252)
                    actual_values = raw if isinstance(raw, list) else [raw]
                    saved_values = saved[row] if isinstance(saved[row], list) else [saved[row]]
                    self.assertEqual(len(actual_values), len(saved_values))
                    for original, literal in zip(actual_values, saved_values):
                        if math.isnan(original):
                            self.assertTrue(math.isnan(literal))
                        else:
                            self.assertEqual(literal, float(format(original, ".15g")))

    def test_missing_rejected_samples_reset_and_priming(self):
        subject = master.AutocorrelationHeatmap(length=5, max_lag=12)
        clean = master.AutocorrelationHeatmap(length=5, max_lag=12)
        self.assertEqual(subject.warmup_bars, 16)
        for index, price in enumerate(INPUT_CLOSE[:50]):
            before = subject.state
            self.assertTrue(subject.update(math.nan).is_empty())
            self.assertEqual(subject.state, before)
            for invalid in (math.inf, -math.inf, 1e308):
                with self.assertRaises(ValueError):
                    subject.update(invalid)
                self.assertEqual(subject.state, before)
            actual, expected = subject.update(price), clean.update(price)
            self.assert_numbers(actual.values, expected.values)
            self.assertEqual(subject.primed, index+1 >= 17)
        subject.reset()
        clean.reset()
        self.assertEqual(subject.state, clean.state)
        for price in INPUT_CLOSE[:50]:
            self.assert_numbers(subject.update(price).values, clean.update(price).values)

    def test_analytical_sine_pattern_and_two_point_limit(self):
        # Small zero-centered sinusoid avoids large-price moment cancellation.
        # After the filter transient decays it remains a sinusoid with a phase
        # shift and amplitude change; a full-cycle correlation is cos(2*pi*k/P).
        sine = [math.sin(2.0*math.pi*t/20.0) for t in range(1000)]
        indicator = master.AutocorrelationHeatmap(length=20, max_lag=40)
        for price in sine:
            column = indicator.update(price)
        ideal = [math.cos(2.0*math.pi*k/20.0) for k in range(41)]
        for actual, expected in zip(column.values, ideal):
            self.assertAlmostEqual(actual, expected, delta=1e-11)
        short = master.AutocorrelationHeatmap(length=2, max_lag=20)
        for index, price in enumerate(sine):
            column = short.update(price)
            if short.primed and index > 300:
                for lag, actual in enumerate(column.values):
                    h = short._history
                    direction = (h[0]-h[1])*(h[lag]-h[lag+1])
                    expected = 1.0 if direction > 0 else -1.0
                    self.assertAlmostEqual(actual, expected, delta=2e-9)

    def test_degenerate_variance_retains_previous_and_zero_start(self):
        indicator = master.AutocorrelationHeatmap(length=3, max_lag=2)
        for _ in range(30):
            result = indicator.update(0.0)
        self.assertEqual(result.values, [0.0]*3)
        # With exactly flat zero input/filter history, the source makes no
        # assignment. Seed distinct old values to isolate its no-Else rule.
        indicator._correlations = [0.25, -0.5, 0.75]
        result = indicator.update(0.0)
        self.assertEqual(result.values, [0.25, -0.5, 0.75])
        self.assertEqual(result.value_min, -0.5)
        self.assertEqual(result.value_max, 0.75)

    def test_snapshots_metadata_and_common_lag_independence(self):
        from datetime import datetime, timezone
        stamp = datetime(2026, 2, 1, tzinfo=timezone.utc)
        wide = master.AutocorrelationHeatmap(length=5, max_lag=99)
        small = master.AutocorrelationHeatmap(length=5, max_lag=32)
        zero = master.AutocorrelationHeatmap(length=5, max_lag=0)
        for price in INPUT_CLOSE:
            column = wide.update(price, stamp)
            smaller = small.update(price)
            zero.update(price)
            # History range alters availability, not shared lag calculations.
            self.assertEqual(wide.state.correlations[:33], small.state.correlations)
            self.assertEqual(wide.state.correlations[0], zero.state.correlations[0])
            self.assertEqual(wide.state.filtered, small.state.filtered)
            self.assertEqual(column.time, stamp)
            self.assertEqual(column.parameter_first, 0.0)
            self.assertEqual(column.parameter_last, 99.0)
            self.assertEqual(column.parameter_resolution, 1.0)
            if not column.is_empty():
                self.assertEqual(column.values[:33], smaller.values)
                old_state = wide.state
                column.values[:] = [1234.0]*100
                self.assertEqual(wide.state, old_state)

    def test_invalid_parameters_and_unprimed_long_window(self):
        for kwargs in ({"length":1}, {"length":True}, {"length":2.5},
                       {"max_lag":-1}, {"max_lag":100}, {"max_lag":True},
                       {"smoothing_period":0.5}, {"smoothing_period":math.nan},
                       {"smoothing_period":math.inf}, {"smoothing_period":True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                master.AutocorrelationHeatmap(**kwargs)
        for period in (1.0, 2.0, 10.5, 252.0):
            indicator = master.AutocorrelationHeatmap(2, period, 0)
            for price in INPUT_CLOSE:
                output = indicator.update(price)
            self.assertFalse(output.is_empty())
        long_window = master.AutocorrelationHeatmap(length=300)
        for price in INPUT_CLOSE:
            self.assertTrue(long_window.update(price).is_empty())
        self.assertFalse(long_window.primed)


if __name__ == "__main__":
    unittest.main()
