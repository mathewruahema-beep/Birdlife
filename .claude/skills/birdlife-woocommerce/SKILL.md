---
name: birdlife-woocommerce
description: Read WooCommerce orders, subscriptions and products on birdlife.org.au via the repo's wc.py client, and run the order→Salesforce sync check. Use for any question about WooCommerce orders, payments on the website, membership subscriptions, product/SKU lookups, or whether orders reached Salesforce. Trigger on "WooCommerce", "web order", "shop order", "subscription", "sync check", "did this order reach Salesforce".
---

# BirdLife WooCommerce access

Client: `python3 woocommerce/wc.py <command>` from the repo root. GET-only.
Credentials are the `WOO_CK`/`WOO_CS` environment variables — if unset, or if
the proxy denies `birdlife.org.au`, setup is incomplete: point the user at
`woocommerce/README.md` and stop; do not ask for keys in chat and never accept
keys pasted into prompts (put them in env settings and rotate if pasted).

## Commands

| Command | Use |
|---|---|
| `ping` | auth/reachability check — run first in a new session |
| `orders [--status s] [--days N] [--limit N] [--all]` | recent orders with Salesforce-id column |
| `order <id>` | full order JSON including all meta_data |
| `subscriptions [--status s]` | membership/recurring state (needs Woo Subscriptions active) |
| `products [--search text]` | product/SKU lookup |
| `system` | WP/WC/PHP versions + active plugins with pending updates |
| `sync-check [--days N]` | paid orders missing a Salesforce id; exits 1 if any |
| `get <path> [k=v ...]` | any other wc/v3 endpoint, raw JSON |

## The sync check — what a hit means

miniOrange pushes paid orders to Salesforce and writes the returned Id to order
meta `salesforce_Opportunity_ID` (membership build will use
`salesforce_Membership_ID`). Two known live bugs:

1. **Write-back gap** — order synced but Id never written back. Next status
   change creates a duplicate Salesforce record.
2. **FLS failures** — ~10% of sync attempts fail outright on
   `npe01__Opportunity__c` field-level security.

For each order `sync-check` flags, query Salesforce (Salesforce Production
connector, SOQL on Opportunity by order number/amount/date):

- **Found in SF** → write-back gap. Report the order/Opportunity pair; the fix
  is writing the meta, and until then the order is a duplicate risk.
- **Not in SF** → sync failure. Point at miniOrange logs and integration-user
  FLS. Do not create the Opportunity by hand without being asked.

## Facts that prevent wrong answers

- Production `birdlife.org.au`; staging `birdlifestage.wpengine.com` has 1-day
  subscription periods, `-STAGING` SKUs, and different Salesforce ids — never
  compare staging data to production Salesforce.
- ~A$11k/month flows through WooCommerce; Subscriptions runs unlicensed and
  Memberships is inactive — a 404 from `subscriptions` or empty membership
  data is likely a licence/state issue, not an outage.
- Salesforce remains the system of record for membership status.
- Money follow-ups: Stripe connector for charges/refunds, NetSuite for GL.
