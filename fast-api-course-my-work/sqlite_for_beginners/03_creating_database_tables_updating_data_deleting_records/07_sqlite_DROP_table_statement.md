# 07 — SQLite `DROP TABLE` naredba

## Cilj lekcije

`DROP TABLE` uklanja tabelu iz baze podataka. Za razliku od `DELETE`, koji uklanja redove ali ostavlja tabelu, `DROP TABLE` uklanja i podatke i definiciju tabele. U ovoj lekciji ćemo bezbedno ukloniti tabelu `groups` iz privremene baze i proveriti šta se događa sa njenim povezanim redovima.

> **Upozorenje:** `DROP TABLE` je destruktivna DDL naredba. Ne izvršavaj je nad bazom aplikacije, kursa ili bilo kojim podacima koje želiš da sačuvaš. Primeri su namenjeni isključivo novoj `:memory:` bazi.

## Priprema probne baze

U SQLite CLI-ju otvori privremenu bazu:

```bash
sqlite3 :memory:
```

Uključi proveru stranih ključeva za tu konekciju:

```sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
```

Očekivani rezultat je `1`. Zatim napravi tabele kao u [lekciji o `CREATE TABLE`](./03_sqlite_create_table_statement_part_2.md) i unesi probne podatke:

```sql
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT UNIQUE
);

CREATE TABLE groups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE contact_groups (
    contact_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    PRIMARY KEY (contact_id, group_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
        ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id)
        ON DELETE CASCADE
) WITHOUT ROWID;

INSERT INTO contacts (first_name, last_name, email)
VALUES
    ('Johnny', 'Cash', 'johnny.cash@example.test'),
    ('Jane', 'Doe', 'jane.doe@example.test');

INSERT INTO groups (name)
VALUES ('Cash Flow'), ('Accounts');

INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1), (1, 2), (2, 1);
```

Pre bilo kakve izmene pogledaj trenutne tabele i podatke:

```text
.tables
.schema groups
```

```sql
SELECT id, name FROM groups;
SELECT contact_id, group_id FROM contact_groups;
```

U ovoj novoj bazi očekujemo tri tabele (`contacts`, `groups`, `contact_groups`), dve grupe i tri reda članstva.

## Osnovni oblik naredbe

```sql
DROP TABLE table_name;
```

Za uklanjanje grupe iz probne baze:

```sql
DROP TABLE groups;
```

Potvrdi da je tabela nestala iz šeme:

```text
.tables
.schema groups
```

`groups` se više ne prikazuje. Ako pokušaš da je upitaš:

```sql
SELECT * FROM groups;
```

SQLite će prijaviti da tabela `groups` ne postoji. Ta greška je očekivana u ovoj demonstraciji: tabela i njeni podaci su uklonjeni.

SQLite CLI komanda `.tables` prikazuje tabele koje postoje na toj konekciji. U eksternom Viewer-u ili SQLTools-u možda će biti potrebno osvežiti prikaz, jer ekstenzija može prikazivati ranije učitanu listu.

## Šta tačno uklanja `DROP TABLE`?

Kada se tabela izbriše, uklanjaju se:

- definicija tabele iz šeme baze;
- svi redovi koji su bili sačuvani u tabeli;
- indeksi i okidači (triggers) povezani sa tom tabelom.

Ostale nepovezane tabele i sama SQLite datoteka baze ostaju. `DROP TABLE groups` ne briše bazu kao celinu.

Za poređenje:

| Naredba | Efekat |
|---|---|
| `DELETE FROM groups;` | Briše sve redove iz `groups`, ali tabela i njena definicija ostaju. |
| `DROP TABLE groups;` | Briše tabelu `groups`, njene podatke, indekse i okidače (triggers) vezane za nju. |

`DROP TABLE` nema `WHERE` uslov. Ako želiš da ukloniš samo jedan ili nekoliko redova, koristi `DELETE` sa pažljivo proverenim `WHERE` uslovom, kao u [prethodnoj lekciji](./06_sqlite_DELETE_statement.md).

## Strani ključevi i povezane tabele

U našem modelu `contact_groups.group_id` referencira `groups.id` i koristi `ON DELETE CASCADE`. Kada je provera stranih ključeva uključena, SQLite pri `DROP TABLE groups` prvo izvršava implicitno brisanje redova grupe. Zbog kaskade uklanjaju se i redovi članstva koji upućuju na grupe.

