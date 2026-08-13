# Work Management & Delivery Review — 13 August 2026

A review of all tracked ICT work at BirdLife Australia: the **IT Operations
Project Plan** (Asana), the **Ask Zeus** helpdesk queue (Salesforce), Mathew's
personal task load, the membership programme boards, and the scheduled
automation estate. Everything below is measured from live data pulled
13 August 2026, cross-checked against the 6–7 August findings in `README.md`.

---

## Executive summary

**The helpdesk is not your problem. Project delivery is.**

Over the last 30 days Ask Zeus closed **184 cases against 98 created** — the
queue is burning down, sitting at 22 open. BAU support has real throughput.

The project board is the opposite picture. Of ~100 incomplete tasks on the
IT Operations Project Plan, **90 have no due date**. Eighteen items sit in *In
Development/Progress* — one of them (*Cleaning up Microsoft 365 licences*) was
created exactly **one year ago today** and is still there. *Ready for
Deployment* and *Hypercare* remain empty, as they were in the 6 August pull:
**nothing has ever moved through the release stages**. Work enters the board;
it does not flow across it.

The three things costing you the most delivery right now:

1. **Unbounded work-in-progress.** 18 concurrent "in development" items for a
   team of ~5 means nothing gets the sustained attention required to finish.
2. **Unmade decisions parked as "Blocked".** 11 blocked items; at least three
   are explicitly "decision on responsibility" — one blocked since
   **7 January**, seven months. These need a meeting and an owner, not
   engineering time.
3. **Concentration on you.** ~35 open items are assigned to Mathew personally,
   plus ten unactioned "Consider delegating…" prompts, some from July 2025.

None of the fixes below require buying anything. The tooling exists and is in
several cases already half-configured; what's missing is a small number of
operating rules applied consistently.

---

## What the data says

### Ask Zeus helpdesk (Salesforce, record type `Zeus`)

| Measure | Value |
|---|---|
| Open cases | 22 |
| Created last 30 days | 98 |
| Closed last 30 days | **184** (backlog shrinking) |
| Sitting in **New** | 11 — of which 7 are past a 2-business-day first touch |
| Unassigned (owner = `Zeus` group) | 3, all arrived today — incl. *"URGENT quick fix please"* |
| Open with no `Type` | 14 of 22 (64%) |
| Oldest open case | **00109150**, created 3 Sep 2025 — **344 days** ("UTM fields from Raisely into SF") |
| Next oldest | 00133547 (76 days), 00134670 (58 days) |

Verdict: throughput is healthy; **triage is not**. Cases sit in New for weeks
(00136890 and 00136895 — 24 days each), an urgent ticket can sit unowned in
the group queue, and two-thirds of the queue has no category. Note also that
case 00109150 (UTM fields) has an apparent Asana twin — *"Update UTM fields
and layout in Salesforce"*, assigned to Nina — the same work tracked twice in
two systems with no link between them.

### IT Operations Project Plan (Asana)

215 tasks, 107 incomplete. Section spread of the incomplete work:

| Section | Count | Notes |
|---|---:|---|
| In Development/Progress | ~18 | mostly undated; oldest created 13 Aug 2025 |
| Awaiting Response | 3 | |
| Scoping/Requirements | 2 | |
| Blocked | 11 | 3 are pure decisions; oldest since 7 Jan 2026 |
| Ready for Deployment | **0** | never used |
| Hypercare | **0** | never used |
| Backlog/Requests | ~65 | grew by ~15 tasks between 29 Jul and 5 Aug alone |

- **90 of 100 sampled tasks have no due date.** Of the 10 that do, five are
  bulk-dated to the same day (4 Dec 2026) — a parking date, not a plan.
- The project has a genuinely good custom-field schema — *Priority Rank*,
  *Go-Live Date*, *Approval Status*, *Hours*, *Work Type*, *Technology
  Stack* — and it is essentially **unpopulated**. The board has the shape of a
  delivery process without the data.
- **No project status update has ever been posted** (`current_status: null`).
  Asana's status feature — the 5-minute weekly write-up that would spare the
  team reconstructing state in meetings — has never been used.
- The ~25-task **Salesforce migration batch created 7 January** (Payments2Us
  removal, Conga removal, membership object transfer, GAU reviews…) is all
  assigned to Mathew, all undated, and has only ever been touched by bulk
  edits. It is a *programme* wearing the costume of backlog tasks.
- A task created this morning by the Zeus→Asana email forward is titled
  *"Nina Lewis, Finance & Business Improvement, Legal or governance
  compliance"* — form fields concatenated into a name. The manual forwarding
  workaround (standing in for the SPF-blocked email rule) is producing
  tasks that will need hand-repair.

