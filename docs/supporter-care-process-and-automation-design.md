# Supporter Care in Salesforce — Process Documentation & Automation Design

**Org:** `birdlifeaustralia.lightning.force.com` (Zeus, production)
**Investigated:** 20 August 2026, live SOQL against production (read-only)
**Status:** DESIGN ONLY — nothing has been built or activated
**Author:** ICT (investigation run for Mathew Hema)

---

## Part 1 — How Supporter Care actually works today

### 1.1 Where Supporter Care lives in the Case model

The Case object is shared by the whole organisation (21 record types: citizen-science
counts, Ask Zeus ICT, Bequests, Conservation Campaigns, etc.). Supporter Care's
workhorse is the **General Enquiry Case** record type — by far the highest-volume
record type in the org:

| Record type (top 6, cases created last 365 days) | Volume |
|---|---:|
| **General Enquiry Case** (Supporter Care) | **14,757** |
| Bird Week Cases | 6,642 |
| Great Cocky Count | 1,870 |
| Birdata | 1,746 |
| eStore Enquiries | 1,686 |
| Ask Zeus (ICT) | 881 |

### 1.2 Intake channels (General Enquiry, last 365 days)

| Origin | Volume | Share |
|---|---:|---:|
| Email (email-to-case) | 9,574 | 65% |
| Phone | 1,571 | 11% |
| Web (web-to-case forms) | 1,443 | 10% |
| Outgoing | 611 | 4% |
| Voice Message | 511 | 3% |
| Internal | 474 | 3% |
| Social via Brandwatch (IG/FB/LI/X) | 334 | 2% |
| Letter | 236 | 2% |

Email is the process. Two of every three supporter-care cases arrive as an email
that becomes a Case in status **New**, owned by a queue.

### 1.3 Routing

- One active **assignment rule** ("Case Assignment") routes inbound cases to queues.
- Relevant queues: **Supporter Care**, Membership, Regular Giving, Merchandise
  Requests, eStore Support, Bequests, Major Gifts, General Enquiry, Info, Accounts
  (Finance), Filtered Spam (34 queues total on Case).
- An active before-save flow **"Auto update case record type by queue"** stamps the
  record type from the owning queue — so routing and record type stay consistent
  without agent effort. This is an important precedent: the org already trusts
  record-triggered flows on Case.

### 1.4 Case lifecycle

```
New ──▶ In Progress ──▶ (Pending | On Hold-Internal | Waiting Response-External)
                              │                        │
                              ▼                        ▼
                        Response Received ──────────▶ Closed
```

- **Closing is governed by a mandatory reason.** `Case_Closed_Reason__c` is required
  by validation rule, and the active flow **"Auto close case"** flips Status to
  Closed the moment a closed reason is saved. Agents never set Status=Closed
  directly — they set the reason and the flow does the rest.
- Active Case flows in production: Auto update record type by queue,
  Case bC - Web-to-Case, Auto close case, plus BQ and Bird Week record-type routers.
  There is **no acknowledgement, triage, or resolution automation** — everything
  between "case created" and "reason saved" is manual.

### 1.5 Categorisation — the weak point

Two fields classify supporter-care work:

- `Type` (~95 picklist values, drifted: "Membership" vs "Membership enquiry" vs
  "Membership Related" all live).
- `SC_Additional_Enquiry_Type__c` "Sub Type" (~200 values).

**73% of General Enquiry cases (10,719 of 14,757) have no Sub Type at all.** The
volumes below are therefore *floors* — true process volumes are likely 2–3× higher.

| Top tagged Sub Types (last 365 days) | Volume |
|---|---:|
| **Update Contact Details** | **674** |
| Update Recurring Payment | 497 |
| Membership Renewal | 430 |
| Once off Donation | 274 |
| Unsubscribe | 174 |
| Receipt + Donation Acknowledgement | 300 |

### 1.6 How cases get resolved (closures, last 365 days: 14,386)

| Closed reason | Volume | What it tells us |
|---|---:|---|
| Closed - No Action Required | 4,376 | Pure triage overhead |
| Closed - Email Sent | 3,199 | Templated reply, sent as-is |
| Closed - Phone Call | 1,411 | Call-back work |
| Closed - Resolved | 1,399 | Substantive work |
| Closed - Email Edited & Sent | 976 | Template + light editing |
| Closed - Autoreply | 632 | A human manually sent a canned reply |
| Closed - Internal Follow up | 573 | Handed inside the org |
| Closed - Abandoned | 530 | Never worked |
| Closed - Duplicate / Spam | 815 | Noise |

