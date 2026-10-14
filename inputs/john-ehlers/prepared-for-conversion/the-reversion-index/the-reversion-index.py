"""The Reversion Index: research prototype MASTER REFERENCE implementation.

John F. Ehlers, TASC January 2026, "The Reversion Index", pp. 16-18.
Numerical authority: the article's EasyLanguage indicator and SuperSmoother.
Read description.md for the complete equations, source differences, and
the agreed standalone initialization convention.

This deliberately uses only the Python standard library. Feed one finite close
at a time to ReversionIndex.update(); its named tuple contains ratio, smooth,
and trigger. No future samples or external market-data service are required.

Unlike the article, the two filter periods are configurable. Defaults reproduce
its Length(20), Smooth period 8, and Trigger period 4. The first length updates
return NaN in every field. The first complete window is valid immediately;
the first three valid ratios seed both filters by passing through unchanged.

Commands, from this directory or any other working directory:
    python3 the-reversion-index.py              # example and confirmed grid
    python3 the-reversion-index.py --generate   # update all five data files
    python3 the-reversion-index.py --verify     # validate saved data and tests

Reference values have 15 digits AFTER the decimal point, as in the existing
conversion example. Internal state always retains the unrounded float.
"""

import argparse
import ast
import math
from pathlib import Path
import re
from typing import NamedTuple
import unittest


class ReversionIndexResult(NamedTuple):
    """One bar's outputs; all fields are NaN until a full window exists."""

    ratio: float
    smooth: float
    trigger: float


