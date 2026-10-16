"""Independent article-expression, analytic and five-language fixture checks.

Run with python3 -m unittest -v test_cybernetic_oscillator.py in this folder.
Expected-data checks require all 16 confirmed cases in all five languages.
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
ARTICLE = DIRECTORY.parent.parent / 'tasc/2025-06-making-a-better-oscillator/content.md'
SPEC = importlib.util.spec_from_file_location('cybernetic_master', DIRECTORY / 'cybernetic-oscillator.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
ARRAYS = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
CLOSE = ARRAYS['INPUT_CLOSE']
BLOCKS = re.findall(r'```easylanguage\n(.*?)```', ARTICLE.read_text(), re.DOTALL)


def article_filter(prices, period, highpass, full_precision=True):
    """Batch oracle evaluates formulas extracted from the supplied article.

    It uses full lists and source expressions, independent of master helpers,
    ring storage and streaming-state logic. Only the documented constants are
    substituted for full-precision comparisons; article mode is literal.
    """
    label = 'Highpass Function' if highpass else 'SuperSmoother Function'
    function = '$HighPass' if highpass else '$SuperSmoother'
    block = next(block for block in BLOCKS if label in block)
    functions = {
        'expvalue': math.exp,
        'Cosine': math.cos if full_precision else lambda v: math.cos(math.radians(v)),
    }
    coefficients = {'Period': period, 'PI': math.pi, 'SQRT_TWO': math.sqrt(2.0)}
    for name in ('a1', 'b1', 'c2', 'c3', 'c1'):
        expression = re.search(r'\b' + name + r'\s*=\s*(.*?);', block).group(1)
        if full_precision:
            expression = expression.replace('1.414', 'SQRT_TWO').replace('3.14159', 'PI').replace('180', 'PI')
        coefficients[name] = eval(expression, {'__builtins__': {}}, functions | coefficients)
    recurrence = re.search(r'If CurrentBar >= 4 Then\s+' + re.escape(function) + r'\s*=\s*(.*?);', block, re.DOTALL).group(1)
    recurrence = recurrence.replace(function + '[1]', 'output1').replace(function + '[2]', 'output2')
    recurrence = recurrence.replace('Price[1]', 'price1').replace('Price[2]', 'price2')
    recurrence = ' '.join(recurrence.split())
    outputs = []
    for t, price in enumerate(prices):
        if t < 3:
            outputs.append(0.0 if highpass else price)
        else:
            values = coefficients | {
                'Price': price, 'price1': prices[t - 1], 'price2': prices[t - 2],
                'output1': outputs[t - 1], 'output2': outputs[t - 2],
            }
            outputs.append(eval(recurrence, {'__builtins__': {}}, values))
    return outputs


def article_oscillator(prices, hp_length, lp_length, full_precision=True):
    hp = article_filter(prices, hp_length, True, full_precision)
    lp = article_filter(hp, lp_length, False, full_precision)
    rms_block = next(block for block in BLOCKS if 'RMS Function' in block)
    term = re.search(r'SumSq = SumSq \+ (.*?);', rms_block).group(1).replace('Price[count]', 'value')
    rms_expression = re.search(r'If SumSq <> 0 Then \$RMS = (.*?);', rms_block).group(1)
    oscillator_block = next(block for block in BLOCKS if 'Cybernetic Oscillator\n' in block)
    ratio = re.search(r'If RMS <> 0 Then CyberneticOsc = (.*?);', oscillator_block).group(1)
    squares = [eval(term, {'__builtins__': {}}, {'value': value}) for value in lp]
    output, rms_values = [], []
    rms, previous = 0.0, 0.0
    for t, value in enumerate(lp):
        if t < 99:
            output.append(math.nan)
            rms_values.append(math.nan)
            continue
        total = 0.0
        for lag in range(100):
            total = total + squares[t - lag]
        if total != 0.0:
            rms = eval(rms_expression, {'__builtins__': {}},
                       {'SumSq': total, 'Length': 100, 'SquareRoot': math.sqrt})
        if rms != 0.0:
            previous = eval(ratio, {'__builtins__': {}}, {'LP': value, 'RMS': rms})
        rms_values.append(rms)
        output.append(previous)
    return output, hp, lp, rms_values


def assert_values(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for index, (a, e) in enumerate(zip(actual, expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a), (index, a, e))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a, e, rel_tol=tolerance, abs_tol=tolerance),
                            (index, a, e))


class CyberneticOscillatorTests(unittest.TestCase):
    def test_all_cases_match_extracted_source_in_both_precision_modes(self):
        for case in MASTER.REFERENCE_CASES:
            for mode in ('full_precision', 'article'):
                expected, hp, lp, rms = article_oscillator(CLOSE, case.hp_length, case.lp_length,
                                                         mode == 'full_precision')
                indicator = MASTER.CyberneticOscillator(case.hp_length, case.lp_length, coefficient_mode=mode)
                outputs, hp_outputs, lp_outputs, rms_outputs = [], [], [], []
                for price in CLOSE:
                    outputs.append(indicator.update(price))
                    hp_outputs.append(indicator.highpass)
                    lp_outputs.append(indicator.smoothed)
                    rms_outputs.append(indicator.rms)
                for actual, reference in ((outputs, expected), (hp_outputs, hp),
                                          (lp_outputs, lp), (rms_outputs, rms)):
                    assert_values(self, actual, reference, 0.0)

    def test_helper_startup_and_cascade_input(self):
        hp, lp = MASTER.HighPass(), MASTER.SuperSmoother()
        raw_hp = [hp.update(c) for c in CLOSE[:4]]
        self.assertEqual(raw_hp[:3], [0.0] * 3)
        self.assertNotEqual(raw_hp[3], 0.0)
        # Standalone SuperSmoother passes through its actual input initially.
        self.assertEqual([lp.update(c) for c in CLOSE[:3]], CLOSE[:3])
        indicator = MASTER.CyberneticOscillator()
        for t, price in enumerate(CLOSE[:4]):
            indicator.update(price)
            self.assertEqual(indicator._lowpass._price1, raw_hp[t])
        self.assertEqual(indicator.smoothed, indicator._lowpass._c1 * raw_hp[3] / 2)
        self.assertEqual(indicator._highpass._price1, CLOSE[3])

    def test_99_nan_warmup_independent_of_period(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.CyberneticOscillator(case.hp_length, case.lp_length)
            self.assertFalse(indicator.is_primed)
            self.assertEqual(indicator.warmup_bars, 99)
            for t, price in enumerate(CLOSE):
                value = indicator.update(price)
                self.assertEqual(indicator.is_primed, t >= 99)
                self.assertEqual(math.isnan(value), t < 99)
                self.assertEqual(indicator._highpass._count, t + 1)
                self.assertEqual(indicator._lowpass._count, t + 1)
            self.assertEqual(len(indicator._rms_filter._squares), 100)

    def test_constant_and_affine_prices_annihilated(self):
        for prices in ([25.0] * 252, [10.0 + 0.5 * t for t in range(252)]):
            indicator = MASTER.CyberneticOscillator()
            outputs = [indicator.update(price) for price in prices]
            self.assertTrue(all(math.isnan(value) for value in outputs[:99]))
            self.assertEqual(outputs[99:], [0.0] * 153)
            self.assertEqual(indicator.rms, 0.0)

    def test_both_persistent_zero_conditions(self):
        rms = MASTER.RootMeanSquare(2)
        self.assertTrue(math.isnan(rms.update(3)))
        self.assertEqual(rms.update(4), math.sqrt(25 / 2))
        self.assertEqual(rms.update(0), math.sqrt(16 / 2))
        self.assertEqual(rms.update(0), math.sqrt(16 / 2))
        rms.reset()
        self.assertTrue(math.isnan(rms.update(0)))
        self.assertEqual(rms.update(0), 0.0)

        class ConstantStage:
            def update(self, value):
                return 4.0

        class ControlledRMS:
            is_primed = True

            def __init__(self):
                self.values = iter((2.0, 0.0))

            def update(self, value):
                return next(self.values)

        indicator = MASTER.CyberneticOscillator()
        indicator._highpass = indicator._lowpass = ConstantStage()
        indicator._rms_filter = ControlledRMS()
        self.assertEqual(indicator.update(10), 2.0)
        self.assertEqual(indicator.update(11), 2.0)

    def test_rms_energy_and_newest_first_ring_wrap(self):
        # Independent list windows also exercise many ring wraps and dynamic range.
        prices = [1e7 if t % 7 == 0 else (0.125 * (t % 3)) for t in range(30)]
        rms = MASTER.RootMeanSquare(5)
        previous = 0.0
        for t, value in enumerate(prices):
            actual = rms.update(value)
            if t < 4:
                self.assertTrue(math.isnan(actual))
            else:
                total = 0.0
                for lag in range(5):
                    total = total + prices[t - lag] * prices[t - lag]
                if total != 0:
                    previous = math.sqrt(total / 5)
                self.assertEqual(actual, previous)
        rms = MASTER.RootMeanSquare(3)
        for value in (1, 2, 3):
            result = rms.update(value)
        self.assertEqual(result, math.sqrt(14 / 3))
        self.assertNotEqual(result, math.sqrt(2 / 3))  # Centered population stddev.

    def test_cascade_matches_analytic_sinusoid_transfer(self):
        omega = 2 * math.pi / 25
        q = cmath.exp(-1j * omega)

        def transfer(period, highpass):
            angle = math.sqrt(2) * math.pi / period
            radius = math.exp(-angle)
            c2, c3 = 2 * radius * math.cos(angle), -radius * radius
            numerator = ((1 + c2 - c3) / 4 * (1 - q) ** 2 if highpass
                         else (1 - c2 - c3) / 2 * (1 + q))
            return numerator / (1 - c2 * q - c3 * q * q)

        response = transfer(30, True) * transfer(20, False)
        indicator = MASTER.CyberneticOscillator()
        for t in range(1200):
            indicator.update(math.sin(omega * t))
            if t > 1000:
                expected = (response * cmath.exp(1j * omega * t)).imag
                self.assertAlmostEqual(indicator.smoothed, expected, places=11)

    def test_lowpass_transmission_zero_at_nyquist(self):
        indicator = MASTER.CyberneticOscillator()
        values = []
        for t in range(800):
            indicator.update(1.0 if t % 2 == 0 else -1.0)
            values.append(indicator.smoothed)
        self.assertLess(max(abs(v) for v in values[-100:]), 1e-12)
        # The raw bandpass tends to zero. Division by its vanishing RMS need
        # not produce a normalized oscillator tending to zero, so test LP.

    def test_scale_translation_polarity_and_normalization_bound(self):
        prices = [100 + (t % 11) - (t % 7) for t in range(252)]
        outputs = []
        for transform in (lambda p: p, lambda p: p + 1000, lambda p: 8 * p, lambda p: -p):
            indicator = MASTER.CyberneticOscillator()
            outputs.append([indicator.update(transform(price)) for price in prices])
        assert_values(self, outputs[0], outputs[1], 1e-11)
        assert_values(self, outputs[0], outputs[2], 1e-11)
        assert_values(self, [-v for v in outputs[0]], outputs[3], 1e-11)
        self.assertTrue(all(abs(v) <= 10 + 1e-12 for v in outputs[0][99:]))
        self.assertTrue(any(abs(v) > 1 for v in outputs[0][99:]))

    def test_causality_and_complete_reset(self):
        indicator = MASTER.CyberneticOscillator()
        full = [indicator.update(price) for price in CLOSE]
        prefix = MASTER.CyberneticOscillator()
        assert_values(self, [prefix.update(price) for price in CLOSE[:170]], full[:170], 0.0)
        changed = MASTER.CyberneticOscillator()
        changed_outputs = [changed.update(price) for price in CLOSE[:170] + [1000.0] * 82]
        assert_values(self, changed_outputs[:170], full[:170], 0.0)
        indicator.reset()
        self.assertFalse(indicator.is_primed)
        self.assertTrue(math.isnan(indicator.rms))
        assert_values(self, [indicator.update(price) for price in CLOSE], full, 0.0)

    def test_invalid_input_precision_and_fractional_parameters(self):
        for period in (True, False, 0, 0.5, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                MASTER.CyberneticOscillator(period, 20)
            with self.assertRaises(ValueError):
                MASTER.CyberneticOscillator(30, period)
        for length in (0, 1.5, True):
            with self.assertRaises(ValueError):
                MASTER.RootMeanSquare(length)
        with self.assertRaises(ValueError):
            MASTER.CyberneticOscillator(coefficient_mode='rounded')
        a, b = MASTER.CyberneticOscillator(30.5, 20.5), MASTER.CyberneticOscillator(30.5, 20.5)
        self.assertEqual((a.hp_length, a.lp_length), (30.5, 20.5))
        for price in CLOSE[:120]:
            a.update(price)
            b.update(price)
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                a.update(value)
        assert_values(self, [a.update(p) for p in CLOSE[120:]], [b.update(p) for p in CLOSE[120:]], 0.0)
        full = article_oscillator(CLOSE, 30, 20, True)[0]
        printed = article_oscillator(CLOSE, 30, 20, False)[0]
        self.assertGreater(max(abs(a - b) for a, b in zip(full[99:], printed[99:])), 1e-7)

    def test_all_five_expected_files_and_comments(self):
        expected_names = {'EXPECTED_' + MASTER._case_suffix(case) for case in MASTER.REFERENCE_CASES}
        self.assertEqual({n for n in ARRAYS if n.startswith('EXPECTED_')}, expected_names)
        patterns = {
            'testdata_test.go': r'var (expected\w+) = \[\]float64\{(.*?)\n\}',
            'testdata.ts': r'export const (expected\w+): number\[\] = \[(.*?)\n\];',
            'testdata.rs': r'pub fn (expected_\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\n    \]',
            'testdata.zig': r'pub fn (expected\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\n    \};',
        }
        for case in MASTER.REFERENCE_CASES:
            suffix = MASTER._case_suffix(case)
            reference = ARRAYS['EXPECTED_' + suffix]
            indicator = MASTER.CyberneticOscillator(case.hp_length, case.lp_length)
            assert_values(self, reference, [indicator.update(p) for p in CLOSE])
            self.assertEqual(len(reference), 252)
            self.assertTrue(all(math.isnan(v) for v in reference[:99]))
            self.assertTrue(all(math.isfinite(v) for v in reference[99:]))
            python_comments = f'# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\nEXPECTED_{suffix}'
            self.assertIn(python_comments, (DIRECTORY / 'test_testdata.py').read_text())
            for filename, pattern in patterns.items():
                text = (DIRECTORY / filename).read_text()
                arrays = dict(re.findall(pattern, text, re.DOTALL))
                name = 'expected_' + suffix.lower() if filename.endswith('.rs') else 'expected' + suffix
                self.assertEqual(len(arrays), len(MASTER.REFERENCE_CASES))
                literals = [v.strip() for v in arrays[name].split(',') if v.strip()]
                values = [math.nan if v in ('math.NaN()', 'NaN', 'f64::NAN', 'nan') else float(v)
                          for v in literals]
                assert_values(self, values, reference, 0.0)
                comments = f'// {case.what_it_tests}\n// {MASTER._parameter_comment(case)}\n'
                self.assertIn(comments, text)
        self.assertIn('package cyberneticoscillator', (DIRECTORY / 'testdata_test.go').read_text())
        self.assertIn('import "math"', (DIRECTORY / 'testdata_test.go').read_text())

    def test_generator_is_repeatable_and_preserves_all_input_data(self):
        filenames = ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for filename in filenames:
                (target / filename).write_bytes((DIRECTORY / filename).read_bytes())
            before = {filename: (target / filename).read_bytes() for filename in filenames}
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, target)
                MASTER.generate_reference_data(CLOSE, target)
            self.assertEqual(before, {filename: (target / filename).read_bytes() for filename in filenames})
            # All copied inputs remain exact, not just the closes used here.
            for name, values in ARRAYS.items():
                if name.startswith('INPUT_'):
                    self.assertEqual(values, MASTER._load_literal_arrays(target / 'test_testdata.py')[name])
        # The embedded __main__ sample must also be exactly the input fixture.
        tree = ast.parse((DIRECTORY / 'cybernetic-oscillator.py').read_text())
        main = next(node for node in tree.body if isinstance(node, ast.If))
        assignment = next(node for node in main.body if isinstance(node, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == 'INPUT_CLOSE' for t in node.targets))
        self.assertEqual(ast.literal_eval(assignment.value), CLOSE)


if __name__ == '__main__':
    unittest.main()
