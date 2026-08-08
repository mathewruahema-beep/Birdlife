#!/usr/bin/env python3
"""Generate and validate the budget CSV that budget-vs-actual depends on.

Budget figures are not in NetSuite (no budget record type exists in the SuiteQL
catalogue), so finance supplies them as a file. Hand-typing period names, account
numbers and department names that must match NetSuite exactly is the single most
likely way this goes wrong — a mismatched row contributes nothing and the totals
just come in low, with nothing in the model to tell you.

Both subcommands read the CSVs that extract.py already wrote. Neither needs
credentials or network access.

    # Build next year's skeleton, seeded from this year's actuals month-for-month
    python budget_tool.py skeleton --year "FY 2027" --seed-from "FY 2026"

    # Check finance's completed file before it goes near Power BI
    python budget_tool.py validate --file budget.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_EXTRACT = HERE.parent / "extract" / "out"

PERIODS_CSV = "netsuite_accounting_periods.csv"
ACTUALS_CSV = "netsuite_pl_actuals_by_period.csv"

COLUMNS = ["period_name", "account_number", "department", "class", "budget_amount"]

# The GL stores income as a credit (negative). Finance writes budgets as positive
# magnitudes for both income and expense, and measures.md flips the actuals to
# match — so seeded figures are flipped here too, for the same reason.
INCOME_TYPES = {"Income", "OthIncome"}


def load_csv(directory: Path, name: str) -> list[dict]:
    path = directory / name
    if not path.exists():
        sys.exit(
            f"Missing {path}.\n"
            f"Run the extract first:  cd ../extract && python extract.py --out ./out"
        )
    # utf-8-sig: extract.py writes a BOM so Excel opens the files cleanly, and
    # csv.DictReader would otherwise fold it into the first column name.
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalise(amount: str, account_type: str) -> float:
    try:
        value = float(amount or 0)
    except ValueError:
        return 0.0
    return -value if account_type in INCOME_TYPES else value


def months_of(periods: list[dict], year: str) -> list[dict]:
    """Months belonging to one year, in calendar order."""
    rows = [p for p in periods if p["year_name"] == year]
    return sorted(rows, key=lambda p: p["period_start"])


# --------------------------------------------------------------------------- #

def cmd_skeleton(args: argparse.Namespace) -> int:
    periods = load_csv(args.extract, PERIODS_CSV)
    actuals = load_csv(args.extract, ACTUALS_CSV)

    target = months_of(periods, args.year)
    if not target:
        years = sorted({p["year_name"] for p in periods})
        sys.exit(f"No periods found for {args.year!r}. Available: {', '.join(years)}")

    seed_months = months_of(periods, args.seed_from) if args.seed_from else []
    if args.seed_from and not seed_months:
        sys.exit(f"No periods found for seed year {args.seed_from!r}")

    # Map seed month -> target month by position, so January seeds January. Seasonality
    # is real here — the autumn appeal is not the same size as February — and an even
    # 1/12 spread would erase it.
    seed_for = {
        target[i]["period_name"]: seed_months[i]["period_name"]
        for i in range(min(len(target), len(seed_months)))
    }

    # (account, department) -> {period_name: normalised amount}
    by_combo: dict[tuple[str, str, str], dict[str, float]] = defaultdict(dict)
    totals: dict[tuple[str, str, str], float] = defaultdict(float)
    for row in actuals:
        key = (row["account_number"], row["account_name"], row["department"] or "")
        value = normalise(row["actual_amount"], row["account_type"])
        by_combo[key][row["period_name"]] = by_combo[key].get(row["period_name"], 0.0) + value
        if row["period_name"] in seed_for.values():
            totals[key] += abs(value)

    combos = sorted(
        (k for k in by_combo if totals[k] >= args.min_amount),
        key=lambda k: (k[2], k[0]),
    )
    dropped = len(by_combo) - len(combos)

    rows = []
    for account_number, _account_name, department in combos:
        for month in target:
            seeded = ""
            source_month = seed_for.get(month["period_name"])
            if source_month:
                value = by_combo[(account_number, _account_name, department)].get(source_month)
                if value is not None:
                    seeded = f"{round(value, 2)}"
            rows.append({
                "period_name": month["period_name"],
                "account_number": account_number,
                "department": department,
                "class": "",
                "budget_amount": seeded,
            })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"→ {args.out}")
    print(f"  {len(combos)} account × department combinations × {len(target)} months "
          f"= {len(rows)} rows")
    if args.seed_from:
        filled = sum(1 for r in rows if r["budget_amount"] != "")
        print(f"  seeded {filled} rows from {args.seed_from} (same month, prior year)")
    if dropped:
        print(f"  dropped {dropped} combinations under the ${args.min_amount:,.0f} "
              f"materiality threshold — lower --min-amount to include them")
    print("\n  Seeded figures are LAST YEAR'S ACTUALS, not a budget. They are a "
          "starting point\n  for finance to edit, not a forecast. Review every line "
          "before use.")
    return 0


# --------------------------------------------------------------------------- #

def cmd_validate(args: argparse.Namespace) -> int:
    periods = load_csv(args.extract, PERIODS_CSV)
    actuals = load_csv(args.extract, ACTUALS_CSV)
    budget = load_csv(args.file.parent, args.file.name)

    valid_periods = {p["period_name"] for p in periods}
    valid_accounts = {a["account_number"] for a in actuals}
    valid_departments = {a["department"] for a in actuals if a["department"]}

    problems: list[str] = []
    warnings: list[str] = []

    missing_columns = [c for c in COLUMNS if c not in (budget[0] if budget else {})]
    if missing_columns:
        sys.exit(f"budget file is missing required columns: {', '.join(missing_columns)}")

    seen: dict[tuple, int] = {}
    with_class = without_class = 0

    for line_no, row in enumerate(budget, start=2):
        period = (row.get("period_name") or "").strip()
        account = (row.get("account_number") or "").strip()
        department = (row.get("department") or "").strip()
        klass = (row.get("class") or "").strip()
        amount_raw = (row.get("budget_amount") or "").strip()

        if period not in valid_periods:
            problems.append(
                f"line {line_no}: period_name {period!r} does not match any NetSuite "
                f"period (expected e.g. 'Jan 2026')")
        if account and account not in valid_accounts:
            problems.append(
                f"line {line_no}: account_number {account!r} has no P&L activity — "
                f"check for a stripped leading zero or a balance-sheet account")
        if department and department not in valid_departments:
            problems.append(
                f"line {line_no}: department {department!r} does not match NetSuite")

        if amount_raw:
            try:
                amount = float(amount_raw)
            except ValueError:
                problems.append(f"line {line_no}: budget_amount {amount_raw!r} is not a number")
            else:
                if amount < 0:
                    warnings.append(
                        f"line {line_no}: negative budget_amount ({amount}). Budgets are "
                        f"positive magnitudes for income AND expense — see README.md")

        key = (period, account, department, klass)
        if key in seen:
            problems.append(f"line {line_no}: duplicate of line {seen[key]} — this "
                            f"double-counts")
        else:
            seen[key] = line_no

        if klass:
            with_class += 1
        else:
            without_class += 1

    if with_class and without_class:
        warnings.append(
            f"mixed grain: {with_class} rows specify a class and {without_class} do not. "
            f"This double-counts when class is on a slicer — pick one grain for the "
            f"whole file")

    budgeted_periods = {(r.get("period_name") or "").strip() for r in budget}
    for year in sorted({p["year_name"] for p in periods if p["period_name"] in budgeted_periods}):
        expected = {p["period_name"] for p in periods if p["year_name"] == year}
        missing = expected - budgeted_periods
        if missing and len(missing) < len(expected):
            warnings.append(
                f"{year}: no budget rows for {', '.join(sorted(missing))} — those months "
                f"will show 100% favourable variance on expense")

    print(f"Checked {len(budget)} rows in {args.file}\n")
    for warning in warnings:
        print(f"  warning  {warning}")
    for problem in problems:
        print(f"  ERROR    {problem}")

    if problems:
        print(f"\n{len(problems)} error(s). Fix these before loading into Power BI — "
              f"each one silently contributes nothing to the totals.")
        return 1
    print(f"\nNo errors{' (see warnings above)' if warnings else ''}. "
          f"Safe to copy to budget.csv and refresh.")
    return 0


# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--extract", type=Path, default=DEFAULT_EXTRACT,
                        help="directory holding extract.py output (default ../extract/out)")
    sub = parser.add_subparsers(dest="command", required=True)

    skeleton = sub.add_parser("skeleton", help="generate a budget file to fill in")
    skeleton.add_argument("--year", required=True, help='target year, e.g. "FY 2027"')
    skeleton.add_argument("--seed-from", help='prior year to seed amounts from, e.g. "FY 2026"')
    skeleton.add_argument("--min-amount", type=float, default=1000.0,
                          help="omit combinations under this absolute annual total "
                               "(default 1000; use 0 for everything)")
    skeleton.add_argument("--out", type=Path, default=HERE / "budget_skeleton.csv")
    skeleton.set_defaults(func=cmd_skeleton)

    validate = sub.add_parser("validate", help="check a completed budget file")
    validate.add_argument("--file", type=Path, default=HERE / "budget.csv")
    validate.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
