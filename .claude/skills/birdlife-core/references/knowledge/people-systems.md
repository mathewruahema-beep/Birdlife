# People Systems Digest — Employment Hero, Culture Amp, Google Workspace

Compiled: 2026-08-02. Sources: all .md files under `text/Employment Hero` (incl. `aPI/`), `text/Culture Amp`, `text/Google`. Dates from `manifest.tsv`.

---

## 1. Employment Hero (incl. Entra sync, payroll migration, TeamOrgChart)

### 1.1 Purpose & role
- Employment Hero (EH) is BirdLife Australia's HR system of record / intended single source of truth for people data (names, roles, worker codes, locations, employment status, reporting lines). EH Org ID **450790**; API base `https://api.employmenthero.com/api/v1/organisations/450790/`. Single employing entity: BirdLife Australia, ABN 75 149 124 774.
- Current subscription is **HR-only** (no Payroll module — Add-ons shows Payroll "Connect", no Payroll nav icon). Payroll runs entirely outside EH in NetSuite (instance 3440597) via **"Infinity Cloud" = Infinet Cloud Payroll, now ZonePayroll** (SuiteApp bundle 30500, v26.3.03); all ~128 employees paid in one pay run.
- Modules in use: People, Compliance, Time, Engagement, Development (Go1-powered EH Learning — Connected), Performance (Goals/OKRs and Performance Reviews in use; templates exist e.g. "General", "Q2 Performance Review - Senior Leaders", but **no active Review Period** configured), Workflows, Reports.
- Employee guides exist for login (SSO), Goals (employee + manager) and Performance Reviews (employee + manager), all dated 2026-07-29.

### 1.2 Key configuration facts
- **SSO/login**: SAML SSO via Microsoft Entra ID ("Sign in with SAML SSO" using @birdlife.org.au Company Email, or via the M365 Apps portal tile). Company Email must be unique and populated or SSO login fails. EH enforces its own second 2FA step after Microsoft auth (ATO-driven compliance requirement, by design; 45-day device memory). Account Email may legitimately remain a personal address.
- **M365 add-on**: Settings > Add-ons shows Microsoft 365 "Connected" — one-way EH→M365 provisioning/deprovisioning (name, work email, dept, title, status).
- **EH public API**: OAuth 2.0 with PKCE; access tokens expire every 15 min; refresh tokens rotate on each use; rate limits 20 req/s, 100 req/min. **Full API (write-back, NetSuite/LearnUpon integrations) requires Platinum tier.** OAuth app scopes are locked permanently at app creation — cannot be edited later. API access is limited to the authorising user's platform role; EH docs recommend an admin/owner account.
- **Data entry rules** (Data Rules doc, 2026-07-29): BLA### worker code mandatory; Company Email format firstname.lastname@birdlife.org.au; Work Location = state abbreviation; use "Add Employee"/Start onboarding (not CSV Quick-add); capture **personal email** at invite (root cause of the broken invite loop was using work email); reactivate, don't duplicate, rehires; onboarding checklists must have scope + recipient toggles set or they silently never run.
- Configuration gaps found in the July 2026 audit: Company Default Super Fund blank, **no ATO integration, no electronic TFN declaration** (live compliance exposure per new starter); all Mandatory Field toggles off; onboarding checklist unscoped; **no offboarding checklist**; dozens of duplicate inactive workflows; payslips hidden from employee menu; Time menu off; only 3 leave categories; Document Management/Company Policies empty; 2 aged workplace incidents pending; wrong industry classification; Cost Centres has a single entry ("Supporter Care"); Expense Categories empty; no Authorising Signatory; no pinned reports.

