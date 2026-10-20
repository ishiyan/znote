"""Ehlers Deviation-Scaled Moving Average (DSMA), TASC / Mesa, July 2018.

Streaming research prototype master; use only the Python standard library.
Close-Close[2] -> SuperSmoother at Period/2 -> Period-bar zero-centered RMS
-> persistent ScaledFilt -> abs(ScaledFilt)*5/Period -> adaptive price EMA.
The Mesa / TradeStation zero-RMS guard is authoritative; never clamp alpha.
Use math.sqrt(2.0) and math.pi instead of truncated EasyLanguage constants.

Startup follows the explicit zero-variable seed in the source / NinjaTrader:
first two closes establish Close[2]; first filter at t=2 uses Zeros[1]=0 and
two zero recursive lags. The DSMA recurrence starts at that same t=2 with
DSMA[1]=0. RMS always divides by the full Period, including during startup.
Public outputs are NaN until Period actual filtered values exist: first
numeric index / NaN prefix = Period+1. Hidden finite recursion still advances
while that RMS history fills. Constant input from reset gives primed zero,
not the constant price; this deliberately preserves the source zero seed.

Normal execution demonstrates 252 embedded closes. All twenty reference periods
were confirmed by the user on 2026-10-20. --generate-reference-data writes
15-significant-digit Python arrays, reopens / verifies them, then translates
four other languages.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# Binary64 mathematical constants, NOT the rounded 1.414 and 3.14159.
PI = math.pi
SQRT_TWO = math.sqrt(2.0)
# Five is the source's deliberate approximate critical-period scaling, not a
# truncated mathematical constant. Do not replace it with 2*pi or EMA span.
ALPHA_SCALE = 5.0


class DSMAState(NamedTuple):
    """Latest accepted diagnostics, separate from scalar update output.

    zeros is unavailable for the first two raw observations. filtered exists
    from t=2. rms, scaled_filtered, alpha, and recursive_dsma expose the finite
    internal calculations during window fill; those partial RMS windows do NOT
    prime the public dsma. Public NaNs are never fed into recursive state.
    """
    zeros: float
    filtered: float
    rms: float
    scaled_filtered: float
    alpha: float
    recursive_dsma: float
    dsma: float


class DeviationScaledMovingAverage:
    """One-period DSMA with literal source recurrence and explicit availability.

    period: integer >=1, default 40. Sets both RMS sample count and the
    smoother period period/2. Odd periods retain a fractional smoother period.
    Very small periods are algebraically allowed by TradeStation but can give
    alpha>1, overshoot, and alpha>2 growth; the source includes no alpha clamp.
    Storage and work per update are O(period), bounded by observed history.
    reset() preserves configuration and starts a new independent stream.
    """

    def __init__(self, period: int = 40) -> None:
        # A loop/window length must be an integer, not a rounded real period.
        # Reject bool even though Python makes it a subclass of int.
        if isinstance(period, bool) or not isinstance(period, int) or period < 1:
            raise ValueError("period must be an integer of at least 1")
        try:
            real_period = float(period)
        except OverflowError as error:
            raise ValueError("period must yield representable stable coefficients") from error
        angle = SQRT_TWO * PI / (0.5 * real_period)
        a1 = math.exp(-angle)
        self._c2 = 2.0 * a1 * math.cos(angle)
        self._c3 = -a1 * a1
        self._c1 = 1.0 - self._c2 - self._c3
        if not (0.0 < a1 < 1.0 and self._c1 > 0.0):
            # Huge periods can round poles to one or cancel the feedforward
            # coefficient. Reject rather than create an inert/unstable filter.
            raise ValueError("period must yield representable stable coefficients")
        self._period = period
        self.reset()

    @property
    def period(self) -> int:
        """Read-only configuration; create another instance to change it."""
        return self._period

    @property
    def smooth_period(self) -> float:
        """The source's HALF period, with no integer division or rounding."""
        return 0.5 * self._period

    @property
    def warmup_bars(self) -> int:
        """Leading public NaNs and first numeric zero-based index: P+1."""
        return self._period + 1

    @property
    def is_primed(self) -> bool:
        """True when the RMS has P actual filter samples, including zeros."""
        return len(self._history) == self._period

    @property
    def state(self) -> DSMAState:
        """Reading diagnostics does not advance the stream."""
        return self._state

    @property
    def output(self) -> float:
        return self._state.dsma

    def reset(self) -> None:
        """Empty real histories and reset every source recursive variable."""
        self._prices: list[float] = []  # At most two prior REAL prices, newest first.
        self._zeros1 = 0.0              # Source Zeros(0) before first real difference.
        self._filt1 = self._filt2 = 0.0  # Source Filt(0) seeds, private only.
        self._history: list[float] = [] # At most P ACTUAL filter values, newest first.
        self._scaled = 0.0              # Persistent source ScaledFilt(0).
        self._dsma = 0.0                # Source DSMA(0), not a price-based seed.
        self._state = DSMAState(*(math.nan for _ in range(7)))

    def update(self, close: float) -> float:
        """Accept one chronological finite close and return one scalar DSMA.

        Compute candidates locally; reject nonfinite input/overflow without
        consuming a bar or changing any previous raw/recursive history.
        Source multiplication/addition order is intentional for language ports.
        """
        price = float(close)
        if not math.isfinite(price):
            raise ValueError("close must be finite")
        if len(self._prices) < 2:
            # Close[2] does not yet exist; only the real raw history advances.
            # Do not invent a pre-record close or feed a public NaN to a filter.
            self._prices = [price] + self._prices
            return math.nan

        # Fixed two-bar RAW difference, unrelated to the configurable Period.
        zeros = price - self._prices[1]
        pair = zeros + self._zeros1
        if not math.isfinite(zeros) or not math.isfinite(pair):
            raise ValueError("two-bar difference arithmetic must remain finite")
        # Literal source c1*(Zeros+Zeros[1])/2 + c2*Filt[1] + c3*Filt[2].
        # c3 is NEGATIVE and is ADDED as a signed term. Read old lags first.
        filtered = (self._c1 * pair / 2.0
                    + self._c2 * self._filt1 + self._c3 * self._filt2)
        if not math.isfinite(filtered):
            raise ValueError("SuperSmoother arithmetic must remain finite")
        history = [filtered] + self._history[:self._period - 1]

        # Recompute source RMS newest to oldest each bar, with ordinary binary64
        # additions. A rolling sum, compensated sum, centered standard deviation,
        # or sample-variance denominator changes this master numerical reference.
        # Missing private filter lags contribute zero; omitting +0 terms is
        # equivalent. Still divide by P, never by the current fill count.
        power = 0.0
        for value in history:
            power = power + value * value
            if not math.isfinite(power):
                raise ValueError("RMS square accumulation must remain finite")
        rms = math.sqrt(power / self._period)
        scaled = self._scaled
        if rms != 0.0:
            scaled = filtered / rms
        # NO ELSE: Mesa / TradeStation retains previous ScaledFilt on exact
        # zero RMS. Do not silently clear it, add an epsilon, or return NaN.
        alpha = abs(scaled) * ALPHA_SCALE / self._period
        # The source does NOT bound alpha at one. In particular, the maximal
        # full-window value is 5/sqrt(P), and P<25 permits extrapolation.
        # Do not rewrite as old + alpha*(price-old): rounding order differs.
        dsma = alpha * price + (1.0 - alpha) * self._dsma
        if not all(math.isfinite(value) for value in (scaled, alpha, dsma)):
            raise ValueError("adaptive EMA arithmetic must remain finite")

        # The recurrence advances even before the complete public RMS window.
        # Masking is solely an availability convention, not delayed EMA startup.
        result = dsma if len(history) == self._period else math.nan
        self._prices = [price, self._prices[0]]
        self._zeros1 = zeros
        self._filt2, self._filt1 = self._filt1, filtered
        self._history = history
        self._scaled = scaled
        self._dsma = dsma
        self._state = DSMAState(zeros, filtered, rms, scaled, alpha, dsma, result)
        return result


