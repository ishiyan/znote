# Marc Chaikin — Research Brief

## Biography

Marc Chaikin is a Wall Street veteran with a career spanning more than 50 years. He received his stockbroker's license on the exact day the bear market of 1966 ended — making his start on Wall Street in 1966 as a stockbroker with the most fortuitous timing possible [1].

Over the following decades, Chaikin worked at several major Wall Street firms. He served as senior vice president of Instinet Corp. (as of 1994) [1], and worked at firms including Drexel Burnham Lambert. He gravitated from brokerage toward trading and technical research after fundamental research repeatedly disappointed him [1].

In the 1970s–1980s, Chaikin developed the computerized stock selection models and technical indicators that would become industry standards. Building on the volume-analysis work of Joe Granville (On-Balance Volume) and Larry Williams (Accumulation/Distribution), he created the Chaikin Money Flow indicator, the Chaikin Oscillator, and the Chaikin Volatility indicator [1][2]. He also pioneered the first real-time analytics workstation for portfolio managers and stock traders [3].

Chaikin founded Chaikin Stock Research (later renamed Chaikin Analytics), headquartered online at chaikinanalytics.com. At the core of the company is the Chaikin Power Gauge, a 20-factor alpha model that combines fundamental and technical factors to rate stocks and ETFs [3]. The company is now part of MarketWise, Inc. and has a corporate affiliation with Stansberry Research [3].

Marc Chaikin has been featured in Barron's, Forbes, Bloomberg, CNBC (including endorsements from Jim Cramer on Mad Money), Fox Business, and numerous financial media outlets [3]. His indicators (particularly CMF and the Chaikin Oscillator) are built into virtually every charting platform worldwide, including MetaTrader, TradingView, StockCharts, Bloomberg Terminal, and TA-Lib.

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| Accumulation/Distribution Line (Chaikin variant) | ~1970s | Volume |
| Chaikin Money Flow (CMF) | ~1980s (TASC 1994) | Volume |
| Chaikin Oscillator (CHO) | ~1980s | Oscillator |
| Chaikin Volatility (CHV) | ~1980s | Channel |
| Chaikin Power Gauge | 2009 (proprietary) | Multi-purpose |
| Persistency of Money Flow | ~1990s | Volume |

### Indicator Formulas

#### Accumulation/Distribution Line (Chaikin Variant)

The Chaikin A/D Line uses the Close Location Value (CLV) rather than the simple close-to-close approach of Granville's OBV:

```
CLV = [(Close - Low) - (High - Close)] / (High - Low)
AD Line = Cumulative Sum of (CLV × Volume)
```

**Attribution note:** The Accumulation/Distribution concept is shared between Marc Chaikin and Larry Williams. Williams published the original Accumulation/Distribution formula in 1971. Chaikin's contribution was the Close Location Value (CLV) weighting, which scales volume by where the close falls within the day's range rather than simply comparing today's close to yesterday's.

#### Chaikin Money Flow (CMF)

```
CLV = [(Close - Low) - (High - Close)] / (High - Low)
Money Flow Volume = CLV × Volume
CMF(n) = Sum(Money Flow Volume, n) / Sum(Volume, n)
```

Default period: n = 20 or 21 days. Values range from -1 to +1. Positive CMF indicates buying pressure; negative indicates selling pressure.

#### Chaikin Oscillator (CHO)

```
AD Line = Cumulative Sum of [(CLV) × Volume]
CHO = EMA(AD Line, 3) - EMA(AD Line, 10)
```

The oscillator applies MACD-style logic to the Accumulation/Distribution Line. A cross above zero signals bullish momentum; a cross below zero signals bearish momentum.

#### Chaikin Volatility (CHV)

```
HL_EMA = EMA(High - Low, 10)
CHV = [(HL_EMA today - HL_EMA 10 days ago) / HL_EMA 10 days ago] × 100
```

This measures the rate of change of the trading range. Unlike ATR, it does not account for gaps. Chaikin's interpretation: a rapid increase in volatility over a short period indicates a bottom is near (panic selling); a decrease over a longer period indicates a top is approaching (mature bull market) [4].

