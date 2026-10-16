"""Ultimate Bands: self-contained streaming research master and fixture generator.

Source authority: May 2024 Ultimate Channels And Ultimate Bands, supplemented
by April 2024 Ultimate Smoother. Uses full-precision pi and sqrt(2), as requested.
See description.md for exact startup, formulas, pitfalls, and porting rules.
Standard Python only. Run without flags for a streaming example; use
--generate-reference-data after confirming the listed parameter cases.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# Binary64 mathematical constants, rather than the printed 3.14159 and 1.414.
# A port should use its standard pi constant and sqrt(2.0), not rounded decimals.
PI = math.pi
SQRT_TWO = math.sqrt(2.0)


class UltimateSmoother:
    """Second-order lowpass formed by subtracting a highpass from raw input.

    period is a finite real number >= 1.0, measured in bars; default 20.0.
    Fractional periods are supported. This is a coefficient-setting parameter,
    not a rolling window length and not a required count of warm-up observations.

    The first three successful updates return their input unchanged. Thereafter
    the article's recurrence uses two previous raw prices and two previous
    outputs. All samples are consumed once, chronologically, without look-ahead.
    """

    def __init__(self, period: float = 20.0) -> None:
        self._period = float(period)
        # The supplied NinjaTrader UI uses a minimum period of one. The article
        # does not specify a minimum; this API accepts fractional periods >= 1.
        if not math.isfinite(self._period) or self._period < 1.0:
            raise ValueError("period must be finite and at least 1.0")

        # Full-precision radian form of the source's degree-based coefficients.
        # Compute this angle once; its negative sets the pole radius and its
        # cosine sets the pole rotation. Both child poles have radius a1 < 1.
        angle = SQRT_TWO * PI / self._period
        a1 = math.exp(-angle)
        b1 = 2.0 * a1 * math.cos(angle)

        # Keep the article's April 2024 names and signs. In particular c3 is
        # NEGATIVE, so the last recurrence term is +c3*previous_previous_output.
        self._c2 = b1
        self._c3 = -a1 * a1
        self._c1 = (1.0 + self._c2 - self._c3) / 4.0
        self.reset()

    @property
    def period(self) -> float:
        """Read-only configuration; construct another filter to change period."""
        return self._period

    @property
    def is_primed(self) -> bool:
        """True after the first update, since startup outputs are defined."""
        return self._count > 0

    @property
    def warmup_bars(self) -> int:
        """Number of leading NaN outputs: zero for the article's pass-through."""
        return 0

    def reset(self) -> None:
        """Clear histories; the next three observations will pass through."""
        self._count = 0
        # These initial zero histories are never read by the recursive formula:
        # the first three pass-through samples fill them before recursion starts.
        self._price1 = self._price2 = 0.0
        self._output1 = self._output2 = 0.0

    def update(self, price: float) -> float:
        """Consume one finite price and return this bar's smoothed price."""
        price = float(price)
        if not math.isfinite(price):
            # Check before any state changes. Do not silently fill missing bars.
            raise ValueError("price must be finite")

        if self._count < 3:
            # With standalone CurrentBar=count+1, the article's CurrentBar<4
            # branch applies to indices 0, 1, and 2. It assigns US=Price.
            output = price
        else:
            # Exactly the article's direct-form recurrence, with today's Price
            # and the two PRIOR raw inputs and outputs. Do not overwrite any of
            # those values until the entire expression has been evaluated.
            output = (
                (1.0 - self._c1) * price
                + (2.0 * self._c1 - self._c2) * self._price1
                - (self._c1 + self._c3) * self._price2
                + self._c2 * self._output1
                + self._c3 * self._output2
            )

        # Reject arithmetic overflow before committing. Ordinary finite prices
        # in the fixtures never take this branch. A rejected input does not
        # advance the successful-sample count or either history.
        if not math.isfinite(output):
            raise ValueError("filtered output must be finite")

        # Shift older values before assigning current values. Tuple assignment
        # makes simultaneous history updates explicit in this Python reference.
        self._price2, self._price1 = self._price1, price
        self._output2, self._output1 = self._output1, output
        self._count += 1
        return output


class BandsResult(NamedTuple):
    """Center is available immediately; other fields need a complete window."""

    center: float
    standard_deviation: float
    upper: float
    lower: float


