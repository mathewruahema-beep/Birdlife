# Knowledge Digest — Volunteering, Membership, Events & Journal Access
**BirdLife Australia ICT knowledge base | Compiled 2 August 2026 | Sources: all .md files under `text/Better Impact`, `text/Memberships`, `text/Humanitix`, `text/Taylor and Francis` (dates per `manifest.tsv`)**

---

## 1. Better Impact (volunteer management platform)

### 1.1 Purpose & role
- Cloud volunteer (and member) management platform: profiles, online application forms, activities/shifts, hours logging, qualifications, eLearning. Central home for the volunteer lifecycle (apply → screen → accept → assign → track hours → archive).
- BirdLife runs a single **Enterprise account with 10 sub-accounts (branches)**: BirdLife Australia Volunteers (national), Melbourne, Capricornia, Castlemaine, Mornington, Northern Queensland, Photography, Southern NSW, Tasmania, Top End. Live since ~mid-2025 (Melbourne created Jun 2025, most branches Aug 2025).
- Modules enabled: Administrator (ADM), Member (MEM), Volunteer (VOL). Client/Donor not purchased.
- Project owner: Mathew Hema (ICT Manager). Asana project "ICT Better Impact Implementation" (private to ICT Manager), phased plan starting **1 August 2026**.

### 1.2 Key configuration facts (live state as reviewed 11 Jul 2026)
- Only **2 of 10 branches have any volunteers**: national account (56 Long Term, 9 In Process, 2 Applicant, 1 Rejected, 1 Other) and Melbourne (1 Active, 1 Long Term). Other 8 branches: zero volunteers.
- **7 Enterprise Full Administrators; none have 2FA enabled**; no Security Groups (scoped/limited admin) exist.
- 3 application forms per branch (Volunteer 1 general; Volunteer 2 = Great Cocky Count 2026; Volunteer 3 = Network Forum). All require manual approval; **none send a confirmation email**; policy/Code-of-Conduct acceptance step OFF on all forms; birthdate capture OFF on all forms.
- **1 Activity Template only** ("GCC 2026"): one-time activity, Auto Log Hours ON, max 900 volunteers, public, no self-scheduling, 24h withdrawal window, description still placeholder text. No Shift Templates, no Feedback Fields (note: Feedback Fields do not fire when Auto Log Hours is on — conflict).
- **1 Qualification only** (Code of Conduct — also duplicated as a signed-document custom field). Classifications (Region/Focus/Activity Type/Suitability/Time & Duration) all empty. No eLearning modules. Badges/Committees empty.
- Public Volunteer Page: title "Birdlife Australia" set; Public Page Message and Mission Statement empty. MyImpactPage/mobile app/Timeclock links all generated and working.
- Custom Field library is extensive: emergency contact, medical, membership, SIG registrations (Seabird, Wader Studies, Raptor), declarations, communication preferences.
- Discrepancy: 11 Jul audit said "8 General Interest templates active" (Bird Surveying, Community Engagement, Data Analysis, Education, Habitat Restoration, Shorebirds, Species Recovery, Volunteering); **20 Jul live re-check found ZERO active General Interests** — the 8 names exist only as an unused template library. Flag to James.
- Session timeout 30 min (recommended default); timezone correct (Melbourne/Sydney). One API key already exists with ADM/MEM/VOL access.

