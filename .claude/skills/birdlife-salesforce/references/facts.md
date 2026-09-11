# Salesforce (Zeus): facts

The lookup table for `birdlife-salesforce`. Every value here is copied from a
verified read; the SKILL.md prose explains what the values mean. **When a value
changes, edit this file first, then the prose.** Dates are the verification
date; re-verify anything older than 90 days before asserting it.

## Org

| Fact | Value | Verified |
|---|---|---|
| Production (Lightning) | `https://birdlifeaustralia.lightning.force.com` | Jun 2026 |
| Production (API) | `birdlifeaustralia.my.salesforce.com` | Jun 2026 |
| Setup | `birdlifeaustralia.my.salesforce-setup.com` | Jun 2026 |
| Staging sandbox | `birdlifeaustralia--staging.sandbox.my.salesforce.com` | Jun 2026 |
| Edition / instance / currency / TZ | Enterprise / AUS92 / AUD / AEST (GMT+10) | Jun 2026 |
| Data model | NPSP, Household Account model | Jun 2026 |
| Org created | 25 Jan 2021, by Reza Torkman | Jun 2026 |
| Objects | 424 via `getObjectSchema` index (KB says 439 custom; reconcile before quoting) | Aug 2026 |
| Full licences | 70 of 70 consumed | Jun 2026 |
| Case intake address | `zeus@birdlife.org.au` | Jun 2026 |
| Case link pattern | `https://birdlifeaustralia.lightning.force.com/lightning/r/Case/{Id}/view` | Aug 2026 |

## Connectors

| Display name (exact, with spaces) | Use |
|---|---|
| `Salesforce Production` | Live org; propose-then-write, one record at a time |
| `Salesforce Staging` | Experiments, write-response shapes, structural tests |

Tools on both: `soqlQuery`, `getObjectSchema`, `find`, `getRelatedRecords`,
`listRecentSobjectRecords`, `createSobjectRecord`, `updateSobjectRecord`,
`updateRelatedRecord`, `deleteSobjectRecord` (never used), `getUserInfo`.

## Record types, users, folders, reports

