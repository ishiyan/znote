"""Meaningful verification of the streaming master and its confirmed fixtures.

Run with: python3 -m unittest discover -p 'test_one_euro_filter.py' -v
No external Python packages or source-file top-level execution are required.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re
from types import SimpleNamespace
import unittest


DIRECTORY = Path(__file__).resolve().parent
SOURCE_DIRECTORY = DIRECTORY.parent.parent / "tasc" / "2025-12-the-one-euro-filter"
SPEC = importlib.util.spec_from_file_location("one_euro_master", DIRECTORY / "the-one-euro-filter.py")
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUT_CLOSE = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")["INPUT_CLOSE"]


def published_python_function():
    """Execute the actual supplied function body, excluding downloads and plots.

    Its only NumPy operations are conversion to an array, zeros allocation,
    scalar indexing, and access to pi. A list adapter provides precisely those
    operations, keeping these reference tests runnable using standard Python.
    """
    source = SOURCE_DIRECTORY / "tips" / "Python_OneEuroFilter.py"
    parsed = ast.parse(source.read_text(encoding="utf-8"))
    function = next(
        node for node in parsed.body
        if isinstance(node, ast.FunctionDef) and node.name == "calc_one_euro_filter"
    )
    namespace = {
        "np": SimpleNamespace(asarray=lambda values: list(values), zeros=lambda n: [0.0] * n, pi=math.pi)
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), namespace)
    return namespace["calc_one_euro_filter"]


class OneEuroFilterTests(unittest.TestCase):
    def test_matches_original_python_body_for_all_confirmed_cases(self):
        # Original source recurrence versus streaming state. This catches
        # initialization, source constant, index, and update-order differences.
        original = published_python_function()
        self.assertEqual(len(INPUT_CLOSE), 252)
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(period_min=case.period_min, beta=case.beta):
                expected = original(INPUT_CLOSE, case.period_min, case.beta)
                indicator = MASTER.OneEuroFilter(case.period_min, case.beta)
                actual = [indicator.update(price) for price in INPUT_CLOSE]
                self.assertEqual(actual, expected)
                self.assertTrue(all(math.isfinite(value) for value in actual))

    def test_first_sample_primes_immediately_and_reset_reseeds(self):
        indicator = MASTER.OneEuroFilter()
        self.assertFalse(indicator.is_primed)
        self.assertEqual(indicator.warmup_bars, 0)
        self.assertEqual(indicator.update(91.5), 91.5)
        self.assertTrue(indicator.is_primed)
        first_run = [indicator.update(value) for value in INPUT_CLOSE[1:]]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertEqual(indicator.update(91.5), 91.5)
        self.assertEqual(first_run, [indicator.update(value) for value in INPUT_CLOSE[1:]])
        indicator.reset()
        self.assertEqual(indicator.update(0.0), 0.0)
        self.assertTrue(indicator.is_primed)

    def test_fixed_ema_matches_analytic_step_response(self):
        # This oracle uses the closed-form step response, not the master loop.
        # The first input seeds zero; thereafter the target is exactly one.
        indicator = MASTER.OneEuroFilter(period_min=10, beta=0)
        alpha = 2 * math.pi / (4 * math.pi + 10)
        self.assertEqual(indicator.update(0), 0)
        for n in range(1, 101):
            expected = 1.0 - (1.0 - alpha) ** n
            self.assertAlmostEqual(indicator.update(1), expected, places=14)

    def test_unity_gain_for_constant_input(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.OneEuroFilter(case.period_min, case.beta)
            for _ in range(100):
                self.assertAlmostEqual(indicator.update(25.0), 25.0, places=12)

    def test_signed_difference_cancels_before_absolute_value(self):
        # With +1 then -1, the derivative must be negative and small. An EMA
        # of absolute differences would instead be positive and much larger.
        indicator = MASTER.OneEuroFilter(period_min=10, beta=2)
        for value in (0.0, 1.0, 0.0):
            indicator.update(value)
        a = 2 * math.pi / (4 * math.pi + 10)
        self.assertAlmostEqual(indicator._smoothed_dx, -(a * a), places=15)
        self.assertLess(abs(indicator._smoothed_dx), a)

    def test_positive_beta_smooths_and_negative_beta_sharpens(self):
        outputs = {}
        for beta in (-0.2, 0.0, 0.2, 2.0):
            indicator = MASTER.OneEuroFilter(period_min=10, beta=beta)
            indicator.update(0.0)
            outputs[beta] = indicator.update(1.0)
        self.assertGreater(outputs[-0.2], outputs[0.0])
        self.assertGreater(outputs[0.0], outputs[0.2])
        self.assertGreater(outputs[0.2], outputs[2.0])

    def test_prefix_causality_and_convex_output(self):
        indicator = MASTER.OneEuroFilter(period_min=2, beta=-0.2)
        full = []
        previous = INPUT_CLOSE[0]
        for price in INPUT_CLOSE:
            output = indicator.update(price)
            self.assertLessEqual(min(price, previous) - 1e-12, output)
            self.assertLessEqual(output, max(price, previous) + 1e-12)
            full.append(output)
            previous = output
        prefix = MASTER.OneEuroFilter(period_min=2, beta=-0.2)
        self.assertEqual(full[:87], [prefix.update(price) for price in INPUT_CLOSE[:87]])

    def test_fractional_period_supported(self):
        original = published_python_function()
        indicator = MASTER.OneEuroFilter(period_min=2.5, beta=0.05)
        self.assertEqual(
            [indicator.update(price) for price in INPUT_CLOSE],
            original(INPUT_CLOSE, period_min=2.5, beta=0.05),
        )

    def test_invalid_parameters(self):
        for period in (0, -1, math.nan, math.inf, -math.inf):
            with self.subTest(period=period), self.assertRaises(ValueError):
                MASTER.OneEuroFilter(period_min=period)
        for beta in (math.nan, math.inf, -math.inf):
            with self.subTest(beta=beta), self.assertRaises(ValueError):
                MASTER.OneEuroFilter(beta=beta)

    def test_invalid_input_and_cutoff_preserve_state(self):
        indicator = MASTER.OneEuroFilter(period_min=2, beta=-0.2)
        twin = MASTER.OneEuroFilter(period_min=2, beta=-0.2)
        for value in (100.0, 101.0):
            self.assertEqual(indicator.update(value), twin.update(value))
        # Infinity/NaN input and an extreme admissible input price whose delta
        # makes negative beta produce a nonpositive adaptive cutoff are errors.
        for bad in (math.nan, math.inf, -math.inf, 1000.0):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                indicator.update(bad)
        self.assertEqual(indicator.update(102.0), twin.update(102.0))
        fresh = MASTER.OneEuroFilter()
        with self.assertRaises(ValueError):
            fresh.update(math.nan)
        self.assertFalse(fresh.is_primed)

    def test_input_arrays_preserved_and_main_embeds_all_closes(self):
        # Check copied OHLC data against the unchanged shared input templates.
        copied = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        templates = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        for name in ("INPUT_CLOSE", "INPUT_HIGH", "INPUT_LOW", "INPUT_OPEN"):
            self.assertEqual(len(copied[name]), 252)
            self.assertEqual(copied[name], templates[name])
        parsed = ast.parse((DIRECTORY / "the-one-euro-filter.py").read_text())
        embedded = next(
            node for node in ast.walk(parsed)
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "INPUT_CLOSE" for target in node.targets)
        )
        self.assertEqual(ast.literal_eval(embedded.value), INPUT_CLOSE)

    def test_generated_python_fixtures(self):
        # Confirmation has been received; missing expected data is now a failure.
        arrays = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        names = {name for name in arrays if name.startswith("EXPECTED_")}
        self.assertEqual(names, {"EXPECTED_" + MASTER._case_suffix(case) for case in MASTER.REFERENCE_CASES})
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.OneEuroFilter(case.period_min, case.beta)
            fixture = arrays["EXPECTED_" + MASTER._case_suffix(case)]
            self.assertEqual(len(fixture), 252)
            self.assertEqual(fixture[0], INPUT_CLOSE[0])
            for price, expected in zip(INPUT_CLOSE, fixture):
                self.assertTrue(math.isclose(indicator.update(price), expected, rel_tol=5e-14, abs_tol=5e-14))

    def test_other_language_fixtures_match_python_values_and_comments(self):
        # Check every serialized value, portable identifier, and required pair
        # of comments. This catches omissions or changes during translation.
        arrays = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        patterns = {
            "testdata_test.go": r"var expected(\w+) = \[\]float64\{\s*(.*?)\n\}",
            "testdata.ts": r"export const expected(\w+): number\[\] = \[\s*(.*?)\n\];",
            "testdata.rs": r"pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[\s*(.*?)\n\s*\]\s*\}",
            "testdata.zig": r"pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{\s*(.*?)\n\s*\};\s*\}",
        }
        for filename, pattern in patterns.items():
            with self.subTest(filename=filename):
                text = (DIRECTORY / filename).read_text(encoding="utf-8")
                matches = re.findall(pattern, text, flags=re.DOTALL)
                self.assertEqual(len(matches), len(MASTER.REFERENCE_CASES))
                serialized = dict(matches)
                self.assertEqual(len(serialized), len(matches))
                for case in MASTER.REFERENCE_CASES:
                    suffix = MASTER._case_suffix(case)
                    name = suffix.lower() if filename.endswith(".rs") else suffix
                    values = [float(token.strip()) for token in serialized[name].split(",") if token.strip()]
                    self.assertEqual(values, arrays["EXPECTED_" + suffix])
                    comments = (
                        f"// {case.what_it_tests}\n"
                        f"// period_min={case.period_min:g}, beta={case.beta:g}, period_dx=10 (fixed)\n"
                    )
                    self.assertIn(comments, text)


if __name__ == "__main__":
    unittest.main()
