"""Independent numerical and cross-language fixture verification tests.

Run via:
    python3 adaptive-super-smoother.py --verify
or:
    python3 -m unittest discover -s inputs/john-ehlers/prepared-for-conversion/adaptive-super-smoother
"""

from __future__ import annotations

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "adaptive_super_smoother_master", HERE / "adaptive-super-smoother.py"
)
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)


def article_batch(
    closes: list[float], period0: int | float = 20, rms_length: int = 81
) -> list[MASTER.AdaptiveSuperSmootherResult]:
    """Independent batch transcription of Ehlers' EasyLanguage listings.

    Written using full array histories and direct equations rather than calling
    the master's `_SuperSmoother` helper or ring buffer.
    """
    p0 = float(period0)
    ss_history: list[float] = []
    fixed_history: list[float] = []
    roc1_history: list[float] = []
    period = p0
    roc = 0.0
    outputs: list[MASTER.AdaptiveSuperSmootherResult] = []

    for t, price in enumerate(closes):
        price = float(price)
        current_bar = t + 1

        if current_bar < 4:
            ss = price
            fixed = price
        else:
            q_adapt = math.exp(-1.414 * 3.14159 / period)
            c1_adapt = (
                0.0
                if q_adapt == 0.0
                else 2.0 * q_adapt * math.cos((1.414 * 180.0 / period) * (math.pi / 180.0))
            )
            c2_adapt = q_adapt * q_adapt
            a0_adapt = (1.0 - c1_adapt + c2_adapt) / 2.0
            ss = (
                a0_adapt * (price + float(closes[t - 1]))
                + c1_adapt * ss_history[t - 1]
                - c2_adapt * ss_history[t - 2]
            )

            q_fix = math.exp(-1.414 * 3.14159 / p0)
            c1_fix = (
                0.0
                if q_fix == 0.0
                else 2.0 * q_fix * math.cos((1.414 * 180.0 / p0) * (math.pi / 180.0))
            )
            c2_fix = q_fix * q_fix
            a0_fix = (1.0 - c1_fix + c2_fix) / 2.0
            fixed = (
                a0_fix * (price + float(closes[t - 1]))
                + c1_fix * fixed_history[t - 1]
                - c2_fix * fixed_history[t - 2]
            )

        ss_history.append(ss)
        fixed_history.append(fixed)

        if t == 0:
            outputs.append(
                MASTER.AdaptiveSuperSmootherResult(
                    math.nan, math.nan, math.nan, math.nan
                )
            )
            continue

        roc1 = ss - ss_history[t - 1]
        roc1_history.append(roc1)

        if len(roc1_history) < rms_length:
            outputs.append(
                MASTER.AdaptiveSuperSmootherResult(
                    math.nan, math.nan, math.nan, math.nan
                )
            )
            continue

        sum_sq = 0.0
        for count in range(rms_length):
            diff = roc1_history[-1 - count]
            sum_sq = sum_sq + diff * diff
        rocrms = math.sqrt(sum_sq / rms_length) if sum_sq != 0.0 else 0.0
        if rocrms != 0.0:
            roc = abs(roc1 / rocrms)
        if roc > 2.0:
            roc = 2.0
        period = p0 * (1.0 - 0.5 * roc) * (1.0 - 0.5 * roc)
        if period < 2.0:
            period = 2.0

        outputs.append(
            MASTER.AdaptiveSuperSmootherResult(ss, fixed, ss - fixed, period)
        )

    return outputs


