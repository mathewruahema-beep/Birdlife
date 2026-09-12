---
name: birdlife-payments2us
description: "Expert operator and deep technical knowledge for Payments2Us (AAkPay) in BirdLife Australia's Salesforce org (Zeus): the licence deadline, live configuration, the full automation stack (managed triggers, 13 BirdLife Flows, 9 DLRS rollups, scheduled jobs), the Active_BL_Member__c chain, direct debit internals, and the live defects. Trigger on Payments2Us, AAkPay, AAkonsult, direct debit, DD batch, recurring payment, regular giving, membership subscription, merchant facility, payment form, payment txn, card expiry, ABA file, GAU allocation from a payment, or a supporter whose payment did not go through."
---

# BirdLife Australia, Payments2Us (AAkPay)

Payments2Us is the membership and direct debit engine at BirdLife. It is live money, not legacy. Every figure below was read from production on 10 September 2026; re-run the verification query before quoting any number.

Companion document: `IT-SF-018_Payments2Us_Expert_Operator_Reference.md` in Mathew's Google Drive (the Claude parent folder, ADR 0021). Read `birdlife-core` first, `birdlife-salesforce` for the wider org, `birdlife-conga` and `birdlife-sdocs` for receipting, `birdlife-netsuite` for the GL side, `birdlife-wordpress` for the membership rebuild.

---

## 1. The deadline, check this first

**The Payments2Us licence on both live merchant facilities expires 30 November 2026.** `AAkPay__License_Expiry_Date__c = 2026-11-30` on BirdLife DONATIONS Facility and BirdLife MEMBERSHIP Facility, licence options `Direct Debit` and `Batch Entry`. If it lapses, direct debit extract and batch entry stop, taking out roughly $16,000 a month of collection.

AAkonsult's model: Payments2Us Finance permission set holders manage feature licences directly from the License Options interface, no support case needed. A feature once added cannot be removed for 30 days. Changes apply across all associated merchant facilities.

```sql
SELECT Name, AAkPay__License_Expiry_Date__c, AAkPay__License_Options__c, AAkPay__Active__c
FROM AAkPay__Payment_Setting__c WHERE AAkPay__Active__c = true
```

## 2. Naming traps, learn before touching anything

| UI label | API name |
|---|---|
| Payment Form | `AAkPay__Payment_Type__c` (154 fields) |
| Payment Type | the picklist on that object: Donation, Order, Membership, Training, Subscription, Event, Program, Peer-to-Peer |
| Merchant Facility | `AAkPay__Payment_Setting__c` (162 fields) |
| Payment Txn | `AAkPay__Payment_Txn__c` (284 fields) |
| Recurring Payment | `AAkPay__Recurring_Payment__c` (144 fields) |
| Subscription | `AAkPay__Subscription__c` (147 fields) |

- **Namespace collision.** Keith Tsui's unmanaged `Subscription__c` is a different object from `AAkPay__Subscription__c`. Always qualify.
- **Superseded fields.** On Direct Debit Batch use the `_RUS__c` roll-ups (`No_in_Batch_RUS__c`, `No_Completed_RUS__c`, `No_In_Error_RUS__c`, `Total_Batch_Amount_RUS__c`); the non-RUS versions do not populate. On Payment Form, `AAkPay__Enable_Recurring__c`, `AAkPay__Enable_Membership_Search__c` and `AAkPay__Surcharge_Card_*` are deprecated in favour of `AAkPay__Enable_Recurring_Opt__c`, `AAkPay__Enable_Membership_Search_Options__c`, `AAkPay__Enable_Surcharge__c`.
- **Orphaned picklist value.** 28 Recurring Payments carry Frequency `Yearly`, not a defined value; the valid one is `Annually`. Reports filtering `Annually` lose them silently.
- **Never trust `!= null` counts in this org.** Number fields default to 0. Count with `!= null AND != 0` or sample rows.

## 3. What is live and what is dead

80 AAkPay objects, 736 managed Apex classes, 42 managed triggers, 132 Visualforce pages. Payments2Us is the fourth largest body of Apex in Zeus, behind Stripe (5,509), DevOps Center (1,859) and NPSP (1,035).

**Merchant facilities: 9 exist, 3 Active, 2 carry traffic.**

| Facility | State | Gateway | Notes |
|---|---|---|---|
| BirdLife MEMBERSHIP Facility `a1i5g000000ovPeAAI` | Active | Stripe | Lapsed grace **90 days**, Tax rate not set |
| BirdLife DONATIONS Facility `a1i5g000000ovPjAAI` | Active, **Primary** | Stripe | Lapsed grace 30 days, Tax 10%, masking `2X....4X` |
| BirdLife COMP MEMBERSHIP Facility `a1i5g000000p8uoAAA` | Active | Stripe | Manual only, Create Opportunity off, zero txns in 12 months |
| DEMO FACILITY, Direct Debit Facility (Sandbox) x2, Donations - Stripe (TEST), Memberships - Windcave (Demo), Stripe Test Merchant Facility (Sandbox) | Inactive | Windcave / Stripe | Licences expired 2023-11-30 |

Both live facilities carry gateway option `Enforce New Public Sites Security`, matching method `Nonprofit Starter Pack 3+`, `Match and Create New If No Match Found`, and ABA direct debit file format. Matching rules **differ**: Donations includes `Last Name + Email` and `Last Name + Mobile`, Membership includes `First Name + Mobile`. Looser Donations matching feeds the duplicate problem.

**Payment forms: 31 exist, 7 carry traffic.** Everything else is an AAkonsult demo form installed twice (2021 and 2022) or the superseded 2021 BirdLife generation. All 31 show LastModifiedDate 2026-02-04 08:20:07, a single package-upgrade touch; nobody has deliberately edited a form in production this year.

