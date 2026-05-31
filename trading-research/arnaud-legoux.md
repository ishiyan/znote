# Arnaud Legoux — Trading Research Profile

## Biography

| Field | Detail |
|-------|--------|
| Full name | Arnaud Legoux |
| Location | Paris, France |
| Co-author | Dimitris Kouzis-Loukas (also spelled "Dimitrios Douzis-Loukas") |
| Known for | ALMA — Arnaud Legoux Moving Average (2009–2010) |
| Website | arnaudlegoux.com (offline since ~2024; archived) |
| Twitter | @arnaudlx |
| Facebook | facebook.com/profile.php?id=1228069491 |
| Professional background | Unknown — no academic or corporate affiliation disclosed |
| Publications | 1 self-published PDF technical article (2011), no journal/magazine articles |

### About

Arnaud Legoux is a Paris-based independent trader/developer who co-created the **ALMA (Arnaud Legoux Moving Average)** around 2009–2010 with colleague **Dimitris Kouzis-Loukas**. The indicator was first released as a free NinjaTrader download on March 21, 2010, via his personal website. A technical PDF article explaining the formula was published in March 2011. MQL4, MQL5, and TradeStation versions followed.

Legoux has no academic publications, no TASC articles, no books, and no public speaking appearances. His entire public contribution consists of:
1. The ALMA indicator (NinjaTrader, open source)
2. A single PDF article explaining the formula
3. A WordPress blog (4 posts, 2010–2012)

Despite this minimal output, ALMA achieved wide adoption and is now a **built-in indicator on TradingView** and included in most major TA libraries.

---

## TASC Publications

**None.** Arnaud Legoux has no articles in Technical Analysis of Stocks & Commodities.

---

## IFTA Journal / JoTA / Trader's World

**None** in any of these publications.

---

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| ALMA (Arnaud Legoux Moving Average) | March 2010 (NinjaTrader release); PDF article March 2011 | Adaptive MA / FIR Filter |

### ALMA — Technical Description

**Mechanism:** A Gaussian-weighted FIR filter applied to price data, with an adjustable offset parameter that shifts the Gaussian curve's peak position along the window.

**Parameters:**
- **Window** (period): Default 9. The number of bars in the lookback.
- **Offset**: Default 0.85. Controls where the Gaussian peak is placed (0 = centered like SMA, 1 = aligned to most recent bar like EMA).
- **Sigma**: Default 6. Controls the width/sharpness of the Gaussian curve.

**Key properties:**
1. Applies the average from left-to-right AND right-to-left, creating a "combo line"
2. Uses Gaussian distribution (normal curve) as weights rather than uniform (SMA) or exponential (EMA)
3. The offset parameter biases toward recent prices, reducing phase lag
4. Zero-phase digital filtering concept — reduces noise without adding delay
5. Classified as an FIR (Finite Impulse Response) filter

**Formula** (pseudocode):
```
m = offset * (window - 1)
s = window / sigma
w[i] = exp(-(i - m)^2 / (2 * s^2))   for i = 0..window-1
ALMA = sum(w[i] * price[window-1-i]) / sum(w[i])
```

**Claimed advantages over HMA (Hull Moving Average):**
- Smoother output
- More responsive to price changes
- Fewer false signals

---

## MQL5 Implementations

