# Hilbert Transform Modernization Assessment

Assessment date: **2026-10-25**.

## Findings and recommendation

The 2013 book changes the approach substantially, but it does **not** provide
drop-in replacements for all six copied indicators. Retain the classic
implementations, fix the concrete defects identified below, and introduce the
2013 techniques as distinct alternatives with explicit source identities.

The relevant chapter of *Cycle Analytics for Traders* is
[Chapter 14: The Hilbert Transformer](../2013-cycle-analytics-for-traders/ch14.md).
The requested `ch41.md` is not present; Chapter 14 is the chapter listed in the
[table of contents](../2013-cycle-analytics-for-traders/toc.md).

The copied implementation closely follows the **2001 family**, with configurable
smoothing, custom initialization, and some TA-Lib conventions. That lineage does
not establish exact equivalence to every book listing or current native TA-Lib
output. For example, the homodyne implementations use `atan2`, and the dominant
cycle phase wraps above 360 degrees rather than the book's 315-degree display
boundary. Such choices should be documented and preserved when maintaining
existing reference fixtures.

The most consequential change in 2013 is the author's recommendation to use
**the autocorrelation periodogram for dominant-cycle estimation**, rather than
to replace old Hilbert estimators with the new Chapter 14 estimators.

## Source history

| Source | Relevant approach | Relationship to the copied code |
|---|---|---|
| March 2000, *Hilbert Indicators Tell You When To Trade* | Seven-bar price differencing, recursive in-phase/quadrature calculations, and phase accumulation. | An earlier construction, not the copied seven-tap estimator pipeline. |
| May 2000, *Adaptive Trends And Oscillators* | Six-bar detrending, smoothed in-phase/quadrature components, phase accumulation, and adaptive trend/sine indicators. | Earlier adaptive indicators with different preprocessing and smoothing. |
| 2001, *Rocket Science for Traders*, Chapters 6–7 | Short weighted average, seven-tap Hilbert filters, period-dependent amplitude correction, and three period-estimation methods. | Main mathematical basis of the copied estimator family. |
| 2001, Chapters 9–11 and 17; September 2001 MAMA article | Dominant-cycle phase projection, Sinewave, cycle-length trend averaging, regime rules, and MAMA/FAMA. | Main basis of the five consumers of the estimator family. |
| 2004, *Cybernetic Analysis for Stocks and Futures*, Chapters 9–11 | Retains the seven-tap kernel but uses Cyber Cycle preprocessing, modified amplitude correction, and median-filtered differential phase. | An intermediate methodological change; the copied common estimators are primarily the 2001 variants. |
| 2013, *Cycle Analytics for Traders*, Chapters 8, 11, 12 and 14 | Roofing filters, normalized differencing, autocorrelation periodograms, and Even Better Sinewave. | Distinct alternatives, not a universal update of the classic family. |

In the 2004 cycle-measurement listing, the input smoother uses weights
`(1, 2, 2, 1) / 6`; the cyclic component is extracted with a second-order
recurrence using `alpha=0.07`; amplitude correction is `0.5 + 0.08*InstPeriod[1]`.
Differential phase is limited, median-filtered over five samples, and converted
to period with further smoothing. This is not equivalent to merely changing the
constants of the copied 2001 homodyne estimator.

## What changes in 2013

| Part | Copied implementation / 2001 approach | 2013 approach |
|---|---|---|
| Preprocessing | Short WMA followed by a Hilbert-based detrender. | Two-pole high-pass filter at 48 bars followed by a SuperSmoother. The Chapter 14 modified transformer defaults to a 20-bar SuperSmoother. |
| Quadrature generation | Seven-tap FIR with nonzero coefficients `0.0962`, `0.5769`, `-0.5769`, `-0.0962`; the in-phase component is delayed three bars. | One-bar difference of the peak-normalized real component. |
| Amplitude correction | Feedback factor `0.54 + 0.075*previous_period`. | Independent real and quadrature peak normalizers, each with decay `0.991`. |
| Homodyne calculation | Complex averaging and EMA smoothing, followed by arctangent conversion and period-change limits. | Direct products of normalized components, a small-angle approximation, and a SuperSmoother applied to period. |
| Period limits | Generally 6–50 bars; homodyne and dual differentiator also limit changes to `0.67`–`1.5` times the previous period. Phase accumulation has a separate history restriction. | Intermediate period bounds of 8–48 bars for dual differentiator and 10–48 for homodyne, before final smoothing. |
| Recommended estimator | The 2001 book prefers homodyne among its three methods. | The 2013 book prefers the autocorrelation periodogram. |