| Live form | Facility |
|---|---|
| BirdLife Membership `a1k5g000000tu40AAA` | MEMBERSHIP |
| BirdLife Direct Debit Donation `a1k5g000000tu3qAAA` | DONATIONS |
| Birdlife Offline Donation Form `a1k5g000000tu3kAAA` | DONATIONS |
| BirdLife Photography Membership `a1k5g000000tu3vAAA` | MEMBERSHIP |
| BirdLife Australasian Wader Studies Group Membership `a1k5g000000tu3nAAA` | MEMBERSHIP |
| BirdLife Australia Raptor Group Membership `a1k5g000000tu3oAAA` | MEMBERSHIP |
| BirdLife Australasian Seabird Group Membership `a1k5g000000tu3mAAA` | MEMBERSHIP |

Dormant but not deleted: the duplicated demo set (1. Online Payment through 7. Appeal, each twice), the 2021 legacy set (Membership BirdLife Australia, Membership BirdLife Photography, Membership Raptor Group, Membership Australasian Seabird Group, Membership Australasian Wader Studies Group, Donation Form - Stripe, Donation Form - Direct Debit), BirdLife $0 Memberships, BirdLife Organisation Membership, Offline Donation Form - Stripe (Sandbox).

**Before changing any form or facility, confirm it is one of the live ones.** Editing "Membership BirdLife Australia" when you meant "BirdLife Membership" changes nothing and you will not find out for days.

---

# THE TECHNICAL LAYER

## 4. The complete automation stack on a Payment Txn

This is what actually executes when a supporter pays. Four separate automation technologies, from two vendors plus BirdLife's own build, all firing on one record. Nothing else in this skill matters as much for diagnosis.

**Salesforce order of execution on `AAkPay__Payment_Txn__c` insert:**

```
1. Before-save flows      none on this object
2. Before triggers        AAkPay.paymentTxnUpd            (managed, before insert/update)
                          dlrs_AAkPay_Payment_TxnTrigger  (unmanaged, DLRS realtime, API 59)
3. Validation rules
4. After triggers         AAkPay.paymentTxnUpd            (after insert/update)
                          dlrs_AAkPay_Payment_TxnTrigger
5. After-save flows       Payment_Txn_aCU_Payment_and_GAU_Creation
                          Payment_Txn_aCU_Batch_Entry_and_Batch_Entry_Line_Creation
                          Payment_Txn_After_Insert_or_Update_if_Membership_update_Membership_Option
                          Payment_Txn_After_insert_if_Country_is_Afghanistan_update_to_Australia
6. Rollups (DLRS)         Last_Payment_Txn_Date -> Recurring_Payment.LastPaymentTxnDate__c  (Realtime)
7. Async                  PaymentTxnQueueableProcessor, paymentStatusCheckProcessor,
                          paymentTxnExtShareLockProcessor
```

### The circular data path, and the likely root of the trigger errors

```
AAkPay__Payment_Txn__c  created
        |
        v  Flow: Payment_Txn_aCU_Payment_and_GAU_Creation  (after save)
        |
   npe01__OppPayment__c  +  npsp__Allocation__c  created
        |                          ^  Apex: CreateGauAllocations (API 67)
        |                          |  Flow: GAU_Allocate_Rounding_to_Highest_Opp
        |
        v  DLRS Realtime x2:  Payment_Fee_at_Payment_Txn   -> Payment_Txn.Payment_Fee__c
        |                     Payment_Gross_at_Payment_Txn -> Payment_Txn.Payment_Gross__c
        v
AAkPay__Payment_Txn__c  updated again, re-entering step 2
```

Creating a Payment Txn causes a child record to be created which immediately rolls values back up onto the same Payment Txn, re-entering the managed trigger. **This is the most plausible root of both live error patterns:** the `SELF_REFERENCE_FROM_TRIGGER` in `AAkPay.recurringPaymentUpd` line 205, and the 852 `batchProcessor.statusUpdate` errors on `Database.update(paymentTxnList)`. Offer it to AAkonsult as a hypothesis, not a finding, but offer it, because it changes what they look at.

`Block_Reconciled_Changes` (validation rule on `npe01__OppPayment__c`, created by Nina Lewis 8 Dec 2025) also sits in this path. A reconciled Payment cannot be manually corrected, but the realtime DLRS still rolls its values up. Manual correction and automated rollup obey different rules.

## 5. BirdLife's own Flows on Payments2Us objects

Thirteen active record-triggered Flows sit on Payments2Us and Payment objects. These are BirdLife's, not the vendor's, which means they are yours to change and yours to break.

### On `AAkPay__Payment_Txn__c` (4)

| Flow | Type | Modified | What it does |
|---|---|---|---|
| `Payment_Txn_aCU_Payment_and_GAU_Creation` | After save | 2026-06-30 | **The NPSP bridge.** Creates `npe01__OppPayment__c` and GAU allocations. The single most important custom flow in the estate |
| `Payment_Txn_aCU_Batch_Entry_and_Batch_Entry_Line_Creation` | After save | 2024-05-21 | Creates Batch Entry and Batch Entry Line records |
| `Payment_Txn_After_Insert_or_Update_if_Membership_update_Membership_Option` | After save | 2022-08-21 | Sets Membership Option on membership payments |
| `Payment_Txn_After_insert_if_Country_is_Afghanistan_update_to_Australia` | After save | 2023-02-16 | Fixes the AF/AU country code collision |

### On `AAkPay__Recurring_Payment__c` (4)

| Flow | Type | Modified | What it does |
|---|---|---|---|
| `Recurring_Payment_Before_Insert_Flow` | Before save | 2022-02-21 | Field defaulting |
| `Recurring_Payment_aCU_Status_Changed` | After save | 2023-10-21 | Reacts to status transitions |
| `Recurring_Payment_After_insert_send_Welcome_to_Wildbird_Regular_Giving_Email` | After save | 2022-12-10 | The Wildbird welcome email. Pairs with `AAkPay__Welcome_Email_Sent__c` |
| `Recurring_Payment_After_Update_when_new_or_status_is_changed_to_active...` | After save, **scheduled path** | 2023-10-01 | Scheduled delay, then writes Pay Method onto the Subscription. A scheduled path means the effect is not immediate; do not diagnose it as failed within the first hour |

### On `AAkPay__Subscription__c` (6)

