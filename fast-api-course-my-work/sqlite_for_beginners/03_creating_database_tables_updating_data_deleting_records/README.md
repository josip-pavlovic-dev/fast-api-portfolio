# Oblast 03 — Kreiranje tabela, izmena podataka i brisanje zapisa

Ova oblast pokriva modelovanje tabela i veza, ograničenja integriteta i osnovne naredbe za kreiranje, unos, izmenu i brisanje podataka. Lekcije prolazi redom: kasnije vežbe koriste tabele i pravila definisana ranije.

## Lekcije

1. [SQLite ograničenja (`constraints`)](./01_sqlite_constraints.md)
2. [`CREATE TABLE` i planiranje modela — prvi deo](./02_sqlite_create_table_statement_part_1.md)
3. [`CREATE TABLE` — drugi deo](./03_sqlite_create_table_statement_part_2.md)
4. [`INSERT INTO`](./04_sqlite_INSERT_INTO_table_statement.md)
5. [`UPDATE`](./05_sqlite_UPDATE_statement.md)
6. [`DELETE`](./06_sqlite_DELETE_statement.md)
7. [`DROP TABLE`](./07_sqlite_DROP_table_statement.md)

## Cilj i prioritet

Posle oblasti treba da možeš da:

- modeluješ tabele, primarne i strane ključeve i veze N:M pomoću povezničke tabele;
- izabereš ograničenja koja sprovode pravila podataka u samoj bazi;
- bezbedno dodaš, izmeniš i obrišeš redove, proveriš rezultat i po potrebi vratiš transakciju;
- razlikuješ brisanje reda (`DELETE`) od uklanjanja tabele iz šeme (`DROP TABLE`);
- razumeš kako SQLAlchemy mapira šemu i upravlja ORM objektima, a da ne mešaš ORM vezu sa ograničenjem baze.

Temeljno nauči prenosive principe: integritet podataka, PK/FK veze, ograničenja, CRUD naredbe i transakcije. SQLite specifičnosti — `rowid`, `WITHOUT ROWID`, ponašanje `NULL`, `PRAGMA` i detalje tipizacije — razumi dovoljno da prepoznaš njihov uticaj. Prati i [plan učenja](../plan_ucenja/sta_je_vazno.md), naročito naglasak na ispravnom upravljanju transakcijama i greškama.

## Na šta posebno da obratiš pažnju

### Ograničenja i vrednosti

- `NOT NULL` odbija `NULL`, ali ne i prazan tekst `''` ili samo razmake. Za neprazan naziv potreban je i odgovarajući `CHECK`; `trim()` bez dodatnih znakova uklanja obične razmake, ne nužno sve Unicode razmake.
- `UNIQUE` samo po sebi ne znači obavezno: SQLite dozvoljava više `NULL` vrednosti u jedinstvenoj koloni. Podrazumevano poređenje teksta razlikuje velika i mala slova.
- `CHECK` koji daje `NULL` ne smatra se prekršenim. Zato pravilo kao `CHECK (age >= 18)` ne zamenjuje `NOT NULL`. U običnoj SQLite tabeli `CHECK` takođe ne garantuje deklarisani tip vrednosti.
- `DEFAULT` se koristi kada se kolona izostavi iz `INSERT`-a; eksplicitni `NULL` nije izostavljanje. U SQLAlchemy-ju razlikuj Python/ORM `default` od DB `server_default`.
- FK provera mora biti uključena sa `PRAGMA foreign_keys = ON` na svakoj konekciji, pre transakcije. `PRAGMA foreign_keys` pokazuje podešavanje te konekcije, dok `PRAGMA foreign_key_list(...)` prikazuje FK definicije u šemi.

### Modelovanje i `CREATE TABLE`

- Tačan `INTEGER PRIMARY KEY` u običnoj rowid tabeli ima posebno SQLite ponašanje: alias je za `rowid`. To ne važi za `INT PRIMARY KEY`, tekstualni ili složeni ključ, niti za `WITHOUT ROWID` tabelu. Ne dodaj `AUTOINCREMENT` automatski.
- Zbog istorijskog SQLite ponašanja, nemoj pretpostaviti da je svaki tekstualni ili složeni `PRIMARY KEY` automatski `NOT NULL`; navedi obaveznost eksplicitno kada je potrebna.
- Složeni PK u povezničkoj tabeli sprečava ponavljanje istog para, ali dozvoljava da se svaki pojedinačni ID ponavlja u drugim parovima. FK-ovi proveravaju postojeće veze; sami ne zahtevaju da svaki kontakt ima bar jedno članstvo.
- `WITHOUT ROWID` zahteva PK i prikladan je za neke tabele sa prirodnim složenim ključem; nije podrazumevani izbor za svaku tabelu.
- `CREATE TABLE IF NOT EXISTS` preskače kreiranje ako objekat već postoji, ali ne proverava niti usklađuje postojeću šemu. `create_all()` takođe nije migracija; za promene postojeće šeme koristi kontrolisane migracije.
- SQLite `String(n)` ili `VARCHAR(n)` samo po sebi ne ograničava dužinu teksta. Ako je maksimalna dužina pravilo integriteta, definiši je odgovarajućim ograničenjem.

### `INSERT`, `UPDATE` i `DELETE`

