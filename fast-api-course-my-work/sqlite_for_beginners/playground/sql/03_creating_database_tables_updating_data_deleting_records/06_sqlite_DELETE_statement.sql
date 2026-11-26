-- Oblast 03, lekcija 06: DELETE
-- Pokreni u novoj memorijskoj bazi: sqlite3 :memory:
-- Iz SQLite CLI prompta, iz root-a repozitorijuma:
-- .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/06_sqlite_DELETE_statement.sql
-- DELETE menja podatke; ne pokreći ga nad Chinook ili aplikacionom bazom.

-- @block Priprema: Omogući FK proveru, napravi šemu i početne redove
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

-- @block Vežba 1: Pregledaj ciljne redove pre brisanja
SELECT id, name
FROM groups
ORDER BY id;

SELECT contact_id, group_id
FROM contact_groups
ORDER BY contact_id, group_id;

-- @block Vežba 2: Obriši samo članstvo, ne kontakt ili grupu
DELETE FROM contact_groups
WHERE contact_id = 1
  AND group_id = 2;

SELECT changes() AS directly_deleted_memberships;

SELECT id, first_name, last_name
FROM contacts
ORDER BY id;

SELECT id, name
FROM groups
ORDER BY id;

-- Očekivano: kontakt i grupa Accounts ostaju; obrisan je samo njihov par.

-- @block Vežba 3: Ponovo dodaj vezu i testiraj kaskadu uz ROLLBACK
INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 2);

BEGIN;

DELETE FROM groups
WHERE id = 2;

SELECT changes() AS directly_deleted_groups;

SELECT COUNT(*) AS memberships_during_delete
FROM contact_groups;

SELECT COUNT(*) AS groups_during_delete
FROM groups;

ROLLBACK;

SELECT id, name
FROM groups
ORDER BY id;

SELECT contact_id, group_id
FROM contact_groups
ORDER BY contact_id, group_id;

-- U transakciji su kaskadno uklonjena članstva za grupu 2; ROLLBACK vraća sve.

-- @block Vežba 4: Uslov bez odgovarajućeg reda
DELETE FROM groups
WHERE id = 999;

SELECT changes() AS deleted_rows_for_missing_id;

-- @block Ivični slučaj: Ovaj upit bi obrisao sve redove; namerno je samo komentar.
-- DELETE FROM groups;
