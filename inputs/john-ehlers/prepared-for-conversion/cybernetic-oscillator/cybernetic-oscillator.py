"""John Ehlers' June 2025 Cybernetic Oscillator: streaming master reference.

Close -> second-order HighPass -> SuperSmoother -> fixed 100-bar RMS -> ratio.
Only standard Python is required. update(close) returns one float, with 99
leading NaNs for missing RMS history. See description.md for the full theory,
source initialization, parameter cases and differences among published ports.

Full-precision pi and sqrt(2) are the default, following the user's preference.
coefficient_mode="article" reproduces the printed 1.414/3.14159 coefficients.
Run normally for an example on the embedded 252 closes. After confirmation,
--generate-reference-data writes all five languages' full-precision fixtures.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# Compute these constants once in binary64. Ports should use their own standard
# pi constant and sqrt(2.0), preserving precision throughout recursive state.
PI = math.pi
SQRT_TWO = math.sqrt(2.0)

# This is a literal 100 in the article's indicator, not a tunable third input.
RMS_LENGTH = 100


def _period(value: float) -> float:
    """Validate a coefficient-setting period; fractional bars are meaningful."""
    if isinstance(value, bool):
        raise ValueError("period must be a finite real number of at least 1")
    value = float(value)
    # A minimum of one follows the supplied NinjaTrader parameter range. The
    # article recommends substantially longer settings for practical trading.
    # Periods are NOT sample-window lengths and must not be integer-truncated.
    if not math.isfinite(value) or value < 1.0:
        raise ValueError("period must be finite and at least 1.0")
    return value


def _coefficients(period: float, highpass: bool, mode: str) -> tuple[float, float, float]:
    """Return c1, c2, c3 for either of the article's two recursive filters."""
    if mode == "full_precision":
        # The article's Cosine accepts DEGREES; math.cos accepts RADIANS.
        # Replacing sqrt(2) and pi in both exponent and angle consistently
        # produces the ideal mathematical coefficients used in our fixtures.
        angle = SQRT_TWO * PI / period
        a1 = math.exp(-angle)
        b1 = 2.0 * a1 * math.cos(angle)
    elif mode == "article":
        # Keep the two printed constants separate. The exponential contains
        # 3.14159, whereas conversion of the printed degree angle uses pi.
        # Using 1.414*3.14159 for BOTH angles would not reproduce EasyLanguage.
        a1 = math.exp(-1.414 * 3.14159 / period)
        b1 = 2.0 * a1 * math.cos(math.radians(1.414 * 180.0 / period))
    else:
        raise ValueError('coefficient_mode must be "full_precision" or "article"')
    c2 = b1
    c3 = -a1 * a1  # Negative: the recurrence ADDS c3 times the second lag.
    c1 = (1.0 + c2 - c3) / 4.0 if highpass else 1.0 - c2 - c3
    return c1, c2, c3


class HighPass:
    """Second-order highpass, with three zero outputs before recursion starts."""

    def __init__(self, period: float = 30.0, *, coefficient_mode: str = "full_precision") -> None:
        self.period = _period(period)
        self._c1, self._c2, self._c3 = _coefficients(self.period, True, coefficient_mode)
        self.reset()

    def reset(self) -> None:
        """Restart CurrentBar at one on the next successful update."""
        self._count = 0
        self._price1 = self._price2 = 0.0
        self._output1 = self._output2 = 0.0

    def update(self, price: float) -> float:
        """Consume one raw price; use only this bar and already stored lags."""
        price = float(price)
        if not math.isfinite(price):
            raise ValueError("price must be finite")
        if self._count < 3:
            # Standalone bar numbering: CurrentBar=count+1. The source assigns
            # HighPass=0 on bars 1, 2, 3, EVEN though price lags exist on bar 3.
            output = 0.0
        else:
            # Evaluate before shifting ANY histories; order and signs follow
            # c1*(Price-2*Price[1]+Price[2])+c2*HP[1]+c3*HP[2] literally.
            output = (
                self._c1 * (price - 2.0 * self._price1 + self._price2)
                + self._c2 * self._output1
                + self._c3 * self._output2
            )
        if not math.isfinite(output):
            raise ValueError("highpass output must be finite")
        # Raw prices must still be stored on all three zero-output startup bars.
        self._price2, self._price1 = self._price1, price
        self._output2, self._output1 = self._output1, output
        self._count += 1
        return output


