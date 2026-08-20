# BirdLife Digital Ecosystem — Integration Map & Deepening Plan

Surveyed live on **20 August 2026** from the connected Claude workspace. This is the
companion to `README.md`: that file covers the ICT dashboard; this one covers what
Claude can currently see across the whole estate, where the blind spots are, and the
ordered list of moves that buy the most context for the least effort.

---

## 1. What is connected today

### Native Claude connectors — 16, all authenticated and enabled

| System | What Claude can reach | Depth notes |
|---|---|---|
| **Salesforce Production** (Zeus) | SOQL, record CRUD, object schemas, related records | No report/dashboard metadata — report fixes stay manual (see README) |
| **NetSuite** | SuiteQL, saved searches, reports, record read/write, subsidiaries | Full analytical depth on the GL side |
| **Stripe** | Account info, API read/write, analytics, docs | eCommerce live account |
| **Microsoft 365** | Outlook mail/calendar, SharePoint, OneDrive, Teams chat search | Collaboration layer only — **not** Entra ID directory admin |
| **Gmail / Google Calendar / Google Drive** | Personal Google workspace | Secondary to M365 |
| **Asana** | Tasks, projects, portfolios, comments, search | IT Operations Project Plan lives here |
| **Atlassian Rovo** | Jira, Confluence, Compass, Teamwork Graph | |
| **Cloudflare Developer Platform** | Workers, R2, D1, KV on both accounts (Domain.admin + Mathew.hema) | CDN/DNS/WAF controls are dashboard-only, not in this MCP |
| **Zoom / Granola** | Meeting recordings, transcripts, AI notes | Meeting context both sides |
| **Miro / Canva** | Boards, designs, exports | |
| **Microsoft Learn** | Docs search | Reference only |
| **GitHub** | Scoped to `mathewruahema-beep/birdlife` | Via MCP tools, no `gh` CLI |
| **Zapier** | Bridge to everything below | |

### Zapier-bridged apps — 18 enabled

The reach into systems with no native connector. Connected and working:

| App | Why it matters | Connection |
|---|---|---|
| **Raisely** | Fundraising campaigns → MoveData → Salesforce | BirdLife Australia |
| **Ortto** | Marketing automation (Pardot's replacement) | birdlife |
| **Campaign Monitor** | Email campaigns | org account |
| **Humanitix** | Event ticketing | mathew.hema |
| **Google Analytics 4** | Web analytics, 2 accounts | mathew.hema.admin |
| **LearnUpon** | LMS (volunteer/staff training) | 1 connection |
| **Award Force** | Awards/grants management (33 actions) | 1 connection |
| **Content Workflow (Bynder)** | Content production pipeline | 1 connection |
| **BugHerd** | Website feedback/QA | 1 connection |
| **Pardot** | Legacy — being decommissioned for Ortto | 2 connections |
| **Storage by Zapier** | Key-value state between Zaps | 1 connection |
| Excel, Teams, Outlook, Salesforce, Asana | Duplicates of native connectors — kept for Zaps; prefer native MCP in sessions | many |
| Webhooks by Zapier, Zapier Manager | Plumbing (LearnUpon catch-hook lives here) | — |

### The context layer — 10 `birdlife-*` skills

Operator knowledge for Salesforce, NetSuite, M365/Entra, WordPress, Stripe, Asana,
Zapier, Cloudflare, the ICT assistant, and the morning brief. These are what turn raw
connector access into situated answers. **They are only as good as their last update**
— when any recommendation below lands (e.g. WooCommerce access changes), the matching
skill needs the same edit.

---

## 2. The blind spots, ranked by cost of not seeing

### 🥇 WordPress / WooCommerce — the biggest one

`birdlife.org.au` runs memberships, donations and the shop; orders flow through
WooCommerce → miniOrange → Salesforce and on to NetSuite. **Claude currently has no
read access at any point in that chain's origin.** Every payment-reconciliation,
membership or order question starts blind.

History makes this worse: the deleted dashboard routines embedded live WooCommerce
API keys in plaintext prompts (see README §credential exposure). Rotation is still
outstanding — which means the current keys must be treated as burned.

Options, in order of preference:

1. **Direct REST with env-var credentials — built, awaiting setup.** The client
   (`woocommerce/wc.py`), runbook (`woocommerce/README.md`) and project skill
   (`.claude/skills/birdlife-woocommerce/`) are in this repo. Three user steps
   remain: rotate the burned keys, set `WOO_CK`/`WOO_CS` env vars, and allow
   `birdlife.org.au` on the environment's network policy — **verified blocked
   (CONNECT 403) on 20 Aug 2026**, so the allowlist step is mandatory.
2. **Zapier WooCommerce app.** Exists (11 read / 17 write / 9 search actions) but
   requires the **paid WooCommerce Zapier extension plugin** installed on the site —
   a licence purchase and a Blitzm/WP admin task. Worth it only if Zaps need
   Woo triggers anyway.
3. **WordPress.com MCP connector** — *not applicable*: it only manages
   WordPress.com-hosted sites, and birdlife.org.au is self-hosted on WP Engine.

### 🥈 Employment Hero — HR source of truth, zero visibility

Onboarding/offboarding is 20% of ICT case volume (README §what the data says), and
Employment Hero drives the Entra sync — yet Claude cannot see starters, leavers or
org structure. Zapier has an **Employment Hero Payroll** app with 3 read-only
actions. Low risk, read-only, one authentication in the Zapier UI. This directly
feeds the identity-lifecycle automation the case data is begging for.

### 🥉 Routine connector grants — already-built integration doing nothing

The weekday dashboard routine (`trig_0126KYAM3TAaZpBQKN8UeVdk`) still has **no
connectors attached** — the org doesn't permit attaching them via API, so it fires
and reads nothing. Two minutes in claude.ai → Routines → attach **Salesforce
Production** and **Asana**. This is the single highest ratio of context-gained to
effort on this page.

### Entra ID directory administration

The M365 connector reads mail, files and Teams but not directory admin: MFA state,
Conditional Access, licences, group membership. The `birdlife-ict-assistant` skill
already documents this boundary. Closing it means an Entra admin consent for a Graph
integration — a deliberate security decision to take to the ICT Steering Group, not
a quick win. Until then, directory tasks remain "draft the change, human executes".

### WP Engine platform

Deploys, backups, staging copies (`birdlifestage`) are dashboard/SSH only. WP Engine
has an API, but there is no MCP connector and the volume of tasks is low. Accept the
gap; revisit if the membership rebuild increases release cadence.

### Housekeeping that sharpens context

- **Pardot (Zapier)** — decommission target. Once the Ortto migration completes,
  disable its 12 Zapier actions and archive the 2 connections: fewer stale surfaces,
  less chance of writing to a dead system.
- **Duplicate connections** — 9 Excel, 8 Outlook, 3 Teams, 3 Salesforce connections
  in Zapier. Worth a pass in the Zapier UI to name/prune them so actions run against
  the intended account.
- **`ICT Priorities.xlsx`** — the Asana↔Zeus join is still a hand-typed spreadsheet
  column with ≥4 divergent copies. The dashboard supersedes it; consolidate to one
  copy or retire it.

### Noted, not urgent

- **GoCardless MCP** exists in the registry (BECS direct debit). If Stripe's BECS
  constraints bite during the membership migration, a purpose-built DD provider with
  an MCP connector is an option to weigh — a payments-architecture decision, not an
  integration one.

---

## 3. The plan, in order

| # | Action | Effort | Who/where | Context gained |
|---|---|---|---|---|
| 1 | Attach Salesforce + Asana connectors to the dashboard routine | 2 min | claude.ai UI (manual, one-time) | Dashboard actually refreshes with live data |
| 2 | Rotate WooCommerce API keys (new key: **Read** permission) | 15 min | WP admin → WooCommerce → REST API | Closes an open credential exposure |
| 3 | Set `WOO_CK`/`WOO_CS` env vars + allow `birdlife.org.au` egress; then un-park the order-sync check | 30 min | Claude Code environment settings (vars + network) | Order flow visible end-to-end via `woocommerce/wc.py` |
| 4 | Connect Employment Hero Payroll in Zapier (read-only) | 10 min | Zapier UI authentication | Starters/leavers visible; feeds onboarding automation |
| 5 | Decide: Zapier WooCommerce extension — buy or skip | decision | ICT + Blitzm | Woo triggers for Zaps (only if needed beyond #3) |
| 6 | Post-Ortto-cutover: disable Pardot Zapier actions | 10 min | Zapier | Removes a stale write surface |
| 7 | Prune duplicate Zapier connections | 20 min | Zapier UI | Actions hit the right account |
| 8 | Take Entra/Graph admin access proposal to ICT Steering Group | meeting | governance | Unlocks directory-level automation |
| 9 | Update `birdlife-wordpress` / `birdlife-zapier` skills after #3–5 land | 15 min | skill edits | Keeps the context layer truthful |

Items 1–4 are a single afternoon and close the two loudest gaps (payments-origin
visibility and identity lifecycle) plus one security debt. Everything after is
governance-paced.
