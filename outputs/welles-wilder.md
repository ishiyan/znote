# J. Welles Wilder Jr. — Research Brief

**Date:** 2026-05-07  
**Status:** Final

---

## Biography

John Welles Wilder Jr. (June 11, 1935 – April 18, 2021) was an American mechanical engineer and real estate developer who became the most influential technical analyst of the twentieth century. Born in Norris, Tennessee, he served in the U.S. Navy during the Korean War before earning a B.S. in Mechanical Engineering from North Carolina State University in 1962. After a successful career in real estate development in Greensboro, North Carolina, Wilder turned to commodity trading and technical analysis.

In 1978, he published *New Concepts in Technical Trading Systems*, a book that introduced seven indicators — RSI, ATR, ADX/DMI, Parabolic SAR, Swing Index, Commodity Selection Index, and Wilder's Smoothing — that became the universal foundation of computerized technical analysis. Every trading platform built since has incorporated his indicators as built-in functions, an achievement unmatched by any other technical analyst.

**Forbes** (October 1980) called him "the premier technical trader publishing his work today." **Barron's** (July 1984) credited his 1978 work with expanding mathematical analysis into the field. **Financial World** (July 1985) stated he "developed more accurate commodity trading systems and concepts than any other expert."

Wilder subsequently published *The Adam Theory of Markets* (1987), proposing that markets are perfectly efficient reflectors requiring traders to follow rather than predict, and *The Delta Phenomenon* (1991), which posited a hidden cyclic order across five time frames with a 19-year longest cycle. He also published *The Wisdom of the Ages in Acquiring Wealth* (1989).

He operated Trend Research LTD in Greensboro, NC, and later Delta Society International. In October 1999, he relocated to Christchurch, New Zealand, where he continued system development. He died there on April 18, 2021, of vascular dementia/Alzheimer's disease, aged 85.

**Family:** Wife Eleanor Dawn Barefoot (m. 1958); children John III, Catharine, and David. His brother Albert "Bert" Wilder (1939–2012) was an NFL player.

### Famous Quotes
1. "Letting your emotions override your plan or system is the biggest cause of failure."
2. "Some traders are born with an innate discipline. Most have to learn it the hard way."
3. "If you can't deal with emotion, get out of trading."

---

## Technical Indicators & Tools

### Core Indicators (All from *New Concepts in Technical Trading Systems*, 1978)

| Indicator | Category |
|-----------|----------|
| RSI (Relative Strength Index) | Oscillator |
| ATR (Average True Range) | Filter |
| ADX / DMI (Directional Movement Index) | Trend |
| Parabolic SAR (Stop and Reverse) | Strategy |
| Swing Index / ASI (Accumulative Swing Index) | Oscillator |
| Commodity Selection Index (CSI) | Filter |
| Wilder's Smoothing | Filter |

---

### Indicator Formulas

#### RSI (Relative Strength Index)
- **Default period:** 14
- **Step 1 — First Average:**
  - Average Gain₁ = Sum of gains over N periods / N
  - Average Loss₁ = Sum of losses over N periods / N
- **Step 2 — Subsequent (Wilder smoothing):**
  - Average Gain = (Previous Average Gain × (N−1) + Current Gain) / N
  - Average Loss = (Previous Average Loss × (N−1) + Current Loss) / N
- **Step 3:**
  - RS = Average Gain / Average Loss
  - **RSI = 100 − 100 / (1 + RS)**
- Range: 0–100. Overbought ≥ 70, Oversold ≤ 30.

#### ATR (Average True Range)
- **Default period:** 14 (Wilder originally used 7)
- **True Range:**
  - TR = max(High − Low, |High − Close₋₁|, |Low − Close₋₁|)
- **First ATR:** Simple average of first N True Range values
- **Subsequent:**
  - **ATR = (Previous ATR × (N−1) + Current TR) / N**

#### ADX / DMI (Directional Movement Index)
- **Default period:** 14
- **Directional Movement:**
  - +DM = High − High₋₁ (if > L₋₁ − Low AND > 0, else 0)
  - −DM = Low₋₁ − Low (if > High − H₋₁ AND > 0, else 0)
