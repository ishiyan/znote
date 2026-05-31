"""
Instantaneous Sine Wave Period (ISWP)

Estimates the dominant cycle period of price data by modeling it locally as a
single sine wave superimposed on a constant level:

    x = A * sin(omega * t + phi) + D

Two methods are combined (4-point and 5-point), selecting the one with lower
estimation error at each bar.

Reference:
    Mak, Don K. (2006). Mathematical Techniques in Financial Market Trading.
    World Scientific. Chapter 6 & Appendix 3.

Usage:
    indicator = InstantaneousSineWavePeriod(smoothing=6)
    for price in prices:
        result = indicator.update(price)
        # result['period'] is the estimated cycle period in bars (or NaN)
"""

import math


class InstantaneousSineWavePeriod:
    """
    Streaming Instantaneous Sine Wave Period indicator.

    Parameters
    ----------
    smoothing : int, default 0
        EMA smoothing length for input prices before frequency estimation.
        0 means no smoothing. When > 0, EMA alpha = 2 / (smoothing + 1).
    min_period : float, default 4.0
        Minimum allowed period in bars. Estimates below this are rejected.
    max_period : float, default 50.0
        Maximum allowed period in bars. Estimates above this are rejected.
    error_threshold : float, default 20.0
        If both IF4 and IF5 errors exceed this, output is NaN.
    dx : float, default 0.01
        Assumed measurement error for each price (for error propagation).
    """

    def __init__(self, smoothing=0, min_period=4.0, max_period=50.0,
                 error_threshold=20.0, dx=0.01):
        # --- Validate parameters ---
        if smoothing < 0:
            raise ValueError(f"smoothing must be >= 0; got {smoothing}")
        if min_period <= 0:
            raise ValueError(f"min_period must be > 0; got {min_period}")
        if max_period <= min_period:
            raise ValueError(
                f"max_period ({max_period}) must be > min_period ({min_period})")
        if error_threshold <= 0:
            raise ValueError(
                f"error_threshold must be > 0; got {error_threshold}")
        if dx <= 0:
            raise ValueError(f"dx must be > 0; got {dx}")

        self.smoothing = smoothing
        self.min_period = min_period
        self.max_period = max_period
        self.error_threshold = error_threshold
        self.dx = dx

        # --- EMA state ---
        # alpha = 2 / (L + 1), initialized on first price
        if smoothing > 0:
            self.ema_alpha = 2.0 / (smoothing + 1.0)
        else:
            self.ema_alpha = 1.0  # no smoothing (pass-through)
        self.ema_value = None  # will be set on first price

        # --- Ring buffer for the last 5 smoothed prices ---
        # Index 0 = most recent (x_0), index 1 = one bar ago (x_{-1}), etc.
        self.buffer = [0.0] * 5
        self.count = 0  # number of prices received so far

    def _apply_ema(self, price):
        """
        Apply EMA smoothing to the incoming price.
        Returns the smoothed price.
        """
        if self.ema_value is None:
            # Initialize EMA to first price
            self.ema_value = price
        else:
            # Standard EMA update: ema = alpha * price + (1 - alpha) * ema
            self.ema_value = (self.ema_alpha * price +
                             (1.0 - self.ema_alpha) * self.ema_value)
        return self.ema_value

    def _push_buffer(self, value):
        """
        Push a new smoothed price into the ring buffer.
        Shifts old values right (index 0 is newest).
        """
        # Shift: [0,1,2,3,4] -> [new,0,1,2,3]
        for i in range(4, 0, -1):
            self.buffer[i] = self.buffer[i - 1]
        self.buffer[0] = value

    def _calc_omega4(self):
        """
        Calculate circular frequency using 4-point method.

        Uses x_0, x_{-1}, x_{-2}, x_{-3} (buffer indices 0,1,2,3).

        Returns (omega4, error4) or (NaN, error_threshold) if invalid.
        """
        x0 = self.buffer[0]
        xm1 = self.buffer[1]
        xm2 = self.buffer[2]
        xm3 = self.buffer[3]

        # Denominator: x_{-1} - x_{-2}
        den = xm1 - xm2

        # Check: denominator must be non-zero
        if den == 0.0:
            return (math.nan, self.error_threshold)

        # Ratio R4 = (x_0 - x_{-3}) / (x_{-1} - x_{-2})
        ratio = (x0 - xm3) / den

        # sqrt_arg = 3 - ratio (must be >= 0)
        sqrt_arg = 3.0 - ratio
        if sqrt_arg < 0.0:
            return (math.nan, self.error_threshold)

        # arg of arcsin = 0.5 * sqrt(sqrt_arg), must be <= 1
        sqrt_val = math.sqrt(sqrt_arg)
        arg = 0.5 * sqrt_val
        if arg > 1.0:
            return (math.nan, self.error_threshold)

        # omega4 = 2 * arcsin(arg)
        omega4 = 2.0 * math.asin(arg)

        # --- Error calculation ---
        # From Appendix 3, Eqn A3.25-A3.26
        dx = self.dx
        dx2 = dx * dx

        # Check denominators for error formula
        denom1 = 1.0 - 0.25 * sqrt_arg  # = 1 - (1/4)(3 - ratio) = (ratio - 1)/4 + 0.5
        if denom1 <= 0.0 or sqrt_arg == 0.0:
            return (omega4, self.error_threshold)

        # f1 = 1 / ((1 - 0.25*sqrt_arg) * sqrt_arg)
        f1 = 1.0 / (denom1 * sqrt_arg)

        # q^2 = (1/den)^2 * (dx0^2 + dxm3^2) + (ratio/den)^2 * (dxm1^2 + dxm2^2)
        # Note: (x0-xm3)/(den^2) = ratio/den
        inv_den2 = 1.0 / (den * den)
        q2 = inv_den2 * (dx2 + dx2) + (ratio * ratio) * inv_den2 * (dx2 + dx2)

        # delta_omega4 = 0.5 * sqrt(f1 * q2)
        product = f1 * q2
        if product < 0.0:
            return (omega4, self.error_threshold)

        error4 = 0.5 * math.sqrt(product)
        return (omega4, error4)

    def _calc_omega5(self):
        """
        Calculate circular frequency using 5-point method.

        Uses x_0, x_{-1}, x_{-3}, x_{-4} (buffer indices 0,1,3,4).

        Returns (omega5, error5) or (NaN, error_threshold) if invalid.
        """
        x0 = self.buffer[0]
        xm1 = self.buffer[1]
        xm3 = self.buffer[3]
        xm4 = self.buffer[4]

        # Denominator: x_{-1} - x_{-3}
        den1 = xm1 - xm3

        # Check: denominator must be non-zero
        if den1 == 0.0:
            return (math.nan, self.error_threshold)

        # arg of arccos = (x_0 - x_{-4}) / (2 * (x_{-1} - x_{-3}))
        arg = 0.5 * (x0 - xm4) / den1

        # Check: |arg| must be <= 1
        if abs(arg) > 1.0:
            return (math.nan, self.error_threshold)

        # omega5 = arccos(arg)
        omega5 = math.acos(arg)

        # --- Error calculation ---
        # From Appendix 3, Eqn A3.27-A3.28
        dx = self.dx
        dx2 = dx * dx

        # Check denominator for error formula
        denom = 1.0 - arg * arg
        if denom <= 0.0:
            return (omega5, self.error_threshold)

        # f1 = 1 / (1 - arg^2)
        f1 = 1.0 / denom

        # r^2 = (1/den1)^2 * (dx0^2 + dxm4^2)
        #      + ((x0-xm4)/(den1^2))^2 * (dxm1^2 + dxm3^2)
        inv_den1_2 = 1.0 / (den1 * den1)
        numerator_ratio = (x0 - xm4) / (den1 * den1)
        r2 = inv_den1_2 * (dx2 + dx2) + (numerator_ratio * numerator_ratio) * (dx2 + dx2)

        # delta_omega5 = 0.5 * sqrt(f1 * r2)
        product = f1 * r2
        if product < 0.0:
            return (omega5, self.error_threshold)

        error5 = 0.5 * math.sqrt(product)
        return (omega5, error5)

    def _calc_model_params(self, omega):
        """
        Calculate amplitude A, phase phi, velocity, acceleration, dc_level
        from the chosen omega and buffer prices.

        Uses the 4-point system equations (A3.12-A3.18).
        """
        x0 = self.buffer[0]
        xm1 = self.buffer[1]
        xm2 = self.buffer[2]

        # Precompute trig values
        half_w = omega / 2.0
        three_half_w = 1.5 * omega

        sin_hw = math.sin(half_w)
        cos_hw = math.cos(half_w)
        sin_3hw = math.sin(three_half_w)
        cos_3hw = math.cos(three_half_w)

        # D0 = sin^2(w/2) * cos(w/2) * sin(3w/2) - sin^3(w/2) * cos(3w/2)
        # Factor: sin^2(w/2) * [cos(w/2)*sin(3w/2) - sin(w/2)*cos(3w/2)]
        # The bracket = sin(3w/2 - w/2) = sin(w) by angle subtraction
        # So D0 = sin^2(w/2) * sin(w)
        D0 = sin_hw * sin_hw * cos_hw * sin_3hw - sin_hw * sin_hw * sin_hw * cos_3hw

        # Avoid division by zero
        if abs(D0) < 1e-15:
            return (math.nan, math.nan, math.nan, math.nan, math.nan, math.nan)

        inv_D0 = 1.0 / D0

        # Differences
        dx0_m1 = x0 - xm1       # x_0 - x_{-1}
        dxm1_m2 = xm1 - xm2     # x_{-1} - x_{-2}

        # C = 2A*cos(phi) from Eqn A3.12
        C = inv_D0 * (dx0_m1 * sin_hw * sin_3hw - dxm1_m2 * sin_hw * sin_hw)

        # S = 2A*sin(phi) from Eqn A3.13
        S = inv_D0 * (dxm1_m2 * sin_hw * cos_hw - dx0_m1 * sin_hw * cos_3hw)

        # Amplitude: A = sqrt(C^2 + S^2) / 2
        amplitude = 0.5 * math.sqrt(C * C + S * S)

        # Phase: phi = atan2(S, C)
        phi = math.atan2(S, C)

        # Wave velocity: v = A * omega * cos(phi)
        velocity = amplitude * omega * math.cos(phi)

        # Wave acceleration: a = -A * omega^2 * sin(phi)
        acceleration = -amplitude * omega * omega * math.sin(phi)

        # DC level: D = x_0 - A*sin(phi) = x_0 - S/2
        dc_level = x0 - S / 2.0

        return (amplitude, phi, velocity, acceleration, dc_level, D0)

    def update(self, price):
        """
        Process one new price bar.

        Parameters
        ----------
        price : float
            Closing price of the current bar.

        Returns
        -------
        dict with keys:
            'period'       - Cycle period in bars (NaN if invalid)
            'omega'        - Circular frequency in radians/bar (NaN if invalid)
            'velocity'     - Wave velocity (NaN if invalid)
            'acceleration' - Wave acceleration (NaN if invalid)
            'amplitude'    - Sine wave amplitude (NaN if invalid)
            'phase'        - Phase angle in radians (NaN if invalid)
            'dc_level'     - Constant level D (NaN if invalid)
        """
        nan = math.nan
        invalid = {
            'period': nan, 'omega': nan, 'velocity': nan,
            'acceleration': nan, 'amplitude': nan, 'phase': nan,
            'dc_level': nan
        }

        # --- Step 1: Apply EMA smoothing ---
        if self.smoothing > 0:
            smoothed = self._apply_ema(price)
        else:
            smoothed = price

        # --- Step 2: Push into ring buffer ---
        self._push_buffer(smoothed)
        self.count += 1

        # --- Step 3: Need at least 5 prices to use both methods ---
        if self.count < 5:
            return invalid

        # --- Step 4: Calculate omega using both methods ---
        omega4, error4 = self._calc_omega4()
        omega5, error5 = self._calc_omega5()

        # --- Step 5: Select best omega (lowest error) ---
        if error4 >= self.error_threshold and error5 >= self.error_threshold:
            # Neither method produced a valid result
            return invalid

        if error5 < error4:
            omega = omega5
        else:
            omega = omega4

        # Omega must be positive and finite
        if math.isnan(omega) or omega <= 0.0:
            return invalid

        # --- Step 6: Calculate period and check bounds ---
        period = (2.0 * math.pi) / omega

        if period < self.min_period or period > self.max_period:
            return invalid

        # --- Step 7: Calculate derived quantities ---
        amplitude, phi, velocity, acceleration, dc_level, _ = \
            self._calc_model_params(omega)

        return {
            'period': period,
            'omega': omega,
            'velocity': velocity,
            'acceleration': acceleration,
            'amplitude': amplitude,
            'phase': phi,
            'dc_level': dc_level
        }


