#!/usr/bin/env python3
"""
Remote IT job search tool for Mathew Hema.

Finds remote senior IT roles that are friendly to a Melbourne-based worker
(AEST/AEDT time zone, Australia/APAC/worldwide eligibility) but are not
Melbourne office roles, scores them against profile.json, keeps a tracked
pipeline in data/jobs.json, prepares application packs, and regenerates the
local board (board.html).

Usage:
  python jobsearch.py search [--sources a,b,c] [--max-age 45] [--dry-run]
  python jobsearch.py links                      # one-click search URLs for boards without APIs
  python jobsearch.py list [--status X] [--min-score N] [--all]
  python jobsearch.py show <id>
  python jobsearch.py set <id> <status> [--note TEXT] [--next TEXT] [--due YYYY-MM-DD]
  python jobsearch.py add --title T --company C --url U [--location L] [--source S] [--description D]
  python jobsearch.py prepare <id> [--claude]    # application pack in applications/<id>-<slug>/
  python jobsearch.py board                      # regenerate board.html with current data embedded
  python jobsearch.py export                     # data/jobs.csv and data/board-export.json
  python jobsearch.py import <file.json>         # merge a board export back into data/jobs.json

Statuses: sourced, shortlisted, applied, interviewing, offer, closed
"""

from __future__ import annotations

import argparse
import csv
import signal
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import textwrap
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    print("Missing dependency: pip install requests", file=sys.stderr)
    sys.exit(1)

HERE = Path(__file__).resolve().parent
PROFILE_PATH = HERE / "profile.json"
DATA_DIR = HERE / "data"
JOBS_PATH = DATA_DIR / "jobs.json"
APPS_DIR = HERE / "applications"
BOARD_PATH = HERE / "board.html"

STATUSES = ["sourced", "shortlisted", "applied", "interviewing", "offer", "closed"]
UA = {"User-Agent": "Mozilla/5.0 (compatible; jobsearch-tool/1.0; personal job search)"}
TIMEOUT = 25
TODAY = dt.date.today()


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def load_jobs() -> dict:
    if JOBS_PATH.exists():
        return json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    return {"updated": None, "jobs": []}


def save_jobs(store: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    store["updated"] = dt.datetime.now().isoformat(timespec="seconds")
    store["jobs"].sort(key=lambda j: (-j.get("score", 0), j.get("posted") or ""), reverse=False)
    JOBS_PATH.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")


def strip_html(s: str | None) -> str:
    if not s:
        return ""
    s = html.unescape(s)
    s = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def make_id(company: str, title: str, url: str) -> str:
    key = norm(company) + "|" + norm(title)
    if len(key) < 6:
        key = url
    return hashlib.sha1(key.encode()).hexdigest()[:10]


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:50]


def to_date(value) -> str | None:
    """Normalise many date shapes to YYYY-MM-DD."""
    if value in (None, "", 0):
        return None
    try:
        if isinstance(value, (int, float)):
            if value > 1e12:
                value = value / 1000
            return dt.datetime.utcfromtimestamp(value).date().isoformat()
        s = str(value).strip()
        if re.fullmatch(r"\d{10,13}", s):
            return to_date(int(s))
        m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
        if m:
            return m.group(1)
        for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%d %b %Y", "%Y/%m/%d"):
            try:
                return dt.datetime.strptime(s, fmt).date().isoformat()
            except ValueError:
                pass
    except Exception:
        return None
    return None


def age_days(posted: str | None) -> int | None:
    if not posted:
        return None
    try:
        return (TODAY - dt.date.fromisoformat(posted)).days
    except ValueError:
        return None


def get_json(url: str, **kw):
    r = requests.get(url, headers=UA, timeout=TIMEOUT, **kw)
    r.raise_for_status()
    return r.json()


# ----------------------------------------------------------------------------
# location policy and scoring
# ----------------------------------------------------------------------------

def _any(patterns, text) -> str | None:
    for p in patterns:
        if re.search(p, text, flags=re.I):
            return p
    return None


def classify_location(profile: dict, location: str, description: str, remote_only_source: bool) -> tuple[str, str]:
    """Return (policy, reason). policy in explicit_apac_or_au | worldwide | unrestricted | unknown | excluded."""
    pol = profile["location_policy"]
    loc = (location or "").strip()
    loc_l = loc.lower()
    desc_head = (description or "")[:1500].lower()

    hit = _any(pol["exclude_patterns"], loc_l)
    if hit:
        return "excluded", f"location '{loc}' matches exclude rule '{hit}'"

    # Hard residency restrictions stated in the description body.
    for pat in (r"must (be|reside|live) (located )?in (the )?(us|usa|united states|uk|united kingdom|canada|eu|europe)",
                r"(us|usa|uk|eu|canada)[- ]based (candidates )?only",
                r"only (accepting|considering) (candidates|applicants) (located |based )?in (the )?(us|usa|united states|uk|canada|europe|eu)",
                r"authori[sz]ed to work in the (united states|us|uk|united kingdom|canada)"):
        if re.search(pat, desc_head):
            if not _any(pol["allow_patterns"], desc_head):
                return "excluded", f"description restricts residency ('{pat}')"

    allow_hit = _any(pol["allow_patterns"], loc_l)
    if allow_hit:
        if allow_hit in ("worldwide", "anywhere", "global", "international", "remote - any", "any location", "any country"):
            return "worldwide", f"location '{loc}' is {allow_hit}"
        return "explicit_apac_or_au", f"location '{loc}' matches '{allow_hit}'"

    restricted_hit = _any(pol["restricted_region_patterns"], loc_l)
    if restricted_hit:
        return "excluded", f"location '{loc}' is restricted to another region ('{restricted_hit}')"

    if "remote" in loc_l or remote_only_source:
        return "unrestricted", f"remote with no stated restriction ('{loc or 'remote board'}')"
    return "unknown", f"location '{loc}' gives no remote signal"


