"""Independent source, analytic and fixture verification for the RSI-NET master.

Source-expression checks use the supplied article in this repository. The
master class, mathematical documentation and data fixtures are self-contained
for conversion. Confirmed expected fixtures are required; checks inspect
every scalar, array name and preceding comment in all five languages.
"""

import ast
import importlib.util
import math
from pathlib import Path
import re
import unittest


DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("rsi_net_master", DIRECTORY / "rsi-net.py")
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
INPUTS = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")["INPUT_CLOSE"]
ARTICLE = DIRECTORY.parent.parent / "tasc/2020-12-noise-elimination-technology/content.md"


def source_expressions():
    """Extract source assignments, preserving left-associated CU/CD arithmetic."""
    code = re.findall(r"```easylanguage\n(.*?)```", ARTICLE.read_text(), re.S)[-1]
    expressions = {}
    for name in ("CU", "CD", "MyRSI", "Num", "Denom", "NET"):
        matches = re.findall(r"\b" + name + r"\s*=\s*(.*?);", code, re.S)
        expression = " ".join(matches[-1].split())
        expressions[name] = compile(expression, "<supplied EasyLanguage>", "eval")
    return expressions


def literal_source_outputs(prices, rsi_length, net_length):
    """Batch-evaluate extracted expressions with full observed-window priming.

    No missing close/RSI values are synthesized. This interpreter uses the
    source's one-based X and nested loops, unlike the master's zero-based lists.
    """
    expressions = source_expressions()
    scope = {"NETLength": net_length, "MyRSI": 0.0,
             "Sign": lambda value: (value > 0) - (value < 0)}
    history = []
    results = []
    for t in range(len(prices)):
        myrsi, net = math.nan, math.nan
        if t >= rsi_length:
            scope["Close"] = list(reversed(prices[:t + 1]))
            scope["CU"], scope["CD"] = 0.0, 0.0
            for count in range(rsi_length):
                scope["count"] = count
                difference = scope["Close"][count] - scope["Close"][count + 1]
                if difference > 0:
                    scope["CU"] = eval(expressions["CU"], {"__builtins__": {}}, scope)
                if difference < 0:
                    scope["CD"] = eval(expressions["CD"], {"__builtins__": {}}, scope)
            if scope["CU"] + scope["CD"] != 0:
                scope["MyRSI"] = eval(expressions["MyRSI"], {"__builtins__": {}}, scope)
            myrsi = scope["MyRSI"]
            history.append(myrsi)
            if len(history) >= net_length:
                scope["X"] = [0.0] + list(reversed(history[-net_length:]))
                scope["Num"] = 0.0
                for count in range(2, net_length + 1):
                    scope["count"] = count
                    for k in range(1, count):
                        scope["K"] = k
                        scope["Num"] = eval(expressions["Num"], {"__builtins__": {}}, scope)
                scope["Denom"] = eval(expressions["Denom"], {"__builtins__": {}}, scope)
                net = eval(expressions["NET"], {"__builtins__": {}}, scope)
        results.append(MASTER.RSIOutput(myrsi, net))
    return results


def chronological_tau(values):
    """Independent chronological concordance count; explicit ties in denominator."""
    concordant = discordant = tied = 0
    for earlier in range(len(values) - 1):
        for later in range(earlier + 1, len(values)):
            if values[later] > values[earlier]:
                concordant += 1
            elif values[later] < values[earlier]:
                discordant += 1
            else:
                tied += 1
    return (concordant - discordant) / (concordant + discordant + tied)


def translated_arrays(language):
    """Read generated array values with their exact two preceding comments."""
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