| Flow | Type | Modified | What it does |
|---|---|---|---|
| `Reactive_Subscription_and_Recurring_Payment` ("Reactivate Subscription") | Before save | 2023-12-21 | Reactivation path |
| `Update_Checked_details_on_Check` | Before save | 2023-05-16 | Sets `Checkedby__c` and `LastCheckedDate__c` from `CheckStatus__c` |
| `Subscription_aCU_Program_Engagement` | After save | 2023-07-26 | Creates or updates `pmdm__ProgramEngagement__c` |
| `Subscription_aCU_Program_Engagement_for_Groups` | After save | 2023-08-20 | Same, for special interest groups |
| `Membership_Email_Renewal_Category_Change` | **Scheduled trigger** | 2022-03-21 | Renewal email where the category changed |
| `Membership_Email_Renewal_No_Change` | **Scheduled trigger** | 2022-03-21 | Renewal email, no change |

The two Program Engagement flows matter beyond Payments2Us: they are why `pmdm__ProgramEngagement__c` carries a second, parallel definition of "active membership", rolled up by `Active_Memberships` into `Contact.ActiveMemberships__c`. **Two definitions of membership exist in this org from two different source objects. Never mix them in one report.**

### On `npe01__OppPayment__c` (Payment) (4)

| Flow | Type | Modified | What it does |
|---|---|---|---|
| `Payment_bCU_Negate_Woo_Refund_Amount` | Before save | **2026-09-02** | Negates WooCommerce refund amounts |
| `Create_Refund_Postage` | After save | **2026-09-02** | Refund postage handling |
| `Payment_aCU_Bank_Transfer_and_Reallocate` | After save | 2025-02-10 | Bank transfer reallocation |
| `Remove_Auto_Created_Payment_Major_Donor_Only` | After save | 2026-03-26 | Suppresses the NPSP auto-payment for Major Donor and Bequest |

The two flows dated 2 September 2026 are recent remediation of the WooCommerce refund defect, where refunds created a positive Payment. **Before repeating the older "refunds are broken" finding, check whether these have closed it.** Test with a real refund in staging.

### Upstream on Opportunity, same money path

`Stripe_aCU_Opportunity_Get_Balance_Transaction` (2026-09-02), `GAU_Allocate_Rounding_to_Highest_Opp` (2025-12-12), `Opportunity_aCU_Product_Sale` (2026-07-31), `Opportunity_aC_Calculate_missing_Postage` (2026-07-21), `Manage_Opportunities_1`, `Opportunity_Loop_through_GAU_allocations_and_roll_up_tax_deductible_and_non_deductible_amounts`, `Opportunity_Before_Insert_Flow`, `Opportunity_Before_Update_Flow`, `Opportunity_aCU` (Set Name on Product Sale).

And **23 active record-triggered Flows on Contact**, on top of the managed `AAkPay.contactUpd` trigger, `dlrs_ContactTrigger`, `ContactDuplicateEmailTrigger` and the 13 other Contact triggers. Contact is the most heavily automated object in the org and Payments2Us adds to it on every payment.

## 6. The DLRS layer, all nine rollups touching Payments2Us

Declarative Lookup Rollup Summaries (`dlrs` namespace, 118 classes) carry rollups Salesforce cannot do natively. Realtime rollups fire through an unmanaged trigger; Scheduled rollups run nightly and are therefore stale by up to 24 hours.

| Rollup | Parent | Child | Mode | Criteria | Result field |
|---|---|---|---|---|---|
| `Last_Payment_Txn_Date` | Recurring Payment | Payment Txn | **Realtime** | none | `LastPaymentTxnDate__c` (Max CreatedDate) |
| `No_of_RP_Change_Logs` | Recurring Payment | `RP_Change_Log__c` | **Realtime** | none | `NoofRPChangeLogs__c` |
| `Payment_Fee_at_Payment_Txn` | Payment Txn | `npe01__OppPayment__c` | **Realtime** | none | `Payment_Fee__c` |
| `Payment_Gross_at_Payment_Txn` | Payment Txn | `npe01__OppPayment__c` | **Realtime** | none | `Payment_Gross__c` |
| `ActiveRPbyDD` | Contact | Recurring Payment | **Realtime** | `Status = 'Active' AND Merchant_Facility_Name__c = 'BirdLife DONATIONS Facility'` | `No_of_Active_RPs__c` |
| `ActiveBirdlifeMemberships` | Contact | Subscription | Scheduled 05:20 | `(Approved AND Payment_Form__c='Birdlife Membership') OR (Approved AND Subscription__c='Lifetime Membership')` | `No_of_active_BL_Memberships__c` |
| `ActiveSIGMemberships` | Contact | Subscription | Scheduled 04:30 | `Approved AND Special_Interest_Group__c = TRUE` | `No_of_active_SIG_Memberships__c` |
| `PrintMagazineFromSubscriptions` | Contact | Subscription | Scheduled 06:00 | `AAkPay__Payment_Option__r.EligibleForPrintMagazine__c = TRUE AND Approved` | `BirdLifePrintMagazineFromMembership__c` |
| `NumberRecurringPayments` | Subscription | Recurring Payment | Scheduled 02:15 | `Payment_Type__c = 'Membership'` | `No_of_Recurring_Payments__c` |

Supporting unmanaged triggers: `dlrs_AAkPay_Payment_TxnTrigger` (API 59), `dlrs_AAkPay_Recurring_PaymentTrigger` (API 51), `dlrs_AAkPay_SubscriptionTrigger` (API 51), `dlrs_RP_Change_LogTrigger` (API 59), plus `dlrs_ContactTrigger`, `dlrs_OpportunityTrigger`, `dlrs_npe01_OppPaymentTrigger`, `dlrs_npsp_AllocationTrigger`, `dlrs_pmdm_ProgramEngagementTrigger`.

**Two hardcoded strings to guard.** `ActiveRPbyDD` hardcodes `Merchant_Facility_Name__c = 'BirdLife DONATIONS Facility'`, `ActiveBirdlifeMemberships` hardcodes `Payment_Form__c = 'Birdlife Membership'`. Rename either record and the rollup silently returns zero. Neither has a validation or test protecting it.

