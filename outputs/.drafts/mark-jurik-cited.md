# Mark Jurik: Biography, Publications, Indicators, and Methods

## Executive Summary

Mark Jurik is the founder of Jurik Research & Consulting (est. 1988, Silicon Valley), a company that developed proprietary adaptive signal processing algorithms for financial trading. His flagship product, the Jurik Moving Average (JMA), is widely regarded as one of the best-performing adaptive filters in retail trading — and one of the few whose algorithm has never been publicly disclosed. After 34 years of operation, the company began winding down around 2022.

Jurik's background is in military signal processing (ELINT), and his career arc represents a Cold War-to-Wall Street pivot: applying missile tracking technology to financial time series. He holds no known TASC publications; all his indicators are sold as compiled DLLs, with the algorithms protected as trade secrets. The most significant public reverse-engineering is by Weld/Igor (ForexTSD, 2005-2008, JMA decompilation). A second, more comprehensive decompilation by "Starlight" (Oleg Anashkin) covers 11 indicators but has no known public distribution. Press coverage is sparse — the most substantive independent review (Financial Software Review, 2000) found JMA doubled winning trades vs. SMA/EMA crossovers on DAX intraday data. The only known institutional user citation is Landmark Asset Management ($18M AUM, MARHedge 2005).

---

## 1. Biography

### Career Timeline

- **Pre-1987:** Signal processing work for military projects (ELINT — electronic intelligence). Specific employer and education unknown. [2]
- **1987:** First public appearances — AI Conference (Association of Old Crows, military ELINT), SF Bay Area AI Forum, Lawrence Livermore National Laboratory. [3]
- **1987-1991:** Taught a 10-lecture series on neural networks at UC Extension, repeated annually for five years. [3]
- **1988:** Founded Jurik Research & Consulting. Presented at IEEE Information Theory Society, IEEE ASSP, IEEE Compcon, Santa Clara University AI SIG. [3]
- **1989-1991:** IEEE videoconference on neural networks; "Neural Nets for the Real World" conference; IEEE Wescon; IEEE Asilomar; AOC International Conference; neural network conference in Germany; Stanford University Computer Science Forum. [3]
- **1994:** IEEE SIG Group: AI and Finance. [3]
- **1995:** Futures West International Conference (delivered "Space, Time, Cycles & Phase" lecture, later released as audio seminar). [3]
- **1996:** Published in *Futures Magazine* (May 1996, pp. 44-48) — article on forecasting MACD using an Adaptive Moving Average, the precursor to JMA. [2]
- **1999:** First TASC Readers' Choice Award (4th place). [9]
- **1999:** Published *Computerized Trading* (editor, 20 contributing authors). Presented at Omega World '99. [3][4]
- **2000:** Swiss Association of Market Technicians (SAMT), Zurich. Wall Street Harvest interview. [3][9]
- **2001:** Market Technicians Association (Denver, Chicago). [3]
- **2007-2012:** TASC Readers' Choice Awards — 1st place 2010, 2011, 2012; 2nd place 2007, 2009. [9]
- **2010:** Austin Association of Financial Traders. Trader's Magazine (Germany) interview. [3][9]
- **~2022:** Company begins winding down operations. [2]

### Personal Details

No public information exists about Jurik's formal education, birth year, or personal life. His IEEE presentations and military background strongly suggest training in electrical engineering or computer science, but this is unconfirmed. A portrait photo exists at `http://jurikres.com/gifs1/portrait3.jpg` [1].

### Company

**Jurik Research Software, Inc.**
556 South Fair Oaks Avenue, #595, Pasadena, CA 91105

The company's stated mission: apply "signal processing skills originally intended for military projects" to commercial financial markets [2]. Products are sold as platform-specific DLLs/plugins for 15+ trading platforms including TradeStation, NinjaTrader, MultiCharts, AmiBroker, MATLAB, Sierra Chart, and C/C++/C#/.NET libraries.

---

## 2. Photos and Appearances

- **Portrait:** `http://jurikres.com/gifs1/portrait3.jpg` [1]
- **28+ conference presentations** (1987-2010), documented at `http://jurikres.com/about/presents.txt` [3]
- **NeuroTapes:** 12-hour video course on neural networks, sold worldwide for over a decade [2]
- **"Space, Time, Cycles & Phase":** Audio seminar (MP3 on CD), based on 1995 conference lecture [4]
- **Interviews:** Wall Street Harvest (2000, sector analysis); Trader's Magazine Germany (2010, extended interview on JMA design, risk management, company origins) [9]

---

## 3. Books and Publications

### Books

**Computerized Trading: Maximizing Day Trading and Overnight Profits** (1999)
- Role: Editor
- Publisher: New York Institute of Finance (Prentice Hall)
- 20 contributing authors including DiNapoli, Kiev, Klimasauskas, Katz
- Covers system development, market psychology, advanced indicators, forecasting
- Status: Out of print (sold out) [4]

**Neural Networks and Financial Forecasting**
- Role: Author
- Self-published collection of technical reports (published and unpublished)
- Topics: neural network training, fuzzy logic, data preprocessing, trading system scoring, backpropagation critique, "Backpercolation" algorithm
- Sold only through Jurik Research; out of print [4]

**Virtual Trading** (contributing author, details unknown) [2]

### Articles

- *Futures Magazine*, May 1996, pp. 44-48 — AMA (Adaptive Moving Average) applied to MACD forecasting on D-Mark futures [2]
- *Journal of Computational Intelligence in Finance* (also known as *Neurovest Journal* / *AI in Finance*) — unspecified articles [2]

### Notable Absence

Mark Jurik has **no publications in Technical Analysis of Stocks & Commodities (TASC)**. The TASC author archive returns no results for his name, and a scan of 30+ monthly XML table-of-contents files (1995-2011) found zero articles by him [5]. His indicators are exclusively commercial products, not published through trade magazines.

---

## 4. Trading Indicators

All Jurik indicators share a common design philosophy: replace the smoothing component of a standard indicator with JMA's adaptive engine. The algorithms are proprietary, distributed as compiled binaries, and have never been officially published.

### 4.1 JMA (Jurik Moving Average)

**Purpose:** Ultra-smooth, low-lag adaptive moving average.

**Parameters:**
- Length (smoothing depth)
- Phase (-100 to +100): controls lag vs. overshoot tradeoff

**Claims:** Superior to EMA, KAMA, VIDYA, DEMA, T3, Hull MA, Kalman filters, Savitzky-Golay, and Ehlers' elliptical filters. No overshoots, no oscillations. Can process 1,000,000 points in 3.3 seconds. [6]

**What is known about the algorithm:**
- Adaptive filter that modulates smoothing speed based on market conditions
- Multi-stage IIR structure with adaptive coefficients (from reverse-engineering) [7]
- Likely uses a volatility or efficiency-ratio measure to detect trending vs. ranging [inferred]
- Phase parameter adjusts group delay vs. transient response (analogous to adjusting filter pole positions) [inferred]
- "No overshoots" rules out simple FIR approaches; implies carefully damped IIR poles [inferred]
- Conceptually related to alpha-beta tracking filters used in radar/missile guidance [2]

**Historical note:** An earlier version was called "AMA" (Adaptive Moving Average), published in *Futures Magazine* (1996). AMA is still included as a legacy product. [2]

### 4.2 RSX (Jurik RSI)

**Purpose:** Noise-free RSI replacement with no added lag. [6]

