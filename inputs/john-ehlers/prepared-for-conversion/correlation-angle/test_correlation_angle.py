"""Source-listing, analytical, stream-contract, and five-language fixture checks.

Run with standard-library unittest. The numerical oracle extracts expressions
from the supplied article, Mesa paper, and TradeStation listing rather than
calling the master implementation. Those provenance checks require the source
folder; the master and generated fixtures themselves are standalone.
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
SPEC = importlib.util.spec_from_file_location("correlation_angle_master", DIRECTORY / "correlation-angle.py")
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
CorrelationAngle = MASTER.CorrelationAngle
INPUTS = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
CLOSE = INPUTS["INPUT_CLOSE"]
SOURCE_DIRECTORY = DIRECTORY.parent.parent / "tasc/2020-06-correlation-as-a-cycle-indicator"
SOURCES = (
    SOURCE_DIRECTORY.joinpath("content.md").read_text(),
    SOURCE_DIRECTORY.joinpath("mesa/content.md").read_text(),
    SOURCE_DIRECTORY.joinpath("tips/code/tradestation-correlation-cycle.els").read_text(),
)
FIXTURES = ("test_testdata.py", "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig")


def expressions(source, name):
    """Read sequential assignment expressions, excluding declarations."""
    return [" ".join(v.split()) for v in
            re.findall(r"\b" + name + r"\s*=\s*(.*?);", source, re.I | re.S)]


def source_batch(prices, period, input_period, source):
    """Independent evaluation of the original five-sum and phase expressions.

    The only explicit adaptations are full-precision radians, one-based
    CurrentBar, and the documented complete-observed-window availability rule.
    Recompute templates from the source each bar, without master helpers.
    """
    compiled = lambda expression: compile(" ".join(expression.split()), "EasyLanguage source expression", "eval")
    # EasyLanguage trig takes degrees. Replace its full-turn constant before
    # evaluation so the requested radian multiplication association is explicit.
    trig = lambda expression: re.sub(r"\b360\b", "(2.0 * PI)", expression)
    y_formulas = [compiled(trig(v)) for v in expressions(source, "Y")]
    x_formula = compiled(expressions(source, "X")[0])
    sum_formulas = {name: compiled(expressions(source, name)[1])
                    for name in ("Sx", "Sy", "Sxx", "Sxy", "Syy")}
    component_formulas = [compiled(expressions(source, name)[0]) for name in ("Real", "Imag")]
    synthetic_formula = compiled(trig(expressions(source, "Price")[1]))
    angles = expressions(source, "Angle")
    angle_formula, quadrant_formula = map(compiled, angles[:2])
    # The source guard is extracted too: these are the two identical Pearson
    # conditions, followed by the backward-phase and two market-state guards.
    variance_text = re.findall(r"If\s+(\(\s*Length\s*\*\s*Sxx.*?\))\s+Then", source, re.I | re.S)[0]
    phase_text = re.findall(r"If\s+(Angle\[1\].*?)\s+Then", source, re.I | re.S)[0]
    state_text = re.findall(r"If\s+(AbsValue\(\s*Angle.*?\))\s*<\s*9\s+and\s+(Angle\s*(?:>=|<)\s*0)\s+Then", source, re.I | re.S)
    if len(y_formulas) != 2 or len(angles) != 3 or len(state_text) != 2:
        raise ValueError("source must define two correlations, three angle assignments, and two state guards")
    # Normalize the TradeStation Count/count spelling while keeping expressions.
    evaluate = lambda code, env: eval(code, {"__builtins__": {}}, env)
    variance_guard = compiled(variance_text)
    phase_guard = compiled(phase_text.replace("Angle[1]", "AngleHistory[1]"))
    hold_formula = compiled(angles[2].replace("Angle[1]", "AngleHistory[1]"))
    state_guards = [compiled((a + " < 9 and " + b).replace("Angle[1]", "AngleHistory[1]"))
                    for a, b in state_text]
    state_formulas = [compiled(v) for v in expressions(source, "State")]
    outputs, effective = [], []
    real = imag = previous = 0.0
    for index, supplied in enumerate(prices):
        env = {"PI": math.pi, "Length": period, "Period": period,
               "InputPeriod": input_period, "CurrentBar": index + 1,
               "Sine": math.sin, "Cosine": math.cos, "SquareRoot": math.sqrt,
               "Arctangent": lambda v: (180.0 / math.pi) * math.atan(v), "AbsValue": abs}
        effective.append(evaluate(synthetic_formula, env) if input_period else supplied)
        if index < period - 1:
            outputs.append((math.nan,) * 4)
            continue
        env["Price"] = [effective[index - lag] for lag in range(period)]
        values = [real, imag]
        for component in range(2):
            for name in sum_formulas:
                env[name] = 0.0
            for count in range(1, period + 1):
                env["count"] = env["Count"] = count
                env["X"] = evaluate(x_formula, env)
                env["Y"] = evaluate(y_formulas[component], env)
                for name, formula in sum_formulas.items():
                    env[name] = evaluate(formula, env)
            if evaluate(variance_guard, env):
                values[component] = evaluate(component_formulas[component], env)
        real, imag = values
        env.update(Real=real, Imag=imag, Angle=previous)
        if imag != 0.0:
            env["Angle"] = evaluate(angle_formula, env)
        if imag > 0.0:
            env["Angle"] = evaluate(quadrant_formula, env)
        # Angle[1] is source history, whereas bare Angle is the current candidate.
        env["AngleHistory"] = [env["Angle"], previous]
        if evaluate(phase_guard, env):
            env["Angle"] = evaluate(hold_formula, env)
        env["State"] = evaluate(state_formulas[0], env)
        for condition, formula in zip(state_guards, state_formulas[1:]):
            if evaluate(condition, env):
                env["State"] = evaluate(formula, env)
        previous = env["Angle"]
        outputs.append((real, imag, previous, float(env["State"])))
    return outputs


def compare(test, actual, expected, tolerance=0.0):
    test.assertEqual(len(actual), len(expected))
    for index, (left, right) in enumerate(zip(actual, expected)):
        if math.isnan(right):
            test.assertTrue(math.isnan(left), (index, left, right))
        else:
            test.assertTrue(math.isfinite(left) and math.isclose(left, right,
                            rel_tol=tolerance, abs_tol=tolerance), (index, left, right))


def compare_outputs(test, actual, expected, tolerance=0.0):
    test.assertEqual(len(actual), len(expected))
    for a, e in zip(actual, expected):
        compare(test, a, e, tolerance)


def centered_correlation(x, y):
    """Mathematical check using centered values and accurate stdlib summation."""
    n = len(x)
    mx, my = math.fsum(x) / n, math.fsum(y) / n
    dx, dy = [v - mx for v in x], [v - my for v in y]
    return math.fsum(a * b for a, b in zip(dx, dy)) / math.sqrt(
        math.fsum(v * v for v in dx) * math.fsum(v * v for v in dy))


def language_expected(path):
    """Parse exported decimal values independently of the master renderers."""
    patterns = {
        ".go": r"var expected(\w+) = \[\]float64\{(.*?)\}",
        ".ts": r"export const expected(\w+): number\[\] = \[(.*?)\];",
        ".rs": r"pub fn expected_(\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]\s*\}",
        ".zig": r"pub fn expected(\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\};\s*\}",
    }
    return {"EXPECTED_" + suffix.upper(): [
        math.nan if token.strip() in ("math.NaN()", "NaN", "f64::NAN", "nan")
        else float(token.strip()) for token in body.split(",") if token.strip()
    ] for suffix, body in re.findall(patterns[path.suffix], path.read_text(), re.S)}


class CorrelationAngleTests(unittest.TestCase):
    def test_confirmed_cases_match_three_original_source_listings(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = CorrelationAngle(case.period, case.input_period)
            actual = [indicator.update(value) for value in CLOSE]
            for index, source in enumerate(SOURCES):
                with self.subTest(case=case[:2], source=index):
                    compare_outputs(self, actual, source_batch(CLOSE, *case[:2], source))

    def test_matched_sinusoid_and_normalized_projection(self):
        for period in (3, 4, 5, 14, 20, 40, 60):
            indicator = CorrelationAngle(period, 0)
            for t in range(1, 4 * period + 1):
                phase = 2.0 * math.pi * t / period + 0.17
                out = indicator.update(2.0 + 3.0 * math.sin(phase))
                if indicator.is_primed:
                    self.assertAlmostEqual(out.real, math.sin(phase), delta=3e-13)
                    self.assertAlmostEqual(out.imag, math.cos(phase), delta=3e-13)
                    self.assertAlmostEqual(out.real ** 2 + out.imag ** 2, 1.0, delta=5e-13)

    def test_centered_pearson_and_projection_energy_on_real_prices(self):
        for period in (3, 14, 20, 60, 252):
            indicator = CorrelationAngle(period, 0)
            cos = [math.cos(2.0 * math.pi * k / period) for k in range(period)]
            neg_sin = [-math.sin(2.0 * math.pi * k / period) for k in range(period)]
            for t, price in enumerate(CLOSE):
                out = indicator.update(price)
                if indicator.is_primed:
                    window = [CLOSE[t - k] for k in range(period)]
                    # A nearly flat three-price window subtracts raw moments
                    # of ~100-valued prices. Measured centered error is 2.2e-10;
                    # energy excess is 5.1e-10. Preserve source arithmetic and
                    # allow 1e-9 here; larger windows use a tighter bound.
                    tolerance = 1e-9 if period == 3 else 1e-12
                    self.assertAlmostEqual(out.real, centered_correlation(window, cos), delta=tolerance)
                    self.assertAlmostEqual(out.imag, centered_correlation(window, neg_sin), delta=tolerance)
                    self.assertLessEqual(out.real ** 2 + out.imag ** 2, 1.0 + tolerance)

    def test_orthogonal_templates_and_second_harmonic_rejection(self):
        for period in (3, 4, 5, 20, 60):
            c = [math.cos(2.0 * math.pi * k / period) for k in range(period)]
            s = [-math.sin(2.0 * math.pi * k / period) for k in range(period)]
            self.assertAlmostEqual(math.fsum(c), 0.0, delta=3e-14)
            self.assertAlmostEqual(math.fsum(s), 0.0, delta=3e-14)
            self.assertAlmostEqual(math.fsum(a * b for a, b in zip(c, s)), 0.0, delta=3e-14)
            self.assertAlmostEqual(math.fsum(v * v for v in c), period / 2, delta=3e-14)
            self.assertAlmostEqual(math.fsum(v * v for v in s), period / 2, delta=3e-14)
        # A ten-bar sinusoid in a twenty-bar correlation window is the second
        # harmonic, orthogonal to these first-harmonic templates. Tiny residues
        # can feed an arbitrary phase; this is not a perfect phase measurement.
        indicator = CorrelationAngle(20, 10)
        for i in range(100):
            output = indicator.update(0.0)
            if indicator.is_primed:
                self.assertLess(abs(output.real), 1e-13)
                self.assertLess(abs(output.imag), 1e-13)

    def test_phase_quadrants_zero_imaginary_and_backward_guard(self):
        step = MASTER._phase_step
        for real, imag, candidate in ((1, 1, -45), (1, -1, 45), (-1, -1, 135), (-1, 1, -135)):
            angle, raw, held, state = step(real, imag, -180.0)
            self.assertEqual((angle, raw, held, state), (candidate, candidate, False, 0.0))
        self.assertEqual(step(1, 0, -60), (-60, -60, False, -1.0))
        self.assertEqual(step(-1, -0.0, 60), (60, 60, False, 1.0))
        self.assertEqual(step(-1, 1, 135), (-135, -135, False, 0.0))  # exactly 270
        self.assertEqual(step(-1, 1, 134.999), (134.999, -135, True, 1.0))
        self.assertEqual(step(-1, 1, 136), (-135, -135, False, 0.0))
        self.assertEqual(step(1, 1, 0), (0, -45, True, 1.0))

    def test_strict_nine_degree_threshold_and_raw_wrap_difference(self):
        step = MASTER._phase_step
        self.assertEqual(step(0, -1, 81)[3], 0.0)  # exactly nine is cycle
        self.assertEqual(step(0, -1, 81.001)[3], 1.0)
        self.assertEqual(step(0, -1, 80.999)[3], 0.0)
        self.assertEqual(step(0, 1, -99)[3], 0.0)
        self.assertEqual(step(0, 1, -98.999)[3], -1.0)
        # A small physical advance across the wrap is a large displayed jump.
        a = math.radians(-179.0 + 90.0)
        out = step(math.sin(a), math.cos(a), 179.0)
        self.assertAlmostEqual(out[0], -179.0)
        self.assertFalse(out[2])
        self.assertEqual(out[3], 0.0)

    def test_zero_and_flat_windows_retain_components(self):
        zero = CorrelationAngle(20, 0)
        for i in range(50):
            out = zero.update(0.0)
            if i >= 19:
                self.assertEqual(out, (0.0, 0.0, 0.0, 1.0))
                self.assertFalse(zero.diagnostics.real_sums.variance_valid)
        indicator = CorrelationAngle(5, 0)
        history = CLOSE[:20] + [0.0] * 20
        outputs = [indicator.update(v) for v in history]
        self.assertEqual(outputs[24].real, outputs[23].real)
        self.assertEqual(outputs[24].imag, outputs[23].imag)
        self.assertEqual(outputs[24], outputs[-1])
        compare_outputs(self, outputs, source_batch(history, 5, 0, SOURCES[0]))

    def test_affine_trends_and_short_period_degeneracy(self):
        for direction in (-1.0, 1.0):
            values = [direction * t for t in range(80)]
            indicator = CorrelationAngle(20, 0)
            outputs = [indicator.update(v) for v in values]
            self.assertLess(max(o.real for o in outputs[19:]) - min(o.real for o in outputs[19:]), 1e-12)
            self.assertLess(max(o.imag for o in outputs[19:]) - min(o.imag for o in outputs[19:]), 1e-12)
            self.assertIn(outputs[-1].state, (-1.0, 1.0))
            compare_outputs(self, outputs, source_batch(values, 20, 0, SOURCES[0]))
        for period in (1, 2):
            indicator = CorrelationAngle(period, 0)
            compare_outputs(self, [indicator.update(v) for v in CLOSE[:20]],
                            source_batch(CLOSE[:20], period, 0, SOURCES[0]))

    def test_warmup_one_based_clock_reset_and_causality(self):
        indicator = CorrelationAngle()
        self.assertEqual(indicator.warmup_bars, 19)
        outputs = [indicator.update(v) for v in CLOSE]
        self.assertTrue(all(math.isnan(v) for v in outputs[18]))
        self.assertTrue(all(math.isfinite(v) for v in outputs[19]))
        self.assertAlmostEqual(outputs[19].imag, 1.0)
        self.assertEqual(outputs[19].angle, 0.0)  # initial negative candidate is held
        self.assertTrue(indicator.is_primed)
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        compare_outputs(self, [indicator.update(v) for v in CLOSE], outputs)
        for input_period in (0, 20.5):
            a, b = CorrelationAngle(20, input_period), CorrelationAngle(20, input_period)
            prefix = CLOSE[:100]
            compare_outputs(self, [a.update(v) for v in prefix], [b.update(v) for v in prefix])
            a.update(1000.0)
            b.update(-1000.0)
            if input_period:
                self.assertEqual(a.last_output, b.last_output)
                self.assertEqual(a.diagnostics.price, math.sin(2.0 * math.pi * 101 / input_period))
            else:
                self.assertNotEqual(a.last_output, b.last_output)
        for period, available in ((252, 1), (253, 0)):
            indicator = CorrelationAngle(period, 0)
            results = [indicator.update(v) for v in CLOSE]
            self.assertEqual(sum(math.isfinite(o.real) for o in results), available)

    def test_validation_and_rejection_do_not_advance_state(self):
        for period in (0, -1, True, False, 20.0, "20", None):
            with self.assertRaises(ValueError):
                CorrelationAngle(period)
        for input_period in (-1, math.inf, -math.inf, math.nan, True):
            with self.assertRaises(ValueError):
                CorrelationAngle(20, input_period)
        for ip in (0, 20):
            indicator = CorrelationAngle(20, ip)
            for v in CLOSE[:25]:
                indicator.update(v)
            before = (indicator._prices[:], indicator._count, indicator.last_output, indicator.diagnostics)
            for invalid in (math.nan, math.inf, -math.inf):
                with self.assertRaises(ValueError):
                    indicator.update(invalid)
                self.assertEqual((indicator._prices, indicator._count, indicator.last_output, indicator.diagnostics), before)
            with self.assertRaises(AttributeError):
                indicator.period = 40
        overflow = CorrelationAngle(3, 0)
        overflow.update(3e153)
        overflow.update(-3e153)
        with self.assertRaises(ValueError):
            overflow.update(3e153)  # denominator product overflow
        self.assertEqual(overflow._count, 2)
        tiny_period = CorrelationAngle(20, 5e-324)
        with self.assertRaises(ValueError):
            tiny_period.update(1.0)
        self.assertEqual(tiny_period._count, 0)

    def test_embedded_closes_and_input_copies(self):
        original = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        self.assertEqual({name: INPUTS[name] for name in original}, original)
        self.assertEqual(len(CLOSE), 252)
        tree = ast.parse(DIRECTORY.joinpath("correlation-angle.py").read_text())
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "INPUT_CLOSE" for t in n.targets))
        self.assertEqual(ast.literal_eval(node.value), CLOSE)
        for filename in FIXTURES[1:]:
            before = DIRECTORY.parent.joinpath(filename).read_text()
            after = DIRECTORY.joinpath(filename).read_text()
            if filename.endswith(".go"):
                before = before.replace("package xxxx", "package correlationangle", 1)
                after = after.replace('import "math"\n\n', "", 1)
            if filename.endswith(".rs"):
                before = before[:before.rfind("}")].rstrip()
            self.assertTrue(after.startswith(before.rstrip()), filename)

    def test_expected_arrays_precision_comments_and_native_values(self):
        names = {f"EXPECTED_{MASTER._case_suffix(case)}_{field.upper()}"
                 for case in MASTER.REFERENCE_CASES for field in MASTER.CorrelationAngleOutput._fields}
        self.assertEqual({name for name in INPUTS if name.startswith("EXPECTED_")}, names)
        self.assertEqual(len(names), 64)
        for case in MASTER.REFERENCE_CASES:
            indicator = CorrelationAngle(*case[:2])
            actual = [indicator.update(value) for value in CLOSE]
            for field in MASTER.CorrelationAngleOutput._fields:
                expected = INPUTS[f"EXPECTED_{MASTER._case_suffix(case)}_{field.upper()}"]
                compare(self, expected, [float(format(getattr(o, field), ".15g")) for o in actual])
                self.assertEqual(sum(math.isnan(v) for v in expected), min(252, case.period - 1))
            for filename in FIXTURES:
                prefix = "#" if filename.endswith(".py") else "//"
                self.assertIn(f"{prefix} {case.what_it_tests}\n{prefix} period={case.period}, input_period={case.input_period:g}\n",
                              DIRECTORY.joinpath(filename).read_text())
        for filename in FIXTURES[1:]:
            native = language_expected(DIRECTORY / filename)
            self.assertEqual(set(native), names)
            for name, values in native.items():
                compare(self, values, INPUTS[name])

    def test_generation_is_repeatable_and_preserves_inputs(self):
        with tempfile.TemporaryDirectory(prefix="correlation-angle-fixtures-") as temporary:
            destination = Path(temporary)
            for filename in FIXTURES:
                destination.joinpath(filename).write_text(DIRECTORY.parent.joinpath(filename).read_text())
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, destination)
                first = {filename: destination.joinpath(filename).read_bytes() for filename in FIXTURES}
                MASTER.generate_reference_data(CLOSE, destination)
            self.assertEqual(first, {filename: destination.joinpath(filename).read_bytes() for filename in FIXTURES})
            generated = MASTER._load_literal_arrays(destination / "test_testdata.py")
            for filename in FIXTURES[1:]:
                for name, values in language_expected(destination / filename).items():
                    compare(self, values, generated[name])


if __name__ == "__main__":
    unittest.main()
