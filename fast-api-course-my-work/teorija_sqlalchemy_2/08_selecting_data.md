# Lekcija 08: SELECT i čitanje podataka

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 54:20–1:10:05
**Glavne teme:** tekstualni `SELECT`, Core `select()`, class-level ORM atributi, izbor kolona i tabela, kartezijanski proizvod, join preko FK metadata i kratki pregled subquery-ja.

Transkript pokriva praktičan SELECT nad unapred popunjenim `User` i `Address` tabelama. Cela izvorna skripta nije priložena, pa su primeri ispod rekonstrukcije SQLAlchemy 2.0. Složeni agregatni subquery iz predavanja je označen kao napredni pregled, ne kao potpuna lekcija o agregacijama.

## Dva načina da zatražimo SELECT

Ako znamo SQL koji želimo, možemo ga napisati tekstualno i obmotati sa `text()`:

```python
from sqlalchemy import text

statement = text("SELECT name FROM user_account")

with engine.connect() as connection:
	for row in connection.execute(statement):
		print(row.name)
```

To je potpuno validan način rada. `text()` je koristan kada želimo ručno da napišemo SQL, koristimo specifičnu SQL funkciju ili već imamo postojeći upit. Ako dodajemo vrednosti iz programa, koristimo bind parametre, ne f-string konkatenaciju:

```python
statement = text("SELECT name FROM user_account WHERE name = :name")

with engine.connect() as connection:
	row = connection.execute(statement, {"name": "spongebob"}).first()
```

SQLAlchemy Core nudi i Python API za sastavljanje SQL izraza. Za SELECT koristimo `select()`:

```python
from sqlalchemy import select

statement = select(User.name)
```

Ovaj izraz predstavlja zahtev da se izabere kolona `name` iz tabele koja pripada `User`. Kada se kompajlira za SQLite, približan SQL je:

```sql
SELECT user_account.name
FROM user_account
```

`select(...)` samo konstruiše SQLAlchemy iskaz. Ne otvara konekciju i ne čita bazu dok ga ne izvršimo, na primer sa `connection.execute(statement)`.

## Zašto `User.name` predstavlja SQL kolonu?

U deklarativnom ORM modelu isti naziv se koristi za dva različita Python izraza:

```python
user.name   # vrednost atributa na jednoj instanci, npr. "spongebob"
User.name   # class-level SQLAlchemy atribut, kojim gradimo SQL iskaz
```

Kada model definiše:

```python
class User(Base):
	__tablename__ = "user_account"

	name: Mapped[str] = mapped_column(String(30))
```

SQLAlchemy ne ostavlja `User.name` kao običan atribut klase. Atribut je instrumentisan kao SQLAlchemy descriptor. To mu omogućava da ima ponašanje prilagođeno kontekstu:

- `user.name` na Python objektu daje trenutnu Python vrednost;
- `User.name` na klasi predstavlja mapiranu kolonu i može da učestvuje u SQL izrazima;
- kada promenimo `user.name`, ORM može da prati izmenu objekta.

Zato ovaj izraz ne proverava Python vrednost jednog objekta:

```python
User.name == "spongebob"
```

On pravi SQLAlchemy uslov koji odgovara SQL-u `user_account.name = ...`. Vrednost `"spongebob"` postaje bind parametar; SQLAlchemy je prosleđuje odvojeno od SQL strukture.

Poređenje sa Python vrednošću instance bilo bi drugačije:

```python
user.name == "spongebob"
```

Ovo poredi vrednost već učitanog Python objekta i rezultat je Python `bool`. Nasuprot tome, `User.name == "spongebob"` koristi atribut klase i gradi SQLAlchemy izraz za `WHERE` uslov.

## Izbor jednog entiteta ili više kolona

Argumenti koje damo u `select()` određuju šta želimo da dobijemo:

```python
select(User)                         # ORM entitet / sve mapirane kolone
select(User.id, User.name)           # dve izabrane kolone
select(User.fullname, User.name)     # kolone tačno ovim redosledom
select(User.name)                    # jedna kolona
```

Kolone u rezultatu prate redosled kojim su navedene u `select()`. U primeru `select(User.fullname, User.name)`, `row[0]` je `fullname`, a `row[1]` je `name`. Imena kolona dostupna su i preko `Row` interfejsa:

```python
with engine.connect() as connection:
	row = connection.execute(
		select(User.fullname, User.name)
	).first()

	if row is not None:
		print(row.fullname, row.name)
```