**What is known about the algorithm:**
RSX uses the same mathematical structure as RSI but replaces Wilder's EMA with an "ultralinear" adaptive smoother:

```
signed_change = price[i] - price[i-1]
abs_change = |signed_change|
smooth_signed = JurX(signed_change)    // adaptive smoothing
smooth_abs = JurX(abs_change)          // adaptive smoothing
RSX = smooth_signed / smooth_abs       // bounded ratio, -1 to +1
```

This is RSI reformulated as a centered oscillator with superior internal smoothing. The architecture is well-understood from Kositsin's reverse-engineering. [7]

### 4.3 VEL (Velocity)

**Purpose:** Noise-free market momentum/rate-of-change. [6]

**What is known about the algorithm:**
Almost certainly the **first derivative of JMA** — either:
- `JMA[i] - JMA[i-1]` (simple difference of consecutive JMA values), or
- `JMA(close - close[N])` (JMA applied to raw momentum)

Both formulations yield smooth momentum with minimal lag, since JMA itself has minimal lag. No standalone algorithm exists — VEL is derived from JMA. [7] [inferred]

### 4.4 CFB (Composite Fractal Behavior)

**Purpose:** Measures duration of market trend without assuming cyclical behavior. [8]

**Claims:** More reliable than FFT/MESA cycle analysis because it works even when no cycles exist. Superior to ADX for detecting trend strength. Index increases as trend duration increases; measures up to 192 bars. [8]

**What is known about the algorithm:**
- Uses **fractal dimension estimation** rather than spectral methods [8]
- Fractal dimension (FD) near 1.0 = strong trend; FD near 1.5 = random walk; FD near 2.0 = mean-reverting [inferred from standard FD theory]
- CFB likely inverts FD: low fractal dimension (trending) produces high CFB [inferred]
- "Composite" may indicate multiple-timeframe fractal estimates combined [inferred]
- Related work: Hurst exponent, box-counting, rescaled range analysis, Ehlers' FRAMA
- Discovered by Jurik in 1996 per his website [8]

**Community status:** Less reverse-engineered than JMA/RSX due to lower popularity. No known complete public clone exists.

### 4.5 DMX (Jurik DMI)

**Purpose:** Ultra-smooth replacement for DMI+, DMI-, and ADX. [6]

**What is known about the algorithm:**
Standard DMI calculation with JMA replacing Wilder's exponential smoothing:

```
DI+ = JMA(+DM) / JMA(TR)
DI- = JMA(-DM) / JMA(TR)
Bipolar_DMI = (DI+ - DI-) / (DI+ + DI-)    // single oscillator, -1 to +1
DMX = JMA(Bipolar_DMI)                       // final smoothing pass
```

Included free with JMA purchase. Straightforward to approximate with any JMA clone. [6][7]

### 4.6 CCX (Jurik CCI)

**Purpose:** Jurik's version of the classic Commodity Channel Index (CCI). "Very smooth and timely." [10]

**What is known:** Replaces CCI's internal moving average with JMA. Listed as "JMA CCX" in platform toolsets — requires JMA. A derivative product, not a standalone core algorithm.

### 4.7 EXI (Price Excursion Index)

**Purpose:** "Quantifies short term market moves." [10]

**What is known:** Listed in the eSignal toolset. No further public documentation on algorithm. Likely measures price displacement from a smoothed baseline over a short window. [inferred]

### 4.8 MFF (Maximally Flat Filter)

**Purpose:** "Great for assessing long term trend." [10]

**What is known:** In DSP theory, a maximally flat magnitude filter is a Butterworth filter — zero ripple in the passband. MFF is likely a Butterworth IIR implementation optimized for financial data, distinct from JMA's adaptive approach. Used for long-term trend assessment rather than short-term tracking. [inferred from DSP theory + product description]

### 4.9 SPX Band

**Purpose:** "Jurik's price band that reflects market's fading exponential memory." [10]

**What is known:** An envelope/band indicator that expands and contracts based on recent volatility with exponential decay weighting. Converted to a stochastic oscillator ("SPX Oscillator") for signal generation. Available with Gap Awareness technology.

### 4.10 Other Products

| Product | Description | Likely Method |
|---------|-------------|---------------|
| WAV | Wavelet-like preprocessor for forecast models | Multi-resolution decomposition [6] |
| DDR | Data dimension reduction for leading indicators | PCA or similar [6] [inferred] |
| AMA | Legacy adaptive MA (pre-JMA) | Simpler adaptive EMA [2] |
| DWMA | Double-weighted moving average, crossover companion to JMA | Weighted MA variant [10] |
| Gap Awareness | Detects discontinuous price jumps and adjusts filter state to prevent distortion | Adaptive speed increase at gap detection [10] |

### 4.11 Composite / Derivative Indicators

The freebies page [10] lists dozens of pre-built indicators bundled with Jurik Tools installations. These are not independent algorithms — they are compositions of the core tools (JMA, RSX, VEL, CFB, DMX) applied in specific configurations. Organized by base tool:

**JMA-based composites:**

| Indicator | Description |
|-----------|-------------|
| JMA reset | JMA that can be forced to jump to current price and resume (e.g., start of each trading day) |
| JMA Fast-K | JMA-based stochastic replacing all four classical stochastics (Fast %K, Slow %K, Fast %D, Slow %D) — differentiated by changing JMA length |
| JMA dStoch | Smooth Fast-K double stochastic, sensitive to market acceleration/deceleration |
| JMA DWMA xover | JMA + double-weighted moving average plotted together for crossover analysis |
| JMA DWMA MACD | MACD-like oscillator measuring JMA-to-DWMA distance |
| JMA MACD reversals | JMA MACD with special band to designate market reversals (NinjaTrader) |
| JMA Keltner Band | Classic Keltner Band with JMA in key calculations |
| JMA Bollinger Band | Classic Bollinger Band with JMA in key calculations |
| JMA + trailing MA | JMA with a trailing MA of choice (EMA, DEMA, TEMA, MMF, Bessel, Butterworth) (eSignal) |
| JMA + trailing MA oscillator | MACD-like difference of above (eSignal) |
| JMA hi-lo band | SPX band around JMA on price (eSignal) |
| JMA hi-lo stochastic | Stochastic derived from JMA position within hi-lo band (eSignal) |
| JMA Phaser | Difference between two JMAs with same speed but different Phase parameter (AmiBroker) |
| JMA / T3 crossover | JMA and Tillson's T3 plotted together for crossover analysis (NinjaTrader) |

**RSX-based composites:**

| Indicator | Description |
|-----------|-------------|
| RSX nogap | RSX with gap compensation |
| RSX double | Blend of fast RSX and slow RSX |
| RSX phased | Blend of fast and slow RSX (MultiCharts variant) |
| RSX on RSX | RSX applied to another RSX output — good for reversals in tight trading ranges |
| RSX on JMA | RSX on JMA-presmoothed price — extends dynamic range, fewer micro reversals |
| RSX for scalping | RSX configured for scalping opportunity detection (NinjaTrader) |
| RSX MACD | MACD-like oscillator from fast/slow RSX difference (NinjaTrader) |
| RSX MACD reversals | RSX MACD with reversal band (NinjaTrader) |
| RSX heat maps | Area color intensity displays RSX+/RSX- strength (eSignal) |

**VEL-based composites:**

