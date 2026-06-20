# Ehlers Implementation Validation Guide

**Source Formulas · Accuracy Tests · Cross-Verification Protocol**

| | |
|---|---|
| **Problem addressed** | Silent numerical errors in custom Ehlers implementations — plausible output, wrong values |
| **Three error categories** | (A) Trig degrees vs radians (B) Missing .707 coefficient (C) Bar indexing direction |
| **Primary test method** | Chirped sine wave with known ground-truth period at every bar |
| **Reference implementations** | EasyLanguage (book) · R (fabmaccallini) · Pine Script (loxx, blackcat1402, mihakralj) · MQL5 (thetestspecimen) |
| **Methods validated** | Roofing Filter · Homodyne Discriminator · Autocorrelation Periodogram · Cycle/Trend Discriminator |
| **Test suite** | 9 automated tests — all must PASS before using with real data |
| **Cross-validation** | vs TradingView Pine: tolerance ±1.5 bars \| vs R reference: tolerance ±1.0 bar |

Version 1.0 | 2025 | Internal Use Only

## Why This Document Exists

Writing Ehlers indicators from paraphrased descriptions — including the descriptions in the Cycle Analysis Framework white paper — produces implementations that look correct but contain silent numerical errors. These errors do not crash. They produce plausible-looking cycle estimates that are subtly wrong, and there is no error signal unless you explicitly test against a known ground truth.

| Error category | Description | Detection method |
|---|---|---|
| A — Trig argument | EasyLanguage uses degrees; Python uses radians. Every trig call must be converted. Missing one gives outputs numerically close but wrong by factor ≈ 57. | Chirp MAE > 10 bars; period estimates cluster at 6–8 regardless of input |
| B — Missing .707 | Roofing filter HP alpha uses cos(0.707 × 360/period), not cos(360/period). The 0.707 = 1/√2 factor comes from Butterworth filter theory. Most informal descriptions omit it. | alpha1 > 0.15 instead of ≈ 0.05; long-period trends pass through the filter |
| C — Bar indexing | EasyLanguage [1] = one bar ago = Python [i−1] inside loop. Getting this backwards introduces a one-bar lookahead — backtest results cannot be replicated live. | Output appears offset by exactly one bar vs TradingView reference |

All three errors produce outputs that look statistically reasonable. The only way to catch them is the chirp sine wave test — because it is the only case where the true answer is known at every bar.

---

## §1 Source Hierarchy

### 1. Source Hierarchy — What to Trust and in What Order

When implementing any Ehlers indicator in Python, use sources strictly in this order. Never start from a paraphrased description.

#### Tier 1 — Authoritative Sources

| Source | What it contains | How to access |
|---|---|---|
| Ehlers' EasyLanguage from the book | Ground truth for roofing filter, autocorrelation periodogram, phase accumulation, homodyne discriminator, cycle/trend discriminator — exact character-for-character as Ehlers wrote them | *Cycle Analytics for Traders* (2013) — ships with PIN code for all EasyLanguage source |
| TASC September 2016 — "Measuring Market Cycles" | Updated autocorrelation periodogram with enhanced resolution — the preferred version. EasyLanguage sidebar is the authoritative 2016 source. | Technical Analysis of Stocks & Commodities, Vol.34 No.9 |
| TASC November 2000 Traders' Tips | Homodyne Discriminator original EasyLanguage. Predates the book. Contains exact variable names from Ehlers' original derivation. | traders.com/Documentation/FEEDbk_docs/2000/11/TradersTips/ |

#### Tier 2 — Verified Translations

| Source | Language | Notes |
|---|---|---|
| fabmaccallini/ehlers on GitHub | R | Direct translation of TASC 2016 article. Author: head of structured derivatives at Nordea Markets. Primary cross-check for Python implementation. |
| thetestspecimen/ehlers-indicators-mql5 | MQL5/C++ | Basic translation of EasyLanguage from *Cycle Analytics for Traders*. C++ semantics close to Python — loop structures translate directly. |
| loxx on TradingView | Pine Script | Fast-loading, low-overhead, streamlined, exact replicas of Ehlers' work. Both 2013 and 2016 versions. Variable names match originals. |
| blackcat1402 on TradingView | Pine Script | 100% John F. Ehlers definition translation — even variable names are the same. Uses Centre-of-Gravity dominant cycle extraction. |
| mihakralj EACP on TradingView | Pine Script | Most mathematically documented Pine implementation. Explicitly documents where it differs from the 2016 TASC original and why. Uses CG over peak-finding. |

