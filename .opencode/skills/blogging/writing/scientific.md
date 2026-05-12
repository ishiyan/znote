# Scientific Blog Writing

For research-backed articles targeting technically literate audiences. Bridges academic rigor with blog accessibility.

## When to Use

- Explaining a published paper or set of papers to a broader audience
- Writing up original research, experiments, or data analysis
- Methodology-focused posts (how we measured, why we chose this approach)
- Review/survey posts synthesizing multiple papers on a topic

## Voice

The voice is "researcher explaining at a seminar" — precise but not stiff. You can be enthusiastic about findings without being breathless.

- Use hedging calibration: match confidence to evidence strength
  - Strong evidence: "X causes Y" / "the data show"
  - Moderate: "X appears to cause Y" / "the data suggest"
  - Preliminary: "X may contribute to Y" / "early results indicate"
- Cite inline: (Author et al., Year) or "Smith and colleagues found..."
- Define technical terms on first use, even if your audience is technical
- Distinguish your claims from cited claims clearly

---

## Structure

### Option A: Single-Paper Explainer

```markdown
# [Paper's main finding in plain language]

[1-2 sentence hook: why this matters to the reader]

> **Key Takeaways**
> - [Finding 1 in plain language]
> - [Finding 2]
> - [Practical implication]

## The Problem [Paper's name] Addresses
## What They Did (Methodology)
## What They Found (Results)
## Why This Matters (Implications)
## Limitations and Open Questions
## References
```

### Option B: Multi-Paper Synthesis

```markdown
# [Synthesis claim]

[Hook: the state of the field / the question that matters]

> **Key Takeaways**
> - [Consensus finding]
> - [Key disagreement]
> - [Practical takeaway]

## The Question
## What the Research Shows
### [Sub-topic 1 with papers]
### [Sub-topic 2 with papers]
## Where Researchers Disagree
## Practical Implications
## What We Still Don't Know
## References
```

### Option C: Original Research/Data

```markdown
# [Your main finding]

[Hook: the question you set out to answer]

> **Key Takeaways**
> - [Main finding with number]
> - [Secondary finding]
> - [Implication or next step]

## Motivation
## Methodology
## Results
## Discussion
## Limitations
## References
```

---

## Citation Rules

- Every factual claim needs a citation (inline, not just in References)
- Use (Author, Year) format in the text
- Numbers from papers get the full citation: "reduced latency by 40% (Chen et al., 2024)"
- Distinguish: "We found..." (your work) vs "Smith found..." (cited work)
- When paraphrasing, still cite. Only skip citation for common knowledge.
- Include a full References section at the end (APA 7 format preferred, or use the bibliography skill)

---

## Figures and Data

- Every figure needs a caption explaining what to look at
- Label axes. Include units.
- If reproducing a figure from a paper, cite the source in the caption
- For original data: describe the dataset (N, timeframe, source) before showing results
- Use tables for comparisons across papers/methods:

```markdown
| Method | Dataset | Accuracy | Speed | Source |
|--------|---------|----------|-------|--------|
| Method A | ImageNet | 94.2% | 12ms | Chen et al., 2024 |
| Method B | ImageNet | 92.8% | 3ms | Park et al., 2023 |
```

---

## Hedging and Confidence

Match your language to evidence strength:

| Evidence Level | Language | Example |
|---|---|---|
| Replicated, meta-analyzed | Direct claim | "X causes Y" |
| Single strong study | Attributed claim | "Chen et al. showed X causes Y" |
| Correlational | Hedged | "X is associated with Y" |
| Preliminary / small N | Cautious | "Early results suggest X may affect Y" |
| Speculation | Flagged | "One possibility is..." / "We speculate that..." |

Never:
- State a preliminary finding as established fact
- Drop hedges from cited papers (if they said "may," you say "may")
- Use "clearly" or "obviously" for contested claims

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Citing only papers that agree with you | Include the strongest counter-evidence |
| Describing methodology without saying why | Every method choice answers "why this and not that?" |
| Dense jargon without payoff | If a term doesn't earn its keep in the next 2 sentences, explain or cut it |
| Conflating correlation and causation | State the study design (RCT, observational, case study) |
| Missing effect sizes | "Significant" means nothing without the magnitude |
| Wall of citations | Synthesize, don't list. "Multiple groups have found X (A, 2020; B, 2021; C, 2022)" |

---

## Checklist

- [ ] Every factual claim has an inline citation
- [ ] Hedging matches evidence strength (no over- or under-claiming)
- [ ] Technical terms defined on first use
- [ ] Figures have captions explaining what to see
- [ ] Methodology sections explain "why this approach"
- [ ] Limitations acknowledged honestly
- [ ] References section complete and consistently formatted
- [ ] Distinguishes your claims from cited claims
- [ ] Effect sizes included (not just "significant")