### 1.3 Integrations & data flows
- **Better Impact API is READ-ONLY** (HTTP Basic Auth against API-key username/password). No endpoint exists to create/update profiles. Consequence: Salesforce→Better Impact can never be fully automated.
- **Inbound (SF → BI)**: paid, staff-processed bulk Excel import via Secure File Exchange. .xlsx with worksheet named exactly "UserData", fixed column order (Salutation…FirstName*…LastName*…AddressLine1*, City*, State*, Country*, PostCode*, DateJoined*, Status*), DD/MM/YYYY dates, one branch column per sub-account after Status, "please update" for unknown required values. Blank Status defaults to Accepted. Username prefix (e.g. "blavol-") + language (English AU) decided at submission. Better Impact returns a results file with generated usernames/passwords → distributed by Word/Outlook mail merge. Custom fields/qualifications import billed separately. Only the spreadsheet-generation step (script pulling from Salesforce) is automatable.
- **Outbound (BI → Ortto)**: Ortto `person/merge` endpoint (X-Api-Key header, upsert by email, up to 100 people/request) — genuine automatable one-way sync for marketing segments. Send minimal fields only; never sync qualifications/background checks/medical to Ortto.
- **Outbound (BI → Salesforce)**: two-step lookup-by-email-then-create/update against SF REST API, or cleaner External-ID upsert (Salesforce already has `BetterImpact_ID__c` on Contact; BI has an "Office Use Only — Salesforce ID" custom field). Must be built/tested in sandbox first. Alternative no-code path: Zapier Schedule + Webhooks (GET, Basic Auth) + Salesforce app — no native Better Impact Zapier connector exists (checked 11 Jul 2026).
- **Field mapping (live audit 20–21 Jul 2026, 479,620 SF Contacts)** — headline findings:
  - **The join key is empty on both sides**: `BetterImpact_ID__c` genuinely populated on only **1 of 479,620** Contacts (naive `!= null` falsely showed 479,613 because the field defaults to 0). Populating this pair is the prerequisite for any sync.
  - GW_Volunteers managed package installed but effectively unused: `GW_Volunteers__Volunteer_Status__c`, `First_Volunteer_Date__c`, `Volunteer_Organization__c`, `Volunteer__c`, `npo02__MembershipJoinDate/EndDate__c` all 100% empty. Only `RegisteredVolunteer__c` (169 true) and `BLA_Staff_Member__c` (169 true) carry data — check if same 169 people.
  - Biggest structural gaps: **no Emergency Contact or Medical Details fields exist on SF Contact** at all; sensitivity decision needed (BI may stay system of record).
  - `Do_Not_Mail__c` = 1 record true vs `DoNotCall` = 116,516 — suspicious; `Mail_Opt_Out__c` may be the real suppression field.
  - `AAkPay__Member_Type__c` genuinely 100% blank despite a false 100%-populated `!= null` reading. Do not trust `!= null` counts in this org.
  - New SF fields needed for: Phone Preference, social handles (X/LinkedIn/Instagram), Region/locale, Personal Message, Volunteer Role, per-SIG membership detail, emergency contact, medical, dietary.
  - Multi-branch membership (one BI volunteer in several branches) needs an SF design decision (multi-select vs junction object).

### 1.4 Current state (with dates)
- 11 Jul 2026: full platform review + 10-document set produced; platform "proven at small scale through Great Cocky Count, not yet rolled out".
- 20–21 Jul 2026: live BI-vs-Salesforce field mapping audit completed (spreadsheet dated 23 Jul in manifest).
- **Asana phased plan (project start 1 Aug 2026)**:
  - Phase 1 Foundational config & governance (Aug): confirm bulk-import pricing with BI Success team 4 Aug; Public Page content 7 Aug; Classifications 11 Aug; expand Activity Templates 14 Aug; branch-vs-enterprise admin rules 18 Aug; first eLearning module 25 Aug.
  - Phase 2 Data import pipeline (Sep): SF export/reformat script 4 Sep; first bulk import 8 Sep; credential distribution 11 Sep; error correction 15 Sep.
  - Phase 3 Branch rollout (Sep–Oct): wave 1 of 4 dormant branches 25 Sep; distribute Branch Admin Guide 2 Oct; wave 2 (remaining 4) 9 Oct.
  - Phase 4 Integrations (Oct–Nov): dedicated read-only API key 16 Oct; Ortto sync 23 Oct; SF sync in sandbox 6 Nov; SF sync go-live 13 Nov.
  - Phase 5 Governance & review (Nov–Dec): security/API review 20 Nov; adoption report 27 Nov; lessons learned 11 Dec; GCC 2027 template planning 18 Dec.
- As of digest date (2 Aug 2026) Phase 1 has just begun; no evidence in the KB that any Phase 1 task is complete.

