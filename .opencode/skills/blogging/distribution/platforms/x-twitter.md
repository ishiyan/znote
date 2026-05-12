# X/Twitter Thread

Rewrite a blog post as an X thread in three variants (short, medium, long). Includes a skip mechanism for posts that don't translate.

## Constraints

| Parameter | Value |
|-----------|-------|
| Characters per tweet | 280 max |
| Short variant | 3-5 tweets |
| Medium variant | 6-8 tweets |
| Long variant | 9-12 tweets (hard cap) |
| Hashtags | Zero |
| Emoji | Zero |
| Numbering (1/n) | None (dated for tech accounts post-2026) |
| Links | Final tweet only |

## Variant Selection by Translatability

| Variant | Which spine claims to use |
|---------|--------------------------|
| Short | Only translatability-5 claims |
| Medium | Translatability 4 and 5 |
| Long | Full spine (all claims) |

## Structure

```
Tweet 1 (hook) [N chars]:
{opening — must work standalone; confession or bold claim}

Tweet 2 [N chars]:
{one claim per tweet — stands alone}

Tweet 3 [N chars]:
{next claim}

...

Link tweet [N chars]:
Full essay: {url}
```

Include character count in brackets after each tweet for audit.

## Skip Mechanism

If >60% of spine claims score translatability 2 or below:

```
VERDICT: This post doesn't translate to X. Skip X for this post.
Reason: [brief explanation — too context-dependent, too nuanced for 280-char chunks, etc.]
```

Halt. Do not produce weak variants. Shipping bad threads damages the account more than silence.

## One Claim Per Tweet

Each tweet must pass the "stands alone" test: if someone saw only this tweet (not the thread), would it make sense and be interesting? If not, the claim needs more context than 280 chars allow — either add context or drop the tweet.

## Link Placement

Links ONLY in the final tweet. Mid-thread links get algorithmic depression (post-March 2026). The final tweet format:

```
Full essay: {url}
```

## Guardrails

1. Hard 280-char cap. Include character count in brackets.
2. Max 12 tweets per variant. Attention cliff beyond that.
3. One claim per tweet. Two claims = fails the "stands alone" test.
4. Keep paper attributions intact. If "Chen et al., Google, 2024" won't fit with the claim, drop the tweet entirely. Never collapse the attribution.
5. Hedges from the post preserved verbatim. No sharpening.
6. No hashtags, no emoji, no numbering.
7. If the hook can't fit in 280 chars, the post doesn't translate to X.
