# Skills Overview

A guide for human operators: find your goal, see which skills to use and in what order.

## Quick Reference

| Skill | What it does |
|-------|-------------|
| `humanized-writing` | Write prose that reads as human-authored — voice, structure, genre conventions |
| `blogging` | End-to-end blog workflow: strategy, craft, SEO, scoring, distribution |
| `writing-verification` | 6-pass quality pipeline: structure, logic, claims, style, pre-publish, adversarial review |
| `trading-research` | Research trading authors or topics across TASC, MQL5, forums, academic DBs. Two modes: `author` and `topic` |
| `deep-research` | Structured investigation with citations and provenance tracking (non-trading topics) |
| `source-finder` | Find sources across academic databases, web, blogs, GitHub, forums; generate BibTeX |
| `bibliography` | Manage .bib files, format reference lists (APA7, BibTeX, others) |
| `summarization` | Condense long documents using bounded-window reading (RLM pattern) |
| `document-to-markdown` | Convert PDF, DOCX, PPTX, HTML, MHTML to clean markdown |
| `png-to-svg` | Convert raster diagrams/figures to clean hand-crafted SVG (dark/light compatible) |
| `visual-authoring` | Create Mermaid diagrams, draw.io files, and HTML slide decks |

---

## "I want to write a blog post"

**Skills:** `humanized-writing` → `blogging/writing/craft` → `writing-verification`

1. **Draft** using `humanized-writing` for voice and structure guidance. Pick your genre (blog-and-essay, scientific, business-narrative) and follow the technical-articles structure if applicable.
2. **Refine** with `blogging/writing/craft` — applies craft-level patterns (hooks, pacing, transitions, closers).
3. **Verify** by running the `writing-verification` pipeline (passes 1-5, optionally pass 6 for adversarial review).
4. **Score** with `blogging/scoring/quality-rubric` to get a numeric quality assessment.
5. **SEO** — apply `blogging/seo/on-page` and `blogging/seo/ai-citation` if publishing on the web.

---

## "I want to distribute an article to social platforms"

**Skills:** `blogging/distribution/spine-extraction` → `blogging/distribution/hooks` → platform module → `blogging/distribution/voice-check`

1. **Extract the spine** — distill the article to its core argument arc using `spine-extraction`.
2. **Generate hooks** — create platform-appropriate opening lines using `hooks`.
3. **Adapt for platform** — apply platform-specific constraints:
   - `platforms/linkedin` — 900-2500 chars, 210-char hook above fold, no emoji, practitioner voice
   - `platforms/x-twitter` — thread or single-post format, character limits
   - `platforms/medium` — longer-form, subtitle, tags
   - `platforms/substack` — newsletter framing, subject line
4. **Voice check** — run `voice-check` to verify the adapted post matches author voice and platform tone.

---

## "I want to research a trading author or indicator"

**Skills:** `trading-research` (uses `source-finder` for academic/web, `bibliography` for BibTeX)

Two modes — say which one you need:

| You say | What happens |
|---------|-------------|
| `trading research author John Ehlers` | Full author profile: biography, TASC articles (year-by-year), indicators (categorized + per book), photos/videos/interviews, MQL5 implementations, 10 forum searches, academic papers, books with full citations, BibTeX for everything |
| `trading research topic zig-zag indicators` | Topic survey: TASC articles (by keyword, multi-author), MQL5 implementations, 10 forum searches, academic papers, books, BibTeX. No biography or photos. |

Output goes to `trading-research/{slug}.md` + `trading-research/{slug}.provenance.md`. If the file already exists, the skill asks whether to overwrite or skip.

Uses parallel Task agents for speed (TASC, MQL5, forums, academic, photos each run concurrently).

> **Note:** This replaces the old pattern of `deep research (include trading domain) on topic {name}`. The `deep-research` skill is still available for non-trading research briefs.

---

## "I want to research a topic thoroughly (non-trading)"

**Skills:** `deep-research` (orchestrates `source-finder`, `summarization`, `writing-verification` passes 3b + 6)

1. Invoke `deep-research`. It runs a 7-step pipeline:
   - **Plan** — produces a plan artifact, asks for your approval before proceeding
   - **Scale** — decides direct search vs. parallel agents based on complexity
   - **Gather** — uses `source-finder` to retrieve evidence from multiple databases
   - **Draft** — synthesizes findings into a structured brief
   - **Cite** — applies Pass 3b (evidence provenance) to label every source
   - **Review** — applies Pass 6 (adversarial review) to flag unsupported claims
   - **Deliver** — produces final output + provenance sidecar

You get a `<slug>.md` and `<slug>.provenance.md` with full source accounting.

### Continuing or extending a research run

All deep-research state is persisted on disk (plan, research notes, drafts, cited version, verification, provenance). You can come back later and extend or refine without restarting the pipeline:

| You say | What happens |
|---------|-------------|
| "Extend the research on X — also cover Y" | New evidence gathering on Y, integrated into existing draft, re-cite, re-review |
| "Re-run the adversarial review on X" | Pass 6 runs again on the current final output |
| "The sources table needs fixing" | Targeted edit to the final output and provenance |
| "I found new information about X — here it is" | You provide evidence, agent integrates it directly into the existing artifacts |

