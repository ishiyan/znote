# Summary

William Blau's "Double Smoothed-Stochastics" (TASC, January 1991) introduces the DS-stochastic — an improvement on Lane's stochastic oscillator that applies double exponential moving average smoothing to both numerator and denominator.

## Key Concepts

- **DS-stochastic Formula**: DS(a,y,z) = 100 * Ez(Ey(C - La)) / Ez(Ey(Ha - La))
- Generalizes Lane's stochastic by replacing simple summation with double EMA smoothing
- Parameters: a = lookback days for HH/LL, y = first EMA period, z = second EMA period
- Maps price to 0-100 scale with overbought/oversold regions
- **HLC Index**: Special case DS(1,y,z) — compares close to single-day high/low range; fast response

## Relationship to Lane's Stochastic

- Lane's %K uses raw (C - LL5)/(HH5 - LL5)
- Lane's %D smooths with 3-day summation
- DS-stochastic replaces this with double EMA for superior noise reduction

## Examples

- DS(2,3,15) on Compaq: crossover with 3-day MA gives timely buy/sell signals through trending and consolidation
- DS(1,5,15) on S&P 500: detected August 1987 divergence warning before October crash
