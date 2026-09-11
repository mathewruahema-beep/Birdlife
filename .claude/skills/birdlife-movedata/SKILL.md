---
name: birdlife-movedata
description: "Expert operator knowledge for MoveData at BirdLife Australia: the pipeline phase model, platform keys, extension Flow authoring, the live Zeus configuration and its eight known defects, and the full error catalogue. Trigger on MoveData, Raisely sync, platform key, notification, extension flow, pipeline stage, Question Response, or a donation that did not reach Salesforce."
---

# MoveData at BirdLife Australia

Read `birdlife-core` first for write authority and source precedence. `birdlife-salesforce`
owns the wider Zeus org; this skill owns everything MoveData touches inside it.

Evidence base: the whole of docs.movedata.io read 11 Sep 2026, plus a read-only SOQL audit of
production org `00D5g000004DMayEAG` the same day. Where the two disagree, the org wins and this
file says so.

---

## 1. The three facts that stop most wrong answers

1. **Notifications are not in Salesforce.** There is no `Notification__c`, `Integration__c`,
   `Execution_Log__c` or `Polling_Attempt__c` object in any namespace in this org. The MoveData
   app tabs are Apex controllers (`movedata.NotificationDetailsController`,
   `movedata.IntegrationDetailsController`) making HTTP callouts to MoveData's hosted service.
   **Never promise a failure rate, a notification count or an error breakdown from SOQL.** Those
   live in the MoveData console or come from support@movedata.io.
2. **Three namespaces are installed, not one.** `movedata` (core, 59 Apex classes),
   `md_npsp_pack` (NPSP donation extension, 37 classes, several components labelled
   `[Deprecated]`), `md_forms_pack` (forms/petitions, 4 classes, zero data ever). `mvdt` and `MD`
   do not exist. Always confirm which namespace a field is in before writing SOQL.
3. **MoveData never does DML from your Flow.** Your Flow receives a `Record` variable, assigns
   fields, returns it; MoveData commits. A null assigned into a field **silently wipes existing
   data**. Null-check every input before use. This is the number one cause of self-inflicted data
   loss in extension work.

---

## 2. Architecture

MoveData cloud (AWS Sydney, multi-region) holds integration definitions and credentials,
notification records and statuses, execution logs, polling attempts and retry history, with a
**90-day rolling retention**. The managed package in Zeus holds the inbound Apex REST receiver
(`movedata.MoveDataEndpoint`), four pipeline engines, the stock Flows, the platform key objects,
settings and our own extension Flows.

Four engines exist in Apex: `MoveDataDonationPipeline`, `MoveDataFormsPipeline`,
`MoveDataCommercePipeline`, `MoveDataWebhookPipeline`. **Only donation and forms have pipeline
metadata configured.** Commerce and webhook are shipped and idle.

Ingestion modes across the vendor's 18 platforms: webhook/push (Raisely, GiveEasy, Grassrootz,
GiveWP), polling (Enthuse hourly, Funraisin 10 min, JustGiving 12 h, TapRaise 12 h), platform-
controlled batch push (GoFundraise), and CSV/Excel upload (Benevity, Charitable Giving, CAF,
Good2Give, Facebook, Much Loved, PayPal Giving Fund, Charities Trust). No integration backfills
history; sync starts at connection time and loading earlier data is a paid MoveData service.

---

## 3. The pipeline model

One notification = one Salesforce transaction. Any phase fails, **the whole thing rolls back**.
There are no partial records. Donation pipeline phases, in order:

| # | Phase | Notes |
|---|---|---|
| 0 | Configuration | Sets advanced config for the run. Creates nothing. |
| 1 | Pre-processing | Transforms the raw payload. |
| 2 | Account | Organisation donor. |
| 3 | Contact | Runs more than once per notification (donor, fundraiser, tribute contact, matched donor). |
| 4 | Campaign | Including peer-to-peer parent/child hierarchies. |
| 5 | Recurring Donation | Conditional. Skipped entirely for one-off gifts. |
| 6 | Donation | Creates the Opportunity and links everything. |