| Title | Author | Platform | URL |
|-------|--------|----------|-----|
| ALMA (Arnaud Legoux Moving Average) | Igor Durkin (igorad) | MT5 | [mql5.com/en/code/1175](https://www.mql5.com/en/code/1175) |
| ALMA with addition filters | Mladen Rakic | MT5 | [mql5.com/en/code/16517](https://www.mql5.com/en/code/16517) |
| ALMA 2.0 | Mladen Rakic | MT5 | [mql5.com/en/code/16847](https://www.mql5.com/en/code/16847) |
| Institutional Gaussian Signal Filter (Zero-Lag ALMA) | Amanda Vitoria De Paula Pereira | MT5 | [mql5.com/en/code/71322](https://www.mql5.com/en/code/71322) |
| Moving Averages — 14 different types | Yashar Seyyedin | MT5 | [mql5.com/en/code/48058](https://www.mql5.com/en/code/48058) |
| Moving Averages — 14 different types | Yashar Seyyedin | MT4 | [mql5.com/en/code/48621](https://www.mql5.com/en/code/48621) |
| AllAverages v4.9 MT5 | Ivan Astafurov | MT5 | [mql5.com/en/code/46041](https://www.mql5.com/en/code/46041) |
| AllAverages v4.9 | Ivan Astafurov | MT4 | [mql5.com/en/code/43879](https://www.mql5.com/en/code/43879) |

**Total: 8 entries** (3 dedicated ALMA, 5 multi-MA libraries including ALMA)

---

## Platform Adoption

ALMA is a **built-in indicator** on TradingView (not a community script — official platform support). It is also included in:

| Platform/Library | Status |
|-----------------|--------|
| TradingView | Built-in indicator (Pine Script `ta.alma()` function) |
| NinjaTrader | Original release platform (free download, 2010) |
| TradeStation | Official port by Legoux (2012) |
| MetaTrader 4/5 | Multiple implementations (see MQL5 section) |
| pandas_ta (Python) | Included as `alma()` |
| ta-lib community | Various implementations |

---

## GitHub Repositories

No dedicated ALMA repositories found via GitHub search. ALMA is included in multi-indicator libraries:

| Library | Language | Notes |
|---------|----------|-------|
| twopirllc/pandas_ta | Python | `ta.alma()` included |
| Various Pine Script repos | Pine | TradingView built-in |

---

## Forum Discussions

Forum searches were blocked by CAPTCHA for most sites. Based on the Wayback archive, Legoux linked to **Big Mike Trading (futures.io)** and **NinjaTrader Forum** in his blogroll, suggesting active participation in those communities circa 2010–2012.

| Forum | Result |
|-------|--------|
| futures.io (BigMikeTrading) | Likely active (blogroll link) — blocked |
| NinjaTrader Forum | Likely active (blogroll link) — blocked |
| ForexFactory | blocked |
| Elite Trader | blocked |
| TradingView | ALMA is built-in; numerous community discussions |
| Others | 0 / blocked |

---

## Academic Papers

**None found.** No academic publications by Arnaud Legoux or Dimitris Kouzis-Loukas on ALMA in Crossref, Semantic Scholar, or arXiv.

---

## Photos, Videos & Interviews

### Photos

| Description | URL | Source |
|-------------|-----|--------|
| [URL not found] No personal photo found | — | Blog used a "longcat" meme image as avatar |

### Videos

| Title | URL | Duration | Date |
|-------|-----|----------|------|
| [URL not found] No video appearances found | — | — | — |

### Interviews & Podcasts

No interviews or podcast appearances found.

---

## Related Authors

| Author | Relationship |
|--------|-------------|
| **Dimitris Kouzis-Loukas** | Co-author of ALMA |
| **Alan Hull** | Created HMA (Hull Moving Average) — ALMA explicitly designed to outperform HMA |
| **John Ehlers** | Gaussian/FIR filter approach to indicators; similar DSP tradition |
| **Patrick Mulloy** | DEMA/TEMA — earlier zero-lag MA approaches |
| **Tim Tillson** | T3 — another smooth low-lag MA |

---

## Key Dates

| Date | Event |
|------|-------|
| 2009 | Copyright notice on website — likely when ALMA was conceived |
| March 21, 2010 | First public release (NinjaTrader, free download) |
| May 13, 2010 | Blog post mentioning technical article |
| March 2011 | PDF article published ("ALMA — Arnaud Legoux Moving Average") |
| 2012 | MQL4, MQL5, TradeStation versions released |
| 2012 (Dec) | First MQL5 CodeBase entry (Igor Durkin, MT5) |
| ~2020 | TradingView adds ALMA as built-in indicator |
| ~2024 | arnaudlegoux.com goes offline |

---

## Assessment

ALMA is a genuinely useful contribution to the moving average landscape — a well-parameterized Gaussian FIR filter with an intuitive offset control. Its success is unusual: a single indicator from an anonymous Parisian with no publications, no books, no academic background, and no public presence achieved platform-level adoption (TradingView built-in) purely through community word-of-mouth and technical merit.

The indicator itself is mathematically straightforward (Gaussian-weighted FIR with offset), but the parameterization (window/offset/sigma) makes it accessible to traders who don't understand DSP theory. The "six sigma" default for the sigma parameter is a marketing nod rather than a statistical necessity.

---

## BibTeX

```bibtex
@online{Legoux2010alma,
  author  = {Legoux, Arnaud and Kouzis-Loukas, Dimitris},
  title   = {{ALMA} Moving Average (Download the {NinjaTrader} version for Free)},
  url     = {https://web.archive.org/web/20120829025325/http://www.arnaudlegoux.com/?p=1},
  urldate = {2026-05-31},
  year    = {2010},
  month   = mar,
  note    = {Original release announcement, Wayback Machine capture},
}

@online{Legoux2011article,
  author  = {Legoux, Arnaud and Kouzis-Loukas, Dimitris},
  title   = {{ALMA} --- {Arnaud Legoux Moving Average}},
  url     = {https://web.archive.org/web/20120324082059/http://www.arnaudlegoux.com/wp-content/uploads/2011/03/ALMA-Arnaud-Legoux-Moving-Average.pdf},
  urldate = {2026-05-31},
  year    = {2011},
  month   = mar,
  note    = {Technical PDF article with formula derivation, Wayback Machine capture},
}

@online{tradingview_alma,
  title   = {Arnaud Legoux Moving Average --- {TradingView} Help Center},
  url     = {https://www.tradingview.com/support/solutions/43000594683-arnaud-legoux-moving-average/},
  urldate = {2026-05-31},
  year    = {2026},
  note    = {TradingView built-in indicator documentation},
}

@online{mql5_alma_igorad,
  author  = {{Igor Durkin (igorad)}},
  title   = {{ALMA} ({Arnaud Legoux Moving Average})},
  url     = {https://www.mql5.com/en/code/1175},
  urldate = {2026-05-31},
  year    = {2012},
  note    = {MQL5 CodeBase, MetaTrader 5 indicator},
}

@online{mql5_alma_mladen,
  author  = {{Mladen Rakic}},
  title   = {{ALMA} with addition filters},
  url     = {https://www.mql5.com/en/code/16517},
  urldate = {2026-05-31},
  year    = {2016},
  note    = {MQL5 CodeBase, MetaTrader 5 indicator with additional filters and floating levels},
}

@online{mql5_alma2_mladen,
  author  = {{Mladen Rakic}},
  title   = {{ALMA} 2.0},
  url     = {https://www.mql5.com/en/code/16847},
  urldate = {2026-05-31},
  year    = {2016},
  note    = {MQL5 CodeBase, MetaTrader 5 indicator},
}

@online{wayback_legoux_site,
  author  = {Legoux, Arnaud},
  title   = {Arnaud Legoux --- stock market, future and forex indicator},
  url     = {https://web.archive.org/web/20120828030303/http://www.arnaudlegoux.com/},
  urldate = {2026-05-31},
  year    = {2012},
  note    = {Wayback Machine capture of author's personal website (Paris, France)},
}
```
