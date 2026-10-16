"""Ultimate Channel: self-contained streaming research master and fixture generator.

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


class ChannelResult(NamedTuple):
    """All values for one bar; named fields remove ambiguity for other ports."""

    center: float
    smoothed_true_range: float
    upper: float
    lower: float


class UltimateChannel:
    """Article channel: independent UltimateSmoothers of close and true range.

    length and str_length are finite real periods >= 1, default 20.
    num_strs is a finite nonnegative multiplier, default 1.
    update(close, high, low) consumes ONE complete chronological bar.
    With no preceding close, the first true range is high-low. All four fields
    are valid from the first bar; no leading NaNs or synthetic prior close.
    """

    def __init__(self, length: float = 20.0, str_length: float = 20.0,
                 num_strs: float = 1.0) -> None:
        self._center_filter = UltimateSmoother(length)
        self._range_filter = UltimateSmoother(str_length)
        self.length = self._center_filter.period
        self.str_length = self._range_filter.period
        self.num_strs = float(num_strs)
        if not math.isfinite(self.num_strs) or self.num_strs < 0.0:
            raise ValueError('num_strs must be finite and nonnegative')
        self.reset()

    @property
    def is_primed(self) -> bool:
        """The article's two pass-through paths give valid first-bar values."""
        return self._previous_close is not None

    @property
    def warmup_bars(self) -> int:
        """No leading unavailable channel values under this startup policy."""
        return 0

    def reset(self) -> None:
        """Reset both filters and remove the close used for gap detection."""
        self._center_filter.reset()
        self._range_filter.reset()
        self._previous_close = None

    def update(self, close: float, high: float, low: float) -> ChannelResult:
        """Observe a complete bar; the previous CLOSE detects overnight gaps."""
        close, high, low = float(close), float(high), float(low)
        # Validate the whole bar before updating either stateful filter.
        if not all(math.isfinite(value) for value in (close, high, low)):
            raise ValueError('close, high, and low must be finite')
        if not low <= close <= high:
            raise ValueError('bar must satisfy low <= close <= high')

        # The article uses max(high, previous_close)-min(low, previous_close).
        # On the first bar previous_close is unavailable: use high-low. Zero
        # would be a synthetic prior price and would create an artificial gap.
        if self._previous_close is None:
            true_high, true_low = high, low
        else:
            true_high = max(high, self._previous_close)
            true_low = min(low, self._previous_close)
        true_range = true_high - true_low
        if not math.isfinite(true_range):
            raise ValueError('true range must be finite')

        # Each filter is updated exactly ONCE. The two calls to the same close
        # function shown in EasyLanguage are independent identical series;
        # updating one streaming instance twice would consume two fake bars.
        smoothed_true_range = self._range_filter.update(true_range)
        center = self._center_filter.update(close)
        displacement = self.num_strs * smoothed_true_range
        upper = center + displacement
        lower = center - displacement
        self._previous_close = close

        # Do not clamp STR to zero or sort the two bounds. This IIR can
        # overshoot below zero after a sharp drop in true range. Preserving
        # that behavior is required to reproduce the author's expressions.
        return ChannelResult(center, smoothed_true_range, upper, lower)


class ReferenceCase(NamedTuple):
    """One confirmed parameter case plus its exact fixture comment."""

    length: float
    str_length: float
    num_strs: float
    what_it_tests: str


OUTPUT_FIELDS = ('center', 'smoothed_true_range', 'upper', 'lower')
OUTPUT_TOKENS = ('CENTER', 'STR', 'UPPER', 'LOWER')


def _case_suffix(case: ReferenceCase) -> str:
    """L=center length, S=STR length, M=NumSTRs; decimals use underscores."""
    return f'L{_parameter_token(case.length)}_S{_parameter_token(case.str_length)}_M{_parameter_token(case.num_strs)}'


def _parameter_comment(case: ReferenceCase) -> str:
    return f'length={case.length:g}, str_length={case.str_length:g}, num_strs={case.num_strs:g}'


def _run_case(case: ReferenceCase, arrays: dict[str, list[float]]) -> list[ChannelResult]:
    indicator = UltimateChannel(case.length, case.str_length, case.num_strs)
    return [indicator.update(close, high, low) for close, high, low in zip(
        arrays['INPUT_CLOSE'], arrays['INPUT_HIGH'], arrays['INPUT_LOW'])]