### 1.5 Open actions, risks & known issues
- **No 2FA on any of the 7 Full Administrator accounts** — flagged as the single most important security step; still open per latest docs.
- 7 Full Admins with unrestricted enterprise access; no Security Groups; Better Impact recommends min. 2 (not 7) Full Admins plus scoped branch roles.
- Applicants get no confirmation email and are not asked to accept the Code of Conduct at application — compliance/experience gap.
- GCC 2026 template: placeholder description, confirm 900-max intentional, Auto Log Hours blocks any future Feedback Fields.
- Bulk import is billable and manually processed — confirm scope/pricing with BI Success team before every import (first task, due 4 Aug); also ask whether any write-capable API or partner integration is planned before committing to the SF export script.
- General Interests active-vs-template discrepancy (11 Jul vs 20 Jul) to confirm with James.
- Do-not-mail suppression field ambiguity; SIG aggregate counts disagree (1,107 vs 6,097); Work Phone field choice; secondary email field choice — all need James/data-owner decisions.
- Salesforce sync must not go live without sandbox testing (writes into production CRM). Only minimal non-sensitive fields to Ortto.
- Better Impact volunteer portal integration with the new membership portal is explicitly **Phase 2 of the Membership project** — do not scope into Phase 1.

### 1.6 People named
- **Mathew Hema** — ICT Manager, owner of the entire Better Impact implementation and Asana plan.
- **James** (Salesforce/data owner, referenced throughout the field-mapping audit for decisions; likely James Vilinsky per Memberships docs — confirm).
- Better Impact "Success team" / "Member Success team" — vendor contact for bulk import pricing and Secure File Exchange.

### 1.7 Document register — Better Impact
| Path | Date | Description | Status |
|---|---|---|---|
| `Better Impact/BetterImpact.md` | 2026-07-11 | Master summary: current state, decisions, full Asana phase plan, open items | **Current** (primary index) |
| `Better Impact/BetterImpact_Salesforce_Field_Mapping.md` | 2026-07-23 | Live BI↔SF Contact field mapping with 20–21 Jul population counts and data-quality warnings | **Current** (most recent audit; corrects parts of 11 Jul docs) |
| `Better Impact/BirdlifeAustralia-BetterImpact-RolloutAdminPlan-v2.md` | 2026-07-11 | Current state, Excel-import decision, Zapier assessment, rollout sequence, admin model, Zapier appendix | Current |
| `Better Impact/BetterImpact-ICTManager-TechnicalGuide.md` | 2026-07-11 | Sequential 12-step implementation guide with live screenshots | Current |
| `Better Impact/BetterImpact-OnboardingGapAnalysis-v2.md` | 2026-07-11 | Onboarding current state + 7-gap analysis + action plan | Current (note: its "8 General Interests active" claim superseded by 20 Jul field-mapping finding) |
| `Better Impact/BetterImpact-ActivityTemplates-Review-v2.md` | 2026-07-11 | Activity Templates review, best practice, 5-gap analysis, action plan | Current |
| `Better Impact/BetterImpact-ActivityTemplates-Review.md` | 2026-07-11 | v1 of the above (same text, no screenshots) | **Superseded** by -v2 |
| `Better Impact/BirdlifeAustralia-BetterImpact-OnboardingGuide-v2.md` | 2026-07-11 | Platform primer, account structure, walkthrough, glossary | Current |
| `Better Impact/BetterImpact-ExcelImport-AutomationRunbook.md` | 2026-07-11 | Repeatable bulk-import runbook: file spec, Secure File Exchange steps, automation limits | Current |
| `Better Impact/BirdlifeAustralia-BetterImpact-Ortto-Salesforce-IntegrationGuide.md` | 2026-07-11 | BI read-only API → Ortto person/merge and → SF lookup-then-create / External-ID upsert designs | Current |
| `Better Impact/BetterImpact-EnterpriseAdministrationGuide.md` | 2026-07-11 | Enterprise admin operations manual (admins, branches, API keys, forms, SFE, adoption monitoring) | Current |
| `Better Impact/BetterImpact-BranchNetworkAdminGuide.md` | 2026-07-11 | Branch-level admin day-to-day process guide + network rules | Current |
| `Better Impact/BirdlifeAustralia-BetterImpact-VolunteerManager-ProcessGuide.md` | 2026-07-11 | Plain-language volunteer manager guide + checklists | Current |

