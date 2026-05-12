# draw.io Diagrams

Programmatic editing of `.drawio` XML files. Use when the user wants diagrams editable in draw.io desktop/web, or needs AWS architecture icons.

## Prerequisites

```bash
# draw.io CLI (for PNG/SVG export)
# macOS: brew install --cask drawio
# Or use the desktop app's export function
```

## Basic Rules

- Edit only `.drawio` files (XML)
- Never directly edit `.drawio.png` files
- Render to PNG/SVG via CLI or pre-commit hook

## Conversion Commands

```bash
# Export to PNG (2x scale, transparent background)
drawio -x -f png -s 2 -t -o output.drawio.png input.drawio

# Export to SVG
drawio -x -f svg -o output.svg input.drawio
```

| Option | Description |
|--------|-------------|
| `-x` | Export mode |
| `-f png/svg` | Output format |
| `-s 2` | 2x scale (high resolution) |
| `-t` | Transparent background |
| `-o` | Output file path |

## XML Structure

### Font Settings

```xml
<mxGraphModel defaultFontFamily="Arial" ...>
```

Per-element: `style="text;html=1;fontSize=18;fontFamily=Arial;"`

### Coordinate System

- `x`: Position from left
- `y`: Position from top
- `width`: Element width
- `height`: Element height
- Element center: `y + (height / 2)`

### Layout Tips

- Remove `background="#ffffff"` for transparent backgrounds
- Use 1.5x standard font size (~18px) for PDF readability
- Internal elements: at least 30px margin from frame boundary
- Arrows placed at back (position in XML right after Title element)

### Arrow Connections

For text elements, use explicit coordinates (exitX/exitY don't work):

```xml
<mxCell id="arrow" style="edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="200" y="100" as="sourcePoint"/>
    <mxPoint x="400" y="100" as="targetPoint"/>
  </mxGeometry>
</mxCell>
```

## Design Principles

1. **Clarity**: Simple, visually clean diagrams
2. **Consistency**: Unified colors, fonts, icon sizes, line thickness
3. **Accuracy**: Don't sacrifice accuracy for simplification
4. **Labels**: Label all elements, use arrows for direction
5. **Accessibility**: Sufficient color contrast, patterns in addition to colors
6. **Progressive disclosure**: Separate complex systems into staged diagrams

## AWS Icons

Use official draw.io AWS icon library (`mxgraph.aws4.*`):

```bash
# Search for AWS icons (if script available)
python scripts/find_aws_icon.py ec2
python scripts/find_aws_icon.py lambda
```

## Reference Files

- `references/layout-guidelines.md` — Detailed layout and spacing rules
- `references/aws-icons.md` — Complete AWS icon library reference

## Checklist

- [ ] No background color set (transparent)
- [ ] Font size appropriate (~18px+)
- [ ] Arrows at back layer
- [ ] Arrows not overlapping labels
- [ ] Internal elements not overflowing frames (30px+ margin)
- [ ] AWS icons are latest version (`mxgraph.aws4.*`)
- [ ] PNG conversion verified visually
