# Provenance: Doug Schaff

- **Date:** 2026-06-03
- **Mode:** Author
- **Deliverable:** `trading-research/doug-schaff.md`
- **Companion deep-research brief:** `outputs/doug-schaff.md` (+ `.provenance.md`)
- **Pipeline:** cached TASC index search + 3 parallel Task agents (MQL5/TradingView; GitHub/forums; biography/media) + lead synthesis with independent verification of all biography/photo sources

## Sources Consulted

| Source | Query | Results | Date |
|--------|-------|---------|------|
| TASC cached index (1982–2025) | "Schaff" | 2 articles (both Bressert+Schaff 1999) | 2026-06-03 |
| TASC bib index | EURO / Schaff | 2 BibTeX keys located | 2026-06-03 |
| MQL5 Search API (codebase) | "schaff trend cycle", "schaff" | 33 unique CodeBase entries | 2026-06-03 |
| MQL5 Search API (articles) | "schaff trend cycle" | 1 (articles/3074, indirect) | 2026-06-03 |
| MQL5 code URLs | HTTP check 486/7356/13434/20281-3/21787 | all 200 | 2026-06-03 |
| TradingView scripts tag | schafftrendcycle | built-in ta.stc + ~10 community scripts | 2026-06-03 |
| GitHub repo search (REST) | "schaff trend cycle" | 3 dedicated repos | 2026-06-03 |
| GitHub library file inspection | ta, freqtrade/technical, pandas-ta-classic | 3 libraries with STC | 2026-06-03 |
| FX-Strategy team.php (Wayback 2006) | biography | full primary-source bio (verified 200) | 2026-06-03 |
| FX-Strategy bio_DS.htm (Wayback 2001) | biography | MBA/Bankers Trust/Merrill/Refco (verified 200) | 2026-06-03 |
| FX-Strategy image dir (Wayback 2007) | photos | 3 photos verified 200 image/jpeg | 2026-06-03 |
| WIRED 2005 | "Fearless Traders Flock to Forex" | 1 press mention (verified 200) | 2026-06-03 |
| TASC Letters Jun 2010 | STC 2008 release | verified 200 | 2026-06-03 |
| Crossref (companion brief) | 13 DOIs | all title-verified (see outputs/doug-schaff) | 2026-06-03 |

## Blocked / login-gated (reported, not "no results")

- Forums: ForexFactory (JS shell), futures.io (403), Elite Trader (403), NinjaTrader (login), MQL5 forum (JS), Wealth-Lab (404), Reddit r/algotrading (403), Trade2Win (404) — 8 of 10
- Search engines: Google/Google Books, Bing, DuckDuckGo HTML — CAPTCHA/JS interstitial
- YouTube `/results` — JS-rendered empty shell (no Schaff videos located)
- Investopedia live STC article — HTTP 402 (content confirmed via Wayback in companion brief)
- `twopirllc/pandas-ta` — 404 (repo removed; superseded by pandas-ta-classic fork)
- `tradingview.com/support/solutions/...STC` slug — 404
- `gh` CLI not installed / GitHub code search needs auth — used REST repo search + direct file inspection instead

## Key Findings & Confidence

| Finding | Confidence | Basis |
|---|---|---|
| Founder/president of FX-Strategy, Inc. (Red Hook, NY) | High | Primary source: FX-Strategy team.php (2006) + bio_DS.htm (2001) |
| MBA Univ. of Chicago; Bankers Trust → Merrill Lynch Bank (1982) → Refco (1985); private trader 1987 | High | Primary source: bio_DS.htm (2001) |
| Person↔STC link: firm names STC as Schaff's tool | High | team.php: "Schaff Trend Cycle & automated trading systems on Pro Charts" |
| STC code released publicly 2008 | High | TASC Letters Jun 2010 + EarnForex |
| Only 2 TASC bylines (1999, with Bressert) | High | Exhaustive cached-index check |
| ~33 MQL5 Schaff-family CodeBase entries | High | MQL5 Search API |
| Birth year / current life status | Not found | No record located; do not assert death |
| Firm in-house book ISBNs | Not found | Listed without ISBN |

## Corrections vs. prior research

- **Major correction to `outputs/doug-schaff.md`:** the FX-Strategy firm and Schaff's
  institutional biography are NO LONGER unconfirmed. The earlier brief failed to
  distinguish `fx-strategy.com` (hyphenated, real firm, archived 2001–2011) from
  `fxstrategy.com` (unrelated parked/affiliate site). Primary-source bio pages and 3
  archived photographs were located this pass. The deep-research brief should be
  updated to reflect the confirmed firm + biography.
- No video or dedicated interview of Doug Schaff himself exists (only third-party STC
  tutorials + a 2005 WIRED quote).

## Open gaps / future passes

- Birth year / current life status of Doug Schaff.
- ISBNs for the two FX-Strategy in-house titles.
- Full text of the two paywalled 1999 TASC Euro PDFs.
- Forum reception (8 of 10 forums bot-blocked this pass).
