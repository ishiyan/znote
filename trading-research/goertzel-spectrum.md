# Goertzel Spectrum: Trading Research Brief

## Overview
The **Goertzel spectrum** refers to spectral analysis techniques using the **Goertzel algorithm**, a digital signal processing (DSP) method optimized for detecting specific frequency components. While Gerald Goertzel’s 1958 algorithm was not originally designed for trading, it underpins **cycle detection**, **spectral forecasting**, and **singular spectrum analysis (SSA)** in financial markets.

This brief synthesizes TASC articles, MQL5 implementations, academic papers, and GitHub repositories addressing Goertzel-based spectral methods in trading.

---

## TASC Articles

### 1983–2008: Spectral Analysis Foundations

| Year | Month | Title | Author | Description | Article |
|------|-------|-------|--------|-------------|---------|
| 1983 | Jan | [\V01\C02\MINIG](https://technical.traders.com/archive/article.asp?file=\V01\C02\MINIG.pdf) | Anthony W. Warren | Introduces Fourier spectrum analysis for trading using Goertzel’s recursive DFT method. | [Link](https://technical.traders.com/archive/article.asp?file=\V01\C02\MINIG.pdf) |
| 1984 | Jul | [\V02\C04\FOUR](https://technical.traders.com/archive/article.asp?file=\V02\C04\FOUR.pdf) | William T. Taylor | Demonstrates Fourier spectral analysis for cycle detection. | [Link](https://technical.traders.com/archive/article.asp?file=\V02\C04\FOUR.pdf) |
| 1984 | Sep | [\V02\C05\MOV](https://technical.traders.com/archive/article.asp?file=\V02\C05\MOV.pdf) | A.D. Ridley | Introduces **moving window spectral method** — rolling spectral estimates via Goertzel’s algorithm. Origin of the term "Spectral Forecasting." | [Link](https://technical.traders.com/archive/article.asp?file=\V02\C05\MOV.pdf) |
| 1985 | Apr | [\V03\C02\LEAD](https://technical.traders.com/archive/article.asp?file=\V03\C02\LEAD.pdf) | William T. Taylor | Applies Fourier spectral analysis to derive leading indicators. | [Link](https://technical.traders.com/archive/article.asp?file=\V03\C02\LEAD.pdf) |
| 1993 | Jan | [\V11\C01\SPECTRA](https://technical.traders.com/archive/article.asp?file=\V11\C01\SPECTRA.pdf) | Denis Ridley | Formalizes **Spectral Forecasting** — advanced trading system using Goertzel for real-time cycle extraction. | [Link](https://technical.traders.com/archive/article.asp?file=\V11\C01\SPECTRA.pdf) |
| 2005 | Oct | [\V23\C10\204DROG](https://technical.traders.com/archive/article.asp?file=\V23\C10\204DROG.pdf) | Sergiy Drogobetskii | Introduces **Singular Spectrum Analysis (SSA)** — Goertzel DFT initializes spectral components. | [Link](https://technical.traders.com/archive/article.asp?file=\V23\C10\204DROG.pdf) |
| 2005 | Nov | [\V23\C11\230DROG](https://technical.traders.com/archive/article.asp?file=\V23\C11\230DROG.pdf) | Sergiy Drogobetskii | SSA Part II: applies SSA to Forex trading. Goertzel validates eigenvector oscillations. | [Link](https://technical.traders.com/archive/article.asp?file=\V23\C11\230DROG.pdf) |
| 2008 | Jul | [\V26\C07\133EYO](https://technical.traders.com/archive/article.asp?file=\V26\C07\133EYO.pdf) | S. Drogobetskii & V. Smolynsky | Forecasts exchange rates using SSA. Goertzel pre-computes Fabrizo-SSA spectral basis. | [Link](https://technical.traders.com/archive/article.asp?file=\V26\C07\133EYO.pdf) |

---

## MQL5 Implementations

| Title | Platform | URL | Description |
|-------|----------|-----|-------------|
| [Cycle Analysis Using the Goertzel Algorithm](https://www.mql5.com/en/articles/975) | MetaTrader 5 | [Link](https://www.mql5.com/en/articles/975) | MQL5 implementation for cycle analysis in financial time series. |
| [GoertzelBrain: Adaptive Spectral Cycle Detection](https://www.mql5.com/en/articles/21376) | MetaTrader 5 | [Link](https://www.mql5.com/en/articles/21376) | Combines Goertzel’s algorithm with neural networks for adaptive cycle detection. |

---

## Forum Discussions
No discussions on "Goertzel spectrum" were found across the 10 searched trading forums.

---

## Academic Papers

| Title | Authors | Year | DOI | URL |
|-------|---------|------|-----|-----|
| [Determination of Spectral Parameters of Speech Signal by Goertzel Algorithm](http://www.intechopen.com/download/pdf/15939) | Bozo Tomas, Darko Zelenik | 2011 | [10.5772/16248](https://doi.org/10.5772/16248) | [PDF](http://www.intechopen.com/download/pdf/15939) |
| [Spectral Analysis of Heart Murmurs in Children by Goertzel Algorithm](http://ieeexplore.ieee.org/document/5359664/) | Božo Tomas, Željko Roncevic | 2009 | [10.1109/computationworld.2009.25](https://doi.org/10.1109/computationworld.2009.25) | [IEEE](http://ieeexplore.ieee.org/document/5359664/) |
| [On improving the accuracy of Horner's and Goertzel's algorithms](https://arxiv.org/abs/math/0407177v1) | Alicja Smoktunowicz, Iwona Wróbel | 2004 | [10.1007/s11075-004-4570-4](https://doi.org/10.1007/s11075-004-4570-4) | [arXiv](https://arxiv.org/abs/math/0407177v1) |

---

## GitHub Repositories

| Repository | Stars | Language | Description |
|------------|-------|----------|-------------|
| [jaimedantas/Frequency-Analyzer-Arduino](https://github.com/jaimedantas/Frequency-Analyzer-Arduino) | 15 | C | Spectrum Analyzer using Goertzel Algorithm in Arduino (2016). |
| [ramonfava/spectrum-analyzer](https://github.com/ramonfava/spectrum-analyzer) | 2 | C | Spectrum analyzer for Arduino Mini using Goertzel algorithm. |

---

## BibTeX

```bibtex
@article{tasc_1983_jan_miniguide,
  author = {Warren, Anthony W.},
  title = {A MiniGuide to Fourier Spectrum Analysis},
  journal = {Technical Analysis of Stocks & Commodities},
  year = {1983},
  volume = {1},
  number = {2},
  url = {https://technical.traders.com/archive/article.asp?file=\V01\C02\MINIG.pdf}
}

@article{tasc_1984_sep_moving_window,
  author = {Ridley, A.D.},
  title = {Moving Window Spectral Method: Price Forecasting With Cycles},
  journal = {Technical Analysis of Stocks & Commodities},
  year = {1984},
  volume = {2},
  number = {5},
  url = {https://technical.traders.com/archive/article.asp?file=\V02\C05\MOV.pdf}
}

@article{tasc_1993_jan_spectral_forecasting,
  author = {Ridley, Denis},
  title = {Spectral Forecasting And The Financial Markets},
  journal = {Technical Analysis of Stocks & Commodities},
  year = {1993},
  volume = {11},
  number = {1},
  url = {https://technical.traders.com/archive/article.asp?file=\V11\C01\SPECTRA.pdf}
}

@online{mql5_goertzel_cycle_analysis,
  author = {{Francis Dube}},
  title = {Cycle analysis using the Goertzel algorithm},
  year = {2015},
  url = {https://www.mql5.com/en/articles/975},
  urldate = {2026-06-30}
}

@article{goertzel_2011_spectral_speech,
  author = {Tomas, Bozo and Zelenik, Darko},
  title = {Determination of Spectral Parameters of Speech Signal by Goertzel Algorithm},
  journal = {InTech},
  year = {2011},
  doi = {10.5772/16248},
  url = {http://www.intechopen.com/download/pdf/15939}
}
```