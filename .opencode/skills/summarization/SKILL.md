---
name: summarization
description: Summarize any document (URL, local file, PDF) using bounded-window reading to prevent context degradation. Adapts strategy based on document size — direct read for short docs, windowed extraction for medium, parallel chunked processing for large. Use when the user asks to summarize, condense, extract key points from, or review the contents of any document.
---

# Summarization (RLM Pattern)

Summarize documents of any size without context degradation. The core principle: **the document stays on disk as an external variable** and is read in bounded windows — so context pressure is proportional to the window size, not the document size.

## Why This Exists

Standard summarization injects the full document into context. Above ~15k tokens, early content degrades as the window fills ("context rot"). This skill keeps the source on disk and reads bounded windows, preventing quality loss on long documents.

## When to Use

- Summarize a URL, local file, PDF, or any document
- Extract key claims from a long source
- Condense a paper or report into actionable bullets
- "What does this document say?" questions on files > 8000 characters

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Window size | 6000 chars | How much text to read per pass |
| Overlap | 500 chars | Overlap between adjacent windows (catches cross-boundary arguments) |
| Tier 1 threshold | 8000 chars | Below this: direct read (safe for short inputs) |
| Tier 2 threshold | 60000 chars | Above this: parallel chunked processing |

## Process

### Step 1: Fetch and Measure

1. **Remote URL**: fetch to a local temp file. For GitHub repo URLs, fetch the raw README instead of the HTML page
2. **Local file**: read directly
3. **PDF**: extract text first (via appropriate tools)
4. **Validate**: if result is < 50 bytes, stop and report the error. If binary content detected, stop and report
5. **Measure** decoded text character count (not bytes)

### Step 2: Choose Tier

| Document size | Tier | Strategy |
|---|---|---|
| < 8000 chars | 1 | Direct read — full content enters context (safe for short inputs) |
| 8000 – 60000 chars | 2 | Windowed — read 6000-char windows sequentially, write notes to disk between windows |
| > 60000 chars | 3 | Parallel chunks — split into chunks, process each independently, synthesize |

### Step 3: Execute

#### Tier 1 — Direct Read

Read the full document. Summarize directly. Simple and fast.

#### Tier 2 — Windowed Read

The document stays on disk. For each window:

1. Read a 6000-character slice (with 500-char overlap from previous window)
2. Extract key claims, methodology, and evidence from this window
3. Write extracted notes to a running notes file **before reading the next window** (this is the checkpoint — if interrupted, processed windows survive)
4. Move to next window

After all windows processed: synthesize notes into final summary.

**Critical rule**: write notes after each window. Do NOT accumulate window contents in memory. The entire point is to keep context pressure bounded.

#### Tier 3 — Parallel Chunks

For very large documents, split into independent chunks and process each in a separate Task agent:

1. Split document into 6000-char chunks with 500-char overlap
2. Each chunk gets a fresh agent context (context rot is impossible — no agent sees more than one chunk)
3. Each agent extracts: key claims, methodology, cited evidence. Marks cross-boundary partial claims as `BOUNDARY PARTIAL`
4. Lead agent synthesizes all chunk summaries:
   - Deduplicate (a claim in multiple chunks = one claim; keep most complete formulation)
   - Resolve boundary conflicts (prefer version with more surrounding context)
   - Remove BOUNDARY PARTIAL markers where a complete version exists in a neighbor

## Output Format

All tiers produce the same structure:

```markdown
# Summary: [document title or source filename]

**Source:** [URL or file path]
**Date:** [YYYY-MM-DD]
**Tier:** [1 / 2 (N windows) / 3 (N chunks)]

## Key Claims
- [3-7 most important assertions, each as a bullet]

## Methodology
[Approach, dataset, evaluation — omit for non-research documents]

## Limitations
[What the source explicitly flags as weak, incomplete, or out of scope]

## Verdict
[One paragraph: what this document establishes, its credibility, who should read it]

## Coverage Gaps *(only if some sections couldn't be processed)*
[What was missed and why]
```

## Rules

1. **Never inject large documents into context directly** when they exceed Tier 1 threshold. The window strategy exists precisely to prevent this
2. **Write notes between windows** — don't accumulate in memory
3. **One source only** — summarization verifies the single source is reachable, then works from it. No external sources are added
4. **Honest coverage** — if a section couldn't be processed, note it in Coverage Gaps rather than fabricating content
5. **No hallucinated content** — every claim in the summary must trace to text in the source document
6. **Preserve hedges** — if the source says "X may contribute to Y", the summary must not sharpen to "X causes Y"
