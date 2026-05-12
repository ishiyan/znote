# JVELCFB — VEL with CFB-Driven Depth

## Principle

Combines JVEL with JCFB. CFB estimates the dominant market cycle, then a stochastic normalization maps it to a depth range for VEL. Short cycles → shallow depth (fast response), long cycles → deep depth (more smoothing).

## Mathematical Formulas

1. **CFB series**: `cfb[i] = JCFB(Series, FractalType, Smooth)[i]`
2. **Running extremes** (cumulative, never reset):
   - `cfbmin[i] = min(cfb[0], cfb[1], ..., cfb[i])`
   - `cfbmax[i] = max(cfb[0], cfb[1], ..., cfb[i])`
3. **Stochastic normalization**:
   - `sr[i] = (cfb[i] - cfbmin[i]) / (cfbmax[i] - cfbmin[i])` if `cfbmax[i] != cfbmin[i]`, else `0.5`
4. **Adaptive depth**:
   - `adaptive_depth[i] = int(LoDepth + sr[i] * (HiDepth - LoDepth))`
5. **VEL output**:
   - `vl = JXVELaux3(JXVELaux1(Series, adaptive_depth), Period=3)`

## Algorithm

1. Compute full CFB series from input prices.
2. Initialize cfbmin = cfb[0], cfbmax = cfb[0].
3. For each bar i = 0..N-1:
   a. Update cfbmin = min(cfbmin, cfb[i]), cfbmax = max(cfbmax, cfb[i]).
   b. Compute sr = (cfb[i] - cfbmin) / (cfbmax - cfbmin), or 0.5 if flat.
   c. adaptive_depth[i] = int(LoDepth + sr * (HiDepth - LoDepth)).
4. Pass Series and adaptive_depth into JXVEL (aux1 with variable depth, then aux3 with Period=3).
5. Return final VEL output array.

## Flow Diagram

```
Series ──┬──────────────────────────────────► JXVELaux1(Series, depth_series) ──► JXVELaux3(_, 3) ──► Output
         │                                           ▲
         └──► JCFB(FractalType, Smooth) ──► cfb     │
                                              │      │
                                              ▼      │
                                     stochastic norm │
                                       sr ──► adaptive_depth
```

## Pseudocode

```
function JVELCFB(Series, LoDepth, HiDepth, FractalType, Smooth):
    cfb = JCFB(Series, FractalType, Smooth)
    cfbmin = cfb[0]
    cfbmax = cfb[0]
    depth_series = empty array of length N

    for i = 0 to N-1:
        cfbmin = min(cfbmin, cfb[i])
        cfbmax = max(cfbmax, cfb[i])
        if cfbmax == cfbmin:
            sr = 0.5
        else:
            sr = (cfb[i] - cfbmin) / (cfbmax - cfbmin)
        depth_series[i] = int(LoDepth + sr * (HiDepth - LoDepth))

    vel_stage1 = JXVELaux1(Series, depth_series)
    vel_out = JXVELaux3(vel_stage1, Period=3)
    return vel_out
```

## Variable Mapping

| Variable | Description |
|----------|-------------|
| `sr` | Stochastic ratio — normalized CFB position within its running range [0, 1] |
| `cfbmin` | Cumulative minimum of CFB series (never resets) |
| `cfbmax` | Cumulative maximum of CFB series (never resets) |
| `vl` | Final JVELCFB output — the adaptively-smoothed VEL line |