## 7. The Active_BL_Member__c chain, proved end to end

The most consequential BirdLife-specific plumbing in the package, documented nowhere else.

```
AAkPay__Subscription__c
   |  DLRS "ActiveBirdlifeMemberships" (m0RI80000000022), Scheduled, daily 05:20 AEST
   |  Parent Contact via AAkPay__Contact__c
   |  Criteria: (Membership_Status = 'Approved' AND Payment_Form__c = 'Birdlife Membership')
   |         OR (Membership_Status = 'Approved' AND Subscription__c = 'Lifetime Membership')
   v
Contact.No_of_active_BL_Memberships__c
   v
Contact.Active_BL_Member__c
   v
Taylor and Francis, Emu journal access
```

**Proof:** Contacts with `No_of_active_BL_Memberships__c > 0` = 7,653. Contacts with `Active_BL_Member__c = true` = 7,653. Exact match. Approved subscriptions on the `Birdlife Membership` form = 7,519, the remainder Lifetime Memberships and Contacts holding more than one.

**Three failure modes to hold permanently:**

1. **Hardcoded literal string** `Payment_Form__c = 'Birdlife Membership'`, lowercase l. It breaks if the membership rebuild moves memberships to WooCommerce (no matching Subscription is created), if anyone renames the form, or if anyone recreates the rollup with the "correct" BirdLife capitalisation believing they are fixing a typo. In every case the rollup returns zero overnight and **7,653 members lose Emu journal access the next morning with no error anywhere.** The migration plan must take over this flag explicitly, and the cutover test is the two counts above.
2. **No `End_Date__c` test.** It relies entirely on the 06:00 job flipping status, and it runs at 05:20, forty minutes earlier. `Active_BL_Member__c` is permanently one day behind reality.
3. **SIG memberships are deliberately excluded** and roll up separately (1,074 Contacts). A Photography or Wader Studies member is not a BirdLife member. Correct by design.

**The membership number has three defensible answers. Always say which one you mean.**

| Question | Query | Order of magnitude |
|---|---|---|
| Approved membership records | `Membership_Status__c = 'Approved'` | ~8,900 |
| Current memberships | `Membership_Status__c = 'Approved' AND End_Date__c >= TODAY` | ~8,800 |
| Contacts flagged as BirdLife members | `Contact.Active_BL_Member__c = true` | ~7,650 |

The difference between the first and third is SIG and other-form memberships, not an error.

## 8. The scheduled architecture

### Why 1,005 aborted jobs a week is normal

The batch processor does **not** use a repeating cron. Each cycle it schedules a fresh single-fire job named `batchPaymentsProcessor<epoch-ms>_<counter>` with a one-shot cron expression, then aborts the previous one. Observed: `batchPaymentsProcessor1789082197274_760`, cron `37 26 9 11 9 ? 2026`. At `AAkPay__Batch_Frequency__c = 10` that is a new job every ten minutes.

In `AsyncApexJob` over 7 days: `batchProcessor` **Aborted** ScheduledApex 1,005, `batchProcessor` Completed BatchApex 1,005, `contactUpdateProcessor` Completed BatchApex 1,005. **The aborts are the design, not a failure.** Exclude `batchProcessor` from any generic aborted-job alert or it fires every week forever.

The real failure mode is the rescheduler losing its place. On 16 and 17 April 2026 the Error Log recorded `batchProcessor.schedule` "submit batch failed 6 times", then 12, 18, 24, 30, 36, 42, 48, 54, hourly across a full day. That escalating sequence is the signature.

`paymentStatusCheckProcessor` and `paymentTxnExtShareLockProcessor` run 57 times per 7 days. `URLTokenQueueable` about 39 times, so the token mechanism is alive.

**All nine merchant facilities show `AAkPay__Batch_Processor_Status__c = Started` and are polled every 10 minutes**, including six inactive ones with 2023 licences. Stop the six. It is wasted Apex and it makes diagnosis lie to you.

### The daily schedule (AEST, cron evaluates in org time)

| Job | Schedule | Function |
|---|---|---|
| `batchPaymentsProcessor...` | every 10 min | Payment processing engine |
| `recurPayments` | 01:00 | The recurring charge run. Writes `AAkPay__Last_Recurring_Payment_Run__c` |
| `rollup_NumberRecurringPayments` | 02:15 | DLRS onto Subscription |
| `rollup_Active_Memberships` | 04:00 | DLRS from Program Engagement, not Payments2Us |
| `rollup_ActiveSIGMemberships` | 04:30 | DLRS onto Contact |
| `rollup_ActiveBirdlifeMemberships` | **05:20** | DLRS driving `Active_BL_Member__c` |
| `Subscriptions_Expired_and_Ceased_Memberships-2` | **06:00** | Flips Approved to Expired and Ceased |
| `rollup_PrintMagazineFromSubscriptions` | **06:00** | DLRS driving print magazine eligibility |
| Conga Batch-0008 | 19:00 | Receipts, 50 to 200 per day |

**Two timing defects.** The membership rollup runs 40 minutes before the expiry job, so it always evaluates yesterday's statuses. And the print magazine rollup runs in the same minute as the expiry job, so the print list is non-deterministic at the boundary. Separate them.

## 9. The managed trigger surface

42 AAkPay triggers. On AAkPay objects: `paymentTxnUpd`, `recurringPaymentUpd`, `subscriptionUpd`, `subscriptionIssueUpdate`, `subscriberGroupUpd`, `paymentSettingUpd`, `paymentTypeUpd`, `paymentOptionUpd`, `paymentItemTrigger`, `directDebitBatchUpd`, `batchEntryTrigger`, `BatchEntryLineTrigger`, `changeScheduleUpd`, `accountSubscriptionUpd`, `URLTokenUpd`, `VoucherTrigger`, `ticketTrigger`, `letterTriggerUpdate`, `PeerToPeerCampaignTrigger`, `ImportFileTrigger`, five Bank* triggers, five Xero triggers, `BatchApexErrorEventTrigger`.

**On standard objects, where the hidden cost lives:**

