# Walter Bressert — Indicator(s) & Implementation Plan

Walter Bressert is a **multi-indicator author**, and — unlike Doug Schaff — the
implementation surface splits into several different source-of-truth regimes. This
document is both the indicator list and the plan for deciding **what can be
implemented now, what is partial, and what is blocked.**

> **Revision note (2026-06).** This plan was originally written *before* Bressert's
> books were digitized, and it listed the 3-10 oscillator, timing bands, and PTI as
> "book-only / BLOCKED." Eight primary texts have since been OCR'd into this repo
> (1991, 1992, 1997, 1998, 2000, 2001, 2002, 2003 + the 1998 TASC interview). This
> revision **re-grounds every claim in the actual book text** with `file:line`
> citations. Net effect: several items moved **BLOCKED → READY/PARTIAL**; a set of
> ProfitTrader *software* black boxes (DoubleStoc, BLine, HAL, DTI, trailing stops)
> are now explicitly catalogued as BLOCKED; and PTI / Momentum Index /
> Overbought-Oversold Index are confirmed **absent from every digitized file.**

> **TL;DR.** A larger READY set than previously believed is implementable **with no
> further acquisition** — RSI3M3 (+ its 5-bar detrend), the centered and real-time
> **detrends**, and the **3-10 oscillator** are all defined in Bressert's own books;
> the standard oscillators (CCI, MACD, EMA, MA, RSI, Stochastic) have full textbook
> formulas in the **1991 appendix**. The **DoubleStoc / BLine / HAL / DTI / trailing
> stops** ProfitTrader indicators are **black-boxed in every source** ("a stochastic
> of a stochastic, with another twist or two") and remain platform-conformance-only
> or blocked. **PTI, Momentum Index, and the Overbought/Oversold Index are defined
> nowhere in the digitized corpus** (Blue Book, 1981, is not in hand).

---

## Indicator List

| # | Indicator | Category | Source of truth | Primary author text? | Status |
|---|-----------|----------|-----------------|----------------------|--------|
| 1 | **RSI3M3** (3-period RSI smoothed by 3-bar MA) | Oscillator / trigger | **Author primary** (1997, 1998 manuals + 1998 TASC) | **Yes** — full formula | **READY** |
| 2 | **RSI3M3 Detrend** (`RSI3M3 − SMA(RSI3M3,5)`) | Oscillator / detrend | **Author primary** (1997, 1998) | **Yes** — full formula | **READY** |
| 3 | **3-10 Oscillator** (`SMA(3) − SMA(10)`; crossover = 16-term MA) | Oscillator | **Author primary** (1991 book) | **Yes** — full formula | **READY** *(was BLOCKED)* |
| 4 | **Real-time detrend** (`price − N-MA`) | Cycle / detrend | Author primary (1997, 1998, TASC) | Yes | READY (trivial; weak alone) |
| 5 | **Centered detrend** (`price − N-MA` displaced back N/2) | Cycle / detrend | Author primary (1997, TASC) | Yes | **READY but NON-CAUSAL** — offline/batch only |
| 6 | **MACD Detrend** (COMPUTRAC MACD 26/12/9, detrend around crossover, 3-MA) | Oscillator | Author primary (1991 book) | Yes | READY (3-step recipe) |
| 7 | **Fibonacci oscillator Buy/Sell lines** (`×.618` of prior osc hi/lo) | Band / level | Author primary (1991 book) | Yes | READY |
| 8 | **Keltner band (Bressert variant)** (`MA(5) ± 1.1·σ`) | Band / S&R | Author primary (1997) | Yes | READY *(note: std-dev, not ATR)* |
| 9 | **CCI, MACD, EMA, MA, RSI, Stochastic** (standard) | Oscillator | **1991 Appendix** (textbook formulas) | Yes (credits Lambert/Appel/Wilder) | READY (not Bressert originals) |
| 10 | **Timing Bands** ("middle 70%") | Cycle / forecast | Concept + worked example; **estimator informal** | **Yes** (method described) | **PARTIAL** *(was BLOCKED)* — implementable-with-decisions |
| 11 | **EMA Trend / EMA %Diff / MA %Diff** | Trend | Operation stated; **EMA lengths never stated** | Partial | **PARTIAL — needs periods pinned** |
| 12 | **DoubleStoc / DBS5 / DBS10** (Bressert Double Stochastic) | Oscillator | Platform ports only; **"twist or two" undisclosed** | No | **BLOCKED → conform-to-port only** |
| 13 | **BLine** (RSI-based oscillator) | Oscillator | Named only (2002/2003); no arithmetic | No | **BLOCKED — needs source** |
| 14 | **HAL OB/OS** (A/B versions) | Oscillator / band | Named only (2002); no arithmetic | No | **BLOCKED — likely Blue-Book lineage** |
| 15 | **DTI (Dynamic Trend Indicator)** | Trend | Named only (2002); no arithmetic | No | **BLOCKED** |
| 16 | **Trailing stops** (Multi-Bar, Dynamic ST/LT) | Exit | Named only (2002); no arithmetic | No | **BLOCKED** |
| 17 | **Mid-Cycle Pause (MCP) / Fibonacci forecaster** | Price forecast | Concept only | Partial | **BLOCKED — arithmetic unstated** |
| 18 | **Overbought/Oversold Index** | Oscillator | **Only *The Blue Book* (1981)** — not digitized | Book only | **BLOCKED — needs Blue Book** |
| 19 | **Momentum Index** | Oscillator | **Only *The Blue Book* (1981)** — not digitized | Book only | **BLOCKED — needs Blue Book** |
| 20 | **Profit-Taking Index (PTI)** | Exit / target | **Absent from entire digitized corpus** | None located | **BLOCKED — no source in hand** |
| — | Setup-bar / entry-stop, Left/Right Translation, Bear-Kiss/OSCAR, multi-contract scaling | **Strategy rules / patterns** | Author primary | Yes | Implement as signal logic if a system is built |

---

## Part A — Source-of-Truth Regimes

The books rebalanced the picture. There are now **four** regimes, not three.

### A.1 Regime 1 — Author-defined, formula in a primary text (the BIG win)

The digitized books supply **explicit arithmetic** for far more than the interview did:

- **RSI3M3** — *"a regular RSI 3 smoothed with a 3-bar moving average called the
  RSI3M3"* (1997 content.md:98); *"a 3-bar RSI smoothed with a 3-bar moving average"*
  (1998 content.md:41); *"a 3 RSI smoothed with a 3 MA"* (1998 TASC content.md:164,176).
- **RSI3M3 Detrend** — *"a 5-bar moving average of the RSI3M3 … subtracted from the
  RSI3M3 oscillator to produce the detrended oscillator"* (1997:131; 1998:59).
- **Centered detrend** — full procedure (MA = cycle length, shifted back N/2,
  subtract from high & low) (1997:72-78; TASC:204-208).
- **Real-time detrend** — same minus the back-shift (TASC:212; 1992:366).
- **3-10 Oscillator** — *"the 3-Day Moving Average minus a 10-Day Moving Average …
  the Crossover, which is a 16-Term Moving Average of the oscillator"*
  (1991 ch-13.md:7,11).
- **MACD Detrend** — 3-step recipe: run COMPUTRAC MACD (26,12,9); detrend via Spread
  around the crossover; 3-term MA of the spread (1991 ch-08.md:98-102).
- **Fibonacci oscillator Buy/Sell lines** — `×.618` of the prior oscillator high/low
  (1991 ch-07.md:27,31).
- **Keltner band (Bressert variant)** — *"A 5-week moving average … the Keltner
  Channel is plotted 1.1 standard deviations above and below"* (1997:297). Note: he
  labels it "Keltner" but bands on **standard deviation** (a Bollinger-style band),
  not the classic ATR Keltner.
- **Standard library** — CCI, MACD, EMA, MA, RSI, fast/slow Stochastic each have a
  closed-form formula in the **1991 Appendix** (ap-01.md:5-105), credited to
  Lambert, Appel, and Wilder.

Validation = conform to the author's stated construction + invariant checks;
residual ambiguities become recorded **decisions** (see Part C).

### A.2 Regime 2 — Platform-canonical, attribution-disputed (DoubleStoc)

"**DSS Bressert**" / DoubleStoc is the STC situation exactly, and the 2003 manual
*confirms* the formula is deliberately withheld:

> *"The oscillator is a stochastic of a stochastic, with another twist or two."*
> — 2003 content.md:160

- **No author publication** gives the arithmetic. The "twist or two" is the
  proprietary core and is **never disclosed in any digitized file.**
- The *named* "Double Smoothed Stochastic" has documented priority by **William Blau
  (TASC, Jan 1991)** — and Blau's formula is **mathematically different** (he
  double-smooths the *components* of one stochastic; "Bressert" re-applies the
  *entire stochastic transform twice*). Mladen Rakic ships them as **two separate
  indicators** (MQL5 code/23278 "Blau" vs code/23277 "Bressert ratio").
