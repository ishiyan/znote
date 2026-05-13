# Dependencies

All packages required by the skills in this repository. Install in the order shown.

Install required Python version using `pyenv install 3.14.3`.
If you get installation errors, try to install support packages:

```bash
sudo apt install zlib1g-dev libssl-dev libbz2-dev liblzma-dev libreadline-dev libsqlite3-dev libffi-dev
```

To managing multiple versions:

```bash
# List all installed versions
pyenv versions

# Set global default
pyenv global 3.14.3

# Set version for a specific project directory
cd /path/to/project
pyenv local 3.13.12    # creates a .python-version file

# Use a version only in the current shell
pyenv shell 3.13.12
```

Priority order: `shell` > `local` > `global` > system.

Create a virtual environment:

```bash
pyenv versions
python --version
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Do subsequent installations into this venv.

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
sudo npm install -g @mermaid-js/mermaid-cli
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
