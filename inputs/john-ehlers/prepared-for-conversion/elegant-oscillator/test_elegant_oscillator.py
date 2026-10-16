"""Independent source-expression and analytical checks of the Python master."""

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
SPEC = importlib.util.spec_from_file_location('elegant_master', DIRECTORY / 'elegant-oscillator.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
SOURCE = (DIRECTORY.parent.parent / 'tasc/2022-02-inverse-fisher-transform-redux/tips/code/ElegantOscillator.els').read_text().split('Indicator:', 2)[1]
CLOSE = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')['INPUT_CLOSE']


def source_expression(name):
    """Read an actual assignment from the primary supplied EasyLanguage file."""
    return ' '.join(re.search(r'\b' + name + r'\s*=\s*(.*?);', SOURCE, re.I | re.S).group(1).split())


def source_batch(prices, period, mode):
    """Batch oracle independent of streaming histories and ring indexing.

    Missing normalization is neutral until its first full window, as specified
    for a fresh stream. Published assignments are evaluated directly; only
    coefficient constants are substituted in full-precision mode.
    """
    namespace = {'bandedge': period, 'pi': math.pi, 'sqrt_two': math.sqrt(2)}
    cosine = math.cos if mode == 'full_precision' else lambda angle: math.cos(math.radians(angle))
    functions = {'expvalue': math.exp, 'cosine': cosine}
    for name in ('a1', 'b1', 'c2', 'c3', 'c1'):
        expr = source_expression(name).lower()
        if mode == 'full_precision':
            expr = expr.replace('1.414', 'sqrt_two').replace('3.14159', 'pi').replace('180', 'pi')
        namespace[name] = eval(expr, {'__builtins__': {}}, functions | namespace)
    limiter = source_expression('IFish').lower()
    smoother = source_expression('SS').lower().replace('ifish[1]', 'ifish1').replace('ss[1]', 'ss1').replace('ss[2]', 'ss2')
    derivatives = [math.nan, math.nan] + [prices[t] - prices[t-2] for t in range(2, len(prices))]
    outputs, details = [], []
    previous_ifish = 0.0
    for t in range(len(prices)):
        rms, normalized, ifish = math.nan, 0.0, 0.0
        if t >= 51:
            total = 0.0
            for lag in range(50):
                total += derivatives[t-lag] * derivatives[t-lag]
            rms = math.sqrt(total / 50) if total != 0 else 0.0
            normalized = derivatives[t] / rms if rms != 0 else 0.0
            ifish = eval(limiter, {'__builtins__': {}}, functions | {'nderiv': normalized})
        namespace.update(ifish=ifish, ifish1=previous_ifish,
                         ss1=outputs[t-1] if t else 0.0,
                         ss2=outputs[t-2] if t >= 2 else 0.0)
        ss = 0.0 if t < 2 else eval(smoother, {'__builtins__': {}}, namespace)
        outputs.append(ss)
        previous_ifish = ifish
        details.append((rms, normalized, ifish))
    return [math.nan if t < 51 else v for t, v in enumerate(outputs)], details


def compare(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for t, (a, b) in enumerate(zip(actual, expected)):
        if math.isnan(b):
            test.assertTrue(math.isnan(a), (t, a, b))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance), (t, a, b))


