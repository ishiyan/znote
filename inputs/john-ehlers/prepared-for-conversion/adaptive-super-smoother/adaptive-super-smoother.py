"""Adaptive SuperSmoother: research prototype MASTER REFERENCE implementation.

Source articles:
    1. John F. Ehlers, "Improved Filter Performance: Adaptive SuperSmoother",
       Technical Analysis of STOCKS & COMMODITIES (TASC), Vol. 44, No. 9,
       September 2026.
    2. John F. Ehlers, "Adaptive SuperSmoother", MESA Software technical paper:
       https://www.mesasoftware.com/papers/Adaptive%20SuperSmoother.pdf
    3. Traders' Tips - September 2026, Technical Analysis of STOCKS &
       COMMODITIES, Vol. 44, No. 9, September 2026.

Numerical authority:
    Ehlers' EasyLanguage Code Listings 1, 2, and 3 (Adaptive SuperSmoother,
    $SuperSmoother, and $RMS) from the MESA paper and September 2026 TASC
    article, combined with the confirmed standalone full-window RMS warmup
    convention. Read description.md for the full mathematical derivations,
    book background, and comparison with the Traders' Tips ports.

Design contract for ports (Rust, Zig, Go, TypeScript):
    * Pure Python standard library only (no numpy, no pandas, no third-party
      packages) so every operation translates 1:1 to systems languages.
    * Strictly STREAMING: feed one finite close price at a time into
      `AdaptiveSuperSmoother.update(close)` and receive an
      `AdaptiveSuperSmootherResult(ss, fixed_ss, osc, period)` named tuple.
    * No look-ahead and no unbounded history growth: memory is O(rms_length)
      and per-bar work is O(rms_length).
    * Exact IEEE-754 binary64 evaluation order and exact EasyLanguage literals
      (`1.414`, `3.14159` in `exp`, degree-to-radian conversion in `cos`).
    * Public outputs are `NaN` until `rms_length` one-bar differences of the
      adaptive SuperSmoother (`ROC1 = SS - SS[1]`) have been collected, which
      occurs at 0-based bar index `t = rms_length` (after `rms_length + 1`
      input closes).

Commands (can be run from any working directory):
    python3 adaptive-super-smoother.py              # run example and print grid
    python3 adaptive-super-smoother.py --generate   # write 64 arrays to 5 files
    python3 adaptive-super-smoother.py --verify     # run unit & parity tests
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
import re
from typing import NamedTuple
import unittest


# =============================================================================
# Public output container
# =============================================================================

class AdaptiveSuperSmootherResult(NamedTuple):
    """One bar of Adaptive SuperSmoother output.

    All four fields are IEEE-754 floats (`math.nan` on warmup bars
    `0 <= t < rms_length` before a full RMS window of `ROC1` values exists):
        ss       - Closed-loop Adaptive SuperSmoother (`Plot2(SS)` in article)
        fixed_ss - Fixed-period SuperSmoother with `period0` (`Plot1(...)`)
        osc      - Adaptive SuperSmoother Oscillator (`ss - fixed_ss`)
        period   - Newly tuned critical period computed on this bar (and used
                   to filter `ss` on the next bar), clamped to `[2.0, period0]`
    """

    ss: float
    fixed_ss: float
    osc: float
    period: float


# =============================================================================
# Input validation helpers
# =============================================================================

def _finite_number(value, name: str) -> float:
    """Validate that `value` is a finite int or float (excluding bool).

    Validating before mutating state ensures that a bad update never corrupts
    the streaming filter's internal ring buffer or recursive state.
    Note that in Python `bool` is a subclass of `int`, so it must be excluded
    explicitly.
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


# =============================================================================
# Internal building blocks: Ehlers' 2-Pole SuperSmoother ($SuperSmoother)
# =============================================================================

