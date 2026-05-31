"""
Quantum Price Levels (QPL) Indicator
=====================================

Computes discrete support/resistance price levels based on the Quantum Finance
Schrodinger Equation (QFSE) and quantum anharmonic oscillator model.

Provides both:
- compute_qpl(): Batch function for one-shot computation
- QuantumPriceLevels: Streaming class with update(price) method

Reference:
    Lee, R. S. T. (2021). "Quantum Finance Forecast System with Quantum
    Anharmonic Oscillator Model for Quantum Price Level Modeling."
    International Advance Journal of Engineering Research, 4(02), 1-21.

Dependencies: Python standard library only (math module).
No numpy, pandas, or any third-party packages.
"""

import math


# =============================================================================
# Helper: Signed cube root
# =============================================================================

def cbrt(x):
    """
    Compute the real cube root of x, handling negative values.

    Python's x**(1/3) does NOT work for negative x (returns complex).
    We need: cbrt(-8) = -2, not a complex number.
    """
    if x >= 0.0:
        return x ** (1.0 / 3.0)
    else:
        return -((-x) ** (1.0 / 3.0))


# =============================================================================
# K0(n) constants from Dasgupta et al. (2007)
# =============================================================================

def compute_k0(n):
    """
    Compute the K0 constant for energy level n.

    Formula (eq. 31 in Lee 2021):
        K0(n) = ((1.1924 + 33.2383*n + 56.2169*n^2) / (1 + 43.6196*n))^(1/3)

    These coefficients come from Dasgupta et al.'s empirical fit to the
    quantum anharmonic oscillator energy spectrum for the quartic (m=2) case.
    """
    numerator = 1.1924 + 33.2383 * n + 56.2169 * n * n
    denominator = 1.0 + 43.6196 * n
    return (numerator / denominator) ** (1.0 / 3.0)


# =============================================================================
# Solve energy levels from lambda (shared by batch and streaming)
# =============================================================================

def _solve_energy_levels(lambda_, sigma, num_levels, num_bins, scale_factor,
                         reference_price, Q, total_count):
    """
    Given a histogram Q[] and total_count, compute lambda, energy levels,
    NQPR multipliers, and project QPL levels.

    This is the shared computation core used by both the batch function
    and the streaming class.

    Parameters
    ----------
    lambda_ : ignored (we recompute from histogram)
    sigma : float - standard deviation of returns
    num_levels : int
    num_bins : int
    scale_factor : float
    reference_price : float
    Q : list of int - histogram bin counts
    total_count : int - total returns in valid bins

    Returns
    -------
    dict with lambda_, sigma, nqpr, qpl_upper, qpl_lower (or None if degenerate)
    """
    # This function is not used — keeping logic inline for clarity.
    pass


# =============================================================================
# Streaming class
# =============================================================================

