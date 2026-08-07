#!/usr/bin/env python3
"""Extract NetSuite and Salesforce datasets to CSV for Power BI.

Runs every query file under ../queries/ and writes one CSV per query into --out.
Point Power BI's Folder connector at that directory; refresh re-reads the files.

    pip install -r requirements.txt
    cp .env.example .env && <fill it in> && set -a && . ./.env && set +a
    python extract.py --out ./out

Why files rather than a live connector: NetSuite's supported ODBC/JDBC path is
SuiteAnalytics Connect, a paid add-on BirdLife does not have. This route uses the
SuiteQL REST endpoint that is already enabled, costs nothing, and leaves an
auditable artefact on disk. See ../README.md for the trade-offs.

No credential is ever written to disk by this script — everything comes from the
environment, and the CSVs contain query results only.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import hmac
import os
import random
import string
import sys
import time
import urllib.parse
from pathlib import Path

import requests

QUERIES = Path(__file__).resolve().parent.parent / "queries"
SF_API_VERSION = "v64.0"
HTTP_TIMEOUT = 300


def env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"Missing required environment variable: {name}")
    return value


# --------------------------------------------------------------------------- #
# NetSuite — SuiteQL over REST, authenticated with OAuth 1.0a token-based auth.
# --------------------------------------------------------------------------- #

def _pct(value: object) -> str:
    """Percent-encode per RFC 5849. Note the unreserved set — urlencode's default
    differs and produces signatures NetSuite rejects with a bare 401."""
    return urllib.parse.quote(str(value), safe="-._~")


def _netsuite_auth_header(method: str, url: str, params: dict[str, str]) -> str:
    oauth = {
        "oauth_consumer_key": env("NS_CONSUMER_KEY"),
        "oauth_token": env("NS_TOKEN_ID"),
        "oauth_signature_method": "HMAC-SHA256",
        "oauth_timestamp": str(int(time.time())),
        "oauth_nonce": "".join(random.choices(string.ascii_letters + string.digits, k=32)),
        "oauth_version": "1.0",
    }
    # Query-string params are part of the signature base. Omitting limit/offset here
    # is the usual cause of "works on page 1, 401s on page 2".
    signed = {**params, **oauth}
    normalized = "&".join(f"{_pct(k)}={_pct(signed[k])}" for k in sorted(signed))
    base_string = "&".join([method.upper(), _pct(url), _pct(normalized)])
    signing_key = f'{_pct(env("NS_CONSUMER_SECRET"))}&{_pct(env("NS_TOKEN_SECRET"))}'
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha256).digest()
    ).decode()

    oauth["oauth_signature"] = signature
    pairs = ", ".join(f'{_pct(k)}="{_pct(v)}"' for k, v in oauth.items())
    # realm is the account ID, uppercase, and is NOT part of the signature.
    return f'OAuth realm="{env("NS_ACCOUNT").upper()}", {pairs}'


def netsuite_suiteql(query: str) -> list[dict]:
    account = env("NS_ACCOUNT")
    host = account.lower().replace("_", "-")
    url = f"https://{host}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"

    rows: list[dict] = []
    offset, limit = 0, 1000
    while True:
        params = {"limit": str(limit), "offset": str(offset)}
        response = requests.post(
            url,
            params=params,
            json={"q": query},
            headers={
                "Authorization": _netsuite_auth_header("POST", url, params),
                "Prefer": "transient",
                "Content-Type": "application/json",
            },
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        rows.extend(payload.get("items", []))
        print(f"    …{len(rows)} rows", file=sys.stderr)
        # Pagination is mandatory, not optional: a single page silently truncates
        # at 1000 and looks like a complete result set.
        if not payload.get("hasMore"):
            return rows
        offset += limit


# --------------------------------------------------------------------------- #
# Salesforce — REST query API, client-credentials OAuth.
# --------------------------------------------------------------------------- #

def salesforce_token() -> str:
    response = requests.post(
        f'{env("SF_DOMAIN")}/services/oauth2/token',
        data={
            "grant_type": "client_credentials",
            "client_id": env("SF_CLIENT_ID"),
            "client_secret": env("SF_CLIENT_SECRET"),
        },
        timeout=HTTP_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def salesforce_query(soql: str, token: str) -> list[dict]:
    domain = env("SF_DOMAIN")
    url = f"{domain}/services/data/{SF_API_VERSION}/query"
    params: dict | None = {"q": soql}
    rows: list[dict] = []
    while True:
        response = requests.get(
            url, params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        rows.extend(payload["records"])
        print(f"    …{len(rows)} of {payload.get('totalSize')} rows", file=sys.stderr)
        if payload.get("done"):
            return rows
        url, params = f"{domain}{payload['nextRecordsUrl']}", None


def flatten(record: dict, prefix: str = "") -> dict:
    """Flatten SOQL relationship fields: Owner.Name arrives as a nested object.

    Drops the `attributes` block Salesforce attaches to every record and every
    nested object — it carries the API URL, not data, and would otherwise become
    a column of no value in the model.
    """
    out: dict = {}
    for key, value in record.items():
        if key == "attributes":
            continue
        if isinstance(value, dict):
            out.update(flatten(value, f"{prefix}{key}."))
        else:
            out[f"{prefix}{key}"] = value
    return out


# --------------------------------------------------------------------------- #

def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        print(f"  ! {path.name}: query returned no rows — writing nothing", file=sys.stderr)
        return
    # Union of keys, first-seen order: SuiteQL omits null columns per row, so
    # keying off row 0 alone silently drops fields.
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  → {path} ({len(rows)} rows, {len(columns)} columns)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("./out"),
                        help="directory Power BI points at (default ./out)")
    parser.add_argument("--only", choices=["netsuite", "salesforce"],
                        help="run just one source")
    args = parser.parse_args()

    if args.only != "salesforce":
        for sql_file in sorted((QUERIES / "netsuite").glob("*.sql")):
            print(f"NetSuite: {sql_file.name}")
            rows = netsuite_suiteql(sql_file.read_text(encoding="utf-8"))
            write_csv(rows, args.out / f"netsuite_{sql_file.stem}.csv")

    if args.only != "netsuite":
        soql_files = sorted((QUERIES / "salesforce").glob("*.soql"))
        if soql_files:
            token = salesforce_token()
            for soql_file in soql_files:
                print(f"Salesforce: {soql_file.name}")
                records = salesforce_query(soql_file.read_text(encoding="utf-8"), token)
                write_csv([flatten(r) for r in records],
                          args.out / f"salesforce_{soql_file.stem}.csv")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
