---
name: birdlife-wpengine
description: "Expert operator knowledge for BirdLife Australia's WP Engine account: every User Portal area and what it controls, the five caching layers, network tiers and Web Rules, the SSH/WP-CLI/GitPush/API toolchain, the live seven-environment estate, and the four-tier review playbook for making the sites measurably better. Trigger on WP Engine, my.wpengine.com, User Portal, EverCache, Edge Full Page Cache, Global Edge Security, Web Rules, Smart Plugin Manager, cache hit ratio, error rate, PHP version, SSH gateway, GitPush, SFTP port 2222, backups, birdlifeaus, birdlifestage, birdlifeaoc, awsg, site speed, Lighthouse, or any question about hosting, promotion between environments, or why a WordPress page is slow."
---

# BirdLife Australia — WP Engine

This is the **platform** layer. `birdlife-wordpress` covers what is inside WordPress (plugins, users, WooCommerce, the miniOrange sync, the membership rebuild). This skill covers the host: caching, edge, environments, deployment, limits and the portal itself. When a question spans both, read both and say which layer the answer sits in.

There is **no WP Engine MCP connector**. Work through the User Portal in the browser, the Customer API, or SSH. Always say which you used. Every figure below was read live on **11 September 2026** and must be re-verified before quoting.

Reference document: **IT-WEB-001 WP Engine Mastery Reference** in Mathew's Google Drive (ADR 0021; not found there on 12 Sep 2026, ask Mathew).

---

## 1. The estate

Four Sites, seven environments. All on WordPress 7.0.4.

| Site | Env | Install | Domain | PHP | Storage |
|---|---|---|---|---|---|
| Awsg | PRD | `awsg` | awsg.org.au | **7.4 (EOL)** | 782 MB |
| Birdlife AOC | PRD | `birdlifeaoc` | aoc.org.au | 8.2 | 920 MB |
| Birdlife AOC | STG | `birdlifeaocstg` | birdlifeaocstg.wpenginepowered.com | 8.4 | 381 MB |
| Birdlife AOC | DEV | `birdlifeaocdev` | birdlifeaocdev.wpenginepowered.com | 8.2 | 202 MB |
| birdlifeaus | PRD | `birdlifeaus` | birdlife.org.au | 8.4 | **17.25 GB** |
| birdlifeausstage | STG | `birdlifestage` | birdlifestage.wpengine.com | 8.4 | 7.91 GB |

`birdlifeaus`: eCommerce plan, region Asia/Pacific, created 31 Oct 2022. Files 14.58 GB, DB 2.67 GB. 729 GB bandwidth / 30 days. 180,505 billable visits, 874,734 total (daily avg 28,217).

**The defect to state every time promotion comes up:** `birdlifeaus` and `birdlifeausstage` are **two separate Sites**, each with one environment. `birdlifeaus` has its Staging and Development slots empty. Because they are not in the same Site, WP Engine's native environment **Copy** is unavailable between them, so every staging-to-production promotion is manual. That is the structural cause of the Salesforce ID remapping, the `-STAGING` SKU suffixes and the 1-day-vs-1-year subscription divergence. Birdlife AOC is configured correctly (PRD+STG+DEV in one Site) — the right pattern already exists in the account.

---

## 2. The User Portal, area by area

Install URLs follow `my.wpengine.com/installs/<envname>/<page>`. The page slugs are not obvious; these are the real ones:

| Portal area | URL slug | What it controls |
|---|---|---|
| Overview | *(none)* | Plan features, Lighthouse, usage, password protection, SSH key add, technical contact |
| eCommerce | `ecommerce` | EverCache for Woo, Live Cart, Dynamic Plugin Loading, Stripe Connect/Checkout, slow query monitor |
| Domains | `domains` | Domain list, Network tier, DNS status, SSL status, EFPC per domain, redirects |
| SSL | `ssl` | Certificates, Let's Encrypt (Legacy Network only), third-party import |
| Plugins and themes | `plugins_and_themes` | Full inventory, versions, **security risk flags**, bulk update, SPM entry |
| Backups | `backup_points` | Daily checkpoints, manual checkpoints, restore, prepare ZIP |
| Users and SFTP | `users_summary` | Environment users and roles, SFTP users |
| Cache | `cache_dashboard` | Clear page/network/object/all, EFPC toggle, object cache toggle, cache exclusions |
| Site migration | `site_migration` | Migration tooling |
| Performance | `performance` | **Score, cache hit ratio, error rate, latency, slow pages, slow queries** |
| Usage | `usage` | Storage, bandwidth, visits, overage |
| Logs | `logs` | Error and access logs (export only, no live tail) |
| GitPush | `gitpush` | Git remote setup per environment |
| Utilities | `utilities` | **Alternate Cron**, phpMyAdmin, misc |
| Web rules | `wren` | Access / Header / Rewrite rules, XML-RPC toggle, copy rules between envs |
| Redirect rules | `redirect_rules` | Simple domain redirects |

Account level: `/sites`, `/billing`, `/settings`. `/modify_plan` redirects to `/cart` and often renders empty — go through Billing instead.

**Portal gotcha:** guessing URL slugs mostly 404s (`/cache`, `/backups`, `/caching` are all wrong). Use the left nav or the slugs above.

---

## 3. The five caching layers

Most WP Engine performance problems are caching problems, and most caching mistakes come from treating it as one cache.

1. **Page cache (EverCache)** — Varnish-derived, at origin, **10 min TTL**.
2. **Object cache** — DB query results. **1 MB buffer, no TTL**, oldest evicted first. Keep autoloaded `wp_options` under **~800 KB** or you evict useful results with option data on every request, and at the extreme generate 502s.
3. **Network cache (CDN)** — Cloudflare on Advanced Network / GES. Static assets 365-day TTL.
4. **Edge Full Page Cache** — HTML cached at the Cloudflare edge, 10 min TTL. **Primary domain only by default**; enable per domain from the Domains page.
5. **Browser cache** — 365 days on static assets, minimum settable 600 s.

**Never cached, by design:** `/wp-admin/`, `/wp-login.php`, any slug named cart/checkout/store/check-out, any request with a `wordpress_*` logged-in cookie, and WooCommerce-specific pages and query args. A cart page costs a PHP worker on every single hit. That is the exact mechanism behind the July 2026 cart flood.

**Exclusions** (Path regex / Argument / Cookie) only make pages *less* cached. There is no switch that forces a page to cache — making a page cacheable means removing what disqualifies it, in the application.

**Purging:** Portal (per layer) · WP Admin bar (page + CDN, **not object**) · API `POST /installs/{id}/purge_cache` · PHP `wpecommon::purge_varnish_cache()` · `?a=b` bust.

**Woo-specific:** `EverCache for WooCommerce` **On**. `Live Cart for WooCommerce` **Off** — Live Cart bypasses the cart-fragments AJAX script that fires an uncached `admin-ajax` request on every page load. On a store with a flood history this is mitigation, not a nice-to-have.

---

## 4. Network, edge and Web Rules

| Tier | Cost | Includes |
|---|---|---|
| Legacy Network | included, retiring | WPE proprietary edge, **no CDN**, Let's Encrypt |
| Advanced Network | **free** | Cloudflare CDN, EFPC, HTTP/3, tiered caching, baseline bot mitigation, WAF, Polish |
| Global Edge Security | paid add-on | + Argo routing, customisable bot management, enhanced DDoS, extra managed WAF rules, Edge Traffic Rules dashboard, Under Attack Mode |

GES WAF is managed OWASP ModSecurity at the edge. Running a second WAF (Sucuri etc.) behind it is discouraged. Origin IP is hidden behind Cloudflare.

**Cloudflare error codes:** 520 connection error · 521 refused · 522 handshake timeout · 523 unreachable · 524 origin >100 s · 525/526 SSL. **522 and 524 are your origin, not Cloudflare.**