### Membership work — fragmented across five containers

The single most important delivery programme is spread over:

1. **Membership Build** (created 13 Aug) — gated G0–G8 plan, dated through
   December, vendor deadlines tracked. *This is the model to copy.*
2. **Membership Model** — "Testing in Staging environment", due 28 Aug.
3. **Memberships** — Blitzm epics untouched since **September 2025**.
4. **IT Operations Project Plan** — "Membership Implementation", "Membership
   update", "Transfer of Membership information into a new Object", undated.
5. **🕸️ Blitzm/BirdLife: Website Work** — MyBirdLife verification issue.

Anyone other than Mathew looking for "where is the membership rebuild up to"
cannot find a single answer.

### Scheduled automation — the consolidation regressed

On 7 August, 10 routines were consolidated to 4 (commit `90133cb`). Six days
later there are **13 active routines**, and the overlap is back:

| Dashboard-refresh-related routines today | Fires per weekday |
|---|---:|
| BirdLife dashboards hourly — weekday daytime (10am–5pm) | 8 |
| BirdLife dashboards hourly — weekday mornings (7–9am) | 3 |
| BirdLife ICT hourly monitor (7–9am) | 3 |
| BirdLife ICT dashboard — daily refresh & Teams push | 1 |
| + two weekend dashboard jobs | — |

The consolidated routine from the README (`trig_0126KYAM…`) no longer exists;
it has been replaced by a new generation of overlapping jobs. The good news:
a **Monday stale-case chaser (report-only)** and daily
onboarding/offboarding detectors now exist — those are the right ideas. The
lesson is that consolidation without a guardrail decays in under a week:
automations need an owner and a one-in, one-out rule like any other system.

### Mathew's own load

- ~35 open Asana tasks assigned personally, most undated.
- **10 "Consider delegating X's tasks" prompts** unactioned (oldest July 2025).
- 4 "update your goals" reminders unactioned.
- The entire 7 January Salesforce batch sits on you.

---

## What is already working — keep doing it

- **Helpdesk throughput** (184 closed vs 98 in) — genuinely good.
- **The Membership Build project structure** — gates, dates, vendor deadlines,
  escalation tasks. This is what managed delivery looks like; the fix for the
  rest of the estate is mostly "make it look like this".
- **The dashboard scope-correction work** (record-type filtering) and the
  provenance-visible design principle.
- The custom-field schema on the IT Ops board — right fields, just unused.
- Stale-case chaser and on/offboarding detector routines — right instincts.

---

## The five root problems

### 1. Flow is broken, not intake
Work enters Backlog freely (~15 new items in one week) but nothing exits
through the release stages. Done is reached by teleport or not at all. With no
definition of done and no stage gates, "In Development" is where tasks go to
age — 12 months in the worst case.

### 2. The board records intentions, not commitments
90% undated, custom fields empty, no status updates. A board like this cannot
answer "what will ship this month?", so every standup and steering meeting
spends its time reconstructing state instead of unblocking work — exactly the
cost the hygiene scan flagged for Keith, Karishma and Nina.

### 3. Decisions are queued as if they were tasks
"Duplicate Management in Salesforce — decision on responsibility" has been
Blocked since 7 January. "Portal email mismatch" and "Plauti bulk merge
permissions" are the same shape. A decision costs one agenda item; seven
months of queueing costs every piece of work behind it.

### 4. Delivery concentrates on one person
You are the assignee of last resort, the integration point between systems
(the `ICT Priorities.xlsx` join column — four divergent copies), and the only
person who can see the whole picture. That is a bus-factor risk and a
throughput ceiling.

### 5. Duplication instead of consolidation
Two Finance teams in Asana. Five membership containers. Same work tracked in
Zeus and Asana with no link. Thirteen routines rebuilding overlapping
dashboards. 6–7 duplicate Asana app registrations in Entra. Each duplicate is
a place where truth can diverge — and does.

---

## Missing processes (cost: discipline, not money)

**P1 — A WIP limit.** Cap *In Development/Progress* at ~2 items per person
(team of 5 → max 10, today 18). Everything else goes back to Backlog with its
place in the queue preserved by *Priority Rank*. The rule that makes it stick:
**starting something new requires finishing or demoting something first.**

**P2 — Date it, delegate it, or drop it.** The Monday stale-chaser already
produces the list. Institute the rule that every item it flags gets one of
those three verbs at Monday standup — no fourth option of "leave it". Bulk
outcome for the 7 Jan batch: promote it into a sequenced roadmap under the
Membership Build programme (most of it is the same programme) or archive it.