class SuperSmoother:
    """Second-order lowpass, passing its own input through on the first 3 bars."""

    def __init__(self, period: float = 20.0, *, coefficient_mode: str = "full_precision") -> None:
        self.period = _period(period)
        self._c1, self._c2, self._c3 = _coefficients(self.period, False, coefficient_mode)
        self.reset()

    def reset(self) -> None:
        self._count = 0
        self._price1 = 0.0
        self._output1 = self._output2 = 0.0

    def update(self, price: float) -> float:
        """Smooth one highpass observation; it is NOT another raw close."""
        price = float(price)
        if not math.isfinite(price):
            raise ValueError("SuperSmoother input must be finite")
        if self._count < 3:
            # Price here means the input of THIS helper. In the full indicator
            # that input is HP=0 during startup, so LP is also exactly zero.
            output = price
        else:
            # Retain c1*(today+yesterday)/2 operation order from the source.
            # The two-bar input average supplies a transmission zero at Nyquist.
            output = (
                self._c1 * (price + self._price1) / 2.0
                + self._c2 * self._output1
                + self._c3 * self._output2
            )
        if not math.isfinite(output):
            raise ValueError("SuperSmoother output must be finite")
        self._price1 = price
        self._output2, self._output1 = self._output1, output
        self._count += 1
        return output


class CyberneticOscillator:
    """Serial highpass/lowpass output divided by its fixed 100-bar RMS.

    hp_length: highpass cutoff PERIOD in bars, default 30.
    lp_length: lowpass cutoff PERIOD in bars, default 20.
    Both accept finite real values >=1, including fractional values.
    For practical use the article suggests lp_length>8 and hp_length>=1.4*lp_length.
    These recommendations are not enforced algebraic restrictions.

    coefficient_mode defaults to full_precision. article is available for
    literal EasyLanguage comparison; it is not used in the expected arrays.
    The first 99 update results are NaN. The 100th is defined even if zero.
    A period of 500 does not require 500 observations to produce an output.
    """

    def __init__(self, hp_length: float = 30.0, lp_length: float = 20.0,
                 *, coefficient_mode: str = "full_precision") -> None:
        self._hp_length, self._lp_length = _period(hp_length), _period(lp_length)
        self._coefficient_mode = coefficient_mode
        # Separate stage histories are essential. The lowpass consumes THIS
        # bar's HP output. Do not mistakenly feed both helpers the raw close.
        self._highpass = HighPass(self._hp_length, coefficient_mode=coefficient_mode)
        self._lowpass = SuperSmoother(self._lp_length, coefficient_mode=coefficient_mode)
        self._rms_filter = RootMeanSquare(RMS_LENGTH)
        self.reset()

    @property
    def hp_length(self) -> float:
        return self._hp_length

    @property
    def lp_length(self) -> float:
        return self._lp_length

    @property
    def coefficient_mode(self) -> str:
        return self._coefficient_mode

    @property
    def is_primed(self) -> bool:
        """True once 100 observed LP values, including startup zeros, exist."""
        return self._rms_filter.is_primed

    @property
    def warmup_bars(self) -> int:
        """Number of unavailable output bars, not an IIR settling-time promise."""
        return RMS_LENGTH - 1

    @property
    def highpass(self) -> float:
        """Latest HP in price units; diagnostic, not another plotted output."""
        return self._last_hp

    @property
    def smoothed(self) -> float:
        """Latest bandpass LP in price units."""
        return self._last_lp

    @property
    def rms(self) -> float:
        """Latest LP RMS; NaN until the 100-bar window is available."""
        return self._last_rms

    def reset(self) -> None:
        """Clear all stages and restart the source's persistent output at zero."""
        self._highpass.reset()
        self._lowpass.reset()
        self._rms_filter.reset()
        self._last_hp = self._last_lp = 0.0
        self._last_rms = math.nan
        self._last_output = 0.0

    def update(self, close: float) -> float:
        """Consume one chronological close and return the normalized oscillator."""
        close = float(close)
        if not math.isfinite(close):
            # Missing/invalid observations are rejected before advancing stages.
            # The API does not invent a bar, reset, or inject NaN into recursion.
            raise ValueError("close must be finite")
        hp = self._highpass.update(close)
        lp = self._lowpass.update(hp)
        rms = self._rms_filter.update(lp)
        self._last_hp, self._last_lp, self._last_rms = hp, lp, rms
        if not self.is_primed:
            # All recursive states are populated DURING normalization warmup.
            # These 99 NaNs are an output availability mask, not filter inputs.
            return math.nan
        # Preserve this conditional separately from the RMS helper's zero-sum
        # conditional. If RMS is zero, CyberneticOsc retains its previous value.
        if rms != 0.0:
            self._last_output = lp / rms
        return self._last_output


