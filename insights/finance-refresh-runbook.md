# Finance Dashboard — NetSuite Refresh Runbook

The NetSuite connector was authorised on 13 Aug 2026, **after** the session that
built the Finance dashboard — so the page still carries dated placeholders. Any
new Claude session with the NetSuite connector can execute this runbook verbatim
to make the page fully live. Nothing here needs designing; it is all execution.

## 1. Run the live queries

All SuiteQL, account 3440597, **subsidiary id 2 only**, read-only, no saved
searches. Validate column names with the SuiteQL metadata tool on first run —
the transactionline join shape varies by record family.

**a. Income by GL account, FYTD (posting-date basis, 1 Jul 2026 onward):**
```sql
SELECT a.acctnumber, a.fullname, SUM(tl.netamount) amt
FROM transactionline tl
JOIN transaction t ON t.id = tl.transaction
JOIN account a ON a.id = tl.expenseaccount
WHERE tl.subsidiary = 2 AND t.posting = 'T'
  AND t.trandate >= DATE '2026-07-01'
  AND a.accttype IN ('Income','OthIncome')
GROUP BY a.acctnumber, a.fullname
ORDER BY SUM(tl.netamount)
```
Feed the total into the tile beside the Salesforce Close-Date figure — the gap
between the two **is** the date-basis exhibit; label both bases.

**b. Income by department with the unmapped share (DQ-13):**
same query grouped by `t.department`; report
`unmapped % = rows where department IS NULL or name in ('_NOT_SPECIFIED','GEN_OVERHEAD')`.

**c. Bank account activity — 11103 NAT ABF Donations, 11104 NAT Operations:**
line counts and value by month since 2022-01-01, plus (if the reconciliation
fields prove queryable via metadata) unreconciled counts. If reconciliation
status is not exposed to SuiteQL, keep the documented figures (378 / 120,
last reconciled 31 Mar 2022) with their date labels — do not guess.

**d. Membership GL check:** 41001/41002 + 44023 totals FYTD — displayed on the
Membership page's finance strip and excluded from fundraising reconciliation
scope (documented discrepancy cause #2).

**e. Unreconciled income, live:** the full SF↔NS ±3-business-day match is the
exception Zap's job (`371228125`, still draft). Until it is published, refresh
the SF-side count from report `00ORF0000033T6z2AE`'s underlying filter and pair
it with (a) — present as "SF-side unreconciled" with the measurement date.

## 2. Update the page

Edit `dashboard/finance-dashboard.html`:
- Replace the three `chip pending`/`dated` panels with live values; every number
  keeps its basis caption (posting date vs Close Date).
- Update the `asof` line and the provenance footer.

## 3. Republish to the SAME artifact URL

From any session, publish the edited file passing the existing URL so the link
department heads hold keeps working:

- Artifact URL to pass as `url`:
  `https://claude.ai/code/artifact/73c13fb9-0307-4898-a631-9820a44e72b1`

Commit and push the edited HTML to the repo as well.

## 4. Make it recurring (one-time manual step)

Routines cannot have connectors attached via API in this org. In claude.ai →
Routines, attach **NetSuite** (alongside Salesforce Production) to whichever
routine refreshes dashboards — recommended: fold a weekly finance refresh into
the existing weekday ICT routine (`trig_0126KYAM3TAaZpBQKN8UeVdk`) rather than
creating a new scheduled job (the account was consolidated from 10 routines to
4 deliberately).

## 5. The two follow-ups this unlocks (from the model)

1. **Publish Zap `371228125`** — needs NetSuite Token-Based Auth credentials
   (integration record + consumer key/secret + token, user Mathew Hema,
   Administrator role). One credential set unblocks all NetSuite Zaps.
2. **Revoke-then-delete the orphaned OAuth2 certificate**
   (`7SCEnbQf…`, linked to departed staff, zero recorded activity, expires
   17 Sep 2026) — confirm with the NetSuite partner first, per the sequence
   prepared for the CFO on 20 Jul 2026.