- U `INSERT`-u navodi kolone eksplicitno. Izostavljena kolona dobija `DEFAULT`, ako postoji, inače `NULL`, nakon čega se primenjuju ograničenja. Automatski generisani ID u primerima odnosi se na `INTEGER PRIMARY KEY`; ne pretpostavljaj unapred konkretne ID vrednosti u postojećoj bazi.
- Višeredni `INSERT` je jedna naredba: ako red prekrši ograničenje uz podrazumevani `ABORT`, poništava se ta naredba u celini, ne ranije završene naredbe u transakciji.
- SQLite podržava `INSERT ... RETURNING` od verzije 3.35.0. Kada koristiš `last_insert_rowid()`, pozovi ga odmah na istoj konekciji. U Python aplikaciji prosleđuj vrednosti kao parametre umesto da sastavljaš SQL string.
- Pre `UPDATE`-a ili `DELETE`-a proveri ciljne redove pomoću istog `WHERE` uslova. Izostavljen `WHERE` menja ili briše sve redove; uslov koji ne pogodi nijedan red može ipak završiti bez SQL greške.
- `changes()` govori koliko je redova direktno obuhvatila poslednja DML naredba. Može brojati red i kada je vrednost posle `UPDATE`-a ista; kod `DELETE`-a ne uključuje redove uklonjene kaskadom.
- Ograničenja važe i pri `UPDATE`-u. Pri neuspelom upitu, podrazumevano `ABORT` poništava tu naredbu, ali ne mora automatski poništiti celu eksplicitnu transakciju; proveri stanje i uradi `ROLLBACK` pre nastavka.
- `DELETE` nad `contact_groups` može ukloniti samo vezu, ostavljajući kontakt i grupu. Brisanje roditeljskog reda može aktivirati `ON DELETE CASCADE`, ali samo kada je FK provera uključena.

### `DROP TABLE` i transakcije

- `DELETE FROM table` uklanja redove; `DROP TABLE table` uklanja definiciju tabele i njene podatke, kao i povezane indekse i okidače. `DROP TABLE` nema `WHERE`.
- Sa aktivnim FK proverama, `DROP TABLE` može sprovesti kaskadno uklanjanje povezanih redova ili biti odbijen zbog FK pravila. U primeru oblasti 03, brisanje `groups` kaskadno uklanja članstva u `contact_groups`, ali ne i kontakte.
- Pri implicitnom brisanju koje SQLite izvršava tokom `DROP TABLE`, okidači vezani za tabelu koja se uklanja ne pokreću se; pregledaj zavisnosti i šemu pre operacije.
- `IF EXISTS` izbegava grešku samo ako tabela ne postoji; ne potvrđuje da je brisanje bezbedno niti štiti od pogrešnog imena.
- `BEGIN`/`COMMIT` i `BEGIN`/`ROLLBACK` su alternativni završeci iste transakcije. U probnoj bazi možeš proveriti da `ROLLBACK` vraća i podatke i šemu nakon `DROP TABLE`; transakcija nije zamena za rezervnu kopiju.
- ORM `Session.delete()` briše red/objekat, ne tabelu. `Table.drop()` i naročito `Base.metadata.drop_all()` menjaju šemu i koriste se samo nad namenskim probnim bazama.

## Vežbe i bezbedan način rada

SQL vežbe su u [playground/sql/03_creating_database_tables_updating_data_deleting_records/](../playground/sql/03_creating_database_tables_updating_data_deleting_records/), a dodatna SQLite CLI vežba za `.tables`, `.schema` i transakcioni `DROP TABLE` nalazi se u [04_sqlite_schema_and_drop_table.txt](../playground/cli/04_sqlite_schema_and_drop_table.txt).

Svaki od sedam `.sql` fajlova pravi probne tabele, a više skripti koristi ista imena. Pokreni svaki u novoj memorijskoj bazi, iz korena repozitorijuma:

```bash
sqlite3 :memory:
```

Zatim, u SQLite CLI promptu, učitaj jednu vežbu:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/01_sqlite_constraints.sql
```

Za sledeći fajl zatvori konekciju sa `.quit` i ponovo pokreni `sqlite3 :memory:`. Ne učitavaj sve fajlove redom u istu već popunjenu bazu. U SQLTools-u koristi posebnu, praznu `sandbox.db` konekciju, nikada Chinook ili bazu aplikacije; proveri putanju i resetuj sandbox pre ponavljanja vežbe.

Nevažeći primeri koji namerno krše ograničenja i opasni upiti bez `WHERE` ostavljeni su kao komentari u skriptama. Pokreni ih samo pojedinačno, nakon pripreme odgovarajuće probne baze. Meta-komande `.tables` i `.schema` unose se u SQLite CLI, ne kao obični SQL upiti. `.read` takođe pripada CLI-ju i izvršava fajl u trenutno otvorenoj konekciji.

Detaljna uputstva, objašnjena rešenja i proverene rezultate za sve lekcije oblasti nalaze se u [danu 07](../pitanja_i_odgovori/dan_07_creating_database_tables_updating_data_deleting_records.md). Oznaka „Dan 07“ je naziv dokumenta: materijal obuhvata celu oblast 03 i nije predviđeno da se završi za jedan dan. Za opšta pravila i primere rada u Playground-u pogledaj [Playground README](../playground/README.md).

### Proverene vežbe

Svih sedam SQL skripti i CLI vežba uspešno su izvršene u zasebnim `:memory:` bazama. To proverava izvršivost primera i izolaciju od trajnih baza; očekivane greške ograničenja su komentarisane i treba ih isprobati odvojeno, kako je opisano u lekcijama.

### Prenosivo znanje i SQLite specifičnosti

Ograničenja integriteta, relacije, CRUD naredbe i transakcije važe i u drugim relacionim bazama, ali se detalji tipova, `NULL`, automatskog generisanja ID-jeva, FK podešavanja i konflikata razlikuju. Kada pređeš na MySQL ili PostgreSQL, ponovo proveri ponašanje ograničenja, transakcija i migracija na ciljnom sistemu; SQLAlchemy ne uklanja razlike između baza.

Nazad na [glavni README kursa](../README.md).