- **Smoothed DM:** Wilder smoothing over N periods
- **Directional Indicators:**
  - +DI = 100 × Smoothed(+DM) / ATR
  - −DI = 100 × Smoothed(−DM) / ATR
- **Directional Index:**
  - DX = 100 × |+DI − −DI| / (+DI + −DI)
- **Average Directional Index:**
  - **ADX = Wilder smoothing of DX over N periods**
- ADXR = (ADX + ADX₋ₙ) / 2

#### Parabolic SAR (Stop and Reverse)
- **SAR(t+1) = SAR(t) + AF × (EP − SAR(t))**
- AF (Acceleration Factor): starts at 0.02, increments by 0.02 each time EP is updated, maximum 0.20
- EP (Extreme Point): highest high in uptrend, lowest low in downtrend
- Reversal: when price crosses SAR, reverse position and reset AF to 0.02

#### Swing Index (SI) / Accumulative Swing Index (ASI)
- **SI = 50 × (Cy − C + 0.5(Cy − Oy) + 0.25(C − O)) / R × K / T**
  - Where: Cy = yesterday's close, Oy = yesterday's open, C = today's close, O = today's open
  - R = largest of: |H−Cy|, |L−Cy|, |H−L| (with adjustments)
  - K = max(|H−Cy|, |L−Cy|)
  - T = limit move (maximum daily price change)
- **ASI = cumulative sum of SI values**

#### Commodity Selection Index (CSI)
- **CSI = ADXR × ATR₁₄ × V × (√(Margin Requirement) / (150 + Commission))**
  - V = value of a 1-cent move (contract point value)
- Ranks commodities by directional movement AND volatility to identify most tradable markets

#### Wilder's Smoothing Method
- **New Average = (Previous Average × (N−1) + Current Value) / N**
- Equivalent to: EMA with period **(2N − 1)**
  - Wilder 14-period smoothing ≈ EMA(27)
  - Wilder 7-period smoothing ≈ EMA(13)
- Also known as: SMMA (Smoothed Moving Average), RMA (TradingView), Wilder's Moving Average
- Used internally by RSI, ATR, ADX, and CSI calculations

---

### Indicators Introduced in Books

#### New Concepts in Technical Trading Systems (1978)

| Indicator | Chapter | Category |
|-----------|---------|----------|
| Relative Strength Index (RSI) | Ch. 5 | Oscillator |
| Average True Range (ATR) | Ch. 2 | Volatility Filter |
| Directional Movement Index (+DI/−DI/ADX) | Ch. 3 | Trend |
| Parabolic Time/Price System (SAR) | Ch. 1 | Strategy |
| Swing Index / Accumulative Swing Index | Ch. 6 | Oscillator |
| Commodity Selection Index (CSI) | Ch. 4 | Filter |
| Wilder's Smoothing Method | Throughout | Smoothing |
| Reaction Trend System | Ch. 7 | Strategy |
| Directional Movement Rating (ADXR) | Ch. 3 | Trend |

#### The Adam Theory of Markets (1987)

| Concept | Category |
|---------|----------|
| Adam Theory (market as perfect reflector) | Philosophy |
| Second reflection (symmetry projection) | Forecasting |
| Following vs. predicting markets | Strategy |

#### The Delta Phenomenon (1991)

| Concept | Category |
|---------|----------|
| Delta turning points (5 time frames) | Cycle analysis |
| Super Long Term Delta (19-year cycle) | Cycle |
| Long Term Delta | Cycle |
| Intermediate Term Delta | Cycle |
| Short Term Delta | Cycle |
| Intraday Delta | Cycle |

---

## Books

