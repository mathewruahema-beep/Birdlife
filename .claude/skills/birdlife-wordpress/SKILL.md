---
name: birdlife-wordpress
description: "Expert web developer and operator knowledge for BirdLife Australia's WordPress estate on WP Engine: the custom BirdLife theme architecture (SCSS build, ACF blocks, 20 CPTs, WooCommerce overrides), full plugin and licence inventory, the miniOrange Salesforce sync and its two defects, the membership rebuild, HPOS and Stripe, live security posture, and how to read production safely."
---

# BirdLife Australia WordPress

Environments, connector abilities, health numbers, membership tiers and the cart-flood rule live in `references/facts.md` (values dated; section 2 below is the 11 Sep 2026 live read). When a value changes, edit the facts file first, then this prose.

Read `birdlife-core` first. This skill is both the operator record and the
developer handbook for birdlife.org.au. Section 1 tells you how to get a live
fact rather than reciting a stale one.

## 1. How to get live facts

Three access paths exist. Name the one you used in every answer.

**Browser on production.** When the Claude in Chrome tools are present and the
user is signed into `birdlife.org.au/wp-admin`, you can read the real
configuration. This is the authoritative path. Method that works:

- Open your own tab with `tabs_create_mcp`, do not hijack the user's.
- `navigate` then `javascript_tool` with `fetch('/wp-admin/...')` plus
  `DOMParser`. Same-origin cookies ride along, so no credentials option is
  needed, and passing one trips the safety filter.
- `javascript_tool` output is capped near 1,000 characters. Return slices, or
  stash results on `window` and page through them. Keep each call to about six
  fetches or it times out.
- WooCommerce renders booleans as `<mark class="yes|no">`, so read the class,
  not `innerText`, or every checkbox looks empty.
- Site Health accordions are collapsed and `hidden`. Strip the attribute, then
  `get_page_text` returns the whole configuration dump in one pass. The status
  tab loads asynchronously, so navigate and wait before reading it.
- The tab group id can change mid-session. If a call reports the tab is not in
  the group, call `tabs_context_mcp` again and use the id it returns.
- Some admin screens (miniOrange sync, WPCode) return BLOCKED because they
  render credentials. That is correct behaviour. Do not work around it. Ask the
  user to read the screen instead.

The highest-yield screens, in order: `site-health.php?tab=debug` (everything),
`admin.php?page=wc-status` (commerce, templates, gateways),
`/wp-json/wp/v2/types` (content model), `users.php?role=administrator`,
`theme-editor.php?theme=birdlife` (file tree), `edit.php?post_type=acf-field-group`.

**UAT MCP connector.** "BirdLife UAT WordPress" exposes eleven WordPress MCP
Adapter abilities: `woocommerce/orders-query`, `products-query`,
`woocommerce-gift-cards/gift-cards-query`,
`woocommerce-product-bundles/query-bundles`, `yoast-seo/get-seo-scores`,
`get-readability-scores` (read) and `order-add-note`, `order-update-status`,
`product-create`, `product-update`, `product-delete` (write). Three rules. It
is UAT, so say "UAT" in any answer using it and never present its data as live
member or order data. The write abilities are real, so propose before writing,
even on UAT, because a wrong product delete costs Blitzm days. And
`products-query` currently fails schema validation on `price` being returned as
a number; if it errors, that is the adapter, not your call.

**Neither available.** Say so, answer from this skill, and label the answer as
recorded knowledge with its date rather than a live fact.

Any WooCommerce REST key you meet: treat as write-capable and possibly
compromised. "Read" keys on this site were found able to write, and keys were
exposed in deleted Claude routine prompts in Aug 2026 with rotation unverified.

## 2. Platform (verified live 11 Sep 2026)