- The "Bressert" label's earliest dateable trace is a **mid-2000s platform lexicon**
  (tradesignalonline, Wayback Dec 2007) + its **Aug 2008** MQL4 port.

Treatment: **declare a reference, conform byte-for-byte, claim concordance not
authorship** — and flag that the "twist or two" means **even a perfect port may not
match Bressert's shipped software.** 13+ MQL implementations + ProRealCode + Pine +
NinjaTrader to triangulate against.

### A.3 Regime 3 — Software black boxes (BLOCKED, no public source at all)

The ProfitTrader 6.0 suite (2002/2003 manuals) names several indicators but gives
**only usage, Styles, and Inputs — never arithmetic**:

- **BLine** — described as RSI-based, turns slower than DoubleStoc, higher hit-rate
  (2002 content.md; 2003:113) — **no formula.**
- **HAL (High And Low) OB/OS Indicator** — A and B band versions (2002) — **no
  formula.** Likely the lineal descendant of the Blue Book "Overbought/Oversold
  Index" (HAL = Bressert's "HALCO" / "High And Low" brand).
- **DTI (Dynamic Trend Indicator)** — named (2002) — **no formula.**
- **Trailing stops** — Multi-Bar, Dynamic Short-Term, Dynamic Long-Term (2002) — **no
  formula.**
