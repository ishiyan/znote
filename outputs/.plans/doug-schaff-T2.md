# Agent Brief T2 — Doug Schaff: Biography, Firm, Publication, Adoption, Legacy, Status

**Output file:** `outputs/.drafts/doug-schaff-research-biography.md`
**Role:** Research Doug Schaff the person and the reach of his work. Write findings to disk; return a short summary only.

## Subject
Doug Schaff — forex trader/strategist, creator of the **Schaff Trend Cycle (STC)**,
associated with **FX Strategy** (fxstrategy.com) and STC-branded sites. Co-authored
two 1999 TASC Euro articles with Walter Bressert.

## Tasks
1. **Biography (verifiable).** Find what is documentable: career in forex, roles
   (e.g., "President/founder of FX Strategy," forex strategist, bank FX dealer
   background if any), timeframe of activity, location. Separate VERIFIED from
   folklore. Birth year/education may be unfindable — flag **[UNCONFIRMED]**.
   Sources to try: archived fxstrategy.com (Wayback), schafftrendcycle.com /
   any STC site, LinkedIn, TASC author archive, interviews/podcasts, forum bios.
2. **Firm/entity.** FX Strategy (or similar) — nature, period, status (active /
   defunct / domain lapsed). Use Wayback to date it. Note any STC LLC / trademark.
3. **Publication record.** Find Schaff's TASC article(s):
   - Fetch the TASC author archive: `https://technical.traders.com/archive/atauth.asp`
     style search, or search the archive for "Schaff". Build the articles table
     (date, title, co-authors, category, PDF URL). Confirm the two 1999 Euro
     articles (`\V17\C05\033EURO`, `\V17\C06\043EURO`) and find the article that
     introduced STC if one exists in TASC. Check Traders' Tips for STC code.
   - Note: STC may have been popularized outside TASC (forex press / Active Trader).
     Record wherever the *first* STC publication appears, with date.
4. **Cross-platform adoption (the objective influence proxy).** Inventory STC
   ports with URLs (all should return HTTP 200): MQL5 CodeBase (search "Schaff
   Trend Cycle"/"STC" — list the codes), TradingView (built-in? Pine scripts),
   NinjaTrader, ProRealTime/ProRealCode, MetaStock, TradeStation, Python
   (pandas-ta / others). This breadth is the legacy evidence.
5. **Forums & media.** Search the mandatory trading forums (ForexFactory,
   futures.io, Elite Trader, NinjaTrader Forum, TradingView, MQL5 Forum,
   Wealth-Lab, Trade2Win, r/algotrading) for STC/Schaff threads — list the
   strongest. Find any actual photo/video/interview URLs (YouTube, company site,
   podcast). Mark unfound items `[URL not found]`.
6. **Current status.** Is Schaff still active? Is FX Strategy live? Do NOT assert
   death unless a real obituary/record is found. State the verdict explicitly.

## Method
- Wayback Machine + Mojeek + direct fetches (DuckDuckGo/Brave/Google may be
  blocked — note it). Verify every URL; record HTTP status. Mark blocked tools.
- Tag every claim **[VERIFIED]** / **[UNCONFIRMED]**. Negative results are valid
  findings — record them.

## Output format
Markdown to the output file: `## Biography (timeline)`, `## Firm/Entity`,
`## Publication record` (articles table + Traders' Tips), `## Cross-platform
adoption` (table of URLs+status), `## Forums & media`, `## Current status`
(explicit verdict), `## Confidence & gaps`, `## Sources`. Include candidate
BibTeX fields for any books/articles found.
