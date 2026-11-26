# Dan 07 — Kreiranje tabela, izmena podataka i brisanje

> **Važna napomena:** naziv „Dan 07“ je oznaka dokumenta, a ne očekivanje da se sav materijal uradi za jedan dan. Ovaj vodič pokriva vežbe iz cele oblasti 03, odnosno svih sedam lekcija. Slobodno ga rasporedi na više dana i sesija; nastavi kada razumeš trenutnu temu, ne prema kalendaru.

## Cilj oblasti

U ovoj oblasti učiš kako se definiše struktura relacionih podataka, kako ograničenja štite integritet i kako se redovi dodaju, menjaju i brišu. Na kraju razlikuješ brisanje reda od uklanjanja cele tabele.

Ovaj vodič prati:

- [lekcije oblasti 03](../03_creating_database_tables_updating_data_deleting_records/)
- [SQL vežbe oblasti 03](../playground/sql/03_creating_database_tables_updating_data_deleting_records/)
- [SQLite CLI vežbu za pregled šeme i `DROP TABLE`](../playground/cli/04_sqlite_schema_and_drop_table.txt)
- [plan učenja](../plan_ucenja/sta_je_vazno.md)
- način rada iz [dana 06](./dan_06_retriving_data_and_manipulating_data_vezbe.md)

Svaki `.sql` fajl je samostalan i pravi svoje tabele. Prvo pokušaj zadatke bez gledanja rešenja, pa pokreni odgovarajući fajl i uporedi rezultate.

## 1. Bezbedan način rada

### Koristi privremenu bazu

Lekcije iz ove oblasti sadrže `CREATE`, `INSERT`, `UPDATE`, `DELETE` i `DROP TABLE`. To su naredbe koje menjaju šemu ili podatke. Ne izvršavaj ih nad Chinook bazom, bazom FastAPI aplikacije ili bilo kojim podacima koje želiš da sačuvaš.

Najbezbedniji način za SQLite CLI je nova memorijska baza za svaki `.sql` fajl. Iz root-a repozitorijuma:

```bash
sqlite3 :memory:
```

Kada se pojavi SQLite prompt, učitaj, na primer, skript za ograničenja:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/01_sqlite_constraints.sql
```

Za sledeću lekciju zatvori tu konekciju sa `.quit`, pa pokreni novu `sqlite3 :memory:` konekciju i učitaj sledeći fajl. Tabele u skriptama imaju iste nazive, zato ih nemoj sve učitavati u istu već popunjenu bazu.

U SQLTools-u izaberi posebnu, praznu `sandbox.db` bazu i proveri punu putanju konekcije pre izvršavanja. Za ponovno pokretanje fajla koristi novu/praznu probnu bazu. Nemoj računati da se promena konekcije u jednom VS Code panelu automatski primenjuje na drugi.

Skripti su organizovani tako da očekivane nevažeće upite ostavljaju komentarisane. Ako želiš da vidiš neku grešku ograničenja, prvo učitaj ispravnu pripremu i podatke, pa odkomentariši i pokreni samo taj nevažeći upit. Posle greške proveri stanje pre nastavka; ako je transakcija ostala aktivna, uradi `ROLLBACK`.

### SQLite CLI i SQLTools

Fajl [`04_sqlite_schema_and_drop_table.txt`](../playground/cli/04_sqlite_schema_and_drop_table.txt) koristi SQLite CLI meta-komande `.tables` i `.schema` uz SQL `PRAGMA` naredbe. Izvršava se u SQLite CLI-ju, ne kao običan SQL upit u SQLTools editoru. Fajl sam učitava pripremni SQL za `contacts`, `groups` i `contact_groups`, pa zatim proverava tabelu tokom transakcionog `DROP TABLE` i nakon `ROLLBACK`-a.

`PRAGMA foreign_keys = ON` je podešavanje pojedinačne konekcije. Uključi ga pre rada sa stranim ključevima i pre početka transakcije; vrednost iz CLI-ja ne podešava automatski SQLTools ili aplikacionu konekciju.

### Proverene vrednosti u vežbama

Ovo su rezultati iz samostalnih, svežih memorijskih baza koje se prave u `.sql` fajlovima:

| Provera                                                   | Očekivani rezultat |
| --------------------------------------------------------- | -----------------: |
| `items.stock` kada se kolona izostavi pri unosu           |                `0` |
| Članstva nakon unosa za kontakte 1 i 2                    |                  3 |
| Kontakti bez telefona u primeru iz lekcije 03             |                  2 |
| `changes()` za `UPDATE ... WHERE id = 2`                  |                  1 |
| `changes()` za `UPDATE ... WHERE id = 999`                |                  0 |
| Članstva tokom brisanja grupe 2 sa uključenim FK-ovima    |                  2 |
| Članstva posle `DROP TABLE groups` sa uključenim FK-ovima |                  0 |
| Članstva posle `ROLLBACK`-a                               |                  3 |

Ove brojke važe za početne podatke iz vežbi, ne za bilo koju drugu bazu.

---

## 2. Rešenja i objašnjenja vežbi

## Lekcija 01 — SQLite ograničenja (`constraints`)

Radni fajl: [01_sqlite_constraints.sql](../playground/sql/03_creating_database_tables_updating_data_deleting_records/01_sqlite_constraints.sql)
Teorija: [01_sqlite_constraints.md](../03_creating_database_tables_updating_data_deleting_records/01_sqlite_constraints.md)

### Vežbe 1–3 — Definiši `categories` i `items`

Jedno moguće rešenje zadataka iz lekcije:

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    CONSTRAINT uq_categories_name UNIQUE (name),
    CONSTRAINT ck_categories_name_nonblank
        CHECK (length(trim(name)) > 0)
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    price NUMERIC NOT NULL
        CHECK (
            typeof(price) IN ('integer', 'real')
            AND price >= 0
        ),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    CONSTRAINT fk_items_category
        FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

- `id INTEGER PRIMARY KEY` identifikuje svaki red.
- `name TEXT NOT NULL UNIQUE` bi obezbedio obavezno i jedinstveno ime, a `CHECK` dodatno odbija prazan tekst ili tekst sastavljen samo od običnih razmaka.
- `category_id` je obavezan FK ka postojećoj kategoriji. Provera FK vrednosti radi samo dok je `PRAGMA foreign_keys` uključen za tu konekciju.
- `price >= 0` odbija negativnu cenu.
- `stock INTEGER NOT NULL DEFAULT 0` postavlja nulu samo kada `INSERT` izostavi kolonu.

U radu je `name` jedinstven preko imenovanog ograničenja `uq_categories_name`. Može se napisati i kraće kao `name TEXT NOT NULL UNIQUE`.

### Vežba 4 — Validan unos i podrazumevana vrednost

```sql
INSERT INTO categories (name)
VALUES ('Books');

