"""
Fractal Dispersion
Mnemonic: fdisp

Multi-timeframe fractal dispersion: measures how similar the fractal
dimension is across different timeframes. Uses FGDI computed on multiple
timeframes and outputs the weighted standard deviation around the longest
active timeframe's FDI.

Author: Jean-Philippe Poton (jppoton@yahoo.com), v1.1 April 2010
Reference: https://www.mql5.com/en/code/9604
"""

import sys
import os
import numpy as np
from typing import Optional

import importlib.util

_parent = os.path.join(os.path.dirname(__file__), '..')
_fgdi_path = os.path.join(
    _parent, 'fractal-graph-dimension-indicator',
    'fractal_graph_dimension_indicator.py',
)
_spec = importlib.util.spec_from_file_location(
    'fractal_graph_dimension_indicator', _fgdi_path,
)
_fgdi_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fgdi_mod)
fractal_graph_dimension_indicator = _fgdi_mod.fractal_graph_dimension_indicator

# Standard MT4 timeframes in minutes
TIMEFRAMES = ["5", "15", "30", "60", "240", "1440"]
TIMEFRAME_MINUTES = {
    "5": 5, "15": 15, "30": 30, "60": 60, "240": 240, "1440": 1440,
}
DEFAULT_WEIGHTS = {"5": 1, "15": 1, "30": 1, "60": 1, "240": 0, "1440": 0}


def fractal_dispersion(
    timeframe_prices: dict[str, np.ndarray],
    period: int = 30,
    weights: Optional[dict[str, int]] = None,
) -> np.ndarray:
    """
    Compute multi-timeframe fractal dispersion.

    Measures the weighted standard deviation of FGDI values across timeframes,
    centered on the longest active timeframe's FDI.

    Parameters
    ----------
    timeframe_prices : dict[str, np.ndarray]
        Price arrays keyed by timeframe string (e.g. "5", "15", "30", "60").
        Each array has index 0 = oldest.
    period : int
        Lookback period for FGDI computation (>= 2).
    weights : dict[str, int] or None
        Weights for each timeframe. Keys must match timeframe_prices keys.
        Defaults to {"5": 1, "15": 1, "30": 1, "60": 1, "240": 0, "1440": 0}.

    Returns
    -------
    np.ndarray
        Fractal dispersion values (10 * sigma), indexed on the reference
        timeframe's bar count.
    """
    if period < 2:
        raise ValueError("period must be >= 2")

    if weights is None:
        weights = dict(DEFAULT_WEIGHTS)

    # Filter to active timeframes (weight > 0 and data provided)
    active_tfs = sorted(
        [tf for tf in weights if weights[tf] > 0 and tf in timeframe_prices],
        key=lambda tf: TIMEFRAME_MINUTES[tf],
    )

    total_weight = sum(weights[tf] for tf in active_tfs)
    if total_weight < 2:
        raise ValueError("At least two timeframes must have weight > 0")

    # Reference = longest active timeframe
    ref_tf = active_tfs[-1]
    ref_minutes = TIMEFRAME_MINUTES[ref_tf]
    ref_prices = timeframe_prices[ref_tf]
    n_ref = len(ref_prices)

    # Pre-compute FGDI for all active timeframes
    fgdi_cache: dict[str, np.ndarray] = {}
    for tf in active_tfs:
        result = fractal_graph_dimension_indicator(
            timeframe_prices[tf], period=period
        )
        fgdi_cache[tf] = result.fdi

    # Shorter timeframes (exclude reference)
    shorter_tfs = [tf for tf in active_tfs if tf != ref_tf]

    output = np.full(n_ref, np.nan)

    for pos in range(period, n_ref):
        fdi_ref = fgdi_cache[ref_tf][pos]
        if np.isnan(fdi_ref):
            continue

        dev_sum = 0.0
        valid = True

        for tf in shorter_tfs:
            tf_minutes = TIMEFRAME_MINUTES[tf]
            # Map reference bar index to shorter TF index
            mapped_pos = int(pos * (ref_minutes / tf_minutes))
            tf_fdi_arr = fgdi_cache[tf]

            if mapped_pos >= len(tf_fdi_arr):
                mapped_pos = len(tf_fdi_arr) - 1

            fdi_tf = tf_fdi_arr[mapped_pos]
            if np.isnan(fdi_tf):
                valid = False
                break

            w = weights[tf]
            dev_sum += w * (fdi_tf - fdi_ref) ** 2

        if not valid:
            continue

        # N-1 denominator (sample std dev, matching MQ4)
        sigma = np.sqrt(dev_sum / (total_weight - 1))
        output[pos] = 10.0 * sigma

    return output


if __name__ == "__main__":
    np.random.seed(42)

    # Synthetic multi-timeframe data
    # Simulate 1-hour bars (reference), then derive shorter TF bars
    n_1h = 200
    prices_1h = 1.3000 + np.cumsum(np.random.randn(n_1h) * 0.0005)

    # Simulate shorter TFs by interpolating + noise
    def upsample(prices: np.ndarray, factor: int) -> np.ndarray:
        """Simple linear interpolation to simulate higher-frequency data."""
        x_orig = np.arange(len(prices))
        x_new = np.linspace(0, len(prices) - 1, len(prices) * factor)
        interp = np.interp(x_new, x_orig, prices)
        interp += np.random.randn(len(interp)) * 0.00005
        return interp

    timeframe_prices = {
        "60": prices_1h,
        "30": upsample(prices_1h, 2),
        "15": upsample(prices_1h, 4),
        "5": upsample(prices_1h, 12),
    }

    weights = {"5": 1, "15": 1, "30": 1, "60": 1}

    result = fractal_dispersion(timeframe_prices, period=20, weights=weights)

    print("Fractal Dispersion")
    print("=" * 50)
    print(f"Period: 20, Reference TF: 60min")
    print(f"Active TFs: {list(weights.keys())}")
    print(f"Output length: {len(result)}")
    valid = result[~np.isnan(result)]
    print(f"Valid values: {len(valid)}")
    if len(valid) > 0:
        print(f"  Mean:  {np.mean(valid):.4f}")
        print(f"  Min:   {np.min(valid):.4f}")
        print(f"  Max:   {np.max(valid):.4f}")
    print(f"\nSample values (bars 50-60):")
    for i in range(50, min(60, len(result))):
        val = f"{result[i]:.4f}" if not np.isnan(result[i]) else "NaN"
        print(f"  Bar {i}: dispersion={val}")
