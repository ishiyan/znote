"""Ehlers' April 2025 Ultimate Oscillator: self-contained streaming master.

Two parallel highpasses, their difference, and a fixed 100-sample RMS produce
one scalar oscillator per observed close. Full-precision pi and sqrt(2) follow
the established user preference. See description.md for original formulas,
the explicit 99-NaN warmup, source conditionals and platform differences.

Standard Python only. Run without flags for a streaming demonstration on the
embedded 252 closes. After confirming the listed cases, run with
--generate-reference-data to verify and write fixtures for five languages.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# Binary64 mathematical constants, rather than the printed 3.14159 and 1.414.
# A port should use its standard pi constant and sqrt(2.0), not rounded decimals.
PI = math.pi
SQRT_TWO = math.sqrt(2.0)


class HighPass:
    """Second-order highpass with the article's first-three-zero startup.

    period is a finite real number >= 1.0, measured in bars; default 20.0.
    Fractional periods are supported. This is a coefficient-setting parameter,
    not a rolling window length and not a required count of warm-up observations.

    The first three successful updates return zero while storing raw prices. Thereafter
    the article's recurrence uses two previous raw prices and two previous
    outputs. All samples are consumed once, chronologically, without look-ahead.
    """

    def __init__(self, period: float = 20.0) -> None:
        self._period = float(period)
        # The supplied NinjaTrader UI uses a minimum period of one. The article
        # does not specify a minimum; this API accepts fractional periods >= 1.
        if not math.isfinite(self._period) or self._period < 1.0:
            raise ValueError("period must be finite and at least 1.0")

        # Full-precision radian form of the source's degree-based coefficients.
        # Compute this angle once; its negative sets the pole radius and its
        # cosine sets the pole rotation. Both child poles have radius a1 < 1.
        angle = SQRT_TWO * PI / self._period
        a1 = math.exp(-angle)
        b1 = 2.0 * a1 * math.cos(angle)

        # Keep the article's coefficient names and signs. In particular c3 is
        # NEGATIVE, so the last recurrence term is +c3*previous_previous_output.
        self._c2 = b1
        self._c3 = -a1 * a1
        self._c1 = (1.0 + self._c2 - self._c3) / 4.0
        self.reset()

    @property
    def period(self) -> float:
        """Read-only configuration; construct another filter to change period."""
        return self._period

    @property
    def is_primed(self) -> bool:
        """True after the first update, since zero-valued startup outputs are defined."""
        return self._count > 0

    @property
    def warmup_bars(self) -> int:
        """Number of leading NaN outputs: zero for the article's highpass-zero startup."""
        return 0

    def reset(self) -> None:
        """Clear histories; the next three observations will return zero."""
        self._count = 0
        # These initial zero histories are never read by the recursive formula:
        # the first three startup samples fill them before recursion starts.
        self._price1 = self._price2 = 0.0
        self._output1 = self._output2 = 0.0

    def update(self, price: float) -> float:
        """Consume one finite price and return this bar's highpass value."""
        price = float(price)
        if not math.isfinite(price):
            # Check before any state changes. Do not silently fill missing bars.
            raise ValueError("price must be finite")

        if self._count < 3:
            # With standalone CurrentBar=count+1, the article's CurrentBar<4
            # branch applies to indices 0, 1, and 2. HighPass is assigned zero.
            output = 0.0
        else:
            # Exactly the article's direct-form recurrence, with today's Price
            # and the two PRIOR raw inputs and outputs. Do not overwrite any of
            # those values until the entire expression has been evaluated.
            output = (
                self._c1 * (price - 2.0 * self._price1 + self._price2)
                + self._c2 * self._output1
                + self._c3 * self._output2
            )

        # Reject arithmetic overflow before committing. Ordinary finite prices
        # in the fixtures never take this branch. A rejected input does not
        # advance the successful-sample count or either history.
        if not math.isfinite(output):
            raise ValueError("filtered output must be finite")

        # Shift older values before assigning current values. Tuple assignment
        # makes simultaneous history updates explicit in this Python reference.
        self._price2, self._price1 = self._price1, price
        self._output2, self._output1 = self._output1, output
        self._count += 1
        return output