INSERT INTO items (category_id, name, price)
VALUES (1, 'SQLite workbook', 12.50);

SELECT id, category_id, name, price, stock
FROM items;
```

U radnoj skripti `SQLite workbook` dobija `stock = 0`, jer je kolona izostavljena i ima `DEFAULT 0`. Drugi validan red pokazuje da možeš proslediti i konkretnu vrednost:

```sql
INSERT INTO items (category_id, name, price, stock)
VALUES (1, 'SQL notebook', 4.25, 7);
```

`DEFAULT` se ne koristi kada upit izričito pošalje `NULL`. Ovde bi `stock = NULL` bio odbijen zbog `NOT NULL`.

### Vežbe 4–5 — Koje unose odbijaju ograničenja?

Pokreni sledeće primere pojedinačno u probnoj bazi:

```sql
-- Ne postoji kategorija sa id=999.
INSERT INTO items (category_id, name, price)
VALUES (999, 'Unknown category', 1.00);

-- Cena ne sme biti negativna.
INSERT INTO items (category_id, name, price)
VALUES (1, 'Negative price', -1.00);

-- Naziv kategorije već postoji.
INSERT INTO categories (name)
VALUES ('Books');
```

Prvi upit krši `FOREIGN KEY`, drugi `CHECK`, a treći `UNIQUE`. Ako `PRAGMA foreign_keys` vrati `0`, SQLite na toj konekciji neće sprovesti FK proveru; uključi je pre ponovnog testa.

### Ivični slučajevi za ograničenja

`NOT NULL` ne odbija `''` niti tekst sa razmacima. Zato `categories.name` ima i `CHECK (length(trim(name)) > 0)`. SQLite `trim()` bez dodatnih znakova uklanja obične razmake na krajevima; za druge Unicode razmake može biti potrebna posebna normalizacija.

`CHECK` izrazi proveravaju rezultat uslova, ne garantuju tip kolone. U običnoj, fleksibilno tipizovanoj SQLite tabeli, prost `CHECK (price >= 0)` može prihvatiti nenumerički tekst jer SQLite poredi storage klase. Zato ovaj primer dodatno proverava `typeof(price)`. Provera `typeof()` je SQLite specifična; proveri ograničenje i u ciljnoj bazi kada pređeš na MySQL ili PostgreSQL.

`UNIQUE(phone)` dozvoljava više `NULL` vrednosti. U skripti za `CREATE TABLE` unose se dva kontakta bez telefona, a oba su prihvaćena. Ako polje mora biti i popunjeno i jedinstveno, potrebna su oba pravila: `NOT NULL` i `UNIQUE`.

`CHECK` koji daje `NULL` ne smatra se prekršenim u SQLite-u. Zato `CHECK (age >= 18)` sam po sebi ne zabranjuje `NULL`; obaveznost se dodaje sa `NOT NULL`.

### Vežba 6 — Mapiranje u SQLAlchemy 2

SQLAlchemy modeli opisuju iste vrste pravila: `primary_key=True`, `nullable=False`, `unique=True`, `ForeignKey`, `CheckConstraint` i `server_default`. `relationship()` olakšava ORM-u navigaciju između objekata, ali nije zamena za FK ograničenje u samoj bazi.

Važno je razlikovati:

- `default=0` je vrednost koju SQLAlchemy može primeniti pri ORM unosu;
- `server_default=text("0")` se upisuje u DDL, pa podrazumevanu vrednost može primeniti sama baza i na unos iz drugog klijenta.

Ako je pravilo potrebno za sve upise, definiši ga na nivou baze. Sama Pydantic ili Python validacija ne štiti upise koji dolaze iz SQLite CLI-ja, SQLTools-a, migracije ili druge aplikacije. SQLAlchemy i SQLite grešku ograničenja obično prijavljuju kao `IntegrityError`; obradi je kao očekivan poslovni konflikt i ne izlaži korisniku internu poruku baze.

### Kratki odgovori na pitanja iz lekcije

1. `NOT NULL` odbija odsutnu vrednost; `CHECK (length(trim(name)) > 0)` odbija prazan ili razmacima popunjen tekst.
2. `UNIQUE` sam dozvoljava više `NULL` vrednosti u SQLite-u. Za obavezan email koristi `NOT NULL UNIQUE`.
3. FK u tabeli deteta ne mora biti jedinstven; više zadataka može pripadati istom korisniku.
4. `DEFAULT` se koristi kada se kolona izostavi. Eksplicitni `NULL` nije izostavljanje i može biti odbijen pravilom `NOT NULL`.
5. `ForeignKey` sprovodi referencu u šemi baze; `relationship()` definiše ORM navigaciju između objekata.
6. Promena modela ne migrira postojeću tabelu. Za verzionisane promene šeme koristi migracije, npr. Alembic.
7. SQLite FK provera mora biti uključena za svaku konekciju pomoću `PRAGMA foreign_keys = ON`.

## Lekcija 02 — `CREATE TABLE` i planiranje modela (1. deo)

Radni fajl: [02_sqlite_create_table_statement_part_1.sql](../playground/sql/03_creating_database_tables_updating_data_deleting_records/02_sqlite_create_table_statement_part_1.sql)
Teorija: [02_sqlite_create_table_statement_part_1.md](../03_creating_database_tables_updating_data_deleting_records/02_sqlite_create_table_statement_part_1.md)

### Vežbe 1 i 4 — Model kontakata i grupa

Model ima tri tabele:

- `contacts` čuva kontakte, jedan red po osobi;
- `groups` čuva grupe, jedan red po grupi;
- `contact_groups` čuva članstva, jedan red po paru kontakt–grupa.

Jedan kontakt može biti povezan sa više grupa, a jedna grupa sa više kontakata. To je veza N:M i sprovodi se pomoćnom tabelom:

```text
contacts (id PK) 1 ───< contact_groups (contact_id PK/FK, group_id PK/FK) >─── 1 groups (id PK)
```

Složeni PK `(contact_id, group_id)` sprečava ponavljanje istog članstva. Ne sprečava da se isti kontakt ili grupa pojave u nekom drugom paru. Sam model dozvoljava kontaktu da nema nijednu grupu; FK-ovi zahtevaju da svaki _postojeći red članstva_ upućuje na postojeći kontakt i grupu, ali ne zahtevaju članstvo za svaki kontakt.

### Vežbe 2–3 — `reading_notes` i `IF NOT EXISTS`

```sql
CREATE TABLE reading_notes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reading_notes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

