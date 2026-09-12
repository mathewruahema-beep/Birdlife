# ADR 0012: Monitoring alerts route to Teams, not Salesforce Cases

- **Status:** Accepted
- **Date:** August 2026
- **Decided by:** Mathew Hema

## Context
Instrument 1 (IT-OPS-001) is a Salesforce plus external heartbeat health monitor. Alerts
could have been raised as Salesforce Cases, which would have put them in the existing
helpdesk queue, or pushed to Microsoft Teams.

The Salesforce queue currently carries over 4,000 cases in New status. That is an
acknowledgement bottleneck, not a resolution one.

## Decision
Alerts deliver to Microsoft Teams. The destination is a standard channel inside a new
private team. Critical alerts additionally direct message Mathew. All severities notify.

Remaining monitoring documentation is parked until the instrument is actually deployed.

## Rationale
Routing machine-generated alerts into a queue with a four-thousand item acknowledgement
backlog would have buried them. A separate private team keeps the signal clean and avoids
alarming the wider organisation with raw infrastructure noise.

"All severities notify" was chosen deliberately over a filtered start, on the basis that
tuning down from too much noise is easier than discovering what was silently suppressed.

Parking the documentation is a correction to a real pattern: this programme has produced
more documents than deployed instruments.

## Consequences
Alert fatigue is the predictable failure mode of notifying on all severities. If the
channel becomes noise within a month, that is the signal to tune, and the tuning decision
gets its own ADR.

Critical alerts direct messaging one person is a single point of failure. When Andrew's
capability grows (ADR 0015), he should be added to the Critical path.

The Teams routing decision is made but not yet written into the Power Automate setup guide.
That gap is the immediate action.
