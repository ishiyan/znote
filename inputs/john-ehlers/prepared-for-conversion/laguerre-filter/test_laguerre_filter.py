"""Independent source, analytical and portable-fixture validation.

Run python3 -m unittest -v test_laguerre_filter.py in this indicator's directory.
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
SOURCE_DIRECTORY = DIRECTORY.parent.parent / 'tasc/2025-07-laguerre-filters'
TRADESTATION = (SOURCE_DIRECTORY / 'tips/TradeStation_LaguerreFilters.els').read_text()
ARTICLE = (SOURCE_DIRECTORY / 'content.md').read_text()
IS_FILTER = True
SPEC = importlib.util.spec_from_file_location('laguerre_master', DIRECTORY / 'laguerre-filter.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
ARRAYS = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
CLOSE = ARRAYS['INPUT_CLOSE']
CLASS = MASTER.LaguerreFilter


def assert_values(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for t, (a, e) in enumerate(zip(actual, expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a), (t, a, e))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a, e, rel_tol=tolerance, abs_tol=tolerance),
                            (t, a, e))


def source_smoother(prices, length, full_precision):
    """Evaluate actual TradeStation expressions independently in batch lists."""
    block = TRADESTATION.split('Function: $UltimateSmoother', 1)[1]
    coefficients = {'Period': length, 'PI': math.pi, 'SQRT_TWO': math.sqrt(2.0)}
    functions = {'ExpValue': math.exp,
                 'Cosine': math.cos if full_precision else lambda a: math.cos(math.radians(a))}
    for name in ('a1', 'b1', 'c2', 'c3', 'c1'):
        expression = re.search(r'\b' + name + r'\s*=\s*(.*?);', block).group(1)
        if full_precision:
            expression = expression.replace('1.414', 'SQRT_TWO').replace('3.14159', 'PI').replace('180', 'PI')
        coefficients[name] = eval(expression, {'__builtins__': {}}, functions | coefficients)
    recurrence = re.search(r'if CurrentBar >= 4 then\s+US\s*=\s*(.*?);', block, re.DOTALL | re.IGNORECASE).group(1)
    recurrence = recurrence.replace('Price[1]', 'p1').replace('Price[2]', 'p2').replace('US[1]', 'u1').replace('US[2]', 'u2')
    recurrence = ' '.join(recurrence.split())
    outputs = []
    for t, price in enumerate(prices):
        if t < 3:
            outputs.append(price)
        else:
            values = coefficients | {'Price': price, 'p1': prices[t - 1], 'p2': prices[t - 2],
                                     'u1': outputs[t - 1], 'u2': outputs[t - 2]}
            outputs.append(eval(recurrence, {'__builtins__': {}}, values))
    return outputs


def source_indicator(prices, length, gamma, full_precision=True, recurrence_mode='tradestation'):
    l0 = source_smoother(prices, length, full_precision)
    if IS_FILTER:
        block = TRADESTATION.split('Indicator: Laguerre Oscillator', 1)[0]
        expressions = [re.search(r'\bL' + str(n) + r'\s*=\s*(.*?);', block).group(1) for n in range(1, 5)]
        weighted = re.search(r'\bLaguerre\s*=\s*(.*?);', block).group(1)
        history = [(0.0,) * 5]
        result = {'laguerre': [], 'ultimate_smoother': l0, 'stages': []}
        for t, value in enumerate(l0):
            old = history[-1]
            namespace = {'Gama': gamma}
            current = [value]
            for expression in expressions:
                for n in range(5):
                    expression = expression.replace(f'L{n}[1]', f'old{n}')
                    namespace[f'old{n}'] = old[n]
                current.append(eval(expression, {'__builtins__': {}}, namespace))
            history.append(tuple(current))
            namespace.update({f'L{n}': current[n] for n in range(5)})
            result['laguerre'].append(eval(weighted, {'__builtins__': {}}, namespace))
            result['stages'].append(tuple(current))
        return result

    if recurrence_mode == 'article':
        blocks = re.findall(r'```easylanguage\n(.*?)```', ARTICLE, re.DOTALL)
        block = next(b for b in blocks if 'Laguerre Oscillator\n' in b)
    else:
        block = TRADESTATION.split('Indicator: Laguerre Oscillator', 1)[1].split('Function: $RMS', 1)[0]
    expression = re.search(r'\bL1\s*=\s*(.*?);', block).group(1)
    expression = expression.replace('Gama', 'gamma').replace('gama', 'gamma')
    expression = expression.replace('L0[1]', 'old0').replace('L1[1]', 'old1')
    result = {'oscillator': [], 'l0': l0, 'l1': [], 'signal': [], 'rms': []}
    old0 = old1 = rms = previous = 0.0
    rms_block = TRADESTATION.split('Function: $RMS', 1)[1].split('Function: $UltimateSmoother', 1)[0]
    square = re.search(r'SumSq = SumSq \+ (.*?);', rms_block).group(1).replace('Price[count]', 'value')
    root = re.search(r'If SumSq <> 0 then\s+\$RMS\s*=\s*(.*?);', rms_block, re.IGNORECASE).group(1)
    squares = []
    for t, value in enumerate(l0):
        l1 = eval(expression, {'__builtins__': {}}, {'gamma': gamma, 'L0': value, 'old0': old0, 'old1': old1})
        signal = value - l1
        old0, old1 = value, l1
        result['l1'].append(l1)
        result['signal'].append(signal)
        squares.append(eval(square, {'__builtins__': {}}, {'value': signal}))
        if t < 99:
            result['oscillator'].append(math.nan)
            result['rms'].append(math.nan)
        else:
            total = 0.0
            for lag in range(100):
                total = total + squares[t - lag]
            if total != 0:
                rms = eval(root, {'__builtins__': {}}, {'SumSq': total, 'Length': 100, 'SquareRoot': math.sqrt})
            if rms != 0:
                previous = signal / rms
            result['oscillator'].append(previous)
            result['rms'].append(rms)
    return result


class LaguerreTests(unittest.TestCase):
    def test_all_pairs_match_extracted_source_and_precision_options(self):
        for case in MASTER.REFERENCE_CASES:
            for precision in ('full_precision', 'article'):
                for recurrence in (('tradestation',) if IS_FILTER else ('tradestation', 'article')):
                    kwargs = {'coefficient_mode': precision}
                    if not IS_FILTER:
                        kwargs['recurrence_mode'] = recurrence
                    indicator = CLASS(case.length, case.gamma, **kwargs)
                    expected = source_indicator(CLOSE, case.length, case.gamma, precision == 'full_precision', recurrence)
                    actual = {field: [] for field in MASTER.OUTPUT_FIELDS}
                    for t, price in enumerate(CLOSE):
                        output = indicator.update(price)
                        for field in MASTER.OUTPUT_FIELDS:
                            actual[field].append(getattr(output, field) if IS_FILTER else output)
                        if IS_FILTER:
                            self.assertEqual(indicator.stages, expected['stages'][t])
                        else:
                            self.assertEqual(indicator.l0, expected['l0'][t])
                            self.assertEqual(indicator.l1, expected['l1'][t])
                            self.assertEqual(indicator.signal, expected['signal'][t])
                    for field in MASTER.OUTPUT_FIELDS:
                        assert_values(self, actual[field], expected[field], 0.0)

    def test_source_startup_and_output_availability(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = CLASS(case.length, case.gamma)
            self.assertFalse(indicator.is_primed)
            for t, close in enumerate(CLOSE):
                output = indicator.update(close)
                self.assertEqual(indicator._smoother._count, t + 1)
                self.assertEqual(indicator.is_primed, True if IS_FILTER else t >= 99)
                if IS_FILTER:
                    self.assertTrue(math.isfinite(output.laguerre))
                    if t == 0:
                        self.assertEqual(output.laguerre, close / 16)
                        self.assertEqual(indicator.stages, (close, 0, 0, 0, 0))
                else:
                    self.assertEqual(math.isnan(output), t < 99)
                    if t == 0:
                        self.assertEqual(indicator.l1, -case.gamma * close)
                if t < 3:
                    self.assertEqual(indicator._smoother._output1, close)

    def test_gamma_zero_has_analytic_delay_or_difference_limit(self):
        indicator = CLASS(20, 0)
        l0 = source_smoother(CLOSE, 20, True)
        for t, close in enumerate(CLOSE):
            output = indicator.update(close)
            if IS_FILTER:
                expected = sum(w * (l0[t - lag] if t >= lag else 0)
                               for lag, w in enumerate((1, 4, 6, 4, 1))) / 16
                self.assertAlmostEqual(output.laguerre, expected, places=12)
            else:
                self.assertEqual(indicator.l1, l0[t - 1] if t else 0)
                self.assertEqual(indicator.signal, l0[t] - (l0[t - 1] if t else 0))

    def test_constant_price_startup_and_long_term_behavior(self):
        gamma, price = 0.5, 8.0
        indicator = CLASS(20, gamma)
        for t in range(200):
            output = indicator.update(price)
            if IS_FILTER:
                self.assertAlmostEqual(indicator.stages[1], price * (1 - gamma ** t), places=12)
            else:
                self.assertAlmostEqual(indicator.signal, (1 + gamma) * price * gamma ** t, places=12)
        if IS_FILTER:
            self.assertAlmostEqual(output.laguerre, price, places=12)
        # A decaying raw signal and its decaying RMS need not imply the same
        # limit for their ratio; validate raw decay rather than inventing a bound.

    def test_actual_transfer_function_matches_long_sinusoid(self):
        length, gamma = 30, 0.8
        omega = 2 * math.pi / 25
        q = cmath.exp(-1j * omega)
        theta = math.sqrt(2) * math.pi / length
        a = math.exp(-theta)
        c2, c3 = 2 * a * math.cos(theta), -a * a
        c1 = (1 + c2 - c3) / 4
        u = ((1 - c1) + (2 * c1 - c2) * q - (c1 + c3) * q * q) / (1 - c2 * q - c3 * q * q)
        if IS_FILTER:
            stage = (1 - gamma) * q / (1 - gamma * q)
            response = u * (1 + stage) ** 4 / 16
        else:
            stage = (q - gamma) / (1 - gamma * q)
            self.assertAlmostEqual(abs(stage), 1.0, places=14)
            response = u * (1 - stage)
        indicator = CLASS(length, gamma)
        for t in range(1200):
            output = indicator.update(math.sin(omega * t))
            if t > 1000:
                expected = (response * cmath.exp(1j * omega * t)).imag
                actual = output.laguerre if IS_FILTER else indicator.signal
                self.assertAlmostEqual(actual, expected, places=11)
                if not IS_FILTER:
                    self.assertAlmostEqual(output, expected / (abs(response) / math.sqrt(2)), places=10)

    def test_stage_source_distinction_and_normalized_equivalence(self):
        if IS_FILTER:
            indicator = CLASS(40, 0.8)
            indicator.update(10)
            second = indicator.update(20)
            # Delayed source stage gives (1-gamma)*10=2; allpass would be -6.
            self.assertAlmostEqual(indicator.stages[1], 2.0, places=14)
            self.assertNotAlmostEqual(indicator.stages[1], -6.0, places=14)
        else:
            for gamma in (0, 0.2, 0.5, 0.8, 0.99):
                a, b = CLASS(30, gamma), CLASS(30, gamma, recurrence_mode='article')
                actual, article = [], []
                for close in CLOSE:
                    actual.append(a.update(close))
                    article.append(b.update(close))
                    self.assertTrue(math.isclose(a.signal, (1 + gamma) * b.signal, rel_tol=1e-11, abs_tol=1e-11))
                assert_values(self, actual, article, 1e-11)

    def test_zero_price_and_rms_persistent_conditions(self):
        indicator = CLASS()
        outputs = [indicator.update(0) for _ in CLOSE]
        if IS_FILTER:
            self.assertEqual(outputs, [MASTER.LaguerreFilterResult(0, 0)] * 252)
        else:
            self.assertTrue(all(math.isnan(v) for v in outputs[:99]))
            self.assertEqual(outputs[99:], [0.0] * 153)
            rms = MASTER.RootMeanSquare(2)
            self.assertTrue(math.isnan(rms.update(3)))
            self.assertEqual(rms.update(4), math.sqrt(25 / 2))
            self.assertEqual(rms.update(0), math.sqrt(16 / 2))
            self.assertEqual(rms.update(0), math.sqrt(16 / 2))

            class ControlledRMS:
                is_primed = True
                def __init__(self): self.values = iter((2.0, 0.0))
                def update(self, signal): return next(self.values)

            indicator = CLASS()
            indicator._rms_filter = ControlledRMS()
            first = indicator.update(10)
            self.assertEqual(indicator.update(11), first)

    def test_causality_reset_and_scale(self):
        a, b = CLASS(), CLASS()
        full = [a.update(p) for p in CLOSE]
        scaled = [b.update(8 * p) for p in CLOSE]
        for field in MASTER.OUTPUT_FIELDS:
            original = [getattr(v, field) for v in full] if IS_FILTER else full
            modified = [getattr(v, field) / 8 for v in scaled] if IS_FILTER else scaled
            assert_values(self, original, modified, 1e-11)
        prefix = CLASS()
        partial = [prefix.update(p) for p in CLOSE[:140]]
        for field in MASTER.OUTPUT_FIELDS:
            assert_values(self, [getattr(v, field) for v in partial] if IS_FILTER else partial,
                          [getattr(v, field) for v in full[:140]] if IS_FILTER else full[:140], 0.0)
        a.reset()
        self.assertFalse(a.is_primed)
        again = [a.update(p) for p in CLOSE]
        for field in MASTER.OUTPUT_FIELDS:
            assert_values(self, [getattr(v, field) for v in again] if IS_FILTER else again,
                          [getattr(v, field) for v in full] if IS_FILTER else full, 0.0)

    def test_invalid_configuration_and_missing_input_preserve_state(self):
        for length in (0, 0.5, -1, True, math.nan, math.inf):
            with self.assertRaises(ValueError): CLASS(length, 0.5)
        for gamma in (-0.1, 1, 1.1, True, math.nan, math.inf):
            with self.assertRaises(ValueError): CLASS(20, gamma)
        with self.assertRaises(ValueError): CLASS(coefficient_mode='bad')
        if not IS_FILTER:
            with self.assertRaises(ValueError): CLASS(recurrence_mode='all')
        a, b = CLASS(20.5, 0.8), CLASS(20.5, 0.8)
        self.assertEqual(a.length, 20.5)
        for p in CLOSE[:120]:
            a.update(p)
            b.update(p)
        for p in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError): a.update(p)
        aa, bb = [a.update(p) for p in CLOSE[120:]], [b.update(p) for p in CLOSE[120:]]
        for field in MASTER.OUTPUT_FIELDS:
            assert_values(self, [getattr(v, field) for v in aa] if IS_FILTER else aa,
                          [getattr(v, field) for v in bb] if IS_FILTER else bb, 0.0)

    def test_five_language_values_names_comments_and_priming(self):
        names = {MASTER._expected_name(case, field) for case in MASTER.REFERENCE_CASES for field in MASTER.OUTPUT_FIELDS}
        self.assertEqual({n for n in ARRAYS if n.startswith('EXPECTED_')}, names)
        patterns = {
            'testdata_test.go': r'var (expected\w+) = \[\]float64\{(.*?)\n\}',
            'testdata.ts': r'export const (expected\w+): number\[\] = \[(.*?)\n\];',
            'testdata.rs': r'pub fn (expected_\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\n    \]',
            'testdata.zig': r'pub fn (expected\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\n    \};',
        }
        for case in MASTER.REFERENCE_CASES:
            source = source_indicator(CLOSE, case.length, case.gamma)
            for field in MASTER.OUTPUT_FIELDS:
                name = MASTER._expected_name(case, field)
                values = ARRAYS[name]
                assert_values(self, values, source[field])
                warmup = MASTER.WARMUP_BARS[field]
                self.assertEqual(len(values), 252)
                self.assertTrue(all(math.isnan(v) for v in values[:warmup]))
                self.assertTrue(all(math.isfinite(v) for v in values[warmup:]))
                suffix = name.removeprefix('EXPECTED_')
                comments = f'# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\n{name}'
                self.assertIn(comments, (DIRECTORY / 'test_testdata.py').read_text())
                for filename, pattern in patterns.items():
                    text = (DIRECTORY / filename).read_text()
                    translated = dict(re.findall(pattern, text, re.DOTALL))
                    target = 'expected_' + suffix.lower() if filename.endswith('.rs') else 'expected' + suffix
                    self.assertEqual(len(translated), len(names))
                    literals = [v.strip() for v in translated[target].split(',') if v.strip()]
                    floats = [math.nan if v in ('math.NaN()', 'NaN', 'f64::NAN', 'nan') else float(v) for v in literals]
                    assert_values(self, floats, values, 0.0)
                    self.assertIn(f'// {case.what_it_tests}\n// {MASTER._parameter_comment(case)}\n', text)

    def test_regeneration_identical_and_input_closes_preserved(self):
        filenames = ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            before = {n: (DIRECTORY / n).read_bytes() for n in filenames}
            for n, contents in before.items(): (target / n).write_bytes(contents)
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, target)
                MASTER.generate_reference_data(CLOSE, target)
            self.assertEqual(before, {n: (target / n).read_bytes() for n in filenames})
        original = MASTER._load_literal_arrays(DIRECTORY.parent / 'test_testdata.py')
        for name, values in original.items():
            if name.startswith('INPUT_'): self.assertEqual(values, ARRAYS[name])
        main = next(n for n in ast.parse((DIRECTORY / 'laguerre-filter.py').read_text()).body if isinstance(n, ast.If))
        embedded = next(n for n in main.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'INPUT_CLOSE' for t in n.targets))
        self.assertEqual(ast.literal_eval(embedded.value), CLOSE)


if __name__ == '__main__':
    unittest.main()
