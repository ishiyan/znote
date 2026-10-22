# Fisher Adaptive Relative Strength Index — Chapter 15 research prototype master

`FisherAdaptiveRelativeStrengthIndex.update(close, time=None)` embeds the complete Chapter 11 RSI and applies Chapter 15 listing 15-1. This is a self-contained standard-library streaming reference for later conversion to five languages; it requires no sibling master. The exact original 252 closes are embedded in `__main__`.

Full `math.pi`, `math.sqrt(2.0)` and its reciprocal replace printed `3.14159`, `1.414` and `.707`. Trigonometric arguments use radians. Design decimals such as .2/.8, source-specific .991/.995, transform gains and clipping stay unchanged. State uses unrounded binary64; only exported data uses 15 significant digits. The original truncated-constant listing will differ slightly.

## Fisher transform of the smoothed adaptive RSI

The returned `FisherOutput` contains `value`, `dominant_cycle` and `lookback_length`. The base smoothed RSI $y_t$ remains in internal diagnostics as `state.base_value`; its feedback is never replaced by Fisher output. Chapter 15 replaces only the Chapter 11 plots:

$$u_t=2(y_t-0.5),\quad v_t=1.5u_t,\quad
\widehat v_t=\min(0.999,\max(-0.999,v_t)),$$

$$F_t=\frac12\ln\left(\frac{1+\widehat v_t}{1-\widehat v_t}\right)=\operatorname{atanh}(\widehat v_t).$$

The source gain **1.5** and clipping threshold **0.999** are fixed design values. Only the amplified transform input is clipped; the base smoother can overshoot $[0,1]$ without altering base feedback. The logarithm uses the printed ratio expression, not an alternative approximation. The plot reference levels $\pm2$ are display guides, not output series or thresholds for automatic trading.

For $|v|\ll1$,

$$\operatorname{atanh}(v)=v+\frac{v^3}{3}+\frac{v^5}{5}+\cdots,\qquad
\frac{d\operatorname{atanh}(v)}{dv}=\frac1{1-v^2}.$$

Small values are nearly linear and extremes are stretched. Clipping makes the actual bound

$$|F_t|\le\operatorname{atanh}(0.999)=\frac12\ln(1999)\approx3.8002011672502.$$

It saturates when $y_t\ge0.833$ or $y_t\le0.167$, rather than only at zero or one. The transform is pointwise and adds no time lag to the adaptive RSI; its existing roof, estimator and smoother still have delay.

The chapter interprets the Fisher output as a Gaussian sigma score and gives associated trading probabilities. **That interpretation is not generally valid.** `atanh` does not turn an arbitrary bounded distribution into a Gaussian. In the unclipped case, the change-of-variable formula is

$$p_F(f)=p_V(\tanh f)\operatorname{sech}^2f.$$

For example uniform input on $[-1,1]$ gives $p_F(f)=\tfrac12\operatorname{sech}^2f$, not a Gaussian. Clipping adds point masses at the bounds. Standard deviation can also be defined for many non-Gaussian distributions. No mean/variance calibration or probability model is computed here, and $\pm2$ are not calibrated probabilities of future price movement. These corrections preserve the numerical listing while clarifying its theoretical limits.

## Adaptive observation interval

A changing oscillator period calls for an observation interval that tracks its cycle. RSI uses half a cycle of upward/downward changes; Stochastic uses a full cycle to include both range extremes. The causal periodogram can be noisy or ambiguous; the selected period is not statistical confidence. Filtering and smoothing retain their delay after the pointwise transform.

## Shared Roofing Filter equations

Let $x_t$ be Close, $H$ be `highpass_period`, $L$ be `smoothing_period`, and $h_t,f_t$ be high-pass and roofed outputs. Periods are in bars. Define

$$\theta_H=\frac{2\pi}{\sqrt2 H},\quad
\alpha_H=\frac{\cos\theta_H+\sin\theta_H-1}{\cos\theta_H},\quad q=1-\alpha_H.$$

$$h_t=(1-\alpha_H/2)^2(x_t-2x_{t-1}+x_{t-2})+2q h_{t-1}-q^2 h_{t-2}.$$

Equation 3-3's SuperSmoother follows:

$$a=e^{-\sqrt2\pi/L},\quad c_2=2a\cos(\sqrt2\pi/L),\quad c_3=-a^2,\quad c_1=1-c_2-c_3,$$

$$f_t=\frac{c_1}{2}(h_t+h_{t-1})+c_2f_{t-1}+c_3f_{t-2}.$$

The transfer functions are

$$H_{HP}(z)=\frac{(1-\alpha_H/2)^2(1-z^{-1})^2}{1-2qz^{-1}+q^2z^{-2}},\quad
H_{SS}(z)=\frac{(c_1/2)(1+z^{-1})}{1-c_2z^{-1}-c_3z^{-2}},\quad H_{Roof}=H_{HP}H_{SS}.$$

Two high-pass poles reject slow spectral dilation; their low-frequency roll-off is approximately 12 dB/octave compared with the source's approximate 6 dB/octave growth of swing amplitude with period. The SuperSmoother reduces high-frequency noise and has a feedforward zero at Nyquist, the highest representable frequency of one-half cycle per bar. Its poles act like an exponentially damped rotation. This is an analogy for the filter, not a physical equation for market prices.

