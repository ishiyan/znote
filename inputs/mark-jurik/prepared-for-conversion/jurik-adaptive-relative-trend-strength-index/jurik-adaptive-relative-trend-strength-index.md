# JARSX — Jurik Adaptive Relative Trend Strength Index

## Principle

JARSX combines two components:

1. **RSX core** — A triple-cascaded lag-reduced EMA applied to momentum, producing a bounded [0, 100] oscillator similar to RSI but much smoother and with less lag.
2. **Adaptive length selection** — A volatility regime detector that computes a per-bar adaptive length based on the ratio of long-term to short-term price volatility.

When short-term volatility is high relative to long-term (trending/volatile market), the adaptive length shortens for faster response. When the market is calm relative to history, the length increases for more smoothing.

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `prices` | array | — | — | Input price series (e.g. closing prices) |
| `lo_len` | int | 5 | 2–20 | Minimum adaptive length (fastest response) |
| `hi_len` | int | 30 | 20–100 | Maximum adaptive length (most smoothing) |

## Implementation Note: Sensitivity Parameter Removed

The original decompiled WealthScript source (by Starlight) includes a `Sensitivity` parameter that scales the log-ratio of volatilities before squashing. However, **this parameter has no effect on the output** due to how the RSX core consumes the adaptive length:

- The RSX core (JXRSX) reads only `adaptive_length[0]` — the value at bar 0 — to compute its fixed EMA gain $K_g$.
- At bar 0, both the long-term and short-term volatility windows contain a single bar, making the log-ratio ≈ 0 regardless of the sensitivity scaling.
- Therefore `adaptive_length[0]` always equals the midpoint `(lo_len + hi_len) / 2`, and the sensitivity parameter cannot influence the output.

This is a design limitation of the JXRSX API (which only reads the first element of the length series). The sensitivity parameter is retained in the adaptive length computation conceptually but has been removed from this implementation to avoid confusion.

## Mathematical Formulas

### Adaptive Length Computation

Given a price series $p$ with parameters $\text{LoLen}$ and $\text{HiLen}$:

**Absolute price changes:**

$$\text{value1}[i] = |p[i] - p[i-1]|$$

**Long-term volatility (~100-bar SMA of |changes|):**

$$\text{avg1}[i] = \text{SMA}(\text{value1},\; \min(i, 99) + 1)$$

**Short-term volatility (~10-bar SMA of |changes|):**

$$\text{avg2}[i] = \text{SMA}(\text{value1},\; \min(i, 9) + 1)$$

**Log ratio of volatilities:**

$$\text{value2}[i] = \ln\!\left(\frac{\varepsilon + \text{avg1}[i]}{\varepsilon + \text{avg2}[i]}\right)$$

where $\varepsilon = 0.001$.

**Soft squash to $(-1, +1)$:**

$$\text{value3}[i] = \frac{\text{value2}[i]}{1 + |\text{value2}[i]|}$$

**Adaptive length mapping to $[\text{LoLen}, \text{HiLen}]$:**

$$L[i] = \text{LoLen} + (\text{HiLen} - \text{LoLen}) \cdot \frac{1 + \text{value3}[i]}{2}$$

### RSX Core (applied with $L = L[0]$)

The RSX core uses the adaptive length from bar 0 to set a fixed EMA gain:

$$K_g = \frac{3}{L_0 + 2}, \qquad c = 1 - K_g$$

Since at bar 0 both volatility windows are 1 bar, $\text{value2}[0] \approx 0$, $\text{value3}[0] \approx 0$, and therefore:

$$L_0 = \left\lfloor \frac{\text{LoLen} + \text{HiLen}}{2} \right\rfloor$$

For each bar $n$, momentum:

$$m_n = 100 \cdot (x_n - x_{n-1})$$

Each **lag-reduced EMA stage** (three cascaded, applied to both signed and absolute momentum):

$$a_n = c \cdot a_{n-1} + K_g \cdot u_n$$
$$b_n = K_g \cdot a_n + c \cdot b_{n-1}$$
$$y_n = 1.5 \cdot a_n - 0.5 \cdot b_n$$

