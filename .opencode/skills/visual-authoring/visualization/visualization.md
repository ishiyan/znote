# Scientific Visualization

Create publication-ready figures using matplotlib and seaborn. For journal submission with multi-panel layouts, error bars, significance annotations, colorblind-safe palettes, and specific journal formatting.

## Prerequisites

```bash
pip install matplotlib seaborn numpy pandas
```

## When to Use

- Creating plots for scientific manuscripts
- Preparing figures for journal submission (Nature, Science, Cell, PLOS)
- Making multi-panel figures with consistent styling
- Colorblind-friendly, accessible visualizations
- Data-driven charts (scatter, line, bar, heatmap, violin, etc.)

**Do NOT use for structural/relational diagrams** — use Mermaid or D2 instead.

## Quick Start

```python
import matplotlib.pyplot as plt
import numpy as np

# Publication style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'],
    'font.size': 8,
    'axes.labelsize': 9,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Single-column figure (Nature: 89mm = 3.5 inches)
fig, ax = plt.subplots(figsize=(3.5, 2.5))
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), label='Signal')
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('Amplitude (mV)')
ax.legend(frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.savefig('figure1.pdf')
plt.savefig('figure1.png', dpi=300)
```

## Color Palettes (Colorblind-Safe)

### Okabe-Ito (Recommended for categorical data)

```python
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=okabe_ito)
```

### Seaborn Colorblind Palette

```python
import seaborn as sns
sns.set_palette('colorblind')
```

### Continuous Data

- Perceptually uniform: `viridis`, `plasma`, `cividis`
- Diverging (colorblind-safe): `PuOr`, `RdBu`, `BrBG`
- **Never use**: `jet`, `rainbow`

### Rules

- Always test in grayscale
- Add redundant encoding (line styles, markers) beyond color
- Max ~8 colors per plot

## Figure Dimensions by Journal

| Journal | Single column | Double column |
|---------|--------------|---------------|
| Nature | 89 mm (3.5 in) | 183 mm (7.2 in) |
| Science | 55 mm (2.2 in) | 175 mm (6.9 in) |
| Cell | 85 mm (3.3 in) | 178 mm (7.0 in) |

## Resolution and Format

| Content type | DPI | Format |
|-------------|-----|--------|
| Line art (graphs) | 600-1200 | PDF, EPS, SVG (vector preferred) |
| Photos / microscopy | 300-600 | TIFF, PNG |
| Combination | 300+ | PDF or TIFF |

**Never use JPEG** for scientific figures (lossy compression creates artifacts).

## Multi-Panel Figures

```python
from string import ascii_uppercase

fig = plt.figure(figsize=(7, 4))
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.4)

axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]

# Add panel labels
for i, ax in enumerate(axes):
    ax.text(-0.15, 1.05, ascii_uppercase[i], transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top')

plt.savefig('figure_panels.pdf')
```

## Seaborn for Statistical Plots

```python
import seaborn as sns

# Configure for publication
sns.set_theme(style='ticks', context='paper', font_scale=1.1)
sns.set_palette('colorblind')

# Box + strip plot (show individual data points)
fig, ax = plt.subplots(figsize=(3.5, 3))
sns.boxplot(data=df, x='treatment', y='response', palette='Set2', ax=ax)
sns.stripplot(data=df, x='treatment', y='response',
              color='black', alpha=0.3, size=3, ax=ax)
ax.set_ylabel('Response (μM)')
sns.despine()

# Line plot with confidence intervals
fig, ax = plt.subplots(figsize=(5, 3))
sns.lineplot(data=df, x='time', y='measurement',
             hue='treatment', errorbar=('ci', 95), markers=True, ax=ax)
sns.despine()

# Heatmap (correlation matrix)
fig, ax = plt.subplots(figsize=(5, 4))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, square=True, ax=ax)
```

## Statistical Rigor

Always include:
- **Error bars** (specify SD, SEM, or CI in caption)
- **Sample size** (n) in figure or caption
- **Significance markers** (*, **, ***)
- **Individual data points** when possible

```python
# Show individual points with summary statistics
ax.scatter(x_jittered, individual_points, alpha=0.4, s=8)
ax.errorbar(x, means, yerr=sems, fmt='o', capsize=3)

# Significance annotation
ax.text(1.5, max_y * 1.1, '***', ha='center', fontsize=8)
```

## Typography

- Sans-serif: Arial, Helvetica, Calibri
- Minimum at final print size:
  - Axis labels: 7-9 pt
  - Tick labels: 6-8 pt
  - Panel labels: 8-12 pt (bold)
- Sentence case: "Time (hours)" not "TIME (HOURS)"
- Always include units in parentheses

## Common Pitfalls

1. Font too small at final print size
2. JPEG format (use PDF/PNG/TIFF)
3. Red-green color combinations (~8% of males can't distinguish)
4. Missing units on axes
5. 3D effects (distort perception)
6. Truncated y-axis without justification
7. Missing error bars
8. `jet`/`rainbow` colormaps
9. Inconsistent styling across figures in same manuscript
10. Chart junk (unnecessary gridlines, shadows, decorations)

## Reference Files

Style presets (copy into project or use with `plt.style.use()`):

- `assets/publication.mplstyle` — Journal submission defaults
- `assets/nature.mplstyle` — Nature-specific formatting
- `assets/presentation.mplstyle` — Large fonts for slides/posters
- `assets/color_palettes.py` — Named palette definitions

Helper scripts:

- `scripts/figure_export.py` — Batch export figures in multiple formats/DPIs
- `scripts/style_presets.py` — Apply journal-specific presets programmatically

## Final Checklist

- [ ] Resolution meets journal requirements (300+ DPI)
- [ ] Vector format for plots (PDF/EPS/SVG)
- [ ] Figure size matches journal column width
- [ ] All text readable at final size (≥6 pt)
- [ ] Colors colorblind-friendly (tested in grayscale)
- [ ] All axes labeled with units
- [ ] Error bars present with type stated in caption
- [ ] Panel labels (A, B, C) present and consistent
- [ ] No chart junk or 3D effects
- [ ] Fonts consistent across all figures
- [ ] Statistical significance clearly marked
- [ ] Legend complete and clear
