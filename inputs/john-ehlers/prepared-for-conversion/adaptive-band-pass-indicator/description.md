# Adaptive Band-Pass Indicator — Chapter 11 research prototype master

## Numerical authority and scope

This is a **research prototype master reference** for later conversion to Python, Go, TypeScript, Rust and Zig. The numerical authority is John F. Ehlers, *Cycle Analytics for Traders: Advanced Technical Trading Concepts* (Wiley, 2013), **Chapter 11**, using this indicator's own listing. The Python file embeds its whole Roofing Filter and autocorrelation periodogram; there are no runtime imports from another master, zpano, NumPy or pandas. Each chronological `update(close, time=None)` consumes one scalar Close and returns a named tuple. All indicator helpers are above the fixture-tooling separator, and the original 252 Close values are embedded in `__main__`.

The shared book machinery is reproduced below, followed by this indicator's calculation, source decisions, reference grid and original source appendix. A copied folder is sufficient for conversion agents without the source book. Article masters with similar names, Swami variants and traditional textbook oscillator definitions do not replace the Chapter 11 listing.

Full mathematical constants are used: `math.pi`, `math.sqrt(2.0)` and its reciprocal replace the printed `3.14159`, `1.414` and `.707`. Trigonometric functions use radians. Design decimals such as `.2`, `.8`, `.991`, `.995`, `.015`, `.9`, `.7`, `1.3` and `.93` retain their printed values. All state remains unrounded binary64; only output serialization uses 15 significant decimal digits. Consequently exact output differs slightly from code retaining the truncated mathematical constants. The calculation flow, guard conditions and ordering remain the authority.

## Why tune an oscillator to a measured cycle?

A fixed lookback measures different fractions of a changing cycle. A short RSI can spend much of a swing at one extreme, while an excessively long one can average upward and downward movement toward neutrality. Stochastic and CCI need a longer interval to capture both sides of a cyclic price range. The book adapts these intervals using a measured dominant period, with an independent Roofing Filter first excluding slow trends and fast noise.

The engineering analogy is a measurement instrument whose observation interval tracks the oscillation being measured. The Band-Pass indicator instead acts like a tunable damped resonator, retuned as the measured pitch changes. Adaptation is causal and reactive; filtering, correlation windows and recursive state introduce delay. None of the resulting values is a calibrated success probability or proof of a market oscillator. The book's optimum-cycle motivation relies on a locally oscillatory signal; nonstationary, noisy prices may have a weak, changing or ambiguous dominant period.

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

For RSI, Stochastic and CCI, the final SuperSmoother uses the same $c_1,c_2,c_3$ coefficients. **Band-Pass has no final SuperSmoother**: changing `smoothing_period` changes its input roofing only. No independent EMA, clipping or output cutoff is inserted. The roof controls are independent of the searched cycle range; a compact range does not silently retune the roof. Fractional roof periods control coefficients and are not rounded into window lengths.

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

$G$ is a fast-attack, slow-decay normalization maximum. No minimum subtraction, cubic color enhancement, separate power normalization or spectral-dilation compensation is inserted. Correlations themselves are amplitude normalized. The zero-maximum branch defines otherwise undefined divisions as an all-zero spectrum, preserving finite feedback. CCI explicitly guards normalization in its source; other listings do not, so this is a documented extension for an initially zero signal.

Select only normalized bins at or above one-half:

$$W_t=\sum_{P:p_t(P)\ge0.5}p_t(P),\quad
W_{x,t}=\sum_{P:p_t(P)\ge0.5}Pp_t(P),$$

$$D_t^*=\begin{cases}W_{x,t}/W_t,&W_t\ne0,\\D_{t-1},&W_t=0,\end{cases}\qquad
D_t=\min(P_1,\max(P_0,D_t^*)).$$

The source clamps an initially zero dominant period to its lower bound. This master initializes the equivalent fallback to $P_0$. If no cycle ever exists, the public period still becomes $P_0$ once history is primed, because that fallback is used to tune the source indicator. `state.cycle.has_cycle` distinguishes a measured/retained centroid from this fallback. Empty later selections hold the previous cycle. `dominant_cycle` is real-valued and must not be rounded before tuning or division.

