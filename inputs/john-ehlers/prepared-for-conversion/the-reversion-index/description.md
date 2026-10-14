# The Reversion Index — research prototype master reference

This directory is the complete reference package for converting John F. Ehlers'
Reversion Index to other languages. The numerical master is
**the-reversion-index.py**, a streaming implementation using only Python's
standard library. The five data files contain the same input prices and the same
reference output values. A port does not need access to the original articles
to implement the algorithm.

The authority is the **January 2026 TASC article's EasyLanguage code**, including
its approximate constants, summation expression order, and retained Ratio
variable. The standalone startup convention and configurable filter periods
were explicitly confirmed by the user. Neither the separate Python Trader's
Tips implementation nor TradingView's implementation is the numerical master.

## 1. Purpose and physical interpretation

The indicator describes short-term directional price movement in a ranging
market. It measures signed displacement divided by the total distance travelled,
then smooths that normalized measurement twice. The faster and slower smoothed
lines have different delays; their crossings help locate turning regions.

Imagine an object moving along a line. Its final displacement can be small even
though it travelled a considerable distance back and forth. Conversely, if it
moves in only one direction, displacement magnitude equals total distance.
The Reversion Index applies this distinction to successive price changes:

- A window containing only upward movement has raw ratio $+1$.
- A window containing only downward movement has raw ratio $-1$.
- Balanced upward and downward movement produces a ratio near zero.
- A completely stationary window needs a separate division-by-zero rule.

This is a normalized movement measure, not a direct estimate of the absolute
price level or a numerical forecast of the next price. Normalization makes the
raw measurement dimensionless. In exact arithmetic, adding a constant to all
prices or multiplying prices by a positive scale leaves the ratio unchanged.
Negative scaling reverses its sign.

Ehlers developed this indicator after the Continuation Index, introduced in
September 2025. The Continuation Index uses a Laguerre filter to describe trend
onset, continuation, and exhaustion. The Reversion Index instead targets
mean-reversion trading in cyclic or ranging data.

### Differentiation and integration

Let $p_t$ be the close at integer bar index $t$, with one uniformly spaced sample
per bar. A first difference is the discrete analogue of differentiation:

$$
\Delta_t=p_t-p_{t-1}.
$$

Summing differences is the discrete analogue of integration. The operations
cancel in the numerator, leaving displacement across the window:

$$
\sum_{i=0}^{L-1}\Delta_{t-i}
=\sum_{i=0}^{L-1}(p_{t-i}-p_{t-i-1})
=p_t-p_{t-L}.
$$

This is the mathematical telescoping identity. The master deliberately
**does not** replace the article's summation with this identity: floating-point
rounding differs between the two calculations.

For a continuous sinusoid, the derivative relationship reproduced in *Cycle
Analytics for Traders*, chapter 1, equation (1-9), is:

$$
\frac{d\sin(2\pi f t)}{dt}=2\pi f\cos(2\pi f t).
$$

Differentiation advances sinusoidal phase by $90^\circ$. Integration restores
the original phase, subject to the finite-window delay described next.

### Why use approximately half a cycle?

Ehlers describes the window as extending from the cycle valley to the cycle
peak. During that upswing, the sum is largest. The result is reported at the
right edge of the data window, which is behind its centre by approximately
$90^\circ$ when the window spans half the dominant cycle.

The exact numerator for a sampled sine wave illustrates the combined effect.
For $p_t=\mu+A\sin(\omega t)$:

$$
N_t=p_t-p_{t-L}
=2A\sin\left(\frac{\omega L}{2}\right)
 \cos\left(\omega t-\frac{\omega L}{2}\right).
$$

If $L=C/2$, where the cycle period $C=2\pi/\omega$, then:

$$
\frac{\omega L}{2}=\frac{\pi}{2},
\qquad N_t=2A\sin(\omega t).
$$

Thus the numerator's extrema align with the input sine's extrema in this ideal
case. The absolute-difference normalization and subsequent smoothing make the
actual indicator nonlinear and delayed, so this identity does not imply exact
turning-point prediction for market prices.

A monthly cycle of about 20 trading bars suggests $L=10$. Increasing the
window far beyond the relevant half-cycle averages across several swings and
makes the ratio describe longer-term direction. That is the trend-like use
Ehlers explicitly distinguishes from the intended mean-reversion use.

## 2. Complete indicator equations and numerical contract

### Normalized short-term movement

For window length $L$, at a bar with $L+1$ available closes:

$$
N_t=\sum_{i=0}^{L-1}(p_{t-i}-p_{t-i-1}),
\qquad
D_t=\sum_{i=0}^{L-1}|p_{t-i}-p_{t-i-1}|.
$$

The article defines a retained series variable, initially zero:

$$
R_{\mathrm{initial}}=0,\qquad
R_t=
\begin{cases}
N_t/D_t,&D_t\ne0,\\
R_{t-1},&D_t=0.
\end{cases}
$$

At the first valid calculation, the second branch retains the initial zero if
no movement has occurred. After an earlier directional move, a later flat
window retains the most recently computed ratio, even when it equals $+1$ or
$-1$. Resetting to zero in that situation changes the original code.

The triangle inequality gives $|N_t|\le D_t$, hence $R_t\in[-1,1]$ in exact
arithmetic whenever $D_t>0$. The master does not clamp floating-point roundoff
at these bounds, and the smoothed lines can overshoot the raw ratio's range.

### Literal operation order

The following is a direct transcription of the article's calculation:

~~~easylanguage
DeltaSum = 0;
AbsDeltaSum = 0;
For count = 0 to Length - 1 Begin
    DeltaSum = DeltaSum + Close[count] - Close[count + 1];
    AbsDeltaSum = AbsDeltaSum + AbsValue(Close[count] - Close[count + 1]);
End;
If AbsDeltaSum <> 0 Then Ratio = DeltaSum / AbsDeltaSum;
~~~

The porting contract is newest-to-oldest traversal with:

~~~text
delta_sum = (delta_sum + current_close) - previous_close
abs_delta_sum = abs_delta_sum + abs(current_close - previous_close)
~~~

The subtraction occurs after adding the price to the numerator accumulator.
Adding a precomputed difference instead, reversing traversal, using a rolling
sum, compensated summation, or directly subtracting the two endpoint closes
can produce different reference decimals.

### Two independent SuperSmoothers

For each period $P$, reproduce the article's coefficients:

$$
Q_P=\exp\left(-\frac{1.414\cdot3.14159}{P}\right),
\qquad
\theta_P^{\circ}=\frac{1.414\cdot180}{P},
$$

$$
c_{1,P}=2Q_P\cos_{\mathrm{degrees}}(\theta_P^{\circ}),
\qquad c_{2,P}=Q_P^2,
\qquad a_{0,P}=\frac{1-c_{1,P}+c_{2,P}}{2}.
$$

Python evaluates the angle as:

~~~python
angle = math.radians(1.414 * 180.0 / period)
c1 = 2.0 * q * math.cos(angle)
~~~

Degree conversion uses the standard library's full-precision $\pi$. The
exponential uses the literal **3.14159**. Do not substitute full-precision
$\pi$ into the exponential, replace 1.414 by $\sqrt{2}$, or assume the same
approximation is used in both coefficient expressions.

Let $k=1,2,\ldots$ count complete-window ratio calculations, and let $t$ refer
to their original input bar indices. The filter is:

$$
S^{(P)}_t=
\begin{cases}
R_t,&k<4,\\
a_{0,P}(R_t+R_{t-1})
 +c_{1,P}S^{(P)}_{t-1}
 -c_{2,P}S^{(P)}_{t-2},&k\ge4.
\end{cases}
$$

This is the article's function:

~~~easylanguage
Q = expvalue(-1.414*3.14159 / Period);
c1 = 2*Q*Cosine(1.414*180 / Period);
c2 = Q*Q;
a0 = (1 - c1 + c2) / 2;

If CurrentBar >= 4 Then $SuperSmoother =
    a0*(Price + Price[1]) + c1*$SuperSmoother[1] - c2*$SuperSmoother[2];
If CurrentBar < 4 Then $SuperSmoother = Price;
~~~

The reported outputs are:

$$
\mathrm{ratio}_t=R_t,\qquad
\mathrm{smooth}_t=S^{(P_s)}_t,\qquad
\mathrm{trigger}_t=S^{(P_f)}_t.
$$

Defaults are $P_s=8$ and $P_f=4$. Both filters consume the raw ratio directly;
the fast filter does not consume the slow filter. They need separate histories
even when periods happen to be equal.

The article's zero reference line is a plotting aid, not an additional output.

## 3. Theoretical background from the books

The following equations preserve the relevant mathematical context from the
available chapters. Equations derived for explanation are identified as such.
The executable authority remains the January 2026 code above.

### Transfer functions, delays, FIR, and IIR

*Cycle Analytics for Traders*, chapter 1, expresses a four-sample moving
average's transfer function as equation (1-1):

$$
H(z)=\frac14+\frac14z^{-1}+\frac14z^{-2}+\frac14z^{-3}.
$$

Here $z^{-1}$ represents one sample of delay. The generalized finite impulse
response (FIR), or nonrecursive, filter is equation (1-2):

$$
H(z)=b_0+b_1z^{-1}+b_2z^{-2}+\cdots+b_Nz^{-N}.
$$

The generalized transfer function in equation (1-3) is:

$$
H(z)=
\frac{b_0+b_1z^{-1}+\cdots+b_Nz^{-N}}
     {a_0+a_1z^{-1}+\cdots+a_Nz^{-N}}.
$$

Cross multiplication yields the implementation equation (1-4), written with
explicit sample indices:

$$
y_t=\frac{\sum_{i=0}^N b_i x_{t-i}
             -\sum_{i=1}^N a_i y_{t-i}}{a_0}.
$$

The numerator uses input samples. The denominator introduces feedback from
earlier output samples: an infinite impulse response (IIR), or recursive,
filter. This feedback can give a sharper transition between passed and rejected
frequencies without a long input moving-average window.

An FIR filter with $N+1$ symmetric coefficients has constant delay $N/2$
samples. Equivalently, a symmetric $M$-sample FIR has delay $(M-1)/2$.
An IIR filter generally has frequency-dependent delay; this is dispersion.
Ehlers explains that much of the dispersion occurs in the attenuated frequency
region, reducing its practical influence on the passed signal.

The two operations preceding normalization have the derived linear response:

$$
H_{\Delta}(z)=1-z^{-1},\qquad
H_{\mathrm{sum}}(z)=\sum_{i=0}^{L-1}z^{-i}
 =\frac{1-z^{-L}}{1-z^{-1}},
$$

$$
H_N(z)=H_{\Delta}(z)H_{\mathrm{sum}}(z)=1-z^{-L}.
$$

The normalized ratio itself does **not** have this linear transfer function:
its denominator depends on the input through absolute values.

### Butterworth origin and the 2004 Super Smoother

A Butterworth analog filter is maximally flat near zero frequency. For an
ideal $n$-pole Butterworth low-pass, the familiar explanatory magnitude model is:

$$
|H(j\Omega)|^2=\frac{1}{1+(\Omega/\Omega_c)^{2n}}.
$$

At cutoff $\Omega_c$, output power is half input power, approximately $-3$ dB.
Traders usually describe the reciprocal cutoff frequency as a cutoff period.
The discrete Ehlers formulas are approximations to the analog design.

*Cybernetic Analysis for Stocks and Futures*, chapter 13, equation (13.10),
gives the two-pole digital Butterworth coefficients and recurrence:

$$
a=e^{-1.414\cdot3.14159/P},\qquad
b=2a\cos_{\mathrm{degrees}}(1.414\cdot180/P),
$$

$$
B_t=\frac{1-b+a^2}{4}(p_t+2p_{t-1}+p_{t-2})
       +bB_{t-1}-a^2B_{t-2}.
$$

Its three-pole counterpart, equation (13.11), is:

$$
a=e^{-3.14159/P},\qquad
b=2a\cos_{\mathrm{degrees}}(1.738\cdot180/P),\qquad c=a^2,
$$

$$
B_t=\frac{(1-b+c)(1-c)}8
 (p_t+3p_{t-1}+3p_{t-2}+p_{t-3})
 +(b+c)B_{t-1}-(c+bc)B_{t-2}+c^2B_{t-3}.
$$

Equation (13.12) writes the second-order response generically:

$$
H(z)=\frac{A_0+A_1z^{-1}+A_2z^{-2}}
           {1+B_1z^{-1}+B_2z^{-2}}.
$$

Removing the FIR numerator reduces lag while retaining the IIR poles. For the
code's recurrence sign convention, the older two-pole Super Smoother
(figure 13.8) is:

$$
C_0=1-b+a^2,\qquad
F_t=C_0p_t+bF_{t-1}-a^2F_{t-2}.
$$

It passes the input through while its original $CurrentBar<3$.
This **older filter does not average two successive input samples**.
It is historical background, not the filter implemented by this master.

The local chapter text has an inconsistent generic denominator/sign
description and normalization statement. For a denominator literally written
$1+B_1z^{-1}+B_2z^{-2}$, unity gain requires numerator
$1+B_1+B_2$. For the executable denominator $1-bz^{-1}+a^2z^{-2}$,
the required numerator is $1-b+a^2$, as figure 13.8 computes.
These are sign conventions, not interchangeable coefficient assignments.

### The 2013 modification and SuperSmoother

*Cycle Analytics for Traders*, chapter 3, explains that the original
Butterworth FIR coefficients are proportional to $[1,2,1]$ for two poles and
$[1,3,3,1]$ for three poles. Deleting that numerator reduces lag. Adding back a
two-sample average rejects the Nyquist component at a cost of half a bar.

For completeness, the local chapter's equations (3-1) and (3-2) are reproduced
below **as transcribed**, including their sign/angle inconsistencies:

$$
\begin{aligned}
a&=e^{-1.414\cdot3.14159/P},\\
b&=2a\cos_{\mathrm{degrees}}(1.414\cdot1.25\cdot180/P),\\
c_2&=b,\quad c_3=-a^2,\quad c_1=1-c_2-c_3,\\
Y_t&=c_1X_t-c_2Y_{t-1}-c_3Y_{t-2}.
\end{aligned}
\tag{3-1, local transcription}
$$

$$
\begin{aligned}
a&=e^{-3.14159/P},\\
b&=2a\cos_{\mathrm{degrees}}(1.738\cdot180/P),\quad c=a^2,\\
d_2&=b+c,\quad d_3=-(c+bc),\quad d_4=c^2,\\
d_1&=1-d_2-d_3-d_4,\\
Y_t&=d_1X_t-d_2Y_{t-1}-d_3Y_{t-2}-d_4Y_{t-3}.
\end{aligned}
\tag{3-2, local transcription}
$$

The extra 1.25 in (3-1) and the feedback signs above conflict with the
SuperSmoother equation (3-3) and the supplied executable code. Their origin
(source typo versus transcription issue) cannot be established from these
Markdown copies. Do not use them to alter the master.

The consistent chapter equation (3-3) is:

$$
\begin{aligned}
a&=e^{-1.414\cdot3.14159/P},\\
b&=2a\cos_{\mathrm{degrees}}(1.414\cdot180/P),\\
c_2&=b,\quad c_3=-a^2,\quad c_1=1-c_2-c_3,\\
Y_t&=c_1(X_t+X_{t-1})/2+c_2Y_{t-1}+c_3Y_{t-2}.
\end{aligned}
\tag{3-3}
$$

This matches the January 2026 filter algebraically. The article's
$a_0,c_1,c_2$ notation corresponds to $(c_1/2,c_2,-c_3)$ in the book.
Preserving the article's arithmetic grouping avoids another rounding change.

The derived transfer function for the master's filter is:

$$
H_P(z)=\frac{a_{0,P}(1+z^{-1})}
                 {1-c_{1,P}z^{-1}+c_{2,P}z^{-2}}.
$$

Its two poles are $Q_Pe^{\pm j\theta_P}$, where $\theta_P$ is the degree
expression converted to radians. For finite positive $P$, the ideal arithmetic
pole radius is $0<Q_P<1$, so the recursive response decays.
Very extreme periods can underflow or lose coefficient precision in binary64;
the reference grid uses ordinary, well-resolved periods. If $Q_P$ underflows to
zero, the master sets $c_{1,P}=0$ without evaluating a possibly overflowing
angle, giving the finite limiting coefficients $a_{0,P}=1/2$, $c_{2,P}=0$.

At $z=1$:

$$
H_P(1)=\frac{2a_{0,P}}{1-c_{1,P}+c_{2,P}}=1.
$$

At the Nyquist frequency, $z=-1$, the numerator is zero. The term
$(1+z^{-1})/2$ is the two-sample average that removes a perfect alternating
component. With one sample per bar, Nyquist is $0.5$ cycles per bar, a
two-bar cycle.

The book describes aliasing noise as falling about 6 dB per octave as the
sampled cycle period grows. The two-pole SuperSmoother's rejection slope is
about 12 dB per octave beyond its cutoff, which can suppress that noise below
the systemic trading-noise level. These are filter-design explanations, not
additional processing stages in the indicator.

For context, chapter 3 compares a five-sample SMA (roughly a ten-bar cutoff and
two bars of delay) with a ten-bar SuperSmoother having approximately 1.5 bars of
maximum delay in the illustrated response. Larger critical periods generally
increase delay. This difference in delay motivates the two-line crossover
method, although delay is frequency dependent rather than exactly proportional
to period for every input frequency.

## 4. Parameters, API, and initialization

| Parameter | Type and supported range | Default | Meaning |
|---|---|---:|---|
| length | Built-in integer, at least 1; bool excluded | 20 | Number of price differences in both sums |
| smooth_period | Finite positive built-in int/float; bool excluded | 8 | Critical period of the smooth line |
| trigger_period | Finite positive built-in int/float; bool excluded | 4 | Critical period of the trigger line |

There is no arbitrary upper window bound. A larger window requires more memory
and more warm-up prices. A period below two bars is mathematically accepted but
does not describe a resolvable sampled cycle; typical pairs use periods of four
bars or longer and a slow period above the fast one. Equal or reversed periods
are allowed and covered by the fixtures.

TASC's executable default is **Length(20)**. Both its prose and the MESA
example recommend **Length(10)** for a 20-bar monthly cycle. These are distinct
settings; the master does not silently substitute the prose example for the
published executable default.

~~~python
indicator = ReversionIndex(length=20, smooth_period=8, trigger_period=4)
result = indicator.update(close)
# result.ratio, result.smooth, result.trigger
~~~