The shared FIR operation in the copied code is

$$
\mathcal H_7(x)_t
=0.0962x_t+0.5769x_{t-2}-0.5769x_{t-4}-0.0962x_{t-6}.
$$

The 2013 modified construction instead forms a roofed signal $f_t$ and computes

$$
E^I_t=\max(0.991E^I_{t-1},|f_t|),\qquad I_t=f_t/E^I_t,
$$

$$
d_t=I_t-I_{t-1},\qquad
E^Q_t=\max(0.991E^Q_{t-1},|d_t|),\qquad Q_t=d_t/E^Q_t.
$$

These source equations require a startup convention when a peak denominator
is zero; the existing prepared master supplies that convention. The independent
gain controls make the revised construction nonlinear. It is not simply a more
accurate FIR approximation to an ideal Hilbert transform.

The first difference has frequency response

$$
1-e^{-i\omega}
=2i\sin(\omega/2)e^{-i\omega/2}.
$$

For positive frequencies below Nyquist, its phase lead is
$\pi/2-\omega/2$: there is half a bar of delay relative to an ideal derivative.
Peak normalization compensates amplitude variation approximately; it does not
remove this phase delay or the preceding roofing filter's phase response.
On changing, noisy prices, exact orthogonality and constant complex magnitude
are not guaranteed.

Listing 14-3 further smooths the normalized quadrature with a 10-bar
SuperSmoother. The book explicitly states that this added smoothing **destroys
orthogonality** by introducing more lag. It makes the plotted waveform easier
to use, but that smoothed plotting output should not become the shared I/Q
source for period estimation.

The revised homodyne listing also changes the conversion from a product angle
to period. The copied code uses an arctangent; Listing 14-6 uses
$2\pi/|\operatorname{Im}/\operatorname{Re}|$, relying on a small-angle
approximation. These formulas differ even for ideal components. Changing only
the front end therefore would not reproduce the 2013 listing.

### The author's change of recommendation

In Chapter 14's section on using the transformer to compute dominant cycle,
Ehlers writes **“do not use the code for trading”** and says the autocorrelation
periodogram is a superior approach. The Chapter 11 key points repeat the
preference for the periodogram. The Chapter 14 period methods are included
primarily for completeness and research.

This is the author's assessment, not a trading-performance result independently
established by this investigation. Publication date alone does not demonstrate
that replacing an existing estimator improves performance on a particular
market or strategy.

The supplied 2013 text also contains numerical ambiguities. For example,
Listing 14-5 limits differential phase to 10–48 **degrees per bar**, while its
comment describes cycle-period bounds; these are not the same units. The
periodogram's local Chapter 8 listing uses a 370-degree Fourier angle and its
AGC prose differs from its code. The prepared periodogram reference documents
its explicit resolutions. Blindly copying the newer listings is insufficient
to define a consistent numerical reference.

## Assessment of the six implementations

| Implementation | Recommendation | Compatibility and integration implications |
|---|---|---|
| `hilbert_transformer` | Retain the classic homodyne, phase-accumulator and dual-differentiator methods, including the unrolled homodyne variant. Fix the defects below. Use a separate 2013 transformer component for normalized Real/Imag outputs. | Replacing the common front end changes all five dependent indicators. The Chapter 14 period estimators should be explicitly identified as research variants. |
| `dominant_cycle` | **Highest modernization priority:** introduce an autocorrelation-periodogram period source while retaining the classic implementation. | A periodogram supplies spectral power and a period estimate, not the existing phase. Combining its period with the old phase projection is a hybrid construction and must be identified as such. |
| `sine_wave` | Introduce **Even Better Sinewave** as a separate indicator. | It eliminates cycle and phase estimation entirely. Its scalar normalized-wave output does not replace the current sine, 45-degree lead, period and phase outputs. |
| `hilbert_transformer_instantaneous_trend_line` | Retain the classic definition; consider an alternative period provider. Use the separate **Decycler** for the book's 2013 trend-line approach. | The current indicator averages price over a measured cycle length, then smooths those averages. A Decycler is a different recurrence and does not produce the same dominant-cycle-period output. |
| `mesa_adaptive_moving_average` | Preserve MAMA/FAMA's mathematical definition. | The 2013 book does not supply a replacement MAMA. Its half-cycle phase snapback creates its ratcheting action; changing to an unwrapped phase changes the indicator. |
| `trend_cycle_mode` | Retain the classic classifier; evaluate any newer regime classifier separately. | Its phase-rate, sine-crossing and price-separation rules depend on the old signal definitions. Hurst or spectral measures are alternatives, not equivalent binary classifiers. |