| Indicator | Description |
|-----------|-------------|
| VEL nogap | VEL with gap compensation |
| VEL double | Blend of fast VEL and slow VEL |
| VEL on VEL | VEL applied to another VEL — good for reversals in tight ranges |
| VEL for scalping | VEL configured for scalping detection (NinjaTrader) |
| VEL MACD | MACD-like oscillator from fast/slow VEL (NinjaTrader) |

**CFB-based composites:**

| Indicator | Description |
|-----------|-------------|
| CFB 24, 48, 96, 192 | CFB calculated on different lookback windows |
| CFB Spectrum | All four CFB lines plotted together for comparison (eSignal) |
| CFB chan plot | Dynamically expanding/contracting band around price, width modulated by CFB |
| CFB chan index | CFB chan plot converted to oscillator for signal generation |
| CFB dyna band | Dynamic band with JMA-colored bull/bear trend, width modulated by CFB |
| CFB dyna Osc | CFB dyna band converted to oscillator |
| CFB dyna RSX | RSX with dynamic speed controlled by CFB — faster during reversals |
| CFB heat map | CFB with background heat map display (eSignal, NinjaTrader) |

**DMX-based composites:**

| Indicator | Description |
|-----------|-------------|
| DMX nogap | DMX with gap compensation |
| DMX-2 | Newer DMX using "a simpler and more robust algorithm" (eSignal) |
| DMX plus/minus | DMI+ and DMI- components of DMX (NinjaTrader) |
| DMX reversals | DMX with special band for market reversals (NinjaTrader) |
| DMX heat maps | DMX+/DMX- with background heat maps (eSignal, NinjaTrader) |

**Other composites:**

| Indicator | Description |
|-----------|-------------|
| Volatility heat map | Market volatility index with background heat map (NinjaTrader) |
| T3 waterfall | Spread of T3 curves yielding price behavior patterns (NinjaTrader) |
| JMA Spandex Stochastic | Fast %K using Jurik's Spandex Band (AmiBroker) |
| Spandex Band | Jurik's own price band (AmiBroker, requires CFB) |

These composites were available across TradeStation, MultiCharts, eSignal, AmiBroker, NinjaTrader, and Sierra Chart, with platform-specific variations. [10]

### 4.12 TPO (Turning Point Oscillator) — Relationship to Jurik

**TPO is NOT a Jurik Research product.** It was developed and sold by **Custom Trading Solutions, Inc.** (CTS), founded by Brian Bell, based in Littleton, Colorado. CTS operated from approximately 2000 to 2005, selling TPO for CQG and TradeStation at $199/year. [11][12]

CTS's product page described TPO as: "The best momentum oscillator I've ever seen... a very low-lag, quick-turning momentum oscillator with very good smoothing characteristics. It excels when used as a timing indicator. The TPO is based on sophisticated statistical analysis techniques." [12]

CTS also sold "CycleTools for CQG" — indicators based on John Ehlers' cycle analysis work, implemented by Brian Bell. The company's disclaimer explicitly stated: "Custom Trading Solutions, Inc. is not affiliated with" CQG, John Ehlers, or Joe DiNapoli. Notably, no Jurik affiliation disclaimer was included. [12]

**Connection to Jurik (user-reported evidence):**
- A "TPO User Manual" PDF exists bearing the label "Custom Trading Solutions TPO User Manual" — consistent with CTS as the vendor
- TPO code was found in **decompiled Delphi sources** associated with Jurik's codebase [user-reported, unverified]
- This could indicate: (a) CTS licensed Jurik's engine internally for TPO, (b) TPO was later acquired or absorbed by Jurik Research, or (c) both products shared common Delphi-based infrastructure

**Status:** CTS shut down in 2005. The TPO product appears to have been discontinued. No evidence of TPO being sold through Jurik Research's website. The exact nature of the relationship remains unclear. [blocked — insufficient evidence]

---

## 5. How the Indicators Work: Technical Context

### The Core Problem

All linear time-invariant (LTI) filters face a fundamental tradeoff: smoothness vs. lag. A 50-period SMA is smooth but lags 25 bars. An EMA with the same lag is less smooth. This is not a design choice — it is a mathematical constraint of LTI systems. [inferred from standard DSP theory]

### Jurik's Approach: Adaptive Nonlinear Filtering

JMA breaks the LTI constraint by being **nonlinear and time-varying**:
- When price is trending (signal-to-noise is high): reduce smoothing, track closely
- When price is noisy/ranging (signal-to-noise is low): increase smoothing, reject noise
- The transition between modes must be smooth to avoid discontinuities

This is conceptually identical to:
- Alpha-beta-gamma tracking filters (missile guidance)
- Kalman filters with adaptive process noise
- Kaufman's Adaptive Moving Average (KAMA) using efficiency ratio

The difference is implementation quality. JMA's marketing claims superiority over KAMA, VIDYA, and other published adaptive filters [6] — plausibly because it uses a more sophisticated adaptivity measure and/or multi-stage cascaded filtering. [inferred]

### The Phase Parameter

The Phase parameter (-100 to +100) controls a lag-overshoot tradeoff:
- Phase = +100: minimum lag, may overshoot on reversals
- Phase = 0: balanced
- Phase = -100: maximum smoothness, more lag

In filter theory terms, this likely adjusts the damping ratio of the IIR poles. Low damping = fast response but ringing. High damping = no ringing but slower. [inferred from standard filter theory]

### Why the Algorithm Remains Secret

Jurik's competitive advantage is the specific adaptive mechanism — how the filter detects market regime changes and modulates its coefficients. The general architecture (cascaded adaptive IIR) is inferable from reverse-engineering [7], but the exact adaptation law, its parameters, and edge-case handling (gaps, spikes, regime transitions) are the trade secret.

---

## 6. Interviews, Reviews, and Media Appearances

Jurik Research maintained an unusually low public profile for a company active since 1988. Mark Jurik gave few interviews, never published under his own name in trade journals, and produced no video content. What press coverage exists was curated on the company's own website [9] and spans 1992 to 2010.

### 6.1 Press Releases and Early Announcements

The earliest known public statement is a June 1992 press release titled **"Star Wars Mathematics"**, announcing AMA (the predecessor to JMA). Key quote from Mark Jurik: "There were no compromises in the development of our MOVING AVERAGE indicator, AMA. AMA utilizes concepts in Robotics and Information Theory. AMA attains a smooth estimate of market price with low lag." The release notes that "numerous statisticians and mathematicians have requested AMA's mathematical formula" and "a handful have paid a significant fee for the actual algorithm" — establishing the secrecy-as-business-model approach from day one. AMA was priced at $205 [9].

### 6.2 Magazine Reviews

**Futures Magazine (January 1995):** Reviewed DDR, AMA, and WAV modules, awarding near-perfect scores (4/4 "Excellent" across categories). AMA is the direct predecessor to JMA, suggesting the core technology was already mature by 1994 [9].

**Technical Analysis of Stocks & Commodities (April 1999):** Reviewed JMA, VEL, and CFB favorably. The reviewer noted of VEL: "a number of key turning points are quickly picked up by VEL." On usability: "working in Excel and the Jurik indicators is a breeze." Jurik tools also won TASC Readers' Choice Awards across multiple categories from 1999 through 2012 [9].