# The 100-bar RMS is fixed in the source indicator, not a third parameter.
RMS_LENGTH = 100


class RootMeanSquare:
    """Finite-window RMS preserving the source's conditional zero-sum return.

    This helper accepts an integer length >= 1 for direct verification, but
    UltimateOscillator always constructs it with the article's fixed 100.
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
        # highpass startup zeros count as observations; absent history does not.
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


class UltimateOscillator:
    """Parallel highpass difference divided by the fixed 100-bar signal RMS.

    band_edge is a finite real period >= 1, default 20; bandwidth is a finite
    real ratio >= 1.4, default 2. Long-period HP1 has period bandwidth*band_edge;
    short-period HP2 has period band_edge. Both read the SAME raw close.
    First 99 returned values are NaN; normalized output begins on sample 100.
    """

    def __init__(self, band_edge: float = 20.0, bandwidth: float = 2.0) -> None:
        band_edge, bandwidth = float(band_edge), float(bandwidth)
        if not math.isfinite(band_edge) or band_edge < 1.0:
            raise ValueError('band_edge must be finite and at least 1.0')
        if not math.isfinite(bandwidth) or bandwidth < 1.4:
            raise ValueError('bandwidth must be finite and at least 1.4')
        long_period = bandwidth * band_edge
        if not math.isfinite(long_period):
            raise ValueError('bandwidth times band_edge must be finite')
        self._band_edge, self._bandwidth = band_edge, bandwidth
        # Independent histories are essential. Neither path takes the other
        # highpass's output as its input: this is a difference, not a cascade.
        self._long_filter = HighPass(long_period)
        self._short_filter = HighPass(band_edge)
        self._rms_filter = RootMeanSquare(RMS_LENGTH)
        self.reset()

    @property
    def band_edge(self) -> float:
        return self._band_edge

    @property
    def bandwidth(self) -> float:
        return self._bandwidth

    @property
    def is_primed(self) -> bool:
        """True once the 100-sample signal RMS window exists."""
        return self._rms_filter.is_primed

    @property
    def warmup_bars(self) -> int:
        """Number of leading unavailable scalar oscillator values."""
        return RMS_LENGTH - 1

    def reset(self) -> None:
        """Restart both highpasses, the signal-square ring and final output."""
        self._long_filter.reset()
        self._short_filter.reset()
        self._rms_filter.reset()
        # Vars: UltimateOsc(0) is the source's persistent final output state.
        self._last_output = 0.0

    def update(self, close: float) -> float:
        """Observe one finite close; return this bar's normalized oscillator."""
        close = float(close)
        if not math.isfinite(close):
            raise ValueError('close must be finite')

        # Match source call order and difference sign: HP1(long)-HP2(short).
        hp1 = self._long_filter.update(close)
        hp2 = self._short_filter.update(close)
        signal = hp1 - hp2
        rms = self._rms_filter.update(signal)
        if not self.is_primed:
            # Keep consuming raw bars and populating both IIR histories even
            # while the final normalized result is unavailable.
            return math.nan

        # Preserve the SECOND conditional independently of RMS's conditional.
        # If RMS==0, hold the previous UltimateOsc. If SumSq==0 after a prior
        # positive RMS, the helper retains RMS and signal==0 divides to ZERO.
        if rms != 0.0:
            self._last_output = signal / rms
        return self._last_output


class ReferenceCase(NamedTuple):
    """A confirmed band-edge/width pair and its exact fixture test comment."""

    band_edge: float
    bandwidth: float
    what_it_tests: str


