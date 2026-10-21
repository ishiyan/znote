# Swami Relative Strength Index: research prototype master

Master: `swami-relative-strength-index.py`, class `SwamiRelativeStrengthIndex`. One accepted chronological update returns a heatmap column. This is the authoritative standalone conversion contract for this folder.

## What a SwamiChart measures

A SwamiChart is a bank of related indicators evaluated at many observation or cycle periods. Its horizontal axis is time and its vertical axis is the period parameter. One streaming update produces one vertical column. Shorter periods usually react earlier but respond to smaller fluctuations; longer periods reveal persistence with more lag. Reading the shorter-period response in the context of longer-period responses is the central idea in the March article and Chapter 16. It makes parameter sensitivity visible instead of choosing one allegedly optimal period.

This resembles a measuring instrument with several selectable time constants, all read simultaneously. For a filter bank it also resembles a collection of resonators tuned to different frequencies. It is not automatically an estimate of spectral power: the vertical parameter means lookback or cycle period as defined below, and the values are normalized indicator responses. Adjacent rows use highly overlapping data and are not independent observations. A colored pattern does not by itself supply a statistical test, calibrated probability, trading rule, or proof of predictive value.

Let $v_t(P)$ be the numerical response at bar $t$ and period $P$. For integer periods $P_0,\ldots,P_1$, the column is

$$\mathbf v_t=[v_t(P_0),v_t(P_0+1),\ldots,v_t(P_1)].$$

Except for Convolution's signed representation, the conventional stoplight palette maps $v\in[0,1]$ to RGB channels:

$$
(R,G,B)=
\begin{cases}
(255,510v,0),&v<1/2,\\
(510(1-v),255,0),&v\ge1/2.
\end{cases}
$$

Thus 0 is red, 0.5 yellow, and 1 green. The numerical master returns values rather than RGB integers. Platform rounding of channel values and interpolation between rows belongs to rendering. The original Swing Wave uses blue/orange and Convolution uses signed red/green intensity; see their specific equations below. Palette changes alone do not warrant new indicator folders.

## Streaming and heatmap contract

The Python file in this folder is self-contained and uses the standard library only. Copying this folder is sufficient; there are no runtime imports from other prepared masters or zpano. Numerical helpers above the fixture-tooling separator are the parts to port. Lists implement bounded newest-first histories; a port may use circular buffers but must preserve the logical order of all sums and comparisons.

`Heatmap` is a named tuple compatible with the requested fields in `external/zpano/py/indicators/core/outputs/heatmap.py`:

| Field | Meaning |
| --- | --- |
| `time` | Optional caller timestamp; does not affect the calculation. |
| `parameter_first`, `parameter_last` | Inclusive first and last displayed periods. |
| `parameter_resolution` | 1.0; row $i$ is $P_0+i$. |
| `value_min`, `value_max` | Actual minimum and maximum of this column, not fixed palette endpoints. |
| `values` | Fresh list of $P_1-P_0+1$ values, independently owned. |

Until the entire selected bank is available, return an empty values list with NaN min/max. During reference export only, expand that empty column to the full row width filled with NaNs. A map is wholly available or wholly unavailable; this avoids differently primed rows within the same public column. `warmup_bars` counts the leading unavailable finite-input observations. `is_primed` reports complete-bank availability, not convergence of recursive transients.

A NaN input means an omitted observation: return an empty public column and preserve every history, retained value, and accepted-bar count. The next finite input follows the preceding finite input, regardless of timestamps. Infinity and invalid OHLC order raise `ValueError` before any normal update. Finite negative or zero prices are accepted. As in the source listings, arithmetic assumes finite, ordinary-magnitude financial samples; extreme finite magnitudes can overflow intermediate arithmetic and are outside the reference-data domain. `reset()` restores all histories, seeds and counters. A missing input must never be saved as NaN recursive state.

## Precision and source fidelity

Use IEEE 754 binary64, full-precision $\pi$ and $\sqrt2$, and radian trigonometric functions. Convert an EasyLanguage degree argument $a$ to $a\pi/180$. Replace printed `1.414` with $\sqrt2$, `.707` with $1/\sqrt2$ where applicable, and `3.14159` or `6.28` with $\pi$ or $2\pi$. This is the requested precision convention, so fixtures cannot also match every decimal of a platform running the rounded printed constants.

