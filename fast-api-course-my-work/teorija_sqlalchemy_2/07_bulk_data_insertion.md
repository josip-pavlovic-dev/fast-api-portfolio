# Lekcija 07: Grupni unos podataka

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 47:08–57:26
**Glavne teme:** paramstyle baze, izvršavanje jednog INSERT iskaza sa više skupova parametara, DBAPI `executemany` i prelaz na `SELECT`.

Transkript nastavlja neposredno prethodnu lekciju: izvršava se jedan INSERT, objašnjava SQLite znak `?`, pa se prelazi na listu rečnika kao ulaz za više redova. Završetak samo započinje poglavlje o čitanju podataka. Primeri ispod su samostalne rekonstrukcije; u transkriptu nema celog programskog fajla.

## Od jednog reda do više redova

U prethodnoj lekciji koristili smo `.values(...)` da vrednosti dodamo samom INSERT iskazu:

```python
statement = insert(User).values(
	name="spongebob",
	fullname="SpongeBob SquarePants",
)

with engine.begin() as connection:
	connection.execute(statement)
```

To je praktično kada konstruišemo jedan INSERT sa jednim skupom vrednosti. Za više redova u Core stilu možemo da prosledimo parametre odvojeno, kao drugi argument `execute()` poziva:

```python
from sqlalchemy import insert

statement = insert(User)
parameters = [
	{
		"name": "spongebob",
		"fullname": "SpongeBob SquarePants",
	},
	{
		"name": "patrick",
		"fullname": "Patrick Star",
	},
]

with engine.begin() as connection:
	result = connection.execute(statement, parameters)
```

`statement` opisuje operaciju i ciljnu tabelu. Lista u drugom argumentu opisuje vrednosti za pojedinačne redove. U ovom primeru SQLAlchemy generiše/kompajlira INSERT koji upisuje `name` i `fullname`, a oba skupa parametara koriste taj oblik.

Svaki rečnik predstavlja jedan red, a njegovi ključevi su mapirana imena atributa/kolona. Za `insert(User)` ova jednostavna imena se poklapaju sa imenima SQL kolona. Vrednosti nisu spojene u SQL tekst; ostaju bind parametri.

## Tri slična, ali različita oblika

Na prvi pogled ovi oblici deluju zamenljivo, ali znače različite stvari:

| Oblik                                                     | Značenje                                                                            |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `insert(User).values(name="spongebob")`                   | Jedan INSERT iskaz sa jednim skupom vrednosti ugrađenim u iskaz kao bind parametri. |
| `connection.execute(insert(User), {"name": "spongebob"})` | Jedan INSERT iskaz i jedan skup parametara prosleđen pri izvršavanju.               |
| `connection.execute(insert(User), [{...}, {...}])`        | Jedan INSERT iskaz i više skupova parametara; SQLAlchemy može da ih obradi grupno.  |

Lekcija koristi treći oblik za sirove rečnike. Ne pravi se po jedan ORM objekat `User` za svaki red i ne koristi se ORM `Session`; iskaz se izvršava kroz Core `Connection`.

Nemoj mešati listu parametara za `execute()` sa ručnim pravljenjem jednog SQL izraza koji sadrži `VALUES (...), (...)`. Prvi oblik daje SQLAlchemy-ju skup parametara za jedan iskaz, a drugi eksplicitno gradi višeredni SQL `VALUES` izraz. Dijalekt može interno da odabere efikasan način izvršavanja; ovde učimo javni oblik SQLAlchemy poziva, ne ručno upravljanje tim detaljima.

## Rečnici moraju imati dosledan oblik

Za listu parametara SQLAlchemy određuje koje kolone pripadaju iskazu na osnovu ključeva prvog rečnika. Ostali rečnici treba da imaju kompatibilan skup ključeva. Ako prvi rečnik sadrži `fullname`, a neki kasniji ga izostavi, izvršavanje može prijaviti da nedostaje vrednost za očekivani parametar. Ako neki red treba da ima SQL `NULL`, napiši ga izričito:

```python
parameters = [
	{"name": "spongebob", "fullname": "SpongeBob SquarePants"},
	{"name": "squidward", "fullname": None},
]
```

`None` je stvarna poslata vrednost i u bazi postaje `NULL` ako kolona to dozvoljava; to nije isto što i izostaviti kolonu. Ako je kolona izostavljena iz svih rečnika, može se primeniti njen server default ili drugo pravilo default-a.

Koristi iste ključeve u svim rečnicima za jedan bulk poziv. To olakšava čitanje koda i izbegava dvosmislenost oko toga da li kolona treba da bude izostavljena ili eksplicitno postavljena na `NULL`.

## SQLAlchemy parametri i DBAPI paramstyle

U prethodnoj lekciji se pri pregledu iskaza mogao videti oblik sa imenovanim placeholder-ima, kao `:name`. Pri izvršavanju nad SQLite-om SQL log prikazuje `?`:

