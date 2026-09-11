# Patterns: Salesforce (Zeus)

Resolved problems, symptom first. Doctrine lives in `birdlife-salesforce` and
`birdlife-ict-assistant`; these entries point at it. Seeded 11 Sep 2026 from
the skills; new entries are appended by sessions as cases close.

### "All the other technicians' cases have vanished from the list view"
- **Seen**: 29 Jun 2026
- **Cause**: the "All Open Cases" list view had been filtered to `Case Owner Alias = mhema`.
- **Fix**: list view filter changed to `Closed = False` only. Tier 1.
- **Verify**: open the list view, check the filter panel shows only the Closed filter.
- **Doctrine**: `birdlife-salesforce`, ICT helpdesk / Case model.

### "I set the Case to Closed and the update failed"
- **Seen**: recurring, every session that closes a Case
- **Cause**: validation rule requires `Case_Closed_Reason__c` with `Status = Closed`.
- **Fix**: send both fields in the same `updateSobjectRecord` call. Tier 1.
- **Verify**: re-read the Case; Status Closed and the reason populated.
- **Doctrine**: `CLAUDE.md` rule 4; `birdlife-ict-assistant/references/reference.md`, closing a Case.

### "Reassigning to Keith picked the wrong Keith"
- **Seen**: Aug 2026, console `case_assign` design
- **Cause**: every ICT staffer has more than one active User record.
- **Fix**: resolve by Name and IsActive, tie-break by Zeus case ownership in the last 180 days, put ambiguity to the user. Tier 1.
- **Verify**: re-read `OwnerId` and the internal comment logging the assignment.
- **Doctrine**: `birdlife-ict-assistant`, resolving an ICT owner.

### "The report says 3,600 cases are waiting in New"
- **Seen**: 1 Jul 2026 dashboards; README finding
- **Cause**: the report counted all 19 record types; Ask Zeus had 8 in New.
- **Fix**: `RecordType.DeveloperName = 'Zeus'` on every Case query and report filter. Tier 1 for queries, Tier 3 for the ten reports (admin runbook in README).
- **Verify**: rerun the count with the filter; expect tens, not thousands.
- **Doctrine**: `CLAUDE.md` rule 5; `birdlife-reporting` data discipline.

### "A field reads 100% populated but the data is empty"
- **Seen**: `BetterImpact_ID__c` (479,613 reported, 1 real), `AAkPay__Member_Type__c`
- **Cause**: number fields default to 0, so `!= null` matches everything.
- **Fix**: count with `!= null AND != 0`, or sample rows.
- **Verify**: sample ten records and eyeball the values.
- **Doctrine**: `birdlife-salesforce`, query discipline.