def _supersmoother_coefficients(period: float) -> tuple[float, float, float]:
    """Compute Ehlers' `$SuperSmoother` coefficients `(a0, c1, c2)`.

    Verbatim EasyLanguage from Code Listing 2:
        Q  = expvalue(-1.414*3.14159 / Period);
        c1 = 2*Q*Cosine(1.414*180 / Period);
        c2 = Q*Q;
        a0 = (1 - c1 + c2) / 2;

    Porting notes:
        1. `1.414` and `3.14159` in `expvalue` are exact decimal literals from
           Ehlers' code. Replacing `1.414` with `sqrt(2)` or `3.14159` with
           `math.pi` alters the 5th-6th significant digit.
        2. EasyLanguage `Cosine(...)` takes DEGREES. We compute the degree
           argument `1.414 * 180.0 / period` first and convert to radians with
           `math.radians(...)` (which multiplies by `math.pi / 180.0`).
        3. If `period` is an extremely small positive subnormal/float such that
           `q` underflows to `0.0`, `c1` is `0.0` without evaluating an angle
           that could overflow to infinity.
    """
    q = math.exp(-1.414 * 3.14159 / period)
    if q == 0.0:
        c1 = 0.0
    else:
        angle_rad = math.radians(1.414 * 180.0 / period)
        c1 = 2.0 * q * math.cos(angle_rad)
    c2 = q * q
    a0 = (1.0 - c1 + c2) / 2.0
    return a0, c1, c2


class _SuperSmoother:
    """Stateful two-pole SuperSmoother matching Code Listing 2.

    In EasyLanguage, every call to `$SuperSmoother(...)` in an indicator owns
    an independent series history (`$SuperSmoother[1]`, `$SuperSmoother[2]`).
    Code Listing 1 calls `$SuperSmoother` twice on each bar:
        - once with the dynamically tuned `Period` (`SS`)
        - once with the fixed base `Period0` (`Plot1`)
    We therefore instantiate two separate `_SuperSmoother` objects inside
    `AdaptiveSuperSmoother`.

    EasyLanguage startup rule (Code Listing 2):
        If CurrentBar >= 4 Then
            $SuperSmoother = a0*(Price + Price[1])
                           + c1*$SuperSmoother[1]
                           - c2*$SuperSmoother[2];
        If Currentbar < 4 Then $SuperSmoother = Price;

    Since `CurrentBar` is 1-based, `CurrentBar < 4` corresponds to the first
    three bars (`_valid_bars` == 1, 2, 3, or 0-based indices 0, 1, 2).
    """

    def __init__(self, initial_period: float):
        # Cache coefficients for the current period so the fixed-period filter
        # (and any bar where the adaptive period does not change) avoids
        # redundant transcendental calls.
        self._cached_period = initial_period
        self._a0, self._c1, self._c2 = _supersmoother_coefficients(initial_period)

        # 1-based count of bars processed by this filter (`CurrentBar`).
        self._valid_bars = 0

        # One-bar-ago input (`Price[1]`) and two-bar output history
        # (`$SuperSmoother[1]` and `$SuperSmoother[2]`).
        self._prev_input = 0.0
        self._prev_output_1 = 0.0
        self._prev_output_2 = 0.0

    def update(self, price: float, period: float) -> float:
        """Advance the SuperSmoother by one bar using `period`."""
        self._valid_bars += 1

        if self._valid_bars < 4:
            # EasyLanguage: `If Currentbar < 4 Then $SuperSmoother = Price;`
            output = price
        else:
            # Recompute coefficients only when the tuned period changes.
            if period != self._cached_period:
                self._cached_period = period
                self._a0, self._c1, self._c2 = _supersmoother_coefficients(period)

            # Preserve the exact left-to-right arithmetic grouping of
            # `a0*(Price + Price[1]) + c1*$SuperSmoother[1] - c2*$SuperSmoother[2]`.
            output = (
                self._a0 * (price + self._prev_input)
                + self._c1 * self._prev_output_1
                - self._c2 * self._prev_output_2
            )

        # Shift state histories AFTER computing the current bar's output so
        # `[1]` and `[2]` strictly reference prior bars.
        self._prev_input = price
        self._prev_output_2 = self._prev_output_1
        self._prev_output_1 = output
        return output


# =============================================================================
# Master streaming indicator: AdaptiveSuperSmoother
# =============================================================================

