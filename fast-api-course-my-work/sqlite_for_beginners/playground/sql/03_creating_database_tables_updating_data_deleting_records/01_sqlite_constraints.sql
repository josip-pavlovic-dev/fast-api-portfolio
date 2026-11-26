-- Oblast 03, lekcija 01: SQLite constraints
-- Koristi samo novu privremenu konekciju: sqlite3 :memory:
-- Iz SQLite CLI prompta, iz root-a repozitorijuma:
-- .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/01_sqlite_constraints.sql
-- Ovaj skript pravi probne tabele i podatke; ne pokreći ga nad Chinook ili aplikacionom bazom.

-- @block Vežba 1: Uključi FK proveru za ovu konekciju
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;

-- @block Vežbe 1-3: Napravi kategorije i stavke sa ograničenjima
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    CONSTRAINT uq_categories_name UNIQUE (name),
    CONSTRAINT ck_categories_name_nonblank
        CHECK (length(trim(name)) > 0)
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    price NUMERIC NOT NULL
        CHECK (
            typeof(price) IN ('integer', 'real')
            AND price >= 0
        ),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    CONSTRAINT fk_items_category
        FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- @block Vežba 4: Ubaci validne vrednosti i proveri DEFAULT
INSERT INTO categories (name)
VALUES ('Books');

INSERT INTO items (category_id, name, price)
VALUES (1, 'SQLite workbook', 12.50);

INSERT INTO items (category_id, name, price, stock)
VALUES (1, 'SQL notebook', 4.25, 7);

SELECT id, category_id, name, price, stock
FROM items
ORDER BY id;

-- Očekivani stock za SQLite workbook je 0, jer je kolona izostavljena.
-- DEFAULT se ne primenjuje ako upit izričito pošalje NULL.
-- typeof() dodatno sprečava da obična SQLite tabela prihvati nenumerički tekst kao cenu.

-- @block Vežba 4: Proveri FK definiciju i aktivno podešavanje
PRAGMA foreign_key_list(items);
PRAGMA foreign_keys;

-- @block Ivični slučajevi: Svaki naredni upit treba da bude odbijen.
-- Pokreni ih pojedinačno nakon što proveriš ispravno povezivanje na bazu.
-- Prazan tekst nije NULL, pa ga ovde odbija CHECK, ne NOT NULL.
-- INSERT INTO categories (name) VALUES ('   ');
-- INSERT INTO categories (name) VALUES ('Books');
-- INSERT INTO items (category_id, name, price) VALUES (999, 'Unknown category', 1.00);
-- INSERT INTO items (category_id, name, price) VALUES (1, 'Negative price', -1.00);
-- INSERT INTO items (category_id, name, price, stock) VALUES (1, 'Negative stock', 1.00, -1);
-- INSERT INTO items (category_id, name, price, stock) VALUES (1, 'Null stock', 1.00, NULL);
-- INSERT INTO items (category_id, name, price) VALUES (1, 'Missing price', NULL);
-- INSERT INTO items (category_id, name, price) VALUES (1, 'Text price', 'not-a-number');

-- @block Vežba 7: DEFAULT naspram eksplicitne vrednosti
INSERT INTO items (category_id, name, price, stock)
VALUES (1, 'Explicit zero', 0, 0);

SELECT id, name, stock
FROM items
ORDER BY id;

-- Tekstualni i SQLAlchemy zadaci iz lekcije rešavaju se u komentarima/beleškama.
