# JCCX — Jurik CCI eXtended

## Principle

JMA-based CCI. Uses two JMAs (fast period=4, slow period=Len) instead of SMAs. Normalizes by 1.5× MAD of the difference series.

## Mathematical Formulas

$$
\text{diff}_i = \text{JMA}(price, 4, 0)_i - \text{JMA}(price, \text{Len}, 0)_i
$$

$$
\text{MAD}_i = \frac{1}{W} \sum_{j=i-W+1}^{i} |\text{diff}_j|, \quad W = \min(i+1,\; 3 \cdot \text{Len})
$$

$$
\text{md}_i = 1.5 \cdot \text{MAD}_i
$$

$$
\text{JCCX}_i =
\begin{cases}
\dfrac{\text{diff}_i}{\text{md}_i} & \text{if } \text{md}_i \ge 0.00001 \\
0 & \text{otherwise}
\end{cases}
$$

## Algorithm

1. Compute fast JMA of price with period=4, phase=0.
2. Compute slow JMA of price with period=Len, phase=0.
3. For each bar $i$, compute $\text{diff}_i = \text{fastJMA}_i - \text{slowJMA}_i$.
4. For each bar $i$, compute $\text{MAD}_i$ as the mean of $|\text{diff}|$ over the last $\min(i+1, 3 \cdot \text{Len})$ bars.
5. Set $\text{md}_i = 1.5 \cdot \text{MAD}_i$.
6. If $\text{md}_i < 0.00001$, output 0; otherwise output $\text{diff}_i / \text{md}_i$.

## Flow Diagram

```mermaid
flowchart TD
    A[Price Series] --> B[JMA period=4, phase=0]
    A --> C[JMA period=Len, phase=0]
    B --> D[diff = fastJMA - slowJMA]
    C --> D
    D --> E[MAD over min(bar+1, 3*Len) bars]
    E --> F[md = 1.5 * MAD]
    F --> G{md >= 0.00001?}
    G -- Yes --> H[JCCX = diff / md]
    G -- No --> I[JCCX = 0]
```

## Pseudocode

```
fastJMA = JMA(price, period=4, phase=0)
slowJMA = JMA(price, period=Len, phase=0)
diff = fastJMA - slowJMA

for i = 0 to N-1:
    W = min(i + 1, 3 * Len)
    MAD = mean(|diff[i-W+1 .. i]|)
    md = 1.5 * MAD
    if md < 0.00001:
        JCCX[i] = 0
    else:
        JCCX[i] = diff[i] / md
```

## Variable Mapping Table

| Variable | Description | Source |
|----------|-------------|--------|
| `price` | Input price series | Parameter |
| `Len` | Slow JMA period | Parameter (default 20) |
| `fastJMA` | JMA(price, 4, 0) | Computed |
| `slowJMA` | JMA(price, Len, 0) | Computed |
| `diff` | fastJMA − slowJMA | Computed |
| `W` | Lookback window: min(bar+1, 3×Len) | Computed |
| `MAD` | Mean absolute deviation of diff over W bars | Computed |
| `md` | 1.5 × MAD | Computed |
| `JCCX` | Final output | Computed |
