# Index: what is known where

One line per file. Read this when you do not know which file holds something.
`grep -ri "<term>" .claude/skills memory os docs` is the fallback. Updated in
the same commit as any file added, moved or retired.

## Kernel

| File | Holds |
|---|---|
| `CLAUDE.md` | The charter: identity, operating rules, the session close rule, the skill table |
| `INDEX.md` | This map |

## Long-term memory: skills (`.claude/skills/`)

Each skill is `SKILL.md` (doctrine, prose) plus `references/` (lookup values).
Facts file first, prose second, when a value changes.

| Skill | SKILL.md holds | references/ holds |
|---|---|---|
| `birdlife-core` | The doctrine: precedence order, four fact classes, write tiers, where a new fact goes, blind spots (Aug 2026, integrated 12 Sep) | `decisions/`: ADRs 0001 to 0020 (0017 missing, 0019 twice); `verification-queries.md`: the query behind every volatile figure (8 Aug baselines); `fact-classification.md`: worked examples; `knowledge/`: six Aug 2026 digests (salesforce, security, people-systems, finance-infra-web, volunteer-membership-events, master index) |
| `birdlife-manager` | Weekly ICT manager review: scorecard, one learning, delegations, decisions needed (IT-GOV-003) | |
| `birdlife-atlassian`, `birdlife-canva`, `birdlife-granola`, `birdlife-miro`, `birdlife-microsoft-learn`, `birdlife-gmail`, `birdlife-google-calendar` | One small skill per connector: what it reaches, what it is for, the boundary (Aug 2026) | |
| `birdlife-ict-assistant` | Case and Asana workflow, tiers, guardrails, owner resolution | `reference.md`: Case statuses, close reasons, Type values, Asana IDs, write mechanics, Tier 2 playbooks, institutional memory |
| `birdlife-salesforce` | The Zeus org: packages, integrations, landmines, query discipline | `facts.md`: URLs, record types, user IDs, namespaces, fields, integration constants, staging differences |
| `birdlife-asana` | Board semantics, the SPF blocker, hygiene governance | `facts.md`: workspace, project and section gids, team gids, API shapes, thresholds |
| `birdlife-microsoft365` | Entra, CA, MFA, Intune, Defender, EH sync, connector behaviour | `facts.md`: tenant IDs, CA policies, admin accounts, remediation population, Logic App components, dates |
| `birdlife-netsuite` | ERP model, controls, reconciliation, SuiteQL cookbook, BC advisory | `facts.md`: account, GL codes, roles, reconciliation figures, certificate record |
| `birdlife-wordpress` | WP Engine estate, privilege flaw, membership rebuild, incidents | `facts.md`: environments, connector abilities, health numbers, tiers, mappings, cart-flood rule |
| `birdlife-stripe` | Money chain, refund gap, migration constraints, playbook | `facts.md`: five account IDs, connector mechanics, constants |
| `birdlife-zapier` | When Zapier versus native, the exception report, the runbook | `facts.md`: connected apps, Zap 371228125 steps, other automations |
| `birdlife-cloudflare` | What the MCP cannot do, email authentication runbook, edge controls | `facts.md`: account IDs, deployed surfaces, SPF/DMARC findings |
| `birdlife-wpengine` | WP Engine User Portal, five caching layers, Web Rules, SSH/WP-CLI/GitPush/API, the seven environments, review playbook | |
| `google-workspace-expert` | Google Workspace admin model, tenant C01muaswh verified configuration, decision rules | |
| `birdlife-payments2us` | Payments2Us licence deadline, automation stack (triggers, 13 Flows, 9 DLRS rollups), direct debit internals, defects | |
| `birdlife-conga` | 17 Conga batches, query and template inventory, Composer grammar, defects, S-Docs scope (verified 10 Sep 2026) | |
| `birdlife-sdocs` | S-Docs and S-Sign configuration; installed in neither org as at 10 Sep 2026 | |
| `birdlife-movedata` | MoveData pipeline model, extension Flow authoring, live Zeus config, eight defects, error catalogue (verified 11 Sep 2026) | |
| `birdlife-powerbi` | Power BI and Fabric backlog, Zeus data-model traps, Copilot exposure, Fabric cost | |
| `birdlife-prompting` | The six-line prompt frame and how to route a prompt to the right skill | |
| `birdlife-security` | Posture by system, SC-300 identity baseline, P1 versus P2, deadline register, identity playbooks, incident playbooks (CONFIDENTIAL) | (deadline register is in the SKILL.md table) |
| `birdlife-people-lifecycle` | Joiner, mover, leaver in order with the Tier 2 scripts, credential sweep | |
| `birdlife-reporting` | Report library, data discipline, skeletons, production path | |
| `birdlife-improvement` | Observe, propose, decide, track, verify, learn; the fix format; the Fixes tab | |
| `email-voice` | Mathew's three registers, sign-offs, phrasing | `samples.md`: verbatim sent-mail excerpts |
| `morning` | Mathew's personal morning brief (HTML artifact, optional weekday routine) | `assets/`: font |
| `birdlife-os` | Managing Claude itself: console, the lens model (IT Admin live), weekly audit, routine lifecycle, skill estate | |

