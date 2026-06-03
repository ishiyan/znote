# Doug Schaff — Deep Research Brief

> Investigative synthesis. Claims are tagged **[VERIFIED]** (a dated, retrievable
> source was obtained) or **[UNCONFIRMED]** (plausible but not corroborated by a
> located primary source). The STC formula is recovered from convergent
> open-source implementations, not a primary Schaff text — flagged throughout.
> Compiled 2026-06-03.

## Executive Summary

Doug Schaff is a forex trader/programmer known for exactly one thing: the
**Schaff Trend Cycle (STC)**, an oscillator that runs a **MACD line through two
cascaded Lane-style stochastic transforms with EMA smoothing**, producing a 0–100
trend/cycle indicator marketed as "faster and more accurate than MACD" [1][2]. The
man himself is almost undocumented — no birth year, education, photograph,
interview, or verifiable company record could be located — but the *indicator* is
one of the most widely ported in retail trading: built into TradingView, present
across ~25 MQL5/MQL4 CodeBase variants, and implemented in ProRealTime,
NinjaTrader, MotiveWave, cTrader, MetaTrader and Python [3]. His only footprint in
the TASC archive is **two 1999 articles on Euro cycles co-authored with Walter
Bressert** — the cycle-trading pioneer whose "stochastic-of-a-stochastic" DSS
pattern STC's architecture closely mirrors [4][5].

Two findings frame the assessment. First, **STC is, structurally, a faster MACD
with a bounded, double-smoothed display** — a deterministic transform that adds no
information its MACD core lacks; its "earlier" signal is a re-scaling artifact and
its "cleaner" line is low-pass smoothing (which trades whipsaw for lag) [6]. The
0–100 rescaling also reintroduces the **stochastic's trend-pinning weakness** that
the unbounded MACD avoids — a genuine structural regression in exactly the
trending regimes a "trend cycle" tool targets [6]. Second, there is **no
peer-reviewed study of STC by name**, and the by-category FX/timing literature on
its underlying rule class runs mostly negative after costs and data-snooping
adjustment — including studies covering the precise market (FX) and era
(late-1990s) of STC's birth [7][8][9][10]. The honest verdict: a causal,
well-engineered *cosmetic* reformatting of a fast MACD whose durable legacy is
presentational clarity and cross-platform ubiquity, not demonstrated alpha.

---

## 1. The Schaff Trend Cycle, Mechanically

### What it is

```
STC = SecondSmooth( Stochastic( FirstSmooth( Stochastic( MACD ) ) ) ), scaled 0–100
```

The exact algorithm is recoverable from two byte-concordant open-source
implementations — the ProRealCode "schaff-trend-cycle2" code and the pandas-ta
`stc.py` port, which re-implements it [1][2]. The chain, verbatim from the code [1]:

