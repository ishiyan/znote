# SuperSmoother and Roofing Filter: implementation investigation

Investigation date: 2026-10-20. Scope: the two requested filters, their article and book definitions, and the copied Python implementations. This report precedes the master preparation procedure; it does not change either copied implementation or generate conversion fixtures. The article's third indicator is MESA Stochastic.

## Decision

The SuperSmoother's numeric core is suitable for reuse. It implements book equation 3-3 with full-precision constants. Its initialization and output availability are additional implementation choices, not rules specified by that equation.

The Roofing Filter implements the recurrences of all three variants in book chapter 7, but is not ready to be the requested full-precision master as supplied. Its SuperSmoother stage uses `1.414`; its default selects the book's preliminary one-pole variant rather than the article's two-pole filter; and its startup handling needs an explicit specification. There is also a parameter boundary error in the one-pole high-pass coefficient calculation.

Standalone preparation packages are recommended for **both** filters, reusing the existing numeric work. There is no need to invent new filtering algorithms. The packages are needed to make the code executable independently, preserve the source theory, define initialization precisely, and provide accurate 252-sample fixtures in all five requested languages. The copied fixtures are not adequate substitutes.

## Sources located in the book

- [Chapter 3, Smoothing Filters on Steroids](../../2013-cycle-analytics-for-traders/ch3.md): SuperSmoother derivation and equation 3-3. This is the relevant equation, rather than the preceding modified Butterworth equations 3-1 and 3-2.
- [Chapter 7, Spectral Dilation](../../2013-cycle-analytics-for-traders/ch7.md): the one-pole Roofing Filter in listing 7-1, its additional high-pass stage in listing 7-2, and the two-pole Roofing Filter indicator in listing 7-3. Listings 7-4 and 7-5 reuse the two-pole filter for stochastic and RSI calculations.
- [Chapter 4, Decyclers](../../2013-cycle-analytics-for-traders/ch4.md): supporting high-pass and complementary low-pass transfer functions, including two-pole high-pass applications.

Other chapters reuse these filters as preprocessing stages; they do not change the comparison below. The book's [table of contents and bibliographic record](../../2013-cycle-analytics-for-traders/toc.md) identifies the 2013 Wiley edition.

## Article versus book

| Filter | Article definition | Book definition | Difference |
| --- | --- | --- | --- |
| SuperSmoother | Two-pole recursive low-pass filter with a two-sample input average; critical period fixed at 10 in the example | Equation 3-3 gives the same filter with a general `Period`; chapter 3 recommends about 10 bars | No change to the recurrence or published constants. The book supplies more derivation and a general period. |
| One-pole Roofing | Discussed as insufficient to overcome spectral dilation; not the article's final Roofing Filter | Listing 7-1: one-pole high-pass at 48 followed by SuperSmoother at 10 | A preliminary book variant, not equivalent to the article's final filter. |
| One-pole Roofing plus another high-pass | The article instead uses a two-pole high-pass | Listing 7-2: one-pole high-pass at 48, SuperSmoother at 10, then another one-pole high-pass at 48 | Has two high-pass stages overall. The book plots both the intermediate and final values. |
| Two-pole Roofing | Two-pole high-pass at 48 followed by SuperSmoother at 10; plots the result and zero | Listing 7-3: same recurrence with `LPPeriod(40)` and `HPPeriod(80)` inputs; plots the result, its two-bar delay, and zero | Parameter defaults and plotting differ. Setting book inputs to 10 and 48 reproduces the article's recurrence and coefficients. Book listings 7-4/7-5 already use 10 and 48. |

The one-pole-plus-high-pass variant and the two-pole variant use different high-pass angles at the same nominal period. They should not be expected to yield identical arrays merely because each contains two high-pass poles.

### Full-precision mathematical comparison

Let $x_t$ denote the scalar input and $L$ the shortest, low-pass critical period. Write the SuperSmoother coefficients as

$$
\begin{aligned}
\beta &= \frac{\sqrt{2}\pi}{L}, & a &= e^{-\beta}, \\
c_2 &= 2a\cos\beta, & c_3 &= -a^2, \\
c_1 &= 1-c_2-c_3, \\
y_t &= \frac{c_1}{2}(x_t+x_{t-1})+c_2y_{t-1}+c_3y_{t-2}.
\end{aligned}
$$