PRAGMA table_info(reading_notes);
```

Druga naredba ne prijavljuje grešku, ali ni ne menja postojeću tabelu. `created_at` ostaje u šemi. `IF NOT EXISTS` sprečava grešku zbog postojećeg objekta; nije migracija, provera kompatibilnosti niti popravka tabele.

U SQLite CLI-ju možeš koristiti `.schema reading_notes` za DDL. `.schema` je meta-komanda CLI alata, a `PRAGMA table_info(reading_notes)` je SQL-pozivani SQLite pragma.

### Vežba 5 — `rowid` i `WITHOUT ROWID`

```sql
CREATE TABLE rowid_demo (
    id INTEGER PRIMARY KEY,
    label TEXT NOT NULL
);

INSERT INTO rowid_demo (label)
VALUES ('ordinary rowid table');

SELECT id, rowid, label
FROM rowid_demo;
```

U običnoj rowid tabeli, kada je PK tačno `INTEGER PRIMARY KEY`, `id` je alias za `rowid`; u prikazu će vrednosti biti jednake. `rowid` nije obična kolona i ne pojavljuje se u `SELECT *`.

Pomoćnu tabelu je moguće definisati ovako:

```sql
CREATE TABLE contact_groups_demo (
    contact_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    PRIMARY KEY (contact_id, group_id)
) WITHOUT ROWID;
```

`WITHOUT ROWID` tabela nema skriveni `rowid` i mora imati PK. Ova SQLite opcija može biti primerena za prirodno složeni ključ, ali je ne treba automatski dodavati svakoj tabeli. Ne pokušavaj `SELECT rowid FROM contact_groups_demo`; takvo ime tamo ne postoji kao rowid.

### Vežba 6 — SQLAlchemy model

SQLAlchemy 2 Declarative modeli i `Table` objekat mogu opisati `contacts`, `groups` i asocijativnu tabelu `contact_groups`. `ForeignKey` definiše referencijalni integritet; `relationship(secondary=contact_groups)` daje ORM-u način da navigira N:M vezom. Uporedi stvarni DDL kroz `.schema` ili `sqlite_schema`, ne samo Python definicije.

### Kratki odgovori na pitanja iz lekcije

1. `CREATE TABLE` navodi ime tabele, kolone, njihove tipove i ograničenja; lista je unutar zagrada.
2. Ako objekat istog imena već postoji, `IF NOT EXISTS` preskače kreiranje bez poređenja postojeće i tražene šeme.
3. `main` je glavna baza konekcije, `temp` privremena baza konekcije, a alias poput `archive` može predstavljati bazu dodatu komandom `ATTACH`.
4. `rowid` je SQLite mehanizam obične tabele; nije obična definisana kolona i ne prikazuje se sa `SELECT *`.
5. `id INTEGER PRIMARY KEY` u običnoj rowid tabeli postaje alias za rowid. `WITHOUT ROWID` koristi PK kao osnovu i nema skriveni rowid.
6. Pomoćna tabela pretvara vezu N:M u dva odnosa 1:N.
7. Ne. FK-ovi proveravaju postojeće redove članstva, ali ne zahtevaju da svaki kontakt ima članstvo.
8. `ForeignKey` je pravilo šeme baze; `relationship()` je ORM veza između Python objekata.

## Lekcija 03 — `CREATE TABLE` (2. deo)

Radni fajl: [03_sqlite_create_table_statement_part_2.sql](../playground/sql/03_creating_database_tables_updating_data_deleting_records/03_sqlite_create_table_statement_part_2.sql)
Teorija: [03_sqlite_create_table_statement_part_2.md](../03_creating_database_tables_updating_data_deleting_records/03_sqlite_create_table_statement_part_2.md)

### Vežbe 1–2 — Kreiraj tabele i proveri FK-ove

Najpre uključi proveru stranih ključeva, a zatim napravi roditeljske tabele pre tabele članstva:

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

`PRAGMA foreign_keys;` prikazuje je li provera aktivna za ovu konekciju: `1` znači uključena. `PRAGMA foreign_key_list(contact_groups);` prikazuje FK definicije koje su upisane u šemu. To su različite provere: jedna je podešavanje konekcije, druga opisuje veze tabele.

`PRAGMA table_info(...)` prikazuje kolone i PK informacije. U CLI-ju `.tables` prikazuje tabele, a `.schema contacts` / `.schema contact_groups` DDL za izabrane tabele.

### Vežba 3 — Napravi više članstava

U skripti se unose tri kontakta, dve grupe i tri veze:

```sql
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES
    ('Ana', 'Anic', 'ana@example.test', '+381601234567'),
    ('Milan', 'Milic', 'milan@example.test', NULL),
    ('Toni', 'Ivic', 'toni@example.test', NULL);

