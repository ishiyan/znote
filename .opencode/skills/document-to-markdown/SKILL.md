---
name: document-to-markdown
description: Use this skill whenever the user wants to extract content from a document file or web page into markdown, images, and code. Supports PDF, PPTX, PPT (legacy), DOCX, XLSX, HTML, MHTML, and live web pages (including SPAs). Handles the full pipeline: source detection, text extraction to markdown, image/figure extraction, code listing extraction, and produces a standardized output structure.
---

# Document-to-Markdown Extraction

## Purpose

Extract structured content (markdown text, images, code listings) from any supported source into a standardized output directory.

## Supported Sources

| Source type | Detection method |
|-------------|-----------------|
| PDF | Magic bytes `%PDF-` |
| EPUB | ZIP magic + `mimetype` entry containing `application/epub+zip` |
| PPTX / DOCX / XLSX | ZIP magic + internal paths |
| PPT / DOC (legacy OLE) | OLE2 magic bytes |
| HTML file | `<html` or `<!doctype` in first 500 bytes |
| MHTML file | `From:` or `MIME-Version:` header |
| Live web page (URL) | Starts with `http://` or `https://` |

## Standard Output Structure

```
<output_dir>/
  content.md          # Main markdown content
  summary.md          # Brief summary (title, key topics, source info)
  assets/             # Images, diagrams, figures, photos
    figure-01.png
    photo-author.jpg
  code/               # Extracted code listings (actual source code only)
    listing-01.py
    listing-02.go
  manifest.json       # Metadata about the extraction
```

### Rules

1. **Asset locality** — All images/assets referenced by the content MUST be copied into the output `assets/` directory. Update paths in `content.md` to use relative references (`![](assets/filename.png)`). Never leave references pointing to the original source location. This includes:
   - `<img src="...">` tags
   - Custom viewer components (e.g., `<mb-svg-viewer src="...">`) that embed SVG illustrations
   - Any other tag with a `src` attribute referencing a local asset file
   - For web pages: resolve relative URLs to absolute, then download

2. **SVG color compatibility** — SVGs from web apps often rely on CSS-inherited colors. When copying SVGs, inject a `<style>` block with `prefers-color-scheme` media queries:
   ```xml
   <style>
     svg { stroke: black; fill: black; }
     @media (prefers-color-scheme: dark) {
       svg { stroke: white; fill: white; }
     }
   </style>
   ```
   Skip if the SVG already has both `stroke` and `fill` color attributes explicitly defined.

3. **Math vs. code** — The `code/` directory is for actual source code listings only. Mathematical equations (LaTeX, KaTeX, MathJax) should remain inline in `content.md` using standard LaTeX notation (`$$...$$` for display, `$...$` for inline). **Important:** `pdftotext` cannot extract equations rendered as vector graphics — they appear as blank lines or garbled symbols. Always visually inspect rendered page images for equations and transcribe them manually into LaTeX. Common in technical/academic PDFs.

4. **Document what's lost** — If content cannot be extracted (interactive charts, video, canvas elements), note it in `manifest.json` under `"notes"` and add a placeholder comment in `content.md`:
   ```markdown
   <!-- Interactive chart: [description] — cannot be extracted as static image -->
   ```

## Step 1: Source Detection

### Local files
Use magic bytes to detect format. Do NOT trust file extensions alone. See `reference/format-detection.py` for implementation.

If the file format cannot be determined or the file is corrupted, log the error in `manifest.json` under `"notes"` and skip extraction for that file.

### URLs (web pages)
If the source is a URL:
1. Fetch with markdown conversion first (tools like WebFetch in markdown mode, or `trafilatura`). This works for **static HTML** pages.
2. If the result is mostly empty or just navigation chrome, the page is likely a **Single-Page Application (SPA)** rendered client-side by JavaScript.
3. For SPAs: note that a headless browser (Puppeteer, Playwright) would be needed for full extraction. Extract what's available from the HTTP response.

## Step 2: Content Extraction

### Decision tree

First determine the source type, then apply the matching extraction strategy:

| Source | Strategy | Details |
|--------|----------|---------|
| URL (static HTML) | Fetch + strip boilerplate | See "Web page specifics" below |
| URL (SPA) | Extract what's available | Document limitations in manifest |
| PDF (selectable text) | markitdown + pdfplumber | Text + images (see "PDF Figure Extraction" below) |
| PDF (scanned) | pdftoppm → tesseract → crop | OCR pipeline |
| EPUB | Unzip → OPF spine → html2text | See "EPUB specifics" below |
| PPTX | markitdown + python-pptx | Text + images |
| PPT (legacy) | libreoffice or olefile | Convert first |
| DOCX | markitdown + python-docx | Text + images |
| XLSX/XLSM | openpyxl (data_only=True) | See "Excel specifics" below |
| HTML file | markitdown or beautifulsoup | Strip boilerplate |
| MHTML | Parse MIME parts | Extract HTML + embedded images |

### MHTML Traders' Tips specifics

MHTML files from TASC (Technical Analysis of Stocks & Commodities) Traders' Tips follow a consistent structure. Use this pipeline:

#### Parsing

```python
import email, glob, os

mhtml_files = glob.glob(os.path.join(tips_dir, "*.mhtml"))  # handles whitespace filenames
with open(mhtml_files[0], 'rb') as f:
    msg = email.message_from_bytes(f.read())

for part in msg.walk():
    ct = part.get_content_type()
    loc = part.get("Content-Location", "")
    if ct == "text/html":
        html = part.get_payload(decode=True).decode('utf-8', errors='replace')
    elif ct.startswith("image/"):
        fname = os.path.basename(loc)
        # Skip vendor logos and static images
        if "vendor_logos" not in loc and "static_images" not in loc:
            payload = part.get_payload(decode=True)
            # Save to assets/
```

