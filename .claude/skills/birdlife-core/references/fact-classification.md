# Fact Classification, Worked Examples

Use this when you are unsure which layer a piece of knowledge belongs in, or whether a
figure can be quoted. The test is always: **how long does this stay true, and what
happens to the reader if it does not?**

## Class 1: Live

Changes on a timescale of days or faster. Quoting it from storage is a defect.

| Example | Why it is live |
|---|---|
| Unreconciled SF-to-NetSuite income | Moves roughly $87K a day |
| Cases in "New" | Moved 3,600 to 4,047 in five weeks |
| Salesforce licence headroom | Changed within one session, by our own offboarding |
| Vulnerability and CVE counts | Change with every Patch Tuesday |
| MFA registration percentage | Moves with every remediation batch |
| Device compliance and stale-device counts | Continuous |

**Handling:** never store the value. Store the query. See `verification-queries.md`.

## Class 2: Durable

Stable for years. The genuine content of the brain.

| Example | Why it is durable |
|---|---|
| Raisely joins to Salesforce on `movedata__Contact_Platform_Key__c` | Schema-level |
| Employment Hero's M365 add-on overwrites rather than merges | Vendor behaviour |
| Salesforce cannot close a Case without `Case_Closed_Reason__c` | Validation rule |
| Number fields default to 0, so `!= null` reads as 100% populated | Platform behaviour |
| BLA### worker code is the payroll-to-NetSuite join key | Design decision, embedded |
| Payments2Us also syncs to Xero | Integration topology |
| Each ICT staffer has multiple active Salesforce User records | Org history |

**Handling:** put it in the relevant system skill. State how it was established.

## Class 3: Decision

Made once, at a point in time, by a named person, for stated reasons. Immutable.

| Example | Recorded |
|---|---|
| Anchor to ACSC Essential Eight with a SaaS/identity overlay | ADR + memory |
| Approve-only automation: Claude prepares, Mathew approves Entra writes | ADR + memory |
| Salesforce, Asana and Office 365 as the first three connected systems | ADR |
| Business Central recommended but **not yet decided** | ADR, status open |

**Handling:** new dated file in `decisions/`. Never edit an existing one. To change a
decision, write a new ADR that supersedes it by number, and say why. The superseded
reasoning is often more valuable later than the decision itself.

A decision that is still open must be recorded as open. "Recommended, not decided" is a
real and useful state, and collapsing it to "decided" is a common and costly error.

## Class 4: Open item

Has a date and needs a human to act. The class that causes the most damage when
misfiled, because a document cannot escalate.

| Example | Belongs |
|---|---|
| Vevox SAML cert expires 21 Aug 2026 | Asana task, owner, due date |
| Rotate the plaintext miniOrange webhook keys printed in three docs | Asana task |
| Publish the unreconciled-income exception Zap (ID 371228125) | Asana task |
| Recover the two corrupted developer-handover documents | Asana task |
| 237-account MFA remediation list, all still "Pending" | Asana project |

**Handling:** create it in Asana in the IT Operations Project Plan with an owner and a
due date. Then, if useful, note the task URL in the knowledge layer. The file points at
the tracker; the tracker never points at the file.

**The test:** if the only thing standing between this item and a production outage is
somebody happening to re-read a markdown file, it is misfiled.

## Edge cases

**A dated baseline that shows a trend.** Keep it, next to the query, and always present
it as a trend rather than a level. "Unreconciled income was $671K on 3 Jul and growing
about $87K a day" is useful. "Unreconciled income is $671K" is false.

**A durable fact that might change soon.** Record it as durable, and raise the pending
change as an open item. Do not pre-emptively write the future state as though it were
current. The Business Central migration is the live example: the current ledger is
NetSuite, full stop, and BC is an open decision.

**Something a vendor told you.** Durable, but attribute it. Vendor statements about their
own product behaviour have been wrong here before, which is exactly how the Employment
Hero overwrite behaviour was discovered the hard way.

**A number in a screenshot or an exported report.** Live, always, no matter how official
the document looks. The report was true when it was run.
