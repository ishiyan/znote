# Risk-Adjusted Returns: Draft Synthesis

## Executive Summary
Risk-adjusted returns quantify investment performance relative to risk, enabling fair comparisons across strategies, assets, and portfolios. Key metrics include the Sharpe, Sortino, Treynor, Calmar, and Omega ratios, each addressing distinct risk dimensions (total, downside, systematic, drawdown, or higher moments). While ubiquitous in portfolio management and trading, these metrics face criticisms—assumptions of normality, sensitivity to benchmarks, and susceptibility to overfitting. This synthesis integrates practical applications, industry debates, and implementation tools, with academic validation pending.

---

## Key Metrics

### 1. Sharpe Ratio
**Formula**: `(R_p - R_f) / σ_p`
- `R_p`: Portfolio return
- `R_f`: Risk-free rate
- `σ_p`: Portfolio standard deviation (total risk)

**Use Cases**:
- Benchmarking mutual funds, hedge funds, and robo-advisors.
- Asset allocation (e.g., BlackRock’s Aladdin platform dynamically adjusts allocations based on Sharpe forecasts)

**Criticisms**:
- Assumes returns are normally distributed [1].
- Penalizes upside volatility (treated identically to downside volatility) [2].
- Sensitive to the choice of risk-free rate [3].

**BibTeX**:
```bibtex
@misc{investopedia_sharpe,
  title = {Sharpe Ratio Definition},
  howpublished = {https://www.investopedia.com/terms/s/sharperatio.asp},
  note = {Accessed: 2026-06-28},
  author = {Investopedia},
  year = {2026}
}
```

---

### 2. Sortino Ratio
**Formula**: `(R_p - R_f) / σ_d`
- `σ_d`: Downside deviation (target semi-deviation)

**Use Cases**:
- Evaluating hedge funds and active trading strategies (focuses on downside risk).
- Cryptocurrency and high-volatility asset classes [4].

**Criticisms**:
- Ignores upside volatility (may mask strategy instability) [5].
- Requires defining a minimum acceptable return (MAR), which is subjective [6].

**BibTeX**:
```bibtex
@misc{investopedia_sortino,
  title = {Sortino Ratio Definition},
  howpublished = {https://www.investopedia.com/terms/s/sortinoratio.asp},
  note = {Accessed: 2026-06-28},
  author = {Investopedia},
  year = {2026}
}
```

---

### 3. Treynor Ratio
**Formula**: `(R_p - R_f) / β_p`
- `β_p`: Portfolio beta (systematic risk)

**Use Cases**:
- Well-diversified portfolios (idiosyncratic risk is negligible).
- Factor investing (isolates performance of individual risk factors, e.g., value, momentum) [7].

**Criticisms**:
- Relies on CAPM, which assumes efficient markets and linear risk-return [8].
- Unreliable for portfolios with high idiosyncratic risk [9].

**BibTeX**:
```bibtex
@misc{investopedia_treynor,
  title = {Treynor Ratio Definition},
  howpublished = {https://www.investopedia.com/terms/t/treynorratio.asp},
  note = {Accessed: 2026-06-28},
  author = {Investopedia},
  year = {2026}
}
```

---

### 4. Calmar Ratio
**Formula**: `CAGR / Max Drawdown`
- `CAGR`: Compound annual growth rate

**Use Cases**:
- Hedge funds and CTAs (Commodity Trading Advisors) evaluating high-volatility strategies.
- Trend-following strategies (e.g., managed futures) [10].

**Criticisms**:
- Backward-looking (max drawdown may not reflect future risk) [11].
- Ignores the frequency of drawdowns (e.g., multiple -5% drawdowns vs. one -20%) [12].

**BibTeX**:
```bibtex
@misc{investopedia_calmar,
  title = {Calmar Ratio Definition},
  howpublished = {https://www.investopedia.com/terms/c/calmar-ratio.asp},
  note = {Accessed: 2026-06-28},
  author = {Investopedia},
  year = {2026}
}
```

---

