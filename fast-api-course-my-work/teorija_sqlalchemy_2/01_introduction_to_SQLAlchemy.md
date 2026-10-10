# Lekcija 01: Uvod u SQLAlchemy

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 0:04–4:46
**Napomena o obimu:** Ovaj deo je uvod u alat i strukturu predavanja. Još nema konkretnog programskog primera; tema `Engine` je samo najavljena na kraju.

## Cilj uvoda

Najvažnija poruka nije da je SQLAlchemy „biblioteka za ORM“, nego da je **alatni komplet za rad sa relacionim bazama**. ORM je jedan njegov deo. Možemo da koristimo `SQLAlchemy Core` za `konekcije`, `SQL upite` i `upravljanje šemom` i `bez mapiranja` Python klasa na tabele.

Predavanje zatim postavlja širu putanju učenja: prvo `osnove povezivanja` i `transakcija`, zatim `opis šeme` i `sastavljanje SQL upita`, pa tek onda `ORM obrasci za čuvanje i učitavanje Python objekata`.

---

## Šta SQLAlchemy obuhvata?

U uvodu se pominje nekoliko sposobnosti koje zajedno čine SQLAlchemy:

| Oblast                    | Šta rešava                                                                   | Primer pojma koji ćemo kasnije sresti |
| ------------------------- | ---------------------------------------------------------------------------- | ------------------------------------- |
| Rad sa DBAPI drajverom    | Pruža bogatiji i ujednačeniji sloj iznad Python interfejsa za drajvere baza. | `Engine`, `Connection`, transakcije   |
| Opis šeme                 | Opisuje tabele, kolone, tipove i ograničenja; može da generiše DDL za šemu.  | `MetaData`, `Table`, `Column`         |
| Izgradnja SQL upita       | Gradi SQL iskaze pomoću Python objekata i izraza.                            | `select()`, `insert()`, `where()`     |
| Inspekcija postojeće baze | Čita strukturu baze koja već postoji.                                        | tabele, kolone, tipovi, ograničenja   |
| ORM                       | Povezuje Python klase i objekte sa relacionim podacima.                      | deklarativni modeli, `Session`, veze  |

Ovo su povezani slojevi, ali nisu ista stvar. Na primer, `ORM` ne zamenjuje samu bazu niti ukida SQL; `ORM` koristi `SQLAlchemy Core` da bi sastavio i izvršio `SQL` potreban za rad sa mapiranim objektima.

---

## DBAPI i SQLAlchemy

**DBAPI** je uobičajeni naziv za `Python Database API`, definisan specifikacijom `PEP 249`. Specifikacija opisuje zajednički skup metoda i atributa (`connection`, `cursor`, `execute`, `fetch`) kojim Python programi pristupaju drajverima baza. Konkretan drajver (`sqlite3`, `psycopg2`, itd.) zatim `komunicira sa određenom bazom`, na primer `SQLite`-om ili `PostgreSQL`-om.

`SQLAlchemy` sedi iznad `drajvera`. Njegov `dijalekt` poznaje razlike u SQL sintaksi i tipovima određene baze, a `Engine` obezbeđuje SQLAlchemy-jevu ulaznu tačku za izvršavanje. Zato aplikacioni kod može da koristi dosledniji skup SQLAlchemy API-ja, dok `dijalekt` i `drajver` obavljaju posao `prilagođavanja` i `komunikacije`.

To ne znači da SQLAlchemy može da sakrije sve razlike između baza. Razlike u tipovima, ograničenjima, transakcijama i funkcijama baze i dalje mogu biti važne. SQLAlchemy olakšava rad sa njima; ne čini različite baze potpuno identičnim.

---

## Core i ORM

SQLAlchemy se često objašnjava kroz dva velika dela:

- **Core** je temeljni sloj za `konekcije`, `šemu` i `SQL izraze`. Njime radimo sa `objektima` koji predstavljaju `tabele` i `SQL iskaze`, čak i ako `nemamo` ORM klase.
- **ORM** je viši sloj koji `mapira` Python klase na tabele i Python objekte na redove. `ORM` je izgrađen na `Core`-u i koristi njegove mehanizme za izvršavanje upita.

`Core` nije samo „sirovi SQL“, a `ORM` nije „baza bez SQL-a“. U `Core`-u možemo `SQL` da gradimo kompoziciono, kroz Python objekte. `ORM` nam omogućava da radimo preko mapiranih klasa, ali ispod toga i dalje postoje `SQL iskazi`, `konekcije` i `transakcije` koje su deo `Core` sloja.

U `SQLAlchemy`-ju 2.0 ova veza je naročito vidljiva u obrascu za upite: funkcija `select()` služi kao osnova za izgradnju iskaza, a način izvršavanja određuje da li dobijamo obične rezultate iz `Core` konekcije ili `ORM` objekte kroz `Session`.

