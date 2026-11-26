-- Lekcija: ../../../02_retriving_data_and_manipulating_data/09_sqlite_aliases.md
-- Vežbaj u SQLTools-u povezanim na ChinookPractice ili u SQLite CLI-ju
-- otvorenom nad chinook_practice.db. Svi blokovi su samo za čitanje.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- a zatim u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/09_sqlite_aliases.sql
--
-- Alias važi samo u jednom upitu i ne menja šemu niti imena kolona.

-- @block Vežba 1: Alias kolona u zaglavljima rezultata
SELECT
    CustomerId AS id,
    FirstName AS first_name,
    LastName AS last_name
FROM customers
ORDER BY CustomerId
LIMIT 3;

-- @block Dodatni primer: Alias sa razmakom mora biti citiran
SELECT FirstName AS "Customer first name"
FROM customers
ORDER BY CustomerId
LIMIT 3;

-- @block Vežba 2: Alias tabele u filtriranju po gradu
SELECT c.FirstName, c.LastName, c.City
FROM customers AS c
WHERE c.City LIKE 'A%'
ORDER BY c.LastName, c.CustomerId;

-- c je alias za customers. Posle dodeljivanja aliasa koristi c.City,
-- a ne customers.City. LIKE 'A%' traži gradove koji počinju slovom A.

-- @block Vežba 3: Alias tabele i aliasi kolona zajedno
SELECT
    c.FirstName AS first_name,
    c.LastName AS last_name,
    c.City AS city
FROM customers AS c
WHERE c.City LIKE 'A%'
ORDER BY last_name, c.CustomerId;

-- Alias kolone last_name može se koristiti u ORDER BY. CustomerId je
-- dodat kao tie-breaker radi stabilnog redosleda istih prezimena.

-- @block Vežba 4.1: Alias u rezultatu i ORDER BY
SELECT CustomerId AS id, FirstName AS first_name
FROM customers
WHERE CustomerId = 1
ORDER BY id;

-- @block Vežba 4.2: Potvrdi da je stvarno ime kolone nepromenjeno
PRAGMA table_info(customers);

-- Kolona se i dalje zove CustomerId; id postoji samo u rezultatu prvog
-- upita. Sledeći upit je namerno neaktivan i prijavio bi grešku:
-- SELECT id FROM customers;

-- SQLite ponekad prihvata SELECT alias u WHERE kao nestandardno
-- proširenje, ali nemoj se oslanjati na njega. Prenosivi oblik koristi
-- stvarnu kolonu:
-- SELECT FirstName AS first_name FROM customers WHERE FirstName = 'Johannes';
-- Rizični, neprenosivi oblik:
-- SELECT FirstName AS first_name FROM customers WHERE first_name = 'Johannes';

-- Alias tabele takođe zamenjuje originalno ime u okviru upita. Ovaj
-- upit je namerno neaktivan jer customers više nije ime izvora:
-- SELECT customers.City FROM customers AS c;