### Web Rules Engine
`.htaccess` is not the control surface on WP Engine; WREn replaced it. Three families: **Access** (IP/GeoIP allow-deny), **Header**, **Rewrite** (301/302 or internal, regex with named groups `(?P<name>…)`). Soft cap ~1,000 rewrite rules.

**Evaluation is top to bottom, first match wins.** An exception placed *below* a broad deny never fires. Every allow-list exception must sit **above** its deny.

**Live on `birdlifeaus`:** rank 0 Deny All "Block cart remove_item flood" (`URI ~ ^/cart` + 2 conditions); rank 1 Allow `125.254.72.66/.67/…` "Whitelisting Precision Group IP". If the allow is meant as an exception to the deny it is in the wrong position. Flag this whenever web rules come up until it is reviewed and commented.

**Where a control belongs:** anything whose job is to stop traffic reaching PHP belongs at the **Cloudflare edge**, not in Web Rules, because an origin rule still consumes a connection to evaluate. Moving the flood rule to Cloudflare remains open.

---

## 5. Limits that shape design

| Item | Value |
|---|---|
| PHP supported 2026 | 7.4 (EOL), 8.2, 8.4 |
| Max execution time | **60 s, can only be lowered** |
| PHP memory | 40 MB default, 512 MB max via wp-config |
| `max_input_vars` | 10,000, fixed |
| Upload | 50 MB default, 256 MB by support request |
| File permissions | dirs `0775`, files `0664`, hard capped — a plugin asking `777` fails |
| Image resize | 8000×8000 px / 40 MP |
| Backups | daily + manual, **30-day retention** |
| Visitor overage | USD $2 per 1,000 |

**Blocked:** root/sudo, system crontab, raw log tailing, public access to `.htaccess` / `wp-config.php` / `debug.log` / `._wpeprivate/` / PHP in `wp-content/uploads`. The `disable_functions` list and system username are deliberately unpublished.

**Disallowed plugins** worth knowing by reason: caching conflicts (W3 Total Cache, WP File Cache) · backup duplication (WP DB Backup, BackupWordPress, VersionPress) · excessive DB writes (WP PostViews, MyReviewPlugin, LinkMan) · related-posts query load (Similar Posts, Contextual Related Posts) · **security (WP phpMyAdmin, Sweet Captcha, TimThumb, Uploadify)** · needs PHP sessions + system cron (Digital Access Pass).

**Cron:** WP's pseudo-cron is unreliable on a cached site. WP Engine's **Alternate Cron** is a real server-side service curling `wp-cron.php` **every 60 s**, and sets `define('DISABLE_WP_CRON', true);`. Toggle at Utilities. **If scheduled tasks are unreliable, check this before touching plugin code.**

**Backups reality for DR:** restore is whole-environment. **Per-table partial restore is not a feature** — the workaround is download ZIP, unzip, SFTP directories back or import `mysql.sql` selectively. Prepared ZIPs live 7 days. IT-BCP-001 must state WordPress RPO = 24 h and granularity = whole environment, which is a different risk profile from the Veeam-backed Salesforce position and must not be described in the same sentence.

---

## 6. Developer toolchain

```bash
# SSH — ED25519 keys ONLY, RSA/SHA-1 rejected
ssh <envname>@<envname>.ssh.wpengine.net
ssh-keygen -t ed25519
```
Keys attach to a **portal user**, not an install: one key reaches every environment that user can access. Available: WP-CLI, MySQL CLI, bash, vi, grep, scp/rsync, Composer. Not available: root, sudo, raw logs, portal admin functions.

```bash
wp search-replace 'https://old' 'https://new' --dry-run   # ALWAYS dry-run first
wp db query "SELECT option_name, LENGTH(option_value) sz FROM wp_options WHERE autoload='yes' ORDER BY sz DESC LIMIT 25;"
wp cache flush                                  # object cache only
wp plugin list --skip-plugins --skip-themes     # when a broken plugin blocks CLI
```
That `wp db query` is the fastest way to find what is filling the 1 MB object-cache buffer.

