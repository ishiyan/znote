"""Ehlers MyRSI — input-smoothed RSI (May 2018).

Streaming research prototype master reference; source name MyRSI.

The article smooths CLOSE with a two-pole SuperSmoother BEFORE computing the
normalized finite-window gain/loss imbalance. This is the MyRSI sidebar, not
the article's RocketRSI extension or Wilder's recursively averaged RSI.

Only the standard library is used. Full-precision pi and sqrt(2) replace the
article's rounded constants. See description.md for equations and startup.
First store one real close; then calculate the smoother from zero recursive
state. N actual filtered changes require N+1 valid filtered prices, giving
N+1 public NaNs followed by the first output at zero-based index N+1.

Normal execution demonstrates 252 embedded closes. All twenty parameter cases
are confirmed. --generate-reference-data writes and verifies all
five languages' expected arrays using 15 significant decimal digits.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# Compute these at full precision in every port. Both the exponential decay
# and the radian cosine use the SAME angle, unlike the rounded source text.
PI = math.pi
SQRT_TWO = math.sqrt(2.0)


class MyRSI:
    """Input-smoothed, centered finite-window RSI, default S=8 and R=10.

    smooth_length is a real coefficient period >=3, not a buffer length.
    rsi_length is an integer >=1 counting CHANGES, so it needs one extra
    filtered price. Longer smoothing is allowed even when S>R, although the
    article recommends S<=R in typical use because smoothing adds lag.

    update(close) returns one dimensionless float. Unavailable public NaNs
    never enter either the recursive smoother or the persistent MyRSI seed.
    Each update uses O(R) work and O(R) bounded storage; no numerical package,
    rolling sum, compensated accumulator, or data service is needed.
    """

    def __init__(self, smooth_length: float = 8.0, rsi_length: int = 10) -> None:
        # bool is a Python integer subclass but not a sensible period setting.
        if isinstance(smooth_length, bool):
            raise ValueError("smooth_length must be finite and at least 3")
        self._smooth_length = float(smooth_length)
        if not math.isfinite(self._smooth_length) or self._smooth_length < 3.0:
            raise ValueError("smooth_length must be finite and at least 3")
        if isinstance(rsi_length, bool) or not isinstance(rsi_length, int) or rsi_length < 1:
            raise ValueError("rsi_length must be an integer of at least 1")
        self._rsi_length = rsi_length

        # Source expvalue(-1.414*3.14159/S) and Cosine(1.414*180/S).
        # Replacing their approximations and converting degrees gives this
        # common radian angle. DO NOT round S or replace this with EMA weights.
        angle = SQRT_TWO * PI / self._smooth_length
        a1 = math.exp(-angle)
        self._c2 = 2.0 * a1 * math.cos(angle)
        self._c3 = -a1 * a1   # Negative coefficient; ADD its signed product.
        self._c1 = 1.0 - self._c2 - self._c3
        # At enormous periods, binary64 can round the pole to one or lose the
        # feedforward gain by cancellation. Report that numerical boundary.
        if not (0.0 < a1 < 1.0 and self._c1 > 0.0):
            raise ValueError("smooth_length must yield representable stable coefficients")
        self.reset()

    @property
    def smooth_length(self) -> float:
        """Read-only smoother coefficient period; fractions are not rounded."""
        return self._smooth_length

    @property
    def rsi_length(self) -> int:
        """Number of filtered one-bar changes in the RSI calculation."""
        return self._rsi_length

    @property
    def warmup_bars(self) -> int:
        """NaN-prefix length, equal to the first available zero-based index."""
        return self._rsi_length + 1

    @property
    def is_primed(self) -> bool:
        """True when R+1 actual smoother outputs exist, even if all are zero."""
        return len(self._history) == self._rsi_length + 1

    @property
    def filtered_value(self) -> float:
        """Latest available SuperSmoother value, useful for conversion checks."""
        return self._filt1 if self._bars >= 2 else math.nan

    @property
    def output(self) -> float:
        """Latest public scalar; reading it does not consume another bar."""
        return self._output

    def reset(self) -> None:
        """Clear raw/filter histories and restore the source MyRSI(0) seed."""
        self._bars = 0
        self._close1 = 0.0  # Placeholder only; NEVER used as a fabricated close.
        self._filt1 = 0.0   # Article Filt(0) supplies recursive output prehistory.
        self._filt2 = 0.0   # Keep two lags independently, including when R=1.
        self._history: list[float] = []  # Newest FIRST; actual filter outputs only.
        self._myrsi = 0.0   # Persistent value when CU+CD==0; not a public NaN.
        self._output = math.nan

    def update(self, close: float) -> float:
        """Consume one finite, finalized chronological close and return MyRSI.

        Reject nonfinite inputs and arithmetic overflow before committing any
        candidate state. Rejected observations do not advance the bar count.
        """
        price = float(close)
        if not math.isfinite(price):
            raise ValueError("close must be finite")
        if self._bars == 0:
            # The smoother requires Close[1]. Remember one actual close and
            # wait for the second; do not zero-pad or copy price into Filt.
            self._close1 = price
            self._bars = 1
            return math.nan

        # Preserve the article's association and negative c3 sign. The division
        # by two occurs AFTER multiplying c1; do not fold it into a coefficient.
        # Evaluate against OLD filter lags, and advance both only after success.
        pair = price + self._close1
        filtered = (self._c1 * pair / 2.0
                    + self._c2 * self._filt1 + self._c3 * self._filt2)
        if not math.isfinite(pair) or not math.isfinite(filtered):
            raise ValueError("SuperSmoother arithmetic must remain finite")

        history = [filtered] + self._history[:self._rsi_length]
        myrsi = self._myrsi
        public = math.nan
        if len(history) == self._rsi_length + 1:
            cu = 0.0
            cd = 0.0
            # Literal source count=0..R-1 runs NEWEST to OLDEST. Recompute
            # totals from scratch every bar. Do not use rolling sums or fsum.
            for count in range(self._rsi_length):
                newer = history[count]
                older = history[count + 1]
                difference = newer - older
                if not math.isfinite(difference):
                    raise ValueError("filtered price changes must remain finite")
                if difference > 0.0:
                    # Source CU = CU + Filt[count] - Filt[count+1] is LEFT
                    # associated, not CU + (newer-older). Preserve the two
                    # operations even though the expressions are algebraically
                    # equal; rounding may affect small moves near large prices.
                    intermediate = cu + newer
                    cu = intermediate - older
                    if not math.isfinite(intermediate) or not math.isfinite(cu):
                        raise ValueError("closes-up accumulation must remain finite")
                if difference < 0.0:
                    # Down moves contribute a POSITIVE magnitude to CD.
                    intermediate = cd + older
                    cd = intermediate - newer
                    if not math.isfinite(intermediate) or not math.isfinite(cd):
                        raise ValueError("closes-down accumulation must remain finite")

            total = cu + cd
            numerator = cu - cd
            if not math.isfinite(total) or not math.isfinite(numerator):
                raise ValueError("MyRSI totals must remain finite")
            if total != 0.0:
                myrsi = numerator / total
                if not math.isfinite(myrsi):
                    raise ValueError("MyRSI output must remain finite")
            # Article has NO ELSE: retain old MyRSI for an exactly flat window.
            # Initially this is zero. No epsilon, output smoothing, saturation,
            # RocketRSI .999 clipping, or Fisher transform applies to MyRSI.
            public = myrsi

        # Commit exactly one accepted observation. Public NaN availability is
        # separate from private finite recursive state and retained RSI seed.
        self._close1 = price
        self._filt2, self._filt1 = self._filt1, filtered
        self._history = history
        self._myrsi = myrsi
        self._bars += 1
        self._output = public
        return public


class ReferenceCase(NamedTuple):
    """A confirmed parameter pair and the shared five-language comment text."""

    smooth_length: float
    rsi_length: int
    what_it_tests: str


# The user confirmed all twenty MyRSI pairs on 2026-10-20. The recorded
# confirmation authorizes generation and future regeneration of these cases.
REFERENCE_CASES_CONFIRMED = True
REFERENCE_CASES = (
    ReferenceCase(8.0, 10, "Article MyRSI default and nominal twenty-bar cycle."),
    ReferenceCase(3.0, 1, "Minimum smoothing period and one-change direction limit."),
    ReferenceCase(3.0, 2, "Minimum smoothing with a two-change RSI window."),
    ReferenceCase(3.0, 5, "Minimum smoothing with a short five-change window."),
    ReferenceCase(3.0, 10, "Default RSI window with minimum smoothing lag."),
    ReferenceCase(5.0, 10, "Default RSI window with intermediate fast smoothing."),
    ReferenceCase(10.0, 10, "Equal smoothing and RSI periods; TradeStation RocketRSI settings."),
    ReferenceCase(8.5, 10, "Fractional smoother period without rounding the coefficient control."),
    ReferenceCase(20.0, 10, "Smoothing longer than the RSI window and increased lag."),
    ReferenceCase(8.0, 5, "Default smoothing with a short RSI lookback."),
    ReferenceCase(8.0, 8, "Matched eight-bar settings and nominal sixteen-bar cycle."),
    ReferenceCase(8.0, 14, "Default smoothing with Wilder's traditional fourteen-change length."),
    ReferenceCase(8.0, 20, "Default smoothing with a nominal forty-bar cycle."),
    ReferenceCase(8.0, 30, "Default smoothing with a long thirty-change RSI window."),
    ReferenceCase(10.0, 20, "Moderate smoothing relative to a twenty-change RSI window."),
    ReferenceCase(20.0, 40, "Longer smoothing and a nominal eighty-bar cycle."),
    ReferenceCase(40.0, 80, "Slow smoothing and an extended RSI window."),
    ReferenceCase(8.0, 250, "Record boundary: only the final observation is primed."),
    ReferenceCase(8.0, 251, "Record boundary: every output remains unprimed."),
    ReferenceCase(252.0, 10, "Full-record smoothing period with a long startup transient."),
)


def _case_suffix(case: ReferenceCase) -> str:
    """S is SmoothLength and R is RSILength; decimal points become underscores."""
    smooth = format(case.smooth_length, "g").replace(".", "_")
    return f"S{smooth}_R{case.rsi_length}"


def _parameter_comment(case: ReferenceCase) -> str:
    """This exact comment line accompanies each translated expected array."""
    return f"smooth_length={case.smooth_length:g}, rsi_length={case.rsi_length}"


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
    begin = f"{comment} BEGIN GENERATED MYRSI EXPECTED DATA"
    end = f"{comment} END GENERATED MYRSI EXPECTED DATA"
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
        indicator = MyRSI(case.smooth_length, case.rsi_length)
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
    go_text = go_text.replace("package xxxx", "package myrsi", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package myrsi\n",
                                  'package myrsi\n\nimport "math"\n', 1)
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

    # Streaming usage: consume each finalized close once, in chronological order.
    indicator = MyRSI(smooth_length=8.0, rsi_length=10)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print("Default first five available MyRSI values:",
          outputs[indicator.warmup_bars:indicator.warmup_bars + 5])
    print("Reference cases (" + ("confirmed" if REFERENCE_CASES_CONFIRMED else "proposed") + "):")
    for case in REFERENCE_CASES:
        print(f"  {_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        if not REFERENCE_CASES_CONFIRMED:
            parser.error("the user must confirm the proposed reference parameter table first")
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
