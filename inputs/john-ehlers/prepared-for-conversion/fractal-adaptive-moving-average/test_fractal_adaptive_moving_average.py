"""Independent source-equation and five-language fixture checks for FRAMA.

Run with python3 -m unittest discover -s . -p 'test_fractal_adaptive_moving_average.py'.
The chronological reference below shares no numerical helpers with the master.
The copied zpano framework is neither imported nor modified by these tests.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("frama_master", HERE / "fractal-adaptive-moving-average.py")
FRAMA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FRAMA)


def literal_arrays(path):
    # Independent literal reader, so the master's serializer/parser cannot
    # accidentally validate a matching mistake in its own parser.
    result = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            result[node.targets[0].id] = [math.nan if isinstance(v, ast.Name) and v.id == "NaN"
                                         else float(ast.literal_eval(v)) for v in node.value.elts]
    return result


INPUTS = literal_arrays(HERE / "test_testdata.py")["INPUT_CLOSE"]


def article_batch(prices, length, slowest=0.01, coefficient_mode=0, highs=None, lows=None):
    """Chronological translation of the 2005 guarded ranges and EMA.

    Defaults reproduce the literal article. coefficient_mode=1 replaces its
    rounded exponential scale with log(slowest), the full-precision endpoint
    mapping requested for the new master. No dimension clamp is introduced.
    """
    highs = prices if highs is None else highs
    lows = prices if lows is None else lows
    half = length // 2
    scale = math.log(slowest) if coefficient_mode == 1 else -4.6
    dim = 0.0
    value = 0.0
    result = []
    for t, price in enumerate(prices):
        if t + 1 >= length:
            recent = range(t - half + 1, t + 1)
            older = range(t - length + 1, t - half + 1)
            whole = range(t - length + 1, t + 1)
            n1 = (max(highs[j] for j in recent) - min(lows[j] for j in recent)) / half
            n2 = (max(highs[j] for j in older) - min(lows[j] for j in older)) / half
            n3 = (max(highs[j] for j in whole) - min(lows[j] for j in whole)) / length
            if n1 > 0 and n2 > 0 and n3 > 0:
                dim = (math.log(n1 + n2) - math.log(n3)) / math.log(2.0)
            alpha = math.exp(scale * (dim - 1.0))
            alpha = min(1.0, max(slowest, alpha))
            value = alpha * price + (1.0 - alpha) * value
        # One-based CurrentBar < N+1 forces the first N prices to pass through.
        if t + 1 <= length:
            value = price
        result.append((value, dim) if t + 1 >= length else (math.nan, math.nan))
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

    def test_all_cases_match_independent_source_equations(self):
        for case in FRAMA.REFERENCE_CASES:
            with self.subTest(parameters=case[:3]):
                stream = FRAMA.FractalAdaptiveMovingAverage(*case[:3])
                actual = [stream.update(price) for price in INPUTS]
                expected = article_batch(INPUTS, *case[:3])
                for a, b in zip(actual, expected):
                    self.assert_values(a, b)

    def test_literal_article_bar_ranges_match_independent_source(self):
        fixtures = literal_arrays(HERE / "test_testdata.py")
        highs, lows = fixtures["INPUT_HIGH"], fixtures["INPUT_LOW"]
        midpoints = [(high + low) / 2.0 for high, low in zip(highs, lows)]
        stream = FRAMA.FractalAdaptiveMovingAverage(coefficient_mode=0)
        actual = [stream.update(price, high, low) for price, high, low in zip(midpoints, highs, lows)]
        expected = article_batch(midpoints, 16, highs=highs, lows=lows)
        for a, b in zip(actual, expected):
            self.assert_values(a, b)

    def test_priming_final_price_seed_and_first_adaptive_update(self):
        stream = FRAMA.FractalAdaptiveMovingAverage(length=16)
        for t, price in enumerate(INPUTS):
            previous = stream._value
            output = stream.update(price)
            self.assertEqual(stream.samples_seen, t + 1)
            self.assertEqual(stream.is_primed, t >= 15)
            self.assertEqual(stream.warmup_bars, 15)
            self.assertEqual(math.isnan(output.value), t < 15)
            self.assertEqual(math.isnan(output.fractal_dimension), t < 15)
            if t == 15:
                self.assertEqual(output.value, price)
            if t == 16:
                self.assertEqual(output.value, stream.alpha * price + (1.0 - stream.alpha) * previous)

    def test_long_lookback_priming_boundaries(self):
        for length, finite_count in ((128, 125), (250, 3), (252, 1), (254, 0)):
            stream = FRAMA.FractalAdaptiveMovingAverage(length=length)
            outputs = [stream.update(price) for price in INPUTS]
            self.assertEqual(sum(math.isfinite(row.value) for row in outputs), finite_count)
            self.assertEqual(sum(math.isfinite(row.fractal_dimension) for row in outputs), finite_count)
            if length == 252:
                self.assertEqual(outputs[-1].value, INPUTS[-1])

    def test_raw_dimension_of_ramp_is_below_one(self):
        expected = math.log2(28.0 / 15.0)
        for offset in (100.0, 0.0, -100.0):
            stream = FRAMA.FractalAdaptiveMovingAverage(length=16)
            for t in range(40):
                output = stream.update(offset + t)
                if t >= 15:
                    self.assertAlmostEqual(output.fractal_dimension, expected, places=13)
                    self.assertLess(output.fractal_dimension, 1.0)
                    self.assertEqual(stream.alpha, 1.0)
                    self.assertEqual(output.value, offset + t)

    def test_gap_dimension_is_not_clamped_or_exponentiated_unsafely(self):
        stream = FRAMA.FractalAdaptiveMovingAverage(length=4)
        for price in (0.0, 1.0, 100.0, 101.0):
            output = stream.update(price)
        self.assertAlmostEqual(output.fractal_dimension, math.log2(4.0 / 101.0))
        self.assertLess(output.fractal_dimension, 0.0)
        self.assertEqual(stream.alpha, 1.0)
        self.assertEqual(output.value, 101.0)

    def test_constant_and_minimum_length_guard(self):
        for level in (-123.0, 0.0, 123.0):
            stream = FRAMA.FractalAdaptiveMovingAverage(length=4)
            for _ in range(20):
                output = stream.update(level)
                if stream.is_primed:
                    self.assertEqual(output.value, level)
                    self.assertEqual(output.fractal_dimension, 0.0)
        stream = FRAMA.FractalAdaptiveMovingAverage(length=2)
        for price in INPUTS:
            output = stream.update(price)
            if stream.is_primed:
                self.assertEqual(output.fractal_dimension, 0.0)
                self.assertEqual(output.value, price)

    def test_invalid_half_boxes_hold_previous_dimension(self):
        stream = FRAMA.FractalAdaptiveMovingAverage(length=4)
        for price in (0.0, 1.0, 0.0, 1.0):
            stream.update(price)
        self.assertEqual(stream.fractal_dimension, 2.0)
        stream.update(1.0)  # Recent half is flat, although older half is not.
        self.assertEqual(stream.fractal_dimension, 2.0)
        for _ in range(10):
            stream.update(1.0)
            self.assertEqual(stream.fractal_dimension, 2.0)

    def test_alpha_endpoints_and_full_precision_difference(self):
        precise = FRAMA.FractalAdaptiveMovingAverage(length=4)
        article = FRAMA.FractalAdaptiveMovingAverage(length=4, coefficient_mode=0)
        for _ in range(5):
            # Constant midpoints with nonzero bar ranges give exactly D=2.
            precise.update(1.0, 2.0, 0.0)
            article.update(1.0, 2.0, 0.0)
        self.assertEqual(precise.fractal_dimension, 2.0)
        self.assertEqual(article.fractal_dimension, 2.0)
        self.assertAlmostEqual(precise.alpha, 0.01, places=15)
        self.assertEqual(article.alpha, math.exp(-4.6))
        self.assertGreater(article.alpha, precise.alpha)
        unit = FRAMA.FractalAdaptiveMovingAverage(slowest_smoothing_factor=1.0)
        for price in INPUTS:
            output = unit.update(price)
            if unit.is_primed:
                self.assertEqual(output.value, price)
                self.assertEqual(unit.alpha, 1.0)

    def test_scalar_matches_explicit_equal_high_low(self):
        scalar = FRAMA.FractalAdaptiveMovingAverage()
        bars = FRAMA.FractalAdaptiveMovingAverage()
        for price in INPUTS:
            self.assert_values(scalar.update(price), bars.update(price, price, price))

    def test_affine_invariance_including_negative_price_levels(self):
        original = FRAMA.FractalAdaptiveMovingAverage()
        transformed = FRAMA.FractalAdaptiveMovingAverage()
        for price in INPUTS:
            a = original.update(price)
            b = transformed.update(3.0 * price - 1000.0)
            if original.is_primed:
                self.assertAlmostEqual(a.fractal_dimension, b.fractal_dimension, places=11)
                self.assertAlmostEqual(3.0 * a.value - 1000.0, b.value, places=10)

    def test_nan_gap_and_reset(self):
        stream = FRAMA.FractalAdaptiveMovingAverage()
        control = FRAMA.FractalAdaptiveMovingAverage()
        for price in INPUTS[:80]:
            self.assert_values(stream.update(price), control.update(price))
            count, saved = stream.samples_seen, stream.output
            self.assertTrue(all(math.isnan(v) for v in stream.update(math.nan)))
            self.assertTrue(all(math.isnan(v) for v in stream.update(price, math.nan, price)))
            self.assertEqual(stream.samples_seen, count)
            self.assertIs(stream.output, saved)
        parameters = stream.parameters
        stream.reset()
        self.assertEqual(stream.parameters, parameters)
        self.assertEqual(stream.samples_seen, 0)
        self.assertFalse(stream.is_primed)
        fresh = FRAMA.FractalAdaptiveMovingAverage()
        for price in INPUTS:
            self.assert_values(stream.update(price), fresh.update(price))

    def test_invalid_observations_preserve_state(self):
        stream = FRAMA.FractalAdaptiveMovingAverage(length=2)
        stream.update(0.0)
        for args in ((math.inf,), (True,), (None,), ("invalid",),
                     (1.0, 2.0), (1.0, 0.0, 2.0), (1.0, math.inf, 0.0),
                     (0.0, 1e308, -1e308)):
            saved = (stream.samples_seen, stream.output, list(stream._highs), list(stream._lows))
            with self.subTest(args=args), self.assertRaises(ValueError):
                stream.update(*args)
            self.assertEqual(stream.samples_seen, saved[0])
            self.assertIs(stream.output, saved[1])
            self.assertEqual(stream._highs, saved[2])
            self.assertEqual(stream._lows, saved[3])

    def test_configuration_validation(self):
        for kwargs in ({"length": 1}, {"length": 17}, {"length": 16.0}, {"length": True},
                       {"slowest_smoothing_factor": 0.0}, {"slowest_smoothing_factor": -0.1},
                       {"slowest_smoothing_factor": 1.1}, {"slowest_smoothing_factor": math.nan},
                       {"slowest_smoothing_factor": math.inf}, {"coefficient_mode": 2},
                       {"coefficient_mode": True}, {"coefficient_mode": 0, "slowest_smoothing_factor": 0.1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                FRAMA.FractalAdaptiveMovingAverage(**kwargs)


class FixtureTests(unittest.TestCase):
    def assert_exact(self, a, b):
        self.assertEqual(len(a), len(b))
        for x, y in zip(a, b):
            if math.isnan(y):
                self.assertTrue(math.isnan(x))
            else:
                self.assertEqual(x, y)

    def test_python_expected_arrays(self):
        arrays = literal_arrays(HERE / "test_testdata.py")
        self.assertEqual(len([name for name in arrays if name.startswith("EXPECTED_")]), 32)
        for case in FRAMA.REFERENCE_CASES:
            stream = FRAMA.FractalAdaptiveMovingAverage(*case[:3])
            result = [stream.update(price) for price in INPUTS]
            alpha = format(case.slowest_smoothing_factor, ".15g").replace(".", "_")
            suffix = f"L{case.length}_A{alpha}_C{case.coefficient_mode}"
            for index, field in enumerate(("VALUE", "FDIM")):
                expected = [math.nan if math.isnan(row[index]) else float(format(row[index], ".15g"))
                            for row in result]
                self.assert_exact(arrays[f"EXPECTED_{suffix}_{field}"], expected)

    def test_all_cross_language_inputs_values_and_nan_masks(self):
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
                self.assertEqual(len(actual), 36)
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

    def test_comments_match_in_each_language(self):
        python = (HERE / "test_testdata.py").read_text()
        for filename in ("testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig"):
            text = (HERE / filename).read_text()
            for case in FRAMA.REFERENCE_CASES:
                parameters = (f"length={case.length}, slowest_smoothing_factor={case.slowest_smoothing_factor}, "
                              f"coefficient_mode={case.coefficient_mode}; input=INPUT_CLOSE; high=low=close")
                self.assertEqual(python.count(f"# {case.what_it_tests}\n# {parameters}\n"), 2)
                header = f"// {case.what_it_tests}\n// {parameters}\n"
                if filename.endswith(".rs"):
                    header = header.replace("\n//", "\n    //").rstrip("\n")
                self.assertEqual(text.count(header), 2)

    def test_regeneration_is_byte_identical(self):
        names = ("test_testdata.py", "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig")
        with tempfile.TemporaryDirectory(prefix="frama-regeneration-") as directory:
            root = Path(directory)
            for name in names:
                (root / name).write_bytes((HERE / name).read_bytes())
            self.assertEqual(FRAMA.generate_reference_data(root, INPUTS), 32)
            for name in names:
                self.assertEqual((root / name).read_bytes(), (HERE / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