def score_job(profile: dict, job: dict) -> tuple[int, list[str]]:
    sc = profile["scoring"]
    title = (job.get("title") or "").lower()
    text = (title + " " + (job.get("description") or "")).lower()
    score = 0
    reasons: list[str] = []

    best_title = 0
    best_kw = None
    for kw, pts in sc["title_keywords"].items():
        if kw in title and pts > best_title:
            best_title, best_kw = pts, kw
    if best_kw:
        score += best_title
        reasons.append(f"title matches '{best_kw}' (+{best_title})")

    for kw, pts in sc["seniority_bonus"].items():
        if re.search(rf"\b{re.escape(kw)}\b", title):
            score += pts
            reasons.append(f"seniority '{kw}' (+{pts})")

    skill_hits = []
    for kw, pts in sc["skill_keywords"].items():
        if kw in text:
            skill_hits.append((kw, pts))
    skill_hits.sort(key=lambda x: -x[1])
    skill_pts = min(40, sum(p for _, p in skill_hits))
    if skill_hits:
        score += skill_pts
        reasons.append("skills: " + ", ".join(k for k, _ in skill_hits[:8]) + f" (+{skill_pts})")

    for kw, pts in sc["negative_keywords"].items():
        if kw in title:
            score += pts
            reasons.append(f"title contains '{kw}' ({pts})")

    rc = sc["remote_confidence"].get(job.get("remote_policy", "unknown"), 0)
    score += rc
    if rc:
        reasons.append(f"remote policy {job.get('remote_policy')} (+{rc})")

    a = age_days(job.get("posted"))
    if a is not None and a > 30:
        score -= 5
        reasons.append("posted more than 30 days ago (-5)")

    return max(0, min(100, score)), reasons


# ----------------------------------------------------------------------------
# sources (each returns a list of raw job dicts in the common shape)
# ----------------------------------------------------------------------------

def raw(title, company, url, location="", posted=None, description="", source="", salary="", tags=None, remote_only=True):
    return {
        "title": (title or "").strip(),
        "company": (company or "").strip(),
        "url": (url or "").strip(),
        "location_raw": (location or "").strip(),
        "posted": to_date(posted),
        "description": strip_html(description)[:6000],
        "source": source,
        "salary": (salary or "").strip() if isinstance(salary, str) else (str(salary) if salary else ""),
        "tags": tags or [],
        "_remote_only": remote_only,
    }


def src_remotive(profile):
    out = []
    seen = set()
    for q in profile["targets"]["search_queries"]:
        data = get_json("https://remotive.com/api/remote-jobs", params={"search": q, "limit": 100})
        for j in data.get("jobs", []):
            if j.get("id") in seen:
                continue
            seen.add(j.get("id"))
            out.append(raw(j.get("title"), j.get("company_name"), j.get("url"), j.get("candidate_required_location"),
                           j.get("publication_date"), j.get("description"), "remotive", j.get("salary"),
                           [j.get("category"), j.get("job_type")]))
        time.sleep(0.4)
    return out


def src_himalayas(profile):
    out = []
    pages = profile["sources"].get("himalayas_pages", 5)
    for p in range(pages):
        data = get_json("https://himalayas.app/jobs/api", params={"limit": 100, "offset": p * 100})
        jobs = data.get("jobs", data if isinstance(data, list) else [])
        if not jobs:
            break
        for j in jobs:
            locs = j.get("locationRestrictions") or j.get("locations") or []
            tz = j.get("timezoneRestrictions") or []
            loc = ", ".join([str(x) for x in locs] + [str(x) for x in tz]) or "Remote"
            sal = ""
            if j.get("minSalary") or j.get("maxSalary"):
                sal = f"{j.get('minSalary') or ''}-{j.get('maxSalary') or ''} {j.get('currency') or ''}".strip()
            out.append(raw(j.get("title"), j.get("companyName"), j.get("applicationLink") or j.get("url"), loc,
                           j.get("pubDate"), j.get("description") or j.get("excerpt"), "himalayas", sal,
                           (j.get("categories") or []) + ([j.get("seniority")] if j.get("seniority") else [])))
        time.sleep(0.4)
    return out


def src_jobicy(profile):
    out = []
    for geo in profile["sources"].get("jobicy_geos", ["australia"]):
        data = get_json("https://jobicy.com/api/v2/remote-jobs", params={"count": 100, "geo": geo})
        for j in data.get("jobs", []):
            sal = ""
            if j.get("annualSalaryMin") or j.get("annualSalaryMax"):
                sal = f"{j.get('annualSalaryMin') or ''}-{j.get('annualSalaryMax') or ''} {j.get('salaryCurrency') or ''}".strip()
            out.append(raw(j.get("jobTitle"), j.get("companyName"), j.get("url"), j.get("jobGeo"), j.get("pubDate"),
                           j.get("jobDescription") or j.get("jobExcerpt"), "jobicy", sal,
                           [j.get("jobLevel"), j.get("jobType")] + (j.get("jobIndustry") or [])))
        time.sleep(0.4)
    return out


