# JTPO — Jurik Turning Point Oscillator

## Principle

Measures trend strength and direction via **Spearman rank correlation** between price ranks and time positions over a rolling window.

- **+1** = perfect uptrend (prices monotonically increasing)
- **-1** = perfect downtrend (prices monotonically decreasing)
- **0** = no monotonic trend

The indicator detects when a trend is weakening (correlation moving toward zero from ±1) before price reverses, hence "turning point."

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `prices` | array | — | — | Input price series (e.g. closing prices) |
| `length` | int | 14 | 2–100 | Rolling window length for rank correlation |

## Mathematical Formulas

**Spearman's rank correlation coefficient:**

$$\rho = \frac{12}{n(n^2 - 1)} \sum_{i=1}^{n} \left( R_{\text{price}}(i) - \frac{n+1}{2} \right) \left( R_{\text{time}}(i) - \frac{n+1}{2} \right)$$

where $n$ = window length, $R_{\text{time}}(i)$ = original time position (1-based), $R_{\text{price}}(i)$ = price rank after sorting.

**Normalization factor:**

$$f_{18} = \frac{12}{n(n-1)(n+1)}$$

This ensures output is bounded to $[-1, +1]$.

**Tied-rank handling:**

When consecutive sorted prices are equal, their ranks are replaced by the average rank of the tied group:

$$R_{\text{avg}} = \frac{r_{\text{start}} + r_{\text{end}}}{2}$$

## Algorithm

1. Wait for `length` bars before producing output.
2. For each bar (once window is full):
   - Extract the rolling window of the last `length` prices.
   - Sort prices ascending, tracking original time positions.
   - Assign price ranks 1..n; for tied values, use the average rank.
   - Compute correlation sum: $\sum (R_{\text{price}}(i) - \text{midpoint}) \cdot (R_{\text{time}}(i) - \text{midpoint})$
   - Output = $f_{18} \times \text{sum}$

## Flow Diagram

```
prices (rolling window of length n)
  │
  ▼
Sort ascending, track original positions
  │
  ├──► arr2: original time positions (reordered by sort)
  │
  ├──► arr3: price ranks (1..n, averaged for ties)
  │
  ▼
Σ (arr3[i] - midpoint) × (arr2[i] - midpoint)
  │
  ▼
output = 12 / (n(n²-1)) × sum    ∈ [-1, +1]
```

## Variable Mapping

| Variable | Description |
|----------|-------------|
| `length` / `f48` | Window size parameter |
| `f18` | Normalization factor: 12 / (n(n-1)(n+1)) |
| `midpoint` / `f20` | Center rank: (n+1)/2 |
| `arr0` | Rolling price buffer |
| `arr1` | Working copy for sorting |
| `arr2` | Original time positions (tracked through sort) |
| `arr3` | Price ranks (adjusted for ties) |

## Notes

- Output range is [-1, +1], making it easy to interpret: magnitude indicates trend strength, sign indicates direction.
- Handles tied prices correctly via average rank assignment.
- Constant-price windows (all values equal) produce no output (NaN) since rank correlation is undefined.
- Computational complexity is O(n log n) per bar due to sorting (or O(n²) in the original decompiled selection sort).
