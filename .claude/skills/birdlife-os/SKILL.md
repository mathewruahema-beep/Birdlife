---
name: birdlife-os
description: >-
  The operating system for managing the Claude estate at BirdLife Australia:
  routines, skills, connectors, sessions and artefacts, governed by the rules in
  os/README.md and the registers in os/registers.md. Use whenever the user wants
  to audit, list, create, change, pause, consolidate or retire scheduled
  routines; check why a routine failed or went quiet; review or sync skills
  between the repo and the claude.ai account; review connectors or artefact
  URLs; run the weekly OS audit; or update, fix or extend the BirdLife Australia
  console (the Jarvis command deck artifact). Trigger on "audit the routines",
  "OS audit", "claude os", "what's running", "why didn't the dashboard update",
  "too many routines", "create a routine", "retire that routine", "sync the
  skills", "update the console", "fix Jarvis", "the console shows an error", or
  any request to manage Claude itself rather than BirdLife's systems.
---

# Claude OS operator

You are operating the management layer over Claude itself. The rules live in
`os/README.md`, the state of record in `os/registers.md`. Read both before
acting. Everything below assumes them.

The single most important habit: **the register moves with reality**. Any
routine, skill, connector or artefact change you make gets its register row
updated, committed and pushed in the same session. A register that lags is
worse than no register, because people trust it.

## The console (the Jarvis command deck)

The daily working surface is the **BirdLife Australia** console:
https://claude.ai/code/artifact/2a9b7e57-dbc5-49e3-a4d7-c0a36bd236b2
Source of truth: `os/claude-os-overview.html` in this repo. Stark HUD single-look
design (dark, cyan/gold, explicit colours). Tabs: Command (default, the full
picture: operations, project rollup, decisions, patterns), Today, Projects
(Asana board by section), Money (money in/out and the reconciliation bridges),
Security (posture, admins, deadlines — CONFIDENTIAL), Fixes (the suggested-fixes
catalogue, technical and process, with Jarvis live suggestions), The system,
Schedule, Registers, Rules.

### Updating it
1. Edit `os/claude-os-overview.html`, then republish with the Artifact tool
   passing `url` = the address above (same URL, never a new artifact) AND
   restating the FULL capabilities manifest (a non-empty capabilities object is
   a full-set declaration; omitting it also works and carries the stored one):
   `sample: {}` plus `mcp.servers`:
   - "Salesforce Production": soqlQuery, createSobjectRecord, updateSobjectRecord
   - "Asana": search_tasks, add_comment, update_tasks, create_tasks (one task
     per approval, used only by fix_track)
   - "Microsoft 365": outlook_email_search, chat_message_search,
     teams_list_chats, outlook_create_reply_draft
   - "Stripe": stripe_api_read (READ ONLY — never declare stripe_api_write)
   - "NetSuite": ns_runCustomSuiteQL
2. Connector names are DISPLAY NAMES with spaces ("Salesforce Production", not
   "Salesforce-Production"; the hyphenated forms in routine mcp_connections are
   not what the mcp capability wants). A wrong name shows as "Add <name> in
   Settings, Connectors" on the tile.
3. Never declare a connector tool the session has not observed a real
   request/response for, or disclose it as unverified when publishing.
4. Commit and push the source in the same session, and update the artefact
   register row in `os/registers.md` if the capability surface changed.
5. Keep the page's embedded register data (routines, decisions, counts) in sync
   with `os/registers.md`; the page is a mirror, the markdown is authoritative.

### Observed API facts (hard-won, do not rediscover)
- M365 tools return ONE JSON block per item in `result.content`, not a single
  payload; parse all text blocks and drop pagination trailers
  (moreResults/nextOffset/nextCursor).
- `outlook_create_reply_draft` answers in PLAIN TEXT ("id: ... webLink: ..."),
  not JSON. It creates a draft only; `outlook_send_draft` exists but the console
  deliberately never sends (charter: drafts are reviewed in Outlook).
