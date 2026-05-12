# Jack K. Hutson — Technical Indicators Research

## Background

Jack K. Hutson was an editor for *Technical Analysis of Stocks and Commodities* (TASC) magazine. He developed the TRIX indicator in the early 1980s.

---

## 1. TRIX Indicator

### Overview

- **Full name:** Triple Exponential Average (TRIX)
- **Developer:** Jack K. Hutson
- **Year introduced:** Early 1980s
- **Original publication:** *Technical Analysis of Stocks and Commodities* (TASC) magazine [UNVERIFIED: exact issue/year — commonly cited as 1983]
- **Purpose:** A momentum oscillator designed to filter out insignificant price movements by displaying the percent rate of change of a triple exponentially smoothed moving average.

### Formula

The TRIX is computed in four steps:

```
1. EMA1 = EMA(Close, n)           — Single-smoothed EMA
2. EMA2 = EMA(EMA1, n)            — Double-smoothed EMA
3. EMA3 = EMA(EMA2, n)            — Triple-smoothed EMA
4. TRIX = ((EMA3_today - EMA3_yesterday) / EMA3_yesterday) × 100
```

Where:
- `n` = period (default: 15)
- Signal line = 9-period EMA of TRIX

### Standard Parameters

| Parameter | Default Value |
|-----------|--------------|
| Triple EMA period | 15 |
| Signal line period | 9 |

### Intended Use

- **Trend identification:** TRIX positive = triple-smoothed EMA rising (bullish); TRIX negative = falling (bearish)
- **Signal line crossovers:** TRIX crossing above/below its 9-period EMA signal line
- **Centerline crossovers:** Crossing zero indicates shift in momentum bias
- **Divergences:** Bullish/bearish divergences between TRIX and price can foreshadow reversals
- **Noise filtering:** The triple smoothing eliminates minor price fluctuations, focusing only on significant trend changes

### Comparison to MACD

| Feature | TRIX (15,9) | MACD (12,26,9) |
|---------|-------------|----------------|
| Type | Momentum oscillator | Momentum oscillator |
| Zero line | Yes | Yes |
| Signal line | 9-day EMA | 9-day EMA |
| Smoothness | Smoother (less whipsaws) | More responsive |
| Lag | Higher | Lower |
| Construction | Rate of change of triple EMA | Difference of two EMAs |

TRIX is smoother than MACD due to triple exponential smoothing, producing fewer false signals but with greater lag.

---

## 2. Other Indicators by Jack K. Hutson

### [UNVERIFIED] Contributions

Jack Hutson is primarily known for the TRIX indicator. As editor of TASC, he was instrumental in popularizing many technical analysis concepts, but TRIX is his signature creation. No other specific indicators have been reliably attributed to him as inventor in publicly available sources.

[UNVERIFIED] Some sources suggest he contributed to discussions of:
- Smoothing techniques in technical analysis
- Applications of exponential moving averages

---

## 3. Place in Technical Analysis History

- TRIX belongs to the family of **momentum oscillators** alongside MACD, ROC (Rate of Change), and PPO (Percentage Price Oscillator)
- It was one of the early indicators to apply **multiple exponential smoothing** to reduce noise — a concept that influenced later indicator design
- Published during the "golden age" of technical indicator development (late 1970s–1980s) when TASC magazine was a primary vehicle for new indicator research
- The triple-smoothing approach influenced subsequent work on smoothed oscillators and noise-reduction techniques in quantitative trading

---

## 4. Original Article Reference

- **Author:** Jack K. Hutson
- **Publication:** *Technical Analysis of Stocks and Commodities* (TASC)
- **Approximate date:** Early 1980s (commonly cited as 1983) [UNVERIFIED: exact month/issue]
- **Title:** [UNVERIFIED — original article title not confirmed from available sources]

---

## Sources

1. StockCharts ChartSchool — TRIX documentation (https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/trix)
2. General technical analysis literature references to Jack Hutson as TRIX creator and TASC editor
