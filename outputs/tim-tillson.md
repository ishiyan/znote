# Tim Tillson — Research Brief

## Biography

Tim Tillson (possibly Timothy Tillson) is the creator of the T3 Moving Average. He published a single article in *Technical Analysis of Stocks & Commodities* magazine in January 1998. Based on that article's technical sophistication — DSP concepts, generalized exponential smoothing, mathematical derivation, and included code — Tillson appears to have had a background in signal processing, mathematics or quantitative finance, and software development.

No affiliations (company, university, or trading firm) are documented publicly. No further publications, conference appearances, interviews, or media presence have been found. Like Patrick Mulloy (creator of DEMA/TEMA), Tillson published one seminal article and left virtually no public biographical footprint.

---

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| T3 (Tillson T3 Moving Average) | TASC Jan 1998, [\V16\C01\005SMO](https://technical.traders.com/archive/article.asp?file=\V16\C01\005SMO.pdf) | Adaptive MA / Low-pass Filter |

### T3 — Technical Description

**Formula:**

Generalized Double EMA (GD):
```
GD(x, v) = EMA(x) × (1 + v) − EMA(EMA(x)) × v
```

T3 = Triple application of GD:
```
T3 = GD(GD(GD(price, v), v), v)
```

Expanded form (6 EMAs):
```
EMA1 = EMA(Price, period)
EMA2 = EMA(EMA1, period)
EMA3 = EMA(EMA2, period)
EMA4 = EMA(EMA3, period)
EMA5 = EMA(EMA4, period)
EMA6 = EMA(EMA5, period)

c1 = −v³
c2 = 3v² + 3v³
c3 = −6v² − 3v − 3v³
c4 = 1 + 3v + v³ + 3v²

T3 = c1×EMA6 + c2×EMA5 + c3×EMA4 + c4×EMA3
```

**Default parameters:** period=5, volume factor v=0.7

**Key properties:**
- v=0 → Triple EMA (no DEMA component)
- v=1 → Triple DEMA (Mulloy's DEMA applied three times)
- v=0.7 → **T3** (Tillson's recommendation — balance of smoothness and responsiveness)
- Builds on Mulloy's DEMA/TEMA (TASC Jan–Feb 1994)
- Smoother than DEMA/TEMA with lower lag than simple triple EMA
- Acts as a low-pass filter with steeper rolloff than traditional MAs
- Can overshoot price (unlike simple averages) due to v > 0
- Uses 6 internal EMAs but only 2 user parameters (period, v)

**Fulks/Matulich modification (April 2003):** Bob Fulks and Alex Matulich modified the T3 calculation to reduce overshoot and improve response. Commonly offered as a toggle in MetaTrader implementations.

---

## Books

No known books authored by Tim Tillson.

### External Books Referencing T3

| # | Title | Author | Year | Publisher | ISBN | Link |
|---|-------|--------|------|-----------|------|------|
| 1 | Trading Systems and Methods (5th ed.) | Perry J. Kaufman | 2013 | Wiley | — | [Google Books](https://books.google.com/books?id=eFDIBQAAQBAJ) |
| 2 | Encyclopedia of Technical Market Indicators (2nd ed.) | Robert W. Colby | 2003 | McGraw-Hill | 978-0070120570 | [Google Books](https://books.google.com/books?id=ARkL2dJVYBwC) |
| 3 | Technical Analysis: The Complete Resource for Financial Market Technicians (2nd ed.) | Charles D. Kirkpatrick & Julie R. Dahlquist | 2010 | FT Press | 978-0137059447 | — |

---

## TASC Publications (Complete List)

### 1998

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Jan | Smoothing Techniques For More Accurate Signals | Introduces T3 Moving Average — a generalized triple-smoothed EMA with a single volume factor parameter, providing superior smoothing with reduced lag | [\V16\C01\005SMO](https://technical.traders.com/archive/article.asp?file=\V16\C01\005SMO.pdf) |

**Total TASC articles: 1**

---

## Articles by Category

| Category | Count | Articles |
|----------|-------|----------|
| Adaptive MA / Filters | 1 | Smoothing Techniques For More Accurate Signals (Jan 1998) |

---

## Photos, Videos & Interviews

### Photos

| Description | URL | Source |
|-------------|-----|--------|
| [URL not found] No known photos | — | Exhaustive search |

### Videos

| Title | URL | Duration | Date |
|-------|-----|----------|------|
| [URL not found] No known videos | — | — | — |

### Interviews

None found outside the TASC article itself.

---

## Forum Discussions

| Forum | T3/Tillson Content |
|-------|-------------------|
| MQL5 Codebase | **Confirmed** — 156+ implementations, 90+ referencing Tillson by name |
| TradingView | **Confirmed** — Multiple Pine Script community scripts |
| ForexFactory | Expected (major indicator discussion forum) |
| futures.io | Expected |
| EliteTrader | Expected |
| NinjaTrader Forum | Expected |
| Reddit r/algotrading | Expected |
| Trade2Win | Expected |

---

## MQL5 Implementations

Top 20 dedicated T3 indicators from 156 total codebase results:

| Title | Author | Platform | URL |
|-------|--------|----------|-----|
| Tillson T3 | Vladislav Boyko | MT5 | https://www.mql5.com/en/code/66616 |
| T3 Moving Average | Salman Soltaniyan | MT5 | https://www.mql5.com/en/code/56927 |
| T3 | Scriptor | MT5 | https://www.mql5.com/en/code/21842 |
| T3 | Nikolay Kositsin | MT5 | https://www.mql5.com/en/code/424 |
| T3_MA | Scriptor | MT5 | https://www.mql5.com/en/code/20373 |
| T3 floating levels | Mladen Rakic | MT5 | https://www.mql5.com/en/code/16696 |
| T3 floating levels oscillator | Mladen Rakic | MT5 | https://www.mql5.com/en/code/16697 |
| T3 Deviation | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20695 |
| T3 Velocity | Mladen Rakic | MT5 | https://www.mql5.com/en/code/16765 |
| T3 Velocity V.2.0 | Mladen Rakic | MT5 | https://www.mql5.com/en/code/16838 |
| Zero lag T3 | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20684 |
| T3 stripped | Mladen Rakic | MT5 | https://www.mql5.com/en/code/22444 |
| Stripped T3 levels | Mladen Rakic | MT5 | https://www.mql5.com/en/code/22941 |
| Corrected T3 | Mladen Rakic | MT5 | https://www.mql5.com/en/code/22019 |
| ATR adaptive T3 | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21894 |
| Multi T3 Slopes | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21600 |
| RSI - of adaptive T3 | Mladen Rakic | MT5 | https://www.mql5.com/en/code/17059 |
| CCI T3 Based | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21253 |
| CCI T3 Tick | Alexey Topounov | MT5 | https://www.mql5.com/en/code/940 |
| Module of Trade Signals, Based on T3 Indicator | Aleksey Sergan | MT5 | https://www.mql5.com/en/code/447 |

---

## Community & Reference Implementations

| Platform/Library | Function | Status |
|-----------------|----------|--------|
| TA-Lib | `TA_T3()` — params: period, vFactor (default 0.7) | Built-in |
| pandas-ta | `df.ta.t3()` — params: length, a (volume factor) | Built-in |
| TradingView | Community Pine Scripts (search "T3 Tillson") | Community |
| MetaTrader 4/5 | 156+ custom indicators in MQL5 codebase | Community |
| NinjaTrader | Custom community indicators | Community |

---

## BibTeX

```bibtex
@article{tasc:tillson1998t3,
  author  = {Tillson, Tim},
  title   = {Smoothing Techniques For More Accurate Signals},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1998},
  month   = jan,
  volume  = {16},
  number  = {1},
  pages   = {33--37},
  url     = {https://technical.traders.com/archive/article.asp?file=\V16\C01\005SMO.pdf}
}

@book{kaufman2013systems,
  author    = {Kaufman, Perry J.},
  title     = {Trading Systems and Methods},
  edition   = {5},
  year      = {2013},
  publisher = {Wiley},
  url       = {https://books.google.com/books?id=eFDIBQAAQBAJ}
}

@book{colby2003encyclopedia,
  author    = {Colby, Robert W.},
  title     = {Encyclopedia of Technical Market Indicators},
  edition   = {2},
  year      = {2003},
  publisher = {McGraw-Hill},
  isbn      = {978-0070120570},
  url       = {https://books.google.com/books?id=ARkL2dJVYBwC}
}

@book{kirkpatrick2010technical,
  author    = {Kirkpatrick, Charles D. and Dahlquist, Julie R.},
  title     = {Technical Analysis: The Complete Resource for Financial Market Technicians},
  edition   = {2},
  year      = {2010},
  publisher = {FT Press},
  isbn      = {978-0137059447}
}
```

---

## Sources

[1] TASC Author Archive: http://technical.traders.com/archive/combo/display5.asp?author=Tim%20Tillson  
[2] TASC TOC XML (Jan 1998): https://traders.com/Mobile/Archive/JAN1998.XML  
[3] TASC Article PDF: https://technical.traders.com/archive/article.asp?file=\V16\C01\005SMO.pdf  
[4] TASC Store link: https://traderscom.stores.yahoo.net/-v16-c01-005smo-pdf.html  
[5] MQL5 Codebase search "T3": https://www.mql5.com/en/code  
[6] MQL5 Codebase search "Tillson": https://www.mql5.com/en/code  
[7] TA-Lib function reference: TA_T3  
[8] pandas-ta documentation  
[9] Google Books — Kaufman: https://books.google.com/books?id=eFDIBQAAQBAJ  
[10] Google Books — Colby: https://books.google.com/books?id=ARkL2dJVYBwC  
[11] TradingView community scripts  
[12] TASC Author Archive "Timothy Tillson" (no additional results)  
[13] TASC TOC XMLs 1996–2002 (scanned, no other Tillson entries)  
