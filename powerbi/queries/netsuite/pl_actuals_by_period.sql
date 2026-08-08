-- P&L actuals aggregated to budget grain: period x account x department x class.
-- Validated 2026-08-07.
--
-- This is the actuals side of budget-vs-actual. It is deliberately separate from
-- gl_transaction_lines.sql, which stays at transaction-line grain for drill-down
-- and audit. Two facts, two jobs:
--
--   pl_actuals_by_period   compare against budget      (thousands of rows)
--   gl_transaction_lines   "what made up that number"  (tens of thousands)
--
-- Scope decisions worth knowing:
--   * P&L account types only. Budget-vs-actual is an operating-result question;
--     Bank, AcctRec and other balance-sheet accounts do not belong here.
--   * Rolling 36 months, so the prior full year is available for comparison
--     alongside the current one.
--   * Grouped on the posting period, not the transaction date. A transaction dated
--     31 Dec but posted to Jan belongs in Jan for budget purposes, and finance will
--     expect it there.
--
-- Sign convention: raw GL signs are preserved — income is negative, expense
-- positive. measures.md normalises both to positive magnitudes so budget lines can
-- be written the way finance writes them. Do not "fix" the sign here.
--
-- Department coverage on P&L lines is 99.9%; class coverage is 72.7% on expense and
-- 99.4% on income (measured over calendar 2026). Budget by department is sound.
-- Budget by class will carry an unallocated bucket on the expense side.

SELECT
    BUILTIN.DF(t.postingperiod)  AS period_name,
    a.acctnumber                 AS account_number,
    a.accountsearchdisplayname   AS account_name,
    a.accttype                   AS account_type,
    BUILTIN.DF(tl.department)    AS department,
    BUILTIN.DF(tl.class)         AS class,
    SUM(tl.foreignamount)        AS actual_amount
FROM transaction t
JOIN transactionline tl ON tl.transaction = t.id
JOIN account a          ON a.id = tl.account
WHERE t.posting = 'T'
  AND a.accttype IN ('Income', 'Expense', 'OthIncome', 'OthExpense', 'COGS')
  AND t.trandate >= SYSDATE - 1095
GROUP BY
    BUILTIN.DF(t.postingperiod),
    a.acctnumber,
    a.accountsearchdisplayname,
    a.accttype,
    BUILTIN.DF(tl.department),
    BUILTIN.DF(tl.class)
