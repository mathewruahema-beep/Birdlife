# WordPress / WooCommerce: facts

The lookup table for `birdlife-wordpress`. **Edit this file first when a
value changes, then the prose.** Health numbers date from Jul to Aug 2026.

## Environments

| Environment | Value |
|---|---|
| Production | `birdlife.org.au`, WP Engine environment `birdlifeaus`, behind Cloudflare |
| Staging | `birdlifestage.wpengine.com` |
| Deployment | Git |
| Platform | WordPress 7.0, PHP 8.4.22, custom BirdLife theme |
| Registered users | 14,285 |
| miniOrange staging redirect URI | `https://birdlifestage.wpengine.com` |

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

## Health snapshot (Jul to Aug 2026)

| Item | Value |
|---|---|
| Score | 5/10 |
| Plugins | 82 (62 active, 20 inactive), 30 awaiting update, auto-updates off |
| Themes | 5 inactive |
| Page cache | 31 ms |
| Autoloaded options | 1,063 (~1 MB per request) |
| Risky active plugins | WP File Manager v8.0.2; WP phpMyAdmin; ACF to REST API v3.3.4 |
| WP 2FA | Melapress v3.1.1.2, four majors behind, not enforced |
| Logged emails with PII in DB | 82,089 |
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
| "Anyone can register" | ENABLED, default role Shop Manager |
| Admin accounts | 25 (6 Blitzm, 2 EnvisionCP, 1 The PG, 1 Xecurify, `wpengine` system account) |
| 2FA | enforced on none, configured on 3; 20 admins never logged in |
| Agreed removals (not executed) | Ahilya, Ayush Saxena, David Arvaji, Holly Browne, James O'Brien, Justin Joseph, Justin Rivera, Krish, Ross James; `wpengine` to inactive |
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