Pošto se ovde uklanja **cela** tabela `groups`, svi njeni redovi nestaju, pa se brišu i sva članstva u `contact_groups`. Tabela `contact_groups` i kontakti ostaju:

```sql
PRAGMA foreign_keys;

DROP TABLE groups;

SELECT COUNT(*) FROM contact_groups;
SELECT COUNT(*) FROM contacts;
```

U pripremljenom primeru očekuješ `0` redova u `contact_groups` i `2` kontakta u `contacts`. `PRAGMA foreign_keys` mora vratiti `1` da bi SQLite sproveo deklarisana FK pravila na toj konekciji.

Ovo ponašanje zavisi od šeme i FK podešavanja. Sa uključenim stranim ključevima, ako implicitno brisanje pre uklanjanja tabele prekrši ograničenje bez odgovarajuće kaskadne akcije, naredba može da ne uspe i tabela neće biti uklonjena. Zato proveri zavisne tabele i ograničenja pre `DROP TABLE`.

SQLite uklanja okidače koji pripadaju tabeli pre implicitnog brisanja, pa se ti okidači ne pokreću kao posledica tog internog brisanja. Ovo je još jedan razlog da se `DROP TABLE` ne posmatra kao običan `DELETE` nad redovima.

## `IF EXISTS`

Ako tabela možda ne postoji, možeš koristiti:

```sql
DROP TABLE IF EXISTS groups;
```

Ako `groups` postoji, biće uklonjena. Ako ne postoji, SQLite neće prijaviti grešku samo zbog njenog nepostojanja. Ova opcija je korisna u skriptama koje čiste privremenu šemu pre ponovnog kreiranja.

`IF EXISTS` nije bezbednosna potvrda i ne sprečava brisanje pogrešne postojeće tabele. Takođe ne skriva druge greške, kao što su problemi sa stranim ključevima. Proveri bazu i naziv tabele pre izvršavanja.

## Može li transakcija da poništi `DROP TABLE`?

SQLite podržava transakcije oko ove operacije. U probnoj bazi možeš proveriti da `ROLLBACK` vraća i šemu i podatke:

```sql
BEGIN;

DROP TABLE groups;

.tables
```

`.tables` će tokom transakcije pokazati da `groups` više nije dostupna. Sada poništi transakciju:

```sql
ROLLBACK;
```

Proveri da li su tabela i podaci vraćeni:

```text
.tables
```

```sql
SELECT id, name FROM groups;
SELECT contact_id, group_id FROM contact_groups;
```

U ovom primeru se očekuju obe grupe i sva tri reda članstva. Ako umesto `ROLLBACK` izvršiš `COMMIT`, uklanjanje postaje potvrđena promena baze. Transakcija nije zamena za rezervnu kopiju: radi samo dok je transakcija aktivna i ne štiti od kasnijeg gubitka ili oštećenja datoteke.

## SQLAlchemy 2: uklanjanje tabele iz šeme

`Session.delete()` služi za brisanje ORM objekta i njegovog reda, ne za uklanjanje tabele. Za DDL operacije SQLAlchemy nudi `Table.drop()` i `MetaData.drop_all()`.

Koristeći `Group` i `engine` iz [SQLAlchemy mape u lekciji o `CREATE TABLE`](./03_sqlite_create_table_statement_part_2.md), možeš ukloniti samo tabelu `groups` iz **privremene baze**:

```python
from sqlalchemy import inspect


if not inspect(engine).has_table("groups"):
    raise LookupError("Tabela groups ne postoji.")

Group.__table__.drop(engine, checkfirst=True)

assert not inspect(engine).has_table("groups")
```

`Group.__table__.drop(...)` emituje DDL za tu tabelu. `checkfirst=True` proverava da li tabela postoji pre nego što se pokuša njeno uklanjanje. U ovom modelu `engine` mora imati uključen SQLite `PRAGMA foreign_keys`, kao što je prikazano u prethodnoj lekciji; zato se pri uklanjanju tabele sprovode i definisane kaskadne FK akcije.

SQLAlchemy takođe može ukloniti sve tabele koje su registrovane u metapodacima:

```python
Base.metadata.drop_all(engine)
```

Ova naredba je znatno šira od `Group.__table__.drop(...)`: može ukloniti sve mapirane tabele. Koristi je samo nad novom, privremenom ili namenski pripremljenom test bazom, nikada kao rutinsku aplikacionu operaciju nad produkcionom bazom.

U aplikaciji se promene šeme obično upravljaju migracijama (na primer Alembic), a ne pozivanjem `drop_all()` pri pokretanju aplikacije.

## Šta je transkript pojednostavio — važne ispravke

1. **`DROP TABLE` briše i strukturu i podatke.** Nije samo uklanjanje naziva iz liste tabela.
2. **Povezani redovi mogu biti pogođeni.** SQLite može izvršiti kaskadne FK akcije pre uklanjanja tabele; u našem modelu time se brišu redovi `contact_groups`.
3. **Ostale tabele ne nestaju automatski.** `contacts` i `contact_groups` ostaju, ali se njihovi podaci menjaju u skladu sa FK pravilima.
4. **CLI greška pri `SELECT`-u posle brisanja je očekivana.** Potvrdi uklanjanje preko `.tables` ili pregleda šeme, a ne samo pokušajem upita nad uklonjenom tabelom.
5. **`IF EXISTS` rešava samo slučaj nepostojeće tabele.** Ne proverava da li je bezbedno obrisati tabelu.
6. **Ne koristi produkcionu bazu za vežbu.** SQLAlchemy `drop_all()` je još šire destruktivan, jer cilja sve tabele u metapodacima.

## Vežbe

Sve vežbe radi u novoj `:memory:` bazi sa šemom i početnim podacima iz ove lekcije.

1. Prikaži tabele i sadržaj `groups` i `contact_groups` pre brisanja.
2. U transakciji izvrši `DROP TABLE groups`, proveri broj redova u `contact_groups`, a zatim uradi `ROLLBACK`. Potvrdi da su tabela i podaci vraćeni.
3. U novoj probnoj bazi izvrši `BEGIN;`, zatim `DROP TABLE groups;` i na kraju `COMMIT;`. Koje tabele ostaju? Koji podaci ostaju u `contacts` i `contact_groups`?
4. U drugoj svežoj probnoj bazi izvrši `DROP TABLE IF EXISTS groups` dva puta. Uporedi rezultat sa običnim `DROP TABLE` nad tabelom koja ne postoji.
5. Napravi indeks ili trigger vezan za probnu tabelu, ukloni tabelu i proveri šta se desilo sa tim objektom.
6. Pre uklanjanja neke druge roditeljske tabele razmotri strane ključeve koji na nju upućuju. Objasni koje pravilo (`CASCADE`, `RESTRICT`/`NO ACTION` ili neko drugo) važi u tvojoj šemi.
7. U SQLAlchemy probnoj bazi ukloni samo `Group.__table__`, pa proveri da li su `contacts` i `contact_groups` i dalje prisutne.
8. Objasni zašto `Base.metadata.drop_all(engine)` ne treba koristiti nad bazom sa važnim podacima.

## Provera razumevanja

1. Koja je razlika između `DELETE FROM groups` i `DROP TABLE groups`?
2. Šta se dešava sa indeksima i okidačima (triggers) vezanim za tabelu koja se uklanja?
3. Zašto se `contact_groups` redovi brišu kada se ukloni `groups` u ovom modelu?
4. Šta radi `DROP TABLE IF EXISTS` i šta **ne** garantuje?
5. Koja je razlika između SQLAlchemy `Session.delete()` i `Group.__table__.drop()`?
6. Kada je prihvatljivo koristiti `Base.metadata.drop_all(engine)`?
7. Kako `ROLLBACK` može pomoći tokom kontrolisane vežbe `DROP TABLE`?

## Izvori za dalje čitanje

- [SQLite: DROP TABLE](https://www.sqlite.org/lang_droptable.html)
- [SQLite: Foreign Key Support](https://www.sqlite.org/foreignkeys.html)
- [SQLite: Transactions](https://www.sqlite.org/lang_transaction.html)
- [SQLAlchemy 2.0: Creating and Dropping Database Tables](https://docs.sqlalchemy.org/en/20/core/metadata.html#creating-and-dropping-database-tables)
