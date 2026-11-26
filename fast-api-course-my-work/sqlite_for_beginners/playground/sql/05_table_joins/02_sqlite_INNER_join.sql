-- Oblast 05, lekcija 02: INNER JOIN
-- Teorija: ../../../05_table_joins/02_sqlite_INNER_join.md
-- Svi blokovi su samo za čitanje. Vežbaj nad ChinookPractice ili SQLite CLI-jem
-- otvorenim nad chinook_practice.db, nikada nad bazom aplikacije.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/05_table_joins/02_sqlite_INNER_join.sql

-- @block Vežba 1: Numere i njihovi albumi
SELECT
    t.TrackId,
    t.Name AS TrackName,
    a.AlbumId,
    a.Title AS AlbumTitle
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
ORDER BY t.TrackId
LIMIT 10;

-- @block Vežba 2: Broj spojenih numera i albuma
SELECT
    COUNT(*) AS joined_rows,
    COUNT(DISTINCT t.TrackId) AS distinct_tracks,
    COUNT(DISTINCT a.AlbumId) AS albums_in_result
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId;

-- Očekivano u priloženoj kopiji: 3503 reda, 3503 numere i 347 albuma.

-- @block Vežba 3: Ponovljeni naslov albuma predstavlja više numera
SELECT
    a.AlbumId,
    a.Title AS AlbumTitle,
    COUNT(*) AS track_count
FROM albums AS a
INNER JOIN tracks AS t
    ON t.AlbumId = a.AlbumId
WHERE a.Title = 'Greatest Hits'
GROUP BY a.AlbumId, a.Title;

-- U ovoj kopiji Greatest Hits ima 57 numera. To su različiti redovi numera,
-- a ne ponovljeni zapisi iste numere.

-- @block Vežba 4: Jedinstvena lista albuma koji imaju numere
SELECT DISTINCT
    a.AlbumId,
    a.Title
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
ORDER BY a.AlbumId;

-- @block Vežba 4.1: Prebroj jedinstvene albume u rezultatu
SELECT COUNT(*) AS albums_with_tracks
FROM (
    SELECT DISTINCT a.AlbumId
    FROM tracks AS t
    INNER JOIN albums AS a
        ON a.AlbumId = t.AlbumId
);

-- Očekivano: 347.

-- @block Vežba 5: Uporedi INNER i LEFT JOIN u ovoj kopiji
SELECT COUNT(*) AS inner_join_rows
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId;

SELECT COUNT(*) AS left_join_rows
FROM tracks AS t
LEFT JOIN albums AS a
    ON a.AlbumId = t.AlbumId;

-- Ovde oba broja iznose 3503 jer svaki track ima poklapanje. To ne znači da
-- INNER JOIN i LEFT JOIN imaju isto ponašanje kad poklapanje nedostaje.

-- @block Vežba 5.1: Potraži numere bez albuma pomoću LEFT JOIN-a
SELECT t.TrackId, t.Name
FROM tracks AS t
LEFT JOIN albums AS a
    ON a.AlbumId = t.AlbumId
WHERE a.AlbumId IS NULL
ORDER BY t.TrackId;

-- U ovoj kopiji nema takvih redova. LEFT JOIN čini nepoklopljene redove
-- vidljivim, dok bi INNER JOIN takve numere izostavio.

-- @block Vežba 6: Uslov u ON-u
SELECT COUNT(*) AS matching_tracks
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
   AND a.Title LIKE 'A%';

-- @block Vežba 6.1: Isti filter u WHERE-u
SELECT COUNT(*) AS matching_tracks
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
WHERE a.Title LIKE 'A%';

-- Oba upita vraćaju 369 u trenutnoj kopiji. Za INNER JOIN ovaj filter ne
-- zadržava redove bez poklapanja; ne prenosi isti zaključak na LEFT JOIN.

-- @block Ivični slučaj: NULL vrednosti se ne spajaju pomoću =
WITH left_values(id) AS (
    VALUES (1), (NULL)
),
right_values(id) AS (
    VALUES (1), (NULL)
)
SELECT l.id AS left_id, r.id AS right_id
FROM left_values AS l
INNER JOIN right_values AS r
    ON l.id = r.id;

-- Vraća se samo par (1, 1). Uslov NULL = NULL nije TRUE.