INSERT INTO groups (name)
VALUES ('Family'), ('Work');

INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1), (1, 2), (2, 1);
```

Članstva su `(1,1)`, `(1,2)` i `(2,1)`. Isti kontakt 1 pripada dvema grupama, a grupa 1 ima dva kontakta. Isti _par_ ne sme se ponoviti zbog složenog PK-a. Dva kontakta sa `phone = NULL` su dozvoljena, iako je `phone` označen sa `UNIQUE`; SQLite tretira `NULL` vrednosti u `UNIQUE` kao različite.

### Vežba 4 — Očekivani nevažeći unosi

Pokreni zasebno u probnoj konekciji:

```sql
-- Email već postoji.
INSERT INTO contacts (first_name, last_name, email)
VALUES ('Other', 'Person', 'ana@example.test');

-- Isti par članstva već postoji.
INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1);

-- Kontakt sa id=999 ne postoji.
INSERT INTO contact_groups (contact_id, group_id)
VALUES (999, 1);
```

Greške odgovaraju redom ograničenjima `UNIQUE`, složenom `PRIMARY KEY` i `FOREIGN KEY`. Treći pokušaj se može pravilno proveriti samo ako je `PRAGMA foreign_keys = ON` na aktivnoj konekciji.

### Vežba 5 — Kaskadno brisanje unutar transakcije

Skripta briše kontakt 1 i odmah proverava rezultat, pa vraća stanje:

```sql
BEGIN;

DELETE FROM contacts
WHERE id = 1;

SELECT COUNT(*) FROM contact_groups;
SELECT COUNT(*) FROM groups;

ROLLBACK;
```

Tokom transakcije ostaje jedno članstvo `(2,1)`, jer se dva članstva kontakta 1 kaskadno brišu. Obe grupe ostaju. `ROLLBACK` vraća kontakt i sva tri početna članstva. Kaskada radi samo kada je FK provera uključena i kada je u definiciji FK-a navedeno `ON DELETE CASCADE`.

### Vežba 6 — Ista struktura u ORM-u

SQLAlchemy `Base.metadata.create_all()` pravi tabele koje ne postoje, ali ne migrira postojeću tabelu kada izmeniš model. U ORM-u testiraj:

- primarne ključeve `contacts.id` i `groups.id`;
- asocijativnu tabelu sa složenim PK-om;
- FK-ove ka roditeljskim tabelama;
- `relationship(..., secondary=contact_groups)`;
- događaj koji uključuje `PRAGMA foreign_keys=ON` pri svakoj novoj DBAPI konekciji.

`String(80)` sam po sebi ne ograničava broj karaktera u običnoj SQLite tabeli. Za ograničenje koje baza sprovodi potreban je, na primer, `CHECK`.

## Lekcija 04 — `INSERT INTO`

Radni fajl: [04_sqlite_INSERT_INTO_table_statement.sql](../playground/sql/03_creating_database_tables_updating_data_deleting_records/04_sqlite_INSERT_INTO_table_statement.sql)
Teorija: [04_sqlite_INSERT_INTO_table_statement.md](../03_creating_database_tables_updating_data_deleting_records/04_sqlite_INSERT_INTO_table_statement.md)

### Vežbe 1–3 — Unesi kontakte, grupe i veze

Jasan oblik unosa navodi kolone i vrednosti u istom redosledu:

```sql
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES ('Johnny', 'Cash', 'johnny.cash@example.test', '+12025550101');
```

Zatim se u jednoj naredbi mogu dodati dva kontakta:

```sql
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES
    ('Jane', 'Doe', 'jane.doe@example.test', '+12025550102'),
    ('Toni', 'Ivic', 'toni@example.test', NULL);
