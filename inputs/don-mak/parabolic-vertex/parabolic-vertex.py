"""
Parabolic Vertex Indicator

Predicts turning points by fitting a parabola to the 3 most recent price
points and computing where the vertex (extremum) occurs.

Reference:
    Mak, D.K. (2003). The Science of Financial Market Trading.
    World Scientific. Chapter 7, Appendix 5.

Output:
    {"bars_to_near_turn": float} — bars from current bar to turning point.
    Positive = future, negative = past, near zero = now.
    NaN when undefined (priming or collinear points).

Usage:
    indicator = ParabolicVertex()
    for price in smoothed_prices:
        result = indicator.update(price)
        print(result["bars_to_near_turn"])
"""

import math


class ParabolicVertex:
    """
    Parabolic Vertex indicator.

    Fits a parabola to the 3 most recent data points and computes the
    location of the turning point (vertex) relative to the current bar.

    Attributes:
        priming_period: 2 (first valid output at bar index 2).
    """

    def __init__(self):
        """Initialize the Parabolic Vertex indicator."""
        # Ring buffer for 3 most recent prices
        self._buffer = [0.0, 0.0, 0.0]
        self._count = 0
        self._index = 0
        self.priming_period = 2

    def update(self, price):
        """
        Process one new price bar.

        Args:
            price (float): Input price (ideally pre-smoothed).

        Returns:
            dict: {"bars_to_near_turn": float} or NaN if undefined.
        """
        # Store price in ring buffer
        self._buffer[self._index] = price
        self._index = (self._index + 1) % 3
        self._count += 1

        # Need at least 3 prices
        if self._count < 3:
            return {"bars_to_near_turn": math.nan}

        # Extract prices: x[n] (newest), x[n-1], x[n-2] (oldest)
        xn = self._buffer[(self._index - 1) % 3]
        xn1 = self._buffer[(self._index - 2) % 3]
        xn2 = self._buffer[(self._index - 3) % 3]

        # Denominator = second-order finite difference (proportional to curvature)
        # If zero, the three points are collinear — no turning point exists.
        denom = xn - 2.0 * xn1 + xn2

        if denom == 0.0:
            return {"bars_to_near_turn": math.nan}

        # Numerator = first derivative at t=0 (velocity at current bar)
        # From the parabola fit: e = (3*xn - 4*xn1 + xn2) / 2
        # Vertex at tv = -e/(2d) = -(3xn - 4xn1 + xn2) / (2*(xn - 2xn1 + xn2))
        # Simplified: tv = -(1.5*xn - 2*xn1 + 0.5*xn2) / (xn - 2*xn1 + xn2)
        numer = 1.5 * xn - 2.0 * xn1 + 0.5 * xn2

        bars_to_near_turn = -numer / denom

        return {"bars_to_near_turn": bars_to_near_turn}


if __name__ == "__main__":
    # Test with known parabola: x = -(t-25)^2 + 100
    # Vertex at t=25. At bar t, offset should be (25 - t).
    print("=== Parabolic Vertex Indicator ===\n")
    print("Test: Known parabola x = -(t-25)^2 + 100")
    print("  Vertex at t=25. Predicted offset = (25 - current_bar).\n")

    indicator = ParabolicVertex()
    for t in range(50):
        price = -(t - 25) ** 2 + 100.0
        result = indicator.update(price)
        v = result["bars_to_near_turn"]
        if not math.isnan(v) and abs(t - 25) <= 5:
            expected = 25 - t
            print(f"  t={t:2d}: bars_to_near_turn={v:+.1f} (expected={expected:+d})")
