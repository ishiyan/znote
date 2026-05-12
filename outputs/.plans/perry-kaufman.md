# Research Plan: Perry Kaufman

## Key Questions

1. Who is Perry Kaufman? (biography, career, education, books, consulting)
2. What technical indicators did he invent? (KAMA, Efficiency Ratio, others from his books)
3. What TASC articles did he author? (full list — he's been writing for TASC for decades, likely 20+ articles)
4. What books did he write? (Trading Systems and Methods is the definitive reference, multiple editions)
5. What are the reference/community implementations? (MQL5, TA-Lib, TradingView, pandas-ta)
6. What forum discussions exist about his work?
7. Are there photos, videos, interviews available?

## Evidence Needed

- TASC Author Archive page (likely extensive — possibly 30+ articles spanning 1990s–2020s)
- TASC TOC XMLs (systematic scan 1990–2026)
- MQL5 CodeBase (KAMA, Efficiency Ratio, Kaufman)
- Trading forums (all 10 mandatory)
- Wikipedia / web bios
- YouTube / podcast interviews
- His books (Trading Systems and Methods 1st–6th ed., Smarter Trading, Alpha Trading, others)

## Scale Decision

**Parallel Task agents (2 agents)** — Perry Kaufman is extremely prolific (likely 30+ TASC articles, 6+ books, many indicators). Split:
- Agent T1: TASC articles (full XML scan + author archive) + Traders' Tips
- Agent T2: MQL5 implementations + forums + photos/videos/interviews + books

## Task Ledger

| Task | Agent | Status |
|------|-------|--------|
| TASC articles + PDFs + Tips | T1 | pending |
| MQL5 implementations | T2 | pending |
| Forum search (10 forums) | T2 | pending |
| Photos/videos/interviews | T2 | pending |
| Books (full citations) | T2 | pending |
| BibTeX generation | lead | pending |
| Final draft | lead | pending |

## Verification Log

(filled during run)

## Known Indicators (to verify & expand)

- **KAMA (Kaufman Adaptive Moving Average)** — adapts speed based on Efficiency Ratio
- **Efficiency Ratio (ER)** — direction/volatility measure
- **Adaptive Momentum** — from books
- Various systems from "Trading Systems and Methods"
- Possibly: noise filters, volatility-based position sizing methods

## Known Books (to get full citations)

- Trading Systems and Methods (1st ed 1978, ... 6th ed 2020)
- Smarter Trading (1995)
- A Short Course in Technical Trading (2003)
- Alpha Trading (2011)
- Possibly others
