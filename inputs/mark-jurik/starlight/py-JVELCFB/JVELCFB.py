"""JVELCFB — VEL with CFB-Driven Depth.

Uses CFB output as a stochastic oscillator to modulate VEL's depth bar-by-bar.
Short cycles → shallow depth (fast response), long cycles → deep depth (more smoothing).
"""

import numpy as np
import sys
from pathlib import Path

# Allow imports from sibling packages
_parent = str(Path(__file__).resolve().parent.parent)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from py_JCFB.JCFB import jcfb  # noqa: E402
from py_JVEL.JVEL import jxvel_aux1, jxvel_aux3  # noqa: E402


def jvelcfb(
    prices: np.ndarray,
    lo_depth: int = 5,
    hi_depth: int = 30,
    fractal_type: int = 1,
    smooth: int = 10,
) -> np.ndarray:
    """Compute VEL with CFB-driven adaptive depth.

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    lo_depth : int
        Minimum VEL depth (used when CFB is at its running minimum).
    hi_depth : int
        Maximum VEL depth (used when CFB is at its running maximum).
    fractal_type : int
        CFB fractal type (1-4).
    smooth : int
        CFB smoothing parameter.

    Returns
    -------
    np.ndarray
        Adaptively-smoothed VEL output.
    """
    n = len(prices)
    cfb = jcfb(prices, fractal_type=fractal_type, smooth=smooth)

    # Build adaptive depth series via stochastic normalization of CFB
    depth_series = np.empty(n, dtype=int)
    cfbmin = cfb[0]
    cfbmax = cfb[0]

    for i in range(n):
        cfbmin = min(cfbmin, cfb[i])
        cfbmax = max(cfbmax, cfb[i])
        if cfbmax == cfbmin:
            sr = 0.5
        else:
            sr = (cfb[i] - cfbmin) / (cfbmax - cfbmin)
        depth_series[i] = int(lo_depth + sr * (hi_depth - lo_depth))

    # Two-stage VEL: variable-depth aux1, then fixed-period aux3
    vel_stage1 = jxvel_aux1(prices, depth_series)
    vel_out = jxvel_aux3(vel_stage1, period=3)
    return vel_out
