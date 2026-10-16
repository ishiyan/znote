"""April 2026 Synthetic Oscillator: standard-library streaming master.

TradeStation's complete supplied Traders' Tips listing is the source. There is
no article content.md in the input folder. See description.md for every source
equation, nonlinear phase synthesis, initialization and platform differences.

Default precision uses full pi, sqrt(2), and 2*pi in place of printed 6.28.
coefficient_mode='article' reproduces the printed coefficient/DC constants.
The first 110 scalar results are NaN; all internal phase/reset state advances.
Length is an unused input in the source oscillator, retained for compatibility.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple

PI = math.pi
SQRT_TWO = math.sqrt(2.0)
HANN_LENGTH = 12
RMS_LENGTH = 100
OUTPUT_FIELDS = ('synth',)
WARMUP_BARS = {'synth': (HANN_LENGTH - 1) + (RMS_LENGTH - 1)}


def _period(value: float) -> float:
    """A filter period is finite and >=1; fractional values are not truncated."""
    if isinstance(value, bool):
        raise ValueError('period must be a finite real number >= 1')
    value = float(value)
    if not math.isfinite(value) or value < 1.0:
        raise ValueError('period must be finite and at least 1')
    return value


class HannFilter:
    """Source Hann-windowed FIR, with a complete observed window before output."""

    def __init__(self, length: int = HANN_LENGTH) -> None:
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError('Hann length must be a positive integer')
        self.length = length
        # Source count runs from 1 THROUGH Length. Price[count-1] is newest
        # first. The Length+1 denominator keeps BOTH endpoint weights nonzero.
        self._weights = [1.0 - math.cos(math.radians(360.0 * count / (length + 1)))
                         for count in range(1, length + 1)]
        self._coefficient = 0.0
        for weight in self._weights:
            self._coefficient = self._coefficient + weight
        self.reset()

    @property
    def is_primed(self) -> bool:
        return len(self._prices) == self.length

    def reset(self) -> None:
        self._prices = []
        self._next = 0

    def update(self, price: float) -> float:
        price = float(price)
        if not math.isfinite(price):
            raise ValueError('Hann input must be finite')
        if len(self._prices) < self.length:
            self._prices.append(price)
            self._next = len(self._prices) % self.length
        else:
            self._prices[self._next] = price
            self._next = (self._next + 1) % self.length
        if not self.is_primed:
            # Missing close history is not filled with zeros or a partial Hann.
            return math.nan
        total = 0.0
        for lag, weight in enumerate(self._weights):
            index = (self._next - 1 - lag) % self.length
            total = total + weight * self._prices[index]
        return total / self._coefficient


class Biquad:
    """One of the source's three second-order filters, with separate histories.

    kind is 'highpass', 'supersmoother' or 'ultimatesmoother'. The formulas below
    preserve source arithmetic and first-three-observation startup. Each helper
    advances when it receives an actual finite input; absent Hann values never
    enter its recurrence. Combining histories across instances is incorrect.
    """

    def __init__(self, period: float, kind: str, coefficient_mode: str = 'full_precision') -> None:
        self.period = _period(period)
        if kind not in ('highpass', 'supersmoother', 'ultimatesmoother'):
            raise ValueError('unknown second-order filter kind')
        self.kind = kind
        if coefficient_mode == 'full_precision':
            theta = SQRT_TWO * PI / self.period
            radius = math.exp(-theta)
            b = 2.0 * radius * math.cos(theta)
        elif coefficient_mode == 'article':
            # Printed exponential has rounded pi; degree cosine conversion
            # uses full pi. These angles must not be merged in article mode.
            radius = math.exp(-1.414 * 3.14159 / self.period)
            b = 2.0 * radius * math.cos(math.radians(1.414 * 180.0 / self.period))
        else:
            raise ValueError('coefficient_mode must be "full_precision" or "article"')
        self._b = b
        self._square = radius * radius
        # Positive radius squared is -c3 in source HighPass/UltimateSmoother,
        # and +C2 in source SuperSmoother. Keep the distinct normalizations.
        self._gain = ((1.0 - b + self._square) / 2.0 if kind == 'supersmoother'
                      else (1.0 + b + self._square) / 4.0)
        self.reset()

    def reset(self) -> None:
        self._count = 0
        self._price1 = self._price2 = 0.0
        self._output1 = self._output2 = 0.0

    def update(self, price: float) -> float:
        price = float(price)
        if not math.isfinite(price):
            raise ValueError('biquad input must be finite')
        if self._count < 3:
            output = 0.0 if self.kind == 'highpass' else price
        elif self.kind == 'highpass':
            output = (self._gain * (price - 2.0 * self._price1 + self._price2)
                      + self._b * self._output1 - self._square * self._output2)
        elif self.kind == 'supersmoother':
            # This listing folds the divide-by-two into A0. Do NOT replace it
            # by the earlier c1*(Price+Price[1])/2 form and reorder rounding.
            output = (self._gain * (price + self._price1)
                      + self._b * self._output1 - self._square * self._output2)
        else:
            output = ((1.0 - self._gain) * price
                      + (2.0 * self._gain - self._b) * self._price1
                      - (self._gain - self._square) * self._price2
                      + self._b * self._output1 - self._square * self._output2)
        if not math.isfinite(output):
            raise ValueError('biquad output must be finite')
        # Commit after evaluation; raw inputs and recursive outputs differ.
        self._price2, self._price1 = self._price1, price
        self._output2, self._output1 = self._output1, output
        self._count += 1
        return output


class SyntheticState(NamedTuple):
    """Unmasked current source variables, for inspection and port validation."""

    hann: float
    highpass: float
    lowpass: float
    real: float
    roc: float
    imag: float
    denominator: float
    dominant_cycle: float
    bandpass: float
    phase_degrees: float
    synth: float


class SyntheticOscillator:
    """Measured period and independently aligned phase synthesize a sine wave.

    lower_bound=15, upper_bound=25 are real periods >=1, lower<=upper.
    length=4 is a positive integer, UNUSED by the source oscillator.
    Hann length=12 and both RMS lengths=100 are fixed. Scalar update returns
    NaN for 110 closes, then this bar's Synth in [-1,1]. Phase is not modulo
    wrapped: source glitch tests compare the actual unwrapped degree angle.
    """

    def __init__(self, lower_bound: float = 15.0, upper_bound: float = 25.0,
                 length: int = 4, *, coefficient_mode: str = 'full_precision') -> None:
        self._lower_bound, self._upper_bound = _period(lower_bound), _period(upper_bound)
        if self._lower_bound > self._upper_bound:
            raise ValueError('lower_bound must not exceed upper_bound')
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError('length must be a positive integer')
        self._length = length  # Compatibility metadata, not a filter setting.
        product = self._lower_bound * self._upper_bound
        if not math.isfinite(product):
            raise ValueError('bound product must be finite')
        # Geometric midpoint is fixed by bounds, NOT the measured adaptive DC.
        # Retain its fraction; truncating this period changes reset timing.
        self._mid = math.sqrt(product)
        self._coefficient_mode = coefficient_mode
        self._cycle_constant = 2.0 * PI if coefficient_mode == 'full_precision' else 6.28
        self._hann = HannFilter(HANN_LENGTH)
        self._measurement_hp = Biquad(self._upper_bound, 'highpass', coefficient_mode)
        self._measurement_lp = Biquad(self._lower_bound, 'supersmoother', coefficient_mode)
        self._rms_real = RootMeanSquare(RMS_LENGTH)
        self._rms_imag = RootMeanSquare(RMS_LENGTH)
        self._timing_hp = Biquad(self._mid, 'highpass', coefficient_mode)
        self._timing_lp = Biquad(self._mid, 'ultimatesmoother', coefficient_mode)
        self.reset()

    @property
    def lower_bound(self) -> float:
        return self._lower_bound

    @property
    def upper_bound(self) -> float:
        return self._upper_bound

    @property
    def length(self) -> int:
        return self._length

    @property
    def coefficient_mode(self) -> str:
        return self._coefficient_mode

    @property
    def midpoint(self) -> float:
        return self._mid

    @property
    def warmup_bars(self) -> int:
        return WARMUP_BARS['synth']

    @property
    def is_primed(self) -> bool:
        return self._rms_real.is_primed and self._rms_imag.is_primed

    @property
    def state(self) -> SyntheticState:
        """Internal Synth is finite during the external NaN availability mask."""
        return self._state

    def reset(self) -> None:
        for stage in (self._hann, self._measurement_hp, self._measurement_lp,
                      self._rms_real, self._rms_imag, self._timing_hp, self._timing_lp):
            stage.reset()
        self._real = self._imag = self._phase = self._synth = self._bp = 0.0
        # Source DC starts at zero and is clamped to LowerBound on bar one.
        self._dc = 0.0
        self._count = 0
        self._state = SyntheticState(math.nan, math.nan, math.nan, 0, 0, 0, 0, 0, 0, 0, 0)

    def update(self, close: float) -> float:
        close = float(close)
        if not math.isfinite(close):
            raise ValueError('close must be finite')
        old_real, old_imag, old_bp, old_synth = self._real, self._imag, self._bp, self._synth

        # Measurement path starts as actual Hann observations become available.
        # During the 11 missing Hann outputs, do not inject NaN into an IIR.
        price = self._hann.update(close)
        hp = lp = math.nan
        if self._hann.is_primed:
            hp = self._measurement_hp.update(price)
            lp = self._measurement_lp.update(hp)
            rms = self._rms_real.update(lp)
            if self._rms_real.is_primed and rms != 0.0:
                self._real = lp / rms
        # Real's initialized zero/previous value is retained while its source
        # assignment cannot be made. Those are actual held state values, so ROC
        # and its RMS advance on EVERY raw bar, not only after Real is primed.
        roc = self._real - old_real
        qrms = self._rms_imag.update(roc)
        if self._rms_imag.is_primed and qrms != 0.0:
            self._imag = roc / qrms

        denom = (self._real - old_real) * self._imag - (self._imag - old_imag) * self._real
        if denom != 0.0:
            # Source signed denominator is retained: negative estimates clamp
            # to the lower bound; do not abs(), invert orientation, or add epsilon.
            self._dc = self._cycle_constant * (self._real * self._real + self._imag * self._imag) / denom
        # Preserve source persistence when denominator is zero, THEN clamp the
        # stored DC, including its first zero value, in the original order.
        if self._dc < self._lower_bound:
            self._dc = self._lower_bound
        if self._dc > self._upper_bound:
            self._dc = self._upper_bound

        # Timing path bypasses Hann and consumes the original close from bar 1.
        hp2 = self._timing_hp.update(close)
        bp = self._timing_lp.update(hp2)
        self._phase = self._phase + 360.0 / self._dc
        # Crossing means a strict sign on this bar after the other side or zero.
        # Landing exactly on zero alone causes no reset. Do not reset every bar
        # with positive/negative BP, and never use future prices to find crossings.
        if bp > 0.0 and old_bp <= 0.0:
            self._phase = 180.0 / self._dc
        if bp < 0.0 and old_bp >= 0.0:
            self._phase = 180.0 + 180.0 / self._dc
        synth = math.sin(math.radians(self._phase))
        # These are exact SOURCE ranges on the UNWRAPPED angle, not general
        # modulo quadrants. Held Synth is the previous internal output, even
        # if update() returned NaN for that bar during availability warmup.
        if 0.0 < self._phase < 90.0 and synth < old_synth:
            synth = old_synth
        if 180.0 < self._phase < 270.0 and synth > old_synth:
            synth = old_synth
        self._synth, self._bp = synth, bp
        self._count += 1
        self._state = SyntheticState(price, hp, lp, self._real, roc, self._imag,
                                     denom, self._dc, bp, self._phase, synth)
        return synth if self.is_primed else math.nan


class RootMeanSquare:
    """Finite-window RMS preserving the source's conditional zero-sum return.

    This helper accepts an integer length >= 1 for direct verification, but
    SyntheticOscillator always constructs it with the article's fixed 100.
    Missing window history is not padded: the first length-1 returns are NaN.
    When a full sum is zero, retain the previous RMS as the source does.
    """

    def __init__(self, length: int = RMS_LENGTH) -> None:
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError('RMS length must be an integer of at least 1')
        self.length = length
        self.reset()

    @property
    def is_primed(self) -> bool:
        return len(self._squares) == self.length

    def reset(self) -> None:
        """Clear squared-sample ring and initialize the persistent RMS to zero."""
        self._squares = []
        self._next = 0
        self._last_rms = 0.0

    def update(self, value: float) -> float:
        """Insert this sample and sum a full window from newest to oldest."""
        value = float(value)
        if not math.isfinite(value):
            raise ValueError('RMS input must be finite')
        square = value * value
        if not math.isfinite(square):
            raise ValueError('squared RMS input must be finite')

        # Store only squares, incrementally until the ring is full. Observed
        # signal samples count as observations; absent history does not.
        if len(self._squares) < self.length:
            self._squares.append(square)
            self._next = len(self._squares) % self.length
        else:
            self._squares[self._next] = square
            self._next = (self._next + 1) % self.length
        if not self.is_primed:
            # Do not assign this unavailable output to persistent _last_rms.
            return math.nan

        # Match for count=0 to Length-1 inclusively: exactly length terms,
        # newest first, plain sequential addition. A compensated or rolling
        # total can produce different last bits from the reference loop.
        total = 0.0
        for lag in range(self.length):
            index = (self._next - 1 - lag) % self.length
            total = total + self._squares[index]
        if not math.isfinite(total):
            raise ValueError('RMS sum must be finite')

        # The source assigns the function result ONLY if SumSq<>0. Hence
        # an all-zero full window retains a previous nonzero RMS if one exists.
        # Do not replace this conditional by an unconditional sqrt expression.
        if total != 0.0:
            self._last_rms = math.sqrt(total / self.length)
        return self._last_rms






class ReferenceCase(NamedTuple):
    """One confirmed source-input combination and its portable test comment."""

    lower_bound: float
    upper_bound: float
    length: int
    what_it_tests: str


# All 16 cases were confirmed by the user on 2026-10-16.
REFERENCE_CASES = (
    ReferenceCase(15.0, 25.0, 4, 'TradeStation default.'),
    ReferenceCase(15.0, 25.0, 8, 'Unused Length input leaves output unchanged.'),
    ReferenceCase(17.0, 23.0, 8, 'Python tip\'s example bounds.'),
    ReferenceCase(1.0, 2.0, 4, 'Minimum supported periods.'),
    ReferenceCase(8.0, 16.0, 4, 'Short-cycle response.'),
    ReferenceCase(10.0, 20.0, 4, 'One-octave range.'),
    ReferenceCase(12.0, 24.0, 4, 'Intermediate-cycle range.'),
    ReferenceCase(20.0, 20.0, 4, 'Equal bounds fix the measured period.'),
    ReferenceCase(20.0, 40.0, 4, 'Longer one-octave range.'),
    ReferenceCase(30.0, 60.0, 4, 'Slower cycle range.'),
    ReferenceCase(60.0, 120.0, 4, 'Long filter memory.'),
    ReferenceCase(100.0, 200.0, 4, 'Periods near the record length.'),
    ReferenceCase(126.0, 252.0, 4, 'Upper bound equals the record length.'),
    ReferenceCase(15.5, 25.5, 4, 'Fractional periods.'),
    ReferenceCase(15.0, 25.0, 1, 'Minimum unused Length value.'),
    ReferenceCase(15.0, 25.0, 12, 'Larger unused Length value.'),
)


def _parameter_token(value: float) -> str:
    """Use compact integer tokens and underscores for fractional values."""
    return format(value, 'g').replace('.', '_')


def _case_suffix(case: ReferenceCase) -> str:
    return f'LB{_parameter_token(case.lower_bound)}_UB{_parameter_token(case.upper_bound)}_L{case.length}'


def _parameter_comment(case: ReferenceCase) -> str:
    return f'lower_bound={case.lower_bound:g}, upper_bound={case.upper_bound:g}, length={case.length}'


def _expected_name(case: ReferenceCase, field: str) -> str:
    """Multi-output fields follow the parameter suffix; scalar outputs omit it."""
    suffix = _case_suffix(case)
    if len(OUTPUT_FIELDS) > 1:
        suffix += '_' + field.upper()
    return 'EXPECTED_' + suffix


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write Python reference arrays, verify them, then translate their values.

    All generation is binary64 with rounding only during text emission. Each
    rerun replaces its own marked section and preserves the copied input data.
    Rendering helpers and file I/O are tooling; only the indicator is ported.
    """
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError('expected 252 closes and between 1 and 64 parameter cases')
    python_path = directory / 'test_testdata.py'
    if _load_literal_arrays(python_path)['INPUT_CLOSE'] != input_close:
        raise ValueError('embedded INPUT_CLOSE differs from the copied fixture')
    raw_outputs = {}
    sections = []
    for case in REFERENCE_CASES:
        # Precision and any source-selection options deliberately use the
        # documented master defaults; only the three declared source inputs vary in fixtures.
        indicator = SyntheticOscillator(case.lower_bound, case.upper_bound, case.length)
        outputs = [indicator.update(price) for price in input_close]
        for field in OUTPUT_FIELDS:
            values = outputs if len(OUTPUT_FIELDS) == 1 else [getattr(v, field) for v in outputs]
            name = _expected_name(case, field)
            raw_outputs[name] = (values, WARMUP_BARS[field])
            sections.append(
                f'# {case.what_it_tests}\n# {_parameter_comment(case)}\n'
                f'{name} = [\n{_array_lines(values, "    ", "math.nan")}\n]'
            )
    _write_generated_section(python_path, '\n\n'.join(sections), '#')

    # Reopen the generated Python data before using it as the source for all
    # other languages. Counts, unavailable prefixes and rounding are checked.
    written = _load_literal_arrays(python_path)
    if {n for n in written if n.startswith('EXPECTED_')} != set(raw_outputs):
        raise ValueError('missing or unexpected Python expected arrays')
    for name, (raw, warmup) in raw_outputs.items():
        values = written[name]
        if len(values) != 252:
            raise ValueError(f'{name} must have 252 values')
        if not all(math.isnan(v) for v in values[:warmup]):
            raise ValueError(f'{name} has an incorrect NaN prefix')
        if not all(math.isfinite(v) for v in values[warmup:]):
            raise ValueError(f'{name} must be finite after priming')
        for before, after in zip(raw, values):
            if math.isnan(before) and math.isnan(after):
                continue
            if not math.isclose(before, after, rel_tol=5e-14, abs_tol=5e-14):
                raise ValueError(f'{name} did not retain 15-digit precision')

    go_path = directory / 'testdata_test.go'
    text = go_path.read_text().replace('package xxxx', 'package syntheticoscillator', 1)
    if 'import "math"' not in text:
        preamble = 'package syntheticoscillator\n\nimport "math"\n'
        if not any(math.isnan(v) for name in raw_outputs for v in written[name]):
            # Go rejects unused imports. Keep the requested NaN helper import
            # without inserting artificial NaNs into defined startup outputs.
            preamble += '\n// Keep the NaN helper available; startup outputs are defined.\nvar _ = math.NaN\n'
        text = text.replace('package syntheticoscillator\n', preamble, 1)
    go_path.write_text(text)
    zig_path = directory / 'testdata.zig'
    text = zig_path.read_text()
    if 'const math = @import("std").math;' not in text:
        text = 'const math = @import("std").math;\n' + text
    if 'const nan = math.nan(f64);' not in text:
        text = text.replace('const math = @import("std").math;\n',
                            'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(text)

    translated = {'go': [], 'ts': [], 'rs': [], 'zig': []}
    for case in REFERENCE_CASES:
        for field in OUTPUT_FIELDS:
            name = _expected_name(case, field)
            suffix = name.removeprefix('EXPECTED_')
            values = written[name]  # Values come from the verified PYTHON file.
            comments = f'// {case.what_it_tests}\n// {_parameter_comment(case)}\n'
            translated['go'].append(comments + f'var expected{suffix} = []float64{{\n'
                                    + _array_lines(values, '\t', 'math.NaN()') + '\n}')
            translated['ts'].append(comments + f'export const expected{suffix}: number[] = [\n'
                                    + _array_lines(values, '    ', 'NaN') + '\n];')
            translated['rs'].append(comments + f'pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n'
                                    + _array_lines(values, '        ', 'f64::NAN') + '\n    ]\n}')
            translated['zig'].append(comments + f'pub fn expected{suffix}() [252]f64 {{\n    return .{{\n'
                                     + _array_lines(values, '        ', 'nan') + '\n    };\n}')
    for language, filename in (('go', 'testdata_test.go'), ('ts', 'testdata.ts'),
                               ('rs', 'testdata.rs'), ('zig', 'testdata.zig')):
        _write_generated_section(directory / filename, '\n\n'.join(translated[language]), '//')
    print(f'Verified {len(raw_outputs)} arrays of 252 values for {len(REFERENCE_CASES)} cases; wrote all five languages.')


def _float_literal(value: float, nan_literal: str) -> str:
    """Emit 15 significant digits, ensuring an explicit floating-point literal."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("infinite reference output")
    # Rounding happens only here, after the entire binary64 stream calculation.
    # Do not feed these decimal-rounded values back into the filter state.
    literal = format(value, ".15g")
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _array_lines(values: list[float], indent: str, nan_literal: str) -> str:
    """Wrap an array at six values per row for reviewable fixture files."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return "\n".join(
        indent + ", ".join(literals[i:i + 6]) + ","
        for i in range(0, len(literals), 6)
    )