```

Skripta dodaje i Morgan bez kolone `phone`. U ovoj šemi telefon je opcioni i nema drugu podrazumevanu vrednost, pa i izostavljanje i eksplicitni `NULL` daju odsutnu vrednost. To se razlikuje od praznog teksta `''`.

Posle unosa, redosled ID-jeva u novoj bazi je Johnny `1`, Jane `2`, Toni `3`, Morgan `4`. Višeredni unos grupa daje `Cash Flow` ID `1` i `Accounts` ID `2`. Zatim tri članstva:

```sql
INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1), (1, 2), (2, 1);
```

`SELECT` sa `JOIN`-ovima prikazuje tri veze: Johnny–Cash Flow, Johnny–Accounts i Jane–Cash Flow. U postojećoj bazi nemoj nagađati ID-jeve; pronađi ih upitom.

### Vežba 4 — Proveri generisani ID

SQLite 3.35.0+ podržava `RETURNING`:

```sql
INSERT INTO contacts (first_name, last_name, email)
VALUES ('Riley', 'Park', 'riley.park@example.test')
RETURNING id, email;
```

U samostalnom skriptu Riley dobija `id = 5`. `last_insert_rowid()` na istoj konekciji zatim vraća `5`. Za SQLite verziju stariju od 3.35.0 koristi se `last_insert_rowid()` odmah posle uspešnog inserta; SQLAlchemy ORM obično popuni atribut PK-a posle `flush()`-a.

### Ivični slučajevi pri unosu

- Broj vrednosti mora odgovarati broju navedenih kolona.
- Kada navedeš kolone, redosled vrednosti prati tu listu, ne nužno redosled definicije tabele.
- Izostavljena kolona dobija `DEFAULT`, ako postoji; u suprotnom `NULL`. `NOT NULL` može odbiti taj rezultat.
- `NOT NULL` ne odbija `''`; za neprazan tekst potreban je i `CHECK`.
- `UNIQUE` ne znači `NOT NULL`; može dozvoliti više `NULL` vrednosti.
- Ako vrednost prekrši ograničenje, podrazumevano ponašanje `ABORT` poništava izmene te `INSERT` naredbe. To samo po sebi ne poništava prethodne nezavisne SQL naredbe u otvorenoj transakciji.

Nevažeći primeri iz radnog fajla — pokreći jedan po jedan:

```sql
INSERT INTO contacts (first_name, last_name, email)
VALUES ('Duplicate', 'Email', 'johnny.cash@example.test');

INSERT INTO contact_groups (contact_id, group_id)
VALUES (1, 1);

INSERT INTO contact_groups (contact_id, group_id)
VALUES (999, 1);
```

Oni krše jedinstvenost email-a, jedinstvenost para članstva i FK redom. Prvi nevažeći email ne znači da je aplikacija proverila sve ostale podatke — proveravaj bazu direktno.

### SQLAlchemy 2 i bezbedno vezivanje vrednosti

ORM upis koristi `session.add()` / `session.add_all()` i transakciju. Ako se preko `relationship()` dodaju objekti u `johnny.groups`, ORM upisuje i redove u asocijativnu tabelu. Nemoj zatim ručno unositi iste parove još jednom.

Za SQL vrednosti koje stižu iz aplikacije koristi parametarsko vezivanje (`text("... :name")` uz poseban parametarski rečnik), ne f-string ili konkatenaciju SQL stringa. Parametri su za _vrednosti_, ne za dinamička imena tabela ili kolona.

### Kratki odgovori na pitanja iz lekcije

1. Eksplicitna lista kolona čini unos razumljivijim i otpornijim na promenu šeme.
2. U ovom primeru `id INTEGER PRIMARY KEY` može dobiti vrednost od SQLite-a; tekstualni ili složeni PK ne dobija je automatski na isti način.
3. Izostavljena kolona pokreće `DEFAULT` ili postaje `NULL`; eksplicitni `NULL` nije isto što i `''`.
4. Neusklađen broj kolona i vrednosti dovodi do SQL greške.
5. `flush()` šalje promene bazi unutar trenutne transakcije, ali nije isto što i `commit()`.
6. Parametri odvajaju SQL strukturu od aplikacijskih podataka i izbegavaju nesigurno sastavljanje upita.
7. ORM veza `relationship(secondary=...)` opisuje navigaciju; FK-ovi i PK-ovi u bazi čuvaju integritet redova veze.

## Lekcija 05 — `UPDATE`

Radni fajl: [05_sqlite_UPDATE_statement.sql](../playground/sql/03_creating_database_tables_updating_data_deleting_records/05_sqlite_UPDATE_statement.sql)
Teorija: [05_sqlite_UPDATE_statement.md](../03_creating_database_tables_updating_data_deleting_records/05_sqlite_UPDATE_statement.md)

### Vežbe 1–2 — Proveri red i promeni prezime

Pre promene:

```sql
SELECT id, first_name, last_name, email
FROM contacts
WHERE id = 2;
```

U svežoj probnoj tabeli red `id = 2` pripada Jane Doe. Ograniči promenu primarnim ključem:

```sql
UPDATE contacts
SET last_name = 'Johnson'
WHERE id = 2;