def src_arbeitnow(profile):
    out = []
    for p in range(1, profile["sources"].get("arbeitnow_pages", 3) + 1):
        data = get_json("https://www.arbeitnow.com/api/job-board-api", params={"page": p})
        for j in data.get("data", []):
            if not j.get("remote"):
                continue
            out.append(raw(j.get("title"), j.get("company_name"), j.get("url"), j.get("location") or "Remote",
                           j.get("created_at"), j.get("description"), "arbeitnow", "", j.get("tags") or []))
        time.sleep(0.4)
    return out


def src_remoteok(profile):
    data = get_json("https://remoteok.com/api")
    out = []
    for j in data:
        if not isinstance(j, dict) or not j.get("position"):
            continue
        sal = ""
        if j.get("salary_min") or j.get("salary_max"):
            sal = f"{j.get('salary_min') or ''}-{j.get('salary_max') or ''} USD"
        out.append(raw(j.get("position"), j.get("company"), j.get("url"), j.get("location") or "Remote",
                       j.get("date"), j.get("description"), "remoteok", sal, j.get("tags") or []))
    return out


def src_wwr(profile):
    out = []
    for feed in profile["sources"].get("wwr_feeds", []):
        r = requests.get(feed, headers=UA, timeout=TIMEOUT)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        for item in root.iter("item"):
            t = item.findtext("title") or ""
            company, _, title = t.partition(":")
            if not title:
                title, company = t, ""
            region = item.findtext("region") or "Remote"
            out.append(raw(title, company, item.findtext("link"), region, item.findtext("pubDate"),
                           item.findtext("description"), "weworkremotely"))
    return out


def src_workingnomads(profile):
    data = get_json("https://www.workingnomads.com/api/exposed_jobs/")
    out = []
    for j in data:
        out.append(raw(j.get("title"), j.get("company_name"), j.get("url"), j.get("location") or "Remote",
                       j.get("pub_date"), j.get("description"), "workingnomads", "",
                       [j.get("category_name")] + [t.strip() for t in (j.get("tags") or "").split(",") if t.strip()]))
    return out


REMOTE_SIGNAL = re.compile(r"remote|work from anywhere|distributed|work from home|wfh", re.I)


def src_greenhouse(profile):
    out = []
    for token in profile["sources"].get("greenhouse_boards", []):
        try:
            data = get_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs", params={"content": "true"})
        except Exception as e:  # one bad token should not kill the source
            print(f"  greenhouse/{token}: {e}", file=sys.stderr)
            continue
        for j in data.get("jobs", []):
            loc = (j.get("location") or {}).get("name", "")
            content = html.unescape(j.get("content") or "")
            if not (REMOTE_SIGNAL.search(loc) or REMOTE_SIGNAL.search(content[:2000])):
                continue
            out.append(raw(j.get("title"), token, j.get("absolute_url"), loc, j.get("updated_at"), content,
                           f"greenhouse:{token}", "", [], remote_only=False))
        time.sleep(0.3)
    return out


def src_lever(profile):
    out = []
    for site in profile["sources"].get("lever_boards", []):
        try:
            data = get_json(f"https://api.lever.co/v0/postings/{site}", params={"mode": "json"})
        except Exception as e:
            print(f"  lever/{site}: {e}", file=sys.stderr)
            continue
        for j in data:
            cats = j.get("categories") or {}
            loc = cats.get("location") or ""
            wt = (j.get("workplaceType") or "").lower()
            if not (wt == "remote" or REMOTE_SIGNAL.search(loc)):
                continue
            out.append(raw(j.get("text"), site, j.get("hostedUrl"), loc, j.get("createdAt"), j.get("descriptionPlain"),
                           f"lever:{site}", "", [cats.get("commitment"), cats.get("team")], remote_only=False))
        time.sleep(0.3)
    return out


def src_ashby(profile):
    out = []
    for name in profile["sources"].get("ashby_boards", []):
        try:
            data = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{name}", params={"includeCompensation": "true"})
        except Exception as e:
            print(f"  ashby/{name}: {e}", file=sys.stderr)
            continue
        for j in data.get("jobs", []):
            loc = j.get("location") or ""
            if not (j.get("isRemote") or REMOTE_SIGNAL.search(loc)):
                continue
            out.append(raw(j.get("title"), name, j.get("jobUrl"), loc, j.get("publishedAt"), j.get("descriptionPlain"),
                           f"ashby:{name}", "", [j.get("employmentType")], remote_only=False))
        time.sleep(0.3)
    return out


