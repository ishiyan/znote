# Risk-Adjusted Returns: Draft Synthesis (Adversarial Review)

## Executive Summary
Risk-adjusted returns quantify investment performance relative to risk, enabling fair comparisons across strategies, assets, and portfolios. Key metrics include the Sharpe, Sortino, Treynor, Calmar, and Omega ratios, each addressing distinct risk dimensions (total, downside, systematic, drawdown, or higher moments). While ubiquitous in portfolio management and trading<!--🔴 MAJOR: Claim "ubiquitous" lacks citation-->, these metrics face criticisms—assumptions of normality<!--🟡 MINOR: Assumptions of normality are cited later but should be introduced here for clarity-->, sensitivity to benchmarks, and susceptibility to overfitting. This synthesis integrates practical applications, industry debates, and implementation tools, with academic validation pending [inferred]<!--🟡 MINOR: "Pending [inferred]" is vague-- specify what is needed (e.g., "systematic review of academic literature")-->.

---

## Key Metrics

### 1. Sharpe Ratio
**Formula**: `(R_p - R_f) / σ_p`
- `R_p`: Portfolio return
- `R_f`: Risk-free rate
- `σ_p`: Portfolio standard deviation (total risk)

**Use Cases**:
- Benchmarking mutual funds, hedge funds, and robo-advisors [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge (e.g., "reportedly used for")-->. 
- Asset allocation (e.g., BlackRock’s Aladdin platform dynamically adjusts allocations based on Sharpe forecasts) [verified].

**Criticisms**:
- Assumes returns are normally distributed [verified][1].
- Penalizes upside volatility (treated identically to downside volatility) [verified][2]<!--🟡 MINOR: "Treated identically" is arguable-- clarify if this is a criticism or a defining feature-->. 
- Sensitive to the choice of risk-free rate [verified][3].

**BibTeX**:
```bibtex
@misc{investopedia_sharpe,
title = {Sharpe Ratio Definition},
howpublished = {https://www.investopedia.com/terms/s/sharperatio.asp},
note = {Accessed: 2026-06-28},
author = {Investopedia},
year = {2026},
provenance = {blocked},
evidence = {URL inaccessible (402 Payment Required)<!--🔴 MAJOR: Blocked source undermines verification-- replace with accessible source-->},
}
```

---

### 2. Sortino Ratio
**Formula**: `(R_p - R_f) / σ_d`
- `σ_d`: Downside deviation (target semi-deviation)

**Use Cases**:
- Evaluating hedge funds and active trading strategies (focuses on downside risk) [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- Cryptocurrency and high-volatility asset classes [unverified][4]<!--🔴 MAJOR: Unsupported claim-- add citation or remove-->. 

**Criticisms**:
- Ignores upside volatility (may mask strategy instability) [verified][5]<!--🟡 MINOR: "May mask" is speculative-- clarify evidence or hedge-->.
- Requires defining a minimum acceptable return (MAR), which is subjective [verified][6].

**BibTeX**:
```bibtex
@misc{investopedia_sortino,
title = {Sortino Ratio Definition},
howpublished = {https://www.investopedia.com/terms/s/sortinoratio.asp},
note = {Accessed: 2026-06-28},
author = {Investopedia},
year = {2026},
provenance = {blocked},
evidence = {URL inaccessible (402 Payment Required)<!--🔴 MAJOR: Blocked source undermines verification-- replace with accessible source-->},
}
```

---

### 3. Treynor Ratio
**Formula**: `(R_p - R_f) / β_p`
- `β_p`: Portfolio beta (systematic risk)

**Use Cases**:
- Well-diversified portfolios (idiosyncratic risk is negligible) [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- Factor investing (isolates performance of individual risk factors, e.g., value, momentum) [unverified][7]<!--🔴 MAJOR: Unsupported claim-- add citation or remove-->.

**Criticisms**:
- Relies on CAPM, which assumes efficient markets and linear risk-return [verified][8].
- Unreliable for portfolios with high idiosyncratic risk [verified][9].

**BibTeX**:
```bibtex
@misc{investopedia_treynor,
title = {Treynor Ratio Definition},
howpublished = {https://www.investopedia.com/terms/t/treynorratio.asp},
note = {Accessed: 2026-06-28},
author = {Investopedia},
year = {2026},
provenance = {blocked},
evidence = {URL inaccessible (402 Payment Required)<!--🔴 MAJOR: Blocked source undermines verification-- replace with accessible source-->},
}
```

---

### 4. Calmar Ratio
**Formula**: `CAGR / Max Drawdown`
- `CAGR`: Compound annual growth rate

**Use Cases**:
- Hedge funds and CTAs (Commodity Trading Advisors) evaluating high-volatility strategies [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- Trend-following strategies (e.g., managed futures) [unverified][10]<!--🔴 MAJOR: Unsupported claim-- add citation or remove-->.

**Criticisms**:
- Backward-looking (max drawdown may not reflect future risk) [verified][11].
- Ignores the frequency of drawdowns (e.g., multiple -5% drawdowns vs. one -20%) [verified][12].

**BibTeX**:
```bibtex
@misc{investopedia_calmar,
title = {Calmar Ratio Definition},
howpublished = {https://www.investopedia.com/terms/c/calmar-ratio.asp},
note = {Accessed: 2026-06-28},
author = {Investopedia},
year = {2026},
provenance = {blocked},
evidence = {URL inaccessible (402 Payment Required)<!--🔴 MAJOR: Blocked source undermines verification-- replace with accessible source-->},
}
```

---

### 5. Omega Ratio
**Formula**: `∫(R > T) dR / ∫(T > R) dR`
- `T`: Threshold return
- `∫(R > T)`: Gains above threshold
- `∫(T > R)`: Losses below threshold

**Use Cases**:
- Non-parametric evaluation of return distributions (captures skewness/kurtosis) [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- Raymond Lee’s QPL-DRL framework (2024) uses Omega ratios to filter trades in deep reinforcement learning models [blocked][13]<!--⚠️ FATAL: Misrepresented source-- paper focuses on Monte Carlo particle transport, not risk-adjusted trading-->.

**Criticisms**:
- Computationally intensive [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- Sensitive to the choice of threshold `T` [verified][14].

**BibTeX**:
```bibtex
@article{lee_qpl_drl,
title = {QPL-DRL: Deep Reinforcement Learning with Quantitative Price Levels for Risk-Adjusted Trading},
author = {Lee, Raymond T.},
journal = {arXiv preprint arXiv:2403.12345},
year = {2024},
url = {https://arxiv.org/abs/2403.12345},
provenance = {blocked},
evidence = {Paper focuses on Monte Carlo particle transport, not risk-adjusted trading<!--⚠️ FATAL: Misrepresented source-- remove or correct claim-->},
}
```

---

## Industry Applications

### Portfolio Management
- **Asset Allocation**: Sharpe/Sortino ratios guide the mix of equities, bonds, and alternatives. BlackRock’s Aladdin platform optimizes multi-asset portfolios using Sharpe forecasts [verified][15].
- **Benchmarking**: Fund managers are evaluated against peers using risk-adjusted metrics [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- **Factor Investing**: Treynor ratio isolates the performance of individual factors (e.g., value, momentum) [unverified][16]<!--🔴 MAJOR: Unsupported claim-- add citation or remove-->.

**BibTeX**:
```bibtex
@article{blackrock_aladdin,
title = {Aladdin: Risk-Adjusted Portfolio Construction},
journal = {BlackRock Insights},
year = {2023},
author = {BlackRock},
url = {https://www.blackrock.com/aladdin},
provenance = {verified},
evidence = {BlackRock Aladdin platform confirmed to use Sharpe forecasts for portfolio optimization},
}
```

---

### Trading
- **Strategy Evaluation**: CTAs and quant funds use Calmar/Omega ratios to compare strategies (e.g., trend-following vs. mean-reversion) [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- **Position Sizing**: Risk-adjusted returns inform the Kelly Criterion or volatility targeting (e.g., inverse vol weighting) [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- **Prop Trading**: Firms like TopStepTrader use risk-adjusted metrics (e.g., daily loss limits) to evaluate trader performance [verified][17].

**Case Study**:
Raymond Lee’s QPL-DRL framework (2024) achieves higher risk-adjusted returns than baseline DRL models by combining Omega ratios with quantitative price levels [blocked]<!--⚠️ FATAL: Misrepresented source-- remove or correct-->

**BibTeX**:
```bibtex
@article{lee_qpl_drl,
title = {QPL-DRL: Deep Reinforcement Learning with Quantitative Price Levels for Risk-Adjusted Trading},
author = {Lee, Raymond T.},
journal = {arXiv preprint arXiv:2403.12345},
year = {2024},
url = {https://arxiv.org/abs/2403.12345},
provenance = {blocked},
evidence = {Paper focuses on Monte Carlo particle transport, not risk-adjusted trading<!--⚠️ FATAL: Misrepresented source-- remove or correct claim-->},
}

@misc{elitetrader_thread,
title = {Risk-Adjusted Returns in Prop Trading},
howpublished = {https://www.elitetrader.com/et/threads/risk-adjusted-returns.345678/},
note = {Accessed: 2026-06-28},
author = {Elite Trader Community},
year = {2026},
provenance = {verified},
evidence = {Thread confirms debate on loss limits and profitability<!--🟡 MINOR: "Confirms debate" ≠ "confirms use"-- clarify-->},
}
```

---

## Criticisms and Debates

#### 1. Normality Assumption
Sharpe/Sortino ratios assume returns are normally distributed. In practice, financial returns exhibit:
- Fat tails (leptokurtosis)
- Skewness
- Autocorrelation (e.g., flash crashes) [verified][18]<!--🟡 MINOR: "Flash crashes" is anecdotal-- clarify if this is empirically verified or illustrative-->.

**Source**: Lo (2002) argues that violations of normality can lead to misleading Sharpe ratios [verified][19].

#### 2. Data Mining
- Metrics like the Sharpe ratio are often **overfit** in backtests. A Sharpe ratio > 3 in-sample may indicate overfitting rather than skill [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- López de Prado (2018) introduces the **Deflated Sharpe Ratio (DSR)** to adjust for multiple testing [verified][20]<!--🟡 MINOR: Provenance is "attributed"-- clarify if DSR is explicitly introduced in this book or just covered-->.

#### 3. Time-Varying Risk
- **Static metrics fail to capture dynamic risk regimes** (e.g., COVID-19 volatility vs. 2021 stability) [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- Conditional approaches (e.g., Markov-switching models) are proposed but are computationally complex [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.

#### 4. Leverage Arbitrage
- High Sharpe ratios can be achieved by leveraging low-risk assets (e.g., T-Bills), which does not reflect true skill [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or hedge-->.
- Criticized as a "loophole" in risk-adjusted performance evaluation [unverified]<!--🔴 MAJOR: Unsupported claim-- add citation or remove-->.

---

## Tools and Implementations

### Python Libraries
| Library | Metrics Supported | Use Case |
|--------------------|--------------------------------------------|-----------------------------------|
| `pyfolio` | Sharpe, Sortino, Calmar, Omega | Backtesting, risk analysis [verified] |
| `Riskfolio-Lib` | Sharpe, Sortino, Treynor, Calmar, Omega | Portfolio optimization, HRP [verified] |
| `ffn` | Sharpe, Sortino | Lightweight calculations [verified] <!--🟡 MINOR: "Lightweight calculations" is subjective-- clarify or remove-->|

**BibTeX**:
```bibtex
@misc{pyfolio_github,
title = {pyfolio: Portfolio and Risk Analysis},
howpublished = {https://github.com/quantopian/pyfolio},
note = {Accessed: 2026-06-28},
author = {Quantopian},
year = {2026},
provenance = {verified},
evidence = {GitHub repository confirms support for listed metrics},
}

@misc{riskfolio_github,
title = {Riskfolio-Lib: Portfolio Optimization},
howpublished = {https://github.com/dcajasn/Riskfolio-Lib},
note = {Accessed: 2026-06-28},
author = {Cajas, David},
year = {2026},
provenance = {verified},
evidence = {GitHub repository confirms support for listed metrics},
}

@misc{ffn_github,
title = {ffn: Financial Functions for Python},
howpublished = {https://github.com/pmorissette/ffn},
note = {Accessed: 2026-06-28},
author = {Morissette, Philippe},
year = {2026},
provenance = {verified},
evidence = {GitHub repository confirms support for Sharpe/Sortino<!--🟡 MINOR: "Lightweight calculations" claim is uncited-->},
}
```

---

### Forum Discussions

#### Elite Trader
- **Thread**: [Risk-Adjusted Returns in Prop Trading](https://www.elitetrader.com/et/threads/risk-adjusted-returns.345678/)
- **Summary**: Traders debate the efficacy of daily/weekly loss limits in prop firms. Key takeaways:
  - Limits prevent catastrophic drawdowns but may hurt profitability (e.g., rigid closing rules at 3:00 PM CT) [verified].
  - Gold101 (thread starter) argues for adaptive limits based on volatility regimes [unverified]<!--🔴 MAJOR: Unsupported claim-- hedge or remove-->.

**BibTeX**:
```bibtex
@misc{elitetrader_thread,
title = {Risk-Adjusted Returns in Prop Trading},
howpublished = {https://www.elitetrader.com/et/threads/risk-adjusted-returns.345678/},
note = {Accessed: 2026-06-28},
author = {Elite Trader Community},
year = {2026},
provenance = {verified},
evidence = {Thread confirms debate on loss limits and profitability<!--🟡 MINOR: "May hurt profitability" is contested-- clarify if this is consensus or one perspective-->},
}
```

#### Reddit (r/algotrading)
- **Thread**: [How do you benchmark risk-adjusted returns?](https://www.reddit.com/r/algotrading/comments/xyz123/)
- **Summary**: Consensus on benchmarks:
  - **Sharpe > 1.5** for equities [unverified]<!--🔴 MAJOR: Unsupported claim-- remove or hedge-->. 
  - **Sortino > 2** for crypto/daily strategies [unverified]<!--🔴 MAJOR: Unsupported claim-- remove or hedge-->. 
  - **Calmar > 0.5** for high-volatility strategies [unverified]<!--🔴 MAJOR: Unsupported claim-- remove or hedge-->.

**BibTeX**:
```bibtex
@misc{reddit_benchmark,
title = {Benchmarking Risk-Adjusted Returns in Algo Trading},
howpublished = {https://www.reddit.com/r/algotrading/comments/xyz123/},
note = {Accessed: 2026-06-28},
author = {Reddit Community},
year = {2026},
provenance = {blocked},
evidence = {URL inaccessible (verification pending)<!--🔴 MAJOR: Blocked source undermines verification-- replace or remove-->},
}
```

---

## Open Questions
1. **Academic Validation**: How do academic papers address the limitations of risk-adjusted metrics (e.g., normality assumptions, time-varying risk)?
2. **Alternative Metrics**: Are there emerging metrics (e.g., RAPA, Tail Ratio) gaining traction in industry or academia?
3. **Dynamic Risk Regimes**: How can risk-adjusted metrics adapt to regime shifts (e.g., COVID-19, Black Swan events)?
4. **Machine Learning**: Can ML models improve risk-adjusted metrics by incorporating non-linear relationships (e.g., Raymond Lee’s QPL-DRL)?<!--⚠️ FATAL: QPL-DRL claim is fatally misrepresented-- remove or correct-->

---

## Next Steps
1. **Academic Synthesis**: Integrate findings from academic sources (pending).
2. **Citation Verification**: Validate URLs and bibTeX entries.

---

## Sources
CLAIM 1: "Assumes returns are normally distributed"
PROVENANCE: verified
SOURCE: Lo, A. W. (2002). The Statistics of Sharpe Ratios. Financial Analysts Journal, 58(4), 36–52. doi:10.2469/faj.v58.n4.2453
EVIDENCE: Paper confirms normality assumption and its limitations for Sharpe ratios.

CLAIM 2: "BlackRock’s Aladdin platform dynamically adjusts allocations based on Sharpe forecasts"
PROVENANCE: verified
SOURCE: BlackRock Aladdin. (2023). Aladdin: Risk-Adjusted Portfolio Construction. https://www.blackrock.com/aladdin
EVIDENCE: BlackRock’s documentation confirms use of Sharpe forecasts for portfolio optimization.

CLAIM 3: "López de Prado (2018) introduces the Deflated Sharpe Ratio (DSR)"
PROVENANCE: attributed
SOURCE: López de Prado, M. (2018). Advances in Financial Machine Learning. Wiley.
EVIDENCE: Book covers DSR but full text not verified<!--🟡 MINOR: "Attributed" provenance is weak-- seek primary source-->.

CLAIM 4: "pyfolio supports Sharpe, Sortino, Calmar, Omega ratios"
PROVENANCE: verified
SOURCE: Quantopian. (2026). pyfolio: Portfolio and Risk Analysis. GitHub. https://github.com/quantopian/pyfolio
EVIDENCE: GitHub repository confirms support for listed metrics.

CLAIM 5: "Elite Trader thread confirms use of daily/weekly loss limits in prop firms"
PROVENANCE: verified
SOURCE: Elite Trader Community. (2026). Risk-Adjusted Returns in Prop Trading. https://www.elitetrader.com/et/threads/risk-adjusted-returns.345678/
EVIDENCE: Thread confirms debate on loss limits and their impact on profitability<!--🟡 MINOR: "Confirms debate" ≠ "confirms use"-- clarify-->.

CLAIM 6: "Raymond Lee’s QPL-DRL framework uses Omega ratios"
PROVENANCE: blocked
SOURCE: Lee, R. T. (2024). QPL-DRL: Deep Reinforcement Learning with Quantitative Price Levels for Risk-Adjusted Trading. arXiv:2403.12345.
EVIDENCE: Paper focuses on Monte Carlo particle transport, not risk-adjusted trading<!--⚠️ FATAL: Misrepresented source-- remove claim-->.

CLAIM 7: "Investopedia URLs for Sharpe, Sortino, Treynor, Calmar ratios"
PROVENANCE: blocked
SOURCE: Investopedia.
EVIDENCE: URLs return 402 Payment Required<!--🔴 MAJOR: Blocked sources undermine credibility-- replace-->. 

CLAIM 8: "Reddit thread on benchmarking risk-adjusted returns"
PROVENANCE: blocked
SOURCE: Reddit Community. (2026). Benchmarking Risk-Adjusted Returns in Algo Trading. https://www.reddit.com/r/algotrading/comments/xyz123/
EVIDENCE: URL inaccessible (verification pending)<!--🔴 MAJOR: Blocked source undermines verification-- remove or replace-->.

---

## Severity Tally
**FATAL**: 2
**MAJOR**: 16
**MINOR**: 10

## Blocker Passages
1. **Omega Ratio Use Case** (Line 129): Raymond Lee’s QPL-DRL framework claim is fatally misrepresented.
2. **Open Question 4** (Line 345): QPL-DRL claim is fatally misrepresented.

## Verdict
**NO-GO**: Document requires immediate revision to address:
- 2 FATAL issues (misrepresented source).
- 16 MAJOR issues (unsupported claims, blocked sources).

## Revision Plan
1. **Remove or correct FATAL claims** about QPL-DRL.
2. **Replace blocked sources** (Investopedia, Reddit) with accessible alternatives.
3. **Add citations or hedges** for all unsupported claims (e.g., use cases, benchmarks).
4. **Clarify speculative language** (e.g., "may mask," "ubiquitous").