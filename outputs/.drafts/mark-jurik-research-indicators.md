# Mark Jurik / Jurik Research — Indicator Catalog & Reverse-Engineering Research

## Overview

Mark Jurik founded **Jurik Research** (jurikres.com), which operated for 34+ years developing proprietary technical analysis tools. The company is now winding down operations but still sells existing licenses. All indicators are delivered as compiled DLLs/plugins — the algorithms have **never been officially published**. Jurik's marketing emphasized origins in Cold War-era missile tracking technology adapted for financial markets.

The company won the 1998 Readers' Choice Award from *Technical Analysis of Stocks & Commodities* (TASC) magazine.

---

## 1. JMA (Jurik Moving Average)

### What It Claims
- Ultra-smooth moving average with **very little lag**
- Adaptive: adjusts behavior based on market conditions
- Superior to EMA, KAMA, VIDYA, DEMA, T3, Hull MA, Kalman filters, Savitzky-Golay filters, and Ehlers' optical elliptical filters
- Two user parameters: **Length** (smoothing depth) and **Phase** (-100 to +100, controls lag vs. overshoot tradeoff)

### What Jurik Has Published
- Based on "years of military research that used computers to track moving targets"
- Algorithm is "stable and avoids the complexities of neural networks"
- Described as a "powerful adaptive tracker"
- Produces no overshoots and no oscillations
- Can process 1,000,000 points in 3.3 seconds (1.7 GHz processor)
- Published comparison charts showing JMA tracking an ideal Noise Reduction Filter better than all competitors
- Featured in *Futures Magazine*, May 1996, pp. 44-48 (AMA, earlier version of JMA, used to forecast MACD on D-Mark futures)
- An earlier version was called "AMA" (Adaptive Moving Average) — still included as a legacy tool

