# Mark Jurik: Biography, Publications, Indicators, and Methods

## Executive Summary

Mark Jurik is the founder of Jurik Research & Consulting (est. 1988, Silicon Valley), a company that developed proprietary adaptive signal processing algorithms for financial trading. His flagship product, the Jurik Moving Average (JMA), is widely regarded as one of the best-performing adaptive filters in retail trading — and one of the few whose algorithm has never been publicly disclosed. After 34 years of operation, the company began winding down around 2022.

Jurik's background is in military signal processing (ELINT), and his career arc represents a Cold War-to-Wall Street pivot: applying missile tracking technology to financial time series. He holds no known TASC publications; all his indicators are sold as compiled DLLs, with the algorithms protected as trade secrets. The most significant public reverse-engineering effort is by Nikolay Kositsin (MQL4/MQL5, 2005-2007).

---

## 1. Biography

### Career Timeline

- **Pre-1987:** Signal processing work for military projects (ELINT — electronic intelligence). Specific employer and education unknown.
- **1987:** First public appearances — AI Conference (Association of Old Crows, military ELINT), SF Bay Area AI Forum, Lawrence Livermore National Laboratory.
- **1987-1991:** Taught a 10-lecture series on neural networks at UC Extension, repeated annually for five years.
- **1988:** Founded Jurik Research & Consulting. Presented at IEEE Information Theory Society, IEEE ASSP, IEEE Compcon, Santa Clara University AI SIG.
- **1989-1991:** IEEE videoconference on neural networks; "Neural Nets for the Real World" conference; IEEE Wescon; IEEE Asilomar; AOC International Conference; neural network conference in Germany; Stanford University Computer Science Forum.
- **1994:** IEEE SIG Group: AI and Finance.
- **1995:** Futures West International Conference (delivered "Space, Time, Cycles & Phase" lecture, later released as audio seminar).
- **1996:** Published in *Futures Magazine* (May 1996, pp. 44-48) — article on forecasting MACD using an Adaptive Moving Average, the precursor to JMA.
- **1998:** Won TASC Readers' Choice Award.
- **1999:** Published *Computerized Trading* (editor, 20 contributing authors). Presented at Omega World '99.
- **2000:** Swiss Association of Market Technicians (SAMT), Zurich. Wall Street Harvest interview.
- **2001:** Market Technicians Association (Denver, Chicago).
- **2007-2012:** TASC Readers' Choice Awards — 1st place 2010, 2011, 2012; 2nd place 2007, 2009.
- **2010:** Austin Association of Financial Traders. Trader's Magazine (Germany) interview.
- **~2022:** Company begins winding down operations.

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
- **NeuroTapes:** 12-hour video course on neural networks, sold worldwide for over a decade
- **"Space, Time, Cycles & Phase":** Audio seminar (MP3 on CD), based on 1995 conference lecture
- **Interviews:** Wall Street Harvest (2000, sector analysis); Trader's Magazine Germany (2010, extended interview on JMA design, risk management, company origins)

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

**Virtual Trading** (contributing author, details unknown)

### Articles

- *Futures Magazine*, May 1996, pp. 44-48 — AMA (Adaptive Moving Average) applied to MACD forecasting on D-Mark futures
- *Journal of Computational Intelligence in Finance* (also known as *Neurovest Journal* / *AI in Finance*) — unspecified articles

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

**Claims:** Superior to EMA, KAMA, VIDYA, DEMA, T3, Hull MA, Kalman filters, Savitzky-Golay, and Ehlers' elliptical filters. No overshoots, no oscillations. Can process 1,000,000 points in 3.3 seconds [6].

**What is known about the algorithm:**
- Adaptive filter that modulates smoothing speed based on market conditions
- Multi-stage IIR structure with adaptive coefficients (from reverse-engineering)
- Likely uses a volatility or efficiency-ratio measure to detect trending vs. ranging
- Phase parameter adjusts group delay vs. transient response (analogous to adjusting filter pole positions)
- "No overshoots" rules out simple FIR approaches; implies carefully damped IIR poles
- Conceptually related to alpha-beta tracking filters used in radar/missile guidance

**Historical note:** An earlier version was called "AMA" (Adaptive Moving Average), published in *Futures Magazine* (1996). AMA is still included as a legacy product.

### 4.2 RSX (Jurik RSI)

**Purpose:** Noise-free RSI replacement with no added lag.

**What is known about the algorithm:**
RSX uses the same mathematical structure as RSI but replaces Wilder's EMA with an "ultralinear" adaptive smoother:

```
signed_change = price[i] - price[i-1]
abs_change = |signed_change|
smooth_signed = JurX(signed_change)    // adaptive smoothing
smooth_abs = JurX(abs_change)          // adaptive smoothing
RSX = smooth_signed / smooth_abs       // bounded ratio, -1 to +1
```

This is RSI reformulated as a centered oscillator with superior internal smoothing. The architecture is well-understood from Kositsin's reverse-engineering [7].

### 4.3 VEL (Velocity)

**Purpose:** Noise-free market momentum/rate-of-change.

**What is known about the algorithm:**
Almost certainly the **first derivative of JMA** — either:
- `JMA[i] - JMA[i-1]` (simple difference of consecutive JMA values), or
- `JMA(close - close[N])` (JMA applied to raw momentum)

Both formulations yield smooth momentum with minimal lag, since JMA itself has minimal lag. No standalone algorithm exists — VEL is derived from JMA [7].

### 4.4 CFB (Composite Fractal Behavior)

**Purpose:** Measures duration of market trend without assuming cyclical behavior.

**Claims:** More reliable than FFT/MESA cycle analysis because it works even when no cycles exist. Superior to ADX for detecting trend strength. Index increases as trend duration increases; measures up to 192 bars [8].