```text
INSERT INTO user_account (name, fullname) VALUES (?, ?)
```

To je zato što SQLAlchemy kompajlira iskaz prema dijalektu i DBAPI drajveru. SQLite `sqlite3` drajver koristi `qmark` oblik, odnosno upitnike. Drugi drajveri koriste druge dozvoljene DBAPI stilove, na primer imenovane ili `%s` placeholder-e.

U Python SQLAlchemy kodu vrednosti se prosleđuju kao rečnici, što je dosledno i razumljivo. Dijalekt prevede iskaz i vrednosti u oblik koji konkretni drajver očekuje. Kada drajver koristi pozicione placeholder-e kao `?`, SQLAlchemy može pretvoriti vrednosti rečnika u pozicioni tuple, u ispravnom redosledu. Aplikacioni kod ne mora ručno da obavlja tu konverziju.

Zato mogu istovremeno važiti oba zapažanja:

- na nivou SQLAlchemy iskaza parametar je imenovan i vezan za ključ kao što je `name`;
- u SQLite SQL logu placeholder je `?`, a parametri se prikazuju kao pozicione vrednosti.

Nemoj ručno menjati `:name` u `?` ili sastavljati tuple redosled po osećaju. Prepusti dijalektu da prevede iskaz.

## Šta se dešava pri bulk `execute()` pozivu?

Za SQLAlchemy 2.0 Core poziv:

```python
connection.execute(insert(User), parameters)
```

lista rečnika je niz skupova vrednosti za isti logički INSERT. U mnogim uobičajenim kombinacijama SQLAlchemy prosleđuje iskaz i niz parametara DBAPI `executemany()` operaciji. DBAPI i drajver tada izvršavaju isti SQL oblik nad više skupova parametara.

To je često efikasnije i jednostavnije od Python petlje koja za svaki red posebno poziva `connection.execute()`, jer SQLAlchemy može da grupiše rad i drajver može da optimizuje izvršavanje. Ipak, nemoj to tumačiti kao obećanje da će svaki dijalekt izvršiti isti broj mrežnih poziva ili koristiti identičnu internu strategiju. Konkretno ponašanje zavisi od dijalekta, drajvera, iskaza, `RETURNING` zahteva i podešavanja.

SQLAlchemy 2.0 može za odgovarajuće dijalekte da koristi i optimizovan `insertmanyvalues` pristup. To je interna strategija za efikasno grupisanje/izvršavanje, a ne razlog da menjamo javni obrazac koji učimo. Važna je razlika između API-ja koji prosleđuje listu parametara i tačne optimizacije koju dijalekt izabere.

U `echo=True` logu se tipično vidi jedan SQL oblik i više skupova parametara, na primer:

```text
INSERT INTO user_account (name, fullname) VALUES (?, ?)
[generated ...] [('spongebob', 'SpongeBob SquarePants'), ('patrick', 'Patrick Star')]
```

Log pokazuje SQLAlchemy-jevu perspektivu i prosleđene vrednosti; to je koristan dokaz da smo napravili grupni poziv, ali samo po sebi ne otkriva svaki detalj šta DBAPI ili server rade interno.

## Default vrednosti u bulk INSERT-u

U prethodnoj lekciji `created_at` je imao `server_default=func.now()`. Ako ga izostavimo iz svih parametarskih rečnika:

```python
parameters = [
	{"name": "spongebob", "fullname": "SpongeBob SquarePants"},
	{"name": "patrick", "fullname": "Patrick Star"},
]
```

baza primenjuje serverski default za svaki umetnuti red, pod uslovom da postojeća tabela zaista sadrži `DEFAULT` pravilo. Vrednosti `id` i `created_at` iz primera tako ne moraju biti sastavljene u Python-u.

Ovo važi zato što su kolone izostavljene, ne zato što SQLAlchemy grupni INSERT „automatski zna“ kako da napravi timestamp. SQLAlchemy emituje INSERT za prosleđene kolone; bazni server primenjuje pravilo iz DDL-a.

Ako pošaljemo `"created_at": None`, to je eksplicitni SQL `NULL`, a ne zahtev da se server default primeni. Ako je kolona `NOT NULL`, baza bi trebalo da odbije red.

## Transakcija i atomicity

Primer iz predavanja koristi:

```python
with engine.begin() as connection:
	connection.execute(insert(User), parameters)
```

Svi redovi iz tog poziva pripadaju istoj transakciji. Normalan izlazak iz bloka potvrđuje transakciju; greška koja izađe iz bloka pokreće rollback, pa ne ostavljamo namerno samo deo uspešno upisanih redova.