def src_adzuna(profile):
    app_id, app_key = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        raise RuntimeError("set ADZUNA_APP_ID and ADZUNA_APP_KEY (free at developer.adzuna.com) to enable")
    out = []
    for cc in profile["sources"].get("adzuna_countries", ["au"]):
        for q in profile["targets"]["search_queries"][:10]:
            data = get_json(f"https://api.adzuna.com/v1/api/jobs/{cc}/search/1",
                            params={"app_id": app_id, "app_key": app_key, "results_per_page": 50,
                                    "what": q + " remote", "content-type": "application/json"})
            for j in data.get("results", []):
                sal = ""
                if j.get("salary_min") or j.get("salary_max"):
                    sal = f"{int(j.get('salary_min') or 0)}-{int(j.get('salary_max') or 0)} {cc.upper()}D"
                out.append(raw(j.get("title"), (j.get("company") or {}).get("display_name"), j.get("redirect_url"),
                               (j.get("location") or {}).get("display_name", ""), j.get("created"), j.get("description"),
                               f"adzuna:{cc}", sal, [], remote_only=False))
            time.sleep(0.3)
    return out


def src_jooble(profile):
    key = os.environ.get("JOOBLE_API_KEY")
    if not key:
        raise RuntimeError("set JOOBLE_API_KEY (free at jooble.org/api/about) to enable")
    out = []
    for q in profile["targets"]["search_queries"][:10]:
        r = requests.post(f"https://jooble.org/api/{key}", json={"keywords": q + " remote", "location": "Australia"},
                          headers=UA, timeout=TIMEOUT)
        r.raise_for_status()
        for j in r.json().get("jobs", []):
            out.append(raw(j.get("title"), j.get("company"), j.get("link"), j.get("location"), j.get("updated"),
                           j.get("snippet"), "jooble", j.get("salary"), [], remote_only=False))
        time.sleep(0.3)
    return out


SOURCES = {
    "remotive": src_remotive,
    "himalayas": src_himalayas,
    "jobicy": src_jobicy,
    "arbeitnow": src_arbeitnow,
    "remoteok": src_remoteok,
    "weworkremotely": src_wwr,
    "workingnomads": src_workingnomads,
    "greenhouse": src_greenhouse,
    "lever": src_lever,
    "ashby": src_ashby,
    "adzuna": src_adzuna,
    "jooble": src_jooble,
}


# ----------------------------------------------------------------------------
# search links for boards without a usable public API
# ----------------------------------------------------------------------------

def search_links(profile: dict) -> list[tuple[str, str, str]]:
    q = urllib.parse.quote_plus
    queries = ["IT Manager", "Head of IT", "Head of Technology", "IT Operations Manager", "Information Security Manager", "CIO"]
    links = []
    for t in queries:
        links += [
            ("SEEK (AU, remote filter)", t, f"https://www.seek.com.au/{q(t).replace('+', '-')}-jobs?workarrangement=1"),
            ("LinkedIn (AU, remote)", t, f"https://www.linkedin.com/jobs/search/?keywords={q(t)}&location=Australia&f_WT=2&f_TPR=r604800"),
            ("Indeed AU (remote)", t, f"https://au.indeed.com/jobs?q={q(t)}&l=Remote&fromage=14"),
            ("EthicalJobs (NFP, AU)", t, f"https://www.ethicaljobs.com.au/search?keywords={q(t)}&work_types=remote"),
            ("Jora (AU)", t, f"https://au.jora.com/j?q={q(t + ' remote')}&l=Australia"),
            ("Glassdoor (AU)", t, f"https://www.glassdoor.com.au/Job/australia-{q(t).replace('+', '-').lower()}-jobs-SRCH_IL.0,9_IN16_KO10,{10 + len(t)}.htm?remoteWorkType=1"),
            ("SEEK NZ (remote)", t, f"https://www.seek.co.nz/{q(t).replace('+', '-')}-jobs?workarrangement=1"),
        ]
    links += [
        ("Remote Rocketship (AU)", "all", "https://www.remoterocketship.com/country/australia/"),
        ("Jobgether (APAC)", "all", "https://jobgether.com/remote-jobs/apac"),
        ("Dynamite Jobs (AU/NZ)", "all", "https://dynamitejobs.com/location/remote-jobs-in-australia"),
        ("InfoSec Job Board (APAC remote)", "security", "https://www.infosecjobboard.com/remote-cybersecurity-jobs-in-asia-pacific"),
        ("Working Nomads (AU)", "all", "https://www.workingnomads.com/remote-australia-jobs"),
        ("Working Nomads (APAC)", "all", "https://www.workingnomads.com/remote-apac-jobs"),
        ("Remotive (AU)", "all", "https://remotive.com/remote-australia-jobs"),
        ("Himalayas (AU)", "all", "https://himalayas.app/jobs/countries/australia"),
        ("Wellfound (remote, AU)", "all", "https://wellfound.com/remote/australia"),
        ("Technology Leaders Australia (fractional CIO network)", "fractional", "https://theconsultingcio.com/join-network"),
        ("Fractional Jobs", "fractional", "https://www.fractionaljobs.io/"),
        ("Hays AU (IT leadership)", "all", "https://www.hays.com.au/jobs/it-jobs?q=IT%20Manager&remote=true"),
        ("Robert Half AU (technology)", "all", "https://www.roberthalf.com/au/en/jobs/all/technology?remote=true"),
        ("Talent.com AU", "all", "https://au.talent.com/jobs?k=IT+Manager+remote&l=Australia"),
        ("NotFor-Profit People (AU NFP)", "all", "https://notforprofitpeople.com.au/jobs/?search=technology"),
        ("Pro Bono Australia jobs", "all", "https://probonoaustralia.com.au/jobs/?search_keywords=technology"),
    ]
    return links


