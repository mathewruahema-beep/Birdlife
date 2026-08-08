-- Period dimension: one row per accounting month, with its quarter and year.
-- Validated 2026-08-07 — 24 months from Jan 2026, 68 period records in total.
--
-- This replaces a synthetic DAX calendar. Use NetSuite's own periods, because they
-- are what finance closes on: "Jan 2026" here is the same Jan 2026 the ledger was
-- closed against, and month/quarter/year roll up exactly as the GL does.
--
-- BirdLife's fiscal year is the CALENDAR year — FY 2026 runs 1 Jan to 31 Dec 2026,
-- Q1 2026 is Jan-Mar. This is confirmed from the accountingperiod records, not
-- assumed; do not apply the Australian July-June convention here.
--
-- accountingperiod is self-referencing: month.parent = quarter, quarter.parent =
-- year. Power BI will not roll a self-referencing hierarchy up on its own without
-- PATH() gymnastics, so the two self-joins below flatten it into plain columns.
--
-- isadjust = 'F' drops adjustment periods, which would otherwise double-count.

SELECT
    m.periodname    AS period_name,
    m.startdate     AS period_start,
    m.enddate       AS period_end,
    q.periodname    AS quarter_name,
    y.periodname    AS year_name,
    m.closed        AS is_closed
FROM accountingperiod m
JOIN accountingperiod q ON q.id = m.parent
JOIN accountingperiod y ON y.id = q.parent
WHERE m.isquarter = 'F'
  AND m.isyear    = 'F'
  AND m.isadjust  = 'F'
