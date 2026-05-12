# DOI / arXiv Direct Retrieval

When the user provides an exact DOI or arXiv ID, retrieve metadata, abstract, BibTeX, and PDF link directly.

## DOI Resolution

### Step 1: Get metadata from Crossref

```
GET https://api.crossref.org/works/{DOI}
```

Returns: title, authors, journal, year, volume, issue, pages, abstract, references, type.

### Step 2: Get open access PDF link from Unpaywall

```
GET https://api.unpaywall.org/v2/{DOI}?email=user@example.com
```

Returns: `best_oa_location.url_for_pdf` (direct PDF link if available).

### Step 3: Get citation context from Semantic Scholar

```
GET https://api.semanticscholar.org/graph/v1/paper/DOI:{DOI}?fields=title,authors,year,abstract,citationCount,references,tldr
```

Returns: abstract, TLDR, citation count, references.

### Step 4: Generate BibTeX

Use Crossref metadata to construct BibTeX entry. See [retrieval/bibtex-templates.md](../retrieval/bibtex-templates.md) for templates.

### Step 5: Download PDF (if available)

If Unpaywall returns a PDF URL, download it:
```bash
curl -L -o paper.pdf "https://..."
```

## arXiv ID Resolution

### Step 1: Get metadata from arXiv API

```
GET http://export.arxiv.org/api/query?id_list={ARXIV_ID}
```

Returns Atom XML with: title, authors, abstract, categories, published date, PDF link.

### Step 2: Download PDF

arXiv always provides free PDF:
```
https://arxiv.org/pdf/{ARXIV_ID}.pdf
```

### Step 3: Check if published (optional)

Query Semantic Scholar to see if the preprint has a published DOI:
```
GET https://api.semanticscholar.org/graph/v1/paper/ARXIV:{ARXIV_ID}?fields=externalIds
```

If `externalIds.DOI` exists, the paper has been published — fetch the published version's metadata too.

### Step 4: Generate BibTeX

```bibtex
@misc{authorYYYYkeyword,
  author       = {First Last and First Last},
  title        = {Paper Title},
  year         = {2024},
  eprint       = {2401.12345},
  archiveprefix = {arXiv},
  primaryclass = {cs.AI},
  url          = {https://arxiv.org/abs/2401.12345}
}
```

## PMID Resolution

1. Convert PMID → DOI using PMC ID Converter:
   ```
   GET https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={PMID}&format=json
   ```
2. Then follow the DOI workflow above.

## Output Format

For every resolved identifier, deliver:

1. **Metadata** — title, authors, year, journal/venue, abstract
2. **BibTeX entry** — ready to paste into `.bib` file
3. **PDF link** — direct download URL (or "not available as open access")
4. **Citation count** — from Semantic Scholar (if available)
5. **Related papers** — 2-3 most relevant (from Semantic Scholar recommendations)
