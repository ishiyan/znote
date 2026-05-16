# Fractal Adaptive Simple Moving Average v2 (FRASMAv2)

**Mnemonic:** `frasma2`  
**Author:** Jean-Philippe Poton (jppoton@yahoo.com), Copyright 2008  
**Reference MQ4:** `fractal_adamtive_simple_moving_average_2.mq4`  
**Source:** [https://www.mql5.com/en/code/8866](https://www.mql5.com/en/code/8866)

## Overview

FRASMAv2 is an updated version of the Fractal Adaptive Simple Moving Average.
It differs from the original FRASMA in two ways:

1. **Corrected FDI formula** -- uses $\ln(2(N-1))$ in the denominator instead
   of $\ln(2N)$, matching the Fractal Graph Dimension Indicator (FGDI)
   correction.
2. **N-1 path segments** -- the loop iterates over $N$ points
   ($0 \ldots N-1$ inclusive), yielding $N-1$ segments, compared to FRASMA v1
   which yields $N-2$ segments.

The original MQ4 source includes `shift` and `normal_speed` parameters.
`shift` is always 0 and is excluded from the interface. `normal_speed` is
hardcoded at 20.

## Parameters

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| `period` | int | 30 | $\geq 2$ | Lookback period for FDI computation |

## Input

- `close`: array of float, length >= period + 1. Typically close prices. Index 0 = oldest bar.

## Output

- Single array of float, same length as input.
- First `period` values are NaN (insufficient data for FDI).
- Subsequent values: the adaptive SMA.

## Mathematical Foundation

### Step 1: Compute FDI (corrected FGDI formula)

Normalize prices in the lookback window and compute path length $L$ over
$N-1$ segments:

$$L = \sum_{i=1}^{N-1} \sqrt{\left(\text{norm}_i - \text{norm}_{i-1}\right)^2 + \frac{1}{N^2}}$$

$$D_f = 1 + \frac{\ln(L) + \ln(2)}{\ln\!\big(2(N-1)\big)}$$

### Step 2: Hurst exponent

$$H = 2 - D_f$$

### Step 3: Trail dimension

$$D_{\text{trail}} = \frac{1}{H} = \frac{1}{2 - D_f}$$

### Step 4: Alpha factor

$$\alpha = \frac{D_{\text{trail}}}{2}$$

### Step 5: Adaptive speed

$$\text{speed} = \max\!\left(1,\; \text{round}\!\left(20 \times \alpha\right)\right)$$

### Step 6: Output

$$\text{FRASMAv2}[i] = \text{SMA}(\text{close}, \text{speed})[i]$$

## Algorithm Flow

```mermaid
flowchart TD
    A[Input: close array, period N] --> B[For each bar pos >= N]
    B --> C[Extract window: pos-N+1 .. pos]
    C --> D[Find priceMax, priceMin]
    D --> E[Normalize prices to 0..1]
    E --> F["Compute path length L (N-1 segments)"]
    F --> G["FDI = 1 + (ln L + ln 2) / ln(2*(N-1))"]
    G --> H["trail_dim = 1 / (2 - FDI)"]
    H --> I[alpha = trail_dim / 2]
    I --> J["speed = max(1, round(20 * alpha))"]
    J --> K["Output[pos] = SMA(close, speed)"]
    K --> B
```

## Variable Names (from MQ4 source)

| Variable | Description |
|----------|-------------|
| `e_period` | Lookback period $N$ for FDI |
| `normal_speed` | Base SMA period before adaptation (hardcoded 20) |
| `shift` | Output buffer displacement (always 0, excluded) |
| `g_period_minus_1` | $N - 1$, used as loop bound and in denominator |
| `priceMax`, `priceMin` | Max/min price in the lookback window |
| `diff` | Normalized price at current step |
| `priorDiff` | Normalized price at previous step |
| `length` | Cumulative path length $L$ |
| `fdi` | Computed fractal dimension |
| `trail_dim` | Trail dimension $1/H$ |
| `alpha` | Scaling factor $D_{\text{trail}} / 2$ |
| `speed` | Adapted SMA period |
| `ExtOutputBuffer` | Output buffer (the adaptive SMA line) |
| `LOG_2` | Precomputed $\ln(2)$ constant |

## Differences from FRASMA v1

| Aspect | FRASMA v1 | FRASMAv2 |
|--------|-----------|----------|
| FDI denominator | $\ln(2N)$ | $\ln(2(N-1))$ |
| Loop bound | `iteration < g_period_minus_1` ($N-2$ segments) | `iteration <= g_period_minus_1` ($N-1$ segments) |
| Smoothing method | Exponential: $\alpha = e^{-4.6(D_f-1)}$ | SMA with adaptive window length |
| Shift parameter | absent | present (but always 0) |
| MQL5 code base | #8718 | #8866 |

## Test Data

8 parameter combinations: period = {5, 10, 15, 20, 30, 50, 80, 120}.
252 data points per output array.

## References

- Poton, J.-P. (2008). Fractal Adaptive Simple Moving Average v2 (FRASMAv2). MQL5 Code Base #8866.
- Poton, J.-P. (2009). "Speed of FRAMA -- Part 2: FRASMA." Fractal Finance blog.
- iliko (2007). Fractal Dimension indicator for MetaTrader 4. MQL5 Code Base #7758.
