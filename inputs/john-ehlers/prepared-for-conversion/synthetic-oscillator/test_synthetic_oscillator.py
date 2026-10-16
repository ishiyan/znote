"""Independent source-expression, analytical and five-language data checks."""

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
SOURCE = (DIRECTORY.parent.parent / 'tasc/2026-04-a-synthetic-oscillator/tips/SyntheticOscillator.els').read_text()
SPEC = importlib.util.spec_from_file_location('synthetic_master', DIRECTORY / 'synthetic-oscillator.py')
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)
ARRAYS = MASTER._load_literal_arrays(DIRECTORY / 'test_testdata.py')
CLOSE = ARRAYS['INPUT_CLOSE']


def assert_values(test, actual, expected, tolerance=5e-13):
    test.assertEqual(len(actual), len(expected))
    for t, (a, e) in enumerate(zip(actual, expected)):
        if math.isnan(e):
            test.assertTrue(math.isnan(a), (t, a, e))
        else:
            test.assertTrue(math.isfinite(a) and math.isclose(a, e, rel_tol=tolerance, abs_tol=tolerance),
                            (t, a, e))


def _expression(block, name):
    """Extract an assignment from the actual supplied EasyLanguage source."""
    return ' '.join(re.search(re.escape(name) + r'\s*=\s*(.*?);', block, re.DOTALL | re.IGNORECASE).group(1).split())


def source_biquad(prices, period, kind, full_precision=True):
    marker = {'highpass': 'Function: $HighPass', 'supersmoother': 'Function: $SuperSmoother',
              'ultimatesmoother': 'Function $UltimateSmoother'}[kind]
    block = SOURCE.split(marker, 1)[1].split('Function:', 1)[0].split('Indicator:', 1)[0]
    namespace = {'Period': period, 'PI': math.pi, 'SQRT_TWO': math.sqrt(2.0)}
    functions = {'expvalue': math.exp, 'cosine': math.cos if full_precision else lambda a: math.cos(math.radians(a))}
    names = ('Q', 'C1', 'C2', 'A0') if kind == 'supersmoother' else ('a1', 'b1', 'c2', 'c3', 'c1')
    # EasyLanguage identifiers are case-insensitive; normalize extracted code.
    for name in names:
        expression = _expression(block, name).lower()
        if full_precision:
            expression = expression.replace('1.414', 'sqrt_two').replace('3.14159', 'pi').replace('180', 'pi')
        values = {k.lower(): v for k, v in namespace.items()}
        namespace[name] = eval(expression, {'__builtins__': {}}, functions | values)
    result_name = {'highpass': '$HighPass', 'supersmoother': '$SuperSmoother', 'ultimatesmoother': 'US'}[kind]
    expression = re.search(r'if CurrentBar >= 4\s+then\s+' + re.escape(result_name) + r'\s*=\s*(.*?);',
                           block, re.DOTALL | re.IGNORECASE).group(1)
    expression = ' '.join(expression.split()).lower()
    expression = expression.replace(result_name.lower() + '[1]', 'old1').replace(result_name.lower() + '[2]', 'old2')
    expression = expression.replace('price[1]', 'price1').replace('price[2]', 'price2')
    outputs = []
    for t, value in enumerate(prices):
        if t < 3:
            outputs.append(0.0 if kind == 'highpass' else value)
        else:
            namespace.update(Price=value, price1=prices[t-1], price2=prices[t-2], old1=outputs[t-1], old2=outputs[t-2])
            outputs.append(eval(expression, {'__builtins__': {}}, {k.lower(): v for k, v in namespace.items()}))
    return outputs


