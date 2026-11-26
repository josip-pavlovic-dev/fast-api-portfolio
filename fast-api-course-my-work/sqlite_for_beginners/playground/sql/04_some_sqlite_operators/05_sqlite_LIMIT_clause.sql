-- Oblast 04, lekcija 05: LIMIT i OFFSET
-- Teorija: ../../../04_some_sqlite_operators/05_sqlite_LIMIT_clause.md
-- Svi blokovi su samo za čitanje. Vežbaj nad ChinookPractice ili SQLite CLI-jem
-- otvorenim nad chinook_practice.db, nikada nad bazom aplikacije.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/04_some_sqlite_operators/05_sqlite_LIMIT_clause.sql

-- @block Vežba 1: Pet prvih numera uz stabilan redosled
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 5;

-- Tracks ima ukupno 3503 reda; LIMIT 5 prikazuje samo pet.

-- @block Vežba 2: Druga stranica sa pet numera
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 5 OFFSET 5;

-- OFFSET 5 preskače prvih pet; očekivani TrackId su 6–10.

-- @block Vežba 3: Preskoči 12 i vrati narednih 12
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 12 OFFSET 12;

-- Prvi vraćeni TrackId je 13. OFFSET 12 preskače 12 redova.

-- @block Vežba 4: Deset najdužih numera uz tie-breaker
SELECT TrackId, Name, Milliseconds
FROM tracks
ORDER BY Milliseconds DESC, TrackId ASC
LIMIT 10;

-- TrackId daje stabilan redosled kada više numera ima isto trajanje.

-- @block Ivični slučaj: LIMIT 0
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 0;

-- Očekivano: nula redova.

-- @block SQLite specifičnost: Negativan LIMIT nema gornju granicu
SELECT COUNT(*) AS rows_with_negative_limit
FROM (
    SELECT TrackId
    FROM tracks
    LIMIT -1
);

-- Očekivano: 3503. Validiraj veličinu stranice u aplikaciji.

-- @block SQLite specifičnost: Negativan OFFSET se tretira kao nula
SELECT TrackId
FROM tracks
ORDER BY TrackId
LIMIT 3 OFFSET -5;

-- Očekivani TrackId su 1, 2, 3. Aplikacija ipak treba da odbije negativan offset.

-- @block Ivični slučaj: OFFSET izvan dostupnih redova
SELECT COUNT(*) AS rows_after_large_offset
FROM (
    SELECT TrackId
    FROM tracks
    ORDER BY TrackId
    LIMIT 5 OFFSET 4000
);

-- Očekivano: 0.

-- @block Poređenje sintaksi
SELECT TrackId
FROM tracks
ORDER BY TrackId
LIMIT 5 OFFSET 5;

SELECT TrackId
FROM tracks
ORDER BY TrackId
LIMIT 5, 5;

-- Obe sintakse daju TrackId 6–10. U LIMIT offset, count redosled je obrnut.

-- @block Vežba 6: Ukupan broj pogodaka nije isto što i LIMIT
SELECT COUNT(*) AS tracks_on_album_1
FROM tracks
WHERE AlbumId = 1;

SELECT TrackId, Name
FROM tracks
WHERE AlbumId = 1
ORDER BY TrackId
LIMIT 4;

-- Ukupno je 10 numera na albumu 1; drugi upit prikazuje samo prve četiri.

-- @block Primer: Keyset straničenje posle TrackId 10
SELECT TrackId, Name
FROM tracks
WHERE TrackId > 10
ORDER BY TrackId
LIMIT 5;

-- Ovo nastavlja posle poslednjeg viđenog identifikatora umesto da preskoči 10 redova.