- **Mid-Cycle Pause (MCP)** — concept (2002) — **arithmetic unstated.**

These are blocked pending a source that actually discloses the math (decompiled
MetaStock/ProfitTrader formulas, or a third-party reimplementation if one exists).

### A.4 Regime 4 — Book-only, book NOT in hand (BLOCKED)

- **Overbought/Oversold Index** and **Momentum Index** — the two indices in *The Blue
  Book* (1981) subtitle. **Absent from every digitized file** (confirmed by search
  across all eight books + interview). The Blue Book is **not yet digitized.**
- **Profit-Taking Index (PTI)** — name appears only in reseller/course materials;
  **does not appear anywhere in the digitized corpus** (the phrase "profit taking"
  occurs only as a verb, e.g. 1991 ch-11.md:474, 1997:243). Mechanics public nowhere.

---

## Part B — Books: status

**All indicator-bearing Bressert books except *The Blue Book* are now digitized in
this repo.** The acquisition recommendation has therefore largely been satisfied.

| Source | In repo? | Carries | Notes |
|--------|----------|---------|-------|
| ***The Power of Oscillator/Cycle Combinations*** (1991) | **YES** (`1991-*/`) | 3-10 oscillator arithmetic, MACD-detrend recipe, Fibonacci osc lines, **standard-indicator appendix**, smoothed-CCI/RSI combos | The single most formula-dense Bressert text. ~15% codeable math, rest charts/research tables/psychology |
| ***Cycle Trading Pattern Manual*** (1997) | **YES** (`1997-*/`) | **Most implementable** — centered detrend, RSI3M3, RSI3M3 detrend, Keltner, entry/stop mechanics | ~45-55% codeable |
| ***Trading With Time Fractals*** (1998) | **YES** (`1998-*/`) | RSI3M3, 3M3 detrend, entry mechanics, concrete timing-band numbers | ~30-40% codeable |
| *Cycles, Patterns and Oscillators…* (1992) | **YES** (`1992-*/`) | Detrend subtraction, entry mechanics, Bear-Kiss/OSCAR pattern | Workshop transcript; ~10-15% math |
| 2000 / 2001 / 2002 / 2003 | **YES** | Parameter Inputs, thresholds, usage | Marketing + software manuals; **~85-90% non-math** |
| 1998 TASC interview "Trading and Control" | **YES** (`tasc/1998-03-*/`) | Primary definitions of detrends, RSI3M3, timing-band concept | The original primary source |
| ***The Blue Book*** (1981) | **NO** | Overbought/Oversold Index, Momentum Index (#18, #19) | Rare, HALCO Dallas — **only outstanding acquisition** |
| Course *"Reducing Risk Using Cycles and Oscillators"* | NO | Possibly PTI + timing-band mechanics | Non-authoritative provenance |
| *12 Cardinal Mistakes…* | n/a | nothing (psychology) | SKIP |

**You do NOT need any further book for the READY set (Part A.1).** The only book
worth acquiring is *The Blue Book* — and only for indicators #18 & #19.

---

## Part C — Canonical Specifications (what we can pin down today)

### C.1 RSI3M3 (Regime 1 — author-defined)

Author's words: *"a regular RSI 3 smoothed with a 3-bar moving average"* (1997:98).

```
rsi3      = RSI(close, period=3)
rsi3m3[i] = SMA(rsi3, 3)[i]          # 3-bar simple MA of the 3-period RSI
detrend[i] = rsi3m3[i] - SMA(rsi3m3, 5)[i]   # the RSI3M3 detrend (1997:131, 1998:59)
```

Buy/sell lines are **NOT universal constants** — see Part C.7.

### C.2 3-10 Oscillator (Regime 1 — author-defined, NEWLY UNBLOCKED)

*"the 3-Day Moving Average minus a 10-Day Moving Average … the Crossover, which is a
16-Term Moving Average of the oscillator"* (1991 ch-13.md:7,11).

```
osc3_10[i]   = SMA(price, 3)[i] - SMA(price, 10)[i]
crossover[i] = SMA(osc3_10, 16)[i]
```

`price` defaults to close. Patterns (Two-Step Sell, Small-Bump Sell, Bear-Kiss/OSCAR)
are built on the oscillator's crossings of the crossover and zero line (ch-13.md:15;
1992:560-562) and are **signal logic**, not part of the oscillator value.

