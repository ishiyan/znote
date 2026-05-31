"""
Cubic Vertex Indicator

Predicts turning points by fitting a cubic polynomial to the 4 most recent
price points and computing where the two vertices (extrema) occur.

Reference:
    Mak, D.K. (2003). The Science of Financial Market Trading.
    World Scientific. Chapter 7, Appendix 5.

Output:
    {"bars_to_near_turn": float, "bars_to_far_turn": float}
    bars_to_near_turn = root closer to zero (the more imminent turning point)
    bars_to_far_turn = root farther from zero (the more distant turning point)
    Positive = future, negative = past.
    NaN when undefined.

Usage:
    indicator = CubicVertex()
    for price in smoothed_prices:
        result = indicator.update(price)
        print(result["bars_to_near_turn"], result["bars_to_far_turn"])
"""

import math


class CubicVertex:
    """
    Cubic Vertex indicator.

    Fits a cubic to the 4 most recent data points and computes the
    locations of both turning points relative to the current bar.

    Attributes:
        priming_period: 3 (first valid output at bar index 3).
    """

    def __init__(self):
        """Initialize the Cubic Vertex indicator."""
        # Ring buffer for 4 most recent prices
        self._buffer = [0.0, 0.0, 0.0, 0.0]
        self._count = 0
        self._index = 0
        self.priming_period = 3

    def update(self, price):
        """
        Process one new price bar.

        Args:
            price (float): Input price (ideally pre-smoothed).

        Returns:
            dict: {"bars_to_near_turn": float, "bars_to_far_turn": float}
                  bars_to_near_turn = root with smaller absolute value
                  bars_to_far_turn = root with larger absolute value
                  NaN for undefined cases.
        """
        # Store price in ring buffer
        self._buffer[self._index] = price
        self._index = (self._index + 1) % 4
        self._count += 1

        nan_result = {"bars_to_near_turn": math.nan, "bars_to_far_turn": math.nan}

        # Need at least 4 prices
        if self._count < 4:
            return nan_result

        # Extract prices: x[n] (newest), x[n-1], x[n-2], x[n-3] (oldest)
        xn = self._buffer[(self._index - 1) % 4]
        xn1 = self._buffer[(self._index - 2) % 4]
        xn2 = self._buffer[(self._index - 3) % 4]
        xn3 = self._buffer[(self._index - 4) % 4]

        # Compute cubic polynomial coefficients (Eq 7.2a-c)
        # c = third-order finite difference / 6
        c = (xn - 3.0 * xn1 + 3.0 * xn2 - xn3) / 6.0

        # d = second-order coefficient
        d = (2.0 * xn - 5.0 * xn1 + 4.0 * xn2 - xn3) / 2.0

        # e = first-order coefficient (velocity at t=0)
        e = (11.0 * xn - 18.0 * xn1 + 9.0 * xn2 - 2.0 * xn3) / 6.0

        # Case: c == 0 — cubic term vanishes, reduces to parabola or line
        if c == 0.0:
            if d == 0.0:
                # Linear or constant — no turning point
                return nan_result
            else:
                # Parabolic fallback: single vertex at -e/(2d)
                # Only one turning point — it's both near and far
                vertex = -e / (2.0 * d)
                return {"bars_to_near_turn": vertex, "bars_to_far_turn": math.nan}

        # Full cubic: solve quadratic 3c*t² + 2d*t + e = 0
        # Discriminant: d² - 3ce (from (2d)² - 4*(3c)*e, divided by 4)
        disc = d * d - 3.0 * c * e

        if disc < 0.0:
            # No real roots — only inflection, no turning points
            return nan_result

        if disc == 0.0:
            # One degenerate vertex (double root)
            vertex = -d / (3.0 * c)
            return {"bars_to_near_turn": vertex, "bars_to_far_turn": vertex}

        # Two distinct real roots
        sqrt_disc = math.sqrt(disc)
        three_c = 3.0 * c

        t_plus = (-d + sqrt_disc) / three_c
        t_minus = (-d - sqrt_disc) / three_c

        # near = closer to zero (smaller |value|), far = farther from zero
        if abs(t_plus) <= abs(t_minus):
            near = t_plus
            far = t_minus
        else:
            near = t_minus
            far = t_plus

        return {"bars_to_near_turn": near, "bars_to_far_turn": far}


if __name__ == "__main__":
    # Test with known cubic: x = (t-10)(t-30)(t-50)/100
    # Vertices where x'=0: t ≈ 21.84 and t ≈ 38.16
    print("=== Cubic Vertex Indicator ===\n")
    print("Test: Known cubic x = (t-10)(t-30)(t-50)/100")
    print("  Vertices at t ≈ 21.84 and t ≈ 38.16\n")

    indicator = CubicVertex()
    for t in range(60):
        price = (t - 10.0) * (t - 30.0) * (t - 50.0) / 100.0
        result = indicator.update(price)
        near = result["bars_to_near_turn"]
        far = result["bars_to_far_turn"]
        if not math.isnan(near) and 20 <= t <= 40:
            print(f"  t={t:2d}: near={near:+.4f} far={far:+.4f} "
                  f"(abs_pos: near={t+near:.2f}, far={t+far:.2f})")
