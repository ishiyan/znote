"""Independent batch-source oracle and behavior checks for this research master.

Run with: python3 -m unittest discover -s . -p 'test_griffiths*.py'
No NumPy, external indicator package or expected-data fixture is the oracle.
"""

import importlib.util
import math
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("griffiths_master", HERE / "griffiths-predictor.py")
master = importlib.util.module_from_spec(spec)
spec.loader.exec_module(master)
FIXTURE_ARRAYS = master._load_python_arrays(HERE / "test_testdata.py")
INPUT_CLOSE = FIXTURE_ARRAYS["INPUT_CLOSE"]


def batch_source(closes, lower, upper, length, kind, horizon=2, mode="article"):
    """Translate the complete source into full histories, unlike streaming code.

    One-based coefficient and XX arrays deliberately preserve the zero final
    regressor. Source recurrences run even while public output is masked. This
    oracle never calls the master filters, adaptation, spectrum or serializer.
    """
    n = len(closes)
    hp = [0.0] * n
    lp = [0.0] * n
    signal = [0.0] * n
    coeff = [0.0] * (length + 1)
    power = [0.0] * (upper + 1)
    peak, cycle = 0.1, 0.0
    result = []
    a_h = math.exp(-math.sqrt(2.0) * math.pi / upper)
    b_h = 2.0 * a_h * math.cos(math.sqrt(2.0) * math.pi / upper)
    c_h = -a_h * a_h
    gain_h = (1.0 + b_h - c_h) / 4.0
    a_l = math.exp(-math.sqrt(2.0) * math.pi / lower)
    b_l = 2.0 * a_l * math.cos(math.sqrt(2.0) * math.pi / lower)
    c_l = -a_l * a_l
    gain_l = 1.0 - b_l - c_l
    for t in range(n):
        if t >= 3:
            hp[t] = (gain_h * (closes[t] - 2.0 * closes[t-1] + closes[t-2])
                     + b_h * hp[t-1] + c_h * hp[t-2])
            lp[t] = (gain_l * (hp[t] + hp[t-1]) / 2.0
                     + b_l * lp[t-1] + c_l * lp[t-2])
        peak = 0.991 * peak
        if abs(lp[t]) > peak:
            peak = abs(lp[t])
        signal[t] = lp[t] / peak if peak != 0.0 else (signal[t-1] if t else 0.0)
        xx = [0.0] * (length + 1)
        for count in range(1, length + 1):
            index = t - (length - count)
            xx[count] = signal[index] if index >= 0 else 0.0
        xbar = 0.0
        for count in range(1, length + 1):
            xbar += xx[length-count] * coeff[count]
        for count in range(1, length + 1):
            coeff[count] = coeff[count] + (1.0 / length) * (xx[length] - xbar) * xx[length-count]
        if kind == "predictor":
            prediction = 0.0
            for advance in range(1, horizon + 1):
                prediction = 0.0
                for count in range(1, length + 1):
                    prediction += xx[length+1-count] * coeff[count]
                if mode == "tradestation":
                    for count in range(advance, length-advance+1):
                        xx[count] = xx[count+1]
                for count in range(1, length):
                    xx[count] = xx[count+1]
                xx[length] = prediction
            public = (signal[t], prediction)
        else:
            for period in range(lower, upper + 1):
                real = imaginary = 0.0
                for count in range(1, length + 1):
                    real += coeff[count] * math.cos(2.0 * math.pi * count / period)
                    imaginary += coeff[count] * math.sin(2.0 * math.pi * count / period)
                denom = (1.0-real) * (1.0-real) + imaginary * imaginary
                power[period] = (0.1 / denom + 0.9 * power[period]
                                 if kind == "spectrum" else 0.1 / denom)
            maximum, selected = 0.0, lower
            for period in range(lower, upper + 1):
                if power[period] > maximum:
                    maximum, selected = power[period], period
            if kind == "spectrum":
                for period in range(lower, upper + 1):
                    if maximum != 0.0:
                        power[period] = power[period] / maximum
                public = (power[lower:upper+1], float(selected))
            else:
                candidate = float(selected)
                if candidate > cycle + 2.0:
                    candidate = cycle + 2.0
                if candidate < cycle - 2.0:
                    candidate = cycle - 2.0
                cycle = candidate
                public = cycle
        if t + 1 < max(4, length):
            public = ((math.nan, math.nan) if kind == "predictor" else
                      ([], math.nan) if kind == "spectrum" else math.nan)
        result.append(public)
    return result


