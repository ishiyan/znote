"""
Quantum Price Levels (QPL) Indicator
=====================================

Computes discrete support/resistance price levels based on the Quantum Finance
Schrodinger Equation (QFSE) and quantum anharmonic oscillator model.

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
# Step 6: K0(n) constants from Dasgupta et al. (2007)
# =============================================================================

def compute_k0(n):
    """
    Compute the K0 constant for energy level n.

    Formula (eq. 31 in Lee 2021):
        K0(n) = ((1.1924 + 33.2383*n + 56.2169*n^2) / (1 + 43.6106*n))^(1/3)

    NOTE: The published paper/book text prints the denominator constant as
    43.6196, but that is a typo. Both deployed reference implementations
    (the MQ4 QPL_Calculation.mq4 and the official Python on qffc.uic.edu.cn)
    use 43.6106, which we follow here.

    These coefficients come from Dasgupta et al.'s empirical fit to the
    quantum anharmonic oscillator energy spectrum for the quartic (m=2) case.
    """
    numerator = 1.1924 + 33.2383 * n + 56.2169 * n * n
    denominator = 1.0 + 43.6106 * n
    return (numerator / denominator) ** (1.0 / 3.0)


# =============================================================================
# Main computation
# =============================================================================

def compute_qpl(prices, reference_price, num_levels=21, num_bins=100, scale_factor=0.21):
    """
    Compute Quantum Price Levels from a historical price series.

    The algorithm has two independent parts:
    1. CALIBRATION: Compute λ and NQPR multipliers from the price history.
       This uses consecutive price ratios (returns) to build the quantum
       wavefunction and solve for energy levels.
    2. PROJECTION: Apply NQPR multipliers to a reference price to get
       concrete support/resistance levels.

    In Lee's original paper, calibration uses daily closes and projection
    uses the day's open (levels are intraday S&R targets). But the math
    works with any timeframe — the prices just need to be consecutive
    observations at the same interval.

    Parameters
    ----------
    prices : list of float
        Historical prices (e.g. closes), oldest first. Must have at least
        num_bins/2 + 2 elements (practically, 2048+ is recommended).
        Used for calibration (computing λ from the return distribution).
    reference_price : float
        The price to project QPL levels from. Typically today's open
        (for intraday use) or the last close (for next-bar levels).
    num_levels : int, default 21
        Number of quantum energy levels to compute (n = 0..num_levels-1).
    num_bins : int, default 100
        Number of histogram bins for the wavefunction distribution.
    scale_factor : float, default 0.21
        Empirical scaling constant in the NQPR formula.

    Returns
    -------
    dict with keys:
        'lambda_'   : float - the anharmonic coefficient
        'sigma'     : float - standard deviation of returns
        'mu'        : float - mean of returns
        'qfel'      : list of float - quantum finance energy levels [0..num_levels-1]
        'qpr'       : list of float - quantum price returns (normalized by ground state)
        'nqpr'      : list of float - normalized QPR values
        'qpl_upper' : list of float - upper price levels (reference * NQPR[n])
        'qpl_lower' : list of float - lower price levels (reference / NQPR[n])
    """

    n_prices = len(prices)
    if n_prices < 3:
        raise ValueError("Need at least 3 prices to compute returns")

    # =========================================================================
    # Step 1: Compute consecutive price ratios (returns)
    # =========================================================================
    # r(t) = prices[t-1] / prices[t], for t = 1..N-1
    # This is the INVERSE return ratio, matching Lee's MQ4 and Python code.
    # For a price going up, r < 1; for price going down, r > 1.
    # Most returns cluster around 1.0.

    returns = []
    for t in range(1, n_prices):
        if prices[t] > 0.0:
            returns.append(prices[t - 1] / prices[t])
        else:
            # Guard against zero/negative prices (shouldn't happen in real data)
            returns.append(1.0)

    m = len(returns)  # Number of return observations

    # =========================================================================
    # Step 2: Compute mean (mu) and standard deviation (sigma) of returns
    # =========================================================================
    # Using POPULATION std dev (divide by M, not M-1), matching Lee's code.

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
        raise ValueError("Standard deviation is zero (all returns identical)")

    # =========================================================================
    # Step 3: Build wavefunction histogram (100 bins centered at r=1)
    # =========================================================================
    # Bin width: dr = 3*sigma/50
    # This means the 100 bins span 100*dr = 6*sigma total, i.e. ±3*sigma around 1.0
    # (covers ~99.7% of returns assuming roughly normal distribution)

    half_bins = num_bins // 2  # 50 for default num_bins=100
    dr = 3.0 * sigma / half_bins

    # Left boundary of bin 0:
    left_boundary = 1.0 - half_bins * dr

    # Histogram: count how many returns fall into each bin
    Q = [0] * num_bins       # Raw counts per bin
    total_count = 0          # Total returns that fell into valid bins

    for r in returns:
        # Compute which bin this return belongs to
        bin_index = int((r - left_boundary) / dr)

        # Only count if within valid range [0, num_bins-1]
        if 0 <= bin_index < num_bins:
            Q[bin_index] += 1
            total_count += 1

    if total_count == 0:
        raise ValueError("No returns fell within the histogram range")

    # Normalize: NQ[k] = Q[k] / total_count
    # This gives us the wavefunction (probability distribution)
    NQ = [0.0] * num_bins
    for k in range(num_bins):
        NQ[k] = Q[k] / total_count

    # =========================================================================
    # Step 4: Find ground state (peak of the wavefunction)
    # =========================================================================

    max_q = 0.0
    max_qno = 0
    for k in range(num_bins):
        if NQ[k] > max_q:
            max_q = NQ[k]
            max_qno = k

    # Guard: peak must not be at the edge (need neighbors for FDM)
    if max_qno == 0 or max_qno == num_bins - 1:
        raise ValueError(
            f"Wavefunction peak at edge bin {max_qno}; "
            "cannot compute lambda (need left and right neighbors)"
        )

    # =========================================================================
    # Step 5: Evaluate lambda via Finite Difference Method (FDM)
    # =========================================================================
    # Position values around the peak:
    #   r[maxQno] = left_boundary + maxQno * dr  (left edge of peak bin)
    #   r0 = r[maxQno] - dr/2   (shifted left by half bin — matching Lee's code)
    #   r+1 = r0 + dr
    #   r-1 = r0 - dr
    #
    # Lambda formula (eq. 34 in Lee 2021):
    #   Lup = r-1^2 * NQ[maxQno-1] - r+1^2 * NQ[maxQno+1]
    #   Ldw = r+1^4 * NQ[maxQno+1] - r-1^4 * NQ[maxQno-1]
    #   lambda = |Lup / Ldw|

    r_peak = left_boundary + max_qno * dr  # Left edge of peak bin
    r0 = r_peak - dr / 2.0                 # Shifted center (per Lee's code)
    r_plus1 = r0 + dr
    r_minus1 = r0 - dr

    phi_plus1 = NQ[max_qno + 1]   # Wavefunction at right neighbor
    phi_minus1 = NQ[max_qno - 1]  # Wavefunction at left neighbor

    # Numerator and denominator of lambda formula
    l_up = (r_minus1 ** 2) * phi_minus1 - (r_plus1 ** 2) * phi_plus1
    l_dw = (r_plus1 ** 4) * phi_plus1 - (r_minus1 ** 4) * phi_minus1

    if l_dw == 0.0:
        raise ValueError("Lambda denominator is zero (degenerate wavefunction)")

    lambda_ = abs(l_up / l_dw)

    # =========================================================================
    # Step 6: Compute K0(n) constants
    # =========================================================================

    K = [0.0] * num_levels
    for n in range(num_levels):
        K[n] = compute_k0(n)

    # =========================================================================
    # Step 7: Solve for energy levels using Cardano's method
    # =========================================================================
    # For each n = 0..num_levels-1, solve the depressed cubic:
    #   E^3 + p*E + q = 0
    # where:
    #   p = -(2n+1)^2
    #   q = -lambda * (2n+1)^3 * K0(n)^3
    #
    # Cardano's formula:
    #   D = q^2/4 + p^3/27   (discriminant)
    #   u = cbrt(-q/2 + sqrt(D))
    #   v = cbrt(-q/2 - sqrt(D))
    #   E(n) = u + v
    #
    # For our parameters, D > 0 always (one real root, two complex conjugates).
    # Proof: p < 0, |q| grows as (2n+1)^3 while |p^3/27| grows as (2n+1)^6/27.
    # For n=0: p=-1, q=-lambda*K0^3 ≈ -1.19, D = 1.19^2/4 - 1/27 ≈ 0.317 > 0.
    # For larger n: q^2/4 dominates because K0(n) grows, making D even more positive.

    QFEL = [0.0] * num_levels

    for n in range(num_levels):
        two_n_plus_1 = 2 * n + 1

        p = -(two_n_plus_1 ** 2)
        q = -lambda_ * (two_n_plus_1 ** 3) * (K[n] ** 3)

        # Discriminant
        discriminant = (q * q / 4.0) + (p * p * p / 27.0)

        if discriminant < 0.0:
            # This should not happen for valid lambda > 0, but guard anyway.
            # If it does, the cubic has three real roots and we'd need a
            # trigonometric solution. For now, raise an error.
            raise ValueError(
                f"Negative discriminant at level {n} (D={discriminant:.6e}). "
                f"This indicates an unusual lambda value."
            )

        sqrt_d = math.sqrt(discriminant)

        # Cardano's u and v
        u_arg = -q / 2.0 + sqrt_d
        v_arg = -q / 2.0 - sqrt_d

        u = cbrt(u_arg)
        v = cbrt(v_arg)

        QFEL[n] = u + v

    # =========================================================================
    # Step 8: Compute QPR and NQPR
    # =========================================================================
    # QPR(n) = QFEL(n) / QFEL(0)  — normalized by ground state energy
    # NQPR(n) = 1 + scale_factor * sigma * QPR(n)  — maps to price return scale
    #
    # NQPR(0) ≈ 1.0028 (very close to 1, meaning level 0 is near the open)
    # NQPR(20) ≈ 1.10 for typical forex (meaning level 20 is ~10% away)

    if QFEL[0] == 0.0:
        raise ValueError("Ground state energy QFEL(0) is zero")

    QPR = [0.0] * num_levels
    NQPR = [0.0] * num_levels

    for n in range(num_levels):
        QPR[n] = QFEL[n] / QFEL[0]
        NQPR[n] = 1.0 + scale_factor * sigma * QPR[n]

    # =========================================================================
    # Step 9: Project price levels from reference price
    # =========================================================================
    # QPL_upper[n] = reference_price * NQPR[n]  (levels above reference)
    # QPL_lower[n] = reference_price / NQPR[n]  (levels below reference)
    #
    # Note: The levels are symmetric in LOG space (return space),
    # NOT in absolute price space.

    qpl_upper = [0.0] * num_levels
    qpl_lower = [0.0] * num_levels

    for n in range(num_levels):
        qpl_upper[n] = reference_price * NQPR[n]
        qpl_lower[n] = reference_price / NQPR[n]

    # =========================================================================
    # Return all computed values
    # =========================================================================

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
    # Simulates ~8 years of daily data (2048 bars) for a forex-like instrument
    # starting at 1.0000 with daily volatility ~0.5%

    random.seed(42)

    n_bars = 2048
    daily_volatility = 0.005  # 0.5% daily moves (typical forex)
    start_price = 1.0000

    prices = [start_price]
    for _ in range(n_bars - 1):
        # Log-normal random walk
        daily_return = math.exp(random.gauss(0.0, daily_volatility))
        prices.append(prices[-1] * daily_return)

    # Use last price as reference (e.g. last close or today's open)
    reference_price = prices[-1]

    print(f"Synthetic data: {n_bars} bars")
    print(f"Start price:     {prices[0]:.6f}")
    print(f"End price:       {prices[-1]:.6f}")
    print(f"Reference price: {reference_price:.6f}")
    print()

    # -------------------------------------------------------------------------
    # Compute QPL
    # -------------------------------------------------------------------------

    result = compute_qpl(prices, reference_price)

    print(f"Lambda:      {result['lambda_']:.8f}")
    print(f"Sigma:       {result['sigma']:.8f}")
    print(f"Mu:          {result['mu']:.8f}")
    print()

    # Print energy levels and NQPR
    print(f"{'Level':>5}  {'QFEL':>12}  {'QPR':>10}  {'NQPR':>12}")
    print("-" * 48)
    for n in range(21):
        print(f"{n:>5}  {result['qfel'][n]:>12.6f}  "
              f"{result['qpr'][n]:>10.6f}  {result['nqpr'][n]:>12.8f}")
    print()

    # Print price levels
    print(f"{'Level':>5}  {'QPL_upper':>14}  {'QPL_lower':>14}  {'Band width':>12}")
    print("-" * 52)
    for n in range(21):
        upper = result['qpl_upper'][n]
        lower = result['qpl_lower'][n]
        width = upper - lower
        print(f"{n:>5}  {upper:>14.8f}  {lower:>14.8f}  {width:>12.8f}")
