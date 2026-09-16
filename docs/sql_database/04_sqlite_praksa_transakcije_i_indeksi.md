# 04 SQLite praksa, transakcije i indeksi

## Zasto SQLite za pocetak

SQLite je serverless baza, cuva podatke u jednom fajlu.
Prednosti za ucenje:

- brz start
- nema posebne instalacije server procesa
- odlicna za lokalni razvoj i prototipe

Ogranicenja:

- nije idealna za jake konkurentne write scenarije
- manje opcija za enterprise skaliranje nego PostgreSQL

## Kako SQLite cuva podatke

Sve ide u .db fajl.
Taj fajl mozes backup-ovati, premestiti, verzionisati oprezno.

## Transakcija

Transakcija je grupa promena koje se tretiraju kao celina.
Ili sve prodje, ili nista ne ostane (rollback).

ACID skraceno:

- Atomicity
- Consistency
- Isolation
- Durability

Za backend ovo znaci sigurnost podataka i predvidivo ponasanje.

## Primer transakcije

```sql
BEGIN;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;
```

Ako druga komanda padne, radi se ROLLBACK.

## Zakljucavanje i konkurentnost u SQLite

SQLite podrzava vise citanja, ali upis moze biti usko grlo.
U FastAPI app to je prihvatljivo za manji projekat, ucenje i MVP.

## WAL mode

Write-Ahead Logging mode cesto poboljsava konkurentnost citanja.
Koristan je kad app ima vise paralelnih zahteva.

## Indeksi

Indeks ubrzava pretragu, ali usporava upis.

Koristi indeks kada:

- cesto filtriras po koloni
- cesto sortiras po koloni
- cesto JOIN-ujes po koloni

Primer:

```sql
CREATE INDEX idx_items_owner_id ON items(owner_id);
```

## Composite index

Ako cesto radis upit po owner_id i created_at:

```sql
CREATE INDEX idx_items_owner_created ON items(owner_id, created_at);
```

Redosled kolona u indeksu je bitan.

## Kako proceniti da li indeks treba

1. Pogledaj realne upite.
2. Meri spor upit pre indeksa.
3. Dodaj indeks.
4. Ponovo meri.

Ne indeksirati sve naslepo.

## Integritet i pragma podesavanja

SQLite ima korisna PRAGMA podesavanja.
Bitno: foreign key provere treba da budu ukljucene.

## Backup i oprez

- pre vecih izmena napravi backup .db fajla
- izbegavaj rucne izmene baze bez migracija kad app poraste

## Zadaci

1. Kreiraj SQLite bazu i 3 tabele users, categories, items.
2. Dodaj 2 indeksa koja deluju smisleno.
3. Napisi primer transakcije sa dve UPDATE komande.
4. Objasni kada bi presao sa SQLite na PostgreSQL.

## Zakljucak

SQLite je odlican most izmedju teorije i realnog rada sa bazom.
Sledece ide SQLAlchemy, koji ti omogucava Pythonic rad nad SQL bazom.
