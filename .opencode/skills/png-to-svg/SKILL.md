---
name: png-to-svg
description: Use this skill when the user wants to convert a PNG (or other raster) image into a clean, hand-crafted SVG. Best suited for diagrams, charts, technical figures, and line art — not photographs. Handles color remapping for light/dark theme compatibility, transparent backgrounds, and produces semantic SVG with proper text elements, paths, and markers.
---

# PNG-to-SVG Conversion

## Purpose

Convert raster images (PNG, JPG) of diagrams, charts, and technical figures into clean, hand-crafted SVG files that are:
- Transparent-background
- Light/dark theme compatible
- Semantically structured (real `<text>`, `<path>`, `<line>` elements)
- Scalable without quality loss

## When to Use

- Technical diagrams with lines, curves, arrows, and labels
- Chart figures from papers/books
- Simple graphics with distinct colored elements
- Any figure that needs to work on both light and dark backgrounds

## When NOT to Use

- Photographs (use embedded `<image>` instead)
- Highly complex illustrations with gradients/textures
- Screenshots of UIs (keep as raster)

## Workflow

### Step 1: Analyze the Source Image

Read the PNG and identify:
1. **Elements**: curves, lines, arrows, shapes, text labels, angle arcs, axes
2. **Colors**: list each distinct color and its semantic role
3. **Layout**: approximate coordinates, proportions, spatial relationships
4. **Text**: all labels, subscripts, superscripts, mathematical notation

### Step 2: Plan Color Remapping

For light/dark compatibility:

| Original Color | Problem on Dark BG? | Replacement |
|---------------|---------------------|-------------|
| Black | Invisible | Green `#22c55e` or white-safe color |
| White | Invisible on light | Remove (transparent) or contextual |
| Dark gray | Low contrast | Lighten or use green/teal |
| Red | Usually fine | Keep `#dc2626` |
| Blue | Usually fine | Keep `#2563eb` |
| Other | Assess contrast | Choose colors with ≥4.5:1 ratio on both |

**Rules:**
- Background MUST be transparent (no `<rect>` fill for background)
- Black lines/text → green (`#22c55e`) or another high-contrast color the user specifies
- Keep red, blue, and other saturated colors as-is (they work on both backgrounds)
- If the user specifies a color mapping, use that instead

### Step 3: Determine SVG Canvas

- Set `viewBox` to encompass the figure with small padding
- Typical: `viewBox="0 0 700 560"` for landscape diagrams
- Use `fill="none"` on the root `<svg>` element

### Step 4: Build SVG Structure

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 W H" fill="none">
  <defs>
    <!-- Arrow markers, gradients, patterns -->
  </defs>

  <!-- Group by semantic layer -->
  <!-- 1. Main curves/shapes -->
  <!-- 2. Annotation lines (arrows, dimension lines) -->
  <!-- 3. Text labels -->
</svg>
```

### Step 5: Recreate Elements

#### Curves
- Use `<path>` with cubic Bezier (`C`) or quadratic (`Q`) commands
- Estimate control points from visual curvature
- Set `stroke-width`, `stroke-linecap="round"`, `fill="none"`

#### Straight Lines & Arrows
- Use `<line>` with `marker-start`/`marker-end` for arrowheads
- Define arrow markers in `<defs>`:

```xml
<marker id="arrow-COLOR" markerWidth="10" markerHeight="7"
        refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#COLOR"/>
</marker>
```

#### Text Labels
- Use `<text>` elements with `font-family="serif"` (for math/technical) or `sans-serif`
- Subscripts: position a smaller `<text>` slightly below and right
- Superscripts: position slightly above and right
- Unicode for Greek: φ=`&#x03C6;`, ℓ=`&#x2113;`, α=`&#x03B1;`, etc.
- Match the `fill` color to the element the label belongs to

#### Arcs (angle indicators)
- Use `<path>` with arc command: `A rx ry rotation large-arc-flag sweep-flag x y`

#### Shapes
- `<rect>`, `<circle>`, `<ellipse>` as appropriate
- For complex shapes, use `<path>`

### Step 6: Validate

Checklist:
- [ ] No white/black background rectangle
- [ ] All text is `<text>` elements (not traced paths)
- [ ] Arrow markers defined and referenced correctly
- [ ] Colors match the remapping plan
- [ ] `viewBox` proportions match the original figure's aspect ratio
- [ ] File opens correctly in a browser (if tools available to check)

## Output

Write the SVG to the same directory as the source PNG, with the same base filename but `.svg` extension.

## Example Prompt Formulations

Good prompts for invoking this skill:

- "Convert `path/to/figure.png` to SVG with transparent background, green instead of black"
- "Recreate this diagram as clean SVG, dark-mode compatible"
- "Turn this chart PNG into a hand-crafted SVG"

## Color Palette Reference

Safe colors for both light and dark backgrounds:

| Color | Hex | Use for |
|-------|-----|---------|
| Green | `#22c55e` | Primary lines (replaces black) |
| Red | `#dc2626` | Secondary/highlight |
| Blue | `#2563eb` | Tertiary |
| Amber | `#f59e0b` | Warning/accent |
| Purple | `#8b5cf6` | Additional series |
| Teal | `#14b8a6` | Alternative to green |
| Dark red | `#991b1b` | Emphasis arrows |
| Coral | `#f97316` | Warm accent |