1. **MACD line:** `XMAC = EMA(close, MA1) − EMA(close, MA2)`.
2. **First stochastic %K** of the MACD over `TCLen` bars → 0–100.
3. **EMA smoothing** of that %K (`PF = PF[1] + Factor·(K1 − PF[1])`, an EMA with
   α = Factor; sources label it Lane's "%Fast D").
4. **Second stochastic %K** of the smoothed series `PF` over `TCLen` bars.
5. **EMA smoothing** of that → **STC** (0–100). Flat-window guard: hold previous
   value when high = low to avoid divide-by-zero [1][2].

So STC is a **stochastic-of-a-(smoothed)-stochastic applied to MACD** — a double
stochastic, not a single pass. ProRealCode, pandas-ta and the pandas-ta docstring
("two cascaded stochastic calculations") all confirm two passes; a single-pass
community variant exists but is a simplification, not the reference STC [1][2][11].

### Default parameters

| Parameter | Forex-native | Generic/library | Status |
|-----------|--------------|-----------------|--------|
| Cycle length `TCLen` | **10** | **10** | **[VERIFIED]** consistent [1][2][11] |
| Fast MACD EMA | **23** | 12 | **[VERIFIED as ProRealCode default; UNCONFIRMED as Schaff's own published numbers]** [1][2] |
| Slow MACD EMA | **50** | 26 | same |
| Smoothing factor | **0.5** (EMA α=0.5, ≈3-period) | **0.5** | **[VERIFIED]** [1][2] |
| Overbought / oversold | **75 / 25** (some platforms 80/20) | — | **[VERIFIED — varies by platform]** [1][12][13] |

The **23/50** forex pair is the value that propagates through forex-oriented STC
code [1]; whether Schaff himself published these exact numbers is **[UNCONFIRMED]**
— no primary Schaff source was located. The generic ports default to the classic
MACD 12/26 [2].

### What it claims to solve

The origin claim (Investopedia, attributing Schaff/FX-Strategy): STC "reacts faster
to changing market conditions" and "identifies up and downtrends long before MACD"
because it adds a cycle/time component on top of MACD's EMAs, while the double
smoothing makes it less whippy than a raw stochastic [12]. The same source concedes
the drawback: STC **"can stay in overbought or oversold territory for long
stretches"** — i.e., it pins to 0/100 [12]. The superiority claim is the
author/vendor's; **[UNCONFIRMED]** by any independent test located.

> **Provenance note.** No primary Schaff publication or TASC article that
> *introduces* STC was located; the formula is documented from convergent platform
> code, and the 1999 dating rests on Investopedia [12]. The full text of the two
> 1999 TASC Euro articles is paywalled (HTTP 302 → subscriber login), so whether
> STC appears inside them could not be confirmed [4].

---

## 2. Lineage — a Four-Author Composite

STC is a clean composition of prior work; documented links vs. analytic inference
are tagged [1][2][5][14].

| Author | Contribution to STC | Inheritance | Confidence |
|--------|---------------------|-------------|-----------|
| **Gerald Appel** | MACD line = STC's input | direct, in code | **[VERIFIED]** |
| **George Lane** | stochastic %K + "%D" smoothing, applied twice | direct, in code | **[VERIFIED]** |
| **Walter Bressert** | cycle framing + stochastic-of-a-stochastic (DSS) architecture; 1999 forex collaboration | documented collaboration; strong mechanical match | **[VERIFIED collab; INFERRED copy]** |
| **William Blau** | double-smoothing-before-normalize philosophy | conceptual cousin, different mechanism | **[VERIFIED as cousin]** |

The **Bressert link is the load-bearing one**. Schaff co-authored two 1999 TASC
articles with Bressert in the forex-cycle domain the same year STC is dated to [4].
STC's repeated *stochastic-of-a-stochastic* construction structurally matches the
**"DSS Bressert"** pattern documented in the Bressert brief
(`sto2 = stochastic(EMA(stochastic(x))); out = EMA(sto2)`) — **not** Blau's
component-double-EMA DSS [5][14]. STC differs only in that its input is the MACD
line (rather than price) and it adds smoothing. That the patterns match is
**[VERIFIED]**; that Schaff consciously copied Bressert's DSS is **[INFERRED]** from
the mechanical match plus the documented collaboration. Blau is a *parallel* — same
double-smoothing spirit, different mechanism (he double-EMAs the numerator and
denominator of a single stochastic) [14].

### The 1999 Euro articles (what the collaboration actually was)

| | Article 1 | Article 2 |
|---|-----------|-----------|
| Title | *The Euro's True Colors* | *The Euro's Weekly Cycles* |
| Authors | Walter Bressert & Doug Schaff | Walter Bressert & Doug Schaff |
| Issue | TASC May 1999 (V17:5) | TASC Jun 1999 (V17:6) |
| PDF | `…\V17\C05\033EURO.pdf` | `…\V17\C06\043EURO.pdf` (302→login) |

From the public TASC abstracts: *True Colors* (May) tackles analyzing a currency
**with no price history** (the Euro launched 4 Jan 1999); *Weekly Cycles* (June) is
an explicit follow-up forecasting the Euro's weekly cycles [4][15]. Both are
**cycle/timing pieces in Bressert's idiom**; neither abstract mentions STC, MACD,
or a "trend cycle" indicator. **[VERIFIED via abstracts; STC presence in full text
UNCONFIRMED — paywalled]** [4].

---

## 3. Biography, Firm & Current Status

**Bottom line:** Schaff is a real, named figure — STC's creator and Bressert's
1999 co-author — but the personal record is thin to the point of near-absence [3].

- **The person.** Described across indicator-reference sites as a forex
  trader/programmer who observed that currency trends accelerate and decelerate in
  cycles and built STC to detect turns faster than MACD [3][12]. **Birth year,
  education, nationality, and any photograph/interview/video of the man himself
  could not be located** — every "Schaff" media hit is a third-party tutorial about
  the indicator. **[UNCONFIRMED — unfindable]** [3].
- **"FX Strategy."** The line "Doug Schaff, founder/president of FX Strategy" (or
  "owns FX-Strategy") recurs across secondary STC write-ups [3]. But it **cannot be
  tied to the live `fxstrategy.com` domain**, which Wayback shows as parked/for-sale
  (2005–2008) and later an unrelated Joomla FX-affiliate site with no Schaff content
  [3]. `schafftrendcycle.com` was never archived. No company registration or
  trademark was found. **[UNCONFIRMED — firm status; treat the fxstrategy.com link
  with caution]** [3].
- **Publication.** Schaff's only TASC byline is the two 1999 Euro articles (an
  exhaustive 1982–2025 index grep confirms no others) [3][4]. **STC's first
  publication was *outside* TASC**: the algorithm "was made public in 2008" via the
  forex software ecosystem, then mainstream TA media (Investopedia, by Jan 2010,
  written by Brian Twomey — not Schaff) [3][12]. No canonical "first paper" by
  Schaff was located. **[VERIFIED non-TASC origin ~2008; exact first venue
  UNCONFIRMED]**.
- **Current status.** **UNKNOWN — do not assume deceased.** No death record was
  found (FindAGrave/obituary channels were blocked, not confirmed negative); no
  active personal site, LinkedIn, or firm presence exists. Most likely reading: an
  active forex trader/programmer of the late-1990s–2000s who released STC ~2008 and
  kept a very low profile since. **The man is undocumented; the indicator is
  ubiquitous.** [3].

---

## 4. Adoption & Legacy

STC's cross-platform reach is the strongest objective measure of Schaff's
influence [3]:

- **MQL5/MQL4 CodeBase:** ~25 "Schaff Trend Cycle" entries (base note on the
  canonical code/486: *"Real author: Doug Schaff"*), including a large family of
  variants (DEMA, TEMA, NonLag, Jurik, Hull, CCI, RSI, etc.) [3].
- **TradingView:** built-in `Schaff Trend Cycle (STC)` plus 10+ community Pine
  scripts (adaptive, zero-lag, volume-adjusted, CCI-modified variants) [3].
- **Other platforms:** ProRealTime/ProRealCode, NinjaTrader ecosystem, MotiveWave,
  cTrader, MetaTrader, and Python (pandas-ta) all carry STC [1][2][3].

New variants were still being published in the 2020s (AlgoAlpha, Loxx). The breadth
of porting — and its persistence — is Schaff's durable legacy, independent of
whether the indicator carries an edge. **[VERIFIED]** [3].

> Forum reach (ForexFactory, futures.io, NinjaTrader, etc.) is known to exist but
> could not be enumerated — those sites returned HTTP 403 to automated search this
> pass. The MQL5 and TradingView communities are directly evidenced [3].

---

## 5. Critical Assessment

No peer-reviewed study addresses the STC, Doug Schaff, or FX Strategy's products
**by name** — expected for a branded vendor indicator, and stated plainly: there is
neither academic validation nor academic refutation of STC specifically [6]. The
assessment is therefore *by category*.

### STC vs MACD — structural

1. **No new information.** STC is a deterministic function of MACD, itself a
   deterministic function of price. It cannot contain information the MACD lacks;
   its value is purely presentational (bounding + smoothing) [6].
2. **"Earlier" is a re-scaling artifact.** The stochastic step maps the MACD's
   recent range onto 0–100, so %K saturates toward 100 *before* the MACD rolls over
   in absolute terms — a monotonic transform reaching the edge of its recent range,
   not anticipation of future prices [6].
3. **"Cleaner" is low-pass smoothing → lag.** The double-smoothing suppresses
   whipsaw but delays genuine turns; "earlier" and "cleaner" pull in opposite
   directions, and the net lead is parameter-dependent [6].
4. **Bounded-oscillator pinning — a real regression.** The 0–100 rescaling
   reintroduces the stochastic's trend-pinning failure that the *unbounded* MACD
   avoids: in strong trends STC saturates and fires premature counter-trend reads —
   precisely the regime a "trend cycle" tool is sold to handle [6][12].
5. **Parameter inflation.** ~6–8 free knobs vs MACD's 3 → a larger data-snooping
   surface,    the condition whose correction (White's Reality Check) deflates apparent
   edges [7][8]. In STC's *favor*: it is **causal** (no future data), so unlike
   centered-MA cycle methods it is not guilty of look-ahead — its risk is
   over-fitting/selection, not hindsight [6].

### By-category academic evidence (DOIs Crossref-verified)

- **MACD, directly:** Chong & Ng (2008) found MACD(12,26,9) generated returns on
  the FT30 (1976–2002) — the most direct pro-momentum data point for STC's engine,
  but a single index, not snooping-adjusted, and on *classic* MACD [16].
- **FX, Schaff's home market:** Qi & Wu (2006) — FX rule profits shrink sharply
  under White's Reality Check [9]; **Olson (2004) — MA-rule profits in FX declined
  to near zero by the 1990s**, the very market and era of STC's birth [10]; Neely &
  Weller (2003) — intraday FX rules show little profit after costs [17].
- **General frame:** Park & Irwin (2007) — positives "heavily compromised by
  data-snooping" and declining over time [18]; Sullivan, Timmermann & White (1999)
  — best-rule significance "evaporates" once the search universe is accounted for
  [7]; Marshall et al. (2008) — commodity/futures timing rules don't survive the
  reality check [19]; Brock et al. (1992) as the strongest *pro*-TA result [20];
  Hsu & Kuan (2005) for a calibrated middle reading [21].
- **What momentum has going for it:** Lo-MacKinlay (1988) short-horizon
  autocorrelation [22]; Lo-Mamaysky-Wang (2000) modest pattern information [23].
- **Arbitrage prior:** Timmermann & Granger (2004) — a public, simple, widely
  re-implemented rule (STC is in nearly every platform) is *a priori* unlikely to
  retain an edge [24].

### Steelman — what holds up

- **Readability & cross-market comparability** — a bounded 0–100 line with fixed
  25/75 bands is genuinely easier to read, alert and systematize, and an STC of 80
  means the same on EUR/USD as on gold (a MACD value does not) [6].
- **Noise reduction is real** in choppy regimes (regime-dependent, lag-paying) [6].
- **Momentum is the least-bad TA family** — STC is built on the better end of the
  evidence (Chong-Ng; Lo-MacKinlay), not the discredited fixed-cycle end [16][22].
- **As an attention/gating heuristic** paired with risk management, it is defensible
  *process* even if it adds no alpha over a fast MACD [6].

### Marketing-vs-substance caveats

Vendor incentive (FX Strategy sells education/signals); chart-selection bias;
"earlier and smoother" is a chart-aesthetics claim, not a net-of-cost P&L claim; and
the Timmermann-Granger arbitrage paradox all apply [6][24].

**Verdict:** STC is a causal, well-engineered *cosmetic* reformatting of a fast
MACD — easier to read and threshold, but adding no information its MACD core lacks,
reintroducing the stochastic's trend-pinning weakness, and carrying more parameters
and thus more data-snooping exposure. With no study validating it by name and the
FX/timing literature on its rule class running mostly negative after costs and
snooping adjustment, it is best treated as **unproven and structurally redundant
rather than debunked** — its real value presentational discipline, not demonstrated
alpha [6][7][10].

---

## Articles

| Date | Title | Authors | Category | PDF |
|------|-------|---------|----------|-----|
| May 1999 | The Euro's True Colors | Walter Bressert & Doug Schaff | Market Timing | [\V17\C05\033EURO](https://technical.traders.com/archive/article.asp?file=\V17\C05\033EURO.pdf) |
| Jun 1999 | The Euro's Weekly Cycles | Walter Bressert & Doug Schaff | Market Timing | [\V17\C06\043EURO](https://technical.traders.com/archive/article.asp?file=\V17\C06\043EURO.pdf) |

These are Schaff's only TASC bylines (exhaustive 1982–2025 index check). PDFs are
subscriber-paywalled (HTTP 302 → login). No TASC Traders' Tips entry exists (that
section began in 2009; the articles are from 1999) [3][4].

---

## MQL5 Implementations

Representative STC CodeBase entries (~25 total; all resolve on mql5.com) [3]:

| Code | Title | Platform | Author |
|------|-------|----------|--------|
| [code/486](https://www.mql5.com/en/code/486) | Schaff Trend Cycle ("Real author: Doug Schaff") | MT5 | N. Kositsin |
| [code/7356](https://www.mql5.com/en/code/7356) | Schaff Trend Cycle | MT4 | Scriptor |
| [code/20281](https://www.mql5.com/en/code/20281) | Schaff Trend Cycle | MT5 | M. Rakic |
| [code/20282](https://www.mql5.com/en/code/20282) | Schaff Trend Cycle – DEMA | MT5 | M. Rakic |
| [code/20283](https://www.mql5.com/en/code/20283) | Schaff Trend Cycle – TEMA | MT5 | M. Rakic |
| [code/21787](https://www.mql5.com/en/code/21787) | Schaff Trend Cycle – NonLag MA | MT5 | M. Rakic |
| [code/13434](https://www.mql5.com/en/code/13434) | ColorSchaffRSITrendCycle | MT5 | N. Kositsin |

Plus ports on TradingView (built-in `ta.stc` + 10+ Pine scripts), ProRealCode,
NinjaTrader, MotiveWave, cTrader, and Python pandas-ta — see the open-source
formula references [1][2].

---

## Open Questions

1. Is there any primary Schaff publication defining STC and the 23/50/10/0.5
   defaults in his own words?
2. Does STC appear inside the full text of the 1999 TASC Euro PDFs (paywalled)?
3. Who is Doug Schaff — birth year, education, nationality, a photograph? Is he
   living?
4. What was the real "FX Strategy" entity, and on what domain?
5. Where exactly did STC *first* appear publicly (the ~2008 release venue)?

---

## Sources

| # | Source | Status |
|---|--------|--------|
| [1] | ProRealCode "Schaff Trend Cycle" (schaff-trend-cycle2, F. Malagrida, 2017) — canonical double-stochastic code; defaults 10/23/50/0.5 — https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle2/ | verified (HTTP 200) |
| [2] | pandas-ta-classic `momentum/stc.py` — Python port; "two cascaded stochastic calculations" — https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/momentum/stc.py | verified (HTTP 200) |
| [3] | Biography/adoption research pass (TASC index grep, MQL5 search API, TradingView, Wayback) | verified (incl. negative results) |
| [4] | TASC Vol. 17 (1999) abstracts — both Bressert/Schaff Euro articles; no STC article in index — https://traders.com/Documentation/RESource_docs/VolAbs/V17abs.html | verified (HTTP 200); PDFs paywalled (302) |
| [5] | Walter Bressert deep-research brief (this repo), §3 DSS attribution — `outputs/walter-bressert.md` | verified (local) |
| [6] | STC critical/structural analysis (this research pass) | verified (structural/deductive) |
| [7] | Sullivan, Timmermann & White, "Data-Snooping, Technical Trading Rule Performance, and the Bootstrap," *J. Finance* 1999 — https://doi.org/10.1111/0022-1082.00163 | verified (Crossref) |
| [8] | White, "A Reality Check for Data Snooping," *Econometrica* 2000 — https://doi.org/10.1111/1468-0262.00152 | verified (Crossref) |
| [9] | Qi & Wu, "Technical Trading-Rule Profitability, Data Snooping, and Reality Check: Evidence from the FX Market," *JMCB* 2006 — https://doi.org/10.1353/mcb.2007.0006 | verified (Crossref) |
| [10] | Olson, "Have trading rule profits in the currency markets declined over time?," *JBF* 2004 — https://doi.org/10.1016/s0378-4266(02)00399-0 | verified (Crossref) |
| [11] | ProRealCode "Schaff Trend Cycle" (lolo, 2015) — single-stochastic variant — https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle/ | verified (HTTP 200) |
| [12] | Twomey, "Schaff Trend: A Faster and More Accurate Indicator," Investopedia (origin/1999 claim) — https://www.investopedia.com/articles/forex/10/schaff-trend-cycle-indicator.asp | verified (via Wayback) |
| [13] | MotiveWave STC study docs (0–100, OB 75 / OS 25) — https://docs.motivewave.com/studies/s-t.md | verified (HTTP 200) |
| [14] | William Blau deep-research brief (this repo) — Blau vs Bressert DSS distinction — `outputs/william-blau.md` | verified (local) |
| [15] | TASC Euro article PDFs (paywalled) — `\V17\C05\033EURO.pdf`, `\V17\C06\043EURO.pdf` | blocked (302 → login) |
| [16] | Chong & Ng, "Technical analysis and the London stock exchange: testing the MACD and RSI rules using the FT30," *Applied Economics Letters* 2008 — https://doi.org/10.1080/13504850600993598 | verified (Crossref) |
| [17] | Neely & Weller, "Intraday technical trading in the foreign exchange market," *JIMF* 2003 — https://doi.org/10.1016/s0261-5606(02)00101-8 | verified (Crossref) |
| [18] | Park & Irwin, "What Do We Know About the Profitability of Technical Analysis?," *J. Econ. Surveys* 2007 — https://doi.org/10.1111/j.1467-6419.2007.00519.x | verified (Crossref) |
| [19] | Marshall, Cahan & Cahan, "Can commodity futures be profitably traded…?," *JBF* 2008 — https://doi.org/10.1016/j.jbankfin.2007.12.011 | verified (Crossref) |
| [20] | Brock, Lakonishok & LeBaron, "Simple Technical Trading Rules…," *J. Finance* 1992 — https://doi.org/10.1111/j.1540-6261.1992.tb04681.x | verified (Crossref) |
| [21] | Hsu & Kuan, "Reexamining the Profitability of Technical Analysis…," *J. Fin. Econometrics* 2005 — https://doi.org/10.1093/jjfinec/nbi026 | verified (Crossref) |
| [22] | Lo & MacKinlay, "Stock Market Prices Do Not Follow Random Walks," *RFS* 1988 — https://doi.org/10.1093/rfs/1.1.41 | verified (Crossref) |
| [23] | Lo, Mamaysky & Wang, "Foundations of Technical Analysis," *J. Finance* 2000 — https://doi.org/10.1111/0022-1082.00265 | verified (Crossref) |
| [24] | Timmermann & Granger, "Efficient market hypothesis and forecasting," *IJF* 2004 — https://doi.org/10.1016/s0169-2070(03)00012-8 | verified (Crossref) |
| [25] | EarnForex STC guide — "developed by Doug Schaff… algorithm made public in 2008" — https://www.earnforex.com/guides/schaff-trend-cycle/ | verified by agent (timed out from final-pass env) |

---

## BibTeX

```bibtex
@article{Bressert1999EuroTrueColors,
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

@article{Bressert1999EuroWeeklyCycles,
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

@online{Twomey2010STC,
  author  = {Twomey, Brian},
  title   = {Schaff Trend: A Faster and More Accurate Indicator},
  year    = {2010},
  howpublished = {Investopedia},
  note    = {Live by 2010-01-17 (Wayback); credits Doug Schaff, STC developed 1999},
  url     = {https://www.investopedia.com/articles/forex/10/schaff-trend-cycle-indicator.asp},
  urldate = {2026-06-03},
}

@online{Malagrida2017STC,
  author  = {Malagrida, Francesco},
  title   = {Schaff Trend Cycle (open-source double-stochastic implementation)},
  year    = {2017},
  howpublished = {ProRealCode},
  note    = {Canonical code; defaults TCLen=10, MA1=23, MA2=50, Factor=0.5},
  url     = {https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle2/},
  urldate = {2026-06-03},
}

@misc{PandasTaSTC,
  author = {{pandas-ta-classic contributors}},
  title  = {Schaff Trend Cycle (STC) -- momentum/stc.py},
  year   = {2020},
  howpublished = {GitHub: xgboosted/pandas-ta-classic},
  url    = {https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/momentum/stc.py},
}

@online{Kositsin486STC,
  author  = {Kositsin, Nikolay},
  title   = {Schaff Trend Cycle (Real author: Doug Schaff)},
  howpublished = {MQL5 Code Base, code/486},
  note    = {Algorithm made public in 2008},
  url     = {https://www.mql5.com/en/code/486},
  urldate = {2026-06-03},
}

@online{EarnForexSTC,
  author  = {{EarnForex}},
  title   = {Schaff Trend Cycle},
  note    = {Attributes STC to Doug Schaff; algorithm made public in 2008},
  url     = {https://www.earnforex.com/guides/schaff-trend-cycle/},
  urldate = {2026-06-03},
}

@article{White2000,
  author  = {White, Halbert},
  title   = {A Reality Check for Data Snooping},
  journal = {Econometrica},
  year    = {2000},
  volume  = {68},
  number  = {5},
  pages   = {1097--1126},
  doi     = {10.1111/1468-0262.00152},
}

@article{ChongNg2008,
  author  = {Chong, Terence Tai-Leung and Ng, Wing-Kam},
  title   = {Technical Analysis and the London Stock Exchange: Testing the MACD and RSI Rules Using the FT30},
  journal = {Applied Economics Letters},
  year    = {2008},
  volume  = {15},
  number  = {14},
  pages   = {1111--1114},
  doi     = {10.1080/13504850600993598},
}

@article{QiWu2006,
  author  = {Qi, Min and Wu, Yangru},
  title   = {Technical Trading-Rule Profitability, Data Snooping, and Reality Check: Evidence from the Foreign Exchange Market},
  journal = {Journal of Money, Credit and Banking},
  year    = {2006},
  volume  = {38},
  number  = {8},
  pages   = {2135--2158},
  doi     = {10.1353/mcb.2007.0006},
}

@article{Olson2004,
  author  = {Olson, Dennis},
  title   = {Have Trading Rule Profits in the Currency Markets Declined Over Time?},
  journal = {Journal of Banking \& Finance},
  year    = {2004},
  volume  = {28},
  number  = {1},
  pages   = {85--105},
  doi     = {10.1016/s0378-4266(02)00399-0},
}

@article{NeelyWeller2003,
  author  = {Neely, Christopher J. and Weller, Paul A.},
  title   = {Intraday Technical Trading in the Foreign Exchange Market},
  journal = {Journal of International Money and Finance},
  year    = {2003},
  volume  = {22},
  number  = {2},
  pages   = {223--237},
  doi     = {10.1016/s0261-5606(02)00101-8},
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
```
