# Mark Jurik's Technical Analysis Trading Indicators: A Comprehensive Guide

## Executive Summary

Mark Jurik is a computer scientist and electrical engineer who founded Jurik Research Software, Inc. in 1988 in Silicon Valley [14]. Over 34+ years, he developed a suite of proprietary technical analysis indicators rooted in military signal processing technology — specifically, the adaptive tracking algorithms originally designed for radar-based target tracking [9]. His core innovation was applying these advanced non-linear filtering techniques to financial time series data, achieving what classical technical analysis tools could not: simultaneously minimizing lag *and* noise without the trade-offs inherent in conventional approaches [1][13].

Jurik Research produced **seven distinct indicator tools** (plus one legacy tool), organized into two categories: (1) **tools for superior technical analysis** — JMA, VEL, CFB, RSX, and DMX — and (2) **tools for creating leading indicators** — WAV and DDR [1]. The company also developed **Gap Awareness© Technology** as a late-stage enhancement [16]. All algorithms are proprietary (registered with the U.S. Copyright Office and held as trade secrets) [13], so only their principles and behavior — not their exact formulas — are publicly documented. As of 2023–2024, Jurik Research announced it was winding down operations after 34 years [16].

This report documents each indicator's purpose, the theoretical principles it is based on, how it works, its parameters, and how it compares to classical alternatives, drawing primarily from Jurik Research's own official documentation.

---

## 1. Background: Mark Jurik and Jurik Research

**Mark Jurik** holds technical credentials in Chemistry, Electrical Engineering, and Psychology. He began developing data analysis algorithms in 1978, primarily for military applications. In 1988 he founded Jurik Research Software, Inc. in Silicon Valley, redirecting signal processing expertise from military target tracking to financial markets [14].

Key biographical facts [13][14]:
- Lectured at 28 conferences and seminars on neural networks and technical analysis
- Created "NeuroTapes," a 12-hour video course on neural network technology (approved by U.C. Berkeley Independent Studies Program)
- Taught classes on Artificial Intelligence in California
- Contributing author to *Virtual Trading*; author of *Neural Networks and Financial Forecasting*; editor of *Computerized Trading* (published by New York Institute of Finance)
- Published articles in *Futures Magazine* and *Journal of Computational Intelligence in Finance*
- Clients included Merrill Lynch, Shearson Lehman, and Deutsche Bank
- Software tools received top scores in a *Futures Magazine* review

**Core philosophy:** Popular technical indicators suffer from two fundamental problems — **noise** (jagged, jittery signals that produce false triggers) and **lag** (delay that causes late trades). Classical approaches force a trade-off: smoothing reduces noise but adds lag; speed reduces lag but increases noise. Jurik's tools were designed to break this trade-off using adaptive non-linear filtering from military radar technology [1][13].

**Design methodology:** All tools were first designed and tested in MATLAB, then alpha-tested for several months, then beta-tested for several more months before release [13].

---

## 2. The Indicators

### 2.1 JMA — Jurik Moving Average

**Category:** Technical analysis (data smoother)  
**Full name:** Jurik Moving Average  
**Replaces/improves:** All classical moving averages (SMA, EMA, WMA), Kalman filters, KAMA, VIDYA, DEMA, T3, HMA, Savitzky-Golay filters [2][9]  

#### Principles

JMA is based on the same technology the military uses to track moving objects via noisy radar signals. It treats the price time series as a noisy image of a "moving target" (the underlying true smooth price) and estimates the location of that target [9].

The theoretical foundation combines [9]:
- **Information theory** — assessing the information content in a time series
- **Adaptive non-linear filtering** — dynamically adjusting the filter response based on current market conditions (volatility, price gaps, trend changes)

According to Jurik, the ideal noise reduction filter must satisfy four requirements [9]:
1. **Minimum lag** between signal and price (otherwise trade triggers come late)
2. **Minimum overshoot** (otherwise the signal produces false price levels)
3. **Minimum undershoot** (otherwise time is lost waiting for convergence after price gaps)
4. **Maximum smoothness**, except at the moment when price gaps to a new level

