# Walter Bressert — Indicator(s) & Implementation Plan

Walter Bressert is a **multi-indicator author**, and — unlike Doug Schaff — the
implementation surface splits into three very different source-of-truth regimes.
This document is both the indicator list and the plan for deciding **what can be
implemented now, what is blocked, and what (if anything) requires acquiring his
books.**

> **TL;DR.** Two indicators (**RSI3M3**, **DSS Bressert**) are implementable
> immediately with **no book needed** — RSI3M3 from the author's own interview,
> DSS Bressert from deployed platform code (the exact Schaff/STC playbook).
> Several others (the *Blue Book* indices, the 3-10 oscillator's exact arithmetic,
> timing-band estimator, Profit-Taking Index) are defined **nowhere in any located
> public source** and are **book-only** — those are the only reason to buy a book.

---

## Indicator List

| # | Indicator | Category | Source of truth | Primary author text? | Status |
|---|-----------|----------|-----------------|----------------------|--------|
| 1 | **RSI3M3** (3-period RSI smoothed by 3-bar MA) | Oscillator / trigger | **Author primary** (1998 TASC interview) + retail ports | **Yes** — defined in the interview | **READY** |
| 2 | **DSS Bressert** (Double Smoothed Stochastic) | Oscillator | Convergent platform code (ProRealCode, MQL5) | No author text; attribution disputed | **READY (STC-style conformance)** |
| 3 | **Real-time detrend** (`price − N-MA`) | Cycle / detrend | Author primary (interview) | Yes | READY (trivial; weak alone) |
| 4 | **Centered detrend** (`price − N-MA` displaced back N/2) | Cycle / detrend | Author primary (interview) | Yes | **NON-CAUSAL** — offline/batch only |
| 5 | **3-10 Oscillator** | Oscillator | Interview names it; **arithmetic not stated** | Partial | **BLOCKED — needs 1991 book** |
| 6 | **Timing Bands** ("middle 70%") | Cycle / forecast | Concept only; **estimator unstated** | Partial | **BLOCKED — needs 1991 book** |
| 7 | **Overbought/Oversold Index** | Oscillator | **Only *The Blue Book* (1981)** | Book only | **BLOCKED — needs Blue Book** |
| 8 | **Momentum Index** | Oscillator | **Only *The Blue Book* (1981)** | Book only | **BLOCKED — needs Blue Book** |
| 9 | **Profit-Taking Index (PTI)** | Exit / target | Book / course only; name in resellers | Book only | **BLOCKED — needs book/course** |
| — | Setup-bar / entry-stop, Left/Right Translation, multi-contract scaling | **Strategy rules, not indicators** | Author primary (interview) | Yes | Defer — implement as signal logic if a system is built |

---

## Part A — Three Source-of-Truth Regimes (the key difference from Schaff)

With **Schaff** there was **one** indicator and **zero** primary sources, so deployed
platform code was the *only* possible source of truth. **Bressert is a mixed bag**,
and the three regimes need different treatment:

### A.1 Regime 1 — Author-defined (BETTER than Schaff)

The March 1998 *Technical Analysis of Stocks & Commodities* interview ("Trading and
Control," Hartle) is a **primary author source** that *explicitly defines* RSI3M3 and
both detrends. This is strictly stronger footing than STC: we have the author's own
words, not just third-party code. Validation = conform to the author's stated
construction + invariant checks; residual ambiguities (e.g. Wilder vs simple RSI
smoothing) become recorded **decisions**, resolved against deployed ports.

### A.2 Regime 2 — Platform-canonical, attribution-disputed (SAME as Schaff)

"**DSS Bressert**" is the STC situation exactly:

- **No author publication** defines it. The 1998 interview discusses detrend, RSI3M3,
  and timing bands but **never mentions a double smoothed stochastic**.
- The *named* "Double Smoothed Stochastic" has documented priority by **William Blau
  (TASC, Jan 1991)** — and Blau's formula is **mathematically different** (he
  double-smooths the *components* of one stochastic; "Bressert" re-applies the
  *entire stochastic transform twice*). Mladen Rakic ships them as **two separate
  indicators** (MQL5 code/23278 "Blau" vs code/23277 "Bressert ratio").
- The "Bressert" label's earliest dateable trace is a **mid-2000s platform lexicon**
  (tradesignalonline, Wayback Dec 2007) + its **Aug 2008** MQL4 port — a
  retail-platform-era attribution, not proof of origin.

