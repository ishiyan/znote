# William Blau's Indicator Ecosystem: Influence, Adoption, and Derivatives

## 1. Blau's Original Publications (TASC)

William Blau published four foundational articles in *Technical Analysis of Stocks & Commodities*:

| Date | Title | Key Contribution |
|------|-------|-----------------|
| Nov 1991 (V9 C11) | True Strength Index | TSI — double-smoothed momentum normalized by absolute momentum |
| Jan 1992 (V9 C01) | Double Smoothed-Stochastics | DSS — applying double EMA smoothing to the stochastic oscillator |
| May 1992 (V9 C05) | Double-Smoothed Momenta | Generalizing double-smoothing to various momentum measures |
| Jan 1993 (V11 C01) | Stochastic Momentum | SMI — measuring distance from midpoint of HL range rather than from low |

His 1995 book *Momentum, Direction, and Divergence* (Wiley, ISBN 978-0-471-02729-4) consolidated and extended these ideas.

## 2. The Core Innovation: Double Smoothing

Blau's fundamental insight was applying **two successive exponential moving averages** to momentum data before normalization. This produces indicators that are:
- Smoother than single-smoothed equivalents (less noise)
- Still responsive to genuine momentum shifts
- Bounded between +100 and −100 (for TSI and SMI)

The formula for TSI:
```
TSI = 100 × EMA(EMA(momentum, r), s) / EMA(EMA(|momentum|, r), s)
```
Default parameters: r=25, s=13.

## 3. Relationship to Prior Work

### TSI vs. Welles Wilder's RSI (1978)
Both normalize momentum into a bounded oscillator. Key differences:
- **RSI** separates momentum into "up" and "down" components, averages them separately, then forms a ratio
- **TSI** keeps momentum intact (positive and negative together), applies double smoothing, then normalizes by the double-smoothed absolute momentum
- TSI preserves directional information more naturally; RSI's segregation of up/down moves is mathematically arbitrary (Blau explicitly criticizes this in his 1993 article)
- TSI is smoother due to double EMA; standard RSI uses a single Wilder smoothing (equivalent to EMA with α=1/n)

### SMI vs. George Lane's Stochastic Oscillator (1950s)
- Lane's %K = (Close − Lowest Low) / (Highest High − Lowest Low) × 100
- Blau's SMI = (Close − Midpoint of HL range) / (Half the HL range) × 100, then double-smoothed
- By measuring distance from **midpoint** rather than from the low, SMI centers at zero and gives equal weight to overbought/oversold conditions
- Double smoothing removes the erratic behavior of raw stochastics

### Tushar Chande — Contemporary Parallel Work
Chande published "The Midpoint Oscillator" in the **same November 1991 TASC issue** (V9 C11) as Blau's TSI. Chande's later "Stochastic RSI" (V11 C05, with Stanley Kroll) applied stochastic normalization to RSI values. Both Chande and Blau were working on the problem of improving momentum oscillators simultaneously, but with different approaches:
- Blau: double smoothing + preserving signed momentum
- Chande: adaptive lookback periods (Variable Index Dynamic Average, CMO) and recursive normalization (StochRSI)

No direct citation of Blau by Chande or vice versa is evident in the TASC index, suggesting parallel independent development.

### John Ehlers and DSP Perspective
Ehlers has not published a TASC article directly referencing Blau's double smoothing. However, Ehlers' extensive work on digital signal processing filters (low-pass, band-pass, Laguerre, super-smoothers) addresses the same fundamental problem from a more rigorous engineering perspective. Double EMA smoothing is, in DSP terms, a cascade of two first-order IIR low-pass filters — Ehlers would characterize this as choosing a specific frequency response without explicit attention to phase delay or spectral properties. Ehlers' "Ultimate Smoother" (2024) and super-smoother filters are the DSP-informed successors to Blau's empirical approach.

## 4. Walter Bressert's DSS vs. Blau's DSS

Walter Bressert popularized a "Double Smoothed Stochastic" (DSS) that is **related but distinct** from Blau's version:
- **Blau's DSS**: Double-smooth the raw stochastic calculation components (numerator and denominator separately), then form the ratio
- **Bressert's DSS**: Compute a standard stochastic %K, then apply an EMA to get a smoothed stochastic, then apply stochastic normalization *again* to that smoothed line, and smooth once more — effectively a "stochastic of a stochastic" with intermediate smoothing

Bressert's version appeared in his cycle-trading work and was co-developed with Doug Schaff (who later created the Schaff Trend Cycle, which also uses double stochastic logic). Bressert published in TASC (V17 C05–C06, 1999) on cycle-based trading but those articles focus on the Euro, not DSS methodology directly.