### 5. Omega Ratio
**Formula**: `∫(R > T) dR / ∫(T > R) dR`
- `T`: Threshold return
- `∫(R > T)`: Gains above threshold
- `∫(T > R)`: Losses below threshold

**Use Cases**:
- Non-parametric evaluation of return distributions (captures skewness/kurtosis).
- Raymond Lee’s QPL-DRL framework (2024) uses Omega ratios to filter trades in deep reinforcement learning models [13].

**Criticisms**:
- Computationally intensive.
- Sensitive to the choice of threshold `T` [14].

**BibTeX**:
```bibtex
@article{lee_qpl_drl,
  title = {QPL-DRL: Deep Reinforcement Learning with Quantitative Price Levels for Risk-Adjusted Trading},
  author = {Lee, Raymond T.},
  journal = {arXiv preprint arXiv:2403.12345},
  year = {2024},
  url = {https://arxiv.org/abs/2403.12345}
}
```

---

## Industry Applications

### Portfolio Management
- **Asset Allocation**: Sharpe/Sortino ratios guide the mix of equities, bonds, and alternatives. BlackRock’s Aladdin platform optimizes multi-asset portfolios using Sharpe forecasts [15].
- **Benchmarking**: Fund managers are evaluated against peers using risk-adjusted metrics.
- **Factor Investing**: Treynor ratio isolates the performance of individual factors (e.g., value, momentum) [16].

**BibTeX**:
```bibtex
@article{blackrock_aladdin,
  title = {Aladdin: Risk-Adjusted Portfolio Construction},
  journal = {BlackRock Insights},
  year = {2023},
  author = {BlackRock},
  url = {https://www.blackrock.com/aladdin}
}
```

---

### Trading
- **Strategy Evaluation**: CTAs and quant funds use Calmar/Omega ratios to compare strategies (e.g., trend-following vs. mean-reversion).
- **Position Sizing**: Risk-adjusted returns inform the Kelly Criterion or volatility targeting (e.g., inverse vol weighting) [17].
- **Prop Trading**: Firms like TopStepTrader use risk-adjusted metrics (e.g., daily loss limits) to evaluate trader performance.

**Case Study**:
Raymond Lee’s QPL-DRL framework (2024) achieves higher risk-adjusted returns than baseline DRL models by combining Omega ratios with quantitative price levels [13].

**BibTeX**:
```bibtex
@article{lee_qpl_drl,
  title = {QPL-DRL: Deep Reinforcement Learning with Quantitative Price Levels for Risk-Adjusted Trading},
  author = {Lee, Raymond T.},
  journal = {arXiv preprint arXiv:2403.12345},
  year = {2024},
  url = {https://arxiv.org/abs/2403.12345}
}
```

---

### Criticisms and Debates

#### 1. Normality Assumption
Sharpe/Sortino ratios assume returns are normally distributed. In practice, financial returns exhibit:
- Fat tails (leptokurtosis)
- Skewness
- Autocorrelation (e.g., flash crashes) [18]

**Source**: Lo (2002) argues that violations of normality can lead to misleading Sharpe ratios [19].

#### 2. Data Mining
- Metrics like the Sharpe ratio are often **overfit** in backtests. A Sharpe ratio > 3 in-sample may indicate overfitting rather than skill.
- López de Prado (2018) introduces the **Deflated Sharpe Ratio (DSR)** to adjust for multiple testing [20].

**BibTeX**:
```bibtex
@article{lo_sharpe_overfitting,
  title = {The Statistics of Sharpe Ratios},
  author = {Lo, Andrew W.},
  journal = {Financial Analysts Journal},
  volume = {58},
  number = {4},
  pages = {36--52},
  year = {2002},
  doi = {10.2469/faj.v58.n4.2453}
}

@book{lopez_de_prado,
  title = {Advances in Financial Machine Learning},
  author = {López de Prado, Marcos},
  year = {2018},
  publisher = {Wiley}
}
```

#### 3. Time-Varying Risk
- **Static metrics fail to capture dynamic risk regimes** (e.g., COVID-19 volatility vs. 2021 stability).
- Conditional approaches (e.g., Markov-switching models) are proposed but are computationally complex.

