# Fractal Graph Dimension Indicator (FGDI)

**Mnemonic:** `fgdi`  
**Author:** Jean-Philippe Poton (jppoton@yahoo.com)  
**Reference MQ4:** `fractal_graph_dimension_indicator.mq4`  
**Source:** [https://www.mql5.com/en/code/8844](https://www.mql5.com/en/code/8844)  
**Blog:** [http://fractalfinance.blogspot.com/2009/04/fractal-dimensionsand-fractal-graph.html](http://fractalfinance.blogspot.com/2009/04/fractal-dimensionsand-fractal-graph.html)  
**Master reference implementation:** `fractal_graph_dimension_indicator.py`

## Overview

The FGDI is Poton's corrected and enhanced version of iliko's Fractal Dimension
Index (FDI). It fixes two bugs in the original and adds **standard deviation
bands** around the estimated dimension, providing a confidence interval for
the fractal dimension estimate.

**Interpretation:**

| FDI Value | Market Regime | Meaning |
|-----------|---------------|---------|
| ≈ 1.0 | Trending | Smooth, well-defined trend; low noise |
| ≈ 1.5 | Random | Pure Brownian motion; no exploitable pattern |
| ≈ 2.0 | Erratic | Highly volatile, space-filling; extreme noise |

## Corrections from the original FDI

1. **Loop boundary:** uses `iteration <= period-1` (inclusive), yielding N-1
   path segments (vs N-2 in the original iliko code)
2. **Denominator:** uses $\ln(2(N-1))$ instead of $\ln(2N)$

## Parameters

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| `period` | int | 30 | >= 2 | Lookback period N. Window is N prices (N-1 segments). |

## Input

- `close`: array of float, length >= period. Typically close prices. Index 0 = oldest bar.

## Output

`FGDIResult` named tuple with four arrays, each the same length as input:

| Field | Description |
|-------|-------------|
| `fdi` | Fractal graph dimension values. First `period - 1` values are NaN. |
| `upper_band` | fdi + stddev |
| `lower_band` | fdi - stddev |
| `stddev` | Standard deviation of the dimension estimate (from segment variance) |

Conversion agents should map `FGDIResult` to a Band-style struct with the same
four fields.

## Mathematical Foundation

### Step 1: Extract and normalize prices to [0, 1]

For each bar at position `pos` (where pos >= period - 1), extract a window of
N prices: `close[pos - period + 1]` through `close[pos]` inclusive.

Normalize each price:

$$\text{norm}_i = \frac{\text{price}_i - \text{price}_{\min}}{\text{price}_{\max} - \text{price}_{\min}}$$

If price_max = price_min (flat market), FDI = 1.0, stddev = 0.

### Step 2: Compute path segments

$$\delta_i = \sqrt{\left(\text{norm}_i - \text{norm}_{i-1}\right)^2 + \frac{1}{N^2}} \quad \text{for } i = 1, \ldots, N-1$$

### Step 3: Path length

$$L = \sum_{i=1}^{N-1} \delta_i$$

### Step 4: Fractal dimension

$$D_f = 1 + \frac{\ln(L) + \ln(2)}{\ln(2(N-1))}$$

### Step 5: Standard deviation of the estimate

The variance measures how uniform the path segments are. Uniform segments
(straight line) give zero variance; jagged paths give high variance.

$$\bar{\delta} = \frac{L}{N-1}$$

$$\text{variance} = \frac{\sum_{i=1}^{N-1}(\delta_i - \bar{\delta})^2}{L^2 \cdot [\ln(2(N-1))]^2}$$

$$\text{stddev} = \sqrt{\text{variance}}$$

### Step 6: Bands

$$\text{upper} = D_f + \text{stddev}$$
$$\text{lower} = D_f - \text{stddev}$$

## Algorithm Flow

```mermaid
flowchart TD
    A[Input: close array, period N] --> B[For each bar pos >= N-1]
    B --> C["Extract window: pos-N+1 .. pos (N prices)"]
    C --> D[Find priceMax, priceMin]
    D --> E[Normalize prices to 0,1]
    E --> F["Compute path segments delta_i (N-1 segments)"]
    F --> G[Sum path length L]
    G --> H["FDI = 1 + (ln L + ln 2) / ln(2*(N-1))"]
    H --> I["mean_delta = L / (N-1)"]
    I --> J["variance = sum((delta_i - mean_delta)^2) / (L^2 * ln(2*(N-1))^2)"]
    J --> K[stddev = sqrt(variance)]
    K --> L["Upper = FDI + stddev, Lower = FDI - stddev"]
    L --> B
```

## Color Coding (MQ4 display)

- **FDI > random_line** → BLUE (erratic/volatile)
- **FDI < random_line** → RED (trending)
- Same color logic applies to the bands (split at random_line boundary)

Note: `random_line` (default 1.5) is a display-only parameter in the MQ4.
It does not affect the computed values and is not included in the Python interface.

## Variable Names (from MQ4 source)

| Variable | Description |
|----------|-------------|
| `e_period` | Lookback period $N$ |
| `g_period_minus_1` | $N-1$, loop upper bound and denominator factor |
| `length` | Cumulative path length $L$ |
| `fdi` | Computed fractal graph dimension |
| `mean` | Mean segment length $L/(N-1)$ |
| `sum` | Accumulator for segment variance |
| `variance` | Variance of the dimension estimate |
| `stddev` | Standard deviation (band width) |
| `ExtOutputBufferUp/Down` | FDI line (split by color at random_line) |
| `UpBufferUp/Down` | Upper band (split by color) |
| `DownBufferUp/Down` | Lower band (split by color) |

## Differences from FDI (fractal_dimension)

| Aspect | FDI (iliko) | FGDI (Poton) |
|--------|-------------|--------------|
| Loop bound | `iteration < period-1` (N-2 segments) | `iteration <= period-1` (N-1 segments) |
| Denominator | $\ln(2N)$ | $\ln(2(N-1))$ |
| Window | N+1 prices, N segments | N prices, N-1 segments |
| Output | Single FDI array | 4 arrays: fdi, upper, lower, stddev |
| Bands | None | ± stddev from segment variance |
| MQL5 code | #7758 | #8844 |

## Test Parameter Combinations

| # | period | NaN count | Valid values | What it tests |
|---|--------|-----------|--------------|---------------|
| 1 | 5 | 4 | 248 | Very short lookback |
| 2 | 10 | 9 | 243 | Short lookback |
| 3 | 15 | 14 | 238 | Medium-short lookback |
| 4 | 20 | 19 | 233 | Medium lookback |
| 5 | 30 | 29 | 223 | Default period |
| 6 | 50 | 49 | 203 | Long lookback |
| 7 | 80 | 79 | 173 | Very long lookback |
| 8 | 120 | 119 | 133 | Extended lookback |

## Dependencies

None. This is a standalone indicator.

## References

- Poton, J.-P. (2009). "Fractal dimensions...And a Fractal Graph Dimension Indicator." Fractal Finance blog.
- Poton, J.-P. (2009). FGDI indicator for MetaTrader 4. MQL5 Code Base #8844.
- iliko (2007). Fractal Dimension indicator. MQL5 Code Base #7758.
- Mandelbrot, B. B. (1997). *Fractals and Scaling in Finance*. Springer.
- Falconer, K. (2003). *Fractal Geometry*. Wiley.
