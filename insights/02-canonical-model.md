# L1 — Canonical Model

Conformed dimensions and fact tables. Every department metric in the catalog is
defined **only** over these structures, so two departments quoting "income" or
"members" are provably counting the same thing. DDL in `sql/warehouse-schema.sql`;
sanctioned extraction per fact in `sql/extraction-queries.md`.

## Conformed dimensions

### dim_supporter
One row per person or organisation BirdLife has a relationship with.
- **Source:** SF Contact (`C-…`) + Household Account (`N-…`), NPSP Household model.
- **Keys carried:** `sf_contact_id`, `sf_account_id`, `raisely_uuid`,
  `betterimpact_id` (currently ~empty), `ortto_synced` flag.
- **Identity resolution:** Salesforce is the master; Plauti merge discipline
  applies (Contacts ≥2.5 ID points, Accounts ≥3; portal-user record is always
  merge master). API-sourced records (Raisely) bypass UI duplicate rules, so a
  residual duplicate rate is expected — measured, not assumed away.
- **Attributes:** household, postcode/state, supporter type flags (donor, member,
  regular giver, volunteer, advocate), first/last gift dates, deceased/inactive.

### dim_staff
One row per employee.
- **Source:** Employment Hero master, keyed on worker code **BLA###**; conformed
  against NetSuite employee list and Entra users (`#EXT#` guests excluded).
- **The three-way headcount triangle (EH vs NetSuite vs Entra) is itself a
  published metric** — until the EH↔NS link exists, the triangle never closes and
  the delta is the data-integrity signal.

### dim_date
Calendar + Australian FY (Jul–Jun) + NetSuite fiscal (Jan–Dec calendar FY) +
business-day flags (needed for the ±3-business-day reconciliation window).
Note the two fiscal calendars coexist: fundraising reports on Australian FY,
NetSuite's fiscal year is calendar-year. Every metric states which it uses.

### dim_campaign
- **Source:** SF Campaign hierarchy.
- **Caveat baked in:** Raisely maps one campaign → one SF Campaign, so online
  community-fundraising gifts attribute to the top-level appeal only. A
  `attribution_grain` column ('campaign' | 'appeal-only') makes this queryable.

### dim_gl_account
NetSuite chart of accounts (413 accounts, 5-digit blocks) + the GAU→GL mapping.
Notable members: 11103 NAT ABF Donations, 11104 NAT Operations, 41001/41002
Memberships, 44013 Merchandise (known GST issue), 44023 Subscriptions, 21304
Unearned Revenue, 118636581 NAT donations bank clearing.

### dim_org_unit
Department dimension conformed across systems — this is what makes
"per-department" reporting possible:
- NetSuite Department (86 active) / Class (312 active) / Location (36) /
  Project (~281 active)
- Asana team (programme teams: Beach-nesting Birds, Black-cockatoos, Citizen
  Science, Coastal & Wetland, Fundraising & Marketing, Finance, eCommerce, …)
- EH/Entra department attribute
The mapping table is maintained by hand until the NetSuite Class/Project cleanse
(`[PROGRAM]_[FUNDER]_[TYPE]_[FY]` convention) lands; expect `unmapped` rows and
report their share.

### dim_membership_tier
Individual $84 · Concession $65 · Family $132 (1 primary + up to 6) · Financial
Hardship $35 (hidden) · Free $0 (Lifetime/Honorary/Fellow). 12-month term,
3-month grace (End +12m, Cease +15m). Source: staging config 30 Jul 2026 —
re-verify at go-live.

### dim_channel
Gift/order/case intake channel: web (Woo), Raisely, direct debit batch
(Payments2Us), email, phone, event (Humanitix), bequest, in-branch. For ICT
cases: email / internal / web / phone (Ask Zeus is 96.5% email).

### dim_system
Which source system produced the row — every fact carries it, so any metric can
be split by provenance and cross-system disagreement is always visible.

## Fact tables