**The oscillator's final SuperSmoother uses these same $c_1,c_2,c_3$ coefficients.** Changing `smoothing_period` changes both roofing smoothing and output smoothing. No independent EMA, clipping or output cutoff is inserted. The roof controls are independent of the searched cycle range; a compact range does not silently retune the roof. Fractional roof periods control coefficients and are not rounded into window lengths.

## Embedded Chapter 11 autocorrelation periodogram

Let $P_0,P_1$ be the minimum and maximum trial periods. All internal lags $\ell=0,\ldots,P_1$ are evaluated. For `averaging_length=A>0` use $M_\ell=A$; for zero use $M_\ell=\ell$. With $X_j=f_{t-j}$ and $Y_j=f_{t-\ell-j}$,

$$S_x=\sum_{j=0}^{M_\ell-1}X_j,\quad S_y=\sum_jY_j,\quad
S_{xx}=\sum_jX_j^2,\quad S_{xy}=\sum_jX_jY_j,\quad S_{yy}=\sum_jY_j^2.$$

$$V_\ell=(M_\ell S_{xx}-S_x^2)(M_\ell S_{yy}-S_y^2),$$

$$r_t(\ell)=\frac{M_\ell S_{xy}-S_xS_y}{\sqrt{V_\ell}}\quad(V_\ell>0).$$

If $V_\ell\le0$, retain the preceding **raw** correlation at that lag, initially zero. Do not map it to colors or reset it to zero. Lag zero at $A=0$ has no samples and retains zero; hidden lags zero through two are not included in the Fourier sum. Five sums visit samples newest first in source order. No centered-sum replacement, clamping or variance epsilon is added.

For every trial period $P=P_0,\ldots,P_1$,

$$C_t(P)=\sum_{n=3}^{P_1}r_t(n)\cos(2\pi n/P),\quad
S_t(P)=\sum_{n=3}^{P_1}r_t(n)\sin(2\pi n/P),$$

$$Q_t(P)=C_t(P)^2+S_t(P)^2,\qquad
R_t(P)=0.2Q_t(P)^2+0.8R_{t-1}(P).$$

The source explicitly squares `SqSum` again: $R$ smooths the **fourth power of Fourier amplitude**, not ordinary magnitude squared. This matters when reproducing dominant periods. The Fourier transform is across lag, while the EMA is across time. The Chapter 11 listings use a full 360-degree angle, without Chapter 8's local 370-degree anomaly.

Let $d$ be the listing-specific decay:

$$G_t=\max(dG_{t-1},\max_PR_t(P)),\quad
p_t(P)=\begin{cases}R_t(P)/G_t,&G_t\ne0,\\0,&G_t=0.\end{cases}$$

$G$ is a fast-attack, slow-decay normalization maximum. No minimum subtraction, cubic color enhancement, separate power normalization or spectral-dilation compensation is inserted. Correlations themselves are amplitude normalized. The zero-maximum branch defines otherwise undefined divisions as an all-zero spectrum, preserving finite feedback. The embedded listing does not guard this zero division; the all-zero spectrum is an explicit finite-stream extension.

Select only normalized bins at or above one-half:

$$W_t=\sum_{P:p_t(P)\ge0.5}p_t(P),\quad
W_{x,t}=\sum_{P:p_t(P)\ge0.5}Pp_t(P),$$

$$D_t^*=\begin{cases}W_{x,t}/W_t,&W_t\ne0,\\D_{t-1},&W_t=0,\end{cases}\qquad
D_t=\min(P_1,\max(P_0,D_t^*)).$$

The source clamps an initially zero dominant period to its lower bound. This master initializes the equivalent fallback to $P_0$. If no cycle ever exists, the public period still becomes $P_0$ once history is primed, because that fallback is used to tune the source indicator. `state.cycle.has_cycle` distinguishes a measured/retained centroid from this fallback. Empty later selections hold the previous cycle. `dominant_cycle` is real-valued and must not be rounded before tuning or division.

**The embedded RSI uses $d=0.991$**, as printed in listing 11-1. The book periodogram and Stochastic use 0.995; composing those would alter the RSI base and is avoided.

## Configuration, API and initialization

| Parameter | Default | Valid range and role |
| --- | --- | --- |
| `min_period` | 10 | Integer $\ge6$; first trial cycle and fallback lower bound. |
| `max_period` | 48 | Integer $\ge\texttt{min_period}$; final trial cycle, including a single-bin range. |
| `averaging_length` | 3 | Integer zero or $\ge2$; zero gives $M=\ell$. One is rejected as a degenerate correlation window. |
| `highpass_period` | 48.0 | Finite real $\ge5$ yielding resolvable stable coefficients. |
| `smoothing_period` | 10.0 | Finite real $\ge2$ yielding resolvable stable coefficients; shared by input and output smoothing. |

`max_period` controls both the Fourier lag range and cycle search. It is not a scalar lookback selected once at construction. Its minimum of six leaves at least a three-change RSI window and keeps all adaptive tunings strictly slower than Nyquist. No arbitrary upper cap is imposed, but storage and computation grow with the chosen range. Coefficient periods so large that poles numerically collapse are rejected. Booleans are not valid numerical parameters.