**Financial Software Review (2000):** The most substantive independent review found. The reviewer tested JMA against SMA and EMA on a DAX futures intraday chart, finding JMA "far more responsive." A crude day-trading system comparison showed JMA produced "roughly twice the number of winning trades and seventy percent greater net profit" versus SMA/EMA crossover systems. The review discusses the Phase parameter (-100 to +100) in detail, noting its effect on lag-vs-overshoot tradeoffs, and concludes the algorithm includes "some form of signal processing filter for removing noise" prior to averaging. Final assessment: "At $205, the JMA package is good value... this is the sort of tool that could add significant value on any trading desk" [21].

### 6.3 Interviews

**Wall Street Harvest (2000):** A brief article on sector analysis when trading securities. The content is available only as an embedded image (GIF) on Jurik's website, making full-text extraction impossible [9].

**Trader's Magazine of Germany (March 2010):** Topics listed include: how Jurik Research came about, why JMA is different from other moving averages, risk and money management, common features in custom trading strategies, testing and validating trading systems, and advice for novices and professionals. The article also contains an anecdote about "getting lost riding the New York subway, ultimately taking a stroll in a tuxedo, at night, through Harlem" — one of very few personal anecdotes in any public source. Available only as an embedded image (GIF, in German) [9].

### 6.4 Industry Articles

**MARHedge (November 21, 2005):** "Eliminating Lag, part II" — discusses the philosophy behind Jurik's indicators and includes charts comparing JMA and RSX to classical technical analysis tools. The article interviews **Landmark Asset Management** on their use of VEL and RSX to manage **$18 million** in assets. This is the only known reference to an institutional user citing specific Jurik tools by name with disclosed AUM [9].

### 6.5 Lectures and Presentations

**Futures International Conference (1995):** Jurik delivered a lecture titled "Space, Time, Cycles & Phase" covering four perspectives on market data: Space (geometric perspective, decorrelation), Time (optimal sampling, temporal compression), Cycles (filtering, frequency spectrum, low-lag smoothing), and Phase (phase-shifting MACD, phase diagrams). A recording was later sold as an MP3-on-CD audio seminar [22].

**Society for the Advancement of Management Technology (SAMT), year 2000:** Annual meeting presentation. Listed on press page but no further details available [9].

**Austin Association of Financial Traders (February 2010):** Lecture topics included representing market dynamics in high-dimensional space, semi-chaotic behavior and nodes of stability between regime changes, market noise effects, spatio-temporal compression, and "amazingly simple trading strategies that work." A feedback letter exists on the Jurik website but its content is available only as an image [9].

### 6.6 Educational Media

**NeuroTapes:** A 12-hour video course on neural network technology applied to trading. Sold worldwide for 11 years. Referenced in multiple product guides and third-party document archives. A ZoomInfo profile confirms: "As a lecturer and instructor for over a decade, Mark's presentations covered both the theoretical and practical aspects of neural network technology" [22].

**"Space, Time, Cycles & Phase" (audio seminar):** Recording of the 1995 Futures International conference lecture. Catalog page includes audience feedback quotes. Topics align closely with Jurik's military ELINT signal processing background [22].

**Math Contest (2009):** Jurik Research sponsored a geometry contest with prize money, judged by Mark Jurik for "elegance and simplicity," with an additional prize for the best suggestion on applying the geometric property to signal processing [9].

### 6.7 TASC Readers' Choice Awards

Jurik tools won awards in the following categories across multiple years (1999-2012): Add-On Software, Analytical Software, and "Best of" categories. The awards indicate sustained recognition within the retail technical analysis community over a 13-year span [9].

### 6.8 Online Discussion

**Elite Trader, "Why are quants afraid of Mark Jurik?" (October 2010):** A 9-page thread revealing community perceptions. Notable claims: [23]

- kut2k2 observed Jurik has "almost zero presence on wilmott.com" despite being widely discussed on retail trading forums — suggesting his audience was retail, not institutional quant.
- dandxg claimed to have "personally seen reverse engineered JMA, and RSX that are identical to the real thing and they were mediocre."
- dtrader98 described seeing "a proprietary version of his algorithm reconstructed, but it wasn't anything unusually special, it ended up being something like a 7 tap FIR" — a characterization inconsistent with the actual decompiled algorithm (which is adaptive IIR, not static FIR).
- LeeD noted that filtering is "one of the most important things in higher-frequency auto-trading" and that practitioners who build their own filters are "extra cautious about everything that is proprietary."
- Random.Capital claimed "HMA supersedes it" — debatable given HMA lacks any adaptive component [inferred].

### 6.9 Absence of Video and Social Media

No YouTube videos by Mark Jurik or Jurik Research exist. No official social media accounts have been identified. One third-party YouTube video ("Jurik Moving Average (JMA) Explained," December 2025, 7:04 duration) discusses the indicator but does not feature Jurik. The company's entire public communication channel was its website.

---

## 7. Reverse-Engineering Attempts

The JMA algorithm has never been officially published. Over two decades, multiple independent efforts have attempted to reconstruct it — ranging from direct DLL decompilation to simplified approximations. These efforts split into two distinct tiers: **full decompilations** that reveal the adaptive volatility mechanism, and **simplified clones** that capture only the static three-stage EMA structure.

### 7.1 Tier 1: Full Decompilation — Weld (2005-2008)

The earliest and most significant reverse-engineering was performed by a user known as **"Weld"** (real name Igor; website: `weld.torguem.net`), who decompiled Jurik's compiled DLL. The results were posted on the ForexTSD forum (thread #164, now archived at `mql5.com/en/forum/173010`) on 2005-10-28 by moderator Sergey Golubev ("newdigital"). [7][13]

In November 2008, Weld published a standalone PDF summarizing his findings in clean mathematical notation, titled "Good news for all of you — JMA's algorithm revealed!" [19]. This document classifies JMA as a **"triple adaptive filter with unique Jurik smoothing and dynamic factor"** and provides the clearest public description of the algorithm's mathematical structure. Weld notes he spent "months" studying the decompiled code to produce this description, and explicitly dismissed an earlier Russian article by Alexander Smirnov et al. in *Spekulant* magazine as inaccurate ("real JMA has nothing common with described in the article"). [19]

The decompilation revealed that JMA is **not** a simple moving average variant but a complex multi-stage adaptive filter with three major components:

**Component 1 — Parameter initialization:**

```
lengthParam = (Length - 1) / 2.0
phaseParam  = Phase / 100.0 + 1.5       // clamped to [0.5, 2.5]
logParam    = log(sqrt(lengthParam)) / log(2.0) + 2.0
sqrtParam   = sqrt(lengthParam) * logParam
lengthDivider = (lengthParam * 0.9) / (lengthParam * 0.9 + 2.0)
```

**Component 2 — Adaptive volatility estimation (the core trade secret):**

This is what separates JMA from every public adaptive filter. The algorithm maintains a **128-element sorted list** and a **10-element ring buffer** to compute a running trimmed-percentile volatility estimate:

```
// Per bar:
absValue = max(|price - paramA|, |price - paramB|)
dValue   = absValue + 1e-10

// Ring buffer tracks recent volatility samples
cycleDelta += dValue - ring2[counterB]
ring2[counterB] = dValue

// After 10 bars: highDValue = cycleDelta / 10
// After 127 bars: binary search inserts highDValue into sorted list[128]
//   maintaining indices s38 (upper bound) and s40 (lower bound)
// lowDValue = sum of list[s40..s38]  (trimmed interior sum)

// Adaptive smoothing exponent:
powerValue = max(0.5, logParam - 2.0)
dValue = min(logParam, (absValue / (lowDValue / (s38 - s40 + 1)))^powerValue)
dValue = max(1, dValue)
powerValue = sqrtDivider ^ sqrt(dValue)   // final adaptive alpha
```