# ----------------------------------------------------------------------------
# pipeline
# ----------------------------------------------------------------------------

def normalise_and_score(profile: dict, r: dict) -> dict | None:
    if not r["title"] or not r["url"]:
        return None
    policy, why = classify_location(profile, r["location_raw"], r["description"], r.get("_remote_only", True))
    if policy == "excluded":
        return None
    job = {
        "id": make_id(r["company"], r["title"], r["url"]),
        "title": r["title"],
        "company": r["company"] or "(unknown)",
        "url": r["url"],
        "source": r["source"],
        "location_raw": r["location_raw"],
        "remote_policy": policy,
        "remote_reason": why,
        "posted": r["posted"],
        "salary": r["salary"],
        "tags": [t for t in r["tags"] if t],
        "description": r["description"],
    }
    job["score"], job["reasons"] = score_job(profile, job)
    if job["score"] < profile["scoring"]["min_score_to_keep"]:
        return None
    return job


def merge(store: dict, found: list[dict]) -> tuple[int, int]:
    by_id = {j["id"]: j for j in store["jobs"]}
    new = updated = 0
    now = TODAY.isoformat()
    for j in found:
        cur = by_id.get(j["id"])
        if cur:
            for k in ("title", "url", "location_raw", "remote_policy", "remote_reason", "posted", "salary", "tags", "description", "score", "reasons", "source"):
                cur[k] = j[k]
            cur["last_seen"] = now
            updated += 1
        else:
            j.update({"status": "sourced", "notes": "", "next_action": "", "next_due": "", "applied_on": "",
                      "first_seen": now, "last_seen": now})
            store["jobs"].append(j)
            by_id[j["id"]] = j
            new += 1
    return new, updated


def cmd_search(args):
    profile = load_profile()
    store = load_jobs()
    wanted = [s.strip() for s in args.sources.split(",")] if args.sources else list(SOURCES)
    max_age = args.max_age or profile["sources"].get("max_age_days", 45)
    all_raw: list[dict] = []
    report = []
    for name in wanted:
        fn = SOURCES.get(name)
        if not fn:
            print(f"unknown source: {name}", file=sys.stderr)
            continue
        t0 = time.time()
        try:
            rows = fn(profile)
            all_raw += rows
            report.append((name, "ok", len(rows), f"{time.time() - t0:.1f}s"))
        except Exception as e:
            report.append((name, "FAILED", 0, str(e)[:110]))
    kept = []
    for r in all_raw:
        a = age_days(r["posted"])
        if a is not None and a > max_age:
            continue
        j = normalise_and_score(profile, r)
        if j:
            kept.append(j)
    # dedupe within this run, keep the higher score
    dedup: dict[str, dict] = {}
    for j in kept:
        if j["id"] not in dedup or j["score"] > dedup[j["id"]]["score"]:
            dedup[j["id"]] = j
    kept = list(dedup.values())

    print("\nSource report")
    for name, status, n, note in report:
        print(f"  {name:16} {status:7} {n:5} raw   {note}")
    print(f"\nRaw rows: {len(all_raw)}   Passed location policy and score gate: {len(kept)}")

    if args.dry_run:
        for j in sorted(kept, key=lambda x: -x["score"])[:40]:
            print(f"  [{j['score']:3}] {j['title']} | {j['company']} | {j['location_raw']} | {j['source']}")
        return

    new, updated = merge(store, kept)
    save_jobs(store)
    print(f"Merged: {new} new, {updated} refreshed. Store now holds {len(store['jobs'])} jobs -> {JOBS_PATH}")
    thr = profile["scoring"]["shortlist_threshold"]
    top = [j for j in store["jobs"] if j["status"] == "sourced" and j["score"] >= thr]
    top.sort(key=lambda x: -x["score"])
    if top:
        print(f"\n{len(top)} sourced roles at or above the shortlist threshold ({thr}):")
        for j in top[:25]:
            print(f"  {j['id']}  [{j['score']:3}] {j['title']} | {j['company']} | {j['location_raw'] or 'remote'} | {j['source']}")
    write_board(store)
    print(f"Board regenerated -> {BOARD_PATH}")


def cmd_links(args):
    profile = load_profile()
    for site, q, url in search_links(profile):
        print(f"{site:42} {q:32} {url}")


def cmd_list(args):
    store = load_jobs()
    rows = store["jobs"]
    if args.status:
        rows = [j for j in rows if j["status"] == args.status]
    elif not args.all:
        rows = [j for j in rows if j["status"] != "closed"]
    if args.min_score:
        rows = [j for j in rows if j["score"] >= args.min_score]
    rows.sort(key=lambda x: (-x["score"], x["title"]))
    for j in rows:
        due = f" due {j['next_due']}" if j.get("next_due") else ""
        print(f"{j['id']}  [{j['score']:3}] {j['status']:12} {j['title'][:48]:48} | {j['company'][:28]:28} | {j['source']}{due}")
    print(f"\n{len(rows)} jobs")


