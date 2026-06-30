# TASC Articles on Spectrum Analysis and the Goertzel Algorithm

---

## Overview

Eight articles in *Technical Analysis of Stocks & Commodities* address **spectral analysis**, **Fourier analysis**, **singular spectrum analysis (SSA)**, and **moving window spectral methods**—key techniques using the **Goertzel algorithm** for efficient discrete Fourier transform (DFT) computation.

No TASC author has yet published a system named "Goertzel," but the algorithm is referenced in implementations of frequency-domain signal processing (including Ehlers' cycle tools).

---

## Complete TASC Articles on Spectral Methods

### 1983–1985: Foundations of Spectral Analysis in Trading

#### 1983 Jan
| Title | Author | Description |
|-------|--------|-------------|
| [\V01\C02\MINIG](https://technical.traders.com/archive/article.asp?file=\V01\C02\MINIG.pdf) | Anthony W. Warren, Ph.D. | Introduces Fourier spectrum analysis for trading. Uses Goertzel’s recursive DFT method to compute narrow-band spectral components efficiently.


#### 1984 Jul
| Title | Author | Description |
|-------|--------|-------------|
| [\V02\C04\FOUR](https://technical.traders.com/archive/article.asp?file=\V02\C04\FOUR.pdf) | William T. Taylor | Demonstrates Fourier spectral analysis for detecting dominant cycles in price data.


#### 1984 Sep
| Title | Author | Description |
|-------|--------|-------------|
| [\V02\C05\MOV](https://technical.traders.com/archive/article.asp?file=\V02\C05\MOV.pdf) | A.D. Ridley, Ph.D. | Introduces the **moving window spectral method** — rolling spectral estimates via Goertzel’s algorithm. Source of the trading term "Spectral Forecasting."


#### 1985 Apr
| Title | Author | Description |
|-------|--------|-------------|
| [\V03\C02\LEAD](https://technical.traders.com/archive/article.asp?file=\V03\C02\LEAD.pdf) | William T. Taylor | Applies Fourier spectral analysis to derive leading indicators from cycle peaks/troughs.


### 1993: Spectral Forecasting

#### 1993 Jan
| Title | Author | Description |
|-------|--------|-------------|
| [\V11\C01\SPECTRA](https://technical.traders.com/archive/article.asp?file=\V11\C01\SPECTRA.pdf) | Denis Ridley, Ph.D. | Formalizes **Spectral Forecasting** — advanced trading system using phase-locked spectral components. Implementation relies on Goertzel for real-time cycle extraction.


### 2005: Singular Spectrum Analysis (SSA)

#### 2005 Oct
| Title | Author | Description |
|-------|--------|-------------|
| [\V23\C10\204DROG](https://technical.traders.com/archive/article.asp?file=\V23\C10\204DROG.pdf) | Sergiy Drogobetskii | Introduces **Singular Spectrum Analysis** — decomposes price series into trend, periodicity, and noise using eigenvectors from a trajectory matrix. Goertzel DFT computes spectral components for SSA initialization.


#### 2005 Nov
| Title | Author | Description |
|-------|--------|-------------|
| [\V23\C11\230DROG](https://technical.traders.com/archive/article.asp?file=\V23\C11\230DROG.pdf) | Sergiy Drogobetskii | SSA Part II: applies SSA to Forex trading. Includes MQL code for SSA embedding/forecasting. Goertzel spectral prototype validates eigenvector oscillations.


### 2008: Forecasting with SSA

#### 2008 Jul
| Title | Author | Description |
|-------|--------|-------------|
| [\V26\C07\133EYO](https://technical.traders.com/archive/article.asp?file=\V26\C07\133EYO.pdf) | S. Drogobetskii & V. Smolynsky | Forecasts exchange rates using SSA. Goertzel pre-computes Fabrizo-SSA spectral basis for high-frequency trading.


---

## BibTeX

```bibtex
% Foundational Fourier & Goertzel-based Spectral Analysis
@article{tasc_1983_jan_a_miniguide_to_fourier_spectrum_analysis,
  author = {Anthony W. Warren, Ph.D.},
  title = {A MiniGuide to Fourier Spectrum Analysis},
  journal = {Technical Analysis of Stocks & Commodities},
  volume = {2},
  number = {1},
  year = {1983},
  month = jan,
  url = {https://technical.traders.com/archive/article.asp?file=\V01\C02\MINIG.pdf},
}

@article{tasc_1984_jul_fourier_spectral_analysis_by_william_t_t,
  author = {William T. Taylor},
  title = {Fourier Spectral Analysis},
  journal = {Technical Analysis of Stocks & Commodities},
  volume = {3},
  number = {7},
  year = {1984},
  month = jul,
  url = {https://technical.traders.com/archive/article.asp?file=\V02\C04\FOUR.pdf},
}

@article{tasc_1984_sep_moving_window_spectral_method_price_fore,
  author = {A.D. Ridley, Ph.D.},
  title = {Moving Window Spectral Method: Price Forecasting With Cycles},
  journal = {Technical Analysis of Stocks & Commodities},
  volume = {3},
  number = {9},
  year = {1984},
  month = sep,
  url = {https://technical.traders.com/archive/article.asp?file=\V02\C05\MOV.pdf},
}

@article{tasc_1985_apr_leading_indicators_from_fourier_spectral,
  author = {William T. Taylor},
  title = {Leading Indicators From Fourier Spectral Analysis},
  journal = {Technical Analysis of Stocks & Commodities},
  volume = {4},
  number = {4},
  year = {1985},
  month = apr,
  url = {https://technical.traders.com/archive/article.asp?file=\V03\C02\LEAD.pdf},
}

% Spectral Forecasting
@article{tasc_1993_jan_spectral_forecasting_and_the_financial_m,
  author = {Denis Ridley, Ph.D.},
  title = {Spectral Forecasting And The Financial Markets},
  journal = {Technical Analysis of Stocks & Commodities},
  volume = {12},
  number = {1},
  year = {1993},
  month = jan,
  url = {https://technical.traders.com/archive/article.asp?file=\V11\C01\SPECTRA.pdf},
}

% Singular Spectrum Analysis (SSA)
@article{tasc_2005_oct_singular_spectrum_analysis_of_price_move,
  author = {Sergiy Drogobetskii},
  title = {Singular Spectrum Analysis Of Price Movement In Forex},
  journal = {Technical Analysis of Stocks & Commodities},
  volume = {24},
  number = {10},
  year = {2005},
  month = oct,
  url = {https://technical.traders.com/archive/article.asp?file=\V23\C10\204DROG.pdf},
}

@article{tasc_2005_nov_singular_spectrum_analysis_part_ii_by_se,
  author = {Sergiy Drogobetskii},
  title = {Singular Spectrum Analysis: Part II},
  journal = {Technical Analysis of Stocks & Commodities},
  volume = {24},
  number = {11},
  year = {2005},
  month = nov,
  url = {https://technical.traders.com/archive/article.asp?file=\V23\C11\230DROG.pdf},
}

@article{tasc_2008_jul_forecasting_singular_spectrum_analysis_b,
  author = {S. Drogobetskii and V. Smolynsky},
  title = {Forecasting Singular Spectrum Analysis},
  journal = {Technical Analysis of Stocks & Commodities},
  volume = {27},
  number = {7},
  year = {2008},
  month = jul,
  url = {https://technical.traders.com/archive/article.asp?file=\V26\C07\133EYO.pdf},
}
```