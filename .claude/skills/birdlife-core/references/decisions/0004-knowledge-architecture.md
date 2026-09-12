# ADR 0004: Four-layer knowledge architecture with an explicit precedence order

- **Status:** Accepted
- **Date:** 8 August 2026
- **Decided by:** Mathew Hema

## Context
BirdLife's operational knowledge had accumulated across four stores with no defined
relationship between them: 17 Claude skills, a six-digest knowledge base, Cowork memory,
and the project instruction block. The same facts appeared in several places at several
vintages, and nothing declared which one won.

Two failures were confirmed by live query on 8 August 2026:
- The knowledge base recorded Salesforce full licences as 70/70 with zero headroom. The
  live figure was 69/70.
- The knowledge base recorded roughly 3,600 cases in New as at 1 July. The live figure was
  4,047, understating the backlog by 12%.
- The master index recorded Salesforce as not yet connected. It had been connected for days.

Neither digest was wrong when written. Both were wrong when read.

## Decision
Four layers, one precedence order, and a fact-classification rule.

**Precedence, highest first:** live connector query, then system skill, then knowledge
digest, then Cowork memory.

**Classification:** every fact is live, durable, a decision, or an open item. Live facts
are never stored, only their queries are. Open items live in Asana, never in a document.

**No duplication:** a fact lives in exactly one layer.

## Consequences
Volatile figures disappear from the written brain and are replaced by verification
queries, which makes the brain smaller and more trustworthy at the same time. Open items
gain owners and due dates, which means they can actually escalate. The cost is discipline
at write time: every new fact needs classifying before it is filed.
