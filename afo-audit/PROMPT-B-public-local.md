# Prompt B — Public/technical audit via Claude Code on your machine

Run locally (this repo cloned, or any folder) — the cloud session's network policy
blocks the domain, a local machine is unrestricted. Paste:

```text
Audit the public website https://afo.birdlife.org.au/afo/index.php/afo (Australian
Field Ornithology, an Open Journal Systems install by BirdLife Australia) so it can be
rebuilt on another platform. Work read-only, be polite to the server (sequential
requests, no parallel hammering). Write all outputs into a folder ./afo-audit/ and
produce a final report afo-audit/PUBLIC-AUDIT.md.

1. FINGERPRINT
   - Fetch the homepage; record the <meta name="generator"> tag (OJS version), page
     <title>, theme CSS paths, and any version hints in asset URLs.
   - Fetch /afo/index.php/afo/about and its sub-pages (editorial team, submissions,
     contact, policies) — save each as HTML and note the URL.
   - Fetch robots.txt and any sitemap (try /afo/index.php/afo/sitemap and /sitemap.xml).

2. FULL CONTENT INVENTORY via OAI-PMH (authoritative — prefer over scraping):
   - Endpoint: https://afo.birdlife.org.au/afo/index.php/afo/oai
   - ?verb=Identify — save response (confirms OJS version, repository info,
     earliest datestamp).
   - ?verb=ListMetadataFormats and ?verb=ListSets — save responses.
   - ?verb=ListRecords&metadataPrefix=oai_dc — page through ALL records using
     resumptionToken until exhausted. Save the raw XML pages, then parse into
     afo-audit/articles.csv with columns: identifier, datestamp, title, creators,
     date, sets, landing-page URL.
   - Report: total article count, records per year, oldest and newest record.

3. ISSUE ARCHIVE
   - Fetch /afo/index.php/afo/issue/archive (and paginate). List every issue:
     volume, number, year, issue URL. Save as afo-audit/issues.csv.
   - Open ONE recent article landing page and ONE old one; document the URL pattern
     for landing pages and PDF galleys (e.g. /article/view/<id> and
     /article/view/<id>/<galleyId>), and whether PDFs are behind a viewer.

4. URL / REDIRECT MAP
   - From everything gathered, write afo-audit/redirect-map.csv: every distinct
     public URL pattern (homepage, archive, issue, article, galley, about pages,
     search, login, RSS/Atom feeds) with an example URL and a column left blank
     for the new-platform target.

5. EXTERNAL FOOTPRINT
   - Check whether article pages expose Google Scholar meta tags (citation_title etc.)
     — critical to preserve for indexing.
   - Note any DOIs present on article pages (search the HTML for "doi.org").
   - Record the RSS/Atom feed URLs if linked.

6. REPORT afo-audit/PUBLIC-AUDIT.md: platform + version, content totals (issues,
   articles, per-year table), URL patterns + redirect map summary, indexing/SEO
   findings, and a "Migration risk register" (large PDF volume? mixed URL schemes?
   missing metadata years? anything odd).

When done, tell me the totals and offer to commit ./afo-audit/ to the git repo
mathewruahema-beep/birdlife on branch claude/website-audit-migration-6ymaha.
```
