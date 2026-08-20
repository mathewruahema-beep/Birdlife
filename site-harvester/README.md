# BirdLife Site Harvester

Point it at any website and it pulls down **everything** — pages, images, PDFs,
stylesheets — and turns it into migration-ready output so the site can be rebuilt
on a new platform. Built for updating BirdLife's outdated websites
(AFO journal, microsites, legacy pages).

## Quick start (run on your own machine — the Claude cloud session cannot reach these domains)

```bash
cd site-harvester
pip3 install -r requirements.txt

# Basic harvest
python3 harvest.py https://afo.birdlife.org.au/afo/index.php/afo --out ./harvest/afo

# Harvest + WordPress import file, larger site
python3 harvest.py https://some-old-site.birdlife.org.au \
    --out ./harvest/oldsite --max-pages 5000 --wxr
```

## What you get

| File | What it is | Use it for |
|---|---|---|
| `AUDIT.md` | Human-readable audit summary | First look: platform, size, biggest pages |
| `manifest.json` | Platform fingerprint + stats | Detects WordPress/OJS/Drupal/Joomla/Wix/Squarespace |
| `content/*.md` | One clean markdown file per page | **The migratable content** — paste into any new CMS |
| `raw/` | Byte-exact mirror of every page/asset | Reference copy, offline archive, diffing |
| `pages.csv` | Every page: URL, title, description, word count | Content inventory / what-to-keep decisions |
| `assets.csv` | Every image, PDF, CSS, JS with sizes | Asset migration checklist |
| `links.csv` | Full internal link graph | Finding orphan pages, fixing navigation |
| `redirect-map.csv` | Old URL → (blank) new URL | Fill in as you build the new site; becomes your 301 map |
| `wordpress-export.xml` | WXR import file (with `--wxr`) | WordPress: Tools → Import → WordPress. Pages arrive as drafts |

## Options

```
--max-pages N          fetch cap, pages + assets (default 2000)
--delay S              seconds between requests (default 0.5 — be polite)
--include-subdomains   follow links to *.same-domain
--extra-root URL       treat another root as in-scope (repeatable)
--wxr                  also emit wordpress-export.xml
--ignore-robots        skip robots.txt (only on sites we own)
```

## Notes and limits

- **Read-only** and sequential; default 0.5s delay. Safe to run against production.
- Honours `robots.txt` by default.
- Captures what the server sends (server-rendered HTML). JavaScript-only content
  (React/Vue SPAs) won't be in the extracted markdown — the raw mirror still
  captures the JS, but for SPAs use a headless-browser pass instead.
- **Login-protected areas are not captured** — it harvests the public site.
  For the AFO journal's editorial side (submissions, peer review, users), use the
  platform's own export tools (see `afo-audit/PROMPT-A-admin-chrome.md`).
- Dynamic *functionality* (search, forms, checkout, peer review) is inventoried
  but not replicated — the harvest tells you what needs rebuilding; the platform
  choice (see `afo-audit/PLATFORM-ASSESSMENT.md`) decides how.

## Typical workflow for one site

1. Harvest: `python3 harvest.py <url> --out ./harvest/<name> --wxr`
2. Read `AUDIT.md`, skim `pages.csv` — decide keep / cut / rewrite per page.
3. Build the new site; import `wordpress-export.xml` or paste from `content/`.
4. Fill `redirect-map.csv`, load as 301 redirects (Cloudflare Bulk Redirects works well).
5. Keep `raw/` as the permanent archive of the old site.
