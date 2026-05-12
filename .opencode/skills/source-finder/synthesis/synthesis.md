# Research Synthesis

Multi-source validation, quality scoring, and literature review generation.

## When to Use

- After collecting sources from multiple sub-skills
- When the user needs a literature review or research summary
- When conflicting information needs resolution
- For comprehensive "state of the art" overviews

## Synthesis Workflow

### 1. Collect

Gather results from academic/, web/, domain/ searches. Deduplicate on DOI/URL.

### 2. Assess Quality

Score each source (see web/web.md for scoring criteria):

| Criteria | Weight |
|----------|--------|
| Authority (official, expert, peer-reviewed) | 30% |
| Recency | 25% |
| Specificity (detail, examples, data) | 25% |
| Independence (unbiased, non-sponsored) | 20% |

### 3. Cross-Validate

For each key claim:
- Find 2+ independent sources confirming
- Note contradictions explicitly
- Distinguish primary vs. secondary sources
- Flag single-source claims as "unverified"

### 4. Identify Themes

Group findings into:
- **Consensus** — agreed by multiple sources
- **Contested** — sources disagree
- **Gaps** — important questions with no good sources
- **Emerging** — recent findings not yet widely validated

### 5. Synthesize

Produce a structured output:

```markdown
## Topic Overview
[1-2 paragraph summary]

## Key Findings
1. [Finding with citations]
2. [Finding with citations]

## Contested Points
- [Claim A (source 1) vs Claim B (source 2)]

## Gaps
- [What's missing from the literature]

## Sources
[BibTeX entries or formatted references]
```

## Depth Levels

| Level | Sources | Output | Use when |
|-------|---------|--------|----------|
| Quick | 3-5 | 1-2 paragraphs | Simple factual question |
| Standard | 8-12 | Structured report | Technical comparison |
| Deep | 15+ | Full literature review | Architecture decisions, comprehensive analysis |

## Bias Mitigation

- **Vendor content**: include but flag as potentially biased
- **Sponsored results**: deprioritize, note sponsorship
- **Popularity bias**: don't assume most-cited = most correct
- **Recency bias**: older sources may be more rigorous
- **Confirmation bias**: actively search for contradicting evidence
