# DSS Provenance: William Blau vs. Walter Bressert — Who Originated the Double Smoothed Stochastic?

> Research compiled 2026-06-03. Claims are tagged **[DOCUMENTED]** (a dated, citable primary or strong secondary source exists) or **[FOLKLORE/UNCONFIRMED]** (widely repeated but not corroborated by a dated source located during research). All URLs were retrieved during research.

## Question

The "Double Smoothed Stochastic" (DSS) is routinely co-attributed to **William Blau** and **Walter Bressert** — most retail platforms literally name the indicator "DSS Bressert" while their own description credits Blau. This brief establishes the documentary timeline, determines whether the two named formulations are the *same* or *different*, and gives a reasoned verdict on priority and attribution, separating what is dated and citable from what is repeated folklore.

**Bottom line up front:** The earliest *dated, citable* publication of a "Double Smoothed Stochastic" by that name is **William Blau, TASC, January 1991**. No located source shows Bressert publishing a *named* "Double Smoothed Stochastic" before that date. The popular "DSS Bressert" is a **distinct formula** (a stochastic-of-a-stochastic) whose earliest dateable trace is a mid-2000s trading-platform lexicon entry — i.e., a later popularization, not evidence of earlier origin. The co-attribution reflects **two related but mathematically distinct formulations**, not a settled joint invention.

---

## Timeline