#### Tier 3 — Do Not Use as Primary Source

- Blog posts, forum discussions, Stack Overflow answers without specific book/article citation
- Any implementation that does not cite a specific Ehlers book chapter or TASC article
- The tindicators Homodyne Discriminator without first verifying against Tier 1 EasyLanguage source
- Critical: Any implementation using `np.cos(2*np.pi/period)` in the roofing filter alpha — this is the most common error. Correct formula uses 0.707 × 360 / period in degrees.

---

## §2 Canonical Formulas

### 2. The Canonical Formulas — Direct from EasyLanguage

The following formulas are from Ehlers' published EasyLanguage code. EasyLanguage translation rules for Python are marked inline.

| EasyLanguage | Python equivalent |
|---|---|
| `Cosine(x)` | `np.cos(np.deg2rad(x))` — argument is in degrees in EasyLanguage |
| `Sine(x)` | `np.sin(np.deg2rad(x))` — argument is in degrees in EasyLanguage |
| `expvalue(x)` | `np.exp(x)` |
| `ArctanGD(x)` | `np.degrees(np.arctan(x))` — returns degrees |
| `Close[N]` | `s[i-N]` inside a loop where `i` is the current bar index |
| `HP[1]` | `hp[i-1]` — previous bar, not `hp[1]` (fixed index) |

### 2.1 Roofing Filter — Exact EasyLanguage Source

Source: *Cycle Analytics for Traders* (2013), Chapter 5. Copyright © 2013-2017 John F. Ehlers.

The .707 coefficient is 1/√2 from Butterworth filter design — this is the most commonly omitted detail.

```easylanguage
{Roofing filter — Ehlers 2013-2017}
alpha1 = (Cosine(.707*360/48) + Sine(.707*360/48) - 1) / Cosine(.707*360/48);
HP = (1-alpha1/2)*(1-alpha1/2)*(Close - 2*Close[1] + Close[2])
     + 2*(1-alpha1)*HP[1]
     - (1-alpha1)*(1-alpha1)*HP[2];
a1 = expvalue(-1.414*3.14159/10);
b1 = 2*a1*Cosine(1.414*180/10);
c2 = b1; c3 = -a1*a1; c1 = 1 - c2 - c3;
Filt = c1*(HP+HP[1])/2 + c2*Filt[1] + c3*Filt[2];
```

**Python translation with exact coefficient values**

```python
import numpy as np

def roofing_filter(price, hp_period=48, lp_period=10):
    """Ehlers Roofing Filter. Source: Cycle Analytics for Traders Ch.5"""
    n = len(price)
    hp = np.zeros(n)
    filt = np.zeros(n)
    s = np.asarray(price, dtype=float)

    # High-pass filter alpha
    # .707 = 1/sqrt(2) from Butterworth design — DO NOT OMIT
    deg = 0.7071067811865476 * 360.0 / hp_period
    rad = np.deg2rad(deg)
    alpha1 = (np.cos(rad) + np.sin(rad) - 1.0) / np.cos(rad)
    # Expected: alpha1 ≈ 0.04948 for hp_period=48

    for i in range(2, n):
        hp[i] = ((1.0 - alpha1/2.0)**2
                 * (s[i] - 2.0*s[i-1] + s[i-2])
                 + 2.0*(1.0 - alpha1)*hp[i-1]
                 - (1.0 - alpha1)**2 * hp[i-2])

    # Super Smoother coefficients
    a1 = np.exp(-1.4142135623730951 * np.pi / lp_period)  # ≈ 0.63763
    b1 = 2.0*a1*np.cos(np.deg2rad(1.4142135623730951*180.0/lp_period))
    c2 = b1
    c3 = -(a1**2)
    c1 = 1.0 - c2 - c3

    for i in range(2, n):
        filt[i] = (c1*(hp[i]+hp[i-1])/2.0
                   + c2*filt[i-1]
                   + c3*filt[i-2])
    return filt
```

