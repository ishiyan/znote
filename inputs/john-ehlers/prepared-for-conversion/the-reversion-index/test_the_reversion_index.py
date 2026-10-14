"""Independent numerical and fixture acceptance tests; standard library only.

Run python3 the-reversion-index.py --verify, or python3 -m unittest discover.
The batch oracle below follows the article using full arrays, not the master's
ring, private coefficient helper, or per-sample filter state.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "reversion_index_master", HERE / "the-reversion-index.py"
)
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)


def article_batch(closes, length, smooth_period, trigger_period):
    """Separate batch transcription of the article with confirmed prehistory.

    Inputs before index length supply history only; CurrentBar starts at 1 on
    the first full window. Retained ratios and filter histories use full lists.
    """
    ratios = []
    retained = 0.0
    for t in range(length, len(closes)):
        numerator = 0.0
        denominator = 0.0
        for offset in range(length):
            numerator = numerator + closes[t - offset] - closes[t - offset - 1]
            denominator = denominator + abs(closes[t - offset] - closes[t - offset - 1])
        if denominator != 0.0:
            retained = numerator / denominator
        ratios.append(retained)

    lines = []
    for period in (smooth_period, trigger_period):
        q = math.exp(-1.414 * 3.14159 / period)
        # Written independently rather than calling the master's helper.
        c1 = 2.0 * q * math.cos((1.414 * 180.0 / period) * (math.pi / 180.0))
        c2 = q * q
        a0 = (1.0 - c1 + c2) / 2.0
        output = []
        for k, value in enumerate(ratios):
            if k + 1 < 4:
                output.append(value)
            else:
                output.append(a0 * (value + ratios[k - 1])
                              + c1 * output[k - 1] - c2 * output[k - 2])
        lines.append(output)
    # When length exceeds the input count, do not return excess padding.
    padding = [MASTER.ReversionIndexResult(math.nan, math.nan, math.nan)
               for _ in range(min(length, len(closes)))]
    return padding + [MASTER.ReversionIndexResult(r, s, t)
                      for r, s, t in zip(ratios, lines[0], lines[1])]


def literal_inputs(path):
    """Only evaluate literal INPUT_* lists; NaN definitions are irrelevant."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {node.targets[0].id: ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.startswith("INPUT_")}


def parse_tokens(body, nan_token):
    """Parse comma-separated numeric fixture literals without executing code."""
    tokens = [value.strip() for value in body.split(",") if value.strip()]
    return [math.nan if value == nan_token else float(value) for value in tokens]


