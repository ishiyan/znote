"""Ehlers' February 2025 autocorrelation heatmap: streaming research master.

Standard library only. Read description.md for complete theory, equations,
source differences, initialization, signed heatmap semantics and port rules.
The default computes Pearson correlations of Ultimate-Smoother prices against
lags 0..99 with a 20-sample window and an independent smoother period of 20.
Full-precision sqrt(2) and pi replace the printed decimal approximations.

__main__ embeds the shared 252 closes. The user confirmed the twelve-case
reference grid on 2026-10-21; generation writes and verifies all five languages.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import math
from pathlib import Path
from typing import NamedTuple


SQRT_TWO = math.sqrt(2.0)


class Heatmap(NamedTuple):
    """One signed correlation column, matching the requested zpano fields.

    values[i] is the correlation at lag parameter_first + i*resolution.
    Values retain their signed scale; there is no power or maximum scaling.
    Each list is independently owned, never reused as recursive state.
    time is optional caller metadata and does not affect calculations.
    """

    time: datetime.datetime | None
    parameter_first: float
    parameter_last: float
    parameter_resolution: float
    value_min: float
    value_max: float
    values: list[float]

    def is_empty(self) -> bool:
        return len(self.values) == 0

    @staticmethod
    def empty(time: datetime.datetime | None, first: float, last: float,
              resolution: float = 1.0) -> Heatmap:
        return Heatmap(time, first, last, resolution, math.nan, math.nan, [])


class AutocorrelationState(NamedTuple):
    """Immutable diagnostics, including state hidden by the public warm-up mask.

    correlations[k] corresponds to the source Corr[k+1], not Corr[k].
    filtered is an Ultimate-Smoother price, not a detrended oscillator.
    """

    accepted_samples: int
    filtered: float
    correlations: tuple[float, ...]


class AutocorrelationHeatmap:
    """Causal Pearson lag map of smoothed prices with source-preserving sums.

    length: integer >=2, default 20; number of pairs per lag.
    smoothing_period: finite real >=1, default 20; independent filter cutoff.
    max_lag: integer 0..99, default 99; inclusive upper lag, minimum is zero.

    The first three accepted prices pass through the Ultimate Smoother.
    Internal correlations update from the beginning with zero prehistory.
    Public columns become available after max(4, length+max_lag) samples:
    enough for every pair in the entire selected lag range to be real history.
    NaN input is skipped without advancing state; infinity is rejected.
    A nonpositive variance retains that lag's previous correlation, initially
    zero. No clipping, mean-subtraction reformulation or variance epsilon is
    inserted into the article's raw-moment Pearson computation.
    """

    def __init__(self, length: int = 20, smoothing_period: float = 20.0,
                 max_lag: int = 99) -> None:
        if isinstance(length, bool) or not isinstance(length, int) or length < 2:
            raise ValueError("length must be an integer of at least 2")
        if isinstance(max_lag, bool) or not isinstance(max_lag, int) or not 0 <= max_lag <= 99:
            raise ValueError("max_lag must be an integer in [0, 99]")
        if isinstance(smoothing_period, bool):
            raise ValueError("smoothing_period must be a finite real number >=1")
        smoothing_period = float(smoothing_period)
        if not math.isfinite(smoothing_period) or smoothing_period < 1.0:
            raise ValueError("smoothing_period must be a finite real number >=1")
        self._length = length
        self._smoothing_period = smoothing_period
        self._max_lag = max_lag
        self._history_length = length + max_lag
        self._prime_count = max(4, self._history_length)

        # Full-precision radian conversion of the EasyLanguage degree formulas.
        # Period is a real divisor, never an integer rolling-window size.
        angle = SQRT_TWO * math.pi / smoothing_period
        a = math.exp(-angle)
        self._c2 = 2.0 * a * math.cos(angle)
        self._c3 = -a * a  # This sign must remain negative in every port.
        self._c1 = (1.0 + self._c2 - self._c3) / 4.0
        self.reset()

    @property
    def length(self) -> int:
        return self._length

    @property
    def smoothing_period(self) -> float:
        return self._smoothing_period

    @property
    def max_lag(self) -> int:
        return self._max_lag

    @property
    def primed(self) -> bool:
        """Sufficient history for all lags; not evidence of market predictability."""
        return self._count >= self._prime_count

    @property
    def warmup_bars(self) -> int:
        """Number of leading empty public columns on a finite input stream."""
        return self._prime_count - 1

    @property
    def state(self) -> AutocorrelationState:
        return AutocorrelationState(self._count, self._filtered1,
                                    tuple(self._correlations))

    def reset(self) -> None:
        """Preserve configuration, restore explicit source initial conditions."""
        self._count = 0
        self._price1 = self._price2 = 0.0
        self._filtered1 = self._filtered2 = 0.0
        self._history = [0.0] * self._history_length  # newest value first
        self._correlations = [0.0] * (self._max_lag + 1)

    def update(self, price: float,
               time: datetime.datetime | None = None) -> Heatmap:
        """Consume one price and return a signed correlation heatmap snapshot."""
        price = float(price)
        if math.isnan(price):
            # Public unavailable value; NEVER introduce NaN into recursive state.
            return Heatmap.empty(time, 0.0, float(self._max_lag))
        if not math.isfinite(price):
            raise ValueError("price must be finite or NaN (missing sample)")

        # CurrentBar=count+1. The first three outputs pass the current price.
        # Ultimate Smoother = input minus the specified second-order highpass;
        # it is not the SuperSmoother supplied as a separate optional tip.
        if self._count < 3:
            filtered = price
        else:
            filtered = ((1.0 - self._c1) * price
                        + (2.0 * self._c1 - self._c2) * self._price1
                        - (self._c1 + self._c3) * self._price2
                        + self._c2 * self._filtered1 + self._c3 * self._filtered2)
        if not math.isfinite(filtered):
            raise ValueError("Ultimate Smoother calculation overflowed")

        # Candidate state keeps rejected arithmetic from partially aging a stream.
        # Only bounded filter history is needed, not the full price record.
        history = [filtered] + self._history[:-1]
        correlations = self._correlations.copy()
        for lag in range(self._max_lag + 1):
            # Reinitialize and sum in precisely the order of the source loops.
            # Reusing rolling moments or centered sums changes floating point
            # results, especially at Length=2 and nearly constant price levels.
            sx = sy = sxx = sxy = syy = 0.0
            for j in range(self._length):
                x = history[j]
                y = history[lag + j]
                sx = sx + x
                sy = sy + y
                sxx = sxx + x * x
                sxy = sxy + x * y
                syy = syy + y * y
            # The factors equal length times the two centered sums of squares.
            # Floating point cancellation may make either nonpositive. The
            # published If has no Else: retain this lag's old value in that case.
            vx = self._length * sxx - sx * sx
            vy = self._length * syy - sy * sy
            if not all(math.isfinite(v) for v in (sx, sy, sxx, sxy, syy, vx, vy)):
                raise ValueError("Pearson sums overflowed; reduce input magnitude")
            if vx > 0.0 and vy > 0.0:
                product = vx * vy
                numerator = self._length * sxy - sx * sy
                if product <= 0.0 or not math.isfinite(product) or not math.isfinite(numerator):
                    raise ValueError("Pearson denominator or numerator overflowed/underflowed")
                correlation = numerator / math.sqrt(product)
                if not math.isfinite(correlation):
                    raise ValueError("Pearson correlation is not finite")
                # Do not force lag zero to 1 or clamp other values to [-1, 1].
                # Those statements are mathematical expectations, not source code.
                correlations[lag] = correlation

        # Commit only after filtering and every Pearson calculation succeeded.
        self._price2, self._price1 = self._price1, price
        self._filtered2, self._filtered1 = self._filtered1, filtered
        self._history, self._correlations = history, correlations
        self._count += 1
        if not self.primed:
            return Heatmap.empty(time, 0.0, float(self._max_lag))
        return Heatmap(time, 0.0, float(self._max_lag), 1.0,
                       min(correlations), max(correlations), correlations.copy())


class ReferenceCase(NamedTuple):
    length: int
    smoothing_period: float
    max_lag: int
    what_it_tests: str


# The user confirmed these twelve combinations and the folder name on 2026-10-21.
REFERENCE_CASES_CONFIRMED = True
REFERENCE_CASES = (
    ReferenceCase(20, 20.0, 99, "Article default and Figure 4: monthly window, all computed lags."),
    ReferenceCase(2, 20.0, 99, "Figure 5: two-point reversal map with independent twenty-bar smoothing."),
    ReferenceCase(3, 20.0, 99, "Small increase from two pairs: temper abrupt correlation reversals."),
    ReferenceCase(5, 20.0, 99, "Short multi-pair window: compare sign saturation with graded correlation."),
    ReferenceCase(40, 20.0, 99, "Longer correlation window: retain two monthly cycles per comparison."),
    ReferenceCase(100, 20.0, 99, "Long history boundary: late whole-column priming within the 252 closes."),
    ReferenceCase(20, 10.0, 99, "Faster Ultimate Smoother: separate cutoff changes from correlation length."),
    ReferenceCase(20, 10.5, 99, "Fractional cutoff: preserve real-valued coefficient calculation."),
    ReferenceCase(20, 40.0, 99, "Slower Ultimate Smoother: sustained filter memory with fixed Pearson length."),
    ReferenceCase(20, 20.0, 32, "Compact lag range: earlier priming and exact common-bin agreement."),
    ReferenceCase(2, 20.0, 32, "Compact reversal map: short history and two-point correlation edge cases."),
    ReferenceCase(20, 20.0, 0, "Zero-lag-only boundary: self-correlation and single-bin heatmap structure."),
)


def _parameter_token(value: float) -> str:
    return format(value, "g").replace(".", "_")


def _case_suffix(case: ReferenceCase) -> str:
    # L=Pearson length, P=Ultimate Smoother period, H=inclusive maximum lag.
    return f"L{case.length}_P{_parameter_token(case.smoothing_period)}_H{case.max_lag}"


def _parameter_comment(case: ReferenceCase) -> str:
    return (f"length={case.length}; smoothing_period={case.smoothing_period}; "
            f"max_lag={case.max_lag}")


def _float_literal(value: float, nan: str) -> str:
    """Round text only; retain full binary64 precision in every calculation."""
    if math.isnan(value):
        return nan
    if not math.isfinite(value):
        raise ValueError("reference values must be finite or NaN")
    literal = format(value, ".15g")
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"  # Rust and Zig require an explicit float literal here.
    return literal


def _array_body(values: list, indent: str, nan: str, language: str) -> str:
    """Serialize scalar series or time-major rectangular heatmap matrices."""
    if values and isinstance(values[0], list):
        opening, closing = {"py": ("[", "]"), "go": ("{", "}"),
                            "ts": ("[", "]"), "rs": ("vec![", "]"),
                            "zig": (".{", "}")}[language]
        return "\n".join(indent + opening + ", ".join(_float_literal(v, nan) for v in row)
                         + closing + "," for row in values)
    tokens = [_float_literal(v, nan) for v in values]
    return "\n".join(indent + ", ".join(tokens[i:i + 6]) + ","
                     for i in range(0, len(tokens), 6))


def _load_python_arrays(path: Path) -> dict[str, list]:
    """Read fixture literals without executing arbitrary source or imports."""
    def decode(node):
        if isinstance(node, ast.List):
            return [decode(child) for child in node.elts]
        if isinstance(node, ast.Name) and node.id == "NaN":
            return math.nan
        return float(ast.literal_eval(node))
    arrays = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    arrays[target.id] = decode(node.value)
    return arrays


def _write_generated_section(path: Path, section: str, comment: str) -> None:
    """Append once; reruns replace only this generator's marked section."""
    begin = f"{comment} BEGIN GENERATED AUTOCORRELATION HEATMAP EXPECTED DATA"
    end = f"{comment} END GENERATED AUTOCORRELATION HEATMAP EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    block = begin + "\n\n" + section.rstrip() + "\n\n" + end
    if begin in original:
        start = original.index(begin)
        finish = original.index(end, start) + len(end)
        result = original[:start] + block + original[finish:]
    else:
        result = original.rstrip() + "\n\n" + block + "\n"
    path.write_text(result, encoding="utf-8")


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write Python expected arrays, verify, then translate the reopened literals."""
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError("reference parameter combinations await user confirmation")
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 inputs and 1..64 reference cases")
    python_path = directory / "test_testdata.py"
    if _load_python_arrays(python_path)["INPUT_CLOSE"] != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from copied fixture")
    arrays = {}
    sections = ["# NaN marks unavailable output, never internal state.\nNaN = math.nan"]
    for case in REFERENCE_CASES:
        indicator = AutocorrelationHeatmap(case.length, case.smoothing_period, case.max_lag)
        results = [indicator.update(price) for price in input_close]
        bins = case.max_lag + 1
        components = {
            "HEATMAP": [r.values if not r.is_empty() else [math.nan] * bins for r in results],
            "MIN": [r.value_min for r in results],
            "MAX": [r.value_max for r in results],
        }
        for component, values in components.items():
            name = "EXPECTED_" + _case_suffix(case) + "_" + component
            if name in arrays:
                raise ValueError("duplicate reference array name")
            arrays[name] = (case, values)
            sections.append(f"# {case.what_it_tests}\n# {_parameter_comment(case)}\n"
                            + f"{name} = [\n{_array_body(values, '    ', 'NaN', 'py')}\n]")
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # Python is the authoritative rounded dataset. All other languages below
    # read these verified values rather than performing independent rounding.
    written = _load_python_arrays(python_path)
    if {name for name in written if name.startswith("EXPECTED_")} != set(arrays):
        raise ValueError("Python expected arrays are missing or unexpected")
    for name, (case, raw) in arrays.items():
        actual = written[name]
        if len(actual) != 252:
            raise ValueError(f"{name} must contain 252 rows")
        matrix = name.endswith("_HEATMAP")
        if matrix and any(len(row) != case.max_lag + 1 for row in actual):
            raise ValueError(f"{name} has incorrect heatmap dimensions")
        raw_flat = [v for row in raw for v in row] if matrix else raw
        flat = [v for row in actual for v in row] if matrix else actual
        for original, literal in zip(raw_flat, flat):
            if math.isnan(original):
                if not math.isnan(literal):
                    raise ValueError(f"{name} has incorrect NaN masks")
            elif literal != float(_float_literal(original, "NaN")):
                raise ValueError(f"{name} has incorrect 15-digit values")

    go_path = directory / "testdata_test.go"
    package = directory.name.replace("-", "").replace("_", "").lower()
    go_text = go_path.read_text(encoding="utf-8").replace("package xxxx", f"package {package}", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace(f"package {package}\n",
                                  f'package {package}\n\nimport "math"\n', 1)
    go_path.write_text(go_text, encoding="utf-8")
    zig_path = directory / "testdata.zig"
    zig_text = zig_path.read_text(encoding="utf-8")
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n' + zig_text
    if "const nan = math.nan(f64);" not in zig_text:
        zig_text = zig_text.replace('const math = @import("std").math;\n',
                                    'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(zig_text, encoding="utf-8")

    translated = {language: [] for language in ("go", "ts", "rs", "zig")}
    for name, (case, _) in arrays.items():
        suffix = name.removeprefix("EXPECTED_")
        values = written[name]
        matrix = name.endswith("_HEATMAP")
        bins = case.max_lag + 1
        comments = f"// {case.what_it_tests}\n// {_parameter_comment(case)}\n"
        go_type = "[][]float64" if matrix else "[]float64"
        ts_type = "number[][]" if matrix else "number[]"
        rs_type = "Vec<Vec<f64>>" if matrix else "Vec<f64>"
        zig_type = f"[252][{bins}]f64" if matrix else "[252]f64"
        translated["go"].append(comments + f"var expected{suffix} = {go_type}{{\n"
                                + _array_body(values, "\t", "math.NaN()", "go") + "\n}")
        translated["ts"].append(comments + f"export const expected{suffix}: {ts_type} = [\n"
                                + _array_body(values, "    ", "NaN", "ts") + "\n];")
        translated["rs"].append(comments + f"pub fn expected_{suffix.lower()}() -> {rs_type} {{\n    vec![\n"
                                + _array_body(values, "        ", "f64::NAN", "rs") + "\n    ]\n}")
        translated["zig"].append(comments + f"pub fn expected{suffix}() {zig_type} {{\n    return .{{\n"
                                 + _array_body(values, "        ", "nan", "zig") + "\n    };\n}")
    for language, filename in (("go", "testdata_test.go"), ("ts", "testdata.ts"),
                               ("rs", "testdata.rs"), ("zig", "testdata.zig")):
        _write_generated_section(directory / filename, "\n\n".join(translated[language]), "//")
    print(f"Verified {len(arrays)} expected arrays for {len(REFERENCE_CASES)} cases in all five languages.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true")
    arguments = parser.parse_args()
    # Identical to the shared 252 INPUT_CLOSE prices; embedded for portability.
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
    example = AutocorrelationHeatmap()
    outputs = [example.update(close) for close in INPUT_CLOSE]
    last = outputs[-1]
    print(f"Default after {len(INPUT_CLOSE)} closes: {len(last.values)} lag bins; "
          f"range=({last.value_min}, {last.value_max}); first 5={last.values[:5]}")
    print(f"Reference grid: {len(REFERENCE_CASES)} combinations; confirmed={REFERENCE_CASES_CONFIRMED}")
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