The return type is a named tuple, **ReversionIndexResult**, with three float
fields in that order. Construction parameters and **warmup_bars** are readable
properties. To reset, construct a new instance.

The file has a hyphenated name to match the indicator folder. A complete import
example, run from this directory, is:

~~~python
import importlib.util

spec = importlib.util.spec_from_file_location("reversion_index", "the-reversion-index.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

indicator = module.ReversionIndex(length=10, smooth_period=8, trigger_period=4)
for close in [100.0, 101.0, 100.5, 102.0, 101.5, 102.5,
              103.0, 102.0, 103.5, 104.0, 103.0, 104.5, 105.0, 103.5]:
    output = indicator.update(close)
    print(output.ratio, output.smooth, output.trigger)
~~~

Each close must be a finite built-in int/float. Invalid types raise TypeError;
invalid ranges, NaN, infinity, or unrepresentable numbers raise ValueError.
Rejected updates consume no bar and change no history. No missing-value
interpolation, price caching across instances, or implicit gap handling occurs.
Ordinary prices and parameters are expected; intermediate binary64 arithmetic
can overflow for extreme finite prices just as in the source.

### Confirmed standalone startup

Platforms can load invisible price history before their CurrentBar starts.
The supplied article does not define a standalone no-prehistory convention.
The user confirmed the following explicit mapping for this master:

| Input index, zero-based | Available closes | Behavior |
|---|---:|---|
| 0 through length−1 | Fewer than length+1 | All three outputs NaN; filters untouched |
| length | length+1 | First full ratio; both lines equal that ratio |
| length+1 | At least length+1 | Second valid ratio passes through |
| length+2 | At least length+1 | Third valid ratio passes through |
| length+3 onward | At least length+1 | Recursive filtering |

CurrentBar is counted from **1 over valid full-window calculations**. No
partial-window ratios are computed to seed the filters. NaN represents unavailable
public output and is never stored in their internal histories.

For a 252-close input, length 251 produces exactly one valid result at index
251. Length 252 produces only NaNs. The first valid values count as primed;
“primed” does not mean that an IIR transient has completely settled.

### Streaming flow

~~~mermaid
flowchart TD
    A["update(close)"] --> B{"Finite built-in int/float?"}
    B -- No --> C["Raise; preserve all state"]
    B -- Yes --> D["Insert close into bounded ring"]
    D --> E{"length + 1 closes available?"}
    E -- No --> F["Return NaN, NaN, NaN"]
    E -- Yes --> G["Set both sums to zero"]
    G --> H["Visit length adjacent pairs, newest first"]
    H --> I["Preserve (sum + current) - previous; sum absolute differences"]
    I --> J{"Absolute sum nonzero?"}
    J -- Yes --> K["Assign ratio = signed sum / absolute sum"]
    J -- No --> L["Keep previous ratio; initially zero"]
    K --> M["Feed raw ratio to two independent filters"]
    L --> M
    M --> N["Return ratio, smooth, trigger"]
~~~

~~~mermaid
flowchart TD
    A["Valid ratio arrives at one filter"] --> B["Increment valid calculation count"]
    B --> C{"Count less than 4?"}
    C -- Yes --> D["Output = current ratio"]
    C -- No --> E["Output = a0 times current + prior input, plus c1 times prior output, minus c2 times second prior output"]
    D --> F["Shift histories after computing output"]
    E --> F
    F --> G["Return this line"]
~~~

One fixed-size ring stores length+1 closes; each filter stores one prior input
and two prior outputs. Full-window runtime is $O(L)$ and retained memory is
$O(L)$. Reference generation may collect all results, but the indicator itself
never stores the entire input stream.

Ring indexing adds capacity before subtraction so all operands stay
nonnegative. This avoids Python's negative-modulo convention, which differs
from Go/Rust remainder rules, and avoids unsigned underflow in Zig. Preserve
that adjustment when porting the indexing expressions.

## 5. Crossovers, MESA display offset, and source differences

A typical valley signal is the faster trigger crossing above the slower smooth
line in the lower part of the oscillator range. A peak signal is the trigger
crossing below smooth in the upper part. The article suggests looking beyond
thresholds such as $\pm0.3$.

An illustrative discrete crossing convention is:

$$
\mathrm{crossUp}_t=(T_{t-1}\le S_{t-1})\land(T_t>S_t),
$$

$$
\mathrm{crossDown}_t=(T_{t-1}\ge S_{t-1})\land(T_t<S_t).
$$

For example, qualify crossUp when both current lines are below $-0.3$, or
crossDown when both are above $+0.3$. This particular threshold qualification is
an example, not a source-defined trading-system contract. The master returns
the lines and does not generate orders or threshold flags.

MESA enhances plot visibility using:

$$
\mathrm{Trigger1}_t=
\begin{cases}
T_t+0.1,&T_t\ge S_t,\\
T_t-0.1,&T_t<S_t.
\end{cases}
$$

Trigger1 is a **display offset**, not the unmodified Trigger. It is explained
here but excluded from the master return value and expected arrays.

| Supplied source | Differences from this master |
|---|---|
| TASC article | Fixed filter periods 8 and 4; platform-managed prehistory. Master preserves equations with the confirmed standalone initialization |
| MESA paper | Default length 10; plots shifted Trigger1 rather than raw Trigger |
| TradeStation Trader's Tips | Algebraically equivalent filter coefficient naming/grouping; length 20; header contains inconsistent April/2005 labels despite January 2026 context |
| Rajeev Jain Python Trader's Tips | Full-precision pi in exponential; partial windows; initial synthetic zero difference; zero-denominator reset; four input values pass through before recursion |
| PineCoders TradingView | sqrt(2) and full-precision pi; zero-seeded recursive histories; its own full-window and missing-input behavior |
| NinjaTrader files | Loop visits length−1 differences; delayed start; zero reset; full-precision pi; global bar-based filter startup |
| Wealth-Lab notes | Period default 10; one smoothing-period parameter per indicator instance, paired by the strategy designer |
| NeuroShell notes | Formula describes normalized momentum sums and separate period-4/period-8 filtering, without an explicit standalone initialization contract |

These variants explain why the package cannot match every supplied platform
implementation simultaneously. Numerical comparisons here mean parity with the
article's algorithm under the explicitly documented input-history convention;
no commercial-platform runtime was executed to certify hidden prehistory.

## 6. Reference fixtures and reproduction

All five templates were copied from the parent prepared-for-conversion
directory. Their **252 INPUT_CLOSE/testInput/test_input values match exactly**.
The existing high, low, and open arrays are preserved although this indicator
uses only close. The C template is outside the requested five-language package.

The user confirmed this selected grid, not its Cartesian product:

| Length | Smooth period | Trigger period | What it tests |
|---:|---:|---:|---|
| 20 | 8 | 4 | TASC code defaults |
| 10 | 8 | 4 | Article's monthly-cycle example and MESA default |
| 1 | 8 | 4 | Smallest difference window |
| 2 | 8 | 4 | Two-difference window |
| 5 | 8 | 4 | Short window |
| 14 | 8 | 4 | Intermediate window |
| 40 | 8 | 4 | Long window and trend-like behavior |
| 251 | 8 | 4 | First valid output on the final input |
| 252 | 8 | 4 | Insufficient history; all outputs remain NaN |
| 10 | 4 | 2 | Fast smoothing pair |
| 10 | 12 | 6 | Moderate smoothing pair |
| 10 | 16 | 8 | Slow smoothing pair |
| 20 | 16 | 8 | Longer window with slower smoothing |
| 10 | 8 | 8 | Equal periods produce identical lines |
| 10 | 4 | 8 | Reversed periods swap the two lines |
| 10 | 8.5 | 4.5 | Fractional periods and array naming |

There are **16 combinations, 3 outputs each, 48 arrays per language**.
Each array has 252 values. Each is preceded by the exact What it tests text and
a second comment listing length, smooth_period, and trigger_period.

Parameter shortcuts are L, S, and T. Output suffixes are RATIO, SMOOTH, and
TRIGGER. Decimal points in parameter values become underscores; integral values
omit .0. For instance:

| Language / file | Identifier and declaration | NaN representation |
|---|---|---|
| Python / test_testdata.py | EXPECTED_L10_S8_5_T4_5_SMOOTH = [...] | NaN, defined as math.nan |
| Go / testdata_test.go | var expectedL10_S8_5_T4_5_SMOOTH = []float64{...} | math.NaN() |
| TypeScript / testdata.ts | export const expectedL10_S8_5_T4_5_SMOOTH: number[] = [...] | NaN |
| Rust / testdata.rs | pub fn expected_l10_s8_5_t4_5_smooth() -> Vec<f64> | f64::NAN |
| Zig / testdata.zig | pub fn expectedL10_S8_5_T4_5_SMOOTH() [252]f64 | nan |

Go package name is **thereversionindex**. Rust functions live inside the copied
cfg(test) module. Zig defines std.math and nan at the top, and functions return
fixed-size array literals. The spellings math.NaN(), f64::NAN, and TypeScript's
typed exported constants use valid language syntax.

Finite output literals use **15 digits after the decimal point**, following the
existing conversion example. This is fixed decimal precision, not 15
significant digits. The generator uses unrounded binary64 state to calculate
the complete series, then rounds only the emitted literals.

~~~sh
python3 the-reversion-index.py
python3 the-reversion-index.py --generate
python3 the-reversion-index.py --verify
~~~

The executable embeds all 252 closes inside its main block and checks them
against the copied Python input array. Generation first saves Python output,
then reads its literal tokens and comments to generate the other languages.
It never recomputes outputs independently for each language.

On first generation, outputs are appended. On later generations, only the
marked generated sections are replaced. Input arrays and their existing text
survive. Repeated generation is byte-identical.

## 7. Verification and porting acceptance

The standard-library tests in **test_the_reversion_index.py** independently
translate the article in batch form, including the confirmed CurrentBar mapping.
They compare that implementation with the bounded streaming ring for the
entire grid and synthetic edge cases.

Acceptance covers:

- Exactly length leading NaNs, three valid pass-through ratios, and recursion
  beginning at input index length+3.
- Constant prices, one-way motion, alternating motion, sampled sinusoidal
  motion, and retained ratio after a moving window becomes flat.
- Exact loop-expression order on prices that expose floating-point
  cancellation; positive/negative movement; no clamping.
- Equal-period identity and reversal of the named filter periods.
- Fractional periods, invalid parameters, rejected updates preserving state,
  read-only parameters, bounded memory, and independent instances.
- The 251-window final result and completely unprimed 252-window series.
- All 48 saved arrays, fixed 15-decimal tokens, matching comments, preserved
  input arrays, same NaN positions, and identical parsed values in every
  language.

Compare NaNs by classification, never by equality. Finite cross-implementation
comparisons allow absolute and relative tolerance $10^{-12}$:

$$
|a-b|\le\max(10^{-12},10^{-12}\max(|a|,|b|)).
$$

Shared serialized arrays should parse to exactly the same binary64 values.
The tolerance accommodates platform libm and evaluation differences in ports;
it does not permit changing startup, denominator handling, or source constants.

Language validation compiles/loads the five data files and explicitly uses all
generated functions so lazy compilation cannot hide invalid array literals.
TypeScript can be loaded through Node's TypeScript stripping support.
Rust validation enables cfg(test). Zig 0.16 or another compatible toolchain
checks every fixed-size return value.

For a new port, reproduce the retained-ratio rule, exact ring indexing,
newest-to-oldest arithmetic, degree conversion, separate filter histories, and
NaN warm-up mask before attempting optimized storage or arithmetic.
Do not reduce the final dataset to only one smoothed line.

Verified on October 14, 2026: all 13 Python acceptance tests passed. Go,
TypeScript through Node, Rust with cfg(test), and Zig 0.16 each loaded all
52 input/reference series (four inputs plus 48 expected arrays) and matched the
Python decimal source exactly, including NaN positions. Repeated reference
generation produced byte-identical files in all five languages.

## 8. References and BibTeX

1. John F. Ehlers, “Identifying Peaks And Valleys In Ranging Markets:
   The Reversion Index,” *Technical Analysis of Stocks & Commodities*,
   volume 44, number 1, January 2026, pp. 16–18.
   [Article](https://technical.traders.com/archive/article.asp?file=%5CV44%5CC01%5C066EHLE.pdf).
   Read from the supplied TASC content.md.
2. John F. Ehlers, “Reversion Index,” MESA Software paper, supplied local copy.
   [Paper](https://www.mesasoftware.com/papers/Reversion%20Index.pdf).
   The supplied metadata dates it 2026; the code copyright is 2025.
3. *Traders' Tips — January 2026*, supplied tips.md and code files:
   John Robinson/TradeStation; Dion Kurczek/Wealth-Lab;
   PineCoders/TradingView; Ward Systems/NeuroShell;
   Rajeev Jain/Python; and the supplied NinjaTrader port.
   [Traders' Tips](https://www.traders.com/Documentation/FEEDbk_docs/2026/01/TradersTips.html).
4. John F. Ehlers, *Cycle Analytics for Traders: Advanced Technical Trading
   Concepts*, Wiley, 2013, ISBN 9781118728604. Chapters 1, “Unified Filter
   Theory,” and 3, “Smoothing Filters on Steroids,” consulted locally.
5. John F. Ehlers, *Cybernetic Analysis for Stocks and Futures: Cutting-Edge
   DSP Technology to Improve Your Trading*, Wiley, 2004,
   ISBN 9780471463078. Chapter 13, “Super Smoothers,” consulted locally.
6. John F. Ehlers, *Cybernetic Trading Indicators*, 2025. Listed in the article's
   further reading; its contents were not available in the supplied package
   and are not claimed as a mathematical source for this implementation.
7. John F. Ehlers, “The Continuation Index: Trend Onset And Trend Exhaustion,”
   *Technical Analysis of Stocks & Commodities*, volume 43, September 2025.
   Listed as historical context in the article; its algorithm is not used here.

The Python tip's attribution names Rajeev Jain and dates its implementation
November 12–14, 2025, with
[TraderTipArticles](https://github.com/jainraje/TraderTipArticles/) as its repository.
The NinjaTrader source headers identify NinjaTrader_HelomS and
NinjaTrader_ChelseaB; their unrelated Laguerre/Highpass captions are not used to
infer different indicator provenance.

~~~bibtex
@article{ehlers2026reversionIndex,
  author = {Ehlers, John F.},
  title = {Identifying Peaks And Valleys In Ranging Markets: The Reversion Index},
  journal = {Technical Analysis of Stocks \& Commodities},
  year = {2026},
  volume = {44},
  number = {1},
  month = jan,
  pages = {16--18},
  url = {https://technical.traders.com/archive/article.asp?file=%5CV44%5CC01%5C066EHLE.pdf}
}
@misc{ehlers2026mesaReversionIndex,
  author = {Ehlers, John F.},
  title = {Reversion Index},
  year = {2026},
  howpublished = {MESA Software paper},
  url = {https://www.mesasoftware.com/papers/Reversion%20Index.pdf},
  note = {Year follows supplied metadata; code copyright 2025}
}
@misc{traderstips2026jan,
  title = {Traders' Tips --- January 2026},
  howpublished = {Technical Analysis of Stocks \& Commodities},
  year = {2026},
  month = jan,
  url = {https://www.traders.com/Documentation/FEEDbk_docs/2026/01/TradersTips.html},
  note = {Reversion Index implementations from TradeStation, Wealth-Lab,
          TradingView, NeuroShell, Python, and NinjaTrader}
}
@misc{jain2025pythonReversionIndex,
  author = {Jain, Rajeev},
  title = {Python Reversion Index},
  year = {2025},
  month = nov,
  url = {https://github.com/jainraje/TraderTipArticles/},
  note = {November 12--14 implementation; January 2026 Traders' Tips}
}
@misc{robinson2026tradeStationReversion,
  author = {Robinson, John},
  title = {TradeStation: Reversion Index},
  year = {2026},
  url = {https://www.traders.com/Documentation/FEEDbk_docs/2026/01/TradersTips.html},
  note = {TradeStation Securities; supplied EasyLanguage code}
}
@misc{pinecoders2026reversion,
  author = {{PineCoders}},
  title = {TASC 2026.01 The Reversion Index},
  year = {2026},
  url = {https://www.tradingview.com/u/PineCodersTASC/#published-scripts},
  note = {Supplied Pine Script version 6}
}
@misc{kurczek2026wealthlabReversion,
  author = {Kurczek, Dion},
  title = {Wealth-Lab: Reversion Index},
  year = {2026},
  url = {https://www.traders.com/Documentation/FEEDbk_docs/2026/01/TradersTips.html},
  note = {WealthLab 8 indicator and crossover strategy description}
}
@misc{ward2026neuroshellReversion,
  author = {{Ward Systems Group}},
  title = {NeuroShell Trader: Reversion Index},
  year = {2026},
  url = {https://www.traders.com/Documentation/FEEDbk_docs/2026/01/TradersTips.html},
  note = {Normalized momentum sums and two SuperSmoother lines}
}
@misc{ninjatrader2026reversion,
  author = {{NinjaTrader\_HelomS} and {NinjaTrader\_ChelseaB}},
  title = {ReversionIndex and SuperSmootherFunction},
  year = {2026},
  howpublished = {Supplied NinjaTrader 8 C\# port},
  note = {Contributor names taken from the supplied source headers}
}
@book{ehlers2013cycle,
  author = {Ehlers, John F.},
  title = {Cycle Analytics for Traders: Advanced Technical Trading Concepts},
  publisher = {Wiley},
  year = {2013},
  series = {Wiley Trading},
  isbn = {9781118728604},
  note = {Chapters 1 and 3 consulted}
}
@book{ehlers2004cybernetic,
  author = {Ehlers, John F.},
  title = {Cybernetic Analysis for Stocks and Futures:
           Cutting-Edge DSP Technology to Improve Your Trading},
  publisher = {Wiley},
  year = {2004},
  series = {Wiley Trading},
  isbn = {9780471463078},
  note = {Chapter 13 consulted}
}
@book{ehlers2025cyberneticTrading,
  author = {Ehlers, John F.},
  title = {Cybernetic Trading Indicators},
  year = {2025},
  note = {Bibliographic-only further reading from the TASC article}
}
@article{ehlers2025continuation,
  author = {Ehlers, John F.},
  title = {The Continuation Index: Trend Onset And Trend Exhaustion},
  journal = {Technical Analysis of Stocks \& Commodities},
  year = {2025},
  volume = {43},
  month = sep,
  note = {Historical context; not used in the Reversion Index computation}
}
~~~
