-- Oblast 06, lekcija 03: SQLite COUNT()
-- Teorija: ../../../06_sqlite_aggregate_functions/03_sqlite_COUNT_function.md
-- Svi blokovi su samo za čitanje. Pokreći ih nad chinook_practice.db.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/03_sqlite_COUNT_function.sql

-- @block Vežba 1: Redovi, popunjene kompanije i različite države
SELECT
    COUNT(*) AS all_customers,
    COUNT(Company) AS customers_with_company,
    COUNT(DISTINCT Country) AS distinct_countries
FROM customers;

-- Očekivano u ovoj kopiji: 59 | 10 | 24.

-- @block Vežba 2: Broj računa i različitih iznosa
SELECT
    COUNT(*) AS invoice_rows,
    COUNT(Total) AS totals_present,
    COUNT(DISTINCT Total) AS distinct_totals
FROM invoices;

-- Očekivano: 412 | 412 | 23.

-- @block Vežba 3: Broj numera po albumu
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
ORDER BY track_count DESC, AlbumId;

-- @block Ivični slučaj: prazan skup i samo NULL vrednosti
WITH empty(value) AS (
    SELECT NULL
    WHERE 0
),
all_null(value) AS (
    VALUES (NULL), (NULL)
)
SELECT 'empty' AS input_case, COUNT(*) AS row_count, COUNT(value) AS value_count
FROM empty
UNION ALL
SELECT 'all NULL', COUNT(*), COUNT(value)
FROM all_null;

-- Očekivano: empty | 0 | 0; all NULL | 2 | 0.

-- @block Ivični slučaj: nula, prazan tekst i uslovno brojanje
WITH sample(value, is_positive) AS (
    VALUES (NULL, 0), (0, 0), ('', 0), ('x', 0), (1, 1), (1, 1)
)
SELECT
    COUNT(*) AS all_rows,
    COUNT(value) AS non_null_values,
    COUNT(DISTINCT value) AS distinct_values,
    COUNT(CASE WHEN is_positive = 1 THEN 1 END) AS positive_values
FROM sample;

-- COUNT(value) broji 0 i prazan tekst; COUNT(CASE...) broji samo redove
-- za koje je uslov tačan.

-- @block Vežba 4: COUNT(*) u LEFT JOIN-u naspram broja poklopljenih albuma
SELECT
    ar.ArtistId,
    ar.Name,
    COUNT(*) AS joined_rows,
    COUNT(al.AlbumId) AS album_count
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
GROUP BY ar.ArtistId, ar.Name
ORDER BY ar.ArtistId;

-- Za izvođača bez albuma COUNT(*) je 1 zbog NULL-proširenog reda,
-- a COUNT(al.AlbumId) je 0.

-- @block Ivični slučaj: kolacija menja broj različitih tekstualnih vrednosti
WITH sample(value) AS (
    VALUES ('a'), ('A'), (NULL)
)
SELECT
    COUNT(DISTINCT value) AS binary_distinct_count,
    COUNT(DISTINCT value COLLATE NOCASE) AS nocase_distinct_count
FROM sample;

-- Očekivano: 2 | 1.