SELECT changes();
```

`changes()` vraća `1`, a ponovni `SELECT` prikazuje Jane Johnson. `UPDATE` menja postojeći red, ne dodaje novi.

### Vežba 5 — Transakcija i `ROLLBACK`

U radnom fajlu promena se prvo izvršava između `BEGIN` i `ROLLBACK`. Tokom transakcije prezime je Johnson; nakon `ROLLBACK`-a vraća se na Doe. Ako se rezultat potvrđuje sa `COMMIT`, promena postaje trajna u datoj bazi; ne koristi oba završetka za istu transakciju.

### Vežbe 3–4 — Više kolona, nula redova i isti sadržaj

```sql
UPDATE contacts
SET first_name = 'Jane',
    last_name = 'Johnson'
WHERE id = 2;
```

Jedan `UPDATE` može menjati više kolona; dodele se razdvajaju zarezima. Izmena nad nepostojećim ID-jem:

```sql
UPDATE contacts
SET last_name = 'Nobody'
WHERE id = 999;

SELECT changes();
```

vraća `0`, jer nijedan red ne odgovara uslovu. To nije SQL greška; aplikacija treba da odluči da li je nula pogođenih redova očekivana.

Skripta zatim postavi prezime na `Doe` i ponovi isti `UPDATE`. U oba slučaja `changes()` vraća `1` u proveravanoj SQLite verziji: funkcija broji redove pogođene poslednjim DML-om i nije pouzdan dokaz da se sadržaj zaista promenio.

### Ivični slučajevi za `UPDATE`

- Bez `WHERE` uslova menjaš sve redove tabele; SQLite ne traži potvrdu.
- `WHERE` može odgovarati nijednom, jednom ili mnogim redovima. Za jedan red koristi PK ili drugo jedinstveno pravilo.
- `UPDATE` podleže istim `UNIQUE`, `NOT NULL`, `CHECK` i FK ograničenjima kao `INSERT`.
- Ako izmena prekrši `UNIQUE`, SQLite prijavljuje grešku. Podrazumevano `ABORT` poništava trenutnu naredbu, ali ne nužno celu eksplicitnu transakciju; proveri stanje i uradi `ROLLBACK` pre nastavka.
- Uvek prvo izvrši `SELECT` sa istim `WHERE` uslovom i proveri ciljane redove.

Primer koji treba da bude odbijen jer email već pripada Johnny-ju:

```sql
UPDATE contacts
SET email = 'johnny.cash@example.test'
WHERE id = 2;
```

Nevažeći primer ostaje komentar u SQL fajlu kako normalno pokretanje vežbe ne bi bilo prekinuto greškom.

### SQLAlchemy 2

Za ORM promenu možeš pronaći Jane sa `session.get(Contact, 2)`, proveriti da nije `None`, pa promeniti `jane.last_name`. Transakcioni blok `with Session(engine) as session, session.begin():` potvrđuje promenu pri uspehu i radi rollback pri izuzetku. `flush()` šalje SQL bazi; uspešan izlazak iz transakcionog bloka obavlja commit.

### Kratki odgovori na pitanja iz lekcije

1. `SET` definiše nove vrednosti; `WHERE` bira redove kojima se dodeljuju.
2. Bez `WHERE`, naredba menja sve redove.
3. PK je jedinstven, dok isto prezime može pripadati više kontakata.
4. `changes() = 0` znači da poslednja naredba nije pogodila nijedan red.
5. Konflikt sa `UNIQUE` izaziva grešku; ne zanemaruj je niti je maskiraj.
6. `flush()` šalje SQL, `commit()` potvrđuje transakciju.
7. Koristi `COMMIT` kada su promene proverene i nameravane; `ROLLBACK` kada rezultat nije ispravan ili se desi greška.

## Lekcija 06 — `DELETE`

Radni fajl: [06_sqlite_DELETE_statement.sql](../playground/sql/03_creating_database_tables_updating_data_deleting_records/06_sqlite_DELETE_statement.sql)
Teorija: [06_sqlite_DELETE_statement.md](../03_creating_database_tables_updating_data_deleting_records/06_sqlite_DELETE_statement.md)

### Vežbe 1–2 — Obriši samo članstvo

Početni podaci imaju dve grupe i tri članstva: `(1,1)`, `(1,2)` i `(2,1)`. Ako želiš da ukloniš samo Johnny-jevo članstvo u grupi Accounts:

```sql
DELETE FROM contact_groups
WHERE contact_id = 1
  AND group_id = 2;
```

`changes()` vrati `1`. Kontakt Johnny i grupa Accounts i dalje postoje; uklonjen je samo jedan red u pomoćnoj tabeli. Precizan uslov koristi obe komponente složenog PK-a.

### Vežba 3 — Obriši grupu i proveri kaskadu

Skripta prvo vrati članstvo, a zatim u transakciji obriše `groups.id = 2`. Uz `PRAGMA foreign_keys = ON` i `ON DELETE CASCADE`, brišu se direktno izabrana grupa i njen red članstva. Tokom transakcije ostaju jedna grupa i dva članstva. `ROLLBACK` vraća grupu i sva tri početna članstva.

Kaskada zavisi od FK definicije i podešavanja konekcije. Ako je FK provera isključena, može ostati članstvo koje pokazuje na nepostojeću grupu.

### Vežbe 4–5 — Nema pogodaka i brojanje brisanja

```sql
DELETE FROM groups
WHERE id = 999;

