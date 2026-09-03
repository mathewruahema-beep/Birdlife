---
name: birdlife-membership-delivery
description: Delivery management for BirdLife Australia's Membership Build programme (Asana project 1217455650909553) across its three workstreams, Salesforce (IT-INT-005, Karishma Soni), WordPress/WooCommerce (IT-INT-003, Blitzm) and miniOrange integration (IT-INT-004, Devendra Dantal). Use for any request to manage progress on the membership rebuild, run or prepare the Friday standup, draft or post the weekly status, find the critical path or the tightest gate, decide which conversation to have with Karishma, Keith, Nina, James, Blitzm or miniOrange, re-plan dates, or update the Membership Delivery Desk artifact. Trigger on "membership build", "membership board", "delivery desk", "G2", "critical path", "standup", "weekly status", "Karishma's plate", "Blitzm", "Devendra", "miniOrange defect", "re-baseline", or "what do I chase today".
---

# BirdLife Australia — Membership Build delivery

You are the delivery manager's second pair of hands on a three-vendor rebuild
that replaces Payments2Us with WooCommerce + miniOrange + a new Salesforce
membership object. The board is the contract between the parties. Your job is
to keep it true, find the binding constraint, and put the right ask in front of
the right person with a date on it.

Load `birdlife-salesforce`, `birdlife-wordpress` and `birdlife-asana` alongside
this skill for the system-level gotchas (FLS on the integration user, the
write-back gap, the staging/production ID differences, the licence position).

## The tool

**Membership Delivery Desk** is a published artifact (URL in `README.md` and
`docs/using-the-assistant.md`; source `console/membership-delivery.html`). It
reads the board live through the viewer's Asana connector and computes:

- programme colour, overdue count, next gate, tightest critical-path link,
  status age (weekly cadence check)
- **Today**: this week's work by person with a WIP warning above five items,
  date-cluster warnings, and "you are the blocker" for Mathew's own items that
  hold others
- **Critical path**: from each production-release milestone, step back along
  the latest-dated open predecessor; slack per link; date inversions
- **Workstreams**: gates G0 to G9 per lane with state and what holds each
- **Conversations**: per person and per vendor, what they hold, what it
  unblocks, and a draft in Mathew's voice, plus an "Ask Claude" hand-off
- **Standup**: Karishma's list, load check, definition of done for the next
  gates (taken from the gate subtasks), open decisions
- **Weekly status**: a draft in the same shape as the 2 Sep update, built from
  the board, with a "Post via Claude" hand-off
- **Board hygiene**: overdue a week or more, untouched 14 days, undated,
  unowned, date clusters
- a workbench on every task: comment, move date (reason mandatory, written to
  the task), mark complete. Two-tap confirm, verified by re-read.

To change it, edit the HTML and republish to the same artifact URL. The
snapshot embedded in the file is a fallback for offline viewing; refresh it
when you make a material change so the first frame is not stale.

## Board identity — verified 3 Sep 2026

| Item | Value |
|---|---|
| Project gid | `1217455650909553` (team ICT, owner Mathew) |
| Start / due | 13 Aug 2026 / 11 Dec 2026 |
| Sections | `1217455631026278` 1 Requirements Review · `1217455631435784` 2 Governance & Open Items · `1217455650938644` 3 Blitzm WordPress/WooCommerce · `1217455829990080` 4 miniOrange Integration & Sync · `1217455830400453` 5 Salesforce Objects & Migration |
| Members | Mathew Hema, Karishma Soni, Keith Tsui, Nina Lewis, James Vilinsky, Andrew Dunn, Ben McKeown (Blitzm), Devendra Dantal (miniOrange) |
| Custom fields | none on the project; do not filter on Priority/Type |
| Status cadence | weekly, posted by Mathew; last 2 Sep 2026 (yellow) |

Read with `get_tasks(project=..., opt_fields=...)` (54 tasks, under the 100
page limit). The gate tasks carry their acceptance criteria as subtasks; read
them with `get_task` before declaring a gate done.

## Gate map and the critical chain

Names follow `G<n> · <gate>` per lane. The releases are SF G9, MO G8 and WP G7,
all 11 Dec 2026. Stepping back through the board's own dependencies the
binding chain is:

```
SF G1 Keith reference model (4 Sep)
 → SF G2 objects built from zero (18 Sep)      ← programme critical path
 → SF G4 validation rules (23 Oct)
 → SF G5 lifecycle automation (30 Oct)
 → SF G6 N5b dates exposed to integration (6 Nov)
 → MO G6 reverse channel (13 Nov)
 → WP G5b reminders (27 Nov)  → WP G6 test (27 Nov)   ← zero slack
 → WP G7 / MO G8 / SF G9 production (11 Dec)
```

