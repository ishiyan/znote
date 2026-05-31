"""
Mexican Hat Wavelet Filter (MHW)

A causal bandpass FIR filter derived from the Mexican Hat wavelet (second
derivative of a Gaussian). Decomposes price data into frequency bands with
zero phase shift at the center frequency.

Three standard bands are provided as an enumeration:
    Band.HIGH  - period ~4.6 bars  (7 taps)
    Band.MID   - period ~13.5 bars (17 taps)
    Band.LOW   - period ~54 bars   (65 taps)
    Band.CUSTOM - user-specified dilation or period

All coefficients are computed at full precision from the wavelet formula.
The book (Mak 2006, Section 5.7) lists coefficients rounded to 4 decimal
places (Matlab's format short). We compute from the exact formula instead.

Reference:
    Mak, Don K. (2006). Mathematical Techniques in Financial Market Trading.
    World Scientific. Chapter 5: Causal Wavelet Filters.

Usage:
    indicator = MexicanHatWavelet(band=Band.MID)
    for price in prices:
        result = indicator.update(price)
        # result['value'] is the bandpass-filtered component (or NaN)
"""

import math
from enum import Enum


# =============================================================================
# Band enumeration
# =============================================================================

class Band(Enum):
    """Frequency band selection for the Mexican Hat Wavelet filter."""
    HIGH = 0    # a_f = 1.483, omega_0 = 1.356 rad, period ~ 4.6 bars
    MID = 1     # a_f = 4.048, omega_0 = 0.467 rad, period ~ 13.5 bars
    LOW = 2     # a_f = 15.97, omega_0 = 0.116 rad, period ~ 54 bars
    CUSTOM = 3  # User-specified dilation or period


# =============================================================================
# Preset dilation values (from Table 5.2 in the book)
# =============================================================================

# These are the a_f values for the three standard bands.
# The book derives them from the zero-phase frequency omega_0 via:
#   (2/a)_f = 1.091 * omega_0 - 0.071 * omega_0^2
#   a_f = 2 / (2/a)_f
DILATION_HIGH = 1.483   # omega_0 = 1.3558 rad, period ~ 4.63 bars
DILATION_MID = 4.048    # omega_0 = 0.4670 rad, period ~ 13.45 bars
DILATION_LOW = 15.97    # omega_0 = 0.1156 rad, period ~ 54.35 bars


# =============================================================================
# Coefficient computation from the exact wavelet formula
# =============================================================================

def _compute_coefficients(a_f):
    """
    Compute normalized Mexican Hat wavelet FIR coefficients for a given
    dilation parameter a_f.

    The wavelet function is:
        psi(t) = (1 - 2*t^2) * exp(-t^2)

    Filter coefficients are sampled at integer n:
        h(n) = psi(n / a_f) for n = 0, 1, ..., K

    where K = 4 * round(a_f). This ensures we capture the full extent of
    the wavelet (beyond K, coefficients are negligible: < 1e-7).

    Normalization divides by the fitted amplitude at zero-phase frequency:
        |H(omega_0)|_f = 0.488 + 0.646 * a_f + 0.0001 * a_f^2

    This ensures unit gain at the center frequency omega_0.

    Parameters
    ----------
    a_f : float
        Dilation parameter (> 0).

    Returns
    -------
    list of float
        Normalized filter coefficients (K+1 values).
    """
    # Number of taps: K = 4 * round(a_f)
    # The wavelet decays as exp(-(n/a_f)^2), so at n = 4*a_f,
    # the value is exp(-16) ~ 1.1e-7 — negligible.
    K = 4 * round(a_f)
    if K < 1:
        K = 1

    # Compute raw coefficients: h(n) = psi(n / a_f)
    # psi(t) = (1 - 2*t^2) * exp(-t^2)
    coeffs = []
    for n in range(K + 1):
        t = n / a_f
        t2 = t * t
        h_n = (1.0 - 2.0 * t2) * math.exp(-t2)
        coeffs.append(h_n)

    # Normalization factor: |H(omega_0)|_f = 0.488 + 0.646*a_f + 0.0001*a_f^2
    # This is a curve fit from Table 5.3 (Eq 5.12 in the book).
    norm = 0.488 + 0.646 * a_f + 0.0001 * a_f * a_f

    # Normalize so output has unit amplitude at center frequency
    for i in range(len(coeffs)):
        coeffs[i] /= norm

    return coeffs


def _dilation_from_period(period):
    """
    Compute dilation a_f from a desired center period in bars.

    Steps:
        1. omega_0 = 2*pi / period
        2. (2/a)_f = 1.091 * omega_0 - 0.071 * omega_0^2  (Eq 5.11)
        3. a_f = 2 / (2/a)_f

    Parameters
    ----------
    period : float
        Desired center period in bars (> 2).

    Returns
    -------
    float
        Dilation parameter a_f.
    """
    omega_0 = 2.0 * math.pi / period
    two_over_a = 1.091 * omega_0 - 0.071 * omega_0 * omega_0
    if two_over_a <= 0.0:
        raise ValueError(
            f"Period {period} is too large for the fitting formula "
            f"(2/a = {two_over_a:.6f} <= 0). Use dilation directly.")
    a_f = 2.0 / two_over_a
    return a_f


