"""
Polynomial Fit Derivative (PFD) Indicator
==========================================

A unified indicator that fits a polynomial of degree d to the most recent
d+1 price bars and evaluates its k-th derivative at the current bar.

This single implementation covers all of Don Mak's polynomial-based
velocity and acceleration indicators:

    degree=2  →  Parabolic Velocity / Acceleration   (Mak 2003, Ch 6.1–6.2)
    degree=3  →  Cubic Velocity / Acceleration        (Mak 2003, Ch 6.3)
    degree=4  →  Quartic Velocity / Acceleration      (Mak 2006, Ch 8.4)
    degree=5  →  Quintic Velocity / Acceleration      (Mak 2006, Ch 8.5)
    degree=6  →  Sextic Velocity / Acceleration       (Mak 2006, Ch 8.6)

The indicator output is a simple FIR (Finite Impulse Response) filter —
a dot product of fixed coefficients with the last d+1 smoothed prices.

Coefficients are derived from Lagrange interpolation: fit a unique
polynomial through d+1 equally-spaced points, then evaluate the k-th
derivative at the endpoint. This is equivalent to the backward finite
difference formula for the k-th derivative.

Pre-smoothing with an Exponential Moving Average (EMA) is recommended
to suppress noise before the derivative filter amplifies it.

This implementation uses only the Python standard library (no numpy,
no pandas) to facilitate porting to Rust, Zig, Go, etc.
"""

import math


# ---------------------------------------------------------------------------
# Coefficient computation via Lagrange interpolation
# ---------------------------------------------------------------------------

