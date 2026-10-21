"""GriffithsPredictor: standalone streaming research master, standard library only.

Read description.md for full equations, source variants and startup semantics.
Full-precision sqrt(2) and pi replace the printed rounded constants.
The user confirmed all 48 combinations: 32 predictor, 8 spectrum, 8 dominant cycle.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import math
from pathlib import Path
from typing import NamedTuple


SQRT_TWO = math.sqrt(2.0)
TWO_PI = 2.0 * math.pi
AGC_DECAY = 0.991  # A design parameter; keep this exact printed decimal.
POWER_SCALE = 0.1  # Also the spectrum's new-power smoothing weight.
POWER_MEMORY = 0.9
MAX_CYCLE_CHANGE = 2.0


class Heatmap(NamedTuple):
    """A single heatmap column with zpano-compatible metadata and owned values.

    values[i] is the power at parameter_first + i * parameter_resolution.
    time is optional caller metadata, never an input to the DSP calculation.
    Empty public columns use [] and NaN extrema. Values are not RGB colors.
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
    def empty(time: datetime.datetime | None, first: int, last: int,
              resolution: float = 1.0) -> Heatmap:
        return Heatmap(time, float(first), float(last), resolution,
                       math.nan, math.nan, [])


class AdaptiveState(NamedTuple):
    """Immutable diagnostics, including internal state during public warm-up.

    coefficients is ONE-BASED: index zero and the final coefficient stay zero.
    The final coefficient has a fixed zero regressor in the published code.
    """

    accepted_samples: int
    high_pass: float
    filtered: float
    peak: float
    signal: float
    fitted_value: float
    coefficients: tuple[float, ...]


def _integer(name: str, value: int, minimum: int, maximum: int) -> None:
    # bool subclasses int in Python; do not silently accept it as a period.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}]")


