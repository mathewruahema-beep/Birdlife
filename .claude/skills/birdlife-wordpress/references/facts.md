# WordPress / WooCommerce: facts

The lookup table for `birdlife-wordpress`. **Edit this file first when a
value changes, then the prose.** Health numbers date from Jul to Aug 2026.

## Environments (live read 11 Sep 2026; Jul values in brackets where changed)

| Environment | Value |
|---|---|
| Production | `birdlife.org.au`, WP Engine environment `birdlifeaus`, behind Cloudflare; root `/nas/content/live/birdlifeaus` |
| Staging | `birdlifestage.wpengine.com` |
| Deployment | Git, via admin account `bitbucket@wpengine.com` |
| Core | WordPress 7.0.4, 7.1 available (was 7.0), single site |
| PHP | 8.4.25 FPM, 512M limit, OPcache disabled by configuration (was 8.4.22) |
| Server / DB | nginx, Linux 6.8 (GKE); MySQL 8.4.11, `wp_birdlifeaus`, prefix `wp_` |
| Size | 15.39 GB: uploads 11.17 GB, DB 1.82 GB, plugins 606 MB, themes 60 MB |
| Constants | `WP_MEMORY_LIMIT` 40M, `WP_DEBUG` off, `WP_DEBUG_LOG` off (fixed), `WP_CACHE` on, `DISALLOW_FILE_EDIT` unset |
| Theme | `birdlife` v2.4.6.31 by Webplace, classic parent theme, no child theme, 1,146 files |
| Registered users | 15,380 (was 14,285) |
| miniOrange staging redirect URI | `https://birdlifestage.wpengine.com` |
| Cart / checkout | `/cart/` Cart block; `/checkout/` `[woocommerce_checkout]` shortcode |

Staging differences: subscription period 1 day (production 1 year); SKUs
suffixed `-STAGING`; all Salesforce IDs differ.

## Connector (`BirdLife UAT WordPress`, WordPress MCP Adapter, UAT only)

| Ability | Kind |
|---|---|
| `woocommerce/orders-query`, `woocommerce/products-query` | read |
| `woocommerce-gift-cards/gift-cards-query`, `woocommerce-product-bundles/query-bundles` | read |
| `yoast-seo/get-seo-scores`, `yoast-seo/get-readability-scores` | read |
| `woocommerce/order-add-note`, `woocommerce/order-update-status` | write |
| `woocommerce/product-create`, `woocommerce/product-update`, `woocommerce/product-delete` | write |

Tools: `mcp-adapter-discover-abilities`, `mcp-adapter-get-ability-info`,
`mcp-adapter-execute-ability`. No production connector exists.

## Health snapshot (11 Sep 2026 live read; Jul values in brackets where changed)

| Item | Value |
|---|---|
| Score | 5/10 (Jul 2026) |
| Plugins | 62 active, 22 inactive, 6 WP Engine must-use; 44 updates pending (was 30); auto-updates off |
| Themes | 5 inactive |
| Page cache | 31 ms (Jul 2026) |
| Autoloaded options | 1,174, ~1 MB per request (was 1,063) |
| Risky active plugins | ACF to REST API 3.3.4; WPCode Lite (5 PHP/JS snippets in the DB); SVG Support; Email Log 2.63. WP File Manager and WP phpMyAdmin REMOVED (do not cite) |
| WP 2FA | 4.1.0, no enforcement policy, 3 of 20 admins configured (was Melapress 3.1.1.2) |
| Logged emails with PII in DB | 86,629 (was 82,089), no retention policy |
| Gravity Forms | 3.1.0.2, 87 forms, reCAPTCHA inactive |
| ACF PRO | 6.8.7, 72 field groups, 1,122 fields, 4 ACF blocks |
| Content model | 20 CPTs, 35+ taxonomies via Custom Post Type UI (database config, not in Git) |
| WooCommerce | 11.0.1, HPOS enabled; Stripe gateway 10.8.5 live on `acct_1PaqQkEdZ08H7Yxq` (card, apple_pay, google_pay, au_becs_debit); Subscriptions 9.1.0 with zero subscriptions on any gateway; WooPayments 11.0.0 also active |
| miniOrange | Object Data Sync For Salesforce Enterprise 25.0.2 |
| Salesforce paths | three: miniOrange sync, forked Custom Salesforce OIDC Generic 3.9.1 (SSO), Integration for Gravity Forms and Salesforce Pro |
| Mobile PageSpeed | 46/100 |
| Smart Plugin Manager | 2 of 115 licences used |
| WooCommerce sales | ~A$11,108.70/month |
| WooCommerce orders (Jul 2026) | ~6,466: 6,331 completed, 70 refunded, 60 failed |