This is equation 3-3 and the article's SuperSmoother calculation, with `1.414` replaced by $\sqrt{2}$ and `3.14159` by $\pi$. EasyLanguage's cosine angle is in degrees: `1.414*180/L` becomes $\sqrt{2}\pi/L$ radians. The copied SuperSmoother stores `gamma1 = c1/2`, so the absence of `/2` in its update expression is correct.

Let $H$ be the longest, high-pass critical period. Define

$$
\alpha(\theta)=\frac{\cos\theta+\sin\theta-1}{\cos\theta},\qquad
q=1-\alpha,\qquad g=1-\frac{\alpha}{2}.
$$

For book listing 7-1, $\theta=2\pi/H$ and

$$h_t=g(x_t-x_{t-1})+qh_{t-1}.$$

The Roofing result is obtained by applying the SuperSmoother to $h_t$, using $h_t$ in place of $x_t$ in its recurrence. Book listing 7-2 additionally computes

$$z_t=g(y_t-y_{t-1})+qz_{t-1}.$$

For book listing 7-3 and the article's final Roofing Filter, the full-precision angle is $\theta=\sqrt{2}\pi/H$, and

$$h_t=g^2(x_t-2x_{t-1}+x_{t-2})+2qh_{t-1}-q^2h_{t-2}.$$

Again apply the SuperSmoother to $h_t$. The published `.707*360/H` degree angle corresponds to replacing `.707` by $1/\sqrt{2}$ before conversion to radians.

The smoothing stage reduces short-period noise and has a zero at the two-bar Nyquist cycle. The two-pole high-pass stage rejects long-period components more strongly than a single pole, addressing the spectral dilation discussed in chapter 7 and the article. Its nominal zero mean does not imply that every finite observation window has an arithmetic mean exactly equal to zero.

## Copied SuperSmoother

Source: [super_smoother.py](../../../../external/zpano/py/indicators/john_ehlers/super_smoother/super_smoother.py).

- Coefficients use `math.sqrt(2)` and `math.pi`; both coefficient signs and the input averaging are correct.
- Default shortest cycle period is 10, matching the article example and the book's recommendation.
- The first finite input seeds the previous input and both filter-history values. The recurrence is evaluated during startup, but the first two returned values are NaN. The third finite input produces the first visible result.
- NaN inputs return NaN and leave state unchanged, including the priming counter. This is a library convention not specified by the article or book.
- `update(sample)` applies the correct filter to the supplied scalar. `update_bar()` defaults to median price `(high + low)/2`, whereas the published examples use `Close`. The parameter documentation incorrectly says the default bar component is Close. This does not affect direct scalar updates with `INPUT_CLOSE`.

**Assessment:** correct implementation of the source recurrence with a reasonable, but independently chosen, initialization. Its standalone master can reuse this numeric core, after choosing and documenting the initialization contract.

## Copied Roofing Filter

Sources: [roofing_filter.py](../../../../external/zpano/py/indicators/john_ehlers/roofing_filter/roofing_filter.py) and [params.py](../../../../external/zpano/py/indicators/john_ehlers/roofing_filter/params.py).

### Variant mapping

| Copied configuration | Book correspondence | First visible output |
| --- | --- | --- |
| `has_two_pole_highpass_filter=False`, `has_zero_mean=False` | Listing 7-1, intermediate one-pole Roofing Filter | Fourth finite input |
| `has_two_pole_highpass_filter=False`, `has_zero_mean=True` | Listing 7-2's final `Filt2` | Fifth finite input |
| `has_two_pole_highpass_filter=True` | Listing 7-3's `Filt`; also the article's final Roofing Filter | Fifth finite input |

The copied tests deliberately exercise book settings 10/48, 10/48, and 40/80 respectively. This makes the book correspondence clear. `has_zero_mean` is ignored when two-pole mode is selected, so the booleans describe three effective variants, not four.

### Changes and decisions needed

