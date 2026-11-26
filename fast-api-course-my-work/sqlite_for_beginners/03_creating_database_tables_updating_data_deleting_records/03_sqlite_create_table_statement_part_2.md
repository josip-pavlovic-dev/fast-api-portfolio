# 03 — SQLite `CREATE TABLE` izjava (2. deo)

## Cilj lekcije

U [prvom delu lekcije](./02_sqlite_create_table_statement_part_1.md) isplanirali smo adresar i vezu N:M između kontakata i grupa. Sada ćemo napraviti tri tabele koje taj model sprovode:

1. `contacts` — podaci o kontaktima;
2. `groups` — grupe kontakata;
3. `contact_groups` — redovi koji povezuju kontakt sa grupom.

Koristićemo primarne i strane ključeve, jedinstvena ograničenja i SQLAlchemy 2 mapiranje. Primer izvršavaj u novoj memorijskoj bazi, ne nad bazom kursa ili aplikacije.

## Priprema SQLite CLI-ja

U terminalu otvori privremenu bazu:

```bash
sqlite3 :memory:
```

SQLite podržava deklarisanje stranih ključeva, ali njihova provera mora biti uključena za svaku konekciju. U ovom CLI-ju to uradi pre kreiranja tabela i pre početka transakcije:

```sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
```

Očekivani rezultat druge naredbe je `1`. Ovo podešavanje važi samo za tu konekciju; uključi ga i u drugim klijentima, kao što su aplikacija ili SQLTools.

## 1. Tabela `contacts`

Prvo pravimo tabelu kontakata:

```sql
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT UNIQUE
);
```

- `id INTEGER PRIMARY KEY` je primarni ključ kontakta. U običnoj SQLite tabeli, `INTEGER PRIMARY KEY` je alias za `rowid`; kada `id` izostavimo pri unosu, SQLite može dodeliti vrednost.
- `first_name` i `last_name` moraju imati vrednost zbog `NOT NULL`. To samo odbija SQL `NULL`; ne odbija prazan tekst.
- `email` je obavezan i jedinstven u ovoj šemi.
- `phone` je jedinstven, ali namerno nije obavezan: `NULL` je dozvoljen. SQLite dopušta više `NULL` vrednosti u jedinstvenoj koloni.

Transkript postavlja `NOT NULL` i na telefon. Ovde ga ostavljamo opcionim, u skladu sa modelom iz [prvog dela](./02_sqlite_create_table_statement_part_1.md): kontakt može imati email, a nemati telefon. Ako je telefon obavezan u tvojoj aplikaciji, promeni definiciju u `phone TEXT NOT NULL UNIQUE`. Jedinstvenost telefona je takođe poslovno pravilo — ako više kontakata sme deliti broj, ukloni `UNIQUE`.

## 2. Tabela `groups`

Zatim pravimo tabelu grupa:

```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
```

Grupa ima svoj primarni ključ i obavezan, jedinstven naziv. `UNIQUE` sprečava dve grupe sa istim nazivom u okviru pravila poređenja SQLite-a; podrazumevano poređenje teksta razlikuje velika i mala slova.

## 3. Pomoćna tabela `contact_groups`

Na kraju pravimo tabelu koja čuva članstva:

```sql
CREATE TABLE contact_groups (
    contact_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    PRIMARY KEY (contact_id, group_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
        ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id)
        ON DELETE CASCADE
) WITHOUT ROWID;
```

Ova tabela sprovodi model N:M:

- `contact_id` referencira `contacts.id`;
- `group_id` referencira `groups.id`;
- svaki red članstva mora sadržati obe vrednosti;
- složeni `PRIMARY KEY (contact_id, group_id)` ne dopušta da se isti kontakt doda istoj grupi više puta;
- isti kontakt može imati više redova sa različitim grupama, a ista grupa više redova sa različitim kontaktima.

`ON DELETE CASCADE` je eksplicitna odluka ovog primera: ako se izbriše kontakt ili grupa, brišu se njegovi/njeni redovi članstva iz `contact_groups`. Ne brišu se druge grupe ili kontakti. Ovo nije obavezna posledica svakog stranog ključa — izaberi ponašanje pri brisanju prema pravilima aplikacije.

