---
name: birdlife-wordpress
description: Expert operator knowledge for BirdLife Australia's WordPress estate on WP Engine — plugin and licence inventory, the WooCommerce membership rebuild, the miniOrange Salesforce sync, the self-registration privilege flaw, expired licences on live payments, and the cart-flood incident. Use for any task involving birdlife.org.au the website, WooCommerce orders, products, subscriptions or memberships, WordPress users and roles, plugins, staging vs production, or site performance and security. Trigger on "WordPress", "WP Engine", "WooCommerce", "birdlifestage", "plugin", "Gravity Forms", "shop_order", "Blitzm", or a website incident.
---

# BirdLife Australia — WordPress

**There is no WordPress MCP connector in this session.** Everything here is operator knowledge, not executable capability. Work through WP Engine, the WP admin, or the browser tools — and say which you are using.

## Environments

| Environment | Detail |
|---|---|
| Production | `birdlife.org.au` — WP Engine environment **`birdlifeaus`**, behind Cloudflare CDN |
| Staging | `birdlifestage.wpengine.com` |
| Deployment | Git |
| Platform | WordPress **7.0**, PHP **8.4.22**, custom BirdLife theme |
| Users | **14,285** |

**Staging differs from production in ways that break naive promotion:**
- Membership subscription periods run **1 day in staging, 1 year in production**.
- Staging SKUs are suffixed **`-STAGING`**.
- **All Salesforce IDs differ** (record types, Product2, PricebookEntry) and must be re-set on production deploy.
- miniOrange staging redirect URI is `https://birdlifestage.wpengine.com`.

## Health: 5/10, "needs attention"

**82 plugins (62 active / 20 inactive), 30 awaiting update, auto-updates OFF for all.** 5 inactive themes. Page cache 31ms (genuinely excellent).

**Critical items:**
- **WP_DEBUG_LOG writing publicly.**
- **1,063 autoloaded options, ~1MB per request.**
- **WP File Manager v8.0.2** (CVE history) and **WP phpMyAdmin** both active — either is a full compromise path.
- **ACF to REST API v3.3.4 — known vulnerable, publicly exposes custom fields.**
- WP 2FA is four major versions behind.
- OPcache not enabled; disk-space check failing (blocks updates).
- Spellbook plugin inactive, breaking GP Populate Anything.

**Six expired licences, two of them on live money:**
- **WooCommerce Subscriptions — running unlicensed on live payments** (~A$11,108.70/month in WooCommerce sales)
- **WooCommerce Memberships — inactive**
- GTM PRO, Import Export Suite, TIV Multi-currency, Gravity Forms↔Pardot

Say this plainly whenever the membership build comes up: **building against an inactive plugin means testing against nothing.** The Memberships and Subscriptions licences are ICT-owned blockers gating all Blitzm work — FR-8 e-store discount, FR-3 access plans, FR-4 auto-renewal and both new miniOrange mappings.

## The privilege flaw

**"Anyone can register" is ENABLED with default role Shop Manager.** Public self-registration grants access to orders and customer data. This is the most serious configuration item on the site and it is a one-toggle fix.

Alongside it: **25 admin accounts** (6 Blitzm, 2 EnvisionCP, 1 The PG, 1 Xecurify, plus the `wpengine` system account). **2FA enforced on none, configured on only 3. 20 admins have never logged in.** Ahilya (Blitzm) explicitly excluded from 2FA. **82,089 logged emails containing PII** sitting in the database.

WP 2FA (Melapress v3.1.1.2) is installed but not enforced. Email-based 2FA is the sanctioned method for elevated users: 6-digit code, 15-minute expiry, 10 one-time backup codes.

Elevated Users List decisions made but **not executed** — Remove: Ahilya, Ayush Saxena, David Arvaji, Holly Browne, James O'Brien, Justin Joseph, Justin Rivera, Krish, Ross James. `wpengine` → inactive. Undecided: Fiona Cahill, Hannah Langford, James Vilinsky, editors.

## Integration stack

- **miniOrange "Object Data Sync For Salesforce" (Enterprise)** — the Salesforce integration layer. Real-time triggers, no cron. Primary key is post meta `salesforce_Opportunity_ID`.
- **Ortto plugin v1.0.24**
- Stripe gateway; Gravity Forms (+ Stripe, + Pardot); WooCommerce Subscriptions; WooCommerce Memberships.

**Staging mappings as at 30 Jul 2026 — 6, none touching membership:** Product2, Woo Payments Sync, OpportunityLineItem, `shop_order`→Opportunity, Product2→WP Product, WP Product Variation→SF Product. A 7th "Woo Members Sync" mapping was deleted, consistent with Memberships being inactive.

