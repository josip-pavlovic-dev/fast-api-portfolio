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

| Naredba               | Efekat                                                                            |
| --------------------- | --------------------------------------------------------------------------------- |
| `DELETE FROM groups;` | Briše sve redove iz `groups`, ali tabela i njena definicija ostaju.               |
| `DROP TABLE groups;`  | Briše tabelu `groups`, njene podatke, indekse i okidače (triggers) vezane za nju. |

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

Da. SQLite može da izvrši `DROP TABLE` unutar eksplicitne transakcije. Dok je transakcija otvorena, možeš pregledati posledice i zatim odlučiti da promene potvrdiš pomoću `COMMIT` ili poništiš pomoću `ROLLBACK`.

### Šta je transakcija?

**Transakcija** je logička celina jedne ili više operacija nad bazom. Pomaže da povezane promene budu potvrđene zajedno ili da se ponište zajedno. Na primer, pri prebacivanju novca između dva računa ne želiš da se potvrdi samo umanjenje jednog stanja, a da uvećanje drugog ne uspe.

Važni pojmovi koji se često povezuju sa transakcijama su **ACID**:

- **Atomicity — atomarnost:** uspešno potvrđuješ celinu promena ili ih poništavaš, umesto da namerno ostaviš samo deo logičke operacije.
- **Consistency — konzistentnost:** transakcija treba da sačuva pravila podataka; SQLite proverava definisana ograničenja, ali sama transakcija ne može garantovati ispravnost svih poslovnih pravila koja nisu izražena u bazi ili aplikaciji.
- **Isolation — izolacija:** druge konekcije ne vide neophodno svaku međukorak-promenu kao deo svoje redovne obrade; detalji vidljivosti i konkurentnog pristupa zavise od konekcija i režima baze.
- **Durability — trajnost:** uspešno potvrđene promene treba da opstanu. Stvarna otpornost na prekide zavisi i od SQLite podešavanja, fajl-sistema i hardvera. Baza `:memory:` nestaje kada se konekcija zatvori, čak i ako je transakcija potvrđena.

Transakcije nisu namenjene samo za `DROP TABLE`: koriste se i za više povezanih `INSERT`, `UPDATE` ili `DELETE` naredbi, kao i kada želiš da pregledaš probnu promenu pre potvrde.

### Šta rade `BEGIN`, `COMMIT` i `ROLLBACK`?

| Naredba     | Značenje                                                    |
| ----------- | ----------------------------------------------------------- |
| `BEGIN;`    | Započinje eksplicitnu transakciju na trenutnoj konekciji.   |
| `COMMIT;`   | Pokušava da potvrdi promene i završi aktivnu transakciju.   |
| `ROLLBACK;` | Poništava nepotvrđene promene te transakcije i završava je. |

`BEGIN TRANSACTION;` je čitljivija varijanta `BEGIN;`. `END TRANSACTION;` je u SQLite-u alternativa za `COMMIT;`. U primerima ćemo koristiti kraće oblike.

Završavaš transakciju sa **jednom** od dve alternative: `COMMIT` ili `ROLLBACK`. Ne izvršavaj oba kao dva koraka za istu transakciju. Na primer:

```text
BEGIN
  ├─ SQL promene i provera
  ├─ COMMIT   → prihvati promene
  └─ ROLLBACK → poništi promene
```

Između `BEGIN` i završetka transakcije tvoja trenutna konekcija vidi sopstvene promene, pa možeš da ih proveriš upitom ili komandom `.tables`. To što ih vidiš ne znači da su potvrđene.

### Primer: poništi uklanjanje tabele