Commerce pipeline reuses 2-4 then adds Catalogue, Order, Order Item. Orders land on
**Opportunity and OpportunityLineItem**, never native Order/OrderItem, even under Nonprofit Cloud.

### The five flow roles

Every object in every phase uses the same skeleton. Learn these and you can predict where any
behaviour lives.

- **Platform Key** - builds the `platform:key` string. Pure string work, no DML.
- **Record Match** - `salesforceKey` short-circuit, then platform-key junction lookup via
  `PlatformKeyLookupComponent`, then native Salesforce duplicate rules.
- **Mapping** - the real transform, gated by Protect checkboxes and `Config_*` toggles.
- **Post Upsert** - junctions, NPSP Affiliations, Campaign Members, soft credits, GAU copy,
  matched-gift linkage.
- **Name** - Campaign only. Colon for two tiers (`Parent: Child`), hyphen for three or more.

**Never edit a stock flow.** Build a new unmanaged autolaunched Flow and register it.

---

## 4. Writing an extension Flow

Naming: `[MoveData Extension] {Schema}: {Object} - {Stage}`, e.g.
`[MoveData Extension] Donation: Contact - Mapping`.

Register with a row in `movedata__MoveData_Pipeline__mdt`:

| Field | Value |
|---|---|
| DeveloperName | `<EXTENSION>_<ENTITY>_<STAGE>_EXT`, e.g. `DONATION_CONTACT_MAPPING_EXT` |
| `movedata__Handler__c` | Flow API name (or a literal when Type is `Config`) |
| `movedata__Type__c` | `Flow`, `Fieldset` or `Config` |
| `movedata__Order__c` | **4** runs before the stock flow, **5** standard, **6** runs after |
| `movedata__Disabled__c` | Turns the stage off without deleting it |

STAGE values seen in this org: `FIELDSET`, `MAPPING`, `DUPLICATE`, `PLATFORM_KEY`, `POST`,
`NAME`, `CONFIGURATION`, `SOBJECT`. ENTITY values: `ACCOUNT`, `CONTACT`, `CAMPAIGN`, `DONATION`,
`RECURRING` (donation family) and `ACCOUNT`, `CONTACT`, `CAMPAIGN`, `PETITION` (forms family).

**Custom metadata SOQL has two traps:** `OR` in the WHERE clause returns
`MALFORMED_QUERY: Disjunctions not supported` (split into separate queries), and `first`/`last`
are reserved alias names (use `firstSeen`/`lastSeen`).

### Control outputs

`Cancel` (Boolean) aborts the entire notification, nothing is created. `Break`, `Continue`,
`PostUpsert` (Boolean) and `Errors` (Text collection) round out the command set.
`DuplicateCheck` lets you match on extra fields in memory without persisting them. `IsActor`
gates logic to the primary contact only.

### Context variables available inside a Flow

- Record: `Record`, and the `{Stage}RecordAlt` pattern
- Account phase: `Context_AccountType`, `Context_Fundraiser`, `Context_Donor`,
  `Context_RecurringDonor`, `Context_MatchedDonor`
- Contact phase: the same five plus `Context_ContactType`, `Context_TributeContact`
- Campaign phase: `CampaignIndex`, `CampaignCount`, `CampaignIdList`, `HasCampaignAccount`,
  `HasCampaignContact`, `HasParentCampaign`
- Cross-stage donation: `ParentAccount`, `DonorContact`, `CampaignContact`, `DonationCampaign`,
  `CampaignIdList`, `RecurringRecord`, `IsNewRecord`
- Cross-stage commerce: `PrimaryContact`, `PrimaryAccount`, `OrderCampaign`, `CatalogRecord`,
  `OrderRecord`, `StandardPriceBookId`
- Identity: `Platform`, `PlatformKey`, `Key`
- Config: `Config_ContactProtectLevel`, `Config_ContactAddressInheritAccount`,
  `Config_ContactUseMailingAddress`, `Config_ContactUseStateCode`, `Config_ContactUseCountryCode`,
  `Config_CreateCampaignMembers`, `Config_CampaignMemberDeleteExistingStatuses`,
  `Config_OrderTotalSubtractFeePlatform`, `Config_OrderStageNameDefault`,
  `Config_DonationSuppressGiftDesignations`, `Config_MoveDataEngine`

