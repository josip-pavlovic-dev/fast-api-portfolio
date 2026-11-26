-- Oblast 05, lekcija 01: LEFT JOIN
-- Teorija: ../../../05_table_joins/01_sqlite_LEFT_join.md
-- Svi blokovi su samo za čitanje. Vežbaj nad ChinookPractice ili SQLite CLI-jem
-- otvorenim nad chinook_practice.db, nikada nad bazom aplikacije.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/05_table_joins/01_sqlite_LEFT_join.sql

-- @block Vežba 1: Izvođači i njihovi albumi
SELECT
    ar.ArtistId,
    ar.Name AS ArtistName,
    al.AlbumId,
    al.Title AS AlbumTitle
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
ORDER BY ar.ArtistId, al.AlbumId
LIMIT 15;

-- @block Vežba 1.1: Proveri broj redova i nepoklopljenih izvođača
SELECT
    COUNT(*) AS joined_rows,
    COUNT(DISTINCT ar.ArtistId) AS artists_preserved,
    COUNT(DISTINCT al.AlbumId) AS matched_albums,
    SUM(al.AlbumId IS NULL) AS artists_without_album
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId;

-- U ovoj kopiji očekivano je 418 redova, 275 izvođača, 347 albuma
-- i 71 red bez poklopljenog albuma.

-- @block Vežba 2: Pronađi izvođače bez albuma
SELECT ar.ArtistId, ar.Name
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
WHERE al.AlbumId IS NULL
ORDER BY ar.ArtistId;

-- @block Vežba 3: Uslov za album u ON-u čuva izvođače bez takvog albuma
SELECT
    COUNT(*) AS result_rows,
    COUNT(DISTINCT ar.ArtistId) AS artists_preserved,
    SUM(al.AlbumId IS NULL) AS null_extended_rows
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
   AND al.Title LIKE 'A%';

-- Svi izvođači ostaju na levoj strani; album se pridružuje samo ako mu naslov
-- počinje slovom A. Izvođač bez takvog albuma dobija NULL vrednosti za al.*.

-- @block Vežba 3.1: Isti uslov u WHERE-u uklanja nepoklopljene redove
SELECT
    COUNT(*) AS result_rows,
    COUNT(DISTINCT ar.ArtistId) AS artists_with_matching_album
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
WHERE al.Title LIKE 'A%';

-- WHERE se primenjuje na rezultat spajanja i odbacuje redove sa NULL naslovom.
-- Uporedi ga sa prethodnim blokom: mesto uslova menja rezultat LEFT JOIN-a.

-- @block Vežba 4: COUNT(*) naspram brojanja poklopljenih ključeva
SELECT
    COUNT(*) AS all_joined_rows,
    COUNT(al.AlbumId) AS matched_album_rows,
    COUNT(*) - COUNT(al.AlbumId) AS unmatched_left_rows
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId;

-- COUNT(*) broji i NULL-proširene redove; COUNT(al.AlbumId) ih ne broji.

-- @block Ivični slučaj: ne mešaj NULL ključ sa nepostojećim redom
WITH sample_artist(ArtistId) AS (
    VALUES (1), (NULL)
),
sample_album(ArtistId) AS (
    VALUES (1), (NULL)
)
SELECT a.ArtistId, al.ArtistId AS album_artist_id
FROM sample_artist AS a
LEFT JOIN sample_album AS al
    ON al.ArtistId = a.ArtistId
ORDER BY a.ArtistId;

-- NULL = NULL nije TRUE, pa se NULL ključ sa leve strane ne poklapa sa NULL
-- ključem sa desne strane; LEFT JOIN ipak zadržava levi red.