class _AdaptiveCore:
    """Shared equations copied into each independent conversion folder.

    Arrays deliberately retain EasyLanguage's one-based tap indices to avoid
    translating c[1] into a lag-zero coefficient by mistake. Real observations
    are retained separately from the predictor's disposable future window.
    """

    def __init__(self, lower_bound: int, upper_bound: int, length: int,
                 array_limit: int) -> None:
        _integer("lower_bound", lower_bound, 3, array_limit)
        _integer("upper_bound", upper_bound, 4, array_limit)
        _integer("length", length, 2, array_limit)
        if lower_bound >= upper_bound:
            raise ValueError("lower_bound must be less than upper_bound")
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._length = length
        self._mu = 1.0 / length  # Floating-point division is essential in ports.
        self._prime_count = max(4, length)

        # Both filters use the same second-order poles but different numerators.
        # Python's sin/cos expect radians; EasyLanguage's functions use degrees.
        hp_angle = SQRT_TWO * math.pi / upper_bound
        hp_a = math.exp(-hp_angle)
        self._hp2 = 2.0 * hp_a * math.cos(hp_angle)
        self._hp3 = -hp_a * hp_a
        self._hp1 = (1.0 + self._hp2 - self._hp3) / 4.0
        ss_angle = SQRT_TWO * math.pi / lower_bound
        ss_a = math.exp(-ss_angle)
        self._ss2 = 2.0 * ss_a * math.cos(ss_angle)
        self._ss3 = -ss_a * ss_a
        self._ss1 = 1.0 - self._ss2 - self._ss3
        self.reset()

    @property
    def lower_bound(self) -> int:
        return self._lower_bound

    @property
    def upper_bound(self) -> int:
        return self._upper_bound

    @property
    def length(self) -> int:
        return self._length

    @property
    def primed(self) -> bool:
        # Priming means sufficient history, not convergence or predictive skill.
        return self._count >= self._prime_count

    @property
    def state(self) -> AdaptiveState:
        return AdaptiveState(self._count, self._hp_previous, self._lp_previous,
                             self._peak, self._signal, self._xbar,
                             tuple(self._coefficients))

    def reset(self) -> None:
        # Reproduce the explicit source initial conditions. No first-price seed.
        self._count = 0
        self._price_previous = self._price_older = 0.0
        self._hp_previous = self._hp_older = 0.0
        self._lp_previous = self._lp_older = 0.0
        self._peak = 0.1
        self._signal = self._xbar = 0.0
        self._history = [0.0] * self._length  # newest first, zero prehistory
        self._coefficients = [0.0] * (self._length + 1)
        self._power = [0.0] * (self._upper_bound - self._lower_bound + 1)
        self._cycle = 0.0

    def _adapt(self, value: float) -> list[float] | None:
        # NaN means a missing sample: it does not age ANY recursive state.
        # Infinity is an invalid price. Reject it before changing any state.
        value = float(value)
        if math.isnan(value):
            return None
        if not math.isfinite(value):
            raise ValueError("input must be finite or NaN (missing sample)")
        count = self._count + 1
        if count < 4:
            hp = 0.0  # Literal CurrentBar < 4 initialization in the functions.
            lp = hp   # SuperSmoother returns its input during these bars.
        else:
            hp = (self._hp1 * (value - 2.0 * self._price_previous + self._price_older)
                  + self._hp2 * self._hp_previous + self._hp3 * self._hp_older)
            lp = (self._ss1 * (hp + self._hp_previous) / 2.0
                  + self._ss2 * self._lp_previous + self._ss3 * self._lp_older)
        if not math.isfinite(hp) or not math.isfinite(lp):
            raise ValueError("filter calculation overflowed; input magnitude is too large")

        # Fast attack and slow decay normalize the band-limited signal, not price.
        peak = AGC_DECAY * self._peak
        if abs(lp) > peak:
            peak = abs(lp)
        signal = lp / peak if peak != 0.0 else self._signal
        history = [signal] + self._history[:-1]
        xx = [0.0] * (self._length + 1)
        for tap in range(1, self._length + 1):
            xx[tap] = history[self._length - tap]

        # Fit CURRENT sample using PREVIOUS samples and the old coefficients.
        # xx[0] is permanently zero, so coefficient[length] remains zero.
        xbar = 0.0
        for tap in range(1, self._length + 1):
            xbar += xx[self._length - tap] * self._coefficients[tap]
        error = xx[self._length] - xbar
        coefficients = self._coefficients.copy()
        for tap in range(1, self._length + 1):
            coefficients[tap] += self._mu * error * xx[self._length - tap]
        if not all(math.isfinite(c) for c in coefficients):
            raise ValueError("adaptive coefficient calculation overflowed")

        # Commit the accepted REAL observation after the candidate is valid.
        self._count = count
        self._price_older, self._price_previous = self._price_previous, value
        self._hp_older, self._hp_previous = self._hp_previous, hp
        self._lp_older, self._lp_previous = self._lp_previous, lp
        self._peak, self._signal, self._xbar = peak, signal, xbar
        self._history, self._coefficients = history, coefficients
        return xx

    def _raw_spectrum(self) -> list[float]:
        # A sweep generator evaluates the all-pole response at every integer
        # period. Explicit sums make the calculation easy to port without FFTs.
        power = []
        for period in range(self._lower_bound, self._upper_bound + 1):
            real = imaginary = 0.0
            for tap in range(1, self._length + 1):
                angle = TWO_PI * tap / period
                real += self._coefficients[tap] * math.cos(angle)
                imaginary += self._coefficients[tap] * math.sin(angle)
            denominator = (1.0 - real) * (1.0 - real) + imaginary * imaginary
            # Do not insert an epsilon: it would silently change the reference.
            if denominator <= 0.0 or not math.isfinite(denominator):
                raise ValueError("all-pole spectrum denominator is not finite and positive")
            p = POWER_SCALE / denominator
            if not math.isfinite(p):
                raise ValueError("all-pole spectrum power overflowed")
            power.append(p)
        return power

    def _peak_period(self, power: list[float]) -> float:
        # Ascending sweep and STRICT > select the shortest period on exact ties.
        maximum = 0.0
        peak_period = float(self._lower_bound)
        for index, value in enumerate(power):
            if value > maximum:
                maximum = value
                peak_period = float(self._lower_bound + index)
        return peak_period


class PredictorOutput(NamedTuple):
    signal: float       # Current normalized, band-limited observation.
    prediction: float   # Forecast bars_forward bars ahead, published NOW.