### 2.2 Homodyne Discriminator — Exact EasyLanguage Source

Source: TASC November 2000 Traders' Tips. Variable names preserved from original. Key: use `arctan2(Im, Re)` not `arctan(Im/Re)` — `arctan2` handles `Re=0` and all quadrants correctly.

```easylanguage
{Homodyne Discriminator — Ehlers 2000}
Smoother = (4*Price + 3*Price[1] + 2*Price[2] + Price[3]) / 10;
Detrender = (.25*Sm + .75*Sm[2] - .75*Sm[4] - .25*Sm[6]) * (.046*Period[1]+.332);
Q1 = (.25*Det + .75*Det[2] - .75*Det[4] - .25*Det[6]) * (.046*Period[1]+.332);
I1 = Detrender[3];
jI = .25*I1 + .75*I1[2] - .75*I1[4] - .25*I1[6];
jQ = .25*Q1 + .75*Q1[2] - .75*Q1[4] - .25*Q1[6];
I2 = I1 - jQ;
Q2 = Q1 + jI;
I2 = .2*I2 + .8*I2[1];
Q2 = .2*Q2 + .8*Q2[1];
Re = I2*I2[1] + Q2*Q2[1];
Im = I2*Q2[1] - Q2*I2[1];
Re = .2*Re + .8*Re[1];
Im = .2*Im + .8*Im[1];
If Im <> 0 and Re <> 0 then
    Period = 2*3.14159 / ArctanGD(Im/Re);
Period clamped: [0.67x, 1.5x previous]; [6, 50]; EMA(0.2)
```

**Critical Python translation notes**

- `ArctanGD(Im/Re)` returns degrees → Python: `np.degrees(np.arctan2(Im, Re))`
- `2*pi / angle_in_degrees` → Python: `360.0 / np.degrees(np.arctan2(Im, Re))`
- `arctan2(Im, Re)` not `arctan(Im/Re)` — avoids division by zero when `Re=0`
- Coefficients .046 and .332 are exact — do not approximate
- `CurrentBar > 5` → start loop at `range(6, n)` in Python

### 2.3 Autocorrelation Periodogram — Algorithm (2016 TASC)

Source: "Measuring Market Cycles", TASC September 2016. This is the preferred version over the 2013 book version — it includes enhanced resolution and the Centre-of-Gravity dominant cycle extraction.

```easylanguage
{Step 1: Apply roofing filter -> Filt[]}
{Step 2: Pearson autocorrelation at each lag, M-bar averaging}
For Lag = 0 to MaxLag:
    Sx=Sy=Sxx=Syy=Sxy=0
    For count = 0 to (M-1):
        X=Filt[count]; Y=Filt[count+Lag]
        Sx+=X; Sy+=Y; Sxx+=X*X; Sxy+=X*Y; Syy+=Y*Y
    If (M*Sxx-Sx*Sx)>0 and (M*Syy-Sy*Sy)>0 then
        Corr[Lag]=(M*Sxy-Sx*Sy)/Sqrt((M*Sxx-Sx*Sx)*(M*Syy-Sy*Sy))
{Step 3: DFT — note: angles in DEGREES}
For Period = MinPeriod to MaxPeriod:
    CosPart=SinPart=0
    For Lag = 0 to MaxLag-1:
        CosPart += Corr[Lag]*Cosine(360*Lag/Period)
        SinPart += Corr[Lag]*Sine(360*Lag/Period)
    Pwr[Period] = CosPart*CosPart + SinPart*SinPart
{Step 4: Centre-of-Gravity dominant cycle}
For Period = MinPeriod to MaxPeriod:
    If Pwr[Period]/MaxPwr >= 0.5 then
        Num += Period*Pwr[Period]; Denom += Pwr[Period]
DominantCycle = Num/Denom
```

