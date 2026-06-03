# Deep Research Plan: Doug Schaff

**Slug:** `doug-schaff`
**Date:** 2026-06-03

**Context:** Doug Schaff is the creator of the **Schaff Trend Cycle (STC)** — a
widely-ported indicator that runs MACD through a Bressert/Lane-style cyclic
stochastic double-smoothing. He co-authored two 1999 TASC articles on the Euro
with **Walter Bressert** (just researched — `outputs/walter-bressert.md`). No
prior catalog or brief exists for Schaff in this repo. This is a TASC-contributor
/ trading-indicator subject, so the trading-domain deliverable rules apply
(articles table with PDFs/Tips, MQL5 implementations, forums, photos/interviews,
full BibTeX).

## Key Questions

1. **Biography & career** — Who is Doug Schaff? Verifiable life/career facts: FX
   trading background, founder/role at **FX Strategy / Schaff Trend Cycle LLC**,
   relationship to the forex industry, current status. Separate verified from
   folklore. (Birth year/education likely hard to find — flag.)

2. **The Schaff Trend Cycle, mechanically** — Exact construction: MACD → stochastic
   transform → smoothing → second stochastic/cycle pass. Default parameters
   (cycle length, fast/slow MACD, smoothing). What problem it claims to solve
   (faster, smoother MACD with fewer whipsaws). Where the precise formula is
   documented vs. inferred from platform code.

3. **Lineage & the Bressert collaboration** — How STC relates to its antecedents:
   Appel's MACD, Lane's stochastic, Bressert's cycle/timing work, Blau's double
   smoothing. What the 1999 Bressert co-authored TASC Euro articles actually
   contain, and how the collaboration fed into STC. Resolve attribution honestly.

4. **Publication, adoption & legacy** — TASC article(s) introducing STC (date,
   issue); cross-platform porting (MT4/MT5/MQL5, TradingView, NinjaTrader,
   ProRealTime, etc.) as the objective influence proxy; persistence in retail
   communities.

5. **Critical assessment** — Does STC hold up? Is it materially better than MACD,
   or a repackaging? Any independent/academic testing of STC specifically (likely
   none) vs. by-category evidence on oscillator/cycle timing and data-snooping.
   Marketing-vs-substance caveats.

## Evidence Needed
- Primary: TASC article(s) by Schaff introducing STC; the 1999 Bressert/Schaff
  Euro articles (`\V17\C05`, `\V17\C06`); FX Strategy / schafftrendcycle.com
  archived pages; any Schaff interview/bio.
- Secondary: platform STC implementations (MQL5 CodeBase, TradingView Pine,
  ProRealCode) for the formula; Etzkorn/oscillator literature.
- Tertiary: forum discussions (ForexFactory, futures.io, etc.); academic
  literature on MACD/stochastic/cycle timing & data-snooping (reuse Bressert set).
- Reuse: `outputs/walter-bressert.md` + `trading-research/walter-bressert.md`,
  `outputs/william-blau.md` (double-smoothing/DSS lineage), TASC article index.

## Scale Decision
**Parallel — 3 Task agents.** Lead synthesizes. (Tighter than Bressert's 4: the
DSS-style provenance question and the critical question are lighter here.)

- **T1 — STC mechanics + lineage**: exact formula/parameters from primary +
  platform code; relation to MACD/Lane/Bressert/Blau; the 1999 Euro articles.
- **T2 — Biography, firm, publication, adoption, legacy, status**: verifiable life
  facts; FX Strategy; TASC publication; cross-platform adoption; forums; media.
- **T3 — Critical/academic assessment**: STC vs MACD substance; by-category
  academic evidence; data-snooping/marketing caveats.

## Task Ledger
| Agent | Brief | Output |
|-------|-------|--------|
| T1 | outputs/.plans/doug-schaff-T1.md | outputs/.drafts/doug-schaff-research-mechanics.md |
| T2 | outputs/.plans/doug-schaff-T2.md | outputs/.drafts/doug-schaff-research-biography.md |
| T3 | outputs/.plans/doug-schaff-T3.md | outputs/.drafts/doug-schaff-research-critical.md |

## Verification Log
(empty — filled during run)

## Deliverables
- `outputs/doug-schaff.md` — cited investigative brief (with `## Articles`,
  `## MQL5 Implementations`, and `## BibTeX` per trading-domain requirement)
- `outputs/doug-schaff.provenance.md`
