# Source Retrieval

Download PDFs, save web pages, and manage retrieved files.

## PDF Download

### From Unpaywall/PMC (open access)

```bash
# Direct PDF download
curl -L -o "author_year_keyword.pdf" "https://pdf-url-from-unpaywall.pdf"
```

### From arXiv

```bash
curl -L -o "author_year_keyword.pdf" "https://arxiv.org/pdf/YYMM.NNNNN.pdf"
```

### Naming Convention

```
{firstauthor}_{year}_{keyword}.pdf
```

Examples: `jurik_1999_jma.pdf`, `smith_2024_adaptive_filters.pdf`

## Web Page Save

For non-PDF sources, save the page content:

1. Use `WebFetch` to get the page
2. Hand to `document-to-markdown` skill for structured extraction
3. Store as markdown with metadata header

## File Organization

```
sources/
├── pdfs/           # Downloaded PDF files
├── bibtex/         # Generated .bib entries (or single sources.bib)
└── pages/          # Saved web pages as markdown
```

## Verification

After download:
- [ ] File is non-empty and valid (PDF opens, markdown renders)
- [ ] BibTeX entry generated with correct metadata
- [ ] Source URL recorded in BibTeX `url` field
- [ ] Access date recorded in BibTeX `urldate` field
