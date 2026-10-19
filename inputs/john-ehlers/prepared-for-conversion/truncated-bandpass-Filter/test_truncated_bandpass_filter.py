"""Research verification against source expressions and independent FIR math.

Only source-expression verification needs the original repository article.
The Python master, description and generated fixtures are otherwise portable.
The confirmed fixtures are required; checks cover every value in all languages.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest


DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "truncated_bandpass_master", DIRECTORY / "truncated-bandpass-Filter.py")
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")["INPUT_CLOSE"]
ARTICLE = DIRECTORY.parent.parent / "tasc/2020-07-truncated-indicators/content.md"


def source_expressions():
    """Extract actual EasyLanguage assignments, not copied Python expressions."""
    text = ARTICLE.read_text()
    code = re.findall(r"```easylanguage\n(.*?)```", text, re.S)[-1]
    expressions = {}
    for name in ("L1", "G1", "S1", "BP", "Trunc[count]"):
        # Trunc[count] is assigned both by the stack and by the recurrence;
        # the LAST assignment is the actual filter expression we must test.
        matches = re.findall(re.escape(name) + r"\s*=\s*(.*?);", code, re.S)
        expression = matches[-1] if name == "Trunc[count]" else matches[0]
        expression = " ".join(expression.split())
        # A bare EasyLanguage Close means Close[0]. Keep delayed Close[k]
        # references exactly as printed while making the expression Python.
        expression = re.sub(r"\bClose\b(?!\s*\[)", "Close[0]", expression)
        expressions[name] = compile(expression, "<supplied EasyLanguage>", "eval")
    return expressions


def literal_source_outputs(prices, period, bandwidth, length):
    """Evaluate the supplied formulas and original 101-slot workspace shift.

    Apply explicit standalone availability without fabricating missing closes.
    NaNs are public masks, while source standard feedback remains numeric zero.
    """
    expressions = source_expressions()
    scope = {"Period": period, "Bandwidth": bandwidth,
             "Cosine": lambda degrees: math.cos(math.radians(degrees)),
             "SquareRoot": math.sqrt}
    for name in ("L1", "G1", "S1"):
        scope[name] = eval(expressions[name], {"__builtins__": {}}, scope)
    bp_history = []
    trunc = [0.0] * 101  # Source array has indices 0 through 100.
    results = []
    for t in range(len(prices)):
        if t < 3:
            bp = 0.0
        else:
            scope["Close"] = list(reversed(prices[:t + 1]))
            scope["BP"] = [0.0, bp_history[-1], bp_history[-2]]
            bp = eval(expressions["BP"], {"__builtins__": {}}, scope)
        bp_history.append(bp)

        # Keep the source's redundant stack to test that omitting it is safe.
        for count in range(100, 1, -1):
            trunc[count] = trunc[count - 1]
        if t >= length + 1:
            scope["Close"] = list(reversed(prices[:t + 1]))
            trunc[length + 2] = 0.0
            trunc[length + 1] = 0.0
            scope["Trunc"] = trunc
            for count in range(length, 0, -1):
                scope["count"] = count
                trunc[count] = eval(expressions["Trunc[count]"], {"__builtins__": {}}, scope)
            bpt = trunc[1]
        else:
            bpt = math.nan
        results.append(MASTER.BandpassOutput(bpt, bp if t >= 3 else math.nan))
    return results


def fir_weights(period, bandwidth, length):
    """Independent analytic expansion of the all-pole response, then numerator."""
    center = math.cos(2.0 * math.pi / period)
    gamma = math.cos(2.0 * math.pi * bandwidth / period)
    damping = 1.0 / gamma - math.sqrt(1.0 / gamma**2 - 1.0)
    drive = (1.0 - damping) / 2.0
    feedback = center * (1.0 + damping)
    q = [1.0]
    if length > 1:
        q.append(feedback)
    while len(q) < length:
        q.append(feedback * q[-1] - damping * q[-2])
    return drive, q, feedback, damping


def translated_arrays(language):
    """Read values plus the exact two preceding comments in each generated file."""
    patterns = {
        "go": ("testdata_test.go", r"// ([^\n]*)\n// ([^\n]*)\nvar (expected\w+) = \[\]float64\{(.*?)\n\}"),
        "ts": ("testdata.ts", r"// ([^\n]*)\n// ([^\n]*)\nexport const (expected\w+): number\[\] = \[(.*?)\n\];"),
        "rs": ("testdata.rs", r"// ([^\n]*)\n// ([^\n]*)\npub fn (expected_\w+)\(\) -> Vec<f64> \{\n\s*vec!\[(.*?)\n\s*\]\n\}"),
        "zig": ("testdata.zig", r"// ([^\n]*)\n// ([^\n]*)\npub fn (expected\w+)\(\) \[252\]f64 \{\n\s*return \.\{(.*?)\n\s*\};\n\}"),
    }
    filename, pattern = patterns[language]
    nan_token = {"go": "math.NaN()", "ts": "NaN", "rs": "f64::NAN", "zig": "nan"}[language]
    found = {}
    for what, parameters, name, body in re.findall(pattern, (DIRECTORY / filename).read_text(), re.S):
        tokens = [token.strip() for token in body.split(",") if token.strip()]
        values = [math.nan if token == nan_token else float(token) for token in tokens]
        if name in found:
            raise AssertionError(f"duplicate translated name: {name}")
        found[name] = (what, parameters, values, tokens)
    return found


class TestTruncatedBandpassFilter(unittest.TestCase):
    def assert_scalar(self, actual, expected, *, exact=False):
        if math.isnan(expected):
            self.assertTrue(math.isnan(actual))
        elif exact:
            self.assertEqual(actual, expected)
        else:
            self.assertTrue(math.isfinite(actual))
            self.assertTrue(math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12),
                            f"{actual!r} != {expected!r}")

    def assert_outputs(self, actual, expected, *, exact=False):
        self.assertEqual(len(actual), len(expected))
        for left, right in zip(actual, expected):
            for field in MASTER.OUTPUT_FIELDS:
                self.assert_scalar(getattr(left, field), getattr(right, field), exact=exact)

    def test_all_cases_match_actual_source_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case[:3]):
                indicator = MASTER.TruncatedBandpassFilter(*case[:3])
                actual = [indicator.update(value) for value in INPUTS]
                expected = literal_source_outputs(INPUTS, *case[:3])
                self.assert_outputs(actual, expected, exact=True)

    def test_independent_fir_convolution(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(case=case[:3]):
                indicator = MASTER.TruncatedBandpassFilter(*case[:3])
                actual = [indicator.update(value).truncated_bandpass for value in INPUTS]
                drive, q, _, _ = fir_weights(*case[:3])
                for t in range(case.length + 1, len(INPUTS)):
                    expected = drive * sum(q[k] * (INPUTS[t - k] - INPUTS[t - k - 2])
                                           for k in range(case.length))
                    self.assert_scalar(actual[t], expected)

    def test_field_specific_warmups_and_named_order(self):
        for length in (1, 2, 10, 97):
            indicator = MASTER.TruncatedBandpassFilter(length=length)
            self.assertEqual(indicator.warmup_bars, max(3, length + 1))
            self.assertFalse(indicator.is_primed)
            for t, close in enumerate(INPUTS[:101]):
                result = indicator.update(close)
                self.assertEqual(result._fields, ("truncated_bandpass", "bandpass"))
                self.assertEqual(math.isnan(result.bandpass), t < 3)
                self.assertEqual(math.isnan(result.truncated_bandpass), t < length + 1)
                self.assertEqual(indicator.is_primed, t >= max(3, length + 1))
                self.assertIs(result, indicator.output)

    def test_minimum_length_formulas(self):
        for length in (1, 2):
            drive, _, feedback, _ = fir_weights(20, 0.1, length)
            indicator = MASTER.TruncatedBandpassFilter(length=length)
            for t, close in enumerate(INPUTS):
                actual = indicator.update(close).truncated_bandpass
                if t >= length + 1:
                    expected = drive * (INPUTS[t] - INPUTS[t - 2])
                    if length == 2:
                        expected += feedback * drive * (INPUTS[t - 1] - INPUTS[t - 3])
                    self.assert_scalar(actual, expected)

    def test_constant_and_ramp_analytic_results(self):
        for length in (1, 2, 10, 97):
            constant = MASTER.TruncatedBandpassFilter(length=length)
            for _ in range(110):
                result = constant.update(123.0)
                for value in result:
                    if not math.isnan(value):
                        self.assertEqual(value, 0.0)
            drive, q, _, _ = fir_weights(20, 0.1, length)
            ramp = MASTER.TruncatedBandpassFilter(length=length)
            expected = 2.0 * drive * 0.5 * sum(q)
            for t in range(110):
                result = ramp.update(100.0 + t * 0.5)
                if t >= length + 1:
                    self.assert_scalar(result.truncated_bandpass, expected)

    def test_standard_startup_is_independent_of_length(self):
        reference = MASTER.TruncatedBandpassFilter(length=1)
        expected = [reference.update(close).bandpass for close in INPUTS]
        for length in (2, 5, 10, 40, 97):
            indicator = MASTER.TruncatedBandpassFilter(length=length)
            actual = [indicator.update(close).bandpass for close in INPUTS]
            for left, right in zip(actual, expected):
                self.assert_scalar(left, right, exact=True)
        drive, _, _, _ = fir_weights(20, 0.1, 1)
        self.assert_scalar(expected[3], drive * (INPUTS[3] - INPUTS[1]), exact=True)

    def test_impulse_expires_after_exact_finite_support(self):
        length, spike = 10, 30
        indicator = MASTER.TruncatedBandpassFilter(length=length)
        outputs = [indicator.update(1.0 if t == spike else 0.0) for t in range(100)]
        # A current impulse's last possible contribution is lag length+1.
        self.assertNotEqual(outputs[spike + length + 1].truncated_bandpass, 0.0)
        for result in outputs[spike + length + 2:]:
            self.assertEqual(result.truncated_bandpass, 0.0)
        self.assertTrue(any(result.bandpass != 0.0 for result in outputs[spike + length + 2:]))

    def test_same_tail_forgets_history_only_in_truncated_output(self):
        length = 10
        tail = INPUTS[-(length + 2):]
        first = MASTER.TruncatedBandpassFilter(length=length)
        second = MASTER.TruncatedBandpassFilter(length=length)
        for close in INPUTS[:100] + tail:
            left = first.update(close)
        for close in [500.0] * 100 + tail:
            right = second.update(close)
        self.assertEqual(left.truncated_bandpass, right.truncated_bandpass)
        self.assertNotEqual(left.bandpass, right.bandpass)

    def test_reset_and_causal_prefix(self):
        indicator = MASTER.TruncatedBandpassFilter()
        full = [indicator.update(close) for close in INPUTS]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertTrue(all(math.isnan(value) for value in indicator.output))
        replay = [indicator.update(close) for close in INPUTS]
        self.assert_outputs(replay, full, exact=True)
        for stop in (2, 4, 12, 37, 100):
            prefix = MASTER.TruncatedBandpassFilter()
            results = [prefix.update(close) for close in INPUTS[:stop]]
            self.assert_outputs(results, full[:stop], exact=True)

    def test_invalid_parameters_and_transactional_input_rejection(self):
        for kwargs in ({"period": 2}, {"period": 20.0}, {"period": True},
                       {"length": 0}, {"length": 98}, {"length": 1.5}, {"length": True},
                       {"bandwidth": 0}, {"bandwidth": -0.1}, {"bandwidth": 5},
                       {"bandwidth": math.nan}, {"bandwidth": math.inf}, {"bandwidth": True},
                       {"bandwidth": 1e-100}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                MASTER.TruncatedBandpassFilter(**kwargs)
        indicator = MASTER.TruncatedBandpassFilter()
        reference = MASTER.TruncatedBandpassFilter()
        for value in INPUTS[:30]:
            indicator.update(value)
            reference.update(value)
        before = indicator.output
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(value)
            self.assertIs(indicator.output, before)
        self.assertEqual(indicator.update(INPUTS[30]), reference.update(INPUTS[30]))
        # Individually finite operands can still overflow their difference.
        extreme = MASTER.TruncatedBandpassFilter(length=1)
        for value in (0.0, -1e308, 0.0):
            extreme.update(value)
        before = extreme.output
        with self.assertRaises(ValueError):
            extreme.update(1e308)
        self.assertIs(extreme.output, before)
        self.assertEqual(extreme._bars, 3)

    def test_embedded_and_copied_input_integrity(self):
        parent = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        copied = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        for name, values in parent.items():
            if name.startswith("INPUT_"):
                self.assertEqual(copied[name], values)
                self.assertEqual(len(values), 252)
        module_ast = ast.parse((DIRECTORY / "truncated-bandpass-Filter.py").read_text())
        embedded = [node for node in ast.walk(module_ast)
                    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                    and target.id == "INPUT_CLOSE" for target in node.targets)]
        self.assertEqual(len(embedded), 1)
        self.assertEqual(ast.literal_eval(embedded[0].value), INPUTS)
        # Expected generation must preserve every other-language input token.
        for filename in ("testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig"):
            original = (DIRECTORY.parent / filename).read_text()
            copied_text = (DIRECTORY / filename).read_text()
            input_tokens = re.findall(r"-?\d+\.\d{6}(?!\d)", original)
            self.assertEqual(re.findall(r"-?\d+\.\d{6}(?!\d)",
                                        copied_text.split("BEGIN GENERATED")[0]), input_tokens)

    def test_expected_data_in_all_five_languages(self):
        python_path = DIRECTORY / "test_testdata.py"
        written = MASTER._load_literal_arrays(python_path)
        expected_names = {name for name in written if name.startswith("EXPECTED_")}
        self.assertTrue(expected_names, "Confirmed expected fixtures must be generated")
        wanted = {"EXPECTED_" + MASTER._case_suffix(case) + "_" + token
                  for case in MASTER.REFERENCE_CASES for token in MASTER.OUTPUT_TOKENS}
        self.assertEqual(expected_names, wanted)
        translated = {language: translated_arrays(language) for language in ("go", "ts", "rs", "zig")}
        for language, arrays in translated.items():
            expected_language_names = {("expected_" + name[9:].lower()) if language == "rs"
                                       else ("expected" + name[9:]) for name in wanted}
            self.assertEqual(set(arrays), expected_language_names)
        python_text = python_path.read_text()
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.TruncatedBandpassFilter(*case[:3])
            actual = [indicator.update(close) for close in INPUTS]
            for field, token in zip(MASTER.OUTPUT_FIELDS, MASTER.OUTPUT_TOKENS):
                suffix = MASTER._case_suffix(case) + "_" + token
                name = "EXPECTED_" + suffix
                comments = f"# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\n{name} = ["
                self.assertIn(comments, python_text)
                expected = written[name]
                self.assertEqual(len(expected), 252)
                for index, value in enumerate(expected):
                    raw = getattr(actual[index], field)
                    self.assert_scalar(value, raw)
                    if not math.isnan(raw):
                        self.assertEqual(value, float(MASTER._float_literal(raw, "nan")))
                for language, arrays in translated.items():
                    other_name = "expected_" + suffix.lower() if language == "rs" else "expected" + suffix
                    what, parameters, values, tokens = arrays[other_name]
                    self.assertEqual(what, case.what_it_tests)
                    self.assertEqual(parameters, MASTER._parameter_comment(case))
                    self.assertEqual(len(values), 252)
                    nan_token = {"go": "math.NaN()", "ts": "NaN", "rs": "f64::NAN", "zig": "nan"}[language]
                    for value, expected_value, literal in zip(values, expected, tokens):
                        self.assert_scalar(value, expected_value, exact=True)
                        self.assertEqual(literal, MASTER._float_literal(expected_value, nan_token))


if __name__ == "__main__":
    unittest.main()
