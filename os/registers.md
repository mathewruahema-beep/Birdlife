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

### Orphan check, 3 Sep 2026 (live `list_triggers` pull, 14 triggers)

- All 14 live triggers (12 recurring, 2 one-shots) are registered above; no
  unregistered routine, no ghost row. Nothing to delete.
- ICT overnight pre-draft `trig_01EbMkfD4UcGUKLkUB1mNQ8V`: last run ABANDONED
  3 Sep 5:32am AEST. Its step 5 still targets the retired case-workbench
  console (branch `claude/ai-ict-assistant-birdlife-1sqen8`, `console/index.html`,
  artifact `29a063d4`, now a tombstone) and republishes via the Artifact tool,
  which routine sessions do not have (see artefact finding below). Fix
  proposed: `update_trigger` to drop step 5 entirely (the live Today tab in the
  Claude OS console replaced the baked snapshot) and turn failure notifications
  on (currently push, email and slack all false, against the 12 Aug rule).
- Weekend job `trig_01CUkTdAFSisnzyU6pwgkH4k`: last run ABANDONED 29 Aug,
  before the 2 Sep rewrite; unproven until the 5 to 7 Sep verification window.
- OS weekly audit, Membership Friday draft and ICT Weekly Status have never
  fired yet (created 2 Sep); first fires are 4 Sep and 7 Sep.

## 2. Skill register

Versioned in `.claude/skills/` here; mirrored to the claude.ai account so they
load without the repo. **The repo is the source of truth only once the account
content has been committed.** On 11 Sep 2026 the account was found AHEAD of the
repo: eight skills existed on the account only and three account copies were
newer than the repo (security, wordpress, ict-assistant, plus os with the lens
model). All were pulled into the repo that day (commit on
`claude/birdlife-brain-build-02zobt`). Until the two-brains decision is made,
every audit compares the live account list against this table.

| Skill | Scope | Repo | Account (11 Sep 2026) |
|---|---|---|---|
| birdlife-ict-assistant | Core workflow, tiers, guardrails, Zeus-group assignment rule | yes | yes, pulled 11 Sep (newer: Zeus group rule of 4 Sep) |
| birdlife-salesforce | Zeus org | yes | yes, stale (lacks facts file) |
| birdlife-microsoft365 | Entra, M365 | yes | yes, stale (lacks facts file) |
| birdlife-asana | IT Operations Project Plan | yes | yes, stale (lacks facts file) |
| birdlife-netsuite | ERP | yes | yes, stale (lacks facts file) |
| birdlife-wordpress | WP Engine estate, theme developer handbook | yes | yes, pulled 11 Sep (rewrite, live read 11 Sep) |
| birdlife-wpengine | WP Engine account, portal, caching, Web Rules | yes (pulled 11 Sep) | yes |
| birdlife-stripe | Payments | yes | yes, stale (lacks facts file) |
| birdlife-zapier | Automation | yes | yes, stale (lacks facts file) |
| birdlife-cloudflare | DNS, edge | yes | yes, stale (lacks facts file) |
| google-workspace-expert | Google Workspace tenant C01muaswh | yes (pulled 11 Sep) | yes |
| birdlife-payments2us | Payments2Us deep dive | yes (pulled 11 Sep) | yes |
| birdlife-conga | Conga receipting estate | yes (pulled 11 Sep) | yes |
| birdlife-sdocs | S-Docs and S-Sign | yes (pulled 11 Sep) | yes |
| birdlife-movedata | MoveData / Raisely pipeline | yes (pulled 11 Sep) | yes |
| birdlife-powerbi | Power BI and Fabric | yes (pulled 11 Sep) | yes |
| birdlife-os | This operating system, the console, the lens model | yes (merged 11 Sep: account lens model plus repo memory audit) | yes, stale (lacks memory audit steps) |
| birdlife-security | Posture, SC-300 baseline, deadlines, incidents (CONFIDENTIAL) | yes | yes, pulled 11 Sep (newer: SC-300 baseline, P1/P2, identity playbooks) |
| birdlife-people-lifecycle | Joiner/mover/leaver | yes | yes, identical |
| birdlife-reporting | Report library and data discipline | yes | yes, identical |
| birdlife-improvement | Process observation, fixes, learning loop | yes | **no** (never uploaded) |
| birdlife-prompting | Six-line prompt frame | yes (pulled 11 Sep) | yes |
| email-voice | Mathew's email voice | yes | yes, identical |
| morning | Personal morning brief | yes (pulled 11 Sep) | yes |
| birdlife-core | The doctrine: precedence, fact classes, tiers, ADR log 0001 to 0020, verification queries, six knowledge digests | yes (pulled 12 Sep from the Aug 2026 plugin in Google Drive) | **no** (was only ever in the plugin) |
| birdlife-manager | Weekly ICT manager review, learning log (IT-GOV-003) | yes (patch 0002 applied 12 Sep) | **no** (the 7 Sep note says saved; the live list does not show it) |
| birdlife-atlassian, birdlife-canva, birdlife-gmail, birdlife-google-calendar, birdlife-granola, birdlife-microsoft-learn, birdlife-miro | One small skill per connector (Aug 2026) | yes (pulled 12 Sep from the plugin) | no |

