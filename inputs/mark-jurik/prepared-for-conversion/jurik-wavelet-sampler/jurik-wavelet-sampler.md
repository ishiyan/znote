# WAV — Jurik Wavelet Sampler

## Principle

WAV (originally "WaveSamp") is a multi-resolution historical data sampler that compresses a time series into a small number of representative columns for use in forecasting systems. It applies the principle of wavelet-like sampling: fast cycles are sampled frequently (short lookbacks), slow cycles are sampled infrequently (long lookbacks), with a low-pass filter applied at each scale to prevent aliasing.

The key insight is that market oscillations at different frequencies require different sampling rates. WAV achieves efficient compression by:
1. Defining geometrically-spaced sample points (the n-M table)
2. Applying a centered SMA filter of width (M+1) at each sample point to capture surrounding price action
3. Producing one output column per scale

For example, INDEX=15 uses 15 columns to represent 139 bars of history — a 9:1 compression ratio.

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `prices` | array | — | — | Input price series |
| `index` | int | 12 | 1–18 | Number of output columns (higher = more history, more columns) |
| `mode` | int | 1 | 1–3 | 1=Standard, 2=Detrend, 3=Detrend+Normalize |

## The n-M Table

Each row defines a scale: `n` is the lookback distance, `M` is the number of additional filter points (filter width = M+1).

| Row | n | M | Filter Width | Max Distance (Dead Zone) |
|-----|---|---|---|---|
| 1 | 1 | 0 | 1 | 1 |
| 2 | 2 | 0 | 1 | 2 |
| 3 | 3 | 0 | 1 | 3 |
| 4 | 4 | 0 | 1 | 4 |
| 5 | 5 | 0 | 1 | 5 |
| 6 | 7 | 2 | 3 | 8 |
| 7 | 10 | 2 | 3 | 11 |
| 8 | 14 | 4 | 5 | 16 |
| 9 | 19 | 4 | 5 | 21 |
| 10 | 26 | 8 | 9 | 30 |
| 11 | 35 | 8 | 9 | 39 |
| 12 | 48 | 16 | 17 | 56 |
| 13 | 65 | 16 | 17 | 73 |
| 14 | 90 | 32 | 33 | 106 |
| 15 | 123 | 32 | 33 | 139 |
| 16 | 172 | 64 | 65 | 204 |
| 17 | 237 | 64 | 65 | 269 |
| 18 | 334 | 128 | 129 | 398 |

The INDEX parameter selects how many rows (columns) to use: INDEX=k outputs k columns using rows 1..k.

## Mathematical Formulas

### Standard Mode (Mode 1)

For each scale $(n, M)$ in the table, the output at bar $i$ is:

**If $M = 0$ (no filtering):**

$$\text{WAV}_k[i] = p[i - n]$$

**If $M > 0$ (centered SMA filter):**

$$\text{WAV}_k[i] = \frac{1}{M+1} \sum_{j=-M/2}^{M/2} p[i - n + j]$$

This is a simple moving average of $(M+1)$ prices centered at lag $n$.

**Dead zone:** The first $n + M/2$ bars produce no output (NaN) because insufficient history exists.

### Detrend Mode (Mode 2)

Produces INDEX+1 columns. The first column is the detrended price series (long-term trend removed). The remaining INDEX columns are WAV Standard applied to the detrended series.

Available for INDEX ≥ 10 (recommended ≥ 12).

### Detrend + Normalize Mode (Mode 3)

Produces INDEX+1 columns. The first column is detrended and volatility-normalized. The remaining INDEX columns are WAV Standard applied to this preprocessed series.

Available for INDEX ≥ 12 (recommended ≥ 14).

## Algorithm (Standard Mode)

1. Define the n-M table (18 rows).
2. Select the first `index` rows from the table.
3. For each selected row (n, M):
   a. Compute dead_zone = n + M/2.
   b. For each bar i ≥ dead_zone:
      - If M=0: output = price[i - n]
      - If M>0: output = mean of price[i-n-M/2 .. i-n+M/2] (inclusive, M+1 points)
   c. Bars before dead_zone: output = NaN.

## Flow Diagram

```
Input price series (length L)
  │
  ▼
For each scale k = 1..INDEX:
  │
  ├── Read (n_k, M_k) from n-M table
  │
  ├── dead_zone = n_k + M_k / 2
  │
  ├── For each bar i >= dead_zone:
  │     │
  │     ├── M_k = 0 ? ──► output[i, k] = price[i - n_k]
  │     │
  │     └── M_k > 0 ? ──► output[i, k] = SMA(price, M_k+1, centered at lag n_k)
  │
  └── Output column k
  
Result: L × INDEX matrix (NaN in dead zones)
```

## Variable Mapping

| Variable | Description |
|----------|-------------|
| `n` | Lookback distance (temporal center of the filter) |
| `M` | Number of additional filter points (0 = no filter) |
| `index` / INDEX | Number of output columns (selects rows from n-M table) |
| `mode` / MODE | Processing mode (1=Standard, 2=Detrend, 3=Detrend+Normalize) |
| `dead_zone` | n + M/2: minimum bars of history needed for each scale |
| `max_distance` | Same as dead_zone: farthest sample point into history |

## Notes

- The n-M table entries approximately double every 2 rows, creating a geometric (octave-like) spacing — the "wavelet" analogy.
- The filter is a flat (rectangular) kernel — simple unweighted average of M+1 points. No triangular or Gaussian windowing.
- Standard mode was verified against authentic DLL output from Excel 97 (test_WAV.xlsx). All values match to machine precision.
- Modes 2 and 3 (Detrend, Normalize) have not been reverse-engineered from test data yet. Only Mode 1 is implemented.
- The algorithm is embarrassingly simple — the "proprietary" aspect was primarily the geometric sampling schedule (the n-M table) and the insight that this achieves efficient multi-resolution representation.

## References

- Jurik, M. (1992). "The Care and Feeding of a Neural Network." *Futures*, October 1992.
- Jurik Research (1994–2002). WAV 2.0 User's Guide. Jurik Research & Consulting.
- Original DLL: `JRS_32.DLL`, functions `WAV()` and `WAVCols()`.