The sorted list is effectively a **running percentile filter** for volatility — robust against outliers and spikes. When volatility is low relative to the trimmed estimate (trending market), `dValue` increases and the filter speeds up. When volatility is high relative to the median (choppy market), `dValue` stays near 1 and the filter smooths aggressively. [13][14]

**Component 3 — Three-stage adaptive cascade (the actual smoothing):**

```
fC0 = (1 - powerValue) * price + powerValue * fC0[prev]
fC8 = (price - fC0) * (1 - lengthDivider) + lengthDivider * fC8[prev]
fA8 = (phaseParam * fC8 + fC0 - JMA[prev])
      * (powerValue^2 - 2*powerValue + 1)
      + powerValue^2 * fA8[prev]
JMA = JMA[prev] + fA8
```

Stage 1 (`fC0`) is an adaptive EMA whose speed varies per bar. Stage 2 (`fC8`) tracks the deviation between raw price and the first EMA — this is the momentum/error signal. Stage 3 (`fA8`) combines the phase-shifted estimate (`fC0 + phaseParam * fC8`) with a second-order adaptive smoothing loop, accumulated into the final JMA output. The Phase parameter controls the weight of the momentum term: higher phase means more lead (and potential overshoot). [13][14]

**Validation:** The ForexTSD community validated the decompilation by visual comparison against the official Jurik DLL output. The thread spans 46 pages (2005-2011+) with extensive discussion. Newdigital noted: "I think some of Jurik indicators may be with small errors. Because all the indicator posted here was created to be Jurik indicators." — acknowledging approximation but functional fidelity. [13]

**Weld's 2008 Mathematical Summary [19]:**

Weld's PDF distills the decompiled code into three named stages plus the adaptive mechanism:

*Stage 1 — Adaptive EMA:*
```
MA1 = (1-alpha)*Price + alpha*MA1[1]
```

*Stage 2 — Kalman-style correction:*
```
Det0 = (Price - MA1)*(1-beta) + beta*Det0[1]
MA2 = MA1 + PR*Det0
```

*Stage 3 — Jurik adaptive filter (final output):*
```
Det1 = (MA2 - JMA[1]) * (1-alpha)^2 + alpha^2 * Det1[1]
JMA = JMA[1] + Det1
```

Where `beta = 0.45*(Length-1) / (0.45*(Length-1)+2)` and `PR` (Phase Ratio) = `Phase/100 + 1.5`, clamped to [0.5, 2.5].

The dynamic factor `alpha = beta^pow` where `pow = rVolty^pow1`, with `rVolty` being the ratio of instantaneous volatility to a 65-bar average volatility. Volatility itself is measured via proprietary "Jurik Bands" — asymmetric envelopes that expand/contract based on `Kv = beta^sqrt(pow2)`. Weld notes these bands "can be a basis for trend following indicator like Wilder's Parabolic." [19]

Weld's PDF also describes two companion MQL4 indicators (`JurikFilter_v2` with 4 filter modes showing each stage, and `JurikVolty_v1` displaying volatility and bands), and includes annotated charts showing all stages overlaid on price. [19]

### 7.2 Tier 1: Full Decompilation — Starlight (Oleg Anashkin, date unknown)

A second, independent full decompilation was performed by a developer using the handle **"Starlight"** (email: extesy@yandex.ru), identified as **Oleg Anashkin** (GitHub: `github.com/extesy`). A collaborator known as "_landy" (_al@bk.ru) compiled the resulting Delphi code into a DLL plugin for **Wealth-Lab**, an institutional-grade backtesting platform. [20]

