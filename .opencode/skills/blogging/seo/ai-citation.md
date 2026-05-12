# AI Citation Optimization (GEO/AEO)

Generative Engine Optimization and Answer Engine Optimization. How to make blog content citable by ChatGPT, Perplexity, Google AI Overviews, and Gemini.

## Why This Matters

AI systems now drive significant traffic and brand visibility. Only 11% of domains overlap between ChatGPT and Perplexity citations, meaning you must optimize for each independently. 76.4% of ChatGPT's most-cited pages were updated within 30 days.

---

## The AI Search Pipeline

AI citation follows three stages (Kevin Indig's framework):

1. **Retrieval** — AI finds your content (crawlability, indexing, freshness)
2. **Citation** — AI selects your content to quote (structure, authority, answer-first)
3. **Trust** — AI ranks your citation higher (E-E-A-T signals, source tier, backlinks)

---

## Content Optimization for AI Citation

### Structure

- **Answer-first formatting**: Every H2 opens with a 40-60 word stat-rich paragraph. AI systems extract from section openers.
- **Question headings**: 60-70% of H2s should be questions matching natural search queries
- **50-150 word chunks**: AI extracts passages of this length. Keep paragraphs in this range.
- **FAQ section**: 5-8 Q&A pairs with 40-60 word answers (strongest single signal for AI citation)
- **Tables and lists**: Structured data is easier for AI to extract and cite

### Citation Position Bias

44.2% of AI citations come from the first 30% of the text. Front-load your most citable content.

### Readability-GEO Connection

Content at Flesch 60-75 readability receives 31% more AI citations than content above or below that range.

---

## Source Tier System

AI systems evaluate your sources. Only cite Tier 1-3:

| Tier | Description | Examples |
|------|-------------|---------|
| **1** | Primary research, official data | Published papers, government statistics, company reports |
| **2** | Major publications, industry leaders | Nature, IEEE, NYT, established tech blogs (official) |
| **3** | Reputable industry sources | Well-known analyst firms, established community sites |
| **4** | General content (DO NOT CITE) | Content mills, affiliate sites, AI-generated aggregators |
| **5** | Unverified (DO NOT CITE) | Forums, social media posts, anonymous blogs |

Citing authoritative sources boosts AI visibility by up to 115% (Princeton GEO research).

---

## Platform-Specific Patterns

### ChatGPT
- Favors comprehensive, well-structured content
- Heavily weights recency (30-day update cycle)
- Values named expert authors with verifiable credentials
- 76.4% of most-cited pages updated within 30 days

### Perplexity
- Favors concise, directly-answering content
- Values structured data (tables, lists, Q&A)
- Weights source authority heavily
- Only 11% domain overlap with ChatGPT (optimize separately)

### Google AI Overviews
- Pulls from already-ranking content (traditional SEO still matters)
- Favors passages that directly answer the query
- Values schema markup (FAQ, HowTo, Article)
- Content must be crawlable (no JS-only rendering)

---

## Off-Site Signals

Off-site signals dominate AI citation rankings:

| Signal | Correlation | Action |
|--------|-------------|--------|
| YouTube mentions | 0.737 | Create companion videos or get mentioned in relevant videos |
| Reddit discussions | 450% growth | Participate authentically in relevant subreddits; link naturally |
| Review platforms (B2B) | Strong | Maintain profiles on G2, Capterra if applicable |
| Wikipedia/Wikidata | 7.8% of ChatGPT citations | If notable, create or improve your Wikipedia presence |

---

## Technical Requirements

AI crawlers cannot render JavaScript. Ensure:

- Server-side rendering (SSR) or static HTML for all content
- No content behind authentication or paywalls (AI bots can't log in)
- `robots.txt` allows GPTBot, ClaudeBot, PerplexityBot
- Fast page load (bots have timeout limits)
- Clean HTML structure (semantic tags, not div soup)
- `dateModified` in schema and visible on page

### AI Crawler User Agents

```
GPTBot, ChatGPT-User, ClaudeBot, PerplexityBot, 
Google-Extended, Applebot-Extended
```

Allow all of these in `robots.txt` unless you have a specific reason to block.

---

## E-E-A-T for AI Citation

AI systems increasingly evaluate author expertise:

- **Experience**: First-person accounts, case studies, "I built this"
- **Expertise**: Credentials, publication history, speaking engagements
- **Authoritativeness**: Backlinks, mentions, citations by others
- **Trustworthiness**: Accurate claims, corrections published, no deceptive practices

Signals:
- Author bio with credentials on every post
- `Person` schema with `sameAs` links (LinkedIn, GitHub, etc.)
- Consistent author across related posts (topical authority)
- Update outdated content promptly

---

## Freshness Strategy

To stay within the 30-day citation window:

- Update key statistics monthly (even small changes trigger dateModified)
- Add new examples or case studies quarterly
- Refresh "Year" in titles annually ("Best X in 2026")
- Monitor for broken links monthly (broken = stale signal)

---

## Checklist

- [ ] Answer-first paragraph on every H2 (40-60 words, stat-rich)
- [ ] 60-70% of H2s are question headings
- [ ] FAQ section with 5-8 Q&A pairs (40-60 word answers)
- [ ] All sources Tier 1-3 (no content mills or unverified sources)
- [ ] Flesch readability 60-75
- [ ] dateModified in schema (updated within 30 days)
- [ ] AI crawlers allowed in robots.txt
- [ ] Content renders without JavaScript (SSR/static)
- [ ] Author bio with credentials present
- [ ] Person schema with sameAs links
- [ ] Key content front-loaded (first 30% of article)