---

## 2. Membership system rebuild (WordPress/WooCommerce + miniOrange + Salesforce)

### 2.1 Purpose & role
- Replace the Payments2Us (AAkPay)–based membership system with: **WordPress/WooCommerce** (birdlife.org.au; staging birdlifestage.wpengine.com) for sign-up/renewal/self-service, **Stripe** (card + BECS direct debit) for payment, **miniOrange "Object Data Sync For Salesforce" Enterprise** as the integration layer, and a **new Salesforce `Membership__c` object** replacing `AAkPay__Subscription__c`. Salesforce is the system of record for membership status.
- Vendor build: **Blitzm** (WooCommerce front end). Phase 1 MVP = memberships in WooCommerce + miniOrange sync + staggered migration at renewal. Phase 2 = secondary-member self-service, partner discounts (Zoos Vic), reserve accommodation discounts, simplified Emu/T&F access, Better Impact portal integration, SIG migration, member-only webinars.

### 2.2 Key configuration facts
- **Tiers/prices (confirmed)**: Individual Standard $84, Concession $65 (honour system, no verification), Family $132 (1 primary + up to 6 others, min 2 / max 7 people), Financial Hardship $35 (hidden product, Supporter Care–controlled, eligibility criteria TBC), Free $0 (Lifetime/Honorary/Fellow, Board approval). Old public page showed superseded $79/$35 — correction was a HIGH prerequisite; Individual $84/$65 and Family $132 confirmed live on staging 30 Jul.
- Duration 12 months; **grace (cease) period 3 months** (per constitution) → End Date = +12m, Cease Date = +15m. Auto-renewal default ON with explicit opt-out. Reminders: 31 days pre-expiry; 7 and 1 days pre-cease (confirmed decision).
- Renewal logic: renew before End Date or in grace → extend End+Cease by 12m, update Last Renewed Date. Renew after Cease Date → old record Ceased, new record created, **Days-as-Member timer pauses and resumes (not reset)** — closed decision (Q3), supports 50-year recognition.
- Family: one bill/renewal; each person counted individually in reporting; children-only families allowed (though FR brief annotates "I don't think we should include this and will verify"); max 2 votes (primary + 1 nominated secondary adult, both 18+); children never vote; one address only (magazine delivery); primary member manages online (MVP).
- Magazine: default print+digital, opt-out of print; 1 print copy per family; digital per family member with email; overseas = digital only (extra-postage option TBC); quarterly mailouts Mar/Jun/Sep/Dec; welcome email links latest digital issue.
- E-store: active members get automatic 20% off full-price products when logged in; Salesforce is source of truth via `Discount_Eligible__c` reverse sync.
- **Salesforce object design (Build Guide, 30 Jul)**: build on the existing empty `Membership__c` shell + new child `Membership_Member__c` (name, email, `Member_Under_18__c`, `Nominated_Secondary_Voter__c`, `Digital_Magazine__c`). Do NOT build on Keith Tsui's unmanaged `Subscription__c`/`Subscription_Member__c` (8 + 421 real test records, built in good faith without context, name-collides with `AAkPay__Subscription__c`); keep as reference model and migration source, archive after verified migration. Key fields: Start/End/Cease dates, `Membership_Status__c` (Pending Approval, Approved, Expired, Ceased, Cancelled), `Membership_Type__c` picklist, `Automatic_Renewal__c`, `No_of_Days_a_Subscriber__c` (pause/resume), reminder-sent checkboxes, `Financial_Hardship_Approved_By__c` (User lookup, required before status passes Pending Approval), lookups to Contact/Account/Product2/Opportunity. Four validation rules: family size 2–7; no under-18 nominated voter; one nominated voter per family; hardship approver required. One record-triggered lifecycle Flow covering purchase/renewal/expiry/cease/reminders.
- **miniOrange current live state (Staging, 30 Jul)**: 6 live mappings (Product2, Woo Payments Sync, OpportunityLineItem, WP shop_order→Opportunity, Product2→WP Product, WP Product Variation→SF Product) — none touch membership. A 7th "Woo Members Sync" mapping was **deleted** (consistent with WooCommerce Memberships being inactive). Real-time trigger pattern (no cron). Primary key = post-meta `salesforce_Opportunity_ID`. New build: Mapping 1 shop_order→`Membership__c` (new dedicated key `salesforce_Membership_ID`; reverse direction scoped to `Discount_Eligible__c` only) and Mapping 2 family-member data→`Membership_Member__c` (one-way, fires per member; `Nominated_Secondary_Voter__c` deliberately excluded pending BR §12 decision).
- Payments2Us (legacy, documented 30 Jun): 31 Payment Forms; tiers Full Member Digital/Print $79, Concession $35, SIG memberships $35 (Raptor, Seabird, Wader Studies, Photography); Stripe gateway ("BirdLife MEMBERSHIP Facility"); subscriptions at Contact level, single (no family bundles); Conga CET templates drive current renewal reminders (Sprint 7A 10-day, Sprint 7B 30-day-before-cease).