def literal_inputs(path: Path) -> dict[str, list[float]]:
    """Parse `INPUT_*` lists from `test_testdata.py` without executing code."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id.startswith("INPUT_")
    }


def parse_tokens(body: str, nan_token: str) -> list[float]:
    """Parse comma-separated numeric literals from a language fixture block."""
    tokens = [value.strip() for value in body.split(",") if value.strip()]
    return [math.nan if value == nan_token else float(value) for value in tokens]


class AdaptiveSuperSmootherTests(unittest.TestCase):
    def assert_number_equal(self, actual: float, expected: float) -> None:
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual), f"Expected NaN, got {actual!r}")
        else:
            self.assertTrue(math.isfinite(actual), f"Expected finite, got {actual!r}")
            self.assertTrue(
                math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12),
                f"{actual!r} != {expected!r}",
            )

    def assert_series_equal(self, actual, expected) -> None:
        self.assertEqual(len(actual), len(expected))
        for a, e in zip(actual, expected):
            self.assert_number_equal(a, e)

    def compare_to_article(
        self, closes: list[float], period0: int | float = 20, rms_length: int = 81
    ) -> list[MASTER.AdaptiveSuperSmootherResult]:
        indicator = MASTER.AdaptiveSuperSmoother(period0=period0, rms_length=rms_length)
        actual = [indicator.update(close) for close in closes]
        expected = article_batch(closes, period0=period0, rms_length=rms_length)
        self.assertEqual(len(actual), len(expected))
        for index, (a, e) in enumerate(zip(actual, expected)):
            with self.subTest(index=index, period0=period0, rms_length=rms_length):
                self.assert_series_equal(a, e)
        return actual

    def test_confirmed_grid_matches_independent_article(self) -> None:
        closes = MASTER.read_input_close()
        self.assertEqual(len(MASTER.REFERENCE_CASES), 16)
        for period0, rms_length, _ in MASTER.REFERENCE_CASES:
            self.compare_to_article(closes, period0, rms_length)

    def test_first_primed_bar_identity_and_subsequent_divergence(self) -> None:
        closes = MASTER.read_input_close()
        results = self.compare_to_article(closes, period0=20, rms_length=10)
        self.assertEqual(MASTER.AdaptiveSuperSmoother(20, 10).warmup_bars, 10)
        # Bars 0..9 are NaN; bar 10 is the first primed bar.
        self.assertTrue(all(math.isnan(v) for r in results[:10] for v in r))
        first_primed = results[10]
        self.assertTrue(all(math.isfinite(v) for v in first_primed))
        # On bar t = rms_length, adaptive and fixed have used period0 on every
        # bar up to and including t, so ss == fixed_ss and osc == 0.0.
        self.assertEqual(first_primed.ss, first_primed.fixed_ss)
        self.assertEqual(first_primed.osc, 0.0)
        self.assertLess(first_primed.period, 20.0)
        # On bar t = rms_length + 1, adaptive uses the newly tuned period, so
        # ss and fixed_ss diverge.
        self.assertNotEqual(results[11].ss, results[11].fixed_ss)
        self.assertNotEqual(results[11].osc, 0.0)

    def test_nyquist_floor_period_two_identity(self) -> None:
        closes = MASTER.read_input_close()
        results = self.compare_to_article(closes, period0=2, rms_length=81)
        for r in results[81:]:
            self.assertEqual(r.ss, r.fixed_ss)
            self.assertEqual(r.osc, 0.0)
            self.assertEqual(r.period, 2.0)

    def test_three_bar_supersmoother_passthrough_with_rms_length_two(self) -> None:
        closes = [100.0, 102.0, 101.0, 105.0, 103.0, 106.0]
        results = self.compare_to_article(closes, period0=20, rms_length=2)
        self.assertTrue(all(math.isnan(v) for r in results[:2] for v in r))
        # Index 2 is CurrentBar=3 (< 4), so both filters pass closes[2] through.
        self.assertEqual(results[2].ss, closes[2])
        self.assertEqual(results[2].fixed_ss, closes[2])
        self.assertEqual(results[2].osc, 0.0)
        # Index 3 is CurrentBar=4 (>= 4), where IIR filtering begins.
        self.assertNotEqual(results[3].ss, closes[3])
        self.assertNotEqual(results[3].fixed_ss, closes[3])

    def test_constant_series_retained_roc_and_two_sigma_clamping(self) -> None:
        flat_zero = self.compare_to_article([0.0] * 30, period0=20, rms_length=5)
        for r in flat_zero[5:]:
            self.assertEqual(r, (0.0, 0.0, 0.0, 20.0))

        flat_p10 = self.compare_to_article([50.0] * 30, period0=10, rms_length=5)
        for r in flat_p10[5:]:
            self.assertEqual(r, (50.0, 50.0, 0.0, 10.0))

        # Step during first 2 bars (while SS passes close through) then flat:
        # At t=1: SS=110 (passthrough), ROC1[1] = 10.
        # At t=2: SS=110 (passthrough), ROC1[2] = 0.
        # At t=3..6: Price=110, SS[t-1]=110, SS[t-2]=110 -> SS=110, ROC1=0!
        # With rms_length=4:
        #   t=4 has ROC1 window [10, 0, 0, 0] -> rocrms = 5, roc1 = 0 -> roc = 0.
        #What if the jump happens at t=2 (still passthrough!) and rms_length=1:
        #   t=0: 100, t=1: 110 (ROC1=10, rocrms=10, roc=1.0, period=5.0)
        #   t=2: 110 (CurrentBar=3 passthrough -> SS=110, ROC1=0, rocrms=0 -> retains roc=1.0!)
        step_retain = self.compare_to_article([100.0, 110.0, 110.0], period0=20, rms_length=1)
        self.assertEqual(step_retain[1].period, 5.0)
        # On t=2, ROC1=0 and ROCRMS=0, so retained ROC remains 1.0 and period stays 5.0!
        self.assertEqual(step_retain[2].period, 5.0)

        # Sharp jump after flat window of rms_length=4:
        # At jump bar, ROC1 = J != 0 while prior 3 ROC1s are 0 ->
        # ROCRMS = |J| / sqrt(4) = |J| / 2 -> |ROC1 / ROCRMS| = 2.0 -> period = 2.0.
        jump_prices = [100.0] * 6 + [120.0]
        jump_results = self.compare_to_article(jump_prices, period0=10, rms_length=4)
        self.assertEqual(jump_results[-1].period, 2.0)

    def test_invalid_parameters_and_updates_do_not_consume_bars(self) -> None:
        for bad_p0 in (True, False, "20", None):
            with self.assertRaises(TypeError):
                MASTER.AdaptiveSuperSmoother(period0=bad_p0)
        for bad_p0 in (0, -5, -0.1, math.nan, math.inf, -math.inf, 10**400):
            with self.assertRaises(ValueError):
                MASTER.AdaptiveSuperSmoother(period0=bad_p0)
        for bad_rms in (True, False, 10.0, "81", None):
            with self.assertRaises(TypeError):
                MASTER.AdaptiveSuperSmoother(rms_length=bad_rms)
        for bad_rms in (0, -1, -81):
            with self.assertRaises(ValueError):
                MASTER.AdaptiveSuperSmoother(rms_length=bad_rms)

        a = MASTER.AdaptiveSuperSmoother(period0=12, rms_length=3)
        b = MASTER.AdaptiveSuperSmoother(period0=12, rms_length=3)
        for close in (91.5, 94.815, 94.375, 95.095, 93.78, 94.625):
            for invalid, exc in (
                (None, TypeError),
                (True, TypeError),
                ("91.5", TypeError),
                (math.nan, ValueError),
                (math.inf, ValueError),
                (-math.inf, ValueError),
                (10**400, ValueError),
            ):
                with self.assertRaises(exc):
                    a.update(invalid)
            self.assert_series_equal(a.update(close), b.update(close))

        for prop in ("period0", "rms_length", "warmup_bars"):
            with self.assertRaises(AttributeError):
                setattr(a, prop, 10)

    def test_bounded_storage_and_positive_period_underflow(self) -> None:
        ind = MASTER.AdaptiveSuperSmoother(period0=20, rms_length=5)
        for i in range(400):
            ind.update(100.0 + math.sin(i * 0.2))
            self.assertEqual(len(ind._roc1_ring), 5)
            self.assertLessEqual(ind._roc1_count, 5)

        tiny = MASTER.AdaptiveSuperSmoother(period0=5e-324, rms_length=1)
        out = [tiny.update(c) for c in (10.0, 12.0, 14.0, 16.0, 18.0)]
        self.assertTrue(all(math.isnan(v) for v in out[0]))
        self.assertTrue(all(math.isfinite(v) for r in out[1:] for v in r))
        # At bar 3 (CurrentBar=4), fixed_ss uses tiny period0 where q=0 -> a0=0.5, c1=0, c2=0
        self.assertEqual(out[3].fixed_ss, 0.5 * (16.0 + 14.0))

    def test_last_bar_and_entirely_unprimed_windows(self) -> None:
        closes = MASTER.read_input_close()
        last = self.compare_to_article(closes, period0=20, rms_length=251)
        never = self.compare_to_article(closes, period0=20, rms_length=252)
        beyond = self.compare_to_article(closes, period0=20, rms_length=300)
        self.assertTrue(all(math.isnan(v) for r in last[:-1] for v in r))
        self.assertTrue(all(math.isfinite(v) for v in last[-1]))
        self.assertEqual(last[-1].ss, last[-1].fixed_ss)
        self.assertEqual(last[-1].osc, 0.0)
        self.assertTrue(all(math.isnan(v) for r in never + beyond for v in r))

    def test_saved_python_reference_data_matches_master(self) -> None:
        closes = MASTER.read_input_close()
        computed = MASTER.compute_reference_vectors(closes)
        saved = MASTER.read_serialized_vectors()
        self.assertEqual(len(saved), 64)
        for (name, explanation, parameters, tokens), expected in zip(saved, computed):
            self.assertEqual((name, explanation, parameters), expected[:3])
            canonical = [
                "NaN" if math.isnan(v) else format(v, ".15f") for v in expected[3]
            ]
            self.assertEqual(tokens, canonical)
            values = [math.nan if token == "NaN" else float(token) for token in tokens]
            self.assert_series_equal(values, expected[3])

        python_data: dict[str, object] = {}
        exec(
            compile(
                (HERE / "test_testdata.py").read_text(encoding="utf-8"),
                "test_testdata.py",
                "exec",
            ),
            python_data,
        )
        self.assertEqual(
            sum(k.startswith("EXPECTED_") for k in python_data), 64
        )
        for name, _, _, tokens in saved:
            self.assert_series_equal(
                python_data[name],
                [math.nan if t == "NaN" else float(t) for t in tokens],
            )

    def test_other_language_arrays_and_comments_match_python(self) -> None:
        saved = MASTER.read_serialized_vectors()
        languages = (
            (
                "testdata_test.go",
                r"^// ([^\n]+)\n// ([^\n]+)\nvar expected([A-Z0-9_]+) = \[\]float64\{\n(.*?)\n\}",
                "math.NaN()",
                False,
            ),
            (
                "testdata.ts",
                r"^// ([^\n]+)\n// ([^\n]+)\nexport const expected([A-Z0-9_]+): number\[\] = \[\n(.*?)\n\];",
                "NaN",
                False,
            ),
            (
                "testdata.rs",
                r"^    // ([^\n]+)\n    // ([^\n]+)\n    pub fn expected_([a-z0-9_]+)\(\) -> Vec<f64> \{\n        vec!\[\n(.*?)\n        \]\n    \}",
                "f64::NAN",
                True,
            ),
            (
                "testdata.zig",
                r"^// ([^\n]+)\n// ([^\n]+)\npub fn expected([A-Z0-9_]+)\(\) \[252\]f64 \{\n    return \.\{\n(.*?)\n    \};\n\}",
                "nan",
                False,
            ),
        )
        for filename, pattern, nan_token, lowercase in languages:
            text = (HERE / filename).read_text(encoding="utf-8")
            blocks = re.findall(pattern, text, re.M | re.S)
            self.assertEqual(len(blocks), 64, filename)
            for block, python in zip(blocks, saved):
                explanation, parameters, tag, body = block
                name, py_explanation, py_parameters, tokens = python
                py_tag = name.removeprefix("EXPECTED_")
                self.assertEqual(tag, py_tag.lower() if lowercase else py_tag)
                self.assertEqual(
                    (explanation, parameters), (py_explanation, py_parameters)
                )
                other = [t.strip() for t in body.split(",") if t.strip()]
                self.assertEqual(
                    other, [nan_token if t == "NaN" else t for t in tokens]
                )
                self.assertEqual(len(other), 252)

        go_text = (HERE / "testdata_test.go").read_text(encoding="utf-8")
        self.assertIn("package adaptivesupersmoother\n", go_text)
        self.assertIn('import "math"', go_text)
        zig_text = (HERE / "testdata.zig").read_text(encoding="utf-8")
        self.assertTrue(
            zig_text.startswith(
                'const math = @import("std").math;\nconst nan = math.nan(f64);\n'
            )
        )

    def test_inputs_preserved_in_every_language_and_embedded_main(self) -> None:
        inputs = literal_inputs(HERE / "test_testdata.py")
        self.assertEqual(
            set(inputs), {"INPUT_CLOSE", "INPUT_HIGH", "INPUT_LOW", "INPUT_OPEN"}
        )
        master_tree = ast.parse(
            (HERE / "adaptive-super-smoother.py").read_text(encoding="utf-8")
        )
        main_if = next(
            node for node in master_tree.body if isinstance(node, ast.If)
        )
        embedded = next(
            node for node in main_if.body if isinstance(node, ast.Assign)
        )
        self.assertEqual(ast.literal_eval(embedded.value), inputs["INPUT_CLOSE"])

        names = (
            ("INPUT_CLOSE", "testInput", "test_input"),
            ("INPUT_HIGH", "testHigh", "test_high"),
            ("INPUT_LOW", "testLow", "test_low"),
            ("INPUT_OPEN", "testOpen", "test_open"),
        )
        for py_name, mixed_name, rust_name in names:
            patterns = (
                ("testdata_test.go", rf"var {mixed_name} = \[\]float64\{{(.*?)\}}"),
                ("testdata.ts", rf"export const {mixed_name}: number\[\] = \[(.*?)\]"),
                (
                    "testdata.rs",
                    rf"pub fn {rust_name}\(\) -> Vec<f64> \{{\s*vec!\[(.*?)\]",
                ),
                (
                    "testdata.zig",
                    rf"pub fn {mixed_name}\(\) \[252\]f64 \{{\s*return \.\{{(.*?)\}}",
                ),
            )
            self.assertEqual(len(inputs[py_name]), 252)
            for filename, pattern in patterns:
                match = re.search(
                    pattern, (HERE / filename).read_text(encoding="utf-8"), re.S
                )
                self.assertIsNotNone(match, f"{filename} {mixed_name}")
                self.assertEqual(parse_tokens(match[1], "NaN"), inputs[py_name])

        parent = HERE.parent / "test_testdata.py"
        if parent.exists():
            self.assertEqual(inputs, literal_inputs(parent))


if __name__ == "__main__":
    unittest.main(verbosity=2)