class GriffithsPredictor(_AdaptiveCore):
    """Adaptive normalized-signal forecast; TASC article mode is the default.

    predictor_mode="tradestation" reproduces the extra partial shift printed
    in the local MESA and TradeStation listings. It is an explicit alternative,
    never a silent correction to the article's single-shift recurrence.
    """

    def __init__(self, lower_bound: int = 18, upper_bound: int = 40,
                 length: int = 18, bars_forward: int = 2,
                 predictor_mode: str = "article") -> None:
        _integer("bars_forward", bars_forward, 1, 200)
        if predictor_mode not in ("article", "tradestation"):
            raise ValueError('predictor_mode must be "article" or "tradestation"')
        self._bars_forward = bars_forward
        self._predictor_mode = predictor_mode
        super().__init__(lower_bound, upper_bound, length, 200)

    @property
    def bars_forward(self) -> int:
        return self._bars_forward

    @property
    def predictor_mode(self) -> str:
        return self._predictor_mode

    def update(self, value: float) -> PredictorOutput:
        xx = self._adapt(value)
        if xx is None:
            return PredictorOutput(math.nan, math.nan)
        # Forecast using the NEW coefficients, with no synthetic LMS updates.
        # xx is disposable: synthetic samples never enter real signal history.
        prediction = 0.0
        for advance in range(1, self._bars_forward + 1):
            prediction = 0.0
            for tap in range(1, self._length + 1):
                prediction += xx[self._length + 1 - tap] * self._coefficients[tap]
            if self._predictor_mode == "tradestation":
                # Inclusive EasyLanguage range: advance .. Length - advance.
                # Preserve the ordered in-place partial shift before the full one.
                for index in range(advance, self._length - advance + 1):
                    xx[index] = xx[index + 1]
            for index in range(1, self._length):
                xx[index] = xx[index + 1]
            xx[self._length] = prediction
        if not math.isfinite(prediction):
            raise ValueError("forecast overflowed; shorten bars_forward")
        if not self.primed:
            return PredictorOutput(math.nan, math.nan)
        return PredictorOutput(self._signal, prediction)


# The user explicitly confirmed all 48 combinations on 2026-10-21.
REFERENCE_CASES_CONFIRMED = True


class ReferenceCase(NamedTuple):
    lower_bound: int
    upper_bound: int
    length: int
    bars_forward: int
    predictor_mode: str
    what_it_tests: str


def _case_suffix(case: ReferenceCase) -> str:
    suffix = f"LB{case.lower_bound}_UB{case.upper_bound}_L{case.length}"
    if KIND == "predictor":
        suffix += f"_BF{case.bars_forward}_V{int(case.predictor_mode == 'tradestation')}"
    return suffix


def _parameter_comment(case: ReferenceCase) -> str:
    text = (f"lower_bound={case.lower_bound}; upper_bound={case.upper_bound}; "
            f"length={case.length}")
    if KIND == "predictor":
        text += f"; bars_forward={case.bars_forward}; predictor_mode={case.predictor_mode}"
    return text


def _new_indicator(case: ReferenceCase):
    if KIND == "predictor":
        return MASTER_CLASS(case.lower_bound, case.upper_bound, case.length,
                            case.bars_forward, case.predictor_mode)
    return MASTER_CLASS(case.lower_bound, case.upper_bound, case.length)


def _float_literal(value: float, nan: str) -> str:
    # Round only serialized data, to 15 SIGNIFICANT decimal digits.
    if math.isnan(value):
        return nan
    if not math.isfinite(value):
        raise ValueError("reference values must be finite or NaN")
    literal = format(value, ".15g")
    if "." not in literal and "e" not in literal.lower():
        literal += ".0"  # Explicit floating point literals for Rust and Zig.
    return literal


def _array_body(values: list, indent: str, nan: str, language: str) -> str:
    # Heatmaps are rectangular TIME-MAJOR matrices; scalar arrays have 252 items.
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
    # Parse literals without executing arbitrary fixture code or imports.
    def decode(node):
        if isinstance(node, ast.List):
            return [decode(child) for child in node.elts]
        if isinstance(node, ast.Name) and node.id == "NaN":
            return math.nan
        return float(ast.literal_eval(node))
    arrays = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    arrays[target.id] = decode(node.value)
    return arrays


def _write_generated_section(path: Path, section: str, comment: str) -> None:
    # Append on the first run. On reruns replace ONLY our own marked section.
    begin = f"{comment} BEGIN GENERATED GRIFFITHS EXPECTED DATA"
    end = f"{comment} END GENERATED GRIFFITHS EXPECTED DATA"
    original = path.read_text(encoding="utf-8")
    block = begin + "\n\n" + section.rstrip() + "\n\n" + end
    if begin in original:
        start = original.index(begin)
        finish = original.index(end, start) + len(end)
        result = original[:start] + block + original[finish:]
    else:
        result = original.rstrip() + "\n\n" + block + "\n"
    path.write_text(result, encoding="utf-8")


