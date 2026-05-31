# Dr. Manfred G. Dürschner — Trading Research Profile

## Biography

| Field | Detail |
|-------|--------|
| Full name | Dr. Manfred G. Dürschner |
| Title | Dr. (German doctorate) |
| Location | Germany |
| Affiliation | VTAD (Vereinigung Technischer Analysten Deutschlands e.V.) — German TA society, IFTA member |
| Known for | "3rd Generation Moving Average" / "Moving Averages 3.0" — lag-free MA using sampling theorem |
| Awards | **1st Prize, VTAD Award 2011** for "Gleitende Durchschnitte 3.0" |
| Publications | 2 IFTA Journal articles (2012, 2014); 1 VTAD Award paper (2011) |
| Professional background | Unknown — likely engineering/signal processing (uses sampling theorem from signal transmission theory) |
| Public profile | Low — no social media, interviews, or videos found |

### About

Dr. Manfred G. Dürschner is a German technical analyst who won the prestigious **1st Prize VTAD Award 2011** for his paper "Gleitende Durchschnitte 3.0" (Moving Averages 3.0). His core contribution is applying the **Nyquist-Shannon sampling theorem** from signal processing to modify standard moving averages (SMA, EMA, WMA), producing lag-reduced variants he calls "3rd Generation Moving Averages."

His approach uses a sampling period parameter to estimate and subtract the lag component from a standard MA, yielding an MA that tracks trends accurately while maintaining smoothness. The technique is mathematically elegant and computationally simple.

---

## TASC Publications

**None.** Dr. Dürschner has no articles in Technical Analysis of Stocks & Commodities (confirmed via TASC author search).

---

## IFTA Journal Publications

| Year | Title | Pages | Notes |
|------|-------|-------|-------|
| 2012 | Moving Averages 3.0 | 27–32 | English version of VTAD Award paper |
| 2014 | How to Determine Trends Accurately | 40–41 | Trend determination methodology |

---

## VTAD Award Paper (2011)

**Title:** Gleitende Durchschnitte 3.0 (Moving Averages 3.0)
**Award:** 1st Prize, VTAD Award 2011
**Language:** German (English version published in IFTA Journal 2012)

**Abstract (translated):**
> The best-known moving averages (MA) — simple (SMA), exponential (EMA), and weighted (WMA) — are modified using the sampling theorem from signal transmission theory. These modified MAs ("Moving Averages 3.0") exhibit very good smoothing depending on period settings, represent trends very well, and detect trend reversals computationally without time delay. They represent a significant improvement over conventional standard MAs ("Moving Averages 1.0"). The effectiveness is demonstrated through several tests and a simple, profitable trading system based on such a modified MA.