def source_synthetic(prices, lower, upper, full_precision=True):
    """Batch oracle with source expressions and the documented startup contract.

    Full Hann observations start the measurement helper clock. Real's zero
    state is held until its full RMS exists, but ROC, QRMS and phase run on every
    raw bar. No master helper, ring buffer or streaming method is used here.
    """
    functions = {'Cosine': lambda a: math.cos(math.radians(a)), 'SquareRoot': math.sqrt,
                 'Sine': lambda a: math.sin(math.radians(a))}
    hann_block = SOURCE.split('Function: $Hann', 1)[1].split('Function $UltimateSmoother', 1)[0]
    weight = re.search(r'coef = coef \+ (.*?);', hann_block, re.DOTALL).group(1)
    weight = ' '.join(weight.split())
    weights = [eval(weight, {'__builtins__': {}}, functions | {'count': c, 'Length': 12}) for c in range(1, 13)]
    denominator = 0.0
    for w in weights: denominator = denominator + w
    hann = [math.nan] * min(11, len(prices))
    for t in range(11, len(prices)):
        total = 0.0
        for lag, w in enumerate(weights): total = total + w * prices[t-lag]
        hann.append(total / denominator)
    hp = source_biquad(hann[11:], upper, 'highpass', full_precision)
    lp = source_biquad(hp, lower, 'supersmoother', full_precision)
    mid = math.sqrt(lower * upper)
    timing_hp = source_biquad(prices, mid, 'highpass', full_precision)
    bp = source_biquad(timing_hp, mid, 'ultimatesmoother', full_precision)
    main = SOURCE.split('Indicator: Synthetic Oscillator', 1)[1]
    expressions = {n: _expression(main, n) for n in ('Real', 'ROC', 'Imag', 'Denom', 'DC', 'Phase', 'Synth')}
    if full_precision: expressions['DC'] = expressions['DC'].replace('6.28', 'TAU')
    rms_block = SOURCE.split('Function: $RMS', 1)[1].split('Function: $SuperSmoother', 1)[0]
    root = _expression(rms_block, '$RMS')
    real = imag = phase = synth = dc = previous_bp = 0.0
    r = qr = 0.0
    rocs = []
    output, states = [], []
    for t in range(len(prices)):
        old_real, old_imag, old_synth = real, imag, synth
        namespace = functions | {'TAU': 2 * math.pi}
        if t >= 110:
            total = 0.0
            for lag in range(100): total = total + lp[t-11-lag] * lp[t-11-lag]
            if total != 0: r = eval(root, {'__builtins__': {}}, namespace | {'SumSq': total, 'Length': 100})
            if r != 0: real = eval(expressions['Real'], {'__builtins__': {}}, {'LP': lp[t-11], 'RMS': r})
        roc = eval(expressions['ROC'].replace('Real[ 1 ]', 'old_real'), {'__builtins__': {}}, {'Real': real, 'old_real': old_real})
        rocs.append(roc)
        if t >= 99:
            total = 0.0
            for lag in range(100): total = total + rocs[t-lag] * rocs[t-lag]
            if total != 0: qr = eval(root, {'__builtins__': {}}, namespace | {'SumSq': total, 'Length': 100})
            if qr != 0: imag = eval(expressions['Imag'], {'__builtins__': {}}, {'ROC': roc, 'QRMS': qr})
        values = namespace | {'Real': real, 'Imag': imag, 'old_real': old_real, 'old_imag': old_imag}
        expression = expressions['Denom'].replace('Real[ 1 ]', 'old_real').replace('Imag[ 1 ]', 'old_imag')
        denom = eval(expression, {'__builtins__': {}}, values)
        if denom != 0: dc = eval(expressions['DC'], {'__builtins__': {}}, values | {'Denom': denom})
        if dc < lower: dc = lower
        if dc > upper: dc = upper
        phase = eval(expressions['Phase'], {'__builtins__': {}}, {'Phase': phase, 'DC': dc})
        if bp[t] > 0 and previous_bp <= 0: phase = 180.0 / dc
        if bp[t] < 0 and previous_bp >= 0: phase = 180.0 + 180.0 / dc
        previous_bp = bp[t]
        synth = eval(expressions['Synth'], {'__builtins__': {}}, namespace | {'Phase': phase})
        if 0 < phase < 90 and synth < old_synth: synth = old_synth
        if 180 < phase < 270 and synth > old_synth: synth = old_synth
        states.append((hann[t], hp[t-11] if t >= 11 else math.nan, lp[t-11] if t >= 11 else math.nan,
                       real, roc, imag, denom, dc, bp[t], phase, synth))
        output.append(synth if t >= 110 else math.nan)
    return output, states


