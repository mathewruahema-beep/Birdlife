# ADR 0001: Anchor the security programme to ACSC Essential Eight with a SaaS/identity overlay

- **Status:** Accepted
- **Date:** August 2026
- **Decided by:** Mathew Hema

## Context
BirdLife needed a single named framework to measure security posture against. Drivers:
risk reduction, board governance, insurance and grant compliance obligations, and a
recent incident or near miss.

## Decision
Adopt the ACSC Essential Eight as the primary framework, with an explicit SaaS and
identity overlay layered on top.

## Rationale for the overlay
Most of BirdLife's real exposure sits in Salesforce, WordPress, Google Workspace and
roughly 129 enterprise applications. Essential Eight was designed to measure a managed
endpoint and server estate. Measured on E8 alone, the organisation would score itself
against the part of its attack surface that matters least.

## Targets
Maturity Level 1 within 12 weeks, Maturity Level 2 within 12 months.

## Consequences
Board reporting speaks E8, which is recognised by insurers and grant bodies. The overlay
findings need their own reporting line, because they will not appear in an E8 scorecard.
