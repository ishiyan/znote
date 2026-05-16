# Fractal Dimension Index (FDI)

**Mnemonic:** `fdi`  
**Original author:** iliko (arcsin5@netscape.net), v1.0 February 2007  
**Reference MQ4:** `fractal_dimension.mq4`  
**Source:** [https://www.mql5.com/en/code/7758](https://www.mql5.com/en/code/7758)  
**Master reference implementation:** `fractal_dimension.py`

## Overview

The Fractal Dimension Index (FDI) measures the fractal dimension of a price
time series using a normalized path-length method. It quantifies the
"roughness" of the price curve, providing a volatility measure that is
independent of price direction.

**Interpretation:**

| FDI Value | Market Regime | Meaning |
|-----------|---------------|---------|
| ≈ 1.0 | Trending | Smooth, well-defined trend; low noise |
| ≈ 1.5 | Random | Pure Brownian motion; no exploitable pattern |
| ≈ 2.0 | Erratic | Highly volatile, space-filling; extreme noise |

## Parameters

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| `period` | int | 30 | ≥ 2 | Lookback period N. Number of price segments used to compute path length. Window size is N+1 prices. |

## Input

- `prices`: array of float, length ≥ period + 1. Typically close prices. Index 0 = oldest bar.

## Output

- Single array of float, same length as input.
- First `period` values are NaN (insufficient data).
- Subsequent values: fractal dimension estimate ∈ [1.0, 2.0] approximately.

## Mathematical Foundation

The algorithm estimates the fractal (graph) dimension of the price curve by
computing the normalized path length over N periods and applying the
Hausdorff–Besicovitch dimension formula.

### Step 1: Extract and normalize prices to [0, 1]

For each bar at position `pos` (where pos ≥ period), extract a window of
N+1 prices: `prices[pos - period]` through `prices[pos]` inclusive.

Normalize each price in the window:

$$\text{norm}_i = \frac{\text{price}_i - \text{price}_{\min}}{\text{price}_{\max} - \text{price}_{\min}}$$

If price_max = price_min (flat market), FDI = 1.0 (straight line).

### Step 2: Compute path length

$$L = \sum_{i=1}^{N} \sqrt{\left(\text{norm}_i - \text{norm}_{i-1}\right)^2 + \frac{1}{N^2}}$$

The term $1/N^2$ represents the squared horizontal step between bars
(the x-axis is implicitly divided into N equal segments of width 1/N).

### Step 3: Compute fractal dimension

$$D_f = 1 + \frac{\ln(L) + \ln(2)}{\ln(2N)}$$

Where:
- $\ln(2)$ accounts for the normalization factor
- $\ln(2N)$ is the denominator scaling

## Algorithm (pseudocode)

```
function fractal_dimension(prices, period):
    n = length(prices)
    fdi = array of NaN, length n
    log_2n = ln(2 * period)
    ln2 = ln(2)
    inv_n_sq = 1 / (period * period)

    for pos = period to n-1:
        window = prices[pos - period .. pos]  (inclusive, N+1 points)
        price_max = max(window)
        price_min = min(window)
        price_range = price_max - price_min

        if price_range < 1e-10:
            fdi[pos] = 1.0
            continue

        prior_norm = (prices[pos - period] - price_min) / price_range
        length = 0.0

        for k = (pos - period + 1) to pos:
            curr_norm = (prices[k] - price_min) / price_range
            diff = curr_norm - prior_norm
            length += sqrt(diff * diff + inv_n_sq)
            prior_norm = curr_norm

        fdi[pos] = 1.0 + (ln(length) + ln2) / log_2n

    return fdi
```

## Notes on MQ4 Original

The original MQ4 by iliko has a subtle difference in loop bounds:
- It iterates from `iteration=0` to `iteration < period-1` (i.e., `period - 1` iterations)
- It skips `iteration == 0` for the length calculation
- This yields `period - 2` path segments

This Python implementation uses N segments from N+1 points, which is the
mathematically standard formulation. The corrected version by Poton (FGDI,
see `fractal_graph_dimension_indicator/`) uses N-1 segments with denominator
`ln(2*(N-1))`.

## Test Parameter Combinations

| # | period | What it tests |
|---|--------|---------------|
| 1 | 5 | Very short lookback — responsive but noisy |
| 2 | 10 | Short lookback |
| 3 | 15 | Medium-short lookback |
| 4 | 20 | Medium lookback |
| 5 | 30 | Default period |
| 6 | 50 | Long lookback |
| 7 | 80 | Very long lookback |
| 8 | 120 | Extended lookback — nearly half the data |

## Dependencies

None. This is a standalone indicator.

## References

- iliko (2007). Fractal Dimension indicator for MetaTrader 4. MQL5 Code Base #7758.
- Mandelbrot, B. B. (1997). *Fractals and Scaling in Finance*. Springer.
- Falconer, K. (2003). *Fractal Geometry*. Wiley. Chapter on box-counting dimension.
- Poton, J.-P. (2008). "Comments on some existing fractal-related tools." Fractal Finance blog.
