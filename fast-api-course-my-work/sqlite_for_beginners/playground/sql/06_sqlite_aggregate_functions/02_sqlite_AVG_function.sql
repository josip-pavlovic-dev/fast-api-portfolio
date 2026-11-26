-- Oblast 06, lekcija 02: SQLite AVG()
-- Teorija: ../../../06_sqlite_aggregate_functions/02_sqlite_AVG_function.md
-- Svi blokovi su samo za čitanje. Pokreći ih nad chinook_practice.db.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/02_sqlite_AVG_function.sql

-- @block Vežba 1: Prosek trajanja svih numera
SELECT
    AVG(Milliseconds) AS average_milliseconds,
    ROUND(AVG(Milliseconds) / 60000.0, 2) AS average_minutes
FROM tracks;

-- U ovoj kopiji prosek je približno 393599.21 ms.

-- @block Vežba 2: Prosek po albumu
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    ROUND(AVG(Milliseconds) / 60000.0, 2) AS average_minutes
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;

-- @block Ivični slučaj: celobrojno deljenje pre AVG() menja rezultat
SELECT
    AVG(Milliseconds) / 60000.0 AS average_after_averaging,
    AVG(Milliseconds / 60000) AS average_after_integer_division
FROM tracks
WHERE AlbumId = 1;

-- Za AlbumId 1 očekivani rezultati su približno 4.00069 i 3.5.

-- @block Ivični slučaj: NULL se ignoriše, nula se računa
WITH sample(value) AS (
    VALUES (0), (10), (NULL)
)
SELECT
    COUNT(*) AS input_rows,
    COUNT(value) AS values_counted,
    AVG(value) AS average_value
FROM sample;

-- Očekivano: 3 | 2 | 5.0.

-- @block Ivični slučaj: prazan ulaz naspram redova sa svim NULL vrednostima
WITH empty(value) AS (
    SELECT NULL
    WHERE 0
),
all_null(value) AS (
    VALUES (NULL), (NULL)
)
SELECT 'empty' AS input_case, COUNT(*) AS row_count, AVG(value) AS average
FROM empty
UNION ALL
SELECT 'all NULL', COUNT(*), AVG(value)
FROM all_null;

-- AVG() je NULL u oba slučaja; COUNT(*) razlikuje prazan ulaz od dva reda.

-- @block Ivični slučaj: DISTINCT i ponderisani prosek
WITH sample(group_id, value) AS (
    VALUES ('A', 10), ('B', 0), ('B', 0), ('B', 0)
),
group_averages AS (
    SELECT group_id, AVG(value) AS group_average, COUNT(value) AS value_count
    FROM sample
    GROUP BY group_id
)
SELECT
    (SELECT AVG(value) FROM sample) AS overall_average,
    (SELECT AVG(group_average) FROM group_averages) AS unweighted_group_average,
    (SELECT SUM(group_average * value_count) / SUM(value_count)
     FROM group_averages) AS weighted_group_average;

-- Očekivano: 2.5 | 5.0 | 2.5. Prosek grupnih proseka nije nužno
-- jednak ukupnom proseku ako grupe imaju različit broj vrednosti.

-- @block Ivični slučaj: SQLite konverzija tekstualnih vrednosti
WITH sample(value) AS (
    VALUES ('10'), ('not numeric'), (NULL)
)
SELECT COUNT(value) AS non_null_values, AVG(value) AS average_value
FROM sample;

-- U SQLite-u očekivano je 2 | 5.0; nebrojčani tekst učestvuje kao nula.