The two DSS variants share the name and the idea of repeated smoothing of stochastic data, but differ in implementation. Most modern platform implementations labeled "DSS" follow Bressert's recursive-stochastic approach rather than Blau's double-EMA-of-components approach.

## 5. Adoption in Trading Platforms and Libraries

### TradingView (Built-in)
TSI is a standard built-in indicator in TradingView's Pine Script library. Their documentation describes it as a "momentum oscillator designed to detect, confirm or visualize the strength of a trend." Signal line (7-period EMA of TSI) is standard. TSI has been available since TradingView's early indicator set.

### pandas-ta (Python)
The pandas-ta library (4000+ GitHub stars) includes TSI in its momentum category. Implementation follows Blau's original formula with configurable fast/slow periods.

### TA-Lib
TA-Lib (the C-based technical analysis library used across multiple languages) does **not** include TSI in its standard function list. This is notable — TA-Lib's function set was largely frozen in the early 2000s and reflects the Wilder/Lane/Appel era indicators.

### MetaTrader 4/5
TSI is not built-in to MT4/MT5 by default but is widely available as a custom indicator. Multiple MQL4/MQL5 implementations exist on the MQL5 marketplace.

### Other Platforms
- **ThinkOrSwim (TDAmeritrade)**: TSI built-in
- **NinjaTrader**: TSI built-in
- **TradeStation**: TSI available (referenced in Tom Hartle's 2002 *Active Trader* article with TradeStation code)

## 6. Secondary Literature and Citations

### Authors Who Wrote About TSI
- **Tom Hartle** (Jan 2002, *Active Trader*): "The True Strength Index" — practical guide with TradeStation implementation
- **Mark Etzkorn** (1997, *Trading with Oscillators*, Wiley): pp. 91–93 devoted to TSI analysis
- **Michael C. Thomsett** (2009, *The Options Trading Body of Knowledge*, FT Press): references TSI on p. 268

### TASC Sidebar Coverage
TASC published calculation sidebars alongside Blau's articles:
- "SIDEBAR: CALCULATING TSI" (V9 C11)
- "SIDEBAR: Calculating TrSI" (V10 C05) — accompanying a follow-up "Trading With The True Strength Index" article

## 7. Later Derivatives and Modifications

### "Improved TSI" Variants
No single "Improved TSI" has become canonical, but common modifications include:
- Using different smoothing methods (DEMA, TEMA, Hull MA) instead of standard EMA
- Adaptive-period TSI where r and s adjust based on volatility
- TSI with volume weighting (volume-weighted momentum as input)

### Schaff Trend Cycle (STC)
Doug Schaff (Bressert's collaborator) created the STC, which applies double stochastic normalization to MACD — conceptually combining Blau's double-smoothing philosophy with Appel's MACD. This became fairly popular in forex trading.

### Ergodic Indicators
Some platforms label variants of Blau's indicators as "Ergodic" oscillators (e.g., the "True Strength Index" is sometimes called the "Ergodic TSI"). This terminology appears in Blau's own book where he discusses the ergodic properties of his smoothed oscillators.

## 8. Adoption Timeline

| Period | Milestone |
|--------|-----------|
| 1991 | TSI published in TASC (November issue) |
| 1992 | Double-Smoothed Stochastics and SMI published |
| 1993 | Stochastic Momentum article; wider awareness |
| 1995 | *Momentum, Direction, and Divergence* book consolidates the work |
| 1997 | Etzkorn's *Trading with Oscillators* includes TSI chapter |
| 2002 | Hartle's *Active Trader* article with TradeStation code |
| ~2005–2010 | TSI appears as built-in indicator on NinjaTrader, ThinkOrSwim |
| ~2012 | TradingView includes TSI as built-in indicator |
| ~2018–2020 | Python TA libraries (pandas-ta, ta) add TSI |
| Present | TSI is standard on all major charting platforms; SMI less universally adopted |

## 9. Summary of Influence

William Blau's contribution was **methodological** rather than just creating a single indicator. His key insight — that double exponential smoothing of momentum components before normalization produces superior oscillators — influenced:

1. **Direct implementations**: TSI is now a standard platform indicator alongside RSI, MACD, and Stochastics
2. **Conceptual descendants**: Schaff Trend Cycle, various "ergodic" oscillators, Bressert's DSS
3. **The smoothing paradigm**: His work validated the idea of cascaded smoothing in technical analysis, paving the way for Patrick Mulloy's DEMA/TEMA (also 1990s TASC) and anticipating Ehlers' more rigorous filter-design approach

Blau occupies an interesting position: more mathematically rigorous than the 1970s–80s indicator creators (Wilder, Lane, Appel) but less formally grounded in DSP theory than Ehlers. His indicators solved real problems (noise, whipsaw, arbitrary up/down separation) and achieved broad platform adoption, though Blau himself remains less famous than the names his work improved upon.
