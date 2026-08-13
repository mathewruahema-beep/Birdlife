# L2 — Metrics Catalog, by Department

Every metric states: definition, grain/scope, source facts, and **known
distortions** (cross-referenced `DQ-##` → `04-data-quality-register.md`).
A metric quoted without its stated scope is not this metric.

Baseline figures are point-in-time (Jun–Aug 2026) and shown only to anchor the
definitions — recompute, never re-quote.

---

## 1. Fundraising & Philanthropy

| Metric | Definition | Source | Distortions |
|---|---|---|---|
| Fundraising income | Sum of won `fact_gift` in period, Australian FY basis, by campaign/GAU | SF Opportunity | DQ-01 (Woo sync loss ~10%), DQ-03 (refunds inflate), DQ-07 (Major Donor tile double-count, ~$37.5K confirmed) |
| Regular giving — active agreements | Count of active `fact_recurring_agreement` — **union of NPSP RD + AAkPay RP, always** | Both objects (1,778 + 392 baseline) | DQ-05: either object alone is wrong. AAkPay side goes away at P2U decommission — series break to be annotated |
| Regular giving — monthly value | Sum of normalised monthly amount over the union | As above | Normalise frequencies (annual/quarterly→monthly) in the query, not by eye |
| Donor retention rate | % of prior-FY donors giving again this FY, household grain | `fact_gift` + `dim_supporter` | Duplicate supporters (DQ-09) split giving histories and understate retention |
| Average gift / gifts per donor | Standard, household grain, excluding memberships (`is_membership = false`) | `fact_gift` | Membership opps included by accident is the classic inflation |
| Campaign attribution | Income by `dim_campaign`, with `attribution_grain` shown | `fact_gift` | DQ-10: Raisely gifts attribute to top-level appeal only — segment-level campaign ROI for online community fundraising is not currently measurable, say so on the tile |
| Receipting SLA | % of gifts receipted within N days | Conga Batch-0008 logs | DQ-11: EOFY query hardcodes FY `'25f'`; individual EOFY button deleted. Metric is unreliable until the native-SF receipting rebuild |
| Bequest & major gift pipeline | Open opportunities by stage, major-gift record types | SF Opportunity | Keep as a separate query from the income tiles (DQ-07 was caused by independent tile queries) |

## 2. Membership & Participation

| Metric | Definition | Source | Distortions |
|---|---|---|---|
| Active members | Count of current `fact_membership_period` — **today** `Active_BL_Member__c = true`; **post-migration** `Membership__c` status | P2U / future `Membership__c` | DQ-06: `Active_BL_Member__c` is maintained by Payments2Us, which is being decommissioned — if the new build doesn't take the flag over, this metric (and Emu journal access) silently breaks |
| New joins / renewals / lapses | Period starts, renewals, and periods passing cease date (+15m) without renewal | `fact_membership_period` | During migration, dual-source with `source_system` split visible |
| Auto-renewal rate | % of active memberships with auto-renew on | Woo Subscriptions + `Automatic_Renewal__c` | DQ-12: `Automatic_Renewal__c` mapping exists **only in staging** |
| Tier mix | Active members by `dim_membership_tier` | As above | Tier prices verified on staging 30 Jul 2026; re-verify at go-live |
| Migration acceptance | P2U active count vs new-platform active count at cutover; target delta = explained 100% | Both sources | BECS members cannot migrate (fresh mandate needed) — they will appear as "lapsed" unless flagged; this is a comms metric, not churn |
| Member journal eligibility | Members entitled to Emu (T&F) access | `Active_BL_Member__c` today | Same DQ-06 dependency |

## 3. Finance

