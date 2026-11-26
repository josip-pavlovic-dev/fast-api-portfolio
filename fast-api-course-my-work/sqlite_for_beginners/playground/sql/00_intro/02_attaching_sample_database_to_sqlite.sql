-- Lekcija: ../../../00_intro/02_attaching_sample_database_to_sqlite.md
-- SQL primeri za vežbe. Izvršavaj iz root-a repozitorijuma.
--
-- Bezbedan CLI način za ovaj fajl:
--   sqlite3 :memory:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/02_attaching_sample_database_to_sqlite.sql
--
-- .databases, .tables i .schema su dot-komande; pokreni ih odvojeno
-- u SQLite CLI promptu. Ne unosi ih u SQLTools kao SQL naredbe.
-- Chinook fajlovi se priključuju u URI režimu samo za čitanje. Putanja
-- je relativna prema radnom direktorijumu SQLite procesa, zato pokreni
-- komandu iz root-a. mode=ro sprečava i slučajno pravljenje fajla ako
-- se putanja ne poklapa sa postojećom bazom.

-- VEŽBA 1: dot-komandama pregledaj glavnu bazu u zasebnoj CLI sesiji:
-- sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- .databases
-- .tables
-- .schema albums
-- Sledeći SQL blok je alternativa za čitanje šeme. U ovoj skripti
-- priključujemo istu radnu kopiju pod aliasom practice, ne kao main.
ATTACH DATABASE
    'file:fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db?mode=ro'
    AS practice;

-- @block Vežba 1: Definicija albums
SELECT name, sql
FROM practice.sqlite_schema
WHERE type = 'table'
  AND name = 'albums';

-- @block Vežba 1: Strani ključevi albums
PRAGMA practice.foreign_key_list(albums);

DETACH DATABASE practice;

-- VEŽBA 2: dodaj Chinook kao attached bazu uz memorijski main.
-- Pokreni ceo fajl u svežoj sqlite3 :memory: konekciji.
ATTACH DATABASE
    'file:fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db?mode=ro'
    AS chinook;

-- SQL varijanta provere .databases; main je :memory:, chinook je fajl.
-- @block Vežba 2: Priključene baze
PRAGMA database_list;

-- @block Vežba 2: Pet umetnika iz priključene baze
SELECT Name
FROM chinook.artists
ORDER BY Name
LIMIT 5;

-- DETACH uklanja alias iz ove konekcije; ne briše chinook.db.
DETACH DATABASE chinook;

-- Posle DETACH-a PRAGMA database_list više ne treba da prikazuje chinook.
-- @block Vežba 2: Provera nakon DETACH
PRAGMA database_list;

-- EDGE CASE: prazna attached baza u memoriji nema korisničke tabele.
-- Ne koristi nepostojeću putanju do fajla; običan ATTACH može da je napravi.
ATTACH DATABASE ':memory:' AS empty_demo;

-- @block Granični slučaj: broj tabela u praznoj bazi
SELECT COUNT(*) AS table_count
FROM empty_demo.sqlite_schema
WHERE type = 'table';

DETACH DATABASE empty_demo;

-- VEŽBA 3: putanja do fajla zavisi od trenutnog direktorijuma.
-- Iz root-a:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db
-- Iz foldera fast-api-course-my-work/sqlite_for_beginners/chinook:
--   sqlite3 -readonly chinook.db
-- Ove su Bash komande, ne SQL; izvrši ih ručno u terminalu.

-- VEŽBA 4: tokovi i objašnjenje su u dnevniku za Dan 05.
-- Prvi tok otvara Chinook kao main; drugi pokreće :memory: kao main
-- pa radi ATTACH DATABASE ... AS chinook.
