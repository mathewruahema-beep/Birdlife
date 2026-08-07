# Model and measures

Two datasets, two dashboards, one refresh job. Build them as separate Power BI
reports — the finance and helpdesk audiences share no filters and no vocabulary.

---

## Model

Both models are star schemas with a **shared date table**. Create it once, mark it as
the date table (Modeling → Mark as date table), and relate it to each fact.

```
Date[Date] ──┬─→ netsuite_gl_transaction_lines[transaction_date]
             └─→ salesforce_zeus_cases[CreatedDate]
```

```dax
Date =
VAR MinDate = MIN ( netsuite_gl_transaction_lines[transaction_date] )
VAR MaxDate = MAX ( netsuite_gl_transaction_lines[transaction_date] )
RETURN
ADDCOLUMNS (
    CALENDAR ( MinDate, MaxDate ),
    "Year",         YEAR ( [Date] ),
    "Month",        FORMAT ( [Date], "mmm yyyy" ),
    "MonthSort",    YEAR ( [Date] ) * 100 + MONTH ( [Date] ),
    "FY",           "FY" & IF ( MONTH ( [Date] ) >= 7, YEAR ( [Date] ) + 1, YEAR ( [Date] ) ),
    "FYMonthNo",    IF ( MONTH ( [Date] ) >= 7, MONTH ( [Date] ) - 6, MONTH ( [Date] ) + 6 )
)
```

Australian financial year runs July–June, so `FY` and `FYMonthNo` are what finance
will actually ask for. Sort the `Month` column by `MonthSort` or the axis orders
alphabetically.

`netsuite_chart_of_accounts[account_number]` → `netsuite_gl_transaction_lines[account_number]`
is a one-to-many relationship; use the dimension for slicers so accounts with no
activity in the period still appear.

---

## NetSuite — finance dashboard

```dax
Total Amount = SUM ( netsuite_gl_transaction_lines[amount] )

-- The GL is signed: income is negative, expense positive. Finance wants both
-- shown as positive magnitudes, which is the single most common cause of a
-- "the dashboard is wrong" conversation.
Income  = -1 * CALCULATE ( [Total Amount], netsuite_chart_of_accounts[account_type] = "Income" )
Expense =      CALCULATE ( [Total Amount], netsuite_chart_of_accounts[account_type] = "Expense" )

Net Surplus = [Income] - [Expense]

Bank Balance =
CALCULATE (
    [Total Amount],
    netsuite_chart_of_accounts[account_type] = "Bank",
    FILTER ( ALL ( 'Date' ), 'Date'[Date] <= MAX ( 'Date'[Date] ) )
)

Income YoY % =
VAR Current = [Income]
VAR Prior   = CALCULATE ( [Income], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
RETURN DIVIDE ( Current - Prior, Prior )
```

`Bank Balance` is cumulative by design — a balance-sheet account is a running total,
not a period sum. Every other measure here is a period figure.

**Scope warning, same class as the one this repo was built to fix.** The extract is
rolling 24 months and posting lines only. Any figure on this dashboard is
period-limited and excludes non-posting documents (quotes, unapproved bills). Put
that on the page, in the footer, in words — a correct number under an unstated scope
is how the Zeus dashboards went wrong in the first place.

---

## Salesforce — Ask Zeus helpdesk dashboard

Every measure below is already scoped to the `Ask Zeus` record type, because the
extract query filters on it. Do not add cases from any other source to this model.

```dax
Cases = COUNTROWS ( salesforce_zeus_cases )

Open Cases   = CALCULATE ( [Cases], salesforce_zeus_cases[IsClosed] = FALSE )
Closed Cases = CALCULATE ( [Cases], salesforce_zeus_cases[IsClosed] = TRUE )

-- Real mean time to resolution, in days. The report currently labelled
-- "MTTR by Agent" is a count of closed cases, not a duration.
MTTR Days =
AVERAGEX (
    FILTER ( salesforce_zeus_cases, NOT ISBLANK ( salesforce_zeus_cases[ClosedDate] ) ),
    DATEDIFF ( salesforce_zeus_cases[CreatedDate], salesforce_zeus_cases[ClosedDate], DAY )
)

-- The data-quality measure. Drive it to zero and every category report
-- becomes trustworthy.
Untyped Open Cases =
CALCULATE ( [Cases], salesforce_zeus_cases[IsClosed] = FALSE, ISBLANK ( salesforce_zeus_cases[Type] ) )

Type Completeness % =
DIVIDE ( [Cases] - CALCULATE ( [Cases], ISBLANK ( salesforce_zeus_cases[Type] ) ), [Cases] )

-- Identity lifecycle: 20% of volume, and the automation target.
Identity Lifecycle Cases =
CALCULATE ( [Cases], salesforce_zeus_cases[Type] IN { "IAM", "New User", "Departing Staff" } )

Identity Lifecycle % = DIVIDE ( [Identity Lifecycle Cases], [Cases] )

Ageing Open Cases =
CALCULATE (
    [Cases],
    salesforce_zeus_cases[IsClosed] = FALSE,
    FILTER ( salesforce_zeus_cases,
        DATEDIFF ( salesforce_zeus_cases[CreatedDate], TODAY (), DAY ) > 30 )
)

Unassigned Cases = CALCULATE ( [Cases], salesforce_zeus_cases[Owner.Name] = "Zeus" )
```

`Owner.Name = "Zeus"` is the **unassigned intake queue, not a person.** Any "cases by
agent" visual that leaves it in will show a phantom top performer. Exclude it from
per-agent charts and give it its own tile.

Baseline at 7 Aug 2026, from the live org — use these to check the model is right
when you first load it:

| Measure | Expected |
|---|---:|
| Open Cases | 20 |
| Open, status New | 8 |
| Untyped Open Cases | 13 |
| Cases, last 365 days | 870 |
| Identity Lifecycle %, last 365 days | 20% |
| Origin = Email, last 365 days | 96.8% |

If `Open Cases` comes back in the thousands, the record-type filter has been lost
somewhere — that is the 217× inflation this repo documents, not a data problem.
