# ADR 0013: Offboarding extends to third-party SaaS revocation

- **Status:** Accepted
- **Date:** August 2026
- **Decided by:** Mathew Hema

## Context
The standard offboarding pattern is the `C:\azureintegration\offboard-<name>.ps1` Graph and
Exchange script. It handles Microsoft identity thoroughly and everything else not at all.

BirdLife runs 129 enterprise applications. An offboarding that revokes Microsoft access and
nothing else leaves a departed staff member with live credentials to whatever they held
directly.

## Decision
Bolt a third-party SaaS revocation checklist onto the existing offboarding runbook, rather
than treating each leaver as an individual case to close.

Delivered as IT-SEC-003, with a system register CSV and a PowerShell checklist generator.

Standing rules within the pattern:

- deactivate the staff Salesforce user
- leave external and portal logins on personal addresses alone unless confirmed
- leave the originating Case untouched until Mathew has run the script

## Rationale
A checklist generated from a system register scales. A per-leaver case does not, and it
depends on whoever is handling that case remembering the full estate.

The Salesforce rule exists because ICT staff hold multiple active User records, and the
portal rule exists because deactivating a personal-address login can remove a volunteer or
supporter relationship that has nothing to do with employment.

## Consequences
The system register becomes a maintained artefact. If it drifts, the checklist silently
under-revokes, which is worse than no checklist because it looks complete.

Andrew can execute more of the offboarding sequence once the Entra write tier lands, but
the third-party revocations mostly sit in systems where he does not hold admin. Those stay
with Mathew until the delegation ladder moves.

## Related
IT-SEC-002 (privileged access capability ladder), IT-SEC-003, ADR 0002, ADR 0015.
