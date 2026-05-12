# Plan: Mark Jurik

## Key Questions

1. **Biography** — Who is Mark Jurik? Background, education, career timeline, company (Jurik Research & Consulting).
2. **Photos** — Any publicly available photos or appearances (conferences, interviews, book covers).
3. **Books & Publications** — What has he written or co-authored? TASC articles, books, white papers.
4. **Trading Indicators** — Complete catalog of indicators he created (JMA, VEL, CFB, RSX, DMX, etc.) — what each does, the claimed principles, any known algorithmic details.
5. **How They Work** — Mathematical/DSP underpinnings where known. Since JMA and others are proprietary/closed-source, document: (a) what Jurik himself has published about the methods, (b) reverse-engineering efforts by the community (MQL5, TradingView, forums).

## Evidence Needed

- TASC archive: search author "Mark Jurik" for all his published articles
- Traders' Tips pages referencing Jurik indicators
- Jurik Research website (jurikres.com) — product pages, white papers, any bio page
- MQL5 articles/code: reverse-engineered JMA, RSX implementations
- TradingView: Pine Script implementations of Jurik indicators
- ForexFactory/EliteTrader discussions
- Books: search for "Computerized Trading" (1999) edited by Jurik
- Academic/web sources on adaptive filtering that Jurik references

## Scale Decision

**Parallel Task agents (3 agents)** — This is a multi-faceted topic covering biography, publications, and technical indicator details across many source types.

- T1: Biography, photos, books, career (web sources, jurikres.com, book databases)
- T2: TASC publications and Traders' Tips (traders.com archive XML + Tips pages)
- T3: Indicators catalog and how they work (MQL5, TradingView, forums, reverse-engineering)

## Task Ledger

| Task | Owner | Status |
|------|-------|--------|
| T1 — Bio, photos, books | Task agent 1 | pending |
| T2 — TASC articles & Tips | Task agent 2 | pending |
| T3 — Indicators & internals | Task agent 3 | pending |
| Synthesis & draft | Lead | pending |
| Citation pass (3b) | Lead | pending |
| Adversarial review (6) | Lead | pending |
| Delivery | Lead | pending |

## Verification Log

(To be filled during execution)

## Decision Log

- Scale: 3 parallel agents chosen because topic spans biography (web), publications (traders.com structured data), and technical reverse-engineering (forums/code) — clearly decomposable.
- Will NOT attempt to access subscription-only TASC PDFs. Will extract metadata, synopses, and search for freely available copies.
