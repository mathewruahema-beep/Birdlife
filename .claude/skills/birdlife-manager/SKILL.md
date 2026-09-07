---
name: birdlife-manager
description: The weekly ICT manager review for Mathew Hema at BirdLife Australia, run from live evidence (Asana IT Operations Project Plan, Zeus Case queue, routine health, the security deadline register) and turned into a one-page scorecard, one learning for the week, and named delegations under the IT-SEC-002 capability ladder. Use when Mathew asks how he is doing as a manager, wants the weekly review, the manager scorecard, the learning log, what to delegate, what is blocked on him, or "make me a better ICT manager". Trigger on "weekly review", "manager review", "scorecard", "learning log", "what should I delegate", "what is blocked on me", "how is the team tracking", "am I improving", or a Monday request to see the state of ICT.
---

# BirdLife ICT manager review

This skill exists because the record shows the same four manager failures repeating since August 2026: figures carried without their scope, tasks with no date, work blocked on a decision only Mathew can make, and deliverables that land on Mathew instead of the team. It does not teach ICT management. It measures Mathew's management against BirdLife's live data every week and writes down one thing learned, so the record gets better and so does he.

Read `birdlife-core` first (precedence order, fact classes, write tiers). This skill is Tier 1 for reads and for writing its own files. Anything it recommends in Entra, Salesforce configuration or a vendor stays Tier 2 or 3 and is handed over, never claimed done.

Boundary with the daily "AI Daily Ten and learning loop" routine (created 7 Sep 2026, AI Field Guide artifact, repo `docs/ai-practice/`): that loop watches Mathew's AI practice daily. This skill watches Mathew's management of the estate and the team weekly. Do not merge them and do not duplicate their entries. Where both notice the same thing, this skill records it and the daily loop links to it.

## Files

| File | Path | Rule |
|---|---|---|
| Weekly review | `OneDrive Birdlife\Claude\Manager\Manager-Review-<YYYY-MM-DD>.md` | One per week, never edited after the day it is written |
| Learning log | `OneDrive Birdlife\Claude\Manager\Manager-Learning-Log.md` | Append only. One dated entry per week, one learning per entry |
| Document ID | IT-GOV-003 | Both files carry it |

Repo copy: `docs/manager/` in the Birdlife repo when the session has it; otherwise write a patch to `OneDrive Birdlife\Claude\repo-inbox\` as the prompting skill did.

## The review, in order

Every step names the query it ran. A number without a query does not go in the scorecard.

### 1. Prove state (four pulls, ten minutes)

**Zeus queue** (`mcp__Salesforce_Production__soqlQuery`). Always scope to the record type; the org holds thousands of programme Cases that are not ICT's.
```sql
SELECT Status, COUNT(Id) total FROM Case
WHERE RecordType.DeveloperName = 'Zeus' AND IsClosed = false GROUP BY Status
```
```sql
SELECT Owner.Name, COUNT(Id) total FROM Case
WHERE RecordType.DeveloperName = 'Zeus' AND IsClosed = false GROUP BY Owner.Name
```
```sql
SELECT COUNT(Id) FROM Case WHERE RecordType.DeveloperName = 'Zeus' AND ClosedDate = LAST_N_DAYS:7
```
Also the sysadmin count from `birdlife-core` verification queries.

**Asana IT Operations Project Plan** (`mcp__Asana__search_tasks`, project `1211042432693678`, `completed=false`, limit 100, `opt_fields` name, assignee.name, due_on, modified_at, memberships.section.name). Count: open, undated, overdue, due this week, per assignee, in Blocked, untouched 30+ days, assigned to Mathew. The search caps at 100; take the true total from `mcp__Asana__get_project` (task_counts.num_incomplete_tasks) and run a second search per assignee for anyone whose tasks were cut off. On 7 Sep 2026 the cap hid 12 of Mathew's own tasks.

**Routines** (`mcp__claude-code-remote__list_triggers`, limit 50; parse the saved file with python). Count recurring against the budget of 12, and list any last run that is not SUCCEEDED or is older than its schedule implies.

**Deadline register** from `birdlife-security`. Compute days remaining today. Anything passed and unverified is a finding. Entra items cannot be verified live (Tier 2); say so and name the check Mathew runs.

Money bridges (Stripe, unreconciled income, bank recs) are pulled monthly, first review of the month, using `birdlife-stripe` and `birdlife-netsuite` queries. Weekly is too often for numbers that Finance moves monthly.

### 2. Score it

Six lines, each a number with a direction against last week's review file. First week has no direction; say so.

| Measure | Query source | Target |
|---|---|---|
| Zeus open, and New | Salesforce | New at 0 by Friday |
| Zeus closed last 7 days | Salesforce | Steady or rising |
| Asana undated | Asana | Falling every week until 0 |
| Asana overdue | Asana | 0 |
| Blocked on a Mathew decision | Asana (Blocked section, title or comment says decision) | 0 older than 14 days |
| Deadlines inside 14 days | Security register | Each has an owner and a dated Asana task |

### 3. One learning

Exactly one. It must come from something that happened this week, name the evidence, and state the habit that replaces it. Not advice, not a reading list. Test: could Andrew read it and know what Mathew will do differently next week.

### 4. Delegations under the ladder

Three at most, one each for Andrew, Keith, Nina where the evidence supports it, aligned to IT-SEC-002 (cleanup before privilege; evidence before promotion). Each delegation is: the task, the DONE test they can run themselves, the date. Karishma is out of scope unless a Salesforce build is the blocker. Never delegate a Tier 2 Entra action; that stays with Mathew until the entra-admin write tier is consented.

### 5. Mathew's own three

What only Mathew can do this week: decisions the Blocked section is waiting on, Tier 2 actions, and any deadline inside 14 days. Dated.

### 6. Decisions needed

Anything the review surfaced that changes the estate or the doctrine (a wrong baseline, a routine over budget, a register row that is stale). One line each with a recommendation. Not made until the ADR exists.

## Writing rules

- Frank. Say when nothing moved. Say when a number in the doctrine is wrong and which layer was stale.
- No em dashes. Board Paper template only when the review is turned into a document for the ED or Board; the weekly file is markdown.
- Every open item with a date goes to Asana with an owner in the same session (`create_tasks`, project `1211042432693678`, section Backlog/Requests `1216556543715194` unless it is already in progress). Never create an undated task.
- Confidential: admin names and deadline dates stay in the file and in Asana, never in Teams or a Case.
- Close-out per `birdlife-prompting` step 5: update this skill or the affected system skill with any durable fact, put the learning in the log, tell Mathew what in memory is stale, and give three lines he can send the team.

## Verification queries learned by this skill

- Helpdesk backlog must be Zeus-scoped. On 7 Sep 2026 the org held 4,612 open Cases; 18 were Zeus. The "4,047 New" figure carried in `birdlife-core` since 8 Aug 2026 was org-wide and was never the ICT queue. Programme queues (Powerful Owl, General Enquiry, Swift Parrot Search, AOC, Conservation Campaigns) are business-owned and reported separately if at all.
- Asana Blocked items whose title ends "decision on responsibility" are blocked on Mathew, not on a system.
