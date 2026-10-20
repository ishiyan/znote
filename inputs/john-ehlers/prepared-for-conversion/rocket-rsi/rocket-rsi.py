"""Ehlers RocketRSI — Fisher transform of RSI on smoothed momentum (May 2018).

Standalone streaming research prototype master reference; standard library only.
Source pipeline: Close - Close[RSILength-1] -> two-pole SuperSmoother ->
finite-window centered gain/loss ratio -> +/-0.999 clamp -> Fisher transform.
Full-precision pi and sqrt(2) replace the source's rounded filter constants.

update(close) returns one scalar. Only REAL momentum/filter observations count
toward availability. The first 2*RSILength outputs are NaN; the first numeric
zero-based index is 2*RSILength. Zero recursive filter lags are not RSI data.
RSILength=1 is supported: zero-lag momentum is identically zero and the primed
oscillator is zero. The clipped ratio persists when its denominator is zero.

Normal execution demonstrates the 252 embedded closes. The twenty reference
pairs were confirmed by the user on 2026-10-20. --generate-reference-data
appends and verifies 15-significant-digit arrays in all five language fixtures.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# Full-precision design constants. CLIP is a deliberate source threshold,
# not an approximation to a mathematical constant; keep it exactly 0.999.
PI = math.pi
SQRT_TWO = math.sqrt(2.0)
CLIP = 0.999


class RocketRSIState(NamedTuple):
    """Latest accepted intermediate values, for tracing another-language port.

    Each unavailable field is public NaN. myrsi is the CLIPPED ratio used by
    the Fisher transform, not the price-based MyRSI in the sibling folder.
    These are diagnostics; update still returns only the rocket_rsi scalar.
    """

    momentum: float
    filtered: float
    myrsi: float
    rocket_rsi: float


class RocketRSI:
    """Finite-window RSI of smoothed momentum, then source Fisher transform.

    smooth_length: finite real coefficient period >=3, default 8.0.
    rsi_length: integer >=1, default 10. BOTH the momentum lag R-1 and the
    number of filtered one-bar changes R derive from this same parameter.

    Smoothing longer than the RSI window is permitted but increases lag.
    update consumes one finite finalized close; reset preserves configuration.
    O(R) bounded storage and O(R) work per accepted update make the source
    arithmetic transparent to port without a scientific/statistical library.
    """

    def __init__(self, smooth_length: float = 8.0, rsi_length: int = 10) -> None:
        if isinstance(smooth_length, bool):
            raise ValueError("smooth_length must be finite and at least 3")
        self._smooth_length = float(smooth_length)
        if not math.isfinite(self._smooth_length) or self._smooth_length < 3.0:
            raise ValueError("smooth_length must be finite and at least 3")
        # bool is an int subclass in Python, but is not a valid sample count.
        if isinstance(rsi_length, bool) or not isinstance(rsi_length, int) or rsi_length < 1:
            raise ValueError("rsi_length must be an integer of at least 1")
        self._rsi_length = rsi_length
        self._momentum_lag = rsi_length - 1  # Literal source lag, NOT R.

        # Source expvalue(-1.414*3.14159/S), Cosine(1.414*180/S) in degrees.
        # Full-precision replacements give the SAME radian angle in both.
        angle = SQRT_TWO * PI / self._smooth_length
        a1 = math.exp(-angle)
        self._c2 = 2.0 * a1 * math.cos(angle)
        self._c3 = -a1 * a1  # Negative coefficient, ADDED as a signed term.
        self._c1 = 1.0 - self._c2 - self._c3
        if not (0.0 < a1 < 1.0 and self._c1 > 0.0):
            # Extreme periods can round the pole to one or cancel c1 away.
            raise ValueError("smooth_length must yield representable stable coefficients")
        self.reset()

    @property
    def smooth_length(self) -> float:
        """Read-only real smoother period; fractions are never rounded."""
        return self._smooth_length

    @property
    def rsi_length(self) -> int:
        """Number of filtered changes; also sets momentum lag to R-1."""
        return self._rsi_length

    @property
    def momentum_lag(self) -> int:
        return self._momentum_lag

    @property
    def warmup_bars(self) -> int:
        """NaN-prefix length and first numeric zero-based input index."""
        return 2 * self._rsi_length

    @property
    def is_primed(self) -> bool:
        """True after R+1 actual filter outputs, even if the signal is flat."""
        return len(self._history) == self._rsi_length + 1

    @property
    def state(self) -> RocketRSIState:
        """Diagnostic observations; reading them never advances the stream."""
        return self._state

    @property
    def output(self) -> float:
        return self._state.rocket_rsi

    def reset(self) -> None:
        """Empty actual input histories and reset source recursive variables."""
        self._prices: list[float] = []  # Newest FIRST, at most R prices.
        self._mom1 = None              # No previous REAL momentum yet.
        self._filt1 = 0.0              # Source Filt(0) recursive output seed.
        self._filt2 = 0.0              # Two independent lags, even when R=1.
        self._history: list[float] = []  # Actual filtered momentum only.
        self._myrsi = 0.0              # Persistent CLIPPED ratio, source MyRSI(0).
        self._state = RocketRSIState(math.nan, math.nan, math.nan, math.nan)

    def update(self, close: float) -> float:
        """Consume a finite chronological Close and return one RocketRSI value.

        All candidate state stays local until arithmetic succeeds. Invalid
        inputs and overflow consume no observation and preserve old state.
        Public NaNs express unavailable observations and are never recursed.
        """
        price = float(close)
        if not math.isfinite(price):
            raise ValueError("close must be finite")

        # At R-1 raw lag, momentum requires exactly R REAL prices. R=1 uses
        # current Close minus itself, deliberately yielding zero for any price.
        prices = [price] + self._prices[:self._momentum_lag]
        if len(prices) < self._rsi_length:
            self._prices = prices
            self._state = RocketRSIState(math.nan, math.nan, math.nan, math.nan)
            return math.nan
        momentum = price - prices[self._momentum_lag]
        if not math.isfinite(momentum):
            raise ValueError("momentum arithmetic must remain finite")
        if self._mom1 is None:
            # First actual momentum is stored only. The filter uses Mom[1],
            # so wait for a second actual momentum rather than fabricate one.
            self._prices = prices
            self._mom1 = momentum
            self._state = RocketRSIState(momentum, math.nan, math.nan, math.nan)
            return math.nan

        # Preserve source grouping: multiply c1 BEFORE dividing by two.
        # c3 is negative and its signed product is ADDED. Read OLD lags.
        pair = momentum + self._mom1
        filtered = (self._c1 * pair / 2.0
                    + self._c2 * self._filt1 + self._c3 * self._filt2)
        if not math.isfinite(pair) or not math.isfinite(filtered):
            raise ValueError("SuperSmoother arithmetic must remain finite")

        # Only actual filter outputs count toward the RSI window. Zero
        # recursive prehistory must not become fabricated filtered prices.
        history = [filtered] + self._history[:self._rsi_length]
        myrsi = self._myrsi
        public_ratio = rocket = math.nan
        if len(history) == self._rsi_length + 1:
            cu = 0.0
            cd = 0.0
            # Source count=0..R-1 runs NEWEST to OLDEST and recomputes
            # both sums every bar. Do not maintain rolling/compensated sums.
            for count in range(self._rsi_length):
                newer = history[count]
                older = history[count + 1]
                difference = newer - older
                if not math.isfinite(difference):
                    raise ValueError("filtered changes must remain finite")
                if difference > 0.0:
                    # Literal source CU = CU + Filt[count] - Filt[count+1].
                    # LEFT association differs from CU += (newer-older).
                    intermediate = cu + newer
                    cu = intermediate - older
                    if not math.isfinite(intermediate) or not math.isfinite(cu):
                        raise ValueError("closes-up accumulation must remain finite")
                if difference < 0.0:
                    # Downward movement is stored as a POSITIVE magnitude.
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
                    raise ValueError("MyRSI ratio must remain finite")
            # NO ELSE assignment: hold previous CLIPPED ratio if the window
            # is flat. The article overwrites persistent MyRSI when clipping;
            # do not retain an unclipped +/-1 behind the scenes instead.
            if myrsi > CLIP:
                myrsi = CLIP
            if myrsi < -CLIP:
                myrsi = -CLIP
            # This .999 threshold bounds Fisher at +/-3.8002011672502,
            # not exactly +/-3 despite the source's standard-deviation comment.
            # Preserve the literal logarithm of a ratio, not an alternative
            # atanh/log1p evaluation with different floating-point grouping.
            rocket = 0.5 * math.log((1.0 + myrsi) / (1.0 - myrsi))
            public_ratio = myrsi

        # Commit accepted state only now. The diagnostic NaNs do not enter
        # finite recursive lags, the actual history, or the retained ratio.
        self._prices = prices
        self._mom1 = momentum
        self._filt2, self._filt1 = self._filt1, filtered
        self._history = history
        self._myrsi = myrsi
        self._state = RocketRSIState(momentum, filtered, public_ratio, rocket)
        return rocket


class ReferenceCase(NamedTuple):
    """Confirmed S/R pair with its exact shared five-language fixture comment."""

    smooth_length: float
    rsi_length: int
    what_it_tests: str


# RocketRSI is a separate indicator. The user explicitly confirmed all twenty
# RocketRSI cases on 2026-10-20; preserve that authorization for regeneration.
REFERENCE_CASES_CONFIRMED = True
REFERENCE_CASES = (
    ReferenceCase(8.0, 10, "Article RocketRSI default and nominal twenty-bar cycle."),
    ReferenceCase(3.0, 1, "Zero-lag momentum boundary: primed outputs are identically zero."),
    ReferenceCase(3.0, 2, "One-bar momentum and the shortest nondegenerate RSI window."),
    ReferenceCase(3.0, 5, "Minimum smoothing with a short momentum and RSI horizon."),
    ReferenceCase(3.0, 10, "Default RSI horizon with minimum smoothing lag."),
    ReferenceCase(5.0, 10, "Default RSI horizon with fast intermediate smoothing."),
    ReferenceCase(10.0, 10, "TradeStation RocketRSI default and matched parameter periods."),
    ReferenceCase(8.5, 10, "Fractional smoother period without coefficient-period rounding."),
    ReferenceCase(20.0, 10, "Smoother longer than the RSI horizon and increased lag."),
    ReferenceCase(8.0, 5, "Default smoothing with a short momentum and RSI horizon."),
    ReferenceCase(8.0, 8, "Matched eight-bar settings and nominal sixteen-bar cycle."),
    ReferenceCase(8.0, 14, "Default smoothing with a fourteen-change RSI window."),
    ReferenceCase(8.0, 20, "Default smoothing with a nominal forty-bar cycle."),
    ReferenceCase(8.0, 30, "Default smoothing with a long thirty-change RSI window."),
    ReferenceCase(10.0, 20, "Moderate smoothing relative to a twenty-change RSI window."),
    ReferenceCase(20.0, 40, "Longer smoothing and a nominal eighty-bar cycle."),
    ReferenceCase(40.0, 80, "Slow smoothing and extended momentum and RSI horizons."),
    ReferenceCase(8.0, 125, "Record boundary: only the final two observations are primed."),
    ReferenceCase(8.0, 126, "Record boundary: every output remains unprimed."),
    ReferenceCase(252.0, 10, "Full-record smoothing period with a long recursive transient."),
)


def _case_suffix(case: ReferenceCase) -> str:
    """S=SmoothLength and R=RSILength; use underscores for decimal points."""
    smooth = format(case.smooth_length, "g").replace(".", "_")
    return f"S{smooth}_R{case.rsi_length}"


def _parameter_comment(case: ReferenceCase) -> str:
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
    begin = f"{comment} BEGIN GENERATED ROCKET RSI EXPECTED DATA"
    end = f"{comment} END GENERATED ROCKET RSI EXPECTED DATA"
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
        indicator = RocketRSI(case.smooth_length, case.rsi_length)
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
    go_text = go_text.replace("package xxxx", "package rocketrsi", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package rocketrsi\n",
                                  'package rocketrsi\n\nimport "math"\n', 1)
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
    indicator = RocketRSI(smooth_length=8.0, rsi_length=10)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print("Default first five available RocketRSI values:",
          outputs[indicator.warmup_bars:indicator.warmup_bars + 5])
    print("Reference cases (" + ("confirmed" if REFERENCE_CASES_CONFIRMED else "proposed") + "):")
    for case in REFERENCE_CASES:
        print(f"  {_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        if not REFERENCE_CASES_CONFIRMED:
            parser.error("the user must confirm the proposed reference parameter table first")
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
