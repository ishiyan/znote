"""
Velocity-Corrected Exponential Moving Average (VCEMA)
=====================================================

A reduced-lag EMA that pre-corrects price by adding its polynomial
velocity before smoothing:

    corrected = price + PFD(price, degree, order=1)
    output    = EMA(corrected, period)

Source: Don K. Mak, Mathematical Techniques in Financial Market Trading
(2006), Chapter 4.1. Called "Zero-Lag EMA" in the book.

This implementation uses only the Python standard library.
"""

import math


# ---------------------------------------------------------------------------
# PFD Coefficient computation (order=1 only)
# ---------------------------------------------------------------------------

def _compute_velocity_coefficients(degree):
    """
    Compute FIR coefficients for the first derivative of a degree-d
    polynomial fit evaluated at the most recent point.
    """
    n_points = degree + 1
    coefficients = []

    for i in range(n_points):
        denom = 1.0
        for j in range(n_points):
            if j != i:
                denom *= float(j - i)

        others = [j for j in range(n_points) if j != i]

        numerator = 0.0
        for ell_idx in range(len(others)):
            term = 1.0
            for m_idx in range(len(others)):
                if m_idx != ell_idx:
                    term *= float(others[m_idx])
            numerator += term

        coefficients.append(numerator / denom)

    return coefficients


# ---------------------------------------------------------------------------
# Streaming VCEMA class
# ---------------------------------------------------------------------------

class VelocityCorrectedExponentialMovingAverage:
    """
    Streaming Velocity-Corrected EMA indicator.

    Parameters
    ----------
    period : int
        EMA smoothing period (default: 6).
    degree : int
        Polynomial degree for velocity estimation (2-6, default: 3).
    """

    def __init__(self, period=6, degree=3):
        if period < 2:
            raise ValueError("period must be >= 2")
        if degree < 2:
            raise ValueError("degree must be >= 2")

        self.period = period
        self.degree = degree

        # EMA alpha
        self._ema_alpha = 2.0 / (period + 1.0)
        self._ema_value = 0.0
        self._ema_initialized = False

        # PFD velocity coefficients
        self._coeff = _compute_velocity_coefficients(degree)
        self._n_points = degree + 1

        # Ring buffer for raw prices (for PFD computation)
        self._buf = [0.0] * self._n_points
        self._buf_pos = 0
        self._buf_count = 0

        # Output
        self.value = math.nan
        self.primed = False

    def update(self, price):
        """Process one bar and return {'value': float}."""
        # Store raw price in ring buffer
        self._buf[self._buf_pos] = price
        self._buf_pos = (self._buf_pos + 1) % self._n_points
        self._buf_count += 1

        # Check if PFD can be computed
        if self._buf_count < self._n_points:
            self.value = math.nan
            self.primed = False
            return {'value': math.nan}

        self.primed = True

        # Compute velocity from raw prices
        values = [0.0] * self._n_points
        for k in range(self._n_points):
            idx = (self._buf_pos - 1 - k) % self._n_points
            values[k] = self._buf[idx]

        velocity = 0.0
        for k in range(self._n_points):
            velocity += self._coeff[k] * values[k]

        # Corrected price = price + velocity
        corrected = price + velocity

        # Apply EMA to corrected price
        if not self._ema_initialized:
            self._ema_value = corrected
            self._ema_initialized = True
        else:
            self._ema_value = (self._ema_alpha * corrected
                               + (1.0 - self._ema_alpha) * self._ema_value)

        self.value = self._ema_value
        return {'value': self.value}
