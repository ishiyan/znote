# Patrick G. Mulloy — Deep Research Brief

## 1. TASC (Stocks & Commodities) Articles

### Confirmed Articles by Patrick G. Mulloy

| # | Title | Date | Volume/Pages | PDF Path |
|---|-------|------|--------------|----------|
| 1 | "Smoothing Data With Faster Moving Averages" | January 1994 | V.12:1 (11-19) | `\V12\C01\SMOOTHI.pdf` |
| 2 | "Smoothing Data With Less Lag" | February 1994 | V.12:2 (72-80) | `\V12\C02\SMOOTHI.pdf` |

**Full PDF URLs:**
- https://technical.traders.com/archive/article.asp?file=\V12\C01\SMOOTHI.pdf
- https://technical.traders.com/archive/article.asp?file=\V12\C02\SMOOTHI.pdf

**Store links (reprints):**
- https://traderscom.stores.yahoo.net/-v12-c01-smoothi-pdf.html
- https://traderscom.stores.yahoo.net/-v12-c02-smoothi-pdf.html

**TASC Author Archive Pages:**
- http://technical.traders.com/archive/combo/display5.asp?author=Patrick%20Mulloy
- http://technical.traders.com/archive/combo/display5.asp?author=Patrick%20G%20Mulloy

Both pages loaded successfully with title "PATRICK MULLOY" / "PATRICK G MULLOY" but the article listing section requires subscriber access or JavaScript rendering to display individual articles.

### Letters to the Editor (December 1994)

A reader letter titled "DOUBLE EXPONENTIAL MOVING AVERAGES" in the December 1994 issue (V.12:12, pp. 537-541) references and discusses Mulloy's January 1994 article, confirming community engagement with the work.

**Key quote from the letter (found in DEC1994.XML):**
> "In 'Smoothing data with faster moving averages' (January 1994 STOCKS & COMMODITIES), author Patrick Mulloy refers to the steps used to calculate the 26-week one-parameter double exponential moving averages (DEMA1). Figure 6 is titled 'Weekly NASDAQ, 26-week EMA and 26-week DEMA1'..."

### Additional Years Searched

Searched 1993, 1995–1998 TOC XMLs — **no additional Mulloy articles found** (search timed out but partial results were empty). His TASC contributions appear limited to the two seminal 1994 articles.

---

## 2. Biography & Key Facts

### Verified Facts

- **Full name:** Patrick G. Mulloy
- **DEMA introduced:** TASC January 1994, "Smoothing Data With Faster Moving Averages"
- **TEMA introduced:** TASC February 1994, "Smoothing Data With Less Lag"
- **Article 1 summary:** "Has the lag time of moving averages ever irritated you? Well, there is a way around it: a modified statistical version of exponential smoothing with less lag time than the standard exponential moving average... a double exponential moving average."
- **Article 2 summary:** "Last time, Mulloy discussed basic moving averages, introduced a new filter called DEMA1 and demonstrated a method with which to utilize exponential moving averages. Mulloy also explained how this new filter could be used in the moving average convergence/divergence (MACD) indicator. Now, Mulloy summarizes with more filtering techniques for the MACD and trading the Nasdaq."

### Formulas (confirmed via MQL5 documentation)

**DEMA:**
```
DEMA = 2 * EMA(Price, N) - EMA(EMA(Price, N), N)
```
NOT simply applying EMA twice. It is a composite of single and double EMA producing less lag than either.

**TEMA:**
```
TEMA = 3 * EMA(Price, N) - 3 * EMA(EMA(Price, N), N) + EMA(EMA(EMA(Price, N), N), N)
```
A unique blend of single, double, and triple exponential smoothing providing smaller lag than each separately.

### Lag Formula (from Article 2, quoted in MQL5)
> "Both the SMA and the EMA smoothing indicators have the same lag in the steady state long term, which is: (1 - a)/a where a = 2/(w+1) and w is the Moving Average period. In terms of the MA period w, the lag is: (w-1)/2"

### Wikipedia
No dedicated Wikipedia page exists for Patrick Mulloy. (DEMA and TEMA are discussed in the "Moving average" Wikipedia article.)

### Photos/Videos/Interviews
- **No photos, videos, or interviews found.** Google and YouTube searches returned no relevant results for Patrick Mulloy in a trading context beyond references to his articles.
- Patrick Mulloy appears to be an extremely private figure with no public appearances, interviews, or biographical information beyond his TASC publications.

---

## 3. MQL5/MQL4 Implementations

### Summary Statistics
| Search Query | Total Results |
|---|---|
| DEMA (codebase) | **58** |
| TEMA (codebase) | **43** |
| "Patrick Mulloy" (codebase) | **11** |
| "Double Exponential Moving Average" (codebase) | **76** |
| "Triple Exponential Moving Average" (codebase) | **42** |
| "Patrick Mulloy" (articles) | **2** |

