# Jack Hutson & TRIX Indicator — Implementations Research

**Date:** 2026-05-07

## Background

Jack K. Hutson developed the TRIX (Triple Exponential Average) indicator in the early 1980s. He was an editor for *Technical Analysis of Stocks & Commodities* magazine. The original article was published in July 1983: "Good TRIX" (*Stocks & Commodities*, July 1983).

TRIX is a momentum oscillator that displays the percent rate of change of a triple exponentially smoothed moving average (TEMA). It uses a logarithm of price in the original formulation (often omitted in modern implementations).

---

## 1. GitHub Repositories Implementing TRIX

### Dedicated / Prominent TRIX Implementations

| Repository | Language | Stars | URL |
|---|---|---|---|
| anilca/NetTrader.Indicator | C# | 142 | https://github.com/anilca/NetTrader.Indicator |
| mpquant/Python-Financial-Technical-Indicators-Pandas | Python | 78 | https://github.com/mpquant/Python-Financial-Technical-Indicators-Pandas |
| Alex5574/Trix | (unknown) | 0 | https://github.com/Alex5574/Trix |
| stpaulchuck/Forex-Indicator-Data-Generators | C# | 3 | https://github.com/stpaulchuck/Forex-Indicator-Data-Generators |
| kunogi/fin-calc | TypeScript | 8 | https://github.com/kunogi/fin-calc |
| quantiacs/strategy-predict-NASDAQ100-use-trix-ema | Jupyter Notebook | 0 | https://github.com/quantiacs/strategy-predict-NASDAQ100-use-trix-ema |
| coolshou/ta-lib | C | 0 | https://github.com/coolshou/ta-lib |
| datxsoft/trader | PHP | 6 | https://github.com/datxsoft/trader |

### Major Libraries That Include TRIX

| Library | Language | Stars | URL |
|---|---|---|---|
| TA-Lib (original C library) | C | — | https://ta-lib.org/ |
| pandas-ta | Python | ~5,000+ | https://github.com/twopirllc/pandas-ta |
| peerchemist/finta | Python | 2,252 | https://github.com/peerchemist/finta |
| anandanand84/technicalindicators | JavaScript/TypeScript | 2,431 | https://github.com/anandanand84/technicalindicators |
| DaveSkender/Stock.Indicators | C# | 1,198 | https://github.com/DaveSkender/Stock.Indicators |
| andredumas/techan.js | JavaScript (D3) | 2,437 | https://github.com/andredumas/techan.js |

### Python Libraries with TRIX

- **TA-Lib Python wrapper** (`talib.TRIX`): https://github.com/TA-Lib/ta-lib-python
- **pandas-ta** (`pandas_ta.momentum.trix`): https://github.com/twopirllc/pandas-ta
- **finta** (`TA.TRIX`): https://github.com/peerchemist/finta
- **ta** (by bukosabino): https://github.com/bukosabino/ta — includes TRIXIndicator class

---

## 2. TradingView Pine Script Implementations

Source: https://www.tradingview.com/scripts/trix/

### Notable Scripts

| Script | Author | Likes | URL |
|---|---|---|---|
| TRIX (canonical implementation) | everget | 1,200+ | https://www.tradingview.com/script/NTAdUxle-TRIX/ |
| TRIX Histogram R1-12 | JustUncleL | 3,200+ | https://www.tradingview.com/script/zR5M5N6O-TRIX-Histogram-R1-12-by-JustUncleL/ |
| TRIX ribbon w/ Up/Down colours | squattter | 372 | https://www.tradingview.com/script/f3pR53ol-TRIX-ribbon-w-Up-Down-colours-squattter/ |
| PA-Adaptive TRIX Log | loxx | 80 | https://www.tradingview.com/script/rnd8QdKc-PA-Adaptive-TRIX-Log-Loxx/ |
| Jurik Filter TRIX Log | loxx | 75 | https://www.tradingview.com/script/lc8wDLQW-Jurik-Filter-TRIX-Log-Loxx/ |
| TRIX with Colour Change | garrick.wynne | 544 | https://www.tradingview.com/script/oGKqxc12-TRIX-with-Colour-Change/ |
| TRIX with Momentum | c00l75 | 93 | https://www.tradingview.com/script/cW5jhwgW/ |
| Edo TRIX Core Cross | EdoLab-Markets | 4 | https://www.tradingview.com/script/jQ0npfNo-Edo-TRIX-Core-Cross/ |
| Alpha TRIX Strategy | BVL-Crypto | 29 | https://www.tradingview.com/script/1BJZkv2N-Alpha-TRIX-Strategy/ |
| Colored Trix with spike detection | Theterran | 19 | https://www.tradingview.com/script/psclOqyD-Colored-Trix-with-spike-detection/ |
| TRIX RSI (TRSI) | imal_max | 166 | https://www.tradingview.com/script/tehxoJsx-TRIX-RSI-Tripple-Exponetial-Relative-Strength-TRSI/ |
| Volume Weighted ALMA TRIX | rumpypumpydumpy | 139 | https://www.tradingview.com/script/nGYvv11R-Volume-Weighted-ALMA-TRIX/ |

