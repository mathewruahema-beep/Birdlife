-- NetSuite account dimension. 392 active accounts at 2026-08-07.
-- Joins to gl_transaction_lines on account_number.

SELECT
    a.id                        AS account_id,
    a.acctnumber                AS account_number,
    a.accountsearchdisplayname  AS account_name,
    a.accttype                  AS account_type,
    a.isinactive                AS is_inactive
FROM account a
WHERE a.isinactive = 'F'
