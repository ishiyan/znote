---
name: humanized-writing
description: Use when writing any prose humans will read — articles, documentation, essays, blog posts, reports, emails, UI text, or scientific papers. Produces clear, forceful, natural-sounding writing free of AI patterns. Covers voice/style (foundations), document architecture (structure), and domain-specific guidance (genres).
---

# Humanized Writing

Write prose that sounds like a specific person thought it through, not like a language model smoothed it into paste.

## Universal Rules (always apply)

1. **Active voice by default.** "We shipped the fix" not "The fix was shipped."
2. **Concrete over abstract.** Name the thing, state the number, cite the source.
3. **Omit needless words.** "Because" not "due to the fact that." "Now" not "at this point in time."
4. **Use contractions.** "don't", "won't", "it's" — uncontracted forms are a major AI tell.
5. **One paragraph, one topic.** Lead with the topic sentence.
6. **Vary sentence length.** Short for punch. Longer for flow. Fragments for emphasis.
7. **Place emphatic words at end of sentence.**
8. **Positive form.** Say what it is, not what it isn't.
9. **Proof instead of adjectives.** "Cut reporting from 4 hours to 15 minutes" not "dramatically improved efficiency."
10. **Kill correlative constructions.** Never write "It's not just X — it's Y." State the stronger claim directly.

## Kill-on-Sight Patterns

Any of these in output = rewrite that sentence:

- **Vocabulary:** delve, crucial, pivotal, foster, leverage, tapestry, testament, underscore, vibrant, landscape (abstract), interplay, multifaceted, enhance, enduring, garner, showcase, seamless, robust, cutting-edge, groundbreaking, realm, paradigm, synergy
- **Openers:** "In today's world...", "Let's dive in", "In the ever-evolving landscape...", "Gone are the days..."
- **Structural tells:** forced triads, "Not just X but Y", synonym cycling, fake ranges, summary sandwiches
- **Filler:** "It is important to note that", "In order to" (→ "To"), "When it comes to", "At the end of the day"
- **Communication artifacts:** "Great question!", "I hope this helps!", "As of my last update"

## Three Layers

### Layer 1: Foundations (always loaded)

Core voice, style, and anti-AI enforcement. Apply to every sentence.

- `foundations/voice-and-style.md` — Registers, rhythm, human markers, lint checklist
- `foundations/clarity-and-concision.md` — Strunk's composition principles, grammar rules
- `foundations/signs-of-ai-writing.md` — Reference: comprehensive AI-pattern detection guide

### Layer 2: Structure (apply when planning a document)

Document architecture before drafting. How to organize ideas.

- `structure/architecture.md` — McPhee's 8 structure types, diagramming, gold-coin placement
- `structure/technical-articles.md` — Thesis spine, directional movement, earned solutions, narrative arc

### Layer 3: Genres (apply by document type)

Domain-specific rules loaded on demand:

- `genres/blog-and-essay.md` — Lead with concrete, banned patterns, voice handling
- `genres/scientific.md` — IMRAD, field terminology, reporting guidelines, LaTeX
- `genres/business-narrative.md` — Story structures (SCR, Hero's Journey), audience adaptation

## Workflow

1. **Before writing:** Classify document type → load relevant genre module
2. **If document is >500 words:** Plan structure using Layer 2 before drafting
3. **While writing:** Apply Layer 1 continuously
4. **After drafting:** Run the lint checklist from `foundations/voice-and-style.md`

## The Read-Aloud Test

If any sentence sounds like a press release, a Wikipedia article, or a chatbot response — rewrite it. If you stumble reading it aloud, readers will too.
