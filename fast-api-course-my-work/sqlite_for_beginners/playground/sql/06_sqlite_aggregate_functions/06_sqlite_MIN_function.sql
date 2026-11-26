-- Oblast 06, lekcija 06: SQLite MIN()
-- Teorija: ../../../06_sqlite_aggregate_functions/06_sqlite_MIN_function.md
-- Svi blokovi su samo za čitanje. Pokreći ih nad chinook_practice.db.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/06_sqlite_MIN_function.sql

-- @block Vežba 1: Pronađi sve numere sa najkraćim trajanjem
SELECT TrackId, Name, AlbumId, Milliseconds
FROM tracks
WHERE Milliseconds = (
    SELECT MIN(Milliseconds)
    FROM tracks
)
ORDER BY TrackId;

-- U ovoj kopiji najkraća numera traje 1071 ms i ima TrackId 2461.

-- @block Ivični slučaj: celobrojni i decimalni minuti
SELECT
    MIN(Milliseconds) AS shortest_milliseconds,
    MIN(Milliseconds) / 60000 AS whole_minutes,
    MIN(Milliseconds) / 60000.0 AS exact_minutes
FROM tracks;

-- Očekivano: 1071 | 0 | 0.01785. Celobrojno deljenje skraćuje rezultat.

-- @block Vežba 2: Najkraće trajanje po albumu
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    MIN(Milliseconds) AS shortest_milliseconds
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;

-- @block Ivični slučaj: svi redovi sa istim minimumom
WITH sample(track_id, duration) AS (
    VALUES (1, 5), (2, 1), (3, 1)
)
SELECT track_id, duration
FROM sample
WHERE duration = (SELECT MIN(duration) FROM sample)
ORDER BY track_id;

-- Očekivano su vraćena oba reda sa trajanjem 1.

-- @block Ivični slučaj: NULL i DISTINCT
WITH sample(value) AS (
    VALUES (5), (1), (1), (NULL)
)
SELECT MIN(value), MIN(DISTINCT value)
FROM sample;

-- Oba izraza vraćaju 1; NULL se ignoriše.

-- @block Ivični slučaj: tekstualni redosled i mešani tipovi
WITH sample(value) AS (
    VALUES (100), ('9'), ('10'), (NULL)
)
SELECT MIN(value), typeof(MIN(value))
FROM sample;

-- Rezultat je numeričko 100: SQLite poredi storage klase i ne pretvara
-- tekstualne vrednosti '9' i '10' u brojeve.

-- @block Ivični slučaj: agregatni i skalarni min()
SELECT min(10, 20, 5) AS scalar_minimum;

SELECT min(10, NULL, 5) AS scalar_minimum_with_null;

-- Skalarni min() poredi argumente jednog reda; NULL argument daje NULL.
