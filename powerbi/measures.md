# Model and measures

Two datasets, two dashboards, one refresh job. Build them as separate Power BI
reports — the finance and helpdesk audiences share no filters and no vocabulary.

---

## Model

> **Correction, 2026-08-07.** An earlier version of this file built a synthetic date
> table with a July–June financial year, on the assumption that BirdLife follows the
> usual Australian convention. It does not. NetSuite's `accountingperiod` records
> show **FY 2026 = 1 Jan – 31 Dec 2026** and **Q1 2026 = Jan–Mar**. The fiscal year
> is the calendar year. Anything built on the old July–June logic would have put
> every figure in the wrong quarter and the wrong year.

Use **`netsuite_accounting_periods` as the period dimension**, not a generated
calendar. It comes from NetSuite, so "Jan 2026" here is the same Jan 2026 the ledger
was closed against, and month → quarter → year rolls up exactly as the GL does.

```
netsuite_accounting_periods[period_name] ──┬─→ netsuite_pl_actuals_by_period[period_name]
                                           └─→ budget[period_name]

Date[Date] ──┬─→ netsuite_gl_transaction_lines[transaction_date]
             └─→ salesforce_zeus_cases[CreatedDate]
```

Two period concepts, deliberately:

- **`netsuite_accounting_periods`** drives everything budget-related. Periods are
  discrete named buckets, and budget-vs-actual is a period question, not a
  daily-dates question.
- **`Date`** drives the daily-grain facts — GL drill-down and helpdesk cases —
  where you want real date intelligence.

```dax
Date =
VAR MinDate = MIN ( netsuite_gl_transaction_lines[transaction_date] )
VAR MaxDate = MAX ( netsuite_gl_transaction_lines[transaction_date] )
RETURN
ADDCOLUMNS (
    CALENDAR ( MinDate, MaxDate ),
    "Year",      YEAR ( [Date] ),
    "Quarter",   "Q" & QUARTER ( [Date] ) & " " & YEAR ( [Date] ),
    "Month",     FORMAT ( [Date], "mmm yyyy" ),
    "MonthSort", YEAR ( [Date] ) * 100 + MONTH ( [Date] )
)
```

Calendar quarters and calendar years, matching NetSuite. Mark it as the date table
(Modeling → Mark as date table). Sort `Month` by `MonthSort`, or the axis orders
alphabetically — Apr, Aug, Dec.

Sort order on the period dimension: set `period_name` to sort by `period_start`,
and `quarter_name` likewise. Without that, "Q1 2026" and "Q2 2026" sort fine but the
months inside them do not.

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

## Budget vs actual — month, quarter, year

Facts: `netsuite_pl_actuals_by_period` and `budget`, both joined to
`netsuite_accounting_periods` on `period_name`. Both relationships are
many-to-one, single direction, filtering from the period dimension.

### Normalising the sign

The GL stores income as negative and expense as positive. Finance writes budgets as
positive for both. Rather than asking anyone to enter negative income budgets, the
actual is flipped to match:

```dax
Actual =
SUMX (
    netsuite_pl_actuals_by_period,
    IF (
        netsuite_pl_actuals_by_period[account_type] IN { "Income", "OthIncome" },
        -1 * netsuite_pl_actuals_by_period[actual_amount],
        netsuite_pl_actuals_by_period[actual_amount]
    )
)

Budget = SUM ( budget[budget_amount] )
```

`Actual` is now a positive magnitude for both income and expense, directly
comparable to `Budget`.

### Variance

```dax
Variance   = [Actual] - [Budget]
Variance % = DIVIDE ( [Variance], [Budget] )
```

`Variance` is *not* self-describing, and this is the single most common way a
budget report misleads people: +$10k on income is good news, +$10k on expense is
bad news, and the number looks identical. Use the sign-aware measure for anything
with conditional formatting or a traffic light on it:

```dax
Variance (favourable) =
IF (
    SELECTEDVALUE ( netsuite_pl_actuals_by_period[account_type] ) IN { "Income", "OthIncome" },
    [Actual] - [Budget],   -- income: over budget is favourable
    [Budget] - [Actual]    -- expense: under budget is favourable
)
```