#### HTML section structure

The HTML uses `div.logoBorder` elements as section headers (containing vendor logo + `<h3>`), with the actual section content (paragraphs, `<pre>` code blocks, images) as **sibling** elements following the div — NOT nested inside it. To parse sections correctly:

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')
logo_divs = soup.find_all('div', class_='logoBorder')

for i, logo_div in enumerate(logo_divs):
    h3 = logo_div.find('h3')
    name = h3.get_text(strip=True) if h3 else f'Section {i}'
    next_div = logo_divs[i+1] if i+1 < len(logo_divs) else None
    
    # Walk siblings until next logoBorder div
    node = logo_div.next_sibling
    while node:
        if node == next_div:
            break
        if hasattr(node, 'name') and node.name:
            if node.name == 'pre':
                # Code block for this platform
                pass
            elif node.name in ('p', 'div'):
                # Prose text or image container
                pass
        node = node.next_sibling
```

#### Key conventions

1. **Traders' Tips URL** — Found in `Content-Location` header of the HTML part (part index 1). Always include in the output markdown header and in BibTeX.

2. **Asset filtering** — MHTML contains vendor logos (`vendor_logos/`) and static site images (`static_images/bookArrow.gif`). Skip these; only extract `images/TT-*.gif` chart figures and the article thumbnail.

3. **Output structure** — Place in same directory as source MHTML:
   ```
   tips/
     tips.md              # Main markdown
     assets/              # Chart GIFs (TT-*.gif)
     code/                # External code files
       DMH.els
       DMH.pine
       DMH.c
       DMH.efs
       DMH.optuma
       DMH.trs
       DMH.xlsm
     ninja-trader/        # Pre-existing NinjaTrader .cs files (if present)
   ```

   **Naming convention:** Use the indicator abbreviation as the base filename with the platform's native extension — e.g., `DMH.els`, `DMH.pine`, `DMH.c`, `DMH.trs`, `DMH.optuma`, `DMH.efs`, `RSIH.els`. Use the platform's native file extension (`.els` for EasyLanguage, `.rtest` for RealTest, `.pine` for Pine Script, `.cs` for C#, `.c` for C/Zorro, `.py` for Python, `.eds` for AIQ EDS, `.efs` for eSignal, `.optuma` for Optuma, `.trs` for TradersStudio). Use `.txt` only for platforms with no specific extension (MetaStock, NeuroShell). When a platform has multiple code blocks that serve different purposes (indicator + strategy), append `_indicator`, `_strategy`, `_test` etc. to the base name.

4. **Code extraction** — Each `<pre>` block in the HTML contains code for one platform. Extract both as embedded fenced code blocks in `tips.md` AND as standalone external files. Use language hints: `easylanguage`, `metastock`, `csharp`, `realtest`, `pine`, `c`, `python`. **Multiple `<pre>` blocks per platform:** Some platforms (notably Zorro) split their code across 2–3 `<pre>` blocks (e.g., helper function + main function + run script). Concatenate them into a single external file in the order they appear, separated by a blank line.

5. **HTML entity decoding** — Code in `<pre>` blocks uses HTML entities (`&lt;` `&gt;` `&amp;`). Decode these when writing external files. Also watch for `&nbsp;` (non-breaking spaces) in TradingView code — replace with regular spaces.

6. **Platforms without code** — Some platforms (NeuroShell Trader, Optuma, thinkorswim, Trade Navigator) only provide download links, shared URLs, or GUI instructions. Include their prose and chart figures but no external code file. **Wealth-Lab** varies by issue — sometimes provides full C# code, sometimes only describes built-in features with no code. **NinjaTrader** sometimes has `.cs` source files in a `ninja-trader/` subfolder alongside the MHTML — if present, link to them from tips.md rather than creating new external files.

7. **BibTeX** — Always add a `@misc{}` entry at the end of `tips.md` with key `traders_tips_YYYY_MM`, author set to `{{Technical Analysis of STOCKS \& COMMODITIES}}`, title including the article name, `howpublished = {online}`, and the Traders' Tips URL.

8. **Figure numbering** — Figures are numbered sequentially across all platforms (FIGURE 1, 2, 3...). Preserve original numbering and captions.

### Web page specifics

**Boilerplate stripping:** Web pages contain navigation, sidebars, headers, footers. To identify article content:
- Look for `<article>`, `<main>`, or `role="main"` elements
- The first `<h1>` usually marks the start of real content
- Repeated elements across pages from the same site are boilerplate
- Use trafilatura as a fallback for main content extraction

**Asset resolution for web pages:**
- Resolve relative URLs (e.g., `assets/photo.jpg`) against the page's base URL
- Download each referenced image/asset into the output `assets/` directory
- Update references in `content.md` to point to local copies

**Interactive/dynamic content (charts, visualizations):**
- JavaScript-rendered charts (D3, Chart.js, Angular/React components) cannot be extracted without a headless browser
- Document their existence in manifest.json and as comments in content.md
- If a headless browser is available, use `page.screenshot()` to capture chart regions

### EPUB specifics

EPUB files are ZIP archives containing XHTML chapters, images, and metadata:

1. **Read `META-INF/container.xml`** to find the OPF file path (usually `OEBPS/package.opf`)
2. **Parse the OPF** to get the spine (reading order) and manifest (id→href map)
3. **Process chapters in spine order** — read each XHTML file, convert to markdown with `html2text` (set `body_width=0` to avoid line wrapping)
4. **Fix image paths** — XHTML references like `../images/fig.jpg` must be rewritten to `assets/fig.jpg`
5. **Extract images** — copy all files from the images directory into `assets/`
6. **Join chapters** with `---` separators into a single `content.md`

Key settings for `html2text`:
- `body_width = 0` (no wrapping)
- `unicode_snob = True` (preserve unicode)
- `images_to_alt = False` (keep image references)

### Excel specifics (XLSX, XLSM, XLS)

Excel workbooks contain multiple sheets with mixed content types. Use `openpyxl` with `data_only=True` to read computed values.

#### Sheet classification

Scan each sheet and classify it before converting:

| Sheet type | Detection heuristic | Conversion strategy |
|---|---|---|
| **Prose/notes** | Few columns, mostly text, sparse cells | Extract as paragraphs |
| **Tabular data** | Clear header row + many uniform data rows | Markdown table (truncated) + full CSV export |
| **Parameter/control** | Scattered labels and values, no uniform rows | Key-value list or indented block |
| **Mixed** | Has both free-form areas and data grids | Split into subsections at the boundary |

**Header detection heuristic:** Scan the first 30 rows. The header row is typically the first row where >50% of cells contain non-empty strings AND the next row has similar column count with data values.

#### CSV export (mandatory for data sheets)

Every sheet with tabular data (>10 rows) MUST be exported as a CSV file in `assets/`:

```
assets/
  sheet-inputpricedata.csv
  sheet-calculations.csv