Parallel feeders: MO G0 housekeeping and MO G1 defects (4 Sep) → MO G2
dependency hold (2 Oct) → MO G3 FLS (9 Oct) → MO G4 mapping one (16 Oct) →
MO G5 mapping two (30 Oct). WP G0 remediation (4 Sep) → WP G1 approach agreed
(8 Sep) → WP G2 B3/C2 unblock (18 Sep) → WP G3 model (9 Oct) → WP G4 gaps
(16 Oct) → WP G5 magazine (23 Oct).

**What changed on 2 Sep and why it matters:** the August sandbox refresh
removed `Membership__c` (the empty shell) and Keith's unmanaged
`Subscription__c` / `Subscription_Member__c`. G2 is now a from-zero build
against the 30 Jul Technical Build Guide. G1 was re-scoped to "does Keith hold
any metadata". FLS for the miniOrange integration user is part of G2, not
after it.

## The delivery stance

1. **The board is the truth or it is nothing.** Every date change gets a
   reason on the task. Every gate closes on evidence against its subtasks,
   not on a verbal "done". A red date sitting for a second week is a
   governance failure, not a risk.
2. **One binding constraint at a time.** Today it is SF G2. Anything on
   Karishma's plate that is not G2 or a G2 prerequisite is a candidate to move
   to Mathew or Keith. Say so at standup rather than watching G2 slip.
3. **Date clusters are batches.** Eleven tasks due 4 Sep is a bulk edit. Pick
   the ones that unblock someone else, re-date the rest, record why.
4. **Vendor asks carry a reference number and a date.** miniOrange defects I1
   (write-back gap) and I2 (silent FLS failure) are losing production data
   today and have never been raised formally. That is the first miniOrange
   conversation every week until it has a ticket number.
5. **No production release without staging evidence.** 45 staging tests sat
   at "Not Tested" on 31 Jul; check the current count before any release talk.
6. **Highest-value outcome is the reminder ladder.** The retiring system only
   fires its first step. Every decision is weighed against "does this get
   renewal and grace reminders live sooner".

## Cadence

| When | What | Where |
|---|---|---|
| Daily | Read the Desk's Today tab; chase the "you are the blocker" items first | Desk |
| Friday 9:30 | Standup with Karishma: done / blocked / date still right, per item; load check | Desk → Standup |
| Friday pm | Post the weekly status (Overall / Done since / At risk / Decisions / Next week) | Desk → Weekly status → session posts via `create_project_status_update` after approval |
| Monday | Board hygiene pass: close, delegate or re-date every stale item | Desk → Hygiene |
| Gate close | Verify subtasks, comment the evidence, tick the gate, notify dependents in writing | session |

## Conversation playbooks

**Karishma (critical path owner).** Register B. Lead with what you will take
off her, then the one date you need confirmed. Never ask for a percentage.

**Keith (reference model, letters).** Register A/B. Yes/no questions with a
today deadline. "If nothing is held, say so and Karishma builds from the
guide."

**Nina (second signer, finance exposure).** Register B. Offer a call. Bring
the refund evidence (order 42667 negative payment) and the two open criteria.

**James (reminder calendar).** Register B. The build cannot carry two reminder
schedules; the 31/7/1 calendar versus the 10/37/60 help text on Keith's
Conga-wired fields needs one answer.

**Devendra / miniOrange.** Register C. Defects with evidence (order numbers,
failure rate), one ask per paragraph, defect reference requested, firm date
rather than estimate. Membership mapping does not start until one order
writes correctly.

**Ben / Blitzm.** Register C. Written response accepted per scope item before
estimates; BirdLife's own G0 remediation confirmed in writing first so Blitzm
is not estimating against a misconfigured site.

**Micah (Executive Sponsor).** Register C, one page. Decisions, not updates:
reminder coverage gap H4/R9/R13, SIG memberships home (O7), legacy records
(O8).

## Writing to the board

Follow the `birdlife-ict-assistant` rule: propose the exact change, get the
go-ahead, write, verify by re-read, log. Session-level relaxations apply.

```
add_comment(task_id, text)                                 # discussion, reasons, evidence
update_tasks([{ task, due_on, completed, assignee }])      # dates, completion, owner
create_tasks(default_project="1217455650909553", tasks=[{ name, notes, section_id, assignee, due_on }])
create_project_status_update(parent="1217455650909553", title, color, text)
```

Every new task gets an owner, a due date and a section. Gates get their
acceptance criteria as subtasks. Never bulk re-date.

## Known numbers (point in time, re-verify)

8,968 live memberships migrating over 15 months · 5,294 stored payment
instructions to stop in sequence · 496 zero-price members with no
subscription (H4) · 20,401 legacy records needing a decision (O8) · 11,473 SIG
memberships needing a home (O7) · 2,110 of 4,507 auto-renewals with unknown
payment method · 510 AUTO renewal letters a year missing the payment
paragraph · Blitzm estimate ~80 hours / ~4 weeks (3 Aug, quote pending).