class RootMeanSquare:
    """Finite-window RMS preserving the source's conditional zero-sum return.

    This helper accepts an integer length >= 1 for direct verification, but
    CyberneticOscillator always constructs it with the article's fixed 100.
    Missing window history is not padded: the first length-1 returns are NaN.
    When a full sum is zero, retain the previous RMS as the source does.
    """

    def __init__(self, length: int = RMS_LENGTH) -> None:
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError('RMS length must be an integer of at least 1')
        self.length = length
        self.reset()

    @property
    def is_primed(self) -> bool:
        return len(self._squares) == self.length

    def reset(self) -> None:
        """Clear squared-sample ring and initialize the persistent RMS to zero."""
        self._squares = []
        self._next = 0
        self._last_rms = 0.0

    def update(self, value: float) -> float:
        """Insert this sample and sum a full window from newest to oldest."""
        value = float(value)
        if not math.isfinite(value):
            raise ValueError('RMS input must be finite')
        square = value * value
        if not math.isfinite(square):
            raise ValueError('squared RMS input must be finite')

        # Store only squares, incrementally until the ring is full. Actual
        # filter startup zeros count as observations; absent history does not.
        if len(self._squares) < self.length:
            self._squares.append(square)
            self._next = len(self._squares) % self.length
        else:
            self._squares[self._next] = square
            self._next = (self._next + 1) % self.length
        if not self.is_primed:
            # Do not assign this unavailable output to persistent _last_rms.
            return math.nan

        # Match for count=0 to Length-1 inclusively: exactly length terms,
        # newest first, plain sequential addition. A compensated or rolling
        # total can produce different last bits from the reference loop.
        total = 0.0
        for lag in range(self.length):
            index = (self._next - 1 - lag) % self.length
            total = total + self._squares[index]
        if not math.isfinite(total):
            raise ValueError('RMS sum must be finite')

        # The source assigns the function result ONLY if SumSq<>0. Hence
        # an all-zero full window retains a previous nonzero RMS if one exists.
        # Do not replace this conditional by an unconditional sqrt expression.
        if total != 0.0:
            self._last_rms = math.sqrt(total / self.length)
        return self._last_rms




class ReferenceCase(NamedTuple):
    """A confirmed HP/LP pair and its exact portable fixture test comment."""

    hp_length: float
    lp_length: float
    what_it_tests: str