All absent raw prices, roof outputs, correlations, powers, maximum and output smoother histories are explicitly zero. The first finite Close is accepted as standalone CurrentBar=1. The roof, estimator and oscillator update from that first bar using their defined prehistory, even while public outputs are NaN. A nonzero constant input has an initial transient from absent zero closes. Do not seed prices with the first actual Close, postpone the estimator until full history, clear it when the cycle changes, or replay old oscillator windows.

NaN input means an omitted observation: return all-NaN output and preserve state, accepted count and last accepted `output`. Infinity, bool input, invalid parameters and arithmetic overflow raise `ValueError` before state commit. Time is optional, ignored by scalar calculations. `parameters` is immutable; `samples_seen` counts accepted finite inputs; `warmup_bars` counts leading unavailable outputs; `is_primed` marks full required history, not convergence. `state` exposes immutable diagnostics. `reset()` clears all histories while keeping coefficients and configuration.

The estimator's required correlation history is

$$N_{corr}=P_1+(A\text{ if }A>0\text{ else }P_1).$$

Each public output waits for this full bank history, plus the indicator-specific history stated below. All named output fields share that NaN prefix. Internal state and the prior oscillator result used for smoothing are never replaced by public NaN values. Defaults have $N_{corr}=51$ and publish first at bar 51, index 50. A commercial platform with earlier price data can match this reference only after matching its initial conditions and evaluation history.

## Fixture generation and porting

The user confirmed all **36 combinations**, twelve per folder, on 2026-10-22. Every folder retains the original four 252-element OHLC input arrays in the five language fixtures, although only Close is used. The master embeds the exact Close array in `__main__`. Expected values use 15 significant digits; all-NaN startup rows are exported as ordinary per-component scalar arrays. Parameter tokens are `P0`, `P1`, `A`, `HP`, `LP` with decimal points changed to underscores. Component suffixes identify the named output fields. Each array has a description comment and a parameter/input comment.

Run `python3 fisher-adaptive-relative-strength-index.py` for the streaming demonstration, `python3 fisher-adaptive-relative-strength-index.py --generate-reference-data` to regenerate marked expected sections, and `python3 verify_reference_data.py` to verify all five languages against the master. Python expected arrays are reopened and checked before translating their rounded values to the other languages. Go package names strip hyphens and underscores from the folder name; NaN spelling is `math.NaN()`, TypeScript `NaN`, Rust `f64::NAN` and Zig `nan` using the supplied standard math declarations. All functions/arrays retain the valid language forms of the established fixture templates.

Binary64 libm results can vary in their last bits across languages. Compare NaN placement exactly, and finite values with combined absolute and relative tolerances (for example $10^{-10}$ for this supplied record). A port must preserve the adaptive integer-bound semantics, newest-first sums, source-specific decay, guard conditions and previous-bar ratio definitions. Running future bars must never change earlier returned values.

## Autocorrelation background and source interpretation

Chapter 8 motivates the calculation by analogy with noisy radar reflections: an exponentially filtered random input can retain memory even though its new innovations are random. A one-pole memory model is $y_t=\eta u_t+(1-\eta)y_{t-1}$. The chapter also gives the long-memory power-law form

$$\operatorname{Autocorrelation}(\ell)=C\ell^{-\alpha},\qquad \ell>0,$$

as contextual motivation, not an equation evaluated by this indicator or a universal market law. For an ideal sine wave $f_t=a\sin(2\pi t/T+\phi)$ and an appropriate full-cycle average, the normalized autocorrelation is

$$r(\ell)=\cos(2\pi\ell/T).$$

It is $+1$ at zero/full-cycle lag and $-1$ at half-cycle lag. Thus a Fourier analysis of lag correlations exposes cyclic recurrence, independent of the sine amplitude. Short, finite Pearson windows do not equal this ideal cosine exactly, and may saturate at $\pm1$ for two samples. No physical sinusoidal model is fitted to Close.

The Chapter 8 prose connects cosine and sine parts through the identity

$$a^2=a^2\sin^2(\theta)+a^2\cos^2(\theta).$$

The implementation follows the **actual Chapter 11 fourth-power smoothing expression** already given above. It does not substitute the ordinary power suggested by that prose identity. Similarly, Chapter 8's listing contains 370 degrees and its prose says decay 0.991 while its code says 0.995; each Chapter 11 listing explicitly uses 360 degrees and its own decay. The source code chosen for this master resolves these discrepancies.

The two-pole Roofing Filter is not an ideal brick-wall pass band, and its output is not guaranteed to have an exactly zero mean on every finite record. The book's spectral-dilation and aliasing discussions motivate the cutoffs; they are not empirical validation of this dataset. The SuperSmoother equations above are the complete relevant Equation 3-3 with full mathematical precision and the **positive feedback signs** used in Chapter 11. The modified Butterworth equations elsewhere in Chapter 3 are different filters and are not additional stages here.

The normalization is an amplitude/envelope operation rather than a probability. A strongest period still exists when a noisy record has no economically meaningful cycle. The public fallback and diagnostics let a port reproduce this behavior without interpreting a selected period as statistical confidence.

