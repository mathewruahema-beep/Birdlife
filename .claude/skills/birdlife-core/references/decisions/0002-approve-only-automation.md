# ADR 0002: Approve-only automation for identity and offboarding

- **Status:** Accepted
- **Date:** August 2026
- **Decided by:** Mathew Hema

## Context
Identity lifecycle work is roughly 20% of the helpdesk queue and the single highest-value
automation target. It is also the work with the worst blast radius when it goes wrong: a
mistaken disable or licence strip hits a real person mid-workday.

## Decision
Unattended and assisted tasks **detect and prepare**. A human approves every Entra write.
Claude produces the exact Graph PowerShell or click-path; Mathew or a delegated admin runs it.

## Current enabling state
Read-only Entra and Intune MCP server at `C:\azureintegration` (app `d8125f4d`). A
write-tier `entra-admin` server has been built alongside it but is **pending a separate
app registration and admin consent**. Until that consent lands, every Entra write is
prepare-and-hand-over by necessity as well as by policy.

## Consequences
Offboarding stays partly manual and therefore stays slow. The Finn Saurine offboarding
(Case 00136940) ran 19 days past the termination date with the account still enabled and
licensed. That latency is the accepted cost of the model today, and it is the argument
for completing the admin consent, not for abandoning the approval gate.

## Revisit when
Admin consent is granted. At that point re-decide whether the approval gate stays manual
or becomes a logged, reversible auto-action with notification.
