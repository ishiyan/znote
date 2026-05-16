# Fractal Dispersion

**Mnemonic:** `fdisp`  
**Author:** Jean-Philippe Poton (jppoton@yahoo.com), v1.1 April 2010  
**Reference MQ4:** `fractal_dispersion.mq4` (MTF_FractalDispersion11)  
**Source:** [https://www.mql5.com/en/code/9604](https://www.mql5.com/en/code/9604)  
**Blog:** [http://fractalfinance.blogspot.com/](http://fractalfinance.blogspot.com/)  
**Master reference implementation:** `fractal_dispersion.py`

## Overview

Fractal Dispersion measures the weighted standard deviation of Fractal Graph
Dimension (FGDI) values across multiple observation scales, centered on a
reference FDI. It quantifies how "consistent" the fractal dimension is: low
dispersion means the market looks similar at all scales (self-similar), high
dispersion means scale-dependent behavior.

In the original MQ4, MetaTrader provides multi-timeframe data internally via
`iCustom(Symbol(), TIMEFRAME, "FGDI", ...)`. This standalone version accepts
pre-computed FDI arrays directly, decoupling from the MT4 mechanism.

## Parameters

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| `fdi_arrays` | list[list[float]] | — | length >= 2 | Pre-computed FDI arrays, ordered shortest to longest timeframe. Last = reference. All must have same length. |
| `weights` | list[int] | all 1 | each >= 0, sum >= 2 | Weight per FDI array. |

## Input

- `fdi_arrays`: list of FDI arrays (e.g., from `fractal_graph_dimension_indicator` at different periods). All arrays must be the same length. The caller is responsible for alignment/resampling.

## Output

- Single array of float, same length as input arrays.
- Values are NaN where any input FDI is NaN at that position.
- Valid values = 10 * sigma (weighted sample standard deviation).

## Mathematical Foundation

### Step 1: Reference FDI

The reference is the last array in `fdi_arrays` (longest timeframe / slowest scale).

### Step 2: Weighted squared deviations

For each shorter-timeframe array $i$ (all except last):

$$\text{dev}_i = w_i \cdot (FDI_i[\text{pos}] - FDI_{\text{ref}}[\text{pos}])^2$$

### Step 3: Sample standard deviation

$$\sigma = \sqrt{\frac{\sum_i \text{dev}_i}{W - 1}}$$

where $W = \sum_i w_i$ is the total weight.

### Step 4: Output scaling

$$\text{output}[\text{pos}] = 10 \cdot \sigma$$

The factor of 10 scales the dispersion into a more readable range (typically 0–5 for normal markets).

## Algorithm Flow

```mermaid
flowchart TD
    A["Input: fdi_arrays (N arrays), weights"] --> B[Reference = fdi_arrays[last]]
    B --> C[For each bar pos]
    C --> D[Get ref_fdi = reference[pos]]
    D --> E["For each shorter array i: dev += weight_i * (fdi_i[pos] - ref_fdi)^2"]
    E --> F["sigma = sqrt(dev_sum / (total_weight - 1))"]
    F --> G["output[pos] = 10 * sigma"]
    G --> C
```

## MQ4 Timeframe Mapping

The original MQ4 uses these timeframes with index scaling:

| Timeframe | Minutes | Scale factor (from daily) |
|-----------|---------|--------------------------|
| M5 | 5 | ×288 |
| M15 | 15 | ×96 |
| M30 | 30 | ×48 |
| H1 | 60 | ×24 |
| H4 | 240 | ×6 |
| D1 | 1440 | ×1 (reference) |

Default weights in MQ4: M5=1, M15=1, M30=1, H1=1, H4=0, D1=0.

## Test Strategy

Since this standalone version accepts pre-computed FDI arrays, we simulate
"multi-timeframe" by computing FGDI on the same INPUT_CLOSE at different
periods (shorter period ≈ faster timeframe). Test data includes the
intermediate FDI arrays as inputs so conversion agents can verify the full
pipeline.

## Test Parameter Combinations

| # | Arrays | Periods | Weights | What it tests |
|---|--------|---------|---------|---------------|
| C1 | 3 | [5,10,20] | [1,1,1] | Equal weights, small periods |
| C2 | 4 | [5,10,20,40] | [1,1,1,1] | 4 arrays, equal weights |
| C3 | 3 | [5,10,30] | [2,1,1] | Unequal weights |
| C4 | 4 | [5,15,30,60] | [1,2,1,1] | Mixed, heavier middle |
| C5 | 2 | [10,30] | [1,1] | Minimal (2 arrays) |
| C6 | 3 | [20,50,80] | [1,1,1] | Large periods |
| C7 | 4 | [5,10,20,30] | [1,1,2,1] | Heavy third weight |
| C8 | 3 | [10,30,50] | [3,1,1] | Heavy first weight |

## Dependencies

- Requires pre-computed FDI arrays (e.g., from `fractal_graph_dimension_indicator`).
  The dispersion function itself is standalone.

## References

- Poton, J.-P. (2010). Multi-Timeframe Fractal Dispersion. MQL5 Code Base #9604.
- Poton, J.-P. (2009). "Fractal dimensions...And a Fractal Graph Dimension Indicator." Fractal Finance blog.
- Mandelbrot, B. B. (1997). *Fractals and Scaling in Finance*. Springer.