| Metric | Definition | Source | Distortions |
|---|---|---|---|
| **Unreconciled income** | SF won gifts with no NS posting match within ±3 business days (policy Option A, SF Close Date basis) | `fact_reconciliation` | Baseline $671,117 / 2,878 records (3 Jul 2026), growing ~$87K/day. Detection Zap `371228125` is **drafted, unpublished** — publishing it is the standing recommendation |
| Income by GL / programme | `fact_gl_line` by `dim_gl_account` × `dim_org_unit`, NetSuite fiscal basis | NetSuite SuiteQL, subsidiary 2 | DQ-13: Class/Project segments ~67% inactive with no naming convention — show `unmapped %` on every programme split |
| Bank reconciliation ageing | Unmatched `fact_bank_line` count and oldest item age, per account | NetSuite | 11104: 378 unmatched, 11103: 120 — both last reconciled **31 Mar 2022**. This metric is a control alarm, and a mandatory precondition of any BC migration |
| GST exceptions | GST anomalies by GL account | NetSuite | Known: merchandise 44013 ~$7,224/yr |
| Refund traceability | % of Stripe refunds matchable to an SF record | Stripe + SF | DQ-03: currently ~0% traceable natively (no `re_xxx` in SF); metric exists to prove the fix |
| Payroll variance | Run-over-run payroll total variance | `fact_payroll_summary` | Aggregate only; ~128 staff, single run |
| SF↔NS date-basis disclosure | Every finance number states Close Date vs posting date basis | — | The 1–3 day Stripe clearing lag means the two bases never align; a number without its basis is unusable |

## 4. Supporter Care & eCommerce

| Metric | Definition | Source | Distortions |
|---|---|---|---|
| Order volume & value | Completed `fact_order` per period | Woo API | Baseline ~6,466 orders / ~A$11.1K month |
| Refund rate | Refunded / completed orders | Woo + Stripe | Baseline 70 / 6,331. Verify against Stripe, not SF (DQ-03) |
| **Sync integrity** | % of paid orders with (a) SF Id written back, (b) successful sync | `fact_order` flags | DQ-01: ~10.3–10.5% FLS failure rate; DQ-02: write-back gap. This is the health metric for the whole Woo→SF chain |
| Duplicate supporter rate | Plauti duplicate-group count / active contacts | dupcheck objects | API-sourced records bypass UI rules — expect a floor above zero |
| Supporter care case load | Cases by non-Zeus, non-conservation record types | `fact_case` | Scope by record type explicitly, per the ICT lesson |

## 5. ICT (Ask Zeus + project delivery)

Scope filter for every case metric: `RecordType.DeveloperName = 'Zeus'`. The
repo root README documents why (217× inflation without it).

| Metric | Definition | Source | Distortions |
|---|---|---|---|
| Open queue / by status | Open Zeus cases; `Owner.Name = 'Zeus'` shown as **unassigned intake**, not a person | `fact_case` | Baseline 20 open, 8 New |
| MTTR | Avg `days_to_resolution` on closed Zeus cases | `fact_case` | The legacy "MTTR by Agent" report is a closed-case *count* — rename pending (root README task 3) |
| Time-to-acknowledge / time-in-status | Requires Case Status field-history tracking | — | **Not measurable yet** — tracking not enabled; Asana task exists (Kate Rogerson) |
| Category coverage | % open cases with `Type` set | `fact_case` | Baseline 65% blank; validation rule `Zeus_Type_Required_On_Close` is the designed fix |
| Identity-lifecycle share | IAM + onboarding + offboarding cases / total | `fact_case` | Baseline 87/425 = 20% — the automation business case |
| Channel mix | Case origin split | `fact_case` | Zeus is 96.5% email; zero self-service |
| Project flow | Asana tasks by section; Blocked age; overdue; undated; unassigned | `fact_work_item` | DQ-14: board hygiene — undated/stale tasks make flow metrics structurally incomplete; publish the hygiene numbers alongside |
| Case↔task linkage | % of Zeus cases with a linked Asana task | — | **Not measurable** — the join is a spreadsheet column; SPF-blocked email rule is the designed fix |

## 6. People & Culture

