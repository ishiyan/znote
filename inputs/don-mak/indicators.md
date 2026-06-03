# Don Mak — Implementable Trading Indicators

A consolidated catalogue of indicators, filters, and techniques derived from three books by Don K. Mak, suitable for algorithmic implementation.

## Sources

| Key | Book | Year |
|-----|------|------|
| **B1** | The Science of Financial Market Trading | 2003 |
| **B2** | Mathematical Techniques in Financial Market Trading | 2006 |
| **B3** | Trading Tactics in the Financial Market | 2021 |

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
| PCTK | StochK | Stochastic %K = (C − L)/(H − L) (standard; Mak analyzes it) | Ch 4.1 |
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

## Book 3: Trading Tactics in the Financial Market (2021)

### Third-Party Indicators Mak Analyzes (Ch 5–6)

| Abbrev | Mnemonic | Name | Source | Origin |
|--------|----------|------|--------|--------|
| AO | Awesome | Awesome Oscillator = SMA(median,5) − SMA(median,34) | Ch 5 | Bill Williams |
| AC | Accel | Accelerator Oscillator = AO − SMA(AO,5) | Ch 5 | Bill Williams |
| MACD | MACD | MACD = EMA(12) − EMA(26); signal = EMA(MACD,9) | Ch 6 | Appel |
| MACDH | MACDHist | MACD Histogram = MACD − signal | Ch 6 | Appel |

These are standard third-party indicators. Mak's contribution is the frequency-response analysis (each is a velocity or acceleration filter), not the indicators themselves. They are cataloged here for completeness but skipped for implementation (ubiquitous). See Skip table below.

### Mak Reduced-Lag Tactics (Ch 8)

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| PMSMA | PriceMinusSMA | price − SMA(N) (zero Loss Zone by design) | Ch 8 (D.26) |
| PMEMA | PriceMinusEMA | price − EMA(M) (zero Loss Zone by design) | Ch 8 (D.24) |

**PMSMA / PMEMA** — Mak's deliberately phase-optimal velocity tactics: subtracting a moving average from raw price yields an oscillator whose entire spectrum lies in the Profit Zone (no Loss Zone), per his Appendix A framework. Trivial composition (`price − ma`), so skipped for standalone implementation, but theoretically the "best" of the velocity tactics in the book.

### Novel Velocity / Acceleration Indicators

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| EAACC | EmaAccel | EMA Acceleration Oscillator | Ch 4.2.4 |
| MCDH1 | MacdH1 | MACDH with Price Replacing Fast EMA | Ch 6.3 |

**EAACC** — Defined as (EMA3 − EMA6) − EMA9(EMA3 − EMA6). Uses short EMA lengths to create an acceleration indicator that behaves like a velocity indicator. Sure Profit Zone: 0 < ω < 0.53.

**MCDH1** — Replaces the fast EMA (M₁=12) in standard MACD with raw price (M₁=1), keeping M₂=26, M₃=9. Phase lies between π and 0 for all 0 < ω < π, making the entire spectrum a Profit Zone — unlike standard MACDH which has a Loss Zone.

### Skipped Convolution Technique

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| SKCONV | SkipConv | Skipped Convolution | Ch 2.4.4 |

**SKCONV** — Applies a velocity indicator on sub-sampled data (e.g., hourly data within a daily chart) to detect turning points earlier than waiting for end-of-bar close. Skip-N convolves the indicator on every Nth sample of a lower timeframe.

### Analytical Frameworks

| Abbrev | Mnemonic | Name | Source |
|--------|----------|------|--------|
| PRFZN | ProfZone | Profit Zone / Loss Zone Analysis | Ch 2.3.1, Ch 8.1 |
| SPRFZ | SureProfZone | Sure Profit Zone Criterion | Ch 2.4.3 |

**PRFZN** — Framework classifying frequency ranges into Profit Zone (phase lead 0 to π) and Loss Zone (phase lead −π to 0) based on DTFT phase response of any velocity indicator. Provides a theoretical method to evaluate indicator profitability across frequencies.

