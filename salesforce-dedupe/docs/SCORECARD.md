# The duplicate scorecard

Every duplicate group the automation evaluates gets one `Dedupe_Merge_Audit__c`
record — that record *is* the scorecard. Report and dashboard on the object, or
open `Scorecard_JSON__c` for the full per-pair, per-field breakdown.

## How a group is scored

1. **Discovery.** Contacts are grouped on normalised
   `FirstName | LastName | Email` (all three present) — the same grouping the
   Plauti *Clone: Daily Contact Merge* job uses.
2. **Scenario scores (0–100).** Every configured scenario (`Dedupe_Rule__mdt`)
   is evaluated for every pair in the group:
   `score = 100 × Σ(weight × fieldMatch) / Σ(weight)`.
   Fields blank on *both* sides drop out of the denominator; a field present on
   one side only counts against the score. The **group score for a scenario is
   the weakest pair's score** — one doubtful member holds the whole group back.
3. **ID points.** Independently of the 0–100 score, each matched field earns
   points of identification (full points for an exact-equivalent match, half for
   a fuzzy match ≥ 0.5). The group's points are again the weakest pair's total.

| Field | Exact-match points |
|---|---|
| Email / AllEmail | 1.5 |
| Phone / AllPhone / Mobile | 1.0 |
| First name | 0.5 |
| Last name | 0.5 |
| Mailing street | 0.75 |
| Mailing state | 0.25 |
| Account Name (Accounts) | 2.0 |
| Billing postcode (Accounts) | 1.0 |

First + Last + Email exact = **2.5 points** — exactly the SOP bar for Contacts.
A name-only or email-only match can never reach it on its own.

## The auto-merge gate (all four must pass)

| Gate | Ships as |
|---|---|
| Scenario score ≥ its Auto Merge Score | Only *Name and Email - Exact* has one (100) |
| ID points ≥ required | 2.5 (Contact), 3.0 (Account) |
| Guardrails green | portal users, active recurring giving, deceased conflicts |
| Capacity | group ≤ 6 records, ≤ 200 merges per run |

Fail the score → **Review**. Pass the score but trip a guardrail → **Blocked**
(these are the ones worth a human's time first). Pass everything in dry-run →
**Dry Run - Would Merge**. Pass everything live → **Auto-Merged**.

## Master record selection

1. The record with the **active portal login** (forced, per SOP).
2. Otherwise the record holding **active recurring giving**, then the most
   Opportunities, then the **oldest** record.

Before merging, blank master fields (phones, mailing address, birthdate) are
filled from the losers, and losers in other households are re-parented into the
master's household so the merge is valid; NPSP cleans up emptied households.

## Reading the audit record

| Field | Meaning |
|---|---|
| `Outcome__c` | Auto-Merged · Dry Run - Would Merge · Review · Blocked · Error |
| `Score__c` | Best scenario's group score (0–100, Plauti-aligned) |
| `Best_Scenario__c` | Which scenario produced that score |
| `Id_Points__c` | Group ID points (weakest pair) |
| `Flags__c` | Guardrail output, one flag per line |
| `Master_Id__c` / `Merged_Ids__c` | The merge trail |
| `Scorecard_JSON__c` | Full detail: every pair, every scenario, every field |
| `Run_Id__c` | Groups audits by run for reporting |

Suggested reports: outcome counts by `Run_Id__c` (trend), `Blocked` list (work
queue for Supporter Care), `Error` list (ICT follow-up).
