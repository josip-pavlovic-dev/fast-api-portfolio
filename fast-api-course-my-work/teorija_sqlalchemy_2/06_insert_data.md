# Lekcija 06: INSERT i prvi podaci

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 40:05–47:08
**Glavne teme:** server-side `created_at`, `func.now()`, SQLAlchemy Core `insert()` nad ORM entitetom, `.values()` i bind parametri.

Transkript se završava u trenutku kada predavač počinje da izvršava INSERT. Zato su model i konstrukcija iskaza ispod rekonstrukcija slajda, dok su izvršavanje, čitanje upisanog reda i objašnjenja ponašanja baze jasno označeni kao dopuna.

## Od praznih tabela do INSERT-a

Prethodne lekcije su uspostavile sledeći lanac:

1. Python deklaracija opisuje tabele u `Base.metadata`.
2. `Base.metadata.create_all(...)` šalje DDL i pravi tabele koje nedostaju.
3. Tabela postoji u bazi, ali je i dalje prazna.
4. `insert()` gradi SQL iskaz kojim tražimo da baza doda red.
5. `Connection.execute()` izvršava iskaz, a transakcija se zatim potvrđuje.

`insert()` odgovara SQL operaciji `INSERT`. On najpre napravi SQLAlchemy iskaz; sam poziv `insert(...)` ili `.values(...)` još ne šalje SQL bazi.

## Model iz predavanja: timestamp sa strane baze

U prethodnoj lekciji `created_at` je koristio Python dataclass `default_factory`. Predavač ga sada menja u `server_default=func.now()` i isključuje polje iz dataclass konstruktora:

```python
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
	pass


class User(Base):
	__tablename__ = "user_account"

	id: Mapped[int] = mapped_column(primary_key=True, init=False)
	name: Mapped[str] = mapped_column(String(30))
	fullname: Mapped[str | None] = mapped_column(String(100), default=None)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		init=False,
	)
```

Ovde `created_at` ima tri odvojena aspekta:

- `Mapped[datetime]` opisuje mapiranu Python vrednost kao `datetime` i podrazumevano označava obaveznu kolonu.
- `DateTime(timezone=True)` traži SQLAlchemy tip kolone sa podrškom za vremensku zonu, ako je izabrani dijalekt i baza podržavaju.
- `server_default=func.now()` traži od SQLAlchemy-ja da u DDL šeme upiše serverski `DEFAULT` izraz za trenutno vreme.
- `init=False` je dataclass opcija: `created_at` se ne pojavljuje kao argument u automatskom Python konstruktoru.

Primarni ključ `id` takođe ima `init=False`: aplikacija ne prosleđuje ID pri stvaranju novog korisnika, a baza ga generiše kao integer primarni ključ.

### Šta zapravo znači `func.now()`?

`func` je SQLAlchemy namespace za SQL funkcije. Izraz `func.now()` nije poziv Python funkcije koji odmah vraća Python `datetime`. On pravi SQLAlchemy objekat koji predstavlja SQL funkciju za trenutno vreme. Dijalekt ga prevodi u SQL izraz koji ciljna baza razume.

Za ovaj primer SQLAlchemy `2.0.38` sa SQLite-om emituje DDL u ovom obliku:

```sql
created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL
```

PostgreSQL ili drugi dijalekt može emitovati drugačiji izraz ili tip. Zato naziv Python funkcije `func.now()` ne garantuje identičan SQL tekst ni identično ponašanje svake baze.

### `server_default` je pravilo šeme

Kada `create_all()` napravi novu tabelu, `server_default` se upisuje kao `DEFAULT` u DDL. Zatim baza primenjuje default kada INSERT izostavi kolonu. To važi i za SQLAlchemy klijenta i za drugi SQL klijent, sve dok taj klijent izostavi kolonu ili koristi `DEFAULT`.

To se razlikuje od `default_factory`:

