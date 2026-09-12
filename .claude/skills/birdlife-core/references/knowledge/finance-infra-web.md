# BirdLife Australia — Finance, Infrastructure & Web Knowledge Digest
Compiled 2026-08-02 from /home/claude/kb/text (dates from manifest.tsv). Scope: NetSuite, Fundraising, Conga, AWS, Ortto, WordPress, Asana, Claude, ABC2026 fix report.

---

## 1. NetSuite (ERP) — incl. OAuth2 certificate findings & Business Central migration business case

### Purpose & role
Oracle NetSuite OneWorld is BirdLife Australia's central finance/ERP system: GL, AR/AP, banking (60–90+ bank accounts), fixed assets, project/grant accounting, payroll (Infinet Cloud/ZonePayroll bundle + Electronic Bank Payments EFT), AASB 16 lease accounting, JB Were investment tracking (~$8.4M under management), GST/BAS compliance.

### Key configuration facts
- Account ID **3440597** (OAuth2 findings doc also cites account label "BirdLife Australia_090721"), Release 2026.1, Australia edition, AP Melbourne data centre, AUD, calendar fiscal year (Jan–Dec). ABN 75 149 124 774.
- Two entities: BirdLife Parent + Birdlife Australia (single operating subsidiary; no intercompany eliminations).
- Chart of accounts: 413 accounts, 5-digit blocks (10000 assets … 50000 expenses); ~90 bank accounts branch-suffixed (11003–11159); AR/AP split by branch (11200_x / 21101–21117); NAB credit cards per staff (21124–21199); key accounts: 11103 NAT ABF Donations, 11104 NAT Operations, 21304 Unearned Revenue, 21103 PAYG, 12300/12301/21600/22300 AASB 16 (54 Wellington St Collingwood lease).
- Segmentation: Department (86 active/114), Class "Class/Project" (312 active/952, ~67% inactive), Location/Branch (36 active/38), plus Project/Job records (~281 active/831, ~66% inactive). 3 branch-code mismatches found (MOR, BUN, SHI). 279 active projects, 12–15 project types, no enforced naming convention — proposed 4-segment standard [PROGRAM]_[FUNDER]_[TYPE]_[FYSTART FYEND] from FY2026-27 (per Project Codes Analysis, Jul 2026).
- Users/roles: 221 active user-role assignments across 52 roles; ~160 employees mostly on "Birdlife ESS Centre_No projects". Admins: BLA362 Mathew R Hema, BLA100 Claudia L Abad (Finance Manager), BLA058 Infinet Cloud Support. External logins: Infinet Cloud, Fusion5, RSM Audit (CEO Hands-Off), ICS Support.
- Customisation footprint small: 470 scripts (450 from vendor bundles), only 20 custom (7 Fusion5 "F5:", 13 "SF:" custom NAB bank-feed connector with PGP/SSH); 7 workflows (5 custom, incl. Vendor Invoice Approval auto-approving no-PO bills entered by Bookkeeper–Branches role). Native Approval Routing is switched OFF for all 7 transaction types.
- Reporting: 212 saved searches (115 never run; 46% owned by Fusion5 Support login; 43 run in 2026), 34 saved custom reports (incl. duplicates and "test"/"test1").
- Data volume: 587,260 GL journal lines back to Dec 2016; vendor bills to Jul 2017.

### Integrations & data flows
- Only 2 formal integration records (Default Web Services, SuiteCloud Development Integration) and 1 active access token. Bundle audit (212 events, 7 bundles) confirms **no CRM/fundraising/donor/BI integration exists in NetSuite** — Salesforce data reaches NetSuite via **manual monthly CSV export/import** by Finance (see Fundraising section). NAB bank feeds via custom SF: scripts; EFT payments via Electronic Bank Payments bundle; payroll via Infinet Cloud bundle with STP to ATO.
- Salesforce↔NetSuite flows (Reconciliation Guide, 1 Jul 2026): Web orders (WooCommerce)→SF Opportunities→NS sales invoices; donations→SF→NS bank deposits/income; memberships→NS 41001/41002; recurring donations & direct debit batches→NS bank receipts. SF GAU allocations map to NS GL codes.

