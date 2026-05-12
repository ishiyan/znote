# JAVEL — Jurik Adaptive Zero-Lag Velocity

## Principle

JAVEL combines two components:

1. **VEL core (JXVEL)** — A two-stage velocity indicator: Stage 1 computes a per-bar weighted least-squares slope (local velocity), Stage 2 applies an adaptive smoother with velocity/position dynamics to reduce noise while preserving responsiveness.
2. **Adaptive depth selection** — A volatility regime detector that dynamically adjusts the WLS lookback depth based on the ratio of long-term to short-term price volatility.

When short-term volatility is high relative to long-term (trending/volatile market), the adaptive depth shortens for faster slope detection. When the market is calm, depth increases for smoother slopes.

Unlike JARSX (where the RSX core only reads `depth_series[0]`), **JXVEL reads the full depth series per bar**, so the adaptive depth genuinely affects Stage 1's behavior on every bar. The sensitivity parameter therefore has a real effect on the output.

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `prices` | array | — | — | Input price series (e.g. closing prices) |
| `lo_len` | int | 5 | 2–20 | Minimum adaptive depth (fastest response) |
| `hi_len` | int | 30 | 20–100 | Maximum adaptive depth (most smoothing) |
| `sensitivity` | float | 1.0 | 0.1–5.0 | Controls how aggressively depth adapts to volatility regime |
| `period` | float | 3.0 | 1–500 | Stage 2 smoother period (controls damping, buffer length, response) |

## Mathematical Formulas

### Adaptive Depth Computation

Given a price series $p$ with parameters $\text{LoLen}$, $\text{HiLen}$, and $\text{Sensitivity}$:

**Absolute price changes:**

$$\text{value1}[i] = |p[i] - p[i-1]|$$

**Long-term volatility (~100-bar SMA of |changes|):**

$$\text{avg1}[i] = \text{SMA}(\text{value1},\; \min(i, 99) + 1)$$

**Short-term volatility (~10-bar SMA of |changes|):**

$$\text{avg2}[i] = \text{SMA}(\text{value1},\; \min(i, 9) + 1)$$

**Log ratio of volatilities (scaled by sensitivity):**

$$\text{value2}[i] = \text{Sensitivity} \cdot \ln\!\left(\frac{\varepsilon + \text{avg1}[i]}{\varepsilon + \text{avg2}[i]}\right)$$

where $\varepsilon = 0.001$.

**Soft squash to $(-1, +1)$:**

$$\text{value3}[i] = \frac{\text{value2}[i]}{1 + |\text{value2}[i]|}$$

**Adaptive depth mapping to $[\text{LoLen}, \text{HiLen}]$:**

$$D[i] = \text{LoLen} + (\text{HiLen} - \text{LoLen}) \cdot \frac{1 + \text{value3}[i]}{2}$$

### Stage 1 — Per-Bar Weighted Least-Squares Slope

On each bar $b$, compute $D_b = \lceil D[b] \rceil$ and set $N_b = D_b + 1$:

$$S_1 = \frac{N_b(N_b+1)}{2}, \quad S_2 = \frac{S_1(2N_b+1)}{3}$$

$$\text{denom} = S_1^3 - S_2^2$$

$$\text{sum\_xw} = \sum_{i=0}^{D_b} p[b - i] \cdot (N_b - i)$$

$$\text{sum\_xw2} = \sum_{i=0}^{D_b} p[b - i] \cdot (N_b - i)^2$$

$$\text{slope}[b] = \frac{\text{sum\_xw2} \cdot S_1 - \text{sum\_xw} \cdot S_2}{\text{denom}}$$

### Stage 2 — Adaptive Smoother

**Constants derived from Period:**

$$\text{jrc03} = \min(500,\; \max(\varepsilon,\; \text{Period}))$$

$$\text{jrc06} = \max(31,\; \lceil 2 \cdot \text{Period} \rceil) \quad \text{(buffer usage length)}$$

$$\text{jrc07} = \min(30,\; \lceil \text{Period} \rceil) \quad \text{(initial lookback)}$$

$$\text{ema\_factor} = 1 - \exp\!\left(-\frac{\ln 4}{\text{Period} / 2}\right)$$

$$\text{damping} = 0.86 - \frac{0.55}{\sqrt{\text{jrc03}}}$$

**Per-bar update:**

1. Insert slope value into 1001-element circular buffer.
2. Compute linear regression over buffer (up to jrc06 elements).
3. Compute MAD from regression, scale by $1.2 \cdot (\text{jrc06}/\text{len})^{0.25}$.
4. Smooth MAD via EMA.
5. Prediction error: $\text{error} = \text{slope}[b] - \text{position}$.
6. Response: $\text{response} = 1 - \exp(-|\text{error}| / (\text{smoothed\_mad} \cdot \text{jrc03}))$.
7. Update velocity: $\text{velocity} = \text{response} \cdot \text{error} + \text{velocity} \cdot \text{damping}$.
8. Update position: $\text{position} \mathrel{+}= \text{velocity}$.

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
LoLen + (HiLen - LoLen) * (1 + value3) / 2 ──► adaptive_depth[bar]
  │
  ▼
┌─────────────────────────────────────────┐
│ Stage 1: Per-bar WLS slope              │
│   depth = ceil(adaptive_depth[bar])     │
│   N = depth + 1                         │
│   Compute S1, S2, denom                 │
│   Compute sum_xw, sum_xw2 over window  │
│   slope = (sum_xw2*S1 - sum_xw*S2)/den │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│ Stage 2: Adaptive smoother (Period)     │
│   1001-element circular buffer          │
│   Linear regression over buffer         │
│   MAD → response factor                 │
│   velocity += response * error          │
│   position += velocity                  │
└─────────────────────────────────────────┘
  │
  ▼
JAVEL output (velocity/position series)
```

## Variable Mapping

| Variable | Description |
|----------|-------------|
| `value1` | Absolute bar-to-bar price change |
| `avg1` | Long-term volatility (~100-bar SMA of value1) |
| `avg2` | Short-term volatility (~10-bar SMA of value1) |
| `value2` | Log-ratio of avg1/avg2, scaled by sensitivity |
| `value3` | Soft-squashed value2, range (-1, +1) |
| `adaptive_depth` | Dynamic WLS depth mapped to [LoLen, HiLen] |
| `eps` / `EPS` | Small constant (0.001) to avoid log(0) |
| `slope` | Stage 1 output: per-bar WLS velocity |
| `jrc03` | Clamped period for Stage 2 |
| `jrc06` | Buffer usage length: max(31, ceil(2*Period)) |
| `jrc07` | Initial lookback: min(30, ceil(Period)) |
| `ema_factor` | MAD smoothing factor |
| `damping` | Velocity damping coefficient |
| `velocity` | Stage 2 adaptive velocity accumulator |
| `position` | Stage 2 output position (smoothed slope) |
| `smoothed_mad` | EMA-smoothed mean absolute deviation |
| `response_factor` | Exponential response magnitude |

## Notes

- Unlike JARSX, JXVEL reads the full depth series per bar, so **sensitivity genuinely affects the output**.
- The output is unbounded (not [0, 100]) — it represents velocity (rate of price change).
- Positive values indicate upward momentum, negative values indicate downward momentum, near-zero values indicate consolidation.
- Stage 2's circular buffer is 1001 elements; buffer usage grows to `max(31, ceil(2*Period))`.
- Warmup: Stage 1 requires at least `ceil(depth)` bars of history per bar. Stage 2 initializes on its first valid input.
