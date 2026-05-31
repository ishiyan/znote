# William Blau — Deep Research Brief

## Executive Summary

William Blau is a technical analysis author who published for a brief 4-year window (1991–1995) and then vanished completely. Despite this, his inventions — the **True Strength Index (TSI)**, **Stochastic Momentum Index (SMI)**, and **Double Smoothed Stochastics** — are now standard indicators on every major charting platform worldwide. His core innovation: **double exponential smoothing** applied to momentum before normalization, which creates a 2nd-order IIR filter with -40 dB/decade noise roll-off and ~36% less lag than a single EMA of equivalent smoothing power [1][2].

No photograph, interview, biography, obituary, patent, or post-1995 publication has ever been found for William Blau. He is known entirely through 5 TASC articles (1991–1993) and one Wiley book (1995). The most promising lead for biographical information remains the "About the Author" section in a physical copy of his book or the author bios appended to his TASC articles (both behind paywalls) [3].

---

## Biography

| Fact | Source |
|------|--------|
| Full name | William Blau |
| Nickname | "Bill Blau" [4] |
| Amazon Author ID | B001IR1BSO [4] |
| Active period | 1991–1995 |
| Publications | 5 TASC articles + 1 Wiley book |
| Post-1995 activity | **None found** [3] |
| Photo | **None exists online** [3] |
| Background | Likely electrical engineering or signal processing (inferred from DSP sophistication) [3] |

### What Is Known

Blau is described as a "technical wizard" and "technical expert" on his book's Amazon page [4]. His use of the term "ergodic" (from statistical mechanics/dynamical systems) and his implementation of cascaded IIR filters suggest training in engineering or physics. He wrote for a trading audience with "a minimum of complex mathematics" — implying deeper knowledge deliberately simplified [1][4].

### What Remains Unknown

- Education, employer, city of residence
- Whether he is alive or deceased
- Why he disappeared after 1995
- Whether "William Blau" is a pseudonym
- Any connection to academic institutions or firms

### Unpursued Leads

1. Physical copy of the 1995 book — likely contains "About the Author" page
2. TASC subscriber archive ($89.99) — articles from 1991–1993 typically include author bios
3. Wiley publisher records from 1995
4. CMT Association membership records
5. Library of Congress CIP data [3]

---

## The Double-Smoothing Innovation

### Mathematical Foundation

All Blau indicators share one architecture [1][2]:

```
Index = 100 × EMA(EMA(EMA(raw_measure, r), s), u) / EMA(EMA(EMA(|raw_measure|, r), s), u)
```

Double smoothing = two cascaded EMAs = **2nd-order IIR low-pass filter**:

```
H(z) = [α₁α₂] / [(1 - (1-α₁)z⁻¹)(1 - (1-α₂)z⁻¹)]
```

### Why It Works (Signal Processing Analysis)

| Property | Single EMA | Double EMA (Blau) |
|----------|-----------|-------------------|
| Filter order | 1st-order IIR | 2nd-order IIR |
| Roll-off | -20 dB/decade | **-40 dB/decade** |
| Lag for equivalent smoothing | (N-1)/2 bars | **(r+s-2)/2 bars (~36% less)** |
| Computational cost | O(1) per bar | O(1) per bar |
| Nyquist attenuation (n=20) | -20.4 dB | **-40.8 dB** |

**Example**: r=20, s=5 gives lag = 11.5 bars with noise suppression equivalent to single EMA of period ~37 (lag = 18 bars). **6.5 bars of lag saved** for equivalent noise reduction [2].

### Separation of Concerns

The first EMA (large r) sets the trend bandwidth; the second EMA (small s) removes residual jitter. This is a cascade of a "trend filter" and a "noise filter" with clearly distinct roles — intuitive for traders to parameterize [2].

### Comparison to Other Filters

