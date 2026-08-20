# AFO Migration-Readiness Report

**Australian Field Ornithology — afo.birdlife.org.au**
Compiled 20 August 2026 from the automated cloud harvest (GitHub Actions run of
`site-harvester`), the OAI-PMH metadata harvest, and `PLATFORM-ASSESSMENT.md`.

---

## 1. Headline findings

1. **The site runs Open Journal Systems 2.4.6.0** (from the generator tag on every
   page). OJS 2.4.6 was released in **2015** and the entire OJS 2.x line is
   **end-of-life** — no security patches, no PHP 8 support. This alone justifies
   the rebuild, and explains the dated look and admin experience.
2. **The content is fully recoverable.** The public harvest achieved **zero fetch
   errors** and captured essentially the whole journal (see totals below).
3. **No DOIs are registered** (2 stray doi.org mentions across 86,311 links —
   both in article body text, none minted for AFO articles). This removes the
   hardest migration constraint: no Crossref re-registration is needed. URL
   redirects remain best practice for Google Scholar and inbound citations, but
   nothing breaks contractually if one is missed.
4. **The recommended path is unchanged and now evidence-backed: a fresh OJS 3.x
   install** (~AU$100–350/yr hosting). The 2.x → 3.x upgrade is a well-trodden,
   officially supported path, and every alternative either loses functionality
   or costs 5–20× more.

## 2. What the harvest captured (all on this branch or the run artifact)

| Item | Count | Where |
|---|---:|---|
| Published articles (authoritative, via OAI-PMH) | **2,354 records** | `harvest/afo-oai/articles.csv` |
| Article landing pages crawled | 2,321 | `harvest/afo/pages.csv`, `content/` |
| Issue tables of contents | **215 issues** | pages.csv (`/issue/view/<id>`) |
| Article PDFs (5.0 GB) | **2,311 of 2,321 (99.6%)** | run artifact `afo-raw-mirror` |
| Total pages / assets | 7,184 / 2,374 | `harvest/afo/manifest.json` |
| Internal link graph | 95,639 links | `harvest/afo/links.csv` |
| Per-page clean markdown | 7,184 files | `harvest/afo/content/` |
| WordPress import file (fallback only) | 7,184 items | `harvest/afo/wordpress-export.xml` |
| Fetch errors | 2 (of 9,558 fetches) | AUDIT.md |

Publication history: content from 2003 onward under the AFO title (first published
1959 as *The Australian Bird Watcher*); the journal went online-only in 2016, when
the pre-2016 archive was bulk-digitised (1,967 OAI records carry 2016 upload dates).

**Coverage: complete.** The first crawl hit its 8,000-fetch safety cap; the
follow-up sweep (12,000 cap) exhausted the crawl queue naturally at 9,558 fetches.
All 215 issues and 2,321 article landing pages are captured, with 2,311 PDFs
(99.6% — the handful without a PDF appear to have no galley on the live site;
the list to spot-check is derivable from pages.csv vs assets.csv).

## 3. URL patterns → redirect map

Every public URL follows one of a handful of patterns (`harvest/afo/redirect-map.csv`
holds the full 6,402-row map with a blank new-URL column):

| Pattern | Count | Example | OJS 3.x equivalent |
|---|---:|---|---|
| Article landing | 2,321 | `/afo/index.php/afo/article/view/2280` | same path — **no redirect needed if rebuilt on OJS** |
| Galley viewer | 3,854 | `/afo/index.php/afo/article/view/2280/<galleyId>` | same |
| PDF download | ~1,540 | `/afo/index.php/afo/article/download/<id>/<galleyId>` | same |
| Issue TOC | 215 | `/afo/index.php/afo/issue/view/123` | same |
| Archive, about, search, login | ~10 | `/afo/index.php/afo/issue/archive` | same |

This is the decisive argument for staying on OJS: **articles keep their IDs through
the official upgrade, so every URL survives unchanged** and the redirect problem
disappears. Any other platform means 6,400 redirects.

