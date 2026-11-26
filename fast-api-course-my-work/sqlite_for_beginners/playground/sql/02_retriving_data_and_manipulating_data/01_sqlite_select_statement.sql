-- Lekcija: ../../../02_retriving_data_and_manipulating_data/01_sqlite_select_statement.md
-- Vežbaj u SQLTools-u povezanim na ChinookPractice ili u SQLite CLI-ju
-- otvorenom nad chinook_practice.db. Ovaj fajl sadrži samo SELECT upite.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma otvori radnu kopiju:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu učitaj ovaj fajl:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/01_sqlite_select_statement.sql
--
-- Upiti bez FROM-a računaju izraze i ne čitaju tabelu. Ostali blokovi
-- čitaju podatke iz Chinook-a; nijedan blok ne menja bazu.

-- @block Vežba 1.1: Saberi bez tabele
SELECT 7 + 7 AS zbir;

-- Očekivani rezultat: jedna kolona (zbir) i jedna vrednost (14).

-- @block Vežba 1.2: Dva izraza u istom rezultatu
SELECT
    10 / 2 AS rezultat_deljenja,
    3 * 5 AS rezultat_mnozenja;

-- Očekivani rezultat: rezultat_deljenja = 5, rezultat_mnozenja = 15.

-- @block Vežba 1.3: Celobrojno i realno deljenje u SQLite-u
SELECT
    5 / 2 AS celobrojno,
    5.0 / 2 AS decimalno;

-- Očekivani rezultat: celobrojno = 2, decimalno = 2.5.
-- U prvom izrazu oba operanda su celi brojevi, pa se rezultat deli
-- celobrojno. U drugom je jedan operand REAL.

-- @block Vežba 1.4: Smisleni aliasi za izraze
SELECT
    7 + 7 AS broj_dana_u_dve_nedelje,
    10 / 2 AS polovina_deset,
    3 * 5 AS pet_grupa_od_tri;

-- @block Vežba 2: Prvih pet albuma
SELECT AlbumId, Title
FROM albums
ORDER BY AlbumId
LIMIT 5;

-- U radnoj Chinook kopiji prva vrednost AlbumId je 1.
-- Rezultat sadrži samo AlbumId i Title, ne sve kolone albums tabele.
-- ERD opisuje strukturu tabele i veze; SELECT vraća trenutne redove.

-- @block Vežba 3.1: ArtistId za svaki album, uključujući ponavljanja
SELECT ArtistId
FROM albums
ORDER BY ArtistId;

-- @block Vežba 3.2: Jedinstvene ArtistId vrednosti u rezultatu
SELECT DISTINCT ArtistId
FROM albums
ORDER BY ArtistId;

-- DISTINCT uklanja duplikate samo iz ovog rezultata. Tabela albums
-- ostaje neizmenjena. Poredi broj redova ova dva upita.

-- @block Vežba 3.3: Jedinstvene kombinacije ArtistId i Title
SELECT DISTINCT ArtistId, Title
FROM albums
ORDER BY ArtistId, Title;

-- DISTINCT ovde poredi ceo par kolona. Isti ArtistId može se ponoviti
-- ako se razlikuje Title; rezultat nije spisak jedinstvenih umetnika.

-- @block Vežba 4: Prepoznaj ulogu klauzula
SELECT ArtistId, COUNT(*) AS album_count
FROM albums
WHERE ArtistId > 0
GROUP BY ArtistId
HAVING COUNT(*) > 1
ORDER BY album_count DESC, ArtistId ASC
LIMIT 5;

-- SELECT: bira kolonu ArtistId i izračunat broj albuma.
-- FROM: čita ulazne redove iz albums.
-- WHERE: odbacuje redove sa ArtistId <= 0 pre grupisanja.
-- GROUP BY: pravi po jednu grupu za svaki ArtistId.
-- HAVING: zadržava grupe koje imaju više od jednog albuma.
-- ORDER BY: sortira po broju albuma, opadajuće; ArtistId razrešava
-- izjednačenja da bi LIMIT 5 vraćao predvidive grupe.
-- LIMIT: prikazuje najviše pet grupa.
