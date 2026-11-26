-- Lekcija: ../../../02_retriving_data_and_manipulating_data/08_sqllite_data_types.md
-- Lekcija pokriva SQLite storage classes, afinitet i STRICT tabele.
-- Upiti nad Chinook čitaju bazu; demonstracioni objekti su isključivo
-- TEMP tabele i postoje samo u trenutnoj konekciji.
--
-- Koristi SQLTools konekciju ka ChinookPractice ili u CLI-ju:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- Zatim u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/08_sqllite_data_types.sql
--
-- TEMP tabele mogu da se prave i uz read-only glavnu bazu; ne menjaju
-- chinook_practice.db. Pokreni setup blokove i test blokove u istoj
-- konekciji. Zatvaranjem konekcije privremene tabele se uklanjaju.
-- STRICT zahteva SQLite 3.37.0 ili noviji. Proveri verziju u prvom
-- bloku; ako je starija, nemoj pokretati strict_demo setup blok.
-- Ne učitavaj ceo fajl odjednom u starijem klijentu.

-- @block Proveri verziju SQLite klijenta pre STRICT primera
SELECT sqlite_version() AS sqlite_version;

-- @block Vežba 1: Storage class izraza
SELECT
    typeof(100) AS integer_class,
    typeof(10.5) AS real_class,
    typeof('SQLite') AS text_class,
    typeof(X'53514C') AS blob_class,
    typeof(NULL) AS null_class;

-- Očekivano: integer, real, text, blob, null.

-- @block Vežba 2: Chinook deklarisani tipovi
PRAGMA table_info(tracks);

-- @block Vežba 2: Stvarni storage class vrednosti u tracks
SELECT
    typeof(TrackId) AS track_id_class,
    typeof(Name) AS name_class,
    typeof(Milliseconds) AS milliseconds_class,
    typeof(UnitPrice) AS unit_price_class
FROM tracks
LIMIT 1;

-- U postojećim redovima se očekuju integer, text, integer i real.
-- PRAGMA pokazuje deklaraciju kolone; typeof() proverava sačuvanu vrednost.

-- @block Vežba 2 setup: Pripremi bezbednu affinity_demo TEMP tabelu
DROP TABLE IF EXISTS temp.affinity_demo;
CREATE TEMP TABLE affinity_demo (
    integer_value INTEGER,
    text_value TEXT,
    blob_value BLOB
);
INSERT INTO affinity_demo
VALUES ('42', 42, X'53514C');

-- @block Vežba 2: Proveri afinitet konverzijom i typeof()
SELECT
    integer_value,
    typeof(integer_value) AS integer_class,
    text_value,
    typeof(text_value) AS text_class,
    blob_value,
    typeof(blob_value) AS blob_class
FROM affinity_demo;

-- '42' se u INTEGER koloni čuva kao integer 42; broj 42 se u TEXT
-- koloni čuva kao tekst '42'. X'53514C' ostaje BLOB.

-- @block Ivični slučaj setup: Obična INTEGER kolona je fleksibilna
DROP TABLE IF EXISTS temp.flexible_integer;
CREATE TEMP TABLE flexible_integer (value INTEGER);
INSERT INTO flexible_integer VALUES ('not a number');

-- @block Ivični slučaj: Neusaglašen tekst u običnoj INTEGER koloni
SELECT value, typeof(value) AS storage_class
FROM flexible_integer;

-- Obična tabela prihvata tekst koji ne može da konvertuje u integer.

-- @block Vežba 3 setup: STRICT tabela (zahteva SQLite 3.37.0+)
DROP TABLE IF EXISTS temp.strict_demo;
CREATE TEMP TABLE strict_demo (
    value INTEGER
) STRICT;
INSERT INTO strict_demo VALUES (42.0);
INSERT INTO strict_demo VALUES (NULL);

-- @block Vežba 3: Lossless konverzija i NULL u STRICT koloni
SELECT value, typeof(value) AS storage_class
FROM strict_demo
ORDER BY value;

-- 42.0 se bez gubitka pretvara u integer 42. NULL je dozvoljen jer
-- kolona nije NOT NULL: STRICT ne dodaje NOT NULL automatski.

-- Sledeći pokušaji su namerno komentarisani jer očekivano izazivaju grešku.
-- Pokreni ih jedan po jedan samo ako želiš da proveriš odbijanje vrednosti:
-- INSERT INTO strict_demo VALUES ('not a number');
-- INSERT INTO strict_demo VALUES (42.5);
-- STRICT INTEGER prihvata 42.0 (lossless), ali odbija tekstualni broj
-- koji ne može da se konvertuje i realni broj 42.5 koji gubi preciznost.

-- @block Dodatna provera: Boolean i SQLite storage class
SELECT
    TRUE AS true_value,
    typeof(TRUE) AS true_class,
    FALSE AS false_value,
    typeof(FALSE) AS false_class;

-- TRUE/FALSE su vrednosti 1/0, storage class im je integer.

-- @block Dodatna provera: Primeri zapisa datuma i vremena
SELECT
    typeof('2025-03-08 14:30:00') AS iso_text_class,
    typeof(julianday('2025-03-08 14:30:00')) AS julian_day_class,
    typeof(CAST(strftime('%s', '2025-03-08 14:30:00') AS INTEGER)) AS unix_time_class;

-- Datumi su tekst, REAL ili INTEGER vrednosti; SQLite nema posebnu
-- DATE/DATETIME storage class. strftime('%s') daje tekst, pa ga CAST
-- pretvara u celobrojni broj sekundi od Unix epohe.

-- @block Vežba 4: Deklarisani i stvarni tipovi nisu isto
PRAGMA table_info(tracks);

-- @block Vežba 4: Proveri storage class u Chinook redu
SELECT
    TrackId,
    typeof(TrackId) AS track_id_class,
    Name,
    typeof(Name) AS name_class,
    Milliseconds,
    typeof(Milliseconds) AS milliseconds_class,
    UnitPrice,
    typeof(UnitPrice) AS unit_price_class
FROM tracks
LIMIT 1;

-- @block Ivični slučaj: Približna REAL aritmetika
SELECT 0.1 + 0.2 AS floating_point_sum,
       typeof(0.1 + 0.2) AS storage_class;

-- REAL je binarni floating-point tip; ne oslanjaj se na njega za
-- novčanu tačnost bez dodatnog dizajna (npr. čuvanje centi kao INTEGER).