| Trigger | Object | Contexts |
|---|---|---|
| `contactUpd` | Contact | before/after insert, before/after update |
| `accountUpd` | Account | all four |
| `opportunityUpdate` | Opportunity | before/after insert, before update |
| `leadUpd` | Lead | all four |
| `campaignUpdate` | Campaign | before/after insert, before update |
| `campaignMemberUpd` | CampaignMember | before/after insert, before update |
| `caseUpd` | **Case** | before/after insert, before update |
| `activityUpdate` | Task | before insert, before update |
| `attachmentUpdate` | Attachment | after insert, after update |
| `ContentDocumentLinkTrigger` | ContentDocumentLink | all four |

**Payments2Us fires on every ICT helpdesk Case.** 53,000 email-origin cases in the Zeus queue. Payments2Us is a dependency of the helpdesk, not only of fundraising, and nobody would guess that from the product name.

**Payments2Us fires on every Contact change** in a 480,000-Contact org. Any upgrade or uninstall is an org-wide regression event across Contact, Account, Opportunity, Lead, Campaign, CampaignMember, Case, Task, Attachment and ContentDocumentLink. Never let anyone describe an uninstall as "just removing the payments app".

### Managed classes worth recognising in a stack trace

| Class | Function |
|---|---|
| `batchProcessor` | The 10-minute self-rescheduling engine |
| `contactUpdateProcessor` | Same cycle |
| `recurringPaymentsProcessor`, `recurringPaymentQueueable` | Daily recurring charge run |
| `recurringCPIProcessor`, `recurringCPIProcessorInvoker` | Annual CPI uplift via `AAkPay__I_agree_to_annual_CPI_Increases__c` |
| `directDebitBatchExtractProcessor` | Builds the ABA file |
| `directDebitBatchChargeProcessor`, `directDebitBatchBulkProcessor`, `directDebitUtil` | DD charge run |
| `paymentMatchingUtil` | Contact, Account, Opportunity and Campaign Member matching and creation |
| `paymentStatusCheckProcessor` | Polls gateway for pending outcomes |
| `paymentTxnExtShareLockProcessor` | External sharing locks on Payment Txn |
| `PaymentTxnArchiveProcessor` | Writes to `AAkPay__Payment_Txn_Archive__b` big object |
| `URLTokenQueueable` | Issues self-service tokens |
| `HealthCheckMerchantFacilityProcessor` / `...UserPermissionProcessor` / `...WorkflowsProcessor` | The three Health Check domains. Beta, introduced in version 11.0, creates a "License Expiring" item against the facility |
| `payments2UsWebhook`, `payments2UsWebhookPaymentCompleteREST` | Webhook API, installed but **not licensed** on either live facility |
| `subscriptionsUpdate.checkRecurring` | Source of the live SELF_REFERENCE error |
| `payments2UsBillingCheckProcessor`, `payments2UsBillingFetchQueueable` | Vendor billing retrieval |

Dead vendor code for gateways BirdLife does not use: `authorizeNetSettledBatchProcessor`, `EziDebitGetPaymentsProcessor`, `BlackBaudSettlementProcessor`, `GlobalPaymentsOceaniaSettlementProcessor`, `payfURLSettlementProcessor`, `importFileWindcaveUploadProcessor`, `BBMSStoreTokenQueueable`. Useful only for reading a stack trace.

## 10. BirdLife's unmanaged Apex, and the API version debt

134 unmanaged Apex classes and 16 unmanaged triggers. Relevant to the payment path:

| Class | Size | API | Role |
|---|---|---|---|
| `CreateGauAllocations` | 8,992 | 67 | GAU allocation from the payment flow |
| `ContactDuplicateEmailService` | 10,452 | 67 | 1,785 Queueable runs / 7 days |
| `FindBestMatchContact` | 3,625 | 63 | Contact matching |
| `RDChangeLogTriggerHandler` | 5,072 | 52 | Recurring Donation change log |
| `RaiselyHttpCallouts` | 3,530 | 52 | Raisely integration |
| `myBirdlifeConfigSelfReg` | 5,241 | 57 | Portal self-registration |
| `UpdateContactLoginTimeBatch` | 7,515 | 58 | Hourly at :15 and :45 |
| `SendBetterEmail` suite | 23,705 + 61,400 test | 51 | UnofficialSF email action used by Flows |
| Collection processor library (`SortCollection`, `FilterCollection`, `MapCollection`, `CollectionCalculate`, `DeepClone`, ~30 classes) | various | 57 to 59 | UnofficialSF Flow actions |
| `MetadataService` | **787,158** | **34** | FinancialForce metadata library |

**The API version debt is a real finding.** `MetadataService` and its 20 companion classes sit at **API 34 (Summer 2015)**; `AppConstants`, `CSVFileUtil`, `CustomMetadata*` at 34; `JsonUtilities` and the Metadata* family at 39. Salesforce retires old API versions on a rolling basis and each retirement breaks whatever still targets it. `MetadataService` at 787KB is also close to Apex size limits. Not a Payments2Us problem, but it sits in the same org and it will bite. Raise it with Karishma Soni as a technical debt item with a named retirement date, not as an opinion.

## 11. The public web surface

Eleven Sites, five Active and relevant, all four Payments2Us Sites LastModified 2026-07-30.

| Site | Subdomain + path | Guest user |
|---|---|---|
| Membership | `birdlife` + `/Membership` | 0055g00000DqVRuAAN |
| Membership_Renewal | `birdlife` + `/membership` | 0055g00000DqUa2AAF |
| Update_card_details | `birdlife` + `/updateCardDetails` | 0055g00000DqUa4AAF |
| Update_DD_Bank_details | `birdlife` + `/updateBankDetails` | 0055g00000DqUa3AAF |
| Integration | `birdlife` | 005I8000000Ik64IAC |
| myBirdLife2 / myBirdLife21 | `supporters` | 005I8000000J0n0IAC |

Inactive: Birdlife_Community_Portal, Birdlife_Community_Portal1, Login, Login1.

**The case trap.** `Membership` and `Membership_Renewal` share the subdomain and differ only by the capitalisation of the path, `/Membership` against `/membership`. Anyone writing a link into a Conga template or an Ortto email will get this wrong eventually.

