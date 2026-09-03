---
name: birdlife-asana
description: Expert operator knowledge for BirdLife Australia's Asana workspace — the IT Operations Project Plan, the Salesforce Case email rule and its SPF blocker, the Better Impact implementation plan, the Salesforce developer onboarding board, and backlog hygiene governance. Use for any task involving Asana tasks, projects, sections, portfolios, assignments, due dates, or turning meeting actions and tickets into tracked work. Trigger on "Asana", "IT Operations Project Plan", "task board", "backlog", "sprint board", "assign to Keith", "move to Blocked", or a request to track or chase work.
---

# BirdLife Australia — Asana

## Workspace identity — verified

| Fact | Value |
|---|---|
| Workspace GID | **443963187362944** |
| Mathew's user GID | **1210202992538499** (mathew.hema@birdlife.org.au) |
| SF developer onboarding board | `app.asana.com/1/443963187362944/project/1211042432693678` |
| Better Impact board | "ICT Better Impact Implementation" — **private to the ICT Manager**, phased plan from 1 Aug 2026 |

Teams are organised by conservation programme and function, not by system. Verified team GIDs include: Advocacy/Policy `1210433663470343`, Beach-nesting Birds `1207819728138563`, Black-cockatoos `1207418217121010`, Campaign Management `1205098136351778`, Citizen Science `1204255684549550`, Coastal and Wetland Birds `1207947394108072`, Comms and Engagement `1204164938395809`, eCommerce `1211041491719670`, Finance `1211135286171472` and `1213223677662621` (**duplicate Finance teams — a cleanup item**), Finance & Business Improvement `1213223677662598`, Fundraising and Marketing `1204407434526263`, Global Authentication (login.birdlife.org.au) `1204617145641439`, Glossy Black-Cockatoo `1207321314790331`, Grasswrens `1207489426903543`, 2024 Nature Laws Project `1206587228062563`, Advanced Tier `1211029269244275`.

Also present and worth flagging as untidy: "BirdLife's first team" and "Caroline's first team" — default artefacts that should be archived.

## IT Operations Project Plan: the IDs (verified, mirrored from `birdlife-ict-assistant`)

Project gid **`1211042432693678`**. Sections and their gids:

| Section | gid | Meaning in the flow |
|---|---|---|
| Backlog/Requests | `1216556543715194` | Intake. Anything here without an owner and a date is unqualified |
| Scoping/Requirements Gathering | `1216556543715193` | Being defined; should have a decision date |
| In Development/Progress | `1216556543715191` | Actively worked; stale here 14+ days is a standup question |
| Awaiting Response | `1217146608838572` | Waiting on someone outside ICT; name who and chase weekly |
| Blocked | `1216556543715197` | Cannot proceed; every item names the blocker and its owner |
| Ready for Deployment | `1216556543715188` | Built, awaiting change window or sign-off (Nina for website) |
| Hypercare | `1211042432693693` | Deployed, being watched; time-box it |
| Done | `1211051239943465` | Complete |
| Meeting agenda (Marketing+ICT) | `1214293208933456` | Not a work state: agenda items for the joint meeting |

Live task memberships override this table if a section was renamed; `get_project`
or the `memberships.section` field on a `search_tasks` result is the check. Moving
a task to the wrong section is silently wrong, so verify by re-reading the task.

### Observed API behaviour
- `search_tasks({projects_any, completed:false, limit, opt_fields:"name,assignee.name,due_on,memberships.section.name,modified_at"})`
  returns `{data:[...]}`; sections come through `memberships[].section.{gid,name}`.
- `update_tasks` returns per-task `succeeded` / `failed` arrays. Check `failed`
  before claiming success; a partial batch is the normal failure mode.
- Section move: `update_tasks(tasks=[{task, add_projects:[{project_id, section_id}]}])`.
- `add_comment(task_id, text)` is a human-authored story; field changes are
  logged automatically and do not need a comment, but a decision does.
- Task link: `https://app.asana.com/1/443963187362944/project/1211042432693678/task/<gid>`.

### Board reading rules (how the console and the hygiene report judge it)
- **Attention** = Blocked, Awaiting Response, or due date passed, or no due
  date on anything outside Backlog.
- **Stale** = `modified_at` older than 30 days while not in Done.
- The recommendation per stale item is one of three words: close, delegate,
  or date it. Anything else is avoidance.

## The Salesforce Case → Asana email rule (open blocker)

**Intent:** Salesforce Case emails sent from `zeus@birdlife.org.au` to an `x@mail.asana.com` address auto-create tasks in the IT Operations Project Plan, addressed by putting `#IT Operations Project Plan` in the subject line.

**It does not work.** Asana rejects the email because the sender authenticates as salesforce.com while the From domain is birdlife.org.au. Root cause: **the birdlife.org.au SPF record does not authorise Salesforce's mail servers**, and Asana validates SPF/DKIM, so it reads the message as spoofing.

**Fix, three steps, none done:**
1. Add `include:_spf.salesforce.com` to the birdlife.org.au SPF TXT record.
2. Enable Enhanced Domains and configure DKIM signing in Salesforce Setup → Email → Deliverability.
3. Re-test Case email to Asana task creation.

**Do not treat step 1 as a small change.** It is a domain-wide email-authentication change affecting deliverability and anti-spoofing for all of birdlife.org.au. It goes through IT/security review, not an ad-hoc DNS edit. Say so every time it comes up.

## Backlog hygiene — the governance problem

From a live scan of 50+ open tasks (Aug 2026):

- **~30 tasks have no due date.**
- A block of **~25 Salesforce migration tasks created 7 January 2026 was last touched in a bulk edit on 15 July** — six months of drift.
- **5 auto-generated "Consider delegating X's tasks" items** unactioned.
- **4 "update your goals" reminders** unactioned.

Stated plainly: this backlog would fail Mathew's own governance review. The Monday hygiene report is the designed remedy — tasks with no due date, tasks untouched 30/60/90+ days, unactioned delegation prompts, and a blunt "close, delegate, or date it" recommendation per stale item.

**Impact on people, which is the reason it matters:** Keith, Karishma and Nina work off a board that does not reflect reality, so standups are spent reconstructing status instead of resolving blockers. Fixing the board shortens their meetings, not just Mathew's.

## Enterprise app hygiene

Entra holds **6-7 duplicate Asana enterprise-app registrations**. Consolidate as part of the app access review (next due 19 Sep 2026).

## Available tooling

`mcp__Asana__*` supports full read plus create/update/delete on tasks, comments, project status updates and project creation. `search_objects` and `search_tasks` are the efficient entry points. `get_my_tasks` for Mathew's own list.

**Zapier also holds an Asana connection (41 actions, 1 connection).** Two paths into the same workspace is a duplication risk — prefer the native MCP for anything interactive, and reserve Zapier for scheduled/triggered automation.

## Operating rules
1. **Read the project's sections before moving anything.** Never guess a section GID.
2. **Every task you create gets an owner and a due date.** Creating undated tasks in this workspace makes an existing problem worse.
3. When asked to "track" something, ask whether it belongs in the IT Operations Project Plan or a programme team's board before creating it in the wrong place.
4. When a Salesforce Case is being turned into an Asana task manually, note that the automated route is blocked on SPF — do not let the manual workaround quietly become permanent.
5. Do not create new teams. There are already two Finance teams and two "first team" artefacts.
