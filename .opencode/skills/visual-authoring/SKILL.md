---
name: visual-authoring
description: Create diagrams, slides, and publication figures from text or images. Supports Mermaid (24 diagram types), D2 (C4 architecture), draw.io (XML editing), Marp (7 themes), and matplotlib/seaborn (journal-ready plots). Use when the user says "diagram", "flowchart", "slide", "presentation", "figure", "plot", "architecture diagram", "Mermaid", "D2", "Marp", "draw.io", "convert image to SVG/Mermaid", or "visualize".
---

# Visual Authoring

Create diagrams, presentations, and publication-quality figures using text-based tools. All outputs are version-control friendly (text source committed alongside rendered artifacts).

## When to Use

- Creating any diagram (workflow, architecture, data model, state machine, timeline)
- Converting an image of a diagram to SVG or Mermaid code
- Creating presentations/slides (Marp markdown)
- Producing publication-ready scientific figures (matplotlib/seaborn)
- Drawing architecture diagrams with C4 model (D2 or Mermaid)
- Editing draw.io files programmatically (XML)

## Prerequisites

```bash
# Marp (slides → PDF/HTML/PPTX)
npm install -g @marp-team/marp-cli

# D2 (architecture diagrams → SVG/PNG)
brew install d2          # macOS
# or: curl -fsSL https://d2lang.com/install.sh | sh

# draw.io (diagram editing → PNG/SVG export)
brew install --cask drawio   # macOS

# Scientific visualization
pip install matplotlib seaborn numpy pandas
```

## Tool Selection

| Need | Tool | When to prefer |
|------|------|----------------|
| Quick inline diagram in markdown | **Mermaid** | Renders natively on GitHub/GitLab/Notion. 24 types. No build step. |
| Architecture diagram with C4 model | **D2** | Better layout engine (ELK), richer styling, SVG/PNG output. Needs `d2` CLI. |
| Editable diagram with GUI option | **draw.io** | When the user wants to open/edit in draw.io desktop. AWS icons. |
| Presentation slides | **Marp** | Markdown → PDF/HTML slides. 7 built-in themes. Needs `marp` CLI. |
| Data visualization / publication figure | **matplotlib/seaborn** | Scatter plots, line charts, heatmaps, statistical plots. Journal submission. |

**Decision heuristic:**
1. If it goes inline in a `.md` file → **Mermaid**
2. If it's a standalone architecture/system diagram → **D2**
3. If the user mentions draw.io or needs AWS icons → **draw.io**
4. If slides/presentation → **Marp**
5. If data-driven plot or publication figure → **matplotlib/seaborn**

## Converting an Image to Diagram Code

When the user provides an image of a diagram and asks to convert it:

1. **Examine the image** — identify shapes, connections, labels, flow direction
2. **Choose output format** — ask if not specified:
   - `.mmd` (Mermaid) — for embedding in markdown
   - `.svg` — for standalone vector graphic (produce via D2 or hand-written SVG)
   - `.d2` — for D2 source with rendering
3. **Transcribe the structure** — map visual elements to the chosen syntax
4. **Verify** — render and compare against the original image

## Sub-Skill Index

| Sub-skill | Path | Covers |
|-----------|------|--------|
| Mermaid diagrams | [mermaid/](mermaid/mermaid.md) | 24 diagram types, style guide, color palette, accessibility |
| D2 diagrams | [d2/](d2/d2.md) | C4 model, style classes, judge loop, advanced features |
| draw.io | [drawio/](drawio/drawio.md) | XML editing, coordinate system, AWS icons, conversion |
| Marp slides | [slides/](slides/slides.md) | 7 themes, image patterns, best practices, Marp syntax |
| Scientific visualization | [visualization/](visualization/visualization.md) | matplotlib, seaborn, publication styles, color palettes |

## Shared Color Palette

All diagram tools should use this consistent semantic palette where possible:

| Semantic | Hex (fill) | Hex (stroke) | Hex (text) |
|----------|-----------|-------------|-----------|
| Primary / action | `#dbeafe` | `#2563eb` | `#1e3a5f` |
| Success / positive | `#dcfce7` | `#16a34a` | `#14532d` |
| Warning / caution | `#fef9c3` | `#ca8a04` | `#713f12` |
| Danger / critical | `#fee2e2` | `#dc2626` | `#7f1d1d` |
| Neutral / info | `#f3f4f6` | `#6b7280` | `#1f2937` |
| Accent / highlight | `#ede9fe` | `#7c3aed` | `#3b0764` |
| Warm / commercial | `#ffedd5` | `#ea580c` | `#7c2d12` |

These are tested in both GitHub light and dark modes.

## SVG Color Compatibility

When saving SVG files, inject a `<style>` block with `prefers-color-scheme` media queries so the diagram is visible in both light and dark editor/browser themes:

```xml
<style>
  svg { stroke: black; fill: black; }
  @media (prefers-color-scheme: dark) {
    svg { stroke: white; fill: white; }
  }
</style>
```

Do NOT set `stroke="currentColor"` on individual elements — it breaks some previewers. Instead, omit explicit stroke/fill attributes on lines and text so they inherit from the `<style>` block. Use `fill="none"` on shapes that should be transparent (letting the background show through). Skip this block only if the SVG already uses explicit non-black colors throughout.

## Quality Checklist (All Outputs)

- [ ] Source file committed (`.mmd`, `.d2`, `.drawio`, `.md`, `.py`)
- [ ] Rendered output present alongside source (`.svg`, `.png`, `.pdf`)
- [ ] Accessibility: alt text, `accTitle`/`accDescr` (Mermaid), tooltips (D2)
- [ ] No hardcoded absolute paths
- [ ] Consistent color palette with other diagrams in the project
- [ ] Text readable at intended display size