## Episodic memory (`memory/`)

| File | Holds |
|---|---|
| `memory/README.md` | Who writes, the entry formats, the rules (no credentials, no PII) |
| `memory/journal/YYYY-MM-DD.md` | Per day: decisions (by whom, why), done, learned, open. Backfilled from 7 Aug 2026 |
| `memory/patterns/salesforce.md` | Resolved Zeus problems: symptom, cause, fix, verify |
| `memory/patterns/website.md` | Resolved WordPress, WooCommerce, WP Engine, email-auth problems |
| `memory/patterns/claude-estate.md` | Resolved routine, console and skill problems |

## State of record (`os/`)

| File | Holds |
|---|---|
| `os/README.md` | The Claude operating system: estate model, rules, cadence, change control, incidents |
| `os/registers.md` | Routine register (trigger IDs, schedules, retirements), skill register, connector register, artefact register (URLs), credential watchlist, memory register |
| `os/lenses.md` | IT-GOV-004 lens model: five lenses, the IT Admin capability matrix (22 systems, verified 8 Sep 2026), findings F1 to F6 |
| `os/claude-os-overview.html` | Source of the BirdLife Australia console (Jarvis) with the Lens tab (8 Sep 2026); published artifact URL is in the artefact register |
| `os/birdlife-brain.html` | Source of The BirdLife Brain map (i, Robot style neural view of every skill, ADR, routine, system and artefact, coloured by layer; 12 Sep 2026); published artifact URL is in the artefact register. Data is baked in, rebuild after estate changes |

## Routines (`routines/`)

| File | Holds |
|---|---|
| `routines/os-weekly-audit.md` | Definition of record for the Monday OS audit routine |
| `routines/overnight-pre-draft.md` | Definition of record for the weekday 5:30am pre-draft (write-capable, capped) |
| `routines/routines-backup-*.json` | Retired routine definitions, credentials redacted |
| `routines/unused-routines-review-2026-09-03.md` | The 3 Sep review that retired two routines |

## Docs and history

| File | Holds |
|---|---|
| `README.md` | Dashboard findings, the Salesforce admin runbook (record-type filter, Type on close, MTTR), the Aug 2026 routine consolidation, credential exposure note, repo layout |
| `docs/using-the-assistant.md` | Remote access channels, the console link, prompt playbook, tiers |
| `docs/entra-admin-connector.md` | Plan to promote Tier 2 Entra/Exchange actions to approve-only execution |
| `docs/manager/` | The weekly manager reviews and the append-only learning log (IT-GOV-003), from 7 Sep 2026 |
| `docs/brain-v1/` | The August 2026 Cowork plugin's README, GOVERNANCE (the write test, roles, bus factor) and CONNECTORS, kept as history; `os/README.md` and `CLAUDE.md` supersede where they differ |
| `.github/workflows/harvest.yml` | Site harvester workflow (runs against the website-audit branch) |

## Not in the repo (and where it is)

| Thing | Where |
|---|---|
| Live routines | claude.ai Routines; IDs in `os/registers.md` |
| Connector credentials | claude.ai Settings, Connectors; never here |
| Account-synced skill copies | claude.ai account; repo wins on drift only once account content is committed (11 Sep 2026: the account was ahead) |
| Mathew's Google Drive `GoogleDrive/Claude` folder (personal account) | The human-readable layer: IT-GOV-004 and IT-GOV-005 documents, the repo-inbox (all three patches now applied), the Manager folder, the Aug 2026 plugin and repo snapshot, the 17 archived artifact exports of 3 Sep, KnowledgeBase, Skills (Aug zips). Reached through the Google Drive connector; the M365 connector cannot see it |
| Mathew's Google Drive parent folder | The IT-* document library (IT-SF-001 to 021, IT-SEC-006, IT-INT-004/005, IT-GOV-002/004 strategy), Zoom and Salesforce runbooks, dashboards, PowerShell scripts; Word and PDF documents stay there, indexed by name here |
| `salesforce-delivery-governance` skill, ADR 0017 (autonomy levels), IT-SEC-002/003/004/007, IT-WEB-001, IT-SF-018 | Cited by skills and ADRs; not found in the repo, the account, the plugin or Google Drive search on 12 Sep 2026 |
| Dashboards and console | artifact URLs in `os/registers.md`; Teams copies on SharePoint |
| June 2026 security reviews, July NetSuite review, WordPress health check | SharePoint documents, not yet ingested (open item, journal 11 Sep 2026) |