**Four guest users, four permission surfaces.** A permissions audit must cover all four. This sits against the org finding of guest profiles with Edit on 45 objects.

**The mandatory July 2026 hardening.** AAkonsult requires "Lightning Features for Guest Users" disabled on every Site hosting a Payments2Us form, in production and every sandbox. Standard forms are unaffected; custom implementations must be revalidated. The Site object does not expose that checkbox to a query. **Verify it in Setup on all five before treating it as closed.**

`Update_card_details` is the endpoint behind the expired-card problem. The flow is: Payments2Us issues an `AAkPay__URL_Tokens__c` record, the token is embedded in a link sent to the supporter, the link resolves to that Site, `URLTokenUpd` fires on the token record. `URLTokenQueueable` runs about 39 times per 7 days. Against roughly 2,190 expired cards, that rate is far too low. Either reminders are not being sent or they are not converting.

## 12. Recurring Payments

Status values: `Awaiting Account Verification`, `Active`, `Suspended - Max retries exceeded`, `Expired`, `Cancelled AR`, `Cancelled`, `Inactive`, `Suspended`.
Frequency: Daily, Weekly, Fortnightly, 4 Weeks, Monthly, Bi-Monthly, Quarterly, Six Monthly, Annually, Two Yearly.
Payment Method (multi): Credit Card, Invoice Me, Send By Post, Pledge, Bank Transfer, PayPal, Direct Debit.
Cancellation Reason: Financial, Employment changes, Moving (interstate or overseas), Changed mind, Thought single gift only, Public image issue with organisation, Don't agree with campaigns, Fraudulent sign-up, Unspecified, Deceased.
Payment Day: `01` to `28` zero-padded, plus `Last`. No 29, 30 or 31 by design.

**Do not quote 392 as the active recurring count.** That is Monthly only. At extract the true active total was 5,336 (4,934 Annually, 392 Monthly, 8 Yearly, 1 Quarterly, 1 Six Monthly) worth roughly $371,000 per annual cycle. The `birdlife-salesforce` skill's "392 active" line is monthly regular giving only.

Regular giving spans **both** NPSP Recurring Donations and AAkPay Recurring Payments. Any number from one object alone is wrong.

**Standing finding: roughly 2,190 Active Recurring Payments carry a card expiry date in the past, about 41% of the active book**, plus around 565 in `Suspended - Max retries exceeded`. The flags are `AAkPay__Expiry_Reminder__c` and `AAkPay__Resend_Card_Expiring__c`. ICT owns the evidence, Fundraising owns the outreach.

Encrypted, not reportable: `AAkPay__Account_No__c`, `AAkPay__BSB_No__c`, `AAkPay__Expiry_MMYYYY__c`, `AAkPay__Routing_Number__c`. Card token `AAkPay__DpsBillingId__c`, masked PAN `AAkPay__Payment_CC_No__c`, last four `AAkPay__Card_Last_4_Digits__c`. `AAkPay__Is_BECS__c` and the `BECS` gateway option are the hooks for the BECS migration work.

Field history tracking is on. `RP_Change_Log__c` carries change history with a realtime DLRS count into `NoofRPChangeLogs__c`.

## 13. Subscriptions and membership

Membership Status: `New`, `Approved`, `Awaiting Account Verification`, `Suspended - Max retries exceeded`, `Expired`, `Ceased`, `Cancelled`. Renewal Reminder: `Set Reminder`, `1st` to `4th Reminder`, `Cancelled`. CheckStatus: `All OK`, `Needs Review`, `Waiting on External`. Never invent a value.

BirdLife business rules on fields: `Cease_Date__c` (voting rights end about three months after End Date), `Overseas_Member__c`, `Missed_Print_Window__c`, `Special_Interest_Group__c`, `Gift_Membership_Donor__c`, `Auto_Renewal_Expiry_Date__c`. `No_of_Recurring_Payments__c` above 1 signals a data problem.

`Cease_Notification__c`, `Expiry_Notification__c` and `Renewal_Notification__c` are **set by Conga**, not by Payments2Us.

About 55 of the 147 Subscription fields are Conga Composer URL button formulas (`Conga_*`, `Q2_*`, `Q3_*`, `SP5_*`, `SP6_*`, `SP7A_*`, `SP7B_*`) generating every renewal, expiry and cease notice. That is the inventory to rebuild in S-Docs.

## 14. Direct debit

Runs **monthly around the 20th**, three batches: one large DONATIONS batch of roughly 390 to 415 payments worth $15,000 to $18,000, plus two small MEMBERSHIP batches. Names `DD00002xx`.

Status lifecycle: `New` (default), `Extracted`, `Charge Processing Started`, `Charge Processing Completed`, `Complete`, with `Cancelled` as the exit.

`AAkPay__Processing_Date__c` sets the Banking Date on each Payment Txn and defaults to today at extract. Get it wrong and the reconciliation date is wrong.

ABA format on both live facilities. `AAkPay__No_in_Last_Extracted_File__c` may be one higher than the batch count because of the self-balancing transaction controlled by `AAkPay__Include_a_Self_Balancing_transaction__c`. Not an error.

Processor classes: `directDebitBatchExtractProcessor`, `directDebitBatchChargeProcessor`, `directDebitBatchBulkProcessor`, `directDebitUtil`.

**If no batch has appeared by the 21st of a month, direct debit has failed silently and roughly $16,000 has not been collected.** The DONATIONS batch also fails one to two payments every month and nobody chases them, roughly fifteen supporters a year lost quietly. Batch numbers have gaps (DD0000199 and DD0000192 missing), so sequence is not an audit trail.

## 15. Receipting is not Payments2Us

All nine `AAkPay__Letter__c` records are AAkonsult demo templates prefixed `DEMO:`, unmodified since February 2022. **BirdLife does not use the Payments2Us receipting engine at all.** Every receipt, renewal, expiry and cease notice comes from Conga, driven by the Conga URL formula fields on Subscription and Conga Batch-0008 nightly at 19:00 AEST.

