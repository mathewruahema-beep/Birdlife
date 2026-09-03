# Daily improvement schedule

The Claude estate already works for you before you sit down: drafts at 5:30am,
dashboards at 7:04am, the identity detectors at 8:00 and 8:30, the feed and
expiry monitor at 9:00. What has been missing is **your** cadence: fixed slots
where you take what the machines produced and turn it into a verified
improvement, every working day, across all three of your roles (ICT
management, IT security, coding). This document is that cadence. The usable
board is published as the *ICT Improvement Cadence* artifact
(https://claude.ai/code/artifact/0132d64d-f0c2-4ab3-87ab-eaeede193704, source
`docs/cadence-board.html`); this file is the source of truth.

Times are AEST (UTC+10) until Sunday 4 October 2026, when Melbourne moves to
AEDT. The routines are scheduled in UTC, so from 5 October they fire an hour
later on the clock until the DST one-shot (`trig_01YY3yjtTASm7MvUCh8ceW11`)
re-derives them. Shift your slots with them, not before.

## The rules that make it work

1. **Two hours a day, in four fixed slots.** Not "when there is time". The
   slots are the improvement; everything else is the job.
2. **One fix to verified per day.** Verified means the control is observed in
   the system (the policy is on, the account is disabled, the count moved),
   not that a script was written. A Tier 2 fix counts when the admin has run
   it and you have re-read the result.
3. **Learn in the same day.** A fix that lands without a skill edit will be
   rediscovered in three months. The close-out slot exists for this.
4. **No new routines.** The budget is 12 of 12. If a task keeps appearing in
   your 9:15 slot, the answer is a change to an existing routine, not a new
   one.
5. **Three at a time.** The weekly plan names three fixes. The fourth is
   noise until one of the three is verified.
6. **Impact on people on every line.** A fix without who it helps and who it
   disrupts is a technical preference, not a proposal. This is your own
   standard; the schedule holds you to it.

## The daily spine (weekdays)

| AEST | Slot | Minutes | What happens | Fed by |
|---|---|---|---|---|
| 07:30 | **Approve** | 20 | Open the console, *Catch me up*. Approve or bin each `[ASSISTANT DRAFT` on the queue (max 8). Anything in New older than 2 business days gets an owner now. | Overnight pre-draft 05:30, dashboards 07:04 |
| 09:15 | **Improve** | 60 | The day's theme (below). Take the top fix from the Fixes tab or the weekly plan and drive it to *verified*. Tier 2: send the prepared change to Andrew, Keith or Nina with the exact command and a verification step, then chase in the 16:30 slot. | Detectors 08:00 and 08:30, feed and expiry monitor 09:00 |
| 12:30 | **Sweep** | 10 | Queue: New count, oldest New, anything Waiting Response over 7 days. Board: anything moved to Blocked today. One decision or one chase, then stop. | Dashboards light slot 12:04 |
| 16:30 | **Close out** | 30 | Write the day's line in `docs/improvement-log.md`. Teach the assistant one thing (skill edit committed, or "nothing learned" written down). Check the 16:04 dashboard slot ran. Set tomorrow's 09:15 fix. | Dashboards light slot 16:04 |

The 09:15 slot is the one that moves the estate. If a day is lost to
incidents, the 16:30 close-out still runs: the log line says "no fix today,
incident X", which is data, not failure.

## The weekly themes

Each weekday carries one role so that every role improves every week and
none of them silently owns all five days.

