# Search Strategies

How to find papers and sources using academic search engines.

## Google Scholar

**URL**: https://scholar.google.com/

### Search Operators

| Operator | Example | Effect |
|----------|---------|--------|
| `"exact phrase"` | `"moving average"` | Exact match |
| `author:` | `author:Jurik` | Papers by author |
| `intitle:` | `intitle:"adaptive filter"` | Term must be in title |
| `source:` | `source:Nature` | Papers from specific journal |
| `-term` | `filter -Kalman` | Exclude term |
| `OR` | `"JMA" OR "Jurik"` | Either term |
| `2015..2024` | `"deep learning" 2020..2024` | Year range |

### Finding Seminal Papers

1. Search your topic
2. Sort by citation count (most cited first)
3. Check "Cited by" counts — high counts indicate influence
4. Use "Cited by" links to find newer papers building on seminal work
5. Check "Related articles" for adjacent work

### Citation Count Thresholds

| Paper Age | Citations | Status |
|-----------|-----------|--------|
| 0–3 years | 20+ | Noteworthy |
| 0–3 years | 100+ | Highly influential |
| 3–7 years | 100+ | Significant |
| 3–7 years | 500+ | Landmark |
| 7+ years | 500+ | Seminal |
| 7+ years | 1000+ | Foundational |

---

## PubMed

**URL**: https://pubmed.ncbi.nlm.nih.gov/

### MeSH Terms

PubMed uses Medical Subject Headings (MeSH) for controlled vocabulary. Find terms at: https://meshb.nlm.nih.gov/search

```
"Diabetes Mellitus, Type 2"[MeSH]
"Signal Processing, Computer-Assisted"[MeSH]
```

### Field Tags

| Tag | Searches |
|-----|----------|
| `[Title]` | Title only |
| `[Title/Abstract]` | Title or abstract |
| `[Author]` | Author name |
| `[Journal]` | Journal name |
| `[Publication Date]` | Date range |
| `[Publication Type]` | Article type (Review, Clinical Trial) |
| `[MeSH]` | MeSH term |

### Query Construction

```
"adaptive filter"[Title] AND "moving average"[Title/Abstract] AND 2015:2024[Publication Date]
```

Boolean operators: `AND`, `OR`, `NOT`

---

## arXiv

**URL**: https://arxiv.org/

### Categories (relevant to signal processing / quantitative finance)

- `q-fin.TR` — Trading and Market Microstructure
- `q-fin.ST` — Statistical Finance
- `cs.CE` — Computational Engineering
- `eess.SP` — Signal Processing
- `stat.ML` — Machine Learning (Statistics)

### Search

Use the search bar or API:
```
https://arxiv.org/search/?query=jurik+moving+average&searchtype=all
```

---

## Semantic Scholar

**URL**: https://www.semanticscholar.org/

- 200M+ papers across all disciplines
- Excellent citation graph and influence metrics
- "Highly Influential Citations" feature identifies papers that substantively build on a work
- Free API: `https://api.semanticscholar.org/graph/v1/paper/{paper_id}`

---

## Search Strategy Workflow

1. **Start broad**: Use 2–3 core terms, no filters
2. **Assess landscape**: How many results? Which are most cited?
3. **Narrow**: Add filters (date range, specific journals, authors)
4. **Expand via citations**: From key papers, follow "Cited by" and reference lists
5. **Cross-database**: Search at least 2 sources (Scholar + PubMed, Scholar + arXiv)
6. **Document**: Record exact queries, dates, result counts for reproducibility

---

## Tips

- Google Scholar is best for comprehensive cross-disciplinary coverage
- PubMed is best for biomedical literature with controlled vocabulary
- arXiv is best for recent preprints in physics, math, CS, finance
- Always check if a preprint has been published — cite the published version
- Citation count alone isn't quality — check venue tier and author reputation