**SPRFZ** — The condition φ > ω guarantees profit regardless of sampling delay. The boundary φ = ω line plotted against the phase curve partitions frequencies into Sure Profit Zone (guaranteed) and Unsure Profit Zone.

---

## Implementation Status and Assessment

### Implemented

| Indicator | Implementation | Novelty | Notes |
|-----------|---------------|---------|-------|
| **PFD** (CV/CA/QV/QA/QNV/QNA/SXV/SXA/PV/PA) | `polynomial-fit-derivative` | High | Unified indicator: all polynomial velocity/acceleration via degree (2–6) and order (1–2) params. FIR coefficients from Lagrange basis derivatives. 4–7 taps. Unique to Mak — not available in standard libraries. |
| **ISWP** (IF4/IF5) | `instantaneous-sine-wave-period` | High | Combines IF4 and IF5 methods, selects by lowest error. Outputs period/omega/velocity/acceleration. Returns NaN when data doesn't fit sine model (~40–50% of bars on real data). Novel frequency estimator. |
| **MHW** (MHH/MHM/MHL) | `mexican-hat-wavelet` | High | Causal Mexican Hat (Ricker) wavelet filter. Smooth bell-shaped frequency response centered on a single peak. Coefficients computed from exact formula (not book's 4-decimal rounded values). Band enum: HIGH/MID/LOW/CUSTOM. |
| **SWB** (WBH/WBM/WBL/WBV) | `sinc-wavelet-bandpass` | Medium | Sinc-based band-pass filter with sharp rectangular passband. 121–201 taps. Octave decomposition (periods 8–64). Optional cubic velocity mode (WBV equivalent). Less novel than MHW (standard DSP technique) but specific to Mak's trading application. |
| **PVX** | `parabolic-vertex` | Medium | Fits parabola to 3 points, outputs bars-to-turning-point. Simple formula but novel concept: predicts *when* the reversal will occur rather than detecting it after the fact. Best on pre-smoothed data. |
| **CVX** | `cubic-vertex` | Medium | Fits cubic to 4 points, outputs two turning-point locations (near/far by absolute distance). More complex edge cases (negative discriminant, parabolic fallback). Same predictive concept as PVX but with two potential reversals. |
| **AEMA** | `adaptive-exponential-moving-average` | Medium | EMA with frequency-dependent α via embedded ISWP. Hyperbolic 1/ω mapping between alpha_max and alpha_min. Introduces feedback loop: frequency estimate modulates the smoothing. Falls back to alpha_min when ISWP returns NaN (conservative smoothing). |
| **PF** (F1V/F1VA) | `polynomial-forecast` | Low | 1-bar-ahead price forecast via Taylor expansion using PFD derivatives. order=1 uses velocity only (F1V), order=2 adds acceleration (F1VA). Trivial math but convenient as a standalone indicator: outputs a price level (not a derivative), natural for stop/target placement. Degree 2–6, optional EMA pre-smoothing. |
| **MEMA** (MEMA/MEMA-D) | `modified-exponential-moving-average` | Low | Reduced-lag EMA: adds EMA's own PFD velocity back to output. Skip param gives MEMA-D (multi-timeframe lag correction via strided polynomial fit). Reduces lag significantly (e.g., from 5 to 3 bars on period=6 linear ramp). Trivial math but useful as standalone smoothing filter. |
| **VCEMA** (ZEMA) | `velocity-corrected-exponential-moving-average` | Low | Pre-corrects price by adding raw PFD velocity before EMA smoothing. Same lag reduction as MEMA on linear data; noisier on nonlinear data (velocity estimated from raw price). Mak's "Zero-Lag EMA" — renamed to avoid collision with Ehlers' method. |

### Skipped — Trivial Composition

These are not standalone algorithms but trivial one-line compositions of other indicators:

| Indicator | Reason skipped |
|-----------|---------------|
| **SKEMA / SKCV / SKCONV** | Meta-technique for multiple-timeframe analysis within a single data stream. See detailed explanation below. |

#### SKEMA / SKCV / SKCONV — Skipped Convolution and Multiple Timeframes

**Concept:** Mak's "skipped convolution" is his approach to multiple timeframe (MTF) analysis done within a single data stream, rather than loading separate timeframe charts.

**Traditional MTF approach:**
- Load daily chart → compute indicator
- Load weekly chart → compute same indicator
- Compare signals across timeframes

**Mak's skipped convolution approach:**
- Have intraday data (e.g., hourly bars within a daily timeframe)
- Compute indicator on every D-th bar (e.g., every 8th hourly bar ≈ daily spacing)
- But update more frequently than once per day — the "daily-scale" signal updates every hour

**The advantage:** Detect the daily-scale turning point *within* the day, hours before the daily bar closes. Traditional MTF only updates the daily signal once per day at close.

**Why not implemented as a generic wrapper:**

For PFD (velocity/acceleration), the skip param is mathematically clean — spacing the Lagrange interpolation points wider changes the effective frequency band being measured. For arbitrary indicators, "skipping" means something fundamentally different depending on indicator type:

- **FIR filters (MHW, SWB):** Would need to redesign filter coefficients for the new effective sample rate — not a simple wrapper.
- **EMA:** Skipping inputs changes the effective alpha in a non-obvious way.
- **ISWP:** The frequency estimate would be in units of the sub-sampled timeframe, requiring unit conversion.

It's not a uniform operation — each indicator type responds differently to sub-sampling.

**What we implemented instead:** The `skip` parameter in `modified-exponential-moving-average` (MEMA-D) already implements the useful core of SKCONV for the velocity-correction case. The PFD indicator could similarly accept a `skip` param (same Lagrange basis, wider point spacing). This covers the most valuable use cases without a problematic generic wrapper.

### Skipped — Not Novel or Not Practical

| Indicator | Reason skipped |
|-----------|---------------|
| **MCDH1** (MACDH with price as fast EMA) | The book's own author concludes it's "not a good idea" (Ch 7.4.2). Theoretically has zero Loss Zone, but acts as high-pass filter amplifying noise. Real market results: −9.25% average. Trivially composed from two EMAs: `(price - ema26) - ema9(price - ema26)`. |
| **EAACC** (EMA Acceleration) | `(ema3 - ema6) - ema9(ema3 - ema6)` — composition of standard EMAs with specific periods. No novel algorithm. |
| **PRFZN / SPRFZ** (Profit Zone) | Analytical framework for evaluating indicators, not a tradeable indicator itself. Useful for theory but produces no trading signals. |
| **SMA / EMA / BWF / SINC** | Well-known DSP filters available in every library. No novelty. |
| **MOM / MACD / MACDH** | Standard momentum indicators available everywhere. |
| **DEMA** (Double EMA) | `ema(ema(price))` — trivial. |
| **AO** (Awesome Oscillator, B3 Ch5) | Bill Williams indicator: `sma(median,5) − sma(median,34)`. Third-party, ubiquitous. Mak only contributes frequency analysis. |
| **AC** (Accelerator Oscillator, B3 Ch5) | Bill Williams indicator: `AO − sma(AO,5)`. Third-party, ubiquitous. |
| **PMSMA / PMEMA** (B3 Ch8) | `price − sma(N)` / `price − ema(M)`. Trivial one-line composition. Theoretically zero-Loss-Zone, but not a standalone algorithm. |
| **PCTK** (Stochastic %K, B1 Ch4.1) | `(C−L)/(H−L)`. Standard, ubiquitous. Mak analyzes it critically. |
| **Simple return** (B1 Ch3.1) | `(x(n)−x(n−1))/x(n−1)`. Preprocessing transform, not an indicator. |

### Not from Don Mak

| Indicator | Implementation | Source |
|-----------|---------------|--------|
| **Moving Mini-Max** | `moving-mini-max` | Silagadze 2008 |

---

## Confirmed Non-Implementable (surveyed, not formulated)

A full deep-read of all three books verified that several topics one might expect to yield
indicators contain **no formulas, coefficients, or algorithms** — they are literature surveys,
market-characterization models, or analytical frameworks. These are documented here so they are
not mistakenly re-investigated as implementation candidates.

| Topic | Location | Why not implementable |
|-------|----------|-----------------------|
| Fractal dimension / Hurst exponent / R/S analysis | B1 Ch 2 ("Is the Market Random?") | Literature survey only; results quoted (D≈1.33–1.69) but no estimator algorithm given. |
| Approximate entropy, BDS test, runs test, close-returns test | B1 Ch 2 | Named only; no formulas. |
| Chaos theory / Lyapunov exponent / correlation dimension | B1 Ch 12 | Philosophical/narrative wrap-up; no algorithm. |
| Fuzzy-logic decision procedure | B1 Ch 3.7 | Framework described; no concrete rule set or numbers. |
| ARIMA(p,d,q) forecasting | B1 Ap 1 | Standard Box–Jenkins; cited fitted examples (IBM, DJU, S&P), not Mak's own indicator. |
| Log-normal / Lévy / Tsallis-entropy distributions | B2 Ch 2 | Market-characterization models, not chart indicators. |
| Variance-ratio test, modified R/S, log-periodic crash model, Omori law | B2 Ch 2 | Statistical/descriptive models, no tradeable signal. |
| Phase / causality framework (H_R ↔ H_I relation) | B2 Ch 7 | Analytical filter-design framework, not a standalone signal. |
| Ideal brick-wall low-pass filter | B2 Ch 3 | Non-causal / theoretical reference filter. |
| Profit Zone / Loss Zone taxonomy | B3 Ap A | Evaluation framework for ranking velocity indicators; produces no signal. |
| Money-management stop-loss expected-value engine | B2 Ch 12–13, Ap 5 | Risk-management math (MATLAB over a Lévy distribution), not a chart indicator. |

### Coefficient errata confirmed during review

The 2003 book's chapter body contains transcription typos that the **appendices correct**. Our
implementations already use the authoritative appendix forms (verified exactly via the Lagrange
basis), so no code change is required — recorded here for provenance:

- **Eq 10.4** (velocity forecast) misprints the leading coefficient as `11/6`; correct is `17/6`
  (Ap 8, A8.12). `polynomial-forecast` computes `price + velocity`, yielding `17/6` exactly. ✓
- **Eq 10.5** (vel+acc forecast) misprinted; correct is `(23/6, −11/2, 7/2, −5/6)` (A8.14).
  `polynomial-forecast` order=2 reproduces this exactly. ✓
- **Eq 9.1** (high wavelet) misprinted; correct sinc form is A7.44. `mexican-hat-wavelet` /
  `sinc-wavelet-bandpass` compute from the exact formula, not the book's rounded/typo values. ✓

---

## Implementation Priority (Revised)

### Tier 1 — Implemented (unique to Mak, most novel)

1. **PFD** — Polynomial Fit Derivative (unifies CV/CA/QV/QA/QNV/QNA/SXV/SXA/PV/PA)
2. **ISWP** — Instantaneous Sine Wave Period (unifies IF4/IF5)
3. **MHW** — Mexican Hat Wavelet (unifies MHH/MHM/MHL + CUSTOM)
4. **SWB** — Sinc Wavelet Band-Pass (unifies WBH/WBM/WBL/WBV)
5. **PVX** — Parabolic Vertex
6. **CVX** — Cubic Vertex
7. **AEMA** — Adaptive Exponential Moving Average
8. **PF** — Polynomial Forecast (unifies F1V/F1VA — Taylor extrapolation)
9. **MEMA** — Modified Exponential Moving Average (unifies MEMA/MEMA-D — reduced-lag EMA)
10. **VCEMA** — Velocity-Corrected Exponential Moving Average (Mak's "Zero-Lag EMA")

### Tier 2 — Skipped (trivial composition, 1–2 lines on top of Tier 1)

8. **SKEMA / SKCV** — Skipped convolution (meta-technique, not an algorithm)

### Tier 3 — Skipped (not novel, not practical, or not an indicator)

11. **MCDH1** — Author-discredited, negative real returns, trivial EMA composition
12. **EAACC** — Standard EMA composition with specific periods
13. **SKCONV** — Data sampling technique, not an algorithm
14. **PRFZN / SPRFZ** — Evaluation framework, not tradeable
15. **SMA / EMA / BWF / SINC / MOM / MACD** — Ubiquitous, no implementation needed