class ReferenceCase(NamedTuple):
    """Confirmed period and exact shared five-language fixture description."""
    period: int
    what_it_tests: str


# The user explicitly confirmed all twenty DSMA cases on 2026-10-20.
# Preserve this authorization for repeatable regeneration of the reference data.
REFERENCE_CASES_CONFIRMED = True
REFERENCE_CASES = (
    ReferenceCase(40, "Article, Mesa, and TradeStation default critical period."),
    ReferenceCase(1, "Minimum algebraic period: alpha equals five on nonzero RMS and growth is preserved."),
    ReferenceCase(2, "Very short period: unclamped alpha can exceed two and amplify recursion."),
    ReferenceCase(3, "Odd short period: half-period smoothing and unclamped overshoot."),
    ReferenceCase(5, "Five-bar RMS window with an odd half-period smoother."),
    ReferenceCase(8, "Fast eight-bar adaptation with a four-bar smoother."),
    ReferenceCase(10, "Short ten-bar critical period and five-bar smoother."),
    ReferenceCase(14, "Intermediate fourteen-bar responsiveness."),
    ReferenceCase(20, "Twenty-bar critical period with possible alpha above one."),
    ReferenceCase(24, "Just below the theoretical alpha-at-most-one boundary."),
    ReferenceCase(25, "Exact theoretical alpha-at-most-one boundary with a 12.5-bar smoother."),
    ReferenceCase(26, "Just above the boundary: alpha strictly below one."),
    ReferenceCase(30, "JuicyCharts default period and moderately fast adaptation."),
    ReferenceCase(50, "Moderately slower adaptation than the article default."),
    ReferenceCase(80, "Long eighty-bar RMS window and forty-bar smoother."),
    ReferenceCase(100, "TradeStation strategy slow period with an alpha upper bound of one half."),
    ReferenceCase(200, "Long-history smoothing with fifty-one primed observations."),
    ReferenceCase(249, "Record boundary: only the final two observations are primed."),
    ReferenceCase(250, "Record boundary: only the final observation is primed."),
    ReferenceCase(251, "Record boundary: every output remains unprimed."),
)