SELECT changes();
```

Rezultat je `0`; naredba može da se izvrši bez SQL greške iako nije obrisala red.

`changes()` broji direktno obrisani red `groups`, ne dodatne redove koje su uklonile FK kaskade. Zato `changes() = 1` ne znači da je ukupno izmenjen samo jedan red baze.

### Vežba 7 — Zašto je opasan `DELETE` bez `WHERE`?

```sql
DELETE FROM groups;
```

Ovo briše sve redove iz `groups`, ali ne i definiciju tabele. Ako postoje FK veze, zavisni redovi zavise od aktivnog FK podešavanja i `ON DELETE` pravila. SQLite ne pita za potvrdu. Zato se nevažeći/destruktivni primeri drže komentarisani i pokreću samo u namerno napravljenoj probnoj bazi.

### SQLAlchemy 2

`session.delete(group)` briše ORM objekat/red. U ovom modelu ORM veze mogu ukloniti redove članstva; FK `ON DELETE CASCADE` dodatno štiti direktne SQL naredbe kada su FK provere uključene. Uklanjanje samo veze radi se iz ORM kolekcije, npr. `accounts.contacts.remove(johnny)`, a ne brisanjem samog kontakta ili grupe.

### Kratki odgovori na pitanja iz lekcije

1. `DELETE ... WHERE ...` briše izabrane redove; `DELETE FROM groups` bez uslova briše sve redove iz tabele.
2. `DELETE` ne uklanja tabelu, njenu šemu ili indekse.
3. U ovom modelu brisanje grupe kaskadno uklanja njena članstva, ali ne briše kontakte.
4. FK provera je podešavanje svake pojedinačne SQLite konekcije.
5. `changes()` broji direktne izmene naredbe, ne FK kaskade.
6. Ukloni jedan red iz `contact_groups` uz uslov na obe FK kolone.
7. `COMMIT` potvrđuje proverene promene; `ROLLBACK` ih poništava dok je transakcija aktivna.
8. `DELETE` uklanja redove; `DROP TABLE` uklanja i tabelu i njen sadržaj.

## Lekcija 07 — `DROP TABLE`

Radni fajl: [07_sqlite_DROP_table_statement.sql](../playground/sql/03_creating_database_tables_updating_data_deleting_records/07_sqlite_DROP_table_statement.sql)
Teorija: [07_sqlite_DROP_table_statement.md](../03_creating_database_tables_updating_data_deleting_records/07_sqlite_DROP_table_statement.md)

### Vežba 1 — Proveri šta postoji pre brisanja

Početno stanje sadrži tabele `contacts`, `groups` i `contact_groups`, dve grupe i tri članstva. SQL skripta proverava i `sqlite_schema`; u SQLite CLI-ju možeš koristiti:

```text
.tables
.schema groups
```

`sqlite_schema` je SQL tabela-sistemskog kataloga koja opisuje objekte baze. `.tables` i `.schema` su meta-komande CLI-ja, ne SQL izrazi.

### Vežba 2 — `DROP TABLE` i `ROLLBACK`

Skripta otvara transakciju, izvršava `DROP TABLE groups` i zatim proverava šemu i članstva:

```sql
BEGIN;
DROP TABLE groups;

SELECT name, type
FROM sqlite_schema
WHERE type = 'table'
ORDER BY name;