```

In `content.md`, show a truncated preview (first 20 + last 5 rows as markdown table) and reference the full CSV:

```markdown
*Full data: [assets/sheet-inputpricedata.csv](assets/sheet-inputpricedata.csv) (12,700 rows)*
```

#### Data formatting rules for CSV export

1. **Dates** — Always format as `YYYY-MM-DD`. Never use locale-specific formats (MM/DD/YYYY, DD.MM.YYYY). For datetime values, use `YYYY-MM-DD HH:MM:SS`. Apply this in both CSV and markdown tables.

2. **Floating-point numbers** — Use full precision up to 14 significant digits. Strip trailing zeros only after the significant digits are exhausted. The goal is to preserve the exact value Excel stores (IEEE 754 double = ~15.9 significant digits).
   ```python
   def format_float(val):
       """Format float with full precision, strip trailing zeros."""
       if val == int(val) and abs(val) < 1e15:
           return str(int(val))
       # repr gives 17 significant digits (round-trip safe)
       s = f'{val:.14g}'
       return s
   ```
   Examples:
   - `0.034920867792589204` → `0.034920867792589` (14 significant digits)
   - `1.0` → `1` (integer)
   - `0.005` → `0.005`
   - `209.83` → `209.83`

3. **Integer values** — Format without decimal point (`5652`, not `5652.0`).

4. **Empty cells** — Empty string in CSV, empty cell in markdown table.

#### Large data truncation

If a data table exceeds 100 rows in markdown:
- Show first 20 rows + last 5 rows in `content.md`
- Insert a `| ... |` separator row between them
- Note the total row count
- The full data is always available in the CSV export

#### Embedded charts

Use openpyxl to read chart metadata (title, type, data series references). Document in `content.md` as HTML comments:
```markdown
<!-- Chart: "SPY Price" (LineChart) — data from CalculationsAndCharts!E31:E877 -->
```
If LibreOffice is available, render to PNG: `libreoffice --headless --convert-to png file.xlsx`

#### VBA macros (XLSM only)

- Note presence of macros in `manifest.json` under `"has_vba": true`
- If `oletools` (`olevba`) is available, decompile and save to `code/macros.vba`
- Otherwise, just document their existence

#### Multi-sheet output

Produce a single `content.md` with `## Sheet: Name` sections. Each sheet gets its own heading. The CSV exports in `assets/` provide the full data.


### PDF Figure Extraction (selectable-text PDFs)

`pdfimages` extracts embedded raster images from the PDF stream, but these are often **not** the visible figures/charts. Common problems:

1. **Vector charts** — Most charts in technical journals are vector graphics (paths, lines, text). `pdfimages` cannot extract these at all since they aren't raster images.
2. **Leaked images** — PDFs extracted from larger journals may contain embedded raster images from adjacent pages (e.g., stock photos, illustrations from the previous article) that are invisible in the rendered PDF but stored in its stream.
3. **Background textures** — Colored backgrounds behind code listings or sidebars are extracted as images, not the actual figures.

**Correct approach: render pages then crop figures**

```bash
# 1. Render all pages at 300 DPI
pdftoppm -png -r 300 input.pdf /tmp/pages/page

# 2. Visually inspect rendered pages to locate figures
# 3. Crop figure regions using PIL
```

```python
from PIL import Image

img = Image.open('/tmp/pages/page-01.png')
w, h = img.size
# Crop figure region (percentages determined by visual inspection)
figure = img.crop((0, int(h * 0.37), w, int(h * 0.88)))
figure.save('assets/figure-1.png')
```

**Crop tuning workflow:**
1. Render all pages with `pdftoppm`
2. Open rendered page images to identify figure boundaries (use Read tool to view)
3. Estimate crop coordinates for each figure (prefer absolute pixel values over percentages for precision)
4. Crop and verify — if text leaks in above, increase top; if chart bottom is cut, increase bottom
5. Iterate until the crop captures only the chart + its axis labels (exclude captions — those go in markdown)

