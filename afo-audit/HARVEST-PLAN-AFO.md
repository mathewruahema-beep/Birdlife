# AFO Harvest Plan

One command, run locally: `bash afo-audit/harvest-afo.sh`
(cloud sessions can't reach the domain; any laptop on a normal network can).

## What it runs and why

**Pass 1 — OAI-PMH metadata harvest** (`oai_harvest.py`, ~2 minutes).
OJS publishes an OAI-PMH feed at `/afo/index.php/afo/oai` listing every published
article with title, authors, date, and landing URL. This is the *authoritative*
content inventory — if the crawl misses a page, this catches it. Output:
`harvest/afo-oai/articles.csv` + per-year counts.

**Pass 2 — full site crawl** (`harvest.py`, 1–2 hours at 0.5 s/request).
Mirrors the public site: issue archive, article landing pages, galley PDFs, about
pages, theme assets. Output: offline mirror (`raw/`), per-page markdown
(`content/`), inventories, redirect-map template, `AUDIT.md`.

## AFO/OJS-specific expectations

- **Scale**: AFO has published since 2003 online (~4 issues/yr). Expect roughly
  800–1,500 articles → landing page + PDF each, plus ~90 issue pages. The 8,000
  fetch cap has comfortable headroom; if AUDIT.md shows it was hit, re-run with
  `--max-pages 15000`.
- **PDFs**: OJS serves galleys via `/article/view/<id>/<galleyId>` (HTML viewer)
  and `/article/download/<id>/<galleyId>` (the actual PDF). The crawler follows
  both; the PDFs land in `raw/` and `assets.csv`. Expect several GB total.
- **Crawl traps that are safely ignored**: `/search` result pages with query
  strings and `/login`/`/user/register` pages will be fetched once each (they're
  same-site links) but don't explode — OJS search links are bounded. If the crawl
  seems to wander, check `pages.csv` for `search` URLs and just note it.
- **What this does NOT capture**: the signed-in editorial side — submissions in
  progress, peer-review records, user accounts, email templates. That comes from
  the OJS admin export (`PROMPT-A-admin-chrome.md`). Both are needed for a full
  migration; only Pass 1+2 are needed to rebuild the public archive.

## Success checklist

- [ ] `articles.csv` row count looks right (compare oldest year to first online issue)
- [ ] `AUDIT.md` platform fingerprint says OJS and shows the generator version
- [ ] Spot-check 2–3 PDFs in `raw/` open correctly
- [ ] `pages.csv` contains the issue archive pages (`/issue/view/...`)
- [ ] Results committed back to `claude/website-audit-migration-6ymaha`

## After the harvest

Bring `articles.csv`, `AUDIT.md`, `manifest.json`, and the CSVs back to this repo
(the run script prints the exact git commands). Claude then produces:
1. The consolidated migration-readiness report (content volumes, redirect map, risks)
2. The concrete OJS rebuild plan (hosting shortlist, import steps, cutover sequence)
   per `PLATFORM-ASSESSMENT.md`
