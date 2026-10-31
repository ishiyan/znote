"""Metonic Williams Percent R: standalone streaming research prototype master.

Read description.md for equations, source adaptations, input contracts,
priming and porting conventions. Only Python standard-library binary64 math.
"""

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

from datetime import date, datetime, timedelta


def fill_calendar_days(records):
    """Yield (date, payload), copying the preceding FULL payload into gaps.

    records must be increasing completed daily observations. Payload can be
    a close, an OHLC tuple, or any immutable caller-owned value. No market
    holiday knowledge is required: every absent calendar date is filled.
    """
    previous_day = previous_payload = None
    for day, payload in records:
        if type(day) is not date:
            raise ValueError("calendar records require datetime.date")
        if previous_day is not None:
            if day <= previous_day:
                raise ValueError("calendar records must increase strictly")
            missing = previous_day + timedelta(days=1)
            while missing < day:
                yield missing, previous_payload
                missing += timedelta(days=1)
        yield day, payload
        previous_day, previous_payload = day, payload


class _Calendar:
    """Dates affect indexing; they are not merely optional plot metadata."""
    def __init__(self):
        self.last = None
        self.dated = None

    def validate(self, time):
        # Undated mode is allowed only under the caller's daily-grid promise.
        if isinstance(time, datetime):
            raise ValueError("use a date, not a datetime with timezone ambiguity")
        if time is not None and type(time) is not date:
            raise ValueError("time must be a date or None")
        if self.dated is not None and self.dated != (time is not None):
            raise ValueError("cannot mix dated and undated accepted observations")
        if self.last is not None and time != self.last + timedelta(days=1):
            raise ValueError("calendar gap: call fill_calendar_days before update")

    def commit(self, time):
        self.last = time
        self.dated = time is not None


class _DelayMean:
    """Bounded calendar-day ring; NaN underlying WARMUP still occupies a day."""
    def __init__(self, delays):
        self.delays = delays
        self.history = deque(maxlen=max(delays)+1)

    def update(self, value):
        self.history.append(value)
        if len(self.history) < self.history.maxlen:
            return math.nan
        values = [self.history[-1-delay] for delay in self.delays]
        if any(math.isnan(item) for item in values):
            return math.nan
        total = 0.0
        for item in values:
            total += item
        return total/len(values)

class MetonicWilliamsOutput(NamedTuple):
    value: float
    linear_percent_r: float


class MetonicWilliamsR:
    """Conventional high/low/close Williams %R, then three-delay average.

    No close-only extrema substitute is silently created. All three prices
    belong to the same completed calendar-day bar, including filled days.
    """
    def __init__(self, length=13, delay1=6939, delay2=4016, delay3=2922):
        self.length = _integer(length,'length')

        self.delay1 = _integer(delay1,'delay1')
        self.delay2 = _integer(delay2,'delay2')
        self.delay3 = _integer(delay3,'delay3')
        self.delays = (self.delay1,self.delay2,self.delay3)
        if len(set(self.delays))!=3:
            raise ValueError("three delays must be distinct")

        self.linear_warmup_bars = self.length-1
        self.warmup_bars = max(self.delays)+self.linear_warmup_bars
        self.reset()

    def reset(self):
        self.samples_seen = 0
        self.highs,self.lows = deque(maxlen=self.length),deque(maxlen=self.length)
        self.calendar = _Calendar()
        self.delay = _DelayMean(self.delays)
        self.last_value = math.nan

    @property
    def is_primed(self):
        return not math.isnan(self.last_value)

    def update(self, close, high=None, low=None, time=None):
        close = _sample(close)
        if math.isnan(close):
            return MetonicWilliamsOutput(math.nan,math.nan)
        if high is None or low is None:
            raise ValueError("conventional Williams %R requires high and low")
        high,low = _sample(high),_sample(low)
        if math.isnan(high) or math.isnan(low):
            return MetonicWilliamsOutput(math.nan,math.nan)
        if not low<=close<=high:
            raise ValueError("completed HLC bar must satisfy low <= close <= high")
        self.calendar.validate(time)
        self.highs.append(high)
        self.lows.append(low)
        linear = math.nan
        if len(self.highs)==self.length:
            maximum,minimum = max(self.highs),min(self.lows)
            # A zero range is undefined. Preserve its DAY as NaN in the ring.
            if maximum>minimum:
                linear = -100.0*(maximum-close)/(maximum-minimum)
        self.last_value = self.delay.update(linear)
        self.samples_seen += 1
        self.calendar.commit(time)
        return MetonicWilliamsOutput(self.last_value,linear)

INDICATOR_SLUG = 'metonic-williams-percent-r'
MASTER_CLASS = MetonicWilliamsR
PARAMETER_SHORTCUTS = [('length', 'L'), ('delay1', 'D1'), ('delay2', 'D2'), ('delay3', 'D3')]
REFERENCE_CASES = ({'params': {'length': 13, 'delay1': 6939, 'delay2': 4016, 'delay3': 2922},
  'what_it_tests': 'Production calendar delays: linear %R available, composite unprimed.'},
 {'params': {'length': 13, 'delay1': 19, 'delay2': 11, 'delay3': 8},
  'what_it_tests': 'Short synthetic delays give finite HLC-based composites.'},
 {'params': {'length': 1, 'delay1': 19, 'delay2': 11, 'delay3': 8},
  'what_it_tests': 'Single HLC bar underlying range.'},
 {'params': {'length': 14, 'delay1': 19, 'delay2': 11, 'delay3': 8},
  'what_it_tests': 'Conventional fourteen-day underlying window.'},
 {'params': {'length': 50, 'delay1': 100, 'delay2': 60, 'delay3': 40},
  'what_it_tests': 'Longer HLC window and larger synthetic delay buffer.'},
 {'params': {'length': 13, 'delay1': 8, 'delay2': 19, 'delay3': 11},
  'what_it_tests': 'Unsorted delays retain identical average semantics.'},
 {'params': {'length': 13, 'delay1': 239, 'delay2': 100, 'delay3': 50},
  'what_it_tests': 'First complete composite arrives at the final sample.'},
 {'params': {'length': 13, 'delay1': 240, 'delay2': 100, 'delay3': 50},
  'what_it_tests': 'Delayed underlying range still unavailable at record end.'})
OUTPUT_FIELDS = ('value', 'linear_percent_r')


def flatten_output(indicator,output):
    # Scalar filters expose VALUE; named outputs preserve each numeric field.
    if isinstance(output,(int,float)):
        return {'value':output}
    return {name:getattr(output,name) for name in OUTPUT_FIELDS}


def fixture_update(indicator,index,price,arrays):
    time = date(2000,1,1)+timedelta(days=index)
    return indicator.update(price,high=arrays['INPUT_HIGH'][index],low=arrays['INPUT_LOW'][index],time=time)

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
