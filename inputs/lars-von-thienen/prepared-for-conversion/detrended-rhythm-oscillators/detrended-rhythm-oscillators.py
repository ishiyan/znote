"""Detrended Rhythm Oscillator: standalone streaming research prototype master.

Read description.md for equations, source adaptations, input contracts,
priming and porting conventions. Only Python standard-library binary64 math.
"""

# Source: Detrended Rhythm Oscillator, © WhenToTrade / Lars von Thienen.
# SPDX-License-Identifier: MPL-2.0
# https://www.mozilla.org/en-US/MPL/2.0/
# Adaptations: numeric-only pivot state, zero-extremum repair, explicit priming.

from __future__ import annotations

import math
from collections import deque
from typing import NamedTuple


def _integer(value, name, minimum=1):
    # A Python bool is an int subclass, but is not a meaningful period.
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _real(value, name, minimum=0.0):
    # Reject booleans and non-finite parameters before allocating state.
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite real >= {minimum}")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"invalid {name}") from error
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f"{name} must be a finite real >= {minimum}")
    return value


def _sample(value):
    # NaN denotes a skipped observation. It must never enter feedback state.
    # Infinity and booleans are invalid; validation itself changes no state.
    if isinstance(value, bool):
        raise ValueError("price must be finite or NaN")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("price must be finite or NaN") from error
    if math.isinf(value):
        raise ValueError("price must be finite or NaN")
    return value


def _finite(value):
    # Do not serialize or feed back an infinity produced by overflow.
    if not math.isfinite(value):
        raise ValueError("numerical overflow; reset the indicator before reuse")
    return value


def _median(values):
    # Ordinary median, including the arithmetic mean of two central values.
    ordered = sorted(values)
    n = len(ordered)
    if not n:
        return math.nan
    middle = n // 2
    return ordered[middle] if n % 2 else (ordered[middle-1] + ordered[middle]) / 2.0

class _EMA:
    """First-price seed; recursive output starts on the first finite sample."""
    def __init__(self, length):
        self.alpha = 2.0 / (length + 1.0)
        self.value = math.nan

    def update(self, value):
        # Every term reads the previous accepted observation's state.
        new = value if math.isnan(self.value) else (
            self.alpha * value + (1.0-self.alpha) * self.value)
        self.value = _finite(new)
        return self.value

class RhythmOutput(NamedTuple):
    value: float
    direction: float
    cycle_length: float
    pivot_value: float
    pivot_offset: float


