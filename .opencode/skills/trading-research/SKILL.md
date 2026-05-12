---
name: trading-research
description: Research trading authors or trading topics across TASC archive, MQL5, trading forums, academic papers, and the web. Two modes — "trading research author {name}" produces a full author profile (TASC articles, indicators, books, biography, photos, academic papers, forum threads, MQL5 implementations, BibTeX). "trading research topic {topic}" produces topic-centric research (same sources, no biography/photos). Use when the user says "trading research author" or "trading research topic".
---

# Trading Research

Comprehensive research on trading authors or trading topics. Searches TASC archive, MQL5, 10 mandatory trading forums, academic databases, and the web. Produces a structured markdown output with BibTeX citations for every source.

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| Author | `trading research author {name}` | Full profile: biography, TASC articles, indicators, books, photos/videos, forum threads, MQL5 implementations, academic papers, BibTeX |
| Topic | `trading research topic {topic}` | Topic survey: TASC articles (by keyword), implementations, forum threads, academic papers, books, BibTeX. No biography or photos. |

## Output Directory

All output goes to `trading-research/` in the workspace root.

| Artifact | Path |
|----------|------|
| Main output | `trading-research/{slug}.md` |
| Provenance sidecar | `trading-research/{slug}.provenance.md` |

Derive the slug: lowercase, hyphenated, no filler words, max 5 words. For authors, use the name (e.g., `john-ehlers`). For topics, use the topic (e.g., `zig-zag-indicators`).

### Skip-with-Prompt

Before starting, check if `trading-research/{slug}.md` already exists. If it does, **stop and ask**:

> `trading-research/{slug}.md` already exists (last modified {date}). Overwrite from scratch, or skip?

Do NOT proceed until the user responds. If they say skip, stop. If they say overwrite, delete the existing file and provenance sidecar, then proceed.

## Cooperation with Other Skills

```
trading-research
  ├── source-finder     →  academic papers (arXiv, Crossref, Semantic Scholar), web search
  ├── bibliography      →  BibTeX management, deduplication, formatting
  └── gh CLI            →  GitHub repository and code search
```

- Use `source-finder` sub-skills for academic and web evidence gathering
- Use `bibliography` for BibTeX file management if the user requests a `.bib` file
- Do NOT use `deep-research` — this skill replaces the deep-research wrapper for trading topics

## Pipeline

No plan gate. No scale decision. Go straight into evidence gathering.

```
Detect mode → Check existing output → Gather evidence (parallel) → Write output → Write provenance
```

### Parallelism

Use Task agents for independent source searches to maximize speed. Recommended split:

- **Agent 1**: TASC archive (author page or keyword search) + Traders' Tips
- **Agent 2**: MQL5 CodeBase + MQL5 Articles
- **Agent 3**: 10 mandatory forums (site: searches)
- **Agent 4**: Academic papers (arXiv, Crossref, Semantic Scholar) + web search + GitHub repositories
- **Agent 5** (author mode only): Photos, videos, interviews + biography

Each agent writes its findings to a section of the output. The lead agent assembles the final document.

---

## Source Pipeline

### 1. TASC Archive

Published by Traders.com since 1982. The definitive magazine for trading indicators, DSP-based methods, and system development. Article PDFs require subscription, but extensive metadata is freely available.

Base domain: `technical.traders.com` and `traders.com`

#### Cached Index (1982–2025)

A complete pre-downloaded index of all 7,975 TASC articles from 1982–2025 is available at:
- **Article index:** `.opencode/skills/trading-research/tasc-article-index.md` — grouped by year/month with title, author, subject, and PDF URL
- **BibTeX:** `.opencode/skills/trading-research/tasc-article-index.bib` — one `@article` entry per article

**Search procedure (1982–2025):**
1. Read the cached index file (`tasc-article-index.md`)
2. Search for the author name or topic keywords
3. Extract matching articles with their PDF URLs and BibTeX keys
4. No online fetches needed for articles in this range

**For 2026+ articles:** fetch the XML TOC online (see below).

#### Online Resources (2026+ only)

##### TOC Archive (XML)

URL pattern: `https://traders.com/Mobile/Archive/{MON}{YYYY}.XML`

- `{MON}` = 3-letter uppercase month abbreviation: JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC
- `{YYYY}` = 4-digit year
- There is a 13th "bonus" issue each year using `BON` as the month code

