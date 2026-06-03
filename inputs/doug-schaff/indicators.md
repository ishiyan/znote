# Doug Schaff — Indicator(s) & Implementation Plan

Doug Schaff is a single-indicator author. The entire implementation surface is one
oscillator: the **Schaff Trend Cycle (STC)**. This document is both the indicator
list and the plan for (a) implementing STC and (b) **validating** an implementation
when **no primary source from the author exists**.

## Indicator List

| # | Indicator | First Public | Category | Source of truth | Primary author text? |
|---|-----------|--------------|----------|-----------------|----------------------|
| 1 | **Schaff Trend Cycle (STC)** | Code released 2008 (developed late 1990s) | Oscillator / Cycle | Convergent open-source code (ProRealCode `schaff-trend-cycle2`) | **None located** — no article, white paper, or book by Schaff defines the formula or defaults |

Everything below is about this one indicator.

---

## Part A — The Verification Problem (the hard question)

> *"How do we know that various MQL5 implementations are correct if we don't have
> the definitive article/book from the author?"*

**Short answer: we can't establish *authorial* correctness, because there is no
ground truth to check against.** Schaff never published a formula. So "correct" has
to be **redefined** — and the implementations do **not** in fact all agree.

### A.1 Three notions of "correct"

| Notion | Definition | Achievable here? |
|--------|-----------|------------------|
| **Authoritative correctness** | Matches the author's published specification | **No** — no primary spec exists |
| **Reference/consensus correctness** | Matches the de-facto reference that the ecosystem actually descends from | **Yes** — pick a named reference and conform to it byte-for-byte |
| **Internal/numerical correctness** | No NaN/∞, no divide-by-zero, deterministic, bounded 0–100, causal (no look-ahead) | **Yes** — testable mechanically |

Since (1) is impossible, the only honest plan is: **declare a reference, conform to
it, and characterize every deviation.** We do **not** claim our output is "what
Schaff intended"; we claim it is "bit-concordant with reference X under parameters
Y."

### A.2 Proof that the implementations disagree (this is the whole point)

I pulled three widely-used public implementations. They are **not** the same
indicator:

| Implementation | Stochastic passes | %D smoothing | Final formula | Default fast/slow/cycle | Verdict |
|----------------|-------------------|--------------|---------------|--------------------------|---------|
| **ProRealCode `schaff-trend-cycle2`** (Malagrida 2017) | **2** (cascade) | EMA, α = factor (0.5) | `PFF` = smoothed 2nd %K | 23 / 50 / 10 | **De-facto reference** |
| **pandas-ta-classic** `stc.py` | 2 (cascade) | EMA, α = 0.5 | same as ProRealCode | **12 / 26** / 10 | Faithful port **except a guard bug** (see A.3) + different default periods |
| **freqtrade/technical** `stc()` | **1** (single) | SMA (`STOD`) | `100·(MACD−STOK·MACD)/(STOD·MACD−STOK·MACD)` — **algebraically not STC** | 23 / 50 / 10 | **Incorrect** — different structure and a nonsensical final expression |

Three "Schaff Trend Cycle" functions, three different outputs. Anyone who picks one
at random and assumes it is "the" STC is wrong. This is exactly why a reference must
be declared explicitly.

### A.3 A concrete porting bug (illustrates the risk)

ProRealCode guards the first stochastic on the **range** being positive:

```
Value2 = Highest[TCLen](XMAC) - Value1     // the range
if Value2 > 0 then  Frac1 = (XMAC - Value1)/Value2 * 100  else  Frac1 = Frac1[1]
```

pandas-ta-classic ports the **second** stochastic correctly (`if pf_range > 0`) but
the **first** one guards on the wrong quantity — the *lowest value* instead of the
range:

```python
if lowest_xmacd.iloc[i] > 0:          # <-- should be xmacd_range > 0
    stoch1[i] = 100 * ((xmacd.iloc[i] - lowest_xmacd.iloc[i]) / xmacd_range.iloc[i])
else:
    stoch1[i] = stoch1[i - 1]
```

Because a MACD line is **negative** much of the time, `lowest_xmacd > 0` is often
false, so the code carries the previous value forward when it shouldn't — producing
values that **diverge from the reference** in any down-trend. A reader without the
reference code would never notice. This single line is the case study for the user's
question.

