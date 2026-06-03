# Walter Bressert — Deep Research Brief

> Investigative synthesis, not a catalog. The article/MQL5/forum/book inventory
> lives in `trading-research/walter-bressert.md`. This brief answers five
> analytical questions — methodology, DSS provenance, biography/status, legacy,
> and critical assessment — with cited evidence and explicit confidence labels.
> Claims are tagged **[VERIFIED]** (a dated, citable source was retrieved) or
> **[UNCONFIRMED]** (plausible but not corroborated). Compiled 2026-06-03.

## Executive Summary

Walter J. Bressert is the practitioner who **operationalized cycle theory for
futures traders**. He did not invent market cycles — Edward Dewey's Foundation
for the Study of Cycles (1941) and J.M. Hurst's *Profit Magic* (1970) precede
him — but he is reasonably credited with turning that descriptive tradition into
a *mechanical, tradable* system: centered/real-time detrending, the **RSI3M3**
trigger oscillator, **"timing bands,"** the oscillator/cycle "combination"
thesis, and a defined-risk multi-contract money-management frame [1][2]. His
working life is documentable in outline — the **HAL Commodity Cycles** newsletter
(started 1974), co-development of **CompuTrac** with Tim Slater (1979), retirement
from the newsletter in 1985, the 1991 book *The Power of Oscillator/Cycle
Combinations*, and the CycleWatch/ProfitTrader software era — but his birth year,
education, and current life status are **not in any located record** [3].

Two findings cut against the folklore. First, the **"Double Smoothed Stochastic"
that bears his name is, on the documentary record, William Blau's** (TASC, January
1991); the popular "DSS Bressert" is a *different* formula (a
stochastic-of-a-stochastic) whose earliest dateable trace is a mid-2000s platform
lexicon — a later popularization, not evidence of prior origin [4][5][6]. Second,
the **predictive core of his method is unproven and partly contradicted** by the
academic literature on fixed cycles and technical-trading-rule profitability,
while the **risk-management scaffolding he wrapped around it is sound and
standard** — and is the part most likely responsible for any real-world success
of his students [7][8][9][10]. The honest verdict: a genuine popularizer and able
systems-builder whose durable legacy is a cross-platform indicator he probably did
not originate, and whose cycle forecasts should be read as attention-organizing
heuristics rather than validated predictions.

---

## 1. The Methodology, Mechanically

Bressert's system is a **two-engine method** bolted to a money-management frame: a
*timing engine* (cycles, made visible by detrending and tradable by timing bands)
and a *trigger engine* (oscillators that turn at cycle tops/bottoms without
"wiggle"). The unifying thesis — the title of his 1991 book — is that cycles tell
you *when* to expect a turn and oscillators *confirm* it has happened, so each
covers the other's weakness [1][2]. The primary source for the mechanics is his
own words in the March 1998 *Stocks & Commodities* interview with Thom Hartle [1].

### Centered detrend (the foundation)

The construction is explicit and unambiguous [1]:

1. Find the dominant cycle length by hand (count bars between significant lows).
   Most daily markets show a 14–25 bar cycle; **a 20-day MA is the default start**.
2. Compute an MA **equal in length to the cycle**, up to the last close.
3. **Displace it back half the cycle length** (a 20-period MA plotted on day 10).
4. **Detrend by subtraction:** `detrend = price − (N-period MA displaced back N/2)`.

The result oscillates around zero, with troughs/peaks marking cyclic lows/highs.
The catch is structural: because the MA is shifted back N/2 bars, **the most recent
plottable value sits half a cycle in the past** — it cannot be read at the live
right edge. Bressert is candid that a beginner "will think… they've found the Holy
Grail" before discovering the lag [1]. This is a textbook non-causal (zero-phase)
filter, and it matters for the critical assessment (§5).

### Real-time detrend + the 3-10 oscillator

