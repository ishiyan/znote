# Provenance: Tushar Chande

## Sources Consulted

| Source | Query | Results | Date |
|--------|-------|---------|------|
| TASC Article Index (cached, 1982–2025) | "Chande" | 23 entries (21 by Chande, 2 about him) | 2026-06-03 |
| IFTA Journal Index | "Chande" | 0 results | 2026-06-03 |
| JoTA Journal Index | "Chande" | 0 results | 2026-06-03 |
| Trader's World Magazine Index | "Chande" | 0 results | 2026-06-03 |
| MQL5 CodeBase | CMO / VIDYA / Aroon | code/784, code/75, code/389 | 2026-06-03 |
| MQL5 Forum | "Chande Momentum Oscillator" | forum/4355 | 2026-06-03 |
| Quantitative Finance Stack Exchange | "Chande Momentum Oscillator" | questions/37636 | 2026-06-03 |
| Google Patents | inventor:"Tushar S. Chande" | 11 patents (9 first-inventor), all GE | 2026-06-03 |
| OpenLibrary | Chande book titles | 5 records (2 distinct works + editions/translation) | 2026-06-03 |
| GitHub (git tree + curl HTTP 200) | CMO/VIDYA/Aroon/StochRSI/Qstick/CKSP | 18 verified file URLs across 6 libraries | 2026-06-03 |
| Top Traders Unplugged | "Tushar Chande" | Ep. 05/06 (2014) + guest page | 2026-06-03 |
| YouTube / StockCharts TV / TrendSpider | "Tushar Chande" | Channel + 6 video appearances | 2026-06-03 |
| Reddit | "Tushar Chande" | BLOCKED | 2026-06-03 |
| Web search engines (Google/Bing/DDG/Brave) | Tuscarora CTA, MBA | BOT-BLOCKED | 2026-06-03 |

## Confidence Summary

**VERIFIED (primary/authoritative source):**
- All 21 Chande-authored + 2 about-him TASC articles (verbatim from cached `tasc-article-index.bib`).
- 11 U.S. patents (Google Patents, all assigned to General Electric) — corroborates the engineering Ph.D. and "nine patents" claim (9 as first-named inventor).
- Book ISBNs/editions (OpenLibrary): *The New Technical Trader* (1994), *Beyond Technical Analysis* 1st (1997) / 2nd (2001) / e-book (2008) / Spanish trans. (1999). **Corrected** the earlier file's 1997↔2001 ISBN mismatch.
- 18 GitHub implementation file URLs (each curl-confirmed HTTP 200).
- Rho Asset Management role (Top Traders Unplugged 2014 episodes).
- Stanley Kroll collaboration (1994 co-authored book + May 1993 TASC article).

**REPORTED BUT UNCONFIRMED (search engines bot-blocked / sources paywalled):**
- MBA in finance.
- Tuscarora Capital Management CTA registration (NFA/SEC not reachable).
- *Schenectady, NY* specifically (GE patents confirm GE, not the city).

## Notes & Caveats

- The "When Is Berkshire Hathaway" TASC entry carries `month = {bon}` (Bonus issue, V35/N13).
- Book-introduced indicators (CMO, Aroon, Qstick, IMI, Chande-Kroll Stop in *The New Technical Trader*; RAVI, Chandelier Exit in *Beyond Technical Analysis*) are attributed by established convention, not a primary-source read of the books.
- `twopirllc/pandas-ta` is removed (404); `xgboosted/pandas-ta-classic` is the verified successor used here.
- No verified clean library implementation of Chande's Dynamic Momentum Index or RAVI; `dm.py` in pandas-ta-classic is Wilder's Directional Movement (do not conflate).
