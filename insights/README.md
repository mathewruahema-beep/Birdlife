# BirdLife Australia — Cross-Department Insights Model

A single, versioned definition of **what BirdLife measures, where each number comes
from, and what is known to distort it** — spanning every connected system, for every
department.

This is a *semantic model*, not a BI tool. It exists so that when Fundraising,
Finance, Membership, ICT, People & Culture or a programme team asks "how many / how
much / how fast", the answer is computed the same way every time, from the agreed
system of record, with the known data defects stated instead of silently absorbed.

## Why this exists

Three incidents proved the need:

1. **The ICT dashboards counted 4,344 open cases when the true number was 20** —
   an unstated record-type scope, not a wrong query (see repo root README).
2. **"Regular giving" has two homes** — NPSP Recurring Donations (1,778 active) and
   Payments2Us Recurring Payments (392 active). Any number quoted from one object is
   wrong, and both have been quoted.
3. **$671,117 of income sat unreconciled between Salesforce and NetSuite** (3 Jul
   2026, growing ~$87K/day) because the systems join by a manual monthly CSV and the
   detection Zap was never published.

The common failure is never arithmetic — it is **unstated scope, unagreed source of
record, and undocumented defects**. This model fixes that at the definition layer.

## Architecture — four layers

```
 L0  SOURCE SYSTEMS      Salesforce (Zeus) · NetSuite · Stripe · WooCommerce/WP
                         Employment Hero · M365/Entra · Asana · Ortto · Raisely
                         LearnUpon · Humanitix · Award Force · GA4 · Campaign Monitor
                         (Better Impact incoming)
        │  extraction: SOQL / SuiteQL / REST via MCP connectors & Zapier
        ▼
 L1  CANONICAL MODEL     Conformed dimensions (Supporter, Staff, GL Account,
                         Campaign, Membership Tier, Date, Channel) and facts
                         (gifts, payments, memberships, GL lines, cases, work
                         items, engagement events)        → 02-canonical-model.md
        │
        ▼
 L2  METRICS CATALOG     Department-owned metric definitions with source mapping,
                         grain, and known distortions      → 03-metrics-catalog.md
        │
        ▼
 L3  DELIVERY            Dashboards (artifact pattern per ict-dashboard), scheduled
                         routines, exception reports, board pack
```

The **data-quality register** (`04-data-quality-register.md`) cuts across all
layers: every defect lists the metrics it corrupts, so a dashboard builder can
check in one place what must be caveated or excluded.

## Design principles

1. **Scope is a visible design element.** Every metric states its filter (record
   type, subsidiary, date basis). This is the lesson of the ICT dashboard defect.
2. **One system of record per entity, ruled explicitly.** The ruling table is in
   `01-source-systems.md`. Where two systems disagree, the gap *is* the insight —
   report the discrepancy, don't average it away.
3. **Defects are stated, not absorbed.** A metric computed over a field that is 65%
   blank says so on the tile.
4. **Point-in-time figures are dated.** Every number in these documents carries its
   measurement date (Jun–Aug 2026 unless stated). Re-verify before re-quoting.
5. **Extraction leaves no artefacts.** SuiteQL over new saved searches (115 of 212
   existing ones have never been run); SOQL over new reports; read-only API calls.

## File map

| File | Contents |
|---|---|
| `01-source-systems.md` | System inventory, system-of-record rulings, extraction paths, cross-system key map |
| `02-canonical-model.md` | Conformed dimensions and facts, grains, identity resolution rules |
| `03-metrics-catalog.md` | Department-by-department metric definitions |
| `04-data-quality-register.md` | Known defects and the metrics each one corrupts |
| `sql/warehouse-schema.sql` | Target star schema DDL (portable ANSI SQL) |
| `sql/extraction-queries.md` | Canonical SOQL / SuiteQL / API queries per fact — the *only* sanctioned way to compute each base number |

## Implementation path (recommended, not yet built)

There is currently **no data warehouse**; the model is deliberately
platform-neutral. Pragmatic sequence:

1. **Now (no new infrastructure):** compute metrics live via the canonical queries
   in `sql/extraction-queries.md`, delivered through the existing scheduled-routine
   + artifact pattern already proven by the ICT dashboard.
2. **Next:** publish the drafted Zapier exception report (Zap `371228125`) — the
   cheapest win in the finance stack — and stand up the two or three highest-value
   department dashboards.
3. **Later:** if/when the Business Central migration is decided, the BC advisory
   already recommends Power BI from day one; this schema is the model to load. If
   BC does not proceed, the same DDL runs on any warehouse (the org already holds
   Cloudflare accounts where D1 is available for a lightweight start).

## Change control

Metric definitions are code. Changes to this model go through a PR on this repo
with the affected department named as reviewer. A metric whose definition changed
mid-series gets a new name or an annotated break — never a silent redefinition.