## RSI calculation and half-cycle rationale

Wilder's original formulation, reproduced in Chapter 11, is

$$RSI_{100}=100-\frac{100}{1+RS},\qquad
RS=\frac{\text{average upward Close changes over 14 bars}}{\text{average downward Close changes over 14 bars}}.$$

Writing the positive sums as $CU,CD$ gives the chapter's full algebraic reduction (the prose's substitution of `RSI = CU / CD` should read `RS = CU / CD`):

$$\begin{aligned}
RSI_{100}&=100-\frac{100}{1+CU/CD}\\
&=100-\frac{100CD}{CD+CU}\\
&=\frac{100CU+100CD-100CD}{CU+CD}\\
&=\frac{100CU}{CU+CD}.
\end{aligned}$$

Removing the display factor 100 yields $RSI=CU/(CU+CD)$. The Chapter 11 adaptive calculation uses **finite sums on roofed Close** rather than Wilder's recursive averages on raw Close.

For the real measured cycle $D_t$, the exact source loop contains

$$K_t=\operatorname{trunc}(D_t/2-1)+1=\lfloor D_t/2\rfloor$$

changes, where the equivalence holds over the accepted $D_t\ge6$. This consumes $K_t+1$ roofed samples. Define

$$\Delta_{t,j}=f_{t-j}-f_{t-j-1},\quad
U_t=\sum_{j=0}^{K_t-1}\max(\Delta_{t,j},0),\quad
V_t=\sum_{j=0}^{K_t-1}\max(-\Delta_{t,j},0),\quad B_t=U_t+V_t.$$

$$q_t=\begin{cases}U_t/B_t,&B_t\ne0,\\q_{t-1},&B_t=0.\end{cases}$$

The output's guard is significant:

$$y_t=\begin{cases}
\frac{c_1}{2}(q_t+q_{t-1})+c_2y_{t-1}+c_3y_{t-2},&B_t\ne0\text{ and }B_{t-1}\ne0,\\
y_{t-1},&\text{otherwise}.
\end{cases}$$

At a zero denominator the retained raw ratio is merely a finite diagnostic convention: the listing does not evaluate either ratio unless both denominators are valid. The **previous** ratio comes from the previous bar's own window $K_{t-1}$; never recompute it using today's $K_t$. When the output holds, its two recursive histories still advance with bar time. The initial ratio, denominators and output histories are zero, so the first nonflat observation alone does not trigger a smoothing update.

A clean sine wave contains one uninterrupted rise over half its period and one uninterrupted fall over the other half. A half-cycle sum can therefore just reach one or zero near those extremes. A much longer sum mixes both directions, while a shorter sum can stick at one extreme. This is the book's motivation for adapting to half a cycle, rather than a proof of optimum trading performance.

The embedded base calculation produces fraction-scale smoothed RSI, a real-valued dominant cycle, and a lookback measured in price changes. The public `value` is its Fisher transform; cycle and lookback diagnostics are exported unchanged. The final SuperSmoother can overshoot the raw ratio's $[0,1]$ interval; no clipping or 100 scaling is applied. The published .3/.7 reference lines are plotting choices, not additional outputs or parameters.

Required public history is

$$N_{RSI}=\max\bigl(N_{corr},\lfloor P_1/2\rfloor+2\bigr),\qquad
\texttt{warmup\_bars}=N_{RSI}-1.$$

The extra sample supports the preceding ratio's largest change window. The default has **50 leading NaNs**; the first public row is bar 51.

## Calculation flow

```mermaid
flowchart TD
    I["Chronological Close"] --> V{"Finite or missing?"}
    V -->|NaN| N["Return all NaNs; preserve state and count"]
    V -->|invalid| E["Reject without state mutation"]
    V -->|finite| R["Two-pole high-pass then input SuperSmoother"]
    R --> A["Raw lag Pearson bank; retain invalid-denominator correlations"]
    A --> D["Lag DFT; fourth-power EMA; source-specific normalization decay"]
    D --> P["Half-power centroid; retain/clamp real dominant cycle"]
    P --> B["Half-cycle changes; raw gain ratio; guarded base RSI smoothing"]
    B --> T["Translate about 0.5; multiply 1.5; clip to ±0.999"]
    T --> F["Fisher log ratio; keep base feedback separate"]
    F --> C{"All candidate arithmetic finite?"}
    C -->|no| E
    C -->|yes| K["Commit every stage together; increment accepted count"]
    K --> W{"Full explicit input history?"}
    W -->|no| U["Return all-NaN public tuple"]
    W -->|yes| O["Return immutable named output"]
```

Candidate arithmetic is separate from commit. A downstream failure cannot leave the roof or cycle estimator one bar ahead. Missing observations do not shift the preceding-value trigger or derivative history. Every returned tuple is immutable and future observations cannot revise it.

For maximum period $P_1$ and $B=P_1-P_0+1$ trial bins, fixed-average updates take $O(P_1A+P_1B)$ work; lag-dependent averages take $O(P_1^2)$ work. Cached trigonometric tables use $O(P_1B)$ memory and bounded dynamic histories use $O(P_1+A)$ for fixed averages or $O(P_1)$ for lag-dependent averages. Adaptive oscillator window work is at most $O(P_1)$ and the final transform is $O(1)$.

