# IT-GOV-004: BirdLife OS lens model, IT Admin lens first

Owner: Mathew Hema, Senior Manager ICT. Date: 8 September 2026. Status: Live (IT Admin lens), Stub (four others).
Human copy: GoogleDrive\Claude\IT-GOV-004_BirdLife_OS_Lens_Model.md in Mathew's personal Google Drive (ADR 0021; the OneDrive path in the 8 Sep original was the same folder seen through OneDrive sync). This file (os/lenses.md) is the repo record.

## 1. What a lens is

The BirdLife OS is the existing Claude estate (birdlife-os skill, the BirdLife Australia console with Jarvis, the routines, the skills, the registers). A lens is a persona laid over that estate. It fixes five things before any question is asked:

| Element | Meaning |
|---|---|
| Who | The role the session or the console is acting as |
| Systems | Which connectors the lens reaches and in what order it looks |
| Authority | The write tier per action (1 execute after approval, 2 prepare for a named runner, 3 design only) |
| Questions | The standing questions the lens answers first |
| Outputs | The reports and records it produces, and where they land |

A lens never raises authority above what the connector and the ADRs allow. It can only narrow it. The tiers come from birdlife-core rule 3 and the approve-then-write charter; the lens says which tier applies to which action in which system, verified live, so nobody has to guess.

## 2. The five lenses

| Lens | Status | Who | Primary systems | Standing question | Outputs |
|---|---|---|---|---|---|
| IT Admin | Live 8 Sep 2026 | Mathew acting as administrator of every connected system | All 20 probed below | What can I do in each system right now, at what tier, and what proves it worked | Capability matrix (section 3), one admin action per system with its DONE test, delegation candidates for IT-SEC-002 |
| Security | Stub | Mathew as security owner, Essential Eight anchor | Entra, Salesforce, WordPress, Cloudflare, Stripe, Zapier | What is overdue, who holds privilege, what changed | Security tab, Sunday security dashboard, deadline register, incident playbooks (birdlife-security) |
| Finance link | Stub | Nina Lewis with Mathew, the bridge to Finance | Salesforce, Stripe, NetSuite, Zapier | Do the three money systems agree, and where is the gap | Money tab, money state report, reconciliation pack (birdlife-netsuite, birdlife-reconciliation) |
| Manager | Stub | Mathew as manager of the team of four | Salesforce Zeus queue, Asana, routines, deadline register | What moved, what stalled, what I delegate this week, one learning | Weekly manager review, learning log, delegation ladder under IT-SEC-002 (birdlife-manager, IT-GOV-003) |
| Board and Exec | Stub | Mathew reporting to Kate Millar, the CFO, the ISG and the Board | Read only over everything | What does the CEO or Board need to decide, in five sentences | Exec brief, Board paper on the Board Paper template, ISG deck (birdlife-reporting) |

Stub means: named, owned, wired to the skills that already carry the knowledge, not yet given its own live matrix or console behaviour. Each stub gets built the same way the IT Admin lens was: probe live, write the matrix, prove one action, record.

## 3. IT Admin lens: the capability matrix, verified live 8 September 2026 (9:30am AEST)

Every row was probed with one call this session. "Reached" means the connector answered with real data under Mathew's identity. Write columns state what the tool surface exposes and what the record allows. A tool that exists is not authority to use it; the tier column is the rule.

