# Vladimir Kravchuk — Research Brief (Direct Evidence)

**Date:** 2026-05-07  
**Status:** Exploratory — strong MQL5/codebase evidence; TASC page exists but article listing not extractable without subscriber access.

---

## 1. TASC (Stocks & Commodities) Author Archive

The TASC website has a dedicated author page at:  
`https://technical.traders.com/archive/combo/display5.asp?author=Vladimir%20Kravchuk`

The page title confirms **"VLADIMIR KRAVCHUK"** as a recognized author. However, the actual article listing requires subscriber login to view. The page structure exists but no article titles were extractable from the public HTML.

**TASC XML Scan (2004–2010):** No matches found for "Kravchuk" in any of the monthly XML files scanned. This suggests either his articles predate 2004, appeared in a different section, or the XML files don't cover his contributions.

**Key finding from MQL5 sources:** According to the MQL5 article by Dmitriy Gizlyk, Kravchuk's trading system was **"first described by Vladimir Kravchuk in the 'Currency speculator' magazine in 2001–2002."** This is a Russian-language publication ("Валютный спекулянт"), not TASC directly. His work may have been later translated/republished in TASC.

---

## 2. MQL5/MQL4 Codebase Results (PRIMARY SOURCE)

### Total results: 10 codebase entries + 1 dedicated article

This is the richest source of information. Vladimir Kravchuk is credited as the **"Real author"** on numerous digital filter indicators uploaded by **Nikolay Kositsin** (login: GODZILLA) to MQL5, and by **Scriptor** and **Finware.ru Ltd.** to MQL4.

### Indicators Attributed to Vladimir Kravchuk:

| Indicator | Full Name | Platform | URL |
|-----------|-----------|----------|-----|
| **FATL** | Fast Adaptive Trend Line | MT5 | https://www.mql5.com/en/code/403 |
| **SATL** | Slow Adaptive Trend Line | MT5 | https://www.mql5.com/en/code/404 |
| **RFTL** | Reference Fast Trend Line | MT5 | https://www.mql5.com/en/code/405 |
| **RSTL** | Reference Slow Trend Line | MT5 | https://www.mql5.com/en/code/406 |
| **FTLM-STLM** | Fast/Slow Trend Line Momentum | MT5 | https://www.mql5.com/en/code/407 |
| **RBCI** | Range Bound Channel Index | MT5 | https://www.mql5.com/en/code/408 |
| **PCCI** | Perfect Commodity Channel Index | MT5 | https://www.mql5.com/en/code/409 |
| **AT_CF** | All four filters combined | MT5 | https://www.mql5.com/en/code/456 |
| **FTLM_hist** | FTLM histogram | MT4 | https://www.mql5.com/en/code/7206 |
| **FTLM_STLM** | FTLM/STLM combined | MT4 | https://www.mql5.com/en/code/7282 |

### MQL5 Article (Detailed Implementation):

- **Title:** "Practical evaluation of the adaptive market following method"
- **Author:** Dmitriy Gizlyk (2017)
- **URL:** https://www.mql5.com/en/articles/3456
- **Content:** Full implementation of Kravchuk's AT&CF method as an MQL5 Expert Advisor signal module, including spectral analysis, filter coefficient calculation, and 8 trading patterns.

---

## 3. The AT&CF Method — Core Technical Description

Vladimir Kravchuk developed the **"Adaptive Trend & Cycles Following" (AT&CF)** method. Key characteristics:

### Theoretical Foundation:
- Based on **digital signal processing (DSP)** applied to financial time series
- Uses **spectral estimation** (maximum entropy method / parametric PSD estimation) to determine filter parameters
- Employs **non-recursive digital low-pass filters** (FIR filters) with Blackman window function
- Filters provide **≥40 dB attenuation** in stop band with zero phase distortion in passband
- Filter coefficients are **adaptively calculated** per-instrument based on its spectral density

### Design Philosophy:
> "The main objective of the AT&CF method is creation of the minimum number of technical tools possessing set properties. There must be enough of these tools to build a trading algorithm that would provide maximum possible profitability, while possessing the least possible risk level, for some definite market."

### How It Differs from Moving Averages:
- FATL/SATL are **not** moving averages — they are adaptive trend line estimates
- Unlike MA, they have **no phase delay** relative to current prices in the passband
- They provide significantly better noise suppression than simple MAs
- FTLM/STLM are smoother than classic Momentum because they use filtered (not raw) prices

