---
name: birdlife-reporting
description: How BirdLife Australia's ICT reports get written from live data in Mathew Hema's voice: the report library (weekly ICT status, money state, security posture, executive brief, Board paper, incident report, project status, OS audit, backlog hygiene), the data sources and queries behind each, the data-discipline rules that stop a report lying, and the production path from the console's Jarvis draft to a finished document on SharePoint or Teams. Use whenever the user asks for a report, brief, paper, summary, update, status, one-pager, or "write this up", or when a routine produces a scheduled report. Trigger on "report", "write up", "brief", "board paper", "exec summary", "status update", "one page", "weekly", "monthly", "summarise for the CEO", or "what do I tell the CFO".
---

# BirdLife Australia: Reporting

A report here is a decision instrument, not a record of activity. Every one
leads with what the reader has to decide or know, gives the number and its
date, names an owner and a date for each action, and says where the data came
from. Written in Mathew's voice (load `email-voice`; reports are register C).

## Data discipline (a report that breaks these is wrong, however well written)

1. **Every number carries an as-of.** "3,600 cases in New (1 Jul 2026)", not
   "3,600 cases in New".
2. **Ask Zeus scoping.** Any Case figure without `RecordType.DeveloperName =
   'Zeus'` counts all record types and inflates ICT numbers roughly 200 times.
   `Owner.Name = 'Zeus'` is the unassigned queue, not a person.
3. **Money never agrees across systems and the gap is the finding.** Quote
   Stripe, Salesforce and NetSuite side by side with the date basis stated
   (SF Close Date vs bank posting date vs Stripe available/pending).
4. **Number fields: `!= null AND != 0`.** Bare `!= null` reads 100% populated
   on empty fields in this org.
5. **Regular giving = NPSP Recurring Donations plus AAkPay Recurring
   Payments.** One object alone is wrong.
6. **Five Stripe accounts.** A Stripe figure names which accounts it covers.
7. **Confidentiality tiers.** Security names and gaps stay in the Security
   dashboard, the console Security tab and `birdlife-security`; reports for
   any wider audience carry counts and ratios only. Donor and card data never
   appear anywhere.
8. **Provenance line at the end**: systems read, queries or tools used, time
   of read, and what could not be read (Entra posture, for instance, is not
   readable from the connectors; say so rather than omit it).
9. **Unverified claims are labelled.** The Business Central ">$100k saving"
   is a vendor claim with no quote; write it that way.

## The library

| Report | Audience | Cadence | Sources | Length |
|---|---|---|---|---|
| Weekly ICT status | Mathew, ICT team, Mathew's manager | Weekly (Mon) | Zeus queue, Asana board, inbox themes, money and security snapshots, routine health | 1 page |
| Money state | Mathew, Nina Lewis, CFO | Weekly or on ask | SF won/paid 7d, Stripe balances x5, NetSuite unreconciled, bank rec ages, Zap 371228125 status | Half page + table |
| Security posture | Mathew only (names) / exec (ratios) | Weekly (Sun refresh) and on ask | SF User queries, Security dashboard, deadline register, M365 skill facts with dates | 1 page |
| Executive brief | CEO, Exec team | Monthly or on event | The three above, condensed to decisions | Half page |
| Board paper | Board / Finance, Audit and Risk | Quarterly | Exec brief plus E8 maturity table, incident count, spend, risk register movement | 2 pages max |
| Incident report | Exec, affected teams, sometimes members | Per incident | Timeline from Cases, logs, vendor tickets; email-voice "Short answer:" opening | 1 page |
| Project status (e.g. membership rebuild) | Steering group, vendor | Fortnightly | Asana sections, staging test evidence (45 tests), blockers (licences), decision gates | 1 page |
| Backlog hygiene | Mathew, ICT team | Monday | Asana: no due date, untouched 30/60/90 days, delegation prompts; "close, delegate or date it" per item | Table |
| Claude OS audit | Mathew | Monday | list_triggers vs `os/registers.md`, skill drift, artefact URLs | Decisions first, one line each |

## Live sources and the calls behind them

- **Queue**: `SELECT Id, CaseNumber, Subject, Status, Type, Owner.Name,
  CreatedDate FROM Case WHERE IsClosed = false AND RecordType.DeveloperName =
  'Zeus' ORDER BY CreatedDate ASC LIMIT 200`; ageing from CreatedDate; New vs
  In Progress ratio is the acknowledgement metric.
