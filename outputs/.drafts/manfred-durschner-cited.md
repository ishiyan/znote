# Dr. Manfred G. Dürschner

## Executive Summary

Dr. Manfred G. Dürschner is a German physicist and independent technical analyst who applies signal processing theory and nonlinear mathematics to financial markets. He is best known for developing the **3rd Generation Moving Average** (also called the New Moving Average / NMA), which uses the Nyquist-Shannon sampling theorem to eliminate temporal lag from moving averages [1][2]. He received the First Prize of the VTAD Award (German Association of Technical Analysts) in 2011 for this work [3][5]. He also authored the book *Technische Analyse mit EMD* (Wiley-VCH, 2014), which applies NASA's Empirical Mode Decomposition to financial time series analysis [3][7].

## Biography

### Academic Background

Dürschner holds a doctorate in physics ("promovierte Physiker") [3]. No specific university affiliation has been publicly documented. His approach to financial markets is grounded in physics and signal processing theory — he explicitly frames his contributions as applying physical models and reasoning to investment decisions [3].

### Career and Affiliations

- **Active trader:** Has been trading successfully on stock markets for an extended period, with several years of practical experience in market technics and trading systems [3].
- **VTAD membership:** Member of the Vereinigung Technischer Analysten Deutschlands e.V. (German Association of Technical Analysts) [3][5].
- **IFTA contributor:** Published in the International Federation of Technical Analysts (IFTA) Journal [2].
- **Independent researcher:** No known institutional affiliation; appears to work independently [inferred].

### Awards

- **2011 VTAD Award, First Prize** — for the paper "Gleitende Durchschnitte 3.0" (Moving Averages 3.0), which introduced the Nyquist-Shannon-based moving average method [3][5].

### Public Presence and Photos

No publicly available photographs of Dr. Dürschner were found. He maintains a low public profile with no discoverable personal website, LinkedIn page, or social media presence [inferred from negative search results].

## Publications

### Papers

| Year | Title | Venue | Language |
|------|-------|-------|----------|
| 2011 | Gleitende Durchschnitte 3.0 | VTAD (research paper) [5][9] | German |
| 2012 | Moving Averages 3.0 | IFTA Journal, 2012 Edition, pp. 14–19 [2] | English |
| ~2019 | EMD for Technical Analysis | ResearchGate [4] | English |

### Books

| Year | Title | Publisher | ISBN | Pages |
|------|-------|-----------|------|-------|
| 2014 | Technische Analyse mit EMD: die Anwendung der EMD auf Indizes, Rohstoffe, Währungen und Aktien | Wiley-VCH (Weinheim), Wiley Trading series [3][7][8] | 978-3-527-50718-4 | 220 |

**Book structure** (based on reviews and publisher description) [8]:
- **Part 1:** Fundamental analysis, macroeconomics, behavioral finance overview
- **Part 2:** Technical analysis indicators — includes novel indicators developed by the author
- **Part 3:** Empirical Mode Decomposition (EMD) — mathematical foundations, application to price series, trading examples. Implementation uses Wolfram Mathematica.

**Contributor:** Michael Lehnert [7].

**Reception:** Mixed (2.5/5 on Amazon.de with 3 reviews). Criticized for not providing implementable code for the EMD portion; praised for Part 2's indicator innovations [8].

## Technical Indicators Created

### 1. New Moving Average (NMA) / 3rd Generation Moving Average

**The core innovation.** A lag-free moving average derived from signal processing theory [1][2][6].

**Problem solved:** All conventional moving averages (SMA, EMA, WMA) introduce temporal lag proportional to their period. This causes delayed signals at trend reversals [1].

**Method:** Apply two moving averages in cascade, then geometrically extrapolate to cancel the combined lag [1][2]:

$$\text{NMA}[n_1, n_2] = (1 + \alpha) \cdot \text{MA}_1[\text{price} \mid n_1] - \alpha \cdot \text{MA}_2[\text{MA}_1 \mid n_2]$$

where:

$$\alpha = \frac{\lambda \cdot (n_1 - 1)}{n_1 - \lambda}, \quad \lambda = \left\lfloor \frac{n_1}{n_2} \right\rfloor \geq 2$$