| Day | Theme | Role | 09:15 block does | Who it affects |
|---|---|---|---|---|
| Monday | **Estate and queue** | ICT management | Read the 06:00 OS audit report and make its decisions, one line each. Act on the 08:30 stale case chaser. Backlog hygiene on the Asana board: close, delegate or date every untouched item over 30 days. Set the week's three fixes. | Andrew, Keith, Nina (owner load), requesters waiting in New |
| Tuesday | **Security** | IT security | Deadline register with days remaining computed. One Essential Eight control moved (report-only first for CA). One credential watchlist row closed with who verified. Update the posture number and date in `birdlife-security`. | Every staff member (MFA, CA), CFO (NetSuite certificate), donors (WordPress exposure) |
| Wednesday | **Data and money** | ICT management | Salesforce data quality (Type on close, report record-type filter, MTTR field). Money lens: the gap between Stripe, Salesforce and NetSuite this week, named. One reconciliation bridge advanced. | Nina Lewis (reconciliation), CFO, fundraising (a correct dashboard) |
| Thursday | **Build** | Coding | Console, skills, routine prompts, the Entra admin connector plan. Ship one change end to end: edit, commit, push, republish, register row. Diagnose any routine whose last run was abandoned. | You (the 07:30 slot gets faster), the team (a shared console) |
| Friday | **People and reporting** | ICT management | Polish the 14:00 weekly status draft and send it. Membership Build status to the steering group. Weekly scorecard filled in. Next week's three fixes chosen and one Asana task each. | Your manager and the exec (status), the membership steering group, the team (a clear next week) |

## The weekly scorecard (fill in Friday 16:30)

Every number carries its as-of date. Baselines are the last live reads in the
repo and skills; the first Friday re-reads all of them.

| Measure | Query or source | Baseline (as of) | Target | Direction |
|---|---|---|---|---|
| Open Ask Zeus cases | Queue SOQL, `RecordType.DeveloperName = 'Zeus'` | 20 (6 Aug 2026) | Under 20 | Down |
| New older than 2 business days | Console Today tab | 5 of 8 (6 Aug 2026) | 0 | Down |
| Open cases older than 30 days not Waiting External | Queue SOQL by CreatedDate | 2 (6 Aug 2026) | 0 | Down |
| Open cases with no Type | Queue SOQL, `Type = null` | 13 of 20, 65% (6 Aug 2026) | Under 20% | Down |
| Asana Blocked with no movement over 14 days | Projects tab | 4 (6 Aug 2026) | 0 | Down |
| Asana overdue | `due_on` past | 4 (6 Aug 2026) | 0 | Down |
| Salesforce sysadmin ratio | `birdlife-security` User query | 15% (Jun 2026) | 5% or under | Down |
| Entra Global Administrators | Entra admin center | 6 (Jun 2026) | 4 | Down |
| Routines with a failed or abandoned last run | `list_triggers` | 1, overnight pre-draft (3 Sep 2026) | 0 | Down |
| Credential watchlist rows open | `os/registers.md` section 5 | 9 (3 Sep 2026) | 0 open past its date | Down |
| Deadline rows past with no verified outcome | `birdlife-security` register | 4 (3 Sep 2026) | 0 | Down |
| Fixes verified this week | `docs/improvement-log.md` | 0 | 3 | Up |
| Skill edits committed this week | `git log --since` on `.claude/skills` | see log | 3 or more | Up |

If a measure has not moved in three consecutive weeks, the Monday block asks
why and the answer goes in the log. Three weeks flat is a process problem, not
a workload problem.

## Monthly and quarterly

| When | What | Owner |
|---|---|---|
| First Monday of the month | Routine slot review: does each of the 12 still earn its place. Re-verify any fact in a skill older than 90 days that a fix depends on. Retire dismissed fixes older than 60 days from the Fixes seed. | Mathew |
| First Tuesday of the month | MFA audit re-run, Zapier connection ownership, admin counts (Entra and Salesforce). | Mathew |
| Quarterly (next 19 Sep 2026) | Enterprise app access review; Salesforce sysadmin and inactive-user review; NetSuite role review. | Mathew |
| Quarterly | Board paper from the exec brief: Essential Eight table with movement, incidents, spend, top three risks with owner and date. | Mathew |

## The first three weeks, dated

This is the plan the themes run on until the Friday scorecard produces a new
one. Deadline items come first because a passed date is a finding.