Invocable Apex components shipped by the package: `ClearFieldFlowComponent`, `SetValueComponent`,
`GetValueComponent`, `ConvertToLocalDateFlowComponent`, `CurrencyCodeComponent`,
`PlatformKeyCreateComponent`, `PlatformKeyLookupComponent`, `WriteToLogFlowComponent`.

### Disabling or retargeting a phase

Disable: metadata row with `Type = config`, `Handler = true`, DeveloperName `{phase}_disable`.
Change a phase's SObject: register a Flow that overrides it, **then remap six metadata entries**
(Fieldset, Platform Key, Record Match, Name, Mapping, Post Upsert) to flows that work with the
new object. Miss one and the phase half-works, which is worse than not working.

Verify every change by reprocessing one notification and reading the Execution tab and Variable
Inspector. Never verify by waiting for live traffic.

---

## 5. The schema

Two schemas, `donation` and `commerce`, sharing an envelope: `schema`, `schemaVersion`,
`platform`, `platformLabel`, `platformVersion`, `prefix`, `client`, `action`, `custom`, `global`,
`createdAt`, `modifiedAt`. `action` is `metadata` (campaigns, recurring changes, fundraisers) or
`donation`.

Donation graph: root holds `campaign[]`, `donor` (Person or Organisation), and optionally
`tribute`, `matched`, `recurring`, `donation`. Campaign carries its own `primaryContact`,
addresses, `questions[]`, `marketing`. Donation carries `financials[]` (each with origin and
settled Financial entry), `marketing`, `related`. Person, Organisation, Address, Communication,
Marketing, Question and Relationship are shared leaves, identical in both schemas.

**`salesforceKey`** on Person, Organisation and Campaign short-circuits matching entirely and
forces the record. It is the escape hatch when matching goes wrong. `prefix` exists so multiple
instances of the same platform do not collide.

### Platform key syntax

`<platform>:<external id>`, e.g. `raisely:aa88bd90-562c-11eb-bf24-6bd493dd10e5`. This string is
the **sole idempotency anchor**. Mapping MoveData onto pre-existing Salesforce records means
backfilling the platform key field so MoveData matches rather than duplicates. Do it in a sandbox
first, every time.

---

## 6. What is actually live in Zeus

Verified 11 Sep 2026. Treat these as facts, re-verify before quoting a number externally.

### Real object and field API names

| API name | Note |
|---|---|
| `movedata__Platform_Key__c` on Opportunity | Text(255), External Id, unique. **The live donation key.** |
| `movedata__Platform_Key__c` on Campaign | With `movedata__Platform__c`, `movedata__Campaign_Code__c`, `movedata__Protect_Name__c`, `movedata__Protect_Campaign_Parent__c` |
| `movedata__Contact_Platform_Key__c` | Junction object. Contact keys live **here**, not on Contact. Many keys per Contact. |
| `movedata__Account_Platform_Key__c` | Same pattern for Account. |
| `movedata__ExtensionSetting__c` | Key/Type/Value rows. **Read `movedata__Key__c`, never `Name`** - Name truncates at 38 chars. |
| `movedata__MoveData_Pipeline__mdt` | 73 rows, all `NamespacePrefix = null` (deployed, not packaged). |
| `md_npsp_pack__Platform_Key__c` on `npe03__Recurring_Donation__c` | **Still the live recurring key.** No `movedata__` successor field exists on RD. |
| `md_npsp_pack__Question_Response__c` | 184,002 records. Raisely custom form answers. |
| `md_npsp_pack__Fee__c`, `__Gateway_Fee__c`, `__Gateway_Fee_Tax__c`, `__Platform_Fee__c`, `__Platform_Fee_Tax__c`, `__Tax__c`, `__Receipt_Number__c` on Opportunity | Fee/tax breakdown |
| `md_npsp_pack__Campaign_URL__c`, `__Fundraising_Account__c`, `__Fundraising_Contact__c` on Campaign | Not deprecated |

