# 05 — SQLite `UPDATE` naredba

## Cilj lekcije

`UPDATE` menja vrednosti u postojećim redovima. U ovoj lekciji promenićemo prezime kontakta u tabeli `contacts`, proveriti koji je red izmenjen i povezati SQL naredbu sa SQLAlchemy 2 ORM pristupom.

Radi u novoj, privremenoj bazi. `UPDATE` menja podatke; pogrešan uslov `WHERE` može izmeniti mnogo redova, pa pre svake promene proveri ciljane redove.

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

Očekivani rezultat je `1`. Za predvidive ID-jeve u nastavku, dodaj dva probna kontakta u praznu tabelu:

```sql
INSERT INTO contacts (first_name, last_name, email, phone)
VALUES
    ('Johnny', 'Cash', 'johnny.cash@example.test', '+12025550101'),
    ('Jane', 'Doe', 'jane.doe@example.test', '+12025550102');
```

U ovoj novoj tabeli Jane će dobiti `id = 2`. U već postojećoj bazi nemoj pretpostaviti vrednost ID-ja; prvo je pronađi pomoću `SELECT`-a.

## Osnovni oblik naredbe

```sql
UPDATE table_name
SET column_name = new_value
WHERE condition;
```

- `UPDATE` bira tabelu čije redove menjaš.
- `SET` navodi kolonu i izraz koji postaje njena nova vrednost.
- `WHERE` određuje koje redove treba menjati.

Za promenu prezimena Jane, prvo proveri njen red:

```sql
SELECT id, first_name, last_name, email
FROM contacts
WHERE id = 2;
```

Očekivani rezultat pre izmene je Jane Doe. Zatim izmeni samo prezime:

```sql
UPDATE contacts
SET last_name = 'Johnson'
WHERE id = 2;
```

Ponovo proveri red:

```sql
SELECT id, first_name, last_name, email
FROM contacts
WHERE id = 2;
```

Sada bi prezime trebalo da bude `Johnson`. `UPDATE` ne dodaje novi red; menja vrednost u postojećem.

## Zašto je `WHERE` važan?

`WHERE id = 2` ograničava promenu na red čiji je primarni ključ `2`. Pošto je `id` primarni ključ, najviše jedan red može odgovarati tom uslovu.

Ako izostaviš `WHERE`, promena će biti primenjena na **sve redove** u tabeli:

```sql
UPDATE contacts
SET last_name = 'Johnson';
```

Nemoj pokretati ovaj primer nad podacima koji treba da ostanu netaknuti. Uslov `WHERE` nije nužno jedinstven: na primer, `WHERE last_name = 'Doe'` može odgovarati većem broju kontakata. Ako nameravana promena treba da utiče na jedan red, koristi primarni ključ ili drugo jedinstveno ograničenje i prvo potvrdi rezultat pomoću `SELECT`-a.

`UPDATE` bez `WHERE` nije sintaksna greška i SQLite neće tražiti potvrdu. Odgovornost je na tebi da precizno ograničiš ciljane redove.

## Menjanje više kolona i više redova

U jednom `SET` delu možeš promeniti više kolona; razdvoji dodele zarezima:

```sql
UPDATE contacts
SET first_name = 'Jane',
    last_name = 'Johnson'
WHERE id = 2;
```

Ovo je zaseban primer istog obrasca. Ne moraš ponovo da ga pokreneš ako si već izmenio prezime u prethodnom primeru.

Uslov može namerno da odgovara većem broju redova. Na primer, kada je poslovno pravilo da se isti ispravljeni domen promeni kod svih kontakata koji ga koriste:

```sql
UPDATE contacts
SET email = replace(email, '@old.example', '@new.example')
WHERE email LIKE '%@old.example';
```

Pre takve grupne izmene pokreni `SELECT` sa istim `WHERE` uslovom i proveri tačno koliko i koje redove će obuhvatiti.

## Proveri broj izmenjenih redova

U SQLite CLI-ju, `changes()` vraća broj redova koje je izmenila poslednja `INSERT`, `UPDATE` ili `DELETE` naredba:

```sql
UPDATE contacts
SET last_name = 'Johnson'
WHERE id = 2;

SELECT changes();
```

Ako je ciljni red pronađen, očekuj jedan izmenjen red. Ako je rezultat `0`, proveri ID i uslov — moguće je da nijedan red nije odgovarao. U aplikaciji provera broja izmenjenih redova pomaže da se otkrije promena koja nije pogodila očekivani broj redova.

SQLite može da broji red koji je obuhvaćen naredbom čak i ako je nova vrednost ista kao stara. Zato `changes()` nije pouzdan način da utvrdiš da li se sadržaj vrednosti zaista razlikovao pre i posle `UPDATE`-a.

## Transakcija za pažljivu izmenu

Za važne promene možeš započeti transakciju, proveriti cilj, uraditi `UPDATE` i pročitati rezultat pre potvrde:

```sql
BEGIN;

SELECT id, first_name, last_name
FROM contacts
WHERE id = 2;

UPDATE contacts
SET last_name = 'Johnson'
WHERE id = 2;

SELECT changes();

SELECT id, first_name, last_name
FROM contacts
WHERE id = 2;
```

Ako je izmenjen očekivani red i rezultat je ispravan, potvrdi:

```sql
COMMIT;
```

Ako uslov nije obuhvatio očekivani red ili rezultat nije ispravan, poništi izmenu:

```sql
ROLLBACK;
```

`COMMIT` i `ROLLBACK` su alternative za završetak iste transakcije — ne izvršavaju se oba nakon istog `BEGIN`. Ako `UPDATE` odbije neko ograničenje, proveri stanje transakcije i uradi `ROLLBACK` pre nastavka. Transakcija je naročito važna kada jedna logička promena zahteva više SQL naredbi.

