"""Ehlers autocorrelation periodogram: streaming research master, stdlib only.

Default: TASC September 2016, "Measuring Market Cycles", EasyLanguage sidebar.
source="book": corrected Cycle Analytics for Traders (2013), Listing 8-3.
Both return a structured heatmap AND the thresholded dominant-cycle centroid.
Full-precision pi, sqrt(2), and 1/sqrt(2) replace printed approximations.

Read description.md for equations, source differences, startup, and port rules.
All source state starts at zero and advances during public warm-up. Correlation
is retained when its denominator is nonpositive, as in both source listings.
NaN input is skipped; infinity and overflowing calculations raise ValueError.

The user confirmed all combinations. The 64-case Cartesian product is two
sources x four period ranges x four averaging modes x two enhancement settings.
__main__ embeds the original 252 closes. --generate-reference-data writes and
verifies Python expected arrays, then translates those arrays to Go/TS/Rust/Zig.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import math
from pathlib import Path
from typing import NamedTuple


TWO_PI = 2.0 * math.pi
SQRT_TWO = math.sqrt(2.0)
INVERSE_SQRT_TWO = 1.0 / SQRT_TWO
DFT_LAG_START = 3
POWER_SMOOTHING = 0.2  # Design setting, not a truncated mathematical constant.
BOOK_AGC_DECAY = 0.995  # Listing 8-3 code; its prose inconsistently says 0.991.


class Heatmap(NamedTuple):
    """One independently owned heatmap column, compatible with zpano's fields.

    values[i] belongs to parameter_first + i * parameter_resolution. Runtime
    unavailable columns have values=[] and NaN extrema. No RGB quantization.
    time is caller-supplied metadata; it does not participate in calculations.
    The list is a snapshot, never reused as internal recursive state.
    """

    time: datetime.datetime | None
    parameter_first: float
    parameter_last: float
    parameter_resolution: float
    value_min: float
    value_max: float
    values: list[float]

    def is_empty(self) -> bool:
        return len(self.values) == 0

    @staticmethod
    def empty(time: datetime.datetime | None, first: int, last: int) -> Heatmap:
        return Heatmap(time, float(first), float(last), 1.0, math.nan, math.nan, [])


class PeriodogramOutput(NamedTuple):
    """Dominant cycle is a real-valued period in bars; do not round to an int."""

    heatmap: Heatmap
    dominant_cycle: float


class Parameters(NamedTuple):
    """Resolved, immutable configuration; zero averaging means M=current lag."""

    source: str
    min_period: int
    max_period: int
    averaging_length: int
    enhance_resolution: bool


class PeriodogramState(NamedTuple):
    """Read-only diagnostics for checking a port, including masked startup state.

    correlations uses lag indices 0..max_period. smoothed_power uses period
    bins min_period..max_period. Both snapshots are immutable tuples.
    internal_dominant_cycle is the persistent source variable, initially 0;
    public dominant_cycle is NaN until history is primed and a centroid exists.
    """

    high_pass: float
    filtered: float
    correlations: tuple[float, ...]
    smoothed_power: tuple[float, ...]
    normalization_maximum: float
    internal_dominant_cycle: float


class AutoCorrelationPeriodogram:
    """Causal scalar indicator with bounded history and source-specific behavior.

    min_period: integer >=3; None selects 8 for article or 10 for book.
    max_period: integer >=5 and greater than min_period; default 48.
    averaging_length: 0 (lag-dependent) or integer >=2; default 3.
    enhance_resolution: boolean, default False. Article cubes power before
        the centroid; book squares only the heatmap after the centroid.
    source: "article" (default) or "book". The book Fourier basis uses 2*pi,
        correcting the local Listing 8-3's 370-degree anomaly.

    The cutoff periods track min_period/max_period when generalized, as in the
    copied implementation. EMA 0.2, book AGC 0.995 and thresholds are fixed.
    No minimum-subtraction normalization or disable flags are introduced.
    O(max_period * (number_of_bins + largest_M)) work per accepted sample.
    """

    def __init__(self, min_period: int | None = None, max_period: int = 48,
                 averaging_length: int = 3, enhance_resolution: bool = False,
                 source: str = "article") -> None:
        if source not in ("article", "book"):
            raise ValueError('source must be "article" or "book"')
        if min_period is None:
            min_period = 8 if source == "article" else 10
        for name, value in (("min_period", min_period), ("max_period", max_period),
                            ("averaging_length", averaging_length)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
        if min_period < 3:
            raise ValueError("min_period must be at least 3 (strictly above Nyquist)")
        if max_period < 5 or max_period <= min_period:
            raise ValueError("max_period must be at least 5 and greater than min_period")
        if averaging_length != 0 and averaging_length < 2:
            raise ValueError("averaging_length must be zero or at least 2")
        if not isinstance(enhance_resolution, bool):
            raise ValueError("enhance_resolution must be a boolean")

        self._parameters = Parameters(source, min_period, max_period,
                                      averaging_length, enhance_resolution)
        # Coefficients are evaluated once, with binary64 math and radian angles.
        # Never use integer division for either cutoff or the Fourier basis.
        try:
            theta = TWO_PI / max_period
            if source == "article":
                pole = (1.0 - math.sin(theta)) / math.cos(theta)
                self._hp0 = 0.5 * (1.0 + pole)
                self._hp1 = pole
                self._hp2 = 0.0
            else:
                theta = INVERSE_SQRT_TWO * TWO_PI / max_period
                alpha = (math.cos(theta) + math.sin(theta) - 1.0) / math.cos(theta)
                pole = 1.0 - alpha
                self._hp0 = (1.0 - alpha / 2.0) * (1.0 - alpha / 2.0)
                self._hp1 = 2.0 * pole
                self._hp2 = pole * pole
            a = math.exp(-SQRT_TWO * math.pi / min_period)
            self._ss2 = 2.0 * a * math.cos(SQRT_TWO * math.pi / min_period)
            self._ss3 = -a * a
            self._ss1 = 1.0 - self._ss2 - self._ss3
        except (OverflowError, ZeroDivisionError) as error:
            raise ValueError("periods must yield finite stable coefficients") from error
        if not (0.0 < pole < 1.0 and 0.0 < a < 1.0 and self._ss1 > 0.0):
            raise ValueError("periods must yield finite stable coefficients")

        # The oldest Pearson sample is filt[max_period + M - 1]. A lag-dependent
        # window has M=max_period at the largest lag, needing 2*max_period slots.
        self._history_length = max_period + (averaging_length or max_period)
        # Keep at least three SS slots even for unusually short custom settings.
        self._history_length = max(3, self._history_length)
        self._cosines = []
        self._sines = []
        for period in range(min_period, max_period + 1):
            self._cosines.append(tuple(math.cos(TWO_PI * lag / period)
                                       for lag in range(DFT_LAG_START, max_period + 1)))
            self._sines.append(tuple(math.sin(TWO_PI * lag / period)
                                     for lag in range(DFT_LAG_START, max_period + 1)))
        self.reset()

    @property
    def parameters(self) -> Parameters:
        return self._parameters

    @property
    def warmup_bars(self) -> int:
        """Number of leading unavailable rows / first available zero-based index."""
        return self._history_length - 1

    @property
    def samples_seen(self) -> int:
        return self._samples_seen

    @property
    def is_primed(self) -> bool:
        """History availability, independent of whether a useful cycle exists."""
        return self._samples_seen >= self._history_length

    @property
    def state(self) -> PeriodogramState:
        return self._state

    @property
    def output(self) -> PeriodogramOutput:
        """Last accepted finite sample's output; a skipped NaN does not change it."""
        return self._output

    def reset(self) -> None:
        """Begin an independent run, including zero raw-price prehistory.

        This explicit research convention mirrors the investigation. A positive
        constant price therefore has a startup transient from zero; replacing
        the two absent prices with the first actual price would change fixtures.
        """
        p = self.parameters
        self._samples_seen = 0
        self._close1 = self._close2 = self._high1 = self._high2 = 0.0
        self._filtered = [0.0] * self._history_length  # Newest-to-oldest slots.
        self._correlations = [0.0] * (p.max_period + 1)
        self._power = [0.0] * (p.max_period - p.min_period + 1)
        self._maximum = self._dominant = 0.0
        self._has_dominant = False
        self._state = PeriodogramState(0.0, 0.0, tuple(self._correlations),
                                      tuple(self._power), 0.0, 0.0)
        self._output = PeriodogramOutput(Heatmap.empty(None, p.min_period, p.max_period), math.nan)

    def update(self, sample: float, time: datetime.datetime | None = None) -> PeriodogramOutput:
        """Consume one finalized sample, oldest to newest, exactly once.

        No future samples, framework entities, arrays, or timestamps are needed.
        NaN emits an unavailable result and advances no state or warm-up count.
        Candidate arithmetic is local until the final commit, so rejected
        infinity/overflow cannot contaminate an otherwise valid streaming run.
        """
        price = float(sample)
        p = self.parameters
        if math.isnan(price):
            return PeriodogramOutput(Heatmap.empty(time, p.min_period, p.max_period), math.nan)
        if not math.isfinite(price):
            raise ValueError("sample must be finite or NaN (skipped)")

        # Evaluate using PREVIOUS states. The second price difference belongs
        # only to the book's two-pole HP; article uses the first difference.
        if p.source == "article":
            high = self._hp0 * (price - self._close1) + self._hp1 * self._high1
        else:
            high = (self._hp0 * (price - 2.0 * self._close1 + self._close2)
                    + self._hp1 * self._high1 - self._hp2 * self._high2)
        filtered_value = (self._ss1 * (high + self._high1) / 2.0
                          + self._ss2 * self._filtered[0] + self._ss3 * self._filtered[1])
        if not (math.isfinite(high) and math.isfinite(filtered_value)):
            raise ValueError("filter arithmetic overflowed")
        filtered = [filtered_value] + self._filtered[:-1]

        # Raw Pearson correlations are NOT rescaled to [0,1] here. That mapping
        # belongs to the separate Autocorrelation Indicator (book Listing 8-2).
        # Preserve source operation order and visit samples newest to oldest.
        correlations = self._correlations[:]
        for lag in range(p.max_period + 1):
            m = p.averaging_length if p.averaging_length != 0 else lag
            sx = sy = sxx = syy = sxy = 0.0
            for count in range(m):
                x = filtered[count]
                y = filtered[lag + count]  # BOTH windows go backward in time.
                sx += x
                sy += y
                sxx += x * x
                sxy += x * y
                syy += y * y
            denominator = (m * sxx - sx * sx) * (m * syy - sy * sy)
            if not all(math.isfinite(v) for v in (sx, sy, sxx, syy, sxy, denominator)):
                raise ValueError("Pearson arithmetic overflowed")
            if denominator > 0.0:
                correlations[lag] = (m * sxy - sx * sy) / math.sqrt(denominator)
            # Else retain the previous RAW correlation, as the source arrays
            # do. Do not introduce a variance epsilon, clamping, or zero reset.
            if not math.isfinite(correlations[lag]):
                raise ValueError("Pearson correlation overflowed")

        # DFT across LAG, then EMA across TIME independently for each period.
        # Q is already magnitude squared; the source explicitly squares Q again.
        power = []
        for bin_index in range(len(self._power)):
            cosine_part = sine_part = 0.0
            for offset, lag in enumerate(range(DFT_LAG_START, p.max_period + 1)):
                cosine_part += correlations[lag] * self._cosines[bin_index][offset]
                sine_part += correlations[lag] * self._sines[bin_index][offset]
            squared_sum = cosine_part * cosine_part + sine_part * sine_part
            smoothed = (POWER_SMOOTHING * squared_sum * squared_sum
                        + 0.8 * self._power[bin_index])
            if not math.isfinite(smoothed):
                raise ValueError("spectral arithmetic overflowed")
            power.append(smoothed)

        # The ARTICLE resets the denominator every sample; the BOOK remembers
        # its fast-attack/slow-decay maximum. No floating minimum subtraction.
        maximum = BOOK_AGC_DECAY * self._maximum if p.source == "book" else 0.0
        for value in power:
            if value > maximum:
                maximum = value
        normalized = [value / maximum if maximum > 0.0 else 0.0 for value in power]

        # Article enhancement is upstream of BOTH the centroid and display.
        # Book enhancement is downstream of the centroid and changes only display.
        weights = normalized
        if p.source == "article" and p.enhance_resolution:
            weights = [value * value * value for value in normalized]
        threshold = 0.25 if p.source == "article" else 0.5
        peak = max(weights)
        sp = spx = 0.0
        for bin_index, weight in enumerate(weights):
            if weight >= threshold and (p.source == "book" or peak >= 0.25):
                spx += (p.min_period + bin_index) * weight
                sp += weight
        dominant = self._dominant
        has_dominant = self._has_dominant
        # Article's Sp<0.25 hold branch is explicit. Book holds when Sp==0.
        if sp != 0.0 and (p.source == "book" or sp >= 0.25):
            dominant = spx / sp
            has_dominant = True
        if not math.isfinite(dominant):
            raise ValueError("dominant-cycle arithmetic overflowed")
        values = weights[:]
        if p.source == "book" and p.enhance_resolution:
            values = [value * value for value in normalized]

        # Commit finite source state even when the public result is unavailable.
        # Public NaNs NEVER enter Pearson, EMA, AGC, or dominant hold state.
        self._close2, self._close1 = self._close1, price
        self._high2, self._high1 = self._high1, high
        self._filtered, self._correlations, self._power = filtered, correlations, power
        self._maximum, self._dominant, self._has_dominant = maximum, dominant, has_dominant
        self._samples_seen += 1
        self._state = PeriodogramState(high, filtered_value, tuple(correlations),
                                      tuple(power), maximum, dominant)
        if self.is_primed:
            heatmap = Heatmap(time, float(p.min_period), float(p.max_period), 1.0,
                              min(values), max(values), values)
            public_dominant = dominant if has_dominant else math.nan
        else:
            heatmap = Heatmap.empty(time, p.min_period, p.max_period)
            public_dominant = math.nan
        self._output = PeriodogramOutput(heatmap, public_dominant)
        return self._output


