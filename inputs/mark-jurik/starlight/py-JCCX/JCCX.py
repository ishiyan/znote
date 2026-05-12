"""
JCCX — Jurik CCI eXtended
A JMA-smoothed CCI analog using fast JMA(4) and slow JMA(Len).
"""

import numpy as np

# NOTE: Adjust this import path to match your project structure.
from ..py_JJMA.JJMA import jjma


def jccx(prices: np.ndarray, length: int = 20) -> np.ndarray:
    """
    Compute JCCX (Jurik CCI eXtended).

    Parameters
    ----------
    prices : np.ndarray
        Input price series.
    length : int
        Period for the slow JMA (default 20).

    Returns
    -------
    np.ndarray
        JCCX values for each bar.
    """
    fast_jma = jjma(prices, period=4, phase=0)
    slow_jma = jjma(prices, period=length, phase=0)
    diff = fast_jma - slow_jma

    n = len(prices)
    out = np.zeros(n)

    for i in range(n):
        w = min(i + 1, 3 * length)
        mad = np.mean(np.abs(diff[i - w + 1 : i + 1]))
        md = 1.5 * mad
        if md < 0.00001:
            out[i] = 0.0
        else:
            out[i] = diff[i] / md

    return out