def _case_suffix(case: ReferenceCase) -> str:
    """P abbreviates the single source configuration parameter Period."""
    return f"P{case.period}"


def _parameter_comment(case: ReferenceCase) -> str:
    return f"period={case.period}"


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
    begin = f"{comment} BEGIN GENERATED DSMA EXPECTED DATA"
    end = f"{comment} END GENERATED DSMA EXPECTED DATA"
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
    warmup_by_name = {}
    sections = ["# Public unavailable outputs use the requested NaN spelling.\nNaN = math.nan"]
    for case in REFERENCE_CASES:
        indicator = DeviationScaledMovingAverage(case.period)
        values = [indicator.update(close) for close in input_close]
        name = "EXPECTED_" + _case_suffix(case)
        if name in raw_outputs:
            raise ValueError("parameter cases must have unique names")
        raw_outputs[name] = values
        warmup_by_name[name] = indicator.warmup_bars
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
        warmup = min(warmup_by_name[name], len(input_close))
        if len(values) != 252:
            raise ValueError(f"{name} must contain exactly 252 values")
        if not all(math.isnan(value) for value in values[:warmup]):
            raise ValueError(f"{name} must begin with {warmup} NaNs")
        if not all(math.isfinite(value) for value in values[warmup:]):
            raise ValueError(f"{name} must be finite after priming")
        for before, after in zip(raw[warmup:], values[warmup:]):
            if after != float(_float_literal(before, "NaN")):
                raise ValueError(f"{name} has an incorrect 15-digit literal")

    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8")
    go_text = go_text.replace("package xxxx", "package deviationscaledmovingaverage", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package deviationscaledmovingaverage\n",
                                  'package deviationscaledmovingaverage\n\nimport "math"\n', 1)
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
                        help="generate all confirmed cases in the five fixture files")
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

    # Consume each finalized Close exactly once, oldest to newest.
    indicator = DeviationScaledMovingAverage(period=40)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print("Default first five available DSMA values:",
          outputs[indicator.warmup_bars:indicator.warmup_bars + 5])
    print("Reference cases (" + ("confirmed" if REFERENCE_CASES_CONFIRMED else "proposed") + "):")
    for case in REFERENCE_CASES:
        print(f"  {_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        if not REFERENCE_CASES_CONFIRMED:
            parser.error("the user must confirm the proposed reference parameter table first")
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