- Teams has NO send API: replies are drafted for copy-paste. Chat search with a
  date filter scans recent chats only (channels can be missed).
- Salesforce soqlQuery returns `{totalSize, done, records:[...]}` with
  relationship fields nested (r.Owner.Name).
- Asana `update_tasks` reports per-task `succeeded`/`failed`; check `failed`
  before claiming success. Section move = add_projects {project_id, section_id}.
- Stripe `stripe_api_read` GetBalance returns amounts in CENTS:
  `{available:[{amount,currency}], pending:[...]}` — divide by 100. Pass
  `stripe_context` = the account id and `livemode: true`. There are FIVE
  livemode accounts (see birdlife-stripe skill for the list); balance shape
  observed on eCommerce and assumed identical on the other four.
- NetSuite `ns_runCustomSuiteQL` returns `{data:[...], totalResults,
  numberOfPages}`. Always filter subsidiary id 2; never create saved searches.
- `sample` (Jarvis): the framing must be folded into the FIRST user turn;
  two consecutive user turns, a tool count over `limits().tools.maxCount`,
  or `cache` other than false with tools all fail the call. The page shows
  `[code] message` for page-bug codes so the cause is visible; a bare
  "Transient hiccup" now means a genuine upstream_error.

### The action contract (what Jarvis on the page may do)
Reads: live snapshot, single SOQL SELECT (always LIMIT, Cases always scoped
RecordType.DeveloperName='Zeus'), Asana search. Writes, each behind an in-page
Approve card showing the exact change, one record at a time, verified by
re-read, with an internal audit comment on case writes: `case_comment`
(public false = internal note, public true = reply, optional status),
`case_close` (validated reason, Type if blank), `case_assign` (ICT team only;
duplicate User records resolved live by recent Zeus case ownership, ambiguity
always put to the user), `task_action` (comment, complete, move), `fix_track`,
`email_draft_reply` (Outlook DRAFT). Tools are consolidated to 13 because the
sample capability caps tools per call (`limits().tools.maxCount`); the page
trims to the cap if it is ever lower. Never: send email, bulk actions,
assignment outside the team, Entra/M365 admin, Salesforce config. Decide-as-
Mathew mode states the call (money first, efficiencies second, then risk), the
reason, reversibility, then executes via the card; a cancelled card is an
overrule.

### Money tab and money_snapshot
The Money tab is a LENS, not a ledger: Stripe, Salesforce and NetSuite rarely
agree, and the gap between them IS the finding. It shows won opportunities and
paid payments (last 7 days, Salesforce), live balances summed across all five
Stripe livemode accounts, and the three broken bridges as standing facts: the
SF→NetSuite manual monthly CSV, the unreconciled income backlog, and the two
stale bank reconciliations. Jarvis has a `money_snapshot` tool that returns the
live numbers plus those doctrine facts. Rules: stripe_api_read only, NEVER
stripe_api_write on or from the page (livemode = real donor money); never
assert a refund is reflected in Salesforce without verifying; number-field
filters use `!= null AND != 0`, never bare `!= null`.

### Security tab and security_snapshot
CONFIDENTIAL content: admin names, deadline dates, gaps. Never paste it into
tickets, chat or documents. Shows sysadmin list with last logins (birdbot
service accounts flagged), inactive-admin and stale-user counts from live SF
User queries, and the deadline board with days remaining. Jarvis has a
`security_snapshot` tool; posture beyond Salesforce (Entra, CA, Intune) is not
readable from the page and the snapshot says so instead of guessing. The deep
dive stays in the weekly Security dashboard artifact (linked from the tab).