So, identical to STC: **declare a reference, conform byte-for-byte, claim concordance
not authorship.** There are 13+ MQL implementations + ProRealCode + Pine + NinjaTrader
to triangulate against.

### A.3 Regime 3 — Book-only (WORSE than Schaff)

Several Bressert indicators are defined **nowhere in any located public source** — not
the interview, not platform code, not forums:

- **Overbought/Oversold Index** and **Momentum Index** — the two indices in *The Blue
  Book* (1981) subtitle. Exist nowhere else.
- **3-10 Oscillator** — named in the interview, but the arithmetic (MA-difference? of
  price or of the detrend? any normalization?) is **[UNCONFIRMED]**.
- **Timing-band estimator** — the "keep the middle 70%" concept is stated, but the
  exact estimator (15th–85th percentile? of which interval distribution?) is not.
- **Profit-Taking Index (PTI)** — name appears only in reseller/course materials;
  mechanics are public **nowhere**.

For these, **the books/courses are the only path.** This is the one way Bressert is
*harder* than Schaff, where platform code fully recovered the single indicator.

---

## Part B — Should you acquire the books? (direct recommendation)

**Yes — but selectively. Only two books carry indicator content, and you only need
them for the Regime-3 indicators above.**

| Source | Buy? | Unlocks | Notes |
|--------|------|---------|-------|
| ***The Power of Oscillator/Cycle Combinations*** (1991) | **YES — highest value** | 3-10 oscillator arithmetic, timing-band estimator, possibly PTI, fuller RSI3M3 context | The "combinations" thesis book. **If you buy one thing, buy this.** Shipped with a floppy — a surviving disk image would be literal reference code |
| ***The Blue Book*** (1981) | **Only if you want #7 & #8** | Overbought/Oversold Index, Momentum Index (exist *nowhere else*) | Rare, no ISBN, HALCO Dallas — harder to source |
| Course/workbook *"Reducing Risk Using Cycles and Oscillators"* (PDF + MP3) | Optional (if cheap/findable) | May pin down PTI + timing-band mechanics | Sold by 3rd-party resellers; **[CAUTION]** non-authoritative provenance |
| ***12 Cardinal Mistakes…*** (1981/1997/2016) | **SKIP** | nothing | Trading psychology — **no indicator content** |

**You do NOT need any book for RSI3M3 or DSS Bressert.** Those ship now.

---

## Part C — Canonical Specifications (what we can pin down today)

### C.1 RSI3M3 (Regime 1 — author-defined)

Author's words (1998 interview): *"a 3-period RSI, then smoothed by a 3-bar moving
average."* Plotted on the detrend; a dip **below the buy line at 30** plus an upturn
is the trigger.

```
rsi3      = RSI(close, period=3)
rsi3m3[i] = SMA(rsi3, 3)[i]          # 3-bar simple MA of the 3-period RSI
# bands: buy line = 30 (stated); sell line ~70 (inferred "mirror image", UNCONFIRMED)
```

