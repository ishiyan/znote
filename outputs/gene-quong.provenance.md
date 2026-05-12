# Gene Quong — Provenance Sidecar

## Search Queries Executed

| # | Source | Query / URL | Date | Result |
|---|--------|-------------|------|--------|
| 1 | TASC Author Archive | `display5.asp?author=Gene%20Quong` | 2026-05-07 | Page returned but no parseable article list (subscriber-only content) |
| 2 | TASC Author Archive | `display5.asp?author=Quong` | 2026-05-07 | Same as above |
| 3 | TASC Author Archive | `display5.asp?author=Soudack` | 2026-05-07 | Same as above |
| 4 | TASC XML TOC | `MAR1989.XML` | 2026-05-07 | **HIT** — "Volume-weighted RSI: money flow by Gene Quong and Avrum Soudack" |
| 5 | TASC XML TOC | 1989–1995 (all months) | 2026-05-07 | Only MAR1989 matched for Quong |
| 6 | MQL5 Code Base | `keyword=Money+Flow+Index` | 2026-05-07 | 25 total results, 20 returned |
| 7 | MQL5 Code Base | `keyword=Gene+Quong` (articles) | 2026-05-07 | 1 result (tutorial article) |

## Verification Status

| Claim | Status | Evidence |
|-------|--------|----------|
| Quong & Soudack co-created MFI | **VERIFIED** | TASC Mar 1989 V.7:3 pp.76-77 |
| MFI introduced in TASC March 1989 | **VERIFIED** | XML TOC metadata |
| MFI described as "volume-weighted RSI" | **VERIFIED** | Article title: "Volume-Weighted RSI: Money Flow" |
| Quong associated with MetaStock/Equis | **UNVERIFIED** | No evidence found in accessible sources |
| Quong published only 1 TASC article | **LIKELY** | Full TOC scan 1989-1995 found no other matches |

## Completeness Assessment

- **TASC articles found**: 1 (high confidence this is complete — full XML scan 1989–1995 performed)
- **MQL5 implementations found**: 19 (18 code base + 1 article)
- **Indicators documented**: 1 (Money Flow Index)
- **Books**: None found
- **Limitations**: TASC author archive pages require subscriber login to display article lists; relied on XML TOC scanning instead. XML TOCs before 1989 and after 1995 were not exhaustively scanned but Quong's only known contribution is the 1989 MFI article.
