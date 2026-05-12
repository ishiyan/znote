# BibTeX Processing Workflow

How to parse, validate, and format a .bib file into styled reference output.

## Step 1: Parse the File

Read the .bib file and extract all entries. For each entry, capture:
- Entry type (@article, @book, @misc, etc.)
- Citation key
- All fields and their values

Handle common syntax issues gracefully:
- Unbalanced braces → flag as error
- Missing commas → infer from context
- Non-standard entry types (@Misc vs @misc) → normalize to lowercase

## Step 2: Validate Entries

For each entry, check against the rules in `../formatting/bibtex-rules.md`:

1. **Required fields present?** Flag missing required fields per entry type.
2. **Author format correct?** Verify `and` separators, `Last, First` format.
3. **Pages use double hyphen?** `123--145` not `123-145`.
4. **DOI format clean?** No URL prefix, no `doi:` prefix.
5. **Citation keys unique?** Flag duplicates.
6. **Capitalization protected?** Check for obvious proper nouns in titles without braces.

Output a validation report:
```
Validation Report:
  Total entries: 42
  Valid: 38
  Warnings: 3 (missing optional fields)
  Errors: 1 (missing required field: journal in Smith2023)
```

## Step 3: Detect Duplicates

Check for duplicates by:
1. Same DOI (strongest signal)
2. Same title (case-insensitive, normalized whitespace)
3. Same author + year + first significant title word

Flag but don't auto-remove — let user decide.

## Step 4: Enrich (Optional)

If user requests enrichment:
- **URL verification**: Check all URLs are live (see `url-verification.md`)
- **Google Books**: For @book entries, look up Google Books URL
- **Access dates**: Stamp "Accessed: YYYY-MM-DD" on web sources

## Step 5: Format Output

Convert each entry into the requested citation style (APA 7 by default).

### Mapping BibTeX fields → APA 7

| BibTeX field | APA 7 position |
|---|---|
| author | First element: Last, F. M., & Last, F. M. |
| year | In parentheses after authors |
| title | Sentence case, not italicized (articles) or italicized (books) |
| journal | Italicized, Title Case |
| volume | Italicized |
| number | In parentheses after volume, not italicized |
| pages | After number, en-dash |
| doi | As https://doi.org/... at end |
| url | At end if no DOI; add "Last accessed: YYYY-MM-DD" |
| publisher | After title for books |
| edition | In parentheses after title: (3rd ed.) |
| booktitle | For chapters: In E. Editor (Ed.), *Title* |

### Handling Missing Fields

- Missing DOI for post-2000 paper: flag as warning, output without DOI
- Missing pages: output without, flag as warning
- Missing year: use (n.d.)
- Missing author: start with title

## Step 6: Order and Output

**APA 7 / Chicago**: Alphabetical by first author last name.
**Nature / Vancouver / IEEE**: Order of first appearance in the citing document (if known) or alphabetical fallback.

Output format: Markdown with proper italics (`*...*`), or plain text.

---

## Example: Processing bibliography.bib

Given a .bib file with entries like:
```bibtex
@inproceedings{Shannon_1949,
  author = {Shannon, C. E.},
  booktitle = {Proceedings of the Institute of Radio Engineers (IRE)},
  title = {Communication in the presence of noise},
  volume = 37,
  pages = {10--21},
  year = 1949
}
```

Output (APA 7):
```
Shannon, C. E. (1949). Communication in the presence of noise. In *Proceedings of the Institute of Radio Engineers (IRE)* (Vol. 37, pp. 10–21).
```

Output (IEEE):
```
[1] C. E. Shannon, "Communication in the presence of noise," in Proc. Institute of Radio Engineers (IRE), 1949, vol. 37, pp. 10–21.
```