**Common crop issues:**
- **Top of chart cropped** (header bar, title, or top border missing) → decrease top coordinate. This is common when two figures are stacked vertically and the dividing point is estimated too low. For TASC pages at 300 DPI (3050×4033 px) with two stacked charts, the gap between them may be only 50–150px. Err on the side of starting 150px higher than where you think the figure begins. Example: if figure 3 content ends at y≈1700, figure 4 likely starts at y≈1550, not y≈1700.
- Text from article body appearing above the chart → increase top coordinate
- Bottom axis labels cut off → increase bottom coordinate. **This is the most frequent mistake** — the bottom x-axis date labels and tick marks are easily cut off. Always add at least 250px extra below what appears to be the chart border bottom edge. For TASC pages at 300 DPI (3050×4033 px), a chart that visually ends at y≈1200 typically needs cropping to y≈1780 to capture the full x-axis date row. When in doubt, add 400px below the apparent chart bottom and trim later. For figures with captions below, add 300–400px. **For scatter/loop plots** (Ehlers Loops, Crocker charts) the data points can extend well below the visible x-axis line — always add 500–600px below the axis line to capture outlier points, negative-quadrant data, and the full red/blue border box closure.
- For charts that span most of the page width, use full width (`0` to `w`) and only crop vertically
- **Right side of chart cropped** → increase right coordinate. Don't assume column width matches chart width. The price scale labels on the right side of trading charts are frequently cut off. Always scan for the actual right border position (see programmatic border detection below). **Left-column charts in 2-column layouts:** When figures are stacked in the left column, the chart box + Y-axis price labels extend well beyond the text column boundary. For a TASC page rendered at 300 DPI (2438×3225 px at this resolution), left-column charts need a right crop boundary of ~1200px (roughly half the page width), not ~880px (the text column width). The Y-axis labels (price scale) add 100–200px to the right of the chart border line.
- Left side cropped (especially captions starting with "FIGURE") → decrease left coordinate
- **Include the caption in the crop** — contrary to earlier advice about excluding captions, in practice it's better to include the figure caption text in the image (it provides useful context and avoids ambiguity about whether the full figure was captured). The caption should also appear in the markdown text.
- **3D surface plots and rotated axis labels** — Charts with 3D perspective (optimization profit surfaces, etc.) have axis labels that extend further right and below than flat 2D charts. The vertical "Net Profit" label on the right Z-axis, diagonal "SigPeriod" / "ROCPeriod" labels at the bottom, and tick marks like "14" / "141" at the base all get clipped if crop boundaries assume a standard rectangular chart. For these figures, add 100–200px extra on both the right and bottom beyond where the chart's visible box border ends. Always verify rotated/diagonal text is fully captured.

**Programmatic border detection (recommended):**

Rather than guessing crop coordinates, scan pixel colors to find the exact chart border positions. Most charting platform screenshots have a colored rectangular border (green, blue, black). Use PIL's `getpixel()` to find these borders precisely:

```python
from PIL import Image

img = Image.open('page-5.png')

# Scan a horizontal row at the chart's vertical midpoint to find the right border
# Look for green border: R<100, G>100, B<100
y_mid = 2000  # adjust to be within the chart area
for x in range(2500, 1000, -1):  # scan from right to left
    r, g, b = img.getpixel((x, y_mid))[:3]
    if g > 100 and r < 100 and b < 100:
        right_edge = x + 6  # include border + tiny margin
        break

# Similarly for left border (scan left to right)
for x in range(0, 1500):
    r, g, b = img.getpixel((x, y_mid))[:3]
    if g > 100 and r < 100 and b < 100:
        left_edge = x - 6
        break
```

Key lessons:
- **Beware off-white page backgrounds** — Scanned/rendered PDFs often have an off-white background (e.g., RGB 250,249,245 → sum=744 instead of 765). If your dark-pixel threshold is too high (e.g., sum<750), every background pixel registers as "dark." Use a threshold of sum<400 or sum<500 for reliable text/border detection. When in doubt, sample a few known-background pixels first to calibrate.
- Scan **inward from the page edges** to find borders — scanning outward from an estimated position may overshoot into adjacent content.
- Charts in the **left column** of a 2-column layout have their right green border at ~x=1484 (at 300 DPI / 3050px width). Don't extend past this or you'll capture Figure 2 from the right column.
- **Full-width charts** (spanning both columns) have their right border at ~x=2234.
- **Single-column charts** (e.g., equity curves) may have borders at intermediate positions (~x=1871).
- After finding the border, add only 4–8px margin. Adding too much captures adjacent text or other figures.

**Multi-column PDF layouts (magazines, journals):**

Technical journals like TASC render with two or three text columns but charts that span partial or full page width. When cropping figures from multi-column PDFs:

1. **Use the chart's border line as the crop guide** — Most TradeStation/charting-platform charts have a visible blue, black, or olive/gold rectangular border. Align the left crop edge to this border. For a typical 2-column TASC layout at 300 DPI (3050×4033 px): charts confined to the right column start at x≈660-780 (varies by article — some have the border at x≈780), while full-width charts spanning both columns start at x≈140.

2. **Adjacent column text bleeds in** — The most common issue is body text from the left column appearing at the left edge of the crop. Fix by moving the left crop coordinate rightward to the chart border's left edge.

3. **Top/bottom text bleed** — Article text or figure captions from above/below the chart leak in. Fix by tightening the top/bottom coordinates to the chart border edges.

4. **Use absolute pixel coordinates** — For rendered pages at known DPI, absolute pixel coordinates are more reliable than percentages. Document the render dimensions so coordinates can be reproduced. Note: page dimensions vary by article — TASC full-page articles render to ~3050×4033 at 300 DPI, but shorter articles (4–5 pages from a larger PDF) may render to ~2438×3225 depending on the PDF's internal page size.

5. **Include captions in the crop** — Crop the chart including its internal header bar, axis labels, AND the figure caption text below. Also put the caption in the markdown text. This ensures the image is self-contained and visually complete, while the markdown caption remains searchable/editable.

6. **Iterative visual verification is mandatory** — Always use the Read tool to view cropped PNGs after each adjustment. Expect 2-4 iterations per figure to eliminate all text bleed artifacts.

