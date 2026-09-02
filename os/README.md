# The Claude Operating System

Claude is now a production system at BirdLife: it holds connector credentials to
Salesforce, Microsoft 365, NetSuite, Stripe, Cloudflare and Zapier, it runs
unattended on schedules, and it publishes artefacts people rely on. A system with
that footprint gets managed like any other ICT system, or it sprawls. It has
already sprawled twice: 10 routines in August (two with empty prompts, firing on
schedule and doing nothing), consolidated to 4, and back up to **23 by 2 September**
with overlapping dashboard rebuilds and silently failing jobs. See
[`registers.md`](registers.md) for the audit.

This directory is the operating system: the model, the rules, the registers, and
the cadence that keep the Claude estate under control. The executable half is the
**`claude-os` skill** (`.claude/skills/claude-os/`), which any session runs to
audit the estate and apply these rules.

## The estate model

| Component | Role | Lives at | Changed by |
|---|---|---|---|
| **Charter** | Kernel: loads into every session, sets identity and guardrails | `CLAUDE.md` | Commit via a session, Mathew approves |
| **Skills** | Memory: operator knowledge, versioned | `.claude/skills/` (mirrored to the claude.ai account) | Commit via a session; re-sync account copies |
| **Routines** | Scheduler: unattended work | claude.ai Routines | claude.ai UI or a session with trigger tools |
| **Connectors** | Drivers: access to real systems | claude.ai Settings, Connectors | Mathew only, in the UI |
| **Sessions** | Processes: interactive or routine-fired | claude.ai/code, apps, GitHub | Ephemeral by design |
| **Artefacts** | Outputs: dashboard, console | Stable artifact URLs | Republished by routines or sessions |
| **Registers** | State of record for all of the above | `os/registers.md` | Same commit as any estate change |

## Operating rules

1. **The register is truth.** Anything live that is not in `registers.md` is
   drift, and drift is a finding, not a footnote. Any session that creates,
   changes or retires a routine, skill, connector or artefact updates the
   register in the same piece of work.
2. **One job per outcome.** No two routines may rebuild the same artefact or
   cover the same window. Before creating a routine, check the register for an
   existing job that could absorb the work. The August sprawl and the current
   one both came from ignoring this.
3. **Budget: 12 active scheduled routines.** Above that, something must be
   consolidated or retired before anything new goes live. One-shot reminders
   (send_later, DST fix, certificate renewal) do not count against the budget.
4. **Every routine carries its passport.** Name that says what and when, a
   prompt that states its goal and hard rules, the connectors it needs attached,
   a notification setting, and a register row. A routine that cannot say why it
   exists gets retired.
5. **Report-only by default.** A routine that writes to a production system must
   name its exact write surface and hard caps in the prompt, the way the
   overnight pre-draft does (internal comments only, max 8, never touch Status
   or Owner). New write-capable routines need Mathew's explicit go-ahead.
6. **No credentials in prompts. Ever.** The August WooCommerce key exposure is
   the standing example. Secrets go in connector configs or environment
   variables. Any credential found in a prompt gets the routine paused and the
   credential rotated, in that order.
7. **Retire with a backup.** Before deleting a routine, export its definition to
   `routines/` (credentials redacted), then delete. Deletion without a backup
   loses run history and the ability to reconstruct.
8. **Propose, then write.** The charter rule applies to the estate itself.
   Sessions propose routine changes, skill edits and consolidations; Mathew
   approves; then they execute and commit.

## Cadence

- **Weekly audit (Monday).** Run the `claude-os` skill audit: pull the live
  routine list, compare against the register, verdict every row (healthy,
  failing, paused, overlapping, unregistered), check skill drift between repo
  and account copies, verify artefact URLs still resolve, and report the
  decisions Mathew actually needs to make. The ready-to-create routine
  definition is `routines/os-weekly-audit.md`.
- **Monthly review.** Beyond the audit: does each routine still earn its slot,
  are the budgets right, has anything moved tiers (see
  `docs/entra-admin-connector.md`), do the registers match reality end to end.
- **On every estate change.** Register updated, committed, pushed, in the same
  session as the change. No "will document later".

## Change control

Create, change or retire anything in the estate through the same four steps:

1. **Propose.** State the exact change: name, schedule in UTC and AEST, prompt,
   connectors, notification, and which existing job absorbs or is absorbed.
2. **Approve.** Mathew gives the go-ahead. Per-session relaxations are honoured
   as in the charter.
3. **Execute and verify.** Make the change, then confirm it took: next fire time
   is sane, connectors attached, a paused routine actually stopped.
4. **Record.** Update `registers.md`, back up any deleted definition to
   `routines/`, commit and push.

## Incident handling

A routine is an unattended worker; when it fails, nobody is watching. The audit
treats these as incidents:

- **Abandoned or failed last run.** Diagnose from the run session, fix or
  retire. Two consecutive failures with no action is the OS failing, not the
  routine.
- **Paused with no end date.** A routine paused for more than two weeks is a
  decision being avoided: retire it (with backup) or fix and resume it.
- **Firing but idle.** The worst failure mode, and it has happened here: a
  live schedule with an empty or broken prompt. Verify output exists, not just
  that the run succeeded.
- **Stale documentation.** Docs pointing at deleted triggers or wrong URLs
  mislead every future session. Fix in the same commit as the finding.