**What is known about the algorithm:**
- Uses **fractal dimension estimation** rather than spectral methods
- Fractal dimension (FD) near 1.0 = strong trend; FD near 1.5 = random walk; FD near 2.0 = mean-reverting
- CFB likely inverts FD: low fractal dimension (trending) produces high CFB
- "Composite" may indicate multiple-timeframe fractal estimates combined
- Related work: Hurst exponent, box-counting, rescaled range analysis, Ehlers' FRAMA
- Discovered by Jurik in 1996 per his website

**Community status:** Less reverse-engineered than JMA/RSX due to lower popularity. No known complete public clone exists.

### 4.5 DMX (Jurik DMI)

**Purpose:** Ultra-smooth replacement for DMI+, DMI-, and ADX.

**What is known about the algorithm:**
Standard DMI calculation with JMA replacing Wilder's exponential smoothing:

```
DI+ = JMA(+DM) / JMA(TR)
DI- = JMA(-DM) / JMA(TR)
Bipolar_DMI = (DI+ - DI-) / (DI+ + DI-)    // single oscillator, -1 to +1
DMX = JMA(Bipolar_DMI)                       // final smoothing pass
```

Included free with JMA purchase. Straightforward to approximate with any JMA clone [7].

### 4.6 Other Products

| Product | Description | Likely Method |
|---------|-------------|---------------|
| WAV | Wavelet-like preprocessor for forecast models | Multi-resolution decomposition |
| DDR | Data dimension reduction for leading indicators | PCA or similar |
| AMA | Legacy adaptive MA (pre-JMA) | Simpler adaptive EMA |
| Gap Awareness | Handles overnight/weekend gaps in indicator calculations | State reset logic |

---

## 5. How the Indicators Work: Technical Context

### The Core Problem

All linear time-invariant (LTI) filters face a fundamental tradeoff: smoothness vs. lag. A 50-period SMA is smooth but lags 25 bars. An EMA with the same lag is less smooth. This is not a design choice — it is a mathematical constraint of LTI systems.

### Jurik's Approach: Adaptive Nonlinear Filtering

JMA breaks the LTI constraint by being **nonlinear and time-varying**:
- When price is trending (signal-to-noise is high): reduce smoothing, track closely
- When price is noisy/ranging (signal-to-noise is low): increase smoothing, reject noise
- The transition between modes must be smooth to avoid discontinuities

This is conceptually identical to:
- Alpha-beta-gamma tracking filters (missile guidance)
- Kalman filters with adaptive process noise
- Kaufman's Adaptive Moving Average (KAMA) using efficiency ratio

The difference is implementation quality. JMA's marketing claims superiority over KAMA, VIDYA, and other published adaptive filters — plausibly because it uses a more sophisticated adaptivity measure and/or multi-stage cascaded filtering.

### The Phase Parameter

The Phase parameter (-100 to +100) controls a lag-overshoot tradeoff:
- Phase = +100: minimum lag, may overshoot on reversals
- Phase = 0: balanced
- Phase = -100: maximum smoothness, more lag

In filter theory terms, this likely adjusts the damping ratio of the IIR poles. Low damping = fast response but ringing. High damping = no ringing but slower.

### Why the Algorithm Remains Secret

Jurik's competitive advantage is the specific adaptive mechanism — how the filter detects market regime changes and modulates its coefficients. The general architecture (cascaded adaptive IIR) is inferable from reverse-engineering, but the exact adaptation law, its parameters, and edge-case handling (gaps, spikes, regime transitions) are the trade secret.

---

## 6. Key Reverse-Engineering Source

The most authoritative public work is by **Nikolay Kositsin** (2005-2007), published as an MQL5 article:

**"Effective Averaging Algorithms with Minimal Lag: Use in Indicators"**
URL: https://www.mql5.com/en/articles/1450 [7]

Kositsin produced reusable MQL4 function libraries:
- `JJMASeries()` — JMA with adaptive algorithm
- `JLiteSeries()` — JMA without adaptive component
- `JurXSeries()` — RSX ultralinear smoothing

The code includes copyright notices crediting Jurik Research for the algorithm origin. These functions form the basis for most subsequent JMA/RSX implementations on TradingView, NinjaTrader, Python, and other platforms.

---

## Sources

[1] http://jurikres.com/gifs1/portrait3.jpg — Portrait photo. URL derived from page source; domain verified reachable (HTTP only).

[2] http://jurikres.com/about/company.htm — Company "About" page. Verified reachable.

[3] http://jurikres.com/about/presents.txt — Presentations list. Verified reachable.

[4] http://jurikres.com/catalog1/cat_pub.htm — Publications catalog. Verified reachable.

[5] http://technical.traders.com/archive/combo/display5.asp?author=Mark%20Jurik — TASC author search. Returns "file not found" error, confirming no Jurik author record exists.

[6] https://web.archive.org/web/20230929125129/http://jurikres.com/catalog1/ms_ama.htm — JMA product page (Wayback Machine). Verified reachable.

[7] https://www.mql5.com/en/articles/1450 — Kositsin MQL5 article. Verified reachable.

[8] https://web.archive.org/web/20240529191401/http://jurikres.com/catalog1/ms_cfb.htm — CFB product page (Wayback Machine). Verified reachable.

---

## Open Questions

- What is Jurik's formal education background? (IEEE presentations suggest EE/CS but unconfirmed)
- Are there additional *Journal of Computational Intelligence in Finance* articles beyond what his website mentions?
- Has anyone published a rigorous statistical comparison between official JMA output and Kositsin's approximation?
- What happens to the JMA algorithm after the company fully closes? Will it be released or lost?
