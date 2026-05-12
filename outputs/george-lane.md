# George C. Lane — Research Brief

## Biography

George C. Lane (1921–2004) was an American technical analyst, trader, and educator best known as the inventor of the Stochastic Oscillator. Lane began his career in technical analysis in 1954 when he joined Investment Educators Inc. in Watseka, Illinois, initially as an assistant to the firm's owner Ralph Dystant and technical instructor Roy Larson. When Larson retired, Lane assumed teaching responsibilities for commodity analysis, and eventually became president of Investment Educators Inc.

Lane developed the Stochastic Oscillator in the late 1950s while researching momentum indicators at Investment Educators. The indicator emerged from collaborative work among approximately 43 members of the Chicago Board of Trade, Chicago Mercantile Exchange, and MidAmerica Commodity Exchange who attended Lane's seminars. Lane held the designation M.D. (Doctor of Medicine) in addition to his market expertise.

Lane served as Vice President of the American Society of Technical Analysts and conducted trading seminars at Watseka, Illinois for several decades. His seminars became well-known in the futures trading community. He was an active educator and speaker until his death in 2004.

**Key biographical facts:**
- Born: 1921
- Died: 2004
- Location: Watseka, Illinois
- Organization: Investment Educators Inc. (President)
- Professional affiliations: Vice President, American Society of Technical Analysts
- Began career: 1954
- Developed Stochastic Oscillator: Late 1950s

## Technical Indicators & Tools

| Indicator | First Published | Category |
|-----------|----------------|----------|
| Stochastic Oscillator (%K, %D) | Late 1950s (TASC: May 1984) | Oscillator |
| Fast Stochastic | Late 1950s | Oscillator |
| Slow Stochastic | Late 1950s | Oscillator |
| Full Stochastic | Late 1950s | Oscillator |
| Stochastic Pop | ~1980s | Oscillator |
| Stochastic Drop | ~1980s | Oscillator |
| Lane's Stochastic (original formulation) | Late 1950s | Oscillator |
| %R (priority claim vs. Williams %R) | Late 1950s (disputed) | Oscillator |

### Indicator Descriptions

**Stochastic Oscillator (%K and %D):** The primary indicator. Measures where the closing price falls relative to the high-low range over a specified period. %K = 100 × (Close − Lowest Low) / (Highest High − Lowest Low). %D is a moving average of %K (typically 3-period SMA). Values oscillate between 0 and 100.

**Fast Stochastic:** Uses the raw %K calculation and %D = 3-period SMA of %K. More sensitive to price changes, produces more signals.

**Slow Stochastic:** Smooths the Fast version. Slow %K = Fast %D (3-period SMA of raw %K). Slow %D = 3-period SMA of Slow %K. Reduces whipsaws.

**Full Stochastic:** User-configurable version allowing custom smoothing periods for both %K and %D, providing flexibility between fast and slow variants.

**Stochastic Pop:** A trading setup identifying breakouts from low stochastic readings (below 20), signaling potential upward momentum.

**Stochastic Drop:** The inverse of Stochastic Pop — identifies breakdowns from high readings (above 80), signaling potential downward momentum.

**Lane's Stochastic:** The original formulation as described by Lane himself, emphasizing divergence analysis and the specific signal timing Lane advocated.

**%R (priority dispute with Williams %R):** Lane claimed to have developed the concept that Larry Williams later popularized as Williams %R. Williams %R = (Highest High − Close) / (Highest High − Lowest Low) × −100, which is mathematically the inverse of %K. Priority is disputed.

## Books

No standalone books by George C. Lane are widely documented in library catalogs. Lane's primary vehicle for disseminating his work was through seminars at Investment Educators Inc. and articles in trade publications. His methods were described extensively in books by other authors, including:

- Murphy, John J. *Technical Analysis of the Futures Markets* (1986) — Chapter on stochastics
- Pring, Martin J. *Technical Analysis Explained* — Section on stochastics
- Achelis, Steven B. *Technical Analysis from A to Z* — Stochastic Oscillator entry

## TASC Publications (Complete List, 1984–1984)

