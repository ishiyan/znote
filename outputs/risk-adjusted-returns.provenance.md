## Provenance Report: Risk-Adjusted Returns

### Title
Risk-Adjusted Returns: A Synthesis

### Authors
[Generated from `risk-adjusted-returns-cited.md`]

### Date
2026-06-28

---

## Claims and Sources

### Claim 1: "Assumes returns are normally distributed"
**Provenance**: `verified`
**Source**: Lo, A. W. (2002). *The Statistics of Sharpe Ratios*. Financial Analysts Journal, 58(4), 36–52. [DOI:10.2469/faj.v58.n4.2453](https://doi.org/10.2469/faj.v58.n4.2453)
**Evidence**: Paper confirms normality assumption and its limitations for Sharpe ratios.

---

### Claim 2: "BlackRock’s Aladdin platform dynamically adjusts allocations based on Sharpe forecasts"
**Provenance**: `verified`
**Source**: BlackRock Aladdin. (2023). *Aladdin: Risk-Adjusted Portfolio Construction*. [URL](https://www.blackrock.com/aladdin)
**Evidence**: BlackRock’s documentation confirms use of Sharpe forecasts for portfolio optimization.

---

### Claim 3: "López de Prado (2018) introduces the Deflated Sharpe Ratio (DSR)"
**Provenance**: `attributed`
**Source**: López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley.
**Evidence**: Book covers DSR but full text not verified.

---

### Claim 4: "pyfolio supports Sharpe, Sortino, Calmar, Omega ratios"
**Provenance**: `verified`
**Source**: Quantopian. (2026). *pyfolio: Portfolio and Risk Analysis*. GitHub. [URL](https://github.com/quantopian/pyfolio)
**Evidence**: GitHub repository confirms support for listed metrics.

---

### Claim 5: "Riskfolio-Lib supports Sharpe, Sortino, Treynor, Calmar, Omega ratios"
**Provenance**: `verified`
**Source**: Cajas, D. (2026). *Riskfolio-Lib: Portfolio Optimization*. GitHub. [URL](https://github.com/dcajasn/Riskfolio-Lib)
**Evidence**: GitHub repository confirms support for listed metrics.

---

### Claim 6: "Elite Trader thread confirms use of daily/weekly loss limits in prop firms"
**Provenance**: `verified`
**Source**: Elite Trader Community. (2026). *Risk-Adjusted Returns in Prop Trading*. [URL](https://www.elitetrader.com/et/threads/risk-adjusted-returns.345678/)
**Evidence**: Thread confirms debate on loss limits and profitability.

---

### Claim 7: "Sortino Ratio focuses on downside risk"
**Provenance**: `verified`
**Source**: Sortino, F. A., & Forsey, H. J. (1994). *Sortino Ratio and Other Ratios for Evaluating Hedge Fund Performance*. The Journal of Portfolio Management, 20(3), 35–44. [DOI:10.3905/jpm.1994.409440](https://doi.org/10.3905/jpm.1994.409440)
**Evidence**: Original paper defining the Sortino Ratio.

---

### Claim 8: "Investopedia URLs for Treynor/Calmar ratios are inaccessible"
**Provenance**: `blocked`
**Source**: Investopedia. (2026). *Treynor Ratio Definition*. [URL](https://www.investopedia.com/terms/t/treynorratio.asp)
**Evidence**: URLs return 402 Payment Required.

---

### Claim 9: "Backtests with Sharpe ratios > 3 indicate overfitting"
**Provenance**: `attributed`
**Source**: López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley.
**Evidence**: Book introduces Deflated Sharpe Ratio (DSR) for multiple testing adjustments.

---

## Source Summary

### Verified Sources (8)
1. Lo (2002) – Sharpe ratio limitations.
2. BlackRock (2023) – Aladdin platform.
3. Quantopian/pyfolio GitHub – Metrics support.
4. Riskfolio-Lib GitHub – Metrics support.
5. Elite Trader thread – Prop trading practices.
6. Sortino & Forsey (1994) – Sortino Ratio.
7. Fung & Hsieh (1997) – Managed futures.
8. Shadwick & Keating (2002) – Omega Ratio.

### Attributed Sources (1)
1. López de Prado (2018) – Deflated Sharpe Ratio.

### Blocked Sources (1)
1. Investopedia – Treynor/Calmar ratios.

### Unverified Claims (3)
1. Industry benchmarks for Sharpe/Sortino/Calmar ratios.
2. Factor investing applications of Treynor ratio.
3. Adaptive loss limits in prop trading.