class AdaptiveSuperSmoother:
    """Streaming closed-loop Adaptive SuperSmoother and Oscillator.

    Parameters
    ----------
    period0 : int | float, default 20
        Nominal (unadapted) critical period `Period0` of the SuperSmoother.
        Must be a finite positive int or float (excluding bool). Practical
        values are >= 2.0 (the Nyquist period limit).
    rms_length : int, default 81
        Number of 1-bar adaptive SuperSmoother differences (`ROC1 = SS - SS[1]`)
        included in the Root Mean Square (`$RMS`) normalization window.
        Must be an integer >= 1 (excluding bool).

    Algorithmic summary (per bar `t = 0, 1, 2, ...`)
    ------------------------------------------------
    1. Filter `close` through the adaptive `_SuperSmoother` using `self._period`
       computed at the end of bar `t - 1` (initialized to `float(period0)`).
    2. Filter `close` through an independent fixed `_SuperSmoother` using the
       constant base period `float(period0)`.
    3. On bar `t == 0`, no prior adaptive output `SS[1]` exists yet, so record
       `self._prev_ss = ss` and return `(NaN, NaN, NaN, NaN)`.
    4. On bars `t >= 1`, compute the 1-bar slope `roc1 = ss - self._prev_ss`,
       update `self._prev_ss = ss`, and push `roc1` into the fixed-size ring
       buffer of capacity `rms_length`.
    5. While fewer than `rms_length` differences have been collected
       (`t < rms_length`), keep `self._period = float(period0)` and
       `self._roc = 0.0`, and return `(NaN, NaN, NaN, NaN)`.
    6. Once `rms_length` differences exist (`t >= rms_length`):
       - Accumulate `sum_sq = sum(roc1[k]^2 for k = 0 .. rms_length - 1)` from
         newest (`k = 0`) to oldest (`k = rms_length - 1`).
       - Compute `rocrms = sqrt(sum_sq / rms_length)` if `sum_sq != 0.0` else `0.0`.
       - Update the retained series variable `self._roc`:
         if `rocrms != 0.0`, `self._roc = abs(roc1 / rocrms)` (otherwise retain
         prior `self._roc`), then clamp `self._roc = min(self._roc, 2.0)`.
       - Update `self._period` for the next bar:
         `factor = 1.0 - 0.5 * self._roc`
         `self._period = max((self._period0 * factor) * factor, 2.0)`
       - Compute `osc = ss - fixed_ss` and return
         `AdaptiveSuperSmootherResult(ss, fixed_ss, osc, self._period)`.
    """

    def __init__(self, period0: int | float = 20, rms_length: int = 81):
        base_period = _finite_number(period0, "period0")
        if base_period <= 0.0:
            raise ValueError("period0 must be > 0")
        if isinstance(rms_length, bool) or not isinstance(rms_length, int):
            raise TypeError("rms_length must be an integer, excluding bool")
        if rms_length < 1:
            raise ValueError("rms_length must be >= 1")

        # Construction-time parameters exposed as read-only properties.
        self._period0_raw = period0
        self._period0 = base_period
        self._rms_length = rms_length

        # Two independent SuperSmoother instances:
        #   - `_adaptive_ss` corresponds to `SS = $SuperSmoother(Close, Period)`
        #   - `_fixed_ss` corresponds to `Plot1($SuperSmoother(Close, Period0))`
        self._adaptive_ss = _SuperSmoother(base_period)
        self._fixed_ss = _SuperSmoother(base_period)

        # Retained EasyLanguage variables (`Vars: SS(0), Period(20), ROC(0)`).
        # `_period` starts at `Period0` and is held at `Period0` throughout the
        # RMS warmup window.
        self._period = base_period
        self._roc = 0.0
        self._prev_ss = 0.0
        self._has_prev_ss = False

        # Bounded ring buffer storing the `rms_length` most recent `ROC1`
        # differences. `_roc1_count` tracks how many valid differences have
        # been inserted so far (0 .. rms_length).
        self._roc1_ring = [0.0] * rms_length
        self._next_slot = 0
        self._roc1_count = 0

    @property
    def period0(self) -> float:
        """Nominal base critical period `Period0` as an IEEE-754 float."""
        return self._period0

    @property
    def rms_length(self) -> int:
        """Number of `ROC1` bars in the rolling RMS window."""
        return self._rms_length

    @property
    def warmup_bars(self) -> int:
        """Number of leading bars returning NaN (`== rms_length`)."""
        return self._rms_length

    def update(self, close: int | float) -> AdaptiveSuperSmootherResult:
        """Process one bar's close price and return `(ss, fixed_ss, osc, period)`.

        Raises `TypeError` or `ValueError` without modifying internal state if
        `close` is not a finite `int` or `float` (excluding `bool`).
        """
        price = _finite_number(close, "close")

        # ------------------------------------------------------------------
        # Step 1: Update both SuperSmoother filters.
        # Note that `_adaptive_ss` uses `self._period` computed on the PREVIOUS
        # bar (or `self._period0` during warmup), forming Ehlers' closed loop.
        # ------------------------------------------------------------------
        ss = self._adaptive_ss.update(price, self._period)
        fixed_ss = self._fixed_ss.update(price, self._period0)

        # ------------------------------------------------------------------
        # Step 2: Form the one-bar difference `ROC1 = SS - SS[1]` starting on
        # the second bar (0-based index `t >= 1`).
        # ------------------------------------------------------------------
        if not self._has_prev_ss:
            self._prev_ss = ss
            self._has_prev_ss = True
            return AdaptiveSuperSmootherResult(
                math.nan, math.nan, math.nan, math.nan
            )

        roc1 = ss - self._prev_ss
        self._prev_ss = ss

        # Insert `roc1` into the fixed-size circular buffer.
        capacity = self._rms_length
        self._roc1_ring[self._next_slot] = roc1
        self._next_slot = (self._next_slot + 1) % capacity
        if self._roc1_count < capacity:
            self._roc1_count += 1

        # ------------------------------------------------------------------
        # Step 3: Gate output until a full window of `rms_length` differences
        # has been accumulated (0-based bar index `t == rms_length`).
        # While unprimed, `self._period` remains at `self._period0`.
        # ------------------------------------------------------------------
        if self._roc1_count < capacity:
            return AdaptiveSuperSmootherResult(
                math.nan, math.nan, math.nan, math.nan
            )

        # ------------------------------------------------------------------
        # Step 4: Compute `$RMS(ROC1, rms_length)` (Code Listing 3).
        # Traverse newest-to-oldest (`count = 0 .. capacity - 1`).
        # Adding `capacity` before subtracting `count` keeps the dividend
        # nonnegative so ports to Go, Rust, C, and Zig never hit negative
        # modulo semantics or unsigned integer underflow.
        # ------------------------------------------------------------------
        sum_sq = 0.0
        newest = (self._next_slot + capacity - 1) % capacity
        for count in range(capacity):
            value = self._roc1_ring[(newest + capacity - count) % capacity]
            sum_sq = sum_sq + value * value

        if sum_sq != 0.0:
            rocrms = math.sqrt(sum_sq / capacity)
        else:
            rocrms = 0.0

        # ------------------------------------------------------------------
        # Step 5: Scale `ROC1` in standard deviations and clamp at 2.0
        # (Code Listing 1):
        #   If ROCRMS <> 0 Then ROC = AbsValue(ROC1 / ROCRMS);
        #   If ROC > 2 Then ROC = 2;
        # Notice that `ROC` is a retained series variable: if `rocrms == 0.0`,
        # `self._roc` keeps its previous value rather than resetting to zero.
        # ------------------------------------------------------------------
        if rocrms != 0.0:
            self._roc = abs(roc1 / rocrms)
        if self._roc > 2.0:
            self._roc = 2.0

        # ------------------------------------------------------------------
        # Step 6: Quadratic period tuning for the NEXT bar, floored at 2.0
        # (Code Listing 1):
        #   Period = Period0*(1 - .5*ROC)*(1 - .5*ROC);
        #   If Period < 2 Then Period = 2;
        # Preserve left-to-right multiplication `(Period0 * factor) * factor`.
        # ------------------------------------------------------------------
        factor = 1.0 - 0.5 * self._roc
        period = (self._period0 * factor) * factor
        if period < 2.0:
            period = 2.0
        self._period = period

        # ------------------------------------------------------------------
        # Step 7: Oscillator is adaptive minus fixed (`SS - SS_fixed`).
        # ------------------------------------------------------------------
        osc = ss - fixed_ss
        return AdaptiveSuperSmootherResult(ss, fixed_ss, osc, period)