### Current state (with dates)
- **BC migration decision status:** Two consultant documents recommend migrating to Microsoft Dynamics 365 Business Central: the BC Migration Business Case (Jul 2026, status "Pre-Implementation Advisory") and the NetSuite System Review (10 Jul 2026) which concludes "proceed with a planned migration", **conditional** on: vendor-backed licensing quote (160 employees/221 roles; BC tiers Team Member ~$8–10, Essentials $80, Premium $110/user/mo; claimed >$100k/yr licence saving), finance/payroll team interviews, Class/Project data cleanse, early Infinet Cloud & Fusion5 engagement for payroll, remediation of 4 flagged role templates with excess GL/journal rights (BirdLife Accountant National Office, EP Configurator, EP Processor, Payroll Administrator/Processor family ×11), full volume extraction, rebuild of only confirmed-active searches/reports, and rebuild of 20 custom scripts/5 workflows as BC extensions. Business case recommends Employment Hero as payroll platform with BC, phased (not big-bang) migration, no historical transaction migration (archive to SharePoint), Power BI from day one. **No final signed decision or vendor quote is documented — status remains recommended/advisory.**
- **Bank reconciliation backlog:** 11104 NAT Operations 378 unmatched items and 11103 NAT ABF Donations 120 unmatched items, both last reconciled **31 March 2022** (4+ years). Flagged as urgent control risk regardless of BC decision; must be cleared pre-migration.
- OAuth2 findings prepared 20 Jul 2026 for CFO David Thompson (see below).

### OAuth2 certificate findings (20 Jul 2026)
- OAuth 2.0 Client Credentials (M2M) certificate on the **SuiteCloud Development Integration**; Certificate ID `7SCEnbQf6XYE-nv-8z_q0oWmPNm3RM5aCWD7A2WSklo`; created 28 Oct 2024; **valid 17 Sep 2024 → expires 17 Sep 2026**; not revoked.
- Linked entity BLA216 Rachel Munt; created/referenced by Matej Fucek — **both have left BirdLife** (orphaned credential). Zero recorded activity in all four log categories (SOAP, REST, RESTlets, AI Connector); integration record unchanged since 25 Jul 2024.
- Recommendation: confirm with IT/NetSuite partner no infrequent scheduled job depends on it, then **revoke first, monitor, then delete**. No changes made yet — action pending.

### Open actions, risks & known issues
- OAuth2 M2M cert expires **17 Sep 2026** (~6 weeks away as of digest date); owner-orphaned; revoke/replace decision outstanding.
- Bank rec backlog since 31 Mar 2022 (378 + 120 items) — unresolved.
- Approval routing disabled; control relies on manual status changes + one custom workflow.
- 4 role templates with excessive GL/bank/journal rights (segregation-of-duties risk).
- Class/Project lists ~two-thirds inactive; placeholder "_NOT_SPECIFIED"/"GEN_OVERHEAD" projects still active; some projects missing Customer (funder) field.
- Credit cards 21124–21199 and Unearned Revenue 21304 need clearing/documenting pre-migration.

### People named
Mathew Hema (ICT/admin, BLA362), Claudia L Abad (Finance Manager, BLA100), David Thompson (CFO), Rachel Munt (former, BLA216), Matej Fucek (former), Cat Stewart, Stacy Gurrie, Bruce Potgieter (saved-search owners), Sue Siwinski (BLA015), Graeme Sheppard (BLA089, branch bookkeepers), Pamela M Fallow (BLA069), Jonathon C Wilson (BLA099, Reporting PMs), Jessica Rooke, Darren Quin, James Johnson (credit-card holders). Vendors/partners: Infinet Cloud, Fusion5, RSM (audit), JB Were (Goldman Sachs), NAB.

---

## 2. Fundraising — Salesforce dashboards + Zapier SF↔NetSuite integration

### Purpose & role
Salesforce (NPSP + AAkPay) is the fundraising CRM/system of record. Five active dashboards: four Fundraising-owned (FR: Major Donors; FR: Total Fundraising Income 2026; FR: Regular Giving; FR: Tax Appeal 2026) and one Finance-owned (2026 Net Income excl GST — the authoritative financial view built on GAU Allocations, mapped to NetSuite GL codes). A WooCommerce branch-payments platform decision extends WooCommerce to all 77 branches' donations/events/merchandise.

