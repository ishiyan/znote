# Agent Brief T3 — Doug Schaff / STC: Critical & Academic Assessment

**Output file:** `outputs/.drafts/doug-schaff-research-critical.md`
**Role:** Even-handed critical evaluation of the Schaff Trend Cycle. Write findings to disk; return a short summary only.

## Subject
The **Schaff Trend Cycle (STC)** = MACD passed through a cyclic stochastic
double-smoothing, marketed as a faster, smoother, lower-whipsaw trend/cycle
oscillator. Created by Doug Schaff (late 1990s, forex). Question: does it hold up,
or is it a repackaging of MACD with the same limitations plus extra parameters?

## Tasks
1. **Direct evidence.** Search Crossref / Semantic Scholar / Google Scholar for any
   peer-reviewed study of the "Schaff Trend Cycle" by name. Almost certainly none
   exists — state that plainly. Then assess STC **by category**.
2. **STC vs MACD — substance check.** Analyze structurally (no invented backtests):
   - STC normalizes MACD into a bounded 0–100 oscillator via stochastic transform,
     producing earlier, cleaner-looking turns. The cost: the stochastic
     transform + smoothing add parameters and can introduce **look-ahead-free but
     curve-fit** behavior; bounded oscillators clip in strong trends (same
     overbought/oversold pinning that afflicts stochastics).
   - Is the "earlier signal" a genuine edge or just a faster (noisier) MACD whose
     apparent crispness is a smoothing/normalization artifact? Reason it through.
   - Extra free parameters (cycle length, two MACD lengths, smoothing factor,
     thresholds) → over-parameterization / data-snooping exposure.
3. **By-category academic evidence.** Reuse the Bressert critical set (already in
   `outputs/walter-bressert.md` / `outputs/.drafts/walter-bressert-research-critical.md`),
   verifying DOIs apply here too:
   - Technical-rule profitability & data-snooping: Park & Irwin 2007
     (10.1111/j.1467-6419.2007.00519.x); Sullivan, Timmermann & White 1999
     (10.1111/0022-1082.00163); Brock et al. 1992 (10.1111/j.1540-6261.1992.tb04681.x);
     Hsu & Kuan 2005 (10.1093/jjfinec/nbi026).
   - Commodity/FX timing: Marshall et al. 2008 (10.1016/j.jbankfin.2007.12.011).
   - Some structure exists: Lo, Mamaysky & Wang 2000 (10.1111/0022-1082.00265);
     Lo & MacKinlay 1988 (10.1093/rfs/1.1.41).
   - Search additionally for any study of **MACD** or **stochastic oscillator**
     profitability specifically (FX especially), since STC is built from them.
   Verify each DOI you cite via the Crossref API (`https://api.crossref.org/works/<doi>`)
   and confirm the title matches.
4. **Steelman — what holds up.** Bounded oscillator is easy to read and threshold;
   normalization aids cross-market comparability; combining trend (MACD) with a
   cycle/stochastic gate is a reasonable *attention* heuristic; works best paired
   with risk management (independent of signal validity).
5. **Marketing-vs-substance caveats.** Vendor/educational incentive (FX Strategy
   sells education/signals); selection bias in showcased charts; the
   Timmermann-Granger (2004, 10.1016/s0169-2070(03)00012-8) paradox — a widely
   sold, simple rule is arbitraged away if it ever worked.

## Method
- All cited papers must be real and DOI-verified via Crossref API. Do not invent
  studies or numbers. Distinguish structural/logical critique from empirical claims.
- Tag confidence on each conclusion (High/Medium/Low) with basis.

## Output format
Markdown to output file: `## Direct evidence (none by name)`, `## STC vs MACD`,
`## By-category academic evidence` (with DOIs), `## Statistical/structural
critiques`, `## Steelman`, `## Marketing caveats`, `## Confidence & gaps`,
`## Sources` (DOIs inline). End with a one-line defensible verdict.