### A.4 How we *actually* validate (the method)

Without a primary source, validation = **differential testing against a declared
reference + invariant checks + provenance**:

1. **Declare the reference.** Use **ProRealCode `schaff-trend-cycle2`** as the
   canonical STC (it is the source pandas-ta itself cites, and it implements the
   full double-stochastic with EMA "%Fast D"). Pin the exact version/URL.
2. **Freeze a parameter set.** STC is meaningless without stating
   `(fast, slow, tclen, factor)` — see Part B. Validate per parameter set.
3. **Generate golden vectors.** Run the reference on a fixed synthetic + real OHLC
   series, export `(MACD, stoch1/PF, STC)` to a CSV checked into the repo. These are
   the regression oracle.
4. **Differential test** every new port against the golden vectors to a tolerance
   (e.g. abs error < 1e-6 after warmup). Investigate *every* mismatch — it is either
   a bug in the port or a documented reference divergence.
5. **Invariant checks** (hold for any correct STC, no oracle needed):
   - output ∈ [0, 100] after warmup;
   - finite (no NaN/∞) once enough bars exist;
   - **causal**: `STC[i]` depends only on bars ≤ i (no look-ahead);
   - deterministic / reproducible;
   - flat-input window does not throw (divide-by-zero guard fires).
6. **Cross-implementation triangulation.** Where ≥2 *independent* implementations
   that claim the same structure agree to tolerance, confidence rises that the
   divergence is not in our port. Disagreement localizes the suspect (as in A.3).
7. **Document residual ambiguity.** Anything the reference leaves unspecified
   (warm-up convention, `%D` = EMA vs SMA, initialization of the recursion) is a
   **decision**, recorded in the spec — not a "correctness" claim.

**Bottom line for the catalog:** the MQL5 entries are best treated as *a family of
related implementations*, not interchangeable truths. Our deliverable will state
"concordant with ProRealCode schaff-trend-cycle2 @ params (23,50,10,0.5)" and ship
the golden vectors that back that claim.

---

## Part B — Canonical Specification (recovered from the reference)

> Source-of-truth: ProRealCode `schaff-trend-cycle2`, corroborated step-for-step by
> pandas-ta-classic (modulo A.3). Full sourced derivation:
> `outputs/.drafts/doug-schaff-research-mechanics.md`.

### B.1 Definition

```
STC = SecondSmooth( Stochastic( FirstSmooth( Stochastic( MACD ) ) ) ),  range 0–100
```

### B.2 Parameters (must be stated explicitly with every result)

| Parameter | Symbol | Forex-native default | Generic/library default | Status |
|-----------|--------|----------------------|--------------------------|--------|
| Cycle / TC length | `tclen` | **10** | **10** | consistent everywhere |
| Fast MACD EMA | `fast` | **23** | **12** | **diverges by source** |
| Slow MACD EMA | `slow` | **50** | **26** | **diverges by source** |
| Smoothing factor | `factor` | **0.5** (EMA α) | **0.5** | consistent |
| Overbought / oversold | — | **75 / 25** (some 80/20) | — | platform convention |

> The **23/50** pair is the forex-native default that propagates through the
> reference code, but it is **not confirmed to be Schaff's own published numbers**
> (no primary source). Treat the parameter set as a declared input, never as an
> authorial constant.

### B.3 Reference pseudocode (port this exactly)

```
# STC(close, fast, slow, tclen, factor):

# 0. MACD line
macd[i] = EMA(close, fast)[i] - EMA(close, slow)[i]

# 1. First stochastic %K of MACD over tclen
ll1 = Lowest(macd, tclen)[i]
hh1 = Highest(macd, tclen)[i]
range1 = hh1 - ll1
if range1 > 0:  k1 = 100 * (macd[i] - ll1) / range1      # <-- guard on RANGE (see A.3)
else:           k1 = k1_prev                              # flat-window carry-forward

# 2. First EMA smoothing ("%Fast D"), alpha = factor
pf[i] = pf_prev + factor * (k1 - pf_prev)

# 3. Second stochastic %K of pf over tclen
ll2 = Lowest(pf, tclen)[i]
hh2 = Highest(pf, tclen)[i]
range2 = hh2 - ll2
if range2 > 0:  k2 = 100 * (pf[i] - ll2) / range2
else:           k2 = k2_prev

# 4. Second EMA smoothing -> STC
stc[i] = pff_prev + factor * (k2 - pff_prev)
return stc        # plot with 25/75 (or 20/80) bands
```

