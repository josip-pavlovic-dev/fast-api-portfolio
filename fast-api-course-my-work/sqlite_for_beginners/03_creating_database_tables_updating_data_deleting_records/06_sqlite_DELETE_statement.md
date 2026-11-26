# 06 — SQLite `DELETE` naredba

## Cilj lekcije

`DELETE` uklanja postojeće redove iz tabele. U ovoj lekciji obrisaćemo grupu `Accounts`, proveriti koji su redovi uklonjeni i razjasniti razliku između brisanja veze u `contact_groups`, brisanja roditeljskog reda i brisanja cele tabele.

Brisanje podataka može biti nepovratno nakon potvrde transakcije. Vežbaj samo u novoj memorijskoj bazi, ne nad Chinook, TodoApp ili drugom važnom bazom.

## Priprema baze i podataka

Otvori SQLite memorijsku bazu i napravi tabele kao u [prethodnoj lekciji](./03_sqlite_create_table_statement_part_2.md):

```bash
sqlite3 :memory:
```

Uključi proveru stranih ključeva na ovoj konekciji:

```sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
```

Očekivani rezultat je `1`. Ovo mora biti uključeno na svakoj konekciji na kojoj očekuješ proveru stranih ključeva i `ON DELETE` akcija.

Za ponovljiv primer, u praznoj bazi dodaj kontakte, grupe i članstva:

```sql
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES
    ('Johnny', 'Cash', 'johnny.cash@example.test', '+12025550101'),
    ('Jane', 'Doe', 'jane.doe@example.test', '+12025550102');

INSERT INTO groups (name)
VALUES
    ('Cash Flow'),
    ('Accounts');

INSERT INTO contact_groups (contact_id, group_id)
VALUES
    (1, 1),
    (1, 2),
    (2, 1);
```

U ovoj praznoj bazi `Accounts` će imati `id = 2`. U već postojećoj bazi nemoj pretpostaviti koji je ID grupe — prvo ga pronađi.

## Osnovni oblik naredbe

```sql
DELETE FROM table_name
WHERE condition;
```

- `DELETE FROM` navodi tabelu iz koje se brišu redovi.
- `WHERE` određuje koji redovi se brišu.
- `DELETE` uklanja redove, ali ne uklanja definiciju tabele.

Pre brisanja proveri šta tačno odgovara uslovu:

```sql
SELECT id, name
FROM groups
WHERE id = 2;
```

Očekivani red je grupa `Accounts`. Zatim obriši samo taj red:

```sql
DELETE FROM groups
WHERE id = 2;
```

Proveri da je grupa uklonjena:

```sql
SELECT id, name
FROM groups;
```

U našem modelu `groups.id` je primarni ključ, pa uslov `id = 2` može ciljati najviše jedan red. Uslov po nazivu nije nužno jedinstven u svakoj šemi; za precizno brisanje koristi primarni ključ ili drugo jedinstveno polje.

## Zašto je `WHERE` presudan?

Ako izostaviš `WHERE`, `DELETE` uklanja **sve redove** iz navedene tabele:

```sql
DELETE FROM groups;
```

Nemoj pokretati ovaj primer nad podacima koje želiš da sačuvaš. SQLite neće zatražiti potvrdu. Ako je tabela povezana sa drugim tabelama, strane ključeve i njihove `ON DELETE` akcije takođe treba uzeti u obzir.

`DELETE FROM groups;` ipak ne briše samu tabelu `groups` niti njenu strukturu. Za uklanjanje tabele koristi se `DROP TABLE` — to je druga, znatno šira operacija.

## Brisanje veze nije isto što i brisanje kontakta ili grupe

Ako želiš samo da ukloniš Johnny-jevo članstvo u grupi `Accounts`, obriši red iz pomoćne tabele:

```sql
DELETE FROM contact_groups
WHERE contact_id = 1
  AND group_id = 2;
```

Ovo briše samo vezu između kontakta `1` i grupe `2`. Kontakt Johnny i grupa `Accounts` ostaju u svojim tabelama. Uslov koristi obe kolone složenog primarnog ključa `contact_groups`.