def _compute_coefficients(degree, order):
    """
    Compute the FIR filter coefficients for the k-th derivative of a
    polynomial of given degree, evaluated at the most recent point.

    This computes the backward finite difference coefficients using the
    Lagrange interpolation basis. The data points are at positions
    t = 0, -1, -2, ..., -d (where 0 is the current bar).

    Parameters
    ----------
    degree : int
        Polynomial degree d. Uses d+1 data points.
    order : int
        Derivative order k. Must be 1 (velocity) or 2 (acceleration).
        In principle any k <= d works, but only 1 and 2 are useful
        for trading.

    Returns
    -------
    list of float
        Coefficients [c_0, c_1, ..., c_d] such that:
            y(n) = c_0 * x(n) + c_1 * x(n-1) + ... + c_d * x(n-d)
        gives the k-th derivative of the polynomial fit at bar n.

    Notes
    -----
    The Lagrange basis polynomial L_i(t) for data point at position -i is:

        L_i(t) = product_{j=0..d, j!=i} (t + j) / (j - i)

    The coefficient c_i = L_i^(k)(0), the k-th derivative of L_i at t=0.

    For k=1 (first derivative):
        L_i'(0) = [1 / denom_i] * sum_{ell != i} product_{m != i, m != ell} m

    For k=2 (second derivative):
        L_i''(0) = [1 / denom_i] * sum_{ell < r, ell,r != i}
                   2 * product_{m != i, m != ell, m != r} m

    where denom_i = product_{j != i} (-i + j) = product_{j != i} (j - i).
    """
    if order < 1:
        raise ValueError("order must be >= 1")
    if degree < order:
        raise ValueError(f"degree ({degree}) must be >= order ({order})")

    n_points = degree + 1  # number of data points

    # The data point positions are 0, -1, -2, ..., -d
    # but for the Lagrange formula we work with the "other indices"
    # excluding the current point i.

    coefficients = []

    for i in range(n_points):
        # ---------------------------------------------------------------
        # Compute the denominator: product_{j=0..d, j!=i} (j - i)
        # This is the denominator of the Lagrange basis L_i(t).
        # ---------------------------------------------------------------
        denom = 1.0
        for j in range(n_points):
            if j != i:
                denom *= float(j - i)

        # ---------------------------------------------------------------
        # Compute the numerator: the k-th derivative of the numerator
        # polynomial prod_{j!=i}(t + j) evaluated at t=0.
        #
        # The numerator polynomial is:
        #   N_i(t) = prod_{j=0..d, j!=i} (t + j)
        #
        # Its first derivative at t=0 is:
        #   N_i'(0) = sum_{ell!=i} prod_{m!=i, m!=ell} (0 + m)
        #           = sum_{ell!=i} prod_{m!=i, m!=ell} m
        #
        # Its second derivative at t=0 is:
        #   N_i''(0) = 2 * sum_{ell<r, ell,r!=i} prod_{m!=i, m!=ell, m!=r} m
        # ---------------------------------------------------------------

        # Build the list of "other" indices (all j != i)
        others = [j for j in range(n_points) if j != i]

        if order == 1:
            # First derivative: sum over each "removed" index ell
            numerator = 0.0
            for ell_idx in range(len(others)):
                # Product of all others[m] except others[ell_idx]
                term = 1.0
                for m_idx in range(len(others)):
                    if m_idx != ell_idx:
                        term *= float(others[m_idx])
                numerator += term

        elif order == 2:
            # Second derivative: sum over all pairs (ell, r) with ell < r
            numerator = 0.0
            for ell_idx in range(len(others)):
                for r_idx in range(ell_idx + 1, len(others)):
                    # Product of all others[m] except others[ell_idx]
                    # and others[r_idx], times 2
                    term = 2.0
                    for m_idx in range(len(others)):
                        if m_idx != ell_idx and m_idx != r_idx:
                            term *= float(others[m_idx])
                    numerator += term

        else:
            # General k-th derivative: sum over all k-element subsets
            # of "others", then product of the remaining elements, times k!.
            #
            # This is the generalized Leibniz formula for the k-th derivative
            # of a product of linear factors.
            #
            # N_i^(k)(0) = k! * sum_{S subset of others, |S|=k}
            #              prod_{m in others \ S} m
            #
            # We implement this with a recursive combination generator.
            numerator = 0.0
            factorial_k = 1
            for f in range(1, order + 1):
                factorial_k *= f

            # Generate all k-element subsets of indices into 'others'
            def _combinations(pool_size, choose_k):
                """Yield all choose_k-element index tuples from range(pool_size)."""
                if choose_k == 0:
                    yield ()
                    return
                for start in range(pool_size - choose_k + 1):
                    for rest in _combinations(pool_size - start - 1, choose_k - 1):
                        yield (start,) + tuple(r + start + 1 for r in rest)

            for subset in _combinations(len(others), order):
                # subset contains indices into 'others' that are "removed"
                removed = set(subset)
                term = float(factorial_k)
                for m_idx in range(len(others)):
                    if m_idx not in removed:
                        term *= float(others[m_idx])
                numerator += term

        coefficients.append(numerator / denom)

    return coefficients


# ---------------------------------------------------------------------------
# Streaming PFD indicator class
# ---------------------------------------------------------------------------