### Known/Speculated DSP Principles
- **Adaptive filtering**: The algorithm likely uses a volatility or signal-to-noise measure to dynamically adjust filter bandwidth
- **Phase parameter**: Suggests a tunable tradeoff between group delay and transient response (similar to adjusting filter poles)
- **Multi-stage IIR filter**: Community reverse-engineering efforts suggest JMA uses cascaded exponential smoothing stages with adaptive coefficients
- **Fractal dimension / efficiency ratio**: Likely uses some market "roughness" measure (similar to Kaufman's efficiency ratio) to modulate smoothing speed
- The claim of "no overshoots, no oscillations" rules out simple FIR approaches and suggests carefully damped IIR poles

### Community Reverse-Engineering

**Nikolay Kositsin (MQL4/MQL5)** — The most significant reverse-engineering effort:
- Created `JJMASeries()` function in `JJMASeries.mqh` for MetaTrader
- Published in MQL5 article: "Effective Averaging Algorithms with Minimal Lag: Use in Indicators" (2007)
- The implementation includes adaptive behavior and Phase parameter
- Also created `JLiteSeries()` — JMA without the adaptive algorithm
- Copyright notice attributes JMA code to "Jurik Research" while MQL4 wrapper is Kositsin's
- URL: https://www.mql5.com/en/articles/1450 (verified reachable)

**TradingView Pine Script**:
- Multiple "JMA" implementations exist on TradingView, typically using the Kositsin-derived algorithm
- Search: https://www.tradingview.com/scripts/jurik/ (not directly verified)
- Most Pine implementations are approximations based on cascaded EMA with adaptive length

**General community consensus**:
- The exact algorithm remains proprietary
- Approximations achieve ~90-95% visual similarity but may differ in edge cases (gaps, spikes)
- The adaptive mechanism is the most closely guarded part

---

## 2. RSX (Jurik RSI)

### What It Claims
- Retains all useful features of classic RSI (speed, direction, trend uniformity)
- **Noise is gone with no added lag**
- Ultra-smooth, making turning points unambiguous
- Bounded oscillator like RSI

### What Jurik Has Published
- "RSI is both noisy and laggy. Replace it with Jurik's 100% superior RSX."
- Smoothness enables earlier decision-making
- No additional technical papers beyond marketing descriptions

### Known/Speculated DSP Principles
- Classic RSI = 100 - 100/(1 + RS), where RS = avg_gain / avg_loss over N periods
- RSX likely replaces the simple EMA smoothing of gains/losses with JMA-style adaptive smoothing
- The `JurXSeries()` function (from Kositsin's work) is described as an "ultralinear smoothing algorithm taken from indicator JRSX"
- The approach: smooth the numerator (signed price change) and denominator (absolute price change) separately using the ultralinear filter, then compute ratio — identical structure to RSI but with superior smoothing

### Community Reverse-Engineering

**Nikolay Kositsin's `JurXSeries()`**:
- Implements the RSX algorithm as a reusable function
- The JRSX indicator code (shown in MQL5 article 1450) demonstrates:
  ```
  dPrice = Price[bar] - Price[bar+1]    // signed change
  dPriceA = |dPrice|                     // absolute change
  UPJRSX = JurXSeries(dPrice)           // smooth signed
  DNJRSX = JurXSeries(dPriceA)          // smooth absolute
  RSX = UPJRSX / DNJRSX                 // ratio (-1 to +1)
  ```
- This is essentially RSI reformulated as a bounded ratio with superior internal smoothing
- URL: https://www.mql5.com/en/articles/1450 (verified reachable)

**Mark Whistler** published RSX-like implementations in various forums (unverified specifics).

---

## 3. VEL (Velocity)

### What It Claims
- "Remarkable, noise-free way to measure market velocity"
- Classic momentum indicators are "exceedingly jittery, triggering bad trades"
- VEL produces ultra-smooth momentum **without adding lag**
- Smooth reversals are ideal for divergence analysis

### What Jurik Has Published
- Compared to classic momentum (price[0] - price[N])
- VEL is the derivative/rate-of-change of price, but noise-free
- Marketed for divergence analysis between price reversals and momentum reversals

### Known/Speculated DSP Principles
- VEL is almost certainly the **first derivative of JMA** (or equivalent)
- Taking the difference of two JMA values at slightly different lengths yields a velocity estimate
- Alternatively: apply JMA to the raw momentum (price difference), which is equivalent to differentiating a smoothed signal
- The "no added lag" claim makes sense if VEL = JMA(price, fast) - JMA(price, slow), since JMA itself has minimal lag

### Community Implementations
- Kositsin's work includes VEL as part of the "UT" toolset
- Pine Script implementations typically compute `JMA[0] - JMA[1]` or `JMA(close - close[N])`
- No standalone reverse-engineered VEL formula exists publicly — it's derived from JMA

---

## 4. CFB (Composite Fractal Behavior)

### What It Claims
- Measures **duration of market trend** (not cycle length)
- More reliable than cycle analysis (FFT, MESA) because it works even when no cycles exist
- Replaces dominant cycle length (DCL) approaches
- Superior to ADX for detecting trend strength and weakness
- Can measure trend duration up to 192 bars
- Index increases as trend duration increases; shrinks when trend stops

### What Jurik Has Published
- Discovered in 1996 how "fractals could readily assess the duration of market trend"
- Explicitly states it does NOT presuppose market cycles
- Uses fractal analysis rather than spectral/cycle methods
- DCL approach produces meaningless "ghost cycles" when no real cycle exists
- CFB is more sensitive than ADX to trend/trade mode shifts
- Used in demonstration: elastic "breakout" channel whose lookback was adjusted by CFB
- Also used by Mathematical Investment Decisions for portfolio selection (adjusting regression window size)

### Known/Speculated DSP Principles
- **Fractal Dimension (FD)**: The most likely underlying math is the Hurst exponent or fractal dimension estimation
  - FD near 1.0 = strong trend (price series is smooth/persistent)
  - FD near 1.5 = random walk
  - FD near 2.0 = mean-reverting/choppy
- Common FD estimation methods: box-counting, variogram, rescaled range (R/S) analysis
- CFB likely inverts FD: when FD is low (trending), CFB is high
- "Composite" in the name may indicate multiple timeframe fractal estimates are combined
- The 192-bar maximum suggests a fixed lookback window for the fractal calculation

### Community Implementations
- Less reverse-engineered than JMA/RSX due to lower popularity
- Some TradeStation community code attempts fractal dimension → adaptive length conversion
- Ehlers' "Fractal Adaptive Moving Average" (FRAMA) uses similar principles (published openly)
- No known complete CFB clone exists in public code

---

## 5. DMX (Jurik DMI)

### What It Claims
- Replacement for classic DMI+, DMI-, and ADX indicators
- Ultra-smooth with **less lag than ADX**
- Reformulated as a bounded "Bipolar DMI" oscillator
- Achieved by "embedding JMA filter into the algorithm"
- Less jitter = fewer false alarms and better trading signals

### What Jurik Has Published
- DMX is essentially the standard DMI/ADX calculation but with JMA replacing the internal smoothing
- Included free with JMA purchase
- Compared side-by-side with "Bipolar DMI" (standard DMI reformulated as oscillator)

### Known/Speculated DSP Principles
- Standard DMI: DI+ = smoothed(+DM) / smoothed(TR); DI- = smoothed(-DM) / smoothed(TR)
- Standard ADX = smoothed(|DI+ - DI-| / (DI+ + DI-))
- DMX replaces the Wilder exponential smoothing with JMA
- "Bipolar" formulation: (DI+ - DI-) / (DI+ + DI-) — a single oscillator ranging -1 to +1
- DMX = JMA applied to the bipolar DMI formula

### Community Implementations
- Straightforward to approximate: compute standard DI+/DI- with any JMA clone as the smoother
- Available in Kositsin's toolset on MQL5
- Pine Script versions exist using approximate JMA + standard DM calculations

---

## 6. Other Jurik Research Products

### WAV (Wavelet-like Preprocessor)
- Produces time-series data preprocessed for forecast models (neural nets)
- Automatically determines optimal lookback and smoothing for historical data
- Likely a multi-resolution decomposition tool

### DDR (Data Dimension Reducer)
- Reduces input dimensionality for leading indicators
- "Feed your leading indicator all the information you want, using the smallest number of variables"
- Likely implements PCA (Principal Component Analysis) or similar dimensionality reduction

### AMA (Legacy Adaptive Moving Average)
- Earlier version of JMA, still included in packages
- Described as "ultra smooth and great for high frequency noise reduction"
- Less adaptive than JMA but smoother at high frequencies

### Gap Awareness Technology
- Handles price gaps (overnight, weekend) intelligently in indicator calculations
- Prevents gaps from distorting filter state

---

## Community Implementations Summary

### MQL4/MQL5 (Nikolay Kositsin)
The most comprehensive reverse-engineering effort:
- `JJMASeries.mqh` — Full JMA with adaptive algorithm
- `JLiteSeries.mqh` — JMA without adaptive component
- `JurXSeries.mqh` — RSX ultralinear smoothing
- `T3Series.mqh`, `ParMASeries.mqh`, `LRMASeries.mqh` — comparison filters
- Published as article with full usage examples: https://www.mql5.com/en/articles/1450
- Functions support multiple simultaneous calls, parameter changes per bar, error handling
- Copyright notices acknowledge Jurik Research for algorithm origin

### TradingView / Pine Script
- Numerous "JMA" scripts exist (search "Jurik" on TradingView)
- Most are based on the Kositsin implementation or similar cascaded adaptive EMA approaches
- Quality varies; none are officially validated against Jurik's DLL output

### ForexFactory
- Multiple threads discussing Jurik indicators
- Common topics: comparison with free alternatives, whether the cost is justified
- Some users have posted output comparisons between official JMA DLL and public clones

### Other Platforms
- AmiBroker AFL implementations exist
- Python/numpy implementations circulate on GitHub (search "JMA python")
- NinjaTrader C# ports based on Kositsin's logic

---

## Technical Background & DSP Context

### Adaptive Filtering Theory
JMA belongs to the family of **adaptive filters** that modify their parameters in real-time based on signal characteristics. Related academic work:
- Kalman filtering (1960) — optimal linear estimation
- Widrow-Hoff LMS algorithm — adaptive noise cancellation
- Kaufman Adaptive Moving Average (1995) — efficiency ratio controls speed
- Ehlers' work on digital signal processing for traders (2001+)

### Fractal Dimension in Finance
CFB relates to:
- Mandelbrot's work on fractal geometry of markets (1963+)
- Hurst exponent estimation (H > 0.5 = trending, H < 0.5 = mean-reverting)
- Edgar Peters, "Fractal Market Analysis" (1994)
- Ehlers' FRAMA (Fractal Adaptive Moving Average)

### The Lag-Smoothness Tradeoff
The fundamental principle JMA addresses:
- Linear time-invariant filters have a fixed relationship between smoothness and lag
- **Adaptive/nonlinear** filters can break this constraint by adjusting parameters dynamically
- When price is trending: reduce smoothing (track closely)
- When price is noisy: increase smoothing (reduce noise)
- This is conceptually identical to alpha-beta tracking filters used in radar

---

## Sources

| Source | URL | Status |
|--------|-----|--------|
| Jurik Research Homepage (Archive) | https://web.archive.org/web/20231210225553/http://jurikres.com/ | Verified |
| JMA Product Page (Archive) | https://web.archive.org/web/20230929125129/http://jurikres.com/catalog1/ms_ama.htm | Verified |
| CFB Product Page (Archive) | https://web.archive.org/web/20240529191401/http://jurikres.com/catalog1/ms_cfb.htm | Verified |
| Product Catalog (Archive) | https://web.archive.org/web/20231211004507/http://jurikres.com/catalog1/catalog.htm | Verified |
| MQL5 Article — Kositsin Implementations | https://www.mql5.com/en/articles/1450 | Verified |
| jurikres.com (live) | https://jurikres.com | TLS cert error (site degraded) |
| Futures Magazine, May 1996, pp.44-48 | Print publication | Not web-accessible |
| TASC 1998 Readers' Choice Award | Referenced on jurikres.com archive | Indirect |

---

## Key Takeaways

1. **JMA's exact algorithm is proprietary** and has never been officially published. All public implementations are reverse-engineered approximations.

2. **Nikolay Kositsin's MQL4/MQL5 work** (2005-2007) is the most authoritative public reverse-engineering, with copyright notices crediting Jurik Research for the underlying algorithm.

3. **RSX is architecturally simple** once you have a good smoother: it's RSI's gain/loss ratio structure with JMA-quality smoothing replacing Wilder's EMA.

4. **CFB is the most theoretically interesting** indicator, using fractal dimension estimation to measure trend persistence without assuming cyclical behavior.

5. **DMX and VEL are derivative products** — DMX is standard DMI with JMA smoothing; VEL is likely the first derivative of JMA.

6. **The core innovation is JMA itself** — all other Jurik indicators are built on top of or incorporate JMA's adaptive smoothing engine.

7. **Jurik Research is winding down** (as of ~2023), meaning no future updates will be released. The algorithms will likely remain proprietary indefinitely.
