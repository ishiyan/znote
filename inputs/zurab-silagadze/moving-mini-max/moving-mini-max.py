"""
Moving Mini-Max Indicator
==========================

A nonlinear indicator for technical analysis that emphasizes local maximums
and minimums in price series with inherent smoothing.

Based on: Z. K. Silagadze, "Moving Mini-Max -- a new indicator for technical
analysis," IFTA Journal 11 (2011), 46-49. arXiv:0802.0984v2.

This implementation uses only the Python standard library (no numpy/pandas)
to facilitate porting to Rust, Zig, Go, etc.
"""

import math


def calc_q_values(prices, n, m, negate):
    """
    Compute Q_{i,i+1} and Q_{i,i-1} for each position i = 1..n.

    The Q-values represent unnormalized transition weights based on
    relative price differences with neighboring bars.

    For the "up" mini-max (emphasizes maxima): negate=False
    For the "down" mini-max (emphasizes minima): negate=True

    Parameters
    ----------
    prices : list of float
        Price series of length n. prices[0] = S_1, prices[n-1] = S_n.
    n : int
        Length of the price window.
    m : int
        Smoothing window width.
    negate : bool
        If True, negate the exponent (for down mini-max).

    Returns
    -------
    q_plus : list of float
        Q_{i,i+1} for i = 0..n-1 (0-indexed).
    q_minus : list of float
        Q_{i,i-1} for i = 0..n-1 (0-indexed).
    """
    # Sign multiplier: +1 for up mini-max, -1 for down mini-max
    sign = -1.0 if negate else 1.0

    q_plus = [0.0] * n   # Q_{i,i+1}
    q_minus = [0.0] * n  # Q_{i,i-1}

    for i in range(n):
        # Current price S_i (1-indexed i corresponds to 0-indexed prices[i])
        s_i = prices[i]

        sum_plus = 0.0
        sum_minus = 0.0

        for k in range(1, m + 1):
            # --- Forward neighbor S_{i+k} ---
            # Boundary condition: if i+k > n-1 (0-indexed), clamp to S_n = prices[n-1]
            idx_plus = i + k
            if idx_plus >= n:
                s_forward = prices[n - 1]
            else:
                s_forward = prices[idx_plus]

            # --- Backward neighbor S_{i-k} ---
            # Boundary condition: if i-k < 0 (0-indexed), clamp to S_1 = prices[0]
            idx_minus = i - k
            if idx_minus < 0:
                s_backward = prices[0]
            else:
                s_backward = prices[idx_minus]

            # Compute relative difference: 2*(S_neighbor - S_i) / (S_neighbor + S_i)
            # This is the symmetric percentage change (difference / average).
            #
            # Guard against zero denominator (prices should always be positive,
            # but protect anyway).
            denom_plus = s_forward + s_i
            if denom_plus == 0.0:
                arg_plus = 0.0
            else:
                arg_plus = sign * 2.0 * (s_forward - s_i) / denom_plus

            denom_minus = s_backward + s_i
            if denom_minus == 0.0:
                arg_minus = 0.0
            else:
                arg_minus = sign * 2.0 * (s_backward - s_i) / denom_minus

            sum_plus += math.exp(arg_plus)
            sum_minus += math.exp(arg_minus)

        q_plus[i] = sum_plus
        q_minus[i] = sum_minus

    return q_plus, q_minus


def calc_p_values(q_plus, q_minus, n):
    """
    Compute transition probabilities P_{i,i+1} and P_{i,i-1} from Q-values.

    P_{i,i+1} = Q_{i,i+1} / (Q_{i,i+1} + Q_{i,i-1})
    P_{i,i-1} = Q_{i,i-1} / (Q_{i,i+1} + Q_{i,i-1})

    Parameters
    ----------
    q_plus : list of float
        Q_{i,i+1} values.
    q_minus : list of float
        Q_{i,i-1} values.
    n : int
        Length of the window.

    Returns
    -------
    p_plus : list of float
        P_{i,i+1} for i = 0..n-1.
    p_minus : list of float
        P_{i,i-1} for i = 0..n-1.
    """
    p_plus = [0.0] * n
    p_minus = [0.0] * n

    for i in range(n):
        denom = q_plus[i] + q_minus[i]
        if denom == 0.0:
            # Degenerate case: assign equal probability
            p_plus[i] = 0.5
            p_minus[i] = 0.5
        else:
            p_plus[i] = q_plus[i] / denom
            p_minus[i] = q_minus[i] / denom

    return p_plus, p_minus