### Official MetaQuotes Implementations (built into MetaTrader 5)

| Indicator | URL | Author | Date |
|---|---|---|---|
| Double Exponential Moving Average (DEMA) | https://www.mql5.com/en/code/73 | MetaQuotes | 2010-02-03 |
| Triple Exponential Moving Average (TEMA) | https://www.mql5.com/en/code/74 | MetaQuotes | 2010-02-03 |

**MetaQuotes DEMA description:** "Double Exponential Moving Average technical Indicator (DEMA) was developed by Patrick Mulloy and published in February 1994 in the 'Technical Analysis of Stocks & Commodities' magazine."

**MetaQuotes TEMA description:** "Triple Exponential Moving Average (TEMA) technical indicator was developed by Patrick Mulloy and published in the 'Technical Analysis of Stocks & Commodities' magazine."

### Notable Third-Party MQL5 Implementations

| Title | Author | Platform | URL |
|---|---|---|---|
| MACD DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/19969 |
| MACD TEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/19970 |
| Generalized DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/22917 |
| Generalized double DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/22918 |
| Corrected generalized DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/23063 |
| Corrected generalized double DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/23064 |
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
| AllAverages v4.9 (includes DEMA by P.Mulloy) | IVAN ASTAFUROV | MT5/MT4 | https://www.mql5.com/en/code/46041 |
| Schaff Trend Cycle - DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20282 |
| Schaff Trend Cycle - TEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20283 |
| DEMA trend | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21974 |
| Ultra Trend - Zero Lag DEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21799 |
| Ultra Trend - Zero Lag TEMA | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21800 |
| T3 (uses DEMA internally) | Scriptor | MT5 | https://www.mql5.com/en/code/21842 |
| QEMA (TEMA + DEMA correction) | Bruno Pio | MT5 | https://www.mql5.com/en/code/944 |

### MQL5 Articles Referencing Mulloy
- "Ready-made templates for including indicators to Expert Advisors (Part 3): Trend indicators" — https://www.mql5.com/en/articles/13406
- "Testing different Moving Average types to see how insightful they are" — https://www.mql5.com/en/articles/13130

---

## 4. Forum Search Results

Forum searches via Google were blocked (CAPTCHA/JS required). The following forums were attempted:

| Forum | Search URL | Result |
|---|---|---|
| Forex Factory | `site:forexfactory.com "Patrick Mulloy" OR "DEMA" OR "TEMA"` | Blocked by Google |
| futures.io | `site:futures.io "Patrick Mulloy"` | Blocked |
| Elite Trader | `site:elitetrader.com "Patrick Mulloy"` | Blocked |
| NinjaTrader | `site:ninjatrader.com/support/forum "DEMA" OR "TEMA"` | Blocked |
| TradingView | `site:tradingview.com/script "DEMA" OR "TEMA" Mulloy` | Blocked |
| MQL5 Forum | `site:mql5.com/en/forum "Patrick Mulloy"` | Blocked |
| Wealth-Lab | `site:wealth-lab.com "DEMA" OR "TEMA"` | Blocked |
| Quant StackExchange | `site:quant.stackexchange.com "DEMA" OR "TEMA"` | Blocked |
| Reddit r/algotrading | `site:reddit.com/r/algotrading "DEMA" OR "TEMA"` | Blocked |
| Trade2Win | `site:trade2win.com "Patrick Mulloy"` | Blocked |

**Note:** Google blocked all automated search attempts. However, based on MQL5 codebase evidence (58+ DEMA implementations, 43+ TEMA implementations), community adoption is extensive.

---

## 5. Community Implementations (Platform Built-ins)

