# Super Passband Filter: source investigation

Investigation date: 2026-10-20. Completed before preparing the standalone master.

## Book search and comparison

The supplied [2013 book](../../2013-cycle-analytics-for-traders/toc.md), including all 17 chapters, contains no Super Passband Filter listing or the `5/Period` two-EMA recurrence. Relevant background is present, but it is not another implementation of this indicator:

- [Chapter 2](../../2013-cycle-analytics-for-traders/ch2.md), equations 2-2 and 2-3: EMA recurrence and static-lag matching `alpha=2/(N+1)`. The article's heuristic `alpha=5/P` corresponds to conventional EMA length `N=2P/5-1`, not `N=P`.
- [Chapter 5](../../2013-cycle-analytics-for-traders/ch5.md): resonant two-pole band-pass, parameterized by center period and bandwidth, with input difference `Input-Input[2]` and zeros at both DC and Nyquist. Super Passband instead uses two real EMA poles, one DC zero, and no exact Nyquist zero. The book additionally uses a high-pass and peak AGC in its indicator listing; neither belongs in Super Passband.
- [Chapter 12](../../2013-cycle-analytics-for-traders/ch12.md): three-bar amplitude and power normalization illustrates RMS, but normalizes a different filtered waveform. Super Passband returns the raw PB and RMS threshold levels instead of dividing PB by RMS.

## Article authority

The [article](content.md), [TradeStation](tips/SPB.els), [TradersStudio](tips/SPB.trs), and [MetaStock](tips/SPB.txt) agree on

$$a_1=5/P_1,\quad a_2=5/P_2,\quad q_1=1-a_1,\quad q_2=1-a_2,$$

$$PB_t=(a_1-a_2)p_t+(a_2q_1-a_1q_2)p_{t-1}+(q_1+q_2)PB_{t-1}-q_1q_2PB_{t-2},$$

$$R_t=\sqrt{\frac1W\sum_{j=0}^{W-1}PB_{t-j}^2},\qquad W=50\text{ by default}.$$

The default periods are 40 and 60. The article explicitly permits another sufficiently long RMS window. Outputs are PB, +RMS, and -RMS; the plotted zero is a constant reference. The factor **5 is a heuristic setting**, not truncated pi or another exact mathematical constant. No approximate 1.414 or 3.14159 appears in the indicator code.

## Standalone startup and parameter domain

The article does not specify finite-sequence seeds or a NaN prefix. Use the first actual price as the common starting level of the two conceptual EMAs; their difference is zero. Set PB histories to zero and store that first price. Evaluate the printed recurrence from bar 2, avoiding artificial differences against a zero price before the record.

Keep the first bar's internal PB=0 in the RMS history. Expose PB from bar 2. Expose RMS only once W actual accepted bars, including the initial zero PB, are available, and no sooner than bar 2. For default W=50, PB has one leading NaN and each RMS field has 49. W=1 exposes all fields from bar 2. These conventions are part of the master API, not universal platform behavior.

Use finite real P1 and P2 strictly greater than 2.5: this is the exact stability condition `|1-5/P|<1`. Ordinary convex EMA gains additionally require P>=5. Values between 2.5 and 5 are stable but give alternating negative poles and are documented as unusual. Reject 2.5 and smaller rather than generating unstable fixtures. Equal periods produce zero; reversed periods invert PB and leave RMS unchanged. RMS window must be a positive integer. Missing NaN calls skip all states and the accepted-sample count; infinity is rejected.

## Supplied Tips differences

| Source | Difference | Master decision |
| --- | --- | --- |
| [TradeStation](tips/SPB.els) | Same PB recurrence and 50-bar RMS; additional example strategy. | Primary corroboration; retain current-to-oldest RMS loop. |
| [MetaStock](tips/SPB.txt) | Same formulas; PREV and moving-sum startup depend on platform history. | Declare finite-sequence initialization and availability explicitly. |
| [TradersStudio](tips/SPB.trs) | Same formulas, supplied as separate PB and RMS functions; strategy adds unrelated rules. | Return PB and both RMS levels together, without strategy behavior. |
| [AmiBroker](tips/SPB.afl) | Computes two AMAs/EMAs separately and subtracts; notes MACD equivalence. | Use the article's closed recurrence, which is algebraically equivalent but can differ in floating-point rounding. |
| [eSignal](tips/code/SuperPassband.efs) | Same recurrence and adjustable RMS window; waits for long EMA period, relies on internal history, and sums RMS from JavaScript null (coerced to zero). | Expose PB once the real previous price is available and RMS once its declared window is full. |
| [NinjaTrader](tips/ninja-trader/SuperPassBandFilter.cs) | Sets first **two PB values to raw prices**, causing a large price-level transient; sums RMS oldest to newest. Count is configurable but its divisor stays hard-coded 50. | Seed PB to zero; newest-to-oldest sum; configurable window is also the divisor. |
| [Updata](tips/SPB_updata.txt) | Starts its loop at max(P1,P2), delaying all computation; supplied continuation marker is platform-specific. | Start recursion on bar 2 and state the master availability rules. |
| [NeuroShell](tips/SPB_neuroshell_trader.txt) | Subtracts exponential averages labeled lengths 16 and 24. Its exact built-in smoothing convention is not supplied. | Derive coefficient-equivalent conventional lengths as 15 and 23 for alpha=2/(N+1); do not assume the snippet's 16/24 reproduces coefficients exactly. |
| [Wealth-Lab](tips/SPB.cs) | Calls unavailable library implementations, with hard-coded 40/60 despite configurable strategy periods. | Not an executable numeric oracle for arbitrary parameters. |

The spreadsheet is an additional platform artifact; no mesa source folder is supplied. TradeStation and the original article provide complete numeric equations without requiring the spreadsheet.

## Theory qualifications

DC cancellation is exact in the algebraic transfer function, but it does not guarantee the mean of every finite output window is zero or remove phase delay at every frequency. The EMAs have phase response and stored history. The article's subtraction of illustrated response curves should be understood as subtraction of **complex** responses, not just magnitudes. Super Passband attenuates high frequencies but has nonzero Nyquist gain for unequal periods.

RMS is square root of mean squared amplitude. Mean square, rather than RMS itself, is proportional to power. RMS equals population standard deviation only when the window mean is zero; no probability of reversal follows from RMS alone. The master preserves the source thresholds without adding a mean subtraction, statistical probability, AGC, or normalization.

The new standalone reference follows this article. All 20 reference cases were subsequently confirmed by the user on 2026-10-20.
