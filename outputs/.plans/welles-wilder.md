# Research Plan: Welles Wilder

## Key Questions

1. Who is J. Welles Wilder Jr.? (biography, career, mechanical engineering background, real estate, trading career, death)
2. What technical indicators did he invent? (RSI, ATR, ADX/DMI, Parabolic SAR, others — all from his 1978 book)
3. What TASC articles did he author? (likely few — his indicators predate TASC or were published in his book, not the magazine)
4. What books did he write?
5. What are the reference/community implementations? (MQL5, TA-Lib, TradingView, pandas-ta)
6. What forum discussions exist about his work?
7. Are there photos, videos, interviews available?

## Evidence Needed

- TASC Author Archive page
- TASC TOC XMLs (scan 1982–2000 for any Wilder articles)
- MQL5 CodeBase (RSI, ATR, ADX, Parabolic SAR, Wilder)
- Trading forums (all 10 mandatory)
- Wikipedia (he has a page)
- YouTube / interviews
- His book: "New Concepts in Technical Trading Systems" (1978) — THE foundational text

## Scale Decision

**Parallel Task agents (2 agents)** — Wilder invented 6-8 universally-adopted indicators (RSI, ATR, ADX are arguably the 3 most-used indicators in all of trading). MQL5 results will be enormous.
- Agent T1: TASC articles + biography + books + photos/videos
- Agent T2: MQL5 implementations (very large — RSI alone will have 500+) + forums + community implementations

## Task Ledger

| Task | Agent | Status |
|------|-------|--------|
| TASC articles + PDFs | T1 | pending |
| Biography (Wikipedia, web) | T1 | pending |
| Books (full citations) | T1 | pending |
| Photos/videos/interviews | T1 | pending |
| MQL5 implementations | T2 | pending |
| Forum search (10 forums) | T2 | pending |
| Community implementations | T2 | pending |
| BibTeX generation | lead | pending |
| Final draft | lead | pending |

## Verification Log

(filled during run)

## Known Indicators (all from "New Concepts in Technical Trading Systems", 1978)

- **RSI (Relative Strength Index)** — the most famous oscillator in existence
- **ATR (Average True Range)** — volatility measure
- **ADX (Average Directional Index) / DMI (Directional Movement Index)** — +DI, -DI, ADX
- **Parabolic SAR (Stop and Reverse)** — trailing stop/trend system
- **Swing Index / Accumulative Swing Index (ASI)** — price pattern indicator
- **Commodity Selection Index (CSI)** — ranks commodities by directional movement × volatility
- **True Range** — max(H-L, |H-C[1]|, |L-C[1]|)
- Possibly: Wilder's Smoothing (exponential-like with 1/N factor)

## Known Bio Facts

- J. Welles Wilder Jr. (June 11, 1935 – April 18, 2021)
- Born in Norris, Tennessee
- Mechanical engineer by training
- Made fortune in real estate before trading
- Published "New Concepts in Technical Trading Systems" in 1978
- Later became interested in astrology-based trading (Adam Theory, Delta Theory)
- Lived in New Zealand in later years
- Wikipedia page exists