Gornji primer članstva i brisanja veze nezavisan je od primera koji briše grupu `Accounts`: ako si već obrisao grupu, kaskadno je uklonjen i njen red veze. Za isprobavanje oba oblika, ponovo napravi praznu bazu i dodaj početne podatke.

## Šta se dešava sa povezanim redovima?

U šemi iz prethodne lekcije strane ključne kolone u `contact_groups` definisane su sa `ON DELETE CASCADE`. Zato brisanje grupe iz `groups` uklanja i redove članstva koji upućuju na nju:

```sql
SELECT contact_id, group_id
FROM contact_groups;

DELETE FROM groups
WHERE id = 2;

SELECT contact_id, group_id
FROM contact_groups;

SELECT id, first_name, last_name
FROM contacts;
```

Pre brisanja su članstva `(1, 1)`, `(1, 2)` i `(2, 1)`. Posle brisanja grupe `2`, ostaju `(1, 1)` i `(2, 1)`. Oba kontakta i grupa `Cash Flow` ostaju u svojim tabelama. `ON DELETE CASCADE` ovde čisti zavisne redove u pomoćnoj tabeli, a ne briše sve povezane entitete.

Kaskada radi samo ako je provera stranih ključeva uključena na toj konekciji. Ako je `PRAGMA foreign_keys` isključen, SQLite može obrisati grupu, a ostaviti redove u `contact_groups` koji više ne upućuju ni na jednu grupu.

### Proveri broj obrisanih redova

SQLite CLI funkcija `changes()` vraća broj redova koje je izmenila poslednja `INSERT`, `UPDATE` ili `DELETE` naredba:

```sql
DELETE FROM groups
WHERE id = 2;

SELECT changes();
```

Ako je grupa pronađena, očekuj jedan direktno obrisan red. Broj ne uključuje dodatne redove uklonjene kaskadnim akcijama. Ako dobiješ `0`, proveri ID i uslov — možda više nema grupe sa tim ID-jem.

## Koristi transakciju za proveru pre potvrde

Za važnije brisanje možeš proveriti redove, obrisati ih i proveriti rezultat u transakciji:

```sql
BEGIN;

SELECT id, name
FROM groups
WHERE id = 2;

DELETE FROM groups
WHERE id = 2;

SELECT changes();

SELECT id, name
FROM groups;

SELECT contact_id, group_id
FROM contact_groups;
```

Ako je rezultat očekivan, potvrdi transakciju:

```sql
COMMIT;
```

Ako si izabrao pogrešan red ili je rezultat neočekivan, poništi je:

```sql
ROLLBACK;
```

`COMMIT` i `ROLLBACK` su alternative za završetak iste transakcije; ne izvršavaju se oba nakon istog `BEGIN`. Pre `COMMIT`-a proveri i kaskadno obrisane redove. Ako se dogodi greška, uradi `ROLLBACK` pre nastavka rada.

## Isti koncept u SQLAlchemy 2

Koristi `Contact`, `Group` i `engine` iz [prethodne SQLAlchemy mape](./03_sqlite_create_table_statement_part_2.md). Za probu dodaj kontakte, dve grupe i njihove veze:

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
```

Zatim obriši grupu `Accounts` po njenom primarnom ključu:

```python
with Session(engine) as session, session.begin():
    accounts = session.get(Group, 2)
    if accounts is None:
        raise LookupError("Grupa sa id=2 ne postoji.")

    session.delete(accounts)
```

`session.delete()` označava ORM objekat za brisanje; SQLAlchemy izvršava potrebne `DELETE` naredbe pri `flush()`-u ili završetku transakcije. Sa `relationship(..., secondary=contact_groups)` ORM uklanja i redove članstva povezane sa grupom, a ne kontakt `Johnny`. Dodatno, FK `ON DELETE CASCADE` u šemi štiti i direktne SQL upite, pod uslovom da je SQLite FK provera uključena.

Ako želiš samo da ukloniš vezu preko ORM-a, a da sačuvaš grupu i kontakt, ukloni kontakt iz kolekcije grupe:

```python
with Session(engine) as session, session.begin():
    accounts = session.get(Group, 2)
    johnny = session.get(Contact, 1)
    if accounts is None or johnny is None:
        raise LookupError("Kontakt ili grupa ne postoje.")

    accounts.contacts.remove(johnny)