class ReferenceCase(NamedTuple):
    source: str
    min_period: int
    max_period: int
    averaging_length: int
    enhance_resolution: bool
    what_it_tests: str


# Confirmation in this conversation applies to the full 64-case product.
# Fixed EMA/AGC coefficients and centroid thresholds are source design choices,
# not exposed axes. E=1 means article cube or book display square respectively.
REFERENCE_CASES_CONFIRMED = True
REFERENCE_CASES = tuple(
    ReferenceCase(source, first, last, average, enhanced,
                  f"{'Article: one-pole HP/current maximum/0.25 centroid' if source == 'article' else 'Corrected book: two-pole HP/0.995 AGC/0.5 centroid'}; "
                  f"{first}-{last} period range; "
                  f"{'lag-dependent Pearson windows' if average == 0 else str(average) + '-sample Pearson windows'}; "
                  f"{'article cube before centroid' if source == 'article' and enhanced else 'book display square after centroid' if enhanced else 'unenhanced spectrum'}.")
    for source in ("article", "book")
    for first, last in ((8, 24), (8, 48), (10, 48), (16, 64))
    for average in (0, 3, 5, 10)
    for enhanced in (False, True)
)


def _case_suffix(case: ReferenceCase) -> str:
    # V0=article, V1=corrected book; L/H=period bounds, A=averaging, E=enhancement.
    return (f"V{int(case.source == 'book')}_L{case.min_period}_H{case.max_period}"
            f"_A{case.averaging_length}_E{int(case.enhance_resolution)}")