| Metric | Definition | Source | Distortions |
|---|---|---|---|
| Headcount triangle | EH active vs NetSuite payroll vs Entra enabled staff (guests excluded), matched on BLA### | `dim_staff` | The triangle **should** close to zero; every mismatch is a leaver not offboarded, a starter not provisioned, or dual-entry drift (DQ-15) |
| Onboarding completeness | New starters with: EH record, BLA###, Entra account, licence, correct email format | `dim_staff` | EH invite must capture *personal* email; CSV Quick-add is banned |
| Offboarding latency | Days from EH termination to Entra disable | EH + Entra sign-in logs | **No offboarding checklist exists today** — baseline will be ugly; the Power Automate leaver flow is the designed fix |
| Training enrolment | Enrolments per period | `fact_training` | Completion is **not captured** (LearnUpon webhook config + no EH write-back without Platinum tier) — never present enrolment as completion |
| Expense reporting | Expense volume/value by department | NetSuite | Blocked: EH Expense Categories empty; NS expense roles are among the four flagged for excessive rights — fix precedes measurement |

## 7. Marketing, Communications & Engagement

| Metric | Definition | Source | Distortions |
|---|---|---|---|
| Audience size | Ortto people, `Ortto Inactive = false` | Ortto | Leads not synced; retention limit reached blocks expansion (DQ-16) |
| Email engagement | Opens/clicks/unsubscribes per campaign | Ortto + Campaign Monitor | Two sending systems until CM retires — always state which |
| Web traffic & conversion | GA4 sessions → donation/membership conversion | GA4 via Zapier | Cart-flood-style bot traffic can distort; the Jul 2026 incident is the precedent |
| Pardot cutover | Assets/automations migrated vs total, countdown to 31 Aug 2026 | Project tracking | After cutover, Pardot history is gone — export first or the engagement series breaks |
| Event attendance | Tickets by event | `fact_event_attendance` (Humanitix) | — |

## 8. Conservation Programmes & Citizen Science

Honest position: **the big conservation datasets (Birdata surveys, KBA
monitoring) live outside the connected estate.** What is measurable today:

| Metric | Definition | Source | Distortions |
|---|---|---|---|
| Public enquiry load per programme | Cases by conservation record types (Powerful Owl, Swift Parrot Search, KBA, Birdata, Conservation Campaigns, …) | `fact_case` | These are the very cases the ICT filter excludes — same data, opposite scope |
| Programme delivery flow | Asana tasks by programme team (Beach-nesting Birds, Black-cockatoos, Grasswrens, …) | `fact_work_item` | Team-board hygiene varies |
| Programme financials | Income/spend by `dim_org_unit` programme mapping | `fact_gl_line` | DQ-13 unmapped share applies hardest here |
| Advocacy engagement | Campaign actions via Ortto/Raisely | `fact_engagement` | Raisely attribution coarseness (DQ-10) |
| Birdata/survey metrics | — | **Not connected** | Flag as roadmap; do not fake with proxies |

## 9. Volunteering

Everything here is **pending Better Impact go-live**. Pre-live, the only honest
metrics are readiness metrics:

| Metric | Definition | Source |
|---|---|---|
| BI implementation progress | Better Impact board plan vs actual | Asana (private board) |
| Contact linkage readiness | Contacts with `BetterImpact_ID__c` populated (count real values — baseline **1**, and the `!= null` trap reads it as 479,613; DQ-04) | SF |
| Post-live: active volunteers, hours, retention | `fact_volunteer_activity` | Better Impact |

## 10. Executive / Board rollup

One page, one number per department, each carrying its scope caption:

1. Fundraising income FYTD vs target (Australian FY, SF Close Date basis)
2. Active members + trend (source system named during migration)
3. Regular-giving agreements (union) + monthly value
4. Unreconciled income $ + oldest item age (the control number)
5. Bank-rec backlog (11103/11104 unmatched count)
6. ICT: open Zeus queue + MTTR
7. People: headcount triangle mismatch count
8. Security: Secure Score % + MFA coverage % (aggregate only)
9. Marketing: audience size + engagement rate
10. Volunteering: BI milestone status (pre-live)

The board pack rule: **positives get stated too** (the security precedent: 0
risky sign-ins, 19 attacks blocked) — a register of pure defects trains readers
to ignore it.
