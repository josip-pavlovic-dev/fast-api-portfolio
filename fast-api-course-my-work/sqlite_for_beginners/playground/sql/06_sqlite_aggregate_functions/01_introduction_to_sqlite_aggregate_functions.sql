-- Oblast 06, lekcija 01: Uvod u SQLite agregatne funkcije
-- Teorija: ../../../06_sqlite_aggregate_functions/01_introduction_to_sqlite_aggregate_functions.md
-- Svi blokovi su samo za čitanje. Pokreći ih nad chinook_practice.db.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/01_introduction_to_sqlite_aggregate_functions.sql

-- @block Vežba 1: Više agregata nad svim računima
SELECT
    COUNT(*) AS invoice_rows,
    COUNT(Total) AS totals_present,
    SUM(Total) AS total_sum,
    AVG(Total) AS average_total,
    MIN(Total) AS minimum_total,
    MAX(Total) AS maximum_total
FROM invoices;

-- U ovoj kopiji očekivano je 412 računa, zbir 2328.6, minimum 0.99
-- i maksimum 25.86. Prosek i zbir zavise od podataka u kopiji.

-- @block Vežba 2: Agregati po državi
SELECT
    BillingCountry,
    COUNT(*) AS invoice_count,
    ROUND(SUM(Total), 2) AS invoice_total,
    ROUND(AVG(Total), 2) AS average_invoice
FROM invoices
GROUP BY BillingCountry
ORDER BY invoice_count DESC, BillingCountry
LIMIT 10;

-- @block Ivični slučaj: COUNT i AVG nad vrednostima sa NULL
WITH sample(value) AS (
    VALUES (10), (20), (NULL)
)
SELECT
    COUNT(*) AS input_rows,
    COUNT(value) AS non_null_values,
    SUM(value) AS total,
    AVG(value) AS average
FROM sample;

-- Očekivano: 3 reda, 2 nenulte vrednosti, zbir 30 i prosek 15.0.
-- NULL se ignoriše u SUM/AVG i u COUNT(value), ali ga COUNT(*) broji.
