# Donald Lambert — Research Brief

## Biography

Donald R. Lambert is a technical analyst and commodity trader who developed the Commodity Channel Index (CCI), one of the most widely used oscillators in technical analysis. Lambert first published the CCI in the October 1980 issue of *Commodities* magazine (later renamed *Futures* magazine, now *Modern Trader*). The indicator was designed to identify cyclical turns in commodity prices.

Lambert observed that many commodities displayed cyclic patterns reminiscent of sine waves. He formulated the CCI to measure the deviation of a commodity's price from its average statistical price, using mean absolute deviation as the normalization factor. The constant 0.015 was chosen so that approximately 70–80% of CCI values would fall within the ±100 range, making readings outside that band signals of unusually strong trends.

Lambert later contributed articles to *Technical Analysis of Stocks & Commodities* (TASC) magazine starting with its earliest volumes (Vol. 1, 1983). His contributions covered the CCI, exponentially smoothed moving averages, and a critical analysis of Bézier curves as a trading tool. No published books by Lambert are known.

## Technical Indicators & Tools

| Indicator | First Published | Category |
|-----------|----------------|----------|
| Commodity Channel Index (CCI) | *Commodities* magazine, Oct 1980 | Oscillator |

### Commodity Channel Index (CCI)

**Formula:**
```
CCI = (Typical Price - SMA of Typical Price) / (0.015 × Mean Absolute Deviation)
```
Where Typical Price = (High + Low + Close) / 3.

**Purpose:** Measures the current price level relative to an average price level over a given period. High values indicate prices are far above their average (overbought); low values indicate prices are far below their average (oversold). Originally designed to identify cyclical turns in commodities, it is now applied universally to stocks, ETFs, indices, and other securities.

**Key usage patterns:**
- Overbought/oversold identification (±100 levels)
- Divergence detection
- Trend identification (sustained readings above +100 or below −100)
- Zero-line crossovers

## Books

No known published books by Donald R. Lambert.

## TASC Publications (Complete List, 1983–1990)

