# Estate registers

State of record for the Claude estate. Updated in the same commit as any estate
change. Last full audit: **3 September 2026, 22:04 AEST** (unused-routines review, live
`list_triggers` pull; findings in `routines/unused-routines-review-2026-09-03.md`). AEST times assume UTC+10; the DST fix routine handles the
October shift.

## 1. Routine register

Consolidation executed 2 Sep 2026 with Mathew's approval: 23 triggers reduced
to 15 (13 recurring active + 2 one-shots). Nine routines retired with full
definitions backed up in `routines/routines-backup-2026-09-02.json`; two updated
in place as merge survivors; one created (the weekly audit).

**Budget: 11 of 12 as at 3 Sep 2026 (evening).** Mathew retired the Top 10 morning
email draft in the morning (backup `routines/routines-backup-2026-09-03.json`), then
after the evening review retired the weekend dashboards job and the Friday weekly
status update (backup `routines/routines-backup-2026-09-03b.json`). AI Daily Ten was
created the same day outside the register and is now registered below.

### Active recurring (11)

| Routine | Trigger | Schedule (AEST) | Notes |
|---|---|---|---|
| ICT weekday dashboards and monitor (single job) | `trig_01HhAKnEe6PXAvo6EEq72BHo` | hourly 7:04am to 5:04pm weekdays | Merge survivor. FIXED 3 Sep: website probes moved from the Zapier webhook action (held for approval in unattended runs, stalled every slot) to WebFetch; the Zapier Teams post is now the last connector call so a held approval cannot take the SharePoint push or heartbeat down. Heartbeat log had been silent since 25 Aug; first verified heartbeat is the test. 7am deep slot: Ops dashboard + Teams push + heartbeat + monitor sweep + department suite. Other slots light. Fires on Melbourne weekends too (cron cannot span the UTC midnight boundary) and exits immediately via a weekend gate; those no-op fires are expected |
| Claude OS weekly audit | `trig_01V3i4b5zekjZuuFTF6Ymu9G` | Mon 6am | Created 2 Sep. Observe-and-record only; needs no connectors (repo and trigger list come from the environment) |
| ICT overnight pre-draft (approve-first) | `trig_01EbMkfD4UcGUKLkUB1mNQ8V` | weekdays 5:30am | Write-capable, capped: internal comments only, max 8. FIXED 3 Sep: the Salesforce create is held for approval in unattended runs (zero autonomous drafts 24 Aug to 2 Sep); prompt now prints the full draft pack as text before attempting writes, and the retired console snapshot step was removed. Push notification still off (cannot be set via API); pre-approving createSobjectRecord in the Routines UI restores full function |
| Refund fix watch, daily blast radius scan | `trig_01VdzVKqN12nyemiu976mNca` | daily 8:15am | |
| Membership boards date sync (Build to Model) | `trig_01K4kh1m8foc2oYAv9Gs8xqo` | daily 7:30am | |
| Offboarding detector, daily scan and approval pack | `trig_016nQBEZNDReT1DyrEbbqeSU` | daily 8am | |
| Onboarding detector, daily scan and approval pack | `trig_01HiCsJkKpSUqPxq2xUpAbEo` | daily 8:30am | |
| Data feed and expiry monitor | `trig_01Q6X1Xr1syjg7U5QGNwDSUg` | daily 9am | |
| Stale case chaser (report-only) | `trig_01S3ShSb7KSBA32LxFWaLaNa` | Mon 8:30am | |
| Membership Build delivery briefing | `trig_01F7wy1pGcauqCsgUxVU4b47` | Mon, Wed, Fri 7:08am | Extended 3 Sep from Friday-only to Mon/Wed/Fri; Friday adds the status update draft. Read-only |
| AI Daily Ten (Gmail newsletters into the AI Field Guide) | `trig_01Y69zEQwQtn4HcGw9Esz8ua` | weekdays 6:34am | Created 3 Sep outside the register. Read-only on Gmail, republishes artifact 3dd8818e. Gmail must be attached in the Routines UI before its first fire or it stops and reports that |

### One-shots (do not count against budget)