XML structure (key elements per `<Article>`):
- `<Name>` — article title
- `<Author>` — author name
- `<Year>` — publication year
- `<Subject>` — topic category
- `<More>` — article synopsis/abstract
- `<To>` — PDF path (e.g., `\V40\C01\353KAUF.pdf`). Extract the filename part to search for freely available copies online.
- `<charmonth>` — 3-letter month code

Note: SSL certificate on traders.com may fail verification — use `--insecure` with curl. Most browsers fail to render these XMLs due to a missing XSL reference. Fetch raw XML and parse directly.

##### Author Search (author mode)

URL pattern: `http://technical.traders.com/archive/combo/display5.asp?author={Name}`

- URL-encode the author name (spaces as `%20`, drop periods)
- Example: `http://technical.traders.com/archive/combo/display5.asp?author=John%20F%20Ehlers`

Returns HTML with article entries containing:
- Article title (in `<h3 class="articleTitle">`)
- Synopsis (in `<p class="caption">`)
- Author, date, subject (in `<p class="byline">`)
- PDF link (in `<div class="link">`)

##### Title Archive (topic mode)

`https://technical.traders.com/archive/combo/title/titlelist.asp?word=atitlelist`

For topic mode, search this alphabetical title list for keyword matches. Also search TOC XML files for articles whose `<Name>` or `<Subject>` match the topic.

##### Complete Author List

`https://technical.traders.com/archive/combo/authorlist.asp`

##### Magazine Covers

Full resolution (1000px PNG):
`https://technical.traders.com/images/New-2014/1000px-png/{YYMM}.png`

Mini-cover:
`https://technical.traders.com/images/New-2014/{YYYY}/{YYMM}_Minicover.png`

Format for `{YYMM}`:
- March 2025 → `2503`
- January 2001 → `0101`
- January 2000 → `0001`
- January 1999 → `9901`
- October 1982 → `8210`
- Bonus issues use `13` as month: `2513` for bonus 2025

The `New-2014` path segment is constant (not year-related). The `{YYYY}` folder in mini-cover URLs is the 4-digit year.

##### Traders' Tips (Free Reference Implementations)

URL pattern: `http://traders.com/Documentation/FEEDbk_docs/{YYYY}/{MM}/TradersTips.html`

- `{YYYY}` = 4-digit year, `{MM}` = 2-digit month (zero-padded)
- First available issue: 2009/01
- Example: `http://traders.com/Documentation/FEEDbk_docs/2009/01/TradersTips.html`

Each page contains reference implementations of indicators from the current or previous TASC issue, contributed by platform vendors (TradeStation, MetaStock, AmiBroker, NinjaTrader, etc.).

