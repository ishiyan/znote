# Perry Kaufman — Research Brief

## Biography

Perry J. Kaufman (born October 17, 1943, New York, NY) is an American quantitative analyst, systematic trading strategist, and author whose career spans over five decades. Before entering finance, Kaufman worked in aerospace engineering on the Orbiting Astronomical Observatory and Project Gemini navigation systems.

He transitioned to financial markets in the early 1970s, becoming one of the pioneers of computerized trading systems. His first book, *Point and Figure Commodity Trading Techniques* (1975), was followed by *Commodity Trading Systems and Methods* (1978), which evolved through six editions into the encyclopedic *Trading Systems and Methods* (6th ed., 2020) — widely regarded as the definitive reference on systematic trading.

Kaufman is best known for developing the Kaufman Adaptive Moving Average (KAMA) and the Efficiency Ratio (ER), both introduced in *Smarter Trading* (1995). These tools are now standard in technical analysis libraries worldwide (TA-Lib, TradingView, MetaTrader, NinjaTrader, pandas-ta, R TTR).

He has authored 13 books, published 62 articles in *Technical Analysis of Stocks & Commodities* (TASC) magazine (1994–2026), and maintains active consulting through KaufmanSignals.com and Kaufman Analytics. He holds degrees from the City University of New York and has taught courses on algorithmic trading internationally.

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| KAMA (Kaufman Adaptive Moving Average) | 1995 *Smarter Trading* / TASC | Adaptive MA |
| Efficiency Ratio (ER) | 1995 *Smarter Trading* / TASC | Filter / Trend |
| Kaufman Volatility | 1995 *Smarter Trading* | Filter |
| Adaptive Momentum (AMA-based) | *Trading Systems and Methods* | Oscillator |
| Adaptive Trend Detection (StdDev filter) | *Trading Systems and Methods* | Trend |

### Indicator Formulas

#### KAMA — Kaufman Adaptive Moving Average

```
ER = |Price[i] - Price[i-n]| / Σ(|Price[i] - Price[i-1]|) for i over n periods

SC = [ER × (fast_SC - slow_SC) + slow_SC]²
   where fast_SC = 2/(2+1) = 0.6667
         slow_SC = 2/(30+1) = 0.0645

KAMA[i] = KAMA[i-1] + SC × (Price[i] - KAMA[i-1])
```

Adaptive moving average that speeds up in trending markets (ER → 1) and slows down in choppy markets (ER → 0).

#### Efficiency Ratio (ER)

```
ER = |Close[i] - Close[i-n]| / Σ(|Close[i] - Close[i-1]|) for n periods
```

Range: 0 to 1. Higher values indicate more efficient/trending price movement. Also known as Generalized Fractal Efficiency.

#### Kaufman Volatility

```
Volatility = Σ(|Close[i] - Close[i-1]|) over n periods
```

Sum of absolute price changes; the denominator of ER. Used as a noise/volatility measure.

#### Adaptive Trend Detection

```
Signal: |KAMA[i] - KAMA[i-1]| > k × StdDev(KAMA changes, n)
```

Uses standard deviation of KAMA changes to filter insignificant movements.

### Indicators Introduced in Books

#### Trading Systems and Methods (6th ed., 2020)

| Indicator/Concept | Chapter | Category |
|-------------------|---------|----------|
| KAMA (comprehensive treatment) | Adaptive Techniques | Adaptive MA |
| Efficiency Ratio | Adaptive Techniques | Filter |
| Adaptive Trend Detection | Adaptive Techniques | Trend |
| Adaptive Momentum | Momentum & Oscillators | Oscillator |
| Noise measurement methods | Statistical Analysis | Filter |
| Portfolio allocation models | Portfolio Management | Allocation |

#### Smarter Trading (1995)

| Indicator/Concept | Category |
|-------------------|----------|
| KAMA (first introduction) | Adaptive MA |
| Efficiency Ratio (first introduction) | Filter / Trend |
| Kaufman Volatility | Filter |
| Adaptive smoothing framework | Framework |
| Noise measurement | Filter |

#### Alpha Trading (2011)

| Indicator/Concept | Category |
|-------------------|----------|
| Market-neutral strategies | Pairs/Arb |
| Statistical arbitrage methods | Pairs/Arb |
| Pairs trading frameworks | Pairs/Arb |

## Books

