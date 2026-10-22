# Decycler — Chapter 4 research prototype master

## Numerical authority and conversion scope

This is a self-contained **research prototype master reference**, based on the indicator's own listing in John F. Ehlers' *Cycle Analytics for Traders: Advanced Technical Trading Concepts* (Wiley, 2013). The Python calculation is chronological, standard-library only, and independent of other masters, zpano, NumPy and pandas. Each folder includes its complete numerical source, original source appendix, reference inputs and expected outputs for Python, Go, TypeScript, Rust and Zig. A conversion agent does not need the source book to implement the mathematics described here.

Mathematical constants have full precision: `math.pi`, `math.sqrt(2.0)` and its reciprocal replace printed `3.14159`, `1.414` and `.707` where they mean those constants. Python sine/cosine use radians; $360/P$ degrees becomes $2\pi/P$ radians. Design constants such as .25, .5, 1.5 and .991 retain their printed values. State calculations use unrounded binary64. Only the final exported literals use **15 significant digits**. Results therefore differ slightly from the original listing's truncated mathematical constants; source arithmetic ordering, signs, recurrences and guard conditions remain authoritative.

Each master is deliberately distinct from later similarly named Ehlers indicators. The Decycler is a one-pole low-pass, the Decycler Oscillator subtracts two two-pole high-pass outputs, Band-Pass uses a fixed-period resonator and its own leading trigger, and Hurst measures finite-window ranges. None is a substitute for the already prepared Chapter 11 adaptive family or spectrum filter banks.

## Stream API, state and startup

Call `update(close, time=None)` once per chronological Close. Time is accepted for interface consistency but has no numerical role. `parameters` is an immutable named tuple; `samples_seen` counts accepted observations; `warmup_bars` is the deterministic number of leading unavailable outputs; `is_primed` indicates that the required input history exists; `output` is the last accepted public result. `state` returns immutable diagnostic values, including internal results computed before public priming. `reset()` clears all histories while retaining the configuration and coefficients.

**Zero prehistory is part of this finite-record reference.** Absent Close values and declared source variables are zero. The first finite Close is accepted as standalone CurrentBar=1. Every recurrence and window calculation runs from that bar, even while public values are NaN. Do not seed histories with the first actual price, defer recurrence until priming, use public NaNs in feedback, or restart after a skipped observation. Commercial platforms may supply earlier history; matching this master requires the same initial conditions and accepted bars.

NaN represents a missing input: return an all-NaN result and preserve histories, accepted count and the previous `output`. Infinity, bool, nonnumeric input and arithmetic overflow raise `ValueError` before state mutation. All candidate downstream values are checked before commit, so a rejected update cannot leave one stage ahead of another. A missing or rejected value neither inserts a zero nor ages a finite lookback.

Public startup NaNs mark **input-history availability**, not convergence of an infinite-impulse-response filter. Coefficient periods do not specify a mandatory waiting window. A recursive filter with a period longer than 252 can still produce a valid finite-record output well before 252 bars; it may retain a large initialization transient. Changing a configured period requires a new instance rather than mutating an established stream. Future inputs never revise previously returned results.

## Shared sampled-data filter background

One Close per bar is a sampled signal. The Nyquist frequency is one-half cycle per bar, or a two-bar period. Low-pass filters retain slower changes and attenuate faster oscillations; high-pass filters remove a static term and attenuate slow changes. A band-pass combines those effects around a selected cycle period. Zeros determine exact rejected components, while poles determine recursive memory, damping and phase. A transfer function describes fixed coefficients with zero initial conditions, not a prediction of future prices.

The book's practical motivation is reduced delay without excessive aliasing noise. A first-order filter generally has weaker stop-band attenuation than a two-pole filter. For an analog-style interpretation, the recursive pole stores part of yesterday's displacement, much as a damped physical system retains energy. Cancellation is analogous to removing the rapidly varying part of a measured waveform. The resonator analogy for Band-Pass explains why sharper selectivity prolongs ringing. These are engineering explanations of the algorithm, not physical equations for market behavior.

The book discusses **spectral dilation**: market swing amplitude often grows with cycle period, approximately 6 dB per octave in its model. A single high-pass stage can then equalize rather than eliminate long-period content. This motivates two high-pass poles in the Decycler Oscillator and an additional high-pass before the Band-Pass resonator. The cited empirical approximations do not establish that every price record follows that spectral law.

## Cancellation principle and complete mathematical derivation

Let $x_t$ be Close and $P$ be `cutoff` in bars. Define the source high-pass coefficient and pole:

