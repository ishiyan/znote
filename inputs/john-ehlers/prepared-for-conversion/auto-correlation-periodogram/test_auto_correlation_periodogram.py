"""Source transcription, source-specific semantics, and five-language parity.

Only Python's standard library is used. The independent reference stores the
whole chronological record and directly indexes source histories, rather than
using the master's bounded streaming buffers or Fourier coefficient tables.
"""

import ast
import math
from pathlib import Path
import re
import runpy
import unittest


DIRECTORY = Path(__file__).resolve().parent
MASTER = runpy.run_path(str(DIRECTORY / "auto-correlation-periodogram.py"))
Indicator = MASTER["AutoCorrelationPeriodogram"]
CASES = MASTER["REFERENCE_CASES"]
DATA = runpy.run_path(str(DIRECTORY / "test_testdata.py"))
CLOSE = DATA["INPUT_CLOSE"]


def source_reference(prices, case):
    """Direct batch translation of the chosen EasyLanguage calculation.

    Zero prehistory; retained raw correlations; fourth-power Fourier EMA;
    book code decay 0.995; corrected complete-turn angle; article enhancement
    BEFORE centroid; book enhancement AFTER centroid. No public NaN masking.
    Coefficients are written in degree-based source notation for independence.
    """
    book = case.source == "book"
    hp, filtered = [], []
    correlations = [0.0] * (case.max_period + 1)
    powers = [0.0] * (case.max_period - case.min_period + 1)
    maximum = dominant = 0.0
    has_dominant = False
    records = []
    ss_angle = math.radians(math.sqrt(2.0) * 180.0 / case.min_period)
    a = math.exp(-math.sqrt(2.0) * math.pi / case.min_period)
    c2, c3 = 2.0 * a * math.cos(ss_angle), -a * a
    c1 = 1.0 - c2 - c3
    hp_angle = math.radians(360.0 / case.max_period)
    article_pole = (1.0 - math.sin(hp_angle)) / math.cos(hp_angle)
    hp_angle = math.radians((1.0 / math.sqrt(2.0)) * 360.0 / case.max_period)
    alpha = (math.cos(hp_angle) + math.sin(hp_angle) - 1.0) / math.cos(hp_angle)

    def old(series, index):
        return series[index] if index >= 0 else 0.0

    for t, price in enumerate(prices):
        if book:
            h = ((1.0 - alpha / 2.0) * (1.0 - alpha / 2.0)
                 * (price - 2.0 * old(prices, t - 1) + old(prices, t - 2))
                 + 2.0 * (1.0 - alpha) * old(hp, t - 1)
                 - (1.0 - alpha) * (1.0 - alpha) * old(hp, t - 2))
        else:
            h = (0.5 * (1.0 + article_pole) * (price - old(prices, t - 1))
                 + article_pole * old(hp, t - 1))
        hp.append(h)
        f = (c1 * (h + old(hp, t - 1)) / 2.0
             + c2 * old(filtered, t - 1) + c3 * old(filtered, t - 2))
        filtered.append(f)
        for lag in range(case.max_period + 1):
            m = case.averaging_length or lag
            sx = sy = sxx = syy = sxy = 0.0
            for j in range(m):
                x, y = old(filtered, t - j), old(filtered, t - lag - j)
                sx += x
                sy += y
                sxx += x * x
                sxy += x * y
                syy += y * y
            d = (m * sxx - sx * sx) * (m * syy - sy * sy)
            if d > 0.0:
                correlations[lag] = (m * sxy - sx * sy) / math.sqrt(d)
        for b, period in enumerate(range(case.min_period, case.max_period + 1)):
            cp = sp = 0.0
            for lag in range(3, case.max_period + 1):
                angle = math.radians(360.0 * lag / period)
                cp += correlations[lag] * math.cos(angle)
                sp += correlations[lag] * math.sin(angle)
            q = cp * cp + sp * sp
            powers[b] = 0.2 * q * q + 0.8 * powers[b]
        maximum = 0.995 * maximum if book else 0.0
        for p in powers:
            if p > maximum:
                maximum = p
        normalized = [p / maximum if maximum > 0.0 else 0.0 for p in powers]
        weights = [p ** 3 for p in normalized] if not book and case.enhance_resolution else normalized
        spx = sp = 0.0
        for b, p in enumerate(weights):
            if (book and p >= 0.5) or (not book and max(weights) >= 0.25 and p >= 0.25):
                spx += (case.min_period + b) * p
                sp += p
        candidate = spx / sp if sp != 0.0 else 0.0
        if book and sp == 0.0 or not book and sp < 0.25:
            candidate = dominant
        elif sp != 0.0:
            has_dominant = True
        dominant = candidate
        display = [p ** 2 for p in normalized] if book and case.enhance_resolution else weights
        records.append((h, f, correlations[:], powers[:], maximum, dominant, display, has_dominant))
    return records


