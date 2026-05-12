# Writing Craft

Voice, structure, openings, closings, and anti-patterns for all blog genres.

## Voice

Sound like a knowledgeable practitioner explaining something they care about to a peer. Not a press release, not a textbook, not a sales deck.

**Voice attributes**:
- Direct and specific (not hedging or corporate)
- Technically precise (correct terms, correct numbers)
- Opinionated where warranted (state your position, then back it)
- Conversational but not sloppy (contractions OK, slang sparingly)
- Honest about limitations and uncertainty

Use "you" (reader) and "I" or "we" (author/team). This is a conversation.

Humor is welcome but must serve the content. One good joke per post is plenty. Sarcasm works in moderation.

---

## Opening (First 2-3 Sentences)

The opening must do one of two things: **state the problem** or **state the conclusion**. Never start with background, history, setup, or hype.

**Patterns that work**:
- **Problem-first**: "Two weeks before launch, we killed our entire metrics product. Here's why pre-aggregating time-series metrics breaks down for debugging."
- **Conclusion-first**: "Moving averages with zero lag don't exist. But you can get close enough to trade on it."
- **Confession**: "I spent four months building something nobody needed."
- **Surprising claim**: "Your JavaScript bundle has 47% dead code. Here's how to find it."

**Patterns that fail**:
- "At [Company], we're always looking for ways to improve..."
- "In today's fast-paced world of..."
- "In this blog post, we will explore..."
- Background/history before the point arrives

---

## Structure

Organize around the reader's questions, not your internal narrative:

1. **What problem does this solve?** (1-2 paragraphs max)
2. **How does it actually work?** (Bulk of the post — be specific)
3. **What were the trade-offs or alternatives?** (Separates good from great)
4. **How do I use/try/implement this?** (Concrete next steps)

For engineering posts, add:
5. **What did we try that didn't work?** (Builds trust)
6. **What are the known limitations?** (Shows honesty)

### Key Takeaways Box

Near the top (after opening), include a summary box:

```markdown
> **Key Takeaways**
> - [Main finding/claim in one sentence]
> - [Second key point]
> - [Third key point — action-oriented]
```

3-5 bullets, 40-60 total words. This serves both human scanners and AI citation extraction.

### Section Structure

Every H2 section follows this pattern:
1. **Answer-first paragraph** (40-60 words summarizing what this section establishes)
2. Supporting evidence, examples, code
3. Transition sentence to next section

---

## Headings

Headings must convey information. They are claims, not labels.

| Weak | Strong |
|------|--------|
| Background | Why time-series pre-aggregation destroys debugging context |
| Architecture | The scatter-gather approach to distributed GROUP BY |
| Results | Where this breaks down: the cardinality wall |
| Conclusion | Ship the simpler version first |

Rules:
- H1: one per post (the title)
- H2: 5-8 per post, forming the main structure
- H3: as needed under H2s for sub-topics
- Never skip levels (H1 → H3 without H2)
- 60-70% of H2s should be questions or claims

---

## Paragraphs and Sentences

- **Paragraph length**: 40-80 words, 2-3 sentences max
- **Sentence length**: average 15-20 words, max 25. Variance is key — mix short punchy sentences (5-8 words) with longer complex ones (20-25)
- **Sentence length StdDev**: ≥5 words (monotone rhythm reads as AI)
- **One idea per paragraph**. If you're making two points, split.

---

## Closings

End with something useful:
- A link to docs or getting-started guide
- A way to try the thing described
- A call to give feedback or share results
- A forward-looking statement about what's next

Never end with:
- "We can't wait to see what you build!"
- A recap of what you just said
- Generic hype or inspiration
- "In conclusion..." (just end)

---

## Titles

The title is the highest-leverage sentence. It must stop a reader scrolling through RSS or social feeds.

**Strong titles** make a specific claim or promise a specific payoff:
- "The metrics product we built worked. But we killed it and started over anyway"
- "How we reduced release delays by 5% by fixing Salt"
- "Your JavaScript bundle has 47% dead code. Here's how to find it."

**Weak titles** are vague announcements:
- "Introducing our new metrics product"
- "Performance improvements in Sentry"
- "AI-powered debugging with Seer"

Title rules:
- 40-60 characters (displays fully in search results and social previews)
- Positive framing outperforms negative (but honest negative works for postmortems)
- Include the core keyword naturally

---

## Anti-AI Detection Patterns

Content must read as human-written. Automated detection rules:

| Pattern | Rule |
|---------|------|
| Em dashes | Zero. Use commas, parentheses, colons, or periods. |
| AI trigger words | ≤5 per 1000 words (furthermore, moreover, crucial, comprehensive, innovative, facilitate, utilize, optimal, enhance, leverage, delve, unpack, streamline, paradigm) |
| Passive voice | ≤10% of sentences |
| Sentence starters | No more than 2 consecutive paragraphs starting with the same word pattern |
| Over-qualified hedging | Never "It is important to note that perhaps..." — just state the hedge directly |
| Burstiness | Vary paragraph length. 1-sentence paragraphs mixed with 3-sentence ones. |
| Lists | Don't over-use bullet lists. 1-2 per post section max. Prose preferred. |

---

## Formatting for Readability

- **Bold** 3-5 phrases per 300 words for scanners (key terms, not emphasis)
- Visual content every 200-350 words (diagram, code block, table, image)
- Use tables for comparisons (3+ items with 2+ attributes)
- Use code blocks for any literal code, commands, or structured output
- Use blockquotes for external citations only (not for emphasis)

---

## The Review Checklist

Before publishing:

**Technical**:
- [ ] All claims are accurate and verifiable
- [ ] Code samples work (tested)
- [ ] Numbers and benchmarks are correct and sourced
- [ ] No oversimplifications that would make an expert cringe

**Editorial**:
- [ ] Opening hooks within 2 sentences
- [ ] Passes the "Would I Share This?" test
- [ ] No banned language or filler
- [ ] Headings convey information
- [ ] Right length (not padded, not too thin)
- [ ] Title is specific and compelling

**Formatting**:
- [ ] Paragraphs ≤80 words
- [ ] Sentence length varies (StdDev ≥5)
- [ ] Visual content every 200-350 words
- [ ] Zero em dashes
- [ ] AI trigger words ≤5 per 1000
