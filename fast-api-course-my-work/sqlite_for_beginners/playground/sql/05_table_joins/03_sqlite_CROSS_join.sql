-- Oblast 05, lekcija 03: CROSS JOIN
-- Teorija: ../../../05_table_joins/03_sqlite_CROSS_join.md
-- Svi blokovi su samo za čitanje. Vežbaj nad ChinookPractice ili SQLite CLI-jem
-- otvorenim nad chinook_practice.db, nikada nad bazom aplikacije.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/05_table_joins/03_sqlite_CROSS_join.sql

-- @block Vežba 1: Svaki album u kombinaciji sa svakim tipom medija
SELECT
    a.AlbumId,
    a.Title AS AlbumTitle,
    a.ArtistId,
    m.MediaTypeId,
    m.Name AS MediaTypeName
FROM albums AS a
CROSS JOIN media_types AS m
ORDER BY a.AlbumId, m.MediaTypeId
LIMIT 10;

-- Ovaj par nije provera stvarne relacije; CROSS JOIN pravi sve kombinacije.

-- @block Vežba 2: Proveri Dekartov proizvod
SELECT
    (SELECT COUNT(*) FROM albums) AS album_count,
    (SELECT COUNT(*) FROM media_types) AS media_type_count,
    (SELECT COUNT(*) FROM albums CROSS JOIN media_types) AS combinations;

-- Očekivano: 347 × 5 = 1735 redova u priloženoj kopiji.

-- @block Vežba 3: Izaberi samo potrebne kolone i koristi alias-e
SELECT
    a.AlbumId AS AlbumId,
    a.Title AS AlbumTitle,
    m.MediaTypeId AS MediaTypeId,
    m.Name AS MediaTypeName
FROM albums AS a
CROSS JOIN media_types AS m
ORDER BY a.AlbumId, m.MediaTypeId
LIMIT 10;

-- @block Vežba 4: Uporedi CROSS JOIN sa brojem parova bez poklapanja
SELECT COUNT(*) AS all_combinations
FROM albums AS a
CROSS JOIN media_types AS m;

-- Nema ON uslova: svaki album se kombinuje sa svih 5 tipova medija.

-- @block Ivični slučaj: prazna desna tabela daje nula kombinacija
WITH empty_media_types(MediaTypeId, Name) AS (
    SELECT MediaTypeId, Name
    FROM media_types
    WHERE 0
)
SELECT COUNT(*) AS combinations_with_empty_table
FROM albums AS a
CROSS JOIN empty_media_types AS m;

-- Očekivano: 0. Broj redova proizvoda je m × 0 = 0.

-- @block Ivični slučaj: broj kombinacija brzo raste
WITH left_sample(value) AS (
    VALUES (1), (2), (3), (4)
),
right_sample(value) AS (
    VALUES ('a'), ('b'), ('c')
)
SELECT COUNT(*) AS combinations
FROM left_sample
CROSS JOIN right_sample;

-- Očekivano: 4 × 3 = 12. Procenjuj veličinu proizvoda pre upita nad velikim tabelama.