### 1983
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Jul (V.1:5) | Commodity Channel Index: Tool for Trading Cyclic Trends | Explains how to calculate and use the CCI for identifying cyclical and seasonal price trends in stocks and commodities | [PDF](https://technical.traders.com/archive/article.asp?file=\V01\C05\COMM.PDF) |

### 1984
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Sep (V.2:5) | Exponentially Smoothed Moving Averages | Discussion of exponentially smoothed moving averages and their application to trading | [PDF](https://technical.traders.com/archive/article.asp?file=\V02\C05\EXPO.PDF) |

### 1990
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Aug (V.8:8) | Bézier Curves: No Tool For Trading | Critical analysis arguing that Bézier curves are not suitable as a trading tool | [PDF](https://technical.traders.com/archive/article.asp?file=\V08\C08\BEZIER.pdf) |

## Articles by Category

| Category | Count | Articles |
|----------|-------|----------|
| Oscillator | 1 | Commodity Channel Index: Tool for Trading Cyclic Trends (Jul 1983) |
| Filter / Moving Average | 1 | Exponentially Smoothed Moving Averages (Sep 1984) |
| Critique / Methodology | 1 | Bézier Curves: No Tool For Trading (Aug 1990) |

## MQL5 Implementations

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Commodity Channel Index (CCI) | MetaQuotes | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/18 |
| Commodity Channel Index, CCI | MetaQuotes | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/7769 |
| Exponential Commodity Channel Index | Fernando Carreiro | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/43864 |
| Exponential Commodity Channel Index | Fernando Carreiro | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/43863 |
| CCI alternative | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/19942 |
| Woodies CCI | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/19912 |
| Adaptive CCI | Josemir Da Silva Dias | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/62155 |
| QQE of CCI | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/21802 |
| PCCI | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/409 |
| PCCI | Scriptor | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/7342 |
| IncCCIOnArray | Dmitry Fedoseev | MetaTrader 5 | Library | https://www.mql5.com/en/code/649 |
| iCCI iMA | Vladimir Karputov | MetaTrader 5 | Expert | https://www.mql5.com/en/code/18776 |
| Example of Commodity Channel Index Automated | Mohammed Abdulwadud Soubra | MetaTrader 4 | Expert | https://www.mql5.com/en/code/15213 |
| CCI and Martin | Vladimir Karputov | MetaTrader 5 | Expert | https://www.mql5.com/en/code/21511 |
| Starter | Vladimir Karputov | MetaTrader 5 | Expert | https://www.mql5.com/en/code/22647 |

*Total MQL5/MQL4 codebase results for "Commodity Channel Index": 85*

## Traders' Tips

N/A — CCI was introduced before the Traders' Tips section began (2009+).

## Indicators Introduced in Books

N/A — No known published books by Donald R. Lambert.

## BibTeX

```bibtex
@article{lambert1980cci,
  author  = {Lambert, Donald R.},
  title   = {Commodity Channel Index: Tools for Trading Cyclic Trends},
  journal = {Commodities},
  year    = {1980},
  month   = oct,
  note    = {Later renamed Futures magazine, now Modern Trader}
}

@article{lambert1983cci_tasc,
  author  = {Lambert, Donald R.},
  title   = {Commodity Channel Index: Tool for Trading Cyclic Trends},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1983},
  volume  = {1},
  number  = {5},
  pages   = {120--122},
  month   = jul,
  url     = {https://technical.traders.com/archive/article.asp?file=\V01\C05\COMM.PDF}
}

@article{lambert1984ema,
  author  = {Lambert, Donald R.},
  title   = {Exponentially Smoothed Moving Averages},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1984},
  volume  = {2},
  number  = {5},
  pages   = {182--183},
  month   = sep,
  url     = {https://technical.traders.com/archive/article.asp?file=\V02\C05\EXPO.PDF}
}

@article{lambert1990bezier,
  author  = {Lambert, Donald R.},
  title   = {B\'{e}zier Curves: No Tool For Trading},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1990},
  volume  = {8},
  number  = {8},
  pages   = {313--315},
  month   = aug,
  url     = {https://technical.traders.com/archive/article.asp?file=\V08\C08\BEZIER.pdf}
}
```

## Sources

[1] TASC Mobile Archive XML, Jul 1983 — `https://traders.com/Mobile/Archive/JUL1983.XML` (verified, contains Lambert article listing)
[2] TASC Mobile Archive XML, Sep 1984 — `https://traders.com/Mobile/Archive/SEP1984.XML` (verified, contains Lambert article listing)
[3] TASC Mobile Archive XML, Aug 1990 — `https://traders.com/Mobile/Archive/AUG1990.XML` (verified, contains Lambert article listing)
[4] TASC Mobile Archive XML, Feb 1992 — `https://traders.com/Mobile/Archive/FEB1992.XML` (verified, mentions Lambert as CCI creator in Barbara Star article)
[5] MQL5 Codebase Search API — `https://search.mql5.com/api/query?keyword=Commodity+Channel+Index&module=mql5.com.en.codebase|mql4.com.en.codebase` (verified, 85 total results)
[6] MQL5 Article: "CCI indicator. Upgrade and new features" by Aleksej Poljakov — `https://www.mql5.com/en/articles/11126` (verified, confirms Lambert published CCI in Commodities magazine 1980)
[7] MQL5 Code: "CCI alternative" by Mladen Rakic — `https://www.mql5.com/en/code/19942` (verified, states "Developed by Donald Lambert and featured in 'Commodities' magazine in 1980")
[8] TASC Author Archive page for "Donald Lambert" — `http://technical.traders.com/archive/combo/display5.asp?author=Donald%20Lambert` (verified, returns "XML could not be found" — no indexed XML file under this name variant)
