# JARSX — Adaptive RSX

## Principle

Wraps JXRSX with automatic length selection based on volatility regime detection. Uses the log-ratio of long-term to short-term volatility with soft squashing to adapt RSX length dynamically.

When short-term volatility is high relative to long-term (trending/volatile market), the adaptive length shortens for faster response. When the market is calm relative to history, the length increases for more smoothing.

## Mathematical Formulas

Given a price series $p$ with parameters $\text{LoLen}$, $\text{HiLen}$, and $\text{Sensitivity}$:

**Absolute price changes:**

$$\text{value1}[i] = |p[i] - p[i-1]|$$

**Long-term volatility (≈100-bar SMA of |changes|):**

$$\text{avg1}[i] = \text{SMA}(\text{value1},\; \min(i, 99) + 1)$$

**Short-term volatility (≈10-bar SMA of |changes|):**

$$\text{avg2}[i] = \text{SMA}(\text{value1},\; \min(i, 9) + 1)$$

**Log ratio of volatilities:**

$$\text{value2}[i] = \text{Sensitivity} \cdot \ln\!\left(\frac{\varepsilon + \text{avg1}[i]}{\varepsilon + \text{avg2}[i]}\right)$$

where $\varepsilon = 0.001$.

**Soft squash to $(-1, +1)$:**

$$\text{value3}[i] = \frac{\text{value2}[i]}{1 + |\text{value2}[i]|}$$

**Adaptive length mapping to $[\text{LoLen}, \text{HiLen}]$:**

$$L[i] = \text{LoLen} + (\text{HiLen} - \text{LoLen}) \cdot \frac{1 + \text{value3}[i]}{2}$$

## Algorithm

1. Compute absolute price changes for each bar.
2. For each bar, compute long-term (~100-bar) and short-term (~10-bar) moving averages of those changes.
3. Take the log-ratio of long-term to short-term volatility, scaled by Sensitivity.
4. Squash the ratio into (-1, +1) using the soft-squash function $x/(1+|x|)$.
5. Map the squashed value linearly to the range [LoLen, HiLen].
6. Pass the resulting adaptive length series to JXRSX.

## Flow Diagram

```
prices
  │
  ▼
|price[i] - price[i-1]| ──► value1
  │
  ├──► SMA(value1, ~100) ──► avg1 (long-term vol)
  │
  ├──► SMA(value1, ~10)  ──► avg2 (short-term vol)
  │
  ▼
Sensitivity * ln((eps + avg1) / (eps + avg2)) ──► value2
  │
  ▼
value2 / (1 + |value2|) ──► value3  (squashed to (-1,+1))
  │
  ▼
LoLen + (HiLen - LoLen) * (1 + value3) / 2 ──► adaptive_length
  │
  ▼
JXRSX(prices, adaptive_length) ──► JARSX output
```

## Pseudocode

```
function JARSX(prices, LoLen, HiLen, Sensitivity):
    eps = 0.001
    n = length(prices)
    value1[0] = 0
    for i = 1 to n-1:
        value1[i] = |prices[i] - prices[i-1]|

    adaptive_length = array(n)
    for i = 0 to n-1:
        window_long = min(i, 99) + 1
        window_short = min(i, 9) + 1
        avg1 = SMA(value1[0..i], window_long)
        avg2 = SMA(value1[0..i], window_short)
        value2 = Sensitivity * ln((eps + avg1) / (eps + avg2))
        value3 = value2 / (1 + |value2|)
        adaptive_length[i] = LoLen + (HiLen - LoLen) * (1 + value3) / 2

    return JXRSX(prices, adaptive_length)
```

## Variable Mapping

| Variable | Description |
|----------|-------------|
| `value1` | Absolute bar-to-bar price change |
| `avg1` | Long-term volatility (~100-bar SMA of value1) |
| `avg2` | Short-term volatility (~10-bar SMA of value1) |
| `value2` | Sensitivity-scaled log-ratio of avg1/avg2 |
| `value3` | Soft-squashed value2, range (-1, +1) |
| `adaptive_length` | Dynamic RSX length mapped to [LoLen, HiLen] |
| `eps` | Small constant (0.001) to avoid log(0) |
| `LoLen` | Minimum adaptive length (fastest response) |
| `HiLen` | Maximum adaptive length (most smoothing) |
| `Sensitivity` | Controls how aggressively length adapts |
