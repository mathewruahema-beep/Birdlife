# Governance

How this knowledge base stays true. Without this, it becomes a confident liar within a
quarter, which is worse than having nothing.

## Roles

| Role | Who | Responsibility |
|---|---|---|
| Owner | Mathew Hema | Approves merges, owns the quarterly review, arbitrates precedence disputes |
| Contributors | Andrew Dunn, Keith Tsui, Nina Lewis | Raise pull requests, own assigned open items |
| Reviewer | Any contributor other than the author | One approval before merge |

**Bus-factor requirement:** at least two people must be able to build and publish the
plugin. If only the owner can, the repository has reproduced the exact problem it was
created to fix.

## The write test

Before adding anything, classify it.

1. **Can a connector answer this?** Then do not write the value. Write the query into
   `verification-queries.md`.
2. **Will it still be true in a year?** Then it is durable. Put it in the relevant skill.
3. **Is it a choice somebody made?** Then it is a decision. New ADR in `decisions/`, dated
   and attributed. Never edit an existing ADR.

   **A decision is not made until the ADR exists.** Cowork memory is not the decision log.
   Memory sits last in the precedence order and is scoped to preferences, so a decision
   recorded only there is invisible to everyone else and unavailable as evidence. This rule
   exists because it was broken: ADRs 0007 to 0016 were backfilled on 11 August 2026 from
   decisions made across the preceding three days and captured nowhere else.

   **Risk acceptances are ADRs, not notes.** Any decision that knowingly leaves a control
   gap open is tagged `Type: Risk acceptance`, states the risk in plain terms, names who
   accepted it, and carries a review trigger. ADR 0008 is the worked example. An assessor,
   an insurer or a board will ask for exactly this document and nothing else will do.
4. **Does it have a due date and need a human?** Then it is an open item. Asana task with
   an owner. Not a file.

Anything that fails all four is probably not worth recording.

## Review cadence

**Weekly, about ten minutes.** Run the verification queries. Update any baseline that has
moved, with today's date. This is the cheapest possible defence against staleness and it
is the one most likely to be skipped, so put it in a calendar with a name on it.

**Monthly.** Review open items. Anything with a due date inside 30 days gets confirmed with
its owner. Anything overdue gets escalated or explicitly re-dated with a reason. Silent
slippage is the failure mode.

**Quarterly.** Full read of every skill against reality. Move resolved findings into the
relevant digest under a "Closed" heading rather than deleting them, because the record of
what was fixed and when is itself governance evidence. Re-run the ingestion over any
source documents that changed.

**Event-driven.** Any material system change, new integration, or incident updates the
affected skill within the same week. Not at the next quarterly.

## Provenance

Every non-obvious claim carries how it was established and when.

Good: "MFA-capable 203 of 2,561 (7.9%), baseline audit 23 Jun 2026, refresh with the Graph
query in verification-queries.md."

Bad: "MFA coverage is about 8%."

The second is the same fact with the accountability removed. It survives being copied into
a board paper, where it becomes unattributable and unfalsifiable.

## Handling disagreement between layers

Live query wins. Always. Then fix the layer that was wrong, in the same session, and note
in the commit message what was stale and by how much. Those commit messages accumulate into
a useful record of which parts of the estate move fastest and therefore need the most
frequent verification.

## What must never go in this repository

- **Secrets of any kind.** Not keys, not tokens, not webhook URLs, not connection strings.
  This is not hypothetical: the knowledge base's own finding 3 records plaintext miniOrange
  webhook access keys printed across three documents and a live Zapier catch-hook URL in a
  fourth. Those keys need rotating and those documents need scrubbing before any of this is
  distributed more widely. Reference secrets by vault location only.
- **Personal information about staff or supporters.** Names in an operational context are
  fine. Health, performance, salary and personal contact details are not.
- **Live figures.** Covered above, but it bears repeating, because it is the most common
  and most tempting mistake.

## Pre-distribution checklist

Before this repository goes anywhere beyond the ICT team:

- [ ] Rotate the exposed miniOrange webhook keys, both production and staging
- [ ] Rotate or retire the exposed Zapier catch-hook URL
- [ ] Scrub the four documents that carried them, and check version history
- [ ] Confirm no skill or digest contains a credential
- [ ] Confirm every volatile figure carries a date and a refresh query
- [ ] Confirm a second person can run `scripts/build.sh` successfully

## Definition of done for a change

- Fact classified against the four-way test
- Filed in exactly one layer
- Provenance and date recorded
- Volatile figures paired with a query
- Reviewed by someone other than the author
- Plugin rebuilt and the version bumped