def calc_minimax(p_plus, p_minus, n):
    """
    Compute the normalized mini-max series from transition probabilities.

    The recurrence is:
        u_1 = 1
        u_i = (P_{i-1,i} / P_{i,i-1}) * u_{i-1}    for i = 2..n

    where:
        P_{i-1,i} = P_{i-1, i-1+1} = p_plus[i-1]   (probability at i-1 of moving right to i)
        P_{i,i-1} = p_minus[i]                        (probability at i of moving left to i-1)

    Then normalize: u(S)_i = u_i / sum(u_j)

    Parameters
    ----------
    p_plus : list of float
        P_{i,i+1} for i = 0..n-1 (0-indexed).
    p_minus : list of float
        P_{i,i-1} for i = 0..n-1 (0-indexed).
    n : int
        Window length.

    Returns
    -------
    minimax : list of float
        Normalized mini-max values, length n.
    """
    # Compute unnormalized u_i values
    u = [0.0] * n
    u[0] = 1.0

    for i in range(1, n):
        # P_{i-1, i} = probability at position (i-1) of moving right = p_plus[i-1]
        p_prev_to_i = p_plus[i - 1]

        # P_{i, i-1} = probability at position i of moving left = p_minus[i]
        p_i_to_prev = p_minus[i]

        # Guard against division by zero
        if p_i_to_prev == 0.0:
            # If probability of moving left from i is zero, u_i grows unbounded;
            # cap it at a large value (will be normalized anyway)
            u[i] = u[i - 1] * 1e10
        else:
            u[i] = (p_prev_to_i / p_i_to_prev) * u[i - 1]

    # Normalize so that sum = 1
    total = sum(u)
    if total == 0.0:
        # Degenerate: uniform distribution
        minimax = [1.0 / n] * n
    else:
        minimax = [val / total for val in u]

    return minimax


