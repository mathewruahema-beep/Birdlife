# Estate registers

State of record for the Claude estate. Updated in the same commit as any estate
change. Last full audit: **2 September 2026** (live `list_triggers` pull from the
OS build session). AEST times assume UTC+10; the DST fix routine handles the
October shift.

## 1. Routine register

23 triggers live at audit. The 7 August consolidation (10 routines down to 4) has
been fully reversed by ad hoc creation since. Recurring active count is **17
against a budget of 12**.

### Healthy

| Routine | Trigger | Schedule (AEST) | Last run |
|---|---|---|---|
| Refund fix watch, daily blast radius scan | `trig_01VdzVKqN12nyemiu976mNca` | daily 8:15am | succeeded |
| Membership boards date sync (Build to Model) | `trig_01K4kh1m8foc2oYAv9Gs8xqo` | daily 7:30am | succeeded |
| ICT overnight pre-draft (approve-first) | `trig_01EbMkfD4UcGUKLkUB1mNQ8V` | weekdays 5:30am | pending at audit |
| Membership Build: Friday status update draft | `trig_01F7wy1pGcauqCsgUxVU4b47` | Fri 7am | not yet fired |
| ICT Weekly Status Update, Fridays 2pm | `trig_01AsdSGs9WiwRUrmbRmSxtAZ` | Fri 2pm (persistent session) | n/a |
| BirdLife Top 10 morning email draft | `trig_016BES4jwEodCfNdSTBYfSow` | weekdays 6am | pending at audit |
| Data feed and expiry monitor | `trig_01Q6X1Xr1syjg7U5QGNwDSUg` | daily 9am | succeeded |
| Onboarding detector, daily scan and approval pack | `trig_01HiCsJkKpSUqPxq2xUpAbEo` | daily 8:30am | succeeded |
| Offboarding detector, daily scan and approval pack | `trig_016nQBEZNDReT1DyrEbbqeSU` | daily 8am | succeeded |
| Stale case chaser (report-only) | `trig_01S3ShSb7KSBA32LxFWaLaNa` | Mon 8:30am | succeeded |

### One-shots (do not count against budget)

| Routine | Trigger | Fires |
|---|---|---|
| DST fix for dashboards and Morning brief | `trig_01YY3yjtTASm7MvUCh8ceW11` | 5 Oct 2026 |
| Renew entra-admin-mcp certificate | `trig_01Vp14cTKJCLnC7psjiRZnUC` | 25 Jul 2027 (cert expires 26 Aug 2027) |

### Dashboard sprawl group: 7 jobs where 2 would do

The exact failure mode removed on 7 August is back. On weekday mornings at 7am
AEST the dashboard is rebuilt by **three jobs inside five minutes** (daily
refresh at 7:00, hourly monitor at 7:00 in the same minute, morning hourly at
7:04), then twice more at 8am and 9am, then hourly all day.

| Routine | Trigger | Schedule (AEST) | Last run |
|---|---|---|---|
| ICT dashboard, daily refresh and Teams push | `trig_01QKqXyfwVoUwejxBbe15gX9` | weekdays 7am | pending at audit |
| ICT hourly monitor | `trig_015SYdBtkDn7jt8dz6MdvXyE` | weekdays 7, 8, 9am | succeeded |
| Dashboards, weekday mornings hourly + department suite | `trig_01HhAKnEe6PXAvo6EEq72BHo` | weekdays 7:04 to 9:04am | pending at audit |
| Dashboards hourly, weekday daytime | `trig_01Egd8XCKdBErqNPYnFkgTJB` | weekdays 10:04am to 5:04pm | pending at audit |
| Dashboards, weekend 7am | `trig_01CUkTdAFSisnzyU6pwgkH4k` | Sat, Sun 7:04am | **abandoned** |
| Dashboards, weekend 6pm | `trig_01HaRnkdKPD8Fu2HWMn616Nm` | Sat, Sun 6:04pm | **abandoned** |
| Security dashboard, weekly Monday | `trig_014DUzUYB3RwZSpvRTjokFFd` | Mon 12am | **abandoned** |

**Proposed target (Mathew to approve):** one weekday dashboard routine (hourly
cron, prompt runs the full 7am suite on the first fire of the day and a light
refresh otherwise), one weekend routine (daily, absorbing the security dashboard
on its Monday-adjacent run or keeping security as its own weekly job if the
prompt is too different). Retire the other five with backups to `routines/`.
The three abandoned jobs also need their last run sessions read before retiring,
so we know whether abandonment was connectors, permissions or prompt.

### Paused since mid-August: decide, do not drift

All four show not enabled with stale next-fire dates. OS rule: paused more than
two weeks means retire with backup, or fix and resume.

| Routine | Trigger | Was scheduled (AEST) | Recommendation |
|---|---|---|---|
| Zeus triage and first-touch drafter, hourly | `trig_01EpSqssk6qvoFRg2UNoEH5o` | hourly business hours | **Retire.** Overlaps the live overnight pre-draft |
| Meeting actions collector | `trig_014XfhCxMe3nwBgAeGAACp8B` | weekdays 4:30pm | Fix and resume, or retire |
| Unreconciled income exception report | `trig_01QC85zSvXoEWHTEzkip9ajp` | weekdays 7:30am | Decide with the Zapier version (see birdlife-zapier skill) |
| Identity lifecycle pack-to-plan | `trig_01FXchh6R9btpstDt6fSaLsM` | daily 9:10am | Decide against onboarding and offboarding detectors, which look like its replacements |

### Stale references fixed by this audit

- `trig_0126KYAM3TAaZpBQKN8UeVdk` (the 7 August consolidated dashboard routine,
  named in README.md and docs/using-the-assistant.md) no longer exists. The
  current weekday dashboard job is `trig_01QKqXyfwVoUwejxBbe15gX9`.
- `routines/overnight-pre-draft.md` said "not yet live". It is live as
  `trig_01EbMkfD4UcGUKLkUB1mNQ8V`. Header updated.

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
| email-voice | Mathew's email voice | **no, account only** | yes |
| morning | Morning brief | no, account only | yes |

Account-only skills are unversioned: if the account loses them, they are gone.
`email-voice` is load-bearing (the overnight pre-draft depends on it) and should
be committed into `.claude/skills/` at the next opportunity.

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
| ICT dashboard | https://claude.ai/code/artifact/3aa92e1f-c8d7-4a91-95ad-c6dcd5db7606 | Dashboard routines (see sprawl group above) |
| ICT Console | https://claude.ai/code/artifact/29a063d4-20c6-4793-bee5-d9916b40c84e | Sessions, on request ("update the console") |

Both are private artifact URLs. Do not publish either via GitHub Pages or any
public host; they name internal systems.

## 5. Credential watchlist

| Item | Status | Action |
|---|---|---|
| WooCommerce API keys exposed in deleted routine prompts (Aug 2026) | Rotation was flagged, **not verified done** | Confirm rotation with Mathew; until confirmed, treat as open |
| entra-admin-mcp certificate | Expires 26 Aug 2027 | Renewal reminder routine live (`trig_01Vp14cTKJCLnC7psjiRZnUC`) |
| Zapier connected app credentials (17 apps) | In Zapier vault | Reviewed in monthly OS review |
