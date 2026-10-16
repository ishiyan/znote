"""July 2025 Laguerre Oscillator: self-contained streaming master reference.

Only the standard library is required. See description.md for the complete
theory, source differences, initialization and fixture conversion conventions.
All 16 Length/Gamma pairs are confirmed. Run normally for a demonstration;
--generate-reference-data regenerates all five languages' expected arrays.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# The master follows the user's full-precision preference. Do not truncate
# these constants when converting into another language or computing state.
PI = math.pi
SQRT_TWO = math.sqrt(2.0)


def _validate_length(length: float) -> float:
    """Length sets coefficients; it is a real period, not a sample count."""
    if isinstance(length, bool):
        raise ValueError('length must be a finite real period of at least 1')
    length = float(length)
    if not math.isfinite(length) or length < 1.0:
        raise ValueError('length must be finite and at least 1.0')
    return length


def _validate_gamma(gamma: float) -> float:
    """Restrict gamma to the conventional nonnegative, stable pole range."""
    if isinstance(gamma, bool):
        raise ValueError('gamma must be a finite real number in [0, 1)')
    gamma = float(gamma)
    if not math.isfinite(gamma) or not 0.0 <= gamma < 1.0:
        raise ValueError('gamma must be finite and satisfy 0 <= gamma < 1')
    return gamma


class UltimateSmoother:
    """Source UltimateSmoother with first-three-input startup and two lags.

    The full_precision default uses sqrt(2) and pi consistently. article uses
    the exact printed exponential constants and a degree-based cosine.
    Neither precision policy changes the source's arithmetic or bar numbering.
    """

    def __init__(self, period: float = 20.0, *, coefficient_mode: str = 'full_precision') -> None:
        self.period = _validate_length(period)
        if coefficient_mode == 'full_precision':
            angle = SQRT_TWO * PI / self.period
            a1 = math.exp(-angle)
            b1 = 2.0 * a1 * math.cos(angle)
        elif coefficient_mode == 'article':
            # Exponent and cosine angles are deliberately computed separately:
            # EasyLanguage Cosine accepts degrees, converted with full pi.
            a1 = math.exp(-1.414 * 3.14159 / self.period)
            b1 = 2.0 * a1 * math.cos(math.radians(1.414 * 180.0 / self.period))
        else:
            raise ValueError('coefficient_mode must be "full_precision" or "article"')
        self._c2 = b1
        self._c3 = -a1 * a1  # Negative; the recurrence ADDS this signed product.
        self._c1 = (1.0 + self._c2 - self._c3) / 4.0
        self.reset()

    def reset(self) -> None:
        """Clear raw price and smoother output histories independently."""
        self._count = 0
        self._price1 = self._price2 = 0.0
        self._output1 = self._output2 = 0.0

    def update(self, price: float) -> float:
        price = float(price)
        if not math.isfinite(price):
            raise ValueError('price must be finite')
        if self._count < 3:
            # CurrentBar=count+1: source bars 1, 2, 3 pass Price through.
            output = price
        else:
            # Keep the original operation order and signs, and evaluate with
            # OLD histories. Compute coefficients once, never on rounded data.
            output = (
                (1.0 - self._c1) * price
                + (2.0 * self._c1 - self._c2) * self._price1
                - (self._c1 + self._c3) * self._price2
                + self._c2 * self._output1
                + self._c3 * self._output2
            )
        if not math.isfinite(output):
            raise ValueError('UltimateSmoother output must be finite')
        self._price2, self._price1 = self._price1, price
        self._output2, self._output1 = self._output1, output
        self._count += 1
        return output


class ReferenceCase(NamedTuple):
    """One confirmed Length/Gamma pair and its exact fixture comment."""

    length: float
    gamma: float
    what_it_tests: str


# Identical confirmed pairs allow direct comparison of the two indicators.
# All 16 pairs were confirmed by the user for both indicators on 2026-10-16.
REFERENCE_CASES = (
    ReferenceCase(40.0, 0.8, 'Filter default.'),
    ReferenceCase(30.0, 0.5, 'Oscillator default.'),
    ReferenceCase(30.0, 0.8, 'Article\'s first Filter chart.'),
    ReferenceCase(60.0, 0.2, 'Article\'s crossover example.'),
    ReferenceCase(20.0, 0.8, 'Article\'s Oscillator chart.'),
    ReferenceCase(1.0, 0.0, 'Minimum period and pure-delay boundary.'),
    ReferenceCase(2.0, 0.2, 'Nyquist-period boundary.'),
    ReferenceCase(5.0, 0.5, 'Short-period response.'),
    ReferenceCase(10.0, 0.8, 'Short smoother with strong stage memory.'),
    ReferenceCase(20.0, 0.0, 'Zero-gamma limit.'),
    ReferenceCase(20.0, 0.2, 'Low stage memory.'),
    ReferenceCase(20.0, 0.5, 'Moderate stage memory.'),
    ReferenceCase(20.0, 0.95, 'Long stage memory.'),
    ReferenceCase(20.0, 0.99, 'Near-unit-pole behavior.'),
    ReferenceCase(20.5, 0.8, 'Fractional smoother period.'),
    ReferenceCase(252.0, 0.8, 'Full-record period.'),
)


# The source calls $RMS(L0-L1,100): normalization length is fixed at 100.
RMS_LENGTH = 100
OUTPUT_FIELDS = ('oscillator',)
WARMUP_BARS = {'oscillator': RMS_LENGTH - 1}


class RootMeanSquare:
    """Finite-window RMS preserving the source's conditional zero-sum return.

    This helper accepts an integer length >= 1 for direct verification, but
    LaguerreOscillator always constructs it with the article's fixed 100.
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





