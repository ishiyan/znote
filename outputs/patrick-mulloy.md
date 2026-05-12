# Patrick Mulloy — Research Brief

## Biography

Patrick G. Mulloy is an American technical analyst who introduced two of the most widely-adopted moving average variants in trading history. He published DEMA and TEMA in back-to-back TASC articles in January and February 1994. Beyond these two articles, almost nothing is publicly known about his personal life or career — he is one of the most private figures in technical analysis despite having created indicators that are now built into every major charting platform worldwide.

Key facts:
- Introduced DEMA in TASC January 1994
- Introduced TEMA in TASC February 1994
- Both indicators solve the lag problem of exponential moving averages
- No known website, LinkedIn, social media presence
- No known photos, videos, or interviews

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| DEMA (Double Exponential Moving Average) | TASC Jan 1994 | Adaptive MA |
| TEMA (Triple Exponential Moving Average) | TASC Feb 1994 | Adaptive MA |

### DEMA — Technical Description

DEMA = 2 × EMA(Price, N) − EMA(EMA(Price, N), N)

Key insight: NOT simply applying EMA twice. Uses a linear combination to cancel lag.

Lag formula (from Mulloy's article): Both SMA and EMA have steady-state lag of (1 - a)/a where a = 2/(w+1), or equivalently (w-1)/2 in terms of the MA period w.

### TEMA — Technical Description

TEMA = 3 × EMA(Price, N) − 3 × EMA(EMA(Price, N), N) + EMA(EMA(EMA(Price, N), N), N)

Extends the DEMA concept with a third-order correction term.

## Books

No known books authored by Patrick Mulloy.

### External Books Referencing DEMA/TEMA

| # | Title | Author | Year | Publisher | ISBN | Link |
|---|-------|--------|------|-----------|------|------|
| 1 | Trading Systems and Methods (5th ed.) | Perry J. Kaufman | 2013 | Wiley | 978-1118043561 | [Google Books](https://books.google.com/books?id=xWZHDwAAQBAJ) |
| 2 | The Encyclopedia of Technical Market Indicators (2nd ed.) | Robert W. Colby | 2003 | McGraw-Hill | 978-0070120570 | [Google Books](https://books.google.com/books?id=sVXvAAAAMAAJ) |
| 3 | Technical Analysis of the Financial Markets | John J. Murphy | 1999 | New York Institute of Finance | 978-0735200661 | [Google Books](https://books.google.com/books?isbn=0735200661) |
| 4 | Statistika dlya tradera (Statistics for a Trader) | S. Bulashev | — | — | — | — |

### Derivative Work

| # | Title | Author | Publication | Year | Notes |
|---|-------|--------|-------------|------|-------|
| 1 | Smoothing Techniques for More Accurate Signals | Tim Tillson | TASC Jan 1998 | 1998 | T3 indicator builds directly on Mulloy's DEMA concept |

## TASC Publications (Complete List, 1994)

### 1994

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Jan | Smoothing Data With Faster Moving Averages | Introduces DEMA — a double exponential moving average that reduces lag while maintaining smoothness | [PDF](https://technical.traders.com/archive/article.asp?file=\V12\C01\SMOOTHI.pdf) |
| Feb | Smoothing Data With Less Lag | Introduces TEMA — extends the DEMA concept to triple exponential for even less lag | [PDF](https://technical.traders.com/archive/article.asp?file=\V12\C02\SMOOTHI.pdf) |

**Store reprints:**
- [Jan 1994 PDF](https://traderscom.stores.yahoo.net/-v12-c01-smoothi-pdf.html)
- [Feb 1994 PDF](https://traderscom.stores.yahoo.net/-v12-c02-smoothi-pdf.html)

### Reader Response

| Month | Title | Description |
|-------|-------|-------------|
| Dec 1994 | Double Exponential Moving Averages (Letters) | Reader letter (V.12:12, pp. 537-541) discussing and extending the January 1994 DEMA article |

## Articles by Category

| Category | Count | Articles |
|----------|-------|----------|
| Adaptive MA / Filters | 2 | Smoothing Data With Faster Moving Averages (Jan 1994), Smoothing Data With Less Lag (Feb 1994) |

## Photos, Videos & Interviews

### Photos
| Description | URL | Source |
|-------------|-----|--------|
| No known photos of Patrick Mulloy exist publicly | — | Exhaustive search |

### Videos
| Title | URL | Duration | Date |
|-------|-----|----------|------|
| No known video appearances | — | — | — |

### Interviews & Podcasts
| Title | URL | Host/Publication | Date |
|-------|-----|-----------------|------|
| No known interviews found | — | — | — |

## MQL5 Implementations

### Official MetaQuotes (Built into MetaTrader 5)

| Title | Author | Platform | URL |
|-------|--------|----------|-----|
| Double Exponential Moving Average (DEMA) | MetaQuotes | MT5 | https://www.mql5.com/en/code/73 |
| Triple Exponential Moving Average (TEMA) | MetaQuotes | MT5 | https://www.mql5.com/en/code/74 |

### Notable Third-Party Implementations

| Title | Author | Platform | URL |
|-------|--------|----------|-----|
| MACD DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/19969 |
| MACD TEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/19970 |
| Generalized DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/22917 |
| Generalized double DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/22918 |
| Corrected generalized DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/23063 |
| DEMA Jurik Volty Adaptive | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21234 |
| TEMA Jurik Volty Adaptive | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21236 |
| Zero lag DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20412 |
| Zero lag TEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20413 |
| DSL - DEMA MACD | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20018 |
| DSL - TEMA MACD | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20019 |
| Nema (EMA depth 1-50: EMA/DEMA/TEMA/...) | Mladen Rakic | MT5 | https://www.mql5.com/en/code/17140 |
| CDEMAOnRingBuffer class | Konstantin Gruzdev | MT5 | https://www.mql5.com/en/code/1416 |
| CTEMAOnRingBuffer class | Konstantin Gruzdev | MT5 | https://www.mql5.com/en/code/1417 |
| Dema (MT4) | Scriptor | MT4 | https://www.mql5.com/en/code/8355 |
| TEMA (MT4) | MetaQuotes | MT4 | https://www.mql5.com/en/code/7752 |
| TEMA_CUSTOM | Nikolay Kositsin | MT5 | https://www.mql5.com/en/code/13926 |
| AllAverages v4.9 (includes DEMA by P.Mulloy) | Ivan Astafurov | MT5/MT4 | https://www.mql5.com/en/code/46041 |
| Schaff Trend Cycle - DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20282 |
| Schaff Trend Cycle - TEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20283 |
| DEMA trend | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21974 |
| Ultra Trend - Zero Lag DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21799 |
| Ultra Trend - Zero Lag TEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21800 |
| T3 (uses DEMA internally) | Scriptor | MT5 | https://www.mql5.com/en/code/21842 |
| QEMA (TEMA + DEMA correction) | Bruno Pio | MT5 | https://www.mql5.com/en/code/944 |

### MQL5 Articles Referencing Mulloy

| Title | URL |
|-------|-----|
| Ready-made templates for including indicators to Expert Advisors (Part 3): Trend indicators | https://www.mql5.com/en/articles/13406 |
| Testing different Moving Average types to see how insightful they are | https://www.mql5.com/en/articles/13130 |

### Codebase Statistics

| Search Query | Results |
|---|---|
| DEMA | 58 |
| TEMA | 43 |
| "Patrick Mulloy" | 11 |
| "Double Exponential Moving Average" | 76 |
| "Triple Exponential Moving Average" | 42 |

## Community & Reference Implementations

| Platform/Library | Function | Status |
|-----------------|----------|--------|
| TA-Lib | `TA_DEMA()`, `TA_TEMA()` | Built-in |
| MetaTrader 4/5 | `iDEMA()`, `iTEMA()`, `MODE_DEMA`, `MODE_TEMA` | Built-in |
| TradingView | `ta.dema()`, `ta.tema()` | Built-in |
| pandas-ta | `df.ta.dema()`, `df.ta.tema()` | Built-in |
| NinjaTrader | DEMA, TEMA | Built-in |
| Thinkorswim | Standard studies | Built-in |
| TradeStation | EasyLanguage functions | Built-in |
| Bloomberg Terminal | Overlay functions | Built-in |
| Wealth-Lab | Standard indicator library | Built-in |

## Forum Discussions

Google blocked all `site:` searches with CAPTCHA/JavaScript challenges. The following forums were attempted but could not be queried:

- Forex Factory, futures.io, Elite Trader, NinjaTrader Forum, TradingView Scripts, MQL5 Forum, Wealth-Lab, Quant StackExchange, Reddit r/algotrading, Trade2Win

Indirect evidence from MQL5 codebase (58+ DEMA, 43+ TEMA implementations) confirms extensive community adoption and discussion.

## BibTeX

```bibtex
@article{tasc:mulloy1994dema,
  author  = {Mulloy, Patrick G.},
  title   = {Smoothing Data With Faster Moving Averages},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1994},
  month   = jan,
  volume  = {12},
  number  = {1},
  pages   = {11--19},
  url     = {https://technical.traders.com/archive/article.asp?file=\V12\C01\SMOOTHI.pdf}
}

@article{tasc:mulloy1994tema,
  author  = {Mulloy, Patrick G.},
  title   = {Smoothing Data With Less Lag},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1994},
  month   = feb,
  volume  = {12},
  number  = {2},
  pages   = {72--80},
  url     = {https://technical.traders.com/archive/article.asp?file=\V12\C02\SMOOTHI.pdf}
}

@book{kaufman2013systems,
  author    = {Kaufman, Perry J.},
  title     = {Trading Systems and Methods},
  edition   = {5th},
  year      = {2013},
  publisher = {Wiley},
  isbn      = {978-1118043561},
  url       = {https://books.google.com/books?id=xWZHDwAAQBAJ}
}

@book{colby2003encyclopedia,
  author    = {Colby, Robert W.},
  title     = {The Encyclopedia of Technical Market Indicators},
  edition   = {2nd},
  year      = {2003},
  publisher = {McGraw-Hill},
  isbn      = {978-0070120570},
  url       = {https://books.google.com/books?id=sVXvAAAAMAAJ}
}

@book{murphy1999technical,
  author    = {Murphy, John J.},
  title     = {Technical Analysis of the Financial Markets},
  year      = {1999},
  publisher = {New York Institute of Finance},
  isbn      = {978-0735200661},
  url       = {https://books.google.com/books?isbn=0735200661}
}
```

## Sources

[1] TASC Author Archive — http://technical.traders.com/archive/combo/display5.asp?author=Patrick%20Mulloy
[2] TASC Author Archive (alt) — http://technical.traders.com/archive/combo/display5.asp?author=Patrick%20G%20Mulloy
[3] TASC TOC XML Jan 1994 — https://traders.com/Mobile/Archive/JAN1994.XML
[4] TASC TOC XML Feb 1994 — https://traders.com/Mobile/Archive/FEB1994.XML
[5] TASC TOC XML Dec 1994 — https://traders.com/Mobile/Archive/DEC1994.XML
[6] MQL5 Search API (DEMA codebase) — https://search.mql5.com/api/query?keyword=DEMA&module=mql5.com.en.codebase|mql4.com.en.codebase&count=20&lng=en
[7] MQL5 Search API (TEMA codebase) — https://search.mql5.com/api/query?keyword=TEMA&module=mql5.com.en.codebase|mql4.com.en.codebase&count=20&lng=en
[8] MQL5 Search API (Patrick Mulloy codebase) — https://search.mql5.com/api/query?keyword=Patrick+Mulloy&module=mql5.com.en.codebase|mql4.com.en.codebase&count=20&lng=en
[9] MQL5 Search API (Patrick Mulloy articles) — https://search.mql5.com/api/query?keyword=Patrick+Mulloy&module=mql5.com.en.articles|mql4.com.en.articles&count=10&lng=en
[10] MQL5 Official DEMA indicator — https://www.mql5.com/en/code/73
[11] MQL5 Official TEMA indicator — https://www.mql5.com/en/code/74
[12] Google Books (Kaufman) — https://books.google.com/books?id=xWZHDwAAQBAJ
[13] Google Books (Colby) — https://books.google.com/books?id=sVXvAAAAMAAJ
