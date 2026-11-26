-- Oblast 06, lekcija 05: SQLite MAX()
-- Teorija: ../../../06_sqlite_aggregate_functions/05_sqlite_MAX_function.md
-- Svi blokovi su samo za čitanje. Pokreći ih nad chinook_practice.db.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/05_sqlite_MAX_function.sql

-- @block Vežba 1: Najduže trajanje
SELECT
    MAX(Milliseconds) AS longest_milliseconds,
    MAX(Milliseconds) / 60000 AS whole_minutes,
    MAX(Milliseconds) / 60000.0 AS exact_minutes,
    ROUND(MAX(Milliseconds) / 60000.0, 2) AS rounded_minutes
FROM tracks;

-- Očekivano: 5286953 ms, 88 celih minuta i približno 88.12 minuta.

-- @block Vežba 2: Vrati redove koji imaju najduže trajanje
SELECT TrackId, Name, AlbumId, Milliseconds
FROM tracks
WHERE Milliseconds = (
    SELECT MAX(Milliseconds)
    FROM tracks
)
ORDER BY TrackId;

-- U ovoj kopiji rezultat je TrackId 2820, Occupation / Precipice.

-- @block Vežba 3: Najduže trajanje po albumu
SELECT
    AlbumId,
    MAX(Milliseconds) AS longest_milliseconds
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;

-- @block Ivični slučaj: zadrži sve redove koji dele maksimum
WITH sample(track_id, duration) AS (
    VALUES (1, 5), (2, 9), (3, 9)
)
SELECT track_id, duration
FROM sample
WHERE duration = (SELECT MAX(duration) FROM sample)
ORDER BY track_id;

-- Očekivano su vraćena oba reda sa trajanjem 9.

-- @block Ivični slučaj: NULL i DISTINCT
WITH sample(value) AS (
    VALUES (1), (1), (5), (NULL)
)
SELECT MAX(value), MAX(DISTINCT value)
FROM sample;

-- Oba izraza vraćaju 5; NULL se ignoriše.

-- @block Ivični slučaj: poređenje različitih storage klasa
WITH sample(value) AS (
    VALUES (100), ('9'), ('10'), (NULL)
)
SELECT MAX(value), typeof(MAX(value))
FROM sample;

-- Tekstualni '9' je posle broja 100 u SQLite redosledu tipova;
-- ne mešaj MAX() sa numeričkom validacijom podataka.

-- @block Ivični slučaj: agregatni i skalarni max()
SELECT max(10, 20, 5) AS scalar_maximum;

SELECT max(10, NULL, 5) AS scalar_maximum_with_null;

-- Skalarni max() poredi argumente jednog reda; NULL argument daje NULL.
