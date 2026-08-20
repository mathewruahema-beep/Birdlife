#!/usr/bin/env python3
"""
OAI-PMH metadata harvester — companion to harvest.py for OJS journals.

The web crawl gets you the pages; this gets you the AUTHORITATIVE list of every
published article with clean metadata, straight from the journal's OAI-PMH feed.

Usage:
  python3 oai_harvest.py https://afo.birdlife.org.au/afo/index.php/afo/oai --out ./harvest/afo-oai

Outputs:
  identify.xml, sets.xml    repository info (includes earliest record date)
  records-NNN.xml           every raw ListRecords response page
  articles.csv              identifier, datestamp, title, creators, date, sets, url
"""
import argparse
import csv
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

OAI = "{http://www.openarchives.org/OAI/2.0/}"
DC = "{http://purl.org/dc/elements/1.1/}"
UA = "BirdLifeSiteHarvester/1.0 (OAI-PMH; site migration audit)"


def get(session, url, params):
    r = session.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("endpoint", help="OAI endpoint, e.g. .../index.php/afo/oai")
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", default="oai_dc")
    ap.add_argument("--delay", type=float, default=0.5)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA

    for verb, fname in (("Identify", "identify.xml"), ("ListSets", "sets.xml")):
        try:
            r = get(s, args.endpoint, {"verb": verb})
            (out / fname).write_bytes(r.content)
            print(f"saved {fname}")
        except Exception as e:
            print(f"warn: {verb} failed: {e}", file=sys.stderr)
        time.sleep(args.delay)

    rows, page, token = [], 0, None
    while True:
        params = {"verb": "ListRecords"}
        if token:
            params["resumptionToken"] = token
        else:
            params["metadataPrefix"] = args.prefix
        try:
            r = get(s, args.endpoint, params)
        except Exception as e:
            print(f"error fetching page {page}: {e}", file=sys.stderr)
            break
        page += 1
        (out / f"records-{page:03d}.xml").write_bytes(r.content)

        root = ET.fromstring(r.content)
        err = root.find(f"{OAI}error")
        if err is not None:
            print(f"OAI error: {err.get('code')} {err.text}", file=sys.stderr)
            break
        lst = root.find(f"{OAI}ListRecords")
        if lst is None:
            break
        for rec in lst.findall(f"{OAI}record"):
            hdr = rec.find(f"{OAI}header")
            ident = hdr.findtext(f"{OAI}identifier", "")
            stamp = hdr.findtext(f"{OAI}datestamp", "")
            sets = ";".join(e.text or "" for e in hdr.findall(f"{OAI}setSpec"))
            if hdr.get("status") == "deleted":
                rows.append([ident, stamp, "(deleted)", "", "", sets, ""])
                continue
            meta = rec.find(f"{OAI}metadata")
            dcb = meta[0] if meta is not None and len(meta) else None
            def dcv(tag, joiner="; "):
                if dcb is None:
                    return ""
                return joiner.join((e.text or "").strip() for e in dcb.findall(DC + tag))
            url = ""
            if dcb is not None:
                for e in dcb.findall(DC + "identifier"):
                    if (e.text or "").startswith("http"):
                        url = e.text.strip()
                        break
            rows.append([ident, stamp, dcv("title"), dcv("creator"),
                         dcv("date"), sets, url])
        tok_el = lst.find(f"{OAI}resumptionToken")
        token = tok_el.text.strip() if (tok_el is not None and tok_el.text
                                        and tok_el.text.strip()) else None
        print(f"page {page}: {len(rows)} records so far"
              + (f" (token continues)" if token else " (complete)"))
        if not token:
            break
        time.sleep(args.delay)

    with (out / "articles.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["identifier", "datestamp", "title", "creators", "date", "sets", "url"])
        w.writerows(rows)
    years = {}
    for r_ in rows:
        y = (r_[4] or r_[1])[:4]
        years[y] = years.get(y, 0) + 1
    print(f"\nDone: {len(rows)} records -> {out}/articles.csv")
    for y in sorted(years):
        print(f"  {y}: {years[y]}")


if __name__ == "__main__":
    main()