| Year | Who | What was published / what is documented | Source URL |
|------|-----|------------------------------------------|------------|
| 1981 | **Bressert** (w/ J.H. Jones) | *The Blue Book* — features an **Overbought/Oversold Index** and a **Momentum Index** for cycle timing. **No "Double Smoothed Stochastic" by that name is documented in the record.** | [OpenLibrary OL15057618M](https://openlibrary.org/books/OL15057618M) |
| **Jan 1991** | **Blau** | **TASC "Double Smoothed-Stochastics"** (Vol. 9, No. 1, `\V09\C01\DOUBLES`). **First dated, citable appearance of a named "Double Smoothed Stochastic."** | [technical.traders.com …DOUBLES.pdf](https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf) |
| May 1991 | Blau | TASC "Double-Smoothed Momenta" (Vol. 9, No. 5) — generalizes the double-EMA smoothing concept to momentum. | [technical.traders.com …DOUBLE.pdf](https://technical.traders.com/archive/article.asp?file=\V09\C05\DOUBLE.pdf) |
| 1991 | **Bressert** | *The Power of Oscillator/Cycle Combinations* — combined oscillator + cycle methodology, detrend-based oscillators, timing bands; shipped with a software floppy. **No "Double Smoothed Stochastic" by that name located in the description.** | [AbeBooks listing](https://www.abebooks.com/servlet/SearchResults?an=Walter+Bressert) |
| Nov 1991 | Blau | TASC "True Strength Index" (Vol. 9, No. 11) — same double-smoothing family. | [technical.traders.com …TRUESTR.pdf](https://technical.traders.com/archive/article.asp?file=\V09\C11\TRUESTR.pdf) |
| Jan 1993 | Blau | TASC "Stochastic Momentum" (Vol. 11, No. 1) — Stochastic Momentum Index (SMI). | [technical.traders.com …STOCHAS.pdf](https://technical.traders.com/archive/article.asp?file=\V11\C01\STOCHAS.pdf) |
| 1995 | Blau | *Momentum, Direction, and Divergence* (Wiley) — collects DSS, TSI, SMI under the double-smoothing framework. | [Wiley/Amazon](https://www.amazon.com/Momentum-Direction-Divergence-Applying-Convergence/dp/0471027294) |
| ≤ Dec 2007 | (attributed to **Bressert**) | **tradesignalonline.com lexicon entry "DSS: Double Smoothed Stochastics (Bressert)"** — earliest *dateable* appearance of the *named "Bressert" formula* (Wayback first capture 27 Dec 2007). | [Wayback capture](https://web.archive.org/web/20141104164900/http://www.tradesignalonline.com/Lexicon/Default.aspx?name=DSS:+Double+Smoothed+Stochastics+\(Bressert\)) |
| Aug 2008 | (attributed to Bressert) | **MQL4/MQL5 "DSS Bressert" code (code/8310)** — implements the tradesignalonline formula; states "One after the other, William Blau and Walter Bressert each presented a version." Published 13 Aug 2008. | [mql5.com/en/code/8310](https://www.mql5.com/en/code/8310) |
| 2012 | (attributed to Bressert) | MQL5 port (code/789, "Rosh"/Kositsin): "proposed by William Blau and Walter Bressert." | [mql5.com/en/code/789](https://www.mql5.com/en/code/789) |
| 2014 | Blau (credited) | TradingView "DSS Bressert" (HPotter): named "Bressert" but description credits **"William Blaw [Blau]."** | [tradingview.com/script/W9J3VZUu](https://www.tradingview.com/script/W9J3VZUu-DSS-Bressert-Double-Smoothed-Stochastic/) |
| 2018 | Both, separated | Mladen Rakic publishes **separate** "DSS Blau" (code/23278) and "DSS of ratio (Bressert)" (code/23277), explicitly distinguishing the two lineages. | [code/23278](https://www.mql5.com/en/code/23278) · [code/23277](https://www.mql5.com/en/code/23277) |
| 2019 | Both (credited) | ProRealCode "DSS Bressert": "proposed by William Blau and Walter Bressert." | [prorealcode.com](https://www.prorealcode.com/prorealtime-indicators/dss-bressert-double-smoothed-stochastic/) |

---

## The two formulations

Multiple independent sources confirm that **Blau's DSS and the "DSS Bressert" formula are not the same calculation**. They share a goal (smooth a raw stochastic by applying exponential smoothing twice) but differ in *what* gets smoothed and *how the stages are chained*.

### Blau's Double Smoothed Stochastic (TASC Jan 1991)

Blau's method applies **two cascaded EMAs separately to the stochastic's numerator and denominator**, then forms the ratio. As reproduced in Mladen Rakic's "DSS Blau" implementation ([code/23278](https://www.mql5.com/en/code/23278)), with `C` = close, `La`/`Ha` = lowest-low/highest-high over `a` days, `Ey`/`Ez` = successive `y`- and `z`-day EMAs:

```
DSS = 100 * EMA_z( EMA_y( C - La ) ) / EMA_z( EMA_y( Ha - La ) )
```

This is a **double-exponential smoothing of the raw stochastic components** — the numerator `(C − La)` and the range `(Ha − La)` are each passed through two EMAs before the division. Blau's broader thesis (TASC May 1991, *Momentum, Direction, and Divergence* 1995) is that *double* EMA smoothing yields a smoother oscillator with less lag than an equivalent single long EMA. **[DOCUMENTED — TASC \V09\C01, Blau 1995, code/23278]**

### The "DSS Bressert" formula (tradesignalonline lexicon / MQL 2008)

The popular "DSS Bressert" is a **stochastic-of-a-stochastic**: compute a full stochastic, EMA-smooth it, then run the stochastic transform **again** on that smoothed series and EMA-smooth the result. From the MQL5 code/8310 description (quoting the tradesignalonline lexicon):

> "1.) The numerator: the difference between the current close and the period low... The denominator: the difference between the period high minus the period low... the quotient... exponentially smoothed and then multiplied by 100. 2.) The method is analogous to 1.) with the distinction that now the prices of the newly calculated price series of 1.) is used."
> — [mql5.com/en/code/8310](https://www.mql5.com/en/code/8310)

The ProRealCode implementation makes the two-stage stochastic explicit ([prorealcode.com](https://www.prorealcode.com/prorealtime-indicators/dss-bressert-double-smoothed-stochastic/)):

```
sto1     = stochastic(PDS,1, close)         // first stochastic
xPreCalc = EMA(EMAlen, sto1)                 // smooth it
sto2     = (xPreCalc - lowest(PDS,xPreCalc)) / (highest(PDS,xPreCalc)-lowest(PDS,xPreCalc)) * 100  // stochastic of the smoothed stochastic
xDSS     = EMA(EMAlen, sto2)                  // smooth again
```

A related strand attributed to Bressert is the **EMA(short)/EMA(long) "ratio" oscillator** (Mladen's "DSS of ratio," [code/23277](https://www.mql5.com/en/code/23277)): "the 'ratio' part of this version can be traced back to Walter Bressert — he uses it as an oscillator." **[DOCUMENTED — code/8310, code/23277, ProRealCode]**

### Why they differ

- **Blau** double-smooths the *components* of one stochastic (EMA-of-EMA on numerator and denominator), then divides **once**. It is a single stochastic whose inputs are double-smoothed.
- **"Bressert"** re-applies the *entire stochastic transform twice* (stochastic → EMA → stochastic → EMA). It is a stochastic computed on a smoothed stochastic.

These produce different output series. Mladen Rakic — who reverse-engineered both from primary sources — deliberately ships them as **two separate indicators** ("DSS Blau" vs. the Bressert "ratio" version), which is the cleanest practitioner-level confirmation that the formulations are genuinely distinct rather than notational variants.

---

## Verdict / what the record supports

**1. Documented priority for the *named* "Double Smoothed Stochastic" belongs to William Blau.**
Blau's TASC article (Vol. 9, No. 1, **January 1991**) is a concrete, dated, citable publication titled "Double Smoothed-Stochastics." It is the earliest located source that introduces a "Double Smoothed Stochastic" under that name. His subsequent 1991–1995 output (Double-Smoothed Momenta, TSI, SMI, the 1995 Wiley book) establishes double-EMA smoothing as a coherent, authored body of work. **[DOCUMENTED]**

**2. Bressert's documented record contains related oscillator/cycle tools — but no located source shows a *named* DSS predating Blau.**
*The Blue Book* (1981) is real and contains an Overbought/Oversold Index and a Momentum Index; *The Power of Oscillator/Cycle Combinations* (1991) is real and combines oscillators with cycle analysis. Neither located description names a "Double Smoothed Stochastic." Bressert's prolific 1980s cycle work (the *HAL Commodity Cycles* newsletter era) was self-published and is **not** in the searchable TASC/online archives, so an earlier Bressert DSS cannot be *disproven* — but it also cannot be *documented*. **[FOLKLORE/UNCONFIRMED]**

**3. The "DSS Bressert" label is a later popularization attached to a different formula.**
The named "DSS Bressert" formula traces, in the dateable record, only as far back as the **tradesignalonline.com lexicon** (Wayback-captured from **December 2007**) and its **August 2008** MQL4 implementation. From there it propagated to MQL5, TradingView, ProRealTime, NinjaTrader, TC2000, etc. Every one of those secondary sources hedges authorship ("Blau and Bressert," "designed by William Blaw," "traced back to Bressert") rather than citing a primary Bressert publication. This is the signature of an **attribution that hardened in the retail-platform era**, not one anchored to a dated original. **[DOCUMENTED that the label is recent; Bressert's primary authorship UNCONFIRMED]**

**4. Therefore the co-attribution is best read as two related-but-distinct formulations, not a joint origin.**
- Blau owns the *documented* "Double Smoothed Stochastic" (component double-EMA, Jan 1991).
- "Bressert" names a *different* construction (stochastic-of-a-stochastic / EMA-ratio oscillator) whose link to Bressert is plausible — it fits his documented use of EMA-ratio oscillators — but is **sourced only to mid-2000s platform lexicons**, not to a dated Bressert original.

The honest characterization: **Blau has priority on the documentary record; "DSS Bressert" is a later, distinct, platform-propagated variant whose Bressert attribution is traditional rather than proven.**

---

## Confidence & gaps

| Item | Confidence | Basis / gap |
|------|-----------|-------------|
| Blau published "Double Smoothed-Stochastics," TASC Jan 1991 | **High** | TASC archive index + multiple secondary confirmations (Mladen code/23278 links the exact PDF). |
| Blau and "Bressert" formulas are mathematically different | **High** | Two independent reconstructions (tradesignalonline/MQL code/8310 vs. Blau/code/23278) show different calculation chains; Mladen ships them separately. |
| Earliest dateable "DSS Bressert" name = tradesignalonline ≤ Dec 2007, MQL 2008 | **Medium-High** | Wayback first capture 27 Dec 2007; MQL4 publish date 08 Aug 2008. Could exist slightly earlier on tradesignalonline before first crawl. |
| Bressert never published a *named* DSS before 1991 | **Medium** | Absence of evidence: his 1981/1991 books describe *other* named indicators, and his newsletter corpus is not archived/searchable. Cannot fully exclude an earlier unindexed source. |
| "1990" date for Blau's article (seen on MQL5 code/23278) | **Low / likely error** | TASC Vol. 9 = 1991; the linked PDF is `\V09\C01` = January 1991. The "1990" is loose folklore; treat **Jan 1991** as authoritative. |
| The tradesignalonline lexicon body text (full original wording/date) | **Gap** | The Wayback capture rendered only page chrome, not the article body; the formula is recovered via the MQL5 quotation of it, not the lexicon page directly. |

### Open gaps worth a future pass
- A page-level scan of *The Power of Oscillator/Cycle Combinations* (1991) and *The Blue Book* (1981) to confirm/deny any "double smoothed stochastic" terminology inside Bressert's own books (only their titles/subtitles and seller descriptions were available here).
- The original German tradesignalonline lexicon text and its first publication date (only the Dec-2007 Wayback shell and the MQL5 re-quote were obtainable).
- Any first-person statement by Bressert claiming the DSS (none located; his March 1998 TASC interview discusses cycles, detrend, RSI3M3, timing bands — **not** a double smoothed stochastic).

---

## Sources

- William Blau, "Double Smoothed-Stochastics," *TASC* Vol. 9 No. 1, Jan 1991 — https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf
- William Blau, *Momentum, Direction, and Divergence* (Wiley, 1995) — https://www.amazon.com/Momentum-Direction-Divergence-Applying-Convergence/dp/0471027294
- Bressert, *The Blue Book* (1981) — https://openlibrary.org/books/OL15057618M
- Bressert, *The Power of Oscillator/Cycle Combinations* (1991) — https://www.abebooks.com/servlet/SearchResults?an=Walter+Bressert
- MQL5 "DSS Bressert" (code/8310, MetaQuotes, 2008), quoting tradesignalonline lexicon — https://www.mql5.com/en/code/8310
- MQL5 "DSS Bressert" (code/789, Rosh/Kositsin, 2012) — https://www.mql5.com/en/code/789
- MQL5 "Double smoothed stochastic Blau" (code/23278, M. Rakic, 2018) — https://www.mql5.com/en/code/23278
- MQL5 "Double smoothed stochastic of ratio" / Bressert EMA-ratio (code/23277, M. Rakic, 2018) — https://www.mql5.com/en/code/23277
- tradesignalonline lexicon "DSS: Double Smoothed Stochastics (Bressert)," Wayback 2007–2014 — https://web.archive.org/web/20141104164900/http://www.tradesignalonline.com/Lexicon/Default.aspx?name=DSS:+Double+Smoothed+Stochastics+(Bressert)
- TradingView "DSS Bressert" (HPotter, 2014/2021) — https://www.tradingview.com/script/W9J3VZUu-DSS-Bressert-Double-Smoothed-Stochastic/
- ProRealCode "DSS Bressert" (Nicolas, 2019) — https://www.prorealcode.com/prorealtime-indicators/dss-bressert-double-smoothed-stochastic/
- Bressert interview, Thom Hartle, "Trading and Control," *TASC* Mar 1998 (no DSS mentioned) — https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB3.html