| Item | Value |
|---|---|
| Production | `birdlife.org.au`, WP Engine env `birdlifeaus`, behind Cloudflare |
| Staging | `birdlifestage.wpengine.com` |
| Root | `/nas/content/live/birdlifeaus` |
| Core | WordPress 7.0.4 (7.1 available), single site |
| PHP | 8.4.25 FPM, 512M limit, **OPcache disabled by configuration** |
| Server | nginx on Linux 6.8 (GKE) |
| Database | MySQL 8.4.11, `wp_birdlifeaus`, prefix `wp_`, utf8mb4_unicode_520_ci |
| Size | 15.39 GB total: uploads 11.17 GB, DB 1.82 GB, plugins 606 MB, themes 60 MB |
| Cache | WP Engine page cache plus `advanced-cache.php` and `object-cache.php` drop-ins |
| Locale | en_AU, Australia/Melbourne, permalinks `/%postname%/` |
| Constants | `WP_MEMORY_LIMIT` **40M** (default, never raised), `WP_DEBUG` off, `WP_DEBUG_LOG` off, `WP_CACHE` on |
| Deployment | Git, via an admin account `bitbucket@wpengine.com` |
| Users | 15,380 |

Staging differs from production in ways that break naive promotion. Membership
subscription periods are 1 day in staging and 1 year in production. Staging SKUs
carry a `-STAGING` suffix. All Salesforce ids differ (record types, Product2,
PricebookEntry) and must be re-set on deploy. The miniOrange staging redirect
URI is `https://birdlifestage.wpengine.com`.

## 3. Theme architecture: this is the developer core

**Theme `birdlife` v2.4.6.31 by Webplace. Classic theme, parent theme, and
there is no child theme.** 1,146 files.

```
themes/birdlife/
  functions.php
  assets/scss/           SCSS source, compiled to assets/css/bundle.css
    components/          _card.scss _hero.scss _nav.scss _form.scss ... (one per component)
  inc/
    acf-blocks/blocks/   call-to-action | cards-grid | page-header | people-grid
                         each with block.json + style.css + render php
    components/          bird-profiles, dashboard, events, hero
    gravity-forms/       gravity-forms.php, supporter-care-workflow.php,
                         bl-get-donations-form.php, address-autocomplete perk glue
    woocommerce/         custom-membership.php  subscriptions.php
                         checkout-donations.php  checkout.php  myaccount.php
                         emails.php  subscription-detail.php  acf-locations.php
    ajax/                fetch-species.php + markers.json
    enqueue_scripts.php  customizer.php  wp_bootstrap_navwalker.php
  archive-<cpt>.php  single-<cpt>.php  taxonomy-<tax>.php
  template-parts/
    bird-profile/        overview, identification-distribution, habitat, behaviour,
                         conservation, songs-calls, similar-species, subspecies,
                         how-to-help, call-to-action, extra-section, popups/
    woocommerce/mini-cart.php  third-party-embed/ortto-signup.php  login.php  unauthorised.php
  woocommerce/           20+ core template overrides
```

Rules that follow from this, and that you enforce:

1. **Edit SCSS, never `bundle.css`.** There is a build step. A change made to
   the compiled CSS is lost on the next build.
2. **Membership and donation logic lives in `inc/woocommerce/`, not in a
   plugin.** `custom-membership.php` and `subscriptions.php` are the files to
   read before believing anything about how membership behaves.
3. **New editor components are ACF blocks**, registered with `block.json` in
   `inc/acf-blocks/blocks/`. Four exist. Follow that pattern rather than adding
   another third-party block library.
4. **There is no child theme, so every override is inside vendor code.** A
   Webplace theme update can overwrite BirdLife customisation. Raise this in
   any conversation about updating the theme.
5. **Four WooCommerce overrides are already out of date against core:**
   `emails/email-order-details.php` (10.7.0 vs 10.8.0),
   `emails/email-styles.php` (10.7.0 vs 11.0.0),
   `myaccount/form-edit-account.php` (10.5.0 vs 11.0.0),
   `order/order-details.php` (10.1.0 vs 11.0.0). Subscriptions overrides
   `my-subscriptions.php` and `related-subscriptions.php` are at 7.3.0 vs 8.2.0,
   migrated from Subscriptions 2.6.0. Check this list again before quoting it.
