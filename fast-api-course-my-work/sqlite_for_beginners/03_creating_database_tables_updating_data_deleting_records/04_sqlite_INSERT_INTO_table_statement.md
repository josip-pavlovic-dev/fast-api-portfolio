# 04 — SQLite `INSERT INTO` naredba

## Cilj lekcije

U ovoj lekciji dodajemo redove u tabele `contacts`, `groups` i `contact_groups` koje smo napravili u [prethodnoj lekciji o `CREATE TABLE`](./03_sqlite_create_table_statement_part_2.md). Naučićeš kako da navedeš kolone i vrednosti, ubaciš jedan ili više redova, izostaviš vrednost koja ima podrazumevano ili opciono ponašanje i proveriš rezultat.

Važno: `INSERT` menja podatke. Za vežbe koristi novu, privremenu bazu, ne Chinook, TodoApp ili neku drugu bazu sa važnim podacima.

## Priprema baze

U SQLite CLI-ju pokreni:

```bash
sqlite3 :memory:
```

Zatim izvrši DDL iz prethodne lekcije, uključujući:

```sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
```

Očekivana vrednost je `1`. Ona važi samo za tu konekciju; uključi proveru stranih ključeva za svaku konekciju u kojoj radiš.

## Osnovni oblik `INSERT`

Najjasniji oblik za dodavanje jednog reda je:

```sql
INSERT INTO table_name (column_a, column_b)
VALUES (value_a, value_b);
```

Imena kolona i vrednosti moraju odgovarati po poziciji:

| Kolona     | Vrednost  |
| ---------- | --------- |
| `column_a` | `value_a` |
| `column_b` | `value_b` |

Prvi navedeni naziv kolone dobija prvu vrednost u `VALUES`, drugi naziv drugu vrednost i tako redom. Broj vrednosti mora biti isti kao broj navedenih kolona.

Upotreba eksplicitne liste kolona je preporučena:

```sql
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES ('Ana', 'Anić', 'ana@example.test', '+381601234567');
```

Ovde ne navodimo `id`, jer je kolona definisana kao `id INTEGER PRIMARY KEY`. U običnoj SQLite tabeli to je alias za `rowid`, pa SQLite može dodeliti ID. To pravilo ne važi za svaki primarni ključ: tekstualni i složeni ključevi ne dobijaju automatski vrednost na ovaj način. Ako sistem treba da koristi posebno generisanje identifikatora, ono mora biti definisano za taj tip baze i ključ.

### Tekst, brojevi i `NULL`

- Tekstualne vrednosti pišu se u jednostrukim navodnicima: `'Ana'`.
- Brojevi se pišu bez navodnika: `42`.
- SQL vrednost odsutnosti je ključna reč `NULL`, bez navodnika.
- Ako tekst sadrži jednostruki navodnik, udvostruči ga: `'O''Brien'`.

Ne stavljaj vrednosti u dvostruke navodnike kao da su tekst. U SQL-u su dvostruki navodnici namenjeni identifikatorima, kao što su imena kolona i tabela.

## Dodaj kontakte

Možeš dodati više kontakata istom naredbom. U ovom primeru dodajemo tri kontakta različita od Ane iz prethodnog primera:

```sql
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES
    ('Johnny', 'Cash', 'johnny.cash@example.test', '+12025550101'),
    ('Jane', 'Doe', 'jane.doe@example.test', '+12025550102'),
    ('Toni', 'Ivić', 'toni@example.test', NULL);
```

Ovo je jedna `INSERT` naredba sa tri reda. `NULL` u telefonskoj koloni je dozvoljen jer smo u prethodnoj lekciji izabrali da je `phone` opcion. Nije isto što i prazan tekst `''`: prazan tekst je prisutna tekstualna vrednost, a `NULL` predstavlja odsustvo vrednosti.

Ako izostaviš opcionu kolonu `phone` iz liste kolona, SQLite će primeniti njenu podrazumevanu vrednost ako je definisana, ili `NULL` ako nema `DEFAULT`. U našoj šemi nema `DEFAULT` za `phone`, pa važi `NULL`:

```sql
INSERT INTO contacts (first_name, last_name, email)
VALUES ('Morgan', 'Lee', 'morgan.lee@example.test');
```

Izostavljanje obavezne kolone kao što je `email` dovodi do greške, osim ako kolona ima `DEFAULT` koji zadovoljava pravila šeme. `NOT NULL` odbija `NULL`, ali sam po sebi ne odbija prazan tekst. `UNIQUE` sprečava duplikat vrednosti, ali ne znači da je kolona obavezna.

## Dodaj grupe i redove članstva

Možeš dodati više grupa jednim `INSERT`-om:

```sql
INSERT INTO groups (name)
VALUES
    ('Cash Flow'),
    ('Accounts');
```

