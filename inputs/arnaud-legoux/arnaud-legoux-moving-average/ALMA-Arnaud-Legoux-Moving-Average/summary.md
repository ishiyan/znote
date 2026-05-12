# Summary: ALMA — Arnaud Legoux Moving Average

**Title:** ALMA — Arnaud Legoux Moving Average  
**Authors:** Arnaud Legoux & Dimitrios Kouzis-Loukas  
**Date:** November 24, 2009  
**Source:** arnaudlegoux.com (original whitepaper)  
**Pages:** 6  
**Format:** PDF (Mac OS X Word export, custom font encoding)

## Key Topics

- Moving Average comparison: SMA, EMA, HMA, ALMA
- Smoothness vs. responsiveness tradeoff (Uncertainty Principle for discrete-time filters)
- Gaussian-weighted kernel with adjustable offset and sigma parameters
- Information value vs. information confidence concepts
- ALMA outperforms HMA: same responsiveness, better smoothness, no overshoot effects

## ALMA Parameters

- **Window (SIZE):** lookback period
- **Offset:** 0 to 1, controls bias toward recent days (default: 0.85)
- **Sigma (σ):** controls filter width (default: 6, inspired by Six Sigma)