# =============================================================================
# Confirmed reference grid (16 combinations x 4 outputs = 64 arrays)
# =============================================================================

# Confirmed with the user: 16 `(period0, rms_length, explanation)` cases.
REFERENCE_CASES = (
    (20, 81, "TASC article and MESA code defaults"),
    (10, 81, "Ehlers' standard 10-bar aliasing-noise period"),
    (12, 81, "Article's 12-bar critical period benchmark"),
    (4, 81, "WealthLab optimizer minimum period"),
    (2, 81, "Nyquist floor period (Period >= 2 lower clamp boundary)"),
    (30, 81, "Medium-long base period"),
    (40, 81, "WealthLab optimizer maximum period"),
    (60, 81, "Long trend-smoothing base period"),
    (20, 2, "Minimum RMS window (Pine Script lower bound, frequent 2-sigma capping)"),
    (20, 10, "Short 10-bar RMS window"),
    (20, 20, "Equal base period and RMS window"),
    (20, 50, "Intermediate 50-bar RMS window"),
    (20, 120, "Long 120-bar RMS window"),
    (14, 20, "Short-medium period with 20-bar RMS window"),
    (12.5, 81, "Non-integer base period exercising _ decimal formatting"),
    (20, 251, "Full-dataset RMS window boundary on 252 closes"),
)