7. **Two charts on the same page** — When a page has two charts stacked vertically (e.g., Figure 2 at top and Figure 3 below), crop each independently. The gap between them is typically 50–100px. Be careful not to let the bottom of Figure N's crop eat into the top border of Figure N+1, and vice versa. Verify each figure separately with the Read tool. **Caption placement between figures:** When Figure 1's caption text sits between the two charts, start Figure 2's crop BELOW Figure 1's caption (skip ~100px of caption text). If you start Figure 2's crop immediately after Figure 1's chart bottom border, you'll include Figure 1's caption at the top of Figure 2's image.

   **Finding the dividing line between stacked figures:** Scan dark pixel counts per row across the full page height to find structural landmarks:
   - **Full-width horizontal lines** (dark_count ≈ 255–260 at step=10 sampling) mark chart bottom borders, separator bars, or header bars. These appear as 5–10 consecutive rows with uniformly high counts.
   - **Caption text** (dark_count ≈ 40–130) appears 10–30px below a full-width line.
   - **Background gaps** (dark_count < 20) separate figures — look for 30–50px of near-zero rows between one figure's caption and the next figure's header bar.
   
   Example for a TASC page at 300 DPI (3050×4033 px) with two stacked charts:
   ```
   y=100:  Chart 1 header bar starts
   y=1726-1734: Full-width separator line (dark_count≈259) = Chart 1 bottom border
   y=1755-1790: Caption text "FIGURE 1: ULTIMATE CHANNEL..." (dark_count≈40-130)
   y=1790-1835: Background gap (dark_count<16)
   y=1839-1841: Full-width line (dark_count≈259) = Chart 2 header bar
   y=1850+: Chart 2 content begins
   y=3204-3208: Full-width separator line = Chart 2 bottom border
   y=3233-3270: Caption text "FIGURE 2: ULTIMATE BAND..." (dark_count≈40-130)
   ```
   
   Crop Figure 1 as `(85, 100, 2845, 1800)` — from above header to below caption. Crop Figure 2 as `(85, 1835, 2845, 3280)` — from header bar to below caption. The scanning code:
   
   ```python
   from PIL import Image
   img = Image.open('page-2.png')
   for y in range(0, img.size[1], 1):
       row_dark = 0
       for x in range(100, 2800, 10):
           r, g, b = img.getpixel((x, y))[:3]
           if r + g + b < 500:
               row_dark += 1
       if row_dark > 15:
           print(f"y={y}: dark_count={row_dark}")
   ```

**Best practice: crop generously, let user do final trim.**
When iterating on crops is slow or the user will review the output, always err on the side of including MORE surrounding area (generous margins of 5-10% extra on each side). It is far easier for the user to do a final manual crop than to repeatedly ask for re-crops. Only crop tightly when the figure boundaries are unambiguous (e.g., scanned books with clear border lines detected programmatically).

**Side-by-side figures:** When two small diagrams appear next to each other (e.g., Figures 1 and 2 showing clockwise and counterclockwise conditions), crop them together as a single image rather than trying to separate them. Reference both figure numbers in the markdown and include both captions.

**Magazine PDF pages with ads or legal notices:** TASC PDFs extracted from the full magazine issue sometimes contain unrelated content on intermediate pages (advertisements, legal notices, settlement announcements). Skip these entirely — do not include them in `content.md`. Use `pdftotext` output to identify which pages contain article text vs. unrelated content.

**Articles with only one figure:** Many TASC articles (especially shorter 2–3 page ones) have a single chart. Don't skip the crop step — still extract it to `assets/figure-01.png` and reference it from the markdown. The chart typically occupies the right column or spans both columns on page 2. **Right-column figures** on a 2438px-wide page start at x≈1250 and extend to x≈2400. These often have dark backgrounds (TradeStation dark theme) making border detection harder — use the green/teal outer border line as the guide.

**Multiple figures on one page (right-column stacked):** Some articles place 3 figures vertically stacked in the right column of a single page. Each figure has its own pink/red border box and caption below it. To find exact boundaries, scan for the pink border color (R>180, G<50, B<80) along the left edge (x≈1000–1010 on a 2438px page) to find continuous vertical pink ranges — each range corresponds to one figure's border. Crop each figure from its border top to just above the next figure's border top (to include the caption). Right edge is typically at x≈2243. Example: page with 3 figures yielded pink ranges y=294–591, y=728–1572, y=1797–end.

**Charts with two or three stacked panels (price + oscillator(s)):** Some figures have a price chart panel on top and one or two indicator/oscillator panels below, all within a single red/green/blue/orange border. Treat the entire multi-panel area as one figure — crop from the top of the upper panel border to the bottom of the lowest panel border (including x-axis labels), then include the caption below. Do not split them into separate figures unless they have separate figure numbers. **Three-panel charts** (e.g., price + MAD in red + MADH in yellow, or price + classic RSI + improved RSIH) are common in Ehlers articles comparing indicators — the total height is much larger than expected (~850–1200px on a 2438×3225 page). Always verify all panels are visible before finalizing the crop. Start with a generous vertical range (e.g., y=155 to y=1440) and trim if needed — it's better to include too much than to cut off the bottom panel or caption. **Two-panel charts with left-column text wrapping** (e.g., DMH, MADH articles): the chart spans x≈555–2395 with body text to the left. Start the crop at the chart's colored border left edge to exclude body text.

**"DIGITAL SIGNAL PROCESSING" header bar:** Many Ehlers articles have a section header bar ("DIGITAL SIGNAL PROCESSING") above the chart on page 2. Exclude this from figure crops — start the crop below it (typically y≈155 on a 300 DPI render, though header bottom edge varies from y=90 to y=155 depending on article layout).

**Interview articles (multi-column text, inline figure):** Interview-format articles (e.g., "A Conversation With...") are mostly text with Q&A. Figures may appear inline within a column rather than spanning the full page width. The chart occupies part of one column with text wrapping around it. Crop coordinates must exclude adjacent column text — push the left boundary rightward until no body text bleeds in. Expect 3–4 crop iterations for these inline figures. Use `pdftotext` for the full text since the content is selectable, then format questions in bold italic and answers as regular paragraphs.