`WITHOUT ROWID` koristi složeni primarni ključ kao osnovni ključ tabele umesto posebnog `rowid`-a. To je razumno za ovu pomoćnu tabelu, ali nije pravilo koje treba automatski dodati svim SQLite tabelama.

### Pokreni ceo DDL redom

U praznoj bazi možeš izvršiti ovaj ceo skript:

```sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;

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
```

Kreiranje treba da se izvrši bez greške. Sve definicije kolona i ograničenja razdvojene su zarezima; nema zareza iza poslednjeg ograničenja pre zatvarajuće zagrade.

## Proveri kreirane tabele i strane ključeve

U SQLite CLI-ju:

```text
.tables
.schema contacts
.schema groups
.schema contact_groups
```

Za pregled kolona i FK-ova koriste se SQL `PRAGMA` naredbe:

```sql
PRAGMA table_info(contacts);
PRAGMA table_info(groups);
PRAGMA table_info(contact_groups);
PRAGMA foreign_key_list(contact_groups);
```

`PRAGMA foreign_key_list(contact_groups)` prikazuje dve veze iz pomoćne tabele: jednu ka `contacts`, drugu ka `groups`. Naredba `PRAGMA foreign_keys;` proverava da li je uključena provera na trenutnoj konekciji; to nije isto što i lista FK definicija u šemi.

## Probaj validno članstvo i ograničenja

Ubaci kontakt, grupu i njihovu vezu:

```sql
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES ('Ana', 'Anić', 'ana@example.test', '+381601234567');

INSERT INTO groups (name)
VALUES ('Porodica');

INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1);

SELECT * FROM contact_groups;
```

U novoj bazi, sa ovim redosledom unosa, očekivano je jedno članstvo `(1, 1)`. Probaj i sledeće naredbe **pojedinačno**; svaka treba da bude odbijena:

```sql
-- Email mora biti jedinstven.
INSERT INTO contacts (first_name, last_name, email)
VALUES ('Druga', 'Osoba', 'ana@example.test');

-- Isti kontakt ne može dva puta biti dodat u istu grupu.
INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1);

-- Kontakt sa id=999 ne postoji.
INSERT INTO contact_groups (contact_id, group_id)
VALUES (999, 1);

-- Telefonski broj ne može biti ponovljen kada je naveden.
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES ('Treća', 'Osoba', 'treca@example.test', '+381601234567');
```

Prvi i poslednji pokušaj krše `UNIQUE`, drugi krši složeni `PRIMARY KEY`, a treći krši strani ključ. Ako bi tabela `contact_groups` bila samo deklarisana sa FK kolonama, ali `PRAGMA foreign_keys` nije uključen, SQLite ne bi sproveo proveru tih FK vrednosti na toj konekciji.

Možeš da proveriš i odabrano ponašanje brisanja. U memorijskoj bazi sa prethodnim validnim podacima:

```sql
BEGIN;
DELETE FROM contacts WHERE id = 1;
SELECT COUNT(*) FROM contact_groups;
SELECT COUNT(*) FROM groups;
ROLLBACK;
```

U toku transakcije očekuješ `0` redova članstva i `1` grupu. `ROLLBACK` vraća probno brisanje i njegove kaskadne promene, tako da možeš nastaviti vežbu sa početnim podacima.

## Ista šema u SQLAlchemy 2

SQLAlchemy modeli ispod opisuju iste tri tabele. Kod se oslanja na SQLAlchemy 2 typed Declarative stil:

```python
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Table,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


contact_groups = Table(
    "contact_groups",
    Base.metadata,
    Column(
        "contact_id",
        ForeignKey("contacts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "group_id",
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sqlite_with_rowid=False,
)


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True)

    groups: Mapped[list["Group"]] = relationship(
        secondary=contact_groups,
        back_populates="contacts",
    )


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    contacts: Mapped[list[Contact]] = relationship(
        secondary=contact_groups,
        back_populates="groups",
    )


engine = create_engine("sqlite+pysqlite:///:memory:")


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    previous_autocommit = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    try:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()
    finally:
        dbapi_connection.autocommit = previous_autocommit


Base.metadata.create_all(engine)
```

U SQLAlchemy mapiranju:

- `mapped_column(primary_key=True)` pravi pojedinačne primarne ključeve `contacts.id` i `groups.id`.
- `contact_groups` je Core `Table`; dve kolone obeležene sa `primary_key=True` formiraju složeni PK.
- `ForeignKey("contacts.id")` i `ForeignKey("groups.id")` definišu stvarne FK veze; `relationship(..., secondary=contact_groups)` omogućava ORM navigaciju N:M.
- `unique=True` i `nullable=False` odgovaraju pravilima u DDL-u. `phone` je namerno nullable, kao u SQL primeru.
- `sqlite_with_rowid=False` je SQLite specifičan Table parametar koji generiše `WITHOUT ROWID`.
- `PRAGMA foreign_keys=ON` se izvršava za svaku novu DBAPI konekciju ovog engine-a. Potreban je zbog SQLite FK ponašanja, a nije zamena za deklarisanje `ForeignKey`.

Iako su u SQLAlchemy modelu tipovi navedeni kao `String(254)` i `String(80)`, SQLite obična tabela sama ne nameće taj maksimalan broj znakova. Ako je ograničenje dužine neophodno, dodaj odgovarajući `CheckConstraint`, kao što je objašnjeno u [lekciji o ograničenjima](./01_sqlite_constraints.md).

## Šta je transkript pojednostavio — važne ispravke

1. **`TEXT` je deklaracija tipa, a ne SQLite storage class svake vrednosti.** SQLite kolona ima afinitet, dok upisana vrednost ima jednu od storage klasa; za obične tabele tip nije stroga garancija.
2. **`INTEGER PRIMARY KEY` ima posebno SQLite ponašanje.** U rowid tabeli postaje alias za `rowid`, ali to ne važi za proizvoljnu deklaraciju `INT PRIMARY KEY` ili za složeni ključ.
3. **Dva FK-a u pomoćnoj tabeli realizuju vezu N:M.** Složeni PK osigurava da se isti par ne ponovi; sam dijagram ne sprovodi integritet.
4. **Foreign key deklaracija i njena provera nisu isto.** SQLite proverava FK vrednosti samo kada je `PRAGMA foreign_keys` uključen na toj konekciji.
5. **Obaveznost telefona je izbor modela.** Izvorni video ga čini obaveznim; u ovoj verziji je opcionalan i jedinstven, u skladu sa modelom iz prvog dela. Promeni `NULL` pravilo prema stvarnom zahtevu aplikacije.

## Vežbe

1. Pokreni tri `CREATE TABLE` naredbe u novoj `:memory:` bazi. Proveri sve tabele pomoću `.tables` i `.schema`.
2. Proveri `PRAGMA foreign_keys;` i `PRAGMA foreign_key_list(contact_groups);`. Objasni zašto su to različite provere.
3. Ubaci drugi kontakt i drugu grupu. Napravi tri članstva i proveri da li isti kontakt i grupa mogu da se ponove u različitim parovima.
4. Pokušaj da uneseš ponovljeni email, ponovljeni par članstva i nepostojeći `contact_id`. Zabeleži koje ograničenje odbija svaki pokušaj.
5. U jednoj transakciji izbriši kontakt i proveri efekat `ON DELETE CASCADE`; zatim uradi `ROLLBACK`.
6. Napravi istu strukturu SQLAlchemy modelima i uporedi generisanu šemu sa ručno napisanim DDL-om.

## Provera razumevanja

1. Zašto se `contacts` i `groups` prave pre `contact_groups`?
2. Šta sprečava ponovljeni par u `contact_groups`?
3. Zašto SQLite mora imati uključen `PRAGMA foreign_keys` na svakoj konekciji?
4. Šta se briše kada se izbriše kontakt sa `ON DELETE CASCADE` u ovom modelu?
5. Zašto je telefon deklarisan kao `TEXT`, a ne kao `INTEGER`?
6. Koja je razlika između `relationship()` i `ForeignKey` u SQLAlchemy-ju?
7. Da li `String(80)` sam po sebi ograničava dužinu u SQLite-u?

## Izvori za dalje čitanje

- [SQLite: CREATE TABLE](https://www.sqlite.org/lang_createtable.html)
- [SQLite: Foreign Key Support](https://www.sqlite.org/foreignkeys.html)
- [SQLite: WITHOUT ROWID tables](https://www.sqlite.org/withoutrowid.html)
- [SQLAlchemy 2.0: SQLite dialect — Foreign Key Support](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support)
- [SQLAlchemy 2.0: Basic Relationship Patterns — Many To Many](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many)
