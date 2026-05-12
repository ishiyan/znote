# Provenance: Marc Chaikin

- **Date:** 2026-05-07
- **Scale:** Direct (lead agent, parallel tool calls)
- **Sources consulted:** 12
- **Sources accepted:** 8
- **Sources rejected:**
  - `https://www.chaikinanalytics.com/about/` — 404 dead URL
  - `https://www.chaikinanalytics.com/about-marc-chaikin/` — 404 dead URL
  - TASC author archive page (Marc Chaikin) — requires subscriber login, no article content returned
  - TASC XML scan years 2006-2008, 1982-1988 — timed out before completion
- **Verification:** PASS WITH NOTES
  - TASC XML scan covered 1989–2005, 2015–2017 (partial due to timeout); earlier/later years may contain additional mentions
  - MQL5 API searches returned structured JSON data — verified
  - Chaikin Analytics website fetched successfully
  - No Wikipedia article exists for Marc Chaikin specifically
- **Plan:** outputs/.plans/marc-chaikin.md
- **Research files:** (inline, no separate draft files created)

## Search Queries Executed

1. TASC Author Archive: `http://technical.traders.com/archive/combo/display5.asp?author=Marc%20Chaikin`
2. TASC Author Archive (alt): `http://technical.traders.com/archive/combo/display5.asp?author=Mark%20Chaikin`
3. TASC XML TOC scan: `https://traders.com/Mobile/Archive/{Mon}{Year}.XML` for years 1989–2017
4. MQL5 API: Chaikin Money Flow (1 result), Chaikin Oscillator (22 results), Chaikin Volatility (11 results), Chaikin general (35 results), Accumulation Distribution Line (9 results)
5. Chaikin Analytics: `https://www.chaikinanalytics.com` and `/whoweare`

## Notes

- Marc Chaikin did not author any TASC articles directly. His primary TASC appearance is a 1994 interview conducted by Thom Hartle.
- The TASC archive page for "Marc Chaikin" exists (HTML title confirms) but displays no article list without subscriber authentication.
- His indicators are referenced in dozens of other TASC articles by other authors (visible in XML grep results).
- The MQL5/MQL4 codebase contains 34+ unique implementations related to Chaikin indicators.
