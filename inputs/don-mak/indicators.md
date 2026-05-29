# Don Mak — Implementable Trading Indicators

A consolidated catalogue of indicators, filters, and techniques derived from two books by Don K. Mak, suitable for algorithmic implementation.

## Sources

| Key | Book | Year |
|-----|------|------|
| **B1** | The Science of Financial Market Trading | 2003 |
| **B2** | Mathematical Techniques in Financial Market Trading | 2006 |

---

## Book 1: The Science of Financial Market Trading (2003)

### Low Pass Filters (Trending)

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| SMA | SMA | Simple Moving Average | Ch 5.1 |
| EMA | EMA | Exponential Moving Average | Ch 5.2 |
| AMA | AMA | Adaptive Moving Average (Jurik) | Ch 5.3 |

### High Pass Filters (Oscillators)

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| MOM | MOM | Momentum (2-point difference) | Ch 4.2 |
| PV | ParVel | Parabolic Velocity | Ch 6.1 |
| PA | ParAcc | Parabolic Acceleration | Ch 6.2 |
| CV | CubVel | Cubic Velocity | Ch 6.3 |
| CA | CubAcc | Cubic Acceleration | Ch 6.3 |

### Vertex Indicators (Turning Point Forecasters)

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| PVX | ParVtx | Parabolic Vertex | Ch 7.1 |
| CVX | CubVtx | Cubic Vertex | Ch 7.2 |

### Wavelet Band Pass Filters

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| WBH | WavHi | High Wavelet (periods 8–16) | Ch 9.1 |
| WBM | WavMid | Middle Wavelet (periods 16–32) | Ch 9.2 |
| WBL | WavLo | Low Wavelet (periods 32–64) | Ch 9.3 |
| WBV | WavVel | Combined Wavelet Velocity | Ch 9 |

### Multi-Timeframe / Forecasting

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| SKEMA | SkipEMA | Skipped EMA | Ch 10.1 |
| SKCV | SkipCubVel | Skipped Cubic Velocity | Ch 10.1 |
| F1V | Fcast1V | 1-Step Forecast (velocity) | Ch 10.2 |
| F1VA | Fcast1VA | 1-Step Forecast (vel+acc) | Ch 10.2 |

---

## Book 2: Mathematical Techniques in Financial Market Trading (2006)

### Low Pass Filters

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| BWF | Butter | Butterworth Filter (order 1–4) | Ch 3.3 |
| SINC2 | Sinc2 | Sinc Filter cutoff π/2 | Ch 3.4 |
| SINC4 | Sinc4 | Sinc Filter cutoff π/4 | Ch 3.5 |
| AEMA | AdaptEMA | Adaptive EMA (freq-dependent α) | Ch 3.6 |

### Reduced Lag Filters

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| ZEMA | ZeroLagEMA | Zero-Lag EMA | Ch 4.1 |
| MEMA | ModEMA | Modified EMA (EMA + cubic vel) | Ch 4.2 |
| MEMA-D | ModEMA-Skip | Modified EMA with Skip D | Ch 4.2.4 |

### Causal Wavelet (Mexican Hat) Filters

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| MHH | MexHatHi | Mexican Hat Wavelet a=1.483 | Ch 5.7 |
| MHM | MexHatMid | Mexican Hat Wavelet a=4.048 | Ch 5.7 |
| MHL | MexHatLo | Mexican Hat Wavelet a=15.97 | Ch 5.7 |

### Instantaneous Frequency

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| IF4 | InstFreq4 | Instantaneous Frequency (4 pt) | Ch 6.1 |
| IF5 | InstFreq5 | Instantaneous Frequency (5 pt) | Ch 6.5 |

### Higher-Order Velocity / Acceleration

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| QV | QuartVel | Quartic Velocity | Ch 8.4 |
| QA | QuartAcc | Quartic Acceleration | Ch 8.4 |
| QNV | QuintVel | Quintic Velocity | Ch 8.5 |
| QNA | QuintAcc | Quintic Acceleration | Ch 8.5 |
| SXV | SextVel | Sextic Velocity | Ch 8.6 |
| SXA | SextAcc | Sextic Acceleration | Ch 8.6 |

### Composite / Tactical

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| MACDL | MACDLine | MACD Line | Ch 10.2 |
| MACDS | MACDSig | MACD Signal Line | Ch 10.2 |
| MACDH | MACDHist | MACD Histogram | Ch 10.3 |
| DEMA | DblEMA | EMA of EMA (double smoothing) | Ch 10.4 |

---

## Implementation Priority

### Tier 1 — Core (unique to Mak, most novel)

1. **CV / CA** — Cubic Velocity / Acceleration
2. **PVX / CVX** — Parabolic / Cubic Vertex
3. **ZEMA / MEMA** — Zero-lag and Modified EMA
4. **MHH / MHM / MHL** — Mexican Hat Wavelet filters
5. **IF4 / IF5** — Instantaneous Frequency estimators
6. **SKEMA / SKCV** — Skipped convolution variants
7. **QV / QA / QNV / QNA / SXV / SXA** — Higher-order polynomial derivatives

### Tier 2 — Standard (well-known, include for completeness)

8. **SMA / EMA / BWF / SINC** — Classic low-pass filters
9. **MOM / MACD variants** — Standard momentum indicators

### Tier 3 — Experimental

10. **F1V / F1VA** — One-step-ahead forecasting
11. **AEMA** — Adaptive EMA with frequency-dependent smoothing
12. **WBH / WBM / WBL / WBV** — Sinc-based wavelet band-pass filters
