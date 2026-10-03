# Lekcija 04: Deklarativna baza (`DeclarativeBase`)

## Cilj lekcije

Pre definisanja ORM modela potrebno je napraviti zajedničku baznu klasu od koje će modeli nasleđivati SQLAlchemy ORM ponašanje. Ova lekcija uvodi deklarativno mapiranje i pokazuje njegovu najmanju početnu definiciju:

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
	pass
```

U ovoj skripti još nema konkretnih modela, kolona, engine-a, sesije niti povezivanja sa bazom. To je nameran prvi korak; konkretne klase tabela dolaze u sledećim lekcijama.

## Ispravka naziva iz transkripta

U transkriptu se nekoliko puta čuje „decorative mapping“ i „decorative base“. To je greška automatskog prepoznavanja govora. Ispravni termini su **declarative mapping** i **declarative base**, odnosno deklarativno mapiranje i deklarativna baza.

## Šta je ORM mapiranje?

ORM (Object Relational Mapper) povezuje Python klase i objekte sa relacionom šemom i zapisima u bazi. **Mapiranje** je skup informacija koje SQLAlchemy koristi da bi znao:

- koja Python klasa predstavlja koji entitet;
- kojoj tabeli klasa odgovara;
- koje osobine klase predstavljaju kolone;
- kako se redovi baze pretvaraju u Python objekte i obrnuto.

U deklarativnom stilu programer opisuje modele pomoću Python klasa. SQLAlchemy pregleda te deklaracije i izgradi ORM mapiranja i opis šeme. To ne znači da se sirovi SQL više ne koristi: SQLAlchemy na kraju sastavlja i izvršava SQL prema bazi.

## Tri koraka koja transkript uvodi

Transkript predstavlja proces kao tri faze:

1. **Definišemo baznu klasu.** Ona pruža zajedničku osnovu za ORM modele.
2. **Definišemo Python klase za entitete iz ERD-a.** Svaka konkretna klasa opisuje odgovarajuću tabelu i njene kolone.
3. **SQLAlchemy mapira klase i kasnije se njihovi opisi koriste za pravljenje tabela.** U sledećoj oblasti engine i metadata će omogućiti da se opis šeme primeni na konkretnu bazu.

U ovoj lekciji završavamo samo prvi korak. Korisno je razlikovati „SQLAlchemy zna kako je tabela opisana“ od „tabela je već napravljena u bazi“.

## Šta radi `DeclarativeBase`?

`DeclarativeBase` je klasa iz `sqlalchemy.orm` uvedena u SQLAlchemy 2.0. Kada od nje izvedemo sopstveni `Base`, dobijamo deklarativnu osnovu za modele.

SQLAlchemy na toj osnovi organizuje ORM infrastrukturu, uključujući registry za mapirane klase i metadata objekat koji prikuplja opise tabela. Kada se kasnije definiše konkretna klasa koja nasleđuje `Base` i navede tabelu, njen opis ulazi u taj zajednički sistem.

Zajednički `Base` zato omogućava da modeli koji pripadaju istoj šemi budu prikupljeni u jednom metadata objektu. Kasnije se taj metadata koristi, na primer, pozivom `Base.metadata.create_all(engine)`.

### `Base` nije tabela

Sama klasa `Base` iz ove lekcije nije tabela `base` i nema svoje kolone. Ona je osnova za buduće deklaracije. Konkretni ORM model obično nasleđuje `Base` i navodi `__tablename__` i mapirane atribute.

### `Base` ne pravi vezu sa bazom

U ovoj skripti ne postoje:

- database URL;
- `create_engine(...)`;
- ORM sesija;
- poziv ka PostgreSQL-u ili SQLite-u;
- naredba koja kreira tabelu.

Zato se ovaj fajl može uvesti bez pokretanja baze. Engine i operacije nad stvarnom bazom obrađuju se kasnije.

## Objašnjenje skripte red po red

### `from sqlalchemy.orm import DeclarativeBase`

`DeclarativeBase` dolazi iz ORM sloja SQLAlchemy-ja. Uvozimo ga zato što pravimo ORM deklarativnu osnovu, a ne samo SQL izraz ili konekciju.

### `class Base(DeclarativeBase):`

Definišemo svoju klasu nazvanu `Base` koja nasleđuje `DeclarativeBase`. Naziv `Base` je uobičajena konvencija, ali nije rezervisana reč: tehnički bi klasa mogla da se zove i drugačije. Važan je odnos nasleđivanja.

Kada kasnije napišemo, na primer, `class Product(Base):`, model će biti deo deklarativnog sistema koji je ova baza postavila.

### `pass`

Python zahteva telo klase. `pass` je naredba koja ne radi ništa i služi da telo klase bude sintaksički validno dok nemamo sopstvena podešavanja za nju.

ORM funkcionalnost ne dolazi od `pass`; dolazi od nasleđivanja `DeclarativeBase`. U ovom trenutku klasa nema dodatne metode ili atribute, pa je `pass` dovoljan. Kasnije se telo `Base` klase može proširiti, ali za primere iz kursa to nije potrebno.

## Zašto svi modeli nasleđuju istu bazu?

Modeli koji pripadaju istoj šemi obično nasleđuju isti `Base`. Tako SQLAlchemy može da prikupi njihove tabele u istom metadata objektu. Kada se u sledećoj oblasti pozove `Base.metadata.create_all(engine)`, SQLAlchemy može da pronađe tabele svih učitanih modela u toj metadata kolekciji.

Ako model ne nasleđuje odgovarajući `Base`, ne mora biti deo metadata objekta koji koristi ostatak aplikacije. Posledica može biti da se njegova tabela ne pojavi pri kreiranju šeme ili da ORM nema odgovarajuće mapiranje.

Jedna aplikacija može imati više deklarativnih baza kada za to postoji razlog, na primer odvojene metadata kolekcije ili različiti sistemi. Za primere u ovom kursu koristimo jednu zajedničku bazu.

## Od deklaracije do stvarne tabele

Proces je najbolje razumeti kao nekoliko odvojenih slojeva:

1. Python klasa nasledi `Base`.
2. Deklarativni sistem mapira konkretnu klasu i sastavlja opis tabele u metadata objektu.
3. Aplikacija napravi engine koji zna kako da se poveže sa određenom bazom.
4. Operacija poput `Base.metadata.create_all(engine)` pošalje bazi potrebne DDL naredbe za tabele koje nedostaju.

Definisanje `Base` samo po sebi završava se prvim pripremnim korakom. Ne treba poistovećivati definisanje Python klase, kreiranje metadata opisa i izvršavanje DDL-a nad serverom baze.

`create_all()` je koristan za početne primere i razvoj. On ne zamenjuje verzionisane migracije: kasnije izmene već postojeće šeme u ozbiljnom projektu obično se vode Alembicom.

## Dopunski primer: konkretan model na istoj osnovi

Sledeći primer je dodatak radi povezivanja lekcije 04 sa narednim korakom. Finalna skripta ove lekcije sadrži samo `Base`; konkretni model obrađuje se kasnije.

```python
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
	pass