#### Chaikin Power Gauge

A proprietary 20-factor stock rating system combining four categories:
1. **Financials** (earnings growth, profit margin, ROE, price-to-book, debt-to-equity)
2. **Earnings** (earnings surprises, estimate revisions, analyst consensus)
3. **Technicals** (relative price strength, price trend, volume trend, Chaikin Money Flow)
4. **Expert opinions** (analyst ratings, insider activity, short interest)

Output: Very Bearish / Bearish / Neutral / Bullish / Very Bullish rating for 3–6 month forward performance.

## Books

Marc Chaikin has not authored a standalone book. His indicator formulas and methodologies have been extensively documented in:

- **Technical Analysis from A to Z** by Steven B. Achelis — includes detailed entries on Chaikin Oscillator and Chaikin Volatility
- **Technical Analysis of the Financial Markets** by John J. Murphy — references Chaikin's indicators
- **Encyclopedia of Technical Market Indicators** by Robert W. Colby — detailed entries on CMF, CHO, CHV
- **New Trading Systems and Methods** by Perry J. Kaufman — discusses Chaikin indicators

## TASC Publications (Complete List, 1994–2016)

### 1994

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| January | Chatting With Marc Chaikin | Interview by Thom Hartle. Covers career from 1966, indicator development, Instinet work | [V.12:1 (30-37)](https://technical.traders.com/archive/article.asp?file=\V12\C01\CHATTIN.pdf) |
| January | Traders' Tips (MetaStock: Chaikin Money Flow) | MetaStock implementation of 21-day CMF discussed in interview | [V.12:1](https://technical.traders.com/archive/article.asp?file=\V12\C01\CHATTIN.pdf) |
| July | SIDEBAR: Chaikin's Money Flow Indicator | Formula and sample code for MetaStock and TradeStation | [V.12:7 (306-309)](https://technical.traders.com/archive/article.asp?file=\V12\C07\SIDEBC.pdf) |

### 1996

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| June | Mention in article on price/volume analysis | Referenced alongside Granville, Arms, Fosback as volume analysis pioneers | [V.14:6](https://technical.traders.com/archive/article.asp?file=\V14\C06\JIMBIAN.pdf) |

### 2015

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| December | Trade News & Products | "New Options Feature In Chaikin Analytics Platform" | [V.33:12](https://technical.traders.com/archive/article.asp?file=\V33\C12\119NEWS.pdf) |
| December | Letters To S&C | Discussion of "Money Flow Oscillator" | [V.33:12](https://technical.traders.com/archive/article.asp?file=\V33\C12\107LETT.pdf) |

### 2016

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| August | Product Review: Chaikin Analytics | Review by Barbara Star, Ph.D. of the Chaikin Analytics platform and Power Gauge | [V.34:8](https://technical.traders.com/archive/article.asp?file=\V34\C08\270PRCA.pdf) |

### 2017

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| February | Trade News & Products | "New Features In Chaikin Analytics Stock Research Platform" | [V.35:2](https://technical.traders.com/archive/article.asp?file=\V35\C02\384NEWS.pdf) |

## Articles by Category

| Category | Count | Articles |
|----------|-------|----------|
| Interview | 1 | Chatting With Marc Chaikin (Jan 1994) |
| Sidebar/Formula | 1 | Chaikin's Money Flow Indicator (Jul 1994) |
| Product Review | 1 | Chaikin Analytics (Aug 2016) |
| News/Mentions | 3 | Dec 2015, Feb 2017, Jun 1996 |

## Photos, Videos & Interviews

Marc Chaikin maintains a highly public media profile:

- **CNBC Mad Money**: Jim Cramer has publicly endorsed the Power Gauge system: "I want to explain why I love [Marc Chaikin's] stuff, it's simple, it's understandable, it's rational" [3]
- **Bloomberg TV**: Regular appearances discussing market analysis
- **Fox Business**: Featured guest
- **Chaikin Analytics YouTube Channel**: Company videos and market commentary
- **Stansberry Research**: Partnership for distribution of newsletters and research
- **Barron's, Forbes**: Feature articles
- **TASC Interview (1994)**: Detailed career interview with Thom Hartle [1]
- **Company "Who We Are" video**: Available at chaikinanalytics.com/whoweare [3]

## MQL5 Implementations

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Chaikin Money Flow | Artyom Trishkin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/49029 |
| Chaikin Oscillator (CHO) | MetaQuotes | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/19 |
| Chaikin Volatility (CHV) | MetaQuotes | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/20 |
| Chaikin Oscillator | MetaQuotes | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/7761 |
| Chaikin's Volatility - CHV | MetaQuotes | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/7058 |
| Chaikin Oscillator (smoothing selection) | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/476 |
| Chaikin Oscillator (averaging selection) | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/2439 |
| Chaikin Volatility Index (smoothing selection) | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/471 |
| Chaikin_Volatility | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/2432 |
| Chaikin Volatility Histogram | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/21498 |
| Stochastic Chaikin's Volatility | Giampiero Raschetti | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/8824 |
| Chaikin's Volatility (2 lines) | Scriptor | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/7974 |
| Chaikin Oscillator smoothed for MT4 | maximo | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/38974 |
| i-SpectrAnalysis_Chaikin | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/13756 |
| Chaikin_3HTF | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/13768 |
| CHO_3HTF | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/14559 |
| CHOWithFlat | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/11321 |
| CronexChaikin | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/2369 |
| ZigZag_CHO | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/16530 |
| IncCHOOnArray | Dmitry Fedoseev | MetaTrader 5 | Library | https://www.mql5.com/en/code/670 |
| IncCHVOnArray | Dmitry Fedoseev | MetaTrader 5 | Library | https://www.mql5.com/en/code/671 |
| One Two Three (EA using iChaikin) | Vladimir Karputov | MetaTrader 5 | Expert | https://www.mql5.com/en/code/22127 |
| Pipsover (EA using Chaikin) | Vladimir Karputov | MetaTrader 5 | Expert | https://www.mql5.com/en/code/17163 |
| Pipsover 2 | Vladimir Karputov | MetaTrader 5 | Expert | https://www.mql5.com/en/code/19981 |
| iCHO Trend CCIDualOnMA Filter | Vladimir Karputov | MetaTrader 5 | Expert | https://www.mql5.com/en/code/37799 |
| CHO Smoothed Arrow | Vladimir Karputov | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/38963 |
| CHO Smoothed Arrow 2 | Vladimir Karputov | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/39032 |
| Chaikin | Yury Reshetov | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/7679 |
| Pipsover (MT4) | Yury Reshetov | MetaTrader 4 | Expert | https://www.mql5.com/en/code/8167 |
| Stochastic_Chaikins_Volatility | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/18004 |
| Chaikin_Volatility_Stochastic | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/15772 |
| XCHV_HTF | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/17580 |
| KWAN_CCC | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/20608 |
| iCrossAD | Artyom Trishkin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/22753 |
| IncADOnArray | Dmitry Fedoseev | MetaTrader 5 | Library | https://www.mql5.com/en/code/669 |

**Total MQL5/MQL4 implementations found: 34** (across searches totaling 35+ for "Chaikin" general, 22 for CHO, 11 for CHV, 1 for CMF, 9 for A/D Line)

## Community & Reference Implementations

Chaikin's indicators are standard in virtually every technical analysis library:

- **TA-Lib**: `TA_AD()` (Chaikin A/D Line), `TA_ADOSC()` (Chaikin A/D Oscillator, fast=3/slow=10). Note: CMF is not a separate TA-Lib function but is computed from A/D values.
- **MetaTrader**: `iChaikin()` built-in function (Chaikin Oscillator is a standard MT4/MT5 indicator)
- **TradingView**: CMF and Chaikin Oscillator are built-in indicators available from the indicators menu
- **pandas-ta**: `df.ta.cmf()`, `df.ta.ad()`, `df.ta.adosc()`
- **StockCharts.com**: CMF is a standard overlay/indicator with educational articles
- **Bloomberg Terminal**: Available as standard technical study
- **Thinkorswim (TD Ameritrade/Schwab)**: Built-in ChaikinOsc and ChaikinMoneyFlow studies
- **Python (ta library)**: `ta.volume.ChaikinMoneyFlowIndicator`, `ta.volume.AccDistIndexIndicator`

## BibTeX

```bibtex
@article{hartle1994chaikin,
  author  = {Thom Hartle},
  title   = {Chatting With Marc Chaikin},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1994},
  volume  = {12},
  number  = {1},
  pages   = {30--37},
  url     = {https://technical.traders.com/archive/article.asp?file=\\V12\\C01\\CHATTIN.pdf}
}

@article{tasc1994cmf,
  author  = {{Technical Analysis, Inc.}},
  title   = {Sidebar: Chaikin's Money Flow Indicator},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1994},
  volume  = {12},
  number  = {7},
  pages   = {306--309},
  url     = {https://technical.traders.com/archive/article.asp?file=\\V12\\C07\\SIDEBC.pdf}
}

@article{star2016chaikin,
  author  = {Barbara Star},
  title   = {Product Review: Chaikin Analytics},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {2016},
  volume  = {34},
  number  = {8},
  url     = {https://technical.traders.com/archive/article.asp?file=\\V34\\C08\\270PRCA.pdf}
}

@book{achelis2000ta,
  author    = {Steven B. Achelis},
  title     = {Technical Analysis from A to Z},
  publisher = {McGraw-Hill},
  year      = {2000},
  edition   = {2nd},
  note      = {Includes entries on Chaikin Oscillator and Chaikin Volatility}
}

@misc{chaikinanalytics2026,
  author       = {{Chaikin Analytics}},
  title        = {Who We Are},
  year         = {2026},
  url          = {https://www.chaikinanalytics.com/whoweare},
  note         = {Accessed May 2026}
}

@misc{mql5_cho_official,
  author  = {MetaQuotes},
  title   = {Chaikin Oscillator (CHO)},
  year    = {2010},
  url     = {https://www.mql5.com/en/code/19},
  note    = {Official MetaTrader 5 implementation}
}

@misc{mql5_chv_official,
  author  = {MetaQuotes},
  title   = {Chaikin Volatility (CHV)},
  year    = {2010},
  url     = {https://www.mql5.com/en/code/20},
  note    = {Official MetaTrader 5 implementation}
}
```

## Sources

[1] Hartle, T. (1994). "Chatting With Marc Chaikin." *Technical Analysis of Stocks & Commodities*, V.12:1, pp. 30–37. https://technical.traders.com/archive/article.asp?file=\V12\C01\CHATTIN.pdf — *verified (URL live)*

[2] MQL5 Code Base — Chaikin Oscillator description by Nikolay Kositsin: "Chaikin Oscillator is named after its author Marc Chaikin and based on the Accumulation/Distribution indicator and a number of Joe Granville and Larry Williams works." https://www.mql5.com/en/code/476 — *verified*

[3] Chaikin Analytics. "Who We Are." https://www.chaikinanalytics.com/whoweare — *verified (fetched May 2026)*

[4] MetaQuotes. "Chaikin Volatility (CHV)." https://www.mql5.com/en/code/20 — *verified*

[5] Technical Analysis, Inc. (1994). "Sidebar: Chaikin's Money Flow Indicator." *TASC*, V.12:7, pp. 306–309. https://technical.traders.com/archive/article.asp?file=\V12\C07\SIDEBC.pdf — *verified (URL live)*

[6] Star, B. (2016). "Product Review: Chaikin Analytics." *TASC*, V.34:8. https://technical.traders.com/archive/article.asp?file=\V34\C08\270PRCA.pdf — *verified (URL live)*

[7] Chaikin Analytics homepage. https://www.chaikinanalytics.com — *verified (fetched May 2026)*

[8] MQL5 search results for "Chaikin" — total 35 codebase implementations found. https://search.mql5.com — *verified*
