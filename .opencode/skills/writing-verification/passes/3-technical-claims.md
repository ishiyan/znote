# Pass 3: Technical Claims

Verify factual accuracy of technical claims using the 5-bucket taxonomy.

## Five-Bucket Taxonomy

| Bucket | Meaning | Action |
|--------|---------|--------|
| `simplified-correct` | Strips detail but claim still holds | Keep as-is |
| `simplified-boundary` | Holds in common case, breaks at edge | Note the boundary; suggest folding it in |
| `wrong` | Flat factual error | **BLOCKER — must fix before publish** |
| `contested` | Field actively debates this; asserting as settled is premature | Add hedge or acknowledge debate |
| `overclaim` | True in narrow scope, asserted broadly | Scope the claim appropriately |

See [../reference/claim-buckets.md](../reference/claim-buckets.md) for detailed definitions and examples.

## Process

1. **Extract atomic claims**: Break compound sentences into individual testable assertions
2. **Classify each claim** into one of 5 buckets
3. **Cross-reference**: For non-trivial claims, identify a primary source (paper, RFC, textbook, official docs) — never a blog post or social media thread
4. **Flag boundary breaks** as teaching opportunities (can be folded into the text)

## Per-Claim Record

```
CLAIM [n]: "[atomic assertion]"
BUCKET: simplified-correct | simplified-boundary | wrong | contested | overclaim
SOURCE: [primary reference, or "could-not-verify"]
NOTE: [if boundary — what breaks; if contested — both sides; if overclaim — correct scope]
```

## Go/No-Go

- `GO`: 0 claims in `wrong` bucket
- `GO-WITH-HEDGES`: >=1 `contested` or `overclaim` (flag for author, does not block)
- `NO-GO`: >=1 `wrong` claim (automatic blocker)

## Rules

1. Never mark a simplification as wrong — simplified-correct is a valid and expected state
2. Never cite blogs/tweets/Medium as primary sources
3. "Could-not-verify" is a valid output — never fabricate a source
4. If the author has marked a claim as intentionally contrarian, reclassify from `wrong` to `contested` or `overclaim`

## Output

```
PASS 3 RESULT: PASS / FAIL
Claims extracted: [count]
simplified-correct: [count]
simplified-boundary: [count]
wrong: [count]
contested: [count]
overclaim: [count]
Verdict: GO / GO-WITH-HEDGES / NO-GO
Blockers: [list of wrong claims, or "none"]
Warnings: [list of contested/overclaim, or "none"]
```