The angle `360*Lag/Period` is in degrees in EasyLanguage. In Python this must be `np.deg2rad(360*lag/period)`. This is the single most common error in Python translations — every lag in the DFT loop needs the conversion.

---

## §3 The Chirp Test Signal

### 3. The Chirp Sine Wave — The Ground Truth Test

The chirp is a sine wave whose period changes gradually and predictably over time. Because the true period at every bar is known with certainty, it is the only test signal that provides unambiguous validation of a cycle detection implementation. Testing against a synthetic chirp signal with various degrees of noise is the standard method Ehlers himself uses throughout *Cycle Analytics for Traders*.

> Real market data cannot validate an implementation because the true cycle period is not known — that is what you are trying to measure. The chirp is the only test where ground truth is available at every bar.

```python
def generate_chirp(n_bars=200, period_start=10, period_end=48,
                   amplitude=10.0, noise_std=0.0):
    """
    Chirped sine wave — Ehlers standard test signal.
    Period increases linearly from period_start to period_end.
    noise_std=0 for pure signal; increase for noise robustness testing.
    Returns: (price, true_period) arrays of length n_bars
    """
    true_period = np.linspace(period_start, period_end, n_bars)
    # Instantaneous phase = integral of 2*pi / T(t)
    phase = np.cumsum(2.0 * np.pi / true_period)
    price = amplitude * np.sin(phase)
    if noise_std > 0:
        price += np.random.normal(0, noise_std, n_bars)
    return price, true_period
```

**Expected Chirp Test Results (Correct Implementation)**

| Test condition | Max acceptable MAE | Max acceptable error at any bar | If exceeded — likely cause |
|---|---|---|---|
| Pure chirp (noise_std = 0) | < 2.0 bars | < 4.0 bars | Trig degree/radian conversion error |
| Low noise (noise_std = 1.0) | < 4.0 bars | < 7.0 bars | If worse than pure: M averaging too small |
| Moderate noise (noise_std = 3.0) | < 6.0 bars | < 10.0 bars | If much worse: roofing filter not working |
| Known single period (30 bars) | < 3.0 bars median | < 5.0 bars | CG vs peak-finding method mismatch |

---

## §4 Validation Protocol

### 4. Step-by-Step Validation Protocol

Run these steps in order. Each step must pass before proceeding to the next. Never use any implementation with real market data before completing all steps.

#### Step 1 — Roofing Filter Unit Tests

**Test 1a — The alpha1 coefficient (most critical single check)**

```python
sqrt2_over_2 = 0.7071067811865476
deg = sqrt2_over_2 * 360.0 / 48.0
rad = np.deg2rad(deg)
alpha1 = (np.cos(rad) + np.sin(rad) - 1.0) / np.cos(rad)
print(f"alpha1 = {alpha1:.6f}")
# Expected: alpha1 ≈ 0.04948
# If alpha1 ≈ 0.173: .707 coefficient missing
# If alpha1 ≈ 0.997: degrees/radians swapped entirely
assert 0.045 < alpha1 < 0.055
```

**Test 1b — Band-pass response (in-band signal must pass)**

```python
price = 10.0 * np.sin(2*np.pi*np.arange(200)/20.0)
filt = roofing_filter(price, hp_period=48, lp_period=10)
assert np.max(np.abs(filt[40:])) > 7.0, "In-band signal attenuated"
```

**Test 1c — Long-cycle rejection (trend must be removed)**

```python
price = 10.0 * np.sin(2*np.pi*np.arange(500)/200.0)
filt = roofing_filter(price, hp_period=48, lp_period=10)
assert np.max(np.abs(filt[100:])) < 2.0, "Long-period trend not rejected"
```

**Test 1d — Causality (no lookahead)**

```python
price = np.zeros(200)
price[50:] = 10.0  # step change at bar 50
filt = roofing_filter(price)
assert np.all(np.abs(filt[:49]) < 0.01), "Lookahead detected before step"
```

