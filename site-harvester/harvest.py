#!/usr/bin/env python3
"""
BirdLife Site Harvester
-----------------------
Pulls down an entire website and produces migration-ready output:

  raw/        exact copies of every page and asset (a browsable mirror)
  content/    one clean markdown file per page (title, metadata, body text)
  pages.csv   inventory of every page: URL, title, status, description, word count
  assets.csv  inventory of every asset: images, PDFs, CSS, JS, docs
  links.csv   the full internal link graph (for redirect planning)
  redirect-map.csv  every old URL with a blank column for its new home
  manifest.json     platform fingerprint + crawl statistics
  AUDIT.md    human-readable audit summary
  wordpress-export.xml  (optional, --wxr) WordPress WXR import file of all pages

Usage:
  python3 harvest.py https://example.org --out ./harvest/example
  python3 harvest.py https://afo.birdlife.org.au/afo/index.php/afo --out ./harvest/afo --wxr

Read-only and polite by default: honours robots.txt, one request at a time,
0.5s delay between requests.
"""

import argparse
import csv
import hashlib
import json
import re
import sys
import time
import urllib.robotparser
from collections import Counter, deque
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

UA = "BirdLifeSiteHarvester/1.0 (site migration audit; ICT; contact via birdlife.org.au)"
HTML_TYPES = ("text/html", "application/xhtml")
ASSET_EXTS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
    ".css", ".js", ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".mp4",
}
MAX_ASSET_BYTES = 100 * 1024 * 1024

PLATFORM_SIGNATURES = [
    ("WordPress", [r"/wp-content/", r"/wp-includes/", r"wp-json"]),
    ("Open Journal Systems (OJS)", [r"index\.php/[^/]+/(article|issue|oai)", r"pkp", r"ojs"]),
    ("Drupal", [r"/sites/default/files", r"drupal\.js", r"/sites/all/"]),
    ("Joomla", [r"/media/jui/", r"com_content", r"joomla"]),
    ("Squarespace", [r"squarespace\.com", r"static1\.squarespace"]),
    ("Wix", [r"wixstatic\.com", r"wix-code"]),
    ("Shopify", [r"cdn\.shopify\.com", r"myshopify"]),
]


def normalize(url: str) -> str:
    """Strip fragments, normalise trailing default pages."""
    p = urlparse(url)
    path = p.path or "/"
    return urlunparse((p.scheme, p.netloc.lower(), path, "", p.query, ""))


def same_site(url: str, roots: list, include_subdomains: bool) -> bool:
    host = urlparse(url).netloc.lower()
    for root in roots:
        rhost = urlparse(root).netloc.lower()
        if host == rhost:
            return True
        if include_subdomains and host.endswith("." + rhost.split(":")[0]):
            return True
    return False


def url_to_path(url: str, base_dir: Path) -> Path:
    """Map a URL to a safe local file path under base_dir."""
    p = urlparse(url)
    path = p.path.strip("/") or "index"
    if path.endswith("/"):
        path += "index"
    # keep it filesystem-safe
    path = re.sub(r"[^A-Za-z0-9._/\-]", "_", path)
    if p.query:
        path += "__q_" + hashlib.md5(p.query.encode()).hexdigest()[:10]
    parts = [seg[:120] for seg in path.split("/") if seg not in ("", ".", "..")]
    local = base_dir.joinpath(*parts) if parts else base_dir / "index"
    if not local.suffix:
        local = local.with_suffix(".html")
    return local


def looks_like_asset(url: str) -> bool:
    return Path(urlparse(url).path).suffix.lower() in ASSET_EXTS


