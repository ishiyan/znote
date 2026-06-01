# Summary

William Blau's "Trading With The True Strength Index" (TASC, May 1992) is a follow-up to his November 1991 introduction of the TSI. It explains the mechanism behind using double-smoothed momentum as a price proxy and demonstrates trading system applications.

## Key Concepts

- **TrSI Formula**: TrSI(y,z) = 100 * Ez(Ey(Mtm)) / Ez(Ey(|Mtm|))
- **Divergence Indicator (DI)**: The numerator alone, DI = Ez(Ey(Mtm)), serves as a scaled proxy for price
- **Large moving average momentum** (e.g., 300-day) closely replicates price shape; normalization introduces scale compression that creates divergences
- **Double smoothing** removes noise while preserving turning point timeliness

## Trading System Components

- **Slow TrSI** (e.g., 100,20 or 40,20): defines the trend direction
- **Fast TrSI** (e.g., 20,6): selects entry/exit points within the trend
- Divergences in the overbought/oversold regions of the fast index signal timely exits
- Alternative: use 20-day EMA of fast TrSI as trend instead of separate slow TrSI

## Suggested Parameters

- Fast: TrSI(20, 6)
- Slow: TrSI(40, 20)
- Slower: TrSI(80, 40)
