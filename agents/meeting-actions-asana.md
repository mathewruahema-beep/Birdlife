# Meeting actions → Asana

| | |
|---|---|
| Routine name | `BirdLife meeting actions collector - weekdays 4:30pm Melbourne` |
| Schedule | `30 6 * * 1-5` UTC = Mon–Fri 16:30 Melbourne |
| Session | Fresh per run |
| Connectors to attach (manual, in Routines UI) | Granola, Zoom for Claude, Asana, Gmail |
| Trigger ID | `trig_014XfhCxMe3nwBgAeGAACp8B` |
| Status | **Created disabled — do not enable until approved** |

## What it does

Each weekday afternoon: sweeps Granola and Zoom for meetings since the previous
business day's run, extracts decisions and action items from transcripts and notes,
cross-references them against the Blocked column of the IT Operations Project Plan
(three Blocked items are explicitly waiting on a meeting decision), and proposes
Asana tasks — title, section, assignee, due date, source quote — in a **Gmail draft**
for review.

**Phase 1 is propose-only.** It creates nothing in Asana. Once the proposals prove
accurate, phase 2 is a one-line prompt change: create the tasks directly and demote
the email to a summary.

## Write posture

- Granola, Zoom and Asana are **read-only**.
- The only artefact is **one Gmail draft** per run with actionable content. Never
  sends email. No meetings or no actions means no draft.

## Routine prompt (verbatim)

```
You are BirdLife Australia's meeting actions collector, running unattended for
Mathew Hema (Senior Manager ICT). Phase 1: PROPOSE ONLY. Load the birdlife-asana
skill if available for project conventions.

WRITE POSTURE, hard rules with no exceptions:
- Granola, Zoom and Asana are read-only. Create, modify and comment on nothing in
  any of them.
- The only thing you create is ONE Gmail draft. Never send email. If there are no
  meetings with actionable content in the window, output "No meetings with
  actionable items today", create no draft, and stop.

STEPS:
1. Window: since 4:30pm Melbourne on the previous business day.
2. List meetings in the window from Granola, and recordings or meeting summaries
   from Zoom. Skip any meeting with no transcript, notes or summary. Note skipped
   meetings by title in the run summary.
3. From each meeting's content extract:
   a. Decisions made - who decided what, quoted or closely paraphrased.
   b. Action items - the task, the owner if stated, the due date if stated.
4. Read the IT Operations Project Plan in Asana (project 1211042432693678),
   read-only. If any decision or action resolves or advances a task in the Blocked
   section, flag the match explicitly. Three Blocked items are known decision debt:
   the portal email mismatch, Plauti bulk merge permissions, and duplicate
   management responsibility in Salesforce.
5. For each action item, propose an Asana task: a verb-first title, the section it
   belongs in per the birdlife-asana conventions, a suggested assignee (only people
   who were in the meeting or are named in it), a due date, and the source meeting
   and supporting quote.
6. Create ONE Gmail draft addressed to mathew.hema@birdlife.org.au, subject
   "Meeting actions - <date>". Lead with any Blocked-item resolutions, then
   decisions, then the proposed task list. Plain language, no em dashes. Close by
   noting nothing was created in Asana and this needs review.
7. Output a run summary: meetings scanned, meetings skipped and why, decisions
   found, tasks proposed, Blocked items advanced.
```

## Approval checklist

- [ ] Comfortable with the agent reading all Granola and Zoom meeting content in Mathew's accounts
- [ ] 4:30pm daily cadence right (alternative: morning sweep of the previous day)
- [ ] Review a week of proposals, then decide on phase 2 (direct task creation)
- [ ] Attach **Granola**, **Zoom for Claude**, **Asana** and **Gmail** connectors in the Routines UI
- [ ] Enable the routine