def md_from_node(node, base_url: str) -> str:
    """Very small HTML→markdown walker: good enough for content migration."""
    out = []

    def walk(n, depth=0):
        if isinstance(n, NavigableString):
            text = re.sub(r"\s+", " ", str(n))
            if text.strip():
                out.append(text)
            return
        if not isinstance(n, Tag):
            return
        name = n.name.lower()
        if name in ("script", "style", "noscript", "nav", "form"):
            return
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            out.append("\n\n" + "#" * int(name[1]) + " ")
            for c in n.children:
                walk(c, depth)
            out.append("\n\n")
        elif name == "p":
            out.append("\n\n")
            for c in n.children:
                walk(c, depth)
            out.append("\n\n")
        elif name == "br":
            out.append("\n")
        elif name in ("ul", "ol"):
            out.append("\n")
            for i, li in enumerate(n.find_all("li", recursive=False), 1):
                marker = "-" if name == "ul" else f"{i}."
                out.append(f"\n{'  ' * depth}{marker} ")
                for c in li.children:
                    walk(c, depth + 1)
            out.append("\n")
        elif name == "a":
            href = n.get("href", "")
            inner = n.get_text(" ", strip=True)
            if inner:
                out.append(f"[{inner}]({urljoin(base_url, href)})")
        elif name == "img":
            src = n.get("src", "")
            alt = n.get("alt", "")
            if src:
                out.append(f"![{alt}]({urljoin(base_url, src)})")
        elif name in ("table",):
            out.append("\n\n")
            for i, tr in enumerate(n.find_all("tr")):
                cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
                out.append("| " + " | ".join(cells) + " |\n")
                if i == 0:
                    out.append("|" + "---|" * len(cells) + "\n")
            out.append("\n")
        elif name in ("strong", "b"):
            out.append("**")
            for c in n.children:
                walk(c, depth)
            out.append("**")
        elif name in ("em", "i"):
            out.append("*")
            for c in n.children:
                walk(c, depth)
            out.append("*")
        else:
            for c in n.children:
                walk(c, depth)

    walk(node)
    text = "".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main_content(soup: BeautifulSoup):
    """Pick the most content-ful region of the page."""
    for selector in ("main", "article", "[role=main]", "#content", ".content",
                     "#main", ".main", "#primary"):
        node = soup.select_one(selector)
        if node and len(node.get_text(strip=True)) > 100:
            return node
    return soup.body or soup


def fingerprint(html_samples: list) -> dict:
    """Identify the CMS/platform from generator tags and path signatures."""
    generators = Counter()
    scores = Counter()
    blob = "\n".join(html_samples).lower()
    for sample in html_samples:
        m = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', sample, re.I)
        if m:
            generators[m.group(1)] += 1
    for platform, sigs in PLATFORM_SIGNATURES:
        for sig in sigs:
            if re.search(sig, blob):
                scores[platform] += 1
    best = scores.most_common(1)
    return {
        "generator_tags": dict(generators),
        "signature_scores": dict(scores),
        "best_guess": (generators.most_common(1)[0][0] if generators
                       else (best[0][0] if best else "unknown")),
    }


