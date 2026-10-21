"""Shared, standard-library Corona research engine and conversion primitives.

Source: Ehlers' November 2008 Corona Charts, corroborated by the readable
April 2012 Corona Swing listing. See description.md for the source audit and
explicit standalone initialization/degenerate-data decisions. This is not the
2013 book's comb filter. All trig functions use radians and full precision pi.

The engine advances once per accepted price. Four wrappers may consume the
same immutable snapshot without advancing the engine four times. No external
framework, numerical package, charting library, or clock is needed.
"""
from __future__ import annotations

import datetime
import importlib.util
import math
from pathlib import Path
import sys
from typing import NamedTuple

TWO_PI = 2.0 * math.pi
SQRT_THREE_OVER_TWO = math.sqrt(3.0) / 2.0
FIRST_BANK_SAMPLE = 13  # Literal CurrentBar > 12, one-based accepted samples.
FIR_WEIGHTS = (1.0, 2.0, 3.0, 3.0, 2.0, 1.0)


class Heatmap(NamedTuple):
    """An owned column, retaining all seven zpano Heatmap fields.

    values[i] belongs to parameter_first + i * parameter_resolution; resolution
    means units per bin. value_min/max are actual column extrema, not axis
    bounds. Lower intensity means hotter. Callers may mutate the returned list
    without changing recursive indicator state or another output column.
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
    def empty(time, first, last, step):
        return Heatmap(time, first, last, step, math.nan, math.nan, [])


class CoronaParameters(NamedTuple):
    high_pass_cutoff: int = 30
    min_period: int = 6
    max_period: int = 30
    decibels_threshold: float = 6.0
    max_raster_value: float = 20.0


class CoronaSnapshot(NamedTuple):
    """All arrays are immutable and ordered by increasing half-bar period.

    accepted=False marks a skipped NaN input, with no accepted-bar advance.
    internal DC values stay finite during warm-up so adaptive filters never
    see infinity sentinels. Wrappers mask their public values until primed.
    has_cycle_estimate requires nonzero power and currently selected channels;
    a held centroid can remain finite even when this flag is false.
    """
    parameters: CoronaParameters
    sample_count: int
    accepted: bool
    primed: bool
    price: float
    time: datetime.datetime | None
    high_pass: float
    filtered: float
    bandwidth: float
    dominant_cycle: float
    dominant_cycle_median: float
    maximum_power: float
    normalization_power: float
    selected_bins: int
    has_cycle_estimate: bool
    power: tuple[float, ...]
    relative_power: tuple[float, ...]
    decibels: tuple[float, ...]


class _Channel(NamedTuple):
    # The first two fields are t-1 and t-2 at evaluation time. Distinguish them
    # explicitly; arrays in EasyLanguage do not gain bar history automatically.
    in_phase_1: float = 0.0
    in_phase_2: float = 0.0
    quadrature_1: float = 0.0
    quadrature_2: float = 0.0
    real_1: float = 0.0
    real_2: float = 0.0
    imaginary_1: float = 0.0
    imaginary_2: float = 0.0
    power: float = 0.0
    decibels: float = 0.0


def integer_parameter(name, value, minimum):
    # bool is a subclass of int in Python, but is not a period or raster size.
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')


def finite_parameter(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name} must be finite')
    return float(value)


def valid_price(price):
    """NaN skips a bar; other nonfinite values are rejected before mutation."""
    if math.isnan(price):
        return False
    if not math.isfinite(price):
        raise ValueError('price must be finite or NaN')
    return True


def checked(value):
    """Catch overflow rather than allow hidden NaNs to poison recursive state."""
    if not math.isfinite(value):
        raise ValueError('calculation overflow; use finite, reasonably scaled prices')
    return value


def clip(value, lower, upper):
    return max(lower, min(upper, value))


class Corona:
    """Streaming channelized receiver; update(price, time=None) -> snapshot.

    Defaults cover periods 6..30 at fixed half-bar spacing, HP30, selection6,
    intensity20. min_period>=6 preserves the source's aliasing guard and avoids
    unstable broad-startup short-period channels. HP>=5 avoids its removable
    0/0 at cutoff4 and the Nyquist pole at2. No zero-means-default convention.
    Complexity: O(max_period-min_period) work/history per accepted sample.
    """
    def __init__(self, high_pass_cutoff=30, min_period=6, max_period=30,
                 decibels_threshold=6.0, max_raster_value=20.0):
        integer_parameter('high_pass_cutoff', high_pass_cutoff, 5)
        integer_parameter('min_period', min_period, 6)
        integer_parameter('max_period', max_period, min_period + 1)
        threshold = finite_parameter('decibels_threshold', decibels_threshold)
        ceiling = finite_parameter('max_raster_value', max_raster_value)
        if not 0.0 <= threshold < ceiling or ceiling <= 0.0:
            raise ValueError('require 0 <= decibels_threshold < max_raster_value')
        self.parameters = CoronaParameters(high_pass_cutoff, min_period, max_period,
                                           threshold, ceiling)
        self.periods = tuple(n / 2.0 for n in range(2 * min_period, 2 * max_period + 1))
        self._betas = tuple(math.cos(TWO_PI / p) for p in self.periods)
        angle = TWO_PI / high_pass_cutoff
        self._pole = (1.0 - math.sin(angle)) / math.cos(angle)
        if not 0.0 < self._pole < 1.0:
            raise ValueError('highpass coefficient must have a stable positive pole')
        self.reset()

    def reset(self):
        """Discard history but retain the validated configuration."""
        self.sample_count = 0
        self._price_previous = 0.0
        self._hp_history = [0.0] * 6  # Oldest first, newest last.
        self._filtered_previous = 0.0
        self._bank = [_Channel() for _ in self.periods]
        self._dc = 0.0  # Persistent source centroid; do not reset each bar.
        self._dc_history = [0.0] * 5  # Source Median(DC,5), zero initialized.
        self.last_snapshot = None

    def is_primed(self):
        return self.sample_count >= FIRST_BANK_SAMPLE

    def update(self, price, time=None):
        if not valid_price(price):
            # Do not count missing samples. Returning a distinct snapshot
            # prevents a skipped bar from looking like a new accepted bar.
            if self.last_snapshot is not None:
                return self.last_snapshot._replace(accepted=False, price=price, time=time)
            zeros = (0.0,) * len(self.periods)
            return CoronaSnapshot(self.parameters, 0, False, False, price, time,
                                  0.0, 0.0, 0.5, 0.0, float(self.parameters.min_period),
                                  0.0, 0.01, 0, False, zeros, zeros, zeros)

        count = self.sample_count + 1
        # Standalone input has no Price[1] before the first sample. Seed the
        # first historical price with price itself, suppressing a fictitious gap.
        previous = price if count == 1 else self._price_previous
        hp = checked(0.5 * (1.0 + self._pole) * (price - previous)
                     + self._pole * self._hp_history[-1])
        hp_history = self._hp_history[1:] + [hp]
        filtered = checked(sum(v * w for v, w in zip(hp_history, FIR_WEIGHTS)) / 12.0)
        if count < 7:
            filtered = checked(price - previous)
        if count == 1:
            filtered = 0.0
        bandwidth = max(0.1, 0.5 - 0.015 * count)

        # Compute into a fresh bank. A bad finite input causing overflow cannot
        # partially commit the highpass or any channel history.
        bank = []
        for period, beta, old in zip(self.periods, self._betas, self._bank):
            if count < FIRST_BANK_SAMPLE:
                bank.append(old)
                continue
            gamma = 1.0 / math.cos(2.0 * TWO_PI * bandwidth / period)
            alpha = gamma - math.sqrt(gamma * gamma - 1.0)
            in_phase = filtered
            quadrature = checked((period / TWO_PI) * (filtered - self._filtered_previous))
            real = checked(0.5 * (1.0 - alpha) * (in_phase - old.in_phase_2)
                           + beta * (1.0 + alpha) * old.real_1 - alpha * old.real_2)
            imaginary = checked(0.5 * (1.0 - alpha) * (quadrature - old.quadrature_2)
                                + beta * (1.0 + alpha) * old.imaginary_1 - alpha * old.imaginary_2)
            power = checked(real * real + imaginary * imaginary)
            bank.append(_Channel(in_phase, old.in_phase_1, quadrature, old.quadrature_1,
                                 real, old.real_1, imaginary, old.imaginary_1, power, old.decibels))

        maximum = max(channel.power for channel in bank)
        # The later listing first reads Ampl[12], substitutes .01 if it is
        # zero, then scans the bank. This differs from a permanent .01 floor.
        normalizer = max(bank[0].power or 0.01, maximum)
        numerator = denominator = 0.0
        selected = 0
        for i, (period, channel) in enumerate(zip(self.periods, bank)):
            relative = channel.power / normalizer
            raw = channel.decibels  # Source conditional assignment retains DB.
            if relative > 0.0:
                raw = 10.0 * math.log10((1.0 - 0.99 * relative) / 0.01)
            db = min(self.parameters.max_raster_value,
                     0.33 * raw + 0.67 * channel.decibels)
            bank[i] = channel._replace(decibels=db)
            if db <= self.parameters.decibels_threshold:
                weight = self.parameters.max_raster_value - db
                numerator += period * weight
                denominator += weight
                selected += 1
        dc = numerator / denominator if denominator > 0.0 else self._dc
        dc_history = self._dc_history[1:] + [dc]
        median = max(float(self.parameters.min_period), sorted(dc_history)[2])
        powers = tuple(channel.power for channel in bank)
        snapshot = CoronaSnapshot(
            self.parameters, count, True, count >= FIRST_BANK_SAMPLE, float(price), time,
            hp, filtered, bandwidth, dc, median, maximum, normalizer, selected,
            maximum > 0.0 and selected > 0, powers,
            tuple(power / normalizer for power in powers),
            tuple(channel.decibels for channel in bank))

        # Commit only after every calculation succeeded.
        self.sample_count = count
        self._price_previous = price
        self._hp_history = hp_history
        self._filtered_previous = filtered
        self._bank = bank
        self._dc = dc
        self._dc_history = dc_history
        self.last_snapshot = snapshot
        return snapshot


class AdaptiveCycle(NamedTuple):
    band_pass: float
    quadrature: float
    amplitude: float
    lead60: float


class AdaptiveBandPass:
    """Raw-price two-pole BP, tuned each bar to the finite median period.

    Source gain: gamma=sec(4*pi*.1/period). A backward difference estimates
    quadrature. Leading signal always uses CURRENT BP; shift history last.
    No Price[2] exists for standalone samples1/2, so BP/Q are zero on those
    two samples and both actual prices are retained for sample3.
    """
    def __init__(self):
        self._prices = []
        self._bp1 = self._bp2 = 0.0

    def update(self, price, period):
        if len(self._prices) < 2:
            self._prices.append(price)
            return AdaptiveCycle(0.0, 0.0, 0.0, 0.0)
        omega = TWO_PI / period
        beta = math.cos(omega)
        gamma = 1.0 / math.cos(2.0 * omega * 0.1)
        alpha = gamma - math.sqrt(gamma * gamma - 1.0)
        bp = checked(0.5 * (1.0 - alpha) * (price - self._prices[0])
                     + beta * (1.0 + alpha) * self._bp1 - alpha * self._bp2)
        quadrature = checked((bp - self._bp1) / omega)
        amplitude = checked(math.sqrt(bp * bp + quadrature * quadrature))
        lead = checked(0.5 * bp + SQRT_THREE_OVER_TWO * quadrature)
        self._prices = [self._prices[1], price]
        self._bp2, self._bp1 = self._bp1, bp
        return AdaptiveCycle(bp, quadrature, amplitude, lead)


class Raster:
    """Source logical cells j=1..R stored at Python index j-1.

    Display lower bound is deliberately not sampled: with50 Swing cells,
    coordinates are -4.8,-4.6,...,5.0. This preserves the source distance
    recurrence AND accurately describes it in the Heatmap geometry fields.
    The caller's scalar still uses the complete display bounds -5..5.
    """
    def __init__(self, length, lower, upper, ceiling):
        integer_parameter('raster_length', length, 2)
        self.lower = finite_parameter('display_min', lower)
        self.upper = finite_parameter('display_max', upper)
        self.ceiling = finite_parameter('max_raster_value', ceiling)
        if self.upper <= self.lower or self.ceiling <= 0.0:
            raise ValueError('require display_max > display_min and max_raster_value > 0')
        self.length = length
        self.step = (self.upper - self.lower) / length
        self.first = self.lower + self.step
        self.values = [0.0] * length

    def empty(self, time):
        return Heatmap.empty(time, self.first, self.upper, self.step)

    def column(self, time):
        values = list(self.values)
        return Heatmap(time, self.first, self.upper, self.step, min(values), max(values), values)

    def update(self, position, width, kind, suppress=False):
        """Use half-up rounding explicitly; target-language round() may differ.

        Marker0 is outside the original1..R domain and markerR is inside it.
        Fractional powers use nonnegative distances. Width0 never divides.
        Trend follows readable C# with a .01 guard only at zero width; Swing follows
        the later listing without C#'s extra top-distance cutoff. SNR retains
        that cutoff. Old intensities remain binary64, never RGB-quantized.
        """
        marker = int(math.floor(self.length * position + 0.5))
        exponent, scale, history_scale = {
            'swing': (0.95, 0.5, 0.5),
            'trend': (0.85, 0.8, 0.2),
            'snr': (0.8, 0.5, 1.0),
        }[kind]
        values = []
        for i, old in enumerate(self.values):
            j = i + 1
            if suppress:
                value = self.ceiling
            elif j == marker:
                value = 0.5 * old
            elif width <= 0.0:
                value = self.ceiling
            else:
                distance = abs(self.ceiling * position - self.ceiling * j / self.length) / width
                if kind == 'snr' and j > marker and distance <= 1.0:
                    value = self.ceiling
                else:
                    value = scale * (math.pow(distance, exponent) + history_scale * old)
            values.append(clip(value, 0.0, self.ceiling))
        self.values = values


class CoronaConsumer:
    """Common wrapper protocol: standalone update OR shared snapshot consumption.

    A consumer must see each accepted snapshot exactly once and in order from
    sample1. This catches accidental double advancement, dropped histories,
    and incompatible shared settings before changing its wrapper state.
    """
    def _initialize_consumer(self, high_pass_cutoff, min_period, max_period,
                             decibels_threshold=6.0, max_raster_value=20.0):
        self.corona = Corona(high_pass_cutoff, min_period, max_period,
                             decibels_threshold, max_raster_value)
        self.parameters = self.corona.parameters
        self.sample_count = 0

    def _accept_snapshot(self, snapshot):
        if not isinstance(snapshot, CoronaSnapshot) or snapshot.parameters != self.parameters:
            raise ValueError('snapshot must use this consumer\'s Corona parameters')
        if not snapshot.accepted:
            return False
        if snapshot.sample_count != self.sample_count + 1:
            raise ValueError('consume every accepted snapshot exactly once, in order from sample1')
        self.sample_count = snapshot.sample_count
        return True

    def is_primed(self):
        return self.sample_count >= FIRST_BANK_SAMPLE


def rolling_append(history, value, length):
    """Tiny bounded window, avoiding numpy and language-specific deque APIs."""
    history.append(value)
    if len(history) > length:
        del history[0]
    return min(history), max(history)


def load_module(name, path):
    """Explicit path loader used by examples/generator, not by update math."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def example_main(indicator_class, folder):
    """Each leaf __main__ reads exactly the local252 input prices via the generator.

    Default execution demonstrates streaming. Explicit generation writes and
    verifies all five fixtures for that leaf's confirmed16 parameter cases.
    """
    import argparse
    parser = argparse.ArgumentParser(description=indicator_class.__doc__)
    parser.add_argument('--generate-reference-data', action='store_true')
    options = parser.parse_args()
    generator = load_module('corona_reference_generator', Path(__file__).with_name('generate_reference.py'))
    data = generator.read_inputs(Path(folder) / 'test_testdata.py')
    instance = indicator_class()
    for i, price in enumerate(data['INPUT_CLOSE']):
        if indicator_class.__name__ == 'CoronaSignalToNoiseRatio':
            output = instance.update(price, high=data['INPUT_HIGH'][i], low=data['INPUT_LOW'][i])
        else:
            output = instance.update(price)
    print(f'{indicator_class.__name__}: {len(data["INPUT_CLOSE"])} prices; '
          f'{len(output.heatmap.values)} heatmap cells')
    for name, value in output._asdict().items():
        if name != 'heatmap' and not isinstance(value, (tuple, list)):
            print(f'  {name}={value}')
    if options.generate_reference_data:
        generator.generate_folder(Path(folder), indicator_class)


