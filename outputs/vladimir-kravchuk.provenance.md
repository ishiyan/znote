# Vladimir Kravchuk — Provenance Sidecar

**Research date:** 2026-05-07  
**Researcher:** OpenCode (claude-opus-4.6)  
**Status:** Complete (with noted gaps)

---

## Source Classification

| # | Source | Type | Access | Confidence |
|---|--------|------|--------|------------|
| 1–10 | MQL5 Code Base indicator pages | Primary (code attribution) | Public | High |
| 11 | MQL5 Article (Gizlyk 2017) | Secondary (implementation) | Public | High |
| 12 | TASC Author Archive page | Primary (existence confirmation) | Public (listing requires login) | Medium |
| 13 | "Currency Speculator" magazine 2001–2002 | Primary (original publication) | Not accessed; cited via [11] | Medium (secondhand) |

---

## Methodology

1. Attempted TASC author page fetch — confirmed page exists, article list behind paywall
2. Scanned TASC XML monthly archives (2004–2010) — no matches for "Kravchuk"
3. Searched MQL5 code base — found 10 indicator entries crediting Kravchuk as "Real author"
4. Retrieved MQL5 article by Gizlyk (2017) — primary English-language technical description of AT&CF
5. Attempted Google searches for Russian-language sources — blocked by bot detection
6. Searched TradingView — no scripts found
7. Checked for Krawtchouk polynomial connection — ruled out (different person, different math)

---

## Known Gaps

| Gap | Impact | Mitigation |
|-----|--------|------------|
| TASC article titles/PDF paths unknown | Cannot provide direct TASC citations | Author page URL provided; subscriber could complete |
| Original Russian articles not accessed | Technical details rely on MQL5 secondhand descriptions | Gizlyk 2017 article is detailed and consistent |
| No photo/bio confirmed | Cannot verify identity details | Low impact for technical research |
| Google blocked Cyrillic searches | May miss Russian forum discussions | Could retry with VPN/different search engine |
| Finware.ru website not accessed | Cannot confirm company details | Noted as associated entity |

---

## Verification Notes

- All 10 MQL5 code entries independently and consistently credit "Vladimir Kravchuk" as Real Author
- All reference the same source: "Currency Speculator" magazine, 2001–2002
- Technical description is internally consistent across all sources
- The 8 indicators form a mathematically coherent filter bank (verified: FTLM = FATL − RFTL is consistent with FIR filter theory)
- No contradictory information found across any source

---

## Replication Instructions

To verify or extend this research:
1. Access TASC subscriber archive at the author URL to get article titles and PDF paths
2. Search for "Валютный спекулянт Кравчук" on Russian search engines (Yandex)
3. Check Finware.ru (may be archived on Wayback Machine)
4. Review MQL5 forum threads referencing AT&CF method