def _write_generated_section(path: Path, section: str, comment: str) -> None:
    """Preserve copied input data; append or replace only the marked outputs."""
    begin = f"{comment} BEGIN GENERATED SYNTHETIC OSCILLATOR EXPECTED DATA"
    end = f"{comment} END GENERATED SYNTHETIC OSCILLATOR EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    generated = begin + "\n\n" + section.rstrip() + "\n\n" + end + "\n"
    if begin in original:
        # Never truncate a malformed existing file after a lone start marker.
        start = original.index(begin)
        finish = original.index(end, start) + len(end)
        result = original[:start] + generated.rstrip("\n") + original[finish:]
    else:
        result = original.rstrip() + "\n\n" + generated
    path.write_text(result, encoding="utf-8")


def _load_literal_arrays(path: Path) -> dict[str, list[float]]:
    """Read fixture list assignments without imports or arbitrary execution."""
    arrays = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.List):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            values = []
            for element in node.value.elts:
                if (isinstance(element, ast.Attribute) and isinstance(element.value, ast.Name)
                        and element.value.id == "math" and element.attr == "nan"):
                    values.append(math.nan)
                else:
                    values.append(float(ast.literal_eval(element)))
            arrays[target.id] = values
    return arrays



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data', action='store_true',
                        help='regenerate all 16 confirmed parameter cases')
    arguments = parser.parse_args()

    INPUT_CLOSE = [
        91.500000, 94.815000, 94.375000, 95.095000, 93.780000, 94.625000, 92.530000, 92.750000, 90.315000, 92.470000,
        96.125000, 97.250000, 98.500000, 89.875000, 91.000000, 92.815000, 89.155000, 89.345000, 91.625000, 89.875000,
        88.375000, 87.625000, 84.780000, 83.000000, 83.500000, 81.375000, 84.440000, 89.250000, 86.375000, 86.250000,
        85.250000, 87.125000, 85.815000, 88.970000, 88.470000, 86.875000, 86.815000, 84.875000, 84.190000, 83.875000,
        83.375000, 85.500000, 89.190000, 89.440000, 91.095000, 90.750000, 91.440000, 89.000000, 91.000000, 90.500000,
        89.030000, 88.815000, 84.280000, 83.500000, 82.690000, 84.750000, 85.655000, 86.190000, 88.940000, 89.280000,
        88.625000, 88.500000, 91.970000, 91.500000, 93.250000, 93.500000, 93.155000, 91.720000, 90.000000, 89.690000,
        88.875000, 85.190000, 83.375000, 84.875000, 85.940000, 97.250000, 99.875000, 104.940000, 106.000000, 102.500000,
        102.405000, 104.595000, 106.125000, 106.000000, 106.065000, 104.625000, 108.625000, 109.315000, 110.500000, 112.750000,
        123.000000, 119.625000, 118.750000, 119.250000, 117.940000, 116.440000, 115.190000, 111.875000, 110.595000, 118.125000,
        116.000000, 116.000000, 112.000000, 113.750000, 112.940000, 116.000000, 120.500000, 116.620000, 117.000000, 115.250000,
        114.310000, 115.500000, 115.870000, 120.690000, 120.190000, 120.750000, 124.750000, 123.370000, 122.940000, 122.560000,
        123.120000, 122.560000, 124.620000, 129.250000, 131.000000, 132.250000, 131.000000, 132.810000, 134.000000, 137.380000,
        137.810000, 137.880000, 137.250000, 136.310000, 136.250000, 134.630000, 128.250000, 129.000000, 123.870000, 124.810000,
        123.000000, 126.250000, 128.380000, 125.370000, 125.690000, 122.250000, 119.370000, 118.500000, 123.190000, 123.500000,
        122.190000, 119.310000, 123.310000, 121.120000, 123.370000, 127.370000, 128.500000, 123.870000, 122.940000, 121.750000,
        124.440000, 122.000000, 122.370000, 122.940000, 124.000000, 123.190000, 124.560000, 127.250000, 125.870000, 128.860000,
        132.000000, 130.750000, 134.750000, 135.000000, 132.380000, 133.310000, 131.940000, 130.000000, 125.370000, 130.130000,
        127.120000, 125.190000, 122.000000, 125.000000, 123.000000, 123.500000, 120.060000, 121.000000, 117.750000, 119.870000,
        122.000000, 119.190000, 116.370000, 113.500000, 114.250000, 110.000000, 105.060000, 107.000000, 107.870000, 107.000000,
        107.120000, 107.000000, 91.000000, 93.940000, 93.870000, 95.500000, 93.000000, 94.940000, 98.250000, 96.750000,
        94.810000, 94.370000, 91.560000, 90.250000, 93.940000, 93.620000, 97.000000, 95.000000, 95.870000, 94.060000,
        94.620000, 93.750000, 98.000000, 103.940000, 107.870000, 106.060000, 104.500000, 105.000000, 104.190000, 103.060000,
        103.420000, 105.270000, 111.870000, 116.000000, 116.620000, 118.280000, 113.370000, 109.000000, 109.700000, 109.250000,
        107.000000, 109.190000, 110.000000, 109.200000, 110.120000, 108.000000, 108.620000, 109.750000, 109.810000, 109.000000,
        108.750000, 107.870000,
    ]

    # Observe the same 252 copied closes once each, with no external data feed.
    indicator = SyntheticOscillator(lower_bound=15, upper_bound=25, length=4)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print('Default first five primed values (indices 110-114):', ', '.join(
        _float_literal(v, 'NaN') for v in outputs[110:115]))
    print('Reference parameter cases:')
    for case in REFERENCE_CASES:
        print(f'  {_case_suffix(case)}: {case.what_it_tests}')
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