Zatim upiši redove koji povezuju kontakte i grupe:

```sql
INSERT INTO contact_groups (contact_id, group_id)
VALUES
    (1, 1),
    (1, 2),
    (2, 1);
```

Ovi brojevi odgovaraju ID-jevima u praznoj bazi posle prethodnih primera: prva dva kontakta su `1` i `2`, a grupe su `1` i `2`. Ako radiš sa postojećim podacima, nemoj pretpostaviti da će ID-jevi biti baš ti brojevi — prvo pronađi stvarne ID vrednosti.

Red u `contact_groups` mora upućivati na postojeći kontakt i grupu. Ako proveru stranih ključeva nisi uključio na toj konekciji, SQLite možda neće odbiti nepostojeći ID pri upisu. Za objašnjenje i proveru tog podešavanja pogledaj [prethodnu lekciju](./03_sqlite_create_table_statement_part_2.md).

## Pregledaj rezultat

U SQLite CLI-ju pročitaj podatke koje si upravo uneo:

```sql
SELECT id, first_name, last_name, email, phone
FROM contacts;

SELECT id, name
FROM groups;

SELECT contact_id, group_id
FROM contact_groups;
```

`SELECT` ne unosi podatke; koristi se da ih pročitaš. Najpre proveri rezultate pre nego što nastaviš sa izmenama.

### Saznaj generisani ID

SQLite 3.35.0 i noviji podržava `RETURNING`, koji vraća vrednosti iz novo ubačenog reda:

```sql
INSERT INTO contacts (first_name, last_name, email)
VALUES ('Riley', 'Park', 'riley.park@example.test')
RETURNING id, email;
```

U SQLite-u starijem od 3.35.0 ova sintaksa nije dostupna. Za ID koji generiše `INTEGER PRIMARY KEY` može se odmah nakon `INSERT`-a, na istoj konekciji, proveriti `last_insert_rowid()`. SQLAlchemy ORM obično popunjava atribut primarnog ključa prilikom `flush()`-a.

```sql
SELECT last_insert_rowid();
```

## Kolone mogu da se izostave — ali ne i nasumično

Ako navedeš listu kolona, redosled vrednosti u `VALUES` prati taj spisak, a ne nužno redosled kolona u definiciji tabele. Zato je ovaj oblik jasan i otporan na kasnije dodavanje kolona:

```sql
INSERT INTO contacts (email, last_name, first_name)
VALUES ('sam@example.test', 'Rivera', 'Sam');
```

Ako izostaviš listu kolona:

```sql
INSERT INTO contacts
VALUES (NULL, 'Sam', 'Rivera', 'sam.positional@example.test', NULL);
```

moraš navesti vrednost za svaku kolonu u tačnom redosledu definicije tabele. Ovaj oblik je krhak: promena šeme može promeniti redosled ili broj kolona i učiniti upit netačnim. Uobičajeno je da se kolone uvek navedu eksplicitno.

Ako izostaviš kolonu iz liste, njena vrednost postaje njen `DEFAULT`, ako je definisan, a inače `NULL`. Zato izostavljanje obavezne kolone bez podrazumevane vrednosti obično dovodi do greške `NOT NULL`.

## Umetanje podataka u SQLAlchemy 2

Koristi modele `Contact` i `Group` i engine iz [prethodne SQLAlchemy 2 mape](./03_sqlite_create_table_statement_part_2.md). Ovde je prikazan unos preko ORM-a:

```python
from sqlalchemy.orm import Session


with Session(engine) as session, session.begin():
    johnny = Contact(
        first_name="Johnny",
        last_name="Cash",
        email="johnny.cash@example.test",
        phone="+12025550101",
    )
    jane = Contact(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.test",
        phone="+12025550102",
    )
    cash_flow = Group(name="Cash Flow")
    accounts = Group(name="Accounts")

    johnny.groups.extend([cash_flow, accounts])
    jane.groups.append(cash_flow)
    session.add_all([johnny, jane])
    session.flush()

    print(johnny.id, jane.id, cash_flow.id, accounts.id)
```

`relationship()` omogućava ORM-u da napravi odgovarajuće redove u pomoćnoj tabeli `contact_groups` kada se objekti upišu. Ne dodaj ručno iste redove u `contact_groups` povrh veza koje si već postavio preko `johnny.groups` i `jane.groups`, jer bi pokušaj ponovnog upisa istog para prekršio složeni primarni ključ.

- `session.add_all(...)` dodaje ORM objekte u sesiju.
- `session.flush()` šalje `INSERT` naredbe bazi i popunjava generisane ID atribute, ali samo po sebi ne završava transakciju.
- `session.begin()` potvrđuje transakciju ako blok uspe, a radi rollback ako se dogodi izuzetak. `Session` se po završetku zatvara.