**RSI and CCI use $d=0.991$; Stochastic and Band-Pass use $d=0.995$.** These are distinct source listings. The existing `auto-correlation-periodogram` master's `source="book"` uses 0.995 and therefore does not reproduce RSI/CCI simply by composition. Each adaptive folder embeds the correct engine. The BP listing clamps only the lower period explicitly; a centroid of finite in-range powers cannot exceed $P_1$, so the shared upper clamp has equivalent behavior.

## Configuration, API and initialization

| Parameter | Default | Valid range and role |
| --- | --- | --- |
| `min_period` | 10 | Integer $\ge6$; first trial cycle and fallback lower bound. |
| `max_period` | 48 | Integer $\ge\texttt{min_period}$; final trial cycle, including a single-bin range. |
| `averaging_length` | 3 | Integer zero or $\ge2$; zero gives $M=\ell$. One is rejected as a degenerate correlation window. |
| `highpass_period` | 48.0 | Finite real $\ge5$ yielding resolvable stable coefficients. |
| `smoothing_period` | 10.0 | Finite real $\ge2$ yielding resolvable stable coefficients; used by input roofing smoothing; no final smoothing stage. |

`max_period` controls both the Fourier lag range and cycle search. It is not a scalar lookback selected once at construction. Its minimum of six leaves at least a three-change RSI window and keeps all adaptive tunings strictly slower than Nyquist. No arbitrary upper cap is imposed, but storage and computation grow with the chosen range. Coefficient periods so large that poles numerically collapse are rejected. Booleans are not valid numerical parameters.

All absent raw prices, roof outputs, correlations, powers, maximum, output smoother histories and historical means are explicitly zero. The first finite Close is accepted as standalone CurrentBar=1. The roof, estimator and oscillator update from that first bar using their defined prehistory, even while public outputs are NaN. A nonzero constant input has an initial transient from absent zero closes. Do not seed prices with the first actual Close, postpone the estimator until full history, clear it when the cycle changes, or replay old oscillator windows.

NaN input means an omitted observation: return all-NaN output and preserve state, accepted count and last accepted `output`. Infinity, bool input, invalid parameters and arithmetic overflow raise `ValueError` before state commit. Time is optional, ignored by scalar calculations. `parameters` is immutable; `samples_seen` counts accepted finite inputs; `warmup_bars` counts leading unavailable outputs; `is_primed` marks full required history, not convergence. `state` exposes immutable diagnostics. `reset()` clears all histories while keeping coefficients and configuration.

The estimator's required correlation history is

$$N_{corr}=P_1+(A\text{ if }A>0\text{ else }P_1).$$

Each public output waits for this full bank history, plus the indicator-specific history stated below. All named output fields share that NaN prefix. Internal state and the prior oscillator result used for smoothing are never replaced by public NaN values. Defaults have $N_{corr}=51$; most default family members publish first at bar 51, index 50. CCI has a longer historical-mean requirement. A commercial platform with earlier price data can match this reference only after matching its initial conditions and evaluation history.

## Fixture generation and porting

The user confirmed all **48 combinations**, twelve per folder, on 2026-10-22. Every folder retains the original four 252-element OHLC input arrays in the five language fixtures, although only Close is used. The master embeds the exact Close array in `__main__`. Expected values use 15 significant digits; all-NaN startup rows are exported as ordinary per-component scalar arrays. Parameter tokens are `P0`, `P1`, `A`, `HP`, `LP` and `B`, with decimal points changed to underscores. Component suffixes identify the named output fields. Each array has a description comment and a parameter/input comment.

Run `python3 adaptive-band-pass-indicator.py` for the streaming demonstration, `python3 adaptive-band-pass-indicator.py --generate-reference-data` to regenerate marked expected sections, and `python3 verify_reference_data.py` to verify all five languages against the master. Python expected arrays are reopened and checked before translating their rounded values to the other languages. Go package names strip hyphens and underscores from the folder name; NaN spelling is `math.NaN()`, TypeScript `NaN`, Rust `f64::NAN` and Zig `nan` using the supplied standard math declarations. All functions/arrays retain the valid language forms of the established fixture templates.