- **Throughput**: closed in the period by `Case_Closed_Reason__c` and `Type`,
  Zeus-scoped, with `ClosedDate = LAST_N_DAYS:7`.
- **Board**: Asana `search_tasks` on project `1211042432693678`, completed
  false, grouped by section; Blocked and Awaiting Response called out by name.
- **Money in**: `SELECT COUNT(Id), SUM(Amount) FROM Opportunity WHERE IsWon =
  true AND CloseDate = LAST_N_DAYS:7`; `SELECT COUNT(Id),
  SUM(npe01__Payment_Amount__c) FROM npe01__OppPayment__c WHERE npe01__Paid__c
  = true AND npe01__Payment_Date__c = LAST_N_DAYS:7`; Stripe GetBalance per
  account (cents); sync errors from `stripeGC__Sync_Log__c` in 24h.
- **Money bridges** (standing facts until the systems change): manual monthly
  CSV to NetSuite; unreconciled income $671,117.07 across 2,878 records at 3
  Jul 2026 growing ~$87K/day; bank recs 11104 (378 unmatched) and 11103 (120)
  last reconciled 31 Mar 2022; exception-report Zap in DRAFT.
- **Security**: the four SF User queries in `birdlife-security`; deadline
  register with days computed; M365 facts dated Jun 2026 flagged as such.
- **Estate**: `list_triggers` for routine health; `os/registers.md` for the
  state of record.
- **Voice and themes**: `outlook_email_search` for the week's threads (people
  only, drop notifications) to name what actually consumed the week.

The console's Jarvis has `money_snapshot`, `security_snapshot` and the live
snapshot tools; ask it for the report and it pulls these itself.

## Skeletons

**Weekly ICT status**
```
Short answer: <the one sentence the reader needs>.

What moved this week
- Queue: <open> open (<new> New, <inprog> In Progress), <closed> closed, oldest <days>d (<as-of>).
- Board: <n> in progress, <n> blocked (<names>), <n> done.
- Money: <SF won 7d> / <SF paid 7d> / Stripe available <sum, n accounts>; gap <x>.
- Security: <ratio> admins, <n> stale, next deadline <item> in <d> days.

Decisions I owe or need
1. <decision>: <recommendation>. Owner <name>, by <date>.

Risks I am carrying
- <risk>: <why it matters to people>, <what I am doing>.

Sources: <systems, time of read, what was not readable>.
```

**Money state**
```
Short answer: <agreement or gap in one line>.
| View | Figure | Basis | As of |
| Salesforce won (7d) | | Close Date | |
| Salesforce paid (7d) | | Payment Date | |
| Stripe available / pending | | 5 accounts, cents/100 | |
| NetSuite unreconciled | | posting date | |
The bridges: <manual CSV / unreconciled / bank rec / exception report status>.
What I would do: <one action, owner, date>.
```

**Incident report**: opening "Short answer:", then "What happened", "What we
have checked", "Impact on people" (members, staff, donors, by count), "What we
owe you and when", "What changes so it does not recur". Owned mistakes first,
plainly, with the mechanism.

**Board paper**: purpose and recommendation in the first paragraph; E8 table
with movement since last paper; incidents (count, severity, closed); spend
against budget; top three risks with owner and date; positives stated as
facts, not reassurance.

## Production path

1. **Draft** in the console (Jarvis chip "Weekly report", or ask in words) or
   in a session. Both pull live snapshots first.
2. **Polish** in a repo session when a document is needed: docx or pptx via
   the document skills when available; otherwise Markdown to HTML. Never a
   public host.
3. **Distribute**: Outlook draft for Mathew to send (`outlook_create_draft`,
   never send directly); SharePoint upload (`sharepoint_upload_file`) to the
   ICT Teams channel with a **fixed filename** (the dashboard convention:
   fixed names, never renamed). Confidential reports go only to Mathew.
4. **Record**: a recurring report is a routine and gets a register row in
   `os/registers.md` like any other job; a one-off gets the Case or Asana
   task it belongs to.

## Operating rules

1. **Lead with the decision.** If the first sentence is background, rewrite.
2. **Fresh reads before writing.** Never report from memory of a previous
   snapshot.
3. **Owner and date on every action line.** "The team will look into it" is
   banned.
4. **State what you could not read.** Missing data is a line in the report,
   not a silent gap.
5. **Mathew's voice, register C.** No exclamation marks, no filler, "X rather
   than Y" sparingly, Australian spelling.
6. **No em dashes** in anything written for Mathew.
7. **Confidentiality tier checked** before distribution, every time.