Point the agent at the slug or topic name so it can locate the existing artifacts (e.g., "continue deep research on `mark-jurik`").

---

## "I want to find and cite sources"

**Skills:** `source-finder` → `bibliography`

1. **Find** — use `source-finder` with your search phrase. It covers:
   - Academic: arXiv, Semantic Scholar, CrossRef, PubMed, OpenAlex, bioRxiv, CORE, Unpaywall
   - Web: blogs, GitHub repos, forums, social media
   - Domain-specific: trading/finance sources
2. **Retrieve** — get metadata, abstracts, PDFs, and auto-generated BibTeX for every result.
3. **Manage** — use `bibliography` to deduplicate entries, format reference lists (APA7, BibTeX, custom styles), and verify URLs.

---

## "I want to verify or review a draft"

**Skills:** `writing-verification`

Run the passes in order. Each pass is independent — you can run all 6 or pick the ones you need:

| Pass | Focus |
|------|-------|
| 1 — Structural review | Section flow, heading hierarchy, missing/redundant sections |
| 2 — Logical clarity | Argument coherence, unsupported leaps, circular reasoning |
| 3 — Technical claims | Factual accuracy, citation needed, hedging calibration |
| 3b — Evidence provenance | Label every source verified/unverified/blocked/inferred |
| 4 — Style and voice | Tone consistency, author voice fidelity, readability |
| 5 — Pre-publish gate | Final checklist: links, formatting, metadata, legal |
| 6 — Adversarial review | FATAL/MAJOR/MINOR severity, inline annotations quoting passages |

Pass 6 is especially useful before publishing high-stakes content — it actively tries to break your arguments.

---

## "I want to summarize a long document"

**Skills:** `summarization`

Uses bounded-window reading (RLM pattern) to prevent context overflow on large documents:

1. Reads the source in sequential windows from disk
2. Maintains a running summary that fits within a target length
3. Each window pass integrates new material and compresses prior summary
4. Produces a final summary that covers the entire document without hallucinating from lost context

Best for: long PDFs, research papers, book chapters, transcripts, or any source too large to fit in a single context window.

---

## "I want to convert a document to markdown"

**Skills:** `document-to-markdown`

Supports: PDF, DOCX, PPTX, HTML, MHTML. Extracts text, tables, and structure into clean markdown. Use this as a preprocessing step before summarization, research, or content adaptation.

---

## "I want to convert a diagram PNG to clean SVG"

**Skills:** `png-to-svg`

Converts raster diagrams (PNG/JPG) into hand-crafted, semantic SVG files with transparent backgrounds and theme-safe colors.

1. **Analyze** — read the PNG, identify elements (curves, arrows, text, arcs), colors, and layout.
2. **Remap colors** — black → green (or user-specified) for dark-mode compatibility; keep saturated colors (red, blue).
3. **Recreate** — build SVG with proper `<text>`, `<path>`, `<line>`, arrow `<marker>` elements.
4. **Validate** — no background rect, real text (not traced), correct markers, both-theme contrast.

Best for: technical diagrams, chart figures from papers, line art with distinct colors. Not for photographs.

Example prompts:
- "Convert `path/to/figure.png` to SVG with transparent background, green instead of black"
- "Recreate this diagram as clean SVG, dark-mode compatible"

---

## "I want to create diagrams or visuals"

**Skills:** `visual-authoring`

Three sub-skills:

- **Mermaid** — flowcharts, sequence diagrams, ER diagrams, Gantt charts, state diagrams, C4, mindmaps, timelines, and 20+ other diagram types. Outputs `.mmd` files renderable in any Mermaid-compatible viewer.
- **Draw.io** — produces `.drawio` XML files for complex diagrams that need manual layout refinement.
- **Slides** — generates self-contained HTML slide decks. Seven templates available (basic, minimal, dark, gradient, business, tech, colorful).

---

## "I want to plan a content calendar"

**Skills:** `blogging/planning/content-calendar` + `blogging/planning/blog-strategy`

1. **Strategy** — define audience, topics, positioning, and cadence with `blog-strategy`.
2. **Calendar** — generate a time-bound posting schedule with topic clusters, dependencies, and platform assignments using `content-calendar`.

---

## Skill Composition Patterns

Skills are designed to compose. Common pipelines:

```
Trading Author/Topic Research:
  trading-research → (parallel: TASC + MQL5 + forums + academic + photos)

General Research + Write:
  deep-research → humanized-writing → writing-verification

Blog + Distribute:
  blogging/craft → writing-verification → spine-extraction → hooks → platform adaptation

Source to Summary:
  document-to-markdown → summarization → bibliography (for citations)

Document Figures:
  document-to-markdown (extract PNGs) → png-to-svg (convert diagrams to vector)

Full Article Pipeline:
  deep-research → humanized-writing → blogging/craft → writing-verification → blogging/seo → distribution
```

---

## Notes

- Skills are stored in `.opencode/skills/` and are automatically available to the agent.
- You do not need to "activate" skills — just describe your goal and the agent will select the appropriate ones.
- If you want to force a specific skill or pass, name it explicitly (e.g., "run pass 6 on this draft").
- The `writing-verification` pipeline is non-destructive: it produces annotations and findings, not edits. You decide what to fix.
