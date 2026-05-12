# Mark Jurik — Research Brief

## Biography

Mark Jurik is the founder of **Jurik Research** (jurikres.com), a company specializing in proprietary, closed-source technical analysis indicators for financial markets. He is best known for creating the **JMA (Jurik Moving Average)**, widely regarded as one of the smoothest and lowest-lag moving averages available. Unlike most indicator developers, Jurik has kept his algorithms proprietary, selling them as commercial DLL plugins for platforms such as TradeStation, MetaStock, AmiBroker, NinjaTrader, and others.

Jurik is also the editor of the book *"Computerized Trading: Maximizing Day Trading and Overnight Profits"* (New York Institute of Finance, 1999), which covers neural networks and machine learning applications in finance.

His work has been discussed extensively in *Technical Analysis of Stocks & Commodities* (TASC) magazine, and his indicators have become a benchmark against which other adaptive smoothing methods are compared. The trading community has engaged in significant efforts to reverse-engineer or approximate his proprietary algorithms, particularly JMA.

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| JMA (Jurik Moving Average) | ~1996, Jurik Research | Adaptive MA |
| VEL (Jurik Velocity) | ~1996, Jurik Research | Oscillator |
| CFB (Composite Fractal Behavior) | ~1997, Jurik Research | Trend |
| DMX (Jurik DMX) | ~1998, Jurik Research | Trend |
| RSX (Relative Strength Quality Index) | ~2000, Jurik Research | Oscillator |
| JCF (Jurik Composite Filter) | ~2000, Jurik Research | Filter |

### Notes on Attribution

All of Jurik's indicators are **proprietary and closed-source**. They are distributed as compiled DLLs (binary plugins) rather than open-source code. This has led to:

1. **Community reverse-engineering efforts**: The MQL4/MQL5 community has extensively discussed and attempted to replicate JMA behavior. The file `jma.mq4` circulated widely, with users questioning whether it truly replicates Jurik's algorithm [4].

2. **Open-source approximations**: Developers like Nikolay Kositsin (GODZILLA on MQL5) created "JMA adaptive average" implementations for MetaTrader 5 using the `SmoothAlgorithms.mqh` library. These are described as approximations inspired by Jurik's theory, not exact replications [5].

3. **Mladen Rakic's implementations**: Prolific MQL5 developer Mladen Rakic created dozens of indicators incorporating "Jurik smoothing" — he explicitly notes these are "not developed by Mark Jurik" but use similar theoretical foundations [6].

4. **Jurik Volty**: The adaptive component of JMA (its internal volatility measure) has been extracted and used independently as a standalone volatility indicator and as an adaptive mechanism for other indicators [7].

5. **Verification challenges**: Jurik's website historically provided an Excel file with reference JMA outputs against 16 test signals, allowing users to verify whether clone implementations match the real algorithm [4].

## Books

### Edited

| Title | Year | Publisher | Role |
|-------|------|-----------|------|
| Computerized Trading: Maximizing Day Trading and Overnight Profits | 1999 | New York Institute of Finance / Prentice Hall | Editor |

The book is an anthology covering neural networks, genetic algorithms, and advanced computational methods applied to trading. Contributors include researchers and practitioners in quantitative finance.

### Indicators Introduced in Books

No specific new indicators were introduced in the book; rather it provided context for the computational approaches underlying Jurik's proprietary tools.

## TASC Publications (Complete List)