$$\theta=\frac{2\pi}{P},\qquad
\alpha=\frac{\cos\theta+\sin\theta-1}{\cos\theta},\qquad q=1-\alpha.$$

A complementary **one-pole** high-pass is

$$h_t=(1-\alpha/2)(x_t-x_{t-1})+q h_{t-1},\qquad
H_{HP}(z)=\frac{(1-\alpha/2)(1-z^{-1})}{1-qz^{-1}}.$$

The Chapter 4 construction subtracts high-frequency output from the original input. Its full transfer-function derivation is

$$\begin{aligned}
H_D(z)&=1-\frac{(1-\alpha/2)(1-z^{-1})}{1-(1-\alpha)z^{-1}}\\
&=\frac{1-(1-\alpha)z^{-1}-(1-\alpha/2)(1-z^{-1})}
{1-(1-\alpha)z^{-1}}\\
&=\frac{(\alpha/2)(1+z^{-1})}{1-(1-\alpha)z^{-1}}.
\end{aligned}$$

Thus Listing 4-1 directly computes the equivalent low-pass recurrence:

$$d_t=\frac{\alpha}{2}(x_t+x_{t-1})+(1-\alpha)d_{t-1}.$$

The direct recurrence is the numerical authority. The master does not actually compute $h_t$ and subtract it, which could introduce another rounding path. The independent tests check both the direct listing and the complementary cancellation identity. Do not replace it with an EMA of current Close alone: the two-element feedforward average $(x_t+x_{t-1})/2$ is essential.

The transfer function has a zero at Nyquist ($z=-1$), unity DC gain, and one recursive pole $q$. A stationary constant input therefore tends to itself. For an impulse $x_0=1$ with zero prehistory,

$$d_0=\alpha/2,\qquad
d_t=(\alpha/2)(1+q)q^{t-1}\quad(t\ge1).$$

The pole produces an exponential tail. The half-power cutoff is determined by $\theta=2\pi/P$; it is not a finite SMA window. Fractional cutoff periods affect the coefficient continuously and are not rounded. The textbook equivalent $\alpha=2\tan(\theta/2)/(1+\tan(\theta/2))$ follows algebraically, but ports should preserve the source trigonometric expression and calculation order for reference agreement.

Chapter 4 describes the low lag at attenuated high-frequency components and approximately 6 dB/octave first-order roll-off away from the cutoff, while distinguishing it from a stronger SuperSmoother. Those are frequency-dependent characteristics, not a universal absence of delay. The zero at Nyquist rejects the exact two-bar component, but one-pole selectivity is insufficient to replace dedicated noise filtering for all frequencies. This master is the book's **single-pole Decycler**, not a two-pole subtraction sometimes called a Decycler in later implementations.

## Parameters, outputs and history requirement

| Parameter | Default | Valid range and meaning |
| --- | --- | --- |
| `cutoff` | 60.0 | Finite real $\ge5$; coefficient cutoff period in bars, with a numerically resolvable $0<q<1$. |

The conservative minimum avoids the source's singular/troublesome very-short angle region. There is no arbitrary maximum, but excessively large periods that round the pole to one or alpha to zero are rejected. bool is not a valid period. The source only exposes `Cutoff(60)`; no output scale, extra smoother or high-pass order is added.

`update` returns a **scalar float** in the same units as Close. `state.value` holds the unmasked internal Decycler and `state.previous_close` holds the current accepted Close that will be previous on the next call. `warmup_bars=1`: the first output is NaN and bar two supplies current and preceding real Close. Recurrence nevertheless runs at bar one with $x_{-1}=d_{-1}=0$. At first Close $x_0$, internal $d_0=(\alpha/2)x_0$; a first-price seed would give a different history. Large cutoff periods such as 252 or 500 keep this same one-bar public history rule.

## Calculation flow

```mermaid
flowchart TD
    I["Chronological Close"] --> V{"Input valid?"}
    V -->|NaN| N["Return NaN; preserve state"]
    V -->|invalid| X["Reject; preserve state"]
    V -->|finite| D["alpha over two times current plus preceding Close, plus pole times preceding Decycler"]
    D --> F{"Result finite?"}
    F -->|no| X
    F -->|yes| C["Commit Close and Decycler; increment accepted count"]
    C --> W{"At least two accepted observations?"}
    W -->|no| N2["Return NaN; retain computed feedback"]
    W -->|yes| O["Return scalar Decycler"]
```

Calculation and memory per accepted bar are both $O(1)$. Coefficients are computed once at construction. No raw record, rolling extrema or hidden filter-bank dependency is stored.

## Confirmed reference combinations