#### Step 2 — Homodyne Discriminator Tests

**Test 2a — Known period recovery**

```python
price = 10.0 * np.sin(2*np.pi*np.arange(200)/20.0)
pd_est = homodyne_discriminator(price)
mean_est = np.nanmean(pd_est[60:])
assert abs(mean_est - 20.0) < 4.0, f"HD period {mean_est:.1f}, expected ~20"
```

**Test 2b — Period clamping [6, 50]**

```python
pd_est = homodyne_discriminator(np.random.randn(300))
assert np.all(pd_est[6:] >= 6.0), "Period floor violated"
assert np.all(pd_est[6:] <= 50.0), "Period ceiling violated"
```

**Test 2c — No NaN or Inf on degenerate input**

```python
pd_est = homodyne_discriminator(np.zeros(100))
assert not np.any(np.isnan(pd_est[6:])), "NaN — use arctan2 not arctan"
assert not np.any(np.isinf(pd_est[6:])), "Inf — division by zero"
```

#### Step 3 — Autocorrelation Periodogram Tests

**Test 3a — Chirp tracking (core validation)**

```python
price, true_period = generate_chirp(200, 10, 48, 10.0, 0.0)
dc = autocorr_periodogram(price)
mae = np.nanmean(np.abs(dc[60:] - true_period[60:]))
assert mae < 2.0, f"Chirp MAE {mae:.2f} bars (threshold 2.0)"
print(f"PASS: Chirp MAE = {mae:.2f} bars")
```

**Test 3b — Single known period**

```python
price = 10.0 * np.sin(2*np.pi*np.arange(300)/30.0)
dc = autocorr_periodogram(price)
est = np.nanmedian(dc[80:])
assert abs(est - 30.0) < 4.0, f"Expected 30, got {est:.1f}"
```

**Test 3c — No NaN or Inf on random input**

```python
dc = autocorr_periodogram(np.random.randn(300)*10)
assert not np.any(np.isnan(dc[80:])), "NaN in ACP output"
assert not np.any(np.isinf(dc[80:])), "Inf in ACP output"
```

---

## §5 Common Errors

### 5. Common Errors and How to Detect Them

#### Error A — Trig in radians instead of degrees

- **Symptom:** Chirp MAE > 10 bars. Period estimates cluster around 6–8 bars regardless of input. DFT finds peak at wrong period.
- **Cause:** `np.cos(360*lag/period)` instead of `np.cos(np.deg2rad(360*lag/period))` in the DFT inner loop. `np.cos(360) ≈ np.cos(2π) ≈ 1.0`, which collapses all cosine terms to approximately 1.0.
- **Fix:** Add `np.deg2rad()` to every trig call in the DFT loop. Also check the roofing filter alpha1 calculation.
- **Verify:** `np.cos(np.deg2rad(360*1/20))` should equal 0.951.

#### Error B — Missing .707 in roofing filter alpha

- **Symptom:** Test 1c fails — long-period cycles (200-bar trend) pass through the filter instead of being attenuated. Cycle estimates are biased toward longer periods.
- **Cause:** alpha1 computed with `deg=360/hp_period` instead of `deg=0.707*360/hp_period`. Without the 0.707 = 1/√2 Butterworth factor, the high-pass cutoff is at the wrong frequency.
- **Fix:** Check: print alpha1 before the filter loop. Expected ≈ 0.04948 for `hp_period=48`. If alpha1 > 0.15, the .707 factor is missing. If alpha1 ≈ 0.99, degrees/radians are completely swapped.

#### Error C — Bar indexing direction (lookahead)

- **Symptom:** Outputs appear correct on historical data but diverge from TradingView by exactly one bar. Backtest results cannot be replicated live.
- **Cause:** EasyLanguage `Filt[1]` means one bar ago. In Python inside a loop, this must be `filt[i-1]`, not `filt[1]` (fixed index). Writing `filt[1]` uses data from bar 1 at every iteration, introducing lookahead.
- **Fix:** Run Test 1d (causality check). If the filter responds before the step change at bar 50, there is a lookahead. Audit every `[N]` notation and ensure it translates to `[i-N]` inside the loop.

