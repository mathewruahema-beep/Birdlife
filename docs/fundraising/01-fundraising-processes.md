# How Fundraising Works in Salesforce Production ("Zeus")

**Org:** birdlifeaustralia.my.salesforce.com (Enterprise, NPSP Household Account model)
**Method:** Read-only discovery — SOQL against live production data and `FlowDefinitionView`, 20 Aug 2026. No records or metadata were changed.
**Author's scope:** Fundraising income (donations, regular giving, memberships-as-income, bequests, merchandise), the automation that touches it, and where the repeatable gaps are.

---

## 1. Data model

Fundraising revenue lands on the standard **Opportunity** object, one record per gift/order, attached to an NPSP Household (or Organisation/Estate) Account and a primary Contact. Money is then tracked at three deeper levels:

| Layer | Object | Purpose |
|---|---|---|
| Gift | `Opportunity` | One per donation / membership sale / order |
| Cash | `npe01__OppPayment__c` (NPSP Payment) | Actual payment legs, reconciliation flag (guarded by validation rule `Block_Reconciled_Changes`) |
| Designation | `npsp__Allocation__c` (GAU Allocation) | Splits each gift across General Accounting Units, incl. tax-deductible vs non-deductible roll-ups |
| Gateway | `AAkPay__Payment_Txn__c` (Payments2Us) | Card/direct-debit transaction from web forms and recurring debits; generates the Opportunity + Payment + GAU via flow |

### Opportunity record types in use for fundraising

| Record type | Closed Won last 365 days | Amount | Notes |
|---|---:|---:|---|
| Donation | 41,540 | A$6,251,513 | Bulk of transactional income |
| Bequest | 40 (Estate Closed) | A$3,197,863 | Own stage set ("Estate Closed") |
| Membership | 8,828 | A$572,294 | Also mirrored in `AAkPay__Subscription__c` membership records |
| Product Sale | 5,076 ("completed") | A$352,851 | WooCommerce shop orders — stages are **raw Woo strings** (`processing`, `completed`, `refunded`, `failed`), not standard picklist stages |
| Major Gift | 4 | A$139,990 | High-touch, low volume |
| Grant | 2 open | — | Pipeline-style stages ("Application Submitted") |

Supporter identity conventions: Contacts `C-xxxxxxx`, Household Accounts `N-xxxxx`. Membership No. is kept in sync with Supporter Id by a Contact flow.

## 2. Income channels — how gifts actually enter the org

| Channel | Path into Salesforce | Created by (last 90 days of Donations) |
|---|---|---|
| **Online appeals / regular giving sign-up (Raisely)** | Raisely → MoveData managed flows (`[MoveData] Donation: …` + unmanaged `[MoveData Extension]` overrides) → upsert on `Raisely_UUID__c` | "Bird Bot" — 1,747 |
| **Payments2Us web forms** (donation forms, membership joins/renewals, direct debit) | `AAkPay__Payment_Txn__c` → flow `Payment Txn aCU - Payment and GAU Creation` → Opportunity/Payment/GAU | Runs under P2Us automation |
| **Mail appeal banking / imports** | Batch entry & data loads (P2Us Batch Entry flows; bulk imports) | Keith Tsui — 11,051 |
| **WooCommerce shop** (miniOrange sync) | Woo order → Opportunity (Product Sale) + OpportunityLineItems; SF Id written back to Woo post meta | Sync user; known ~10% FLS failure rate & refund-flow defects |
| **Bequests** | Web/email → Case (flow `BQ Case: Web and email to Case Bequests`) → managed manually to Estate Account + Bequest Opportunity | Fundraising team |

Two structural cautions verified in the KB and still current:
- Raisely campaigns map to **one** SF Campaign each — online gifts attribute to the top-level appeal, not the segment campaign.
- The Woo→SF refund flow is materially broken (positive-amount refund Payments, invalid stage strings — visible above as `refunded`/`failed` stages).

## 3. Campaign structure and attribution

Campaign record types in use: Appeals, Fundraising, Community Fundraising, Event, Marketing, Mailings, Hierarchy Campaign, General. Appeals follow a seasonal naming pattern with segment children (`T26 DM W1` = Tax 2026, direct mail, wave 1).

Top campaigns by Closed Won amount, last 365 days:

| Campaign | Gifts | Amount |
|---|---:|---:|
| Australian Bird Fund | 119 | A$2,457,650 |
| Tax Appeal 2026 (T26) | 6,000 | A$1,288,235 |
| WILDBIRD (regular giving program) | 15,515 | A$569,718 |
| BirdLife Australia Memberships | 7,679 | A$547,163 |
| Spring Appeal 2025 (S25) | 4,257 | A$466,968 |
| Xmas Appeal 2025 (X25) | 3,040 | A$345,647 |
| Autumn Appeal 2026 (A26) | 1,733 | A$206,933 |
| T26 MGD Pool | 5 | A$140,000 |

So the fundraising year is: **four seasonal appeals (Tax/Spring/Xmas/Autumn) + always-on WILDBIRD regular giving + memberships + major gifts/bequests**, with campaign hierarchies rolling segments into the headline appeal.

## 4. Recurring giving — two parallel engines (both live)

Any "regular giving" figure that reads only one of these objects is wrong.

### 4.1 NPSP Enhanced Recurring Donations (`npe03__Recurring_Donation__c`)
| Status | Count | Committed |
|---|---:|---:|
| Active — Monthly | 1,847 | A$58,137/mo |
| Active — Yearly | 410 | A$68,278/yr |
| Lapsed | 78 | A$2,171/mo equiv. |
| Paused | 3 | — |
| Closed | 2,390 | — |

