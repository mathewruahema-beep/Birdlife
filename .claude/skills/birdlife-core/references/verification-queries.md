# Verification Queries

Every volatile figure that appears anywhere in this brain, paired with the query that
refreshes it. **Run the query. Do not quote the baseline.**

Baselines are recorded only so you can state the direction of travel ("up from X in
July"), never so you can present them as current.

Queries marked **VERIFIED** were executed successfully on 8 Aug 2026 and returned the
value shown. Unmarked queries are written from the schema and should be sanity-checked
on first use.

---

## Salesforce (connector: `mcp__Salesforce_Production__soqlQuery`)

### Full-licence headroom
**VERIFIED 8 Aug 2026 → Salesforce 69/70 used, 1 free. Platform 21/40.**
Baseline in the digests: "70/70, zero headroom" (2 Aug). Already wrong.

```sql
SELECT Name, TotalLicenses, UsedLicenses
FROM UserLicense WHERE TotalLicenses > 0 ORDER BY UsedLicenses DESC
```

### Helpdesk backlog by status
**VERIFIED 8 Aug 2026 → New 4,047 · In Progress 250 · Waiting Response-External 168 ·
Response Received 99 · On Hold-Internal 47 · Closed 116,587.**
Baseline: "~3,600 New (1 Jul)". Understated by 12%.

```sql
SELECT Status, COUNT(Id) total FROM Case GROUP BY Status ORDER BY COUNT(Id) DESC
```

### Cases with no sub-type (reporting-quality metric)
```sql
SELECT COUNT(Id) FROM Case WHERE Sub_Type__c = NULL
```

### System administrators as a share of internal users
Target is 5% or below. Baseline claim: 15%.
```sql
SELECT COUNT(Id) FROM User WHERE IsActive = true AND Profile.Name = 'System Administrator'
```

### Active users never logged in, or dormant 90+ days
Feeds both licence reclaim and the access review.
```sql
SELECT Id, Name, Username, Profile.Name, LastLoginDate
FROM User WHERE IsActive = true AND (LastLoginDate = NULL OR LastLoginDate < LAST_N_DAYS:90)
ORDER BY LastLoginDate NULLS FIRST
```

### Leavers still holding an active user record
Run after every offboarding. Catches the second-account problem.
```sql
SELECT Id, Name, Username, IsActive, Profile.Name, LastLoginDate
FROM User WHERE IsActive = true AND Name LIKE '%SURNAME%'
```

### miniOrange / WooCommerce sync failure rate
Baseline: 10.3-10.5% failing on FLS against `npe01__Opportunity__c`.
```sql
SELECT COUNT(Id) FROM stripeGC__Sync_Log__c WHERE stripeGC__Error_Details__c != NULL
AND CreatedDate = LAST_N_DAYS:7
```

### Never trust a null-count in this org
Number fields default to 0, so `!= null` reads as 100% populated. Always:
```sql
-- WRONG: WHERE Field__c != null
-- RIGHT:
SELECT COUNT(Id) FROM Contact WHERE BetterImpact_ID__c != null AND BetterImpact_ID__c != 0
```

---

## NetSuite (connector: `mcp__NetSuite__ns_runCustomSuiteQL`)

### Unreconciled income
The single most-quoted and fastest-decaying number in the estate. Baseline
**$671,117.07 across 2,878 records as at 3 Jul 2026, growing roughly $87K/day**. On that
growth rate the figure is out by seven figures within two months. Never quote the
baseline. Re-derive it, and if the SuiteQL below does not match the finance definition,
fix the query here rather than falling back to the stale number.

```sql
SELECT COUNT(*) AS records, SUM(amount) AS total
FROM transaction WHERE /* reconciliation flag per the Master Technical Guide, Section 7 */
```

### Bank reconciliation currency
Accounts 11104 and 11103. Baseline: last reconciled 31 Mar 2022, 4+ years overdue, and a
mandatory precondition of any Business Central migration.

### Saved search hygiene
Baseline: 212 searches, 115 never run, 46% owned by the Fusion5 Support login.
```
mcp__NetSuite__ns_listSavedSearches
```

---

## Microsoft 365 and Entra

**No admin connector.** Everything here is Tier 2: read via the local read-only MCP at
`C:\azureintegration`, Graph PowerShell, or the portal. Prepare, do not execute.

### MFA coverage
Baseline 23 Jun 2026: 203 of 2,561 (7.9%) MFA-capable. One skill rounds this to "~8%";
prefer the precise figure and its date, or refresh it.
```powershell
Get-MgReportAuthenticationMethodUserRegistrationDetail -All |
  Group-Object IsMfaCapable | Select-Object Name, Count
```

### Licence headroom and reclaim candidates
```powershell
Get-MgSubscribedSku | Select-Object SkuPartNumber, ConsumedUnits,
  @{n='Total';e={$_.PrepaidUnits.Enabled}}
```

### Disabled accounts still holding a licence
The direct measure of whether offboarding is actually completing.
```powershell
Get-MgUser -Filter "accountEnabled eq false" -All -Property Id,DisplayName,AssignedLicenses |
  Where-Object { $_.AssignedLicenses.Count -gt 0 }
```

### Secure Score and device posture
Baseline: Secure Score 48.19% (554.2/1150); 115 devices in MDE; 5,422 vulnerabilities,
200 critical, 122 exploitable. Refresh from the Defender portal, not from this file.

---

## Certificate and deadline expiries, do not store these, track them

Every item below is an **open item**, not a fact. Each one needs an Asana task with an
owner and a due date. A file does not chase anybody.

| Item | Date | Consequence if missed |
|---|---|---|
| Vevox Dashboard SAML cert | 21 Aug 2026 | SSO breaks |
| Pardot hard stop | 31 Aug 2026 | Cutover window closes |
| Vevox second cert | 8 Sep 2026 | SSO breaks |
| Salesforce release updates ×4 | 1 Sep 2026 | Forced, unplanned |
| NetSuite OAuth2 M2M cert | 17 Sep 2026 | Integration fails, and it is orphaned |
| Enterprise app access review | 19 Sep 2026 | Quarterly governance overdue |
| EmpHero-Entra Graph secret | 5 Jan 2027 | Sync fails |
| Ortto renewal | 12 Aug 2027 | Contract auto-decision |

**Already passed and unactioned at last check:** Salesforce Transaction Security Policies
(13 Jul 2026), AWS EKS end of standard support (29 Jul 2026, now accruing extended-support
fees), Google SAML IdP signing certificate (expired, date unrecorded).

---

## Stripe and WooCommerce

Baseline: ~A$11,108.70/month WooCommerce sales; ~6,466 orders as at Jul 2026, 70 refunded.
Refresh via `mcp__Stripe__stripe_api_read` against the eCommerce account. Remember only
one of three Stripe accounts is directly connected; the other two are observable through
Salesforce via `stripeGC`.

---

## Maintenance of this file

When you cite a volatile figure and find the baseline stale, **update the baseline here
in the same session** with the new value and today's date. That is the only place a
number should ever be written down, because it sits next to the query that proves it.
