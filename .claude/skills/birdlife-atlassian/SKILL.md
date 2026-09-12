---
name: birdlife-atlassian
description: Operator knowledge for BirdLife Australia's Atlassian site (birdlife-ict.atlassian.net) — the ICT Confluence space, personal-space sprawl, what the Rovo connector can reach, and how Confluence should relate to the OneDrive knowledge base. Use for tasks involving Confluence pages, documentation, runbooks, wikis, or Jira issues. Trigger on "Confluence", "Atlassian", "Rovo", "Jira", "wiki page", "runbook", or a request to document something for the team.
---

# BirdLife Australia — Atlassian (Confluence)

## Site identity — verified live

| Fact | Value |
|---|---|
| Site | `https://birdlife-ict.atlassian.net` |
| Cloud ID | `f21ef93c-1ce4-4c99-81d1-d223f83d202f` |
| Site name | `birdlife-ict` |
| Mathew's account ID | `712020:37f78e14-9822-4123-b50b-b4e18b2b4454` |
| Granted scopes | Confluence read/write for pages, comments, spaces, search, users |

**Note the scope list carefully: there are no Jira scopes on this connection.** The Rovo connector advertises Jira tools, but this site's grant covers Confluence only. If a Jira task comes up, verify access before promising anything — the tools may exist while the permission does not.

## Spaces — verified live

| Space | Key | ID | Type |
|---|---|---|---|
| **ICT** | **`OPERATIONS`** (web alias `/spaces/ict`) | **229380** | global |
| Justin Joseph | `~71202087eb…` | 65697 | personal |
| Andrew Dunn | `~70121860b…` | 458818 | personal |
| nina.lewis | `~712020228…` | 459061 | personal |
| keith.tsui | `~712020771…` | 459304 | personal |
| mathew.hema | `~712020 37f…` | 14909451 | personal |
| Thomas.Anthony | `~712020e42…` | 44138507 | personal |
| melvin.kurian | `~712020bb7…` | 44171275 | personal |

**One global space and seven personal spaces.** That ratio is the finding. Two of the personal-space holders are external or departed contacts (Thomas Anthony holds a stale Salesforce admin account; Melvin Kurian is Envision CP). Personal spaces belonging to people who have left are a documentation-loss and access-review item, not a housekeeping detail.

The ICT space key is `OPERATIONS` but the display name is `ICT` and the URL alias is `ict`. All three appear in different places. Use the key `OPERATIONS` for API calls, `ict` for links.

## The documentation problem worth naming

BirdLife's real ICT knowledge base is **not** in Confluence. It is a set of markdown digests in the repository (`.claude/skills/birdlife-core/references/knowledge/`, ADR 0021) with document copies in Mathew's Google Drive (`Birdlife\Claude\KnowledgeBase\`) plus ~116 Word documents. Confluence has one populated global space.

That split means:
- Documentation is only discoverable by people who have the repository or know the Google Drive folder exists.
- There is no page history, no comments, no ownership metadata, no permissions model on the authoritative content.
- The two corrupted source files (Arun Nair's DocGen LWC spec and the Developer Onboarding System Audit) had **no second copy**, and their content is now unrecoverable. Confluence would have prevented that.

If asked where a runbook should live, the honest answer is Confluence for anything the team needs to find and version, OneDrive only for working drafts and generated artefacts. Do not add to the sprawl by creating a third location.

## Available tooling

`mcp__Atlassian_Rovo__*` gives full Confluence page CRUD (`createConfluencePage`, `updateConfluencePage`, `getConfluencePage`, descendants, footer and inline comments), CQL search, and the Teamwork Graph tools.

Use `getTeamworkGraphContext` when reasoning about relationships between entities (work items, people, goals). Do **not** use Teamwork Graph tools for plain CRUD.

Jira, Compass and their tools appear in the toolset but are not covered by this site's grant. Verify before use.

## Operating rules
1. **Write to the ICT space (`OPERATIONS`), not to a personal space**, unless explicitly asked otherwise. Content in a personal space disappears when the person leaves.
2. Search with CQL before creating a page. There is enough duplication in this environment already.
3. Anything containing per-user security-weakness detail (who lacks MFA, elevated user lists) is CONFIDENTIAL and needs space permissions checked before it is published, not after.
4. If a Jira request arrives, confirm the scope grant first rather than failing halfway through.