# =============================================================================
# Main class
# =============================================================================

class MexicanHatWavelet:
    """
    Streaming Mexican Hat Wavelet bandpass filter.

    Parameters
    ----------
    band : Band
        Frequency band selection (HIGH, MID, LOW, or CUSTOM).
    dilation : float or None
        Custom dilation parameter a_f. Only used when band=CUSTOM.
    period : float or None
        Custom center period in bars. Only used when band=CUSTOM.
        Mutually exclusive with dilation.
    """

    def __init__(self, band=Band.MID, dilation=None, period=None):
        # --- Determine dilation value ---
        if band == Band.HIGH:
            self.a_f = DILATION_HIGH
        elif band == Band.MID:
            self.a_f = DILATION_MID
        elif band == Band.LOW:
            self.a_f = DILATION_LOW
        elif band == Band.CUSTOM:
            # Must provide exactly one of dilation or period
            if dilation is not None and period is not None:
                raise ValueError(
                    "Provide only one of 'dilation' or 'period', not both")
            if dilation is None and period is None:
                raise ValueError(
                    "band=CUSTOM requires either 'dilation' or 'period'")
            if period is not None:
                if period <= 2.0:
                    raise ValueError(f"period must be > 2; got {period}")
                self.a_f = _dilation_from_period(period)
            else:
                if dilation <= 0.0:
                    raise ValueError(f"dilation must be > 0; got {dilation}")
                self.a_f = dilation
        else:
            raise ValueError(f"Unknown band: {band}")

        # --- Compute coefficients from the exact formula ---
        self.coefficients = _compute_coefficients(self.a_f)

        # --- Number of taps ---
        self.num_taps = len(self.coefficients)

        # --- Ring buffer for storing the last num_taps prices ---
        # buffer[0] = most recent price, buffer[1] = one bar ago, etc.
        self.buffer = [0.0] * self.num_taps
        self.count = 0  # number of prices received

    def update(self, price):
        """
        Process one new price bar.

        Parameters
        ----------
        price : float
            Closing price of the current bar.

        Returns
        -------
        dict with key:
            'value' - Filtered output (NaN until buffer is full).
        """
        # Shift buffer right and insert new price at position 0
        for i in range(self.num_taps - 1, 0, -1):
            self.buffer[i] = self.buffer[i - 1]
        self.buffer[0] = price
        self.count += 1

        # Need at least num_taps prices before producing output
        if self.count < self.num_taps:
            return {'value': math.nan}

        # FIR convolution: y = sum(h[k] * x[n-k]) for k = 0..K
        # buffer[k] holds x[n-k]
        y = 0.0
        for k in range(self.num_taps):
            y += self.coefficients[k] * self.buffer[k]

        return {'value': y}


# =============================================================================
# Batch function (convenience wrapper)
# =============================================================================

def mexican_hat_wavelet(prices, band=Band.MID, dilation=None, period=None):
    """
    Batch computation of Mexican Hat Wavelet filter.

    Parameters
    ----------
    prices : list of float
        Price series (closing prices).
    band : Band
        Frequency band (HIGH, MID, LOW, CUSTOM).
    dilation : float or None
        Custom dilation (only for CUSTOM).
    period : float or None
        Custom period in bars (only for CUSTOM).

    Returns
    -------
    list of dict
        One result dict per input price.
    """
    indicator = MexicanHatWavelet(band=band, dilation=dilation, period=period)
    results = []
    for price in prices:
        results.append(indicator.update(price))
    return results


