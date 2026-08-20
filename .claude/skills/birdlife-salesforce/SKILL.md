---
name: birdlife-salesforce
description: Expert operator knowledge for BirdLife Australia's Salesforce org ("Zeus") — NPSP/Household model, Payments2Us, Conga, miniOrange/WooCommerce sync, Raisely/MoveData, Pardot-to-Ortto decommission, Plauti dedupe, the ICT helpdesk Case model, and the membership rebuild. Use whenever a task touches Salesforce records, SOQL, Cases, Opportunities, Contacts, memberships, donations, receipting, duplicates, sandbox/staging deployment, Salesforce security or licences, or any integration that reads from or writes to Salesforce. Trigger on "Zeus", "SOQL", "NPSP", "Payments2Us", "AAkPay", "Conga", "miniOrange", "Raisely", "Ortto sync", "recurring donation", "EOFY receipt", "membership object", "duplicate contacts", or a Case number like 00137xxx.
---

# BirdLife Australia — Salesforce (Zeus)

You are operating a 424-object, 4,600-report NPSP org that runs fundraising, memberships, advocacy, payments AND the internal ICT helpdesk. Nothing here is greenfield. Assume every change has a downstream consumer you have not thought of.

## Org identity — verified facts

| Fact | Value |
|---|---|
| Production | `birdlifeaustralia.lightning.force.com` / API `birdlifeaustralia.my.salesforce.com` |
| Setup | `birdlifeaustralia.my.salesforce-setup.com` |
| Staging sandbox | `birdlifeaustralia--staging.sandbox.my.salesforce.com` |
| Edition / instance | Enterprise, AUS92, AUD, AEST (GMT+10) |
| Data model | NPSP (Nonprofit Success Pack), **Household Account model** |
| Org created | 25/01/2021 by Reza Torkman |
| Objects (live count) | **424 returned by getObjectSchema index**; KB records 439 custom objects — reconcile before quoting a number |
| Case intake | `zeus@birdlife.org.au` — 53k email-origin cases, 115k closed all time |
| Mathew's user | `005RF000003ahkfYAA`, profile System Administrator `00e5g000001jYQ6AAM`, role node **CEO**, alias `mhema` |

**Licence position is a hard constraint: 70 full licences, 70/70 consumed.** There is zero headroom. A new staff member or a new integration user requires freeing one first. Never propose a solution that needs a new full licence without saying which licence gets released.

## Managed packages — know the namespace before you query

| Namespace | Package | What it owns |
|---|---|---|
| `npsp` / `npe01` / `npe03` / `npe4` / `npe5` | NPSP v14.x | Donations, Recurring Donations, Payments (`npe01__OppPayment__c`), Allocations (`npsp__Allocation__c`), Affiliations, Relationships |
| `AAkPay` | Payments2Us (AAkonsult) — **82 objects** | Payment forms, direct debit batches, Recurring Payments, `AAkPay__Subscription__c` memberships, Xero bridge objects |
| `APXTConga4` / `APXT_BPM` / `APXT_CongaSign` | Conga Composer, Batch, Sign | Receipts and letters. Being replaced by native SF |
| `md_npsp_pack` / `movedata` | MoveData NPSP | Generic upsert framework — this is how Raisely writes in |
| `pi` / `sl_flow` | Pardot / Account Engagement v5.10 + Sercante | **Being decommissioned — hard stop 31 Aug 2026** |
| `dupcheck` | Plauti Duplicate Check — 17 objects | Dedupe |
| `GW_Volunteers` | Volunteers for Salesforce | **Installed but effectively empty** |
| `stripeGC` | Stripe | Balance transactions, sync log |
| `ZVC` | Zoom for Salesforce — 18 objects | Meetings, webinars, call logs |
| `LearnUponP` | LearnUpon LMS | Enrolments |
| `pmdm` | Program Management Module | Programs, Services, Service Deliveries |
| `agf` — **97 objects** | Agile Accelerator | Almost certainly unused bloat. Candidate for removal |
| `bofc` — 27 objects | BOFC admin toolkit | Metadata bulk ops |
| `sf_devops`, `dlrs`, `ZeroBounce`, `Field_Trip`, `uar`, `Streams` | Misc | DevOps Center, Declarative Rollups, email validation, field usage, user access review |

**Naming collision trap:** Keith Tsui built an unmanaged `Subscription__c` / `Subscription_Member__c` (8 + 421 test records). It name-collides with managed `AAkPay__Subscription__c`. Anyone querying "Subscription" without checking the namespace hits the wrong object. Always qualify.

## Query discipline — two rules that will save you

1. **Never trust `!= null` counts in this org.** Number fields default to 0, so `!= null` returns a false 100% populated reading. `BetterImpact_ID__c` read as 479,613 of 479,620 populated; the real figure is **1**. `AAkPay__Member_Type__c` reads 100% populated and is genuinely 100% blank. Count with `!= null AND != 0`, or sample rows.
2. **Supporter ID conventions:** Contacts prefix `C-` (e.g. `C-0491796`), Household Accounts prefix `N-` (e.g. `N-15613`).

## ICT helpdesk / Case model