**Found and imported, 12 Sep 2026.** The missing rule set lived in Mathew's
personal Google Drive (`GoogleDrive/Claude`), not OneDrive: the August 2026
Cowork plugin `birdlife-ict.plugin` (birdlife-core with ADRs 0001 to 0016, the
verification queries, the fact classification and six knowledge digests, plus
nine connector skills), the `repo-inbox` with patches 0001 to 0003 and their
apply notes, IT-GOV-004 and IT-GOV-005, ADRs 0018 to 0020 and the Manager
folder. All committed on 12 Sep. Still cited and still not found: the
`salesforce-delivery-governance` skill, ADR 0017, IT-SEC-002/003/004/007,
IT-WEB-001 and IT-SF-018 as Markdown (IT-SF-018 exists in Drive as a 68 KB
Markdown reference and was not imported; it is the Payments2Us operator
reference behind `birdlife-payments2us`). Not imported by choice: the August
`birdlife-google-workspace` skill (superseded by `google-workspace-expert`),
`birdlife-spotify` (personal, no business function), and the
`birdlife-ict-brain-repo.tar.gz` snapshot of 11 Aug.

**Facts files, 11 Sep 2026:** the eight core system skills (salesforce, asana,
microsoft365, netsuite, wordpress, stripe, zapier, cloudflare) gained
`references/facts.md`, the structured lookup for IDs, URLs, counts and dates,
with the rule "facts file first, prose second" when a value changes.
`birdlife-ict-assistant` keeps `references/reference.md` in that role. Account
copies must be re-uploaded as zips that include `references/`.

Account-only skills are unversioned: if the account loses them, they are gone.
That is exactly what eight skills were until 11 Sep 2026. `email-voice` was
account-only and load-bearing (the overnight pre-draft depends on it); it was
copied verbatim into `.claude/skills/email-voice/` on 2 Sep 2026.

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
| The BirdLife Brain (VIKI-style map) | https://claude.ai/code/artifact/7c0faca1-812a-4ce2-8b0e-b9d501ef95d3 | Reads itself: nothing is baked in. Source at `os/birdlife-brain.html`, first published 12 Sep 2026, made live the same day. At every open the page reads the repository through the viewer's claude.ai "GitHub" connector (`get_file_contents`, READ ONLY, the only tool declared; the connector's GitHub App must have repository access to the private Birdlife repo, granted in GitHub Settings, Applications): CLAUDE.md (skill table), INDEX.md, `os/registers.md` (routine, connector and artefact registers), the `os/`, `.claude/skills/`, `memory/journal/`, `memory/patterns/` and decisions folders. Branch field defaults to the working branch `claude/birdlife-brain-build-02zobt`; change it to `main` once that branch exists. Refreshes every five minutes while open; Reload re-reads. Click a node to read the file's heading. No writes, no other connectors. Skill-to-system edges are a static map in the page (update when a skill starts reading a new system); routine edges are keyword mentions from the register rows. If the register table formats change (section 1 Active recurring and One-shots tables, section 3 bold connector names, section 4 table), the page's parsers need the same change |
| Claude OS console with Jarvis | https://claude.ai/code/artifact/2a9b7e57-dbc5-49e3-a4d7-c0a36bd236b2 | Sessions, on request; source at `os/claude-os-overview.html` (8 Sep 2026 version with the Lens tab, committed 12 Sep from the repo-inbox; the live artifact was republished 8 Sep with the capability surface unchanged). Daily console: live Today tab (queue, board attention, Outlook inbox filtered to people, latest Teams messages) plus a Board tab by section, via the viewer's "Salesforce Production", "Asana" and "Microsoft 365" connectors. Jarvis HUD assistant (sample capability, viewer's own Claude usage). Write surface, each behind an in-page Approve card: Case internal note, public reply, close with reason, assign to the ICT team only (duplicate User records resolved live by recent Zeus case ownership, ambiguous matches always put to the user) (`createSobjectRecord`/`updateSobjectRecord`, verified by re-read); Asana comment, complete, move section (`add_comment`/`update_tasks`); Outlook reply DRAFT only, never send (`outlook_create_reply_draft`). Teams is read-only (no send API); replies are drafted to copy. Reads via `soqlQuery`/`search_tasks`/`outlook_email_search`/`chat_message_search`/`teams_list_chats`, plus (added 3 Sep) "Stripe" `stripe_api_read` (GetBalance across the five livemode accounts, READ ONLY — `stripe_api_write` is never declared) and "NetSuite" `ns_runCustomSuiteQL` for the Money tab, and live SF User queries for the Security tab (CONFIDENTIAL content). Jarvis carries `money_snapshot` and `security_snapshot` tools and a report library (weekly ICT status, money state, security posture, exec brief). Fixes tab (added 3 Sep): seeded catalogue of technical and process fixes plus Jarvis live suggestions (`fixes_catalog`, `fix_propose`, `fix_status`); `fix_track` creates one Asana task per approval via `create_tasks` (added to the Asana surface), verified by re-read. No bulk actions, no reassignment, no email sending from the page. Update this row and the page when the registers change materially |

