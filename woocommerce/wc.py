#!/usr/bin/env python3
"""Read-only WooCommerce REST client for birdlife.org.au.

Credentials come from environment variables — never from arguments, prompt
text, or files in this repo (see woocommerce/README.md for why):

    WOO_CK        consumer key   (ck_...)
    WOO_CS        consumer secret (cs_...)
    WOO_BASE_URL  optional, default https://birdlife.org.au/wp-json/wc/v3
                  (staging: https://birdlifestage.wpengine.com/wp-json/wc/v3)
    WOO_SF_META_KEYS  optional comma list of Salesforce id meta keys checked
                  by sync-check, default salesforce_Opportunity_ID,salesforce_Membership_ID

This client is deliberately GET-only. Writes to the live store go through
the WP admin or an explicitly reviewed change, not through ad-hoc tooling.

Commands:
    ping                          auth + reachability check
    orders   [--status s] [--days N] [--limit N] [--all]
    order    <id>                 full order JSON
    subscriptions [--status s] [--limit N] [--all]
    products [--search text] [--limit N] [--all]
    system                        store environment + active plugin summary
    sync-check [--days N]         paid orders missing a Salesforce id (exit 1 if any)
    get <path> [k=v ...] [--all]  raw GET against any wc/v3 path

Only stdlib. Honors HTTPS_PROXY and the system CA store automatically.
"""

import argparse
import base64
import datetime as dt
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("WOO_BASE_URL", "https://birdlife.org.au/wp-json/wc/v3").rstrip("/")
SF_META_KEYS = [
    k.strip()
    for k in os.environ.get(
        "WOO_SF_META_KEYS", "salesforce_Opportunity_ID,salesforce_Membership_ID"
    ).split(",")
    if k.strip()
]
PER_PAGE = 100
MAX_PAGES = 50  # safety cap for --all: 5,000 records


def _auth_header():
    ck, cs = os.environ.get("WOO_CK"), os.environ.get("WOO_CS")
    if not ck or not cs:
        sys.exit(
            "WOO_CK / WOO_CS are not set. These are configured as environment "
            "variables in the Claude Code environment settings — see woocommerce/README.md."
        )
    token = base64.b64encode(f"{ck}:{cs}".encode()).decode()
    return {"Authorization": f"Basic {token}", "User-Agent": "birdlife-wc-client/1.0"}


def _get(path, params=None):
    url = f"{BASE}/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=_auth_header())
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    ctx = ssl.create_default_context(cafile=cafile)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            body = json.load(resp)
            total = resp.headers.get("X-WP-Total")
            total_pages = resp.headers.get("X-WP-TotalPages")
            return body, total, total_pages
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        sys.exit(f"HTTP {e.code} from {url}\n{detail}")
    except urllib.error.URLError as e:
        sys.exit(
            f"Cannot reach {url}: {e.reason}\n"
            "If this is a proxy CONNECT 403, birdlife.org.au is not on this "
            "environment's network allowlist — see woocommerce/README.md step 3."
        )


def _get_all(path, params, fetch_all, limit):
    params = dict(params or {})
    if not fetch_all:
        params.setdefault("per_page", min(limit or 25, PER_PAGE))
        body, total, _ = _get(path, params)
        return body if isinstance(body, list) else [body], total
    out, page = [], 1
    params["per_page"] = PER_PAGE
    while page <= MAX_PAGES:
        params["page"] = page
        body, total, total_pages = _get(path, params)
        out.extend(body)
        if not total_pages or page >= int(total_pages):
            return out, total
        page += 1
    print(f"note: stopped at safety cap of {MAX_PAGES * PER_PAGE} records", file=sys.stderr)
    return out, total


def _after_iso(days):
    d = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    return d.strftime("%Y-%m-%dT%H:%M:%S")


def _order_row(o):
    sf = {m["key"]: m.get("value") for m in o.get("meta_data", []) if m.get("key") in SF_META_KEYS}
    sf_id = next((v for v in sf.values() if v), None)
    return {
        "id": o["id"],
        "date": (o.get("date_created") or "")[:16],
        "status": o.get("status"),
        "total": o.get("total"),
        "currency": o.get("currency"),
        "salesforce_id": sf_id or None,
    }


def _print_table(rows, cols):
    if not rows:
        print("(no records)")
        return
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    for r in rows:
        print("  ".join(str(r.get(c, "") if r.get(c) is not None else "—").ljust(widths[c]) for c in cols))


def cmd_ping(_args):
    _, total, _ = _get("orders", {"per_page": 1})
    host = urllib.parse.urlparse(BASE).netloc
    print(f"OK — authenticated against {host}, {total or '?'} orders visible")