### Why there is no universal estimator substitution

The current interfaces couple cycle-period estimation to Hilbert-specific
outputs. Actual dependencies are narrower in some consumers:

| Consumer | Information it uses |
|---|---|
| MAMA | In-phase and quadrature components for phase; raw price for the moving averages. |
| Hilbert-based instantaneous trend line | Estimated period; its own raw-price history. |
| Dominant cycle | Estimated period and WMA-smoothed price history for a separate phase projection. |
| Sinewave | Dominant-cycle period and projected phase. |
| Trend/cycle mode | Dominant-cycle period, projected phase and smoothed price, plus its own price-average trend line. |

A period-only provider would allow the trend line to consume a periodogram
without requiring the periodogram to implement Hilbert I/Q methods. Keep an
I/Q provider for MAMA. Period estimation and phase projection should remain
distinct responsibilities when introducing alternatives.

In particular, feeding normalized or roofed values into the current
TrendCycleMode's 1.5% separation rule changes the signal's units and its meaning.
Its trend line is in price units. Such a substitution requires a newly defined
classifier and separate validation, not just a different estimator enum value.

### MAMA's phase snapback is intentional

The existing MAMA obtains phase with an arctangent whose range is one half
cycle. It computes the previous phase minus the current phase and limits that
change to at least one degree. The resulting large fast-limit updates at phase
snapbacks create MAMA's characteristic ratcheting behavior.

Both the 2001 book and September 2001 article explain this behavior explicitly.
Replacing the arctangent with a full-circle or continuously unwrapped phase
calculation as a generic numerical cleanup would alter MAMA. A MAMA-like filter
using the 2013 normalized transformer would be a research variant, not a
published 2013 revision of MAMA.

## Existing references to reuse

| Existing implementation or master | Relevant capability | Remaining work for modernization |
|---|---|---|
| [Copied autocorrelation periodogram](../../../external/zpano/py/indicators/john_ehlers/auto_correlation_periodogram/auto_correlation_periodogram.py) | Computes the spectrum and exposes a heatmap. | It currently does not expose a dominant-cycle centroid. Its display normalization should not define centroid weights. |
| [Prepared autocorrelation periodogram](auto-correlation-periodogram/description.md) | Exposes both heatmap and dominant-cycle centroid, with an explicit `source="book"` variant. | Port/integrate the selected source variant and its documented initialization and numerical conventions. |
| [Prepared Hilbert Transformer Indicator](hilbert-transformer-indicator/description.md) | Implements Listing 14-3 and the raw-quadrature Listing 14-2 variant through `smooth_imaginary=False`. | Port/integrate as a distinct Real/Imag indicator. It is not a period estimator and should not replace the classic shared estimator automatically. |
| [Prepared Even Better Sinewave](even-better-sinewave/description.md) | Implements Chapter 12's normalized modified-roofing-filter waveform. | Port/integrate as a separate scalar indicator. |
| [Prepared Decycler](decycler/description.md) | Implements Chapter 4's one-pole trend filter. | Port/integrate as a distinct trend-line alternative. |
| [Prepared Hurst coefficient](hurst-coefficient/description.md) | Implements Chapter 6's finite-window range-based measure. | Evaluate any proposed regime interpretation separately from the classic trend/cycle classifier. |

The prepared transformer master was also found while preparing this written
report. Both of its published quadrature variants already exist, so a new
research implementation of those variants is unnecessary.

The periodogram's
[source and implementation investigation](auto-correlation-periodogram/investigation.md)
documents differences between the copied spectrum-only implementation and the
2013/2016 sources. Use that investigation when selecting a source identity;
adding a centroid to a display-normalized heatmap alone would not reproduce
the book calculation.

## Confirmed defects and an inherited limitation

### 1. Dual differentiator: unguarded denominator

