# Blog Search

Find and cite content from blog platforms: Medium, Substack, dev.to, personal technical blogs.

## When to Use

- Practitioner perspectives on tools/techniques
- Tutorials and how-to guides
- Recent opinions and experiences (not yet in papers)
- Explanatory content (often better than docs for learning)

## Search Strategies

### Medium

- Search via web: `site:medium.com "search terms"`
- Or: `site:towardsdatascience.com "topic"` (ML/data science)
- Note: many articles are paywalled — check accessibility

### Substack

- Search via web: `site:substack.com "search terms"`
- Many finance/tech newsletters are on Substack
- Usually not paywalled

### dev.to

- Search via web: `site:dev.to "search terms"`
- API: `https://dev.to/api/articles?tag=topic&per_page=10`
- Good for developer tooling, frameworks

### Personal Blogs

- Often found via web search naturally
- Higher quality when author is a known expert
- Check author credentials before citing

## Quality Assessment

Blog-specific quality signals:

| Signal | Good | Bad |
|--------|------|-----|
| Author | Named expert, credentials visible | Anonymous, no bio |
| Content | Code examples, data, references | Opinion without evidence |
| Date | Recent, maintained | Outdated, broken links |
| Comments | Expert discussion | Spam or none |
| Platform | Personal site, known newsletter | Content farm |

## BibTeX

Use `@online` entry type — see [retrieval/bibtex-templates.md](../retrieval/bibtex-templates.md).