if __name__ == '__main__':
    # This demonstration shares one spectral update across four independent
    # consumers. Each leaf also runs on its own from its own working directory.
    prepared = Path(__file__).resolve().parent.parent
    # Load this file under the wrappers' canonical module name; otherwise
    # __main__ would define a different NamedTuple type for snapshots.
    core = load_module('corona_reference_core', Path(__file__))
    classes = []
    for folder, class_name in (
        ('corona-spectrum', 'CoronaSpectrum'), ('corona-swing-position', 'CoronaSwingPosition'),
        ('corona-trend-vigor', 'CoronaTrendVigor'), ('corona-signal-to-noise-ratio', 'CoronaSignalToNoiseRatio')):
        module = load_module(folder.replace('-', '_') + '_example', prepared / folder / (folder + '.py'))
        classes.append(getattr(module, class_name))
    generator = load_module('corona_reference_generator', Path(__file__).with_name('generate_reference.py'))
    data = generator.read_inputs(prepared / 'test_testdata.py')
    engine = core.Corona()
    consumers = [cls() for cls in classes]
    for i, price in enumerate(data['INPUT_CLOSE']):
        snapshot = engine.update(price)
        for consumer in consumers:
            if consumer.__class__.__name__ == 'CoronaSignalToNoiseRatio':
                result = consumer.update_from_snapshot(snapshot, high=data['INPUT_HIGH'][i], low=data['INPUT_LOW'][i])
            else:
                result = consumer.update_from_snapshot(snapshot)
    print(f'Shared engine processed {engine.sample_count} bars for {len(consumers)} indicators.')