class ElegantOscillatorTests(unittest.TestCase):
    def test_all_confirmed_cases_in_both_modes_match_source_expressions(self):
        for mode in ('full_precision', 'article'):
            for case in MASTER.REFERENCE_CASES:
                indicator = MASTER.ElegantOscillator(case.band_edge, coefficient_mode=mode)
                expected, details = source_batch(CLOSE, case.band_edge, mode)
                actual = []
                for t, price in enumerate(CLOSE):
                    actual.append(indicator.update(price))
                    if t >= 51:
                        self.assertEqual(indicator.state.rms, details[t][0])
                        self.assertEqual(indicator.state.normalized_derivative, details[t][1])
                        self.assertEqual(indicator.state.inverse_fisher, details[t][2])
                compare(self, actual, expected)

    def test_exact_warmup_and_first_smoother_assignment(self):
        indicator = MASTER.ElegantOscillator()
        for t, price in enumerate(CLOSE[:55]):
            output = indicator.update(price)
            self.assertEqual(indicator.is_primed, t >= 51)
            self.assertEqual(math.isnan(output), t < 51)
            self.assertEqual(len(indicator._squares), min(50, max(0, t-1)))
            if t < 51:
                self.assertEqual(indicator.state.inverse_fisher, 0)
                self.assertEqual(indicator.state.super_smoother, 0)
            if t == 51:
                self.assertEqual(output, indicator._c1 * indicator.state.inverse_fisher / 2)
        self.assertEqual(indicator.warmup_bars, 51)

    def test_rms_normalization_bound_and_inverse_fisher_identity(self):
        indicator = MASTER.ElegantOscillator()
        for price in CLOSE:
            indicator.update(price)
            if indicator.is_primed:
                z = indicator.state.normalized_derivative
                self.assertLessEqual(abs(z), math.sqrt(50) + 1e-14)
                self.assertAlmostEqual(indicator.state.inverse_fisher, math.tanh(z), places=14)
                self.assertLessEqual(abs(indicator.state.inverse_fisher), 1)

    def test_zero_rms_extension_and_decay_after_flat_window(self):
        indicator = MASTER.ElegantOscillator()
        values = [indicator.update(100) for _ in range(252)]
        self.assertTrue(all(math.isnan(v) for v in values[:51]))
        self.assertEqual(values[51:], [0.0] * 201)
        for price in CLOSE:
            indicator.update(price)
        for _ in range(52):
            indicator.update(CLOSE[-1])
        self.assertEqual(indicator.state.rms, 0)
        self.assertEqual(indicator.state.normalized_derivative, 0)
        self.assertEqual(indicator.state.inverse_fisher, 0)
        old1, old2 = indicator._ss1, indicator._ss2
        self.assertEqual(indicator.update(CLOSE[-1]), indicator._c2 * old1 + indicator._c3 * old2)

    def test_translation_scaling_sign_symmetry_and_causal_prefix(self):
        base = MASTER.ElegantOscillator()
        full = [base.update(p) for p in CLOSE]
        prefix = MASTER.ElegantOscillator()
        compare(self, [prefix.update(p) for p in CLOSE[:170]], full[:170], 0)
        # Eight is an exact power-of-two rescaling; adding a price offset must
        # vanish in the two-bar difference, within floating-point tolerance.
        for prices, sign in (([8*p for p in CLOSE], 1), ([p+128 for p in CLOSE], 1), ([-p for p in CLOSE], -1)):
            other = MASTER.ElegantOscillator()
            compare(self, [other.update(p) for p in prices], [sign*v for v in full], 1e-11)

    def test_reset_and_rejected_nonfinite_inputs_preserve_stream(self):
        indicator = MASTER.ElegantOscillator()
        full = [indicator.update(p) for p in CLOSE]
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        compare(self, [indicator.update(p) for p in CLOSE], full, 0)
        other = MASTER.ElegantOscillator()
        indicator.reset()
        for p in CLOSE[:100]:
            indicator.update(p)
            other.update(p)
        for value in (math.nan, math.inf, -math.inf):
            before = indicator.state
            with self.assertRaises(ValueError):
                indicator.update(value)
            self.assertEqual(indicator.state, before)
        compare(self, [indicator.update(p) for p in CLOSE[100:]], [other.update(p) for p in CLOSE[100:]], 0)

    def test_parameter_validation_and_fractional_coefficients(self):
        for value in (0, -1, True, math.nan, math.inf):
            with self.assertRaises(ValueError):
                MASTER.ElegantOscillator(value)
        with self.assertRaises(ValueError):
            MASTER.ElegantOscillator(coefficient_mode='wrong')
        indicator = MASTER.ElegantOscillator(20.5)
        self.assertEqual(indicator.band_edge, 20.5)
        self.assertEqual(indicator.coefficient_mode, 'full_precision')
        angle = math.sqrt(2) * math.pi / 20.5
        self.assertEqual(indicator._c2, 2 * math.exp(-angle) * math.cos(angle))

    def test_price_derivative_and_smoother_transfer_response(self):
        # Sinusoidal closes exercise the nonlinear normalization/limiter.
        # Verify the linear SS stage using its actual internal IFish inputs,
        # rather than assuming that the complete oscillator stays linear.
        indicator = MASTER.ElegantOscillator()
        omega = 2 * math.pi / 30
        signal = [math.sin(omega*t) for t in range(1200)]
        ifish = []
        output = []
        for t, p in enumerate(signal):
            output.append(indicator.update(p))
            ifish.append(indicator.state.inverse_fisher)
            if t >= 2:
                self.assertEqual(indicator.state.derivative, signal[t] - signal[t-2])
        # Independently reconstruct the IIR via its impulse response, then
        # convolve recent IFish. This checks signs and delay locations.
        impulse = []
        for t in range(300):
            h = indicator._c1 / 2 if t in (0, 1) else 0.0
            if t >= 1: h += indicator._c2 * impulse[t-1]
            if t >= 2: h += indicator._c3 * impulse[t-2]
            impulse.append(h)
        for t in range(1100, 1200):
            expected = sum(impulse[k] * ifish[t-k] for k in range(300))
            self.assertAlmostEqual(output[t], expected, places=12)
        q = cmath.exp(-1j*omega)
        response = (indicator._c1 * (1+q) / 2) / (1-indicator._c2*q-indicator._c3*q*q)
        empirical = sum(h * cmath.exp(-1j*omega*k) for k, h in enumerate(impulse))
        self.assertAlmostEqual(abs(response-empirical), 0, places=12)

    def test_all_copied_input_arrays_and_embedded_close_are_unchanged(self):
        before = MASTER._load_literal_arrays(DIRECTORY.parent / 'test_testdata.py')
        after = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
        for name, values in before.items():
            if name.startswith('INPUT_'):
                self.assertEqual(values, after[name])
                self.assertEqual(len(values), 252)
        module = ast.parse((DIRECTORY / 'elegant-oscillator.py').read_text())
        main = next(node for node in module.body if isinstance(node, ast.If))
        embedded = next(node for node in main.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'INPUT_CLOSE' for t in node.targets))
        self.assertEqual(ast.literal_eval(embedded.value), CLOSE)

    def test_every_expected_array_has_source_values_comments_and_exact_warmup(self):
        arrays = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
        names = {MASTER._expected_name(case, 'oscillator') for case in MASTER.REFERENCE_CASES}
        self.assertEqual({name for name in arrays if name.startswith('EXPECTED_')}, names)
        patterns = {
            'testdata_test.go': r'var (expected\w+) = \[\]float64\{(.*?)\n\}',
            'testdata.ts': r'export const (expected\w+): number\[\] = \[(.*?)\n\];',
            'testdata.rs': r'pub fn (expected_\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\n    \]',
            'testdata.zig': r'pub fn (expected\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\n    \};',
        }
        translated = {}
        texts = {filename: (DIRECTORY / filename).read_text() for filename in patterns}
        for filename, pattern in patterns.items():
            translated[filename] = dict(re.findall(pattern, texts[filename], re.DOTALL))
            self.assertEqual(len(translated[filename]), 12)
        python_text = (DIRECTORY / 'test_testdata.py').read_text()
        for case in MASTER.REFERENCE_CASES:
            name = MASTER._expected_name(case, 'oscillator')
            values = arrays[name]
            expected, _ = source_batch(CLOSE, case.band_edge, 'full_precision')
            compare(self, values, expected)
            self.assertEqual(len(values), 252)
            self.assertTrue(all(math.isnan(value) for value in values[:51]))
            self.assertTrue(all(math.isfinite(value) for value in values[51:]))
            self.assertIn(f'# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\n{name}', python_text)
            suffix = name.removeprefix('EXPECTED_')
            for filename in patterns:
                target = 'expected_' + suffix.lower() if filename.endswith('.rs') else 'expected' + suffix
                literals = [v.strip() for v in translated[filename][target].split(',') if v.strip()]
                floats = [math.nan if v in ('math.NaN()', 'NaN', 'f64::NAN', 'nan') else float(v) for v in literals]
                compare(self, floats, values, 0)
                self.assertIn(f'// {case.what_it_tests}\n// {MASTER._parameter_comment(case)}\n', texts[filename])

    def test_regeneration_is_identical_and_preserves_copied_inputs(self):
        filenames = ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')
        before = {name: (DIRECTORY / name).read_bytes() for name in filenames}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name, content in before.items():
                (target / name).write_bytes(content)
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, target)
                MASTER.generate_reference_data(CLOSE, target)
            self.assertEqual(before, {name: (target / name).read_bytes() for name in filenames})
        # Everything before the generated output marker retains the exact
        # copied input text. Only Go/Zig require additional language imports.
        for filename in ('test_testdata.py', 'testdata.ts', 'testdata.rs'):
            original = (DIRECTORY.parent / filename).read_text().rstrip()
            marker = '# BEGIN GENERATED' if filename.endswith('.py') else '// BEGIN GENERATED'
            prefix = (DIRECTORY / filename).read_text().split(marker, 1)[0].rstrip()
            self.assertEqual(prefix, original)


if __name__ == '__main__':
    unittest.main()
