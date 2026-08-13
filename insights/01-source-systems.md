# L0 — Source Systems

Inventory of every system feeding the insights model: what it is the system of
record for, how data gets out, and the caveats that survive into every downstream
number. Figures are point-in-time (Jun–Aug 2026) unless stated.

## System-of-record rulings

When two systems disagree, the ruled system of record wins and the discrepancy is
reported as a reconciliation metric — never silently averaged.

| Entity | System of record | Everything else is |
|---|---|---|
| Supporters, donors, households | Salesforce (NPSP Household model) | Ortto/Raisely/Woo = copies |
| Gifts, opportunities, pledges | Salesforce | NetSuite = financial posting of same |
| Membership **status** | Salesforce (today via Payments2Us `Active_BL_Member__c`; future `Membership__c`) | WooCommerce = transaction front end |
| Card/direct-debit transactions | Stripe (`acct_1PaqQkEdZ08H7Yxq`, livemode) | SF Payments = synced copy |
| General ledger, AP/AR, bank | NetSuite (account 3440597, subsidiary id **2**) | — |
| Payroll | NetSuite / Infinet Cloud ZonePayroll (~128 staff, one pay run) | Employment Hero holds a *second, manually maintained* copy |
| Employee master (HR) | Employment Hero (join key: worker code **BLA###**) | Entra `employeeId` = downstream sync target |
| Identity & access | Microsoft Entra ID (tenant `2b431a7b-…`) | — |
| ICT work / project work | Asana (workspace `443963187362944`) + Salesforce Cases (record type `Zeus`) | — |
| Marketing audience & engagement | Ortto (2,038,253 records, 15.9M activities) | Pardot decommissions 31 Aug 2026 |
| Volunteering | **No system of record today.** GW_Volunteers installed but empty; Better Impact implementation in flight | `BetterImpact_ID__c` populated on **1** contact |

## Systems

### Salesforce — "Zeus" (`birdlifeaustralia.my.salesforce.com`)
- **Role:** CRM and operational spine — fundraising, memberships, advocacy,
  payments, and the ICT helpdesk. 424 objects, NPSP Household model, Enterprise
  edition, AUD/AEST.
- **Extraction:** SOQL via the Salesforce Production MCP connector. Read-only for
  insights work.
- **Key namespaces:** `npsp/npe01/npe03` (donations, recurring donations,
  payments), `AAkPay` (Payments2Us — 82 objects, memberships & direct debit),
  `movedata` (Raisely ingest), `dupcheck` (Plauti), `stripeGC`.
- **Standing caveats (full detail in the data-quality register):**
  - Number fields default to 0 — `!= null` population counts are lies. Always
    `!= null AND != 0` or sample rows.
  - `Subscription__c` (Keith Tsui, unmanaged) name-collides with
    `AAkPay__Subscription__c`. Always qualify the namespace.
  - Case reports without `RecordType.DeveloperName = 'Zeus'` count 19 record
    types across the whole organisation.
  - Supporter ID conventions: Contacts `C-…`, Household Accounts `N-…`.
  - Licence position 70/70 full licences — any design needing a new integration
    user must name the licence it frees.

### NetSuite (OneWorld, account 3440597)
- **Role:** Finance system of record — GL (413 accounts, 587,260 journal lines
  back to Dec 2016), AR/AP, banking (60–90+ accounts), fixed assets,
  project/grant accounting, payroll, AASB 16, GST/BAS.
- **Extraction:** SuiteQL (`ns_runCustomSuiteQL`) — always scoped to
  **subsidiary id 2**. Do not add saved searches (115 of 212 never run).
- **Segmentation for department reporting:** Department (86 active of 114),
  Class/"Class/Project" (312 active of 952 — ~67% inactive), Location/Branch (36
  of 38; branch-code mismatches MOR, BUN, SHI), Project/Job (~281 active of 831).
  A naming convention `[PROGRAM]_[FUNDER]_[TYPE]_[FYSTART FYEND]` is proposed from
  FY2026-27 but not yet enforced — department-level splits are only as good as
  this cleanup.
- **Standing caveats:** bank accounts 11103/11104 last reconciled 31 Mar 2022
  (378 + 120 unmatched items); SF→NS is a manual monthly CSV; no CRM/fundraising
  /BI integration exists in NetSuite at all.

### Stripe (`acct_1PaqQkEdZ08H7Yxq`, **livemode**)
- **Role:** Payment processor for WooCommerce (card + BECS direct debit),
  ~A$11,108.70/month.
- **Extraction:** `stripe_api_read` / `stripe_api_search` only. Writes are real
  donor money and are out of scope for this model.
- **Standing caveats:** Refund IDs (`re_xxx`) are **not** synced to Salesforce —
  refund analysis must start in Stripe and match back by amount/date. A payout
  webhook support thread was unresolved as at Aug 2026 — payout data may be
  incomplete.

### WordPress / WooCommerce (`birdlife.org.au`, WP Engine `birdlifeaus`)
- **Role:** Website, e-commerce (~6,466 orders: 6,331 completed, 70 refunded,
  60 failed), and the future membership front end (Blitzm build).
- **Extraction:** WooCommerce REST API (`/wp-json/wc/v3`) — **no MCP connector**;
  API keys must come from environment variables, never inline (see the credential
  exposure note in the root README).
- **Standing caveats:** miniOrange→SF sync fails on ~10.3–10.5% of attempts (FLS
  gap on `npe01__Opportunity__c`); the SF-Id write-back gap creates duplicates;
  the refund flow writes invalid picklist values and positive refund payments.
  Order counts from WooCommerce and Opportunity counts from SF will **never**
  match exactly — the delta is a quality metric, not noise.

### Employment Hero
- **Role:** HR system of record. Worker code **BLA###** is the join key to
  NetSuite payroll and (via the Logic App) to Entra `employeeId`;
  `company_email` ↔ Entra `mail`.
- **Extraction:** no MCP connector. The `logic-emphero-entra-sync` Logic App is
  deployed but **0 succeeded / 2 failed runs** (EH permission 403). The native
  EH→M365 add-on is connected and **overwrites, never merges**.
- **Standing caveats:** EH and NetSuite payroll are maintained twice with no
  live link — the KB calls this the biggest data-integrity risk in the landscape.
  Expense Categories in EH are empty.

### Microsoft 365 / Entra ID (tenant `2b431a7b-9a21-4b53-8943-4a10ff69970d`)
- **Role:** Identity, email, SharePoint/Teams, device management (Intune),
  security telemetry (Defender, Secure Score).
- **Extraction:** M365 MCP covers mail/calendar/SharePoint/Teams only. Directory,
  Intune, Defender and CA data come from the local read-only Entra MCP
  (`C:\azureintegration`), Graph PowerShell, or portal exports.
- **Standing caveats:** 2,707 users but ~2,700 are `#EXT#` guests — **exclude
  guests from any people-matching logic**. Security posture figures are dated
  19–30 Jun 2026. Named per-user MFA weakness data is confidential and never
  goes into shared documents.

### Asana (workspace `443963187362944`)
- **Role:** Work management — IT Operations Project Plan, programme team boards,
  Better Impact implementation plan (private board).
- **Extraction:** Asana MCP (`search_tasks`, `get_project`). Read the project's
  sections live; never guess section GIDs.
- **Standing caveats:** ~30 open tasks with no due date and a 25-task block
  untouched for six months — "tasks by due date" metrics are structurally
  incomplete until hygiene improves. Two duplicate Finance teams exist.

### Ortto (via Zapier; native SF data source "Birdlifeaustralia")
- **Role:** Marketing automation replacing Pardot (hard stop **31 Aug 2026**).
  2,038,253 records, 15.9M activities; Contact filter `Ortto Inactive is false`;
  **Lead not synced**.
- **Standing caveat:** retention limit already reached — blocks expanded sync.

### Raisely (via MoveData → SF API)
- **Role:** Community/peer-to-peer fundraising. Upserts on `Raisely_UUID__c`.
- **Standing caveats:** one Raisely campaign maps to one SF Campaign — online
  gifts code to the top-level appeal, not segment campaigns, so campaign-level
  attribution is coarse by design. API writes bypass UI duplicate rules.

### Long-tail systems (Zapier-only reach)
| System | Data | Note |
|---|---|---|
| LearnUpon (`learn.birdlife.org.au`) | Training enrolments | Webhook fires on **enrolment only, not completion** — completion metrics are not currently measurable. Hook owned by keith.tsui's Zapier account |
| Humanitix | Event ticketing | 1 action, connected as mathew.hema |
| Award Force | Awards/grants applications | 33 actions |
| Campaign Monitor | Email campaigns | Legacy alongside Ortto |
| Google Analytics 4 | Web analytics | Connected as mathew.hema.admin |
| BugHerd / Content Workflow | Web QA / content ops | Peripheral |
| Zoom (`ZVC` in SF) | Meetings/webinars | Attendance data available in SF |

Zapier itself is transport, not a source. Pardot's two Zapier connections die
with the 31 Aug 2026 decommission.

## Cross-system key map (identity crosswalk)

The joins that hold the whole model together. Anything not in this table joins
by fuzzy match (name/email) and must be labelled as such.

| From | To | Key | Reliability |
|---|---|---|---|
| WooCommerce order | SF Opportunity | post meta `salesforce_Opportunity_ID` | **Leaky** — write-back gap leaves "None" on some paid orders |
| Raisely person | SF Contact | `Raisely_UUID__c` (external ID upsert) | Good |
| Stripe charge | SF Payment | via `stripeGC` sync / balance transaction | Good for charges; **absent for refunds** |
| SF Opportunity/GAU | NetSuite GL code | GAU→GL mapping (Master Technical Guide §7) via monthly CSV | Manual, monthly latency |
| Employment Hero employee | NetSuite employee | worker code **BLA###** | Ruled key; manually maintained both sides |
| Employment Hero employee | Entra user | `company_email` ↔ `mail`; `employeeId` once Logic App works | Sync broken (403) as at Aug 2026 |
| SF Case (Zeus) | Asana task | **none** — a human types it into `ICT Priorities.xlsx`; email rule blocked on SPF | Weakest join in the landscape |
| SF Contact | Better Impact volunteer | `BetterImpact_ID__c` | Populated on **1 of 479,620** contacts — unusable until BI implementation |
| SF Contact | Ortto person | Ortto native SF source | Good; Leads excluded |
