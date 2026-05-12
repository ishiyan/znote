# Mermaid Diagrams

Create text-based diagrams that render natively in GitHub, GitLab, Notion, VS Code, and any markdown viewer. Mermaid is the default choice for any diagram that will live inside a `.md` file.

## Why Mermaid First

- Git diff readable (text, not binary)
- No build step needed
- Token-efficient (smaller than prose describing the same relationship)
- Parseable by AI without vision
- Convertible to image later — but text stays as source of truth

## Diagram Type Selection

Match your content to the most specific type. Do NOT default to flowcharts for everything.

| Use case | Type | Reference |
|----------|------|-----------|
| Process steps / decision logic | Flowchart | [diagrams/flowchart.md](diagrams/flowchart.md) |
| Service interactions / API calls | Sequence | [diagrams/sequence.md](diagrams/sequence.md) |
| Database schema / data model | ER Diagram | [diagrams/er.md](diagrams/er.md) |
| State machine / lifecycle | State | [diagrams/state.md](diagrams/state.md) |
| Project timeline / roadmap | Gantt | [diagrams/gantt.md](diagrams/gantt.md) |
| Proportions / composition | Pie | [diagrams/pie.md](diagrams/pie.md) |
| System architecture (zoom levels) | C4 | [diagrams/c4.md](diagrams/c4.md) |
| Concept hierarchy / brainstorm | Mindmap | [diagrams/mindmap.md](diagrams/mindmap.md) |
| Chronological events | Timeline | [diagrams/timeline.md](diagrams/timeline.md) |
| Class hierarchy / types | Class | [diagrams/class.md](diagrams/class.md) |
| User experience / satisfaction | User Journey | [diagrams/user_journey.md](diagrams/user_journey.md) |
| Two-axis comparison | Quadrant | [diagrams/quadrant.md](diagrams/quadrant.md) |
| Requirements traceability | Requirement | [diagrams/requirement.md](diagrams/requirement.md) |
| Flow magnitude / distribution | Sankey | [diagrams/sankey.md](diagrams/sankey.md) |
| Numeric trends (bar + line) | XY Chart | [diagrams/xy_chart.md](diagrams/xy_chart.md) |
| Component layout | Block | [diagrams/block.md](diagrams/block.md) |
| Work item status board | Kanban | [diagrams/kanban.md](diagrams/kanban.md) |
| Cloud infrastructure topology | Architecture | [diagrams/architecture.md](diagrams/architecture.md) |
| Multi-dimensional comparison | Radar | [diagrams/radar.md](diagrams/radar.md) |
| Hierarchical proportions | Treemap | [diagrams/treemap.md](diagrams/treemap.md) |
| Binary protocol / data format | Packet | [diagrams/packet.md](diagrams/packet.md) |
| Git branching / merge strategy | Git Graph | [diagrams/git_graph.md](diagrams/git_graph.md) |
| Code-style sequence | ZenUML | [diagrams/zenuml.md](diagrams/zenuml.md) |

## Style Guide

### Accessibility (Mandatory)

Every diagram MUST include both `accTitle` and `accDescr`:

```
accTitle: Short Name 3-8 Words
accDescr: One or two sentences explaining what this diagram shows.
```

**Types that do NOT support `accTitle`/`accDescr`:** Mindmap, Timeline, Quadrant, Sankey, XY Chart, Block, Kanban, Packet, Architecture, Radar, Treemap. For these, place a descriptive _italic_ paragraph directly above the code block.

### Theme Rules

- **No `%%{init}` directives** — breaks GitHub dark mode
- **No inline `style`** — use `classDef` only
- Let GitHub auto-theme

### Color Classes (GitHub light + dark safe)

```mermaid
classDef primary fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
classDef success fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d
classDef warning fill:#fef9c3,stroke:#ca8a04,stroke-width:2px,color:#713f12
classDef danger fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d
classDef neutral fill:#f3f4f6,stroke:#6b7280,stroke-width:2px,color:#1f2937
classDef accent fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#3b0764
classDef warm fill:#ffedd5,stroke:#ea580c,stroke-width:2px,color:#7c2d12
```

Rules:
- Always include `color:` (text color) in every `classDef`
- Max 3-4 color classes per diagram
- Never rely on color alone — pair with emoji, shape, or label text

### Node Naming

- `snake_case` IDs that match labels
- 3-6 word labels, active voice, sentence case
- Edge labels: 1-4 words
- One emoji per node max, at the start: `[🔐 Authenticate]`

### Node Shapes

| Shape | Syntax | Meaning |
|-------|--------|---------|
| Rounded rectangle | `([text])` | Start / end / terminal |
| Rectangle | `[text]` | Process / action |
| Diamond | `{text}` | Decision / condition |
| Subroutine | `[[text]]` | Subprocess |
| Cylinder | `[(text)]` | Database / data store |
| Hexagon | `{{text}}` | Preparation / init |

### Complexity Management

| Nodes | Strategy |
|-------|----------|
| 1-10 | Flat diagram, no subgraphs |
| 10-20 | Use subgraphs (2-4 groups) |
| 20-30 | Subgraphs mandatory, consider overview + detail |
| 30+ | Split into multiple diagrams |

Subgraph format: `subgraph name ["📋 Descriptive Title"]`

### Common Pitfalls

| Type | Gotcha | Fix |
|------|--------|-----|
| Radar | `radar` keyword doesn't exist | Use `radar-beta` with `axis` and `curve` |
| Architecture | Emoji in `[]` labels | Use plain text labels only |
| Architecture | Hyphens parsed as operators | `[US East Region]` not `[US-East Region]` |
| Flowchart | Word `end` breaks parsing | Wrap: `["End"]` or use `end_node` ID |
| Sankey | No emoji in node names | Parser doesn't support them |
| ZenUML | Requires external plugin | Prefer `sequenceDiagram` syntax |

## Workflow

1. **Pick diagram type** — scan selection table, match content to type
2. **Read type reference** — open the specific `diagrams/*.md` file
3. **Write diagram** — apply style guide (accessibility, naming, colors)
4. **Verify** — test render in mermaid.live or VS Code preview
5. **Commit** — the `.md` with embedded Mermaid is the source of truth
