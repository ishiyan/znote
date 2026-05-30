"""
Moving Mini-Max — Streaming API
================================

A streaming (bar-by-bar) implementation of the Moving Mini-Max indicator.
Accepts one price sample at a time, maintains an internal sliding window,
and returns indicator output after each update.

Based on: Z. K. Silagadze, "Moving Mini-Max -- a new indicator for technical
analysis," IFTA Journal 11 (2011), 46-49. arXiv:0802.0984v2.

This file is self-contained (all computation functions inlined) and uses
only the Python standard library to facilitate porting to Rust, Zig, Go, etc.

See streaming.md for full documentation, state diagrams, and flowcharts.
"""

import math


# ---------------------------------------------------------------------------
# Core computation functions (inlined for self-containment)
# ---------------------------------------------------------------------------

def _calc_q_values(prices, n, m, negate):
    """
    Compute Q_{i,i+1} and Q_{i,i-1} for each position i in the window.

    For "up" mini-max (emphasizes maxima): negate=False
    For "down" mini-max (emphasizes minima): negate=True

    The Q-value measures how much neighboring prices differ from the
    current price, using the symmetric relative difference:
        2*(S_neighbor - S_i) / (S_neighbor + S_i)

    Parameters
    ----------
    prices : list of float
        Price window of length n. prices[0] = oldest, prices[n-1] = newest.
    n : int
        Window length.
    m : int
        Smoothing window width (number of neighbors to examine in each direction).
    negate : bool
        If True, negate the exponent argument (for down mini-max).

    Returns
    -------
    q_plus : list of float
        Q_{i,i+1} for i = 0..n-1 (forward-looking weights).
    q_minus : list of float
        Q_{i,i-1} for i = 0..n-1 (backward-looking weights).
    """
    sign = -1.0 if negate else 1.0
    q_plus = [0.0] * n
    q_minus = [0.0] * n

    for i in range(n):
        s_i = prices[i]
        sum_plus = 0.0
        sum_minus = 0.0

        for k in range(1, m + 1):
            # Forward neighbor: clamp to last price if out of bounds
            idx_fwd = i + k
            s_fwd = prices[idx_fwd] if idx_fwd < n else prices[n - 1]

            # Backward neighbor: clamp to first price if out of bounds
            idx_bwd = i - k
            s_bwd = prices[idx_bwd] if idx_bwd >= 0 else prices[0]

            # Symmetric relative difference with forward neighbor
            denom_fwd = s_fwd + s_i
            if denom_fwd == 0.0:
                arg_fwd = 0.0
            else:
                arg_fwd = sign * 2.0 * (s_fwd - s_i) / denom_fwd

            # Symmetric relative difference with backward neighbor
            denom_bwd = s_bwd + s_i
            if denom_bwd == 0.0:
                arg_bwd = 0.0
            else:
                arg_bwd = sign * 2.0 * (s_bwd - s_i) / denom_bwd

            sum_plus += math.exp(arg_fwd)
            sum_minus += math.exp(arg_bwd)

        q_plus[i] = sum_plus
        q_minus[i] = sum_minus

    return q_plus, q_minus


def _calc_p_values(q_plus, q_minus, n):
    """
    Compute transition probabilities from Q-values.

    P_{i,i+1} = Q_{i,i+1} / (Q_{i,i+1} + Q_{i,i-1})
    P_{i,i-1} = Q_{i,i-1} / (Q_{i,i+1} + Q_{i,i-1})

    These always sum to 1 at each position.

    Parameters
    ----------
    q_plus : list of float
    q_minus : list of float
    n : int

    Returns
    -------
    p_plus : list of float — P_{i,i+1}
    p_minus : list of float — P_{i,i-1}
    """
    p_plus = [0.0] * n
    p_minus = [0.0] * n

    for i in range(n):
        denom = q_plus[i] + q_minus[i]
        if denom == 0.0:
            p_plus[i] = 0.5
            p_minus[i] = 0.5
        else:
            p_plus[i] = q_plus[i] / denom
            p_minus[i] = q_minus[i] / denom

    return p_plus, p_minus


def _calc_minimax(p_plus, p_minus, n):
    """
    Compute the normalized mini-max series via chained recurrence.

    u_1 = 1
    u_i = (P_{i-1, i} / P_{i, i-1}) * u_{i-1}

    where:
        P_{i-1, i} = p_plus[i-1]   (probability at i-1 of moving right)
        P_{i, i-1} = p_minus[i]     (probability at i of moving left)

    Then normalize: result[i] = u_i / sum(u_j)

    Parameters
    ----------
    p_plus : list of float
    p_minus : list of float
    n : int

    Returns
    -------
    list of float — normalized mini-max values, length n, summing to 1.0
    """
    u = [0.0] * n
    u[0] = 1.0

    for i in range(1, n):
        p_right = p_plus[i - 1]   # P_{i-1, i}
        p_left = p_minus[i]       # P_{i, i-1}

        if p_left == 0.0:
            u[i] = u[i - 1] * 1e10
        else:
            u[i] = (p_right / p_left) * u[i - 1]

    total = sum(u)
    if total == 0.0:
        return [1.0 / n] * n
    else:
        return [val / total for val in u]


