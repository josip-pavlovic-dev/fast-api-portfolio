-- Oblast 04, lekcija 04: GLOB
-- Teorija: ../../../04_some_sqlite_operators/04_sqlite_GLOB_operator.md
-- Svi blokovi su samo za čitanje. Vežbaj nad ChinookPractice ili SQLite CLI-jem
-- otvorenim nad chinook_practice.db, nikada nad bazom aplikacije.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/04_some_sqlite_operators/04_sqlite_GLOB_operator.sql

-- @block Vežba 1: Nazivi numera koji počinju velikim slovom Man
SELECT TrackId, Name
FROM tracks
WHERE Name GLOB 'Man*'
ORDER BY Name, TrackId;

-- U ovoj kopiji uslov odgovara 11 redova.

-- @block Vežba 1.1: Prvih pet rezultata
SELECT TrackId, Name
FROM tracks
WHERE Name GLOB 'Man*'
ORDER BY Name, TrackId
LIMIT 5;

-- @block Vežba 2: Nazivi koji se završavaju sa Man
SELECT TrackId, Name
FROM tracks
WHERE Name GLOB '*Man'
ORDER BY Name, TrackId
LIMIT 10;

-- U ovoj kopiji '*Man' odgovara 28 naziva. GLOB razlikuje velika i mala slova.

-- @block Dodatni obrazac: Man se pojavljuje bilo gde
SELECT TrackId, Name
FROM tracks
WHERE Name GLOB '*Man*'
ORDER BY Name, TrackId
LIMIT 10;

-- @block Vežba 3: ? odgovara tačno jednom znaku
SELECT
    'track1' GLOB 'track?' AS one_character,
    'track10' GLOB 'track?' AS too_many_characters;

-- Očekivano: 1, 0.

-- @block Vežba 4.1: Skup znakova
SELECT
    'aable' GLOB '[at]able' AS matches_a,
    'table' GLOB '[at]able' AS matches_t;

-- Očekivano: 1, 1. [at] poklapa jedan znak: a ili t.

-- @block Vežba 4.2: ASCII opseg i velika/mala slova
SELECT
    'apple' GLOB '[a-z]*' AS lowercase_start,
    'Apple' GLOB '[a-z]*' AS uppercase_rejected,
    'Apple' GLOB '[^a-z]*' AS not_lowercase_start;

-- Očekivano: 1, 0, 1.

-- @block Ivični slučaj: Doslovni * i ?
SELECT
    '*' GLOB '[*]' AS literal_asterisk,
    '?' GLOB '[?]' AS literal_question_mark;

-- Očekivano: 1, 1. GLOB nema LIKE-ovu ESCAPE klauzulu.

-- @block Poređenje LIKE i GLOB
SELECT
    'track1' LIKE 'track_' AS like_underscore_wildcard,
    'track1' GLOB 'track?' AS glob_question_wildcard,
    'track1' GLOB 'track_' AS glob_underscore_literal;

-- Očekivano: 1, 1, 0.

-- @block Vežba 6: Nazivi SQLite objekata sa prefiksom sqlite_
SELECT name, type
FROM sqlite_schema
WHERE name GLOB 'sqlite_*'
ORDER BY name;

-- _ je doslovna podvlaka u GLOB-u; * poklapa ostatak naziva.

-- @block Ivični slučaj: NULL GLOB
SELECT
    NULL GLOB '*' AS null_glob,
    NULL NOT GLOB 'Man*' AS null_not_glob;

-- Oba rezultata su NULL, ne TRUE.
