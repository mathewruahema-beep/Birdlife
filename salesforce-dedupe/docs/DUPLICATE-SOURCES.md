# Where the duplicates come from — and the build-out that stops them

Root-cause inventory of every process creating duplicate Contacts/Accounts in
production, with the remediation designed for **development (staging sandbox)
first**. Evidence read live from production on **20 Aug 2026**. The interactive
program board tracks delivery status of each workstream.

## The intake picture (Contacts created, last 180 days: ~11,500)

| Creator | Records | What it is |
|---|---:|---|
| Keith Tsui | 5,305 | Bulk imports / admin data loads |
| Bird Bot (birdbot1 — **System Administrator profile**) | 2,965 | Integration writes (identify: miniOrange/Zapier) |
| Bird Bot (birdbot2 — Base Integration Profile) | 1,464 | Integration writes |
| Nina Lewis | 776 | Finance / supporter care imports |
| B2BMA Integration | 397 | Pardot analytics user — decommissioning 31 Aug 2026 |
| Mathew Hema + other staff | ~550 | Manual UI entry |

`LeadSource` is blank on **11,515 of 11,521** recent creates — provenance is
untracked, which is why source attribution needs `CreatedById` archaeology.

**Plauti review backlog: 101,691 unhandled duplicate groups** (`dupcheck__dcGroup__c`
where handled = false). This is the mop-up debt the merge automation exists to burn down.

## Workstreams (mirrored on the board)

### 1. WooCommerce → miniOrange sync — no dedupe keys in production
Production mappings have **no duplicate-check keys** on Product/Opportunity
mappings (they exist only in staging), and the plugin sometimes fails to write
the returned Salesforce Id back to WordPress post meta ("Salesforce UUID:
None") — the next status change then creates a duplicate.
**Dev build-out:** replicate the staging mapping keys to a prod-shaped staging
test, run a deliberate write-back test, add a weekly exception report (orders
missing `salesforce_Opportunity_ID` meta), then promote the mapping config.
Depends on the Blitzm/Karishma Week-4 refund-flow decision gate.

### 2. Raisely → MoveData — API writes bypass UI duplicate rules
Raisely upserts on `Raisely_UUID__c` as the Raisely Integration User. A
supporter who signs up with a new email gets a new UUID → new contact; UI
duplicate rules do not fire on this path (MoveData Contact/Account duplicate
rules exist and are active — verify their API action is Report, and alert on it).
**Dev build-out:** staging test matrix of Raisely payloads (same email/new UUID,
new email/same person); confirm MoveData rule action + reporting; rely on the
nightly scorecard automation for detection; do NOT modify managed MoveData flows.

### 3. Bulk imports — largest single source
5,300 + 776 records in 180 days from two people's loads. Any import without
email/Supporter-ID matching mints duplicates in batches.
**Dev build-out:** import SOP — upsert on external Id (Supporter ID / email via
NPSP Data Import with matching rules), Plauti single-upload check for ad-hoc
files; rehearse in staging with a real file before every production load.

### 4. Bot integrations on wrong profiles
birdbot1 creates ~3,000 contacts/180d **as a System Administrator** — sysadmin
writes can bypass sharing and make attribution/dedupe governance impossible;
birdbot2 adds ~1,500 on the Base Integration Profile. Which external systems own
birdbot1/2 writes needs to be pinned down (miniOrange, Zapier, Ortto are the candidates).
**Dev build-out:** map each bot to its integration; move birdbot1 off System
Administrator to a scoped integration profile/permission set; enforce upsert-by-
external-Id in each integration; stamp `LeadSource` per integration so
provenance stops being archaeology. (Licence-neutral: existing users.)

### 5. Pardot / B2BMA — self-resolving 31 Aug 2026
397 creates in 180 days from the B2BMA Integration user. The Pardot hard
cutover removes this source; verify `AccountEngagementSync__c` is retained and
watch that the Ortto replacement sync (2M records) doesn't become a new
duplicate source — Ortto is read-heavy but its retention ceiling blocks sync
expansion.

### 6. Staff manual entry — smallest source, already fenced
Plauti runs *Name and Email - Exact* on INSERT and *All Email* on
INSERT/UPDATE/FLOW; native NPSP email-match rule is active in the UI.
**Dev build-out:** none beyond keeping the rules on; add the Type-on-entry
provenance (LeadSource default per app) while in there.

### 7. The mop-up engine — scorecard merge automation (this repo)
101,691 unhandled Plauti groups + whatever the intake fixes above don't stop.
**Dev build-out:** deploy `salesforce-dedupe` to staging → dry run → review
scorecards → supervised live run (cap 50) → nightly schedule in production.
Retire the Plauti "Clone: Daily Contact Merge" job once live (one auto-merge
engine at a time).

### 8. Refund/cancellation sync defects (adjacent, same root)
The miniOrange refund flow writes invalid Opportunity stages and duplicate
positive Payments and never deactivates `Subscription_Member__c` — same
write-back gap family as #1, tracked to the Karishma Week-4 fix-or-accept gate.

### 9. One identity, many keys
Supporter ID (`C-…`/`N-…`), `Raisely_UUID__c`, WooCommerce post meta, Ortto
person id, LearnUpon, Humanitix… each integration keys on something different,
so each can re-create a supporter the others already know.
**Dev build-out:** identity-key register (which system owns which external Id
field), Contact Platform Key objects as the join table, and a rule: every new
integration must upsert on a registered external Id before go-live.

## Sequencing

1. **Now:** #7 staging deploy + dry run (unblocks backlog burn-down and gives
   the measurement baseline for everything else).
2. **Next:** #1 and #4 (biggest preventable inflows), #3 SOP (cheap, immediate).
3. **Watch:** #5 resolves itself at Pardot cutover; #2 verify-and-monitor.
4. **Then:** #9 as the durable fix; #8 rides the Week-4 decision.
