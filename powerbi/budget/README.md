# Budget input

**Budget figures do not exist in NetSuite.** Verified 2026-08-07: there is no
`budget` record type in the SuiteQL catalogue, and the only two saved searches
matching "budget" are both `Transaction` searches — actuals sliced for comparison,
not budget records. So the budget has to come in from outside, and this directory is
where it lands.

Put the finance budget file here as `budget.csv`, matching the columns in
[`budget_template.csv`](budget_template.csv). Power BI reads it alongside the
extracted actuals.

---

## Columns

| Column | Must match | Notes |
|---|---|---|
| `period_name` | `accounting_periods[period_name]` exactly | `Jan 2026`, `Feb 2026` — NetSuite's own period names, not `2026-01` |
| `account_number` | `chart_of_accounts[account_number]` | `41001`, `11200_NAT` — text, not a number |
| `department` | `pl_actuals_by_period[department]` | e.g. `Individual Giving` |
| `class` | `pl_actuals_by_period[class]` | Optional — leave blank to budget at department level |
| `budget_amount` | — | **Positive magnitude**, for both income and expense |

### Two things that will bite

**Sign.** Write budgets as positive numbers for both income and expense — the way
finance writes them. The GL stores income as negative, and `measures.md` flips the
actuals to match rather than asking you to flip the budget. Do not enter negative
income budgets.

**Grain.** One row per period × account × department × class. If you budget at
department level only, leave `class` blank — but be consistent, because a file that
mixes both grains double-counts when class is on a slicer. Pick one and stick to it
for the whole year.

`account_number` must be text. Excel will silently strip a leading zero and turn
`11200_NAT` into something else if the column is typed as General — format the
column as Text before entering anything.

---

## Checking it loaded correctly

After the first refresh, put `Budget` and `Actual` on a table with no filters and
compare `Budget` against the finance-approved annual total. If it is out by a round
factor, the usual causes in order: a duplicated month, mixed grain (some rows with
class, some without), or a `period_name` that didn't match and silently dropped to
blank.

Add `Unmatched Budget Rows` from `measures.md` to a card on the page during
build — it should read zero. A budget row whose period or account doesn't match the
actuals will otherwise sit in the model contributing nothing and saying nothing.
