# William Blau's Indicators: Mathematical Foundations

## Sources

- William Blau, *Momentum, Direction, and Divergence* (Wiley, 1995)
- William Blau, "True Strength Index", *Stocks & Commodities* Vol. 11 No. 1, Nov 1991
- William Blau, "Stochastic Momentum", *Stocks & Commodities* Vol. 9 No. 11, Jan 1993
- Wikipedia: [True Strength Index](https://en.wikipedia.org/wiki/True_strength_index)
- MQL5: [William Blau's Indicators Part 1](https://www.mql5.com/en/articles/190)

---

## 1. Double Smoothing: The Core Technique

### Definition

Double smoothing applies two cascaded exponential moving averages:

$$\text{DS}(x, r, s) = \text{EMA}(\text{EMA}(x, r), s)$$

where:
$$\text{EMA}(x_k, n) = \frac{2}{n+1} \cdot x_k + \left(1 - \frac{2}{n+1}\right) \cdot \text{EMA}(x_{k-1}, n)$$

Blau generalizes to triple smoothing: $\text{EMA}(\text{EMA}(\text{EMA}(x, r), s), u)$

### Why Two EMAs Instead of One Longer EMA?

A single EMA with smoothing factor $\alpha = 2/(n+1)$ has a transfer function (z-domain):

$$H(z) = \frac{\alpha}{1 - (1-\alpha)z^{-1}}$$

Two cascaded EMAs with factors $\alpha_1, \alpha_2$ yield:

$$H(z) = \frac{\alpha_1 \alpha_2}{[1 - (1-\alpha_1)z^{-1}][1 - (1-\alpha_2)z^{-1}]}$$

This is a **second-order IIR filter** with a double pole. Key advantages:

1. **Steeper roll-off**: -40 dB/decade vs. -20 dB/decade for a single EMA. High-frequency noise is suppressed quadratically.
2. **Better time-domain response**: The impulse response of a double EMA is a convolution of two exponentials, producing a smoother "hump-shaped" weighting that avoids the discontinuous jump of a single EMA.
3. **Tunable lag vs. smoothing**: By choosing short second period $s \ll r$, you get most noise suppression from the first EMA while the second only removes residual chatter with minimal additional lag.
4. **Reduced lag compared to single EMA of equivalent smoothing**: A single EMA achieving the same noise reduction would need period $\approx r + s - 1$, giving lag $\approx (r+s-2)/2$. The double EMA has total group delay $\approx (r-1)/2 + (s-1)/2 = (r+s-2)/2$ --- same delay but the frequency response shape is superior (steeper transition band).

---

## 2. True Strength Index (TSI)

### Formula

$$\text{TSI}(q, r, s) = 100 \times \frac{\text{EMA}(\text{EMA}(\text{mtm}, r), s)}{\text{EMA}(\text{EMA}(|\text{mtm}|, r), s)}$$

where:
- $\text{mtm} = \text{price}(t) - \text{price}(t - (q-1))$ (q-period momentum; Blau default $q=2$, i.e. 1-bar change)
- $r = 25$ (long EMA period, sets the trend smoothing)
- $s = 13$ (short EMA period, removes residual noise)

### Interpretation

- Numerator: double-smoothed signed momentum (preserves direction)
- Denominator: double-smoothed absolute momentum (normalizer)
- Result bounded to $[-100, +100]$
- Overbought: TSI > +25; Oversold: TSI < -25

### Blau's Triple-Smoothed Generalization

$$\text{TSI}(q, r, s, u) = 100 \times \frac{\text{EMA}(\text{EMA}(\text{EMA}(\text{mtm}, r), s), u)}{\text{EMA}(\text{EMA}(\text{EMA}(|\text{mtm}|, r), s), u)}$$

Default from MQL5 implementation: $q=2, r=20, s=5, u=3$.

---

## 3. Ergodic Oscillator

$$\text{Ergodic} = \text{TSI}(q, r, s, u)$$
$$\text{Signal} = \text{EMA}(\text{Ergodic}, ul)$$

where $ul$ equals the period of the last significant smoothing (e.g., if $u=1$, then $ul = s$).

- Buy signal: Ergodic crosses above Signal
- Sell signal: Ergodic crosses below Signal
- Trend: Ergodic above Signal = uptrend

---

## 4. Stochastic Momentum Index (SMI)

### Lane's Standard Stochastic

$$\%K = 100 \times \frac{C - L_q}{H_q - L_q}$$

where $H_q, L_q$ = highest high / lowest low over $q$ periods. Range: $[0, 100]$.

### Blau's Stochastic Momentum

The key insight: instead of measuring distance from the low, measure distance from the **midpoint**:

$$\text{SM}(q) = C - \frac{1}{2}(H_q + L_q)$$

This is the **stochastic momentum** --- how far price is from the middle of the recent range.

### Stochastic Momentum Index

$$\text{SMI}(q, r, s, u) = 100 \times \frac{\text{EMA}(\text{EMA}(\text{EMA}(\text{SM}(q), r), s), u)}{\frac{1}{2} \cdot \text{EMA}(\text{EMA}(\text{EMA}(H_q - L_q, r), s), u)}$$

- Range: $[-100, +100]$ (centered on zero, unlike Lane's $[0, 100]$)
- Zero crossing indicates price at midpoint of range
- More symmetric; better suited for divergence analysis

### Difference from Lane's Stochastic

| Feature | Lane %K | Blau SMI |
|---------|---------|----------|
| Reference point | Low of range | Midpoint of range |
| Range | [0, 100] | [-100, +100] |
| Smoothing | Single SMA or EMA | Double/triple EMA |
| Sensitivity to range shifts | High | Lower (midpoint is more stable) |

---

## 5. Double Smoothed Stochastics (DSS)

### Blau Version

Blau's stochastic index applies double smoothing to the raw stochastic before normalization:

$$\text{Stoch}(q) = C - L_q \quad \text{(distance from low)}$$

$$\text{StochI}(q, r, s) = 100 \times \frac{\text{EMA}(\text{EMA}(\text{Stoch}(q), r), s)}{\text{EMA}(\text{EMA}(H_q - L_q, r), s)}$$

### Bressert Version (DSS Bressert)

Walter Bressert's DSS applies a stochastic calculation *twice*:

1. Compute raw stochastic $\%K$ over $q$ periods
2. Smooth with EMA to get $\text{DS} = \text{EMA}(\%K, r)$
3. Apply stochastic again to the smoothed line: $\text{DSS} = 100 \times \frac{DS - L_{DS}}{H_{DS} - L_{DS}}$
4. Smooth: $\text{DSSLine} = \text{EMA}(\text{DSS}, s)$

Key difference: Bressert applies the stochastic *operator* twice; Blau applies the *smoothing* twice to the raw data before normalizing once.

---

## 6. Directional Trend Index (DTI)

Based on "composite high-low momentum":

$$\text{HLM}(q) = H - H_{q-1} + L - L_{q-1}$$

This captures both upper and lower price boundary movements (virtual close concept).

$$\text{DTI}(q, r, s, u) = 100 \times \frac{\text{EMA}(\text{EMA}(\text{EMA}(\text{HLM}(q), r), s), u)}{\text{EMA}(\text{EMA}(\text{EMA}(|\text{HLM}(q)|, r), s), u)}$$

Interpretation: measures directional strength using the full bar range rather than just close-to-close momentum.

---

## 7. Candlestick Momentum (CMtm)

$$\text{CMtm} = C - O$$

The intra-bar momentum (close minus open of the same bar). Captures buying/selling pressure within each period.

### Candlestick Momentum Index (CMI)

$$\text{CMI}(q, r, s, u) = 100 \times \frac{\text{EMA}(\text{EMA}(\text{EMA}(C - O, r), s), u)}{\text{EMA}(\text{EMA}(\text{EMA}(|C - O|, r), s), u)}$$

### Candlestick Size Index (CSI)

$$\text{CSI}(q, r, s, u) = 100 \times \frac{\text{EMA}(\text{EMA}(\text{EMA}(C - O, r), s), u)}{\frac{1}{2}\cdot\text{EMA}(\text{EMA}(\text{EMA}(H - L, r), s), u)}$$

---

## 8. Comparison: Double Smoothing vs. Other Filter Approaches

| Filter | Order | Phase Lag | Roll-off | Complexity | Notes |
|--------|-------|-----------|----------|------------|-------|
| Single EMA | 1st-order IIR | $(n-1)/2$ bars | -20 dB/dec | O(1) per bar | Simple but gradual roll-off |
| **Double EMA (Blau)** | **2nd-order IIR** | $(r-1)/2 + (s-1)/2$ | **-40 dB/dec** | **O(1) per bar** | **Best simplicity/performance ratio** |
| Butterworth (2nd order) | 2nd-order IIR | Non-linear phase | -40 dB/dec | O(1) per bar | Maximally flat passband; phase distortion |
| Gaussian filter | FIR | $(n-1)/2$ (linear phase) | Depends on width | O(n) per bar | No phase distortion; computationally heavier |
| Jurik MA (JMA) | Proprietary | Low (adaptive) | Steep | Proprietary | Adaptive bandwidth; black box |
| Zero-lag EMA (Ehlers) | Modified IIR | Near zero | -20 dB/dec | O(1) per bar | Achieves low lag by error correction; can overshoot |
| DEMA (Mulloy) | 2×EMA - EMA(EMA) | Reduced | Moderate | O(1) per bar | Different from Blau; subtracts lag component |
| TEMA (Mulloy) | 3×EMA - 3×EMA(EMA) + EMA³ | Very low | Good | O(1) per bar | Can overshoot; not pure smoothing |

### Phase/Lag Characteristics of Double Smoothing

The group delay of a single EMA at DC (zero frequency) is:
$$\tau_{\text{EMA}} = \frac{1-\alpha}{\alpha} = \frac{n-1}{2} \text{ bars}$$

For cascaded EMAs:
$$\tau_{\text{double}} = \frac{r-1}{2} + \frac{s-1}{2} \text{ bars}$$

At higher frequencies, the group delay is frequency-dependent (non-linear phase), which causes some waveform distortion. However, for trend-following applications this is acceptable because:
- The signal of interest (trend) is at very low frequencies where group delay is approximately constant
- High-frequency components (noise) are being rejected, not preserved

---

## 9. Signal Processing Analysis: Why Double Smoothing Works

### Frequency Response

A single EMA with $\alpha = 2/(n+1)$ has magnitude response:

$$|H(e^{j\omega})| = \frac{\alpha}{\sqrt{1 - 2(1-\alpha)\cos\omega + (1-\alpha)^2}}$$

Two cascaded EMAs multiply the magnitude responses:

$$|H_{\text{double}}(e^{j\omega})| = |H_1(e^{j\omega})| \cdot |H_2(e^{j\omega})|$$

This **squares the attenuation** at each frequency (in linear scale). At the Nyquist frequency ($\omega = \pi$), a single EMA with $n=20$ attenuates by ~0.095 (-20.4 dB); double smoothing attenuates by $0.095^2 \approx 0.009$ (-40.8 dB).

### Noise Reduction vs. Lag Tradeoff

The fundamental tradeoff in any causal filter:
- More smoothing = more lag
- Double smoothing's advantage is **efficiency**: it achieves the same noise reduction as a single longer EMA but with a steeper transition band

Quantitatively, for equivalent noise reduction $\sigma_{\text{out}}/\sigma_{\text{in}}$:
- Single EMA needs period $N$ with lag $(N-1)/2$
- Double EMA with periods $r, s$ where $r \cdot s \approx N$ achieves similar noise reduction with lag $(r+s-2)/2 < (N-1)/2$ when $r, s > 1$

Example: $r=20, s=5$ gives lag = 11.5 bars and noise suppression equivalent to single EMA of period ~37 (lag = 18 bars). **Savings: ~36% less lag for equivalent smoothing.**

### Why Blau's Approach Is Elegant

1. **Computational simplicity**: Each EMA is O(1) per bar --- just one multiply-add. Double/triple smoothing remains O(1).
2. **Recursive (online)**: No lookback buffer needed beyond state variables.
3. **Normalization preserves scale**: Dividing smoothed momentum by smoothed absolute momentum creates a bounded oscillator without arbitrary scaling.
4. **Separation of concerns**: First EMA (large $r$) captures the trend; second EMA (small $s$) removes residual jitter. This is analogous to a cascade of a "trend filter" and a "noise filter" with clearly distinct roles.

### Comparison to Butterworth

A 2nd-order Butterworth also has -40 dB/decade roll-off but is designed for maximally flat passband. Blau's double EMA has a gentler passband shape (slight droop at mid-frequencies) but:
- Simpler to implement
- Parameters are intuitive (periods in bars)
- More robust to parameter choices (no ringing/overshoot)
- Naturally causal with well-behaved transient response

---

## 10. Summary of All Blau Indicator Formulas

| Indicator | Formula | Output Range |
|-----------|---------|--------------|
| Momentum | $\text{Mtm} = \text{EMA}(\text{EMA}(\text{EMA}(C_t - C_{t-q+1}, r), s), u)$ | Unbounded |
| TSI | $100 \times \frac{\text{Mtm}}{\text{EMA}(\text{EMA}(\text{EMA}(|C_t - C_{t-q+1}|, r), s), u)}$ | [-100, +100] |
| Ergodic | TSI + Signal line $= \text{EMA}(\text{TSI}, ul)$ | [-100, +100] |
| Stochastic | $100 \times \frac{\text{EMA}(\text{EMA}(\text{EMA}(C - L_q, r), s), u)}{\text{EMA}(\text{EMA}(\text{EMA}(H_q - L_q, r), s), u)}$ | [0, +100] |
| SMI | $100 \times \frac{\text{EMA}(\text{EMA}(\text{EMA}(C - \text{mid}_q, r), s), u)}{0.5 \cdot \text{EMA}(\text{EMA}(\text{EMA}(H_q - L_q, r), s), u)}$ | [-100, +100] |
| DTI | $100 \times \frac{\text{EMA}(\text{EMA}(\text{EMA}(\text{HLM}, r), s), u)}{\text{EMA}(\text{EMA}(\text{EMA}(|\text{HLM}|, r), s), u)}$ | [-100, +100] |
| CMI | $100 \times \frac{\text{EMA}(\text{EMA}(\text{EMA}(C-O, r), s), u)}{\text{EMA}(\text{EMA}(\text{EMA}(|C-O|, r), s), u)}$ | [-100, +100] |

All share the same architectural pattern: **double/triple smooth a raw measure, then normalize by the smoothed absolute value** to create a bounded oscillator.

---

## References

1. Blau, W. (1995). *Momentum, Direction, and Divergence*. John Wiley & Sons. ISBN 978-0-471-02729-4.
2. Blau, W. (1991). "True Strength Index". *Stocks & Commodities*, 11(1), 438-446.
3. Blau, W. (1993). "Stochastic Momentum". *Stocks & Commodities*, 9(11), 11-18.
4. Zelinsky, A.F. (2011). "William Blau's Indicators and Trading Systems in MQL5". MQL5 Articles.
5. Ehlers, J.F. (2001). *Rocket Science for Traders*. John Wiley & Sons.
