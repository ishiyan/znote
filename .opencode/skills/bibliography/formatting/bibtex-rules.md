# BibTeX Rules

Entry types, required fields, formatting conventions, and common mistakes.

## Entry Types

### @article — Journal Articles

**Required**: author, title, journal, year
**Recommended**: volume, number, pages, doi

```bibtex
@article{Jumper2021,
  author  = {Jumper, John and Evans, Richard and Pritzel, Alexander and others},
  title   = {Highly Accurate Protein Structure Prediction with {AlphaFold}},
  journal = {Nature},
  year    = {2021},
  volume  = {596},
  number  = {7873},
  pages   = {583--589},
  doi     = {10.1038/s41586-021-03819-2}
}
```

### @book — Books

**Required**: author OR editor, title, publisher, year
**Recommended**: edition, address, isbn, url

```bibtex
@book{Oppenheim2010,
  author    = {Oppenheim, Alan V. and Schafer, Ronald W.},
  title     = {Discrete-Time Signal Processing},
  publisher = {Pearson},
  year      = {2010},
  edition   = {3},
  isbn      = {978-0-13-198842-2}
}
```

### @inproceedings — Conference Papers

**Required**: author, title, booktitle, year
**Recommended**: pages, address, doi

```bibtex
@inproceedings{Vaswani2017,
  author    = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and others},
  title     = {Attention is All You Need},
  booktitle = {Advances in Neural Information Processing Systems 30},
  year      = {2017},
  pages     = {5998--6008}
}
```

### @incollection — Book Chapters

**Required**: author, title, booktitle, publisher, year
**Recommended**: editor, pages, chapter

### @phdthesis / @mastersthesis — Theses

**Required**: author, title, school, year

### @misc — Everything Else

Preprints, datasets, software, websites, forum posts.

**Required**: author (if known), title, year
**Recommended**: howpublished, url, doi, note

```bibtex
@misc{tslab2010jma,
  author       = {{tsLab forum}},
  title        = {{JMA} code},
  year         = {2010},
  howpublished = {Forum post},
  url          = {https://forum.tslab.ru/ubb/ubbthreads.php?ubb=showflat&Number=5796},
  note         = {Accessed: 2025-04-12}
}
```

### @online — Web Resources (biblatex only)

**Required**: author OR organization, title, url, year

```bibtex
@online{JurikHowItWorks,
  author = {Jurik, Mark},
  title  = {How it works},
  url    = {http://jurikres.com/faq1/faq_ama.htm#how_work},
  year   = {1999},
  note   = {Accessed: 2025-04-12}
}
```

---

## Formatting Conventions

### Author Names
- Format: `Last, First` separated by `and`
- Wrong: semicolons, commas between authors, ampersands
- 10+ authors: `{First, A. and Second, B. and ... and others}`
- Organizations: double braces `{{World Health Organization}}`

### Titles
- Protect capitalization with braces: `{AlphaFold}`, `{DNA}`, `{Python}`
- Sentence case in the .bib file (style will adjust)

### Pages
- En-dash via double hyphen: `123--145`
- Not: `123-145` (single hyphen) or `pp. 123--145`

### DOIs
- Just the identifier: `10.1038/nature12345`
- Not: `https://doi.org/10.1038/nature12345` or `doi:10.1038/nature12345`

### Citation Keys
- Convention: `FirstAuthorYEARkeyword`
- Examples: `Shannon1949`, `Oppenheim2010dsp`, `Vaswani2017attention`
- Alphanumeric plus `-`, `_`, `.`, `:`
- Must be unique within file

### Months
- Three-letter unquoted abbreviations: `month = jan`

---

## Common Mistakes

| Mistake | Wrong | Correct |
|---------|-------|---------|
| Author separator | `Smith, J.; Doe, J.` | `Smith, John and Doe, Jane` |
| Missing comma | field without trailing `,` | comma after every field except last |
| Single hyphen pages | `123-145` | `123--145` |
| DOI with URL | `https://doi.org/...` | `10.1038/...` |
| Unprotected caps | `{AlphaFold}` missing braces | `{AlphaFold}` |
| Redundant pp. | `pp. 123--145` | `123--145` |

---

## Validation Checklist

When processing a .bib file, check:
- [ ] All required fields present for each entry type
- [ ] Author names use `and` separator
- [ ] Pages use `--` (double hyphen)
- [ ] DOIs are bare identifiers (no URL prefix)
- [ ] Citation keys are unique
- [ ] Proper nouns / acronyms protected with braces in titles
- [ ] No duplicate entries (same DOI or same author+title+year)
- [ ] Balanced braces throughout
- [ ] Commas between fields (not after last field)
