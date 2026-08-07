# Power BI datasets from NetSuite and Salesforce

A refresh job that pulls both systems into CSVs Power BI can model, plus the schema
and measures for the two dashboards built on top.

| | |
|---|---|
| Queries | [`queries/`](queries/) — SuiteQL and SOQL, one file per dataset |
| Extract | [`extract/extract.py`](extract/extract.py) — runs them, writes CSVs |
| Model + DAX | [`measures.md`](measures.md) — star schema, measures, expected baselines |

The queries in this directory were run against the live NetSuite account and
Salesforce org on 7 August 2026 and returned the rows they claim to. They are not
templates to adapt.

---

## How the data gets to Power BI

```
NetSuite  ──SuiteQL/REST──┐
                          ├──→ extract.py ──→ out/*.csv ──→ Power BI (Folder) ──→ model ──→ report
Salesforce ──SOQL/REST────┘
```

`extract.py` runs every file in `queries/` and writes one CSV per query. Power BI
points at the output folder and refreshes from disk.

### Why files, not a live connection

This is the decision worth understanding, because the obvious answer is wrong for
one of the two systems.

**NetSuite.** Power BI's supported live path is **SuiteAnalytics Connect** — an
ODBC/JDBC add-on that is separately licensed and, at current list, costs more per
year than this entire reporting effort is worth to BirdLife. Without it there is no
sanctioned live connector. The SuiteQL REST endpoint used here is already enabled on
the account, costs nothing, and is what `extract.py` talks to. If finance ever buys
SuiteAnalytics Connect, the SQL in `queries/netsuite/` transfers over almost
unchanged.

**Salesforce.** Power BI *does* ship native Salesforce connectors, and for a simple
model they are fine. They are not used here for three reasons: the *Salesforce
Reports* connector caps at 2,000 rows, which the Case object blows through
immediately; the *Salesforce Objects* connector pulls whole objects with no SOQL, so
you cannot apply the `Ask Zeus` record-type filter at source and would drag all 19
record types across the wire; and using one connector for Salesforce and files for
NetSuite means two refresh mechanisms, two failure modes, and two things to explain.

One mechanism for both is worth more than a marginally slicker connector for one.

**What you give up:** freshness. This is a scheduled snapshot, not DirectQuery.
For a finance dashboard read weekly and a helpdesk queue of 20 open cases, daily is
comfortably enough. Say so on the page — put the extract timestamp in the footer.

---

## Setup

```bash
cd powerbi/extract
pip install -r requirements.txt
cp .env.example .env          # fill in — see the comments in that file
set -a && . ./.env && set +a
python extract.py --out ./out
```

Then in Power BI Desktop: **Get Data → Folder →** `powerbi/extract/out` **→ Combine
& Transform**, or add each CSV individually with **Get Data → Text/CSV** (clearer,
and you want the datasets modelled separately anyway).

Build the model and measures from [`measures.md`](measures.md), then check your
figures against the baseline table at the bottom of it. `Open Cases` should be **20**.

### Credentials

Both integrations need setting up once; the comments in `.env.example` say where.
Two rules:

- **Read-only.** The Salesforce connected app's run-as user gets a read-only profile;
  the NetSuite role gets REST Web Services and SuiteAnalytics Workbook, nothing more.
  This job never writes, so nothing it holds should be able to.
- **Environment, never a file in git.** `.gitignore` covers `.env` and the CSVs, but
  the real control is not pasting secrets anywhere they get persisted — a prompt, a
  routine definition, a commit message. The WooCommerce keys documented in the root
  README leaked exactly that way and still need rotating.

### Scheduling

Once it runs by hand, put it on a schedule that lands before people look:

- **Windows Task Scheduler** on a machine that's on overnight, or
- **A GitHub Actions workflow** with the credentials as repository secrets, writing
  to a storage account Power BI can read.

Then set the Power BI dataset to refresh after it. If the CSVs live on a local disk
or file share rather than OneDrive/SharePoint, scheduled refresh in the Power BI
service needs an **on-premises data gateway** — that is the usual thing people hit
after everything works on the desktop.

---

## Practice worth keeping

### Filter at source, not in the visual

Both queries constrain at the API: `RecordType.DeveloperName = 'Zeus'`,
`t.posting = 'T'`. Do it there, not in a Power BI filter pane, for three reasons —
less data over the wire, no chance of a report author removing the filter without
realising, and the constraint is visible in git rather than buried in a `.pbix`
nobody can diff.

This is the same defect the root README documents: ten Salesforce reports with no
record-type filter, inflating open cases by 217×. Filters that live inside a binary
report file are filters nobody reviews.

### State the scope on the page

Every dashboard page says what it was computed under — record type, date window,
posting status — and the footer says what's excluded. A wrong number is easy to
spot; a correct number under an unstated scope is what actually misleads people, and
it is precisely how the existing Zeus dashboards went wrong.

### Check the extract, not just the report

A silently empty or truncated extract renders as a healthy-looking dashboard with
small numbers. Two specific traps, both handled in `extract.py`:

- **NetSuite pagination is mandatory.** A single SuiteQL page stops at 1,000 rows and
  looks exactly like a complete result. The GL extract runs to tens of thousands of
  lines; `extract.py` follows `hasMore` to the end and prints a running count.
- **SuiteQL omits null columns per row.** Building the CSV header from the first row
  alone drops fields that happen to be blank early in the result — `department` and
  `class` are null on most lines here, so this is not hypothetical. The writer takes
  the union of keys across all rows.

Watch the row counts it prints. If the GL extract returns a suspiciously round
number, it truncated.

### Two reports, not one

Finance and ICT share no filters, no vocabulary, and no audience. One combined
report serves neither and doubles the surface where a wrong cross-filter can mislead.

---

## Known gaps

- **No join between the two systems.** There isn't one in the source data either —
  the ICT/finance linkage today is a hand-typed spreadsheet column
  (`ICT Priorities.xlsx`, at least four divergent copies). Don't invent a
  relationship in the model that doesn't exist in the data.
- **`department` and `class` are null on most GL lines**, including every AR Payment.
  Segment-level reporting will be sparse until coding discipline improves upstream —
  that is a finance process fix, not a Power BI one.
- **Salesforce has no field history on Case Status**, so time-in-status and true SLA
  compliance cannot be computed yet. Turning on Field History Tracking is already an
  Asana task (*Field History Tracking setup*, Kate Rogerson, Backlog). `MTTR Days` in
  `measures.md` is created-to-closed, which is the honest measure available today.
