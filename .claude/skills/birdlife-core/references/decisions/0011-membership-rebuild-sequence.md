# ADR 0011: Membership rebuild sequence and scope

- **Status:** Accepted
- **Date:** August 2026
- **Decided by:** Mathew Hema

## Context
The membership model is being rebuilt across WooCommerce and Salesforce. Several
candidate starting points existed: the Blitzm WordPress build, the miniOrange field
mapping, a new Salesforce Membership object, or extending Keith's existing
`Subscription__c`. Starting in the wrong place would have forced rework in the other two.

## Decision
Build in this order.

1. Blitzm WordPress build direction
2. miniOrange field mapping
3. The new Salesforce Membership object

Payments2Us is being replaced and is explicitly out of scope of the build. The Payments2Us
technical documentation (IT-SF-001) was produced as an as-is baseline for migration
framing only, not as a target state.

Keith's `Subscription__c` is a migration source only. It is not the build target.

## Rationale
The WordPress side determines what data exists and in what shape. Mapping before the source
is settled means mapping twice. Building the Salesforce object before the mapping is known
means designing fields against assumptions.

Naming `Subscription__c` as a source rather than a target was necessary because it is the
obvious thing to extend, and extending it would have carried the old model into the new one.

## Consequences
Keith has clarity that his existing object is not being extended, which is a message worth
delivering directly rather than letting him infer it from the build order.

The build cannot start until the WooCommerce Subscriptions licence is renewed. That lapsed
licence is currently sitting on live payments of roughly A$11k per month and is also the
gate on this sequence, which makes it a higher priority than its cost suggests.

## Related
IT-INT-001 (membership field mapping), IT-INT-002 (Blitzm gap analysis), IT-SF-001
(Payments2Us as-is baseline).