### 2.3 Integrations & data flows
- WooCommerce → Salesforce: order/renewal/cancellation events real-time → `Membership__c` (+`Membership_Member__c` per family member). Contact matched by name/email (duplicate-email checkout triggers login prompt, FR-2.2 Built). Opportunity still created by existing shop_order→Opportunity mapping; `Membership__c.Opportunity__c` links them.
- Salesforce → WooCommerce: membership status changes (e.g. manual Ceased) flow back so e-store discount and access plans update — implemented as `Discount_Eligible__c` reverse sync only.
- Stripe: card tokens reused for migrated card auto-renewal members (approach still to confirm with Blitzm — may restart due to new platform); **BECS direct debit members must set up a fresh mandate** (cannot migrate).
- Legacy: Payments2Us continues until staggered migration completes; ICT turns off P2U auto-renewals at cutover; existing WooCommerce subscriptions stay Active 15 months so no member loses access mid-transition; no double-charging across systems.

### 2.4 Current state (with dates)
- 19 May 2026: Business Requirements & Open Decisions v1.0 drafted (15 open questions; sign-off block for Micah Demmert / James Vilinsky — no signed copy in KB). v2.0 dated 30 Jun 2026 is referenced by the test script and the Blitzm brief but is not itself in this folder.
- 30 Jun 2026: Payments2Us technical guide (legacy system documented); Test Script v1.0 (30 test cases TC-001–TC-030, all "Not Tested"; built against the older assumption set, e.g. Membership Status "Active", `Membership_Expiry_Date__c`).
- Jun 2026 WordPress Health Report + **23 Jul 2026 staging deep dive**: environment gaps identified; per that report **no Blitzm build activity commences until all CRITICAL items resolved** (WooCommerce Memberships licence, WooCommerce Subscriptions licence).
- 30 Jul 2026: staging verification pass — prices confirmed live, family builder (2–7, child flags, per-member digital toggle) built, auto-renew checkbox default-on present, magazine dropdown built; **Add-to-Cart bug found live (YITH Pre-Order / Cart block incompatibility)**. Salesforce Technical Build Guide and miniOrange requirements produced (both 30 Jul).
- 31 Jul 2026: Blitzm Functional Requirements Brief finalised; **Membership Staging Test Script** issued (45 tests across Blitzm/miniOrange/Salesforce-Developer/End-to-End tabs) — **all 45 "Not Tested" as of 31 Jul**.
- Build status summary from the FR brief: front-end (Blitzm) largely Built/Partially built; **entire Salesforce side (FR-5 lifecycle, FR-6 reminders, FR-9 voting, FR-10 object+sync) Not built**; FR-8 e-store discount Blocked; migration (FR-11) Not built.

