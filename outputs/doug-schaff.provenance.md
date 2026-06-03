# Provenance: Doug Schaff

- **Date:** 2026-06-03
- **Scale:** 3 parallel agents (T1 mechanics+lineage, T2 biography+adoption, T3 critical/academic) + lead synthesis
- **Deliverable:** `outputs/doug-schaff.md` (investigative deep-research brief, 522 lines)
- **Companion catalog:** none yet (no standalone `trading-research/doug-schaff.md`); the two 1999 Bressert+Schaff Euro entries live in `trading-research/walter-bressert.md` and `.opencode/skills/trading-research/tasc-article-index.md`
- **Sources cited in brief:** 25
- **DOIs verified in Crossref (titles matched exact):** 13 / 13 (12 original + White 2000 added in review)
- **Platform/code/abstract URLs verified HTTP 200:** prorealcode schaff-trend-cycle2, prorealcode schaff-trend-cycle, github pandas-ta-classic stc.py, traders.com V17abs, motivewave studies/s-t, mql5 code/486, 7356, 20281, 20282, 20283, 21787, 13434
- **Investopedia (live URL 402 bot-block):** content confirmed live via Wayback CDX — snapshot **2010-01-17, status 200** (validates "live by 2010" + STC "developed 1999" attribution to Schaff via Brian Twomey)
- **Sources blocked / unverified this pass:** earnforex.com STC guide (HTTP 000 timeout from final-pass env; content agent-confirmed); TASC Euro PDFs `\V17\C05\033EURO`, `\V17\C06\043EURO` (HTTP 302 → subscriber login — abstracts verified, full text paywalled); Google/Bing/DDG/Brave/SearXNG, ForexFactory & futures.io search (403); Reddit JSON
- **Verification:** PASS WITH NOTES
- **Adversarial review:** 1 MINOR fixed — source [8] was a placeholder redirect ("see [18]") cited in-text at §5; replaced with the genuine distinct method paper White (2000) "A Reality Check for Data Snooping" (Econometrica, DOI Crossref-verified), which the text already references by name; BibTeX added
- **Plan:** `outputs/.plans/doug-schaff.md` (APPROVED) + agent briefs `doug-schaff-T{1,2,3}.md`
- **Research files:**
  - `outputs/.drafts/doug-schaff-research-mechanics.md` (T1: STC formula/params/pseudocode + lineage + 1999 articles)
  - `outputs/.drafts/doug-schaff-research-biography.md` (T2: bio/firm/publication/adoption/status)
  - `outputs/.drafts/doug-schaff-research-critical.md` (T3: STC vs MACD, academic evidence, verdict)
  - `outputs/.drafts/doug-schaff-draft.md` (synthesis = final)

## Key Findings & Confidence

| Finding | Confidence | Basis |
|---|---|---|
| STC = double-stochastic (stochastic-of-smoothed-stochastic) applied to MACD line, scaled 0–100 | High | Byte-concordant open-source code (ProRealCode schaff-trend-cycle2 + pandas-ta stc.py) |
| Defaults TCLen=10, Factor=0.5 (EMA α=0.5), OB/OS 75/25 | High (as platform defaults) | ProRealCode + pandas-ta + MotiveWave docs |
| Fast/slow MACD EMA = 23/50 (forex-native) vs 12/26 (generic library) | Medium | 23/50 verified as ProRealCode default; **UNCONFIRMED as Schaff's own published numbers** |
| Lineage: Appel (MACD input) + Lane (stochastic ×2) | High | Direct, in code |
| Lineage: Bressert closest ancestor (DSS stochastic-of-a-stochastic + 1999 forex collab) | High (collab) / Inferred (copy) | TASC 1999 co-authorship + mechanical pattern match to "DSS Bressert" |
| Lineage: Blau = conceptual cousin, different mechanism | High | Component-double-EMA vs cascade distinction |
| STC "developed 1999" | Low | Sourced only to Investopedia/Twomey; no primary Schaff dating |
| Schaff's only TASC bylines = 2 Bressert co-authored 1999 Euro articles | High | Exhaustive 1982–2025 index check |
| STC first published OUTSIDE TASC (~2008 via forex software, then Investopedia ~2010) | Medium | EarnForex/MQL5 "made public 2008"; exact first venue UNCONFIRMED |
| "FX Strategy" firm (Schaff founder/president) | Low / unconfirmed | Cannot tie to fxstrategy.com (parked 2005–08 per Wayback); no registration/trademark found |
| Schaff biography (birth year, education, nationality, photo, interview) | Not found | Every "Schaff" media hit is third-party indicator tutorial |
| Current life status | Unknown | No death record found (channels blocked, not confirmed negative); do not assert death |
| Cross-platform adoption (TradingView built-in, ~25 MQL CodeBase, ProRealTime, NinjaTrader, MotiveWave, cTrader, pandas-ta) | High | MQL5 search API + TradingView directly evidenced |
| STC structurally redundant with fast MACD; "earlier" = rescaling artifact; bounding reintroduces trend-pinning; STC is causal (no look-ahead) | High | Deductive/structural from formula |
| No peer-reviewed study of STC by name; rule-class FX/timing evidence mostly negative after costs + snooping | High | Crossref-verified literature (Qi-Wu, Olson, Neely-Weller, Sullivan-Timmermann-White, Park-Irwin, White, Marshall) |

## Corrections vs. folklore
- STC was **not** first published in TASC under Schaff's name; his only TASC bylines are two 1999 cycle articles co-authored with Walter Bressert that do not (per their abstracts) introduce STC.
- The "Doug Schaff, founder of FX Strategy" attribution could **not** be tied to the live fxstrategy.com domain (parked/for-sale 2005–08) — treat with caution.
- STC's much-marketed "faster and more accurate than MACD" is an author/vendor claim; **no independent test or academic validation by name was located.**
- STC's canonical form is a **double** stochastic; single-pass community variants are simplifications, not the reference indicator.

## Open gaps / future passes
- Locate any primary Schaff publication defining STC and its 23/50/10/0.5 defaults in his own words.
- Obtain full text of the two 1999 TASC Euro PDFs (paywalled) to confirm whether STC appears inside.
- Identify Doug Schaff personally (birth year, education, nationality, photograph; living or deceased).
- Determine the real "FX Strategy" entity and the exact ~2008 first-publication venue of STC.
- Enumerate ForexFactory / futures.io / NinjaTrader forum reception once search bot-walls clear.
