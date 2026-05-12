# LinkedIn Post

Rewrite a blog post as a LinkedIn post with a hook fitting the 210-character fold, practitioner framing, and short paragraphs.

## Constraints

| Parameter | Value |
|-----------|-------|
| Total length | 900-2500 characters |
| Hook (above fold) | 210 characters max |
| Paragraphs | 2-3 lines each |
| Hashtags | 0-2 (niche only) |
| Emoji | Zero |
| Exclamation points | Zero |
| Bold text | None (renders as markdown leak) |

## Structure

```
{hook: 1-2 lines, 210 chars max — must survive the "...see more" fold}

{one-sentence pivot paragraph}

{body: 4-7 short paragraphs of 2-3 lines each}

{optional list block only if genuinely enumerable}

{practitioner takeaway — plain text, not bolded}

Full essay: {url}

{#NicheHashtag1 #NicheHashtag2}  ← 0-2 only
```

## Voice Shift

LinkedIn reads "practitioner sharing learnings" — slightly less confessional than a blog essay, slightly more professional.

| Blog voice | LinkedIn adaptation |
|---|---|
| "I do not know whether this generalizes." | "I'm still figuring out if this generalizes." |
| "I shipped a demo in a weekend." | "A team I worked with shipped a demo in a weekend." |
| Raw confession opener | "Here's what broke" rather than "I was wrong" |

The shift is subtle. Full pronoun-stripping or corporate-speak is NOT acceptable.

## Hashtag Rules

- 0-1 hashtags preferred; max 2
- Niche only: `#MultiAgentSystems`, `#LLMEngineering`, `#SignalProcessing`
- Never generic: `#AI`, `#tech`, `#innovation`, `#thoughts`, `#leadership`, `#motivation`

## Guardrails

1. First 210 chars MUST fit the fold. Count and verify.
2. Total 2500 chars max. LinkedIn caps at 3000 but dwell data drops above 2500.
3. White space is structural. No dense walls of text.
4. Use list blocks only if the content is genuinely enumerable. Never shoehorn.
5. Preserve paper attributions (Author, Institution, Year).
6. No bold (renders poorly). No emoji. No exclamation points. No custom CTA.
7. Link goes on its own line near the end.