# Only the two input periods vary. RMS=100 and full_precision are fixed.
# Generation requires the explicit CLI flag; the normal demonstration writes
# no files. All 16 pairs were confirmed by the user on 2026-10-16.
REFERENCE_CASES = (
    ReferenceCase(30.0, 20.0, 'Article default and swing example.'),
    ReferenceCase(250.0, 20.0, 'Article trend example.'),
    ReferenceCase(55.0, 20.0, 'Fast highpass from the strategy example.'),
    ReferenceCase(156.0, 20.0, 'Slow highpass from the strategy example.'),
    ReferenceCase(1.0, 1.0, 'Minimum algebraic periods, below Nyquist.'),
    ReferenceCase(3.0, 2.0, 'Nyquist-scale smoothing.'),
    ReferenceCase(12.0, 8.0, 'Short smoothing at the article\'s suggested boundary.'),
    ReferenceCase(15.0, 10.0, 'Short passband with half-octave separation.'),
    ReferenceCase(20.0, 14.0, 'Intermediate, closely spaced edges.'),
    ReferenceCase(28.0, 20.0, 'Article\'s minimum recommended 1.4 ratio.'),
    ReferenceCase(30.5, 20.0, 'Fractional highpass period.'),
    ReferenceCase(30.0, 20.5, 'Fractional lowpass period.'),
    ReferenceCase(60.0, 40.0, 'Longer swing cycles.'),
    ReferenceCase(150.0, 100.0, 'Lowpass period equal to the RMS window.'),
    ReferenceCase(252.0, 180.0, 'Long filter memory on the 252-bar record.'),
    ReferenceCase(500.0, 20.0, 'Highpass period longer than the input record.'),
)


def _parameter_token(value: float) -> str:
    """Make portable names: 0.2 -> 0_2, -0.2 -> m0_2, 10.0 -> 10."""
    # A minus sign is invalid in an identifier, so 'm' denotes minus. Keep
    # integral parameter values compact; fixtures themselves always use floats.
    return format(value, "g").replace("-", "m").replace(".", "_")


def _case_suffix(case: ReferenceCase) -> str:
    """HP=HPLength, LP=LPLength; decimal points become underscores."""
    return f'HP{_parameter_token(case.hp_length)}_LP{_parameter_token(case.lp_length)}'


