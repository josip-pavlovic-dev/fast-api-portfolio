-- Lekcija: ../../../02_retriving_data_and_manipulating_data/02_querying_data_from_all_columns_in_a_table.md
-- Vežbaj u SQLTools-u povezanim na ChinookPractice ili u SQLite CLI-ju
-- otvorenom nad chinook_practice.db. Svi blokovi su samo za čitanje.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- a zatim u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/02_querying_data_from_all_columns_in_a_table.sql
--
-- SELECT * vraća sve kolone koje su trenutno definisane u tabeli.
-- Za aplikacioni kod obično navedi samo potrebne kolone.

-- @block Vežba 1: Sve kolone i svi redovi iz albums
SELECT *
FROM albums;

-- albums u ovoj radnoj kopiji ima 347 redova. Rezultat ima tri kolone:
-- AlbumId, Title i ArtistId. Proveri broj redova i redosled kolona.

-- @block Provera: Broj redova u albums
SELECT COUNT(*) AS album_count
FROM albums;

-- @block Provera šeme: Nazivi i pozicije kolona
PRAGMA table_info(albums);

-- @block Vežba 2: Sve kolone uz stabilan redosled i ograničenje
SELECT *
FROM albums
ORDER BY AlbumId
LIMIT 5;

-- LIMIT 5 ograničava broj redova, a ne broj kolona.
-- ORDER BY AlbumId čini izbor prvih pet redova predvidljivim.

-- @block Vežba 2: Uporedi sa celom tabelom
SELECT *
FROM albums;

-- Uporedi sa prethodnim blokom: broj kolona i njihov redosled su isti;
-- razlikuje se broj redova, jer samo prvi upit ima LIMIT 5.

-- @block Vežba 3.1: Širok rezultat za prvih pet albuma
SELECT *
FROM albums
ORDER BY AlbumId
LIMIT 5;

-- @block Vežba 3.2: Uži rezultat za iste albume
SELECT AlbumId, Title
FROM albums
ORDER BY AlbumId
LIMIT 5;

-- Oba upita vraćaju iste albume i isti broj redova.
-- Drugi rezultat ima dve kolone umesto tri.

-- @block Vežba 4: Zapiši sve kolone uz eksplicitnu tabelu
SELECT albums.*
FROM albums
ORDER BY AlbumId
LIMIT 5;

-- albums.* znači sve kolone iz albums. Ovo postaje korisno kada upit
-- čita više tabela i želiš da jasno navedeš izvor kolona.

-- @block Vežba 5.1: Sve kolone iz druge tabele
SELECT artists.*
FROM artists
ORDER BY ArtistId
LIMIT 5;

-- @block Vežba 5.2: Izabrane kolone iz iste tabele
SELECT ArtistId, Name
FROM artists
ORDER BY ArtistId
LIMIT 5;

-- Poredi broj kolona, nazive zaglavlja i redove. Izbor konkretnih
-- kolona ne filtrira redove; ORDER BY i LIMIT utiču na redosled/broj.