class UltimateBands:
    """UltimateSmoother center plus/minus the article's residual RMS width.

    length is an integer >= 1, default 20. It is BOTH the smoother period and
    the count of historical residuals in the RMS. num_sds is finite and >= 0,
    default 1. A residual is close[t]-smooth[t], paired on the SAME bar.
    First length-1 updates return NaN for SD and both bounds; center is valid.
    """

    def __init__(self, length: int = 20, num_sds: float = 1.0) -> None:
        # A floating-point length is ambiguous in the inclusive source loop.
        # Reject it rather than truncating or rounding a requested window.
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError('length must be an integer of at least 1')
        self.length = length
        self.num_sds = float(num_sds)
        if not math.isfinite(self.num_sds) or self.num_sds < 0.0:
            raise ValueError('num_sds must be finite and nonnegative')
        self._center_filter = UltimateSmoother(length)
        self.reset()

    @property
    def is_primed(self) -> bool:
        """True once all length residuals are available, including startup zeros."""
        return len(self._squares) == self.length

    @property
    def warmup_bars(self) -> int:
        """Number of leading NaNs in SD, upper and lower; center has none."""
        return self.length - 1

    def reset(self) -> None:
        """Clear smoother history, residual ring, and source SD persistent value."""
        self._center_filter.reset()
        self._squares = []
        self._next = 0
        # Vars: SD(0) in EasyLanguage initializes persistent SD to ZERO.
        # It is not assigned NaN internally during unavailable output bars.
        self._sd = 0.0

    def update(self, close: float) -> BandsResult:
        """Consume one close and return center, residual RMS, upper and lower."""
        close = float(close)
        if not math.isfinite(close):
            raise ValueError('close must be finite')
        center = self._center_filter.update(close)
        residual = close - center
        square = residual * residual

        # Store just the squared paired residual, not a whole price window.
        # Growing until full avoids preallocating a huge requested length.
        if len(self._squares) < self.length:
            self._squares.append(square)
            self._next = len(self._squares) % self.length
        else:
            self._squares[self._next] = square
            self._next = (self._next + 1) % self.length

        if not self.is_primed:
            # Do not pad absent history with zero or divide a partial sum by a
            # different denominator. Feed all closes into the smoother anyway.
            return BandsResult(center, math.nan, math.nan, math.nan)

        # Match For count=0 to Length-1 INCLUSIVELY: exactly length terms,
        # newest first. A running sum changes rounding and accumulates drift;
        # this research master deliberately uses the original O(length) loop.
        total = 0.0
        for count in range(self.length):
            index = (self._next - 1 - count) % self.length
            total = total + self._squares[index]

        # Preserve the author's conditional assignment, including its subtle
        # zero-window behavior: if total == 0, retain the PREVIOUS SD. Setting
        # SD=0 unconditionally would be a reasonable change but a different
        # algorithm. This is RMS about zero, not stdev about mean(residual).
        if total != 0.0:
            self._sd = math.sqrt(total / self.length)
        displacement = self.num_sds * self._sd
        return BandsResult(center, self._sd, center + displacement,
                           center - displacement)


class ReferenceCase(NamedTuple):
    """One confirmed integer window and multiplier plus fixture comment."""

    length: int
    num_sds: float
    what_it_tests: str


OUTPUT_FIELDS = ('center', 'standard_deviation', 'upper', 'lower')
OUTPUT_TOKENS = ('CENTER', 'SD', 'UPPER', 'LOWER')


def _case_suffix(case: ReferenceCase) -> str:
    """L=length, M=NumSDs; field suffix distinguishes four output arrays."""
    return f'L{case.length}_M{_parameter_token(case.num_sds)}'


def _parameter_comment(case: ReferenceCase) -> str:
    return f'length={case.length}, num_sds={case.num_sds:g}'


def _run_case(case: ReferenceCase, arrays: dict[str, list[float]]) -> list[BandsResult]:
    indicator = UltimateBands(case.length, case.num_sds)
    return [indicator.update(close) for close in arrays['INPUT_CLOSE']]


REQUIRED_INPUTS = ('INPUT_CLOSE',)
REFERENCE_CASES = (
    ReferenceCase(20, 1, 'Article default: twenty-bar historical residual RMS with unit width.'),
    ReferenceCase(1, 1, 'Minimum window: one residual, immediate priming, and zero-sum SD retention.'),
    ReferenceCase(2, 1, 'Two-bar window: newest-first residual summation and short warmup.'),
    ReferenceCase(3, 1, 'Three-bar window: first full window consists of pass-through residuals.'),
    ReferenceCase(5, 1, 'Short window: eviction of startup zeros and rapid residual-width response.'),
    ReferenceCase(8, 1, 'Intermediate short window: residual ring-buffer wraparound.'),
    ReferenceCase(40, 1, 'Long window: historical residuals paired with their own smoothed prices.'),
    ReferenceCase(60, 1, 'Longer window: extended warmup and slower RMS width changes.'),
    ReferenceCase(252, 1, 'Full-record window: only the final band pair is primed.'),
    ReferenceCase(20, 0, 'Zero multiplier: primed bands collapse to the center but keep window warmup.'),
    ReferenceCase(20, 0.5, 'Fractional multiplier: half-width without changing residual RMS.'),
    ReferenceCase(20, 2, 'Double multiplier: doubled band displacement without changing residual RMS.'),
)


