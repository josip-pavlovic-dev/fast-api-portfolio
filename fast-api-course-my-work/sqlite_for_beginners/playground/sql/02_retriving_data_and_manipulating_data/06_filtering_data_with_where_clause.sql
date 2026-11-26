-- Lekcija: ../../../02_retriving_data_and_manipulating_data/06_filtering_data_with_where_clause.md
-- Vežbaj u SQLTools-u povezanim na ChinookPractice ili u SQLite CLI-ju
-- otvorenom nad chinook_practice.db. Svi blokovi su samo za čitanje.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- a zatim u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/06_filtering_data_with_where_clause.sql
--
-- WHERE izdvaja redove; ne menja ih. Proveri uslove pre dodavanja
-- LIMIT-a, jer LIMIT prikazuje samo deo redova koji ispunjavaju uslov.

-- @block Vežba 1.1: Sve numere sa albuma 1
SELECT Name, Composer, AlbumId
FROM tracks
WHERE AlbumId = 1;

-- U trenutnoj Chinook kopiji uslov odgovara 10 redova.

-- @block Vežba 1.2: Četiri prva rezultata po TrackId
SELECT TrackId, Name, Composer, AlbumId
FROM tracks
WHERE AlbumId = 1
ORDER BY TrackId
LIMIT 4;

-- LIMIT prikazuje samo 4 od 10 odgovarajućih redova.

-- @block Vežba 2: Numere duže od 300000 ms
SELECT TrackId, Name, Milliseconds
FROM tracks
WHERE Milliseconds > 300000
ORDER BY Milliseconds DESC, TrackId ASC
LIMIT 5;

-- @block Vežba 3: Kupci iz Brazila
SELECT CustomerId, FirstName, LastName, Country
FROM customers
WHERE Country = 'Brazil'
ORDER BY LastName, FirstName, CustomerId
LIMIT 5;

-- Tekstualna vrednost mora biti u jednostrukim navodnicima.
-- CustomerId je dodat kao tie-breaker za predvidiv redosled.

-- @block Vežba 4.1: Album 1 ili album 2, zatim filtriraj trajanje
SELECT TrackId, Name, AlbumId, Milliseconds
FROM tracks
WHERE (AlbumId = 1 OR AlbumId = 2)
  AND Milliseconds > 240000
ORDER BY AlbumId, TrackId;

-- @block Ivični slučaj: Ista logika bez zagrada
SELECT TrackId, Name, AlbumId, Milliseconds
FROM tracks
WHERE AlbumId = 1
   OR AlbumId = 2 AND Milliseconds > 240000
ORDER BY AlbumId, TrackId;

-- AND ima jači prioritet od OR: drugi upit znači
-- AlbumId = 1 OR (AlbumId = 2 AND Milliseconds > 240000).
-- U trenutnoj kopiji prvi uslov vraća 5, a drugi 11 redova.

-- @block Vežba 5.1: Numere bez poznatog kompozitora
SELECT TrackId, Name, Composer
FROM tracks
WHERE Composer IS NULL
ORDER BY TrackId;

-- @block Vežba 5.2: Numere sa poznatim kompozitorom
SELECT TrackId, Name, Composer
FROM tracks
WHERE Composer IS NOT NULL
ORDER BY TrackId
LIMIT 10;

-- @block Ivični slučaj: <> ne uključuje NULL vrednosti
SELECT COUNT(*) AS nonmatching_nonnull_composers
FROM tracks
WHERE Composer <> 'Angus Young, Malcolm Young, Brian Johnson';

-- NULL <> tekst daje UNKNOWN, pa ga WHERE ne zadržava.
-- Za nedostajuće vrednosti koristi IS NULL, ne = NULL ili <> NULL.

-- @block Ivični slučaj: NULL nije prazan tekst (Company IS NULL)
SELECT CustomerId, Company
FROM customers
WHERE Company IS NULL
ORDER BY CustomerId;

-- @block Ivični slučaj: Prazan tekst nije NULL (Company = '')
SELECT CustomerId, Company
FROM customers
WHERE Company = ''
ORDER BY CustomerId;

-- U trenutnoj kopiji postoje NULL vrednosti u Company, ali nema
-- vrednosti jednakih praznom tekstu.

-- @block Dodatna vežba: LIKE obrazac sa prefiksom
SELECT CustomerId, FirstName, LastName
FROM customers
WHERE FirstName LIKE 'A%'
ORDER BY LastName, CustomerId;

-- LIKE koristi % za nula ili više znakova i _ za tačno jedan znak.
-- Za GLOB se koriste drugi džokeri: * i ?.
