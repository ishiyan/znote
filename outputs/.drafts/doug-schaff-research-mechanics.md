# Doug Schaff — STC Mechanics & Lineage (Research Draft)

> Research compiled 2026-06-03. Every claim is tagged **[VERIFIED]** (a dated,
> retrievable source was obtained) or **[UNCONFIRMED]** (plausible but not
> corroborated by a located primary source). No formula or parameter is invented;
> gaps are flagged explicitly. URLs were retrieved and HTTP status recorded
> (see `## Sources`).

---

## Executive Summary

The **Schaff Trend Cycle (STC)** was created by currency trader **Doug Schaff**
and, per the most cited secondary source (Investopedia / Brian Twomey),
**developed in 1999** [S1]. Mechanically it is an **MACD line run through two
cascaded Lane-style stochastic transforms, each followed by an exponential
("Fast %D") smoothing**, producing a 0–100 oscillator. The exact algorithm is
recoverable from concordant open-source implementations (ProRealCode → pandas-ta);
they agree on the calculation chain and on the smoothing recursion to the byte
[S2][S3][S4]. The one point of genuine divergence among sources is **the MACD
EMA periods**: the forex-native defaults are **fast 23 / slow 50** (ProRealCode
"schaff-trend-cycle2"), while the generic/library defaults are **fast 12 / slow 26**
(standard MACD, pandas-ta). The cycle length (**10**) and smoothing factor (**0.5**)
are consistent across all located implementations [S2][S3][S4].

STC's lineage is a clean four-author composite: **Appel's MACD** (the input),
**Lane's stochastic %K/%D** (the normalizing transform), **Bressert's
cycle/"stochastic-of-a-stochastic" thinking** (the double-stochastic
architecture and the forex-cycle framing — Schaff and Bressert co-authored two
1999 TASC Euro articles), and the broader **Blau double-smoothing** context.
Crucially: STC's repeated *stochastic-of-a-stochastic* construction matches the
"**DSS Bressert**" pattern, **not** Blau's component-double-EMA DSS — so the
direct mechanical ancestor is the Bressert-attributed DSS, with Blau as a
conceptual cousin [S5][S6].

I could **not** retrieve any original Schaff publication or a TASC article that
*introduces* STC — no such article appears in the TASC V17 (1999) index, and the
two Bressert/Schaff Euro articles are cycle/timing-band pieces that **do not
mention STC** [S7]. The formula is therefore documented from convergent platform
implementations, not from a primary Schaff text.

---

## STC Mechanics

### What it is (one sentence)

STC = `SecondSmooth( Stochastic( FirstSmooth( Stochastic( MACD ) ) ) )`, scaled
0–100. [VERIFIED — convergent implementations S2][S3][S4]

### Default parameters

| Parameter | Symbol | Forex-native default | Generic/library default | Source |
|-----------|--------|----------------------|--------------------------|--------|
| Cycle / TC length | `TCLen` / `tclength` | **10** | **10** | [S2][S3][S4] **[VERIFIED]** |
| Fast MACD EMA | `MA1` / `fast` | **23** | **12** | [S2] (23/50) · [S4] (12/26) **[VERIFIED, source-dependent]** |
| Slow MACD EMA | `MA2` / `slow` | **50** | **26** | [S2] (23/50) · [S4] (12/26) **[VERIFIED, source-dependent]** |
| Smoothing factor | `Factor` | **0.5** | **0.5** | [S2][S3][S4] **[VERIFIED]** |

Notes:
- **23/50** is the value pair that propagates through forex-oriented STC code and
  is presented as the canonical Schaff currency setting [S2]. **[VERIFIED]** as
  the ProRealCode default; **[UNCONFIRMED]** that Schaff *himself* published these
  exact numbers (no primary Schaff source located).
- **12/26** is simply the standard MACD pair adopted as a convenience default by
  the pandas-ta port [S4].
