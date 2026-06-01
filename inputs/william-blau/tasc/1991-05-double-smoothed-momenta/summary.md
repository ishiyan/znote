# Summary

William Blau's "Double-Smoothed Momenta" (TASC, May 1991) introduces the DM indicator — a generalized family of double-smoothed momentum oscillators that map price into a 0-100 range using exponential moving averages of exponential moving averages.

## Key Concepts

- **DM Formula**: DM(a,y,z) = 100 * Ez(Ey(C - LCa)) / Ez(Ey(HCa - LCa))
- Maps closing prices to a bounded 0-100 scale (overbought/oversold)
- Uses highest/lowest close over a lookback of "a" days
- Double EMA smoothing reduces false signals while preserving timeliness

## Relationship to RSI

- RSI is a special case: RSI_z = DM(2,1,z) — single-smoothed with a=2
- Double-smoothed RSI: DRSI(y,z) = DM(2,y,z) — adds second smoothing layer
- Both RSI formulations (100-100/(1+RS) and 100*a/(a+b)) are algebraically equivalent

## Practical Examples

- DM(12,8,1): compared favorably with 9-day RSI, slow stochastic, Williams %R on S&P 500
- DM(2,5,25): detected August 1987 divergence and October 1987 crash warning via support break at level 40
