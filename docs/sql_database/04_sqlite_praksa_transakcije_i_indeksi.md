# 04 SQLite praksa, transakcije i indeksi

## Zašto SQLite za početak

SQLite je serverless baza, koja čuva podatke u jednom fajlu.
Prednosti za učenje:

- brz start i jednostavno korišćenje
- nema posebne instalacije server procesa
- odlična za lokalni razvoj i prototipe

Ograničenja:

- nije idealna za jake konkurentne `write` scenarije (više paralelnih upisa)

- manje opcija za enterprise skaliranje nego PostgreSQL

---

## Kako SQLite čuva podatke

Sve ide u .db fajl.
Taj fajl možeš backup-ovati, premestiti, verzionisati oprezno.

---

## Transakcija

Transakcija je grupa promena koje se tretiraju kao celina.
Ili sve prođe, ili ništa ne ostane (rollback).

ACID skraćeno:

- Atomicity
- Consistency
- Isolation
- Durability

Za backend ovo znači sigurnost podataka i predvidivo ponašanje, čak i kada dođe do greške u toku izvršavanja upita.

---

## Primer transakcije

```sql
BEGIN;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;
```

Ako druga komanda padne, radi se ROLLBACK. U suprotnom, sve promene se trajno čuvaju.

## Zaključavanje i konkurentnost u SQLite

---

SQLite podržava više čitanja, ali upis može biti usko grlo.
U FastAPI app-u to je prihvatljivo za manji projekat, učenje i MVP.

---

## WAL mode

Write-Ahead Logging mode često poboljšava konkurentnost čitanja.
Koristan je kad app ima više paralelnih zahteva.

---

## Indeksi

Indeks ubrzava pretragu, ali usporava upis.

Koristi indeks kada:

- često filtriraš po koloni
- često sortiraš po koloni
- često JOIN-uješ po koloni

Primer:

```sql
CREATE INDEX idx_items_owner_id ON items(owner_id);
```

## Composite index

Ako često radiš upit po owner_id i created_at:

```sql
CREATE INDEX idx_items_owner_created ON items(owner_id, created_at);
```

Redosled kolona u indeksu je bitan.

---

## Kako proceniti da li indeks treba

1. Pogledaj realne upite.
2. Meri spor upit pre indeksa.
3. Dodaj indeks.
4. Ponovo meri.

Ne indeksirati sve naslepo.

---

## Integritet i pragma podešavanja

SQLite ima korisna PRAGMA podešavanja.
Bitno: foreign key provere treba da budu uključene. To se radi komandom:

```sql
PRAGMA foreign_keys = ON;
```

---

## Backup i oprez

- pre većih izmena napravi backup .db fajla
- izbegavaj ručne izmene baze bez migracija kad app poraste

---

## Zadaci

1. Kreiraj SQLite bazu i 3 tabele users, categories, items.
2. Dodaj 2 indeksa koja deluju smisleno.
3. Napiši primer transakcije sa dve UPDATE komande.
4. Objasni kada bi prešao sa SQLite na PostgreSQL.

---

## Zaključak

SQLite je odličan most između teorije i realnog rada sa bazom.
Sledeće ide SQLAlchemy, koji ti omogućava Pythonic rad nad SQL bazom.