6. **The theme file editor is enabled** (`DISALLOW_FILE_EDIT` unset). Any of the
   20 admins can execute arbitrary PHP on live, bypassing Git. Treat this as a
   finding, not a convenience.

**Cart and checkout run on different technologies.** `/cart/` uses the
WooCommerce Cart block; `/checkout/` uses the `[woocommerce_checkout]`
shortcode. This split is the most likely root of the 30 Jul 2026 Add-to-Cart
defect with YITH Pre-Order (test BZ-04) and it constrains which extensions work
end to end. Surface it whenever block-vs-shortcode compatibility comes up.

## 4. Content model

Twenty custom post types, thirty-five-plus taxonomies, registered through
**Custom Post Type UI**, so the content model is database configuration and is
**not in Git**. Changing it in staging does not promote it.

CPTs: `bird_profile` (184) `news` (641) `event` (932) `campaign` (21)
`project` (20) `program` (10) `group` (49) `place` (7) `habitat` `kba` (5)
`publication` (9) `appeal` (23) `donate` (9) `award` (13) `how_to` (8)
`volunteer_opportunit` (31) `case_study` (1) `annual_reports` (1) `report` (2)
plus `product` (374), `product_variation` (100), `shop_order` (6,967),
`shop_order_refund` (154), `page` (192) and a legacy `post` count of 15,140.

Taxonomies split into an ornithological vocabulary (`bird_groups`, `bird_size`,
`bird_colour`, `bird_shape`, `bird_distinctive_feature`, `bird_family`,
`conservation_status`, `conservation_status_epbc`, `habitat_type`,
`risks_to_birds`, `plant_type`) and an organisational one (`state_territory`,
`local_group`, `special_interest_group`, `pillars`, `campaign_type`,
`committee_member`, `award_types`, `experience_level`, `news_types`,
`event_types`, `publication_types`, `publication_series`, `organisers`,
`partners`, `people`, `team_member`, `volunteer`, `action_type`,
`location_features`, `campaign_resource_types`).

**ACF PRO 6.8.7** carries the structure: 72 field groups, 1,122 fields, 34 JSON
groups, 4 registered ACF blocks, licence active (Developer, registered to
birdlife.org.au). Groups worth knowing: `Salesforce Campaign`, `Salesforce
fields`, `Donation Campaign Codes`, `API Settings`, `User role restrictions`,
`Global fields`, `Important Pages`, the `Block:` and `Reusable:` families, and
`Project - not used to be deleted`, which tells you the estate has never been
pruned.

## 5. Commerce

| Item | Value |
|---|---|
| WooCommerce | 11.0.1, **HPOS enabled**, `OrdersTableDataStore`, data sync on, sync-on-read off |
| Currency | AUD, left symbol, 2 decimals |
| Pages | `/shop/` `/cart/` (block) `/checkout/` (shortcode) `/my-account/` |
| Stripe gateway | 10.8.5, **live**, account `acct_1PaqQkEdZ08H7Yxq`, OAuth connected, optimised checkout on, express checkout on cart |
| Stripe methods | card, apple_pay, google_pay, **au_becs_debit** |
| Subscriptions | 9.1.0, live mode, subscriptions-core 8.3.0, **zero subscriptions recorded against any gateway** |
| Other gateways | WooPayments 11.0.0 active; PayPal Payments inactive |
| Product types | simple, variable, grouped, external, bundle, subscription, variable-subscription, flexible |

Two things to say out loud whenever membership comes up. **Nothing is currently
billing through WooCommerce Subscriptions**, so the auto-renewal design is
untested in production. And **two gateways (Stripe and WooPayments) are active
on the same rails**, which is a reconciliation and support hazard worth
resolving before volume arrives.

## 6. Integrations