Explicit EMA weights `.33/.67`, `.5/.5`, `.2/.8`, CCI's `.015`, and Convolution's contrast factor 3 remain the source constants. In particular, `.33` is not silently replaced by $1/3$. Do not round intermediates. Export alone uses **15 significant digits**, Python `.15g`, rather than 15 digits after the decimal point. Go, Rust, Zig and other math libraries may differ in their last bits; compare finite fixture values with a suitable relative/absolute tolerance such as $10^{-11}$, while matching NaN positions exactly.

Chart platforms choose historical availability, MaxBarsBack, seeds, and invocation timing differently. This master defines a standalone startup explicitly below: actual raw differences, zero recursive seeds, and actual complete finite windows. It preserves the source recurrence and the documented degenerate branches, rather than claiming a unique cross-platform first-bar oracle. Independent tests evaluate the selected source formulas over the same standalone history convention, including startup. The documented corrections or extensions are part of the conversion contract.

## Reference-data workflow

All five shared input files are copied into this folder: `test_testdata.py`, `testdata_test.go`, `testdata.ts`, `testdata.rs`, and `testdata.zig`. The master `__main__` embeds the exact 252 shared close/high/low values and demonstrates the default. Run `python3 swami-relative-strength-index.py` for that demonstration. The user confirmed all 56 Swami combinations on 2026-10-21, including the eight combinations in this folder. The source flag `REFERENCE_CASES_CONFIRMED` records that authorization and is true. All five language fixtures now contain 24 generated expected arrays for the eight cases.

To regenerate the confirmed data, run `python3 swami-relative-strength-index.py --generate-reference-data`. The generator appends a marked expected-data section to Python, reopens and verifies every rounded value, NaN and dimension, then translates those verified Python literals to the other four languages. Regeneration replaces only that marked section and preserves all inputs. Run `python3 verify_reference_data.py` to check the resulting values, names, comments, shapes and NaN masks in all five languages. [validation.md](validation.md) records completed checks and [reference_manifest.json](reference_manifest.json) records the full fixture inventory. Each array contains 252 time positions; heatmaps and per-period diagnostics have a second dimension equal to the bin count. Every array has two comments: the exact What it tests description below, then parameter values and input convention.

Names are `EXPECTED_<parameter tokens>_<component>`. Period bounds use `P0`, `P1`; variants use `V2012` and `V2013`; `LP/HP` are filter periods; `RA/OA/A` are EMA weights; `C` is RSI contrast; `D/F/PA` are bandwidth, fraction and peak-average length. Decimal points become underscores. For example `EXPECTED_V2013_P05_P148_LP10_5_HEATMAP` identifies the fractional roofed case. Unspecified parameters take the documented defaults; the comments list every explicitly varied parameter and the source input convention.

Python uses `NaN = math.nan`, Go `math.NaN()`, TypeScript `NaN`, Rust `f64::NAN`, and Zig `nan` with `const math = @import("std").math; const nan = math.nan(f64);`. Go packages use the folder name with hyphens/underscores removed. Go/TypeScript/Zig expected names begin `expected` with uppercase shortcuts; Rust functions begin `expected_` with lowercase tokens. TypeScript exports valid typed constants; Rust returns vectors; Zig returns `[252]f64` or `[252][bins]f64`. These are compilable versions of the intended language formats.

## Roofing and SuperSmoother mathematics

Ehlers describes market prices as having spectral dilation: slower components often have larger amplitudes and can dominate oscillators meant to describe shorter cycles. The roofing stage is analogous to placing a detrending circuit and a noise-removal circuit ahead of an instrument. A two-pole high-pass rejects DC and attenuates slow components; the following SuperSmoother attenuates very short periods. Together they pass a gradual band of cycles, not an ideal rectangular frequency band.

Let $x_t$ be input, $H$ the longest-period coefficient control, and $L$ the shortest-period coefficient control. In Chapter 16 use $\theta=\sqrt2\pi/H$, the precise form of `.707*360/H` degrees. In **Convolution listing 13-1 use $\theta=2\sqrt2\pi/H$**, the precise form of `1.414*360/H` degrees. The latter is a factor of two larger and is intentionally preserved. Define

$$\alpha=\frac{\cos\theta+\sin\theta-1}{\cos\theta},\quad q=1-\alpha,\quad g=1-\alpha/2.$$