class LaguerreOscillator:
    """UltimateSmoother minus its first allpass stage, scaled to 100-bar RMS.

    Defaults length=30, gamma=0.5, recurrence_mode='tradestation'. This is the
    allpass recurrence in TradeStation and Mesa, -gamma*CURRENT_L0. The article
    transcription uses -gamma*PREVIOUS_L0, available via recurrence_mode='article'.
    For matched initialization the raw differences are proportional by 1+gamma,
    so RMS-normalized results agree mathematically, with rounding differences.
    The first 99 normalized outputs are NaN, while all internal states advance.
    """

    def __init__(self, length: float = 30.0, gamma: float = 0.5,
                 *, coefficient_mode: str = 'full_precision',
                 recurrence_mode: str = 'tradestation') -> None:
        self._length = _validate_length(length)
        self._gamma = _validate_gamma(gamma)
        if recurrence_mode not in ('tradestation', 'article'):
            raise ValueError('recurrence_mode must be "tradestation" or "article"')
        self._recurrence_mode = recurrence_mode
        self._coefficient_mode = coefficient_mode
        self._smoother = UltimateSmoother(self._length, coefficient_mode=coefficient_mode)
        self._rms_filter = RootMeanSquare(RMS_LENGTH)
        self.reset()

    @property
    def length(self) -> float:
        return self._length

    @property
    def gamma(self) -> float:
        return self._gamma

    @property
    def coefficient_mode(self) -> str:
        return self._coefficient_mode

    @property
    def recurrence_mode(self) -> str:
        return self._recurrence_mode

    @property
    def is_primed(self) -> bool:
        return self._rms_filter.is_primed

    @property
    def warmup_bars(self) -> int:
        return RMS_LENGTH - 1

    @property
    def l0(self) -> float:
        return self._l0

    @property
    def l1(self) -> float:
        return self._l1

    @property
    def signal(self) -> float:
        """Latest unnormalized L0-L1, in price units."""
        return self._signal

    @property
    def rms(self) -> float:
        return self._rms

    def reset(self) -> None:
        self._smoother.reset()
        self._rms_filter.reset()
        self._l0 = self._l1 = self._signal = 0.0
        self._rms = math.nan
        self._last_output = 0.0

    def update(self, close: float) -> float:
        close = float(close)
        if not math.isfinite(close):
            raise ValueError('close must be finite')
        l0 = self._smoother.update(close)
        gamma = self._gamma
        if self._recurrence_mode == 'tradestation':
            # Allpass: current L0 is in the NEGATIVE term; old L0 and old L1
            # are the other two terms. Compute before committing current L0.
            l1 = -gamma * l0 + self._l0 + gamma * self._l1
        else:
            # Literal article transcription: both input terms use old L0.
            l1 = -gamma * self._l0 + self._l0 + gamma * self._l1
        signal = l0 - l1
        # Normalize the DIFFERENCE, never L1, L0, or the raw close separately.
        rms = self._rms_filter.update(signal)
        self._l0, self._l1, self._signal, self._rms = l0, l1, signal, rms
        if not self.is_primed:
            return math.nan
        # Retain the source's persistent output if RMS is zero. RMS itself
        # separately retains its prior result when the full squared sum is zero.
        if rms != 0.0:
            self._last_output = signal / rms
        return self._last_output


def _parameter_token(value: float) -> str:
    """Use compact integer tokens and underscores for fractional values."""
    return format(value, 'g').replace('.', '_')


def _case_suffix(case: ReferenceCase) -> str:
    return f'L{_parameter_token(case.length)}_G{_parameter_token(case.gamma)}'


def _parameter_comment(case: ReferenceCase) -> str:
    return f'length={case.length:g}, gamma={case.gamma:g}'


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
        # documented master defaults; only Length and Gamma vary in fixtures.
        indicator = LaguerreOscillator(case.length, case.gamma)
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
    text = go_path.read_text().replace('package xxxx', 'package laguerreoscillator', 1)
    if 'import "math"' not in text:
        preamble = 'package laguerreoscillator\n\nimport "math"\n'
        if not any(math.isnan(v) for name in raw_outputs for v in written[name]):
            # Go rejects unused imports. Keep the requested NaN helper import
            # without inserting artificial NaNs into defined startup outputs.
            preamble += '\n// Keep the NaN helper available; startup outputs are defined.\nvar _ = math.NaN\n'
        text = text.replace('package laguerreoscillator\n', preamble, 1)
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
    begin = f"{comment} BEGIN GENERATED LAGUERRE OSCILLATOR EXPECTED DATA"
    end = f"{comment} END GENERATED LAGUERRE OSCILLATOR EXPECTED DATA"
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
                        help='regenerate all confirmed cases in five languages')
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

    # Streaming example: observe each close once in chronological order.
    # No external market-data service or scientific Python package is required.
    indicator = LaguerreOscillator(length=30.0, gamma=0.5)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print('Default first available results:', outputs[indicator.warmup_bars:indicator.warmup_bars + 5])
    print('Confirmed parameter cases:')
    for case in REFERENCE_CASES:
        print(f'  {_case_suffix(case)}: {case.what_it_tests}')
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
