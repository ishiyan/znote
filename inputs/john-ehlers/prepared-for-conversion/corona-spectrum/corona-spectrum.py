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


class SpectrumOutput(NamedTuple):
    heatmap: _core.Heatmap
    dominant_cycle: float
    dominant_cycle_median: float
    maximum_power: float
    normalization_power: float
    selected_bins: float
    has_cycle_estimate: float
    power: tuple[float, ...]
    relative_power: tuple[float, ...]


class CoronaSpectrum(_core.CoronaConsumer):
    """49-bin spectral heatmap plus current/median dominant cycle by default.

    Parameters: HP30, periods6..30 (fixed0.5 step), selection threshold6,
    intensity ceiling20. Every constructor parameter is explicit; a zero does
    not silently select a default. Availability begins at accepted sample13.
    Outputs retain a held centroid if channels no longer qualify, while the
    has_cycle_estimate flag reports whether the current spectrum supports it.
    """
    def __init__(self, high_pass_cutoff=30, min_period=6, max_period=30,
                 decibels_threshold=6.0, max_raster_value=20.0):
        self._initialize_consumer(high_pass_cutoff, min_period, max_period,
                                  decibels_threshold, max_raster_value)

    def _empty(self, time):
        p = self.parameters
        cells = (math.nan,) * len(self.corona.periods)
        heatmap = _core.Heatmap.empty(time, float(p.min_period), float(p.max_period), 0.5)
        return SpectrumOutput(heatmap, *(math.nan,) * 6, cells, cells)

    def update(self, price, time=None):
        """Accept one scalar price; time is optional metadata only."""
        return self.update_from_snapshot(self.corona.update(price, time))

    def update_from_snapshot(self, snapshot):
        """Consume a shared engine snapshot, once and in accepted-sample order."""
        if not self._accept_snapshot(snapshot) or not snapshot.primed:
            return self._empty(snapshot.time)
        values = list(snapshot.decibels)
        p = self.parameters
        heatmap = _core.Heatmap(snapshot.time, float(p.min_period), float(p.max_period),
                                0.5, min(values), max(values), values)
        # Diagnostics use floats (0/1 flags, selected count) so the same fixture
        # serializer and NaN warm-up representation work in all five languages.
        return SpectrumOutput(heatmap, snapshot.dominant_cycle,
                              snapshot.dominant_cycle_median, snapshot.maximum_power,
                              snapshot.normalization_power, float(snapshot.selected_bins),
                              float(snapshot.has_cycle_estimate), snapshot.power,
                              snapshot.relative_power)


if __name__ == '__main__':
    _core.example_main(CoronaSpectrum, Path(__file__).resolve().parent)
