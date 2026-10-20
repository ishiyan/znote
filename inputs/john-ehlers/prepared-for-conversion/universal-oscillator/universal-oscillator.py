"""Ehlers' January 2015 Universal Oscillator: streaming research master.

Raw price -> two-bar differencer -> SuperSmoother -> peak-envelope AGC.
The explicit article startup overrides and peak seed are part of the method.
Full-precision sqrt(2) and pi replace printed mathematical approximations;
0.991 and 1e-7 remain the author's chosen algorithmic settings.
"""

from __future__ import annotations

import math


# Fixed source settings, deliberately not additional configuration parameters.
# INITIAL_PEAK is a one-time seed, not a recurring floor on the envelope.
PEAK_DECAY = 0.991
INITIAL_PEAK = 0.0000001


class UniversalOscillator:
    """Consume scalar raw prices and return one dimensionless oscillator.

    band_edge: finite real SuperSmoother critical period >= 2 bars, default 20.
    Fractional periods are valid: the period selects coefficients, not a window.
    The first three accepted finite samples return NaN; bar 4 is visible.
    Missing NaN samples are omitted without shifting history or decaying peak.
    """

    def __init__(self, band_edge: float = 20.0) -> None:
        self._band_edge = float(band_edge)
        if not math.isfinite(self._band_edge) or self._band_edge < 2.0:
            raise ValueError("band_edge must be finite and at least 2 bars")

        # EasyLanguage Cosine uses degrees. Replacing 1.414 by sqrt(2) and
        # converting sqrt(2)*180/B degrees to radians gives sqrt(2)*pi/B.
        # Use the same angle for the exponential and cosine; an extra factor
        # 0.5 (as in the supplied Updata tip) changes the filter's pole angle.
        angle = math.sqrt(2.0) * math.pi / self._band_edge
        a1 = math.exp(-angle)
        self._c2 = 2.0 * a1 * math.cos(angle)
        self._c3 = -a1 * a1
        self._c1 = 1.0 - self._c2 - self._c3
        self.reset()

    @property
    def band_edge(self) -> float:
        """Read-only coefficient setting; use a new object to change it."""
        return self._band_edge

    @property
    def warmup_bars(self) -> int:
        """Three hidden startup values, independent of band_edge."""
        return 3

    @property
    def is_primed(self) -> bool:
        """Output is available after finite bar 4; IIR memory may persist."""
        return self._count >= 4

    def reset(self) -> None:
        """Clear raw history, white-noise history, filter, peak, output, count."""
        self._count = 0
        self._price1 = self._price2 = 0.0
        self._white1 = 0.0
        self._filt1 = self._filt2 = 0.0
        self._peak = 0.0
        self._universal = 0.0

    def update(self, sample: float) -> float:
        """Accept one scalar raw price; return NaN until startup is complete."""
        sample = float(sample)
        if math.isnan(sample):
            # Omit the entire observation. Peak decay measures accepted bars,
            # not calendar time. Do not treat a missing sample as a zero price.
            return math.nan
        if not math.isfinite(sample):
            # Reject before mutating state so a later valid sample can proceed.
            raise ValueError("sample must be finite or NaN")

        # The two-bar difference needs two REAL raw prices. Avoid differencing
        # the initial price against an invented zero-price prehistory.
        # On bar 3 calculate WhiteNoise even though Filt is still forced to 0:
        # bar 4 must use bar 3's WhiteNoise in its two-element input average.
        white = (sample - self._price2) / 2.0 if self._count >= 2 else 0.0

        if self._count < 3:
            # The article overrides Filt after its ordinary calculation on
            # Currentbar 1, 2, 3. With zero Filt seeds all three are exactly 0.
            # This is not ordinary SuperSmoother startup from price-valued seeds.
            filt = 0.0
        else:
            # Keep source operation order, c3 NEGATIVE and ADDED. WhiteNoise
            # already averages two one-bar differences, but the (white+old)/2
            # here is a separate input average in the SuperSmoother recurrence.
            filt = (
                self._c1 * (white + self._white1) / 2.0
                + self._c2 * self._filt1
                + self._c3 * self._filt2
            )

        # The first accepted bar sets Peak=1e-7; every later bar first decays
        # the old envelope, THEN compares the current absolute filter value.
        # Keep the seed and 0.991 literally. Replacing either with a derived
        # constant or dropping the seed changes small-amplitude startup output.
        peak = INITIAL_PEAK if self._count == 0 else PEAK_DECAY * self._peak
        if abs(filt) > peak:
            peak = abs(filt)

        # Exact article conditional: preserve previous Universal on zero Peak.
        # There is no epsilon floor, clip, percentage scaling, or extra smoother.
        # Since peak >= |filt|, this ratio normally remains in [-1,1].
        universal = filt / peak if peak != 0.0 else self._universal

        # Commit histories only after every stage has read the previous states.
        # Hidden startup bars still store white, decay peak, and advance count.
        self._price2, self._price1 = self._price1, sample
        self._white1 = white
        self._filt2, self._filt1 = self._filt1, filt
        self._peak = peak
        self._universal = universal
        self._count += 1
        return universal if self.is_primed else math.nan