**Text wrapping on BOTH sides of a chart:** In some magazine layouts, article body text wraps around the chart on both the left AND right sides. The chart occupies the center of the page and narrow text columns flow on either side. This means you must find the chart box border on ALL four sides, not just left and top/bottom. Common scenario: a chart on page N has a sidebar column to the right (page x≈2500+) with article text like variable descriptions. Cropping at the page right edge (x=2845 or x=3050) will include this sidebar text.

**Finding the chart box border with vertical line scanning:** When the chart border is not a bright color (green/blue) but a thin dark line blending with chart content, simple single-row scanning is unreliable. Instead, count how many y-positions have a dark pixel at each x-coordinate across the full chart height range. The chart box border is a continuous vertical line that appears at the SAME x-position for nearly every y, while chart data (candlesticks, indicators) produces scattered hits at varying x positions.

```python
# Find the chart box left border by counting vertical continuity
candidates = {}
for x in range(200, 900):
    hit_count = 0
    for y in range(110, 1490, 10):  # chart vertical range
        r, g, b = img.getpixel((x, y))[:3]
        if (r + g + b) < 500 and b >= r:  # dark, slightly blue-tinted
            hit_count += 1
    if hit_count > 100:  # present at >70% of sampled rows
        candidates[x] = hit_count
# The x with the highest count is the border line
```

**Chart header bar wider than the chart box:** Some TradeStation charts have a header bar ("@ES - Daily CME L=5,667.50...") that spans the full page width, while the chart box body (with candlesticks and indicators) has its left border indented. For example, the header may start at x=208 but the chart box left border is at x=585. Article body text occupies the column between x=208 and x=585, wrapping to the LEFT of the chart body but below the header bar. When cropping:
- If the chart box left border is far from the header start, crop from the chart box border (not the header) to exclude the text column
- The header text to the left of the chart box border will be lost, but the chart data is preserved
- This is preferable to including article body text in the figure

**Sidebar text on the right side of charts:** Some pages have article sidebar text (e.g., "The variables SU and SD are exceptionally ragged waveforms...") in a narrow column to the RIGHT of the chart. The chart box right border (at the right edge of the price axis) marks where chart content ends and sidebar text begins. On a 3050px-wide TASC page, the chart right border may be at x≈2460 while the sidebar text starts at x≈2519. Crop at the chart box right border + a few pixels margin (e.g., x=2465), NOT at the page edge or at the rightmost pixel of chart price labels. Scan for the continuous vertical right border the same way as the left border.

### TASC Article content.md format

For TASC (Technical Analysis of Stocks & Commodities) articles, the output `content.md` follows this structure:

```markdown
# Article Title

- **Author:** Author Name
- **Publication:** Technical Analysis of STOCKS & COMMODITIES, Volume NN, Month YYYY, pp. X--Y
- **Article URL:** [Article PDF](https://technical.traders.com/archive/article.asp?file=\VNN\CNN\NNNXXXX.pdf)
- **Traders' Tips URL:** [Traders' Tips, Month YYYY](https://www.traders.com/Documentation/FEEDbk_docs/YYYY/MM/TradersTips.html)

---

## Subtitle / Section Header

Body text...

![Figure N: Description](assets/figure-0N.png)
**FIGURE N: TITLE.** Caption text.

## Code Sidebar Title, In EasyLanguage

\`\`\`easylanguage
{ code }
\`\`\`

## Further Reading
## About The Author

---

Availability note linking to Traders.com and Traders' Tips.

---

## BibTeX

\`\`\`bibtex
@article{key,
  ...
}

@misc{traders_tips_YYYY_MM,
  ...
}
\`\`\`
```

Key conventions:
- Use `pdftotext` to extract selectable text; use page images for figure cropping
- Include ALL code sidebars as fenced `easylanguage` blocks under H2 headings
- Mathematical equations → LaTeX (`$$...$$` display, `$...$` inline)
- Figures referenced as `assets/figure-0N.png` (zero-padded)
- BibTeX: `@article` for the main article, `@misc` for the Traders' Tips page

### Format-specific extraction

See reference implementations in the `reference/` subdirectory:
- `reference/format-detection.py` — Magic byte detection
- `reference/extract-pdf.py` — PDF text + image extraction
- `reference/extract-pptx.py` — PPTX text + image extraction
- `reference/extract-ppt-legacy.py` — Legacy PPT via OLE
- `reference/extract-html.py` — HTML content extraction
- `reference/extract-mhtml.py` — MHTML parsing
- `reference/extract-docx.py` — DOCX text + image extraction
- `reference/extract-xlsx.py` — XLSX text extraction

## Step 3: Generate Manifest

```json
{
  "source": "<filepath or URL>",
  "format": "<detected format>",
  "extracted_at": "<ISO 8601 timestamp>",
  "assets_count": 3,
  "code_listings_count": 1,
  "assets": ["figure-01.png", "photo-author.jpg", "diagram.svg"],
  "code": ["listing-01.py"],
  "notes": "<any limitations, lost content, or issues>"
}
```

## Step 4: Batch Conversion

When converting multiple related documents from the same source:

1. **Shared assets** — If the same image (e.g., author photo) appears in multiple documents, duplicate it into each output directory. Each extraction should be self-contained.
2. **Cross-references** — If documents link to each other, preserve the links using relative paths between output directories (e.g., `../sma/content.md`).
3. **Common boilerplate** — When processing multiple pages from the same website, identify the common navigation/chrome once and strip it consistently from all pages.

## Scanned PDF Pipeline

Scanned PDFs contain page images rather than selectable text. They require OCR and manual figure extraction. PDFs may be **single-paged** (one real page per PDF page) or **double-paged** (two real pages side-by-side per PDF page, common in book scans).

### Detection

