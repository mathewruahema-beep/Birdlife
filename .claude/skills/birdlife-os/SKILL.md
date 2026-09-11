---
name: birdlife-os
description: "The operating system for managing the Claude estate at BirdLife Australia: routines, skills, connectors, artefacts, the Jarvis console, and the lens model (IT Admin live; Security, Finance link, Manager, Board and Exec stubbed). Use for OS audits, routine changes, skill sync, console updates, or any request to act through a lens."
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
picture: operations, project rollup, decisions, patterns), Lens (the active
persona and the IT Admin capability matrix), Today, Projects
(Asana board by section), Money (money in/out and the reconciliation bridges),
Security (posture, admins, deadlines, CONFIDENTIAL), Fixes (the suggested-fixes
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
   - "Stripe": stripe_api_read (READ ONLY, never declare stripe_api_write)
   - "NetSuite": ns_runCustomSuiteQL
2. Connector names are DISPLAY NAMES with spaces ("Salesforce Production", not
   "Salesforce-Production"; the hyphenated forms in routine mcp_connections are
   not what the mcp capability wants). A wrong name shows as "Add <name> in
   Settings, Connectors" on the tile.
3. Never declare a connector tool the session has not observed a real
   request/response for, or disclose it as unverified when publishing.
4. Commit and push the source in the same session, and update the artefact
   register row in `os/registers.md` if the capability surface changed. When
   GitHub is not connected to the session, save the patch and full-file copies
   to `OneDrive Birdlife\Claude\repo-inbox` with a REGISTER-ROW-nnnn.md apply
   note (pattern established 7 Sep 2026, patches 0001 to 0003).
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
  `{available:[{amount,currency}], pending:[...]}`, divide by 100. Pass
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
`case_close` (validated reason, Type if blank), `case_assign` (ICT team only,
defined live as members of the Zeus public group 00GRF000001s1RZ2AY with a
birdlife.org.au username; duplicate User records resolved by recent Zeus case
ownership, ambiguity always put to the user; charter rule 4), `task_action`
(comment, complete, move), `fix_track`, `email_draft_reply` (Outlook DRAFT).
Tools are consolidated to 13 because the sample capability caps tools per call
(`limits().tools.maxCount`); the page trims to the cap if it is ever lower.
Never: send email, bulk actions, assignment outside the team, Entra/M365 admin,
Salesforce config. Decide-as-Mathew mode states the call (money first,
efficiencies second, then risk), the reason, reversibility, then executes via
the card; a cancelled card is an overrule.

### Money tab and money_snapshot
The Money tab is a LENS, not a ledger: Stripe, Salesforce and NetSuite rarely
agree, and the gap between them IS the finding. It shows won opportunities and
paid payments (last 7 days, Salesforce), live balances summed across all five
Stripe livemode accounts, and the three broken bridges as standing facts: the
SF to NetSuite manual monthly CSV, the unreconciled income backlog, and the two
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

## Lenses (added 8 Sep 2026, IT-GOV-004, ADR 0019)

A lens is a persona laid over the estate. It fixes who is acting, which systems
and in what order, the write tier per action, the standing questions and the
outputs. A lens narrows authority; it never raises it above what the connector
and the ADRs allow. Five lenses exist: **IT Admin** (live), **Security**,
**Finance link**, **Manager**, **Board and Exec** (stubs, each named, owned and
wired to the skill that already carries its knowledge).

- The record is `os/lenses.md` (repo) with the human copy at
  `OneDrive Birdlife\Claude\IT-GOV-004_BirdLife_OS_Lens_Model.md`.
- The console has a **Lens** tab (second tab). The active lens is stored per
  browser (`claude-os.lens`) and its `framing` string is prepended to every
  Jarvis turn, so Jarvis answers in that persona and applies that tier table.
  `LENSES` and `ITADMIN_MATRIX` in the page are the data; both are also folded
  into the Jarvis state pack.
- A session opening with "act as IT Admin" (or any lens name) reads the matrix
  first, states the tier out loud for the action in hand, and never goes quiet
  on a Tier 2 action.
- The IT Admin matrix is re-verified at the Monday OS audit: one identity or
  capability call per connector. Any row older than 30 days is a baseline, not
  a fact (birdlife-core rule 2). Update the row in `os/lenses.md`, the page
  `ITADMIN_MATRIX`, and republish.
- Building a stub lens follows the same four steps: probe live, write the
  matrix, prove one action through it with its DONE test, record (ADR if a
  decision was made, register row, skill update).

### IT Admin lens: facts observed 8 Sep 2026 (re-probe before quoting)
- 22 systems in the matrix, 20 reached. Tier 1 rows: Salesforce Production and
  Staging (data only), M365 user level, Asana, NetSuite reads, WordPress UAT,
  Zapier Teams posts and reads, Atlassian ICT space, Canva, Miro, Zoom, Granola,
  Google personal folder, the Claude estate itself. Tier 2: Entra admin (write
  tools exist, gate in ADR 0019), Azure, Cloudflare (this connector does not
  reach DNS or WAF), Raisely writes, Ortto writes. Tier 3: Stripe money movement,
  NetSuite record writes, Salesforce configuration.
- Not usable: AWS bridge (no credential profile on h20blacks), GitHub (not
  connected to Cowork; patches queue in `OneDrive Birdlife\Claude\repo-inbox`).
- Findings carried as open items: F1 Entra write connector live while ADR 0002
  says pending; F2 Zapier holds a 2024 Teams connection under the shared
  admin365.ross .onmicrosoft.com login (credential watchlist); F3 AWS bridge
  credentials; F4 GitHub connection or formalise repo-inbox; F5 Raisely MCP
  token privilege unknown; F6 three overlapping Salesforce read paths.
- Delegation reads off the matrix: Tier 1 rows with one-record blast radius
  (Asana, Zeus Case comments and assignment inside the Zeus group, WordPress
  UAT order notes, Confluence ICT pages) are the first rung for Andrew Dunn
  under IT-SEC-002.

### Console publish note
The 8 Sep republish carried the stored capability declaration forward
(Salesforce Production 3 tools, Asana 4, Microsoft 365 4, Stripe 1, NetSuite 1,
sample). The Lens tab adds no new connector tools. The `show` tool now accepts
`lens` as a tab.

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
- 8 Sep 2026: lens model added (IT-GOV-004, ADR 0019 Proposed). Console gained
  the Lens tab and active-lens framing for Jarvis; open decisions now three
  (Entra write gate, dashboard estate, WooCommerce key rotation). IT Admin
  matrix verified live: 22 systems, 20 reached, AWS bridge and GitHub unusable.

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
6. **Re-probe the IT Admin matrix**: one identity or capability call per
   connector; update any row whose reach or write surface changed.
7. **Check the memory** (`memory/`, rules in `memory/README.md`):
   `git log --since=<last audit> --name-only` against `memory/journal/`. A
   commit day that touched a skill, `os/`, `routines/` or a system of record
   with no journal file that day is drift and gets a one-line finding. Then:
   journal "Open" items older than 14 days with no owner or date; fixes
   marked done in the Fixes tab or Asana with no "Learned" line; a `SKILL.md`
   changed in the window whose `references/facts.md` was not, where the
   diff contains an ID, URL or number. Write the audit's own journal entry.
8. **Check the account skill list** against `.claude/skills/`: any skill on
   the account that is not in the repo, or whose account copy is newer, is
   unversioned knowledge and a finding (11 Sep 2026: eight skills and three
   newer copies were found this way). Repo wins only once the account
   content has been committed.
9. **Report**: lead with what changed since last audit and the decisions Mathew
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

Twenty-four skills, all versioned in `.claude/skills/` and mirrored to the
account by uploading a zip per skill (the uploader rejects any name containing
"claude"; the zip must include the skill's `references/` directory, which
since 11 Sep 2026 carries a `facts.md` lookup file for the eight core system
skills). System skills: `birdlife-salesforce`, `birdlife-microsoft365`,
`birdlife-asana`, `birdlife-netsuite`, `birdlife-wordpress`,
`birdlife-wpengine`, `birdlife-stripe`, `birdlife-zapier`,
`birdlife-cloudflare`, `google-workspace-expert`. Salesforce deep dives:
`birdlife-payments2us`, `birdlife-conga`, `birdlife-sdocs`,
`birdlife-movedata`, `birdlife-powerbi`. Cross-cutting:
`birdlife-ict-assistant` (workflow and tiers), `birdlife-security` (posture,
deadlines, incidents), `birdlife-people-lifecycle` (joiner/mover/leaver),
`birdlife-reporting` (report library and data discipline),
`birdlife-improvement` (the process-to-fix-to-learning loop behind the Fixes
tab), `birdlife-prompting` (the six-line prompt frame), `email-voice`
(Mathew's voice), `morning` (personal brief), `birdlife-os` (this one).
Referenced by several skills but existing nowhere found on 11 Sep 2026:
`birdlife-core`, `birdlife-manager`, `salesforce-delivery-governance`; treat
those references as pointers to `CLAUDE.md` and this skill until the files
are located or written.

A skill earns a slot when its knowledge is hard-won and reused. Connectors
without a skill (Atlassian, Canva, Miro, Zoom, Granola, Gmail, Google Drive
and Calendar, Microsoft Learn) are reviewed at the weekly audit: each names
the job it serves or is a disconnect candidate. Do not write speculative
skills for idle connectors; that is skill sprawl.

## Skill lifecycle

- New knowledge goes into the relevant `birdlife-*` skill file, committed and
  pushed; that is how every future session learns it. Values (IDs, URLs,
  counts, dates) go in that skill's `references/facts.md` first, prose
  second. What happened (the decision, the case, the lesson) goes in
  `memory/journal/` the same day; see the charter's session close rule.
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
- A lens narrows authority. No lens, prompt or persona raises a Tier 2 or
  Tier 3 action to Tier 1; only a dated ADR does.