# William Blau — Implementable Indicators & Utilities

Based on: *Momentum, Direction, and Divergence* (1995), 5 TASC articles (1991–1993),
MQL5 implementation by Zelinsky (2011), and research materials.

---

## Core Utility: Double/Triple EMA Smoothing

All Blau indicators share one building block:

```
DEMA(x, r, s)    = EMA(EMA(x, r), s)
TEMA(x, r, s, u) = EMA(EMA(EMA(x, r), s), u)
```

Convention: period = 1 means no smoothing (passthrough).

---

## Group 1: Momentum-Based

### 1.1 Momentum (Mtm)

```
mtm(price, q) = price - price[q-1]
Mtm(price, q, r, s, u) = TEMA(mtm(price, q), r, s, u)
```

- **Parameters**: q=2, r=20, s=5, u=3
- **Use**: Smoothed first derivative of price; reproduces price shape

### 1.2 True Strength Index (TSI)

```
TSI(price, q, r, s, u) = 100 * TEMA(mtm, r, s, u) / TEMA(|mtm|, r, s, u)
```

- **Parameters**: q=2, r=25, s=13, u=1 (classic); or r=20, s=5, u=3
- **Range**: [-100, +100]
- **Levels**: ±25 overbought/oversold

### 1.3 Divergence Indicator (DI)

TSI numerator standalone — Blau's personal primary tool:

```
DI(price, q, r, s, u) = TEMA(mtm(price, q), r, s, u)
```

- **Use**: Divergence detection, trendlines, crossover with 3-bar SMA

### 1.4 Ergodic Oscillator (TSI-based)

```
Ergodic = TSI(price, q, r, s, u)
Signal  = EMA(Ergodic, ul)
```

- **Parameters**: ul = last significant smoothing period (e.g., 5)
- **Levels**: ±25

---

## Group 2: Stochastic-Based

### 2.1 DS-Stochastic (Double-Smoothed Stochastic)

```
DS(q, r, s) = 100 * EMA(EMA(close - LL(q), r), s) / EMA(EMA(HH(q) - LL(q), r), s)
```

- **Parameters**: q=5, r=7, s=3 (or q=2, r=3, s=15)
- **Range**: [0, 100]
- **Signal**: 3-day SMA crossover

### 2.2 Smoothed Stochastic (unnormalized)

```
TStoch(price, q, r, s, u) = TEMA(price - LL(q), r, s, u)
```

### 2.3 Stochastic Index (normalized)

```
TStochI(price, q, r, s, u) = 100 * TEMA(price - LL(q), r, s, u) / TEMA(HH(q) - LL(q), r, s, u)
```

- **Range**: [0, 100]

### 2.4 HLC Index (one-bar DS-Stochastic)

```
HLC(1, y, z) = 100 * EMA(EMA(C - L, y), z) / EMA(EMA(H - L, y), z)
```

- **Properties**: Very fast; single-bar close position; gap-immune

---

## Group 3: Stochastic Momentum-Based

### 3.1 Stochastic Momentum (SM)

```
sm(price, q) = price - 0.5 * (HH(q) + LL(q))
SM(price, q, r, s, u) = TEMA(sm(price, q), r, s, u)
```

- **Properties**: Bipolar; measures distance from midpoint of range

### 3.2 Stochastic Momentum Index (SMI)

```
SMI(q, r, s, u) = 100 * TEMA(sm, r, s, u) / (0.5 * TEMA(HH(q) - LL(q), r, s, u))
```

- **Parameters**: q=13, r=25, s=2, u=1 (basic); q=2, r=20, s=20 (two-day)
- **Range**: [-100, +100]
- **Levels**: ±40

### 3.3 One-Day Stochastic (Sentiment Indicator)

```
SM(1) = close - 0.5 * (high + low)
SMI(1, r, s, u) = 100 * TEMA(SM(1), r, s, u) / (0.5 * TEMA(H - L, r, s, u))
```

- **Properties**: Gap-immune; detects whether closes favor highs or lows; sentiment/trend ID
- **Parameters**: r=100, s=20 (slow trend); r=40, s=20 (faster)

### 3.4 Stochastic Momentum Oscillator (Ergodic)

```
Ergodic = SMI(q, r, s, u)
Signal  = EMA(Ergodic, ul)
```

---