def generate_reference_data(input_close: list[float], directory: Path) -> None:
    """Write Python expected arrays, reopen and verify, then translate literals.

    The proposal needs user confirmation before this function may write data.
    Other languages are generated from the reopened Python arrays, ensuring
    identical rounding, comments, time alignment and NaN masks everywhere.
    """
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError("reference parameter combinations await user confirmation")
    if len(input_close) != 252 or not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError("expected 252 inputs and 1..64 reference cases")
    python_path = directory / "test_testdata.py"
    if _load_python_arrays(python_path)["INPUT_CLOSE"] != input_close:
        raise ValueError("embedded INPUT_CLOSE differs from copied fixture")
    arrays = {}
    sections = ["# NaN marks unavailable public output, never recursive state.\nNaN = math.nan"]
    for case in REFERENCE_CASES:
        indicator = _new_indicator(case)
        results = [indicator.update(value) for value in input_close]
        bins = case.upper_bound - case.lower_bound + 1
        if KIND == "predictor":
            components = {"SIGNAL": [r.signal for r in results],
                          "PRED": [r.prediction for r in results]}
        elif KIND == "spectrum":
            components = {
                "IP": [r.instantaneous_period for r in results],
                "HEATMAP": [r.heatmap.values if not r.heatmap.is_empty()
                            else [math.nan] * bins for r in results],
                "MIN": [r.heatmap.value_min for r in results],
                "MAX": [r.heatmap.value_max for r in results],
            }
        else:
            components = {"DC": results}
        for component, values in components.items():
            name = "EXPECTED_" + _case_suffix(case) + "_" + component
            if name in arrays:
                raise ValueError("duplicate reference array name")
            arrays[name] = (case, values)
            sections.append(f"# {case.what_it_tests}\n# {_parameter_comment(case)}\n"
                            + f"{name} = [\n{_array_body(values, '    ', 'NaN', 'py')}\n]")
    _write_generated_section(python_path, "\n\n".join(sections), "#")

    # The Python fixture is authoritative. Verify its values BEFORE translation.
    written = _load_python_arrays(python_path)
    if {name for name in written if name.startswith("EXPECTED_")} != set(arrays):
        raise ValueError("Python expected arrays are missing or unexpected")
    for name, (case, raw) in arrays.items():
        actual = written[name]
        if len(actual) != 252:
            raise ValueError(f"{name} must contain 252 rows")
        matrix = name.endswith("_HEATMAP")
        if matrix and any(len(row) != case.upper_bound - case.lower_bound + 1 for row in actual):
            raise ValueError(f"{name} has incorrect heatmap dimensions")
        raw_flat = [v for row in raw for v in row] if matrix else raw
        flat = [v for row in actual for v in row] if matrix else actual
        for original, literal in zip(raw_flat, flat):
            if math.isnan(original):
                if not math.isnan(literal):
                    raise ValueError(f"{name} has incorrect NaN masks")
            elif literal != float(_float_literal(original, "NaN")):
                raise ValueError(f"{name} has incorrect 15-digit values")

    go_path = directory / "testdata_test.go"
    package = directory.name.replace("-", "").replace("_", "").lower()
    go_text = go_path.read_text(encoding="utf-8").replace("package xxxx", f"package {package}", 1)
    if 'import "math"' not in go_text:
        go_text = go_text.replace(f"package {package}\n",
                                  f'package {package}\n\nimport "math"\n', 1)
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
    for name, (case, _) in arrays.items():
        suffix = name.removeprefix("EXPECTED_")
        values = written[name]
        matrix = name.endswith("_HEATMAP")
        bins = case.upper_bound - case.lower_bound + 1
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
    print(f"Verified {len(arrays)} expected arrays for {len(REFERENCE_CASES)} cases in all five languages.")


KIND = 'predictor'
MASTER_CLASS = GriffithsPredictor