**GitPush** (current in 2026, not deprecated): `git remote add wpe git@git.wpengine.com:<envname>.git`. One remote per environment. `.gitignore` must exclude core, `wp-content/uploads`, `wp-config.php`, `object-cache.php`, binaries, secrets. **Never manage the same files with both SFTP and Git** — SFTP edits are invisible to Git and a later push silently overwrites newer work with no warning.

**SFTP:** `<envname>.sftp.wpengine.com`, **port 2222 only**. Per-environment credentials, scopable to a subdirectory, usernames immutable, passwords unrecoverable.

**GitHub Actions:** `wpengine/github-action-wpe-site-deploy@v3`, secret `WPE_SSHG_KEY_PRIVATE`, inputs `WPE_ENV`, `SRC_PATH`, `REMOTE_PATH`, `PHP_LINT`, `CACHE_CLEAR`, `FLAGS`, `SCRIPT`. **Always set `PHP_LINT: TRUE`** — a free syntax gate before anything touches a live environment.

**Customer API:** `https://api.wpengineapi.com/v1/`, HTTP **Basic** auth with a portal-generated API user ID and password.
```bash
curl -u "$WPE_API_USER_ID:$WPE_API_PASSWORD" "https://api.wpengineapi.com/v1/installs?limit=3"
```
Endpoints: Account, Account Users, Backups, Cache purge, Certificates, Domains, Installs, Sites, Site Reports, Site Transfers, SSH Keys, Usage Metrics, Status. Rate limits unpublished. There is **no** official general-purpose WPE CLI (the `wpe` CLI is headless-platform only).

**Smart Plugin Manager:** daily check, apply daily/weekly/monthly in a chosen 6-hour window. Visual regression on 10 pages default (homepage always), up to 20, configurable sensitivity. **Auto-rollback** on significant visual diff or 4xx/5xx. Retries 3 days, can skip one problem plugin. **BirdLife holds 115 licences and uses 2.**

**Local / headless:** Local Connect needs account-level API Access; `wp-config.php` excluded from push/pull; `.wpe-pull-ignore` / `.wpe-push-ignore`; multisite unsupported. Atlas is rebranded **WP Engine Headless Platform**, still current, Faust.js still maintained.

**Logs:** no live tailing. Portal → Logs, or WP Admin → WP Engine → Information. You export and read; you do not `tail -f`.

---

## 7. Live performance baseline (11 Sep 2026)

| Metric | Value | Band | Trend |
|---|---|---|---|
| WPE site performance score | **90/100** | "Looking good" | — |
| Average page latency | 402 ms | Good (<800) | flat |
| Cache hit ratio | **67.35%** | Fair (Good >70%) | **down from 69.71%** |
| Error rate | **5.08%** | Fair (0.3–20%) | **up from 4.34%** |
| Page loads busiest hour | 5,018 | — | down from 5,501 |
| Total daily page loads | 66,387 | — | — |
| Lighthouse desktop / mobile | 66 / **28** | — | — |

**Never report the 90 without the 5.08% beside it.** The target for "Good" error rate is under 0.3%, so we are ~17× it and rising. The score still reads 90 only because WP Engine's "Fair" band runs 0.3% to 20%. One in twenty requests to birdlife.org.au is erroring and the work has no owner.

**Product pages are effectively uncached** — the biggest available win:

| Page | Load | Cache hit | Loads/7d |
|---|---|---|---|
| /product/superb-lyrebird-bird-pin | 1,766 ms | **5%** | 4,136 |
| /cart | 982 ms | 0% (correct) | **12,900** |
| /product/galah-bird-pin | 1,598 ms | 3% | 838 |
| other product pages | ~1,520–1,580 ms | 2–7% | 650–870 each |

A public Woo product page should cache at 80%+. At 2–7% it explains both the 1.5 s loads and the sub-70% site-wide ratio. Leading hypotheses, in test order: cart-fragments AJAX (Live Cart is **Off**), a session/personalisation cookie set on product views, a Woo query arg defeating the cache key. **Diagnose, do not assert.**