Two consequences: the Conga replacement is a Payments2Us dependency, not a parallel project; and there is no fallback, because pushing Payments2Us into receipting would mean building the templates from scratch.

`AAkPay__Send_Receipt__c` on Payment Form and Recurring Payment: `Yes - PDF Version`, `Yes - PDF Version - Skip Recurring`, `Yes - Interim`, `No - Skip Receipting`, `No - Manually mark as Receipted`.

## 16. Finance side

20 of the 80 objects are the Xero bridge. BirdLife runs NetSuite, so a quarter of the object footprint is dead weight.

`AAkPay__Payment_Setting__c.BirdLife_Bank_Account__c` is a BirdLife custom picklist with values `11103 (Australian Bird Fund)` and `11104 (Operations account)`, built to map facilities to NetSuite GL accounts and **left null on all nine facilities**. The finance integration was designed and never finished, which is why Payments2Us income lands in manual reconciliation. Raise with Nina Lewis and Peggy Dias against the unreconciled income backlog.

The live GL path today runs through `Payment_Txn_aCU_Payment_and_GAU_Creation` into GAU allocations, then `GAU_Allocate_Rounding_to_Highest_Opp` and `Opportunity_Loop_through_GAU_allocations...` for tax-deductible splitting. That is BirdLife-built Flow, not vendor function, and it is yours to maintain.

## 17. Live defect register

| # | Defect | Action |
|---|---|---|
| R1 | Licence expiry 30 Nov 2026 on both live facilities | Renewal terms from AAkonsult, decision to ICT Steering Group |
| R2 | ~2,190 Active Recurring Payments with expired cards, 41% of the book | List to Fundraising, verify the URL token reminder mechanism fires |
| R3 | `SELF_REFERENCE_FROM_TRIGGER` in `AAkPay.recurringPaymentUpd` line 205 from `subscriptionsUpdate.checkRecurring`, 45 times in 180 days, still firing September 2026 | AAkonsult case with the Error Log IDs. Offer the circular-path hypothesis from section 4. Never patch a managed package |
| R4 | Error Log unmonitored: 1,831 `DirectDebitBulkProcessor` and 852 `batchProcessor.statusUpdate` errors untriaged | Add `AAkPay__Error_Log__c` to the monitoring instrument |
| R5 | Health Check run once, February 2026 | Run it, read the items, schedule it |
| R6 | ~565 Recurring Payments suspended on max retries | Recovery list to Fundraising |
| R7 | Membership rollup depends on a hardcoded `'Birdlife Membership'` string and runs 40 min before the expiry job | Take over explicitly in the membership rebuild; cutover test is the two counts |
| R8 | Batch processor polling six dead facilities every 10 minutes | Set their Batch Processor Status to Stopped, staging first |
| R9 | `BirdLife_Bank_Account__c` null on all facilities | Populate, agree treatment with Finance |
| R10 | 24 dormant payment forms, 6 dormant facilities | Prefix `ZZ_RETIRED_` so they cannot be picked by accident |
| R11 | 28 Recurring Payments with orphaned `Yearly` frequency | Data fix to `Annually` after checking report dependencies |
| R12 | Print magazine rollup races the expiry job at 06:00 | Move one of them |
| R13 | Mandatory July 2026 Sites hardening on all five Payments2Us Sites | Verify in Setup, do not assume |
| R14 | `ActiveRPbyDD` hardcodes the merchant facility name | Guard it, or make it criteria-free and filter downstream |
| R15 | Unmanaged Apex at API 34 and 39, including a 787KB `MetadataService` | Technical debt item with a retirement date, to Karishma Soni |
| R16 | Circular path: Payment Txn to OppPayment to realtime DLRS back to Payment Txn | Likely root of R3 and the statusUpdate errors. Test in staging before proposing a change |

## 18. Verification queries