### 2.5 Open actions, risks & known issues
- **CRITICAL blockers (ICT-owned, gate all Blitzm work)**: WooCommerce Memberships licence renewal + reactivation (blocks FR-8 discount, FR-3 access plans, both new miniOrange mappings — "building against an inactive plugin means testing against nothing"); WooCommerce Subscriptions licence renewal/update (blocks FR-4 auto-renewal); Spellbook/GP Populate Anything broken (FR-2 dynamic fields — "do we need this?"); miniOrange field-mapping coverage of new Membership object (HIGH); public pricing correction (HIGH — since confirmed for the visible tiers).
- **Two live miniOrange bugs that must not be repeated on the new mappings**: (1) primary-key **write-back gap** — plugin fails to write returned SF Id into post meta ("Salesforce UUID: None" on two real paid orders) → duplicate-record risk on next status change; (2) **field-level-security gap** on `npe01__Opportunity__c` causing **~10.3–10.5% of sync attempts to fail outright, confirmed on both Staging AND Production**. Mitigations specified: dedicated `salesforce_Membership_ID` key, FLS granted to the integration user on every new field *before* first sync, deliberate write-back test first (MO-05).
- **Reminder-timing conflict**: BR-confirmed 31/7/1 days vs 10/37/60-style timings in help text on Keith's `Subscription__c` fields already wired into a Conga flow. Escalate to James Vilinsky / Conga rebuild owner before building reminder fields — otherwise two contradictory reminder schedules launch.
- **Object naming collision risk**: Keith's `Subscription__c` vs managed `AAkPay__Subscription__c` — anyone querying "Subscription" without checking namespace hits the wrong object. New build deliberately avoids the name.
- Open decisions still unresolved (BR register): Financial Hardship criteria (Q1, Micah), family alternate magazine address (Q4), quarterly digital-link owner (Q5), Company field (Q6 — though FR-2.5 marked Built), billing-vs-shipping address (Q7, Ben/Blitzm), **voting-rights recording mechanism auto vs manual (Q8/BR §12, Jonathon Wilson — blocks `Nominated_Secondary_Voter__c` logic)**, branch unsubscribe path (Q9), transition messaging (Q10), overseas print postage (Q11), **reporting requirements list (Q12, Micah — not yet given to dev team)**, named system testers (Q13), day-to-day vendor contact (Q14), SIG Phase 1-vs-later (Q15).
- FR-level open items: Financial Hardship hidden product not built (FR-1.3); Birthdate field needs verification (FR-2.3); Stripe token migration approach unconfirmed (FR-4.2); family mechanism (Product Bundles vs custom post type) unconfirmed with Blitzm — different reporting implications; voting cap enforcement stated in UI but untested with 3+ adults (FR-9.2); children-only family rule itself queried.
- BZ-04 test specifically re-checks the 30 Jul Add-to-Cart bug fix.
- Pre-build confirmations for Karishma: Pending Approval vs "Awaiting Account Verification" picklist question (Keith), Legacy Raiser's Edge fields still needed? (Keith).
- Test Script v1.0 (30 Jun) is partially inconsistent with the final design (status values, field names) — use the 31 Jul Staging Test Script as the authoritative test set.

### 2.6 People named
- **Micah Demmert** — Executive Director, Participation & Engagement; final sign-off; owns Q1, Q6, Q12–Q15.
- **James Vilinsky** — Senior Manager, Participation; member comms plan, transition decisions, Q2–Q5, Q9–Q11; escalation point for reminder-timing conflict.
- **Jonathon Wilson** — Salesforce Lead; membership object design, voting-rights recording (Q8).
- **Keith Tsui** — built the prototype `Subscription__c`/`Subscription_Member__c` objects (testing since March; last touched 27 Jul); consulted on picklist/legacy-field questions.
- **Karishma** — new Salesforce developer executing the `Membership__c` build (10-step sequence in Build Guide).
- **Mathew Hema** — ICT Manager (Financial Hardship process confirmation, E2E-06).
- **Shantal** — grace-reminder timing input (via James V).
- **Blitzm** — vendor building the WooCommerce front end; contact **Ben** (Q7).
- Vendors referenced: miniOrange (plugin), Stripe, Salesforce; Supporter Care team (hardship approvals, unsubscribes); Participation team (magazine link).
- ICT / Finance — plugin licence renewals; ICT — Payments2Us auto-renewal switch-off.