**Open decisions (record, don't guess):**

| Ambiguity | Status | Plan |
|-----------|--------|------|
| RSI smoothing base | Wilder vs simple — **not stated** | Default **Wilder** (standard RSI); expose as param; cross-check vs a deployed RSI3M3 port |
| Final MA type | "moving average" — SMA vs EMA unstated | Default **SMA** (interview says "3-bar moving average"); document |
| Sell line | "mirror image" only | Default **70**; flag as inferred |

### C.2 DSS Bressert (Regime 2 — platform-canonical, STC-style)

```
DSS = EMA( Stochastic( EMA( Stochastic( close ) ) ) )      # stochastic-of-a-stochastic
# i.e.:
sto1 = stochastic(close, len);  xPre = EMA(sto1, ema_len)
sto2 = stochastic(xPre,  len);  DSS  = EMA(sto2, ema_len)
```

Treat **exactly like STC**: declare a reference (candidate: **ProRealCode "DSS
Bressert"**), triangulate against MQL5 code/8310 + code/789, conform byte-for-byte,
characterize warm-up/seed/guard differences. **Do not** conflate with Blau's DSS
(code/23278) — that is a different formula and a separate deliverable if wanted.

### C.3 Detrends (Regime 1 — author-defined)

```
real_time_detrend[i] = price[i] - SMA(price, N)[i]                 # causal, right-edge usable
centered_detrend[i]  = price[i] - SMA(price, N)[i + N/2]           # NON-CAUSAL: uses N/2 future bars
```

**Centered detrend uses future data** (the symmetric MA needs ~N/2 *future* bars). It
is a zero-phase / non-causal filter and **cannot be a streaming indicator** — implement
only as an offline/batch transform, and flag the look-ahead explicitly. `N` = dominant
cycle length (default start = 20).

---

## Part D — Verification method (same machinery as STC)

For every implementable indicator, validation = **conform to a declared source +
invariant checks + provenance**, reusing the STC infrastructure:

1. **Declare the source** per indicator: RSI3M3 → the 1998 interview text;
   DSS Bressert → a named platform reference (pin version/URL); detrends → interview.
2. **Freeze parameters** — no indicator is meaningful without stated lengths.
3. **Golden vectors** — run the reference (or the author's construction) on the
   shared fixture; commit per-param golden arrays (same close-only INPUT we used for
   STC, where applicable).
4. **Differential test** ports against golden vectors to tolerance; investigate every
   mismatch.
5. **Invariants:** bounded range (oscillators ∈ [0,100] or stated band), finite after
   warm-up, **causal** (no look-ahead — *centered detrend deliberately fails this and
   is marked batch-only*), deterministic, flat-input safe.
6. **Cross-implementation triangulation** for DSS Bressert (≥2 independent MQL/Pine
   ports), exactly as done for STC vs MQL5 486/55511.
7. **Conformance doc, not authorship:** "concordant with {reference} @ {params}." Only
   RSI3M3/detrends may additionally claim *author-defined* fidelity (Regime 1).

---

## Part E — Recommended sequencing

Produce deliverables now without waiting on book acquisition:

1. **RSI3M3** — smallest, author-defined, fast win (reuses RSI + SMA primitives).
2. **DSS Bressert** — reuses the *entire* STC verification/triangulation machinery
   (structurally a stochastic-of-a-stochastic, close cousin of the STC cascade).
3. **(optional) Real-time / centered detrend** — trivial; detrend pair, with centered
   flagged batch-only.
4. **THEN decide on books** — acquire *The Power of Oscillator/Cycle Combinations*
   (and optionally *The Blue Book*) to unblock the 3-10 oscillator, timing bands,
   O/B-O/S + Momentum indices, and PTI (Parts A.3 / B).

### What we deliberately will NOT do
- Claim DSS Bressert is "Bressert's" rather than platform-canonical (Blau holds the
  documented priority for the *named* DSS).
- Conflate "DSS Bressert" (stochastic-of-a-stochastic) with Blau's DSS (component
  double-EMA) — they are different indicators.
- Stream the **centered** detrend as if causal (it uses future bars).
- Guess the 3-10 / timing-band / PTI arithmetic from secondary sources — those are
  book-gated and stay BLOCKED until a primary is in hand.

---

## Reference Sources

| Role | Source | URL |
|------|--------|-----|
| **Author primary** (RSI3M3, detrends, strategy) | Bressert & Hartle, "Trading and Control," *TASC* Mar 1998 | https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB3.html |
| Career/methodology overview | "Walter Bressert's Professional Career" (Wayback) | https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB2.html |
| DSS Bressert candidate reference | ProRealCode "DSS Bressert" | https://www.prorealcode.com/prorealtime-indicators/dss-bressert-double-smoothed-stochastic/ |
| DSS Bressert port (lexicon-sourced) | MQL5 code/8310 (MetaQuotes, 2008) | https://www.mql5.com/en/code/8310 |
| DSS Bressert port | MQL5 code/789 (Rosh/Kositsin) | https://www.mql5.com/en/code/789 |
| DSS **Blau** (do NOT conflate) | MQL5 code/23278 (Rakic) | https://www.mql5.com/en/code/23278 |
| DSS Bressert "ratio" strand | MQL5 code/23277 (Rakic) | https://www.mql5.com/en/code/23277 |
| Blau priority for *named* DSS | Blau, "Double Smoothed-Stochastics," *TASC* V9N1 Jan 1991 | https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf |
| **Book-only** #7 & #8 | *The Blue Book* (1981), OpenLibrary | https://openlibrary.org/books/OL15057618M |
| **Book-only** #5, #6, #9 | *The Power of Oscillator/Cycle Combinations* (1991) | https://www.abebooks.com/servlet/SearchResults?an=Walter+Bressert |
| Full investigative brief | this repo | `inputs/walter-bressert/deep-research.md` |
| Full catalog of implementations | this repo | `inputs/walter-bressert/trading-research.md` |
</content>
</invoke>