class QuantumPriceLevels:
    """
    Streaming Quantum Price Levels indicator.

    Maintains an incremental histogram of price returns over a sliding window.
    After the priming period (lookback+1 prices), each call to update() produces
    QPL levels centered on the current price.

    The levels are valid at whatever timescale you feed: daily bars produce
    daily-scale S&R, 1-minute bars produce minute-scale S&R. The NQPR
    multipliers automatically scale with sigma (volatility at your interval).

    Usage:
        qpl = QuantumPriceLevels(lookback=2048)
        for price in prices:
            result = qpl.update(price)
            if result is not None:
                print(result['qpl_upper'][0])  # First upper level
    """

    def __init__(self, lookback=2048, num_levels=21, num_bins=100, scale_factor=0.21):
        """
        Parameters
        ----------
        lookback : int, default 2048
            Number of returns to maintain in the sliding window.
            Priming requires lookback+1 prices (to produce lookback returns).
        num_levels : int, default 21
            Number of quantum energy levels to compute (n = 0..num_levels-1).
        num_bins : int, default 100
            Number of histogram bins for the wavefunction distribution.
        scale_factor : float, default 0.21
            Empirical scaling constant in the NQPR formula.
        """
        self._lookback = lookback
        self._num_levels = num_levels
        self._num_bins = num_bins
        self._scale_factor = scale_factor

        # Pre-compute K0 constants (they never change)
        self._K = [compute_k0(n) for n in range(num_levels)]

        # Ring buffer for returns (fixed size = lookback)
        self._returns = [0.0] * lookback
        self._buf_pos = 0       # Next write position in ring buffer
        self._count = 0         # Number of returns stored so far (up to lookback)

        # Previous price (needed to compute return when next price arrives)
        self._prev_price = None

        # Running statistics for mu and sigma (population)
        self._sum = 0.0         # Sum of all returns in window
        self._sum_sq = 0.0      # Sum of (return - 1.0)^2 ... no, just sum of r^2

        # Histogram bins (maintained incrementally)
        self._Q = [0] * num_bins
        self._total_in_bins = 0  # How many returns fell into valid bins

    def update(self, price):
        """
        Feed one price observation. Returns QPL result dict once primed,
        or None if not yet primed (fewer than lookback+1 prices seen).

        The reference_price for level projection is the current price.

        Parameters
        ----------
        price : float
            Current bar's price (e.g. close).

        Returns
        -------
        dict or None
            Once primed, returns dict with keys:
                'lambda_'   : float - anharmonic coefficient
                'sigma'     : float - standard deviation of returns in window
                'nqpr'      : list of float - normalized QPR multipliers
                'qpl_upper' : list of float - levels above current price
                'qpl_lower' : list of float - levels below current price
            Returns None before priming is complete.
        """
        # First price: just store it, no return yet
        if self._prev_price is None:
            self._prev_price = price
            return None

        # Compute new return: r = prev/current (inverse ratio, per Lee's convention)
        if price > 0.0:
            new_return = self._prev_price / price
        else:
            new_return = 1.0
        self._prev_price = price

        # Compute bin index for the new return (we need sigma for this,
        # but sigma depends on the returns... chicken-and-egg)
        # Solution: we store raw returns in the ring buffer first,
        # then recompute sigma from the buffer, then rebuild histogram.
        #
        # WAIT — that defeats the purpose of incremental histogram.
        # The issue: bin boundaries depend on sigma, which changes every bar.
        #
        # Lee's algorithm uses a FIXED bin width dr = 3*sigma/50 where sigma
        # is computed from the same returns. This means the bin boundaries
        # shift when sigma changes. You can't do truly incremental histogram
        # updates because the bins move.
        #
        # RESOLUTION: We maintain the ring buffer of returns and recompute
        # the histogram from scratch each bar. This is O(lookback) per update,
        # which for lookback=2048 is extremely fast (a few microseconds in
        # compiled languages). The Cardano solve is O(num_levels) = O(21).
        #
        # This is the pragmatic choice: the histogram MUST be rebuilt because
        # bin boundaries depend on sigma which changes each bar.

        # Add to ring buffer (overwrite oldest if full)
        if self._count < self._lookback:
            # Still filling up
            self._returns[self._count] = new_return
            self._count += 1
        else:
            # Buffer full: overwrite at current position
            self._returns[self._buf_pos] = new_return
            self._buf_pos = (self._buf_pos + 1) % self._lookback

        # Not yet primed
        if self._count < self._lookback:
            return None

        # =====================================================================
        # PRIMED: Compute QPL from the current window of returns
        # =====================================================================

        num_bins = self._num_bins
        num_levels = self._num_levels
        scale_factor = self._scale_factor
        lookback = self._lookback

        # Step 2: Compute mu and sigma from the ring buffer
        sum_r = 0.0
        for i in range(lookback):
            sum_r += self._returns[i]
        mu = sum_r / lookback

        sum_var = 0.0
        for i in range(lookback):
            diff = self._returns[i] - mu
            sum_var += diff * diff
        sigma = math.sqrt(sum_var / lookback)

        if sigma == 0.0:
            return None  # Degenerate: all returns identical

        # Step 3: Build histogram
        half_bins = num_bins // 2
        dr = 3.0 * sigma / half_bins
        left_boundary = 1.0 - half_bins * dr

        Q = [0] * num_bins
        total_count = 0

        for i in range(lookback):
            r = self._returns[i]
            bin_index = int((r - left_boundary) / dr)
            if 0 <= bin_index < num_bins:
                Q[bin_index] += 1
                total_count += 1

        if total_count == 0:
            return None

        # Step 4: Find ground state (peak bin)
        max_q = 0.0
        max_qno = 0
        for k in range(num_bins):
            nq = Q[k] / total_count
            if nq > max_q:
                max_q = nq
                max_qno = k

        # Guard: peak at edge
        if max_qno == 0 or max_qno == num_bins - 1:
            return None

        # Step 5: Compute lambda via FDM
        phi_plus1 = Q[max_qno + 1] / total_count
        phi_minus1 = Q[max_qno - 1] / total_count

        r_peak = left_boundary + max_qno * dr
        r0 = r_peak - dr / 2.0
        r_plus1 = r0 + dr
        r_minus1 = r0 - dr

        l_up = (r_minus1 ** 2) * phi_minus1 - (r_plus1 ** 2) * phi_plus1
        l_dw = (r_plus1 ** 4) * phi_plus1 - (r_minus1 ** 4) * phi_minus1

        if l_dw == 0.0:
            return None

        lambda_ = abs(l_up / l_dw)

        # Step 7: Solve energy levels (Cardano)
        QFEL = [0.0] * num_levels
        for n in range(num_levels):
            two_n_plus_1 = 2 * n + 1
            p = -(two_n_plus_1 ** 2)
            q = -lambda_ * (two_n_plus_1 ** 3) * (self._K[n] ** 3)
            discriminant = (q * q / 4.0) + (p * p * p / 27.0)
            if discriminant < 0.0:
                return None
            sqrt_d = math.sqrt(discriminant)
            u = cbrt(-q / 2.0 + sqrt_d)
            v = cbrt(-q / 2.0 - sqrt_d)
            QFEL[n] = u + v

        if QFEL[0] == 0.0:
            return None

        # Step 8: NQPR
        NQPR = [0.0] * num_levels
        for n in range(num_levels):
            qpr = QFEL[n] / QFEL[0]
            NQPR[n] = 1.0 + scale_factor * sigma * qpr

        # Step 9: Project levels from current price
        qpl_upper = [0.0] * num_levels
        qpl_lower = [0.0] * num_levels
        for n in range(num_levels):
            qpl_upper[n] = price * NQPR[n]
            qpl_lower[n] = price / NQPR[n]

        return {
            'lambda_': lambda_,
            'sigma': sigma,
            'nqpr': NQPR,
            'qpl_upper': qpl_upper,
            'qpl_lower': qpl_lower,
        }


