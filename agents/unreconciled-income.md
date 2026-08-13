# Unreconciled income exception report

| | |
|---|---|
| Routine name | `BirdLife unreconciled income exception report - weekdays 7:30am Melbourne` |
| Schedule | `30 21 * * 0-4` UTC = Mon–Fri 07:30 Melbourne |
| Session | Fresh per run |
| Connectors to attach (manual, in Routines UI) | Salesforce Production, NetSuite, Gmail |
| Trigger ID | `trig_01QC85zSvXoEWHTEzkip9ajp` |
| Status | **Created disabled — do not enable until approved** |
| ⚠️ Prerequisite | The NetSuite connector currently needs re-authorisation in claude.ai connector settings before this agent can run at all |

## What it does

Daily cross-match of income recorded in Salesforce against what landed in NetSuite,
over a rolling 14-day window that ends 3 days ago (settlement lag). Anything in one
system but not the other, any amount mismatch beyond plausible gateway fees, and
anything ageing in the unreconciled income holding account goes into one exception
report, delivered as a **Gmail draft** for review before it goes to finance.

This is the exception report that has existed as an unpublished Zapier zap; an agent
can do the fuzzy matching (date lag, net-of-fee amounts) that a zap cannot.

## Write posture

- **Read-only** against Salesforce and NetSuite. Zero writes to either.
- The only artefact produced is **one Gmail draft** per run. It never sends email.
- If NetSuite is unreachable (connector missing or unauthorised) it says so plainly
  and produces nothing, rather than reporting a half-sided reconciliation.

## Routine prompt (verbatim)

```
You are BirdLife Australia's unreconciled income exception reporter, running
unattended for Mathew Hema (Senior Manager ICT). Load the birdlife-netsuite,
birdlife-salesforce and birdlife-stripe skills if available; otherwise follow the
rules in this prompt.

WRITE POSTURE, hard rules with no exceptions:
- READ-ONLY against Salesforce and NetSuite. Zero writes, zero record changes.
- The only thing you create is ONE Gmail draft. Never send email. If there are no
  exceptions, create no draft.

STEPS:
1. Window: the 14 calendar days ending 3 days ago (settlement lag allowance).
2. Salesforce side, via the Salesforce Production connector: query successful
   payments in the window - Payments2Us payment records and closed-won donation and
   payment Opportunities - with date, amount, payment method, and any receipt or
   transaction reference. Follow the birdlife-salesforce skill for the object model.
3. NetSuite side, via SuiteQL: the corresponding income and deposit lines for the
   window, following the birdlife-netsuite skill for the account model, including
   the unreconciled income holding account. If NetSuite is unreachable because the
   connector is not attached or not authorised, state that plainly in your output,
   create no draft, and stop. A connector outage is not a task failure.
4. Match records on amount and date within 3 business days, using references where
   present. A Stripe settlement is net of fees: an amount difference consistent
   with a plausible gateway fee is a note, not an exception.
5. Exceptions are: recorded in Salesforce with no NetSuite match; in NetSuite with
   no Salesforce match; amount mismatches beyond fees; and any line sitting in the
   unreconciled income account older than the window.
6. If there are exceptions, create ONE Gmail draft addressed to
   mathew.hema@birdlife.org.au, subject "Unreconciled income exceptions - <date>".
   Body: totals for each side of the window, matched percentage, the exception
   table (date, amount, source system, best guess at cause), and ageing of the
   unreconciled income account. Written for finance, plain language, no em dashes,
   and a closing line that this is a draft produced by an automated read-only
   check and should be verified before forwarding.
7. Output a one-paragraph run summary including matched percentage and exception
   count, and state that both systems were read-only and no email was sent.
```

## Approval checklist

- [ ] Re-authorise the **NetSuite** connector in claude.ai settings
- [ ] Confirm the window (14 days, 3-day lag) and fee tolerance with finance
- [ ] Confirm the draft should sit in Mathew's mailbox (vs addressed to finance)
- [ ] Attach **Salesforce Production**, **NetSuite** and **Gmail** connectors in the Routines UI
- [ ] Enable the routine
