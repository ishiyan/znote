# Pass 3b: Evidence Provenance

Verify that every factual claim in the document has a traceable source. Runs after Pass 3 (Technical Claims) and before Pass 4 (Style).

## Purpose

Pass 3 classifies claims into quality buckets. This pass asks a different question: **can every claim be traced to a specific, verifiable source?** A claim can be technically correct (Pass 3: `simplified-correct`) but still lack provenance — which means it can't be independently verified by a reader.

## When to Run

- **Always** for research briefs, technical articles citing papers, and any document with quantitative claims
- **Optional** for opinion essays, personal narratives, and how-to guides where claims are experiential
- Skip for fiction, poetry, and purely subjective pieces

## Process

1. **Extract sourced claims**: Identify every factual assertion that is not common knowledge, opinion, or the author's original observation
2. **Check provenance**: For each claim, determine whether a traceable source exists in the document (inline citation, footnote, link, or explicit attribution)
3. **Classify provenance status** using the 5-level taxonomy below
4. **Verify links**: For claims with URLs — check that the URL resolves and its content supports the specific claim attached to it
5. **Build provenance ledger**: Output a per-claim record

## Provenance Taxonomy

| Status | Meaning | Action |
|--------|---------|--------|
| `verified` | Source URL/citation present AND confirmed to support the specific claim | Keep as-is |
| `attributed` | Author/Year/Title cited but URL not checkable (book, paywall) | Keep — note as non-verifiable externally |
| `unverified` | Claim is plausible but no source provided | Flag — author must add source or downgrade to opinion |
| `inferred` | Claim derived from combining multiple sources (none states it directly) | Flag — author must acknowledge inference explicitly |
| `blocked` | Source URL is dead, redirects elsewhere, or doesn't support the claim | **BLOCKER — source must be replaced or claim removed** |

## Per-Claim Record

```
CLAIM [n]: "[factual assertion]"
PROVENANCE: verified | attributed | unverified | inferred | blocked
SOURCE: [URL, citation, or "none"]
EVIDENCE: [what in the source supports this specific claim]
NOTE: [if blocked — what failed; if inferred — from what sources]
```

## Link Verification Protocol

For each URL cited as a source:

- **Live + supports claim**: status = `verified`
- **Live + supports different claim**: status = `blocked` (citation mismatch)
- **Dead / 404**: search for archived version or alternative URL. If found, suggest replacement. If not, status = `blocked`
- **Redirects to unrelated content**: status = `blocked`
- **Paywall / login-gated**: status = `attributed` (note: not independently verifiable without access)

## Quantitative Claims Audit

Before completing this pass, scan specifically for:
- Numeric scores or percentages
- Benchmark results and comparison tables
- Dataset sizes or experimental parameters
- "X% improvement" or "Y times faster" claims
- Figure/chart data points

Each must map to a source. Unsourced quantitative claims are automatic `unverified` flags.

## Go/No-Go

- `GO`: 0 claims `blocked`, ≤2 claims `unverified`
- `GO-WITH-NOTES`: 0 claims `blocked`, 3+ claims `unverified` (author acknowledges and accepts)
- `NO-GO`: ≥1 claim `blocked` (automatic blocker — dead source or citation mismatch)

## Rules

1. "URL or it didn't happen" — a claim without a traceable source is `unverified`, period
2. A citation is valid only if the source supports the **specific** claim, not merely the general topic
3. Never fabricate a source to fill a gap. `unverified` is always an honest output
4. Author's own observations/experiences ("I found that...") don't need external provenance — they're experiential claims, not factual claims
5. Common knowledge doesn't need provenance (e.g., "water boils at 100C at sea level")
6. When multiple claims cite the same source, verify the source supports ALL of them — not just the first one checked

## Output

```
PASS 3b RESULT: PASS / FAIL
Claims audited: [count]
verified: [count]
attributed: [count]
unverified: [count]
inferred: [count]
blocked: [count]
Dead links found: [count]
Citation mismatches: [count]
Verdict: GO / GO-WITH-NOTES / NO-GO
Blockers: [list of blocked claims, or "none"]
Warnings: [list of unverified/inferred, or "none"]
```