**Features off or unused:** Live Cart **Off** · Dynamic Plugin Loading not installed · Site Monitoring **not activated** (no WPE-side uptime alerting at all) · NitroPack/Page Speed Boost not activated · Smart Plugin Manager **2/115 licences** · Stripe Connect "Configuration required" · zero cache exclusions (clean).

**Plugins:** 84 total, 11 with updates, **2 flagged as security risks** — `ACF to REST API 3.3.4` (**no update available, plugin abandoned**, exposes ACF fields over REST; ACF PRO 6.8.7 is already installed and has native REST, so test removal) and `EWWW Image Optimizer 8.7.5 → 8.7.7` (one-click fix).

---

## 8. Access and governance

Portal users on `birdlifeaus` production:

| User | Role |
|---|---|
| Mathew Hema, Andrew Dunn, Nina Lewis, Keith Tsui | **Owner** ×4 |
| Caroline Scales | Full |
| Ben McKeown, James O'Brien, Botian Chen, Krish Gupta (all Blitzm) | **Full, external** ×4 |

This does not match the documented BirdLife model (Mathew holds the keys, devolving as capability grows). WP Engine is the one system where an external build vendor holds standing production access.

**How to raise it — the people impact matters here.** This is not a case for removing Andrew, Nina or Keith, who need access to work. It is a case for (a) deciding deliberately whether four Owners is intended, since Owner includes billing and user management, and (b) time-bounding the Blitzm accounts to the membership build with a named end date. Four external Full accounts is defensible during a build and indefensible after it. Raised now, while the build is live and the relationship is good, it is governance. Raised after an incident, it is an accusation. James O'Brien and Krish Gupta are already on the un-executed WordPress admin removal list.

**Offboarding trap to state unprompted:** portal SSO does **not** cover SFTP, SSH or API credentials. A vendor offboard must sweep all four credential types. This belongs in IT-SEC-003.

**Backups discipline is genuinely good** and should be written into the release runbook rather than left as a habit: daily checkpoints running reliably ~10:55 AEST, 30-day window intact, manual pre-release checkpoints taken by Keith Tsui (31 Aug, "Before CRM Perks Salesforce Pro update") and Ben at Blitzm (21 Aug, "Manual backup before release").

**Domains:** `actforbirds.org` shows **DNS not pointed** and `www.actforbirds.org` blocked — configured in WP Engine but not resolving. Point it or remove it; a half-configured domain is a certificate and SEO liability and a takeover risk if registration lapses.

---

## 9. The review playbook — what to look at, in order

Run monthly on `birdlifeaus`, quarterly on the rest. Work the tiers in order; do not jump to Tier 4 because it is more interesting.

### Tier 1 — Correctness. Is the site lying to us?
1. **Error rate** (Performance). Target <0.3%. Anything over 1% is an incident with no ticket attached. Direction matters more than level.
2. **Plugins**, security risk column. A flag is a same-week action. A flag with **no available update** means an abandoned plugin: that is a removal decision, not an update decision.
3. **Backups**: newest daily older than 26 h → raise with WP Engine.
4. **Domains**: every domain green on DNS and SSL, or deleted.
5. **PHP version**: anything unsupported is on borrowed time. WP Engine force-upgrades EOL versions with no deferral once triggered.

### Tier 2 — Efficiency. Are we paying for work we need not do?
6. **Cache hit ratio.** >70% minimum, 85% target on a content site.
7. **Slow pages, cache-hit column.** Any public non-personalised page under 50% is a defect. **Rank by `page loads × (1 − cache hit)`**, not by load time — that finds the true cost.
8. **Autoloaded options** via the `wp db query` above. Over 800 KB is actively degrading the object cache. Look for plugins autoloading transients or logs.
9. **Slow query monitor** (included on eCommerce plans). Trend count and latency together.
10. **Plugin count.** 84 is a performance budget, a security surface and a maintenance liability at once. For each: does it earn its place, and what breaks if it goes?

