"""Independent source-expression and analytical tests for the RSIH master.

The commercial trading platform is not required. The batch oracle extracts
the supplied EasyLanguage arithmetic rather than calling the streaming class.
The twelve cases have been confirmed and generated. Fixture checks require
all twelve arrays in every language and verify deterministic regeneration.
"""

import ast
import contextlib
import importlib.util
import io
import math
from pathlib import Path
import re
import tempfile
import unittest

DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("rsi_hann_master", DIRECTORY / "rsi-hann.py")
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
CLOSE = INPUTS["INPUT_CLOSE"]
SOURCE = (DIRECTORY.parent.parent / "tasc/2022-01-(yet-another)-improved-rsi/tips/code/RSIH.els").read_text()
FIXTURES = ("test_testdata.py", "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig")


def source_batch(prices, length):
    """Evaluate actual supplied source expressions against chronological prices.

    Explicit finite-record startup matches the master's contract. Warmup
    returns are masked, while MyRSI keeps its source-declared zero seed.
    Cosine uses the degree convention of the original EasyLanguage runtime.
    """
    up = re.search(r"if\s+([^;\r\n]*?)\s+then\s+CU\s*=\s*(.*?);", SOURCE, re.S | re.I)
    down = re.search(r"if\s+([^;\r\n]*?)\s+then\s+CD\s*=\s*(.*?);", SOURCE, re.S | re.I)
    ratio = re.search(r"MyRSI\s*=\s*(.*?);", SOURCE, re.S | re.I).group(1)
    expressions = [up.group(1), up.group(2), down.group(1), down.group(2), ratio]
    expressions = [compile(" ".join(expression.split()), "<supplied RSIH.els>", "eval")
                   for expression in expressions]
    result = 0.0
    outputs = []
    for t in range(len(prices)):
        if t < length:
            outputs.append(math.nan)
            continue
        # This full batch slice and reversed history are independent from
        # RsiHann's bounded state and precomputed coefficient list.
        env = {"RSILength": length, "Close": list(reversed(prices[:t + 1])),
               "Cosine": lambda degrees: math.cos(math.radians(degrees)),
               "CU": 0.0, "CD": 0.0}
        for count in range(1, length + 1):
            env["count"] = count
            if eval(expressions[0], {"__builtins__": {}}, env):
                env["CU"] = eval(expressions[1], {"__builtins__": {}}, env)
            if eval(expressions[2], {"__builtins__": {}}, env):
                env["CD"] = eval(expressions[3], {"__builtins__": {}}, env)
        if env["CU"] + env["CD"] != 0.0:
            result = eval(expressions[4], {"__builtins__": {}}, env)
        outputs.append(result)
    return outputs


