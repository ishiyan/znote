"""Projected Moving Average: self-contained streaming research master.

Source: Ehlers' March 2025 Removing Moving Average Lag article and matching
TradeStation code. Returns PMA, slope, PMA prediction, slope prediction, SMA.
Uses the author's literal Length/2 projection rather than a regression-endpoint
substitute. See description.md for its half-bar distinction and exact warmups.

Standard Python only. Run without flags for a 252-close streaming example.
After confirming the listed Length cases, --generate-reference-data writes
Python expected arrays, verifies them, then translates them into four languages.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


class PMAResult(NamedTuple):
    """Five explicitly named outputs; each field has its own priming rule."""

    pma: float
    slope: float
    prediction: float
    slope_prediction: float
    sma: float


class ProjectedMovingAverage:
    """Window regression slope projected across Length/2 from the mean.

    length is an integer >= 2, default 20. A one-sample regression has zero
    denominator and is rejected. Fractional windows are not truncated.
    PMA, slope, SMA need length prices; prediction needs two additional bars;
    slope_prediction needs four additional bars. Missing fields return NaN.
    """

    def __init__(self, length: int = 20) -> None:
        if isinstance(length, bool) or not isinstance(length, int) or length < 2:
            raise ValueError('length must be an integer of at least 2')
        self._length = length
        self.reset()

    @property
    def length(self) -> int:
        """Read-only window; construct a fresh instance to change Length."""
        return self._length

    @property
    def warmup_bars(self) -> int:
        """Leading NaNs in the core PMA, slope, and SMA fields."""
        return self._length - 1

    @property
    def prediction_warmup_bars(self) -> int:
        """PMA prediction needs a valid slope from two bars earlier."""
        return self._length + 1

    @property
    def slope_prediction_warmup_bars(self) -> int:
        """Slope prediction needs a valid slope from four bars earlier."""
        return self._length + 3

    @property
    def is_primed(self) -> bool:
        """True once the core PMA/slope/SMA fields have a full price window."""
        return len(self._prices) == self._length

    @property
    def is_prediction_primed(self) -> bool:
        return self._valid_slopes >= 3

    @property
    def is_slope_prediction_primed(self) -> bool:
        return self._valid_slopes >= 5

    def reset(self) -> None:
        """Clear price ring, historical valid slopes, and all priming state."""
        self._prices = []
        self._next = 0
        self._slopes = []
        self._valid_slopes = 0

    def update(self, price: float) -> PMAResult:
        """Consume one chronological finite price and return this bar's fields."""
        price = float(price)
        if not math.isfinite(price):
            # Reject missing/infinite observations before changing either ring.
            raise ValueError('price must be finite')

        # Grow the raw-price ring until full, then replace exactly the oldest
        # observation. No implicit prior prices or partial-window regression.
        if len(self._prices) < self._length:
            self._prices.append(price)
            self._next = len(self._prices) % self._length
        else:
            self._prices[self._next] = price
            self._next = (self._next + 1) % self._length
        if not self.is_primed:
            return PMAResult(math.nan, math.nan, math.nan, math.nan, math.nan)

        # Match the original loop exactly: count runs from ONE to Length,
        # inclusive, with count=1 reading TODAY's price. Older prices have
        # larger time coordinates, so the computed regression slope's sign
        # must be reversed to express a chronological price rise as positive.
        sx = sy = sxx = syy = sxy = 0.0
        for count in range(1, self._length + 1):
            index = (self._next - count) % self._length
            observed = self._prices[index]
            sx = sx + count
            sy = sy + observed
            sxx = sxx + count * count
            # Syy is accumulated in the article even though its value is not
            # used by slope, SMA, or PMA. It is not a variance or extra output.
            syy = syy + observed * observed
            sxy = sxy + count * observed

        # Preserve raw covariance and denominator expressions and operation
        # order. A centered fit, np.polyfit, precomputed weighted sum or rolling
        # moments can be equivalent algebraically but differ in binary64 bits.
        numerator = self._length * sxy - sx * sy
        denominator = self._length * sxx - sx * sx
        slope = -numerator / denominator
        sma = sy / self._length

        # Literal source: PMA = SMA + Slope*Length/2. Do not substitute
        # (Length-1)/2, which gives a fitted current-bar regression endpoint.
        # The source projects an extra half bar relative to that endpoint.
        pma = sma + slope * self._length / 2.0

        # Read PRIOR slopes before appending today's value. A history of two
        # valid slopes gives slope[t-2]; four gives slope[t-4]. A bar lag is
        # not a lag of two or four raw prices or two/four updates of this call.
        if len(self._slopes) >= 2:
            prediction = pma + 0.5 * (slope - self._slopes[-2]) * self._length
        else:
            prediction = math.nan
        if len(self._slopes) >= 4:
            slope_prediction = 1.5 * slope - 0.5 * self._slopes[-4]
        else:
            slope_prediction = math.nan

        # Do not store unavailable NaNs as valid slope history. Once a complete
        # regression window exists, a new valid slope is calculated every bar.
        self._slopes.append(slope)
        if len(self._slopes) > 4:
            del self._slopes[0]
        self._valid_slopes += 1
        return PMAResult(pma, slope, prediction, slope_prediction, sma)


