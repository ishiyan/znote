"""Independent source equations, analytical properties and fixture checks.

The source oracle extracts EasyLanguage expressions, substitutes the requested
full-precision pi/sqrt(2), and evaluates independent chronological histories.
Fixture checks verify all confirmed reference cases in the five language files.
"""

import ast
import cmath
import contextlib
import importlib.util
import io
import math
from pathlib import Path
import re
import tempfile
import unittest

DIRECTORY = Path(__file__).resolve().parent
INDICATOR_NAME = "trendflex"
CLASS_NAME = "Trendflex"
SPEC = importlib.util.spec_from_file_location("flex_master", DIRECTORY / (INDICATOR_NAME + ".py"))
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INDICATOR = getattr(MASTER, CLASS_NAME)
INPUTS = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
CLOSE = INPUTS["INPUT_CLOSE"]
SOURCE_FILE = DIRECTORY.parent.parent / "tasc/2020-02-reflex-a-new-zero-lag-ndicator/tips/ReflexTrendFlex.els"
SOURCE_ALL = SOURCE_FILE.read_text()
SOURCE = (SOURCE_ALL.split("Function: _TrendFlex")[0] if INDICATOR_NAME == "reflex"
          else SOURCE_ALL.split("Function: _TrendFlex")[1].split("Indicator:")[0])
FIXTURES = ("test_testdata.py", "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig")


def assignment(name):
    """First assignment to a source variable; declarations have no equals."""
    value = re.search(r"\b" + name + r"\s*=\s*(.*?);", SOURCE, re.I | re.S).group(1)
    return " ".join(value.split())


def source_batch(prices, length, full_precision=True):
    """Evaluate source arithmetic with explicitly documented fresh-history gate.

    No class methods or precomputed coefficients are used. Original printed
    constants can also be evaluated for measuring the requested substitution.
    The full-precision radian cosine preserves the master's specified order.
    """
    env = {"Length": length, "ExpValue": math.exp, "SquareRoot": math.sqrt,
           "Cosine": lambda degrees: math.cos(math.radians(degrees)),
           "PI": math.pi, "SQRT_TWO": math.sqrt(2.0), "CosRadians": math.cos}
    for name in ("a1", "b1", "c2", "c3", "c1"):
        expression = assignment(name)
        if full_precision:
            expression = expression.replace("1.414", "SQRT_TWO").replace("3.14159", "PI")
            # Degrees * pi/180 cancels mathematically; declare the intended
            # full-precision radian expression to preserve identical op order.
            if name == "b1":
                expression = "2 * a1 * CosRadians(SQRT_TWO * PI / (.5 * Length))"
        env[name] = eval(expression, {"__builtins__": {}}, env)
    filt_expression = assignment("Filt").replace("Close[1]", "price1").replace("Close", "price")
    filt_expression = filt_expression.replace("Filt[1]", "filt1").replace("Filt[2]", "filt2")
    accumulation = re.search(r"Sum\s*=\s*Sum\s*\+\s*(.*?);", SOURCE, re.I | re.S).group(1)
    accumulation = "Sum + " + " ".join(accumulation.split())
    mean_square_expression = assignment("MS").replace("MS[1]", "previous_ms")
    output_expression = assignment(CLASS_NAME)
    filts, outputs, raws, squares = [math.nan], [math.nan], [math.nan], [0.0]
    ms, stored = 0.0, 0.0
    for t in range(1, len(prices)):
        env.update(price=prices[t], price1=prices[t - 1],
                   filt1=filts[t - 1] if t > 1 else 0.0,
                   filt2=filts[t - 2] if t > 2 else 0.0)
        filt = eval(filt_expression, {"__builtins__": {}}, env)
        filts.append(filt)
        if t < length + 1:
            outputs.append(math.nan)
            raws.append(math.nan)
            squares.append(0.0)
            continue
        env.update(Filt=[filts[t - lag] for lag in range(length + 1)])
        if INDICATOR_NAME == "reflex":
            slope = assignment("Slope").replace(" - Filt )", " - Filt[0] )")
            env["Slope"] = eval(slope, {"__builtins__": {}}, env)
        # Replace unindexed current Filt while preserving Filt[count] history.
        summed_expression = re.sub(r"\bFilt\b(?!\[)", "Filt[0]", accumulation)
        env["Sum"] = 0.0
        for count in range(1, length + 1):
            env["count"] = count
            env["Sum"] = eval(summed_expression, {"__builtins__": {}}, env)
        env["Sum"] /= length
        env["previous_ms"] = ms
        ms = eval(mean_square_expression, {"__builtins__": {}}, env)
        env["MS"] = ms
        if ms != 0.0:
            stored = eval(output_expression, {"__builtins__": {}}, env)
        outputs.append(stored)
        raws.append(env["Sum"])
        squares.append(ms)
    return outputs, filts, raws, squares