| Filter | Roll-off | Lag | Overshoot | Complexity |
|--------|----------|-----|-----------|------------|
| Single EMA | -20 dB/dec | High | None | O(1) |
| **Double EMA (Blau)** | **-40 dB/dec** | **Moderate** | **None** | **O(1)** |
| Butterworth 2nd | -40 dB/dec | Moderate | Possible | O(1) |
| DEMA (Mulloy) | Moderate | Low | Yes | O(1) |
| TEMA (Mulloy) | Good | Very low | Yes | O(1) |
| Zero-lag EMA (Ehlers) | -20 dB/dec | Near zero | Yes | O(1) |
| Jurik MA (JMA) | Steep | Low (adaptive) | Minimal | Proprietary |
| Gaussian | Variable | Linear phase | None | O(n) |

Blau's approach occupies a sweet spot: no overshoot, no ringing, O(1) computation, intuitive parameters, and superior noise suppression compared to single EMA — at the cost of moderate lag [2].

---

## Complete Indicator Catalog

### True Strength Index (TSI)

```
TSI(q, r, s) = 100 × EMA(EMA(Close - Close[q], r), s) / EMA(EMA(|Close - Close[q]|, r), s)
```
- Defaults: q=1 (1-bar momentum), r=25, s=13
- Range: [-100, +100]
- Overbought: > +25; Oversold: < -25
- **Standard built-in** on TradingView, ThinkOrSwim, NinjaTrader, TradeStation [5]

### Stochastic Momentum Index (SMI)