A PDF is scanned if:
- `pdftotext file.pdf -` produces empty or garbled output
- Pages contain one large image covering the full page (check with `pdfimages -list file.pdf`)
- Text extraction tools (markitdown, pdfplumber) return mostly whitespace

### Pipeline Overview

```
1. Render PDF pages to PNGs (pdftoppm)
2. Split double-paged PNGs into individual page halves (if applicable)
3. OCR each page image (tesseract)
4. Compose markdown from OCR text (manual editing required)
5. Detect and crop figures from page images
6. Update markdown to reference cropped figures
```

### Step 1: Render PDF Pages to PNGs

```bash
# Render at 300 DPI for good OCR quality
pdftoppm -png -r 300 input.pdf images/page
# Produces: images/page-01.png, images/page-02.png, ...
```

### Step 2: Split Double-Paged Scans

Double-paged scans have two real pages laid out horizontally (landscape) on each PDF page. Split each into left and right halves.

**How to detect double-paged layout:**
- Page image is landscape (width > height)
- Visual inspection shows two columns of text with a gutter in the middle
- Each "half" has its own page number/header

Use `reference/extract-scanned-pdf.py` function `split_double_pages()`. Each half-page image will be approximately `width/2 × height` pixels.

**Naming convention:** `ch1-p01.png` (chapter 1, page 1), where page numbers refer to the real book pages, not PDF pages. For a double-paged PDF, PDF page 1 produces `ch1-p01.png` (left) and `ch1-p02.png` (right).

### Step 3: OCR

```bash
# OCR a single page
tesseract images/ch1-p01.png stdout > ocr/ch1_p01.txt

# Batch OCR all pages
for f in images/ch1-p*.png; do
  base=$(basename "$f" .png)
  tesseract "$f" "ocr/${base}" 2>/dev/null
done
```

**OCR quality tips:**
- 300 DPI input gives best results
- Grayscale or binarized images OCR better than color
- tesseract `--psm 6` (assume uniform block of text) works well for single-column pages
- Review OCR output carefully — mathematical formulas, variable names, and code listings are frequently garbled

### Step 4: Compose Markdown

OCR output requires significant manual cleanup:

1. **Structure** — Add markdown headings (`##`, `###`) matching the book's section structure
2. **Code listings** — Must be in fenced code blocks with language tags. Code spanning multiple scanned pages must be combined into a single block. OCR mangles code heavily — verify character-by-character against the scan.
3. **Math** — Convert OCR'd equations to LaTeX notation (`$...$` inline, `$$...$$` display)
4. **Figure references** — Insert `![Figure X.Y - Caption](images/figures/figX-Y.png)` placeholders where figures appear in the text
5. **Page artifacts** — Remove page numbers, headers/footers, and hyphenation at line breaks

**Large file workaround:** Writing very large markdown files with mathematical notation through tool JSON can cause parsing failures. Workaround: write a Python script that generates the markdown file, then execute it with bash.

### Step 5: Detect and Crop Figures

Figures in scanned books are typically charts/graphs enclosed in rectangular borders with a caption line below. The goal is to crop each figure tightly: chart box + caption only, excluding page headers, body text, and surrounding whitespace.

#### Figure anatomy in scanned pages

For typical half-page scans (~1754×2553 pixels at 300 DPI):

| Region | Y range (approx) | Dark pixel count per row |
|--------|-------------------|--------------------------|
| Page header (chapter title, page number) | 0–200 | 100–400 |
| Body text lines | varies | 200–600 |
| Chart box border (thick line) | varies | **800–1500+** |
| Chart interior (gridlines, data) | varies | 200–800 |
| Chart box border (bottom) | varies | **800–1500+** |
| Caption text ("FIGURE X.Y: ...") | 30–80px below bottom border | 200–600 |

#### Border detection algorithm

The key insight: chart box borders are thick horizontal lines that produce rows with a very high count of dark pixels (brightness < 128). Body text and gridlines produce fewer dark pixels per row.

```python
# Pseudocode for border detection
1. Convert image to grayscale
2. For each row y, count pixels where brightness < 128
3. Find rows with dark_pixel_count > BORDER_THRESHOLD
   - Use 800 for most charts
   - Use 1200+ for charts with dense gridlines (e.g., frequency response plots)
4. Group consecutive high-count rows into border bands
5. The first band = top border, last band = bottom border
6. Scan 30-100px below bottom border for caption text (rows with 200-600 dark pixels)
7. Crop: x=150 to x=width-150 (margins), y=top_border-15 to y=last_caption_line+15
```

#### Practical approach

Rather than fully automating detection (which is fragile), use a semi-automated approach:

1. **Run the border analyzer** (`reference/extract-scanned-pdf.py` function `analyze_borders()`) on each page image to get dark pixel counts per row
2. **Visually inspect** the output to identify border positions and caption locations
3. **Build a crop spec** — a list of `(source_file, output_file, left, top, right, bottom)` tuples with precise coordinates
4. **Run the cropper** to batch-crop all figures

See `reference/extract-scanned-pdf.py` for the complete implementation with `analyze_borders()`, `crop_figures()`, and `split_double_pages()` functions.

#### Common pitfalls

