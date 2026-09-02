---
name: claude-os
description: >-
  The operating system for managing the Claude estate at BirdLife Australia:
  routines, skills, connectors, sessions and artefacts, governed by the rules in
  os/README.md and the registers in os/registers.md. Use whenever the user wants
  to audit, list, create, change, pause, consolidate or retire scheduled
  routines; check why a routine failed or went quiet; review or sync skills
  between the repo and the claude.ai account; review connectors or artefact
  URLs; or run the weekly OS audit. Trigger on "audit the routines", "OS audit",
  "claude os", "what's running", "why didn't the dashboard update", "too many
  routines", "create a routine", "retire that routine", "sync the skills", or
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