Ako želimo samo jednu Python vrednost po redu, možemo koristiti `scalars()`:

```python
with engine.connect() as connection:
	names = connection.execute(select(User.name)).scalars().all()
```

Ovde `scalars()` uzima prvu izabranu kolonu svakog reda; `.all()` zatim pravi listu. `select(User.name)` daje skalarne vrednosti poput stringova, dok `select(User.id, User.name)` bez `scalars()` daje redove sa dve vrednosti.

### `select(User)` preko `Connection`-a i preko `Session`-a

Sintaksa iskaza može biti ORM-orijentisana, ali objekat koji dobijemo zavisi i od toga preko čega ga izvršimo:

```python
statement = select(User)

with engine.connect() as connection:
	row = connection.execute(statement).first()
	# Core Connection: rezultat je Row sa vrednostima kolona.

with Session(engine) as session:
	users = session.scalars(statement).all()
	# ORM Session: rezultat su User instance.
```

`Connection` izvršava iskaz u Core stilu. Iako `select(User)` bira sve kolone ORM entiteta, `connection.execute(...)` ne pravi automatski ORM `User` objekte; dobija se `Row` sa izabranim vrednostima. `Session` koristi ORM mapiranje i `session.scalars(select(User))` vraća `User` instance.

Ovo je razlog što predavanje može da koristi ORM modele da bi lakše sastavilo Core SQL, a da i dalje dobija obične redove preko `Connection`-a. ORM klasa kao izvor informacija za kolonu ne znači da je ceo izvršni put ORM `Session`.

## Kako se određuje `FROM`?

U SQL tekstu moramo navesti izvor kolone, na primer:

```sql
SELECT name FROM user_account
```

U Core iskazu `select(User.name)` SQLAlchemy već zna kojoj tabeli pripada class-level atribut `User.name`. Zato može da izvede `FROM user_account` bez posebnog stringa ili `select_from(User)` poziva.

Ovo nije nagađanje: izvor tabele je sadržan u mapiranom atributu koji smo prosledili u `select()`. Možemo i eksplicitno zadati `FROM` kada to čini iskaz jasnijim ili kada izraz sam ne određuje sve izvore:

```python
statement = select(User.name).select_from(User)
```

U jednostavnom primeru je to suvišno, jer `User.name` već nosi informaciju o tabeli. Predavač ovu redukciju ponavljanja naziva automatizacijom, ne skrivanjem SQL namere.

## Više kolona iz iste tabele

Ako izaberemo dve kolone koje pripadaju istoj tabeli:

```python
statement = select(User.name, User.fullname)
```

SQLAlchemy izvede jedan `FROM user_account`, a rezultat ima dve kolone po redu, redom `name`, pa `fullname`. Svaki rezultat je i dalje običan `Row` kada iskaz izvršimo preko `Connection`-a.

## Više tabela ne znači automatski JOIN

Pogledajmo izraz:

```python
statement = select(User.name, Address.email_address)
```

`User.name` pripada tabeli `user_account`, a `Address.email_address` tabeli `address`. SQLAlchemy zato uključuje obe tabele u `FROM`. Ako ne zadamo kako ih povezati, SQL semantika je kartezijanski proizvod, približno:

```sql
SELECT user_account.name, address.email_address
FROM user_account, address
```

To uparuje svaki `User` red sa svakim `Address` redom. Ako tabela `user_account` ima $m$ redova, a `address` ima $n$ redova, rezultat može imati $m \times n$ parova.

Na primer, tri korisnika i četiri adrese bez uslova spajanja daju do 12 kombinacija. One ne znače da svaki korisnik zaista poseduje svaku adresu; to su sve moguće kombinacije redova. Na velikim tabelama ovakav upit može stvoriti ogroman rezultat i opteretiti bazu i aplikaciju.

Kartezijanski proizvod ponekad je nameran, ali kod običnog upita nad povezanim tabelama obično nedostaje JOIN uslov. Važno: prisustvo FK metadata-e samo po sebi ne pretvara `select(User.name, Address.email_address)` u JOIN. FK omogućava inferenciju kada zatražimo JOIN.

## JOIN preko FK metadata-e

`Address.user_id` je deklarisan sa:

```python
user_id: Mapped[int] = mapped_column(
	ForeignKey("user_account.id"),
	nullable=False,
)
```

SQLAlchemy metadata-e zato zna da `address.user_id` referencira `user_account.id`. Možemo zatražiti INNER JOIN ovako:

```python
statement = (
	select(User.name, Address.email_address)
	.join_from(User, Address)
)
```

