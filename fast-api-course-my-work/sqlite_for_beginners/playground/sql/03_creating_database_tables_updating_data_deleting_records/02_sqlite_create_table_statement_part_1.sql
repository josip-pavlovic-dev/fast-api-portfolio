-- Oblast 03, lekcija 02: CREATE TABLE, modelovanje i SQLite tabele
-- Koristi novu konekciju: sqlite3 :memory:
-- Iz SQLite CLI prompta, iz root-a repozitorijuma:
-- .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/02_sqlite_create_table_statement_part_1.sql
-- Nacrte i tekstualne odgovore zapiši u komentarima ili svojim beleškama.

-- @block Vežba 1: Plan modela adresara
-- Entiteti: contacts i groups.
-- Veza je N:M; jedan red u contact_groups predstavlja jedno članstvo.
-- Oznake modela: contacts.id PK; groups.id PK;
-- contact_groups(contact_id, group_id) složeni PK i dve FK veze.

-- @block Vežba 2: Napravi tabelu sa podrazumevanom vrednošću
CREATE TABLE reading_notes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

PRAGMA table_info(reading_notes);

-- @block Vežba 3: IF NOT EXISTS ne menja postojeću šemu
CREATE TABLE IF NOT EXISTS reading_notes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

PRAGMA table_info(reading_notes);

-- Očekivano: created_at je i dalje prisutan; IF NOT EXISTS ne migrira tabelu.

-- @block Vežba 5: rowid tabela i WITHOUT ROWID tabela
CREATE TABLE rowid_demo (
    id INTEGER PRIMARY KEY,
    label TEXT NOT NULL
);

CREATE TABLE contact_groups_demo (
    contact_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    PRIMARY KEY (contact_id, group_id)
) WITHOUT ROWID;

INSERT INTO rowid_demo (label)
VALUES ('ordinary rowid table');

INSERT INTO contact_groups_demo (contact_id, group_id)
VALUES (1, 10), (1, 20), (2, 10);

SELECT id, rowid, label
FROM rowid_demo;

SELECT contact_id, group_id
FROM contact_groups_demo
ORDER BY contact_id, group_id;

-- U običnoj tabeli id INTEGER PRIMARY KEY je alias za rowid.
-- contact_groups_demo nema rowid; ne pokreći SELECT rowid FROM contact_groups_demo.

-- @block Vežba 6: Pregled SQLAlchemy modela
-- U Python/SQLAlchemy vežbi uporedi modele iz teorijske lekcije sa
-- reading_notes i kontakt/grupa modelom. relationship() nije FK ograničenje.
