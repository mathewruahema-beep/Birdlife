# ADR 0010: Host the entra-admin MCP server in Azure rather than on the local workstation

- **Status:** Accepted
- **Date:** 11 August 2026
- **Decided by:** Mathew Hema

## Context
The read-only Entra MCP runs locally at `C:\azureintegration`. A locally hosted server only
works when that specific workstation is running and reachable. Mathew works from home four
days a week and from varying locations, which also makes location-based Conditional Access
controls unusable as a compensating control.

## Decision
Host the entra-admin MCP server remotely in Azure Container Apps, using a system-assigned
managed identity.

Connect the Entra MCP to Cowork directly for the Employment Hero to Entra reconciliation
work, rather than running one-off scripts or uploading CSV exports.

## Rationale
A system-assigned managed identity removes the need to store or rotate a client secret,
which is the failure mode that has already appeared elsewhere in the estate. See the
Employment Hero Logic App defect where a rotated refresh token was never persisted back to
Key Vault.

Remote hosting means the capability survives a laptop rebuild, a lost device, or travel.
It also means the server is reachable by a second person later, which matters for the
delegation path in ADR 0015.

## Consequences
The control boundary moves from "the server only runs on Mathew's machine" to Conditional
Access and the managed identity role assignments. CA-005 and ADR 0008 therefore carry more
weight than they did when the server was local.

Location-based Conditional Access is off the table as a control. Device compliance and
sign-in frequency are doing that work instead.

Container Apps introduces a small ongoing Azure cost and a component that needs patching
and monitoring like any other. It should appear in the Instrument 1 monitoring scope.
