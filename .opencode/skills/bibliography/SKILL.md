---
name: bibliography
description: Manage citations and bibliographies for technical and academic writing. Parse BibTeX files, format references in APA 7 (default), Nature, Vancouver, IEEE, or Chicago style, verify URL liveness with access-date stamping, and enrich entries with Google Books links. Use when formatting references, processing .bib files, validating citations, or building a bibliography.
---

# Bibliography

Format, validate, and manage citations. Default style: APA 7. Supports BibTeX input and multiple output styles.

## When to Use

- Formatting a reference list or bibliography section
- Processing an existing .bib file into styled output
- Verifying URLs in references are live and stamping access dates
- Finding or citing papers (search strategies)
- Converting between citation formats
- Building a bibliography from scratch

## Supported Styles

| Style | Use case | In-text format |
|-------|----------|----------------|
| **APA 7** (default) | Social sciences, technical writing, general | (Author, Year) |
| **Nature** | Natural sciences journals | Superscript numbers |
| **Vancouver** | Biomedical, clinical | Superscript numbers |
| **IEEE** | Engineering, CS | Bracketed numbers |
| **Chicago** | Humanities, history | (Author Year) or footnotes |

See [formatting/apa7-style.md](formatting/apa7-style.md) for APA 7 rules.
See [formatting/other-styles.md](formatting/other-styles.md) for Nature, Vancouver, IEEE, Chicago.

## Core Workflow

### 1. Input Assessment

Determine what the user has:
- **A .bib file** → Parse with BibTeX rules, then format. See [workflow/bibtex-processing.md](workflow/bibtex-processing.md)
- **A list of references (plain text)** → Validate, enrich, format
- **DOIs / URLs / paper titles** → Look up metadata, build entries
- **Nothing yet** → Use search strategies to find sources. See [reference/search-strategies.md](reference/search-strategies.md)

### 2. Validation and Enrichment

For every reference:
1. Check required fields are present (per entry type)
2. Verify URLs are accessible → stamp "Last accessed: YYYY-MM-DD"
3. Resolve DOIs → confirm they point to the right paper
4. Look up Google Books URL if entry is a book and user wants it
5. Flag issues (missing fields, dead URLs, broken DOIs)

See [workflow/url-verification.md](workflow/url-verification.md) for URL checking.

### 3. Formatted Output

Produce the reference list in the chosen style. Rules:
- One style per document (don't mix)
- Alphabetical by first author (APA 7, Chicago) or order of appearance (Nature, Vancouver, IEEE)
- Include DOI as URL when available
- Include "Last accessed" date for web-only sources (no DOI)
- Optionally include Google Books URL for books

## BibTeX Support

When a user provides a .bib file:
1. Parse all entries (understand types: @article, @book, @inproceedings, etc.)
2. Validate syntax and required fields
3. Detect duplicates
4. Format output in the requested citation style
5. Report issues

See [formatting/bibtex-rules.md](formatting/bibtex-rules.md) for BibTeX entry types and field requirements.

## Google Books URLs

Optional enrichment for book entries. Include when:
- User requests it
- The book has a Google Books preview available
- Format: append after standard APA 7 entry as `Available at: [Google Books URL]`

This isn't standard APA but is practical for web-published technical articles where readers benefit from direct book access.

## Reference Files

- [formatting/apa7-style.md](formatting/apa7-style.md) — APA 7th edition rules
- [formatting/other-styles.md](formatting/other-styles.md) — Nature, Vancouver, IEEE, Chicago
- [formatting/bibtex-rules.md](formatting/bibtex-rules.md) — BibTeX entry types and formatting
- [workflow/bibtex-processing.md](workflow/bibtex-processing.md) — Parsing and processing .bib files
- [workflow/url-verification.md](workflow/url-verification.md) — URL liveness, access-date stamping
- [reference/metadata-sources.md](reference/metadata-sources.md) — CrossRef, PubMed, arXiv, DataCite APIs
- [reference/search-strategies.md](reference/search-strategies.md) — Google Scholar, PubMed search operators