| # | Title | Author | Year | Publisher | ISBN | Link |
|---|-------|--------|------|-----------|------|------|
| 1 | New Concepts in Technical Trading Systems | Wilder, J. Welles | 1978 | Trend Research | 978-0-89459-027-6 | [Google Books](https://books.google.com/books?id=WesJAQAAMAAJ) |
| 2 | The Adam Theory of Markets or What Matters Is Profit | Wilder, J. Welles | 1987 | Trend Research | 978-9997619730 | — |
| 3 | The Wisdom of the Ages in Acquiring Wealth | Wilder, J. Welles | 1989 | Cavida | 978-0974645803 | — |
| 4 | The Delta Phenomenon, Or, The Hidden Order in All Markets | Wilder, J. Welles | 1991 | Delta Society International | 978-9992823262 | — |
| 5 | Technical Analysis of the Financial Markets | Murphy, John J. | 1999 | New York Institute of Finance | 978-0735200661 | [Google Books](https://books.google.com/books?id=5zhXEAAAQBAJ) |
| 6 | Technical Analysis from A to Z (2nd ed.) | Achelis, Steven B. | 2001 | McGraw-Hill | 978-0071363488 | [Google Books](https://books.google.com/books?id=KRkNAQAAMAAJ) |
| 7 | Trading Systems and Methods (5th ed.) | Kaufman, Perry J. | 2013 | Wiley | 978-1118043561 | [Google Books](https://books.google.com/books?id=86TZCwAAQBAJ) |
| 8 | Technical Analysis: Power Tools for Active Investors | Appel, Gerald | 2005 | FT Press | 978-0131479029 | [Google Books](https://books.google.com/books?id=RFYIAAAACAAJ) |

---

## TASC Publications (Complete List)

Wilder never authored articles for *Technical Analysis of Stocks & Commodities* — his book predates the magazine (1978 vs. 1982 launch). One interview exists:

### 2009

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Mar | Surviving The Test Of Time: J. Welles Wilder | Interview by Brian Twomey covering biography, Delta Phenomenon theory, and continued system development from New Zealand | [\V27\C03\123WILD](https://technical.traders.com/archive/article.asp?file=\V27\C03\123WILD.pdf) |

---

## Photos, Videos & Interviews

### Photos

| Description | URL | Source |
|-------------|-----|--------|
| Portrait photograph | https://upload.wikimedia.org/wikipedia/commons/e/ef/Welles_Wilder.jpg | Wikimedia Commons |

### Videos

| Title | URL | Duration | Date |
|-------|-----|----------|------|
| [No confirmed video interviews located] | — | — | — |

### Interviews

| Title | URL | Host/Publication | Date |
|-------|-----|-----------------|------|
| Surviving The Test Of Time: J. Welles Wilder | http://traders.com/Documentation/FEEDbk_docs/2009/03/Interview.html | TASC (Brian Twomey) | March 2009 |

### Other Media

| Type | Description | URL |
|------|-------------|-----|
| Obituary | Greensboro News & Record via Legacy.com | https://www.legacy.com/us/obituaries/greensboro/name/welles-wilder-obituary?id=53397461 |
| Blog | "Welles Wilder - Father of RSI & SAR" | https://thebestbusinessintheworld.blogspot.com/2010/05/welles-wilder-father-of-rsi-sar.html |

---

## Forum Discussions

**Note:** Google search was blocked by CAPTCHA during research. MQL5 forum search via API confirmed **232 threads** referencing "Welles Wilder."

### MQL5 Forum (232 threads)

| # | Thread Title | URL |
|---|-------------|-----|
| 1 | ADX Welles Wilder Classic Version | https://www.mql5.com/en/forum/465728 |
| 2 | Everything about RSI | https://www.mql5.com/en/forum/178733 |
| 3 | Looking for good explanation of smoothing and weighting | https://www.mql5.com/en/forum/157443 |
| 4 | EA using ATR and ADX | https://www.mql5.com/en/forum/179132 |
| 5 | Requests & Ideas (Wilder indicators) | https://www.mql5.com/en/forum/179807 |
| 6 | Need help with EMA for LinearRegression formula | https://www.mql5.com/en/forum/481490 |
| 7 | Moving Average of custom indicator | https://www.mql5.com/en/forum/455053 |
| 8 | Strategic Tips on Milking Major Currency Pairs | https://www.mql5.com/en/forum/178812 |
| 9 | Elite indicators | https://www.mql5.com/en/forum/175037 |
| 10 | Indicators with alerts/signal | https://www.mql5.com/en/forum/180648 |

### Other Forums (Known Activity)

- **ForexFactory:** Extensive threads on "Wilder's RSI vs Cutler's RSI", "ADX Trading Systems" (100+ pages), "Parabolic SAR Trading Method"
- **futures.io:** Wilder's Volatility System, ATR-based position sizing, ADX filter implementations (NinjaTrader)
- **EliteTrader:** Book reviews of *New Concepts*, RSI divergence strategies
- **TradingView:** Hundreds of Pine Script implementations tagged "Wilder"
- **Quant StackExchange:** Discussions on Wilder smoothing equivalence, RSI calculation methods
- **Reddit r/algotrading:** RSI implementation correctness, Wilder smoothing vs SMA, backtesting original systems
- **Trade2Win:** Parabolic Time/Price System and Reaction Trend System discussions

---

## MQL5 Implementations

**Total MQL4/MQL5 codebase entries referencing Wilder indicators: ~476** (with overlap across categories; estimated 300+ unique implementations).

### RSI Implementations (137 total)

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Relative Strength Index (RSI) | MetaQuotes | MT5 | Built-in | https://www.mql5.com/en/code/47 |
| Relative Strength Index (RSI) | MetaQuotes | MT4 | Built-in | https://www.mql5.com/en/code/7898 |
| Relative Strength Index | MetaQuotes | MT4 | Alternate | https://www.mql5.com/en/code/7677 |
| **Wilder's Relative Strength Index** | **Fernando Carreiro (FMIC)** | **MT5** | **Faithful to book** | https://www.mql5.com/en/code/42414 |
| **Wilder's Relative Strength Index** | **Fernando Carreiro (FMIC)** | **MT4** | **Faithful to book** | https://www.mql5.com/en/code/42413 |
| MTF Relative Strength Index | Rafal Dubiel | MT4 | Multi-timeframe | https://www.mql5.com/en/code/8948 |
| Non Lag Relative Strength Index | Roberto Jacobs | MT5 | Lag-reduced | https://www.mql5.com/en/code/28577 |
| Non Lag Relative Strength Index | Roberto Jacobs | MT4 | Lag-reduced | https://www.mql5.com/en/code/28576 |
| Figurelli RSI | Rogerio Figurelli | MT4 | Gain-adjusted | https://www.mql5.com/en/code/10539 |
| MQL5 Wizard MA RSI | Vladimir Karputov | MT5 | EA (MA + RSI) | https://www.mql5.com/en/code/17489 |

### ATR Implementations (121 total)

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Average True Range (ATR) | MetaQuotes | MT5 | Built-in | https://www.mql5.com/en/code/12 |
| Average True Range, ATR | MetaQuotes | MT4 | Built-in | https://www.mql5.com/en/code/7807 |
| **Wilder's Average True Range (ATR)** | **Fernando Carreiro (FMIC)** | **MT5** | **Faithful to book (SMMA, period 7)** | https://www.mql5.com/en/code/42408 |
| **Wilder's Average True Range (ATR)** | **Fernando Carreiro (FMIC)** | **MT4** | **Faithful to book (SMMA, period 7)** | https://www.mql5.com/en/code/42407 |
| ATR class using ring buffer | Konstantin Gruzdev (Lizar) | MT5 | OOP | https://www.mql5.com/en/code/1344 |
| Average Day Range | Artyom Trishkin | MT5 | ADR vs ATR | https://www.mql5.com/en/code/49013 |

### ADX Implementations (39 total)

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Average Directional Movement Index (ADX) | MetaQuotes | MT5 | Built-in (EMA-based) | https://www.mql5.com/en/code/7 |
| **Average Directional Movement Index Wilder** | **MetaQuotes** | **MT5** | **Built-in (SMMA, faithful)** | https://www.mql5.com/en/code/8 |
| Average Directional Movement Index, ADX | MetaQuotes | MT4 | Built-in | https://www.mql5.com/en/code/7955 |
| ADX class using ring buffer | Konstantin Gruzdev (Lizar) | MT5 | OOP | https://www.mql5.com/en/code/1343 |
| ADX Wilder class using ring buffer | Konstantin Gruzdev (Lizar) | MT5 | OOP, Wilder smoothing | https://www.mql5.com/en/code/1356 |
| ADMIR (ADX Rating) | Scriptor | MT5 | Dual-period ADX ratio | https://www.mql5.com/en/code/20910 |

### Parabolic SAR Implementations (102 total)

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Parabolic SAR | MetaQuotes | MT5 | Built-in | https://www.mql5.com/en/code/43 |
| Parabolic SAR | MetaQuotes | MT4 | Built-in | https://www.mql5.com/en/code/7787 |
| Parabolic SAR, Parabolic | MetaQuotes | MT4 | Built-in (alternate) | https://www.mql5.com/en/code/7892 |
| Color Parabolic SAR | Вадим (Rinng) | MT5 | Color-coded | https://www.mql5.com/en/code/90 |
| PZ Parabolic SAR EA | Point Zero (Arturo Lopez) | MT4 | EA with dual PSAR | https://www.mql5.com/en/code/10957 |
| MQL5 Wizard MACD Parabolic SAR | Vladimir Karputov | MT5 | Wizard EA | https://www.mql5.com/en/code/17357 |

### Swing Index Implementations (26 total)

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Accumulation Swing Index (ASI) | MetaQuotes | MT5 | Built-in | https://www.mql5.com/en/code/11 |
| Accumulative Swing Index - ASI | MetaQuotes | MT4 | Built-in | https://www.mql5.com/en/code/7057 |
| Accumulative Swing Index - ASI | Nikolay Kositsin | MT5 | Enhanced | https://www.mql5.com/en/code/6974 |
| Swing Index | Nikolay Kositsin | MT5 | Single-bar SI | https://www.mql5.com/en/code/513 |
| Accumulative Swing Index Smoothed | Mladen Rakic | MT5 | JMA-smoothed | https://www.mql5.com/en/code/21518 |
| ASI Smoothed - Floating Levels | Mladen Rakic | MT5 | Adaptive levels | https://www.mql5.com/en/code/21520 |

### Faithful-to-Book Implementations (Fernando Carreiro / FMIC)

Fernando Carreiro's MQL5 CodeBase contributions are explicitly faithful to Wilder's 1978 book. They correct MetaTrader's built-in indicators, which use SMA or EMA where Wilder specified SMMA (his proprietary smoothing). Key corrections:

| Indicator | MT Built-in Issue | FMIC Correction | MT5 URL | MT4 URL |
|-----------|------------------|-----------------|---------|---------|
| RSI | Uses SMA for initial average | Uses SMMA throughout | https://www.mql5.com/en/code/42414 | https://www.mql5.com/en/code/42413 |
| ATR | Uses SMA smoothing, period 14 | Uses SMMA, period 7 (as in book) | https://www.mql5.com/en/code/42408 | https://www.mql5.com/en/code/42407 |

### Other Named "Welles Wilder" Implementations (51 total)

| Title | Author | Platform | URL |
|-------|--------|----------|-----|
| Wilder's Volatility System | Walter (brother3th) | MT4 | https://www.mql5.com/en/code/9983 |

---

## Community & Reference Implementations

| Platform/Library | Functions | Status |
|-----------------|-----------|--------|
| TA-Lib | TA_RSI(), TA_ATR(), TA_ADX(), TA_PLUS_DI(), TA_MINUS_DI(), TA_SAR(), TA_TRANGE(), TA_ADXR(), TA_DX() | Built-in |
| MetaTrader 4/5 | iRSI(), iATR(), iADX(), iSAR(); ADX Wilder (MT5 only) | Built-in |
| TradingView | ta.rsi(), ta.atr(), ta.dmi(), ta.sar(), ta.rma() (= Wilder smoothing) | Built-in |
| pandas-ta | rsi(), atr(), adx(), psar() | Built-in |
| Bloomberg Terminal | RSI, ATR, ADX, PSAR | Built-in |
| NinjaTrader | RSI, ATR, ADX, ParabolicSAR | Built-in |
| TradeStation | RSI, ATR, ADX, SAR (EasyLanguage) | Built-in |
| AmiBroker | RSI(), ATR(), ADX(), SAR() (AFL) | Built-in |
| Thinkorswim | RSI, ATR, ADX, ParabolicSAR (thinkScript) | Built-in |
| QuantConnect (LEAN) | RSI, ATR, ADX, PSAR (C#/Python) | Built-in |
| Backtrader (Python) | RSI, ATR, ADX, PSAR | Built-in |
| Zipline (Python) | Via TA-Lib integration | Available |

---

## BibTeX

```bibtex
@book{wilder1978,
  author    = {Wilder, J. Welles},
  title     = {New Concepts in Technical Trading Systems},
  year      = {1978},
  publisher = {Trend Research},
  address   = {Greensboro, NC},
  isbn      = {978-0-89459-027-6}
}

@book{wilder1987,
  author    = {Wilder, J. Welles},
  title     = {The Adam Theory of Markets or What Matters Is Profit},
  year      = {1987},
  publisher = {Trend Research},
  address   = {Greensboro, NC},
  isbn      = {978-9997619730}
}

@book{wilder1989,
  author    = {Wilder, J. Welles},
  title     = {The Wisdom of the Ages in Acquiring Wealth},
  year      = {1989},
  publisher = {Cavida},
  isbn      = {978-0974645803}
}

@book{wilder1991,
  author    = {Wilder, J. Welles},
  title     = {The Delta Phenomenon, Or, The Hidden Order in All Markets},
  year      = {1991},
  publisher = {Delta Society International},
  isbn      = {978-9992823262}
}

@article{twomey2009,
  author  = {Twomey, Brian},
  title   = {Surviving The Test Of Time: {J. Welles Wilder}},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {2009},
  volume  = {27},
  number  = {3},
  month   = mar,
  note    = {Interview}
}

@book{murphy1999,
  author    = {Murphy, John J.},
  title     = {Technical Analysis of the Financial Markets},
  year      = {1999},
  publisher = {New York Institute of Finance},
  isbn      = {978-0735200661}
}

@book{achelis2001,
  author    = {Achelis, Steven B.},
  title     = {Technical Analysis from {A} to {Z}},
  edition   = {2},
  year      = {2001},
  publisher = {McGraw-Hill},
  isbn      = {978-0071363488}
}

@book{kaufman2013,
  author    = {Kaufman, Perry J.},
  title     = {Trading Systems and Methods},
  edition   = {5},
  year      = {2013},
  publisher = {Wiley},
  isbn      = {978-1118043561}
}

@book{appel2005,
  author    = {Appel, Gerald},
  title     = {Technical Analysis: Power Tools for Active Investors},
  year      = {2005},
  publisher = {FT Press},
  isbn      = {978-0131479029}
}

@online{wilder_photo,
  title        = {Welles Wilder portrait},
  url          = {https://upload.wikimedia.org/wikipedia/commons/e/ef/Welles_Wilder.jpg},
  urldate      = {2026-05-07},
  note         = {Wikimedia Commons}
}

@online{wilder_obituary,
  title        = {Welles Wilder Obituary},
  url          = {https://www.legacy.com/us/obituaries/greensboro/name/welles-wilder-obituary?id=53397461},
  urldate      = {2026-05-07},
  note         = {Greensboro News \& Record via Legacy.com}
}
```

---

## Sources

[1] Wikipedia. "J. Welles Wilder Jr." https://en.wikipedia.org/wiki/J._Welles_Wilder_Jr.

[2] Wilder, J. W. (1978). *New Concepts in Technical Trading Systems*. Trend Research. ISBN 978-0-89459-027-6.

[3] Twomey, B. (2009). "Surviving The Test Of Time: J. Welles Wilder." *Technical Analysis of Stocks & Commodities*, 27(3). http://traders.com/Documentation/FEEDbk_docs/2009/03/Interview.html

[4] TASC Archive. http://technical.traders.com/archive/combo/display5.asp

[5] MQL5 CodeBase. https://www.mql5.com/en/code

[6] MQL5 Forum. https://www.mql5.com/en/forum (232 threads referencing "Welles Wilder")

[7] Wikimedia Commons. Portrait photograph. https://upload.wikimedia.org/wikipedia/commons/e/ef/Welles_Wilder.jpg

[8] Legacy.com. Obituary. https://www.legacy.com/us/obituaries/greensboro/name/welles-wilder-obituary?id=53397461

[9] Internet Archive. *New Concepts in Technical Trading Systems*. https://archive.org/details/newconceptsintec00wild

[10] Fernando Carreiro (FMIC). Faithful Wilder implementations on MQL5 CodeBase. https://www.mql5.com/en/code/42414