```sql
-- Still processing?
SELECT COUNT(Id) FROM AAkPay__Payment_Txn__c WHERE CreatedDate = LAST_N_DAYS:7

-- The deadline
SELECT Name, AAkPay__License_Expiry_Date__c, AAkPay__License_Options__c
FROM AAkPay__Payment_Setting__c WHERE AAkPay__Active__c = true

-- Did direct debit run this month?
SELECT Name, CreatedDate, AAkPay__Status__c, AAkPay__No_in_Batch_RUS__c,
       AAkPay__No_Completed_RUS__c, AAkPay__No_In_Error_RUS__c,
       AAkPay__Total_Batch_Amount_RUS__c, AAkPay__Payment_Setting__r.Name
FROM AAkPay__Direct_Debit_Batch__c ORDER BY CreatedDate DESC LIMIT 6

-- Cards killing the regular giving book
SELECT COUNT(Id) FROM AAkPay__Recurring_Payment__c
WHERE AAkPay__Recurring_Payment_Status__c = 'Active' AND AAkPay__Card_Expiry_Date__c < TODAY

-- True active recurring, by frequency
SELECT AAkPay__Frequency__c, COUNT(Id), SUM(AAkPay__Payment_Amount__c)
FROM AAkPay__Recurring_Payment__c WHERE AAkPay__Recurring_Payment_Status__c = 'Active'
GROUP BY AAkPay__Frequency__c

-- The three membership numbers, and the rollup chain
SELECT COUNT(Id) FROM AAkPay__Subscription__c WHERE AAkPay__Membership_Status__c = 'Approved'
SELECT COUNT(Id) FROM AAkPay__Subscription__c WHERE AAkPay__Membership_Status__c = 'Approved' AND AAkPay__End_Date__c >= TODAY
SELECT COUNT(Id) FROM Contact WHERE Active_BL_Member__c = true
SELECT COUNT(Id) FROM Contact WHERE No_of_active_BL_Memberships__c > 0
SELECT COUNT(Id) FROM AAkPay__Subscription__c WHERE AAkPay__Membership_Status__c = 'Approved' AND Payment_Form__c = 'Birdlife Membership'

-- The DLRS layer touching Payments2Us
SELECT DeveloperName, dlrs__ParentObject__c, dlrs__ChildObject__c, dlrs__RelationshipCriteria__c,
       dlrs__AggregateResultField__c, dlrs__CalculationMode__c, dlrs__Active__c
FROM dlrs__LookupRollupSummary2__mdt WHERE dlrs__ChildObject__c LIKE 'AAkPay%'

-- Every active Flow on a Payments2Us object
SELECT ApiName, Label, TriggerType, TriggerObjectOrEventLabel, LastModifiedDate
FROM FlowDefinitionView WHERE IsActive = true AND TriggerObjectOrEventLabel IN
('Payment Txn','Recurring Payment','Subscription','Payment') ORDER BY TriggerObjectOrEventLabel

-- The managed trigger surface
SELECT Name, TableEnumOrId, Status FROM ApexTrigger WHERE NamespacePrefix = 'AAkPay' ORDER BY TableEnumOrId

-- Scheduled jobs
SELECT CronJobDetail.Name, CronExpression, State, NextFireTime, PreviousFireTime, TimesTriggered
FROM CronTrigger ORDER BY NextFireTime NULLS LAST

-- Batch processor health (expect roughly equal Aborted ScheduledApex and Completed BatchApex)
SELECT ApexClass.Name, Status, JobType, COUNT(Id) FROM AsyncApexJob
WHERE CreatedDate = LAST_N_DAYS:7 GROUP BY ApexClass.Name, Status, JobType ORDER BY COUNT(Id) DESC

-- What is erroring now
SELECT Name, CreatedDate, AAkPay__Program_Area__c, AAkPay__Subject__c, AAkPay__Description__c
FROM AAkPay__Error_Log__c WHERE CreatedDate = LAST_N_DAYS:30 ORDER BY CreatedDate DESC

-- Which forms are actually live
SELECT AAkPay__Payment_Type__r.Name, AAkPay__Payment_Setting__r.Name, COUNT(Id)
FROM AAkPay__Payment_Txn__c WHERE CreatedDate = LAST_N_DAYS:365
GROUP BY AAkPay__Payment_Type__r.Name, AAkPay__Payment_Setting__r.Name ORDER BY COUNT(Id) DESC

-- Subscriptions with more than one recurring payment, a data health check
SELECT Id, Name, No_of_Recurring_Payments__c FROM AAkPay__Subscription__c
WHERE No_of_Recurring_Payments__c > 1 LIMIT 50

-- Unmanaged Apex API version debt
SELECT Name, ApiVersion, LengthWithoutComments FROM ApexClass
WHERE NamespacePrefix = null AND ApiVersion < 45 ORDER BY ApiVersion
```

## 19. Diagnostic order for the common questions

**"My regular gift stopped."** `AAkPay__Recurring_Payment__c` for that Contact: `Recurring_Payment_Status__c`, then `Card_Expiry_Date__c`, then `Last_Declined_Date__c` and `Retry_Attempts__c`, then `LastPaymentTxnDate__c` (realtime, trustworthy). Suspended on max retries plus a past card expiry is the common answer, and the fix is the `updateCardDetails` Site, not a manual edit.

**"The direct debit did not run."** Latest `AAkPay__Direct_Debit_Batch__c` and its Status; then `AAkPay__Last_Recurring_Payment_Run__c` on the facility; then `AAkPay__Error_Log__c` for the last 7 days; then the licence expiry. Only then call AAkonsult.

**"The payment is there but finance cannot see it."** The bridge is `Payment_Txn_aCU_Payment_and_GAU_Creation`. Check the Flow ran, check `npe01__OppPayment__c` exists, check GAU allocations, check `Payment_Fee__c` and `Payment_Gross__c` rolled back onto the Payment Txn. A break anywhere in that chain looks identical from the supporter side.

**"A supporter did not get their receipt."** Not a Payments2Us problem. Go to `birdlife-conga` and Conga Batch-0008.

**"Members lost journal access."** Section 7. Run the two counts. If `No_of_active_BL_Memberships__c > 0` returns zero or near zero, the rollup criteria has stopped matching.

**"Someone edited a form and nothing changed."** Check it was one of the seven live forms.

**"How many members do we have."** Give the three answers and say which one the audience needs.

## 20. Change discipline

1. **Never edit the managed package.** All 736 AAkPay classes and 42 triggers are vendor-owned. Broken means a support case.
2. **The unmanaged layer is yours.** 13 Flows, 9 DLRS rollups and the unmanaged triggers on Payments2Us objects are BirdLife's. Changing one is a real change with a real blast radius. Staging first, always.
3. **Staging differs deliberately.** Membership subscription periods are 1 day in staging and 1 year in production, and every record ID differs.
4. **Never assert a picklist value you have not read from the org.**
5. **Confirm the record is live before editing.** 24 of 31 forms and 6 of 9 facilities are dead.
6. **Trace the whole stack before changing one layer.** Managed trigger, then unmanaged DLRS trigger, then Flow, then rollup. Changing a Flow without checking the rollup that reads its output is how a silent break happens.
7. **Licence impact.** The org sits at 70 of 70 full Salesforce licences. Anything needing a new user must name the one being released.
8. **Money system tier.** Any change touching a live merchant facility, a live payment form, the DD batch or the GAU creation flow is Tier 2: prepared by ICT, executed by a named runner with a rollback and a proving query, never ad hoc.
9. **Upgrade and uninstall are org-wide regression events**, because AAkPay triggers sit on Contact, Account, Opportunity, Lead, Campaign, CampaignMember, Case, Task, Attachment and ContentDocumentLink.

## 21. People

Mathew Hema owns the system and the vendor relationship. Keith Tsui is second operator. Nina Lewis needs sections 16 and 17 and owns the `Block_Reconciled_Changes` validation rule on `npe01__OppPayment__c`. Peggy Dias runs the daily bank reconciliation that Payments2Us income lands in. Karishma Soni needs sections 4, 5, 6, 7 and 10 before touching membership or the refund work. Veronica and Fundraising own the recurring payment recovery lists. Downstream of a mistake: about 7,650 flagged members, every direct debit donor, and Emu journal access.

Vendor: AAkonsult, `help.payments2us.com`, support requests at `payments2us.com/log-a-request`. Grant login access and quote the org ID when raising a case.