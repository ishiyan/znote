# Dependencies

All packages required by the skills in this repository. Install in the order shown.

## 1. System packages (requires sudo)

```bash
sudo apt-get install -y \
  poppler-utils \
  tesseract-ocr \
  pandoc \
  imagemagick
```

| Package | Required by |
|---------|-------------|
| `poppler-utils` | `document-to-markdown` — pdf2image uses `pdftoppm`/`pdfinfo` |
| `tesseract-ocr` | `document-to-markdown` — pytesseract OCR for scanned PDFs |
| `pandoc` | General document conversion |
| `imagemagick` | Image manipulation and conversion |

## 2. CLI tools (no sudo required)

### D2 (diagram renderer)

```bash
curl -fsSL https://d2lang.com/install.sh | sh -s --
```

Required by: `visual-authoring/d2`

### Mermaid CLI

```bash
npm install -g @mermaid-js/mermaid-cli
```

Required by: `visual-authoring/mermaid` — renders `.mmd` files to SVG/PNG via `mmdc`

## 3. Python packages (into repo .venv)

```bash
# Activate the venv first
source .venv/bin/activate

# Document-to-markdown
pip install \
  markitdown==0.0.2 \
  pdfplumber==0.11.9 \
  pdf2image==1.17.0 \
  pytesseract==0.3.13 \
  python-pptx==1.0.2 \
  olefile==0.47 \
  python-docx==1.2.0 \
  openpyxl==3.1.5 \
  beautifulsoup4==4.14.3 \
  pillow==12.2.0 \
  lxml==6.1.0 \
  trafilatura==2.0.0 \
  html2text==2024.2.26 \
  oletools==0.60.2

# Scientific visualization
pip install matplotlib seaborn numpy pandas
```

| Package group | Required by |
|---------------|-------------|
| markitdown, pdfplumber, pdf2image, pytesseract, python-pptx, olefile, python-docx, openpyxl, beautifulsoup4, pillow, lxml, trafilatura, html2text, oletools | `document-to-markdown` |
| matplotlib, seaborn, numpy, pandas | `visual-authoring/visualization` |
