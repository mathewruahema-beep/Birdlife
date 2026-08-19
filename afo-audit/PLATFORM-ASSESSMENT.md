# AFO Rebuild — Platform Assessment (pre-audit)

Goal: rebuild https://afo.birdlife.org.au with **the same functionality**, on a free
platform if possible, otherwise the most cost-effective one.

## What "same functionality" means here

The site is PKP **Open Journal Systems (OJS)**. Functional parity means all of:
author submission portal · editorial workflow + peer review (roles: manager, editor,
section editor, reviewer, author, reader) · issue-based open-access publishing ·
searchable archive back to 2003+ · OAI-PMH metadata feed · Google Scholar
citation meta tags · user accounts/registration · email notifications.

## The core finding

**The current software is already free.** OJS is open source ($0 licence). The only
real costs are hosting and maintenance. No free *hosted* service (Wix, WordPress.com,
GitHub Pages, Cloudflare Pages…) provides a peer-review workflow — a truly free
platform exists only if the functionality is cut down to a static archive, or if a
partner (e.g. a university library OJS service) hosts it gratis.

## Options compared (AUD approx., 2026)

| Option | Software | Hosting/yr | Maintenance | Functional parity |
|---|---|---|---|---|
| **A. Fresh OJS 3.5 on shared/VPS hosting** | $0 | ~$100–350 | You apply updates (~2×/yr) | 100% |
| **B. PKP Publishing Services (official hosted OJS)** | $0 | ~US$1,000+ | Fully managed, upgrades incl. | 100% |
| **C. Janeway (open source, Birkbeck)** | $0 | ~$100–350 (Python host) | You maintain | ~95% (different UX; migration harder) |
| **D. Scholastica SaaS** | — | US$99/mo OA platform + US$250/yr + US$10/submission peer review ≈ US$2,000+/yr | Fully managed | High, but proprietary lock-in |
| **E. Static archive (GitHub/Cloudflare Pages) + external submissions** | $0 | $0 | Minimal | ❌ loses submission/review/login |
| **F. University library OJS partner hosting** | $0 | $0 (if partner agrees) | Partner | 100% |

## Recommendation

**Option A** — a clean install of current OJS (3.4/3.5 LTS) on modest LAMP hosting,
importing content via Native XML export from the existing site. Rationale:
- Only path with guaranteed 100% functional parity, because it *is* the same product.
- If the motivation for "another platform" is that the current install feels old/clunky,
  that is almost certainly an outdated OJS version, not OJS itself — 3.x is a full rework.
- Cheapest real-money option (~$10–30/month). BirdLife's existing WP Engine (WordPress-only)
  and Cloudflare (no PHP runtime) cannot host it, so a small separate host is needed either way.
- Escape hatches preserved: content stays in open formats (Native XML, OAI-PMH), so a later
  move to B (managed) or D (SaaS) stays easy.

Worth one email before committing: **Option F** — Australian university libraries
(e.g. those running OJS services for society journals) sometimes host at no cost;
BirdLife's research partnerships may qualify.

## Is the audit still needed? Yes — for the migration, not the platform choice

The platform decision above holds regardless of audit results. The audit determines
**migration effort and completeness**:

Must-have (admin pass, Prompt A):
1. **Exact current OJS version** — determines the upgrade/import path (OJS 2.x → 3.x
   needs a staged upgrade or XML crosswalk; 3.x → 3.x is near-trivial).
2. **Native XML export of all issues** — this IS the migration payload (metadata + galleys).
3. **DOI/Crossref config** — if DOIs exist, landing URLs must be redirected and Crossref updated.
4. **Plugin list & theme** — identifies custom functionality to replicate.
5. **User export + role counts** — decides whether accounts migrate or users re-register.
6. **Active submissions count** — in-flight peer reviews constrain cutover timing.

Nice-to-have (public pass, Prompt B): full URL inventory for the redirect map,
OAI harvest as a fallback payload if the admin export fails, per-year content volumes.

**Minimum viable audit** if time is short: System Information screenshot (item 1)
+ Native XML export (item 2) + a copy of the galley PDFs. Everything else can be
reconstructed from the public site.
