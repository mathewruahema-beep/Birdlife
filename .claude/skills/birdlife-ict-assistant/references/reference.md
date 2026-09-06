# BirdLife ICT Assistant — Reference

Concrete IDs, picklist values, write mechanics, and per-issue playbooks. Load this
when you need exact values; the SKILL.md body has the workflow and rules.

## Table of contents
1. Salesforce — Cases (identifiers, statuses, close mechanics, write examples)
2. Salesforce — owners (and the duplicate-user caution)
3. Asana — project and section IDs, write mechanics
4. Microsoft 365 / Entra playbooks (Tier 2 — prepare, human runs)
5. Common Salesforce Case playbooks (Tier 1)

---

## 1. Salesforce — Cases

- **Helpdesk record type**: "Ask Zeus", `DeveloperName = 'Zeus'`, Id `012I80000004IPnIAM`.
  Scope the queue with `WHERE RecordType.DeveloperName='Zeus' AND IsClosed=false`.
- **Case link (for humans)**: `https://birdlifeaustralia.lightning.force.com/lightning/r/Case/{Id}/view`

### Status picklist (exact API values)
`New` · `In Progress` · `Pending` · `On Hold-Internal` · `Waiting Response-External`
· `Response Received` · `Closed`

### Priority
`High` · `Medium` (default) · `Low`

### Closing a Case — both fields required
Validation rule blocks close without a reason. Set **both**:
- `Status = "Closed"`
- `Case_Closed_Reason__c` = one of:
  `Closed - Resolved`, `Closed - Resolved First Call`, `Closed - Email Sent`,
  `Closed - Email Edited & Sent`, `Closed - Phone Call`, `Closed - No Action Required`,
  `Closed - Internal Follow up`, `Closed - Duplicate`, `Closed - Spam`,
  `Closed - Abandoned`, `Closed - Autoreply`, `Closed - Returned Letter`.

### Categorisation fields (help reporting — set when closing if empty)
- `Type` — high-level (Admin, Troubleshooting, IAM, New User, Departing Staff,
  New Feature, Purchase/Renew, Spam, …).
- `SC_Additional_Enquiry_Type__c` — the system/sub-type (Software, Mailbox Access,
  Phishing Email, Email Distribution Group, Salesforce, Website, Canva, Asana,
  Google Workspace, Teams/SharePoint Access, Hardware, …). ~48% of cases have this
  blank — filling it on close quietly improves every future report.

### Write mechanics
Update a Case (only changed fields):
```
updateSobjectRecord(sobject-name="Case", id="<CaseId>",
  body={ "Status": "Closed", "Case_Closed_Reason__c": "Closed - Resolved" })
```
Add an **internal comment** (audit note / working note) — create a CaseComment child:
```
createSobjectRecord(sobject-name="CaseComment",
  body={ "ParentId": "<CaseId>", "CommentBody": "…", "IsPublished": false })
```
(`IsPublished=false` keeps it internal. There is also a `Comments` textarea field on
the Case itself, but CaseComment gives a threaded, timestamped, attributed trail —
prefer it.)

Reassign owner: set `OwnerId` to a User Id or a Queue Id — **but resolve it first**
(next section).

---

## 2. Salesforce — owners (duplicate-user caution)

Each ICT staffer has **multiple active User records** — do not hardcode. Always
resolve at write time and, if more than one active match, show them and let the user
choose. Query:
```
SELECT Id, Name, IsActive, Username FROM User WHERE Name = 'Keith Tsui' AND IsActive = true
```
IDs observed owning real Ask-Zeus cases this session (use as the *likely* match, still
confirm on reassign):
- Andrew Dunn — `0055g00000DqUq9AAF` (also active: `0055g00000DqbMVAAZ`, `005RF000006cU6TYAU`)
- Keith Tsui — `005I8000000J4L5IAK` (also active: `005RF000002E8qzYAC`)
- Mathew Hema — `005RF000003ahkfYAA` (also active: `005RF000007mSM9YAM`)
- Nina Lewis — active: `005I8000000J5EtIAK`, `005RF000001n46kYAA` (confirm which)

The duplicate accounts are themselves worth flagging to Mathew as a cleanup item.

