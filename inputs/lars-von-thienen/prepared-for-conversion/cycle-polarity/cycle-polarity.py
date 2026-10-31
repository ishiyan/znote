"""Cycle Polarity: standalone streaming research prototype master.

Read description.md for equations, source adaptations, input contracts,
priming and porting conventions. Only Python standard-library binary64 math.
"""

# Source-derived numerical sections: © 2017 Lars von Thienen / WhenToTrade.
# Book: Decoding the Hidden Market Rhythm, Part 1: Dynamic Cycles.
# https://www.whentotrade.com/ ; https://creativecommons.org/licenses/by/4.0/
# Streaming, startup and source repairs are identified in description.md.

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

def hp_trend(values, smoothing):
    """Complete source pentadiagonal HP solver, oldest observation first.

    Source: Lars von Thienen, hp_filter.cpp, CC BY 4.0 (2017).
    The forward loop is retained in its published operation order. The
    backward loop returns all trends; the last forward value is its endpoint.
    Unlike a streaming wrapper, this BATCH helper can revise old estimates.
    """
    n = len(values)
    if n < 6:
        raise ValueError("HP source solver requires at least six observations")
    smoothing = _real(smoothing, 'smoothing')
    data = [_sample(value) for value in values]
    if any(math.isnan(value) for value in data):
        raise ValueError("HP batch input must be finite")
    # Diagonals of I + lambda * D^T D, with natural endpoint conditions.
    a = [6.0*smoothing+1.0] * n
    b = [-4.0*smoothing] * n
    c = [smoothing] * n
    a[0] = a[-1] = 1.0+smoothing
    a[1] = a[-2] = 1.0+5.0*smoothing
    b[0] = b[-2] = -2.0*smoothing
    b[-1] = c[-1] = c[-2] = 0.0
    h1 = h2 = h3 = h4 = h5 = 0.0
    hh2 = hh3 = hh5 = 0.0
    for i in range(n):
        # In-place arrays become elimination coefficients, not price history.
        z = _finite(a[i]-h4*h1-hh5*hh2)
        if z <= 0.0:
            raise ValueError("HP elimination lost positive definiteness")
        hb = b[i]
        hh1 = h1
        h1 = (hb-h4*h2)/z
        b[i] = h1
        hc = c[i]
        hh2 = h2
        h2 = hc/z
        c[i] = h2
        a[i] = _finite((data[i]-hh3*hh5-h3*h4)/z)
        hh3 = h3
        h3 = a[i]
        h4 = hb-h5*hh1
        hh5 = h5
        h5 = hc
    output = [0.0]*n
    h2 = 0.0
    h1 = a[-1]
    output[-1] = h1
    for i in range(n-1, 0, -1):
        output[i-1] = _finite(a[i-1]-b[i-1]*h1-c[i-1]*h2)
        h2, h1 = h1, output[i-1]
    return output


def _cycle_data(values, smoothing):
    # smoothing == 0 intentionally disables detrending; it does NOT request
    # the HP residual at lambda=0, which would be identically zero.
    if smoothing == 0.0:
        return list(values)
    trend = hp_trend(values, smoothing)
    return [_finite(value-base) for value, base in zip(values, trend)]

class CycleModel(NamedTuple):
    """phase is a SINE phase at the FIRST sample of the analysis window."""
    period: float
    amplitude: float
    phase: float
    trough_offset: float


def goertzel(values, period):
    """Published single-period GDFT; no taper, centering, or peak selection.

    Source: Lars von Thienen, goertzel.cpp, CC BY 4.0 (2017).
    Standard-library pi replaces PI; every calculation is binary64.
    """
    period = _real(period, 'period', 2.0000000000000004)
    n = len(values)
    if not n:
        raise ValueError("Goertzel needs observations")
    omega = 2.0*math.pi/period
    sine, cosine = math.sin(omega), math.cos(omega)
    coefficient = 2.0*cosine
    q1 = q2 = 0.0
    for value in values:
        value = _sample(value)
        if math.isnan(value):
            raise ValueError("Goertzel batch input must be finite")
        q0 = _finite(coefficient*q1-q2+value)
        q2, q1 = q1, q0
    r1, i1 = q1-q2*cosine, q2*sine
    cn, sn = math.cos((n-1)*omega), math.sin((n-1)*omega)
    real = _finite(r1*cn+i1*sn)
    imaginary = _finite(i1*cn-r1*sn)
    # Keep published normalization. Using hypot changes operation/rounding.
    amplitude = _finite(2.0*math.sqrt(_finite(real*real+imaginary*imaginary))/n)
    if amplitude == 0.0:
        # A zero vector has no phase. atan2(0,0) would invent a sine phase.
        return CycleModel(period, 0.0, math.nan, math.nan)
    phase = math.pi/2.0 + math.atan2(imaginary, real)
    offset = period*(0.75-phase/(2.0*math.pi))
    return CycleModel(period, amplitude, phase, offset)


def cycle_value(model, offset):
    # A zero-amplitude wave is zero even though its phase is unavailable.
    if model.amplitude == 0.0:
        return 0.0
    return model.amplitude*math.sin(2.0*math.pi*offset/model.period+model.phase)