# =============================================================================
# Batch function (convenience wrapper)
# =============================================================================

def instantaneous_sine_wave_period(prices, smoothing=0, min_period=4.0,
                                   max_period=50.0, error_threshold=20.0,
                                   dx=0.01):
    """
    Batch computation of Instantaneous Sine Wave Period.

    Parameters
    ----------
    prices : list of float
        Price series (closing prices).
    smoothing : int
        EMA smoothing length (0 = none).
    min_period : float
        Minimum allowed period.
    max_period : float
        Maximum allowed period.
    error_threshold : float
        Error threshold for validity.
    dx : float
        Assumed measurement error.

    Returns
    -------
    list of dict
        One result dict per input price.
    """
    indicator = InstantaneousSineWavePeriod(
        smoothing=smoothing,
        min_period=min_period,
        max_period=max_period,
        error_threshold=error_threshold,
        dx=dx
    )
    results = []
    for price in prices:
        results.append(indicator.update(price))
    return results


# =============================================================================
# Main: demonstration with synthetic and real-ish data
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Instantaneous Sine Wave Period (ISWP) — Demonstration")
    print("=" * 70)

    # --- Test 1: Pure sine wave (should recover exact frequency) ---
    print("\n--- Test 1: Pure sine wave ---")
    print("    A=0.25, omega=pi/4, phi=pi/3, D=0.6")
    print("    Expected period T = 2*pi / (pi/4) = 8.0 bars")

    A_true = 0.25
    omega_true = math.pi / 4.0
    phi_true = math.pi / 3.0
    D_true = 0.6
    T_true = 2.0 * math.pi / omega_true  # = 8.0

    # Generate 20 bars of pure sine wave
    N = 20
    prices_sine = []
    for t in range(N):
        x = A_true * math.sin(omega_true * t + phi_true) + D_true
        prices_sine.append(x)

    # Run ISWP with no smoothing
    iswp = InstantaneousSineWavePeriod(smoothing=0, min_period=2.0, max_period=100.0)
    print(f"\n  {'Bar':>4s}  {'Price':>8s}  {'Period':>8s}  {'Omega':>8s}  {'Velocity':>10s}  {'Accel':>10s}")
    for t, price in enumerate(prices_sine):
        r = iswp.update(price)
        period_str = f"{r['period']:.4f}" if not math.isnan(r['period']) else "NaN"
        omega_str = f"{r['omega']:.4f}" if not math.isnan(r['omega']) else "NaN"
        vel_str = f"{r['velocity']:.6f}" if not math.isnan(r['velocity']) else "NaN"
        acc_str = f"{r['acceleration']:.6f}" if not math.isnan(r['acceleration']) else "NaN"
        print(f"  {t:4d}  {price:8.5f}  {period_str:>8s}  {omega_str:>8s}  {vel_str:>10s}  {acc_str:>10s}")

    print(f"\n  True period: {T_true:.4f}")

    # --- Test 2: Frequency chirp ---
    print("\n--- Test 2: Frequency chirp (linearly increasing frequency) ---")
    print("    A=0.25, omega0=pi/4, c=0.1, phi=0, D=0.3")

    A2 = 0.25
    omega0 = math.pi / 4.0
    c = 0.1
    phi2 = 0.0
    D2 = 0.3

    N2 = 30
    prices_chirp = []
    for t in range(N2):
        # Phase: omega0 * (1 + c*t) * t + phi
        phase = omega0 * (1.0 + c * t) * t + phi2
        x = A2 * math.sin(phase) + D2
        prices_chirp.append(x)

    iswp2 = InstantaneousSineWavePeriod(smoothing=0, min_period=2.0, max_period=100.0)
    print(f"\n  {'Bar':>4s}  {'Price':>8s}  {'Period':>8s}  {'True ω':>8s}  {'Est ω':>8s}")
    for t, price in enumerate(prices_chirp):
        r = iswp2.update(price)
        # True instantaneous omega at time t: omega0 * (1 + 2*c*t)
        true_omega = omega0 * (1.0 + 2.0 * c * t)
        true_period = 2.0 * math.pi / true_omega

        period_str = f"{r['period']:.3f}" if not math.isnan(r['period']) else "NaN"
        omega_str = f"{r['omega']:.4f}" if not math.isnan(r['omega']) else "NaN"
        print(f"  {t:4d}  {price:8.5f}  {period_str:>8s}  {true_omega:8.4f}  {omega_str:>8s}")

    # --- Test 3: Real-ish financial data (noisy) ---
    print("\n--- Test 3: Financial data with EMA(6) smoothing ---")

    # Use some typical stock-like prices
    prices_real = [
        91.50, 94.82, 94.38, 95.10, 93.78, 94.63, 92.53, 92.75,
        90.32, 92.47, 96.13, 97.25, 98.50, 89.88, 91.00, 92.82,
        89.16, 89.35, 91.63, 89.88, 88.38, 87.63, 84.78, 83.00,
        83.50, 81.38, 84.44, 89.25, 86.38, 86.25
    ]

    iswp3 = InstantaneousSineWavePeriod(smoothing=6, min_period=4.0, max_period=50.0)
    print(f"\n  {'Bar':>4s}  {'Price':>8s}  {'Period':>8s}  {'Omega':>8s}  {'Amplitude':>10s}")
    valid_count = 0
    for t, price in enumerate(prices_real):
        r = iswp3.update(price)
        period_str = f"{r['period']:.2f}" if not math.isnan(r['period']) else "NaN"
        omega_str = f"{r['omega']:.4f}" if not math.isnan(r['omega']) else "NaN"
        amp_str = f"{r['amplitude']:.4f}" if not math.isnan(r['amplitude']) else "NaN"
        if not math.isnan(r['period']):
            valid_count += 1
        print(f"  {t:4d}  {price:8.2f}  {period_str:>8s}  {omega_str:>8s}  {amp_str:>10s}")

    print(f"\n  Valid estimates: {valid_count}/{len(prices_real)} bars")
    print("  (NaN is expected when data doesn't fit sine model)")
    print("\nDone.")
