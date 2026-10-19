"""December 2021 Directional Movement using Hann Windowing (DMH).

Standard-library streaming research master of the article/Mesa/TradeStation
equations. See description.md for theory, startup and platform differences.

DMH requires High and Low, not Close. update(high, low) returns one float in
price units. Equal competing movements are discarded. The signed movement
is smoothed with a zero-seeded EMA using alpha=1/Length, then a normalized
Length-tap interior Hann FIR. No ATR or directional-movement ratio is used.

The first bar establishes previous High/Low but creates no EMA observation.
The first Length outputs are NaN; index Length has the first complete FIR.
NaNs are availability markers and NEVER enter the EMA or FIR state.

Run without flags for an example using the embedded 252 aligned price bars.
--generate-reference-data regenerates the twelve confirmed cases in all five
fixtures. The case table and output format are documented in description.md.
The streaming class does no file I/O and uses no third-party packages.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple

OUTPUT_FIELDS = ('dmh',)


class DirectionalMovementHannState(NamedTuple):
    """Read-only diagnostics; unavailable movements/output are NaN.

    The initial EMA is zero, as declared in the primary source. On the first
    bar no movement can be computed. Thereafter EMA is available even while
    the complete Hann window is still being collected.
    """

    upper_move: float
    lower_move: float
    plus_dm: float
    minus_dm: float
    ema: float
    dmh: float


class DirectionalMovementHann:
    """Winner-selected high/low movement -> EMA -> normalized Hann FIR.

    length is a positive integer, default 14; booleans are not lengths.
    Each call consumes one chronological, completed bar. Input prices must
    be finite with high >= low; zero/negative prices are otherwise accepted.
    Return NaN during history collection, and a scalar DMH once primed.

    A bounded newest-first list holds the last length EMA observations.
    Work per update and persistent memory are O(length). This simple layout
    makes the source's EMA[count-1] indexing explicit for future ports.
    """

    def __init__(self, length: int = 14) -> None:
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError('length must be a positive integer')
        self._length = length
        # Source SF=1/Length, NOT a conventional EMA's 2/(Length+1).
        # The numerator must be floating-point in languages with int division.
        self._sf = 1.0 / length
        self._retention = 1.0 - self._sf
        self._weights, self._coefficient = self._kernel(length)
        self.reset()

    @staticmethod
    def _kernel(length: int) -> tuple[list[float], float]:
        """Preserve inclusive source count=1..Length and sequential sum."""
        weights = []
        coefficient = 0.0
        for count in range(1, length + 1):
            # EasyLanguage Cosine takes DEGREES; Python cos takes radians.
            # Use full math.pi, not a rounded 3.14159 or 6.28 approximation.
            # Denominator Length+1 samples the INTERIOR of a Hann window:
            # both stored endpoint taps are positive, unlike library hanning.
            weight = 1.0 - math.cos(math.radians(360.0 * count / (length + 1)))
            weights.append(weight)
            coefficient = coefficient + weight
        # In exact arithmetic coefficient=Length+1. Retain the source's sum
        # to preserve binary64 arithmetic instead of replacing it with N+1.
        return weights, coefficient

    @property
    def length(self) -> int:
        """Read-only source parameter; construct a new instance to change it."""
        return self._length

    @property
    def warmup_bars(self) -> int:
        """Number of unavailable returned bars: one setup bar plus N-1."""
        return self._length

    @property
    def is_primed(self) -> bool:
        """Complete EMA history exists; this does not imply a settled EMA."""
        return len(self._emas) == self._length

    @property
    def state(self) -> DirectionalMovementHannState:
        """Latest diagnostics without exposing mutable internal histories."""
        return self._state

    def reset(self) -> None:
        """Discard all bars and restore the primary source's EMA(0) seed."""
        self._previous_high = None
        self._previous_low = None
        self._ema = 0.0
        self._emas = []
        self._state = DirectionalMovementHannState(
            math.nan, math.nan, math.nan, math.nan, 0.0, math.nan)

    def update(self, high: float, low: float) -> float:
        """Consume one High/Low pair; reject invalid bars before committing.

        There is no resampling, missing-bar filling, or intrabar replacement.
        A caller wishing to recompute history must reset and replay the bars.
        Invalid/nonfinite prices and arithmetic overflow leave state intact.
        """
        high = float(high)
        low = float(low)
        if not math.isfinite(high) or not math.isfinite(low):
            raise ValueError('high and low must be finite')
        if high < low:
            raise ValueError('high must be greater than or equal to low')

        if self._previous_high is None:
            # No actual High[1]/Low[1] exists. Establish the preceding bar,
            # but do not invent a zero-price bar or count a synthetic EMA tap.
            self._previous_high = high
            self._previous_low = low
            return math.nan

        # Positive upper movement means a higher high. Positive lower
        # movement means a lower low, hence the REVERSED subtraction order.
        upper_move = high - self._previous_high
        lower_move = self._previous_low - low
        if not math.isfinite(upper_move) or not math.isfinite(lower_move):
            raise ValueError('directional price differences must be finite')

        # Clear both directions on EVERY bar. At most one wins; a positive
        # tie is discarded, as is an inside bar or a nonpositive movement.
        plus_dm = 0.0
        minus_dm = 0.0
        if upper_move > lower_move and upper_move > 0.0:
            plus_dm = upper_move
        elif lower_move > upper_move and lower_move > 0.0:
            minus_dm = lower_move

        # Preserve the source order. Do not SMA-seed, sum without alpha,
        # normalize by ATR, or substitute a library EMA/RMA initialization.
        ema = self._sf * (plus_dm - minus_dm) + self._retention * self._ema
        if not math.isfinite(ema):
            raise ValueError('EMA must be finite')

        # Build the prospective bounded window before changing persistent
        # state, so a rejected arithmetic overflow cannot corrupt the stream.
        # Index 0 is current EMA, index 1 is EMA[1], etc., exactly as in source.
        emas = [ema] + self._emas[:self._length - 1]
        dmh = math.nan
        if len(emas) == self._length:
            total = 0.0
            for lag, weight in enumerate(self._weights):
                total = total + weight * emas[lag]
            if not math.isfinite(total):
                raise ValueError('Hann weighted sum must be finite')
            # With a positive integer length the Hann coefficient cannot be
            # zero. Keep the source's normalization guard explicit for ports.
            dmh = total / self._coefficient if self._coefficient != 0.0 else 0.0
            if not math.isfinite(dmh):
                raise ValueError('DMH output must be finite')

        # Commit all accepted-bar state together. Output NaN only masks
        # unavailable history; it never contaminates the recursive EMA.
        self._previous_high = high
        self._previous_low = low
        self._ema = ema
        self._emas = emas
        self._state = DirectionalMovementHannState(
            upper_move, lower_move, plus_dm, minus_dm, ema, dmh)
        return dmh


