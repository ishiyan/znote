# URL Verification and Access-Date Stamping

Verify that URLs in references are accessible, and stamp the access date.

## When to Verify

- Processing a .bib file with `url` fields
- Formatting a reference list that includes web sources
- User explicitly asks to check URL liveness
- Before publishing: run verification on all non-DOI URLs

## Process

### 1. Extract URLs

From a .bib file, extract:
- `url` fields
- `howpublished` fields containing URLs
- DOI-derived URLs (`https://doi.org/` + doi field)

From a reference list (plain text/markdown):
- Any `http://` or `https://` URL
- DOI links

### 2. Check Liveness

For each URL:
1. Send HTTP HEAD request (faster than GET)
2. If HEAD fails, try GET
3. Record response:
   - **200–299**: URL is live
   - **301/302**: Follow redirect, record final URL
   - **403**: May be live but access-restricted (note as "restricted")
   - **404/410**: Dead link — flag as error
   - **Timeout**: Flag as "unreachable"

### 3. Stamp Access Date

For live URLs:
- Add `note = {Accessed: YYYY-MM-DD}` to the .bib entry (if processing .bib)
- Add "Last accessed: YYYY-MM-DD" to the formatted reference (if producing output)
- Use today's date as the access date

### 4. Handle DOIs Separately

DOIs are permanent identifiers. Rules:
- Verify DOI resolves: `https://doi.org/[DOI]` should return 200 or redirect to publisher
- DOI sources don't need "last accessed" dates (they're permanent)
- If DOI is broken, flag as error — this suggests the DOI is wrong

### 5. Report

```
URL Verification Report:
  Total URLs checked: 15
  Live: 12
  Redirected: 1 (updated final URL)
  Restricted (403): 1
  Dead (404): 1 — [url] in entry [citation_key]
  DOIs verified: 8/8

Dead URLs:
  - [citation_key]: http://example.com/old-page → 404
    Suggestion: Check Wayback Machine or find new URL

Redirected URLs:
  - [citation_key]: http://old.com/page → https://new.com/page
    Updated in output.
```

## APA 7 Rules for Access Dates

APA 7 requires retrieval dates only when content may change over time:
- Websites without DOIs: include "Last accessed: YYYY-MM-DD"
- Social media posts: include access date
- Wiki pages: include access date
- Journal articles with DOIs: NO access date needed
- Books with DOIs: NO access date needed

For this skill, we're slightly more aggressive: stamp access dates on all non-DOI URLs, because we're primarily producing references for technical articles where URL stability matters.

## Wayback Machine Fallback

If a URL is dead (404):
1. Check `https://web.archive.org/web/[URL]` for archived version
2. If found: suggest using the archived URL as an alternative
3. Format: `Archived at: https://web.archive.org/web/YYYYMMDD/[original URL]`