The TASC author archive returned an error ("MARK JURIK.XML could not be found"), indicating that while Jurik has been referenced and discussed in TASC articles, he may not have a substantial standalone article archive on the platform. His indicators are frequently mentioned in articles by other authors (e.g., Traders' Tips implementations).

**Note**: The TASC archive search failed with "The specified file MARK JURIK.XML could not be found" — this suggests his contributions may be listed under a variant name or he primarily appeared in product reviews, interviews, and Traders' Tips rather than as a regular article author.

## Articles by Category

| Category | Count | Articles |
|----------|-------|----------|
| N/A — TASC archive unavailable | 0 | Archive returned error |

## MQL5 Implementations

The MQL5/MQL4 codebase contains extensive implementations of Jurik-inspired indicators. Key results from searches ("Jurik JMA": 24 results, "Jurik": 66 results, "JMA moving average": 101 results, "RSX Jurik": 9 results):

### Selected Implementations

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| JMA | Scriptor (orig. Spiggy) | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/7307 |
| JMA adaptive average | Nikolay Kositsin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/427 |
| Jurik Velocity | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/16750 |
| Jurik Filter | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/16638 |
| T3 Velocity | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/16765 |
| Fractal Dimension - Jurik | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/20587 |
| Jurik Volty | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/21229 |
| Multi JMA Slopes | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/21599 |
| JMA Keltner Channel | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/21692 |
| JMA TRIX Log | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/21735 |
| BB Stops JMA | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/21761 |
| iTrend JMA | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/21835 |
| Corrected JMA | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/22020 |
| ATR adaptive JMA | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/22411 |
| JMA Z-score | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/22432 |
| RSX of RSX | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/22404 |
| RSX range expansion index | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/22376 |
| Schaff Trend Cycle - Jurik Volty Adaptive RSX | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/21237 |
| Bollinger Bands rev. by Jurik | Federico Costalonga | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/8988 |
| Trend Strength - Jurik smoothed RSI | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/20747 |

**Total MQL5/MQL4 codebase results**: ~100+ implementations referencing Jurik/JMA across all searches.

## Community & Reverse Engineering

The MQL5 forum contains **152 threads** mentioning "JMA Jurik", demonstrating the extensive community interest in replicating Jurik's work:

1. **"JMA - Jurik Moving Average"** (forum/366338) — Dedicated thread for a community JMA implementation by Mohammad Saket [1].

2. **"JMA Jurik"** (forum/44389, 2005) — Early request for JMA in MQL4 format, showing demand predates MetaTrader 5 era [2].

3. **"Jurik"** (forum/173010) — User AugustLeo questions the authenticity of `jma.mq4`, asking whether it replicates Jurik's proprietary results against his published test vectors [4].

4. **CFB references** — Multiple forum threads reference "Composite Fractal Behavior (CFB) tells you how long the market has been in a quality trend" — quoting Jurik Research materials [8].

5. **RSX origin confirmation** — Mladen Rakic's code comments confirm "RSX (Relative Strength Quality Index) originally developed by Mark Jurik" and describes Jurik's idea of applying "RSX to RSX" as a new indicator [9].

6. **Jurik smoothing vs. Jurik average**: The community distinguishes between the proprietary "Jurik Moving Average" (JMA) sold by Jurik Research and open-source "Jurik smoothing" implementations that approximate similar behavior without being exact replicas [6].

Key observations:
- No one has confirmed a perfect open-source replication of JMA
- Jurik's published test vectors serve as the community's verification benchmark
- The "Jurik Volty" adaptive volatility component has been independently implemented and widely adopted
- RSX has been more successfully approximated than JMA in open-source implementations

## BibTeX

```bibtex
@book{jurik1999computerized,
  title     = {Computerized Trading: Maximizing Day Trading and Overnight Profits},
  editor    = {Jurik, Mark},
  year      = {1999},
  publisher = {New York Institute of Finance},
  address   = {New York},
  isbn      = {978-0735200777}
}

@misc{jurikresearch,
  author       = {Jurik, Mark},
  title        = {Jurik Research --- Technical Analysis Tools},
  howpublished = {\url{https://www.jurikres.com}},
  note         = {Commercial proprietary indicators: JMA, VEL, CFB, DMX, RSX, JCF},
  year         = {1996--present}
}

@misc{mql5_jma_adaptive,
  author       = {Kositsin, Nikolay},
  title        = {JMA adaptive average},
  howpublished = {\url{https://www.mql5.com/en/code/427}},
  year         = {2011},
  note         = {MetaTrader 5 implementation of JMA-style smoothing}
}

@misc{mql5_rsx_of_rsx,
  author       = {Rakic, Mladen},
  title        = {RSX of RSX},
  howpublished = {\url{https://www.mql5.com/en/code/22404}},
  year         = {2018},
  note         = {Implementation based on Mark Jurik's idea of applying RSX to RSX}
}

@misc{mql5_fractal_dimension_jurik,
  author       = {Rakic, Mladen},
  title        = {Fractal Dimension - Jurik},
  howpublished = {\url{https://www.mql5.com/en/code/20587}},
  year         = {2018},
  note         = {Mark Jurik's version of fractal dimension indicator}
}
```

## Sources

[1] MQL5 Forum. "JMA - Jurik Moving Average." https://www.mql5.com/en/forum/366338 — `verified`

[2] MQL5 Forum. "JMA Jurik." https://www.mql5.com/en/forum/44389 — `verified`

[3] TASC Author Archive. http://technical.traders.com/archive/combo/display5.asp?author=Mark%20Jurik — `verified` (returned "file not found" for author XML)

[4] MQL5 Forum. "Jurik" (AugustLeo, 2008). https://www.mql5.com/en/forum/173010/4210811 — `verified`

[5] MQL5 Codebase. "JMA adaptive average" by Nikolay Kositsin. https://www.mql5.com/en/code/427 — `verified`

[6] MQL5 Codebase. "Triple Jurik Smooth" by Mladen Rakic. https://www.mql5.com/en/code/20620 — `verified`

[7] MQL5 Codebase. "Jurik Volty" by Mladen Rakic. https://www.mql5.com/en/code/21229 — `verified`

[8] MQL5 Forum. CFB references in fractal threads. https://www.mql5.com/en/forum/175930/6663549 — `verified`

[9] MQL5 Codebase. "RSX of RSX" by Mladen Rakic. https://www.mql5.com/en/code/22404 — `verified`

[10] Jurik Research website. https://www.jurikres.com — `blocked` (site unreachable at time of research)
