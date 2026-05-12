"""
JRSX — Jurik RSX (Relative Strength eXtended)

A momentum oscillator (0–100) that uses triple-cascaded, lag-compensated EMAs
applied to both signed and absolute momentum. Produces output similar to RSI
but with significantly less lag and smoother transitions.

Reference: Decompiled from WealthScript implementation by Mark Jurik.
"""

import numpy as np


def jrsx(prices: np.ndarray, length: int = 14) -> np.ndarray:
    """
    Compute the Jurik RSX indicator.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values (e.g. close prices).
    length : int, optional
        Smoothing period (default 14). Must be >= 2.

    Returns
    -------
    np.ndarray
        Array of same length as `prices` with JRSX values in [0, 100].
        Warmup bars are set to NaN.
    """
    n = len(prices)
    out = np.full(n, np.nan)

    if n < 2 or length < 2:
        return out

    # EMA gain and complement
    kg = 3.0 / (length + 2)
    c = 1.0 - kg

    # Warmup: need at least max(length-1, 5) bars of data before output
    warmup = max(length - 1, 5)

    # Signal path accumulators (3 cascaded stages)
    sig1_a = sig1_b = 0.0
    sig2_a = sig2_b = 0.0
    sig3_a = sig3_b = 0.0

    # Denominator path accumulators (3 cascaded stages)
    den1_a = den1_b = 0.0
    den2_a = den2_b = 0.0
    den3_a = den3_b = 0.0

    for bar in range(1, n):
        # Momentum scaled by 100
        mom = 100.0 * (prices[bar] - prices[bar - 1])
        abs_mom = abs(mom)

        # --- Signal path (signed momentum) ---
        # Stage 1
        sig1_a = c * sig1_a + kg * mom
        sig1_b = kg * sig1_a + c * sig1_b
        s1 = 1.5 * sig1_a - 0.5 * sig1_b

        # Stage 2
        sig2_a = c * sig2_a + kg * s1
        sig2_b = kg * sig2_a + c * sig2_b
        s2 = 1.5 * sig2_a - 0.5 * sig2_b

        # Stage 3
        sig3_a = c * sig3_a + kg * s2
        sig3_b = kg * sig3_a + c * sig3_b
        numerator = 1.5 * sig3_a - 0.5 * sig3_b

        # --- Denominator path (absolute momentum) ---
        # Stage 1
        den1_a = c * den1_a + kg * abs_mom
        den1_b = kg * den1_a + c * den1_b
        d1 = 1.5 * den1_a - 0.5 * den1_b

        # Stage 2
        den2_a = c * den2_a + kg * d1
        den2_b = kg * den2_a + c * den2_b
        d2 = 1.5 * den2_a - 0.5 * den2_b

        # Stage 3
        den3_a = c * den3_a + kg * d2
        den3_b = kg * den3_a + c * den3_b
        denominator = 1.5 * den3_a - 0.5 * den3_b

        # --- Produce output after warmup ---
        if bar >= warmup:
            if denominator != 0.0:
                value = (numerator / denominator + 1.0) * 50.0
            else:
                value = 50.0
            # Clamp to [0, 100]
            out[bar] = max(0.0, min(100.0, value))

    return out


if __name__ == "__main__":
    # Quick sanity check with random data
    np.random.seed(42)
    test_prices = np.cumsum(np.random.randn(100)) + 100.0
    result = jrsx(test_prices, length=14)
    valid = result[~np.isnan(result)]
    print(f"JRSX computed: {len(valid)} valid bars, "
          f"range [{valid.min():.2f}, {valid.max():.2f}]")