Binary64 libm results can vary in their last bits across languages. Compare NaN placement exactly, and finite values with combined absolute and relative tolerances (for example $10^{-10}$ for this supplied record). A port must preserve the adaptive integer-bound semantics, newest-first sums, source-specific decay, guard conditions and previous-bar ratio/mean definitions. Rewriting the mean into a fixed-window rolling update is incorrect because its window changes. Running future bars must never change earlier returned values.

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

## Adaptive resonator, normalization and plotted trigger

Let $B$ be the fractional `bandwidth`, default .3, and tune the resonator to a period ten percent shorter than the measured cycle:

$$T_t=0.9D_t,\quad
\beta_t=\cos(2\pi/T_t),\quad
\gamma_t=\frac{1}{\cos(2\pi B/T_t)},\quad
\alpha_t=\gamma_t-\sqrt{\gamma_t^2-1}.$$

For every accepted bar, recompute these coefficients from the **real** $D_t$. Keep all previous filter states when $T_t$ changes. The two-pole recurrence, from Equation 5-2 and Listing 11-4, is

$$v_t=\frac{1-\alpha_t}{2}(f_t-f_{t-2})+
\beta_t(1+\alpha_t)v_{t-1}-\alpha_tv_{t-2}.$$

Override $v_t=0$ on accepted CurrentBar one and two, exactly as the listing does. The Roofing Filter and cycle estimator still advance on those bars.

For a fixed tuning, the unnormalized transfer function is

$$H_{BP}(z)=\frac{0.5(1-\alpha)(1-z^{-2})}
{1-\beta(1+\alpha)z^{-1}+\alpha z^{-2}}.$$

It has zeros at DC and Nyquist; its denominator is that of a damped resonator. The narrow-band electronic-circuit analogy uses the Chapter 5 quality-factor relations

$$Q\simeq\frac{f_0}{\Delta f}\simeq\frac1B,\qquad
Q=2\pi\frac{\text{energy stored}}{\text{energy dissipated per cycle}}.$$

The chapter's example $Q=20/(23-17)=3.33$ motivates the default 30 percent bandwidth. Smaller bandwidth increases selectivity and prolongs impulse ringing; wider bandwidth reacts faster but passes more neighboring frequencies. The approximate Q relationship is explanatory, not another computed output.

For completeness, the supplied Chapter 5 text first prints Equation 5-1 as

$$H(z)=\frac{1-\sigma z^{-1}}{(1-\gamma z^{-1})(1-\gamma z^{-2})},$$

then prints the implemented two-pole form

$$H(z)=\frac{0.5(1-\sigma)(1-z^{-2})}
{1-\lambda(1+\sigma)z^{-1}+\sigma z^{-2}}.$$

These expressions are not algebraically identical as printed. Chapter 11's complete coefficient definitions and recurrence resolve that source inconsistency: use the second form with $\sigma=\alpha$, $\lambda=\beta$. The first expression is reproduced for source context and is not used in this master.

The envelope AGC and public curves are

$$E_t=\max(0.991E_{t-1},|v_t|),\qquad
s_t=\begin{cases}v_t/E_t,&E_t\ne0,\\s_{t-1},&E_t=0,\end{cases}\qquad
\operatorname{trigger}_t=0.9s_{t-1}.$$

With finite state, $s_t\in[-1,1]$ and the trigger lies in $[-.9,.9]$. The spectral maximum uses a different decay, .995. Do not confuse this normalization with the spectral AGC or with a rolling maximum.

The source additionally computes an **unplotted** leading curve:

$$\ell_t=\frac{1.3}{4}(s_t+s_{t-1}-s_{t-2}-s_{t-3}),\quad
E^\ell_t=\max(0.93E^\ell_{t-1},|\ell_t|),$$

$$s^\ell_t=\begin{cases}0.7\ell_t/E^\ell_t,&E^\ell_t\ne0,\\s^\ell_{t-1},&E^\ell_t=0.\end{cases}$$