### 1.3 Integrations & data flows
- **EH → Microsoft 365/Entra ID** (native add-on): account provisioning/deprovisioning + profile fields; email address is the match key (EH work email must equal Entra Member UPN @birdlife.org.au; ~2,700 #EXT# guest accounts to exclude from matching). Sync **overwrites** Entra values (blank EH fields blank out Entra); planned 4-hour schedule per TeamOrgChart plan.
- **EH → Entra ID Employee ID sync** (custom, aPI/ docs, 2026-07-09): Azure Logic App (Consumption) `logic-emphero-entra-sync` in RG `rg-emphero-entra-sync`, subscription "BirdLife Australia Azure" f0b2d7cf-c6f1-4ab0-9c67-cc3dff6721cd, tenant 2b431a7b-9a21-4b53-8943-4a10ff69970d. Daily poll: Key Vault `kv-emphero-sync` (5 secrets: EH-CLIENT-ID/SECRET/ORGANISATION-ID/REFRESH-TOKEN, GRAPH-CLIENT-SECRET) via system-assigned managed identity → refresh EH token → GET employees → Graph `$filter=mail eq '{company_email}'` → PATCH `employeeId`. One-way EH→Entra, employeeId field only; join key = EH `company_email` ↔ Graph `mail`. Entra app registration **EmpHero-EmployeeID-Sync** (client 86345594-9286-40ae-85a8-f9c1c63e5482) has User.Read (delegated) + User.ReadWrite.All (application, admin-consented); Graph client secret **expires 2027-01-05**. EH OAuth app has 4 read-only scopes (teams:employees:list, employees:list, employees:show, employees:onboard_polling_status). Monitoring dashboard `emphero-entra-sync-monitoring`. Deprecated Function App resources (func-emphero-entra-sync, AustraliaEastPlan, stemphentrasync) pending user deletion; empty "Azure subscription 1" (82c42bb2-…) pending cancellation.
- **EH → Azure AD manager sync via Zapier** (2026-06-26 guide): Zapier trigger "New or Updated Employee" → filter out Contractors → Graph client-credentials token (app **EH-OrgSync-Zapier**, User.ReadWrite.All) → PUT manager `$ref`. ~4 Zapier tasks/employee; usage 142/2,000 monthly. This design fed the old Org Explorer and is effectively superseded by the native EH M365 integration approach (June 29 plan).
- **TeamOrgChart+** (TeamImprover.Com Ltd, v2.1.20): third-party org chart app for Teams/Outlook/M365, deployed org-wide via Teams Admin Center; replaces built-in Org Explorer (blocked org-wide). Reads live from Entra ID (no cache); chart admin andrew.dunn@birdlife.org.au. Implementation plan (Option 3, June 2026): EH M365 field sync (Job Title, Department, Manager, Office Location — NOT Display Name/UPN/address) every 4 h + Power Automate flows: new-starter provisioning (create Entra user, assign M365 Business Premium licence, notify IT/manager) and leaver offboarding (30-min delay → revoke sessions → disable account → convert mailbox to shared → remove licence → 90-day delete reminder). CEO Kate Millar intentionally has no manager (org-tree root).
- **Culture Amp ← EH**: one-way daily pull of employee master data (name, email, employee ID, dept, manager, location, start date). Per the Holistic doc (2026-07-27) a Culture Amp sync is **already active but ungoverned** — configured from the Culture Amp side; Culture Amp does not appear in EH's Add-ons list. Roadmap docs (same date) treat connection as future Phase 5 and could not confirm the subscription/tier — an unresolved internal contradiction to verify.
- **NetSuite**: **no live link today** — employee/pay data maintained twice (EH + NetSuite), the biggest data-integrity risk in the landscape. Future: EH Payroll native journal-service integration to NetSuite (token-based auth: Account ID, Consumer Key/Secret, Token ID/Secret; map pay categories/departments to GL accounts/classes; worker code as employee match key).
- **LearnUpon** (learn.birdlife.org.au): partially configured Webhooks v2 → Zapier catch-hook **[catch-hook URL REDACTED — see GOVERNANCE.md pre-distribution checklist; this URL is live and must be rotated]** with only "Course enrolment" ticked (not completion); Zapier account belongs to keith.tsui@birdlife.org.au; no write-back to EH exists. Proposed future bridge: LearnUpon completion webhook → Zapier → PATCH EH Certification API (Platinum required).
- **EH Learning (Go1)**: connected add-on; Go1 End User Minimum Terms deliberately left un-accepted pending decision.

### 1.4 Current state / in-flight work (with dates)
- **System audit & clean-up programme** (Sessions 1–3, ~25–28 July 2026): Programme Plan (28 Jul) defines Phase 0 governance (that week) through Phase 1 invite fixes (wks 1–2), Phase 2 data governance (wks 2–4), Phase 3 workflow/compliance clean-up (wks 3–5), Phase 4 self-service/reporting (wks 4–6), Phase 5 Culture Amp (wks 5–8), Phase 6 Payroll/NetSuite feasibility (separate Finance-led track). As of 2026-08-02 these are plans, not confirmed done.
- **NetSuite→EH Payroll migration** (guide dated 2026-07-27): ~16-week 8-phase plan — data readiness → activate EH Payroll module (requires commercial upgrade) → employee payroll data migration → leave/timesheets → NetSuite journal connection → validation against a closed pay period → one side-by-side live pay run → cut-over and ZonePayroll decommission (read-only retention). Not started; blocked on subscription/commercial decision and data clean-up.
- **Entra employee ID sync** (as of 2026-07-09): built and deployed but **not yet working end-to-end** — blocked by a 403 (EH platform permission on Mathew Hema's account, needs Admin/Owner or org-wide view-employees). Dashboard shows 0 succeeded / 2 failed runs. Refresh-token persistence fix documented but not implemented. Existing read-only EH OAuth app can never gain write scopes; a new EH app with Employees:Update scope is the recommended path for any write-back.
- **Org chart work**: TeamOrgChart+ deployed org-wide and comparison vs EH completed (28–29 Jun 2026). Key fix: Dale Wright's manager in EH should be Lyndel Wilson, not CEO Kate Millar. 2 vacant positions tracked only in TOC. Note a **source-of-truth conflict** between documents: the June comparison doc declares TeamOrgChart (fed by Entra) source of truth with EH updated to match, while all sync designs (June–July) make EH the source of truth pushing to Entra. Latest thinking (July docs) = EH is upstream.

### 1.5 Open actions, risks & known issues
- **Compliance (highest priority)**: default super fund blank, no ATO integration, no electronic TFN declaration — exposure grows with every new starter. Ownership unconfirmed (Phase 0 action).
- **Data inconsistencies** (2026-07-27 review, unresolved as documented): all-caps names (Alice McNeill, Joe Douglas, Karina Schiller, Michael Macdonald); missing BLA worker codes (Catherine Johnson, Joe Douglas, Thea O'Loughlin) — worker code is the payroll/NetSuite join key; "Collingwood" instead of state code (Joe Douglas, Shan Nagar, Thea O'Loughlin); expired invites (Andrew Dinwoodie, Craig Morley, Finn Roff-Marsh); stale statuses (Thea O'Loughlin preboarding; Jessica Rooke, Lynette Plenderleith offboarding); spaced hyphens (Finn Roff-Marsh, Kerri-Anne Bartley, James McCracken-Johnson). Plus 6 employees missing company email and 2 sharing one (SSO blockers). Must be fixed before payroll migration and Culture Amp reliance.
- **Culture Amp already syncing dirty data** (if the Holistic doc's finding stands): connected before clean-up, ungoverned/outside EH Add-ons — inconsistencies have already propagated; correct in EH and re-sync, never fix in Culture Amp. Reconcile against roadmap docs that say it isn't connected yet.
- **Entra sync operational gaps**: 403 blocker (EH role for Mathew's account); rotated EH refresh token not persisted to Key Vault (next run may fail if tokens are single-use); Key Vault secrets have no expiry metadata; Graph client secret expires 2027-01-05; deprecated Function App resources and empty Azure subscription awaiting deletion.
- **Payroll double-entry** between EH and NetSuite continues until migration — ongoing reconciliation burden and drift risk.
- **Keith's orphaned Zapier/LearnUpon webhook** — confirm purpose before building on or repointing; live catch-hook URL is documented in the KB (treat as sensitive).
- Onboarding checklists unscoped / no offboarding checklist — leavers' access removal is currently ad hoc (security gap the Power Automate leaver flow would close).
- EH limitation: no multiple active positions per person; sync overwrites (never merges) Entra fields.

### 1.6 People named
Mathew Hema (Senior ICT Manager; EH admin-role requester; accounts mathew.hema@birdlife.org.au / mathew.hema.admin@birdlife.org.au) · Kate Millar (CEO, org-tree root) · Lyndel Wilson (exec; correct manager for Dale Wright) · Dale Wright · David Thompson (exec, 3 direct managers) · Andrew Dunn (TeamOrgChart admin) · Keith Tsui (Zapier/LearnUpon owner) · Data-issue employees: Alice McNeill, Joe Douglas, Karina Schiller, Michael Macdonald, Catherine Johnson, Thea O'Loughlin, Shan Nagar, Andrew Dinwoodie, Craig Morley, Finn Roff-Marsh, Jessica Rooke, Lynette Plenderleith, Kerri-Anne Bartley, James McCracken-Johnson · Arun Nair / Karishma / Veronica appear elsewhere in the KB (Salesforce), not in these systems.

---

## 2. Culture Amp (SSO)

### Purpose & role
Employee experience platform (engagement surveys, performance, development) intended to complement EH; EH remains the system of record, Culture Amp pulls people data one-way.

### Key configuration facts (SSO setup guide, 2026-07-06)
- Self-service SAML SSO with Microsoft Entra ID requires a **custom non-gallery** enterprise app (the gallery connector is unsupported for this flow).
- Setup: Culture Amp (Account Admin) Settings > Account > Authentication > "+ Add SAML Provider" → copy ACS URL + Entity ID → Azure custom app: Entity ID = Identifier, ACS = Reply URL → Name ID = user.mail, format Email address → assign users/groups (only assigned users can SSO) → download Base64 cert + Login URL → paste into Culture Amp wizard (endpoint URL, X.509 cert, Nameid-format Email) → incognito test → Finish.
- Operational notes: keep password login enabled until SSO confirmed; Azure SAML certs expire ~3 years — rotate ≥2 weeks early; disable any legacy SSO connection with Culture Amp support to avoid duplicate login buttons.

### Integrations & data flows
One-way daily API pull EH→Culture Amp (name, email, employee ID, dept, manager, location, start date); alternative SFTP/CSV mode. Core fields auto-map; custom field mappings are effectively permanent. Initial sync up to 12 h; review created/updated/deactivated counts before first import. Setup typically 2–3 weeks.

### Current state
Contradictory findings dated the same week (2026-07-27): Holistic doc says sync is **live and ungoverned** (configured from Culture Amp side); Roadmap/Programme docs schedule connection as future Phase 5 (weeks 5–8) after data clean-up and could not confirm whether BirdLife holds a subscription or which tier. SSO guide (07-06) is a how-to; no evidence in these docs that Culture Amp SSO is actually configured yet.

### Open actions & risks
Confirm subscription/tier with Culture Amp account contact; confirm whether the sync is genuinely live and who set it up; if live, it has inherited EH data inconsistencies — fix upstream in EH only; sequence any survey launch after EH clean-up; certificate rotation calendar entry.

### People named
None individually in the SSO guide; Mathew Hema is the audience of the related EH docs.

---

## 3. Google Workspace

### Purpose & role
Secondary identity/collaboration estate on domain **birdlife.org.au** (Customer ID C01muaswh), on the free Google Workspace for Nonprofits plan, serving staff plus branch/program communities (24 OUs incl. AWSG, Friends of Hooded Plover, Twitchathon, deactivated users).

### Key configuration facts (Admin Console review, 2026-07-05)
- Groups: 5 total — **Microsoft 365 SSO Users (171 members)** drives federation; ICT Staff (5), Network Liaison Staff (5), Survey Monkey (2, domain-disabled), Classroom Teachers (0).
- Devices: 214 BYOD endpoints, all Approved (Windows/macOS/iOS/Android); no managed Chrome browsers, no network profiles/certificates — device network policy is Google defaults only.
- Apps: 13 core + 59 additional Google services; zero Marketplace/third-party apps added.
- Hybrid identity: Microsoft Entra ID SAML profile assigned to the 171-member SSO group; **rest of the domain signs in directly with Google**. Google is also configured as a SAML IdP for other apps — **its signing certificate has expired** (likely breaking any relying app).
- Storage 328.48 GB of 100 TB pooled (Drive 223.15, Gmail 95.14, Photos 10.19). 15 admin roles; Super Admin held by a small named group. Rules engine is nearly all Google defaults.

### Integrations & data flows
Entra ID federated SSO for the 171-member group; Google-as-IdP path effectively broken by the expired cert. No third-party app footprint managed in-console; 2 configured third-party API apps, 98 apps with historical data access, 0 restricted vs 18 unrestricted API services.

### Current state
Reviewed 2026-07-05 as onboarding awareness for a newly onboarded senior engineer; no in-flight remediation documented.

### Open actions, risks & known issues
- **348 users without any 2SV; 2SV enforcement OFF at domain level** — top remediation with the expired IdP cert.
- Google Cloud session control set to never require reauthentication — validate intent.
- Data protection: 78.1% of scanned sensitive-data Gmail messages sent externally (4.6k sample; some categories likely conservation-content false positives).
- Alert Center history: phishing reports, a super-admin password reset, 3 SSO profile changes, 1 compromise-related spam suspension — phishing/account compromise are the active threat categories.
- Pending Terms of Service acceptance in Account Settings; API controls fully unrestricted.

### People named
None individually (Super Admins referenced as "a small group of named administrators").

---

## 4. Document register

| Relative path | Date | Description | Status |
|---|---|---|---|
| Employment Hero/BirdLife Australia Employment Hero Data Rules.md | 2026-07-29 | EH data-entry process: record creation, emails, worker codes, checklists, termination, hygiene | Current |
| Employment Hero/BirdLife Australia Goals Employee Guide.md | 2026-07-29 | How employees use EH Goals/OKRs | Current |
| Employment Hero/BirdLife Australia Goals Manager Guide.md | 2026-07-29 | How managers create/track team and company goals | Current |
| Employment Hero/BirdLife Australia Performance Review Employee Guide.md | 2026-07-29 | Employee steps for drafting/publishing reviews | Current |
| Employment Hero/BirdLife Australia Performance Review Guide.md | 2026-07-29 | Combined manager+employee review guide (duplicates the two role guides) | Current (redundant combo) |
| Employment Hero/BirdLife Australia Performance Review Manager Guide.md | 2026-07-29 | Manager steps: complete reviews, next steps, reminders | Current |
| Employment Hero/BirdLife_EmploymentHero_CultureAmp_Payroll_Roadmap.md | 2026-07-27 | Session 3: rationale, Culture Amp, payroll/NetSuite feasibility, phased roadmap, click-path fixes | Current |
| Employment Hero/BirdLife_EmploymentHero_Data_Inconsistencies.md | 2026-07-27 | Live People List review: 5 categories of data defects with named records | Current (fixes not yet confirmed) |
| Employment Hero/BirdLife_EmploymentHero_HR_Payroll_Report.md | 2026-07-27 (body dated 28 Jul) | Plain-English findings/plan for HR & Payroll team; decisions needed | Current |
| Employment Hero/BirdLife_EmploymentHero_Holistic_Current_and_Future_State.md | 2026-07-27 | Current-state architecture (M365, Go1, Culture Amp live/ungoverned, NetSuite, LearnUpon), clean-up plan, payroll & LearnUpon future state | Current — most complete architecture picture |
| Employment Hero/BirdLife_EmploymentHero_Programme_Plan.md | 2026-07-27 (body 28 Jul) | Phase 0–6 programme plan with comms plan | Current |
| Employment Hero/BirdLife_NetSuite_to_EmploymentHero_Payroll_Migration_Guide.md | 2026-07-27 | 16-week 8-phase ZonePayroll→EH Payroll migration incl. parallel run | Current |
| Employment Hero/BirdLife_OrgChart_Comparison.md | 2026-06-28 (body 29 Jun) | EH vs TeamOrgChart discrepancies (Dale Wright fix, vacancies) | Stale-ish — snapshot; SoT stance contradicted by later docs |
| Employment Hero/EH to Azure AD Org Sync - Technical Guide.md | 2026-06-26 | Zapier-based EH→Entra manager sync for Org Explorer, contractor exclusion | Superseded (Org Explorer blocked; native EH M365 sync + TeamOrgChart plan replaces it) |
| Employment Hero/EH_TeamOrgChart_Implementation_Plan_BirdLife.md | 2026-06-29 | Option 3 full automated sync: EH M365 integration + Power Automate starter/leaver flows | Current plan (implementation status unconfirmed) |
| Employment Hero/Employment_Hero_Entra_ID_Admin_Guide.md | 2026-07-02 | Scoped EH admin role (no pay access) + Entra integration setup request | Current (short-form; role grant still pending per 07-09 findings) |
| Employment Hero/Logging into Employment Hero.md | 2026-07-29 | Staff SSO login guide (EH page or M365 portal tile) | Current |
| Employment Hero/TeamOrgChart-Deployment-Guide.md | 2026-06-29 | Deploy/block/restore TeamOrgChart+ org-wide via Teams Admin Center | Current |
| Employment Hero/aPI/Employment_Hero_Entra_Sync_Findings.md | 2026-07-09 | Root cause of insufficient_scope: read-only EH app scopes locked; new app needed for writes | Current |
| Employment Hero/aPI/emphero_entra_sync_report.md | 2026-07-09 | Full technical design/build/runbook for Logic App employee ID sync, credential expiry, cleanup steps | Current — authoritative for the sync |
| Employment Hero/aPI/progress-log.md | 2026-07-09 | Session-by-session build log (architecture pivots, 403 diagnosis, outstanding items) | Current (working log) |
| Culture Amp/Culture Amp x Azure AD SSO Setup Guide.md | 2026-07-06 | SAML SSO setup: Culture Amp custom app in Entra ID, cert rotation notes | Current (how-to; execution unconfirmed) |
| Google/BirdLife Australia - Google Workspace Admin Console Review.md | 2026-07-05 | Full admin console review: identity, groups, devices, security posture, billing | Current |

---
*Cross-cutting note: the June org-chart documents treat TeamOrgChart/Entra as source of truth; all July documents treat Employment Hero as upstream source of truth for people data. Adopt the July position (EH upstream) and treat the June comparison as a point-in-time reconciliation exercise.*
