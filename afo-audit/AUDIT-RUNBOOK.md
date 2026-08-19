# AFO Website Audit Runbook

Audit of **Australian Field Ornithology** (https://afo.birdlife.org.au/afo/index.php/afo)
ahead of a rebuild on another platform.

## What we know already

| Item | Detail |
|---|---|
| Platform | PKP Open Journal Systems (OJS) — PHP/MySQL, journal path `afo` |
| Journal | Australian Field Ornithology, BirdLife Australia |
| ISSNs | Print 1448-0107 · Online 2206-3447 |
| History | 1959 as *The Australian Bird Watcher*; current title since 2003; online-only since 2016 |
| Publication | Quarterly, open access |
| External indexing | Informit (coverage from ~2000), Google Scholar |
| Hosting | Separate from the WP Engine WordPress estate; not in Cloudflare/WordPress operator notes |

## Why two audit passes

- **Admin pass (signed-in)** — OJS version, plugins, users/roles, in-flight submissions,
  DOI/distribution config, native XML exports. Run via **Claude in Chrome** on a
  signed-in browser, or manually. Prompt: `PROMPT-A-admin-chrome.md`.
- **Public pass** — full content inventory (OAI-PMH harvest), issue archive, URL/redirect
  map, SEO/indexing footprint. Run via **Claude Code locally** (this remote session's
  egress policy blocks the domain). Prompt: `PROMPT-B-public-local.md`.

## Deliverables expected back in this folder

- `PUBLIC-AUDIT.md`, `articles.csv`, `issues.csv`, `redirect-map.csv` (public pass)
- `ADMIN-AUDIT.md` + native XML issue export, users export (admin pass)
- Then: consolidated migration-readiness report + platform gap analysis (done here)

## Key OJS endpoints

- User dashboard: `/afo/index.php/afo/user`
- Issue archive: `/afo/index.php/afo/issue/archive`
- OAI-PMH: `/afo/index.php/afo/oai` (`?verb=Identify`, `?verb=ListRecords&metadataPrefix=oai_dc`)
- Article pattern: `/afo/index.php/afo/article/view/<id>` (galley: `/<id>/<galleyId>`)

## Migration questions to settle (affect scope massively)

1. Does the new platform need the **peer-review workflow**, or is it an archive +
   publish-only rebuild (reviews handled elsewhere)?
2. Are **DOIs** registered (Crossref)? If yes, landing-page URLs must be preserved or
   redirected and Crossref metadata updated.
3. Must **Google Scholar indexing** be preserved? (Requires `citation_*` meta tags on
   article pages in the new platform.)
4. Who owns hosting/DNS for `afo.birdlife.org.au`, and where does TLS terminate?
5. Retention: do all ~25 years of issues migrate, or archive-freeze the old system?
