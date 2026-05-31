"""
Adaptive Exponential Moving Average (AEMA)

An EMA with time-varying smoothing factor alpha that adapts based on the
instantaneous frequency of the price data. Uses an embedded ISWP
(Instantaneous Sine Wave Period) estimator to detect the dominant frequency.

Reference:
    Mak, D.K. (2006). Mathematical Techniques in Financial Market Trading.
    World Scientific. Chapter 3.6.

Parameters:
    alpha_max (float): Smoothing factor for trending data (default 0.5).
    alpha_min (float): Smoothing factor for noisy data (default 0.05).
    omega_0 (float): Crossover frequency in radians/bar (default 1.0).
    smoothing (int): ISWP internal smoothing parameter (default 3).

Output:
    {"value": float, "omega": float, "alpha": float}
    value = adaptively smoothed price (never NaN)
    omega = instantaneous frequency estimate (may be NaN)
    alpha = smoothing factor used for this bar

Usage:
    indicator = AdaptiveExponentialMovingAverage()
    for price in prices:
        result = indicator.update(price)
        print(result["value"])
"""

import math
import os
import sys
import importlib.util

# Load the ISWP module from the same repository structure.
# When porting to other languages, the ISWP logic must be embedded or imported.
_ISWP_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'prepared-for-conversion', 'instantaneous-sine-wave-period',
    'instantaneous-sine-wave-period.py'
)
if not os.path.exists(_ISWP_PATH):
    # Try relative to current file's directory structure
    _ISWP_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'instantaneous-sine-wave-period',
        'instantaneous-sine-wave-period.py'
    )

_iswp_spec = importlib.util.spec_from_file_location("iswp_module", _ISWP_PATH)
_iswp_mod = importlib.util.module_from_spec(_iswp_spec)
_iswp_spec.loader.exec_module(_iswp_mod)
InstantaneousSineWavePeriod = _iswp_mod.InstantaneousSineWavePeriod


