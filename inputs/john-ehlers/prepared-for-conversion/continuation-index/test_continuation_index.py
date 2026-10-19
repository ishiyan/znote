"""Verify the causal master against the article with full-precision constants.

Only standard Python is used. All sixteen cases have been confirmed; missing
expected arrays, incorrect warm-up, or mistranslated fixture data are failures.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest


DIRECTORY = Path(__file__).resolve().parent
ARTICLE = DIRECTORY.parent.parent / "tasc" / "2025-09-the-continuation-index" / "content.md"
SPEC = importlib.util.spec_from_file_location("continuation_index_master", DIRECTORY / "continuation-index.py")
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUT_CLOSE = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")["INPUT_CLOSE"]


def article_batch(close, gama, order, length, full_precision=True):
    """Evaluate arithmetic extracted from the original EasyLanguage listing.

    This is an independent batch interpreter of the provided expressions, not
    a call to the master's classes. The full_precision path replaces the
    article's two literal approximations with math.pi and math.sqrt(2), and
    expresses the cosine angle directly in radians. False preserves the printed
    coefficients for a regression comparison. Startup and averaging are equal.
    """
    blocks = re.findall(r"```easylanguage\n(.*?)```", ARTICLE.read_text(), flags=re.DOTALL)
    ci_block = next(block for block in blocks if "Variance = Average" in block)
    us_block = next(block for block in blocks if "Q = expvalue" in block)
    lag_block = next(block for block in blocks if "LG[count, 1] =" in block)
    coefficient_expressions = [
        (name, re.search(r"\b" + name + r"\s*=\s*(.*?);", us_block).group(1))
        for name in ("Q", "c1", "c2", "a0")
    ]
    if full_precision:
        # Make the explicitly requested coefficient changes in the independently
        # extracted expressions. The original recurrence and all other formulas
        # remain untouched. The master classes are never used by this oracle.
        coefficient_expressions = [
            (name, expression.replace("1.414", "SQRT_TWO").replace("3.14159", "PI")
             .replace("180", "PI"))
            for name, expression in coefficient_expressions
        ]
    us_expression = re.search(r"If CurrentBar >= 4 Then US = (.*?);", us_block, flags=re.DOTALL).group(1)
    us_expression = us_expression.replace("Price[1]", "price1").replace("Price[2]", "price2")
    us_expression = us_expression.replace("US[1]", "us1").replace("US[2]", "us2")
    us_expression = " ".join(us_expression.split())
    lag_expression = re.search(r"LG\[count, 1\] = (.*?);", lag_block, flags=re.DOTALL).group(1)
    lag_expression = lag_expression.replace("LG[count - 1, 2]", "previous_preceding")
    lag_expression = lag_expression.replace("LG[count, 2]", "previous_own")
    lag_expression = " ".join(lag_expression.split())
    ref_expression = re.search(r"Then Ref = (.*?);", ci_block).group(1)
    ci_expression = re.search(r"\bCI = (.*?);", ci_block).group(1)

    # Original EasyLanguage Cosine takes degrees; the full-precision coefficient
    # expressions above replace 180 with pi, so that path now uses radians.
    functions = {"expvalue": math.exp, "ExpValue": math.exp,
                 "Cosine": math.cos if full_precision else lambda angle: math.cos(math.radians(angle))}

    def evaluate(expression, values):
        return eval(expression, {"__builtins__": {}}, functions | values)

    def smoother(period):
        values = {"Period": period, "PI": math.pi, "SQRT_TWO": math.sqrt(2.0)}
        for name, expression in coefficient_expressions:
            values[name] = evaluate(expression, values)
        outputs = []
        for t, price in enumerate(close):
            if t < 3:
                outputs.append(price)
            else:
                values.update(Price=price, price1=close[t-1], price2=close[t-2],
                              us1=outputs[t-1], us2=outputs[t-2])
                outputs.append(evaluate(us_expression, values))
        return outputs

    fast = smoother(length / 2.0)
    full = smoother(length)
    previous = [0.0] * order
    slow = []
    for t in range(len(close)):
        current = [full[t]]
        for j in range(1, order):
            current.append(evaluate(lag_expression, {
                "gama": gama, "previous_preceding": previous[j-1], "previous_own": previous[j]
            }))
        total = 0.0
        for component in current:
            total += component
        slow.append(total / order)
        previous = current

    # The list-based oracle and master's wrapped ring use different storage.
    # Summation follows the same explicit newest-to-oldest addition order.
    magnitudes = [abs(u-l) for u, l in zip(fast, slow)]
    ref = 0.0
    outputs = []
    for t in range(len(close)):
        if t < length - 1:
            outputs.append(math.nan)
            continue
        total = 0.0
        for k in range(length):
            total += magnitudes[t-k]
        variance = total / length
        if variance != 0.0:
            ref = evaluate(ref_expression, {"US": fast[t], "LG": slow[t], "Variance": variance})
        # Original expression is intentionally used in this oracle. The
        # confirmed real-price fixtures stay in its finite exponential domain.
        outputs.append(evaluate(ci_expression, {"Ref": ref}))
    return outputs


class ContinuationIndexTests(unittest.TestCase):
    def assert_same_floats(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for index, (left, right) in enumerate(zip(actual, expected)):
            with self.subTest(index=index):
                if math.isnan(right):
                    self.assertTrue(math.isnan(left))
                else:
                    self.assertEqual(left, right)

    def test_matches_full_precision_article_expressions_for_all_confirmed_cases(self):
        self.assertEqual(len(INPUT_CLOSE), 252)
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(gama=case.gama, order=case.order, length=case.length):
                expected = article_batch(INPUT_CLOSE, case.gama, case.order, case.length)
                indicator = MASTER.ContinuationIndex(case.gama, case.order, case.length)
                actual = [indicator.update(price) for price in INPUT_CLOSE]
                self.assert_same_floats(actual, expected)

    def test_full_precision_changes_values_from_printed_constants(self):
        # A reversion to either printed approximation must no longer pass the
        # master reference checks. Both paths evaluate the same source formulas.
        full = article_batch(INPUT_CLOSE, gama=0.8, order=8, length=40)
        printed = article_batch(INPUT_CLOSE, gama=0.8, order=8, length=40, full_precision=False)
        self.assertTrue(any(left != right for left, right in zip(full[39:], printed[39:])))

    def test_exact_priming_for_every_case(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.ContinuationIndex(case.gama, case.order, case.length)
            self.assertFalse(indicator.is_primed)
            self.assertEqual(indicator.warmup_bars, case.length - 1)
            for t, price in enumerate(INPUT_CLOSE):
                value = indicator.update(price)
                self.assertEqual(math.isnan(value), t < case.length - 1)
                self.assertEqual(indicator.is_primed, t >= case.length - 1)

    def test_causal_prefix_ignores_future_changes(self):
        # A centered convolution would change earlier values after replacing
        # the future tail. A trailing online implementation must not do so.
        original = MASTER.ContinuationIndex()
        changed = MASTER.ContinuationIndex()
        tail_changed = INPUT_CLOSE[:100] + [10000.0] * 152
        a = [original.update(value) for value in INPUT_CLOSE]
        b = [changed.update(value) for value in tail_changed]
        self.assert_same_floats(a[:100], b[:100])
        prefix = MASTER.ContinuationIndex()
        self.assert_same_floats(a[:100], [prefix.update(value) for value in INPUT_CLOSE[:100]])

    def test_gamma_zero_is_delayed_fir_not_passthrough(self):
        laguerre = MASTER.LaguerreFilter(gama=0.0, order=4, length=40)
        smoother = MASTER.UltimateSmoother(40)
        history = []
        for value in INPUT_CLOSE:
            history.append(smoother.update(value))
            # Missing pre-stream stage values are zero, not first-price seeds.
            expected = sum(reversed(history[-4:])) / 4.0
            self.assertAlmostEqual(laguerre.update(value), expected, places=12)
        fresh = MASTER.LaguerreFilter(gama=0.0, order=4, length=40)
        self.assertEqual(fresh.update(100.0), 25.0)

    def test_order_one_reduces_to_full_length_smoother(self):
        for gama in (0.0, 0.4, 0.8, 0.999):
            laguerre = MASTER.LaguerreFilter(gama=gama, order=1, length=40)
            smoother = MASTER.UltimateSmoother(40)
            self.assertEqual([laguerre.update(value) for value in INPUT_CLOSE],
                             [smoother.update(value) for value in INPUT_CLOSE])

    def test_odd_length_uses_fractional_half_period(self):
        indicator = MASTER.ContinuationIndex(length=21)
        self.assertEqual(indicator._fast.period, 10.5)
        odd = [indicator.update(value) for value in INPUT_CLOSE]
        # Replacing the internal fast period with the truncated platform
        # variant must measurably change the post-warmup outputs.
        truncated = MASTER.ContinuationIndex(length=21)
        truncated._fast = MASTER.UltimateSmoother(10)
        other = [truncated.update(value) for value in INPUT_CLOSE]
        self.assertTrue(any(a != b for a, b in zip(odd[20:], other[20:])))

    def test_zero_denominator_retains_reference(self):
        indicator = MASTER.ContinuationIndex(gama=0, order=1, length=2)
        # A zero stream gives exactly zero filter differences and mean.
        self.assertTrue(math.isnan(indicator.update(0.0)))
        self.assertEqual(indicator.update(0.0), 0.0)
        # Give the held reference a nonzero value to verify the source's
        # absent 'else' even when the current zero stream carries no signal.
        indicator._ref = 0.5
        self.assertEqual(indicator.update(0.0), MASTER.inverse_fisher(0.5))

    def test_inverse_fisher_bounds_and_overflow(self):
        for ref in (-1000, -100, -1, 0, 1, 100, 1000):
            value = MASTER.inverse_fisher(ref)
            self.assertTrue(math.isfinite(value))
            self.assertGreaterEqual(value, -1.0)
            self.assertLessEqual(value, 1.0)
            self.assertAlmostEqual(value, math.tanh(ref), places=15)
        # A long window with all-zero input until the last bar drives the
        # reference to 2*length. The original exponential would overflow.
        indicator = MASTER.ContinuationIndex(gama=0.8, order=8, length=252)
        for _ in range(251):
            self.assertTrue(math.isnan(indicator.update(0.0)))
        self.assertEqual(indicator.update(100.0), 1.0)

    def test_reset_and_invalid_inputs(self):
        indicator = MASTER.ContinuationIndex()
        first = [indicator.update(value) for value in INPUT_CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assert_same_floats(first, [indicator.update(value) for value in INPUT_CLOSE])
        twin = MASTER.ContinuationIndex()
        indicator.reset()
        for value in INPUT_CLOSE[:30]:
            indicator.update(value)
            twin.update(value)
        for invalid in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(invalid)
        self.assert_same_floats([indicator.update(value) for value in INPUT_CLOSE[30:]],
                                [twin.update(value) for value in INPUT_CLOSE[30:]])

    def test_invalid_parameters(self):
        for gama in (-0.1, 1.0, 1.1, math.nan, math.inf):
            with self.subTest(gama=gama), self.assertRaises(ValueError):
                MASTER.ContinuationIndex(gama=gama)
        for order in (0, 11, 4.5, 4.0, True):
            with self.subTest(order=order), self.assertRaises(ValueError):
                MASTER.ContinuationIndex(order=order)
        for length in (0, -1, 20.5, 20.0, True):
            with self.subTest(length=length), self.assertRaises(ValueError):
                MASTER.ContinuationIndex(length=length)
        for period in (0, -1, math.nan, math.inf):
            with self.subTest(period=period), self.assertRaises(ValueError):
                MASTER.UltimateSmoother(period=period)

    def test_length_one_primes_on_first_sample(self):
        indicator = MASTER.ContinuationIndex(length=1)
        self.assertEqual(indicator.warmup_bars, 0)
        self.assertTrue(math.isfinite(indicator.update(100.0)))
        self.assertTrue(indicator.is_primed)

    def test_input_preservation_and_embedded_main_array(self):
        copied = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        source = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        for name in ("INPUT_CLOSE", "INPUT_HIGH", "INPUT_LOW", "INPUT_OPEN"):
            self.assertEqual(len(copied[name]), 252)
            self.assertEqual(copied[name], source[name])
        parsed = ast.parse((DIRECTORY / "continuation-index.py").read_text())
        assignment = next(node for node in ast.walk(parsed)
                          if isinstance(node, ast.Assign) and any(
                              isinstance(target, ast.Name) and target.id == "INPUT_CLOSE"
                              for target in node.targets))
        self.assertEqual(ast.literal_eval(assignment.value), INPUT_CLOSE)

    def test_generated_fixtures(self):
        arrays = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        names = {name for name in arrays if name.startswith("EXPECTED_")}
        self.assertEqual(names, {"EXPECTED_" + MASTER._case_suffix(case) for case in MASTER.REFERENCE_CASES})
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.ContinuationIndex(case.gama, case.order, case.length)
            values = arrays["EXPECTED_" + MASTER._case_suffix(case)]
            self.assertEqual(len(values), 252)
            for t, (price, expected) in enumerate(zip(INPUT_CLOSE, values)):
                actual = indicator.update(price)
                self.assertEqual(math.isnan(expected), t < case.length - 1)
                if not math.isnan(expected):
                    self.assertTrue(math.isclose(actual, expected, rel_tol=5e-13, abs_tol=5e-14))

    def test_translated_fixtures(self):
        arrays = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        patterns = {
            "testdata_test.go": (r"var expected(\w+) = \[\]float64\{\s*(.*?)\n\}", "math.NaN()"),
            "testdata.ts": (r"export const expected(\w+): number\[\] = \[\s*(.*?)\n\];", "NaN"),
            "testdata.rs": (r"pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[\s*(.*?)\n\s*\]\s*\}", "f64::NAN"),
            "testdata.zig": (r"pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{\s*(.*?)\n\s*\};\s*\}", "nan"),
        }
        for filename, (pattern, nan_literal) in patterns.items():
            with self.subTest(filename=filename):
                text = (DIRECTORY / filename).read_text()
                matches = re.findall(pattern, text, flags=re.DOTALL)
                self.assertEqual(len(matches), len(MASTER.REFERENCE_CASES))
                translated = dict(matches)
                self.assertEqual(len(translated), len(matches))
                for case in MASTER.REFERENCE_CASES:
                    suffix = MASTER._case_suffix(case)
                    identifier = suffix.lower() if filename.endswith(".rs") else suffix
                    tokens = [token.strip() for token in translated[identifier].split(",") if token.strip()]
                    values = [math.nan if token == nan_literal else float(token) for token in tokens]
                    self.assert_same_floats(values, arrays["EXPECTED_" + suffix])
                    comments = (
                        f"// {case.what_it_tests}\n"
                        f"// gama={case.gama:g}, order={case.order}, length={case.length}\n"
                    )
                    self.assertIn(comments, text)


if __name__ == "__main__":
    unittest.main()