### B.4 Decisions the reference leaves open (record these in the spec)

| Ambiguity | Reference behavior | Our decision |
|-----------|--------------------|--------------|
| `%D` smoothing | EMA with α = factor (NOT Lane's SMA) | **EMA, α = factor** — match reference |
| Recursion seed | `PF[0]=0`, `PFF[0]=0` (pandas-ta); ProRealTime auto-seeds first bar | **Seed = 0**, document warm-up |
| Flat window (range = 0) | carry forward previous %K (ProRealCode) vs previous smoothed (pandas-ta) | **carry previous %K** (reference) |
| First-stoch guard | range > 0 (ProRealCode) — NOT `lowest > 0` (pandas-ta bug) | **range > 0** |
| Warm-up length | ≈ `slow + 2·tclen` bars before output is meaningful | mark first ≈ `slow+2·tclen` bars as warm-up/NaN |
| Default periods | 23/50 (forex) vs 12/26 (generic) | **expose as parameters**; default 23/50, document both |

---

## Part C — Implementation Plan (tasks)

Aligned with the repo convention (stdlib-only, deterministic, portable to
Rust/Zig/Go). STC needs only: EMA, rolling-min, rolling-max, and a scalar EMA
recursion — no external math libraries.

1. **Primitives** (reusable, already needed by other indicators):
   - `ema(series, period)` — standard EMA, α = 2/(period+1).
   - `rolling_min(series, win)`, `rolling_max(series, win)` — windowed extrema
     (O(n) deque or simple O(n·win) for the reference port).
2. **Core `stc(close, fast=23, slow=50, tclen=10, factor=0.5)`** — implement B.3
   verbatim; return `(stc, macd, pf)` so intermediate stages are testable, not just
   the final line.
3. **Edge-case handling** — flat-window guard (range = 0 → carry %K), warm-up NaN
   region, seed = 0; assert output ∈ [0,100].
4. **Golden vectors** — vendor a fixed OHLC fixture (synthetic ramp+sine + a real
   FX/equity slice), run the reference, commit `stc_golden_{params}.csv`.
5. **Differential tests** — compare port vs golden vectors (abs tol 1e-6 post
   warm-up); invariant tests (bounds, finiteness, causality, determinism,
   flat-input).
6. **Cross-checks** — optionally diff against pandas-ta-classic with its bug
   *patched* (range guard) to confirm independent agreement; record the unpatched
   discrepancy as a known difference.
7. **Conformance doc** — one line per output: "concordant with ProRealCode
   schaff-trend-cycle2 @ (23,50,10,0.5)" + link to golden CSV. **No claim of
   authorial fidelity.**
8. **Port** the verified reference to Rust/Zig/Go, each re-validated against the
   *same* golden CSV (the CSV is the language-independent oracle).

### What we deliberately will NOT do
- Claim any single MQL5 entry is "the correct" STC.
- Treat 23/50 (or 12/26) as an authorial constant.
- Use freqtrade/technical's `stc` as a reference (its formula is not STC).
- Trust pandas-ta-classic's first-stochastic branch without the A.3 fix.

---

## Reference Sources

| Role | Source | URL |
|------|--------|-----|
| **Declared reference** | ProRealCode `schaff-trend-cycle2` (Malagrida 2017) | https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle2/ |
| Corroborating port (with A.3 bug) | pandas-ta-classic `momentum/stc.py` | https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/momentum/stc.py |
| Counter-example (NOT STC) | freqtrade/technical `stc()` | https://github.com/freqtrade/technical/blob/master/technical/indicators/indicators.py |
| Credits Schaff, alt port | bukosabino/ta `STCIndicator` | https://github.com/bukosabino/ta/blob/master/ta/trend.py |
| Single-stochastic variant | ProRealCode `schaff-trend-cycle` (lolo 2015) | https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle/ |
| Thresholds / prose | MotiveWave STC docs (0–100, 75/25) | https://docs.motivewave.com/studies/s-t.md |
| Full sourced mechanics | this repo | `outputs/.drafts/doug-schaff-research-mechanics.md` |
| Catalog of all implementations | this repo | `trading-research/doug-schaff.md` |
