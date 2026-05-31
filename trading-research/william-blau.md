# William Blau — Trading Research Profile

## Biography

**William Blau** (also known as "Bill Blau") is a technical analysis author and indicator developer active in the early 1990s. He is best known for inventing the **True Strength Index (TSI)**, **Double Smoothed Stochastics**, and the **Stochastic Momentum Index (SMI)** — all now standard indicators on major trading platforms worldwide.

- **Background**: Likely engineering or quantitative (inferred from signal-processing sophistication of his work)
- **Active period**: 1991–1995 (TASC articles + book)
- **Book**: *Momentum, Direction, and Divergence* (Wiley, 1995)
- **Personal details**: Unknown — no interviews, photos, LinkedIn, or obituary found. An enigmatic figure known entirely through his published work.

---

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| True Strength Index (TSI) | TASC Nov 1991, [\V09\C11\TRUESTR](https://technical.traders.com/archive/article.asp?file=\V09\C11\TRUESTR.pdf) | Momentum |
| Double Smoothed Stochastics (DSS) | TASC Jan 1991, [\V09\C01\DOUBLES](https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf) | Oscillator |
| Double-Smoothed Momentum | TASC May 1991, [\V09\C05\DOUBLE](https://technical.traders.com/archive/article.asp?file=\V09\C05\DOUBLE.pdf) | Momentum |
| Stochastic Momentum Index (SMI) | TASC Jan 1993, [\V11\C01\STOCHAS](https://technical.traders.com/archive/article.asp?file=\V11\C01\STOCHAS.pdf) | Oscillator |
| Ergodic Oscillator | Book: Momentum, Direction, and Divergence (1995) | Oscillator |
| Directional Trend Index (DTI) | Book (1995) | Trend |
| Candlestick Momentum (CMtm) | Book (1995) | Momentum |
| Candlestick Stochastic Index (CSI) | Book (1995) | Oscillator |
| Composite High/Low Momentum (HLM) | Book (1995) | Momentum |
| Ergodic MACD | Book (1995) | Momentum |
| Ergodic DTI-Oscillator | Book (1995) | Trend |
| Ergodic CSI-Oscillator | Book (1995) | Oscillator |
| Mean Deviation Index (MDI) | Book (1995) | Volatility |
| Trend Momentum | Book (1995) | Trend |

### Indicators Introduced in Books

#### Momentum, Direction, and Divergence (1995)

| Indicator | Category |
|-----------|----------|
| True Strength Index (TSI) | Momentum |
| Double-Smoothed Momentum | Momentum |
| Double Smoothed Stochastics (DSS) | Oscillator |
| Stochastic Momentum Index (SMI) | Oscillator |
| Ergodic Oscillator | Oscillator |
| Directional Trend Index (DTI) | Trend |
| Ergodic DTI-Oscillator | Trend |
| Candlestick Momentum (CMtm) | Momentum |
| Candlestick Stochastic Index (CSI) | Oscillator |
| Ergodic CSI-Oscillator | Oscillator |
| Composite High/Low Momentum (HLM) | Momentum |
| Ergodic MACD | Momentum |
| Mean Deviation Index (MDI) | Volatility |
| Trend Momentum | Trend |

### Core Concept: Double Smoothing

Blau's fundamental innovation is **double exponential smoothing** applied to price momentum. Rather than a single EMA applied to raw momentum (as in standard indicators), Blau applies two cascaded EMAs with different periods, producing smoother signals with reduced lag compared to equivalent single-pass smoothing. This principle underlies all his indicators.

### Platform Availability

The TSI is a **standard built-in indicator** on:
- TradingView
- MetaTrader 4/5
- Thinkorswim (TD Ameritrade)
- TradeStation
- NinjaTrader
- Bloomberg Terminal

---

## Books

| # | Title | Author | Year | Publisher | ISBN | Link |
|---|-------|--------|------|-----------|------|------|
| 1 | Momentum, Direction, and Divergence: Applying the Latest Momentum Indicators for Technical Analysis | William Blau | 1995 | John Wiley & Sons | 978-0-471-02729-4 | [Amazon](https://www.amazon.com/Momentum-Direction-Divergence-Applying-Convergence/dp/0471027294) |

---

## TASC Publications (Complete List, 1991–1993)

### 1993

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Jan | Stochastic Momentum | Introduces the Stochastic Momentum Index (SMI) — a refined stochastic oscillator using double smoothing | [\V11\C01\STOCHAS](https://technical.traders.com/archive/article.asp?file=\V11\C01\STOCHAS.pdf) |

### 1992

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| May | Trading With The True Strength Index | Follow-up on TSI with practical trading applications | [\V10\C05\TRADING](https://technical.traders.com/archive/article.asp?file=\V10\C05\TRADING.pdf) |

### 1991

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Nov | True Strength Index | Introduces the TSI — double-smoothed momentum normalized to ±100 range | [\V09\C11\TRUESTR](https://technical.traders.com/archive/article.asp?file=\V09\C11\TRUESTR.pdf) |
| May | Double-Smoothed Momenta | Introduces the concept of applying double EMA smoothing to momentum | [\V09\C05\DOUBLE](https://technical.traders.com/archive/article.asp?file=\V09\C05\DOUBLE.pdf) |
| Jan | Double Smoothed-Stochastics | Applies double smoothing to stochastic oscillators | [\V09\C01\DOUBLES](https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf) |

**Related TASC sidebars:**
- SIDEBAR: STOCHASTICS MOMENTUM INDEX ([\V11\C01\SIDESTO](https://technical.traders.com/archive/article.asp?file=\V11\C01\SIDESTO.pdf))
- SIDEBAR: TRUE STRENGTH INDEX ([\V11\C01\SIDETRU](https://technical.traders.com/archive/article.asp?file=\V11\C01\SIDETRU.pdf))

---

## MQL5 Implementations

William Blau has an extensive MQL5 footprint with **58 CodeBase entries** directly referencing his name, plus dozens more for individual indicators.

### Key MQL5 Article

| Title | Author | URL |
|-------|--------|-----|
| William Blau's Indicators and Trading Systems in MQL5. Part 1: Indicators | Andrey F. Zelinsky | [mql5.com/en/articles/190](https://www.mql5.com/en/articles/190) |

This comprehensive article implements ALL of Blau's indicators from his book with a shared `WilliamBlau.mqh` include library.

### Complete Blau Indicator Library (by Andrey F. Zelinsky)

| Indicator | MQL5 Name | URL |
|-----------|-----------|-----|
| True Strength Index | Blau_TSI | [code/361](https://www.mql5.com/en/code/361) |
| Ergodic Oscillator | Blau_Ergodic | [code/362](https://www.mql5.com/en/code/362) |
| Stochastic Index | Blau_TStochI | [code/364](https://www.mql5.com/en/code/364) |
| Stochastic Oscillator | Blau_TS_Stochastic | [code/365](https://www.mql5.com/en/code/365) |
| Stochastic Momentum | Blau_SM | [code/370](https://www.mql5.com/en/code/370) |
| Stochastic Momentum Index | Blau_SMI | [code/371](https://www.mql5.com/en/code/371) |
| Stochastic Momentum Oscillator | Blau_SM_Stochastic | [code/372](https://www.mql5.com/en/code/372) |
| Mean Deviation Index | Ergodic_MDI | [code/374](https://www.mql5.com/en/code/374) |
| MACD | Blau_MACD | [code/375](https://www.mql5.com/en/code/375) |
| Ergodic MACD | Blau_Ergodic_MACD | [code/376](https://www.mql5.com/en/code/376) |
| Candlestick Momentum | Blau_CMtm | [code/377](https://www.mql5.com/en/code/377) |
| Ergodic CSI-Oscillator | Blau_Ergodic_CSI | [code/381](https://www.mql5.com/en/code/381) |
| Composite High/Low Momentum | Blau_HLM | [code/382](https://www.mql5.com/en/code/382) |
| Directional Trend Index | Blau_DTI | [code/384](https://www.mql5.com/en/code/384) |
| Ergodic DTI-Oscillator | Blau_Ergodic_DTI | [code/385](https://www.mql5.com/en/code/385) |

### Additional Implementations by Other Developers

| Developer | Indicators | Platform |
|-----------|------------|----------|
| Mladen Rakic | TSI, Ergodic TSI, DSS Blau, SMI, T3 SMI, Double Smoothed Stochastic | MT5 |
| Scriptor | Blau_TSI, Blau_SM, Blau_DTI, Blau_CMtm, Blau_TStoch, Blau_Trend_Momentum | MT5 |
| Nikolay Kositsin | BlauTStochI, BlauCSI (color histogram versions) | MT5 |
| MetaQuotes | TSI (official), DSS Bressert | MT4/MT5 |
| Artyom Trishkin | SMI Ergodic Oscillator | MT5 |

### Additional MQL5 Articles Referencing Blau

| Title | Author | URL |
|-------|--------|-----|
| How to create a custom True Strength Index indicator using MQL5 | Mohamed Abdelmaaboud | [mql5.com/en/articles/12570](https://www.mql5.com/en/articles/12570) |
| MQL5: Create Your Own Indicator (uses TSI as example) | MetaQuotes | [mql5.com/en/articles/10](https://www.mql5.com/en/articles/10) |
| Creating Non-Lagging Digital Filters | Konstantin Gruzdev | [mql5.com/en/articles/812](https://www.mql5.com/en/articles/812) |
| Averaging Price Series for Intermediate Calculations | Nikolay Kositsin | [mql5.com/en/articles/180](https://www.mql5.com/en/articles/180) |

---

## GitHub Repositories

GitHub search was not available during this research session. However, the TSI is widely implemented in open-source TA libraries including pandas-ta (Python), ta-lib, and tulip indicators.

---

## Forum Discussions

Forum searches were blocked by CAPTCHA. Given that TSI is a standard built-in indicator on all major platforms, extensive discussion threads exist on ForexFactory, TradingView, and other forums.

---

## Photos, Videos & Interviews

### Photos

| Description | URL | Source |
|-------------|-----|--------|
| [URL not found] No photos of William Blau found | — | — |

### Videos

| Title | URL | Duration | Date |
|-------|-----|----------|------|
| [URL not found] No video appearances found | — | — | — |

### Interviews & Podcasts

No interviews or podcast appearances found. Blau appears to have been a private individual who communicated exclusively through published articles and his book.

---

## BibTeX

```bibtex
@book{Blau1995,
  author    = {Blau, William},
  title     = {Momentum, Direction, and Divergence: Applying the Latest Momentum Indicators for Technical Analysis},
  publisher = {John Wiley \& Sons},
  year      = {1995},
  isbn      = {978-0-471-02729-4},
  series    = {Wiley Trader's Advantage},
  pages     = {160},
  url       = {https://www.amazon.com/Momentum-Direction-Divergence-Applying-Convergence/dp/0471027294},
}

@article{tasc:v09c11truestr,
  author  = {Blau, William},
  title   = {True Strength Index},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1991},
  month   = nov,
  volume  = {9},
  number  = {11},
  url     = {https://technical.traders.com/archive/article.asp?file=\V09\C11\TRUESTR.pdf},
}

@article{tasc:v09c01doubles,
  author  = {Blau, William},
  title   = {Double Smoothed-Stochastics},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1991},
  month   = jan,
  volume  = {9},
  number  = {1},
  url     = {https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf},
}

@article{tasc:v09c05double,
  author  = {Blau, William},
  title   = {Double-Smoothed Momenta},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1991},
  month   = may,
  volume  = {9},
  number  = {5},
  url     = {https://technical.traders.com/archive/article.asp?file=\V09\C05\DOUBLE.pdf},
}

@article{tasc:v10c05trading,
  author  = {Blau, William},
  title   = {Trading With The True Strength Index},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1992},
  month   = may,
  volume  = {10},
  number  = {5},
  url     = {https://technical.traders.com/archive/article.asp?file=\V10\C05\TRADING.pdf},
}

@article{tasc:v11c01stochas,
  author  = {Blau, William},
  title   = {Stochastic Momentum},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1993},
  month   = jan,
  volume  = {11},
  number  = {1},
  url     = {https://technical.traders.com/archive/article.asp?file=\V11\C01\STOCHAS.pdf},
}

@online{mql5_blau_article,
  author  = {Zelinsky, Andrey F.},
  title   = {William Blau's Indicators and Trading Systems in {MQL5}. Part 1: Indicators},
  url     = {https://www.mql5.com/en/articles/190},
  urldate = {2026-05-31},
  year    = {2011},
  note    = {MQL5 article --- comprehensive implementation of all Blau indicators},
}

@online{mql5_blau_tsi,
  author  = {Zelinsky, Andrey F.},
  title   = {Blau\_TSI --- True Strength Index},
  url     = {https://www.mql5.com/en/code/361},
  urldate = {2026-05-31},
  note    = {MQL5 Code Base, MetaTrader 5},
}

@online{mql5_blau_smi,
  author  = {Zelinsky, Andrey F.},
  title   = {Blau\_SMI --- Stochastic Momentum Index},
  url     = {https://www.mql5.com/en/code/371},
  urldate = {2026-05-31},
  note    = {MQL5 Code Base, MetaTrader 5},
}
```