Expired licences: WooCommerce Subscriptions (unlicensed on live payments),
WooCommerce Memberships (inactive), GTM PRO, Import Export Suite, TIV
Multi-currency, Gravity Forms to Pardot.

## Users and roles

| Item | Value |
|---|---|
| "Anyone can register" | DISABLED (fixed by 11 Sep 2026; was enabled with default role Shop Manager, which is still the default if re-enabled) |
| Admin accounts | 20 (was 25): 7 external vendor accounts, 11 never logged in; vendor accounts Blitzm x5, Xecurify x1, The PG x1, plus `bitbucket@wpengine.com` deploy account. Ahilya removed |
| 2FA | no enforcement policy, configured on 3 of 20 |
| Agreed removals (Jul list, partly executed) | Ahilya (done), Ayush Saxena, David Arvaji, Holly Browne, James O'Brien, Justin Joseph, Justin Rivera, Krish, Ross James; `wpengine` to inactive |
| Custom roles | Content Lead, Content Creator, Group content creator, SEO Manager, SEO Editor, Supporter Care User (User Role Editor) |
| Undecided | Fiona Cahill, Hannah Langford, James Vilinsky, editors |
| Sanctioned 2FA | email code, 6 digits, 15-minute expiry, 10 backup codes |

## Integration stack

| Item | Value |
|---|---|
| miniOrange plugin | "Object Data Sync For Salesforce" (Enterprise); real-time, no cron |
| Primary key | post meta `salesforce_Opportunity_ID`; new membership key `salesforce_Membership_ID` |
| Staging mappings (30 Jul 2026) | Product2; Woo Payments Sync; OpportunityLineItem; `shop_order` to Opportunity; Product2 to WP Product; WP Product Variation to SF Product |
| Deleted mapping | Woo Members Sync |
| Sync failure rate | ~10.3 to 10.5% (FLS on `npe01__Opportunity__c`) |
| Write-back test | MO-05 |
| Ortto plugin | v1.0.24 |
| Other | Stripe gateway; Gravity Forms (+Stripe, +Pardot); WooCommerce Subscriptions; WooCommerce Memberships |
| SF to WP webhook keys | prod `7cf2…`, staging `8d8f…` (leaked, rotation unverified) |
| Synced-order fingerprint | `transaction_id`, `salesforce_Opportunity_ID`, `salesforce_npe01__OppPayment__c_ID`, `mo_sf_sync_line_item_ids` |

## Membership rebuild (Blitzm)

| Tier | Price |
|---|---|
| Individual | $84 |
| Concession | $65 (honour system) |
| Family | $132 (1 primary + up to 6; min 2, max 7) |
| Financial Hardship | $35 (hidden product, Supporter Care) |
| Free | $0 (Lifetime / Honorary / Fellow, Board approval) |

Duration 12 months; cease +15 months; reminders 31 days pre-expiry, 7 and 1
days pre-cease; auto-renewal default on. Conflicting help-text timing on
Keith Tsui's `Subscription__c` fields (10/37/60 style) is wired to a Conga
flow; escalate to James Vilinsky. Staging tests: 45, all "Not Tested" at 31 Jul
2026 (Blitzm 15, miniOrange 10, Salesforce dev 12, end-to-end 8). BZ-04
re-checks the 30 Jul Add-to-Cart bug (YITH Pre-Order / Cart block).

## Cart-flood incident (Jul 2026)

| Item | Value |
|---|---|
| Pattern | `/cart/?remove_item=…` from hundreds of IPs, product IDs 37909, 37910, 37911, 30651 |
| Impact | 4,410 5xx on /cart of 66,507 requests in 30 days; error rate 6.67%; cache hit 55.4%; ~30 GB on ~9 Jul vs 14 to 16 GB/day |
| Mitigation | WP Engine Web Rules Deny, ranked first: URI `^/cart` AND query contains `remove_item=` AND Referer NOT matching `birdlife\.org\.au` |
| Caveat | privacy browsers stripping Referer are false-positived |
| Also | `/wp-login.php` >50,000 hits in 30 days at 67% error |
