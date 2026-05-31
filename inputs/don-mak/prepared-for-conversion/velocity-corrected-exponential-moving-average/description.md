# Velocity-Corrected Exponential Moving Average (VCEMA)

## Summary

A reduced-lag EMA that pre-corrects price by adding its polynomial velocity estimate before smoothing. This "correct first, smooth second" approach shifts the input signal forward in time, compensating for the EMA's inherent lag.

Distinct from Ehlers' Zero-Lag EMA (which uses error-correction feedback) — this uses Mak's polynomial fit derivative (PFD) for the velocity estimate.

## Source

- Don K. Mak, *Mathematical Techniques in Financial Market Trading* (2006), Chapter 4.1
- Called "Zero-Lag EMA" in the book, renamed here to avoid collision with Ehlers' method.

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| period | int | 6 | 2+ | EMA smoothing period |
| degree | int | 3 | 2–6 | Polynomial degree for velocity estimation (uses degree+1 raw price bars) |

## Formula

```
velocity       = PFD(price, degree, order=1, smoothing=0)
corrected_price = price + velocity
output         = EMA(corrected_price, period)
```

The velocity term estimates how fast price is moving and adds that to the current price, effectively "projecting" it one bar forward before smoothing.

## Output

| Field | Type | Description |
|-------|------|-------------|
| value | float | Lag-corrected smoothed price. NaN during priming. |

## Priming

First valid output at bar `degree` (need degree+1 prices for PFD). EMA initializes to the first corrected price.

## VCEMA vs MEMA

These two indicators share the same goal (reduce EMA lag using polynomial velocity correction) but differ in signal path:

| | VCEMA (this indicator) | MEMA |
|-|------------------------|------|
| Formula | `EMA(price + PFD(price))` | `EMA(price) + PFD(EMA(price))` |
| Signal path | Correct first, smooth after | Smooth first, correct after |
| Velocity source | Raw price (noisy) | EMA output (already smoothed) |

### Why the difference matters

On **linear data** (constant velocity): both produce identical results. The velocity estimate is the same regardless of whether it's computed from raw price or from EMA output (since EMA of a line is still a line, just shifted).

On **nonlinear/noisy real market data** they diverge:

- **VCEMA** estimates velocity from raw noisy price. The velocity term carries noise, which then gets partially (but not fully) suppressed by the subsequent EMA smoothing. This can cause overshooting near sharp reversals. Better for clean/pre-filtered data where raw velocity is meaningful.

- **MEMA** estimates velocity from the already-smoothed EMA curve. This gives a stable, low-noise velocity estimate. The correction is conservative and reliable. Better for noisy instruments or short periods.

**Practical guidance:** On typical market data, MEMA tends to be the safer choice. VCEMA can be slightly more responsive but at the cost of occasional overshoot artifacts.

## Trading Use

- **Fast trend following:** Tracks price more closely than plain EMA, giving earlier crossover signals.
- **When to prefer over MEMA:** On clean/pre-filtered data where raw price velocity is reliable.
- **When to prefer MEMA:** On noisy data where raw velocity estimates are unreliable.

## Implementation Notes

- Self-contained: embeds PFD coefficient computation and EMA logic.
- PFD is applied to raw price (no pre-smoothing), then EMA smooths the corrected signal.
- Uses only standard library math for portability.

## Naming

- Folder: `velocity-corrected-exponential-moving-average`
- Go package: `velocitycorrectedexponentialmovingaverage`
- Test data arrays: `EXPECTED_P{period}_D{degree}`