def find(store, jid):
    for j in store["jobs"]:
        if j["id"] == jid or j["id"].startswith(jid):
            return j
    sys.exit(f"no job with id {jid}")


def cmd_show(args):
    j = find(load_jobs(), args.id)
    d = dict(j)
    desc = d.pop("description", "")
    print(json.dumps(d, indent=2, ensure_ascii=False))
    print("\n" + textwrap.fill(desc[:3000], 100))


def cmd_set(args):
    store = load_jobs()
    j = find(store, args.id)
    if args.status not in STATUSES:
        sys.exit(f"status must be one of {STATUSES}")
    j["status"] = args.status
    if args.status == "applied" and not j.get("applied_on"):
        j["applied_on"] = TODAY.isoformat()
    if args.note:
        stamp = TODAY.isoformat()
        j["notes"] = (j.get("notes", "") + f"\n[{stamp}] {args.note}").strip()
    if args.next is not None:
        j["next_action"] = args.next
    if args.due is not None:
        j["next_due"] = args.due
    save_jobs(store)
    write_board(store)
    print(f"{j['id']} -> {j['status']}  {j['title']} | {j['company']}")


def cmd_add(args):
    profile = load_profile()
    store = load_jobs()
    r = raw(args.title, args.company, args.url, args.location or "Remote", TODAY.isoformat(), args.description or "",
            args.source or "manual", remote_only=False)
    policy, why = classify_location(profile, r["location_raw"], r["description"], False)
    job = {
        "id": make_id(r["company"], r["title"], r["url"]), "title": r["title"], "company": r["company"], "url": r["url"],
        "source": r["source"], "location_raw": r["location_raw"], "remote_policy": policy if policy != "excluded" else "unknown",
        "remote_reason": why, "posted": r["posted"], "salary": "", "tags": [], "description": r["description"],
    }
    job["score"], job["reasons"] = score_job(profile, job)
    new, _ = merge(store, [job])
    save_jobs(store)
    write_board(store)
    print(f"{'added' if new else 'already present'}: {job['id']}  [{job['score']}] {job['title']} | {job['company']}")


# ----------------------------------------------------------------------------
# application pack
# ----------------------------------------------------------------------------

def pick_relevant(profile: dict, job: dict) -> dict:
    text = (job["title"] + " " + job.get("description", "")).lower()
    hits = [kw for kw in profile["scoring"]["skill_keywords"] if kw in text]
    exp_ranked = []
    for e in profile["experience"]:
        blob = (e["title"] + " " + e["sector"] + " " + " ".join(e["bullets"])).lower()
        n = sum(1 for kw in hits if kw in blob)
        exp_ranked.append((n, e))
    exp_ranked.sort(key=lambda x: -x[0])
    hl_ranked = []
    for h in profile["highlights"]:
        n = sum(1 for kw in hits if kw in h.lower())
        hl_ranked.append((n, h))
    hl_ranked.sort(key=lambda x: -x[0])
    return {"hits": hits, "experience": [e for _, e in exp_ranked[:3]], "highlights": [h for _, h in hl_ranked[:3]]}


