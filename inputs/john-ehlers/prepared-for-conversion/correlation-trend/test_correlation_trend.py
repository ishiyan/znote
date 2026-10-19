"""Source-expression oracle, correlation theory, and portable fixture validation.

The runtime master is standalone. Provenance tests read the supplied article,
Mesa paper, and TradeStation listing, so keep those sources when moving tests.
No external numerical or testing libraries are required.
"""

import ast
import contextlib
from fractions import Fraction
import importlib.util
import io
import math
from pathlib import Path
import re
import tempfile
import unittest


DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("correlation_trend_master", DIRECTORY / "correlation-trend.py")
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
CorrelationTrend = MASTER.CorrelationTrend
INPUTS = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
CLOSE = INPUTS["INPUT_CLOSE"]
SOURCE_DIRECTORY = DIRECTORY.parent.parent / "tasc/2020-05-correlation-as-a-trend-indicator"
ARTICLE = SOURCE_DIRECTORY.joinpath("content.md").read_text()
MESA = SOURCE_DIRECTORY.joinpath("mesa/content.md").read_text()
TRADESTATION = SOURCE_DIRECTORY.joinpath("tips/CTI.els").read_text().split("Function: _CorrelationTrend")[1]
FIXTURES = ("test_testdata.py", "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig")


def source_expression(source, variable):
    """Extract a formula following =, not an EasyLanguage declaration."""
    matches = re.findall(r"\b" + variable + r"\s*=\s*(.*?);", source, re.I | re.S)
    # Sum variables have a reset assignment followed by their loop assignment.
    expression = matches[-1]
    return " ".join(expression.split())


def source_batch(prices, length, source=ARTICLE):
    """Evaluate literal source formulas against independent full histories.

    Zero-filled prehistory is not invented. Until the complete price window is
    available, the public output is NaN and the persistent Corr remains zero.
    Uses no streaming class methods, helpers, or cached master coefficients.
    """
    sum_formulas = {name: source_expression(source, name)
                    for name in ("Sx", "Sy", "Sxx", "Sxy", "Syy")}
    x_formula = compile(source_expression(source, "X"), "source-X", "eval")
    y_formula = compile(source_expression(source, "Y"), "source-Y", "eval")
    sum_formulas = {name: compile(expression, "source-" + name, "eval")
                    for name, expression in sum_formulas.items()}
    if source == TRADESTATION:
        numerator = source_expression(source, "Num")
        denominator = source_expression(source, "Denom")
        formula = source_expression(source, "Corr")
    else:
        numerator = None
        denominator = None
        formula = source_expression(source, "Corr")
    formula = compile(formula, "source-Corr", "eval")
    outputs = []
    corr = 0.0
    for t in range(len(prices)):
        if t < length - 1:
            outputs.append(math.nan)
            continue
        env = {"Length": length, "Close": [prices[t - i] for i in range(length)],
               "SquareRoot": math.sqrt, "Sx": 0.0, "Sy": 0.0, "Sxx": 0.0,
               "Sxy": 0.0, "Syy": 0.0}
        for count in range(length):
            env["count"] = count
            env["X"] = eval(x_formula, {"__builtins__": {}}, env)
            env["Y"] = eval(y_formula, {"__builtins__": {}}, env)
            for name, expression in sum_formulas.items():
                env[name] = eval(expression, {"__builtins__": {}}, env)
        if source == TRADESTATION:
            env["Num"] = eval(numerator, {"__builtins__": {}}, env)
            env["Denom"] = eval(denominator, {"__builtins__": {}}, env)
            guard = env["Denom"] != 0
        else:
            # Literal article/Mesa guard: BOTH variance terms must be positive.
            guard = (length * env["Sxx"] - env["Sx"] * env["Sx"] > 0
                     and length * env["Syy"] - env["Sy"] * env["Sy"] > 0)
        if guard:
            corr = eval(formula, {"__builtins__": {}}, env)
        outputs.append(corr)
    return outputs


