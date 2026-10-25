"""March 2005 Median-Average Adaptive Filter, streaming research master.

The numerical authority is the article's recurrence with the eSignal tip's
termination guard and explicit startup. Read description.md before porting:
trial EMAs always read the PREVIOUS BAR's one shared Value2, the successful
trial length is decremented by two, and the first public value is at bar 39.
The first three intermediate Smooth entries are zero, exactly as in the tip.

Only standard Python is used. Internal state is never rounded. The executable
demo uses 252 embedded closes. All 14 threshold cases are user-confirmed;
reference generation exports 15-significant-digit decimals to five languages.
"""

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# These are algorithm constants, not adjustable parameters in the article.
# 0.2 is a SEARCH SENTINEL, not a rounded mathematical approximation. Do not
# replace it with infinity: thresholds >=0.2 intentionally skip the search.
SEARCH_LENGTH = 39
MINIMUM_OUTPUT_LENGTH = 3
INITIAL_DISCREPANCY = 0.2


class MedianAverageAdaptiveFilterState(NamedTuple):
    """Owned diagnostic snapshot; histories are newest first, never sorted."""

    samples_seen: int
    previous_prices: tuple[float, ...]
    smoothed_history: tuple[float, ...]
    candidate_ema: float
    filtered: float
    selected_length: int | None
    evaluated_length: int | None
    trial_count: int
    discrepancy: float | None
    alpha: float | None