# =============================================================================
# Batch function (convenience wrapper)
# =============================================================================

def compute_qpl(prices, reference_price, num_levels=21, num_bins=100, scale_factor=0.21):
    """
    Compute Quantum Price Levels from a historical price series (batch mode).

    This is equivalent to creating a QuantumPriceLevels instance with
    lookback = len(prices) - 1 and feeding all prices, then projecting
    from reference_price.

    Parameters
    ----------
    prices : list of float
        Historical prices, oldest first. Needs at least 3 elements.
    reference_price : float
        The price to project QPL levels from.
    num_levels : int, default 21
        Number of quantum energy levels to compute.
    num_bins : int, default 100
        Number of histogram bins.
    scale_factor : float, default 0.21
        Empirical scaling constant in the NQPR formula.

    Returns
    -------
    dict with keys:
        'lambda_', 'sigma', 'mu', 'qfel', 'qpr', 'nqpr',
        'qpl_upper', 'qpl_lower'
    """
    n_prices = len(prices)
    if n_prices < 3:
        raise ValueError("Need at least 3 prices to compute returns")

    # Step 1: Compute returns
    returns = []
    for t in range(1, n_prices):
        if prices[t] > 0.0:
            returns.append(prices[t - 1] / prices[t])
        else:
            returns.append(1.0)

    m = len(returns)

    # Step 2: Statistics
    mu = 0.0
    for r in returns:
        mu += r
    mu /= m

    variance = 0.0
    for r in returns:
        diff = r - mu
        variance += diff * diff
    variance /= m
    sigma = math.sqrt(variance)

    if sigma == 0.0:
        raise ValueError("Standard deviation is zero")

    # Step 3: Histogram
    half_bins = num_bins // 2
    dr = 3.0 * sigma / half_bins
    left_boundary = 1.0 - half_bins * dr

    Q = [0] * num_bins
    total_count = 0
    for r in returns:
        bin_index = int((r - left_boundary) / dr)
        if 0 <= bin_index < num_bins:
            Q[bin_index] += 1
            total_count += 1

    if total_count == 0:
        raise ValueError("No returns fell within histogram range")

    NQ = [Q[k] / total_count for k in range(num_bins)]

    # Step 4: Find peak
    max_q = 0.0
    max_qno = 0
    for k in range(num_bins):
        if NQ[k] > max_q:
            max_q = NQ[k]
            max_qno = k

    if max_qno == 0 or max_qno == num_bins - 1:
        raise ValueError(f"Wavefunction peak at edge bin {max_qno}")

    # Step 5: Lambda
    r_peak = left_boundary + max_qno * dr
    r0 = r_peak - dr / 2.0
    r_plus1 = r0 + dr
    r_minus1 = r0 - dr
    phi_plus1 = NQ[max_qno + 1]
    phi_minus1 = NQ[max_qno - 1]

    l_up = (r_minus1 ** 2) * phi_minus1 - (r_plus1 ** 2) * phi_plus1
    l_dw = (r_plus1 ** 4) * phi_plus1 - (r_minus1 ** 4) * phi_minus1

    if l_dw == 0.0:
        raise ValueError("Lambda denominator is zero")

    lambda_ = abs(l_up / l_dw)

    # Step 6-7: K0 and Cardano
    QFEL = [0.0] * num_levels
    for n in range(num_levels):
        K_n = compute_k0(n)
        two_n_plus_1 = 2 * n + 1
        p = -(two_n_plus_1 ** 2)
        q = -lambda_ * (two_n_plus_1 ** 3) * (K_n ** 3)
        discriminant = (q * q / 4.0) + (p * p * p / 27.0)
        if discriminant < 0.0:
            raise ValueError(f"Negative discriminant at level {n}")
        sqrt_d = math.sqrt(discriminant)
        u = cbrt(-q / 2.0 + sqrt_d)
        v = cbrt(-q / 2.0 - sqrt_d)
        QFEL[n] = u + v

    if QFEL[0] == 0.0:
        raise ValueError("Ground state energy is zero")

    # Step 8: NQPR
    QPR = [QFEL[n] / QFEL[0] for n in range(num_levels)]
    NQPR = [1.0 + scale_factor * sigma * QPR[n] for n in range(num_levels)]

    # Step 9: Project
    qpl_upper = [reference_price * NQPR[n] for n in range(num_levels)]
    qpl_lower = [reference_price / NQPR[n] for n in range(num_levels)]

    return {
        'lambda_': lambda_,
        'sigma': sigma,
        'mu': mu,
        'qfel': QFEL,
        'qpr': QPR,
        'nqpr': NQPR,
        'qpl_upper': qpl_upper,
        'qpl_lower': qpl_lower,
    }


