# Walter Bressert — Implementation Spec (READY set)

Build reference for the indicators that are **author-defined with a full formula in a
primary Bressert text**. Companion to `indicators.md` (catalog/plan) and
`deep-research.md` (provenance). Every spec below cites its source `file:line` in this
repo. Items still BLOCKED/PARTIAL (DoubleStoc, BLine, HAL, DTI, trailing stops, timing
bands, Blue-Book indices, PTI) are **out of scope here** — see `indicators.md`.

Convention: `SMA(x, n)` = simple moving average; `EMA(x, n)` = exponential MA with
`K = 2/(n+1)`; `RSI(x, n)` = Wilder RSI. All series are bar-indexed `[i]`, newest at
the right edge. `price` defaults to `close` unless stated.

---

## 0. Shared primitives (build/verify first)

These back every indicator below and have closed-form definitions in the 1991
appendix (`1991-*/ap-01.md`). Reuse existing STC primitives where they exist.

| Primitive | Definition | Source |
|-----------|------------|--------|
| `SMA(x,n)` | mean of last `n` values | ap-01.md:37-45 |
| `EMA(x,n)` | `(x[i] − ema[i-1])·K + ema[i-1]`, `K=2/(n+1)` | ap-01.md:52-58 |
| `RSI(x,n)` | `100 − 100/(1+RS)`, Wilder `(n−1)/n` recursive smoothing | ap-01.md:65-76 |
| `Stoch %K(n)` | `100·(C − Lₙ)/(Hₙ − Lₙ)` | ap-01.md:89-92 |
| `meanDev(x,n)` | mean absolute deviation over `n` | ap-01.md:11 |

**Seed/warm-up decision (record):** Wilder RSI and EMA need a seed. Default to the
standard "first value = SMA of first `n`" seed; expose as a parameter; cross-check the
warm-up region against any deployed port before trusting early bars.

---

## 1. RSI3M3 (+ 5-bar detrend) — READY

**Source:** "a regular RSI 3 smoothed with a 3-bar moving average called the RSI3M3"
(1997:98); "a 3-bar RSI smoothed with a 3-bar moving average" (1998:41);
"a 3 RSI smoothed with a 3 MA" (TASC:164,176). Detrend: "a 5-bar moving average of the
RSI3M3 … subtracted from the RSI3M3 oscillator" (1997:131; 1998:59).

```
rsi3        = RSI(close, 3)
rsi3m3      = SMA(rsi3, 3)
rsi3m3_dt   = rsi3m3 - SMA(rsi3m3, 5)     # the detrended variant
```

**Params:** `rsi_len=3`, `smooth_len=3`, `detrend_len=5`. Buy/sell **lines are
parameters** (Part C.7 of `indicators.md`): default `buy=30`, `sell=70` (mirror,
inferred — 1997:110/1998:43); 1991 ch-10:15 uses `buy=30, sell=75`.

**Open decisions:** (a) RSI base — Wilder vs simple — *not stated*; default Wilder,
expose param. (b) final smoother — "moving average" → default SMA, expose param.
(c) sell line is inferred, flag it.

**Invariants:** `rsi3m3 ∈ [0,100]`; `rsi3m3_dt` centered near 0; finite after warm-up;
causal; flat-input → RSI defined-by-convention (document the 0/0 guard).

**Golden vectors:** commit arrays for `{buy=30}` on the shared fixture; cross-check
against a deployed RSI3M3 port.

---

## 2. 3-10 Oscillator (+ 16-term crossover) — READY *(newly unblocked)*

**Source:** "the 3-Day Moving Average minus a 10-Day Moving Average … the Crossover,
which is a 16-Term Moving Average of the oscillator" (1991 ch-13.md:7,11).

```
osc3_10     = SMA(price, 3) - SMA(price, 10)
crossover   = SMA(osc3_10, 16)
```

**Params:** `fast=3`, `slow=10`, `cross_len=16`, `price=close`.

**Pattern logic (signal layer, not the indicator value)** — implement separately if a
system is built: a valid high is above the zero line **and** the crossover and follows
a low formed below the crossover; mirror for lows (ch-13.md:15). Named patterns:
Two-Step Sell, Small-Bump Sell (ch-13), Bear-Kiss/OSCAR (1992:560-562, exact
conditions).

**Invariants:** unbounded oscillator centered near 0; finite after warm-up; causal;
flat-input → 0.

**Golden vectors:** `osc3_10` + `crossover` on the fixture.

---

## 3. Detrend pair — READY (centered = batch-only)

**Source:** centered detrend procedure (1997:72-78; TASC:204-208); real-time = same
without the back-shift (TASC:212; 1992:366).

```
real_time_detrend = price - SMA(price, N)                  # causal
centered_detrend  = price - shift(SMA(price, N), +N/2)     # NON-CAUSAL, batch only
```