class DetrendedRhythmOscillator:
    """PPO-driven rolling-extremum ZigZag and completed-cycle median.

    Source: dro.pinesctipt, Lars von Thienen (MPL 2.0). This numerical
    extraction removes dependence on chart labels being enabled and fixes
    zero-valued-extremum truthiness. Current pivot outputs are PROVISIONAL.
    """
    def __init__(self, fast_length=3, slow_length=50, zig_period=30,
                 cycle_memory=15, detrend=True):
        self.fast_length = _integer(fast_length, 'fast_length')
        self.slow_length = _integer(slow_length, 'slow_length', 2)
        if self.fast_length >= self.slow_length:
            raise ValueError("fast_length must be smaller than slow_length")
        self.zig_period = _integer(zig_period, 'zig_period', 5)
        self.cycle_memory = _integer(cycle_memory, 'cycle_memory', 3)
        if type(detrend) is not bool:
            raise ValueError("detrend must be bool")
        self.detrend = detrend
        # A finite PPO exists immediately, but hide its initialization period.
        self.warmup_bars = self.slow_length-1 if detrend else 0
        self.reset()

    def reset(self):
        self.samples_seen = 0
        self.fast, self.slow = _EMA(self.fast_length), _EMA(self.slow_length)
        self.window = deque(maxlen=self.zig_period)
        self.pivots = []  # newest first; (value, accepted zero-based index)
        self.direction = 0
        self.last_cycle_length = math.nan

    @property
    def is_primed(self):
        return self.samples_seen > self.warmup_bars

    @property
    def is_cycle_primed(self):
        return self.is_primed and not math.isnan(self.last_cycle_length)

    def update(self, price):
        price = _sample(price)
        if math.isnan(price):
            return RhythmOutput(*(math.nan,)*5)
        if self.detrend:
            fast, slow = self.fast.update(price), self.slow.update(price)
            # PPO is undefined at a zero slow EMA. No made-up ratio is used.
            value = math.nan if slow == 0.0 else _finite(100.0*(fast-slow)/slow)
        else:
            value = price
        index = self.samples_seen
        self.samples_seen += 1
        if math.isnan(value):
            return RhythmOutput(*(math.nan,)*5)
        self.window.append(value)
        high, low = value == max(self.window), value == min(self.window)
        # If both extrema occur (constant window), retain the old direction.
        direction = 1 if high and not low else -1 if low and not high else self.direction
        if direction and (high or low):
            if direction != self.direction or not self.pivots:
                self.pivots.insert(0, (value, index))
                # At most memory completed full-cycle measurements are needed.
                del self.pivots[self.cycle_memory+3:]
            elif (direction == 1 and value > self.pivots[0][0]) or (
                    direction == -1 and value < self.pivots[0][0]):
                self.pivots[0] = (value, index)
        self.direction = direction
        # Pivot 0 is still moving. Use only pairs of CONFIRMED like-type pivots.
        # Five pivots give three completed legs and two full-cycle distances.
        cycles = [float(self.pivots[i][1]-self.pivots[i+2][1])
                  for i in range(1, len(self.pivots)-2)] if len(self.pivots)>=5 else []
        self.last_cycle_length = _median(cycles[-self.cycle_memory:])
        if not self.is_primed:
            return RhythmOutput(*(math.nan,)*5)
        pivot_value = self.pivots[0][0] if self.pivots else math.nan
        offset = float(self.pivots[0][1]-index) if self.pivots else math.nan
        return RhythmOutput(value, float(direction), self.last_cycle_length, pivot_value, offset)

INDICATOR_SLUG = 'detrended-rhythm-oscillators'
MASTER_CLASS = DetrendedRhythmOscillator
PARAMETER_SHORTCUTS = [('fast_length', 'F'), ('slow_length', 'S'), ('zig_period', 'Z'), ('cycle_memory', 'M'), ('detrend', 'D')]
REFERENCE_CASES = ({'params': {'fast_length': 3,
             'slow_length': 50,
             'zig_period': 30,
             'cycle_memory': 15,
             'detrend': True},
  'what_it_tests': 'Published PPO lengths and 30-bar ZigZag extrema.'},
 {'params': {'fast_length': 3,
             'slow_length': 50,
             'zig_period': 5,
             'cycle_memory': 15,
             'detrend': True},
  'what_it_tests': 'Short extrema window detects more completed rhythms.'},
 {'params': {'fast_length': 3,
             'slow_length': 50,
             'zig_period': 10,
             'cycle_memory': 15,
             'detrend': True},
  'what_it_tests': 'Intermediate extrema window.'},
 {'params': {'fast_length': 2,
             'slow_length': 20,
             'zig_period': 10,
             'cycle_memory': 15,
             'detrend': True},
  'what_it_tests': 'Faster PPO detrending.'},
 {'params': {'fast_length': 5,
             'slow_length': 100,
             'zig_period': 30,
             'cycle_memory': 15,
             'detrend': True},
  'what_it_tests': 'Longer PPO trend memory.'},
 {'params': {'fast_length': 3,
             'slow_length': 50,
             'zig_period': 5,
             'cycle_memory': 3,
             'detrend': True},
  'what_it_tests': 'Short completed-cycle median memory.'},
 {'params': {'fast_length': 3,
             'slow_length': 50,
             'zig_period': 10,
             'cycle_memory': 15,
             'detrend': False},
  'what_it_tests': 'Source switch off: ZigZag uses raw close prices.'},
 {'params': {'fast_length': 3,
             'slow_length': 300,
             'zig_period': 30,
             'cycle_memory': 15,
             'detrend': True},
  'what_it_tests': 'Slow EMA initialization exceeds the 252-sample record.'})
OUTPUT_FIELDS = ('value', 'direction', 'cycle_length', 'pivot_value', 'pivot_offset')