def _finite_number(value, name):
    """Validate before state changes; reject bool and implicit string parsing.

    Restricting values to built-in int/float keeps the porting contract simple.
    Integer prices are accepted and converted to IEEE-754 binary64.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be an int or float, excluding bool")
    try:
        number = float(value)
    except OverflowError as error:
        raise ValueError(f"{name} must be representable as a finite float") from error
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


class _SuperSmoother:
    """Private two-pole filter; called only with complete-window ratios.

    Each instance owns independent histories. Calling it only when the ratio
    exists is essential: NaN is an outward warm-up marker, never filter state.
    """

    def __init__(self, period):
        # Exact article literals. Replacing 1.414 with sqrt(2), or 3.14159
        # with math.pi in the exponential, changes the reference values.
        q = math.exp(-1.414 * 3.14159 / period)

        # EasyLanguage Cosine accepts DEGREES. The exact degree expression
        # is evaluated first, then converted to radians for Python's cosine.
        # The conversion uses math.pi; the exponential above does not.
        if q == 0.0:
            # At extremely small positive periods q underflows to zero.
            # Its multiplied cosine coefficient is then zero regardless of
            # angle; avoid evaluating an angle that may overflow to infinity.
            # This binary64 limit does not affect any confirmed grid period.
            self._c1 = 0.0
        else:
            angle = math.radians(1.414 * 180.0 / period)
            self._c1 = 2.0 * q * math.cos(angle)
        self._c2 = q * q
        self._a0 = (1.0 - self._c1 + self._c2) / 2.0

        self._valid_bars = 0
        self._input_previous = 0.0
        self._output_previous = 0.0
        self._output_two_ago = 0.0

    def update(self, value):
        self._valid_bars += 1
        if self._valid_bars < 4:
            # Article: If CurrentBar < 4 Then $SuperSmoother = Price.
            # CurrentBar is 1-based over valid ratio calculations here.
            output = value
        else:
            # Article's a0/c1/c2 form, with its left-to-right additions and
            # subtraction. Do not use fused multiply-add or round this.
            output = (
                self._a0 * (value + self._input_previous)
                + self._c1 * self._output_previous
                - self._c2 * self._output_two_ago
            )

        # Shift AFTER evaluation so [1] and [2] refer to prior bars.
        self._input_previous = value
        self._output_two_ago = self._output_previous
        self._output_previous = output
        return output


class ReversionIndex:
    """Streaming normalized price displacement and its two smoothed lines.

    length: integer >= 1; number of differences, requiring length+1 closes.
    smooth_period, trigger_period: finite positive int/float, default 8 and 4.
    Periods >= 2 are meaningful relative to the sampled-data Nyquist limit;
    practical smoothing pairs usually use a slow period above a fast period.
    Equal/reversed periods are supported intentionally for diagnostic tests.

    Runtime is O(length) per full-window update and memory is O(length).
    A fixed-size ring of closes keeps streaming state bounded. O(length)
    recomputation preserves the original summation order instead of slowly
    accumulating roundoff through a rolling sum.
    """

    def __init__(self, length=20, smooth_period=8, trigger_period=4):
        if isinstance(length, bool) or not isinstance(length, int):
            raise TypeError("length must be an integer, excluding bool")
        if length < 1:
            raise ValueError("length must be >= 1")
        slow = _finite_number(smooth_period, "smooth_period")
        fast = _finite_number(trigger_period, "trigger_period")
        if slow <= 0.0 or fast <= 0.0:
            raise ValueError("smoothing periods must be > 0")

        # These public read-only properties describe the construction-time
        # parameters. Mutating periods mid-stream would invalidate histories.
        self._length = length
        self._smooth_period = slow
        self._trigger_period = fast
        self._smooth = _SuperSmoother(slow)
        self._trigger = _SuperSmoother(fast)

        # Ring cursor identifies the next insertion slot. Values of zero
        # in unused slots are never read: the count gates full-window work.
        self._prices = [0.0] * (length + 1)
        self._next_slot = 0
        self._count = 0

        # EasyLanguage Ratio(0) is a retained series variable. When the
        # denominator becomes zero, its last assigned value survives.
        self._ratio = 0.0

    @property
    def length(self):
        return self._length

    @property
    def smooth_period(self):
        return self._smooth_period

    @property
    def trigger_period(self):
        return self._trigger_period

    @property
    def warmup_bars(self):
        """Number of leading NaN outputs, not a filter convergence estimate."""
        return self._length

    def update(self, close):
        """Accept one finite close; return ratio, smooth, trigger for this bar.

        Missing/nonfinite inputs raise without consuming a bar. To start a new
        independent series, construct a new instance; no gap filling is implicit.
        """
        price = _finite_number(close, "close")
        capacity = len(self._prices)
        self._prices[self._next_slot] = price
        self._next_slot = (self._next_slot + 1) % capacity
        self._count = min(self._count + 1, capacity)

        if self._count < capacity:
            # No synthetic previous close or partial-window ratio is used.
            return ReversionIndexResult(math.nan, math.nan, math.nan)

        delta_sum = 0.0
        abs_delta_sum = 0.0
        # Add capacity BEFORE subtraction. Negative remainders differ between
        # Python and Go/Rust, and unsigned subtraction may trap in Zig.
        # These nonnegative expressions can be copied directly into ports.
        newest = (self._next_slot + capacity - 1) % capacity
        for count in range(self._length):
            current = self._prices[(newest + capacity - count) % capacity]
            previous = self._prices[(newest + capacity - count - 1) % capacity]

            # EasyLanguage: DeltaSum = DeltaSum + Close[count] - Close[count+1].
            # In finite precision (sum+current)-previous can differ from
            # sum+(current-previous). Preserve the published expression.
            delta_sum = (delta_sum + current) - previous
            abs_delta_sum = abs_delta_sum + abs(current - previous)

        if abs_delta_sum != 0.0:
            self._ratio = delta_sum / abs_delta_sum
        # There is intentionally no else: retain Ratio, including +/-1 after
        # a one-way price move ages out of a now completely flat window.

        return ReversionIndexResult(
            self._ratio,
            self._smooth.update(self._ratio),
            self._trigger.update(self._ratio),
        )


# Confirmed by the user. This is a selected grid, not a Cartesian product.
# Fourth element is the exact "What it tests" comment for all three outputs.
REFERENCE_CASES = (
    (20, 8, 4, "TASC code defaults"),
    (10, 8, 4, "Article's monthly-cycle example and MESA default"),
    (1, 8, 4, "Smallest difference window"),
    (2, 8, 4, "Two-difference window"),
    (5, 8, 4, "Short window"),
    (14, 8, 4, "Intermediate window"),
    (40, 8, 4, "Long window and trend-like behavior"),
    (251, 8, 4, "First valid output on the final input"),
    (252, 8, 4, "Insufficient history; all outputs remain NaN"),
    (10, 4, 2, "Fast smoothing pair"),
    (10, 12, 6, "Moderate smoothing pair"),
    (10, 16, 8, "Slow smoothing pair"),
    (20, 16, 8, "Longer window with slower smoothing"),
    (10, 8, 8, "Equal periods produce identical lines"),
    (10, 4, 8, "Reversed periods swap the two lines"),
    (10, 8.5, 4.5, "Fractional periods and array naming"),
)
OUTPUT_FIELDS = ("ratio", "smooth", "trigger")
DATA_FILES = ("test_testdata.py", "testdata_test.go", "testdata.ts",
              "testdata.rs", "testdata.zig")
BEGIN_MARKER = "BEGIN GENERATED REVERSION INDEX REFERENCE DATA"
END_MARKER = "END GENERATED REVERSION INDEX REFERENCE DATA"
HERE = Path(__file__).resolve().parent


def _parameter_text(value):
    # The confirmed finite numbers have simple, stable decimal spellings.
    return str(value) if isinstance(value, int) else format(value, "g")


def parameter_tag(length, smooth, trigger):
    """Portable tag, e.g. L10_S8_5_T4_5; integral values omit .0."""
    values = (_parameter_text(v).replace(".", "_")
              for v in (length, smooth, trigger))
    return "L%s_S%s_T%s" % tuple(values)


def read_input_close():
    """Read just the literal input array, without executing the data module."""
    tree = ast.parse((HERE / DATA_FILES[0]).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "INPUT_CLOSE"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError("INPUT_CLOSE missing from test_testdata.py")


def compute_reference_vectors(closes):
    """Compute unrounded binary64 values once, one instance per configuration."""
    vectors = []
    for length, slow, fast, explanation in REFERENCE_CASES:
        indicator = ReversionIndex(length, slow, fast)
        results = [indicator.update(close) for close in closes]
        parameters = (
            f"length={length}, smooth_period={_parameter_text(slow)}, "
            f"trigger_period={_parameter_text(fast)}"
        )
        for field in OUTPUT_FIELDS:
            name = f"EXPECTED_{parameter_tag(length, slow, fast)}_{field.upper()}"
            values = [getattr(result, field) for result in results]
            vectors.append((name, explanation, parameters, values))
    return vectors


def _rows(tokens, indent):
    """Ten literals per row; every language uses the same decimal tokens."""
    return "\n".join(
        indent + ", ".join(tokens[start:start + 10]) + ","
        for start in range(0, len(tokens), 10)
    )


def _replace_generated(path, body, prefix, inside_rust_module=False):
    """Append initially; replace only our marked section on subsequent runs.

    Original input arrays and unrelated comments survive byte-for-byte.
    Rust is special: its reference functions belong inside the template's
    existing cfg(test) module, rather than outside the closing module brace.
    """
    text = path.read_text(encoding="utf-8")
    begin = prefix + BEGIN_MARKER
    end = prefix + END_MARKER
    section = begin + "\n" + body + "\n" + end + "\n"
    pattern = re.compile(re.escape(begin) + r"\n.*?" + re.escape(end) + r"\n?", re.S)
    matches = list(pattern.finditer(text))
    if matches:
        if len(matches) != 1:
            raise ValueError(f"Multiple generated sections in {path.name}")
        text = pattern.sub(lambda match: section, text, count=1)
    elif BEGIN_MARKER in text or END_MARKER in text:
        raise ValueError(f"Incomplete generated section in {path.name}")
    elif inside_rust_module:
        closing = text.rfind("}")
        if closing < 0 or text[closing + 1:].strip():
            raise ValueError("Rust template must end with its module brace")
        text = text[:closing].rstrip() + "\n\n" + section + text[closing:]
    else:
        text = text.rstrip() + "\n\n" + section
    path.write_text(text, encoding="utf-8")


def read_serialized_vectors():
    """Read decimal tokens AND the two comments from the Python master data.

    Other-language emitters consume these tokens, not independently recomputed
    or reformatted numbers. This makes Python the single serialization source.
    """
    text = (HERE / DATA_FILES[0]).read_text(encoding="utf-8")
    pattern = re.compile(
        r"^# ([^\n]+)\n# ([^\n]+)\n(EXPECTED_[A-Z0-9_]+) = \[\n(.*?)\n\]",
        re.M | re.S,
    )
    vectors = []
    for explanation, parameters, name, body in pattern.findall(text):
        tokens = [token.strip() for token in body.split(",") if token.strip()]
        if len(tokens) != 252:
            raise ValueError(f"{name} has {len(tokens)} values instead of 252")
        for token in tokens:
            if token != "NaN" and not re.fullmatch(r"-?\d+\.\d{15}", token):
                raise ValueError(f"Invalid reference literal: {token}")
        vectors.append((name, explanation, parameters, tokens))
    if len(vectors) != 48:
        raise ValueError(f"Expected 48 reference arrays, found {len(vectors)}")
    return vectors


def generate_reference_data(closes):
    """Regenerate five files using ONLY the confirmed parameter combinations."""
    if len(closes) != 252 or closes != read_input_close():
        raise ValueError("Embedded closes must equal the 252 template closes")

    python_blocks = ["NaN = math.nan"]
    for name, explanation, parameters, values in compute_reference_vectors(closes):
        tokens = ["NaN" if math.isnan(v) else format(v, ".15f") for v in values]
        python_blocks.append(
            f"# {explanation}\n# {parameters}\n{name} = [\n"
            + _rows(tokens, "    ") + "\n]"
        )
    _replace_generated(HERE / DATA_FILES[0], "\n\n".join(python_blocks), "# ")

    # Re-open Python: all subsequent data comes from its saved decimal arrays.
    vectors = read_serialized_vectors()
    for filename, language in zip(DATA_FILES[1:], ("go", "ts", "rs", "zig")):
        path = HERE / filename
        if language == "go":
            text = path.read_text(encoding="utf-8")
            text = re.sub(r"(?m)^package \w+$", "package thereversionindex", text)
            if 'import "math"' not in text:
                text = text.replace("package thereversionindex\n",
                                    'package thereversionindex\n\nimport "math"\n', 1)
            path.write_text(text, encoding="utf-8")
        # The Zig template already contains std.math and nan definitions.
        blocks = []
        for name, explanation, parameters, tokens in vectors:
            tag = name.removeprefix("EXPECTED_")
            comments = f"// {explanation}\n// {parameters}\n"
            if language == "go":
                body = _rows(["math.NaN()" if t == "NaN" else t for t in tokens], "\t")
                block = f"var expected{tag} = []float64{{\n{body}\n}}"
            elif language == "ts":
                body = _rows(tokens, "    ")
                block = f"export const expected{tag}: number[] = [\n{body}\n];"
            elif language == "rs":
                body = _rows(["f64::NAN" if t == "NaN" else t for t in tokens], "        ")
                block = (f"pub fn expected_{tag.lower()}() -> Vec<f64> {{\n"
                         f"    vec![\n{body}\n    ]\n}}")
            else:
                body = _rows(["nan" if t == "NaN" else t for t in tokens], "        ")
                block = (f"pub fn expected{tag}() [252]f64 {{\n"
                         f"    return .{{\n{body}\n    }};\n}}")
            rendered = comments + block
            if language == "rs":
                rendered = "\n".join("    " + line for line in rendered.splitlines())
            blocks.append(rendered)
        _replace_generated(path, "\n\n".join(blocks), "// ",
                           inside_rust_module=(language == "rs"))
    print("Generated 48 arrays x 252 values in each of the five language files.")


def main(closes):
    """Small executable streaming example, followed by optional generation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true",
                        help="update the confirmed reference arrays in all five files")
    parser.add_argument("--verify", action="store_true",
                        help="run numerical, serialization, and source-parity tests")
    args = parser.parse_args()
    if len(closes) != 252 or closes != read_input_close():
        raise ValueError("Embedded INPUT_CLOSE differs from the template")

    if args.generate:
        generate_reference_data(closes)
    if args.verify:
        # Tests live beside the master. Discovery imports the hyphenated file
        # through importlib; it never runs this script's example recursively.
        suite = unittest.defaultTestLoader.discover(
            str(HERE), pattern="test_the_reversion_index.py"
        )
        outcome = unittest.TextTestRunner(verbosity=2).run(suite)
        if not outcome.wasSuccessful():
            raise SystemExit(1)
    if not args.generate and not args.verify:
        indicator = ReversionIndex()
        print("Article defaults: length=20, smooth_period=8, trigger_period=4")
        print("index  close       ratio              smooth             trigger")
        for index, close in enumerate(closes):
            result = indicator.update(close)
            if index in (0, 19, 20, 21, 22, 23, 250, 251):
                print(f"{index:5d}  {close:8.3f}  {result.ratio: .15f}  "
                      f"{result.smooth: .15f}  {result.trigger: .15f}")
        print("\nConfirmed grid: 16 combinations, 3 outputs, 48 arrays per language.")
        for length, slow, fast, explanation in REFERENCE_CASES:
            print(f"  {parameter_tag(length, slow, fast):20s} {explanation}")
        print("Use --generate to regenerate, or --verify to check the saved references.")


if __name__ == "__main__":
    # This literal is copied exactly from the parent test_testdata.py.
    # Embedding it makes the executable example explicit for porting agents.
    # main() also checks it against the copied template on every invocation.
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
    main(INPUT_CLOSE)
