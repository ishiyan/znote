# Summary

Andrey F. Zelinsky's MQL5 article (August 2011) implements all indicators from William Blau's book "Momentum, Direction, and Divergence" as MQL5 custom indicators for MetaTrader 5.

## Blau's Analysis Framework (4 phases)

1. Calculate raw indicator from price data (q bars)
2. Smooth with EMA (periods r, s, u) — reduces noise, preserves turning points
3. Normalize to [-100, +100] — enables overbought/oversold interpretation
4. Add signal line (EMA period ul) — signals trend end/reversal via crossover

## Indicator Groups Implemented

1. **Momentum-based**: Mtm, TSI, Ergodic Oscillator
2. **Stochastic-based**: TStoch, TStochI, TS_Stochastic
3. **Stochastic Momentum-based**: SM, SMI, SM_Stochastic
4. **Mean Deviation-based**: MDI, Ergodic_MDI
5. **MACD-based**: MACD, Ergodic_MACD
6. **Candlestick Momentum-based**: CMtm, CMI, CSI, Ergodic_CMI, Ergodic_CSI
7. **High-Low Momentum-based**: HLM, DTI, Ergodic_DTI

## Key Implementation Details

- Uses modified `ExponentialMAOnBufferWB()` that accepts period=1 (no smoothing)
- Default parameters: q=2, r=20, s=5, u=3 (signal line ul=3)
- All indicators support configurable price type and display in separate window
- 22 MQL5 source files total (21 indicators + 1 library include)
