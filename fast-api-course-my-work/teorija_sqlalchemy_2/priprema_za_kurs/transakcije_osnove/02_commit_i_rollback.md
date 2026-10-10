# 02: `COMMIT` i `ROLLBACK`

## `COMMIT` potvrđuje uspešan posao

U SQLite SQL-u transakcija može biti započeta i završena ovako:

```sql
BEGIN;

INSERT INTO note (text) VALUES ('Prvi zapis');
INSERT INTO note (text) VALUES ('Drugi zapis');

COMMIT;
```

Posle uspešnog `COMMIT`-a baza potvrđuje izmene. Ako oba INSERT-a pripadaju jednoj transakciji, ona predstavljaju jednu celinu.

## `ROLLBACK` poništava nepotvrđene promene

Ako se pre `COMMIT`-a ispostavi da je došlo do greške, transakcija se može poništiti:

```sql
BEGIN;

INSERT INTO note (text) VALUES ('Ovaj red neće ostati');

ROLLBACK;
```

Posle rollback-a, INSERT iz te transakcije nije sačuvan. `ROLLBACK` ne može vratiti promenu koja je već potvrđena ranijim `COMMIT`-om.

## Mala demonstracija preko Python `sqlite3`

Ovaj primer koristi privremenu bazu u memoriji, pa ne pravi `.db` fajl:

```python
import sqlite3

connection = sqlite3.connect(":memory:")
connection.execute(
    "CREATE TABLE note (id INTEGER PRIMARY KEY, text TEXT NOT NULL)"
)
connection.commit()

connection.execute("BEGIN")
connection.execute("INSERT INTO note (text) VALUES (?)", ("sačuvan red",))
connection.commit()

connection.execute("BEGIN")
connection.execute("INSERT INTO note (text) VALUES (?)", ("poništen red",))
connection.rollback()

rows = connection.execute("SELECT text FROM note ORDER BY id").fetchall()
assert rows == [("sačuvan red",)]

connection.close()
```

Prvi `commit()` završava pripremnu izmenu šeme pre testnih koraka. Zatim jedna transakcija se potvrđuje, a druga se poništava. Završni `SELECT` proverava sačuvano stanje.

`?` je SQLite DBAPI `qmark` placeholder. Vrednost se šalje kao drugi argument `execute()`-u, a ne spaja u SQL string. Kod SQLAlchemy `text()` primera koristićemo imenovane parametre poput `:text`; dijalekt ih prevede za drajver.

## Greška usred transakcije

Ako se dogodi greška, rollback mora da se desi pre nego što nastavimo sa istom konekcijom ili ORM sesijom:

```python
try:
    connection.execute(
        "INSERT INTO note (id, text) VALUES (?, ?)",
        (1, "prvi pokušaj"),
    )
    connection.execute(
        "INSERT INTO note (id, text) VALUES (?, ?)",
        (1, "duplirani primarni ključ"),
    )
    connection.commit()
except sqlite3.IntegrityError:
    connection.rollback()
```

Drugi INSERT krši primarni ključ. Rollback poništava nepotvrđene izmene te transakcije. Ako se greška uhvati, ali se rollback ne pozove, konekcija može ostati u neuspešnom ili nedovršenom transakcijskom stanju.

## Ne potvrđuj korake nezavisno ako pripadaju istoj celini

Ovo su dve zasebne transakcije:

```sql
INSERT INTO account (id, balance) VALUES (1, 100);
COMMIT;

UPDATE account SET balance = balance - 30 WHERE id = 1;
COMMIT;
```

Ako drugi korak ne uspe, prvi ostaje potvrđen. Zato kod složenog posla granicu transakcije postavljamo oko celog skupa izmena koje treba da uspeju ili ne uspeju zajedno.

## Konekcija se ne commit-uje zatvaranjem

Nemoj mešati životni vek konekcije sa transakcijom:

- `connection.close()` završava korišćenje konekcije;
- `connection.commit()` potvrđuje trenutnu transakciju;
- `connection.rollback()` poništava nepotvrđene izmene.

U Python `sqlite3` API-ju `with connection:` može da potvrdi uspešan blok ili da ga rollback-uje ako se izuzetak dogodi. Taj kontekstni menadžer sam po sebi ne zatvara konekciju; nju treba zatvoriti ili koristiti drugi obrazac životnog veka. U SQLAlchemy-ju postoje zasebni kontekstni obrasci koje obrađuje naredna teorijska celina.

## Granice `COMMIT` i `ROLLBACK`

- `COMMIT` potvrđuje sve izmene trenutne transakcije, ne samo poslednji SQL iskaz.
- `ROLLBACK` poništava nepotvrđene izmene trenutne transakcije.
- `ROLLBACK` ne vraća podatke iz ranije potvrđenih transakcija.
- Ako transakcija sadrži samo SELECT, commit obično nije potreban za očuvanje rezultata; SELECT nije promenio redove.
- Kako baze tretiraju DDL (`CREATE TABLE`, `ALTER TABLE`) u transakcijama može da se razlikuje; tu temu ne generalizujemo iz SQLite primera. Pre potvrde proveri da li su povezani koraci uspeli i da li stanje zadovoljava pravila aplikacije.