| System | Connector | Reached | Identity observed | Read | Write surface exposed | Tier and rule | Proof query (DONE test) |
|---|---|---|---|---|---|---|---|
| Salesforce Production (Zeus) | Salesforce Production | Yes | Mathew Hema, System Administrator profile, user 005RF000003ahkfYAA | SOQL, schema, related records | create, update, delete on any sObject | Tier 1 for data, one record per approval, internal audit CaseComment on Case writes, never bulk, never delete without a Case. Tier 3 for configuration (no Metadata API on this connector) | Re-read the record by Id after the write |
| Salesforce Staging | Salesforce Staging | Yes | Same user, username suffixed .staging | Same | Same | Tier 1, experiments go here first. Note: staging was refreshed from Production shortly before 30 Aug, so it is a copy of prod data | Same |
| Salesforce Sandbox (bridge) | Salesforce-Sandbox on the desktop | Present, not probed | Not observed | SOQL only | None | Tier 1 read. Overlaps Salesforce Staging; candidate for the connector review | run_soql_query returns rows |
| Microsoft 365 (user level) | Microsoft 365 | Yes | mathew.hema@birdlife.org.au, Senior Manager ICT | Mail, calendar, Teams read, SharePoint, people search | Send mail, drafts, calendar events, SharePoint upload, Teams chat send | Tier 1 for Mathew's own mailbox and calendar. Console never sends; sessions send only after showing the draft. No admin surface here | Message id or event id returned and re-read |
| Microsoft Entra ID (admin) | entra-admin-cloud on the desktop bridge | Yes, read proven | Graph answered for mathew.hema@birdlife.org.au with licences and department | get_user, auth methods, licence SKUs, offboarding status, employee id coverage | create_user, enable and disable account, set licences, set manager, add and remove group member, revoke sessions, temporary access pass, delete auth method | Tier 2 today by ADR 0002. Tier 1 with approval card is PROPOSED in ADR 0019 for four actions only (disable, revoke sessions, licence removal, group removal) once one write is proven with rollback. create_user and temporary access pass stay Tier 2 with a Case number. Mail-enabled group removal still needs Exchange PowerShell (IT-SEC-004) | get_user re-read shows accountEnabled and assignedLicenses as expected |
| Azure subscription | Azure MCP Server on the desktop bridge | Yes | Subscription BirdLife Australia Azure f0b2d7cf, tenant 2b431a7b, default | Resource groups, Key Vault, Logic Apps, Container Apps, monitor, RBAC | Full ARM surface through the tool set | Tier 2. Mathew's admin identity holds Owner (ADR 0009). No session writes to Azure without a change record; Logic App and Container App changes are prepared as az commands | group_list and the specific resource read after the change |
| Asana | Asana | Yes | Mathew Hema, workspace 443963187362944 | Projects, tasks, stories, portfolios | Create and update tasks, comments, projects, status updates, delete task | Tier 1, one task per approval, section moves by add_projects, never delete | update_tasks reports succeeded, then search_tasks re-read |
| NetSuite OneWorld | NetSuite | Yes | Subsidiary 2 Birdlife Australia, parent context -1 | SuiteQL, saved searches, reports, record get | createRecord, updateRecord exist | Tier 1 read only. Writes are Tier 3 by doctrine (ledger). Never create saved searches (skill rule). Always filter subsidiary id 2 | SuiteQL count before and after |
| Stripe (five livemode accounts) | Stripe | Yes | Ausbirdfund, BLP, eCommerce, eStore/AOC, Memberships, all livemode true | Balances, charges, refunds, payouts, subscriptions via stripe_api_read | stripe_api_write exists | Tier 3 for anything that moves money. stripe_api_write is never declared on the console and never used from a session without a written Case and Mathew in the room | stripe_api_read of the object after the change |
| WordPress UAT (WooCommerce) | BirdLife_UAT_WordPress | Yes | 11 abilities on the UAT site | orders-query, products-query, gift cards, bundles, Yoast scores | order-add-note, order-update-status, product create, update, delete | Tier 1 on UAT only. Production WordPress has no connector; production changes are Tier 2 through wp-admin by Mathew, or Tier 3 for plugin work (Blitzm) | orders-query or products-query re-read |
| Cloudflare | Cloudflare Developer Platform | Yes | Two accounts: Domain.admin 3bd8acff, Mathew.hema 9bff172b; zero Workers in the Domain.admin account | Workers, KV, R2, D1, Hyperdrive, docs | Create and delete of those developer objects | Tier 2 for anything in front of the website. This connector does NOT reach DNS, WAF, rate limiting or cache; those are dashboard changes prepared as exact click-paths with rollback (birdlife-cloudflare) | Dashboard screenshot or dig for DNS; workers_list for Workers |
| Zapier | Zapier | Yes | Teams connections: mathew.hema.admin (Aug 2026), mathew.hema (Aug 2026), and a 2024 connection under the shared admin365.ross@BirdLifeAustralia.onmicrosoft.com login, last refreshed Jul 2024 | Connections, actions, skills, read actions | Write actions on any connected app, code actions, Teams channel post (the standing route for Teams posting) | Tier 1 for Teams posts to the ICT Monitoring team and for read actions. Tier 2 for enabling new write actions. FINDING: the admin365.ross connection is a shared credential from 2024 and belongs on the credential watchlist for removal | The Zapier action result plus a read of the target system |
| Raisely | Raisely | Reached, identity not exposed | get_authenticate returned an empty data object; the token is app scope "mcp", so it carries no user or admin fields | Campaigns, donations, users, profiles, subscriptions | Campaign create and update, interactions, tags, media | Tier 1 read. Writes Tier 2 until the token's privilege is confirmed in the Raisely admin UI. Organisation and webhook endpoints answer 403 (verified 7 Sep) | list_campaigns count and the specific campaign re-read |
| Ortto | Ortto | Yes | Instance birdlife; knowledge base index empty | Campaigns, journeys, audiences, contacts, reports, assets | Create and update email and SMS assets, articles, categories | Tier 1 read. Writes Tier 2 to Marketing's named owner; ICT does not author campaigns | get_asset_html re-read |
| Atlassian (Confluence, Jira) | Atlassian Rovo | Yes | Mathew Hema, account 712020:37f78e14, site birdlife-ict | Pages, spaces, issues, Teamwork Graph | Create and update pages, comments, Jira issues and transitions | Tier 1 in the ICT space. Confluence is not the knowledge base of record (the repo is, ADR 0004); pages are published copies | getConfluencePage re-read |
| Canva | Canva | Yes | Brand kits: BirdLife Australia flagship brand kit kAFMW4XTNVg, OnTrack, Nature laws and Threatened Bird Images | Designs, folders, brand templates, assets | Generate, edit, export, comment, publish brand template | Tier 1 for ICT collateral from the flagship kit. Brand template publish is Tier 2 to Marketing | read-design after the change |
| Miro | Miro | Yes | User 3458764665396343632, team 3458764569241611978, org 3458764569241611977 | Boards, canvases, docs, tables | Board create, share, roles, canvas and diagram create and update | Tier 1 for ICT boards; sharing outside the team is Tier 2 | board_list_items re-read |
| Zoom | Zoom for Claude | Yes | Search schema returned for zoom_meeting | Meetings, recordings, transcripts, chat, canvas, notes | Meeting create, update, delete, in-meeting control, canvas files | Tier 1 for Mathew's own meetings. Zoom admin (SSO, SCIM, app cleanup) has no connector: Tier 2 per IT-INT-003 | search_meetings re-read |
| Granola | Granola | Yes | mathew.hema@birdlife.org.au, workspace Birdlife, scopes personal and public | Meetings, transcripts, folders | None | Tier 1 read. Meeting content stays in the session; nothing pasted into tickets without the participants' knowledge | n/a, read only |
| AWS (Birdata) | AWS API MCP Server on the desktop bridge | Present, NOT reached | "No AWS credentials found" on the bridge | None until configured | Full CLI surface once configured | Not usable. FINDING: the AWS bridge has no credential profile; the EKS extended support fees and the root MFA gap cannot be checked from here. Fix: an aws configure on h20blacks with a least-privilege IAM user, then re-probe | sts get-caller-identity returns the account and ARN |
| GitHub | None in this session | NOT connected | On the approved connector list (project instructions), absent from the tool list | None | None | The repo is the source of truth (ADR 0005) and this session cannot commit to it. Patches go to OneDrive Birdlife\Claude\repo-inbox for Mathew to apply | git log after apply |
| Google Workspace (Drive, Gmail, Calendar) | Google Drive, Gmail, Google Calendar | Present, not probed | Personal account mathew.rua.hema@gmail.com (ADR 0006 exception E1) | Files, mail, events | Files, mail, events | Tier 1 for the personal Birdlife working folder only. Not BirdLife identity; no BirdLife Workspace admin reach (348 users without 2SV and the expired SAML cert stay Tier 2 in the Google admin console) | n/a |
| Microsoft Learn | Microsoft Learn | Present | Public documentation | Docs, code samples | None | Reference only; use before any Graph, PowerShell or Conditional Access work | n/a |
| Claude estate itself | claude-code-remote (routines), Artifact, skills | Yes | This account | Triggers, artefacts, skills | Create, update, delete triggers; publish artefacts | Tier 1 under the birdlife-os change control: passport first, budget 12 of 12, backup before retire, register row same session | list_triggers and the register row |

