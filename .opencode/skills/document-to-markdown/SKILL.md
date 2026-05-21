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

#### Key conventions

1. **Traders' Tips URL** — Found in `Content-Location` header of the HTML part (part index 1). Always include in the output markdown header and in BibTeX.

2. **Asset filtering** — MHTML contains vendor logos (`vendor_logos/`) and static site images (`static_images/bookArrow.gif`). Skip these; only extract `images/TT-*.gif` chart figures and the article thumbnail.

3. **Output structure** — Place in same directory as source MHTML:
   ```
   tips/
     tips.md              # Main markdown
     assets/              # Chart GIFs (TT-*.gif)
     TradeStation_*.els   # External code files
     MetaStock_*.txt
     WealthLab_*.cs
     RealTest_*.rts
     TradingView_*.pine
     Zorro_*.c
     Python_*.py
   ```

4. **Code extraction** — Each `<pre>` block in the HTML contains code for one platform. Extract both as embedded fenced code blocks in `tips.md` AND as standalone external files. Use language hints: `easylanguage`, `metastock`, `csharp`, `realtest`, `pine`, `c`, `python`.

5. **HTML entity decoding** — Code in `<pre>` blocks uses HTML entities (`&lt;` `&gt;` `&amp;`). Decode these when writing external files. Also watch for `&nbsp;` (non-breaking spaces) in TradingView code — replace with regular spaces.

6. **Platforms without code** — Some platforms (NinjaTrader, Wealth-Lab, NeuroShell Trader) only provide download links or GUI instructions. Include their prose and chart figures but no external code file.

7. **BibTeX** — Always add a `@article{}` entry at the end of `tips.md` with the Traders' Tips URL, author (John F. Ehlers for the underlying article), journal (Technical Analysis of Stocks & Commodities), year, month.

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
- Text from article body appearing above the chart → increase top coordinate
- Bottom axis labels cut off → increase bottom coordinate. **This is the most frequent mistake** — the bottom x-axis date labels and tick marks are easily cut off. Always add at least 150px extra below what appears to be the chart border bottom edge. For figures with captions below, add 250–300px.
- For charts that span most of the page width, use full width (`0` to `w`) and only crop vertically
- Right side of chart cropped → increase right coordinate (don't assume column width matches chart width)
- Left side cropped (especially captions starting with "FIGURE") → decrease left coordinate
- **Include the caption in the crop** — contrary to earlier advice about excluding captions, in practice it's better to include the figure caption text in the image (it provides useful context and avoids ambiguity about whether the full figure was captured). The caption should also appear in the markdown text.

**Multi-column PDF layouts (magazines, journals):**

Technical journals like TASC render with two or three text columns but charts that span partial or full page width. When cropping figures from multi-column PDFs:

1. **Use the chart's border line as the crop guide** — Most TradeStation/charting-platform charts have a visible blue, black, or olive/gold rectangular border. Align the left crop edge to this border. For a typical 2-column TASC layout at 300 DPI (3050×4033 px): charts confined to the right column start at x≈660-780 (varies by article — some have the border at x≈780), while full-width charts spanning both columns start at x≈140.

2. **Adjacent column text bleeds in** — The most common issue is body text from the left column appearing at the left edge of the crop. Fix by moving the left crop coordinate rightward to the chart border's left edge.

3. **Top/bottom text bleed** — Article text or figure captions from above/below the chart leak in. Fix by tightening the top/bottom coordinates to the chart border edges.

4. **Use absolute pixel coordinates** — For rendered pages at known DPI (e.g., 3050×4033 at 300 DPI), absolute pixel coordinates are more reliable than percentages. Document the render dimensions so coordinates can be reproduced.

5. **Include captions in the crop** — Crop the chart including its internal header bar, axis labels, AND the figure caption text below. Also put the caption in the markdown text. This ensures the image is self-contained and visually complete, while the markdown caption remains searchable/editable.

6. **Iterative visual verification is mandatory** — Always use the Read tool to view cropped PNGs after each adjustment. Expect 2-4 iterations per figure to eliminate all text bleed artifacts.

7. **Two charts on the same page** — When a page has two charts stacked vertically (e.g., Figure 2 at top and Figure 3 below), crop each independently. The gap between them is typically 50–100px. Be careful not to let the bottom of Figure N's crop eat into the top border of Figure N+1, and vice versa. Verify each figure separately with the Read tool.

**Best practice: crop generously, let user do final trim.**
When iterating on crops is slow or the user will review the output, always err on the side of including MORE surrounding area (generous margins of 5-10% extra on each side). It is far easier for the user to do a final manual crop than to repeatedly ask for re-crops. Only crop tightly when the figure boundaries are unambiguous (e.g., scanned books with clear border lines detected programmatically).

**Articles with only one figure:** Many TASC articles (especially shorter 2–3 page ones) have a single chart. Don't skip the crop step — still extract it to `assets/figure-01.png` and reference it from the markdown. The chart typically occupies the right column or spans both columns on page 2.

**Charts with two stacked panels (price + oscillator):** Some figures have a price chart panel on top and an indicator/oscillator panel below, all within a single blue border. Treat the entire multi-panel area as one figure — crop from the top of the upper panel border to the bottom of the lower panel border (including axis labels), then include the caption below. Do not split them into separate figures unless they have separate figure numbers.

**"DIGITAL SIGNAL PROCESSING" header bar:** Many Ehlers articles have a section header bar ("DIGITAL SIGNAL PROCESSING") above the chart on page 2. Exclude this from figure crops — start the crop below it (typically y≈200 on a 300 DPI render).

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