To get a right-edge signal he dropped the back-shift (same price-minus-MA, no N/2
displacement): "no lag, but degraded accuracy" [1]. Treating the real-time detrend
as insufficient alone, he overlaid a **3-vs-10 momentum oscillator** ("the 3-10
often turned right at those cycle tops and bottoms"). The detrend localizes *where*
in the cycle you are; the oscillator provides the actual turn signal.
**[UNCONFIRMED arithmetic]** the exact 3-10 formula (MA difference? of price or of
the detrend?) and any normalization of the real-time detrend are not stated in the
primary source [1].

### RSI3M3 (the signature trigger)

Defined explicitly: **a 3-period RSI, then smoothed by a 3-bar moving average** [1].
He arrived at it by pushing the RSI lookback to an extreme short (3 = "looks like
static"), then smoothing the static away with a 3-bar average — "a very tradable
oscillator that was better than the stochastic." Plotted *on* the centered detrend,
the two move together; a **dip below the buy line at 30** plus an upturn confirms
momentum has changed [1].

- **Buy line = 30** — stated explicitly twice [1].
- **Sell line — [UNCONFIRMED]:** described only as "the mirror image"; ~70 is
  inferred by symmetry but never printed [1].
- **RSI base — [UNCONFIRMED]:** Wilder vs simple smoothing of the 3-period RSI is
  not specified [1].

### Setup-bar / entry-stop mechanics

The judgment-free entry [1]: (1) oscillator drops below 30; (2) it **turns up** —
that bar is the **setup bar**; (3) place a **buy-stop one tick above the setup
bar's high** ("increase my odds… by 10% to 25%"); (4) protective sell-stop one
tick below the low. Sells are the exact mirror. The stop-above-the-high
deliberately enters *after* the bottom — chasing the exact tick is what produced
his losses [1].

### Timing bands (the "middle 70%")

Built by hand from the historical distribution of low-to-low, low-to-high and
high-to-low intervals: keep the **central 70%** of that distribution and call it
the band [1]. Given a confirmed low, the band forecasts the window for the next
top and the next low. He used it as an *exit gate*: "I am not going to even
consider getting out until I'm into that 70% timing band. Because only 15% of the
tops have occurred before that" [1]. The concept is explicit; **[UNCONFIRMED]** the
estimator ("middle 70%" reads as a 15th–85th-percentile band but the method is not
formally stated) [1].

### Money management (the part that holds up)

Scale out of 2–3 contracts at progressively longer-cycle targets [1]:

- **#1 — fast scalp** of the bounce (off within 4–5 days).
- **#2 — the trading-cycle top** (exit inside the timing band on a sell signal or
  trailing stop).
- **#3 — the longer cycle** (the dominant cycle in the next-longer time frame).

The risk arithmetic is given: a 3-contract position with 10% at risk = 3⅓% each;
banking #1 "lops off 3⅓%… and offsets the second 3⅓%, so exposure drops from 10%
to 3⅓%" [1]. Small per-contract risk (from entering near the bottom) is what
*permits* multiple contracts in the first place.

### Translation (trend bias)

**Right translation** (cycle high leans right / late) = bull; **left translation**
(high leans left / early) = decline [1]. An ideal 20-day cycle is "10 up, 10 down";
a bull might run "15 up, 5 down." Trend is set hierarchically — "the trend to the
time frame you are trading is the dominant cycle in the next longer time frame" [1].

---

## 2. Lineage — Hurst and Dewey, Not Invention

Bressert is explicit that his work is an *applied, quantified* descendant of two
prior bodies of cycle research [1][2].

- **J.M. Hurst** (*The Profit Magic of Stock Transaction Timing*, 1970, + workshops
  Bressert attended): the cyclic/commonality principle, the **nominal model**
  (a hierarchy of cycles each ~twice/half its neighbours — parent of Bressert's
  "next-longer-frame sets the trend"), and the **displaced moving average**, the
  direct mechanical ancestor of the centered detrend [1][2][11].
- **Edward R. Dewey / Foundation for the Study of Cycles** (founded 1941): Bressert
  studied Dewey's books and *The Catalogue of Cycles* (~20,000 cycles), and
  **borrowed the centered-detrend technique directly from the Foundation** by his
  own statement — "the process initially used by the Foundation… I borrowed this
  technique" [1].

The crucial distinction Bressert himself draws: Hurst and the Foundation gave
*theory without tradable structure*. His bio states he "realized that something was
missing… plenty of theory on how to use cycles, but no quantification, or
structure, that would allow him to trade" [2]. The timing bands, RSI3M3 trigger and
money-management frame *are* that quantification. **[UNCONFIRMED nuance]** the
"displaced-MA → centered-detrend" link to Hurst is an analytic inference from
matching mechanics; Bressert's *own* attribution of the detrend is to the
Foundation, so the technique has a dual heritage [1].

---

## 3. The DSS Attribution Question

**Bottom line:** the earliest dated, citable publication of a "Double Smoothed
Stochastic" by that name is **William Blau, TASC, January 1991** [4]. No located
source shows Bressert publishing a *named* DSS before that date. The popular "DSS
Bressert" is a **distinct formula** whose earliest dateable trace is a mid-2000s
platform lexicon — a later popularization, not evidence of earlier origin [5][6].

### The two formulations are mathematically different

**Blau's DSS** (TASC Jan 1991) double-smooths the *components* of one stochastic —
two cascaded EMAs on numerator and denominator separately — then divides **once** [4][12]:

```
DSS_Blau = 100 · EMA_z(EMA_y(C − Lₐ)) / EMA_z(EMA_y(Hₐ − Lₐ))
```

**"DSS Bressert"** (tradesignalonline lexicon / MQL 2008) is a
**stochastic-of-a-stochastic**: compute a stochastic, EMA-smooth it, run the
stochastic transform **again** on the smoothed series, EMA-smooth again [5][6][13]:

```
sto1 = stochastic(close);  xPre = EMA(sto1)
sto2 = stochastic(xPre);   DSS  = EMA(sto2)
```

Blau double-smooths the *inputs* of a single stochastic; "Bressert" re-applies the
*entire transform twice*. They produce different series. The cleanest practitioner
confirmation: Mladen Rakic, who reverse-engineered both, ships them as **two
separate indicators** ("DSS Blau" code/23278 vs. the Bressert "ratio" version
code/23277) [12][14].

### Why the co-attribution exists

Every secondary source hedges authorship ("Blau and Bressert," "designed by William
Blaw," "traced back to Bressert") rather than citing a primary Bressert
publication [5][6][15][16]. The "Bressert" label traces in the dateable record only
to the **tradesignalonline lexicon** (Wayback first capture Dec 2007) and its **Aug
2008** MQL4 implementation [5][6]. This is the signature of an **attribution that
hardened in the retail-platform era** — and notably, Bressert's own March 1998 TASC
interview discusses detrend, RSI3M3 and timing bands but **never mentions a double
smoothed stochastic** [1].

A genuinely Bressert-linked strand does exist: the **EMA(short)/EMA(long) "ratio"
oscillator** that Mladen explicitly traces to him [14]. So the fair characterization
is **two related-but-distinct formulations** — Blau owns the documented DSS; the
"Bressert" construction is a different, platform-propagated variant whose Bressert
attribution is traditional rather than proven. **[UNCONFIRMED]** an earlier
unindexed Bressert DSS cannot be fully excluded (his 1980s newsletter corpus is not
archived), but it cannot be documented either [4][5].

---

## 4. Biography, Firms & Current Status

The richest primary source is Bressert's own archived career overview, corroborated
by the 1998 TASC interview and the Merriman Market Analyst company history [2][1][17].

### Verified timeline

| Period | Event |
|--------|-------|
| Late 1960s | Studied Foundation publications + Hurst; attended Hurst's workshops [2] |
| ~1970s | Commodity broker, West Coast Commodity Exchange floor [1] |
| early 1970s | Studied Edwards & Magee, Gann, Gartley, Elliott; developed the "Bressert Method" + Timing Bands [2] |
| **1974** | Began the **HAL Commodity Cycles** newsletter ("HAL" = High And Low risk) [2] |
| **1976** | Began teaching cycle-trading workshops [2] |
| **1979** | Joined **Tim Slater** to build **CompuTrac** [2][1] |
| **Winter 1980** | Met **Raymond Merriman** in Tucson; Merriman became his apprentice [17] |
| **1981** | *The Blue Book* (HALCO, Dallas, with J.H. Jones) [18] |
| **1985** | **Retired** after 12 years of HAL (profitable 10 of 12 years) [2] |
| **1991** | *The Power of Oscillator/Cycle Combinations* (w/ software floppy) [2][19] |
| **1991–1995** | **CycleWatch** newsletter (fax/DBC Signal/FutureLink/DTN) [2] |
| **1994** | "Award-winning software" → **ProfitTrader** / CycleTrader [2] |
| Present | "Walter is no longer analyzing and trading the markets" [2] |

All **[VERIFIED]** to the cited sources. **[UNCONFIRMED]:** birth date, birthplace,
formal education — not located in any source [3].

### Firms

HALCO / HAL Commodity Cycles (1974–85), Walter Bressert and Associates (1990s),
Walter Bressert Inc., CycleWatch (1991–95), and the websites walterbressert.com
(1998–~2017, now an archive) and bressert.com (son **Jerome Bressert**'s vendor
site, lapsed to a domain-sale parking page by 2024). The active continuation is
**Cycle Trader Pro / CycleTraderPro.com**, run by Jerome [3].

### Foundation for the Study of Cycles — correction

Bressert did **not co-found** the Foundation (Dewey, 1941). His own page says he was
"a **director and president**" of it — a *later leadership role*. The **director**
title is independently corroborated by Merriman's event bio; the **president** title
appears only in his own bio. **[VERIFIED director; "president" UNCONFIRMED]** [2][20].

### Current status — explicit verdict

**UNKNOWN. Do not assert death.** No obituary, death notice, or grave record was
located (findagrave returned HTTP 403, not a confirmed result) [3]. He is
documentably *retired* and out of public activity; his domain lapsed ~2023–24; his
son markets the indicators in the past tense ("My father, Walter Bressert made
these DDS famous for years") — which implies he is no longer operationally involved
but is **not** a death statement [3][21]. Given a late-1960s career start he would
likely be in his 80s+, but no birth year anchors this. **[UNCONFIRMED whether
living or deceased]**.

---

## 5. Influence, Legacy & Critical Assessment

### Legacy — real, as a popularizer and via platform adoption

- **"Brought cycles to the futures markets"** is repeated across independent sources
  (his bio; Merriman calls him a "legendary cycles analyst"), not merely
  self-asserted. Credible as a **popularizer/quantifier** claim; the "first/sole"
  framing is **[UNCONFIRMED]** [2][17].
- **Direct lineage:** Raymond Merriman (MMA, est. 1983) began "in 1980 as an
  apprentice to Walter Bressert" — a documented teacher→prominent-student line [17].
- **Platform adoption of the DSS** is the strongest objective proxy: a 13-strong
  MQL4/MQL5 DSS family (several Bressert-attributed), TradingView Pine scripts,
  ProRealTime/NinjaTrader/TC2000/MetaStock ports, and a commercial CycleTraderPro
  suite [3][6][15]. Caveat: the credit is shared with Blau (§3).
- **[UNCONFIRMED]:** in-text citation by Murphy/Kaufman/Pring/Ehlers could not be
  tested (Google Books API quota 0/day this pass) — a tooling limit, not a negative
  result [3].

### Critical assessment — even-handed

No peer-reviewed study addresses Bressert *by name* (normal for a vendor) [7], so
the assessment evaluates his methods *by category* against the literature.

**Against the predictive core:**

- **Fixed-period cycles have little support.** Spectral analysis found stock-price
  spectra dominated by low-frequency trend and high-frequency noise, with **no
  significant fixed periodicities** — the foundational strike against deterministic
  cycle projection [7]. Markets show time-varying, stochastic quasi-cyclicality at
  best, consistent with weak-form efficiency [8][22].
- **The centered MA uses future data.** A symmetric N-period MA needs ~N/2 *future*
  bars; every clean historical cycle turn it reveals is a **hindsight artifact**,
  and the current turn — the one you want — is exactly the one it cannot locate.
  Displacing it forward reintroduces the same ~N/2 **lag**. No free lunch [1].
- **TA edges erode under data-snooping.** Re-examining the famous Brock-Lakonishok-
  LeBaron (1992) positive result across ~7,800 rules, the apparent significance
  "largely evaporates" and does not survive out-of-sample [9][23][24]. The survey
  literature (Park-Irwin 2007) finds profitability heavily compromised by snooping
  and declining over time [10]. Closest to Bressert's home turf, Marshall et al.
  (2008) test thousands of timing rules on commodity futures and find **no
  profitability after snooping adjustment** [25].
- **Timing bands are descriptive, not validated.** Keeping the central 70% of an
  in-sample interval histogram is an interquantile range, not a calibrated forecast;
  wide bands are "hit" by chance and there is no out-of-sample calibration test [26].
- **Vendor incentive + the Timmermann-Granger paradox:** a genuinely profitable,
  simple, *publicly sold* rule should be arbitraged away as subscribers act on it —
  so decades of a paid fixed-cycle product is weak evidence *for* a real edge [27].

**What genuinely holds up (the steelman):**

1. **Defined-risk money management** — every entry paired with a stop and exit
   plan; the component most robustly tied to survival, and *independent of whether
   cycles exist* [1].
2. **Multi-contract scaling / partial profit-taking** — a legitimate way to manage
   timing uncertainty and P&L path-dependency [1].
3. **Momentum confirmation before acting** — demanding an oscillator turn is, in
   effect, requiring short-horizon return structure, the one TA family with *some*
   academic support [22][28].
4. **Process discipline** — mechanical rules reduce behavioral error, orthogonal to
   the indicators' predictive validity.

**Verdict:** *unproven and partly contradicted on the predictive (cycle-forecasting,
timing-band) claims; sound and standard on the risk-management claims.* Not
"debunked" — absence of a direct study is not proof of failure — but the burden of
proof on the cycle clock is unmet, while the discipline scaffolding is real [10][29].

---

## MQL5 Implementations

Bressert-attributed DSS code in the MQL5/MQL4 CodeBase (full family + forum/Pine
inventory in `trading-research/walter-bressert.md`). Representative, all HTTP 200:

| Code | Author / note | URL |
|------|---------------|-----|
| code/8310 | MetaQuotes (2008); quotes tradesignalonline lexicon; "Blau and Bressert each presented a version" | https://www.mql5.com/en/code/8310 |
| code/789 | Rosh/Kositsin (2012); "proposed by William Blau and Walter Bressert" | https://www.mql5.com/en/code/789 |
| code/23277 | M. Rakic (2018); "DSS of ratio (Bressert)" — the EMA-ratio strand | https://www.mql5.com/en/code/23277 |
| code/23278 | M. Rakic (2018); "DSS Blau" — shipped separately to mark the distinction | https://www.mql5.com/en/code/23278 |
| product/37936 | Jerome Bressert; commercial CycleTraderPro suite | https://www.mql5.com/en/market/product/37936 |

> Note on attribution: "DSS Bressert" on these platforms implements the
> stochastic-of-a-stochastic / EMA-ratio formula (§3), **not** Blau's component
> double-EMA DSS. Blau holds documented priority for the *named* DSS (TASC Jan 1991).

---

## Open Questions

1. Is Walter Bressert living or deceased? (No birth year, no death record.)
2. Do Murphy / Kaufman / Pring / Ehlers cite him in-text? (Books API blocked.)
3. Does any Bressert primary source predate Blau's Jan-1991 named DSS?
4. Birth date / birthplace / education — anywhere? (Likely a book "About the
   Author" page or Tucson public records.)
5. The original tradesignalonline German lexicon text and its first date.

---

## Sources

| # | Source | Status |
|---|--------|--------|
| [1] | Bressert, interviewed by Thom Hartle, "Trading and Control," *TASC* Mar 1998 — https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB3.html | verified |
| [2] | "Walter Bressert's Professional Career: An Overview," walterbressert.com (Wayback) — https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB2.html | verified |
| [3] | Biography/status research pass (Mojeek, Wayback, MQL5); findagrave/Google Books blocked | verified (incl. negative results) |
| [4] | Blau, "Double Smoothed-Stochastics," *TASC* V9N1, Jan 1991 — https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf | verified |
| [5] | tradesignalonline lexicon "DSS (Bressert)," Wayback first capture Dec 2007 — https://web.archive.org/web/20141104164900/http://www.tradesignalonline.com/Lexicon/Default.aspx?name=DSS:+Double+Smoothed+Stochastics+(Bressert) | verified |
| [6] | MQL5 "DSS Bressert" code/8310 (2008), quoting the lexicon — https://www.mql5.com/en/code/8310 | verified |
| [7] | Granger & Morgenstern, "Spectral Analysis of NY Stock Market Prices," *Kyklos* 1963 — https://doi.org/10.1111/j.1467-6435.1963.tb00270.x | verified |
| [8] | Fama, "Efficient Capital Markets," *J. Finance* 1970 — https://doi.org/10.2307/2325486 | verified |
| [9] | Sullivan, Timmermann & White, "Data-Snooping, Technical Trading Rule Performance, and the Bootstrap," *J. Finance* 1999 — https://doi.org/10.1111/0022-1082.00163 | verified |
| [10] | Park & Irwin, "What Do We Know About the Profitability of Technical Analysis?," *J. Econ. Surveys* 2007 — https://doi.org/10.1111/j.1467-6419.2007.00519.x | verified |
| [11] | Hurst, *The Profit Magic of Stock Transaction Timing* (Prentice-Hall, 1970) | verified (book) |
| [12] | MQL5 "DSS Blau" code/23278 (M. Rakic, 2018) — https://www.mql5.com/en/code/23278 | verified |
| [13] | ProRealCode "DSS Bressert" — https://www.prorealcode.com/prorealtime-indicators/dss-bressert-double-smoothed-stochastic/ | verified |
| [14] | MQL5 "DSS of ratio (Bressert)" code/23277 (M. Rakic, 2018) — https://www.mql5.com/en/code/23277 | verified |
| [15] | TradingView "DSS Bressert" (HPotter) — https://www.tradingview.com/script/W9J3VZUu-DSS-Bressert-Double-Smoothed-Stochastic/ | verified |
| [16] | MQL5 "DSS Bressert" code/789 (Rosh/Kositsin, 2012) — https://www.mql5.com/en/code/789 | verified |
| [17] | Merriman Market Analyst, "About Us" — https://www.mmacycles.com/about-us/ | verified |
| [18] | Bressert, *The Blue Book* (HALCO, 1981) — https://openlibrary.org/books/OL15057618M | verified |
| [19] | Bressert, *The Power of Oscillator/Cycle Combinations* (1991), AbeBooks — https://www.abebooks.com/servlet/SearchResults?an=Walter+Bressert | verified |
| [20] | Astrology FL event bio (Merriman/Bressert "director" corroboration) — https://astrologyfla.com/event/ray-merriman-forecast-2024/ | verified |
| [21] | MQL5 user Jerome Bressert (CycleTraderPro) — https://www.mql5.com/en/users/jbressert | verified |
| [22] | Lo & MacKinlay, "Stock Market Prices Do Not Follow Random Walks," *RFS* 1988 — https://doi.org/10.1093/rfs/1.1.41 | verified |
| [23] | Brock, Lakonishok & LeBaron, "Simple Technical Trading Rules…," *J. Finance* 1992 — https://doi.org/10.1111/j.1540-6261.1992.tb04681.x | verified |
| [24] | Hsu & Kuan, "Reexamining the Profitability of Technical Analysis…," *J. Fin. Econometrics* 2005 — https://doi.org/10.1093/jjfinec/nbi026 | verified |
| [25] | Marshall, Cahan & Cahan, "Can Commodity Futures Be Profitably Traded with Quantitative Market Timing Strategies?," *JBF* 2008 — https://doi.org/10.1016/j.jbankfin.2007.12.011 | verified |
| [26] | Critical-assessment research pass (timing-band statistics critique) | verified (inference) |
| [27] | Timmermann & Granger, "Efficient Market Hypothesis and Forecasting," *IJF* 2004 — https://doi.org/10.1016/s0169-2070(03)00012-8 | verified |
| [28] | Lo, Mamaysky & Wang, "Foundations of Technical Analysis," *J. Finance* 2000 — https://doi.org/10.1111/0022-1082.00265 | verified |
| [29] | Critical-assessment synthesis (steelman / verdict) | verified (inference) |

---

## BibTeX

```bibtex
@article{Bressert1998interview,
  author  = {Bressert, Walter and Hartle, Thom},
  title   = {Trading and Control},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1998},
  month   = mar,
  volume  = {16},
  number  = {3},
  note    = {Interview; full text archived at walterbressert.com},
  url     = {https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB3.html},
}

@book{Bressert1991,
  author    = {Bressert, Walter J.},
  title     = {The Power of Oscillator/Cycle Combinations},
  publisher = {Walter Bressert and Associates},
  year      = {1991},
  note      = {Shipped with companion software},
}

@book{Bressert1981bluebook,
  author    = {Bressert, Walter J. and Jones, James Hardie},
  title     = {The {Blue} {Book}},
  subtitle  = {How to Use Cycles with an Overbought/Oversold Index and a Momentum Index for More Consistent Profits},
  publisher = {HALCO, Commodity Research and Brokerage},
  address   = {Dallas, TX},
  year      = {1981},
  url       = {https://openlibrary.org/books/OL15057618M},
}

@article{Blau1991dss,
  author  = {Blau, William},
  title   = {Double Smoothed-Stochastics},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1991},
  month   = jan,
  volume  = {9},
  number  = {1},
  url     = {https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf},
}

@book{Hurst1970,
  author    = {Hurst, J. M.},
  title     = {The Profit Magic of Stock Transaction Timing},
  publisher = {Prentice-Hall},
  year      = {1970},
}

@article{GrangerMorgenstern1963,
  author  = {Granger, Clive W. J. and Morgenstern, Oskar},
  title   = {Spectral Analysis of New York Stock Market Prices},
  journal = {Kyklos},
  year    = {1963},
  volume  = {16},
  number  = {1},
  pages   = {1--27},
  doi     = {10.1111/j.1467-6435.1963.tb00270.x},
}

@article{Fama1970,
  author  = {Fama, Eugene F.},
  title   = {Efficient Capital Markets: A Review of Theory and Empirical Work},
  journal = {Journal of Finance},
  year    = {1970},
  volume  = {25},
  number  = {2},
  pages   = {383--417},
  doi     = {10.2307/2325486},
}

@article{LoMacKinlay1988,
  author  = {Lo, Andrew W. and MacKinlay, A. Craig},
  title   = {Stock Market Prices Do Not Follow Random Walks: Evidence from a Simple Specification Test},
  journal = {Review of Financial Studies},
  year    = {1988},
  volume  = {1},
  number  = {1},
  pages   = {41--66},
  doi     = {10.1093/rfs/1.1.41},
}

@article{Brock1992,
  author  = {Brock, William and Lakonishok, Josef and LeBaron, Blake},
  title   = {Simple Technical Trading Rules and the Stochastic Properties of Stock Returns},
  journal = {Journal of Finance},
  year    = {1992},
  volume  = {47},
  number  = {5},
  pages   = {1731--1764},
  doi     = {10.1111/j.1540-6261.1992.tb04681.x},
}

@article{Sullivan1999,
  author  = {Sullivan, Ryan and Timmermann, Allan and White, Halbert},
  title   = {Data-Snooping, Technical Trading Rule Performance, and the Bootstrap},
  journal = {Journal of Finance},
  year    = {1999},
  volume  = {54},
  number  = {5},
  pages   = {1647--1691},
  doi     = {10.1111/0022-1082.00163},
}

@article{LoMamayskyWang2000,
  author  = {Lo, Andrew W. and Mamaysky, Harry and Wang, Jiang},
  title   = {Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation},
  journal = {Journal of Finance},
  year    = {2000},
  volume  = {55},
  number  = {4},
  pages   = {1705--1765},
  doi     = {10.1111/0022-1082.00265},
}

@article{HsuKuan2005,
  author  = {Hsu, Po-Hsuan and Kuan, Chung-Ming},
  title   = {Reexamining the Profitability of Technical Analysis with Data Snooping Checks},
  journal = {Journal of Financial Econometrics},
  year    = {2005},
  volume  = {3},
  number  = {4},
  pages   = {606--628},
  doi     = {10.1093/jjfinec/nbi026},
}

@article{TimmermannGranger2004,
  author  = {Timmermann, Allan and Granger, Clive W. J.},
  title   = {Efficient Market Hypothesis and Forecasting},
  journal = {International Journal of Forecasting},
  year    = {2004},
  volume  = {20},
  number  = {1},
  pages   = {15--27},
  doi     = {10.1016/s0169-2070(03)00012-8},
}

@article{ParkIrwin2007,
  author  = {Park, Cheol-Ho and Irwin, Scott H.},
  title   = {What Do We Know About the Profitability of Technical Analysis?},
  journal = {Journal of Economic Surveys},
  year    = {2007},
  volume  = {21},
  number  = {4},
  pages   = {786--826},
  doi     = {10.1111/j.1467-6419.2007.00519.x},
}

@article{Marshall2008,
  author  = {Marshall, Ben R. and Cahan, Rochester H. and Cahan, Jared M.},
  title   = {Can Commodity Futures Be Profitably Traded with Quantitative Market Timing Strategies?},
  journal = {Journal of Banking \& Finance},
  year    = {2008},
  volume  = {32},
  number  = {9},
  pages   = {1810--1819},
  doi     = {10.1016/j.jbankfin.2007.12.011},
}

@misc{RakicDSSBlau2018,
  author = {Rakic, Mladen},
  title  = {Double Smoothed Stochastic (Blau)},
  year   = {2018},
  howpublished = {MQL5 CodeBase code/23278},
  url    = {https://www.mql5.com/en/code/23278},
}

@misc{RakicDSSBressert2018,
  author = {Rakic, Mladen},
  title  = {Double Smoothed Stochastic of Ratio (Bressert)},
  year   = {2018},
  howpublished = {MQL5 CodeBase code/23277},
  url    = {https://www.mql5.com/en/code/23277},
}
```