class ReferenceCase(NamedTuple):
    """One confirmed integer window and its exact What-it-tests comment."""

    length: int
    what_it_tests: str


REFERENCE_CASES = (
    ReferenceCase(2, 'Minimum nonsingular regression: two prices and distinctly staged prediction warmups.'),
    ReferenceCase(3, 'Short odd window: positive chronological slope from backwards time indices.'),
    ReferenceCase(4, 'Short even window: preserve the literal half-length projection.'),
    ReferenceCase(5, 'Short odd window: two-bar and four-bar historical slope access.'),
    ReferenceCase(8, 'Moderate short window: repeated price-ring and slope-history wraparound.'),
    ReferenceCase(14, 'Fourteen-bar window: intermediate responsiveness and regression smoothing.'),
    ReferenceCase(20, 'Article and TradeStation default: twenty-bar PMA with both prediction streams.'),
    ReferenceCase(30, 'Article chart and Python tip example: thirty-bar projected moving average.'),
    ReferenceCase(60, 'Longer intermediate window: broader regression horizon without recursive state.'),
    ReferenceCase(100, 'One-hundred-bar window: longer warmup and raw covariance accumulation.'),
    ReferenceCase(200, 'Article long-term example: two-hundred-day SMA and PMA comparison.'),
    ReferenceCase(252, 'Full-record window: only the final core values are primed; both predictions remain NaN.'),
)


OUTPUT_FIELDS = ('pma', 'slope', 'prediction', 'slope_prediction', 'sma')
OUTPUT_TOKENS = ('PMA', 'SLOPE', 'PREDICTION', 'SLOPE_PREDICTION', 'SMA')


def _case_suffix(case: ReferenceCase) -> str:
    return f'L{case.length}'


def _parameter_comment(case: ReferenceCase) -> str:
    return f'length={case.length}'


def _run_case(case: ReferenceCase, arrays: dict[str, list[float]]) -> list[PMAResult]:
    indicator = ProjectedMovingAverage(case.length)
    return [indicator.update(price) for price in arrays['INPUT_CLOSE']]


REQUIRED_INPUTS = ('INPUT_CLOSE',)


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
    begin = f"{comment} BEGIN GENERATED PROJECTED MOVING AVERAGE EXPECTED DATA"
    end = f"{comment} END GENERATED PROJECTED MOVING AVERAGE EXPECTED DATA"
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
    case produces FIVE scalar arrays, one for each named result field. The
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
                        help='regenerate the approved reference cases in five languages')
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

    arrays = {'INPUT_CLOSE': INPUT_CLOSE}
    # Example: construct once, then feed all 252 prices one observed bar at a
    # time. Result fields become available on their own documented schedules.
    indicator = ProjectedMovingAverage(length=20)
    outputs = [indicator.update(price) for price in INPUT_CLOSE]
    print('Default first result with all five fields primed (index 23):')
    print({field: _float_literal(getattr(outputs[23], field), 'NaN') for field in OUTPUT_FIELDS})
    print('Reference parameter cases:')
    for case in REFERENCE_CASES:
        print(_case_suffix(case), _parameter_comment(case), case.what_it_tests)
    if arguments.generate_reference_data:
        generate_reference_data(arrays, Path(__file__).resolve().parent)