### Key configuration facts
- FR dashboards read Opportunity records on Close Date (gross Allocated/Total Amount); Finance dashboard reads npsp__Allocation__c with custom "GAU Net excl GST" field on Stripe/receipt date, split reconciled vs unreconciled. Regular Giving uses NPSP Recurring Donations (credit card) + AAkPay Recurring Payments (direct debit).
- Figures as at 3 Jul 2026 (latest): Finance Net Income **$6,234,694.64** (reconciled $5,563,577.57; **unreconciled $671,117.07** across 2,878 records; unknown $943.25); FR Total Fundraising **$5,921,988.46** (2025: $7,748,235); Major Donors this year $2,383,741.66; Tax Appeal $1,111,905.07 excl MDs vs $1M target + $289,556.70 MD gifts = combined $1,401,461.77 (14.4% up on last year); Active RDs 1,778 / RPs 392; monthly RD income $56,057.
- Earlier snapshot (29–30 Jun): Finance $5,972,779.84, FR $5,635,389.78, unreconciled $409,202.27 — unreconciled grew **$261,915 in 3 days**.
- Seven documented discrepancies: (1) Close Date vs bank posting date (1–3 business days); (2) membership (41001) & subscriptions (44023) excluded from FR scope (Membership & Publications team owns them); (3) **MD double counting** in program tiles (Regular Giving, Bequests, Major Gifts tiles all include MD gifts; tiles are independent queries — sum ≠ grand total, $9,089 gap; ~$37,500 confirmed double-counted); (4) GST on merchandise GL 44013 (~$7,224/yr); (5) unreconciled income; (6) no GL-code↔FR-program mapping (now built, Section 7 of Master Technical Guide); (7) Tax Appeal MD gifts intentionally excluded from appeal dashboard.

### Zapier SF↔NetSuite integration
- **Zap ID 371228125** — "Unreconciled Income Exception Report", built during the Jul 2026 review. Schedule trigger every Tue & Fri 12:00 AM AEST → Salesforce Find Records (report 00ORF0000033T6z2AE, unreconciled Opportunities, last 7 days) → NetSuite Find Records (account 3440597, Token-Based Auth, ±3-business-day matching) → email HTML exception table to mathew.hema@birdlife.org.au.
- **Status: DRAFT — not published.** Prerequisites before activation: connect Salesforce (OAuth) and NetSuite (TBA: integration record + consumer key/secret + token ID/secret, user Mathew Hema, Administrator role), test each step, second-person review, then Publish.
- Underlying architecture today: **no real-time API integration** — monthly manual CSV export from Salesforce imported to NetSuite; Stripe webhook creates SF Opportunities; bank clears 1–3 days later into NAT account 118636581.
- Note: `Fundraising/BirdLife_Zapier_Salesforce_NetSuite_Integration_Guide.docx` (2026-07-03) is a **CORRUPTED source file** — content unrecoverable; the Master Technical Guide (same date) covers the Zapier build.

### Current state (with dates)
- Master Technical Guide v1.0 FINAL (3 Jul 2026) is the authoritative reference; all original dashboard figures verified accurate against live data.
- Recommendations pending team decisions (Stakeholder Brief, Jul 2026): date-gap policy (Option A: SF Close Date + NS +3-day month-end window, from 1 Aug 2026), Zap activation/testing, backlog owner for 2,878 unmatched transactions, Tax Appeal combined-figure reporting, mapping-table ownership (suggested: Mathew, quarterly review).
- Branch Payments working session (Jun 2026): WooCommerce confirmed as single branch payments platform (chain WooCommerce→Stripe→Salesforce→Ortto, via existing miniOrange layer); pilot branches Top End + Southern NSW; Blitzm is build vendor; decision log largely unanswered at time of writing.

### Open actions, risks & known issues
- $671,117 unreconciled (growing fast) — donor stewardship (thank-yous) missed for unmatched gifts.
- Zapier Zap unpublished; NetSuite TBA credentials not yet created.
- MD double counting unfixed (reconfigure Bequests/RG tiles or add "do not sum" label); grand-total report deduplication unverified.
- NetSuite bank rec overdue since 31 Mar 2022 flagged again here as CRITICAL.
- GL↔FR mapping table needs an owner and quarterly review.

### People named
Mathew Hema (owner of Zap/mapping; facilitator), John, Veronica (Finance & Ops), Kate, Jonathon, Helena (Fundraising & Partnerships), Shantal (Supporter Care), Nina (ICT), James (Participation & Branches), Ben (Blitzm). Role-based: Finance Manager, Fundraising Manager/Director, Salesforce Administrator, Fundraising Ops/Database Manager.

---

## 3. Conga (Salesforce document generation) — audit & replacement

### Purpose & role
Conga Composer (APXTConga4) + Conga Batch (APXT_BPM) + Conga Trigger (CongaWorkflow, v8.22, installed 15 Mar 2024 by Ross James) generate and email donation receipts, EOFY tax receipts, membership receipts and Sprint 7A/7B renewal letters from Salesforce data. **Mission-critical: daily Donation Receipts batch (Conga Batch-0008, 7:00 PM AEST) processes ~50–200 receipts/day.**