Read together: **~44% of all closures (6,353) involved no substantive supporter
outcome** (no-action, autoreply, duplicate, spam, abandoned), and another **29%
(4,175) were closed by sending a template email**. Under a third of Supporter
Care's case volume is genuinely bespoke work.

### 1.7 Current load

At time of investigation, open General Enquiry cases: **524 New** (unacknowledged),
199 In Progress, 118 Waiting-External, 41 other. Ownership of the open book is
heavily concentrated: Lee Christian 362, Supporter Care queue 126, Lorilee
Shepherd-Hartney 78, Ellie Bosic 45, Angelica Fazio 40, Fiona Cahill 38.

Sampled cycle times for "Update Contact Details" cases: 4 hours to 5 days from
created to closed — nearly all closing as *Email Sent / Email Edited & Sent /
Phone Call*.

---

## Part 2 — The repeatable process selected: **Update Supporter Contact Details**

### 2.1 Why this one

- **Highest tagged volume** (674/yr floor; realistically 1,500–2,000/yr given 73%
  of cases are untagged).
- **Fully deterministic**: the supporter states new details; the work is verify →
  update Contact → confirm → close. No judgement calls, no money movement.
- **Every step already happens in Salesforce** — no external system in the loop, so
  no integration user, no new licence (org is at 70/70), no FLS exposure.
- **The close mechanic is already automated** ("Auto close case" flow). The new
  build slots into a proven, live pattern instead of inventing one.
- Contrast: *Update Recurring Payment* (497/yr) is the next candidate but touches
  two payment systems (NPSP Recurring Donations + Payments2Us Recurring Payments)
  mid-decommission — wrong time. *Receipt resend* is blocked on the defective Conga
  stack. Contact details is the clean first move.

### 2.2 The manual process today (per case: ~10–15 min touch time, 1–5 days elapsed)

1. Agent opens the New case, reads the inbound email.
2. Finds the Contact (email match or C-number), verifies it's the right person.
3. Edits Contact fields; for address changes, edits the mailing address on the
   NPSP **Household** (Household Account model — address lives on
   `npsp__Address__c`, not just the Contact).
4. Spot-checks linked records (active membership, recurring gift) so mail/receipts
   go to the new address.
5. Writes or picks a confirmation email, sends it.
6. Sets Sub Type (usually skipped — hence 73% untagged) and Case Closed Reason;
   the auto-close flow closes the case.

---

## Part 3 — The automation build (design only, not executed)

### 3.1 Pattern

**"Triage-and-Guided-Resolve"** — the standard Service Cloud pattern, implemented
with the same tooling the org already runs:

```
┌───────────────────────────────────────────────────────────────────────┐
│  A. INTAKE (record-triggered flow, after save, on create)             │
│     General Enquiry + Origin=Email/Web                                │
│     • match Contact by inbound address (if not already matched)       │
│     • send auto-acknowledgement with Case Number (email template)     │
│     • keyword-classify subject/body → propose Type + Sub Type         │
└──────────────────────────────┬────────────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│  B. RESOLVE (screen flow, quick action on Case page)                  │
│     "Update Supporter Details"                                        │
│     1. show matched Contact + verification hints (C-number, email)    │
│     2. side-by-side: current values vs fields to change               │
│     3. agent types new values ONCE                                    │
│     4. flow updates Contact; address changes create a new             │
│        npsp__Address__c on the Household (history preserved,          │
│        NPSP propagates to all household members correctly)            │
│     5. warning panel if Contact has active recurring gift /           │
│        membership / open Plauti duplicate                             │
│     6. sends confirmation email (Lightning email template)            │
│     7. stamps Sub Type='Update Contact Details' and                   │
│        Case_Closed_Reason__c='Closed - Email Sent'                    │
└──────────────────────────────┬────────────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│  C. CLOSE — existing "Auto close case" flow fires (unchanged).        │
│     No new close logic. Reuses the org's proven mechanic.             │
└───────────────────────────────────────────────────────────────────────┘
```

**Deliberately human-in-the-loop.** The flow never writes Contact data straight
from an inbound email. Identity verification stays with the agent; the automation
removes navigation, re-keying, template hunting, and tagging — not judgement.

### 3.2 Components to build (all declarative, staging first)