## Ograničenja važe i pri `UPDATE`-u

Ista pravila koja su važila pri `INSERT`-u proveravaju se i kada menjaš postojeći red. Na primer, email mora ostati jedinstven, a `NOT NULL` kolona ne može se postaviti na `NULL`. Ako promena prekrši `UNIQUE`, `CHECK`, `NOT NULL` ili aktivno strano ključno pravilo, SQLite vraća grešku i podrazumevano poništava tu `UPDATE` naredbu.

Probaj u probnoj bazi — ovaj upit treba da bude odbijen jer email već pripada drugom kontaktu:

```sql
UPDATE contacts
SET email = 'johnny.cash@example.test'
WHERE id = 2;
```

Ne uklanjaj ograničenje samo da bi upit prošao. Odluči šta konflikt znači u pravilima aplikacije i prikaži korisniku razumljiv ishod.

## Isti koncept u SQLAlchemy 2

Koristi `Contact`, `Group` i `engine` iz [prethodne SQLAlchemy mape](./03_sqlite_create_table_statement_part_2.md). Za izolovanu probu najpre unesi dva kontakta:

```python
from sqlalchemy.orm import Session


with Session(engine) as session, session.begin():
    session.add_all(
        [
            Contact(
                first_name="Johnny",
                last_name="Cash",
                email="johnny.cash@example.test",
                phone="+12025550101",
            ),
            Contact(
                first_name="Jane",
                last_name="Doe",
                email="jane.doe@example.test",
                phone="+12025550102",
            ),
        ]
    )
```

Zatim pronađi kontakt pomoću primarnog ključa i promeni njegov atribut:

```python
with Session(engine) as session, session.begin():
    jane = session.get(Contact, 2)
    if jane is None:
        raise LookupError("Kontakt sa id=2 ne postoji.")

    jane.last_name = "Johnson"
```

Kada se transakcioni blok uspešno završi, SQLAlchemy šalje `UPDATE` i potvrđuje promenu. Ako se dogodi izuzetak, `session.begin()` radi rollback; kontekst sesije je zatvara po završetku. `session.get()` vraća `None` ako kontakt ne postoji, zato primer to proverava umesto da tiho nastavi.

ORM promena atributa objekta nije posebna SQL sintaksa: SQLAlchemy je pretvara u parametrizovani `UPDATE`. Ne sastavljaj SQL pomoću f-string-a ili spajanja korisničkih vrednosti. Za direktne SQL izraze koristi parametre, a za ORM objekte dodeljuj vrednost atributu i upravljaj transakcijom.

## Šta je transkript pojednostavio — važne ispravke

1. **Ispravan oblik je `UPDATE table_name SET ... WHERE ...`; reč `TO` se ne piše posle `UPDATE`.**
2. **`WHERE` može da obuhvati više redova ili nijedan.** Za ciljanje jednog reda koristi primarni ključ ili drugo jedinstveno pravilo i proveri ga.
3. **Izraz posle `SET` je nova vrednost, ne nužno stara vrednost.** Može biti literal, `NULL` ili SQL izraz.
4. **Izostavljen `WHERE` menja sve redove.** SQLite ne traži dodatnu potvrdu, čak ni u produkcionoj bazi.
5. **Ažuriranje ne zaobilazi ograničenja.** Važeća vrednost pre izmene može postati nevažeća posle nje, pa se `UNIQUE`, `NOT NULL`, `CHECK` i FK pravila ponovo primenjuju.

## Vežbe

U novoj `:memory:` bazi napravi šemu iz prethodne lekcije i unesi probne kontakte:

1. Pre izmene prikaži red Jane Doe pomoću `SELECT`.
2. Promeni njeno prezime koristeći `WHERE id = 2`, pa ponovo prikaži red.
3. Pokreni `SELECT changes();` odmah posle izmene. Ponovi istu promenu i uporedi rezultat.
4. Promeni dve kolone jednim `UPDATE`-om, sa tačnim uslovom `WHERE`.
5. U transakciji promeni prezime, proveri rezultat, pa namerno uradi `ROLLBACK`. Potvrdi da se stara vrednost vratila.
6. Pokušaj da Jane postaviš email koji već koristi Johnny. Objasni dobijenu grešku i proveri da li su podaci ostali nepromenjeni.
7. U bezbednoj probnoj tabeli testiraj `UPDATE` bez `WHERE` i objasni zašto su se izmenili svi redovi. Ne radi to nad važnom bazom.
8. Ponovi promenu preko SQLAlchemy ORM-a i potvrdi rezultat u bazi ili ponovnim čitanjem objekta.

## Provera razumevanja

1. Koja je uloga `SET`, a koja `WHERE` dela?
2. Šta se dešava ako se `WHERE` izostavi?
3. Zašto je `WHERE id = 2` pouzdaniji za jedan red od `WHERE last_name = 'Doe'`?
4. Šta znači rezultat `0` od `SELECT changes();`?
5. Šta se dešava ako nova vrednost prekrši `UNIQUE` ograničenje?
6. Koja je razlika između `session.flush()` i uspešnog završetka transakcije?
7. Kada biraš `COMMIT`, a kada `ROLLBACK`?

## Izvori za dalje čitanje

- [SQLite: UPDATE](https://www.sqlite.org/lang_update.html)
- [SQLite: Transactions](https://www.sqlite.org/lang_transaction.html)
- [SQLAlchemy 2.0: Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [SQLAlchemy 2.0: ORM-enabled UPDATE statements](https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-update-and-delete)