def cmd_orders(args):
    params = {"orderby": "date", "order": "desc"}
    if args.status:
        params["status"] = args.status
    if args.days:
        params["after"] = _after_iso(args.days)
    orders, total = _get_all("orders", params, args.all, args.limit)
    _print_table([_order_row(o) for o in orders], ["id", "date", "status", "total", "currency", "salesforce_id"])
    if total:
        print(f"\n{len(orders)} shown of {total} matching")


def cmd_order(args):
    body, _, _ = _get(f"orders/{args.id}")
    json.dump(body, sys.stdout, indent=2)
    print()


def cmd_subscriptions(args):
    params = {}
    if args.status:
        params["status"] = args.status
    subs, total = _get_all("subscriptions", params, args.all, args.limit)
    rows = [
        {
            "id": s["id"],
            "status": s.get("status"),
            "total": s.get("total"),
            "next_payment": (s.get("next_payment_date_gmt") or "")[:10],
            "customer": s.get("billing", {}).get("email", ""),
        }
        for s in subs
    ]
    _print_table(rows, ["id", "status", "total", "next_payment", "customer"])
    if total:
        print(f"\n{len(subs)} shown of {total} matching")


def cmd_products(args):
    params = {}
    if args.search:
        params["search"] = args.search
    products, total = _get_all("products", params, args.all, args.limit)
    rows = [
        {"id": p["id"], "sku": p.get("sku"), "name": p.get("name"), "price": p.get("price"), "status": p.get("status")}
        for p in products
    ]
    _print_table(rows, ["id", "sku", "name", "price", "status"])
    if total:
        print(f"\n{len(products)} shown of {total} matching")


def cmd_system(_args):
    body, _, _ = _get("system_status")
    env = body.get("environment", {})
    print(f"site:        {env.get('site_url')}")
    print(f"wp version:  {env.get('wp_version')}   wc version: {env.get('version', body.get('version'))}")
    print(f"php:         {env.get('php_version')}")
    active = body.get("active_plugins", [])
    print(f"\nactive plugins: {len(active)}")
    for p in sorted(active, key=lambda x: x.get("name", "")):
        latest = p.get("version_latest")
        stale = f"  (update available: {latest})" if latest and latest != p.get("version") else ""
        print(f"  {p.get('name')} {p.get('version')}{stale}")


def cmd_sync_check(args):
    # Paid orders only: these are the ones miniOrange must have pushed to
    # Salesforce and written the returned Id back onto ("Salesforce UUID: None"
    # on a paid order is the known write-back bug).
    params = {"status": "processing,completed", "after": _after_iso(args.days)}
    orders, _ = _get_all("orders", params, True, None)
    rows = [_order_row(o) for o in orders]
    missing = [r for r in rows if not r["salesforce_id"]]
    print(f"paid orders in last {args.days} days: {len(rows)}")
    print(f"missing a Salesforce id ({', '.join(SF_META_KEYS)}): {len(missing)}\n")
    if missing:
        _print_table(missing, ["id", "date", "status", "total", "currency"])
        print(
            "\nNext step: for each order above, check Salesforce for an Opportunity "
            "with this order's number/amount. Present in SF = write-back gap "
            "(duplicate risk on next status change). Absent = sync failure "
            "(check miniOrange logs and integration-user FLS)."
        )
        sys.exit(1)
    print("all paid orders in the window carry a Salesforce id")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping").set_defaults(fn=cmd_ping)

    p = sub.add_parser("orders")
    p.add_argument("--status")
    p.add_argument("--days", type=int)
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_orders)

    p = sub.add_parser("order")
    p.add_argument("id", type=int)
    p.set_defaults(fn=cmd_order)

    p = sub.add_parser("subscriptions")
    p.add_argument("--status")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_subscriptions)

    p = sub.add_parser("products")
    p.add_argument("--search")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_products)

    sub.add_parser("system").set_defaults(fn=cmd_system)

    p = sub.add_parser("sync-check")
    p.add_argument("--days", type=int, default=7)
    p.set_defaults(fn=cmd_sync_check)

    p = sub.add_parser("get")
    p.add_argument("path")
    p.add_argument("params", nargs="*", help="key=value query params")
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_get)

    args = ap.parse_args()
    args.fn(args)


def cmd_get(args):
    params = dict(kv.split("=", 1) for kv in args.params)
    if args.all:
        body, total = _get_all(args.path, params, True, None)
    else:
        body, total, _ = _get(args.path, params)
    json.dump(body, sys.stdout, indent=2)
    print()
    if total:
        print(f"X-WP-Total: {total}", file=sys.stderr)


if __name__ == "__main__":
    main()