| Podešavanje                     | Ko izračunava vrednost? | Kada?                                | U kom slučaju važi?                                                           |
| ------------------------------- | ----------------------- | ------------------------------------ | ----------------------------------------------------------------------------- |
| Dataclass `default_factory=...` | Python                  | Pri pravljenju ORM/dataclass objekta | Objekat dobija vrednost pre INSERT-a.                                         |
| `default=...`                   | SQLAlchemy              | Pri izvršavanju SQLAlchemy INSERT-a  | Važi za iskaze koje izvršava SQLAlchemy, ali se ne upisuje kao DDL `DEFAULT`. |
| `server_default=...`            | Baza                    | Pri INSERT-u koji izostavi kolonu    | Pravilo je deo šeme i dostupno je i drugim klijentima.                        |

`server_default` ne zamenjuje `nullable=False`. Ako INSERT izostavi kolonu, baza može da primeni default. Ako INSERT izričito pošalje `NULL`, default se obično ne primenjuje i `NOT NULL` ograničenje odbija upis.

Server-side timestamp je koristan kada želimo da vreme odgovara satu baze i trenutku izvršavanja INSERT-a u bazi, a ne trenutku kada je Python objekat ranije napravljen. To može da izbegne razlike između satova aplikacionih procesa. Ipak, izbor zavisi od zahteva: baza mora podržavati izabranu funkciju, a timezone i preciznost vremena zavise od dijalekta i tipa kolone.

Ako se tabela već postoji, promena modela na `server_default=...` ne menja postojeću šemu. Potrebna je migracija ili drugi nameran DDL. Novi `create_all()` preskače postojeću tabelu.

### SQLite i vremenska zona

U primeru je zadržan `DateTime(timezone=True)`, ali SQLite-ov uobičajeni `DATETIME` ne pruža PostgreSQL semantiku `TIMESTAMP WITH TIME ZONE`. SQLite `CURRENT_TIMESTAMP` proizvodi vremensku vrednost u formatu i preciznosti koje određuje SQLite; SQLAlchemy-jev SQLite tip pri čitanju ne vraća automatski timezone-aware Python objekat.

Zato `timezone=True` nije obećanje da će SQLite sačuvati `tzinfo` ili originalni offset. Ako je tačna timezone-aware Python vrednost obavezna, strategija čuvanja i čitanja mora se posebno definisati i testirati za ciljnu bazu.

## `insert()` nad ORM entitetom

Predavač prosleđuje ORM klasu kao cilj INSERT iskaza:

```python
from sqlalchemy import insert

statement = insert(User)
```

`User` je ORM entitet, ali `insert(User)` i dalje pravi SQLAlchemy Core DML iskaz nad tabelom koju taj entitet mapira. Klasa je zgodan način da se označi cilj; SQLAlchemy ispod koristi `User.__table__`.

Pošto je INSERT iskaz napravljen bez vrednosti, on još nije spreman za stvarni upis. Pregled njegovog SQL oblika može pokazati placeholder-e za vrednosti koje još nisu određene. `statement` je Python opis naredbe, ne već izvršena promena u bazi.

## `.values()` i generativna izgradnja iskaza

Da bismo naveli podatke, dodajemo `.values(...)`:

```python
statement = insert(User).values(
	name="spongebob",
	fullname="SpongeBob SquarePants",
)
```

`.values()` prima vrednosti po imenima mapiranih atributa/kolona. U ovom primeru `name` i SQL kolona se isto zovu. Kada se Python ime atributa razlikuje od SQL imena kolone, ORM iskaz može koristiti ime mapiranog atributa; u čistom Core `Table.insert()` uobičajeno se koriste imena kolona.

Predavač opisuje obrazac kao „generative“/method chaining: `.values(...)` vraća novi, prošireni iskaz umesto da menja prethodni objekat u mestu. Možemo zato da zadržimo osnovni iskaz i od njega napravimo više varijanti:

```python
base_insert = insert(User)

spongebob_insert = base_insert.values(
	name="spongebob",
	fullname="SpongeBob SquarePants",
)

patrick_insert = base_insert.values(
	name="patrick",
	fullname="Patrick Star",
)
```

`base_insert` ostaje bez dodatih vrednosti, dok su `spongebob_insert` i `patrick_insert` odvojeni iskazi. Imena podataka su ovde samo demonstracioni primeri.

## Zašto se string ne vidi u SQL tekstu?

SQLAlchemy uglavnom ne umeće vrednosti direktno u SQL tekst. Umesto toga, pravi **bind parametre**. Na primer, iskaz:

```python
statement = insert(User).values(
	name="spongebob",
	fullname="SpongeBob SquarePants",
)
```

pri kompajliranju za SQLite može izgledati ovako:

```sql
INSERT INTO user_account (name, fullname) VALUES (?, ?)
```

Vrednosti se šalju odvojeno kroz DBAPI drajver. U `created_at` nema bind parametra zato što ga nismo naveli: primeniće se serverski default. `id` takođe izostavljamo jer ga baza generiše.

Parametrizacija je važna zato što:

- vrednost se ne meša sa strukturom SQL-a, čime se smanjuje rizik od SQL injection-a;
- SQLAlchemy i drajver pravilno prilagođavaju tipove Python vrednosti ciljnoj bazi;
- isti oblik iskaza može se koristiti sa drugim vrednostima;
- SQLAlchemy može ponovo koristiti kompilaciju iskaza istog oblika.

Nemoj ručno praviti INSERT konkatenacijom korisničkog teksta u SQL string. Koristi `.values(...)` ili bind parametre.

## Pregled kompajliranog iskaza za debug

Za uvid u SQLAlchemy iskaz može se koristiti `compile()`:

```python
compiled = statement.compile(engine)
print(compiled)
print(compiled.params)
```

`compiled` prikazuje SQL sa placeholder-ima, a `compiled.params` mapu vrednosti koje će biti vezane uz placeholder-e. U konkretnom SQLite iskazu, nazivi parametara i prikaz mogu se razlikovati po dijalektu.

Za lokalno otklanjanje grešaka postoji i `literal_binds=True`:

```python
debug_sql = statement.compile(
	engine,
	compile_kwargs={"literal_binds": True},
)
print(debug_sql)
```

To može prikazati vrednosti inline u SQL tekstu, ali služi samo za pregled/diagnostiku. Ne treba ga koristiti kao način izvršavanja upita niti za pravljenje SQL stringa od korisničkog unosa. Literalni prikaz može biti nepotpun za tipove ili vrednosti koje dijalekt ne ume da formatira i može otkriti privatne podatke u logovima.

## Izvršavanje: Core INSERT preko konekcije

Transkript se prekida baš dok predavač počinje ovaj korak. Sledeći mali primer je rekonstrukcija izvršavanja na osnovu prethodnih lekcija:

```python
from sqlalchemy import create_engine, insert, select

engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)

statement = insert(User).values(
	name="spongebob",
	fullname="SpongeBob SquarePants",
)

with engine.begin() as connection:
	result = connection.execute(statement)
	new_user_id = result.inserted_primary_key[0]

with engine.connect() as connection:
	row = connection.execute(
		select(User.__table__.c.id, User.__table__.c.name, User.__table__.c.created_at)
		.where(User.__table__.c.id == new_user_id)
	).one()
	print(row)
```

- `connection.execute(statement)` izvršava Core iskaz; ne dodaje ORM objekat u `Session`.
- `engine.begin()` potvrđuje transakciju pri normalnom izlasku iz bloka.
- `result.inserted_primary_key` daje primarni ključ reda kada ga dijalekt može obezbediti.
- Drugi blok je samo ilustrativna provera reda kroz Core `Connection` i `select()`; predavanje će detaljnije obrađivati upite u sledećim poglavljima.
- Server-side `created_at` nije poslat u `.values(...)`; SQLite ga je obezbedio iz DDL `DEFAULT` izraza.