Cases arrive by email to `zeus@birdlife.org.au`. Two dashboards were built 1-2 Jul 2026 and sit in **Mathew Hema's Private folder** (`01ZRF00000FcXoj2AF` Zeus Helpdesk Dashboard; `01ZRF00000FcYsr2AF` Improvement Metrics), backed by 10 Case reports. They should be moved to a shared folder — private dashboards are a single point of failure and a governance finding waiting to happen.

**The live problem: ~3,600 cases in "New" against 165 "In Progress" (1 Jul 2026).** That is an acknowledgement bottleneck, not a resolution bottleneck. Top closers historically: Angelica Fazio (6,300), Alison Bolding (3,800).

**Known incident to never repeat (29 Jun 2026):** the "All Open Cases" list view had been filtered to `Case Owner Alias = mhema`, hiding every other technician's cases. It now filters only on `Closed = False`. If someone reports "cases have vanished", check the list view filter first.

For actual Case statuses, the mandatory close reason, queue names and record types, defer to the installed **`birdlife-ict-assistant`** skill or query the live org. Do not invent picklist values.

Case Status field-history tracking should be enabled — without it you cannot measure time-to-acknowledge, which is exactly the metric the backlog demands.

## Integrations — where the bodies are buried

### miniOrange "Object Data Sync For Salesforce" (WooCommerce ↔ Salesforce)
Real-Time Post/Order Sync **enabled** both envs; User Sync and Scheduled Sync **disabled**. The pattern is upsert with the SF record ID written back to WordPress post meta (`salesforce_Opportunity_ID`).

**Two live bugs:**
- **Write-back gap** — the plugin sometimes fails to write the returned SF Id into post meta ("Salesforce UUID: None" observed on two real paid orders). Missing meta means the next status change creates a duplicate. Always run a deliberate write-back test before trusting a new mapping.
- **Field-level security gap on `npe01__Opportunity__c` causes ~10.3-10.5% of sync attempts to fail outright, confirmed on BOTH staging and production.** Grant FLS to the integration user on every new field BEFORE first sync. This is the single most repeated failure in this org.