- Overbought/oversold thresholds: most commonly **75 / 25** (ProRealCode plots
  the 25/75 levels; Investopedia describes buy "turns up from 25" / sell "turns
  down from 75") [S2][S1]; MotiveWave documents **75 / 25** explicitly [S8].
  Some platforms use 80/20 [S3]. **[VERIFIED — values vary by platform]**

### The calculation chain (sourced)

The following quotes the ProRealCode "schaff-trend-cycle2" implementation
verbatim [S2], which is the exact code pandas-ta re-implements [S4]:

```
//input parameters
TCLen = 10
MA1 = 23
MA2 = 50
Factor = 0.5

//{Calculate a MACD Line}
XMAC = ExponentialAverage[MA1](Close) - ExponentialAverage[MA2](Close)

//{1st Stochastic: Calculate Stochastic of a MACD}
Value1 = Lowest[TCLen](XMAC)
Value2 = Highest[TCLen](XMAC) - Value1
//{%Fast K of MACD}
if Value2 > 0 then
   Frac1 = ((XMAC - Value1)/Value2) * 100
else
   Frac1 = Frac1[1]
endif
//{Smoothed Calculation for % Fast D of MACD}
PF = PF[1] + (Factor * (Frac1 - PF[1]))

//{2nd Stochastic: Stochastic of smoothed Percent Fast D, 'PF', above}
Value3 = Lowest[TCLen](PF)
Value4 = Highest[TCLen](PF) - Value3
//{% of Fast K of PF}
if Value4 > 0 then
   Frac2 = ((PF - Value3)/Value4) * 100
else
   Frac2 = Frac2[1]
endif
//{Smoothed Calculation for %Fast D of PF}
PFF = PFF[1] + (Factor * (Frac2 - PFF[1]))

RETURN PFF   // = STC, with 25 / 75 levels
```

Two details worth flagging from the code itself [S2][S4]:
1. **The smoothing is an EMA with α = Factor (0.5).** `PF = PF[1] + Factor*(Frac1 − PF[1])`
   is algebraically `EMA` with smoothing constant 0.5, i.e. an EMA of effective
   period ≈ 3 (since α = 2/(N+1) ⇒ N = 3). Sources label it "% Fast D" (Lane's
   %D), so STC's "%D" is an EMA-of-%K, not Lane's original SMA-of-%K. **[VERIFIED]**
2. **Carry-forward on a flat window:** when the high=low over the cycle
   (`Value2`/`Value4` ≤ 0), the code holds the previous %K (`Frac1 = Frac1[1]`),
   avoiding division by zero. pandas-ta holds the previous *smoothed* value
   instead; this is a minor edge-case divergence, not a structural one [S4]. **[VERIFIED]**

### Pseudocode (sourced vs inferred steps tagged)

```
# ---- STC(close, TCLen=10, fast=23, slow=50, factor=0.5) ----
# [SOURCED S2,S4] Step 0: MACD line (difference of two EMAs of close)
MACD = EMA(close, fast) - EMA(close, slow)

# [SOURCED S2,S4] Step 1: first stochastic %K of the MACD over TCLen bars
ll1 = Lowest(MACD, TCLen)
hh1 = Highest(MACD, TCLen)
if (hh1 - ll1) > 0:  K1 = 100 * (MACD - ll1) / (hh1 - ll1)
else:                K1 = previous K1          # flat-window carry-forward

# [SOURCED S2,S4] Step 2: EMA smoothing of K1  (Lane "%Fast D", alpha = factor)
PF = PF_prev + factor * (K1 - PF_prev)

# [SOURCED S2,S4] Step 3: second stochastic %K of PF over TCLen bars
ll2 = Lowest(PF, TCLen)
hh2 = Highest(PF, TCLen)
if (hh2 - ll2) > 0:  K2 = 100 * (PF - ll2) / (hh2 - ll2)
else:                K2 = previous K2

# [SOURCED S2,S4] Step 4: EMA smoothing of K2  -> STC, range 0..100
STC = PFF_prev + factor * (K2 - PFF_prev)

# [INFERRED] Signal logic: long when STC turns up through 25; short when it
#            turns down through 75 (thresholds are platform conventions, S1/S2/S8;
#            the exact "turn from level" trigger is Investopedia's description, S1)
```

Marking summary: **Steps 0–4 are SOURCED** (verbatim-concordant across [S2] and
[S4], with [S3] and [S8] corroborating the architecture). **Signal thresholds
and the "turn-from-25/75" entry rule are conventions** documented in secondary
sources [S1][S2][S8] rather than in any primary Schaff text — treat the trigger
rule as **[VERIFIED as common usage / UNCONFIRMED as Schaff's own spec]**.

### Single vs double stochastic — where sources agree/disagree

- **Double stochastic is the canonical STC.** ProRealCode "schaff-trend-cycle2"
  [S2], pandas-ta [S4], and the pandas-ta docstring ("two cascaded stochastic
  calculations with additional smoothing") all implement **two** stochastic
  passes [S2][S4]. **[VERIFIED]**
- **A simplified single-stochastic variant exists.** The older ProRealCode
  "Schaff Trend Cycle" by *lolo* (2015) runs **one** stochastic of the MACD then
  a single Wilder-average smoothing, and—unusually—builds the MACD from
  `WilderAverage` rather than EMA, with periods 10/21 [S3]. This is a
  **community simplification**, not the reference STC; it differs both in the
  number of stochastic passes and in the MA type. **[VERIFIED as a variant]**
- MotiveWave's prose ("MACD calculated first, then a Stochastic Oscillator
  formula is applied," 0–100, 25/75) is consistent with the canonical chain but
  does not expose enough code to confirm one vs two passes [S8]. **[VERIFIED — partial]**

### What problem STC claims to solve

The origin claim (Investopedia, attributing Schaff/FX-Strategy) is that STC is
**faster and more accurate than MACD**: it "will react faster to changing market
conditions" and "typically identifies up and downtrends long before MACD,"
because it adds a **cycle/time component** (the stochastic-over-`TCLen`
normalization) on top of MACD's EMAs [S1]. The double smoothing is meant to make
it **smoother than a raw stochastic** (fewer whipsaws) while the stochastic
normalization makes it **turn earlier than MACD's slow signal line** [S1][S2].
The acknowledged drawback, stated in the same source: STC **"can stay in
overbought or oversold territory for long stretches"** (it pins to 0 or 100) [S1].
**[VERIFIED — claim and its origin]**; the performance superiority itself is a
vendor/author claim, **[UNCONFIRMED]** by any independent test located.

---

## Lineage

STC is a composition of four prior bodies of work. Documented links vs analytic
inference are tagged.

### 1. Gerald Appel — MACD (the input) — **[VERIFIED, documented]**

STC's first operation is literally a MACD line (`EMA(fast) − EMA(slow)`)
[S2][S4]. Every source frames STC as "an improved/evolved MACD" [S1][S2][S8].
MACD is Appel's (late 1970s). The inheritance is direct and explicit. The forex
periods (23/50) differ from Appel's classic 12/26, but the construct is MACD.

### 2. George Lane — stochastic %K/%D (the transform) — **[VERIFIED, documented]**

Each STC stage applies Lane's stochastic formula —
`%K = 100·(x − Lowest)/(Highest − Lowest)` — to a series, then a "%D" smoothing
[S2][S4]. Lane introduced the stochastic oscillator (popularized via S&C, 1984;
the same V17/1999 volume that carries the Schaff Euro articles also runs a
Stuart Evens "Stochastics" tutorial crediting Lane) [S7]. STC's twist is applying
%K to the **MACD line** and to a **smoothed stochastic**, not to raw price.

### 3. Walter Bressert — cycle timing + stochastic-of-a-stochastic — **[VERIFIED collaboration; STRONG mechanical inference on DSS]**

This is the closest and most load-bearing ancestor:

- **Documented collaboration.** Schaff co-authored **two 1999 TASC articles with
  Bressert** ("The Euro's True Colors," May 1999; "The Euro's Weekly Cycles,"
  June 1999) [S7]. So Schaff was working *alongside* Bressert, in the forex-cycle
  domain, the same year STC is dated to. **[VERIFIED]**
- **The cycle premise.** STC's defining idea — that "currency trends accelerate
  and decelerate in cyclical patterns" regardless of timeframe, captured by the
  `TCLen` cycle window — is Bressert's cycle-trading worldview applied inside an
  oscillator [S1]. **[VERIFIED as concept; the specific borrowing is inference]**
- **The architecture.** STC's **stochastic-of-a-stochastic** (run a stochastic,
  smooth it, run the stochastic transform *again*, smooth again) is structurally
  the **"DSS Bressert"** pattern documented in the Bressert brief —
  `sto2 = stochastic(EMA(stochastic(x))); DSS = EMA(sto2)` — **not** Blau's
  component-double-EMA DSS [S5][S6]. STC differs only in that its *input* is the
  MACD line rather than price, and it adds one more smoothing. The match to the
  Bressert-attributed DSS is strong and direct. **[VERIFIED that the patterns
  match; "Schaff consciously copied Bressert's DSS" is INFERRED]**

### 4. William Blau — double-smoothing context — **[VERIFIED as conceptual cousin; NOT the direct ancestor]**

Blau's contribution to the family is the **double-smoothing-before-normalization**
philosophy (TASC, 1991) [S6]. STC shares the *spirit* (cascade smoothing to cut
lag without adding whipsaw) but uses a **different mechanism**: STC re-applies the
whole stochastic transform twice (Bressert-style), whereas Blau double-smooths the
numerator and denominator of a *single* stochastic and divides once. The
`william-blau.md` brief already records the relationship: "Schaff applied double
stochastic normalization to MACD — combining Blau's double-smoothing philosophy
with Appel's MACD" [S6]. So Blau is a **cousin/parallel**, not the line STC's code
descends from. **[VERIFIED distinction]**

### Lineage summary table

| Author | Contribution to STC | Inheritance type | Confidence |
|--------|---------------------|------------------|-----------|
| Appel | MACD line = STC's input | Direct, in code | **[VERIFIED]** |
| Lane | Stochastic %K/%D transform (twice) | Direct, in code | **[VERIFIED]** |
| Bressert | Cycle framing + stochastic-of-a-stochastic (DSS) architecture; 1999 forex collaboration | Documented collaboration; strong mechanical match | **[VERIFIED collab; INFERRED copy]** |
| Blau | Double-smoothing-before-normalize philosophy | Conceptual parallel, different mechanism | **[VERIFIED as cousin]** |

---

## The 1999 Euro Articles

Both articles are **paywalled** on traders.com: the PDF URLs return **HTTP 302**
redirecting to `archivelogin.asp` (subscriber login), so full text was **not
retrieved**. Content below is from the **publicly accessible TASC Vol. 17
abstracts page** [S7] (HTTP 200), cross-checked against the Bressert brief.

| Field | Article 1 | Article 2 |
|-------|-----------|-----------|
| Title | **The Euro's True Colors** | **The Euro's Weekly Cycles** |
| Authors | Walter Bressert & Doug Schaff | Walter Bressert & Doug Schaff |
| Issue | TASC **May 1999** (V17:5) | TASC **June 1999** (V17:6) |
| PDF URL | `…/article.asp?file=\V17\C05\033EURO.pdf` | `…/article.asp?file=\V17\C06\043EURO.pdf` |
| HTTP status | **302 → login (paywalled/blocked)** | **302 → login (paywalled/blocked)** |

**What they contain** (from abstracts [S7]):
- *The Euro's True Colors* (May 1999): frames the analytic problem of a currency
  **with no price history** — the Euro launched 4 Jan 1999 — and how millions of
  participants had instant exposure to an instrument lacking a chart record. It is
  an introduction to analyzing the newborn Euro. **[VERIFIED via abstract]**
- *The Euro's Weekly Cycles* (June 1999): an explicit **follow-up** ("As a
  follow-up to last month's introduction…"), discussing the Euro's start of
  trading on 4 Jan 1999 and "what may happen to the Euro," i.e. a **cycle/timing
  forecast** piece on the weekly timeframe. **[VERIFIED via abstract]**

**Does STC appear in them?** **No located evidence that it does.** The abstracts
describe **cycle and market-timing** analysis of the Euro (Bressert's home turf),
not an oscillator construction; neither abstract names STC, MACD-stochastic, or a
"trend cycle" indicator [S7]. STC is dated to 1999 by Investopedia [S1] but is
**not** documented as having been *introduced* in these articles. Confirming or
denying an STC mention inside the full PDFs requires subscriber access.
**[UNCONFIRMED — full text blocked]**

---

## Confidence & gaps

| # | Claim | Status |
|---|-------|--------|
| 1 | STC = MACD → stochastic → smooth → stochastic → smooth, 0–100 | **[VERIFIED]** ([S2][S4], corroborated [S3][S8]) |
| 2 | Cycle length 10, smoothing factor 0.5 | **[VERIFIED]** ([S2][S3][S4]) |
| 3 | Fast/slow MACD EMA = 23/50 (forex) | **[VERIFIED as ProRealCode default S2]; [UNCONFIRMED as Schaff's own published numbers]** |
| 4 | Fast/slow = 12/26 (generic) | **[VERIFIED — pandas-ta default S4]** |
| 5 | Smoothing is an EMA with α=0.5 (≈3-period), labeled "%Fast D" | **[VERIFIED — from code S2/S4]** |
| 6 | Created by Doug Schaff, ~1999, currency trader | **[VERIFIED via Investopedia S1]; primary Schaff source NOT located** |
| 7 | "Faster/earlier than MACD; can pin OB/OS" problem statement | **[VERIFIED as the origin claim S1]; performance NOT independently tested** |
| 8 | Lineage: Appel + Lane in code; Bressert architecture; Blau cousin | **[VERIFIED for Appel/Lane/Blau-distinction]; Bressert-DSS copy is INFERRED from mechanical match** |
| 9 | Two 1999 Bressert/Schaff Euro articles exist (May, Jun) | **[VERIFIED via TASC abstracts S7]** |
| 10 | STC appears inside the Euro articles | **[UNCONFIRMED — PDFs paywalled (HTTP 302→login)]** |
| 11 | A TASC article that *introduces* STC | **[NOT FOUND — no STC entry in V17 index; none located in any volume]** |

### Open gaps (could not close this pass)
1. **No primary Schaff publication** for STC was located — no article, white
   paper, or book defining the formula or the 23/50/10/0.5 defaults in Schaff's
   own words. The fx-strategy.com bio/strategy pages cited by Investopedia are
   Wayback-archived but render behind a JS "verifying" wall [S1a].
2. **Full text of both Euro PDFs** is paywalled; cannot confirm/deny an STC
   mention or whether STC's cycle math grew directly out of that Euro work.
3. **MQL5 STC code** could not be deep-linked this pass (search endpoint 404'd;
   listing pages did not surface a Schaff entry) — corroboration rests on
   ProRealCode + pandas-ta, which is sufficient for the formula but leaves the
   MQL5/NinjaTrader candidate URLs for the lead to harvest.
4. **TradingView built-in `ta.stc`**: exists as a Pine v5 function but its source
   is not published; the v5 reference page loaded without the function body.

---

## Sources

| # | Source | URL | HTTP | Status |
|---|--------|-----|------|--------|
| S1 | Twomey, B. "Schaff Trend: A Faster and More Accurate Indicator," Investopedia (updated 2022-03-15). Origin facts: Doug Schaff, **developed 1999**, currency trader; faster-than-MACD claim; OB/OS-pinning drawback; 25/75 turn signals. | https://www.investopedia.com/articles/forex/10/schaff-trend-cycle-indicator.asp | 402 live / **200 via Wayback** | verified (Wayback 2022-12-07 capture) |
| S1a | FX-Strategy "About Us"/"Strategy" (Investopedia's primary source for Doug Schaff) | https://www.fx-strategy.com/info/about_us.html | Wayback JS-wall | blocked (verification wall) |
| S2 | ProRealCode "Schaff Trend Cycle" (schaff-trend-cycle2) by Francesco Malagrida, 2017-08-03 — **canonical double-stochastic code; defaults TCLen=10, MA1=23, MA2=50, Factor=0.5** | https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle2/ | 200 | verified |
| S3 | ProRealCode "Schaff Trend Cycle" by lolo, 2015-10-12 — **single-stochastic variant** (WilderAverage MACD 10/21, cycle 10) | https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle/ | 200 | verified |
| S4 | pandas-ta-classic `momentum/stc.py` — Python port (defaults tclength=10, fast=12, slow=26, factor=0.5); docstring: "two cascaded stochastic calculations"; cites ProRealCode schaff-trend-cycle2 | https://raw.githubusercontent.com/xgboosted/pandas-ta-classic/main/pandas_ta_classic/momentum/stc.py | 200 | verified |
| S5 | Walter Bressert deep-research brief (this repo) — §3 DSS attribution; "DSS Bressert" = stochastic-of-a-stochastic | `outputs/walter-bressert.md` | local | verified |
| S6 | William Blau deep-research brief (this repo) — Blau vs Bressert DSS distinction; "Schaff applied double stochastic normalization to MACD" | `outputs/william-blau.md` | local | verified |
| S7 | TASC Vol. 17 (1999) abstracts — both Bressert/Schaff Euro articles (May V17:5, Jun V17:6); Lane/Stochastics context; **no STC article in index** | https://traders.com/Documentation/RESource_docs/VolAbs/V17abs.html | 200 | verified |
| S7a | TASC "The Euro's True Colors" PDF (May 1999) | https://technical.traders.com/archive/article.asp?file=\V17\C05\033EURO.pdf | **302 → archivelogin.asp** | paywalled/blocked |
| S7b | TASC "The Euro's Weekly Cycles" PDF (Jun 1999) | https://technical.traders.com/archive/article.asp?file=\V17\C06\043EURO.pdf | **302 → archivelogin.asp** | paywalled/blocked |
| S8 | MotiveWave studies docs — STC: "MACD calculated first, then Stochastic applied"; 0–100; OB 75 / OS 25 | https://docs.motivewave.com/studies/s-t.md | 200 | verified (partial — prose, no code) |
| S9 | trading-research/walter-bressert.md — Euro article BibTeX + DSS/MQL5 inventory | `trading-research/walter-bressert.md` | local | verified |

### Candidate URLs for the lead to consolidate
- ProRealCode canonical STC (formula): https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle2/
- pandas-ta STC source: https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/momentum/stc.py
- TradingView built-in `ta.stc` (Pine v5 reference): https://www.tradingview.com/pine-script-reference/v5/ (function body not published)
- MotiveWave STC doc: https://docs.motivewave.com/studies/s-t.md
- TASC Euro articles (paywalled): see S7a / S7b above

### Candidate BibTeX

```bibtex
@online{twomey_stc_investopedia,
  author  = {Twomey, Brian},
  title   = {Schaff Trend: A Faster and More Accurate Indicator},
  year    = {2022},
  note    = {States STC developed 1999 by currency trader Doug Schaff},
  url     = {https://www.investopedia.com/articles/forex/10/schaff-trend-cycle-indicator.asp},
  urldate = {2026-06-03},
}

@online{malagrida_stc_prorealcode,
  author  = {Malagrida, Francesco},
  title   = {Schaff Trend Cycle (open-source double-stochastic implementation)},
  year    = {2017},
  howpublished = {ProRealCode},
  note    = {Defaults TCLen=10, MA1=23, MA2=50, Factor=0.5},
  url     = {https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle2/},
  urldate = {2026-06-03},
}

@misc{pandasta_stc,
  author = {{pandas-ta-classic contributors} and rengel8},
  title  = {Schaff Trend Cycle (STC) -- momentum/stc.py},
  year   = {2020},
  howpublished = {GitHub: xgboosted/pandas-ta-classic},
  url    = {https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/momentum/stc.py},
}

@article{bressert1999eurotruecolors,
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

@article{bressert1999euroweekly,
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
```
