# Vladimir Kravchuk — Research Brief

**Date:** 2026-05-07  
**Subject:** Vladimir Kravchuk (Владимир Кравчук), DSP-based trading system developer

---

## Biography

Vladimir Kravchuk is a Russian/Ukrainian digital signal processing specialist who developed the **Adaptive Trend & Cycles Following (AT&CF)** method for financial markets. He published his work in the Russian-language magazine *"Currency Speculator" (Валютный спекулянт)* during 2001–2002, under a series titled "New Adaptive Method of Following the Tendency and Market Cycles."

He is associated with **Finware.ru Ltd.**, a Russian trading technology entity credited on MetaTrader 4 implementations of his indicators. He also has a recognized author page on the *Stocks & Commodities (TASC)* website, suggesting at least one English-language publication.

No academic affiliation, photo, or direct online presence has been identified. His work survives primarily through third-party implementations on the MQL5/MQL4 codebase and a comprehensive 2017 article by Dmitriy Gizlyk.

**Key facts:**
- **Nationality:** Russian or Ukrainian (Eastern Slavic)
- **Active period:** 2001–2002 (original publications)
- **Association:** Finware.ru Ltd.
- **No connection** to Mykhailo Kravchuk (1892–1942) or Krawtchouk polynomials — the shared surname is coincidental.

---

## Technical Indicators & Tools

### Core Indicators (AT&CF Method)

| Indicator | Full Name | Category |
|-----------|-----------|----------|
| FATL | Fast Adaptive Trend Line | Filter (LPF-1 output) |
| SATL | Slow Adaptive Trend Line | Filter (LPF-2 output) |
| RFTL | Reference Fast Trend Line | Filter (LPF-1 + Nyquist delay) |
| RSTL | Reference Slow Trend Line | Filter (LPF-2 + Nyquist delay) |
| FTLM | Fast Trend Line Momentum | Oscillator (FATL − RFTL) |
| STLM | Slow Trend Line Momentum | Oscillator (SATL − RSTL) |
| RBCI | Range Bound Channel Index | Oscillator (FATL − SATL) |
| PCCI | Perfect Commodity Channel Index | Oscillator (Close − FATL) |

These eight indicators form a **coordinated set** — they are not independent tools but outputs of a unified filter bank designed for a specific instrument's spectral characteristics.

### AT&CF Method — Technical Description

The AT&CF method applies **Finite Impulse Response (FIR) digital filters** to financial price data. Unlike generic moving averages, the filter coefficients are custom-designed per instrument using:

- **Spectral estimation** via the Maximum Entropy Method (MEM) / parametric power spectral density (PSD) estimation to identify dominant market cycles and frequencies
- **Blackman window function** for sidelobe attenuation in the filter design
- **≥40 dB stop-band attenuation** ensuring strong suppression of unwanted frequencies
- **Zero phase distortion** in the passband — no lag relative to the true trend component

The filters are **non-recursive** (FIR), meaning they have guaranteed stability and linear phase response. This is a critical distinction from IIR-based indicators (like exponential moving averages) which introduce phase delay.

> "The main objective of the AT&CF method is creation of the minimum number of technical tools possessing set properties. There must be enough of these tools to build a trading algorithm that would provide maximum possible profitability, while possessing the least possible risk level, for some definite market."

### Filter Design Process

1. **Spectral analysis** of price data using the Maximum Entropy Method (parametric PSD)
2. **Identify dominant cycles/frequencies** in the instrument's price series
3. **Design FIR filter coefficients** with specific passband/stopband cutoff frequencies
4. **Apply Blackman window** to the ideal filter impulse response for sidelobe attenuation (≥40 dB)
5. **Result:** A coordinated filter bank producing:
   - FATL/SATL for trend estimation (two timescales)
   - RFTL/RSTL as reference lines (delayed versions)
   - FTLM/STLM for momentum (difference between current and reference)
   - RBCI for range/cycle detection (bandpass output)
   - PCCI for high-frequency residual

### Filter Architecture Diagram

```
Price Data ──┬── LPF-1 ──────────── FATL (fast trend)
             │       └── delay ──── RFTL (reference fast)
             │                         FTLM = FATL − RFTL
             │
             ├── LPF-2 ──────────── SATL (slow trend)
             │       └── delay ──── RSTL (reference slow)
             │                         STLM = SATL − RSTL
             │
             │   RBCI = FATL − SATL (bandpass)
             └── PCCI = Close − FATL (high-frequency residual)
```

### How It Differs from Moving Averages

