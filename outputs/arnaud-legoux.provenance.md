# Arnaud Legoux — Provenance Sidecar

## Research Metadata
- **Date conducted:** 2026-05-07
- **Researcher:** OpenCode (automated)
- **Subject:** Arnaud Legoux, creator of ALMA indicator

## Source Verification Log

| # | Source | Method | Status | Notes |
|---|--------|--------|--------|-------|
| 1 | TASC Author Archive | HTTP GET to technical.traders.com | ✅ Retrieved | Page exists but contains zero article entries |
| 2 | TASC TOC XMLs (2009–2014) | HTTP GET to traders.com/Mobile/Archive/ | ⏱ Timeout | Scan timed out; no matches found before timeout |
| 3 | MQL5 API — "ALMA Arnaud Legoux" | JSON API query | ✅ 5 results | Confirmed co-authorship with Dimitris Kouzis-Loukas |
| 4 | MQL5 API — "ALMA" | JSON API query | ✅ 8 results | Multiple third-party implementations |
| 5 | MQL5 API — articles | JSON API query | ✅ 0 results | No MQL5 articles by Legoux |
| 6 | Wayback Machine — arnaudlegoux.com | WebFetch | ✅ Retrieved | Confirmed Paris address, 2009 copyright, blog posts about ALMA |

## Key Claims & Evidence

| Claim | Evidence | Confidence |
|-------|----------|------------|
| Legoux is based in Paris, France | Wayback archive shows "Paris 75003 France" | High |
| ALMA co-created with Dimitris Kouzis-Loukas | MQL5 code description: "The real author: Arnaud Legoux & Dimitris Kouzis-Loukas" | High |
| ALMA introduced ~2009 | Website copyright "2009 © Arnaud Legoux"; earliest MQL5 code dated Dec 2012 | High |
| No TASC publications | Author archive page returns 0 results | High |
| ALMA uses Gaussian weighting with offset | MQL5 descriptions + website tags ("Fir filter", "alma formula", "Gaussian") | High |

## Gaps & Limitations

1. **arnaudlegoux.com full content** — The site is archived but individual blog posts (e.g., the technical article about ALMA) could not be retrieved (404 on specific post URLs)
2. **TASC TOC XML scan** — Timed out before completing; however, the author archive returning zero results is strong evidence of no TASC publications
3. **Dimitris Kouzis-Loukas** — Co-author's background not researched (he appears to be a data scientist/author of "Learning Scrapy")
4. **Original PDF article** — The website references a "pdf article" (visible in tags) but the document itself was not retrievable from archive
