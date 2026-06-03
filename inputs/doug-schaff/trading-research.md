# Doug Schaff — Trading Research Profile

> Author-mode trading-research dossier on **Doug Schaff**, American forex trader
> and software developer, founder/president of **FX-Strategy, Inc.**, and creator
> of the **Schaff Trend Cycle (STC)** indicator. Compiled 2026-06-03. Every source
> has a BibTeX entry in the [BibTeX](#bibtex) section.
>
> Companion deep-research brief (investigative synthesis, STC mechanics & critical
> assessment): `outputs/doug-schaff.md`.

---

## Biography

**Doug Schaff** is an American foreign-exchange trader and software developer, the
**president and founder of FX-Strategy, Inc.**, a forex research and trading-tools
firm based in the Hudson Valley (71 Starbarrack Road, Red Hook, NY 12571) [bio1][bio2].
He is best known as the creator of the **Schaff Trend Cycle**, developed in the late
1990s and released publicly as code in 2008 [tips2010][bio2].

**Institutional career** (from FX-Strategy's own biography pages) [bio1][bio2]:

- **Education:** MBA, **University of Chicago** [bio1].
- **Bankers Trust** (New York & Paris): completed the bank's management training
  program, joined the Foreign Exchange Trading Division, promoted to **senior trader
  in the Paris office** — priced major/minor currencies, ran the FX/futures arbitrage
  desk, held spot/forward responsibility for the Dutch Guilder, Canadian Dollar and
  British Pound [bio1].
- **Merrill Lynch Bank** (from 1982): **Chief Foreign Exchange Trader** — traded
  Dollar-Yen and **established the bank's OTC currency-options business**, later
  expanded to cross-rate and emerging-market currency options [bio1][bio2].
- **Refco, Inc.** (from 1985): **Senior Partner, Currency Options Trading Division**
  — managed the FX trading area; under his supervision **Refco was the first to
  purchase a 10-year-maturity OTC currency option** [bio1].
- **1987:** began life as a private/independent trader [bio1].

He brought "more than 25 years" of forex experience to FX-Strategy and is described
by the firm as "a pioneer in building technical forex trading tools, including
automated trading systems… **the Schaff Trend Cycle & automated trading systems on
Pro Charts**" — the clearest primary-source link between the man and the indicator
[bio2]. A frequent FX-Strategy collaborator was technical analyst **Ian Copsey**
(author of the firm's Pro Commentary) [bio2].

**Confirmed:** nationality (American); MBA, Univ. of Chicago; employers (Bankers
Trust, Merrill Lynch Bank, Refco); firm (FX-Strategy, Inc.); authorship of STC; 2008
public code release [bio1][bio2][tips2010].
**Not found:** birth year/date, current activity status (no death record located; no
active personal/firm web presence after ~2011).

> **Note — domain disambiguation.** The firm's real domain is **`fx-strategy.com`
> (hyphenated)**, archived ~2001–2011. The non-hyphenated `fxstrategy.com` is an
> unrelated parked/affiliate site with no Schaff connection — this resolves prior
> confusion in earlier research that had left the firm "unconfirmed" [bio2][wired2005].

---

## Technical Indicators & Tools

### Core Indicator

| Indicator | First Public | Category | Notes |
|-----------|--------------|----------|-------|
| **Schaff Trend Cycle (STC)** | Code released 2008 (developed late 1990s) [tips2010] | Oscillator / Cycle | MACD line passed through two cascaded Lane-style stochastic transforms with EMA smoothing, scaled 0–100. Defaults (forex-native): MACD 23/50, cycle 10, factor 0.5, OB/OS 75/25. Full mechanics in `outputs/doug-schaff.md`. |

STC was **not** first published in TASC under Schaff's name; his TASC bylines (below)
are two 1999 cycle articles with Walter Bressert that do not introduce STC. The STC
algorithm entered the public domain via the forex-software/CodeBase ecosystem (~2008)
and mainstream TA media (Investopedia, 2010, written by Brian Twomey — not Schaff)
[tips2010].

---

## TASC Publications (Complete List, 1999)

Schaff's only TASC bylines, both co-authored with **Walter Bressert** (exhaustive
1982–2025 index check confirms no others). PDFs are subscriber-paywalled (HTTP 302 →
login). No Traders' Tips entries exist (that section began 2009; these are 1999).

### 1999

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| Jun | The Euro's Weekly Cycles | Follow-up forecasting the Euro's weekly cycles (Bressert cycle method). | [\V17\C06\043EURO](https://technical.traders.com/archive/article.asp?file=\V17\C06\043EURO.pdf) |
| May | The Euro's True Colors | Analyzing a currency with no price history (Euro launched 4 Jan 1999). | [\V17\C05\033EURO](https://technical.traders.com/archive/article.asp?file=\V17\C05\033EURO.pdf) |

---

## Books

| # | Title | Author(s) | Year | Publisher | Link |
|---|-------|-----------|------|-----------|------|
| 1 | How to Make Money Investing Abroad | Doug Schaff & Nancy Dunnan | 1995 | HarperCollins | [Google Books](https://www.google.com/search?tbm=bks&q=How+to+Make+Money+Investing+Abroad+Dunnan+Schaff) |
| 2 | The Fundraising Planner | Doug Schaff & Terry Schaff | 1999 | Jossey-Bass | [Google Books](https://www.google.com/search?tbm=bks&q=The+Fundraising+Planner+Schaff+Jossey-Bass) |
| 3 | The Four Elements of Successful Currency Trading | Doug Schaff & Terry Schaff | n.d. | FX-Strategy, Inc. | [bio2] (firm imprint; no ISBN located) |
| 4 | Getting Ready to Trade FX | Doug Schaff & Terry Schaff | n.d. | FX-Strategy, Inc. | [bio2] (firm imprint; no ISBN located) |

> Note: Books 1–2 are general-finance/fundraising titles (not technical analysis);
> books 3–4 are FX-Strategy in-house training titles co-authored with his wife,
> Terry Schaff. ISBNs for the firm titles could not be located.

---

## MQL5 Implementations

The MQL5/MQL4 CodeBase carries **~33 Schaff-family entries** — the strongest
objective measure of STC's reach. Canonical code/486 notes "Real author: Doug Schaff."
All entries verified live (HTTP 200 spot-checked on 486, 7356, 13434, 20281–20283,
21787).

### Canonical Schaff Trend Cycle

| Code | Title | Platform | Author |
|------|-------|----------|--------|
| [code/486](https://www.mql5.com/en/code/486) | Schaff Trend Cycle (Real author: Doug Schaff) | MT5 | Nikolay Kositsin |
| [code/7356](https://www.mql5.com/en/code/7356) | Schaff Trend Cycle | MT4 | Scriptor / FostarFX |
| [code/17699](https://www.mql5.com/en/code/17699) | Schaff trend cycle – adjustable smoothing | MT5 | Mladen Rakic |
| [code/17700](https://www.mql5.com/en/code/17700) | Schaff trend cycle – adjustable smoothing | MT4 | Mladen Rakic |
| [code/20281](https://www.mql5.com/en/code/20281) | Schaff Trend Cycle | MT5 | Mladen Rakic |
| [code/55510](https://www.mql5.com/en/code/55510) | Schaff Trend Cycle MT4 | MT4 | Tuan Nguyen Van |
| [code/55511](https://www.mql5.com/en/code/55511) | Schaff Trend Cycle MT5 | MT5 | Tuan Nguyen Van |

### Schaff Trend Cycle — MA / smoothing variants

| Code | Title | Platform | Author |
|------|-------|----------|--------|
| [code/20282](https://www.mql5.com/en/code/20282) | Schaff Trend Cycle – DEMA | MT5 | Mladen Rakic |
| [code/20283](https://www.mql5.com/en/code/20283) | Schaff Trend Cycle – TEMA | MT5 | Mladen Rakic |
| [code/21787](https://www.mql5.com/en/code/21787) | Schaff Trend Cycle – NonLag MA | MT5 | Mladen Rakic |
| [code/21788](https://www.mql5.com/en/code/21788) | Schaff Trend Cycle CD – NonLag MA | MT5 | Mladen Rakic |
| [code/23543](https://www.mql5.com/en/code/23543) | Schaff trend cycle – Hull | MT5 | Mladen Rakic |
| [code/21237](https://www.mql5.com/en/code/21237) | Schaff Trend Cycle – Jurik Volty Adaptive RSX | MT5 | Mladen Rakic |

### Schaff Trend on alternative oscillator inputs (RSI/RSX/CCI/TCD)

| Code | Title | Platform | Author |
|------|-------|----------|--------|
| [code/20491](https://www.mql5.com/en/code/20491) | Schaff Trend RSI | MT5 | Mladen Rakic |
| [code/20494](https://www.mql5.com/en/code/20494) | Schaff Trend RSX | MT5 | Mladen Rakic |
| [code/20498](https://www.mql5.com/en/code/20498) | Schaff TCD RSI | MT5 | Mladen Rakic |
| [code/20499](https://www.mql5.com/en/code/20499) | Schaff TCD RSX | MT5 | Mladen Rakic |
| [code/20519](https://www.mql5.com/en/code/20519) | Schaff Trend RSI MTF | MT5 | Mladen Rakic |
| [code/20520](https://www.mql5.com/en/code/20520) | Schaff Trend RSX MTF | MT5 | Mladen Rakic |
| [code/22335](https://www.mql5.com/en/code/22335) | Schaff trend CCI | MT5 | Mladen Rakic |
| [code/23547](https://www.mql5.com/en/code/23547) | Schaff trend cycle CCI | MT5 | Mladen Rakic |

### EarnForex "ColorSchaff…TrendCycle" family (alternative oscillator engines)

| Code | Title | Platform | Author |
|------|-------|----------|--------|
| [code/13434](https://www.mql5.com/en/code/13434) | ColorSchaffRSITrendCycle | MT5 | N. Kositsin / EarnForex |
| [code/13435](https://www.mql5.com/en/code/13435) | ColorSchaffMomentumTrendCycle | MT5 | N. Kositsin / EarnForex |
| [code/13436](https://www.mql5.com/en/code/13436) | ColorSchaffTriXTrendCycle | MT5 | N. Kositsin / EarnForex |
| [code/13440](https://www.mql5.com/en/code/13440) | ColorSchaffMFITrendCycle | MT5 | N. Kositsin / EarnForex |
| [code/13441](https://www.mql5.com/en/code/13441) | ColorSchaffRVITrendCycle | MT5 | N. Kositsin / EarnForex |
| [code/13442](https://www.mql5.com/en/code/13442) | ColorSchaffWPRTrendCycle | MT5 | N. Kositsin / EarnForex |
| [code/13842](https://www.mql5.com/en/code/13842) | ColorSchaffJJRSXTrendCycle | MT5 | N. Kositsin / EarnForex |
| [code/13877](https://www.mql5.com/en/code/13877) | ColorSchaffJCCXTrendCycle | MT5 | N. Kositsin / EarnForex |
| [code/14055](https://www.mql5.com/en/code/14055) | ColorSchaffDeMarkerTrendCycle | MT5 | N. Kositsin |

### "Schaff Trend" (early / non-cycle) + signal variants

| Code | Title | Platform | Author |
|------|-------|----------|--------|
| [code/8348](https://www.mql5.com/en/code/8348) | Schaff Trend | MT4 | Collector |
| [code/8467](https://www.mql5.com/en/code/8467) | Schaff Trend | MT4 | Collector |
| [code/10830](https://www.mql5.com/en/code/10830) | Schaff Trend + Signal EMA | MT4 | Bruno Pio (blap) |

### MQL5 Articles

| Title | Author | URL |
|-------|--------|-----|
| Comparative Analysis of 10 Trend Strategies (Strategy #8 uses a "Schaff cyclical oscillator") | Alexander Fedosov | [articles/3074](https://www.mql5.com/en/articles/3074) |

No dedicated STC article exists in the MQL5 EN articles index.

---

## GitHub Repositories

### Dedicated Repositories

| Repository | Stars | Language | Description |
|------------|-------|----------|-------------|
| [zschro/GekkoSchaffTrendCycle](https://github.com/zschro/GekkoSchaffTrendCycle) | 16 | JavaScript | STC indicator/strategy for the Gekko bot |
| [EarnForex/Schaff-Trend-Cycle](https://github.com/EarnForex/Schaff-Trend-Cycle) | 8 | MQL5 | MT4/MT5 + NinjaTrader/cAlgo C# port |
| [goki75/SchaffsTrendCycle](https://github.com/goki75/SchaffsTrendCycle) | 1 | Pine | STC in TradingView/PineScript |

### Libraries Including STC

| Repository | Stars | Language | File path | Symbol |
|------------|-------|----------|-----------|--------|
| [bukosabino/ta](https://github.com/bukosabino/ta) | ~5.1k | Python | `ta/trend.py` | `class STCIndicator` / `stc()` — docstring credits "trader Doug Schaff" |
| [freqtrade/technical](https://github.com/freqtrade/technical) | ~1.0k | Python | `technical/indicators/indicators.py` | `stc(df, fast=23, slow=50, length=10)` |
| [xgboosted/pandas-ta-classic](https://github.com/xgboosted/pandas-ta-classic) | ~350 | Python | `pandas_ta_classic/momentum/stc.py` | `stc()` + `schaff_tc()` helper |

> Note: the original `twopirllc/pandas-ta` repo now returns 404 (removed);
> `pandas-ta-classic` is the maintained community fork carrying the STC port.

---

## Forum Discussions

| Forum | Result | Notes |
|-------|--------|-------|
| TradingView | **Results** | Active STC script community (see below) |
| Quant Stack Exchange | 0 results | Definitive empty |
| ForexFactory | blocked | JS-only search shell |
| futures.io / bigmiketrading | blocked | HTTP 403 |
| Elite Trader | blocked | HTTP 403 |
| NinjaTrader forum | blocked | login-gated search |
| MQL5 forum | blocked | JS-rendered search |
| Wealth-Lab | blocked | search 404 |
| r/algotrading (Reddit) | blocked | bot verification / 403 |
| Trade2Win | blocked | search 404 |

8 of 10 forums were bot-blocked or login/CAPTCHA-gated this pass (reported honestly,
not as "no results").

### TradingView — STC scripts (built-in + community)

TradingView ships a **built-in "Schaff Trend Cycle (STC)"** and exposes
`ta.stc(source, fast, slow, factor)` in Pine v5+. Community scripts from the STC tag
(`tradingview.com/scripts/schafftrendcycle/`):

| Script | Author | Type | URL |
|--------|--------|------|-----|
| Indicator: Schaff Trend Cycle (STC) | LazyBear | indicator | [script/dbxXeuw2](https://www.tradingview.com/script/dbxXeuw2-Indicator-Schaff-Trend-Cycle-STC/) |
| Schaff Trend Cycle | everget | indicator | [script/UkWZRgLG](https://www.tradingview.com/script/UkWZRgLG-Schaff-Trend-Cycle/) |
| STC Indicator – A Better MACD [SHK] | shayankm | indicator | [script/WhRRThMI](https://www.tradingview.com/script/WhRRThMI-STC-Indicator-A-Better-MACD-SHK/) |
| Adaptive, Zero lag Schaff Trend Cycle [Loxx] | loxx | indicator | [script/DU0J5PHe](https://www.tradingview.com/script/DU0J5PHe-Adaptive-Zero-lag-Schaff-Trend-Cycle-Loxx/) |
| Adaptive Schaff Trend Cycle (STC) [AlgoAlpha] | AlgoAlpha | indicator | [script/yOxili7R](https://www.tradingview.com/script/yOxili7R-Adaptive-Schaff-Trend-Cycle-STC-AlgoAlpha/) |
| Volume-Adjusted Schaff Trend Cycle (VASTC) | nathanfarmer | indicator | [script/nBBpGrzT](https://www.tradingview.com/script/nBBpGrzT-Volume-Adjusted-Schaff-Trend-Cycle-VASTC/) |
| CCI Cycle (Modified Schaff Trend Cycle) | DreamsDefined | indicator | [script/SYXp2cAq](https://www.tradingview.com/script/SYXp2cAq-CCI-Cycle-Modified-Schaff-Trend-Cycle/) |

---

## Academic Papers

No peer-reviewed study addresses the Schaff Trend Cycle, Doug Schaff, or FX-Strategy
**by name** — expected for a branded vendor indicator. By-category evidence on STC's
underlying rule class (fast MACD / FX timing rules) is collected and assessed in the
companion deep-research brief `outputs/doug-schaff.md` (13 Crossref-verified DOIs:
Chong & Ng 2008; Qi & Wu 2006; Olson 2004; Neely & Weller 2003; Sullivan-Timmermann-
White 1999; White 2000; Park & Irwin 2007; Marshall et al. 2008; Brock et al. 1992;
Hsu & Kuan 2005; Lo-MacKinlay 1988; Lo-Mamaysky-Wang 2000; Timmermann-Granger 2004).

---

## Photos, Videos & Interviews

### Photos

All three are real, Wayback-archived JPEGs from FX-Strategy's own image directory
(verified HTTP 200, `image/jpeg`).

| Description | URL | Source |
|-------------|-----|--------|
| Portrait header banner (640×224) | https://web.archive.org/web/20070730181919/http://www.fx-strategy.com/images/doug_640x224.jpg | FX-Strategy |
| "Doug's Blog" header photo | https://web.archive.org/web/20070820122256/http://www.fx-strategy.com/images/dougblogheader.jpg | FX-Strategy |
| Doug Schaff & Ian Copsey ("doug ian boxing") | https://web.archive.org/web/20070730182658/http://www.fx-strategy.com/images/dougianboxing.jpg | FX-Strategy |

### Videos

| Title | URL | Notes |
|-------|-----|-------|
| Any video of Doug Schaff himself | `[URL not found]` | None located; numerous third-party STC tutorials exist but are not the man |

### Interviews & Podcasts

| Title | URL | Publication | Date |
|-------|-----|-------------|------|
| "Fearless Traders Flock to Forex" (quotes Schaff, links his firm) | https://www.wired.com/2005/12/fearless-traders-flock-to-forex/ | WIRED (J. Glasner) | 2005-12-20 |
| Dedicated interview/podcast with Doug Schaff | `[URL not found]` | — | — |

---

## BibTeX

```bibtex
@article{tasc:v17c05033euro,
  author  = {Bressert, Walter and Schaff, Doug},
  title   = {The Euro's True Colors},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1999},
  month   = may,
  volume  = {17},
  number  = {5},
  url     = {https://technical.traders.com/archive/article.asp?file=\V17\C05\033EURO.pdf},
  note    = {Paywalled (HTTP 302 to subscriber login)},
}

@article{tasc:v17c06043euro,
  author  = {Bressert, Walter and Schaff, Doug},
  title   = {The Euro's Weekly Cycles},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1999},
  month   = jun,
  volume  = {17},
  number  = {6},
  url     = {https://technical.traders.com/archive/article.asp?file=\V17\C06\043EURO.pdf},
  note    = {Paywalled (HTTP 302 to subscriber login)},
}

@online{bio1,
  author  = {Schaff, Doug},
  title   = {Doug's Bio --- FX-Strategy},
  year    = {2001},
  howpublished = {FX-Strategy, Inc. (Wayback Machine)},
  url     = {https://web.archive.org/web/20010430065320/http://www.fx-strategy.com:80/archives/bio_DS.htm},
  urldate = {2026-06-03},
  note    = {Primary source: MBA Univ. of Chicago; Bankers Trust; Merrill Lynch Bank 1982; Refco 1985; private trader 1987},
}

@online{bio2,
  author  = {{FX-Strategy, Inc.}},
  title   = {Company Profile --- Doug Schaff},
  year    = {2006},
  howpublished = {FX-Strategy, Inc. (Wayback Machine)},
  url     = {https://web.archive.org/web/20061018073311/http://www.fx-strategy.com/about/team.php},
  urldate = {2026-06-03},
  note    = {Primary source: founder/president; "Schaff Trend Cycle \& automated trading systems on Pro Charts"},
}

@online{wired2005,
  author  = {Glasner, Joanna},
  title   = {Fearless Traders Flock to Forex},
  year    = {2005},
  month   = dec,
  howpublished = {WIRED},
  url     = {https://www.wired.com/2005/12/fearless-traders-flock-to-forex/},
  urldate = {2026-06-03},
  note    = {Press mention quoting Doug Schaff / FX-Strategy},
}

@online{tips2010,
  author  = {{Technical Analysis of Stocks \& Commodities}},
  title   = {Letters to S\&C (Schaff Trend Cycle code released 2008)},
  year    = {2010},
  month   = jun,
  url     = {http://traders.com/Documentation/FEEDbk_docs/2010/06/Letters.html},
  urldate = {2026-06-03},
}

@book{schaff1995invest,
  author    = {Schaff, Doug and Dunnan, Nancy},
  title     = {How to Make Money Investing Abroad},
  year      = {1995},
  publisher = {HarperCollins},
}

@book{schaff1999fundraising,
  author    = {Schaff, Doug and Schaff, Terry},
  title     = {The Fundraising Planner},
  year      = {1999},
  publisher = {Jossey-Bass},
}

@book{schaff_fourelements,
  author    = {Schaff, Doug and Schaff, Terry},
  title     = {The Four Elements of Successful Currency Trading},
  publisher = {FX-Strategy, Inc.},
  note      = {In-house training title; no ISBN located},
}

@book{schaff_gettingready,
  author    = {Schaff, Doug and Schaff, Terry},
  title     = {Getting Ready to Trade FX},
  publisher = {FX-Strategy, Inc.},
  note      = {In-house training title; no ISBN located},
}

@online{mql5_code486,
  author  = {Kositsin, Nikolay},
  title   = {Schaff Trend Cycle (Real author: Doug Schaff)},
  howpublished = {MQL5 Code Base, code/486},
  url     = {https://www.mql5.com/en/code/486},
  urldate = {2026-06-03},
  note    = {MetaTrader 5 indicator},
}

@online{mql5_code7356,
  author  = {{Scriptor}},
  title   = {Schaff Trend Cycle},
  howpublished = {MQL5 Code Base, code/7356},
  url     = {https://www.mql5.com/en/code/7356},
  urldate = {2026-06-03},
  note    = {MetaTrader 4 indicator},
}

@online{mql5_code20281,
  author  = {Rakic, Mladen},
  title   = {Schaff Trend Cycle (and DEMA/TEMA/NonLag/Hull/RSX/CCI variant family)},
  howpublished = {MQL5 Code Base, code/20281 et seq.},
  url     = {https://www.mql5.com/en/code/20281},
  urldate = {2026-06-03},
  note    = {MetaTrader 5; ~20 Schaff-family variants by this author},
}

@online{mql5_code13434,
  author  = {Kositsin, Nikolay},
  title   = {ColorSchaffRSITrendCycle (EarnForex ColorSchaff…TrendCycle family)},
  howpublished = {MQL5 Code Base, code/13434 et seq.},
  url     = {https://www.mql5.com/en/code/13434},
  urldate = {2026-06-03},
  note    = {MetaTrader 5; alternative-oscillator Schaff family},
}

@online{mql5_art3074,
  author  = {Fedosov, Alexander},
  title   = {Comparative Analysis of 10 Trend Strategies},
  howpublished = {MQL5 Articles, articles/3074},
  url     = {https://www.mql5.com/en/articles/3074},
  urldate = {2026-06-03},
  note    = {Strategy \#8 uses a Schaff cyclical oscillator},
}

@online{gh_zschro_stc,
  author  = {{zschro}},
  title   = {GekkoSchaffTrendCycle --- STC indicator/strategy for Gekko},
  url     = {https://github.com/zschro/GekkoSchaffTrendCycle},
  urldate = {2026-06-03},
  note    = {GitHub repository, 16 stars, JavaScript},
}

@online{gh_earnforex_stc,
  author  = {{EarnForex}},
  title   = {Schaff-Trend-Cycle --- MetaTrader / NinjaTrader / cAlgo ports},
  url     = {https://github.com/EarnForex/Schaff-Trend-Cycle},
  urldate = {2026-06-03},
  note    = {GitHub repository, 8 stars, MQL5/C\#},
}

@online{gh_goki75_stc,
  author  = {{goki75}},
  title   = {SchaffsTrendCycle --- TradingView/PineScript},
  url     = {https://github.com/goki75/SchaffsTrendCycle},
  urldate = {2026-06-03},
  note    = {GitHub repository, Pine Script},
}

@online{gh_bukosabino_ta,
  author  = {Padial, Dario Lopez},
  title   = {ta --- Technical Analysis Library (STCIndicator)},
  url     = {https://github.com/bukosabino/ta},
  urldate = {2026-06-03},
  note    = {GitHub repository, ~5.1k stars, Python; ta/trend.py credits Doug Schaff},
}

@online{gh_freqtrade_technical,
  author  = {{freqtrade}},
  title   = {technical --- Indicator library (stc)},
  url     = {https://github.com/freqtrade/technical},
  urldate = {2026-06-03},
  note    = {GitHub repository, ~1.0k stars, Python; defaults fast=23, slow=50, length=10},
}

@online{gh_pandasta_classic,
  author  = {{pandas-ta-classic contributors}},
  title   = {pandas-ta-classic --- momentum/stc.py},
  url     = {https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/momentum/stc.py},
  urldate = {2026-06-03},
  note    = {GitHub repository, ~350 stars, Python},
}

@online{tv_stc_lazybear,
  author  = {{LazyBear}},
  title   = {Indicator: Schaff Trend Cycle (STC)},
  url     = {https://www.tradingview.com/script/dbxXeuw2-Indicator-Schaff-Trend-Cycle-STC/},
  urldate = {2026-06-03},
  note    = {TradingView Pine Script},
}

@online{tv_stc_everget,
  author  = {{everget}},
  title   = {Schaff Trend Cycle},
  url     = {https://www.tradingview.com/script/UkWZRgLG-Schaff-Trend-Cycle/},
  urldate = {2026-06-03},
  note    = {TradingView Pine Script},
}

@online{photo_doug_portrait,
  author  = {{FX-Strategy, Inc.}},
  title   = {Doug Schaff --- portrait header banner},
  url     = {https://web.archive.org/web/20070730181919/http://www.fx-strategy.com/images/doug_640x224.jpg},
  urldate = {2026-06-03},
  note    = {Photo (Wayback), image/jpeg},
}

@online{photo_doug_blog,
  author  = {{FX-Strategy, Inc.}},
  title   = {Doug's Blog header photo},
  url     = {https://web.archive.org/web/20070820122256/http://www.fx-strategy.com/images/dougblogheader.jpg},
  urldate = {2026-06-03},
  note    = {Photo (Wayback), image/jpeg},
}

@online{photo_doug_ian,
  author  = {{FX-Strategy, Inc.}},
  title   = {Doug Schaff and Ian Copsey ("doug ian boxing")},
  url     = {https://web.archive.org/web/20070730182658/http://www.fx-strategy.com/images/dougianboxing.jpg},
  urldate = {2026-06-03},
  note    = {Photo (Wayback), image/jpeg},
}
```
