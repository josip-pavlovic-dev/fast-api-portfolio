-- Oblast 06, lekcija 07: SQLite GROUP_CONCAT()
-- Teorija: ../../../06_sqlite_aggregate_functions/07_sqlite_GROUP_CONCAT_function.md
-- Svi blokovi su samo za čitanje. Pokreći ih nad chinook_practice.db.
-- ORDER BY unutar agregata zahteva SQLite 3.44.0 ili noviji.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/07_sqlite_GROUP_CONCAT_function.sql

-- @block Vežba 1: Podrazumevana lista numera za album 10
SELECT GROUP_CONCAT(Name) AS track_names
FROM tracks
WHERE AlbumId = 10;

-- Album 10 ima 14 numera. Bez unutrašnjeg ORDER BY njihov redosled nije garantovan.

-- @block Vežba 2: Prilagođeni separator i deterministički redosled
SELECT GROUP_CONCAT(Name, ', ' ORDER BY TrackId) AS track_names
FROM tracks
WHERE AlbumId = 10;

-- @block Vežba 3: Lista numera po albumu
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    GROUP_CONCAT(Name, ', ' ORDER BY Name, TrackId) AS track_names
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;

-- @block Ivični slučaj: NULL se preskače, prazan tekst se zadržava
WITH sample(value) AS (
    VALUES ('a'), (NULL), (''), ('b')
)
SELECT
    COUNT(*) AS input_rows,
    COUNT(value) AS non_null_values,
    GROUP_CONCAT(value, '|') AS concatenated
FROM sample;

-- Očekivano: 4 | 3 | a||b. Prazan string učestvuje i ostavlja susedne separatore.

-- @block Ivični slučaj: DISTINCT sa prilagođenim separatorom preko podupita
WITH sample(value) AS (
    VALUES ('rock'), ('jazz'), ('rock'), (NULL)
)
SELECT GROUP_CONCAT(value, ' | ' ORDER BY value) AS unique_values
FROM (
    SELECT DISTINCT value
    FROM sample
    WHERE value IS NOT NULL
);

-- Očekivano: jazz | rock. DISTINCT u spoljašnjem GROUP_CONCAT-u ne može
-- direktno da koristi drugi argument za separator.

-- @block Ivični slučaj: prazan skup i redovi sa samo NULL vrednostima
WITH empty(value) AS (
    SELECT 'x'
    WHERE 0
),
all_null(value) AS (
    VALUES (NULL), (NULL)
)
SELECT 'empty' AS input_case, COUNT(*) AS input_rows, GROUP_CONCAT(value) AS list
FROM empty
UNION ALL
SELECT 'all NULL', COUNT(*), GROUP_CONCAT(value)
FROM all_null;

-- GROUP_CONCAT() je NULL u oba slučaja; COUNT(*) razlikuje prazan ulaz.

-- @block Ivični slučaj: različiti tipovi pretvaraju se u tekst
WITH sample(value) AS (
    VALUES (1), (2.5), ('x'), (NULL)
)
SELECT GROUP_CONCAT(value, '; ' ORDER BY value) AS concatenated
FROM sample;

-- Očekivano: 1; 2.5; x.