def cycle_slope(model, offset):
    # Analytic derivative is in price units per bar, distinct from A/P.
    if model.amplitude == 0.0:
        return 0.0
    omega = 2.0*math.pi/model.period
    return model.amplitude*omega*math.cos(omega*offset+model.phase)

def _fit_window(prices, smoothing, periods):
    values = _cycle_data(prices, smoothing)
    return tuple(goertzel(values, period) for period in periods)

class PolarityOutput(NamedTuple):
    polarity: float
    short_value: float
    long_value: float
    short_slope: float
    long_slope: float


def cycle_polarity(short_slope, long_slope, tolerance=0.0):
    """Both rising: +1; both falling: -1; disagreement/flat: 0."""
    short_slope, long_slope = _sample(short_slope),_sample(long_slope)
    tolerance = _real(tolerance,'tolerance')
    if math.isnan(short_slope) or math.isnan(long_slope):
        return math.nan
    if short_slope>tolerance and long_slope>tolerance:
        return 1.0
    if short_slope<-tolerance and long_slope<-tolerance:
        return -1.0
    return 0.0


class CyclePolarity:
    """Configured two-cycle rolling fits plus the book's polarity rule."""
    def __init__(self, window=100, short_period=20.0, long_period=40.0,
                 smoothing=1600.0, tolerance=0.0):
        self.window = _integer(window,'window',6)
        self.short_period = _real(short_period,'short_period',2.0000000000000004)
        self.long_period = _real(long_period,'long_period',2.0000000000000004)
        if self.short_period>=self.long_period:
            raise ValueError("short_period must be smaller than long_period")
        self.smoothing = _real(smoothing,'smoothing')
        self.tolerance = _real(tolerance,'tolerance')
        self.warmup_bars = self.window-1
        self.reset()

    def reset(self):
        self.samples_seen = 0
        self.prices = deque(maxlen=self.window)

    @property
    def is_primed(self):
        return len(self.prices)==self.window

    def update(self, price):
        price = _sample(price)
        if math.isnan(price):
            return PolarityOutput(*(math.nan,)*5)
        prices = (list(self.prices)+[price])[-self.window:]
        models = _fit_window(prices,self.smoothing,(self.short_period,self.long_period)) if len(prices)==self.window else ()
        output = PolarityOutput(*(math.nan,)*5)
        if models:
            short,long = models
            s1,s2 = cycle_slope(short,self.window-1),cycle_slope(long,self.window-1)
            output = PolarityOutput(cycle_polarity(s1,s2,self.tolerance),
                                    cycle_value(short,self.window-1),cycle_value(long,self.window-1),s1,s2)
        self.prices.append(price)
        self.samples_seen += 1
        return output

INDICATOR_SLUG = 'cycle-polarity'
MASTER_CLASS = CyclePolarity
PARAMETER_SHORTCUTS = [('window', 'W'), ('short_period', 'S'), ('long_period', 'L'), ('smoothing', 'HP'), ('tolerance', 'T')]
REFERENCE_CASES = ({'params': {'window': 100,
             'short_period': 20.0,
             'long_period': 40.0,
             'smoothing': 1600.0,
             'tolerance': 0.0},
  'what_it_tests': 'Default short/long cycle alignment on HP residual.'},
 {'params': {'window': 100,
             'short_period': 20.0,
             'long_period': 40.0,
             'smoothing': 0.0,
             'tolerance': 0.0},
  'what_it_tests': 'Raw-price cycles without preprocessing.'},
 {'params': {'window': 60,
             'short_period': 10.0,
             'long_period': 20.0,
             'smoothing': 1600.0,
             'tolerance': 0.0},
  'what_it_tests': 'Faster harmonic cycle pair.'},
 {'params': {'window': 200,
             'short_period': 40.0,
             'long_period': 80.0,
             'smoothing': 1600.0,
             'tolerance': 0.0},
  'what_it_tests': 'Longer cycle pair and observation window.'},
 {'params': {'window': 100,
             'short_period': 17.5,
             'long_period': 31.0,
             'smoothing': 1600.0,
             'tolerance': 0.0},
  'what_it_tests': 'Fractional incommensurate cycle periods.'},
 {'params': {'window': 100,
             'short_period': 20.0,
             'long_period': 40.0,
             'smoothing': 1600.0,
             'tolerance': 0.1},
  'what_it_tests': 'Flat-slope tolerance defines a neutral region.'},
 {'params': {'window': 100,
             'short_period': 20.0,
             'long_period': 40.0,
             'smoothing': 1600.0,
             'tolerance': 1000.0},
  'what_it_tests': 'Very large tolerance forces all fitted slopes into neutral.'},
 {'params': {'window': 253,
             'short_period': 20.0,
             'long_period': 40.0,
             'smoothing': 1600.0,
             'tolerance': 0.0},
  'what_it_tests': 'Overlong observation window remains unprimed.'})
OUTPUT_FIELDS = ('polarity', 'short_value', 'long_value', 'short_slope', 'long_slope')


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