class ReversionIndexTests(unittest.TestCase):
    def assert_number_equal(self, actual, expected):
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual))
        else:
            self.assertTrue(math.isfinite(actual))
            self.assertTrue(
                math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12),
                f"{actual!r} != {expected!r}",
            )

    def assert_series_equal(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for a, e in zip(actual, expected):
            self.assert_number_equal(a, e)

    def compare_to_article(self, closes, length, slow=8, fast=4):
        indicator = MASTER.ReversionIndex(length, slow, fast)
        actual = [indicator.update(close) for close in closes]
        expected = article_batch(closes, length, slow, fast)
        self.assertEqual(len(actual), len(expected))
        for index, (a, e) in enumerate(zip(actual, expected)):
            with self.subTest(index=index, length=length, slow=slow, fast=fast):
                self.assert_series_equal(a, e)
        return actual

    def test_confirmed_grid_matches_independent_article(self):
        closes = MASTER.read_input_close()
        self.assertEqual(len(MASTER.REFERENCE_CASES), 16)
        for length, slow, fast, _ in MASTER.REFERENCE_CASES:
            self.compare_to_article(closes, length, slow, fast)

    def test_full_window_start_and_fourth_valid_recursion(self):
        # First three ratios are +1; the fourth differs, so recurrence
        # cannot be confused with a fourth pass-through initialization.
        result = self.compare_to_article([1, 2, 3, 4, 5, 3, 2, 4], 2)
        self.assertEqual(MASTER.ReversionIndex(2).warmup_bars, 2)
        self.assertTrue(all(math.isnan(v) for r in result[:2] for v in r))
        for r in result[2:5]:
            self.assertEqual(r.ratio, r.smooth)
            self.assertEqual(r.ratio, r.trigger)
        self.assertNotEqual(result[5].ratio, result[5].smooth)
        self.assertNotEqual(result[5].ratio, result[5].trigger)

    def test_flat_prices_and_ratio_retained_after_motion(self):
        flat = self.compare_to_article([7.0] * 32, 5)
        self.assertTrue(all(r == (0.0, 0.0, 0.0) for r in flat[5:]))
        for direction in (-1, 1):
            prices = [10.0, 10.0 + direction] + [10.0 + direction] * 24
            result = self.compare_to_article(prices, 1)
            # Once all changes are zero, the article keeps the prior sign.
            self.assertTrue(all(r.ratio == direction for r in result[1:]))

    def test_monotonic_alternating_and_sinusoidal_prices(self):
        for prices in (
            [float(i) for i in range(80)],
            [-float(i) for i in range(80)],
            [1.0 if i % 2 else -1.0 for i in range(80)],
            [100.0 + 5.0 * math.sin(2.0 * math.pi * i / 20) for i in range(80)],
        ):
            for length in (1, 2, 10):
                self.compare_to_article(prices, length, 8.5, 4.5)

    def test_literal_numerator_expression_order(self):
        # For these IEEE-754 inputs, adding the precomputed difference loses
        # a representable bit. This test guards an otherwise tempting rewrite.
        indicator = MASTER.ReversionIndex(2)
        for close in (1e16, 1.0, 2.0):
            result = indicator.update(close)
        self.assertEqual(result.ratio, -0.9999999999999998)
        reassociated = (2.0 - 1.0) + (1.0 - 1e16)
        denominator = abs(2.0 - 1.0) + abs(1.0 - 1e16)
        self.assertNotEqual(result.ratio, reassociated / denominator)

    def test_equal_reversed_and_fractional_periods(self):
        prices = MASTER.read_input_close()
        same = self.compare_to_article(prices, 10, 8, 8)
        normal = self.compare_to_article(prices, 10, 8, 4)
        reverse = self.compare_to_article(prices, 10, 4, 8)
        self.compare_to_article(prices, 10, 8.5, 4.5)
        for e, n, r in zip(same[10:], normal[10:], reverse[10:]):
            self.assertEqual(e.smooth, e.trigger)
            self.assertEqual(n.smooth, r.trigger)
            self.assertEqual(n.trigger, r.smooth)

    def test_invalid_parameters_and_updates_do_not_consume_bars(self):
        for length in (True, 2.0, "2", None):
            with self.assertRaises(TypeError):
                MASTER.ReversionIndex(length)
        for length in (0, -1):
            with self.assertRaises(ValueError):
                MASTER.ReversionIndex(length)
        for field in ("smooth_period", "trigger_period"):
            for value in (True, "8", None):
                with self.assertRaises(TypeError):
                    MASTER.ReversionIndex(**{field: value})
            for value in (0, -1, math.nan, math.inf, -math.inf, 10**400):
                with self.assertRaises(ValueError):
                    MASTER.ReversionIndex(**{field: value})

        a, b = MASTER.ReversionIndex(2), MASTER.ReversionIndex(2)
        for close in (1.0, 2.0, 3.0, 4.0, 2.0, 5.0):
            for invalid, exception in ((None, TypeError), (True, TypeError),
                                       ("1", TypeError), (math.nan, ValueError),
                                       (math.inf, ValueError), (10**400, ValueError)):
                with self.assertRaises(exception):
                    a.update(invalid)
            self.assert_series_equal(a.update(close), b.update(close))
        for name in ("length", "smooth_period", "trigger_period", "warmup_bars"):
            with self.assertRaises(AttributeError):
                setattr(a, name, 7)

    def test_bounded_storage_and_independent_instances(self):
        first = MASTER.ReversionIndex(5)
        second = MASTER.ReversionIndex(5)
        for index in range(500):
            first.update(index)
            self.assertEqual(len(first._prices), 6)
            self.assertLessEqual(first._count, 6)
        self.assertTrue(all(math.isnan(v) for v in second.update(9)))
        self.assertEqual(second._count, 1)
        self.assertEqual(second._smooth._valid_bars, 0)

    def test_positive_period_underflow_has_finite_limiting_coefficients(self):
        # The positive-period API includes subnormal floats. Once q is zero,
        # a0=1/2 and both feedback coefficients are zero: a two-point average.
        tiny = MASTER.ReversionIndex(1, 5e-324, 5e-324)
        results = [tiny.update(close) for close in (1.0, 2.0, 3.0, 1.0, 4.0)]
        self.assertTrue(all(math.isnan(v) for v in results[0]))
        self.assertEqual(results[-1], (1.0, 0.0, 0.0))

    def test_last_bar_and_entirely_unprimed_windows(self):
        prices = MASTER.read_input_close()
        last = self.compare_to_article(prices, 251)
        never = self.compare_to_article(prices, 252)
        beyond = self.compare_to_article(prices, 300)
        self.assertTrue(all(math.isnan(v) for r in last[:-1] for v in r))
        self.assertTrue(all(math.isfinite(v) for v in last[-1]))
        self.assertEqual(last[-1].ratio, last[-1].smooth)
        self.assertEqual(last[-1].ratio, last[-1].trigger)
        self.assertTrue(all(math.isnan(v) for r in never + beyond for v in r))

    def test_saved_python_references_and_precision(self):
        saved = MASTER.read_serialized_vectors()
        computed = MASTER.compute_reference_vectors(MASTER.read_input_close())
        self.assertEqual(len(saved), 48)
        self.assertEqual(len({v[0] for v in saved}), 48)
        for (name, explanation, parameters, tokens), expected in zip(saved, computed):
            self.assertEqual((name, explanation, parameters), expected[:3])
            canonical = ["NaN" if math.isnan(v) else format(v, ".15f")
                         for v in expected[3]]
            self.assertEqual(tokens, canonical)
            values = [math.nan if token == "NaN" else float(token) for token in tokens]
            self.assert_series_equal(values, expected[3])
        python_data = {}
        exec(compile((HERE / "test_testdata.py").read_text(), "test_testdata.py", "exec"),
             python_data)
        self.assertEqual(sum(name.startswith("EXPECTED_") for name in python_data), 48)
        for name, _, _, tokens in saved:
            self.assert_series_equal(python_data[name],
                                     [math.nan if t == "NaN" else float(t) for t in tokens])

    def test_other_language_arrays_and_comments_match_python(self):
        saved = MASTER.read_serialized_vectors()
        languages = (
            ("testdata_test.go",
             r"^// ([^\n]+)\n// ([^\n]+)\nvar expected([A-Z0-9_]+) = \[\]float64\{\n(.*?)\n\}",
             "math.NaN()", False),
            ("testdata.ts",
             r"^// ([^\n]+)\n// ([^\n]+)\nexport const expected([A-Z0-9_]+): number\[\] = \[\n(.*?)\n\];",
             "NaN", False),
            ("testdata.rs",
             r"^    // ([^\n]+)\n    // ([^\n]+)\n    pub fn expected_([a-z0-9_]+)\(\) -> Vec<f64> \{\n        vec!\[\n(.*?)\n        \]\n    \}",
             "f64::NAN", True),
            ("testdata.zig",
             r"^// ([^\n]+)\n// ([^\n]+)\npub fn expected([A-Z0-9_]+)\(\) \[252\]f64 \{\n    return \.\{\n(.*?)\n    \};\n\}",
             "nan", False),
        )
        for filename, pattern, nan_token, lowercase in languages:
            text = (HERE / filename).read_text(encoding="utf-8")
            blocks = re.findall(pattern, text, re.M | re.S)
            self.assertEqual(len(blocks), 48, filename)
            for block, python in zip(blocks, saved):
                explanation, parameters, tag, body = block
                name, py_explanation, py_parameters, tokens = python
                py_tag = name.removeprefix("EXPECTED_")
                self.assertEqual(tag, py_tag.lower() if lowercase else py_tag)
                self.assertEqual((explanation, parameters), (py_explanation, py_parameters))
                other = [t.strip() for t in body.split(",") if t.strip()]
                self.assertEqual(other, [nan_token if t == "NaN" else t for t in tokens])
                self.assertEqual(len(other), 252)
        self.assertIn('package thereversionindex\n', (HERE / "testdata_test.go").read_text())
        self.assertIn('import "math"', (HERE / "testdata_test.go").read_text())
        zig = (HERE / "testdata.zig").read_text()
        self.assertTrue(zig.startswith('const math = @import("std").math;\n'
                                      'const nan = math.nan(f64);\n'))

    def test_inputs_preserved_in_every_language_and_embedded_main(self):
        inputs = literal_inputs(HERE / "test_testdata.py")
        self.assertEqual(set(inputs), {"INPUT_CLOSE", "INPUT_HIGH", "INPUT_LOW", "INPUT_OPEN"})
        # The independent literal inside main must match all 252 close values.
        master_tree = ast.parse((HERE / "the-reversion-index.py").read_text())
        main = next(node for node in master_tree.body if isinstance(node, ast.If))
        embedded = next(node for node in main.body if isinstance(node, ast.Assign))
        self.assertEqual(ast.literal_eval(embedded.value), inputs["INPUT_CLOSE"])

        names = (("INPUT_CLOSE", "testInput", "test_input"),
                 ("INPUT_HIGH", "testHigh", "test_high"),
                 ("INPUT_LOW", "testLow", "test_low"),
                 ("INPUT_OPEN", "testOpen", "test_open"))
        for py_name, mixed_name, rust_name in names:
            patterns = (
                ("testdata_test.go", rf"var {mixed_name} = \[\]float64\{{(.*?)\}}"),
                ("testdata.ts", rf"export const {mixed_name}: number\[\] = \[(.*?)\]"),
                ("testdata.rs", rf"pub fn {rust_name}\(\) -> Vec<f64> \{{\s*vec!\[(.*?)\]"),
                ("testdata.zig", rf"pub fn {mixed_name}\(\) \[252\]f64 \{{\s*return \.\{{(.*?)\}}"),
            )
            self.assertEqual(len(inputs[py_name]), 252)
            for filename, pattern in patterns:
                match = re.search(pattern, (HERE / filename).read_text(), re.S)
                self.assertIsNotNone(match, f"{filename} {mixed_name}")
                self.assertEqual(parse_tokens(match[1], "NaN"), inputs[py_name])

        # When the original templates are available, compare their complete
        # input definitions as well. Tests remain usable after this directory
        # is copied alone to the conversion repository.
        parent = HERE.parent / "test_testdata.py"
        if parent.exists():
            self.assertEqual(inputs, literal_inputs(parent))


if __name__ == "__main__":
    unittest.main(verbosity=2)