### Tier 3 — Resilience. What happens when it goes wrong?
11. **Web rules** read top to bottom; every exception above its rule; every rule carrying a comment saying why it exists.
12. **Users and SFTP** per environment. Externals get an end date. Owners are a small deliberate number.
13. **Environment structure.** Does production have a staging environment *in the same Site*? If not, promotion is manual and will stay error-prone.
14. **Site Monitoring** active, alerting somewhere a human reads.
15. **Smart Plugin Manager** active with VRT and auto-rollback.

### Tier 4 — Experience. Is it good for a supporter?
16. **Lighthouse mobile.** Under 50 is a conversion problem; most Australian supporter traffic is mobile.
17. **Live Cart** and **EverCache for Woo** both on for any store.
18. **EFPC** on every content-serving domain, not just primary.
19. **Dynamic Plugin Loading** where plugin count is high.

---

## 10. Current recommended sequence

**This week, no project needed:** update EWWW · review and comment the two web rules, fix ordering if the allow is an exception · decide `actforbirds.org` · **turn on Site Monitoring**.

**This sprint, staging evidence first:** Live Cart on staging with before/after product cache-hit measurement · test removing ACF to REST API after confirming ACF PRO native REST covers every consumer · activate SPM on `birdlifeaus` with VRT and a low-traffic window · audit autoloaded options against 800 KB.

**This quarter, needs a decision:** **diagnose the 5.08% error rate** from log exports classified by URI and code (highest-value work on the list, currently unowned) · consolidate `birdlifeausstage` into the `birdlifeaus` Site so native Copy works, sequenced with Blitzm around the membership build not through it · plan `awsg` off PHP 7.4 · move flood mitigation to the Cloudflare edge and price GES against the next incident · time-bound the Blitzm accounts and extend IT-SEC-003 to SFTP/SSH/API sweeps.

### Targets to report against

| Metric | Now | Target | By |
|---|---|---|---|
| Error rate | 5.08% | <1.0% interim, <0.3% end | 31 Dec 2026 |
| Cache hit ratio | 67.35% | >80% | 31 Dec 2026 |
| Product page cache hit | 2–7% | >70% | 31 Oct 2026 |
| Lighthouse mobile | 28 | >50 | 31 Dec 2026 |
| Plugins flagged security risk | 2 | 0 | 30 Sep 2026 |
| Plugins with updates | 11 | 0, held by SPM | 31 Oct 2026 |
| Environments on EOL PHP | 1 | 0 | 31 Dec 2026 |
| External vendors with standing Full prod access | 4 | 0 without a documented end date | 31 Oct 2026 |

---

## 11. Operating rules

1. **Re-verify before quoting.** Every number here has a date on it. Read the portal live, then speak.
2. **Never report the performance score without the error rate.** The banding flatters us.
3. **Diagnose cacheability, do not assert it.** "Product pages cache at 5%" is a fact. "It is the cart fragments" is a hypothesis until measured on staging.
4. **Nothing structural ships to production without staging evidence**, and staging promotion is manual until the Sites are consolidated — say so every time a deploy is discussed.
5. **Check Alternate Cron before debugging any scheduled-task problem.**
6. **Put the control where it belongs:** flood and bot mitigation at the Cloudflare edge, redirects and headers in Web Rules, cacheability in the application.
7. **Separate the layers when answering.** Platform problem or WordPress problem? Say which, and route to `birdlife-wordpress` for the second.
8. **Name the people impact** on any access or process recommendation, per standing preference.
9. **No em dashes in any output.**

## 12. Known unknowns

State these rather than guessing: plan tier and PHP worker allocation for `birdlifeaus` (WP Engine does not publish worker counts; `/modify_plan` renders empty) · which network tier each domain is on, so GES status is unverified · Memcached vs Redis for object cache (unpublished) · root cause of the 5.08% error rate (needs log export) · whether `birdlifeaocstg` on PHP 8.4 against 8.2 production is deliberate (defensible as an upgrade test, indefensible as an accident — ask) · Customer API rate limits (unpublished).