### C.3 Detrends (Regime 1 — author-defined)

```
real_time_detrend[i] = price[i] - SMA(price, N)[i]                 # causal, right-edge usable
centered_detrend[i]  = price[i] - SMA(price, N)[i + N/2]           # NON-CAUSAL: uses N/2 future bars
```

The 1997 manual applies the centered detrend to **high and low separately**
(`detrend_hi = high − centeredMA`, `detrend_lo = low − centeredMA`) with bands at
**±0.80** (typical top/bottom) and **±2.0** (extreme) (1997:78). `N` = dominant cycle
length, **default 20**. **Centered detrend uses future data** and is a zero-phase /
non-causal filter — implement only as an offline/batch transform and flag the
look-ahead. The manual itself says it *"cannot be used for real-time trading"*
(1997:80).

### C.4 MACD Detrend (Regime 1 — author-defined)

3-step recipe (1991 ch-08.md:98-102):

```
macd      = EMA(close,12) - EMA(close,26)          # COMPUTRAC MACD
signal    = EMA(macd, 9)                            # the crossover
spread    = macd - signal                           # detrend around the crossover
macd_dt   = SMA(spread, 3)                           # 3-term MA used as the new crossover
```

### C.5 Fibonacci oscillator Buy/Sell lines (Regime 1)

*"multiplying the 1973 oscillator high at .6797 by .618 and subtracting the result
from .6797"* (1991 ch-07.md:27,31).

```
sell_line = osc_high - osc_high * 0.618     # i.e. osc_high * 0.382
buy_line  = osc_low  - osc_low  * 0.618     # mirror, from the prior oscillator low
```

### C.6 Standard library (1991 Appendix, ap-01.md)

All textbook; reproduce verbatim and credit the original authors:

- **CCI** (ap-01.md:5-15): `CCI = (typical − SMA(typical,N)) / (0.015 · meanDev)`,
  `typical = (H+L+C)/3`; Sell +100, Buy −100.