### Key configuration facts
- Inventory (audit, Jun 2026): 10 Solutions (only ~4 production; 5–6 test/incomplete), 31 templates (all Word .docx; CMT-00007 live EOFY; CMT-00031 has NO file; CMT-00004/00015 locked to an owner), **172 SOQL Conga Queries** (renewal triplets: batch/detail/GAU allocations), 50–79 Batch records, 35 Conga email templates (CET-00000 "Donation Receipt – Cover Email (H5N1 Bird Flu)" updated 23 Jun 2026 by Mathew Hema for the Bird Flu emergency appeal).
- Critical control fields outside package: Receipt_Status__c, Regenerate_donation_receipt__c, Conga_Composer_URL__c (Opportunity); Generate_Current_FY_EOFY_Receipt__c, Generate_Previous_FY_EOFY_Receipt__c, EOFY_Batch_Downloaded_Year__c, Conga_Composer_EOFY_Batch_URL__c (Contact). NOTE: deployed EOFY batch sets MFTSValue0=**false** after sending — counter-intuitive convention needing clarification/data audit before migration.
- Key query "BatchEOFYLastYr" (0Q_008EAQ302210); EOFY batch template 0T_003EAQ799020. Experience Cloud self-service flows: "[Community] Generate EOFY receipt", "[Community] Regenerate donation receipts". Consolidated PDF print output to Content Workspaces 0585g000000H8CCAA0 / 058I800000004BmIAI.

### Integrations & data flows
Conga cloud endpoints via OAuth Connected Apps (Composer AP v24.0, Batch v24.0, Conga_Trigger; multi-region APAC/NA/EU). Data from NPSP objects (npe01__OppPayment__c, npsp__General_Accounting_Unit__c). Output: email to donor, Salesforce Files, or consolidated print PDF.

### Current state (with dates)
- Preliminary replacement analysis 22 Jun 2026; deep-dive Composer audit Jun 2026; native-migration technical guide 1 Jul 2026 (for new developer onboarding). Direction: replace with native Salesforce (Flow + Apex + Visualforce PDF + Lightning Email Templates + LWC) — no extra licences. Recommended phased order: EOFY Batch Receipts → Donation/Membership/Photography receipts → Sprint 7A/7B renewals; parallel-run ≥2 weeks per phase before disabling Conga; uninstall last.

### Open actions, risks & known issues
- **CRITICAL:** EOFY Receipt manual button deleted (solution references template CMT-00031 with no file) — individual EOFY receipts cannot be generated manually; must be fixed before EOFY period (Jul 2026).
- **CRITICAL:** EOFY Batch Receipts solution stored URL ≠ live button URL — using "Regenerate Solution" would deploy the wrong URL and break the live batch.
- **HIGH:** Conga hosted infrastructure appears degraded (About page broken iframe, Setup page blank) — possible product end-of-life; accelerates replacement urgency.
- Cleanup: 5 test solutions, backup batch records, CMT-00031; locked templates need ownership transfer; pre-uninstall: export all 172 queries, download 31 templates, capture 35 email templates.

### People named
Mathew Hema (email template author), Ross James (installed Conga Trigger 2024), Bird Bot (automation owner account), new Salesforce developer (onboarding audience; Karishma per adjacent onboarding docs), Fundraising team (UAT sign-off).

---

## 4. AWS — Birdata middleware

### Purpose & role
AWS account **499522613917** (ap-southeast-2 Sydney) powers the Birdata platform: two EKS clusters (production-/staging-middleware-server-cluster) + ElastiCache Redis, plus standalone EC2 (BirdCount API, Birdata WordPress, Birdata API/Data r7i.xlarge — business-critical), S3 (incl. middleware-server-pulumi-state — critical IaC state), SES, ECR. IaC: Pulumi (since Apr 2024); legacy 2016–2019 resources unmanaged (split IaC model).

### Key configuration facts
- Audit 21 Jun 2026 by Mathew_Hema. ~USD $851.78 June spend (forecast ~$1,224/mo). 8 EC2 (5 running/3 stopped), 9 EBS (7 gp2), 89 snapshots no lifecycle policy, 18 IAM users/16 roles, no SSO, no Savings Plans. Both EKS on Kubernetes 1.33, single node each, nodes on deprecated AL2 AMI, no managed add-ons, API servers public 0.0.0.0/0. Redis 7.1.0 cache.t3.small ×2 — no encryption, no Multi-AZ. Route 53: health checks only (4, all production: birdata.birdlife.org.au, aussiebirdcount.org.au); DNS external.
- Staging: EC2 i-0387e58bede33eb11 (t3.medium), IP 52.65.13.47, VPC vpc-0b0ee83f26708205b, 2 NAT gateways, ~$180–210/mo.

