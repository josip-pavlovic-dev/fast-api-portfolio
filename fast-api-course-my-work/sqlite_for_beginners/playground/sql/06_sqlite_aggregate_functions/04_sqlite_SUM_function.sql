-- Oblast 06, lekcija 04: SQLite SUM()
-- Teorija: ../../../06_sqlite_aggregate_functions/04_sqlite_SUM_function.md
-- Svi blokovi su samo za čitanje. Pokreći ih nad chinook_practice.db.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/04_sqlite_SUM_function.sql

-- @block Vežba 1: Ukupna vrednost računa
SELECT SUM(Total) AS invoice_total
FROM invoices;

-- Očekivano u ovoj kopiji: 2328.6.

-- @block Vežba 2: Zbir trajanja po albumu
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    SUM(Milliseconds) AS total_milliseconds,
    SUM(Milliseconds) / 60000 AS whole_minutes,
    ROUND(SUM(Milliseconds) / 60000.0, 2) AS precise_minutes
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;

-- @block Ivični slučaj: prazan skup i svi NULL argumenti
WITH empty(value) AS (
    SELECT 1
    WHERE 0
),
all_null(value) AS (
    VALUES (NULL), (NULL)
)
SELECT 'empty' AS input_case, SUM(value) AS sum_value, TOTAL(value) AS total_value
FROM empty
UNION ALL
SELECT 'all NULL', SUM(value), TOTAL(value)
FROM all_null;

-- SUM() vraća NULL; SQLite TOTAL() vraća 0.0.

-- @block Ivični slučaj: ALL i DISTINCT
WITH sample(value) AS (
    VALUES (1), (1), (NULL)
)
SELECT
    SUM(value) AS default_all,
    SUM(ALL value) AS explicit_all,
    SUM(DISTINCT value) AS distinct_values
FROM sample;

-- Očekivano: 2 | 2 | 1.

-- @block Ivični slučaj: floating-point vrednosti su približne
WITH sample(value) AS (
    VALUES (0.1), (0.2)
)
SELECT SUM(value) AS approximate_sum, typeof(SUM(value)) AS result_type
FROM sample;

-- Rezultat može biti prikazan kao 0.30000000000000004; tip je real.

-- @block Ivični slučaj: SQLite tekstualna konverzija
WITH sample(value) AS (
    VALUES ('10'), ('not numeric'), (NULL)
)
SELECT SUM(value) AS total
FROM sample;

-- U SQLite-u očekivani rezultat je 10.0; nebrojčani tekst učestvuje kao 0.0.

-- Napomena: integer-overflow primer iz teorije namerno nije automatski pokrenut
-- u ovom fajlu, jer bi prijavio grešku. Isprobaj ga odvojeno u :memory: bazi.
