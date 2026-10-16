"""Meaningful verification of the full-precision Ultimate Smoother reference.

Tests use only standard Python. All twelve periods have been confirmed, so
missing expected arrays or any inconsistent language fixtures are failures.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest


DIRECTORY = Path(__file__).resolve().parent
ARTICLE = DIRECTORY.parent.parent / "tasc" / "2024-04-the-ultimate-smoother" / "content.md"
SPEC = importlib.util.spec_from_file_location("ultimate_smoother_master", DIRECTORY / "ultimate-smoother.py")
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUT_CLOSE = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")["INPUT_CLOSE"]


def article_batch(prices, period, full_precision=True):
    """Independent batch evaluation of the actual article's expressions.

    The article is not imported or executed as a program. Only its coefficient
    assignments and US recurrence are extracted. The selected precision policy
    explicitly substitutes sqrt(2) and pi, and converts the cosine to radians.
    full_precision=False evaluates the original printed coefficients instead.
    """
    blocks = re.findall(r"```easylanguage\n(.*?)```", ARTICLE.read_text(), flags=re.DOTALL)
    block = next(block for block in blocks if "UltimateSmoother Function" in block)
    coefficients = [
        (name, re.search(r"\b" + name + r"\s*=\s*(.*?);", block).group(1))
        for name in ("a1", "b1", "c2", "c3", "c1")
    ]
    if full_precision:
        # Only the coefficient constants and cosine units change. All arithmetic
        # in the recursively extracted source expression stays untouched.
        coefficients = [(name, expression.replace("1.414", "SQRT_TWO")
                         .replace("3.14159", "PI").replace("180", "PI"))
                        for name, expression in coefficients]
    recurrence = re.search(r"If CurrentBar >= 4 Then US = (.*?);", block, flags=re.DOTALL).group(1)
    recurrence = recurrence.replace("Price[1]", "price1").replace("Price[2]", "price2")
    recurrence = recurrence.replace("US[1]", "us1").replace("US[2]", "us2")
    recurrence = " ".join(recurrence.split())
    functions = {
        "expvalue": math.exp,
        "Cosine": math.cos if full_precision else lambda angle: math.cos(math.radians(angle)),
    }
    values = {"Period": period, "PI": math.pi, "SQRT_TWO": math.sqrt(2.0)}
    for name, expression in coefficients:
        values[name] = eval(expression, {"__builtins__": {}}, functions | values)
    outputs = []
    for t, price in enumerate(prices):
        if t < 3:
            outputs.append(price)
        else:
            values.update(Price=price, price1=prices[t-1], price2=prices[t-2],
                          us1=outputs[t-1], us2=outputs[t-2])
            outputs.append(eval(recurrence, {"__builtins__": {}}, values))
    return outputs


class UltimateSmootherTests(unittest.TestCase):
    def test_matches_full_precision_article_for_all_confirmed_periods(self):
        self.assertEqual(len(INPUT_CLOSE), 252)
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(period=case.period):
                expected = article_batch(INPUT_CLOSE, case.period)
                indicator = MASTER.UltimateSmoother(case.period)
                actual = [indicator.update(price) for price in INPUT_CLOSE]
                self.assertEqual(actual, expected)
                self.assertTrue(all(math.isfinite(value) for value in actual))

    def test_first_three_outputs_are_valid_passthrough(self):
        indicator = MASTER.UltimateSmoother()
        self.assertFalse(indicator.is_primed)
        self.assertEqual(indicator.warmup_bars, 0)
        for price in INPUT_CLOSE[:3]:
            self.assertEqual(indicator.update(price), price)
            self.assertTrue(indicator.is_primed)
        # The fourth sample is the first recursion, rather than another seed.
        self.assertNotEqual(indicator.update(INPUT_CLOSE[3]), INPUT_CLOSE[3])

    def test_zero_is_a_valid_initial_input(self):
        indicator = MASTER.UltimateSmoother()
        self.assertEqual(indicator.update(0.0), 0.0)
        self.assertTrue(indicator.is_primed)
        self.assertEqual(indicator.update(-1.0), -1.0)

    def test_constant_preservation(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.UltimateSmoother(case.period)
            for _ in range(252):
                self.assertTrue(math.isclose(indicator.update(25.0), 25.0, rel_tol=1e-11, abs_tol=1e-11))

    def test_ramp_preservation(self):
        # The highpass's double DC zero annihilates a linear ramp. This oracle
        # uses the ramp itself rather than a second implementation of the loop.
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.UltimateSmoother(case.period)
            for t in range(252):
                price = 10.0 + 0.75 * t
                self.assertAlmostEqual(indicator.update(price), price, places=8)

    def test_highpass_complement_matches_direct_form(self):
        # Independently compute the highpass and subtract it from raw price.
        # This exercises the design identity, with different state arithmetic.
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.UltimateSmoother(case.period)
            angle = math.sqrt(2.0) * math.pi / case.period
            q = math.exp(-angle)
            c2, c3 = 2.0 * q * math.cos(angle), -q*q
            c1 = (1.0 + c2 - c3) / 4.0
            hp = []
            for t, price in enumerate(INPUT_CLOSE):
                if t < 3:
                    hp.append(0.0)
                else:
                    hp.append(c1*(price-2*INPUT_CLOSE[t-1]+INPUT_CLOSE[t-2])
                              + c2*hp[t-1] + c3*hp[t-2])
                self.assertTrue(math.isclose(indicator.update(price), price-hp[t],
                                             rel_tol=5e-12, abs_tol=5e-12))

    def test_nyquist_alternation_decays(self):
        indicator = MASTER.UltimateSmoother(period=20)
        values = [indicator.update(1.0 if t % 2 == 0 else -1.0) for t in range(300)]
        self.assertLess(max(abs(value) for value in values[-50:]), 1e-12)

    def test_step_can_overshoot_and_is_not_clamped(self):
        indicator = MASTER.UltimateSmoother(period=20)
        for _ in range(3):
            indicator.update(0.0)
        values = [indicator.update(1.0) for _ in range(200)]
        self.assertGreater(max(values), 1.0)
        self.assertAlmostEqual(values[-1], 1.0, places=12)

    def test_causal_prefix_and_reset(self):
        indicator = MASTER.UltimateSmoother()
        full = [indicator.update(price) for price in INPUT_CLOSE]
        prefix = MASTER.UltimateSmoother()
        self.assertEqual(full[:101], [prefix.update(price) for price in INPUT_CLOSE[:101]])
        changed = MASTER.UltimateSmoother()
        other = [changed.update(price) for price in INPUT_CLOSE[:101] + [1000.0]*151]
        self.assertEqual(full[:101], other[:101])
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertEqual(full, [indicator.update(price) for price in INPUT_CLOSE])

    def test_fractional_period_and_full_precision_policy(self):
        fractional = article_batch(INPUT_CLOSE, period=10.5)
        truncated = article_batch(INPUT_CLOSE, period=10)
        self.assertNotEqual(fractional[3:], truncated[3:])
        full = article_batch(INPUT_CLOSE, period=20)
        literal = article_batch(INPUT_CLOSE, period=20, full_precision=False)
        self.assertNotEqual(full[3:], literal[3:])

    def test_invalid_parameters_and_input_preserve_state(self):
        for period in (0.0, 0.5, -1.0, math.nan, math.inf, -math.inf):
            with self.subTest(period=period), self.assertRaises(ValueError):
                MASTER.UltimateSmoother(period)
        indicator, twin = MASTER.UltimateSmoother(), MASTER.UltimateSmoother()
        for price in INPUT_CLOSE[:10]:
            self.assertEqual(indicator.update(price), twin.update(price))
        for price in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(price)
        self.assertEqual([indicator.update(price) for price in INPUT_CLOSE[10:]],
                         [twin.update(price) for price in INPUT_CLOSE[10:]])

    def test_nonfinite_output_does_not_commit_state(self):
        indicator = MASTER.UltimateSmoother()
        for price in (1e308, -1e308, 1e308):
            indicator.update(price)
        state = (indicator._count, indicator._price1, indicator._price2,
                 indicator._output1, indicator._output2)
        with self.assertRaises(ValueError):
            indicator.update(1e308)
        self.assertEqual(state, (indicator._count, indicator._price1, indicator._price2,
                                indicator._output1, indicator._output2))

    def test_input_preservation_and_embedded_array(self):
        copied = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        shared = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        for name in ("INPUT_CLOSE", "INPUT_HIGH", "INPUT_LOW", "INPUT_OPEN"):
            self.assertEqual(len(copied[name]), 252)
            self.assertEqual(copied[name], shared[name])
        parsed = ast.parse((DIRECTORY / "ultimate-smoother.py").read_text())
        assignment = next(node for node in ast.walk(parsed) if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == "INPUT_CLOSE"
                                  for target in node.targets))
        self.assertEqual(ast.literal_eval(assignment.value), INPUT_CLOSE)

    def test_generated_python_fixtures(self):
        arrays = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        names = {name for name in arrays if name.startswith("EXPECTED_")}
        self.assertEqual(names, {"EXPECTED_" + MASTER._case_suffix(case) for case in MASTER.REFERENCE_CASES})
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.UltimateSmoother(case.period)
            values = arrays["EXPECTED_" + MASTER._case_suffix(case)]
            self.assertEqual(len(values), 252)
            self.assertEqual(values[:3], INPUT_CLOSE[:3])
            for price, expected in zip(INPUT_CLOSE, values):
                self.assertTrue(math.isfinite(expected))
                self.assertTrue(math.isclose(indicator.update(price), expected, rel_tol=5e-13, abs_tol=5e-13))

    def test_translated_fixtures(self):
        arrays = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        patterns = {
            "testdata_test.go": r"var expected(\w+) = \[\]float64\{\s*(.*?)\n\}",
            "testdata.ts": r"export const expected(\w+): number\[\] = \[\s*(.*?)\n\];",
            "testdata.rs": r"pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[\s*(.*?)\n\s*\]\s*\}",
            "testdata.zig": r"pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{\s*(.*?)\n\s*\};\s*\}",
        }
        for filename, pattern in patterns.items():
            with self.subTest(filename=filename):
                text = (DIRECTORY / filename).read_text()
                matches = re.findall(pattern, text, flags=re.DOTALL)
                self.assertEqual(len(matches), len(MASTER.REFERENCE_CASES))
                translated = dict(matches)
                self.assertEqual(len(translated), len(matches))
                for case in MASTER.REFERENCE_CASES:
                    suffix = MASTER._case_suffix(case)
                    identifier = suffix.lower() if filename.endswith(".rs") else suffix
                    values = [float(token.strip()) for token in translated[identifier].split(",") if token.strip()]
                    self.assertEqual(values, arrays["EXPECTED_" + suffix])
                    self.assertIn(f"// {case.what_it_tests}\n// period={case.period:g}\n", text)


if __name__ == "__main__":
    unittest.main()