def _find_peaks(values, num_peaks, min_separation):
    """
    Find distinct local peaks in a 1-D series.

    A local peak is a value >= both its neighbors. Peaks are returned
    sorted by value descending. Adjacent peaks within min_separation
    of a stronger peak are suppressed (greedy non-maximum suppression).

    Parameters
    ----------
    values : list of float
    num_peaks : int — max number of peaks to return
    min_separation : int — minimum distance between returned peaks

    Returns
    -------
    list of (value, index) tuples, sorted by value descending.
    """
    n = len(values)
    candidates = []

    for i in range(n):
        if i == 0:
            is_peak = values[i] >= values[i + 1] if n > 1 else True
        elif i == n - 1:
            is_peak = values[i] >= values[i - 1]
        else:
            is_peak = (values[i] >= values[i - 1] and
                       values[i] >= values[i + 1])
        if is_peak:
            candidates.append((values[i], i))

    # Sort strongest first
    candidates.sort(reverse=True)

    # Greedy selection with minimum separation
    selected = []
    for val, idx in candidates:
        if len(selected) >= num_peaks:
            break
        too_close = False
        for _, sel_idx in selected:
            if abs(idx - sel_idx) < min_separation:
                too_close = True
                break
        if not too_close:
            selected.append((val, idx))

    return selected


# ---------------------------------------------------------------------------
# Streaming class
# ---------------------------------------------------------------------------

