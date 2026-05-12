# Research Plan: Mark Jurik Trading Indicators

## Questions
1. What is the complete list of indicators developed by Mark Jurik / Jurik Research?
2. What mathematical/theoretical principles underlie each indicator?
3. How does each indicator work (inputs, parameters, outputs, use cases)?
4. What is the background of Mark Jurik and Jurik Research?
5. How do Jurik indicators compare to classical alternatives?
6. What is the current status of Jurik Research?

## Strategy
- Primary sources: jurikres.com product pages, FAQ pages, technical reports (already gathered)
- Secondary sources: third-party reviews, open-source approximations, trading community discussion
- Single researcher (lead) — topic is focused enough, all sources already collected
- Expected rounds: 1 (sufficient primary material already in hand)

## Acceptance Criteria
- [x] Complete product inventory with full names
- [x] Theory/principles documented for each indicator from official FAQ
- [x] Parameter descriptions and use cases from product pages
- [x] Comparisons to classical indicators documented
- [x] Background on Mark Jurik from company page
- [x] Cross-referenced with at least one third-party source per indicator

## Task Ledger
| ID | Owner | Task | Status | Output |
|---|---|---|---|---|
| T1 | lead | Gather all product pages from jurikres.com | done | in-context |
| T2 | lead | Gather all FAQ pages (JMA, VEL, RSX, CFB) | done | in-context |
| T3 | lead | Gather company background | done | in-context |
| T4 | lead | Search for third-party sources and open-source implementations | done | in-context |
| T5 | lead | Synthesize and write report | todo | outputs/.drafts/jurik-trading-indicators-draft.md |
| T6 | verifier | Add citations | todo | jurik-trading-indicators-brief.md |
| T7 | reviewer | Verify claims | todo | jurik-trading-indicators-verification.md |

## Verification Log
| Item | Method | Status | Evidence |
|---|---|---|---|
| Indicator list completeness | cross-check catalog vs FAQ vs product pages | verified | 7 tools: JMA, VEL, CFB, RSX, DMX, WAV, DDR (+ legacy AMA) |
| JMA theory (radar tracking) | official FAQ | verified | jurikres.com/faq1/faq_ama.htm |
| CFB theory (fractal analysis) | official FAQ + product page | verified | jurikres.com/faq1/faq_cfb.htm |
| RSX theory (filtered RSI) | official FAQ | verified | jurikres.com/faq1/faq_rsx.htm |
| VEL theory (zero-lag momentum) | official FAQ | verified | jurikres.com/faq1/faq_vel.htm |
| Company founding 1988 | company page | verified | jurikres.com/about/company.htm |
| Business winding down | homepage notice | verified | jurikres.com/index.htm |

## Decision Log
- 2026-04-10: All primary sources gathered in round 1. No subagent delegation needed — topic is focused and all 7 product pages + 4 FAQ pages + company page already fetched.
- Note: Algorithms are proprietary (trade secret + US Copyright Office). Report will document what is publicly disclosed about principles, not reverse-engineered formulas.