| # | Component | Type | Notes |
|---|---|---|---|
| 1 | `SC Case Intake - Acknowledge & Classify` | Record-triggered flow (after save) | Entry: RecordType=General Enquiry, Origin Email/Web, created. Suppress for Filtered Spam queue and `Do_Not_Email__c` / `IsEmailBounce__c` cases |
| 2 | `SC - Acknowledgement` | Lightning email template | Case number, expected response time, org-address footer |
| 3 | `Update Supporter Details` | Screen flow + Case quick action | The guided resolve above |
| 4 | `SC - Details Updated Confirmation` | Lightning email template | Echoes what changed |
| 5 | Subflow `NPSP Address Change` | Autolaunched subflow | Creates `npsp__Address__c`, sets as default; reusable by future flows (membership renewal, deceased notice) |
| 6 | Report: "Update Details - flow vs manual" | Report | Measures adoption + cycle time before/after |

### 3.3 Landmines this design respects (org-specific)

- **Household Account model:** never edit `MailingAddress` directly on Contact for
  shared household addresses — go through `npsp__Address__c` (component 5) or
  household members silently desync.
- **Plauti dedupe:** exact First+Last+Email is the Contact match key. An email
  change alters the dedupe key — the flow surfaces open duplicate warnings before
  saving.
- **Downstream sync:** Contact edits propagate to Ortto (2.0M records synced) and
  are upsert-matched by Raisely on `Raisely_UUID__c` (unaffected by these edits).
  `AccountEngagementSync__c` is never touched (referenced by 3 flows, layouts,
  20+ reports).
- **Deceased notices are out of scope** — they're a distinct, sensitive process
  (44/yr tagged) and must not be handled by this flow.
- **Licence impact: none.** Runs as existing internal users. No integration user,
  no FLS change required.

### 3.4 Benefits

**Direct time saved (conservative, tagged volume only):**

| Lever | Volume/yr | Saving | Hours/yr |
|---|---:|---:|---:|
| Guided resolve replaces manual update+email+tag (10–15 → 2–3 min) | 674 (floor) | ~10 min/case | **~110–170 h** |
| Auto-acknowledgement removes "send holding reply" touches | ~9,600 email cases | 1–2 min where done manually | **~100+ h** |

At true volumes (untagged cases included) the first lever alone plausibly doubles.

**Structural benefits — arguably worth more than the hours:**

1. **Acknowledgement without backlog.** Every email/web supporter gets an instant
   case-numbered response — directly attacks the 524-case New backlog perception
   problem, independent of how fast the team resolves.
2. **The 73% untagged problem shrinks.** The flow stamps Sub Type on every case it
   resolves, and intake classification proposes tags on the rest. Within a year
   the team gets, for the first time, a truthful picture of what Supporter Care
   actually does — which is exactly what's needed to pick automation #2 and #3.
3. **Data quality up, risk down.** Address changes go through NPSP correctly every
   time; recurring-gift and duplicate warnings appear at the moment of edit, not
   after the next mail-out bounces.
4. **A reusable pattern.** Intake-classify + guided-resolve + reason-driven
   auto-close generalises directly to the next candidates: Update Recurring
   Payment (497/yr, after the Payments2Us decision), Membership Renewal (430/yr,
   after the membership rebuild), Receipt resend (post-Conga replacement),
   Unsubscribe (174/yr — near-fully automatable).
5. **Zero new close logic, zero new licences, zero integration surface.**

**Costs / effort estimate:** ~3–5 build days declarative work + templates, plus
UAT with Supporter Care and a 2-week measured parallel period. Build in the
staging sandbox first (remember: all record IDs differ between staging and
production — RecordTypeId and queue IDs must be re-mapped on deploy, and email
deliverability behaves differently in sandbox).

### 3.5 What is explicitly NOT in this design

- No auto-writing of supporter data from email content (identity risk).
- No auto-closing of anything a human hasn't approved (except the acknowledgement,
  which closes nothing).
- No changes to assignment rules, queues, record types, or existing flows.
- No AI/Einstein components in phase 1 — keyword classification is enough to
  start; revisit once tagging data improves.

### 3.6 Approval gates before any build

1. Mathew signs off on scope (this document).
2. Supporter Care lead (Lee Christian holds 362 of the open cases — the natural
   pilot user) validates the manual-process description in §2.2.
3. Build in staging → UAT → measured pilot with 2–3 agents → org-wide.

---

*All figures queried live from production on 20 Aug 2026. Record type, queue,
status, closed-reason and flow inventories are verbatim from the org — no values
invented. Nothing has been created, modified or activated in Salesforce.*