**PDF:** [M_Duerschner_Gleitende_Durchschnnitte_3.pdf](https://web.archive.org/web/20140318142320/http://www.vtad.de/sites/files/forschung/M_Duerschner_Gleitende_Durchschnnitte_3.pdf) (Wayback Machine, 2.4 MB)
**Presentation:** [Award2011_1_Duerschner.pdf](https://web.archive.org/web/20140318142320/http://www.vtad.de/sites/files/forschung/Award2011_1_Duerschner.pdf) (Wayback Machine)

---

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| 3rd Generation Moving Average (3GMA / MA 3.0) | VTAD Award 2011 | Adaptive MA / Lag Reduction |

### 3rd Generation Moving Average — Technical Description

**Mechanism:** Takes any standard MA (SMA, EMA, WMA) and subtracts an estimate of the lag, derived using the sampling theorem.

**Formula** (from MQL4 code, confirmed by forum posts):

```
// Parameters:
//   MA_Period       - main MA period
//   MA_Sampling_Period - sampling period (should be < 1/4 of MA_Period)
//   MA_Method       - 0:SMA, 1:EMA, 2:SMMA, 3:LWMA

// Compute Lambda and Alpha from sampling period
Lambda = MA_Period / MA_Sampling_Period
Alpha  = Lambda * (MA_Period - 1) / (MA_Period - Lambda)

// 3rd Gen MA = (1 + Alpha) * MA(price) - Alpha * MA(MA(price))
3GMA = (1 + Alpha) * MA1 - Alpha * MA2
// where MA1 = MA(Price, Period) and MA2 = MA(MA1, Period)
```

**Key properties:**
1. Subtracts the estimated lag via a linear combination of MA and MA-of-MA
2. `Alpha` coefficient derived from the sampling theorem (Nyquist relationship)
3. Sampling period must be less than 1/4 of MA period for proper operation
4. Works with any base MA type (SMA, EMA, SMMA, LWMA)
5. Reduces lag to near-zero while maintaining smoothing
6. Simple computation — only requires two standard MAs and an algebraic combination

**Relationship to other lag-reduction methods:**
- Similar in spirit to Hull MA (which uses WMA(2*WMA(n/2) - WMA(n))) but with a theoretically motivated coefficient
- More rigorous than ad-hoc zero-lag approaches
- The sampling theorem provides the mathematical justification for the specific Alpha value

---

## MQL5 Implementations

| Title | Author | Platform | URL |
|-------|--------|----------|-----|
| 3rdgenma.mq4 | Tsar (forum post) | MT4 | [mql5.com/en/forum/182120](https://www.mql5.com/en/forum/182120) |

**Note:** The original MQL4 code was shared in the MQL5 forum in February 2013, posted by user "Tsar" referencing Dürschner's VTAD paper. No official MQL5 CodeBase entry exists under Dürschner's name.

Additional implementations found via forum:
- 3rd Generation MA histogram variant (requested/created in same thread)
- Referenced in "Experiments" thread by user "altoronto" (2016)

---

## GitHub Repositories

**None found.** No GitHub repositories dedicated to the 3rd Generation Moving Average or referencing Dürschner.

---

## Forum Discussions

| Forum | Thread | Date | Notes |
|-------|--------|------|-------|
| MQL5 Forum | [Moving Average [MA] - Next Generation & Variant](https://www.mql5.com/en/forum/182120) | 2013-02-23 | Original MQL4 code shared; references vtad.de/node/1441 |
| MQL5 Forum | [Experiments...](https://www.mql5.com/en/forum/186064/4507741#comment_4507741) | 2016-05-21 | User "altoronto" posts full code with comments referencing "Dr. Mafred Durschner" |

---

## Platform Adoption

| Platform | Status |
|----------|--------|
| TradingView | Not a built-in indicator; community scripts may exist |
| NinjaTrader | Not found |
| MetaTrader 4/5 | Forum code only (not in official CodeBase) |
| ProRealTime | Not confirmed |

Unlike ALMA or HMA, the 3rd Generation MA has **not achieved mainstream platform adoption** despite winning a prize and being published in IFTA Journal. Its adoption remains limited to forum enthusiasts.

---

## Academic Papers

No papers found in Crossref, Semantic Scholar, or arXiv. Dürschner's work is published exclusively through VTAD and IFTA.

---

## Photos, Videos & Interviews

### Photos

| Description | URL | Source |
|-------------|-----|--------|
| [URL not found] No photo found | — | — |

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
| **Alan Hull** | HMA uses similar subtract-lag approach but with ad-hoc coefficients |
| **Patrick Mulloy** | DEMA/TEMA — earlier lag-reduction via multiple EMAs |
| **John Ehlers** | DSP-based filter design; Dürschner's sampling theorem approach is from same tradition |
| **Tim Tillson** | T3 — iterative smoothing for lag reduction |
| **Arnaud Legoux** | ALMA — Gaussian FIR approach to same problem (smooth + low-lag) |

---

## Key Dates

| Date | Event |
|------|-------|
| 2011 | 1st Prize VTAD Award for "Gleitende Durchschnitte 3.0" |
| 2011 (May) | First archived VTAD page (vtad.de/node/1441) |
| 2012 | English version published in IFTA Journal (pp. 27–32) |
| 2013 (Feb) | MQL4 code shared on MQL5 forum by user "Tsar" |
| 2014 | Second IFTA Journal article: "How to Determine Trends Accurately" (pp. 40–41) |

---

## Assessment

Dürschner's 3rd Generation MA is a theoretically well-motivated lag-reduction technique that deserves more attention than it has received. The key insight — using the sampling theorem to derive the exact coefficient needed to cancel lag — is more rigorous than Hull's or Mulloy's empirical approaches. However, the indicator suffers from:

1. **Poor discoverability** — published in German first, English only in IFTA Journal (not widely read by retail traders)
2. **No catchy name** — "3rd Generation MA" is generic; "Moving Averages 3.0" sounds like a version number
3. **No platform adoption** — not built into any major platform
4. **No ongoing advocacy** — Dürschner published 2 articles and disappeared from public view

The formula itself is trivially simple to implement (just `(1+α)*MA - α*MA(MA)`) and the parameter derivation from sampling theory is sound. It represents an underappreciated contribution to the MA literature.

---

## BibTeX

```bibtex
@article{ifta2012:durschner_ma3,
  author  = {Dürschner, Manfred G.},
  title   = {Moving Averages 3.0},
  journal = {IFTA Journal},
  year    = {2012},
  pages   = {27--32},
  url     = {https://www.ifta.org/assets/docs/d_ifta_journal_12.pdf},
  note    = {ISSN 2409-0271. English version of VTAD Award 2011 paper.}
}

@article{ifta2014:durschner_trends,
  author  = {Dürschner, Manfred G.},
  title   = {How to Determine Trends Accurately},
  journal = {IFTA Journal},
  year    = {2014},
  pages   = {40--41},
  url     = {https://www.ifta.org/assets/docs/d_ifta_journal_14.pdf},
  note    = {ISSN 2409-0271}
}

@online{vtad2011:durschner_gd3,
  author  = {Dürschner, Manfred G.},
  title   = {Gleitende Durchschnitte 3.0 (Moving Averages 3.0)},
  url     = {https://web.archive.org/web/20140318142320/http://www.vtad.de/node/1441},
  urldate = {2026-05-31},
  year    = {2011},
  note    = {1st Prize VTAD Award 2011. Full PDF: https://web.archive.org/web/20140318142320/http://www.vtad.de/sites/files/forschung/M_Duerschner_Gleitende_Durchschnnitte_3.pdf}
}

@online{vtad2011:durschner_presentation,
  author  = {Dürschner, Manfred G.},
  title   = {VTAD Award 2011 Presentation --- Gleitende Durchschnitte 3.0},
  url     = {https://web.archive.org/web/20140318142320/http://www.vtad.de/sites/files/forschung/Award2011_1_Duerschner.pdf},
  urldate = {2026-05-31},
  year    = {2011},
  note    = {Presentation slides for VTAD Award ceremony}
}

@online{mql5forum:3rdgenma,
  author  = {{Tsar (Tsar2508)}},
  title   = {Moving Average [MA] - Next Generation \& Variant},
  url     = {https://www.mql5.com/en/forum/182120},
  urldate = {2026-05-31},
  year    = {2013},
  note    = {MQL5 forum thread with MQL4 implementation of 3rd Generation MA, referencing Dürschner's VTAD paper}
}
```
