"""Portable research core for the seven scanner/model candidates.

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

class BartelsOutput(NamedTuple):
    score: float
    genuine_percent: float
    segments: float


def bartels_score(values, period, max_segments=5, min_segments=2):
    """Harmonic-segment consistency score from BartelsScore.cpp, CC BY 4.0.

    Full-precision pi replaces 3.1415926535. Invalid/no-energy evidence is
    NaN, not the source's misleading no-segment raw zero (100% genuine).
    period is restricted to an integer so phase and segmentation agree.
    """
    period = _integer(period, 'period', 3)
    max_segments = _integer(max_segments, 'max_segments', 2)
    min_segments = _integer(min_segments, 'min_segments', 2)
    if min_segments>max_segments:
        raise ValueError("min_segments must not exceed max_segments")
    data = [_sample(value) for value in values]
    if any(math.isnan(value) for value in data):
        raise ValueError("Bartels batch data must be finite")
    segments = min(len(data)//period,max_segments)
    if segments < min_segments:
        return BartelsOutput(math.nan,math.nan,float(segments))
    total_a = total_b = total_energy = 0.0
    for segment in range(segments):
        a = b = 0.0
        for j in range(period):
            x = segment*period+j
            # Source phase starts at x+1; preserve that convention and order.
            angle = (360.0/period*(x+1))/180.0*math.pi
            a += math.sin(angle)*data[x]
            b += math.cos(angle)*data[x]
        total_a += a
        total_b += b
        total_energy = _finite(total_energy+a*a+b*b)
    if total_energy == 0.0:
        return BartelsOutput(math.nan,math.nan,float(segments))
    average_a, average_b = total_a/segments,total_b/segments
    amplitude = math.sqrt(average_a*average_a+average_b*average_b)
    rms_amplitude = math.sqrt(total_energy/segments)
    reference = rms_amplitude/math.sqrt(segments)
    ratio = amplitude/reference
    # exp(-r^2) avoids overflow in the source's equivalent 1/exp(r^2).
    score = math.exp(-ratio*ratio)
    return BartelsOutput(score,100.0*(1.0-score),float(segments))



from dataclasses import dataclass, asdict
from datetime import date, timedelta
from itertools import combinations
import csv
import json
from pathlib import Path


@dataclass(frozen=True)
class ScanConfig:
    """Explicit reconstruction parameters, not undisclosed WTT settings.

    Integer wavelengths keep Bartels segmentation and spectral periods equal.
    No dynamic HP adjustment or taper is inferred from the books.
    """
    window: int = 200
    min_period: int = 5
    max_period: int = 80
    smoothing: float = 1600.0
    genuine_threshold: float = 49.0
    phase_cycles: float = 2.0
    top_k: int = 3
    peak_distance: int = 2
    max_segments: int = 5

    def __post_init__(self):
        for name, minimum in (('window', 6), ('min_period', 3),
                              ('max_period', 3), ('top_k', 1),
                              ('peak_distance', 1), ('max_segments', 2)):
            _integer(getattr(self, name), name, minimum)
        for name in ('smoothing', 'genuine_threshold', 'phase_cycles'):
            object.__setattr__(self, name, _real(getattr(self, name), name))
        if self.min_period > self.max_period:
            raise ValueError('min_period must not exceed max_period')
        if self.genuine_threshold > 100:
            raise ValueError('genuine_threshold must be in [0, 100]')
        if self.phase_cycles != 0 and self.phase_cycles < 1:
            raise ValueError('phase_cycles is zero (full window) or >= 1')


class RankedCycle(NamedTuple):
    # phase is normalized SINE phase AT THE CURRENT ANALYSIS ENDPOINT.
    # amplitude/strength describe full-window detection, fit_amplitude describes
    # the separate recent-window waveform. Never rank by the latter by accident.
    period: float
    amplitude: float
    phase: float
    strength: float
    genuine_percent: float
    segments: float
    fit_amplitude: float
    fit_samples: float
    value: float
    slope: float
    eta_top: float
    eta_bottom: float


CYCLE_FIELDS = RankedCycle._fields
EMPTY_CYCLE = RankedCycle(*([math.nan] * len(CYCLE_FIELDS)))


class Heatmap(NamedTuple):
    # Structural match to zpano Heatmap; parameter axis is period in bars.
    time: object
    parameter_first: float
    parameter_last: float
    parameter_resolution: float
    value_min: float
    value_max: float
    values: list[float]

    def is_empty(self):
        return not self.values


class ScanOutput(NamedTuple):
    spectrum: Heatmap
    genuine_percent: tuple[float, ...]
    cycles: tuple[RankedCycle, ...]
    accepted_count: float


def empty_scan(config):
    count = config.max_period - config.min_period + 1
    return ScanOutput(Heatmap(None, float(config.min_period),
                             float(config.max_period), 1.0, math.nan, math.nan,
                             [math.nan] * count),
                      tuple([math.nan] * count),
                      tuple([EMPTY_CYCLE] * config.top_k), math.nan)


def phase_state(phase):
    """Continuous reconstruction of the -100..100 phase state.

    This smooth sine mapping reproduces extrema/range, not proprietary text-bin
    values. The books supply examples but no complete phase-region boundaries.
    """
    phase = _sample(phase)
    return math.nan if math.isnan(phase) else 100.0 * math.sin(phase)


def phase_status(phase):
    # Explicit quadrant names avoid inventing undisclosed proprietary statuses.
    if math.isnan(phase):
        return 'unavailable'
    angle = phase % (2.0 * math.pi)
    if angle < math.pi / 2.0:
        return 'rising toward top'
    if angle < math.pi:
        return 'falling from top'
    if angle < 3.0 * math.pi / 2.0:
        return 'falling toward bottom'
    return 'rising from bottom'


def modeled_value(cycle, offset=0.0):
    # offset=0 is the endpoint; negative offsets reconstruct earlier samples.
    return cycle.fit_amplitude * math.sin(cycle.phase + 2.0*math.pi*offset/cycle.period)


def scan_cycles(prices, config):
    """Batch detection/validation/ranking, reusable by rolling and annual tools.

    Window length need not equal config.window here: batch CLI analyzes exactly
    the requested range. RollingScanner alone imposes the fixed-size window.
    """
    prices = [_sample(value) for value in prices]
    if len(prices) < 6 or any(math.isnan(value) for value in prices):
        raise ValueError('scan requires >= 6 finite, oldest-first prices')
    residual = _cycle_data(prices, config.smoothing)
    periods = list(range(config.min_period, config.max_period + 1))
    models = [goertzel(residual, period) for period in periods]
    # Validate ORIGINAL prices, not HP residuals that may contain artificial
    # cycles. Take the most recent m whole cycles, with no zero padding.
    evidence = []
    for period in periods:
        segments = min(len(prices) // period, config.max_segments)
        evidence.append(bartels_score(prices[-segments*period:] if segments else [],
                                      period, config.max_segments, 2))
    amplitudes = [model.amplitude for model in models]
    candidates = []
    for i, (model, score) in enumerate(zip(models, evidence)):
        # Plateau tie: the shortest member wins. Boundary peaks are one-sided;
        # a one-period grid has no neighbors and is a valid candidate.
        left = amplitudes[i-1] if i else -math.inf
        right = amplitudes[i+1] if i+1 < len(amplitudes) else -math.inf
        peak = model.amplitude > 0 and model.amplitude > left and model.amplitude >= right
        if not peak or math.isnan(score.genuine_percent) or score.genuine_percent <= config.genuine_threshold:
            continue
        candidates.append((model, score))
    # Rank the price influence per bar A/P, as disclosed in the whitepaper.
    # Suppression follows validation/ranking: an invalid peak cannot suppress
    # a valid neighbor. Exact strength ties prefer the shorter wavelength.
    candidates.sort(key=lambda item: (-item[0].amplitude/item[0].period, item[0].period))
    accepted = []
    for model, score in candidates:
        if any(abs(model.period - prior.period) < config.peak_distance for prior in accepted):
            continue
        fit_n = (len(prices) if config.phase_cycles == 0 else
                 min(len(prices), max(6, math.ceil(config.phase_cycles * model.period))))
        # Re-detrend the recent raw subset, rather than slicing a full-window
        # residual with different HP endpoint conditions. This is a declared
        # reconstruction of the undisclosed recent-phase procedure.
        fit = model if fit_n == len(prices) else goertzel(
            _cycle_data(prices[-fit_n:], config.smoothing), model.period)
        phase = (fit.phase + 2.0*math.pi*(fit_n-1)/model.period) % (2.0*math.pi)
        omega = 2.0*math.pi/model.period
        value = fit.amplitude * math.sin(phase)
        slope = fit.amplitude * omega * math.cos(phase)
        eta_top = ((math.pi/2.0 - phase) % (2.0*math.pi)) / omega
        eta_bottom = ((3.0*math.pi/2.0 - phase) % (2.0*math.pi)) / omega
        accepted.append(RankedCycle(model.period, model.amplitude, phase,
                                    model.amplitude/model.period,
                                    score.genuine_percent, score.segments,
                                    fit.amplitude, float(fit_n), value, slope,
                                    eta_top, eta_bottom))
    # Unused ranks are NaN; count can legitimately be zero after full priming.
    top = tuple(accepted[:config.top_k])
    top += tuple([EMPTY_CYCLE] * (config.top_k-len(top)))
    spectrum = Heatmap(None, float(config.min_period), float(config.max_period),
                       1.0, min(amplitudes), max(amplitudes), list(amplitudes))
    return ScanOutput(spectrum, tuple(item.genuine_percent for item in evidence),
                      top, float(len(accepted)))


class RollingScanner:
    """Causal rolling pipeline; full N prices prime the analysis, not a cycle.

    Lack of an accepted cycle after priming is a legitimate missing output.
    Validation and calculation happen before the history is committed.
    """
    def __init__(self, window=200, min_period=5, max_period=80, smoothing=1600.0,
                 genuine_threshold=49.0, phase_cycles=2.0, top_k=3,
                 peak_distance=2, max_segments=5):
        self.config = ScanConfig(window, min_period, max_period, smoothing,
                                 genuine_threshold, phase_cycles, top_k,
                                 peak_distance, max_segments)
        self.warmup_bars = window-1
        self.reset()

    def reset(self):
        self.prices = deque(maxlen=self.config.window)
        self.samples_seen = 0

    @property
    def is_primed(self):
        return len(self.prices) == self.config.window

    def update(self, price):
        price = _sample(price)
        if math.isnan(price):
            return empty_scan(self.config)
        prices = (list(self.prices) + [price])[-self.config.window:]
        result = scan_cycles(prices, self.config) if len(prices) == self.config.window else empty_scan(self.config)
        self.prices.append(price)
        self.samples_seen += 1
        return result


class DominantMarketVibration(RollingScanner):
    def update(self, price):
        # The dominant vibration is the first accepted A/P rank, not maximum A.
        return super().update(price).cycles[0]


def centered_mean(values, center, length):
    """Integer-centered MA; even length uses two half-weight endpoints.

    An even L spans L+1 observations: average the two length-L windows whose
    centers straddle the integer center. Odd L spans L observations.
    Missing support returns NaN; it is never extrapolated with future values.
    """
    _integer(length, 'length')
    half = length // 2
    if center-half < 0 or center+half >= len(values):
        return math.nan
    if length % 2:
        return math.fsum(values[center-half:center+half+1])/length
    middle = math.fsum(values[center-half+1:center+half])
    return (0.5*values[center-half] + middle + 0.5*values[center+half])/length


class ExplorerOutput(NamedTuple):
    value: float
    period: float
    phase: float
    eta_top: float
    eta_bottom: float
    highlighter: float
    highlighter_index: float
    fitted_at_highlighter: float


class DynamicCycleExplorer(RollingScanner):
    def update(self, price):
        output = super().update(price)
        cycle = output.cycles[0]
        if math.isnan(cycle.period):
            return ExplorerOutput(*([math.nan] * 8))
        long_length = int(cycle.period)
        short_length = max(2, math.floor(cycle.period/2.0 + 0.5))
        delay = long_length // 2
        prices = list(self.prices)
        center = len(prices)-1-delay
        highlighter = centered_mean(prices, center, short_length) - centered_mean(prices, center, long_length)
        # Dynamic selection may change the delay/index between updates. The
        # index is mandatory metadata; do not plot this at the current bar.
        index = float(self.samples_seen-1-delay) if math.isfinite(highlighter) else math.nan
        fitted = modeled_value(cycle, -delay) if math.isfinite(highlighter) else math.nan
        return ExplorerOutput(cycle.value, cycle.period, cycle.phase, cycle.eta_top,
                              cycle.eta_bottom, highlighter, index, fitted)


class PhaseOutput(NamedTuple):
    value: float
    period: float
    phase: float


class CyclePhaseScore(RollingScanner):
    def update(self, price):
        cycle = super().update(price).cycles[0]
        return PhaseOutput(phase_state(cycle.phase), cycle.period, cycle.phase)


class PhasingOutput(NamedTuple):
    value: float
    short_score: float
    long_score: float
    short_period: float
    long_period: float


class PhasingOscillator:
    """Independently detect in disjoint short/long ranges, then sum states."""
    lower, upper = -150.0, 150.0

    def __init__(self, window=200, short_min=5, short_max=30, long_min=31,
                 long_max=80, smoothing=1600.0, genuine_threshold=49.0,
                 phase_cycles=2.0):
        _integer(short_max, 'short_max', 3)
        _integer(long_min, 'long_min', 3)
        if short_max >= long_min:
            raise ValueError('short and long search ranges must be disjoint and ordered')
        self.short = CyclePhaseScore(window, short_min, short_max, smoothing,
                                     genuine_threshold, phase_cycles, 1)
        self.long = CyclePhaseScore(window, long_min, long_max, smoothing,
                                    genuine_threshold, phase_cycles, 1)
        self.warmup_bars = window-1

    def reset(self):
        self.short.reset()
        self.long.reset()

    @property
    def is_primed(self):
        return self.short.is_primed and self.long.is_primed

    def update(self, price):
        # Validate before either scanner sees the sample. Both have the same
        # window; an ordinary missing sample does not advance either history.
        price = _sample(price)
        short, long = self.short.update(price), self.long.update(price)
        return PhasingOutput(short.value+long.value, short.value, long.value,
                             short.period, long.period)


def pearson(left, right):
    """Population centered Pearson correlation; constant inputs are undefined."""
    if len(left) != len(right) or not left:
        raise ValueError('correlation requires nonempty equal-length vectors')
    a, b = math.fsum(left)/len(left), math.fsum(right)/len(right)
    x, y = [v-a for v in left], [v-b for v in right]
    xx, yy = math.fsum(v*v for v in x), math.fsum(v*v for v in y)
    if xx == 0 or yy == 0:
        return math.nan
    return max(-1.0, min(1.0, math.fsum(u*v for u,v in zip(x,y))/math.sqrt(xx*yy)))


def choose_subset(target, waves, periods, max_components=7):
    """Exhaustive subsets of a bounded pool using covariance/Gram sums.

    The score equals correlation(target, sum(waves_in_subset)); no amplitude
    refit, sign inversion or greedy replacement is added. Cache inner products
    so each candidate combination costs O(k^2) rather than O(N*k).
    """
    _integer(max_components, 'max_components')
    if not waves or len(waves) != len(periods) or len(waves) > 16:
        raise ValueError('require 1..16 candidate waves and matching periods')
    n = len(target)
    if n < 6 or any(len(wave) != n for wave in waves):
        raise ValueError('target and waves must share >= 6 samples')
    target_mean = math.fsum(target)/n
    tc = [value-target_mean for value in target]
    centered = []
    for wave in waves:
        mean = math.fsum(wave)/n
        centered.append([value-mean for value in wave])
    energy = math.fsum(value*value for value in tc)
    if energy == 0:
        raise ValueError('constant target has no defined correlation')
    cov = [math.fsum(a*b for a,b in zip(tc,wave)) for wave in centered]
    gram = [[math.fsum(a*b for a,b in zip(left,right)) for right in centered]
            for left in centered]
    best, best_score, best_key, checked = None, -math.inf, None, 0
    for count in range(1, min(max_components,len(waves))+1):
        for subset in combinations(range(len(waves)), count):
            checked += 1
            numerator = math.fsum(cov[i] for i in subset)
            denominator = math.fsum(gram[i][j] for i in subset for j in subset)
            if denominator <= 0:
                continue
            score = max(-1.0, min(1.0, numerator/math.sqrt(energy*denominator)))
            key = (count, tuple(sorted(periods[i] for i in subset)))
            if score > best_score+1e-12 or (abs(score-best_score) <= 1e-12 and key < best_key):
                best, best_score, best_key = subset, score, key
    if best is None or best_score <= 0:
        raise ValueError('no positive-correlation annual subset')
    return best, best_score, checked


def fit_annual_values(prices, year, min_period=5, max_period=125,
                      smoothing=1600.0, genuine_threshold=49.0,
                      candidate_pool=10, max_components=7, peak_distance=2):
    """Numerical annual fit. Dated completeness is enforced by decode_annual.

    phase_cycles=0 is essential: reconstruct the COMPLETE historical year,
    rather than projecting a phase fit that describes only its final subset.
    """
    _integer(year, 'year')
    _integer(candidate_pool, 'candidate_pool')
    _integer(max_components, 'max_components')
    if candidate_pool > 16 or max_components > 7:
        raise ValueError('candidate_pool <= 16 and max_components <= 7')
    config = ScanConfig(len(prices), min_period, max_period, smoothing,
                        genuine_threshold, 0.0, candidate_pool, peak_distance)
    scan = scan_cycles(prices, config)
    cycles = [cycle for cycle in scan.cycles if math.isfinite(cycle.period)]
    if not cycles:
        raise ValueError('no accepted annual cycles; inspect scanner diagnostics')
    n = len(prices)
    waves = [[modeled_value(cycle, i-(n-1)) for i in range(n)] for cycle in cycles]
    target = _cycle_data(prices, smoothing)
    subset, correlation, checked = choose_subset(target, waves,
                                                [cycle.period for cycle in cycles], max_components)
    selected = [cycles[i] for i in subset]
    selected.sort(key=lambda cycle: cycle.period)
    # Saved phases use the FIRST trading observation as origin, with zero-based
    # ordinal indices. Year boundaries are dates, never approximate 252-day lags.
    components = [dict(period=c.period, amplitude=c.fit_amplitude,
                       phase=(c.phase-2.0*math.pi*(n-1)/c.period) % (2.0*math.pi),
                       strength=c.strength, genuine_percent=c.genuine_percent)
                  for c in selected]
    return dict(schema='lvt-annual-cycle-model', version=1, research_reconstruction=True,
                year=year, sample_count=n, origin='first-observed-trading-day, zero-based ordinal',
                phase_convention='sine radians at ordinal zero', components=components,
                correlation=correlation, subsets_checked=checked, candidate_count=len(cycles),
                config=dict(asdict(config), candidate_pool=candidate_pool, max_components=max_components))


def annual_wave(model, index):
    return math.fsum(c['amplitude']*math.sin(2.0*math.pi*index/c['period']+c['phase'])
                     for c in model['components'])


class AnnualWaveReader:
    """Sequential model playback, no price fitting or price-input pretense."""
    def __init__(self, model):
        validate_annual_model(model)
        self.model = model
        self.reset()

    def reset(self):
        self.index = 0

    def update(self):
        value = annual_wave(self.model, self.index)
        self.index += 1
        return value


def validate_dates(dates, year=None):
    if not dates or any(type(value) is not date for value in dates):
        raise ValueError('require nonempty datetime.date sequence')
    if any(a >= b for a,b in zip(dates,dates[1:])):
        raise ValueError('dates must be unique and strictly increasing')
    if year is not None and any(value.year != year for value in dates):
        raise ValueError('every date must belong to the requested year')


def read_prices(path):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not {'date','close'} <= set(reader.fieldnames):
            raise ValueError('CSV requires date,close columns')
        rows = [(date.fromisoformat(row['date']), _sample(row['close'])) for row in reader]
    validate_dates([day for day,_ in rows])
    if any(not math.isfinite(value) for _,value in rows):
        raise ValueError('CSV closes must be finite; rows are never silently dropped')
    return rows


def read_calendar(path):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or 'date' not in reader.fieldnames:
            raise ValueError('calendar CSV requires date column')
        dates = [date.fromisoformat(row['date']) for row in reader]
    validate_dates(dates)
    return dates


def decode_annual(records, year, as_of=None, expected_dates=None,
                  confirm_complete=False, **parameters):
    _integer(year, 'year')
    as_of = date.today() if as_of is None else as_of
    if type(as_of) is not date or as_of < date(year+1,1,1):
        raise ValueError('annual decoding requires a completed year as of the analysis date')
    validate_dates([day for day,_ in records])
    rows = [(day,value) for day,value in records if day.year == year]
    dates = [day for day,_ in rows]
    validate_dates(dates, year)
    if expected_dates is not None:
        validate_dates(expected_dates, year)
        if dates != expected_dates:
            raise ValueError('observed dates must exactly match the supplied full-year trading calendar')
        coverage = 'exact match to supplied full-year calendar'
    else:
        # Month endpoints cannot establish absence of missing sessions. The
        # fallback requires an explicit caller assertion, recorded in the model.
        if confirm_complete is not True or dates[0].month != 1 or dates[-1].month != 12:
            raise ValueError('provide full-year calendar or confirm_complete=True with Jan..Dec coverage')
        coverage = 'caller asserted complete year; session completeness unverified'
    if dates[0].month != 1 or dates[-1].month != 12:
        raise ValueError('calendar must span January through December')
    model = fit_annual_values([value for _,value in rows], year, **parameters)
    model.update(start_date=dates[0].isoformat(), end_date=dates[-1].isoformat(),
                 dates=[day.isoformat() for day in dates], coverage=coverage,
                 fitted_as_of=as_of.isoformat())
    return model


def validate_annual_model(model):
    """Reject incompatible/NaN JSON models before any forecast computation."""
    if not isinstance(model, dict):
        raise ValueError('annual model must be a JSON object')
    if model.get('schema') != 'lvt-annual-cycle-model' or model.get('version') != 1:
        raise ValueError('unsupported annual model schema/version')
    _integer(model.get('year'), 'year')
    _integer(model.get('sample_count'), 'sample_count', 6)
    components = model.get('components')
    if not isinstance(components, list) or not 1 <= len(components) <= 7:
        raise ValueError('annual model requires 1..7 components')
    periods = []
    for component in components:
        if not isinstance(component, dict) or any(
                type(component.get(name)) not in (int, float)
                for name in ('period','amplitude','phase')):
            raise ValueError('model components require numeric period/amplitude/phase')
        period = _real(component.get('period'), 'period', 2.0000000000000004)
        _real(component.get('amplitude'), 'amplitude')
        phase = _sample(component.get('phase'))
        if not math.isfinite(phase):
            raise ValueError('model phase must be finite')
        periods.append(period)
    if len(set(periods)) != len(periods):
        raise ValueError('model contains duplicate wavelengths')
    if model.get('phase_convention') != 'sine radians at ordinal zero':
        raise ValueError('unsupported phase convention')
    if 'dates' in model:
        dates = [date.fromisoformat(day) for day in model['dates']]
        validate_dates(dates, model['year'])
        if len(dates) != model['sample_count']:
            raise ValueError('model dates must match sample_count')
    if 'fitted_as_of' in model and date.fromisoformat(model['fitted_as_of']) < date(model['year']+1,1,1):
        raise ValueError('saved annual fit predates completion of its source year')


METONIC_LAGS = (8, 11, 19, 27, 30, 38)


def superposition_values(models, target_year, count, normalization='rms',
                         calendar_policy='extend', invert=False):
    """Align historical frozen waves at ordinal zero, then average six.

    RMS scaling uses each SOURCE year's full wave only. Extending to a longer
    target calendar evaluates the stored sinusoids; no time stretching occurs.
    """
    _integer(target_year, 'target_year', 39)
    _integer(count, 'count')
    if normalization not in ('none','rms') or calendar_policy not in ('strict','extend'):
        raise ValueError('normalization=none/rms; calendar_policy=strict/extend')
    if type(invert) is not bool:
        raise ValueError('invert must be a boolean')
    by_year = {}
    for model in models:
        validate_annual_model(model)
        if model['year'] in by_year:
            raise ValueError('duplicate source model year')
        by_year[model['year']] = model
    years = [target_year-lag for lag in METONIC_LAGS]
    if set(by_year) != set(years):
        raise ValueError('require exactly target years minus 8,11,19,27,30,38')
    source_waves, scales = [], []
    for year in years:
        model = by_year[year]
        n = model['sample_count']
        if calendar_policy == 'strict' and count != n:
            raise ValueError('strict ordinal alignment requires equal annual sample counts')
        base = [annual_wave(model,i) for i in range(n)]
        mean = math.fsum(base)/n if normalization == 'rms' else 0.0
        scale = math.sqrt(math.fsum((value-mean)**2 for value in base)/n) if normalization == 'rms' else 1.0
        if scale == 0:
            raise ValueError('zero-energy annual wave cannot be RMS normalized')
        source_waves.append([(annual_wave(model,i)-mean)/scale for i in range(count)])
        scales.append(dict(year=year, mean=mean, scale=scale, sample_count=n))
    sign = -1.0 if invert else 1.0
    values = [sign*math.fsum(wave[i] for wave in source_waves)/6.0 for i in range(count)]
    return values, dict(schema='lvt-superposition-model', version=1,
                        research_reconstruction=True, target_year=target_year,
                        source_years=years, lags=list(METONIC_LAGS), normalization=normalization,
                        calendar_policy=calendar_policy, invert=invert,
                        sample_count=count, scales=scales, annual_models=[by_year[year] for year in years])


class SuperpositionWaveReader:
    def __init__(self, models, target_year, count, normalization='rms', calendar_policy='extend', invert=False):
        self.values, self.model = superposition_values(models, target_year, count,
                                                       normalization, calendar_policy, invert)
        self.reset()

    def reset(self):
        self.index = 0

    def update(self):
        if self.index >= len(self.values):
            raise StopIteration('end of declared target calendar')
        value = self.values[self.index]
        self.index += 1
        return value


def json_clean(value):
    # JSON has no standard NaN. Unavailable report fields are null, whereas
    # numerical reference fixtures retain each language's NaN literal.
    if isinstance(value,float) and not math.isfinite(value):
        return None
    if isinstance(value,dict):
        return {key:json_clean(item) for key,item in value.items()}
    if isinstance(value,(tuple,list)):
        return [json_clean(item) for item in value]
    return value


def save_json(path, value):
    Path(path).write_text(json.dumps(json_clean(value), indent=2, allow_nan=False)+'\n', encoding='utf-8')


def load_annual(path):
    model = json.loads(Path(path).read_text(encoding='utf-8'))
    validate_annual_model(model)
    return model


def save_wave_csv(path, dates, values):
    if len(dates) != len(values):
        raise ValueError('wave and calendar lengths differ')
    with Path(path).open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['date','value'])
        writer.writerows((day.isoformat(), format(value,'.15g')) for day,value in zip(dates,values))


def synthetic_dates(year, count=252):
    """Artificial evenly selected weekdays, ONLY for deterministic port fixtures.

    This is not an exchange holiday calendar, nor real dates for INPUT_CLOSE.
    It covers January through December and retains exactly count observations.
    """
    days, day = [], date(year,1,1)
    while day.year == year:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    if not 2 <= count <= len(days):
        raise ValueError('synthetic calendar count out of range')
    return [days[i*(len(days)-1)//(count-1)] for i in range(count)]


def fixture_annual(input_close, **parameters):
    # The undated closes are assigned an explicitly SYNTHETIC 2020 calendar.
    # A production annual fit must receive actual complete trading-year dates.
    dates = synthetic_dates(2020, len(input_close))
    model = decode_annual(list(zip(dates,input_close)), 2020, date(2021,1,1),
                          expected_dates=dates, **parameters)
    model['fixture_note'] = 'INPUT_CLOSE on synthetic dates; not a historical annual market model'
    return model


def fixture_historical_models(input_close):
    """Six deliberately different synthetic histories derived from INPUT_CLOSE.

    Fixed circular rotations/scales exercise phase alignment and normalization.
    These transformed series are test data, never claimed as historical prices.
    """
    result = []
    for j, lag in enumerate(METONIC_LAGS):
        shift = 7*j
        values = [(1.0+0.1*j)*input_close[(i+shift) % len(input_close)]
                  for i in range(len(input_close))]
        year = 2021-lag
        dates = synthetic_dates(year, len(values))
        model = decode_annual(list(zip(dates,values)), year, date(2021,1,1),
                              expected_dates=dates, min_period=5, max_period=80,
                              smoothing=1600.0, genuine_threshold=49.0,
                              candidate_pool=10, max_components=7)
        model['fixture_note'] = f'SYNTHETIC: INPUT_CLOSE rotation={shift}, scale={1.0+0.1*j}'
        result.append(model)
    return result


def make_cli_parser(slug):
    import argparse
    parser = argparse.ArgumentParser(description=slug + ': documented research reconstruction')
    parser.add_argument('--generate-reference-data', action='store_true')
    commands = parser.add_subparsers(dest='command')
    if slug == 'annual-cycle-pattern-decoder':
        fit = commands.add_parser('fit', help='decode a complete past year, save frozen model')
        fit.add_argument('--input', required=True)
        fit.add_argument('--year', type=int, required=True)
        fit.add_argument('--as-of', type=date.fromisoformat, default=date.today())
        fit.add_argument('--calendar', help='full-year date-column CSV for exact completeness check')
        fit.add_argument('--confirm-complete-year', action='store_true',
                         help='assert full coverage when no calendar is supplied; assertion recorded')
        fit.add_argument('--min-period', type=int, default=5)
        fit.add_argument('--max-period', type=int, default=125)
        fit.add_argument('--smoothing', type=float, default=1600.0)
        fit.add_argument('--genuine-threshold', type=float, default=49.0)
        fit.add_argument('--candidate-pool', type=int, default=10)
        fit.add_argument('--max-components', type=int, default=7)
        fit.add_argument('--peak-distance', type=int, default=2)
        fit.add_argument('--model-out', required=True)
        fit.add_argument('--wave-out', required=True)
        replay = commands.add_parser('replay', help='evaluate a frozen model on its stored dates')
        replay.add_argument('--model', required=True)
        replay.add_argument('--wave-out', required=True)
    elif slug == 'harmonic-energy-superposition-wave':
        build = commands.add_parser('build', help='average six historical annual models on target calendar')
        source = build.add_mutually_exclusive_group(required=True)
        source.add_argument('--models', nargs=6, help='six annual JSON models')
        source.add_argument('--history', help='dated price CSV; decode each required completed historical year')
        build.add_argument('--target-year', type=int, required=True)
        build.add_argument('--calendar', required=True, help='target-year session dates, no target prices')
        build.add_argument('--confirm-complete-years', action='store_true',
                           help='history mode: explicitly assert each source year has complete sessions')
        build.add_argument('--as-of', type=date.fromisoformat, default=date.today())
        build.add_argument('--normalization', choices=('rms','none'), default='rms')
        build.add_argument('--calendar-policy', choices=('extend','strict'), default='extend')
        build.add_argument('--invert', action='store_true')
        build.add_argument('--model-out', required=True)
        build.add_argument('--wave-out', required=True)
        replay = commands.add_parser('replay')
        replay.add_argument('--model', required=True)
        replay.add_argument('--wave-out', required=True)
    else:
        analyze = commands.add_parser('analyze', help='report a chosen dated range; optionally stream all rows')
        analyze.add_argument('--input', required=True)
        analyze.add_argument('--start', type=date.fromisoformat)
        analyze.add_argument('--end', type=date.fromisoformat)
        analyze.add_argument('--window', type=int, default=200, help='rolling buffer only; batch uses entire range')
        analyze.add_argument('--min-period', type=int, default=5)
        analyze.add_argument('--max-period', type=int, default=80)
        analyze.add_argument('--smoothing', type=float, default=1600.0)
        analyze.add_argument('--genuine-threshold', type=float, default=49.0)
        analyze.add_argument('--phase-cycles', type=float, default=2.0)
        analyze.add_argument('--top-k', type=int, default=3)
        analyze.add_argument('--peak-distance', type=int, default=2)
        analyze.add_argument('--max-segments', type=int, default=5)
        analyze.add_argument('--rolling', action='store_true')
        analyze.add_argument('--json-out')
        analyze.add_argument('--series-out', help='retrospective CSV: rolling fields or final-model/highlighter overlay')
        analyze.add_argument('--horizon', type=int, default=0, help='static last-model projection in bars')
        if slug == 'phasing-oscillator':
            analyze.add_argument('--short-min', type=int, default=5)
            analyze.add_argument('--short-max', type=int, default=30)
            analyze.add_argument('--long-min', type=int, default=31)
            analyze.add_argument('--long-max', type=int, default=80)
        if slug == 'cycle-phase-score':
            evaluate = commands.add_parser('phase', help='score a directly supplied sine phase')
            evaluate.add_argument('--radians', type=float, required=True)
    return parser


def scanner_report(scan, config, dates):
    return dict(schema='lvt-cycle-scan', version=1, research_reconstruction=True,
                start_date=dates[0].isoformat(), end_date=dates[-1].isoformat(),
                sample_count=len(dates), config=asdict(config),
                phase_convention='sine radians at analysis endpoint',
                validation_input='raw prices, most recent complete segments',
                accepted_count=scan.accepted_count,
                cycles=[cycle._asdict() for cycle in scan.cycles],
                spectrum=dict(periods=list(range(config.min_period,config.max_period+1)),
                              amplitude=scan.spectrum.values, genuine_percent=scan.genuine_percent))


def run_cli(slug, args, master_class, flatten):
    """Local CSV/JSON workflows; no WTT API calls or network dependencies."""
    if args.command == 'phase':
        if not math.isfinite(args.radians):
            raise ValueError('phase must be finite')
        print(json.dumps(dict(value=phase_state(args.radians), status=phase_status(args.radians))))
        return
    if slug == 'annual-cycle-pattern-decoder':
        if args.command == 'fit':
            rows = read_prices(args.input)
            calendar = read_calendar(args.calendar) if args.calendar else None
            model = decode_annual(rows, args.year, args.as_of, calendar, args.confirm_complete_year,
                                  min_period=args.min_period, max_period=args.max_period,
                                  smoothing=args.smoothing, genuine_threshold=args.genuine_threshold,
                                  candidate_pool=args.candidate_pool, max_components=args.max_components,
                                  peak_distance=args.peak_distance)
            save_json(args.model_out, model)
        else:
            model = load_annual(args.model)
        dates = [date.fromisoformat(day) for day in model['dates']]
        save_wave_csv(args.wave_out, dates, [annual_wave(model,i) for i in range(len(dates))])
        print(json.dumps(dict(year=model['year'], correlation=model['correlation'],
                              components=len(model['components']), sample_count=len(dates))))
        return
    if slug == 'harmonic-energy-superposition-wave':
        if args.command == 'build':
            dates = read_calendar(args.calendar)
            validate_dates(dates, args.target_year)
            if args.models:
                models = [load_annual(path) for path in args.models]
            else:
                rows = read_prices(args.history)
                models = [decode_annual(rows, args.target_year-lag, args.as_of,
                                       confirm_complete=args.confirm_complete_years)
                          for lag in METONIC_LAGS]
            # No target price is ever read. Source years alone supply fitting
            # and source-wave normalization, preventing target-year lookahead.
            values, model = superposition_values(models, args.target_year, len(dates),
                                                 args.normalization, args.calendar_policy, args.invert)
            model['dates'] = [day.isoformat() for day in dates]
            save_json(args.model_out, model)
        else:
            model = json.loads(Path(args.model).read_text(encoding='utf-8'))
            if model.get('schema') != 'lvt-superposition-model' or model.get('version') != 1:
                raise ValueError('unsupported superposition model')
            dates = [date.fromisoformat(day) for day in model['dates']]
            validate_dates(dates, model['target_year'])
            values, _ = superposition_values(model['annual_models'], model['target_year'], len(dates),
                                              model['normalization'], model['calendar_policy'], model['invert'])
        save_wave_csv(args.wave_out, dates, values)
        print(json.dumps(dict(target_year=model['target_year'], source_years=model['source_years'],
                              sample_count=len(values))))
        return
    rows = read_prices(args.input)
    if args.start and args.end and args.start > args.end:
        raise ValueError('start must not exceed end')
    rows = [(day,value) for day,value in rows
            if (args.start is None or day >= args.start) and (args.end is None or day <= args.end)]
    if len(rows) < 6:
        raise ValueError('selected range needs >= 6 prices')
    _integer(args.horizon, 'horizon', 0)
    dates, prices = [day for day,_ in rows], [value for _,value in rows]
    common = dict(window=args.window if args.rolling else len(prices),
                  min_period=args.min_period, max_period=args.max_period,
                  smoothing=args.smoothing, genuine_threshold=args.genuine_threshold,
                  phase_cycles=args.phase_cycles, top_k=args.top_k,
                  peak_distance=args.peak_distance, max_segments=args.max_segments)
    config = ScanConfig(**common)
    scan = (empty_scan(config) if args.rolling and len(prices) < config.window else
            scan_cycles(prices[-config.window:] if args.rolling else prices, config))
    report = scanner_report(scan, config, dates[-config.window:] if args.rolling else dates)
    series = []
    if slug == 'phasing-oscillator':
        indicator = master_class(window=common['window'], short_min=args.short_min,
                                 short_max=args.short_max, long_min=args.long_min, long_max=args.long_max,
                                 smoothing=args.smoothing, genuine_threshold=args.genuine_threshold,
                                 phase_cycles=args.phase_cycles)
    else:
        indicator = master_class(**common)
    if args.rolling or slug == 'phasing-oscillator':
        for day,price in rows:
            output = indicator.update(price)
            series.append(dict(date=day.isoformat(), **flatten(indicator,output)))
        report['output'] = series[-1]
        if slug == 'phasing-oscillator':
            report['phasing_config'] = dict(short=asdict(indicator.short.config), long=asdict(indicator.long.config))
    else:
        cycle = scan.cycles[0]
        if slug == 'complete-cycle-scanner':
            report['output'] = flatten(indicator,scan)
        elif slug == 'dominant-market-vibration':
            report['output'] = cycle._asdict()
        elif slug == 'cycle-phase-score':
            report['output'] = dict(value=phase_state(cycle.phase), period=cycle.period,
                                    phase=cycle.phase, status=phase_status(cycle.phase))
        else:
            report['output'] = dict(value=cycle.value, period=cycle.period,
                                    eta_top=cycle.eta_top, eta_bottom=cycle.eta_bottom)
        # Batch historical overlay uses the final selected period/model. This is
        # retrospective, and expressly distinct from the causal --rolling CSV.
        for i,day in enumerate(dates):
            row = dict(date=day.isoformat(), fitted=modeled_value(cycle,i-(len(prices)-1)))
            if slug == 'dynamic-cycle-explorer':
                if math.isfinite(cycle.period):
                    long_length = int(cycle.period)
                    row['highlighter'] = centered_mean(prices,i,max(2,math.floor(long_length/2+0.5))) - centered_mean(prices,i,long_length)
                else:
                    row['highlighter'] = math.nan
            series.append(row)
    if slug == 'phasing-oscillator':
        # Project the two selected phase STATES, not an unrelated global
        # scanner wave. Re-analyze frozen buffers without advancing a sample.
        side_cycles = []
        for name, side in (('short',indicator.short),('long',indicator.long)):
            side_scan = scan_cycles(list(side.prices),side.config) if side.is_primed else empty_scan(side.config)
            report[name+'_scan'] = scanner_report(side_scan,side.config,dates[-side.config.window:])
            side_cycles.append(side_scan.cycles[0])
        report['projection'] = []
        for h in range(1,args.horizon+1):
            scores = [phase_state(cycle.phase+2.0*math.pi*h/cycle.period) for cycle in side_cycles]
            report['projection'].append(dict(bars_ahead=h,value=sum(scores),
                                              short_score=scores[0],long_score=scores[1]))
    elif slug == 'cycle-phase-score':
        cycle = scan.cycles[0]
        report['projection'] = [dict(bars_ahead=h,value=phase_state(cycle.phase+2.0*math.pi*h/cycle.period))
                                for h in range(1,args.horizon+1)]
    else:
        report['projection'] = [dict(bars_ahead=h,value=modeled_value(scan.cycles[0],h))
                                for h in range(1,args.horizon+1)]
    if args.series_out:
        with Path(args.series_out).open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(series[0]))
            writer.writeheader()
            for row in series:
                writer.writerow({key:('' if isinstance(value,float) and math.isnan(value)
                                      else format(value,'.15g') if isinstance(value,float) else value)
                                 for key,value in row.items()})
    if args.json_out:
        save_json(args.json_out, report)
    print(json.dumps(json_clean(report), allow_nan=False))
