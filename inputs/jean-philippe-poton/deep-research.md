# Arnaud Legoux — Research Brief

## Biography

Arnaud Legoux is a French quantitative analyst and indicator developer based in Paris, France. He co-created the ALMA (Arnaud Legoux Moving Average) with Dimitrios (Dimitris) Kouzis-Loukas around 2009. Legoux maintained a personal website at arnaudlegoux.com (archived 2006–2024) where he published the indicator, provided free downloads (NinjaTrader version), and discussed its mathematical foundations.

**Key facts:**
- Based in Paris, 75003, France
- Co-author with Dimitris Kouzis-Loukas
- Active in trading indicator development from at least 2009
- Published ALMA implementations for NinjaTrader, MQL4, MQL5, and TradeStation
- Website copyright dated 2009
- No known TASC (Stocks & Commodities) publications — the indicator was introduced via his personal website and trading forums rather than through traditional print media

## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| ALMA (Arnaud Legoux Moving Average) | 2009, arnaudlegoux.com | Adaptive MA |

### ALMA — Technical Description

The ALMA applies a Gaussian (normal distribution) window to price data with an adjustable offset parameter, allowing the user to control the trade-off between smoothness and responsiveness.

**Formula:**

```
ALMA(i) = Σ [w(j) * Price(i-j)] / Σ w(j)

where w(j) = exp(-(j - m)² / (2 * s²))
      m = offset * (window - 1)
      s = window / sigma
```

**Default parameters:**
- `window` = 9 (lookback period)
- `offset` = 0.85 (0 to 1; controls position of Gaussian bell on the window)
- `sigma` = 6 (controls width of the Gaussian bell)

**Key properties:**
- Offset = 0.5 centers the Gaussian (maximum smoothing, like a Gaussian filter)
- Offset = 1.0 places the Gaussian at the most recent bar (maximum responsiveness, minimal lag)
- Offset = 0.85 (default) provides a good balance — responsive yet smooth
- Sigma controls the shape: lower sigma = narrower bell = fewer bars contribute significantly

## Books

No known books published by Arnaud Legoux.

## TASC Publications (Complete List)

**No articles found.** The TASC author archive for Arnaud Legoux returns zero results. ALMA was not introduced through Stocks & Commodities magazine — it was published on the author's personal website (arnaudlegoux.com) and disseminated through trading forums (NinjaTrader Forum, Big Mike Trading).

## Articles by Category

| Category | Count | Articles |
|----------|-------|----------|
| N/A | 0 | No TASC publications found |

## MQL5 Implementations

| Title | Author | Platform | Type | URL |
|-------|--------|----------|------|-----|
| ALMA (Arnaud Legoux Moving Average) | Igor Durkin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/1175 |
| ALMA with addition filters | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/16517 |
| ALMA 2.0 | Mladen Rakic | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/16847 |
| Institutional Gaussian Signal Filter (Zero-Lag ALMA) | Amanda V. De Paula Pereira | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/71322 |
| Moving Averages-14 different types | Yashar Seyyedin | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/48058 |
| Moving Averages-14 different types | Yashar Seyyedin | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/48621 |
| AllAverages v4.9 MT5 | Ivan Astafurov | MetaTrader 5 | Indicator | https://www.mql5.com/en/code/46041 |
| AllAverages v4.9 | Ivan Astafurov | MetaTrader 4 | Indicator | https://www.mql5.com/en/code/43879 |

## Community & Reference Implementations

| Platform/Library | Status | Reference |
|-----------------|--------|-----------|
| TradingView Pine Script | Built-in function `ta.alma()` | Native support |
| pandas-ta (Python) | Included as `alma` | https://github.com/twopirllc/pandas-ta |
| NinjaTrader | Original free release by author | arnaudlegoux.com (archived) |
| TradeStation | Released by author | arnaudlegoux.com (archived) |
| MQL4/MQL5 | Multiple implementations | See table above |

## BibTeX

```bibtex
@misc{legoux2009alma,
  author       = {Legoux, Arnaud and Kouzis-Loukas, Dimitris},
  title        = {{ALMA}: {A}rnaud {L}egoux {M}oving {A}verage},
  year         = {2009},
  howpublished = {Personal website},
  url          = {https://web.archive.org/web/20110210200040/http://www.arnaudlegoux.com/},
  note         = {Accessed via Wayback Machine; original site active 2006--2024}
}

@misc{durkin2012alma_mql5,
  author       = {Durkin, Igor},
  title        = {{ALMA} ({A}rnaud {L}egoux {M}oving {A}verage) -- {MT5} Implementation},
  year         = {2012},
  url          = {https://www.mql5.com/en/code/1175},
  note         = {MQL5 Code Base}
}
```

## Sources

[1] Wayback Machine archive of arnaudlegoux.com (captured 2011-02-10): https://web.archive.org/web/20110210200040/http://www.arnaudlegoux.com/
[2] TASC Author Archive — Arnaud Legoux (no results): http://technical.traders.com/archive/combo/display5.asp?author=Arnaud%20Legoux
[3] MQL5 Code Base search for "ALMA Arnaud Legoux": https://www.mql5.com/en/code/1175
[4] MQL5 Code Base search for "ALMA": https://search.mql5.com/api/query?keyword=ALMA&module=mql5.com.en.codebase
[5] TradingView Pine Script Reference — ta.alma(): https://www.tradingview.com/pine-script-reference/v5/#fun_ta.alma
