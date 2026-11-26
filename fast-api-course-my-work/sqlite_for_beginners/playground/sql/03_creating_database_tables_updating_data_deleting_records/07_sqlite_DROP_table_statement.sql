-- Oblast 03, lekcija 07: DROP TABLE
-- Pokreni u novoj memorijskoj bazi: sqlite3 :memory:
-- Iz SQLite CLI prompta, iz root-a repozitorijuma:
-- .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/07_sqlite_DROP_table_statement.sql
-- DROP TABLE briše šemu i podatke; ne pokreći ga nad važnom bazom.

-- @block Priprema: FK provera, tabele i početni podaci
PRAGMA foreign_keys = ON;

CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT UNIQUE
);

CREATE TABLE groups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE contact_groups (
    contact_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    PRIMARY KEY (contact_id, group_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
        ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id)
        ON DELETE CASCADE
) WITHOUT ROWID;

INSERT INTO contacts (first_name, last_name, email)
VALUES
    ('Johnny', 'Cash', 'johnny.cash@example.test'),
    ('Jane', 'Doe', 'jane.doe@example.test');

INSERT INTO groups (name)
VALUES ('Cash Flow'), ('Accounts');

INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1), (1, 2), (2, 1);

-- @block Vežba 1: Proveri stanje pre uklanjanja šeme
SELECT name, type
FROM sqlite_schema
WHERE type = 'table'
ORDER BY name;

SELECT id, name
FROM groups
ORDER BY id;

SELECT contact_id, group_id
FROM contact_groups
ORDER BY contact_id, group_id;

-- @block Vežba 2: DROP je transakcioni u ovom primeru; poništi ga
BEGIN;

DROP TABLE groups;

SELECT name, type
FROM sqlite_schema
WHERE type = 'table'
ORDER BY name;

SELECT COUNT(*) AS memberships_after_drop
FROM contact_groups;

ROLLBACK;

SELECT name, type
FROM sqlite_schema
WHERE type = 'table'
ORDER BY name;

SELECT id, name
FROM groups
ORDER BY id;

SELECT contact_id, group_id
FROM contact_groups
ORDER BY contact_id, group_id;

-- Posle ROLLBACK-a groups, njeni podaci i članstva su vraćeni.

-- @block Vežba 4: IF EXISTS i ponovljeno uklanjanje
BEGIN;

DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS groups;

SELECT name
FROM sqlite_schema
WHERE type = 'table'
ORDER BY name;

ROLLBACK;

-- Drugi DROP TABLE IF EXISTS ne prijavljuje grešku; ROLLBACK vraća šemu.

-- @block Ivični slučaj: Razlikuj brisanje redova od brisanja tabele
SELECT name, type
FROM sqlite_schema
WHERE type = 'table'
ORDER BY name;

-- DROP TABLE IF EXISTS ne štiti od uklanjanja pogrešne postojeće tabele.
-- SQLAlchemy Base.metadata.drop_all(engine) ima širi domet od jednog DROP-a.