**Week of 7 September**
- Mon 7: OS audit decisions. **Merge `claude/os-for-claude-y12d5q` to the default branch.** Until that lands, every fresh session on the repo loads the old charter and none of the security, people-lifecycle, reporting, improvement or OS skills. Then diagnose the overnight pre-draft (last run ABANDONED 2 Sep): read the run session, connector attached or not, fix or pause with a review date.
- Tue 8: **Vevox SAML certificate expires today.** Verify SSO, renew. Verify what Salesforce did with the 1 September release updates (OAuth username-password retirement, instanced URLs, Authorized Email Domains, Profile Filtering) and what MoveData did. Close the WordPress "anyone can register as Shop Manager" toggle: one setting, verified by re-read.
- Wed 9: Add the `Ask Zeus` record-type filter to the ten helpdesk reports (about 10 minutes in the UI). Sanity check: *Open Jobs by Status* totals about 20, not 4,344. Then the `Zeus_Type_Required_On_Close` validation rule spec to a Salesforce admin.
- Thu 10: Build: confirm WooCommerce API key rotation and close the watchlist row, or rotate it. Regenerate the miniOrange access keys in prod and staging, scrub the three documents.
- Fri 11: Weekly status. Scorecard baseline re-read. Next week's three.

**Week of 14 September**
- Mon 14: OS audit decisions. Backlog hygiene: the three Blocked items that are decision debt (portal email mismatch, Plauti bulk merge permissions, duplicate management) get a decision in a meeting this week, not developer time.
- Tue 15: **Tenant-wide MFA Conditional Access target date.** State where it actually is: policy in report-only since when, exclusions, rollback. If it is not enforceable today, the new date and the reason go in the register the same day.
- Wed 16: `Days_to_Resolution__c` formula field and the real MTTR report. Money lens for the week.
- Thu 17: **NetSuite orphaned OAuth2 certificate expires today.** Revoke, monitor, delete, in that order, after confirming no scheduled job uses it. Then Entra admin connector step 1 (app registration) if the GA time is booked.
- Fri 18: Weekly status. Prepare the enterprise app review for tomorrow's deadline.

**Week of 21 September**
- Mon 21: OS audit decisions. Enterprise app access review outcome recorded (due 19 Sep). Disable `test101` and `test123` in Salesforce.
- Tue 22: Salesforce Transaction Security Policies release update (overdue since 13 Jul). Sysadmin count and ratio re-read, the removal list actioned one account at a time.
- Wed 23: Field History Tracking on Case Status (the Asana task assigned to Kate Rogerson, in Backlog since 2025). Unlocks time-in-status.
- Thu 24: Build: the Entra admin connector consent (step 1 item 3) if not landed; otherwise the first supervised offboarding end to end on the next real leaver.
- Fri 25: Weekly status. First monthly review scheduled for Monday 5 October, which is also the day after the DST shift: check every routine's clock time that morning.

## Putting it in your calendar

The four daily slots and the Friday scorecard are recurring Outlook events.
Tell any assistant session "put the improvement cadence in my calendar" and it
will propose the exact series (07:30 to 07:50, 09:15 to 10:15, 12:30 to 12:40,
16:30 to 17:00, weekdays, Melbourne time) for your approval before creating
them. Do not let the 09:15 block get booked over: it is the only slot that
changes anything.

## What this does to the people around you

- **Andrew, Keith and Nina** get one prepared Tier 2 change a day at most,
  with the exact command and a verification step, instead of ad hoc asks.
  Tell them the cadence exists so a 09:30 message is expected, not a surprise.
- **Requesters** stop waiting in New for weeks: the 07:30 and 12:30 slots
  make two-business-day first touch a daily check, not a monthly finding.
- **Nina and the CFO** see a named money gap every Wednesday rather than a
  quarterly surprise.
- **Your manager and the exec** get a status every Friday that leads with a
  decision and carries an owner and a date on every action line.
- **You** stop carrying findings in your head. The log is the record; the
  skills are the memory; the scorecard is the evidence.