### 2.7 Document register — Memberships
| Path | Date | Description | Status |
|---|---|---|---|
| `Memberships/BirdLife - Blitzm Functional Requirements Brief.md` | 2026-07-31 | FR-1…FR-11 with per-requirement staging status (30 Jul verification); build prerequisites; Phase-1 scope fence | **Current** (authoritative for Blitzm scope) |
| `Memberships/Membership Staging Test Script.md` | 2026-07-31 | 45-test staging script (Blitzm 15 / miniOrange 10 / SF Dev 12 / E2E 8); all Not Tested | **Current** (authoritative test set) |
| `Memberships/BirdLife Membership Salesforce Technical Build Guide.md` | 2026-07-30 | `Membership__c`/`Membership_Member__c` field specs, Flow, validation rules, Karishma build sequence, decommission plan | Current |
| `Memberships/BirdLife Membership miniOrange.md` | 2026-07-30 | Object Data Sync live state (6 mappings, 2 live bugs), 2 new mapping specs, test/sign-off checklist | Current |
| `Memberships/BirdLife_Membership_Requirements_Consolidated.md` | 2026-06-18 | Business Requirements & Open Decisions v1.0 (19 May), 15-question open-decision register, sign-off block | **Superseded** by v2.0 (30 Jun, referenced but not in folder); still the only in-KB copy of the decision register |
| `Memberships/BirdLife_Membership_Test_Script_v1.0.md` | 2026-06-30 | 30-test script vs BR v2.0; uses pre-build field/status names; all Not Tested | **Superseded** by 31 Jul Staging Test Script (keep for edge-case ideas: Stripe declines, 3DS, webhooks, browser/session tests) |
| `Memberships/BirdLife_Payments2Us_Membership_Technical_Guide.md` | 2026-06-30 | Full legacy Payments2Us architecture, forms, flows, renewal batches | Current as legacy reference; system is being retired (**will become stale at cutover**) |

---

## 3. Humanitix (event ticketing)

### 3.1 Purpose & role
- Humanitix is used for event ticketing under a "BirdLife Australia" host profile. Only one event is documented: **Botanical Bazaar 2026 — Habitat Gardening for Birds Workshop**, presented by Dr Christina Zdenek.

### 3.2 Key configuration facts
- Event: Sat **1 Aug 2026, 1:00–2:00pm** (listed AEST, timezone set GMT+10 Australia/Sydney), Country Paradise Parklands — Table D Workshops area, 231 Beaudesert Nerang Rd, Nerang QLD 4211.
- Ticketing: single General Admission type, $20.00 AUD, capacity 25 (= total event capacity), no donations configured. Currency AUD; event type "Class, Training or Workshop"; privacy Public.
- URL: events.humanitix.com/botanical-bazaar-2026.

### 3.3 Integrations & data flows
- None documented — standalone Humanitix event, no Salesforce/Ortto linkage described.

### 3.4 Current state
- Guide dated 14 Jul 2026 (manifest). Internal contradiction: header says **Status: Draft (not yet published)** while the Notes section says the event **is Published** at the public URL. The event date (1 Aug 2026) has now passed — this document is post-event.

### 3.5 Open actions, risks & known issues
- Presenter name inconsistency: page copy says "Dr **Christine** Zdenek", prepared-for line says "**Christina** Zdenek" — was flagged for correction before publishing; unknown if fixed.
- Draft-vs-published status contradiction never reconciled in the doc.
- No banner image (default layout) — suggested improvement.
- No post-event reconciliation (attendance/revenue) exists in the KB.

### 3.6 People named
- **Christina Zdenek** (a.k.a. "Dr Christine Zdenek" in event copy) — presenter / document recipient, BirdLife Australia.

### 3.7 Document register — Humanitix
| Path | Date | Description | Status |
|---|---|---|---|
| `Humanitix/Botanical Bazaar 2026 - Event Setup Guide.md` | 2026-07-14 | Setup guide for the 1 Aug 2026 workshop (tickets, info page, schedule, checks) | **Stale** — event date has passed; retain as template for future Humanitix events |

---

## 4. Taylor & Francis — Emu journal access