Positive is always good. Note it needs `account_type` in filter context — it returns
the expense reading on a total row mixing both, so put income and expense on
separate visuals or subtotal by account type.

### The three time windows

Month-to-month needs no measure — put `period_name` on the axis and the period
dimension does it.

```dax
-- Calendar quarter (Q1 2026 = Jan-Mar). Put quarter_name on the axis;
-- no measure needed either.

-- Rolling 3 months, if that is what "3 month" means rather than the quarter.
Actual Rolling 3M =
VAR MaxStart = MAX ( netsuite_accounting_periods[period_start] )
RETURN
CALCULATE (
    [Actual],
    ALL ( netsuite_accounting_periods ),
    netsuite_accounting_periods[period_start] <= MaxStart,
    netsuite_accounting_periods[period_start] > EDATE ( MaxStart, -3 )
)

-- Year to date, Jan-Dec. year_name is NetSuite's FY, which is the calendar year.
Actual YTD =
VAR ThisYear = SELECTEDVALUE ( netsuite_accounting_periods[year_name] )
VAR MaxStart = MAX ( netsuite_accounting_periods[period_start] )
RETURN
CALCULATE (
    [Actual],
    ALL ( netsuite_accounting_periods ),
    netsuite_accounting_periods[year_name] = ThisYear,
    netsuite_accounting_periods[period_start] <= MaxStart
)

Budget YTD =
VAR ThisYear = SELECTEDVALUE ( netsuite_accounting_periods[year_name] )
VAR MaxStart = MAX ( netsuite_accounting_periods[period_start] )
RETURN
CALCULATE (
    [Budget],
    ALL ( netsuite_accounting_periods ),
    netsuite_accounting_periods[year_name] = ThisYear,
    netsuite_accounting_periods[period_start] <= MaxStart
)

Variance YTD   = [Actual YTD] - [Budget YTD]
Variance YTD % = DIVIDE ( [Variance YTD], [Budget YTD] )
```

`TOTALYTD` and friends are deliberately not used — they need a marked date table,
and the period dimension is a named-bucket dimension, not a date table. Filtering on
`year_name` is both simpler and guaranteed to agree with NetSuite's year-end.

### Full-year budget vs YTD actual

The comparison finance will ask for by March: how are we tracking against the whole
year, not just the months elapsed.

```dax
Budget Full Year =
VAR ThisYear = SELECTEDVALUE ( netsuite_accounting_periods[year_name] )
RETURN
CALCULATE (
    [Budget],
    ALL ( netsuite_accounting_periods ),
    netsuite_accounting_periods[year_name] = ThisYear
)

Budget Consumed % = DIVIDE ( [Actual YTD], [Budget Full Year] )
```

Read `Budget Consumed %` against elapsed time: 50% consumed at the end of June is on
track; 50% at the end of March is not.

### Data-quality guard — put this on a card while building

```dax
Unmatched Budget Rows =
COUNTROWS (
    FILTER (
        budget,
        ISBLANK (
            LOOKUPVALUE (
                netsuite_accounting_periods[period_name],
                netsuite_accounting_periods[period_name], budget[period_name]
            )
        )
    )
)
```

Should be zero. A budget row whose `period_name` doesn't match — `2026-01` instead of
`Jan 2026`, a stray space, a year that hasn't been set up in NetSuite yet — silently
contributes nothing and the totals just come in low. Nothing else in the model will
tell you.

### Known limits, worth stating on the page

- **Class coverage on expense is 72.7%** (calendar 2026). Budget-vs-actual by class
  will show an unallocated bucket on expense; by department it is 99.9% and sound.
- **Budget is a snapshot, not a live figure.** It is whatever was last dropped in
  `powerbi/budget/budget.csv`. Show the file's date on the page — a revised forecast
  that never made it into the folder is invisible otherwise.
- **The current period is partial.** The latest month will always look under budget
  until it closes. Either exclude open periods (`is_closed = 'F'`) from the default
  view or label them.

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