def exact_centered(window):
    """Independent rational centered Pearson result for a chronological window.

    Fraction captures each input float exactly; the centered calculation avoids
    the raw-sums cancellation path and tests mathematics rather than copying
    the master formula. Undefined one-price/flat cases return None.
    """
    n = len(window)
    prices = [Fraction(value) for value in window]
    times = [Fraction(i) for i in range(n)]
    mean_x = sum(prices) / n
    mean_y = sum(times) / n
    x = [v - mean_x for v in prices]
    y = [v - mean_y for v in times]
    xx = sum(v * v for v in x)
    yy = sum(v * v for v in y)
    if xx == 0 or yy == 0:
        return None
    return float(sum(a * b for a, b in zip(x, y))) / math.sqrt(float(xx * yy))


def compare(test, actual, expected, tolerance=0.0):
    test.assertEqual(len(actual), len(expected))
    for index, (left, right) in enumerate(zip(actual, expected)):
        if math.isnan(right):
            test.assertTrue(math.isnan(left), (index, left, right))
        else:
            test.assertTrue(math.isfinite(left) and math.isclose(left, right,
                            rel_tol=tolerance, abs_tol=tolerance), (index, left, right))


def language_expected(path):
    """Parse native expected data independently of the master renderers."""
    patterns = {
        ".go": r"var expectedL(\d+) = \[\]float64\{(.*?)\}",
        ".ts": r"export const expectedL(\d+): number\[\] = \[(.*?)\];",
        ".rs": r"pub fn expected_l(\d+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]\s*\}",
        ".zig": r"pub fn expectedL(\d+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\};\s*\}",
    }
    arrays = {}
    for length, body in re.findall(patterns[path.suffix], path.read_text(), re.S):
        arrays["EXPECTED_L" + length] = [
            math.nan if token.strip() in ("math.NaN()", "NaN", "f64::NAN", "nan")
            else float(token.strip()) for token in body.split(",") if token.strip()
        ]
    return arrays