All twelve cases were confirmed as part of the 48-case family plan on 2026-10-22. Each exported component has 252 values.

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `cutoff=60.0` | Published 60-bar cutoff. |
| 2 | `cutoff=30.0` | 30-bar cutoff used in the chapter figures. |
| 3 | `cutoff=5.0` | Fast supported cutoff and strong attenuation of Nyquist noise. |
| 4 | `cutoff=6.0` | Short-cycle cutoff near the supported lower range. |
| 5 | `cutoff=10.0` | Short trend filter. |
| 6 | `cutoff=20.0` | Intermediate cutoff. |
| 7 | `cutoff=40.0` | Intermediate-long cutoff. |
| 8 | `cutoff=60.5` | Fractional coefficient period without window rounding. |
| 9 | `cutoff=80.0` | Slower trend filter. |
| 10 | `cutoff=120.0` | Long recursive memory. |
| 11 | `cutoff=252.0` | Cutoff equal to record length; priming remains input-history based. |
| 12 | `cutoff=500.0` | Cutoff longer than the record; finite recursive startup. |

## Files, reference generation and porting

`decycler.py` contains the complete numerical calculation and marked-off fixture tooling. `description.md` is the standalone conversion specification. `test_decycler.py` contains an independent full-history transcription of the listing and streaming/analytic checks. `verify_reference_data.py` parses all five fixture languages and compares metadata, values and NaN masks to the Python master.

The five fixtures retain the original **four 252-element OHLC arrays**, although this indicator consumes only Close. The exact Close input is also embedded inside the master's `__main__`. There are **12 expected arrays per language** in this folder: twelve parameter cases, with two components for Band-Pass and one VALUE component for each other master. Family total is 48 cases and 60 component arrays per language.

Names use shortcuts `C` (cutoff), `HP1`/`HP2` (the independent high-pass periods), `P`/`B` (center period/bandwidth), and `L`/`LP` (range length/smoothing period). Decimal points in parameter values become underscores. Example names are `EXPECTED_C60_VALUE`, `EXPECTED_HP130_HP260_VALUE`, `EXPECTED_P20_B0_3_SIGNAL`, and `EXPECTED_L30_LP20_VALUE`. Foreign names retain parameter separators: Go, TypeScript and Zig start with `expected`, while Rust uses `expected_` and lower-case tokens. Each array has the same two description/parameter comment lines in every language.

The generator writes Python first, reopens the exported literals, verifies the rounded numbers and NaNs, then translates those authoritative decimals to Go, TypeScript, Rust and Zig. NaN forms are Python `NaN = math.nan`, Go `math.NaN()`, TypeScript `NaN`, Rust `f64::NAN`, and Zig `nan` with the supplied standard math declarations. Go packages strip hyphens/underscores from the folder name. Rerunning replaces only marked expected-data sections and leaves copied input sections intact.

Run from this folder:

```sh
python3 decycler.py
python3 decycler.py --generate-reference-data
python3 verify_reference_data.py
python3 -m unittest discover -s . -p 'test_decycler.py'
```

The master filename follows the folder name. To load it directly for streaming use:

```python
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parent / "decycler.py"
spec = importlib.util.spec_from_file_location("book_master", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
indicator = module.Decycler()
for close in [91.5, 94.815, 94.375, 95.095]:
    print(indicator.update(close))
```

A port needs only ordinary binary64 math, fixed histories and loops. Compare NaN placement exactly and finite values with combined absolute/relative tolerance, for example $10^{-10}$ on this shared record; libm results can vary in the last bits across languages. Internal values are unrounded. Preserving newest-first window bounds, arithmetic signs, initialization and branch ordering is more important than reproducing export formatting inside the indicator.

## Validation record

Completed on 2026-10-22:

- **8 Python tests passed** in this folder, including all twelve parameter cases against the independent listing oracle. Family total: 32 passing tests.
- `verify_reference_data.py` passed: **12 arrays and 3,024 values per language**, exact 15-significant-digit values, metadata comments, component names, NaN masks and preserved OHLC inputs across all five languages. Family total: 60 arrays / 15,120 values per language.
- All five generated fixture files regenerate **byte-for-byte identically**. Family total: twenty fixture files.
- Go, Rust and Zig compiled and ran fixture harnesses checking every exported array's length, exact NaN prefix and finite final value when present. Node loaded TypeScript with type stripping and passed the same checks; a separate TypeScript compiler was not used.
- Python sources and fixtures parse successfully, all new files pass the trailing-whitespace check, and source-document links resolve.

