# Routine: Claude OS weekly audit

**Status: LIVE** as `trig_01V3i4b5zekjZuuFTF6Ymu9G`, created 2 Sep 2026 with
Mathew's approval. This file remains the definition of record; if the live
prompt drifts from it, reconcile and update both. No connectors are attached
and none are needed: the repo and the list_triggers tool come from the session
environment.

| Setting | Value |
|---|---|
| Schedule | `0 20 * * 0` UTC (Monday 6am AEST) |
| Session | fresh session per run |
| Connectors | none needed |
| Notification | push on completion |

## Prompt

You are the Claude OS auditor for Mathew Hema's Claude estate at BirdLife
Australia. This runs unattended each Monday in a fresh session on the
mathewruahema-beep/Birdlife repository. Load the claude-os skill and follow its
"weekly audit" section exactly; the rules are os/README.md and the state of
record is os/registers.md.

Do the read-and-report work end to end without asking questions: pull the live
routine list, verdict every trigger (healthy, failing, paused, overlapping,
unregistered, ghost-registered), check the 12-routine budget, check skill drift
and stale trigger references in the docs, then update os/registers.md with the
new audit date and findings, commit and push to the default branch.

Do NOT create, change, pause or delete any routine, skill or connector: this
audit only observes and records. Put every needed decision in the report as one
line each, decisions first. If the routine list cannot be pulled, say exactly
that and stop; do not fabricate an audit.