### Current state / staging shutdown status (21 Jun 2026)
- Shutdown report concludes staging is **safe to destroy** (no external traffic, no VPC peering, no Route 53/DNS references; only caveat: confirm no CI/CD or dev tooling hardcodes 52.65.13.47) via single `pulumi destroy` (15–20 min), saving ~$150–200/mo; restorable via `pulumi up`. **Status: recommended only — no evidence in the KB that the shutdown was executed.**

### Open actions, risks & known issues (as audited)
- **CRIT-01: EKS 1.33 standard support ended 29 July 2026** — that date has now PASSED (digest date 2 Aug 2026); unless upgraded since the audit, both clusters are in paid extended support (~$876/cluster/yr) with production upgrade blocked by 2 unresolved upgrade insights. CRIT-02: AL2 node AMI deprecated (no patches since Nov 2025).
- CRIT-03: IAM user `planticle-s3-full-access` inactive ~10 years with full S3 access — delete. HIGH-01: admin **Mathew_Hema has no MFA**. HIGH-02: EKS API public. HIGH-03: production Redis unencrypted. HIGH-04: stale IAM users (hanzab 780d, Ross_James 1000d, species-images-s3-write 1727d, Ahilya_Sinha 412d, duplicate Ahilya_Sinha_BirdLife never used). MED: no DLM snapshots, gp2→gp3, ECR tag mutability, 3 stopped instances billing EBS, split IaC.

### People named
Mathew_Hema (auditor/admin), Andrew_Dunn, James_Watmuff (active, MFA OK), James_OBrien (no MFA), Ahilya_Sinha, Botian_Chen, Krish_Gupta, Ross_James, hanzab (stale), service accounts (birdata, birdcount-dev, ses-smtp users, planticle-s3-full-access).

---

## 5. Ortto — MySQL RDS integration

### Purpose & role
Ortto is BirdLife's customer data platform / marketing automation (donor & member communications; receives WooCommerce/Salesforce donor data; WordPress plugin Ortto v1.0.24 active). The guide (Jun 2026) is a developer how-to for syncing Amazon RDS MySQL 8.x contact data into Ortto's CDP via REST API, since Ortto has no native MySQL connector.

### Key configuration facts & data flow
- Pattern: Node.js `sync.js` (mysql2 + axios + dotenv) queries RDS `contacts` table → maps to Ortto person fields (str::email primary merge key; str::ei = MySQL PK as external ID; phn::phone; geo::city/country; custom `str:cm:*`) → `POST {base}/v1/person/merge` with X-Api-Key header; async:true; merge_strategy 2 (overwrite); max 100 people/request; 500ms delay between batches. AU base URL `https://api.au.ap3api.com`. Custom API key created under Settings→Data sources, main association field = Email.
- Security guidance: never open RDS 3306 to 0.0.0.0/0; keys in .env/AWS Secrets Manager. Automation: Lambda + EventBridge (recommended) or EC2 cron; incremental sync via `updated_at` watermark.

### Current state / open items
Generic how-to guide (Jun 2026), current; no evidence of a specific deployed instance, schedule, or named RDS database in the KB — implementation status unknown. Related fact: AWS audit found the RDS service-linked role last active 789 days ago ("no RDS in use"), implying this sync may not yet be running in the audited account.

### People named
None (anonymous developer guide).

---

## 6. WordPress (birdlife.org.au) — site health + cart flood incident

### Purpose & role
Main public website + WooCommerce e-store, hosted on **WP Engine** (production env "birdlifeaus"), Cloudflare CDN. Basis for the coming WooCommerce membership build (with vendor Blitzm) and branch payments platform. Integrations: miniOrange Salesforce sync, Ortto v1.0.24, Stripe gateway, Gravity Forms (+Stripe, +Pardot), WooCommerce Subscriptions/Memberships.

