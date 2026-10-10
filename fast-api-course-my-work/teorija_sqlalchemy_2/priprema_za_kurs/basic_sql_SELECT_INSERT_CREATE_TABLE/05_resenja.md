# 05: Rešenja — CREATE TABLE, INSERT i SELECT

Koristi rešenja tek pošto probaš zadatke iz [vežbi](04_vezbe.md). Primeri su za SQLite. Svaki blok je SQL koji se izvršava nad praznom probnom bazom, osim gde je drugačije navedeno.

## Rešenje 1: protumači tabelu

- `id` je primarni ključ i identifikuje red.
- `name` i `created_at` su obavezni zbog `NOT NULL`.
- `fullname` može biti SQL `NULL`.
- Ako INSERT izostavi `created_at`, SQLite koristi `DEFAULT CURRENT_TIMESTAMP`.

## Rešenje 2: dve povezane tabele

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE user_account (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    fullname TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE address (
    id INTEGER PRIMARY KEY,
    email_address TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES user_account(id)
);
```

`PRAGMA foreign_keys = ON` je SQLite-specifičan connection setting. U aplikaciji treba ga podesiti na svakoj DBAPI konekciji koja treba da sprovodi FK constraint.

## Rešenje 3: jedan korisnik

```sql
INSERT INTO user_account (name, fullname)
VALUES ('sandy', 'Sandy Cheeks');
```

`id` se izostavlja da bi SQLite dodelio primarni ključ, a `created_at` da bi se upotrebio njegov default.

## Rešenje 4: više korisnika

```sql
INSERT INTO user_account (name, fullname)
VALUES
    ('spongebob', 'SpongeBob SquarePants'),
    ('patrick', 'Patrick Star'),
    ('squidward', NULL);
```

Ovde je `NULL` vrednost, ne string. `fullname` nema `NOT NULL`, pa je dozvoljen.

## Rešenje 5: adrese

Pod pretpostavkom zadatka da Sandy ima ID 1, a SpongeBob ID 2:

```sql
INSERT INTO address (email_address, user_id)
VALUES
    ('sandy1@example.test', 1),
    ('sandy2@example.test', 1),
    ('spongebob@example.test', 2);
```

Brojevi 1 i 2 nisu magična SQL pravila. To su ID-jevi koje je SQLite dodelio u ovom konkretnom redosledu unosa u svežu bazu. U aplikaciji se koriste stvarno dobijeni ID-jevi ili ORM veze, ne pretpostavljen redosled.

## Rešenje 6: izaberi kolone i sortiraj

```sql
SELECT name, fullname
FROM user_account
ORDER BY name ASC;
```

`ASC` je podrazumevani smer, ali je ovde napisan radi čitljivosti.

## Rešenje 7: filtriranje

### Tačno ime

```sql
SELECT name, fullname
FROM user_account
WHERE name = 'sandy';
```

### Nepoznato puno ime

```sql
SELECT name
FROM user_account
WHERE fullname IS NULL;
```

Za `NULL` se koristi `IS NULL`, ne `= NULL`.

### Ime počinje sa `s`

```sql
SELECT name
FROM user_account
WHERE name LIKE 's%';
```

`%` odgovara bilo kom nizu znakova. Osetljivost na velika/mala slova može se razlikovati po bazi i kolaciji.

## Rešenje 8: dva uslova

```sql
SELECT id, name
FROM user_account
WHERE id > 1
  AND name <> 'patrick'
ORDER BY id;
```

`AND` zahteva da oba uslova budu tačna. `<>` znači „nije jednako“.

## Rešenje 9: INNER JOIN

```sql
SELECT u.name, a.email_address
FROM user_account AS u
JOIN address AS a ON a.user_id = u.id
ORDER BY u.name, a.email_address;
```

JOIN uslov uparuje samo adrese sa korisnikom čiji se ID nalazi u `address.user_id`. Ako korisnik ima dve adrese, dobićeš dva rezultujuća reda za njega.

## Rešenje 10: LEFT JOIN

```sql
SELECT u.name, a.email_address
FROM user_account AS u
LEFT JOIN address AS a ON a.user_id = u.id
ORDER BY u.name, a.email_address;
```

`LEFT JOIN` zadržava svaki korisnički red. Za korisnika bez odgovarajuće adrese nema vrednosti sa desne strane, pa je `a.email_address` u rezultatu `NULL`.

## Rešenje 11: bind parametar uz SQLAlchemy `text()`

```python
from sqlalchemy import text

statement = text(
    "SELECT id, name FROM user_account WHERE name = :name"
)
rows = connection.execute(statement, {"name": user_input}).all()
```

SQL struktura i vrednost su odvojene. `user_input` se prosleđuje kao podatak, a ne lepi se u SQL string. Konkretan placeholder oblik prilagođava SQLAlchemy dijalekt/drajver.

## Završna provera

- Kolona opisuje jednu vrstu podatka; red sadrži vrednosti jednog zapisa.
- `NULL` znači da vrednost nije prisutna; `''` je prisutan tekst dužine nula.
- Primarni ključ identifikuje red u svojoj tabeli; strani ključ upućuje na ključ reda druge tabele.
- `INSERT` dodaje red; `SELECT` čita rezultat.
- `WHERE` bira koji redovi ulaze u rezultat; `ORDER BY` određuje njihov redosled.
- JOIN `ON` povezuje redove po uslovu; bez uslova dve tabele proizvode kartezijanski proizvod.
