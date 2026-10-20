# Quotient Transform: source investigation

Investigation date: 2026-10-20. This comparison precedes preparation of the standalone `quotient-transform` master.

## Book search result

The supplied 2013 *Cycle Analytics for Traders* chapters do **not** define the Quotient Transform or the Early-Onset Trend Indicator. Chapter 15, *Indicator Transforms*, covers Fisher, inverse Fisher, and cube transforms. There is no book implementation of the quotient mapping to compare directly with the August 2014 article.

The book does contain its components:

- [Chapter 3](../../2013-cycle-analytics-for-traders/ch3.md), equation 3-3: the same two-pole SuperSmoother recurrence.
- [Chapter 7](../../2013-cycle-analytics-for-traders/ch7.md), listing 7-3: the same two-pole high-pass followed by SuperSmoother; the book example uses shortest/longest periods 40/80. Listings 7-4 and 7-5 use 10/48. The article instead uses adjustable low-pass period 30 by default and a **fixed 100-bar** high-pass.
- [Chapter 5](../../2013-cycle-analytics-for-traders/ch5.md): the same fast-attack, slow-decay amplitude envelope, with decay 0.991. Its discussion applies to a band-pass signal, rather than a quotient-mapped Roofing signal.
- [Chapter 14](../../2013-cycle-analytics-for-traders/ch14.md), listings 14-1 and 14-2: normalized Roofing as the `Real` component of a Hilbert transformer. The peak update and division are the same; the filter uses a 48-bar high-pass and low-pass 10 or configurable default 20. The article uses 100/30 and adds the quotient mapping, without computing a Hilbert transform.

## Article definition

The [article](content.md) defines the memoryless mapping

$$Q_K(X)=\frac{X+K}{KX+1},\qquad -1<K<1,\qquad -1\le X\le1.$$

Its complete price-input Early-Onset Trend Indicator performs: two-pole high-pass at 100 bars; SuperSmoother at `LPPeriod`; peak-envelope normalization; then this mapping. Defaults are `LPPeriod=30`, `K=0.85`. The envelope obeys

$$P_t=\max(0.991P_{t-1},|F_t|),\qquad X_t=F_t/P_t\ \text{when}\ P_t\ne0.$$

The EasyLanguage variable `X` retains its previous value when the peak is zero; its initial value is zero. On a constant series with zero filter state this makes the quotient equal to `K`, not zero. The plotted zero line is a reference level, not a second calculated output.

The article's additional `K=0.4` line is an entry/exit interpretation of the same normalized input. A master with one configured K and one returned float can reproduce either line; the static transform helper can map an already normalized oscillator directly.

## Traders' Tips differences

| Supplied implementation | Difference from the article | Master decision |
| --- | --- | --- |
| [TradeStation](tips/QuotientTransform.els) | Same filtering and AGC; computes two outputs with K1=0.85, K2=0.4, and supplies an example strategy | Use this as corroboration of the article; cover both K values in reference cases. |
| [eSignal](tips/QuotientTransform.efs) | Same recurrences; checks platform history availability; returns X=0 on a zero-peak bar instead of retaining the prior X | Keep article's hold-previous-X semantics, explicitly initialized to zero. |
| [AmiBroker](tips/QuotientTransform.afl) | Seeds HP, filter, and peak arrays from raw closes for the first two bars; computes recursion from index 2; uses rounded pi; examples 20/0.9 and 20/0.4 | Use precise constants and zero internal HP/filter/peak seeds; do not copy the price-valued HP/peak initialization. |
| [NinjaTrader](tips/ninja-trader/QuotientTransform.cs) | Holds HP/filter/peak at zero until zero-based `CurrentBar >= LPPeriod`; four K outputs, defaults ±0.4/±0.9 and LP=20 | Process the first available second difference on bar 3 instead of suppressing LPPeriod bars. One K per configured master instance. |
| [CQG](tips/QuotientTransform.cqg) | HP direct input term has one factor `(1-alpha/2)` instead of its square; peak compares to the previous **undecayed** peak before deciding whether to reset; defaults 15/0.95 | Follow the article's squared HP gain and decay-first envelope maximum. |
| [Updata](tips/QuotientTransform.updata) | SuperSmoother exponential uses `-1.414*2*pi/LPPeriod`, twice the article exponent, while its cosine still uses pi; loop starts at LPPeriod | Follow article exponent and declare independent startup. |
| [TradersStudio](tips/QuotientTransform.trs) | Supplied alpha expression has different parentheses, placing a sine expression inside the cosine | Follow the article high-pass coefficient expression. |
| [Wealth-Lab](tips/QuotientTransform.cs) | Strategy wrapper calls an unavailable library implementation; examples default LP=20, K=0.8/0.4 | Useful for interpretation, not an executable numeric oracle in this workspace. |

## Precision and standalone startup

Replace the mathematical approximations `1.414`, `.707`, and `3.14159` with sqrt(2), 1/sqrt(2), and pi. Keep **0.991** as the source's chosen decay parameter: it is an algorithmic setting, not a rounded spelling of a mathematical constant. Full-precision output cannot equal literal truncated-platform output to every decimal.

The book's AGC derivation includes a transcription/arithmetic inconsistency: `-1.5/20` equals `-0.075`, not `-0.75`. The correct gain ratio is approximately 0.8414, yielding approximately 0.99095 as the decay factor over 19 bars. The algorithm still uses the explicitly chosen 0.991, as the article does.

For consistency with the prepared Roofing master, store the first two real raw inputs with zero HP, low-pass, peak, and normalized histories. Evaluate the first complete second difference on **bar 3**. Run the low-pass, peak update, normalization, and transform on every subsequent finite bar, including hidden startup bars. Hide the first four returned values and expose bar 5. This startup policy is a declared standalone convention; the printed listings rely on platform histories and do not prescribe a universal NaN prefix.

The price-input master should expose only `lowpass_period` and `k`, preserving fixed high-pass 100 and decay 0.991. Accept finite real low-pass periods at least 2 and finite K strictly between -1 and 1. Low-pass periods at or above 100 remain mathematically defined even though the nominal filter edges cease to define a useful broad passband. NaN samples skip all state; infinite samples are rejected. A pure helper should implement the mapping for already normalized scalar inputs in [-1,1].

Preparation can now proceed with these source choices. Reference parameter cases require the user's confirmation before expected arrays are generated.