Teams channel copies (SharePoint files, fixed names, never renamed):
BirdLife-ICT-Operations-Dashboard.html, BirdLife-ICT-Monitoring-Dashboard.html,
BirdLife-Security-Dashboard.html, plus the `_dashboard-run-log.txt` heartbeat.

All artifact URLs are private. Do not publish any via GitHub Pages or any
public host; they name internal systems.

**Artefact audit, 3 Sep 2026 (gallery list of the 50 most recent, checked
against this register and the live trigger list):**

- FINDING: the three dashboard artifacts were last republished 11 to 13 Aug
  (Operations 11 Aug, Monitoring 12 Aug, Security 13 Aug) and the department
  suite on 13 Aug, despite hourly and weekend routines. Cause: the routine
  session config (`session_request.config.allowed_tools`) does not include the
  Artifact tool, so every "best effort" republish step is skipped on every run.
  The Teams/SharePoint copies are the only copies those routines can rebuild.
  Decision needed: accept that the artifact copies are frozen (and say so in
  this table), or retire the three artifact URLs and point the register at the
  SharePoint files only. "Rebuilt by" in the table above is therefore wrong for
  the artifact copies until one of those happens.
- The ICT Console row (`29a063d4`) is a tombstone redirect since 3 Sep; row kept
  only so old links resolve. Do not treat it as a rebuild target.
- Live, in use, NOT registered: Security Workbench `0e4c1fb6-95ec-4dc3-a761-166281e79d42`,
  External ICT Console `cfac6ca4-ad47-4df1-bd9e-d49d7132fbc0`, Membership
  Delivery Desk `c79983b4-5375-48b1-8d73-f405c4838f95` (all updated 3 Sep),
  ICT Week in Review `c2f0dcff-9c8d-46e1-aaf8-393bf295499e` (28 Aug), Zeus
  Recovery Map `50250230-8210-48c1-b24b-62e447572621` (DR plan, 2 Sep), After
  Pardot `2f19424a-e08f-46d1-b1d7-63dab615bf0b` (31 Aug), and the five refund
  pages of 29 to 30 Aug that back the Refund fix watch routine. Each needs a
  row naming its owner job or a retire date.
- Unreferenced by any routine, register row or board, untouched two weeks or
  more (17): Gap Register, Zeus Field Kit, Woo Sync Identity Audit, Leaver
  Offboarding, Azure Private Access, Systems Insights, Duplicate Defence,
  Regular Giving Rescue Desk, Supporter Care on Zeus, BirdLife Companion, Mini
  Program Playbook, Flightpath Change Board, AI Opportunity Radar, Dashboard
  Refresh Build & Cost, Agent Aviary, Insights Model, ICT Board Reset. Full HTML
  exported 3 Sep to Google Drive `Claude\Archive\artifact-archive-2026-09-03-*.html` (17 files, confirmed present 12 Sep)
  (17 files). Deletion is Mathew's manual step in the gallery; the tool has no
  delete action.