Using $u=\tan(\theta/2)$ and the half-angle sine/cosine identities gives

$$\alpha=\frac{2u}{1+u}.$$

The master uses this algebraically equivalent expression to avoid a removable $0/0$ at $\theta=\pi/2$ and cancellation near zero. Its admitted angles satisfy $0<\theta<\pi$, giving $|q|<1$. The source two-pole recurrence is

$$h_t=g^2(x_t-2x_{t-1}+x_{t-2})+2qh_{t-1}-q^2h_{t-2}.$$

The two DC zeros remove a sustained linear trend after startup transients; the repeated pole controls the memory. The explanatory transfer function is

$$H_{HP}(z)=\frac{g^2(1-z^{-1})^2}{(1-qz^{-1})^2}.$$

Chapter 3 equation 3-3 supplies the SuperSmoother coefficients:

$$\omega=\frac{\sqrt2\pi}{L},\quad a=e^{-\omega},\quad c_2=2a\cos\omega,\quad c_3=-a^2,\quad c_1=1-c_2-c_3.$$

Apply them to the high-pass output:

$$f_t=\frac{c_1(h_t+h_{t-1})}{2}+c_2f_{t-1}+c_3f_{t-2}.$$

The numerator average supplies a Nyquist zero. Its transfer function is

$$H_{SS}(z)=\frac{(c_1/2)(1+z^{-1})}{1-c_2z^{-1}-c_3z^{-2}},\qquad H_{Roof}(z)=H_{HP}(z)H_{SS}(z).$$

Short periods are high frequencies and long periods are low frequencies. Do not reverse the meanings of the two cutoffs while converting. Keep the sign of $c_3$ negative and add its signed product in the recurrence. No adaptive dominant period is measured here.

The first two accepted prices are stored without fabricating raw prehistory. On bar 3 the first real second difference produces the first finite internal $f_t$; $h$ and $f$ prehistory are zero. Every later filtered value, including values hidden by public bank warm-up, advances the histories. Book RSI/Stochastic share $c_1,c_2,c_3$ between roofing and the final per-bin smoother. This differs from importing a standalone Roofing indicator and feeding only its already-visible outputs into each bin.

## Selected sources and algorithm variants

`SwamiRelativeStrengthIndex` defaults to Chapter 16 listing 16-1, `roofed_2013`. `classic_2012` follows the March TradeStation `_SwamiChart_RSI`. They use different sources of data, averaging rules and smoothing; construct a new instance to change variants. Roofed is a finite-window RSI on filtered changes, while classic uses Wilder-style recursive net/absolute change averages with fourfold contrast. Neither silently delegates to the existing MyRSI master or a platform RSI built-in.

## Classic 2012 calculation

Let $\Delta_t=x_t-x_{t-1}$. For each $P$,

$$n_t(P)=n_{t-1}(P)+\frac{\Delta_t-n_{t-1}(P)}P,$$
$$d_t(P)=d_{t-1}(P)+\frac{|\Delta_t|-d_{t-1}(P)}P,$$
$$r_t(P)=\begin{cases}n_t(P)/d_t(P),&d_t(P)\ne0,\\0,&d_t(P)=0.\end{cases}$$

This signed ratio is in $[-1,1]$ under ordinary arithmetic. The ordinary non-amplified RSI scaling would be $(1+r)/2$. The source instead uses contrast $C=4$ and output EMA weight $a=.33$:

$$\widetilde v_t(P)=a\frac{Cr_t(P)+1}{2}+b\,v_{t-1}(P),\qquad v_t(P)=\min(1,\max(0,\widetilde v_t(P))),$$

where $b=.67$ at the default $a=.33$, preserving the two explicit printed weights; for configurable nondefault $a$, $b=1-a$. Net change, absolute change and clipped output start at zero. Clip after the EMA and save that clipped state. Do not seed with an initial SMA, use a finite window, remove contrast, or clamp the contrast-amplified target before smoothing. Flat input uses $r=0$ and the EMA approaches .5 from its zero seed.

## Roofed 2013 calculation

Use the Chapter 16 roofing formula above. For each $P$, sum exactly $P$ filtered changes, requiring $P+1$ actual filtered values:

$$U_t(P)=\sum_{j=0}^{P-1}\max(f_{t-j}-f_{t-j-1},0),\qquad D_t(P)=\sum_{j=0}^{P-1}\max(f_{t-j-1}-f_{t-j},0).$$

Then

$$r_t(P)=\begin{cases}U_t(P)/(U_t(P)+D_t(P)),&U_t(P)+D_t(P)\ne0,\\r_{t-1}(P),&U_t(P)+D_t(P)=0.\end{cases}$$

There is no ELSE in listing 16-1: retain the previous ratio on an exactly flat window, initially zero. Apply the same coefficients as roofing's low-pass:

$$\widetilde v_t(P)=\frac{c_1(r_t(P)+r_{t-1}(P))}{2}+c_2v_{t-1}(P)+c_3v_{t-2}(P),\qquad v_t(P)=\min(1,\max(0,\widetilde v_t(P))).$$

The clipped output feeds the future recurrence. The flat-window book RSI therefore remains at zero from a fully flat zero-filter history, unlike the book stochastic's documented neutral extension. The two oscillators can reveal similar patterns without being mathematically identical.

## Configuration and startup

| Parameter | Default | Valid range and role |
| --- | --- | --- |
| `variant` | `roofed_2013` | `classic_2012` or `roofed_2013`. |
| `min_period` | 5 roofed; 12 classic | Integer $\ge1$; `None` selects variant default. |
| `max_period` | 48 | Integer $\ge P_0$. |
| `alpha` | .33 | $(0,1]$, classic output EMA weight. |
| `contrast` | 4 | Finite real $\ge0$, classic signed-ratio amplification. |
| `shortest_cycle_period` | 10 | Finite real $L\ge2$, both roofed SuperSmoothers. |
| `longest_cycle_period` | 48 | Finite real $H>L$, roofed HP. |

Inactive-variant parameters must remain at defaults. Classic recurrences start with the first actual price difference on bar 2. Expose the bank after $P_1$ actual changes on bar $P_1+1$, so `warmup_bars=P1`; this is an explicit visibility policy for recursive averaging, not a change to its recurrence. Roofed bin $P$ starts on bar $P+3$ when $P+1$ filtered values exist. After three final-smoother updates in the last bin, the bank is first visible on bar $P_1+5$, so `warmup_bars=P1+4`. Defaults first expose on bar 49 classic and bar 53 roofed.

## Calculation flow

```mermaid
flowchart TD
    A[Receive close] --> B{Finite input?}
    B -- NaN --> X[Empty column; preserve state]
    B -- Infinity --> E[Reject]
    B -- Yes --> V{Variant}
    V -- Classic --> C[Actual close difference; update net and absolute Wilder averages]
    C --> D[Guard ratio; amplify contrast; EMA; clip and store]
    V -- Roofed --> R[Update roofing; append actual filtered value]
    R --> W[For each complete P-change window sum gains and losses]
    W --> Q[Guard ratio by retaining prior value; final SuperSmoother; clip and store]
    D --> P{Whole bank primed?}
    Q --> P
    P -- No --> X
    P -- Yes --> O[Fresh heatmap column]
```

## Confirmed reference combinations (2026-10-21)

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `variant=classic_2012, min_period=12, max_period=48` | Original 2012 Wilder-style changes with fourfold contrast. |
| 2 | `variant=classic_2012, min_period=12, max_period=48, contrast=1.0` | Classic ratio without amplified contrast. |
| 3 | `variant=classic_2012, min_period=12, max_period=24, alpha=0.1` | Compact classic bank with slower output EMA. |
| 4 | `variant=classic_2012, min_period=1, max_period=1` | Single one-change classic RSI boundary. |
| 5 | `variant=roofed_2013, min_period=5, max_period=48` | Book 2013 roofed default bank of finite-window gain/loss ratios. |
| 6 | `variant=roofed_2013, min_period=5, max_period=24` | Compact book bank and correct extra price for P changes. |
| 7 | `variant=roofed_2013, min_period=5, max_period=48, shortest_cycle_period=10.5` | Fractional book low-pass coefficient period without rounding. |
| 8 | `variant=roofed_2013, min_period=5, max_period=48, shortest_cycle_period=20.0, longest_cycle_period=80.0` | Slower book roofing band and output smoothing. |

Unlisted parameters retain the configuration-table defaults. Each case exports `HEATMAP`, `MIN` and `MAX`.