class SyntheticOscillatorTests(unittest.TestCase):
    def test_all_cases_match_source_expressions_in_both_precision_modes(self):
        for case in MASTER.REFERENCE_CASES:
            for mode in ('full_precision', 'article'):
                indicator = MASTER.SyntheticOscillator(case.lower_bound, case.upper_bound, case.length, coefficient_mode=mode)
                expected, states = source_synthetic(CLOSE, case.lower_bound, case.upper_bound, mode == 'full_precision')
                actual = []
                for t, price in enumerate(CLOSE):
                    actual.append(indicator.update(price))
                    assert_values(self, indicator.state, states[t], 0.0)
                assert_values(self, actual, expected, 0.0)

    def test_hann_complete_window_weights_and_ring_wrap(self):
        hann = MASTER.HannFilter(12)
        self.assertAlmostEqual(hann._coefficient, 13.0, places=13)
        for a, b in zip(hann._weights, reversed(hann._weights)): self.assertAlmostEqual(a, b, places=14)
        outputs = [hann.update(p) for p in CLOSE]
        self.assertTrue(all(math.isnan(v) for v in outputs[:11]))
        for t in range(11, 252):
            total = 0.0
            for c in range(1, 13):
                total += (1 - math.cos(math.radians(360 * c / 13))) * CLOSE[t-c+1]
            self.assertEqual(outputs[t], total / hann._coefficient)
        hann.reset()
        self.assertFalse(hann.is_primed)

    def test_all_three_biquad_responses_against_transfer_functions(self):
        period = 20
        omega = 2 * math.pi / 30
        q = cmath.exp(-1j * omega)
        radius = math.exp(-math.sqrt(2) * math.pi / period)
        b, square = 2 * radius * math.cos(math.sqrt(2) * math.pi / period), radius * radius
        den = 1 - b * q + square * q * q
        gain = (1 + b + square) / 4
        responses = {'highpass': gain * (1-q)**2 / den,
                     'supersmoother': (1-b+square)/2 * (1+q) / den,
                     'ultimatesmoother': 1 - gain * (1-q)**2 / den}
        for kind, response in responses.items():
            stage = MASTER.Biquad(period, kind)
            for t in range(1000):
                actual = stage.update(math.sin(omega*t))
                if t > 900: self.assertAlmostEqual(actual, (response * cmath.exp(1j*omega*t)).imag, places=11)

    def test_110_nan_warmup_and_continuous_phase_state(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.SyntheticOscillator(case.lower_bound, case.upper_bound, case.length)
            self.assertEqual(indicator.warmup_bars, 110)
            for t, close in enumerate(CLOSE):
                value = indicator.update(close)
                self.assertEqual(indicator.is_primed, t >= 110)
                self.assertEqual(math.isnan(value), t < 110)
                self.assertEqual(indicator._timing_hp._count, t + 1)
                self.assertEqual(indicator._measurement_hp._count, max(0, t - 10))
                self.assertEqual(len(indicator._rms_imag._squares), min(100, t+1))
                self.assertTrue(math.isfinite(indicator.state.synth))
                if t < 110: self.assertEqual(indicator.state.real, 0)

    def test_phase_resets_glitch_holds_and_unwrapped_comparisons(self):
        class PassThrough:
            def update(self, value): return value
        class Sequence:
            def __init__(self, values): self.values = iter(values)
            def update(self, value): return next(self.values)
        indicator = MASTER.SyntheticOscillator(20, 20)
        indicator._timing_hp = Sequence((0, 1, 2, 0, -1, -2, 0, 1))
        indicator._timing_lp = PassThrough()
        phases, synths = [], []
        for _ in range(8):
            indicator.update(0)
            phases.append(indicator.state.phase_degrees)
            synths.append(indicator.state.synth)
        self.assertEqual(phases, [18, 9, 27, 45, 189, 207, 225, 9])
        self.assertEqual(synths[1], synths[0])  # Positive-quadrant reset glitch.
        indicator = MASTER.SyntheticOscillator(20, 20)
        indicator._timing_hp, indicator._timing_lp = Sequence((-1,)), PassThrough()
        indicator._bp, indicator._synth = 1, -0.9
        indicator.update(0)
        self.assertEqual(indicator.state.phase_degrees, 189)
        self.assertEqual(indicator.state.synth, -0.9)  # Negative-quadrant hold.
        indicator = MASTER.SyntheticOscillator(20, 20)
        indicator._phase, indicator._synth = 400, 0.99
        indicator.update(0)
        self.assertEqual(indicator.state.phase_degrees, 418)
        self.assertAlmostEqual(indicator.state.synth, math.sin(math.radians(418)), places=14)

    def test_cycle_derivative_orientation_and_zero_denominator_persistence(self):
        # Ideal real=cos(wt), imag=-sin(wt) gives a positive signed determinant.
        omega = 2 * math.pi / 20
        real, imag = math.cos(omega), -math.sin(omega)
        denom = (real - 1) * imag - imag * real
        self.assertAlmostEqual(denom, math.sin(omega), places=14)
        self.assertAlmostEqual(2 * math.pi * (real*real + imag*imag) / denom,
                               2 * math.pi / math.sin(omega), places=12)
        indicator = MASTER.SyntheticOscillator(15, 25)
        indicator._dc = 22
        indicator.update(0)
        self.assertEqual(indicator.state.denominator, 0)
        self.assertEqual(indicator.state.dominant_cycle, 22)

    def test_bounds_midpoint_and_scalar_range(self):
        for case in MASTER.REFERENCE_CASES:
            indicator = MASTER.SyntheticOscillator(case.lower_bound, case.upper_bound, case.length)
            self.assertEqual(indicator.midpoint, math.sqrt(case.lower_bound * case.upper_bound))
            for close in CLOSE:
                output = indicator.update(close)
                self.assertTrue(case.lower_bound <= indicator.state.dominant_cycle <= case.upper_bound)
                self.assertTrue(-1 <= indicator.state.synth <= 1)
                if indicator.is_primed: self.assertTrue(-1 <= output <= 1)
                if case.lower_bound == case.upper_bound:
                    self.assertEqual(indicator.state.dominant_cycle, case.lower_bound)

    def test_unused_length_is_exactly_inert(self):
        reference = None
        for length in (1, 4, 8, 12, 252):
            indicator = MASTER.SyntheticOscillator(15, 25, length)
            outputs = [indicator.update(p) for p in CLOSE]
            if reference is None: reference = outputs
            else: assert_values(self, outputs, reference, 0.0)

    def test_zero_input_uses_bounded_clock_without_cycle_measurement(self):
        indicator = MASTER.SyntheticOscillator(15, 25)
        phase = 0.0
        for t in range(252):
            output = indicator.update(0)
            phase += 360 / 15
            self.assertEqual(indicator.state.dominant_cycle, 15)
            self.assertEqual(indicator.state.real, 0)
            self.assertEqual(indicator.state.imag, 0)
            self.assertAlmostEqual(indicator.state.synth, math.sin(math.radians(phase)), places=14)
            self.assertEqual(math.isnan(output), t < 110)

    def test_rms_sum_zero_retains_its_previous_value(self):
        rms = MASTER.RootMeanSquare(2)
        self.assertTrue(math.isnan(rms.update(3)))
        self.assertEqual(rms.update(4), math.sqrt(25/2))
        self.assertEqual(rms.update(0), math.sqrt(16/2))
        self.assertEqual(rms.update(0), math.sqrt(16/2))

    def test_causal_prefix_reset_scale_and_invalid_input(self):
        a, b = MASTER.SyntheticOscillator(), MASTER.SyntheticOscillator()
        full = [a.update(p) for p in CLOSE]
        assert_values(self, [b.update(p) for p in CLOSE[:170]], full[:170], 0.0)
        a.reset()
        self.assertFalse(a.is_primed)
        assert_values(self, [a.update(p) for p in CLOSE], full, 0.0)
        a, b = MASTER.SyntheticOscillator(), MASTER.SyntheticOscillator()
        for p in CLOSE[:120]: a.update(p); b.update(p)
        for p in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError): a.update(p)
        assert_values(self, [a.update(p) for p in CLOSE[120:]], [b.update(p) for p in CLOSE[120:]], 0.0)
        scaled = MASTER.SyntheticOscillator()
        assert_values(self, [scaled.update(8*p) for p in CLOSE], full, 1e-11)
        for bounds in ((0, 25), (15, 0), (25, 15), (True, 25), (math.nan, 25), (15, math.inf), (1e308, 1e308)):
            with self.assertRaises(ValueError): MASTER.SyntheticOscillator(*bounds)
        for length in (0, True, 4.0, 1.5):
            with self.assertRaises(ValueError): MASTER.SyntheticOscillator(length=length)
        with self.assertRaises(ValueError): MASTER.SyntheticOscillator(coefficient_mode='wrong')

    def test_five_expected_files_have_all_values_comments_and_exact_warmup(self):
        names = {MASTER._expected_name(c, 'synth') for c in MASTER.REFERENCE_CASES}
        self.assertEqual({n for n in ARRAYS if n.startswith('EXPECTED_')}, names)
        patterns = {'testdata_test.go': r'var (expected\w+) = \[\]float64\{(.*?)\n\}',
                    'testdata.ts': r'export const (expected\w+): number\[\] = \[(.*?)\n\];',
                    'testdata.rs': r'pub fn (expected_\w+)\(\) -> Vec<f64> \{\s*vec!\[(.*?)\n    \]',
                    'testdata.zig': r'pub fn (expected\w+)\(\) \[252\]f64 \{\s*return \.\{(.*?)\n    \};'}
        for case in MASTER.REFERENCE_CASES:
            name = MASTER._expected_name(case, 'synth')
            values = ARRAYS[name]
            expected, _ = source_synthetic(CLOSE, case.lower_bound, case.upper_bound)
            assert_values(self, values, expected)
            self.assertEqual(len(values), 252)
            self.assertTrue(all(math.isnan(v) for v in values[:110]))
            self.assertTrue(all(math.isfinite(v) for v in values[110:]))
            self.assertIn(f'# {case.what_it_tests}\n# {MASTER._parameter_comment(case)}\n{name}', (DIRECTORY/'test_testdata.py').read_text())
            suffix = name.removeprefix('EXPECTED_')
            for filename, pattern in patterns.items():
                text = (DIRECTORY / filename).read_text()
                arrays = dict(re.findall(pattern, text, re.DOTALL))
                target = 'expected_' + suffix.lower() if filename.endswith('.rs') else 'expected' + suffix
                self.assertEqual(len(arrays), 16)
                literals = [v.strip() for v in arrays[target].split(',') if v.strip()]
                floats = [math.nan if v in ('math.NaN()', 'NaN', 'f64::NAN', 'nan') else float(v) for v in literals]
                assert_values(self, floats, values, 0.0)
                self.assertIn(f'// {case.what_it_tests}\n// {MASTER._parameter_comment(case)}\n', text)

    def test_regeneration_identical_and_input_preserved(self):
        filenames = ('test_testdata.py', 'testdata_test.go', 'testdata.ts', 'testdata.rs', 'testdata.zig')
        before = {n: (DIRECTORY / n).read_bytes() for n in filenames}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for n, content in before.items(): (target / n).write_bytes(content)
            with contextlib.redirect_stdout(io.StringIO()):
                MASTER.generate_reference_data(CLOSE, target)
                MASTER.generate_reference_data(CLOSE, target)
            self.assertEqual(before, {n: (target / n).read_bytes() for n in filenames})
        original = MASTER._load_literal_arrays(DIRECTORY.parent / 'test_testdata.py')
        for name, values in original.items():
            if name.startswith('INPUT_'): self.assertEqual(values, ARRAYS[name])
        main = next(n for n in ast.parse((DIRECTORY/'synthetic-oscillator.py').read_text()).body if isinstance(n, ast.If))
        embedded = next(n for n in main.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'INPUT_CLOSE' for t in n.targets))
        self.assertEqual(ast.literal_eval(embedded.value), CLOSE)


if __name__ == '__main__':
    unittest.main()
