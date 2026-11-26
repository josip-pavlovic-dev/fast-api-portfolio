-- Oblast 03, lekcija 04: INSERT INTO
-- Pokreni u novoj memorijskoj bazi: sqlite3 :memory:
-- Iz SQLite CLI prompta, iz root-a repozitorijuma:
-- .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/04_sqlite_INSERT_INTO_table_statement.sql
-- Svaki pokrenuti INSERT menja probnu bazu; ne koristi važnu bazu.

-- @block Priprema: Omogući FK proveru i napravi šemu
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

-- @block Vežba 1: Insert jednog reda sa eksplicitnom listom kolona
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES ('Johnny', 'Cash', 'johnny.cash@example.test', '+12025550101');

-- @block Vežba 1: Insert više redova jednom naredbom
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES
    ('Jane', 'Doe', 'jane.doe@example.test', '+12025550102'),
    ('Toni', 'Ivic', 'toni@example.test', NULL);

-- @block Vežba 1: Izostavljena opciona kolona dobija NULL
INSERT INTO contacts (first_name, last_name, email)
VALUES ('Morgan', 'Lee', 'morgan.lee@example.test');

SELECT id, first_name, last_name, email, phone
FROM contacts
ORDER BY id;

-- @block Vežba 2: Unesi više grupa
INSERT INTO groups (name)
VALUES ('Cash Flow'), ('Accounts');

-- @block Vežba 3: Unesi članstva uz stvarne ID vrednosti iz ove sveže baze
INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1), (1, 2), (2, 1);

SELECT c.first_name, c.last_name, g.name AS group_name
FROM contact_groups AS cg
JOIN contacts AS c ON c.id = cg.contact_id
JOIN groups AS g ON g.id = cg.group_id
ORDER BY c.id, g.id;

-- @block Vežba 4: SQLite 3.35+ INSERT RETURNING
INSERT INTO contacts (first_name, last_name, email)
VALUES ('Riley', 'Park', 'riley.park@example.test')
RETURNING id, email;

-- @block Vežba 4: Alternativa za generisani ID na istoj konekciji
SELECT last_insert_rowid() AS most_recent_rowid;

-- @block Ivični slučajevi: očekivane greške, pokreni pojedinačno.
-- INSERT INTO contacts (first_name, last_name, email) VALUES ('No', 'Email', NULL);
-- INSERT INTO contacts (first_name, last_name, email) VALUES ('Duplicate', 'Email', 'johnny.cash@example.test');
-- INSERT INTO contact_groups (contact_id, group_id) VALUES (999, 1);
-- INSERT INTO contact_groups (contact_id, group_id) VALUES (1, 1);
-- Tekstualne vrednosti koriste jednostruke navodnike; NULL nije isto što i ''.
