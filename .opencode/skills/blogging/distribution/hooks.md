# Hook Generation

Generate 3-5 candidate opening hooks for a specific platform from a spine. Score each and drop any below quality threshold.

## Workflow

1. Pull `best_hook_candidates` + thesis + opening claim from spine
2. Apply platform hook rules (see table below)
3. Generate 3-5 candidates
4. Score each: attention (1-5), voice-fidelity (1-5), truth-fidelity (1-5)
5. Drop any hook scoring <4 on voice-fidelity
6. Return sorted list (highest total score first)

## Platform Hook Rules

| Platform | Length cap | Pattern | Notes |
|---|---|---|---|
| Substack Note | 1-2 sentences | Confession preferred | Can use reframe; closest to essay voice |
| X (hook tweet) | 240 chars | Confession or bold claim | No question unless genuine; no "here's what I learned" |
| LinkedIn | 210 chars (must survive "...see more" fold) | Practitioner confession | "I spent four months..." > "I had a realization..." |
| Medium | 1-2 sentences | Surprising claim or question | Can be slightly more literary than X/LinkedIn |
| Cross-post blurb | N/A | Third-person positioning | "In this piece, [Author] argues..." |

## Hook Patterns

| Pattern | When it works | Example |
|---------|---------------|---------|
| Confession | Personal essay, failure story | "I spent four months building something nobody needed." |
| Bold claim | Data-backed opinion | "Your JavaScript bundle has 47% dead code." |
| Reframe | Challenging conventional wisdom | "This isn't about prediction markets. It's about the gap between knowing and doing." |
| Question | Only if genuinely provocative | "What if the problem isn't your prompts but your architecture?" |
| Data point | Research or measurement posts | "We measured 2,847 API calls. 63% were redundant." |

## Scoring

| Axis | 5 | 3 | 1 |
|------|---|---|---|
| Attention | Would stop mid-scroll | Mildly interesting | Would skip |
| Voice-fidelity | Sounds exactly like the author | Generic but acceptable | Sounds like a different person |
| Truth-fidelity | Claim fully supported in the post | Slight exaggeration | Promises something the post doesn't deliver |

**Hard rule**: Voice-fidelity < 4 = automatic discard. Never include.

## Banned Hooks

Never generate:
- "AI is transforming..."
- "In today's fast-paced..."
- "Let's explore..."
- "Here's what I learned..."
- "I had a realization..."
- Any hook starting with a stat NOT in the post
- Any question that's rhetorical and obvious

## Guardrails

1. Never generate a hook that promises something the post doesn't deliver.
2. Stay within the platform length cap (a 300-char X hook is not a hook, it's a thread).
3. Cross-post hooks use third person; never "I" in that variant.
4. Don't start with a stat unless the stat is in the post.
5. Per platform, generate at least 3 candidates so the writer has choices.
