"""Chapter 11 streaming research prototype master: adaptive-band-pass-indicator.

Standard library only; numerical code above fixture tooling is what to port.
The complete estimator is embedded so no sibling master is needed at runtime.
See description.md for full mathematics, source differences and initialization.
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path
from typing import NamedTuple


# These are mathematical constants. Source .707 means 1/sqrt(2), and 1.414
# means sqrt(2); preserve the design decimals .995 and .5 as printed.
TWO_PI = 2.0 * math.pi
SQRT_TWO = math.sqrt(2.0)


def _integer(value, name, minimum):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return value


def _real(value, name, minimum):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a finite real >= {minimum}')
    value = float(value)
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f'{name} must be a finite real >= {minimum}')
    return value


def _sample(value):
    # A missing sample is skipped. Infinity is invalid. Neither contaminates
    # the feedback or ages the accepted-bar counter.
    if isinstance(value, bool):
        raise ValueError('price must be a real number')
    value = float(value)
    if math.isinf(value):
        raise ValueError('price must be finite or NaN (missing)')
    return value


class _Roof:
    """Two-pole high-pass then two-pole SuperSmoother (book equation 3-3).

    State begins at zero, including the TWO absent raw closes. This is an
    explicit finite-record reference convention, shared with the existing
    periodogram master. A positive constant close creates a startup transient.
    candidate/commit separates arithmetic from mutation: an overflow rejected
    by a downstream stage cannot leave the roof one observation ahead.
    """
    def __init__(self, highpass_period, smoothing_period):
        hp = _real(highpass_period, 'highpass_period', 5.0)
        lp = _real(smoothing_period, 'smoothing_period', 2.0)
        angle = TWO_PI / (SQRT_TWO * hp)
        cosine = math.cos(angle)
        alpha = (cosine + math.sin(angle) - 1.0) / cosine
        pole = 1.0 - alpha
        a = math.exp(-SQRT_TWO * math.pi / lp)
        self.hp0 = (1.0 - alpha / 2.0) * (1.0 - alpha / 2.0)
        self.hp1 = 2.0 * pole
        self.hp2 = pole * pole  # recurrence SUBTRACTS this positive coefficient
        self.ss2 = 2.0 * a * math.cos(SQRT_TWO * math.pi / lp)
        self.ss3 = -a * a     # recurrence ADDS this negative coefficient
        self.ss1 = 1.0 - self.ss2 - self.ss3
        if not (0.0 < pole < 1.0 and 0.0 < a < 1.0 and self.ss1 > 0.0):
            raise ValueError('periods must produce finite resolvable stable coefficients')
        self.reset()

    def reset(self):
        self.x1 = self.x2 = self.h1 = self.h2 = self.f1 = self.f2 = 0.0

    def candidate(self, price):
        # All states in this expression are PREVIOUS accepted observations.
        high = (self.hp0 * (price - 2.0*self.x1 + self.x2)
                + self.hp1*self.h1 - self.hp2*self.h2)
        filtered = (self.ss1*(high+self.h1)/2.0
                    + self.ss2*self.f1 + self.ss3*self.f2)
        if not (math.isfinite(high) and math.isfinite(filtered)):
            raise ValueError('roofing arithmetic overflowed')
        return high, filtered

    def commit(self, price, high, filtered):
        self.x2, self.x1 = self.x1, price
        self.h2, self.h1 = self.h1, high
        self.f2, self.f1 = self.f1, filtered

# Only the decay differs among Chapter 11 periodogram copies. This is not
# source="book" of the separate Chapter 8 master, whose decay is fixed .995.
DFT_LAG_START = 3


class CycleState(NamedTuple):
    """Immutable diagnostics; correlations are RAW Pearson values, never colors."""
    high_pass: float
    filtered: float
    correlations: tuple[float, ...]
    smoothed_power: tuple[float, ...]
    normalized_power: tuple[float, ...]
    normalization_maximum: float
    dominant_cycle: float
    has_cycle: bool


class _CycleEstimator:
    """Embedded Chapter 11 roofed autocorrelation periodogram, no external imports.

    Work is newest-to-oldest, bin order ascending. Preserve raw correlation
    on a zero denominator, square Fourier power AGAIN before the time EMA,
    and clamp the retained real-valued centroid to the configured range.
    """
    def __init__(self, parameters, decay):
        p = parameters
        self.p = p
        self.decay = decay
        self.roof = _Roof(p.highpass_period,p.smoothing_period)
        self.periods = tuple(range(p.min_period,p.max_period+1))
        self.required_history = p.max_period+(p.averaging_length or p.max_period)
        # CCI needs old means from windows up to max_period, but requires no
        # extra filtered slots beyond max_period (these are separate histories).
        self.capacity = max(self.required_history,p.max_period+2,4)
        self.cosines = [tuple(math.cos(TWO_PI*n/period)
                             for n in range(DFT_LAG_START,p.max_period+1))
                        for period in self.periods]
        self.sines = [tuple(math.sin(TWO_PI*n/period)
                           for n in range(DFT_LAG_START,p.max_period+1))
                      for period in self.periods]
        self.reset()

    def reset(self):
        self.roof.reset()
        self.history = [0.0]*self.capacity
        self.correlations = [0.0]*(self.p.max_period+1)
        self.power = [0.0]*len(self.periods)
        self.normalized = [0.0]*len(self.periods)
        self.maximum = 0.0
        self.dominant = float(self.p.min_period)
        self.has_cycle = False

    @property
    def state(self):
        return CycleState(self.roof.h1,self.roof.f1,tuple(self.correlations),
                          tuple(self.power),tuple(self.normalized),self.maximum,
                          self.dominant,self.has_cycle)

    def candidate(self, price):
        p = self.p
        high,filtered = self.roof.candidate(price)
        history = [filtered]+self.history[:-1]
        correlations = self.correlations.copy()
        for lag in range(p.max_period+1):
            m = p.averaging_length or lag
            sx = sy = sxx = sxy = syy = 0.0
            for count in range(m):
                x,y = history[count],history[lag+count]
                sx = sx+x
                sy = sy+y
                sxx = sxx+x*x
                sxy = sxy+x*y
                syy = syy+y*y
            denominator = (m*sxx-sx*sx)*(m*syy-sy*sy)
            if not all(math.isfinite(v) for v in (sx,sy,sxx,sxy,syy,denominator)):
                raise ValueError('Pearson arithmetic overflowed')
            if denominator > 0.0:
                correlations[lag] = (m*sxy-sx*sy)/math.sqrt(denominator)
            # No Else: keep old RAW r. This differs from listing 8-2's map,
            # where a repeated rescaling of the same array changes its value.
            if not math.isfinite(correlations[lag]):
                raise ValueError('Pearson correlation overflowed')
        power = []
        for i,period in enumerate(self.periods):
            cosine_part = sine_part = 0.0
            for offset,n in enumerate(range(DFT_LAG_START,p.max_period+1)):
                cosine_part = cosine_part+correlations[n]*self.cosines[i][offset]
                sine_part = sine_part+correlations[n]*self.sines[i][offset]
            squared_sum = cosine_part*cosine_part+sine_part*sine_part
            # SqSum is already squared amplitude. The code uses SqSum^2,
            # so this is fourth power of Fourier amplitude, not plain power.
            value = .2*squared_sum*squared_sum+.8*self.power[i]
            if not math.isfinite(value):
                raise ValueError('periodogram arithmetic overflowed')
            power.append(value)
        maximum = self.decay*self.maximum
        for value in power:
            if value > maximum:
                maximum = value
        # The book leaves several zero-MaxPwr divisions unguarded. Define
        # an all-zero normalized spectrum when no energy ever existed. No
        # NaN enters feedback. CCI's explicit guard has the same zero seed.
        normalized = [v/maximum if maximum != 0.0 else 0.0 for v in power]
        sp = spx = 0.0
        for period,value in zip(self.periods,normalized):
            if value >= .5:
                spx = spx+period*value
                sp = sp+value
        dominant = self.dominant
        has_cycle = self.has_cycle
        if sp != 0.0:
            dominant = spx/sp
            has_cycle = True
        # RSI/Stochastic/CCI clamp both ends; BP explicitly clamps only low.
        # A centroid of in-range periods cannot exceed max_period, so the
        # upper clamp is equivalent on finite arithmetic for the BP listing.
        dominant = min(float(p.max_period),max(float(p.min_period),dominant))
        if not math.isfinite(dominant):
            raise ValueError('dominant period arithmetic overflowed')
        return high,history,correlations,power,normalized,maximum,dominant,has_cycle

    def commit(self, price, candidate):
        high,history,corr,power,norm,maximum,dominant,has_cycle = candidate
        self.roof.commit(price,high,history[0])
        self.history,self.correlations,self.power,self.normalized = history,corr,power,norm
        self.maximum,self.dominant,self.has_cycle = maximum,dominant,has_cycle


def _parameters(min_period,max_period,averaging_length,highpass_period,smoothing_period):
    first = _integer(min_period,'min_period',6)
    last = _integer(max_period,'max_period',first)
    avg = _integer(averaging_length,'averaging_length',0)
    if avg == 1:
        raise ValueError('averaging_length must be zero or at least two')
    hp = _real(highpass_period,'highpass_period',5.0)
    lp = _real(smoothing_period,'smoothing_period',2.0)
    return first,last,avg,hp,lp


def _inclusive_cycle_length(dominant):
    """EL For count=0 To DominantCycle-1 uses an integer counter.

    It includes all integers count <= the REAL upper bound: floor(DC-1)+1,
    equivalently floor(DC) for DC>=1. Do not round DC or use ceil(DC).
    Keep the printed expression to document integer-bound semantics.
    """
    return math.floor(dominant-1.0)+1


def _smooth(c1,c2,c3,value,previous_value,out1,out2):
    # Output smoother uses EXACTLY the roofing low-pass coefficients. It is
    # not a separately chosen EMA and does not clip its overshoot.
    result = c1*(value+previous_value)/2.0+c2*out1+c3*out2
    if not math.isfinite(result):
        raise ValueError('output smoother arithmetic overflowed')
    return result

PERIODOGRAM_DECAY = 0.995
TUNING_FACTOR = 0.9


class Parameters(NamedTuple):
    min_period: int
    max_period: int
    averaging_length: int
    highpass_period: float
    smoothing_period: float
    bandwidth: float


class BandPassOutput(NamedTuple):
    """Both plotted curves, measured DC and the 0.9*DC coefficient period.

    trigger is .9*Signal[1], not the unplotted LeadSignal source variable.
    Public fields are all NaN until the complete estimator history is present.
    """
    signal: float
    trigger: float
    dominant_cycle: float
    tuned_period: float


class BandPassState(NamedTuple):
    cycle: CycleState
    band_pass: float
    peak: float
    signal: float
    trigger: float
    tuned_period: float
    lead: float
    lead_peak: float
    lead_signal: float


class AdaptiveBandPassIndicator:
    """Chapter 11 listing 11-4: continuously tuned band-pass and plotted trigger.

    Search 10..48; correlation average 3; independent roof 48/10; bandwidth
    .3. Source tuning .9, spectral decay .995, signal-peak decay .991, and
    first-two-zero band-pass outputs are fixed, not additional parameters.
    """
    def __init__(self,min_period=10,max_period=48,averaging_length=3,
                 highpass_period=48.0,smoothing_period=10.0,bandwidth=0.3):
        controls = _parameters(min_period,max_period,averaging_length,
                               highpass_period,smoothing_period)
        width = _real(bandwidth,'bandwidth',0.0)
        if not 0.0 < width < TUNING_FACTOR*controls[0]/4.0:
            raise ValueError('bandwidth must satisfy 0 < bandwidth < .9*min_period/4')
        # Validate coefficient resolvability throughout the closed tuning range.
        # Numerical rounding can collapse a tiny positive bandwidth to gamma=1.
        for period in (controls[0],controls[1]):
            gamma = 1.0/math.cos(TWO_PI*width/(TUNING_FACTOR*period))
            alpha = gamma-math.sqrt(gamma*gamma-1.0)
            if not 0.0 < alpha < 1.0:
                raise ValueError('bandwidth must yield resolvable stable band-pass poles')
        self._parameters = Parameters(*controls,width)
        self._cycle = _CycleEstimator(self._parameters,PERIODOGRAM_DECAY)
        self.reset()

    @property
    def parameters(self):
        return self._parameters

    @property
    def min_period(self):
        return self.parameters.min_period

    @property
    def max_period(self):
        return self.parameters.max_period

    @property
    def warmup_bars(self):
        return max(self._cycle.required_history,4)-1

    @property
    def samples_seen(self):
        return self._count

    @property
    def is_primed(self):
        return self._count > self.warmup_bars

    @property
    def state(self):
        return BandPassState(self._cycle.state,self._bp1,self._peak,self._signals[0],
                             self._trigger,self._tuned,self._lead,self._lead_peak,
                             self._lead_signal)

    @property
    def output(self):
        return self._output

    def reset(self):
        self._cycle.reset()
        self._count = 0
        self._bp1 = self._bp2 = self._peak = 0.0
        self._signals = [0.0]*3
        self._trigger = self._lead = self._lead_peak = self._lead_signal = 0.0
        self._tuned = TUNING_FACTOR*self.min_period
        self._output = BandPassOutput(math.nan,math.nan,math.nan,math.nan)

    def update(self,close,time=None):
        price = _sample(close)
        if math.isnan(price):
            return BandPassOutput(math.nan,math.nan,math.nan,math.nan)
        candidate = self._cycle.candidate(price)
        history,dominant = candidate[1],candidate[6]
        tuned = TUNING_FACTOR*dominant
        # DC is real-valued. Recompute coefficients EACH accepted bar; changing
        # period does not clear past BP states or replay an old window.
        beta = math.cos(TWO_PI/tuned)
        gamma = 1.0/math.cos(TWO_PI*self.parameters.bandwidth/tuned)
        alpha = gamma-math.sqrt(gamma*gamma-1.0)
        if not 0.0 < alpha < 1.0:
            raise ValueError('adaptive band-pass poles lost numerical resolution')
        bp = (.5*(1.0-alpha)*(history[0]-history[2])
              +beta*(1.0+alpha)*self._bp1-alpha*self._bp2)
        if self._count < 2:
            bp = 0.0  # Exactly CurrentBar=1 or 2; roof/estimator still advance.
        peak = .991*self._peak
        if abs(bp) > peak:
            peak = abs(bp)
        signal = bp/peak if peak != 0.0 else self._signals[0]
        trigger = .9*self._signals[0]
        # Preserve the separately computed but UNPLOTTED source lead variables
        # in diagnostic state, without confusing LeadSignal with Plot14.
        lead = 1.3*(signal+self._signals[0]-self._signals[1]-self._signals[2])/4.0
        lead_peak = .93*self._lead_peak
        if abs(lead) > lead_peak:
            lead_peak = abs(lead)
        lead_signal = .7*lead/lead_peak if lead_peak != 0.0 else self._lead_signal
        if not all(math.isfinite(v) for v in (bp,peak,signal,trigger,lead,lead_peak,lead_signal)):
            raise ValueError('adaptive band-pass arithmetic overflowed')
        self._cycle.commit(price,candidate)
        self._bp2,self._bp1 = self._bp1,bp
        self._peak,self._trigger,self._tuned = peak,trigger,tuned
        self._lead,self._lead_peak,self._lead_signal = lead,lead_peak,lead_signal
        self._signals = [signal]+self._signals[:-1]
        self._count += 1
        self._output = (BandPassOutput(signal,trigger,dominant,tuned) if self.is_primed
                        else BandPassOutput(math.nan,math.nan,math.nan,math.nan))
        return self._output


# Fixture tooling below is not part of the streaming calculation.
INDICATOR_SLUG = 'adaptive-band-pass-indicator'
MASTER_CLASS = AdaptiveBandPassIndicator
REFERENCE_INPUT = 'close'
PARAMETER_SHORTCUTS = {'min_period': 'P0', 'max_period': 'P1', 'averaging_length': 'A', 'highpass_period': 'HP', 'smoothing_period': 'LP', 'bandwidth': 'B'}
REFERENCE_CASES = (
    {'min_period': 10, 'max_period': 48, 'averaging_length': 3, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'bandwidth': 0.3, 'what_it_tests': 'Published defaults and listing-specific periodogram decay.'},
    {'min_period': 10, 'max_period': 48, 'averaging_length': 0, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'bandwidth': 0.3, 'what_it_tests': 'Lag-dependent Pearson windows and longer priming history.'},
    {'min_period': 10, 'max_period': 48, 'averaging_length': 2, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'bandwidth': 0.3, 'what_it_tests': 'Two-sample Pearson windows with strong sign changes.'},
    {'min_period': 10, 'max_period': 48, 'averaging_length': 5, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'bandwidth': 0.3, 'what_it_tests': 'Less reactive fixed correlation window.'},
    {'min_period': 10, 'max_period': 48, 'averaging_length': 3, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'bandwidth': 0.1, 'what_it_tests': 'Narrow adaptive pass band and longer recursive transients.'},
    {'min_period': 10, 'max_period': 48, 'averaging_length': 3, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'bandwidth': 0.7, 'what_it_tests': 'Broad adaptive pass band and faster response.'},
    {'min_period': 10, 'max_period': 48, 'averaging_length': 3, 'highpass_period': 48.0, 'smoothing_period': 10.5, 'bandwidth': 0.3, 'what_it_tests': 'Fractional roofing/output SuperSmoother cutoff.'},
    {'min_period': 10, 'max_period': 48, 'averaging_length': 3, 'highpass_period': 80.0, 'smoothing_period': 20.0, 'bandwidth': 0.3, 'what_it_tests': 'Slower independent roofing and output smoothing.'},
    {'min_period': 6, 'max_period': 24, 'averaging_length': 3, 'highpass_period': 24.0, 'smoothing_period': 6.0, 'bandwidth': 0.3, 'what_it_tests': 'Compact short-cycle estimator and adaptive windows.'},
    {'min_period': 20, 'max_period': 20, 'averaging_length': 3, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'bandwidth': 0.3, 'what_it_tests': 'Single cycle bin, integer-bound window behavior and deterministic tuning.'},
    {'min_period': 10, 'max_period': 48, 'averaging_length': 204, 'highpass_period': 48.0, 'smoothing_period': 10.0, 'bandwidth': 0.3, 'what_it_tests': '252-observation history boundary: first public result at final close.'},
    {'min_period': 24, 'max_period': 60, 'averaging_length': 3, 'highpass_period': 60.0, 'smoothing_period': 12.0, 'bandwidth': 0.3, 'what_it_tests': 'Longer-cycle estimator and adaptive windows.'},
)
# All 48 family cases confirmed by the user on 2026-10-22.
REFERENCE_CASES_CONFIRMED = True


def _parameter_token(value):
    if isinstance(value, bool):
        return '1' if value else '0'
    return format(value, '.15g').replace('.', '_').replace('-', 'm')


def _case_suffix(case):
    return '_'.join(PARAMETER_SHORTCUTS[name]+_parameter_token(value)
                    for name, value in case.items() if name != 'what_it_tests')


def _parameter_comment(case):
    return ', '.join(f'{key}={value}' for key, value in case.items()
                     if key != 'what_it_tests') + '; input=' + REFERENCE_INPUT


def _float_literal(value, nan):
    if math.isnan(value):
        return nan
    if not math.isfinite(value):
        raise ValueError('cannot serialize infinite reference output')
    literal = format(value, '.15g')  # 15 significant digits, only at export.
    if '.' not in literal and 'e' not in literal:
        literal += '.0'
    return literal


def _array_body(values, indent, nan):
    # These masters have scalar components. Keep six literals per line in
    # every language; NaN spelling is the only change to the numeric tokens.
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
        result = original.rstrip()+'\n\n'+block+'\n'
    path.write_text(result, encoding='utf-8')


def _run_reference(case,inputs):
    indicator = MASTER_CLASS(**{k:v for k,v in case.items() if k != 'what_it_tests'})
    outputs = [indicator.update(close) for close in inputs['INPUT_CLOSE']]
    return {field.upper():[getattr(out,field) for out in outputs]
            for field in outputs[0]._fields}


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
            name = 'EXPECTED_'+_case_suffix(case)+'_'+component
            if name in arrays:
                raise ValueError('duplicate expected name')
            arrays[name] = (case, values)
            sections.append(f"# {case['what_it_tests']}\n# {_parameter_comment(case)}\n"
                            +f'{name} = [\n'+_array_body(values, '    ', 'NaN')+'\n]')
    _write_section(python_path, '\n\n'.join(sections), '#')
    # Reopen Python literals and verify dimensions, values, and every NaN.
    # All other languages translate this authoritative rounded Python data.
    written = _load_arrays(python_path)
    if {n for n in written if n.startswith('EXPECTED_')} != set(arrays):
        raise ValueError('missing or unexpected Python reference arrays')
    for name, (case, raw) in arrays.items():
        actual = written[name]
        if len(actual) != 252:
            raise ValueError(f'incorrect dimensions: {name}')
        for source, literal in zip(raw, actual):
            if math.isnan(source):
                if not math.isnan(literal):
                    raise ValueError(f'incorrect NaN mask: {name}')
            elif literal != float(_float_literal(source, 'NaN')):
                raise ValueError(f'incorrect 15-digit value: {name}')
    translated = {language: [] for language in ('go', 'ts', 'rs', 'zig')}
    for name, (case, raw) in arrays.items():
        suffix = name.removeprefix('EXPECTED_')
        values = written[name]
        comments = f"// {case['what_it_tests']}\n// {_parameter_comment(case)}\n"
        translated['go'].append(comments+f'var expected{suffix} = []float64{{\n'
                                +_array_body(values, '\t', 'math.NaN()')+'\n}')
        translated['ts'].append(comments+f'export const expected{suffix}: number[] = [\n'
                                +_array_body(values, '    ', 'NaN')+'\n];')
        translated['rs'].append(comments+f'pub fn expected_{suffix.lower()}() -> Vec<f64> {{\n    vec![\n'
                                +_array_body(values, '        ', 'f64::NAN')+'\n    ]\n}')
        translated['zig'].append(comments+f'pub fn expected{suffix}() [252]f64 {{\n    return .{{\n'
                                 +_array_body(values, '        ', 'nan')+'\n    };\n}')
    # Add imports only when expected NaNs are actually generated, so copied
    # Go input-only fixtures compile before parameter approval as well.
    go_path = directory/'testdata_test.go'
    text = go_path.read_text(encoding='utf-8')
    package = INDICATOR_SLUG.replace('-', '').replace('_', '')
    if 'import "math"' not in text:
        text = text.replace(f'package {package}\n', f'package {package}\n\nimport "math"\n', 1)
        go_path.write_text(text, encoding='utf-8')
    for language, filename in [('go', 'testdata_test.go'), ('ts', 'testdata.ts'),
                               ('rs', 'testdata.rs'), ('zig', 'testdata.zig')]:
        _write_section(directory/filename, '\n\n'.join(translated[language]), '//')
    print(f'Verified {len(arrays)} expected arrays for {len(REFERENCE_CASES)} cases in Python; translated all five languages.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-reference-data',action='store_true')
    args = parser.parse_args()
    # Exact shared 252 closing prices embedded for an independent demo.
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
        generate_reference_data(Path(__file__).resolve().parent,{'INPUT_CLOSE':INPUT_CLOSE})
    else:
        indicator = MASTER_CLASS()
        outputs = [indicator.update(close) for close in INPUT_CLOSE]
        print(f'{INDICATOR_SLUG}: {len(outputs)} closes; warmup={indicator.warmup_bars}')
        print('Last output:',outputs[-1])
        print(f'Reference cases={len(REFERENCE_CASES)}; confirmed={REFERENCE_CASES_CONFIRMED}')