1. **Full precision:** the high-pass stage correctly uses $\sqrt{2}/2$ for the two-pole angle. However, the SuperSmoother stage explicitly uses `beta_ss = 1.414 * math.pi / shortest` to match a C# reference. Replace the truncated factor with `math.sqrt(2)` for the requested master. The current Roofing and standalone SuperSmoother implementations therefore do not use exactly the same smoothing coefficients for the same period.
2. **Default variant:** the copied default is one pole, corresponding to listing 7-1. To reproduce the article's filter, select two-pole mode and periods 10/48. To reproduce the book's listing 7-3 example, select two-pole mode and periods 40/80. Both defaults cannot be represented by one parameter set. An article-based master should default to the article's two-pole 10/48 configuration.
3. **Startup:** in two-pole mode, both HP and SuperSmoother state are forced to zero for the first three finite inputs. Filtering starts on the fourth input and the result is exposed on the fifth. The first complete second difference is available on the third input and is discarded. Neither the article nor the book listing explicitly instructs this omission. Starting HP on the third input with zero HP history is another possible convention and yields materially different early results. Delaying public output alone would not require discarding a valid HP update.
4. **Source plotting:** the copied zero-mean variant returns only final `Filt2`, whereas listing 7-2 plots `Filt` and `Filt2`. The copied two-pole variant returns only `Filt`, whereas listing 7-3 also plots `Filt[2]`. The filter calculation is present; exact reproduction of the book's full indicator display would require those additional outputs. The article needs only the current filter value; its zero plot is a constant reference line.
5. **Input component:** as with the copied SuperSmoother, bar updates default to median price despite documentation claiming Close. Scalar updates using the supplied closes avoid this difference.
6. **One-pole boundary:** `shortest_cycle_period=2`, `longest_cycle_period=4` passes validation. At $H=4$, $\theta=\pi/2$ makes the direct alpha expression formally $0/0$. Python's finite-precision evaluation in this investigation produced `alpha=0`, HP gain 1, and HP decay 1; the continuous extension should give `alpha=1`, gain 0.5, and decay 0. A stable equivalent expression is

   $$\alpha=\frac{2\tan(\theta/2)}{1+\tan(\theta/2)}.$$

   Handle this boundary if the master includes one-pole variants with the copied allowed parameter range. The normal source settings 48 and 80 are unaffected.

**Assessment:** the three filtering recurrences correspond to the book, but constants, configuration, startup, and the one-pole boundary prevent treating the supplied code as an unqualified master reference.

## Numerical checks

The original application imports are missing as expected. For this investigation, the class and factory definitions were loaded from their Python ASTs without changing their numeric statements. Minimal stubs replaced only the unavailable application framework. Independent batch calculations evaluated the source equations. These checks exercise scalar numerical code, not the missing framework or entity adapters.

All numerical comparisons below used the 252 values in [the shared INPUT_CLOSE fixture](../../prepared-for-conversion/test_testdata.py). Comparisons include every finite returned output. Initial states and HP start indices are held equal when isolating coefficient differences.

| Calculation | Maximum absolute difference |
| --- | ---: |
| Copied SuperSmoother versus full-precision source recurrence, same initialization | 0 |
| Copied Roofing, each of three variants, versus source recurrence with identical mixed-precision coefficients and startup | 0 |
| Copied one-pole Roofing 10/48 versus fully precise coefficients | 0.00159649415266117 |
| Copied one-pole plus zero-mean Roofing 10/48 versus fully precise coefficients | 0.00147141366783998 |
| Copied two-pole Roofing 40/80 versus fully precise coefficients | 0.00171757225374103 |
| Copied two-pole Roofing 10/48 versus fully precise coefficients | 0.00155051914736504 |

Coefficient precision alone therefore changes the Roofing expected arrays. The small differences are sufficient to invalidate 15-digit expected values copied from the old implementation.

### Startup is part of the reference contract

The article and book show recursive variables initialized to zero, but do not completely specify the history of a finite standalone input sequence, the host platform's preloaded bars, or when outputs become publicly available. The supplied Traders' Tips do not establish a universal startup convention either:

- [AmiBroker implementation](tips/MESAStochastic.afl) initializes `Filt` from the input array and starts recurrence at zero-based index 2. Its high-pass function also initializes HP from the input array. Those are different seeds from the copied code.
- [eSignal implementation](tips/MESAStochastic.efs) checks availability of prior input samples and uses platform-managed prior filter values.
- [TradeStation implementation](tips/MESAStochastic.els) repeats the article recurrences and zero-initialized variables without adding an explicit standalone startup policy.

With full-precision coefficients, the copied SuperSmoother's first visible value is `92.7696354780799`. Seeding its first two outputs from the first two input prices, as AmiBroker does, instead yields `96.1225600689282` at the same third sample. The difference comes from initialization.

