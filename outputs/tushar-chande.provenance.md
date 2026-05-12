# Tushar Chande — Provenance Sidecar

## Research Metadata
| Field | Value |
|-------|-------|
| Subject | Tushar S. Chande |
| Research Date | 2026-05-07 |
| Output File | `tushar-chande.md` |

## Source Verification

### TASC Articles (17 total)
| # | Article | Verification Method | Status |
|---|---------|-------------------|--------|
| 1–17 | All 17 articles | XML TOC scan of technical.traders.com monthly archives 1991–2010 | ✅ Confirmed via XML metadata |

**Note:** Author archive endpoint broken (XML files missing for "TUSHAR CHANDE" and "TUSHAR S CHANDE"). Articles confirmed via systematic monthly TOC scan instead.

### Books (3 editions)
| Book | Verification | Status |
|------|-------------|--------|
| The New Technical Trader (1994) | ISBN 0471597805 confirmed | ✅ |
| Beyond Technical Analysis 1st ed (1997) | ISBN 0471161888 confirmed | ✅ |
| Beyond Technical Analysis 2nd ed (2001) | ISBN 047141567X confirmed | ✅ |

### MQL5 Implementations (40+ entries)
| Category | Count | Verification |
|----------|-------|-------------|
| CMO | 7 | URLs verified via mql5.com/en/code |
| VIDYA | 8 | URLs verified; code/75 = MetaQuotes built-in |
| Aroon | 8 | URLs verified |
| RAVI | 4 | URLs verified |
| QStick | 3 | URLs verified |
| StochRSI | 1 | URL verified |
| DMI | 4 | URLs verified |
| Chandelier Exit | 4 | URLs verified (misattributed to Chande; actually Le Beau) |
| Mass Index | 1 | URL verified |
| **Total** | **40** | |

### Indicator Formulas (8 documented)
| Indicator | Source | Status |
|-----------|--------|--------|
| CMO | *The New Technical Trader* + TASC articles | ✅ Formula verified |
| VIDYA | TASC Mar 1992 + *Beyond Technical Analysis* p.36 | ✅ Formula verified |
| Aroon | TASC Sep 1995 | ✅ Formula verified |
| RAVI | *Beyond Technical Analysis* (1997) | ✅ Formula verified |
| StochRSI | TASC May 1993 + *The New Technical Trader* | ✅ Formula verified |
| QStick | *The New Technical Trader* | ✅ Formula verified |
| DMI | TASC May 1993 + *The New Technical Trader* | ✅ Formula verified |
| Trend Score | *Beyond Technical Analysis* | ⚠️ Minor indicator, less verified |

### Chandelier Exit Misattribution
| Claim | Correction | Evidence |
|-------|-----------|----------|
| "Chandelier Exit by Chande" | Developed by Charles Le Beau | Le Beau's original work; popularized by Alexander Elder in *Come Into My Trading Room*. Chande discussed ATR-based stops but did not create Chandelier Exit. |

### Media & Photos
| Item | Status | Notes |
|------|--------|-------|
| YouTube videos | ❌ Not found | YouTube blocked scraping |
| Personal website | ❌ Unverified | Domain status unknown |
| LinkedIn | ❌ Not accessible | Requires login |
| TASC Interview (1997) | ✅ Confirmed | V15:10, by Thom Hartle |

### Forum Discussions
| Forum | Status |
|-------|--------|
| MQL5 Forum (5 threads) | ✅ URLs verified |
| ForexFactory, TradingView, futures.io, Reddit | ⚠️ Known active but specific URLs not retrieved (search blocked) |

## Limitations & Gaps

1. **Author archive broken** — technical.traders.com XML files missing for Chande; relied on monthly TOC scan
2. **No Wikipedia page** — No dedicated Wikipedia article exists for Tushar Chande
3. **Video/photo URLs** — Could not retrieve direct YouTube or personal website URLs
4. **Forum URLs** — Google search blocked; only MQL5 forum threads directly confirmed
5. **Traders' Tips** — No applicable Tips pages (last article 2001, Tips format started later for web)
6. **Page numbers** — Not available for all articles (XML metadata incomplete for some issues)

## Completeness Checklist

- [x] 17 TASC articles documented with PDF paths
- [x] 3 books with ISBNs and Google Books links
- [x] 8 indicators with formulas
- [x] 40+ MQL5 implementations catalogued
- [x] Chandelier Exit misattribution corrected
- [x] BibTeX entries for all articles and books (20 entries)
- [x] Community implementations (TA-Lib, pandas-ta, TradingView, MT5)
- [x] Forum discussions documented
- [ ] Video/photo direct URLs (not retrievable)