class Category(Base):
	__tablename__ = "category"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(50))
```

Ovde `Category` predstavlja model koji će se mapirati na tabelu `category`. `__tablename__` daje ime tabele, a `Mapped[...]` i `mapped_column(...)` deklarišu mapirane kolone u SQLAlchemy 2.0 stilu. Tabela još nije nužno napravljena u bazi; za to su potrebni engine i naredni korak.

## `DeclarativeBase` naspram `declarative_base()`

SQLAlchemy 2.0 preporučuje nasleđivanje od `DeclarativeBase`, kao u ovoj lekciji. Ovaj pristup prirodno se uklapa sa tipizovanim deklaracijama `Mapped[...]` i `mapped_column(...)`, a IDE i alati za proveru tipova lakše razumeju vezu između atributa modela i njihovih Python tipova.

Stariji i dalje poznat obrazac koristi funkciju `declarative_base()`:

```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

To je drugačiji način da se dobije deklarativna baza. Prisustvo tog oblika u starijem kodu samo po sebi ne znači da aplikacija ne može raditi u SQLAlchemy 2.0. Za novi tipizovani kod biramo `DeclarativeBase`, ali ne treba tvrditi da je svaka upotreba `declarative_base()` automatski nevažeća.

## Šta transkript objašnjava dobro, a šta treba precizirati