For two-pole Roofing 10/48, retaining the copied HP start at sample 4 but using fully precise coefficients gives `0.298688049645342` at sample 5. Starting HP at sample 3 with zero prior HP/filter state gives `-3.39837559463450` at sample 5, even if both implementations hide their first four outputs. Thus NaN masking alone cannot make their arrays equivalent.

The book recurrence can be implemented under either declared startup convention, but exact finite-sequence output equivalence needs identical seeds and update timing. A master description must state them explicitly. Being “primed” after three or five samples means the implementation exposes an output; it does not mean the transient of a long-period recursive filter has settled.

### Literal original output versus requested precision

Literal article code uses `1.414`, `.707`, and `3.14159`. Using full-precision replacements changes the numerical result even with identical initialization. At the article periods, the maximum differences measured here were approximately `0.00190111211736621` for SuperSmoother and `0.00278297796223770` for two-pole Roofing.

Consequently, the requested full-precision master can reproduce the **source algorithm**, but cannot also reproduce the literal truncated code's arrays to 15 digits. Full precision takes precedence under the user's instruction. Future verification should compare against a source recurrence with the same precise constants and declared startup; comparisons against literal originals should separately document the expected precision differences.

## Why the copied fixtures are insufficient

The copied SuperSmoother fixture contains 500 inputs and its Roofing fixture contains 100; neither is the shared 252-value `INPUT_CLOSE`. Their expected values are generally recorded to about two decimal places.

The [SuperSmoother numerical test](../../../../external/zpano/py/indicators/john_ehlers/super_smoother/test_super_smoother.py) skips output comparison before zero-based index 60 and permits an absolute error of 0.5. Its legacy sample 4 expects `268.7`, but the copied implementation returns `1064.08061109256`. This discrepancy is hidden by the skipped prefix. After the skip, the largest measured difference was about 0.006813.

The [Roofing numerical tests](../../../../external/zpano/py/indicators/john_ehlers/roofing_filter/test_roofing_filter.py) skip comparison before zero-based index 30 and also permit an error of 0.5. Largest differences after that skip were approximately 0.235016, 0.113321, and 0.025848 for the three variants. These checks support approximate later behavior but do not establish exact reference equivalence.

NaN passthrough was additionally checked in all four effective configurations: it returns NaN without modifying numeric state or priming count. No claims are made about tests requiring the absent application framework.

## Recommended later preparation

For `super-smoother-filter`, extract the existing precise numeric core into a standard-library-only streaming class; document the selected initialization and NaN handling; preserve equation 3-3 and its theory; and generate fresh fixtures from the shared closes.

For `roofing-filter`, prepare the two-pole article filter with defaults 10/48, full-precision HP and SuperSmoother constants, and an explicit initialization contract. Cover the book's 40/80 setting in its eventual reference combinations. If the two earlier book variants are retained as configuration options, document their distinct equations and outputs and handle the one-pole period-4 boundary.

Fresh descriptions, executable examples, and five-language fixtures remain necessary. The parameter-combination proposal and its confirmation belong to the subsequent preparation stage requested by the user. They have not been started in this investigation.

## Bibliography

```bibtex
@book{ehlers2013cycle,
  author    = {Ehlers, John F.},
  title     = {Cycle Analytics for Traders: Advanced Technical Trading Concepts},
  publisher = {Wiley},
  year      = {2013},
  series    = {Wiley Trading},
  isbn      = {9781118728604},
  note      = {Chapter 3, equation 3-3; chapter 7, code listings 7-1 through 7-5;
               chapter 4 for supporting high-pass filter theory}
}

@article{ehlers_2014_predictive,
  author  = {Ehlers, John F.},
  title   = {Predictive And Successful Indicators},
  journal = {Technical Analysis of STOCKS \& COMMODITIES},
  volume  = {32},
  number  = {1},
  pages   = {16--25},
  year    = {2014},
  month   = jan,
  url     = {https://technical.traders.com/archive/article.asp?file=\V32\C01\692EHLE.pdf}
}

@misc{traders_tips_2014_01,
  author       = {{Technical Analysis of STOCKS \& COMMODITIES}},
  title        = {Traders' Tips: Predictive And Successful Indicators},
  howpublished = {online},
  year         = {2014},
  month        = jan,
  url          = {https://www.traders.com/Documentation/FEEDbk_docs/2014/01/TradersTips.html},
  note         = {Supplied TradeStation, eSignal, and AmiBroker implementations}
}
```