**Refund/cancellation flow is materially broken** (verified staging order #22553):
- Refunds create a NEW Payment with a **positive** amount, `Paid = false`, Type `shop_order_refund` — the ledger shows two positive payments.
- Opportunity StageName is set to the raw WooCommerce string `"refunded"` / `"cancelled"` — not valid picklist values.
- `TotalOrderAmount__c` unchanged; OpportunityLineItems keep positive values.
- Stripe Refund ID (`re_xxx`) is **not** synced — refunds are untraceable from Salesforce.
- `Subscription_Member__c` is never deactivated — ex-members look active.
- `shop_subscription` is not mapped at all.

This is Karishma Soni's Week-4 decision gate: fix or formally accept.

**Prod vs staging drift:** Woo Members mapping, Pricebook automation, `Automatic_Renewal__c`, `npsp__Type__c` and duplicate-detection keys exist **only in staging**. Production has **no** duplicate-check keys on Product/Opportunity mappings.

**Webhook keys were leaked in plaintext across three documents** (prod access key `7cf2…`, staging `8d8f…`). Rotate via "Regenerate Access Key" and scrub the docs. Treat this as unremediated until proven otherwise.

### Raisely → Salesforce (via MoveData)
There is **no "Raisely" flow**. Raisely calls the SF API as the Raisely Integration User (profile "Raisely - Connected User", account `birdlife@salesfix.com.au`), upserting on external ID `Raisely_UUID__c`.

- `Contact.Raisely_Access_Token__c` is a **credential embedded in a clickable formula URL** (`Update_Card_Details_Raisely__c`). Treat as sensitive.
- **Do not modify MoveData managed flows** (50+ of them). Org rules live in the unmanaged `[MoveData Extension]` layer — e.g. DonationRecurringOffsetDays = 13.
- Structural limit: a Raisely campaign links to only ONE SF Campaign, so online gifts code to the top-level appeal, not segment campaigns. Proposed workaround is a Donor Segment field.
- Flow "Opportunity: Community Fundraising Donor [Checked]" is **INACTIVE** — that checkbox has been stale for every donation since deactivation.

### Ortto
Independent SF data source "Birdlifeaustralia": 2,038,253 records, 15.9M activities. Contact filter `Ortto Inactive is false`. **Lead not synced (0 fields).** Retention limit already reached, which blocks expanded sync. Plan: Professional, effective $1,763.20/mo, 12-month commitment $21,158.40, renewal 12 Aug 2027.

### Pardot decommission (live, urgent)
Hard cutover **31 Aug 2026**. `AccountEngagementSync__c` (non-namespaced, on both Contact and Lead) must be **RETAINED** — it is referenced by 3 flows, the Contact Lightning layout and 20+ reports. 13 triggers on Contact/Lead need regression testing including Pardot's LogContactChange / LogLeadChange. Open decisions: Ortto retention upgrade, 238-vs-287 field discrepancy, whether to sync Lead, final uninstall approval for `pi__` + `sl_flow`.

### Conga receipting — mission critical, currently defective
Conga Batch-0008 runs **daily 7:00 PM AEST, 50-200 donation receipts/day**. Footprint: 10 Solutions, 31 templates, 172 Conga Queries, 35 email templates.

- Query **CMQ-0008 has FY code hardcoded `'25f'`** — zero contacts process unless updated before an EOFY run.
- The individual **"EOFY Receipt" Contact button is DELETED** (points at file-less CMT-00031). Staff cannot generate individual EOFY receipts.
- **The EOFY Batch solution's stored URL differs from the live button URL** — clicking "Regenerate Solution" would break the live batch. Do not regenerate.
- Conga hosted infrastructure looks degraded (broken About iframe, blank Setup page) — possible EOL.

Direction: replace with native SF (Flow + Apex + Visualforce PDF + Lightning Email Templates), 10-week phased plan, minimum 2 weeks parallel run per phase, uninstall last.

## Duplicate management (Plauti)
Thresholds: **Contacts require ≥2.5 points of ID; Accounts ≥3.** Plauti groups Contacts only on exact First + Last + Primary Email. Job "Clone: Daily Contact Merge".

- **Portal-user records must be the merge master** — one active Portal User per group; disable others via "Disable Customer User".
- Financial records on blank duplicates → escalate to manager / Jono / V.
- Post-merge, check for duplicate active Recurring Donations / Recurring Payments / Subscriptions.
- **API integrations (Raisely) bypass UI duplicate rules.** Dedupe cannot be the only control.

## Deployment discipline
Production is read-only for the incoming developer during onboarding. Staging differs deliberately and dangerously:
- Membership subscription periods are **1 day in staging, 1 year in production**.
- Staging SKUs are suffixed `-STAGING`.
- **All record IDs differ** — RecordTypeId, Product2, PricebookEntry must be re-set on every production deploy. Known staging Membership RecordTypeId `012I80000004IpSIAU`.

## Security posture (as at Jun 2026 — re-verify)
Health Check 83%. But: 0 trusted IP ranges; 8 objects with Public external access; guest profiles with Edit on 45 objects; **15% of internal users are System Administrators** (target ≤5%); "Admins can log in as any user" enabled.

**9 of 14 active System Administrators have no MFA** — Hema, Lewis, Tsui, Nair, Anthony, Saxena ×2, Gupta/`blitzm`, Bhadbhade/`xecurify`. Only Andrew Dunn is fully covered. **23 inactive sysadmin accounts are not deprovisioned** (some 5 years stale). Bots birdbot1/5/6 hold System Administrator and sit in the CEO role node.

**Release Updates all at 0%.** Transaction Security Policies was due **13 Jul 2026 — past due**. OAuth username-password flow retirement, instanced-URL retirement, Authorized Email Domains and Profile Filtering all due **1 Sep 2026**. MoveData is flagged as affected by the OAuth change.

## Landmines checklist — run through this before any change
- Validation rule `Block_Reconciled_Changes` on `npe01__OppPayment__c` blocks manual correction of reconciled payments (created Nina Lewis, 8/12/2025).
- `Active_BL_Member__c` is maintained by **Payments2Us, which is being decommissioned**. Taylor & Francis Emu journal access depends on it. If the new `Membership__c` build does not take over this flag, member journal access silently breaks at migration. This is documented nowhere else.
- Recurring giving spans BOTH NPSP Recurring Donations (1,778 active) and AAkPay Recurring Payments (392 active). Any "regular giving" number that queries one object is wrong.
- Change Log objects store only new values — they are functionally useless for before/after audit.
- Arun Nair's BLAU DocGen framework (`BLAU_Doc_Template__c`, `BLAU_Doc_Generation_Log__c`, permission sets BLAU_DocGen_Admin/User) exists in staging with its Apex/Flows uncaptured, and the specification document is corrupted. Treat as knowledge-loss risk.

## People
Mathew Hema (ICT Senior Manager, alias `mhema`) · Karishma Soni (Senior SF Developer, 12-week plan, daily 9:30am standups, gates W4/W6/W8/W10/W12) · Arun Nair (departed) · Nina Lewis (Finance/Supporter Care, reconciliation) · Jonathon Wilson (Salesforce Lead) · Keith Tsui (admin) · Andrew Dunn (only fully-MFA sysadmin) · Veronica "V" (Fundraising data) · Micah Demmert (Exec Director Participation) · James Vilinsky (Senior Manager Participation) · Angelica Fazio, Alison Bolding (helpdesk).

Vendors: Blitzm, Envision CP, Xecurify/miniOrange, MoveData, Salesfix, Plauti, Conga, AAkonsult, Sercante, WP Engine.

## Operating rules for this skill
1. **Read before you write.** Always `soqlQuery` or `getObjectSchema` to confirm the field exists and the namespace is right before proposing a change.
2. **Never assert a picklist value you have not read from the org.**
3. **Sandbox first for anything structural.** Staging exists; use it.
4. **Flag FLS on the integration user** for every new field in a synced mapping, unprompted.
5. **State the licence impact** of anything that would need a new user.
6. All dates in this file are point-in-time (Jun-Aug 2026). Re-verify deadlines rather than asserting them as current.