def same_number(a, b, tolerance=2e-10):
    return math.isnan(a) and math.isnan(b) or math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)


def same_tree(a, b, tolerance=0.0):
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(same_tree(x, y, tolerance) for x, y in zip(a, b))
    return same_number(a, b, tolerance)


class PeriodogramTests(unittest.TestCase):
    def test_every_case_matches_independent_source_transcription(self):
        for case in CASES:
            with self.subTest(case=MASTER["_case_suffix"](case)):
                reference = source_reference(CLOSE, case)
                indicator = Indicator(case.min_period, case.max_period, case.averaging_length,
                                      case.enhance_resolution, case.source)
                for t, price in enumerate(CLOSE):
                    result = indicator.update(price)
                    h, f, corr, power, maximum, dominant, display, has_dominant = reference[t]
                    state = indicator.state
                    for x, y in ((state.high_pass, h), (state.filtered, f),
                                 (state.normalization_maximum, maximum), (state.internal_dominant_cycle, dominant)):
                        self.assertTrue(same_number(x, y), (case, t, x, y))
                    for x, y in zip(state.correlations, corr):
                        self.assertTrue(same_number(x, y), (case, t, "correlation", x, y))
                    for x, y in zip(state.smoothed_power, power):
                        self.assertTrue(same_number(x, y), (case, t, "power", x, y))
                    primed = t >= indicator.warmup_bars
                    self.assertEqual(indicator.is_primed, primed)
                    if primed:
                        self.assertTrue(same_tree(result.heatmap.values, display, 2e-10), (case, t))
                        self.assertTrue(same_number(result.heatmap.value_min, min(display)))
                        self.assertTrue(same_number(result.heatmap.value_max, max(display)))
                    else:
                        self.assertTrue(result.heatmap.is_empty())
                        self.assertTrue(math.isnan(result.heatmap.value_min))
                        self.assertTrue(math.isnan(result.heatmap.value_max))
                    expected_dc = dominant if primed and has_dominant else math.nan
                    self.assertTrue(same_number(result.dominant_cycle, expected_dc), (case, t))

    def test_enhancement_placement_and_book_hold(self):
        records = {}
        for source in ("article", "book"):
            for enhanced in (False, True):
                x = Indicator(enhance_resolution=enhanced, source=source)
                records[source, enhanced] = [x.update(v) for v in CLOSE]
        for t in range(50, 252):
            plain, enhanced = records["book", False][t], records["book", True][t]
            self.assertEqual(plain.dominant_cycle, enhanced.dominant_cycle)
            self.assertEqual(enhanced.heatmap.values, [v * v for v in plain.heatmap.values])
            plain, enhanced = records["article", False][t], records["article", True][t]
            self.assertEqual(enhanced.heatmap.values, [v * v * v for v in plain.heatmap.values])
            self.assertEqual(plain.heatmap.value_max, 1.0)
        self.assertNotEqual(records["article", False][-1].dominant_cycle,
                            records["article", True][-1].dominant_cycle)
        book = records["book", False]
        holds = [i for i in range(51, 252) if book[i].heatmap.value_max < 0.5]
        self.assertTrue(holds)
        for i in holds:
            self.assertEqual(book[i].dominant_cycle, book[i - 1].dominant_cycle)

    def test_zero_power_and_retained_undefined_correlation(self):
        for source in ("article", "book"):
            x = Indicator(source=source)
            for _ in range(100):
                result = x.update(0.0)
            self.assertTrue(x.is_primed)
            self.assertTrue(math.isnan(result.dominant_cycle))
            self.assertEqual(result.heatmap.values, [0.0] * len(result.heatmap.values))
            # A zero denominator must retain RAW correlation, not reset it or
            # reapply the separate autocorrelation indicator's [0,1] mapping.
            x._correlations[12] = 0.75
            x.update(0.0)
            self.assertEqual(x.state.correlations[12], 0.75)

    def test_sine_peak_and_full_precision_basis(self):
        x = Indicator()
        for i in range(1000):
            result = x.update(100.0 + math.sin(2.0 * math.pi * i / 20.0))
        peak = result.heatmap.parameter_first + result.heatmap.values.index(max(result.heatmap.values))
        self.assertEqual(peak, 20.0)
        self.assertTrue(18.0 < result.dominant_cycle < 22.0)
        self.assertEqual(MASTER["SQRT_TWO"], math.sqrt(2.0))
        self.assertEqual(MASTER["INVERSE_SQRT_TWO"], 1.0 / math.sqrt(2.0))
        self.assertEqual(x._cosines[0][0], math.cos(2.0 * math.pi * 3.0 / 8.0))

    def test_skipped_nan_overflow_and_reset_are_deterministic(self):
        x = Indicator()
        first = [x.update(v) for v in CLOSE]
        state, output, count = x.state, x.output, x.samples_seen
        skipped = x.update(math.nan)
        self.assertTrue(skipped.heatmap.is_empty())
        self.assertTrue(math.isnan(skipped.dominant_cycle))
        self.assertIs(x.state, state)
        self.assertIs(x.output, output)
        self.assertEqual(x.samples_seen, count)
        for bad in (math.inf, -math.inf, 1e308):
            with self.assertRaises(ValueError):
                x.update(bad)
            self.assertIs(x.state, state)
            self.assertEqual(x.samples_seen, count)
        x.reset()
        second = [x.update(v) for v in CLOSE]
        for a, b in zip(first, second):
            self.assertTrue(same_tree(a.heatmap.values, b.heatmap.values))
            self.assertTrue(same_number(a.dominant_cycle, b.dominant_cycle, 0.0))
        # Updating another sample never mutates an already returned column.
        saved = second[-1].heatmap.values[:]
        x.update(110.0)
        self.assertEqual(saved, second[-1].heatmap.values)
        self.assertEqual(len(x._filtered), 51)

    def test_parameters_and_embedded_close_data(self):
        self.assertEqual(Indicator().parameters.min_period, 8)
        self.assertEqual(Indicator(source="book").parameters.min_period, 10)
        self.assertEqual(Indicator().warmup_bars, 50)
        self.assertEqual(Indicator(averaging_length=0).warmup_bars, 95)
        for kwargs in ({"min_period": 2}, {"min_period": True}, {"min_period": 8.0},
                       {"max_period": 8}, {"max_period": 4}, {"averaging_length": 1},
                       {"averaging_length": -1}, {"averaging_length": False},
                       {"source": "literal370"}, {"enhance_resolution": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Indicator(**kwargs)
        self.assertEqual(Indicator(averaging_length=2).parameters.averaging_length, 2)
        with self.assertRaises(AttributeError):
            Indicator().parameters = None
        tree = ast.parse((DIRECTORY / "auto-correlation-periodogram.py").read_text())
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "INPUT_CLOSE" for t in n.targets))
        self.assertEqual(ast.literal_eval(node.value), CLOSE)
        self.assertEqual(len(CLOSE), 252)
        self.assertEqual(len(CASES), 64)
        self.assertEqual(len({MASTER["_case_suffix"](c) for c in CASES}), 64)
        shared = runpy.run_path(str(DIRECTORY.parent / "test_testdata.py"))
        for field in ("INPUT_CLOSE", "INPUT_OPEN", "INPUT_HIGH", "INPUT_LOW"):
            self.assertEqual(DATA[field], shared[field])

    def test_generated_python_masks_rounding_and_dimensions(self):
        self.assertEqual(len([k for k in DATA if k.startswith("EXPECTED_")]), 256)
        description = (DIRECTORY / "description.md").read_text()
        for case in CASES:
            self.assertIn(case.what_it_tests, description)
            indicator = Indicator(case.min_period, case.max_period, case.averaging_length,
                                  case.enhance_resolution, case.source)
            outputs = [indicator.update(v) for v in CLOSE]
            suffix = MASTER["_case_suffix"](case)
            bins = case.max_period - case.min_period + 1
            for component in ("DC", "HEATMAP", "MIN", "MAX"):
                values = DATA["EXPECTED_" + suffix + "_" + component]
                self.assertEqual(len(values), 252)
                if component == "HEATMAP":
                    self.assertTrue(all(len(row) == bins for row in values))
                    raw = [o.heatmap.values or [math.nan] * bins for o in outputs]
                else:
                    raw = [o.dominant_cycle if component == "DC" else
                           o.heatmap.value_min if component == "MIN" else o.heatmap.value_max for o in outputs]
                for t, (written, expected) in enumerate(zip(values, raw)):
                    w = written if isinstance(written, list) else [written]
                    e = expected if isinstance(expected, list) else [expected]
                    for actual, value in zip(w, e):
                        rounded = math.nan if math.isnan(value) else float(format(value, ".15g"))
                        self.assertTrue(same_number(actual, rounded, 0.0), (case, component, t))
                    if t < indicator.warmup_bars:
                        self.assertTrue(all(math.isnan(v) for v in w))

    def test_all_other_languages_match_python_literals_and_comments(self):
        formats = (
            ("testdata_test.go", r"var expected(\w+) = (?:\[\]){1,2}float64\{\n(.*?)\n\}", "math.NaN()"),
            ("testdata.ts", r"export const expected(\w+): number\[\](?:\[\])? = \[\n(.*?)\n\];", "NaN"),
            ("testdata.rs", r"pub fn expected_(\w+)\(\) -> Vec<(?:Vec<)?f64>(?:>)? \{\n    vec!\[\n(.*?)\n    \]\n\}", "f64::NAN"),
            ("testdata.zig", r"pub fn expected(\w+)\(\) \[252\](?:\[\d+\])?f64 \{\n    return \.\{\n(.*?)\n    \};\n\}", "nan"),
        )
        for filename, pattern, nan in formats:
            text = (DIRECTORY / filename).read_text()
            matches = re.findall(pattern, text, re.DOTALL)
            self.assertEqual(len(matches), 256, filename)
            for suffix, body in matches:
                expected = DATA["EXPECTED_" + suffix.upper()]
                cleaned = body.replace(nan, "NaN").replace("vec![", "[").replace(".{", "[")
                cleaned = cleaned.replace("{", "[").replace("}", "]")
                literal = ast.parse("[" + cleaned + "]", mode="eval").body

                def decode(n):
                    if isinstance(n, ast.List):
                        return [decode(x) for x in n.elts]
                    if isinstance(n, ast.Name) and n.id == "NaN":
                        return math.nan
                    return float(ast.literal_eval(n))

                self.assertTrue(same_tree(decode(literal), expected), (filename, suffix))
            for case in CASES:
                comments = f"// {case.what_it_tests}\n// {MASTER['_parameter_comment'](case)}\n"
                self.assertEqual(text.count(comments), 4, (filename, case))


if __name__ == "__main__":
    unittest.main()
