"""
Polynomial Forecast Indicator
==============================

One-step-ahead price forecast using Taylor series expansion based on
polynomial fit derivatives (PFD).

    order=1:  forecast = price + velocity                    (F1V)
    order=2:  forecast = price + velocity + 0.5*acceleration (F1VA)

Where velocity = PFD(degree, derivative_order=1) and acceleration =
PFD(degree, derivative_order=2), computed from a local polynomial fit
of the given degree to the most recent (degree+1) prices.

Source: Don K. Mak, The Science of Financial Market Trading (2003), Ch 10.2

This implementation uses only the Python standard library.
"""

import math


# ---------------------------------------------------------------------------
# Coefficient computation (embedded from PFD)
# ---------------------------------------------------------------------------

def _compute_coefficients(degree, order):
    """
    Compute FIR coefficients for the k-th derivative of a degree-d polynomial
    fit evaluated at the most recent point. Uses Lagrange interpolation basis.
    """
    n_points = degree + 1
    coefficients = []

    for i in range(n_points):
        denom = 1.0
        for j in range(n_points):
            if j != i:
                denom *= float(j - i)

        others = [j for j in range(n_points) if j != i]

        if order == 1:
            numerator = 0.0
            for ell_idx in range(len(others)):
                term = 1.0
                for m_idx in range(len(others)):
                    if m_idx != ell_idx:
                        term *= float(others[m_idx])
                numerator += term
        elif order == 2:
            numerator = 0.0
            for ell_idx in range(len(others)):
                for r_idx in range(ell_idx + 1, len(others)):
                    term = 2.0
                    for m_idx in range(len(others)):
                        if m_idx != ell_idx and m_idx != r_idx:
                            term *= float(others[m_idx])
                    numerator += term
        else:
            raise ValueError("order must be 1 or 2")

        coefficients.append(numerator / denom)

    return coefficients


# ---------------------------------------------------------------------------
# Streaming Polynomial Forecast class
# ---------------------------------------------------------------------------

class PolynomialForecast:
    """
    Streaming 1-bar-ahead price forecast using Taylor expansion.

    Parameters
    ----------
    degree : int
        Polynomial degree (2-6, default 3 = cubic).
    order : int
        Taylor expansion order: 1 = velocity only (F1V), 2 = velocity +
        acceleration (F1VA). Default: 1.
    smoothing : int
        EMA pre-smoothing period (0 = none). Default: 0.
    """

    def __init__(self, degree=3, order=1, smoothing=0):
        if degree < 2:
            raise ValueError("degree must be >= 2")
        if order < 1 or order > 2:
            raise ValueError("order must be 1 or 2")
        if smoothing < 0:
            raise ValueError("smoothing must be >= 0")

        self.degree = degree
        self.order = order
        self.smoothing = smoothing

        self._n_points = degree + 1

        # Precompute FIR coefficients for velocity (always needed)
        self._coeff_vel = _compute_coefficients(degree, 1)
        # Precompute acceleration coefficients only if order=2
        self._coeff_acc = _compute_coefficients(degree, 2) if order == 2 else None

        # EMA state
        if smoothing > 0:
            self._ema_alpha = 2.0 / (smoothing + 1.0)
        else:
            self._ema_alpha = 0.0
        self._ema_value = 0.0
        self._ema_initialized = False

        # Ring buffer for smoothed prices
        self._buf = [0.0] * self._n_points
        self._buf_pos = 0
        self._buf_count = 0

        # Output
        self.value = math.nan
        self.primed = False

    def update(self, price):
        """Process one bar and return {'value': float}."""
        # EMA smoothing
        if self.smoothing > 0:
            if not self._ema_initialized:
                self._ema_value = price
                self._ema_initialized = True
            else:
                self._ema_value = (self._ema_alpha * price
                                   + (1.0 - self._ema_alpha) * self._ema_value)
            smoothed = self._ema_value
        else:
            smoothed = price

        # Write to ring buffer
        self._buf[self._buf_pos] = smoothed
        self._buf_pos = (self._buf_pos + 1) % self._n_points
        self._buf_count += 1

        # Check if primed
        if self._buf_count < self._n_points:
            self.value = math.nan
            self.primed = False
            return {'value': math.nan}

        self.primed = True

        # Read buffer: most recent first
        # _buf_pos points to the oldest entry (next to overwrite)
        # So most recent is at _buf_pos - 1 (mod n_points)
        values = [0.0] * self._n_points
        for k in range(self._n_points):
            idx = (self._buf_pos - 1 - k) % self._n_points
            values[k] = self._buf[idx]

        # Compute velocity (dot product)
        velocity = 0.0
        for k in range(self._n_points):
            velocity += self._coeff_vel[k] * values[k]

        # Compute forecast
        # Use the current smoothed price as base
        forecast = smoothed + velocity

        if self.order == 2 and self._coeff_acc is not None:
            acceleration = 0.0
            for k in range(self._n_points):
                acceleration += self._coeff_acc[k] * values[k]
            forecast += 0.5 * acceleration

        self.value = forecast
        return {'value': forecast}