## References and BibTeX

These references supply the theory, formulas, source comparisons and archived presentation notes above. All numerical steps needed for conversion are included in this document; the following links are provenance rather than runtime dependencies.

- Ehlers and Way, March 2012, [Introducing SwamiCharts](../../tasc/2012-03-introducing-swami-charts/content.md), and [March TradeStation code](../../tasc/2012-03-introducing-swami-charts/tips/SwamiCharts.els).
- Ehlers and Way, April 2012, [Setting Strategies With SwamiCharts](../../tasc/2012-04-setting-strategies-with-swami-charts/content.md), and [April Trader's Tips](../../tasc/2012-04-setting-strategies-with-swami-charts/tips/tips.md).
- Ehlers and Way, October 2012, [SwamiCharts Convolution](../../tasc/2012-10-swami-charts-convolution/content.md).
- Ehlers, 2013, *Cycle Analytics for Traders*: [Chapter 3](../../2013-cycle-analytics-for-traders/ch3.md) (SuperSmoother), [Chapter 5](../../2013-cycle-analytics-for-traders/ch5.md) (band-pass), [Chapter 7](../../2013-cycle-analytics-for-traders/ch7.md) (spectral dilation), [Chapter 13](../../2013-cycle-analytics-for-traders/ch13.md) (Convolution listing 13-1), and [Chapter 16](../../2013-cycle-analytics-for-traders/ch16.md) (Swami RSI/Stochastic listings 16-1/16-2).
- [Archived SwamiRSI page](../../../../external/swami/SwamiRSI.mht), a description/screenshot source with no numerical implementation.
- [NinjaTrader BPF](../../tasc/2012-04-setting-strategies-with-swami-charts/tips/ninja-trader/BPF.cs) and [SwamiWave](../../tasc/2012-04-setting-strategies-with-swami-charts/tips/ninja-trader/SwamiWave.cs), for the selected Swing Wave variant.

```bibtex
@article{ehlers_way_2012_swami_intro,
  author = {Ehlers, John F. and Way, Ric},
  title = {Introducing SwamiCharts},
  journal = {Technical Analysis of STOCKS \& COMMODITIES},
  volume = {30}, number = {3}, pages = {15--22}, year = {2012}, month = mar
}
@article{ehlers_way_2012_swami_strategies,
  author = {Ehlers, John F. and Way, Ric},
  title = {Setting Strategies With SwamiCharts},
  journal = {Technical Analysis of STOCKS \& COMMODITIES},
  volume = {30}, number = {4}, year = {2012}, month = apr
}
@article{ehlers_way_2012_swami_convolution,
  author = {Ehlers, John F. and Way, Ric},
  title = {SwamiCharts Convolution},
  journal = {Technical Analysis of STOCKS \& COMMODITIES},
  volume = {30}, number = {10}, pages = {10--13}, year = {2012}, month = oct
}
@book{ehlers2013cycle,
  author = {Ehlers, John F.},
  title = {Cycle Analytics for Traders: Advanced Technical Trading Concepts},
  publisher = {Wiley}, year = {2013}, isbn = {9781118728604}
}
@misc{traders_tips_2012_march,
  author = {{Technical Analysis of STOCKS \& COMMODITIES}},
  title = {Traders' Tips: March 2012}, year = {2012}, month = mar,
  url = {https://www.traders.com/Documentation/FEEDbk_docs/2012/03/TradersTips.html},
  note = {Includes TradeStation listings by Chris Imhof and differing vendor implementations}
}
@misc{traders_tips_2012_april,
  author = {{Technical Analysis of STOCKS \& COMMODITIES}},
  title = {Traders' Tips: April 2012}, year = {2012}, month = apr,
  url = {https://www.traders.com/Documentation/FEEDbk_docs/2012/04/TradersTips.html},
  note = {Includes NinjaTrader SwamiWave/BPF and OmniTrader SwamiMM/OptimizedMarketMode by Jeremy Williams}
}
@misc{swami_archived_product,
  author = {{Securities Analytics, Inc.}},
  title = {SwamiCharts Archived Product Pages},
  howpublished = {Repository-local MHT snapshots in external/swami},
  note = {Descriptions and screenshots; snapshot footer copyright 1998--2011 does not establish the capture date}
}
```
