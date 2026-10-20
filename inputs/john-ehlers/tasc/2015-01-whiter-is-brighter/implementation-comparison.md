# Universal Oscillator: source investigation

Investigation date: 2026-10-20. This comparison was completed before building the standalone master.

## Book search

The supplied 2013 [book contents](../../2013-cycle-analytics-for-traders/toc.md) and all 17 chapters contain no Universal Oscillator definition or implementation. The article presents it as a new indicator. Related book material is not an alternative implementation:

- [Chapter 2](../../2013-cycle-analytics-for-traders/ch2.md): the EMA market-model building block.
- [Chapter 3](../../2013-cycle-analytics-for-traders/ch3.md), equation 3-3: the same SuperSmoother recurrence, with a generic period rather than BandEdge.
- [Chapter 5](../../2013-cycle-analytics-for-traders/ch5.md): the same fast-attack, slow-decay peak envelope with decay 0.991.
- [Chapter 6](../../2013-cycle-analytics-for-traders/ch6.md): power-spectrum exponents and the effect of differentiation; this highlights the amplitude/PSD distinction in the article.
- [Chapter 7](../../2013-cycle-analytics-for-traders/ch7.md): spectral dilation and Roofing, whose two-pole high-pass is different from the article's finite difference.
- [Chapter 12](../../2013-cycle-analytics-for-traders/ch12.md): Even Better Sinewave deliberately preserves trend components, but uses a recursive single-pole high-pass, fixed 10-bar smoothing, and three-bar amplitude/RMS normalization. It is a different indicator.

## Article authority and initialization

The [article](content.md), corroborated by [TradeStation](tips/UO_indicator.els), defines:

$$w_t=(p_t-p_{t-2})/2,$$

$$a=e^{-\sqrt2\pi/B},\quad c_2=2a\cos(\sqrt2\pi/B),\quad c_3=-a^2,\quad c_1=1-c_2-c_3,$$

$$f_t=c_1(w_t+w_{t-1})/2+c_2f_{t-1}+c_3f_{t-2},$$

$$P_t=\max(0.991P_{t-1},|f_t|),\qquad U_t=f_t/P_t\text{ if }P_t\ne0.$$

The first three filtered values are explicitly zero. The peak is explicitly seeded to **1e-7 on bar 1**, then decays on every accepted bar before comparison. This seed matters on tiny signals; it must not be removed or replaced by a continuing epsilon floor. The previous Universal value is retained if peak is exactly zero.

For a standalone finite sequence, store the first two real raw prices with zero white-noise values. Compute and retain the first real white-noise value on **bar 3**, while still forcing that bar's filter to zero. Bar 4 uses both bar 4 and bar 3 white-noise values in the normal filter recurrence. Hide bars 1–3 as NaN and expose bar 4. This NaN visibility convention is declared by the master; the original plots those zeros and relies on platform price prehistory. The calculations from bar 4 preserve its explicit startup conditions without requiring prices before the supplied sequence.

Only BandEdge is configurable, default 20. The master uses finite real `band_edge >= 2` to respect the two-bar sampling limit; the TradeStation code merely requires positive values. Decay 0.991 and initial peak 1e-7 are fixed source settings. NaN calls omit every state update and count increment; infinite input is rejected.

## Supplied Traders' Tips differences

| Source | Difference | Master choice |
| --- | --- | --- |
| [TradeStation](tips/UO_indicator.els) | Same recurrence, zero first-three filter outputs, and first-bar peak seed; adds positive-parameter validation, alerts, and a separate strategy. | Article and TradeStation are the numeric authority. |
| [eSignal](tips/UO.efs) | Uses `(Close-Close[1])/2` rather than lag 2, and passes a degree-valued angle to JavaScript `Math.cos`, which requires radians. | Retain lag 2 and full-precision radian coefficients. |
| [AmiBroker](tips/UO.afl) | Uses sqrt(2), rounded pi, and null-to-zero averaged input; begins IIR at index 2 without explicitly suppressing three bars, and decays the seed from that loop rather than bar 2. Its null handling makes the first complete averaged input available at index 3. | Explicit article startup and peak decay, full pi. |
| [NinjaTrader](tips/ninja-trader/UniversalOsc.cs) | Seeds both first bars, then writes startup overrides **before** the ordinary Filt assignment, which overwrites them. Consequently nonzero filtering starts on bar 3. | Apply article overrides after calculation, equivalently keep first three Filt values zero. |
| [Updata](tips/UO.updata) | Cosine argument has an extra factor 0.5, changing filter poles. Date-loop startup is shifted. | Use article coefficient and declared bar numbering. |
| [TradersStudio](tips/UO.trs) | Mostly article arithmetic, but `CurrentBar-1` shifts the zero overrides and peak seed relative to its initialization. | Use explicit one-based article startup. |
| [MetaStock](tips/UO.txt) | Peak compares current magnitude with **undecayed** previous peak; startup is expressed with platform-specific Cum/PREV. | Decay first, then compare as the article does. |
| [AIQ](tips/UO.eds) | A ten-day recursion boundary seeds history from closes; envelope history lacks the reset maximum, and output is multiplied by 10. | Preserve the recursively reset peak and dimensionless [-1,1] output. |
| [Wealth-Lab](tips/UO.cs) | Strategy invokes an unavailable `UniversalOscillator.Series` library implementation. | No executable numeric oracle is supplied. |

No mesa source folder is supplied.

## Precision and theory cautions

Use sqrt(2) and pi instead of printed 1.414 and 3.14159. Keep **0.991** and **1e-7** unchanged as chosen algorithmic settings. Exact last-digit equality with truncated constants is incompatible with the requested full precision.

The article alternates between amplitude and power descriptions of pink noise. A strict PSD `1/f` model has amplitude density proportional to `1/sqrt(f)`; a 1/f amplitude spectrum has PSD proportional to `1/f^2`. Its EMA model and 6 dB/octave amplitude argument use the latter convention. Whitening here is approximate equalization, not proof that markets are independent white-noise samples. The differencer and smoothing have phase response, AGC changes shape, and price gaps still create transient responses; the source's zero-lag and gap claims are qualitative observations.

The book AGC derivation prints `10^(-0.75)` for `10^(-1.5/20)`. The correct exponent is -0.075. Its numerical ratio approximately 0.841 and chosen decay 0.991 agree with that correction. The source's decay setting is retained.

Proceed with a new standalone master of this article; the book indicators are not substitutes. All 12 reference-data parameter cases were subsequently confirmed by the user on 2026-10-20.
