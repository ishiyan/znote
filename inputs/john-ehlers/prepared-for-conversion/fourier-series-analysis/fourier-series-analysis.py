"""Ehlers Fourier series analysis, TASC June 2019.

Research prototype master reference; Python standard library only.
Three recursive band-pass filters -> one-bar quadrature differences ->
Fundamental-bar powers -> relatively weighted Wave -> optional two-bar ROC.
The sole configurable source input is integer Fundamental, default 20.
Bandwidth stays at the article's 0.1. All angles use full-precision math.pi;
6.28 and 12.57 are replaced by 2*pi and 4*pi, respectively.

update returns FourierSeriesOutput(wave, roc). Internal source computations
continue during startup; public NaNs are never fed into the recursions.
One-based source bars 1..3 force BP=0, and bars 1..4 force Q=0.
Wave first becomes public at zero-based index F-1; ROC at F+1.
The source uses F/(2*pi) for ALL three quadrature components. Preserve this.

__main__ embeds the original 252 closes. Run without arguments for an example
and the confirmed case table. The user confirmed all twenty parameter cases
on 2026-10-20. --generate-reference-data regenerates all five fixture formats.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# EasyLanguage cosine takes degrees. Python cosine takes radians. Do not port
# the article's rounded 6.28/12.57 constants into another language.
TWO_PI = 2.0 * math.pi
FOUR_PI = 4.0 * math.pi
BANDWIDTH = 0.1  # A fixed design coefficient, not an approximation to a constant.


class FourierSeriesOutput(NamedTuple):
    """Public values in price units; unavailable components are NaN."""
    wave: float
    roc: float


class HarmonicCoefficients(NamedTuple):
    """Article L, G, S for one harmonic; useful for independent port checks."""
    l: float
    g: float
    s: float


class FourierSeriesState(NamedTuple):
    """Latest source diagnostics, ordered fundamental, second, third harmonic.

    band_pass, quadrature, power, internal_wave and internal_roc are finite
    source state, including while public output is masked. reset restores zeros.
    output is the same named tuple returned by the latest accepted update.
    """
    band_pass: tuple[float, float, float]
    quadrature: tuple[float, float, float]
    power: tuple[float, float, float]
    internal_wave: float
    internal_roc: float
    output: FourierSeriesOutput


class FourierSeriesAnalysis:
    """Causal, fixed-frequency three-harmonic filter bank with bounded history.

    fundamental: integer >=7, default 20, in input bars. F/2 and F/3 remain
    real-valued periods; never truncate harmonic periods with integer division.
    F>6 keeps the third harmonic strictly below Nyquist. Extremely large F
    that rounds a coefficient onto a stability boundary is rejected as well.
    O(F) work and O(F) memory; newest-to-oldest ordinary binary64 power sums.
    Configuration is read-only; reset starts an independent chronological run.
    """

    def __init__(self, fundamental: int = 20) -> None:
        # Boolean is an int subclass in Python, but is not a meaningful period.
        # Integral floats are intentionally rejected: the power window is a
        # precise sample count, and other ports should expose the same contract.
        if (isinstance(fundamental, bool) or not isinstance(fundamental, int)
                or fundamental < 7):
            raise ValueError("fundamental must be an integer of at least 7")
        try:
            real_fundamental = float(fundamental)
        except OverflowError as error:
            raise ValueError("fundamental must yield stable binary64 coefficients") from error

        coefficients = []
        for harmonic in (1, 2, 3):
            period = real_fundamental / harmonic
            l = math.cos(TWO_PI / period)
            g = math.cos(BANDWIDTH * TWO_PI / period)
            # Keep the published reciprocal/square-root expression. An
            # algebraic sin/cos rewrite could change the final reference bits.
            s = 1.0 / g - math.sqrt(1.0 / (g * g) - 1.0)
            # For the supported domain these strict inequalities guarantee a
            # stable nondegenerate two-pole filter (see description.md).
            if not (-1.0 < l < 1.0 and 0.0 < g < 1.0 and 0.0 < s < 1.0):
                raise ValueError("fundamental must yield stable binary64 coefficients")
            coefficients.append(HarmonicCoefficients(l, g, s))

        self._fundamental = fundamental
        self._coefficients = tuple(coefficients)
        self._quadrature_scale = real_fundamental / TWO_PI
        self._roc_scale = real_fundamental / FOUR_PI
        self.reset()

    @property
    def fundamental(self) -> int:
        return self._fundamental

    @property
    def bandwidth(self) -> float:
        return BANDWIDTH

    @property
    def coefficients(self) -> tuple[HarmonicCoefficients, ...]:
        return self._coefficients

    @property
    def warmup_bars(self) -> int:
        """Leading Wave NaNs / first available zero-based Wave index: F-1."""
        return self._fundamental - 1

    @property
    def roc_warmup_bars(self) -> int:
        """Leading ROC NaNs / first available zero-based ROC index: F+1."""
        return self._fundamental + 1

    @property
    def samples_seen(self) -> int:
        return self._samples_seen

    @property
    def is_primed(self) -> bool:
        """A complete F-bar source observation window exists for Wave."""
        return self._samples_seen >= self._fundamental

    @property
    def roc_is_primed(self) -> bool:
        """Both Wave endpoints in the two-bar difference are available."""
        return self._samples_seen >= self._fundamental + 2

    @property
    def state(self) -> FourierSeriesState:
        return self._state

    @property
    def output(self) -> FourierSeriesOutput:
        return self._state.output

    def reset(self) -> None:
        """Restore source variables and empty all actual price/bar histories."""
        self._samples_seen = 0
        self._prices: list[float] = []  # Two previous actual closes, newest first.
        self._bp1 = (0.0, 0.0, 0.0)    # BP_h[1] seeds, not raw prices.
        self._bp2 = (0.0, 0.0, 0.0)    # BP_h[2] seeds.
        # Every accepted source bar contributes a BP/Q observation. The first
        # forced-zero source bars are REAL observations and count toward F.
        # Each history row is (BP tuple, Q tuple), newest source bar first.
        self._history: list[tuple[tuple[float, ...], tuple[float, ...]]] = []
        self._wave = 0.0               # Persistent source Wave(0).
        self._wave1 = self._wave2 = 0.0  # Two internal Wave lag seeds for ROC.
        self._state = FourierSeriesState(
            (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
            0.0, 0.0, FourierSeriesOutput(math.nan, math.nan))

    def update(self, close: float) -> FourierSeriesOutput:
        """Consume one finite finalized close, oldest to newest, exactly once.

        Invalid input or nonfinite intermediate arithmetic raises ValueError
        without consuming a bar. All candidate calculations are local until
        the final commit. NaN is only an output availability marker.
        """
        price = float(close)
        if not math.isfinite(price):
            raise ValueError("close must be finite")
        source_bar = self._samples_seen + 1  # EasyLanguage CurrentBar is one-based.

        bp_values = []
        q_values = []
        # The source overwrites BP on bars 1..3. Skip its discarded arithmetic
        # instead of inventing missing raw prices for Close[2]. On bar 4 the
        # lagged close is the REAL second input, and both BP lags are zero.
        difference = price - self._prices[1] if source_bar > 3 else 0.0
        if not math.isfinite(difference):
            raise ValueError("two-bar price difference must remain finite")
        for h, (l, _g, s) in enumerate(self._coefficients):
            bp = 0.0
            if source_bar > 3:
                # Preserve the literal source multiplication and left-to-right
                # addition/subtraction. Do not substitute a library IIR filter.
                bp = (0.5 * (1.0 - s) * difference
                      + l * (1.0 + s) * self._bp1[h] - s * self._bp2[h])
            q = 0.0
            if source_bar > 4:
                # All harmonics use F/(2*pi), NOT (F/h)/(2*pi). The article's
                # derivative approximation is intentionally preserved here.
                q = self._quadrature_scale * (bp - self._bp1[h])
            if not (math.isfinite(bp) and math.isfinite(q)):
                raise ValueError("band-pass and quadrature arithmetic must remain finite")
            bp_values.append(bp)
            q_values.append(q)
        band_pass = tuple(bp_values)
        quadrature = tuple(q_values)
        history = [(band_pass, quadrature)] + self._history[:self._fundamental - 1]

        powers = [0.0, 0.0, 0.0]
        for old_bp, old_q in history:
            for h in range(3):
                # The source is (P + BP*BP) + Q*Q, not P + (BP*BP + Q*Q).
                # Visit newest to oldest. Omitted pre-stream zeros add nothing.
                # No rolling subtraction, compensated sum, mean centering, or
                # division by F: these powers are the literal unaveraged sums.
                powers[h] = powers[h] + old_bp[h] * old_bp[h] + old_q[h] * old_q[h]
                if not math.isfinite(powers[h]):
                    raise ValueError("harmonic power accumulation must remain finite")

        wave = self._wave
        if powers[0] != 0.0:
            ratio2 = powers[1] / powers[0]
            ratio3 = powers[2] / powers[0]
            if not (math.isfinite(ratio2) and math.isfinite(ratio3)):
                raise ValueError("relative harmonic powers must remain finite")
            wave = (band_pass[0] + math.sqrt(ratio2) * band_pass[1]
                    + math.sqrt(ratio3) * band_pass[2])
        # NO ELSE: Wave persists when P1 is exactly zero. There is no epsilon
        # threshold, gain cap, additional harmonic phase adjustment, or AGC.
        roc = self._roc_scale * (wave - self._wave2)
        if not (math.isfinite(wave) and math.isfinite(roc)):
            raise ValueError("Wave and ROC arithmetic must remain finite")

        # Availability is separate from numerical state. Source forced-zero
        # bars count toward F, but invented pre-stream histories do not.
        output = FourierSeriesOutput(
            wave if source_bar >= self._fundamental else math.nan,
            roc if source_bar >= self._fundamental + 2 else math.nan)

        # Commit only after every candidate passes its arithmetic checks.
        self._prices = [price] + self._prices[:1]
        self._bp2, self._bp1 = self._bp1, band_pass
        self._history = history
        self._wave = wave
        self._wave2, self._wave1 = self._wave1, wave
        self._samples_seen = source_bar
        self._state = FourierSeriesState(band_pass, quadrature, tuple(powers), wave, roc, output)
        return output


class ReferenceCase(NamedTuple):
    """One confirmed Fundamental and the exact shared fixture comment text."""
    fundamental: int
    what_it_tests: str


# The user confirmed all twenty Fourier parameter combinations on 2026-10-20.
# Preserve this authorization for repeatable regeneration of these exact cases.
REFERENCE_CASES_CONFIRMED = True
REFERENCE_CASES = (
    ReferenceCase(20, "Article default: twenty-bar fundamental with second and third harmonics."),
    ReferenceCase(7, "Minimum supported fundamental: third harmonic just below Nyquist."),
    ReferenceCase(8, "Short even fundamental with a fractional third-harmonic period."),
    ReferenceCase(9, "Short odd fundamental with a three-bar third harmonic."),
    ReferenceCase(10, "Ten-bar fundamental: short-cycle response and fractional third harmonic."),
    ReferenceCase(12, "Exact six-bar second and four-bar third harmonic periods."),
    ReferenceCase(14, "Intermediate fast fundamental with a fractional third harmonic."),
    ReferenceCase(16, "Intermediate even fundamental with an eight-bar second harmonic."),
    ReferenceCase(19, "Odd fundamental immediately below the article default."),
    ReferenceCase(21, "Odd fundamental immediately above the article default."),
    ReferenceCase(24, "Exact twelve-bar second and eight-bar third harmonic periods."),
    ReferenceCase(30, "Longer fundamental with exact fifteen-bar and ten-bar harmonics."),
    ReferenceCase(40, "Twice the default fundamental and a forty-bar power window."),
    ReferenceCase(60, "Long fundamental with exact thirty-bar and twenty-bar harmonics."),
    ReferenceCase(80, "Slow eighty-bar fundamental with a fractional third harmonic."),
    ReferenceCase(100, "Extended hundred-bar power window and slow transient response."),
    ReferenceCase(200, "Long-history setting: fifty-three available Wave and fifty-one ROC values."),
    ReferenceCase(250, "Record boundary: three available Wave values and only the final ROC value."),
    ReferenceCase(252, "Record boundary: only the final Wave value is available and all ROC values are NaN."),
    ReferenceCase(253, "Record boundary: both outputs remain unprimed throughout the 252-bar record."),
)


def _case_suffix(case: ReferenceCase) -> str:
    """F abbreviates Fundamental; output components get a separate suffix."""
    return f"F{case.fundamental}"


def _parameter_comment(case: ReferenceCase) -> str:
    return f"fundamental={case.fundamental}; bandwidth=0.1 (fixed)"


def _float_literal(value: float, nan_literal: str) -> str:
    """Round only output TEXT to 15 significant decimal digits, not state."""
    if math.isnan(value):
        return nan_literal
    if not math.isfinite(value):
        raise ValueError("reference outputs must be finite after priming")
    literal = format(value, ".15g")
    # Rust and Zig benefit from explicit float syntax for integer-valued output.
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"
    return literal


def _array_lines(values: list[float], indent: str, nan_literal: str) -> str:
    """Wrap six numeric literals per row; preserve one value per input bar."""
    literals = [_float_literal(value, nan_literal) for value in values]
    return "\n".join(
        indent + ", ".join(literals[index:index + 6]) + ","
        for index in range(0, len(literals), 6)
    )


def _load_literal_arrays(path: Path) -> dict[str, list[float]]:
    """Parse Python arrays without executing the fixture or its imports."""
    arrays = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.List):
            continue
        values = []
        for element in node.value.elts:
            if (isinstance(element, ast.Name) and element.id == "NaN"):
                values.append(math.nan)
            else:
                values.append(float(ast.literal_eval(element)))
        for target in node.targets:
            if isinstance(target, ast.Name):
                arrays[target.id] = values
    return arrays


def _write_generated_section(path: Path, section: str, comment: str) -> None:
    """Append expected data, or replace only this indicator's own section on a rerun."""
    begin = f"{comment} BEGIN GENERATED FOURIER SERIES EXPECTED DATA"
    end = f"{comment} END GENERATED FOURIER SERIES EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    generated = begin + "\n\n" + section.rstrip() + "\n\n" + end + "\n"
    if begin in original:
        start = original.index(begin)
        finish = original.index(end, start) + len(end)
        # A missing end marker raises before writing, preserving malformed data.
        result = original[:start] + generated.rstrip("\n") + original[finish:]
    else:
        result = original.rstrip() + "\n\n" + generated
    path.write_text(result, encoding="utf-8")


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write approved outputs to Python, verify them, then translate four formats.

    This is standalone conversion tooling, separate from streaming state.
    Only the marked generated sections are replaced on a rerun. Original
    OHLC input arrays stay intact. Both output components get separate arrays
    so each future language can test either or both public values.
    """
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError("confirm the proposed Fourier parameter cases before generating expected data")
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 closes and between 1 and 64 parameter cases")
    python_path = directory / "test_testdata.py"
    if _load_literal_arrays(python_path)["INPUT_CLOSE"] != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from the copied fixture")

    outputs = {}
    warmups = {}
    sections = ["# Public unavailable outputs use the requested NaN spelling.\nNaN = math.nan"]
    for case in REFERENCE_CASES:
        indicator = FourierSeriesAnalysis(case.fundamental)
        results = [indicator.update(close) for close in input_close]
        for component, prefix in (("WAVE", indicator.warmup_bars),
                                  ("ROC", indicator.roc_warmup_bars)):
            name = "EXPECTED_" + _case_suffix(case) + "_" + component
            if name in outputs:
                raise ValueError("parameter/output cases must have unique names")
            values = [getattr(result, component.lower()) for result in results]
            outputs[name] = values
            warmups[name] = min(prefix, 252)
            sections.append(
                f"# {case.what_it_tests}\n# {_parameter_comment(case)}\n"
                f"{name} = [\n{_array_lines(values, '    ', 'NaN')}\n]")
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # The reopened PYTHON arrays, rounded to 15 significant digits, are the
    # sole authority for every translated numeric literal. Other languages
    # never recompute their own references with a different arithmetic order.
    written = _load_literal_arrays(python_path)
    if {name for name in written if name.startswith("EXPECTED_")} != set(outputs):
        raise ValueError("missing or unexpected Python expected arrays")
    for name, raw in outputs.items():
        values = written[name]
        prefix = warmups[name]
        if len(values) != 252:
            raise ValueError(f"{name} must contain exactly 252 values")
        if not all(math.isnan(value) for value in values[:prefix]):
            raise ValueError(f"{name} must start with {prefix} NaNs")
        if not all(math.isfinite(value) for value in values[prefix:]):
            raise ValueError(f"{name} must be finite after priming")
        if values[prefix:] != [float(_float_literal(value, "NaN")) for value in raw[prefix:]]:
            raise ValueError(f"{name} has incorrect 15-digit numeric literals")

    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8")
    go_text = go_text.replace("package xxxx", "package fourierseriesanalysis", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package fourierseriesanalysis\n",
                                  'package fourierseriesanalysis\n\nimport "math"\n', 1)
    go_path.write_text(go_text, encoding="utf-8")

    zig_path = directory / "testdata.zig"
    zig_text = zig_path.read_text(encoding="utf-8")
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n' + zig_text
    if "const nan = math.nan(f64);" not in zig_text:
        zig_text = zig_text.replace('const math = @import("std").math;\n',
                                    'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(zig_text, encoding="utf-8")

    translated = {"go": [], "ts": [], "rs": [], "zig": []}
    for case in REFERENCE_CASES:
        for component in ("WAVE", "ROC"):
            suffix = _case_suffix(case) + "_" + component
            values = written["EXPECTED_" + suffix]
            # These two comments exactly match the two Python comment texts.
            comments = f"// {case.what_it_tests}\n// {_parameter_comment(case)}\n"
            translated["go"].append(comments + f"var expected{suffix} = []float64{{\n"
                                    + _array_lines(values, "\t", "math.NaN()") + "\n}")
            translated["ts"].append(comments + f"export const expected{suffix}: number[] = [\n"
                                    + _array_lines(values, "    ", "NaN") + "\n];")
            translated["rs"].append(comments + f"pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n"
                                    + _array_lines(values, "        ", "f64::NAN") + "\n    ]\n}")
            translated["zig"].append(comments + f"pub fn expected{suffix}() [252]f64 {{\n    return .{{\n"
                                     + _array_lines(values, "        ", "nan") + "\n    };\n}")
    for language, filename in (("go", "testdata_test.go"), ("ts", "testdata.ts"),
                               ("rs", "testdata.rs"), ("zig", "testdata.zig")):
        _write_generated_section(directory / filename, "\n\n".join(translated[language]), "//")
    print(f"Verified {len(outputs)} arrays of 252 values for {len(REFERENCE_CASES)} cases; wrote all five languages.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true",
                        help="generate all user-confirmed cases in the five fixture files")
    arguments = parser.parse_args()

    # The complete shared close record is embedded here so the example is
    # standalone. The generator additionally checks it against test_testdata.py.

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

    indicator = FourierSeriesAnalysis(fundamental=20)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print("Default first five available Wave values:",
          [item.wave for item in outputs[indicator.warmup_bars:indicator.warmup_bars + 5]])
    print("Default first five available ROC values:",
          [item.roc for item in outputs[indicator.roc_warmup_bars:indicator.roc_warmup_bars + 5]])
    print("Reference cases (" + ("confirmed" if REFERENCE_CASES_CONFIRMED else "proposed") + "):")
    for case in REFERENCE_CASES:
        print(f"  {_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        if not REFERENCE_CASES_CONFIRMED:
            parser.error("the user must confirm the proposed Fourier parameter table first")
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
