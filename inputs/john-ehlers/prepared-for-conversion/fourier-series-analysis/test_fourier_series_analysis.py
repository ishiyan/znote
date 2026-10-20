"""Independent source transcription and deterministic signal checks.

Standard library only. Tests exercise real source ambiguities (startup,
harmonic quadrature, weighting, persistent variables) and reference export.
Temporary export tests do not constitute user approval of production cases.
"""

import ast
import cmath
import contextlib
import io
import math
from pathlib import Path
import re
import runpy
import shutil
import tempfile
import unittest
from unittest.mock import patch


DIRECTORY = Path(__file__).resolve().parent
MASTER = runpy.run_path(str(DIRECTORY / "fourier-series-analysis.py"))
Indicator = MASTER["FourierSeriesAnalysis"]
CASES = MASTER["REFERENCE_CASES"]
DATA = runpy.run_path(str(DIRECTORY / "test_testdata.py"))
CLOSE = DATA["INPUT_CLOSE"]
FIXTURES = ("test_testdata.py", "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig")


def article_reference(prices, fundamental):
    """Whole-record literal transcription, with absolute-index historical arrays.

    Independent degree-to-radian coefficient expression; full F-term power
    loops including pre-stream zero seeds; one-based CurrentBar guards; no
    rolling state containers from the implementation. Keeps Wave on P1=0.
    """
    count = len(prices)
    bp = [[0.0] * count for _ in range(3)]
    q = [[0.0] * count for _ in range(3)]
    power = [[0.0] * count for _ in range(3)]
    wave = [0.0] * count
    roc = [0.0] * count
    coefficients = []
    for harmonic in (1, 2, 3):
        period = fundamental / harmonic
        l = math.cos(math.radians(360.0 / period))
        g = math.cos(math.radians(0.1 * 360.0 / period))
        s = 1.0 / g - math.sqrt(1.0 / (g * g) - 1.0)
        coefficients.append((l, s))
    for t in range(count):
        for h, (l, s) in enumerate(coefficients):
            if t + 1 > 3:
                bp[h][t] = (0.5 * (1.0 - s) * (prices[t] - prices[t - 2])
                            + l * (1.0 + s) * bp[h][t - 1] - s * bp[h][t - 2])
            if t + 1 > 4:
                q[h][t] = fundamental / (2.0 * math.pi) * (bp[h][t] - bp[h][t - 1])
            p = 0.0
            for k in range(fundamental):
                b = bp[h][t - k] if t - k >= 0 else 0.0
                quadrature = q[h][t - k] if t - k >= 0 else 0.0
                p = p + b * b + quadrature * quadrature
            power[h][t] = p
        wave[t] = wave[t - 1] if t > 0 else 0.0
        if power[0][t] != 0.0:
            wave[t] = (bp[0][t] + math.sqrt(power[1][t] / power[0][t]) * bp[1][t]
                       + math.sqrt(power[2][t] / power[0][t]) * bp[2][t])
        old_wave = wave[t - 2] if t >= 2 else 0.0
        roc[t] = fundamental / (4.0 * math.pi) * (wave[t] - old_wave)
    return bp, q, power, wave, roc


def close_or_nan(left, right, tolerance=5e-12):
    return (math.isnan(left) and math.isnan(right)) or math.isclose(
        left, right, rel_tol=tolerance, abs_tol=tolerance)


