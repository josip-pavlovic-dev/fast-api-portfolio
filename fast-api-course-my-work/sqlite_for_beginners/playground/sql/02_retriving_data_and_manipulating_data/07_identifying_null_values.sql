-- Lekcija: ../../../02_retriving_data_and_manipulating_data/07_identifying_null_values.md
-- Vežbaj u SQLTools-u povezanim na ChinookPractice ili u SQLite CLI-ju
-- otvorenom nad chinook_practice.db. Svi blokovi su samo za čitanje.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- a zatim u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/07_identifying_null_values.sql
--
-- NULL nije broj 0, prazan tekst '' ni tekst 'NULL'. Alat može prikazati
-- NULL kao praznu ćeliju; koristi SQL uslove da pouzdano razlikuješ vrednosti.

-- @block Vežba 1: Kupci bez kompanije
SELECT CustomerId, FirstName, LastName, Company
FROM customers
WHERE Company IS NULL
ORDER BY CustomerId;

-- @block Vežba 1: Prebroj nedostajuće vrednosti
SELECT COUNT(*) AS customers_without_company
FROM customers
WHERE Company IS NULL;

-- U trenutnoj Chinook kopiji rezultat je 49.

-- @block Vežba 2: Kupci sa kompanijom
SELECT CustomerId, FirstName, LastName, Company
FROM customers
WHERE Company IS NOT NULL
ORDER BY CustomerId;

-- @block Vežba 2: Prebroj poznate vrednosti
SELECT COUNT(*) AS customers_with_company
FROM customers
WHERE Company IS NOT NULL;

-- U trenutnoj kopiji rezultat je 10; 49 + 10 = ukupno 59 kupaca.

-- @block Ivični slučaj: COUNT(*) naspram COUNT(Company)
SELECT
    COUNT(*) AS all_customers,
    COUNT(Company) AS customers_with_company,
    COUNT(*) - COUNT(Company) AS customers_without_company
FROM customers;

-- COUNT(*) broji sve redove. COUNT(Company) preskače NULL, ali bi brojao
-- prazan tekst jer je '' vrednost, a ne NULL.

-- @block Vežba 3.1: Company je NULL
SELECT CustomerId, Company
FROM customers
WHERE Company IS NULL
ORDER BY CustomerId;

-- @block Vežba 3.2: Company je prazan tekst
SELECT CustomerId, Company
FROM customers
WHERE Company = ''
ORDER BY CustomerId;

-- U trenutnoj kopiji drugi upit vraća 0 redova. To nije isto što i NULL.

-- @block Ivični slučaj: Obično poređenje sa NULL ne pronalazi redove
SELECT CustomerId, Company
FROM customers
WHERE Company = NULL;

-- Ovaj blok namerno prikazuje neispravan način provere: poređenje daje
-- UNKNOWN, pa WHERE ne vraća redove. Umesto njega koristi IS NULL.

-- @block Vežba 4.1: Numere bez kompozitora
SELECT TrackId, Name, Composer
FROM tracks
WHERE Composer IS NULL
ORDER BY TrackId;

-- @block Vežba 4.2: Numere sa poznatim kompozitorom
SELECT TrackId, Name, Composer
FROM tracks
WHERE Composer IS NOT NULL
ORDER BY TrackId
LIMIT 10;

-- @block Ivični slučaj: NULL u poređenjima i izrazima
SELECT
    NULL = NULL AS equality_result,
    NULL <> NULL AS inequality_result,
    NULL IS NULL AS is_null_result,
    1 + NULL AS arithmetic_result;

-- equality_result, inequality_result i arithmetic_result su NULL
-- (nepoznati); is_null_result je 1 (tačno).
