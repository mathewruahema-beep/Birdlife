# ADR 0006: Connected estate has outgrown the approved connector list

- **Status:** Open, needs a governance decision
- **Date:** 8 August 2026
- **Raised by:** Claude, for Mathew Hema

## Context
The project instruction block approves seven connectors: Salesforce, WordPress, Asana,
Office 365, Cloudflare, Zoom and Miro. The live session carries well over twenty,
including NetSuite (production financial data), Stripe (live payments), Gmail, Google
Drive, Google Calendar, Atlassian, Canva, Granola, Zapier and AWS plus Azure via the
desktop bridge.

NetSuite was added in August 2026 and is explicitly noted in the NetSuite skill as being
outside the approved list.

## The question
Either the approved list is updated to reflect reality, or the estate is trimmed back to
the list. Running production financial and payment connectors outside a documented
approval is the kind of gap that is uncomfortable to explain to an auditor, and BirdLife
is simultaneously anchoring itself to Essential Eight.

## Options
1. Ratify the current estate. Document each connector, its data scope, its auth method
   and its business owner. Most honest, most work.
2. Trim to the approved seven. Cleanest on paper, loses real capability including the
   NetSuite reconciliation work already underway.
3. Tiered approval. Core seven ratified as standing; finance and payment connectors
   approved individually with a named data owner; the rest treated as low-risk utilities.

## Recommendation
Option 3. It matches the actual risk profile and does not punish useful work.

## Decision
Not yet made.