**miniOrange Object Data Sync For Salesforce Enterprise 25.0.2** is the sync
layer. Real-time triggers, no cron. Primary key is post meta
`salesforce_Opportunity_ID`. Two live defects that must not be repeated:

1. **Primary-key write-back gap.** The plugin fails to write the returned
   Salesforce Id back into post meta ("Salesforce UUID: None" observed on two
   real paid orders). Missing meta means the next status change creates a
   duplicate record instead of updating.
2. **Field-level security gap on `npe01__Opportunity__c`**, causing roughly
   10.3 to 10.5 per cent of sync attempts to fail outright, confirmed on both
   staging and production.

Standing mitigations, offered unprompted: use a dedicated
`salesforce_Membership_ID` key for the new membership mapping; **grant FLS to
the integration user on every new field before first sync**; run a deliberate
write-back test first (test MO-05).

Staging mappings as at 30 Jul 2026, six, none touching membership: Product2,
Woo Payments Sync, OpportunityLineItem, `shop_order` to Opportunity, Product2 to
WP Product, WP Product Variation to SF Product. A seventh "Woo Members Sync"
mapping was deleted, consistent with Memberships being inactive. Production
mappings are not currently verified.

Reverse-flow Salesforce to WordPress webhook access keys were leaked in
plaintext across three documents (prod `7cf2...`, staging `8d8f...`). Rotate via
"Regenerate Access Key" and scrub the docs. Rotation is not confirmed.

**Three separate Salesforce paths exist**, which is itself a finding: miniOrange
object sync, the forked `Custom Salesforce OpenID Connect Generic 3.9.1` for
supporter SSO (a fork, so no upstream security fixes; the stock plugin sits
inactive beside it), and `Integration for Gravity Forms and Salesforce Pro` for
form submissions.

Marketing: **Ortto 1.0.24** is the destination. `Integration for Gravity Forms
and Pardot` is still active with an expired licence and must go out with the
Pardot decommission. GTM for WooCommerce PRO and the Meta pixel carry analytics.
Content Workflow by Bynder replaced GatherContent.

**Gravity Forms 3.1.0.2, 87 forms.** A single submission can reach Salesforce,
Pardot and Stripe through three different add-ons. Gravity Forms Stripe Add-On
is a second payment path independent of WooCommerce; confirm which donations use
which before quoting revenue numbers.

## 7. Plugin estate

**62 active, 22 inactive, 6 WP Engine must-use. Auto-updates off on everything.
44 updates pending.** Full annotated inventory lives in the reference document
`BirdLife_WordPress_Estate_Reference.docx` (IT-WEB-001). The ones that change
a decision:

**Load-bearing:** WooCommerce, WooCommerce Subscriptions, WooCommerce Stripe
Gateway, Product Bundles, ACF PRO, Custom Post Type UI, Gravity Forms + Perks,
miniOrange Object Data Sync, Custom Salesforce OIDC, Relevanssi Premium,
Permalink Manager Pro, EWWW Image Optimizer, FluentSMTP.

**Risk items:**

- **ACF to REST API 3.3.4.** Known vulnerable, unmaintained, exposes custom
  field values over the public REST API. Highest-value removal on the site.
- **Email Log 2.63** holding **86,629 logged emails with full bodies and
  supporter PII**, growing, with no retention policy.
- **WPCode Lite** running **5 snippets** of arbitrary PHP and JS from the
  database, invisible to Git. Audit them; move anything real into the theme.
- **SVG Support** allowing SVG upload, a stored-XSS vector unless sanitisation
  is enforced and roles restricted.
- **Better Search Replace** and **User Switching**, both legitimate and both
  powerful in a compromised admin session.
- **Admin Menu Editor** hides menu items but does not remove capability. It is
  not a security control; never cite it as one.