# All 12 reference cases were confirmed by the user on 2026-10-20.
REFERENCE_CASES_CONFIRMED = True
INDICATOR_SLUG = 'universal-oscillator'
MASTER_CLASS = UniversalOscillator
PARAMETER_SHORTCUTS = [('band_edge', 'BE')]
REFERENCE_CASES = (
    {'band_edge': 2, 'what_it_tests': 'Minimum supported band edge: two-bar sampling limit and short-period coefficients.'},
    {'band_edge': 4, 'what_it_tests': 'Band edge at the whitening filter maximum-gain four-bar period.'},
    {'band_edge': 5, 'what_it_tests': 'Very short smoothing: sensitivity to rapid price changes.'},
    {'band_edge': 10, 'what_it_tests': 'Book SuperSmoother recommendation: short-cycle smoothing with article whitening.'},
    {'band_edge': 20, 'what_it_tests': 'Article default: short-term universal oscillator.'},
    {'band_edge': 20.5, 'what_it_tests': 'Fractional band edge: real-valued coefficient calculation without integer truncation.'},
    {'band_edge': 30, 'what_it_tests': 'Intermediate smoothing between the default and trend example.'},
    {'band_edge': 50, 'what_it_tests': 'Article trend illustration: suppress cycles shorter than fifty bars.'},
    {'band_edge': 100, 'what_it_tests': 'Long smoothing: persistent recursive memory and reduced short-term variation.'},
    {'band_edge': 150, 'what_it_tests': 'Lower endpoint of the article suggested trend-identification range.'},
    {'band_edge': 200, 'what_it_tests': 'Upper endpoint of the article suggested trend-identification range.'},
    {'band_edge': 252, 'what_it_tests': 'Full-record-length band edge: long transient while output remains available from bar four.'},
)

# Everything below this line is fixture-generation tooling. Port the indicator
# class above; these file-formatting helpers are optional.
from pathlib import Path
import argparse
import ast


def _read_arrays(path: Path) -> dict[str, list[float]]:
    """Load numeric list assignments safely, including explicit math.nan."""
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


def _parameter_token(value: float | int | bool) -> str:
    """10.0 -> 10; 10.5 -> 10_5; booleans -> 0/1. All tokens are identifiers."""
    return format(float(value), "g").replace(".", "_").replace("-", "m")


def _case_suffix(case: dict) -> str:
    # Case parameter order is fixed by the declared shortcut order, not sorted
    # alphabetically. That makes Python/Go/TS/Rust/Zig names easy to correlate.
    return "_".join(shortcut + _parameter_token(case[parameter])
                    for parameter, shortcut in PARAMETER_SHORTCUTS)


def _parameters(case: dict) -> dict:
    return {parameter: case[parameter] for parameter, _ in PARAMETER_SHORTCUTS}


def _parameter_comment(case: dict) -> str:
    return ", ".join(f"{parameter}={case[parameter]}" for parameter, _ in PARAMETER_SHORTCUTS)


