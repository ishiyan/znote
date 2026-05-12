# Academic Search

Search academic paper databases for research papers, preprints, and scholarly articles.

## Database Selection

| User needs... | Primary | Also try |
|---------------|---------|----------|
| Papers on any topic | OpenAlex, Semantic Scholar | Crossref |
| Physics/math/CS preprints | arXiv | Semantic Scholar |
| Biomedical papers | PubMed | PMC, Semantic Scholar |
| Biology preprints | bioRxiv | Semantic Scholar |
| Health preprints | medRxiv | Semantic Scholar |
| Specific paper by DOI | Crossref | Unpaywall, Semantic Scholar |
| Open access PDF | Unpaywall | PMC |
| Citation graph | Semantic Scholar | OpenAlex |
| Author's publications | Semantic Scholar | OpenAlex |
| Full text | PMC (biomedical) | Unpaywall (OA link) |

### Cross-Database Strategies

| Goal | Databases |
|------|-----------|
| Comprehensive lit search | OpenAlex + Semantic Scholar + arXiv |
| Find + read paper | Crossref (find) → Unpaywall (OA link) → download |
| Everything about a paper | Crossref + Semantic Scholar + Unpaywall |
| Author overview | Semantic Scholar + OpenAlex |

## Common Identifier Formats

| ID type | Format | Example | Accepted by |
|---------|--------|---------|-------------|
| DOI | `10.xxxx/xxxxx` | `10.1038/nature12373` | All |
| PMID | Integer | `34567890` | PubMed, PMC, Semantic Scholar |
| PMCID | `PMC` + digits | `PMC7029759` | PMC |
| arXiv ID | `YYMM.NNNNN` | `2103.15348` | arXiv, Semantic Scholar |
| OpenAlex ID | `W` + digits | `W2741809807` | OpenAlex |
| ORCID | `0000-XXXX-XXXX-XXXX` | `0000-0001-6187-6610` | OpenAlex, Crossref |

**Semantic Scholar** accepts DOI, PMID, arXiv ID via prefixes: `DOI:10.1038/...`, `PMID:34567890`, `ARXIV:2103.15348`.

## Search Workflow

1. **Identify query type** — topic search, author search, specific paper, or citation exploration
2. **Select 2-3 databases** from the table above
3. **Read the database reference** in `databases/` before making API calls
4. **Query in parallel** where possible (respect rate limits)
5. **Deduplicate** results across databases (match on DOI)
6. **Generate BibTeX** for each unique result (see retrieval/bibtex-templates.md)
7. **Check for open access** via Unpaywall if PDFs needed

## Rate Limits

| Database | Limit | Notes |
|----------|-------|-------|
| arXiv | 1 req / 3 seconds | Returns Atom XML |
| PubMed/PMC | 3 req/s (no key), 10/s (with key) | Sequential requests |
| Crossref | 5 req/s (public), 10/s (with `mailto`) | Add email for polite pool |
| Semantic Scholar | Shared pool (no key) | Burst-friendly |
| OpenAlex | Generous | Add email for priority |

## Database Reference Files

Detailed API docs for each database (endpoints, parameters, response formats):

- [databases/arxiv.md](databases/arxiv.md)
- [databases/crossref.md](databases/crossref.md)
- [databases/semantic-scholar.md](databases/semantic-scholar.md)
- [databases/openalex.md](databases/openalex.md)
- [databases/pubmed.md](databases/pubmed.md)
- [databases/pmc.md](databases/pmc.md)
- [databases/unpaywall.md](databases/unpaywall.md)
- [databases/biorxiv.md](databases/biorxiv.md)
- [databases/medrxiv.md](databases/medrxiv.md)
- [databases/core.md](databases/core.md) (requires API key — use as fallback)
