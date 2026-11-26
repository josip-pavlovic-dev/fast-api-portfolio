-- Oblast 04, lekcija 03: LIKE
-- Teorija: ../../../04_some_sqlite_operators/03_sqlite_LIKE_operator.md
-- Svi blokovi su samo za čitanje. Vežbaj nad ChinookPractice ili SQLite CLI-jem
-- otvorenim nad chinook_practice.db, nikada nad bazom aplikacije.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/04_some_sqlite_operators/03_sqlite_LIKE_operator.sql

-- @block Vežba 1: Nazivi numera koji počinju sa Wild
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE 'Wild%'
ORDER BY Name, TrackId;

-- U ovoj kopiji upit vraća 5 numera.

-- @block Vežba 2.1: Nazivi koji počinju sa Love
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE 'Love%'
ORDER BY Name, TrackId
LIMIT 10;

-- @block Vežba 2.2: Nazivi koji se završavaju sa Love
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE '%Love'
ORDER BY Name, TrackId
LIMIT 10;

-- @block Vežba 2.3: Nazivi koji sadrže Love bilo gde
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE '%Love%'
ORDER BY Name, TrackId
LIMIT 10;

-- % poklapa nula ili više znakova; položaj džokera određuje šta tražiš.

-- @block Vežba 3.1: Drugi znak je r
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE '_r%'
ORDER BY Name, TrackId
LIMIT 10;

-- @block Vežba 3.2: Počinje sa A i ima još najmanje jedan znak
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE 'A_%'
ORDER BY Name, TrackId
LIMIT 10;

-- @block Dodatni obrazac: Počinje sa A i završava se sa o
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE 'A%o'
ORDER BY Name, TrackId
LIMIT 10;

-- Razlikuj 'A%o' od 'A%o%': završni % dozvoljava još teksta posle slova o.

-- @block Vežba 4: Doslovni procenat i podvlaka pomoću ESCAPE
SELECT
    '100% organic' LIKE '100!% organic' ESCAPE '!' AS literal_percent,
    'a_b' LIKE 'a!_b' ESCAPE '!' AS literal_underscore,
    'wow!' LIKE 'wow!!' ESCAPE '!' AS literal_escape_character;

-- Očekivano: 1, 1, 1.

-- @block Vežba 5: SQLite LIKE i ASCII/Unicode velika i mala slova
SELECT
    'a' LIKE 'A' AS ascii_match,
    'æ' LIKE 'Æ' AS unicode_case_match;

-- U ugrađenom SQLite LIKE-u očekivano je 1, 0. To nije puna Unicode case-folding podrška.

-- @block Ivični slučaj: NULL ne odgovara niti NOT LIKE obrascu
SELECT
    NULL LIKE 'A%' AS null_like,
    NULL NOT LIKE 'A%' AS null_not_like;

-- Oba rezultata su NULL; WHERE ih ne tretira kao TRUE.

-- @block Poređenje džokera: LIKE i GLOB nisu zamenljivi
SELECT
    'track1' LIKE 'track_' AS like_underscore_wildcard,
    'track1' GLOB 'track?' AS glob_question_wildcard;

-- Oba rezultata su 1, ali operatori koriste različite znakove za džokere.