class ReferenceCase(NamedTuple):
    """A confirmed Length and the exact portable 'What it tests' comment."""

    length: int
    what_it_tests: str


# All twelve cases were confirmed by the user on 2026-10-19.
REFERENCE_CASES = (
    ReferenceCase(14, 'Article, Mesa and TradeStation default.'),
    ReferenceCase(1, 'Minimum length; raw signed movement after the setup bar.'),
    ReferenceCase(2, 'Smallest smoothing kernel; equal two-tap Hann weights.'),
    ReferenceCase(3, 'Short odd-length symmetric Hann kernel.'),
    ReferenceCase(5, 'Fast response to directional movement spikes.'),
    ReferenceCase(8, 'Short even-length smoothing window.'),
    ReferenceCase(10, 'TradingView default length with primary-source EMA seeding.'),
    ReferenceCase(20, 'Slower response over a monthly-scale window.'),
    ReferenceCase(30, 'Longer smoothing and EMA startup transient.'),
    ReferenceCase(126, 'Half-record Hann window and extended warmup.'),
    ReferenceCase(251, 'Maximum length with one primed value in the 252-bar record.'),
    ReferenceCase(252, 'Insufficient movement history; all 252 outputs are NaN.'),
)


def _case_suffix(case: ReferenceCase) -> str:
    return f'L{case.length}'


def _parameter_comment(case: ReferenceCase) -> str:
    return f'length={case.length}'


def _expected_name(case: ReferenceCase, field: str) -> str:
    return 'EXPECTED_' + _case_suffix(case)