- Personal (non BirdLife) artifacts are out of scope and were not assessed.

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
| GitHub repository `mathewruahema-beep/Birdlife` public since 2 Aug 2026 | Confidential content exposed; visibility is Mathew's setting | Make private, disable Pages, prune branches, then run the leaked-credential sweep over the history (ADR 0021) |
| Zapier: Microsoft Teams connection under the shared `admin365.ross@BirdLifeAustralia.onmicrosoft.com` login (created 24 May 2024, last refreshed 25 Jul 2024, connection 47169426) | Shared admin credential still authorised (IT-GOV-004 finding F2) | Confirm no Zap uses it, remove it, close the row |

## 6. Memory register

Episodic memory lives in `memory/` (rules in `memory/README.md`); the map of
the whole brain is `INDEX.md`. Both created 11 Sep 2026 on Mathew's
instruction ("build it, steps one to four"). The charter's session close rule
makes the journal entry and the skill or facts edit mandatory in the same
commit as any change; the weekly audit (step 6 in `birdlife-os`) reports drift.

| Item | State | As of |
|---|---|---|
| Journal | `memory/journal/`, one file per day; backfilled 7 Aug, 2 Sep, 3 Sep from this register and the git log; live from 11 Sep 2026 | 11 Sep 2026 |
| Patterns | `salesforce.md`, `website.md`, `claude-estate.md` seeded from the skills; new files per system as patterns arrive | 11 Sep 2026 |
| Routine write-back | Not yet: no routine appends to the journal. Adding it to the weekday job and the pre-draft is an estate change (propose first) | 11 Sep 2026 |
| Weekly audit memory check | In the `birdlife-os` skill, which the live audit routine follows; no trigger change needed | 11 Sep 2026 |
| Account pull | Eight account-only skills and four newer account copies committed to the repo; the repo is now a superset of the account except for `references/facts.md` and the memory audit steps, which the account lacks | 11 Sep 2026 |
| Open decision | Two brains: stop syncing skills to the account (always start on the repo) or keep re-uploading by hand. Recommendation on record: repo only, keep `email-voice` on the account. Mathew to decide; nothing deleted yet | 11 Sep 2026 |
| Closed 12 Sep | `birdlife-core`, `os/lenses.md`, ADRs 0001 to 0020 and the repo-inbox patches located in Google Drive and committed | 12 Sep 2026 |
| Decided 12 Sep (ADR 0021) | The git repository is the executable brain; `GoogleDrive/Claude` in Mathew's personal Google account is the human copy and weekly `git bundle` backup; OneDrive is out; the repo-inbox is retired; ownership is Mathew's personally. Decided by Mathew | 12 Sep 2026 |
| **Incident, open** | The repository was found PUBLIC on GitHub on 12 Sep 2026 (created 2 Aug, Pages enabled, 30+ branches, 0 forks, 0 stars). Contains the confidential security register. Remediation is Mathew's in the GitHub UI: make private, disable Pages, prune unrelated branches; then treat as a leaked document under `birdlife-security` | 12 Sep 2026 |

## 7. Decision register

Decisions are ADRs in `.claude/skills/birdlife-core/references/decisions/`,
append-only, never edited, superseded by a new dated entry. The log runs
0001 to 0020 as at 12 Sep 2026. Known defects: ADR 0017 (autonomy levels) is
cited by 0018 and 0019 and was not found; two ADRs carry the number 0019
(Birdata supporter feed, 7 Sep 2026, Accepted; lens model and Entra write
gate, 8 Sep 2026, Proposed). The next number is 0021. Status of the open ones:

| ADR | Decision | Status |
|---|---|---|
| 0018 | Break-glass emergency access, sealed credential with the CEO or CFO, agent emergency stop | Proposed 24 Aug 2026, awaiting Mathew |
| 0019 (lens) | Lens model accepted; Entra write promotion gate (one proven reversible write, then four actions to Tier 1 with approval) | Lens model Accepted 8 Sep; gate Proposed, awaiting Mathew |
| 0019 (Birdata) | Birdata supporter feed goes to Salesforce, aggregates only, not to Ortto | Accepted 7 Sep 2026, execution pending under IT-INT-004 |
| 0020 | Salesforce Outlook add-in pilot for five users; Einstein Activity Capture held; EWS position needed before 1 Oct 2026 | Accepted 11 Sep 2026 |
| 0021 | The brain lives in Mathew's personal git repository; his Google Drive is the human copy and backup; OneDrive and the repo-inbox retired; ownership personal; repository to be made private | Accepted 12 Sep 2026 |
