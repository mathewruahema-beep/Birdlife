# ADR 0007: Dedicated admin identity and app registration for the entra-admin MCP

- **Status:** Accepted
- **Date:** 11 August 2026
- **Decided by:** Mathew Hema

## Context
ADR 0002 established an approve-only automation model for identity work, and the write
tier of the Entra MCP was built but blocked on a separate app registration and admin
consent. Every identity action stayed at Tier 2, prepare and hand over. The cost of that
is measurable: the Finn Saurine offboarding ran 19 days past the termination date, partly
because no write path existed.

The read-only server at `C:\azureintegration` (app `d8125f4d`) runs under Mathew's normal
working account. Extending that same identity to write scope would have put directory
write permissions behind a day-to-day sign-in.

## Decision
Register a dedicated application, `BirdLife-EntraAdminMCP-Auth`, and run it under a
dedicated administrative account, `mathew.hema.admin`, separate from the day-to-day
working account.

Protect that endpoint with Conditional Access policy
`CA-005-EntraAdminMCP-Require-MFA-Compliant`, requiring MFA and a compliant device, with
sign-in frequency set to 1 hour. Deploy in report-only mode first.

Adopt `CA-00x-<Scope>-<Intent>` as the standing Conditional Access naming convention.

## Rationale
Separating the privileged identity from the working identity is the control that limits
blast radius if the working account is phished. Report-only first is standard practice and
avoids locking the only administrator out of the tenant during rollout. The naming
convention exists because a Conditional Access estate without one becomes unreadable at
about a dozen policies, and BirdLife is heading there.

## Consequences
Identity work moves from Tier 2 to Tier 1 once consent is granted, which removes a
hand-off from roughly a third of helpdesk tickets. Andrew and Keith see faster onboarding
and offboarding turnaround without gaining the privilege themselves.

Report-only mode must be promoted to enforced. A policy left in report-only is a policy
that does nothing, and that promotion step is the one most likely to be forgotten.

Sign-in frequency of 1 hour means Mathew reauthenticates often during identity sessions.
That friction is deliberate and should not be relaxed without a new ADR.

## Related
ADR 0002 (approve-only automation), ADR 0008 (MFA strength risk acceptance),
ADR 0009 (Azure subscription Owner), ADR 0010 (hosting).
