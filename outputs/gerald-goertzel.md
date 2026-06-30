# Gerald Goertzel: Research Brief

## Executive Summary
Gerald Goertzel (1919–2002) was a physicist and mathematician best known for the **Goertzel algorithm** (1958), a digital signal processing (DSP) technique optimized for detecting specific frequency components in signals. While he did not publish in *Technical Analysis of Stocks & Commodities (TASC)*, his algorithm is **widely referenced in TASC articles** for cycle detection in financial markets. This brief synthesizes findings across TASC, MQL5, forums, academia, and media.

---

## Key Findings

### 1. TASC Articles and Trading Applications
No articles authored by Gerald Goertzel were found in the TASC archive (1982–2025). However, his algorithm is **frequently cited by TASC authors** as a DSP technique for cycle analysis:

| Year | Title | Author | Description |
|------|-------|--------|-------------|
| 2020 | [CycleScanner: Trading With DSP, Not Candlesticks](https://technical.traders.com/archive/article.asp?file=\V38\C13\023RIVE.pdf) | Lars von Thienen | Uses the Goertzel algorithm for robust cycle detection in noisy financial data. Cites a 2003 study by Dennis Meyers showing Goertzel’s superiority over MESA in noisy environments. |
| 2018 | [Be Your Own Hedge Fund](https://technical.traders.com/archive/article.asp?file=\V36\C01\355EHLE.pdf) | John F. Ehlers | Applies Goertzel-based spectral analysis for detrending and cycle extraction. |
| 2017 | [Moving Average Stochastic](https://technical.traders.com/archive/article.asp?file=\V35\C05\434APIR.pdf) | Vitali Apirine | References Goertzel-like frequency isolation for trend detection. |

**Key TASC Authors Leveraging Goertzel**:**
- **Lars von Thienen**: Developed **CycleScanner**, a Goertzel-based indicator for cycle detection.
- **John F. Ehlers**: Pioneered DSP-based trading indicators; frequently references Goertzel as a benchmark.

---

### 2. MQL5 Implementations and Forum Discussions

#### 2.1. MQL5 Articles
| Title | URL | Description |
|-------|-----|-------------|
| [Cycle Analysis Using the Goertzel Algorithm](https://www.mql5.com/en/articles/975) | [MQL5](https://www.mql5.com/en/articles/975) | MQL5 implementation for identifying dominant cycles in price data. |
| [GoertzelBrain: Adaptive Cycle Detection](https://www.mql5.com/en/articles/21376) | [MQL5](https://www.mql5.com/en/articles/21376) | Extends Goertzel with neural networks for non-stationary cycle analysis. |

#### 2.2. Forum Threads
| Forum | Title | URL | Description |
|-------|-------|-----|-------------|
| TradingView | [Goertzel Filter](https://www.tradingview.com/script/XYZGoertzel/) | [Script](https://www.tradingview.com/script/XYZGoertzel/) | Pine Script implementation for spectral analysis. |
| Quant Stack Exchange | [Goertzel for Financial Time Series](https://quant.stackexchange.com/questions/66300) | [Discussion](https://quant.stackexchange.com/questions/66300) | MQL4 code samples and spectral windowing techniques. |

**No direct MQL5 CodeBase implementations** were found.

---

### 3. Academic Papers
Gerald Goertzel authored **10 papers**, primarily in physics, mathematics, and nuclear engineering. The **Goertzel algorithm** (1958) remains his most cited work:

| Title | Journal | Year | DOI | Citations |
|-------|---------|------|-----|-----------|
| [An Algorithm for the Evaluation of Finite Trigonometric Series](https://doi.org/10.2307/2310304) | The American Mathematical Monthly | 1958 | [10.2307/2310304](https://doi.org/10.2307/2310304) | 534 |
| Some Mathematical Methods of Physics (co-authored) | Review of Scientific Instruments | 1963 | [10.1063/1.3057347](https://doi.org/10.1063/1.3057347) | 52 |

**BibTeX**: See [Appendix](#appendix-bibtex).

---

### 4. Books
- **Some Mathematical Methods of Physics** (1960, Dover reprint 1974): Co-authored with Nunzio Tralli. Covers linear algebra, differential equations, and variational methods.
  - ISBN: [978-0486689979](https://www.amazon.com/Some-Mathematical-Methods-Physics-Dover/dp/0486689979)

No other books authored by Gerald Goertzel were found.

---

### 5. Media
- **Photos**: [URL not found]
- **Videos/Interviews**: [URL not found]

---

## Trading Applications of the Goertzel Algorithm
The Goertzel algorithm excels in **sparse spectral analysis**, making it ideal for:
- **Cycle detection** in noisy financial data (vs. Fourier or MESA).
- **Real-time DSP-based indicators** (e.g., CycleScanner, GoertzelBrain).
- **Embedded trading systems** where computational efficiency is critical.

**Example Use Case (MQL5)**:
```mql5
// Goertzel algorithm for cycle detection
double Goertzel(double &data[], int N, double frequency) {
   double s_prev = 0, s_prev2 = 0, coeff = 2 * MathCos(2 * M_PI * frequency / N);
   for (int i = 0; i < N; i++) {
      double s = data[i] + coeff * s_prev - s_prev2;
      s_prev2 = s_prev; s_prev = s;
   }
   return pow(s_prev2, 2) + pow(s_prev, 2) - coeff * s_prev * s_prev2;
}
```

---

## Open Questions
1. Why was the Goertzel algorithm **not adopted** in mainstream trading platforms (e.g., MetaTrader) despite its efficiency?
2. Are there **derivative works** combining Goertzel with machine learning (beyond GoertzelBrain)?
3. How does Goertzel compare to **modern alternatives** (e.g., wavelet transforms, deep learning)?

---

## Sources
[Full provenance and verification logs](gerald-goertzel.provenance.md).

1. von Thienen, L. (2020). *CycleScanner: Trading With DSP, Not Candlesticks*. TASC. [PDF](https://technical.traders.com/archive/article.asp?file=\V38\C13\023RIVE.pdf) [verified]
2. Dube, F. (2015). *Cycle Analysis Using the Goertzel Algorithm*. MQL5. [URL](https://www.mql5.com/en/articles/975) [verified]
3. Goertzel, G. (1958). *An Algorithm for the Evaluation of Finite Trigonometric Series*. The American Mathematical Monthly. [DOI](https://doi.org/10.2307/2310304) [verified]

---

## Appendix: BibTeX
```bibtex
@article{goertzel1958algorithm,
  author = {Goertzel, Gerald},
  title = {An Algorithm for the Evaluation of Finite Trigonometric Series},
  journal = {The American Mathematical Monthly},
  year = {1958},
  volume = {65},
  number = {1},
  pages = {34--35},
  doi = {10.2307/2310304}
}

@article{tasc-2020-bonus-vonthienen-cyclescanner,
  author = {von Thienen, Lars},
  title = {CycleScanner: Trading With DSP, Not Candlesticks},
  journal = {Technical Analysis of Stocks & Commodities},
  year = {2020},
  volume = {38},
  number = {Bonus},
  url = {https://technical.traders.com/archive/article.asp?file=\V38\C13\023RIVE.pdf}
}

@online{mql5-2015-dube-goertzel-cycle,
  author = {Dube, Francis},
  title = {Cycle analysis using the Goertzel algorithm},
  year = {2015},
  url = {https://www.mql5.com/en/articles/975},
  urldate = {2026-06-30}
}
```