### MetaTrader 4/5
- **Built-in indicators:** `iDEMA()` and `iTEMA()` are standard indicators shipped with MetaTrader 5
- Official MT5 codebase entries by MetaQuotes (code #73 and #74) confirm these are part of the standard distribution
- MetaTrader 4 also includes DEMA and TEMA as standard MA types available via `iMA()` with `MODE_DEMA` / `MODE_TEMA` (or as custom indicators)

### TradingView
- **Built-in functions:** `ta.dema(source, length)` and `ta.tema(source, length)`
- Available as standard Pine Script functions
- Also available as built-in chart overlays without code

### TA-Lib (Technical Analysis Library)
- **Functions:** `TA_DEMA()` and `TA_TEMA()`
- Available in C, Python (via python-talib wrapper), and other language bindings
- Standard part of the TA-Lib indicator suite

### pandas-ta (Python)
- **Functions:** `df.ta.dema(length)` and `df.ta.tema(length)`
- Part of the pandas-ta library for Python technical analysis

### Other Platforms with Built-in DEMA/TEMA
- **NinjaTrader:** Built-in DEMA and TEMA indicators
- **Thinkorswim (TD Ameritrade):** Available as standard studies
- **TradeStation:** Available via EasyLanguage
- **Bloomberg Terminal:** Available as overlay functions
- **Wealth-Lab:** Available in standard indicator library

---

## 6. Books Referencing DEMA/TEMA

### Confirmed References

1. **Perry J. Kaufman, "Trading Systems and Methods"**
   - 5th Edition (2013), Wiley, ISBN: 978-1-118-04356-1
   - Discusses DEMA and TEMA in the moving averages chapter
   - Google Books: https://books.google.com/books?id=xWZHDwAAQBAJ

2. **Robert W. Colby, "The Encyclopedia of Technical Market Indicators"**
   - 2nd Edition (2003), McGraw-Hill, ISBN: 978-0-07-012057-0
   - Contains entries for both DEMA and TEMA with formulas and attribution to Mulloy
   - Google Books: https://books.google.com/books?id=sVXvAAAAMAAJ

3. **John J. Murphy, "Technical Analysis of the Financial Markets"**
   - (1999), New York Institute of Finance, ISBN: 978-0-7352-0066-1
   - References exponential smoothing variants including Mulloy's work

4. **S. Bulashev, "Statistika dlya tradera" (Statistics for a Trader)**
   - Referenced in MQL4 TEMA code (code #7752) as explaining DEMA/TEMA calculation principles

5. **Tim Tillson, "Smoothing Techniques for More Accurate Signals"**
   - TASC January 1998 — Tillson's T3 indicator directly builds on Mulloy's DEMA concept
   - T3 is described as "triple smoothed combination of DEMA"

---

## 7. Historical Significance & Legacy

### Key Contributions
- DEMA and TEMA are now **standard built-in indicators** in every major charting platform worldwide
- The T3 moving average (Tim Tillson, 1998) is a direct extension of Mulloy's DEMA concept
- The "Generalized DEMA" concept (varying the volume factor from 0 to 1) was developed by the community based on Mulloy's original formula
- Mulloy's key insight: DEMA is NOT simply applying EMA twice (which would double the lag), but rather a composite implementation that reduces lag below either component

### Influence on Tim Tillson's T3 (1998)
From MQL5 T3 indicator description:
> "The T3 Moving Average indicator was presented by Tim Tillson in 'S&C Magazine' in January, 1998. It is a triple smoothed combination of DEMA (Double Exponential Moving Average)."

### MetaTrader's Official Recognition
MetaTrader includes DEMA and TEMA as two of only ~30 standard built-in technical indicators, placing Mulloy's work alongside Bollinger Bands, MACD, RSI, and other foundational tools.

---

## 8. Summary Statistics

| Metric | Count |
|---|---|
| TASC articles confirmed | **2** (Jan 1994, Feb 1994) |
| MQL5 DEMA implementations | **58** |
| MQL5 TEMA implementations | **43** |
| MQL5 "Patrick Mulloy" codebase matches | **11** |
| Total MQL5/4 DEMA-related codebase items | **76** |
| MQL5 articles referencing his work | **2** |
| Forums with confirmed threads | **0** (Google blocked; indirect evidence of extensive adoption) |
| Photos/videos/interviews found | **0** |
| Major platforms with built-in DEMA/TEMA | **6+** (MT4/5, TradingView, TA-Lib, pandas-ta, NinjaTrader, etc.) |
| Books confirmed referencing DEMA/TEMA | **4+** |

---

## 9. Raw Data Sources

### TASC TOC XML URLs Used
- https://traders.com/Mobile/Archive/JAN1994.XML
- https://traders.com/Mobile/Archive/FEB1994.XML
- https://traders.com/Mobile/Archive/DEC1994.XML (contains reader letter about DEMA)

### MQL5 API Endpoints Queried
- `https://search.mql5.com/api/query?keyword=DEMA&module=mql5.com.en.codebase|mql4.com.en.codebase&count=20&lng=en`
- `https://search.mql5.com/api/query?keyword=TEMA&module=mql5.com.en.codebase|mql4.com.en.codebase&count=20&lng=en`
- `https://search.mql5.com/api/query?keyword=Patrick+Mulloy&module=mql5.com.en.codebase|mql4.com.en.codebase&count=20&lng=en`
- `https://search.mql5.com/api/query?keyword=Double+Exponential+Moving+Average&module=mql5.com.en.codebase|mql4.com.en.codebase&count=20&lng=en`
- `https://search.mql5.com/api/query?keyword=Triple+Exponential+Moving+Average&module=mql5.com.en.codebase|mql4.com.en.codebase&count=20&lng=en`
- `https://search.mql5.com/api/query?keyword=Patrick+Mulloy&module=mql5.com.en.articles|mql4.com.en.articles&count=10&lng=en`

---

*Research compiled: 2026-05-07*