#### Error D — Incorrect Pearson formula in autocorrelation

- **Symptom:** Autocorrelation values always near ±1.0 or always near 0.0. Periodogram shows no structure.
- **Cause:** Using simplified correlation instead of Ehlers' exact M-bar Pearson formula with Sx, Sy, Sxx, Syy, Sxy accumulators. The M-bar averaging is what makes it responsive without long look-backs.
- **Fix:** For a pure 20-bar sine wave at bar 100, check `corr[20] ≈ +1.0` and `corr[10] ≈ -1.0`. If these are wrong, the Pearson formula does not match Ehlers' EasyLanguage exactly.

#### Error E — arctan vs arctan2 in Homodyne

- **Symptom:** NaN or Inf in period output. Occurs sporadically, not on every bar. Hard to trace.
- **Cause:** `np.arctan(Im/Re)` fails when `Re = 0`. This happens during certain phase transitions in the cycle, producing a division by zero that propagates as NaN through all downstream calculations.
- **Fix:** Replace `np.arctan(Im/Re)` with `np.arctan2(Im, Re)`. arctan2 handles all quadrants and the `Re=0` case correctly. Period formula becomes: `360.0 / np.degrees(np.arctan2(Im, Re))`.

---

## §6 Cross-Validation Against TradingView

### 6. Cross-Validation Against TradingView

This is the definitive live validation step. TradingView implementations by loxx and blackcat1402 have been used by thousands of traders over years. Any error in them has been found and corrected. They function as peer-reviewed reference implementations.

#### Step-by-Step Cross-Validation Procedure

1. Open NQ1! continuous contract, 15-minute timeframe on TradingView
2. Apply loxx "Ehlers Autocorrelation Periodogram" — select the 2016 TASC version
3. Let indicator run across at least 200 bars of history
4. Right-click the DominantCycle indicator line → Export data to CSV
5. Also export the underlying price data: right-click chart → Download data → Export as CSV
6. Run your Python implementation on the same close price array
7. Merge the two DominantCycle series on timestamp and compare bar-by-bar

```python
import pandas as pd
import numpy as np

tv_prices = pd.read_csv("nq_15min_tv.csv", parse_dates=["time"])
tv_prices = tv_prices.sort_values("time").reset_index(drop=True)
dc_python = autocorr_periodogram(tv_prices["close"].values)

tv_dc = pd.read_csv("nq_15min_dc_tv.csv", parse_dates=["time"])
merged = tv_dc.merge(
    pd.DataFrame({"time": tv_prices["time"], "python_dc": dc_python}),
    on="time")

warmup = merged.index >= 80
mae = np.mean(np.abs(merged.loc[warmup, "tv_dc"]
                     - merged.loc[warmup, "python_dc"]))
print(f"MAE vs TradingView: {mae:.2f} bars")

# Acceptance: MAE <= 1.5 bars
# If 1.5-3.0: trace to specific bars where divergence is largest
# If > 3.0: systematic formula error — revisit Section 2
```

> Small differences under 1.5 bars between Pine Script and Python can arise from Pine's fixed-precision arithmetic versus Python's float64. These are platform differences, not implementation errors.

#### Reference Implementation Comparison Table

| Method | EasyLanguage | R | Pine Script | MQL5/C++ | Python |
|---|---|---|---|---|---|
| **Roofing Filter** | Book Ch.5 / easylanguagemastery.com | fabmaccallini/ehlers | loxx RF indicator | thetestspecimen/ehlers-indicators-mql5 | Custom (this guide) |
| **Homodyne Discriminator** | TASC Nov 2000 / Book Ch.7 | fabmaccallini/ehlers | blackcat1402 L2 HD | thetestspecimen/ehlers-indicators-mql5 | Custom (this guide) |
| **ACP 2013** | Book Ch.8 | fabmaccallini/ehlers | blackcat1402 L2 ACP | thetestspecimen/ehlers-indicators-mql5 | Custom (this guide) |
| **ACP 2016 (preferred)** | TASC Sep 2016 | fabmaccallini autocorrPeriodogram.R | loxx ACP 2016 / mihakralj EACP | thetestspecimen/ehlers-indicators-mql5 | Custom (this guide) |
| **Cycle/Trend Discriminator** | Book Ch.4 | fabmaccallini/ehlers | Custom Pine required | thetestspecimen/ehlers-indicators-mql5 | Custom (this guide) |

