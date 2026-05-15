"""
Hurst Difference
Mnemonic: hurdif

Computes the first difference of the Fractal Dimension Index (FDI) over time.
Positive values indicate rising volatility (potential trade entry); negative
values indicate declining volatility.

Author: Jean-Philippe Poton
Source: https://www.mql5.com/en/code/9676
Blog:   http://fractalfinance.blogspot.com/2010/05/variation-of-hurst-exponent.html
"""

import numpy as np


def _compute_fdi_corrected(
    prices: np.ndarray,
    period: int,
) -> np.ndarray:
    """
    Compute FDI using the corrected FGDI formula: ln(2*(period-1)) denominator.

    Parameters
    ----------
    prices : np.ndarray
        1-D price array. Index 0 = oldest bar.
    period : int
        Lookback period N.

    Returns
    -------
    np.ndarray
        FDI value per bar; first ``period`` values are NaN.
    """
    n = len(prices)
    fdi = np.full(n, np.nan)
    ln2 = np.log(2.0)
    log_2pm1 = np.log(2.0 * (period - 1))
    inv_n_sq = 1.0 / (period * period)

    for pos in range(period, n):
        window = prices[pos - period + 1 : pos + 1]  # period elements
        price_max = np.max(window)
        price_min = np.min(window)
        price_range = price_max - price_min

        if price_range <= 0.0:
            fdi[pos] = 0.0
            continue

        length = 0.0
        prior_diff = (window[0] - price_min) / price_range
        for i in range(1, period):
            diff = (window[i] - price_min) / price_range
            delta = diff - prior_diff
            length += np.sqrt(delta * delta + inv_n_sq)
            prior_diff = diff

        if length > 0.0:
            fdi[pos] = 1.0 + (np.log(length) + ln2) / log_2pm1
        else:
            fdi[pos] = 0.0

    return fdi


def hurst_difference(
    prices: np.ndarray,
    period: int = 30,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute the Hurst Difference (first difference of FDI).

    Parameters
    ----------
    prices : np.ndarray
        1-D array of prices (e.g., close). Index 0 = oldest bar.
    period : int
        Lookback period for FDI computation (>= 2).

    Returns
    -------
    hurst_diff : np.ndarray
        First difference of FDI. Positive = increasing volatility.
        First ``period + 1`` values are NaN.
    fdi : np.ndarray
        Raw FDI values (useful for coloring: RED when < 1.5, BLUE when >= 1.5).
    """
    if period < 2:
        raise ValueError("period must be >= 2")

    n = len(prices)
    fdi = _compute_fdi_corrected(prices, period)

    hurst_diff = np.full(n, np.nan)

    # In MQ4: Hurst_Diff[pos] = fdi[pos+1] - fdi[pos]
    # MQ4 index: higher = further past.  Python index 0 = oldest.
    # Equivalent: hurst_diff[pos] = fdi[pos] - fdi[pos - 1]  (current minus previous)
    for pos in range(period + 1, n):
        if np.isnan(fdi[pos]) or np.isnan(fdi[pos - 1]):
            continue
        hurst_diff[pos] = fdi[pos] - fdi[pos - 1]

    return hurst_diff, fdi


def classify_color(fdi_values: np.ndarray, threshold: float = 1.5) -> np.ndarray:
    """
    Classify bars by color based on FDI threshold.

    Returns
    -------
    np.ndarray of str
        'red' when FDI < threshold (trending), 'blue' otherwise (erratic).
    """
    result = np.full(len(fdi_values), "", dtype=object)
    for i, v in enumerate(fdi_values):
        if np.isnan(v):
            result[i] = "unknown"
        elif v < threshold:
            result[i] = "red"
        else:
            result[i] = "blue"
    return result


if __name__ == "__main__":
    np.random.seed(42)

    # Synthetic data: trending then volatile then trending again
    trend1 = np.cumsum(np.ones(40) * 0.01) + 1.3000
    volatile = 1.3000 + np.cumsum(np.random.randn(40) * 0.005)
    trend2 = volatile[-1] + np.cumsum(np.ones(40) * -0.008)
    prices = np.concatenate([trend1, volatile, trend2])

    hdiff, fdi = hurst_difference(prices, period=20)
    colors = classify_color(fdi)

    print("Hurst Difference Indicator")
    print("=" * 55)
    print(f"Period: 20, Data length: {len(prices)}")
    print()

    print("Trending section (bars 25-34):")
    for i in range(25, 35):
        d = fdi[i]
        hd = hdiff[i]
        c = colors[i]
        print(f"  Bar {i}: FDI={d:.4f}  dFDI={hd:+.4f}  color={c}")

    print()
    print("Volatile section (bars 50-59):")
    for i in range(50, 60):
        d = fdi[i]
        hd = hdiff[i]
        c = colors[i]
        d_str = f"{d:.4f}" if not np.isnan(d) else "   NaN"
        hd_str = f"{hd:+.4f}" if not np.isnan(hd) else "   NaN"
        print(f"  Bar {i}: FDI={d_str}  dFDI={hd_str}  color={c}")

    print()
    print("Transition section (bars 75-84):")
    for i in range(75, 85):
        d = fdi[i]
        hd = hdiff[i]
        c = colors[i]
        print(f"  Bar {i}: FDI={d:.4f}  dFDI={hd:+.4f}  color={c}")
