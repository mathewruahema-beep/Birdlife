# Remote IT role search tool

Personal job-search tooling for Mathew Hema. It finds remote senior IT roles that a
Melbourne-based worker can hold (Australia, New Zealand, APAC or worldwide eligibility,
AEST/AEDT hours) but that are **not** Melbourne office roles, scores each one against
the profile built from the resume, prepares an application pack per role, and keeps a
pipeline you can work from a board.

This directory is self-contained. It has nothing to do with the BirdLife assistant
that lives in the rest of this repository, and it should move to a private personal
repository before it grows. See "Things to decide" at the bottom.

## What is in here

| File | Purpose |
|---|---|
| `profile.json` | Your profile, derived from the resume: target titles, search queries, location policy, scoring weights, experience, highlights. Edit this to steer the search. No phone number is stored. |
| `jobsearch.py` | The command line tool. Pulls 12 sources, filters, scores, tracks, prepares packs, regenerates the board. |
| `board.html` | The kanban board. Open it locally (browser storage) or use the published copy (shared database, works on your phone). |
| `data/jobs.json` | The pipeline. Every role seen, its score, status, notes and next action. |
| `data/jobs.csv`, `data/board-export.json` | Produced by `export`. |
| `applications/<id>-<slug>/` | Application packs. Ignored by git by default because they contain tailored personal letters. |

## Setup

```
cd jobsearch
pip install -r requirements.txt
python jobsearch.py search
```

Python 3.10 or newer. Only `requests` is required. For AI-written packs also `pip install anthropic`
and set `ANTHROPIC_API_KEY` (or run `ant auth login`).

The job boards are blocked from the Claude remote sandbox by its egress policy, so
`search` has to run on your own machine. Everything else (board, packs, tracking) works anywhere.

## Daily loop

```
python jobsearch.py search                 # pull every source, score, merge, regenerate board
python jobsearch.py list --min-score 45    # what is worth a look
python jobsearch.py show <id>              # full record and posting text
python jobsearch.py prepare <id>           # cover letter, tailoring notes, screening answers
python jobsearch.py prepare <id> --claude  # same, written by Claude from the full posting
python jobsearch.py set <id> applied --note "Submitted via SEEK" --next "Chase in 7 days" --due 2026-09-10
python jobsearch.py links                  # one-click searches for boards with no API
```

Statuses: `sourced`, `shortlisted`, `applied`, `interviewing`, `offer`, `closed`.

`add` puts a role you found by hand into the pipeline:

```
python jobsearch.py add --title "Head of IT" --company "Acme" --url "https://..." --location "Remote, Australia" --source seek
```

## Sources

Pulled automatically by `search` (all free, no keys):

| Source | What it gives you |
|---|---|
| Remotive | Remote roles with a stated candidate location, searched per query in `profile.json` |
| Himalayas | Remote roles with country and time zone restrictions |
| Jobicy | Remote roles filtered by geo: `australia`, `apac`, `anywhere` |
| Arbeitnow | Remote flag on each posting, mostly European employers hiring worldwide |
| RemoteOK | Remote roles with location text and salary |
| We Work Remotely | RSS feeds for devops/sysadmin, management, and other categories, with region |
| Working Nomads | Remote roles with location and category |
| Greenhouse boards | Company career sites on Greenhouse, listed in `profile.json`, remote-filtered |
| Lever boards | Same for Lever |
| Ashby boards | Same for Ashby |

Enabled with a free key in the environment:

| Source | Key |
|---|---|
| Adzuna (AU and NZ aggregator, covers SEEK/Indeed style postings) | `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` from developer.adzuna.com |
| Jooble (AU aggregator) | `JOOBLE_API_KEY` from jooble.org/api/about |

No public API, so `links` prints ready-made searches for them: SEEK AU and NZ, LinkedIn,
Indeed AU, EthicalJobs, Jora, Glassdoor, Remote Rocketship, Jobgether, Dynamite Jobs,
InfoSec Job Board, Wellfound, Hays, Robert Half, Talent.com, NotFor-Profit People,
Pro Bono Australia, and the fractional CIO networks.