### Key configuration facts
- Health report v2 (Jun 2026): WordPress 7.0, PHP 8.4.22, 82 plugins (62 active/20 inactive), 30 awaiting update, 5 inactive themes, page cache 31ms (excellent), overall health **5/10 NEEDS ATTENTION**. Critical: WP_DEBUG_LOG writing publicly; 1,063 autoloaded options (~1MB/request); WP File Manager v8.0.2 (CVE history) and WP phpMyAdmin active; WP 2FA 4 major versions behind; OPcache not enabled; disk-space check failing; 6 expired licences (WooCommerce Subscriptions — running unlicensed on live payments — Memberships, GTM PRO, Import Export Suite, TIV Multi-currency, GF↔Pardot). Membership pricing on page outdated ($79/$35 → should be $84/$65/$132/$35). Spellbook plugin inactive breaking GP Populate Anything. All CRITICAL/HIGH items must close before Blitzm membership build.

### Cart flood incident (report 14 Jul 2026)
- **Symptom:** repeated 504 Gateway Timeouts; site error rate 6.67% ("Poor"), cache hit ratio 55.4%; /cart 4,410 5xx errors of 66,507 requests over 30 days; bandwidth spike ~30GB on ~9 Jul vs 14–16GB/day baseline.
- **Root cause:** sustained automated distributed flood of `/cart/?remove_item=<hash>&_wpnonce=…&add-to-cart=…` requests from hundreds of IPs worldwide, cycling product IDs 37909/37910/37911/30651, varied user agents. Cart pages are session-specific/uncacheable → each request hit PHP/DB → PHP worker exhaustion → 504s for attackers and legitimate users alike. Source/actor not identified (unresolved attribution; consistent with scripted abuse, not organic traffic).
- **Mitigation deployed:** WP Engine Web Rules **Deny** rule (first-ranked): URI regex `^/cart` AND query `remove_item=` AND Referer NOT matching `birdlife\.org\.au`. Caveat: privacy browsers stripping Referer could be false-positived. Follow-ups: monitor logs 24–48h; raise WP Engine platform-level bot/DDoS mitigation.
- Also found 14 Jul: **ACF to REST API v3.3.4 flagged as known vulnerability** (priority fix); 31/83 plugins outdated (Smart Plugin Manager available, 2/115 licences used); /wp-login.php >50,000 hits/30d at 67% error rate (brute-force noise); mobile PageSpeed 46/100; WordPress core update marked "Deferred" — confirm intentional.

### Open actions & risks
Cart-flood rule effectiveness monitoring; ACF-to-REST-API replacement; 30–31 plugin updates; licence renewals; debug log/phpMyAdmin/File Manager remediation; autoloaded options cleanup; OPcache request; membership build blockers (Memberships licence+activation, family membership custom dev, hidden hardship product, branch pilot pages, pricing update).

### People named
Nina Lewis (ICT Lead — sign-off), Mathew Hema (Project Manager — sign-off), Nina (24h critical fixes), Jonathon (miniOrange/OIDC dependency), James V (Pardot confirmation), Blitzm (build vendor), Finance/Marketing (licences, Meta Pixel).

---

## 7. Asana — Salesforce email-to-task rule (20 Jul 2026)

### Purpose & role
Enable Salesforce Case emails (from zeus@birdlife.org.au) sent to x@mail.asana.com to auto-create tasks in the "IT Operations Project Plan" Asana project (via "#IT Operations Project Plan" subject tag).

### Issue, root cause & fix
- Asana rejected the email: sender authenticated as salesforce.com but From domain birdlife.org.au. Root cause: **birdlife.org.au SPF record does not authorise Salesforce's mail servers**; Asana validates SPF/DKIM, treating the message as spoofing.
- Required actions (IT/DNS admin, not done yet): (1) add `include:_spf.salesforce.com` to the birdlife.org.au SPF TXT record; (2) enable Enhanced Domains + configure DKIM signing in Salesforce Setup (Email > Deliverability); (3) re-test Case email → Asana task creation.
- Explicit warning: this is a domain-wide email-authentication change affecting deliverability/anti-spoofing for all of birdlife.org.au — must go through IT/security review, not ad hoc. **Status: open/pending.**

### People named
None individually (IT/DNS admin, Microsoft 365 admin roles referenced).

---

## 8. ABC2026 fix implementation report (26 Jun 2026)

### Purpose & role
Retest report for 5 fixes to the **Aussie Bird Count Registration 2026 – Testing** form (Gravity Forms ID 15) on aussiebirdcount.org.au; retest results recorded in spreadsheet "Tester 4 – Retest" (columns W/X/Y). Tester: Mathew Hema.