Za ovaj primer otvori **novu** `sqlite3 :memory:` konekciju i ponovi [pripremu probne baze](#priprema-probne-baze), uključujući `PRAGMA foreign_keys = ON` pre transakcije. To je važno jer su raniji primeri možda već obrisali `groups`; očekuju se dve grupe i tri reda u `contact_groups`.

```sql
BEGIN;
DROP TABLE groups;
SELECT COUNT(*) AS remaining_memberships FROM contact_groups;
```

Rezultat za članstva je `0`, jer se uz uključene strane ključeve primenjuje `ON DELETE CASCADE`. U SQLite CLI-ju proveri i tabele:

```text
.tables
```

Na trenutnoj konekciji `groups` se tokom transakcije više ne prikazuje. Zatim **poništi** transakciju:

```sql
ROLLBACK;
```

Sada proveri šemu i podatke:

```text
.tables
```

```sql
SELECT COUNT(*) AS restored_groups FROM groups;
SELECT COUNT(*) AS restored_memberships FROM contact_groups;
```

Rezultati su `2` i `3`: `ROLLBACK` je vratio tabelu `groups`, njene redove i redove članstva uklonjene kaskadom u toj transakciji. Ne vraća se samo ime tabele već i stanje izmenjeno tom transakcijom.

### Primer: potvrdi uklanjanje tabele

U drugoj novoj `:memory:` konekciji ponovo pripremi iste tabele i podatke. Ovaj put umesto `ROLLBACK` izaberi `COMMIT`:

```sql
BEGIN;
DROP TABLE groups;
SELECT COUNT(*) AS remaining_memberships FROM contact_groups;
COMMIT;
```

Broj članstava pre potvrde je `0`. Posle `COMMIT`, `.tables` ne prikazuje `groups`, dok `SELECT COUNT(*) FROM contact_groups;` vraća `0`, a `SELECT COUNT(*) FROM contacts;` vraća `2`. `contacts` i `contact_groups` ostaju, ali kaskadno obrisani redovi članstva su deo potvrđene promene.

Posle uspešnog `COMMIT`-a `ROLLBACK` ne može da vrati tu prethodno potvrđenu transakciju. Za povratak nakon potvrde potrebna je odgovarajuća rezervna kopija ili drugi unapred pripremljen način oporavka.

### Šta ako ne napišem `BEGIN`?

SQLite i dalje koristi transakcije: kada nema aktivne eksplicitne transakcije, naredba kojoj je transakcija potrebna pokreće implicitnu transakciju. Ona se automatski završava kada se završi poslednja aktivna naredba koja je koristi. Zato u uobičajenoj CLI upotrebi samostalni uspešni `DROP TABLE` postaje potvrđena promena bez posebnog `COMMIT`-a.

Ako želiš mogućnost da proveriš rezultat **pre odluke** i više izmena potvrdiš ili poništiš zajedno, pokreni eksplicitni `BEGIN` **pre** promena. Naknadni `ROLLBACK` ne može poništiti prethodnu automatski potvrđenu naredbu.

### Greške, zatvaranje konekcije i granice zaštite

- **Greška ne mora poništiti celu transakciju.** SQLite u mnogim uobičajenim slučajevima, uključujući podrazumevano `ABORT` ponašanje za ograničenja, poništava neuspelu naredbu, dok ranije uspešne promene u transakciji ostaju nepotvrđene. Neke vrste grešaka ili konfliktne politike mogu poništiti i celu transakciju. Pročitaj grešku i proveri stanje; ako transakcija još traje i ne želiš njene promene, koristi `ROLLBACK`.
- **`COMMIT` može da ne uspe**, na primer zbog odloženog ograničenja stranog ključa ili zaključavanja. Nemoj pretpostaviti da je promena potvrđena ako je prijavljena greška. U tim slučajevima transakcija može ostati aktivna: reši problem i pokušaj ponovo ili izvrši `ROLLBACK`.
- **Zatvaranje konekcije sa nepotvrđenom transakcijom** dovodi do poništavanja te transakcije. Nemoj koristiti zatvaranje CLI-ja kao zamenu za jasnu odluku o `COMMIT` ili `ROLLBACK`.
- **Transakcija nije rezervna kopija.** Posle potvrde ne možeš poništiti tu transakciju sa `ROLLBACK`, a transakcija sama ne štiti od kasnijeg gubitka ili oštećenja datoteke.
- **Strani ključevi i konekcija:** proveri `PRAGMA foreign_keys;` i po potrebi ga uključi pre `BEGIN`. Promena te postavke unutar aktivne transakcije nema efekta. `ROLLBACK` poništava i kaskadne promene nastale u istoj transakciji.
- **Nema ugnježđenog `BEGIN`-a:** drugi `BEGIN` dok je transakcija aktivna prijavljuje grešku. Za delimično poništavanje unutar transakcije SQLite podržava `SAVEPOINT` i `ROLLBACK TO`; završetak spoljne transakcije je i dalje zasebna odluka.

### Kratko o konkurentnom radu

Transakcija pripada konekciji koja ju je otvorila; druga CLI ili SQLAlchemy konekcija ne deli automatski istu transakciju. SQLite dozvoljava više čitalaca, ali samo jednu transakciju za pisanje u istom trenutku. Dugo otvorena transakcija, naročito ona koja menja podatke, može otežati rad drugim konekcijama, zato je završi čim je provera gotova.

`BEGIN` bez dodatka koristi podrazumevani `DEFERRED` režim. SQLite podržava i `BEGIN IMMEDIATE` i `BEGIN EXCLUSIVE`, koji drugačije upravljaju početkom transakcije za pisanje i zaključavanjem; za osnovne vežbe dovoljan je `BEGIN`. Pri prelasku na drugi DBMS proveri njegovo ponašanje, posebno oko transakcija i DDL naredbi.

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
9. U novoj probnoj bazi započni transakciju, dodaj jednu grupu i promeni naziv druge. Proveri obe promene, pa izvrši `ROLLBACK` i potvrdi da su obe poništene.
10. U novoj probnoj bazi ponovi prethodnu vežbu, ali potvrdi promene sa `COMMIT`. Objasni zašto naknadni `ROLLBACK` ne može da ih vrati.
11. Tokom transakcije pokušaj unos grupe čiji `name` već postoji. Pročitaj grešku i proveri da li su ranije uspešne promene u transakciji i dalje vidljive; zatim ih poništi pomoću `ROLLBACK`.

## Provera razumevanja

1. Koja je razlika između `DELETE FROM groups` i `DROP TABLE groups`?
2. Šta se dešava sa indeksima i okidačima (triggers) vezanim za tabelu koja se uklanja?
3. Zašto se `contact_groups` redovi brišu kada se ukloni `groups` u ovom modelu?
4. Šta radi `DROP TABLE IF EXISTS` i šta **ne** garantuje?
5. Koja je razlika između SQLAlchemy `Session.delete()` i `Group.__table__.drop()`?
6. Kada je prihvatljivo koristiti `Base.metadata.drop_all(engine)`?
7. Kako `ROLLBACK` može pomoći tokom kontrolisane vežbe `DROP TABLE`?
8. Šta je transakcija i zašto je korisna kada se više izmena odnosi na jednu logičku operaciju?
9. Zašto se `COMMIT` i `ROLLBACK` ne koriste jedan za drugim kao završeci iste transakcije?
10. Šta se dešava ako izvršiš `DROP TABLE` bez eksplicitnog `BEGIN`?
11. Da li greška u jednoj naredbi uvek poništava celu transakciju? Šta treba proveriti pre nastavka?
12. Zašto transakcija nije zamena za rezervnu kopiju?
13. Kada se podešava `PRAGMA foreign_keys` u odnosu na `BEGIN`?

## Izvori za dalje čitanje

- [SQLite: DROP TABLE](https://www.sqlite.org/lang_droptable.html)
- [SQLite: Foreign Key Support](https://www.sqlite.org/foreignkeys.html)
- [SQLite: Transactions](https://www.sqlite.org/lang_transaction.html)
- [SQLAlchemy 2.0: Creating and Dropping Database Tables](https://docs.sqlalchemy.org/en/20/core/metadata.html#creating-and-dropping-database-tables)