- **Dense gridlines** (frequency response charts, etc.) produce 800+ dark pixels on every row inside the chart, making it look like every row is a border. Raise the threshold to 1200+ for these charts.
- **Multi-line captions** — Some figures have two-line captions. Scan further below the bottom border to catch the second line.
- **Body text below caption** — Text paragraphs 100+ pixels below the bottom border may look like a second caption line (200-600 dark pixels). Caption detection must stop after 1-2 text lines with a gap >25 blank rows signaling end-of-caption. Do NOT use large `max_search` values that sweep into body text, Key Points sections, or subsequent code listings.
- **Multiple figures per page** — A single half-page may contain two figures stacked vertically. Look for two separate pairs of top/bottom borders.
- **Code listings vs. charts on same page** — Pages often contain the tail of a code listing (bordered box with monospace text) followed by a chart figure, or vice versa. Both produce high dark-pixel border rows. Use the OCR text or caption position to distinguish which border pair belongs to the target figure. A code listing's caption says "(Continued)" or "Code to Compute..." while a chart figure's caption describes visual output.
- **Multi-panel charts** — Some charts have 3-4 stacked panels (price + indicators) sharing a single border box. Internal divider lines between panels also register as high-dark-pixel rows. The full chart includes ALL panels — crop from the outermost top border to the outermost bottom border.
- **Small schematics/diagrams** — Not all figures are large boxed charts. Schematic diagrams (filter block diagrams, phasor diagrams) may be small (300-500px tall) with thinner borders (600-700 dark pixels). Use a lower threshold for these.

#### Iterative refinement workflow

Automated border detection rarely works perfectly on the first pass across an entire book. The recommended workflow is:

1. **First pass** — Run automated cropper on all figures with best-guess thresholds
2. **Visual review** — Inspect every cropped figure (open the PNGs or use the Read tool to render them). Categorize issues:
   - "Too much above" — crop started too early (e.g., included preceding code listing)
   - "Too much below" — caption detection was too greedy (included body text, Key Points, next listing)
   - "Wrong figure entirely" — border detection locked onto the wrong region
   - "Cut off" — bottom of chart missing (multi-panel chart not fully captured)
3. **Fix pass** — For each problematic figure, analyze the specific page's dark-pixel profile and apply manual crop coordinates or adjusted thresholds
4. **Re-verify** — Spot-check fixed figures visually

Expect 30-50% of figures to need manual correction on the first pass, especially in chapters with mixed content (code listings adjacent to charts).

### Step 6: Update Markdown References

After cropping, update all `![...]()` references in the markdown to point to the cropped figures:

```markdown
# Before (full half-page scan)
![Figure 1.1 - Caption](images/ch1-p04.png)

# After (cropped figure)
![Figure 1.1 - Caption](images/figures/fig1-1.png)
```

Also check for:
- **Missing figure references** — The text mentions "Figure X.Y" but no `![...]` image tag exists. Add one after the paragraph that introduces the figure.
- **Duplicate source references** — Two different figures pointing to the same source image (e.g., both Fig 2.3 and Fig 2.2 pointing to `ch2-p05.png`). Each figure should point to its own cropped file.

## Limitations by Source Type

| Source | What's extractable | What's NOT extractable |
|--------|-------------------|----------------------|
| PDF | Text, embedded images, tables | Scanned text (needs OCR pipeline — see "Scanned PDF Pipeline" section) |
| EPUB | Text, images, code (indented blocks), metadata | DRM-protected content, embedded fonts, audio/video |
| XLSX/XLSM | Cell data, formulas (computed values), sheet structure, chart metadata | Charts as images (needs LibreOffice), VBA source (needs oletools), conditional formatting, pivot tables |
| PPTX | Text, embedded images, speaker notes | Animations, transitions, linked media |
| PPT (legacy) | Images (via OLE), rough text | Precise text layout (use libreoffice conversion) |
| HTML (static) | Text, images, code blocks | — |
| HTML (SPA) | Text if server-rendered | Client-rendered content, interactive charts |
| MHTML | Text, embedded images | External resources not included in archive |
| DOCX | Text, embedded images | Complex layouts, embedded OLE objects |
| XLSX | Cell data as markdown tables | Charts, pivot tables, macros |

## Anti-Patterns (Common Mistakes)

These pitfalls were identified from failed extraction attempts:

1. **Don't write extraction scripts** — Use the available tools directly (WebFetch, Read, Write). Writing Python scripts to `requests.get()` a URL adds complexity and fails on SPAs. The agent already has tools that handle HTTP fetching and markdown conversion.

2. **Don't install headless browsers** — Playwright/Puppeteer require system-level installation and are overkill for most extractions. If WebFetch in markdown mode returns useful content, use it. Document what's missing rather than attempting fragile browser automation.

3. **Watch for backslash corruption** — When LaTeX content passes through Python string handling, `\t` becomes tab, `\n` becomes newline, `\b` becomes backspace. If writing any intermediary scripts, always use raw strings (`r"..."`) or read/write in binary mode. Prefer direct tool-based extraction to avoid this entirely.

4. **Strip rendering artifacts** — SPAs often leave DOM artifacts in extracted text (trailing `#` from anchor links, navigation breadcrumbs, repeated section IDs). Clean these in the final `content.md`.

5. **Don't create empty directories** — If there are no code listings, omit the `code/` directory. If there are no downloadable assets, omit `assets/`. Empty scaffolding adds noise.

6. **Don't use placeholders for missing content** — Instead of `[Chart: screenshot needed]` or `![](assets/placeholder.png)`, use HTML comments that describe what was there: `<!-- Interactive chart: step response for L=5,10,20 -->`. Placeholders look like broken content; comments are invisible to readers.

7. **Prioritize content over tooling** — The goal is readable markdown. Spending time on SVG color-scheme fixes, asset post-processing pipelines, or screenshot checklists is wasted effort if the core text content is corrupted or poorly formatted.

## Required Tools

### System packages (optional, enhance quality)
```bash
sudo apt install poppler-utils tesseract-ocr pandoc libreoffice
```

| Package | Purpose |
|---------|---------|
| `poppler-utils` | PDF rendering (`pdftotext`, `pdftoppm`, `pdfimages`) |
| `tesseract-ocr` | OCR for scanned/image-based PDFs |
| `pandoc` | Universal document converter |
| `libreoffice` | Legacy .ppt/.doc/.xls → modern format conversion |

### Python packages
See `reference/requirements.txt` for the full list.
