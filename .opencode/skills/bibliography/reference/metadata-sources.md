# Metadata Sources

APIs for looking up publication metadata by identifier (DOI, PMID, arXiv ID).

## CrossRef API

**Primary source for DOI resolution and journal article metadata.**

- Endpoint: `https://api.crossref.org/works/{DOI}`
- No API key required (polite pool: add `mailto` parameter for better rate limits)
- Returns: title, authors, journal, volume, issue, pages, publisher, dates, references

**Example**:
```
GET https://api.crossref.org/works/10.1038/s41586-021-03819-2
```

**Fields returned**: author, title, container-title (journal), volume, issue, page, published-print, DOI, URL, publisher, subject, reference-count, is-referenced-by-count (citations).

**Use for**: Any publication with a DOI. Most reliable metadata source.

---

## PubMed E-utilities

**Biomedical and life sciences literature (35M+ citations).**

- ESearch: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
- EFetch: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`
- Free; API key recommended for >3 requests/second

**Search by PMID**:
```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=34265844&rettype=xml
```

**Fields returned**: authors, title, journal, volume, issue, pages, DOI, PMID, PMCID, abstract, MeSH terms, publication date.

**Use for**: Biomedical papers, especially when you have a PMID.

---

## arXiv API

**Preprints in physics, mathematics, CS, quantitative biology, statistics.**

- Endpoint: `http://export.arxiv.org/api/query`
- Free, no key required

**Search by ID**:
```
GET http://export.arxiv.org/api/query?id_list=2103.14030
```

**Fields returned**: title, authors, abstract, categories, published date, updated date, DOI (if linked to published version).

**Use for**: Preprints, especially in ML/AI, physics, math.

---

## DataCite API

**Datasets, software, and non-traditional scholarly outputs with DOIs.**

- Endpoint: `https://api.datacite.org/dois/{DOI}`
- Free, no key required

**Use for**: Zenodo datasets, software DOIs, research data.

---

## Google Books API

**Book metadata and preview availability.**

- Endpoint: `https://www.googleapis.com/books/v1/volumes?q=isbn:{ISBN}`
- Or search by title: `https://www.googleapis.com/books/v1/volumes?q=intitle:{title}+inauthor:{author}`
- Free tier: 1000 requests/day without API key

**Fields returned**: title, authors, publisher, published date, ISBN, page count, preview link, info link.

**Use for**: Finding Google Books URLs for book entries. The `volumeInfo.previewLink` or `volumeInfo.infoLink` gives the stable URL.

**Stable URL format**: `https://books.google.com/books?id={VOLUME_ID}`

---

## Lookup Strategy

Given an identifier, use this priority:

| Identifier | Primary source | Fallback |
|---|---|---|
| DOI | CrossRef | DataCite |
| PMID | PubMed E-utilities | CrossRef (via DOI if available) |
| arXiv ID | arXiv API | CrossRef (if published version exists) |
| ISBN | Google Books | CrossRef (some books have DOIs) |
| URL only | Fetch page, extract metadata | Manual entry |

## Rate Limits

| Source | Free tier | With key |
|---|---|---|
| CrossRef | 50 req/sec (polite pool with email) | Same |
| PubMed | 3 req/sec | 10 req/sec |
| arXiv | 1 req/3sec | Same |
| Google Books | ~1000/day | Higher |
| DataCite | Generous | Same |