Ovaj primer pretpostavlja praznu bazu: ako već postoje redovi sa istim jedinstvenim email-om, telefonom ili nazivom grupe, baza će odbiti upis. SQLAlchemy te konflikte obično prijavi kao `IntegrityError`. Obradi očekivani konflikt na nivou aplikacije; ne ignoriši ga i ne prikazuj korisniku sirovu poruku baze. Za više o tome pogledaj [lekciju o ograničenjima](./01_sqlite_constraints.md).

### Vrednosti iz aplikacije šalji kao parametre

Kada se SQL naredba sastavlja u Python-u, nemoj ugrađivati vrednost u SQL pomoću f-string-a ili spajanja stringova. Koristi parametarsko vezivanje:

```python
from sqlalchemy import text


group_name = "New group"
with engine.begin() as connection:
    connection.execute(
        text("INSERT INTO groups (name) VALUES (:name)"),
        {"name": group_name},
    )
```

Tako SQL i vrednosti ostaju odvojeni, a drajver bezbedno prosleđuje vrednost bazi. Isto važi za `sqlite3` modul: koristi `?` parametre, a ne građenje SQL teksta od korisničkog unosa.

## Šta transkript pojednostavljuje — važne ispravke

1. **`INSERT INTO` podrazumeva dve ključne liste:** kolone i odgovarajuće vrednosti. Izostavljanje liste kolona zahteva vrednost za svaku kolonu u tačnom redosledu; zato je eksplicitna lista bolja.
2. **Ne generiše se svaki primarni ključ automatski.** U našem primeru to radi SQLite posebnost `id INTEGER PRIMARY KEY`. Tekstualni ili složeni PK zahteva drugačije vrednosti ili pravilo.
3. **Izostavljena kolona ne znači uvek „moraš uneti vrednost“.** Baza primenjuje `DEFAULT`, ako postoji, inače `NULL`; zatim `NOT NULL` i ostala ograničenja odlučuju da li je upis prihvatljiv.
4. **`NOT NULL` ne zabranjuje prazan tekst.** Ako polje mora da sadrži neprazan tekst, potrebna je i odgovarajuća `CHECK` provera.
5. **Poruka „query ran“ ili uspeh u GUI alatu nije provera sadržaja.** Proveri redove pomoću `SELECT`-a i ograničenja namerno testiraj zasebnim nevažećim unosima.
6. **Višeredni `INSERT` je jedna SQL naredba.** Ako red prekrši ograničenje uz podrazumevano ponašanje `ABORT`, SQLite poništava izmene te naredbe, a ne prethodne naredbe u transakciji.

## Vežbe

U novoj `:memory:` bazi prvo napravi tabele iz prethodne lekcije, a zatim:

1. Unesi dva kontakta sa eksplicitnim listama kolona. Izostavi `phone` kod jednog kontakta i proveri da li je vrednost `NULL`.
2. Unesi dve grupe jednom višerednom `INSERT` naredbom.
3. Upiši tri reda u `contact_groups` i proveri parove pomoću `SELECT`.
4. Pokušaj da uneseš ponovljeni email, a zatim i ponovljeni par `contact_id` + `group_id`. Zabeleži koja ograničenja odbijaju unose.
5. Izostavi `email` i pokušaj da uneseš kontakt. Objasni dobijenu grešku. Zatim uporedi izostavljeni `phone`, eksplicitni `NULL` i prazan tekst `''`.
6. Ponovi jedan važeći unos pomoću SQLAlchemy ORM-a i potvrdi da su kreirani i redovi u `contact_groups`.
7. Pošalji naziv grupe SQLAlchemy `text()` naredbom sa vezanim parametrom.

## Provera razumevanja

1. Zašto treba pisati listu kolona posle imena tabele?
2. Kada se automatski generiše `id` iz našeg modela, a kada ne treba očekivati automatsko generisanje?
3. Koja je razlika između izostavljene kolone, `NULL` i praznog teksta?
4. Šta se dešava ako se broj vrednosti ne poklapa sa brojem navedenih kolona?
5. Da li je `session.flush()` isto što i `commit()`?
6. Zašto je bolje povezati aplikacijske vrednosti kao SQL parametre?
7. Kako ORM zna koje redove treba uneti u `contact_groups`?

## Izvori za dalje čitanje

- [SQLite: INSERT](https://www.sqlite.org/lang_insert.html)
- [SQLite: RETURNING clause](https://www.sqlite.org/lang_returning.html)
- [SQLite: Foreign Key Support](https://www.sqlite.org/foreignkeys.html)
- [SQLAlchemy 2.0: Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [SQLAlchemy 2.0: INSERT statements](https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html)
