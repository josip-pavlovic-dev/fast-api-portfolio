-- Oblast 03, lekcija 03: Kreiranje contacts, groups i contact_groups
-- Pokreni u novoj memorijskoj bazi: sqlite3 :memory:
-- Iz SQLite CLI prompta, iz root-a repozitorijuma:
-- .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/03_sqlite_create_table_statement_part_2.sql
-- Ne pokreći DDL vežbe nad Chinook ili aplikacionom bazom.

-- @block Vežbe 1-2: FK kontrola je podešavanje pojedinačne konekcije
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;

-- @block Vežba 1: Kreiraj tri tabele u redosledu roditelj pa dete
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

-- @block Vežba 2: Prikaži kolone i FK definicije
PRAGMA table_info(contacts);
PRAGMA table_info(groups);
PRAGMA table_info(contact_groups);
PRAGMA foreign_key_list(contact_groups);

-- @block Vežba 3: Napravi više validnih N:M veza
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES
    ('Ana', 'Anic', 'ana@example.test', '+381601234567'),
    ('Milan', 'Milic', 'milan@example.test', NULL),
    ('Toni', 'Ivic', 'toni@example.test', NULL);

INSERT INTO groups (name)
VALUES ('Family'), ('Work');

INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1), (1, 2), (2, 1);

SELECT contact_id, group_id
FROM contact_groups
ORDER BY contact_id, group_id;

-- Isti kontakt i grupa smeju da se ponavljaju u različitim parovima;
-- identičan par ne sme da se ponovi. UNIQUE(phone) dopušta oba NULL-a.

SELECT COUNT(*) AS contacts_without_phone
FROM contacts
WHERE phone IS NULL;

-- @block Vežba 5: Proveri ON DELETE CASCADE i vrati početno stanje
BEGIN;

DELETE FROM contacts
WHERE id = 1;

SELECT COUNT(*) AS remaining_memberships
FROM contact_groups;

SELECT COUNT(*) AS remaining_groups
FROM groups;

ROLLBACK;

SELECT contact_id, group_id
FROM contact_groups
ORDER BY contact_id, group_id;

-- Posle ROLLBACK-a očekuju se sva tri početna članstva.

-- @block Vežba 4: Očekivane greške — pokreni pojedinačno, ne kao deo skripta.
-- INSERT INTO contacts (first_name, last_name, email) VALUES ('Other', 'Person', 'ana@example.test');
-- INSERT INTO contact_groups (contact_id, group_id) VALUES (1, 1);
-- INSERT INTO contact_groups (contact_id, group_id) VALUES (999, 1);
-- Prvi krši UNIQUE email; drugi složeni PRIMARY KEY; treći FOREIGN KEY.
