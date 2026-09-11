# Cloudflare and email authentication: facts

The lookup table for `birdlife-cloudflare`. **Edit this file first when a
value changes, then the prose.**

## Accounts

| Account | ID |
|---|---|
| Domain.admin@birdlife.org.au's Account | `3bd8acff3934a9c3427a8fa1d23b2a5f` |
| Mathew.hema@birdlife.org.au's Account | `9bff172bca45472c845f907b300eebcd` |

MCP client header to avoid passing the id each call: `cf-account-id`.

## Deployed developer-platform surfaces (verified live, Aug 2026)

| Surface | State |
|---|---|
| Workers | 0 |
| D1 | 0 |
| KV | 0 |
| R2 | not enabled (403) |

Role: CDN, DNS, reverse proxy in front of WP Engine `birdlifeaus`. AWS Route 53
holds health checks only (4: `birdata.birdlife.org.au`,
`aussiebirdcount.org.au`); authoritative DNS is outside AWS.

## Connector (`Cloudflare Developer Platform`)

Exposes Workers, R2, D1, KV, Hyperdrive, documentation search. Does NOT
expose zones, DNS records, WAF, page rules, rate limiting, bot management or
analytics. DNS and edge changes happen in the dashboard by whoever holds the
zone.

## Email authentication findings

| Record | Finding | Fix |
|---|---|---|
| SPF (`birdlife.org.au` TXT) | missing `include:_spf.salesforce.com` | add after sender inventory and lookup count; reviewed change with rollback |
| DMARC | `p=reject; pct=10` | ramp `pct` 10 to 50 to 100 once SPF and DKIM pass for every sender |
| Salesforce DKIM | not aligned | Enhanced Domains + DKIM signing in Setup, Email, Deliverability |

Sender inventory to check before any SPF change: Exchange Online, Salesforce
(zeus@ and receipting), Exclaimer, Campaign Monitor, Ortto, Raisely,
Employment Hero, WordPress / WP Engine transactional, Payments2Us, Conga,
Zapier email steps, NetSuite notifications. SPF limit: 10 DNS lookups.

## Cart-flood mitigation location

Applied in WP Engine Web Rules, not Cloudflare (details in
`birdlife-wordpress/references/facts.md`). Durable control proposed:
Cloudflare WAF or rate limit on `/cart` and `/wp-login.php`; needs an owner.