SQLAlchemy može da izvede `ON` uslov iz FK metadata-e:

```sql
SELECT user_account.name, address.email_address
FROM user_account
JOIN address ON user_account.id = address.user_id
```

Ovo nije isto što i kartezijanski proizvod: `ON` uslov zadržava parove kod kojih je adresa vezana baš za tog korisnika. Podrazumevani JOIN je INNER JOIN, pa korisnik bez adrese neće biti prikazan u rezultatu.

Za upit sa eksplicitnim poređenjem možemo da navedemo `ON` uslov sami:

```python
statement = select(User.name, Address.email_address).join_from(
	User,
	Address,
	User.id == Address.user_id,
)
```

Ovo je korisno kada nema FK metadata-e, kada postoji više mogućih FK puteva ili kada želimo precizno da navedemo uslov. SQLAlchemy može automatski da izvede `ON` samo kada je veza iz metadata-e nedvosmislena. Ako postoje više kandidata ili nijedan, treba navesti uslov umesto očekivati da SQLAlchemy pogodi.

### Šta `join_from()` naglašava?

`join_from(leva_strana, desna_strana)` eksplicitno kaže odakle počinje JOIN i na šta prelazi. U ovoj lekciji modeli imaju `ForeignKey`, ali još nemaju ORM `relationship()` navigaciju.

U drugim primerima postoji i `Select.join()`. On dodaje JOIN postojećem SELECT iskazu, a može da koristi FK metadata-u ili ORM `relationship()` atribut ako ga navedemo. `join_from()` je posebno čitljiv kada hoćemo da jasno zadamo levu stranu; nijedan od ta dva API-ja ne uklanja potrebu da razumemo SQL JOIN.

`ForeignKey` metadata i fizički FK constraint su povezani, ali nisu identična runtime garancija. SQLAlchemy može koristiti FK deklaraciju u Python metadata-i da sastavi JOIN, čak i pre izvršavanja DDL-a. Da li baza fizički sprovodi constraint zavisi od toga da li je constraint u njenoj šemi i od podešavanja baze, kao što smo videli kod SQLite-a.

## JOIN rezultati i demo podaci

Kada SELECT uključi ime i email adresu, rezultat ima po jedan red za svaku korisničku adresu:

```python
statement = (
	select(User.name, User.fullname, Address.email_address)
	.join_from(User, Address)
)

with engine.connect() as connection:
	for row in connection.execute(statement):
		print(row.name, row.fullname, row.email_address)
```

Ako jedan korisnik ima dve adrese, INNER JOIN vraća dva reda za tog korisnika, po jedan za svaku povezanu adresu. To nije dupliranje greškom: svaki red predstavlja par korisnik–adresa. Predavač koristi demonstracione likove: SpongeBob ima jednu adresu, Sandy dve, a Patrick jednu.

Ovaj JOIN ne koristi `relationship()`; veza dolazi iz FK metadata-e. Kada kasnije uvedemo ORM relacije, biće moguće sastaviti i izraze preko ORM navigacionih atributa, ali to je dodatni sloj iznad ovog SQL JOIN-a.

## Napredni pregled: agregatni subquery

Predavač kratko prikaže složeniji primer: pronaći korisnike koji imaju više od jedne email adrese. Primer koristi `GROUP BY`, `COUNT`, `HAVING`, subquery i JOIN. To je preview kompozicije SELECT iskaza, a ne potpuna lekcija o agregatima.

```python
from sqlalchemy import func, select

address_counts = (
	select(
		Address.user_id,
		func.count(Address.id).label("address_count"),
	)
	.group_by(Address.user_id)
	.having(func.count(Address.id) > 1)
	.subquery()
)

statement = (
	select(User.name, address_counts.c.address_count)
	.join_from(User, address_counts)
)
```

Razlaganje:

1. Unutrašnji `select()` bira korisnički ID iz adresa i broj adresa.
2. `group_by(Address.user_id)` pravi jednu grupu po korisniku.
3. `having(count(...) > 1)` zadržava samo grupe sa više od jedne adrese.
4. `.subquery()` pretvara taj SELECT u tabeli sličan izvor pod imenom `address_counts`.
5. `address_counts.c.address_count` pristupa koloni subquery-ja; `.c` je kolekcija njegovih kolona.
6. Spoljašnji SELECT spaja korisnike sa agregatnim rezultatom i bira korisničko ime i broj adresa.

