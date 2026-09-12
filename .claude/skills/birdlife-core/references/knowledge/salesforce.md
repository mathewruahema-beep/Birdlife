# Salesforce Knowledge Digest — BirdLife Australia
*Compiled 2026-08-02 from all .md files under kb/text/Salesforce (incl. New Developer, Pardot). Source dates from kb/manifest.tsv.*

## 1. Purpose & role in ecosystem

Salesforce (internally nicknamed **"Zeus"**) is BirdLife Australia's central CRM: constituent/donor management, fundraising, memberships, advocacy, payments and the internal ICT helpdesk (Cases via **zeus@birdlife.org.au**). Built on **NPSP (Nonprofit Success Pack) Household Account model**, heavily extended by managed packages and custom development. It is the hub for inbound data from WooCommerce (web shop/memberships), Raisely (donations, via MoveData), Payments2Us/AAkPay (payments, direct debits), Pardot/Account Engagement (marketing — being decommissioned in favour of Ortto), LearnUpon (LMS), ZeroBounce (email validation), and BetterImpact (volunteers, in progress). Conga Composer generates receipts/letters. The ICT helpdesk, the fundraising data team, supporter care, and finance reconciliation all operate out of this org.

## 2. Environments & key configuration facts

**Production org**
- URL: `https://birdlifeaustralia.lightning.force.com`; Setup: `https://birdlifeaustralia.my.salesforce-setup.com`
- Enterprise Edition, instance **AUS92**, currency AUD, timezone AEST (GMT+10). Org created 25/1/2021 by Reza Torkman.
- Licenses: 70 full Salesforce (70/70 used — at capacity), 500,000 External Identity, 101 Identity, 5,000 Partner Community Login, B2BMA + Analytics Cloud integration users.
- Scale: **439 custom objects**, 4,500+ API names, ~494–500 custom fields on Contact (167 Account, 193 Opportunity, 125 Campaign), **4,621 reports**, 50+ active flows, ~1,044,208 of 6,000,000 Apex characters used (17.4%).
- 49 profiles (many prefixed `[Deprecated]` after a clean-up); role hierarchy not formally configured; migration toward Enhanced User Profiles in progress.
- Key record types: Opportunity has 10 record types incl. Membership, Donation, Product Sale, Merchandise. Membership RecordTypeId (staging) = `012I80000004IpSIAU`.
- Supporter ID convention: Contacts `C-` prefix (e.g. C-0491796), Household Accounts `N-` prefix (e.g. N-15613).

**Staging**
- Salesforce sandbox: `birdlifeaustralia--staging.sandbox.my.salesforce.com` / `...lightning.force.com`. Production is READ-ONLY for the new developer during onboarding.
- WordPress: production `birdlife.org.au` (WP Engine); staging `birdlifestage.wpengine.com`. Staging membership subscriptions run "1 day" periods (prod = 1 year); staging SKUs suffixed `-STAGING`. All SF IDs (record types, Product2, PricebookEntry) differ between orgs and must be re-set on production deploy.

**Installed packages** (key namespaces): NPSP `npsp` v14.x (+npe01/npe03/npe5), Payments2Us `AAkPay` (82 objects), Conga Composer `APXTConga4` + Conga Sign `APXT_CongaSign`, MoveData NPSP `md_npsp_pack` + MoveData.io, Pardot `pi__` v5.10 (decommissioning), Sercante Flow Actions for Pardot `sl_flow`, Plauti Duplicate Check `dupcheck` (17 objects), LearnUpon `LearnUponP`, Program Management `pmdm`, Field Trip, SFDO Base, plus `agf` (97), `bofc` (27), `ZVC` (18).

**Integration users / identities**: Bird Bot (automation), **Raisely Integration User** (profile "Raisely - Connected User"), DCA Migration user (dca@birdlife.org.au), Media Monks (external consultant), B2BMA/Analytics integration users. miniOrange plugin authenticates as a Connected App (OAuth2, scopes `api refresh_token`; staging redirect URI `https://birdlifestage.wpengine.com`).

## 3. Integrations & data flows

