-- Lekcija: ../../../02_retriving_data_and_manipulating_data/05_removing_duplicate_records_using_distinct_clause.md
-- Vežbaj u SQLTools-u povezanim na ChinookPractice ili u SQLite CLI-ju
-- otvorenom nad chinook_practice.db. Svi blokovi su samo za čitanje.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/05_removing_duplicate_records_using_distinct_clause.sql
--
-- DISTINCT sužava samo rezultat, ne menja redove customers tabele.

-- @block Vežba 1.1: Grad za svakog kupca, uz ponavljanja
SELECT City
FROM customers;

-- @block Vežba 1.2: Jedinstveni gradovi po abecedi
SELECT DISTINCT City
FROM customers
ORDER BY City;

-- U trenutnoj Chinook kopiji: 59 kupaca, 53 različita grada.
-- ORDER BY određuje prikazani redosled, ne DISTINCT.

-- @block Vežba 1.3: Prebroj jedinstvene gradove
SELECT COUNT(DISTINCT City) AS unique_city_count
FROM customers;

-- @block Vežba 2: Jedinstvene države
SELECT DISTINCT Country
FROM customers
ORDER BY Country;

-- @block Vežba 2: Broj jedinstvenih država
SELECT COUNT(DISTINCT Country) AS unique_country_count
FROM customers;

-- Trenutna Chinook kopija sadrži 24 države.

-- @block Vežba 3: Jedinstveni parovi država i gradova
SELECT DISTINCT Country, City
FROM customers
ORDER BY Country, City;

-- @block Vežba 3: Broj jedinstvenih parova
SELECT COUNT(*) AS unique_country_city_pairs
FROM (
    SELECT DISTINCT Country, City
    FROM customers
);

-- U ovoj kopiji ima 53 para. DISTINCT poredi ceo par, ne samo Country.

-- @block Vežba 4: Proveri DISTINCT na malom uzorku
WITH sample(Country, City) AS (
    VALUES
        ('Brazil', 'São Paulo'),
        ('Brazil', 'São Paulo'),
        ('Brazil', 'Rio de Janeiro')
)
SELECT DISTINCT Country, City
FROM sample
ORDER BY Country, City;

-- Dva identična para postaju jedan; Rio ostaje jer se City razlikuje.

-- @block Vežba 5.1: DISTINCT ne uklanja redove iz tabele
SELECT City
FROM customers
ORDER BY City, CustomerId;

-- @block Vežba 5.2: DISTINCT menja samo result set
SELECT DISTINCT City
FROM customers
ORDER BY City;

-- @block Ivični slučaj: NULL, prazan tekst i kolacija
WITH sample(city) AS (
    VALUES ('Paris'), ('PARIS'), ('Paris'), (NULL), (NULL), ('')
)
SELECT DISTINCT city
FROM sample
ORDER BY city;

-- BINARY razlikuje Paris od PARIS; ponovljeni NULL se pojavi jednom,
-- a prazan tekst je posebna vrednost.

-- @block Ivični slučaj: NOCASE pri DISTINCT
WITH sample(city) AS (
    VALUES ('Paris'), ('PARIS'), ('Paris'), (NULL), (NULL), ('')
)
SELECT DISTINCT city COLLATE NOCASE AS city
FROM sample
ORDER BY city COLLATE NOCASE;

-- NOCASE spaja Paris/PARIS za ASCII velika i mala slova; NULL je i dalje
-- jedna vrednost, a '' ostaje različit od NULL.

-- @block Ivični slučaj: COUNT(DISTINCT ...) ne broji NULL
WITH sample(city) AS (
    VALUES ('Paris'), ('Paris'), (NULL), (NULL)
)
SELECT COUNT(DISTINCT city) AS unique_non_null_count
FROM sample;

-- Rezultat je 1. SELECT DISTINCT city bi prikazao i jedan NULL red,
-- ali COUNT(expr) ignoriše NULL vrednosti.
