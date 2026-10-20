# Reverse EMA: source investigation

Investigation date: 2026-10-20. Completed before preparation of the standalone master.

## Book search

The supplied [2013 book contents](../../2013-cycle-analytics-for-traders/toc.md) and all 17 chapters contain no Reverse EMA indicator or eight-stage reverse-EMA implementation. Related material is background rather than another version:

- [Chapter 2](../../2013-cycle-analytics-for-traders/ch2.md), equation 2-2: identical forward EMA recurrence; equation 2-3 maps alpha to conventional EMA length.
- [Chapter 1](../../2013-cycle-analytics-for-traders/ch1.md): transfer-response notation, recursive/FIR filters, poles/zeros, and lag.
- [Chapter 7](../../2013-cycle-analytics-for-traders/ch7.md): Roofing and spectral dilation. Roofing has separately configurable high-pass and low-pass periods and is a different algorithm.

The article cites Martin Vicanek's *A New Reverse IIR Filtering Algorithm* (2015), [paper](https://vicanek.de/articles/ReverseIIR.pdf). No local copy or mesa source folder is supplied. The investigation uses the equations reproduced in Ehlers' article; it does not claim an independent audit of Vicanek's paper.

## Critical difference between the article's theory and executable code

For c=1-alpha, the theoretical truncated geometric FIR factors as

$$\sum_{n=0}^{255}c^nz^{-n}=\prod_{k=0}^7(1+c^{2^k}z^{-2^k}).$$

Reversing its coefficients with a causal delay gives

$$G_{theory}(z)=\prod_{k=0}^7(c^{2^k}+z^{-2^k}),$$

with total degree/delay **255 bars**. However, the printed executable code uses **one bar at every stage**:

```easylanguage
RE1 = CC*EMA + EMA[1];
RE2 = Power(CC, 2)*RE1 + RE1[1];
RE3 = Power(CC, 4)*RE2 + RE2[1];
// ... all remaining historical references are [1] ...
RE8 = Power(CC, 128)*RE7 + RE7[1];
Wave = EMA - AA*RE8;
```

Its actual reverse-stage response is

$$G_{code}(z)=\prod_{k=0}^7(c^{2^k}+z^{-1}),$$

an **eight-bar** FIR applied to the forward EMA. The powers 1,2,4,...,128 change coefficient values, not history indices. TradeStation, AmiBroker, Updata, TradersStudio, MetaStock, NinjaTrader, and eSignal all implement these one-bar stages. The master therefore follows the executable article/Tips code. Substituting dyadic delays would create a different indicator and different reference arrays.

The theory also prints `1/(1-cZ)` just before expanding it in negative powers. The forward causal expression consistent with that expansion is `1/(1-cZ^-1)`. The complete self-contained description preserves the original formulas and explains these notation discrepancies.

## Master calculation and startup

Default alpha=0.1; article examples use 0.05 for trend and 0.3 for cycle. Define c=1-alpha, g_k=c^(2^k), then compute forward EMA, the eight one-bar stages in order, and `EMA-alpha*RE8`. Zero initialize EMA and every reverse-stage history, as in the article's variable declarations. Process the first finite input with `EMA=alpha*price`; do not seed EMA at that first price. Every stage updates on every accepted bar, including hidden startup bars.

The standalone API masks the first eight accepted outputs with NaN, exposing bar 9 once an eight-bar reverse FIR history is available. This is an explicit visibility convention, not an assertion that the EMA's infinite-memory transient has settled. Original EasyLanguage variable histories are initialized to zero; other platforms seed prices or propagate nulls differently.

Only alpha is configurable, finite `0 < alpha <= 1`. The alpha=1 boundary has c=0 and reduces to `price[t]-price[t-8]`, a useful exact test. Alpha=0 is excluded as a degenerate frozen EMA; alpha>1 is outside the ordinary nonnegative EMA-weight domain. The eight stages are fixed. NaN calls omit all states and count increments; infinity is rejected before mutations.

## Source implementation differences

| Supplied source | Difference | Master decision |
| --- | --- | --- |
| [TradeStation](tips/REMA.els) | Same one-bar stage code; wrapper uses separate trend/cycle alphas 0.05/0.3 and adds strategy rules. | Corroborating numeric authority; one configured alpha and scalar output per object. |
| [MetaStock](tips/REMA_metastock.txt) | Same one-bar recurrences; EMA seed and historical null handling depend on PREV/Ref. | Declare zero histories and eight hidden outputs. |
| [TradersStudio](tips/REMA.trs) | Same powers and one-bar stages; function packaging differs. | Preserve article arithmetic. |
| [Updata](tips/REMA_updata.txt) | Same recurrence from its first loop date, with zero-declared states and HIST references. | Preserve article recurrence with explicitly declared finite sequence. |
| [AmiBroker](tips/REMA.afl) | Uses AMA for forward EMA and array Ref with null propagation; loop doubles coefficient exponents, still with lag 1. | Implement scalar zero-seeded forward EMA, update all stages, and mask first eight outputs. Do not assume AMA seeds match. |
| [NinjaTrader](tips/ninja-trader/REMA.cs) | First EMA is raw price and it returns before computing any reverse stages on bar 1. Later equations match. Its UI accepts alpha values beyond the ordinary EMA range. | Keep article zero EMA seed, process every stage from bar 1, and validate ordinary alpha domain. |
| [eSignal](tips/code/Reverse_EMA.efs) | Final subtraction uses **hard-coded 0.1**, ignoring Alpha except at the default. Rewrites EMA as `(price-old)*alpha+old`, propagates stage-history nulls, and delays work by `3*(2/alpha-1)` bars. | Use configured alpha in subtraction, article multiply/add order, and explicit zero histories. |
| [Wealth-Lab](tips/REMA.cs) | Wrapper calls unavailable `ReverseEMA.Series`; library internals are not supplied. | Not an executable numeric oracle. |

## Consequences for interpretation and precision

There are no truncated pi or sqrt(2) constants in this algorithm. Coefficient powers are computed at binary64 precision with `math.pow(c, exponent)`, and the scalar recurrence is not rounded until fixture serialization. Retain fixed eight stages and source multiplication/addition order.

The code's exact DC gain is `c^256`, not strictly zero. The identity `alpha*product(1+c^(2^k))=1-c^256` explains why default alpha appears well detrended, while small alpha can leave substantial constant-price response. Theoretical FIR truncation error and the additional change to one-bar delays are distinct effects. The master neither compensates DC residual nor changes delays to make the theory and code agree.

The literal code is causal, but it is not a general exact zero-phase forward/backward EMA. Its eight-stage cascade and forward EMA have phase response; observed near-alignment of chart turns does not establish zero lag or prediction at every frequency.

The executable article is the master authority. All 14 reference parameter cases were subsequently confirmed by the user on 2026-10-20.