**Expired licences:** WooCommerce Subscriptions (on live payments),
WooCommerce Memberships (inactive), GTM PRO, Import Export Suite, TIV
Multi-currency, Gravity Forms to Pardot. Say plainly whenever the membership
build comes up: **building against an inactive plugin means testing against
nothing.** Memberships and Subscriptions licences are ICT-owned blockers gating
FR-8 e-store discount, FR-3 access plans, FR-4 auto-renewal and both new
miniOrange mappings.

**Present functional defect:** **Spellbook is inactive while GP Populate
Anything is active and depends on it.** That is a live bug, not housekeeping.

**Duplication to resolve:** three Salesforce form connectors (two inactive), two
SMTP routers (FluentSMTP active, WP Mail SMTP inactive), two search plugins
(Relevanssi Premium active, free edition inactive), two GTM plugins, two WebP
converters (EWWW and WebP Express), and three tools that can own the same URL
(Redirection, Yoast redirects, Permalink Manager Pro).

**Removed since the last record:** WP File Manager and WP phpMyAdmin are both
gone. Do not keep citing them.

## 8. Security posture

| Item | State |
|---|---|
| Public self-registration | **Disabled.** Fixed. Default role is still Shop Manager if ever re-enabled. |
| Administrators | **20**, of which **7 are external vendor accounts** and 11 have never logged in |
| 2FA | WP 2FA 4.1.0 installed, **no enforcement policy**, 3 of 20 admins configured |
| File editing | Enabled. `DISALLOW_FILE_EDIT` unset. |
| WP_DEBUG_LOG | Disabled. Fixed. |
| Autoloaded options | **1,174, 1 MB, on every request.** Site Health critical. Growing (was 1,063). |
| OPcache | Still disabled |
| Disk space check | Failing, which can block updates |
| Custom roles | Content Lead, Content Creator, Group content creator, SEO Manager, SEO Editor, Supporter Care User, all built with User Role Editor |

Vendor admin accounts: Blitzm (ben@blitzmdesign.com.au, botian.chen@blitzm.com,
james@blitzm.com, justin@blitzm.com, krish@blitzm.com), Xecurify
(atharvaa.bhadbhade@xecurify.com), The PG (david.arvaji@thepg.com.au), plus the
`bitbucket@wpengine.com` deploy account. Ahilya has been removed.

**Cart-flood incident, Jul 2026.** Distributed flood of
`/cart/?remove_item=...` from hundreds of IPs cycling product ids
37909/37910/37911/30651. Cart pages are uncacheable, so every request hit PHP,
exhausting workers and returning 504s: 4,410 5xx on `/cart` out of 66,507
requests in 30 days. Mitigated with a WP Engine Web Rules "Deny" rule ranked
first: URI regex `^/cart` AND query contains `remove_item=` AND Referer NOT
matching `birdlife\.org\.au`. Privacy browsers that strip Referer get
false-positived. Still open: monitor effectiveness, request platform-level
bot and DDoS mitigation from WP Engine, and move the control to Cloudflare where
it belongs. `/wp-login.php` separately took over 50,000 hits in 30 days at 67
per cent error rate. Note that **reCAPTCHA on Gravity Forms is inactive** across
87 public forms on a site with a documented bot problem.

## 9. Membership rebuild

WooCommerce replaces Payments2Us for membership. Vendor **Blitzm**. Salesforce
remains the system of record for membership status.

Tiers confirmed live on staging 30 Jul 2026: Individual $84, Concession $65
(honour system, no verification), Family $132 (1 primary plus up to 6, min 2 max
7), Financial Hardship $35 (hidden product, Supporter Care controlled), Free $0
(Lifetime, Honorary, Fellow, Board approval). The public page previously showed
superseded $79 and $35.

Duration 12 months, grace and cease period 3 months per the constitution, so End
Date +12m and Cease Date +15m. Auto-renewal default ON with explicit opt-out.
Reminders at 31 days pre-expiry, 7 and 1 days pre-cease.