def flatten_output(indicator,output):
    # Scalar filters expose VALUE; named outputs preserve each numeric field.
    if isinstance(output,(int,float)):
        return {'value':output}
    return {name:getattr(output,name) for name in OUTPUT_FIELDS}


def fixture_update(indicator,index,price,arrays):
    return indicator.update(price)

# ---------------------------------------------------------------------------
# Fixture tooling: numerical classes above are the independent porting master.
# No sibling module, third-party package, market API, or network is required.
# ---------------------------------------------------------------------------
import argparse
import ast
import re
from pathlib import Path


def _load_arrays(path):
    """Parse literal fixture arrays without executing arbitrary fixture code."""
    result = {}
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if not isinstance(node,ast.Assign) or not isinstance(node.value,ast.List):
            continue
        target = node.targets[0]
        if not isinstance(target,ast.Name):
            continue
        values = []
        for item in node.value.elts:
            if isinstance(item,ast.Attribute) and isinstance(item.value,ast.Name) and item.value.id=='math' and item.attr=='nan':
                values.append(math.nan)
            else:
                values.append(float(ast.literal_eval(item)))
        result[target.id] = values
    return result


def _token(value):
    # Tuple periods are encoded in their supplied order, e.g. P20_40.
    if isinstance(value,(tuple,list)):
        return '_'.join(_token(item) for item in value)
    if type(value) is bool:
        return '1' if value else '0'
    return format(float(value),'g').replace('.','_').replace('-','m').replace('+','')


def _suffix(parameters):
    return '_'.join(shortcut+_token(parameters[name]) for name,shortcut in PARAMETER_SHORTCUTS)


def _literal(value,nan_token):
    # Binary64 calculations are rounded ONCE: serialization, 15 significant digits.
    if math.isnan(value):
        return nan_token
    if not math.isfinite(value):
        raise ValueError("fixture output must be finite or NaN")
    text = format(value,'.15g')
    if '.' not in text and 'e' not in text.lower():
        text += '.0'  # Rust/Zig require explicit floating-point literal types.
    return text


def _rows(values,nan_token,indent):
    literals = [_literal(value,nan_token) for value in values]
    return '\n'.join(indent+', '.join(literals[i:i+6])+',' for i in range(0,len(literals),6))


def _replace_section(path,body,comment,rust=False):
    # Idempotent generated blocks preserve every copied INPUT array.
    begin = comment+' BEGIN GENERATED '+INDICATOR_SLUG.upper()+' EXPECTED DATA'
    end = comment+' END GENERATED '+INDICATOR_SLUG.upper()+' EXPECTED DATA'
    original = path.read_text(encoding='utf-8')
    block = begin+'\n\n'+body.rstrip()+'\n\n'+end
    if begin in original:
        start = original.index(begin)
        stop = original.index(end,start)+len(end)
        result = original[:start]+block+original[stop:]
    elif rust:
        # The root Rust fixtures already contain a cfg(test) module. Keep all
        # generated functions INSIDE it, rather than adding inaccessible peers.
        stop = original.rfind('}')
        result = original[:stop].rstrip()+'\n\n'+block+'\n'+original[stop:]
    else:
        result = original.rstrip()+'\n\n'+block+'\n'
    path.write_text(result,encoding='utf-8')


def reference_outputs(input_close,directory):
    arrays = _load_arrays(directory/'test_testdata.py')
    if len(input_close)!=252 or input_close!=arrays['INPUT_CLOSE']:
        raise ValueError("embedded 252 closes must equal the copied fixture")
    if not 1<=len(REFERENCE_CASES)<=64:
        raise ValueError("require one through 64 parameter combinations")
    outputs = []
    for case in REFERENCE_CASES:
        parameters = case['params']
        indicator = MASTER_CLASS(**parameters)
        columns = {}
        for index,price in enumerate(input_close):
            output = fixture_update(indicator,index,price,arrays)
            fields = flatten_output(indicator,output)
            if index and set(fields)!=set(columns):
                raise ValueError("fixture output field set changed")
            for field,value in fields.items():
                columns.setdefault(field,[]).append(float(value))
        for field,values in columns.items():
            if len(values)!=252:
                raise ValueError("one output per supplied close is required")
            suffix = _suffix(parameters)+'_'+field.upper()
            explanation = case['what_it_tests']+' Output: '+field+'.'
            parameter_text = ', '.join(f'{name}={parameters[name]!r}' for name,_ in PARAMETER_SHORTCUTS)
            outputs.append((suffix,explanation,parameter_text,values))
    if len({row[0] for row in outputs})!=len(outputs):
        raise ValueError("expected-array identifiers are not unique")
    return outputs