class PolynomialFitDerivative:
    """
    Streaming Polynomial Fit Derivative (PFD) indicator.

    Processes one price bar at a time via the update() method.
    Internally maintains an EMA smoother and a ring buffer of smoothed
    prices. On each update, computes the dot product of the last (degree+1)
    smoothed prices with the precomputed FIR coefficients.

    Parameters
    ----------
    degree : int, optional
        Polynomial degree (default: 3, i.e. cubic). Must be >= 2.
        The number of data points used is degree + 1.
    order : int, optional
        Derivative order (default: 1 = velocity). Must be >= 1 and < degree.
        1 = first derivative (slope / velocity).
        2 = second derivative (curvature / acceleration).
        3 = third derivative (jerk — rate of change of acceleration).
        Higher orders are supported but amplify noise significantly.
    smoothing : int, optional
        EMA pre-smoothing length (default: 6). Set to 0 for no smoothing.
        Mak recommends 3 (less lag, more noise) or 6 (more lag, less noise).

    Attributes
    ----------
    primed : bool
        True once enough bars have been received to compute the output.
        Requires at least (degree + 1) smoothed prices in the buffer,
        plus (smoothing) bars for the EMA to stabilize (though EMA output
        starts from bar 1).
    value : float
        The most recent indicator output. NaN if not primed.
    coefficients : list of float
        The FIR filter coefficients [c_0, c_1, ..., c_d].
    """

    def __init__(self, degree=3, order=1, smoothing=6):
        # --- Validate parameters ---
        if degree < 2:
            raise ValueError("degree must be >= 2")
        if order < 1 or order > degree:
            raise ValueError(
                f"order must be >= 1 and <= degree ({degree}); got {order}"
            )
        if smoothing < 0:
            raise ValueError("smoothing must be >= 0")

        self.degree = degree
        self.order = order
        self.smoothing = smoothing

        # Number of data points needed for the polynomial fit
        self._n_points = degree + 1

        # --- Compute FIR coefficients at init time ---
        # These are fixed for a given (degree, order) and never change.
        self.coefficients = _compute_coefficients(degree, order)

        # --- EMA state ---
        # alpha = 2 / (L + 1) where L is the EMA period.
        # If smoothing == 0, we skip EMA entirely.
        if smoothing > 0:
            self._ema_alpha = 2.0 / (smoothing + 1.0)
        else:
            self._ema_alpha = 0.0  # not used
        self._ema_value = 0.0
        self._ema_initialized = False

        # --- Ring buffer for smoothed prices ---
        # We only need the last (degree + 1) values, so a fixed-size
        # ring buffer is efficient. _buf[_buf_pos] is the oldest value.
        self._buf = [0.0] * self._n_points
        self._buf_pos = 0      # write position (next slot to overwrite)
        self._buf_count = 0    # how many values have been written

        # --- Output state ---
        self.value = math.nan
        self.primed = False

    def update(self, price):
        """
        Process one new price bar and update the indicator.

        Parameters
        ----------
        price : float
            The closing price (or any single price series value) for
            the current bar.

        Returns
        -------
        dict
            'value': float — the indicator output (NaN if not primed)
            'primed': bool — whether the indicator has enough data
        """
        # --- Step 1: Apply EMA smoothing (if enabled) ---
        if self.smoothing > 0:
            if not self._ema_initialized:
                # First bar: initialize EMA to the first price
                self._ema_value = price
                self._ema_initialized = True
            else:
                # Standard EMA recurrence:
                # EMA(n) = alpha * price(n) + (1 - alpha) * EMA(n-1)
                self._ema_value = (self._ema_alpha * price
                                   + (1.0 - self._ema_alpha) * self._ema_value)
            smoothed = self._ema_value
        else:
            # No smoothing: use raw price
            smoothed = price

        # --- Step 2: Add smoothed price to ring buffer ---
        self._buf[self._buf_pos] = smoothed
        self._buf_pos = (self._buf_pos + 1) % self._n_points
        self._buf_count += 1

        # --- Step 3: Check if we have enough data ---
        if self._buf_count < self._n_points:
            # Not enough smoothed prices yet — can't compute the derivative
            self.value = math.nan
            self.primed = False
            return {'value': self.value, 'primed': self.primed}

        # --- Step 4: Compute the FIR filter output ---
        # The coefficients are [c_0, c_1, ..., c_d] where:
        #   c_0 multiplies x(n)     (most recent smoothed price)
        #   c_1 multiplies x(n-1)   (one bar ago)
        #   c_d multiplies x(n-d)   (oldest in buffer)
        #
        # The ring buffer's most recent value is at position
        # (_buf_pos - 1) mod n_points, the one before that at
        # (_buf_pos - 2) mod n_points, etc.

        result = 0.0
        for j in range(self._n_points):
            # Index into ring buffer: most recent is j=0, oldest is j=d
            buf_idx = (self._buf_pos - 1 - j) % self._n_points
            result += self.coefficients[j] * self._buf[buf_idx]

        self.value = result
        self.primed = True
        return {'value': self.value, 'primed': self.primed}