**Reminder-timing conflict to escalate:** the confirmed 31/7/1 schedule
contradicts a 10/37/60-style timing in help text on Keith Tsui's
`Subscription__c` fields that is already wired into a Conga flow. If both ship,
members get two contradictory reminder schedules. Escalate to James Vilinsky
before building reminder fields.

Build status: front end largely built or partially built. The entire Salesforce
side is Not Built (lifecycle flow, reminders, voting, object and sync). E-store
discount is Blocked. Migration is Not Built. All 45 staging tests were "Not
Tested" as at 31 Jul 2026 (Blitzm 15, miniOrange 10, Salesforce dev 12,
end-to-end 8). BZ-04 re-checks the Add-to-Cart bug.

**Stripe migration constraint:** card tokens may be reusable for migrated
auto-renewal members (unconfirmed with Blitzm). **BECS direct debit members
cannot be migrated and must set up a fresh mandate.** Existing WooCommerce
subscriptions stay active 15 months so nobody loses access mid-transition, and
ICT turns off Payments2Us auto-renewals at cutover. No double-charging across
systems.

## 10. Making a change safely

The order of operations for any code or configuration change:

1. **Say which environment you are talking about.** Production, staging or UAT.
   Never let it be ambiguous.
2. **Read the current state live** before proposing. Section 1 tells you how.
3. **Locate the change correctly.** Presentation goes in SCSS. Editor
   components go in `inc/acf-blocks/`. Commerce behaviour goes in
   `inc/woocommerce/`. Content model goes in CPT UI, which does not promote
   through Git and must be repeated per environment. Anything in WPCode is a
   smell to be moved, not extended.
4. **Check for FLS on the Salesforce integration user for every new field
   before first sync.** Unprompted, every time.
5. **Nothing structural ships to production without staging test evidence.**
   45 tests currently sit at "Not Tested".
6. **Re-map Salesforce ids on deploy.** Staging and production differ.
7. **Check the plugin's licence before designing around it.** Licence expiry is
   a build blocker, not a paperwork item.
8. **State the impact on people.** Who has to re-enrol, who loses an admin
   shortcut, which vendor gets blocked, which supporter sees a different price.

Review checklist for any WordPress change proposed to you, whether by a vendor
or by yourself:

- Does it edit a compiled asset instead of the source?
- Does it add a template override to a parent theme with no child theme?
- Does it add a fifth way to do something the site already does four ways?
- Does it rely on an inactive or unlicensed plugin?
- Does it add an autoloaded option? There are already 1,174.
- Does it write to Salesforce without a confirmed primary-key write-back?
- Does it assume cart and checkout share a technology? They do not.
- Is it reversible, and is the rollback written down?

## 11. People

Nina Lewis (ICT Lead, sign-off, 24h critical fixes), Mathew Hema (Project
Manager, sign-off), Andrew Dunn (level 1 support), Keith Tsui (junior Salesforce
dev), Karishma Soni (external Salesforce dev), Jonathon Wilson (miniOrange and
OIDC dependency), James Vilinsky (Participation, reminder-timing escalation),
Micah Demmert (Exec Director Participation), Caroline Scales and Zoe Woodford
(site admins).

Vendors: **Webplace** (theme author), **Blitzm** (membership build: Ben McKeown,
James O'Brien, Krish Gupta, Botian Chen, Justin Rivera), **WP Engine** (host),
**Xecurify / miniOrange** (Atharvaa Bhadbhade), Envision CP, The PG, Bynder.

## 12. Standing operating rules

1. Verify live before asserting, and name the source.
2. Nothing structural ships to production without staging test evidence.
3. Check FLS on the Salesforce integration user for every new field before
   first sync, unprompted.
4. Licence expiry is a build blocker. Raise it first.
5. Staging and production Salesforce ids differ. Re-map on every deploy.
6. UAT is not production. Label it.
7. Treat every WooCommerce REST key as write-capable and possibly compromised.
8. When a figure in this skill is older than the question, go and get it again
   rather than quoting it.