def generate_reference_data(input_close,directory):
    outputs = reference_outputs(input_close,directory)
    python_sections = []
    for suffix,explanation,parameters,values in outputs:
        python_sections.append(f'# {explanation}\n# {parameters}\nEXPECTED_{suffix} = [\n'
                               +_rows(values,'math.nan','    ')+'\n]')
    _replace_section(directory/'test_testdata.py','\n\n'.join(python_sections),'#')
    # Read BACK the saved Python decimal literals. All other languages copy
    # these exact saved numbers, not separately computed/re-rounded results.
    saved = _load_arrays(directory/'test_testdata.py')
    if {name for name in saved if name.startswith('EXPECTED_')} != {'EXPECTED_'+row[0] for row in outputs}:
        raise ValueError("saved Python array set differs from the reference")
    sections = {name:[] for name in ('testdata_test.go','testdata.ts','testdata.rs','testdata.zig')}
    for suffix,explanation,parameters,raw in outputs:
        values = saved['EXPECTED_'+suffix]
        if len(values)!=252:
            raise ValueError("saved Python output has wrong length")
        for calculated,stored in zip(raw,values):
            if math.isnan(calculated) and math.isnan(stored):
                continue
            if stored!=float(_literal(calculated,'math.nan')):
                raise ValueError("Python serialization lost the defined precision")
        comments = f'// {explanation}\n// {parameters}\n'
        sections['testdata_test.go'].append(comments+'var expected'+suffix+' = []float64{\n'+_rows(values,'math.NaN()','\t')+'\n}')
        sections['testdata.ts'].append(comments+'export const expected'+suffix+': number[] = [\n'+_rows(values,'NaN','    ')+'\n];')
        sections['testdata.rs'].append(comments+'pub fn expected_'+suffix.lower()+'() -> Vec<f64> {\n    vec![\n'+_rows(values,'f64::NAN','        ')+'\n    ]\n}')
        sections['testdata.zig'].append(comments+'pub fn expected'+suffix+'() [252]f64 {\n    return .{\n'+_rows(values,'nan','        ')+'\n    };\n}')
    go_path = directory/'testdata_test.go'
    go_text = go_path.read_text(encoding='utf-8')
    package = INDICATOR_SLUG.replace('-','').replace('_','')
    go_text = re.sub(r'(?m)^package\s+\w+', 'package '+package,go_text)
    if 'import "math"' not in go_text:
        go_text = go_text.replace('package '+package,'package '+package+'\n\nimport "math"',1)
    if 'math.NaN()' not in '\n'.join(sections['testdata_test.go']) and 'var _ = math.NaN' not in go_text:
        # Go rejects an unused import when every fixture is immediately finite.
        # Retain the requested math import without inserting fabricated NaNs.
        go_text = go_text.replace('import "math"','import "math"\n\nvar _ = math.NaN',1)
    go_path.write_text(go_text,encoding='utf-8')
    zig_path = directory/'testdata.zig'
    zig_text = zig_path.read_text(encoding='utf-8')
    if 'const math = @import("std").math;' not in zig_text:
        zig_text = 'const math = @import("std").math;\n'+zig_text
    if 'const nan = math.nan(f64);' not in zig_text:
        zig_text = zig_text.replace('const math = @import("std").math;',
                                   'const math = @import("std").math;\nconst nan = math.nan(f64);',1)
    zig_path.write_text(zig_text,encoding='utf-8')
    for filename,parts in sections.items():
        _replace_section(directory/filename,'\n\n'.join(parts),'//',rust=filename.endswith('.rs'))
    return len(outputs)