Source-oracle comparisons use combined absolute and relative tolerance $10^{-11}$; the fixture verifier checks the exact rounded exported values. Tests also cover invalid input/overflow without partial state commit, reset, immutable configuration, analytic or listing-specific behavior, scale behavior and exact public history boundaries.

The independent oracle recomputes coefficients and keeps full chronological variable histories; the numerical master uses bounded histories and cached coefficients. The oracle uses the same documented full-precision constants and zero-prehistory convention. Agreement with that source transcription does not imply that TradeStation itself was executed, nor that foreign-language indicator implementations have already been created. Compiler/runtime checks validate fixture source forms; the fixture parser checks every exported numeric value and comment.

## Sources and BibTeX

Numerical authority: Ehlers, *Cycle Analytics for Traders*, **Chapter 4, Listing 4-1**. Relevant theory is reproduced above and the original local source is included below. Chapter 3 Equation 3-3 supplies Hurst's final SuperSmoother; Chapter 7's spectral-dilation discussion supports the filter background. No external library implementation is imported or treated as a numerical authority.

- [Book and bibliographic record](../../2013-cycle-analytics-for-traders/toc.md).
- [Chapter 4 source](../../2013-cycle-analytics-for-traders/ch4.md), [Chapter 3 SuperSmoother](../../2013-cycle-analytics-for-traders/ch3.md), [Chapter 7 spectral dilation](../../2013-cycle-analytics-for-traders/ch7.md).

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

## Original source appendix

The supplied Chapter 4 text and complete requested listing are reproduced below for conversion agents who will not have access to the source files. Printed constants, equations and code comments are retained; inaccuracies are identified and resolved by the mathematical/source-authority discussion above. Figure assets are omitted, and malformed caption emphasis is repaired. Both Chapter 4 listings are retained to make the one-pole/two-pole distinction explicit. This folder implements only Listing 4-1.

### Chapter 4: Decyclers

*“The wiggles have been canceled,” said Tom flatly.*

If technical analysis techniques include a detrender, then certainly there is room for its corollary, a decycler. A decycler removes the cycle components and retains only the trend components.

### Decycler Construction

The concept of a decycler is really pretty simple. The cyclic components are removed by the process of cancellation. Figure 4.1 shows the amplitude response of a high-pass filter. Note that the amplitude of the filter output is almost the same as the filter input amplitude (i.e., 0 dB). Thus, if the high-pass filter output is subtracted from the input data, the residual only contains the low-frequency components.

The transfer response of a decycler is written as the difference between input and the output of a high-pass filter as

$$H(z) = 1 - \frac{(1 - \alpha/2)(1 - z^{-1})}{1 - (1 - \alpha) z^{-1}}$$

By putting the right-hand side of this equation over a common denominator, we obtain

$$H(z) = \frac{(\alpha/2)(1 + z^{-1})}{1 - (1 - \alpha) z^{-1}}$$

This transfer response equation shows the decycler to be a one-pole ­filter because the denominator contains only a first-order polynomial. By ­examination, the decycler must closely follow the input data because there is no difference term in the numerator of the transfer response. The Easy-Language code to compute the decycler is written almost directly from the transfer response equation in Code Listing 4-1.

[Source figure omitted; its caption is retained.]

**Figure 4.1** *Frequency Response of a High-Pass Filter Having a 30-Bar Cutoff Period*

**Code Listing 4-1. EasyLanguage Code to Compute a Decycler**

```easylanguage
{
  Decycler
  © 2013 John F. Ehlers
}
Inputs:
  Cutoff(60);
Vars:
  alpha1(0),
  HP(0),
  Decycle(0);

//Highpass filter cyclic components whose periods are shorter than "cutoff" bars
alpha1 = (Cosine(360 / Cutoff) + Sine (360 / Cutoff) - 1) / Cosine(360 / Cutoff);

Decycle = (alpha1 / 2)*(Close + Close[1]) + (1- alpha1)*Decycle[1];

Plot1(Decycle);
```

### Decycler Application

The decycler removes the shorter cycle energy by cancellation, leaving the decycler output to be basically a one-pole low-pass filter. A decycler having a $30$-bar cutoff period is used as an example. The amplitude response is shown in Figure 4.2, and the lag is shown in Figure 4.3. The amplitude response confirms the $6$-dB-per-octave attenuation roll-off rate of a single-pole filter. For example, the response at a frequency of $0.1$ bars per cycle is approximately $−10$ dB, and the response one octave higher at a frequency of $0.2$ bars per cycle is approximately $−16$ dB.

[Source figure omitted; its caption is retained.]