```

Ovo briše članstvo iz pomoćne tabele, ne entitete `accounts` ili `johnny`. U poslovnom kodu izaberi jedan jasan način upravljanja vezom; nemoj istovremeno ručno brisati isti red i preko SQL-a i preko `relationship()`-a.

Kao i kod SQLAlchemy `UPDATE` primera, `with Session(engine) as session, session.begin():` potvrđuje promene ako blok uspe i radi rollback ako se dogodi izuzetak. Promena u bazi postaje trajna tek kada se transakcija potvrdi.

## Šta je transkript pojednostavio — važne ispravke

1. **Ispravan oblik je `DELETE FROM table_name WHERE ...`.** `FROM` je deo sintakse; `DELETE` sam po sebi ne navodi tabelu.
2. **Bez `WHERE` brišu se svi redovi te tabele.** To ne uklanja definiciju tabele, ali može imati kaskadne posledice u drugim tabelama.
3. **Brisanje roditeljskog reda može uticati na povezane redove.** U našem modelu `ON DELETE CASCADE` uklanja članstva; u drugoj šemi FK može zabraniti brisanje ili primeniti drugačiju akciju.
4. **Brisanje članstva nije isto što i brisanje kontakta ili grupe.** Redovi u `contact_groups` predstavljaju veze, pa njihovo brisanje ostavlja entitete netaknutim.
5. **Provera pre brisanja je važna.** Prvo izvrši `SELECT` sa istim uslovom, a zatim proveri direktno i kaskadno obrisane redove pre `COMMIT`-a.

## Vežbe

U novoj `:memory:` bazi napravi šemu iz prethodne lekcije i unesi probne podatke:

1. Pre brisanja prikaži grupe i redove u `contact_groups`.
2. Ukloni vezu između Johnny-ja i grupe `Accounts`, koristeći obe kolone složenog ključa. Potvrdi da su grupa i kontakt i dalje prisutni.
3. Ponovo dodaj članstvo, a zatim obriši grupu `Accounts` po `id`-ju. Proveri kaskadno brisanje reda članstva i očuvanje kontakata.
4. Pokreni `SELECT changes();` odmah posle brisanja i uporedi direktno obrisane redove sa kaskadnim.
5. U transakciji obriši probnu grupu i uradi `ROLLBACK`. Potvrdi da su grupa i članstva vraćeni.
6. Izbriši grupu sa ID-jem koji ne postoji. Objasni zašto SQL može da uspe iako nije obrisao nijedan red.
7. U bezbednoj probnoj tabeli ispitaj šta radi `DELETE FROM table_name` bez `WHERE`. Ne izvršavaj ga nad važnim podacima.
8. Ponovi brisanje grupe i brisanje veze preko SQLAlchemy ORM-a; proveri da li su entiteti koji treba da ostanu sačuvani.

## Provera razumevanja

1. Koja je razlika između `DELETE FROM groups WHERE id = 2` i `DELETE FROM groups`?
2. Da li `DELETE FROM groups` uklanja tabelu ili samo njene redove?
3. Šta se u našem modelu dešava sa `contact_groups` redovima kada se obriše grupa?
4. Zašto se `PRAGMA foreign_keys` mora proveriti na svakoj SQLite konekciji?
5. Šta `changes()` broji, a šta ne broji kada se desi `ON DELETE CASCADE`?
6. Kako obrisati samo vezu kontakta i grupe, a ne sami kontakt ili grupu?
7. Kada treba završiti transakciju sa `COMMIT`, a kada sa `ROLLBACK`?
8. Koja je razlika između brisanja redova (`DELETE`) i brisanja šeme (`DROP TABLE`)?

## Izvori za dalje čitanje

- [SQLite: DELETE](https://www.sqlite.org/lang_delete.html)
- [SQLite: Foreign Key Support](https://www.sqlite.org/foreignkeys.html)
- [SQLite: Transactions](https://www.sqlite.org/lang_transaction.html)
- [SQLAlchemy 2.0: Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [SQLAlchemy 2.0: Basic Relationship Patterns — Many To Many](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many)