Contact has **only** a deprecated `md_npsp_pack__Platform_Key__c`. Account has no
`movedata__Platform_Key__c`. **CampaignMember has zero MoveData fields.**

### Our extension Flows (unmanaged, local)

Donation family: `MoveData_Donation_Account_Mapping_Ext` (6),
`MoveData_Donation_Campaign_Mapping_Ext` (6),
`MoveData_Extension_Donation_Campaign_Mapping_Ext_Pre` (4),
`MoveData_Donation_Contact_Record_Match_Ext` (6, **DISABLED**),
`MoveData_Extension_Donation_Contact_Mapping` (6),
`MoveData_Donation_Contact_Mapping_Pre_Ext` (4),
`MoveData_Donation_Donation_Mapping_Ext` (6),
`MoveData_Donation_Donation_Post_Upsert_Ext` (5),
`MoveData_Donation_Recurring_Mapping_Ext` (6),
`MoveData_Donation_Recurring_Configuration_Ext` (4),
`MoveData_Donation_Configuration_Ext`.
Forms family: `MoveData_Forms_*_Ext` set plus `MoveData_Extension_Forms_Contact_Mapping_Pre`.

Exactly one of the 73 pipeline rows is disabled: `DONATION_CONTACT_DUPLICATE_EXT`. Nobody has
recorded why. The forms-side equivalent is enabled.

### Settings that change the answer

All 21 rows are org-level, `md_npsp_pack.` prefixed, last touched 2022-2023.

| Key | Value | Consequence |
|---|---|---|
| `IgnoreFailedDonations` | **true** | A failed Raisely payment is **never** written to Salesforce |
| `IgnoreOfflineDonations` | **true** | Offline donations never written |
| `ContactIgnoreDoNotContact` | true | NPSP Do Not Contact not set from source newsletter opt-in |
| `ContactUseMailingAddress` | true | Address lands on Mailing, not Other |
| `AccountIgnoreType`, `IgnoreDefaultCampaignType` | true | Type defaults not applied |
| `DonationOpportunityContactRoleSoftCredit` | true | Soft-credit OCRs created |
| `DonationAmountSubtractFeePlatform` | **false** | Opportunity Amount is **gross** of platform fee |

**Say this out loud whenever anyone asks about declined payments, dunning or regular-giving
attrition:** because failed donations are suppressed, the last 90 days show 10,367 Closed Won and
16 Refund and nothing else. There is no declined-payment data in Zeus at all. That analysis has to
come from Raisely. Anyone who has built an attrition view from Zeus has built it wrong.

### Volumes (as at 11 Sep 2026)

122,063 MoveData-keyed Opportunities all-time, ~$9.58m. Last 12 months: 23,643 Opportunities,
effectively 100% `raisely:` prefixed, across 40 campaigns, led by Tax Appeal 2026 (6,093 /
$1,141,309), WILDBIRD (4,934 / $178,011), Spring Appeal 2025 (3,986 / $414,895). Also 19,817
Contact platform keys, 43 keyed Campaigns, 3,507 Recurring Donations, 184,002 Question Responses.
Last write 11 Sep 2026 07:49:59 UTC. Good2Give (`g2g:`) is dead: nothing since 2023.

---

## 7. Known defects - check these before diagnosing anything new

1. Campaign `7015g000000LjcSAAS` "Community Fundraising" has key
   `rasiely:87b00540-91ea-11f0-99e3-edc46a3b30b9` - **prefix misspelled** - and has still taken
   11 gifts / $9,432 in 12 months. Matching is by string, so a correctly keyed twin will appear.
2. Recurring Donations key on `md_npsp_pack__Platform_Key__c` with no `movedata__` successor.
   3,507 regular givers on a deprecating namespace. Largest latent break in the integration.
3. 21,478 answers in 12 months to `thisDonationIsOnBehalfOfAnOrgani` against **zero** Raisely
   Account platform keys. Organisation giving is landing as individual household gifts.
