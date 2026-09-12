# ADR 0015: Privileged access stays with a single owner, with progressive delegation

- **Status:** Accepted
- **Date:** August 2026, exact date not recorded at the time. Confirm and correct.
- **Decided by:** Mathew Hema

## Context
Mathew holds all keys and write access across BirdLife's systems and is the escalation
point and owner of every system. The team is Andrew Dunn (level 1 support), Keith Tsui
(junior Salesforce developer), Nina Lewis (finance background and business support) and
Karishma Soni (external Salesforce developer, four years total experience).

A privileged access and break-glass standard was proposed and declined for now.

## Decision
Sole ownership of keys and write access stays with Mathew, on the stated basis that the
team does not yet have the capability. Roles and privileges move to team members
progressively as their capability grows, tracked through the privileged access capability
ladder (IT-SEC-002) covering all approved connectors, with Karishma on a separate
contractor track.

A formal privileged access and break-glass standard is deferred.

## Rationale
Delegating privilege ahead of capability creates incidents rather than resilience. The
capability ladder makes the delegation path explicit rather than indefinite, which is the
difference between staged delegation and hoarding.

## The counter-argument, recorded deliberately
This decision concentrates every credential, every escalation and every recovery path in
one person. There is no documented break-glass procedure. If Mathew is unavailable,
BirdLife has no tested route into its own systems.

The capability argument justifies not delegating routine privilege. It does not justify the
absence of break-glass, which is an availability control, not a delegation of authority.
A sealed emergency credential held by the CEO or CFO gives no working access to anyone and
removes the single point of failure. These are separable, and treating them as one decision
is the weak point in this ADR.

## Consequences
Andrew, Keith and Nina remain blocked from work they could otherwise absorb, and every
escalation routes to one person. That is a workload risk as much as a security one.

This ADR should be revisited when the capability ladder shows its first role transition, or
immediately if a break-glass event occurs, at which point it will be too late.

## Related
IT-SEC-002 (privileged access capability ladder), ADR 0009 (four Owner principals on the
Azure subscription).