### 4.1 Purpose & role
- BirdLife members are entitled to free access to *Emu — Austral Ornithology* (Taylor & Francis). Setup guide configures the Salesforce member portal so only active members and staff reach Emu via **SAML SSO**: Salesforce = Identity Provider, T&F = Service Provider, WAYFless link on the portal.

### 4.2 Key configuration facts
- Eligibility fields on Contact: `Active_BL_Member__c` (Boolean, **auto-synced by AAkPay** — TRUE = current financial member), `BLA_Staff_Member__c`, optionally `Active_SIG_Member__c` (SIG inclusion unconfirmed). Access rule: show Emu link if Active member OR staff.
- IDP metadata: `https://birdlifeaustralia.my.salesforce.com/.well-known/samlidp.xml`. WAYFless link: `https://www.tandfonline.com/action/ssostart?idp=https://birdlifeaustralia.my.salesforce.com/&redirectUri=https://www.tandfonline.com/journals/temu20`.
- Implementation: Experience Builder Audience "Emu Access - Members and Staff" (OR logic) gates button **visibility only**; T&F SAML is the true security gate. T&F needs 48–72h to confirm the SAML connection after receiving metadata.
- Membership lapse handling is automatic: AAkPay flips `Active_BL_Member__c` false → button disappears at next login.
- Related: *Australian Field Ornithology* is open access to everyone (include in member comms/FAQs).

### 4.3 Integrations & data flows
- Salesforce IdP → T&F SP (SAML assertion) on click of WAYFless link; eligibility driven off AAkPay-maintained Contact flags.
- **Dependency risk with the membership rebuild**: `Active_BL_Member__c` is auto-synced by AAkPay/Payments2Us, which is being decommissioned — the new `Membership__c` build must take over maintaining this flag (or the Emu audience must be repointed to `Discount_Eligible__c`/Membership status) or member journal access silently breaks at migration. Not addressed in any document. Simplified T&F access is explicitly **Phase 2** of the membership project; current process (member creates own T&F account and links it) is acknowledged as clunky.

### 4.4 Current state
- Guide prepared 29 Jun 2026 (manifest 28 Jun). Written as a pre-implementation checklist (all prerequisite boxes unchecked in the doc); no evidence in the KB that the IdP, T&F confirmation, audience, or button have gone live, or that the three test scenarios (active member / lapsed / staff) were executed.

### 4.5 Open actions, risks & known issues
- Confirm with Micah/James whether SIG members also get Emu access (open).
- Complete prerequisite checklist: enable SF Identity Provider, send metadata to T&F, await 48–72h confirmation, confirm Experience Builder admin rights, prepare test accounts.
- Post-migration ownership of `Active_BL_Member__c` (see 4.3) — unassigned risk.
- Troubleshooting rule of thumb: member can't see button → check `Active_BL_Member__c` on their Contact.

### 4.6 People named
- **Janelle Heald** (janelle.heald@tandf.com.au) and **Paul Taylor** — Taylor & Francis contacts.
- **Micah Demmert**, **James Vilinsky** — BirdLife contacts (SIG-access confirmation).

### 4.7 Document register — Taylor & Francis
| Path | Date | Description | Status |
|---|---|---|---|
| `Taylor and Francis/Emu Journal Access Setup Guide.md` | 2026-06-28 | SAML SSO (SF IdP → T&F SP) setup: prerequisites, audience build, button, tests | Current (implementation status unverified; flag AAkPay-field dependency before membership cutover) |

---

## Cross-system observations
- **Payments2Us decommission touches three of these systems**: it is the membership system being replaced, it feeds `Active_BL_Member__c` for Emu access, and its `AAkPay__Member_Type__c` was a candidate BI field-mapping target ("confirm AAkPay is still the live membership system of record"). Sequencing the cutover requires updating the Emu eligibility source and the BI mapping assumptions.
- **Phase-2 fence**: Better Impact portal integration, simplified T&F access, and SIG migration are all explicitly out of Phase 1 membership scope — resist scope creep in all three directions.
- Both integration stacks share the same top risk pattern: **integration-user field permissions and join-key population** (miniOrange FLS/write-back bugs; empty `BetterImpact_ID__c` pair). Check FLS and key write-back first on every new mapping.