### Results
| Row | Issue | Fix | Result |
|---|---|---|---|
| 9 | No PO Box message | Helper text added under Address field | PASS |
| 23 | Parent/Guardian details not required for under-18s | List field ID 91 set Required | FAIL – preview mode only (config confirmed correct) |
| 24 | Consent checkbox not enforced | Required confirmed on checkbox ID 95 | FAIL – preview mode only (config confirmed correct) |
| 27a | T&C link lost form data (same tab) | target="_blank" on T&C + Privacy links | PASS |
| 27b | T&C page showed 2025 content | Page/heading/closing date updated to 2026 (closing Wed 29 Oct 2026) | PASS |

### Key finding & open action
Gravity Forms preview URL (`?gf_page=preview&id=15`) **bypasses server-side validation by design**, so required-field enforcement (rows 19, 23, 24) cannot be verified in preview. Outstanding: retest on the live page `/register-2026-test/` with a fresh MyBirdLife test account not yet registered for 2026 (test password Finch2026, incognito). Compliance stakes: guardian details for minors (safeguarding) and consent capture (Privacy Act 1988 / APPs). **3 of 5 fixes fully verified; 2 pending live retest.**

### People named
Mathew Hema (tester).

---

## 9. Claude — QUICK-REPLAY-GUIDE (25 Jun 2026)

### Purpose & role
A how-to reference for replaying a saved sequence of **11 security-architecture prompts** in a fresh Claude chat, three ways: (1) sequential manual paste from ANWA-Prompts-SimpleList.txt (~90 min); (2) batch mode from ANWA-Complete-Prompt-Sequence.md (~45–60 min); (3) automated via Claude Code with ANWA-Prompts.json (~50 min). Outputs: 13+ documents (security audit, 6-phase remediation plan, Neon DB failover, staging/prod separation, monitoring/alerting, PDPA 2010 (Malaysia) compliance, privacy docs, developer & business security guides, 2-person execution plan).
Companion files referenced: ANWA-Complete-Prompt-Sequence.md, ANWA-Prompts.json, ANWA-Prompts-SimpleList.txt, ANWA-SECURITY.md.

### Caveats / status
Content targets **"ANWA 2.0"** with Malaysia/PDPA references and explicitly suggests customising ("change ANWA 2.0 → your company name, Malaysia → your region") — i.e. it is a **template imported from another context, not BirdLife-specific**. Companion ANWA files are not present in this KB. Operationally useful only as a method reference for prompt-replay workflows; treat its security content as non-BirdLife.

### People named
None.

---

## 10. Document register

