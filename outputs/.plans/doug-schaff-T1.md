# Agent Brief T1 — Doug Schaff: STC Mechanics & Lineage

**Output file:** `outputs/.drafts/doug-schaff-research-mechanics.md`
**Role:** Research the Schaff Trend Cycle (STC) construction and its lineage. Write findings to the output file. Do NOT return large results inline — write to disk and return a short summary.

## Subject
Doug Schaff created the **Schaff Trend Cycle (STC)**, a momentum/trend oscillator
that runs **MACD through a cyclic stochastic double-smoothing** (Lane-style
stochastic applied to MACD, then smoothed, often a second stochastic pass). He
co-authored two 1999 TASC articles on the Euro with **Walter Bressert**. STC was
developed in the late 1990s (forex context) and popularized via TASC and platforms.

## Tasks
1. **Exact STC formula & default parameters.** Recover the precise calculation
   chain from the most authoritative sources available:
   - The TASC article that introduced STC (find issue/date; construct PDF URL).
   - Platform implementations as formula corroboration: MQL5 CodeBase (search
     "Schaff Trend Cycle"/"STC"), TradingView Pine ("Schaff Trend Cycle"),
     ProRealCode, NinjaTrader. Quote the calculation steps.
   - Default params commonly cited: cycle length (e.g., 10), fast MACD (23),
     slow MACD (50), smoothing factor (0.5). Verify against sources; flag any
     number you cannot source as **[UNCONFIRMED]**.
   - Lay out the chain explicitly: MACD(fast,slow) → %K stochastic over `cycle`
     → EMA/smoothing → second stochastic of that → smoothing → 0–100 STC. Note
     where sources agree/disagree on whether it's a single or double stochastic.
2. **What problem STC claims to solve** — faster than MACD, smoother than
   stochastic, fewer whipsaws, earlier turns; cite the claim's origin.
3. **Lineage.** Document, with sources, how STC composes prior work:
   - **Gerald Appel** — MACD (the input).
   - **George Lane** — stochastic %K/%D (the transform).
   - **Walter Bressert** — cycle/timing + the stochastic-of-a-stochastic "DSS
     Bressert" idea (see `outputs/walter-bressert.md` §3 and
     `trading-research/walter-bressert.md`). Assess how directly STC inherits the
     Bressert double-smoothed-stochastic approach (apply stochastic transform to a
     smoothed series, then again).
   - **William Blau** — double-smoothing context (see `outputs/william-blau.md`).
   - Be explicit about what is documented vs. analytic inference.
4. **The 1999 Bressert/Schaff Euro articles** — fetch/skim both:
   - `https://technical.traders.com/archive/article.asp?file=\V17\C05\033EURO.pdf` (May 1999, "The Euro's True Colors")
   - `https://technical.traders.com/archive/article.asp?file=\V17\C06\043EURO.pdf` (Jun 1999, "The Euro's Weekly Cycles")
   Summarize what they actually contain (cycle/timing-band method applied to the
   Euro) and whether STC itself appears in them.

## Method
- Use web search + direct fetches. Reuse the existing Bressert/Blau briefs in
  `outputs/` as lineage evidence. Verify URLs return content; mark blocked ones.
- Tag every claim **[VERIFIED]** (dated/citable source retrieved) or
  **[UNCONFIRMED]**. Never invent a formula or parameter — flag gaps.
- Provide a code-style pseudocode block for the STC calculation, clearly marking
  which steps are sourced vs. inferred.

## Output format
Markdown to the output file: a `## STC Mechanics` section (formula, params,
pseudocode, problem-solved), a `## Lineage` section, a `## The 1999 Euro Articles`
section, a `## Confidence & gaps` section, and a `## Sources` list with URLs.
Include candidate BibTeX/MQL5 URLs you find (the lead will consolidate).
