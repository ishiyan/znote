# JCCX — Jurik Commodity Channel Index

## Principle

JCCX is a JMA-based replacement for the classic Commodity Channel Index (CCI). Instead of using Simple Moving Averages, it uses two Jurik Moving Averages:

- **Fast JMA** (period=4, phase=0) — tracks price closely
- **Slow JMA** (period=Len, phase=0) — represents the adaptive trend

The difference between fast and slow JMA is normalized by 1.5× the Mean Absolute Deviation (MAD) of that difference series, producing an oscillator that indicates overbought/oversold conditions relative to the adaptive trend.

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `prices` | array | — | — | Input price series (e.g. closing prices) |
| `length` | int | 20 | 5–100 | Period for the slow JMA |

## Mathematical Formulas

**Difference series (fast minus slow JMA):**

$$\text{diff}_i = \text{JMA}(p,\; 4,\; 0)_i - \text{JMA}(p,\; \text{Len},\; 0)_i$$

**Mean Absolute Deviation over adaptive window:**

$$\text{MAD}_i = \frac{1}{W} \sum_{j=i-W+1}^{i} |\text{diff}_j|, \quad W = \min(i+1,\; 3 \cdot \text{Len})$$

**Normalization factor:**

$$\text{md}_i = 1.5 \cdot \text{MAD}_i$$

**Final output:**

$$\text{JCCX}_i = \begin{cases} \dfrac{\text{diff}_i}{\text{md}_i} & \text{if } \text{md}_i \ge 0.00001 \\ 0 & \text{otherwise} \end{cases}$$

## Algorithm

1. Compute fast JMA of price with period=4, phase=0.
2. Compute slow JMA of price with period=Len, phase=0.
3. For each bar $i$: $\text{diff}_i = \text{fastJMA}_i - \text{slowJMA}_i$.
4. For each bar $i$: compute MAD of $|\text{diff}|$ over the last $\min(i+1, 3 \cdot \text{Len})$ bars.
5. Set $\text{md}_i = 1.5 \cdot \text{MAD}_i$.
6. If $\text{md}_i < 0.00001$, output 0; otherwise output $\text{diff}_i / \text{md}_i$.

## Flow Diagram

```
Price Series
  │
  ├──► JMA(period=4, phase=0) ──► fastJMA
  │
  ├──► JMA(period=Len, phase=0) ──► slowJMA
  │
  ▼
diff = fastJMA - slowJMA
  │
  ▼
MAD = mean(|diff|) over min(bar+1, 3*Len) bars
  │
  ▼
md = 1.5 × MAD
  │
  ▼
JCCX = diff / md   (or 0 if md < 0.00001)
```

## Dependency

JCCX depends on **JMA (Jurik Moving Average)** — a triple-stage adaptive filter:
1. Adaptive volatility estimation via 128-element sorted list
2. Adaptive first-order EMA with bandwidth controlled by volatility
3. Two-pole IIR filter with phase (overshoot) control

The JMA implementation is inlined in the Python file to keep the package self-contained.

## Variable Mapping

| Variable | Description |
|----------|-------------|
| `prices` | Input price series |
| `length` / `Len` | Slow JMA period parameter |
| `fastJMA` | JMA(prices, period=4, phase=0) |
| `slowJMA` | JMA(prices, period=Len, phase=0) |
| `diff` | fastJMA − slowJMA |
| `W` | Lookback window: min(bar+1, 3×Len) |
| `MAD` | Mean absolute deviation of diff over W bars |
| `md` | 1.5 × MAD (normalization divisor) |
| `JCCX` | Final output (unbounded oscillator) |

## Notes

- Output is **unbounded** (not clamped to any range). Values beyond ±1 indicate strong overbought/oversold conditions.
- The 1.5× MAD normalization mirrors classic CCI's use of 0.015 × mean deviation.
- The MAD window grows from 1 to $3 \times \text{Len}$ bars during warmup, providing a self-calibrating normalization.
- JMA warmup is ~30 bars; JCCX output is valid once both JMAs are initialized and sufficient MAD history exists.
