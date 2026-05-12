# Marp Slides

Create professional presentation slides using Marp (Markdown Presentation Ecosystem). Markdown source → PDF/HTML/PPTX output.

## Prerequisites

```bash
npm install -g @marp-team/marp-cli
# Or: npx @marp-team/marp-cli slide.md -o slide.pdf
```

## When to Use Marp

- Creating presentations from markdown
- Scientific or technical talks
- Any slide deck that benefits from version control
- When the user says "slides", "presentation", "deck"

## Quick Start

```markdown
---
marp: true
theme: default
size: 16:9
paginate: true
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Presentation Title

Presenter Name | Date

---

## Slide Title

- Point one
- Point two
- Point three
```

## Theme Selection

| Content type | Theme | Style |
|-------------|-------|-------|
| Technical / Developer | tech | GitHub-dark, code fonts, `#` headers |
| Business / Corporate | business | White, navy headings, top border |
| Creative / Event | colorful | Pink gradients, rainbow accents |
| Academic / Simple | minimal | White, wide margins, light fonts |
| General / Default | default | Beige, navy text, blue headings |
| Dark preference | dark | Black, cyan/purple glow effects |
| Visual / Creative | gradient | Varying gradients per slide |

## Core Syntax

### Slide Separators

```markdown
---
```

Horizontal rule (`---`) creates a new slide.

### Directives

| Directive | Scope | Example |
|-----------|-------|---------|
| `marp: true` | Global | Enable Marp |
| `theme: default` | Global | Set theme |
| `size: 16:9` | Global | Slide size |
| `paginate: true` | Global | Page numbers |
| `header: 'text'` | Global/local | Header text |
| `footer: 'text'` | Global/local | Footer text |
| `<!-- _class: lead -->` | This slide | Lead/title style |
| `<!-- _paginate: false -->` | This slide | Hide page number |
| `<!-- _backgroundColor: #000 -->` | This slide | Background color |

Underscore `_` = this slide only. Without = all following slides.

### Images

**Background images:**
```markdown
![bg](image.png)              # Full background
![bg right:40%](image.png)   # Right 40%, text on left
![bg left:33%](image.png)    # Left 33%, text on right
![bg fit](image.png)         # Fit within slide
![bg cover](image.png)       # Cover entire slide
```

**Regular images:**
```markdown
![w:600px](image.png)        # Width 600px
![h:400px](image.png)        # Height 400px
![w:600px h:400px](image.png) # Both
```

**Filters:**
```markdown
![bg blur:5px brightness:0.7](background.png)
![grayscale](image.png)
![opacity:0.5](image.png)
```

**Multiple backgrounds (split):**
```markdown
![bg](image1.png)
![bg](image2.png)
```

### Math

```markdown
Inline: $E = mc^2$

Block:
$$
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$
```

### Scoped Styles

```markdown
<style scoped>
h1 { color: red; }
</style>
```

## Best Practices

### Content Rules
- **1 slide = 1 message**
- **3-5 bullet points** per slide (never more than 6)
- **15-25 characters per bullet** (concise)
- **Concise h2 titles** (5-7 words)
- **Generous whitespace** — don't cram

### Structure
1. Title slide (`<!-- _class: lead -->`)
2. Agenda (3-5 items)
3. Content slides
4. Summary / Thank you

### Slide Count Guide
- 5-minute talk: 5-8 slides
- 10-minute talk: 10-15 slides
- 20-minute talk: 15-25 slides

## Presentation Design Philosophy

From scientific-slides best practices (applies to all presentations):

### Visual-First Approach
- Start with visuals, add text as support
- Target: 60-70% visual content, 30-40% text
- Every slide should have a strong visual element

### Typography
- Large fonts: 24-28pt body, 36-44pt titles
- Sans-serif (Arial, Calibri, Helvetica)
- High contrast (7:1 preferred)

### Color
- Modern palette (not default blue/gray)
- 3-5 colors total
- Colorblind-safe (avoid red-green)
- Use color purposefully

### Layout Variety
- Mix full-figure, two-column, text-overlay
- Don't make every slide a bullet list
- Asymmetric compositions are more interesting
- 40-50% white space per slide

## Theme and Template Files

Reference CSS themes and starter templates are available in this skill:

- `themes/theme-default.css` — Beige background, navy text, blue headings
- `themes/theme-dark.css` — Black background, cyan/purple glow
- `themes/theme-minimal.css` — White, wide margins, light fonts
- `themes/theme-business.css` — White, navy headings, top border
- `themes/theme-tech.css` — GitHub-dark, code fonts
- `themes/theme-colorful.css` — Pink gradients, rainbow accents
- `themes/theme-gradient.css` — Varying gradients per slide

Starter templates (copy and customize):

- `templates/template-basic.md`
- `templates/template-dark.md`
- `templates/template-minimal.md`
- `templates/template-business.md`
- `templates/template-tech.md`
- `templates/template-colorful.md`
- `templates/template-gradient.md`

Use `--theme themes/theme-*.css` with marp CLI, or embed the CSS directly in the markdown `<style>` block.

## Rendering

```bash
# PDF output
marp slide.md -o slide.pdf

# HTML output
marp slide.md -o slide.html

# PPTX output
marp slide.md -o slide.pptx

# Watch mode (live preview)
marp -w slide.md

# With custom theme CSS
marp --theme theme.css slide.md -o slide.pdf
```

## Embedded Theme Example (Default)

Themes are embedded directly in the markdown file via `<style>` blocks. This makes the file self-contained — no external CSS files needed.

```markdown
---
marp: true
paginate: true
---

<style>
section {
  background-color: #f8f8f4;
  color: #3a3b5a;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 22px;
}
h1 { font-size: 56px; color: #4f86c6; }
h2 { font-size: 40px; color: #4f86c6; border-bottom: 2px solid #4f86c6; padding-bottom: 8px; }
h3 { font-size: 28px; color: #3a3b5a; }
section.lead { display: flex; flex-direction: column; justify-content: center; text-align: center; }
section.lead h1 { font-size: 64px; }
</style>
```

## Timing and Pacing (for delivery)

- ~1 slide per minute (general rule)
- Introduction: 15-20% of time
- Results/main content: 40-50% of time
- Conclusion: 5% of time
- Practice 3-5 times with timer
- Never skip conclusions if running over
