# Corona Charts: investigation before master preparation

The four copied indicators implement the **2008 Corona family with modifications**.
They do not implement four corresponding algorithms from the 2013 book: those
algorithms are absent from the supplied chapters. The book's bandpass filter and
comb-filter spectrum explain related mathematics, but substituting its spectrum
would change all four indicators.

New reference masters are justified. The existing shared estimator is a useful
structural starting point, and the existing scalar outputs should be preserved.
Several calculation, indexing, and invalid-data behaviors need explicit decisions
before generating reference fixtures. The user subsequently confirmed the
64-case proposal and requested implementation. The completed masters and
finalized conventions are described in [description.md](description.md) and
[validation.md](validation.md). The audit below retains its original
preparation-stage findings and recommendations.

## Sources and strength of evidence

Paths below are relative to this directory.

| Source | Available material and use |
| --- | --- |
| [November 2008 article](../../tasc/2008-11-corona-charts/content.md) | Full explanatory prose and figures for all four indicators. The advertised EasyLanguage sidebars and `CoronaCharts.Eld` are **absent** from the supplied directory. This establishes the purpose and interpretation, but cannot certify every code detail. |
| [November 2008 Traders' Tips](../../tasc/2008-11-corona-charts/tips/tips.md) | Vendor descriptions and code. The TradeStation section points to an ELD download rather than supplying the original listing. |
| [Wealth-Lab C#](../../tasc/2008-11-corona-charts/tips/Corona_wealthlab.cs) | Readable implementation of all four indicators. Useful corroboration of recurrences; also contains demonstrable median and price-indexing errors. |
| [TraderStudio](../../tasc/2008-11-corona-charts/tips/Corona_traderstudio.txt) | All four indicators, but many comparisons and intervening expressions disappeared during transcription. Use surviving expressions only. |
| [eSignal](../../tasc/2008-11-corona-charts/tips/Corona_esignal.efs) | Four concatenated scripts with substantial transcription damage, including missing comparisons and code blocks. Not an executable oracle. |
| [AmiBroker](../../tasc/2008-11-corona-charts/tips/Corona_amibroker.afl) | Readable spectrum and Swing implementation. Several intentional algorithm changes; not numerically interchangeable with the other ports. |
| [March 2008 article](../../tasc/2008-03-measuring-cycle-periods/content.md) | Contains actual EasyLanguage for the predecessor channelized-receiver estimator, and the amplitude/derivative explanation. |
| [March 2008 EasyLanguage tip](../../tasc/2008-03-measuring-cycle-periods/tips/EhlersSpectrum.els) | Corroborates the older estimator, but itself has missing comparison text. |
| [April 2012 Corona Swing listing](<../../tasc/2012-04-setting-strategies-with-swami-charts/tips/code/Corona Chart Swing Position.eqi>) | Later, largely readable EasyLanguage-style Tradesignal listing with the complete Corona estimator and Swing calculation. Strongest local evidence for these calculations, but it is a later port, not the missing November sidebar. Includes a zero-width guard and some plotting anomalies. |
| [Book contents](../../2013-cycle-analytics-for-traders/toc.md) and all 17 chapters | No named Corona Spectrum, Swing Position, Trend Vigor, or Corona SNR algorithm found. |
| [Book Chapter 5](../../2013-cycle-analytics-for-traders/ch5.md) | Two-pole bandpass recurrence, phase/selectivity tradeoff, quality factor, gain control. |
| [Book Chapter 7](../../2013-cycle-analytics-for-traders/ch7.md) | Spectral dilation and roofing-filter theory. |
| [Book Chapter 10](../../2013-cycle-analytics-for-traders/ch10.md) | Related comb-filter spectrum, with different prefilter, power estimate, normalization, and centroid. |
| [Book Chapter 11](../../2013-cycle-analytics-for-traders/ch11.md) | Adaptive indicators using the autocorrelation periodogram, not Corona's estimator. |
| [Book Chapter 16](../../2013-cycle-analytics-for-traders/ch16.md) | SwamiCharts plot conventional indicators over different lookbacks. That vertical axis has a different meaning from a Corona uncertainty raster. |
| [Copied shared estimator](../../../../external/zpano/py/indicators/john_ehlers/corona/corona.py) | Inspected alongside parameters and tests. Framework imports were stubbed for numerical investigation; copied calculations were not edited. |
| [Copied Spectrum](../../../../external/zpano/py/indicators/john_ehlers/corona_spectrum/corona_spectrum.py), [Swing](../../../../external/zpano/py/indicators/john_ehlers/corona_swing_position/corona_swing_position.py), [Trend](../../../../external/zpano/py/indicators/john_ehlers/corona_trend_vigor/corona_trend_vigor.py), [SNR](../../../../external/zpano/py/indicators/john_ehlers/corona_signal_to_noise_ratio/corona_signal_to_noise_ratio.py) | Actual copied directory names use underscores, including Swing and SNR. |
| [Heatmap type](../../../../external/zpano/py/indicators/core/outputs/heatmap.py), [copied ACP](../../../../external/zpano/py/indicators/john_ehlers/auto_correlation_periodogram/auto_correlation_periodogram.py), [prepared ACP master](../auto-correlation-periodogram/auto-correlation-periodogram.py) | Output fields and an existing conversion-reference structure. |

Conclusions distinguish explicit source expressions, numerical observations,
and recommendations. The missing original sidebars prevent claiming exact
reproduction of their unspecified startup and exceptional-input behavior.

## What Corona measures

A bank of overlapping resonators acts like a channelized radio receiver: each
channel responds most strongly near its tuned frequency. A narrower bandwidth
separates nearby cycles better, but takes longer to respond and rings longer
after an impulse. A bell illustrates this tradeoff. The estimate is most useful
when cycles drift gradually rather than jump abruptly.

The shared estimator removes slow components with a highpass filter, smooths
fast variation with a six-tap FIR filter, and drives identical bandpass filters
with in-phase and quadrature signals. The quadrature follows the derivative
analogy

$$\frac{d\sin(\omega t)}{dt}=\omega\cos(\omega t),\qquad
A^2\sin^2(\omega t)+A^2\cos^2(\omega t)=A^2.$$

Its discrete backward difference approximates the derivative. The amplitude
estimate is therefore not a mathematically exact Hilbert-transform envelope.

Spectrum displays the distribution of cyclic energy. Swing displays the position
of a leading cycle waveform within its recent range. Trend compares price
displacement over approximately a cycle with the cycle amplitude. SNR compares
the measured cycle amplitude with smoothed bar height. The latter three spread
their scalar positions into colored rasters using different heuristics. These
rasters are displays of signal conditions, not probability densities or
statistically calibrated confidence intervals.

## Article, predecessor, book, and copied estimator

For Corona let the channel index be $n=12,13,\ldots,60$ and its period
$P=n/2$. This gives **49 channels, periods 6 through 30 in steps of 0.5 bar**.
With price $x_t$, highpass cutoff $H$, and zero-initialized recursive histories:

$$a_H=\frac{1-\sin(2\pi/H)}{\cos(2\pi/H)},\qquad
h_t=\frac{1+a_H}{2}(x_t-x_{t-1})+a_Hh_{t-1},$$

$$s_t=\frac{h_t+2h_{t-1}+3h_{t-2}+3h_{t-3}+2h_{t-4}+h_{t-5}}{12}.$$

The later Corona listing additionally overrides $s_t=x_t-x_{t-1}$ before
bar 7 and $s_1=0$. Its bank starts only when `CurrentBar > 12`.

$$\delta_t=\max(0.1,\ 0.5-0.015t),\quad
b_n=\cos(4\pi/n),\quad g_{n,t}=\sec(8\pi\delta_t/n),\quad
a_{n,t}=g_{n,t}-\sqrt{g_{n,t}^2-1},$$

$$I_{n,t}=s_t,\qquad Q_{n,t}=\frac{n}{4\pi}(s_t-s_{t-1}),$$

$$R_{n,t}=\frac{1-a_{n,t}}{2}(I_{n,t}-I_{n,t-2})
 +b_n(1+a_{n,t})R_{n,t-1}-a_{n,t}R_{n,t-2},$$

$$J_{n,t}=\frac{1-a_{n,t}}{2}(Q_{n,t}-Q_{n,t-2})
 +b_n(1+a_{n,t})J_{n,t-1}-a_{n,t}J_{n,t-2},\qquad
A_{n,t}^2=R_{n,t}^2+J_{n,t}^2.$$

The two-bar input differences are explicit in both the March EasyLanguage
predecessor and the later Corona listing. **The copied engine also uses a
two-bar difference correctly.** Its field `in_phase_previous` is two bars old
at the moment it is read, because the old value is shifted after evaluating
the recurrence. Renaming state fields would make this less misleading.

Normalize with $M_t=\max_n A_{n,t}^2$. For positive $M_t$ and channel power,
the source's sharpened display transform is

$$d^*_{n,t}=10\log_{10}\left(\frac{1-0.99A_{n,t}^2/M_t}{0.01}\right),\qquad
d_{n,t}=\min(20,\ 0.33d^*_{n,t}+0.67d_{n,t-1}).$$

Zero denotes the hottest channel; 20 denotes the coldest display intensity.
This nonlinear transform is **not** the usual physical attenuation
$-10\log_{10}(A^2/M)$. Before temporal smoothing, the transformed threshold 6
corresponds to relative power approximately 0.970. Selection after smoothing
also depends on channel history.

The centroid and five-bar median are

$$D_t=\frac{\sum_{n:d_{n,t}\le6}(n/2)(20-d_{n,t})}
                 {\sum_{n:d_{n,t}\le6}(20-d_{n,t})},\qquad
\widetilde D_t=\max(6,\operatorname{median}(D_t,\ldots,D_{t-4})).$$

The source retains $D_{t-1}$ if the denominator is zero. The copied engine
resets it to zero and then clamps it to 6. This is a significant discrepancy.
Because display smoothing is performed before selecting channels, even the
current maximum-power channel can temporarily exceed the selection threshold.

| Item | March 2008 predecessor | Corona local source evidence | Copied common engine | Book Chapter 10 |
| --- | --- | --- | --- | --- |
| Price | Default median; prose permits Close | Median in ports | Wrapper defaults are median | Close |
| Prefilter | One-pole HP40, six-tap FIR | One-pole HP30, same FIR | Same recurrence, no early FIR override | Two-pole HP48, SuperSmoother10 |
| Period grid | 8..50, integer | 6..30, half-bar | Same default grid | 10..48, integer |
| Bank startup | After bar 6 | After bar 12 in later listing; C# loop starts at zero-based12 | Begins at sample2; public priming at sample 12 | After bar 12 |
| Relative half bandwidth | Floor .15 | Floor .1 in later listing/C#; surviving TraderStudio uses fixed .1 | Floor .1 with sample-count schedule | Fixed `Bandwidth`; parameter declaration missing locally |
| Power | Instantaneous I/Q sum of squares | Instantaneous I/Q sum of squares | Same | Sum of squared single-filter outputs over a period |
| Period compensation | None | None | None | Divide waveform amplitude by period before squaring |
| Normalizer | Current maximum | Current maximum; later listing substitutes .01 at zero | Current maximum | Fast attack, previous maximum decays by .995 |
| Display | Nonlinear 0..20 transform | Same, then .33/.67 temporal smoothing | Same ordinarily | Normalized linear power 0..1; optional power enhancement |
| Centroid | Transform≤3, weights20−transform | Transform≤6, weights20−transform | Same selection; incorrect empty-set fallback | Power≥.5, power weights |
| Median | 10 bars | 5 bars | 5 values, initially infinity sentinels | No median in spectrum listing |

The book's local code computes
$\mathrm{Power}_P=\sum_{m=0}^{P-1}(\mathrm{BP}_{P,t-m}/P)^2$ when
compensation is enabled. Its explanatory prose calls this averaging, but the
listing has no additional division by $P$. That distinction should be retained
if the comb filter is prepared separately.

The November vendor implementations also differ from one another:

- AmiBroker uses a .15 bandwidth floor, **one-bar** I/Q input differences,
  and no .33/.67 temporal smoothing of spectral intensities. Its adaptive
  Swing filter uses the changing bank bandwidth instead of fixed .1. Swing
  remains on a 0..1 axis, and its aura uses a different logarithmic-distance
  formula rather than the temporal raster recurrence.
- Wealth-Lab calls the median routine on an unpopulated `domCyc` series,
  then immediately overwrites the median result with the unfiltered current
  cycle estimate. Its Trend price subtraction uses an absolute bar index,
  and its old raster values are stored as integers.
- The surviving TraderStudio code sets `delta=0.1` directly rather than
  running the startup narrowing schedule. It corroborates the two-bar bank
  differences and several raster expressions, but missing text makes full
  reconstruction speculative.
- eSignal has enough lost code to prevent reliable reconstruction. Its
  surviving highpass coefficient also has a misplaced parenthesis:
  `1 - sin(angle)/cos(angle)` rather than `(1-sin(angle))/cos(angle)`.

These differences preclude choosing an arbitrary vendor port as the numerical
oracle for the entire family.

Chapter 5's usable bandpass transfer function and recurrence agree with the
two-bar numerator above:

$$H_P(z)=\frac{0.5(1-a)(1-z^{-2})}
 {1-b(1+a)z^{-1}+az^{-2}},\qquad
Q_{\mathrm{quality}}\approx\frac{f_0}{\mathrm{bandwidth}}.
$$

The local chapter also prints a conflicting earlier transfer expression and
has incomplete coefficient notation. It explains the principles; it does not
replace the Corona listings. Chapter 16's heatmaps are related visualization,
not an alternate implementation of these four indicators.

## Per-indicator audit

### Corona Spectrum

Existing outputs are `heatmap`, `dominant_cycle`, and
`dominant_cycle_median`. These should all remain in the master. Additional
useful outputs are channel power, relative power, maximum power, and an explicit
`has_cycle_estimate`/selection diagnostic.

Ordinary filter calculations substantially follow the 2008 family. Differences
come from the shared startup, the centroid fallback, and exceptional zero-power
behavior. Constant or zero inputs yield zero power but an all-zero intensity
heatmap and a cycle of 18 in the copied code: visually every channel is hot,
although no cyclic signal exists. The source's conditional DB assignment can
also retain zero initial intensities. A master should distinguish compatibility
display data from an explicit no-signal diagnostic instead of interpreting
these zeros as measured energy.

### Corona Swing Position

At median period $\widetilde D_t$, with $\omega_t=2\pi/\widetilde D_t$
and fixed $\delta_2=0.1$, use $b=\cos\omega_t$,
$g=\sec(2\omega_t\delta_2)$, and $a=g-\sqrt{g^2-1}$:

$$B_t=\frac{1-a}{2}(x_t-x_{t-2})+b(1+a)B_{t-1}-aB_{t-2},\qquad
q_t=\frac{B_t-B_{t-1}}{\omega_t},$$

$$\ell_t=\frac12B_t+\frac{\sqrt3}{2}q_t.$$

The 60-degree phase rotation follows
$\sin(\theta+\pi/3)=\tfrac12\sin\theta+\tfrac{\sqrt3}{2}\cos\theta$.
The copied code instead uses **$B_{t-1}$** in $\ell_t$, after shifting its
state. This changes phase and cannot be explained by the book. Replace the
truncated `.866` with $\sqrt3/2$ as requested.

The later listing scans historical offsets **0..50 and 0..20 inclusive**,
giving 51 lead values and 21 normalized positions. C# and the copied port keep
50 and 20 values. The normalized position is

$$p_t=\frac{\ell_t-\min\ell}{\max\ell-\min\ell},\quad
r_t=\max p-\min p,\quad
w_t=\begin{cases}0.01&r_t>0.85,\\0.15r_t&\text{otherwise}.\end{cases}$$

The scalar is $10p_t-5$ in supplied code and the copied implementation.
The article prose describes an arbitrary axis −10..10. Keep −5..5 as the
compatibility default and explain that display scaling is configurable.

The source raster suppresses the aura when $r_t>0.8$, despite setting a narrow
width above .85. These different thresholds are explicit design settings,
not truncated constants. When the rolling lead range is zero, the copied
position defaults to 0 and its width can remain zero, leaving a hot raster
and scalar −5. The later listing guards zero width, but not the earlier
division by zero. The master needs an explicit flat-waveform policy.

Preserve `swing_position` and add `normalized_position`, bandpass, quadrature,
lead60, range span, width, and both dominant-cycle estimates.

### Corona Trend Vigor

This reuses the same adaptive $B_t,q_t$, with cycle amplitude
$C_t=\sqrt{B_t^2+q_t^2}$. For a stationary cycle over a linear trend,

$$x_t=m t+A\sin(2\pi t/D+\phi),\qquad x_t-x_{t-D}=mD.$$

Full-cycle subtraction cancels the periodic component independently of phase.
The article's interpretation concerns displacement over the cycle relative to
amplitude, rather than a per-bar slope obtained by additionally dividing by $D$.

The readable C# port computes a period `int(DomCyc−1)`, floors it to 12,
then subtracts `ds[cycPeriod]`. In Wealth-Lab that is an **absolute bar index**,
not an offset from the current bar. The missing Trend expressions in the other
ports prevent establishing the original EasyLanguage lookback convention from
them.

The copied implementation sets $L=\lfloor\widetilde D_t-1\rfloor$, then
subtracts `buffer[len−L]` after appending the current sample. The actual lag is
**$L-1$**, an extra one-bar shift. For a median period 20 it compares with
18 bars ago. At startup it can also compare with zero-padded prices when
the requested history has not yet arrived.

Its ratio and mapping are

$$v_t=\operatorname{clip}_{[-10,10]}
 \left(0.33\frac{\mathrm{Trend}_t}{C_t}+0.67v_{t-1}\right),\qquad
u_t=0.05(v_t+10).$$

The source conditionally updates the ratio; an unassigned persistent variable
retains its preceding value. The copied port instead resets the ratio to zero
if trend or amplitude is zero. This changes both scalar and subsequent raster
state. The copied central width is also different from readable C#:

| Normalized vigor | Copied width | C# width |
| --- | --- | --- |
| Outside .3.. .7 | .01 | .01 |
| .3≤u<.5 | u−.29 | u−.3 |
| .5≤u≤.7 | .71−u | .7−u |

The difference may represent a boundary guard, but it is not numerically the
same recurrence. The original 2008 width is not recoverable conclusively from
the damaged copies. Also, the article's neutral scalar region −2..2 corresponds
to normalized .4.. .6, while the code's aura spans .3.. .7 (scalar −4..4).
Document these independently.

Recommended master policy: use the article's full-cycle displacement with a
clearly stated integer offset, such as $L=\lfloor\widetilde D_t\rfloor$;
provide the source-port `floor(D−1)` convention explicitly if retained for
compatibility. In either case, a lag $L$ must read `buffer[-1−L]`, with
adequate real history. Do not adopt the C# absolute-index error. The choice is
an interpretation of the available sources, not a claim that a recovered
original listing specifies it.

Preserve `trend_vigor`, and add unsmoothed ratio, trend displacement, actual
lookback, cycle amplitude, normalized vigor, width, and dominant-cycle values.

### Corona Signal-to-Noise Ratio

The article defines noise as bar height. A close series alone cannot recover it.
Existing master inputs already include `INPUT_HIGH` and `INPUT_LOW`, so future
fixtures can use `INPUT_CLOSE` as the signal price and corresponding H/L ranges
as the necessary second input.

The surviving source calculations are

$$\mathrm{Average}_t=0.1x_t+0.9\mathrm{Average}_{t-1},\qquad
S_t=0.2\sqrt{M_t}+0.9S_{t-1},$$

$$N_t=0.1\operatorname{median}_5(H_t-L_t)+0.9N_{t-1},\qquad
\mathrm{SNR}_{\mathrm{physical},t}=20\log_{10}(S_t/N_t).$$

The signal weights **sum to 1.1**. This is explicit in the supplied ports,
and the copied code preserves it intentionally. With constant measured
amplitude its steady-state signal is twice that amplitude. Changing .9 to .8
would alter the algorithm; these are design coefficients, not approximations.

The copied normalized display and scalar are

$$z_t=\frac{\operatorname{clip}_{[0,10]}
 (\mathrm{SNR}_{\mathrm{physical},t}+3.5)}{10},\qquad
\mathrm{display}_t=1+10z_t,\qquad w_t=\max(0,0.2-0.4z_t).$$

Thus the current scalar **is not the raw physical dB ratio**: it adds calibration,
clips, and adds a display offset. C# additionally replaces a shifted value
below 1 with 0; the damaged other listings suggest different upper-bound
tests involving 11. The article says an aura develops below 4 dB, while the
copied raster disappears above normalized .5 (mapped scalar 6). These sources
do not define one identical display threshold.

The copied scalar, quote, and trade adapters pass `low=high=price`, so noise
is zero and their display remains 1 on a fresh indicator. A scalar-only master
should require an explicit bar range/noise input for SNR rather than silently
inventing a range. Supporting `update(price, high=..., low=...)` and/or
`update(price, bar_range=...)` keeps the calculation portable.

Confirmed exceptional-input problems:

- Constant positive price with nonzero ranges reaches `log10(0)` and raises
  `ValueError` before priming completes.
- A single NaN high contaminates the recursive noise permanently; the eventual
  display is still 1 rather than an unavailable-value indication.
- Reversed high/low ranges can make the logarithm argument negative.
- Infinite prices are accepted and can leave SNR permanently at its upper bound.

Preserve the mapped `signal_to_noise_ratio`, and additionally return raw physical
dB, calibrated dB, normalized display position, smoothed signal and noise,
median bar range, width, dominant cycle, and a validity diagnostic. Clearly
define no-signal, zero-noise, and zero/zero behavior before fixture generation.

## Heatmap geometry and recurrence

Retain the fields `time`, `parameter_first`, `parameter_last`,
`parameter_resolution`, `value_min`, `value_max`, and `values`. Output columns
must own their data rather than expose mutable recursive buffers. Unprimed
columns can be empty with NaN extrema, as in the prepared ACP master; fixed
fixture rows should contain NaNs for every unavailable output cell.

The copied Heatmap class does not specify resolution units. The wrappers use
**bins per ordinate unit**: Spectrum2, Swing4.9, Trend2.45, SNR4.9. The prepared
ACP master explicitly uses **ordinate units per bin**. Define that contract
for Corona rather than assuming the copied value is a step.

The available Corona-style raster listings scan $j=1,\ldots,50$. For Swing its ordinates are
$-5+0.2j$, hence −4.8 through 5; for Trend, −9.6 through 10; for SNR,
1.2 through 11. Spectrum instead includes both endpoints, 6 and30.
The later Swing listing has a first-plot typo, so the regular ordinate formula
is corroborated by the remaining plots and C#.

The copied wrappers changed their loops to $j=0,\ldots,49$ but retained
`round(50*position)` and a raster step20/50. At normalized position1 the
marker is 50, outside the array. Their advertised endpoint metadata also
does not describe the evaluated raster coordinates. This shifts heatmap cells
even when scalar values agree.

Recommended compatibility geometry: keep the source's logical $j=1..R$;
store it at array index $j-1$. For display bounds $a,b$, set
`parameter_first=a+(b−a)/R`, `parameter_last=b`, and
`parameter_resolution=(b−a)/R`. Report $a,b$ separately as scalar display
bounds. Alternatively, deliberately use an endpoint-inclusive grid and change
all marker/distance formulas consistently; that would be a new raster convention.

For each raster, let $m=\operatorname{round}(Ru)$ and
$d_j=|20u-20j/R|/w$. The source uses different temporal recurrences:

| Raster | Away from marker | At marker | Suppression |
| --- | --- | --- | --- |
| Swing | .5(d^.95+.5 previous); C# also has a top-side d>1 guard | .5 previous | position span>.8 ⇒20 |
| Trend | .8(d^.85+.2 previous) | .5 previous | normalized vigor outside .3.. .7 ⇒20 |
| SNR | .5(d^.8+previous), with an extra top-side d>1 test | .5 previous | normalized SNR>.5 ⇒20 |

Clamp resulting intensities to 0..20. The C# raster stores prior values as
integers; copied Python and later EasyLanguage use floating-point arrays.
Do not introduce C# quantization into a full-precision master.

Python's `round` is ties-to-even; different target languages may use another
rounding rule. Choose and document one explicit nonnegative rounding helper
for conversion. **Rounding alone does not create negative fractional-power
arguments** for finite positions in 0..1: checking 10,001 positions over all
50 cells found none. The actual demonstrated failures arise from invalid
inputs, zero denominators, indexing, and state behavior.

Use `math.pi`, `2*math.pi`, and `sqrt(3)/2` for mathematical constants. The
Corona recurrence itself has no `1.414`; related book SuperSmoother formulas
use `sqrt(2)` and Butterworth angles use `1/sqrt(2)`. Preserve fitted/design
values such as .1, .015, .33, .67, .99, .95, .85, and 3.5 according to
their distinct roles.

## Numerical investigation

[investigate_copied.py](investigate_copied.py) runs the copied estimator and
wrapper bodies with unavailable framework imports removed and only entity
selection/metadata helpers stubbed. It also evaluates narrowly scoped changes
and a full-precision reconstruction of the later source estimator. Execute from
any working directory:

```sh
python3 inputs/john-ehlers/prepared-for-conversion/corona/investigate_copied.py
```

Detailed results are in [investigation_results.json](investigation_results.json).
The harness is investigation tooling; it is not the future master.

All **12 selected existing checks pass**: each wrapper's snapshot, priming,
and NaN-input check. That confirms consistency with the copied Go-derived
snapshots, not independent agreement with the original source. Their tolerance
is 1e−4, and the heatmap checks cover extrema rather than every cell.

All four copied fixture series contain the same 252 **high/low median prices**,
not the requested `INPUT_CLOSE`. Their maximum difference from Close is3.815.
Copied SNR snapshots additionally use synthetic high/low data, with fractional
half-range `.005+.03*(1+sin(.37*i))`; they do not use the available real ranges.

Each experiment below changes only the named expression, retaining the copied
startup and all other behaviors. Differences are measured over 241 outputs
at zero-based indices 11..251, using copied median-price fixtures.

| Isolated change | Maximum difference | Outputs changed >1e−10 | Final copied → modified |
| --- | --- | --- | --- |
| Hold previous DC on empty qualifying set | 24 bars in DC | 49 | 6 →12 |
| Swing uses current BP in Lead60 | 2.47235952462902 | 224 | −.852481206090320 →−1.47773205331391 |
| Swing replaces .866 with sqrt(3)/2 only | .000137545979801423 | 218 | −.852481206090320 →−.852510290252059 |
| Swing windows 51/21 instead of50/20 | 1.13813844206992 | 12 | Final unchanged |
| Trend fixes extra buffer offset only; keeps floor(D−1) | 4.34877992447888 | 198 | −.189498995413885 →−.223661706411129 |

The later estimator reconstruction includes its startup gate, early FIR
override, zero-initialized median history, centroid hold, and .01 zero-power
fallback; pi is upgraded to full precision in both comparisons. On the copied
median input its final DC/median is 12/12 versus copied 6/6. On Close it is
11.5/11.5 versus copied 6/6. This reconstruction establishes numerical
consequences of the **available later source**, not definitive results from
the missing 2008 ELD.

With Close and actual high/low ranges, the copied SNR's final display is
7.26557904561101; supplying zero ranges gives 1. That difference directly
illustrates why high/low inputs matter.

Parameter validation also admits unstable settings. `minimal_period=2`
drives a channel coefficient beyond the stable branch during the broad startup
bandwidth: a bounded unit sine around100 produces maximum power approximately
7.04e14 after 150 samples. `high_pass_filter_cutoff=2` has a pole−1 and
cutoff4 evaluates a removable0/0 form numerically. A master should validate
stability and finite parameters, not only permit integer periods≥2. The
proposed fixtures use the article's safe minimum period6 and HP cutoffs ≥30.

## Recommended master structure and reference policy

```text
prepared-for-conversion/
  corona/
    corona.py              # Shared estimator, snapshots, adaptive BP, Heatmap.
    investigation.md       # This comparison.
    description.md         # Complete shared mathematics and conventions.
    generate_reference.py  # Common deterministic five-language serializer.
  corona-spectrum/
    corona-spectrum.py
    description.md
    test_testdata.py, testdata_test.go, testdata.ts, testdata.rs, testdata.zig
  corona-swing-position/   # Same per-indicator structure.
  corona-trend-vigor/
  corona-signal-to-noise-ratio/
```

The filenames/placement above are proposed. Shared code must import safely
from each indicator's working directory using a small standard-library loader,
or an equivalent explicit package convention. Each indicator documentation
must repeat the shared mathematical contract, initialization, and reference
decisions, so the converter can work without access to the source articles.

A common estimator should advance once per accepted bar and return an owned
snapshot. Standalone wrappers may own an estimator; a four-indicator composite
should update a single estimator and pass that snapshot to each wrapper without
advancing it again. Sharing the estimator object while every wrapper calls
`update` would process each bar four times. The adaptive bandpass state can
also be shared between Swing and Trend when they use identical settings.

Default numerical policy should follow the reconstructed 2008 family rather
than the book comb filter: half-bar period grid, HP30/FIR6, two-bar bank
numerators, .1 bandwidth floor, .33/.67 display smoothing, centroid threshold6,
and median 5. Preserve source hold behavior and explicit startup conventions.
Use the later readable listing to resolve shared/Swing details and identify
which details remain inferred for Trend/SNR. Do not claim that errors in a
vendor port are authoritative merely because that port is readable.

Warm-up and validity are separate: sufficient bar count does not establish
the presence of a tradable cycle. NaN samples should not advance accepted-bar
state, infinities should be rejected before mutation, and SNR must validate
its range input atomically. Finite internal startup periods should replace
infinity sentinels before driving the adaptive filter. Specify first public
output by1-based accepted sample count and store NaNs earlier in fixtures.

## Proposed parameter combinations for confirmation

Use **64 total parameter cases: 16 for each of the four indicators**. No
book-based Corona variant is proposed because none is present in the book.

Eight shared configurations are the Cartesian product of HP cutoff
$H\in\{30,48\}$ and these four period ranges:

| Minimum period | Maximum period | What it tests |
| --- | --- | --- |
| 6 | 30 | Original Corona period range and half-bar spectral channels. |
| 6 | 20 | Reduced upper bound and faster-cycle selection. |
| 10 | 30 | Suppression of short-cycle candidates. |
| 10 | 48 | Extended cycle search beyond the original30-bar range. |

HP30 tests the article setting; HP48 tests changed detrending independent
of the bank bounds. Each of these 8 configurations then receives 2 variants:

| Indicator | Variant1 | Variant2 | What it tests |
| --- | --- | --- | --- |
| Spectrum | Centroid threshold6 | Centroid threshold3 | Original selection versus tighter selection and more frequent centroid holds. |
| Swing | Raster length50 | Raster length25 | Original raster density versus coarser raster with consistent geometry. |
| Trend | Raster length50 | Raster length25 | Vigor normalization, buffer indexing, and raster geometry at two densities. |
| SNR | Raster length50 | Raster length25 | Signal/noise smoothing, display clipping, and two raster densities. |

Keep other settings fixed: upper intensity 20, spectrum half-bar step, shared
median 5, phase lead 60°, Swing windows 51/21, Swing display −5..5, Trend −10..10,
and SNR 1..11. These defaults are recommendations pending selection of the
explicit source/edge conventions above. No need to parameterize every smoothing
coefficient merely to obtain more cases.

Every case should have separate 252-element arrays for each scalar/diagnostic
output and a 252-row heatmap array. Unprimed heatmap fixture rows have a fixed
number of NaN cells; runtime columns may still be empty. Name each output
with an output suffix following its parameter suffix, for example
`EXPECTED_H30_PMIN6_PMAX30_DB6_DOMINANT_CYCLE` and
`EXPECTED_H30_PMIN6_PMAX30_R50_HEATMAP`. Rust uses lowercase shortcuts;
Go/TypeScript/Zig retain the corresponding existing naming conventions.
The output suffix is necessary because each parameter case now has several
outputs. Format finite data to 15 significant decimal digits and document
numeric comparison tolerances independently of decimal formatting.

Copy all five input templates into each wrapper folder. Use Close for the
signal price in every case. For SNR also use the existing High/Low arrays;
export those inputs unchanged in all languages. Fixture comment lines should
state the combined shared/variant purpose and every relevant parameter.
Generation must be reproducible and replace only its own generated section
on rerun instead of accumulating duplicate declarations.

## References and BibTeX

```bibtex
@article{ehlers2008corona,
  author  = {Ehlers, John F.},
  title   = {Corona Charts},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume  = {26},
  number  = {11},
  pages   = {18--24},
  year    = {2008},
  month   = nov,
  url     = {https://technical.traders.com/archive/article.asp?file=\V26\C11\200EHLE.pdf}
}
@article{ehlers2008measuring,
  author  = {Ehlers, John F.},
  title   = {Measuring Cycle Periods},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume  = {26},
  number  = {3},
  pages   = {16--22},
  year    = {2008},
  month   = mar,
  url     = {https://technical.traders.com/archive/article.asp?file=\V26\C03\043EHLR.pdf}
}
@misc{traderstips2008corona,
  author  = {{Technical Analysis, Inc.}},
  title   = {Traders' Tips: Corona Charts},
  year    = {2008},
  month   = nov,
  url     = {https://www.traders.com/Documentation/FEEDbk_docs/2008/11/TradersTips/TradersTips.html},
  note    = {Local Wealth-Lab, TraderStudio, eSignal, and AmiBroker code examined}
}
@misc{traderstips2008spectrum,
  author  = {{Technical Analysis, Inc.}},
  title   = {Traders' Tips: Measuring Cycle Periods},
  year    = {2008},
  month   = mar,
  url     = {http://traders.com/Documentation/FEEDbk_docs/2008/03/TradersTips/TradersTips.html}
}
@misc{tradesignal2012coronaswing,
  author  = {{Tradesignal}},
  title   = {Corona Chart Swing Position},
  year    = {2012},
  month   = apr,
  url     = {https://www.traders.com/Documentation/FEEDbk_docs/2012/04/TradersTips.html},
  note    = {Local EasyLanguage-style EQI listing supplied with April Traders' Tips; later corroborating source}
}
@book{ehlers2013cycle,
  author    = {Ehlers, John F.},
  title     = {Cycle Analytics for Traders: Advanced Technical Trading Concepts},
  publisher = {Wiley},
  year      = {2013},
  series    = {Wiley Trading},
  isbn      = {9781118728604},
  note      = {Chapters 5, 7, 10, 11, and 16 provide related background; no four named Corona implementations}
}
@misc{zpanoCoronaSnapshot,
  author = {{zpano}},
  title  = {Copied Python Corona Estimator and Indicators},
  note   = {Local snapshot under external/zpano/py/indicators/john_ehlers;
            detached from its framework; numerical checks described in this investigation}
}
```