REFERENCE_CASES = (
    ReferenceCase(18, 40, 18, 1, 'article', 'Printed predictor default; short adaptive memory; 1-bar forecast; article shift semantics'),
    ReferenceCase(18, 40, 18, 1, 'tradestation', 'Printed predictor default; short adaptive memory; 1-bar forecast; tradestation shift semantics'),
    ReferenceCase(18, 40, 18, 2, 'article', 'Printed predictor default; short adaptive memory; 2-bar forecast; article shift semantics'),
    ReferenceCase(18, 40, 18, 2, 'tradestation', 'Printed predictor default; short adaptive memory; 2-bar forecast; tradestation shift semantics'),
    ReferenceCase(18, 40, 18, 3, 'article', 'Printed predictor default; short adaptive memory; 3-bar forecast; article shift semantics'),
    ReferenceCase(18, 40, 18, 3, 'tradestation', 'Printed predictor default; short adaptive memory; 3-bar forecast; tradestation shift semantics'),
    ReferenceCase(18, 40, 18, 5, 'article', 'Printed predictor default; short adaptive memory; 5-bar forecast; article shift semantics'),
    ReferenceCase(18, 40, 18, 5, 'tradestation', 'Printed predictor default; short adaptive memory; 5-bar forecast; tradestation shift semantics'),
    ReferenceCase(18, 40, 40, 1, 'article', 'Article Figure 2 settings; full-cycle memory; 1-bar forecast; article shift semantics'),
    ReferenceCase(18, 40, 40, 1, 'tradestation', 'Article Figure 2 settings; full-cycle memory; 1-bar forecast; tradestation shift semantics'),
    ReferenceCase(18, 40, 40, 2, 'article', 'Article Figure 2 settings; full-cycle memory; 2-bar forecast; article shift semantics'),
    ReferenceCase(18, 40, 40, 2, 'tradestation', 'Article Figure 2 settings; full-cycle memory; 2-bar forecast; tradestation shift semantics'),
    ReferenceCase(18, 40, 40, 3, 'article', 'Article Figure 2 settings; full-cycle memory; 3-bar forecast; article shift semantics'),
    ReferenceCase(18, 40, 40, 3, 'tradestation', 'Article Figure 2 settings; full-cycle memory; 3-bar forecast; tradestation shift semantics'),
    ReferenceCase(18, 40, 40, 5, 'article', 'Article Figure 2 settings; full-cycle memory; 5-bar forecast; article shift semantics'),
    ReferenceCase(18, 40, 40, 5, 'tradestation', 'Article Figure 2 settings; full-cycle memory; 5-bar forecast; tradestation shift semantics'),
    ReferenceCase(10, 40, 54, 1, 'article', 'Broad band; longer adaptive memory; 1-bar forecast; article shift semantics'),
    ReferenceCase(10, 40, 54, 1, 'tradestation', 'Broad band; longer adaptive memory; 1-bar forecast; tradestation shift semantics'),
    ReferenceCase(10, 40, 54, 2, 'article', 'Broad band; longer adaptive memory; 2-bar forecast; article shift semantics'),
    ReferenceCase(10, 40, 54, 2, 'tradestation', 'Broad band; longer adaptive memory; 2-bar forecast; tradestation shift semantics'),
    ReferenceCase(10, 40, 54, 3, 'article', 'Broad band; longer adaptive memory; 3-bar forecast; article shift semantics'),
    ReferenceCase(10, 40, 54, 3, 'tradestation', 'Broad band; longer adaptive memory; 3-bar forecast; tradestation shift semantics'),
    ReferenceCase(10, 40, 54, 5, 'article', 'Broad band; longer adaptive memory; 5-bar forecast; article shift semantics'),
    ReferenceCase(10, 40, 54, 5, 'tradestation', 'Broad band; longer adaptive memory; 5-bar forecast; tradestation shift semantics'),
    ReferenceCase(12, 24, 24, 1, 'article', 'Short octave band; faster adaptation; 1-bar forecast; article shift semantics'),
    ReferenceCase(12, 24, 24, 1, 'tradestation', 'Short octave band; faster adaptation; 1-bar forecast; tradestation shift semantics'),
    ReferenceCase(12, 24, 24, 2, 'article', 'Short octave band; faster adaptation; 2-bar forecast; article shift semantics'),
    ReferenceCase(12, 24, 24, 2, 'tradestation', 'Short octave band; faster adaptation; 2-bar forecast; tradestation shift semantics'),
    ReferenceCase(12, 24, 24, 3, 'article', 'Short octave band; faster adaptation; 3-bar forecast; article shift semantics'),
    ReferenceCase(12, 24, 24, 3, 'tradestation', 'Short octave band; faster adaptation; 3-bar forecast; tradestation shift semantics'),
    ReferenceCase(12, 24, 24, 5, 'article', 'Short octave band; faster adaptation; 5-bar forecast; article shift semantics'),
    ReferenceCase(12, 24, 24, 5, 'tradestation', 'Short octave band; faster adaptation; 5-bar forecast; tradestation shift semantics'),
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-reference-data", action="store_true",
                        help="write all five languages after case confirmation")
    arguments = parser.parse_args()
    # Exact shared 252-close input is embedded for standalone reproducibility.
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
    example = MASTER_CLASS()
    results = [example.update(close) for close in INPUT_CLOSE]
    print(f"Default streaming output after {len(INPUT_CLOSE)} observations: {results[-1]}")
    print(f"Reference configurations: {len(REFERENCE_CASES)} combinations; confirmed={REFERENCE_CASES_CONFIRMED}")
    if arguments.generate_reference_data:
        generate_reference_data(INPUT_CLOSE, Path(__file__).resolve().parent)
