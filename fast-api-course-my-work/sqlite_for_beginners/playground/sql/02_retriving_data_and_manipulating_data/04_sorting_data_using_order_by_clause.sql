-- Lekcija: ../../../02_retriving_data_and_manipulating_data/04_sorting_data_using_order_by_clause.md
-- Vežbaj u SQLTools-u povezanim na ChinookPractice ili u SQLite CLI-ju
-- otvorenom nad chinook_practice.db. Svi blokovi su samo za čitanje.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- a zatim u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/04_sorting_data_using_order_by_clause.sql
--
-- Redosled u rezultatu postoji samo ako je zatražen pomoću ORDER BY.

-- @block Vežba 1.1: Sortiraj po albumu uz eksplicitan ASC
SELECT TrackId, Name, AlbumId
FROM tracks
ORDER BY AlbumId ASC, TrackId ASC;

-- TrackId dodatno određuje redosled unutar albuma sa više numera.

-- @block Vežba 1.2: ASC je podrazumevani smer
SELECT TrackId, Name, AlbumId
FROM tracks
ORDER BY AlbumId, TrackId;

-- Uporedi sa prethodnim blokom: bez ASC smer je i dalje rastući.

-- @block Vežba 2: Deset najdužih numera
SELECT TrackId, Name, Milliseconds
FROM tracks
ORDER BY Milliseconds DESC, TrackId ASC
LIMIT 10;

-- DESC prikazuje duže numere prve. TrackId rešava izjednačenja u
-- trajanju, pa LIMIT 10 daje predvidiv izbor.

-- @block Vežba 3: Sortiraj po više kolona
SELECT TrackId, AlbumId, Name, Milliseconds
FROM tracks
ORDER BY AlbumId ASC, TrackId DESC
LIMIT 8;

-- Prvo rastu AlbumId vrednosti; unutar albuma TrackId opada.

-- @block Vežba 4: Sortiraj po koloni koja nije prikazana
SELECT Name, AlbumId
FROM tracks
ORDER BY Milliseconds ASC, TrackId ASC
LIMIT 5;

-- Milliseconds određuje redosled, ali nije kolona rezultata.
-- TrackId je tie-breaker ako je trajanje jednako.

-- @block Vežba 5: Stabilno sortiranje deset najdužih numera
SELECT TrackId, Name, Milliseconds
FROM tracks
ORDER BY Milliseconds DESC, TrackId ASC
LIMIT 10;

-- @block Ivični slučaj: Podrazumevani položaj NULL u ASC sortiranju
SELECT CustomerId, Company
FROM customers
ORDER BY Company ASC, CustomerId ASC
LIMIT 8;

-- U SQLite-u se NULL pri podrazumevanom ASC sortiranju pojavljuje prvi.
-- CustomerId daje stabilan redosled redova sa istom Company vrednošću.

-- @block Ivični slučaj: Postavi NULL vrednosti na kraj
SELECT CustomerId, Company
FROM customers
ORDER BY Company ASC NULLS LAST, CustomerId ASC
LIMIT 8;

-- NULLS FIRST/LAST je podržano od SQLite 3.30.0. Prazan tekst nije
-- NULL i nije premešten na kraj ovom klauzulom.

-- @block Ivični slučaj: Sortiranje teksta bez ASCII case razlike
SELECT ArtistId, Name
FROM artists
ORDER BY Name COLLATE NOCASE, ArtistId
LIMIT 10;

-- Ugrađeni NOCASE zanemaruje ASCII velika/mala slova; nije lokalizovano
-- sortiranje srpskog teksta. ArtistId razrešava izjednačene nazive.
