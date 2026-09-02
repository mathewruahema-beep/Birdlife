# Estate registers

State of record for the Claude estate. Updated in the same commit as any estate
change. Last full audit: **2 September 2026** (live `list_triggers` pull from the
OS build session). AEST times assume UTC+10; the DST fix routine handles the
October shift.

## 1. Routine register

Consolidation executed 2 Sep 2026 with Mathew's approval: 23 triggers reduced
to 15 (13 recurring active + 2 one-shots). Nine routines retired with full
definitions backed up in `routines/routines-backup-2026-09-02.json`; two updated
in place as merge survivors; one created (the weekly audit).

**Budget note, decision open:** the budget is 12 recurring active routines and
the estate now sits at 13, because the audit routine itself took the 13th slot.
Nearest consolidation candidates: the two Friday status drafts (Membership Build
Friday draft and ICT Weekly Status Update) could merge, or the Top 10 morning
email draft could absorb the overnight pre-draft's reporting. Mathew to pick one
or raise the budget to 13.

### Active recurring (13)

| Routine | Trigger | Schedule (AEST) | Notes |
|---|---|---|---|
| ICT weekday dashboards and monitor (single job) | `trig_01HhAKnEe6PXAvo6EEq72BHo` | hourly 7:04am to 5:04pm weekdays | Merge survivor. 7am deep slot: Ops dashboard + Teams push + heartbeat + monitor sweep + department suite. Other slots light. Fires on Melbourne weekends too (cron cannot span the UTC midnight boundary) and exits immediately via a weekend gate; those no-op fires are expected |
| Dashboards weekend + weekly security (single job) | `trig_01CUkTdAFSisnzyU6pwgkH4k` | Sat, Sun 7:04am | Merge survivor. Sunday fire also refreshes the Security Dashboard (moved from Monday 12am) |
| Claude OS weekly audit | `trig_01V3i4b5zekjZuuFTF6Ymu9G` | Mon 6am | Created 2 Sep. Observe-and-record only; needs no connectors (repo and trigger list come from the environment) |
| ICT overnight pre-draft (approve-first) | `trig_01EbMkfD4UcGUKLkUB1mNQ8V` | weekdays 5:30am | Write-capable, capped: internal comments only, max 8 |
| BirdLife Top 10 morning email draft | `trig_016BES4jwEodCfNdSTBYfSow` | weekdays 6am | |
| Refund fix watch, daily blast radius scan | `trig_01VdzVKqN12nyemiu976mNca` | daily 8:15am | |
| Membership boards date sync (Build to Model) | `trig_01K4kh1m8foc2oYAv9Gs8xqo` | daily 7:30am | |
| Offboarding detector, daily scan and approval pack | `trig_016nQBEZNDReT1DyrEbbqeSU` | daily 8am | |
| Onboarding detector, daily scan and approval pack | `trig_01HiCsJkKpSUqPxq2xUpAbEo` | daily 8:30am | |
| Data feed and expiry monitor | `trig_01Q6X1Xr1syjg7U5QGNwDSUg` | daily 9am | |
| Stale case chaser (report-only) | `trig_01S3ShSb7KSBA32LxFWaLaNa` | Mon 8:30am | |
| Membership Build: Friday status update draft | `trig_01F7wy1pGcauqCsgUxVU4b47` | Fri 7am | Consolidation candidate (see budget note) |
| ICT Weekly Status Update, Fridays 2pm | `trig_01AsdSGs9WiwRUrmbRmSxtAZ` | Fri 2pm (persistent session) | Consolidation candidate (see budget note) |

### One-shots (do not count against budget)

| Routine | Trigger | Fires |
|---|---|---|
| DST fix for dashboards and Morning brief | `trig_01YY3yjtTASm7MvUCh8ceW11` | 5 Oct 2026. Scope changed by this consolidation: it must now adjust the merged weekday and weekend jobs and the audit routine, not the retired triggers |
| Renew entra-admin-mcp certificate | `trig_01Vp14cTKJCLnC7psjiRZnUC` | 25 Jul 2027 (cert expires 26 Aug 2027) |

### Retired 2 Sep 2026 (definitions in `routines/routines-backup-2026-09-02.json`)

| Routine | Trigger | Disposition |
|---|---|---|
| ICT dashboard, daily refresh and Teams push | `trig_01QKqXyfwVoUwejxBbe15gX9` | Absorbed into weekday job (deep slot: Teams push, heartbeat, fail-loudly email) |
| ICT hourly monitor 7-9am | `trig_015SYdBtkDn7jt8dz6MdvXyE` | Absorbed into weekday job (monitor checks, Teams post rules, monitoring Teams file) |
| Dashboards hourly, weekday daytime | `trig_01Egd8XCKdBErqNPYnFkgTJB` | Absorbed into weekday job (light slots) |
| Dashboards, weekend 6pm | `trig_01HaRnkdKPD8Fu2HWMn616Nm` | Dropped. Abandoned since 30 Aug and nobody noticed, which is the evidence it was not needed |
| Security dashboard, weekly Monday 12am | `trig_014DUzUYB3RwZSpvRTjokFFd` | Absorbed into weekend job, Sunday 7am fire |
| Zeus triage and first-touch drafter, hourly | `trig_01EpSqssk6qvoFRg2UNoEH5o` | Retired: duplicated the live overnight pre-draft |
| Meeting actions collector | `trig_014XfhCxMe3nwBgAeGAACp8B` | Retired on Mathew's call (paused since mid-Aug). Recreate from the backup if wanted later |
| Unreconciled income exception report | `trig_01QC85zSvXoEWHTEzkip9ajp` | Retired on Mathew's call. The Zapier-side version in the birdlife-zapier skill remains the candidate path |
| Identity lifecycle pack-to-plan | `trig_01FXchh6R9btpstDt6fSaLsM` | Retired: superseded by the onboarding and offboarding detectors |