Twenty-three rows here; the console carries 22 (the Salesforce Sandbox bridge and Microsoft Learn are folded into notes). Answered live this session: 19. Usable: those 19 plus the personal Google folder (present, not probed) = 20. Not usable: AWS (no credential) and GitHub (absent). Not probed: Salesforce Sandbox bridge (overlaps Staging).

## 4. What the IT Admin lens changes in practice

1. Every session that opens with "act as IT Admin" reads this matrix before touching a system, states the tier out loud for the action in hand, and refuses to go quiet on a Tier 2 action.
2. The console gets a Lens tab. The active lens is remembered per browser and prepended to every Jarvis turn as ACTIVE LENS, so Jarvis answers from that persona and applies that authority table. The IT Admin lens carries the matrix in the page; the four stubs carry their owner, systems and the skill that will build them.
3. Delegation is read off the same table. A row where the tier is 1 and the blast radius is one record (Asana tasks, Salesforce Case comments and assignment inside the Zeus group, WordPress UAT order notes, Confluence pages in the ICT space) is a candidate first rung for Andrew Dunn under IT-SEC-002. Rows with money, identity or production website stay with Mathew until the ladder says otherwise.

## 5. Findings from the probe that need a decision or an action

| # | Finding | Impact on people | Proposed action | Owner |
|---|---|---|---|---|
| F1 | The Entra admin write connector is live on the bridge and answers Graph reads. ADR 0002 still describes it as pending consent | Andrew and Keith are told Entra work is prepare-only while the session can now, in principle, disable an account. The gap between the record and reality is the risk | ADR 0019 (Proposed): keep Tier 2 until one reversible write is proven under an approval card; then promote four actions to Tier 1 with approval; create_user and TAP stay Tier 2 with a Case | Mathew |
| F2 | Zapier holds a Microsoft Teams connection under the shared admin365.ross@BirdLifeAustralia.onmicrosoft.com login, created May 2024, last refreshed Jul 2024 | A shared admin credential nobody owns is still authorised to post as BirdLife in Teams | Confirm nothing uses it (Zap history), remove it, add to the credential watchlist until removed. Ties to the fix "Retire the two shared .onmicrosoft.com Global Admin accounts" | Mathew |
| F3 | AWS bridge has no credentials | The EKS extended support fees, the root MFA gap and the Birdata middleware cannot be checked from any Claude session | Configure a least-privilege IAM user profile on h20blacks; re-probe; then the Birdata checks join the daily feed monitor | Mathew |
| F4 | GitHub is on the approved list but not connected here; patches queue in repo-inbox | Skill and register changes wait on a manual git am, so the account skills and the repo drift between sessions | Either connect GitHub to Cowork or accept the repo-inbox pattern formally in birdlife-os (currently it is practice, not rule) | Mathew |
| F5 | Raisely token exposes no identity | Nobody can say from a session what privilege the Raisely MCP token carries | Check the app token's scope in Raisely admin; record it in birdlife-zapier or a Raisely note; until then Raisely writes are Tier 2 | Mathew |
| F6 | Three overlapping Salesforce read paths (Production, Staging, Sandbox bridge) | Confusion about which org a figure came from; the staging refresh already invalidated "staging only" facts once | Name the org in every figure; review the Sandbox bridge at the Monday audit as a disconnect candidate | Mathew |

## 6. People

Andrew Dunn: the IT Admin lens is the map of what he will be given first (Asana, Zeus Case comments and assignment, WordPress UAT notes). Nothing changes for him today; the next IT-SEC-002 step names the rung and its DONE test.
Keith Tsui: Salesforce Staging is his experiment space under this lens; production data writes stay one record per approval with Mathew. He owns the fix list items already assigned to him (test accounts, auto-forwarding, Intune) as Tier 2 runners.
Nina Lewis: the Finance link lens is hers when built; today the Money tab is the working surface. Her Salesforce reports are unaffected.
Karishma Soni: contractor track, read only through the lens; her deploys go through Mathew's approval as they do now (26 Aug refund sync change is the precedent).
Staff and supporters: no change today. The lens exists so that when Entra writes are promoted, a disabled account or a stripped licence is a deliberate, approved, reversible act with a named approver, not a silent side effect.

## 7. Done test for this document

One admin action per reached system executed or prepared through the lens with its proof query, in one session, is the test of the lens itself. This document delivers the matrix and the proofs of reach (19 of 23 rows answered live). The write proofs run one at a time on request behind approval cards; Entra's first write is the gate in ADR 0019.
