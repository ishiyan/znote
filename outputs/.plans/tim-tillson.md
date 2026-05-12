# Research Plan: Tim Tillson

## Key Questions

1. Who is Tim Tillson? (biography, career, education — likely a software developer/quant)
2. What technical indicators did he invent? (T3 moving average, possibly others)
3. What TASC articles did he author? (known: Jan 1998 "Smoothing Techniques for More Accurate Signals")
4. What books did he write or contribute to?
5. What are the reference/community implementations? (MQL5, TA-Lib, TradingView, pandas-ta)
6. What forum discussions exist about his work?
7. Are there photos, videos, interviews available?

## Evidence Needed

- TASC Author Archive page
- TASC TOC XMLs (scan 1996–2002 primarily — T3 was Jan 1998)
- MQL5 CodeBase (T3, Tillson, T3 Moving Average)
- Trading forums (all 10 mandatory)
- Web bios / Wikipedia
- YouTube / interviews
- Relationship to Mulloy's DEMA/TEMA (T3 builds on DEMA concept)

## Scale Decision

**Direct search** — Tim Tillson is likely a focused author (1-3 TASC articles, 1-2 indicators). Single agent can handle this.

## Task Ledger

| Task | Agent | Status |
|------|-------|--------|
| TASC articles + PDFs | direct | pending |
| MQL5 implementations | direct | pending |
| Forum search (10 forums) | direct | pending |
| Photos/videos/interviews | direct | pending |
| External books with full refs | direct | pending |
| BibTeX generation | direct | pending |

## Verification Log

(filled during run)

## Known Indicators (to verify & expand)

- **T3 (Tillson T3)** — a smoothed moving average using generalized DEMA (GD) with volume factor; applies GD iteratively 3 times
- **T3 formula:** T3 = GD(GD(GD(price))) where GD(x,v) = EMA(x)×(1+v) - EMA(EMA(x))×v
- Default volume factor v = 0.7
- Possibly other indicators from additional TASC articles

## Known Context

- T3 article was TASC January 1998: "Smoothing Techniques for More Accurate Signals"
- Builds directly on Patrick Mulloy's DEMA/TEMA concept (TASC Jan/Feb 1994)
- T3 is widely implemented but less universally built-in than DEMA/TEMA