- FATL/SATL are **not** moving averages — they are adaptive trend line estimates with designed frequency response
- Unlike MAs, they have **no phase delay** in the passband (zero-phase filtering)
- Provide significantly better noise suppression than equivalent-length simple/exponential MAs
- FTLM/STLM are smoother than classic Momentum because they operate on filtered (not raw) prices
- The entire system is **instrument-specific** — coefficients change per market based on spectral analysis

---

## Books

No known books attributed to Vladimir Kravchuk.

---

## Original Publications

### Currency Speculator (Валютный спекулянт), 2001–2002

| # | Title (reconstructed) | Date | Notes |
|---|----------------------|------|-------|
| 1 | New Adaptive Method of Following the Tendency and Market Cycles (series) | 2001–2002 | Russian-language; original publication of AT&CF method |

The original article series in *Валютный спекулянт* is consistently cited across all MQL5 codebase entries as the foundational reference. Individual issue numbers are not available from public sources. The magazine was a well-known Russian trading publication of the early 2000s.

---

## TASC Publications

Vladimir Kravchuk has a confirmed author page on the Stocks & Commodities archive:  
`https://technical.traders.com/archive/combo/display5.asp?author=Vladimir%20Kravchuk`

Article listing requires subscriber access. No articles were found in the TASC XML archives for 2004–2010, suggesting his contribution(s) may predate 2004 or appeared in a different section.

| # | Title | Issue | PDF Link |
|---|-------|-------|----------|
| — | *Article listing unavailable without TASC subscriber access* | Unknown | [PDF path not found] |

---

## Articles by Category

### Digital Signal Processing / Filter Design
- "New Adaptive Method of Following the Tendency and Market Cycles" — *Currency Speculator*, 2001–2002

### Third-Party Analysis
- "Practical evaluation of the adaptive market following method" — Dmitriy Gizlyk, MQL5 Articles, 2017

---

## Photos, Videos & Interviews

| Type | Status |
|------|--------|
| Photo | [URL not found] |
| Video | [URL not found] |
| Interview | [URL not found] |
| Conference appearance | [URL not found] |

No public photos, videos, or interviews have been located for Vladimir Kravchuk.

---

## MQL5 Implementations

### Indicators (Real Author: Vladimir Kravchuk)

| Title | Uploader | Platform | Type | URL |
|-------|----------|----------|------|-----|
| FATL — Fast Adaptive Trend Line | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/403 |
| SATL — Slow Adaptive Trend Line | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/404 |
| RFTL — Reference Fast Trend Line | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/405 |
| RSTL — Reference Slow Trend Line | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/406 |
| FTLM-STLM | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/407 |
| RBCI — Range Bound Channel Index | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/408 |
| PCCI — Perfect Commodity Channel Index | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/409 |
| AT_CF — Combined (all four filters) | Nikolay Kositsin | MT5 | Indicator | https://www.mql5.com/en/code/456 |
| FTLM_hist | Scriptor / Finware.ru | MT4 | Indicator | https://www.mql5.com/en/code/7206 |
| FTLM_STLM | Scriptor / Finware.ru | MT4 | Indicator | https://www.mql5.com/en/code/7282 |

### Comprehensive Article Implementation

| Title | Author | Year | Type | URL |
|-------|--------|------|------|-----|
| Practical evaluation of the adaptive market following method | Dmitriy Gizlyk (DNG) | 2017 | Article + EA Signal Module | https://www.mql5.com/en/articles/3456 |

This article provides a full implementation of the AT&CF method as an MQL5 Wizard signal module, including spectral analysis, filter coefficient calculation, and 8 trading patterns derived from the indicator set.

---

## Community & Reference Implementations

| Source | Notes |
|--------|-------|
| **Finware.ru Ltd.** | Credited on MQL4 implementations; likely a commercial entity associated with Kravchuk or his method |
| **MQL5 Code Base** | Primary repository of implementations (10 entries) |
| **TradingView** | No scripts found |
| **NinjaTrader / MultiCharts** | Not confirmed |

---

## Key People

| Person | Role | Platform |
|--------|------|----------|
| **Nikolay Kositsin** (GODZILLA) | Primary MT5 implementer of all 8 indicators | MQL5 |
| **Dmitriy Gizlyk** (DNG) | Wrote comprehensive 2017 implementation article | MQL5 |
| **Scriptor** | MT4 indicator uploads | MQL4/MQL5 |
| **Finware.ru Ltd.** | Commercial entity, MT4 indicator credits | MQL4 |

---

## BibTeX