## Confirmed reference combinations

All twelve cases were confirmed in the 36-case Chapter 14–15 family plan on 2026-10-22. Each component array contains 252 values.

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.0` | Published defaults and listing-specific periodogram decay. |
| 2 | `min_period=10, max_period=48, averaging_length=0, highpass_period=48.0, smoothing_period=10.0` | Lag-dependent Pearson windows and longer priming history. |
| 3 | `min_period=10, max_period=48, averaging_length=2, highpass_period=48.0, smoothing_period=10.0` | Two-sample Pearson windows with strong sign changes. |
| 4 | `min_period=10, max_period=48, averaging_length=5, highpass_period=48.0, smoothing_period=10.0` | Less reactive fixed correlation window. |
| 5 | `min_period=10, max_period=48, averaging_length=20, highpass_period=48.0, smoothing_period=10.0` | Longer correlation window and delayed tuning. |
| 6 | `min_period=10, max_period=48, averaging_length=100, highpass_period=48.0, smoothing_period=10.0` | Long fixed Pearson history. |
| 7 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.5` | Fractional roofing/output SuperSmoother cutoff. |
| 8 | `min_period=10, max_period=48, averaging_length=3, highpass_period=80.0, smoothing_period=20.0` | Slower independent roofing and output smoothing. |
| 9 | `min_period=6, max_period=24, averaging_length=3, highpass_period=24.0, smoothing_period=6.0` | Compact short-cycle estimator and adaptive windows. |
| 10 | `min_period=20, max_period=20, averaging_length=3, highpass_period=48.0, smoothing_period=10.0` | Single cycle bin, integer-bound window behavior and deterministic tuning. |
| 11 | `min_period=10, max_period=48, averaging_length=204, highpass_period=48.0, smoothing_period=10.0` | 252-observation history boundary: first public result at final close. |
| 12 | `min_period=24, max_period=60, averaging_length=3, highpass_period=60.0, smoothing_period=12.0` | Longer-cycle estimator and adaptive windows. |

## Example, fixture generation and conversion files

```sh
python3 fisher-adaptive-relative-strength-index.py
python3 fisher-adaptive-relative-strength-index.py --generate-reference-data
python3 verify_reference_data.py
python3 -m unittest discover -s . -p 'test_master.py'
```

The default run processes all 252 embedded closes chronologically and prints the last named output. Import a hyphenated research filename with `importlib.util.spec_from_file_location`, then construct `FisherAdaptiveRelativeStrengthIndex()` and call `update(close)` for each observation; a target language may use its idiomatic module naming.

The Python master is the numerical specification and generator; this description is the standalone theoretical specification. `test_testdata.py`, `testdata_test.go`, `testdata.ts`, `testdata.rs`, `testdata.zig` preserve four input arrays and contain **36 expected component arrays per language**. `test_master.py` compares the bounded stream against an independent full-history source transcription. `verify_reference_data.py` checks all five languages' exact rounded values, comments, names, dimensions, NaNs and preserved inputs.

The generator writes Python expected arrays first, reopens them and checks every 15-significant-digit value, then translates those authoritative rounded literals into the other four languages. Re-running replaces only the marked generated section. Names use uppercase parameter shortcuts after `EXPECTED_`, a component suffix, and underscores instead of decimal points; Go/TypeScript/Zig start `expected` and Rust uses `expected_` plus lowercase shortcuts. Go package names strip hyphens/underscores. NaNs are Python/TypeScript `NaN`, Go `math.NaN()`, Rust `f64::NAN` and Zig `nan` with standard math declarations. Every array has the two approved description/parameter comments.

Keep binary64 recursive state unrounded in every port. Preserve operation order and full mathematical constants; finite libm results can vary in their last bits, so compare finite port results with a combined absolute/relative tolerance such as $10^{-10}$ and NaN masks exactly. No foreign-language indicator implementation is claimed merely because its fixtures compile.

## Validation record

Completed on 2026-10-22:

- **10 Python tests passed** in this folder; **32** passed across the three-master family. All twelve confirmed cases match an independent full-history transcription of the source, including internal values and public NaN masks. Zero input, reset, immutable snapshots, skipped inputs, parameter validation and atomic arithmetic/transform rejection passed.
- Exact five-language fixture verification passed: **36 arrays and 9,072 values per language** in this folder. Family total is **108 arrays and 27,216 values per language**. Original OHLC inputs, every 15-significant-digit decimal, NaN mask, name and both metadata comments are verified.
- All five fixtures in this folder regenerate **byte-for-byte identically**; family total is fifteen files.
- Go 1.27.1, Rust 1.98.1 and Zig 0.16.0 compiled and ran fixture harnesses checking every expected array's length, finite/NaN partition and final value. Node 24.15.0 loaded the TypeScript fixtures with type stripping and passed the same checks. A separate TypeScript compiler was not used.
- Python syntax, whitespace and local source-reference links passed.

