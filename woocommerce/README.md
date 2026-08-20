# WooCommerce integration — setup runbook

Gives Claude read access to orders, subscriptions and products on
`birdlife.org.au`, including the `sync-check` command that catches the two known
miniOrange sync bugs (Salesforce id write-back gap, FLS sync failures) from the
WooCommerce side.

The client is `wc.py` — **GET-only by design**. Writes to the live store go
through the WP admin, not tooling.

## Why the old keys cannot be reused

The previous `ck_/cs_` pair sat in plaintext in scheduled-routine prompts for
weeks (see repo README, "Credential exposure"). Treat them as burned. Setup
starts with rotation, not reuse.

## One-time setup — three steps, all in UIs Claude cannot reach

### 1. Rotate the keys (WP admin, ~10 min)

1. `birdlife.org.au/wp-admin` → **WooCommerce → Settings → Advanced → REST API**.
2. **Revoke** the existing exposed key.
3. **Add key** — description `Claude read-only`, user: a current ICT admin
   account (not a vendor account), permissions: **Read**. Copy the `ck_` and
   `cs_` values now; the secret is shown once.

Read permission covers everything `wc.py` does, including `system_status`.
Do not create a Read/Write key for this.

### 2. Put the keys in the Claude Code environment (claude.ai, ~2 min)

claude.ai → Code → **Environments** → this environment → **Environment
variables**:

| Variable | Value |
|---|---|
| `WOO_CK` | the new consumer key |
| `WOO_CS` | the new consumer secret |

Optional: `WOO_BASE_URL=https://birdlifestage.wpengine.com/wp-json/wc/v3` in a
separate environment if staging access is ever wanted; production is the default.

Never paste the keys into a chat message, a routine prompt, or a file in this
repo. Environment variables are the only sanctioned location.

### 3. Allow the domain on the environment's network policy (claude.ai, ~2 min)

Verified 20 Aug 2026: this environment's egress proxy denies
`birdlife.org.au:443` (CONNECT 403, policy denial). In the same environment
settings, add `birdlife.org.au` to the allowed domains (and
`birdlifestage.wpengine.com` if staging is configured).

If org policy cannot allow the domain, the fallback is the Zapier WooCommerce
app — it runs from Zapier's cloud, but requires the paid WooCommerce Zapier
extension installed on the site. Decision item, see `ECOSYSTEM.md` §3.5.

## Verify

In a fresh session (env vars load at container start):

```
python3 woocommerce/wc.py ping
python3 woocommerce/wc.py sync-check --days 7
```

`ping` confirms auth and reachability. `sync-check` exits 1 and lists paid
orders missing a Salesforce id — expected to fire occasionally until the
miniOrange write-back bug is fixed; that is the point of the check.

Then tell Claude the keys are live, and it will un-park the WooCommerce
order-sync check in the weekday dashboard routine
(`trig_0126KYAM3TAaZpBQKN8UeVdk`) — referencing the env vars, never inline
credentials.

## Troubleshooting

- **CONNECT 403 / "tunnel failed"** — step 3 not done, or reverted.
- **HTTP 401** — key revoked or vars mistyped; re-check step 2 values.
- **HTTP 403 with a Cloudflare or WAF page in the body** — the request cleared
  our proxy but Cloudflare challenged a cloud-datacentre IP. Add a WAF skip
  rule for `/wp-json/wc/v3/*` requests carrying valid Basic auth, scoped as
  narrowly as possible.
- **`subscriptions` returns 404** — the WooCommerce Subscriptions plugin
  licence/state issue (it is currently running unlicensed); the endpoint ships
  with that plugin.

## What Claude does with this

The project skill at `.claude/skills/birdlife-woocommerce/SKILL.md` loads in
any session with this repo and teaches the commands, the meta keys, and the
cross-check flow against Salesforce. Weekly `sync-check` output belongs on the
ICT dashboard alongside the Salesforce and Asana panels.