def _parameter_comment(case: ReferenceCase) -> str:
    return (f"source={case.source}; min_period={case.min_period}; max_period={case.max_period}; "
            f"averaging_length={case.averaging_length}; enhance_resolution={case.enhance_resolution}")


def _float_literal(value: float, nan: str) -> str:
    """Only serialized text is rounded to 15 significant digits, never state."""
    if math.isnan(value):
        return nan
    if not math.isfinite(value):
        raise ValueError("reference data must contain finite values or NaN")
    literal = format(value, ".15g")
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"  # Explicit float syntax for Rust and Zig.
    return literal


def _array_body(values: list, indent: str, nan: str, language: str) -> str:
    """Serialize a scalar series or a rectangular time-major heatmap matrix."""
    if values and isinstance(values[0], list):
        opening, closing = {"py": ("[", "]"), "go": ("{", "}"),
                            "ts": ("[", "]"), "rs": ("vec![", "]"),
                            "zig": (".{", "}")}[language]
        return "\n".join(indent + opening + ", ".join(_float_literal(v, nan) for v in row)
                         + closing + "," for row in values)
    tokens = [_float_literal(v, nan) for v in values]
    return "\n".join(indent + ", ".join(tokens[i:i + 6]) + ","
                     for i in range(0, len(tokens), 6))


