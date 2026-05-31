# Modified Exponential Moving Average (MEMA / MEMA-D)

## Summary

A reduced-lag EMA that compensates for smoothing delay by adding the EMA's own velocity (estimated via polynomial fit derivative) back to its output. The Skip-D variant (MEMA-D) computes velocity on sub-sampled EMA history for multi-timeframe lag correction.

## Source

- Don K. Mak, *Mathematical Techniques in Financial Market Trading* (2006), Chapter 4.2
- MEMA: Section 4.2.1–4.2.3
- MEMA-D: Section 4.2.4

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| period | int | 6 | 2+ | EMA smoothing period |
| degree | int | 3 | 2–6 | Polynomial degree for the velocity correction term |
| skip | int | 1 | 1+ | Stride between points used for polynomial fit. 1 = standard MEMA (consecutive bars). >1 = MEMA-D (every skip-th bar). |

## Formula

```
ema_value = EMA(price, period)
velocity  = PFD(ema_history, degree, order=1, stride=skip)
output    = ema_value + velocity
```

Where PFD with stride means the (degree+1) points used for the polynomial fit are sampled at positions [0, skip, 2*skip, ..., degree*skip] from the EMA history buffer (0 = most recent).

## Output

| Field | Type | Description |
|-------|------|-------------|
| value | float | Lag-corrected smoothed price. NaN during priming. |

## Priming

First valid output requires `degree * skip + 1` EMA values in the buffer. Total NaN bars = `degree * skip` (since EMA starts producing values from bar 0).

## Trading Use

- **Trend following with reduced lag:** MEMA tracks price more closely than a plain EMA of the same period, making crossover signals earlier without sacrificing as much smoothness.
- **Skip-D for longer cycles:** Using skip=2 or skip=4 captures the velocity of longer-term price movement without needing a proportionally longer EMA period. Useful on intraday data where you want daily-scale lag correction.
- **Comparison:** Less lag than EMA, more lag than raw price. The "sweet spot" between noise and delay.

## MEMA vs VCEMA (Mak's "Zero-Lag EMA")

These two indicators share the same goal (reduce EMA lag using polynomial velocity correction) but differ in signal path:

| | MEMA (this indicator) | VCEMA |
|-|----------------------|-------|
| Formula | `EMA(price) + PFD(EMA(price))` | `EMA(price + PFD(price))` |
| Signal path | Smooth first, correct after | Correct first, smooth after |
| Velocity source | EMA output (already smoothed) | Raw price (noisy) |

### Why the difference matters

On **linear data** (constant velocity): both produce identical results. The velocity estimate is the same regardless of whether it's computed from raw price or from EMA output (since EMA of a line is still a line, just shifted).

On **nonlinear/noisy real market data** they diverge:

- **MEMA** estimates velocity from the already-smoothed EMA curve. This gives a stable, low-noise velocity estimate. The correction is conservative and reliable. Better for noisy instruments or short periods.

- **VCEMA** estimates velocity from raw noisy price. The velocity term itself carries noise, which then gets partially (but not fully) suppressed by the subsequent EMA smoothing. This can cause overshooting near sharp reversals. Better for clean/pre-filtered data where raw velocity is meaningful.

**Practical guidance:** On typical market data, MEMA tends to be the safer choice. VCEMA can be slightly more responsive but at the cost of occasional overshoot artifacts.

## Implementation Notes

- Self-contained: embeds EMA logic and PFD coefficient computation.
- Ring buffer stores all EMA values; PFD reads every skip-th entry.
- Coefficients precomputed once at initialization (fixed for given degree).
- Uses only standard library math for portability.

## Naming

- Folder: `modified-exponential-moving-average`
- Go package: `modifiedexponentialmovingaverage`
- Test data arrays: `EXPECTED_P{period}_D{degree}_SK{skip}`