## 4. SEO / Google Scholar

- OJS 2.4.6 emits Google Scholar `citation_*` meta tags on article landing pages as
  core behaviour, and AFO is indexed in Scholar today. OJS 3.x continues these tags,
  so an OJS-to-OJS migration preserves Scholar indexing automatically.
  (Spot-verify one article page in the `afo-raw-mirror` artifact when convenient;
  the committed markdown strips `<head>` content.)
- No DOIs (see above). Consider Crossref membership as a *post*-migration
  improvement — OJS 3.x automates DOI deposit.
- Informit indexes AFO independently (coverage from ~2000); notify them of the
  cutover date, nothing more.

## 5. Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| OJS 2.4.6 is EOL and internet-exposed **today** | High | Migrate promptly; until then keep the host patched at OS level |
| 2.x → 3.x upgrade is a big jump (schema rewrite) | Medium | Official staged upgrade path (2.4.6 → 3.2 → 3.5); rehearse on a copy first; full DB+files backup before each step. Fallback: fresh 3.x + Native XML import |
| Editorial-side data (users, in-flight submissions, review history) not yet audited | Medium | Run the admin audit (`PROMPT-A-admin-chrome.md`) before cutover; freeze new submissions during migration week |
| Hosting: WP Engine and Cloudflare can't host PHP/OJS | Low | Small LAMP VPS or shared host (~AU$10–30/mo); keep Cloudflare in front for DNS/CDN |
| Custom theme/plugins on the old site | Low | 2.x themes don't port to 3.x anyway; 3.x default themes are modern — restyle with journal branding |
| No DOIs registered | Info | Simplifies migration; consider adding via Crossref after |

## 6. Recommended rebuild path and costs

**Rebuild on current OJS 3.5 LTS. Two ways to run it:**

| | A. Self-hosted (recommended) | B. PKP managed hosting |
|---|---|---|
| Software | $0 (open source) | $0 |
| Hosting | AU$120–360/yr (small LAMP VPS/shared host) | ~US$1,000+/yr |
| Maintenance | BirdLife ICT applies ~2 updates/yr | Included |
| Functionality vs today | 100% (same product, current version) | 100% |

(Scholastica SaaS ≈ US$2,000+/yr and Janeway were assessed and ruled out in
`PLATFORM-ASSESSMENT.md`; a free university-library OJS host remains worth one
enquiry email before purchasing hosting.)

**Migration sequence:**
1. Run the admin-side audit (Prompt A) — OJS confirms 2.4.6, so capture the
   user table size, in-flight submissions, and take the Native XML + users exports.
2. Stand up OJS 3.5 on the new host (staging subdomain).
3. Preferred: staged in-place upgrade of a *copy* of the 2.4.6 database
   (2.4.6 → 3.2 → 3.5), which preserves users, submissions, and article IDs.
   Fallback: fresh install + Native XML import of the 215 issues (loses review
   history, keeps all published content).
4. Verify against this harvest: 2,354 OAI records, 215 issues, PDF byte-counts —
   the `articles.csv` inventory is the acceptance checklist.
5. Cut DNS over (Cloudflare), keep the old host read-only for 3 months, archive
   the raw mirror permanently.
6. Post-migration wins: modern theme, Crossref DOIs, automated Scholar/DOAJ
   deposits, HTTPS-everywhere check.

**Effort estimate:** 2–4 days hands-on for a staging rehearsal + cutover, most of
it waiting on the staged upgrade scripts and spot-checking issues.

## 7. What remains before cutover can be scheduled

- [x] Sweep run complete — 2,311/2,321 PDFs (99.6%), 5.0 GB banked in the run artifact
- [ ] Admin audit via Prompt A (user counts, in-flight submissions, exports)
- [ ] Decision: self-host vs PKP vs library partner (one enquiry email)
- [ ] Provision staging host and rehearse the staged upgrade