To je važno za atomicity: čitav posao treba da bude sačuvan ili poništen kao jedinica. Tačno ponašanje pri greškama ipak zavisi i od baze i storage engine-a; za SQLite i uobičajene transakcijske baze ova transakcijska namera ima očekivano ponašanje.

`executemany` je način predaje više skupova parametara drajveru; sam naziv ne garantuje transakciju. Transakciju ovde obezbeđuje `engine.begin()` kontekst.

## Core bulk INSERT naspram ORM bulk rada

U ovom poglavlju „koristimo ORM model“ znači da je `User` zgodan cilj iskaza i izvor metadata-e. Pošto poziv ide preko `Connection.execute()`, to je Core izvršavanje. Rečnici predstavljaju redove; ne prave se `User(...)` instance koje ORM `Session` prati.

SQLAlchemy podržava i izvršavanje INSERT iskaza preko `Session`, uključujući ORM bulk obrasce. Tada se primenjuju ORM specifična pravila za imena atributa i rezultate. Predavač kaže da je sličan unos moguć i u ORM-u, ali u ovoj demonstraciji bira Core `Connection`; ne treba mešati oba mehanizma dok se uče osnove.

## Kratki digresioni odgovor o Pydantic-u

Između objašnjenja placeholder-a i bulk unosa predavač odgovara na pitanje o Pydantic-u/SQLModel-u. Odgovor je neformalan i oprezan: navodi da ne radi mnogo direktno sa Pydantic-om i razmatra Pydantic dataclass integraciju kao moguću kombinaciju sa SQLAlchemy dataclass modelima.

Ovo nije API korak lekcije niti stabilna preporuka koju treba odmah primeniti. Pydantic modeli služe validaciji/serializaciji, a SQLAlchemy modeli mapiranju i radu sa bazom; kasnije se mogu povezati kroz jasne granice, ali se njihove uloge ne poistovećuju. Za sada nastavljamo sa običnim SQLAlchemy primerima.

## Prelaz na `SELECT`

Od 54:33 predavanje započinje čitanje podataka. Prvo prikazuje tekstualni SQL preko `text()`, a zatim SQLAlchemy Core `select()` izraz zasnovan na class-level atributu ORM modela:

```python
from sqlalchemy import select, text

raw_statement = text("SELECT name FROM user_account")
core_statement = select(User.name)
```

U oba slučaja čitanje se izvršava preko `Connection`, a rezultat sadrži obične redove/kolone, ne automatski `User` ORM objekte. `User.name` je descriptor na klasi koji SQLAlchemy koristi kao izraz kolone; `user.name` na instanci je Python vrednost.

Transkript ovde tek počinje SELECT poglavlje i ne pokriva punu izgradnju upita. Detalje `select()`, `where()`, rezultata i ORM objekata ostavićemo za sledeću lekciju.

## Sažetak za ponavljanje

- `connection.execute(insert(User), dict)` unosi jedan red iz odvojenog skupa parametara.
- `connection.execute(insert(User), [dict1, dict2])` prosleđuje više skupova parametara za isti INSERT.
- Ključevi rečnika određuju kolone; svi rečnici u jednoj grupi treba da imaju kompatibilan oblik.
- SQLAlchemy iskaz može prikazati imenovane parametre, dok SQLite koristi `?`; dijalekt prilagođava placeholder-e i parametre drajveru.
- SQLAlchemy često koristi DBAPI `executemany`, ali optimizacija zavisi od dijalekta, drajvera i iskaza.
- Lista parametara nije isto što i ručno građen višeredni `VALUES` iskaz.
- Serverski default važi za svaku izostavljenu kolonu u svakom redu, ako je default prisutan u fizičkoj šemi.
- `engine.begin()` daje transakcijsku granicu; `executemany` sam po sebi ne znači atomicity.
- Ovaj Core primer ne pravi ORM instance niti koristi `Session`.
- Kraj transkripta samo započinje tekstualni i Core `SELECT`; detalji slede u narednoj lekciji.

## Vežbe za playground

Dodaj zaseban fajl u `playground/sqlalchemy_2/` i koristi postojeći root `.venv`.

1. Kreiraj `User` sa server-default vremenom, napravi tabelu i pripremi `insert(User)`.
2. Prosledi jedan rečnik kao drugi argument `execute()` i proveri upis.
3. Prosledi listu od najmanje tri rečnika i uporedi log sa tri zasebna `execute()` poziva.
4. U svim rečnicima koristi isti skup ključeva; zatim namerno izostavi jedan ključ u drugom rečniku i zabeleži grešku.
5. Izostavi `created_at` i potvrdi da baza primenjuje server default za svaki red. Zatim prosledi `None` i proveri razliku.
6. Izazovi grešku u `engine.begin()` bloku i proveri da li se redovi iz te transakcije ponište.
7. Uporedi SQLAlchemy izraz sa parametrima i SQL koji SQLite loguje sa `?` placeholder-ima.