The independent source oracle uses full-precision mathematical constants and the documented zero-prehistory/undefined-division conventions, with a combined absolute/relative comparison tolerance of $5\times10^{-10}$. TradeStation was not executed; its platform history and truncated mathematical constants can change results. The fixture verifier compares exact rounded export values. Foreign compiler checks validate reference fixtures, not completed indicator ports.

Tests exercise clipping saturation and verify that Fisher output stays separate from base RSI feedback. The A204 case has one finite output at the final close, while a separately tested A205 requirement leaves the whole record unprimed.

## Sources and BibTeX

The numerical authority is Chapter 15 listing 15-1 applied to Chapter 11 listing 11-1. Shared theory is Chapter 3 equation 3-3, Chapter 7 Roofing Filter and Chapter 8 autocorrelation/periodogram. The numerical source-specific normalization decay is 0.991. No newer RSI/Stochastic or generic Fisher implementation replaces this base.

- John F. Ehlers, *Cycle Analytics for Traders: Advanced Technical Trading Concepts*, Wiley, 2013. [Book and bibliographic record](../../2013-cycle-analytics-for-traders/toc.md), [Chapter 14](../../2013-cycle-analytics-for-traders/ch14.md), [Chapter 15](../../2013-cycle-analytics-for-traders/ch15.md), [Chapter 11](../../2013-cycle-analytics-for-traders/ch11.md), [Chapter 3](../../2013-cycle-analytics-for-traders/ch3.md), [Chapter 7](../../2013-cycle-analytics-for-traders/ch7.md), [Chapter 8](../../2013-cycle-analytics-for-traders/ch8.md).

```bibtex
@Book{ehlers2013cycle,
  author = {Ehlers, John F.},
  title = {Cycle Analytics for Traders: Advanced Technical Trading Concepts},
  publisher = {Wiley},
  year = {2013},
  series = {Wiley Trading},
  isbn = {9781118728604}
}
```

Wilder is cited by the Chapter 11 narrative for historical RSI background; his original recursive RSI is not the numerical algorithm of this master. The original book was not independently consulted.

```bibtex
@Book{wilder1978new,
  author = {Wilder, J. Welles, Jr.},
  title = {New Concepts in Technical Trading Systems},
  publisher = {Hunter},
  address = {Winston-Salem, NC},
  year = {1978}
}
```

The following source excerpts retain printed approximations and historical interpretation. Port the full-precision equations and explicit finite-stream rules above. Statistical claims in the historical text do not supersede the qualifications above.

## Original Chapter 11 section and Listing 11-1

The following local book section is included so a conversion agent can inspect the complete published calculation without access to the input repository. The EasyLanguage listing retains its printed constants and comments, including source errors already explained above. **Port the full-precision equations and explicit initialization/undefined-division rules in this document**, rather than treating these printed approximations as the fixture authority. Figure assets are omitted; captions are retained. Claims in the historical source narrative do not replace the mathematical interpretations above.


Welles Wilder had just introduced the RSI3 when I began trading. I asked my broker why 14 days was used in the calculation. His response was ­something like “because Wilder said so.” You have no idea how unsatisfying that response was to an engineer, and that started me on my decades-long quest to find the optimum indicator settings. I think I can now describe those optimum settings.

Wilder's original RSI was defined by

$$RSI = 100 - \frac{100}{1 + RS}$$

where

$$RS = \frac{\text{Average of 14 day's closes UP}}{\text{Average of 14 day's closes DOWN}}$$

"Closes UP" meant that if today's close was higher than yesterday's close, we would add the difference in closing prices to the average. Similarly, "closes DOWN" meant that if today's close was lower than yesterday's, we would add the positive difference in closing prices to the average. We can simplify the RSI equation if we substitute $RSI = CU / CD$. Then,

$$RSI = 100 - \frac{100}{1 + \frac{CU}{CD}} = 100 - \frac{100 \cdot CD}{CD + CU} = \frac{100 \cdot CU + 100 \cdot CD - 100 \cdot CD}{CU + CD} = \frac{100 \cdot CU}{CU + CD}$$

Increasing generality, $CU$ can mean the sum of closes up over any interval, and $CD$ can mean the sum of closes down over the same period. Additionally, the factor of 100 is recognized as providing a simple scaling. So, RSI is just the ratio of the sum of closes up to the sum of the absolute value of all the differential closing prices.

$$RSI = \frac{CU}{CU + CD}$$

The question then becomes what is the best length to use for the RSI summation. If we use an extremely long length, then the closes up will be approximately half of the absolute value of all the closing price differentials. In this case, the RSI would hover near $0.5$ and would be basically worthless. However, if the length used for summation is very short, then the RSI would be stuck at $1$ for extended periods in uptrends and would be stuck at $0$ for extended periods in downtrends. In a perfect world where prices swing as a sine wave having the period of the dominant cycle, the RSI would just touch the value of $1$ if the upswing half of the dominant cycle is used for the summation. Similarly, the RSI would just touch the value of $0$ if the downswing half of the dominant cycle is used for the summation. Therefore, to get the optimum swing of the RSI indicator, the best adaptive summation length to use is half the measured dominant cycle.