In the 1997 manual the centered detrend is applied to **high and low separately**:

```
cen_ma     = shift(SMA(close, N), N/2)
detrend_hi = high - cen_ma
detrend_lo = low  - cen_ma
```

**Params:** `N=20` default (dominant cycle, range 14-25). Bands `±0.80` (typical
top/bottom) and `±2.0` (extreme) (1997:78).

**CRITICAL — look-ahead:** `centered_detrend` reads `~N/2` **future** bars. It is a
zero-phase / non-causal filter; the manual states it *"cannot be used for real-time
trading"* (1997:80). Implement **only as an offline/batch transform**, mark
`causal=false`, and exclude it from any streaming/live path. `real_time_detrend` is
causal and right-edge usable.

**Invariants:** both centered near 0; `real_time_detrend` causal; `centered_detrend`
**intentionally fails** the causality invariant — assert it is flagged batch-only;
last `N/2` bars of the centered series are undefined (not zero) — emit NaN, not 0.

---

## 4. MACD Detrend — READY

**Source:** 3-step recipe (1991 ch-08.md:98-102) over the COMPUTRAC MACD (26,12,9).

```
macd      = EMA(close, 12) - EMA(close, 26)
signal    = EMA(macd, 9)
spread    = macd - signal           # detrend around the crossover
macd_dt   = SMA(spread, 3)          # 3-term MA → new crossover line
```

**Params:** `fast=12`, `slow=26`, `signal=9`, `spread_smooth=3`.
**Invariants:** centered near 0; causal; finite after warm-up.

---

## 5. Fibonacci oscillator Buy/Sell lines — READY

**Source:** "multiplying the 1973 oscillator high at .6797 by .618 and subtracting the
result from .6797" (1991 ch-07.md:27,31). Applied to a *prior* oscillator extreme.

```
sell_line = osc_high * (1 - 0.618)   # = osc_high * 0.382
buy_line  = osc_low  * (1 - 0.618)   # mirror, from prior oscillator low
```

**Params:** `ratio=0.618` (expose; .382/.500/.618 are the usual set). These are
**levels overlaid on whichever oscillator** is in use, not a standalone series.

---

## 6. Keltner band — Bressert (σ) variant — READY

**Source:** "A 5-week moving average … the Keltner Channel is plotted 1.1 standard
deviations above and below this moving average" (1997:297).

```
mid   = SMA(close, 5)
upper = mid + 1.1 * stdev(close, 5)
lower = mid - 1.1 * stdev(close, 5)
```

**Params:** `len=5`, `mult=1.1` (both "can be modified" — 1997:297).
**NB:** despite the "Keltner" label this bands on **standard deviation**, i.e. it is a
Bollinger-style band, **not** the classic ATR Keltner. Name it explicitly
(`keltner_bressert_sigma`) to avoid confusion with an ATR Keltner deliverable.
**Invariants:** `lower ≤ mid ≤ upper`; bands collapse to `mid` on flat input.

---

## 7. Standard library (1991 appendix) — READY (textbook; credit originals)

Reproduce verbatim from `1991-*/ap-01.md`; attribute to Lambert/Appel/Wilder, not
Bressert.

```
typical   = (high + low + close) / 3
CCI       = (typical - SMA(typical, N)) / (0.015 * meanDev(typical, N))   # Sell +100 / Buy -100
MACD      = EMA(close,12) - EMA(close,26); signal = EMA(MACD, 9)
stoch_K   = 100 * (close - lowest(low, n)) / (highest(high, n) - lowest(low, n))
stoch_D_slow = SMA(stoch_D_fast, 3)
```

**NB (Stochastic):** the appendix `%D` typesetting (ap-01.md:97-100) is the standard
fast-`%D` sum form; verify against the canonical formula before committing golden
vectors. Use a **half-cycle lookback** per Bressert's usage rule (TASC:112).

---

## Verification plan (all of §1–§7)

Reuse the STC machinery:

1. **Declare source** per indicator (the `file:line` cited above).
2. **Freeze params** — defaults listed; no hardcoded buy/sell lines.
3. **Golden vectors** — run each construction on the shared close-only fixture; commit
   per-param arrays.
4. **Differential test** any third-party port to tolerance; investigate every mismatch.
5. **Invariants** (per-indicator above) + global: deterministic, finite-after-warmup,
   flat-input safe, and **causal except `centered_detrend`** (asserted batch-only).
6. **Provenance doc:** Regime-1 items claim *author-defined* fidelity with citations;
   nothing here claims authorship of the standard library (§7) or of DoubleStoc
   (out of scope — Regime-2 conform-to-port, see `indicators.md` A.2).

### Build order
§0 primitives → §1 RSI3M3 → §2 3-10 → §3 detrends → §4 MACD-detrend → §5 Fib lines →
§6 Keltner(σ) → §7 standard library.