- **MACD** (ap-01.md:23-29): `EMA(C,12) − EMA(C,26)`, crossover `EMA(MACD,9)`.
- **Moving Average** (ap-01.md:37-45): simple mean of last X.
- **EMA** (ap-01.md:52-58): `EMA = (N − Y)·K + Y`, `K = 2/(X+1)`.
- **RSI** (ap-01.md:65-76): Wilder `100 − 100/(1+RS)` with `(X−1)/X` recursive smoothing.
- **Stochastic** (ap-01.md:89-105): fast `%K = 100·(C−L10)/(H10−L10)`, fast `%D`, slow
  `%D = (%D + %D₋₁ + %D₋₂)/3`. *(NB: the appendix `%D` typesetting is the standard
  fast-%D sum form; verify against the formula before coding.)*

### C.7 Buy/Sell lines are PARAMETERS, not constants

The threshold pairs differ by **market and time frame** across sources — they must be
exposed as parameters, never hardcoded:

| Source | Oscillator | Buy line | Sell line |
|--------|-----------|----------|-----------|
| 1991 ch-10.md:15 | smoothed RSI3 | 30 | **75** |
| 1991 ch-11.md:376 | smoothed CCI(5)/MA(8) | −35 | 60 |
| 1992:48-52 | combo oscillator | **40** | 60 |
| 1992:60-64 | CCI 30 (Detrend) | −70 / −100 | — |
| 1992:75-78 | DJIA combo | **55** | — |
| 1997:110 / 1998:43 | RSI3M3 | 30 | (mirror ~70) |
| 2000:30 | 10DS DoubleStoc | 40 | (mirror) |

### C.8 Timing Bands (Regime 1 — method described, estimator informal)

**PARTIAL but implementable-with-decisions** (previously BLOCKED). The method is
stated and worked:

> *"I took the middle 70% of the time periods … I called that a timing band."*
> — 1998 TASC content.md:70

> Worked example (1992:356-360): collect historical low-to-low intervals
> `13,15,16,17,18,18,21,21,22,22,24,26,28,29,30,33`; median ≈ 21-22; *"Seventy-five
> percent of the lows occurred 15 to 26 weeks from the previous low."*

Construction: from a confirmed cycle bottom, build three interval distributions —
trough-to-crest (T-C), trough-to-trough (T-T), crest-to-trough (C-T) — and keep the
**central ~70%** of each as the forecast window. 70/20/10 split: ~70% of turns fall in
the band, ~20% before, ~10% after (1992:314-319; 2000:56). Default cycle length 20,
range 14-27+ (2003:818).

