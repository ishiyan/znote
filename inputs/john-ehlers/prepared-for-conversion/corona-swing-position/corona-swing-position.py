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


class SwingOutput(NamedTuple):
    heatmap: _core.Heatmap
    swing_position: float
    normalized_position: float
    dominant_cycle: float
    dominant_cycle_median: float
    band_pass: float
    quadrature: float
    cycle_amplitude: float
    lead60: float
    position_span: float
    width: float
    has_cycle_estimate: float


class CoronaSwingPosition(_core.CoronaConsumer):
    """Leading cycle position, scalar -5..5 and source Corona intensity raster.

    Defaults: HP30, periods6..30, raster50, display-5..5, intensity20,
    lead_window51 and position_window21 (inclusive source offsets0..50/0..20).
    Current BP and sqrt(3)/2 form the 60-degree lead. Flat lead range uses a
    neutral position0.5 and a cold raster; it does not assert an imminent turn.
    """
    def __init__(self, high_pass_cutoff=30, min_period=6, max_period=30,
                 raster_length=50, display_min=-5.0, display_max=5.0,
                 max_raster_value=20.0, lead_window=51, position_window=21):
        self._raster = _core.Raster(raster_length, display_min, display_max, max_raster_value)
        _core.integer_parameter('lead_window', lead_window, 2)
        _core.integer_parameter('position_window', position_window, 2)
        self.lead_window, self.position_window = lead_window, position_window
        self._initialize_consumer(high_pass_cutoff, min_period, max_period,
                                  max_raster_value=max_raster_value)
        self._bandpass = _core.AdaptiveBandPass()
        # EasyLanguage histories of Lead60 and Psn begin at zero. Include those
        # historical values during startup to make the chosen convention exact.
        self._leads = [0.0] * lead_window
        self._positions = [0.0] * position_window

    def _empty(self, time):
        return SwingOutput(self._raster.empty(time), *(math.nan,) * 11)

    def update(self, price, time=None):
        return self.update_from_snapshot(self.corona.update(price, time))

    def update_from_snapshot(self, snapshot):
        if not self._accept_snapshot(snapshot):
            return self._empty(snapshot.time)
        cycle = self._bandpass.update(snapshot.price, snapshot.dominant_cycle_median)
        lowest, highest = _core.rolling_append(self._leads, cycle.lead60, self.lead_window)
        flat = highest == lowest
        position = 0.5 if flat else (cycle.lead60 - lowest) / (highest - lowest)
        position = _core.clip(position, 0.0, 1.0)
        low_position, high_position = _core.rolling_append(self._positions, position, self.position_window)
        span = high_position - low_position
        width = 0.01 if span > 0.85 else 0.15 * span
        if width == 0.0:
            width = 0.01  # Later listing's zero-width guard, not a general floor.
        # A broad span indicates healthy movement across the whole cycle:
        # suppress the corona but retain the scalar line separately.
        self._raster.update(position, width, 'swing', suppress=span > 0.8 or flat)
        if not snapshot.primed:
            return self._empty(snapshot.time)
        mapped = self._raster.lower + (self._raster.upper - self._raster.lower) * position
        return SwingOutput(self._raster.column(snapshot.time), mapped, position,
                           snapshot.dominant_cycle, snapshot.dominant_cycle_median,
                           cycle.band_pass, cycle.quadrature, cycle.amplitude, cycle.lead60,
                           span, width, float(snapshot.has_cycle_estimate))


if __name__ == '__main__':
    _core.example_main(CoronaSwingPosition, Path(__file__).resolve().parent)