### Fixes tab and the fix tools
The Fixes tab is the improvement loop's working surface (process in
`birdlife-improvement`). Seed catalogue lives in the page as `FIXES_SEED`
(id, title, system, cat, sev 1-3, tier 1-3, effort, owner, why, people,
steps, src); Jarvis uses one `fixes` tool (action list, propose, status) to
read, add live suggestions and record progress, and `fix_track` creates
ONE Asana task in Backlog/Requests behind an approval card, verified by
re-reading the board. Status and Jarvis additions are per-browser
(localStorage); the durable record is the Asana task and, once done, the
skill update. When a seeded fix is completed for good, remove it from
`FIXES_SEED` and record the outcome in the owning skill in the same commit.
`create_tasks` response shape was not observed before first use; the tool
verifies by re-read and refuses to create twice.

### Reports (the console writes them, sessions polish them)
Jarvis on the page writes reports from live snapshots on request. Library:
"weekly ICT status", "money state", "security posture", "exec brief". Rules
baked into the page instructions: pull fresh snapshots first, every action
line carries an owner and a date, Mathew's email voice, one page unless asked.
For a polished document (docx, board paper), the page report is the draft; a
repo session with the document skills produces the file. Register C in
`os/registers.md` tracks any recurring report as a routine like any other job.

### Console failure modes
- Tile says "Add/Reconnect <connector>": connector name mismatch or lapsed
  auth; fix in claude.ai Settings, Connectors, or correct the name and republish.
- Jarvis dead with "not available for this account": sample capability not
  granted for that viewer; the page hides it by design.
- A write "did not stick": the page re-reads and says so; trust the re-read,
  check the record in the source system, never blind-retry a write.
- Page content stale vs registers: republish after syncing the embedded data.

## Estate state checkpoints (update when they change)
- 3 Sep 2026: 12 recurring routines of a budget of 12 (budget decision closed by
  retiring the Top 10 email draft), 2 one-shots. Old ICT Console artifact
  tombstoned to a redirect; console/ and dashboard/ removed from the repo.
  Department suite and Ops/Monitoring dashboards KEPT (console does not cover
  their content or their team audience); the retire-or-share decision is open
  in the registers.
- 3 Sep 2026 (later): console gained Money and Security tabs, money_snapshot
  and security_snapshot Jarvis tools, and the report library; capability
  surface extended with Stripe (stripe_api_read) and NetSuite
  (ns_runCustomSuiteQL). Five livemode Stripe accounts confirmed (the skill
  previously knew one).

## The weekly audit

Run when asked ("run the OS audit") or when the weekly audit routine fires.

1. **Pull the live routine list** with the `list_triggers` tool (claude-code-remote
   MCP server; load via ToolSearch if needed). The result can exceed the output
   limit; if it is saved to a file, parse it with python and extract id, name,
   cron_expression, run_once_at, enabled, ended_reason, suspension_reason,
   next_run_at and last_run per trigger.
2. **Verdict every trigger** against the register:
   - *Healthy*: registered, enabled, last run succeeded or plausibly pending.
   - *Failing*: last run abandoned or failed. Incident: read the run session if
     reachable, name the probable cause (connectors not attached, permissions,
     prompt error), propose fix or retire.
   - *Paused*: not enabled with no suspension_reason. Over two weeks paused is
     a decision to force: retire with backup, or fix and resume.
   - *Overlapping*: shares an outcome or a time window with another routine.
     Convert crons to AEST and actually compare; collisions at the same minute
     have happened twice.
   - *Unregistered*: live but not in the register. Add it and question it.
   - *Ghost-registered*: in the register but not live. Remove the row, note why.
3. **Check the budget**: recurring active routines against the cap of 12
   (one-shots exempt). Over budget means propose consolidation, not shrug.
4. **Check skill drift**: repo `.claude/skills/` against the account-synced
   copies where visible. Flag account-only skills that should be committed.
5. **Check artefacts and docs**: the registered artifact URLs, and grep the
   repo (`README.md`, `docs/`, `routines/`) for trigger IDs that no longer
   exist.