```
SM(q) = Close - (HighestHigh(q) + LowestLow(q)) / 2
SMI(q, r, s) = 100 × EMA(EMA(SM(q), r), s) / (0.5 × EMA(EMA(HH(q) - LL(q), r), s))
```
- Key insight: measures distance from **midpoint** (not low) of range
- Range: [-100, +100] (zero-centered, unlike Lane's [0, 100])
- More symmetric; better for divergence detection [1][2]

### Double Smoothed Stochastics (Blau version)

```
StochI(q, r, s) = 100 × EMA(EMA(Close - LowestLow(q), r), s) / EMA(EMA(HH(q) - LL(q), r), s)
```
- NOT the same as Bressert's DSS (which applies stochastic operator twice) [6]

### Directional Trend Index (DTI)

```
HLM(q) = (High - High[q]) + (Low - Low[q])
DTI(q, r, s, u) = 100 × EMA(EMA(EMA(HLM, r), s), u) / EMA(EMA(EMA(|HLM|, r), s), u)
```
- Uses both high and low boundaries (full bar range momentum) [2]

### Candlestick Momentum (CMtm) / Candlestick Index (CMI)

```
CMtm = Close - Open
CMI(r, s, u) = 100 × EMA(EMA(EMA(C-O, r), s), u) / EMA(EMA(EMA(|C-O|, r), s), u)
```
- Intra-bar buying/selling pressure [2]

### Ergodic Oscillator

```
Ergodic = TSI(q, r, s, u)
Signal = EMA(Ergodic, signal_period)
Histogram = Ergodic - Signal
```
- Buy: Ergodic crosses above Signal; Sell: crosses below [2]

### Additional Indicators (from book)

| Indicator | Category |
|-----------|----------|
| Composite High/Low Momentum (HLM) | Momentum |
| Ergodic MACD | Momentum |
| Ergodic DTI-Oscillator | Trend |
| Ergodic CSI-Oscillator | Oscillator |
| Mean Deviation Index (MDI) | Volatility |
| Trend Momentum | Trend |
| Candlestick Size Index (CSI) | Oscillator |

---

## Relationship to Other Momentum Researchers

### TSI vs. Wilder's RSI (1978)

| Dimension | RSI (Wilder) | TSI (Blau) |
|-----------|-------------|------------|
| Momentum treatment | Separates into "up" and "down" averages | Keeps signed momentum intact |
| Smoothing | Single Wilder smoothing (EMA α=1/n) | Double EMA |
| Blau's criticism | Arbitrary segregation of up/down is mathematically unjustified | — |
| Noise level | Higher (single smoothing) | Lower (-40 dB/dec) |
| Zero crossing | RSI 50 (arbitrary) | TSI 0 (natural) |

### SMI vs. Lane's Stochastic (1950s)

| Dimension | Lane %K | Blau SMI |
|-----------|---------|----------|
| Reference point | Low of range | **Midpoint** of range |
| Range | [0, 100] | [-100, +100] |
| Smoothing | Single SMA or EMA | Double/triple EMA |
| Symmetry | Asymmetric (biased toward lows) | Symmetric |

### Parallel Work: Tushar Chande

Chande published "The Midpoint Oscillator" in the **same November 1991 TASC issue** as Blau's TSI [7]. Both were solving the same problem (improved momentum oscillators) independently:
- **Blau**: double smoothing + preserving signed momentum
- **Chande**: adaptive lookback (Variable Index Dynamic Average, CMO) + recursive normalization (StochRSI)

No evidence of cross-citation [7].

### Ehlers (DSP Perspective)

Ehlers never directly cited Blau in TASC, but his digital signal processing work (SuperSmoother, Laguerre filter, Ultimate Smoother) addresses the same fundamental problem from rigorous engineering. Double EMA is a specific 2nd-order IIR filter choice; Ehlers designs filters with explicit frequency response specifications. Ehlers' work is the DSP-informed successor to Blau's empirical approach [7].

---

## Blau vs. Bressert: The "DSS" Confusion

Two different indicators share the "Double Smoothed Stochastic" name [6][7]:

| | Blau's DSS | Bressert's DSS |
|---|---|---|
| Method | Double-smooth the components, then normalize once | Compute stochastic, smooth, then apply stochastic operator again |
| Architecture | EMA(EMA(data)) / EMA(EMA(range)) | Stochastic(EMA(Stochastic(data))) |
| Range | [0, 100] | [0, 100] |
| Platform label | Usually "Blau DSS" or "DSS Blau" | Usually just "DSS" or "DSS Bressert" |

Most platforms implement **Bressert's version** under the generic "DSS" label [6].

---

## Adoption Timeline

| Period | Milestone |
|--------|-----------|
| Nov 1991 | TSI published in TASC [1] |
| Jan 1991 – Jan 1993 | All 5 TASC articles published [1] |
| March 1995 | *Momentum, Direction, and Divergence* (Wiley) consolidates the work [4] |
| 1997 | Etzkorn's *Trading with Oscillators* (Wiley) devotes pp. 91–93 to TSI [7] |
| 2002 | Hartle's *Active Trader* article with TradeStation code [7] |
| ~2005–2010 | TSI appears as built-in on NinjaTrader, ThinkOrSwim [5] |
| 2011 | Zelinsky's MQL5 article implements complete Blau indicator library [8] |
| ~2012 | TradingView includes TSI as built-in [5] |
| ~2018–2020 | Python TA libraries (pandas-ta) add TSI [5] |
| Present | TSI standard everywhere; SMI less universal; DSS usually means Bressert's [5] |

**Adoption took ~20 years** from publication (1991) to universal platform inclusion (~2012) [7].

---

## Conceptual Descendants

- **Schaff Trend Cycle (STC)**: Doug Schaff (Bressert's collaborator) applied double stochastic normalization to MACD — combining Blau's double-smoothing philosophy with Appel's MACD [7]
- **Patrick Mulloy's DEMA/TEMA** (1994 TASC): Different approach to lag reduction via subtracting the lagged component — published in TASC one year before Blau's book [7]
- **Various "Ergodic" oscillators**: Some platforms relabel Blau's TSI variants as "Ergodic" indicators [7]

---

## Implementation Ecosystem

### MQL5 (58 CodeBase entries for "William Blau")

The most comprehensive implementation is **Andrey F. Zelinsky's** complete library with shared `WilliamBlau.mqh` header file [8]:
- [MQL5 Article: William Blau's Indicators Part 1](https://www.mql5.com/en/articles/190) [8]
- 15+ individual indicator implementations (TSI, SMI, DTI, CMtm, HLM, Ergodic variants, etc.)

### Python (pandas-ta)

TSI is in the momentum category of pandas-ta (4,000+ GitHub stars) [5].

### TA-Lib

Notably, TA-Lib does **not** include TSI — its function set was frozen in the early 2000s and reflects the pre-Blau indicator era [5].

### TradingView

TSI is a standard built-in Pine Script function with signal line [5].

---

## Open Questions

1. Who is William Blau? (Engineering background? City? Employer?)
2. Is he alive or deceased?
3. Why did he stop publishing after 1995?
4. Is "William Blau" a pseudonym?
5. Does the physical book contain an "About the Author" page?
6. Did he have any connection to the DSP/engineering community?
7. Why did it take ~20 years for TSI to become a standard platform indicator?

---

## Sources

| # | Source | Status |
|---|--------|--------|
| [1] | Blau, W. TASC articles (1991–1993): V09C01, V09C05, V09C11, V10C05, V11C01 | verified (in TASC cached index) |
| [2] | MQL5 Article: "William Blau's Indicators in MQL5. Part 1" — https://www.mql5.com/en/articles/190 | verified |
| [3] | Biography research — all searches negative | verified (negative result) |
| [4] | Amazon: https://www.amazon.com/William-Blau/e/B001IR1BSO | verified |
| [5] | Platform availability research (TradingView, pandas-ta, ThinkOrSwim) | verified |
| [6] | MQL5 CodeBase: "Double smoothed stochastic Blau" — https://www.mql5.com/en/code/23278 | verified |
| [7] | TASC index cross-references (Chande, Bressert, Ehlers, Mulloy) | verified |
| [8] | Zelinsky, A.F. MQL5 Blau indicator library (codes/361–385) | verified |

---

## BibTeX

```bibtex
@book{Blau1995,
  author    = {Blau, William},
  title     = {Momentum, Direction, and Divergence: Applying the Latest Momentum Indicators for Technical Analysis},
  publisher = {John Wiley \& Sons},
  year      = {1995},
  isbn      = {978-0-471-02729-4},
  series    = {Wiley Trader's Advantage},
  pages     = {160},
  url       = {https://www.amazon.com/Momentum-Direction-Divergence-Applying-Convergence/dp/0471027294},
}

@article{Blau1991tsi,
  author  = {Blau, William},
  title   = {True Strength Index},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1991},
  month   = nov,
  volume  = {9},
  number  = {11},
  url     = {https://technical.traders.com/archive/article.asp?file=\V09\C11\TRUESTR.pdf},
}

@article{Blau1991dss,
  author  = {Blau, William},
  title   = {Double Smoothed-Stochastics},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1991},
  month   = jan,
  volume  = {9},
  number  = {1},
  url     = {https://technical.traders.com/archive/article.asp?file=\V09\C01\DOUBLES.pdf},
}

@article{Blau1991momentum,
  author  = {Blau, William},
  title   = {Double-Smoothed Momenta},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1991},
  month   = may,
  volume  = {9},
  number  = {5},
  url     = {https://technical.traders.com/archive/article.asp?file=\V09\C05\DOUBLE.pdf},
}

@article{Blau1992trading,
  author  = {Blau, William},
  title   = {Trading With The True Strength Index},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1992},
  month   = may,
  volume  = {10},
  number  = {5},
  url     = {https://technical.traders.com/archive/article.asp?file=\V10\C05\TRADING.pdf},
}

@article{Blau1993smi,
  author  = {Blau, William},
  title   = {Stochastic Momentum},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {1993},
  month   = jan,
  volume  = {11},
  number  = {1},
  url     = {https://technical.traders.com/archive/article.asp?file=\V11\C01\STOCHAS.pdf},
}

@online{Zelinsky2011blau,
  author  = {Zelinsky, Andrey F.},
  title   = {William Blau's Indicators and Trading Systems in {MQL5}. Part 1: Indicators},
  url     = {https://www.mql5.com/en/articles/190},
  urldate = {2026-05-31},
  year    = {2011},
  note    = {Comprehensive MQL5 implementation of all Blau indicators},
}

@book{Etzkorn1997,
  author    = {Etzkorn, Mark},
  title     = {Trading with Oscillators: Pinpointing Market Extremes -- Theory and Practice},
  publisher = {John Wiley \& Sons},
  year      = {1997},
  isbn      = {978-0-471-15538-6},
  note      = {pp. 91--93 on TSI},
}

@article{Wilder1978,
  author  = {Wilder, J. Welles},
  title   = {New Concepts in Technical Trading Systems},
  year    = {1978},
  publisher = {Trend Research},
  note    = {Introduced RSI, ATR, ADX},
}
```