**WooCommerce → Salesforce (miniOrange "Object Data Sync For Salesforce" plugin)**
- Real-Time Post/Order Sync ENABLED both envs; User Sync and Scheduled Sync DISABLED. Upsert pattern: SF record ID written back to WP meta (`salesforce_Opportunity_ID` etc.); missing meta ⇒ duplicates.
- Mappings: WP product/product_variation → Product2; shop_order → Opportunity (Membership record type static, `StripeStatus__c`= "Paid" hardcoded, WC status string → StageName raw); product → OpportunityLineItem (requires `pricebook_entry_id` meta or creation fails); order_payment → `npe01__OppPayment__c` (Stripe charge ID/fee/gross); **staging-only**: woo_members → `Subscription_Member__c` (family members from `_family_members` JSON, one record each). Production has 6 mappings, staging 7.
- Reverse flow: SF → WP "Product2 to WP Product" webhook. Endpoints with access keys: prod `https://birdlife.org.au/?method=soap&action=store&mappinglabel=Product2+to+WP+Product&accesskey=7cf2…REDACTED (rotate: see GOVERNANCE.md)`; staging key `8d8f…REDACTED (rotate: see GOVERNANCE.md)`. **These keys are printed in plaintext in several docs** — rotate via "Regenerate Access Key".
- Approx 6,466 WooCommerce orders as of Jul 2026 (6,331 completed, 70 refunded, 60 failed).
- Refund behaviour (staging-verified, order #22553): refund creates a NEW Payment with **positive** amount, Paid=false, Type=`shop_order_refund`; Opportunity Stage set to raw "refunded" (not a valid picklist value); NPSP rolls Amount to $0 but `TotalOrderAmount__c` unchanged; OpportunityLineItems keep positive values; Stripe Refund ID (re_xxx) NOT synced; `Subscription_Member__c` never deactivated; WooCommerce shop_subscription object not mapped at all (rich `Subscription__c` object with `Membership_Status__c`, End/Cease dates is unused by the integration).

**Raisely → Salesforce (via MoveData NPSP)**
- No "Raisely" flow exists; integration is data-model + API-user level. Raisely calls the SF API as Raisely Integration User, upserting Contacts/Recurring Donations matched on `Raisely_UUID__c` external ID. 4 Raisely custom fields incl. `Contact.Raisely_Access_Token__c` and formula `Raisely_Account_URL__c`; `Recurring_Donation.Update_Card_Details_Raisely__c` combines MoveData's `md_npsp_pack__Campaign_URL__c` + `Platform_Key__c` + the access token.
- MoveData NPSP managed package supplies 50+ generic flows (Mapping / Post Upsert / Record Match / Platform Key per Account, Campaign, Contact, Donation); BirdLife's unmanaged `[MoveData Extension]` layer adds org rules (e.g. "Donation: Configuration" sets DonationRecurringOffsetDays = 13, anonymous donations not private). Do not modify managed MoveData flows.
- Community fundraising flags: flow "Community : Community Fundraiser [Checked]" (Campaign-triggered, ACTIVE) sets `Contact.Community_Fundraiser__c`; flow "Opportunity: Community Fundraising Donor [Checked]" is **INACTIVE**, so the Community Fundraising Donor checkbox is stale for donations since deactivation.
- Known limitation: a Raisely campaign links to only one SF Campaign, so online gifts code to the top-level appeal campaign, not segment campaigns.

**Payments2Us/AAkPay**: internal + public membership forms hit AAkPay checkout pages; objects Account_Subscription, Recurring_Payment, Payment_Txn, Batch_Entry, Direct_Debit_Batch. Regular giving spans NPSP Recurring Donations (RDs) AND AAkPay Recurring Payments (RPs) — dual-object reporting pain.

**Pardot → Ortto**: Ortto has an independent SF data source "Birdlifeaustralia" (2,038,253 records, 15.9M activities synced; Contact filter `Ortto Inactive is false`; Lead NOT synced — 0 fields selected). See §4 for decommissioning state.

**Other**: Conga (receipts, §4); Plauti Duplicate Check/Deduplicate (dedupe, §5); LearnUpon enrollments; ZeroBounce triggers on Contact/Lead; Stripe balance-transaction flow `[Stripe] aCU Opportunity - Get Balance Transaction` (last modified Ayush Saxena 4/6/2026); Asana↔Salesforce email rule (separate doc, Asana folder).

## 4. Current state (in-flight projects, decisions, dates)

- **Pardot (Account Engagement) decommissioning** — hard cutover **31 Aug 2026**, target completion 15 Aug 2026. Six phases: Audit (Jul 14–18), Decouple/Convert (Jul 19–25), Prepare Ortto (Jul 19–26), Rebuild Automation (Jul 27–Aug 5), Cutover (Aug 6–15), Validate (Aug 16–31). As of today (2 Aug) the plan is mid-Phase-4/entering cutover window. Inventory: pi__ package v5.10; 5 pi__ custom objects (incl. late-found `pi__AsyncRequest__c`); 16 "Account Engagement" fields each on Contact AND Lead; `AccountEngagementSync__c` (non-namespaced, exists on BOTH Contact and Lead) to be RETAINED — referenced by 3 flows, Contact Lightning Layout, ~20+ reports; Pardot-owned triggers LogContactChange/LogLeadChange; 13 total triggers on Contact/Lead to regression-test. Open decisions: Ortto retention/plan upgrade (retention limit REACHED, blocking expanded sync; current plan Professional $599/mo base, 250k contacts, effective $1,763.20/mo, 12-mo commitment $21,158.40, renewal 12 Aug 2027), Ortto field-count discrepancy (238 vs 287), whether to sync Lead into Ortto, final approval to uninstall pi__ + sl_flow packages.
- **Membership build (Phase 1)** — WooCommerce Variable Subscriptions (Individual $84/$65 concession, Family $132, SIG subscriptions $15–$40/yr) syncing via miniOrange to Opportunity/OLI/Payment/`Subscription_Member__c` in the staging sandbox. Woo Members mapping and Pricebook automation are staging-only and need production deployment. Target per onboarding plan: Membership Phase 1 live in production ~Week 12 (≈late Sep/Oct 2026), with a Monday 2am cutover that disables Payments2Us and migrates its data into `Subscription__c`.
- **Developer transition** — outgoing developer **Arun Nair** (last login 25 Jun 2026) handed over: BLAU DocGen framework in staging (objects `BLAU_Doc_Template__c`, `BLAU_Doc_Generation_Log__c`; permission sets BLAU_DocGen_Admin/User created 2 May 2026; 13 test runs 3 May, 3 successful PDFs) and an unfinished External Client Application "**Hyperagent**" (registered 26 May 2026, IsAccessible=false, contact arunbnair85@outlook.com). Apex/Flows/audit-trail behind the framework were NOT captured and need manual review.
- **New developer onboarding** — **Karishma Soni** (Senior Salesforce Developer) starting on a 12-week plan (v1.0 dated 2026-07-10) run by Mathew Hema (daily 9:30am standups, Friday 4pm reviews, decision gates W4/W6/W8/W10/W12). Focus shifted from a membership-centric plan (2 Jul) to **refund-system mastery + membership** (9–10 Jul docs). Week-4 gate: fix or accept the refund system. Asana board: app.asana.com/1/443963187362944/project/1211042432693678.
- **ICT Helpdesk dashboards** — built 1–2 Jul 2026 in Mathew Hema's Private folder: "Zeus Helpdesk Dashboard" (01ZRF00000FcXoj2AF) and "Zeus ICT Helpdesk — Improvement Metrics" (01ZRF00000FcYsr2AF), 10 reports on Cases. Live data 1 Jul: 3,600 New vs 165 In Progress (acknowledgement bottleneck), 115k closed all-time, 53k email-origin cases; top closers Angelica Fazio (6,300), Alison Bolding (3,800). Not yet shared beyond Mathew.
- **Conga replacement** — decision made to migrate Conga Composer to native Salesforce (Visualforce PDF + Apex batch + Lightning email templates + screen flows), 10-week plan. Conga currently runs EOFY receipts (Wildbird Protector, batch of up to 5,000), daily donation receipts, membership receipts: 10 Solutions, 31 Word templates (4 active: CMT-00000/00001/00003/00027), 35 email templates, 50+ SOQL queries, 2 community screen flows.
- **Case list-view incident (29 Jun 2026)**: "All Open Cases" had been filtered to `Case Owner Alias = mhema` hiding everyone else's cases; filter removed, now only `Closed = False`.
- **Fundraising data team handover (June 2026)**: V's pain-point list + ICT response with priority matrix (see §5).

## 5. Open actions, risks & known issues

**Overdue / date-critical**
- Pardot cutover: uninstall approval, Ortto retention billing decision, Lead-sync decision and field-count reconciliation all still open with cutover window 6–15 Aug and hard deadline 31 Aug 2026.
- Conga EOFY: query CMQ-0008 has **hardcoded FY code '25f'** — zero contacts processed if not updated before the (July) EOFY run; the individual "EOFY Receipt" Contact button is **DELETED** (solution shows ERROR — staff cannot generate individual EOFY receipts); live EOFY batch button URL mismatches the in-progress URL and uses API v37 vs v52. If native replacement not ready before the July run, keep Conga one more cycle.
- Bequest receipt button for Lee (URGENT, pre-parental-leave item from June): new Conga 'Bequest Receipt' button restricted to Bequest record type; V to upload template before leave, ICT to wire the button. Status unconfirmed.
- Helpdesk backlog: 3,600 unacknowledged "New" cases; recommend auto-assignment/triage SLA, Case Status field-history tracking, share dashboards to a shared folder.

**Refund/data-integrity (HIGH severity, documented Jul 2026)**
- Refund payments created with positive amounts (ledger shows two positive payments); Opportunity stage "refunded"/"cancelled" are raw WC strings not valid SF stages; OLIs never reflect refunds; `Subscription_Member__c` never deactivated (ex-members look active); WC subscriptions not mapped to `Subscription__c`; Stripe Refund IDs untraceable from SF; partial refunds behave like full ones.
- Recommended fixes: add refunded/cancelled stage values, `Membership_Status__c` on Subscription_Member, `Stripe_Refund_ID__c` on Payment, shop_subscription → `Subscription__c` mapping, flow to normalise refunded stage.

**Prod/staging drift (miniOrange)**: Woo Members mapping, Pricebook automation, `Automatic_Renewal__c`, `npsp__Type__c` and duplicate-detection keys exist only in staging; staging Product Variation mapping is stripped to 1 field (regression?); production has no duplicate-check keys on Product/Opportunity mappings.

**Fundraising data team priorities (Jun 2026 matrix)**: URGENT Bequest receipt button; HIGH Next Donation Date restoration on Recurring Donations (removed when Pledged Opportunities were switched off — RG income forecasting broken; Raisely is source of truth; quick win = formula from RP Next Payment Date) and Duplicate Management rules review; MEDIUM Raisely/SF sync health-check (dual-write conflicts, sync failures over past years), custom before/after RG Change Log object (current Change Logs "functionally useless" — only new values), Account-level comms preferences, Pardot Connected Campaigns (moot post-decommission); LOWER Account-to-Account relationships (Estate↔solicitor, PAFs), Donor Segment field workaround for Raisely single-campaign limit, more rollup variants (SG vs RG), phone-donation UTM tracking (Zeus case by Jono — CC buttons link to generic birdlife.org.au/donate).

**Duplicates/Plauti**: process doc (as at 16-1-26) — Contacts need ≥2.5 points of ID, Accounts ≥3; Plauti Deduplicate Job "Clone: Daily Contact Merge" + Plauti Desktop app; Plauti requires exact First+Last+Primary Email match to group Contacts; portal-user records must be the merge master (only one active Portal User per group; disable via "Disable Customer User"); financial records on blank duplicates ⇒ escalate to manager/Jono/V; post-merge check duplicate active RDs/RPs/Subscriptions. Pardot section of this doc becomes obsolete after decommission. API-based integrations (Raisely) may bypass UI duplicate rules.

**Security-relevant**
- Webhook access keys (prod `7cf2…REDACTED (rotate: see GOVERNANCE.md)`, staging `8d8f…REDACTED (rotate: see GOVERNANCE.md)`) and full webhook URLs printed in plaintext in three docs — rotate keys and scrub docs. (The Object Data Sync guide redacted OAuth Client ID/Secret but the Membership guide and comparison doc leaked the access keys.)
- Raisely access tokens stored per-Contact (`Raisely_Access_Token__c`) and embedded in clickable formula URLs — treat as credentials.
- All 70 full licenses consumed — no headroom for new staff/integration users.
- `npe01__OppPayment__c` validation rule "Block_Reconciled_Changes" (Nina Lewis, 8/12/2025) blocks manual corrections to reconciled payments.
- Two corrupted source documents (DocGen LWC spec, Onboarding System Audit) mean the DocGen app specification survives only in Arun's head/external repo — recover before knowledge is lost.

## 6. People

| Person | Role / relevance |
|---|---|
| **Mathew Hema** (mathew.hema@birdlife.org.au, alias mhema) | ICT Manager; primary Salesforce contact; owns helpdesk dashboards, onboarding program, decision gates |
| **Karishma Soni** (karishma.soni@birdlife.org.au) | Incoming Senior Salesforce Developer (12-week onboarding from ~Jul 2026; refund system + membership) |
| **Arun Nair** (arun.nair@birdlife.org.au; personal arunbnair85@outlook.com) | Outgoing SF developer; built BLAU DocGen + Hyperagent in staging; last login 25 Jun 2026 |
| **Nina Lewis** | Finance/Supporter Care — reconciliation & eCommerce refund guides; created Block_Reconciled_Changes rule; processes WP refunds |
| **Veronica ("V")** | Fundraising data team lead; authored pain-points handover before parental leave (~Jun/Jul 2026) |
| **Jono** | Supporter Care/fundraising escalation point (dedupe escalations, comms-prefs review, UTM Zeus case) |
| **Lee** | Bequest receipting (blocked by receipt template issue) |
| **Ayush Saxena** | Developer — modified Stripe Balance Transaction flow 4/6/2026 |
| **Angelica Fazio, Alison Bolding** | ICT helpdesk technicians (top case closers) |
| **Keith Tsui** | Admin — company info changes; tracked-fields list owner |
| **Reza Torkman** | Created the org (25/1/2021) |
| Fiona Mainey, Josephine Ferguson, Doug Merrett | Staff/assessment users noted in Setup |
| Micah, James | Mentioned as briefing recipients in onboarding standups |
| **Vendors/platforms** | miniOrange (Object Data Sync), MoveData.io, Raisely, Stripe, Ortto, Plauti, Conga, Payments2Us (AAkonsult), Sercante, ZeroBounce, LearnUpon, WP Engine, Media Monks (consultant), BetterImpact (volunteer project — ICT not yet involved) |

## 7. Document register

| Path (relative to kb/text/Salesforce) | Date | Description | Status |
|---|---|---|---|
| BirdLife_Australia_ICT_Helpdesk_Dashboard_Technical_Documentation.md | 2026-07-02 | Zeus ICT helpdesk dashboard suite (2 dashboards, 10 Case reports), build steps, live metrics, recommendations | current |
| BirdLife_Raisely_Fundraising_Flows_Technical_Guide.md | 2026-07-13 | How Raisely integrates via MoveData NPSP; 2 community-fundraiser flows (one inactive); integration user & Raisely fields | current |
| How to manage duplicates in Salesforce as at 16-1-26.md | 2026-06-09 (content 16-1-26) | Plauti Deduplicate merge process for Contacts & Accounts, points-of-ID rules, portal-user handling | current but aging — Pardot section becomes obsolete after 31 Aug 2026 decommission |
| List for Mathew of top needs and pain points for Fundraising data team.md | 2026-06-28 | V's raw handover list: duplicates, reconciliation, RG reporting, Next Donation Date, EDM/appeal analysis, Conga templates | superseded-by "…Answer to Veronica's questions" (response doc incorporates and actions it) |
| List for Mathew … - Answer to Veronica's questions.md | 2026-06-28 | ICT response + technical fixes (FIX 1–8) + priority matrix (URGENT Bequest button, HIGH Next Donation Date, dedupe) | current |
| Object_Data_Sync_For_Salesforce_Technical_Guide.md | 2026-07-13 | miniOrange plugin architecture, OAuth flow, 7 staging mappings, triggers, audit log, error codes, troubleshooting | current |
| Salesforce_Case_Filter_Process.md | 2026-06-29 | Incident record: Case Owner Alias=mhema filter on All Open Cases applied and removed | current (historical record) |
| Pardot/Pardot_Decommissioning_Technical_Guide.md | 2026-07-13 (prepared 07-14) | Verified Pardot org inventory, gaps (pi__AsyncRequest__c, Lead AccountEngagementSync__c), Ortto state/billing, 6-phase plan, open decisions | current — supersedes the unfiled 2026-07-13 findings doc it expands |
| Pardot/Pardot_Decommissioning_Execution_Guide_Admin_Developer.md | 2026-07-13 (prepared 07-14) | Role-based (Admin vs Developer) step-by-step execution of the 6 phases | current (companion to Technical Guide) |
| New Developer/Arun_Nair_Salesforce_Developer_Handover.md | 2026-07-01 | Handover of Arun's staging work: BLAU DocGen objects/permission sets/template/test runs, Hyperagent app, gaps, takeover steps | current |
| New Developer/BirdLife_Australia_Salesforce_Audit.md | 2026-07-01 | Org technical audit: 439 custom objects, field counts, packages, platform events, inferred Apex/Flow architecture, SOQL to complete audit | current (partially inferred; tables lost in extraction) |
| New Developer/BirdLife_Australia_Membership_Technical_Guide.md | 2026-07-01 | Staging membership build: WooCommerce products/plans, miniOrange mappings 1–14, SF objects (Opportunity/OLI/Payment/Subscription_Member__c), end-to-end traces, prod-vs-staging notes | current |
| New Developer/BirdLife_Australia_Refund_Cancellation_Technical_Guide.md | 2026-07-01 | Refund/cancellation mechanics WC→SF, confirmed behaviour (order #22553), 10 gaps with severities, 5 recommendations | current |
| New Developer/BirdLife_Australia_Salesforce_Developer_Onboarding_Guide.md | 2026-07-01 | Production org onboarding: org details, licenses, data model, packages, integrations, security, flows, business processes, contacts | current |
| New Developer/BirdLife_Conga_Complete_System_Audit_and_Replacement_Guide.md | 2026-07-01 | Conga audit (Solutions, queries, templates, batches) + 10-week native replacement plan + critical warnings (deleted button, hardcoded '25f') | current |
| New Developer/BirdLife_DocGen_LWC_App_Specification.docx | 2026-07-01 | DocGen LWC app specification — no extracted text | **corrupted** |
| New Developer/BirdLife_Developer_Onboarding_System_Audit.docx | 2026-07-01 | Developer onboarding system audit — no extracted text | **corrupted** |
| New Developer/SF_Sync_Production_vs_Staging_Comparison.md | 2026-07-01 | miniOrange prod vs staging: mapping/field diffs, staging-only Woo Members mapping, access keys, deployment recommendations | current |
| New Developer/WooCommerce_to_Salesforce_DataFlow_Guide.md | 2026-07-01 | Production WooCommerce→SF data flow: 6 mappings, field reference, webhook, troubleshooting, order volumes | current |
| New Developer/Karishma_12Week_Onboarding_Plan.md | 2026-07-02 | Early 12-week plan (membership-launch focused; Subscription__c build, Payments2Us migration, cutover) | superseded-by Salesforce_Developer.md (2026-07-10 consolidated refund-focused plan) — but still the only doc detailing the Weeks 5–12 membership/migration scope |
| New Developer/Karishma_Onboarding_Tracker.md | 2026-07-02 | Phase/weekly status tracker + Mathew's blocking decisions (Days-as-Member formula, Q1–Q13, go-live date) — all "Not Started" | current (tracking artifact, not yet updated) |
| New Developer/Week_1_2_Daily_Standups.md | 2026-07-08 | Detailed Week 1–2 standup Q&A script for individual-membership order flow | current |
| New Developer/Karishma - Onboarding.md | 2026-07-09 | One-page Week 1–2 task/deliverable sheet (screenshots, test orders, refund test, Asana review) | current |
| New Developer/Karishma_Onboarding_StepByStep.md | 2026-07-09 | Full 12-week day-by-day schedule (Track A) — refund-system focused version | current |
| New Developer/Mathew_Manager_Guide_StepByStep.md | 2026-07-09 | Track B: Mathew's daily standup questions, decision gates, red flags for all 12 weeks | current |
| New Developer/Salesforce_Developer.md | 2026-07-10 | Consolidated onboarding master doc v1.0 (both tracks, environments, milestones, success criteria) — declared "single reference document" | current — authoritative onboarding doc |
