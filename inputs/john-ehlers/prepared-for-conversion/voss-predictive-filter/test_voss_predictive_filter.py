"""Source-expression and analytical checks for the Voss research master.

Standard library only. The batch oracle extracts the supplied TradeStation
indicator expressions and keeps chronological, unbounded reference histories.
It does not share streaming coefficients, histories, or update calculations.
All twenty combinations have been confirmed. Expected-fixture tests require
both output components for every case and check deterministic regeneration.
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
SPEC = importlib.util.spec_from_file_location("voss_master", DIRECTORY / "voss-predictive-filter.py")
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
CLOSE = INPUTS["INPUT_CLOSE"]
SOURCE = (DIRECTORY.parent.parent / "tasc/2019-08-a-peek-into-the-future/tips/VPF.els").read_text().split("Strategy:")[0]
FIXTURES = ("test_testdata.py", "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig")
HAS_EXPECTED = any(name.startswith("EXPECTED_") for name in INPUTS)


def expression(name):
    """Read an assignment from the primary source, excluding declarations."""
    match = re.search(r"\b" + name + r"\s*=\s*(.*?);", SOURCE, re.S | re.I)
    return " ".join(match.group(1).split())


def source_batch(prices, period=20, predict=3, bandwidth=0.25):
    """Independent evaluator of source arithmetic with explicit zero seeds.

    Only the fixed source Bandwidth=.25 is substituted by the optional Excel
    extension. CurrentBar=1 corresponds to input index zero. Negative-index
    recursive outputs are zero, whereas no missing price is fabricated.
    """
    env = {"Period": period, "Predict": predict, "Bandwidth": bandwidth,
           "Cosine": lambda degrees: math.cos(math.radians(degrees)),
           "Squareroot": math.sqrt}
    for name in ("Order", "F1", "G1", "S1"):
        env[name] = eval(expression(name), {"__builtins__": {}}, env)
    # The tip omits a semicolon immediately before Else, so stop there.
    filt_expr = expression("Filt").split("else")[0]
    filt_expr = filt_expr.replace("Close[2]", "price2").replace("Close", "price")
    filt_expr = filt_expr.replace("Filt[1]", "filt1").replace("Filt[2]", "filt2")
    # The first SumC assignment is its reset, not the accumulation.
    sum_expr = re.search(r"Sumc\s*=\s*SumC\s*\+\s*(.*?);", SOURCE, re.S | re.I).group(1)
    sum_expr = "SumC + " + " ".join(sum_expr.split())
    sum_expr = sum_expr.replace("Voss[Order - Count]", "voss_lag")
    voss_expr = expression("Voss")
    filts, predictors, outputs = [], [], []
    for t, price in enumerate(prices):
        if t < 5:
            filt = 0.0
        else:
            env.update(price=price, price2=prices[t - 2], filt1=filts[t - 1], filt2=filts[t - 2])
            filt = eval(filt_expr, {"__builtins__": {}}, env)
        env.update(Filt=filt, SumC=0.0)
        for count in range(env["Order"]):
            lag = env["Order"] - count
            env.update(Count=count, voss_lag=predictors[t - lag] if t >= lag else 0.0)
            env["SumC"] = eval(sum_expr, {"__builtins__": {}}, env)
        predictor = eval(voss_expr, {"__builtins__": {}}, env)
        filts.append(filt)
        predictors.append(predictor)
        outputs.append((math.nan, math.nan) if t < 5 else (filt, predictor))
    return outputs


def compare(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for index, (left, right) in enumerate(zip(actual, expected)):
        if math.isnan(right):
            test.assertTrue(math.isnan(left), (index, left, right))
        else:
            test.assertTrue(math.isfinite(left) and math.isclose(left, right,
                            rel_tol=tolerance, abs_tol=tolerance), (index, left, right))


def stream(prices, period=20, predict=3, bandwidth=0.25):
    indicator = MASTER.VossPredictiveFilter(period, predict, bandwidth)
    return [indicator.update(value) for value in prices]


def transfer(period, predict, bandwidth, omega):
    """Independent complex-frequency equations, not streaming coefficients."""
    theta = 2 * math.pi * bandwidth / period
    s = 1 / math.cos(theta) - math.tan(theta)
    f = math.cos(2 * math.pi / period)
    z1 = cmath.exp(-1j * omega)
    bandpass = 0.5 * (1 - s) * (1 - z1**2) / (1 - f * (1 + s) * z1 + s * z1**2)
    order = 3 * predict
    denominator = 1 + sum((order - lag + 1) / order * z1**lag for lag in range(1, order + 1))
    voss = (3 + order) / 2 / denominator
    return bandpass, voss


def language_expected(path):
    """Parse only native expected-array declarations and numeric tokens."""
    patterns = {
        ".go": r"var expected([A-Z0-9_]+) = \[\]float64\{(.*?)\}",
        ".ts": r"export const expected([A-Z0-9_]+): number\[\] = \[(.*?)\];",
        ".rs": r"pub fn expected_([a-z0-9_]+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\]\s*\}",
        ".zig": r"pub fn expected([A-Z0-9_]+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\};\s*\}",
    }
    arrays = {}
    for suffix, body in re.findall(patterns[path.suffix], path.read_text(), re.S):
        values = [math.nan if token.strip() in ("math.NaN()", "NaN", "f64::NAN", "nan")
                  else float(token.strip()) for token in body.split(",") if token.strip()]
        arrays["EXPECTED_" + suffix.upper()] = values
    return arrays


class VossPredictiveFilterTests(unittest.TestCase):
    def test_every_confirmed_case_matches_supplied_source_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            actual = stream(CLOSE, case.period, case.predict, case.bandwidth)
            expected = source_batch(CLOSE, case.period, case.predict, case.bandwidth)
            for field in range(2):
                compare(self, [value[field] for value in actual], [value[field] for value in expected], 0)

    def test_five_bar_gate_and_zero_seed_history(self):
        for predict in (0, 1, 3, 8, 84):
            indicator = MASTER.VossPredictiveFilter(predict=predict)
            self.assertEqual(indicator.warmup_bars, 5)
            for t, close in enumerate(CLOSE[:20]):
                output = indicator.update(close)
                self.assertEqual(indicator.is_primed, t >= 5)
                self.assertEqual(math.isnan(output.bandpass), t < 5)
                self.assertEqual(math.isnan(output.voss), t < 5)
                self.assertEqual(len(indicator._voss_history), 3 * predict)
                self.assertEqual(len(indicator._prices), min(t + 1, 2))
                if t < 5:
                    self.assertEqual(indicator._filt1, 0.0)
                    self.assertEqual(indicator._filt2, 0.0)
                    self.assertEqual(indicator._voss_history, [0.0] * (3 * predict))
                if t == 5:
                    expected_bpf = 0.5 * (1 - indicator._s1) * (CLOSE[5] - CLOSE[3])
                    self.assertEqual(output.bandpass, expected_bpf)
                    self.assertEqual(output.voss, (3 + 3 * predict) / 2 * expected_bpf)
            self.assertEqual(indicator.output, output)

    def test_two_bar_differencing_and_impulse_feedback_order(self):
        period, predict = 20, 1
        # Flat zero input during setup, then a single spike. At t=5 the
        # predictor has no nonzero past values, so Voss=3*BPF. At t=6 its
        # newest past output has feedback coefficient ONE, not 1/Order.
        outputs = stream([0] * 5 + [1, 0, 0, 0], period, predict)
        s = 1 / math.cos(math.pi / 40) - math.tan(math.pi / 40)
        f = math.cos(math.pi / 10)
        b = 0.5 * (1 - s)
        self.assertAlmostEqual(outputs[5].bandpass, b, places=14)
        self.assertAlmostEqual(outputs[5].voss, 3 * b, places=14)
        filt6 = f * (1 + s) * b
        self.assertAlmostEqual(outputs[6].bandpass, filt6, places=14)
        self.assertAlmostEqual(outputs[6].voss, 3 * filt6 - outputs[5].voss, places=14)
        filt7 = -b + f * (1 + s) * filt6 - s * b  # Close[2] sees the spike.
        self.assertAlmostEqual(outputs[7].bandpass, filt7, places=14)
        predictor7 = 3 * filt7 - (2 / 3 * outputs[5].voss + outputs[6].voss)
        self.assertAlmostEqual(outputs[7].voss, predictor7, places=14)

    def test_constant_inputs_and_zero_order_gain(self):
        outputs = stream([42] * 100)
        self.assertEqual(outputs[5:], [(0.0, 0.0)] * 95)
        zero_order = stream(CLOSE, predict=0)
        for output in zero_order[5:]:
            self.assertEqual(output.voss, 1.5 * output.bandpass)

    def test_bandpass_is_independent_of_prediction_parameter(self):
        baseline = stream(CLOSE, predict=1)
        for predict in (0, 2, 3, 4, 8):
            actual = stream(CLOSE, predict=predict)
            compare(self, [value.bandpass for value in actual], [value.bandpass for value in baseline], 0)

    def test_translation_scaling_and_reflection(self):
        baseline = stream(CLOSE)
        for offset, factor in ((1024, 1), (0, 8), (-200, 0.5), (0, -1)):
            actual = stream([offset + factor * value for value in CLOSE])
            for field in range(2):
                compare(self, [value[field] for value in actual], [factor * value[field] for value in baseline], 2e-11)

    def test_sinusoidal_transfer_response_and_phase_lead(self):
        # Settled deterministic sinusoids check the full cascade against its
        # independently derived transfer response, including output amplitude.
        for period, predict, bandwidth in ((10, 1, .25), (20, 3, .25), (20, 3, .1), (30, 3, .5), (20, 8, .25)):
            for wavelength in (period * .85, period, period * 1.15):
                omega = 2 * math.pi / wavelength
                hbp, hvoss = transfer(period, predict, bandwidth, omega)
                indicator = MASTER.VossPredictiveFilter(period, predict, bandwidth)
                for t in range(2200):
                    output = indicator.update(math.sin(omega * t))
                    if t >= 2100:
                        wave = cmath.exp(1j * omega * t)
                        self.assertAlmostEqual(output.bandpass, (hbp * wave).imag, places=10)
                        self.assertAlmostEqual(output.voss, (hbp * hvoss * wave).imag, places=10)
            center_bp, center_voss = transfer(period, predict, bandwidth, 2 * math.pi / period)
            self.assertAlmostEqual(abs(center_bp), 1.0, places=12)
            self.assertAlmostEqual(cmath.phase(center_bp), 0.0, places=12)
            self.assertGreater(cmath.phase(center_voss), 0.0)

    def test_prediction_low_frequency_delay_and_noise_gain(self):
        # M>0: H_voss(0)=1, tau(0)=-(M+1)*(M+2)/(3*(M+3)).
        for predict in (1, 2, 3, 4, 8):
            order = 3 * predict
            _, dc = transfer(20, predict, .25, 0)
            self.assertAlmostEqual(dc.real, 1.0, places=14)
            delta = 1e-6
            _, positive = transfer(20, predict, .25, delta)
            _, negative = transfer(20, predict, .25, -delta)
            delay = -(cmath.phase(positive) - cmath.phase(negative)) / (2 * delta)
            self.assertAlmostEqual(delay, -(order + 1) * (order + 2) / (3 * (order + 3)), places=8)
            _, nyquist = transfer(20, predict, .25, math.pi)
            self.assertGreater(abs(nyquist), abs(dc))
        # At resonance the BPF has zero phase shift, but POSITIVE group delay.
        omega, delta = math.pi / 10, 1e-6
        plus = transfer(20, 3, .25, omega + delta)[0]
        minus = transfer(20, 3, .25, omega - delta)[0]
        delay = -(cmath.phase(plus) - cmath.phase(minus)) / (2 * delta)
        self.assertAlmostEqual(delay, 1 / math.tan(math.pi * .25 / 20), places=6)

    def test_impulse_decay_for_all_confirmed_cases(self):
        for case in MASTER.REFERENCE_CASES:
            # Include long periods and high predictor orders; a zero initial
            # state impulse must decay rather than silently saturate or clamp.
            outputs = stream([0] * 5 + [1] + [0] * 4000,
                             case.period, case.predict, case.bandwidth)
            first_peak = max(abs(output.voss) for output in outputs[5:505])
            tail_peak = max(abs(output.voss) for output in outputs[-252:])
            self.assertLess(tail_peak, first_peak * .001)

    def test_reset_causal_prefixes_and_rejected_updates(self):
        indicator = MASTER.VossPredictiveFilter()
        baseline = [indicator.update(value) for value in CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        replay = [indicator.update(value) for value in CLOSE]
        for field in range(2):
            compare(self, [value[field] for value in replay], [value[field] for value in baseline], 0)
        prefix = stream(CLOSE[:80])
        for field in range(2):
            compare(self, [value[field] for value in prefix], [value[field] for value in baseline[:80]], 0)
        snapshot = (indicator._bars, indicator._prices[:], indicator._filt1,
                    indicator._filt2, indicator._voss_history[:], indicator.output)
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(value)
            self.assertEqual((indicator._bars, indicator._prices, indicator._filt1,
                              indicator._filt2, indicator._voss_history, indicator.output), snapshot)
        extreme = MASTER.VossPredictiveFilter()
        for _ in range(5):
            extreme.update(-1e308)
        with self.assertRaises(ValueError):
            extreme.update(1e308)
        self.assertEqual(extreme._bars, 5)
        self.assertEqual(extreme._prices, [-1e308, -1e308])
        self.assertEqual(extreme._voss_history, [0.0] * 9)

    def test_parameter_ranges_and_floating_point_resolution(self):
        for period in (0, 1, 2, -1, 20.0, True, "20", None):
            with self.assertRaises(ValueError):
                MASTER.VossPredictiveFilter(period=period)
        for predict in (-1, 1.5, True, "3", None):
            with self.assertRaises(ValueError):
                MASTER.VossPredictiveFilter(predict=predict)
        for bandwidth in (0, -1, 5, math.nan, math.inf, True, 1e-20):
            with self.assertRaises(ValueError):
                MASTER.VossPredictiveFilter(bandwidth=bandwidth)
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.VossPredictiveFilter(case.period, case.predict, case.bandwidth)
            self.assertGreater(indicator._s1, 0)
            self.assertLess(indicator._s1, 1)

    def test_embedded_inputs_and_copied_input_declarations(self):
        parent = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        self.assertEqual({name: INPUTS[name] for name in parent}, parent)
        self.assertEqual(len(CLOSE), 252)
        tree = ast.parse((DIRECTORY / "voss-predictive-filter.py").read_text())
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "INPUT_CLOSE" for target in node.targets))
        self.assertEqual(ast.literal_eval(node.value), CLOSE)
        for filename in FIXTURES[1:]:
            before, after = (DIRECTORY.parent / filename).read_text(), (DIRECTORY / filename).read_text()
            if filename.endswith(".go"):
                before = before.replace("package xxxx", "package vosspredictivefilter", 1)
                after = after.replace('import "math"\n\n', "", 1)
            if filename.endswith(".rs") and HAS_EXPECTED:
                before = before[:before.rfind("}")].rstrip()
            self.assertTrue(after.startswith(before.rstrip()), filename)

    def test_expected_arrays_comments_and_native_language_literals(self):
        names = {"EXPECTED_" + MASTER._case_suffix(case) + "_" + token
                 for case in MASTER.REFERENCE_CASES for token in MASTER.OUTPUT_TOKENS}
        self.assertEqual({name for name in INPUTS if name.startswith("EXPECTED_")}, names)
        for case in MASTER.REFERENCE_CASES:
            expected = source_batch(CLOSE, case.period, case.predict, case.bandwidth)
            for field, token in enumerate(MASTER.OUTPUT_TOKENS):
                name = "EXPECTED_" + MASTER._case_suffix(case) + "_" + token
                compare(self, INPUTS[name], [value[field] for value in expected])
                self.assertEqual(len(INPUTS[name]), 252)
                self.assertEqual(sum(math.isnan(value) for value in INPUTS[name]), 5)
            for filename in FIXTURES:
                prefix = "#" if filename.endswith(".py") else "//"
                comments = f"{prefix} {case.what_it_tests}\n{prefix} {MASTER._parameter_comment(case)}\n"
                self.assertEqual((DIRECTORY / filename).read_text().count(comments), 2)
        for filename in FIXTURES[1:]:
            native = language_expected(DIRECTORY / filename)
            self.assertEqual(set(native), names)
            for name, values in native.items():
                compare(self, values, INPUTS[name], 0)

    def test_repeatable_regeneration_preserves_inputs_and_language_values(self):
        with tempfile.TemporaryDirectory(prefix="vpf-fixtures-") as temporary:
            directory = Path(temporary)
            for filename in FIXTURES:
                (directory / filename).write_text((DIRECTORY.parent / filename).read_text())
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, directory)
                first = {filename: (directory / filename).read_bytes() for filename in FIXTURES}
                MASTER.generate_reference_data(CLOSE, directory)
            self.assertEqual(first, {filename: (directory / filename).read_bytes() for filename in FIXTURES})
            python_values = MASTER._load_literal_arrays(directory / "test_testdata.py")
            for filename in FIXTURES[1:]:
                native = language_expected(directory / filename)
                for name, values in native.items():
                    compare(self, values, python_values[name], 0)


if __name__ == "__main__":
    unittest.main()