```bibtex
@article{kravchuk2001atcf,
  author       = {Kravchuk, Vladimir},
  title        = {New Adaptive Method of Following the Tendency and Market Cycles},
  journal      = {Currency Speculator (Валютный спекулянт)},
  year         = {2001--2002},
  note         = {Russian-language series; original publication of AT\&CF method},
  language     = {russian}
}

@article{gizlyk2017atcf,
  author       = {Gizlyk, Dmitriy},
  title        = {Practical evaluation of the adaptive market following method},
  year         = {2017},
  url          = {https://www.mql5.com/en/articles/3456},
  note         = {Full MQL5 implementation of Kravchuk's AT\&CF trading system}
}

@online{kositsin_fatl,
  author       = {Kositsin, Nikolay},
  title        = {FATL --- Fast Adaptive Trend Line},
  year         = {2010},
  url          = {https://www.mql5.com/en/code/403},
  note         = {Real author: Vladimir Kravchuk}
}

@online{kositsin_satl,
  author       = {Kositsin, Nikolay},
  title        = {SATL --- Slow Adaptive Trend Line},
  year         = {2010},
  url          = {https://www.mql5.com/en/code/404},
  note         = {Real author: Vladimir Kravchuk}
}

@online{kositsin_rftl,
  author       = {Kositsin, Nikolay},
  title        = {RFTL --- Reference Fast Trend Line},
  year         = {2010},
  url          = {https://www.mql5.com/en/code/405},
  note         = {Real author: Vladimir Kravchuk}
}

@online{kositsin_rstl,
  author       = {Kositsin, Nikolay},
  title        = {RSTL --- Reference Slow Trend Line},
  year         = {2010},
  url          = {https://www.mql5.com/en/code/406},
  note         = {Real author: Vladimir Kravchuk}
}

@online{kositsin_ftlm_stlm,
  author       = {Kositsin, Nikolay},
  title        = {FTLM-STLM},
  year         = {2010},
  url          = {https://www.mql5.com/en/code/407},
  note         = {Real author: Vladimir Kravchuk}
}

@online{kositsin_rbci,
  author       = {Kositsin, Nikolay},
  title        = {RBCI --- Range Bound Channel Index},
  year         = {2010},
  url          = {https://www.mql5.com/en/code/408},
  note         = {Real author: Vladimir Kravchuk}
}

@online{kositsin_pcci,
  author       = {Kositsin, Nikolay},
  title        = {PCCI --- Perfect Commodity Channel Index},
  year         = {2010},
  url          = {https://www.mql5.com/en/code/409},
  note         = {Real author: Vladimir Kravchuk}
}

@online{kositsin_atcf,
  author       = {Kositsin, Nikolay},
  title        = {AT\_CF --- Combined Indicator},
  year         = {2010},
  url          = {https://www.mql5.com/en/code/456},
  note         = {Real author: Vladimir Kravchuk}
}

@online{finware_ftlm_hist,
  author       = {Scriptor and Finware.ru Ltd.},
  title        = {FTLM\_hist},
  url          = {https://www.mql5.com/en/code/7206},
  note         = {Real author: Vladimir Kravchuk; MT4 platform}
}

@online{finware_ftlm_stlm,
  author       = {Scriptor and Finware.ru Ltd.},
  title        = {FTLM\_STLM},
  url          = {https://www.mql5.com/en/code/7282},
  note         = {Real author: Vladimir Kravchuk; MT4 platform}
}
```

---

## Sources

[1] MQL5 Code Base — FATL indicator page, https://www.mql5.com/en/code/403  
[2] MQL5 Code Base — SATL indicator page, https://www.mql5.com/en/code/404  
[3] MQL5 Code Base — RFTL indicator page, https://www.mql5.com/en/code/405  
[4] MQL5 Code Base — RSTL indicator page, https://www.mql5.com/en/code/406  
[5] MQL5 Code Base — FTLM-STLM indicator page, https://www.mql5.com/en/code/407  
[6] MQL5 Code Base — RBCI indicator page, https://www.mql5.com/en/code/408  
[7] MQL5 Code Base — PCCI indicator page, https://www.mql5.com/en/code/409  
[8] MQL5 Code Base — AT_CF combined indicator, https://www.mql5.com/en/code/456  
[9] MQL5 Code Base — FTLM_hist (MT4), https://www.mql5.com/en/code/7206  
[10] MQL5 Code Base — FTLM_STLM (MT4), https://www.mql5.com/en/code/7282  
[11] Gizlyk, D. (2017). "Practical evaluation of the adaptive market following method," MQL5 Articles, https://www.mql5.com/en/articles/3456  
[12] TASC Author Archive — Vladimir Kravchuk, https://technical.traders.com/archive/combo/display5.asp?author=Vladimir%20Kravchuk  
