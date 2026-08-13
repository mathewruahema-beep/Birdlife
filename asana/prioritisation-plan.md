# IT Operations Project Plan — Prioritisation & Reporting Plan

Prepared 13 August 2026 from a live read of the Asana board
(project `1211042432693678`, [open in Asana](https://app.asana.com/1/443963187362944/project/1211042432693678)).

---

## 1. Where the board stands today

215 tasks total, 108 done, **107 open**, distributed:

| Section | Open tasks | Notes |
|---|---:|---|
| In Development/Progress | 18 | Only 3 have due dates |
| Awaiting Response | 3 | 1 overdue since 31 Jul (ABC registration, Keith) |
| Scoping/Requirements | 2 | 1 unassigned since March |
| Blocked | 11 | None dated; ≥4 are "decision on responsibility" items |
| Ready for Deployment | 0 | Never used |
| Hypercare | 0 | Never used |
| Backlog/Requests | 73 | See composition below |

**The five findings that matter:**

1. **Only 9 of 107 open tasks (8%) have a due date**, and five of those nine share
   the same 4 Dec placeholder. Nothing on the board says *when*, so nothing can be
   reported against.
2. **No project status update has ever been posted.** Asana's native status-update
   feature (the thing leadership can subscribe to) is empty. This is the reporting
   gap in one sentence.
3. **WIP is roughly double what the team can carry.** 23 tasks are active
   (In Dev + Awaiting + Scoping) across a core team of four. Nina alone has 6 in
   progress plus 5 blocked. When everything is in progress, standups reconstruct
   status instead of resolving blockers.
4. **Priority signals are fragmented.** The board's own `Priority Rank` field is
   filled on about half the in-progress tasks — as coarse tiers (1/2), not a rank —
   and three legacy priority fields from other boards (`Priority` ×2,
   `Priority level?`) leak into task panes. Meanwhile `Work Type` and `Department`
   are consistently filled — intake tagging already works.
5. **The backlog is three different things wearing one label:**
   - a **17-task Salesforce migration block** created 7 Jan, all assigned to Mathew,
     untouched since a bulk edit on 15 Jul — this is really the Membership
     Implementation programme, not 17 independent requests;
   - a **~20-task stakeholder intake batch** from 29 Jul that was captured but never
     triaged;
   - a **long tail from the Aug 2025 board setup**, several assigned to people outside
     the ICT team (Kate Rogerson, Rachel Farran, Dale Wright, Sonia Sanchez, Leeann
     Reaney, John D'Rozario) who may not know they own them.

---

## 2. The operating model

### 2.1 One priority scheme

- Hide the three legacy priority fields from this board's view.
- Use **`Priority Rank` as a strict stack rank (1, 2, 3…N)** — and only on
  *committed* work (Next Up + In Development). Two tasks never share a rank; the
  question "which do I pick up first" always has exactly one answer.
- Backlog items carry **no rank by design**. Ranking 73 things is how nothing gets
  ranked.

### 2.2 Now / Next / Later via sections

| Section | Role | Hard rule |
|---|---|---|
| In Development/Progress | **Now** | WIP limit **2 per person** (~8–10 tasks). Every task: assignee + due date. |
| **Next Up — committed** *(new section)* | **Next** | Max 15 tasks, stack-ranked. The *only* place work is pulled from. |
| Backlog/Requests | **Later** | Intake only. Tagged Work Type + Department at triage. Due dates not required here. |
| Blocked | Parked | First line of description: *who* unblocks it, *what's* needed, chase date. |
| Awaiting Response | Parked | Same rule: named person + chase date. |

Drop **Ready for Deployment** and **Hypercare** unless a real entry criterion is
defined this month — both have been empty since the board was created and are
currently just visual noise.

### 2.3 Triage rules (Monday, 30 minutes)

Every new request gets, within 7 days: `Work Type`, `Department`, an assignee, and
one of four decisions:

1. **Next Up** (it beats something already there — bump the loser),
2. **Backlog**,
3. **Decline** (close with a comment — a polite no now beats silence forever),
4. **"That's a Zeus case"** — support/incident work under ~2 hours belongs in the
   Salesforce helpdesk queue, not the project plan. (`Signing out of the LMS`-class
   items.) Note: the Case→Asana email automation is still blocked on the SPF
   record; the manual route stays until that's fixed, but don't let helpdesk work
   colonise the project board.

**Prioritisation test for Next Up**, applied in order:

1. Payment/revenue or security impact? (refund flows, 2FA, expired-licence class)
2. External deadline or third-party dependency? (Ortto go-live 31 Aug, ABC event)
3. Unblocks other committed work or a whole team?
4. At equal impact, a week of effort beats a month — ship small things.

**Staleness rules** (this is the "getting through work" mechanism):

- In Development untouched **14 days** → back to Next Up or Backlog, with a comment
  saying why. No zombie WIP.
- Backlog untouched **90 days** → close or explicitly icebox. The 7 Jan block would
  fail this today.

### 2.4 Programmes are not tasks

Membership Implementation, Ortto migration and Better Impact are programmes. The
17-task January block folds under **Membership Implementation** as subtasks or
milestones with a Go-Live Date. Programmes hold one line on the board each; their
internals don't compete with BAU requests for rank.

### 2.5 Blocked means "a decision is owed"

At least four blocked items are literally titled "decision on responsibility"
(Plauti bulk merge, portal email mismatch, duplicate management, plus Better Impact
integration). No amount of dev time closes them. They become a standing **decision
list** for the ICT Steering Committee — each with the decision needed, options, and
a recommendation. A decision made = a task closed.

---

## 3. Reporting

### 3.1 Weekly — Asana status update (Fridays)

Post natively via the project's status-update feature so it lands in inboxes and
the portfolio view. Template:

> **Status:** On track / At risk / Off track
> **Shipped this week:** …
> **Top 3 next week:** (ranks 1–3 from Next Up)
> **Decisions needed:** (from the Blocked list, with owners)
> **Board health:** open N · % dated N% · WIP N · blocked N · shipped this week N

This is automatable: the MCP's `create_project_status_update` can draft it from
live board data on a Friday routine, for review before posting.

### 3.2 Weekly — board-health metrics (baseline, 13 Aug 2026)

| Metric | Baseline | Target (4 weeks) |
|---|---:|---:|
| Open tasks | 107 | ≤ 80 |
| Open tasks with a due date (committed work) | 8% | 100% of Now/Next |
| Active WIP (In Dev + Awaiting + Scoping) | 23 | ≤ 12 |
| Blocked | 11 | ≤ 5, all with named unblockers |
| Status updates posted | 0 ever | 1/week |
| Throughput (done/week) | measure from week 1 | trend, no target yet |

These belong on the existing ICT dashboard (`dashboard/ict-dashboard.html`,
refreshed weekdays 08:00 AEST) alongside the Zeus queue numbers.

### 3.3 Monthly — steering committee pack

- Throughput by `Work Type` and `Department` — the fields are already populated,
  so this is a pivot, not a data-entry project. It answers "where does ICT time go"
  (BAU vs projects vs governance) with evidence.
- The decision list (§2.5) with ageing.
- Next month's top 10 from Next Up.
- New project requests using the existing `Approval Status` + `Budget Amount`
  fields.

---

## 4. This week's cleanup (in order)

1. **Date-or-demote the 18 In-Dev tasks.** Anything that can't get an honest due
   date and a this-fortnight intention goes to Next Up or Backlog. Enforce 2 per
   person.
2. **Chase the overdue item**: ABC registration setup (Keith, due 31 Jul, sitting in
   Awaiting Response).
3. **Assign or close the 6 unassigned tasks**: Digital mags not sending (In Dev),
   Gravity Forms mobile viewing (Scoping, from March), EPC opt-out rules (due
   31 Aug), My BirdLife portal, Website email sign-up form, Case management for
   Marketing.
4. **Fold the 7 Jan Salesforce block** (17 tasks) under Membership Implementation.
5. **Triage the 29 Jul intake batch** (~20 tasks) with the §2.3 rules — expect a
   third to be Zeus cases or declines.
6. **Confirm off-team assignees** (Kate, Rachel, Dale, Sonia, Leeann, John) actually
   know they own their tasks; reassign or close otherwise.
7. **Create the "Next Up — committed" section**, seed it with ≤15 stack-ranked
   tasks, and hide the legacy priority fields.
8. **Post status update #1** — even if it just says "baseline: here's the mess and
   the plan." Reporting starts with one data point.

Steps 1, 3, 4, 7 and 8 are scriptable via the Asana MCP and can be done in one
assisted session; 2, 5 and 6 need human calls.