REFERENCE_CASES = (
    ReferenceCase(20.0, 2.0, 'Article default: twenty-bar short edge and forty-bar long edge, one octave apart.'),
    ReferenceCase(1.0, 2.0, 'Minimum band edge: algebraic boundary below the two-bar Nyquist wavelength.'),
    ReferenceCase(2.0, 2.0, 'Two-bar band edge: shortest Nyquist-scale short highpass.'),
    ReferenceCase(3.0, 2.0, 'Three-bar band edge: very short parallel highpass periods.'),
    ReferenceCase(5.0, 2.0, 'Short band edge: rapid signal response after the zero-output startup.'),
    ReferenceCase(10.0, 2.0, 'Intermediate short band edge: ten- and twenty-bar highpasses.'),
    ReferenceCase(20.5, 2.0, 'Fractional band edge: preserve coefficient periods without integer truncation.'),
    ReferenceCase(30.0, 2.0, 'Article chart and Traders Tips example: thirty- and sixty-bar highpasses.'),
    ReferenceCase(60.0, 2.0, 'Longer band edge: sixty- and one-hundred-twenty-bar highpasses.'),
    ReferenceCase(100.0, 2.0, 'Band edge equals the fixed RMS window while filter and RMS state remain separate.'),
    ReferenceCase(252.0, 2.0, 'Full-record band edge: long pole memory but priming still takes exactly one hundred bars.'),
    ReferenceCase(20.0, 1.4, 'Minimum recommended bandwidth: closely spaced twenty- and twenty-eight-bar edges.'),
    ReferenceCase(20.0, 1.5, 'Fractional bandwidth: twenty- and thirty-bar edges without ratio truncation.'),
    ReferenceCase(20.0, 3.0, 'Moderately wide band: twenty- and sixty-bar edges.'),
    ReferenceCase(20.0, 4.0, 'Two-octave band: twenty- and eighty-bar edges.'),
    ReferenceCase(20.0, 8.0, 'Three-octave band: twenty- and one-hundred-sixty-bar edges.'),
)


def _parameter_token(value: float) -> str:
    """Make portable names: 0.2 -> 0_2, -0.2 -> m0_2, 10.0 -> 10."""
    # A minus sign is invalid in an identifier, so 'm' denotes minus. Keep
    # integral parameter values compact; fixtures themselves always use floats.
    return format(value, "g").replace("-", "m").replace(".", "_")


def _case_suffix(case: ReferenceCase) -> str:
    """BE=BandEdge, BW=Bandwidth; decimal points become underscores."""
    return f'BE{_parameter_token(case.band_edge)}_BW{_parameter_token(case.bandwidth)}'


def _parameter_comment(case: ReferenceCase) -> str:
    return f'band_edge={case.band_edge:g}, bandwidth={case.bandwidth:g}'


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
    begin = f"{comment} BEGIN GENERATED ULTIMATE OSCILLATOR EXPECTED DATA"
    end = f"{comment} END GENERATED ULTIMATE OSCILLATOR EXPECTED DATA"
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
        indicator = UltimateOscillator(case.band_edge, case.bandwidth)
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
    # the renderer uses each language's NaN syntax for the 99 unavailable bars.
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
        "package xxxx", "package ultimateoscillator", 1
    )
    if 'import "math"' not in go_text:
        go_text = go_text.replace(
            "package ultimateoscillator\n",
            'package ultimateoscillator\n\nimport "math"\n', 1,
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
    # The first 99 normalized outputs are NaN. Both highpasses and the
    # squared-signal ring still advance on every bar during that warmup.
    indicator = UltimateOscillator(band_edge=20.0, bandwidth=2.0)
    outputs = [indicator.update(close) for close in INPUT_CLOSE]
    print("Default first five primed outputs (indices 99-103):", ", ".join(
        _float_literal(value, "NaN") for value in outputs[99:104]
    ))
    print("Reference parameter cases:")
    for case in REFERENCE_CASES:
        print(f"  EXPECTED_{_case_suffix(case)}: {case.what_it_tests}")
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
