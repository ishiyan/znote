---
name: writing-verification
description: Multi-pass verification pipeline for written documents before publication. Runs 5 sequential passes (structural, logical-clarity, technical-claims, style-and-voice, pre-publish-gate) to catch issues at every level from architecture to surface polish. Use when reviewing, verifying, or doing a final check on any written document before sharing or publishing.
---

# Writing Verification

Five-pass review pipeline. Run passes in order — each assumes prior passes are clean.

## When to Use

- Before publishing any article, essay, report, or post
- When asked to "review", "verify", "check", or "final pass" a document
- After the humanized-writing skill has produced a draft

## Pipeline

```
Pass 1: Structural Review       → architecture, section roles, flow
Pass 2: Logical Clarity         → claims, evidence chains, reasoning gaps
Pass 3: Technical Claims        → factual accuracy, 5-bucket classification
Pass 3b: Evidence Provenance    → source traceability, link verification, provenance status
Pass 4: Style and Voice         → surface polish, anti-AI patterns, tone
Pass 5: Pre-Publish Gate        → binary pass/fail checklist, final verdict
Pass 6: Adversarial Review      → inline annotations, severity rating, revision plan
```

## Execution Rules

1. **Sequential**: Do not skip passes. Each builds on the prior.
2. **Flag, don't fix**: Present issues to the user; do not silently rewrite.
3. **Binary outcomes**: Each check item is PASS or FAIL, never "mostly fine".
4. **Preserve voice**: Never alter meaning or authorial intent.
5. **Context-aware**: Adjust rigor to genre (blog vs. academic vs. business).

## Pass Dispatch

| Pass | File | Focus |
|------|------|-------|
| 1 | [passes/1-structural-review.md](passes/1-structural-review.md) | Section architecture, transitions, narrative arc |
| 2 | [passes/2-logical-clarity.md](passes/2-logical-clarity.md) | Claim-evidence chains, hedging, reasoning |
| 3 | [passes/3-technical-claims.md](passes/3-technical-claims.md) | Factual verification, 5-bucket taxonomy |
| 3b | [passes/3b-evidence-provenance.md](passes/3b-evidence-provenance.md) | Source traceability, link verification, provenance audit |
| 4 | [passes/4-style-and-voice.md](passes/4-style-and-voice.md) | Surface polish, AI-pattern detection |
| 5 | [passes/5-pre-publish-gate.md](passes/5-pre-publish-gate.md) | Final pass/fail gate |
| 6 | [passes/6-adversarial-review.md](passes/6-adversarial-review.md) | Inline annotations, FATAL/MAJOR/MINOR severity, revision plan |

## When to Use Pass 6

Pass 6 (Adversarial Review) is optional for most content. Run it when:
- The document makes strong claims that could be challenged publicly
- The document will be submitted to peer review or formal evaluation
- The author explicitly requests adversarial scrutiny
- The document reports quantitative results or benchmarks

Skip Pass 6 for: blog posts, social media adaptations, personal essays, how-to guides.

## Output Format

After all passes, produce a summary:

```
VERIFICATION SUMMARY
====================
Pass 1 (Structure):    PASS / FAIL — [1-line note]
Pass 2 (Logic):        PASS / FAIL — [1-line note]
Pass 3 (Claims):       PASS / FAIL — [1-line note]
Pass 3b (Provenance):  PASS / FAIL — [1-line note]
Pass 4 (Style):        PASS / FAIL — [1-line note]
Pass 5 (Gate):         PASS / FAIL — [1-line note]
Pass 6 (Adversarial):  PASS / FAIL / SKIPPED — [1-line note]

VERDICT: READY TO PUBLISH / NEEDS REVISION
BLOCKERS: [count] items requiring action before publish

Issues:
1. [pass:section] description
2. ...
```

## Go/No-Go Rules

- **READY TO PUBLISH**: All 5 passes PASS, zero blockers.
- **NEEDS REVISION**: Any pass FAIL, or any blocker exists.
- A single `wrong` claim (Pass 3) is an automatic blocker.
- A single structural incoherence (Pass 1) is an automatic blocker.

## Reference

- [reference/hedging-calibration.md](reference/hedging-calibration.md) — 5-level hedge scale
- [reference/claim-buckets.md](reference/claim-buckets.md) — 5-bucket claim taxonomy
