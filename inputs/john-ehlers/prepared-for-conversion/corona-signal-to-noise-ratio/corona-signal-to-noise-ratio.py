"""Streaming Corona research master. See description.md for source conventions."""
from __future__ import annotations

import math
from typing import NamedTuple

# Hyphenated master folders are documents, not importable package names.
# Load the one shared standard-library module by path and a canonical identity.
# This bootstrap is conversion scaffolding; it is not part of update math.
from pathlib import Path
import importlib.util
import sys

_CORE_PATH = Path(__file__).resolve().parent.parent / "corona" / "corona.py"
if "corona_reference_core" not in sys.modules:
    _spec = importlib.util.spec_from_file_location("corona_reference_core", _CORE_PATH)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
_core = sys.modules["corona_reference_core"]


class SignalToNoiseOutput(NamedTuple):
    heatmap: _core.Heatmap
    signal_to_noise_ratio: float
    physical_decibels: float
    calibrated_decibels: float
    normalized_position: float
    signal: float
    noise: float
    median_bar_range: float
    width: float
    dominant_cycle: float
    dominant_cycle_median: float
    has_cycle_estimate: float
    ratio_is_finite: float


def _range_input(high, low, bar_range):
    """Exactly one source of bar height; validation precedes estimator mutation."""
    if bar_range is not None:
        if high is not None or low is not None:
            raise ValueError('supply bar_range OR both high and low')
        value = float(bar_range)
    else:
        if high is None or low is None:
            raise ValueError('SNR requires both high and low, or an explicit bar_range')
        if math.isnan(high) or math.isnan(low):
            return math.nan
        if not math.isfinite(high) or not math.isfinite(low):
            raise ValueError('high and low must be finite')
        value = high - low
    if math.isnan(value):
        return math.nan
    if not math.isfinite(value) or value < 0.0:
        raise ValueError('bar_range must be finite and nonnegative; require high >= low')
    return value


class CoronaSignalToNoiseRatio(_core.CoronaConsumer):
    """Cycle SNR with physical dB, mapped1..11 scalar, and Corona heatmap.

    update(price, *, high=..., low=...) OR update(price, bar_range=...).
    Signal recurrence preserves source .2*amplitude+.9*old (DC gain2).
    Noise uses median5 bar height then .1/.9 smoothing, after accepted bar5.
    Physical zero/positive ratio=-inf; positive/zero=+inf; zero/zero=NaN.
    Display clips physical+3.5 to0..10 then adds1, so it always lies1..11.
    Missing price/range skips the complete standalone bar before mutation.
    """
    def __init__(self, high_pass_cutoff=30, min_period=6, max_period=30,
                 raster_length=50, display_min=1.0, display_max=11.0,
                 max_raster_value=20.0):
        self._raster = _core.Raster(raster_length, display_min, display_max, max_raster_value)
        self._initialize_consumer(high_pass_cutoff, min_period, max_period,
                                  max_raster_value=max_raster_value)
        self._ranges = [0.0] * 5
        self._average = self._signal = self._noise = 0.0

    def _empty(self, time):
        return SignalToNoiseOutput(self._raster.empty(time), *(math.nan,) * 12)

    def update(self, price, time=None, *, high=None, low=None, bar_range=None):
        if not _core.valid_price(price):
            return self._empty(time)
        value = _range_input(high, low, bar_range)
        if math.isnan(value):
            return self._empty(time)
        return self.update_from_snapshot(self.corona.update(price, time), bar_range=value)

    def update_from_snapshot(self, snapshot, *, high=None, low=None, bar_range=None):
        if not snapshot.accepted:
            return self._empty(snapshot.time)
        value = _range_input(high, low, bar_range)
        if math.isnan(value):
            # A shared engine already accepted this bar. Silently skipping its
            # range would desynchronize the consumer. Composite callers should
            # validate all needed bar data before advancing their shared engine.
            raise ValueError('accepted shared snapshot requires a finite bar range')
        self._accept_snapshot(snapshot)
        self._ranges = self._ranges[1:] + [value]
        median_range = sorted(self._ranges)[2]
        if self.sample_count == 1:
            self._average = snapshot.price
        else:
            self._average = 0.1 * snapshot.price + 0.9 * self._average
            if self._average != 0.0 or snapshot.maximum_power > 0.0:
                self._signal = 0.2 * math.sqrt(snapshot.maximum_power) + 0.9 * self._signal
            if self._average != 0.0 and self.sample_count > 5:
                self._noise = 0.1 * median_range + 0.9 * self._noise

        if self._signal > 0.0 and self._noise > 0.0:
            # Difference of logarithms avoids overflow of signal/noise when
            # both positive amplitudes are representable. It is the same dB
            # equation, with binary64 rounding differences below fixture tol.
            physical = 20.0 * (math.log10(self._signal) - math.log10(self._noise))
        elif self._signal > 0.0:
            physical = math.inf
        elif self._noise > 0.0:
            physical = -math.inf
        else:
            physical = math.nan
        calibrated = physical + 3.5
        position = 0.0 if math.isnan(calibrated) else _core.clip(calibrated, 0.0, 10.0) / 10.0
        width = max(0.0, 0.2 - 0.4 * position)
        self._raster.update(position, width, 'snr', suppress=position > 0.5)
        if not snapshot.primed:
            return self._empty(snapshot.time)
        mapped = self._raster.lower + (self._raster.upper - self._raster.lower) * position
        return SignalToNoiseOutput(self._raster.column(snapshot.time), mapped,
                                   physical, calibrated, position, self._signal, self._noise,
                                   median_range, width, snapshot.dominant_cycle,
                                   snapshot.dominant_cycle_median, float(snapshot.has_cycle_estimate),
                                   float(math.isfinite(physical)))


if __name__ == '__main__':
    _core.example_main(CoronaSignalToNoiseRatio, Path(__file__).resolve().parent)
