# ADR 0009: Grant Owner on the Azure subscription to the dedicated admin account

- **Status:** Accepted
- **Date:** 11 August 2026
- **Decided by:** Mathew Hema

## Context
`mathew.hema.admin` held Contributor on the BirdLife Australia Azure subscription.
Contributor cannot assign roles, which blocks the managed identity role assignments needed
to host the entra-admin MCP in Azure (ADR 0010).

## Decision
Grant `mathew.hema.admin` the Owner role on the BirdLife Australia Azure subscription.

## What this surfaced
Three other principals already hold Owner on the same subscription:

- the vendor account `sxiq.azure`
- two shared `.onmicrosoft.com` administrative logins

Shared administrative logins cannot be attributed to an individual, which means no action
taken under them is auditable. A standing vendor Owner grant is a third-party dependency
with no expiry.

## Consequences
The hosting work in ADR 0010 is unblocked.

The subscription now has four Owner principals, three of which BirdLife does not
individually control. That is a finding, not a decision, and it needs its own treatment:
attribute or retire the two shared logins, and either time-bound the vendor grant or move
it to Privileged Identity Management with just-in-time elevation.

Until that happens, any Essential Eight or insurance assertion about privileged access
control on Azure is not defensible.

## Related
ADR 0007, ADR 0010, ADR 0015 (privileged access model).