SELECT COUNT(*) FROM contact_groups;
ROLLBACK;
```

Dok je tabela obrisana, iz liste ostaju `contacts` i `contact_groups`; uz aktivan FK i `ON DELETE CASCADE`, broj članstava je `0`. `ROLLBACK` vraća tabelu `groups`, njene redove i sva tri članstva.

Ovo pokazuje da SQLite podržava transakciju oko ovog `DROP TABLE` primera. `ROLLBACK` je koristan za kontrolisanu probu, ali nije zamena za rezervnu kopiju i ne štiti od greške nakon potvrđenog `COMMIT`-a.

### Vežba 3 — Šta ostaje posle potvrđenog uklanjanja?

Ako umesto `ROLLBACK`-a potvrdiš `COMMIT`, `groups` više ne postoji, a kaskadno su uklonjena sva članstva koja je referenciraju. `contacts` i `contact_groups` tabele ostaju, ali su redovi `contact_groups` uklonjeni zbog `ON DELETE CASCADE`. U radnoj skripti se promena vraća rollback-om da bi skript mogao bezbedno prikazati početno stanje.

### Vežba 4 — `IF EXISTS`

```sql
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS groups;
```

Druga naredba ne prijavljuje grešku samo zato što je tabela već uklonjena. `IF EXISTS` ne proverava da li je brisanje bezbedno niti sprečava pogrešan naziv; ako tabela tog imena postoji, biće obrisana. Vežba zato radi unutar transakcije i završava se `ROLLBACK`-om.

### Indeksi, okidači i povezane tabele

`DROP TABLE` uklanja definiciju tabele, njene redove, povezane indekse i triggere. Ne briše celu SQLite bazu niti nepovezane tabele. Povezane FK tabele zahtevaju dodatnu pažnju: u ovom primeru kaskada briše redove članstva; druga šema može odbiti brisanje zbog `RESTRICT`/`NO ACTION` pravila.

`DROP TABLE groups` se razlikuje od:

```sql
DELETE FROM groups;
```

`DELETE` ostavlja tabelu i njenu šemu. `DROP TABLE` uklanja oba. SQLAlchemy `Session.delete()` briše ORM red, dok `Group.__table__.drop(engine)` uklanja tabelu iz šeme. `Base.metadata.drop_all(engine)` je šire i može obrisati sve mapirane tabele; koristi se samo nad namerno privremenom/test bazom. U aplikacijama promene šeme se obično vode migracijama.

### Kratki odgovori na pitanja iz lekcije

1. `DELETE` uklanja redove; `DROP TABLE` uklanja definiciju tabele i podatke.
2. Indeksi i triggeri vezani za tabelu uklanjaju se zajedno s njom.
3. `contact_groups` se prazni zbog `ON DELETE CASCADE` na FK-u ka grupi.
4. `IF EXISTS` ignoriše samo nepostojanje tabele; ne potvrđuje da je postojeću tabelu bezbedno obrisati.
5. `Session.delete()` uklanja ORM red; `Table.drop()` emituje DDL i uklanja tabelu.
6. `drop_all()` je prihvatljiv samo u izolovanom testu ili namenski privremenoj bazi.
7. `ROLLBACK` može vratiti šemu i podatke dok transakcija nije potvrđena.

---

## 3. Kratka provera razumevanja

1. **Da li `UNIQUE` automatski znači `NOT NULL`?** Ne. SQLite dozvoljava više `NULL` vrednosti pod jedinstvenim ograničenjem.
2. **Da li `IF NOT EXISTS` popravlja pogrešnu tabelu?** Ne; samo preskače kreiranje ako objekat već postoji.
3. **Da li `PRAGMA foreign_keys = ON` važi za sve alate?** Ne; važi samo za aktivnu konekciju.
4. **Kada se primenjuje `DEFAULT`?** Kada je kolona izostavljena, ne kada se eksplicitno pošalje `NULL`.
5. **Šta radi `WHERE` u `UPDATE` i `DELETE`?** Ograničava ciljane redove; bez njega naredba zahvata sve redove tabele.
6. **Da li `changes()` uključuje kaskadno obrisane redove?** Ne, broji direktne promene poslednje DML naredbe.
7. **Koja je razlika između `DELETE` i `DROP TABLE`?** Prvi briše redove, drugi tabelu i njenu šemu.
8. **Šta garantuje `ROLLBACK`?** Poništava promene tekuće transakcije, ne već potvrđene transakcije.
9. **Da li promena SQLAlchemy modela automatski menja postojeću bazu?** Ne; potrebne su migracije.
10. **Da li je `typeof()` prenosiv SQL?** Ne, to je SQLite funkcija; proveri odgovarajuće tipove i pravila u ciljnom DBMS-u.

## 4. Šta je prioritet prema planu učenja?

Ova oblast je važna zato što direktno uvodi integritet podataka i osnovni CRUD rad:

- **Temeljno nauči prenosive principe:** primarni i strani ključevi, `NOT NULL`, `UNIQUE`, `CHECK`, veze 1:N i N:M, eksplicitna lista kolona pri unosu, pažljiv `WHERE` i transakcije.
- **Razumi posledice naredbi:** `INSERT` dodaje, `UPDATE` menja, `DELETE` uklanja redove, a `DROP TABLE` uklanja strukturu.
- **Vežbaj transakcije i greške:** proveri stanje, izvrši promenu, proveri rezultat, pa odluči da li treba `COMMIT` ili `ROLLBACK`. Očekivani konflikt treba obraditi jasno, ne ignorisati.
- **Primeni ista pravila kroz SQLAlchemy 2:** ORM olakšava mapiranje i rad sa objektima, ali integritet i transakcije i dalje treba razumeti na nivou baze.
- **SQLite specifičnosti prepoznaj praktično:** FK provera je per-connection, `INTEGER PRIMARY KEY` je poseban slučaj, `WITHOUT ROWID`, storage klase i `typeof()` imaju SQLite semantiku.

Ne moraš pamtiti unutrašnji format SQLite baze niti svaku detaljnu razliku implementacije. Kada pređeš na PostgreSQL ili MySQL, proveri razlike u tipovima, generisanju ID-ja, ponašanju `NULL`/`UNIQUE`, konfliktima, migracijama i transakcijama. SQLAlchemy olakšava rad kroz dijalekte, ali ne uklanja potrebu da testiraš na bazi koju će aplikacija stvarno koristiti.

### Predlog rasporeda rada

Materijal možeš podeliti prema tempu koji ti odgovara, na primer:

1. Ograničenja i planiranje modela (`01`–`02`).
2. Kreiranje tabela, ključevi i veze (`03`).
3. Dodavanje redova (`04`).
4. Izmena i brisanje redova uz transakcije (`05`–`06`).
5. Uklanjanje tabele, CLI pregled i ponavljanje ključnih razlika (`07`).

Ovo je samo predlog, ne raspored koji moraš ispoštovati. Pređi dalje kada umeš da objasniš zašto je svako ograničenje ili transakcija potrebna i možeš bezbedno da predvidiš koje redove će naredba promeniti.
