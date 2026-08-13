# Canonical Extraction Queries

The **only** sanctioned way to compute each base number. Copy these; do not
paraphrase them — most encode a trap that a paraphrase will reintroduce.
All are read-only. SOQL runs via the Salesforce MCP connector; SuiteQL via
`ns_runCustomSuiteQL`; Stripe via `stripe_api_read`/`stripe_api_search`.

## Salesforce (SOQL)

### Regular giving — the mandatory union (DQ-05)
Two queries, presented together, always.

```sql
SELECT COUNT(Id) FROM npe03__Recurring_Donation__c
WHERE npsp__Status__c = 'Active'
```
```sql
SELECT COUNT(Id) FROM AAkPay__Recurring_Payment__c
WHERE AAkPay__Status__c = 'Active'
```
> Verify both status picklist values against the live org before first use —
> never assert a picklist value not read from the org. Namespace-qualify
> everything: the unmanaged `Subscription__c` collides with
> `AAkPay__Subscription__c` (DQ-20).

### ICT open queue (DQ-08)
```sql
SELECT Owner.Name, Status, COUNT(Id) cnt
FROM Case
WHERE RecordType.DeveloperName = 'Zeus' AND IsClosed = false
GROUP BY Owner.Name, Status
```
`Owner.Name = 'Zeus'` is the unassigned intake queue, not a person. The record
type is `Zeus` (Id `012I80000004IPnIAM`) — **not** `Ask_Zeus`.

### ICT missing-Type coverage
```sql
SELECT COUNT(Id) FROM Case
WHERE RecordType.DeveloperName = 'Zeus' AND IsClosed = false AND Type = null
```
(`Type` is a picklist — `= null` is safe here; the `!= null` trap (DQ-04)
applies to **number** fields.)

### Conservation enquiry load per programme
```sql
SELECT RecordType.DeveloperName, COUNT(Id) cnt
FROM Case
WHERE IsClosed = false AND RecordType.DeveloperName != 'Zeus'
GROUP BY RecordType.DeveloperName
```

### Fundraising income FYTD (Australian FY, Close Date basis)
```sql
SELECT SUM(Amount) FROM Opportunity
WHERE IsWon = true
  AND CloseDate >= 2026-07-01 AND CloseDate < 2027-07-01
  AND RecordType.DeveloperName NOT IN (/* membership record types — read live */)
```
State the FY basis on the tile. Related tiles (major donor, appeal splits) must
derive from this same query with added filters — independent per-tile queries
caused the $37.5K double-count (DQ-07).

### Population/coverage counts on number fields (DQ-04)
```sql
SELECT COUNT(Id) FROM Contact
WHERE BetterImpact_ID__c != null AND BetterImpact_ID__c != 0
```
Number fields default to 0. `!= null` alone reads 479,613; the truth is 1.

### Membership — active members (pre-migration)
```sql
SELECT COUNT(Id) FROM Contact WHERE Active_BL_Member__c = true
```
Caveat on every use: this flag is maintained by Payments2Us, which is being
decommissioned (DQ-06). Post-migration the sanctioned source becomes the new
`Membership__c` object; run both during transition and publish the delta.

## NetSuite (SuiteQL)

Always scope to subsidiary 2. Never create saved searches for these.

### Income by GL account and department, current NS fiscal year
```sql
SELECT a.acctnumber, a.fullname, t.department, SUM(tl.netamount) amt
FROM transactionline tl
JOIN transaction t ON t.id = tl.transaction
JOIN account a ON a.id = tl.expenseaccount
WHERE tl.subsidiary = 2
  AND t.posting = 'T'
  AND t.trandate >= DATE '2026-01-01'
  AND a.accttype IN ('Income','OthIncome')
GROUP BY a.acctnumber, a.fullname, t.department
```
> Validate column names with `ns_getSuiteQLMetadata` before first run; the
> transactionline join shape varies by record family. Show the share of rows
> with department/class null or `_NOT_SPECIFIED` as `unmapped %` (DQ-13).

### Bank reconciliation ageing (DQ-19)
Target accounts: **11104** NAT Operations (378 unmatched baseline), **11103**
NAT ABF Donations (120). Report unmatched count and oldest item age per
account; both were last reconciled 31 Mar 2022 — the metric is a control alarm
until cleared.

### Membership income (GL basis)
Accounts 41001/41002 (memberships), 44023 (subscriptions). Note memberships and
subscriptions sit **outside** fundraising scope in the reconciliation — one of
the seven documented discrepancy causes.

## Stripe (read-only, account `acct_1PaqQkEdZ08H7Yxq`, livemode)

- **Charges/volume:** balance transactions by created date — pair every figure
  with the SF and NS view; the gap is the answer, not an error.
- **Refunds (DQ-03):** list refunds by created date; match to SF by amount +
  date ± 3 days. Label all matches `matched_fuzzy` until `Stripe_Refund_ID__c`
  exists. Never assert a refund is reflected in Salesforce without verifying.
- **Payouts:** cross-check against NAB bank feed lines; the payout webhook
  support thread was unresolved as at Aug 2026 (DQ-17).

## WooCommerce (REST `/wp-json/wc/v3`)

Credentials from environment variables only — keys were previously leaked in a
routine prompt and are to be rotated (root README).

- **Orders:** `GET /orders?status=completed&after=…` → `fact_order`.
- **Write-back check (DQ-02):** for each paid order, test post meta
  `salesforce_Opportunity_ID` present and non-empty → `sf_writeback_ok`.
- **Sync integrity (DQ-01):** completed orders without a corresponding SF
  Opportunity within 24h count as sync failures; expect ~10% until FLS is fixed.

## Asana (MCP)

- **Flow metrics:** `get_project` → read sections live (never hardcode GIDs) →
  tasks per section, plus: `due_on = null` count, days since `modified_at`
  (30/60/90 buckets), unassigned count, overdue count.
- Publish the hygiene counts next to the flow metrics (DQ-14).

## Entra / Defender (read-only local MCP or portal export)

- **Staff extraction:** users excluding `#EXT#` guests, matched on `mail` ↔ EH
  `company_email` and `employeeId` ↔ BLA### where populated.
- **Security snapshot (monthly):** Secure Score %, MFA-capable %, device
  compliance %, E8 levels — aggregates only into `fact_security_posture`;
  named per-user weakness lists are confidential and never leave the security
  team (see sensitive-data rules in `02-canonical-model.md`).

## Employment Hero

No connector. Until the Logic App 403 is resolved (DQ-15), staff extracts are a
governed CSV export keyed on BLA###. The native EH→M365 add-on overwrites
blank-for-blank — never treat Entra attributes as independent evidence of EH
values.
