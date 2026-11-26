-- Lekcija: ../../../00_intro/04_database_concepts.md
-- VEŽBA 2: izvršiv primer šeme voća, povrća i više boja.
--
-- VAŽNO: ovaj fajl sadrži CREATE TABLE i INSERT. Pokreni ga samo u
-- novoj memorijskoj bazi, nikada nad Chinook bazom ili TodoApp bazom.
-- Iz root-a repozitorijuma:
--   sqlite3 :memory:
-- Zatim u SQLite CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/04_database_concepts.sql
--
-- Da ga ponoviš, izađi sa .quit i pokreni novu sqlite3 :memory: sesiju.
-- Ostatak tekstualnih, ERD i FastAPI zadataka rešen je u dnevniku za Dan 05.

-- VEŽBA 1: prikaz reda iz pojednostavljenog primera sa jednom bojom.
-- Ovo je objašnjavajući primer, ne INSERT za šemu iz Vežbe 2:
-- FruitId = 1, Name = 'Apple', ColorId = 1 (Green).
-- FruitId je dobar PK; Name ne mora biti jedinstven.

-- FK provera mora biti uključena za ovu konekciju pre upisa.
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;

-- VEŽBA 2: svaki entitet ima svoj ID; veze sa bojama idu kroz
-- povezničke tabele, jer jedan zapis može imati više boja.
CREATE TABLE fruits (
    FruitId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);

CREATE TABLE vegetables (
    VegetableId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);

CREATE TABLE colors (
    ColorId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL UNIQUE
);

CREATE TABLE fruit_colors (
    FruitId INTEGER NOT NULL,
    ColorId INTEGER NOT NULL,
    PRIMARY KEY (FruitId, ColorId),
    FOREIGN KEY (FruitId) REFERENCES fruits(FruitId),
    FOREIGN KEY (ColorId) REFERENCES colors(ColorId)
);

CREATE TABLE vegetable_colors (
    VegetableId INTEGER NOT NULL,
    ColorId INTEGER NOT NULL,
    PRIMARY KEY (VegetableId, ColorId),
    FOREIGN KEY (VegetableId) REFERENCES vegetables(VegetableId),
    FOREIGN KEY (ColorId) REFERENCES colors(ColorId)
);

-- Isti naziv boje se čuva jednom. Uzorak pokriva nula, jednu i dve
-- boje po voću, kao i deljenje iste boje između voća i povrća.
-- Transakcija potvrđuje ceo uzorak zajedno.
BEGIN;
INSERT INTO colors (ColorId, Name)
VALUES (1, 'Green'), (2, 'Red'), (3, 'Yellow');
INSERT INTO fruits (FruitId, Name)
VALUES (1, 'Apple'), (2, 'Pear'), (3, 'Banana');
INSERT INTO vegetables (VegetableId, Name)
VALUES (1, 'Cucumber');
INSERT INTO fruit_colors (FruitId, ColorId) VALUES (1, 1), (1, 2);
INSERT INTO fruit_colors (FruitId, ColorId) VALUES (3, 3);
INSERT INTO vegetable_colors (VegetableId, ColorId) VALUES (1, 1);
COMMIT;

-- @block Vežba 2: Prikaži boje povezane sa jabukom
SELECT f.Name AS fruit, c.Name AS color
FROM fruits AS f
JOIN fruit_colors AS fc ON fc.FruitId = f.FruitId
JOIN colors AS c ON c.ColorId = fc.ColorId
WHERE f.FruitId = 1
ORDER BY c.Name;

-- Rezultat: Pear | 0, Banana | 1, Apple | 2.
-- @block Granični slučaj: nula, jedna ili više boja
SELECT f.FruitId, f.Name AS fruit, COUNT(fc.ColorId) AS color_count
FROM fruits AS f
LEFT JOIN fruit_colors AS fc ON fc.FruitId = f.FruitId
GROUP BY f.FruitId, f.Name
ORDER BY color_count, f.FruitId;

-- Očekivani rezultat: Pear. FK ograničenja proveravaju postojeće veze,
-- ali ne zahtevaju minimum od jedne boje za svaki red voća.
-- @block Granični slučaj: voće bez boje
SELECT f.FruitId, f.Name
FROM fruits AS f
WHERE NOT EXISTS (
    SELECT 1
    FROM fruit_colors AS fc
    WHERE fc.FruitId = f.FruitId
);

-- Isti zapis boje može biti upotrebljen u obe povezničke tabele.
-- @block Vežba 2: Boja koja se deli između voća i povrća
SELECT c.ColorId, c.Name AS shared_color
FROM colors AS c
WHERE EXISTS (
    SELECT 1 FROM fruit_colors AS fc WHERE fc.ColorId = c.ColorId
)
AND EXISTS (
    SELECT 1 FROM vegetable_colors AS vc WHERE vc.ColorId = c.ColorId
)
ORDER BY c.ColorId;

-- @block Vežba 2: Provera referencijalnog integriteta
PRAGMA foreign_key_check;

-- VEŽBA 3: relacije u Chinook proveri u CLI-ju sa .schema albums,
-- .schema tracks i .schema playlist_track, dok je otvorena Chinook
-- kopija. Upiti za proveru podataka su u dnevniku za Dan 05.
--
-- VEŽBA 4: mapiranje SQLAlchemy klase i Pydantic šeme je objašnjeno
-- u dnevniku; samo pravljenje ORM objekta ne upisuje red.
--
-- VEŽBA 5: FastAPI -> Pydantic -> SQLAlchemy -> sqlite3 drajver ->
-- SQLite tabela, pa povratni odgovor. Dijagram je u dnevniku.