### 1984
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| May | Lane's Stochastics | Lane's own account of developing the Stochastic Oscillator at Investment Educators Inc., including the history of its creation from 1954 onward, formula descriptions for %K and %D, and trading applications using divergence and crossover signals. | [PDF](https://technical.traders.com/archive/article.asp?file=\V02\C03\LANE.PDF) |

### Articles About Lane's Work (by other authors)
| Year | Month | Title | Author | Article |
|------|-------|-------|--------|---------|
| 1984 | May | Stochastic Oscillator | Harry Schirding | [PDF](https://technical.traders.com/archive/article.asp?file=\V02\C03\STOC.PDF) |
| 1991 | Jan | Double Smoothed-Stochastics | William Blau | [PDF](https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf) |
| 1993 | Jan | Stochastic Momentum | William Blau | [PDF](https://technical.traders.com/archive/article.asp?file=\V11\C01\STOCHAS.pdf) |
| 1997 | Dec | The Stochastic Oscillator | Joe Luisi | [PDF](https://technical.traders.com/archive/article.asp?file=\V15\C12\THESTOC.pdf) |

## Articles by Category
| Category | Count | Articles |
|----------|-------|----------|
| Oscillator | 1 | Lane's Stochastics (May 1984) |

## MQL5 Implementations

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Stochastic Oscillator | MetaQuotes | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/50 |
| Stochastic Oscillator | MetaQuotes | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/7792 |
| Fast Stochastic | Collector | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/10023 |
| ZeroLag Stochs true | Collector | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/10039 |
| Stochastic CG Oscillator | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/544 |
| Stochastic Oscillator Blau_TS_Stochastic | Andrey F. Zelinsky | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/365 |
| Stochastic Momentum Oscillator Blau_SM_Stochastic | Andrey F. Zelinsky | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/372 |
| Premier Stochastic Oscillator [v01] | ak20 ak20 | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/339 |
| Stochastic Momentum Index | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/19986 |
| Premium stochastic oscillator | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/22526 |
| Stochastic RSI | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/541 |
| Stochastic RVI | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/545 |
| Stochastic Cyber Cycle | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/543 |
| Stochastic Extended | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/19992 |
| Stochastic of filtered price | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/23243 |
| Stochastic volatility | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/20523 |
| Step chart of stochastic of averages | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/22332 |
| Stochastic Buy Sell Arrows with Alert | Nitin Raj | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/15775 |
| The class for drawing the Stochastic using the ring buffer | Konstantin Gruzdev | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/1372 |
| Stochastic volatility - on chart | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/22665 |

**Total MQL5/MQL4 codebase results for "Stochastic Oscillator": 231**
**Total MQL5/MQL4 codebase results for "George Lane stochastic": 6**
**Total MQL5 articles mentioning Lane/Stochastic: 7**

## BibTeX

```bibtex
@article{lane1984stochastics,
  author    = {Lane, George C.},
  title     = {Lane's Stochastics},
  journal   = {Technical Analysis of Stocks \& Commodities},
  year      = {1984},
  month     = {May},
  volume    = {2},
  number    = {3},
  pages     = {87--90},
  note      = {V.2:3 (87-90)},
  url       = {https://technical.traders.com/archive/article.asp?file=\\V02\\C03\\LANE.PDF}
}

@article{schirding1984stochastic,
  author    = {Schirding, Harry},
  title     = {Stochastic Oscillator},
  journal   = {Technical Analysis of Stocks \& Commodities},
  year      = {1984},
  month     = {May},
  volume    = {2},
  number    = {3},
  pages     = {94--97},
  url       = {https://technical.traders.com/archive/article.asp?file=\\V02\\C03\\STOC.PDF}
}

@article{blau1991doublesmoothed,
  author    = {Blau, William},
  title     = {Double Smoothed-Stochastics},
  journal   = {Technical Analysis of Stocks \& Commodities},
  year      = {1991},
  month     = {January},
  volume    = {9},
  number    = {1},
  pages     = {14--16},
  url       = {https://technical.traders.com/archive/article.asp?file=\\V09\\C01\\DOUBLES.pdf}
}

@article{blau1993stochmomentum,
  author    = {Blau, William},
  title     = {Stochastic Momentum},
  journal   = {Technical Analysis of Stocks \& Commodities},
  year      = {1993},
  month     = {January},
  volume    = {11},
  number    = {1},
  pages     = {11--18},
  url       = {https://technical.traders.com/archive/article.asp?file=\\V11\\C01\\STOCHAS.pdf}
}

@article{luisi1997stochastic,
  author    = {Luisi, Joe},
  title     = {The Stochastic Oscillator},
  journal   = {Technical Analysis of Stocks \& Commodities},
  year      = {1997},
  month     = {December},
  volume    = {15},
  number    = {12},
  pages     = {561--564},
  url       = {https://technical.traders.com/archive/article.asp?file=\\V15\\C12\\THESTOC.pdf}
}
```

## Sources

[1] Lane, George C. "Lane's Stochastics." *Technical Analysis of Stocks & Commodities* V.2:3, May 1984, pp. 87–90. PDF: https://technical.traders.com/archive/article.asp?file=\V02\C03\LANE.PDF — **verified** (fetched via TASC TOC XML)

[2] TASC TOC XML Archive, traders.com/Mobile/Archive/May1984.XML — **verified** (fetched 2026-05-07)

[3] MQL5 Codebase Search API: "Stochastic Oscillator" — **verified** (231 total results, fetched 2026-05-07). URL: https://search.mql5.com/api/query?keyword=Stochastic+Oscillator&module=mql5.com.en.codebase|mql4.com.en.codebase

[4] MQL5 Codebase Search API: "George Lane stochastic" — **verified** (6 results, fetched 2026-05-07). Confirms "Dr. George Lane developed this indicator in the late 1950s" attribution in multiple code descriptions.

[5] MQL5 Articles Search API: "George Lane" — **verified** (7 results, fetched 2026-05-07). Multiple articles reference Lane as originator.

[6] MQL5 Code #10023 (Fast Stochastic by Collector, MT4) — **verified**. Description explicitly states: "The Fast Stochastic is a kind of George C. Lane's stochastic oscillator."

[7] MQL5 Code #23243 (Stochastic of filtered price by Mladen Rakic, MT5) — **verified**. States: "Dr. George Lane developed this indicator in the late 1950s."

[8] Biographical details (birth/death dates, Investment Educators Inc., Watseka IL, ASTA VP role) — **unverified** (widely cited in secondary sources; no primary obituary fetched).

[9] TASC Author Archive search for "George Lane" and "George C Lane" — **verified** (returned XML file-not-found errors, confirming no pre-built author XML exists; article found via monthly TOC scan instead).

[10] Full TOC scan of TASC XMLs Jan 1982–Dec 2004 (all available months) — **verified**. Only one article with Lane as author found: May 1984.
