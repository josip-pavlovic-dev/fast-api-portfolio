-- Lekcija: ../../../02_retriving_data_and_manipulating_data/03_querying_data_from_specific_columns_in_a_table.md
-- Vežbaj u SQLTools-u povezanim na ChinookPractice ili u SQLite CLI-ju
-- otvorenom nad chinook_practice.db. Ovaj fajl sadrži samo SELECT upite.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/03_querying_data_from_specific_columns_in_a_table.sql
--
-- Izbor kolona menja širinu rezultata, ne broj odgovarajućih redova.
-- Bez ORDER BY ne pretpostavljaj redosled redova.

-- @block Vežba 1: Izaberi četiri kolone iz tracks
SELECT TrackId, Name, Composer, UnitPrice
FROM tracks;

-- Rezultat ima četiri kolone. U ovoj radnoj kopiji tracks ima 3503 reda.
-- Composer može prikazati NULL; to nije isto što i prazan tekst.

-- @block Provera: Broj redova u tracks
SELECT COUNT(*) AS track_count
FROM tracks;

-- @block Vežba 2: Isti podaci, drugi redosled kolona
SELECT Name, TrackId, UnitPrice, Composer
FROM tracks;

-- Kolone se prikazuju redom kojim su navedene posle SELECT.
-- Izbor i preuređivanje kolona ne menja broj redova.

-- @block Vežba 3: Izabrane kolone, sortiranje i LIMIT
SELECT TrackId, Name, UnitPrice
FROM tracks
ORDER BY TrackId
LIMIT 5;

-- SELECT određuje kolone; ORDER BY određuje redosled redova;
-- LIMIT ograničava broj vraćenih redova.

-- @block Vežba 4: Izaberi određene kolone iz artists
SELECT ArtistId, Name
FROM artists
ORDER BY ArtistId
LIMIT 5;

-- @block Vežba 4: Uporedi sa svim kolonama iz artists
SELECT *
FROM artists
ORDER BY ArtistId
LIMIT 5;

-- Oba upita prikazuju istih pet umetnika, ali SELECT * vraća sve
-- kolone. U aplikaciji biraj samo polja koja endpointu trebaju.

-- @block Vežba 5: Pregled Composer vrednosti u istim kolonama
SELECT TrackId, Name, Composer, UnitPrice
FROM tracks
ORDER BY TrackId
LIMIT 20;

-- Pregledaj Composer: SQLite klijent može prikazati NULL kao NULL ili
-- prazan prikaz. NULL znači da vrednost nedostaje, ne da je prazan tekst.
-- U sledećoj lekciji koristićemo IS NULL / IS NOT NULL za precizno
-- filtriranje takvih redova.