class AdaptiveExponentialMovingAverage:
    """
    Adaptive EMA with frequency-dependent smoothing factor.

    The smoothing factor alpha varies between alpha_max (for trending/low-freq
    data) and alpha_min (for noisy/high-freq data) based on the instantaneous
    frequency estimated by an embedded ISWP indicator.

    Alpha mapping (hyperbolic in omega):
        omega <= omega_0:          alpha = alpha_max
        omega_0 < omega < pi:      alpha = a/omega + b
        omega >= pi or NaN:        alpha = alpha_min

    where a and b are computed from boundary conditions.

    Attributes:
        alpha_max: Maximum smoothing factor (for low frequency).
        alpha_min: Minimum smoothing factor (for high frequency).
        omega_0: Crossover frequency (radians/bar).
        smoothing: ISWP smoothing parameter.
    """

    def __init__(self, alpha_max=0.5, alpha_min=0.05, omega_0=1.0, smoothing=3):
        """
        Initialize the Adaptive EMA.

        Args:
            alpha_max (float): Smoothing factor for trending data. Range (0, 1].
            alpha_min (float): Smoothing factor for noisy data. Range (0, alpha_max).
            omega_0 (float): Crossover frequency in radians/bar. Range (0, pi).
            smoothing (int): ISWP smoothing parameter. Range [0, inf).

        Raises:
            ValueError: If parameters are out of valid range.
        """
        if not (0.0 < alpha_min < alpha_max <= 1.0):
            raise ValueError(
                f"Need 0 < alpha_min < alpha_max <= 1, got "
                f"alpha_min={alpha_min}, alpha_max={alpha_max}")
        if not (0.0 < omega_0 < math.pi):
            raise ValueError(
                f"Need 0 < omega_0 < pi, got omega_0={omega_0}")
        if smoothing < 0:
            raise ValueError(f"smoothing must be >= 0, got {smoothing}")

        self.alpha_max = alpha_max
        self.alpha_min = alpha_min
        self.omega_0 = omega_0
        self.smoothing = smoothing

        # Compute constants for hyperbolic interpolation:
        #   a / omega_0 + b = alpha_max
        #   a / pi + b = alpha_min
        # Solving:
        #   a = (alpha_max - alpha_min) * omega_0 * pi / (pi - omega_0)
        #   b = alpha_min - a / pi
        self._a = (alpha_max - alpha_min) * omega_0 * math.pi / (math.pi - omega_0)
        self._b = alpha_min - self._a / math.pi

        # Embedded ISWP for frequency estimation
        self._iswp = InstantaneousSineWavePeriod(smoothing=smoothing)

        # EMA state
        self._ema_value = None  # Will be initialized on first price
        self._initialized = False

    def _compute_alpha(self, omega):
        """
        Compute the smoothing factor alpha from the instantaneous frequency.

        Args:
            omega (float): Instantaneous frequency in radians/bar. May be NaN.

        Returns:
            float: Smoothing factor in [alpha_min, alpha_max].
        """
        # If omega is NaN (ISWP couldn't estimate), use maximum smoothing.
        # Rationale: unknown frequency likely means non-periodic/noisy data,
        # so apply conservative (heavy) smoothing.
        if math.isnan(omega):
            return self.alpha_min

        # Clamp: low frequency → alpha_max
        if omega <= self.omega_0:
            return self.alpha_max

        # Clamp: very high frequency → alpha_min
        if omega >= math.pi:
            return self.alpha_min

        # Hyperbolic interpolation: alpha = a/omega + b
        alpha = self._a / omega + self._b

        # Safety clamp (shouldn't be needed if parameters are valid,
        # but protects against floating-point edge cases)
        if alpha > self.alpha_max:
            return self.alpha_max
        if alpha < self.alpha_min:
            return self.alpha_min

        return alpha

    def update(self, price):
        """
        Process one new price bar.

        Args:
            price (float): Input price (raw, not pre-smoothed).

        Returns:
            dict: {"value": float, "omega": float, "alpha": float}
                  value is always valid (never NaN).
                  omega may be NaN if ISWP can't estimate frequency.
                  alpha is the smoothing factor used for this bar.
        """
        # Step 1: Get frequency estimate from embedded ISWP
        iswp_result = self._iswp.update(price)
        omega = iswp_result["omega"]  # May be NaN

        # Step 2: Compute adaptive alpha
        alpha = self._compute_alpha(omega)

        # Step 3: Apply EMA recursion with adaptive alpha
        if not self._initialized:
            # Initialize EMA to first price (no smoothing on first bar)
            self._ema_value = price
            self._initialized = True
        else:
            # Standard EMA: y = alpha * x + (1 - alpha) * y_prev
            self._ema_value = alpha * price + (1.0 - alpha) * self._ema_value

        return {
            "value": self._ema_value,
            "omega": omega,
            "alpha": alpha,
        }


# =============================================================================
# Example usage
# =============================================================================

if __name__ == "__main__":
    print("=== Adaptive Exponential Moving Average ===\n")

    # Test with a synthetic signal: trending then choppy
    N = 100

    # First 50 bars: clean trend (low frequency)
    # Last 50 bars: choppy noise
    import random
    random.seed(42)

    prices = []
    for t in range(50):
        # Smooth uptrend
        prices.append(100.0 + t * 0.5 + math.sin(0.2 * t) * 2)
    for t in range(50):
        # Choppy noise around 125
        prices.append(125.0 + random.gauss(0, 3))

    indicator = AdaptiveExponentialMovingAverage(
        alpha_max=0.5, alpha_min=0.05, omega_0=1.0, smoothing=3)

    print(f"{'Bar':>3s} {'Price':>8s} {'AEMA':>8s} {'Omega':>7s} {'Alpha':>6s}")
    for i, price in enumerate(prices):
        result = indicator.update(price)
        if i % 10 == 0 or i == N - 1:
            omega_str = f"{result['omega']:.3f}" if not math.isnan(result['omega']) else "  NaN"
            print(f"{i:3d} {price:8.3f} {result['value']:8.3f} {omega_str:>7s} {result['alpha']:.4f}")

    # Count NaN omegas
    indicator2 = AdaptiveExponentialMovingAverage()
    nan_count = 0
    for price in prices:
        r = indicator2.update(price)
        if math.isnan(r["omega"]):
            nan_count += 1
    print(f"\nOmega NaN: {nan_count}/{N} bars ({100*nan_count/N:.0f}%)")
