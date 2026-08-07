-- NetSuite GL fact table — one row per posting transaction line, rolling 24 months.
-- Validated against the live account on 2026-08-07.
--
-- Notes on the SuiteQL dialect (it is Oracle, not T-SQL):
--   BUILTIN.DF(x)  resolves an internal ID to its display name. Without it you get
--                  bare integers for type, subsidiary, department, class, location.
--   SYSDATE - 730  is date arithmetic in days. There is no DATEADD.
--   t.posting='T'  restricts to lines that actually hit the general ledger, which is
--                  what makes this a GL extract rather than a list of documents.
--   ||             concatenates. + does not. There is no WITH/CTE support.
--
-- foreignamount is the transaction-currency amount. BirdLife is effectively
-- single-currency (AUD) in practice; if that changes, switch to tl.netamount for the
-- base-currency figure rather than converting in Power BI.

SELECT
    t.id                              AS transaction_id,
    t.tranid                          AS document_number,
    t.trandate                        AS transaction_date,
    BUILTIN.DF(t.type)                AS transaction_type,
    BUILTIN.DF(t.postingperiod)       AS posting_period,
    BUILTIN.DF(tl.subsidiary)         AS subsidiary,
    a.acctnumber                      AS account_number,
    a.accountsearchdisplayname        AS account_name,
    a.accttype                        AS account_type,
    BUILTIN.DF(tl.department)         AS department,
    BUILTIN.DF(tl.class)              AS class,
    BUILTIN.DF(tl.location)           AS location,
    tl.memo                           AS memo,
    tl.foreignamount                  AS amount
FROM transaction t
JOIN transactionline tl ON tl.transaction = t.id
JOIN account a          ON a.id = tl.account
WHERE t.posting = 'T'
  AND t.trandate >= SYSDATE - 730
