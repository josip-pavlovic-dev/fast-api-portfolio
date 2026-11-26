-- Oblast 03, lekcija 05: UPDATE
-- Pokreni u novoj memorijskoj bazi: sqlite3 :memory:
-- Iz SQLite CLI prompta, iz root-a repozitorijuma:
-- .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/05_sqlite_UPDATE_statement.sql
-- UPDATE menja podatke; ne pokreći ga nad Chinook ili aplikacionom bazom.

-- @block Priprema: Napravi contacts tabelu i probne redove
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT UNIQUE
);

INSERT INTO contacts (first_name, last_name, email, phone)
VALUES
    ('Johnny', 'Cash', 'johnny.cash@example.test', '+12025550101'),
    ('Jane', 'Doe', 'jane.doe@example.test', '+12025550102');

-- @block Vežba 1: Pre promene proveri ciljani red
SELECT id, first_name, last_name, email
FROM contacts
WHERE id = 2;

-- @block Vežbe 2 i 5: Izmeni red u transakciji, proveri, pa vrati
BEGIN;

UPDATE contacts
SET last_name = 'Johnson'
WHERE id = 2;

SELECT changes() AS directly_updated_rows;

SELECT id, first_name, last_name, email
FROM contacts
WHERE id = 2;

ROLLBACK;

SELECT id, first_name, last_name, email
FROM contacts
WHERE id = 2;

-- Posle ROLLBACK-a Jane ponovo ima prezime Doe.

-- @block Vežba 3: Više kolona i WHERE bez pogodaka
UPDATE contacts
SET first_name = 'Jane',
    last_name = 'Johnson'
WHERE id = 2;

SELECT changes() AS directly_updated_rows;

UPDATE contacts
SET last_name = 'Nobody'
WHERE id = 999;

SELECT changes() AS rows_for_missing_id;

-- @block Ivični slučaj: SQLite changes() broji pogođen red i kada je vrednost ista
UPDATE contacts
SET last_name = 'Doe'
WHERE id = 2;

SELECT changes() AS rows_reset_to_doe;

UPDATE contacts
SET last_name = 'Doe'
WHERE id = 2;

SELECT changes() AS rows_even_if_value_is_unchanged;

-- @block Ivični slučajevi: očekivane greške ili opasan upit, ne pokreći ovde.
-- UPDATE contacts SET email = 'johnny.cash@example.test' WHERE id = 2;
-- UPDATE contacts SET last_name = 'Same for every row';
-- Prvi krši UNIQUE; drugi menja svaki red jer nema WHERE.