| Routine | Trigger | Fires |
|---|---|---|
| DST fix: shift every recurring routine one hour | `trig_01YY3yjtTASm7MvUCh8ceW11` | 5 Oct 2026 2pm. Prompt rewritten 3 Sep against the current 11 recurring routines (it previously named six retired triggers and the weekday job's old cron, so it would have skipped the main job) |
| Renew entra-admin-mcp certificate | `trig_01Vp14cTKJCLnC7psjiRZnUC` | 25 Jul 2027 (cert expires 26 Aug 2027) |

### Retired 3 Sep 2026, evening (definitions in `routines/routines-backup-2026-09-03b.json`)

| Routine | Trigger | Disposition |
|---|---|---|
| Dashboards weekend + weekly security (single job) | `trig_01CUkTdAFSisnzyU6pwgkH4k` | Retired on Mathew's call after the unused-routines review: its 29 Aug fire stalled 4.5 days and produced nothing. Consequence accepted: no dashboard refresh on Melbourne weekends, and the Security dashboard no longer refreshes automatically (last automated refresh was the Monday 12am routine before 2 Sep). Refresh it from a session on request |
| ICT Weekly Status Update, Fridays 2pm | `trig_01AsdSGs9WiwRUrmbRmSxtAZ` | Retired on Mathew's call. Was bound to persistent session `session_01TQc6wyBqPMpdFhA9bMNw1m` (506k context tokens used, 44.55 USD). The session still exists and can be archived; the report can be produced on request from the console's report library |

### Retired 3 Sep 2026, morning (definition in `routines/routines-backup-2026-09-03.json`)

| Routine | Trigger | Disposition |
|---|---|---|
| BirdLife Top 10 morning email draft | `trig_016BES4jwEodCfNdSTBYfSow` | Retired on Mathew's call: overlapped the console's Catch me up. Closed the budget decision at 12 of 12. Its prompt still carried the Owner.Name scoping bug |

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

### Findings of the 3 Sep evening review (unused routines)

- Three routines were firing but idle because a connector write was held for
  approval in an unattended auto-mode session: the weekday dashboards job
  (Zapier website probe, every slot, heartbeat silent since 25 Aug), the
  overnight pre-draft (Salesforce create, zero drafts 24 Aug to 2 Sep) and the
  weekend job (blocker no longer visible). Two were fixed by prompt, one retired.
- The Routines UI is the only place a tool can be pre-approved for a routine or a
  push notification toggled; the API cannot. Mathew's UI list: pre-approve the
  Zapier action on the weekday job and createSobjectRecord on the pre-draft, turn
  the pre-draft's push notification on, attach Gmail to AI Daily Ten.
- Verification for the weekday fix: the heartbeat line dated 4 Sep 07:xx AEST in
  `_dashboard-run-log.txt` on SharePoint. If it is missing, read the 21:04 UTC
  run session before anything else.
- The `os/` directory was merged to the default branch on 3 Sep so the weekly
  audit can find this register. Before that, every fresh session started without it.

### Follow-ups from the consolidation

- (Closed 3 Sep) The weekend verification window no longer applies; the weekend
  job was retired before it ran again.
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
| birdlife-os | This operating system and the console | yes | re-upload (3 Sep) |
| birdlife-security | Posture, deadlines, incidents (CONFIDENTIAL) | yes (created 3 Sep 2026) | upload |
| birdlife-people-lifecycle | Joiner/mover/leaver | yes (created 3 Sep 2026) | upload |
| birdlife-reporting | Report library and data discipline | yes (created 3 Sep 2026) | upload |
| birdlife-improvement | Process observation, fixes, learning loop | yes (created 3 Sep 2026) | upload |
| email-voice | Mathew's email voice | yes (committed 2 Sep 2026) | re-upload (3 Sep) |
| morning | Morning brief | no, account only | yes |

**Expert pass, 3 Sep 2026:** every repo skill was extended with observed
connector behaviour and runbooks (Salesforce query set and Staging connector;
Asana section semantics and API shapes; M365 connector facts; NetSuite SuiteQL
cookbook; Stripe five-account map and reconciliation playbook; Cloudflare
SPF/DMARC runbook; Zapier exception-report publish runbook; WordPress UAT
connector, which has write abilities; email-voice report register). All
account copies are therefore stale until re-uploaded from the zips sent on
3 Sep; until then the repo copies are the only expert versions.

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
| ICT Operations dashboard | https://claude.ai/code/artifact/3aa92e1f-c8d7-4a91-95ad-c6dcd5db7606 | Weekday job (deep + light slots); no weekend refresh since 3 Sep |
| ICT Monitoring dashboard | https://claude.ai/code/artifact/7ebfafd0-f0be-44af-8ce6-f770ad5e9d6b | Weekday job (every slot); no weekend refresh since 3 Sep |
| Security dashboard (CONFIDENTIAL) | https://claude.ai/code/artifact/ff6c82e3-38d4-41de-b872-606521972498 | No automated refresh since 3 Sep (weekend job retired); sessions on request |
| Department suite (9 pages: fundraising, membership, finance, supporter care, marketing, conservation, people, volunteering, executive rollup) | artifact IDs listed in the weekday job's prompt, section 6 | Weekday job, deep slot |
| ICT Console | https://claude.ai/code/artifact/29a063d4-20c6-4793-bee5-d9916b40c84e | Sessions, on request ("update the console") |
| Claude OS console with Jarvis | https://claude.ai/code/artifact/2a9b7e57-dbc5-49e3-a4d7-c0a36bd236b2 | Sessions, on request; source at `os/claude-os-overview.html`. Daily console: live Today tab (queue, board attention, Outlook inbox filtered to people, latest Teams messages) plus a Board tab by section, via the viewer's "Salesforce Production", "Asana" and "Microsoft 365" connectors. Jarvis HUD assistant (sample capability, viewer's own Claude usage). Write surface, each behind an in-page Approve card: Case internal note, public reply, close with reason, assign to the ICT team only (duplicate User records resolved live by recent Zeus case ownership, ambiguous matches always put to the user) (`createSobjectRecord`/`updateSobjectRecord`, verified by re-read); Asana comment, complete, move section (`add_comment`/`update_tasks`); Outlook reply DRAFT only, never send (`outlook_create_reply_draft`). Teams is read-only (no send API); replies are drafted to copy. Reads via `soqlQuery`/`search_tasks`/`outlook_email_search`/`chat_message_search`/`teams_list_chats`, plus (added 3 Sep) "Stripe" `stripe_api_read` (GetBalance across the five livemode accounts, READ ONLY — `stripe_api_write` is never declared) and "NetSuite" `ns_runCustomSuiteQL` for the Money tab, and live SF User queries for the Security tab (CONFIDENTIAL content). Jarvis carries `money_snapshot` and `security_snapshot` tools and a report library (weekly ICT status, money state, security posture, exec brief). Fixes tab (added 3 Sep): seeded catalogue of technical and process fixes plus Jarvis live suggestions (`fixes_catalog`, `fix_propose`, `fix_status`); `fix_track` creates one Asana task per approval via `create_tasks` (added to the Asana surface), verified by re-read. No bulk actions, no reassignment, no email sending from the page. Update this row and the page when the registers change materially |

Teams channel copies (SharePoint files, fixed names, never renamed):
BirdLife-ICT-Operations-Dashboard.html, BirdLife-ICT-Monitoring-Dashboard.html,
BirdLife-Security-Dashboard.html, plus the `_dashboard-run-log.txt` heartbeat.

All artifact URLs are private. Do not publish any via GitHub Pages or any
public host; they name internal systems.

**Cleanup review, 3 Sep 2026 (Mathew's conditions applied):** the department
suite and the ICT Operations/Monitoring dashboards were reviewed for retirement
conditional on the console covering their content. It does not: the suite carries
department metrics (Salesforce/Stripe/NetSuite) absent from the console, and the
Ops/Monitoring Teams files are the team's shared view while the console is
private to Mathew. Both therefore KEPT. To retire them later: either accept the
loss, or share the console with the team (each viewer needs their own connector
grants) and fold the missing checks in. Security dashboard kept (governance).

## 5. Credential watchlist

| Item | Status | Action |
|---|---|---|
| WooCommerce API keys exposed in deleted routine prompts (Aug 2026) | Rotation was flagged, **not verified done** | Confirm rotation with Mathew; until confirmed, treat as open |
| entra-admin-mcp certificate | Expires 26 Aug 2027 | Renewal reminder routine live (`trig_01Vp14cTKJCLnC7psjiRZnUC`) |
| Zapier connected app credentials (17 apps) | In Zapier vault | Reviewed in monthly OS review |
| miniOrange SF→WP webhook access keys (prod `7cf2…`, staging `8d8f…`) | Leaked in plaintext in three documents; rotation **not verified** | Regenerate Access Key in both envs, scrub the documents, confirm here |
| LearnUpon → Zapier catch-hook URL | In plaintext in documentation; owned by Keith's Zapier account | Confirm purpose with Keith, rotate, scrub, re-own |
| Raisely access token in `Contact.Raisely_Access_Token__c` formula URL | By design, sensitive | Field-level security review; never export in reports |
| NetSuite OAuth2 certificate `7SCEnbQf…` (linked to departed staff) | Expires 17 Sep 2026, zero activity | Revoke, monitor, delete (CFO briefed 20 Jul, no action yet) |
| Vevox SAML certificates | Dashboard 21 Aug 2026 (passed), Vevox 8 Sep 2026 | Verify SSO still works; renew before 8 Sep |
| Employment Hero sync Graph secret | Expires 5 Jan 2027 | Rotate when the Logic App is unblocked; add a reminder routine |
| Salesforce test accounts `test101`, `test123` | Active with real credentials | Disable |