NPSP auto-creates installment Opportunities; status changes are logged to `RD Change Log` by flows `Recurring Donation bCU/aCU - Status Changed`.

### 4.2 Payments2Us Recurring Payments (`AAkPay__Recurring_Payment__c`)
This engine actually charges cards / debits bank accounts (incl. membership auto-renewal):

| Status | Count | Monthly-equivalent |
|---|---:|---:|
| Active | 5,314 | A$44,941/mo |
| Expired | 7,038 | — |
| Cancelled / Cancelled AR | 943 | — |
| **Suspended - Max retries exceeded** | **542** | **A$4,082/mo** |
| Awaiting Account Verification | 36 | A$208/mo |

On sign-up there is a welcome journey: flow **"Recurring Payment: After insert, send Welcome to Wildbird Regular Giving Email"**, plus P2Us's own welcome/receipt machinery (`AAkPay__Welcome_Email_Sent__c`). Status changes are logged (`RP Change Log`). Payment method updates flow through URL tokens (self-service card update links).

**On failure there is nothing** — see §7.

## 5. Receipting and acknowledgement

Three distinct mechanisms:

1. **Transactional receipts** — Payments2Us at payment time (`AAkPay__Send_Receipt__c` per payment form).
2. **Daily donation receipts** — Conga Batch-0008, 7:00 PM AEST daily, 50–200 receipts/day. Known defects: FY code hardcoded `'25f'` in query CMQ-0008; individual "EOFY Receipt" button deleted; batch solution URL drift (do **not** click Regenerate). Replacement by native SF (Flow + Apex PDF) is the agreed direction.
3. **Self-service** — Community flows `[Community] Generate EOFY receipt` and `[Community] Regenerate donation receipts` for portal users.

**Personal acknowledgement (thank-you) is a manual, high-touch-only process.** Of 41,606 Donation Opportunities in the last 365 days, **40,941 (98.4%) have no `npsp__Acknowledgment_Status__c`**; the ~665 populated ones (TY - Called / Left VM / Emailed / Sent Card, Acknowledged, Do Not Acknowledge) are the major-donor courtesy loop. Receipts ≠ thanks; this is a known-by-design gap but there is no systematic first-gift or milestone acknowledgement.

## 6. Live automation inventory relevant to fundraising

327 active flows in the org. The fundraising-relevant set, by trigger:

- **Opportunity:** Before Insert/Update housekeeping; GAU tax-deductible roll-up; GAU rounding allocation; Product Sale naming/postage; Stripe balance-transaction fetch; `Community : Community Fundraiser[Checked]` (Contact-side; the Opportunity-side equivalent is **inactive** — the checkbox has been stale since deactivation).
- **Payment Txn (P2Us):** Payment & GAU creation; Batch Entry creation; membership option update; a country-fix flow ("Afghanistan → Australia" — band-aid over a form default bug).
- **Payment (NPSP):** bank-transfer reallocation; auto-created payment removal for Major Donor/Bequest.
- **Recurring Payment / Recurring Donation:** status-change logging; welcome email (Wildbird); pay-method-to-subscription propagation.
- **Subscription (membership):** scheduled renewal emails ("Renewal - No Change" / "Renewal - Category Change"); reactivation; scheduled "Subscriptions: Expired and Ceased Memberships".
- **Finance/reconciliation screen flows:** Reconcile Batch, Reconcile DD Batch, Reconcile Payout (Stripe payouts), guarded by validation rule `Block_Reconciled_Changes` on Payment.
- **MoveData (Raisely):** ~50 managed `[MoveData]` flows + unmanaged `[MoveData Extension]` overrides — **do not edit managed layer**.
- **Payments2Us Agent actions:** a suite of ~20 autolaunched "Payments2US Agent …" flows (get donor details, send card-update email, cancel recurring + follow-up task, receipts) — building blocks exposed for agent/invocable use.
- **Contact:** First Gift Date stamping; Major Donor household sync; deceased → No Mail; opt-in dedupe hygiene.

## 7. Gap analysis — repeatable processes with no automation

| # | Gap | Evidence | Repeatable? |
|---|---|---|---|
| **1** | **Failed regular giving / membership auto-renewal recovery** | 542 RPs in "Suspended - Max retries exceeded" (A$4,082/mo committed); ~14 new suspensions/month (43 in last 90 days, all with email on file); **0 Tasks logged against any Recurring Payment in 180 days** | **Yes — same trigger, same steps, every time. Chosen for the automation design (doc 02).** |
| 2 | Card-expiry pre-emption | 133 Active RPs with card expiring ≤60 days (A$786/mo); P2Us sets `AAkPay__Expiry_Reminder__c` automatically but nothing consumes it | Yes — natural phase 2 of #1 |
| 3 | Donation acknowledgement at scale | 98.4% of donations have no acknowledgement status; no first-gift welcome for cash donors | Yes, but crosses into supporter-journey strategy (Ortto territory) |
| 4 | NPSP RD Lapsed follow-up | 78 Lapsed RDs, no follow-up flow | Yes — same pattern as #1, different object |
| 5 | Woo refund hygiene | Invalid stages, positive refund payments | A data-fix + integration fix, not a pattern automation (Karishma W4 gate) |

The suspended-payment breakdown shows it hits **both** income lines:
444 BirdLife Memberships (A$2,678/mo), 43 Direct Debit Donations (A$1,310/mo), 55 special-interest-group memberships (A$94/mo). A failed membership renewal also silently threatens journal access (`Active_BL_Member__c`).

Doc **02-automation-design-regular-giving-recovery.md** designs the automation for gap #1 (with #2 as a phase-2 extension). Design only — nothing has been built or activated.
