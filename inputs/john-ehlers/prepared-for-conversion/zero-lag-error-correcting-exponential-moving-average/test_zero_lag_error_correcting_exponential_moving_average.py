"""Source-equation and five-language fixture checks for the zero-lag master.

The chronological source translation below shares no numerical helpers with
the streaming master. The detached zpano framework is not imported or altered.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "zecema_master", HERE / "zero-lag-error-correcting-exponential-moving-average.py")
ZECEMA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ZECEMA)


def literal_arrays(path):
    # Independent parsing prevents a matching bug in the master's reader
    # from accidentally validating its own serialized output.
    arrays = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            arrays[node.targets[0].id] = [math.nan if isinstance(v, ast.Name) and v.id == "NaN"
                                         else float(ast.literal_eval(v)) for v in node.value.elts]
    return arrays


INPUTS = literal_arrays(HERE / "test_testdata.py")["INPUT_CLOSE"]


def article_batch(prices, length, gain_limit):
    """Chronological translation of the literal 2010 EasyLanguage listing."""
    alpha = 2.0 / (length + 1)
    ema = [0.0] * (len(prices) + 1)
    ec = [0.0] * (len(prices) + 1)
    best_gain = 0.0
    result = []
    for t, price in enumerate(prices, 1):
        ema[t] = alpha * price + (1.0 - alpha) * ema[t - 1]
        least_error = 1_000_000.0
        for integer_gain in range(-gain_limit, gain_limit + 1):
            gain = integer_gain / 10.0
            trial = (alpha * (ema[t] + gain * (price - ec[t - 1]))
                     + (1.0 - alpha) * ec[t - 1])
            error = price - trial
            if abs(error) < least_error:
                least_error = abs(error)
                best_gain = gain
        ec[t] = (alpha * (ema[t] + best_gain * (price - ec[t - 1]))
                 + (1.0 - alpha) * ec[t - 1])
        result.append((ec[t], ema[t], best_gain, least_error))
    return result


class NumericalTests(unittest.TestCase):
    def assert_values(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            if math.isnan(b):
                self.assertTrue(math.isnan(a))
            else:
                self.assertTrue(math.isclose(a, b, rel_tol=2e-12, abs_tol=2e-12), f"{a!r} != {b!r}")

    def test_all_cases_match_independent_article_translation(self):
        for case in ZECEMA.REFERENCE_CASES:
            with self.subTest(parameters=case[:2]):
                stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage(*case[:2])
                expected = article_batch(INPUTS, *case[:2])
                for price, reference in zip(INPUTS, expected):
                    result = stream.update(price)
                    self.assert_values(result, reference[:2])
                    self.assertEqual(stream.best_gain, reference[2])
                    self.assertEqual(stream.least_error, reference[3])

    def test_zero_state_startup_and_first_observation_priming(self):
        stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage()
        self.assertFalse(stream.is_primed)
        self.assertTrue(all(math.isnan(v) for v in stream.output))
        self.assertEqual(stream.alpha, 2.0 / 21.0)
        self.assertNotEqual(stream.alpha, 0.095)
        price = INPUTS[0]
        result = stream.update(price)
        ema = (2.0 / 21.0) * price
        ec = (2.0 / 21.0) * (ema + 5.0 * price)
        self.assertEqual(result.ema, ema)
        self.assertEqual(result.value, ec)
        self.assertEqual(stream.best_gain, 5.0)
        self.assertEqual(stream.warmup_bars, 0)
        self.assertTrue(stream.is_primed)
        self.assertEqual(stream.samples_seen, 1)

    def test_inclusive_integer_endpoints(self):
        for limit in (1, 22, 49, 50):
            stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage(gain_limit=limit)
            stream.update(INPUTS[0])
            # At the first bar these ranges undercorrect, so the optimum is
            # the positive endpoint, including the copied loop's missed +2.2.
            self.assertEqual(stream.best_gain, limit / 10.0)

    def test_exact_tie_selects_negative_endpoint(self):
        stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage(gain_limit=49)
        for _ in range(5):
            result = stream.update(0.0)
            self.assertEqual(result, (0.0, 0.0))
            self.assertEqual(stream.least_error, 0.0)
            self.assertEqual(stream.best_gain, -4.9)

    def test_gain_zero_is_two_cascaded_emas(self):
        stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage(length=20, gain_limit=0)
        alpha, q = 2.0 / 21.0, 1.0 - 2.0 / 21.0
        for t in range(50):
            result = stream.update(1.0 if t == 0 else 0.0)
            self.assertAlmostEqual(result.ema, alpha * q ** t, places=14)
            self.assertAlmostEqual(result.value, (t + 1) * alpha * alpha * q ** t, places=14)
            self.assertEqual(stream.best_gain, 0.0)
        self.assertNotEqual(result.value, result.ema)

    def test_selected_candidate_uses_frozen_previous_ec(self):
        stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage(gain_limit=22)
        for price in INPUTS[:60]:
            previous_ec, previous_ema = stream._ec, stream._ema
            ema = stream.alpha * price + (1.0 - stream.alpha) * previous_ema
            candidates = [(stream.alpha * (ema + (i / 10.0) * (price - previous_ec))
                           + (1.0 - stream.alpha) * previous_ec, i / 10.0)
                          for i in range(-22, 23)]
            winner, gain = min(candidates, key=lambda pair: abs(price - pair[0]))
            result = stream.update(price)
            self.assertEqual(result.value, winner)
            self.assertEqual(stream.best_gain, gain)
            self.assertEqual(result.ema, ema)

    def test_gain_limit_does_not_change_baseline_ema(self):
        streams = [ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage(gain_limit=g)
                   for g in (0, 1, 22, 50, 100)]
        ema = 0.0
        for price in INPUTS:
            ema = (2.0 / 21.0) * price + (1.0 - 2.0 / 21.0) * ema
            for stream in streams:
                self.assertEqual(stream.update(price).ema, ema)

    def test_finite_sentinel_retains_previous_gain(self):
        stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage()
        stream.update(0.0)
        self.assertEqual(stream.best_gain, -5.0)
        # Every trial now has error much larger than 1e6. The source retains
        # the earlier gain instead of picking the best large-error candidate.
        result = stream.update(100_000_000.0)
        self.assertEqual(stream.best_gain, -5.0)
        self.assertEqual(stream.least_error, 1_000_000.0)
        self.assertNotEqual(stream.least_error, abs(100_000_000.0 - result.value))
        self.assertLess(result.value, 0.0)
        expected = article_batch([0.0, 100_000_000.0], 20, 50)[-1]
        self.assert_values(result, expected[:2])

    def test_alpha_one_tracks_price(self):
        stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage(length=1)
        for price in INPUTS:
            self.assertEqual(stream.update(price), (price, price))

    def test_long_length_is_not_a_finite_window_warmup(self):
        stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage(length=252)
        for price in INPUTS:
            self.assertTrue(all(math.isfinite(v) for v in stream.update(price)))
            self.assertTrue(stream.is_primed)

    def test_nan_gap_and_reset(self):
        stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage()
        control = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage()
        for price in INPUTS[:80]:
            self.assertEqual(stream.update(price), control.update(price))
            saved, count, gain = stream.output, stream.samples_seen, stream.best_gain
            self.assertTrue(all(math.isnan(v) for v in stream.update(math.nan)))
            self.assertIs(stream.output, saved)
            self.assertEqual(stream.samples_seen, count)
            self.assertEqual(stream.best_gain, gain)
        parameters = stream.parameters
        stream.reset()
        self.assertFalse(stream.is_primed)
        self.assertEqual(stream.samples_seen, 0)
        self.assertEqual(stream.parameters, parameters)
        fresh = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage()
        for price in INPUTS:
            self.assertEqual(stream.update(price), fresh.update(price))

    def test_invalid_observations_and_overflow_do_not_commit(self):
        stream = ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage()
        stream.update(INPUTS[0])
        for price in (math.inf, -math.inf, None, True, "invalid", 1e308):
            state = (stream.output, stream.samples_seen, stream._ema, stream._ec,
                     stream.best_gain, stream.least_error)
            with self.subTest(price=price), self.assertRaises(ValueError):
                stream.update(price)
            self.assertIs(stream.output, state[0])
            self.assertEqual((stream.samples_seen, stream._ema, stream._ec,
                              stream.best_gain, stream.least_error), state[1:])

    def test_configuration_validation(self):
        for kwargs in ({"length": 0}, {"length": True}, {"length": 20.0},
                       {"length": 10**30}, {"gain_limit": -1}, {"gain_limit": 5.0},
                       {"gain_limit": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                ZECEMA.ZeroLagErrorCorrectingExponentialMovingAverage(**kwargs)


class FixtureTests(unittest.TestCase):
    def assert_exact(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            if math.isnan(b):
                self.assertTrue(math.isnan(a))
            else:
                self.assertEqual(a, b)

    def test_python_expected_arrays(self):
        arrays = literal_arrays(HERE / "test_testdata.py")
        self.assertEqual(len([name for name in arrays if name.startswith("EXPECTED_")]), 32)
        for case in ZECEMA.REFERENCE_CASES:
            reference = article_batch(INPUTS, *case[:2])
            for index, field in enumerate(("EC", "EMA")):
                expected = [float(format(row[index], ".15g")) for row in reference]
                name = f"EXPECTED_L{case.length}_G{case.gain_limit}_{field}"
                self.assert_exact(arrays[name], expected)

    def test_all_cross_language_inputs_expected_values_and_nan_masks(self):
        canonical = literal_arrays(HERE / "test_testdata.py")
        patterns = {
            "testdata_test.go": r"var\s+(\w+)\s*=\s*\[\]float64\{(.*?)\}",
            "testdata.ts": r"export const\s+(\w+):\s*number\[\]\s*=\s*\[(.*?)\];",
            "testdata.rs": r"pub fn\s+(\w+)\(\)\s*->\s*Vec<f64>\s*\{\s*vec!\[(.*?)\]",
            "testdata.zig": r"pub fn\s+(\w+)\(\)\s*\[252\]f64\s*\{\s*return\s*\.\{(.*?)\};",
        }
        suffixes = {"CLOSE": "Input", "HIGH": "High", "LOW": "Low", "OPEN": "Open"}
        for filename, pattern in patterns.items():
            with self.subTest(filename=filename):
                actual = {}
                for name, body in re.findall(pattern, (HERE / filename).read_text(), re.DOTALL):
                    actual[name] = [math.nan if v.strip() in ("math.NaN()", "NaN", "f64::NAN", "nan")
                                    else float(v.strip()) for v in body.split(",") if v.strip()]
                self.assertEqual(len(actual), 36)
                for py_name, values in canonical.items():
                    if py_name.startswith("EXPECTED_"):
                        suffix = py_name[len("EXPECTED_"):]
                        name = ("expected_" + suffix.lower() if filename.endswith(".rs")
                                else "expected" + suffix)
                    else:
                        suffix = suffixes[py_name[len("INPUT_"):]]
                        name = ("test_" + suffix.lower() if filename.endswith(".rs") else "test" + suffix)
                    self.assert_exact(actual[name], values)

    def test_comments_match_in_each_language(self):
        python = (HERE / "test_testdata.py").read_text()
        for filename in ("testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig"):
            text = (HERE / filename).read_text()
            for case in ZECEMA.REFERENCE_CASES:
                parameters = (f"length={case.length}, gain_limit={case.gain_limit}; "
                              "gain_step=0.1; input=INPUT_CLOSE; initialization=zeros")
                self.assertEqual(python.count(f"# {case.what_it_tests}\n# {parameters}\n"), 2)
                header = f"// {case.what_it_tests}\n// {parameters}\n"
                if filename.endswith(".rs"):
                    header = header.replace("\n//", "\n    //").rstrip("\n")
                self.assertEqual(text.count(header), 2)

    def test_regeneration_is_byte_identical(self):
        names = ("test_testdata.py", "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig")
        with tempfile.TemporaryDirectory(prefix="zecema-regeneration-") as directory:
            root = Path(directory)
            for name in names:
                (root / name).write_bytes((HERE / name).read_bytes())
            self.assertEqual(ZECEMA.generate_reference_data(root, INPUTS), 32)
            for name in names:
                self.assertEqual((root / name).read_bytes(), (HERE / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
