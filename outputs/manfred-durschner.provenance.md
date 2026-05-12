# Manfred Durschner — Provenance Sidecar

## Research Methodology

- **TASC Author Archive**: Queried http://technical.traders.com/archive/combo/display5.asp with author parameters "Manfred Durschner", "Manfred Dürschner", and "Durschner". All returned empty result pages (no article listings).
- **TASC TOC XMLs**: Scanned https://traders.com/Mobile/Archive/{Mon}{Year}.XML for all months 1990–2026 searching for "dursch" and "rschner" patterns. Zero matches found.
- **MQL5 Code Base Search API**: Queried https://search.mql5.com/api/query with keywords "Durschner", "Manfred Durschner", "Dürschner", "Duerschner", and "3rd generation moving average". Found 5–6 implementations referencing Dürschner.
- **Web Search (Bing)**: Searched for "Manfred Durschner", "Manfred Dürschner", and related queries. No direct results for the author found (only Byron's "Manfred" literary references).
- **EarnForex.com**: Retrieved indicator page confirming attribution to "M. Duerschner" and article title "Gleitende Durchschnitte 3.0".

## Confidence Assessment

| Claim | Confidence | Basis |
|-------|-----------|-------|
| Full name: Manfred G. Dürschner | HIGH | Consistent across 5+ MQL5 implementations |
| Holds doctorate (Dr.) | MEDIUM | Referenced as "Dr. Manfred Dürschner" in one MQL5 code description |
| Published "Gleitende Durchschnitte 3.0" | HIGH | Referenced in all implementations |
| Published in German (not English TASC) | HIGH | Article title is German; TASC archive empty; described as "(in German)" in all refs |
| Publication venue: TRADERS' Magazin (Germany) | LOW | Inferred; no direct confirmation of specific venue |
| Publication year ~2008 | LOW | Estimated from earliest MQL5 implementation date (2012) minus typical lag |
| Not a TASC author | HIGH | Empty TASC archive + empty XML scan across 36 years |
| Created 3rd Generation Moving Average | HIGH | Universal attribution across all sources |

## Date of Research

2026-05-07

## Tools Used

- curl (HTTP requests to TASC archive, TASC XMLs, MQL5 search API)
- WebFetch (Bing searches, EarnForex page)
- MQL5 search API (https://search.mql5.com/api/query)