**Open decisions (record, don't guess):** the exact trimming rule — 15th-85th
percentile vs interquartile-style vs "drop outer 30%" — is **not formally stated**;
the 2003 software's band-width arithmetic is vendor-internal. Implement the percentile
estimator with the rule as an explicit parameter.

---

## Part D — Verification method (same machinery as STC)

For every implementable indicator, validation = **conform to a declared source +
invariant checks + provenance**:

1. **Declare the source** per indicator with `file:line` (RSI3M3 → 1997:98 / TASC:164;
   3-10 → 1991 ch-13:7; detrends → 1997:72 / TASC:204; standard lib → 1991 ap-01).
2. **Freeze parameters** — no indicator is meaningful without stated lengths/lines.
3. **Golden vectors** — run the construction on the shared fixture; commit per-param
   golden arrays.
4. **Differential test** ports against golden vectors to tolerance.
5. **Invariants:** bounded range (oscillators ∈ [0,100] or stated band), finite after
   warm-up, **causal** (centered detrend deliberately fails this → batch-only),
   deterministic, flat-input safe.
6. **Cross-implementation triangulation** for DoubleStoc (≥2 independent MQL/Pine
   ports), exactly as done for STC.
7. **Conformance doc, not authorship:** Regime-1 items may claim *author-defined*
   fidelity with book citations; DoubleStoc claims only *"concordant with {reference}
   @ {params}."*

---

## Part E — Recommended sequencing

1. **RSI3M3 (+ 5-bar detrend)** — smallest, author-defined, reuses RSI + SMA.
2. **3-10 Oscillator (+ 16-term crossover)** — author-defined, trivial MA difference.
3. **Detrend pair** (real-time + centered) — centered flagged batch-only.
4. **MACD-detrend, Fibonacci osc lines, Keltner(σ) variant** — author-defined recipes.
5. **Standard library** (CCI/MACD/EMA/MA/RSI/Stochastic) — from the 1991 appendix.
6. **Timing Bands** — percentile-band estimator with the trimming rule as a parameter.
7. **DoubleStoc** — Regime-2 conform-to-port (reuses STC triangulation machinery);
   document the "twist or two" caveat.
8. **THEN, only if needed:** acquire *The Blue Book* to unblock the Overbought/Oversold
   and Momentum indices (#18, #19); seek a source for BLine/HAL/DTI/trailing-stops/PTI.

### What we deliberately will NOT do
- Claim DoubleStoc is "Bressert's" rather than platform-canonical (Blau holds the
  documented priority for the *named* DSS), or claim byte-fidelity to his shipped
  software (the "twist or two" is undisclosed).
- Conflate "DSS Bressert" (stochastic-of-a-stochastic) with Blau's DSS (component
  double-EMA) — they are different indicators.
- Stream the **centered** detrend as if causal (it uses future bars).
- Guess the BLine / HAL / DTI / trailing-stop / PTI / Momentum / O-B-O-S arithmetic —
  those are book-/software-gated and stay BLOCKED until a primary is in hand.
- Hardcode buy/sell lines — they vary by market/time frame (Part C.7).

---

## Reference Sources

| Role | Source | Locus |
|------|--------|-------|
| **3-10 oscillator** (full arithmetic) | 1991 *Power of Oscillator/Cycle Combinations* | `1991-*/ch-13.md:7,11` |
| **MACD detrend** (recipe) | 1991 book | `1991-*/ch-08.md:98-102` |
| **Fibonacci osc lines** | 1991 book | `1991-*/ch-07.md:27,31` |
| **Standard-indicator formulas** | 1991 book appendix | `1991-*/ap-01.md:5-105` |
| **Centered detrend, RSI3M3, RSI3M3-detrend, Keltner(σ)** | 1997 *Cycle Trading Pattern Manual* | `1997-*/content.md:72-78,98,131,297` |
| **RSI3M3 + 3M3 detrend + timing-band numbers** | 1998 *Trading With Time Fractals* | `1998-*/content.md:41,59,67` |
| **Author primary** (detrends, RSI3M3, timing-band concept) | Bressert & Hartle, "Trading and Control," *TASC* Mar 1998 | `tasc/1998-03-*/content.md:70,164,176,204-212` |
| **DoubleStoc "twist or two" admission** | 2003 *ProfitTrader for MetaStock Manual* | `2003-*/content.md:160` |
| **BLine / HAL / DTI / trailing stops** (named, no math) | 2002 *Overview of ProfitTrader 6.0 Indicators* | `2002-*/content.md` |
| DSS Bressert candidate reference | ProRealCode "DSS Bressert" | https://www.prorealcode.com/prorealtime-indicators/dss-bressert-double-smoothed-stochastic/ |
| DSS Bressert port (lexicon-sourced) | MQL5 code/8310 (MetaQuotes, 2008) | https://www.mql5.com/en/code/8310 |
| DSS Bressert port | MQL5 code/789 (Rosh/Kositsin) | https://www.mql5.com/en/code/789 |
| DSS **Blau** (do NOT conflate) | MQL5 code/23278 (Rakic) | https://www.mql5.com/en/code/23278 |
| DSS Bressert "ratio" strand | MQL5 code/23277 (Rakic) | https://www.mql5.com/en/code/23277 |
| Blau priority for *named* DSS | Blau, "Double Smoothed-Stochastics," *TASC* V9N1 Jan 1991 | https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf |
| **Book-only** #18 & #19 (NOT digitized) | *The Blue Book* (1981), OpenLibrary | https://openlibrary.org/books/OL15057618M |
| Full investigative brief | this repo | `inputs/walter-bressert/deep-research.md` |
| Full catalog of implementations | this repo | `inputs/walter-bressert/trading-research.md` |