## Group 4: Detrending / Mean Deviation

### 4.1 Mean Deviation Index (MDI)

```
md(price, q) = price - EMA(price, q)
MDI(price, q, r, s, u) = 100 * TEMA(md, r, s, u) / TEMA(|md|, r, s, u)
```

- **Parameters**: q=20, r=20, s=5, u=3
- **Range**: [-100, +100]
- **Properties**: Measures deviation from trend; approximates MACD when q >> s

### 4.2 Ergodic MDI Oscillator

```
Ergodic = MDI(price, q, r, s, u)
Signal  = EMA(Ergodic, ul)
```

---

## Group 5: MACD-Based

### 5.1 MACD (Blau-style, normalized)

```
macd(price, q1, q2) = EMA(price, q1) - EMA(price, q2)
MACD_I(price, q1, q2, r, s, u) = 100 * TEMA(macd, r, s, u) / TEMA(|macd|, r, s, u)
```

- **Parameters**: q1=12, q2=26, r=20, s=5, u=3
- **Range**: [-100, +100]

### 5.2 Ergodic MACD Oscillator

```
Ergodic = MACD_I(price, q1, q2, r, s, u)
Signal  = EMA(Ergodic, ul)
```

---

## Group 6: Candlestick Momentum

### 6.1 Candlestick Momentum (CMtm)

```
cmtm = close - open
CMtm(r, s, u) = TEMA(cmtm, r, s, u)
```

- **Properties**: Bipolar; immune to inter-bar gaps

### 6.2 Candlestick Momentum Index (CMI)

```
CMI(r, s, u) = 100 * TEMA(cmtm, r, s, u) / TEMA(|cmtm|, r, s, u)
```

- **Parameters**: r=20, s=5, u=3
- **Range**: [-100, +100]
- **Properties**: TSI-format using intra-bar momentum

### 6.3 Candlestick Strength Index (CSI)

```
CSI(r, s, u) = 100 * TEMA(close - low, r, s, u) / [TEMA(close - low, r, s, u) + TEMA(high - close, r, s, u)]
```

- **Alternative**: `= 100 * TEMA(close - low, r, s, u) / TEMA(high - low, r, s, u)`
- **Parameters**: r=32, s=32, u=1
- **Range**: [0, 100]
- **Properties**: RSI-format for intra-bar close position

### 6.4 Ergodic CMI / CSI Oscillators

Same ergodic pattern with signal line.

---

## Group 7: Directional Trending (High-Low Momentum)

### 7.1 High-Low Momentum (HLM)

```
HMU = max(high - high[1], 0)
LMD = max(low[1] - low, 0)
HLM = HMU - LMD
```

- **Properties**: Composite momentum from bar extremes; cumulative sum = "virtual close"

### 7.2 Directional Trend Index (DTI)

```
DTI(r, s, u) = 100 * TEMA(HLM, r, s, u) / TEMA(|HLM|, r, s, u)
```

- **Parameters**: r=20, s=5, u=3 (or r=25, s=13)
- **Range**: [-100, +100]

### 7.3 Ergodic DTI Oscillator

```
Ergodic = DTI(r, s, u)
Signal  = EMA(Ergodic, ul)
```

---

## Group 8: Tick Volume Indicator (TVI)

### 8.1 TVI

```
TVI(r, s) = 100 * [DEMA(upticks, r, s) - DEMA(downticks, r, s)] / [DEMA(upticks, r, s) + DEMA(downticks, r, s)]
```

- **Parameters**: r=12, s=12 (or r=25, s=13)
- **Range**: [-100, +100]
- **Properties**: Volume-based; gap-immune; proxy for intraday direction
- **Note**: Requires tick data (uptick/downtick counts per bar)

---

## Group 9: Trade Filters

### 9.1 Nonambiguous Trend Filter (_Trade)

Generic pattern applied to any normalized indicator `X`:

```
X_Trade = X   when (X > 0 AND X is rising) OR (X < 0 AND X is falling)
X_Trade = 0   otherwise
```

Implementations:
- **TSI_Trade(price, r, s, u)** — Ch.8 — Parameters: r=32, s=13, u=3
- **SMI_Trade(q, r, s, u)** — Ch.9 — Parameters: q=32, r=64, s=7, u=1
- **DTI_Trade(r, s, u)** — Ch.7 — Parameters: r=28, s=28, u=5
- **TVI_Trade(r, s, u)** — Ch.10 — Parameters: r=32, s=32, u=5

