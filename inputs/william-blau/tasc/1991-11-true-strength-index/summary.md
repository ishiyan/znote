# Summary

William Blau's "True Strength Index" (TASC, November 1991) introduces the TSI as a double-smoothed momentum oscillator that improves on the RSI by applying exponential moving averages directly to the "whole momentum" rather than segregating up/down components.

## Key Concepts

- **TSI Formula**: TSI(y,z) = 100 * Ez(Ey(Mtm)) / Ez(Ey(|Mtm|))
- **Divergence Indicator (DI)**: The numerator alone, DI = Ez(Ey(Mtm)), serves as a standalone trading tool
- **Double smoothing**: First EMA (long duration) extracts slowly-varying signal from noise; second EMA (short duration) strips remaining high-frequency noise with minimal lag
- **Relationship to RSI**: TSI is identical to RSI except for a scale factor when single-smoothed; double smoothing dramatically reduces noise while preserving turning points

## Design Philosophy

- Momentum = Close - Close[1] captures direction, magnitude, and turning points
- Single smoothing lifts momentum away from zero but preserves choppiness
- Second (shorter) smoothing removes noise with little additional lag
- Triple smoothing possible if lag remains acceptable
- Always a tradeoff: smoothness vs. lag — different for each trader

## Practical Use

- TSI provides overbought/oversold levels, divergence detection, and trendline analysis
- DI with 3-bar moving average crossover forms a simple trading system
- Applicable to any timeframe: intraday, daily, weekly, monthly
