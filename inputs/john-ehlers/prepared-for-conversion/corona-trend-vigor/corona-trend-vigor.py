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


class TrendOutput(NamedTuple):
    heatmap: _core.Heatmap
    trend_vigor: float
    normalized_vigor: float
    dominant_cycle: float
    dominant_cycle_median: float
    band_pass: float
    quadrature: float
    cycle_amplitude: float
    trend_displacement: float
    raw_ratio: float
    lookback: float
    width: float
    has_cycle_estimate: float


class CoronaTrendVigor(_core.CoronaConsumer):
    """Cycle-normalized trend displacement with scalar -10..10 and heatmap.

    The article measures a FULL cycle. Default lag=floor(median cycle), with
    actual buffer index[-1-lag]. Optional lookback_offset=-1 reproduces the
    readable port's floor(D-1) lag while avoiding its absolute-index error.
    This documented interpretation replaces the copied extra buffer offset.
    Public output needs both source startup and enough real lookback history.
    """
    def __init__(self, high_pass_cutoff=30, min_period=6, max_period=30,
                 raster_length=50, display_min=-10.0, display_max=10.0,
                 max_raster_value=20.0, lookback_offset=0):
        self._raster = _core.Raster(raster_length, display_min, display_max, max_raster_value)
        if isinstance(lookback_offset, bool) or not isinstance(lookback_offset, int) or lookback_offset not in (0, -1):
            raise ValueError('lookback_offset must be integer 0 or -1')
        self.lookback_offset = lookback_offset
        self._initialize_consumer(high_pass_cutoff, min_period, max_period,
                                  max_raster_value=max_raster_value)
        self._bandpass = _core.AdaptiveBandPass()
        self._prices = []
        self._ratio = 0.0  # Persistent conditional source update, not per-bar reset.
        self._ready = False

    def is_primed(self):
        return self._ready

    def _empty(self, time):
        return TrendOutput(self._raster.empty(time), *(math.nan,) * 12)

    def update(self, price, time=None):
        return self.update_from_snapshot(self.corona.update(price, time))

    def update_from_snapshot(self, snapshot):
        if not self._accept_snapshot(snapshot):
            return self._empty(snapshot.time)
        cycle = self._bandpass.update(snapshot.price, snapshot.dominant_cycle_median)
        self._prices.append(snapshot.price)
        if len(self._prices) > self.parameters.max_period + 1:
            del self._prices[0]
        lag = max(1, int(math.floor(snapshot.dominant_cycle_median)) + self.lookback_offset)
        has_history = len(self._prices) > lag
        trend = snapshot.price - self._prices[-1 - lag] if has_history else math.nan
        raw_ratio = trend / cycle.amplitude if has_history and cycle.amplitude > 0.0 else math.nan
        # If Trend or Ampl2 is zero the source does not assign Ratio. Retain
        # the prior value explicitly. During insufficient history also hold0.
        if has_history and trend != 0.0 and cycle.amplitude > 0.0:
            self._ratio = _core.clip(_core.checked(0.33 * raw_ratio + 0.67 * self._ratio), -10.0, 10.0)
        vigor = 0.05 * (self._ratio + 10.0)
        # Readable C# has triangular central width, zero at.3/.7. A .01
        # denominator guard prevents those two boundary divisions by zero.
        width = min(vigor - 0.3, 0.7 - vigor) if 0.3 <= vigor <= 0.7 else 0.01
        if width == 0.0:
            width = 0.01
        self._raster.update(vigor, width, 'trend', suppress=vigor < 0.3 or vigor > 0.7)
        self._ready = snapshot.primed and has_history
        if not self._ready:
            return self._empty(snapshot.time)
        mapped = self._raster.lower + (self._raster.upper - self._raster.lower) * vigor
        return TrendOutput(self._raster.column(snapshot.time), mapped, vigor,
                           snapshot.dominant_cycle, snapshot.dominant_cycle_median,
                           cycle.band_pass, cycle.quadrature, cycle.amplitude,
                           trend, raw_ratio, float(lag), width, float(snapshot.has_cycle_estimate))


if __name__ == '__main__':
    _core.example_main(CoronaTrendVigor, Path(__file__).resolve().parent)
