# JVELCFB — Jurik Fractal-Adaptive Zero-Lag Velocity

## Principle

JVELCFB combines three components:

1. **CFB (Composite Fractal Behavior)** — Estimates the dominant market cycle period by analyzing trend efficiency at multiple scales using cascading residual-probability weighting.
2. **Stochastic normalization** — Maps the CFB output to a depth range [LoDepth, HiDepth] using a running min/max stochastic.
3. **VEL core (JXVEL)** — Two-stage velocity: per-bar weighted least-squares slope (Stage 1) + adaptive smoother (Stage 2, fixed period=3).

Short detected cycles → shallow depth (faster velocity response). Long detected cycles → deeper depth (more smoothing).

Unlike JAVEL (which uses volatility-regime detection for adaptation), JVELCFB uses **fractal cycle detection** — a fundamentally different adaptation mechanism based on dominant cycle period rather than volatility ratio.

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `prices` | array | — | — | Input price series (e.g. closing prices) |
| `lo_depth` | int | 5 | 2–20 | Minimum VEL depth (fastest response) |
| `hi_depth` | int | 30 | 20–100 | Maximum VEL depth (most smoothing) |
| `fractal_type` | int | 1 | 1–4 | CFB fractal type (controls max scale depth: 24/48/96/192) |
| `smooth` | int | 10 | 3–50 | CFB efficiency ratio smoothing window (SMA) |

## Mathematical Formulas

### CFB — Composite Fractal Behavior

**Single-scale efficiency ratio** for depth $d$:

$$E_d[b] = \frac{|d \cdot p[b] - \sum_{i=0}^{d-1} p[b-i-1]|}{\sum_{i=0}^{d-1} (d-i) \cdot |p[b-i] - p[b-i-1]|}$$

**Scale sets by fractal type:**
- Type 1: {2, 3, 4, 6, 8, 12, 16, 24}
- Type 2: {2, 3, 4, 6, 8, 12, 16, 24, 32, 48}
- Type 3: {2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96}
- Type 4: {2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192}

**Smoothed efficiency:** $\bar{E}_d = \text{SMA}(E_d, \text{smooth})$

**Cascading residual-probability weighting** (even and odd scales processed separately, largest first):

$$w_k = \text{residual} \cdot \bar{E}_k, \quad \text{residual} \leftarrow \text{residual} \cdot (1 - w_k)$$

**Weighted-mean dominant period:**

$$\text{CFB}[b] = \frac{\sum_k w_k^2 \cdot \text{scale}_k}{\sum_k w_k^2}$$

### Stochastic Normalization

Running (cumulative, never-reset) min/max of CFB:

$$\text{sr}[i] = \frac{\text{CFB}[i] - \text{cfbmin}[i]}{\text{cfbmax}[i] - \text{cfbmin}[i]}$$

If $\text{cfbmax} = \text{cfbmin}$: $\text{sr} = 0.5$.

**Adaptive depth:**

$$D[i] = \lfloor \text{LoDepth} + \text{sr}[i] \cdot (\text{HiDepth} - \text{LoDepth}) \rfloor$$

### VEL Core (Stage 1 + Stage 2)

Same as JAVEL's VEL core — see `jurik-adaptive-zero-lag-velocity.md` for full Stage 1 (per-bar WLS slope) and Stage 2 (adaptive smoother with period=3) formulas.

## Flow Diagram

```
prices
  │
  ├──────────────────────────────────────────► Stage 1: Per-bar WLS slope
  │                                                     ▲
  ▼                                                     │
JCFB(fractal_type, smooth)                              │
  │                                                     │
  ▼                                                     │
cfb series                                              │
  │                                                     │
  ▼                                                     │
Running min/max stochastic normalization ──► sr ∈ [0,1] │
  │                                                     │
  ▼                                                     │
LoDepth + sr * (HiDepth - LoDepth) ──► depth_series ────┘
                                                        │
                                                        ▼
                                           Stage 2: Adaptive smoother (period=3)
                                                        │
                                                        ▼
                                                   JVELCFB output
```

## Variable Mapping

| Variable | Description |
|----------|-------------|
| `cfb` | CFB output: estimated dominant cycle period per bar |
| `cfbmin` | Cumulative minimum of CFB (never resets) |
| `cfbmax` | Cumulative maximum of CFB (never resets) |
| `sr` | Stochastic ratio: normalized CFB position in [0, 1] |
| `depth_series` | Adaptive VEL depth mapped to [LoDepth, HiDepth] |
| `fractal_type` | Selects scale set (1–4) for CFB analysis |
| `smooth` | SMA window for efficiency ratio smoothing |
| `lo_depth` | Minimum depth (used when CFB at running min) |
| `hi_depth` | Maximum depth (used when CFB at running max) |

## Notes

- The CFB stochastic uses **cumulative** min/max (never resets), so early bars may see rapid depth changes as the range establishes itself.
- Stage 2 uses a fixed period=3 (hardcoded in the original), matching JAVEL's behavior.
- CFB warmup depends on the largest scale in the fractal type (e.g., type 1 needs ~24 bars, type 4 needs ~192 bars).
- The output is unbounded velocity (rate of price change), same as JAVEL.