### Filter Architecture:
- **LPF-1** (Low-Pass Filter 1) → produces FATL (fast adaptive trend)
- **LPF-2** (Low-Pass Filter 2) → produces SATL (slow adaptive trend)  
- **RFTL/RSTL** = same filters with Nyquist-interval delay (reference lines)
- **FTLM** = FATL − RFTL (fast momentum)
- **STLM** = SATL − RSTL (slow momentum)
- **RBCI** = FATL − SATL (channel/bandpass filter output)
- **PCCI** = Close − FATL (high-frequency residual, analogous to CCI)

---

## 4. Biographical Information

### What is confirmed:
- **Name:** Vladimir Kravchuk (Владимир Кравчук)
- **Active period:** 2001–2002 (original publications)
- **Publication venue:** "Currency Speculator" (Валютный спекулянт) magazine — a Russian-language trading publication
- **TASC connection:** Has an author page on Stocks & Commodities website (suggesting at least one English-language article)
- **Company connection:** Finware.ru Ltd. is credited on some MQL4 implementations, suggesting a possible commercial entity
- **Nationality:** Almost certainly Russian or Ukrainian (published in Russian-language magazine, name is Eastern Slavic)

### What is NOT confirmed:
- No MQL5 user profile found directly for Vladimir Kravchuk
- No academic institution identified
- No connection to Krawtchouk (Kravchuk) polynomials established — this appears to be a coincidence of surname (the polynomials are named after Ukrainian mathematician Mykhailo Kravchuk, 1892–1942)
- No photo or video found

---

## 5. Forum Search Results

| Forum | Result |
|-------|--------|
| TradingView | **No scripts found** (search returned empty) |
| ForexFactory | Not searchable via Google (blocked) |
| futures.io | Not searchable via Google (blocked) |
| elitetrader.com | Not searchable via Google (blocked) |
| mql5.com/en/forum | Likely has threads (given codebase presence) |
| Others | Google searches blocked/inaccessible |

---

## 6. Key Relationships & People

- **Nikolay Kositsin** (MQL5 login: GODZILLA) — Primary implementer of Kravchuk's indicators for MetaTrader 5. Uploaded FATL, SATL, RFTL, RSTL, FTLM-STLM, RBCI, PCCI, and AT_CF.
- **Dmitriy Gizlyk** (MQL5 login: DNG) — Wrote the comprehensive 2017 article implementing the full AT&CF trading system as an MQL5 Wizard signal module.
- **Finware.ru Ltd.** — Credited as author on some MQL4 indicator implementations.
- **Scriptor** — Uploaded MT4 versions of FTLM indicators.

---

## 7. Russian-Language Sources

The original publication was in **"Валютный спекулянт" (Currency Speculator)** magazine, 2001–2002. This was a well-known Russian trading publication. The article/series was titled something equivalent to **"New Adaptive Method of Following the Tendency and Market Cycles"** (as consistently referenced across all MQL5 codebase entries).

Google searches in Cyrillic were blocked by Google's bot detection.

---

## 8. Connection to Krawtchouk Polynomials

**No connection established.** The Krawtchouk polynomials (discrete orthogonal polynomials) are a mathematical concept named after Mykhailo Kravchuk (1892–1942), a Ukrainian mathematician. Vladimir Kravchuk's trading indicators use a completely different mathematical approach:
- His method is based on FIR digital filters with spectral estimation
- Uses Blackman window function for filter design
- Employs maximum entropy method for spectral density estimation
- No polynomial smoothing involved

The shared surname appears coincidental.

---

## Summary Statistics

| Category | Count/Status |
|----------|-------------|
| TASC articles | ≥1 (author page exists, count unknown without subscriber access) |
| MQL5 codebase entries | **10** (as "Real author") |
| MQL5 articles about his method | **1** (Gizlyk 2017, comprehensive) |
| Named indicators | **8** (FATL, SATL, RFTL, RSTL, FTLM, STLM, RBCI, PCCI) |
| Original publication | "Currency Speculator" magazine, 2001–2002 (Russian) |
| TradingView scripts | 0 |
| Forum threads confirmed | Not determinable (Google blocked) |
| Photos/videos | None found |
| Academic affiliation | Unknown |
| MQL5 user profile | Not found (others uploaded his work) |
