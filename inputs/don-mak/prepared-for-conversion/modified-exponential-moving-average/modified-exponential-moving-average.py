"""
Modified Exponential Moving Average (MEMA / MEMA-D)
====================================================

A reduced-lag EMA that adds the EMA's own polynomial velocity back to its
output, compensating for smoothing delay.

    MEMA(n)   = EMA(n) + PFD(EMA, degree, order=1, stride=1)
    MEMA-D(n) = EMA(n) + PFD(EMA, degree, order=1, stride=D)

Source: Don K. Mak, Mathematical Techniques in Financial Market Trading
(2006), Chapter 4.2.

This implementation uses only the Python standard library.
"""

import math


# ---------------------------------------------------------------------------
# PFD Coefficient computation (Lagrange basis derivative, order=1 only)
# ---------------------------------------------------------------------------

def _compute_velocity_coefficients(degree):
    """
    Compute FIR coefficients for the first derivative of a degree-d
    polynomial fit evaluated at the most recent point.
    """
    n_points = degree + 1
    coefficients = []

    for i in range(n_points):
        # Denominator: product_{j!=i} (j - i)
        denom = 1.0
        for j in range(n_points):
            if j != i:
                denom *= float(j - i)

        # Others: all indices except i
        others = [j for j in range(n_points) if j != i]

        # First derivative of numerator at t=0
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
# Streaming Modified EMA class
# ---------------------------------------------------------------------------

class ModifiedExponentialMovingAverage:
    """
    Streaming Modified EMA (MEMA / MEMA-D) indicator.

    Parameters
    ----------
    period : int
        EMA smoothing period (default: 6).
    degree : int
        Polynomial degree for velocity correction (2-6, default: 3).
    skip : int
        Stride for PFD sampling (1 = MEMA, >1 = MEMA-D, default: 1).
    """

    def __init__(self, period=6, degree=3, skip=1):
        if period < 2:
            raise ValueError("period must be >= 2")
        if degree < 2:
            raise ValueError("degree must be >= 2")
        if skip < 1:
            raise ValueError("skip must be >= 1")

        self.period = period
        self.degree = degree
        self.skip = skip

        # EMA alpha
        self._ema_alpha = 2.0 / (period + 1.0)
        self._ema_value = 0.0
        self._ema_initialized = False

        # Precompute velocity FIR coefficients
        self._coeff = _compute_velocity_coefficients(degree)

        # Ring buffer for EMA history
        # Need degree*skip + 1 values to compute PFD with stride
        self._buf_size = degree * skip + 1
        self._buf = [0.0] * self._buf_size
        self._buf_pos = 0
        self._buf_count = 0

        # Output
        self.value = math.nan
        self.primed = False

    def update(self, price):
        """Process one bar and return {'value': float}."""
        # EMA
        if not self._ema_initialized:
            self._ema_value = price
            self._ema_initialized = True
        else:
            self._ema_value = (self._ema_alpha * price
                               + (1.0 - self._ema_alpha) * self._ema_value)

        # Store EMA value in ring buffer
        self._buf[self._buf_pos] = self._ema_value
        self._buf_pos = (self._buf_pos + 1) % self._buf_size
        self._buf_count += 1

        # Check if primed (need degree*skip + 1 values)
        if self._buf_count < self._buf_size:
            self.value = math.nan
            self.primed = False
            return {'value': math.nan}

        self.primed = True

        # Read values at stride positions: most recent, then skip back
        # Most recent is at _buf_pos - 1 (mod buf_size)
        n_points = self.degree + 1
        values = [0.0] * n_points
        for k in range(n_points):
            offset = k * self.skip
            idx = (self._buf_pos - 1 - offset) % self._buf_size
            values[k] = self._buf[idx]

        # Compute velocity (dot product of coefficients with strided values)
        velocity = 0.0
        for k in range(n_points):
            velocity += self._coeff[k] * values[k]

        # Output: EMA + velocity correction
        self.value = self._ema_value + velocity
        return {'value': self.value}