When processing a Traders' Tips page:
1. **Download linked ZIP files** — these contain full source code projects
2. **Download linked XLSM/Excel files** — these contain spreadsheet implementations
3. **Extract inline source listings** — code blocks embedded directly in the HTML (EasyLanguage, AFL, C#, Pine Script, etc.)

##### TASC Search Patterns

```
site:technical.traders.com "indicator name"
site:traders.com "author name"
```

To find freely available TASC PDFs elsewhere:
```
"V40\C01\353KAUF" filetype:pdf
"Technical Analysis of Stocks and Commodities" "article title"
```

Extract the PDF path from the `<To>` element and search for the filename portion.

#### TASC Workflow — Author Mode

When researching a TASC author/editor/contributor, follow these steps to extract full article metadata with PDF links and Traders' Tips references. Do not settle for article titles alone.

**Key requirements at a glance:**
1. Fetch the author archive page and parse article metadata (title, date, PDF path)
2. Construct full PDF URLs and check Traders' Tips for post-2009 articles
3. Fall back to TOC XML for pre-2009 articles
4. Search MQL5 CodeBase for implementations
5. Generate a BibTeX entry for every source found
6. Present TASC articles year-by-year (most recent first)

**Step 1: Fetch the Author Archive Page**

Fetch: `http://technical.traders.com/archive/combo/display5.asp?author={URL-encoded name}`

Parse the HTML to extract for each article:
- Title
- Date (month + year)
- Subject/category
- PDF path (from link href — pattern: `\V{vol}\C{issue}\filename.pdf`)

**Step 2: Construct PDF URLs**

For each article with a PDF path, construct the full URL:
```
https://technical.traders.com/archive/article.asp?file=\V{vol}\C{issue}\{filename}.pdf
```

**Step 3: Check for Traders' Tips**

For articles published **2009 or later**, check the corresponding Traders' Tips page:
```
http://traders.com/Documentation/FEEDbk_docs/{YYYY}/{MM}/TradersTips.html
```

Traders' Tips contain free reference implementations (EasyLanguage, AFL, C#, Pine Script, Python, etc.) contributed by platform vendors.

**Step 4: Fetch TOC XML for Early Articles**

For articles **before 2009** (or when the author page is incomplete), fetch the TOC XML for the specific month:
```
https://traders.com/Mobile/Archive/{MON}{YYYY}.XML
```

Parse `<Article>` elements matching the author name to get `<To>` (PDF path), `<More>` (synopsis), and `<Subject>`.

#### TASC Workflow — Topic Mode

When researching a trading topic/indicator:

**Step 1: Search the Title Archive**

Fetch `https://technical.traders.com/archive/combo/title/titlelist.asp?word=atitlelist` and search for keyword matches in article titles.

**Step 2: Search TOC XML**

Search recent TOC XML files (work backwards from current year) for articles whose `<Name>` or `<Subject>` or `<More>` match the topic keywords.

**Step 3: Construct PDF URLs and check Traders' Tips**

Same as author mode Steps 2-3 above.

**Step 4: Identify Authors**

For each article found, note the author. This helps find related work by the same authors.

### 2. MQL5 CodeBase & Articles

Use the **MQL5 Search API** (returns JSON, works without JS):

```
https://search.mql5.com/api/query?keyword={indicator_name}&module=mql5.com.en.codebase|mql4.com.en.codebase&count=20&lng=en
```

For articles about the indicator:
```
https://search.mql5.com/api/query?keyword={indicator_name}&module=mql5.com.en.articles|mql4.com.en.articles&count=10&lng=en
```

**Response format** (JSON):
```json
{
  "results": [
    {
      "module": "mql5.com.en.codebase",
      "info": {
        "url": "https://www.mql5.com/en/code/22115",
        "author_name": "Scriptor",
        "author_login": "Scriptor",
        "title": "Trix",
        "platform": "MetaTrader 5",
        "download_url": "https://download.terminal.free/cdn/library/mt5/44/22115.zip",
        "category": "Indicators",
        "type": "indicators"
      },
      "text": "Description text..."
    }
  ]
}
```

**Important:** Do NOT use the hash-fragment URL (`mql5.com/en/search#!keyword=...`) — that requires JavaScript. Always use the `search.mql5.com/api/query` endpoint directly via `curl` or WebFetch.

Record for each indicator found:
- MQL5 CodeBase entry title and URL
- Author (MQL5 username)
- Platform (MT4 or MT5)
- Category (Indicators, Experts, Scripts, Libraries)
- Download URL

### 3. Trading Forums — Mandatory Search List

You **MUST** search these forums for dedicated threads, discussions, and implementations. Use `site:` searches or direct forum search endpoints.

| Forum | URL | Search Pattern |
|-------|-----|----------------|
| ForexFactory | https://www.forexfactory.com/forum | `site:forexfactory.com/thread "{name}"` |
| futures.io (BigMikeTrading) | https://futures.io/ | `site:futures.io "{name}"` or `site:bigmiketrading.com "{name}"` |
| Elite Trader | https://www.elitetrader.com/et/forums/ | `site:elitetrader.com "{name}"` |
| NinjaTrader Forum | https://ninjatrader.com/support/forum/ | `site:ninjatrader.com/support/forum "{name}"` |
| TradingView Community | https://www.tradingview.com/scripts/ | `site:tradingview.com/script "{indicator}"` |
| MQL5 Forum | https://www.mql5.com/en/forum | `site:mql5.com/en/forum "{name}"` |
| Wealth-Lab | https://www.wealth-lab.com/ | `site:wealth-lab.com "{name}"` |
| Quant Stack Exchange | https://quant.stackexchange.com/ | `site:quant.stackexchange.com "{indicator}"` |
| r/algotrading | https://www.reddit.com/r/algotrading/ | `site:reddit.com/r/algotrading "{indicator}"` |
| Trade2Win | https://www.trade2win.com/forums/ | `site:trade2win.com "{name}"` |

For each forum where relevant threads are found, include them in the output under a **## Forum Discussions** section with direct URLs to the thread/post.

### 4. Academic Papers

Use the `source-finder` skill's academic sub-skills to search:
- **arXiv** — preprints mentioning the author or topic
- **Crossref** — published papers
- **Semantic Scholar** — citation graph, related work
- **OpenAlex** — open access papers

For author mode, search by author name. For topic mode, search by topic keywords.

#### IFTA Journal

The IFTA Journal (ISSN 2409-0271) is a key source for technical analysis research. A complete article index is available at `.opencode/skills/trading-research/ifta-journal-index.md` covering all issues from 2000–2026.

**Search procedure:**
1. Read the IFTA Journal index file
2. Search for the author name or topic keywords in the index
3. If a match is found, note the year, title, pages, and PDF URL from the index
4. Download the PDF and extract the relevant article text for citation
5. Add a `@article` BibTeX entry with `journal = {IFTA Journal}` and the ISSN

**Rate limiting:** IFTA PDFs are served via Cloudflare. Wait 20 seconds between downloads.

### 5. GitHub Repositories

Search GitHub for repositories implementing or referencing the author's indicators (author mode) or the topic (topic mode).

#### Search Strategy

Use the GitHub Search API via `gh` CLI:

```bash
# By indicator/author name
gh search repos "JMA Jurik" --limit 20 --json fullName,description,url,stargazersCount,language,updatedAt --sort stars

# By indicator keyword
gh search repos "jurik moving average" --limit 20 --json fullName,description,url,stargazersCount,language,updatedAt --sort stars

# Code search for implementations
gh search code "jurik" --filename "*.py" --limit 10 --json repository,path
gh search code "jurik" --filename "*.rs" --limit 10 --json repository,path
gh search code "jurik" --filename "*.go" --limit 10 --json repository,path
```

Search for:
1. Dedicated repos for the author's indicators
2. Trading/TA libraries that include the indicator (e.g., `ta-lib`, `pandas-ta`, `tulip`)
3. Implementations in major languages: Python, Rust, Go, TypeScript/JavaScript, C#, C++, Zig, MQL
4. Forks/ports of well-known implementations

#### Output Format

```markdown
## GitHub Repositories

### Dedicated Repositories

| Repository | Stars | Language | Description |
|------------|-------|----------|-------------|
| [user/repo](https://github.com/user/repo) | 42 | Python | JMA implementation with tests |

### Libraries Including {Indicator}

| Repository | Stars | Language | Indicator(s) | Path |
|------------|-------|----------|---------------|------|
| [twopirllc/pandas_ta](https://github.com/twopirllc/pandas_ta) | 5.2k | Python | JMA | `pandas_ta/overlap/jma.py` |

### Notable Code References

| Repository | Language | File | Context |
|------------|----------|------|---------|
| [user/repo](https://github.com/user/repo) | Rust | `src/jma.rs` | Full implementation with adaptive smoothing |
```

#### BibTeX for Repos

```bibtex
@online{github_user_repo,
  author       = {GitHub username or real name},
  title        = {Repository Name --- Description},
  url          = {https://github.com/user/repo},
  urldate      = {2026-05-10},
  note         = {GitHub repository, {stars} stars, {language}},
}
```

#### Parallelism

GitHub searches can run within any existing agent — typically add to **Agent 4** (academic + web search) or create a dedicated **Agent 6** for GitHub if the author has many indicators to search for.

### 6. Photos, Videos & Interviews (Author Mode Only)

Skip this section entirely in topic mode.

When documenting an author, you **MUST** search for and include **actual URLs** for photos and videos. Do not merely state "photos exist" — provide links.

#### Search Strategy

1. **Photos**: Wikipedia (commons), company website, LinkedIn, conference speaker pages, book jacket images
2. **Videos**: YouTube (`"{author name}" trading`), Vimeo, CNBC/Bloomberg clips, conference talks, webinars
3. **Interviews**: Podcasts (search podcast platforms), magazine interviews, YouTube interviews

#### Output Format

```markdown
## Photos, Videos & Interviews

### Photos
| Description | URL | Source |
|-------------|-----|--------|
| Headshot from company website | https://example.com/photo.jpg | Company site |
| Wikipedia portrait | https://upload.wikimedia.org/... | Wikimedia Commons |
| [URL not found] Speaker photo at conference X | — | Mentioned in conference program |

### Videos
| Title | URL | Duration | Date |
|-------|-----|----------|------|
| Interview on Trading Strategy | https://youtube.com/watch?v=... | 45:00 | 2020-03-15 |
| [URL not found] CNBC appearance discussing X | — | ~5 min | 2018 |

### Interviews & Podcasts
| Title | URL | Host/Publication | Date |
|-------|-----|-----------------|------|
| "Secrets of the Trading Masters" | https://... | Chat With Traders | 2019-06-20 |
```

**Rules:**
- Every item MUST have an actual URL or be explicitly marked `[URL not found]`
- Items marked `[URL not found]` still appear (for completeness) but are clearly flagged
- Each photo/video/interview gets a BibTeX `@online` entry in the BibTeX section
- Search at least: YouTube, the author's company website, Wikipedia/Wikimedia, major podcast directories

#### BibTeX for Media

```bibtex
@online{AuthorYYYYvideo_keyword,
  author  = {Last, First},
  title   = {Video/Photo Title},
  url     = {https://...},
  urldate = {2025-05-07},
  year    = {YYYY},
  note    = {YouTube video, 45:00 / Photo / Podcast episode},
}
```

---

## Output Format

### TASC BibTeX Template

```bibtex
@article{tasc:v{vol}c{issue}{filename_lower},
  author  = {Last, First},
  title   = {Article Title},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {YYYY},
  month   = mon,
  volume  = {vol},
  number  = {issue},
  url     = {https://technical.traders.com/archive/article.asp?file=\V{vol}\C{issue}\{filename}.pdf}
}
```

Volume/issue can be derived from the PDF path: `V40\C01` → volume 40, issue 1.

For books, use `@book`. For web sources, use `@online`.

The final output **MUST** include a complete `## BibTeX` section with all entries in a single fenced code block.

### TASC Publications (Year-by-Year)

Articles MUST be presented in a **year-by-year** section (most recent first), with each year as an `### YYYY` heading:

```markdown
## TASC Publications (Complete List, YYYY–YYYY)

### 2026

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
| May | The AutoTune Filter | Brief description... | [\V44\C06\234AUTO](https://technical.traders.com/archive/article.asp?file=\V44\C06\234AUTO.pdf), [Tips](http://traders.com/Documentation/FEEDbk_docs/2026/05/TradersTips.html) |
| Jan | The Reversion Index | Brief description... | [\V44\C02\198REVI](https://technical.traders.com/archive/article.asp?file=\V44\C02\198REVI.pdf), [Tips](http://traders.com/Documentation/FEEDbk_docs/2026/01/TradersTips.html) |

### 2025

| Month | Title | Description | Article |
|-------|-------|-------------|---------|
...
```

For topic mode, the same format applies but articles may span multiple authors. Add an `Author` column:

```markdown
## TASC Articles on {Topic}

### 2026

| Month | Title | Author | Description | Article |
|-------|-------|--------|-------------|---------|
...
```

### Indicators (Author Mode — Categorized)

All indicators introduced by the author MUST be listed in a categorized table with a `Category` column. Group into sections by era or source:

```markdown
## Technical Indicators & Tools

### Core Indicators

| Indicator | First Published | Category |
|-----------|----------------|----------|
| MESA Adaptive Moving Average | TASC Sep 2001, [\V19\C10\268MESA](https://technical.traders.com/archive/article.asp?file=\V19\C10\268MESA.pdf) | Adaptive MA |
| Fisher Transform | TASC Nov 2002, [\V20\C11\312FISH](https://technical.traders.com/archive/article.asp?file=\V20\C11\312FISH.pdf) | Transform |
| SuperSmoother Filter | Book: Cybernetic Analysis | Filter |

### Later Indicators (YYYY–YYYY)

| Indicator | First Published | Category |
|-----------|----------------|----------|
...
```

Valid categories include (adapt to author's domain): `Filter`, `Adaptive MA`, `Oscillator`, `Cycle`, `Trend`, `Transform`, `Channel`, `Visualization`, `Spectral`, `Prediction`, `Multi-purpose`, `Strategy`.

### Indicators Per Book (Author Mode)

If the author has published books that introduce indicators, you MUST create a separate subsection for each book listing all indicators introduced in that book:

```markdown
### Indicators Introduced in Books

#### Book Title (Year)

| Indicator | Chapter | Category |
|-----------|---------|----------|
| SuperSmoother Filter (2-pole, 3-pole) | Ch. 3 | Filter |
| Cyber Cycle | Ch. 4 | Cycle |
| Adaptive Cyber Cycle | Ch. 5 | Cycle |

#### Another Book Title (Year)

| Indicator | Chapter | Category |
|-----------|---------|----------|
...
```

This is important because many prolific authors (e.g., Ehlers, Kaufman, Appel) introduce indicators in books rather than articles. If chapter numbers are not available, omit the Chapter column but still list all indicators per book.

### PDF Link Format

**CRITICAL — PDF link format rule:**
- The link text MUST be the backslash-separated PDF path (e.g., `\V12\C01\123MULL`), NOT the word "PDF"
- Format: `[\V{vol}\C{issue}\{filename}](https://technical.traders.com/archive/article.asp?file=\V{vol}\C{issue}\{filename}.pdf)`
- Example: `[\V12\C01\062SMOO](https://technical.traders.com/archive/article.asp?file=\V12\C01\062SMOO.pdf)`
- This rule applies to article tables only — BibTeX `url` fields use the full URL as-is
- Do NOT write `[PDF](url)` — always use the path as visible link text

This is **mandatory** — article lists without PDF links and Tips references are incomplete.

### Required Sections

The final output MUST include:
- A **## MQL5 Implementations** section listing CodeBase entries for each indicator
- A **## GitHub Repositories** section with repos found via GitHub search
- A **## Forum Discussions** section with threads found on the 10 mandatory forums
- A **## Academic Papers** section (if any found)
- A **## BibTeX** section with all entries in a single fenced code block

Author mode additionally requires:
- A **## Biography** section
- A **## Photos, Videos & Interviews** section
- A **## Technical Indicators & Tools** section (categorized)

### External Books — Full Reference Requirements

When the output mentions books (whether by the researched author or books that reference them), **every book MUST have a full citation** with:
- Title, Author(s), Year, Publisher, ISBN (if available)
- URL: Google Books link or publisher page
- BibTeX `@book` entry

Do NOT write "referenced in Murphy's Technical Analysis" without providing the full citation and link. Example:

```markdown
| # | Title | Author | Year | Publisher | ISBN | Link |
|---|-------|--------|------|-----------|------|------|
| 1 | Technical Analysis of the Financial Markets | John J. Murphy | 1999 | New York Institute of Finance | 978-0735200661 | [Google Books](https://books.google.com/books?isbn=0735200661) |
```

Every book listed MUST also appear in the `## BibTeX` section as a `@book` entry.

### BibTeX for Forum Posts

For forum posts, use `@online` with:
- `author` = forum username (in braces if pseudonym)
- `title` = thread title
- `url` = direct link to specific post (not just thread)
- `note` = "Forum post" or "MQL5 Code Base"
- `urldate` = access date

---

## Special Considerations

- Many trading indicators are **proprietary/closed-source** — forum discussions about reverse engineering are valuable primary sources
- **Decompiled code** posts are often the authoritative source for proprietary indicators (e.g., JMA)
- **Pine Script** implementations on TradingView are public and citable
- Beware **marketing content** disguised as analysis — many trading sites sell courses/subscriptions

---

## Provenance Sidecar

Write `trading-research/{slug}.provenance.md` listing every source consulted, whether it yielded results or not:

```markdown
# Provenance: {Name or Topic}

## Sources Consulted

| Source | Query | Results | Date |
|--------|-------|---------|------|
| TASC Author Archive | John F Ehlers | 45 articles | 2026-05-09 |
| MQL5 CodeBase | "ehlers" | 12 indicators | 2026-05-09 |
| ForexFactory | site:forexfactory.com "Ehlers" | 3 threads | 2026-05-09 |
| arXiv | "John Ehlers" trading | 0 results | 2026-05-09 |
...
```

This ensures reproducibility and makes it clear which sources were checked even if they returned nothing.
