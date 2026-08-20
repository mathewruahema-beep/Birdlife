# Using the AI ICT Assistant remotely

The assistant is an interaction, not an app: you talk to Claude, and the BirdLife
knowledge (skills in `.claude/skills/` here, mirrored to your claude.ai account)
plus your connected tools (Salesforce Production, Asana, Microsoft 365, NetSuite,
Stripe, Zapier, Cloudflare) make it *your* ICT assistant. It proposes every
production change and waits for your approval before writing. Add "dry run" to any
prompt to preview without writing.

## The online console

**https://claude.ai/code/artifact/29a063d4-20c6-4793-bee5-d9916b40c84e** — bookmark
this on your phone. The Today tab shows the live Ask Zeus queue and Asana board
(via your claude.ai connectors) with a prioritised "What to do next" list, and each
case opens a workbench that can post a response on the case and close it (reason +
type handled, two-tap confirm, internal audit comment, verified by re-query). The
project board shows every section except Backlog, and each task has the same
workbench: comment, move between sections, or mark complete — verified the same way.
It also shows recent Inbox mail from real people (reply in Mathew's voice — save as
an Outlook draft or send, threaded on the original) and recent Teams messages
(reply drafted to copy + a deep link into the chat; Teams has no send API).
Every reply surface offers voice drafts from the email-voice profile to pick,
edit, and execute. The
Ask tab composes exact prompts for a Claude session; Runbooks generates the full
offboarding PowerShell sequence from a name and UPN; Reference carries close
reasons, Asana section gids, and the scoped SOQL. Source lives at `console/index.html` in this repo — tell any
assistant session "update the console" to change it. (Don't enable GitHub Pages
for it on a free plan: Pages would make the page public, and it names internal
systems. The artifact URL is private to you.)

## Ways to reach it

**1. Phone or any browser — claude.ai/code.** Start a new session on
`mathewruahema-beep/Birdlife`. The `CLAUDE.md` in this repo turns the session into
the ICT assistant automatically and the skills load with it. This is the
"solve an issue from anywhere" path — it works from your phone on the train.

**2. Claude / Cowork app (no repo needed).** The same nine `birdlife-*` skills are
synced to your account, so in any Claude conversation the assistant triggers
automatically on ticket-shaped requests, or explicitly with
`/birdlife-ict-assistant`.

**3. Scheduled routines (it works while you sleep).** Already live on the account:
- *ICT Dashboard — weekday refresh & data-flow check* (`trig_0126KYAM3TAaZpBQKN8UeVdk`),
  weekdays 7am AEST — republishes the dashboard from live data and runs the health
  checks. Connectors must be attached to the routine in claude.ai → Routines.
- *BirdLife ICT stale case chaser (report-only)* — Mondays, flags stale cases.
- *Morning brief + ICT* — weekdays 5am AEST.
- *BirdLife security dashboard monthly refresh* — 1st of the month.
Definitions and backups live in `routines/`.

**4. GitHub.** Open an issue on this repo describing the problem and start a Claude
session from it (or mention the issue in a new claude.ai/code session). Useful for
queuing work from a locked-down machine.

## What it can do directly vs prepare

- **T1 — executes now** (with your approval): Salesforce Case reads/updates/
  comments/reassign/close; Asana task moves, comments, creation; drafting replies;
  M365 user-level mail/calendar.
- **T2 — prepares for an admin** (Entra/Exchange admin not yet connected): account
  create/disable, licences, distribution lists, mailbox access, MFA resets. You get
  the exact Graph PowerShell or click-path, ready to run. The plan to promote these
  to direct execution is [`entra-admin-connector.md`](entra-admin-connector.md).
- **T3 — designs only**: Salesforce configuration (fields, flows, validation rules)
  — precise change specs for an admin to implement.

## Prompt playbook

**Triage & overview**
- `Triage the zeus queue and show me what needs action today`
- `Show my open cases aging past 30 days`
- `Summarise case <number> and how to resolve it`

**Work a case [T1]**
- `Close case <number> as resolved`
- `Set case <number> to waiting on the requester`
- `Reassign case <number> to <name>`

**Reply to a requester [T1 — always shows the draft first]**
- `Draft a reply to the requester on case <number>`
- `Reply to case <number> explaining the fix, then set it waiting`

**Asana [T1]**
- `Move the <task> task to <section>`
- `Add a comment to the <task> task: …`
- `Create a Backlog task: …`
- `Link case <number> to its Asana task`

**Onboarding / offboarding [T2]**
- `Offboard <name> — last day <date>`
- `Onboard a new starter: <name>, <role>, starting <date>`

**M365 / Entra / security [T2]**
- `Grant <person> access to <mailbox>`
- `Add <person> to the <distribution list>`
- `Triage the phishing report on case <number>`

**Systems knowledge (any of the nine skills)**
- `Why would a WooCommerce order be missing its Salesforce Opportunity ID?`
- `Walk me through the unreconciled income report in NetSuite`
- `What's our SPF situation for the Salesforce case email rule?`

## Safety, in one line

It never sends email in your name without showing the draft, never bulk-updates or
deletes, confirms the staff record before reassigning, and hands anything
security-, finance- or PII-sensitive to a human with the action prepared.

## Teaching it

The assistant's memory is this repo. When a process changes or you learn a new
gotcha, tell a session "update the <name> skill with …" — it edits the file in
`.claude/skills/`, commits, and pushes. Every future session, on any device,
knows it from then on. (Re-sync the account copies from these files when they
drift.)