**P3 — A decision log with escalation.** The three "decision on
responsibility" blockers go to the next ICT Steering meeting as agenda items
with a written option A/B and a decide-by date. The *Approval Status* field
and the *"Speak to at Meeting 🌟"* field already exist for exactly this — use
them. Any item Blocked >14 days must name the person whose decision unblocks
it.

**P4 — A triage SLA for Ask Zeus.** Assign within 1 business day, first
response within 2. The `Zeus` group queue is the visible intake — an URGENT
ticket sat there today unowned. The hourly-monitor routine can enforce this by
exception (ping only when breached) instead of republishing dashboards
hourly.

**P5 — A weekly written status.** One Asana project status update per week on
the IT Ops board and on Membership Build: shipped / next / blocked / decisions
needed. Five minutes, and standups stop being archaeology. (`current_status`
has been null for a year.)

**P6 — Real delegation.** Convert the ten "consider delegating" prompts into
actual stream ownership: e.g. Keith — Salesforce/UTM/RD change-log stream;
Nina — GAU/donations/eCommerce stream; Andrew — M365/identity/hardware. The
assignee owns moving their items across the board, not just doing the work.

**P7 — Automation governance.** This repo is the registry. Every routine gets
an owner and a purpose line; creating a routine requires retiring or extending
an existing one (one-in, one-out); re-consolidate the current 13 down to ~5
(morning brief, one dashboard job, weekly security, weekly stale-chaser,
on/offboarding detector). The 7 Aug consolidation proved this decays without a
standing rule.

**P8 — One home per programme.** Membership work consolidates into
*Membership Build*; the Sep-2025 Blitzm epics get archived or migrated; IT Ops
membership tasks become links/subtasks. Same principle for the Zeus↔Asana
join (see T3) — retire the four-copy spreadsheet.

## Missing tools (all config on things you already own)

**T1 — Asana rules on the IT Ops board.** Auto-flag anything unmodified 30
days; auto-move dated-overdue items to top of section; require assignee + due
date on section entry to *In Development*. Use the **Workload view** to make
the concentration on you visible to the steering committee.

**T2 — The four Salesforce admin fixes from `README.md`, still pending.**
Record-type filter on the ten reports (~10 min, highest leverage), the
`Zeus_Type_Required_On_Close` validation rule (open queue is still 64%
typeless), `Days_to_Resolution__c` + a real MTTR report, and field history on
`Status`.

**T3 — Unblock the Zeus→Asana email rule (SPF).** Add
`include:_spf.salesforce.com` to the birdlife.org.au SPF record **via
IT/security review — it is a domain-wide email-authentication change** — then
DKIM in Salesforce, then retest. This kills the manual forward that is
generating garbage-titled tasks, and gives you the durable Case↔task link that
replaces `ICT Priorities.xlsx`.

**T4 — A self-service request form for identity lifecycle.** IAM + starters +
leavers = 20% of all helpdesk volume, 96.5% of intake is unstructured email.
A structured form (web-to-case or Gravity Forms → Case) plus the existing
onboarding/offboarding detector routines turns your biggest ticket category
into a checklist. This is the one place a small build is justified.

**T5 — Routine connector hygiene.** Attach Salesforce + Asana connectors to
whichever dashboard routine survives consolidation (the README gap), and
confirm the exposed WooCommerce keys from the deleted routines were rotated.

---

## A 30-day sequence

| Week | Actions |
|---|---|
| **1** | Ten-minute Salesforce report filter fix (T2). Triage the 11 New cases; assign the 3 unowned. Post first weekly status update (P5). Put the three decision items on the steering agenda (P3). |
| **2** | Board reset: WIP limit to 10, everything else to Backlog with Priority Rank set (P1). Date-delegate-drop pass over the stale list (P2). Reassign streams to Keith/Nina/Andrew (P6). |
| **3** | Consolidate membership containers into Membership Build (P8). Archive the Sep-2025 epics. Re-consolidate routines 13 → ~5, attach connectors (P7, T5). |
| **4** | Raise the SPF change through security review (T3). Stand up the validation rule + MTTR field (T2). Scope the identity-lifecycle request form (T4). |

After 30 days, the test of success is a board that can answer three questions
without a meeting: *what ships this month, what is blocked on whom, and what
did we decide.*

---

*Data sources: Asana project 1211042432693678 (13 Aug 2026), Salesforce SOQL
over Case record type `Zeus` (13 Aug 2026), claude.ai routine registry
(13 Aug 2026), `README.md` findings of 6–7 Aug 2026.*
