---
name: source-finder
description: Find, retrieve, and cite sources across academic databases, web, blogs, GitHub, forums, and social networks. Generates BibTeX for every result. Performs DOI/arXiv lookup and PDF download directly; coordinates literature search and multi-source validation via sub-skills. Use when the user says "find papers", "search for", "literature review", "download PDF", "get BibTeX", "look up DOI", "find sources on", or mentions arXiv, DOI, Crossref, Semantic Scholar, or any research task.
---

# Source Finder

Find sources, retrieve them, and deliver structured citations with BibTeX. Covers academic papers, web pages, blogs, GitHub repos, forum posts, and social discussions.

## Core Rule

**Every result gets a BibTeX entry.** No exceptions. Whether it's a Nature paper, a Medium blog post, or a ForexFactory forum thread — generate a BibTeX entry and deliver it alongside the result.

## When to Use

- Given a DOI or arXiv ID → retrieve metadata, abstract, BibTeX, and PDF
- Given a search phrase → find sources across multiple databases
- Given a book/article title → find BibTeX and download links
- Literature review / research synthesis tasks
- Any "find me information about X" request

## Cooperation with Other Skills

```
source-finder    →  finds sources, generates BibTeX, downloads PDFs
       ↓
bibliography     →  manages .bib files, deduplicates, formats reference lists
       ↓
document-to-markdown  →  extracts content from downloaded PDFs/HTML
```

- **After finding**: hand BibTeX entries to `bibliography` skill for `.bib` management
- **After downloading PDF/HTML**: hand to `document-to-markdown` for content extraction
- **source-finder does NOT**: format reference lists, extract document content, or manage .bib files

## Routing Logic

First decide the **category**, then pick the sub-skill:

1. **Direct lookup** — user gives a DOI or arXiv ID → [academic/doi-resolve.md](academic/doi-resolve.md)
2. **Search** — user wants to find sources:
   - Academic papers → [academic/academic.md](academic/academic.md)
   - Web / blogs / GitHub / social → [web/web.md](web/web.md) (see sub-pages for [blogs](web/blogs.md), [GitHub](web/github.md), [social](web/social.md))
   - Domain-specific forums → [domain/domain.md](domain/domain.md)
3. **Retrieve** — user wants to download a PDF or save a page → [retrieval/retrieval.md](retrieval/retrieval.md)
4. **Synthesize** — user wants multi-source validation or lit review → [synthesis/synthesis.md](synthesis/synthesis.md)

## Search Strategy

For any research query, search **multiple source types** in parallel:

1. **Academic** — Crossref, Semantic Scholar, arXiv, OpenAlex (always)
2. **Web** — official docs, independent analyses, tech publications
3. **Domain-specific** — if the topic matches a domain (e.g., trading → MQL5 forums)
4. **Blogs/social** — if the topic is recent or practitioner-oriented

Then **cross-validate** results and **rank by quality** (see synthesis/).

## API Keys

Most databases are free. The following keys are optional (improve rate limits):

| Database | Env Variable | Required? | Effect without key |
|----------|-------------|-----------|-------------------|
| NCBI (PubMed/PMC) | `NCBI_API_KEY` | No | 3 req/s instead of 10 |
| Semantic Scholar | `S2_API_KEY` | No | Shared rate pool |
| OpenAlex | `OPENALEX_API_KEY` | No | Lower priority queue |

**Fully free (no key needed):** arXiv, Crossref, Unpaywall, bioRxiv, medRxiv, GitHub API (for public repos).

**CORE** requires a key for full text — use as fallback only, prefer Unpaywall + PMC for open access.

## Making HTTP Requests

Use `WebFetch` tool for API calls. Fall back to `curl` via Bash if WebFetch fails.

- **arXiv** returns Atom XML (not JSON)
- **Crossref/Unpaywall** benefit from `mailto` parameter for polite pool
- **arXiv** rate limit: 1 request per 3 seconds
- On HTTP 429: wait and retry once

## Quality Principles

1. **No fabricated data** — never invent citations, DOIs, or URLs
2. **Multi-source validation** — cross-reference claims across 2+ sources
3. **Bias awareness** — flag vendor content, sponsored results
4. **Recency preference** — prefer recent sources for technology topics
5. **Primary sources** — prefer original papers over secondary summaries
6. **Link verification** — verify URLs are accessible before delivering

## Sub-Skill Index

| Sub-skill | Path | Covers |
|-----------|------|--------|
| Academic search | [academic/](academic/academic.md) | 9 databases, search strategy, identifier formats |
| DOI/arXiv resolve | [academic/doi-resolve.md](academic/doi-resolve.md) | Direct lookup, metadata, PDF links |
| Web research | [web/](web/web.md) | General web, quality scoring, validation |
| Blog search | [web/blogs.md](web/blogs.md) | Medium, Substack, dev.to, personal blogs |
| GitHub search | [web/github.md](web/github.md) | Repos, code, discussions, README mining |
| Social search | [web/social.md](web/social.md) | LinkedIn, X/Twitter, Reddit |
| Domain sources | [domain/](domain/domain.md) | Extensible domain-specific source lists |
| Retrieval | [retrieval/](retrieval/retrieval.md) | PDF download, page save, format handling |
| BibTeX templates | [retrieval/bibtex-templates.md](retrieval/bibtex-templates.md) | Templates for every source type |
| Synthesis | [synthesis/](synthesis/synthesis.md) | Multi-source validation, quality scoring, lit review |