def _parameter_token(value: float) -> str:
    """Make portable names: 0.2 -> 0_2, -0.2 -> m0_2, 10.0 -> 10."""
    # A minus sign is invalid in an identifier, so 'm' denotes minus. Keep
    # integral parameter values compact; fixtures themselves always use floats.
    return format(value, "g").replace("-", "m").replace(".", "_")


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
    begin = f"{comment} BEGIN GENERATED ULTIMATE BANDS EXPECTED DATA"
    end = f"{comment} END GENERATED ULTIMATE BANDS EXPECTED DATA"
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



def generate_reference_data(arrays: dict[str, list[float]], directory: Path) -> None:
    """Write Python first; verify, then render those written values in four ports.

    This tooling runs only after the proposed cases have been confirmed. Each
    case produces FOUR scalar arrays, one for each named result field. The
    streaming calculation itself never reads any fixture or filesystem path.
    """
    if not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError('case count must be between 1 and 64')
    python_path = directory / 'test_testdata.py'
    copied = _load_literal_arrays(python_path)
    for name in REQUIRED_INPUTS:
        if len(arrays[name]) != 252 or arrays[name] != copied[name]:
            raise ValueError(f'{name} must equal the 252 copied input values')

    raw = {}
    comments_by_name = {}
    sections = []
    for case in REFERENCE_CASES:
        results = _run_case(case, arrays)
        for field, token in zip(OUTPUT_FIELDS, OUTPUT_TOKENS):
            name = 'EXPECTED_' + _case_suffix(case) + '_' + token
            values = [getattr(result, field) for result in results]
            raw[name] = values
            # Both required comments are identical across all five languages.
            comments_by_name[name] = (case.what_it_tests, _parameter_comment(case))
            sections.append(f'# {case.what_it_tests}\n# {_parameter_comment(case)}\n'
                            + f'{name} = [\n' + _array_lines(values, '    ', 'math.nan') + '\n]')
    _write_generated_section(python_path, '\n\n'.join(sections), '#')

    # Round only for serialization, never in recursive filter state. Check
    # the actual Python file before translating those stored decimal values.
    written = _load_literal_arrays(python_path)
    if {name for name in written if name.startswith('EXPECTED_')} != set(raw):
        raise ValueError('unexpected or missing expected arrays')
    for name, originals in raw.items():
        if len(written[name]) != 252:
            raise ValueError(f'{name} does not contain 252 values')
        for before, after in zip(originals, written[name]):
            if math.isnan(before) and math.isnan(after):
                continue
            if not math.isfinite(before) or not math.isclose(before, after, rel_tol=5e-14, abs_tol=5e-14):
                raise ValueError(f'{name} has an invalid value or insufficient precision')

    language_sections = {language: [] for language in ('go', 'ts', 'rs', 'zig')}
    for name in raw:
        suffix = name.removeprefix('EXPECTED_')
        values = written[name]
        what, parameters = comments_by_name[name]
        comments = f'// {what}\n// {parameters}\n'
        language_sections['go'].append(comments + f'var expected{suffix} = []float64{{\n'
                                       + _array_lines(values, '\t', 'math.NaN()') + '\n}')
        language_sections['ts'].append(comments + f'export const expected{suffix}: number[] = [\n'
                                       + _array_lines(values, '    ', 'NaN') + '\n];')
        language_sections['rs'].append(comments + f'pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n'
                                       + _array_lines(values, '        ', 'f64::NAN') + '\n    ]\n}')
        language_sections['zig'].append(comments + f'pub fn expected{suffix}() [252]f64 {{\n    return .{{\n'
                                        + _array_lines(values, '        ', 'nan') + '\n    };\n}')
    for language, filename in (('go','testdata_test.go'), ('ts','testdata.ts'),
                               ('rs','testdata.rs'), ('zig','testdata.zig')):
        _write_generated_section(directory / filename, '\n\n'.join(language_sections[language]), '//')
    print(f'Verified {len(REFERENCE_CASES)} cases, {len(raw)} arrays of 252 values in all five languages.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data', action='store_true',
                        help='generate the approved cases in all five languages')
    arguments = parser.parse_args()

    # Exactly the 252 INPUT_CLOSE observations from the shared Python fixture.
    INPUT_CLOSE = [
        91.500000, 94.815000, 94.375000, 95.095000, 93.780000, 94.625000, 92.530000, 92.750000,
        90.315000, 92.470000, 96.125000, 97.250000, 98.500000, 89.875000, 91.000000, 92.815000,
        89.155000, 89.345000, 91.625000, 89.875000, 88.375000, 87.625000, 84.780000, 83.000000,
        83.500000, 81.375000, 84.440000, 89.250000, 86.375000, 86.250000, 85.250000, 87.125000,
        85.815000, 88.970000, 88.470000, 86.875000, 86.815000, 84.875000, 84.190000, 83.875000,
        83.375000, 85.500000, 89.190000, 89.440000, 91.095000, 90.750000, 91.440000, 89.000000,
        91.000000, 90.500000, 89.030000, 88.815000, 84.280000, 83.500000, 82.690000, 84.750000,
        85.655000, 86.190000, 88.940000, 89.280000, 88.625000, 88.500000, 91.970000, 91.500000,
        93.250000, 93.500000, 93.155000, 91.720000, 90.000000, 89.690000, 88.875000, 85.190000,
        83.375000, 84.875000, 85.940000, 97.250000, 99.875000, 104.940000, 106.000000, 102.500000,
        102.405000, 104.595000, 106.125000, 106.000000, 106.065000, 104.625000, 108.625000, 109.315000,
        110.500000, 112.750000, 123.000000, 119.625000, 118.750000, 119.250000, 117.940000, 116.440000,
        115.190000, 111.875000, 110.595000, 118.125000, 116.000000, 116.000000, 112.000000, 113.750000,
        112.940000, 116.000000, 120.500000, 116.620000, 117.000000, 115.250000, 114.310000, 115.500000,
        115.870000, 120.690000, 120.190000, 120.750000, 124.750000, 123.370000, 122.940000, 122.560000,
        123.120000, 122.560000, 124.620000, 129.250000, 131.000000, 132.250000, 131.000000, 132.810000,
        134.000000, 137.380000, 137.810000, 137.880000, 137.250000, 136.310000, 136.250000, 134.630000,
        128.250000, 129.000000, 123.870000, 124.810000, 123.000000, 126.250000, 128.380000, 125.370000,
        125.690000, 122.250000, 119.370000, 118.500000, 123.190000, 123.500000, 122.190000, 119.310000,
        123.310000, 121.120000, 123.370000, 127.370000, 128.500000, 123.870000, 122.940000, 121.750000,
        124.440000, 122.000000, 122.370000, 122.940000, 124.000000, 123.190000, 124.560000, 127.250000,
        125.870000, 128.860000, 132.000000, 130.750000, 134.750000, 135.000000, 132.380000, 133.310000,
        131.940000, 130.000000, 125.370000, 130.130000, 127.120000, 125.190000, 122.000000, 125.000000,
        123.000000, 123.500000, 120.060000, 121.000000, 117.750000, 119.870000, 122.000000, 119.190000,
        116.370000, 113.500000, 114.250000, 110.000000, 105.060000, 107.000000, 107.870000, 107.000000,
        107.120000, 107.000000, 91.000000, 93.940000, 93.870000, 95.500000, 93.000000, 94.940000,
        98.250000, 96.750000, 94.810000, 94.370000, 91.560000, 90.250000, 93.940000, 93.620000,
        97.000000, 95.000000, 95.870000, 94.060000, 94.620000, 93.750000, 98.000000, 103.940000,
        107.870000, 106.060000, 104.500000, 105.000000, 104.190000, 103.060000, 103.420000, 105.270000,
        111.870000, 116.000000, 116.620000, 118.280000, 113.370000, 109.000000, 109.700000, 109.250000,
        107.000000, 109.190000, 110.000000, 109.200000, 110.120000, 108.000000, 108.620000, 109.750000,
        109.810000, 109.000000, 108.750000, 107.870000,
    ]

    arrays = {'INPUT_CLOSE': INPUT_CLOSE}
    # Example: every close advances state, including unavailable band bars.
    indicator = UltimateBands(length=20, num_sds=1)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print('Default first five named results:')
    for output in outputs[:5]:
        print({field: _float_literal(getattr(output, field), 'NaN') for field in OUTPUT_FIELDS})
    print('Reference cases (generate only after user confirmation):')
    for case in REFERENCE_CASES:
        print(_case_suffix(case), _parameter_comment(case), case.what_it_tests)
    if arguments.generate_reference_data:
        generate_reference_data(arrays, Path(__file__).resolve().parent)
