# Schaff Trend Cycle (STC) — Critical & Academic Assessment

*An even-handed evaluation of Doug Schaff's Schaff Trend Cycle: is it a genuine improvement on the MACD, or a normalized repackaging that inherits MACD's limitations and adds new ones? Every cited paper was located and DOI-verified in the Crossref API; the returned title was confirmed to match before citation. No backtests are invented and no performance numbers are fabricated. Where a claim is structural/logical rather than empirical, it is labelled as such.*

---

## What the STC actually is (so the critique is fair)

The STC is a deterministic transform, not a new data source. Construction (per Schaff's published description):

1. Compute a **MACD** line (difference of two EMAs, conventionally 23 and 50 in Schaff's FX setting).
2. Run a **stochastic %K** normalization over the MACD line across a cycle look-back (commonly 10), mapping it into 0–100.
3. **Double-smooth** that stochastic (a second stochastic pass / EMA smoothing) to produce the final 0–100 oscillator.
4. Read it with **overbought/oversold thresholds** (commonly 25/75) and slope/turn signals.

So STC = MACD → stochastic-normalize → double-smooth → threshold. This is the same "double smoothed stochastic of a momentum series" family as Blau's and Bressert's constructions; STC's distinctive choice is feeding a **MACD** (rather than price) into the stochastic and adding a **cycle** look-back. Everything below follows from that pipeline.

---

## Direct evidence (none by name)

A search of Crossref, Semantic Scholar, and general scholarly indices returns **no peer-reviewed study of the "Schaff Trend Cycle," of Doug Schaff, or of FX Strategy's signal products, by name.** This is the expected outcome — almost no individually branded vendor indicator is studied under its trade name. State it plainly: **there is no academic validation, and no academic refutation, of the STC specifically.** Everything that follows is *by-category* inference from the literature on MACD, stochastic oscillators, moving-average rules, and technical-trading-rule statistics. This is the honest epistemic status, not a hedge. **[Confidence: High — the absence is a verifiable search result; the inferential framing is the only defensible one.]**

---

## STC vs MACD — is the "earlier, cleaner signal" a real edge?

The marketing claim is that STC turns **earlier** and **cleaner** (fewer whipsaws) than MACD. Structurally, both halves of that claim have benign mechanical explanations that do **not** require any new predictive information.

**1. "Earlier" is largely a re-scaling artifact, not new lead time.** The MACD line and the STC carry the *same underlying momentum information* — STC adds no new price input. What the stochastic-normalization step does is map the MACD's recent range onto 0–100. When MACD is near the top of its recent window, %K saturates toward 100 *before* the MACD line itself rolls over in absolute terms. The STC therefore appears to "call the turn early" — but this is a **monotonic transform of the same series reaching the edge of its recent range**, not anticipation of future prices. An equivalently fast MACD (shorter EMAs) plus a normalization would produce a similar visual lead. The apparent earliness is a property of *where the current MACD sits in its recent distribution*, which is information already in the MACD. **[Confidence: High — this follows deductively from the construction; no future data is used, but no new information is created either.]**

**2. "Cleaner" is the double-smoothing, and smoothing trades noise for lag.** The two stochastic/EMA smoothing passes suppress high-frequency reversals, which is exactly why the line looks less jagged than a raw MACD histogram. But smoothing is not free: it is a low-pass filter, and every low-pass filter that removes whipsaws also **delays genuine turns**. The STC's crispness and its claimed earliness are therefore in tension — the normalization pulls signals *earlier* in scale while the double-smoothing pushes them *later* in time. The net "lead" depends entirely on parameter choices, and there is no structural reason the chosen defaults are optimal out-of-sample. **[Confidence: High — standard signal-processing fact about causal low-pass filters.]**

**3. STC is, in effect, a faster MACD with a bounded display.** Strip the cosmetics and STC's economic content is identical to a fast MACD: it fires on momentum acceleration/deceleration. A faster MACD generates *more* signals (more noise); the stochastic+double-smooth wrapper re-imposes order on that noise. The honest description is **"a faster MACD whose output is normalized and re-smoothed for readability,"** not "a new indicator that sees turns the MACD cannot." Any genuine edge must come from MACD-type momentum itself — and that is testable in the literature (below). **[Confidence: High — structural.]**

**4. Bounded-oscillator pinning in trends — STC inherits the stochastic's worst failure.** Because STC is rescaled to 0–100 with overbought/oversold bands, it suffers the **same pinning pathology as the raw stochastic oscillator**: in a strong trend it saturates at 100 (or 0) and stays there, generating premature counter-trend "overbought/oversold" reads and repeated false reversal signals against a persistent move. MACD, being *unbounded*, does not pin — it can keep rising with the trend. So on the specific failure mode that matters most (strong, persistent trends — precisely where a "trend cycle" indicator is marketed to help), **the normalization that makes STC pretty also reintroduces the stochastic's central weakness that the unbounded MACD avoided.** This is a real structural regression, not a stylistic one. **[Confidence: High — direct consequence of bounding + thresholds.]**

**5. Over-parameterization / data-snooping exposure.** STC exposes *more* free knobs than MACD: two EMA lengths, a cycle look-back, the stochastic length(s), the smoothing factor(s), and two thresholds — roughly **6–8 tunable parameters** versus MACD's 3. Each added degree of freedom widens the space of rules that can be fit to a chosen historical window, which is exactly the condition the data-snooping literature shows inflates apparent in-sample performance while eroding out-of-sample (Sullivan-Timmermann-White 1999; Park-Irwin 2007). A good-looking STC chart with tuned parameters is therefore *weaker* evidence of an edge than a good-looking 3-parameter MACD chart, all else equal. **[Confidence: High for the directional claim; the magnitude is unquantified absent a registered test.]**

---

## By-category academic evidence (DOIs verified in Crossref)

### A. MACD specifically — the indicator STC is built from

- **Chong, T.T.-L. & Ng, W.-K. (2008), "Technical analysis and the London stock exchange: testing the MACD and RSI rules using the FT30," *Applied Economics Letters* 15(14):1111–1114.** https://doi.org/10.1080/13504850600993598 — One of the few peer-reviewed tests of the **MACD by name**. Found the MACD(12,26,9) and RSI rules *did* generate returns on the FT30 over 1976–2002. Note the caveats that bound how much this helps STC: it is a single index, a specific period, *without* the full multiple-testing correction of the reality-check studies, and it tests classic MACD — not a normalized/smoothed derivative. It is the **most direct pro-momentum data point** for STC's engine, and it is offered as such. **[Confidence: Medium — real and on-point, but narrow and not snooping-adjusted.]**

### B. FX — Schaff's home market — MACD/oscillator-class rules under proper controls

- **Qi, M. & Wu, Y. (2006), "Technical Trading-Rule Profitability, Data Snooping, and Reality Check: Evidence from the Foreign Exchange Market," *Journal of Money, Credit and Banking* 38(8):2135–2158.** https://doi.org/10.1353/mcb.2007.0006 — Applies White's Reality Check across a large universe of rules on seven currencies. Finds some rules were profitable but that **data-snooping-robust significance is far weaker than naïve testing suggests.** Directly relevant: STC is an FX-born oscillator with *more* parameters than the rules tested here, so its snooping exposure is greater, not less. **[Confidence: High for the FX snooping caution.]**

- **Olson, D. (2004), "Have trading rule profits in the currency markets declined over time?," *Journal of Banking & Finance* 28(1):85–105.** https://doi.org/10.1016/s0378-4266(02)00399-0 — Moving-average-type rule profits in FX **declined to near zero by the 1990s.** Since STC is a moving-average/momentum derivative born in late-1990s FX, this is the most damaging period-specific finding: the very market and era of STC's origin is where mechanical rule edges were already decaying. **[Confidence: High — direct market and period match.]**

- **Neely, C.J. & Weller, P.A. (2003), "Intraday technical trading in the foreign exchange market," *Journal of International Money and Finance* 22(2):223–237.** https://doi.org/10.1016/s0261-5606(02)00101-8 — Intraday FX technical rules show **little profitability after realistic costs.** Relevant because STC is heavily marketed for shorter-horizon FX timing, where the cost drag is exactly what this study flags. **[Confidence: Medium-High.]**

### C. Technical-rule profitability & data-snooping — the general statistical frame

- **Park, C.-H. & Irwin, S.H. (2007), "What Do We Know About the Profitability of Technical Analysis?," *Journal of Economic Surveys* 21(4):786–826.** https://doi.org/10.1111/j.1467-6419.2007.00519.x — The definitive survey: of 95 modern studies, 56 positive, 20 negative, 19 mixed, but positives are "**heavily compromised by data-snooping, ex-post rule selection, and transaction costs**," with profitability declining over time. The single best even-handed anchor. **[High.]**

- **Sullivan, R., Timmermann, A. & White, H. (1999), "Data-Snooping, Technical Trading Rule Performance, and the Bootstrap," *Journal of Finance* 54(5):1647–1691.** https://doi.org/10.1111/0022-1082.00163 — Across ~7,800 rules, once you account for the universe searched, the best rule's apparent significance largely **evaporates** and fails out-of-sample. The methodological heart of the case against any multi-parameter indicator (like STC) selected after seeing the data. **[High.]**

- **Brock, W., Lakonishok, J. & LeBaron, B. (1992), "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns," *Journal of Finance* 47(5):1731–1764.** https://doi.org/10.1111/j.1540-6261.1992.tb04681.x — The landmark **positive** result (MA and range-break rules on the Dow, 1897–1986). Included as the strongest pro-TA evidence; but it tested a small fixed rule set and ignored transaction costs. **[High as cited.]**

- **Hsu, P.-H. & Kuan, C.-M. (2005), "Reexamining the Profitability of Technical Analysis with Data Snooping Checks," *Journal of Financial Econometrics* 3(4):606–628.** https://doi.org/10.1093/jjfinec/nbi026 — Stronger stepwise snooping tests: *some* genuine profitability in younger/less-efficient markets, little in mature large-caps. A calibrated, non-nihilistic reading. **[High.]**

- **Marshall, B.R., Cahan, R.H. & Cahan, J.M. (2008), "Can commodity futures be profitably traded with quantitative market timing strategies?," *Journal of Banking & Finance* 32(9):1810–1819.** https://doi.org/10.1016/j.jbankfin.2007.12.011 — Thousands of timing rules on 15 commodity futures: **no profitability survives the bootstrap reality check.** Close to STC's futures/FX timing domain; negative. **[High.]**

### D. Some structure exists — the steelman's empirical footing

- **Lo, A.W., Mamaysky, H. & Wang, J. (2000), "Foundations of Technical Analysis...," *Journal of Finance* 55(4):1705–1765.** https://doi.org/10.1111/0022-1082.00265 — Chart patterns carry *modest incremental information*; but "information" ≠ "tradable profit." **[Medium.]**

- **Lo, A.W. & MacKinlay, A.C. (1988), "Stock Market Prices Do Not Follow Random Walks...," *Review of Financial Studies* 1(1):41–66.** https://doi.org/10.1093/rfs/1.1.41 — Documents **short-horizon autocorrelation/momentum** — the one structure a momentum oscillator like MACD/STC could in principle exploit. But it is short-horizon serial correlation, not a clean exploitable cycle. **[Medium.]**

### E. The arbitrage paradox

- **Timmermann, A. & Granger, C.W.J. (2004), "Efficient market hypothesis and forecasting," *International Journal of Forecasting* 20(1):15–27.** https://doi.org/10.1016/s0169-2070(03)00012-8 — Any *publicly known*, simple rule tends to be arbitraged away. A widely published, freely re-implemented oscillator (STC is in most charting platforms) is *a priori* unlikely to retain an edge if it ever had one. **[High as a structural prior.]**

---

## Statistical / structural critiques (summary)

1. **No new information.** STC is a deterministic function of MACD, which is a deterministic function of price. It cannot contain information the MACD lacks. Its value is purely *presentational* (bounding + smoothing). **[High.]**
2. **Bounded-oscillator pinning.** The 0–100 rescaling reintroduces the stochastic's trend-pinning failure that the unbounded MACD avoids — a structural regression in exactly the trending regimes the tool targets. **[High.]**
3. **Smoothing ↔ lag tradeoff.** "Cleaner" comes from low-pass filtering, which delays true turns; the "earlier" and "cleaner" claims pull in opposite directions. **[High.]**
4. **Parameter inflation.** ~6–8 free parameters vs MACD's 3 → larger data-snooping surface (Sullivan-Timmermann-White; Park-Irwin). **[High directionally.]**
5. **No look-ahead, but no validation.** Unlike centered-MA cycle methods, STC is causal (no future data) — so it is *not* guilty of the hindsight artifact. Its problem is over-fitting/selection, not look-ahead. This distinction is made in STC's favor. **[High.]**

---

## Steelman — what holds up

1. **Readability and consistent thresholds.** A bounded 0–100 line with fixed 25/75 bands is genuinely easier to read, alert, and systematize than an unbounded MACD whose scale drifts with price and volatility. Normalization aids **cross-market comparability** (an STC of 80 means the same thing on EUR/USD and on gold; a MACD of 0.0012 does not). This is a real, if modest, ergonomic benefit. **[Confidence: High — it is a definitional property.]**
2. **Noise reduction is real where whipsaw is the enemy.** In choppy, range-bound regimes the double-smoothing genuinely cuts the false-signal count relative to a raw MACD histogram. **[Medium — true but regime-dependent and lag-paying.]**
3. **Momentum has *some* empirical footing.** STC's engine (MACD momentum) is the TA family with the least-bad evidence: short-horizon autocorrelation (Lo-MacKinlay 1988), modest pattern information (Lo-Mamaysky-Wang 2000), and at least one direct positive MACD test (Chong-Ng 2008). So STC is built on the *better* end of TA, not the discredited fixed-cycle end. **[Medium.]**
4. **As an attention/gating heuristic, not a standalone edge.** Using STC to *flag* momentum exhaustion and requiring independent confirmation + risk management is a defensible *process*, even if the indicator itself adds no alpha over a fast MACD. The discipline benefit is real and orthogonal to signal validity. **[Medium-High.]**

---

## Marketing-vs-substance caveats

- **Vendor incentive.** Schaff and FX Strategy commercialize education and signals around the STC. Performance claims from the seller of a method are not independent evidence — standard conflict-of-interest flag, stated without ad hominem. **[High.]**
- **Selection bias in showcased charts.** Promotional material self-selects the trades where STC nailed the turn; pinned-in-a-trend periods and late-after-smoothing turns are underrepresented. This is exactly the anecdote/selection bias the snooping literature formalizes. **[High.]**
- **"Earlier and smoother" is a chart-aesthetics claim, not a P&L claim.** Looking better in hindsight is not the same as net-of-cost out-of-sample profit. No located evidence converts STC's visual appeal into validated returns. **[High.]**
- **The Timmermann-Granger paradox.** STC is built into nearly every charting platform and freely re-implemented. A simple, public, widely-used rule is, by this argument, the *least* likely to retain an edge. Persistence of paid STC education is at least as consistent with selling *discipline and clarity* as with selling alpha. **[High as a prior.]**

---

## Confidence & gaps

| Claim | Evidence basis | Confidence |
|---|---|---|
| No peer-reviewed study addresses STC by name | Search result | High |
| STC adds no information beyond MACD (deterministic transform) | Structural/deductive | High |
| Bounded rescaling reintroduces stochastic trend-pinning MACD avoids | Structural | High |
| "Cleaner" = low-pass smoothing = lag tradeoff | Signal-processing fact | High |
| More parameters → greater data-snooping exposure | Sullivan-Timmermann-White; Park-Irwin | High |
| FX/era of STC's birth is where rule profits had already decayed | Olson 2004; Qi-Wu 2006 | High |
| Commodity/FX timing rules don't survive reality-check | Marshall et al.; Qi-Wu; Neely-Weller | High |
| Classic MACD showed some profitability on at least one index | Chong-Ng 2008 | Medium |
| Momentum has modest genuine structure | Lo-MacKinlay; Lo-Mamaysky-Wang | Medium |
| STC is causal — not guilty of centered-MA look-ahead | Structural (in STC's favor) | High |
| Readability/normalization is a real ergonomic benefit | Definitional | High |

**Gaps / honest limits.** (1) No direct empirical test of STC exists, so every profitability conclusion is by-category inference, not refutation. (2) Chong-Ng tests *classic* MACD, not STC's normalized-smoothed derivative, and is not snooping-adjusted — it is suggestive, not decisive. (3) The strongest pro-TA results (Brock 1992; Lo-Mamaysky-Wang 2000) are included to avoid skeptic cherry-picking. (4) Absence of academic study is absence of evidence, not proof of failure — many tradeable methods are unstudied. The fair verdict is **"unvalidated and structurally redundant, not debunked."**

---

## Sources (all DOI-verified in Crossref; titles confirmed to match)

- Chong & Ng 2008 — https://doi.org/10.1080/13504850600993598
- Qi & Wu 2006 — https://doi.org/10.1353/mcb.2007.0006
- Olson 2004 — https://doi.org/10.1016/s0378-4266(02)00399-0
- Neely & Weller 2003 — https://doi.org/10.1016/s0261-5606(02)00101-8
- Park & Irwin 2007 — https://doi.org/10.1111/j.1467-6419.2007.00519.x
- Sullivan, Timmermann & White 1999 — https://doi.org/10.1111/0022-1082.00163
- Brock, Lakonishok & LeBaron 1992 — https://doi.org/10.1111/j.1540-6261.1992.tb04681.x
- Hsu & Kuan 2005 — https://doi.org/10.1093/jjfinec/nbi026
- Marshall, Cahan & Cahan 2008 — https://doi.org/10.1016/j.jbankfin.2007.12.011
- Lo, Mamaysky & Wang 2000 — https://doi.org/10.1111/0022-1082.00265
- Lo & MacKinlay 1988 — https://doi.org/10.1093/rfs/1.1.41
- Timmermann & Granger 2004 — https://doi.org/10.1016/s0169-2070(03)00012-8

---

**Verdict (one line):** The Schaff Trend Cycle is a causal, well-engineered *cosmetic* reformatting of a fast MACD — easier to read and threshold, but adding no information its MACD core lacks, reintroducing the stochastic's trend-pinning weakness, and carrying more parameters and thus more data-snooping exposure; with no study validating it by name and the FX/timing literature on its underlying rule class running mostly negative after costs and snooping adjustment, it is best treated as **unproven and structurally redundant rather than debunked**, whose real value is presentational discipline, not demonstrated alpha.
