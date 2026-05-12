"""
JDMX — Jurik Directional Movement Index

Wilder's DMI/ADX concept using JMA(phase=-100) instead of Wilder's EMA.
Output is signed: positive = bullish, negative = bearish.
"""

import numpy as np

# Assumes JJMA.py is available on the Python path or in a sibling directory.
# Adjust the import below to match your project layout.
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'py-JJMA'))
from JJMA import jjma  # noqa: E402


def jdmx(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    length: int = 14,
) -> np.ndarray:
    """
    Compute the Jurik Directional Movement Index (JDMX).

    Parameters
    ----------
    high : np.ndarray
        Array of high prices.
    low : np.ndarray
        Array of low prices.
    close : np.ndarray
        Array of close prices (used for True Range calculation).
    length : int, optional
        JMA smoothing length (default 14).

    Returns
    -------
    np.ndarray
        Signed DMX values (-100 to +100). First 40 bars are 0.
    """
    n = len(high)
    dm_plus = np.zeros(n)
    dm_minus = np.zeros(n)
    tr = np.zeros(n)

    # Step 1: Compute DM+, DM-, and True Range (scaled ×100)
    for bar in range(1, n):
        up_move = high[bar] - high[bar - 1]
        down_move = low[bar - 1] - low[bar]

        if up_move > down_move and up_move > 0:
            dm_plus[bar] = up_move * 100.0
        else:
            dm_plus[bar] = 0.0

        if down_move > up_move and down_move > 0:
            dm_minus[bar] = down_move * 100.0
        else:
            dm_minus[bar] = 0.0

        tr[bar] = max(
            high[bar] - low[bar],
            abs(high[bar] - close[bar - 1]),
            abs(low[bar] - close[bar - 1]),
        ) * 100.0

    # Step 2: Smooth with JMA(phase=-100)
    numer_plus = jjma(dm_plus, length, phase=-100)
    numer_minus = jjma(dm_minus, length, phase=-100)
    denom = jjma(tr, length, phase=-100)

    # Step 3: Compute DI+, DI-, and signed DMX
    dmx = np.zeros(n)
    for bar in range(40, n):
        if denom[bar] > 0.00001:
            di_plus = 100.0 * numer_plus[bar] / denom[bar]
            di_minus = 100.0 * numer_minus[bar] / denom[bar]
        else:
            di_plus = 0.0
            di_minus = 0.0

        di_sum = di_plus + di_minus
        if di_sum > 0.00001:
            dmx[bar] = 100.0 * (di_plus - di_minus) / di_sum
        else:
            dmx[bar] = 0.0

    return dmx