U dostavljenom skupu podataka rezultat je Sandy sa brojem 2. SQLAlchemy može da izvede JOIN uslov preko linije porekla `Address.user_id` u subquery-ju. Ako bi metadata dopuštala više podjednako mogućih uslova spajanja, iskaz bi postao dvosmislen i trebalo bi navesti eksplicitni `ON` uslov.

Subquery je SQL struktura, ne privremena Python lista i ne nužno fizička tabela. Baza izvršava sastavljeni SELECT kao jedan upit. Za sada je dovoljno razumeti da SQLAlchemy omogućava građenje složenog upita iz manjih SQL izraza bez ručnog kopiranja čitavog SQL teksta.

## Tekstualni SQL i Core izraz

Oba sledeća iskaza mogu vratiti imena korisnika:

```python
text_statement = text("SELECT name FROM user_account")
core_statement = select(User.name)
```

- `text()` je koristan kada želimo doslovno da napišemo SQL.
- `select(User.name)` gradi SQL izraz kroz tipizovani mapirani atribut.
- Oba se mogu izvršiti preko `Connection`-a i vratiti Core `Row` rezultate.
- Core izraz zna da `User.name` potiče iz `user_account`, zna njegov SQLAlchemy tip i može da doprinese izvođenju `FROM` klauzule.

Predavačeva poenta nije da SQL treba zaboraviti. Treba znati kakav SQL želimo, a zatim odlučiti da li je korisnije napisati ga tekstualno ili sastaviti kao Core izraz. SQLAlchemy automatizuje ponavljajuće delove, ali ne sakriva da radimo SELECT ili JOIN.

## Redosled rezultata

Bez `ORDER BY` baza ne garantuje redosled redova, čak i ako test trenutno vraća redove po ID-ju. Kada rezultat treba da ima stabilan redosled, zadaj ga u upitu:

```python
statement = select(User.name).order_by(User.id)
```

Ovo je osnovna napomena za pouzdane primere i testove; detaljnije `ORDER BY` i sortiranje pripadaju narednim lekcijama.

## Sažetak za ponavljanje

- `text("SELECT ...")` izvršava SQL koji smo ručno napisali; `select(...)` gradi SQL izraz kroz Python objekte.
- `select(User.name)` bira jednu kolonu, a SQLAlchemy iz atributa izvodi tabelu `user_account` za `FROM`.
- `User.name` na klasi je SQLAlchemy descriptor; `user.name` na instanci je Python vrednost.
- Redosled izabranih kolona određuje redosled vrednosti u svakom `Row`-u.
- `Connection.execute(select(User))` vraća Core red sa vrednostima; ORM instance dobijamo, na primer, kroz `Session.scalars(select(User))`.
- Izbor kolona iz više tabela sam po sebi dodaje izvore u `FROM`, ali ne pravi JOIN; bez uslova dobija se kartezijanski proizvod.
- `join_from(User, Address)` traži JOIN; FK metadata može da obezbedi nedvosmislen `ON` uslov.
- FK metadata može da omogući SQLAlchemy-ju da sastavi JOIN, ali to nije isto što i garantovano fizičko FK enforcement u bazi.
- Subquery je SELECT ugrađen kao izvor drugog SELECT-a; `.c` pristupa njegovim kolonama.
- Za pouzdan redosled rezultata koristi `ORDER BY`; baza bez njega ne obećava redosled.

## Vežbe za playground

Koristi postojeće `User` i `Address` modele i root `.venv`.

1. Pokreni `text("SELECT name FROM user_account")` i `select(User.name)` preko `Connection`; uporedi ispisani SQL i rezultate.
2. Probaj `select(User)`, `select(User.id, User.name)` i `select(User.fullname, User.name)`. Zabeleži oblik svakog `Row`-a.
3. Izvrši `select(User)` preko `Connection`, pa `session.scalars(select(User))` preko `Session`; proveri tip vrednosti koju dobijaš.
4. Kompajliraj `select(User.name, Address.email_address)` bez JOIN-a i objasni `FROM` izvore. Izbegavaj izvršavanje nad velikim tabelama dok ne dodaš uslov spajanja.
5. Dodaj `.join_from(User, Address)` i pregledaj izvedeni `ON user_account.id = address.user_id`.
6. Navedi `User.id == Address.user_id` kao eksplicitni `ON` uslov i uporedi iskaz.
7. Napravi agregatni subquery koji broji adrese po korisniku i vrati samo one sa više od jedne adrese.
8. Ukloni `ORDER BY` i nemoj pretpostavljati da je redosled koji trenutno vidiš garantovan.