6. **Report**: lead with what changed since last audit and the decisions Mathew
   needs to make, one line each. Then update `os/registers.md` with the new
   audit date and findings, commit, push. Propose fixes; execute only approved
   ones.

## Creating a routine

Refuse to create casually. Walk the change control from `os/README.md`:

1. Check the register for an existing routine that could absorb the work
   (rule: one job per outcome). Check the budget.
2. Draft the passport: name (what and when), cron in UTC with the AEST
   translation shown, prompt with goal and hard rules, connectors needed,
   notification setting. For write-capable routines, the prompt must name the
   exact write surface and hard caps (model: `routines/overnight-pre-draft.md`).
   Never place a credential in a prompt.
3. Show Mathew the passport, get the go-ahead, then create (or, if creation is
   denied by permission mode, save the definition to `routines/<name>.md`
   marked ready-to-create, as done before).
4. Verify next_run_at is sane, remind that connectors must be attached in the
   claude.ai Routines UI (API attachment is not permitted), add the register
   row, commit.

## Changing, pausing, retiring

- **Change**: prefer `update_trigger` over delete-and-recreate; recreation
  loses run history. Update the register row.
- **Pause**: record the date and the intended decision in the register. A pause
  without a review date is drift.
- **Retire**: export the full definition to `routines/` first (redact any
  credential and flag it for rotation on the watchlist), then delete, then
  remove or annotate the register row. Never delete without the backup.

## The skill estate (what exists, what each is for)

Fourteen skills, all versioned in `.claude/skills/` and mirrored to the
account by uploading a zip per skill (the uploader rejects any name containing
"claude"). System skills: `birdlife-salesforce`, `birdlife-microsoft365`,
`birdlife-asana`, `birdlife-netsuite`, `birdlife-wordpress`,
`birdlife-stripe`, `birdlife-zapier`, `birdlife-cloudflare`. Cross-cutting:
`birdlife-ict-assistant` (workflow and tiers), `birdlife-security` (posture,
deadlines, incidents), `birdlife-people-lifecycle` (joiner/mover/leaver),
`birdlife-reporting` (report library and data discipline),
`birdlife-improvement` (the process-to-fix-to-learning loop behind the Fixes
tab), `email-voice` (Mathew's voice), `birdlife-os` (this one). Account-only:
`morning`.

A skill earns a slot when its knowledge is hard-won and reused. Connectors
without a skill (Atlassian, Canva, Miro, Zoom, Granola, Gmail, Google Drive
and Calendar, Microsoft Learn) are reviewed at the weekly audit: each names
the job it serves or is a disconnect candidate. Do not write speculative
skills for idle connectors; that is skill sprawl.

## Skill lifecycle

- New knowledge goes into the relevant `birdlife-*` skill file, committed and
  pushed; that is how every future session learns it.
- New skills get a register row and a CLAUDE.md table entry.
- Drift resolution: repo wins, unless the account copy is deliberately newer,
  in which case commit it to the repo first, then it wins.
- An account-only skill that a routine depends on (currently `email-voice`)
  is a single point of failure; push to get it versioned here.

## Failure diagnosis quick paths

- **"The dashboard didn't update"**: find the responsible trigger in the
  register, check last_run status, then whether connectors are attached to that
  specific routine (the most common cause: routines are created without
  connector grants and fire with no data access).
- **A routine fired but produced nothing**: read its run output before trusting
  ROUTINE_RUN_STATUS_SUCCEEDED; empty-prompt routines have run "successfully"
  for weeks here.
- **Wrong time after October or April**: the DST shift; check the standing DST
  fix one-shot and re-derive UTC crons from the new offset.

## Hard rules

- No credential in any prompt, register, or backup. Redact and rotate on sight.
- Never bulk-delete routines; one at a time, backed up, approved.
- Do not attach or detach connectors yourself; that is Mathew, in the UI.
- The charter's propose-then-write applies to the estate exactly as it does to
  Salesforce.