class TestRSINet(unittest.TestCase):
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

    def test_all_cases_match_extracted_article_expressions(self):
        for case in MASTER.REFERENCE_CASES:
            with self.subTest(parameters=case[:2]):
                indicator = MASTER.RSINet(*case[:2])
                actual = [indicator.update(close) for close in INPUTS]
                expected = literal_source_outputs(INPUTS, *case[:2])
                self.assert_outputs(actual, expected, exact=True)

    def test_independent_chronological_pair_count(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.RSINet(*case[:2])
            results = [indicator.update(close) for close in INPUTS]
            for t in range(indicator.net_warmup_bars, len(INPUTS)):
                values = [result.myrsi for result in results[t - case.net_length + 1:t + 1]]
                self.assertEqual(results[t].net, chronological_tau(values))

    def test_staged_priming_and_record_boundaries(self):
        for rsi_length, net_length in ((1, 2), (14, 14), (14, 100), (251, 2), (252, 14), (152, 100)):
            indicator = MASTER.RSINet(rsi_length, net_length)
            self.assertFalse(indicator.is_primed)
            self.assertTrue(all(math.isnan(value) for value in indicator.output))
            for t, close in enumerate(INPUTS):
                result = indicator.update(close)
                self.assertEqual(result._fields, ("myrsi", "net"))
                self.assertEqual(math.isnan(result.myrsi), t < rsi_length)
                self.assertEqual(math.isnan(result.net), t < rsi_length + net_length - 1)
                self.assertEqual(indicator.is_primed, t >= rsi_length + net_length - 1)
                self.assertIs(indicator.output, result)

    def test_constant_and_price_ramp(self):
        for rsi_length, net_length in ((1, 2), (5, 5), (14, 14)):
            for direction in (0.0, 0.5, -0.5):
                indicator = MASTER.RSINet(rsi_length, net_length)
                for t in range(60):
                    result = indicator.update(100.0 + direction * t)
                    if t >= rsi_length:
                        self.assertEqual(result.myrsi, (direction > 0) - (direction < 0))
                    if t >= indicator.net_warmup_bars:
                        # Rising price can make MyRSI persist at +1, yielding
                        # all rank ties and NET zero rather than NET +1.
                        self.assertEqual(result.net, 0.0)

    def test_zero_denominator_retains_previous_myrsi(self):
        indicator = MASTER.RSINet(2, 3)
        results = [indicator.update(value) for value in [10.0, 12.0, 11.0] + [11.0] * 8]
        self.assert_scalar(results[2].myrsi, 1.0 / 3.0)
        self.assertEqual(results[3].myrsi, -1.0)
        # At index 4 the two differences are zero: no assignment in source.
        self.assertEqual(results[4].myrsi, -1.0)
        self.assert_scalar(results[4].net, -2.0 / 3.0)
        self.assertEqual(results[5].net, 0.0)
        self.assertTrue(indicator.is_primed)

    def test_ties_keep_full_tau_a_denominator(self):
        # rsi_length=1 on nonzero price changes yields exact +/-1 MyRSIs.
        # Chronological MyRSIs [+1,-1,+1] have one tied pair and net zero.
        indicator = MASTER.RSINet(1, 3)
        outputs = [indicator.update(value) for value in [0.0, 1.0, 0.0, 1.0, 2.0]]
        self.assertEqual(outputs[3].net, 0.0)
        # Last three values [-1,+1,+1] give two concordant pairs, one tie.
        self.assert_scalar(outputs[4].net, 2.0 / 3.0, exact=True)

    def test_rising_and_falling_myrsi_rank_direction(self):
        for negate in (False, True):
            indicator = MASTER.RSINet(3, 3)
            prices = [0.0, -3.0, -5.0, -6.0, -5.0, -3.0, 0.0]
            if negate:
                prices = [-value for value in prices]
            outputs = [indicator.update(value) for value in prices]
            self.assertEqual(outputs[5].net, -1.0 if negate else 1.0)
            self.assertEqual(outputs[6].net, -1.0 if negate else 1.0)

    def test_exact_ties_have_no_epsilon(self):
        # Feed candidate prices that yield representably distinct MyRSIs
        # within 1e-12. Their true order must still affect the NET count.
        indicator = MASTER.RSINet(2, 2)
        outputs = [indicator.update(value) for value in [0.0, 1.0, 0.0, 1.0 + 1e-14]]
        self.assertNotEqual(outputs[2].myrsi, outputs[3].myrsi)
        self.assertLess(abs(outputs[3].myrsi - outputs[2].myrsi), 1e-12)
        self.assertEqual(outputs[3].net, 1.0)

    def test_literal_accumulation_order_is_not_reassociated(self):
        prices = [float(2**53), 1.0, float(2**53), float(2**53 + 2), 1.0, 3.0, 0.0, 2.0]
        indicator = MASTER.RSINet(3, 2)
        actual = [indicator.update(value) for value in prices]
        expected = literal_source_outputs(prices, 3, 2)
        self.assert_outputs(actual, expected, exact=True)

    def test_net_length_does_not_change_myrsi(self):
        reference = MASTER.RSINet(14, 2)
        expected = [reference.update(close).myrsi for close in INPUTS]
        for net_length in (5, 14, 30, 100):
            indicator = MASTER.RSINet(14, net_length)
            actual = [indicator.update(close).myrsi for close in INPUTS]
            for left, right in zip(actual, expected):
                self.assert_scalar(left, right, exact=True)

    def test_reset_and_causal_prefixes(self):
        indicator = MASTER.RSINet()
        full = [indicator.update(close) for close in INPUTS]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertEqual(indicator.rsi_length, 14)
        self.assertEqual(indicator.net_length, 14)
        self.assert_outputs([indicator.update(close) for close in INPUTS], full, exact=True)
        for stop in (14, 15, 27, 28, 100):
            prefix = MASTER.RSINet()
            self.assert_outputs([prefix.update(close) for close in INPUTS[:stop]], full[:stop], exact=True)

    def test_invalid_parameters_and_transactional_rejection(self):
        for parameters in ({"rsi_length": 0}, {"rsi_length": -1}, {"rsi_length": 14.0},
                           {"rsi_length": True}, {"net_length": 1}, {"net_length": 101},
                           {"net_length": 14.0}, {"net_length": True}):
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                MASTER.RSINet(**parameters)
        indicator, reference = MASTER.RSINet(), MASTER.RSINet()
        for close in INPUTS[:40]:
            indicator.update(close)
            reference.update(close)
        before = indicator.output
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                indicator.update(value)
            self.assertIs(before, indicator.output)
        self.assertEqual(indicator.update(INPUTS[40]), reference.update(INPUTS[40]))
        extreme = MASTER.RSINet(1, 2)
        before = extreme.update(-1e308)
        with self.assertRaises(ValueError):
            extreme.update(1e308)
        self.assertIs(before, extreme.output)
        self.assertEqual(extreme._bars, 1)

    def test_embedded_and_copied_input_integrity(self):
        parent = MASTER._load_literal_arrays(DIRECTORY.parent / "test_testdata.py")
        copied = MASTER._load_literal_arrays(DIRECTORY / "test_testdata.py")
        for name, values in parent.items():
            if name.startswith("INPUT_"):
                self.assertEqual(copied[name], values)
                self.assertEqual(len(values), 252)
        module_ast = ast.parse((DIRECTORY / "rsi-net.py").read_text())
        embedded = [node for node in ast.walk(module_ast)
                    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                    and target.id == "INPUT_CLOSE" for target in node.targets)]
        self.assertEqual(len(embedded), 1)
        self.assertEqual(ast.literal_eval(embedded[0].value), INPUTS)
        for filename in ("testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig"):
            original = (DIRECTORY.parent / filename).read_text()
            copied_text = (DIRECTORY / filename).read_text().split("BEGIN GENERATED")[0]
            self.assertEqual(re.findall(r"-?\d+\.\d{6}(?!\d)", copied_text),
                             re.findall(r"-?\d+\.\d{6}(?!\d)", original))

    def test_expected_data_in_all_five_languages(self):
        python_path = DIRECTORY / "test_testdata.py"
        written = MASTER._load_literal_arrays(python_path)
        names = {name for name in written if name.startswith("EXPECTED_")}
        self.assertTrue(names, "Confirmed expected fixtures must be generated")
        wanted = {"EXPECTED_" + MASTER._case_suffix(case) + "_" + token
                  for case in MASTER.REFERENCE_CASES for token in MASTER.OUTPUT_TOKENS}
        self.assertEqual(names, wanted)
        translated = {language: translated_arrays(language) for language in ("go", "ts", "rs", "zig")}
        for language, arrays in translated.items():
            language_names = {"expected_" + name[9:].lower() if language == "rs"
                              else "expected" + name[9:] for name in wanted}
            self.assertEqual(set(arrays), language_names)
        python_text = python_path.read_text()
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.RSINet(*case[:2])
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