| Fact | Grain | Source(s) | Notes |
|---|---|---|---|
| `fact_gift` | One committed gift/opportunity | SF Opportunity (won) | Includes membership opps; `is_membership` flag. Close Date basis |
| `fact_payment` | One payment attempt/settlement | SF `npe01__OppPayment__c` + Stripe balance transactions | Refunds currently appear as **positive** payments typed `shop_order_refund` — normalised to negative with `is_refund_defect` flag until the sync is fixed |
| `fact_recurring_agreement` | One active regular-giving agreement | **UNION** of NPSP Recurring Donations (1,778) **and** AAkPay Recurring Payments (392) | The union is mandatory; single-object numbers are wrong by construction |
| `fact_membership_period` | One member-year (start→cease) | Today: `AAkPay__Subscription__c` + `Active_BL_Member__c`; future: `Membership__c` + Woo Subscriptions | Dual-source during migration with `source_system`; the cutover comparison (P2U count vs new count) is the migration acceptance metric |
| `fact_order` | One WooCommerce order | Woo REST API | Carries `sf_writeback_ok` flag (post meta present) and sync outcome |
| `fact_gl_line` | One GL journal line | NetSuite (SuiteQL, subsidiary 2) | 587k lines back to Dec 2016; Department/Class/Location/Project segments |
| `fact_bank_line` | One bank statement line | NetSuite bank feeds (`SF:` connector) | Reconciliation status; feeds the bank-rec ageing metric |
| `fact_reconciliation` | One SF-gift ↔ NS-posting match attempt | Derived: SF export vs NS, ±3-business-day window (policy Option A) | The unreconciled backlog *is* this fact filtered to unmatched |
| `fact_case` | One Salesforce Case | SF Case | **Always** carries `record_type_developer_name`; ICT = `Zeus` only. `days_to_resolution`; time-in-status pending field-history tracking |
| `fact_work_item` | One Asana task | Asana MCP | Project, section, assignee, due date, staleness (days since modified) |
| `fact_engagement` | One marketing/engagement event | Ortto activities (15.9M), Campaign Monitor, GA4 | Post-Pardot only; historical Pardot engagement dies 31 Aug 2026 unless exported |
| `fact_training` | One LMS enrolment | LearnUpon webhook | **Enrolment only — completion is not captured** (webhook not ticked; no EH write-back) |
| `fact_event_attendance` | One ticket | Humanitix via Zapier | |
| `fact_payroll_summary` | One employee-payrun (summary, no line detail) | NetSuite ZonePayroll | Aggregates only; salary detail stays out of the model. ~128 staff/run |
| `fact_security_posture` | One control-snapshot per month | Entra/Defender exports | Secure Score, MFA coverage %, device compliance, E8 maturity — snapshot pattern, never live per-user detail |
| `fact_volunteer_activity` | One volunteer shift/hours entry | **Placeholder** — Better Impact, post-implementation | Blocked until BI go-live and `BetterImpact_ID__c` backfill |

## Identity resolution rules

1. **Supporter matching order:** exact external key (`Raisely_UUID__c`, Woo
   customer→SF Id, `BetterImpact_ID__c`) → Plauti exact First+Last+Primary Email
   → manual. Never auto-merge on name alone.
2. **Staff matching order:** BLA### → company email → never name-only. Exclude
   Entra `#EXT#` guests before any match.
3. **Merges preserve the portal-user record as master**; post-merge, check for
   duplicate active recurring agreements across BOTH recurring objects.
4. **Refund matching (until `Stripe_Refund_ID__c` exists):** Stripe `re_xxx` →
   SF by amount + date ± 3 days + last4 where available; matches are labelled
   `matched_fuzzy`.

## Sensitive-data rules

- Per-user security weakness data (MFA status, sign-in gaps) appears **only** as
  aggregates in `fact_security_posture`. Named lists stay in the security team.
- Payroll enters the model as summaries; no per-person salary in any dashboard.
- Card tokens, webhook URLs and API credentials never appear in extracts,
  documents or dashboards. (Two past leaks — miniOrange webhook keys and
  WooCommerce API keys — are the precedent.)
- Donor giving detail is need-to-know: department dashboards show aggregates;
  named major-donor views are Fundraising-only.