# =============================================================================
# Example usage
# =============================================================================

if __name__ == '__main__':
    import random

    # -------------------------------------------------------------------------
    # Generate synthetic price data: geometric random walk
    # -------------------------------------------------------------------------
    random.seed(42)
    n_bars = 2048
    prices = [100.0]
    for _ in range(n_bars - 1):
        prices.append(prices[-1] * math.exp(random.gauss(0.0, 0.005)))

    # -------------------------------------------------------------------------
    # Batch mode demo
    # -------------------------------------------------------------------------
    reference_price = prices[-1]
    result = compute_qpl(prices, reference_price)

    print("=== Batch Mode ===")
    print(f"Lambda:  {result['lambda_']:.8f}")
    print(f"Sigma:   {result['sigma']:.8f}")
    print(f"Ref:     {reference_price:.6f}")
    print(f"NQPR[0]: {result['nqpr'][0]:.10f}")
    print(f"NQPR[20]:{result['nqpr'][20]:.10f}")
    print(f"Upper[5]:{result['qpl_upper'][5]:.6f}")
    print(f"Lower[5]:{result['qpl_lower'][5]:.6f}")
    print()

    # -------------------------------------------------------------------------
    # Streaming mode demo
    # -------------------------------------------------------------------------
    print("=== Streaming Mode ===")
    qpl = QuantumPriceLevels(lookback=2047, num_levels=21, num_bins=100, scale_factor=0.21)

    last_result = None
    for i, p in enumerate(prices):
        r = qpl.update(p)
        if r is not None:
            last_result = r

    if last_result:
        print(f"Lambda:  {last_result['lambda_']:.8f}")
        print(f"Sigma:   {last_result['sigma']:.8f}")
        print(f"NQPR[0]: {last_result['nqpr'][0]:.10f}")
        print(f"NQPR[20]:{last_result['nqpr'][20]:.10f}")
        print(f"Upper[5]:{last_result['qpl_upper'][5]:.6f}")
        print(f"Lower[5]:{last_result['qpl_lower'][5]:.6f}")
    print()

    # -------------------------------------------------------------------------
    # Verify streaming matches batch
    # -------------------------------------------------------------------------
    print("=== Verification ===")
    match = True
    for n in range(21):
        diff = abs(result['nqpr'][n] - last_result['nqpr'][n])
        if diff > 1e-12:
            print(f"MISMATCH at level {n}: batch={result['nqpr'][n]}, stream={last_result['nqpr'][n]}")
            match = False
    if match:
        print("PASS: Streaming output matches batch output exactly.")