Add more Greenhouse, Lever or Ashby company boards by putting the board token in
`profile.json` under `sources`. The token is the last path segment of the company's
careers URL (for example `job-boards.greenhouse.io/remotecom` gives `remotecom`).

## How filtering works

1. **Location policy** (`profile.json` -> `location_policy`). A posting is dropped when its
   location text matches an exclude rule (Melbourne, Victoria, on-site, hybrid, "US only" and
   similar) or when its description states a residency requirement outside Australia. It is
   kept as `explicit_apac_or_au` when it names Australia, NZ, APAC, Asia, or a UTC+8 to +12 zone,
   `worldwide` when it says anywhere or global, and `unrestricted` when it is a remote posting
   with no stated restriction. Unrestricted roles are kept but scored lower because half of them
   turn out to be US-only once you read the fine print.
2. **Score** (0 to 100). Best title match (Head of IT, CIO, IT Manager and so on), seniority
   words, skill keywords found in the posting (Essential Eight, ISO 27001, Microsoft 365,
   Salesforce, NetSuite, ITIL, vendor management, not-for-profit and the rest), remote policy
   confidence, minus junior or non-IT signals and staleness. Roles under 20 are not stored.
   The shortlist threshold is 45. Every score comes with its reasons; `show <id>` prints them.
3. **Age**. Postings older than 45 days are ignored (`--max-age` or `sources.max_age_days`).

Tune the weights in `profile.json`. If the tool keeps surfacing the wrong kind of role,
change the numbers rather than the code.

## Application packs

`prepare <id>` writes four files: `cover-letter.md`, `tailoring-notes.md`,
`screening-answers.md` and `job.md` (the posting text as fetched). The template version
picks the three highlights and three roles from your profile that best match the posting's
keywords. The `--claude` version sends the full profile and posting to Claude and gets the
three documents written for that employer, with a rule that it may only use facts in the
profile. Read every pack before sending it. The tool never submits an application.

## The board

Two copies of the same page:

- **Local**: `board.html`. Regenerated by `search`, `set`, `add`, `prepare` and `board` with the
  current pipeline embedded. State you change in the browser is kept in that browser's storage.
  Export JSON from the board and run `python jobsearch.py import data/board-export.json` to pull
  those changes back into `data/jobs.json`.
- **Published**: the claude.ai artifact linked in the session that built this. It uses a shared
  database, so changes made on the phone show up on the laptop and future Claude sessions can read
  and update it. Paste the output of `export` into its Import dialog after each `search` run.

Columns are the six statuses. Drag cards or use the arrows. Click a card to edit notes, next
action and due date. The header shows active roles, applications this week, interviews, offers,
and anything due today or overdue.

## Things to decide

- **Move this out of the BirdLife repository.** It is your personal job search sitting in the
  repository that runs your employer's ICT assistant. Anyone you give repository access to
  sees it. A private `mathewruahema-beep/jobsearch` repository is the right home; copy this
  directory across and delete it here.
- **Auto-apply is deliberately not built.** Bulk automated submissions through LinkedIn Easy
  Apply, SEEK or ATS forms are against those platforms' terms, are detected and shadow-banned,
  and produce low-quality applications for senior roles where the hiring manager reads every
  letter. The tool gets you from "found" to "pack ready, link open" in one command; the submit
  step stays with you.
- **The honest market read.** True "work from anywhere" roles at Head of IT or CIO level from
  overseas employers are rare and mostly US-hours. The realistic volume is: Australian employers
  outside Melbourne with remote policies (Sydney, Brisbane, Canberra, Perth), New Zealand
  employers, APAC regional roles at multinationals, and fractional or interim CIO work. The
  location policy and the `links` list are built around that. Expect most good matches to come
  from SEEK, LinkedIn, EthicalJobs and Adzuna rather than the global remote boards.