class MovingMiniMax:
    """
    Streaming Moving Mini-Max indicator.

    Accepts one price bar at a time via update(). Maintains an internal
    sliding window of the last n prices. Once primed (n bars received),
    each update triggers a full recomputation of the indicator.

    The full recomputation is necessary because:
    - The chained recurrence (u_i depends on all u_1..u_{i-1}) means
      every value changes when the window slides.
    - The normalization (sum to 1.0) couples all values together.
    - Boundary conditions at both edges change with each new bar.

    Computational cost: O(n*m) per bar. For n=300, m=5: ~3000 exp() calls,
    well under 1ms on modern hardware.

    Parameters
    ----------
    m : int
        Smoothing window width (default: 5).
    n : int
        Lookback window size (default: 300).
    num_extrema : int
        Number of distinct support/resistance levels to detect (default: 3).
    with_distribution : bool
        If True, include full n-length distribution arrays in output (default: False).

    Example
    -------
    >>> indicator = MovingMiniMax(m=5, n=100, num_extrema=3)
    >>> for price in price_feed:
    ...     result = indicator.update(price)
    ...     if result['primed']:
    ...         print(result['up'], result['resistances'])
    """

    def __init__(self, m=5, n=300, num_extrema=3, with_distribution=False):
        if m < 1:
            raise ValueError("m must be >= 1")
        if n <= 2 * m:
            raise ValueError("n must be > 2*m")
        if num_extrema < 1:
            raise ValueError("num_extrema must be >= 1")

        self._m = m
        self._n = n
        self._num_extrema = num_extrema
        self._with_distribution = with_distribution

        # Internal state: price buffer
        self._buffer = []
        self._count = 0

    def is_primed(self):
        """Return True once n prices have been received."""
        return self._count >= self._n

    def reset(self):
        """Clear all internal state. Indicator returns to UNPRIMED."""
        self._buffer = []
        self._count = 0

    def update(self, price):
        """
        Feed one new price bar and return indicator output.

        Parameters
        ----------
        price : float
            The new price value (must be positive).

        Returns
        -------
        dict with keys:
            'primed' : bool
            'up' : float — latest bar's up-minimax value (NaN if not primed)
            'down' : float — latest bar's down-minimax value (NaN if not primed)
            'resistances' : list of {price, offset, strength} dicts
            'supports' : list of {price, offset, strength} dicts
            'up_distribution' : list of float (empty if not primed or with_distribution=False)
            'down_distribution' : list of float (same)
        """
        # --- Append to buffer ---
        self._buffer.append(price)
        self._count += 1

        # --- Trim buffer to last n elements ---
        if len(self._buffer) > self._n:
            self._buffer = self._buffer[len(self._buffer) - self._n:]

        # --- Check if primed ---
        if self._count < self._n:
            return {
                'primed': False,
                'up': float('nan'),
                'down': float('nan'),
                'resistances': [],
                'supports': [],
                'up_distribution': [],
                'down_distribution': [],
            }

        # --- Full recomputation over the window ---
        n = self._n
        m = self._m
        window = self._buffer  # exactly n elements at this point

        # Compute Q-values
        q_up_plus, q_up_minus = _calc_q_values(window, n, m, negate=False)
        q_dn_plus, q_dn_minus = _calc_q_values(window, n, m, negate=True)

        # Compute transition probabilities
        p_up_plus, p_up_minus = _calc_p_values(q_up_plus, q_up_minus, n)
        p_dn_plus, p_dn_minus = _calc_p_values(q_dn_plus, q_dn_minus, n)

        # Compute normalized mini-max series
        up_dist = _calc_minimax(p_up_plus, p_up_minus, n)
        dn_dist = _calc_minimax(p_dn_plus, p_dn_minus, n)

        # --- Find distinct peaks ---
        min_sep = max(m, 2)
        u_peaks = _find_peaks(up_dist, self._num_extrema, min_sep)
        d_peaks = _find_peaks(dn_dist, self._num_extrema, min_sep)

        # --- Build resistance list ---
        resistances = []
        for strength, idx in u_peaks:
            resistances.append({
                'price': window[idx],
                'offset': (n - 1) - idx,
                'strength': strength,
            })

        # --- Build support list ---
        supports = []
        for strength, idx in d_peaks:
            supports.append({
                'price': window[idx],
                'offset': (n - 1) - idx,
                'strength': strength,
            })

        # --- Latest bar values (rightmost position in window) ---
        up_latest = up_dist[n - 1]
        dn_latest = dn_dist[n - 1]

        # --- Build result ---
        result = {
            'primed': True,
            'up': up_latest,
            'down': dn_latest,
            'resistances': resistances,
            'supports': supports,
            'up_distribution': up_dist if self._with_distribution else [],
            'down_distribution': dn_dist if self._with_distribution else [],
        }

        return result


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import random

    random.seed(42)

    # Generate synthetic price series: sine wave + trend + noise
    num_bars = 400
    prices = []
    for i in range(num_bars):
        trend = 100.0 + 0.02 * i
        cycle = 10.0 * math.sin(2.0 * math.pi * i / 50.0)
        noise = random.gauss(0.0, 1.5)
        price = trend + cycle + noise
        if price <= 0:
            price = 0.01
        prices.append(price)

    # Create streaming indicator
    m = 5
    n = 200
    num_extrema = 3
    indicator = MovingMiniMax(m=m, n=n, num_extrema=num_extrema,
                              with_distribution=False)

    print(f"Streaming Moving Mini-Max (m={m}, n={n}, num_extrema={num_extrema})")
    print(f"  Feeding {num_bars} bars one at a time...")
    print()

    # Feed bars one by one
    first_primed_bar = None
    last_result = None

    for bar_idx, price in enumerate(prices):
        result = indicator.update(price)

        # Record when first primed
        if result['primed'] and first_primed_bar is None:
            first_primed_bar = bar_idx
            print(f"  Primed at bar {bar_idx}")
            print(f"    up={result['up']:.6f}, down={result['down']:.6f}")
            print(f"    resistances: {len(result['resistances'])}")
            print(f"    supports: {len(result['supports'])}")
            print()

        last_result = result

    # Show final result
    print(f"  Final result (bar {num_bars - 1}):")
    print(f"    primed: {last_result['primed']}")
    print(f"    up:   {last_result['up']:.6f}")
    print(f"    down: {last_result['down']:.6f}")
    print()
    print(f"    Resistance levels:")
    for r in last_result['resistances']:
        print(f"      price={r['price']:.2f}, offset={r['offset']:3d} bars, "
              f"strength={r['strength']:.6f}")
    print(f"    Support levels:")
    for s in last_result['supports']:
        print(f"      price={s['price']:.2f}, offset={s['offset']:3d} bars, "
              f"strength={s['strength']:.6f}")
    print()
    print(f"    up_distribution length: {len(last_result['up_distribution'])}")
    print(f"    down_distribution length: {len(last_result['down_distribution'])}")

    # Demonstrate with_distribution=True
    print()
    print("  --- With distribution enabled ---")
    indicator2 = MovingMiniMax(m=m, n=n, num_extrema=num_extrema,
                               with_distribution=True)
    for price in prices:
        result2 = indicator2.update(price)

    print(f"    up_distribution length: {len(result2['up_distribution'])}")
    print(f"    down_distribution length: {len(result2['down_distribution'])}")
    dist_sum = sum(result2['up_distribution'])
    print(f"    up_distribution sum: {dist_sum:.6f} (should be 1.0)")

    # Demonstrate reset
    print()
    print("  --- After reset ---")
    indicator2.reset()
    result_after_reset = indicator2.update(prices[0])
    print(f"    primed: {result_after_reset['primed']}")
    print(f"    up: {result_after_reset['up']} (should be nan)")
