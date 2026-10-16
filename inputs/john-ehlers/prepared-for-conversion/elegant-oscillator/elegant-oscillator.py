"""Elegant Oscillator: February 2022 article/TradeStation streaming master.

Only the Python standard library is needed. See description.md for all source
equations, physical interpretation, startup and differences between platforms.
Default coefficients use full pi and sqrt(2), following the user's preference;
coefficient_mode='article' preserves the two printed coefficient constants.

The first 51 returned values are NaN while TWO actual price delays and FIFTY
actual derivatives become available. Internal unavailable limiter values and
recursive histories stay zero. A full all-zero RMS window maps to a neutral
normalized derivative of zero, extending the article's undefined 0/0 case.

Run without flags to demonstrate the embedded 252 closes. Run with
--generate-reference-data to regenerate all twelve confirmed cases in the
five copied fixtures. The indicator class itself performs no file I/O.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


PI = math.pi
SQRT_TWO = math.sqrt(2.0)
DERIVATIVE_LAG = 2
RMS_LENGTH = 50
OUTPUT_FIELDS = ('oscillator',)
WARMUP_BARS = {'oscillator': DERIVATIVE_LAG + RMS_LENGTH - 1}


class ElegantState(NamedTuple):
    """Current intermediate values, without the scalar availability mask."""

    derivative: float
    rms: float
    normalized_derivative: float
    inverse_fisher: float
    super_smoother: float


class ElegantOscillator:
    """Whiten price, normalize energy, soft-limit, and smooth the result.

    band_edge is a finite real period >=1, not an integer window length.
    RMS length is fixed at the article's 50; the price difference is fixed at
    two bars. Fractional band edges are supported without rounding.

    update(close) returns one float. is_primed becomes true on observation 52
    (zero-based index 51). No clipping is applied to the final IIR output:
    the inverse Fisher stage is bounded, but the smoother can overshoot.
    """

    def __init__(self, band_edge: float = 20.0, *,
                 coefficient_mode: str = 'full_precision') -> None:
        if isinstance(band_edge, bool):
            raise ValueError('band_edge must be a finite real number >=1')
        self._band_edge = float(band_edge)
        if not math.isfinite(self._band_edge) or self._band_edge < 1.0:
            raise ValueError('band_edge must be finite and at least 1')
        if coefficient_mode == 'full_precision':
            # Source Cosine uses degrees. Replacing 1.414 with sqrt(2) and
            # 3.14159 with pi gives this consistent radian angle for both uses.
            angle = SQRT_TWO * PI / self._band_edge
            a1 = math.exp(-angle)
            b1 = 2.0 * a1 * math.cos(angle)
        elif coefficient_mode == 'article':
            # Keep the rounded exponential distinct from the degree cosine.
            # Standard degree-to-radian conversion uses full pi in this mode.
            a1 = math.exp(-1.414 * 3.14159 / self._band_edge)
            b1 = 2.0 * a1 * math.cos(math.radians(1.414 * 180.0 / self._band_edge))
        else:
            raise ValueError('coefficient_mode must be "full_precision" or "article"')
        self._coefficient_mode = coefficient_mode
        # Keep the article's names and signed coefficients. c3 is NEGATIVE.
        # In this 2022 listing c1 has NO factor of 1/2; division occurs inside
        # the recurrence. Avoid substituting the 2026 folded-gain convention.
        self._c2 = b1
        self._c3 = -a1 * a1
        self._c1 = 1.0 - self._c2 - self._c3
        self.reset()

    @property
    def band_edge(self) -> float:
        return self._band_edge

    @property
    def coefficient_mode(self) -> str:
        return self._coefficient_mode

    @property
    def warmup_bars(self) -> int:
        """Number of leading unavailable scalar outputs, independent of P."""
        return WARMUP_BARS['oscillator']

    @property
    def is_primed(self) -> bool:
        """A complete window exists even when every derivative equals zero."""
        return len(self._squares) == RMS_LENGTH

    @property
    def state(self) -> ElegantState:
        """Inspect derivative/RMS availability and the internal finite output."""
        return self._state

    def reset(self) -> None:
        """Restart without preloaded closes, derivatives or smoothed values."""
        self._count = 0
        self._close1 = self._close2 = 0.0
        self._squares = []
        self._next = 0
        self._ifish1 = 0.0
        self._ss1 = self._ss2 = 0.0
        self._state = ElegantState(math.nan, math.nan, 0.0, 0.0, 0.0)

    def update(self, close: float) -> float:
        """Consume one chronological close using bounded history and no lookahead."""
        close = float(close)
        if not math.isfinite(close):
            # This check precedes all state changes; missing inputs do not
            # become zeros and do not consume a bar or alter filter histories.
            raise ValueError('close must be finite')

        derivative = rms = math.nan
        normalized = ifish = 0.0
        if self._count >= DERIVATIVE_LAG:
            # Close[2] is the close TWO raw updates ago, not previous derivative
            # or previous oscillator. Do not divide this difference by two.
            derivative = close - self._close2
            square = derivative * derivative
            if not math.isfinite(square):
                raise ValueError('squared price difference must be finite')

            # RMS needs exactly 50 ACTUAL derivatives. Do not count the first
            # two unavailable differences, zero-pad, or use a partial average.
            if len(self._squares) < RMS_LENGTH:
                self._squares.append(square)
                self._next = len(self._squares) % RMS_LENGTH
            else:
                self._squares[self._next] = square
                self._next = (self._next + 1) % RMS_LENGTH

            if self.is_primed:
                # Re-sum each window newest-to-oldest exactly as the source's
                # for count=0 to 49 loop does. A rolling or compensated sum
                # is a different floating-point reference calculation.
                sum_squares = 0.0
                for lag in range(RMS_LENGTH):
                    index = (self._next - 1 - lag) % RMS_LENGTH
                    sum_squares = sum_squares + self._squares[index]
                if not math.isfinite(sum_squares):
                    raise ValueError('RMS squared sum must be finite')

                # Source resets RMS=0 every bar. Unlike a persistent RMS helper,
                # a zero window does NOT retain a previous RMS measurement.
                rms = math.sqrt(sum_squares / RMS_LENGTH) if sum_squares != 0.0 else 0.0
                if rms != 0.0:
                    normalized = derivative / rms
                # Explicit safe extension: an all-zero window maps 0/0 to 0.
                # eSignal's Calc_NDeriv also initializes this branch to zero.
                # No epsilon or volatility floor changes any nonzero window.
                exponential = math.exp(2.0 * normalized)
                ifish = (exponential - 1.0) / (exponential + 1.0)
                # This equals tanh(normalized) in exact arithmetic. Preserve
                # the displayed exponential ratio for source rounding fidelity.

        # Match the raw-bar CurrentBar<3 assignment: the first two SS values
        # are zero. While normalization history is missing, zero limiter inputs
        # maintain zero SS state. On the FIRST available normalization (t=51),
        # recurse immediately with previous IFish=0 and previous SS values=0;
        # do not restart a local filter clock or discard two normalized samples.
        if self._count < 2:
            ss = 0.0
        else:
            ss = (self._c1 * (ifish + self._ifish1) / 2.0
                  + self._c2 * self._ss1 + self._c3 * self._ss2)
        if not math.isfinite(ss):
            raise ValueError('SuperSmoother output must be finite')

        # Delayed histories are committed only after reading the preceding
        # values. The returned NaN is NEVER stored in any recursive history.
        self._close2, self._close1 = self._close1, close
        self._ifish1 = ifish
        self._ss2, self._ss1 = self._ss1, ss
        self._count += 1
        self._state = ElegantState(derivative, rms, normalized, ifish, ss)
        return ss if self.is_primed else math.nan


class ReferenceCase(NamedTuple):
    """Confirmed BandEdge value and the exact portable fixture comment."""

    band_edge: float
    what_it_tests: str


# All twelve cases were confirmed by the user on 2026-10-16.
# RMS=50 and derivative lag=2 remain fixed, as in the article.
REFERENCE_CASES = (
    ReferenceCase(1.0, 'Minimum supported BandEdge.'),
    ReferenceCase(2.0, 'TradingView minimum BandEdge.'),
    ReferenceCase(3.0, 'Very short smoothing period.'),
    ReferenceCase(5.0, 'Short-cycle response.'),
    ReferenceCase(8.0, 'Fast swing response.'),
    ReferenceCase(10.0, 'Half-default smoothing period.'),
    ReferenceCase(15.0, 'Intermediate smoothing period.'),
    ReferenceCase(20.0, 'Article and TradeStation default.'),
    ReferenceCase(20.5, 'Fractional BandEdge without truncation.'),
    ReferenceCase(30.0, 'Slower swing response.'),
    ReferenceCase(50.0, 'BandEdge equals the fixed RMS length.'),
    ReferenceCase(252.0, 'BandEdge equals the input record length.'),
)


def _case_suffix(case: ReferenceCase) -> str:
    """For example BE20 or BE20_5; periods are not padded with a .0 token."""
    return 'BE' + format(case.band_edge, 'g').replace('.', '_')


def _parameter_comment(case: ReferenceCase) -> str:
    return f'band_edge={case.band_edge:g}, rms_length=50, derivative_lag=2, coefficient_mode=full_precision'


def _expected_name(case: ReferenceCase, field: str) -> str:
    """Only the varying source parameter appears in this scalar array name."""
    return 'EXPECTED_' + _case_suffix(case)


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
        # documented master defaults; only BandEdge varies in these fixtures.
        indicator = ElegantOscillator(case.band_edge)
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
    text = go_path.read_text().replace('package xxxx', 'package elegantoscillator', 1)
    if 'import "math"' not in text:
        preamble = 'package elegantoscillator\n\nimport "math"\n'
        if not any(math.isnan(v) for name in raw_outputs for v in written[name]):
            # Go rejects unused imports. Keep the requested NaN helper import
            # without inserting artificial NaNs into defined startup outputs.
            preamble += '\n// Keep the NaN helper available; startup outputs are defined.\nvar _ = math.NaN\n'
        text = text.replace('package elegantoscillator\n', preamble, 1)
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
    begin = f"{comment} BEGIN GENERATED ELEGANT OSCILLATOR EXPECTED DATA"
    end = f"{comment} END GENERATED ELEGANT OSCILLATOR EXPECTED DATA"
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
                        help='regenerate all twelve confirmed reference cases')
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

    # The demo processes the exact copied 252 closes, without external feeds.
    indicator = ElegantOscillator(band_edge=20)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print('Default first five primed values (indices 51-55):', ', '.join(
        _float_literal(value, 'NaN') for value in outputs[51:56]))
    print('Confirmed reference cases:')
    for case in REFERENCE_CASES:
        print(f'  {_case_suffix(case)}: {case.what_it_tests}')
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
