"""March 2018 Recursive Median Filter: streaming research master reference.

Only Python's standard library is required. Read description.md before porting:
the median has exactly FIVE samples, the recursive state starts at ZERO, and
the first FOUR public outputs are NaN. LPPeriod is a critical-period control,
not a median window length or a conventional EMA length.

Normal execution demonstrates the default filter on 252 embedded closes.
All twelve REFERENCE_CASES are confirmed. --generate-reference-data appends
15-significant-digit expected arrays to all five copied fixture files.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# EasyLanguage Cosine/Sine take degrees; Python takes radians. This full
# precision constant replaces every rounded approximation to pi or 2*pi.
PI = math.pi

# Median(Price, 5) is FIXED in the article. Making it adjustable would add a
# parameter and change the specified indicator; it is deliberately constant.
MEDIAN_LENGTH = 5
WARMUP_BARS = MEDIAN_LENGTH - 1


def _validated_period(lp_period: float) -> float:
    """Require the conventional, positive-weight EMA branch of the formula.

    LPPeriod > 4 gives 0 < alpha < 1 and a positive stable recursive pole.
    Four itself is a removable singularity in the printed quotient; smaller
    periods can imply negative EMA weights, aliases, or unstable recursion.
    They are excluded rather than silently assigned a different coefficient.
    """
    if isinstance(lp_period, bool):
        raise ValueError("lp_period must be a finite real number greater than 4")
    period = float(lp_period)
    if not math.isfinite(period) or period <= 4.0:
        raise ValueError("lp_period must be finite and greater than 4")
    return period


class RecursiveMedianFilter:
    """EMA of a trailing five-value median, exactly the article's RM formula.

    update(close) consumes one chronological value and returns one float.
    Four unavailable outputs precede the first full-window calculation.
    The first available output is alpha * median(first_five), since the
    article's RM(0) initialization gives previous RM = 0, not the first close.

    Coefficients are computed once. The calculation preserves the printed
    multiplication/addition order and never rounds recursive state.
    """

    def __init__(self, lp_period: float = 12.0) -> None:
        self._lp_period = _validated_period(lp_period)

        # 360 degrees / LPPeriod == 2*pi / LPPeriod radians. Do not substitute
        # the article's rough alpha ~= 5 / LPPeriod approximation here.
        angle = 2.0 * PI / self._lp_period
        cosine = math.cos(angle)
        self._alpha = (cosine + math.sin(angle) - 1.0) / cosine

        # Extreme binary64 periods can lose the numerator through cancellation
        # or round the coefficient to a boundary. Fail visibly rather than
        # silently creating a frozen or unintended filter for such periods.
        if not 0.0 < self._alpha < 1.0:
            raise ValueError("lp_period must produce a representable coefficient in (0, 1)")
        self.reset()

    @property
    def lp_period(self) -> float:
        """Read-only configuration: changing it requires a fresh instance."""
        return self._lp_period

    @property
    def alpha(self) -> float:
        """Expose the EMA coefficient for checking conversions and examples."""
        return self._alpha

    @property
    def warmup_bars(self) -> int:
        """Number of initial unavailable outputs, independent of LPPeriod."""
        return WARMUP_BARS

    @property
    def is_primed(self) -> bool:
        """A full median window is available; this does not mean EMA settling."""
        return len(self._prices) == MEDIAN_LENGTH

    def reset(self) -> None:
        """Forget inputs and restore article RM(0), preserving coefficients."""
        self._prices: list[float] = []
        self._rm = 0.0

    def update(self, close: float) -> float:
        """Accept one finite close, returning NaN until five closes exist.

        NaN/inf inputs raise ValueError BEFORE changing any state. A missing
        observation is not a zero price and does not advance this stream.
        """
        price = float(close)
        if not math.isfinite(price):
            raise ValueError("close must be finite")

        # Keep the original chronological window. Never sort it in place:
        # that would lose the oldest sample and change the next median.
        # The short list and ordinary sorting port directly to other languages.
        self._prices.append(price)
        if len(self._prices) > MEDIAN_LENGTH:
            del self._prices[0]

        if not self.is_primed:
            # The private RM remains exactly zero during this startup. Feeding
            # this public NaN into the recurrence would poison every later bar.
            return math.nan

        ordered = sorted(self._prices)
        median_price = ordered[2]  # Third order statistic of FIVE observations.

        # Source: RM = alpha1*Median(Price,5) + (1-alpha1)*RM[1].
        # Evaluate using OLD RM, then replace it. A fused multiply-add or
        # RM += alpha*(median-RM) can change floating-point reference results.
        self._rm = self._alpha * median_price + (1.0 - self._alpha) * self._rm
        return self._rm


class ReferenceCase(NamedTuple):
    """A confirmed LPPeriod and the shared five-language fixture comment text."""

    lp_period: float
    what_it_tests: str


# The user explicitly confirmed all twelve cases on 2026-10-20. This recorded
# confirmation authorizes generation and future regeneration of these cases.
REFERENCE_CASES_CONFIRMED = True
REFERENCE_CASES = (
    ReferenceCase(4.5, "Near the positive-weight boundary and a fractional period."),
    ReferenceCase(5.0, "Shortest conventional integer period; median-dominated response."),
    ReferenceCase(6.0, "Short-period smoothing with modest recursive memory."),
    ReferenceCase(8.0, "Fast smoothing between the shortest periods and the default."),
    ReferenceCase(12.0, "Article and TradeStation lowpass default."),
    ReferenceCase(16.0, "Article chart's smoothing period."),
    ReferenceCase(24.0, "Twice the default period and increased recursive lag."),
    ReferenceCase(30.0, "Intermediate long-period smoothing."),
    ReferenceCase(40.0, "Two-month smoothing scale on daily trading bars."),
    ReferenceCase(100.0, "Long recursive memory and visible startup transient."),
    ReferenceCase(252.0, "Period equal to the full input-record length."),
    ReferenceCase(500.0, "Period longer than the record; availability versus settling."),
)


def _case_suffix(case: ReferenceCase) -> str:
    """Compact names: LP12 for an integer, LP4_5 for a fractional value."""
    return "LP" + format(case.lp_period, "g").replace(".", "_")


def _parameter_comment(case: ReferenceCase) -> str:
    """Copy this exact line above each array in each target language."""
    return f"lp_period={case.lp_period:g}, median_length=5 (fixed)"


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
    """Append expected data, or replace only our own section on a rerun."""
    begin = f"{comment} BEGIN GENERATED RECURSIVE MEDIAN FILTER EXPECTED DATA"
    end = f"{comment} END GENERATED RECURSIVE MEDIAN FILTER EXPECTED DATA"
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
    """Generate, reopen, verify Python output, then copy it to four languages.

    This is conversion tooling, separate from the streaming algorithm. Input
    arrays remain intact and the generator uses no third-party libraries.
    """
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError("confirm the proposed parameter table before generating expected data")
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected exactly 252 closes and between 1 and 64 parameter cases")
    python_path = directory / "test_testdata.py"
    if _load_literal_arrays(python_path)["INPUT_CLOSE"] != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from the copied fixture")

    raw_outputs = {}
    sections = ["# Public unavailable outputs use the requested NaN spelling.\nNaN = math.nan"]
    for case in REFERENCE_CASES:
        indicator = RecursiveMedianFilter(case.lp_period)
        values = [indicator.update(close) for close in input_close]
        name = "EXPECTED_" + _case_suffix(case)
        if name in raw_outputs:
            raise ValueError("parameter cases must have unique names")
        raw_outputs[name] = values
        sections.append(
            f"# {case.what_it_tests}\n# {_parameter_comment(case)}\n"
            f"{name} = [\n{_array_lines(values, '    ', 'NaN')}\n]"
        )
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # Verify actual arrays read from the generated master fixture BEFORE using
    # them as the source for Go, TypeScript, Rust, and Zig. No other language
    # independently recomputes or chooses its own rounded reference outputs.
    written = _load_literal_arrays(python_path)
    if {name for name in written if name.startswith("EXPECTED_")} != set(raw_outputs):
        raise ValueError("missing or unexpected Python reference arrays")
    for name, raw in raw_outputs.items():
        values = written[name]
        if len(values) != 252:
            raise ValueError(f"{name} must contain exactly 252 values")
        if not all(math.isnan(value) for value in values[:WARMUP_BARS]):
            raise ValueError(f"{name} must begin with four NaNs")
        if not all(math.isfinite(value) for value in values[WARMUP_BARS:]):
            raise ValueError(f"{name} must be finite after the first four values")
        for before, after in zip(raw[WARMUP_BARS:], values[WARMUP_BARS:]):
            if after != float(_float_literal(before, "NaN")):
                raise ValueError(f"{name} has an incorrect 15-digit literal")

    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8")
    go_text = go_text.replace("package xxxx", "package recursivemedianfilter", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package recursivemedianfilter\n",
                                  'package recursivemedianfilter\n\nimport "math"\n', 1)
    go_path.write_text(go_text, encoding="utf-8")

    # The copied Zig input template already provides these declarations.
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
        suffix = _case_suffix(case)
        values = written["EXPECTED_" + suffix]
        # Preserve exactly both Python comment texts above every translated
        # output declaration, replacing only the comment delimiter.
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
    print(f"Verified {len(raw_outputs)} arrays of 252 values; wrote all five languages.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true",
                        help="generate all confirmed parameter cases in all five fixture files")
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

    # Example: one instance consumes each close once, with no batch dependency.
    indicator = RecursiveMedianFilter(lp_period=12.0)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print(f"Default alpha: {indicator.alpha:.15g}")
    print("First five available RM values:", outputs[WARMUP_BARS:WARMUP_BARS + 5])
    print("Reference parameter cases (" + ("confirmed" if REFERENCE_CASES_CONFIRMED else "proposed") + "):")
    for case in REFERENCE_CASES:
        print(f"  {_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        if not REFERENCE_CASES_CONFIRMED:
            parser.error("the user must confirm the proposed reference parameter table first")
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
