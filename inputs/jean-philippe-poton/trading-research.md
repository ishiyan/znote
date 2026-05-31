# Jean-Philippe Poton

## Biography

Jean-Philippe Poton is a French autodidact working at the intersection of fractal geometry, philosophy, and financial markets. He previously lived in Hino, western Tokyo, Japan, and relocated to Singapore in March 2011 during the Fukushima nuclear crisis (his wife's family is Singaporean). He currently works in Forex trading from Singapore.

No formal academic affiliation is known. His intellectual profile — drawing on Mandelbrot's fractal geometry, Nishida Kitaro's philosophy of place, Elie Ayache's market ontology (*The Blank Swan*), p-adic number theory, category theory, and French literary tradition (Baudelaire, Oulipo) — suggests a background in quantitative reasoning, but no degree or institution is documented. He has published over fifty papers' worth of indicator code and philosophical commentary on financial markets via blogs and the MQL5 CodeBase.

**Self-declared interests:** Forex, Technical analysis, Mathematics, Literature, Philosophy, Music.

**Online identity:**
- Username: jppoton
- Email: jppoton@yahoo.com
- Blogger profile: https://www.blogger.com/profile/16867058387912497552 (3,664 profile views)
- LinkedIn: Forex trading, Singapore

---

## Technical Indicators & Tools

Jean-Philippe Poton's contribution to trading is a coherent system of fractal-adaptive indicators, all built on the box-counting fractal dimension of price series. His foundational indicator (FGDI) feeds into all others.

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| FRASMA (Fractally Modified Simple Moving Average) | MQL5 CodeBase, Feb 2009 | Adaptive MA |
| FGDI (Fractal Graph Dimension Indicator) | MQL5 CodeBase, Apr 2009 | Fractal |
| FRASMAv2 (Fractal Adaptive SMA v2) | MQL5 CodeBase, Apr 2009 | Adaptive MA |
| Fractal Bands | MQL5 CodeBase, May 2009 | Channel |
| Fractional Bands | MQL5 CodeBase, May 2009 | Channel |
| Fractal Self-Similarity Measure | MQL5 CodeBase, Apr 2010 | Fractal |
| Hurst Exponent Variations | MQL5 CodeBase, May 2010 | Fractal |

### Extended Indicators (MT5 ports by Nikolay Kositsin, all credited to jppoton)

| Indicator | URL | Date |
|-----------|-----|------|
| FGDI (MT5) | https://www.mql5.com/en/code/16916 | 2017-01-19 |
| Fractal_Bands (MT5) | https://www.mql5.com/en/code/16915 | 2017-01-19 |
| Fractal_Keltner | https://www.mql5.com/en/code/16927 | 2017-01-26 |
| Fractal_MA | https://www.mql5.com/en/code/16928 | 2017-01-26 |
| Fractal_RSI | https://www.mql5.com/en/code/16929 | 2017-01-26 |
| Fractal_WPR | https://www.mql5.com/en/code/16945 | 2017-01-26 |
| Fractal_CCI | https://www.mql5.com/en/code/16960 | 2017-01-26 |
| Fractal_DeMarker | https://www.mql5.com/en/code/16980 | 2017-01-26 |
| Fractal_Moving_Average | https://www.mql5.com/en/code/16998 | 2017-01-26 |
| Fractal_Force_Index | https://www.mql5.com/en/code/17008 | 2017-01-26 |
| Fractal_ADX | https://www.mql5.com/en/code/17018 | 2017-01-26 |
| Fractal_Momentum | https://www.mql5.com/en/code/17043 | 2017-01-26 |
| Fractional_Bands (MT5) | https://www.mql5.com/en/code/17074 | 2017-01-26 |
| Fractal_Keltner_x5_Cloud | https://www.mql5.com/en/code/17093 | 2017-01-26 |
| Fractal_MFI | https://www.mql5.com/en/code/17107 | 2017-01-26 |
| Fractal_TRIX | https://www.mql5.com/en/code/17384 | 2017-03-02 |
| FRASMAv2 (MT5) | https://www.mql5.com/en/code/15810 | 2016-07-20 |

### Additional Variants (mentioned in MQL5 forum, "Advanced Elite" section)

- Fractal Dimension Index - jppoton (FDI using Sevcik/Matulich calculation)
- Fractal Dimension Index PA - jppoton (phase accumulation adaptive version)
- Fractal Dimension Index ALB - jppoton (adaptive look-back version)

---

## TASC Publications

**Jean-Philippe Poton has no articles published in Technical Analysis of Stocks & Commodities (TASC).** The complete author list was searched for all name variations — no matches found.

---

## MQL5 Implementations

### Original MQL4 Indicators (by jppoton, account deleted)

| Title | URL | Published | Views | Rating |
|-------|-----|-----------|-------|--------|
| FRASMA: Fractally Modified SMA | https://www.mql5.com/en/code/8718 | 2009-02-18 | 50,668 | 11 votes |
| FGDI (Fractal Graph Dimension Indicator) | https://www.mql5.com/en/code/8844 | 2009-04-21 | 45,107 | 13 votes |
| FRASMAv2 | https://www.mql5.com/en/code/8866 | 2009-04-26 | 18,659 | 12 votes |
| Fractal Bands | https://www.mql5.com/en/code/8895 | 2009-05-06 | 30,831 | 10 votes |
| Fractional Bands | https://www.mql5.com/en/code/8900 | 2009-05-07 | 23,081 | 9 votes |
| Fractal Self-Similarity Measure | https://www.mql5.com/en/code/9604 | 2010-04-05 | 19,662 | 4 votes |
| Hurst Exponent Variations | https://www.mql5.com/en/code/9676 | 2010-05-17 | 35,812 | 1 vote |

**Combined MQL4 page views: ~223,820**

### Indicator Descriptions

**FGDI** — Rework of iliko's "Fractal dimension" script. Corrected two errors and added standard deviation of the box-counting dimension estimation. The foundational indicator on which all others are built. Values near 1.0 indicate strong trend; near 2.0 indicate choppy/mean-reverting market.

**FRASMA / FRASMAv2** — SMA accelerated during trends and slowed during sideways markets using fractal dimension from FGDI. V2 adds a "shift" parameter to move the MA forward/backward. Based on iliko's fractal_dimension.mq4.

**Fractal Bands** — Widens Bollinger Bands using Fractional Brownian Motion model incorporating fractal dimension to avoid/minimize false entry/exit signals.

**Fractional Bands** — More mathematically precise variant of Fractal Bands, using different equations derived from Fractional Brownian Motion theory.

**Fractal Self-Similarity Measure** — Multi-timeframe fractal dispersion indicator. Computes FGDI across multiple timeframes and measures standard deviation of fractal dimensions around the longest timeframe. Low dispersion indicates good entry signal.

**Hurst Exponent Variations** — Based on multi-fractal model. Computes Hurst exponent H from FGDI fractal dimension (H = 2 - D). Positive variations of H predict upcoming high-volatility periods. Does not indicate trade direction.

---

## Other Platform Implementations

| Platform | Title | URL | Date |
|----------|-------|-----|------|
| ProRealCode (ProRealTime) | Fractal Bands — Fractalised Bollinger Bands | https://www.prorealcode.com/prorealtime-indicators/fractal-bands/ | 2017-07-10 |
| Forex Station | FRASMA_v2, FRASMA-SSA_Alert | https://forex-station.com/various-specialist-indicators-for-mt4-t8472209-30.html | 2017-06-03 |

---

## Blog Publications

Jean-Philippe Poton maintained several blogs. The most significant for trading research is **"Fractals, Technical Analysis and other things..."** (fractalfinance.blogspot.com), active 2009–2012.

### Key Blog Posts

| Title | Date | URL | Topic |
|-------|------|-----|-------|
| The Absent Signal | Apr 2012 | https://fractalfinance.blogspot.com/2012/04/absent-signal.html | Philosophical critique: fractal dimension fails to identify time series as fractal; market fractality applies to market existence, not the time series |
| Current Research | Dec 2011 | https://fractalfinance.blogspot.com/2011/12/current-research.html | Discussion with Elie Ayache on *The Blank Swan* and p-adic numbers |
| The Art of Speculation | May 2011 | https://fractalfinance.blogspot.com/2011/05/art-of-speculation.html | Speculation as artistic activity; Baudelaire, Oulipo, Queneau; TA as "useful illusion" |
| The Possibility of Cognition | Apr 2011 | https://fractalfinance.blogspot.com/2011/04/possibility-of-cognition.html | Nishida's action-intuition, homeomorphisms between self-similar fractals and p-adic integers, market topology |
| The Logic of Place | Mar 2011 | https://fractalfinance.blogspot.com/2011/03/logic-of-place.html | Nishida Kitaro's "basho no ronri" applied to market analysis; Levinas' Illeity |
| R/S Analysis to Estimate the Hurst Exponent | Oct 2009 | https://stochasticfractals.wordpress.com/2009/10/14/rs-analysis-to-estimate-the-hurst-exponent/ | Technical: R/S analysis methodology |

### Other Blogs

| Blog | URL | Period | Content |
|------|-----|--------|---------|
| Fractals and Stochastic Calculus | https://stochasticfractals.wordpress.com | 2009 | R/S analysis, Hurst exponent |
| The Nomadic Chronicle | https://thenomadicchronicle.blogspot.com | 2009 | Philosophy, democracy, religion, cooking, literature |
| Chronique nomade | http://chroniquenomade.blogspot.com/ | Unknown | French-language personal blog |

---

## Forum Discussions

Jean-Philippe Poton's indicators are discussed primarily on MQL5 (his home platform). Outside MQL5, forum presence is minimal:

| Forum | Result |
|-------|--------|
| ForexFactory | 5 threads discuss fractal dimension concept; none mention Poton/FGDI/FRASMA by name |
| futures.io | 0 results |
| Elite Trader | 1 tangential mention of fractal dimension |
| NinjaTrader Forum | 0 results |
| TradingView | Scripts use Ehlers' FDI, not Poton's FGDI |
| MQL5 Forum | 15+ posts; Sergey Golubev (newdigital) documents extended variants; Lloyd_au references "Jean-Phillipe's FGDI" in Ehlers thread |
| Wealth-Lab | 0 results |
| Quant Stack Exchange | 1 tangential mention |
| r/algotrading | 3 threads discuss FDI concept generically |
| Trade2Win | 0 results |
| ProRealCode | 1 indicator page — authored by Poton |
| Forex Station | 1 thread redistributing FRASMA_v2 |
| NuclearPhynance | Discussion with Elie Ayache on p-adic numbers and market topology |

---

## Academic Papers

**No academic papers by Jean-Philippe Poton were found.** Searched Google Scholar, Crossref, Semantic Scholar, and arXiv — all returned zero results. His work is published exclusively through blogs, MQL5 CodeBase, and forum posts.

---

## Photos, Videos & Interviews

### Photos

| Description | URL | Source |
|-------------|-----|--------|
| [URL not found] Blogger profile — no photo | https://www.blogger.com/profile/16867058387912497552 | Blogger |
| [URL not found] LinkedIn — directory link only, requires login | — | LinkedIn |
| [URL not found] No Wikipedia article | — | Wikipedia |
| [URL not found] No ProRealCode author photo | — | ProRealCode |

### Videos

No videos found. Searched YouTube for "Jean-Philippe Poton", "jppoton", "fractalfinance" — no relevant results.

### Interviews & Podcasts

No interviews or podcast appearances found. His only known intellectual exchange is a NuclearPhynance forum discussion with Elie Ayache: http://www.nuclearphynance.com/Show%20Post.aspx?PostIDKey=144145

---

## BibTeX

```bibtex
@online{poton2009frasma,
  author       = {Poton, Jean-Philippe},
  title        = {{FRASMA}: Fractally Modified Simple Moving Average},
  date         = {2009-02-18},
  url          = {https://www.mql5.com/en/code/8718},
  urldate      = {2026-05-09},
  note         = {Indicator for MetaTrader~4. Views: 50,668. Rating: 11. Author account deleted; username: jppoton}
}

@online{poton2009fgdi,
  author       = {Poton, Jean-Philippe},
  title        = {Fractal Graph Dimension Indicator ({FGDI})},
  date         = {2009-04-21},
  url          = {https://www.mql5.com/en/code/8844},
  urldate      = {2026-05-09},
  note         = {Indicator for MetaTrader~4. Views: 45,107. Rating: 13. Rework of iliko's fractal dimension script with bug fixes and standard deviation}
}

@online{poton2009frasmav2,
  author       = {Poton, Jean-Philippe},
  title        = {{FRASMAv2}: Fractal Adaptive Simple Moving Average v2},
  date         = {2009-04-26},
  url          = {https://www.mql5.com/en/code/8866},
  urldate      = {2026-05-09},
  note         = {Indicator for MetaTrader~4. Views: 18,659. Rating: 12}
}

@online{poton2009fractalbands,
  author       = {Poton, Jean-Philippe},
  title        = {Fractal Bands},
  date         = {2009-05-06},
  url          = {https://www.mql5.com/en/code/8895},
  urldate      = {2026-05-09},
  note         = {Indicator for MetaTrader~4. Views: 30,831. Rating: 10. Fractalised Bollinger Bands using Fractional Brownian Motion}
}

@online{poton2009fractionalbands,
  author       = {Poton, Jean-Philippe},
  title        = {Fractional Bands},
  date         = {2009-05-07},
  url          = {https://www.mql5.com/en/code/8900},
  urldate      = {2026-05-09},
  note         = {Indicator for MetaTrader~4. Views: 23,081. Rating: 9. Mathematically more precise variant of Fractal Bands}
}

@online{poton2010selfsimilarity,
  author       = {Poton, Jean-Philippe},
  title        = {A Measure of Fractal Self-Similarity},
  date         = {2010-04-05},
  url          = {https://www.mql5.com/en/code/9604},
  urldate      = {2026-05-09},
  note         = {Indicator for MetaTrader~4. Views: 19,662. Rating: 4. Multi-timeframe fractal dispersion}
}

@online{poton2010hurst,
  author       = {Poton, Jean-Philippe},
  title        = {Variations of the {Hurst} Exponent over Time},
  date         = {2010-05-17},
  url          = {https://www.mql5.com/en/code/9676},
  urldate      = {2026-05-09},
  note         = {Indicator for MetaTrader~4. Views: 35,812. Rating: 1. Predicts volatility changes via multi-fractal model}
}

@online{kositsin2017fgdimt5,
  author       = {Kositsin, Nikolay},
  title        = {{FGDI} [MT5 port]},
  date         = {2017-01-19},
  url          = {https://www.mql5.com/en/code/16916},
  urldate      = {2026-05-09},
  note         = {MetaTrader~5 port. Real author: jppoton@yahoo.com. Part of 17-indicator porting series}
}

@online{poton2017fractalbands_prorealcode,
  author       = {Poton, Jean-Philippe},
  title        = {Fractal Bands --- Fractalised {B}ollinger Bands},
  date         = {2017-07-10},
  url          = {https://www.prorealcode.com/prorealtime-indicators/fractal-bands/},
  urldate      = {2026-05-09},
  note         = {ProRealCode implementation with author's strategy note}
}

@online{poton2012absentsignal,
  author       = {Poton, Jean-Philippe},
  title        = {The Absent Signal},
  date         = {2012-04-16},
  url          = {https://fractalfinance.blogspot.com/2012/04/absent-signal.html},
  urldate      = {2026-05-09},
  note         = {Blog: Fractals, Technical Analysis and other things. Critique of fractal dimension as market signal}
}

@online{poton2011artspeculation,
  author       = {Poton, Jean-Philippe},
  title        = {The Art of Speculation},
  date         = {2011-05-22},
  url          = {https://fractalfinance.blogspot.com/2011/05/art-of-speculation.html},
  urldate      = {2026-05-09},
  note         = {Blog post. TA as ``useful illusion''; references Baudelaire, Oulipo, Queneau}
}

@online{poton2011cognition,
  author       = {Poton, Jean-Philippe},
  title        = {The Possibility of Cognition},
  date         = {2011-04-18},
  url          = {https://fractalfinance.blogspot.com/2011/04/possibility-of-cognition.html},
  urldate      = {2026-05-09},
  note         = {Blog post. P-adic numbers, fractals, Nishida Kitaro's action-intuition applied to markets}
}

@online{poton2011logicofplace,
  author       = {Poton, Jean-Philippe},
  title        = {The Logic of Place},
  date         = {2011-03-09},
  url          = {https://fractalfinance.blogspot.com/2011/03/logic-of-place.html},
  urldate      = {2026-05-09},
  note         = {Blog post. Nishida's basho applied to market topology}
}

@online{poton2009hurst_blog,
  author       = {Poton, Jean-Philippe},
  title        = {R/S Analysis to Estimate the {H}urst Exponent},
  date         = {2009-10-14},
  url          = {https://stochasticfractals.wordpress.com/2009/10/14/rs-analysis-to-estimate-the-hurst-exponent/},
  urldate      = {2026-05-09},
  note         = {Blog: Fractals and Stochastic Calculus}
}

@online{potonblog,
  author       = {Poton, Jean-Philippe},
  title        = {Fractals, Technical Analysis and other things\ldots},
  url          = {https://fractalfinance.blogspot.com/},
  urldate      = {2026-05-09},
  note         = {Blog active 2009--2012. Indicator explanations, philosophical essays on market topology}
}

@online{poton_blogger_profile,
  author       = {Poton, Jean-Philippe},
  title        = {Blogger User Profile},
  url          = {https://www.blogger.com/profile/16867058387912497552},
  urldate      = {2026-05-09},
  note         = {Location: Singapore. Interests: Forex, Technical analysis, Mathematics, Literature, Philosophy, Music}
}

@online{poton_nuclearphynance,
  author       = {Poton, Jean-Philippe},
  title        = {Discussion with {E}lie {A}yache on p-adic numbers and market topology},
  url          = {http://www.nuclearphynance.com/Show%20Post.aspx?PostIDKey=144145},
  urldate      = {2026-05-09},
  note         = {NuclearPhynance forum, page 22+}
}

@online{forexstation_frasma_2017,
  author       = {mntiwana},
  title        = {Various (Specialist) indicators for MT4 --- {FRASMA}\_v2 and {FRASMA}-{SSA}\_Alert},
  date         = {2017-06-03},
  url          = {https://forex-station.com/various-specialist-indicators-for-mt4-t8472209-30.html},
  urldate      = {2026-05-09},
  note         = {Forex Station forum thread redistributing Poton's FRASMA}
}
```