**Figure 4.2** *Amplitude Response of a Decycler Having a 30-Bar Cutoff Period*

[Source figure omitted; its caption is retained.]

**Figure 4.3** *Lag of a Decycler Having a 30-Bar Cutoff Period*

The really important characteristic of the decycler is its exceptionally
low lag. The very longest cycle components are delayed less than five bars,
and at a frequency of 0.05 cycles per bar (a 20-bar cycle period), the lag is
on the order of 1.5 bars. Higher-frequency components are delayed even
less. The end result is the higher-frequency wiggles that make it through
the filter attenuation are roughly coincident with the wiggles in the price
itself. This feature makes the decycler an ideal “instantaneous trend line” that
­accurately portrays the trend of the data.

A similar smoothed filter output can be produced using a SuperSmoother
filter. However, when the results of the decycler are compared to those
of the SuperSmoother, the decycler will always have less lag. However, a
decycler is only a one-pole filter and therefore has inferior filtering capa-
bilities. Therefore, a decycler should not be used as a smoothing filter to
remove aliasing noise. Rather, its role should be relegated to producing an
instantaneous trend line where the selected cutoff period is relatively large.
The large cutoff period enables the decycler to attenuate the aliasing noise
because it is many octaves away from the Nyquist frequency.

It is certainly possible to create a decycler by subtracting a two-pole high-
pass filter output from the input data. In fact, such a decycler has some
­interesting properties because the long cycle components have substan-
tial lag, while the short cycle components continue to have minimal lag.
­However, interpretation of the indicator is more difficult because the larger
spread in lag across the spectrum. Therefore, only the single-pole decycler
is recommended for use as instantaneous trend lines.

### Decycler Oscillator

A decycler oscillator is created by subtracting the output of a high-pass filter having a shorter cutoff period from the output of another high-pass filter having a longer cutoff period. This way, both elements have a zero in their transfer responses at zero frequency. Thus, the very, very long cycle components (and the static term) are removed. There is a finite difference between the output of the two filters in the frequency range between their cutoff periods, but shorter cycle components are still removed by cancellation. As a result, the trend line is displayed as an oscillator. The EasyLanguage code to compute the decycler oscillator is shown in Code Listing 4-2.

**Code Listing 4-2. EasyLanguage Code for Decycler Oscillator**

```easylanguage
{
  Decycler Oscillator
  © 2013 John F. Ehlers
}
Inputs:
  HPPeriod1(30),
  HPPeriod2(60);
Vars:
  alpha1(0),
  alpha2(0),
  HP1(0),
  HP2(0),
  Decycle(0);

alpha1 = (Cosine(.707*360 / HPPeriod1) + Sine (.707*360 / HPPeriod1) - 1) / Cosine(.707*360 / HPPeriod1);

alpha2 = (Cosine(.707*360 / HPPeriod2) + Sine (.707*360 / HPPeriod2) - 1) / Cosine(.707*360 / HPPeriod2);

HP1 = (1 - alpha1 / 2)*(1 - alpha1 / 2)*(Close - 2*Close[1] + Close[2]) + 2*(1 - alpha1)*HP1[1] - (1 - alpha1)* (1 - alpha1)*HP1[2];

HP2 = (1 - alpha2 / 2)*(1 - alpha2 / 2)*(Close - 2*Close[1] + Close[2]) + 2*(1 - alpha2)*HP2[1] - (1 - alpha2)*(1 - alpha2)*HP2[2];

Decycle = HP2 - HP1;

Plot1(Decycle);
Plot2(0);
```

The decycler oscillator can be useful for determining the transition between uptrends and downtrends by the crossing of the zero line. Alternatively, the changes of slope of the decycler oscillator are easier to identify than the changes in slope of the original decycler. Optimum cutoff periods can easily be found by experimentation. The decycler and decycler oscillator examples are shown in Figure 4.4, where the cutoff period is $30$ bars. In the case of the decycler oscillator, the longer cutoff period is set to be $60$ bars.

[Source figure omitted; its caption is retained.]

**Figure 4.4** *Both Decyclers Show the Instantaneous Trend with Minimum Lag*

### Key Points to Remember

1. A decycler filter functions the same as a low-pass filter.
2. A decycler filter is created by subtracting the output of a high-pass filter from the input, thereby removing the high-frequency components by cancellation.
3. A decycler filter has very low lag.
4. A decycler oscillator is created by subtracting the output of a high-pass filter having a shorter cutoff period from the output of another high-pass filter having a longer cutoff period.
5. A decycler oscillator shows transitions between uptrends and downtrends at the zero crossings.
