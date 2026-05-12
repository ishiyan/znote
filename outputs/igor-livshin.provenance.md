# Provenance: Igor Livshin TASC Author Research

- **Date:** 2026-05-07
- **Scale:** Direct search (lead agent)
- **Sources consulted:** 8
- **Sources accepted:** 4
- **Sources rejected:**
  - Amazon search for "Igor Livshin trading" — no relevant results (different author "Igor Pinho")
  - Google searches — blocked by JS requirement
  - TASC TOC XMLs for Sep 2009, Oct 2010, Dec 2012, Jan 2002 — no Livshin articles (Jan 2002 had a reader letter referencing his work)
  - MQL4 codebase search "balance of market power" — no direct BMP implementations found
- **Verification:** PASS WITH NOTES
  - Only 1 TASC article confirmed across archive page + XML scan
  - No book identified despite searching Amazon
  - TASC archive page is authoritative and shows only 1 article
- **Plan:** N/A (direct execution per user specification)
- **Research files:** N/A (inline)

## Methodology

1. Fetched TASC author archive page — returned 1 article (Balance Of Market Power, Aug 2001)
2. Fetched Aug 2001 TASC TOC XML — confirmed article with full metadata (V. 19:8, pp. 18-32)
3. Scanned additional TASC TOC XMLs (Sep 2009, Oct 2010, Dec 2012, Jan 2002) — no additional Livshin articles
4. Searched MQL5 codebase for "Igor Livshin" — 6 implementations (all MT5)
5. Searched MQL5 articles — 0 results
6. Searched MQL4 codebase for "Livshin" and "balance of market power" — 0 relevant results
7. Searched Amazon for books — none found
8. Google searches blocked

## Notes

- Igor Livshin appears to be a single-article TASC contributor
- His BMP indicator has gained moderate adoption in the MQL community (6 implementations by 3 different developers)
- The indicator is sometimes called "Balance of Power" (BOP) in third-party implementations
- A reader letter in TASC Jan 2002 discussed the BMP indicator, suggesting it received some attention from the trading community
