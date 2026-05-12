# Pass 6: Adversarial Review

Simulate a skeptical but fair reviewer who challenges claims, evidence, and reasoning. Produces inline annotations with severity ratings and a concrete revision plan.

## Purpose

Passes 1-5 verify from the author's perspective. Pass 6 flips the frame: what would a hostile-but-competent critic say? This catches claims that are technically correct but overstate the evidence, reasoning that holds locally but breaks under scrutiny, and conclusions that outrun the experiments.

## When to Run

- Documents with strong claims that will face public scrutiny
- Research briefs, technical reports, whitepapers
- Any document the author wants stress-tested before publication
- After all other passes are clean (Pass 6 assumes the document is structurally sound and factually checked)

## Process

1. **Read the full document** with the mindset of a skeptical expert in the field
2. **Identify challenges** — keep looking after finding the first problem; do not stop early
3. **Classify severity** for each finding (FATAL / MAJOR / MINOR)
4. **Write inline annotations** quoting the exact passage being challenged
5. **Produce structured review** with strengths, weaknesses, questions
6. **Write revision plan** — prioritized, concrete actions to address each weakness

## Severity Taxonomy

| Severity | Meaning | Effect on Publication |
|----------|---------|----------------------|
| `FATAL` | Claim is unsupported, contradicted by cited evidence, or fundamentally misleading | **BLOCKER** — must fix before publication |
| `MAJOR` | Significant weakness: missing context, overstated confidence, weak evidence for a central claim | Should fix; note in Open Questions if not fixed |
| `MINOR` | Polish issue: imprecise wording, missing hedge, incomplete attribution | Fix if convenient; acceptable to ship with |

## What to Look For

- Claims that outrun the evidence ("we achieve state-of-the-art" when Table 3 says otherwise)
- Conclusions using stronger language than the data warrants
- Missing or weak comparisons/baselines
- Single-source critical claims (one source supporting a central conclusion)
- "Verified" or "confirmed" language without showing what check was performed
- Quantitative claims without methodology or reproducibility information
- Figures, tables, or benchmarks that appear without provenance
- Notation drift or inconsistent terminology
- Sections that appear to survive from earlier drafts without current support
- Hedges that were sharpened for impact ("X may contribute" becoming "X causes")

## Output Format

### Part 1: Structured Review

```markdown
## Summary
1-2 paragraph summary of the document's core argument and approach.

## Strengths
- [S1] [specific strength tied to evidence in the document]
- [S2] ...

## Weaknesses
- [W1] **FATAL:** [specific issue with passage reference]
- [W2] **MAJOR:** [specific issue]
- [W3] **MINOR:** [specific issue]

## Questions for Author
- [Q1] [genuine question that affects interpretation]

## Verdict
Overall assessment. Is this ready for its intended audience?
FATAL issues found: [count]
MAJOR issues found: [count]
MINOR issues found: [count]

## Revision Plan
Prioritized actions:
1. [Fix W1: specific instruction]
2. [Fix W2: specific instruction]
3. [Optional: Fix W3]
```

### Part 2: Inline Annotations

Quote the exact passage and annotate:

```markdown
## Inline Annotations

> "We achieve state-of-the-art results on all benchmarks"
**[W1] FATAL:** Table 3 shows the method underperforms on 2 of 5 benchmarks. Revise to accurately reflect results.

> "Our approach is novel in combining X with Y"
**[W3] MINOR:** Z et al. (2024) combined X and Y in a different domain. Acknowledge and clarify the distinction.

> "We use a learning rate of 1e-4"
**[Q1]:** Was this tuned? What range was searched? Matters for reproducibility.
```

## Rules

1. Every weakness must reference a specific passage or section — no vague complaints
2. Inline annotations must quote the exact text being challenged
3. Do not praise vaguely — every positive claim in Strengths should cite specific evidence
4. A citation attached to a claim is NOT sufficient if the source doesn't support the exact wording
5. Keep looking after finding the first major problem — exhaustive scrutiny is the point
6. Preserve uncertainty — if the document might be acceptable depending on audience, say so
7. Do not conflate "I disagree" with "this is wrong" — distinguish contested from incorrect
8. The revision plan must be concrete enough that the author can act on it without further guidance

## Go/No-Go

- `GO`: 0 FATAL findings
- `GO-WITH-NOTES`: 0 FATAL, but ≥1 MAJOR that the author acknowledges
- `NO-GO`: ≥1 FATAL finding (automatic blocker)

## Output

```
PASS 6 RESULT: PASS / FAIL
FATAL: [count]
MAJOR: [count]
MINOR: [count]
Questions: [count]
Verdict: GO / GO-WITH-NOTES / NO-GO
Blockers: [list of FATAL findings, or "none"]
```
