"""
Sinc Wavelet Band-Pass Filter (SWB)

A causal FIR band-pass filter derived from the sinc wavelet system.
Decomposes price data into frequency bands (HIGH, MID, LOW, or FULL).
Optionally applies a cubic velocity kernel to produce a momentum oscillator.

Reference:
    Mak, D.K. (2003). The Science of Financial Market Trading.
    World Scientific. Chapter 9, Appendix 7.

Parameters:
    band (Band): Which frequency band to extract.
        HIGH = periods 8-16 bars  (omega_0=pi/4, omega_1=pi/8,  121 taps)
        MID  = periods 16-32 bars (omega_0=pi/8, omega_1=pi/16, 121 taps)
        LOW  = periods 32-64 bars (omega_0=pi/16, omega_1=pi/32, 201 taps)
        FULL = periods 8-64 bars  (omega_0=pi/4, omega_1=pi/32, 201 taps)
    velocity (bool): If True, apply cubic velocity kernel to the filtered
        output. Default: False.

Output:
    {"value": float} — band-passed price, or velocity of band-passed price.
    Returns NaN during the priming period.

Usage:
    indicator = SincWaveletBandpass(band=Band.MID, velocity=False)
    for price in prices:
        result = indicator.update(price)
        print(result["value"])
"""

import math
from enum import Enum


class Band(Enum):
    """Frequency band selection for the sinc wavelet filter."""
    HIGH = 0  # periods 8-16 bars
    MID = 1   # periods 16-32 bars
    LOW = 2   # periods 32-64 bars
    FULL = 3  # periods 8-64 bars (sum of HIGH + MID + LOW)


# Band parameters: (omega_0, omega_1, num_taps)
# omega_0 = upper cutoff frequency (radians/bar)
# omega_1 = lower cutoff frequency (radians/bar)
# num_taps = filter length (number of coefficients)
_BAND_PARAMS = {
    Band.HIGH: (math.pi / 4, math.pi / 8, 121),
    Band.MID: (math.pi / 8, math.pi / 16, 121),
    Band.LOW: (math.pi / 16, math.pi / 32, 201),
    Band.FULL: (math.pi / 4, math.pi / 32, 201),
}

# Cubic velocity kernel: first derivative of cubic polynomial fit
# to 4 most recent points, evaluated at the most recent point.
# Coefficients: [11/6, -3, 3/2, -1/3]
# These are the PFD degree=3 order=1 smoothing=0 backward difference coefficients.
_VELOCITY_KERNEL = [
    11.0 / 6.0,   # coefficient for y[n]   (most recent)
    -3.0,          # coefficient for y[n-1]
    3.0 / 2.0,    # coefficient for y[n-2]
    -1.0 / 3.0,   # coefficient for y[n-3] (oldest)
]
_VELOCITY_TAPS = len(_VELOCITY_KERNEL)  # 4


def _compute_coefficients(omega_0, omega_1, num_taps):
    """
    Compute sinc band-pass filter coefficients.

    The ideal band-pass filter in the frequency domain is a rectangle
    between omega_1 and omega_0. Its inverse Fourier transform gives
    the filter coefficients as a difference of two sinc functions.

    Args:
        omega_0: Upper cutoff frequency (radians/bar)
        omega_1: Lower cutoff frequency (radians/bar)
        num_taps: Number of filter coefficients

    Returns:
        List of num_taps float coefficients.

    Formula:
        h(0) = (omega_0 - omega_1) / pi
        h(k) = sin(omega_0 * k) / (pi * k) - sin(omega_1 * k) / (pi * k)
              for k = 1, 2, ..., num_taps - 1
    """
    coeffs = [0.0] * num_taps

    # k = 0: limit of (sin(omega*k) / (pi*k)) as k -> 0 is omega/pi
    coeffs[0] = (omega_0 - omega_1) / math.pi

    # k = 1, 2, ..., num_taps - 1
    for k in range(1, num_taps):
        pi_k = math.pi * k
        coeffs[k] = math.sin(omega_0 * k) / pi_k - math.sin(omega_1 * k) / pi_k

    return coeffs