**Two live bugs that must not be repeated in the new build:**
1. **Primary-key write-back gap** — the plugin fails to write the returned SF Id back into post meta ("Salesforce UUID: None" observed on two real paid orders). Missing meta means the next status change creates a duplicate record.
2. **Field-level security gap on `npe01__Opportunity__c`** causing **~10.3-10.5% of sync attempts to fail outright, confirmed on BOTH staging and production.**

Mitigations already specified: use a dedicated `salesforce_Membership_ID` key for the new membership mapping; **grant FLS to the integration user on every new field BEFORE first sync**; run a deliberate write-back test first (test MO-05).

Reverse flow endpoints exist as SF→WP webhooks. **Their access keys were leaked in plaintext across three documents** (prod `7cf2…`, staging `8d8f…`). Rotate via "Regenerate Access Key" and scrub the docs.

## Membership rebuild — where it stands

WooCommerce replaces Payments2Us for membership. Vendor **Blitzm**. Salesforce remains the system of record for membership status.

**Tiers (confirmed live on staging 30 Jul 2026):** Individual $84 · Concession $65 (honour system, no verification) · Family $132 (1 primary + up to 6, min 2 max 7) · Financial Hardship $35 (hidden product, Supporter Care controlled) · Free $0 (Lifetime/Honorary/Fellow, Board approval). The public page previously showed superseded $79/$35.

Duration 12 months, grace/cease period 3 months per the constitution → End Date +12m, Cease Date +15m. Auto-renewal default ON with explicit opt-out. Reminders at 31 days pre-expiry, 7 and 1 days pre-cease.

**Reminder-timing conflict to escalate:** the confirmed 31/7/1 schedule contradicts a 10/37/60-style timing in help text on Keith Tsui's `Subscription__c` fields that is **already wired into a Conga flow**. If both ship, members get two contradictory reminder schedules. Escalate to James Vilinsky before building reminder fields.

**Build status:** front end largely built or partially built. **The entire Salesforce side is Not Built** — lifecycle flow, reminders, voting, object and sync. E-store discount is Blocked. Migration is Not Built. **All 45 staging tests were "Not Tested" as at 31 Jul 2026** (Blitzm 15 / miniOrange 10 / Salesforce dev 12 / end-to-end 8). BZ-04 re-checks the 30 Jul Add-to-Cart bug (YITH Pre-Order / Cart block incompatibility).

**Stripe migration constraint:** card tokens may be reusable for migrated auto-renewal members (unconfirmed with Blitzm). **BECS direct debit members cannot be migrated — they must set up a fresh mandate.** Existing WooCommerce subscriptions stay active 15 months so nobody loses access mid-transition, and ICT turns off Payments2Us auto-renewals at cutover. No double-charging across systems.

## Cart-flood incident (Jul 2026)

Distributed automated flood of `/cart/?remove_item=…` from hundreds of IPs cycling product IDs 37909/37910/37911/30651. Cart pages are uncacheable, so every request hit PHP → worker exhaustion → 504s. **4,410 5xx on /cart out of 66,507 requests in 30 days.**

Mitigated with a **WP Engine Web Rules "Deny" rule ranked first**: URI regex `^/cart` AND query contains `remove_item=` AND Referer NOT matching `birdlife\.org\.au`. Caveat: privacy browsers stripping Referer get false-positived.

Open: monitor effectiveness; **request platform-level bot/DDoS mitigation from WP Engine**; consider moving this control to Cloudflare where it belongs. `/wp-login.php` separately took >50,000 hits in 30 days at 67% error rate.

Also flagged: mobile PageSpeed 46/100; Smart Plugin Manager available with only 2 of 115 licences used; WordPress core update marked "Deferred" — confirm that is intentional.

## People

Nina Lewis (ICT Lead, sign-off, 24h critical fixes) · Mathew Hema (Project Manager, sign-off) · Jonathon Wilson (miniOrange/OIDC dependency) · James Vilinsky (Participation; reminder-timing escalation) · Micah Demmert (Exec Director Participation) · Karishma Soni (Salesforce side).

Vendors: **Blitzm** (build — Ben, James O'Brien, Krish Gupta, Ahilya Sinha) · **WP Engine** (host) · **Xecurify/miniOrange** (Atharvaa Bhadbhade) · Envision CP · The PG.

## Operating rules
1. **Nothing structural ships to production without staging test evidence.** 45 tests currently sit at "Not Tested".
2. **Check FLS on the Salesforce integration user for every new field before first sync**, unprompted.
3. Licence expiry is a build blocker, not a paperwork item. Raise it first.
4. Public self-registration defaulting to Shop Manager is the item to fix today; it needs no project.
5. Staging and production Salesforce IDs differ — re-map on every deploy.