def _literal(value: float, nan_literal: str) -> str:
    """Round only at serialization, to 15 significant decimal digits."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("infinite reference output cannot be serialized")
    literal = format(value, ".15g")
    # Rust and Zig arrays of f64 need float literals even for integral values.
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _rows(values: list[float], indent: str, nan_literal: str) -> str:
    literals = [_literal(value, nan_literal) for value in values]
    return "\n".join(indent + ", ".join(literals[index:index + 6]) + ","
                     for index in range(0, len(literals), 6))


def _replace_generated_section(path: Path, body: str, comment: str) -> None:
    """Append on first run; replace just the marked outputs on later runs."""
    begin = f"{comment} BEGIN GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA"
    end = f"{comment} END GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    section = begin + "\n\n" + body.rstrip() + "\n\n" + end
    if begin in original:
        start = original.index(begin)
        # A missing end marker raises instead of silently deleting file content.
        finish = original.index(end, start) + len(end)
        result = original[:start] + section + original[finish:]
    else:
        result = original.rstrip() + "\n\n" + section + "\n"
    path.write_text(result, encoding="utf-8")


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write Python first, verify it, then copy its decimal values to ports.

    No other-language implementation calculates or rounds expected data. Every
    expected array has the same 252 positions, NaN mask, and 15-digit literals.
    """
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError("reference cases must be confirmed before generation")
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("require 252 closes and between 1 and 64 confirmed cases")
    python_path = directory / "test_testdata.py"
    if _read_arrays(python_path)["INPUT_CLOSE"] != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from the copied fixture")

    raw_arrays = {}
    sections = []
    for case in REFERENCE_CASES:
        indicator = MASTER_CLASS(**_parameters(case))
        values = [indicator.update(sample) for sample in input_close]
        warmup = indicator.warmup_bars
        if not all(math.isnan(value) for value in values[:warmup]):
            raise ValueError("incorrect NaN prefix")
        if not all(math.isfinite(value) for value in values[warmup:]):
            raise ValueError("unexpected missing or infinite output after priming")
        name = "EXPECTED_" + _case_suffix(case)
        if name in raw_arrays:
            raise ValueError("duplicate reference case")
        raw_arrays[name] = values
        sections.append(
            f"# {case['what_it_tests']}\n# {_parameter_comment(case)}\n"
            f"{name} = [\n{_rows(values, '    ', 'math.nan')}\n]"
        )
    _replace_generated_section(python_path, "\n\n".join(sections), "#")

    # Verify the actual file, not just the in-memory arrays. Comparing each
    # parsed float with the correctly rounded original catches misplaced NaNs,
    # truncated arrays, and accidental extra rounding before propagation.
    written = _read_arrays(python_path)
    if {name for name in written if name.startswith("EXPECTED_")} != set(raw_arrays):
        raise ValueError("missing or unexpected expected arrays in Python")
    for name, raw in raw_arrays.items():
        if len(written[name]) != 252:
            raise ValueError(f"{name} must contain 252 values")
        for original, saved in zip(raw, written[name]):
            if math.isnan(original) and math.isnan(saved):
                continue
            if saved != float(_literal(original, "math.nan")):
                raise ValueError(f"{name} does not preserve 15-digit precision")

    other_sections = {filename: [] for filename in (
        "testdata_test.go", "testdata.ts", "testdata.rs", "testdata.zig"
    )}
    for case in REFERENCE_CASES:
        suffix = _case_suffix(case)
        values = written["EXPECTED_" + suffix]
        comments = f"// {case['what_it_tests']}\n// {_parameter_comment(case)}\n"
        other_sections["testdata_test.go"].append(
            comments + f"var expected{suffix} = []float64{{\n"
            + _rows(values, "\t", "math.NaN()") + "\n}"
        )
        other_sections["testdata.ts"].append(
            comments + f"export const expected{suffix}: number[] = [\n"
            + _rows(values, "    ", "NaN") + "\n];"
        )
        other_sections["testdata.rs"].append(
            comments + f"pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n"
            + _rows(values, "        ", "f64::NAN") + "\n    ]\n}"
        )
        other_sections["testdata.zig"].append(
            comments + f"pub fn expected{suffix}() [252]f64 {{\n    return .{{\n"
            + _rows(values, "        ", "nan") + "\n    };\n}"
        )
    for filename, sections in other_sections.items():
        _replace_generated_section(directory / filename, "\n\n".join(sections), "//")
    print(f"Verified {len(raw_arrays)} arrays of 252 values; wrote Python, Go, TypeScript, Rust, Zig.")


def _run_main(input_close: list[float]) -> None:
    """A runnable example plus the confirmed reference-data generation CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true",
                        help="write all confirmed expected arrays in the five fixture files")
    arguments = parser.parse_args()
    if arguments.generate_reference_data:
        generate_reference_data(input_close, Path(__file__).resolve().parent)
    else:
        # Demonstrate normal streaming without overwriting fixture files.
        indicator = MASTER_CLASS()
        outputs = [indicator.update(sample) for sample in input_close]
        first = next(index for index, value in enumerate(outputs) if math.isfinite(value))
        print(f"{INDICATOR_SLUG}: {len(outputs)} closes; first valid output on bar {first + 1}")
        print("First five valid outputs:", [_literal(value, "NaN") for value in outputs[first:first + 5]])
        print(f"{len(REFERENCE_CASES)} parameter cases confirmed; use --generate-reference-data to regenerate.")



if __name__ == "__main__":
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
    _run_main(INPUT_CLOSE)