# ---------------------------------------------------------------------------
# Batch convenience function
# ---------------------------------------------------------------------------

def polynomial_fit_derivative(prices, degree=3, order=1, smoothing=6):
    """
    Compute the Polynomial Fit Derivative over a full price series (batch).

    This is a convenience wrapper around the streaming class. It processes
    the entire price array and returns an array of output values.

    Parameters
    ----------
    prices : list of float
        Input price series (e.g., closing prices).
    degree : int, optional
        Polynomial degree (default: 3). Must be >= 2.
    order : int, optional
        Derivative order (default: 1). Must be >= 1 and < degree.
    smoothing : int, optional
        EMA pre-smoothing length (default: 6). 0 = no smoothing.

    Returns
    -------
    list of float
        Output values, one per input bar. NaN for bars where the
        indicator is not yet primed.
    """
    indicator = PolynomialFitDerivative(degree=degree, order=order,
                                        smoothing=smoothing)
    output = []
    for price in prices:
        result = indicator.update(price)
        output.append(result['value'])
    return output


# ---------------------------------------------------------------------------
# Verification: check computed coefficients against known book values
# ---------------------------------------------------------------------------

def _verify_coefficients():
    """
    Verify that the Lagrange-derived coefficients match the exact fractions
    from Mak's books.

    Returns True if all match within floating-point tolerance.
    """
    # Known exact coefficients as (numerator, denominator) pairs.
    # velocity = order 1, acceleration = order 2.
    known = {
        # Parabolic (degree 2)
        (2, 1): [(3, 2), (-2, 1), (1, 2)],
        (2, 2): [(1, 1), (-2, 1), (1, 1)],
        # Cubic (degree 3)
        (3, 1): [(11, 6), (-3, 1), (3, 2), (-1, 3)],
        (3, 2): [(2, 1), (-5, 1), (4, 1), (-1, 1)],
        # Quartic (degree 4)
        (4, 1): [(25, 12), (-4, 1), (3, 1), (-4, 3), (1, 4)],
        (4, 2): [(35, 12), (-26, 3), (19, 2), (-14, 3), (11, 12)],
        # Quintic (degree 5)
        (5, 1): [(137, 60), (-5, 1), (5, 1), (-10, 3), (5, 4), (-1, 5)],
        (5, 2): [(15, 4), (-77, 6), (107, 6), (-13, 1), (61, 12), (-5, 6)],
        # Sextic (degree 6)
        (6, 1): [(49, 20), (-6, 1), (15, 2), (-20, 3), (15, 4), (-6, 5),
                  (1, 6)],
        (6, 2): [(203, 45), (-87, 5), (117, 4), (-254, 9), (33, 2),
                  (-27, 5), (137, 180)],
    }

    all_ok = True
    for (deg, ord_), fracs in known.items():
        computed = _compute_coefficients(deg, ord_)
        expected = [n / d for n, d in fracs]
        for j, (c, e) in enumerate(zip(computed, expected)):
            if abs(c - e) > 1e-12:
                print(f"  MISMATCH degree={deg} order={ord_} coeff[{j}]: "
                      f"computed={c:.15f} expected={e:.15f}")
                all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # -----------------------------------------------------------------------
    # 1. Verify coefficients against book values
    # -----------------------------------------------------------------------
    print("Verifying coefficients against known book values...")
    if _verify_coefficients():
        print("  All coefficients match.\n")
    else:
        print("  WARNING: Some coefficients do not match!\n")

    # -----------------------------------------------------------------------
    # 2. Print coefficient tables for all legacy indicators
    # -----------------------------------------------------------------------
    legacy = [
        ("PV",  "Parabolic Velocity",     2, 1),
        ("PA",  "Parabolic Acceleration",  2, 2),
        ("CV",  "Cubic Velocity",          3, 1),
        ("CA",  "Cubic Acceleration",      3, 2),
        ("QV",  "Quartic Velocity",        4, 1),
        ("QA",  "Quartic Acceleration",    4, 2),
        ("QNV", "Quintic Velocity",        5, 1),
        ("QNA", "Quintic Acceleration",    5, 2),
        ("SXV", "Sextic Velocity",         6, 1),
        ("SXA", "Sextic Acceleration",     6, 2),
    ]

    print("Coefficient table:")
    for abbrev, name, deg, ord_ in legacy:
        coeffs = _compute_coefficients(deg, ord_)
        coeffs_str = ", ".join(f"{c:+.6f}" for c in coeffs)
        print(f"  {abbrev:3s} ({name:25s}): [{coeffs_str}]")
    print()

    # -----------------------------------------------------------------------
    # 3. Generate a synthetic sine wave and compute all variants
    # -----------------------------------------------------------------------
    # A sine wave with period 32 bars (omega = 2*pi/32 = pi/16)
    # plus a linear uptrend to make it look like a real price series.
    num_bars = 200
    period = 32
    omega = 2.0 * math.pi / period
    amplitude = 10.0
    base_price = 100.0
    trend = 0.05  # price per bar upward drift

    prices = []
    for i in range(num_bars):
        price = base_price + trend * i + amplitude * math.sin(omega * i)
        prices.append(price)

    print(f"Synthetic data: {num_bars} bars, base={base_price}, "
          f"trend={trend}/bar, amplitude={amplitude}, period={period}")
    print()

    # -----------------------------------------------------------------------
    # 4. Run the streaming indicator for Cubic Velocity (default params)
    # -----------------------------------------------------------------------
    print("=== Cubic Velocity (degree=3, order=1, smoothing=6) ===")
    pfd = PolynomialFitDerivative(degree=3, order=1, smoothing=6)
    for i, price in enumerate(prices):
        result = pfd.update(price)
        if i < 10 or i >= num_bars - 5:
            status = "primed" if result['primed'] else "not primed"
            val = f"{result['value']:+.6f}" if result['primed'] else "NaN"
            print(f"  bar {i:3d}: price={price:8.3f}  "
                  f"CV={val}  ({status})")
        elif i == 10:
            print("  ...")
    print()

    # -----------------------------------------------------------------------
    # 5. Compare all velocity variants on the same data (batch mode)
    # -----------------------------------------------------------------------
    print("=== Velocity indicators at bar 100 (smoothing=6) ===")
    bar = 100
    for abbrev, name, deg, ord_ in legacy:
        if ord_ != 1:
            continue  # skip acceleration for this comparison
        output = polynomial_fit_derivative(prices, degree=deg, order=1,
                                           smoothing=6)
        val = output[bar]
        val_str = f"{val:+.6f}" if not math.isnan(val) else "NaN"
        print(f"  {abbrev:3s} ({name:25s}): {val_str}")

    print()
    print("=== Acceleration indicators at bar 100 (smoothing=6) ===")
    for abbrev, name, deg, ord_ in legacy:
        if ord_ != 2:
            continue
        output = polynomial_fit_derivative(prices, degree=deg, order=2,
                                           smoothing=6)
        val = output[bar]
        val_str = f"{val:+.6f}" if not math.isnan(val) else "NaN"
        print(f"  {abbrev:3s} ({name:25s}): {val_str}")

    # -----------------------------------------------------------------------
    # 6. Demonstrate zero-crossing detection (simple sign change)
    # -----------------------------------------------------------------------
    print()
    print("=== Cubic Velocity zero crossings (potential turning points) ===")
    cv_output = polynomial_fit_derivative(prices, degree=3, order=1,
                                          smoothing=6)
    crossings = 0
    for i in range(1, len(cv_output)):
        if math.isnan(cv_output[i]) or math.isnan(cv_output[i - 1]):
            continue
        if cv_output[i - 1] * cv_output[i] < 0:
            direction = "UP->DOWN" if cv_output[i - 1] > 0 else "DOWN->UP"
            print(f"  bar {i:3d}: price={prices[i]:8.3f}  {direction}")
            crossings += 1
    print(f"  Total crossings: {crossings}")
