-- Oblast 04, lekcija 02: IN
-- Teorija: ../../../04_some_sqlite_operators/02_sqlite_IN_operator.md
-- Svi blokovi su samo za čitanje. Vežbaj nad ChinookPractice ili SQLite CLI-jem
-- otvorenim nad chinook_practice.db, nikada nad bazom aplikacije.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/04_some_sqlite_operators/02_sqlite_IN_operator.sql

-- @block Vežba 1: Numere sa tipom medija 1 ili 2
SELECT TrackId, Name, MediaTypeId
FROM tracks
WHERE MediaTypeId IN (1, 2)
ORDER BY Name, TrackId;

-- U ovoj kopiji uslov vraća 3271 red.

-- @block Vežba 1.1: Prvih pet redova
SELECT TrackId, Name, MediaTypeId
FROM tracks
WHERE MediaTypeId IN (1, 2)
ORDER BY Name, TrackId
LIMIT 5;

-- @block Vežba 2: Isti uslov pomoću OR
SELECT COUNT(*) AS media_types_1_or_2
FROM tracks
WHERE MediaTypeId = 1 OR MediaTypeId = 2;

-- Očekivano: 3271, isto kao MediaTypeId IN (1, 2).

-- @block Vežba 3: Više tekstualnih vrednosti
SELECT CustomerId, FirstName, LastName, Country
FROM customers
WHERE Country IN ('Brazil', 'Canada')
ORDER BY Country, LastName, CustomerId;

-- @block Vežba 4: Numere na računu broj 1 (podupit vraća TrackId)
SELECT TrackId, Name
FROM tracks
WHERE TrackId IN (
    SELECT TrackId
    FROM invoice_items
    WHERE InvoiceId = 1
)
ORDER BY TrackId;

-- U ovoj kopiji račun 1 sadrži TrackId 2 i 4.

-- @block Vežba 5: Numere čiji tip nije 1 niti 2
SELECT COUNT(*) AS other_media_types
FROM tracks
WHERE MediaTypeId NOT IN (1, 2);

-- Očekivano: 232 reda.

-- @block Ivični slučaj: NULL u listi NOT IN
SELECT COUNT(*) AS rows_after_not_in_with_null
FROM tracks
WHERE MediaTypeId NOT IN (1, 2, NULL);

-- Očekivano: 0. Vrednosti koje se ne poklapaju daju UNKNOWN zbog NULL-a u listi.

-- @block Ivični slučaj: Trovalentna logika IN/NOT IN
SELECT
    2 IN (1, 2, NULL) AS matching_value,
    3 IN (1, 2, NULL) AS nonmatching_value,
    3 NOT IN (1, 2, NULL) AS negated_nonmatch;

-- Očekivano: 1, NULL, NULL.

-- @block Ivični slučaj: NULL na levoj strani poređenja
SELECT
    NULL IN (1, 2) AS null_in_nonempty_list,
    NULL NOT IN (1, 2) AS null_not_in_nonempty_list;

-- Oba izraza vraćaju NULL. Za NULL kolonu koristi IS NULL.

-- @block SQLite specifičnost: Prazna IN lista
SELECT
    5 IN () AS empty_in,
    5 NOT IN () AS empty_not_in,
    NULL IN () AS null_empty_in,
    NULL NOT IN () AS null_empty_not_in;

-- SQLite vraća 0, 1, 0, 1. Prazna lista nije prenosiva sintaksa za sve baze.

-- @block Vežba 6: Kupci bez računa pomoću NOT EXISTS
SELECT c.CustomerId, c.FirstName, c.LastName
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM invoices AS i
    WHERE i.CustomerId = c.CustomerId
)
ORDER BY c.CustomerId;

-- NOT EXISTS ne podleže zamci NOT IN sa NULL vrednošću u podupitu.
