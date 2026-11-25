-- Lekcija: ../../../00_intro/03_how_to_connect_to_sqlite.md
-- SQL provere za vežbe povezivanja. Izvršavaj nad chinook_practice.db
-- otvorenom sa -readonly; SQL naredbe u ovom fajlu ne menjaju bazu.
--
-- Dot-komande kao .databases, .tables i .schema nisu SQL i unose se
-- direktno u SQLite CLI prompt, a ne u SQLTools upit.
--
-- VEŽBA 1: prvo iz root-a repozitorijuma otvori radnu kopiju:
-- sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- Zatim u CLI-ju pokreni .databases, .tables i .schema albums.

-- @block Vežba 1: Putanja otvorene baze
PRAGMA database_list;

-- @block Vežba 1: Broj korisničkih tabela
SELECT COUNT(*) AS broj_tabela
FROM sqlite_schema
WHERE type = 'table'
  AND name NOT LIKE 'sqlite_%';

-- VEŽBA 2: Dijagram tri zasebne konekcije ka jednom fajlu nalazi se
-- u dan_05_intro_and_cli_vezbe.md i u lekciji.

-- VEŽBA 3: pwd se izvršava u Bash-u, ne u SQLite CLI-ju.
-- Uporedi pwd sa putanjom iz PRAGMA database_list / .databases.

-- VEŽBA 4: CLI koristi putanju i dot-komande; GUI otvara fajl kroz
-- interfejs. Disconnect/.quit zatvara konekciju, ne briše fajl.

-- @block Vežba 5: SQLite verzija ovog klijenta
SELECT sqlite_version() AS sqlite_verzija;

-- @block Vežba 5: Lista baza ove konkretne konekcije
PRAGMA database_list;

-- @block Vežba 5: Provera FK podešavanja ove konkretne konekcije
PRAGMA foreign_keys;

-- U vežbi 5 se poredi TodoApp URL sa radnim direktorijumom stvarnog
-- server procesa. Pogledaj rešenje u dnevniku; samo učitaj ovaj fajl
-- nad Chinook kopijom i ne pokreći ga umesto provere aplikacije.