Signal path: three cascaded stages on $m_n$ → numerator.
Denominator path: three cascaded stages on $|m_n|$ → denominator.

**Final output:**

$$\text{JARSX}_n = \text{clamp}\!\left(\left(\frac{\text{numerator}}{\text{denominator}} + 1\right) \times 50,\; 0,\; 100\right)$$

## Algorithm

1. Compute absolute bar-to-bar price changes.
2. For each bar, compute long-term (~100-bar) and short-term (~10-bar) SMAs of those changes.
3. Take the log-ratio of long-term to short-term volatility.
4. Squash the ratio into (-1, +1) using the soft-squash function $x/(1+|x|)$.
5. Map the squashed value linearly to [LoLen, HiLen].
6. Use the adaptive length from bar 0 to compute $K_g = 3/(L_0 + 2)$.
7. For each bar from 1 onward, compute momentum and pass through three cascaded lag-reduced EMA stages (signal and denominator paths).
8. After warmup, output clamped ratio.

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
ln((eps + avg1) / (eps + avg2)) ──► value2
  │
  ▼
value2 / (1 + |value2|) ──► value3  (squashed to (-1,+1))
  │
  ▼
LoLen + (HiLen - LoLen) * (1 + value3) / 2 ──► adaptive_length
  │
  ▼
L0 = int(adaptive_length[0])  ≈ (LoLen + HiLen) / 2
Kg = 3 / (L0 + 2),  c = 1 - Kg
  │
  ▼
For each bar:
  mom = 100 * (price[n] - price[n-1])
  │
  ├──► Signal path (3 cascaded lag-reduced EMAs on mom) ──► numerator
  │
  ├──► Denom path (3 cascaded lag-reduced EMAs on |mom|) ──► denominator
  │
  ▼
clamp((numerator / denominator + 1) * 50, 0, 100) ──► JARSX output
```

## Effective Behavior

Because only `adaptive_length[0]` determines $K_g$, and that value is always the midpoint of [LoLen, HiLen], the actual RSX smoothing length is:

| LoLen | HiLen | Effective L₀ | Kg |
|-------|-------|-------------|-----|
| 2 | 15 | 8 | 0.300 |
| 5 | 30 | 17 | 0.158 |
| 5 | 60 | 32 | 0.088 |
| 10 | 30 | 20 | 0.136 |
| 10 | 60 | 35 | 0.081 |

The two parameters effectively control a single thing: the midpoint length. The adaptive per-bar computation runs but its output is discarded beyond bar 0.

## Variable Mapping

| Variable | Description |
|----------|-------------|
| `value1` | Absolute bar-to-bar price change |
| `avg1` | Long-term volatility (~100-bar SMA of value1) |
| `avg2` | Short-term volatility (~10-bar SMA of value1) |
| `value2` | Log-ratio of avg1/avg2 |
| `value3` | Soft-squashed value2, range (-1, +1) |
| `adaptive_length` | Dynamic RSX length mapped to [LoLen, HiLen] |
| `eps` | Small constant (0.001) to avoid log(0) |
| `Kg` | EMA gain: 3/(L0+2) |
| `c` | EMA complement: 1-Kg |
| `sig1_a`, `sig1_b` | Signal stage 1 accumulators |
| `sig2_a`, `sig2_b` | Signal stage 2 accumulators |
| `sig3_a`, `sig3_b` | Signal stage 3 accumulators |
| `den1_a`, `den1_b` | Denominator stage 1 accumulators |
| `den2_a`, `den2_b` | Denominator stage 2 accumulators |
| `den3_a`, `den3_b` | Denominator stage 3 accumulators |
| `numerator` | Signal path output (signed) |
| `denominator` | Denominator path output (absolute) |

## Notes

- The RSX core uses a **fixed** $K_g$ computed from `adaptive_length[0]`. The per-bar adaptive length values are computed but only the initial value determines the EMA characteristics. This is faithful to the decompiled WealthScript source.
- Warmup period is `max(L0 - 1, 5)` bars. Output is NaN during warmup.
- Output range is [0, 100], where 50 = neutral, >50 = bullish momentum, <50 = bearish momentum.