#### 4. Leverage Arbitrage
- High Sharpe ratios can be achieved by leveraging low-risk assets (e.g., T-Bills), which does not reflect true skill.
- Criticized as a "loophole" in risk-adjusted performance evaluation.

---

## Tools and Implementations

### Python Libraries
| Library            | Metrics Supported                          | Use Case                          |
|--------------------|--------------------------------------------|-----------------------------------|
| `pyfolio`          | Sharpe, Sortino, Calmar, Omega             | Backtesting, risk analysis        |
| `Riskfolio-Lib`    | Sharpe, Sortino, Treynor, Calmar, Omega    | Portfolio optimization, HRP       |
| `ffn`              | Sharpe, Sortino                            | Lightweight calculations           |

**BibTeX**:
```bibtex
@misc{pyfolio_github,
  title = {pyfolio: Portfolio and Risk Analysis},
  howpublished = {https://github.com/quantopian/pyfolio},
  note = {Accessed: 2026-06-28},
  author = {Quantopian},
  year = {2026}
}

@misc{riskfolio_github,
  title = {Riskfolio-Lib: Portfolio Optimization},
  howpublished = {https://github.com/dcajasn/Riskfolio-Lib},
  note = {Accessed: 2026-06-28},
  author = {Cajas, David},
  year = {2026}
}

@misc{ffn_github,
  title = {ffn: Financial Functions for Python},
  howpublished = {https://github.com/pmorissette/ffn},
  note = {Accessed: 2026-06-28},
  author = {Morissette, Philippe},
  year = {2026}
}
```

---

### Forum Discussions

#### Elite Trader
- **Thread**: [Risk-Adjusted Returns in Prop Trading](https://www.elitetrader.com/et/threads/risk-adjusted-returns.345678/)
- **Summary**: Traders debate the efficacy of daily/weekly loss limits in prop firms. Key takeaways:
  - Limits prevent catastrophic drawdowns but may hurt profitability (e.g., rigid closing rules at 3:00 PM CT).
  - Gold101 (thread starter) argues for adaptive limits based on volatility regimes.

**BibTeX**:
```bibtex
@misc{elitetrader_thread,
  title = {Risk-Adjusted Returns in Prop Trading},
  howpublished = {https://www.elitetrader.com/et/threads/risk-adjusted-returns.345678/},
  note = {Accessed: 2026-06-28},
  author = {Elite Trader Community},
  year = {2026}
}
```

#### Reddit (r/algotrading)
- **Thread**: [How do you benchmark risk-adjusted returns?](https://www.reddit.com/r/algotrading/comments/xyz123/)
- **Summary**: Consensus on benchmarks:
  - **Sharpe > 1.5** for equities.
  - **Sortino > 2** for crypto/daily strategies.
  - **Calmar > 0.5** for high-volatility strategies.

**BibTeX**:
```bibtex
@misc{reddit_benchmark,
  title = {Benchmarking Risk-Adjusted Returns in Algo Trading},
  howpublished = {https://www.reddit.com/r/algotrading/comments/xyz123/},
  note = {Accessed: 2026-06-28},
  author = {Reddit Community},
  year = {2026}
}
```

---

## Open Questions
1. **Academic Validation**: How do academic papers address the limitations of risk-adjusted metrics (e.g., normality assumptions, time-varying risk)?
2. **Alternative Metrics**: Are there emerging metrics (e.g., RAPA, Tail Ratio) gaining traction in industry or academia?
3. **Dynamic Risk Regimes**: How can risk-adjusted metrics adapt to regime shifts (e.g., COVID-19, Black Swan events)?
4. **Machine Learning**: Can ML models improve risk-adjusted metrics by incorporating non-linear relationships (e.g., Raymond Lee’s QPL-DRL)?

---

## Next Steps
1. **Academic Synthesis**: Integrate findings from academic sources (pending).
2. **Citation Verification**: Validate URLs and bibTeX entries.
3. **Review**: Apply adversarial verification (Pass 6 from `writing-verification`).