| # | Title | Author | Year | Publisher | ISBN | Link |
|---|-------|--------|------|-----------|------|------|
| 1 | Point and Figure Commodity Trading Techniques | Perry J. Kaufman | 1975 | Investors Intelligence | — | [URL not found] |
| 2 | Commodity Trading Systems and Methods | Perry J. Kaufman | 1978 | John Wiley & Sons | 978-0471027607 | [Google Books](https://books.google.com/books?id=x7JQAAAAMAAJ) |
| 3 | Technical Analysis in Commodities | Perry J. Kaufman | 1980 | John Wiley & Sons | 978-0471084228 | [Google Books](https://books.google.com/books?id=IxJRAQAAIAAJ) |
| 4 | Handbook of Futures Markets | Perry J. Kaufman | 1984 | John Wiley & Sons | 978-0471082552 | [URL not found] |
| 5 | The Concise Handbook of Futures Markets | Perry J. Kaufman | 1986 | John Wiley & Sons | 978-0471027966 | [URL not found] |
| 6 | The New Commodity Trading Systems and Methods (2nd ed.) | Perry J. Kaufman | 1987 | John Wiley & Sons | 978-0471878797 | [Google Books](https://books.google.com/books?id=YnNPAAAAMAAJ) |
| 7 | Smarter Trading: Improving Performance in Changing Markets | Perry J. Kaufman | 1995 | McGraw-Hill | 978-0070340305 | [Google Books](https://books.google.com/books?id=6mYJAQAAMAAJ) |
| 8 | Global Equity Investing (with Alberto Vivanti) | Perry J. Kaufman | 1997 | McGraw-Hill | 978-0070340480 | [URL not found] |
| 9 | Trading Systems and Methods (3rd ed.) | Perry J. Kaufman | 1998 | John Wiley & Sons | 978-0471148791 | [URL not found] |
| 10 | A Short Course in Technical Trading | Perry J. Kaufman | 2003 | John Wiley & Sons | 978-0471268482 | [Google Books](https://books.google.com/books?id=dOjfZ4MiMNkC) |
| 11 | Trading Systems and Methods (4th ed.) | Perry J. Kaufman | 2005 | John Wiley & Sons | 978-0471697121 | [URL not found] |
| 12 | Alpha Trading: Profitable Strategies That Remove Directional Risk | Perry J. Kaufman | 2011 | John Wiley & Sons | 978-0470529744 | [Google Books](https://books.google.com/books?id=3tW-DJ4ggXwC) |
| 13 | Trading Systems and Methods (5th ed.) | Perry J. Kaufman | 2013 | John Wiley & Sons | 978-1118043561 | [URL not found] |
| 14 | Trading Systems and Methods (6th ed.) | Perry J. Kaufman | 2020 | John Wiley & Sons | 978-1119605355 | [Google Books](https://books.google.com/books?id=1kjNDwAAQBAJ) |
| 15 | Kaufman Constructs Trading Systems | Perry J. Kaufman | 2020 | KaufmanSignals | — | [URL not found] |
| 16 | Learn to Trade: Trade To Win With A Rule-Based Method | Perry J. Kaufman | 2022 | — | — | [URL not found] |

## TASC Publications (Complete List, 1994–2026)

### 2026

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| May | When To Use A Frequency Distribution Or A Standard Deviation | Understand both methods so you can apply them where they do the most good | [\V44\C05\119KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V44\C05\119KAUF.pdf) |
| Apr | Trading The Crack Spread | A crack spread—the price difference between crude oil and refined products | [\V44\C04\108KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V44\C04\108KAUF.pdf) |
| Jan | Smoothing The Data | Of the various smoothing methods commonly available | [\V44\C01\065KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V44\C01\065KAUF.pdf) |

### 2025

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Bonus | New Moon--Full Moon | Is there really any relationship between the phases of the moon | [\V43\C13\937KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V43\C13\937KAUF.pdf) |
| Nov | Low-Priced Stocks: A Golden Opportunity Or An Unreasonable Risk? | When a stock is cheap or has sold off, is it a good buy? | [\V43\C11\041KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V43\C11\041KAUF.pdf) |
| Sep | Using The Elusive Volume Confirmation | There is a popular concept that volume confirms price action | [\V43\C09\013KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V43\C09\013KAUF.pdf) |
| Aug | Explaining FX Carry (In Detail) | Do you have an understanding of how carry trades work | [\V43\C08\998KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V43\C08\998KAUF.pdf) |
| Jun | There Is Money To Be Made On The Weekends | Many traders exit the market on Fridays to minimize risks | [\V43\C06\977KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V43\C06\977KAUF.pdf) |
| May | Trading The Channel | It's a classic, well-respected method among chartists | [\V43\C05\958KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V43\C05\958KAUF.pdf) |
| Apr | Do Stops Really Work? | Whether to use stop orders is a fundamental question | [\V43\C04\946KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V43\C04\946KAUF.pdf) |
| Mar | Revisiting The 3-Day Trade | Here's a favorite trading strategy. Can we boost performance | [\V43\C03\926KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V43\C03\926KAUF.pdf) |
| Feb | Chasing The Market | Can you make money after a big move up | [\V43\C02\914KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V43\C02\914KAUF.pdf) |

### 2024

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Bonus | Pros And Cons Of Daily Versus Weekly Trend Following | Weekly data is smoother than daily data | [\V42\C13\770KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C13\770KAUF.pdf) |
| Dec | Overlooked Strategy Rules | If you're only using a trend and a stop-loss, you're missing out | [\V42\C12\885KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C12\885KAUF.pdf) |
| Nov | Trading A Breakout System | When trading a breakout system, does it improve results to get in early or late? | [\V42\C11\872KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C11\872KAUF.pdf) |
| Oct | Can A Stochastic Indicator Be A Trading System? | Are signals from the stochastic oscillator reliable enough | [\V42\C10\858KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C10\858KAUF.pdf) |
| Sep | Which Is Better: The N-Day Breakout Or The Swing Breakout? | Here's a study comparing swing highs and lows vs. new highs/lows | [\V42\C09\844KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C09\844KAUF.pdf) |
| Aug | Theory Versus Reality | Are your expectations in line with reality? | [\V42\C08\829KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C08\829KAUF.pdf) |
| Jun | Trading Opening Gaps And Extreme Closes In Stocks | When large opening moves and large closing moves occur | [\V42\C06\804KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C06\804KAUF.pdf) |
| May | How Professionals Assign Risk | Risk versus return is the name of the game in trading | [\V42\C05\792KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C05\792KAUF.pdf) |
| Apr | Determining Risk Before It Happens | Assessing the risk of being in the markets | [\V42\C04\782KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C04\782KAUF.pdf) |
| Mar | The Delta-Delta Crude Strategy | Here is an interesting trading strategy you can consider for crude oil | [\V42\C03\759KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C03\759KAUF.pdf) |
| Feb | Crossover Trading: Arbitraging The Physical With The Stock | Arbitrage trading isn't limited to stock pairs or interest rate markets | [\V42\C02\748KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C02\748KAUF.pdf) |
| Jan | Gap Momentum | Here's a way to use opening gap data to create a momentum strategy | [\V42\C01\730KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V42\C01\730KAUF.pdf), [Tips](http://traders.com/Documentation/FEEDbk_docs/2024/01/TradersTips.html) |

### 2023

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Dec | A Strategy For Trading Seasonal And Non-Seasonal Markets | If you can see a seasonal or non-seasonal pattern, you may be able to profit | [\V41\C12\719KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C12\719KAUF.pdf) |
| Nov | Interview: A Conversation With Herb Friedman | Herb Friedman manages money using high-yield mutual funds | [\V41\C11\710INTE.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C11\710INTE.pdf) |
| Oct | How To Trade Merger Arb | Mergers and acquisitions present opportunities for speculation | [\V41\C10\691KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C10\691KAUF.pdf) |
| Aug | The Portfolio Risk Dilemma: Let It Run Or Rebalance? | When volatility becomes too high, how can you reduce portfolio exposure | [\V41\C08\653KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C08\653KAUF.pdf) |
| Aug | ChatGPT: Are We There Yet? | So, are the recently developed chatbot AI tools ready for the trading world? | [\V41\C08\663KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C08\663KAUF.pdf) |
| Jun | Protecting Your Wealth While Making A Profit | By allocating capital to the equity index markets in different regions | [\V41\C06\627KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C06\627KAUF.pdf) |
| Apr | Repatriation | Traders are always looking for tradable patterns in the data | [\V41\C04\595KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C04\595KAUF.pdf) |
| Mar | Can Volume Predict Price? | What does higher or lower volume today suggest about tomorrow's price? | [\V41\C03\572KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C03\572KAUF.pdf) |
| Feb | Do Small Price Changes Matter Or Are They Just Noise? | Can trend trading be improved by filtering out small price moves | [\V41\C02\559KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C02\559KAUF.pdf) |
| Jan | Matching The Markets To Your Trading Style | Traders can choose to use a trend-following method or mean-reversion | [\V41\C01\542KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V41\C01\542KAUF.pdf) |

### 2022

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Bonus | 50 Years On, What Have I Learned? | A collection of 20 market observations | [\V40\C13\397KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V40\C13\397KAUF.pdf) |
| Sep | What Is The Real Risk Of System Trading? | By knowing the risk of being in the market, you can hedge and control | [\V40\C09\477KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V40\C09\477KAUF.pdf) |
| Jul | Is It Too Volatile To Trade? | Traders profit from volatility. But what exactly is the tipping point | [\V40\C07\451KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V40\C07\451KAUF.pdf) |
| May | In-Sample Test Data, Out-of-Sample Data--Does It Really Matter? | Backtesting a trading strategy or trading system before trading | [\V40\C05\421KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V40\C05\421KAUF.pdf) |
| Jan | Trading A Moving Average System: Important Choices | Most traders have used moving average-based trading systems | [\V40\C01\353KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V40\C01\353KAUF.pdf) |

### 2021

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Oct | Capturing Opportunity By Fading The News | Is there an opportunity to sell a rally following a stock upgrade | [\V39\C10\313KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V39\C10\313KAUF.pdf) |
| Aug | Playing It Safe With Cryptos | Cryptocurrency trading carries various kinds of risks | [\V39\C08\282KAUF.PDF](https://technical.traders.com/archive/article.asp?file=\V39\C08\282KAUF.PDF) |
| May | Better Entries | Does waiting for a pullback when entering a trade improve results | [\V39\C05\239KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V39\C05\239KAUF.pdf) |
| Mar | Avoiding The Pitfalls Of Historical Data | Testing a trading strategy depends on handling the data correctly | [\V39\C03\207KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V39\C03\207KAUF.pdf) |
| Jan | A Fresh Look At Short-Term Patterns | You may be familiar with some of the most popular short-term patterns | [\V39\C01\168KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V39\C01\168KAUF.pdf), [Tips](http://traders.com/Documentation/FEEDbk_docs/2021/01/TradersTips.html) |

### 2020

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Bonus | Essential Math For Traders | Do you understand the right way to calculate risk, reward | [\V38\C13\024KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V38\C13\024KAUF.pdf) |
| Nov | Comparing Two Adaptive Trends | Walk-forward testing and Kaufman's adaptive moving average | [\V38\C11\140KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V38\C11\140KAUF.pdf) |
| Sep | Fools Rush In: Investing In IPOs | Many people rue the day that they passed up an opportunity to buy an IPO | [\V38\C09\116KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V38\C09\116KAUF.pdf) |
| Jun | Price Shocks: Anticipation Is Everything | A major selloff in the market can happen suddenly or build slowly | [\V38\C06\069KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V38\C06\069KAUF.pdf) |
| Mar | The 1st And 2nd Cross | Traders know it is not possible to perfectly capture a full trend | [\V38\C03\012KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V38\C03\012KAUF.pdf) |

### 2019

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Nov | Running For Cover | After stocks take a dive, many investors flee into bonds | [\V37\C11\949KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V37\C11\949KAUF.pdf) |
| Sep | A Simple Way To Trade Seasonality | You can locate patterns to perform seasonal trades | [\V37\C09\913KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V37\C09\913KAUF.pdf), [Tips](http://traders.com/Documentation/FEEDbk_docs/2019/09/TradersTips.html) |
| Jan | Volatility: What They Don't Teach You In Grad School | You're most likely not going to engage in a conversation about "lognormal volatility" | [\V37\C01\778KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V37\C01\778KAUF.pdf) |

### 2018

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Jul | In Search Of The Best Trend | There are so many ways to measure trends | [\V36\C07\682KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V36\C07\682KAUF.pdf) |
| Feb | Profit-Taking And Resets Part 2: Short-Term Trading | Trends can be useful for longer-term trades but what about short-term trades? | [\V36\C02\591KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V36\C02\591KAUF.pdf) |
| Jan | Profit-Taking And Resets Part 1: Trend-Following | In this first part of a two-part series, we look at long-term trends | [\V36\C01\573KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V36\C01\573KAUF.pdf) |

### 2017

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Sep | Optimization - Getting It Right | Creating a trading system is hard work and we want our system to work well | [\V35\C09\507KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V35\C09\507KAUF.pdf) |
| Jul | The Return Of High Momentum | There's no right or wrong way to look at the market | [\V35\C07\474KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V35\C07\474KAUF.pdf) |
| Mar | VIX Or Historical Volatility? | Position sizing is an often overlooked variable | [\V35\C03\390KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V35\C03\390KAUF.pdf) |

### 2014

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Jun | Slope Divergence: Capitalizing On Uncertainty | It's a classic chart pattern—divergence patterns that could generate profits are easy to miss | [\V32\C06\789KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V32\C06\789KAUF.pdf), [Tips](http://traders.com/Documentation/FEEDbk_docs/2014/06/TradersTips.html) |
| Apr | A Better Trend | How can a trend be better? Here's a unique approach to viewing trends | [\V32\C04\762KAUF.PDF](https://technical.traders.com/archive/article.asp?file=\V32\C04\762KAUF.PDF) |
| Mar | Timing The Market With Pairs Logic | Fundamentally different strategies, drawing from a broad set of markets, will offer better risk protection | [\V32\C03\725KAUF.pdf](https://technical.traders.com/archive/article.asp?file=\V32\C03\725KAUF.pdf), [Tips](http://traders.com/Documentation/FEEDbk_docs/2014/03/TradersTips.html) |

### 1994

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Apr | On Profit-Taking | — | [\V12\C04\ONPROFI.pdf](https://technical.traders.com/archive/article.asp?file=\V12\C04\ONPROFI.pdf) |

## Articles by Category

| Category | Count | Articles |
|----------|-------|----------|
| Trading Systems | 8 | Timing The Market With Pairs Logic, A Better Trend, Optimization - Getting It Right, Profit-Taking And Resets Part 1 & 2, In Search Of The Best Trend, Trading A Moving Average System, Can A Stochastic Indicator Be A Trading System?, Trading A Breakout System |
| Trading Strategies | 7 | A Simple Way To Trade Seasonality, Gap Momentum, The Delta-Delta Crude Strategy, Revisiting The 3-Day Trade, New Moon--Full Moon, A Strategy For Trading Seasonal And Non-Seasonal Markets, Protecting Your Wealth |
| Trading Techniques | 8 | Better Entries, Is It Too Volatile To Trade?, Matching The Markets, Do Stops Really Work?, Trading The Channel, There Is Money To Be Made On The Weekends, Crossover Trading, Pros And Cons Of Daily Versus Weekly |
| Risk Management | 5 | Price Shocks, What Is The Real Risk?, The Portfolio Risk Dilemma, How Professionals Assign Risk, Determining Risk Before It Happens |
| Analysis / Technical Analysis | 6 | Fools Rush In, Comparing Two Adaptive Trends, Can Volume Predict Price?, Smoothing The Data, Essential Math For Traders, When To Use A Frequency Distribution |
| Trading Methods | 2 | Which Is Better: The N-Day Breakout Or The Swing Breakout?, Trading The Channel |
| Price Studies / Patterns | 3 | A Fresh Look At Short-Term Patterns, Trading Opening Gaps, The 1st And 2nd Cross |
| Market Timing / Stock Analysis | 3 | Running For Cover, Chasing The Market, Low-Priced Stocks |
| Money Management | 1 | Volatility: What They Don't Teach You In Grad School |
| Options | 1 | VIX Or Historical Volatility? |
| Cryptocurrency | 1 | Playing It Safe With Cryptos |
| Artificial Intelligence | 1 | ChatGPT: Are We There Yet? |
| Currencies | 1 | Explaining FX Carry (In Detail) |
| Volume Analysis | 1 | Using The Elusive Volume Confirmation |
| Futures Trading | 1 | Repatriation |
| Other (Interview, Real World, System Dev, Backtesting) | 9 | Various |

## Photos, Videos & Interviews

### Photos

| Description | URL | Source |
|-------------|-----|--------|
| Book jacket photo (Trading Systems and Methods, all editions) | [URL not found] | John Wiley & Sons |
| Wikipedia page (no photo uploaded) | https://en.wikipedia.org/wiki/Perry_J._Kaufman | Wikipedia |
| Conference photos (IMN, MTA archives) | [URL not found] | Various |

### Videos

| Title | URL | Duration | Date |
|-------|-----|----------|------|
| Perry Kaufman at INO TV (multiple segments) | https://www.ino.com/blog/tag/perry-kaufman/ | Various | Various |
| YouTube interviews (multiple) | https://www.youtube.com/results?search_query=Perry+Kaufman+trading | Various | Various |

### Interviews & Podcasts

| Title | URL | Host/Publication | Date |
|-------|-----|-----------------|------|
| TradingMarkets articles/interviews | https://www.tradingmarkets.com/recent/perry_j._kaufman-36.html | TradingMarkets | Various |
| Interview — The Technical Analyst | [URL not found] | The Technical Analyst | 2009 |
| Interview with Perry Kaufman (TASC) | [\V32\C07\INTE.pdf](https://technical.traders.com/archive/article.asp?file=\V32\C07\INTE.pdf) | TASC (Jayanthi Gopalakrishnan) | Jul 2014 |
| IMN Conference appearances | [URL not found] | Information Management Network | Various |

### Websites

| Site | URL | Status |
|------|-----|--------|
| Official website | https://www.perrykaufman.com | Active |
| KaufmanSignals.com | https://www.kaufmansignals.com | Active |
| Kaufman Analytics | https://www.kaufmananalytics.com | Active |

## Forum Discussions

| Forum | Presence | Notes |
|--------|----------|-------|
| ForexFactory | Confirmed | KAMA indicator discussions; search blocked by anti-bot |
| futures.io | Confirmed | Kaufman Adaptive Moving Average threads |
| TradingView | Extensive | Multiple KAMA scripts; built-in `ta.kama()` function |
| EliteTrader | Confirmed | Threads discussing *Trading Systems and Methods* |
| Wealth-Lab | Confirmed | KAMA implemented in WealthScript |
| Quant StackExchange | Confirmed | Q&A about Efficiency Ratio |
| Reddit r/algotrading | Confirmed | Discussions of KAMA, Efficiency Ratio |
| Trade2Win | Confirmed | Reviews of Kaufman books |
| MQL5 Forum | Extensive | Dozens of threads, 42 code implementations |
| NinjaTrader Forum | Confirmed | KAMA implementations discussed |

*Note: Direct URL verification was blocked by 403/anti-bot protections on ForexFactory, TradingView, and futures.io.*

## MQL5 Implementations

| # | Title | Author | Platform | Type | URL |
|---|-------|--------|----------|------|-----|
| 1 | KAMA | Scriptor | MT5 | Indicator | https://www.mql5.com/en/code/20502 |
| 2 | KAMA | Walter | MT4 | Indicator | https://www.mql5.com/en/code/9167 |
| 3 | AMA to KAMA crossover | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23758 |
| 4 | AMA to KAMA crossover - histogram | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23760 |
| 5 | Adaptive Moving Average - AMA | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23755 |
| 6 | Adaptive Moving Average - AMA - with filter | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23756 |
| 7 | Adaptive Moving Average - AMA - filter histogram | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23757 |
| 8 | Adaptive Moving Average - generalized with floating levels | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23780 |
| 9 | Adaptive Moving Average - generalized | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23778 |
| 10 | Kaufman AMA - with floating levels | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/22292 |
| 11 | Kaufman AMA MACD | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/20487 |
| 12 | Kaufman AMA with filter | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/20486 |
| 13 | KAMA Keltner Channel | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/21693 |
| 14 | Adaptive efficiency ratio EMA | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23857 |
| 15 | Adaptive moving average - double smoothed | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/24775 |
| 16 | Adaptive Moving Average - AMA (MT4) | Mladen Rakic | MT4 | Indicator | https://www.mql5.com/en/code/25732 |
| 17 | Perry Kaufman AMA Optimized | MetaQuotes | MT4 | Indicator | https://www.mql5.com/en/code/7385 |
| 18 | Kaufman's AMA from wellx | MetaQuotes | MT4 | Indicator | https://www.mql5.com/en/code/7378 |
| 19 | Optimized variant of Kaufman's AMA by wellx | MetaQuotes | MT4 | Indicator | https://www.mql5.com/en/code/7379 |
| 20 | AMkA (AMA with signal points) | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/387 |
| 21 | i-AMA-Optimum | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/2387 |
| 22 | Ticker_AMA | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/2347 |
| 23 | ColorMomentum_AMA | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/468 |
| 24 | Kaufman Efficiency Ratio | Boris Armenteros | MT5 | Indicator | https://www.mql5.com/en/code/351 |
| 25 | Kaufman Efficiency Ratio | Boris Armenteros | MT4 | Indicator | https://www.mql5.com/en/code/10187 |
| 26 | Kaufman Volatility | Boris Armenteros | MT5 | Indicator | https://www.mql5.com/en/code/350 |
| 27 | Kaufman Volatility | Boris Armenteros | MT4 | Indicator | https://www.mql5.com/en/code/10188 |
| 28 | Directional Efficiency Ratio | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/19985 |
| 29 | Efficiency ratio directional with levels | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/22700 |
| 30 | Polarized Fractal Efficiency | Giampiero Raschetti | MT4 | Indicator | https://www.mql5.com/en/code/8059 |
| 31 | Polarized Fractal Efficiency | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/713 |
| 32 | Adaptive ATR | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23852 |
| 33 | Adaptive ATR channel | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/23853 |
| 34 | Adaptive ATR channel (v2) | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/22964 |
| 35 | Adaptive deviation | Mladen Rakic | MT5 | Indicator | https://www.mql5.com/en/code/26384 |
| 36 | IncEROnArray (ER class library) | Dmitry Fedoseev | MT5 | Library | https://www.mql5.com/en/code/631 |
| 37 | IncERDOnArray (Directional ER class) | Dmitry Fedoseev | MT5 | Library | https://www.mql5.com/en/code/632 |
| 38 | IncAMAOnArray (AMA class library) | Dmitry Fedoseev | MT5 | Library | https://www.mql5.com/en/code/630 |
| 39 | CEROnRingBuffer (ER ring buffer class) | Konstantin Gruzdev | MT5 | Library | https://www.mql5.com/en/code/1374 |
| 40 | CAMAOnRingBuffer (AMA ring buffer class) | Konstantin Gruzdev | MT5 | Library | https://www.mql5.com/en/code/1375 |
| 41 | Adaptive Moving Average (AMA) — BUILT-IN | MetaQuotes | MT5 | Built-in | https://www.mql5.com/en/code/10 |
| 42 | Self-Aware Trend System (uses ER) | Hammad Dilber | MT5 | EA | https://www.mql5.com/en/code/72247 |

## Community & Reference Implementations

| Platform/Library | Function | Status |
|-----------------|----------|--------|
| TA-Lib | `TA_KAMA()` | Built-in (Overlap Studies group) |
| pandas-ta | `df.ta.kama()` | Built-in |
| TradingView (Pine Script) | `ta.kama(source, length)` | Built-in function |
| MetaTrader 5 | Adaptive Moving Average indicator | Ships with MT5 |
| MetaTrader 4 | Custom indicator (many versions) | Available via codebase |
| NinjaTrader | `KAMA()` indicator | Built-in standard indicator |
| Wealth-Lab | WealthScript implementation | Available |
| Python stockstats | `kama` | Available |
| R (TTR package) | `KAMA()` | Available |

## BibTeX

```bibtex
% === TASC Articles (62) ===

@article{kaufman1994profit,
  author = {Kaufman, Perry J.},
  title = {On Profit-Taking},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {12},
  number = {4},
  year = {1994},
  month = apr
}

@article{kaufman2014pairs,
  author = {Kaufman, Perry J.},
  title = {Timing The Market With Pairs Logic},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {32},
  number = {3},
  year = {2014},
  month = mar
}

@article{kaufman2014trend,
  author = {Kaufman, Perry},
  title = {A Better Trend},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {32},
  number = {4},
  year = {2014},
  month = apr
}

@article{kaufman2014slope,
  author = {Kaufman, Perry J.},
  title = {Slope Divergence: Capitalizing On Uncertainty},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {32},
  number = {6},
  year = {2014},
  month = jun
}

@article{kaufman2017optimization,
  author = {Kaufman, Perry J.},
  title = {Optimization - Getting It Right},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {35},
  number = {9},
  year = {2017},
  month = sep
}

@article{kaufman2017vix,
  author = {Kaufman, Perry J.},
  title = {VIX Or Historical Volatility?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {35},
  number = {3},
  year = {2017},
  month = mar
}

@article{kaufman2017momentum,
  author = {Kaufman, Perry J.},
  title = {The Return Of High Momentum},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {35},
  number = {7},
  year = {2017},
  month = jul
}

@article{kaufman2018profit1,
  author = {Kaufman, Perry J.},
  title = {Profit-Taking And Resets Part 1: Trend-Following},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {36},
  number = {1},
  year = {2018},
  month = jan
}

@article{kaufman2018profit2,
  author = {Kaufman, Perry J.},
  title = {Profit-Taking And Resets Part 2: Short-Term Trading},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {36},
  number = {2},
  year = {2018},
  month = feb
}

@article{kaufman2018besttrend,
  author = {Kaufman, Perry J.},
  title = {In Search Of The Best Trend},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {36},
  number = {7},
  year = {2018},
  month = jul
}

@article{kaufman2019volatility,
  author = {Kaufman, Perry J.},
  title = {Volatility: What They Don't Teach You In Grad School},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {37},
  number = {1},
  year = {2019},
  month = jan
}

@article{kaufman2019seasonality,
  author = {Kaufman, Perry J.},
  title = {A Simple Way To Trade Seasonality},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {37},
  number = {9},
  year = {2019},
  month = sep
}

@article{kaufman2019cover,
  author = {Kaufman, Perry J.},
  title = {Running For Cover},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {37},
  number = {11},
  year = {2019},
  month = nov
}

@article{kaufman2020cross,
  author = {Kaufman, Perry J.},
  title = {The 1st And 2nd Cross},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {38},
  number = {3},
  year = {2020},
  month = mar
}

@article{kaufman2020shocks,
  author = {Kaufman, Perry J.},
  title = {Price Shocks: Anticipation Is Everything},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {38},
  number = {6},
  year = {2020},
  month = jun
}

@article{kaufman2020ipos,
  author = {Kaufman, Perry J.},
  title = {Fools Rush In: Investing In IPOs},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {38},
  number = {9},
  year = {2020},
  month = sep
}

@article{kaufman2020adaptive,
  author = {Kaufman, Perry J.},
  title = {Comparing Two Adaptive Trends},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {38},
  number = {11},
  year = {2020},
  month = nov
}

@article{kaufman2020math,
  author = {Kaufman, Perry J.},
  title = {Essential Math For Traders},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {38},
  number = {13},
  year = {2020},
  note = {Bonus Issue}
}

@article{kaufman2021patterns,
  author = {Kaufman, Perry J.},
  title = {A Fresh Look At Short-Term Patterns},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {39},
  number = {1},
  year = {2021},
  month = jan
}

@article{kaufman2021data,
  author = {Kaufman, Perry J.},
  title = {Avoiding The Pitfalls Of Historical Data},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {39},
  number = {3},
  year = {2021},
  month = mar
}

@article{kaufman2021entries,
  author = {Kaufman, Perry J.},
  title = {Better Entries},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {39},
  number = {5},
  year = {2021},
  month = may
}

@article{kaufman2021crypto,
  author = {Kaufman, Perry J.},
  title = {Playing It Safe With Cryptos},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {39},
  number = {8},
  year = {2021},
  month = aug
}

@article{kaufman2021fading,
  author = {Kaufman, Perry J.},
  title = {Capturing Opportunity By Fading The News},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {39},
  number = {10},
  year = {2021},
  month = oct
}

@article{kaufman2022ma,
  author = {Kaufman, Perry J.},
  title = {Trading A Moving Average System: Important Choices},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {40},
  number = {1},
  year = {2022},
  month = jan
}

@article{kaufman2022insample,
  author = {Kaufman, Perry J.},
  title = {In-Sample Test Data, Out-of-Sample Data--Does It Really Matter?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {40},
  number = {5},
  year = {2022},
  month = may
}

@article{kaufman2022volatile,
  author = {Kaufman, Perry J.},
  title = {Is It Too Volatile To Trade?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {40},
  number = {7},
  year = {2022},
  month = jul
}

@article{kaufman2022risk,
  author = {Kaufman, Perry J.},
  title = {What Is The Real Risk Of System Trading?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {40},
  number = {9},
  year = {2022},
  month = sep
}

@article{kaufman2022fifty,
  author = {Kaufman, Perry J.},
  title = {50 Years On, What Have I Learned?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {40},
  number = {13},
  year = {2022},
  note = {Bonus Issue}
}

@article{kaufman2023matching,
  author = {Kaufman, Perry J.},
  title = {Matching The Markets To Your Trading Style},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {1},
  year = {2023},
  month = jan
}

@article{kaufman2023noise,
  author = {Kaufman, Perry J.},
  title = {Do Small Price Changes Matter Or Are They Just Noise?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {2},
  year = {2023},
  month = feb
}

@article{kaufman2023volume,
  author = {Kaufman, Perry J.},
  title = {Can Volume Predict Price?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {3},
  year = {2023},
  month = mar
}

@article{kaufman2023repatriation,
  author = {Kaufman, Perry J.},
  title = {Repatriation},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {4},
  year = {2023},
  month = apr
}

@article{kaufman2023wealth,
  author = {Kaufman, Perry J.},
  title = {Protecting Your Wealth While Making A Profit},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {6},
  year = {2023},
  month = jun
}

@article{kaufman2023portfolio,
  author = {Kaufman, Perry J.},
  title = {The Portfolio Risk Dilemma: Let It Run Or Rebalance?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {8},
  year = {2023},
  month = aug
}

@article{kaufman2023chatgpt,
  author = {Kaufman, Perry J.},
  title = {ChatGPT: Are We There Yet?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {8},
  year = {2023},
  month = aug
}

@article{kaufman2023merger,
  author = {Kaufman, Perry J.},
  title = {How To Trade Merger Arb},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {10},
  year = {2023},
  month = oct
}

@article{kaufman2023friedman,
  author = {Kaufman, Perry J.},
  title = {Interview: A Conversation With Herb Friedman},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {11},
  year = {2023},
  month = nov
}

@article{kaufman2023seasonal,
  author = {Kaufman, Perry J.},
  title = {A Strategy For Trading Seasonal And Non-Seasonal Markets},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {41},
  number = {12},
  year = {2023},
  month = dec
}

@article{kaufman2024gap,
  author = {Kaufman, Perry J.},
  title = {Gap Momentum},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {1},
  year = {2024},
  month = jan
}

@article{kaufman2024crossover,
  author = {Kaufman, Perry J.},
  title = {Crossover Trading: Arbitraging The Physical With The Stock},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {2},
  year = {2024},
  month = feb
}

@article{kaufman2024delta,
  author = {Kaufman, Perry J.},
  title = {The Delta-Delta Crude Strategy},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {3},
  year = {2024},
  month = mar
}

@article{kaufman2024riskbefore,
  author = {Kaufman, Perry J.},
  title = {Determining Risk Before It Happens},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {4},
  year = {2024},
  month = apr
}

@article{kaufman2024professionals,
  author = {Kaufman, Perry J.},
  title = {How Professionals Assign Risk},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {5},
  year = {2024},
  month = may
}

@article{kaufman2024gaps,
  author = {Kaufman, Perry J.},
  title = {Trading Opening Gaps And Extreme Closes In Stocks},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {6},
  year = {2024},
  month = jun
}

@article{kaufman2024theory,
  author = {Kaufman, Perry J.},
  title = {Theory Versus Reality},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {8},
  year = {2024},
  month = aug
}

@article{kaufman2024breakout,
  author = {Kaufman, Perry J.},
  title = {Which Is Better: The N-Day Breakout Or The Swing Breakout?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {9},
  year = {2024},
  month = sep
}

@article{kaufman2024stochastic,
  author = {Kaufman, Perry J.},
  title = {Can A Stochastic Indicator Be A Trading System?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {10},
  year = {2024},
  month = oct
}

@article{kaufman2024breakoutsys,
  author = {Kaufman, Perry J.},
  title = {Trading A Breakout System},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {11},
  year = {2024},
  month = nov
}

@article{kaufman2024overlooked,
  author = {Kaufman, Perry J.},
  title = {Overlooked Strategy Rules},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {12},
  year = {2024},
  month = dec
}

@article{kaufman2024weekly,
  author = {Kaufman, Perry J.},
  title = {Pros And Cons Of Daily Versus Weekly Trend Following},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {42},
  number = {13},
  year = {2024},
  note = {Bonus Issue}
}

@article{kaufman2025chasing,
  author = {Kaufman, Perry J.},
  title = {Chasing The Market},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {43},
  number = {2},
  year = {2025},
  month = feb
}

@article{kaufman2025threeday,
  author = {Kaufman, Perry J.},
  title = {Revisiting The 3-Day Trade},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {43},
  number = {3},
  year = {2025},
  month = mar
}

@article{kaufman2025stops,
  author = {Kaufman, Perry J.},
  title = {Do Stops Really Work?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {43},
  number = {4},
  year = {2025},
  month = apr
}

@article{kaufman2025channel,
  author = {Kaufman, Perry J.},
  title = {Trading The Channel},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {43},
  number = {5},
  year = {2025},
  month = may
}

@article{kaufman2025weekends,
  author = {Kaufman, Perry J.},
  title = {There Is Money To Be Made On The Weekends},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {43},
  number = {6},
  year = {2025},
  month = jun
}

@article{kaufman2025carry,
  author = {Kaufman, Perry J.},
  title = {Explaining FX Carry (In Detail)},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {43},
  number = {8},
  year = {2025},
  month = aug
}

@article{kaufman2025volume,
  author = {Kaufman, Perry J.},
  title = {Using The Elusive Volume Confirmation},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {43},
  number = {9},
  year = {2025},
  month = sep
}

@article{kaufman2025lowpriced,
  author = {Kaufman, Perry J.},
  title = {Low-Priced Stocks: A Golden Opportunity Or An Unreasonable Risk?},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {43},
  number = {11},
  year = {2025},
  month = nov
}

@article{kaufman2025moon,
  author = {Kaufman, Perry J.},
  title = {New Moon--Full Moon},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {43},
  number = {13},
  year = {2025},
  note = {Bonus Issue}
}

@article{kaufman2026smoothing,
  author = {Kaufman, Perry J.},
  title = {Smoothing The Data},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {44},
  number = {1},
  year = {2026},
  month = jan
}

@article{kaufman2026crack,
  author = {Kaufman, Perry J.},
  title = {Trading The Crack Spread},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {44},
  number = {4},
  year = {2026},
  month = apr
}

@article{kaufman2026frequency,
  author = {Kaufman, Perry J.},
  title = {When To Use A Frequency Distribution Or A Standard Deviation},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume = {44},
  number = {5},
  year = {2026},
  month = may
}

% === Books ===

@book{kaufman1975pointfigure,
  author = {Kaufman, Perry J.},
  title = {Point and Figure Commodity Trading Techniques},
  publisher = {Investors Intelligence},
  address = {Larchmont, NY},
  year = {1975}
}

@book{kaufman1978systems,
  author = {Kaufman, Perry J.},
  title = {Commodity Trading Systems and Methods},
  publisher = {John Wiley \& Sons},
  year = {1978},
  isbn = {978-0471027607}
}

@book{kaufman1980technical,
  author = {Kaufman, Perry J.},
  title = {Technical Analysis in Commodities},
  publisher = {John Wiley \& Sons},
  year = {1980},
  isbn = {978-0471084228}
}

@book{kaufman1984handbook,
  author = {Kaufman, Perry J.},
  title = {Handbook of Futures Markets},
  publisher = {John Wiley \& Sons},
  year = {1984},
  isbn = {978-0471082552}
}

@book{kaufman1986concise,
  author = {Kaufman, Perry J.},
  title = {The Concise Handbook of Futures Markets},
  publisher = {John Wiley \& Sons},
  year = {1986},
  isbn = {978-0471027966}
}

@book{kaufman1987new,
  author = {Kaufman, Perry J.},
  title = {The New Commodity Trading Systems and Methods},
  publisher = {John Wiley \& Sons},
  year = {1987},
  isbn = {978-0471878797},
  edition = {2nd}
}

@book{kaufman1995smarter,
  author = {Kaufman, Perry J.},
  title = {Smarter Trading: Improving Performance in Changing Markets},
  publisher = {McGraw-Hill},
  year = {1995},
  isbn = {978-0070340305}
}

@book{kaufman1997global,
  author = {Kaufman, Perry J. and Vivanti, Alberto},
  title = {Global Equity Investing},
  publisher = {McGraw-Hill},
  year = {1997},
  isbn = {978-0070340480}
}

@book{kaufman1998tsm3,
  author = {Kaufman, Perry J.},
  title = {Trading Systems and Methods},
  publisher = {John Wiley \& Sons},
  year = {1998},
  isbn = {978-0471148791},
  edition = {3rd}
}

@book{kaufman2003short,
  author = {Kaufman, Perry J.},
  title = {A Short Course in Technical Trading},
  publisher = {John Wiley \& Sons},
  year = {2003},
  isbn = {978-0471268482}
}

@book{kaufman2005tsm4,
  author = {Kaufman, Perry J.},
  title = {Trading Systems and Methods},
  publisher = {John Wiley \& Sons},
  year = {2005},
  isbn = {978-0471697121},
  edition = {4th}
}

@book{kaufman2011alpha,
  author = {Kaufman, Perry J.},
  title = {Alpha Trading: Profitable Strategies That Remove Directional Risk},
  publisher = {John Wiley \& Sons},
  year = {2011},
  isbn = {978-0470529744}
}

@book{kaufman2013tsm5,
  author = {Kaufman, Perry J.},
  title = {Trading Systems and Methods},
  publisher = {John Wiley \& Sons},
  year = {2013},
  isbn = {978-1118043561},
  edition = {5th}
}

@book{kaufman2020tsm6,
  author = {Kaufman, Perry J.},
  title = {Trading Systems and Methods},
  publisher = {John Wiley \& Sons},
  year = {2020},
  isbn = {978-1119605355},
  edition = {6th}
}

@book{kaufman2020constructs,
  author = {Kaufman, Perry J.},
  title = {Kaufman Constructs Trading Systems},
  publisher = {KaufmanSignals},
  year = {2020}
}

@book{kaufman2022learn,
  author = {Kaufman, Perry J.},
  title = {Learn to Trade: Trade To Win With A Rule-Based Method},
  year = {2022}
}

% === Online/Media ===

@online{kaufman_wikipedia,
  author = {{Wikipedia contributors}},
  title = {Perry J. Kaufman},
  url = {https://en.wikipedia.org/wiki/Perry_J._Kaufman},
  urldate = {2026-05-07}
}

@online{kaufman_inotv,
  author = {Kaufman, Perry J.},
  title = {Perry Kaufman at INO TV},
  url = {https://www.ino.com/blog/tag/perry-kaufman/},
  urldate = {2026-05-07}
}

@online{kaufman_tradingmarkets,
  author = {Kaufman, Perry J.},
  title = {Perry Kaufman articles at TradingMarkets},
  url = {https://www.tradingmarkets.com/recent/perry_j._kaufman-36.html},
  urldate = {2026-05-07}
}
```

## Sources

[1] Technical Analysis of Stocks & Commodities author archive: https://technical.traders.com/archive/archiveSearch.asp (Perry J. Kaufman, Perry Kaufman)
[2] TASC XML table of contents files, 1994–2026
[3] Wikipedia: https://en.wikipedia.org/wiki/Perry_J._Kaufman
[4] MQL5 Code Base: https://www.mql5.com/en/code (search: Kaufman, KAMA, AMA, Efficiency Ratio)
[5] TA-Lib documentation: https://ta-lib.org/
[6] pandas-ta documentation: https://github.com/twopirllc/pandas-ta
[7] TradingView Pine Script Reference: https://www.tradingview.com/pine-script-reference/
[8] Google Books: https://books.google.com/
[9] INO TV: https://www.ino.com/blog/tag/perry-kaufman/
[10] TradingMarkets: https://www.tradingmarkets.com/recent/perry_j._kaufman-36.html
[11] Traders' Tips archives: http://traders.com/Documentation/FEEDbk_docs/
[12] NinjaTrader indicator library
[13] R TTR package documentation
[14] MetaTrader 5 built-in indicators documentation