The adaptive RSI starts with the computation of the dominant cycle using the autocorrelation periodogram approach. Rather than describing the computations, the reader is referred to the description in Chapter 8. Code Listing 11-1 contains the EasyLanguage code for the adaptive RSI, and the identification of the RSI indicator itself following the dominant cycle calculation is noted by the comment near the end. Since the objective is to use only those frequency components passed by the roofing filter, the variable Filt is used as a data input rather than closing prices. Rather than independently taking the averages of the numerator and denominator, I chose to perform smoothing on the ratio using the SuperSmoother filter described in Chapter 3. The coefficients for the SuperSmoother filters have previously been computed in the dominant cycle measurement part of the code. I have included reference lines at the $30$ percent and $70$ percent levels, but these can easily be adjusted to $20$ percent/$80$ percent or whatever else serves the purpose.

**Code Listing 11-1. EasyLanguage Code for the Adaptive RSI**

```easylanguage
{
  Adaptive RSI
  (c) 2013 John F. Ehlers
}
Vars:
  AvgLength(3),
  M(0),
  N(0),
  X(0),
  Y(0),
  alpha1(0),
  HP(0),
  a1(0),
  b1(0),
  c1(0),
  c2(0),
  c3(0),
  Filt(0),
  Lag(0),
  count(0),
  Sx(0),
  Sy(0),
  Sxx(0),
  Syy(0),
  Sxy(0),
  Period(0),
  Sp(0),
  Spx(0),
  MaxPwr(0),
  DominantCycle(0),
  Color1(0),
  Color2(0),
  Color3(0);

Arrays:
  Corr[48](0),
  CosinePart[48](0),
  SinePart[48](0),
  SqSum[48](0),
  R[48, 2](0),
  Pwr[48](0);

//Highpass filter cyclic components whose periods are shorter than 48 bars
alpha1 = (Cosine(.707*360 / 48) + Sine (.707*360 / 48) - 1) / Cosine(.707*360 / 48);

HP = (1 - alpha1 / 2)*(1 - alpha1 / 2)*(Close - 2*Close[1] + Close[2]) + 2*(1 - alpha1)*HP[1] - (1 - alpha1)*(1 - alpha1)*HP[2];

//Smooth with a Super Smoother Filter from equation 3-3
a1 = expvalue(-1.414*3.14159 / 10);
b1 = 2*a1*Cosine(1.414*180 / 10);
c2 = b1;
c3 = -a1*a1;
c1 = 1 - c2 - c3;
Filt = c1*(HP + HP[1]) / 2 + c2*Filt[1] + c3*Filt[2];

//Pearson correlation for each value of lag
For Lag = 0 to 48 Begin
  //Set the averaging length as M
  M = AvgLength;
  If AvgLength = 0 Then M = Lag;
  Sx = 0;
  Sy = 0;
  Sxx = 0;
  Syy = 0;
  Sxy = 0;

  For count = 0 to M - 1 Begin
    X = Filt[count];
    Y = Filt[Lag + count];
    Sx = Sx + X;
    Sy = Sy + Y;
    Sxx = Sxx + X*X;
    Sxy = Sxy + X*Y;
    Syy = Syy + Y*Y;
  End;

  If (M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy) > 0 Then Corr[Lag] = (M*Sxy - Sx*Sy)/SquareRoot((M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy));
End;

For Period = 10 to 48 Begin
  CosinePart[Period] = 0;
  SinePart[Period] = 0;

  For N = 3 to 48 Begin
    CosinePart[Period] = CosinePart[Period] + Corr[N]*Cosine(360*N / Period);
    SinePart[Period] = SinePart[Period] + Corr[N]*Sine(360*N / Period);
  End;

  SqSum[Period] = CosinePart[Period]*CosinePart[Period] + SinePart[Period]*SinePart[Period];
End;

For Period = 10 to 48 Begin
  R[Period, 2] = R[Period, 1];
  R[Period, 1] = .2*SqSum[Period]*SqSum[Period] + .8*R[Period, 2];
End;

//Find Maximum Power Level for Normalization
MaxPwr = .991*MaxPwr;
For Period = 10 to 48 Begin
  If R[Period, 1] > MaxPwr Then MaxPwr = R[Period, 1];
End;

For Period = 3 to 48 Begin
  Pwr[Period] = R[Period, 1] / MaxPwr;
End;

//Compute the dominant cycle using the CG of the spectrum
Spx = 0;
Sp = 0;
For Period = 10 to 48 Begin
  If Pwr[Period] >= .5 Then Begin
    Spx = Spx + Period*Pwr[Period];
    Sp = Sp + Pwr[Period];
  End;
End;

If Sp <> 0 Then DominantCycle = Spx / Sp;
If DominantCycle < 10 Then DominantCycle = 10;
If DominantCycle > 48 Then DominantCycle = 48;

//Adaptive RSI starts here, using half the measured dominant cycle for tuning
Vars:
  ClosesUp(0),
  ClosesDn(0),
  Denom(0),
  MyRSI(0);

ClosesUp = 0;
ClosesDn = 0;

For count = 0 to IntPortion(DominantCycle / 2 - 1) Begin
  If Filt[count] > Filt[count + 1] Then ClosesUp = ClosesUp + (Filt[count] - Filt[count + 1]);
  If Filt[count] < Filt[count + 1] Then ClosesDn = ClosesDn + (Filt[count + 1] - Filt[count]);
End;

Denom = ClosesUp + ClosesDn;
If Denom <> 0 and Denom[1] <> 0 Then MyRSI = c1*(ClosesUp / Denom + ClosesUp[1] / Denom[1]) / 2 + c2*MyRSI[1] + c3*MyRSI[2];

Plot1(MyRSI);
Plot2(.7);
Plot6(.3);
```

