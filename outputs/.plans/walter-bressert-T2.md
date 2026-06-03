# T2 Brief: DSS Provenance — Blau vs. Bressert

Write findings to `outputs/.drafts/walter-bressert-research-dss.md`.

## Goal
Resolve, or fairly characterize, the question: **who originated the "Double Smoothed Stochastic" (DSS)?** It is commonly co-attributed to William Blau and Walter Bressert. Establish the documentary timeline and explain the co-attribution.

## Key documentary facts to establish (with citations)
1. **William Blau's record**: Blau published "Double Smoothed-Stochastics" in TASC **January 1991** (\V09\C01\DOUBLES) and "Stochastic Momentum" Jan 1993, and his book *Momentum, Direction, and Divergence* (Wiley, 1995). His double-smoothing concept = apply two cascaded EMAs to the stochastic numerator and denominator separately. Confirm dates/titles (see local trading-research/william-blau.md as a starting reference).
2. **Bressert's record**: Bressert's *The Blue Book* (1981, with an Overbought/Oversold Index + Momentum Index) and *The Power of Oscillator/Cycle Combinations* (1991). Did Bressert publish a "double smoothed stochastic" formula, and when? The MQL5/tradesignalonline "DSS:Bressert" formula uses EMA-smoothing of a stochastic-of-a-stochastic / EMA-ratio. Find the earliest dateable Bressert DSS source.
3. **Are the two formulas the same or different?** Characterize: Blau's double-smoothed stochastics vs. the popular "DSS Bressert" formula. Practitioners often note TWO distinct formulations. Document the difference precisely if sources allow.

## Where to look
- TASC archive references for Blau (Jan 1991 is the key early date).
- ProRealCode "DSS Bressert" page: https://www.prorealcode.com/prorealtime-indicators/dss-bressert-double-smoothed-stochastic/ (often states the attribution/formula).
- TradingView script descriptions (HPotter's "DSS Bressert"), LizardIndicators, tradesignalonline DSS:Bressert.
- Forum debates on provenance: ForexFactory, futures.io, NinjaTrader threads (search "DSS Bressert Blau origin").
- Any statement by Bressert himself claiming the indicator.

## Analytical task
- Build a **timeline table**: year | who | what was published | source URL.
- Give a reasoned **verdict**: Is the priority Blau (1991 TASC publication is concrete and early)? Is "DSS Bressert" a later popularization/variant? Or did Bressert have an earlier (1981/1991 book) but less-formally-published version? Be explicit about what is documented vs. folklore. It is acceptable to conclude "co-attribution reflects two related but distinct formulations" if that's what evidence shows.

## Deliverable
Markdown: "Timeline" table, "The two formulations" section, "Verdict / what the record supports" section, "Confidence & gaps". Inline source URLs. Do not overstate — distinguish documented publication dates from popular attribution. Search engines may be blocked; use Brave/Startpage/Mojeek/Wayback and direct fetches.