JMA makes **no assumptions** about the data having cyclic components, Gaussian-distributed price changes, or equally important prices. This allows it to "turn on a dime" when markets reverse or gap [9].

#### Parameters

| Parameter | Description |
|---|---|
| **Length** | Controls smoothing depth. Longer = smoother but more lag [2]. |
| **Phase** | Controls "inertia" (trade-off between lag and overshoot). High phase = more inertia = more overshoot but slower direction reversal. Phase of 0 = no inertia = fastest direction change. Range: -100 to +100 [9]. |

#### How It Works

- JMA processes any time series (not just price — can smooth other indicators' output) [2]
- Uses only current and prior data (never looks forward; works in real-time) [9]
- Produces a single smooth output value per bar
- Adaptively adjusts its filtering based on market conditions: tracks closely during trends, smooths through congestion [2]
- Handles price gaps by rapidly converging to the new level without overshooting or ringing [9]

#### Performance Claims

- JMA outperforms: Kalman filters (g, g-h, g-h-k variants), Savitzky-Golay filters, KAMA, VIDYA, DEMA, T3, Brown's MMA, Ehler's MEF, Ehler's symmetric FIR filter, and Hull Moving Average (HMA) [2]
- Processes 1,000,000 data points in 3.3 seconds on a 1.7 GHz processor [2]
- Jurik offered a performance guarantee: refund if anyone could show a non-proprietary MA that outperforms JMA on smoothness, lag, overshoot, and undershoot across short/medium/long time frames on a random walk (cumulative sum of Cauchy-distributed random numbers) [9]

#### Key Use Cases

- **Price proxy:** Using JMA's trend direction to determine market direction [2]
- **Crossover analysis:** Fast JMA crossing slow JMA (or fast JMA crossing slow SMA) for MACD-type signals — can signal trades up to two weeks earlier than classical EMA crossovers on long-term charts [2]
- **Building block:** Inserting JMA into other indicators' formulas to improve their smoothness and timing [9]
- **Short-term trading:** Eliminates excessive trades while maintaining timely signals [2]

#### Notable Insight from Jurik

A naive MACD using `fast JMA - slow JMA` produces mediocre results because MACD actually *requires* lag between its two lines. The recommended approach is `fast JMA - slow SMA`, which maximizes the lag differential between lines while minimizing crossover delay [13].

---

### 2.2 AMA — Adaptive Moving Average (Legacy)

**Category:** Technical analysis (legacy data smoother)  
**Status:** Legacy product, included as a bonus with JMA purchases [2]  

AMA was Jurik's earlier-generation adaptive moving average, predecessor to JMA. It continued to be distributed because demand persisted for its "ultra smooth" characteristics, particularly suited for high-frequency noise reduction [2]. AMA was superseded by JMA for most purposes but remained available for users who preferred its specific smoothing profile.

---

### 2.3 VEL — Velocity Index

**Category:** Technical analysis (momentum oscillator)  
**Full name:** Jurik Velocity Index  
**Replaces/improves:** Classical momentum indicators, smoothed momentum [3]  

#### Principles

VEL is based on "solid mathematics, not ad-hoc heuristics" [10]. Its key innovation is producing an **ultra-smooth momentum signal with zero additional lag** compared to classical momentum.

VEL does NOT [10]:
- Smooth the classical momentum signal (any smoothing would add lag)
- Calculate momentum of a JMA-smoothed time series (which would have more lag and less vertical accuracy)

Instead, VEL uses a proprietary approach that directly computes smooth momentum without the smoothing-then-lagging pipeline [10].

#### Parameters

| Parameter | Description |
|---|---|
| **Length** | Period length — how many historical samples are used in the evaluation [10]. |

#### How It Works

- Input: any time series (price, indicator output, etc.) [3]
- Output: a smooth, unbounded oscillator representing momentum direction and speed
- VEL measures momentum **to scale** — if bar-to-bar price changes double, VEL doubles. It provides "true momentum" [10].
- Uses only current and prior data; values never change retroactively [10]

#### Comparison to RSX

| Property | VEL | RSX |
|---|---|---|
| Measures | Momentum speed and direction | Momentum quality and direction |
| Scale | Unbounded (proportional to price changes) | Bounded (0–100) |
| Thresholding | Poor (threshold needs continuous readjustment) | Excellent (fixed thresholds work) |
| Best for | Divergence analysis | Buy/sell zone identification, reversal detection |

*Source: [10][11]*

#### Key Use Cases

- **Divergence analysis:** VEL's accurate scaling makes it ideal for comparing price turning points to momentum turning points — detecting when a trend is decelerating [3]
- **Trend momentum confirmation:** Smooth lines eliminate false signals from classical momentum's jitter [3]

---

### 2.4 RSX — Relative Strength Quality Index

**Category:** Technical analysis (oscillator)  
**Full name:** Relative Strength Quality Index  
**Replaces/improves:** Classical RSI (Relative Strength Index) [5]  

#### Principles

In classical RSI, trend strength is measured by computing separate moving averages (originally SMA, now typically EMA) of upward and downward price changes. These averaging techniques introduce significant **lag and noise** into the signal [11].

RSX replaces the internal averaging in RSI with Jurik's proprietary low-lag, high-smoothness filtration. The result is an RSI-type indicator that is "noise-free" with no additional lag over standard RSI [5][11].

#### Parameters

RSX accepts the same basic period length parameter as RSI. The output is bounded between 0 and 100, just like RSI [11].

#### How It Works

- Computes the same conceptual ratio as RSI (strength of up-moves vs. down-moves) but uses advanced internal smoothing instead of simple/exponential moving averages [11]
- Produces ultra-smooth curves that make trend reversals visually obvious [5]
- Bounded 0–100, making it suitable for fixed threshold trading (buy/sell zones) [11]
- Measures trend **quality** rather than speed — a clean trend (small reversals) produces a strong RSX signal; a noisy, congesting trend produces a weak signal [11]

#### Advantages Over RSI [5]

- Eliminates false trade triggers from jitter
- Enables tighter stops and more meaningful threshold levels
- Can run at faster (shorter) period settings without degradation from noise
- Better acceleration analysis
- Can be used to create superior versions of other indicators (e.g., replacing RSI internals in DeMark's REI indicator)

---

### 2.5 DMX — Directional Movement Index

**Category:** Technical analysis (trend direction and strength)  
**Full name:** Directional Movement Index  
**Replaces/improves:** Classical DMI (DMI+, DMI−) and ADX [6]  
**Pricing:** Free with purchase of JMA [6]  

#### Principles

DMX is built by applying JMA smoothing to the classical DMI formula, but with a key modification: it uses a **bipolar** formulation [6].

Classical DMI formula:

> DMI = | DMI+ − DMI− | / | DMI+ + DMI− |

The absolute value makes DMI always positive, losing directional information. DMX removes the absolute value to create "Bipolar DMI" [6]:

> Bipolar DMI = ( DMI+ − DMI− ) / ( DMI+ + DMI− )

This bipolar signal is positive during upward trends and negative during downward trends. It is then smoothed using JMA to produce an ultra-smooth version — that is DMX [6].

#### How It Works

- Output: a single smooth line oscillating around zero [6]
- Positive = uptrend; Negative = downtrend
- Replaces the need for three separate indicators (DMI+, DMI−, ADX) with one clean signal
- Can generate trades on zero-line crossovers or on momentum direction changes [6]

#### Advantages Over ADX/DMI

- Combines directional information (which ADX discards) with trend strength in one indicator [6]
- Ultra-smooth — enables momentum-based trading that would be impossible with noisy classical DMI [6]
- Less lag than ADX [1]

---

### 2.6 CFB — Composite Fractal Behavior Index

**Category:** Technical analysis (trend duration measurement)  
**Full name:** Composite Fractal Behavior Index  
**Replaces/improves:** ADX for trend/consolidation detection; dominant cycle length (DCL) approaches using FFT, MEM, MESA [4][12]  

#### Principles

CFB is based on **fractal analysis** — specifically, it examines a time series for fractal patterns at multiple scales and combines them into a composite index. This was Jurik's 1996 discovery that fractals could assess trend duration without assuming the existence of market cycles [4].

Key theoretical insight: Many traders use **dominant cycle length (DCL)** to dynamically adjust indicator speed. But DCL methods (FFT, MESA, periodograms) assume that cycles exist in the data. When no real cycle exists — which is common — these methods estimate "ghost cycles," producing meaningless values [12]. Jurik demonstrated that random walks generate convincing-looking cycles that are impossible to forecast, proving that cycle-finding tools can be trivially fooled [12].

CFB avoids this problem entirely by measuring trend duration through fractal geometry, not cycle analysis [4][12].

#### Parameters

| Parameter | Description |
|---|---|
| **Period length** | Only four values allowed: 24, 48, 96, or 192 bars. Determines the maximum trend duration that can be detected [12]. |

All four period versions are included with purchase [12].

#### How It Works

- CFB examines the time series for fractal patterns at various scales within the lookback window [12]
- Aggregates these patterns into a single composite index
- **Output:** A value proportional to trend duration, measured in units of **time** (bars), not price [12]
- As trend duration increases → CFB rises [4]
- When trend breaks down → CFB falls [4]
- Sensitive to trend *quality* — drops when a trend breaks down, serving as an early exit signal [4]

#### Comparison to ADX

- CFB is more sensitive to trend/consolidation mode shifts than ADX [4]
- ADX can miss new trends entirely and continue showing a "growing trend" when the trend has already ended [4]
- CFB detects weakening trends faster [4]

#### Key Use Cases [12]

- **Auto-adjusting indicator speed:** Using CFB output to dynamically set the lookback period of stochastic bands, RSI, or other indicators
- **Elastic breakout channels:** Setting channel lookback width proportional to CFB
- **Trend exit signals:** CFB decline indicates trend quality deterioration

---

### 2.7 WAV — Waveform Data Reducer

**Category:** Leading indicator construction (data preprocessing)  
**Full name:** Waveform Data Reducer  
**Purpose:** Temporal compression of historical time-series data for use as inputs to forecasting models [7]  

#### Principles

WAV is based on the insight that financial forecasting models need information about both short (fast) and long (slow) cycles in historical data, and that selecting which historical values to use is a critical, non-trivial problem [7]. Rather than uniformly sampling the past (e.g., every N bars), WAV uses a proprietary sampling scheme that captures information across multiple time scales simultaneously.

The key problem WAV solves: a forecasting model (neural net, regression, genetic algorithm) might need information spanning 120 bars of history, but feeding all 120 values creates an unwieldy, overfitted model. WAV compresses those 120 values into a much smaller set of numbers that efficiently represent the historical activity [7].

#### Parameters

| Parameter | Description |
|---|---|
| **Window width** | Number of bars to examine (e.g., 120) |
| **Detrend option** | Whether to detrend the data before compression |
| **Normalize option** | Whether to normalize the data before compression |

*Source: [7]*

#### How It Works [7]

- WAV takes a time series and a window width as input
- At each bar, it produces multiple output values (columns) instead of one — these columns efficiently represent the activity over the past N bars
- The number of output columns is much smaller than the window width
- Output columns are arranged row-by-row, compatible with regression models, neural nets, and other modeling tools
- Captures information from both short-period and long-period patterns

#### Lab Results [7]

In tests on the Mackey-Glass chaotic time series (a standard benchmark for forecasting):
- With 4 input values, WAV produced 9.8% forecast error vs. 15.6% for uniform sampling
- At every number of inputs tested, WAV-preprocessed data gave lower forecast error than uniformly sampled data

#### Historical Note

An early version of WAV was mentioned on CNBC's *Tech Talk with John Murphy*. The WAV methodology was used by *Futures Magazine* contributing editor Murray Ruggiero in several trading systems, documented in *Futures Magazine* (August 1994 and May 1996 issues) [7].

---

### 2.8 DDR — Decorrelator & Dimension Reducer

**Category:** Leading indicator construction (data preprocessing)  
**Full name:** Decorrelator & Dimension Reducer  
**Purpose:** Decorrelate and reduce the dimensionality of multi-variable indicator data for forecasting models [8]  

#### Principles

DDR addresses the well-documented problem that common technical indicators are highly correlated with each other. Chande and Kroll (*The New Technical Trader*, p. 9) showed that momentum, RSI, stochastics, ADX, etc. have inter-correlations of r = 0.77 to 0.93 [8]. Feeding a forecasting model with multiple correlated indicators means it receives an "empty diet of numbers mostly saying the same thing" [8].

DDR performs **decorrelation and dimensionality reduction** — transforming correlated indicator data into a new set of 100% uncorrelated variables, then ranking them by information content so that the most informative variables come first [8]. The approach is conceptually related to Principal Component Analysis (PCA), though the specific implementation is proprietary.

#### How It Works [8]

1. Input: a spreadsheet-style array where each column is a different indicator and each row is a forecast case
2. DDR transforms the array into a new array of the same size, but with entirely new, mutually uncorrelated columns
3. DDR ranks the columns so that the leftmost columns contain the most information
4. DDR reports how much total information is captured by each successive column
5. The user can discard low-information columns — e.g., in the documented example, 6 columns out of 20 captured 96% of all information

DDR's approach is described as superior to "pairwise elimination" methods used by other products [8].

#### Lab Results [8]

Three models were tested on a simulated financial time series (composite of sinusoidal cycles, Mackey-Glass chaos, and Brownian noise) with 1500 cases and 21 indicators:

| Model | Inputs | Average Forecast Error |
|---|---|---|
| Linear regression | All 21 indicators | 15.0% |
| Neural network | All 21 indicators | 6.4% |
| Neural network | First 5 DDR columns only | 6.4% |

The neural net on just 5 DDR columns matched the neural net on all 21 raw indicators — the other 16 columns could be safely discarded.

#### Recommended Workflow (with WAV) [7][8]

Jurik Research recommended using WAV and DDR together in a pipeline:
1. Export time series from charting platform to Excel
2. Apply WAV for temporal compression of each time series → new columns
3. Apply DDR for decorrelation of all columns → ranked, uncorrelated columns
4. Feed selected DDR output to a modeling tool (neural net, genetic algorithm)
5. Once validated, reconstruct the pipeline in TradeStation for real-time use

---

### 2.9 Gap Awareness© Technology

**Category:** Enhancement layer  
**Status:** Late-stage addition to the product line [16]  

Gap Awareness© Technology was introduced as one of the final innovations from Jurik Research. It was implemented prominently in the eSignal platform, which included "24 Custom Studies with new Gap Awareness Technology" [16]. Detailed public documentation of its internals is limited; it appears to be an enhancement to the existing indicators' gap-handling capabilities rather than a standalone indicator.

---

## 3. Theoretical Foundations: Unified View

Mark Jurik published a technical report titled "The BIG Picture" that provided "a unified perspective showing how and why Jurik's modules work well as building blocks for reliable low-lag indicators" [15]. The foundational principles across all tools include:

### 3.1 Adaptive Non-Linear Filtering (from Military Radar)

The core technology derives from **target tracking algorithms** — the mathematics used to estimate the position and velocity of a moving object (e.g., missile, aircraft) from noisy radar measurements [9][14]. In financial terms:
- The "target" = the underlying smooth price
- The "noisy radar signal" = the observed market price time series
- The goal = estimate the target's true position (smooth value), velocity (momentum), and trajectory with minimal delay

This is mathematically related to the **Kalman filter** family, but Jurik's implementation goes beyond standard Kalman filtering by [9]:
- Not assuming the data follows Gaussian noise distributions
- Adapting to non-stationary behavior (regime changes, price gaps)
- Avoiding overshoot and oscillation at transition points

### 3.2 Information Theory

JMA specifically integrates information theory to assess the "information content" of a time series at each point [9]. This governs how the filter adaptively adjusts its bandwidth — likely speeding up when new, significant information arrives (price gap, trend change) and slowing down during noise (random congestion). *(Note: the exact mechanism is proprietary; the information-theory connection is stated by Jurik but not detailed publicly.)*

### 3.3 Fractal Geometry

CFB uniquely employs fractal analysis to measure trend characteristics without assuming cyclic behavior [4][12]. Fractals provide a scale-independent way to characterize the "roughness" or "trending quality" of a time series, which maps naturally to trend duration.

### 3.4 Decorrelation / Dimensionality Reduction

DDR applies matrix decorrelation techniques to transform correlated financial indicators into orthogonal components ranked by information content [8]. The approach is functionally similar to PCA/SVD, though the specific implementation is proprietary.

### 3.5 Multi-Resolution Sampling

WAV employs a sampling scheme that captures information at multiple time scales simultaneously [7] — conceptually related to wavelet-like multi-resolution analysis, though the specific implementation is proprietary.

---

## 4. Indicator Relationships and Workflow

The Jurik tools form a modular toolkit designed to be combined [1][15]:

```
                    ┌──────────────────────────────────────────┐
                    │     TECHNICAL ANALYSIS LAYER             │
                    │                                          │
                    │  JMA ──→ Smooth price proxy              │
                    │   │                                      │
                    │   ├──→ DMX (JMA applied to bipolar DMI)  │
                    │   │                                      │
                    │  VEL ──→ Smooth momentum (true velocity) │
                    │                                          │
                    │  RSX ──→ Smooth RSI (trend quality)      │
                    │                                          │
                    │  CFB ──→ Trend duration (fractal-based)  │
                    │   │                                      │
                    │   └──→ Auto-adjust other indicator speeds │
                    └──────────────┬───────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────────────────┐
                    │     LEADING INDICATOR LAYER              │
                    │                                          │
                    │  WAV ──→ Temporal compression of history  │
                    │   │                                      │
                    │   ▼                                      │
                    │  DDR ──→ Decorrelation & dimension        │
                    │   │      reduction                       │
                    │   ▼                                      │
                    │  Forecast Model (neural net, GA, etc.)   │
                    └──────────────────────────────────────────┘
```

---

## 5. Comparison Summary: Jurik Tools vs. Classical Indicators

| Jurik Tool | Classical Equivalent | Key Advantage |
|---|---|---|
| JMA | EMA, SMA, WMA, KAMA, VIDYA, DEMA, T3, HMA [2][9] | Minimal lag + maximum smoothness + handles gaps without overshoot |
| VEL | Momentum, Rate of Change (ROC) [3] | Ultra-smooth momentum with zero additional lag |
| RSX | RSI [5] | Noise-free RSI with no added lag; bounded 0–100 |
| DMX | DMI+, DMI−, ADX [6] | Single smooth bipolar line replaces three noisy/laggy indicators |
| CFB | ADX, DCL via FFT/MESA [4] | Fractal-based trend duration; works without assuming cycles exist |
| WAV | Uniform historical sampling [7] | Multi-scale temporal compression; lower forecast error |
| DDR | Manual variable selection, pairwise elimination [8] | Automatic decorrelation; optimal dimension reduction |

---

## 6. Current Status and Legacy

As of the notice on jurikres.com (circa 2023–2024): "After 34 years of successfully developing new tools for technical analysis, Jurik Research Software is winding down its operations" [16]. The company was based in Pasadena, California [14].

Despite the proprietary nature of the algorithms, the community has produced **reverse-engineered approximations** of JMA and RSX. A notable example is a document by "Igor" that reverse-engineered JMA's algorithm, which has been the basis for open-source implementations on platforms like TradingView [17], NinjaTrader [18], and MQL5. These approximations capture the general behavior but are acknowledged to be imperfect replicas of the original [17][18].

Jurik's tools were available across many charting platforms including TradeStation, MultiCharts, eSignal, NinjaTrader, AmiBroker, Sierra Chart, MATLAB, NeuroShell, NeoTicker, and others [1].

---

## Open Questions

1. **Exact algorithms:** The precise mathematical formulations of JMA, VEL, RSX, and CFB remain trade secrets. Only their principles, inputs/outputs, and behavioral characteristics are publicly documented. Disclosed source code was available to U.S. firms under special agreements at $5,000 per tool [9][10][11].

2. **Gap Awareness© Technology:** Very limited public documentation exists about this late-stage innovation [16]. Its exact mechanism and relationship to the existing indicator suite is unclear.

3. **BackPercolation:** Jurik authored a paper on "BackPercolation," a method for training perceptron-based neural nets [15]. Its relationship to the trading indicators is unclear — it appears to be a separate research contribution in neural network methodology.

4. **Accuracy of open-source approximations:** The reverse-engineered JMA implementations vary in fidelity. Multiple TradingView developers have noted that many public implementations deviate from the source reverse-engineering document [17].

5. **Post-wind-down availability:** With Jurik Research winding down [16], the future availability of the official tools (which required activation passwords tied to specific charting platform accounts) is uncertain.

---

## Sources

1. Jurik Research Product Catalog — http://jurikres.com/catalog1/catalog.htm
2. JMA (Jurik Moving Average) Product Page — http://jurikres.com/catalog1/ms_ama.htm
3. VEL (Velocity Index) Product Page — http://jurikres.com/catalog1/ms_vel.htm
4. CFB (Composite Fractal Behavior) Product Page — http://jurikres.com/catalog1/ms_cfb.htm
5. RSX (Relative Strength Quality Index) Product Page — http://www.jurikres.com/catalog1/ms_rsx.htm
6. DMX (Directional Movement Index) Product Page — http://jurikres.com/catalog1/ms_dmx.htm
7. WAV (Waveform Data Reducer) Product Page — http://jurikres.com/catalog1/ms_wav.htm
8. DDR (Decorrelator & Dimension Reducer) Product Page — http://jurikres.com/catalog1/ms_ddr.htm
9. FAQs on JMA — http://jurikres.com/faq1/faq_ama.htm
10. FAQs on VEL — http://jurikres.com/faq1/faq_vel.htm
11. FAQs on RSX — http://jurikres.com/faq1/faq_rsx.htm
12. FAQs on CFB — http://jurikres.com/faq1/faq_cfb.htm
13. Jurik Research General FAQ — http://www.jurikres.com/faq1/main_faq.htm
14. Jurik Research About/Company Page — http://jurikres.com/about/company.htm
15. Jurik Research Technical Reports — http://www.jurikres.com/faq1/reports.htm
16. Jurik Research Homepage — http://jurikres.com/
17. TradingView: Jurik MA [lastguru] — Open-source JMA implementation — https://www.tradingview.com/script/ofu6hRfu-Jurik-MA-lastguru/
18. NinjaTrader Ecosystem: Jurik Moving Average (JMA) — https://ninjatraderecosystem.com/user-app-share-download/jurik-moving-average-jma/
19. Sharp Vision Traders: Dynamic Jurik RSX — https://sharpvisiontraders.com/downloads/dynamic-jurik-rsx-ts/

*Note: jurikres.com sources [1]–[16] employ bot protection (HTTP 403 to automated clients) but are accessible via browser and archived on the Wayback Machine (web.archive.org). Content was retrieved and verified during research on 2026-04-10.*