### 9.2 ADX-Type Filter (ATF)

```
ATF(X, r) = EMA(|single_smoothed_X|, r)
```

Positive slope = trending. Implementations:
- **TSI_ATF(price, r)** — `EMA(|TSI(price, r, 1)|, r)` — e.g., r=32
- **SMI_ATF(q, r)** — `EMA(|SMI(q, r, 1)|, r)` — e.g., q=32, r=32

### 9.3 Slope Divergence Filter (SD)

```
SD_TSI(price, r, s, u, x, y):
  = TSI   when slope(TSI) == slope(DEMA(price, x, y))
  = 0     when slopes diverge (congestion)
```

- **Parameters**: r=32, s=32, u=7, x=32, y=7
- **Properties**: Catches more trends than _Trade filter; fewer premature exits

---

## Group 10: Double-Smoothed RSI (DM Family)

### 10.1 Double-Smoothed Momenta (DM)

```
DM(a, y, z) = 100 * Ez(Ey(C - LCa)) / Ez(Ey(HCa - LCa))
```

- Uses **highest/lowest CLOSE** (not H/L) — distinct from DS-Stochastic
- **Range**: [0, 100]
- **Special case**: `DM(2, 1, z) = RSI(z)` (proven equivalence)
- **Double-smoothed RSI**: `DRSI(y, z) = DM(2, y, z)`

---

## Utilities

### U1. ExponentialMAOnBuffer (period=1 passthrough)

Modified EMA function where period=1 returns input unchanged. Core building block.

### U2. Slope Detection

```
slope(X) = sign(X[0] - X[1])
```

Used in all _Trade filters and slope divergence.

### U3. Highest-High / Lowest-Low over q bars

```
HH(q) = max(high[0], high[1], ..., high[q-1])
LL(q) = min(low[0], low[1], ..., low[q-1])
```

### U4. Highest-Close / Lowest-Close over a bars

```
HC(a) = max(close[0], close[1], ..., close[a-1])
LC(a) = min(close[0], close[1], ..., close[a-1])
```

Used in DM family (Group 10) — distinct from H/L used in stochastics.

---

## Trading System Templates

### Template A: Ergodic Crossover

```
Buy:  Ergodic crosses above Signal Line
Sell: Ergodic crosses below Signal Line
Filter: Only trade when in direction of slow trend indicator
```

### Template B: Trend Filter + Fast Oscillator

```
Entry: Filter nonzero AND slope(Filter) == slope(Oscillator)
Exit:  slope(Oscillator) reverses OR Filter returns to zero
```

Combinations:
| Trend Filter | Fast Oscillator |
|---|---|
| TSI_Trade(32,13,3) | SMI(2,20,5) Ergodic |
| DTI_Trade(28,28,5) | SMI(2,r,5) |
| SMI_Trade(32,64,7) | 2-day Stochastic |
| TVI_Trade(32,32,5) | TVI Ergodic |
| SD_TSI(32,32,7,32,7) | SMI Ergodic |
| Slow TSI(64,64) | Fast TSI(20,6) Ergodic |

### Template C: Slope Divergence Stand-Aside

```
Trade: when slope(indicator) == slope(smoothed_price)
Aside: when slopes diverge (congestion zone)
```

---

## Implementation Priority Suggestion

| Priority | Indicator | Rationale |
|----------|-----------|-----------|
| 1 | EMA utility (period=1 passthrough) | Foundation for everything |
| 2 | TSI | Most referenced; foundation of the system |
| 3 | Ergodic Oscillator (TSI + Signal Line) | Primary trading tool |
| 4 | SMI | Second most important; bipolar stochastic |
| 5 | DS-Stochastic | Classic Blau contribution |
| 6 | DTI | Unique high-low momentum approach |
| 7 | CMI / CSI | Gap-immune intraday tools |
| 8 | MDI | Detrending / MACD alternative |
| 9 | _Trade filters | Nonambiguous trend identification |
| 10 | Slope Divergence filter | Most sophisticated filtering |
| 11 | TVI | Requires tick data; niche |
| 12 | DM / DRSI | Historical interest; RSI generalization |
