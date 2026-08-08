# Budget input

**Budget figures do not exist in NetSuite.** Verified 2026-08-07: there is no
`budget` record type in the SuiteQL catalogue, and the only two saved searches
matching "budget" are both `Transaction` searches — actuals sliced for comparison,
not budget records. So the budget comes in from outside, and this directory is where
it lands.

The finished file goes here as `budget.csv`. `extract.py` copies it into the output
folder so Power BI has one folder to point at.

---

## The workflow

```bash
cd powerbi/budget

# 1. Generate a skeleton for the year, seeded from the prior year's actuals
python budget_tool.py skeleton --year "FY 2027" --seed-from "FY 2026"

# 2. Send budget_skeleton.csv to finance. They edit the budget_amount column.

# 3. Check what comes back, before it goes anywhere near Power BI
python budget_tool.py validate --file budget_skeleton.csv

# 4. When it passes
mv budget_skeleton.csv budget.csv
```

`budget_tool.py` reads the CSVs `extract.py` already wrote. It needs no credentials
and no network access — run the extract first.

### Why generate rather than hand-fill

Three columns have to match NetSuite **exactly** — `period_name`, `account_number`,
`department`. A row that doesn't match contributes nothing, and the totals simply
come in low with nothing in the model to flag it. Generating the file from your own
chart of accounts removes that entire class of error before it happens.

There are 80 departments carrying 10–81 P&L accounts each, so a blank
account × department × month grid would run to thousands of rows nobody will fill
in honestly. Seeding from the prior year turns the job from *typing* into *editing*.

**Seeding is month-for-month, not an even spread.** January seeds January. BirdLife's
income is seasonal — the autumn appeal is not February's number — and a flat twelfth
would erase exactly the pattern that makes a monthly budget worth having.

> **Seeded figures are last year's actuals, not a budget.** They are a starting point
> for finance to edit. Nothing in this repo turns them into a forecast, and a
> skeleton shipped unreviewed is last year's spending wearing this year's label.

### Useful flags

| Flag | Effect |
|---|---|
| `--min-amount 0` | Include every combination, not just those over $1,000/yr |
| `--min-amount 25000` | Only material lines — a much shorter file to start from |
| *(omit `--seed-from`)* | Blank `budget_amount` column, structure only |
| `--out path.csv` | Write somewhere else |

---

## Columns

| Column | Must match | Notes |
|---|---|---|
| `period_name` | `accounting_periods[period_name]` exactly | `Jan 2026` — NetSuite's own period names, not `2026-01` |
| `account_number` | `chart_of_accounts[account_number]` | `41001`, `11200_NAT` — text, not a number |
| `department` | `pl_actuals_by_period[department]` | e.g. `Individual Giving` |
| `class` | `pl_actuals_by_period[class]` | Optional — leave blank to budget at department level |
| `budget_amount` | — | **Positive magnitude**, for both income and expense |

### Three things that will bite

**Sign.** Write budgets as positive numbers for both income and expense — the way
finance writes them. The GL stores income as negative, and `measures.md` flips the
actuals to match rather than asking you to flip the budget. `validate` warns on
negative amounts.

**Grain.** One row per period × account × department × class. If you budget at
department level, leave `class` blank — but be consistent, because a file mixing both
grains double-counts when class is on a slicer. `validate` warns on mixed grain.

**Excel and text columns.** `account_number` must be text. Excel will silently strip
a leading zero and mangle `11200_NAT` if the column is typed as General. Format the
column as Text before entering anything — and re-run `validate` after any round trip
through Excel, not just the first time.

---

## What `validate` checks

Errors (exit code 1 — fix before loading):

- `period_name` not matching a NetSuite period
- `account_number` with no P&L activity
- `department` not matching NetSuite
- duplicate period + account + department + class rows
- `budget_amount` that isn't a number

Warnings (exit code 0 — worth a look):

- negative `budget_amount`
- mixed department/class grain across the file
- a partially budgeted year, naming the missing months

It returns a non-zero exit code on errors, so it drops straight into whatever
scheduled job runs the extract.

---

## Checking it loaded correctly in Power BI

After the first refresh, put `Budget` and `Actual` on a table with no filters and
compare `Budget` against the finance-approved annual total. If it's out by a round
factor, the usual causes in order: a duplicated month, mixed grain, or a
`period_name` that didn't match.

Add `Unmatched Budget Rows` from [`../measures.md`](../measures.md) to a card while
building — it should read zero.