These variables are preserved in `state.lead`, `state.lead_peak` and `state.lead_signal`. `Plot14` is the delayed .9 signal trigger, **not** `LeadSignal`. The source also plots zero and .707/- .707; with full mathematical precision the latter levels represent $\pm1/\sqrt2$. They are display constants and do not alter the numerical outputs. The chapter's prose uses approximately .7 for signal-crossing examples.

A fixed resonator tuned exactly to a stationary sine wave has zero relative phase at its center after transients. Tuning to a shorter period produces phase lead at the measured sine frequency. Chapter 11 estimates roughly 60 degrees, or $D_t/6$ bars (three bars for an 18-bar cycle), for its default detuning. The lead depends on bandwidth, frequency and transients; it is not a guaranteed future-price prediction, and the preceding Roofing Filter adds its own phase. The running adaptive system is time-varying, so a single fixed transfer function only describes frozen coefficients.

| Additional parameter | Default | Valid range |
| --- | --- | --- |
| `bandwidth` | 0.3 | Finite real $0<B<0.9P_0/4$ and numerically resolvable stable coefficients throughout the tuning range. |

This keeps the bandwidth angle below $\pi/2$ so $\gamma>1$ and $0<\alpha<1$. Very tiny bandwidths that round $\gamma$ to one, or values so close to the upper limit that cancellation collapses $\alpha$, are rejected. The .9 tuning factor, .991 signal-peak decay, .995 spectral decay, .93 lead-peak decay, 1.3 lead gain and .7 lead scaling are fixed source design choices.

The returned `BandPassOutput` fields are `signal`, `trigger`, `dominant_cycle` (real bars) and `tuned_period` ($0.9D_t$ bars). There is no final oscillator SuperSmoother: `smoothing_period` changes only the input roof for this member. Required public history is

$$N_{BP}=\max(N_{corr},4),\qquad
\texttt{warmup\_bars}=N_{BP}-1.$$

The default has **50 leading NaNs** and publishes first at bar 51. The four-signal lead expression has the complete current-and-three-prior history by bar four.

## Calculation flow

```mermaid
flowchart TD
    I["Chronological Close input"] --> F{"Finite or missing?"}
    F -->|NaN| M["Return all NaNs; preserve state"]
    F -->|invalid| X["Reject; preserve state"]
    F -->|finite| H["Two-pole high-pass then SuperSmoother"]
    H --> C["Lag Pearson correlations; retain invalid-denominator lags"]
    C --> D["Lag DFT; fourth-power EMA; listing-specific maximum decay"]
    D --> P["Normalize bins and centroid above half power"]
    P --> R["Retain or clamp real dominant cycle"]
    R --> A["Retune band-pass to 0.9 real cycle and compute recurrence"]
    A --> G{"Accepted bar one or two?"}
    G -->|yes| Y["Force band-pass to zero"]
    G -->|no| N["Use computed band-pass"]
    Y --> S["Peak AGC, signal, delayed trigger and unplotted lead"]
    N --> S
    S --> V{"All arithmetic finite?"}
    V -->|no| X
    V -->|yes| K["Commit all candidate histories; increment accepted count"]
    K --> W{"Full required history?"}
    W -->|no| Z["Return all-NaN public tuple"]
    W -->|yes| O["Return named components"]
```

Every arrow is causal. Candidate buffers are temporary until all stages succeed, so rejection cannot advance the roof without advancing the oscillator. Histories have fixed configured capacities, not an unbounded input record; immutable state snapshots remain valid after later updates. With $P_1$ maximum period, $M=A$ or lag, update work is $O(P_1A+P_1(P_1-P_0+1))$ for a fixed average, or $O(P_1^2)$ for lag-dependent averages, plus oscillator window work. Cached sine/cosine tables use $O(P_1(P_1-P_0+1))$ memory; dynamic histories use $O(P_1+A)$ or $O(P_1)$ memory. There is no batch lookahead.

## Confirmed reference combinations