class FourierTests(unittest.TestCase):
    def test_all_cases_and_diagnostics_match_independent_article(self):
        for case in CASES:
            with self.subTest(fundamental=case.fundamental):
                indicator = Indicator(case.fundamental)
                bp, q, powers, wave, roc = article_reference(CLOSE, case.fundamental)
                for t, price in enumerate(CLOSE):
                    result = indicator.update(price)
                    state = indicator.state
                    for h in range(3):
                        for actual, expected in ((state.band_pass[h], bp[h][t]),
                                                 (state.quadrature[h], q[h][t]),
                                                 (state.power[h], powers[h][t])):
                            self.assertTrue(close_or_nan(actual, expected), (case, t, h, actual, expected))
                    self.assertTrue(close_or_nan(state.internal_wave, wave[t]), (case, t))
                    self.assertTrue(close_or_nan(state.internal_roc, roc[t]), (case, t))
                    expected_w = wave[t] if t >= case.fundamental - 1 else math.nan
                    expected_r = roc[t] if t >= case.fundamental + 1 else math.nan
                    self.assertTrue(close_or_nan(result.wave, expected_w), (case, t))
                    self.assertTrue(close_or_nan(result.roc, expected_r), (case, t))
                    self.assertIs(result, indicator.output)
                    self.assertEqual(indicator.is_primed, t >= case.fundamental - 1)
                    self.assertEqual(indicator.roc_is_primed, t >= case.fundamental + 1)
                self.assertEqual(indicator.warmup_bars, case.fundamental - 1)
                self.assertEqual(indicator.roc_warmup_bars, case.fundamental + 1)

    def test_startup_guards_and_first_active_difference(self):
        indicator = Indicator(7)
        prices = [10.0, 11.0, 15.0, 19.0, 23.0]
        for t, price in enumerate(prices):
            indicator.update(price)
            state = indicator.state
            if t <= 2:
                self.assertEqual(state.band_pass, (0.0, 0.0, 0.0))
                self.assertEqual(state.quadrature, (0.0, 0.0, 0.0))
            if t == 3:
                for h, coefficient in enumerate(indicator.coefficients):
                    expected = 0.5 * (1.0 - coefficient.s) * (19.0 - 11.0)
                    self.assertEqual(state.band_pass[h], expected)
                self.assertEqual(state.quadrature, (0.0, 0.0, 0.0))
            if t == 4:
                for h in range(3):
                    expected = 7.0 / (2.0 * math.pi) * (state.band_pass[h] - previous_bp[h])
                    self.assertEqual(state.quadrature[h], expected)
            previous_bp = state.band_pass

    def test_constant_prices_prime_to_zero_without_division(self):
        for fundamental in (7, 20, 253):
            indicator = Indicator(fundamental)
            for t in range(fundamental + 10):
                output = indicator.update(100.0)
                self.assertEqual(indicator.state.internal_wave, 0.0)
                self.assertEqual(indicator.state.internal_roc, 0.0)
                self.assertEqual(indicator.state.power, (0.0, 0.0, 0.0))
                self.assertTrue(close_or_nan(output.wave, 0.0 if t >= fundamental - 1 else math.nan))
                self.assertTrue(close_or_nan(output.roc, 0.0 if t >= fundamental + 1 else math.nan))

    def test_zero_fundamental_power_retains_previous_wave(self):
        # Force a declared zero-power state with a nonzero persistent Wave.
        # Finite real-data recursions rarely hit exact zero again; this checks
        # the literal source branch without adding a production epsilon rule.
        indicator = Indicator(7)
        for _ in range(12):
            indicator.update(10.0)
        indicator._wave = 4.0
        indicator._wave1 = 3.0
        indicator._wave2 = 2.0
        result = indicator.update(10.0)
        self.assertEqual(result.wave, 4.0)
        self.assertEqual(result.roc, 7.0 / (4.0 * math.pi) * (4.0 - 2.0))

    def test_odd_periods_keep_fractional_harmonic_periods(self):
        indicator = Indicator(19)
        for h, coefficient in enumerate(indicator.coefficients, 1):
            self.assertEqual(coefficient.l, math.cos(2.0 * math.pi / (19.0 / h)))
        self.assertNotEqual(indicator.coefficients[1].l, math.cos(2.0 * math.pi / 9.0))

    def test_deterministic_tuned_harmonics_gain_quadrature_and_power(self):
        fundamental = 20
        amplitude = 2.25
        phase = 0.37
        for h in (1, 2, 3):
            with self.subTest(harmonic=h):
                indicator = Indicator(fundamental)
                omega = 2.0 * math.pi * h / fundamental
                d = fundamental / math.pi * math.sin(math.pi * h / fundamental)
                expected_power = fundamental * amplitude * amplitude / 2.0 * (1.0 + d * d)
                for t in range(80 * fundamental):
                    indicator.update(100.0 + amplitude * math.sin(omega * t + phase))
                    if t >= 79 * fundamental:
                        self.assertAlmostEqual(indicator.state.band_pass[h - 1],
                                               amplitude * math.sin(omega * t + phase), delta=2e-10)
                        self.assertAlmostEqual(indicator.state.quadrature[h - 1],
                                               amplitude * d * math.cos(omega * (t - 0.5) + phase), delta=3e-10)
                        self.assertAlmostEqual(indicator.state.power[h - 1], expected_power, delta=3e-8)

    def test_article_patterns_match_steady_state_filter_bank_theory(self):
        # Account analytically for nonzero cross-filter leakage; no assertion
        # of perfect reconstruction or undisclosed amplitude normalization.
        fundamental = 30
        for amplitudes in ((1.0, 0.0, 0.33), (1.0, -0.5, 0.33)):
            with self.subTest(amplitudes=amplitudes):
                responses = []
                powers = []
                for target_h in (1, 2, 3):
                    theta = 2.0 * math.pi * target_h / fundamental
                    l = math.cos(theta)
                    g = math.cos(0.1 * theta)
                    s = 1.0 / g - math.sqrt(1.0 / (g * g) - 1.0)
                    row = []
                    p = 0.0
                    for input_h, amplitude in enumerate(amplitudes, 1):
                        omega = 2.0 * math.pi * input_h / fundamental
                        delay = cmath.exp(-1j * omega)
                        transfer = (0.5 * (1.0 - s) * (1.0 - delay * delay)
                                    / (1.0 - l * (1.0 + s) * delay + s * delay * delay))
                        row.append(amplitude * transfer)
                        d = fundamental / math.pi * math.sin(math.pi * input_h / fundamental)
                        p += fundamental / 2.0 * abs(amplitude * transfer) ** 2 * (1.0 + d * d)
                    responses.append(row)
                    powers.append(p)
                weights = (1.0, math.sqrt(powers[1] / powers[0]), math.sqrt(powers[2] / powers[0]))

                def theoretical_wave(t):
                    bps = [sum((response * cmath.exp(1j * 2.0 * math.pi * h * t / fundamental)).imag
                               for h, response in enumerate(row, 1)) for row in responses]
                    return sum(weight * bp for weight, bp in zip(weights, bps))

                indicator = Indicator(fundamental)
                for t in range(100 * fundamental):
                    price = 100.0 + sum(amplitude * math.sin(2.0 * math.pi * h * t / fundamental)
                                        for h, amplitude in enumerate(amplitudes, 1))
                    output = indicator.update(price)
                    if t >= 99 * fundamental:
                        self.assertAlmostEqual(output.wave, theoretical_wave(t), delta=2e-9)
                        expected_roc = fundamental / (4.0 * math.pi) * (theoretical_wave(t) - theoretical_wave(t - 2))
                        self.assertAlmostEqual(output.roc, expected_roc, delta=3e-9)

    def test_reset_replays_and_histories_are_bounded(self):
        indicator = Indicator(20)
        first = [indicator.update(price) for price in CLOSE]
        self.assertLessEqual(len(indicator._history), 20)
        self.assertLessEqual(len(indicator._prices), 2)
        indicator.reset()
        self.assertEqual(indicator.samples_seen, 0)
        self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isnan(indicator.output.wave))
        second = [indicator.update(price) for price in CLOSE]
        self.assertTrue(all(close_or_nan(a, b, 0.0) for x, y in zip(first, second) for a, b in zip(x, y)))

    def test_parameter_domain_and_read_only_configuration(self):
        for value in (False, True, 0, -1, 1, 5, 6, 7.0, 20.0, 20.5, math.nan, math.inf, "20", 10**400):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Indicator(value)
        self.assertEqual(Indicator().fundamental, 20)
        self.assertEqual(Indicator(7).bandwidth, 0.1)
        with self.assertRaises(AttributeError):
            Indicator().fundamental = 30

    def test_invalid_input_and_overflow_do_not_consume_or_change_state(self):
        indicator = Indicator(20)
        indicator.update(1e308)
        indicator.update(-1e308)
        indicator.update(1e308)
        state = indicator.state
        for price in (math.nan, math.inf, -math.inf, 1e308):
            with self.subTest(price=price):
                with self.assertRaises(ValueError):
                    indicator.update(price)
                self.assertEqual(indicator.samples_seen, 3)
                self.assertIs(indicator.state, state)
        # Power overflow, independent of a price-difference overflow.
        second = Indicator(7)
        for _ in range(3):
            second.update(0.0)
        with self.assertRaises(ValueError):
            second.update(1e200)
        self.assertEqual(second.samples_seen, 3)

    def test_embedded_input_matches_copied_original_and_case_table(self):
        source = (DIRECTORY / "fourier-series-analysis.py").read_text()
        tree = ast.parse(source)
        embedded = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "INPUT_CLOSE" for target in node.targets))
        self.assertEqual(ast.literal_eval(embedded.value), CLOSE)
        self.assertEqual(len(CLOSE), 252)
        self.assertEqual(CLOSE, runpy.run_path(str(DIRECTORY.parent / "test_testdata.py"))["INPUT_CLOSE"])
        self.assertEqual(len(CASES), 20)
        self.assertEqual(len({case.fundamental for case in CASES}), 20)
        description = (DIRECTORY / "description.md").read_text()
        for case in CASES:
            self.assertIn(f"| {case.fundamental} | {case.what_it_tests} |", description)

    def test_unconfirmed_generation_is_guarded_before_writing(self):
        generate = MASTER["generate_reference_data"]
        with tempfile.TemporaryDirectory(prefix="fourier-unconfirmed-") as name:
            directory = Path(name)
            for fixture in FIXTURES:
                shutil.copyfile(DIRECTORY / fixture, directory / fixture)
            before = {fixture: (directory / fixture).read_bytes() for fixture in FIXTURES}
            with patch.dict(generate.__globals__, REFERENCE_CASES_CONFIRMED=False):
                with self.assertRaises(ValueError):
                    generate(CLOSE, directory)
            self.assertTrue(all((directory / fixture).read_bytes() == before[fixture] for fixture in FIXTURES))

    def test_temporary_generation_rounding_masks_translations_and_rerun(self):
        generate = MASTER["generate_reference_data"]
        with tempfile.TemporaryDirectory(prefix="fourier-generated-") as name:
            directory = Path(name)
            for fixture in FIXTURES:
                shutil.copyfile(DIRECTORY / fixture, directory / fixture)
            with patch.dict(generate.__globals__, REFERENCE_CASES_CONFIRMED=True), contextlib.redirect_stdout(io.StringIO()):
                generate(CLOSE, directory)
                before = {fixture: (directory / fixture).read_bytes() for fixture in FIXTURES}
                generate(CLOSE, directory)
            self.assertTrue(all((directory / fixture).read_bytes() == before[fixture] for fixture in FIXTURES))
            written = runpy.run_path(str(directory / "test_testdata.py"))
            self.assertEqual(len([key for key in written if key.startswith("EXPECTED_")]), 40)
            for key in ("INPUT_CLOSE", "INPUT_HIGH", "INPUT_LOW", "INPUT_OPEN"):
                self.assertEqual(written[key], DATA[key])
            languages = (
                ("testdata_test.go", r"var expected(\w+) = \[\]float64\{\s*(.*?)\n\}", "math.NaN()"),
                ("testdata.ts", r"export const expected(\w+): number\[\] = \[\s*(.*?)\n\];", "NaN"),
                ("testdata.rs", r"pub fn expected_(\w+)\(\) -> Vec<f64> \{\n    vec!\[\s*(.*?)\n    \]\n\}", "f64::NAN"),
                ("testdata.zig", r"pub fn expected(\w+)\(\) \[252\]f64 \{\n    return \.\{\s*(.*?)\n    \};\n\}", "nan"),
            )
            for filename, pattern, nan in languages:
                text = (directory / filename).read_text()
                matches = re.findall(pattern, text, re.DOTALL)
                self.assertEqual(len(matches), 40, filename)
                for suffix, body in matches:
                    expected = written["EXPECTED_" + suffix.upper()]
                    values = [math.nan if token.strip() == nan else float(token)
                              for token in body.split(",") if token.strip()]
                    self.assertEqual(len(values), 252)
                    self.assertTrue(all(close_or_nan(x, y, 0.0) for x, y in zip(values, expected)), (filename, suffix))
                for case in CASES:
                    comments = f"// {case.what_it_tests}\n// {MASTER['_parameter_comment'](case)}\n"
                    self.assertEqual(text.count(comments), 2)
            for case in CASES:
                indicator = Indicator(case.fundamental)
                raw = [indicator.update(price) for price in CLOSE]
                for component, prefix in (("WAVE", case.fundamental - 1), ("ROC", case.fundamental + 1)):
                    values = written[f"EXPECTED_F{case.fundamental}_{component}"]
                    n = min(prefix, 252)
                    self.assertTrue(all(math.isnan(x) for x in values[:n]))
                    self.assertTrue(all(math.isfinite(x) for x in values[n:]))
                    self.assertEqual(values[n:], [float(format(getattr(x, component.lower()), ".15g")) for x in raw[n:]])


if __name__ == "__main__":
    unittest.main()