### Pojednostavljen tok

```text
Python kod
	-> gradi SQLAlchemy iskaz (Core; ORM upiti se oslanjaju na Core)
	-> Connection (Core) ili Session (ORM) traži izvršavanje iskaza
	-> Engine obezbeđuje konekciju iz pool-a, a dijalekt prilagođava SQL i parametre bazi
	-> Connection poziva DBAPI drajver, koji izvršava SQL nad bazom
	<- rezultat se vraća iz baze DBAPI drajveru, a zatim SQLAlchemy-ju
	-> Core izlaže Result/Row sa Python vrednostima
	-> ORM Session, kada se biraju ORM entiteti, mapira redove u ORM instance
```

Ovo je mapa pojmova, ne detaljan redosled poziva. `Engine` upravlja pool-om i daje SQLAlchemy `Connection`; dijalekt kompajlira iskaz za ciljnu bazu, a DBAPI drajver obavlja poziv prema njoj. Rezultat ne ide „nazad u Engine“: baza ga vraća drajveru, a drajver ga predaje SQLAlchemy-ju. Core rezultat je `Result`/`Row` sa Python vrednostima; ORM `Session` dodatno može da napravi ili pronađe mapirane instance u identity map-u.

Kod SQLite-a `sqlite3` obično pristupa ugrađenoj bazi u procesu, pa nema zasebnog serverskog procesa. Kod PostgreSQL-a drajver, na primer `psycopg`, komunicira sa odvojenim serverom baze.

Sledeće lekcije razlažu `Engine`, konekcije (`Connection`) i izvršavanje (`execute()`) korak po korak.

---

## Zašto je poznavanje SQL-a važno?

Predavač preporučuje osnovno poznavanje SQL-a: `SELECT`, `INSERT` i pravljenja tabele. Razlog je što SQLAlchemy uglavnom automatizuje i strukturira rad sa SQL-om, ali ne menja relacionu logiku koja stoji iza njega.

Kada ORM upit ne vrati ono što očekujemo, korisno je umeti da razmišljamo o ekvivalentnom SQL-u: koje tabele se čitaju, koji uslov filtrira redove i koje kolone se vraćaju. Isto tako, razumevanje `INSERT`-a i ograničenja pomaže da se protumači zašto baza odbija upis.

Predavač pominje i transakcije kao korisno predznanje. **Transakcija** grupiše rad sa bazom tako da aplikacija može promene da potvrdi (`COMMIT`) ili poništi (`ROLLBACK`). To je važno jer SQLAlchemy upravlja izvršavanjem upita u kontekstu transakcija; transakcija nije samo još jedna sintaksa za INSERT.

---

## Predznanje za praćenje kursa

Prema predavanju, korisno je imati:

- osnovno iskustvo sa Python programiranjem;
- osnovno razumevanje klasa i instanci;
- početno poznavanje SQL-a: `SELECT`, `INSERT` i `CREATE TABLE`;
- makar početnu predstavu o tome šta je transakcija.

Nije potrebno unapred biti ekspert za ORM. Ipak, ako su SQL tabele i upiti potpuno novi pojmovi, vredi prvo utvrditi te osnove; SQLAlchemy ih koristi, ne zamenjuje ih.

---

## Struktura predavanja

Predavač kaže da izvorni materijal ima šest modula, ali da će na vremenski ograničenom predavanju proći većinu od prvih pet. Šesti modul obrađuje ORM veze, temu koja je dovoljno velika za zasebnu lekciju; izvorni GitHub materijal sadrži i taj modul.

Uvod najavljuje ovaj tok:

1. povezivanje sa bazom i transakcije;
2. opis tabela i metadata;
3. izgradnja SQL upita;
4. ORM obrasci za trajno čuvanje podataka;
5. ORM veze kao zasebna, šira tema u dodatnom modulu.

Zato nemoj očekivati da se sve o `relationship()` nauči iz uvodnog dela ili nužno iz vremenski ograničenog predavanja. Ako u transkriptu neke lekcije nedostaje konkretan primer ili objašnjenje sa slajda, možemo ga dopuniti kada pošalješ odgovarajući izvorni kod ili naredni deo materijala.

---

## Dokumentacija koju predavanje preporučuje

Predavač izdvaja tri mesta u zvaničnoj SQLAlchemy dokumentaciji:

- [SQLAlchemy 2.0 dokumentacija](https://docs.sqlalchemy.org/en/20/)
- [Unified Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html), duži vodič koji povezuje osnovne koncepte;
- [ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html), kratak prikaz tipičnog ORM toka;
- [ORM Querying Guide](https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html), vodič za upite ORM stilom u verziji 2.0.

Za ovaj kurs treba čitati dokumentaciju za SQLAlchemy 2.0, a ne nasumične primere za 1.x. Stari primeri mogu da koriste obrasce koji su i dalje dostupni zbog kompatibilnosti, ali više nisu preporučeni kao novi 2.0 stil.

---

## Dopuna iz slajdova: `Engine` i prva konekcija

Dostavljeni transkript samo najavljuje `Engine`, ali priloženi kursni slajdovi `01_engine_usage.py` odmah nastavljaju praktičnim primerom. Ovaj odeljak je dopuna iz slajdova, ne sadržaj izgovoren u uvodnom transkriptu.

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite://", echo=True)
```

`create_engine()` pravi SQLAlchemy `Engine`, ali obično ne otvara DBAPI konekciju odmah. `Engine` je dugotrajan objekat koji sadrži podešavanja dijalekta i drajvera i upravlja pool-om. Stvarna konekcija se uzima kada je prvi put zatražimo ili izvršimo SQL.

- `sqlite://` pravi SQLite bazu u memoriji, vezanu za konekciju;
- `sqlite:///ime_datoteke.db` koristi SQLite bazu u datoteci;
- URL za PostgreSQL ili MySQL dodatno navodi drajver, host, korisnika, lozinku i ime baze.

Uobičajeno je da aplikacija deli jedan `Engine`, a da svaka operacija privremeno uzme konekciju iz njegovog pool-a. Ne pravimo novi `Engine` za svaki upit.

---

### `Engine`, SQLAlchemy `Connection` i DBAPI konekcija

Kada direktno radimo sa Core-om, konekciju uzimamo preko `engine.connect()`:

```python
with engine.connect() as connection:
	...
```

`connection` je SQLAlchemy `Connection`. Dok je iznajmljena, ona koristi konkretnu DBAPI konekciju, na primer Pythonov `sqlite3` objekat za SQLite. SQLAlchemy `Connection` je sloj iznad drajvera; u običnom kodu radimo sa njim, a ne direktno sa internim DBAPI objektom.

Kursni slajd demonstrira uvid u objekat drajvera ovako:

```python
driver_connection = connection.connection.driver_connection
```

Ovo je korisno za učenje šta se nalazi ispod SQLAlchemy sloja, ali nije uobičajen način izvršavanja upita: direktan rad sa DBAPI objektom vezuje kod za konkretan drajver.

Kada se `Connection` zatvori, DBAPI konekcija se obično vraća u pool da bi mogla ponovo da se koristi; pool može i da je fizički zatvori, zavisno od podešavanja. Zato se preporučuje `with engine.connect()` umesto ručnog otvaranja resursa bez jasno određenog mesta zatvaranja.

---

### Tekstualni upit i `Result`

SQLAlchemy Core može da izvrši tekstualni SQL preko `text()`:

```python
from sqlalchemy import text

statement = text("SELECT 'hello world' AS greeting")

with engine.connect() as connection:
	result = connection.execute(statement)
	row = result.first()

	assert row is not None
	print(row.greeting)
```

`text()` pravi SQLAlchemy iskaz od SQL teksta. `Connection.execute()` ga izvršava i vraća `Result` objekat; za ovakav upit rezultat je obično `CursorResult`.

Red `Row` se ponaša slično imenovanom tuple-u:

```python
row[0]
row.greeting
row._mapping["greeting"]
```

`row._mapping` daje pristup mapiranju po imenima kolona. `Row` nije običan `dict`; za dinamičko ime kolone koristi se upravo `_mapping`.

Važno: `Result.first()` uzima prvi red ili vraća `None`, a zatim zatvara result set/kursor. Ako su potrebni drugi načini čitanja, izvrši iskaz ponovo umesto da nastaviš da koristiš isti rezultat:

```python
with engine.connect() as connection:
	first_row = connection.execute(statement).first()
	all_rows = connection.execute(statement).all()
```

Ovo je razlog za grešku `ResourceClosedError` ako se ceo izvorni `01_engine_usage.py` pokrene kao obična Python skripta: posle primera sa `.first()` isti `result` se koristi u kasnijim primerima. Slajdovi su namenjeni `sliderepl`-u; samostalna playground verzija koristi novi `execute()` za svaku demonstraciju.

---

### Iteracija, `all()` i `scalars()`

Za više redova možemo da iteriramo kroz `Result`:

```python
statement = text(
	"SELECT 1 AS item_id, 'hello' AS greeting "
	"UNION ALL SELECT 2, 'SQLAlchemy'"
)

with engine.connect() as connection:
	for item_id, greeting in connection.execute(statement):
		print(item_id, greeting)
```

`result.all()` potroši rezultat i vrati listu `Row` objekata. `result.scalars()` pravi rezultat koji za svaki red daje samo prvu izabranu kolonu; nije ograničen na jedan red:

```python
with engine.connect() as connection:
	item_ids = connection.execute(statement).scalars().all()
	assert item_ids == [1, 2]
```

Ako želiš stringove pozdrava umesto ID-jeva, sastavi iskaz koji bira `greeting` kao prvu kolonu. Za velike rezultate iteracija obično izbegava pravljenje dodatne Python liste; `.all()` je praktičan kada je rezultat mali.

`echo=True` u `create_engine()` prikazuje SQL, parametre i transakcijske poruke u logu. To je zgodno za učenje i debagovanje, ali log može da sadrži i podatke koji ne bi trebalo da procure.

Detaljne transakcijske obrasce, `commit()` i `rollback()` obrađuju naredne lekcije. Za kompletnu ispravljenu vežbu pogledaj [01_engine_usage.py](../playground/sqlalchemy_2/01_engine_usage.py); dopuna o Core tabeli i `MetaData` je u [02_metadata.py](../playground/sqlalchemy_2/02_metadata.py) i u [lekciji 04](04_table_metadata_model.md).

---

## Verzijski okvir

Ovo je predavanje o SQLAlchemy-ju 2.0 iz 2023. godine. Playground u ovom repozitorijumu koristi SQLAlchemy `2.0.38`, pa buduće primere proveravamo u toj verziji.

Glavna praktična posledica za početak je da pratimo savremeni 2.0 stil, naročito `select()` za upite. Ako naiđemo na stariji obrazac, objasnićemo da li je samo drugačiji stil, kompatibilni legacy API ili ponašanje koje se promenilo.

---

## Sažetak za ponavljanje

- SQLAlchemy je alatni komplet za baze; ORM je samo jedan njegov deo.
- Core pruža temelj za konekcije, šemu i SQL izraze; ORM je sloj iznad njega.
- SQLAlchemy koristi DBAPI drajver, ali mu dodaje dijalekt, izvršavanje i druge alate.
- Python izrazi mogu da predstavljaju SQL iskaze; ne izvršavaju se kao obična Python logika nad celom bazom.
- Osnovni SQL i transakcije pomažu da se razume šta SQLAlchemy radi.
- Ovaj transkript je uvod i najava `Engine`-a; u njemu još nema konkretnog modela ni programskog primera.

---

## Dodatak: Core i ORM upit u SQLAlchemy 2.0

**Ovaj primer nije prikazan u dostavljenom transkriptu.** Služi samo da konkretnije prikaže razliku koju predavanje najavljuje. Oba iskaza ispod su SQLAlchemy izrazi; razlikuju se po tome da li su polja opisana kroz Core `Table` ili ORM klasu.

```python
from sqlalchemy import Column, Integer, MetaData, String, Table, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Core opis tabele
metadata = MetaData()
autori_tabela = Table(
	"autori_core",
	metadata,
	Column("id", Integer, primary_key=True),
	Column("ime", String(100), nullable=False),
)

core_iskaz = select(autori_tabela.c.ime).where(
	autori_tabela.c.ime == "Pera"
)


# ORM opis tabele
class Base(DeclarativeBase):
	pass


class Autor(Base):
	__tablename__ = "autori_orm"

	id: Mapped[int] = mapped_column(primary_key=True)
	ime: Mapped[str] = mapped_column(String(100), nullable=False)


orm_iskaz = select(Autor).where(Autor.ime == "Pera")
```

### Kako čitati primer

- `autori_tabela.c.ime` označava kolonu `ime` u Core objektu tabele. `.c` je kolekcija kolona te tabele.
- `Autor.ime` označava mapirani ORM atribut klase `Autor`.
- `select(...)` gradi objekat koji predstavlja upit; linija koja ga napravi sama po sebi još ne šalje upit bazi.
- `.where(...)` dodaje uslov. SQLAlchemy vrednost `"Pera"` tretira kao bind parametar, umesto da je nebezbedno spaja u SQL tekst.
- `core_iskaz` bira vrednost kolone. Izvršavanje preko `Connection`-a daje rezultat na nivou kolona/redova.
- `orm_iskaz` bira ORM entitet `Autor`. Izvršavanje preko `Session`-a može da vrati `Autor` Python objekte.

Važan 2.0 obrazac je da je `select()` zajednički način izgradnje upita; Core ili ORM ponašanje proizlazi iz toga šta se bira i da li se iskaz izvršava preko `Connection`-a ili ORM `Session`-a. Kasnije ćemo ove iskaze zaista izvršiti i pratiti SQL koji baza dobija.

---