All twelve cases below were confirmed as part of the 48-case family plan. Every component has 252 values; NaNs represent the public history rule.

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.0, bandwidth=0.3` | Published defaults and listing-specific periodogram decay. |
| 2 | `min_period=10, max_period=48, averaging_length=0, highpass_period=48.0, smoothing_period=10.0, bandwidth=0.3` | Lag-dependent Pearson windows and longer priming history. |
| 3 | `min_period=10, max_period=48, averaging_length=2, highpass_period=48.0, smoothing_period=10.0, bandwidth=0.3` | Two-sample Pearson windows with strong sign changes. |
| 4 | `min_period=10, max_period=48, averaging_length=5, highpass_period=48.0, smoothing_period=10.0, bandwidth=0.3` | Less reactive fixed correlation window. |
| 5 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.0, bandwidth=0.1` | Narrow adaptive pass band and longer recursive transients. |
| 6 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.0, bandwidth=0.7` | Broad adaptive pass band and faster response. |
| 7 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.5, bandwidth=0.3` | Fractional roofing/output SuperSmoother cutoff. |
| 8 | `min_period=10, max_period=48, averaging_length=3, highpass_period=80.0, smoothing_period=20.0, bandwidth=0.3` | Slower independent roofing and output smoothing. |
| 9 | `min_period=6, max_period=24, averaging_length=3, highpass_period=24.0, smoothing_period=6.0, bandwidth=0.3` | Compact short-cycle estimator and adaptive windows. |
| 10 | `min_period=20, max_period=20, averaging_length=3, highpass_period=48.0, smoothing_period=10.0, bandwidth=0.3` | Single cycle bin, integer-bound window behavior and deterministic tuning. |
| 11 | `min_period=10, max_period=48, averaging_length=204, highpass_period=48.0, smoothing_period=10.0, bandwidth=0.3` | 252-observation history boundary: first public result at final close. |
| 12 | `min_period=24, max_period=60, averaging_length=3, highpass_period=60.0, smoothing_period=12.0, bandwidth=0.3` | Longer-cycle estimator and adaptive windows. |

## Example and files to convert

Run the master directly for a 252-Close streaming example:

```sh
python3 adaptive-band-pass-indicator.py
python3 adaptive-band-pass-indicator.py --generate-reference-data
python3 verify_reference_data.py
python3 -m unittest discover -s . -p 'test_adaptive_band_pass_indicator.py'
```

Hyphens are retained in the requested master filename; a port can use its normal module name. To load this research file from Python:

```python
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parent / "adaptive-band-pass-indicator.py"
spec = importlib.util.spec_from_file_location("adaptive_master", path)
master = importlib.util.module_from_spec(spec)
spec.loader.exec_module(master)
indicator = master.AdaptiveBandPassIndicator()
for close in [91.5, 94.815, 94.375]:
    result = indicator.update(close)
    print(result)  # These early public fields are NaN; state already evolves.
```

`adaptive-band-pass-indicator.py` contains the numerical master and the fixture generator; `description.md` is the standalone conversion specification. `test_testdata.py`, `testdata_test.go`, `testdata.ts`, `testdata.rs` and `testdata.zig` contain preserved OHLC inputs and **48 expected arrays per language**. `test_adaptive_band_pass_indicator.py` has the independent full-history source oracle and streaming behavior checks; `verify_reference_data.py` checks generated literals and metadata against the master. The Python numerical part uses only arithmetic, lists, tuples and standard `math`, so other languages need no numerical package.

Names follow `EXPECTED_P010_P148_A3_HP48_LP10_VALUE`, with `B0_3` appended before the component for Band-Pass. Fractional smoothing uses `LP10_5`. Integer-valued lookback and cycle components are serialized as f64-compatible decimals; input arrays remain exactly as copied. The `A204` case has 251 all-NaN rows followed by one finite row at the final input.

## Validation record

Validation commands and outcomes are recorded here after expected-data generation. The independent oracle recomputes coefficients and retains full variable histories, while the streaming master uses bounded buffers and cached Fourier coefficients. Their comparison covers every approved combination and internal histories, not just the final indicator value. Constant-zero, reset, immutable snapshots, skipped NaNs, rejected infinities/overflow, integer loop boundaries and single-period behavior are also checked. Compiler/runtime checks verify the foreign fixtures; they do not claim that foreign-language indicator implementations have already been created.

Completed on 2026-10-22:

