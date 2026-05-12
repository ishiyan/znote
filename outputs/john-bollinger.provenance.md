# Provenance: John Bollinger Research Brief

- **Date:** 2026-05-07
- **Scale:** Direct search (lead agent)
- **Sources consulted:** 9
- **Sources accepted:** 9
- **Sources rejected:** 0
- **Verification:** PASS WITH NOTES

## Verification Notes

- TASC author archive returned only 2 articles authored directly by Bollinger (1992, 1993). The TASC XML scan (1982–2026) timed out before completing all years but successfully scanned through ~2022. The grep-based approach found articles *mentioning* Bollinger Bands but no additional Bollinger-authored articles beyond the 2 from the author archive.
- Wikipedia biography data is consistent across all cross-referenced sources (born 1950, CFA+CMT, FNN 1984–1990, awards in 1995/2005/2015).
- MQL5 search returned 321 codebase items and 15 articles — these totals come directly from the API `total` field.
- BollingerBands.com was not fetched directly but is referenced as a known source.
- The LA Times and CFA Magazine profiles were not fetched but are cited by Wikipedia with stable URLs.

## Search Queries Executed

1. `curl http://technical.traders.com/archive/combo/display5.asp?author=John%20Bollinger` — 2 articles found
2. `curl https://traders.com/Mobile/Archive/{Mon}{Year}.XML` for 1982–2026 — grep for "bollinger" (case-insensitive)
3. `https://search.mql5.com/api/query?keyword=Bollinger+Bands&module=mql5.com.en.codebase|mql4.com.en.codebase` — 295 results
4. `https://search.mql5.com/api/query?keyword=Bollinger&module=mql5.com.en.codebase|mql4.com.en.codebase` — 321 results
5. `https://search.mql5.com/api/query?keyword=BandWidth+%25b+Bollinger&module=mql5.com.en.codebase|mql4.com.en.codebase` — 1 result
6. `https://search.mql5.com/api/query?keyword=John+Bollinger&module=mql5.com.en.articles|mql4.com.en.articles` — 15 results
7. `https://en.wikipedia.org/wiki/John_Bollinger` — fetched successfully

## Artifacts

- **Final output:** `outputs/john-bollinger.md`
- **Provenance:** `outputs/john-bollinger.provenance.md`
