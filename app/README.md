# BirdLife Companion

A companion app for [birdlife.org.au](https://birdlife.org.au) — installable web app
(PWA), no app stores, no build step, no framework. Three audiences in one shell:

| Tab | What it does | Data source |
|---|---|---|
| **News** | Live articles from the website: search, category filter, offline reading | Public `wp/v2` REST API |
| **Events** | Upcoming events, when the site exposes an events API; graceful link-out until then | `tribe/events/v1` or `wp/v2/events`, auto-detected |
| **Membership** | Public tiers with join/renew links today; member sign-in later via the Worker proxy | Config + (future) `worker/member-proxy.js` |
| **Staff** | Hidden tab — ICT quick links (ops dashboard, Ask Zeus queue, Asana) | Links only, no data |

The Staff tab is hidden until someone opens `#/staff` directly, then stays visible on
that device. It contains only links; every destination enforces its own sign-in.

## Running it

It is static files — any web server works:

```
cd app && python3 -m http.server 8000
# open http://localhost:8000
```

No API reachable? The header shows a **Demo data** badge and bundled sample content so
the UI stays reviewable. Real content loads automatically wherever birdlife.org.au is
reachable (`demoMode: 'auto'` in `js/config.js`).

## Deploying

Any static host. Two sensible options for BirdLife:

1. **Cloudflare Pages** (recommended) — the org already runs Cloudflare in front of
   WP Engine. Point Pages at this repo, build command none, output directory `app/`.
   A custom subdomain like `companion.birdlife.org.au` keeps it first-party.
2. **WP Engine subdirectory** — copy `app/` to e.g. `/companion/` on the existing site.
   Same-origin means CORS never comes up.

After any change to files listed in `sw.js`'s `SHELL`, bump `VERSION` in `sw.js` so
installed clients pick up the update.

## Architecture

```
app/                     static PWA (this directory)
  js/config.js           ALL environment-specific settings — API bases, tiers, links
  js/api.js              WP REST client: localStorage cache, timeouts, demo fallback
  js/app.js              hash router + views + HTML sanitiser
  sw.js                  service worker: shell precache, offline API/image cache
worker/                  Cloudflare Worker — future member API proxy (STUB)
  member-proxy.js        the only place WooCommerce keys will ever live (as secrets)
  wrangler.toml
```

Design decisions worth knowing:

- **No dependencies, no build.** The whole app is ~30KB of hand-written ES modules.
  Anyone on the team can read and change it; nothing to `npm audit` forever.
- **All WordPress HTML is sanitised** before touching the DOM (scripts, embeds,
  event handlers stripped), even though it comes from our own site.
- **Only core `wp/v2` endpoints are used.** The site's *ACF to REST API* plugin is
  known-vulnerable; nothing here depends on it.
- **Offline-first**: the shell is precached, API responses and images are cached
  stale-while-revalidate, and articles you've opened re-open offline.

## Membership: what's live vs. planned

Live now: tier cards (Individual / Concession / Family) linking to the website's
join flow. Prices sit in `js/config.js` and **must be confirmed with Supporter Care
before launch** — the public site has previously carried superseded prices.
Financial Hardship and Free tiers are deliberately not listed; they're Supporter
Care / Board controlled.

Planned: member sign-in showing tier, status and renewal date. That requires the
`worker/member-proxy.js` Worker deployed with an authentication flow (miniOrange
OIDC is the obvious fit since it's already in the stack). The Worker currently
returns `501 not_implemented` on purpose — the app degrades to link-out.

### Security rules (non-negotiable)

- **No credentials in this repo or in the client bundle, ever.** WooCommerce keys
  were previously exposed in routine prompts and had to be rotated; keys go in
  Worker secrets (`wrangler secret put …`) only.
- The Worker returns the minimum fields the app needs — no addresses, no payment
  data, no order history.
- Salesforce remains the system of record for membership; on disagreement,
  Salesforce wins.

## Known constraints

- This development sandbox cannot reach birdlife.org.au (network egress policy), so
  live-API behaviour — including whether the site sends CORS headers for cross-origin
  app hosting, and which events plugin (if any) exposes an API — is untested against
  production. First deploy should check both; a WP Engine subdirectory deploy
  sidesteps CORS entirely.
- Mobile PageSpeed of the main site is 46/100 — one more reason the app fetches JSON
  from the REST API rather than embedding site pages.
