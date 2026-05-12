"""
JXRSX — Extended RSX (Series-Length Input)

Identical algorithm to JRSX but accepts a length *series* (per-bar array).
In practice, only the first bar's length value is used for the EMA gain Kg.
This API enables wrappers like JARSX to pass pre-computed length arrays.

Reference: Decompiled from WealthScript implementation by Mark Jurik.
"""

import numpy as np


def jxrsx(prices: np.ndarray, length_series: np.ndarray) -> np.ndarray:
    """
    Compute the Jurik RSX indicator with a series-length input.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of price values (e.g. close prices).
    length_series : np.ndarray
        1-D array of length values. Only index 0 is used for Kg computation.
        Must have length_series[0] >= 2.

    Returns
    -------
    np.ndarray
        Array of same length as `prices` with JXRSX values in [0, 100].
        Warmup bars are set to NaN.
    """
    n = len(prices)
    out = np.full(n, np.nan)

    # Read length from bar 0 only (faithful to decompiled source)
    length = int(length_series[0])

    if n < 2 or length < 2:
        return out

    # EMA gain and complement (set once, never updated)
    kg = 3.0 / (length + 2)
    c = 1.0 - kg

    # Warmup period
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
    # Quick sanity check — should produce identical results to jrsx(prices, 14)
    np.random.seed(42)
    test_prices = np.cumsum(np.random.randn(100)) + 100.0
    test_lengths = np.full(100, 14.0)  # constant series
    result = jxrsx(test_prices, test_lengths)
    valid = result[~np.isnan(result)]
    print(f"JXRSX computed: {len(valid)} valid bars, "
          f"range [{valid.min():.2f}, {valid.max():.2f}]")