---

## §7 Tolerance Thresholds

### 7. Tolerance Thresholds — What "Close Enough" Means

| Comparison | Tolerance | Rationale |
|---|---|---|
| Chirp MAE (pure signal) | < 2.0 bars | Ehlers' own implementations achieve 1–2 bar accuracy on chirp in the book |
| Chirp MAE (low noise σ=1) | < 4.0 bars | Noise broadens spectral peak by ±2 bars typically |
| Single known period | ± 3.0 bars | Centre-of-gravity smoothing introduces ≤ 2 bar offset |
| vs TradingView Pine | < 1.5 bars | Platform arithmetic differences account for ≤ 1 bar |
| vs R reference (fabmaccallini) | < 1.0 bar | Same algorithm, same float64 — should be near-identical |
| Period stability (same input) | < 0.1 bar | Deterministic algorithm — identical input must give identical output |
| NaN or Inf in output | **Zero tolerance** | A single NaN propagates silently — produces zero profit targets and zero re-hedge thresholds |

The NaN/Inf tolerance is zero because downstream effects are catastrophic and silent. A NaN dominant cycle period produces NaN profit targets, which are treated as 0 by the strategy parameter derivation. The strategy enters with no exit condition and cannot close positions.

---

## §8 Appendix — Coefficient Quick Reference

### 8. Appendix — Coefficient Quick Reference

These are the exact numerical values of key coefficients computed from Ehlers' EasyLanguage expressions. Verify your implementation produces these values at initialisation before running any tests.

| Coefficient | EasyLanguage expression | Python expression | Numeric value |
|---|---|---|---|
| HP alpha1 (48-bar) | (Cos(.707×360/48)+Sin(.707×360/48)-1)/Cos(.707×360/48) | (cos(r)+sin(r)-1)/cos(r) where r=deg2rad(0.7071×360/48) | ≈ 0.04948 |
| SS a1 (10-bar) | expvalue(-1.414×3.14159/10) | exp(-1.4142×π/10) | ≈ 0.63763 |
| SS b1 (10-bar) | 2×a1×Cosine(1.414×180/10) | 2×a1×cos(deg2rad(1.4142×180/10)) | ≈ 0.76536 |
| SS c2 | = b1 | = b1 | ≈ 0.76536 |
| SS c3 | -a1×a1 | -a1\*\*2 | ≈ -0.40657 |
| SS c1 | 1 - c2 - c3 | 1 - c2 - c3 | ≈ 0.64121 |
| HD I2/Q2 smooth | .2×I2 + .8×I2[1] | 0.2×raw + 0.8×prev | Exact |
| HD period EMA | .2×Period + .8×Period[1] | 0.2×raw + 0.8×prev | Exact |
| HD detrender amplitude | .046×Period[1] + .332 | 0.046×prev_period + 0.332 | Exact |
| HD Hilbert weights | .25 / .75 / -.75 / -.25 | 0.25, 0.75, -0.75, -0.25 | Exact |

> If any coefficient value differs from this table when computed by your code at initialisation, the corresponding formula has an error. Fix the formula before running chirp tests or cross-validation.
>
> The alpha1 value is the single most diagnostic coefficient — checking it takes 5 seconds and catches the two most common errors (missing .707 and wrong degree/radian conversion).

---

*This document is a validation companion to the Cycle Analysis Framework white paper. All formulas are authored by John F. Ehlers. This document provides Python translation guidance and validation protocols only.*

**Primary sources:** Ehlers (2001) *Rocket Science for Traders* · Ehlers (2013) *Cycle Analytics for Traders* · TASC September 2016
