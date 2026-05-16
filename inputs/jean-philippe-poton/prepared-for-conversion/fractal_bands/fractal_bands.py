"""
Fractal Bands
Mnemonic: fban

FRASMA center line with upper/lower bands scaled by Hurst exponent.
Replaces Bollinger Bands' fixed multiplier with alpha^H where H is the
local Hurst exponent estimated from the Fractal Dimension Index.

Original author: Jean-Philippe Poton, Copyright 2008
Source: https://www.mql5.com/en/code/8895
Blog: http://fractalfinance.blogspot.com/2009/05/from-bollinger-to-fractal-bands.html
"""

import math


def fractal_bands(
    close: list[float],
    period: int = 30,
    normal_speed: int = 20,
    alpha: float = 2.0,
) -> tuple[list[float], list[float], list[float]]:
    """
    Compute Fractal Bands: FRASMA center line with upper/lower volatility bands.

    The center line is a Fractal Adaptive SMA (FRASMA) whose averaging speed
    adapts to the local fractal dimension. The bands use alpha^H scaling
    instead of a fixed Bollinger multiplier.

    Parameters
    ----------
    close : list[float]
        Close prices, index 0 = oldest.
    period : int, optional
        Lookback period for FDI computation (default 30, range 2..200).
    normal_speed : int, optional
        Base SMA period before fractal adaptation (default 20, range 1..200).
    alpha : float, optional
        Band width multiplier raised to power H (default 2.0, range 0.1..10.0).

    Returns
    -------
    tuple[list[float], list[float], list[float]]
        (frasma, upper_band, lower_band) — each a list of 252 floats.
        NaN for bars with insufficient data.
    """
    n = len(close)
    nan = float("nan")
    frasma_out = [nan] * n
    upper_out = [nan] * n
    lower_out = [nan] * n

    log2 = math.log(2.0)
    period_minus_1 = period - 1
    log_denom = math.log(2.0 * period_minus_1)
    inv_period_sq = 1.0 / (period * period)

    for pos in range(period - 1, n):
        # Window: period bars ending at pos (inclusive)
        win_start = pos - period_minus_1
        # Find max and min in window
        price_max = close[win_start]
        price_min = close[win_start]
        for i in range(win_start + 1, pos + 1):
            if close[i] > price_max:
                price_max = close[i]
            if close[i] < price_min:
                price_min = close[i]

        price_range = price_max - price_min
        if price_range <= 0.0:
            fdi = 0.0
        else:
            # Compute normalized path length over the window
            # period points, period-1 segments
            length = 0.0
            prior_diff = (close[win_start] - price_min) / price_range
            for i in range(1, period):
                diff = (close[win_start + i] - price_min) / price_range
                delta = diff - prior_diff
                length += math.sqrt(delta * delta + inv_period_sq)
                prior_diff = diff

            if length > 0.0:
                fdi = 1.0 + (math.log(length) + log2) / log_denom
            else:
                fdi = 0.0

        # Hurst exponent
        hurst = 2.0 - fdi
        if hurst < 0.01:
            hurst = 0.01
        trail_dim = 1.0 / hurst
        beta = trail_dim / 2.0
        speed = max(round(normal_speed * beta), 1)

        # FRASMA: SMA of close over 'speed' bars ending at pos
        if pos + 1 < speed:
            continue
        sma_start = pos + 1 - speed
        sma_sum = 0.0
        for i in range(sma_start, pos + 1):
            sma_sum += close[i]
        frasma_val = sma_sum / speed
        frasma_out[pos] = frasma_val

        # Deviation over the FDI lookback window (period bars)
        sq_sum = 0.0
        for i in range(win_start, pos + 1):
            res = close[i] - frasma_val
            sq_sum += res * res
        deviation = 2.0 * math.sqrt(sq_sum / period)

        # Fractal bands
        band_mult = deviation * (alpha ** hurst)
        upper_out[pos] = frasma_val + band_mult
        lower_out[pos] = frasma_val - band_mult

    return frasma_out, upper_out, lower_out


if __name__ == "__main__":
    from test_testdata import INPUT_CLOSE

    combos = [
        {"period": 10, "normal_speed": 20, "alpha": 2.0, "label": "P10_NS20_A2"},
        {"period": 20, "normal_speed": 20, "alpha": 2.0, "label": "P20_NS20_A2"},
        {"period": 30, "normal_speed": 20, "alpha": 2.0, "label": "P30_NS20_A2"},
        {"period": 50, "normal_speed": 20, "alpha": 2.0, "label": "P50_NS20_A2"},
        {"period": 30, "normal_speed": 10, "alpha": 2.0, "label": "P30_NS10_A2"},
        {"period": 30, "normal_speed": 40, "alpha": 2.0, "label": "P30_NS40_A2"},
        {"period": 30, "normal_speed": 20, "alpha": 1.0, "label": "P30_NS20_A1"},
        {"period": 30, "normal_speed": 20, "alpha": 3.0, "label": "P30_NS20_A3"},
    ]

    for combo in combos:
        label = combo["label"]
        p = combo["period"]
        ns = combo["normal_speed"]
        a = combo["alpha"]
        frasma, upper, lower = fractal_bands(INPUT_CLOSE, period=p, normal_speed=ns, alpha=a)

        for name, arr in [("FRASMA", frasma), ("UPPER", upper), ("LOWER", lower)]:
            var_name = f"EXPECTED_{name}_{label}"
            print(f"\n# Fractal Bands - {name} output (period={p}, normal_speed={ns}, alpha={a})")
            print(f"# fractal_bands(INPUT_CLOSE, period={p}, normal_speed={ns}, alpha={a})")
            print(f"{var_name}: list[float] = [")
            for i in range(0, len(arr), 6):
                chunk = arr[i:i+6]
                vals = []
                for v in chunk:
                    if math.isnan(v):
                        vals.append("math.nan")
                    else:
                        vals.append(f"{v:.15f}")
                line = ", ".join(vals) + ","
                print(f"    {line}")
            print("]")