# Map `(attribute_name, array_suffix)` for the 4 outputs per parameter case.
OUTPUT_SPECS = (
    ("ss", "SS"),
    ("fixed_ss", "FIXED"),
    ("osc", "OSC"),
    ("period", "PERIOD"),
)

DATA_FILES = (
    "test_testdata.py",
    "testdata_test.go",
    "testdata.ts",
    "testdata.rs",
    "testdata.zig",
)
BEGIN_MARKER = "BEGIN GENERATED ADAPTIVE SUPER SMOOTHER REFERENCE DATA"
END_MARKER = "END GENERATED ADAPTIVE SUPER SMOOTHER REFERENCE DATA"
HERE = Path(__file__).resolve().parent


def _parameter_text(value: int | float) -> str:
    """Format an int or float parameter cleanly without trailing `.0` on ints."""
    return str(value) if isinstance(value, int) else format(value, "g")


def parameter_tag(period0: int | float, rms_length: int) -> str:
    """Build the portable parameter tag, e.g. `P20_R81` or `P12_5_R81`."""
    p_str = _parameter_text(period0).replace(".", "_")
    r_str = _parameter_text(rms_length).replace(".", "_")
    return f"P{p_str}_R{r_str}"


def read_input_close() -> list[float]:
    """Parse `INPUT_CLOSE` from `test_testdata.py` via `ast.literal_eval`."""
    tree = ast.parse((HERE / DATA_FILES[0]).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "INPUT_CLOSE"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError("INPUT_CLOSE missing from test_testdata.py")


def compute_reference_vectors(closes: list[float]):
    """Run all 16 confirmed configurations on `closes` and collect 64 vectors."""
    vectors = []
    for period0, rms_length, explanation in REFERENCE_CASES:
        indicator = AdaptiveSuperSmoother(period0=period0, rms_length=rms_length)
        results = [indicator.update(close) for close in closes]
        parameters = (
            f"period0={_parameter_text(period0)}, rms_length={rms_length}"
        )
        tag = parameter_tag(period0, rms_length)
        for attr, suffix in OUTPUT_SPECS:
            name = f"EXPECTED_{tag}_{suffix}"
            values = [getattr(result, attr) for result in results]
            vectors.append((name, explanation, parameters, values))
    return vectors


def _rows(tokens: list[str], indent: str) -> str:
    """Format 10 comma-separated tokens per line."""
    return "\n".join(
        indent + ", ".join(tokens[start:start + 10]) + ","
        for start in range(0, len(tokens), 10)
    )


def _replace_generated(
    path: Path, body: str, prefix: str, inside_rust_module: bool = False
) -> None:
    """Insert or replace the marked generated section in `path`."""
    text = path.read_text(encoding="utf-8")
    begin = prefix + BEGIN_MARKER
    end = prefix + END_MARKER
    section = begin + "\n" + body + "\n" + end + "\n"
    pattern = re.compile(re.escape(begin) + r"\n.*?" + re.escape(end) + r"\n?", re.S)
    matches = list(pattern.finditer(text))
    if matches:
        if len(matches) != 1:
            raise ValueError(f"Multiple generated sections in {path.name}")
        text = pattern.sub(lambda _match: section, text, count=1)
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
    """Read the 64 serialized reference arrays and comments from Python master."""
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
    expected_count = len(REFERENCE_CASES) * len(OUTPUT_SPECS)
    if len(vectors) != expected_count:
        raise ValueError(
            f"Expected {expected_count} reference arrays, found {len(vectors)}"
        )
    return vectors


def generate_reference_data(closes: list[float]) -> None:
    """Generate all 64 expected reference arrays across the 5 language files."""
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

    # Read back the serialized decimal tokens from `test_testdata.py` so every
    # other language file uses the exact same decimal strings.
    vectors = read_serialized_vectors()
    for filename, language in zip(DATA_FILES[1:], ("go", "ts", "rs", "zig")):
        path = HERE / filename
        if language == "go":
            text = path.read_text(encoding="utf-8")
            text = re.sub(r"(?m)^package \w+$", "package adaptivesupersmoother", text)
            if 'import "math"' not in text:
                text = text.replace(
                    "package adaptivesupersmoother\n",
                    'package adaptivesupersmoother\n\nimport "math"\n',
                    1,
                )
            path.write_text(text, encoding="utf-8")
        elif language == "zig":
            text = path.read_text(encoding="utf-8")
            zig_header = 'const math = @import("std").math;\nconst nan = math.nan(f64);\n'
            if not text.startswith(zig_header):
                raise ValueError("testdata.zig is missing std.math / nan header")

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
                block = (
                    f"pub fn expected_{tag.lower()}() -> Vec<f64> {{\n"
                    f"    vec![\n{body}\n    ]\n}}"
                )
            else:
                body = _rows(["nan" if t == "NaN" else t for t in tokens], "        ")
                block = (
                    f"pub fn expected{tag}() [252]f64 {{\n"
                    f"    return .{{\n{body}\n    }};\n}}"
                )
            rendered = comments + block
            if language == "rs":
                rendered = "\n".join("    " + line for line in rendered.splitlines())
            blocks.append(rendered)
        _replace_generated(
            path,
            "\n\n".join(blocks),
            "// ",
            inside_rust_module=(language == "rs"),
        )
    print(
        f"Generated {len(vectors)} arrays x 252 values in each of the five language files."
    )


def main(closes: list[float]) -> None:
    """Run streaming example, regenerate reference data, or run verification."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--generate",
        action="store_true",
        help="update the 64 confirmed reference arrays in all five files",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="run numerical, serialization, and cross-language parity tests",
    )
    args = parser.parse_args()
    if len(closes) != 252 or closes != read_input_close():
        raise ValueError("Embedded INPUT_CLOSE differs from the template")

    if args.generate:
        generate_reference_data(closes)
    if args.verify:
        suite = unittest.defaultTestLoader.discover(
            str(HERE), pattern="test_adaptive_super_smoother.py"
        )
        outcome = unittest.TextTestRunner(verbosity=2).run(suite)
        if not outcome.wasSuccessful():
            raise SystemExit(1)
    if not args.generate and not args.verify:
        indicator = AdaptiveSuperSmoother(period0=20, rms_length=81)
        print("Article defaults: period0=20, rms_length=81")
        print(
            "index  close       ss                   fixed_ss             "
            "osc                  period"
        )
        for index, close in enumerate(closes):
            result = indicator.update(close)
            if index in (0, 80, 81, 82, 83, 84, 250, 251):
                print(
                    f"{index:5d}  {close:10.6f}  {result.ss: .15f}  "
                    f"{result.fixed_ss: .15f}  {result.osc: .15f}  "
                    f"{result.period: .15f}"
                )
        print(
            "\nConfirmed grid: 16 combinations, 4 outputs, 64 arrays per language."
        )
        for period0, rms_length, explanation in REFERENCE_CASES:
            print(f"  {parameter_tag(period0, rms_length):14s} {explanation}")
        print(
            "Use --generate to regenerate, or --verify to check the saved references."
        )


if __name__ == "__main__":
    # The 252 INPUT_CLOSE values from test_testdata.py are embedded directly in
    # __main__ for standalone execution and checked against test_testdata.py on
    # every run.
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