Live tie-break (used by the console's `case_assign`): among the active matches, the one
owning Zeus cases in the last 180 days is the working account:
```
SELECT OwnerId, COUNT(Id) c FROM Case
WHERE RecordType.DeveloperName = 'Zeus' AND OwnerId IN ('<id1>','<id2>')
  AND CreatedDate = LAST_N_DAYS:180 GROUP BY OwnerId
```
One owner with cases: use it. Zero or several: present candidates (Username + count) and
require an explicit choice. Log the assignment with an internal CaseComment.

---

## 3. Asana — IT Operations Project Plan

- **Project gid**: `1211042432693678`
- **Section gids**:
  - Meeting agenda (Marketing+ICT): `1214293208933456`
  - In Development/Progress: `1216556543715191`
  - Awaiting Response: `1217146608838572`
  - Scoping/Requirements Gathering: `1216556543715193`
  - Blocked: `1216556543715197`
  - Ready for Deployment: `1216556543715188`
  - Hypercare: `1211042432693693`
  - Backlog/Requests: `1216556543715194`
  - Done: `1211051239943465`

### Write mechanics
Move a task to a section (and/or set fields):
```
update_tasks(tasks=[{ "task": "<gid>",
  "add_projects": [{ "project_id": "1211042432693678", "section_id": "<sectionGid>" }] }])
```
Complete a task: `update_tasks(tasks=[{ "task": "<gid>", "completed": true }])`
Reassign / set due date: `assignee`, `due_on` in the same object.
Add a discussion comment (human-authored note, not an auto-logged field change):
```
add_comment(task_id="<gid>", text="…")
```
Create a task in a section:
```
create_tasks(default_project="1211042432693678",
  tasks=[{ "name": "…", "notes": "…", "section_id": "<sectionGid>", "assignee": "<email|gid>" }])
```
Task link: `https://app.asana.com/1/443963187362944/project/1211042432693678/task/<gid>`

---

## 4. Microsoft 365 / Entra playbooks (Tier 2 — prepare, a human runs)

The connected M365 tool is productivity-scoped (mail/calendar/Teams/SharePoint read +
draft). It **cannot** do tenant admin. For the actions below, produce the ready-to-run
remediation and update the Case; an ICT admin executes. If an Entra/Graph admin
connector is added later, these become Tier 1.

Connect once per admin session:
```
Connect-MgGraph -Scopes "User.ReadWrite.All","Group.ReadWrite.All","UserAuthenticationMethod.ReadWrite.All","Directory.ReadWrite.All"
```

- **Password / MFA reset** (security — always hand the decision to a human):
  Reset MFA methods and require re-registration; check risky-sign-in first via the
  Entra sign-in logs. Prepare the steps; do not execute.
- **Mailbox access** (delegate/shared): `Add-MailboxPermission` /
  `Add-RecipientPermission` (Exchange Online PowerShell). State the access type
  (Full Access vs Send As) and that it's approved by People/manager.
- **Distribution list changes**: `Add-DistributionGroupMember` /
  `Remove-DistributionGroupMember` for the named DL.
- **Onboarding a new starter**: create the user, assign licence (confirm which SKU),
  add to the right groups/DLs, set manager. Draft as a checklist tied to the Case;
  pair with the Employment Hero starter record if that feed exists.
- **Offboarding a leaver** (security-critical): on the last day — block sign-in /
  disable account, convert mailbox to shared, reclaim the licence, remove from
  groups/DLs, revoke sessions, and note SaaS apps outside SSO that need manual
  removal. This is the highest-value checklist to standardise.
- **Licence assign/reclaim**: `Set-MgUserLicense`. Reclaiming departed-staff licences
  is a recurring win.

## 5. Common Salesforce Case playbooks (Tier 1 — you execute after confirm)

- **Program Engagement / record requests** (e.g. "create PE for volunteer course"):
  create the requested records with `createSobjectRecord`, confirm the fields with the
  requester if ambiguous, comment + close with `Closed - Resolved`.
- **Portal / Birdata / BOF / LMS login issues**: usually a Portal-email vs
  Preferred-email mismatch on the Contact. Diagnose by reading the Contact; the fix
  (portal-email data change) may be Tier 1, but the *policy* of who owns portal email
  is an open P&E decision — note it, don't invent it.
- **"Waiting on requester"**: set `Status = "Waiting Response-External"`, and when they
  reply the system sets `Response Received` — pick it back up then.
- **Duplicate / spam**: close with `Closed - Duplicate` or `Closed - Spam`; set `Type`
  accordingly.
- **Feature request / dev work**: if it's really project work (not a quick fix), create
  or link an Asana task in the IT Operations project and close the Case with a note
  pointing to the task, so it's tracked where the work actually happens.

---

## 6. Institutional memory (as of 2026-08-04 — keep appending)

Durable context so you don't re-discover it each session. A fuller knowledge base lives
in the user's `birdlife_ict_knowledge_base.md`.

**What you can reach (updated 3 Sep 2026):** Salesforce Production and Salesforce Staging
(write), NetSuite (SuiteQL, reports, records), Stripe (**five livemode accounts**:
eCommerce `acct_1PaqQkEdZ08H7Yxq`, Memberships `acct_1DE94cH9l9pxYNgx`, Ausbirdfund
`acct_1DffVqH1WeNbvypj`, BLP `acct_1OKucyFMYRhNDz9n`, eStore/AOC `acct_1NfHuCCj2I4WmWMH`),
BirdLife UAT WordPress (MCP adapter, WooCommerce read + write, UAT only), Asana, Canva,
Cloudflare (Developer Platform only, no DNS/WAF), Miro, Zoom, Granola, Atlassian, Google
(Gmail/Calendar/Drive), Zapier, GitHub, M365 (productivity only, NOT admin), plus Campaign
Monitor / Ortto / Raisely / Humanitix via Zapier (thin). AWS + Entra are desktop-bridge only.
The earlier "WooCommerce read-only key" is superseded by the UAT connector and its keys
are on the credential watchlist (rotation not verified).

**Salesforce is the hub — most systems write into it and are reachable via the SF connector:**
Stripe ×3 accounts (eCommerce/Memberships/Ausbirdfund) via `stripeGC` (sync health in
`stripeGC__Sync_Log__c.stripeGC__Error_Details__c`); Raisely via **MoveData**
(`movedata__Contact_Platform_Key__c`, ~19,447 Raisely mappings — Raisely donations ARE in SF);
WooCommerce via miniOrange; Payments2Us (`AAkPay__*`, also syncs to Xero); LearnUpon, Pardot,
Plauti, Conga, Volunteers, Zoom, NPSP (recurring donations `npe03__Recurring_Donation__c`).

**Blindspots — don't claim to cover these:** Microsoft Entra/Exchange/Intune/Defender admin
(the #1 gap — ~⅓ of tickets need it); Salesforce config (Metadata API); external *engine*
run-health (miniOrange/MoveData/Zapier pipe — lagging only); the two un-connected Stripe accounts'
*direct* API (reachable via SF); Zapier zap failures (route them to a SF Case Type='System
Notification' via Zapier Zap Manager); the WordPress fleet beyond the main site; Ortto deep sync.
If asked to monitor/fix these, say plainly what's connected vs not and name what's needed.

**Live findings to remember (raise if relevant, don't silently trip over):**
- WooCommerce "Read" API keys can actually WRITE (permission-enforcement gap) — WooCommerce-specific; Gravity Forms enforces correctly.
- DMARC is `p=reject` but `pct=10` — only 10% enforced; the fix is `pct=100` after verifying senders.
- Gravity Forms → SF Web-to-Case creates cases fast but often orphaned (`ContactId` null) — matching-config issue.
- Each ICT staffer has multiple active SF User records — always confirm before reassigning.
- ~48% of zeus cases have no sub-type — fill it on close to improve reporting.
- GA4 is not accessible to any org-held Google account (ownership/governance risk).

**zeus queue shape:** ~877 cases/12mo, falling (−32% YoY). Mostly Admin (36%) + Troubleshooting
(32%) + identity lifecycle (20%). The tools that would unlock the most are Entra/Graph admin
write and an Employment Hero HR feed.

**Data-flow health fingerprint (WooCommerce order fully synced):** carries `transaction_id`
(Stripe) + `salesforce_Opportunity_ID` + `salesforce_npe01__OppPayment__c_ID` +
`mo_sf_sync_line_item_ids` (miniOrange). Missing any on an order older than a few minutes =
broken sync worth flagging.

**When you learn something new and durable** (a new ID, a resolved finding, a new system, a
changed process), tell the user it's worth adding to the knowledge base / this reference so
the memory keeps compounding — you can't self-update the saved skill, but the user can re-save
an updated copy.
