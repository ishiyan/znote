# Plan: William Blau — Deep Research

## Key Questions

1. **Who is William Blau?** — biography, professional background, education, is he still alive?
2. **The double-smoothing innovation** — mathematical details, how it compares to other smoothing techniques (Butterworth, Gaussian, Jurik), what makes it effective
3. **Complete indicator catalog** — all indicators from his book with formulas/pseudocode
4. **Book reception and influence** — who cites him? How did TSI become a standard indicator?
5. **Relationship to other momentum researchers** — Welles Wilder (RSI), George Lane (Stochastics), Gerald Appel (MACD), Tushar Chande
6. **Implementation ecosystem** — how widely implemented across platforms? Pine Script, Python libs, etc.
7. **Any later work or second edition?** — did he publish anything after 1995?

## Evidence Needed

- Amazon/Google Books detailed info on the book
- TASC article content (if accessible)
- Wikipedia articles on TSI, SMI
- Patent searches (did he patent anything?)
- Web archive searches for any personal page
- Technical comparison of double-smoothing vs other filters
- pandas-ta, ta-lib source code for TSI implementation details

## Scale Decision

**Parallel mode — 3 Task agents:**
- T1: Mathematical deep dive — double smoothing formulas, TSI/SMI/DSS computation, comparison with other filters
- T2: Biography hunt + book details + post-1995 activity
- T3: Ecosystem — Wikipedia, platform implementations, who references Blau in later TASC articles, influence chain

## Task Ledger

| Agent | Status | Output |
|-------|--------|--------|
| T1 | pending | outputs/.drafts/william-blau-research-math.md |
| T2 | pending | outputs/.drafts/william-blau-research-biography.md |
| T3 | pending | outputs/.drafts/william-blau-research-ecosystem.md |
