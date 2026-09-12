# ADR 0016: Govern AI connectors through an org-level AI agent privileged access standard

- **Status:** Accepted
- **Date:** August 2026
- **Decided by:** Mathew Hema

## Context
Adding the Cloudflare API MCP server raised the general question rather than the specific
one. Connectors give an AI agent standing access to production systems under a human's
credentials, with no separate identity, no separate role and no separate audit trail.
Existing access control standards do not describe this.

## Decision
Add the Cloudflare API MCP server, and govern AI connector access through an organisation
level AI agent privileged access standard, anchored to Essential Eight, delivered as
markdown.

Begin the Zapier connector inventory (R1).

## Rationale
Essential Eight was chosen as the anchor for consistency with ADR 0001, so that AI agent
access reports into the same board-level framework rather than becoming a separate
conversation.

Markdown was chosen so the standard lives in the same repository as the knowledge it
governs and moves through the same review process.

## Consequences
The standard is unenforceable while ADR 0006 remains open. Approving a governance framework
for connectors while the connected estate has not been ratified is a documented control
with no scope. ADR 0006 is therefore a dependency, not a parallel workstream.

The Zapier inventory is the first evidence base the standard needs.

## Related
ADR 0001 (Essential Eight anchor), ADR 0006 (connector scope, open).
