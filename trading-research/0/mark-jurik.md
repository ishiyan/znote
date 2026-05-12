# Mark Jurik

## Biography

Mark Jurik is the founder of **Jurik Research**, established in **1988 in Silicon Valley**, specializing in proprietary, closed-source technical analysis indicators for financial markets. He specializes in data modeling and time series forecasting methods, with a background rooted in military signal processing — the company's own bio confirms: *"Now that the cold war is over, signal processing skills originally intended for military projects are now successfully applied to the commercial arena."*

Before entering finance, Jurik presented at Association of Old Crows (AOC) electronic warfare conferences (1987, 1990) and Lawrence Livermore Labs (1987). He published two IEEE conference papers (Compcon 1988, Asilomar 1989) on improved back-propagation algorithms. He created **"NeuroTapes"**, a 12-hour video course on neural networks (Ed-U-Tech Productions, 1989) that was sold worldwide for over a decade.

He has lectured at **28+ conferences and seminars** spanning IEEE, military ELINT, Stanford University, Market Technicians Association (Zurich, Denver, Chicago), and trading conferences. He wrote articles for *Futures* magazine, *Neurovest Journal* (later *Journal of Computational Intelligence in Finance*), *PC AI* magazine, and *AI in Finance*.

His flagship product, **JMA (Jurik Moving Average)**, is widely regarded as one of the smoothest and lowest-lag moving averages available. Unlike most indicator developers, Jurik kept all algorithms proprietary, distributed as compiled DLLs for platforms including TradeStation, NinjaTrader, MetaStock, AmiBroker, MultiCharts, MATLAB, and others. Customers span 70+ countries.

As of 2024, Jurik Research is **winding down** after 34 years of operation. The shopping cart has been removed and no future updates are expected.

---

## Books