# =============================================================================
# Main: demonstration
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Mexican Hat Wavelet Filter (MHW) — Demonstration")
    print("=" * 70)

    # Show computed coefficients for presets
    print("\n--- Preset Coefficients (computed at full precision) ---")
    for band_name, a_f_val in [("HIGH", DILATION_HIGH),
                                ("MID", DILATION_MID),
                                ("LOW", DILATION_LOW)]:
        coeffs = _compute_coefficients(a_f_val)
        print(f"\n  {band_name} (a_f={a_f_val}, {len(coeffs)} taps):")
        for i in range(0, len(coeffs), 5):
            chunk = coeffs[i:i+5]
            line = "    " + ", ".join(f"{c:+.15f}" for c in chunk)
            print(line)

    # --- Test 1: Pure sine wave at MID center frequency ---
    print("\n\n--- Test 1: Pure sine wave at MID center frequency ---")
    print("    omega_0 = 0.467 rad/bar, period = 13.45 bars")
    print("    Expected: output ≈ input (zero phase, unit amplitude)")

    omega_mid = 0.467
    N = 50
    prices_sine = []
    for t in range(N):
        x = math.sin(omega_mid * t)
        prices_sine.append(x)

    mhw_mid = MexicanHatWavelet(band=Band.MID)
    print(f"    Number of taps: {mhw_mid.num_taps}")
    print(f"\n  {'Bar':>4s}  {'Input':>8s}  {'Output':>8s}  {'Error':>8s}")
    for t, price in enumerate(prices_sine):
        r = mhw_mid.update(price)
        if not math.isnan(r['value']):
            err = r['value'] - price
            print(f"  {t:4d}  {price:8.5f}  {r['value']:8.5f}  {err:+8.5f}")

    # --- Test 2: Mixed frequencies — band separation ---
    print("\n--- Test 2: Mixed frequencies (high + mid + low) ---")
    print("    p = sin(1.356*t) + 2*sin(0.467*t) + 3*sin(0.116*t)")

    omega_high = 1.356
    omega_low = 0.116
    N2 = 100

    prices_mixed = []
    for t in range(N2):
        x = (math.sin(omega_high * t) +
             2.0 * math.sin(omega_mid * t) +
             3.0 * math.sin(omega_low * t))
        prices_mixed.append(x)

    mhw_h = MexicanHatWavelet(band=Band.HIGH)
    mhw_m = MexicanHatWavelet(band=Band.MID)
    mhw_l = MexicanHatWavelet(band=Band.LOW)

    print(f"    HIGH taps: {mhw_h.num_taps}, MID taps: {mhw_m.num_taps}, "
          f"LOW taps: {mhw_l.num_taps}")

    print(f"\n  {'Bar':>4s}  {'True Hi':>8s}  {'Filt Hi':>8s}  "
          f"{'True Mid':>8s}  {'Filt Mid':>8s}  "
          f"{'True Lo':>8s}  {'Filt Lo':>8s}")

    # Print from bar 65 onwards (when all filters are primed)
    for t in range(N2):
        rh = mhw_h.update(prices_mixed[t])
        rm = mhw_m.update(prices_mixed[t])
        rl = mhw_l.update(prices_mixed[t])

        if t >= 68 and t <= 80:
            true_h = math.sin(omega_high * t)
            true_m = 2.0 * math.sin(omega_mid * t)
            true_l = 3.0 * math.sin(omega_low * t)
            vh = rh['value'] if not math.isnan(rh['value']) else 0.0
            vm = rm['value'] if not math.isnan(rm['value']) else 0.0
            vl = rl['value'] if not math.isnan(rl['value']) else 0.0
            print(f"  {t:4d}  {true_h:8.4f}  {vh:8.4f}  "
                  f"{true_m:8.4f}  {vm:8.4f}  "
                  f"{true_l:8.4f}  {vl:8.4f}")

    # --- Test 3: Custom period ---
    print("\n--- Test 3: Custom period = 20 bars ---")
    omega_20 = 2.0 * math.pi / 20.0
    print(f"    omega_0 = {omega_20:.4f} rad/bar")

    prices_custom = []
    for t in range(80):
        x = math.sin(omega_20 * t)
        prices_custom.append(x)

    mhw_custom = MexicanHatWavelet(band=Band.CUSTOM, period=20.0)
    print(f"    Computed dilation a_f = {mhw_custom.a_f:.4f}")
    print(f"    Number of taps = {mhw_custom.num_taps}")

    print(f"\n  {'Bar':>4s}  {'Input':>8s}  {'Output':>8s}  {'Error':>8s}")
    for t, price in enumerate(prices_custom):
        r = mhw_custom.update(price)
        if not math.isnan(r['value']) and t >= 30 and t <= 45:
            err = r['value'] - price
            print(f"  {t:4d}  {price:8.5f}  {r['value']:8.5f}  {err:+8.5f}")

    # --- Test 4: Real price data ---
    print("\n--- Test 4: Real price data with all three bands ---")

    prices_real = [
        91.50, 94.82, 94.38, 95.10, 93.78, 94.63, 92.53, 92.75,
        90.32, 92.47, 96.13, 97.25, 98.50, 89.88, 91.00, 92.82,
        89.16, 89.35, 91.63, 89.88, 88.38, 87.63, 84.78, 83.00,
        83.50, 81.38, 84.44, 89.25, 86.38, 86.25, 85.25, 87.13,
        85.82, 88.97, 88.47, 86.88, 86.82, 84.88, 84.19, 83.88,
        83.38, 85.50, 89.19, 89.44, 91.10, 90.75, 91.44, 89.00,
        91.00, 90.50
    ]

    mhw_h2 = MexicanHatWavelet(band=Band.HIGH)
    mhw_m2 = MexicanHatWavelet(band=Band.MID)
    mhw_l2 = MexicanHatWavelet(band=Band.LOW)

    print(f"\n  {'Bar':>4s}  {'Price':>8s}  {'High':>8s}  {'Mid':>8s}  {'Low':>8s}")
    for t, price in enumerate(prices_real):
        rh = mhw_h2.update(price)
        rm = mhw_m2.update(price)
        rl = mhw_l2.update(price)
        vh = f"{rh['value']:8.3f}" if not math.isnan(rh['value']) else "     NaN"
        vm = f"{rm['value']:8.3f}" if not math.isnan(rm['value']) else "     NaN"
        vl = f"{rl['value']:8.3f}" if not math.isnan(rl['value']) else "     NaN"
        print(f"  {t:4d}  {price:8.2f}  {vh}  {vm}  {vl}")

    print("\nDone.")