def compare(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for index, (left, right) in enumerate(zip(actual, expected)):
        if math.isnan(right):
            test.assertTrue(math.isnan(left), (index, left, right))
        else:
            test.assertTrue(math.isfinite(left) and math.isclose(left, right,
                            rel_tol=tolerance, abs_tol=tolerance), (index, left, right))


def transfer(length, omega):
    """Independent complex response: raw oscillator BEFORE RMS normalization."""
    period = length / 2
    a = math.exp(-math.sqrt(2) * math.pi / period)
    c2 = 2 * a * math.cos(math.sqrt(2) * math.pi / period)
    c3 = -a * a
    c1 = 1 - c2 - c3
    z1 = cmath.exp(-1j * omega)
    smoother = c1 / 2 * (1 + z1) / (1 - c2 * z1 - c3 * z1**2)
    trend = 1 - sum(z1**k for k in range(1, length + 1)) / length
    reflex = trend + (length + 1) / (2 * length) * (z1**length - 1)
    return smoother, reflex if INDICATOR_NAME == "reflex" else trend


def language_expected(path):
    patterns = {
        ".go": r"var expectedL(\d+) = \[\]float64\{(.*?)\}",
        ".ts": r"export const expectedL(\d+): number\[\] = \[(.*?)\];",
        ".rs": r"pub fn expected_l(\d+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]\s*\}",
        ".zig": r"pub fn expectedL(\d+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\};\s*\}",
    }
    arrays = {}
    for length, body in re.findall(patterns[path.suffix], path.read_text(), re.S):
        arrays["EXPECTED_L" + length] = [math.nan if token.strip() in ("math.NaN()", "NaN", "f64::NAN", "nan")
                                         else float(token.strip()) for token in body.split(",") if token.strip()]
    return arrays


class FlexTests(unittest.TestCase):
    def test_all_confirmed_lengths_match_precision_substituted_source(self):
        for case in MASTER.REFERENCE_CASES:
            expected, filts, raws, squares = source_batch(CLOSE, case.length)
            indicator = INDICATOR(case.length)
            actual, actual_filts, actual_raws, actual_squares = [], [], [], []
            for value in CLOSE:
                actual.append(indicator.update(value))
                actual_filts.append(indicator.state.filtered)
                actual_raws.append(indicator.state.raw_average)
                actual_squares.append(indicator.state.mean_square)
            compare(self, actual, expected, 0)
            compare(self, actual_filts, filts, 0)
            compare(self, actual_raws, raws, 0)
            compare(self, actual_squares, squares, 0)

    def test_user_requested_full_precision_constants(self):
        self.assertEqual(MASTER.PI, math.pi)
        self.assertEqual(MASTER.SQRT_TWO, math.sqrt(2.0))
        indicator = INDICATOR(20)
        self.assertEqual(indicator._a1, math.exp(-math.sqrt(2.0) * math.pi / 10))
        exact = source_batch(CLOSE, 20)[0]
        printed = source_batch(CLOSE, 20, full_precision=False)[0]
        self.assertGreater(max(abs(a - b) for a, b in zip(exact[21:], printed[21:])), 1e-5)

    def test_full_filtered_history_warmup_and_record_boundary(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = INDICATOR(case.length)
            self.assertEqual(indicator.warmup_bars, case.length + 1)
            for t, value in enumerate(CLOSE):
                output = indicator.update(value)
                self.assertEqual(math.isnan(output), t <= case.length)
                self.assertEqual(indicator.is_primed, t > case.length)
                self.assertEqual(len(indicator._filtered), min(t, case.length + 1))
                if t <= case.length:
                    self.assertEqual(indicator._ms, 0.0)
                if t == case.length + 1:
                    self.assertAlmostEqual(abs(output), 5.0, places=13)
        boundary = INDICATOR(251)
        self.assertTrue(all(math.isnan(boundary.update(value)) for value in CLOSE))
        self.assertTrue(math.isfinite(boundary.update(CLOSE[-1])))

    def test_smoother_poles_dc_and_nyquist(self):
        for n in (1, 2, 3, 10, 20, 126, 251):
            indicator = INDICATOR(n)
            self.assertGreater(indicator._a1, 0)
            self.assertLess(indicator._a1, 1)
            self.assertAlmostEqual(indicator._c1 + indicator._c2 + indicator._c3, 1.0, places=15)
            self.assertAlmostEqual(abs(transfer(n, 0)[0]), 1.0, places=12)
            self.assertLess(abs(transfer(n, math.pi)[0]), 1e-12)

    def test_sinusoidal_raw_transfer_and_matched_cycle_geometry(self):
        for n in (8, 20, 30):
            for cycle in (.8 * n, n, 1.2 * n):
                omega = 2 * math.pi / cycle
                hs, hg = transfer(n, omega)
                indicator = INDICATOR(n)
                for t in range(1000):
                    indicator.update(math.sin(omega * t))
                    if t >= 900:
                        wave = cmath.exp(1j * omega * t)
                        self.assertAlmostEqual(indicator.state.filtered, (hs * wave).imag, places=11)
                        self.assertAlmostEqual(indicator.state.raw_average, (hs * hg * wave).imag, places=10)
            hs, hg = transfer(n, 2 * math.pi / n)
            self.assertAlmostEqual(hg.real, 1.0, places=13)
            self.assertAlmostEqual(hg.imag, 0.0, places=13)
            # Zero lag applies to the matched-cycle GEOMETRY relative to Filt.
            # The source SuperSmoother still has a nonzero phase lag from Close.
            self.assertLess(cmath.phase(hs), 0.0)

    def test_linear_trend_removal_or_retention_after_settling(self):
        n = 20
        indicator = INDICATOR(n)
        for t in range(300):
            output = indicator.update(100 + 2 * t)
        if INDICATOR_NAME == "reflex":
            self.assertLess(abs(indicator.state.raw_average), 1e-11)
        else:
            self.assertAlmostEqual(indicator.state.raw_average, 2 * (n + 1) / 2, places=11)
            self.assertAlmostEqual(output, 1.0, places=4)

    def test_zero_inputs_and_source_mean_square_guard(self):
        indicator = INDICATOR(20)
        for t in range(100):
            output = indicator.update(0.0)
            if t >= 21:
                self.assertEqual(output, 0.0)
                self.assertEqual(indicator._ms, 0.0)
        # Isolate the literal zero-denominator guard after a primed flat zero
        # history: an existing persistent output is retained, not reset to zero.
        indicator._last_output = 1.25
        self.assertEqual(indicator.update(0.0), 1.25)

    def test_scale_reflection_and_constant_price_startup(self):
        base = INDICATOR(20)
        expected = [base.update(value) for value in CLOSE]
        for factor in (8, .5, -1):
            transformed = INDICATOR(20)
            actual = [transformed.update(factor * value) for value in CLOSE]
            compare(self, actual, [value * (1 if factor > 0 else -1) for value in expected], 0)
        # Zero-seeded price smoothing is NOT translation invariant at startup.
        flat = INDICATOR(20)
        values = [flat.update(42) for _ in range(100)]
        self.assertGreater(abs(values[21]), 4.99)
        self.assertLess(abs(flat.state.raw_average), 1e-11)

    def test_reset_prefix_causality_and_invalid_update_state(self):
        indicator = INDICATOR(20)
        expected = [indicator.update(value) for value in CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        compare(self, [indicator.update(value) for value in CLOSE], expected, 0)
        fresh = INDICATOR(20)
        compare(self, [fresh.update(value) for value in CLOSE[:80]], expected[:80], 0)
        state = (indicator._previous_price, indicator._filt1, indicator._filt2,
                 indicator._filtered[:], indicator._ms, indicator._last_output, indicator.state)
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(value)
            self.assertEqual((indicator._previous_price, indicator._filt1, indicator._filt2,
                              indicator._filtered, indicator._ms, indicator._last_output, indicator.state), state)
        extreme = INDICATOR(2)
        extreme.update(1e308)
        with self.assertRaises(ValueError):
            extreme.update(1e308)
        self.assertEqual(extreme._previous_price, 1e308)
        self.assertEqual(extreme._filtered, [])

    def test_parameter_validation(self):
        for n in (0, -1, True, False, 20.0, "20", None):
            with self.assertRaises(ValueError):
                INDICATOR(n)
        # Length 1 is permitted and explicitly documented; geometry differs
        # between the indicators, so it is not part of their shared fixture set.
        one = INDICATOR(1)
        self.assertEqual(one.warmup_bars, 2)

    def test_embedded_and_copied_inputs(self):
        parent = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        self.assertEqual({name: INPUTS[name] for name in parent}, parent)
        self.assertEqual(len(CLOSE), 252)
        tree = ast.parse((DIRECTORY / (INDICATOR_NAME + ".py")).read_text())
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "INPUT_CLOSE" for target in node.targets))
        self.assertEqual(ast.literal_eval(node.value), CLOSE)
        for filename in FIXTURES[1:]:
            before, after = (DIRECTORY.parent / filename).read_text(), (DIRECTORY / filename).read_text()
            if filename.endswith(".go"):
                before = before.replace("package xxxx", "package " + INDICATOR_NAME, 1)
                after = after.replace('import "math"\n\n', "", 1)
            if filename.endswith(".rs"):
                before = before[:before.rfind("}")].rstrip()
            self.assertTrue(after.startswith(before.rstrip()), filename)

    def test_expected_reference_arrays_and_language_values(self):
        names = {"EXPECTED_L" + str(case.length) for case in MASTER.REFERENCE_CASES}
        self.assertEqual({name for name in INPUTS if name.startswith("EXPECTED_")}, names)
        for case in MASTER.REFERENCE_CASES:
            values = INPUTS["EXPECTED_L" + str(case.length)]
            compare(self, values, source_batch(CLOSE, case.length)[0])
            self.assertEqual(len(values), 252)
            self.assertEqual(sum(math.isnan(value) for value in values), case.length + 1)
            for filename in FIXTURES:
                prefix = "#" if filename.endswith(".py") else "//"
                comments = f"{prefix} {case.what_it_tests}\n{prefix} length={case.length}\n"
                self.assertIn(comments, (DIRECTORY / filename).read_text())
        for filename in FIXTURES[1:]:
            native = language_expected(DIRECTORY / filename)
            self.assertEqual(set(native), names)
            for name, values in native.items():
                compare(self, values, INPUTS[name], 0)

    def test_repeatable_generation_and_preserved_language_inputs(self):
        with tempfile.TemporaryDirectory(prefix=INDICATOR_NAME + "-fixtures-") as temporary:
            directory = Path(temporary)
            for filename in FIXTURES:
                (directory / filename).write_text((DIRECTORY.parent / filename).read_text())
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, directory)
                first = {filename: (directory / filename).read_bytes() for filename in FIXTURES}
                MASTER.generate_reference_data(CLOSE, directory)
            self.assertEqual(first, {filename: (directory / filename).read_bytes() for filename in FIXTURES})
            arrays = MASTER._load_literal_arrays(directory / "test_testdata.py")
            for filename in FIXTURES[1:]:
                for name, values in language_expected(directory / filename).items():
                    compare(self, values, arrays[name], 0)


if __name__ == "__main__":
    unittest.main()