def _threshold(value):
    """Keep the sole source parameter finite and nonnegative, without caps.

    Threshold is a FRACTION: 0.002 means 0.2 percent, not 0.002 percent.
    Zero permits exact agreement; >=0.2 follows the source's loop-skip branch.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('threshold must be a finite nonnegative real number')
    try:
        number = float(value)
    except (ValueError, OverflowError) as error:
        raise ValueError('threshold must be a finite nonnegative real number') from error
    if not math.isfinite(number) or number < 0.0:
        raise ValueError('threshold must be a finite nonnegative real number')
    return number


class MedianAverageAdaptiveFilter:
    """Streaming scalar Filt for the article/eSignal MAAF, not a median EMA.

    The article supplies Price=(H+L)/2. update accepts an already chosen scalar
    price; these reference cases use INPUT_CLOSE as explicitly requested.

    We replay one completed NEWBAR at a time, as in MAAF.efs. That tip inserts
    a zero Smooth placeholder on each of the first three bars, then computes
    the four-price weighted smoother. Once 39 Smooth entries exist, it begins
    the adaptive recurrence from Value2=Filt=0. Thus exactly 38 public NaNs
    precede the first output. No adaptive recurrence runs during this warmup.
    """

    def __init__(self, threshold=0.002):
        self._threshold = _threshold(threshold)
        self.reset()

    @property
    def threshold(self):
        """Fixed configuration; create a new instance to change it."""
        return self._threshold

    @property
    def warmup_bars(self):
        return SEARCH_LENGTH - 1

    @property
    def is_primed(self):
        # Primed means eSignal's history gate is open, not IIR convergence.
        return self.samples_seen >= SEARCH_LENGTH

    @property
    def state(self):
        return MedianAverageAdaptiveFilterState(
            self.samples_seen, tuple(self._prices), tuple(self._smooth),
            self._candidate, self._filtered, self.selected_length,
            self.evaluated_length, self.trial_count, self.discrepancy, self.alpha)

    def reset(self):
        """Reset all price, smoother and recursive state; retain threshold."""
        self.samples_seen = 0
        self._prices = []
        self._smooth = []
        self._candidate = 0.0  # one shared Value2, not one EMA for each length
        self._filtered = 0.0   # source Filt(0); do not seed from first price
        self.output = math.nan
        self.selected_length = self.evaluated_length = None
        self.trial_count = 0
        self.discrepancy = self.alpha = None

    def update(self, value):
        """Accept one scalar price; return Filt or NaN before bar 39.

        NaN observations are skipped without advancing any state or changing
        the last accepted output. Invalid types, infinities and overflowing
        intermediate arithmetic raise ValueError before any state is committed.
        These missing/invalid-input rules are the master's stream contract;
        the source assumes valid chart data.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('input must be a real number; NaN may mark missing data')
        try:
            price = float(value)
        except (ValueError, OverflowError) as error:
            raise ValueError('input cannot be represented as a float') from error
        if math.isnan(price):
            return math.nan
        if not math.isfinite(price):
            raise ValueError('input must not be infinite')

        # Build LOCAL histories first: a failed calculation must leave the
        # stream untouched. Never sort this chronological history in place.
        bar = self.samples_seen + 1
        prices = [price] + self._prices[:3]
        smooth = 0.0
        if bar >= 4:
            # Preserve the article's arithmetic order and exact rational /6.
            smooth = (prices[0] + 2.0*prices[1] + 2.0*prices[2] + prices[3]) / 6.0
        if not math.isfinite(smooth):
            raise ValueError('non-finite smoother arithmetic; state was not changed')
        history = [smooth] + self._smooth[:SEARCH_LENGTH - 1]

        if bar < SEARCH_LENGTH:
            # eSignal leaves Value2 and Filt unchanged while history fills.
            # The first three Smooth=0 placeholders stay in this history.
            self._prices, self._smooth = prices, history
            self.samples_seen = bar
            return math.nan

        length = SEARCH_LENGTH  # restart search from 39 on EVERY bar
        discrepancy = INITIAL_DISCREPANCY
        candidate = self._candidate
        previous_candidate = self._candidate  # freeze Value2[1] for ALL trials
        evaluated_length = None
        trials = 0
        while discrepancy > self.threshold:
            # Odd lengths 39,37,...,1 use an exact center order statistic.
            # A separate sorted copy is simple to port and preserves time order.
            alpha = 2.0 / (length + 1.0)
            median = sorted(history[:length])[length // 2]
            candidate = alpha*smooth + (1.0 - alpha)*previous_candidate
            if not math.isfinite(candidate):
                raise ValueError('non-finite trial EMA; state was not changed')

            # Source divides by the SIGNED median, not abs(median). Changing
            # that would redesign the algorithm for negative-valued inputs.
            # A zero median leaves the previous trial's discrepancy unchanged.
            if median != 0.0:
                discrepancy = abs(median - candidate) / median
                if not math.isfinite(discrepancy):
                    raise ValueError('non-finite discrepancy; state was not changed')
            evaluated_length = length
            trials += 1
            length -= 2  # unconditional, including the SUCCESSFUL trial
            if length <= 0:
                # eSignal's explicit guard avoids Median with negative length.
                # The article omits it; zero medians can reach invalid lengths.
                break

        length = max(length, MINIMUM_OUTPUT_LENGTH)
        alpha = 2.0 / (length + 1.0)
        filtered = alpha*smooth + (1.0 - alpha)*self._filtered
        if not math.isfinite(filtered):
            raise ValueError('non-finite output EMA; state was not changed')

        # Commit once. Value2 saves ONLY the last trial's result across bars.
        # Filt has its own independent recurrence with the decremented length.
        # If threshold>=0.2, no trial ran: length remains 39 and Value2 is held.
        self._prices, self._smooth = prices, history
        self._candidate, self._filtered = candidate, filtered
        self.samples_seen = bar
        self.selected_length, self.evaluated_length = length, evaluated_length
        self.trial_count, self.discrepancy, self.alpha = trials, discrepancy, alpha
        self.output = filtered
        return filtered


# Everything below is fixture tooling, separate from the recurrence to port.
INDICATOR_SLUG = 'median-average-adaptive-filter'
MASTER_CLASS = MedianAverageAdaptiveFilter
REFERENCE_INPUT = 'close'
PARAMETER_SHORTCUTS = {'threshold': 'T'}
# The user explicitly confirmed all 14 thresholds on 2026-10-25. This also
# authorizes regeneration of the same reference cases without another prompt.
REFERENCE_CASES_CONFIRMED = True


REFERENCE_CASES = tuple(dict(threshold=threshold, what_it_tests=what)
                        for threshold, what in (
    (0.0, 'Exact-agreement search and minimum output-length clamp'),
    (0.0001, 'Very strict tolerance; rapid adaptation'),
    (0.0005, 'Strict tolerance below the article default'),
    (0.001, 'Half the article threshold'),
    (0.002, 'Article and eSignal default threshold'),
    (0.003, 'Moderately relaxed tolerance near the default'),
    (0.005, 'Half-percent median-to-trial discrepancy tolerance'),
    (0.01, 'One-percent discrepancy tolerance'),
    (0.02, 'Two-percent tolerance and longer smoothing'),
    (0.05, 'Loose tolerance and slower adaptation'),
    (0.1, 'Ten-percent tolerance and long selected lengths'),
    (0.199, 'Search enabled just below the initial discrepancy sentinel'),
    (0.2, 'Sentinel equality skips the search; fixed 39-length output EMA'),
    (0.25, 'Above-sentinel threshold preserves the loop-skip branch'),
))


def _parameter_token(value):
    if isinstance(value, str):
        return value.upper()
    if isinstance(value, bool):
        return '1' if value else '0'
    return format(value, '.15g').replace('.', '_').replace('-', 'm')


def _case_suffix(case):
    return '_'.join(PARAMETER_SHORTCUTS[name]+_parameter_token(value)
                    for name, value in case.items() if name != 'what_it_tests')


def _parameter_comment(case):
    return ', '.join(f'{key}={value}' for key, value in case.items()
                     if key != 'what_it_tests') + '; search_length=39 (fixed); input=' + REFERENCE_INPUT


def _float_literal(value, nan):
    if math.isnan(value):
        return nan
    if not math.isfinite(value):
        raise ValueError('cannot serialize infinite reference output')
    literal = format(value, '.15g')  # 15 significant digits, only at export.
    if '.' not in literal and 'e' not in literal:
        literal += '.0'
    return literal


def _array_body(values, indent, nan, language):
    if values and isinstance(values[0], list):
        opening, closing = {'py': ('[', ']'), 'go': ('{', '}'),
                            'ts': ('[', ']'), 'rs': ('vec![', ']'),
                            'zig': ('.{', '}')}[language]
        return '\n'.join(indent+opening+', '.join(_float_literal(v, nan) for v in row)
                          + closing+',' for row in values)
    tokens = [_float_literal(v, nan) for v in values]
    return '\n'.join(indent+', '.join(tokens[i:i+6])+','
                      for i in range(0, len(tokens), 6))


def _load_arrays(path):
    def decode(node):
        if isinstance(node, ast.List):
            return [decode(child) for child in node.elts]
        if isinstance(node, ast.Name) and node.id == 'NaN':
            return math.nan
        return float(ast.literal_eval(node))
    arrays = {}
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    arrays[target.id] = decode(node.value)
    return arrays


def _write_section(path, content, comment):
    # Rerunning replaces this marked generated section, never the input arrays.
    begin = f'{comment} BEGIN GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA'
    end = f'{comment} END GENERATED {INDICATOR_SLUG.upper()} EXPECTED DATA'
    original = path.read_text(encoding='utf-8')
    block = begin+'\n\n'+content.rstrip()+'\n\n'+end
    if begin in original:
        start = original.index(begin)
        finish = original.index(end, start)+len(end)
        result = original[:start]+block+original[finish:]
    else:
        if path.suffix == '.rs':
            # Keep expected functions INSIDE the original cfg(test) module.
            original = original.rstrip()
            if not original.endswith('}'):
                raise ValueError('expected a closing Rust testdata module')
            result = original[:-1].rstrip()+'\n\n'+block+'\n}\n'
        else:
            result = original.rstrip()+'\n\n'+block+'\n'
    path.write_text(result, encoding='utf-8')


def _run_reference(case, inputs):
    indicator = MASTER_CLASS(**{k:v for k,v in case.items() if k != 'what_it_tests'})
    # A single output needs no component suffix in its expected array name.
    return {'': [indicator.update(close) for close in inputs['INPUT_CLOSE']]}


def generate_reference_data(directory, embedded_inputs=None):
    if not REFERENCE_CASES_CONFIRMED:
        raise ValueError('reference combinations await user confirmation')
    if not 1 <= len(REFERENCE_CASES) <= 64:
        raise ValueError('expected at most 64 combinations')
    python_path = directory/'test_testdata.py'
    inputs = _load_arrays(python_path)
    if len(inputs['INPUT_CLOSE']) != 252:
        raise ValueError('expected 252 closes')
    for name, values in (embedded_inputs or {}).items():
        if inputs[name] != values:
            raise ValueError(f'embedded {name} differs from copied fixture')
    arrays = {}
    sections = ['# NaN marks unavailable public output only.\nNaN = math.nan']
    for case in REFERENCE_CASES:
        for component, values in _run_reference(case, inputs).items():
            name = 'EXPECTED_'+_case_suffix(case)+('_'+component if component else '')
            if name in arrays:
                raise ValueError('duplicate expected name')
            arrays[name] = (case, values)
            sections.append(f"# {case['what_it_tests']}\n# {_parameter_comment(case)}\n"
                            +f'{name} = [\n'+_array_body(values, '    ', 'NaN', 'py')+'\n]')
    _write_section(python_path, '\n\n'.join(sections), '#')
    # Reopen Python literals and verify dimensions, values, and every NaN.
    # All other languages translate this authoritative rounded Python data.
    written = _load_arrays(python_path)
    if {n for n in written if n.startswith('EXPECTED_')} != set(arrays):
        raise ValueError('missing or unexpected Python reference arrays')
    for name, (case, raw) in arrays.items():
        actual = written[name]
        matrix = isinstance(raw[0], list)
        bins = len(raw[0]) if matrix else 0
        if len(actual) != 252 or (matrix and any(len(row) != bins for row in actual)):
            raise ValueError(f'incorrect dimensions: {name}')
        flat = [v for row in actual for v in row] if matrix else actual
        raw_flat = [v for row in raw for v in row] if matrix else raw
        for source, literal in zip(raw_flat, flat):
            if math.isnan(source):
                if not math.isnan(literal):
                    raise ValueError(f'incorrect NaN mask: {name}')
            elif literal != float(_float_literal(source, 'NaN')):
                raise ValueError(f'incorrect 15-digit value: {name}')
    translated = {language: [] for language in ('go', 'ts', 'rs', 'zig')}
    for name, (case, raw) in arrays.items():
        suffix = name.removeprefix('EXPECTED_')
        values = written[name]
        matrix = isinstance(raw[0], list)
        bins = len(values[0]) if matrix else 0
        comments = f"// {case['what_it_tests']}\n// {_parameter_comment(case)}\n"
        go_type = '[][]float64' if matrix else '[]float64'
        ts_type = 'number[][]' if matrix else 'number[]'
        rs_type = 'Vec<Vec<f64>>' if matrix else 'Vec<f64>'
        zig_type = f'[252][{bins}]f64' if matrix else '[252]f64'
        translated['go'].append(comments+f'var expected{suffix} = {go_type}{{\n'
                                +_array_body(values, '\t', 'math.NaN()', 'go')+'\n}')
        translated['ts'].append(comments+f'export const expected{suffix}: {ts_type} = [\n'
                                +_array_body(values, '    ', 'NaN', 'ts')+'\n];')
        translated['rs'].append(comments+f'pub fn expected_{suffix.lower()}() -> {rs_type} {{\n    vec![\n'
                                +_array_body(values, '        ', 'f64::NAN', 'rs')+'\n    ]\n}')
        translated['zig'].append(comments+f'pub fn expected{suffix}() {zig_type} {{\n    return .{{\n'
                                 +_array_body(values, '        ', 'nan', 'zig')+'\n    };\n}')
    # The shared input fixture's package declaration can follow a file comment.
    # Find its declaration line explicitly instead of assuming it is first or
    # already has the indicator package name. Add math for generated NaNs.
    go_path = directory/'testdata_test.go'
    text = go_path.read_text(encoding='utf-8')
    package = INDICATOR_SLUG.replace('-', '').replace('_', '')
    lines = text.splitlines(keepends=True)
    declarations = [index for index, line in enumerate(lines)
                    if line.startswith('package ')]
    if len(declarations) != 1:
        raise ValueError('expected exactly one Go package declaration')
    lines[declarations[0]] = f'package {package}\n'
    text = ''.join(lines)
    if 'import "math"' not in text:
        text = text.replace(f'package {package}\n', f'package {package}\n\nimport "math"\n', 1)
    go_path.write_text(text, encoding='utf-8')
    for language, filename in [('go', 'testdata_test.go'), ('ts', 'testdata.ts'),
                               ('rs', 'testdata.rs'), ('zig', 'testdata.zig')]:
        _write_section(directory/filename, '\n\n'.join(translated[language]), '//')
    print(f'Verified {len(arrays)} expected arrays for {len(REFERENCE_CASES)} cases in Python; translated all five languages.')




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data', action='store_true',
                        help='write and verify all confirmed five-language fixtures')
    args = parser.parse_args()
    # Exact 252 INPUT_CLOSE values embedded for a standalone streaming demo.
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
    if args.generate_reference_data:
        generate_reference_data(Path(__file__).resolve().parent, {'INPUT_CLOSE': INPUT_CLOSE})
    else:
        indicator = MedianAverageAdaptiveFilter()  # article threshold=0.002
        results = [indicator.update(price) for price in INPUT_CLOSE]
        print(f'{len(results)} closes; first valid bar={indicator.warmup_bars + 1}')
        print('Default MAAF final output:', results[-1])
        print('Selected length:', indicator.selected_length, 'alpha:', indicator.alpha)
        print(f'{len(REFERENCE_CASES)} reference cases; confirmed={REFERENCE_CASES_CONFIRMED}')