def _load_python_arrays(path: Path) -> dict[str, list]:
    """Read numeric literals without executing fixture imports or arbitrary code."""
    def decode(node):
        if isinstance(node, ast.List):
            return [decode(child) for child in node.elts]
        if isinstance(node, ast.Name) and node.id == "NaN":
            return math.nan
        return float(ast.literal_eval(node))
    result = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    result[target.id] = decode(node.value)
    return result


def _write_generated_section(path: Path, section: str, comment: str) -> None:
    """Append expected arrays; on reruns replace only this marked section."""
    begin = f"{comment} BEGIN GENERATED AUTOCORRELATION PERIODOGRAM EXPECTED DATA"
    end = f"{comment} END GENERATED AUTOCORRELATION PERIODOGRAM EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    block = begin + "\n\n" + section.rstrip() + "\n\n" + end
    if begin in original:
        start = original.index(begin)
        finish = original.index(end, start) + len(end)
        text = original[:start] + block + original[finish:]
    else:
        text = original.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8")


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Compute Python arrays, reopen/verify them, translate to four languages.

    Each case exports DC, HEATMAP, MIN, MAX. All arrays have 252 time rows;
    HEATMAP rows have H-L+1 bins ordered shortest to longest. Empty runtime
    columns become full NaN rows for fixed-size language fixtures.
    """
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError("reference cases must be confirmed before generation")
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 inputs and at most 64 cases")
    python_path = directory / "test_testdata.py"
    if _load_python_arrays(python_path)["INPUT_CLOSE"] != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from the copied fixture")
    outputs = {}
    sections = ["# NaN marks unavailable output; it is never recursive state.\nNaN = math.nan"]
    for case in REFERENCE_CASES:
        indicator = AutoCorrelationPeriodogram(case.min_period, case.max_period,
                                              case.averaging_length, case.enhance_resolution, case.source)
        results = [indicator.update(value) for value in input_close]
        bins = case.max_period - case.min_period + 1
        arrays = {
            "DC": [r.dominant_cycle for r in results],
            "HEATMAP": [r.heatmap.values if not r.heatmap.is_empty() else [math.nan] * bins for r in results],
            "MIN": [r.heatmap.value_min for r in results],
            "MAX": [r.heatmap.value_max for r in results],
        }
        for component, values in arrays.items():
            name = "EXPECTED_" + _case_suffix(case) + "_" + component
            if name in outputs:
                raise ValueError("duplicate reference array name")
            outputs[name] = values
            sections.append(f"# {case.what_it_tests}\n# {_parameter_comment(case)}\n"
                            + f"{name} = [\n{_array_body(values, '    ', 'NaN', 'py')}\n]")
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # Reopen the Python source: it is the authoritative 15-digit dataset.
    # Other languages serialize these reopened literals, never fresh runs.
    written = _load_python_arrays(python_path)
    if {k for k in written if k.startswith("EXPECTED_")} != set(outputs):
        raise ValueError("Python fixture expected arrays are incomplete")
    for name, raw in outputs.items():
        actual = written[name]
        if len(actual) != 252:
            raise ValueError(f"{name} must contain 252 rows")
        raw_flat = [v for row in raw for v in row] if name.endswith("_HEATMAP") else raw
        flat = [v for row in actual for v in row] if name.endswith("_HEATMAP") else actual
        if len(flat) != len(raw_flat):
            raise ValueError(f"{name} has incorrect matrix dimensions")
        for original, literal in zip(raw_flat, flat):
            if math.isnan(original):
                if not math.isnan(literal):
                    raise ValueError(f"{name} has incorrect NaN masks")
            elif literal != float(_float_literal(original, "NaN")):
                raise ValueError(f"{name} has incorrect 15-digit values")

    go_path = directory / "testdata_test.go"
    go_text = go_path.read_text(encoding="utf-8").replace("package xxxx", "package autocorrelationperiodogram", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace("package autocorrelationperiodogram\n",
                                  'package autocorrelationperiodogram\n\nimport "math"\n', 1)
    go_path.write_text(go_text, encoding="utf-8")
    zig_path = directory / "testdata.zig"
    zig_text = zig_path.read_text(encoding="utf-8")
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n' + zig_text
    if "const nan = math.nan(f64);" not in zig_text:
        zig_text = zig_text.replace('const math = @import("std").math;\n',
                                    'const math = @import("std").math;\nconst nan = math.nan(f64);\n', 1)
    zig_path.write_text(zig_text, encoding="utf-8")

    translated = {language: [] for language in ("go", "ts", "rs", "zig")}
    for case in REFERENCE_CASES:
        bins = case.max_period - case.min_period + 1
        for component in ("DC", "HEATMAP", "MIN", "MAX"):
            suffix = _case_suffix(case) + "_" + component
            values = written["EXPECTED_" + suffix]
            matrix = component == "HEATMAP"
            comments = f"// {case.what_it_tests}\n// {_parameter_comment(case)}\n"
            go_type = "[][]float64" if matrix else "[]float64"
            ts_type = "number[][]" if matrix else "number[]"
            rs_type = "Vec<Vec<f64>>" if matrix else "Vec<f64>"
            zig_type = f"[252][{bins}]f64" if matrix else "[252]f64"
            translated["go"].append(comments + f"var expected{suffix} = {go_type}{{\n"
                                    + _array_body(values, "\t", "math.NaN()", "go") + "\n}")
            translated["ts"].append(comments + f"export const expected{suffix}: {ts_type} = [\n"
                                    + _array_body(values, "    ", "NaN", "ts") + "\n];")
            translated["rs"].append(comments + f"pub fn expected_{suffix.lower()}() -> {rs_type} {{\n    vec![\n"
                                    + _array_body(values, "        ", "f64::NAN", "rs") + "\n    ]\n}")
            translated["zig"].append(comments + f"pub fn expected{suffix}() {zig_type} {{\n    return .{{\n"
                                     + _array_body(values, "        ", "nan", "zig") + "\n    };\n}")
    for language, filename in (("go", "testdata_test.go"), ("ts", "testdata.ts"),
                               ("rs", "testdata.rs"), ("zig", "testdata.zig")):
        _write_generated_section(directory / filename, "\n\n".join(translated[language]), "//")
    print(f"Verified {len(outputs)} Python expected arrays for {len(REFERENCE_CASES)} cases; wrote all five languages.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true")
    arguments = parser.parse_args()
    # INPUT_CLOSE is embedded below, identical to the shared 252-close fixture.
    # Running an example or generating fixtures requires no outside repository.
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
    indicator = AutoCorrelationPeriodogram()
    outputs = [indicator.update(value) for value in INPUT_CLOSE]
    print("Default parameters:", indicator.parameters)
    print("First available index:", indicator.warmup_bars)
    if outputs:
        print("Final dominant cycle:", outputs[-1].dominant_cycle)
        print("Final heatmap:", outputs[-1].heatmap)
    print(f"Confirmed reference combinations: {len(REFERENCE_CASES)}")
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