def template_pack(profile: dict, job: dict) -> dict[str, str]:
    c = profile["candidate"]
    rel = pick_relevant(profile, job)
    company = job["company"]
    title = job["title"]
    skills_line = ", ".join(rel["hits"][:8]) if rel["hits"] else "ICT strategy, security and service delivery"

    cover = f"""# Cover letter draft: {title} at {company}

Dear Hiring Manager,

I am applying for the {title} role at {company}. I am a senior technology leader based in Melbourne with 25 years across ICT management, cyber security and digital transformation, including Chief Information Officer and Head of Technology appointments. I work remotely on Australian Eastern time and have led distributed teams and vendors across Asia Pacific, the USA, the UK and India.

The pattern of my career matches what this role appears to need. I inherit fragmented or under-invested ICT functions, establish governance and a security baseline, rebuild the team and vendor model, and reduce cost while lifting service levels. Three examples:

- {rel['highlights'][0]}
- {rel['highlights'][1]}
- {rel['highlights'][2]}

Your posting emphasises {skills_line}. My most relevant recent experience:

"""
    for e in rel["experience"]:
        cover += f"**{e['title']}, {e['org']} ({e['period']})**\n"
        for b in e["bullets"][:2]:
            cover += f"- {b}\n"
        cover += "\n"
    cover += f"""I am comfortable at board and executive level and remain hands-on with delivery. I would welcome a conversation about how I can help {company}.

Kind regards,
{c['name']}
{c['email']}
Melbourne, Australia (AEST/AEDT)
"""

    tailoring = f"""# Resume tailoring notes: {title} at {company}

Score {job['score']}/100. Reasons: {'; '.join(job.get('reasons', []))}
Remote policy: {job.get('remote_policy')} ({job.get('remote_reason')})
Posted: {job.get('posted') or 'unknown'}   Source: {job['source']}   Link: {job['url']}

## Keywords found in the posting that also appear in your profile
{', '.join(rel['hits']) or '(none detected; read the posting and add the employer language by hand)'}

## Suggested headline for this application
{c['headline']} | {title.title()} candidate

## Reorder the resume so these three roles lead the experience section
"""
    for e in rel["experience"]:
        tailoring += f"- {e['title']}, {e['org']} ({e['period']})\n"
    tailoring += """
## Checklist before submitting
- [ ] Mirror the employer's exact title and 3 to 5 of their own phrases in the profile paragraph.
- [ ] Put the remote and time zone statement in the header: "Melbourne, Australia. Remote. AEST/AEDT with overlap to APAC, US Pacific mornings and UK afternoons."
- [ ] Confirm work rights wording the employer asks for (citizenship, PR, right to work in Australia).
- [ ] Quantify: budget owned, team size, cost reduction, maturity level reached.
- [ ] Remove anything that reads as local-office-only (venue AV, on-site fleet) unless the posting values it.
- [ ] Save as PDF named "Mathew Hema - {title} - {company}.pdf".
""".replace("{title}", title).replace("{company}", company)

    screening = f"""# Screening answers: {title} at {company}

**Where are you located and what hours will you work?**
Melbourne, Australia. I work remotely on AEST/AEDT and routinely overlap with APAC, US Pacific mornings and UK afternoons. I have run regional operations reporting to a Global CIO in the USA with teams in the UK and India, so asynchronous and cross time zone delivery is normal for me.

**Do you have the right to work?**
{c['work_rights']}

**Why are you leaving your current role?**
I have delivered the security uplift, integration and e-commerce programme I was brought in to do at BirdLife Australia and I am looking for a larger remit. Adjust this to the truth of the moment before sending.

**Salary expectation?**
Full-time from AUD {profile['targets']['salary_floor_aud']:,} base plus super depending on scope. Contract or fractional from AUD {profile['targets']['day_rate_floor_aud']:,} per day. State a range only when asked; ask for theirs first.

**Notice period?**
Four weeks. Confirm your contract before answering.

**What is your experience with {skills_line}?**
Draw from: {'; '.join(b for e in rel['experience'][:2] for b in e['bullets'][:2])}

**Describe a time you reduced cost without hurting service.**
Crawford & Company Asia Pacific: managed a $5M+ regional ICT budget and delivered about 10% cost reduction and 10% productivity improvement year on year while the business grew from 165 to over 1,000 staff. Good Shepherd Microfinance: reduced ICT cost every quarter while maintaining SLAs during a cloud transformation.

**Describe your security leadership.**
Implemented Essential Eight Maturity Level 3 in two regulated organisations (Partners Wealth Group and Medical Indemnity Protection Society) and ISO 27001 processes across Asia Pacific at Crawford. Currently leading an Essential Eight aligned uplift with a SaaS and identity overlay at BirdLife Australia, reported to the board.
"""
    jobmd = f"# {title} at {company}\n\nSource: {job['source']}\nURL: {job['url']}\nLocation: {job.get('location_raw')}\nPosted: {job.get('posted')}\nSalary: {job.get('salary') or 'not stated'}\n\n---\n\n{job.get('description', '')}\n"
    return {"cover-letter.md": cover, "tailoring-notes.md": tailoring, "screening-answers.md": screening, "job.md": jobmd}


