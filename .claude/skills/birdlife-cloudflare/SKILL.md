---
name: birdlife-cloudflare
description: Operator knowledge for BirdLife Australia's Cloudflare estate — two accounts, CDN/DNS/proxy role in front of WP Engine, what the connected MCP can and cannot do, and where the real edge controls actually live. Use for any task about DNS records, SPF/DKIM, CDN caching, WAF, rate limiting, DDoS or bot mitigation, or Cloudflare Workers/R2/D1/KV. Trigger on "Cloudflare", "DNS record", "SPF", "nameserver", "WAF", "rate limit", "cache", "Worker", "R2 bucket", or a birdlife.org.au domain question.
---

# BirdLife Australia — Cloudflare

## Accounts — verified live

| Account | ID |
|---|---|
| Domain.admin@birdlife.org.au's Account | `3bd8acff3934a9c3427a8fa1d23b2a5f` |
| Mathew.hema@birdlife.org.au's Account | `9bff172bca45472c845f907b300eebcd` |

Two accounts for one organisation is itself a finding. Consolidate or document why both exist. Set a `cf-account-id` header in MCP client config to avoid passing `account_id` on every call.

## What is actually deployed — verified live, this session

| Surface | State |
|---|---|
| Workers | **0** |
| D1 databases | **0** |
| KV namespaces | **0** |
| R2 | **403 — "Please enable R2 through the Cloudflare Dashboard"** (never enabled) |

**BirdLife uses Cloudflare purely as CDN, DNS and reverse proxy.** There is no developer-platform footprint. Do not propose a Workers-based solution as though the platform is already in use; it would be a new capability with new operational ownership.

## The capability gap you must state out loud

The connected Cloudflare MCP is the **Developer Platform** server. It exposes Workers, R2, D1, KV, Hyperdrive and documentation search.

**It exposes no tools for zones, DNS records, WAF rules, page rules, rate limiting, bot management or analytics.**

That means: when someone asks you to "add a DNS record", "check the WAF", or "put a rate limit on /cart", you cannot do it from here. Say so immediately and offer the real paths — the Cloudflare dashboard, the Cloudflare API via an authenticated request, or WP Engine's own controls. Do not imply capability you do not have.

## Architecture context

`birdlife.org.au` production is **WP Engine (environment `birdlifeaus`) behind Cloudflare CDN**. Staging is `birdlifestage.wpengine.com`. AWS Route 53 holds **health checks only** (4, all production: `birdata.birdlife.org.au`, `aussiebirdcount.org.au`) — **authoritative DNS is external to AWS**, consistent with Cloudflare holding it.

## The one documented DNS finding

**The birdlife.org.au SPF TXT record does not include `include:_spf.salesforce.com`.** This is why Salesforce Case emails are rejected by Asana's inbound email (SPF/DKIM validation reads them as spoofed). Fixing it is a domain-wide email-authentication change affecting deliverability and anti-spoofing for every sender on birdlife.org.au — it goes through IT/security review with a rollback plan, not an ad-hoc edit.

Paired change: enable Enhanced Domains and DKIM signing in Salesforce Setup → Email → Deliverability.

## The cart-flood incident — mitigated at WP Engine, NOT Cloudflare

This gets misattributed constantly. Get it right.

**Symptom (Jul 2026):** repeated 504 Gateway Timeouts; site error rate 6.67%; cache hit ratio 55.4%; **4,410 5xx errors on /cart out of 66,507 requests over 30 days**; bandwidth spiked to ~30GB on ~9 Jul against a 14-16GB/day baseline.

**Root cause:** a sustained, distributed, automated flood of `/cart/?remove_item=<hash>&_wpnonce=…&add-to-cart=…` from hundreds of IPs worldwide, cycling product IDs 37909 / 37910 / 37911 / 30651 with varied user agents. Cart pages are session-specific and uncacheable, so every request reached PHP and the database → PHP worker exhaustion → 504s for attackers and legitimate customers alike. Attribution unresolved; consistent with scripted abuse.

**Mitigation deployed — in WP Engine Web Rules, not Cloudflare:** a "Deny" rule ranked first, matching URI regex `^/cart` AND query containing `remove_item=` AND Referer NOT matching `birdlife\.org\.au`.

**Known caveat:** privacy browsers that strip the Referer header get false-positived. That is a real customer-impact trade-off, currently accepted.

Follow-ups still open: monitor logs; **ask WP Engine for platform-level bot/DDoS mitigation**. The strategic point is that this class of attack is exactly what Cloudflare's WAF and rate limiting are for, and BirdLife paid for Cloudflare and mitigated at the origin host instead. If the question is "should we move this control to Cloudflare", the honest answer is yes, and it needs an owner.

`/wp-login.php` also took **>50,000 hits in 30 days at a 67% error rate** — brute-force noise that belongs behind an edge rate limit.

## Operating rules
1. **Declare the tool gap** the moment a DNS/WAF/rate-limit request arrives. Do not attempt a workaround through unrelated tools.
2. **Never call the cart-flood fix a Cloudflare change.**
3. Any SPF change is a security-reviewed, rollback-planned change affecting all mail from the domain.
4. If Workers, R2, D1 or KV are proposed, treat it as introducing a new platform with new ownership, not as using something already there.
5. Confirm which of the two accounts a request refers to before acting.
