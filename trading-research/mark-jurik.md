# Mark Jurik — Trading Research Profile

## Biography

| Field | Detail |
|-------|--------|
| Full name | Mark Jurik |
| Location | Pasadena, California (formerly Silicon Valley) |
| Company | Jurik Research Software, Inc. (founded 1988, winding down ~2023) |
| Address | 556 South Fair Oaks Avenue, #595, Pasadena, CA 91105 |
| Agent | Norman Smith (support@nfsmith.net) |
| Known for | JMA (Jurik Moving Average), RSX, VEL, DMX, CFB — proprietary closed-source indicators |
| Background | Signal processing, robotics, information theory (military/defense origins) |
| Awards | TASC Readers' Choice Award — 1st place 2010, 2011, 2012 (Software Plug-in category) |
| Books | *Computerized Trading* (editor, NYIF); *Neural Networks and Financial Forecasting* (author) |
| Website | jurikres.com (winding down; archived via Wayback Machine) |
| Photo | [Portrait](https://web.archive.org/web/20230929134742im_/http://jurikres.com/gifs1/portrait3.jpg) (from company website) |

### About

Mark Jurik is a signal processing specialist who founded Jurik Research in 1988 in Silicon Valley. The company develops proprietary, closed-source algorithms for financial technical analysis. His background is in military/defense signal processing ("Star Wars" mathematics), which he redirected to financial markets after the Cold War ended.

Jurik's products are **entirely proprietary** — the algorithms have never been published. This is the defining characteristic of his operation: premium-priced black-box indicators sold as platform plugins. The JMA algorithm, in particular, has been the subject of extensive reverse-engineering efforts in the trading community.

From the company website:
> "Jurik Research was founded in 1988 in Silicon Valley and develops algorithms that identify and classify complex data. Now that the cold war is over, signal processing skills originally intended for military projects are now successfully applied to the commercial arena."

The company is currently winding down after 34+ years of operation (announced ~2023). Sales continue on request via email only.

---

## TASC Publications

**None** — Mark Jurik has zero articles published in TASC. However, TASC reviewed Jurik products favorably (April 1999) and gave Jurik Research the **Readers' Choice Award** in the Software Plug-in category:

| Year | Ranking |
|------|---------|
| 2012 | 1st place (winner) |
| 2011 | 1st place (winner) |
| 2010 | 1st place (winner) |
| 2009 | 2nd place |
| 2008 | 3rd place |
| 2007 | 2nd place |
| 2006 | 4th place |
| 2005 | 4th place |
| 2004 | 4th place |
| 2002 | 4th place |
| 2000 | 4th place |
| 1999 | 4th place |

---

## IFTA Journal / JoTA / Trader's World

**None** in any of these publications.

---

## Technical Indicators & Tools

### Core Indicators (All Proprietary / Closed-Source)

| Indicator | Category | Description |
|-----------|----------|-------------|
| **JMA** (Jurik Moving Average) | Adaptive MA | Ultra-smooth MA with very low lag; originally called "AMA" (1992), renamed JMA ~1995 |
| **VEL** (Velocity) | Momentum | Noise-free momentum/velocity measure; replaces classic ROC/Momentum |
| **RSX** | Oscillator | Smooth, lag-free replacement for RSI; retains all RSI properties minus noise |
| **DMX** | Trend Strength | Smooth replacement for DMI/ADX; less lag than ADX |
| **CFB** (Composite Fractal Behavior) | Trend/Range | Fractal-based trend strength measure; replaces cycle analysis (FFT/MESA) |
| **WAV** | Data Preprocessing | Time-series preprocessor for neural net forecast models |
| **DDR** | Data Preprocessing | Dimensionality reduction across multiple indicators |

### Additional Free Studies (released publicly)

| Study | Description |
|-------|-------------|
| Gap Awareness© Technology | Handles price gaps in indicator calculation |
| DWMA (Double-Weighted MA) | Available as free study with JMA subscription |
| RSX Double | Double-application RSX variant |
| JMA DWMA | Combination indicator |

### JMA — What Is Known

**Parameters:** Length, Phase, Power (3 user-adjustable parameters)

**Known properties:**
- Adaptive: responds quickly to fast moves, smooths during consolidation
- Uses concepts from robotics and information theory
- Handles price gaps natively (Gap Awareness©)
- Non-linear — not a standard FIR or IIR filter
- Produces smoother output than any published MA at equivalent lag

**What is NOT known:** The actual algorithm. Despite 30+ years of community reverse-engineering attempts, no fully accurate open-source clone exists. The closest approximations are community "Jurik smooth" implementations on MQL5.

---

## Books & Publications

| # | Title | Year | Publisher | Role |
|---|-------|------|-----------|------|
| 1 | Computerized Trading: Maximizing Day Trading and Overnight Profits | 1999 | New York Institute of Finance (Prentice Hall) | Editor |
| 2 | Neural Networks and Financial Forecasting | ~1995 | Jurik Research | Author |
| 3 | NeuroTapes (12-hour video course on neural networks) | ~1993 | Jurik Research | Author |
| 4 | Contributing chapter in *Virtual Trading* | — | — | Contributing author |

### Articles

- Articles in **Futures Magazine**
- Articles in **Journal of Computational Intelligence in Finance**
- Complete publication list: [pub_list.txt](https://web.archive.org/web/20230929134742/http://jurikres.com/about/pub_list.txt)

---

## Presentations (28 conferences/seminars)

Notable appearances:
- Swiss Association of Market Technicians (SAMT), Zurich, November 2000
- Austin Association of Financial Traders, February 2010
- Trader's Magazine (Germany) interview, March 2010
- Full list: [presents.txt](https://web.archive.org/web/20230929134742/http://jurikres.com/about/presents.txt)

---

## MQL5 Implementations

**66 total entries** referencing "Jurik" in MQL5 CodeBase. These are community reverse-engineering attempts and JMA-based derivative indicators (NOT official Jurik code).

### Dedicated JMA/Jurik Implementations

| Title | Author | Platform | URL |
|-------|--------|----------|-----|
| JMA | Scriptor | MT4 | [mql5.com/en/code/7307](https://www.mql5.com/en/code/7307) |
| Triple Jurik Smooth | Mladen Rakic | MT5 | [mql5.com/en/code/20620](https://www.mql5.com/en/code/20620) |
| Jurik Volty | Mladen Rakic | MT5 | [mql5.com/en/code/21229](https://www.mql5.com/en/code/21229) |
| Jurik Volty Multi Timeframe | Mladen Rakic | MT5 | [mql5.com/en/code/21230](https://www.mql5.com/en/code/21230) |
| Jurik Filter | Mladen Rakic | MT5 | [mql5.com/en/code/16638](https://www.mql5.com/en/code/16638) |
| Jurik Velocity | Mladen Rakic | MT5 | [mql5.com/en/code/16750](https://www.mql5.com/en/code/16750) |
| Fractal Dimension - Jurik | Mladen Rakic | MT5 | [mql5.com/en/code/20587](https://www.mql5.com/en/code/20587) |

### JMA-Based Derivative Indicators (by Mladen Rakic, MT5)

| Title | URL |
|-------|-----|
| Multi JMA Slopes | [mql5.com/en/code/21599](https://www.mql5.com/en/code/21599) |
| JMA Keltner Channel | [mql5.com/en/code/21692](https://www.mql5.com/en/code/21692) |
| JMA TRIX Log | [mql5.com/en/code/21735](https://www.mql5.com/en/code/21735) |
| BB Stops JMA | [mql5.com/en/code/21761](https://www.mql5.com/en/code/21761) |
| iTrend JMA | [mql5.com/en/code/21835](https://www.mql5.com/en/code/21835) |
| Corrected JMA | [mql5.com/en/code/22020](https://www.mql5.com/en/code/22020) |
| ATR adaptive JMA | [mql5.com/en/code/22411](https://www.mql5.com/en/code/22411) |
| JMA Z-score | [mql5.com/en/code/22432](https://www.mql5.com/en/code/22432) |
| CCI JMA based | [mql5.com/en/code/22482](https://www.mql5.com/en/code/22482) |
| Force index - JMA | [mql5.com/en/code/22537](https://www.mql5.com/en/code/22537) |
| BB stops JMA - multiple stops | [mql5.com/en/code/22636](https://www.mql5.com/en/code/22636) |

### Jurik Volty Adaptive Variants

| Title | URL |
|-------|-----|
| EMA Jurik Volty Adaptive | [mql5.com/en/code/21233](https://www.mql5.com/en/code/21233) |
| DEMA Jurik Volty Adaptive | [mql5.com/en/code/21234](https://www.mql5.com/en/code/21234) |
| TEMA Jurik Volty Adaptive | [mql5.com/en/code/21236](https://www.mql5.com/en/code/21236) |
| Schaff Trend Cycle - Jurik Volty Adaptive RSX | [mql5.com/en/code/21237](https://www.mql5.com/en/code/21237) |

### MQL5 Articles

| Title | URL |
|-------|-----|
| Effective Averaging Algorithms with Minimal Lag: Use in Indicators | [mql5.com/en/articles/1450](https://www.mql5.com/en/articles/1450) |

**Note:** Mladen Rakic (MQL5 user "mladen") is the most prolific implementer of Jurik-style indicators, with 40+ entries. His implementations are approximations based on observed JMA behavior, not the actual algorithm.

---

## Platform Support (Official)

| Platform | Status |
|----------|--------|
| TradeStation | Supported (official plugin) |
| NinjaTrader 8 | Supported (official plugin) |
| MultiCharts | Supported |
| AmiBroker | Supported |
| eSignal 12 | Supported |
| Investor/RT | Supported |
| Trade Navigator | Supported |
| Sierra Chart | Supported |
| MATLAB | Supported |
| NeuroShell | Supported |
| NeoTicker | Supported |
| C/C++/C#/Pascal/VB/.NET | DLL available |

---

## GitHub Repositories

**None found** as dedicated repos. JMA approximations exist in various TA libraries but no official Jurik code is open-source.

---

## Forum Discussions

The Jurik indicators are extensively discussed on trading forums, particularly regarding reverse-engineering JMA. Notable threads (based on MQL5 search):

| Forum | Thread | Notes |
|-------|--------|-------|
| MQL5 Forum | Multiple threads by Mladen Rakic | Dozens of JMA-based indicators |
| ForexFactory | Extensive JMA discussions | blocked |
| futures.io | JMA discussions | blocked |
| Elite Trader | JMA discussions | blocked |

---

## Academic Papers

**None found** in Crossref, Semantic Scholar, or arXiv under "Mark Jurik." His articles appeared in *Journal of Computational Intelligence in Finance* (industry journal, not indexed in academic databases).

---

## Photos, Videos & Interviews

### Photos

| Description | URL | Source |
|-------------|-----|--------|
| Portrait (headshot) | [portrait3.jpg](https://web.archive.org/web/20230929134742im_/http://jurikres.com/gifs1/portrait3.jpg) | jurikres.com (Wayback) |

### Videos

| Title | URL | Duration | Date |
|-------|-----|----------|------|
| [URL not found] No public video appearances found | — | — | — |

### Interviews

| Title | Source | Date |
|-------|--------|------|
| Trader's Magazine (Germany) interview | Trader's Mag (German) | March 2010 |
| Wall Street Harvest interview | wallstreetharvest.com | September 2000 |

---

## "Snake Oil" Section

Jurik's website notably includes a "[Snake Oil](https://web.archive.org/web/20231210225553/http://jurikres.com/snake/main_oil.htm)" section warning traders about fraudulent products and indicators — an unusual and honest touch for a commercial vendor.

---

## Key Dates

| Date | Event |
|------|-------|
| 1988 | Jurik Research founded in Silicon Valley |
| 1992 | First product announcement ("AMA" using "Star Wars mathematics") |
| 1995 | Futures Magazine review — top scores; AMA renamed to JMA |
| 1999 | TASC favorable review (April issue); first RCA placement (4th) |
| 1999 | *Computerized Trading* book published (NYIF, editor) |
| 2000 | Spoke at SAMT (Swiss Association of Market Technicians), Zurich |
| 2005 | MARHedge article — hedge fund using VEL/RSX to manage $18M |
| 2010 | TASC RCA 1st place; German Trader's Magazine interview |
| 2011 | TASC RCA 1st place |
| 2012 | TASC RCA 1st place |
| ~2023 | Business winding down announced |

---

## Assessment

Mark Jurik represents the **ultimate proprietary approach** to trading indicator development. Unlike Ehlers, Blau, or Legoux who publish their formulas, Jurik kept his algorithms completely secret for 35 years and built a successful business selling them as black-box plugins.

**Strengths:**
- 12 consecutive TASC Readers' Choice Awards (1999–2012) demonstrates genuine user satisfaction
- Products used by institutional hedge funds (MARHedge 2005: $18M under management)
- Legitimate signal processing background (not marketing hype)
- 34+ years of sustained commercial operation
- 66 MQL5 implementations (all reverse-engineering attempts) = massive community interest

**Controversies:**
- Completely closed-source — impossible to verify claims independently
- Claims of "robotics and information theory" origins without published proofs
- Community reverse-engineering has produced approximations but never exact clones
- Price point ($205+ per indicator) criticized as high for unverifiable claims
- No academic publications or peer review of algorithms

**Legacy:** JMA is probably the most reverse-engineered indicator in trading history. The community's inability to fully replicate it after 30+ years suggests either genuine algorithmic innovation or sophisticated obfuscation (or both). The "Jurik smooth" approximations in MQL5 (primarily by Mladen Rakic) have become standard tools in their own right.

---

## BibTeX

```bibtex
@book{Jurik1999,
  author    = {Jurik, Mark},
  title     = {Computerized Trading: Maximizing Day Trading and Overnight Profits},
  publisher = {New York Institute of Finance (Prentice Hall)},
  year      = {1999},
  isbn      = {978-0735200654},
  note      = {Editor; 20 contributing authors},
}

@online{jurikres_home,
  author  = {{Jurik Research Software, Inc.}},
  title   = {Jurik Research --- Superior Technical Analysis},
  url     = {https://web.archive.org/web/20231210225553/http://jurikres.com/},
  urldate = {2026-05-31},
  year    = {2023},
  note    = {Wayback Machine capture; company winding down after 34 years},
}

@online{jurikres_about,
  author  = {Jurik, Mark},
  title   = {About Jurik Research},
  url     = {https://web.archive.org/web/20230929134742/http://jurikres.com/about/company.htm},
  urldate = {2026-05-31},
  year    = {2023},
  note    = {Biography, publications list, 28 conference presentations},
}

@online{jurikres_awards,
  author  = {{Jurik Research Software, Inc.}},
  title   = {News, Reviews, Awards --- Jurik Research},
  url     = {https://web.archive.org/web/20230720184109/http://jurikres.com/press/mainpres.htm},
  urldate = {2026-05-31},
  year    = {2023},
  note    = {TASC Readers' Choice Award 1st place 2010--2012; complete award history 1999--2012},
}

@online{mql5_jurik_smooth,
  author  = {{Mladen Rakic}},
  title   = {Triple Jurik Smooth},
  url     = {https://www.mql5.com/en/code/20620},
  urldate = {2026-05-31},
  year    = {2018},
  note    = {MQL5 CodeBase; community approximation of Jurik smoothing algorithm},
}

@online{mql5_jma_mt4,
  author  = {{Scriptor}},
  title   = {{JMA}},
  url     = {https://www.mql5.com/en/code/7307},
  urldate = {2026-05-31},
  note    = {MQL4 CodeBase; reverse-engineered JMA approximation for MetaTrader 4},
}

@article{mql5_article_averaging,
  title   = {Effective Averaging Algorithms with Minimal Lag: Use in Indicators},
  url     = {https://www.mql5.com/en/articles/1450},
  urldate = {2026-05-31},
  note    = {MQL5 article discussing JMA and other low-lag averaging methods},
}

@online{jurikres_catalog,
  author  = {{Jurik Research Software, Inc.}},
  title   = {Product Catalog --- Jurik Research},
  url     = {https://web.archive.org/web/20231211004507/http://jurikres.com/catalog1/catalog.htm},
  urldate = {2026-05-31},
  year    = {2023},
  note    = {Full product listing: JMA, VEL, CFB, RSX, DMX, WAV, DDR},
}
```