This is the **most comprehensive decompilation known** — covering 11 distinct indicators (vs. Weld's JMA + RSX), with full Delphi Object Pascal source code plus WealthScript wrappers. The code targets Wealth-Lab's COM interface via type libraries.

**Provenance status:** No public URL found. Neither "starlight jurik" nor "extesy" + trading terms return search results. The code was likely distributed privately or on now-defunct forums. Oleg Anashkin's public GitHub (134 followers, known for HoverZoom Chrome extension) contains no trading-related repositories. Classification: **UNVERIFIED — no public distribution found.** [20]

**Files:**
- `Calc.pas` (~1254 lines) — All indicator algorithms
- `Indicator.pas` — Wealth-Lab COM wrapper (12 exported procedures)
- `Jurik_TLB.pas` / `WealthLab_TLB.pas` — Type libraries
- WealthScript wrappers (.WS) — Direct implementations and adaptive-length variants (aJ*.ws)

**JMA implementation** — Matches Weld's decompilation exactly: same 128-element sorted list, 10-element ring buffer, 62-element initialization buffer, binary search insertion, trimmed-percentile volatility, and three-stage adaptive cascade. Variable naming differs (f-prefixed floats, s-prefixed integers) but the algorithm is structurally identical.

**The unique value of Starlight is the 10 additional indicators not covered by Weld:**

---

#### 6.2.1 JCFB — Composite Fractal Behavior

**Purpose:** Estimates the dominant cycle period of a time series using a multi-scale fractal decomposition.

**Architecture:** Parallel bank of sub-filters at geometrically-spaced lookback depths, with cascading residual-weight allocation.

**Variants by maximum period:**
| Variant | Sub-filters | Depths |
|---------|-------------|--------|
| JCFB24 | 8 | 2, 3, 4, 6, 8, 12, 16, 24 |
| JCFB48 | 10 | + 32, 48 |
| JCFB96 | 12 | + 64, 96 |
| JCFB192 | 14 | + 128, 192 |

**Algorithm (pseudocode):**

```
function JCFBaux(price[], depth, bar):
    // Compute weighted-deviation ratio at specific lookback
    sum_weighted = 0, sum_weight = 0
    for i = 0 to depth-1:
        weight = depth - i  // linear decay
        sum_weighted += weight * |price[bar-i] - price[bar-depth]|
        sum_weight += weight
    avg_dev = sum_weighted / sum_weight
    range = highest(price, depth) - lowest(price, depth)
    return avg_dev / (range + epsilon)

function JCFB(price[], maxPeriod, bar):
    // Compute weight for each sub-filter
    for i = 0 to N-1:
        w[i] = JCFBaux(price, depths[i], bar)

    // Cascading residual-weight allocation
    // Even indices processed coarse-to-fine, odd separately
    // Normalize: w[i] = w[i] / sum(w)

    // Weighted-mean dominant cycle period:
    result = sum(w[i]^2 * depths[i]) / sum(w[i]^2)
    return result
```

**DSP interpretation:** JCFB is a spectral estimator — it decomposes price action across multiple time scales and returns a single "dominant period" value. The squared-weight aggregation emphasizes scales where the fractal signature is strongest. This is conceptually similar to MESA (Maximum Entropy Spectral Analysis) but uses a deterministic filter bank rather than autoregressive modeling.

---

#### 6.2.2 JRSX — Jurik RSX (Relative Strength Index)

Matches the known triple-cascaded lag-reduced EMA architecture documented in section 7.5. The Starlight implementation (`JXRSXSeries` in Calc.pas) adds an **adaptive-length variant** that accepts a per-bar length series, applying the same triple cascade but recomputing `Kg = 3/(Length[bar]+2)` at each bar.

---

#### 6.2.3 JCCX — Jurik CCI Analog

**Algorithm:**
```
JCCX = (JMA(price, 4, phase=0) - JMA(price, Length, phase=0))
       / (1.5 * MeanAbsDev(diff, 3*Length))
```

Where `diff = JMA(price,4,0) - JMA(price,Length,0)` and the mean absolute deviation is computed over a `3*Length` bar window.

**DSP interpretation:** This is a CCI (Commodity Channel Index) constructed entirely from JMA-smoothed components. The fast JMA (period=4) tracks price closely while the slow JMA (period=Length) provides the baseline. Normalization by 1.5× MAD maps the output to approximate [-100, +100] scaling, matching CCI conventions.

---

#### 6.2.4 JTPO — Jurik Turning Point Oscillator

**Algorithm:**
```
function JTPO(price[], Length, bar):
    // Extract window
    window = price[bar-Length+1 .. bar]

    // Sort and assign ranks (with tie-averaging)
    sorted = sort(window)
    for each value in window:
        rank[i] = position_in_sorted + average_of_ties

    // Spearman rank correlation: price rank vs. time rank
    // Time ranks are simply 1, 2, ..., N
    N = Length
    d_squared_sum = sum((rank[i] - i)^2 for i=1..N)
    rho = 1 - (6 * d_squared_sum) / (N * (N^2 - 1))

    // Alternative computation in code uses:
    // 12 / (N*(N-1)*(N+1)) scaling factor
    return rho  // scaled to [-1, +1]
```

**DSP interpretation:** JTPO measures the monotonicity of price over a window. A value near +1 means price has been steadily rising (perfectly ordered); -1 means steadily falling. Near 0 means no trend. This is identical to Spearman's rank correlation coefficient between price and time — a non-parametric trend strength measure that is robust to outliers.

**Note:** Despite the name matching "TPO" (sold by Custom Trading Solutions Inc.), the algorithm here is clearly Jurik's own implementation within his DLL suite.

---

#### 6.2.5 JVEL — Jurik Velocity

**Purpose:** A smoothed velocity (rate of change / regression slope) indicator with a proprietary adaptive smoother.

**Architecture:** Two stages — `JVELaux1` (weighted least-squares slope) and `JVELaux3` (adaptive smoothing).

**Stage 1 — JVELaux1 (regression slope):**
```
function JVELaux1(price[], depth, bar):
    // Weighted least-squares slope over [bar-depth+1 .. bar]
    // Weights are linear (higher for more recent)
    sum_wx = 0, sum_w = 0, sum_wxx = 0, sum_wy = 0, sum_wxy = 0
    for i = 0 to depth-1:
        w = depth - i
        x = i
        y = price[bar - depth + 1 + i]
        sum_w += w; sum_wx += w*x; sum_wy += w*y
        sum_wxx += w*x*x; sum_wxy += w*x*y
    slope = (sum_w*sum_wxy - sum_wx*sum_wy) / (sum_w*sum_wxx - sum_wx^2)
    return slope
```

**Stage 2 — JVELaux3 (Jurik adaptive smoother — novel filter):**
```
function JVELaux3(input[], period, bar):
    // Maintains:
    //   - 100-element circular buffer (history)
    //   - Running linear regression for trend estimation
    //   - MAD (mean absolute deviation) for volatility
    //   - Exponential response function for adaptation

    buffer[pos] = input[bar]
    pos = (pos + 1) mod 100

    // Linear regression over min(bar, 100) samples for trend
    trend_slope = linreg_slope(buffer, available_samples)

    // MAD = mean(|buffer[i] - linear_trend[i]|) over buffer
    mad = mean_absolute_deviation_from_trend(buffer)

    // Adaptive step:
    error = input[bar] - smoothed[bar-1]
    response = 1 - exp(-|error| / (mad * period + epsilon))
    smoothed[bar] = smoothed[bar-1] + sign(error) * |error| * response

    return smoothed[bar]
```

**DSP interpretation:** Stage 2 is a **novel adaptive filter** distinct from JMA. Where JMA uses a sorted-list percentile estimator, JVEL's smoother uses MAD-normalized exponential response. The function `1 - exp(-|error|/volatility/period)` creates a response curve that:
- Passes large moves through quickly (response → 1 when error >> volatility)
- Heavily smooths small moves (response → 0 when error << volatility)

This is reminiscent of Hampel's influence function in robust statistics — a soft-clipping adaptive gain. This mechanism is NOT documented anywhere in the public literature on Jurik indicators.

---

#### 6.2.6 JXVEL — Adaptive-Depth Velocity

Same as JVEL but accepts a per-bar depth series (from JCFB or other source), recomputing the regression slope at variable lookback depths. This enables the velocity estimate to automatically adjust its measurement window to the dominant cycle.

---

#### 6.2.7 JAVEL — Adaptive Velocity (Auto-Depth)

**Purpose:** Wraps JXVEL with an automatic depth selector based on volatility regime.

**Algorithm:**
```
function JAVEL(price[], LoLen, HiLen, Sensitivity, bar):
    // Compare long-term vs short-term average absolute change
    avg100 = mean(|price[i] - price[i-1]| for i in [bar-99..bar])
    avg10  = mean(|price[i] - price[i-1]| for i in [bar-9..bar])

    // Log-ratio sensitivity transform
    ratio = ln((epsilon + avg100) / (epsilon + avg10))
    scaled = Sensitivity * ratio

    // Squashing function: maps to (-1, +1)
    squashed = scaled / (1 + |scaled|)

    // Map to depth range
    depth = LoLen + (HiLen - LoLen) * (squashed + 1) / 2

    // Feed into JXVEL
    return JXVEL(price, depth, period=3, bar)
```

**DSP interpretation:** When short-term volatility exceeds long-term (avg10 > avg100), the ratio is negative, squash output is negative, and depth decreases toward LoLen (faster response). When markets calm (avg10 < avg100), depth increases toward HiLen (more smoothing). The `x/(1+|x|)` squashing function is a computationally cheap sigmoid alternative.

---

#### 6.2.8 JARSX — Adaptive RSX

Uses the same JAVEL-style sensitivity/depth mechanism but feeds the adaptive length into JXRSX (adaptive-length RSX) instead of JXVEL. Parameters: LoLen, HiLen, Sensitivity.

---

#### 6.2.9 JDMX / JDMXP / JDMXM — Jurik Directional Movement

**Purpose:** Jurik's version of Wilder's ADX/DMI system, with JMA replacing Wilder's EMA.

**Algorithm:**
```
// Directional Movement (identical to Wilder's definition):
upMove   = high[bar] - high[bar-1]
downMove = low[bar-1] - low[bar]
DMplus   = (upMove > downMove AND upMove > 0) ? upMove : 0
DMminus  = (downMove > upMove AND downMove > 0) ? downMove : 0
TR       = TrueRange(high, low, close, bar)

// JMA smoothing (phase=-100 = maximum lag / maximum smoothness):
smoothDMplus  = JMA(DMplus, Length, phase=-100)
smoothDMminus = JMA(DMminus, Length, phase=-100)
smoothTR      = JMA(TR, Length, phase=-100)

// Directional indicators:
JDMXP = 100 * smoothDMplus / smoothTR    // equivalent to +DI
JDMXM = 100 * smoothDMminus / smoothTR   // equivalent to -DI

// Combined oscillator:
JDMX = 100 * (JDMXP - JDMXM) / (JDMXP + JDMXM + epsilon)
```

**DSP interpretation:** Wilder's original DMI uses a simple EMA (his "smoothed moving average" = EMA with alpha=1/N). Jurik replaces this with full adaptive JMA, gaining the benefit of adaptive volatility-based smoothing. Phase=-100 selects maximum smoothness (no lead/overshoot), appropriate for a volatility-normalized ratio indicator where noise reduction matters more than responsiveness.

---

#### 6.2.10 JVELCFB — Velocity with Fractal-Driven Depth

**Purpose:** Combines JVEL with JCFB to create a velocity indicator whose measurement depth is automatically driven by the dominant cycle period.

**Algorithm:**
```
function JVELCFB(price[], LoDepth, HiDepth, CFBperiod, bar):
    // Compute dominant cycle via JCFB
    cfb_raw = JCFB(price, CFBperiod, bar)

    // Normalize to [0, 1] using running min/max
    cfb_min = running_min(cfb_raw, lookback)
    cfb_max = running_max(cfb_raw, lookback)
    cfb_norm = (cfb_raw - cfb_min) / (cfb_max - cfb_min + epsilon)

    // Map to depth range
    depth = LoDepth + (HiDepth - LoDepth) * cfb_norm

    // Feed into JXVEL with period=3
    return JXVEL(price, depth, period=3, bar)
```

**DSP interpretation:** This is the most sophisticated indicator in the suite — a velocity estimator whose lookback window automatically matches the dominant market cycle. When JCFB detects short cycles, the velocity uses a short regression window (capturing fast moves). When JCFB detects long cycles, it uses a long window (filtering noise in slow trends). The period=3 for the adaptive smoother keeps the final smoothing minimal.

---

#### 6.2.11 Summary: Starlight vs. Weld

| Aspect | Weld (2005-2008) | Starlight |
|--------|-----------------|-----------|
| Language | MQL4 | Delphi Object Pascal |
| Platform | MetaTrader 4 | Wealth-Lab |
| Indicators covered | JMA, RSX | JMA, JRSX, JCFB, JCCX, JTPO, JVEL, JAVEL, JDMX, JDMXP, JDMXM, JVELCFB |
| JMA algorithm | Identical | Identical |
| Novel discoveries | — | JVEL adaptive smoother (exponential response function), JCFB spectral estimator, JAVEL auto-depth mechanism |
| Public availability | ForexTSD/MQL5 forums | None found |
| Date | 2005-2008 (documented) | Unknown |
| Author identity | "Weld" / Igor | Oleg Anashkin ("Starlight") |

The Starlight decompilation confirms Weld's JMA work independently and extends coverage to Jurik's full indicator suite. The most significant new discovery is the **JVEL adaptive smoother** — a novel adaptive filtering mechanism (MAD-normalized exponential response) distinct from both JMA's sorted-list approach and standard adaptive filters in the DSP literature.

---

### 7.3 Tier 1: Full Decompilation — AmiBroker AFL Port (regtrading.com)

A complete translation of the decompiled algorithm to AmiBroker Formula Language (AFL) was published at regtrading.com, attributed to "a German programmer" who translated it from MT4. The author tested it against the official JMA plugin and reported: "the results are the same/accurate (if I'm not mistaken) but there are drawbacks, maybe because the translation is not perfect, sometimes we got an error." [14]

This implementation preserves all three components of the full algorithm — the 128-element sorted list, the ring buffers, the adaptive power calculation — making it the most complete non-MQL port. The AFL code is approximately 200 lines and includes proper initialization handling. [14]

### 7.4 Kositsin's Library Functions (2005-2007)

**Nikolay Kositsin** (username "GODZILLA," Khabarovsk, Russia) took the decompiled JMA/RSX algorithms and packaged them into reusable MQL4 library functions, published in February 2007 as "Effective Averaging Algorithms with Minimal Lag: Use in Indicators." [7]

His libraries provide:

| Function | Description |
|----------|-------------|
| `JJMASeries()` | Full adaptive JMA (Weld's decompilation) |
| `JLiteSeries()` | JMA without adaptive volatility component |
| `JurXSeries()` | RSX ultralinear smoothing (see 6.6) |
| `ParMASeries()` | Parabolic approximation smoothing |
| `LRMASeries()` | Linear regression smoothing |
| `T3Series()` | Tilson T3 smoothing |

Kositsin's copyright headers explicitly acknowledge: `"JMA code: Copyright 2005, Jurik Research"`. His contribution was primarily engineering — proper state management, multi-instance support, and EA compatibility. These functions form the basis for most subsequent JMA implementations across all platforms. [7]

### 7.5 Tier 2: Simplified Approximation — everget (2018)

The most widely used JMA clone was published on TradingView by **everget** (Alexander, Pine Wizard) in October 2018. With 2,400+ favorites and 66,000+ chart uses, it is the de facto reference implementation in the retail trading community. everget's disclaimer: "If Mr. Jurik ask me to remove this indicator from public access then I will do it." [15]

The algorithm **strips out the entire adaptive volatility mechanism** and uses fixed coefficients:

```pine
// Pine Script (TradingView) — everget's JMA
length = input(7)
phase  = input(50)
power  = input(2)

phaseRatio = phase < -100 ? 0.5 : phase > 100 ? 2.5 : phase / 100 + 1.5
beta  = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
alpha = pow(beta, power)

e0 = 0.0
e0 := (1 - alpha) * close + alpha * nz(e0[1])

e1 = 0.0
e1 := (close - e0) * (1 - beta) + beta * nz(e1[1])

e2 = 0.0
e2 := (e0 + phaseRatio * e1 - nz(jma[1])) * pow(1 - alpha, 2)
      + pow(alpha, 2) * nz(e2[1])

jma = 0.0
jma := nz(jma[1]) + e2
```

This captures the three-stage cascade structure correctly but makes `alpha` and `beta` **static** — they never change based on market conditions. The real JMA's `powerValue` varies per bar via the sorted-list volatility estimator. This means everget's version:
- Performs identically to the real JMA in trending markets where volatility is stable
- Diverges in choppy or transitional markets where the adaptive mechanism matters most
- Has no equivalent to the sorted-list volatility component at all [15]

All subsequent ports — PHP (`romulodl/jma`), Python (`pandas-ta`), thinkScript, and others — derive from this simplified structure rather than from the full decompilation. [16][17]

### 7.6 JRSX Decompilation — Weld (2005)

The RSX (Jurik RSI) decompilation revealed a different architecture from JMA. Rather than adaptive volatility, RSX uses a **triple-cascaded lag-reduced EMA** applied to both signed and absolute price changes:

```
Kg = 3.0 / (Length + 2.0)
Hg = 1.0 - Kg

// Each stage: EMA1 → EMA2 → output = 1.5*EMA1 - 0.5*EMA2
// Applied 3 times to signed changes (→ v14)
// Applied 3 times to absolute changes (→ v20)

// Stage 1:
f28 = Hg*f28 + Kg*change;     f30 = Kg*f28 + Hg*f30
v0C = 1.5*f28 - 0.5*f30

// Stage 2:
f38 = Hg*f38 + Kg*v0C;        f40 = Kg*f38 + Hg*f40
v10 = 1.5*f38 - 0.5*f40

// Stage 3:
f48 = Hg*f48 + Kg*v10;        f50 = Kg*f48 + Hg*f50
v14 = 1.5*f48 - 0.5*f50

// Same 3 stages for |change| → v20
// Final: RSX = (v14/v20 + 1.0) * 50    (clamped to 0-100)
```

The `1.5*EMA1 - 0.5*EMA2` pattern at each stage is a standard lag-elimination technique — linear extrapolation from two EMAs to cancel first-order lag. Applied three times, it creates a 6th-order filter with very low lag but **no adaptive component**. RSX's smoothness comes from filter order, not from runtime adaptation. [7][13]

### 7.7 The Gaussian Filter Hypothesis — bigboss/useThinkScript (2022)

A different hypothesis was proposed on the useThinkScript forum: that JMA is essentially a **two-pole Gaussian filter** as described in John Ehlers' "Gaussian Filters" paper (mesasoftware.com). [18]

```thinkscript
// Two Pole Gaussian Filter (proposed as JMA equivalent)
input length = 7;
input n = 2.0;

def w = (2 * Double.Pi / length);
def beta1 = (1 - Cos(w)) / (Power(1.414, 2.0 / n) - 1);
def alpha1 = (-beta1 + Sqrt(beta1 * beta1 + 2 * beta1));
def g = power(alpha1, 2) * close
        + 2 * (1 - alpha1) * g[1]
        - power(1 - alpha1, 2) * g[2];
```

The poster ("bigboss") noted it is "very close to the jma on tradingview" and "faster than the hull of equivalent length by a bar or two." This hypothesis conflates the output appearance with the mechanism — a Gaussian filter can produce visually similar smooth output but lacks JMA's adaptive volatility behavior entirely. It is a fixed-coefficient IIR filter. [18]

### 7.8 Academic Treatment

JMA is consistently excluded from academic comparative studies. Raudys, Lenciauskas & Malcius (2013, "Moving averages for financial data smoothing," cited 94 times) surveyed 19 moving averages and explicitly noted: "Proprietary moving averages (like Jurik Moving Average) are discarded from this study." No academic paper has published a decompiled or verified JMA algorithm. [inferred from literature survey]

### 7.9 Summary: What Reverse-Engineering Revealed

| Aspect | Full Decompilation (Weld) | Simplified Clone (everget) |
|--------|--------------------------|---------------------------|
| Three-stage cascade | Yes | Yes |
| Phase parameter | Yes | Yes |
| 128-element sorted list | Yes | **No** |
| 10-element ring buffer | Yes | **No** |
| Adaptive per-bar alpha | Yes | **No** (static) |
| Trimmed-percentile volatility | Yes | **No** |
| Power parameter | Via adaptive exponent | Via `beta^power` (static) |
| Accuracy vs. official JMA | High (community-validated) | Approximate — matches in trending, diverges in chop |
| Code availability | MQL4, AmiBroker AFL | Pine Script, Python, PHP, thinkScript |

The fundamental discovery: JMA's competitive advantage is not the three-stage EMA cascade (which is straightforward) but the **sorted-list volatility estimator** that drives adaptive coefficient modulation. This mechanism — a running percentile filter over 128 samples — is robust, computationally efficient, and not obvious from the filter's external behavior. It is the component that most public clones omit. [7][13][14]

---

## Sources

| # | URL | Verification | Date |
|---|-----|-------------|------|
| [1] | http://jurikres.com/gifs1/portrait3.jpg | unverified — path derived from page source; domain reachable via HTTP | 2026-05-03 |
| [2] | http://jurikres.com/about/company.htm | verified — HTTP 200 | 2026-05-03 |
| [3] | http://jurikres.com/about/presents.txt | verified — HTTP 200 | 2026-05-03 |
| [4] | http://jurikres.com/catalog1/cat_pub.htm | verified — HTTP 200 | 2026-05-03 |
| [5] | http://technical.traders.com/archive/combo/display5.asp?author=Mark%20Jurik | verified — returns "file not found" (confirms absence) | 2026-05-03 |
| [6] | https://web.archive.org/web/20230929125129/http://jurikres.com/catalog1/ms_ama.htm | verified — Wayback Machine snapshot | 2026-05-03 |
| [7] | https://www.mql5.com/en/articles/1450 | verified — HTTP 200 | 2026-05-03 |
| [8] | https://web.archive.org/web/20240529191401/http://jurikres.com/catalog1/ms_cfb.htm | verified — Wayback Machine snapshot | 2026-05-03 |
| [9] | http://jurikres.com/press/mainpres.htm | verified — HTTP 200 | 2026-05-03 |
| [10] | http://jurikres.com/freebies1/mainfree.htm | verified — HTTP 200 | 2026-05-03 |
| [11] | http://day.traders.com/Products/display.asp?dbname=software%5Csoftware&prodid=598&tablename=soft_quest | verified — HTTP 200 | 2026-05-03 |
| [12] | https://web.archive.org/web/20021210102803/http://www.customtradingsolutions.com/cts_products.htm | verified — Wayback Machine snapshot | 2026-05-03 |
| [13] | https://www.mql5.com/en/forum/173010 | verified — ForexTSD thread archive (46 pages, Weld's JMA decompilation) | 2026-05-03 |
| [14] | https://regtrading.com/the-real-jurik-moving-average-jma/ | verified — HTTP 200, full AmiBroker AFL JMA implementation | 2026-05-03 |
| [15] | https://www.tradingview.com/script/nZuBWW9j/ | verified — everget's JMA, 2,400+ favorites, 66K+ chart uses | 2026-05-03 |
| [16] | https://github.com/romulodl/jma | verified — PHP port of everget's algorithm | 2026-05-03 |
| [17] | https://pypi.org/project/pandas-ta/ | verified — Python library with JMA implementation | 2026-05-03 |
| [18] | https://usethinkscript.com/threads/jurik-moving-average.9817/ | verified — HTTP 200, Gaussian filter hypothesis thread | 2026-05-03 |
| [19] | https://c.mql5.com/forextsd/forum/164/jurik_1.pdf | verified — PDF, Weld's 2008-11-27 mathematical summary of JMA decompilation | 2026-05-03 |
| [20] | N/A — no public URL found | unverified — Delphi source code by "Starlight" (Oleg Anashkin, extesy@yandex.ru); GitHub: github.com/extesy; compiled by "_landy" (_al@bk.ru) for Wealth-Lab; no public distribution discovered | 2026-05-03 |
| [21] | http://jurikres.com/press/financialsoftwarereview.htm | verified — HTTP 200, full review text | 2026-05-03 |
| [22] | http://jurikres.com/catalog1/cat_pub.htm | verified — HTTP 200, publications/audio seminar catalog | 2026-05-03 |
| [23] | https://www.elitetrader.com/et/threads/why-are-quants-afraid-of-mark-jurik.205765/ | verified — 9-page thread, Oct 2010 | 2026-05-03 |

Claims marked `[inferred]` are analytical conclusions drawn from published evidence and standard DSP theory, not directly stated by any source.

---

## Open Questions

- What is Jurik's formal education background? (IEEE presentations suggest EE/CS but unconfirmed)
- Are there additional *Journal of Computational Intelligence in Finance* articles beyond what his website mentions?
- Has anyone published a rigorous statistical comparison between official JMA output and Kositsin's full decompilation vs. everget's simplified version?
- What happens to the JMA algorithm after the company fully closes? Will it be released or lost?
- When was the Starlight decompilation performed? The code has no date stamps. The Wealth-Lab platform target suggests pre-2010 (WealthScript era), but this is speculative.
- Is the JVEL adaptive smoother (exponential response / MAD normalization) used in any other Jurik product beyond JVEL/JAVEL/JVELCFB?