| Relative path | Date | Description | Status |
|---|---|---|---|
| Netsuite/BirdLife Australia - NetSuite System Review.md | 2026-07-12 | Independent consultant review of live NetSuite (dated 10 Jul); recommends conditional BC migration; permission matrix, bank-rec backlog, saved-search audit, data volumes | current |
| Netsuite/BirdLife_Australia_BC_Migration_BusinessCase.docx (.md) | 2026-07-03 | BC migration business case/advisory for CFO & Finance Manager; licensing, Salesforce/payroll integration architecture, pre-migration actions, 5-yr TCO | current (pre-implementation advisory; complements 10 Jul review) |
| Netsuite/BirdLife_Australia_NetSuite_GL_Guide.docx | 2026-07-01 | GL/chart-of-accounts orientation guide for new staff (full code listing, transaction flows, tips) | current |
| Netsuite/BirdLife_Australia_NetSuite_User_Guide.docx | 2026-07-03 | Role-by-role NetSuite usage workflows (ESS, bookkeepers, accountant, PMs, CEO, payroll, admin) | current |
| Netsuite/BirdLife_Australia_Project_Codes_Analysis.docx | 2026-07-03 | Analysis of 279 active project codes; 9 structural problems; proposed 4-segment naming convention + 10-step implementation plan | current |
| Netsuite/BirdLife_Australia_Reconciliation_Guide_SF_vs_NetSuite.docx | 2026-07-01 | Step-by-step SF↔NS reconciliation process for Finance & Fundraising; common issues/fixes | current |
| Netsuite/NetSuite_OAuth2_Certificate_Findings.docx | 2026-07-20 | OAuth2 M2M certificate expiring 17 Sep 2026; orphaned (Munt/Fucek departed); revoke-then-delete recommendation | current — action open |
| Fundraising/BirdLife_Australia_Dashboard_Review_2026.docx | 2026-06-29 | First full dashboard review (29–30 Jun figures; $409k unreconciled), tensions & 4-stage plan | superseded (by v2 and Updated) |
| Fundraising/BirdLife_Australia_Dashboard_Review_2026_v2.docx | 2026-07-02 | Restructured review, 30 Jun figures; program-tile double-count tables | superseded (by Updated, 3 Jul figures) |
| Fundraising/BirdLife_Australia_Dashboard_Review_2026_Updated.docx | 2026-07-02 | Updated review verified against live dashboards 3 Jul (Finance $6.23M; unreconciled $671k) | current |
| Fundraising/BirdLife_Australia_Master_Technical_Guide_2026.docx | 2026-07-03 | v1.0 FINAL master technical reference: 5 problems + fixes, Zapier Zap 371228125 (DRAFT) full config, NetSuite TBA setup, GL↔FR mapping | current |
| Fundraising/BirdLife_Australia_Stakeholder_Brief_2026.docx | 2026-07-03 | Plain-language brief; 5 findings, 4 builds, 5 decisions needed | current |
| Fundraising/BirdLife_Branch_Working_Session.docx | 2026-06-19 | Branch payments/WooCommerce working session: platform decision, questions & decision log per team, pilot Top End + Southern NSW | current (many decisions still unanswered) |
| Fundraising/BirdLife_Dashboard_Discussion_PlainEnglish.docx | 2026-07-02 | Plain-English discussion aid (30 Jun figures) | superseded (figures outdated by 3 Jul docs) |
| Fundraising/BirdLife_Zapier_Salesforce_NetSuite_Integration_Guide.docx | 2026-07-03 | Zapier SF↔NetSuite integration guide (source file unreadable) | **corrupted** |
| Conga/Conga Configuration Technical Guide - Birdlife Australia Salesforce Org.docx | 2026-06-21 | Conga Trigger + Conga Batch package inventory (v8.22, installed Mar 2024) | current (supplementary) |
| Conga/1Conga Replacement Analysis_ Migration to Salesforce Flows and Code.docx | 2026-06-22 | Preliminary replacement assessment (connected apps, options, roadmap, risks) | superseded (by audit + migration guide) |
| Conga/Conga Composer Audit — BirdLife Australia Salesforce Org.docx | 2026-06-22 | Deep-dive audit: 10 solutions/31 templates/172 queries/79 batches/35 email templates; critical broken-button & URL-mismatch findings; native replacement designs | current |
| Conga/BirdLife_Conga_to_Salesforce_Native_Migration_Guide.docx | 2026-06-30 | Step-by-step native migration guide for new developer (dated 1 Jul); EOFY end-to-end, Apex/Flow build plan, checklist | current |
| AWS/AWS Review.docx | 2026-06-21 | Full AWS infrastructure audit (acct 499522613917): inventory, costs, IAM, 16-finding action plan | current — but EKS deadline (29 Jul 2026) has now passed; verify remediation |
| AWS/AWS Birdata Middleware — Staging Shutdown Report.docx | 2026-06-21 | Staging environment dependency audit + Pulumi shutdown procedure; ~$150–200/mo saving; safe to destroy | current (recommendation; execution unconfirmed) |
| Ortto/Ortto-MySQL-RDS-Integration-Guide.html (.md) | 2026-06-22 | Developer guide: RDS MySQL → Ortto CDP sync via /v1/person/merge (Node.js, Lambda/cron automation) | current (generic guide; deployment status unknown) |
| WordPress/BirdLife_WordPress_Health_Report_v2.docx | 2026-06-19 | Full WP health/plugin/security audit + WooCommerce membership build readiness; 20-item priority list | current (pre-incident; partially overtaken by 14 Jul findings — plugin counts/ACF vuln differ) |
| WordPress/BirdLife_Site_Review_and_Cart_Flood_Report.md | 2026-07-14 | Cart "remove_item" flood incident (504s), deny-rule mitigation, holistic review (ACF-to-REST-API vulnerability, 31 outdated plugins) | current |
| Asana/Asana Salesforce Email Rule.md | 2026-07-20 | Salesforce-Case→Asana email rejection; SPF/DKIM root cause; DNS fix required | current — action open |
| ABC2026_Fix_Implementation_Report_files/ABC2026_Fix_Implementation_Report.doc (.md) | 2026-06-26 | ABC 2026 registration form fix retest (GF ID 15): 3/5 PASS; 2 pending live retest due to preview-mode validation bypass | current — action open |
| Claude/QUICK-REPLAY-GUIDE.txt (.md) | 2026-06-25 | How to replay 11 "ANWA 2.0" security prompts in Claude (3 methods); companion ANWA files not in KB | stale (non-BirdLife template content; ANWA/Malaysia specific) |
