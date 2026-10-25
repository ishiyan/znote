"""Behavioral and five-language fixture checks for the EMD master.

Run with python3 -m unittest discover -s . -p 'test_empirical_mode_decomposition.py'.
The independent chronological calculation below translates the source equations
without sharing the streaming implementation's state or averaging helpers.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("emd_master", HERE / "empirical-mode-decomposition.py")
EMD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EMD)


def literal_arrays(path):
    # Parse the canonical fixture without executing it or using the master's
    # parser, so a serialization/parser bug cannot validate itself.
    result = {}
    for node in ast.parse(path.read_text()).body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.List):
            continue
        name = node.targets[0].id
        result[name] = [math.nan if isinstance(v, ast.Name) and v.id == "NaN"
                        else float(ast.literal_eval(v)) for v in node.value.elts]
    return result


INPUTS = literal_arrays(HERE / "test_testdata.py")["INPUT_CLOSE"]


def article_batch(prices, period, delta, fraction):
    """Chronological batch translation, with explicit source zero seeds.

    Degree-to-radian conversion is written differently from the master to
    independently check the EasyLanguage angle interpretation. A numerical
    tolerance accommodates the last-bit differences in angle construction.
    """
    beta = math.cos(math.radians(360.0 / period))
    gamma = 1.0 / math.cos(math.radians(720.0 * delta / period))
    alpha = gamma - math.sqrt(gamma * gamma - 1.0)
    bp = [0.0] * len(prices)
    peaks = [0.0] * len(prices)
    valleys = [0.0] * len(prices)
    for t in range(2, len(prices)):
        bp[t] = (0.5 * (1.0 - alpha) * (prices[t] - prices[t - 2])
                 + beta * (1.0 + alpha) * bp[t - 1] - alpha * bp[t - 2])
        peaks[t] = peaks[t - 1]
        valleys[t] = valleys[t - 1]
        if bp[t - 1] > bp[t] and bp[t - 1] > bp[t - 2]:
            peaks[t] = bp[t - 1]
        if bp[t - 1] < bp[t] and bp[t - 1] < bp[t - 2]:
            valleys[t] = bp[t - 1]
    result = []
    for t in range(len(prices)):
        trend = (sum(bp[t - j] for j in range(2 * period)) / (2 * period)
                 if t + 1 >= 2 * period else math.nan)
        ap = (sum(peaks[t - j] for j in range(50)) / 50.0
              if t + 1 >= 50 else math.nan)
        av = (sum(valleys[t - j] for j in range(50)) / 50.0
              if t + 1 >= 50 else math.nan)
        result.append((trend, ap, fraction * ap, av, fraction * av))
    return result


class NumericalTests(unittest.TestCase):
    def assert_values(self, actual, expected, tolerance=2e-12):
        self.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            if math.isnan(b):
                self.assertTrue(math.isnan(a))
            else:
                self.assertTrue(math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance),
                                f"{a!r} != {b!r}")

    def test_all_cases_match_independent_article_translation(self):
        for case in EMD.REFERENCE_CASES:
            with self.subTest(case=case[:3]):
                stream = EMD.EmpiricalModeDecomposition(*case[:3])
                actual = [stream.update(price) for price in INPUTS]
                expected = article_batch(INPUTS, *case[:3])
                for a, b in zip(actual, expected):
                    self.assert_values(a, b)

    def test_output_names_and_independent_priming(self):
        self.assertEqual(EMD.OUTPUT_FIELDS,
                         ("Trend", "AvgPeak", "FractalAbgPeak", "AvgValley", "FractalAvhValley"))
        for period in (3, 20, 25, 40, 126, 127):
            with self.subTest(period=period):
                stream = EMD.EmpiricalModeDecomposition(period, 0.25, 0.1)
                for t, price in enumerate(INPUTS):
                    output = stream.update(price)
                    self.assertEqual(math.isnan(output.Trend), t < 2 * period - 1)
                    for value in output[1:]:
                        self.assertEqual(math.isnan(value), t < 49)
                    self.assertEqual(stream.is_primed, t >= max(2 * period, 50) - 1)

    def test_zero_startup_and_real_two_bar_price_lag(self):
        stream = EMD.EmpiricalModeDecomposition()
        stream.update(100.0)
        stream.update(200.0)
        self.assertEqual(stream._bp, [0.0, 0.0])
        stream.update(101.0)
        self.assertEqual(stream._bp[0], stream._gain * (101.0 - 100.0))
        self.assertEqual(stream._peak, 0.0)
        self.assertEqual(stream._valley, 0.0)

    def test_extrema_require_confirmation_and_hold_on_flat_plateau(self):
        # Drive controlled internal BP histories through one recurrence step.
        # This isolates strict comparison/confirmation behavior from the
        # filter frequency response and intentionally inspects internal state.
        stream = EMD.EmpiricalModeDecomposition()
        stream.update(0.0)
        stream.update(0.0)
        stream._bp = [2.0, 1.0]
        # Select a current price that creates a BP below the previous peak.
        price = (0.0 - stream._feedback * 2.0 + stream._alpha) / stream._gain
        stream.update(price)
        self.assertEqual(stream._peak, 2.0)
        self.assertEqual(stream._peak_history[0], 2.0)
        # If the previous two BP values are equal, neither strict test holds.
        stream._bp = [2.0, 2.0]
        old_peak, old_valley = stream._peak, stream._valley
        stream.update(0.0)
        self.assertEqual((stream._peak, stream._valley), (old_peak, old_valley))

    def test_held_extrema_average_counts_bars_not_events(self):
        stream = EMD.EmpiricalModeDecomposition()
        for _ in range(50):
            stream.update(0.0)
        # A held negative peak is valid; it is neither clamped nor omitted.
        stream._peak = -2.0
        first = stream.update(0.0)
        second = stream.update(0.0)
        self.assertEqual(first.AvgPeak, -2.0 / 50.0)
        self.assertEqual(second.AvgPeak, -4.0 / 50.0)

    def test_fraction_changes_only_thresholds(self):
        streams = [EMD.EmpiricalModeDecomposition(fraction=f) for f in (0.0, 0.1, 1.0)]
        for t, price in enumerate(INPUTS):
            zero, default, unit = [stream.update(price) for stream in streams]
            for field in (0, 1, 3):
                self.assert_values([zero[field], unit[field]], [default[field], default[field]])
            if t >= 49:
                self.assertEqual(zero.FractalAbgPeak, 0.0)
                self.assertEqual(zero.FractalAvhValley, 0.0)
                self.assertEqual(unit.FractalAbgPeak, unit.AvgPeak)
                self.assertEqual(unit.FractalAvhValley, unit.AvgValley)
                self.assertEqual(default.FractalAbgPeak, 0.1 * default.AvgPeak)
                self.assertEqual(default.FractalAvhValley, 0.1 * default.AvgValley)

    def test_constant_input_has_no_startup_impulse(self):
        stream = EMD.EmpiricalModeDecomposition()
        for t in range(100):
            result = stream.update(123.0)
            self.assertEqual(stream._bp[0], 0.0)
            for value in result:
                if not math.isnan(value):
                    self.assertEqual(value, 0.0)

    def test_ramp_limit_and_tuned_sine_rejection(self):
        slope = 0.25
        ramp = EMD.EmpiricalModeDecomposition()
        sine = EMD.EmpiricalModeDecomposition()
        for t in range(1200):
            ramp_result = ramp.update(100.0 + slope * t)
            wave = math.sin(2.0 * math.pi * t / 20.0)
            sine_result = sine.update(100.0 + wave)
        alpha, beta = ramp._alpha, ramp._beta
        limit = (1.0 - alpha) * slope / ((1.0 + alpha) * (1.0 - beta))
        self.assertAlmostEqual(ramp_result.Trend, limit, places=11)
        self.assertAlmostEqual(sine._bp[0], wave, places=11)
        self.assertAlmostEqual(sine_result.Trend, 0.0, places=11)

    def test_missing_input_and_reset(self):
        actual = EMD.EmpiricalModeDecomposition()
        control = EMD.EmpiricalModeDecomposition()
        for price in INPUTS[:80]:
            expected = control.update(price)
            self.assert_values(actual.update(price), expected)
            saved = actual.output
            count = actual.samples_seen
            self.assertTrue(all(math.isnan(v) for v in actual.update(math.nan)))
            self.assertIs(actual.output, saved)
            self.assertEqual(actual.samples_seen, count)
        parameters = actual.parameters
        actual.reset()
        self.assertEqual(actual.samples_seen, 0)
        self.assertFalse(actual.is_primed)
        self.assertEqual(actual.parameters, parameters)
        fresh = EMD.EmpiricalModeDecomposition()
        for price in INPUTS:
            self.assert_values(actual.update(price), fresh.update(price))

    def test_invalid_inputs_and_arithmetic_failure_preserve_state(self):
        stream = EMD.EmpiricalModeDecomposition()
        stream.update(1.0)
        stream.update(1.0)
        for bad in (math.inf, -math.inf, True, None, "invalid", -1e308):
            if bad == -1e308:
                # Finite but adversarial history makes the price difference
                # overflow; this must not poison the following update.
                stream._prices[1] = 1e308
            saved = (stream.samples_seen, list(stream._prices), list(stream._bp), stream.output)
            with self.assertRaises(ValueError):
                stream.update(bad)
            self.assertEqual(stream.samples_seen, saved[0])
            self.assertEqual(stream._prices, saved[1])
            self.assertEqual(stream._bp, saved[2])
            self.assertIs(stream.output, saved[3])

    def test_configuration_validation(self):
        for kwargs in ({"period": 2}, {"period": 20.0}, {"period": True},
                       {"delta": 0.0}, {"delta": 2.5}, {"delta": math.nan},
                       {"delta": 1e-30}, {"fraction": -0.1}, {"fraction": 1.1},
                       {"fraction": math.inf}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                EMD.EmpiricalModeDecomposition(**kwargs)


class FixtureTests(unittest.TestCase):
    def assert_exact(self, a, b):
        self.assertEqual(len(a), len(b))
        for x, y in zip(a, b):
            if math.isnan(y):
                self.assertTrue(math.isnan(x))
            else:
                self.assertEqual(x, y)

    def test_python_arrays_and_masks(self):
        arrays = literal_arrays(HERE / "test_testdata.py")
        names = {name for name in arrays if name.startswith("EXPECTED_")}
        self.assertEqual(len(names), 80)
        for case in EMD.REFERENCE_CASES:
            stream = EMD.EmpiricalModeDecomposition(*case[:3])
            result = [stream.update(price) for price in INPUTS]
            suffix = (f"P{case.period}_D{format(case.delta, '.15g').replace('.', '_')}"
                      f"_F{format(case.fraction, '.15g').replace('.', '_')}")
            for index, field in enumerate(EMD.OUTPUT_FIELDS):
                name = f"EXPECTED_{suffix}_{field.upper()}"
                expected = [math.nan if math.isnan(row[index])
                            else float(format(row[index], ".15g")) for row in result]
                self.assert_exact(arrays[name], expected)

    def test_input_and_expected_values_in_all_other_languages(self):
        canonical = literal_arrays(HERE / "test_testdata.py")
        patterns = {
            "testdata_test.go": r"var\s+(\w+)\s*=\s*\[\]float64\{(.*?)\}",
            "testdata.ts": r"export const\s+(\w+):\s*number\[\]\s*=\s*\[(.*?)\];",
            "testdata.rs": r"pub fn\s+(\w+)\(\)\s*->\s*Vec<f64>\s*\{\s*vec!\[(.*?)\]",
            "testdata.zig": r"pub fn\s+(\w+)\(\)\s*\[252\]f64\s*\{\s*return\s*\.\{(.*?)\};",
        }
        input_suffixes = {"CLOSE": "Input", "HIGH": "High", "LOW": "Low", "OPEN": "Open"}
        for filename, pattern in patterns.items():
            with self.subTest(filename=filename):
                text = (HERE / filename).read_text()
                actual = {}
                for name, body in re.findall(pattern, text, re.DOTALL):
                    actual[name] = [math.nan if v.strip() in ("math.NaN()", "NaN", "f64::NAN", "nan")
                                    else float(v.strip()) for v in body.split(",") if v.strip()]
                self.assertEqual(len(actual), 84)
                for py_name, values in canonical.items():
                    if py_name.startswith("EXPECTED_"):
                        suffix = py_name[len("EXPECTED_"):]
                        name = ("expected_" + suffix.lower() if filename.endswith(".rs")
                                else "expected" + suffix)
                    else:
                        suffix = input_suffixes[py_name[len("INPUT_"):]]
                        name = ("test_" + suffix.lower() if filename.endswith(".rs")
                                else "test" + suffix)
                    self.assert_exact(actual[name], values)

    def test_two_comments_match_in_each_export(self):
        python = (HERE / "test_testdata.py").read_text()
        for filename in ("testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig"):
            text = (HERE / filename).read_text()
            for case in EMD.REFERENCE_CASES:
                parameters = (f"period={case.period}, delta={case.delta}, fraction={case.fraction}; "
                              "peak_average_length=50; input=INPUT_CLOSE")
                self.assertEqual(python.count(f"# {case.what_it_tests}\n# {parameters}\n"), 5)
                header = f"// {case.what_it_tests}\n// {parameters}\n"
                if filename.endswith(".rs"):
                    header = header.replace("\n//", "\n    //").rstrip("\n")
                self.assertEqual(text.count(header), 5)

    def test_regeneration_is_byte_identical_and_preserves_inputs(self):
        names = ("test_testdata.py", "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig")
        with tempfile.TemporaryDirectory(prefix="emd-regeneration-") as directory:
            root = Path(directory)
            for name in names:
                (root / name).write_bytes((HERE / name).read_bytes())
            self.assertEqual(EMD.generate_reference_data(root, INPUTS), 80)
            for name in names:
                self.assertEqual((root / name).read_bytes(), (HERE / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