4. Campaign ABC23 Donations has key `raisely:` with no UUID.
5. Forms/petitions extension configured but inert: 17 pipeline stages, 4 Apex classes, fields
   deployed, zero records ever, and its petition target `CampaignMember` carries no MoveData field
   so it has no idempotency anchor. Finish it or uninstall it.
6. Six campaigns (In Memoriam and others) have a valid `raisely:` key but null
   `movedata__Platform__c`, so platform-grouped reporting undercounts.
7. `DONATION_CONTACT_DUPLICATE_EXT` disabled for unrecorded reasons.
8. Live in-org error pattern is row-lock contention between MoveData inbound writes, NPSP
   customisable rollups and Plauti account merges (`ENTITY_IS_DELETED`, `UNABLE_TO_LOCK_ROW` in
   `npsp__ACCT_AccountMerge_TDTM`, `CRLP.RecurringDonations`, `CRLP.ContactHardCredit`) - about 18
   of 21 `npsp__Error__c` rows in 180 days. The fix is scheduling, not code.

---

## 8. Error catalogue

| Error text | Fix |
|---|---|
| `UNABLE_TO_LOCK_ROW` | Auto-retries 3x. If persistent, find and reschedule the competing process. |
| `An unhandled fault has occurred in this flow` | Generic wrapper. Real cause is in Paused and Failed Flow Interviews. |
| `MAXIMUM_HIERARCHY_LEVELS_REACHED` | SF caps campaign hierarchy at 5; MoveData uses 3. Trim your own levels. |
| `A Campaign Member status already a specified sort order` | Renamed status, or sort order colliding with MoveData's reserved **8921-8961** range. |
| `End date must be later than the last Closed Won Opportunity's Close Date` | Same-day payment + cancel edge case. Wait a day, reprocess. No prevention needed. |
| Campaign Parent silently overwritten | Set `movedata__Protect_Campaign_Parent__c = true`. |
| Campaign Name silently reverted | Set `movedata__Protect_Name__c = true`. |
| `Cannot Refund due to missing original Donation.` | Original failed or its platform key is wrong. Fix original, then reprocess refund. |
| Accounts created as "Anonymous Household" | Authorised User's profile default Account record type is wrong. Set it to Organisation. |
| `You can't change the Household Account or Contact on a Recurring Donation that has Closed Opportunities` | Align SF contact/account to source, merge duplicates, or force-match by platform key. |
| `You must select a Contact associated with this Household Account` | Reopen Closed Won opps, fix the Account on the RD, reclose, reprocess. |
| `Apex CPU time limit exceeded` / `Too many SOQL queries: 101` | Our other automation, not MoveData. Trim competing flows/triggers; consider async post-processing. |
| `Too many SOQL queries: 101` in DLRS | Switch DLRS rollups from Realtime to "Watch for Changes and Process Later" on a schedule. |
| `Can't perform callout because of pending uncommitted changes` | Move the callout to an async flow or an after-insert/after-update trigger. |
| `DUPLICATE_VALUE, A Product with this SKU already exists` | Commerce extension below v1.114. Upgrade. |
| `OAUTH_APPROVAL_ERROR_GENERIC` on authorise | Temporarily enable "Approve Uninstalled Connected Apps" on the profile, authorise, disable again. |
| Everything stopped after a My Domain change | Re-click Authorise in MoveData Settings. |

**Duplicate rules must be set to Report, not Alert.** Alert causes MoveData to fail on duplicate
detection. To keep Alert for humans: clone the rule, set the clone to Report scoped to the
MoveData Authorised User only, and exclude that user from the original Alert rule.

**Authorised User**: one named Salesforce user, needs `MoveData Application` plus every extension
permission set in use (and native `FundraisingAccess` under Nonprofit Cloud). From 1 Jul 2026
Salesforce enforces phishing-resistant MFA; MoveData's JWT auth is unaffected but that account
still needs a passkey or conversion to an Integration User. IP-restricted orgs whitelist
`13.237.31.104` and `3.105.105.117` in Login IP Ranges.

---

## 9. Raisely specifics