- Tačno je da se klasa `Base` koristi kao osnova za buduće ORM modele.
- Tačno je da deklarativni stil omogućava opis modela pomoću Python klasa umesto ručnog pisanja DDL-a za svaku tabelu.
- Korist za tipizaciju i IDE podršku najjasnija je kada se uz `DeclarativeBase` koriste `Mapped` i `mapped_column`; sama prazna klasa `Base` ne dodaje tipizaciju kolonama koje još nisu napisane.
- Izraz „svaka klasa koja nasleđuje Base automatski je tabela“ je pojednostavljenje. Konkretna ORM klasa mora imati odgovarajuću mapiranu tabelu ili nasleđeno mapiranje; mogu postojati i apstraktne bazne klase i mixin-i koji nisu samostalne tabele.
- `pass` nije SQLAlchemy konfiguracija niti posebna ORM naredba. To je obična Python naredba koja popunjava prazno telo klase.
- Baza u smislu `Base` klase nije isto što i server baze podataka. Ona ne otvara konekciju i ne čuva redove podataka.

## Povezivanje sa TodoApp-om

TodoApp već koristi isti osnovni obrazac kroz `class Base(DeclarativeBase)` u `TodoApp/db/base.py`. Sadašnji `TodoApp/models.py` nasleđuje taj `Base` i koristi SQLAlchemy 2.0 tipizovani stil. Zbog toga ovu lekciju možeš neposredno povezati sa svojim refaktorom: `Base` je zajednički koren metadata sistema u koji se registruju `Todos` i `Users` modeli.

Kada modeli budu učitani, `Base.metadata` sadrži njihove opise tabela. Poziv `Base.metadata.create_all(bind=engine)` u TodoApp-u koristi engine da obezbedi tabele u podešenoj bazi. To je odvojeno od same definicije klase `Base`.

## Provera razumevanja

1. Zašto pravimo prilagođenu klasu `Base` umesto da svaki model definišemo nezavisno?
2. Koju ulogu ima nasleđivanje iz `DeclarativeBase`?
3. Šta radi `pass`, a šta radi `DeclarativeBase`?
4. Da li se baza podataka ili tabela pravi izvršavanjem ove skripte?
5. Gde SQLAlchemy kasnije čuva opise modela i šta je potrebno da se ti opisi primene na stvarnu bazu?
6. Zašto se `DeclarativeBase` preporučuje za novi SQLAlchemy 2.0 kod, a zašto `declarative_base()` ne treba automatski proglasiti nevažećim?

## Sažetak

- Deklarativno mapiranje opisuje ORM modele pomoću Python klasa.
- `DeclarativeBase` iz SQLAlchemy 2.0 daje osnovu za te klase.
- `Base` je zajednički koren mapiranih modela i metadata kolekcije, a nije sama tabela niti database connection.
- `pass` samo omogućava prazno telo klase; ne aktivira ORM.
- Konkretni modeli i kolone dolaze u sledećoj lekciji, a kreiranje stvarnih tabela zahteva engine i zaseban korak.
- Savremeni tipizovani stil koristi `Mapped` i `mapped_column`; stariji `declarative_base()` obrazac i dalje postoji u SQLAlchemy 2.0.