| # | Title | Year | Publisher | ISBN | Pages | Link |
|---|-------|------|-----------|------|-------|------|
| 1 | Computerized Trading: Maximizing Day Trading and Overnight Profits | 1999 | New York Institute of Finance / Prentice Hall | 0-7352-0077-7 | 442 | [Google Books](https://books.google.com/books/about/Computerized_Trading.html?id=JdgpAQAAMAAJ) |
| 2 | Neural Networks & Financial Forecasting | 1995 | Jurik Research (self-published) | — | — | [Google Books](https://books.google.com/books/about/Neural_Networks_Financial_Forecasting.html?id=7fHkPgAACAAJ) |

### Computerized Trading (1999)

Edited by Jurik with 20 contributing authors (DiNapoli, Kiev, Kase, Katz, and others). Covers designing/testing/analyzing trading strategies, risk control, neural networks, genetic algorithms, and data modeling. Jurik authored two appendices: "Finding the Best Data" and "Books, Consultants, Software." Cited by 11 on Google Scholar.

### Neural Networks & Financial Forecasting (1995)

A bound collection of ~15 published and unpublished technical reports by Jurik Research. Includes:
- "Wall Street Forecast with a Neural Network"
- "Consumer Guide to Software for Smart Forecasting"
- "Indicator Development Issues in the Space Domain"
- Reports on chaos analysis, backpercolation algorithm, training performance
- Application notes on phase in crossover MAs and adaptive moving averages

OCLC: 258096428. Available only from Jurik Research (not in bookstores).

### Chapter Contributions

| Title | Book | Year | Publisher |
|-------|------|------|-----------|
| On Creating Optimal Indicators for Trading | *Virtual Trading* | 1994 | Probus Publishing |

---

## Complete Publications List

| # | Title | Venue | Year |
|---|-------|-------|------|
| 1 | Neural Nets on a Personal Computer | *PC AI Magazine* | Nov 1988 |
| 2 | Back Error Propagation: a Critique | *IEEE Compcon* | Spring 1988 |
| 3 | NeuroTapes (12-hour video course) | Ed-U-Tech Productions | 1989 |
| 4 | Improved Back-Propagation Algorithms | *IEEE Conference on Parallel Processing*, Asilomar CA | 1989 |
| 5 | Introduction to a Neural Network Algorithm | *AOC Electronic Warfare*, tech issue #90-10 | 1990 |
| 6 | Wall Street Forecasting with a Neural Network | BrainCel user manual appendix | 1991 |
| 7 | Going Fishing with a Neural Network | *Futures Magazine* | Sep 1992 |
| 8 | The Care and Feeding of a Neural Network | *Futures Magazine* | Oct 1992 |
| 9 | Consumer's Guide to Neural Networks | *Futures Magazine* | Jul 1993 |
| 10 | Using Chaos Analysis to Predict the Optimal Forecast Distance | *Neurovest Journal* | Jan 1993 |
| 11 | A Primer on Market Forecasting with Neural Networks, Part 1 | *Neurovest Journal* | Sep 1993 |
| 12 | A Method for Determining Optimal Performance Error in Neural Nets | *Neurovest Journal* | Mar 1994 |
| 13 | On Creating Optimal Indicators for Trading | *Virtual Trading* (book chapter) | Nov 1994 |
| 14 | On Creating Optimal Indicators for Trading | *AI in Finance* | Spring 1995 |
| 15 | Neural Networks & Financial Forecasting (bound collection) | Jurik Research | 1995 |
| 16 | Computerized Trading (editor) | Prentice Hall | 1999 |
| 17 | Finding the Best Data (appendix) | *Computerized Trading* | 1999 |

---

## Technical Indicators & Tools

All indicators are **proprietary and closed-source**, distributed as compiled DLLs. No patents were found — the algorithms are trade secrets, not patent-protected.

### Core Indicators

| Indicator | First Published | Category | Description |
|-----------|----------------|----------|-------------|
| JMA (Jurik Moving Average) | ~1996, Jurik Research | Adaptive MA | Flagship product. Proprietary adaptive moving average with superior smoothness and low lag. Remains benchmark for noise reduction filters. |
| VEL (Jurik Velocity) | ~1996, Jurik Research | Oscillator | Noise-free market velocity/momentum. Replaces classic momentum (MOM). Ideal for divergence analysis. |
| RSX (Relative Strength Quality Index) | ~2000, Jurik Research | Oscillator | Noise-free replacement for RSI. Retains speed, direction, and trend uniformity without jitter or added lag. |
| DMX (Jurik DMX) | ~1998, Jurik Research | Trend | Enhanced DMI reformulated as bounded bipolar oscillator. Embeds JMA for smoothness without additional lag. |
| CFB (Composite Fractal Behavior) | ~1997, Jurik Research | Trend | Measures how long the market has been in a quality trend using fractal analysis. |
| JCF (Jurik Composite Filter) | ~2000, Jurik Research | Filter | Composite filtering tool. |

### Notes on Attribution

1. **Community reverse-engineering**: The MQL4/MQL5 community has extensively attempted to replicate JMA behavior. The file `jma.mq4` circulated widely, with users questioning whether it truly replicates the proprietary algorithm.
2. **Open-source approximations**: Nikolay Kositsin (GODZILLA on MQL5) created "JMA adaptive average" using `SmoothAlgorithms.mqh`. Described as approximations, not exact replications.
3. **Mladen Rakic's implementations**: Dozens of indicators incorporating "Jurik smoothing" — explicitly noted as "not developed by Mark Jurik" but using similar theoretical foundations.
4. **Jurik Volty**: The adaptive volatility component of JMA has been extracted and used independently as a standalone indicator.
5. **Verification**: Jurik's website historically provided an Excel file with reference JMA outputs against 16 test signals, allowing users to verify clone implementations.
6. **No patents found**: Despite claims in forum discussions, no US patents were found under inventor "Mark Jurik" on Google Patents.

---

## TASC Publications

**Mark Jurik has no articles published in Technical Analysis of Stocks & Commodities (TASC).** The complete author list was searched — no match. He published primarily in *Futures* magazine and *Neurovest Journal*. However, his indicators are frequently referenced by other TASC authors, and John Ehlers explicitly references "Mark Jurik's commercial filters" in his 2010 TASC article "Zero Lag (Well, Almost)."

---

## MQL5 Implementations

The MQL5/MQL4 codebase contains **100+ implementations** referencing Jurik/JMA. Key entries:

### Core Implementations

| Title | Author | Platform | URL |
|-------|--------|----------|-----|
| JMA | Scriptor (orig. Spiggy) | MT4 | https://www.mql5.com/en/code/7307 |
| JMA adaptive average | Nikolay Kositsin | MT5 | https://www.mql5.com/en/code/427 |
| Jurik Velocity | Mladen Rakic | MT5 | https://www.mql5.com/en/code/16750 |
| Jurik Filter | Mladen Rakic | MT5 | https://www.mql5.com/en/code/16638 |
| Fractal Dimension - Jurik | Mladen Rakic | MT5 | https://www.mql5.com/en/code/20587 |
| Jurik Volty | Mladen Rakic | MT5 | https://www.mql5.com/en/code/21229 |
| RSX of RSX | Mladen Rakic | MT5 | https://www.mql5.com/en/code/22404 |
| Bollinger Bands rev. by Jurik | Federico Costalonga | MT4 | https://www.mql5.com/en/code/8988 |

### JMA-Based Derivatives (by Mladen Rakic, all MT5)

| Title | URL |
|-------|-----|
| Multi JMA Slopes | https://www.mql5.com/en/code/21599 |
| JMA Keltner Channel | https://www.mql5.com/en/code/21692 |
| JMA TRIX Log | https://www.mql5.com/en/code/21735 |
| BB Stops JMA | https://www.mql5.com/en/code/21761 |
| iTrend JMA | https://www.mql5.com/en/code/21835 |
| Corrected JMA | https://www.mql5.com/en/code/22020 |
| ATR adaptive JMA | https://www.mql5.com/en/code/22411 |
| JMA Z-score | https://www.mql5.com/en/code/22432 |
| RSX range expansion index | https://www.mql5.com/en/code/22376 |
| Schaff Trend Cycle - Jurik Volty Adaptive RSX | https://www.mql5.com/en/code/21237 |
| T3 Velocity | https://www.mql5.com/en/code/16765 |
| Trend Strength - Jurik smoothed RSI | https://www.mql5.com/en/code/20747 |

### Community & Reverse Engineering (MQL5 Forum)

The MQL5 forum contains **152 threads** mentioning "JMA Jurik":

| Thread | URL | Topic |
|--------|-----|-------|
| JMA - Jurik Moving Average | https://www.mql5.com/en/forum/366338 | Community JMA implementation by Mohammad Saket |
| JMA Jurik | https://www.mql5.com/en/forum/44389 | Early (2005) request for JMA in MQL4 |
| Jurik (AugustLeo) | https://www.mql5.com/en/forum/173010 | Authenticity debate — does jma.mq4 match Jurik's test vectors? |

---

## GitHub Repositories

### Dedicated Repositories

| Repository | Stars | Language | Description |
|------------|-------|----------|-------------|
| [romulodl/jma](https://github.com/romulodl/jma) | 13 | PHP | Jurik Moving Average implementation |
| [snehghetia/JMAStrategy](https://github.com/snehghetia/JMAStrategy) | 0 | Python | Bitcoin Trading Bot using JMA and machine learning for buy/sell signals with backtesting |

### Libraries Including JMA

| Repository | Stars | Language | Indicator(s) | Notes |
|------------|-------|----------|---------------|-------|
| [twopirllc/pandas_ta](https://github.com/twopirllc/pandas_ta) | 5.2k+ | Python | JMA | Popular TA library with 130+ indicators; includes JMA in overlap category |
| [xgboosted/pandas-ta-classic](https://github.com/xgboosted/pandas-ta-classic) | 310 | Python | JMA | Fork/continuation of pandas_ta with 200+ indicators |

### Notes

- GitHub presence for Jurik indicators is limited compared to forum/MQL5 presence — most implementations remain in MQL4/MQL5 CodeBase and TradingView Pine Script
- No Rust, Go, Zig, or TypeScript implementations found as dedicated repos
- The `pandas_ta` library's JMA implementation is the most widely used open-source version in Python

---

## Forum Discussions

Mark Jurik has significant forum presence — his indicators are among the most discussed proprietary tools in trading.

### ForexFactory

| Thread | Description |
|--------|-------------|
| [Jurik indicators](https://www.forexfactory.com/thread/jurik-indicators) | 25+ page mega-thread. MT4/MT5 implementations by Mladen (JMA MACD, JMA PPO, Gann HiLo Activator JMA, DMX histograms). Discusses JMA as "price proxy" and optimal settings. |
| [Jurik Moving Average](https://www.forexfactory.com/thread/jurik-moving-average) | 2006 comparison with Hull MA. Consensus: HMA is closest free alternative. |
| [6 Less Lagging MAs + 2 New MA Indicators](https://www.forexfactory.com/thread/6-less-lagging-moving-averages-2-new-ma-indicators) | "Double Jurik MA" by Mladen (later renamed "Double Smoother" — not genuine JMA). |

### futures.io

| Thread | Description |
|--------|-------------|
| [Opinion on Jurik indicators](https://futures.io/trading-reviews-vendors/41007-opinion-jurik-indicators.html) | User reviews. Key advice: use JMA as "price proxy" — substitute JMA(close,3,0) for raw close. |
| [Jurik Research Indicators](https://futures.io/trading-reviews-vendors/20366-jurik-research-indicators-www-jurikres-com.html) | 2012 vendor review thread. |
| [JMA modification](https://futures.io/tradestation/30042-jma-modification.html) | Discussion of Kositsin's open-source JMA approximation from FXCodeBase. |
| [JMA in Indicator?](https://futures.io/ninjatrader-programming/988-jma-indicator.html) | NinjaTrader JMA integration. |

### Elite Trader

| Thread | Description |
|--------|-------------|
| [Why are quants afraid of Mark Jurik?](https://www.elitetrader.com/et/threads/why-are-quants-afraid-of-mark-jurik.209408/) | 8+ page debate (2010) on Jurik's credibility, patents claims, and blackbox criticism. |
| [Jurik Adaptive MAs and Adaptive MAs in general](https://www.elitetrader.com/et/threads/jurik-adaptive-moving-averages-and-adaptive-moving-averages-in-general.243113/) | JMA vs. Precision Trading PLA comparison. |
| [Jurik RSX, MESA Ehlers, Regression — all in one](https://www.elitetrader.com/et/threads/jurik-rsx-mesa-ehlers-regression-linear-quadratic-logarithmic-exponential-all-in-one.323028/) | RSX vs. MESA Ehlers vs. regression methods. |
| [Jurik JMA](https://www.elitetrader.com/et/threads/jurik-jma.20338/) | Early thread discussing military/radar origins. |
| [Jurik RSX](https://www.elitetrader.com/et/threads/jurik-rsx.234717/) | Seeking free RSX alternatives (2012). |
| [JMA Clone to Amibroker](https://www.elitetrader.com/et/threads/translate-net-jurik-moving-average-jma-clone-to-amibroker.81823/) | Porting .NET JMA clone to Amibroker. |

### NinjaTrader Forum

| Thread | Description |
|--------|-------------|
| [Jurik MA](https://forum.ninjatrader.com/forum/ninjatrader-7/indicator-development-aa/48283-jurik-ma) | Technical support for JurikJMA in NinjaTrader 7. |
| [Have any traders used the Jurik Indicators?](https://forum.ninjatrader.com/forum/ninjatrader-7/platform-technical-support/49005-have-any-traders-used-the-jurik-indicators) | Positive user testimonials. |
| [Indicator similar to Jurik RSX](https://forum.ninjatrader.com/forum/ninjatrader-7/indicator-development-aa/17736-indicator-similar-to-jurik-rsx) | RSX alternatives. Quote: "90+% of third party indicators are trash... Jurik is the rare exception." |
| [Quick MA an alternative to Jurik MA](https://forum.ninjatrader.com/forum/ninjatrader-7/indicator-development-aa/12596-quick-ma-an-alternative-to-juirk-ma) | Visual comparison with screenshots. |
| [Jurik Moving Average (JMA)](https://forum.ninjatrader.com/forum/ninjascript-file-sharing/user-app-submission/1343575-jurik-moving-average-jma) | Downloadable JMA implementation. |

### TradingView

| Thread | Description |
|--------|-------------|
| [Jurik Moving Average — scripts tag](https://www.tradingview.com/scripts/jurikmovingaverage/) | Numerous Pine Script JMA implementations and derivatives. |

### Other Forums

| Forum | Result |
|-------|--------|
| Wealth-Lab | 0 results |
| Quant Stack Exchange | 0 results |
| r/algotrading | 2 threads: RSX C# implementation help; Dickson MA (JMA approximation with EasyLanguage code) |
| Trade2Win | 3 threads: Jurik UT review, early 2004 discussion, JMA recommended as "developed to track missiles" |

---

## Academic Papers

Mark Jurik published two IEEE conference papers in the late 1980s, before transitioning fully to financial applications:

| Title | Venue | Year |
|-------|-------|------|
| Back Error Propagation: a Critique | IEEE Compcon | Spring 1988 |
| Improved Back-Propagation Algorithms: a Systems Control and Identification Approach | IEEE Conference on Parallel Processing, Asilomar CA | 1989 |

### Papers Citing Jurik / JMA (third-party)

| Authors | Title | Venue | Year | Citations |
|---------|-------|-------|------|-----------|
| Raudys, Lenčiauskas, Malčius | Moving averages for financial data smoothing | ICIST, Springer | 2013 | 94 |
| Iacomin | Stock market prediction | IEEE ICSTCC | 2015 | 45 |
| Ehlers & Way | Zero Lag (Well, Almost) | TASC | 2010 | 13 |
| Trigo & Costanzo | Redes neuronales en la predicción... | El trimestre económico | 2007 | 10 |
| Benenati | Neuronale Netze im Portfoliomanagement | Springer | 1998 | 8 |

### Patents

**No patents found** under inventor "Mark Jurik" on Google Patents. His algorithms are trade secrets, not patent-protected.

---

## Conference Presentations (28+ documented)

| Venue | Year(s) |
|-------|---------|
| AOC (military ELINT) AI conference | 1987 |
| Lawrence Livermore Labs | 1987 |
| San Francisco Bay Area AI forum | 1987, 88, 90 |
| IEEE Information Theory Society | 1988 |
| IEEE Acoustic, Speech and Signal Processing Society | 1988 |
| IEEE Compcon | 1988 |
| IEEE Asilomar Microcomputer workshop | 1988, 90, 91 |
| Santa Clara University AI SIG | 1988 |
| University California Extension (10-lecture series) | 1987–91 |
| IEEE Videoconference: Neural Networks Capabilities | 1989 |
| Neural Nets for the Real World, Conference | 1989 |
| AOC (military ELINT) Technical Symposium | 1990 |
| AOC (military ELINT) International Conference | 1990 |
| IEEE Wescon | 1990, 93 |
| Neural Network Conference, Germany | 1990 |
| Stanford University Computer Science Forum | 1991 |
| IEEE SIG Group: AI and Finance | 1994 |
| Futures West International Conference | 1995 |
| Omega World '99 (Investor's Conference) | 1999 |
| MTA (Market Technicians Association, Zurich) | 2000 |
| MTA (Market Technicians Association, Denver) | 2001 |
| MTA (Market Technicians Association, Chicago) | 2001 |

---

## Photos, Videos & Interviews

### Photos

| Description | URL | Source |
|-------------|-----|--------|
| Portrait of Mark Jurik (Wayback Machine 2003) | https://web.archive.org/web/20031204191155im_/http://www.jurikres.com/gifs/port_1e.gif | jurikres.com company page |
| [URL not found] No YouTube photos/videos found | — | YouTube |
| [URL not found] No LinkedIn public profile confirmed | — | LinkedIn |

### Videos

| Title | URL | Duration | Date |
|-------|-----|----------|------|
| NeuroTapes — 12-hour video course on neural networks | [URL not found] — sold by mail order, no online copies | 12 hours | 1989 |
| [URL not found] No YouTube videos found | — | — | — |

### Audio Seminars

| Title | URL | Date |
|-------|-----|------|
| Space, Time, Cycles and Phase — audio recording + lecture notes from 1995 Futures International Conference | https://web.archive.org/web/20060110195239/http://www.jurikres.com/catalog/cat_pub.htm | 1995 |

### Interviews & Podcasts

No published interviews or podcast appearances found.

---

## BibTeX

```bibtex
@book{jurik1999computerized,
  author    = {Jurik, Mark},
  title     = {Computerized Trading: Maximizing Day Trading and Overnight Profits},
  publisher = {New York Institute of Finance / Prentice Hall},
  year      = {1999},
  pages     = {442},
  isbn      = {0735200777},
  note      = {Editor; 20 contributing authors including DiNapoli, Kiev, Kase, Katz},
  url       = {https://books.google.com/books/about/Computerized_Trading.html?id=JdgpAQAAMAAJ}
}

@book{jurik1995neuralfinancial,
  author    = {Jurik, Mark},
  title     = {Neural Networks \& Financial Forecasting: Published and Unpublished Technical Reports},
  publisher = {Jurik Research},
  year      = {1995},
  note      = {Self-published bound collection, OCLC:258096428},
  url       = {https://books.google.com/books/about/Neural_Networks_Financial_Forecasting.html?id=7fHkPgAACAAJ}
}

@inproceedings{jurik1988backprop,
  author    = {Jurik, Mark},
  title     = {Back Error Propagation: A Critique},
  booktitle = {IEEE Compcon},
  year      = {1988},
  note      = {Spring 1988}
}

@inproceedings{jurik1989improved,
  author    = {Jurik, Mark},
  title     = {Improved Back-Propagation Algorithms: A Systems Control and Identification Approach},
  booktitle = {IEEE Conference on Parallel Processing},
  year      = {1989},
  address   = {Asilomar, CA}
}

@article{jurik1988pcai,
  author  = {Jurik, Mark},
  title   = {Neural Nets on a Personal Computer},
  journal = {PC AI Magazine},
  year    = {1988},
  month   = nov
}

@article{jurik1992fishing,
  author  = {Jurik, Mark},
  title   = {Going Fishing with a Neural Network},
  journal = {Futures Magazine},
  year    = {1992},
  month   = sep
}

@article{jurik1992care,
  author  = {Jurik, Mark},
  title   = {The Care and Feeding of a Neural Network},
  journal = {Futures Magazine},
  year    = {1992},
  month   = oct
}

@article{jurik1993consumer,
  author  = {Jurik, Mark},
  title   = {Consumer's Guide to Neural Networks},
  journal = {Futures Magazine},
  year    = {1993},
  month   = jul
}

@article{jurik1993chaos,
  author  = {Jurik, Mark},
  title   = {Using Chaos Analysis to Predict the Optimal Forecast Distance},
  journal = {Neurovest Journal},
  year    = {1993},
  month   = jan
}

@article{jurik1993primer,
  author  = {Jurik, Mark},
  title   = {A Primer on Market Forecasting with Neural Networks, Part 1},
  journal = {Neurovest Journal},
  year    = {1993},
  month   = sep
}

@article{jurik1994optimal,
  author  = {Jurik, Mark},
  title   = {A Method for Determining Optimal Performance Error in Neural Nets},
  journal = {Neurovest Journal},
  year    = {1994},
  month   = mar
}

@incollection{jurik1994virtualtrading,
  author    = {Jurik, Mark},
  title     = {On Creating Optimal Indicators for Trading},
  booktitle = {Virtual Trading},
  publisher = {Probus Publishing},
  year      = {1994}
}

@article{jurik1995aifinance,
  author  = {Jurik, Mark},
  title   = {On Creating Optimal Indicators for Trading},
  journal = {AI in Finance},
  publisher = {Miller Freeman},
  year    = {1995},
  note    = {Spring 1995}
}

@article{jurik1990aoc,
  author  = {Jurik, Mark},
  title   = {Introduction to a Neural Network Algorithm},
  journal = {Association of Old Crows Electronic Warfare},
  year    = {1990},
  note    = {Tech issue \#90-10, Alexandria, VA}
}

@misc{jurik1989neurotapes,
  author  = {Jurik, Mark},
  title   = {NeuroTapes: Video-Tutorial Course on Neural Network Technology},
  year    = {1989},
  publisher = {Ed-U-Tech Productions},
  address = {Aptos, CA},
  note    = {12-hour video course, sold worldwide for over a decade}
}

@misc{jurik1995spacetime,
  author  = {Jurik, Mark},
  title   = {Space, Time, Cycles and Phase},
  year    = {1995},
  note    = {Audio seminar from 1995 Futures International Conference},
  url     = {https://web.archive.org/web/20060110195239/http://www.jurikres.com/catalog/cat_pub.htm}
}

@online{jurikresearch,
  author       = {{Jurik Research}},
  title        = {Jurik Research --- Technical Analysis Tools},
  url          = {https://www.jurikres.com},
  urldate      = {2026-05-10},
  note         = {Commercial proprietary indicators: JMA, VEL, CFB, DMX, RSX, JCF. Founded 1988, winding down 2024.}
}

@online{jurik2003portrait,
  author       = {{Jurik Research}},
  title        = {Portrait of Mark Jurik},
  url          = {https://web.archive.org/web/20031204191155im_/http://www.jurikres.com/gifs/port_1e.gif},
  urldate      = {2026-05-10},
  note         = {Accessed via Wayback Machine}
}

@online{jurik2003company,
  author       = {{Jurik Research}},
  title        = {About Jurik Research --- Company Profile},
  url          = {https://web.archive.org/web/20031204191155/http://jurikres.com/about/company.htm},
  urldate      = {2026-05-10},
  note         = {Confirms military signal processing origins}
}

@online{mql5_jma_spiggy,
  author       = {{Scriptor (orig. Spiggy)}},
  title        = {JMA},
  url          = {https://www.mql5.com/en/code/7307},
  urldate      = {2026-05-10},
  note         = {MQL4 Code Base -- widely circulated JMA clone}
}

@online{mql5_jma_kositsin,
  author       = {Kositsin, Nikolay},
  title        = {JMA adaptive average},
  url          = {https://www.mql5.com/en/code/427},
  urldate      = {2026-05-10},
  note         = {MQL5 Code Base -- JMA approximation using SmoothAlgorithms.mqh}
}

@online{mql5_jurik_volty,
  author       = {Rakic, Mladen},
  title        = {Jurik Volty},
  url          = {https://www.mql5.com/en/code/21229},
  urldate      = {2026-05-10},
  note         = {MQL5 Code Base -- extracted adaptive volatility component of JMA}
}

@online{mql5_rsx_of_rsx,
  author       = {Rakic, Mladen},
  title        = {RSX of RSX},
  url          = {https://www.mql5.com/en/code/22404},
  urldate      = {2026-05-10},
  note         = {MQL5 Code Base -- based on Mark Jurik's idea of applying RSX to RSX}
}

@online{mql5_fractal_dimension_jurik,
  author       = {Rakic, Mladen},
  title        = {Fractal Dimension - Jurik},
  url          = {https://www.mql5.com/en/code/20587},
  urldate      = {2026-05-10},
  note         = {MQL5 Code Base -- Mark Jurik's version of fractal dimension}
}

@online{forexfactory_jurik_indicators,
  title        = {Jurik indicators},
  url          = {https://www.forexfactory.com/thread/jurik-indicators},
  urldate      = {2026-05-10},
  note         = {ForexFactory Platform Tech, 25+ pages}
}

@online{elitetrader_quants_afraid_jurik,
  title        = {Why are quants afraid of Mark Jurik?},
  url          = {https://www.elitetrader.com/et/threads/why-are-quants-afraid-of-mark-jurik.209408/},
  urldate      = {2026-05-10},
  note         = {Elite Trader, 8+ page debate on Jurik's credibility and patents claims}
}

@online{github_romulodl_jma,
  author       = {romulodl},
  title        = {jma --- Jurik Moving Average},
  url          = {https://github.com/romulodl/jma},
  urldate      = {2026-05-10},
  note         = {GitHub repository, 13 stars, PHP},
}

@online{github_snehghetia_jmastrategy,
  author       = {snehghetia},
  title        = {JMAStrategy --- Bitcoin Trading Bot using JMA and ML},
  url          = {https://github.com/snehghetia/JMAStrategy},
  urldate      = {2026-05-10},
  note         = {GitHub repository, Python},
}

@online{github_twopirllc_pandas_ta,
  author       = {twopirllc},
  title        = {pandas\_ta --- Technical Analysis Indicators for Pandas},
  url          = {https://github.com/twopirllc/pandas_ta},
  urldate      = {2026-05-10},
  note         = {GitHub repository, 5200+ stars, Python; includes JMA implementation},
}

@online{tradingview_jma_scripts,
  title        = {Jurik Moving Average --- Indicators and Strategies},
  url          = {https://www.tradingview.com/scripts/jurikmovingaverage/},
  urldate      = {2026-05-10},
  note         = {TradingView tag page with numerous Pine Script JMA implementations}
}

@inproceedings{raudys2013moving,
  author    = {Raudys, Aistis and Len\v{c}iauskas, Vaidotas and Mal\v{c}ius, Edmundas},
  title     = {Moving Averages for Financial Data Smoothing},
  booktitle = {International Conference on Information and Software Technologies},
  publisher = {Springer},
  year      = {2013},
  note      = {Cited by 94; mentions JMA as proprietary}
}

@article{ehlers2010zerolag,
  author  = {Ehlers, John F. and Way, Ric},
  title   = {Zero Lag (Well, Almost)},
  journal = {Technical Analysis of Stocks and Commodities},
  year    = {2010},
  note    = {Cited by 13; references Mark Jurik's commercial filters}
}

@inproceedings{iacomin2015stock,
  author    = {Iacomin, R.},
  title     = {Stock Market Prediction},
  booktitle = {19th International Conference on System Theory, Control and Computing (ICSTCC)},
  publisher = {IEEE},
  year      = {2015},
  note      = {Cited by 45; references JMA}
}
```
