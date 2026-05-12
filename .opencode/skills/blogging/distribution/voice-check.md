# Voice Check

Quality gate that audits all platform outputs for voice fidelity before delivery.

## When to Run

After all platform rewrites are complete, before delivering to the user. This is the final gate.

## Workflow

1. Read all platform output files
2. For each file, scan for:
   - **Voice-don'ts**: banned vocabulary, emoji, exclamations, generic openers
   - **Voice-dos**: opener classification, hedge preservation, paper attribution
   - **Platform-specific tonal drift**
3. Report pass/fail per file with specific flags
4. If FAIL: loop back to the relevant platform rewrite (max 2 loops)
5. After 2 failed loops: ship best-so-far with a design note

## Banned Vocabulary (All Platforms)

Regex scan for these — automatic FAIL if found:

```
delve, unpack, paradigm shift, game-changer, transformative,
revolutionary, synergy, leverage (as verb), utilize, furthermore,
moreover, it's worth noting, at the end of the day
```

Also fail on:
- Any emoji
- Any exclamation point
- "I think" (weak; replace with direct claim or proper hedge)
- "AI is transforming..."
- Any custom CTA not in the original post

## Platform-Specific Tonal Checks

| Platform | Expected Tone | Flag If |
|---|---|---|
| Substack Note | Closest to essay voice | Over-polished; reads AI-rewritten |
| X thread | More declarative, quotable | Over-hedging ("Substack leak on X") |
| LinkedIn | Practitioner, slightly less confessional | Raw confession on LinkedIn ("Substack leak on LinkedIn") |
| Medium | Polished, slightly literary | Too casual or too corporate |
| Cross-post blurb | Third person, neutral-analytical | Any first-person ("I argue...") |

"Substack leak" = the confessional/raw voice from the essay showing up unchanged on a platform where it reads as inappropriate.

## Attribution Check

If the original post cites papers or data sources:
- Every platform file must mention Author, Institution, Year on first reference
- If a platform's character limit makes attribution impossible, drop the claim (don't cite without attribution)

## Hedge Preservation

If the original post hedges a claim ("X may contribute to Y"), every platform output must preserve that hedge. Sharpening hedges for engagement ("X causes Y") is a FAIL.

## Loop-Back Protocol

```
Loop 1: Flag issues → return to rewrite skill → regenerate
Loop 2: Flag remaining issues → return to rewrite skill → regenerate
Loop 3: STOP. Ship best-so-far with design note:
```

> DESIGN-NOTE: This post's voice may not translate cleanly to {platform}. User review recommended for {specific issue}.

## Output Format

```markdown
## Voice Check Results

### linkedin.md: PASS / FAIL
- [line/location] — [issue] — [rule violated]

### x-twitter.md: PASS / FAIL
- variant: short — [issue]
- variant: medium — [issue]

### substack.md: PASS / FAIL
- [issue]

### medium.md: PASS / FAIL
- [issue]

### cross-post-blurb: PASS / FAIL
- [issue]
```

## Guardrails

1. Every flag must cite a specific rule. No flags without citation.
2. Do not edit platform files directly. Emit flags; let the rewrite re-run.
3. Check banned vocabulary first (fast regex), tonal shift second (requires judgment).
4. Max 2 loops per artifact. Ship after that.
5. Zero emoji tolerance across all files.