class SincWaveletBandpass:
    """
    Sinc Wavelet Band-Pass Filter.

    Extracts a frequency band from a price series using a causal FIR filter
    derived from the sinc wavelet. Optionally applies cubic velocity.

    Attributes:
        band: The selected frequency band (Band enum).
        velocity: Whether cubic velocity is applied.
        num_taps: Number of band-pass filter coefficients.
        priming_period: Total number of bars before first valid output.
    """

    def __init__(self, band, velocity=False):
        """
        Initialize the Sinc Wavelet Band-Pass indicator.

        Args:
            band (Band): Frequency band to extract.
            velocity (bool): If True, apply cubic velocity kernel.
        """
        if not isinstance(band, Band):
            raise ValueError(f"band must be a Band enum value, got {band}")

        self.band = band
        self.velocity = velocity

        # Get band parameters and compute filter coefficients
        omega_0, omega_1, self.num_taps = _BAND_PARAMS[band]
        self._coefficients = _compute_coefficients(omega_0, omega_1, self.num_taps)

        # Ring buffer for price data (size = num_taps)
        # Stores the most recent num_taps prices for convolution.
        self._price_buffer = [0.0] * self.num_taps
        self._price_count = 0  # how many prices received so far
        self._price_index = 0  # current write position in ring buffer

        # Velocity buffer (size = 4) — only used if velocity=True
        # Stores the most recent 4 band-pass outputs for velocity computation.
        if self.velocity:
            self._vel_buffer = [0.0] * _VELOCITY_TAPS
            self._vel_count = 0  # how many band-pass outputs fed to velocity
            self._vel_index = 0  # current write position

        # Priming period: number of bars before first valid output
        # Band-pass needs num_taps bars to fill the buffer (first valid at bar num_taps-1,
        # i.e., after num_taps-1 NaN outputs). With velocity, need 3 more.
        self.priming_period = self.num_taps - 1
        if self.velocity:
            self.priming_period += _VELOCITY_TAPS - 1  # +3

    def update(self, price):
        """
        Process one new price bar.

        Args:
            price (float): Closing price for the current bar.

        Returns:
            dict: {"value": float} where value is the filtered output,
                  or NaN if the indicator is not yet primed.
        """
        # Store price in ring buffer
        self._price_buffer[self._price_index] = price
        self._price_index = (self._price_index + 1) % self.num_taps
        self._price_count += 1

        # Check if band-pass filter has enough data
        if self._price_count < self.num_taps:
            return {"value": math.nan}

        # Compute band-pass filter output: convolution of coefficients with
        # the price buffer. h[0] multiplies the most recent price, h[1] the
        # second most recent, etc.
        #
        # The most recent price is at index (self._price_index - 1) mod num_taps.
        # Going backwards: index (self._price_index - 1 - k) mod num_taps for h[k].
        bp_value = 0.0
        idx = self._price_index - 1  # index of most recent price
        for k in range(self.num_taps):
            # Wrap around using modulo
            buf_idx = idx % self.num_taps
            bp_value += self._coefficients[k] * self._price_buffer[buf_idx]
            idx -= 1

        # If velocity is not enabled, return band-pass output directly
        if not self.velocity:
            return {"value": bp_value}

        # Store band-pass output in velocity ring buffer
        self._vel_buffer[self._vel_index] = bp_value
        self._vel_index = (self._vel_index + 1) % _VELOCITY_TAPS
        self._vel_count += 1

        # Check if velocity buffer is full
        if self._vel_count < _VELOCITY_TAPS:
            return {"value": math.nan}

        # Compute cubic velocity: dot product of velocity kernel with
        # the last 4 band-pass values. Kernel[0] applies to most recent.
        vel_value = 0.0
        idx = self._vel_index - 1  # index of most recent bp value
        for k in range(_VELOCITY_TAPS):
            buf_idx = idx % _VELOCITY_TAPS
            vel_value += _VELOCITY_KERNEL[k] * self._vel_buffer[buf_idx]
            idx -= 1

        return {"value": vel_value}


# =============================================================================
# Example usage and verification
# =============================================================================

if __name__ == "__main__":
    # Generate a test signal: sum of three sine waves at the center
    # frequencies of the three bands.
    #
    # HIGH center: omega = pi/(4*sqrt(2)) ≈ 0.5553 rad/bar (period ≈ 11.3)
    # MID center:  omega = pi/(8*sqrt(2)) ≈ 0.2776 rad/bar (period ≈ 22.6)
    # LOW center:  omega = pi/(16*sqrt(2)) ≈ 0.1388 rad/bar (period ≈ 45.3)
    #
    N = 300
    omega_high = math.pi / (4 * math.sqrt(2))
    omega_mid = math.pi / (8 * math.sqrt(2))
    omega_low = math.pi / (16 * math.sqrt(2))

    prices = []
    for t in range(N):
        # Each component has amplitude 1.0
        p = (math.sin(omega_high * t) +
             math.sin(omega_mid * t) +
             math.sin(omega_low * t))
        prices.append(p)

    print("=== Sinc Wavelet Band-Pass Filter ===\n")
    print(f"Test signal: {N} bars, 3 sine components")
    print(f"  HIGH component: omega={omega_high:.4f} rad/bar (period={2*math.pi/omega_high:.1f})")
    print(f"  MID component:  omega={omega_mid:.4f} rad/bar (period={2*math.pi/omega_mid:.1f})")
    print(f"  LOW component:  omega={omega_low:.4f} rad/bar (period={2*math.pi/omega_low:.1f})")
    print()

    # Test each band without velocity
    for band in Band:
        indicator = SincWaveletBandpass(band=band, velocity=False)
        last_values = []
        for price in prices:
            result = indicator.update(price)
            if not math.isnan(result["value"]):
                last_values.append(result["value"])

        if last_values:
            # After priming, the band-pass should isolate its component
            # RMS of the last 100 valid values
            tail = last_values[-100:]
            rms = math.sqrt(sum(v * v for v in tail) / len(tail))
            print(f"  {band.name:4s} band: {len(last_values)} valid values, "
                  f"RMS(last 100)={rms:.4f} (ideal=0.707 for single sine)")
        else:
            print(f"  {band.name:4s} band: no valid values (need more data)")

    print()

    # Test FULL band with velocity (= WBV)
    indicator = SincWaveletBandpass(band=Band.FULL, velocity=True)
    last_values = []
    for price in prices:
        result = indicator.update(price)
        if not math.isnan(result["value"]):
            last_values.append(result["value"])
    print(f"  FULL+velocity (WBV): {len(last_values)} valid values, "
          f"last={last_values[-1]:.6f}")
