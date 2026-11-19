-- @block Vežba 1: Putanja baze
-- Lekcija: ../../../00_intro/01_what_is_sqlite.md
--
-- Poveži SQLTools na ChinookPractice. Svaki -- @block označava zaseban
-- upit: klikni Run on active connection iznad željenog bloka, ili označi samo SQL naredbu i izaberi SQLTools Connection: Run Selected Query.
-- Upiti služe samo za pregled i ne menjaju podatke.
--
-- VEŽBA 1: Pronađi Chinook bazu
--
-- Terminal, iz korena repozitorijuma:
-- pwd
-- sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
--
-- Zatim u SQLite CLI prompt-u:
-- .databases
-- .tables
-- .quit
--
-- Koristimo radnu kopiju chinook_practice.db. Lekcija navodi original
-- chinook/chinook.db, koji ostaje neizmenjen. .databases treba da pokaže
-- putanju radne kopije kada nju otvoriš.
--
-- VEŽBA 2: Istraži šemu i ključeve
--
-- U SQLite CLI-ju definicije možeš pregledati pomoću:
-- .schema albums
-- .schema tracks
-- .schema playlist_track
--
-- Ključevi pronađeni u šemi:
-- albums:
--   PK: AlbumId
--   FK: ArtistId -> artists.ArtistId
-- tracks:
--   PK: TrackId
--   FK: AlbumId -> albums.AlbumId
--   FK: GenreId -> genres.GenreId
--   FK: MediaTypeId -> media_types.MediaTypeId
-- playlist_track:
--   složeni PK: (PlaylistId, TrackId)
--   FK: PlaylistId -> playlists.PlaylistId
--   FK: TrackId -> tracks.TrackId
--
-- ERD prikazuje veze linijama i oznakama kardinalnosti, a SQL šema ih
-- definiše kroz FOREIGN KEY, PRIMARY KEY i druga ograničenja.
-- Na primer, za albums.ArtistId šema navodi ON DELETE NO ACTION i
-- ON UPDATE NO ACTION, dok dijagram te akcije ne prikazuje.
-- Zato dijagram nije zamena za proveru šeme i ponašanja baze.
--
-- VEŽBA 3: Verzija i provera stranih ključeva
--
-- Verzija pripada SQLite biblioteci koju koristi trenutni alat.
-- SQLTools i sqlite3 CLI ne moraju koristiti istu verziju.
-- Za PRAGMA foreign_keys, 1 znači uključeno, a 0 isključeno.
-- Pokreni oba upita i u CLI-ju, pa zabeleži rezultate za svaku konekciju.
-- PRAGMA foreign_keys je podešavanje pojedinačne konekcije: rezultat u
-- SQLTools-u ne garantuje isto stanje u CLI-ju ili FastAPI aplikaciji.
-- Kada su provere isključene, izmene mogu narušiti referencijalni integritet.
-- Aplikacija koja se oslanja na te provere treba da ih uključi za svaku
-- konekciju i proveri da su uključene.
--
-- VEŽBA 4: Izaberi bazu za scenario
--
-- 1. Lična kolekcija muzike: SQLite je razuman izbor za lokalni fajl,
--    mali broj korisnika i ograničen broj istovremenih upisa.
-- 2. Lokalni FastAPI testovi: SQLite je praktičan za brzu pripremu
--    izolovane baze; nije nužno zamena za testiranje na produkcionoj bazi.
-- 3. API sa mnogo istovremenih upisa iz više instanci: razmotri
--    klijent-server bazu, npr. PostgreSQL, zbog centralnog pristupa i
--    podrške za konkurentne upise. SQLite ima jednog zapisivača u datom
--    trenutku, pa može postati usko grlo.
--
-- VEŽBA 5: Putanja podatka kroz FastAPI
--
-- HTTP zahtev -> FastAPI -> Pydantic -> SQLAlchemy -> SQLite drajver
-- -> SQLite biblioteka -> fajl baze -> odgovor klijentu.
--
-- FastAPI prima zahtev i poziva odgovarajući endpoint.
-- Pydantic validira i parsira podatke prema definisanoj šemi.
-- SQLAlchemy priprema rad sa modelima, upitima i transakcijom.
-- SQLite drajver povezuje Python sa SQLite bibliotekom.
-- SQLite biblioteka izvršava SQL i upravlja podacima u fajlu baze.
-- COMMIT potvrđuje transakciju; endpoint zatim može vratiti odgovor.
--
-- Ovaj prvi SQL upit prikazuje putanju otvorene baze:
PRAGMA database_list;

-- @block Vežba 1: Tražene tabele
SELECT name
FROM sqlite_schema
WHERE type = 'table'
  AND name IN ('artists', 'albums', 'tracks', 'customers', 'invoices')
ORDER BY name;

-- @block Vežba 2: Definicije tabela
SELECT name, sql
FROM sqlite_schema
WHERE type = 'table'
  AND name IN ('albums', 'tracks', 'playlist_track')
ORDER BY name;

-- @block Vežba 3: SQLite verzija
SELECT sqlite_version() AS sqlite_verzija;

-- @block Vežba 3: Provera stranih ključeva
PRAGMA foreign_keys;