def build_wxr(pages: list, site_url: str) -> str:
    """Emit a minimal WordPress WXR import file — every harvested page becomes a WP page."""
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for i, pg in enumerate(pages, 1):
        if not pg.get("markdown"):
            continue
        body_html = pg.get("content_html") or "<p></p>"
        slug = re.sub(r"[^a-z0-9]+", "-", (pg.get("title") or f"page-{i}").lower()).strip("-")[:80]
        items.append(f"""
  <item>
    <title>{escape(pg.get("title") or f"Page {i}")}</title>
    <link>{escape(pg["url"])}</link>
    <pubDate>{now}</pubDate>
    <dc:creator><![CDATA[harvester]]></dc:creator>
    <guid isPermaLink="false">{escape(pg["url"])}</guid>
    <description></description>
    <content:encoded><![CDATA[{body_html}]]></content:encoded>
    <excerpt:encoded><![CDATA[]]></excerpt:encoded>
    <wp:post_id>{i}</wp:post_id>
    <wp:post_date_gmt>{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}</wp:post_date_gmt>
    <wp:post_name><![CDATA[{slug}]]></wp:post_name>
    <wp:status><![CDATA[draft]]></wp:status>
    <wp:post_type><![CDATA[page]]></wp:post_type>
    <wp:post_parent>0</wp:post_parent>
    <wp:menu_order>{i}</wp:menu_order>
    <wp:is_sticky>0</wp:is_sticky>
  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0"
  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
  <title>Harvested: {escape(site_url)}</title>
  <link>{escape(site_url)}</link>
  <description>Site harvest for migration</description>
  <language>en-AU</language>
  <wp:wxr_version>1.2</wp:wxr_version>
{''.join(items)}
</channel>
</rss>
"""


def run(args):
    start_url = normalize(args.url)
    roots = [start_url] + [normalize(u) for u in (args.extra_root or [])]
    out = Path(args.out)
    raw_dir = out / "raw"
    content_dir = out / "content"
    for d in (raw_dir, content_dir):
        d.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = UA

    robots = None
    if not args.ignore_robots:
        robots = urllib.robotparser.RobotFileParser()
        try:
            base = urlparse(start_url)
            robots.set_url(f"{base.scheme}://{base.netloc}/robots.txt")
            robots.read()
        except Exception:
            robots = None

    queue = deque([start_url])
    seen = {start_url}
    pages, assets, links = [], [], []
    html_samples = []
    errors = []

    while queue and len(pages) + len(assets) < args.max_pages:
        url = queue.popleft()
        if robots and not robots.can_fetch(UA, url):
            errors.append((url, "blocked by robots.txt"))
            continue
        try:
            resp = session.get(url, timeout=30, stream=True)
            ctype = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
            is_html = any(ctype.startswith(t) for t in HTML_TYPES)
            body = b""
            for chunk in resp.iter_content(65536):
                body += chunk
                if len(body) > MAX_ASSET_BYTES:
                    break
        except Exception as e:
            errors.append((url, str(e)))
            continue

        local = url_to_path(url, raw_dir)
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(body)

        if is_html and resp.status_code == 200:
            html = body.decode(resp.encoding or "utf-8", errors="replace")
            if len(html_samples) < 20:
                html_samples.append(html)
            soup = BeautifulSoup(html, "html.parser")
            title = (soup.title.get_text(strip=True) if soup.title else "")
            desc_tag = soup.find("meta", attrs={"name": "description"})
            desc = desc_tag.get("content", "") if desc_tag else ""
            content_node = main_content(soup)
            md = md_from_node(content_node, url)
            page = {
                "url": url, "status": resp.status_code, "title": title,
                "description": desc, "word_count": len(md.split()),
                "local_path": str(local.relative_to(out)),
                "markdown": md, "content_html": str(content_node)[:500000],
            }
            pages.append(page)

            md_path = url_to_path(url, content_dir).with_suffix(".md")
            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text(
                f"---\nurl: {url}\ntitle: \"{title.replace(chr(34), chr(39))}\"\n"
                f"description: \"{desc.replace(chr(34), chr(39))[:300]}\"\n---\n\n{md}\n",
                encoding="utf-8")

            for a in soup.find_all("a", href=True):
                target = normalize(urljoin(url, a["href"]))
                if not target.startswith("http"):
                    continue
                links.append((url, target, a.get_text(" ", strip=True)[:120]))
                if same_site(target, roots, args.include_subdomains) and target not in seen:
                    seen.add(target)
                    queue.append(target)
            for tag, attr in (("img", "src"), ("link", "href"), ("script", "src"),
                              ("source", "src")):
                for t in soup.find_all(tag, **{attr: True}):
                    target = normalize(urljoin(url, t[attr]))
                    if (target.startswith("http") and target not in seen
                            and same_site(target, roots, args.include_subdomains)
                            and looks_like_asset(target)):
                        seen.add(target)
                        queue.append(target)
        else:
            assets.append({
                "url": url, "status": resp.status_code, "content_type": ctype,
                "bytes": len(body), "local_path": str(local.relative_to(out)),
            })

        done = len(pages) + len(assets)
        if done % 25 == 0:
            print(f"  {done} fetched, {len(queue)} queued", file=sys.stderr)
        time.sleep(args.delay)

    # ---- outputs ----
    with (out / "pages.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "status", "title", "description", "word_count", "local_path"])
        for p in pages:
            w.writerow([p["url"], p["status"], p["title"], p["description"],
                        p["word_count"], p["local_path"]])
    with (out / "assets.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "status", "content_type", "bytes", "local_path"])
        for a in assets:
            w.writerow([a["url"], a["status"], a["content_type"], a["bytes"], a["local_path"]])
    with (out / "links.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["from_url", "to_url", "anchor_text"])
        w.writerows(links)
    with (out / "redirect-map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["old_url", "new_url_TODO", "title"])
        for p in pages:
            w.writerow([p["url"], "", p["title"]])

    fp = fingerprint(html_samples)
    manifest = {
        "start_url": start_url,
        "harvested_at": datetime.now(timezone.utc).isoformat(),
        "pages": len(pages), "assets": len(assets),
        "internal_links": len(links), "errors": len(errors),
        "platform": fp,
        "total_asset_bytes": sum(a["bytes"] for a in assets),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    top_types = Counter(a["content_type"] for a in assets).most_common(8)
    audit = [
        f"# Site Audit — {start_url}",
        f"\nHarvested {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n",
        f"| Metric | Value |\n|---|---|",
        f"| Platform (best guess) | {fp['best_guess']} |",
        f"| Pages captured | {len(pages)} |",
        f"| Assets captured | {len(assets)} ({manifest['total_asset_bytes']//1024//1024} MB) |",
        f"| Internal links mapped | {len(links)} |",
        f"| Fetch errors | {len(errors)} |",
        "\n## Asset types\n",
        *[f"- {t or 'unknown'}: {c}" for t, c in top_types],
        "\n## Largest pages (by word count)\n",
        *[f"- {p['word_count']:>6} words — [{p['title'] or p['url']}]({p['url']})"
          for p in sorted(pages, key=lambda x: -x["word_count"])[:15]],
    ]
    if errors:
        audit += ["\n## Errors\n"] + [f"- {u} — {e}" for u, e in errors[:30]]
    audit += ["\n## Next steps\n",
              "1. Review `content/` markdown — this is your migratable content.",
              "2. Fill in `redirect-map.csv` once new URLs exist.",
              "3. `raw/` is a byte-exact mirror for reference and diffing.",
              "4. Re-run with `--wxr` to produce a WordPress import file."]
    (out / "AUDIT.md").write_text("\n".join(audit), encoding="utf-8")

    if args.wxr:
        (out / "wordpress-export.xml").write_text(build_wxr(pages, start_url), encoding="utf-8")

    print(f"\nDone: {len(pages)} pages, {len(assets)} assets, "
          f"{len(errors)} errors → {out}/AUDIT.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Harvest a website for migration.")
    ap.add_argument("url", help="Start URL (e.g. https://afo.birdlife.org.au/afo/index.php/afo)")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--max-pages", type=int, default=2000, help="Fetch cap (pages+assets)")
    ap.add_argument("--delay", type=float, default=0.5, help="Seconds between requests")
    ap.add_argument("--include-subdomains", action="store_true")
    ap.add_argument("--extra-root", action="append",
                    help="Additional root URL treated as in-scope (repeatable)")
    ap.add_argument("--ignore-robots", action="store_true",
                    help="Skip robots.txt (only for sites you own)")
    ap.add_argument("--wxr", action="store_true",
                    help="Also write wordpress-export.xml (WXR) for WordPress import")
    run(ap.parse_args())
