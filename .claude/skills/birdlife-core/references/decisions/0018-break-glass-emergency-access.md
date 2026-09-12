# ADR 0018: Establish break-glass emergency access, separated from privilege delegation

- **Status:** Proposed
- **Date:** 24 August 2026
- **Raised by:** Claude, for Mathew Hema
- **Decided by:** Pending

## Context
ADR 0015 concentrated all keys and write access with one person, Mathew Hema, on the stated
basis that the team does not yet have the capability, with progressive delegation tracked
through the capability ladder (IT-SEC-002). A privileged access and break-glass standard was
proposed at the same time and declined.

ADR 0015 records its own counter-argument: the capability argument justifies not delegating
routine privilege, but it does not address break-glass, which is an availability control
rather than a delegation of authority. The two were declined as one decision. This ADR
separates them and decides only the availability half.

ADR 0017 makes this urgent rather than merely outstanding. It introduces agents that act
unattended under credentials that one person controls. If that person is unavailable, nobody
can administer the estate and nobody can stop the agents either.

## Decision proposed
Establish break-glass emergency access as a control independent of the capability ladder.
Two components.

### Component 1: sealed emergency credential
- A dedicated cloud-only Entra account holding Global Administrator, created solely for
  emergency use and used for nothing else.
- Excluded from Conditional Access policies that could lock it out, on the standard ACSC
  and Microsoft guidance for emergency access accounts. This exclusion is deliberate and
  documented, not an oversight.
- Authentication by a hardware method stored physically with the sealed credential.
- The credential is sealed and held in physical custody by the Chief Executive Officer or
  the Chief Financial Officer. No standing access is granted to any additional person and
  no additional person learns the credential.
- Any use triggers an automatic alert to the ICT alert channel, a mandatory post-use review,
  and immediate credential rotation and resealing.
- Tested once per year as a scheduled exercise. The test result and the reseal are recorded.

### Component 2: agent emergency stop
- Every L3 agent under ADR 0017 has a documented emergency stop, exercisable by any member
  of the ICT team without the credential holder present.
- The stop is documented in the instrument runbook and exercised at go-live.

## Rationale
This delegates no authority. Nobody gains working access to any system on any ordinary day.
The custodian holds a sealed envelope, not a role. That is precisely why it does not conflict
with ADR 0015: the capability argument is about who may exercise privilege routinely, and
this control is about whether the organisation can reach its own systems at all when the one
person who can is unreachable.

Custody sits with the CEO or CFO because the control needs a custodian outside ICT and
senior enough that opening it is a recorded organisational act rather than an informal one.

The annual test is the part that makes this real. An untested emergency credential is a
belief, not a control, and the common failure is discovering at the worst moment that the
account was disabled by a policy change or that the hardware token has expired.

## Consequences of accepting
An emergency access account excluded from Conditional Access is, by construction, a
high-value target. That exposure is real and is the price of the control. It is mitigated by
single-use custody, alerting on any use, and rotation after every use including tests.

The annual test needs a diary entry and about an hour of two people's time.

## Consequences of declining
BirdLife retains no tested route into its own systems if one person is unavailable, and
under ADR 0017 also no route to stop unattended agents acting under that person's
credentials. The organisation would be accepting a single point of failure across identity,
finance, payments, website and helpdesk simultaneously.

If declined, that acceptance should be recorded as an explicit risk acceptance with a named
accepting officer above the Senior Manager ICT, in the same form as the MFA strength risk
acceptance in ADR 0008. It should not sit as an unstated consequence of a delegation
decision.

## Impact on people
Andrew Dunn, Keith Tsui and Nina Lewis gain no new privileges. The capability ladder
(IT-SEC-002) is unchanged and no rung moves. This ADR should not be presented to them as a
delegation, because it is not one.

The CEO or CFO takes on custody, not administration. The realistic objection is that it
looks like handing IT keys to Finance or to the CEO's office. It is not, and the annual
test is the evidence that distinguishes the two. Framing the ask as custody of a sealed
item, with an annual fifteen-minute obligation, is what makes it acceptable.

For Mathew Hema personally, this reduces exposure. At present, being unreachable is an
organisational incident. After this, it is an inconvenience.

## Related
ADR 0015 (single-owner privileged access, partially superseded on the availability question
only; the delegation decision stands unchanged), ADR 0008 (form for a recorded risk
acceptance if this is declined), ADR 0017 (autonomous agent operation, which depends on the
Component 2 emergency stop), ADR 0009 (Azure subscription Owner principals),
IT-SEC-002 (privileged access capability ladder, unaffected).