def flatten(output):
    if master.KIND == "predictor":
        return list(output)
    if master.KIND == "spectrum":
        return output.heatmap.values + [output.instantaneous_period]
    return [output]


class TestGriffithsMaster(unittest.TestCase):
    def assert_numbers(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            if math.isnan(b):
                self.assertTrue(math.isnan(a))
            else:
                self.assertTrue(math.isclose(a, b, rel_tol=2e-13, abs_tol=2e-13), (a, b))

    def test_every_confirmed_case_against_source_and_expected_fixtures(self):
        self.assertEqual(len(INPUT_CLOSE), 252)
        self.assertLessEqual(len(master.REFERENCE_CASES), 64)
        components = (("SIGNAL", "PRED") if master.KIND == "predictor" else
                      ("IP", "HEATMAP", "MIN", "MAX") if master.KIND == "spectrum" else ("DC",))
        expected_names = {"EXPECTED_" + master._case_suffix(case) + "_" + component
                          for case in master.REFERENCE_CASES for component in components}
        self.assertEqual({n for n in FIXTURE_ARRAYS if n.startswith("EXPECTED_")}, expected_names)
        for case in master.REFERENCE_CASES:
            with self.subTest(case=case):
                indicator = master._new_indicator(case)
                expected = batch_source(INPUT_CLOSE, case.lower_bound, case.upper_bound,
                                        case.length, master.KIND, case.bars_forward,
                                        case.predictor_mode)
                for name in expected_names:
                    self.assertEqual(len(FIXTURE_ARRAYS[name]), 252)
                for row, (price, reference) in enumerate(zip(INPUT_CLOSE, expected)):
                    output = indicator.update(price)
                    flat_reference = (reference[0] + [reference[1]] if master.KIND == "spectrum"
                                      else list(reference) if master.KIND == "predictor" else [reference])
                    self.assert_numbers(flatten(output), flat_reference)
                    prefix = "EXPECTED_" + master._case_suffix(case) + "_"
                    if master.KIND == "predictor":
                        actual_components = {"SIGNAL": output.signal, "PRED": output.prediction}
                    elif master.KIND == "spectrum":
                        bins = case.upper_bound - case.lower_bound + 1
                        actual_components = {
                            "IP": output.instantaneous_period,
                            "HEATMAP": output.heatmap.values if not output.heatmap.is_empty()
                                       else [math.nan] * bins,
                            "MIN": output.heatmap.value_min, "MAX": output.heatmap.value_max,
                        }
                    else:
                        actual_components = {"DC": output}
                    for component, raw in actual_components.items():
                        saved = FIXTURE_ARRAYS[prefix + component][row]
                        raw_values = raw if isinstance(raw, list) else [raw]
                        saved_values = saved if isinstance(saved, list) else [saved]
                        self.assertEqual(len(raw_values), len(saved_values))
                        for original, literal in zip(raw_values, saved_values):
                            if math.isnan(original):
                                self.assertTrue(math.isnan(literal))
                            else:
                                self.assertEqual(literal, float(format(original, ".15g")))
                self.assertEqual(indicator.state.coefficients[-1], 0.0)
                self.assertEqual(indicator.state.coefficients[0], 0.0)

    def test_nan_skip_infinity_rejection_and_reset(self):
        subject, clean = master.MASTER_CLASS(), master.MASTER_CLASS()
        for value in INPUT_CLOSE[:80]:
            before = subject.state
            unavailable = subject.update(math.nan)
            self.assertEqual(subject.state, before)
            self.assertTrue(all(math.isnan(v) for v in flatten(unavailable)))
            self.assert_numbers(flatten(subject.update(value)), flatten(clean.update(value)))
        before = subject.state
        for value in (math.inf, -math.inf):
            with self.assertRaises(ValueError):
                subject.update(value)
            self.assertEqual(subject.state, before)
        subject.reset()
        fresh = master.MASTER_CLASS()
        self.assertEqual(subject.state, fresh.state)
        for value in INPUT_CLOSE:
            self.assert_numbers(flatten(subject.update(value)), flatten(fresh.update(value)))

    def test_priming_and_zero_signal_ties(self):
        indicator = master.MASTER_CLASS(18, 40, 2)
        for index in range(1, 30):
            output = indicator.update(100.0)
            self.assertEqual(indicator.state.signal, 0.0)
            self.assertEqual(indicator.primed, index >= 4)
            if index < 4:
                self.assertTrue(all(math.isnan(v) for v in flatten(output)))
            elif master.KIND == "spectrum":
                self.assertEqual(output.instantaneous_period, 18.0)
                self.assertEqual(output.heatmap.values, [1.0] * 23)
            elif master.KIND == "dominant-cycle":
                self.assertEqual(output, float(min(2 * index, 18)))
            else:
                self.assertEqual(output.signal, 0.0)
                self.assertEqual(output.prediction, 0.0)

    def test_boundary_and_synthetic_cycle(self):
        upper = 99 if master.KIND == "spectrum" else 200
        signal = [100.0 + math.sin(2.0 * math.pi * t / 30.0)
                  + 0.2 * math.sin(2.0 * math.pi * t / 13.0) for t in range(400)]
        case = master.ReferenceCase(9, upper, upper, 3, "article", "Boundary sweep")
        indicator = master._new_indicator(case)
        expected = batch_source(signal, 9, upper, upper, master.KIND, 3)
        for price, reference in zip(signal, expected):
            flat_reference = (reference[0] + [reference[1]] if master.KIND == "spectrum"
                              else list(reference) if master.KIND == "predictor" else [reference])
            self.assert_numbers(flatten(indicator.update(price)), flat_reference)

    def test_invalid_configuration(self):
        for kwargs in ({"lower_bound": True}, {"lower_bound": 2},
                       {"lower_bound": 40, "upper_bound": 40}, {"length": 1},
                       {"length": 2.5}, {"upper_bound": 201}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                master.MASTER_CLASS(**kwargs)
        if master.KIND == "predictor":
            for kwargs in ({"bars_forward": 0}, {"bars_forward": True},
                           {"predictor_mode": "unknown"}):
                with self.assertRaises(ValueError):
                    master.MASTER_CLASS(**kwargs)

    def test_output_specific_behavior(self):
        if master.KIND == "spectrum":
            from datetime import datetime, timezone
            stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
            subject, clean = master.MASTER_CLASS(), master.MASTER_CLASS()
            for value in INPUT_CLOSE[:100]:
                output = subject.update(value, stamp)
                reference = clean.update(value)
                self.assertEqual(output.heatmap.time, stamp)
                if not output.heatmap.is_empty():
                    self.assertEqual(output.heatmap.parameter_first, 10.0)
                    self.assertEqual(output.heatmap.parameter_last, 40.0)
                    self.assertEqual(output.heatmap.parameter_resolution, 1.0)
                    self.assertEqual(output.heatmap.value_min, min(output.heatmap.values))
                    self.assertEqual(output.heatmap.value_max, 1.0)
                    self.assertEqual(output.instantaneous_period,
                                     10.0 + output.heatmap.values.index(1.0))
                    output.heatmap.values[:] = [1234.0] * len(output.heatmap.values)
                # Internal normalized feedback must be unaffected by caller edits.
                self.assertEqual(subject._power, clean._power)
            self.assert_numbers(flatten(subject.update(INPUT_CLOSE[100])),
                                flatten(clean.update(INPUT_CLOSE[100])))
        elif master.KIND == "predictor":
            one_a = master.MASTER_CLASS(bars_forward=1)
            one_t = master.MASTER_CLASS(bars_forward=1, predictor_mode="tradestation")
            longer = master.MASTER_CLASS(bars_forward=5)
            alternate = master.MASTER_CLASS(bars_forward=5, predictor_mode="tradestation")
            diverged = False
            for price in INPUT_CLOSE:
                self.assert_numbers(flatten(one_a.update(price)), flatten(one_t.update(price)))
                a, b = longer.update(price), alternate.update(price)
                # Forecast horizon and shift mode cannot feed synthetic data back.
                self.assertEqual(one_a.state, one_t.state)
                self.assertEqual(one_a.state, longer.state)
                self.assertEqual(longer.state, alternate.state)
                if longer.primed:
                    diverged = diverged or abs(a.prediction - b.prediction) > 1e-8
            self.assertTrue(diverged)
        else:
            indicator = master.MASTER_CLASS()
            previous = 0.0
            for price in INPUT_CLOSE:
                indicator.update(price)
                self.assertLessEqual(abs(indicator._cycle - previous), 2.0)
                previous = indicator._cycle


if __name__ == "__main__":
    unittest.main()