Both calculation paths in
[dual_differentiator_estimator.py](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/dual_differentiator_estimator.py)
divide by `discriminator` without checking it. Their later NaN/infinity checks
cannot catch a Python `ZeroDivisionError` that has already been raised.

With default `CycleEstimatorParams`, constant inputs of **0, 1 and 100** all
raise `ZeroDivisionError` on the **23rd accepted sample**. The original 2001
listing guards its denominator. This is a correctness defect independently
of any choice to adopt a newer technique. The fix must define denominator
handling before division and test both initialization and steady-state paths.

### 2. Phase accumulator: incorrect quadrant-wrap threshold

In
[phase_accumulator_estimator.py](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/phase_accumulator_estimator.py),
the wraparound condition compares the current phase with
`3*math.pi/4`, or **135 degrees**. The source condition specifies a current
phase above **270 degrees**, or `3*math.pi/2`, when the preceding phase is below
90 degrees.

For a preceding phase of 45 degrees and current phase of 180 degrees, the
implementation incorrectly adds a full turn and produces a maximum-clamped
60-degree advance. With the intended wrap condition, the negative difference
is instead minimum-clamped to approximately 7.2 degrees under the current
configured 50-bar bound. This defect can affect responses to erratic phase
changes even though clean-sinusoid tests pass.

### 3. Phase accumulator: 40-sample history versus an advertised 50-bar bound

The shared
[estimator helpers](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/estimator.py)
declare `ACCUMULATION_LENGTH=40`, while the estimator reports `max_period=50`.
Forty exact differential phases from a 41–50-bar cycle do not accumulate one
full turn, so the period helper holds the previous estimate.

This is **an inherited design restriction**, not simply a missing feature in
the port. The 2001 book explains its assumption that sufficiently long cycles
are trend mode and detailed period measurement is unnecessary. The existing
interface and tests nevertheless imply a wider measurable range than that
history supports. Document the restriction, or introduce an explicitly extended
variant with new reference data; do not silently change historical behavior.

## Validation evidence

All **140 existing tests** across the four estimator implementations and five
consumer indicators passed during the assessment. These passing tests do not
cover the two defects described above. No native TA-Lib runtime comparison was
performed, so the result establishes agreement with the repository's tests,
not independent proof of complete native TA-Lib compatibility.

Additional read-only probes used the standard library and the copied classes.
For the following clean-sinusoid experiment:

- Input was `100 + sin(2*pi*t/period)` for 1,000 chronological samples,
  with zero-based `t=0..999`.
- Every estimator used the generic default `CycleEstimatorParams()`;
  all quadrature and period smoothing factors were therefore 0.2.
- The reported value is the median estimate over samples 501–1,000.
- These are illustrative measurements on noiseless synthetic signals, not
  results of a comparison with the 2013 methods or a trading benchmark.

| Input period | Homodyne | Unrolled homodyne | Phase accumulator | Dual differentiator |
|---:|---:|---:|---:|---:|
| 10 | 10.102 | 10.102 | 10.529 | 10.919 |
| 20 | 20.005 | 20.005 | 20.492 | 20.347 |
| 30 | 29.997 | 29.997 | 30.513 | 30.221 |
| 40 | 40.008 | 40.008 | 40.000 | 40.292 |
| 48 | 48.037 | 48.037 | 38.222 | 48.041 |
| 50 | 49.805 | 49.805 | 38.454 | 49.556 |

The classic homodyne estimator remains accurate under these favorable
conditions. The phase accumulator's long-period limitation is visible, despite
its existing maximum-period test passing with a tolerance of 12.5 bars.

The direct accumulation helper was also tested with 40 identical differential
phases `2*pi/period` and previous estimate 6. It returned 20, 30 and 40 for
those respective periods, but held 6 for periods 41, 48 and 50. Flat-price and
quadrant-jump probes reproduced the two defects as described above.

The assessment did not execute a comparative noise study of the 2001 and 2013
pipelines, a strategy backtest, or a profitability evaluation. Future comparisons
should use matched inputs and initialization, fixed periods, chirps, abrupt
period changes, trends, amplitude changes and controlled noise. Keep classic
reference-fixture validation separate from evaluating a new algorithm's quality.

## Recommended priorities

1. Fix the dual-differentiator denominator handling and phase-wrap threshold,
   with regressions for flat inputs and quadrant jumps. Document the inherited
   phase-accumulation range limitation.