| Fact | Value | Verified |
|---|---|---|
| Ask Zeus record type | `DeveloperName = 'Zeus'`, Id `012I80000004IPnIAM` | Aug 2026 |
| Staging Membership record type | `012I80000004IpSIAU` (staging only; production differs) | Jul 2026 |
| Mathew Hema user | `005RF000003ahkfYAA` (also active `005RF000007mSM9YAM`), alias `mhema`, profile System Administrator `00e5g000001jYQ6AAM`, role node CEO | Aug 2026 |
| Andrew Dunn users | working `0055g00000DqUq9AAF`; also active `0055g00000DqbMVAAZ`, `005RF000006cU6TYAU` | Aug 2026 |
| Keith Tsui users | working `005I8000000J4L5IAK`; also active `005RF000002E8qzYAC` | Aug 2026 |
| Nina Lewis users | active `005I8000000J5EtIAK`, `005RF000001n46kYAA` (confirm which) | Aug 2026 |
| Zeus Helpdesk Dashboard | folder `01ZRF00000FcXoj2AF` (Mathew's private folder) | Jul 2026 |
| Improvement Metrics dashboard | `01ZRF00000FcYsr2AF` (Mathew's private folder) | Jul 2026 |
| Unreconciled Opportunities report (Zap source) | `00ORF0000033T6z2AE` | Jul 2026 |
| Raisely integration user | profile "Raisely - Connected User", account `birdlife@salesfix.com.au`, upsert key `Raisely_UUID__c` | Jun 2026 |

User IDs are the likely working accounts; the owner-resolution algorithm in
`birdlife-ict-assistant` is still run at write time because duplicates exist.

## Case model values

Statuses, close reasons, Type and sub-type values, and the write mechanics are
in `birdlife-ict-assistant/references/reference.md` (single source; do not
copy them here).

## Managed package namespaces

| Namespace | Package |
|---|---|
| `npsp`, `npe01`, `npe03`, `npe4`, `npe5` | NPSP v14.x |
| `AAkPay` | Payments2Us (82 objects) |
| `APXTConga4`, `APXT_BPM`, `APXT_CongaSign` | Conga Composer, Batch, Sign |
| `md_npsp_pack`, `movedata` | MoveData NPSP (Raisely path) |
| `pi`, `sl_flow` | Pardot / Account Engagement v5.10 + Sercante (decommission, hard stop 31 Aug 2026) |
| `dupcheck` | Plauti Duplicate Check (17 objects) |
| `GW_Volunteers` | Volunteers for Salesforce (installed, empty) |
| `stripeGC` | Stripe |
| `ZVC` | Zoom for Salesforce (18 objects) |
| `LearnUponP` | LearnUpon LMS |
| `pmdm` | Program Management Module |
| `agf` | Agile Accelerator (97 objects, removal candidate) |
| `bofc` | BOFC admin toolkit (27 objects) |
| `sf_devops`, `dlrs`, `ZeroBounce`, `Field_Trip`, `uar`, `Streams` | DevOps Center, rollups, email validation, field usage, access review |

## Objects and fields that matter

| API name | Note |
|---|---|
| `npe01__OppPayment__c` | Payments; validation rule `Block_Reconciled_Changes` (Nina Lewis, 8 Dec 2025) |
| `npe03__Recurring_Donation__c` | NPSP recurring donations, 1,778 active (Jun-Aug 2026) |
| `AAkPay__Recurring_Payment__c` | Payments2Us recurring, 392 active (Jun-Aug 2026); regular giving is the union of both |
| `npsp__Allocation__c` | GAU allocations (map to NetSuite GL codes) |
| `AAkPay__Subscription__c` | Managed membership subscription |
| `Subscription__c`, `Subscription_Member__c` | Keith Tsui's unmanaged objects (8 + 421 test records); name-collide with the above |
| `Active_BL_Member__c` | Maintained by Payments2Us; Taylor & Francis Emu journal access depends on it |
| `AccountEngagementSync__c` | Non-namespaced, Contact and Lead; RETAIN through the Pardot uninstall (3 flows, layout, 20+ reports) |
| `stripeGC__Sync_Log__c` / `stripeGC__Error_Details__c` | Stripe sync health |
| `movedata__Contact_Platform_Key__c` | Raisely mappings (~19,447) |
| `Contact.Raisely_Access_Token__c`, `Update_Card_Details_Raisely__c` | Credential in a formula URL; sensitive |
| `BetterImpact_ID__c` | Reads 479,613 populated; real count 1 (number-field default trap) |
| `AAkPay__Member_Type__c` | Reads 100% populated; genuinely 100% blank |
| `SC_Additional_Enquiry_Type__c` | Case sub-type; ~48% blank on Zeus cases |
| `BLAU_Doc_Template__c`, `BLAU_Doc_Generation_Log__c` | Arun Nair's DocGen framework, staging only, Apex uncaptured |

Supporter ID prefixes: Contacts `C-` (e.g. `C-0491796`), Household Accounts
`N-` (e.g. `N-15613`).

## Integration constants

| Item | Value |
|---|---|
| MoveData extension setting | `DonationRecurringOffsetDays = 13` |
| Inactive flow | "Opportunity: Community Fundraising Donor [Checked]" |
| miniOrange primary key (post meta) | `salesforce_Opportunity_ID` |
| miniOrange failure rate on `npe01__Opportunity__c` FLS | ~10.3 to 10.5% of sync attempts, both envs |
| miniOrange webhook access keys | prod `7cf2…`, staging `8d8f…` (leaked; rotation unverified; never write the full key here) |
| Conga daily batch | Batch-0008, 7:00 PM AEST, 50 to 200 receipts/day |
| Conga EOFY query | CMQ-0008, FY code hardcoded `'25f'` |
| Conga deleted button target | CMT-00031 (file-less) |
| Conga footprint | 10 Solutions, 31 templates, 172 queries, 35 email templates |
| Plauti thresholds | Contacts 2.5 points, Accounts 3; job "Clone: Daily Contact Merge" |
| Ortto data source | "Birdlifeaustralia": 2,038,253 records, 15.9M activities; filter `Ortto Inactive is false`; Lead not synced |
| Ortto plan | Professional, $1,763.20/month, $21,158.40 per 12 months, renewal 12 Aug 2027 |

## Staging versus production differences

| Item | Staging | Production |
|---|---|---|
| Membership subscription period | 1 day | 1 year |
| SKUs | suffixed `-STAGING` | plain |
| RecordTypeId, Product2, PricebookEntry | differ | differ; re-set on every deploy |
| Woo Members mapping, Pricebook automation, `Automatic_Renewal__c`, `npsp__Type__c`, duplicate keys | present | absent |

## Security posture numbers (Jun 2026; the register with dates is `birdlife-security`)

Health Check 83%; 0 trusted IP ranges; 8 objects public external access; guest
profiles with Edit on 45 objects; 15% of internal users are System
Administrators (target 5%); 9 of 14 active sysadmins without MFA; 23 inactive
sysadmin accounts; bots birdbot1/5/6 as System Administrator in the CEO role
node; Release Updates 0%; Transaction Security Policies due 13 Jul 2026; four
release updates due 1 Sep 2026.

## Counts worth keeping (point in time)

| Count | Value | As of |
|---|---|---|
| Email-origin cases, all record types | 53k; 115k closed all time | Jun 2026 |
| Cases in New, all record types | ~3,600 (of which 8 Ask Zeus) | 1 Jul 2026 |
| Ask Zeus volume | ~877 cases in 12 months, down 32% year on year | Aug 2026 |
| Money in, 7 days | 516 won opps / $824,378.63; 612 paid payments / $827,300.15 | 3 Sep 2026 |
| Top closers historically | Angelica Fazio 6,300; Alison Bolding 3,800 | Jul 2026 |
