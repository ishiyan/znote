# Spine Extraction

Extract the 5-7 load-bearing claims from a blog post or essay into a structured spine that downstream platform-rewrite files consume.

## When to Use

Before creating social media posts from a blog article. The spine is the intermediate representation that all platform rewrites consume.

## Workflow

1. Read the post end-to-end
2. Identify the thesis (usually opening confession + first pivot sentence)
3. Extract 5-7 load-bearing claims IN ORDER
4. Tag each claim: evidence type, section, translatability score
5. Extract the closing maxim verbatim
6. Extract 3 candidate hook sentences (from the post itself, not paraphrases)
7. Output the spine

## Output Schema

```json
{
  "thesis": "one sentence, verbatim or lightly-compressed from the post",
  "claims": [
    {
      "text": "verbatim from post",
      "evidence_type": "confession|claim|paper|analogy|formula|maxim|data",
      "section": "opener|pivot|body|closer",
      "translatability": 1-5
    }
  ],
  "closing_maxim": "verbatim from post, usually bolded or the final insight",
  "best_hook_candidates": [
    "verbatim sentence 1",
    "verbatim sentence 2",
    "verbatim sentence 3"
  ]
}
```

## Evidence Types

| Type | Description | Example |
|------|-------------|---------|
| confession | Personal admission or failure | "I spent four months building something nobody needed." |
| claim | Assertion requiring support | "Most prompt engineering advice mistakes the unit of analysis." |
| paper | Citation of research | "Chen et al. (2024) found multi-agent outperforms by 40%." |
| analogy | Comparison to familiar domain | "It's like optimizing the menu when the kitchen is on fire." |
| formula | Mathematical or quantitative | "Brier score: (predicted - actual)^2" |
| maxim | Pithy truth or principle | "I have not tried this. Not once." |
| data | Original data point or metric | "Our p99 dropped from 340ms to 45ms." |

## Translatability Score

How well does this claim work WITHOUT the full post's context?

| Score | Meaning | Platform use |
|-------|---------|-------------|
| 5 | Works standalone on any platform | Use in short X thread, LinkedIn hook |
| 4 | Works with minimal setup (1 sentence) | Use in medium X thread, LinkedIn body |
| 3 | Needs 2-3 sentences of context | Use in long X thread, Substack Note |
| 2 | Needs significant essay context | Only in full-length rewrites |
| 1 | Only makes sense in the full essay | Skip for all platform rewrites |

## Guardrails

1. **Pull verbatim sentences.** Paraphrasing is the slop door. The writer's voice is in the exact phrasing.
2. **Never invent a claim not in the post.**
3. **Exactly 5-7 claims.** Fewer under-represents; more overwhelms downstream rewrites.
4. **Preserve paper attributions intact.** Platform rewrites decide per-post trade-offs later.
5. **closing_maxim is verbatim** — it's what gets bolded in the Substack Note.
6. **Translatability is the writer's dial.** Use it honestly; don't inflate everything to 5.

## Example

**Input** (post about zero-lag moving averages, abridged):

> Standard moving averages are always late. By the time a 20-period EMA confirms a trend change, you've already missed 60% of the move.
>
> [methodology section on Ehlers' approach...]
>
> The math works. But the overshoot on reversals will kill you in choppy markets.
>
> **There is no free lunch in filtering. You trade lag for overshoot, always.**

**Output**:
```json
{
  "thesis": "Standard moving averages are always late, and eliminating that lag comes with unavoidable overshoot costs.",
  "claims": [
    {"text": "By the time a 20-period EMA confirms a trend change, you've already missed 60% of the move.", "evidence_type": "data", "section": "opener", "translatability": 5},
    {"text": "Ehlers' approach uses the difference between the current price and the EMA as a correction term.", "evidence_type": "formula", "section": "body", "translatability": 3},
    {"text": "The math works. But the overshoot on reversals will kill you in choppy markets.", "evidence_type": "claim", "section": "body", "translatability": 5},
    {"text": "There is no free lunch in filtering. You trade lag for overshoot, always.", "evidence_type": "maxim", "section": "closer", "translatability": 5}
  ],
  "closing_maxim": "There is no free lunch in filtering. You trade lag for overshoot, always.",
  "best_hook_candidates": [
    "Standard moving averages are always late.",
    "By the time a 20-period EMA confirms a trend change, you've already missed 60% of the move.",
    "The math works. But the overshoot on reversals will kill you in choppy markets."
  ]
}
```