2. Integrate the prepared periodogram's dominant-cycle output. For a 2013-based
   alternative, select its documented `source="book"` mode explicitly rather
   than inheriting the master's 2016 article default.
3. Integrate the already prepared Even Better Sinewave and modified Hilbert
   Transformer Indicator as separate indicators.
4. Evaluate a periodogram-driven trend-line variant and the existing Decycler
   reference. Any old phase projection combined with a periodogram is a hybrid.
5. Preserve MAMA and the classic trend/cycle definition while independently
   evaluating alternatives. Changes to their phase conventions, units, or
   thresholds require new numerical references and behavioral validation.

This document records an assessment and proposed priorities. Creating it does
not modify any indicator or expected output arrays.

## Sources and inspected implementations

### Books and articles

- [Rocket Science for Traders, contents](../2001-rocket-science-for-traders/toc.md):
  [Chapter 6, Hilbert Transforms](../2001-rocket-science-for-traders/ch6.md),
  [Chapter 7, Measuring Cycle Periods](../2001-rocket-science-for-traders/ch7.md),
  [Chapter 9, The Sinewave Indicator](../2001-rocket-science-for-traders/ch9.md),
  [Chapter 10, Instantaneous Trendline](../2001-rocket-science-for-traders/ch10.md),
  [Chapter 11, Identifying Market Modes](../2001-rocket-science-for-traders/ch11.md),
  and [Chapter 17, MAMA](../2001-rocket-science-for-traders/ch17.md).
- [Cybernetic Analysis for Stocks and Futures, contents](../2004-cybernetic-analysis-for-stocks-and-futures/toc.md):
  [Chapter 9, Measuring Cycles](../2004-cybernetic-analysis-for-stocks-and-futures/ch9.md),
  [Chapter 10, Adaptive Indicators](../2004-cybernetic-analysis-for-stocks-and-futures/ch10.md),
  and [Chapter 11, The Sinewave Indicator](../2004-cybernetic-analysis-for-stocks-and-futures/ch11.md).
- [Cycle Analytics for Traders, contents](../2013-cycle-analytics-for-traders/toc.md):
  [Chapter 4, Decyclers](../2013-cycle-analytics-for-traders/ch4.md),
  [Chapter 8, Autocorrelation](../2013-cycle-analytics-for-traders/ch8.md),
  [Chapter 11, Adaptive Filters](../2013-cycle-analytics-for-traders/ch11.md),
  [Chapter 12, Even Better Sinewave](../2013-cycle-analytics-for-traders/ch12.md),
  and [Chapter 14, The Hilbert Transformer](../2013-cycle-analytics-for-traders/ch14.md).
- [March 2000: Hilbert Indicators Tell You When To Trade](../tasc/2000-03-hilbert-indicators-tell-you-when-to-trade/content.md).
- [May 2000: Adaptive Trends And Oscillators](../tasc/2000-05-adaptive-trends-and-oscillators/content.md).
- [September 2001: MESA Adaptive Moving Averages](../tasc/2001-09-mesa-adaptive-moving-averages/content.md).

### Copied implementations

- [Common helpers and factory](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/estimator.py),
  [common interface](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/cycle_estimator.py),
  [parameters](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/cycle_estimator_params.py),
  [homodyne](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/homodyne_discriminator_estimator.py),
  [unrolled homodyne](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/homodyne_discriminator_estimator_unrolled.py),
  [phase accumulator](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/phase_accumulator_estimator.py),
  and [dual differentiator](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer/dual_differentiator_estimator.py).
- [Dominant cycle](../../../external/zpano/py/indicators/john_ehlers/dominant_cycle/dominant_cycle.py).
- [Hilbert-based instantaneous trend line](../../../external/zpano/py/indicators/john_ehlers/hilbert_transformer_instantaneous_trend_line/hilbert_transformer_instantaneous_trend_line.py).
- [MAMA/FAMA](../../../external/zpano/py/indicators/john_ehlers/mesa_adaptive_moving_average/mesa_adaptive_moving_average.py).
- [Sinewave](../../../external/zpano/py/indicators/john_ehlers/sine_wave/sine_wave.py).
- [Trend/cycle mode](../../../external/zpano/py/indicators/john_ehlers/trend_cycle_mode/trend_cycle_mode.py).