def moving_minimax(prices, m=5, n=300):
    """
    Compute the Moving Mini-Max indicator on a price series.

    Parameters
    ----------
    prices : list of float
        Full price series (e.g., closing prices). Must have at least n elements.
        The last n elements are used as the analysis window.
    m : int, optional
        Smoothing window width (default: 5). Controls noise suppression.
        Larger m = smoother output, fewer detected peaks.
    n : int, optional
        Lookback window size (default: 300). Number of bars to analyze.

    Returns
    -------
    dict with keys:
        'uSi' : list of float
            Up mini-max values (length n). Peaks at local price maxima.
        'dSi' : list of float
            Down mini-max values (length n). Peaks at local price minima.
        'resistance_price' : float
            Price at the strongest local maximum (where uSi peaks).
        'support_price' : float
            Price at the strongest local minimum (where dSi peaks).
        'resistance_offset' : int
            Bars from the end of the window to the resistance level.
            0 = most recent bar, n-1 = oldest bar.
        'support_offset' : int
            Bars from the end of the window to the support level.

    Raises
    ------
    ValueError
        If prices has fewer than n elements, or parameters are invalid.
    """
    # --- Validate parameters ---
    if m < 1:
        raise ValueError("m must be >= 1")
    if n <= 2 * m:
        raise ValueError("n must be > 2*m")
    if len(prices) < n:
        raise ValueError(
            f"prices has {len(prices)} elements, need at least {n}"
        )

    # --- Extract the last n prices as the analysis window ---
    # window[0] = oldest bar (S_1 in paper), window[n-1] = newest bar (S_n)
    window = prices[len(prices) - n:]

    # --- Compute Q-values ---
    # Up mini-max: positive exponent (emphasizes maxima)
    q_up_plus, q_up_minus = calc_q_values(window, n, m, negate=False)
    # Down mini-max: negative exponent (emphasizes minima)
    q_dn_plus, q_dn_minus = calc_q_values(window, n, m, negate=True)

    # --- Compute transition probabilities ---
    p_up_plus, p_up_minus = calc_p_values(q_up_plus, q_up_minus, n)
    p_dn_plus, p_dn_minus = calc_p_values(q_dn_plus, q_dn_minus, n)

    # --- Compute normalized mini-max series ---
    uSi = calc_minimax(p_up_plus, p_up_minus, n)
    dSi = calc_minimax(p_dn_plus, p_dn_minus, n)

    # --- Find peaks (strongest extrema) ---
    # Resistance: bar with maximum uSi value
    max_u = -1.0
    resistance_idx = 0
    for i in range(n):
        if uSi[i] > max_u:
            max_u = uSi[i]
            resistance_idx = i

    # Support: bar with maximum dSi value
    max_d = -1.0
    support_idx = 0
    for i in range(n):
        if dSi[i] > max_d:
            max_d = dSi[i]
            support_idx = i

    # --- Compute offsets (bars from end of window) ---
    # offset = 0 means the most recent bar, offset = n-1 means the oldest
    resistance_offset = (n - 1) - resistance_idx
    support_offset = (n - 1) - support_idx

    return {
        'uSi': uSi,
        'dSi': dSi,
        'resistance_price': window[resistance_idx],
        'support_price': window[support_idx],
        'resistance_offset': resistance_offset,
        'support_offset': support_offset,
    }


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Generate a synthetic price series: sine wave + upward drift + noise
    # This simulates a price with clear peaks and troughs.
    import random

    random.seed(42)

    num_bars = 400
    prices = []
    for i in range(num_bars):
        # Base: upward trending sine wave
        trend = 100.0 + 0.02 * i
        cycle = 10.0 * math.sin(2.0 * math.pi * i / 50.0)
        noise = random.gauss(0.0, 1.5)
        price = trend + cycle + noise
        # Prices must be positive for the indicator to work
        if price <= 0:
            price = 0.01
        prices.append(price)

    # Compute the Moving Mini-Max with default parameters
    m = 5
    n = 200

    result = moving_minimax(prices, m=m, n=n)

    print(f"Moving Mini-Max (m={m}, n={n})")
    print(f"  Window: bars {num_bars - n} to {num_bars - 1}")
    print(f"  Resistance price: {result['resistance_price']:.4f}")
    print(f"  Resistance offset: {result['resistance_offset']} bars from latest")
    print(f"  Support price:     {result['support_price']:.4f}")
    print(f"  Support offset:    {result['support_offset']} bars from latest")
    print()

    # Verify normalization
    u_sum = sum(result['uSi'])
    d_sum = sum(result['dSi'])
    print(f"  uSi sum: {u_sum:.6f} (should be 1.0)")
    print(f"  dSi sum: {d_sum:.6f} (should be 1.0)")
    print()

    # Show top-5 peaks in uSi (resistance candidates)
    indexed_u = [(val, i) for i, val in enumerate(result['uSi'])]
    indexed_u.sort(reverse=True)
    print("  Top 5 resistance candidates (uSi peaks):")
    for val, idx in indexed_u[:5]:
        offset = (n - 1) - idx
        bar_price = prices[len(prices) - n + idx]
        print(f"    offset={offset:3d} bars, price={bar_price:.2f}, uSi={val:.6f}")

    # Show top-5 peaks in dSi (support candidates)
    indexed_d = [(val, i) for i, val in enumerate(result['dSi'])]
    indexed_d.sort(reverse=True)
    print("  Top 5 support candidates (dSi peaks):")
    for val, idx in indexed_d[:5]:
        offset = (n - 1) - idx
        bar_price = prices[len(prices) - n + idx]
        print(f"    offset={offset:3d} bars, price={bar_price:.2f}, dSi={val:.6f}")
