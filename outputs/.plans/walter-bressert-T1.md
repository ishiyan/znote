# T1 Brief: Bressert Methodology & Lineage

Write findings to `outputs/.drafts/walter-bressert-research-methodology.md`.

## Goal
Document, mechanically and precisely, Walter Bressert's cycle-trading methodology, and trace its intellectual lineage to J.M. Hurst and Edward R. Dewey / Foundation for the Study of Cycles.

## Primary source (read first)
- The full text of his 1998 TASC interview "Trading and Control" is mirrored on Wayback: https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWB3.html — read it carefully and quote the mechanics.
- Also archived bio pages: https://web.archive.org/web/2017if_/http://www.walterbressert.com/aboutWBTitle.html and aboutWB1.html
- Existing local catalog (evidence base, do not just copy): trading-research/walter-bressert.md

## Questions to answer with citations
1. **Centered detrend vs real-time detrend** — exact construction (e.g., N-period MA displaced back N/2 bars, subtracted from price), why it lags, how Bressert used the real-time version at the hard right edge.
2. **Timing bands** — how he built forecast windows from the distribution of historical cycle low-to-low / low-to-high intervals (the "middle 70%" method). What they predict.
3. **RSI3M3** — exact definition (3-period RSI smoothed by 3-bar MA), buy/sell line levels, how it pairs with the detrend, setup-bar/entry-stop mechanics.
4. **The "oscillator/cycle combination" thesis** — the central idea of his 1991 book: confirming cycle timing with oscillator turns. What problem it solves.
5. **Controlled-risk multi-contract money management** — scaling out of 2-3 contracts at trading-cycle vs longer-cycle targets.
6. **Left/right translation** — definition and trend-bias use.

## Lineage
- **J.M. Hurst** — Bressert attended Hurst workshops. What did Hurst's "Profit Magic of Stock Transaction Timing" (1970) contribute (cyclic principle, FLD, displaced MAs, nominal model)? How does Bressert's detrend derive from Hurst's centered MA / envelope work?
- **Edward R. Dewey / Foundation for the Study of Cycles** (founded 1941) — the centered-detrend technique and the *Catalogue of Cycles*. Confirm Bressert was a USER not founder.
- Note distinction from Blau's double-smoothing (covered by another agent — just flag the boundary).

## Deliverable format
Markdown with: a "Methodology" section (one subsection per technique, with mechanics + a source URL each), a "Lineage" section (Hurst, Dewey), and a short "Confidence notes" list separating well-documented mechanics from vaguely-described ones. Provide source URLs inline. Do NOT invent formulas — if the exact formula isn't in a source, say so. Use web fetch/search; search engines may be blocked (try Brave, Startpage, Mojeek, Wayback).