**The Nyquist constraint:** When a moving average is applied to already-smoothed data (resampling), the Nyquist-Shannon theorem requires: $n_1 \geq 2 \cdot n_2$. Violating this (as Ehlers' "Moving Averages 2.0" does with $n_1 = n_2$) can produce aliasing artifacts [1][2].

**Key properties:**
- Theoretical lag: **zero** bars [1][2]
- Recommended MA type: Linear Weighted Moving Average (LWMA) — smallest inherent lag [1]
- Best lag reduction at $\lambda = 2$ [6]; higher $\lambda$ increases similarity to classic MA
- When $\lambda = 1$ (degenerate case), formula reduces to Ehlers' MMA [1]

**Generations framework** [1][2]:
- Moving Averages 1.0: SMA, EMA, WMA (standard)
- Moving Averages 2.0: Ehlers' MMA, Mulloy's TEMA (lag reduction without Nyquist constraint)
- Moving Averages 3.0: Dürschner's NMA (Nyquist-constrained lag elimination)

### 2. NWMA Trading System (Medium-Term)

A complete trading system using the NMA as foundation [1][2]:

- **Signal chain:** Price → NWMA(89, 21) → Aroon Oscillator(5) → Inverse Fisher Transform
- **Rules:** Buy when IFT > 0, sell when IFT < 0
- **Timeframe:** Daily charts, stocks
- **Backtesting results** (104 stocks, 11 years, Jan 2000 – Jan 2011) [1]:
  - NWMA(89,21): +4,697% net profit (avg per share, from EUR 1,000)
  - NWMA(100,25): +3,229%
  - MWMA(89) [Ehlers]: +1,232%
  - WMA(89): +839%
  - SMA(89): +455%
  - Buy & Hold: +110%

### 3. StochRSI Intraday System (Short-Term)

- **Signal chain:** Price → NWMA(8, 3) → RSI(5) → Stochastic(3) → Inverse Fisher Transform [1][5]
- **Timeframe:** M15, designed for DAX intraday trading
- **Purpose:** Short-term scalping with lag-free price proxy

### 4. EMD-Based Technical Analysis ("Technical Analysis 2.0")

Dürschner's 2014 book applies NASA's Empirical Mode Decomposition (developed by Norden Huang) to financial time series [3][7]. The EMD decomposes a nonlinear, non-stationary signal into Intrinsic Mode Functions (IMFs) without requiring predefined basis functions.

**Application to markets** [3][7]:
- Decompose price series into oscillatory components (IMFs) + residual trend
- Each IMF represents a different time-scale of market behavior
- The residual represents the underlying trend stripped of noise
- Enables construction of modified Bollinger Bands, trend indicators, and timing signals

**Implementation:** Wolfram Mathematica [8]. No source code was published in the book — only mathematical formulations.

**Indicators mentioned in book context** (based on book keywords) [7]:
- EMD Trend extraction
- Modified Bollinger Bands (EMD-based)
- MACD variants using EMD decomposition
- RAVI (Range Action Verification Index) with EMD
- Aroon Oscillator on EMD output
- SRSI (Stochastic RSI) on EMD output
- Efficiency line ("Effizienzlinie")

## Community Reception and Impact

### Positive
- The NMA/3rd Generation Moving Average has been independently implemented in MQL4, Python, and other platforms by community members [5][6]
- Jürgen Moeck (simplex) created the first known MQL4 implementation in July 2013 [5]
- ThirdBrainFx distributes a MetaTrader indicator based on the method [6]
- The "Moving Averages 3.0" paper won the VTAD's top research award [3][5]
- One Amazon reviewer described Part 2 of the EMD book as the best practical inspiration they'd encountered across extensive trading literature [8]

### Critical
- The EMD book received criticism for not providing implementable code [8]
- Reviewers noted the EMD section occupies only ~90 of 300 pages, with the remainder covering standard topics [8]
- The backtesting methodology (equal periods across different MA types) was questioned by independent analysts as potentially unfair comparison [5]
- Forum members found the NMA's practical edge over conventional short-period MAs to be modest (1-2 bars faster, but more whipsaws) [5]

## Open Questions

- No confirmed photo or detailed personal biography beyond "PhD physicist, active trader"
- Exact university where doctorate was obtained is unknown
- Whether he continues to publish or trade actively (post-2019) is unclear
- The full content of the "EMD for Technical Analysis" ResearchGate paper could not be accessed (blocked)
- Relationship between the book's EMD approach and any commercial products/services is unknown

## Sources

| # | Source | Status |
|---|--------|--------|
| [1] | Dürschner, M. G. (2012). Moving Averages 3.0. *IFTA Journal*, 2012 Ed., pp. 14–19. Local copy: `inputs/manfred-dürschner/moving-averages-3.0/Moving-Averages-3.0.md` | verified |
| [2] | Dürschner, M. G. (2011). Gleitende Durchschnitte 3.0. IFTA Journal URL: https://www.ifta.org/assets/docs/d_ifta_journal_12.pdf | unverified (too large to fetch) |
| [3] | Google Books "Technische Analyse mit EMD" — author bio and metadata. https://books.google.com/books/about/Technische_Analyse_mit_EMD.html?id=p_w5BAAAQBAJ | verified |
| [4] | ResearchGate: "EMD for Technical Analysis." https://www.researchgate.net/publication/338105724_EMD_for_Technical_Analysis | blocked (403) |
| [5] | Moeck, J. (2013). Nyquist-Shannon Moving Average [Forum]. https://www.stevehopwoodforex.com/phpBB3/viewtopic.php?t=2637 | verified |
| [6] | ThirdBrainFx. 3rd Generation Moving Average. https://www.thirdbrainfx.com/indicator/3rd-generation-moving-average/ | verified |
| [7] | EconBiz library record. https://www.econbiz.de/Record/technische-analyse-mit-emd-die-anwendung-der-emd-auf-indizes-rohstoffe-währungen-und-aktien-dürschner-manfred/10010218571 | unverified (not fetched) |
| [8] | Amazon.com product page and reviews. https://www.amazon.com/Technische-Analyse-mit-EMD-Anwendung/dp/3527507183 | verified |
| [9] | Web Archive — VTAD paper. https://web.archive.org/web/20200109020131/http://www.vtad.de/sites/files/forschung/M_Duerschner_Gleitende_Durchschnnitte_3.pdf | unverified (not fetched) |
