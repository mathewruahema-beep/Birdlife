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
(Asana board by section), The system, Schedule, Registers, Rules.

### Updating it
1. Edit `os/claude-os-overview.html`, then republish with the Artifact tool
   passing `url` = the address above (same URL, never a new artifact) AND
   restating the FULL capabilities manifest (a non-empty capabilities object is
   a full-set declaration; omitting it also works and carries the stored one):
   `sample: {}` plus `mcp.servers`:
   - "Salesforce Production": soqlQuery, createSobjectRecord, updateSobjectRecord
   - "Asana": search_tasks, add_comment, update_tasks
   - "Microsoft 365": outlook_email_search, chat_message_search,
     teams_list_chats, outlook_create_reply_draft
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

### The action contract (what Jarvis on the page may do)
Reads: live snapshot, single SOQL SELECT (always LIMIT, Cases always scoped
RecordType.DeveloperName='Zeus'), Asana search. Writes, each behind an in-page
Approve card showing the exact change, one record at a time, verified by
re-read, with an internal audit comment on case writes: case internal note,
case public reply (+optional status), case close (validated reason, Type if
blank), case assign (ICT team only; duplicate User records resolved live by
recent Zeus case ownership, ambiguity always put to the user), task comment,
task complete, task move, Outlook reply DRAFT. Never: send email, bulk actions,
assignment outside the team, Entra/M365 admin, Salesforce config. Decide-as-
Mathew mode states the call (money first, efficiencies second, then risk), the
reason, reversibility, then executes via the card; a cancelled card is an
overrule.

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