**Key quote from PA-Adaptive TRIX Log description:**
> "TRIX is a momentum oscillator that displays the percent rate of change of a TEMA. It was developed in the early 1980's by Jack Hutson, an editor for 'Technical Analysis of Stocks and Commodities' magazine."

---

## 3. MQL4/MQL5 Implementations

TRIX is available in the MQL5 CodeBase. Search results at:
- https://www.mql5.com/en/search#!keyword=TRIX&module=mql5_module_codebase

Known implementations:
- **Built-in TRIX indicator** in MetaTrader 5 (included in standard indicators)
- Various custom TRIX EAs and indicators available in the MQL5 CodeBase and Market

[UNVERIFIED] Specific MQL5 CodeBase entries — the search page did not return individual results in fetched content. Manual browsing at https://www.mql5.com/en/code would reveal specific implementations.

---

## 4. Python Libraries That Include TRIX

| Library | Function/Class | PyPI Package | URL |
|---|---|---|---|
| TA-Lib | `talib.TRIX(close, timeperiod=30)` | `TA-Lib` | https://ta-lib.github.io/ta-lib-python/ |
| pandas-ta | `df.ta.trix(length=18)` | `pandas-ta` | https://github.com/twopirllc/pandas-ta |
| ta (bukosabino) | `ta.trend.TRIXIndicator` | `ta` | https://github.com/bukosabino/ta |
| finta | `TA.TRIX(df)` | `finta` | https://github.com/peerchemist/finta |
| tulipy | `tulipy.trix(close, period)` | `tulipy` | https://github.com/jesse-ai/tulipy |
| bta-lib | `bta-lib` includes TRIX | `bta-lib` | https://github.com/mementum/bta-lib |

---

## 5. Video Interviews, Podcasts, and Conference Talks

### [UNVERIFIED] — No confirmed video/audio media found

Jack Hutson was the **publisher and editor** of *Technical Analysis of Stocks & Commodities* (TASC) magazine, not primarily a public speaker or media personality. Research yielded:

- **No YouTube interviews** found specifically featuring Jack Hutson speaking on camera.
- **No podcast episodes** identified with Jack Hutson as guest.
- **No conference talk recordings** located.

He is known primarily through his written work:
- "Good TRIX" — *Technical Analysis of Stocks & Commodities*, July 1983
- Various editorial contributions to TASC magazine throughout the 1980s-1990s

[UNVERIFIED] It is possible that TASC magazine events or early technical analysis conferences may have featured Hutson, but no recordings appear to be publicly available online.

---

## 6. Photos of Jack Hutson

[UNVERIFIED] — No publicly accessible photographs of Jack Hutson were confirmed through this research. He maintained a relatively low public profile compared to other technical analysis figures. Possible sources:

- Historical issues of *Technical Analysis of Stocks & Commodities* magazine (print archives)
- [UNVERIFIED] The TASC magazine website (https://www.traders.com) may contain editorial staff photos in older issues

---

## Summary

Jack Hutson's TRIX indicator has been widely implemented across virtually every technical analysis platform and library. It is a standard indicator in:
- TA-Lib (the de facto standard C library for technical analysis)
- All major Python TA libraries (pandas-ta, ta, finta, tulipy)
- TradingView (built-in + 100+ community scripts)
- MetaTrader 4/5 (standard indicator)
- .NET libraries (Stock.Indicators, NetTrader.Indicator)
- JavaScript libraries (technicalindicators, techan.js)

Despite the indicator's ubiquity, Jack Hutson himself remains a relatively obscure figure with no confirmed video appearances, interviews, or publicly available photographs online.
