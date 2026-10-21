# Autocorrelation periodogram: source and implementation investigation

This records the investigation requested before creating the Python master and
its five-language reference fixtures. The two copied indicators examined are
`AutoCorrelationIndicator` and `AutoCorrelationPeriodogram`. After this report,
the user confirmed all combinations and requested implementation; the completed
master and 64-case dataset are described in [description.md](description.md).
The numerical comparisons below remain the original investigation results.

The 2016 article and the 2013 book describe the same general technique but
implement different numerical algorithms. The copied autocorrelation indicator
substantially follows book Listing 8-2. The copied periodogram follows a modified
version of book Listing 8-3 and omits its dominant-cycle output. A new master is
appropriate; adding a dominant-cycle field alone would leave the source
differences unresolved.

## Sources examined

- [2016 TASC article, Measuring Market Cycles](../../tasc/2016-09-measuring-market-cycles/content.md),
  including its complete EasyLanguage sidebar.
- [September 2016 Traders' Tips](../../tasc/2016-09-measuring-market-cycles/tips/tips.md),
  with the local TradeStation, eSignal, Wealth-Lab, AmiBroker, NinjaTrader, and
  Updata code inspected for differences.
- [Book contents](../../2013-cycle-analytics-for-traders/toc.md).
- [Book Chapter 8, Autocorrelation](../../2013-cycle-analytics-for-traders/ch8.md),
  particularly Listings 8-2 and 8-3 and their explanations.
- [Book Chapter 3, SuperSmoother](../../2013-cycle-analytics-for-traders/ch3.md),
  Equation 3-3.
- [Book Chapter 7, Spectral Dilation](../../2013-cycle-analytics-for-traders/ch7.md),
  for the roofing filter background.
- [Book Chapter 9, Fourier Transforms](../../2013-cycle-analytics-for-traders/ch9.md),
  for related Fourier and gain-control conventions.
- [Book Chapter 11, Adaptive Filters](../../2013-cycle-analytics-for-traders/ch11.md),
  which repeats the periodogram calculation as a dominant-cycle estimator.
- [Copied autocorrelation indicator](../../../../external/zpano/py/indicators/john_ehlers/auto_correlation_indicator/auto_correlation_indicator.py)
  and its parameters and fixtures.
- [Copied autocorrelation periodogram](../../../../external/zpano/py/indicators/john_ehlers/auto_correlation_periodogram/auto_correlation_periodogram.py)
  and its parameters and fixtures.
- [Copied heatmap output structure](../../../../external/zpano/py/indicators/core/outputs/heatmap.py).

All conclusions about printed listings refer to these local Markdown/code
sources. There is no original book PDF in the supplied book directory, so a
listing anomaly cannot be classified conclusively as a publication error versus
a transcription error.

## Article versus book Listing 8-3

| Calculation | 2016 article | 2013 book Listing 8-3 |
| --- | --- | --- |
| Input | Close | Close |
| High-pass filter | One pole, cutoff period 48 | Two poles, cutoff period 48 |
| SuperSmoother cutoff | 8 | 10 |
| Analyzed/displayed periods | 8 through 48, inclusive: 41 bins | 10 through 48, inclusive: 39 bins |
| Pearson averaging | Fixed 3; zero selects the current lag | Fixed 3; zero selects the current lag |
| Correlation lags | 0 through 48 | 0 through 48 |
| Fourier summation lags | 3 through 48 | 3 through 48 |
| Fourier angles | `360*N/Period` degrees | Local Listing 8-3 says `370*N/Period` degrees |
| Spectrum smoothing | `0.2*SqSum*SqSum + 0.8*previous` | Same |
| Normalization denominator | Maximum of the current smoothed spectrum; reset every bar | Maximum of current spectrum and `0.995*previous_maximum` |
| Minimum subtraction | None | None |
| Resolution enhancement | Optional cube of normalized spectrum, before dominant-cycle calculation | Optional square, commented out, after dominant-cycle calculation |
| Dominant-cycle threshold | Include bins with power at least 0.25; also require peak at least 0.25 | Include bins with power at least 0.5 |
| Missing qualifying power | Retain previous dominant cycle when selected power sum is below 0.25 | Retain previous dominant cycle when selected power sum is zero |
| Dominant-cycle plotting | Calculated internally; no dominant-cycle plot in the sidebar | Explicit blue dominant-cycle line |

Two important consequences:

1. In the article, enhancement changes **both the heatmap and the dominant
   cycle**, because the centroid is computed after cubing the power. In the book,
   the optional display transformation does not change the dominant cycle.
2. With positive finite power, the article's maximum normalized bin is always
   one, even with enhancement. Its `PeakPwr >= 0.25` condition therefore does not
   provide an absolute signal-strength test. The book's slow-decaying
   denominator can make every current bin fall below 0.5 and cause the dominant
   cycle to hold its previous value.

Both listings define `SqSum` as cosine-part squared plus sine-part squared and
then square `SqSum` again before smoothing. Thus the input to the EMA is the
fourth power of the Fourier magnitude. This second squaring must be preserved
to reproduce the source algorithm.

## Mathematical differences

Let $x_t$ be the input price, $h_t$ the high-pass output, $f_t$ the final roofing
filter output, $H$ the high-pass cutoff period, and $L$ the SuperSmoother cutoff.
All trigonometric functions below take radians.

The article uses:

$$
b = \frac{1-\sin(2\pi/H)}{\cos(2\pi/H)},\qquad
h_t = \frac{1+b}{2}(x_t-x_{t-1}) + b h_{t-1}.
$$

The book uses:

$$
\theta = \frac{2\pi}{\sqrt{2}H},\qquad
\alpha = \frac{\cos\theta+\sin\theta-1}{\cos\theta},
$$

$$
h_t = (1-\alpha/2)^2(x_t-2x_{t-1}+x_{t-2})
       +2(1-\alpha)h_{t-1}-(1-\alpha)^2h_{t-2}.
$$

Both use the SuperSmoother recurrence, with different $L$:

$$
a = \exp(-\sqrt{2}\pi/L),\quad
c_2 = 2a\cos(\sqrt{2}\pi/L),\quad
c_3 = -a^2,\quad c_1 = 1-c_2-c_3,
$$

$$
f_t = c_1\frac{h_t+h_{t-1}}{2}+c_2f_{t-1}+c_3f_{t-2}.
$$

For lag $\ell$, the Pearson input pairs are $X_j=f_{t-j}$ and
$Y_j=f_{t-\ell-j}$ for $j=0,\ldots,M-1$. With
$S_x=\sum X_j$, $S_y=\sum Y_j$, $S_{xx}=\sum X_j^2$,
$S_{yy}=\sum Y_j^2$, and $S_{xy}=\sum X_jY_j$:

$$
\rho_t(\ell) =
\frac{M S_{xy}-S_xS_y}
{\sqrt{(M S_{xx}-S_x^2)(M S_{yy}-S_y^2)}}.
$$

The proper Fourier basis for candidate period $p$ is:

$$
C_t(p)=\sum_{n=3}^{48}\rho_t(n)\cos(2\pi n/p),\qquad
S_t(p)=\sum_{n=3}^{48}\rho_t(n)\sin(2\pi n/p),
$$

$$
Q_t(p)=C_t(p)^2+S_t(p)^2,\qquad
R_t(p)=0.2 Q_t(p)^2+0.8R_{t-1}(p).
$$

The article normalizes with $A_t=\max_p R_t(p)$. The book uses
$A_t=\max(0.995 A_{t-1},\max_p R_t(p))$. In either case the
unmodified normalized spectrum is $P_t(p)=R_t(p)/A_t$ when $A_t>0$.

The dominant cycle is a thresholded power-weighted centroid, **not the period
of the single largest bin**:

$$
D_t = \frac{\sum_{p\in\mathcal S_t}p W_t(p)}
{\sum_{p\in\mathcal S_t}W_t(p)}.
$$

For the article, $W_t=P_t$ or $P_t^3$ according to enhancement, and selected
bins satisfy $W_t\geq0.25$. For the book, $W_t=P_t$ and selected bins satisfy
$P_t\geq0.5$; optional display squaring happens afterward. Each listing has the
hold rule described in the comparison table.

## Book anomalies and precision policy

- **`370` in the Fourier basis:** Chapter 11 repeatedly uses `360`, as does the
  2016 article. A complete turn is $2\pi$, and literal `370` shifts the frequency
  represented by a period label by a factor of $370/360$. This is strong evidence
  for correcting it to `360`, while documenting the correction rather than
  silently claiming literal Listing 8-3 equivalence.
- **AGC prose versus code:** Chapter 8's explanation says decay `0.991`, but
  Listing 8-3 says `0.995`. Chapter 11 contains examples using each value.
  A Listing 8-3 profile should use `0.995`. This is an algorithm setting, not a
  truncated representation of $\pi$ or $\sqrt{2}$.
- **Listing 8-2 transcription:** Its variable block contains a stray executable
  `Filt2` statement; its plotting block contains malformed comment text and a
  duplicate lag-7 plot where lag 6 would be expected. These are not additional
  filtering stages to copy into a master implementation.
- **Full precision:** Use `math.pi`, `math.sqrt(2.0)`, and
  `1.0 / math.sqrt(2.0)` instead of `3.14159`, `1.414`, and `0.707`.
  A full-precision reference reproduces the chosen equations with this requested
  substitution; it will not be bit-for-bit equal to a run using truncated source
  constants.

## Audit of the copied indicators

### AutoCorrelationIndicator versus Listing 8-2

The main calculation matches: two-pole high-pass, 10-bar SuperSmoother,
lag-dependent averaging by default, Pearson correlation, and mapping
$\rho\mapsto(\rho+1)/2$ into a heatmap over lags 3 through 48.

Differences and qualifications:

- It uses truncated `0.707` and `1.414`, although it already uses `math.pi`.
- Bar updates default to the median `(high + low)/2`, whereas the book uses
  `Close`. Scalar updates process the supplied scalar directly. The parameter
  documentation incorrectly says the default bar component is Close.
- It initializes absent history to zero, updates state throughout startup, and
  exposes the first heatmap after 96 valid samples with default lag-dependent
  averaging. This is a library warm-up convention, not an explicit book rule.
- If Pearson's denominator is not positive, the copied estimator uses raw
  correlation zero, yielding the neutral heatmap value 0.5. The literal book
  array is left unchanged and then scaled again, which can produce different
  behavior on degenerate windows. The copy avoids this problematic reuse.
- It computes all displayed bins, including lag 6. It returns numeric heatmap
  values rather than book-specific RGB plot calls.
- No dominant cycle is expected in Listing 8-2. This indicator is a correlation
  display; the Fourier transform and spectral centroid belong to the periodogram.

Verdict: substantially faithful to the book's intended autocorrelation
calculation, with explicit library conventions and edge-case differences.

### AutoCorrelationPeriodogram versus Listing 8-3

Matching parts: two-pole high-pass, 10-bar SuperSmoother, fixed three-sample
Pearson averaging, Fourier lags 3 through 48, periods 10 through 48, second
spectral squaring, EMA coefficient 0.2, and AGC decay 0.995.

Differences and issues:

- It uses the mathematically appropriate `2*pi` Fourier basis rather than the
  local Listing 8-3's `370` degrees.
- It **does not compute or expose a dominant cycle**. `update` returns only a
  `Heatmap`; its output enumeration and metadata describe one output.
- Default output applies an extra transformation
  $(P_t(p)-\min_qP_t(q))/(1-\min_qP_t(q))$. Neither source does this. Setting
  `fixed_normalization=True` removes the extra minimum subtraction.
- Its zero averaging length means "use default 3"; source zero means $M=\ell$.
  The copied periodogram cannot select the source's lag-dependent mode through
  that parameter.
- Averaging length 1 is accepted, but Pearson correlation is undefined with one
  sample. A numerical check produced an entirely zero spectrum for all 252
  supplied fixture values with that setting.
- Its disabling flags introduce variants absent from the default source
  calculation. Disabling spectral squaring is different from disabling display
  enhancement. There is no article-style enhancement parameter.
- It defaults bar updates to median price, with the same inaccurate Close
  parameter documentation noted above.
- It uses truncated `0.707` and `1.414`. Warm-up is 51 valid samples at the
  default fixed averaging length. Nonpositive Pearson denominators reset the
  correlation to zero instead of retaining the book's previous raw correlation.
- It handles zero maximum power by returning a zero spectrum, whereas the
  listings' unconditional normalization can divide by zero.

Verdict: a modified book-style periodogram heatmap, not an exact implementation
of either the article or the complete book indicator.

## Numerical investigation

The copied estimator classes were extracted with Python's `ast` module and run
with their standard-library dependencies. This avoids fabricating missing
framework imports or treating the context-extracted files as a buildable package.
No copied files were changed.

| Check | Result |
| --- | --- |
| Copied autocorrelation indicator: 28 bundled snapshot checks | Maximum absolute error approximately $3.13\times10^{-14}$ |
| Copied periodogram: 28 bundled snapshot checks | Maximum absolute error approximately $4.80\times10^{-14}$ |
| Copied periodogram: averaging length 1 | Final spectrum entirely zero |
| Fixture input identity | Both copied indicators use 252 median prices, exactly `(INPUT_HIGH + INPUT_LOW)/2`, not `INPUT_CLOSE` |
| Largest copied-fixture versus common-close difference | 3.815 price units |

These snapshot results establish agreement with the copies' own fixtures. They
do not establish agreement with a TradeStation execution of the sources.

Separate direct translations of the article and book recurrences were compared
using the requested 252 `INPUT_CLOSE` values, zero prehistory, fixed $M=3$, and
full-precision mathematical constants. The book comparison uses the corrected
$2\pi$ basis and code decay 0.995. Internal filtering, correlations, EMA, AGC,
and dominant-cycle calculations start with the first sample. Comparisons below
are after 51 samples, when the 51-slot filtered history has filled under this
startup convention. This is an investigation convention, not a final master
warm-up specification.

| Zero-based input index | Article dominant cycle | Corrected book dominant cycle |
| --- | --- | --- |
| 50 | 35.425419166972 | 40.150602193389 |
| 120 | 13.325967780638 | 14.000000000000 |
| 150 | 11.824504905765 | 14.000000000000 |
| 200 | 18.811695387554 | 17.992804934434 |
| 250 | 8.691526053049 | 17.499743876420 |
| 251 | 8.719570248582 | 17.499743876420 |

Across indices 50 through 251:

- Maximum article versus corrected-book dominant-cycle difference: approximately
  **17.9127063867733 bars**.
- Maximum corrected-book versus literal-370-book difference: approximately
  **1.10387676604945 bars**.
- Maximum article full-precision versus truncated-constant difference:
  approximately **0.00993201156648 bars**.
- Maximum corrected-book full-precision versus truncated-constant difference:
  approximately **0.00163440027227 bars**.

At index 150 the corrected book's largest normalized spectral value is about
0.05444, below its 0.5 threshold. The book therefore holds an earlier dominant
cycle. The article normalizes its current peak to one and calculates a fresh
centroid. These differences cannot be reconciled by using a looser test tolerance.

## Traders' Tips are not interchangeable numeric references

The TradeStation EasyLanguage strategy repeats the article's estimation stages.
It then clamps the dominant cycle to at least one and applies `Ceiling` for the
CCI length. Those strategy-specific steps should not round the master
periodogram output.

Other supplied ports contain material divergences:

- AmiBroker smooths `SqSum` without the article's second squaring, then applies
  display squaring. These operations are not equivalent.
- NinjaTrader uses rounded filter coefficients, rounds intermediate calculations
  to two decimal places, and computes Fourier angles using integer operands.
  It is unsuitable as the full-precision numeric oracle.
- Wealth-Lab uses a different high-pass coefficient, indexes the delayed Pearson
  window as `bar - Lag + count` rather than `bar - Lag - count`, recreates the
  smoothing-state array on each bar, and includes Fourier period zero.
- eSignal applies an additional degree-to-radian conversion to an already-radian
  SuperSmoother angle, omits correlations for lags 3 through 7 used by the DFT,
  and smooths across adjacent period bins rather than across time for each bin.
- The Updata contribution follows several book conventions rather than the
  article and includes integer expressions such as `370/180` in its angle
  calculation.

Use Ehlers' article EasyLanguage as the primary 2016 algorithm source, with
explicit full-precision substitutions and a documented startup/degeneracy policy.
The vendor tips provide comparison material, not a single mutually consistent
set of expected numeric values.

## Recommendation for the next phase

Use the **2016 article as the default master**, since it is the selected input
document, and keep an explicit **corrected book profile** if book compatibility
is also wanted. Each profile must set the high-pass order, smoothing cutoff,
period range, gain-control convention, dominant-cycle threshold, and position of
the enhancement stage together. Avoid mixing individual defaults into an
unidentified third algorithm.

Return a named result with `heatmap` and `dominant_cycle`. The standalone heatmap
can preserve the copied structure's names:

- `time` (optional for scalar research use),
- `parameter_first`, `parameter_last`, `parameter_resolution`,
- `value_min`, `value_max`, `values`.

For unit-resolution bins, `values[i]` represents period `parameter_first + i`.
An unprimed heatmap should be empty with NaN extrema, and the dominant cycle
should be NaN. Five-language expected data should cover **every spectrum bin
and the dominant cycle for every input sample**, not just the existing sparse
heatmap snapshots. A fixed-size fixture can represent an unprimed heatmap row
with NaNs while the runtime heatmap retains its empty-column convention.

Before generating final fixtures, the master documentation must define startup,
valid-sample counting, zero-variance correlation behavior, zero-power handling,
and hold-last-dominant behavior. At fixed averaging length $M$, the largest
filtered-history index is $48+M-1$, requiring $48+M$ filtered values. In
lag-dependent mode it is 95, requiring 96 values. This differs from treating the
article's informal "48-bar block" wording as an exact history length.

The requested parameter-combination table and confirmation belong to the master
preparation phase after this investigation, before expected arrays are generated.

## Bibliography

```bibtex
@article{ehlers_measuring_cycles_2016,
  author  = {Ehlers, John F.},
  title   = {Measuring Market Cycles},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume  = {34},
  number  = {9},
  pages   = {11--16},
  year    = {2016},
  month   = sep,
  url     = {https://technical.traders.com/archive/article.asp?file=\V34\C09\280EHLE.pdf}
}

@book{ehlers2013cycle,
  author    = {Ehlers, John F.},
  title     = {Cycle Analytics for Traders: Advanced Technical Trading Concepts},
  publisher = {Wiley},
  year      = {2013},
  series    = {Wiley Trading},
  isbn      = {9781118728604},
  note      = {Chapters 3, 7, 8, 9, and 11; especially Listings 8-2 and 8-3}
}

@misc{traders_tips_2016_09,
  author = {{Technical Analysis of Stocks \& Commodities}},
  title  = {Traders' Tips: Measuring Market Cycles},
  year   = {2016},
  month  = sep,
  url    = {https://www.traders.com/Documentation/FEEDbk_docs/2016/09/TradersTips.html}
}
```