def compare(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for index, (left, right) in enumerate(zip(actual, expected)):
        if math.isnan(right):
            test.assertTrue(math.isnan(left), (index, left, right))
        else:
            test.assertTrue(math.isfinite(left) and math.isclose(left, right,
                            rel_tol=tolerance, abs_tol=tolerance), (index, left, right))


def language_expected(path):
    """Read the restricted numeric expected-array syntax, never execute it."""
    patterns = {
        ".go": r"var expectedL(\d+) = \[\]float64\{(.*?)\}",
        ".ts": r"export const expectedL(\d+): number\[\] = \[(.*?)\];",
        ".rs": r"pub fn expected_l(\d+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]\s*\}",
        ".zig": r"pub fn expectedL(\d+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\};\s*\}",
    }
    arrays = {}
    for length, body in re.findall(patterns[path.suffix], path.read_text(), re.S):
        values = [math.nan if token.strip() in ("math.NaN()", "NaN", "f64::NAN", "nan")
                  else float(token.strip()) for token in body.split(",") if token.strip()]
        arrays[f"EXPECTED_L{length}"] = values
    return arrays


HAS_EXPECTED = any(name.startswith("EXPECTED_") for name in INPUTS)


class RsiHannTests(unittest.TestCase):
    def test_every_confirmed_length_matches_supplied_easylanguage(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.RsiHann(case.length)
            actual = [indicator.update(value) for value in CLOSE]
            compare(self, actual, source_batch(CLOSE, case.length), tolerance=0)
            self.assertTrue(all(-1 <= value <= 1 for value in actual if not math.isnan(value)))

    def test_history_availability_and_record_boundaries(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.RsiHann(case.length)
            self.assertEqual(indicator.warmup_bars, case.length)
            for t, value in enumerate(CLOSE):
                output = indicator.update(value)
                self.assertEqual(math.isnan(output), t < case.length)
                self.assertEqual(indicator.is_primed, t >= case.length)
                self.assertEqual(len(indicator._prices), min(t + 1, case.length + 1))
        longest = MASTER.RsiHann(252)
        self.assertTrue(all(math.isnan(longest.update(value)) for value in CLOSE))
        self.assertTrue(math.isfinite(longest.update(CLOSE[-1])))

    def test_interior_hann_kernel_and_component_delay(self):
        for n in (1, 2, 3, 5, 14, 126, 252):
            weights = MASTER.RsiHann(n)._weights
            self.assertEqual(len(weights), n)
            self.assertGreater(min(weights), 0.0)
            self.assertAlmostEqual(sum(weights), n + 1, places=11)
            for c, weight in enumerate(weights, 1):
                self.assertAlmostEqual(weight, 2 * math.sin(math.pi * c / (n + 1))**2, places=14)
                self.assertAlmostEqual(weight, weights[-c], places=13)
            center = sum(k * w for k, w in enumerate(weights)) / sum(weights)
            self.assertAlmostEqual(center, (n - 1) / 2, places=12)
        self.assertEqual(MASTER.RsiHann(1)._weights, [2.0])

    def test_hand_calculated_mixed_changes_and_inclusive_final_tap(self):
        # N=3 gives [1,2,1]. Newest changes are +3, -1, +2:
        # CU=3+2=5, CD=2, ratio=(5-2)/(5+2)=3/7.
        indicator = MASTER.RsiHann(3)
        values = [indicator.update(value) for value in (10, 12, 11, 14)]
        self.assertTrue(all(math.isnan(value) for value in values[:3]))
        self.assertAlmostEqual(values[-1], 3 / 7, places=15)
        # Dropping the oldest tap, as the supplied C snippet does, gives 1/5.
        self.assertNotAlmostEqual(values[-1], 1 / 5, places=12)

    def test_flat_startup_and_flat_window_persistence_after_a_trend(self):
        for n in (1, 3, 14):
            flat = MASTER.RsiHann(n)
            output = [flat.update(42) for _ in range(n + 10)]
            self.assertTrue(all(math.isnan(value) for value in output[:n]))
            self.assertEqual(output[n:], [0.0] * 10)
            for direction in (-1, 1):
                indicator = MASTER.RsiHann(n)
                prices = [100 + direction * t for t in range(n + 1)]
                prices.extend([prices[-1]] * (n + 5))
                actual = [indicator.update(value) for value in prices]
                self.assertEqual(actual[n:], [float(direction)] * (n + 6))
                compare(self, actual, source_batch(prices, n), tolerance=0)
        # The shared record includes equal closes. N=1 preserves the previous
        # sign on every equal close instead of resetting the ratio to zero.
        indicator = MASTER.RsiHann(1)
        previous = math.nan
        for t, price in enumerate(CLOSE):
            actual = indicator.update(price)
            if t > 0 and price == CLOSE[t - 1]:
                self.assertEqual(actual, previous)
            previous = actual

    def test_translation_scaling_and_sign_reflection(self):
        baseline = MASTER.RsiHann(14)
        outputs = [baseline.update(value) for value in CLOSE]
        for offset, scale in ((1024, 1), (0, 8), (-200, 0.5)):
            transformed = MASTER.RsiHann(14)
            compare(self, [transformed.update(offset + scale * value) for value in CLOSE], outputs)
        reflected = MASTER.RsiHann(14)
        compare(self, [reflected.update(-value) for value in CLOSE], [-value for value in outputs], tolerance=0)

    def test_reset_and_causal_replay(self):
        indicator = MASTER.RsiHann(14)
        outputs = [indicator.update(value) for value in CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertEqual(indicator._last_output, 0.0)
        compare(self, [indicator.update(value) for value in CLOSE], outputs, tolerance=0)
        prefix = MASTER.RsiHann(14)
        compare(self, [prefix.update(value) for value in CLOSE[:80]], outputs[:80], tolerance=0)

    def test_invalid_parameters_and_rejected_updates_preserve_state(self):
        for length in (0, -1, 1.5, "14", True, False, None):
            with self.assertRaises(ValueError):
                MASTER.RsiHann(length)
        indicator = MASTER.RsiHann(3)
        for value in (10, 12, 11, 14):
            indicator.update(value)
        snapshot = (indicator._prices[:], indicator._last_output)
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(value)
            self.assertEqual((indicator._prices, indicator._last_output), snapshot)
        valid = indicator.update(13)
        self.assertEqual(valid, source_batch([10, 12, 11, 14, 13], 3)[-1])
        # Individually finite prices can still overflow their subtraction.
        # Reject that pair even while a long window is collecting history.
        for n in (1, 14):
            overflowing = MASTER.RsiHann(n)
            overflowing.update(-1e308)
            with self.assertRaises(ValueError):
                overflowing.update(1e308)
            self.assertEqual(overflowing._prices, [-1e308])
            self.assertEqual(overflowing._last_output, 0.0)
        # Differences can be finite while weighting/accumulation overflows.
        overflowing = MASTER.RsiHann(3)
        for value in (0, 1e308, 0):
            overflowing.update(value)
        with self.assertRaises(ValueError):
            overflowing.update(1e308)
        self.assertEqual(overflowing._prices, [0.0, 1e308, 0.0])

    def test_embedded_and_copied_inputs_remain_identical(self):
        parent_inputs = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        self.assertEqual({name: INPUTS[name] for name in parent_inputs}, parent_inputs)
        self.assertEqual(len(CLOSE), 252)
        tree = ast.parse((DIRECTORY / "rsi-hann.py").read_text())
        embedded = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "INPUT_CLOSE"
                                for target in node.targets))
        self.assertEqual(ast.literal_eval(embedded.value), CLOSE)
        for filename in FIXTURES[1:]:
            before = (DIRECTORY.parent / filename).read_text()
            after = (DIRECTORY / filename).read_text()
            if filename.endswith(".go"):
                before = before.replace("package xxxx", "package rsihann", 1)
                after = after.replace('import "math"\n\n', "", 1)
            if filename.endswith(".rs") and HAS_EXPECTED:
                # Expected functions are inserted before the final module brace.
                before = before[:before.rfind("}")].rstrip()
            self.assertTrue(after.startswith(before.rstrip()), filename)

    def test_generated_fixtures_match_source_and_language_literals(self):
        expected_names = {f"EXPECTED_L{case.length}" for case in MASTER.REFERENCE_CASES}
        self.assertEqual({name for name in INPUTS if name.startswith("EXPECTED_")}, expected_names)
        for case in MASTER.REFERENCE_CASES:
            name = f"EXPECTED_L{case.length}"
            compare(self, INPUTS[name], source_batch(CLOSE, case.length))
            self.assertEqual(len(INPUTS[name]), 252)
            for filename in FIXTURES:
                prefix = "#" if filename.endswith(".py") else "//"
                paired_comments = f"{prefix} {case.what_it_tests}\n{prefix} length={case.length}\n"
                self.assertIn(paired_comments, (DIRECTORY / filename).read_text())
        for filename in FIXTURES[1:]:
            arrays = language_expected(DIRECTORY / filename)
            self.assertEqual(set(arrays), expected_names)
            for name, values in arrays.items():
                compare(self, values, INPUTS[name], tolerance=0)

    def test_regeneration_is_repeatable_and_preserves_input_declarations(self):
        with tempfile.TemporaryDirectory(prefix="rsihann-fixtures-") as temporary:
            directory = Path(temporary)
            for filename in FIXTURES:
                (directory / filename).write_text((DIRECTORY.parent / filename).read_text())
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, directory)
                first = {filename: (directory / filename).read_bytes() for filename in FIXTURES}
                MASTER.generate_reference_data(CLOSE, directory)
            second = {filename: (directory / filename).read_bytes() for filename in FIXTURES}
            self.assertEqual(first, second)
            python_values = MASTER._load_literal_arrays(directory / "test_testdata.py")
            for filename in FIXTURES[1:]:
                arrays = language_expected(directory / filename)
                for name, values in arrays.items():
                    compare(self, values, python_values[name], tolerance=0)
            rust = (directory / "testdata.rs").read_text()
            self.assertTrue(rust.rstrip().endswith("}"))
            self.assertEqual(rust.count("pub mod testdata"), 1)
            self.assertGreater(rust.rfind("}"), rust.index("expected_l14"))


if __name__ == "__main__":
    unittest.main()