### Follow-ups from the consolidation

- The three retired-or-absorbed jobs whose last runs were ABANDONED (security
  weekly, both weekend slots) were never diagnosed; the merged jobs inherit
  their duties, so the first weekend (5 to 7 Sep) is the verification window.
  If Saturday's run or Sunday's security refresh fails, diagnose the run
  session before anything else.
- First weekday deep slot for the merged job is Thursday 3 Sep 7:04am AEST
  (it previously had no 21:xx deep behaviour; watch the first heartbeat line).
- The 7am deep slot now does the work of three former sessions in one. If it
  starts timing out, the designed split point is moving the department suite
  (section 6 of its prompt) to its own daily routine; that is the one
  pre-approved exception to growing the count.

## 2. Skill register

Versioned in `.claude/skills/` here; mirrored to the claude.ai account so they
load without the repo. Repo copies are the source of truth; when they diverge,
re-sync the account from the repo unless the account copy is deliberately newer,
in which case commit it back first.

| Skill | Scope | Repo | Account |
|---|---|---|---|
| birdlife-ict-assistant | Core workflow, tiers, guardrails | yes | yes |
| birdlife-salesforce | Zeus org | yes | yes |
| birdlife-microsoft365 | Entra, M365 | yes | yes |
| birdlife-asana | IT Operations Project Plan | yes | yes |
| birdlife-netsuite | ERP | yes | yes |
| birdlife-wordpress | WP Engine estate | yes | yes |
| birdlife-stripe | Payments | yes | yes |
| birdlife-zapier | Automation | yes | yes |
| birdlife-cloudflare | DNS, edge | yes | yes |
| claude-os | This operating system | yes | sync it |
| email-voice | Mathew's email voice | yes (committed 2 Sep 2026) | yes |
| morning | Morning brief | no, account only | yes |

Account-only skills are unversioned: if the account loses them, they are gone.
`email-voice` was account-only and load-bearing (the overnight pre-draft depends
on it); it was copied verbatim into `.claude/skills/email-voice/` on 2 Sep 2026.
`morning` remains account-only; low stakes, commit when convenient.

## 3. Connector register

Attached at the claude.ai account level; routines additionally need connectors
attached to them individually (the organisation does not permit attaching
connectors via API, so this is a one-time UI step per routine).

Operational core: **Salesforce Production**, **Salesforce Staging**, **Asana**,
**Microsoft 365**, **NetSuite**, **Stripe**, **Zapier**, **Cloudflare** (two
accounts: Domain.admin `3bd8acff…`, Mathew.hema `9bff172b…`), **GitHub**,
**BirdLife UAT WordPress**. Also connected and available to sessions: Gmail,
Google Calendar, Google Drive, Canva, Miro, Zoom, Granola, Atlassian Rovo,
Microsoft Learn.

Rules: Salesforce Staging for anything experimental; Production writes follow
the charter (propose, then write). The Entra admin promotion plan is
`docs/entra-admin-connector.md`.

## 4. Artefact register

| Artefact | URL | Rebuilt by |
|---|---|---|
| ICT Operations dashboard | https://claude.ai/code/artifact/3aa92e1f-c8d7-4a91-95ad-c6dcd5db7606 | Weekday job (deep + light slots), weekend job |
| ICT Monitoring dashboard | https://claude.ai/code/artifact/7ebfafd0-f0be-44af-8ce6-f770ad5e9d6b | Weekday job (every slot), weekend job |
| Security dashboard (CONFIDENTIAL) | https://claude.ai/code/artifact/ff6c82e3-38d4-41de-b872-606521972498 | Weekend job, Sunday fire |
| Department suite (9 pages: fundraising, membership, finance, supporter care, marketing, conservation, people, volunteering, executive rollup) | artifact IDs listed in the weekday job's prompt, section 6 | Weekday job, deep slot |
| ICT Console | https://claude.ai/code/artifact/29a063d4-20c6-4793-bee5-d9916b40c84e | Sessions, on request ("update the console") |

Teams channel copies (SharePoint files, fixed names, never renamed):
BirdLife-ICT-Operations-Dashboard.html, BirdLife-ICT-Monitoring-Dashboard.html,
BirdLife-Security-Dashboard.html, plus the `_dashboard-run-log.txt` heartbeat.

All artifact URLs are private. Do not publish any via GitHub Pages or any
public host; they name internal systems.

## 5. Credential watchlist

| Item | Status | Action |
|---|---|---|
| WooCommerce API keys exposed in deleted routine prompts (Aug 2026) | Rotation was flagged, **not verified done** | Confirm rotation with Mathew; until confirmed, treat as open |
| entra-admin-mcp certificate | Expires 26 Aug 2027 | Renewal reminder routine live (`trig_01Vp14cTKJCLnC7psjiRZnUC`) |
| Zapier connected app credentials (17 apps) | In Zapier vault | Reviewed in monthly OS review |
