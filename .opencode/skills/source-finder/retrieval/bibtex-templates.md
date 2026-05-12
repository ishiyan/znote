# BibTeX Templates

Templates for generating BibTeX entries for every source type. Every result delivered by source-finder MUST include a BibTeX entry.

## Journal Article

```bibtex
@article{author2024keyword,
  author    = {Last, First and Last, First},
  title     = {Article Title},
  journal   = {Journal Name},
  year      = {2024},
  volume    = {10},
  number    = {3},
  pages     = {123--145},
  doi       = {10.1234/example},
  url       = {https://doi.org/10.1234/example}
}
```

## arXiv Preprint

```bibtex
@misc{author2024keyword,
  author        = {Last, First and Last, First},
  title         = {Paper Title},
  year          = {2024},
  eprint        = {2401.12345},
  archiveprefix = {arXiv},
  primaryclass  = {cs.AI},
  url           = {https://arxiv.org/abs/2401.12345}
}
```

## Conference Paper

```bibtex
@inproceedings{author2024keyword,
  author    = {Last, First and Last, First},
  title     = {Paper Title},
  booktitle = {Proceedings of Conference Name},
  year      = {2024},
  pages     = {1--10},
  doi       = {10.1234/example},
  url       = {https://doi.org/10.1234/example}
}
```

## Book

```bibtex
@book{author2024keyword,
  author    = {Last, First},
  title     = {Book Title},
  publisher = {Publisher Name},
  year      = {2024},
  isbn      = {978-0-123456-78-9},
  url       = {https://...}
}
```

## Website / Blog Post / Online Resource

```bibtex
@online{author2024keyword,
  author  = {Last, First},
  title   = {Page or Post Title},
  year    = {2024},
  url     = {https://example.com/page},
  urldate = {2024-12-01},
  note    = {Blog post on Medium}
}
```

## Forum Post

```bibtex
@online{username2024keyword,
  author  = {{ForumUsername}},
  title   = {Thread Title},
  year    = {2024},
  url     = {https://forum.example.com/thread/123#post456},
  urldate = {2024-12-01},
  note    = {Forum post on MQL5}
}
```

## GitHub Repository

```bibtex
@software{author2024reponame,
  author  = {Last, First},
  title   = {Repository Name},
  year    = {2024},
  url     = {https://github.com/user/repo},
  version = {1.2.3},
  urldate = {2024-12-01}
}
```

## Social Media Post

```bibtex
@online{author2024keyword,
  author  = {Last, First},
  title   = {Post text (first 50 chars)...},
  year    = {2024},
  url     = {https://x.com/user/status/123456},
  urldate = {2024-12-01},
  note    = {Post on X/Twitter}
}
```

## Technical Report / White Paper

```bibtex
@techreport{author2024keyword,
  author      = {Last, First},
  title       = {Report Title},
  institution = {Organization Name},
  year        = {2024},
  url         = {https://...},
  urldate     = {2024-12-01}
}
```

## Citation Key Convention

Format: `{firstauthor_lastname}{year}{keyword}`

- Lowercase, no spaces
- Keyword = 1-2 descriptive words from title
- Examples: `jurik1999jma`, `smith2024adaptive`, `tensorflow2024docs`

## Required Fields by Source Type

| Source | Must have |
|--------|-----------|
| Journal article | author, title, journal, year, doi |
| Preprint | author, title, year, eprint, archiveprefix |
| Website | author (or org), title, year, url, urldate |
| Forum post | author (username), title, year, url, urldate, note |
| GitHub repo | author, title, year, url, urldate |
| Book | author, title, publisher, year |
