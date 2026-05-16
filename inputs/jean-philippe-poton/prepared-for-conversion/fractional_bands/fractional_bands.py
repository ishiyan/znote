"""
Fractional Bands (fctban)

Fractal-adaptive moving average with FBM-scaled volatility bands.
Uses fractional Brownian motion power law: band_width = 2 * deviation^(2*H)
where H is the Hurst exponent derived from the Fractal Dimension Index.

Original author: Jean-Philippe Poton, Copyright 2009
Source: https://www.mql5.com/en/code/8900
Blog: http://fractalfinance.blogspot.com/2009/05/fractional-bands.html

Parameters
----------
close : list[float]
    Close prices, index 0 = oldest. Minimum length: period + 1.
period : int
    Lookback period for FDI computation and base SMA speed.
    Range: 2..500, default 30.
price_scale : float
    Multiplier converting price to a working numeric space for the
    deviation exponentiation. Use 1.0 for indices/commodities,
    100.0 for percentage-quoted instruments, 10000.0 for 4-digit FX.
    Range: > 0, default 1.0.
    (Renamed from the original MQ4 parameter ``PIP_Convertor``.)

Returns
-------
tuple[list[float], list[float], list[float]]
    (frasma, upper_band, lower_band) — each list has the same length
    as *close*. Unprimed positions are ``float('nan')``.
"""

import math


def fractional_bands(
    close: list[float],
    period: int = 30,
    price_scale: float = 1.0,
) -> tuple[list[float], list[float], list[float]]:
    """Compute Fractional Bands: FRASMA centre line with FBM-scaled bands.

    Parameters
    ----------
    close : list[float]
        Close prices (index 0 = oldest).
    period : int
        Lookback period for FDI and base SMA speed (default 30, min 2).
    price_scale : float
        Price-to-working-space multiplier (default 1.0).

    Returns
    -------
    tuple of three list[float]
        (frasma, upper_band, lower_band), each of length len(close).
        Unprimed values are float('nan').
    """
    n = len(close)
    nan = float("nan")
    frasma_out = [nan] * n
    upper_out = [nan] * n
    lower_out = [nan] * n

    if period < 2 or n < period + 1:
        return frasma_out, upper_out, lower_out

    ln2 = math.log(2.0)
    log_denom = math.log(2.0 * (period - 1))
    pm1 = period - 1
    inv_period_sq = 1.0 / (period * period)
    p = float(price_scale)

    for pos in range(period, n):
        # --- FDI over window [pos-period .. pos] (period+1 values) ---
        win_start = pos - period
        price_max = close[win_start]
        price_min = close[win_start]
        for i in range(win_start + 1, pos + 1):
            v = close[i]
            if v > price_max:
                price_max = v
            if v < price_min:
                price_min = v

        price_range = price_max - price_min
        if price_range < 1e-10:
            fdi = 1.0
        else:
            # Normalise and compute path length over period segments
            # (period+1 points → period segments, but MQ4 uses period-1
            # segments: iteration 1..period-1)
            inv_range = 1.0 / price_range
            prev_norm = (close[win_start] - price_min) * inv_range
            length = 0.0
            for i in range(1, period):  # period-1 segments
                cur_norm = (close[win_start + i] - price_min) * inv_range
                diff = cur_norm - prev_norm
                length += math.sqrt(diff * diff + inv_period_sq)
                prev_norm = cur_norm
            if length > 0.0:
                fdi = 1.0 + (math.log(length) + ln2) / log_denom
            else:
                fdi = 1.0

        # --- Hurst exponent and adaptive speed ---
        hurst = 2.0 - fdi
        if hurst < 0.01:
            hurst = 0.01
        trail_dim = 1.0 / hurst
        beta = trail_dim / 2.0
        speed = max(int(round(period * beta)), 1)

        # --- FRASMA (SMA of *speed* most recent closes) ---
        if pos + 1 < speed:
            continue
        sma_start = pos + 1 - speed
        total = 0.0
        for i in range(sma_start, pos + 1):
            total += close[i]
        frasma_val = total / speed
        frasma_out[pos] = frasma_val

        # --- Deviation in scaled space over last *period* closes ---
        dev_start = pos + 1 - period
        frasma_scaled = p * frasma_val
        sq_sum = 0.0
        for i in range(dev_start, pos + 1):
            res = p * close[i] - frasma_scaled
            sq_sum += res * res
        deviation = math.sqrt(sq_sum / period)

        # --- FBM band offset: 2 * sigma^(2H) ---
        two_h = 2.0 * hurst
        band_offset = 2.0 * math.pow(deviation, two_h)
        upper_out[pos] = (frasma_scaled + band_offset) / p
        lower_out[pos] = (frasma_scaled - band_offset) / p

    return frasma_out, upper_out, lower_out


if __name__ == "__main__":
    from test_testdata import INPUT_CLOSE

    combos = [
        (5, 1.0),
        (10, 1.0),
        (20, 1.0),
        (30, 1.0),
        (50, 1.0),
        (80, 1.0),
        (30, 100.0),
        (30, 10000.0),
    ]

    for period, ps in combos:
        frasma, upper, lower = fractional_bands(INPUT_CLOSE, period=period, price_scale=ps)
        tag = f"P{period}_S{int(ps) if ps == int(ps) else ps}"
        print(f"\n# period={period}, price_scale={ps}")
        print(f"EXPECTED_FRASMA_{tag} = [")
        for i, v in enumerate(frasma):
            end = ",\n" if (i + 1) % 10 == 0 or i == len(frasma) - 1 else ", "
            if math.isnan(v):
                print("float('nan')", end=end)
            else:
                print(f"{v:.15f}", end=end)
        print("]")
        print(f"EXPECTED_UPPER_{tag} = [")
        for i, v in enumerate(upper):
            end = ",\n" if (i + 1) % 10 == 0 or i == len(upper) - 1 else ", "
            if math.isnan(v):
                print("float('nan')", end=end)
            else:
                print(f"{v:.15f}", end=end)
        print("]")
        print(f"EXPECTED_LOWER_{tag} = [")
        for i, v in enumerate(lower):
            end = ",\n" if (i + 1) % 10 == 0 or i == len(lower) - 1 else ", "
            if math.isnan(v):
                print("float('nan')", end=end)
            else:
                print(f"{v:.15f}", end=end)
        print("]")