Ako izvršimo `insert(User)` preko ORM `Session`-a, SQLAlchemy može da primeni ORM-specifično ponašanje i vrati ORM rezultate, zavisno od iskaza i verzije. U ovoj lekciji cilj je Core obrazac kroz `Connection`; ORM dodavanje objekata i praćenje stanja obrađuju se kasnije.

## `create_all()` i serverski default

Redosled je bitan:

1. `server_default=func.now()` mora biti prisutan kada se nova tabela kreira da bi se `DEFAULT` našao u njenom DDL-u.
2. `create_all()` kreira tabelu koja nedostaje.
3. INSERT izostavi `created_at`.
4. Baza primeni podrazumevanu funkciju i napravi vrednost.

Ako model promenimo nakon što tabela već postoji, novi `create_all()` neće dodati default na tu postojeću kolonu. Metadata opisuje željeni model, ali ne migrira živu tabelu. Za promenu postojeće šeme koristi se migracija.

Takođe, `server_default` radi kada kolona nije navedena. Ako klijent izričito pošalje `NULL`, baza obično neće zameniti tu vrednost default-om; pošto je `created_at` ne-nullable, takav INSERT treba da bude odbijen.

## Istorijska napomena o MyPy-u iz predavanja

Predavanje pominje problem u MyPy `1.1.1` vezan za noviju Python dataclass funkcionalnost. To je napomena o alatima iz vremena snimanja 2023. godine, ne opšti nedostatak SQLAlchemy-ja niti razlog da danas instaliramo baš tu verziju. Ako statička provera prijavi problem u aktuelnom okruženju, proveri verzije MyPy-ja i SQLAlchemy dokumentaciju za odgovarajuću kombinaciju verzija.

## Sažetak za ponavljanje

- `insert(User)` pravi Core INSERT iskaz čiji je cilj tabela ORM entiteta `User`.
- `.values(...)` dodaje vrednosti i vraća novi, generativno izgrađen iskaz.
- `created_at` je izostavljen iz Python konstruktora (`init=False`) i INSERT-a; bazni DDL `DEFAULT` ga popunjava.
- `server_default=func.now()` čuva funkciju u šemi; `func.now()` nije poziv Python sata.
- Bind parametri drže vrednosti odvojeno od SQL teksta; `compiled.params` ih može prikazati za debug.
- `literal_binds=True` je samo za pregled i može otkriti vrednosti; ne koristi se za izvršavanje korisničkog SQL-a.
- `Connection.execute()` je ovde Core putanja; ORM `Session` i persistencija ORM objekata dolaze kasnije.
- Serverski default u DDL-u važi i za druge klijente koji izostave kolonu, ali samo ako je postojeća šema zaista kreirana/migrirana sa tim default-om.

## Vežbe za playground

Dodaj zaseban fajl u `playground/sqlalchemy_2/` i koristi postojeći root `.venv`.

1. Definiši `User` sa `id`, `name`, `fullname` i `created_at`; stavi `init=False` na ID i timestamp.
2. Postavi `server_default=func.now()` na `created_at`, napravi novu memorijsku tabelu i pregledaj DDL uz `echo=True`.
3. Sastavi `insert(User).values(...)`; ispiši običnu kompilaciju i `compiled.params`. Proveri da `created_at` nije prosleđen.
4. Izvrši INSERT unutar `with engine.begin()` i pročitaj upisani red kroz Core `select()`.
5. Napravi drugu instancu istog iskaza sa drugim `.values(...)` i proveri da prethodni iskaz nije promenjen.
6. Uporedi Python `default_factory` sa baznim `server_default` u zasebnoj tabeli; proveri ko popunjava vrednost i kada.
7. Nemoj dodavati korisnički tekst u SQL f-string. Uporedi siguran bind parametar sa vrednošću koju `compiled.params` prikazuje samo radi pregleda.
