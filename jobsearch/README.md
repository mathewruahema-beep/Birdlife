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
| `jobsearch.py` | The command line tool. Pulls 22 sources, filters, scores, tracks, prepares packs, regenerates the board. |
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

`search` pulls all of these. Every source is isolated: one failing does not stop the rest,
and the source report at the end of each run tells you what worked.

Free, no key, on by default:

| Source | What it gives you |
|---|---|
| Remotive | Remote roles with a stated candidate location, searched per query |
| Himalayas | Remote roles with country and time zone restrictions (8 pages) |
| Jobicy | Remote roles by geo: `australia`, `apac`, `anywhere` |
| Arbeitnow | Remote-flagged postings, mostly European employers hiring worldwide |
| RemoteOK | Remote roles with location text and salary |
| We Work Remotely | RSS for devops/sysadmin, management, and other categories, with region |
| Working Nomads | Remote roles with location and category |
| The Muse | Remote-flex roles in IT, management and project management |
| Jobspresso | Curated remote board, RSS feed |
| Hacker News "Who is hiring" | Latest monthly thread, remote comments only |
| Greenhouse boards | 49 company career sites (GitLab, Remote, Canonical, Deel, PagerDuty, SafetyCulture, Culture Amp, Employment Hero, Octopus Deploy, Zapier, Automattic, Cloudflare, Elastic, HashiCorp, MongoDB, Datadog, Twilio, Okta, Grafana, Postman, Dovetail, Go1, Rokt, Envato, Immutable, Deputy, Airwallex, Atlassian, Xero, Linktree, SiteMinder, Nearmap, security vendors and more), remote-filtered |
| Lever boards | 13 company sites (Canva, 1Password, Doist, Atlassian, Brighte, Pushpay, Mable and more) |
| Ashby boards | 9 company sites (Linktree, Deel, Remote, Dovetail, Clipchamp, Secure Code Warrior and more) |
| Workable boards | 5 company sites (UpGuard, Whispir, Bigtincan, Brighte, Mable) |
| SmartRecruiters boards | Visa, Bosch, Ubisoft as examples; add your own |
| Recruitee and BambooHR boards | Supported, empty by default; add company slugs |

Some of the board tokens are educated guesses. A wrong token fails for that company only
and is printed in the run log. Prune the noise after your first run and add the companies
you care about: the token is the last path segment of the company's careers URL.

Free key in the environment:

| Source | Key |
|---|---|
| Adzuna (AU and NZ aggregator, indexes most Australian postings) | `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` from developer.adzuna.com |
| Jooble (AU aggregator) | `JOOBLE_API_KEY` from jooble.org/api/about |
| Findwork (remote tech board) | `FINDWORK_TOKEN` from findwork.dev/developers |

Experimental, off by default. SEEK and LinkedIn have no public job-search API. The tool
can read the undocumented endpoints their own websites use (`seek` and `linkedin` sources),
at low volume, when you set `EXPERIMENTAL_BOARDS=1`. Both sites' terms of use prohibit
automated access, the endpoints change without notice, and LinkedIn rate-limits guest
requests hard. It is your decision. Without the flag they are reported as skipped and the
`links` command gives you the same searches to run by hand in one click.

`links` prints 81 ready-made searches for boards with no API: SEEK AU and NZ, LinkedIn,
Indeed AU, EthicalJobs, Jora, Glassdoor, CareerOne, Adzuna, ACS jobs, APS Jobs, TradeMe,
Remote.co, NoDesk, FlexJobs, Welcome to the Jungle, Built In, PowerToFly, Remote Rocketship,
Jobgether, Dynamite Jobs, InfoSec Job Board, Wellfound, the fractional CIO networks, Toptal,
and the Australian IT recruiters (Hays, Robert Half, Peoplebank, Paxus, Talent International,
Michael Page, Hudson).

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
  current pipeline and your profile embedded. State you change in the browser is kept in that
  browser's storage. Export JSON from the board and run
  `python jobsearch.py import data/board-export.json` to pull those changes back into `data/jobs.json`.
- **Published**: the claude.ai artifact linked in the session that built this. It uses a shared
  database, so changes made on the phone show up on the laptop and future Claude sessions can read
  and update it. It also has the two abilities the local copy cannot: Claude writes the application
  in the page, and Gmail drafts are created from it. Paste the output of `export` into its Import
  dialog after each `search` run.

Columns are the six statuses. Drag cards or use the arrows. Click a card to edit notes, next
action, due date and the posting text. **Re-score from posting** in that dialog runs the same
location policy and scoring as the command line, so roles you add on the phone get a real score.

### Applying from the board

**Apply** on a card opens the application workspace:

1. Paste the full posting text (left side). Set how you will apply and the contact email if
   there is one.
2. **Write with Claude** produces the cover letter, screening answers and resume tailoring notes
   from your profile and that posting, in the page, under a rule that it may only use facts in
   the profile. **Use template** does the same from fixed text without AI. Edit in place; every
   tab has a Copy button. The pack is saved on the card so it is there on any device.
3. **Draft in Gmail** creates a draft in your Gmail addressed to the contact, subject
   "Application: {title} - Mathew Hema", body the cover letter. You attach the tailored resume
   and send from Gmail. Nothing is sent by the page.
4. **Open posting and mark applied** opens the job in a new tab for board or ATS applications
   and moves the card to Applied with a follow-up due in seven days. **Mark applied** does the
   same without opening the link.
5. The checklist (eligibility confirmed, letter reviewed, resume tailored, answers ready,
   submitted, follow-up set) is saved per role and shown on the card as `pack n/6`.

Claude writing and Gmail drafting spend your own claude.ai usage and use your own Gmail
connector; the page asks for consent on first use. The header dots show which of the three
abilities (shared database, Claude writing, Gmail drafts) are live in the copy you have open.

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