def generate_reference_data(input_close: list[float], input_high: list[float],
                            input_low: list[float], directory: Path) -> None:
    """Write Python reference arrays, verify them, then translate their values.

    All generation is binary64 with rounding only during text emission. Each
    rerun replaces its own marked section and preserves the copied input data.
    Rendering helpers and file I/O are tooling; only the indicator is ported.
    """
    if any(len(v) != 252 for v in (input_close, input_high, input_low)) or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError('expected 252 aligned Close/High/Low bars and 1 to 64 cases')
    python_path = directory / 'test_testdata.py'
    copied = _load_literal_arrays(python_path)
    for name, values in (('INPUT_CLOSE', input_close), ('INPUT_HIGH', input_high), ('INPUT_LOW', input_low)):
        if copied[name] != values:
            raise ValueError(f'embedded {name} differs from the copied fixture')
    raw_outputs = {}
    sections = []
    for case in REFERENCE_CASES:
        # Only the source Length varies. Close identifies the shared data
        # record but the actual directional-movement inputs are High and Low.
        indicator = DirectionalMovementHann(case.length)
        outputs = [indicator.update(high, low) for high, low in zip(input_high, input_low)]
        for field in OUTPUT_FIELDS:
            values = outputs if len(OUTPUT_FIELDS) == 1 else [getattr(v, field) for v in outputs]
            name = _expected_name(case, field)
            raw_outputs[name] = (values, indicator.warmup_bars)
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
    text = go_path.read_text().replace('package xxxx', 'package directionalmovementhann', 1)
    if 'import "math"' not in text:
        preamble = 'package directionalmovementhann\n\nimport "math"\n'
        if not any(math.isnan(v) for name in raw_outputs for v in written[name]):
            # Go rejects unused imports. Keep the requested NaN helper import
            # without inserting artificial NaNs into defined startup outputs.
            preamble += '\n// Keep the NaN helper available; startup outputs are defined.\nvar _ = math.NaN\n'
        text = text.replace('package directionalmovementhann\n', preamble, 1)
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
    begin = f"{comment} BEGIN GENERATED DIRECTIONAL MOVEMENT HANN EXPECTED DATA"
    end = f"{comment} END GENERATED DIRECTIONAL MOVEMENT HANN EXPECTED DATA"
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
                        help='regenerate the twelve confirmed reference cases')
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

    INPUT_HIGH = [
        93.250000, 94.940000, 96.375000, 96.190000, 96.000000, 94.720000, 95.000000, 93.720000, 92.470000, 92.750000,
        96.250000, 99.625000, 99.125000, 92.750000, 91.315000, 93.250000, 93.405000, 90.655000, 91.970000, 92.250000,
        90.345000, 88.500000, 88.250000, 85.500000, 84.440000, 84.750000, 84.440000, 89.405000, 88.125000, 89.125000,
        87.155000, 87.250000, 87.375000, 88.970000, 90.000000, 89.845000, 86.970000, 85.940000, 84.750000, 85.470000,
        84.470000, 88.500000, 89.470000, 90.000000, 92.440000, 91.440000, 92.970000, 91.720000, 91.155000, 91.750000,
        90.000000, 88.875000, 89.000000, 85.250000, 83.815000, 85.250000, 86.625000, 87.940000, 89.375000, 90.625000,
        90.750000, 88.845000, 91.970000, 93.375000, 93.815000, 94.030000, 94.030000, 91.815000, 92.000000, 91.940000,
        89.750000, 88.750000, 86.155000, 84.875000, 85.940000, 99.375000, 103.280000, 105.375000, 107.625000, 105.250000,
        104.500000, 105.500000, 106.125000, 107.940000, 106.250000, 107.000000, 108.750000, 110.940000, 110.940000, 114.220000,
        123.000000, 121.750000, 119.815000, 120.315000, 119.375000, 118.190000, 116.690000, 115.345000, 113.000000, 118.315000,
        116.870000, 116.750000, 113.870000, 114.620000, 115.310000, 116.000000, 121.690000, 119.870000, 120.870000, 116.750000,
        116.500000, 116.000000, 118.310000, 121.500000, 122.000000, 121.440000, 125.750000, 127.750000, 124.190000, 124.440000,
        125.750000, 124.690000, 125.310000, 132.000000, 131.310000, 132.250000, 133.880000, 133.500000, 135.500000, 137.440000,
        138.690000, 139.190000, 138.500000, 138.130000, 137.500000, 138.880000, 132.130000, 129.750000, 128.500000, 125.440000,
        125.120000, 126.500000, 128.690000, 126.620000, 126.690000, 126.000000, 123.120000, 121.870000, 124.000000, 127.000000,
        124.440000, 122.500000, 123.750000, 123.810000, 124.500000, 127.870000, 128.560000, 129.630000, 124.870000, 124.370000,
        124.870000, 123.620000, 124.060000, 125.870000, 125.190000, 125.620000, 126.000000, 128.500000, 126.750000, 129.750000,
        132.690000, 133.940000, 136.500000, 137.690000, 135.560000, 133.560000, 135.000000, 132.380000, 131.440000, 130.880000,
        129.630000, 127.250000, 127.810000, 125.000000, 126.810000, 124.750000, 122.810000, 122.250000, 121.060000, 120.000000,
        123.250000, 122.750000, 119.190000, 115.060000, 116.690000, 114.870000, 110.870000, 107.250000, 108.870000, 109.000000,
        108.500000, 113.060000, 93.000000, 94.620000, 95.120000, 96.000000, 95.560000, 95.310000, 99.000000, 98.810000,
        96.810000, 95.940000, 94.440000, 92.940000, 93.940000, 95.500000, 97.060000, 97.500000, 96.250000, 96.370000,
        95.000000, 94.870000, 98.250000, 105.120000, 108.440000, 109.870000, 105.000000, 106.000000, 104.940000, 104.500000,
        104.440000, 106.310000, 112.870000, 116.500000, 119.190000, 121.000000, 122.120000, 111.940000, 112.750000, 110.190000,
        107.940000, 109.690000, 111.060000, 110.440000, 110.120000, 110.310000, 110.440000, 110.000000, 110.750000, 110.500000,
        110.500000, 109.500000,
    ]

    INPUT_LOW = [
        90.750000, 91.405000, 94.250000, 93.500000, 92.815000, 93.500000, 92.000000, 89.750000, 89.440000, 90.625000,
        92.750000, 96.315000, 96.030000, 88.815000, 86.750000, 90.940000, 88.905000, 88.780000, 89.250000, 89.750000,
        87.500000, 86.530000, 84.625000, 82.280000, 81.565000, 80.875000, 81.250000, 84.065000, 85.595000, 85.970000,
        84.405000, 85.095000, 85.500000, 85.530000, 87.875000, 86.565000, 84.655000, 83.250000, 82.565000, 83.440000,
        82.530000, 85.065000, 86.875000, 88.530000, 89.280000, 90.125000, 90.750000, 89.000000, 88.565000, 90.095000,
        89.000000, 86.470000, 84.000000, 83.315000, 82.000000, 83.250000, 84.750000, 85.280000, 87.190000, 88.440000,
        88.250000, 87.345000, 89.280000, 91.095000, 89.530000, 91.155000, 92.000000, 90.530000, 89.970000, 88.815000,
        86.750000, 85.065000, 82.030000, 81.500000, 82.565000, 96.345000, 96.470000, 101.155000, 104.250000, 101.750000,
        101.720000, 101.720000, 103.155000, 105.690000, 103.655000, 104.000000, 105.530000, 108.530000, 108.750000, 107.750000,
        117.000000, 118.000000, 116.000000, 118.500000, 116.530000, 116.250000, 114.595000, 110.875000, 110.500000, 110.720000,
        112.620000, 114.190000, 111.190000, 109.440000, 111.560000, 112.440000, 117.500000, 116.060000, 116.560000, 113.310000,
        112.560000, 114.000000, 114.750000, 118.870000, 119.000000, 119.750000, 122.620000, 123.000000, 121.750000, 121.560000,
        123.120000, 122.190000, 122.750000, 124.370000, 128.000000, 129.500000, 130.810000, 130.630000, 132.130000, 133.880000,
        135.380000, 135.750000, 136.190000, 134.500000, 135.380000, 133.690000, 126.060000, 126.870000, 123.500000, 122.620000,
        122.750000, 123.560000, 125.810000, 124.620000, 124.370000, 121.810000, 118.190000, 118.060000, 117.560000, 121.000000,
        121.120000, 118.940000, 119.810000, 121.000000, 122.000000, 124.500000, 126.560000, 123.500000, 121.250000, 121.060000,
        122.310000, 121.000000, 120.870000, 122.060000, 122.750000, 122.690000, 122.870000, 125.500000, 124.250000, 128.000000,
        128.380000, 130.690000, 131.630000, 134.380000, 132.000000, 131.940000, 131.940000, 129.560000, 123.750000, 126.000000,
        126.250000, 124.370000, 121.440000, 120.440000, 121.370000, 121.690000, 120.000000, 119.620000, 115.500000, 116.750000,
        119.060000, 119.060000, 115.060000, 111.060000, 113.120000, 110.000000, 105.000000, 104.690000, 103.870000, 104.690000,
        105.440000, 107.000000, 89.000000, 92.500000, 92.120000, 94.620000, 92.810000, 94.250000, 96.250000, 96.370000,
        93.690000, 93.500000, 90.000000, 90.190000, 90.500000, 92.120000, 94.120000, 94.870000, 93.000000, 93.870000,
        93.000000, 92.620000, 93.560000, 98.370000, 104.440000, 106.000000, 101.810000, 104.120000, 103.370000, 102.120000,
        102.250000, 103.370000, 107.940000, 112.500000, 115.440000, 115.500000, 112.250000, 107.560000, 106.560000, 106.870000,
        104.500000, 105.750000, 108.620000, 107.750000, 108.060000, 108.000000, 108.190000, 108.120000, 109.060000, 108.750000,
        108.560000, 106.620000,
    ]

    # Close is retained verbatim as requested, but cannot replace High/Low.
    # Each output index refers to the same bar in all three 252-value arrays.
    indicator = DirectionalMovementHann(length=14)
    outputs = [indicator.update(high, low) for high, low in zip(INPUT_HIGH, INPUT_LOW)]
    print('Default first five primed values (indices 14-18):', ', '.join(
        _float_literal(value, 'NaN') for value in outputs[14:19]))
    print('Confirmed reference cases:')
    for case in REFERENCE_CASES:
        print(f'  {_case_suffix(case)}: {case.what_it_tests}')
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, INPUT_HIGH, INPUT_LOW, Path(__file__).resolve().parent)