- **9 Python tests passed** in this folder, including all twelve cases against the independent source-listing oracle. Family total: 36 passing tests.
- `verify_reference_data.py` passed: **48 arrays and 12,096 values per language**, with exact 15-significant-digit agreement, component names, two metadata comments, NaN masks and preserved four-array OHLC input sections across all five languages.
- Regeneration of all five fixtures was **byte-for-byte identical**; family total: twenty fixture files.
- Go 1.27.1, Rust 1.98.1 and Zig 0.16.0 compiled and ran fixture harnesses checking every component's length, NaN prefix and final value. Node 24.15.0 loaded the TypeScript fixtures with type stripping and passed the same checks. No separate TypeScript compiler was used.
- All Python sources and fixtures parsed successfully, and all new files passed the trailing-whitespace check.

The independent oracle uses full-precision constants and the documented zero-prehistory/undefined-division conventions. It checks agreement with a transcription of the listing; TradeStation itself was not executed. The original truncated-constant listing will differ slightly. The oracle compares binary64 values with combined absolute/relative tolerance $5\times10^{-10}$; the fixture verifier checks the exact rounded exported values.

## Sources and BibTeX

The only numerical authority is Ehlers' Chapter 11 **Listing 11-4**. The shared theory uses the same book's Chapter 3 Equation 3-3, Chapter 5 Equations 5-2/5-3 and AGC discussion, Chapter 7 Roofing Filter/spectral-dilation discussion, and Chapter 8 Pearson/periodogram/centroid discussion. Chapter 5's printed Equation 5-1 inconsistency is explained in the Band-Pass master. No external implementation is imported or used as a substitute for these listings.

- John F. Ehlers, *Cycle Analytics for Traders: Advanced Technical Trading Concepts*, Wiley, 2013. [Book and bibliographic record](../../2013-cycle-analytics-for-traders/toc.md), [Chapter 11](../../2013-cycle-analytics-for-traders/ch11.md), [Chapter 3](../../2013-cycle-analytics-for-traders/ch3.md), [Chapter 5](../../2013-cycle-analytics-for-traders/ch5.md), [Chapter 7](../../2013-cycle-analytics-for-traders/ch7.md), [Chapter 8](../../2013-cycle-analytics-for-traders/ch8.md).
- J. Welles Wilder, Jr., *New Concepts in Technical Trading Systems*, 1978. Historical RSI background cited by Ehlers; this is not Wilder's original smoothing implementation.
- Donald Lambert, *Commodities*, October 1980. Historical CCI background cited by Ehlers; this adaptive master follows the RMS-based book variant.

```bibtex
@Book{ehlers2013cycle,
  author = {Ehlers, John F.},
  title = {Cycle Analytics for Traders: Advanced Technical Trading Concepts},
  publisher = {Wiley},
  year = {2013},
  series = {Wiley Trading},
  isbn = {9781118728604}
}
@Book{wilder1978new,
  author = {Wilder, J. Welles, Jr.},
  title = {New Concepts in Technical Trading Systems},
  publisher = {Hunter},
  address = {Winston-Salem, NC},
  year = {1978},
  note = {Historical RSI reference as identified by Ehlers in Chapter 11; original book not independently consulted}
}
@Article{lambert1980cci,
  author = {Lambert, Donald},
  title = {Commodity Channel Index: Tool for Trading Cyclic Trends},
  journal = {Commodities},
  year = {1980},
  month = oct,
  note = {Historical CCI reference identified in Chapter 11; original article not independently consulted; not the numerical authority for this adaptive RMS variant}
}
```

## Original Chapter 11 section and Listing 11-4

The following local book section is included so a conversion agent can inspect the complete published calculation without access to the input repository. The EasyLanguage listing retains its printed constants and comments, including source errors already explained above. **Port the full-precision equations and explicit initialization/undefined-division rules in this document**, rather than treating these printed approximations as the fixture authority. Figure assets are omitted; captions are retained. Claims in the historical source narrative do not replace the mathematical interpretations above.


