# ADR 0014: LearnUpon to Employment Hero completion sync runs on Logic Apps, not Zapier Code

- **Status:** Accepted, pending a scope verification
- **Date:** August 2026
- **Decided by:** Mathew Hema

## Context
Training completions in LearnUpon need to write certification records into Employment Hero.
Two orchestration options existed: a Zapier Code step against the existing LearnUpon catch
hook, or the Azure Logic App plus Key Vault pattern already in use for the Employment Hero
to Entra sync.

## Decision
Run the orchestration on the existing Azure Logic App plus Key Vault pattern.

Verify the Employment Hero certification write scope before building anything.

## Rationale
One integration pattern is cheaper to operate than two. The Logic App pattern already has
Key Vault secret handling, retry semantics and Azure-side logging. Zapier Code would have
put business logic in a place with weaker observability and a credential model that sits
outside the tenant.

Verifying the write scope first is a direct response to the Employment Hero to Entra sync,
which is currently at zero succeeded and two failed on a 403 caused by insufficient
Employment Hero platform permission. Building before confirming scope has already cost this
programme once.

## Consequences
Two known defects in the existing Logic App pattern are inherited and must be fixed rather
than replicated: the rotated refresh token is not persisted back to Key Vault, and Key
Vault secrets carry no expiry metadata. Both should be fixed while the pattern is being
reused, not after.

Zapier stays in scope for connecting systems with no native connector, which is what it is
good at. It does not become the orchestration layer.

## Related
ADR 0006 (connector scope), the Employment Hero to Entra Logic App open item.