def _parameter_comment(case: ReferenceCase) -> str:
    return f'hp_length={case.hp_length:g}, lp_length={case.lp_length:g}'


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
    begin = f"{comment} BEGIN GENERATED CYBERNETIC OSCILLATOR EXPECTED DATA"
    end = f"{comment} END GENERATED CYBERNETIC OSCILLATOR EXPECTED DATA"
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


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Generate Python first, verify it, then translate its decimal literals.

    Only file syntax and names change across languages. Other-language expected
    data is loaded back from test_testdata.py, rather than being independently
    calculated or rounded from some other implementation.
    """
    if len(input_close) != 252:
        raise ValueError("the reference input must contain exactly 252 closes")
    if not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("reference case count must be between 1 and 64")

    # Check that the embedded main array equals the copied Python input. AST
    # parsing avoids executing any fixture file while loading numeric literals.
    python_path = directory / "test_testdata.py"
    copied_input = _load_literal_arrays(python_path)["INPUT_CLOSE"]
    if copied_input != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from test_testdata.py")

    python_sections = []
    raw_outputs = {}
    for case in REFERENCE_CASES:
        indicator = CyberneticOscillator(case.hp_length, case.lp_length)
        values = [indicator.update(price) for price in input_close]
        name = "EXPECTED_" + _case_suffix(case)
        raw_outputs[name] = values
        python_sections.append(
            f"# {case.what_it_tests}\n"
            f"# {_parameter_comment(case)}\n"
            f"{name} = [\n{_array_lines(values, '    ', 'math.nan')}\n]"
        )
    _write_generated_section(python_path, "\n\n".join(python_sections), "#")

    # Read the written Python arrays back and check count, length, and precision
    # before appending them to other languages. Current cases need a full 100-sample RMS;
    # the renderer uses each language's NaN syntax for the 99 unavailable bars. All fixtures use full_precision coefficients.
    written_arrays = _load_literal_arrays(python_path)
    expected_names = {name for name in written_arrays if name.startswith("EXPECTED_")}
    if expected_names != set(raw_outputs):
        raise ValueError("unexpected or missing Python expected array names")
    for name, raw in raw_outputs.items():
        written = written_arrays[name]
        if len(written) != 252:
            raise ValueError(f"{name} does not contain 252 outputs")
        if not all(math.isnan(value) for value in written[:RMS_LENGTH - 1]):
            raise ValueError(f"{name} must have exactly 99 leading NaNs")
        if not all(math.isfinite(value) for value in written[RMS_LENGTH - 1:]):
            raise ValueError(f"{name} must be finite after the RMS window is complete")
        for before, after in zip(raw, written):
            if math.isnan(before) and math.isnan(after):
                continue
            if not math.isclose(before, after, rel_tol=5e-14, abs_tol=5e-14):
                raise ValueError(f"{name} did not retain 15-digit precision")

    # Go uses its math import for the 99 NaNs in every expected array.
    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8").replace(
        "package xxxx", "package cyberneticoscillator", 1
    )
    if 'import "math"' not in go_text:
        go_text = go_text.replace(
            "package cyberneticoscillator\n",
            'package cyberneticoscillator\n\nimport "math"\n', 1,
        )
    go_path.write_text(go_text, encoding="utf-8")

    zig_path = directory / "testdata.zig"
    zig_text = zig_path.read_text(encoding="utf-8")
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n' + zig_text
    if 'const nan = math.nan(f64);' not in zig_text:
        zig_text = zig_text.replace(
            'const math = @import("std").math;\n',
            'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1,
        )
    zig_path.write_text(zig_text, encoding="utf-8")

    sections = {"go": [], "ts": [], "rs": [], "zig": []}
    for case in REFERENCE_CASES:
        suffix = _case_suffix(case)
        # This list is explicitly the data read from the Python fixture above.
        values = written_arrays["EXPECTED_" + suffix]
        comments = (
            f"// {case.what_it_tests}\n"
            f"// {_parameter_comment(case)}\n"
        )
        sections["go"].append(
            comments + f"var expected{suffix} = []float64{{\n"
            + _array_lines(values, "\t", "math.NaN()") + "\n}"
        )
        # Follow the existing valid TypeScript array syntax. The sample syntax
        # in the request contains a typo; export const name: number[] is valid.
        sections["ts"].append(
            comments + f"export const expected{suffix}: number[] = [\n"
            + _array_lines(values, "    ", "NaN") + "\n];"
        )
        sections["rs"].append(
            comments + f"pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n"
            + _array_lines(values, "        ", "f64::NAN") + "\n    ]\n}"
        )
        sections["zig"].append(
            comments + f"pub fn expected{suffix}() [252]f64 {{\n    return .{{\n"
            + _array_lines(values, "        ", "nan") + "\n    };\n}"
        )

    # Rust's copied input functions stay inside their existing cfg(test)
    # module. Expected functions are appended at file scope for direct access
    # from a port's tests, with no rename or reorganization of copied inputs.
    for language, filename in (
        ("go", "testdata_test.go"), ("ts", "testdata.ts"),
        ("rs", "testdata.rs"), ("zig", "testdata.zig"),
    ):
        _write_generated_section(directory / filename, "\n\n".join(sections[language]), "//")
    print(f"Verified {len(REFERENCE_CASES)} arrays of 252 outputs in Python; wrote all five languages.")


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



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--generate-reference-data", action="store_true",
        help="regenerate the confirmed reference cases in all five languages",
    )
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

    # Example streaming usage: feed all 252 closes, one call per observed bar.
    # The first 99 normalized outputs are NaN. Both recursive filters and the
    # squared-signal ring still advance on every bar during that warmup.
    indicator = CyberneticOscillator(hp_length=30.0, lp_length=20.0)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print("Default first five primed outputs (indices 99-103):", ", ".join(
        _float_literal(value, "NaN") for value in outputs[99:104]
    ))
    print("Reference parameter cases:")
    for case in REFERENCE_CASES:
        print(f"  EXPECTED_{_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