The adaptive RSI has been applied to Dollar General (symbol DG) over roughly the last year in Figure 11.1. Note that the indicator reaches zero or one only when the prices have had a cyclic swing over half the period of the dominant cycle. These events happen relatively rarely, and show that the indicator is properly tuned.

[The source figure is omitted; its caption is retained below.]

**Figure 11.1** *Adaptive RSI Is Properly Tuned to Half the Dominant Cycle Period*


## Original Chapter 15 transform section



A common fallacy in the use of technical indicators is that their probability distribution follows a normal, or Gaussian, probability distribution. That just is not so, as you can prove for yourself by analyzing a reasonable amount of data. If the data do not have a normal probability distribution, then the calculation of a standard deviation is based on a false premise. The purpose of the Fisher transform is to take any indicator having a nominally zero mean and bounded between the limits of −1 to +1 and convert the amplitude so that the transformed indicator has an approximate normal probability distribution.

Plotting an indicator scaled to a normal probability distribution has a huge advantage on indicator interpretation. If the transformed indicator has a value of $−1$, it has a value of negative one standard deviation and therefore there is a $32$ percent chance prices will go lower. If the transformed indicator has a value of $−2$, it has a value of negative two standard deviations, and therefore there is only an $8$ percent chance prices will go lower. This is a high-probability buying opportunity. At a level of $−3$, the negative $3$ standard deviations means there is only a $2$ percent chance of the prices going lower. The transformed values are symmetrical, so positive deviations are high-probability indications to exit a long position or to sell short.

The equation for a Fisher transform is

 $$\text{Output} = 0.5\ln\left(\frac{1+\text{Input}}{1-\text{Input}}\right)$$

Since an input value of unity can cause the ratio to go to infinity, the input must be limited to $0.999$, which corresponds to an output on the order of three standard deviations. Similarly, the argument of the natural logarithm cannot be allowed to go to zero, and so the input must also be limited at $−0.999$.

The transfer response of the Fisher transform is shown in Figure 15.1. The straight line shows the range of inputs, and the curved line shows the corresponding range of outputs. When the inputs are less than an absolute value of $0.5$, the outputs are almost the same as the inputs. However, there is a greater and greater magnification of the outputs as the inputs approach the absolute value of $1$. It is this nonlinear magnification that produces the “long tails” in the output probability distribution, thus creating the resulting normal probability distribution.

[Source figure omitted; caption retained.]

**Figure 15.1** *Transfer Response of the Fisher Transform Shows Greater Magnification of the Outputs as the Inputs Approach an Absolute Value of 1*

To implement the Fisher transform on the adaptive RSI, replace the plot statements of Code Listing 11-1 with the following code fragment:

**Code Listing 15-1. EasyLanguage Code Fragment to Add the Fisher Transform to the Adaptive RSI Indicator**

```easylanguage
Vars:
  TranslatedRSI(0),
  AmplifiedRSI(0),
  Fish(0);

TranslatedRSI = 2*(MyRSI - .5);
AmplifiedRSI = 1.5*TranslatedRSI;
If AmplifiedRSI > .999 Then AmplifiedRSI = .999;
If AmplifiedRSI < -.999 Then AmplifiedRSI = -.999;
Fish = .5*Log((1 + AmplifiedRSI) / (1 - AmplifiedRSI));

Plot1(Fish);
Plot2(2);
Plot6(-2);
```

The variable `MyRSI` ranges between zero and one, and therefore to accommodate the conditions for the Fisher transform, this variable must be translated and dilated to range between $−1$ and $+1$. If the `MyRSI` variable does not range fully between zero and one, you can shorten the RSI lookback period to be less than half the measured dominant cycle, or you can simply multiply it by a magnification factor as I have done in the code fragment. The amplifying factor was selected to make the indicator rarely exceed the two sigma points in the output. The amplified RSI is then limited to be within the range of $−0.999$ to $+0.999$ to avoid a computer crash, and then is used to compute the Fisher transform. The plus and minus two standard deviation levels are included in the indicator display. An example of the adaptive RSI using the Fisher transform is shown in Figure 15.2. The trend up is heralded by the Fisherized indicator’s falling below $−2$. Then, the trend down is signaled by the Fisherized indicator rising above $+2$. These major turning points are relatively rare events and are perhaps best used in association with trend trading.

[Source figure omitted; caption retained.]

**Figure 15.2** *Adaptive RSI with Fisher Transform Clearly Identifies Major Turning Points*

Since the Stochastic and commodity channel index (CCI) indicators measure relative position in a channel, they tend to be near the upper or lower limits during trends. That means that they do not have a zero mean in the short run and therefore are not good candidates on which to apply the Fisher transform. A band-pass filter would be a much better candidate, but the major cyclic turning points are already easy to identify and don’t require a more complex statistical approach.

