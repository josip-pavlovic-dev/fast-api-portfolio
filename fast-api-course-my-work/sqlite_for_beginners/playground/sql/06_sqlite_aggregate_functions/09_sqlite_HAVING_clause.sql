-- Oblast 06, lekcija 09: SQLite HAVING
-- Teorija: ../../../06_sqlite_aggregate_functions/09_sqlite_HAVING_clause.md
-- Svi blokovi su samo za čitanje. Pokreći ih nad chinook_practice.db.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/09_sqlite_HAVING_clause.sql

-- @block Vežba 1: Albumi sa 18 do 20 numera, uključujući granice
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
HAVING COUNT(TrackId) BETWEEN 18 AND 20
ORDER BY AlbumId;

-- U ovoj kopiji rezultat sadrži 16 albuma. BETWEEN uključuje 18 i 20.

-- @block Vežba 2: WHERE filtrira numere, HAVING filtrira grupe
SELECT
    AlbumId,
    COUNT(*) AS qualifying_track_count
FROM tracks
WHERE Milliseconds >= 180000
GROUP BY AlbumId
HAVING COUNT(*) >= 3
ORDER BY qualifying_track_count DESC, AlbumId;

-- COUNT(*) broji samo numere koje su prošle WHERE; HAVING zatim zadržava
-- albume sa najmanje tri takve numere.

-- @block Vežba 3: Agregat u HAVING-u ne mora biti prikazan u SELECT-u
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
HAVING MAX(Milliseconds) > 300000
ORDER BY AlbumId;

-- @block Vežba 4: HAVING bez GROUP BY filtrira jednu implicitnu grupu
SELECT COUNT(*) AS total_tracks
FROM tracks
HAVING COUNT(*) > 3000;

-- Očekivano je jedan red sa 3503.

-- @block Ivični slučaj: HAVING odbacuje implicitnu grupu
SELECT COUNT(*) AS total_tracks
FROM tracks
HAVING COUNT(*) > 4000;

-- Upit ne vraća redove; HAVING ne postaje WHERE.

-- @block Ivični slučaj: NULL agregat ne prolazi HAVING uslov
WITH sample(group_id, value) AS (
    VALUES (1, NULL), (1, NULL), (2, 5), (2, 0)
)
SELECT group_id, SUM(value) AS total
FROM sample
GROUP BY group_id
HAVING SUM(value) > 0
ORDER BY group_id;

-- Vraća samo grupu 2. Za grupu 1 je SUM(value) NULL, a NULL > 0 nije TRUE.
