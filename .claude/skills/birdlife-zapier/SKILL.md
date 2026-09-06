---
name: birdlife-zapier
description: Operator knowledge for BirdLife Australia's Zapier account — the 17 connected apps and their credentials, the unpublished unreconciled-income exception report, the LearnUpon catch-hook, and when Zapier is the right tool versus a native connector. Use for any task about Zaps, automation between SaaS apps, scheduled data pulls, webhooks, or connecting a system with no native MCP. Trigger on "Zapier", "Zap", "catch hook", "webhook automation", "connect X to Y", "Raisely", "Ortto", "Campaign Monitor", "Humanitix", "Award Force", "LearnUpon", or "Content Workflow".
---

# BirdLife Australia — Zapier

Zapier is BirdLife's integration layer of last resort. It reaches systems that have no native MCP connector: **Raisely, Ortto, Campaign Monitor, Humanitix, Award Force, LearnUpon, BugHerd, Content Workflow (Bynder), Google Analytics 4**. That is its real value here. For Salesforce, Asana, Outlook, Teams and Excel it duplicates a native connector, and duplication is a governance cost.

## Connected apps — verified live

| App | Actions | Connections | Named connection |
|---|---|---|---|
| **Salesforce** | 41 | 3 | — |
| **Asana** | 41 | 1 | — |
| Microsoft Outlook | 44 | 8 | — |
| Award Force | 33 | 1 | — |
| Microsoft Teams | 30 | 3 | — |
| Content Workflow (Bynder) | 24 | 1 | — |
| Microsoft Excel | 22 | 9 | — |
| Storage by Zapier | 16 | 1 | — |
| Pardot | 12 | 2 | **decommissioning 31 Aug 2026** |
| BugHerd | 10 | 1 | — |
| LearnUpon | 8 | 1 | — |
| Campaign Monitor | 7 | 1 | Campaign Monitor |
| **Raisely** | 6 | 1 | BirdLife Australia |
| **Ortto** | 6 | 1 | birdlife |
| Google Analytics 4 | 3 | 2 | mathew.hema.admin@birdlife.org.au |
| Humanitix | 1 | 1 | mathew.hema@birdlife.org.au |
| Webhooks by Zapier | 1 | **0** | — |

**Credential sprawl is the standing risk: 8 Outlook connections and 9 Excel connections.** Nobody knows who owns all of them or what they can reach. That belongs in the next access review.

**Pardot connections (2) become dead weight after 31 Aug 2026** — remove them with the decommission.

## The Zap that should be running and is not

**Zap ID 371228125 — "Unreconciled Income Exception Report"**

| Step | Detail |
|---|---|
| Trigger | Schedule, **every Tue and Fri 12:00 AM AEST** |
| Step 1 | Salesforce Find Records — report `00ORF0000033T6z2AE`, unreconciled Opportunities, last 7 days |
| Step 2 | NetSuite Find Records — account 3440597, Token-Based Auth, **±3-business-day matching** |
| Step 3 | Email an HTML exception table to mathew.hema@birdlife.org.au |
| **Status** | **DRAFT. Never published.** |

Prerequisites: connect Salesforce (OAuth) and NetSuite (**TBA credentials do not yet exist** — needs an integration record plus consumer key/secret and token ID/secret, user Mathew Hema, Administrator role), test each step, second-person review, publish.

**This is the cheapest high-value action in the finance stack.** Unreconciled income was $671,117 across 2,878 records at 3 Jul 2026 and growing roughly $87K/day. The detection mechanism exists and is switched off. Raise it every time reconciliation comes up.

Cost note: the same NetSuite TBA credential set unblocks other NetSuite Zaps, so create it once, properly.

## The LearnUpon catch-hook — treat as sensitive

LearnUpon (`learn.birdlife.org.au`) has a partially configured **Webhooks v2 → Zapier catch-hook**, with **only "Course enrolment" ticked, not completion**. The Zapier account behind it belongs to **keith.tsui@birdlife.org.au**, not Mathew.

The live catch-hook URL appears in plaintext in BirdLife documentation. **Rotate it and scrub the docs.** Confirm purpose with Keith before building on it or repointing it — an unowned live webhook that somebody else's account controls is exactly the kind of thing that breaks silently.

There is no write-back to Employment Hero. A proposed future bridge (LearnUpon completion → Zapier → PATCH the EH Certification API) requires the **EH Platinum tier**, which BirdLife does not hold.

## The historical EH → Azure AD manager sync (superseded)

Zapier trigger "New or Updated Employee" → filter out Contractors → Graph client-credentials token via Entra app `EH-OrgSync-Zapier` (`User.ReadWrite.All`) → `PUT` manager `$ref`. Cost profile ~4 tasks per employee; usage was 142 of 2,000 monthly.

**Superseded** by the native Employment Hero → M365 integration. If it is still enabled, it is now a second uncontrolled writer into Entra. Check and disable.

## Publishing the exception report: the runbook

Everything below is Tier 2 (a human with Zapier and NetSuite admin runs it);
the session prepares and verifies.

1. **NetSuite TBA credentials** (do not exist yet): Setup, Integration,
   Manage Integrations, New: name "Zapier Exception Report", Token-Based
   Authentication ticked, TBA authorization flow off, save and capture the
   consumer key/secret once (they are shown once). Then Setup, Users/Roles,
   Access Tokens, New: application = that integration, user = Mathew Hema,
   role = Administrator (note the segregation-of-duties smell; a dedicated
   integration role with read-only transaction access is the better long-term
   answer). Capture token id/secret once. Store all four in the Zapier
   connection, nowhere else.
2. **Salesforce OAuth** connection as the Zapier integration user, not
   Mathew's personal login, so it survives a password change.
3. **Test each step** with the report id `00ORF0000033T6z2AE` and a known
   week; confirm the ±3-business-day matching returns both matched and
   unmatched examples.
4. **Second-person review** (Nina Lewis or Keith) of the step mappings and
   the email recipient list, recorded in an Asana comment.
5. **Publish**, then verify the first Tuesday run produced an email; a Zap
   that runs and emails nothing is the "firing but idle" failure the OS treats
   as an incident.
6. Register it: `os/registers.md` gains a row (it is a scheduled job even
   though it is not a Claude routine).

## Failure routing
Zap errors should not die in Mathew's inbox. The designed route is Zap
Manager error, then a Salesforce Case with Type `System Notification` on the
Zeus record type, so failures show up in the queue the team already works.
Until that route is built, a Zapier error email is a ticket in disguise: log
it as a Case when you see one.

## Available tooling

`mcp__Zapier__*` can discover, enable, disable, inspect and execute actions, manage connections, and create Zapier skills. `list_zapier_connections` requires a `selected_api` argument — use `inspect_zapier_actions` with no arguments to enumerate apps first.

**Never display `selected_api` values to the user.** They are internal identifiers.

## Operating rules
1. **Prefer the native MCP connector** for Salesforce, Asana, Outlook, Teams and Excel. Use Zapier only for apps with no native path.
2. **A Zap that writes to a system of record needs a second-person review before publishing.** That is the rule the exception report is currently waiting on.
3. Every live webhook URL is a credential. It does not go in a document.
4. Before enabling a new action, check whether an existing connection already covers it — there are already 8 Outlook and 9 Excel connections.
5. Zapier is not on this project's approved connector list. Flag that in anything governance-facing, and note that it holds credentials for nine systems that are also not on the list.
