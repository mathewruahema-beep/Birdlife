# BirdLife Salesforce dedupe automation

Scorecard-driven duplicate merge automation for **production** ("Zeus"),
aligned rule-for-rule with the live Plauti Duplicate Check configuration and
the manual dedupe SOP — plus the guardrails Plauti doesn't enforce.

| | |
|---|---|
| Matching rules | Mirror of the 8 live Plauti scenarios ([docs/ALIGNMENT.md](docs/ALIGNMENT.md)) |
| Scorecard | 0–100 Plauti-aligned score **+** SOP "points of identification" ([docs/SCORECARD.md](docs/SCORECARD.md)) |
| Auto-merge bar | Name+Email exact at 100, ≥2.5 ID points, guardrails green |
| Ships as | Dry-run ON, auto-merge OFF — first runs only produce scorecards |
| Licence impact | None — runs as an existing admin user |

## What it does that Plauti doesn't

- One **auditable scorecard per duplicate group**, persisted on
  `Dedupe_Merge_Audit__c` (reportable/dashboardable), with the full per-field
  breakdown in JSON.
- **SOP guardrails enforced in code**: portal-user-must-be-master, block on two
  active portal users, block when two records both hold active recurring giving
  (NPSP Recurring Donations, Payments2Us Recurring Payments, current
  Payments2Us Subscriptions), deceased-conflict block.
- **Master selection policy** (portal login → financial holder → oldest) and
  automatic fill-forward of blank master fields from the losers.
- Cross-household merges handled (losers re-parented, NPSP cleans up).
- Rate-limited, resumable nightly batch with dry-run mode.

## Components

```
force-app/main/default/
  classes/            DedupeConfig, DedupeEngine, DedupeGuardrails,
                      DedupeMergeBatch, DedupeScheduler (+ 2 test classes)
  objects/            Dedupe_Merge_Audit__c (scorecard/audit object)
                      Dedupe_Rule__mdt, Dedupe_Setting__mdt (config)
  customMetadata/     17 rule rows (the 8 Plauti scenarios) + Default settings
  permissionsets/     Dedupe_Admin
config/scorecard.json Machine-readable mirror of the rule set
scripts/apex/         dry-run-now, merge-now, schedule-nightly, unschedule,
                      last-run-summary
docs/DUPLICATE-SOURCES.md  Root-cause inventory of every duplicate-creating
                      process + the staging-first remediation plan
board/                Source of the interactive program board (live at
                      https://claude.ai/code/artifact/76712b3d-9d81-488a-974b-777343a58dae —
                      the artifact is the live copy; this file is the seed)
```

## Deployment — staging first, always

```bash
# 1. Staging
sf project deploy start -o birdlife-staging -d force-app -l RunSpecifiedTests \
   -t DedupeEngineTest DedupeMergeBatchTest
sf apex run -o birdlife-staging -f scripts/apex/dry-run-now.apex

# review Dedupe_Merge_Audit__c rows in staging, then:

# 2. Production (same command against the prod alias)
sf project deploy start -o birdlife-prod -d force-app -l RunSpecifiedTests \
   -t DedupeEngineTest DedupeMergeBatchTest
```

Note: `AllEmail__c` / `AllPhone__c` are referenced from custom metadata, not
compiled code — if a sandbox lacks them the engine skips those fields instead
of failing.

## Rollout sequence (recommended)

1. **Week 1 — dry run.** `scripts/apex/dry-run-now.apex`, then review the
   audit scorecards: outcome counts, spot-check 20 `Dry Run - Would Merge`
   groups and every `Blocked` group.
2. **Week 2 — supervised live.** Set `Dedupe_Setting__mdt.Default`:
   `Dry_Run__c = false`, `Auto_Merge_Enabled__c = true`,
   `Max_Merges_Per_Run__c = 50`. Run once manually, verify, raise the cap.
3. **Steady state.** `scripts/apex/schedule-nightly.apex` (9pm AEST, clear of
   the 7pm Conga receipting batch). Plauti's *Daily Contact Merge* clone job
   should then be retired or left as a cross-check — don't run two auto-merge
   engines against the same book.

## Operational notes

- **Kill switch:** set `Auto_Merge_Enabled__c = false` on the Default setting
  (metadata change, no deploy) or run `scripts/apex/unschedule.apex`.
- **Merges are not reversible.** The audit record keeps master + merged Ids;
  standard "undelete the merged contact" recovery applies within the recycle
  bin window only.
- Every run writes audits for **all** discovered groups; a first full pass over
  ~480k contacts will produce thousands of Review rows — that's the backlog
  scorecard, not noise. Filter dashboards by `Run_Id__c`.
- The batch only groups contacts with First + Last + Email all present, exactly
  like Plauti's daily job. Email-less duplicates surface through the *Same
  Address* and *Mobile Match* scenarios in Review — they never auto-merge.
- API-side prevention (Raisely/MoveData, miniOrange) is deliberately out of
  scope here — see the duplicate-sources remediation board for that work.