REQUIRED_INPUTS = ('INPUT_CLOSE', 'INPUT_HIGH', 'INPUT_LOW')
REFERENCE_CASES = (
    ReferenceCase(20, 20, 1, 'Article default: twenty-bar center and true-range smoothing with unit width.'),
    ReferenceCase(1, 1, 1, 'Minimum periods: independent smoother startup and gap-aware true range.'),
    ReferenceCase(2, 2, 1, 'Two-bar periods: very short center and range filters.'),
    ReferenceCase(3, 3, 1, 'Three-bar periods: transition from pass-through startup to recursion.'),
    ReferenceCase(5, 5, 1, 'Short equal periods: fast channel response.'),
    ReferenceCase(10.5, 10.5, 1, 'Fractional equal periods: coefficients must not truncate the periods.'),
    ReferenceCase(40, 40, 1, 'Long equal periods: slower pole damping and possible range overshoot.'),
    ReferenceCase(252, 252, 1, 'Full-record periods: outputs remain valid without a rolling-window warmup.'),
    ReferenceCase(20, 5, 1, 'Independent periods: moderate center with fast true-range smoothing.'),
    ReferenceCase(5, 20, 1, 'Independent periods: fast center with moderate true-range smoothing.'),
    ReferenceCase(20, 60, 1, 'Independent periods: moderate center with long range memory.'),
    ReferenceCase(60, 20, 1, 'Independent periods: long center memory with moderate range smoothing.'),
    ReferenceCase(20, 10.5, 1, 'Fractional range period independent of the integer center period.'),
    ReferenceCase(20, 20, 0, 'Zero multiplier: upper and lower collapse onto the center.'),
    ReferenceCase(20, 20, 0.5, 'Fractional multiplier: half-width without altering either smoother.'),
    ReferenceCase(20, 20, 2, 'Double multiplier: doubled channel displacement without changing filter state.'),
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
    begin = f"{comment} BEGIN GENERATED ULTIMATE CHANNEL EXPECTED DATA"
    end = f"{comment} END GENERATED ULTIMATE CHANNEL EXPECTED DATA"
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

    # Exactly the 252 INPUT_HIGH observations from the shared Python fixture.
    INPUT_HIGH = [
        93.250000, 94.940000, 96.375000, 96.190000, 96.000000, 94.720000, 95.000000, 93.720000,
        92.470000, 92.750000, 96.250000, 99.625000, 99.125000, 92.750000, 91.315000, 93.250000,
        93.405000, 90.655000, 91.970000, 92.250000, 90.345000, 88.500000, 88.250000, 85.500000,
        84.440000, 84.750000, 84.440000, 89.405000, 88.125000, 89.125000, 87.155000, 87.250000,
        87.375000, 88.970000, 90.000000, 89.845000, 86.970000, 85.940000, 84.750000, 85.470000,
        84.470000, 88.500000, 89.470000, 90.000000, 92.440000, 91.440000, 92.970000, 91.720000,
        91.155000, 91.750000, 90.000000, 88.875000, 89.000000, 85.250000, 83.815000, 85.250000,
        86.625000, 87.940000, 89.375000, 90.625000, 90.750000, 88.845000, 91.970000, 93.375000,
        93.815000, 94.030000, 94.030000, 91.815000, 92.000000, 91.940000, 89.750000, 88.750000,
        86.155000, 84.875000, 85.940000, 99.375000, 103.280000, 105.375000, 107.625000, 105.250000,
        104.500000, 105.500000, 106.125000, 107.940000, 106.250000, 107.000000, 108.750000, 110.940000,
        110.940000, 114.220000, 123.000000, 121.750000, 119.815000, 120.315000, 119.375000, 118.190000,
        116.690000, 115.345000, 113.000000, 118.315000, 116.870000, 116.750000, 113.870000, 114.620000,
        115.310000, 116.000000, 121.690000, 119.870000, 120.870000, 116.750000, 116.500000, 116.000000,
        118.310000, 121.500000, 122.000000, 121.440000, 125.750000, 127.750000, 124.190000, 124.440000,
        125.750000, 124.690000, 125.310000, 132.000000, 131.310000, 132.250000, 133.880000, 133.500000,
        135.500000, 137.440000, 138.690000, 139.190000, 138.500000, 138.130000, 137.500000, 138.880000,
        132.130000, 129.750000, 128.500000, 125.440000, 125.120000, 126.500000, 128.690000, 126.620000,
        126.690000, 126.000000, 123.120000, 121.870000, 124.000000, 127.000000, 124.440000, 122.500000,
        123.750000, 123.810000, 124.500000, 127.870000, 128.560000, 129.630000, 124.870000, 124.370000,
        124.870000, 123.620000, 124.060000, 125.870000, 125.190000, 125.620000, 126.000000, 128.500000,
        126.750000, 129.750000, 132.690000, 133.940000, 136.500000, 137.690000, 135.560000, 133.560000,
        135.000000, 132.380000, 131.440000, 130.880000, 129.630000, 127.250000, 127.810000, 125.000000,
        126.810000, 124.750000, 122.810000, 122.250000, 121.060000, 120.000000, 123.250000, 122.750000,
        119.190000, 115.060000, 116.690000, 114.870000, 110.870000, 107.250000, 108.870000, 109.000000,
        108.500000, 113.060000, 93.000000, 94.620000, 95.120000, 96.000000, 95.560000, 95.310000,
        99.000000, 98.810000, 96.810000, 95.940000, 94.440000, 92.940000, 93.940000, 95.500000,
        97.060000, 97.500000, 96.250000, 96.370000, 95.000000, 94.870000, 98.250000, 105.120000,
        108.440000, 109.870000, 105.000000, 106.000000, 104.940000, 104.500000, 104.440000, 106.310000,
        112.870000, 116.500000, 119.190000, 121.000000, 122.120000, 111.940000, 112.750000, 110.190000,
        107.940000, 109.690000, 111.060000, 110.440000, 110.120000, 110.310000, 110.440000, 110.000000,
        110.750000, 110.500000, 110.500000, 109.500000,
    ]

    # Exactly the 252 INPUT_LOW observations from the shared Python fixture.
    INPUT_LOW = [
        90.750000, 91.405000, 94.250000, 93.500000, 92.815000, 93.500000, 92.000000, 89.750000,
        89.440000, 90.625000, 92.750000, 96.315000, 96.030000, 88.815000, 86.750000, 90.940000,
        88.905000, 88.780000, 89.250000, 89.750000, 87.500000, 86.530000, 84.625000, 82.280000,
        81.565000, 80.875000, 81.250000, 84.065000, 85.595000, 85.970000, 84.405000, 85.095000,
        85.500000, 85.530000, 87.875000, 86.565000, 84.655000, 83.250000, 82.565000, 83.440000,
        82.530000, 85.065000, 86.875000, 88.530000, 89.280000, 90.125000, 90.750000, 89.000000,
        88.565000, 90.095000, 89.000000, 86.470000, 84.000000, 83.315000, 82.000000, 83.250000,
        84.750000, 85.280000, 87.190000, 88.440000, 88.250000, 87.345000, 89.280000, 91.095000,
        89.530000, 91.155000, 92.000000, 90.530000, 89.970000, 88.815000, 86.750000, 85.065000,
        82.030000, 81.500000, 82.565000, 96.345000, 96.470000, 101.155000, 104.250000, 101.750000,
        101.720000, 101.720000, 103.155000, 105.690000, 103.655000, 104.000000, 105.530000, 108.530000,
        108.750000, 107.750000, 117.000000, 118.000000, 116.000000, 118.500000, 116.530000, 116.250000,
        114.595000, 110.875000, 110.500000, 110.720000, 112.620000, 114.190000, 111.190000, 109.440000,
        111.560000, 112.440000, 117.500000, 116.060000, 116.560000, 113.310000, 112.560000, 114.000000,
        114.750000, 118.870000, 119.000000, 119.750000, 122.620000, 123.000000, 121.750000, 121.560000,
        123.120000, 122.190000, 122.750000, 124.370000, 128.000000, 129.500000, 130.810000, 130.630000,
        132.130000, 133.880000, 135.380000, 135.750000, 136.190000, 134.500000, 135.380000, 133.690000,
        126.060000, 126.870000, 123.500000, 122.620000, 122.750000, 123.560000, 125.810000, 124.620000,
        124.370000, 121.810000, 118.190000, 118.060000, 117.560000, 121.000000, 121.120000, 118.940000,
        119.810000, 121.000000, 122.000000, 124.500000, 126.560000, 123.500000, 121.250000, 121.060000,
        122.310000, 121.000000, 120.870000, 122.060000, 122.750000, 122.690000, 122.870000, 125.500000,
        124.250000, 128.000000, 128.380000, 130.690000, 131.630000, 134.380000, 132.000000, 131.940000,
        131.940000, 129.560000, 123.750000, 126.000000, 126.250000, 124.370000, 121.440000, 120.440000,
        121.370000, 121.690000, 120.000000, 119.620000, 115.500000, 116.750000, 119.060000, 119.060000,
        115.060000, 111.060000, 113.120000, 110.000000, 105.000000, 104.690000, 103.870000, 104.690000,
        105.440000, 107.000000, 89.000000, 92.500000, 92.120000, 94.620000, 92.810000, 94.250000,
        96.250000, 96.370000, 93.690000, 93.500000, 90.000000, 90.190000, 90.500000, 92.120000,
        94.120000, 94.870000, 93.000000, 93.870000, 93.000000, 92.620000, 93.560000, 98.370000,
        104.440000, 106.000000, 101.810000, 104.120000, 103.370000, 102.120000, 102.250000, 103.370000,
        107.940000, 112.500000, 115.440000, 115.500000, 112.250000, 107.560000, 106.560000, 106.870000,
        104.500000, 105.750000, 108.620000, 107.750000, 108.060000, 108.000000, 108.190000, 108.120000,
        109.060000, 108.750000, 108.560000, 106.620000,
    ]

    arrays = {'INPUT_CLOSE': INPUT_CLOSE, 'INPUT_HIGH': INPUT_HIGH, 'INPUT_LOW': INPUT_LOW}
    # Example: construct once and feed one HLC bar into each update call.
    indicator = UltimateChannel(length=20, str_length=20, num_strs=1)
    outputs = [indicator.update(close, high, low) for close, high, low in
               zip(INPUT_CLOSE, INPUT_HIGH, INPUT_LOW)]
    print('Default first five named results:')
    for output in outputs[:5]:
        print({field: _float_literal(getattr(output, field), 'NaN') for field in OUTPUT_FIELDS})
    print('Reference cases (generate only after user confirmation):')
    for case in REFERENCE_CASES:
        print(_case_suffix(case), _parameter_comment(case), case.what_it_tests)
    if arguments.generate_reference_data:
        generate_reference_data(arrays, Path(__file__).resolve().parent)
