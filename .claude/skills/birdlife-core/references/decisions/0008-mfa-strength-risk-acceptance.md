# ADR 0008: Risk acceptance, push MFA rather than phishing-resistant authentication on the entra-admin endpoint

- **Status:** Accepted, with a recorded risk acceptance
- **Date:** 11 August 2026
- **Decided by:** Mathew Hema
- **Type:** Risk acceptance. This is the record an assessor will ask for.

## Context
`CA-005-EntraAdminMCP-Require-MFA-Compliant` (ADR 0007) requires multi-factor
authentication on the privileged endpoint. The choice of factor was open: standard
Microsoft Authenticator push, or a phishing-resistant method such as a passkey or FIDO2
security key.

## Decision
Use standard Microsoft Authenticator push.

## The risk being accepted
Push notification MFA does not resist adversary-in-the-middle phishing. An attacker
operating a proxy phishing page can relay the authentication and capture the resulting
session token. The compliant-device requirement in CA-005 raises the bar, but it does not
close this specific attack path.

The identity being protected holds directory write permissions and, per ADR 0009, Owner on
the Azure subscription. Compromise of this account is a tenant-level event.

## Rationale
Deliverability and speed. The endpoint needs to work now, from home and while travelling,
and hardware key logistics were judged to be a delay the programme could not absorb. The
decision was made with full knowledge of the limitation, not by default.

## Consequences
This is a known, deliberate gap against Essential Eight expectations for privileged access
and should be presented to the board as an accepted risk rather than as a control in place.

It should be revisited when the tenant-wide Conditional Access MFA rollout completes,
because at that point the marginal cost of issuing a passkey to one privileged account is
close to zero and the justification for accepting the risk weakens considerably.

Review trigger: completion of the tenant-wide MFA policy, or any adversary-in-the-middle
phishing attempt observed against BirdLife, whichever comes first.
