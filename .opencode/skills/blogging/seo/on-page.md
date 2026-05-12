# On-Page SEO

Heading hierarchy, keyword placement, meta descriptions, answer-first formatting, and schema markup for blog posts.

## Answer-First Formatting

The single most impactful structural pattern for both search ranking and AI citation:

**Every H2 section opens with a 40-60 word paragraph that directly answers the section's implied question.** This paragraph should contain a statistic or specific claim. AI systems extract from section openers, and Google's featured snippets prefer concise answer-first content.

Example:
```markdown
## How much does zero-lag filtering actually reduce latency?

Zero-lag filtering reduces group delay by 60-80% compared to standard EMAs
of equal smoothing, at the cost of 10-15% more overshoot on sharp reversals.
A 20-period zero-lag EMA typically shows 3-4 bars less lag than its
conventional counterpart on daily equity data.

[Supporting detail, methodology, caveats follow...]
```

---

## Title Tag

- **Length**: 40-60 characters (displays fully in SERPs)
- **Structure**: `[Primary Keyword] — [Specific Claim or Payoff]` or `How to [Achieve X] with [Method/Tool]`
- Positive framing outperforms negative in CTR
- Include primary keyword in first half
- Never stuff — one primary keyword, naturally placed

---

## Meta Description

- **Length**: 150-160 characters
- Include primary keyword once
- Include a specific number or claim (improves CTR)
- End with implied benefit to the reader
- Never use filler ("In this article, we explore...")

---

## Heading Hierarchy

- One H1 per page (the title)
- 6-8 H2 sections forming the main structure
- H3s as needed under H2s
- **Never skip levels** (H1 → H3 is invalid)
- 60-70% of H2s should be questions or specific claims
- Include primary keyword in 1-2 H2s (naturally)
- Include related keywords in remaining H2s

---

## Keyword Placement

| Location | Rule |
|----------|------|
| Title (H1) | Primary keyword, naturally placed |
| First paragraph | Primary keyword within first 100 words |
| H2 headings | Primary in 1-2; related terms in others |
| Body | No density target — natural usage only |
| Alt text | Describe the image; include topic keyword if natural |
| URL slug | Short, includes primary keyword, hyphens only |

**Never keyword-stuff.** Google penalizes this. If a keyword feels forced, rephrase.

---

## Content Structure for Search

- **Paragraph length**: 40-80 words (50-150 word chunks for AI extraction)
- **Sentence length**: 15-20 words average, max 25
- **Readability**: Flesch 60-70 (Grade 7-8)
- **Bold key phrases**: 3-5 per 300 words (helps scanners AND search extractors)
- **Visual content**: every 200-350 words (image, diagram, table, code block)
- **Internal links**: 3-5 per 1500 words to related content
- **External links**: 2-4 to authoritative sources (Tier 1-2 only)

---

## FAQ Schema

If the post naturally answers multiple questions, add an FAQ section:

```markdown
## Frequently Asked Questions

### [Question using natural search language]?

[40-60 word direct answer. One paragraph. No hedging in the answer itself.]

### [Next question]?

[40-60 word direct answer.]
```

This maps to FAQ schema (JSON-LD) and is strongly favored by AI citation systems. 5-8 questions per post is optimal.

---

## Schema Markup (JSON-LD)

Include in the post's frontmatter or template:

**BlogPosting** (minimum):
```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Title",
  "datePublished": "2026-04-30",
  "dateModified": "2026-04-30",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "description": "Meta description"
}
```

**Additional schemas** (add when applicable):
- `FAQPage` for FAQ sections
- `HowTo` for step-by-step guides
- `Person` with sameAs links for author E-E-A-T
- `BreadcrumbList` for site navigation

---

## Freshness Signals

76.4% of the most-cited pages in AI systems were updated within the last 30 days.

- Include `dateModified` in schema (update when content changes)
- Reference current year data where possible
- Update statistics annually at minimum
- Add "Last updated: YYYY-MM-DD" visible in the post

---

## Internal Linking

- 3-5 internal links per 1500-word post
- Use descriptive anchor text (not "click here" or "this article")
- Link to related content that deepens the reader's understanding
- Hub-and-spoke model: pillar pages link to supporting articles and vice versa
- Check for orphan pages (new content must link to something and be linked from something)

---

## Image Optimization

- Every image needs descriptive alt text (not "image1.png")
- Include topic keywords in alt text naturally
- Compress images (WebP preferred)
- Add width/height attributes to prevent layout shift
- Use descriptive filenames: `zero-lag-ema-comparison.webp` not `img_2847.webp`

---

## Checklist

- [ ] Title 40-60 chars with primary keyword
- [ ] Meta description 150-160 chars with keyword and number
- [ ] H1 → H2 → H3 hierarchy (no skips)
- [ ] Primary keyword in first 100 words
- [ ] Answer-first paragraph on every H2 section
- [ ] 3-5 internal links with descriptive anchors
- [ ] All images have descriptive alt text
- [ ] FAQ section (if applicable) with 40-60 word answers
- [ ] Schema markup (BlogPosting minimum)
- [ ] dateModified updated
- [ ] URL slug is short and includes keyword
