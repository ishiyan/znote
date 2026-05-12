# GitHub Search

Find and cite GitHub repositories, code, discussions, and documentation.

## When to Use

- Finding reference implementations
- Discovering libraries/tools for a task
- Finding code examples and patterns
- Community discussions about technical issues

## Search Methods

### Repository Search

Via web: `site:github.com "topic" language:python`

Via GitHub API:
```
GET https://api.github.com/search/repositories?q={query}+language:{lang}&sort=stars
```

### Code Search

Via GitHub API:
```
GET https://api.github.com/search/code?q={query}+language:{lang}
```

### Discussions / Issues

Via web: `site:github.com "topic" inurl:issues` or `inurl:discussions`

## Quality Signals

| Signal | Weight | Best |
|--------|--------|------|
| Stars | High | >100 for libraries, >10 for niche |
| Recent activity | High | Commits in last 6 months |
| Documentation | Medium | README + docs/ folder |
| Tests | Medium | CI passing, test coverage |
| License | Low | Permissive (MIT, Apache) |

## What to Extract

- **README** — primary documentation, often best overview
- **Source code** — reference implementations
- **Issues/discussions** — known problems, design decisions
- **Releases** — version history, changelogs

## BibTeX

Use `@software` entry type — see [retrieval/bibtex-templates.md](../retrieval/bibtex-templates.md).
