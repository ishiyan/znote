---
name: blogging
description: Write, optimize, and distribute blog articles. Covers technical, scientific, and general-audience posts. Can write from scratch given a topic, "blogerize" existing markdown documents, create social media posts (LinkedIn, X, Substack, Medium), and plan editorial calendars. Use when the user says "blog", "blogerize", "write a post", "social post", "content calendar", "thread", or "distribute".
---

# Blogging

Write blog articles, convert existing documents into blog posts, distribute content across social platforms, and plan editorial series.

## When to Use

- Writing a blog article from scratch (any genre)
- Converting an existing markdown document into blog format ("blogerize")
- Creating social media posts from a blog article or essay
- Planning a series of blog articles covering a subject
- Reviewing/scoring blog post quality

## Workflow by Use Case

### Use Case 1: Write a Blog Article

1. Clarify: topic, audience, genre (technical / scientific / general), target length
2. Select template → see [writing/templates.md](writing/templates.md)
3. Apply craft rules → see [writing/craft.md](writing/craft.md)
4. Apply genre-specific rules:
   - Technical → [writing/technical.md](writing/technical.md)
   - Scientific → [writing/scientific.md](writing/scientific.md)
   - General → craft.md is sufficient
5. Apply SEO → see [seo/on-page.md](seo/on-page.md)
6. Score quality → see [scoring/quality-rubric.md](scoring/quality-rubric.md)

### Use Case 2: Blogerize an Existing Document

1. Read the source markdown
2. Identify the core argument, key claims, and target audience
3. Select appropriate template from [writing/templates.md](writing/templates.md)
4. Rewrite applying craft rules from [writing/craft.md](writing/craft.md):
   - Add a hook opening (problem or conclusion first)
   - Convert academic/dry sections to conversational flow
   - Add information headings (not generic labels)
   - Break long paragraphs (max 80 words / 3 sentences)
   - Add a Key Takeaways box near the top
   - End with actionable next steps
5. Apply genre rules if technical/scientific
6. Apply SEO rules
7. Score and iterate

### Use Case 3: Distribute to Social Platforms

1. Extract the argument spine → see [distribution/spine-extraction.md](distribution/spine-extraction.md)
2. Generate platform-specific hooks → see [distribution/hooks.md](distribution/hooks.md)
3. Rewrite for each target platform:
   - LinkedIn → [distribution/platforms/linkedin.md](distribution/platforms/linkedin.md)
   - X/Twitter → [distribution/platforms/x-twitter.md](distribution/platforms/x-twitter.md)
   - Substack → [distribution/platforms/substack.md](distribution/platforms/substack.md)
   - Medium → [distribution/platforms/medium.md](distribution/platforms/medium.md)
4. Run voice check → see [distribution/voice-check.md](distribution/voice-check.md)

### Use Case 4: Plan a Blog Series

1. Define the subject and audience
2. Apply strategy framework → see [planning/blog-strategy.md](planning/blog-strategy.md)
3. Generate editorial calendar → see [planning/content-calendar.md](planning/content-calendar.md)

## Core Principles

These apply to ALL blog content regardless of genre:

1. **Problem-first opening** — state the problem or conclusion in the first 2-3 sentences. Never start with background, history, or hype.
2. **Information headings** — every heading conveys a specific claim or finding. Never "Background" or "Results."
3. **Numbers over adjectives** — every performance claim needs a number. "Reduced latency from 340ms to 45ms" not "significantly improved."
4. **Short paragraphs** — 40-80 words max. 2-3 sentences. White space is structural.
5. **Answer-first formatting** — every H2 section opens with a 40-60 word summary paragraph before going deeper.
6. **Honest hedging** — acknowledge limitations. If something is uncertain, say so. Never overclaim.
7. **One voice per document** — pick the voice (practitioner, researcher, explainer) and hold it.

## Banned Language

Never use in any blog post:

- "We're excited/thrilled to announce" — just announce it
- "Best-in-class" / "industry-leading" / "cutting-edge"
- "Seamless" / "seamlessly"
- "Empower" / "leverage" / "unlock"
- "Robust" — describe what makes it robust
- "Streamline"
- "In this blog post, we will explore..."
- "Let's dive in" / "Without further ado"
- "That being said" / "It's worth noting that"
- "At the end of the day"
- "Delve" / "unpack" / "paradigm shift"
- "Game-changer" / "revolutionary" / "transformative"

## Anti-AI Detection Rules

Blog content must not read as AI-generated:

- Zero em dashes (use commas, parentheses, or periods instead)
- AI trigger words ≤5 per 1000 words (furthermore, moreover, crucial, comprehensive, innovative, facilitate, utilize, optimal, enhance, leverage)
- Passive voice ≤10% of sentences
- Sentence length variance: StdDev ≥5 words (mix short punchy with longer complex)
- No repetitive sentence starters (vary first 3 words)
- No over-qualified hedging ("It is important to note that perhaps...")

## Quality Gate

Before publishing, the post must pass the "Would I Share This?" test:

- Does it contain at least one of:
  - A technical decision explained with trade-offs
  - Original data or insight not found elsewhere
  - A real-world story with specific details
  - An honest accounting of something that went wrong
  - A how-to that saves the reader real time
- Would a practitioner in the field share this in their team chat?

If the answer is no, the post needs more depth or original insight.

## File Index

### Writing
- [writing/craft.md](writing/craft.md) — Voice, structure, openings, closings, banned patterns
- [writing/technical.md](writing/technical.md) — Source-code deep dives, Mermaid diagrams, file:line citations
- [writing/scientific.md](writing/scientific.md) — Academic blog style, citation-heavy, methodology
- [writing/templates.md](writing/templates.md) — 12 post-type skeletons with word counts

### SEO
- [seo/on-page.md](seo/on-page.md) — Heading hierarchy, keywords, meta, answer-first, schema
- [seo/ai-citation.md](seo/ai-citation.md) — GEO/AEO: AI Overviews, ChatGPT/Perplexity citation

### Distribution
- [distribution/spine-extraction.md](distribution/spine-extraction.md) — Extract argument backbone
- [distribution/hooks.md](distribution/hooks.md) — Platform-specific opening hooks
- [distribution/platforms/linkedin.md](distribution/platforms/linkedin.md) — LinkedIn post rules
- [distribution/platforms/x-twitter.md](distribution/platforms/x-twitter.md) — X thread rules
- [distribution/platforms/substack.md](distribution/platforms/substack.md) — Substack Note + cross-post
- [distribution/platforms/medium.md](distribution/platforms/medium.md) — Medium article rules
- [distribution/voice-check.md](distribution/voice-check.md) — QA gate for all platform outputs

### Planning
- [planning/blog-strategy.md](planning/blog-strategy.md) — Topic clustering, audience, differentiation
- [planning/content-calendar.md](planning/content-calendar.md) — Series planning, cadence, content mix

### Scoring
- [scoring/quality-rubric.md](scoring/quality-rubric.md) — 100-point scoring rubric
