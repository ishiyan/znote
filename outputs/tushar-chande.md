# Tushar Chande — Research Brief

## Biography

Tushar S. Chande, PhD, is an Indian-American engineer and technical analyst who transitioned from academic research into quantitative trading and indicator development. He holds a PhD in engineering and became one of the most prolific contributors to *Technical Analysis of Stocks & Commodities* (TASC) magazine during the 1990s, serving as a Contributing Editor. Chande is CEO of Tuscarora Capital Management, a quantitative investment firm. He is the author of *Beyond Technical Analysis* (1997, 2nd ed. 2001) and co-author (with Stanley Kroll) of *The New Technical Trader* (1994). His indicators — particularly Aroon, CMO, and VIDYA — are now built into major trading platforms worldwide. He is widely regarded as one of the most important technical indicator developers of the 1990s.

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| CMO | TASC ~1993, *The New Technical Trader* (1994) | Oscillator |
| VIDYA | TASC Mar 1992, [\V10\C03\ADAPTIN](https://technical.traders.com/archive/article.asp?file=\V10\C03\ADAPTIN.pdf) | Adaptive MA |
| Aroon | TASC Sep 1995, [\V13\C09\THETIME](https://technical.traders.com/archive/article.asp?file=\V13\C09\THETIME.pdf) | Trend |
| RAVI | *Beyond Technical Analysis* (1997) | Filter |
| StochRSI | TASC May 1993, [\V11\C05\STOCHAS](https://technical.traders.com/archive/article.asp?file=\V11\C05\STOCHAS.pdf) (with Stanley Kroll) | Oscillator |
| QStick | *The New Technical Trader* (1994) | Trend |
| DMI (Dynamic Momentum Index) | TASC May 1993, *The New Technical Trader* (1994) (with Stanley Kroll) | Oscillator |
| Trend Score | *Beyond Technical Analysis* (1997) | Trend Strength |

### Indicator Formulas

#### CMO — Chande Momentum Oscillator
```
CMO = 100 × (Sum_Up - Sum_Down) / (Sum_Up + Sum_Down)
```
Where: Sum_Up = sum of positive price changes over n periods; Sum_Down = sum of absolute negative price changes over n periods. Range: -100 to +100. Default period: 9 or 14. OB/OS levels: +50 / -50.

#### VIDYA — Variable Index Dynamic Average
```
VIDYA(t) = Price × F × VI + VIDYA(t-1) × (1 - F × VI)
```
Where: `VI = |CMO(n)| / 100` (Volatility Index); `F = 2 / (period + 1)` (EMA smoothing constant). Default: CMO period 9, EMA period 12. Adapts speed based on CMO volatility — fast in trends, slow in ranges.

#### Aroon Up/Down & Oscillator
```
Aroon Up   = 100 × (period - bars_since_highest_high) / period
Aroon Down = 100 × (period - bars_since_lowest_low) / period
Aroon Osc  = Aroon Up - Aroon Down
```
Range: 0–100 (Up/Down); -100 to +100 (Oscillator). Default period: 25. "Aroon" = Sanskrit for "dawn's early light."

#### RAVI — Range Action Verification Index
```
RAVI = |SMA(short) - SMA(long)| / SMA(long) × 100
```
Default: Short SMA 7, Long SMA 65. Threshold: ±3%. Above = trending, below = ranging.

#### StochRSI — Stochastic RSI
```
StochRSI = (RSI - Min(RSI, n)) / (Max(RSI, n) - Min(RSI, n))
```
Range: 0 to 1. Default: RSI period 14, Stochastic period 14. Co-developed with Stanley Kroll.

#### QStick
```
QStick = MA(Close - Open, n)
```
Default period: 8. Positive = bullish candle dominance; negative = bearish candle dominance.

#### Dynamic Momentum Index (DMI)
```
Period = Int(14 / (StdDev(5) / SMA(StdDev(5), 10)))   [clamped to 3–30]
DMI = RSI(Period)
```
Variable-period RSI: shorter period in high volatility for faster response. Interpreted like RSI (70/30).

#### Trend Score
```
Trend Score = Σ sign(Close - Close[i]) for i = 1..n lookback comparisons
```
Sum of +1/-1 for each lookback comparison. Minor indicator, not widely adopted.

### Indicators Introduced in Books

#### The New Technical Trader (1994, with Stanley Kroll)
| Indicator | Category |
|-----------|----------|
| CMO (Chande Momentum Oscillator) | Oscillator |
| VIDYA (Variable Index Dynamic Average) | Adaptive MA |
| StochRSI (Stochastic RSI) | Oscillator |
| Dynamic Momentum Index | Oscillator |
| QStick | Trend/Candlestick |

#### Beyond Technical Analysis (1997/2001)
| Indicator | Category |
|-----------|----------|
| RAVI (Range Action Verification Index) | Filter |
| Aroon (refined) | Trend |
| VIDYA (refined, p.36 2nd ed.) | Adaptive MA |
| Trend Score | Trend Strength |

### Chandelier Exit — Misattribution Note

The Chandelier Exit is **NOT** Tushar Chande's indicator. It was developed by **Charles Le Beau** and popularized by Alexander Elder. While Chande discussed ATR-based stops in *Beyond Technical Analysis*, the Chandelier Exit is Le Beau's creation. MQL5 implementations frequently misattribute it to Chande.

## Books

| # | Title | Author | Year | Publisher | ISBN | Link |
|---|-------|--------|------|-----------|------|------|
| 1 | The New Technical Trader: Boost Your Profit by Plugging into the Latest Indicators | Tushar S. Chande, Stanley Kroll | 1994 | John Wiley & Sons | 978-0471597803 | [Google Books](https://books.google.com/books?isbn=0471597805) |
| 2 | Beyond Technical Analysis: How to Develop and Implement a Winning Trading System | Tushar S. Chande | 1997 | John Wiley & Sons | 978-0471161882 | [Google Books](https://books.google.com/books?isbn=0471161888) |
| 3 | Beyond Technical Analysis: How to Develop and Implement a Winning Trading System (2nd Ed.) | Tushar S. Chande | 2001 | John Wiley & Sons | 978-0471415671 | [Google Books](https://books.google.com/books?isbn=047141567X) |

### External Books Referencing Chande's Work

| # | Title | Author | Indicators Referenced |
|---|-------|--------|---------------------|
| 4 | Trading with the Odds | Cynthia Kase | CMO, VIDYA |
| 5 | Technical Analysis: The Complete Resource for Financial Market Technicians | Kirkpatrick & Dahlquist | Aroon, CMO |
| 6 | New Trading Systems and Methods | Perry Kaufman | VIDYA, CMO, Aroon |
| 7 | Encyclopedia of Technical Market Indicators | Robert Colby | CMO, Aroon, VIDYA, QStick |
| 8 | Come Into My Trading Room | Alexander Elder | Chandelier Exit (Le Beau) |
| 9 | Trading for a Living (Updated) | Alexander Elder | Chandelier Exit (Le Beau) |

## TASC Publications (Complete List, 1991–2001)

### 2001
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Jul | Estimating Future Drawdowns | Risk management and drawdown estimation | [\V19\C07\077EST](https://technical.traders.com/archive/article.asp?file=\V19\C07\077EST.pdf) |

### 1995
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Dec | Computer-Assisted Trading | Systematic trading approaches | [\V13\C12\COMPUTE](https://technical.traders.com/archive/article.asp?file=\V13\C12\COMPUTE.pdf) |
| Oct | Identifying Powerful Breakouts Early | Aroon indicator for breakout detection | [\V13\C10\IDENTIF](https://technical.traders.com/archive/article.asp?file=\V13\C10\IDENTIF.pdf) |
| Sep | The Time Price Oscillator | Aroon/trend timing indicator | [\V13\C09\THETIME](https://technical.traders.com/archive/article.asp?file=\V13\C09\THETIME.pdf) |
| Mar | A Market Bottom Pattern for S&P Futures | Pattern recognition for market bottoms | [\V13\C03\AMARKET](https://technical.traders.com/archive/article.asp?file=\V13\C03\AMARKET.pdf) |

### 1994
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Aug | Solving The Portfolio Puzzle | Portfolio optimization | [\V12\C08\SOLVING](https://technical.traders.com/archive/article.asp?file=\V12\C08\SOLVING.pdf) |
| May | Breadth Stix And Other Tricks | Market breadth indicators | [\V12\C05\BREADTH](https://technical.traders.com/archive/article.asp?file=\V12\C05\BREADTH.pdf) |
| Feb | Lattice Trees | Option pricing models | [\V12\C02\LATTICE](https://technical.traders.com/archive/article.asp?file=\V12\C02\LATTICE.pdf) |

### 1993
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Dec | The Cumulative Market Thrust Line | Market breadth analysis | [\V11\C12\THECUMU](https://technical.traders.com/archive/article.asp?file=\V11\C12\THECUMU.pdf) |
| Sep | Rating Trend Strength | CMO-based trend strength rating | [\V11\C09\RATINGT](https://technical.traders.com/archive/article.asp?file=\V11\C09\RATINGT.pdf) |
| May | Stochastic RSI And Dynamic Momentum Index | StochRSI & DMI introduction (with Stanley Kroll) | [\V11\C05\STOCHAS](https://technical.traders.com/archive/article.asp?file=\V11\C05\STOCHAS.pdf) |

### 1992
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Dec | Smart Stops | Volatility-based stop methods | [\V10\C12\SMARTST](https://technical.traders.com/archive/article.asp?file=\V10\C12\SMARTST.pdf) |
| Oct | Stocks Yield To Bonds | Intermarket analysis | [\V10\C10\STOCKSY](https://technical.traders.com/archive/article.asp?file=\V10\C10\STOCKSY.pdf) |
| Aug | Market Thrust | Market breadth momentum | [\V10\C08\MARKET](https://technical.traders.com/archive/article.asp?file=\V10\C08\MARKET.pdf) |
| May | Forecasting Tomorrow's Trading Day | Forecasting methodology | [\V10\C05\FORCAST](https://technical.traders.com/archive/article.asp?file=\V10\C05\FORCAST.pdf) |
| Mar | Adapting Moving Averages To Market Volatility | VIDYA introduction | [\V10\C03\ADAPTIN](https://technical.traders.com/archive/article.asp?file=\V10\C03\ADAPTIN.pdf) |

### 1991
| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Nov | The Midpoint Oscillator | Price midpoint-based oscillator | [\V09\C11\MIDPOIN](https://technical.traders.com/archive/article.asp?file=\V09\C11\MIDPOIN.pdf) |

### Interview (about Chande)
| Month | Year | Title | Article |
|-------|------|-------|---------|
| Oct | 1997 | Analysis in Action: Tushar Chande (by Thom Hartle) | [\V15\C10\ANALYSI](https://technical.traders.com/archive/article.asp?file=\V15\C10\ANALYSI.pdf) |

## Articles by Category

| Category | Count | Articles |
|----------|-------|----------|
| Indicators & Oscillators | 6 | Midpoint Oscillator, Adapting MAs (VIDYA), StochRSI/DMI, Rating Trend Strength, Time Price Oscillator, Identifying Breakouts (Aroon) |
| Market Breadth | 3 | Market Thrust, Cumulative Market Thrust Line, Breadth Stix |
| Trading Systems & Methods | 3 | Forecasting Tomorrow's Trading Day, Smart Stops, Computer-Assisted Trading |
| Intermarket / Macro | 2 | Stocks Yield To Bonds, Market Bottom Pattern |
| Risk Management | 1 | Estimating Future Drawdowns |
| Options / Pricing | 1 | Lattice Trees |
| Portfolio | 1 | Solving The Portfolio Puzzle |

## Photos, Videos & Interviews

| Source | Description | URL |
|--------|-------------|-----|
| TASC Interview | "Analysis in Action: Tushar Chande" by Thom Hartle, Oct 1997 | [\V15\C10\ANALYSI](https://technical.traders.com/archive/article.asp?file=\V15\C10\ANALYSI.pdf) |
| Book Author Photos | Author photos in *The New Technical Trader* and *Beyond Technical Analysis* jacket covers | [Print only] |
| YouTube | Trading presentations and indicator tutorials | [URL not found] |
| Bloomberg TV | Known market commentary appearances | [URL not found] |
| LinkedIn | CEO, Tuscarora Capital Management | [URL not found — requires login] |

## Forum Discussions

| Forum | Topic | URL |
|-------|-------|-----|
| MQL5 Forum | Tushar Chande's DMI discussion | https://www.mql5.com/en/forum/99452 |
| MQL5 Forum | Aroon Oscillator discussion | https://www.mql5.com/en/forum/4297/775036#comment_775036 |
| MQL5 Forum | VIDYA vs CDMA clarification | https://www.mql5.com/en/forum/175478/4283800#comment_4283800 |
| MQL5 Forum | Aroon corrections (Mladen Rakic) | https://www.mql5.com/en/forum/175037/4589561#comment_4589561 |
| MQL5 Forum | DMI improvements (Elite indicators) | https://www.mql5.com/en/forum/173874/4559256#comment_4559256 |
| ForexFactory | Aroon indicator and VIDYA threads | [Search: "Tushar Chande" site:forexfactory.com] |
| TradingView | Aroon built-in; CMO/VIDYA community scripts | https://www.tradingview.com/scripts/ |
| futures.io | VIDYA and Aroon discussions | [Known active] |
| Reddit r/algotrading | Aroon commonly discussed | [Known active] |

## MQL5 Implementations

### CMO (Chande Momentum Oscillator)
| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Chande Momentum Oscillator | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/411 |
| CMO (smoothed price version) | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/784 |
| DSL Chande momentum oscillator - smoothed | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/22649 |
| Dsl - CMO | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/20428 |
| Dsl - CMO bars | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/20429 |
| Chande Momentum Oscillator_Candle | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/14066 |
| Module of Trade Signals based on CMO | Aleksey Sergan | MT5 | Signal Module | https://www.mql5.com/en/code/444 |

### VIDYA (Variable Index Dynamic Average)
| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Variable Index Dynamic Average (VIDYA) | MetaQuotes | MT5 | Built-in | https://www.mql5.com/en/code/75 |
| Vidya (optimized CMO calculation) | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/22652 |
| Vidya zone | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/17804 |
| Vidya zone (MetaTrader 4) | Mladen Rakic | MT4 | Indicator | https://www.mql5.com/en/code/17803 |
| VIDYA indicator | Walter | MT4 | Indicator | https://www.mql5.com/en/code/9191 |
| VIDYA N Bars Borders | Vladimir Karputov | MT5 | EA | https://www.mql5.com/en/code/39574 |
| VIDYA N Bars Borders Martingale | Vladimir Karputov | MT5 | EA | https://www.mql5.com/en/code/39638 |
| iVIDyA indicator for mt4 | James Kirika Wanjiru | MT4 | Indicator | https://www.mql5.com/en/code/67497 |

### Aroon Indicator / Oscillator
| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Aroon | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/388 |
| Aroon Oscillator | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/389 |
| AROON | Scriptor | MT5 | Indicator | https://www.mql5.com/en/code/21022 |
| Aroon Oscillator | Collector | MT4 | Indicator | https://www.mql5.com/en/code/8328 |
| Aroon Oscillator (v2) | Collector | MT4 | Indicator | https://www.mql5.com/en/code/8363 |
| Aroon oscillator - multi time frame | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/24708 |
| Aroon oscillator - dynamic zones | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/17029 |
| Swami Aroon | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/22980 |

### RAVI (Range Action Verification Index)
| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| RAVI (Range Action Verification Index) | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/16067 |
| RAVI (Range Action Verification Index) | Scriptor | MT4 | Indicator | https://www.mql5.com/en/code/7871 |
| Range Action Verification Index - extended | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/22294 |
| RAVI iFish | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/19867 |

### QStick
| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Chandes Quick Stick (Qstick) | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/19858 |
| Chande QStick v1 | Scriptor | MT4 | Indicator | https://www.mql5.com/en/code/7886 |
| ChandeQStick | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/1885 |

### StochRSI
| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Stoch_RSI | Scriptor | MT5 | Indicator | https://www.mql5.com/en/code/21111 |

### Dynamic Momentum Index (DMI)
| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Tushar Chande's DMI | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/16806 |
| Chande's DMI (Dynamic Momentum Index) | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/20177 |
| Chande's DMI - std adaptive with floating levels | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/24385 |
| Chande's DMI - std adaptive with dsl signal lines | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/24384 |

### Chandelier Exit (NOTE: Charles Le Beau's indicator, not Chande's)
| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Chandelier exit | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/19875 |
| Chandelier Exit | Scriptor | MT4 | Indicator | https://www.mql5.com/en/code/7249 |
| Chandelier Exit | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/2194 |
| ChandelierExit_Candle | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/21739 |

### Mass Index (Dorsey/Chande)
| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| Mass Index | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/512 |

### MQL5 Articles Referencing Chande
| Title | URL |
|-------|-----|
| Learn how to design a trading system by VIDYA | https://www.mql5.com/en/articles/11341 |
| Building and testing Aroon Trading Systems | https://www.mql5.com/en/articles/14006 |
| Ready-made templates for including indicators to EAs (Part 3) | https://www.mql5.com/en/articles/13406 |

## Community & Reference Implementations

| Platform/Library | Function | Status |
|------------------|----------|--------|
| TA-Lib | `TA_CMO()` | ✅ Built-in |
| TA-Lib | `TA_AROON()` | ✅ Built-in |
| TA-Lib | `TA_AROONOSC()` | ✅ Built-in |
| TA-Lib | `TA_STOCHRSI()` | ✅ Built-in |
| pandas-ta | `cmo()` | ✅ Built-in |
| pandas-ta | `aroon()` | ✅ Built-in |
| pandas-ta | `vidya()` | ✅ Built-in |
| pandas-ta | `stochrsi()` | ✅ Built-in |
| pandas-ta | `qstick()` | ✅ Built-in |
| TradingView | Aroon | ✅ Built-in |
| TradingView | CMO (Chande Momentum Oscillator) | ✅ Built-in |
| TradingView | Stochastic RSI | ✅ Built-in |
| MetaTrader 5 | `iVIDyA` | ✅ Built-in |

## BibTeX

```bibtex
@article{chande1991midpoint,
  author  = {Chande, Tushar S.},
  title   = {The Midpoint Oscillator},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1991},
  volume  = {9},
  number  = {11},
  pages   = {431--434},
  url     = {https://technical.traders.com/archive/article.asp?file=\V09\C11\MIDPOIN.pdf}
}

@article{chande1992vidya,
  author  = {Chande, Tushar S.},
  title   = {Adapting Moving Averages To Market Volatility},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1992},
  volume  = {10},
  number  = {3},
  pages   = {108--114},
  url     = {https://technical.traders.com/archive/article.asp?file=\V10\C03\ADAPTIN.pdf}
}

@article{chande1992forecasting,
  author  = {Chande, Tushar S.},
  title   = {Forecasting Tomorrow's Trading Day},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1992},
  volume  = {10},
  number  = {5},
  pages   = {220--224},
  url     = {https://technical.traders.com/archive/article.asp?file=\V10\C05\FORCAST.pdf}
}

@article{chande1992thrust,
  author  = {Chande, Tushar S.},
  title   = {Market Thrust},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1992},
  volume  = {10},
  number  = {8},
  pages   = {347--350},
  url     = {https://technical.traders.com/archive/article.asp?file=\V10\C08\MARKET.pdf}
}

@article{chande1992stocks,
  author  = {Chande, Tushar S.},
  title   = {Stocks Yield To Bonds},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1992},
  volume  = {10},
  number  = {10},
  pages   = {403--406},
  url     = {https://technical.traders.com/archive/article.asp?file=\V10\C10\STOCKSY.pdf}
}

@article{chande1992stops,
  author  = {Chande, Tushar S.},
  title   = {Smart Stops},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1992},
  volume  = {10},
  number  = {12},
  pages   = {507--510},
  url     = {https://technical.traders.com/archive/article.asp?file=\V10\C12\SMARTST.pdf}
}

@article{chande1993stochrsi,
  author  = {Chande, Tushar S. and Kroll, Stanley},
  title   = {Stochastic {RSI} And Dynamic Momentum Index},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1993},
  volume  = {11},
  number  = {5},
  pages   = {189--199},
  url     = {https://technical.traders.com/archive/article.asp?file=\V11\C05\STOCHAS.pdf}
}

@article{chande1993rating,
  author  = {Chande, Tushar S.},
  title   = {Rating Trend Strength},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1993},
  volume  = {11},
  number  = {9},
  pages   = {382--386},
  url     = {https://technical.traders.com/archive/article.asp?file=\V11\C09\RATINGT.pdf}
}

@article{chande1993cumulative,
  author  = {Chande, Tushar S.},
  title   = {The Cumulative Market Thrust Line},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1993},
  volume  = {11},
  number  = {12},
  pages   = {506--511},
  url     = {https://technical.traders.com/archive/article.asp?file=\V11\C12\THECUMU.pdf}
}

@article{chande1994lattice,
  author  = {Chande, Tushar S.},
  title   = {Lattice Trees},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1994},
  volume  = {12},
  number  = {2},
  pages   = {65--69},
  url     = {https://technical.traders.com/archive/article.asp?file=\V12\C02\LATTICE.pdf}
}

@article{chande1994breadth,
  author  = {Chande, Tushar S.},
  title   = {Breadth Stix And Other Tricks},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1994},
  volume  = {12},
  number  = {5},
  pages   = {211--214},
  url     = {https://technical.traders.com/archive/article.asp?file=\V12\C05\BREADTH.pdf}
}

@article{chande1994portfolio,
  author  = {Chande, Tushar S.},
  title   = {Solving The Portfolio Puzzle},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1994},
  volume  = {12},
  number  = {8},
  url     = {https://technical.traders.com/archive/article.asp?file=\V12\C08\SOLVING.pdf}
}

@article{chande1995bottom,
  author  = {Chande, Tushar S.},
  title   = {A Market Bottom Pattern for {S\&P} Futures},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1995},
  volume  = {13},
  number  = {3},
  url     = {https://technical.traders.com/archive/article.asp?file=\V13\C03\AMARKET.pdf}
}

@article{chande1995timeprice,
  author  = {Chande, Tushar S.},
  title   = {The Time Price Oscillator},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1995},
  volume  = {13},
  number  = {9},
  url     = {https://technical.traders.com/archive/article.asp?file=\V13\C09\THETIME.pdf}
}

@article{chande1995breakouts,
  author  = {Chande, Tushar S.},
  title   = {Identifying Powerful Breakouts Early},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1995},
  volume  = {13},
  number  = {10},
  url     = {https://technical.traders.com/archive/article.asp?file=\V13\C10\IDENTIF.pdf}
}

@article{chande1995computer,
  author  = {Chande, Tushar S.},
  title   = {Computer-Assisted Trading},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1995},
  volume  = {13},
  number  = {12},
  url     = {https://technical.traders.com/archive/article.asp?file=\V13\C12\COMPUTE.pdf}
}

@article{chande2001drawdowns,
  author  = {Chande, Tushar S.},
  title   = {Estimating Future Drawdowns},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {2001},
  volume  = {19},
  number  = {7},
  pages   = {28--34},
  url     = {https://technical.traders.com/archive/article.asp?file=\V19\C07\077EST.pdf}
}

@book{chande1994newtrader,
  author    = {Chande, Tushar S. and Kroll, Stanley},
  title     = {The New Technical Trader: Boost Your Profit by Plugging into the Latest Indicators},
  year      = {1994},
  publisher = {John Wiley \& Sons},
  isbn      = {978-0471597803},
  url       = {https://books.google.com/books?isbn=0471597805}
}

@book{chande1997beyond,
  author    = {Chande, Tushar S.},
  title     = {Beyond Technical Analysis: How to Develop and Implement a Winning Trading System},
  year      = {1997},
  publisher = {John Wiley \& Sons},
  isbn      = {978-0471161882},
  url       = {https://books.google.com/books?isbn=0471161888}
}

@book{chande2001beyond,
  author    = {Chande, Tushar S.},
  title     = {Beyond Technical Analysis: How to Develop and Implement a Winning Trading System},
  edition   = {2},
  year      = {2001},
  publisher = {John Wiley \& Sons},
  isbn      = {978-0471415671},
  url       = {https://books.google.com/books?isbn=047141567X}
}

@online{hartle1997chande,
  author  = {Hartle, Thom},
  title   = {Analysis in Action: Tushar Chande},
  year    = {1997},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume  = {15},
  number  = {10},
  url     = {https://technical.traders.com/archive/article.asp?file=\V15\C10\ANALYSI.pdf}
}
```

## Sources

[1] Technical Analysis of Stocks & Commodities magazine XML TOC archives, systematic scan 1991–2010. https://technical.traders.com/
[2] MQL5 Code Base. https://www.mql5.com/en/code
[3] MQL5 Forum discussions. https://www.mql5.com/en/forum
[4] TA-Lib documentation. https://ta-lib.org/
[5] pandas-ta Python library. https://github.com/twopirllc/pandas-ta
[6] TradingView built-in indicators. https://www.tradingview.com/
[7] MetaTrader 5 documentation — iVIDyA. https://www.mql5.com/en/docs/indicators/ividya
[8] Chande, T.S. & Kroll, S. (1994). *The New Technical Trader*. Wiley.
[9] Chande, T.S. (2001). *Beyond Technical Analysis* (2nd ed.). Wiley.
[10] MQL5 Articles referencing Chande indicators. https://www.mql5.com/en/articles