Webhook, real time. API key from Raisely Settings > API & Webhooks; per campaign, add MoveData's
Integration URL as a webhook subscribing to `profile` (created/updated/deleted), `donation`
(created/succeeded/updated/refunded), `subscription.updated`, `order.succeeded`.

- Campaigns are **not** created in Salesforce until the first notification. Force one early by
  re-saving the campaign's root profile to fire `profile.updated`.
- Mapping to an existing Campaign needs `Platform Key = raisely:<UUID>` **and** `Protect Name = true`.
- Organisation donations require a Raisely custom field with the **exact lowercase Field ID
  `company`**. Anything else silently fails to trigger Account and Affiliation logic. This is
  almost certainly the cause of defect 3 above - check it first.
- Migrating recurring donations from another platform means backfilling
  `Platform Key = raisely:<Subscription UUID>`. Sandbox first.
- Missing LastName errors: Raisely allows optional name fields. Make them required, or edit and
  re-save the donor record.
- Recurring status map: OK -> Active, PAUSED -> Paused, CANCELLED -> Closed, FAILED -> Lapsed.
  Linked pledged Opportunities lag until the next real donation event.
- **No webhook signal exists** for GDPR "forget person" or for Raisely communications (receipts,
  emails). Neither syncs. Both are manual in Salesforce.
- Settings worth knowing: Processor Version V1/V2 (V2 needed for tickets via Commerce), Fee
  Allocation Method, Address Processing (defaults to the person-profile address over the donation
  address), Recurring Currency Mode.
- The Jul 2026 Raisely CAPTCHA/API-key change on write endpoints does not affect MoveData, which
  only receives events.

---

## 10. How to work a MoveData question

1. **Establish the layer.** Is this a MoveData cloud question (notification status, retry,
   integration config) or a Salesforce question (records, mappings, flows)? Cloud questions cannot
   be answered by SOQL. Say so rather than guessing.
2. **Verify live before asserting.** Query the org. Confirm namespace, field API name and current
   setting value before quoting any of section 6.
3. **Check section 7 first.** Most "new" problems are one of the eight known defects.
4. **Reprocess is not a fix.** Reprocessing creates a *new* notification with current mappings;
   the original stays Failed forever. Root-cause first, then reprocess. There is no bulk
   reprocess - email support@movedata.io (Mon-Fri, 8am-11pm AEST) for volume.
5. **Sandbox before production**, without exception, for any pipeline metadata or extension Flow
   change. Reference: `salesforce-delivery-governance`.
6. **Name the people impact.** Supporter Care sees the wrong entity on corporate gifts while
   defect 3 stands. Fundraising cannot see declined payments. Peggy should know Opportunity
   Amount is gross of platform fee so she is not hunting a variance that is by design. Keith and
   Karishma are the only people who know why the eleven custom Flows exist, and that is a single
   point of failure on $1.8m a year.

---

## 11. Vendor position

AWS Sydney, multi-region active-active. AES-256-GCM at rest via KMS, HTTPS/OAuth in transit, JWT
server-to-server to Salesforce. 90-day notification retention; inactive accounts anonymised or
deleted after two years. **CSA STAR Level 1 - self-assessment, not third-party audited.**
48-hour breach notification. Sub-processors: AWS (AU), Atlassian (AU), Intercom (US), Google (US).
No named independent penetration tester and no published cadence. No published uptime SLA.
MoveData will not complete a bespoke security questionnaire without a paid 4-8 hour engagement.

Current versions at 11 Sep 2026: core 1.342, NPSP extension 1.176, Nonprofit Cloud extension
1.165, Commerce extension 1.130. Orgs on core below 1.167 need a migration before any extension
released after 1.167 will work. NPSP extension v1.157 removed deprecated platform-key fields and
the Question Responses object - that is the only breaking change in the last 12 months and it is
directly relevant to defect 2.

The Commerce extension is **not compatible with Nonprofit Cloud**. Under NPC, ticketing and
merchandise come from NPC's own built-in Commerce pipeline stage instead.

Residual risk is concentration, not breach: one vendor, one platform, one namespace, $1.8m a year,
eleven undocumented Flows and the recurring key on a deprecating namespace.