def claude_pack(profile: dict, job: dict) -> dict[str, str] | None:
    """Optional: ask Claude to write the pack from the full profile and posting. Needs `pip install anthropic`
    and ANTHROPIC_API_KEY (or `ant auth login`)."""
    try:
        import anthropic
    except ImportError:
        print("pip install anthropic to use --claude; falling back to templates", file=sys.stderr)
        return None
    client = anthropic.Anthropic()
    prompt = f"""You are helping Mathew Hema, a senior ICT executive in Melbourne, apply for a remote role.
Write three documents for this specific posting, in Australian English, no em dashes, plain and direct.
Return them as JSON with keys "cover-letter.md", "tailoring-notes.md", "screening-answers.md".

Rules:
- Use only facts in the profile. Never invent employers, metrics, certifications or dates.
- Cover letter: 280 to 380 words, mirror the employer's language, state Melbourne/AEST remote working plainly, three quantified proof points.
- Tailoring notes: which roles to lead with, which bullets to rewrite and how, keywords from the posting to add, anything in the profile that could read as local-office-only.
- Screening answers: location and hours, work rights, salary approach (full-time floor AUD {profile['targets']['salary_floor_aud']}, day rate floor AUD {profile['targets']['day_rate_floor_aud']}), notice, and three role-specific behavioural answers drawn from the profile.

PROFILE (JSON):
{json.dumps({k: profile[k] for k in ('candidate', 'highlights', 'capabilities', 'technical', 'experience', 'credentials')}, ensure_ascii=False)}

POSTING:
Title: {job['title']}
Company: {job['company']}
Location text: {job.get('location_raw')}
Description:
{job.get('description', '')[:9000]}
"""
    with client.beta.messages.stream(
        model="claude-opus-5",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        print("Claude declined this request; falling back to templates", file=sys.stderr)
        return None
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    m = re.search(r"\{.*\}", text, flags=re.S)
    try:
        data = json.loads(m.group(0) if m else text)
    except Exception:
        print("Could not parse Claude output as JSON; saving raw text", file=sys.stderr)
        return {"claude-output.md": text}
    data["job.md"] = template_pack(profile, job)["job.md"]
    return data


def cmd_prepare(args):
    profile = load_profile()
    store = load_jobs()
    j = find(store, args.id)
    pack = None
    if args.claude:
        pack = claude_pack(profile, j)
    if pack is None:
        pack = template_pack(profile, j)
    out = APPS_DIR / f"{j['id']}-{slugify(j['company'])}-{slugify(j['title'])}"
    out.mkdir(parents=True, exist_ok=True)
    for name, body in pack.items():
        (out / name).write_text(body, encoding="utf-8")
    if j["status"] == "sourced":
        j["status"] = "shortlisted"
    j["next_action"] = j.get("next_action") or "Review pack, tailor resume, submit"
    j["notes"] = (j.get("notes", "") + f"\n[{TODAY.isoformat()}] Application pack prepared at {out.relative_to(HERE)}").strip()
    save_jobs(store)
    write_board(store)
    print(f"Pack written to {out}\n  " + "\n  ".join(pack.keys()))
    print(f"\nApply here: {j['url']}\nThen run: python jobsearch.py set {j['id']} applied --note \"Submitted via {j['source']}\"")


# ----------------------------------------------------------------------------
# board, export, import
# ----------------------------------------------------------------------------

def board_payload(store: dict) -> list[dict]:
    keep = ("id", "title", "company", "url", "source", "location_raw", "remote_policy", "posted", "salary", "score",
            "reasons", "status", "notes", "next_action", "next_due", "applied_on", "first_seen", "last_seen", "tags")
    rows = []
    for j in store["jobs"]:
        row = {k: j.get(k, "") for k in keep}
        row["summary"] = (j.get("description") or "")[:600]
        rows.append(row)
    return rows


def write_board(store: dict) -> None:
    if not BOARD_PATH.exists():
        print("board.html missing; skipping board regeneration", file=sys.stderr)
        return
    html_text = BOARD_PATH.read_text(encoding="utf-8")
    payload = json.dumps({"generated": dt.datetime.now().isoformat(timespec="minutes"), "jobs": board_payload(store)},
                         ensure_ascii=False).replace("</", "<\\/")
    new = re.sub(r'(<script id="seed" type="application/json">).*?(</script>)', lambda m: m.group(1) + payload + m.group(2),
                 html_text, flags=re.S)
    BOARD_PATH.write_text(new, encoding="utf-8")


def cmd_board(args):
    write_board(load_jobs())
    print(f"Board regenerated -> {BOARD_PATH}")


def cmd_export(args):
    store = load_jobs()
    rows = board_payload(store)
    DATA_DIR.mkdir(exist_ok=True)
    with (DATA_DIR / "jobs.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["id"])
        w.writeheader()
        for r in rows:
            r = dict(r)
            r["reasons"] = "; ".join(r.get("reasons") or [])
            r["tags"] = ", ".join(str(t) for t in (r.get("tags") or []))
            w.writerow(r)
    (DATA_DIR / "board-export.json").write_text(json.dumps({"jobs": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {DATA_DIR / 'jobs.csv'} and {DATA_DIR / 'board-export.json'} ({len(rows)} jobs)")


def cmd_import(args):
    store = load_jobs()
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    rows = data.get("jobs", data if isinstance(data, list) else [])
    by_id = {j["id"]: j for j in store["jobs"]}
    n = 0
    for r in rows:
        if not r.get("id"):
            continue
        cur = by_id.get(r["id"])
        fields = ("status", "notes", "next_action", "next_due", "applied_on")
        if cur:
            for k in fields:
                if k in r:
                    cur[k] = r[k]
        else:
            r.setdefault("description", r.get("summary", ""))
            r.setdefault("reasons", [])
            r.setdefault("score", 0)
            store["jobs"].append(r)
            by_id[r["id"]] = r
        n += 1
    save_jobs(store)
    write_board(store)
    print(f"Imported {n} rows from {args.file}")


# ----------------------------------------------------------------------------

def main():
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search"); s.add_argument("--sources"); s.add_argument("--max-age", type=int); s.add_argument("--dry-run", action="store_true"); s.set_defaults(fn=cmd_search)
    s = sub.add_parser("links"); s.set_defaults(fn=cmd_links)
    s = sub.add_parser("list"); s.add_argument("--status", choices=STATUSES); s.add_argument("--min-score", type=int); s.add_argument("--all", action="store_true"); s.set_defaults(fn=cmd_list)
    s = sub.add_parser("show"); s.add_argument("id"); s.set_defaults(fn=cmd_show)
    s = sub.add_parser("set"); s.add_argument("id"); s.add_argument("status"); s.add_argument("--note"); s.add_argument("--next"); s.add_argument("--due"); s.set_defaults(fn=cmd_set)
    s = sub.add_parser("add"); s.add_argument("--title", required=True); s.add_argument("--company", required=True); s.add_argument("--url", required=True); s.add_argument("--location"); s.add_argument("--source"); s.add_argument("--description"); s.set_defaults(fn=cmd_add)
    s = sub.add_parser("prepare"); s.add_argument("id"); s.add_argument("--claude", action="store_true"); s.set_defaults(fn=cmd_prepare)
    s = sub.add_parser("board"); s.set_defaults(fn=cmd_board)
    s = sub.add_parser("export"); s.set_defaults(fn=cmd_export)
    s = sub.add_parser("import"); s.add_argument("file"); s.set_defaults(fn=cmd_import)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
