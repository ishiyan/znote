# Quality Rubric

100-point scoring system for blog post quality. Use to evaluate before publishing and to identify improvement priorities.

## Scoring Categories

| Category | Points | Weight |
|----------|--------|--------|
| Content Quality | 30 | Depth, readability, originality, structure, engagement |
| SEO Optimization | 25 | Headings, title, keywords, internal links, meta |
| E-E-A-T Signals | 15 | Author, citations, trust, experience |
| Technical Elements | 15 | Schema, images, speed, mobile, OG tags |
| AI Citation Readiness | 15 | Passage citability, Q&A format, entity clarity |

---

## Content Quality (30 points)

| Item | Points | Criteria |
|------|--------|----------|
| Depth & completeness | 8 | Covers the topic thoroughly; reader doesn't need to look elsewhere |
| Readability | 5 | Flesch 60-70, Grade 7-8, sentence variety (StdDev ≥5) |
| Originality | 5 | Contains insight, data, or perspective not found in top 5 competitors |
| Structure | 5 | Clear progression, answer-first paragraphs, logical flow |
| Engagement | 4 | Hook opening, information headings, varied formatting |
| Grammar & anti-pattern | 3 | Zero banned language, zero em dashes, AI triggers ≤5/1K, passive ≤10% |

---

## SEO Optimization (25 points)

| Item | Points | Criteria |
|------|--------|----------|
| Heading hierarchy | 5 | One H1, 6-8 H2s, no skipped levels, question/claim headings |
| Title tag | 4 | 40-60 chars, primary keyword, specific claim |
| Keyword placement | 4 | In first 100 words, 1-2 H2s, URL slug; no stuffing |
| Internal linking | 4 | 3-5 links to related content, descriptive anchors |
| URL structure | 3 | Short, keyword-rich, hyphens only |
| Meta description | 3 | 150-160 chars, keyword + number/claim |
| External links | 2 | 2-4 to Tier 1-2 sources |

---

## E-E-A-T Signals (15 points)

| Item | Points | Criteria |
|------|--------|----------|
| Author attribution | 4 | Real name, credentials, bio on page |
| Source citations | 4 | Claims backed by Tier 1-3 sources, inline attribution |
| Trust indicators | 4 | Honest limitations, corrections noted, no overclaiming |
| Experience signals | 3 | First-person accounts, case studies, "I built/tested this" |

---

## Technical Elements (15 points)

| Item | Points | Criteria |
|------|--------|----------|
| Schema markup | 4 | BlogPosting minimum; FAQ/HowTo if applicable |
| Image optimization | 3 | Alt text on all, compressed, descriptive filenames |
| Structured data | 3 | Tables, lists, code blocks properly formatted |
| Page speed | 3 | No oversized images, efficient loading |
| Mobile & OG tags | 2 | Responsive, og:title, og:description, og:image |

---

## AI Citation Readiness (15 points)

| Item | Points | Criteria |
|------|--------|----------|
| Passage citability | 4 | Answer-first paragraphs (40-60 words), extractable chunks |
| Q&A format | 4 | FAQ section with 5-8 questions, 40-60 word answers |
| Entity clarity | 3 | Key terms defined, no ambiguity about what's being discussed |
| Content structure | 2 | 50-150 word paragraphs, question headings |
| Crawler accessibility | 2 | SSR/static, no JS-only content, AI bots allowed |

---

## Scoring Bands

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Exceptional | Publish as-is. Flagship content. |
| 80-89 | Strong | Minor polish, ready for publication. |
| 70-79 | Acceptable | Targeted improvements needed before publishing. |
| 60-69 | Below Standard | Significant rework required. Do not publish. |
| < 60 | Rewrite | Fundamental issues. Start from outline. |

**Minimum publishing threshold: 80 points.**

---

## Priority Classification

When a post scores below 80, prioritize fixes:

| Priority | Fix if... | Impact |
|----------|-----------|--------|
| Critical | Factual errors, broken code, misleading claims | Immediate trust damage |
| High | Missing answer-first paragraphs, no FAQ, weak opening | Large scoring impact (5+ points) |
| Medium | Missing internal links, weak headings, no schema | Moderate impact (2-4 points) |
| Low | Image optimization, OG tags, minor readability | Small impact (1-2 points) |

---

## Quick Automated Checks

These can be verified programmatically:

- [ ] Title length: 40-60 characters
- [ ] Meta description: 150-160 characters
- [ ] H1 count: exactly 1
- [ ] H2 count: 6-8
- [ ] No H-level skips (H1→H3)
- [ ] Primary keyword in first 100 words
- [ ] Flesch readability: 60-70
- [ ] Sentence length StdDev: ≥5
- [ ] Em dash count: 0
- [ ] AI trigger word density: ≤5 per 1000 words
- [ ] Passive voice: ≤10%
- [ ] Paragraph max: 80 words
- [ ] Internal links: ≥3
- [ ] External links: ≥2
- [ ] All images have alt text
- [ ] FAQ section present (if post >1500 words)
- [ ] dateModified in frontmatter/schema