If a band-pass filter can be designed, it just makes since to tune that filter to the measured dominant cycle to eliminate all the other frequency components that are of no interest. The band-pass filter was described in ­Chapter 5. Here, the adaptive band-pass indicator starts with the computation of the dominant cycle using the autocorrelation periodogram approach. Code Listing 11-4 contains the EasyLanguage code for the adaptive band-pass indicator, and the identification of the indicator itself is noted by the comment near the end following the calculation of the dominant cycle.

One way to make a band-pass filter have a leading phase capability is to tune the filter to a period shorter than the period of the cycle being measured. In this case, the bandwidth of filter is set to $0.3$. That is $30$ percent of the tuned center period. Therefore, the half bandwidth is $15$ percent. We tune the filter to be $10$ percent toward the shorter period from the dominant cycle period to provide the phase lead while still having the data of interest be within the filter bandwidth. This provides a phase lead of the dominant cycle to be something on the order of $60$ degrees, or one-sixth of a cycle. If the dominant cycle were $18$ bars, for example, then the detuning of the filter would produce a $3$-bar lead. This leading function is not huge, but it is significant.

A convenient trigger line is included in the adaptive band-pass filter to signal the more highly likely buy and sell points. The trigger is compute as $90$ percent of the amplitude of the adaptive band-pass filter line and is ­delayed by one bar. While the line crossings occur after the peak of the band-pass filter, phase lead provides for the generation of a timely signal. Significant trading signals should also include the criteria that the line crossing occur at greater than the $+0.7$ and less than the $−0.7$ reference lines.

**Code Listing 11-4. EasyLanguage Code to Compute the Adaptive Band-Pass Filter**

```easylanguage
{
  Adaptive BandPass Indicator
  (c) 2013 John F. Ehlers
}
Inputs:
  Bandwidth(.3);

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
  DominantCycle(0);

Arrays:
  Corr[48](0),
  CosinePart[48](0),
  SinePart[48](0),
  SqSum[48](0),
  R[48, 2](0),
  Pwr[48](0);

//Highpass filter cyclic components whose periods are shorter than 48 bars
alpha1 = (Cosine(.707*360 / 48) + Sine (.707*360 / 48) - 1) / Cosine(.707*360 / 48);

HP = (1 - alpha1 / 2)*(1 - alpha1 / 2)*(Close - 2*Close[1] + Close[2]) + 2*(1 - alpha1)*HP[1] - (1 - alpha1)* (1 - alpha1)*HP[2];

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
MaxPwr = .995*MaxPwr;
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

//Adaptive BandPass indicator tunes a BandPass filter to 90% of the period of the Dominant Cycle
Vars:
  gamma1(0),
  alpha2(0),
  beta1(0),
  BP(0),
  Peak(0),
  Signal(0),
  Lead(0),
  LeadPeak(0),
  LeadSignal(0);

beta1 = Cosine(360 / (.9*DominantCycle));
gamma1 = 1 / Cosine(360*Bandwidth / (.9*DominantCycle));
alpha2 = gamma1 - SquareRoot(gamma1*gamma1 - 1);
BP = .5*(1 - alpha2)*(Filt - Filt[2]) + beta1*(1 +
alpha2)*BP[1] - alpha2*BP[2];

If Currentbar = 1 or CurrentBar = 2 Then BP = 0;

Peak = .991*Peak[1];
If AbsValue(BP) > Peak Then Peak = AbsValue(BP);
If Peak <> 0 Then Signal = BP / Peak;

Lead = 1.3*(Signal + Signal[1] - Signal[2] - Signal[3]) / 4;
LeadPeak = .93*LeadPeak[1];

If AbsValue(Lead) > LeadPeak Then LeadPeak = Absvalue(Lead);
If LeadPeak <> 0 Then LeadSignal = .7*Lead / LeadPeak;

Plot1(Signal);
Plot14(.9*Signal[1]);
Plot2(0);
Plot6(.707);
Plot10(-.707);
```

[The source figure is omitted; its caption is retained below.]

**Figure 11.4** *The Adaptive Band-Pass Filter Shows Buying and Selling Opportunities*

The adaptive band-pass filter has been applied to Dollar General (symbol DG) over roughly the past year in Figure 11.4. This indicator accurately displays cyclic entry points when the two indicator lines cross outside the plus or minus $0.7$ reference lines.