if __name__ == '__main__':
    # Embedded requested INPUT_CLOSE. Auxiliary OHLC comes from local fixtures.
    INPUT_CLOSE = [91.5, 94.815, 94.375, 95.095, 93.78, 94.625, 92.53, 92.75, 90.315, 92.47, 96.125, 97.25, 98.5, 89.875, 91.0, 92.815, 89.155, 89.345, 91.625, 89.875, 88.375, 87.625, 84.78, 83.0, 83.5, 81.375, 84.44, 89.25, 86.375, 86.25, 85.25, 87.125, 85.815, 88.97, 88.47, 86.875, 86.815, 84.875, 84.19, 83.875, 83.375, 85.5, 89.19, 89.44, 91.095, 90.75, 91.44, 89.0, 91.0, 90.5, 89.03, 88.815, 84.28, 83.5, 82.69, 84.75, 85.655, 86.19, 88.94, 89.28, 88.625, 88.5, 91.97, 91.5, 93.25, 93.5, 93.155, 91.72, 90.0, 89.69, 88.875, 85.19, 83.375, 84.875, 85.94, 97.25, 99.875, 104.94, 106.0, 102.5, 102.405, 104.595, 106.125, 106.0, 106.065, 104.625, 108.625, 109.315, 110.5, 112.75, 123.0, 119.625, 118.75, 119.25, 117.94, 116.44, 115.19, 111.875, 110.595, 118.125, 116.0, 116.0, 112.0, 113.75, 112.94, 116.0, 120.5, 116.62, 117.0, 115.25, 114.31, 115.5, 115.87, 120.69, 120.19, 120.75, 124.75, 123.37, 122.94, 122.56, 123.12, 122.56, 124.62, 129.25, 131.0, 132.25, 131.0, 132.81, 134.0, 137.38, 137.81, 137.88, 137.25, 136.31, 136.25, 134.63, 128.25, 129.0, 123.87, 124.81, 123.0, 126.25, 128.38, 125.37, 125.69, 122.25, 119.37, 118.5, 123.19, 123.5, 122.19, 119.31, 123.31, 121.12, 123.37, 127.37, 128.5, 123.87, 122.94, 121.75, 124.44, 122.0, 122.37, 122.94, 124.0, 123.19, 124.56, 127.25, 125.87, 128.86, 132.0, 130.75, 134.75, 135.0, 132.38, 133.31, 131.94, 130.0, 125.37, 130.13, 127.12, 125.19, 122.0, 125.0, 123.0, 123.5, 120.06, 121.0, 117.75, 119.87, 122.0, 119.19, 116.37, 113.5, 114.25, 110.0, 105.06, 107.0, 107.87, 107.0, 107.12, 107.0, 91.0, 93.94, 93.87, 95.5, 93.0, 94.94, 98.25, 96.75, 94.81, 94.37, 91.56, 90.25, 93.94, 93.62, 97.0, 95.0, 95.87, 94.06, 94.62, 93.75, 98.0, 103.94, 107.87, 106.06, 104.5, 105.0, 104.19, 103.06, 103.42, 105.27, 111.87, 116.0, 116.62, 118.28, 113.37, 109.0, 109.7, 109.25, 107.0, 109.19, 110.0, 109.2, 110.12, 108.0, 108.62, 109.75, 109.81, 109.0, 108.75, 107.87]
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data',action='store_true',
                        help='write and verify expected arrays in all five fixtures')
    args = parser.parse_args()
    if args.generate_reference_data:
        count = generate_reference_data(INPUT_CLOSE,directory)
        print(f'{INDICATOR_SLUG}: {len(REFERENCE_CASES)} cases, {count} arrays per language, 252 values each')
    else:
        # Show a complete update loop for each named configuration.
        arrays = _load_arrays(directory/'test_testdata.py')
        for case in REFERENCE_CASES:
            indicator = MASTER_CLASS(**case['params'])
            for index,price in enumerate(INPUT_CLOSE):
                output = fixture_update(indicator,index,price,arrays)
            print(case['params'], flatten_output(indicator,output))
