# Web Research

Structured workflow for finding, validating, and citing information from general web sources.

## When to Use

- Technical comparisons, feature analysis
- Finding official documentation
- Independent analyses and benchmarks
- Community discussions and expert opinions
- Any non-academic research

## Search Strategy

### Multi-Angle Queries

Execute parallel searches from different angles:

| Angle | Query pattern | Example |
|-------|--------------|---------|
| Factual | "What is X" | "What is Jurik Moving Average" |
| Comparative | "X vs Y" | "JMA vs KAMA comparison" |
| Technical | "X implementation" | "JMA algorithm implementation" |
| Practical | "X tutorial/guide" | "JMA trading strategy guide" |
| Recent | "X 2024 2025" | "JMA indicator 2025" |

### Query Tips

- Add year constraints for technology topics
- Include exact product/concept name
- Focus each query on a single aspect
- Use negative keywords to exclude noise

## Source Types and Priority

| Priority | Source type | Trust level | Examples |
|----------|------------|-------------|----------|
| 1 | Official documentation | Highest | API docs, product docs, specs |
| 2 | Peer-reviewed papers | High | Journal articles, conference papers |
| 3 | Official blogs | High | Company engineering blogs |
| 4 | Independent tech analysis | Medium-high | InfoQ, Martin Fowler, personal expert blogs |
| 5 | Community validated | Medium | Stack Overflow (high votes), GitHub discussions |
| 6 | General blogs | Medium-low | Medium, dev.to (verify quality first) |
| 7 | Forum posts | Low-medium | Reddit, specialized forums |
| 8 | Social media | Low | X/Twitter, LinkedIn (use as leads only) |

## Source Diversification Checklist

For standard research, ensure coverage across:
- [ ] Official documentation (≥2 sources)
- [ ] Independent analysis (≥1 source)
- [ ] Community discussion (≥1 source)
- [ ] Recent content (<2 years)

## Quality Scoring

Rate each source on:

| Criteria | Weight | 5 = best | 1 = worst |
|----------|--------|----------|-----------|
| Authority | 30% | Official docs, known expert | Anonymous, unknown |
| Recency | 25% | <6 months | >3 years |
| Specificity | 25% | Detailed with examples | Vague overview |
| Independence | 20% | Unbiased analysis | Vendor/sponsored content |

## Bias Detection

Flag sources that:
- Are produced by a vendor being evaluated
- Contain affiliate links or sponsored markers
- Lack author attribution
- Make claims without evidence or references
- Are SEO-optimized content farms

## Conflict Resolution

When sources disagree:
1. Prefer official documentation
2. Check publication dates (newer wins for tech)
3. Note the disagreement explicitly
4. Provide both perspectives if unresolved

## Link Verification

Before delivering results:
- Verify URLs are accessible (WebFetch or curl HEAD)
- Replace 404 links with alternatives
- Ensure page content matches the claimed information

## Output

Every web source gets:
1. **Title and URL** — verified accessible
2. **Summary** — 1-2 sentences of what it contains
3. **Quality score** — based on criteria above
4. **BibTeX entry** — see retrieval/bibtex-templates.md for `@online` template
5. **Access date** — when the page was retrieved
