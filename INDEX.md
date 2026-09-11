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
| `birdlife-ict-assistant` | Case and Asana workflow, tiers, guardrails, owner resolution | `reference.md`: Case statuses, close reasons, Type values, Asana IDs, write mechanics, Tier 2 playbooks, institutional memory |
| `birdlife-salesforce` | The Zeus org: packages, integrations, landmines, query discipline | `facts.md`: URLs, record types, user IDs, namespaces, fields, integration constants, staging differences |
| `birdlife-asana` | Board semantics, the SPF blocker, hygiene governance | `facts.md`: workspace, project and section gids, team gids, API shapes, thresholds |
| `birdlife-microsoft365` | Entra, CA, MFA, Intune, Defender, EH sync, connector behaviour | `facts.md`: tenant IDs, CA policies, admin accounts, remediation population, Logic App components, dates |
| `birdlife-netsuite` | ERP model, controls, reconciliation, SuiteQL cookbook, BC advisory | `facts.md`: account, GL codes, roles, reconciliation figures, certificate record |
| `birdlife-wordpress` | WP Engine estate, privilege flaw, membership rebuild, incidents | `facts.md`: environments, connector abilities, health numbers, tiers, mappings, cart-flood rule |
| `birdlife-stripe` | Money chain, refund gap, migration constraints, playbook | `facts.md`: five account IDs, connector mechanics, constants |
| `birdlife-zapier` | When Zapier versus native, the exception report, the runbook | `facts.md`: connected apps, Zap 371228125 steps, other automations |
| `birdlife-cloudflare` | What the MCP cannot do, email authentication runbook, edge controls | `facts.md`: account IDs, deployed surfaces, SPF/DMARC findings |
| `birdlife-security` | Posture by system, deadline register, ratios, incident playbooks (CONFIDENTIAL) | (deadline register is in the SKILL.md table) |
| `birdlife-people-lifecycle` | Joiner, mover, leaver in order with the Tier 2 scripts, credential sweep | |
| `birdlife-reporting` | Report library, data discipline, skeletons, production path | |
| `birdlife-improvement` | Observe, propose, decide, track, verify, learn; the fix format; the Fixes tab | |
| `email-voice` | Mathew's three registers, sign-offs, phrasing | `samples.md`: verbatim sent-mail excerpts |
| `birdlife-os` | Managing Claude itself: console, weekly audit, routine lifecycle, skill estate | |

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
| `os/claude-os-overview.html` | Source of the BirdLife Australia console (Jarvis); published artifact URL is in the artefact register |

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
| `.github/workflows/harvest.yml` | Site harvester workflow (runs against the website-audit branch) |

## Not in the repo (and where it is)

| Thing | Where |
|---|---|
| Live routines | claude.ai Routines; IDs in `os/registers.md` |
| Connector credentials | claude.ai Settings, Connectors; never here |
| Account-synced skill copies | claude.ai account; repo wins on drift |
| Dashboards and console | artifact URLs in `os/registers.md`; Teams copies on SharePoint |
| June 2026 security reviews, July NetSuite review, WordPress health check | SharePoint documents, not yet ingested (open item, journal 11 Sep 2026) |
