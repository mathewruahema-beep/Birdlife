# BirdLife Australia — CAB Reporting Process

**Version 1.0 — August 2026**
**Owner:** Mathew Hema (CAB Chair) · Companion to `CAB-PROCESS.md`

---

## 1. Why the CAB reports

The CAB was created to provide a better service to the organisation. Reporting
is how the organisation sees that service — and how the CAB gets the decisions
it can't make alone. Every report is generated from the Flightpath register,
so the discipline is circular: **if a change isn't in the register, it doesn't
appear in the report, and it didn't happen.** That single rule is what drives
register adoption.

## 2. Reporting lines and cadence

| Report | Cadence | Audience | Produced from | Distribution |
|---|---|---|---|---|
| CAB meeting record | Fortnightly | ICT team | Flightpath **Agenda** tab + decision log (no separate document — the register's decision log *is* the record) | Lives in the tool |
| **CAB report** | Monthly | ICT Steering Group | Flightpath **Report** tab, period = the calendar month | Email to Steering Group + filed in the Confluence **ICT** space (`OPERATIONS`) under *CAB reports*; standing item on the Steering agenda |
| Metrics review | Quarterly | Executive / leadership | Flightpath **Report** tab, period = the quarter; keep only Summary, Metrics, Failed/rolled-back, and Decisions-needed sections | One page, attached to the quarterly ICT update |

## 3. How to produce the monthly report — ~10 minutes

1. Open Flightpath → **Report** tab.
2. Set the period (defaults to the last 30 days).
3. Review the generated report on screen. The numbers are live from the
   register — do not retype or adjust them.
4. Add the two things only you can add, at the top of the pasted copy:
   - **Narrative** (2–3 sentences): the month in plain words for a
     non-technical reader.
   - **Unrecorded changes discovered**: anything found changed in production
     with no register entry (§10 of the process). Zero is the target; report
     the number honestly either way.
5. **Copy report as Markdown** (or download the `.md`), paste into the
   Confluence page and the Steering email.
6. Commit the `.md` to the repo under `cab/reports/` for the audit trail.

## 4. What each section means

| Section | What it answers | Source |
|---|---|---|
| Summary | What happened this period, in counts | Register, period-filtered |
| Decisions this period | What the CAB approved, rejected, deferred — with who and why | Change decision logs |
| Implemented & closed | What actually shipped, and its outcome | Status transitions + close outcomes |
| Failed or rolled back | What went wrong and the PIR lesson — **no blame, mechanism only** | Close outcomes `Rolled back` / `Failed` + log notes |
| High-risk pipeline | What's coming that stakeholders should see early | Open changes scored High |
| Decisions needed | The ask list. Every item names **who** must decide and **what it costs to not decide** | Deferred changes (decision debt) |
| Freeze windows ahead | Planning constraint for the next 90 days | Freeze config |
| Metrics | Success rate, emergency ratio — period and all-time vs target | Register |

## 5. Quality rules

1. **Register facts only.** The report generator is the single source of
   numbers. If a number looks wrong, fix the register, not the report.
2. **The Decisions-needed section is the point.** The Steering Group exists to
   unblock decision debt (Plauti ownership, duplicate management, portal
   email). If that section is empty two months running while Blocked items sit
   in Asana, the CAB is under-asking.
3. **PIR summaries name mechanisms, not people.** "The rollback plan hadn't
   been rehearsed" — never "Keith broke it".
4. **Report the emergency ratio even when it's embarrassing.** A rising ratio
   is the earliest signal that planning is failing upstream; hiding it defeats
   the CAB.
5. **Keep the quarterly to one page.** Executives get trends and asks, not the
   change list.

## 6. Archive

- Confluence ICT space → *CAB reports* page tree (canonical, linkable).
- `cab/reports/*.md` in this repository (audit trail, diff-able).
- The register itself keeps every decision log permanently — reports are
  snapshots, the register is the record.
