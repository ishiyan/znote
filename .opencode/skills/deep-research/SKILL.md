---
name: deep-research
description: Run a thorough, source-heavy investigation on a topic and produce a research brief with inline citations and a provenance sidecar. Use when the user says "deep research", "investigate", "research brief", "comprehensive analysis", or needs a multi-source investigation with citation verification.
---

# Deep Research

A structured research workflow that produces a cited brief with provenance tracking. Uses direct search for narrow questions (fewer than 3 sub-questions, answerable in 3–10 tool calls) and parallel Task agents for broader surveys (3+ sub-questions or multi-domain topics). See Step 2 for full criteria.

## Pipeline

```
Plan (with user gate) → Scale → Gather → Draft → Cite → Review → Deliver
```

**Quick decision guide:** Plan always runs first and requires user approval. Scale picks direct vs. parallel mode. Gather uses `source-finder`. Draft is always written by the lead agent. Cite, Review, and Deliver run sequentially on the draft.

## Cooperation with Other Skills

```
deep-research
  ├── source-finder     →  evidence gathering (databases, web, forums)
  ├── summarization     →  condensing large sources via bounded-window reading
  ├── writing-verification
  │     ├── Pass 3b    →  evidence provenance labeling
  │     └── Pass 6     →  adversarial review (FATAL/MAJOR/MINOR)
  └── bibliography      →  BibTeX management for cited sources
```

## Artifacts

Derive a short slug from the topic: lowercase, hyphenated, no filler words, max 5 words.

Every run produces:

| Artifact | Path |
|----------|------|
| Plan | `outputs/.plans/<slug>.md` |
| Draft | `outputs/.drafts/<slug>-draft.md` |
| Cited draft | `outputs/.drafts/<slug>-cited.md` |
| Final output | `outputs/<slug>.md` |
| Provenance sidecar | `outputs/<slug>.provenance.md` |

## Step 1: Plan

Create `outputs/.plans/<slug>.md` containing:

- Key questions to answer
- Evidence needed (types of sources, domains)
- Scale decision (see Step 2)
- Task ledger (who does what)
- Verification log (empty, filled during run)

After writing the plan, **stop and ask the user for approval**:

> Proceed with this deep research plan? Reply "yes" to continue, or tell me what to change.

Do not gather evidence, draft, or deliver until the user confirms. If the user requests changes, update the plan and ask again.

## Step 2: Scale Decision

**Direct search** (lead agent does everything):
- Single fact or narrow "what is X" question
- Answerable with 3-10 tool calls
- Do NOT inflate simple explainers into multi-agent surveys

**Parallel Task agents** (use OpenCode's `Task` tool):
- Direct comparison of 2-3 items: 2 Task agents
- Broad survey or multi-faceted topic: 3-4 Task agents
- Complex multi-domain research: 4-6 Task agents

Each Task agent gets a written brief file (`outputs/.plans/<slug>-T<n>.md`) and writes its findings to `outputs/.drafts/<slug>-research-<label>.md`.

## Step 3: Gather Evidence

Use the `source-finder` skill for structured source retrieval.

**Direct mode:**
- Run at least 3 distinct queries covering different angles (definition, mechanism, current usage/comparison)
- Record search terms in `outputs/.drafts/<slug>-research-direct.md`
- Write notes to the same file

**Parallel mode:**
- Write per-agent briefs to `outputs/.plans/<slug>-T<n>.md`
- Launch Task agents with `subagent_type: "general"`
- Each agent reads its brief, gathers evidence, writes findings to disk

**Domain-specific workflows (MUST apply when relevant):**
- **TASC authors/contributors:** When the research subject is a TASC magazine author, editor, or contributor, follow the "TASC Author Research Workflow" in `source-finder/domain/trading.md`. That workflow covers fetching the author archive, constructing PDF URLs, checking Traders' Tips, searching MQL5 CodeBase, and generating BibTeX. Agent briefs for publication-related tasks MUST reference that workflow. The final output MUST contain: articles table with PDFs/Tips, MQL5 implementations section, and a complete BibTeX section.
- **Additional TASC research requirements:** Search the mandatory trading forums list (ForexFactory, futures.io, Elite Trader, NinjaTrader Forum, TradingView, MQL5 Forum, Wealth-Lab, Quant SE, r/algotrading, Trade2Win) for dedicated threads. Find actual photo/video/interview URLs (YouTube, company sites, Wikipedia/Wikimedia, podcasts) — mark unfound items `[URL not found]`. All external books mentioned must have full citations with ISBN, publisher, Google Books link, and BibTeX `@book` entry.
- Set expectations: agents should use file-based output, not return large results inline

After gathering, update the plan's task ledger and verification log.

## Step 4: Draft

The lead agent always writes the synthesis. Never delegate drafting.

Save to `outputs/.drafts/<slug>-draft.md`. Include:

- Executive summary
- Findings organized by question or theme
- Evidence-backed caveats and disagreements
- Open questions
- No invented sources, figures, benchmarks, or data

**Domain-specific sections (include when applicable):**
- **Trading/indicators research:** The draft MUST include a `## BibTeX` section (all articles and books as BibTeX entries) and a `## MQL5 Implementations` section (CodeBase links for each indicator). These are mandatory deliverables, not optional appendices.

Pre-citation sweep: every critical claim must map to a source URL, research note, or artifact path. Remove or downgrade unsupported claims. Mark inferences explicitly as inferences.

## Step 5: Cite

Apply the **evidence provenance pass** (Pass 3b from `writing-verification`):

- Add inline citations `[n]` for every factual claim
- Build a Sources section with URLs
- Label each source: `verified` / `unverified` / `blocked` / `inferred`
- Verify reachable URLs where possible

Write the result to `outputs/.drafts/<slug>-cited.md`.

## Step 6: Review

Apply the **adversarial review pass** (Pass 6 from `writing-verification`):

- Flag unsupported claims, logical gaps, single-source critical claims, overstated confidence
- Classify findings as FATAL / MAJOR / MINOR
- Write findings to `outputs/.drafts/<slug>-verification.md`

Resolution:
- FATAL: fix before delivery, re-verify the fix landed
- MAJOR: fix or note in Open Questions
- MINOR: accept

If fixes are needed, write corrected version to `outputs/.drafts/<slug>-revised.md`.

## Step 7: Deliver

Copy final candidate to `outputs/<slug>.md`.

Write provenance sidecar `outputs/<slug>.provenance.md`:

```markdown
# Provenance: [topic]

- **Date:** [date]
- **Scale:** [direct / N parallel agents]
- **Sources consulted:** [count]
- **Sources accepted:** [count]
- **Sources rejected:** [list with reasons: dead URL, unverifiable, etc.]
- **Verification:** [PASS / PASS WITH NOTES / BLOCKED]
- **Plan:** outputs/.plans/<slug>.md
- **Research files:** [list]
```

Before responding, verify all required artifacts exist on disk.

## Degraded Mode

If any capability fails after plan approval:
- Continue with available evidence
- Mark blocked checks in provenance as `BLOCKED`
- Still produce a final output and provenance sidecar
- Never end with chat-only output after the user approved the plan

## Honesty Rules

- Never use `verified` or `confirmed` unless the check actually ran
- Never smooth over missing checks — use `blocked`, `unverified`, or `inferred`
- Never invent sources, figures, or benchmarks
- If a fix is claimed, verify the old text is gone and new text exists before marking it done