class CorrelationTrendTests(unittest.TestCase):
    def test_all_confirmed_lengths_match_three_source_listings(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = CorrelationTrend(case.length)
            actual = [indicator.update(v) for v in CLOSE]
            for source in (ARTICLE, MESA, TRADESTATION):
                compare(self, actual, source_batch(CLOSE, case.length, source))

    def test_centered_exact_rational_pearson_on_fixture_windows(self):
        for n in (3, 10, 20, 40, 60, 126, 252):
            indicator = CorrelationTrend(n)
            for t, price in enumerate(CLOSE):
                output = indicator.update(price)
                if t in (n - 1, 150, 251) and indicator.is_primed:
                    expected = exact_centered(CLOSE[t - n + 1:t + 1])
                    self.assertIsNotNone(expected)
                    self.assertAlmostEqual(output, expected, delta=2e-11)

    def test_pearson_raw_prices_are_not_spearman_ranks(self):
        indicator = CorrelationTrend(3)
        actual = [indicator.update(v) for v in (1, 2, 10)]
        self.assertEqual(actual[-1], 27 / math.sqrt(876))
        self.assertLess(actual[-1], 0.95)  # Monotonic ranks would correlate as 1.
        self.assertAlmostEqual(actual[-1], exact_centered([1, 2, 10]), places=15)

    def test_positive_negative_and_affine_trend_geometry(self):
        for n in (2, 3, 5, 20, 60):
            for slope in (2, -3):
                indicator = CorrelationTrend(n)
                for t in range(2 * n):
                    value = indicator.update(100 + slope * t)
                    if indicator.is_primed:
                        self.assertAlmostEqual(value, 1 if slope > 0 else -1, places=15)

    def test_symmetric_window_zero_covariance_and_time_sums(self):
        indicator = CorrelationTrend(5)
        for value in (1, 4, 9, 4, 1):
            output = indicator.update(value)
        self.assertEqual(output, 0.0)
        self.assertEqual(indicator.state.numerator, 0.0)
        for n in (1, 2, 3, 20, 126, 252):
            instance = CorrelationTrend(n)
            for i in range(n):
                instance.update(i)
            self.assertEqual(instance.state.sum_y, -n * (n - 1) / 2)
            self.assertEqual(instance.state.sum_yy, n * (n - 1) * (2 * n - 1) / 6)
            self.assertEqual(instance.state.time_variance_term, n * n * (n * n - 1) / 12)

    def test_flat_window_retains_previous_correlation(self):
        for prices, sign in (([1, 2, 2, 2, 3], 1), ([3, 2, 2, 2, 1], -1)):
            indicator = CorrelationTrend(2)
            actual = [indicator.update(v) for v in prices]
            self.assertTrue(math.isnan(actual[0]))
            self.assertEqual(actual[1:], [float(sign)] * 4)
            compare(self, actual, source_batch(prices, 2))
        for constant in (0, 42, -42):
            indicator = CorrelationTrend(5)
            for t in range(20):
                output = indicator.update(constant)
                if t >= 4:
                    self.assertEqual(output, 0.0)
                    self.assertTrue(indicator.is_primed)
                    self.assertFalse(indicator.state.variance_valid)

    def test_nonpositive_roundoff_variance_uses_article_guard(self):
        # At a large price offset, literal binary64 raw sums can cancel to a
        # negative variance. This source-preserving master holds Corr instead
        # of evaluating sqrt(negative), centering, or inventing a new zero.
        prices = [100000000.0 + v for v in (0, 1, 2)]
        indicator = CorrelationTrend(3)
        actual = [indicator.update(v) for v in prices]
        compare(self, actual, source_batch(prices, 3))
        self.assertLessEqual(indicator.state.price_variance_term, 0.0)
        self.assertFalse(indicator.state.variance_valid)
        self.assertEqual(actual[-1], 0.0)

    def test_one_price_degenerate_time_ramp(self):
        indicator = CorrelationTrend(1)
        self.assertEqual(indicator.warmup_bars, 0)
        for price in CLOSE:
            self.assertEqual(indicator.update(price), 0.0)
            self.assertTrue(indicator.is_primed)
            self.assertFalse(indicator.state.variance_valid)
            self.assertEqual(indicator.state.time_variance_term, 0.0)

    def test_priming_and_exact_record_boundaries(self):
        for case in MASTER.REFERENCE_CASES:
            n = case.length
            indicator = CorrelationTrend(n)
            self.assertEqual(indicator.warmup_bars, n - 1)
            for t, price in enumerate(CLOSE):
                value = indicator.update(price)
                self.assertEqual(math.isnan(value), t < n - 1)
                self.assertEqual(indicator.is_primed, t >= n - 1)
                self.assertEqual(len(indicator._prices), min(n, t + 1))
        boundary = CorrelationTrend(253)
        self.assertTrue(all(math.isnan(boundary.update(v)) for v in CLOSE))
        self.assertTrue(math.isfinite(boundary.update(CLOSE[-1])))

    def test_scale_offset_reflection_and_prefix_causality(self):
        prices = [3, 7, 2, 9, 4, 6, 0, -3, 5, 10]
        indicator = CorrelationTrend(5)
        expected = [indicator.update(v) for v in prices]
        for scale, offset in ((8, 0), (1, 100), (-1, 0), (2, -20)):
            fresh = CorrelationTrend(5)
            actual = [fresh.update(scale * v + offset) for v in prices]
            compare(self, actual, [v * (1 if scale > 0 else -1) for v in expected], 1e-14)
        prefix = CorrelationTrend(5)
        compare(self, [prefix.update(v) for v in prices[:7]], expected[:7])

    def test_reset_and_invalid_updates_leave_state_unchanged(self):
        indicator = CorrelationTrend(20)
        expected = [indicator.update(v) for v in CLOSE]
        state = (indicator._prices[:], indicator._corr, indicator.state)
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(value)
            self.assertEqual((indicator._prices, indicator._corr, indicator.state), state)
        extreme = CorrelationTrend(2)
        extreme.update(1e308)
        before = (extreme._prices[:], extreme._corr, extreme.state)
        with self.assertRaises(ValueError):
            extreme.update(1e308)
        self.assertEqual((extreme._prices, extreme._corr, extreme.state), before)
        # Both factors can be finite while their product overflows.
        product_overflow = CorrelationTrend(3)
        product_overflow.update(3e153)
        product_overflow.update(-3e153)
        before = (product_overflow._prices[:], product_overflow._corr, product_overflow.state)
        with self.assertRaises(ValueError):
            product_overflow.update(3e153)
        self.assertEqual((product_overflow._prices, product_overflow._corr, product_overflow.state), before)
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isnan(indicator.state.correlation))
        compare(self, [indicator.update(v) for v in CLOSE], expected)

    def test_parameter_validation(self):
        for length in (0, -1, True, False, 20.0, "20", None):
            with self.assertRaises(ValueError):
                CorrelationTrend(length)
        indicator = CorrelationTrend(20)
        with self.assertRaises(AttributeError):
            indicator.length = 40

    def test_embedded_inputs_and_fixture_copies(self):
        parent = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        self.assertEqual({name: INPUTS[name] for name in parent}, parent)
        self.assertEqual(len(CLOSE), 252)
        tree = ast.parse(DIRECTORY.joinpath("correlation-trend.py").read_text())
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "INPUT_CLOSE" for t in node.targets))
        self.assertEqual(ast.literal_eval(node.value), CLOSE)
        for filename in FIXTURES[1:]:
            before = DIRECTORY.parent.joinpath(filename).read_text()
            after = DIRECTORY.joinpath(filename).read_text()
            if filename.endswith(".go"):
                before = before.replace("package xxxx", "package correlationtrend", 1)
                after = after.replace('import "math"\n\n', "", 1)
            if filename.endswith(".rs"):
                before = before[:before.rfind("}")].rstrip()
            self.assertTrue(after.startswith(before.rstrip()), filename)

    def test_expected_arrays_and_all_language_values(self):
        names = {"EXPECTED_L" + str(case.length) for case in MASTER.REFERENCE_CASES}
        self.assertEqual({name for name in INPUTS if name.startswith("EXPECTED_")}, names)
        for case in MASTER.REFERENCE_CASES:
            values = INPUTS["EXPECTED_L" + str(case.length)]
            compare(self, values, source_batch(CLOSE, case.length), 5e-13)
            self.assertEqual(len(values), 252)
            self.assertEqual(sum(math.isnan(v) for v in values), min(252, case.length - 1))
            for filename in FIXTURES:
                prefix = "#" if filename.endswith(".py") else "//"
                self.assertIn(f"{prefix} {case.what_it_tests}\n{prefix} length={case.length}\n",
                              DIRECTORY.joinpath(filename).read_text())
        for filename in FIXTURES[1:]:
            native = language_expected(DIRECTORY / filename)
            self.assertEqual(set(native), names)
            for name, values in native.items():
                compare(self, values, INPUTS[name])

    def test_repeatable_generation_preserves_inputs(self):
        with tempfile.TemporaryDirectory(prefix="correlation-trend-fixtures-") as temporary:
            directory = Path(temporary)
            for filename in FIXTURES:
                directory.joinpath(filename).write_text(DIRECTORY.parent.joinpath(filename).read_text())
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, directory)
                first = {filename: directory.joinpath(filename).read_bytes() for filename in FIXTURES}
                MASTER.generate_reference_data(CLOSE, directory)
            self.assertEqual(first, {filename: directory.joinpath(filename).read_bytes() for filename in FIXTURES})
            arrays = MASTER._load_literal_arrays(directory / "test_testdata.py")
            for filename in FIXTURES[1:]:
                for name, values in language_expected(directory / filename).items():
                    compare(self, values, arrays[name])


if __name__ == "__main__":
    unittest.main()
