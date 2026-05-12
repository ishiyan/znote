# Research Plan: Tushar Chande

## Key Questions

1. Who is Tushar Chande? (biography, career, PhD, engineering background, consulting)
2. What technical indicators did he invent? (CMO, VIDYA, Aroon, others)
3. What TASC articles did he author? (likely 15-30+ articles, very prolific 1990s)
4. What books did he write?
5. What are the reference/community implementations? (MQL5, TA-Lib, TradingView, pandas-ta)
6. What forum discussions exist about his work?
7. Are there photos, videos, interviews available?

## Evidence Needed

- TASC Author Archive page (likely extensive — 1992–2000s)
- TASC TOC XMLs (systematic scan 1992–2010)
- MQL5 CodeBase (CMO, VIDYA, Aroon, Chande)
- Trading forums (all 10 mandatory)
- Wikipedia / web bios
- YouTube / podcast interviews
- His books (Beyond Technical Analysis, The New Technical Trader)

## Scale Decision

**Parallel Task agents (2 agents)** — Tushar Chande is very prolific (likely 15-30 TASC articles, 2-3 books, 8+ indicators). Split:
- Agent T1: TASC articles (full XML scan + author archive) + Traders' Tips
- Agent T2: MQL5 implementations + forums + photos/videos + books + indicator documentation

## Task Ledger

| Task | Agent | Status |
|------|-------|--------|
| TASC articles + PDFs + Tips | T1 | pending |
| MQL5 implementations | T2 | pending |
| Forum search (10 forums) | T2 | pending |
| Photos/videos/interviews | T2 | pending |
| Books (full citations) | T2 | pending |
| Indicator documentation | T2 | pending |
| BibTeX generation | lead | pending |
| Final draft | lead | pending |

## Verification Log

(filled during run)

## Known Indicators (to verify & expand)

- **CMO (Chande Momentum Oscillator)** — Oscillator
- **VIDYA (Variable Index Dynamic Average)** — Adaptive MA using CMO as volatility index
- **Aroon (Up/Down/Oscillator)** — Trend indicator measuring time since highs/lows
- **RAVI (Range Action Verification Index)** — Trend filter
- **StochRSI** — co-created with Stanley Kroll (RSI applied to RSI)
- **QStick** — quantifies candlestick patterns
- **Comfort Zone stops** — volatility-based trailing stops
- **Trend Score** — trend strength measure
- Possibly more from his books

## Known Books

- The New Technical Trader (with Stanley Kroll, 1994)
- Beyond Technical Analysis (1st ed 1997, 2nd ed 2001)
- Possibly others

## Known Bio Facts

- PhD in Engineering (metallurgical/materials, likely from University of Illinois or similar)
- Indian-American quantitative analyst
- Very active TASC contributor in the 1990s
- Founded tushar.com or similar consulting firm
- One of the most innovative indicator developers of the 1990s
