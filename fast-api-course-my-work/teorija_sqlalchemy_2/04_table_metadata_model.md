# Lekcija 04: Table metadata i deklarativni ORM model

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 20:33–33:51
**Tema:** opis tabele kroz Core `Table`, deklarativni ORM modeli, `Mapped[...]`, `mapped_column()` i opciona integracija sa Python dataclass-ama.

Transkript opisuje kod na slajdovima, ali ne sadrži njihove kompletne definicije. Primeri u ovoj belešci zato su ispravna SQLAlchemy 2.0 rekonstrukcija, a ne doslovni prepis koda predavača. Deo o atomarnosti je kratak nastavak prethodne lekcije; kraj transkripta prelazi ka tome kako deklarativna klasa obezbeđuje `Table` metadata.

## Zašto nam treba opis tabele?

U prethodnim lekcijama slali smo iskaze koji nisu morali da koriste postojeće tabele, kao `SELECT 1` ili parametarski `SELECT`. Čim želimo upit nad tabelom, aplikaciji treba način da opiše njenu strukturu: ime, kolone, tipove i ograničenja.

SQLAlchemy Core nudi Python objekte za taj opis. Najvažniji su `MetaData`, `Table` i `Column`. ORM deklarativni stil nudi drugi, klasno orijentisan način da se opiše ista tabela. Ne pravimo dve različite baze: oba pristupa mogu predstavljati metadata za tabelu u bazi.

## Core pristup: `MetaData`, `Table` i `Column`

`MetaData` je Python kolekcija koja okuplja opise tabela. `Table` u tu kolekciju dodaje opis jedne tabele, a `Column` opisuje njene kolone.

```python
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table

metadata = MetaData()

user_table = Table(
	"user_account",
	metadata,
	Column("id", Integer, primary_key=True),
	Column("name", String(30), nullable=False),
	Column("fullname", String(100), nullable=True),
	Column("created_at", DateTime(timezone=True), nullable=False),
)
```

Kako čitati ovu definiciju:

- `MetaData()` napravi praznu kolekciju za opise tabela.
- Prvi argument `Table()` je ime tabele u bazi.
- Drugi argument je `MetaData` objekat kome tabela pripada.
- Svaki `Column()` navodi ime kolone, SQLAlchemy tip i dodatna pravila.
- `primary_key=True` označava primarni ključ.
- `nullable=False` traži da kolona u šemi baze bude `NOT NULL`; `nullable=True` dozvoljava SQL `NULL`.
- `String(30)` navodi tekstualni SQL tip i željenu dužinu. Konkretan DDL može da se razlikuje po dijalektu baze.

Ovaj Python kod sam po sebi još ne izvršava `CREATE TABLE`. On opisuje šemu u memoriji. Kreiranje fizičke tabele u bazi je zaseban korak, na primer preko `metadata.create_all(engine)`, što pripada narednim lekcijama.

Core pristup ne zahteva ORM klasu, ORM `Session` ni Python objekat za svaki red. Možemo da koristimo opis tabele za SQL izraze i da radimo direktno sa `Connection`-om.

## ORM pristup: deklarativni model

U deklarativnom ORM stilu klasa predstavlja model, a SQLAlchemy iz njenih deklaracija pravi i ORM mapiranje i pripadajući `Table` objekat.

```python
from datetime import UTC, datetime

from sqlalchemy import DateTime, String
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
		default_factory=lambda: datetime.now(UTC),
	)


user = User("spongebob", "SpongeBob SquarePants")
print(user)
print(User.__table__)
print(Base.metadata.tables.keys())
```

Ime Python klase `User` i ime tabele `user_account` ne moraju biti ista. `__tablename__` određuje ime SQL tabele.

### Šta `DeclarativeBase` radi?

`DeclarativeBase` daje zajedničku osnovu za deklarativne modele. Kada klasa kao `User` nasledi `Base` i navede `__tablename__`, SQLAlchemy je registruje, obrađuje deklarisane atribute i napravi ORM mapper.

Osnovna klasa poseduje `Base.metadata`, zajednički registar opisa tabela. Deklarativni model dobija `User.__table__`, Python objekat `Table` koji odgovara toj klasi. U ovom primeru važi:

```python
User.__table__ is Base.metadata.tables["user_account"]
```

Zato predavač kaže da ORM klasa i Core `Table` pristup mogu opisati suštinski istu tabelu. Razlikuje se način na koji programer piše deklaraciju i šta dobija kao centralni objekat:

| Pristup          | Šta programer definiše?                | Šta dobija?                                                       |
| ---------------- | -------------------------------------- | ----------------------------------------------------------------- |
| Core             | `MetaData`, `Table`, `Column`          | Tabelu i SQL izraze nad njenim kolonama.                          |
| Deklarativni ORM | `DeclarativeBase` i Python model-klasu | ORM klasu, mapper i automatski kreirani `Table` metadata objekat. |

Ako je ostatak programa Core aplikacija i ne želi ORM `Session`, i dalje može koristiti `User.__table__` kao tabelu za Core upite. Deklarativna klasa ne primorava aplikaciju da koristi ORM operacije za svaki upit.

## `Mapped[...]`: Python tip i mapirana kolona

SQLAlchemy 2.0 koristi generičku anotaciju `Mapped[T]` da označi atribut koji učestvuje u ORM mapiranju:

```python
name: Mapped[str] = mapped_column(String(30))
```

- `Mapped[str]` govori da je vrednost atributa na Python objektu tipa `str` i da je atribut mapiran.
- `mapped_column(...)` je deklarativna konfiguracija kolone: ovde eksplicitno zadajemo SQLAlchemy tip `String(30)`.
- SQLAlchemy iz anotacije može da zaključi SQLAlchemy tip i nullability. Na primer, `Mapped[str]` podrazumevano označava ne-nullable atribut; `Mapped[str | None]` podrazumevano označava nullable atribut.

U jednostavnim slučajevima `mapped_column()` se može izostaviti:

```python
name: Mapped[str]
```

SQLAlchemy iz anotacije može zaključiti da je ovo mapirana tekstualna kolona. Koristimo `mapped_column()` kada treba da navedemo dodatne podatke, na primer primarni ključ, dužinu tipa, `nullable`, default ili druga pravila.

`Mapped[...]` nije isto što i SQL tip. To je tipizovani SQLAlchemy ORM atribut. `String`, `Integer` i `DateTime` su SQLAlchemy tipovi kolona koji se prevode u tipove izabranog dijalekta baze.

### `Mapped[T]` i `NULL`

Za polja iz primera:

| Deklaracija                             | Uobičajeni zaključak za kolonu     | Python vrednost                                                                  |
| --------------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------- |
| `name: Mapped[str]`                     | `NOT NULL`                         | Tekstualna vrednost; ne `None`.                                                  |
| `fullname: Mapped[Optional[str]]`       | `NULL` je dozvoljen                | Tekst ili `None`.                                                                |
| `id: Mapped[int]` uz `primary_key=True` | Primarni ključ, koji je `NOT NULL` | Može biti `None` pre nego što baza dodeli generisani ID; posle upisa je integer. |

Anotacija i konfiguracija kolone treba da opisuju isto pravilo. Ako je potrebno, `nullable=True` ili `nullable=False` u `mapped_column()` može eksplicitno da zada pravilo šeme, ali nemoj da Python tip tvrdi jedno, a kolona drugo bez jasnog razloga.

Obavezno polje i dalje nije isto što i „neprazan tekst“: `Mapped[str]`/`NOT NULL` sprečava `None`/SQL `NULL`, ali samo po sebi ne odbija `""` ili tekst od razmaka.

## `MappedAsDataclass`: ORM klasa sa dataclass ponašanjem

U predavanju se koristi dataclass integracija kao opcija. Osnovna ORM klasa i bez nje može da mapira tabelu; `MappedAsDataclass` dodaje dataclass ponašanje deklarativnim klasama, poput automatskog konstruktora (`__init__`) i prikaza (`__repr__`).

```python
class Base(MappedAsDataclass, DeclarativeBase):
	pass
```

Kada model nasledi ovaj `Base`, SQLAlchemy obradi mapirana polja kao dataclass polja. `mapped_column()` prihvata i opcije koje određuju kako će se polje ponašati u dataclass konstruktoru.

### Primarni ključ van konstruktora

U primeru je ID deklarisan ovako:

```python
id: Mapped[int] = mapped_column(primary_key=True, init=False)
```

- `primary_key=True` ga označava kao primarni ključ tabele.
- `init=False` je dataclass opcija: izostavlja `id` iz generisanog `__init__` konstruktora.

ID se obično generiše pri upisu u bazu, zato programer ne treba da ga prosleđuje prilikom pravljenja novog korisnika. Pre upisa, `user.id` može biti `None`; posle INSERT-a i flush/commit koraka baza može vratiti dodeljeni ID. Tip `Mapped[int]` opisuje mapirano polje, ali ne znači da novi objekat već ima generisanu celobrojnu vrednost.

`init=False` ne znači da kolona nije deo tabele. Kolona je i dalje u metadata i ostaje primarni ključ; samo nije argument Python konstruktora.

### Dataclass `default_factory` i vreme nastanka vrednosti

U primeru:

```python
created_at: Mapped[datetime] = mapped_column(
	DateTime(timezone=True),
	default_factory=lambda: datetime.now(UTC),
)
```

`default_factory` je Python factory za dataclass konstruktor. SQLAlchemy je pozove kada pravimo novi `User` objekat, pa svaki objekat dobije svoju vrednost vremena. Funkciju prosleđujemo kao factory; ne pozivamo je pri učitavanju modula.

To samo po sebi nije `DEFAULT` klauzula u bazi i ne čini da direktan SQL ili druga aplikacija dobije timestamp. U ovom obrascu Python objekat već nosi vrednost pre INSERT-a, pa ORM tu vrednost može da upiše. Serverski default, koji baza primenjuje i za druge klijente, zasebna je tema.

Predavač izričito kaže da kasnije pokazuje varijantu u kojoj vreme obezbeđuje baza. Dakle, ovde je namerno prikazan Python-side factory da bi se objasnila dataclass integracija; ne treba ga pomešati sa konačnim izborom gde aplikacija želi da izračuna vreme.

U dodatom primeru je korišćen `datetime.now(UTC)` da bi Python vrednost bila timezone-aware. To ne garantuje da će svaka baza sačuvati `tzinfo` ili offset. Konkretno, SQLite-ov standardni `DATETIME` ih ne čuva na isti način kao PostgreSQL `TIMESTAMP WITH TIME ZONE`; vremenske zone ćemo proveravati prema konkretnom dijalektu.

### Redosled i pozicioni argumenti

Dataclass konstruktor izlaže polja koja imaju `init=True` redom kojim su deklarisana. Pošto je `id` izostavljen iz konstruktora, sledeća dva argumenta u našem primeru su `name` i `fullname`:

```python
user = User("spongebob", "SpongeBob SquarePants")
```

To je validan pozicioni poziv, koji predavač koristi da pokaže da je klasa dataclass. U aplikacionom kodu često je čitljivije koristiti imenovane argumente:

```python
user = User(
	name="spongebob",
	fullname="SpongeBob SquarePants",
)
```

Polje `fullname` ima `default=None`, zato može da se izostavi. `created_at` ima `default_factory`, pa ni njega ne prosleđujemo. Ako promenimo redosled polja ili koja polja imaju default, menja se i konstruktor; imenovani argumenti smanjuju rizik od greške.

## Zašto se `Mapped` atribut drugačije ponaša na klasi i objektu?

Ovo je ključni obrazac koji predavač najavljuje za naredne Core upite. Jedan deklarisani atribut ima dva korisna oblika:

```python
user.name       # vrednost sa konkretnog Python objekta, npr. "spongebob"
User.name       # class-level SQLAlchemy atribut za upite i mapiranje
```

SQLAlchemy instrumentiše mapirani atribut kao Python descriptor:

- Kada čitamo `user.name` sa instance, dobijamo običnu Python vrednost.
- Kada koristimo `User.name` na klasi, dobijamo SQLAlchemy objekat koji može da učestvuje u SQL izrazima.
- Kada dodelimo `user.name = "new-name"`, ORM može da prati promenu objekta radi kasnijeg upisa.

Zato ovaj izraz gradi uslov upita, ali još ne izvršava SQL:

```python
from sqlalchemy import select

statement = select(User).where(User.name == "spongebob")
```

`User.name == "spongebob"` nije obična Python provera `True`/`False` nad jednom instancom. Class-level atribut prepoznaje poređenje kao SQL izraz koji odgovara uslovu `WHERE`. Tek kada iskaz izvršimo preko odgovarajuće konekcije ili ORM `Session`-a, SQLAlchemy šalje SQL bazi.

Tip `Mapped[str]` unapred daje alatima za statičku analizu informaciju da je atribut mapiran i tipizovan. U starijim obrascima deo te informacije dolazio je iz plugin-a; cilj 2.0 tipizovanog stila je da veliki deo bude vidljiv direktno iz modela.

## Jedna ORM klasa, Core upit

ORM model ne primorava aplikaciju da koristi ORM `Session`. Njegov `Table` objekat može se direktno koristiti za Core SQL izraze:

```python
from sqlalchemy import select

core_statement = select(User.__table__.c.name).where(
	User.__table__.c.name == "spongebob"
)

orm_statement = select(User).where(User.name == "spongebob")
```

- `core_statement` bira kolonu iz Core `Table` objekta; izvršavanje preko `Connection`-a daje Core rezultate.
- `orm_statement` bira ORM entitet; izvršavanje preko `Session`-a može da vrati `User` objekte.
- Oba iskaza koriste isti deklarativno kreirani opis tabele.

Ovo je razlog za komentar iz predavanja da i Core-orijentisana aplikacija može definisati metadata preko ORM klasa, a zatim koristiti `Engine`, `Connection` i SQL izraz bez ORM `Session`-a.

## Prikaz objekta u interaktivnoj konzoli

Predavač objašnjava da se korisnik pitao ko je pozvao `print()`. U interaktivnoj Python konzoli, kada se unese izraz kao:

```python
user
```

konzola automatski prikaže reprezentaciju rezultata izraza. Uz `MappedAsDataclass`, dataclass `__repr__` daje prikaz polja objekta. U običnoj `.py` skripti vrednost se neće sama ispisati; potreban je `print(user)` ili drugi način prikaza.

U ovom trenutku `user` je samo Python objekat. Njegovo pravljenje ne šalje INSERT i ne pravi red u bazi. ORM upis zahteva kasniji rad sa sesijom; kreiranje fizičke tabele zahteva zasebno izvršavanje DDL-a. Ove korake kurs obrađuje u drugim modulima.

## Kratak povratak na transakcijsku atomarnost

Pitanje iz publike vraća se na razliku između autocommit-a i transakcije. U autocommit režimu svaki iskaz se potvrđuje zasebno. Ako prvi i drugi INSERT uspeju, a treći padne, prva dva mogu ostati sačuvana, dok treći nije uspeo.

Transakcija omogućava atomarnost: skup promena se potvrdi kao celina ili se poništi kao celina. Ako tri povezana upisa pripadaju jednoj transakciji i treći ne uspe, aplikacija može da uradi rollback tako da prva dva ne ostanu kao delimično stanje.

SQLAlchemy 2.0 ne koristi raniji SQLAlchemy-level `autocommit` koji je automatski potvrđivao pojedine upite. Aplikacija treba jasno da označi granice transakcije kroz `commit()` ili transakcijski kontekst, kao što je `engine.begin()`. DBAPI/driver-level autocommit je zasebna, specifična postavka i ne obrađuje se u ovom primeru.

Za uobičajene aplikacione upise zato razmišljamo u terminima jedinice rada: koje promene pripadaju zajedno, gde počinje njihova transakcija i na kom mestu se potvrđuju ili poništavaju.

## Verzijski okvir i obim lekcije

Predavanje predstavlja tipizovani deklarativni stil i `mapped_column()` kao važne delove SQLAlchemy-ja 2.0. U ovom repozitorijumu koristimo SQLAlchemy `2.0.38`; smoke test je potvrdio da primer sa `MappedAsDataclass` radi u toj verziji.

Dataclass integracija je opcionalna. Ako je ne uključimo, i dalje možemo koristiti `DeclarativeBase`, `Mapped[...]` i `mapped_column()` za ORM model. Ne treba dodavati `MappedAsDataclass` svakom modelu samo zato što ga ovaj slajd koristi.

Ovaj transkript završava se dok predavač poredi automatski kreirani `User.__table__` sa ranije ručno napravljenim Core `Table` objektom. Sledeći deo predavanja nastavlja da koristi klasu za Core metadata i iskaze.

## Sažetak za ponavljanje

- Core `MetaData` prikuplja `Table` opise; `Column` opisuje kolone i njihova pravila.
- Python metadata opisuje šemu, ali je ne kreira u bazi sve dok se ne izvrši DDL.
- `DeclarativeBase` daje zajednički `Base.metadata`; deklarativna ORM klasa automatski dobija `__table__` i mapper.
- `Mapped[T]` označava tipizovani mapirani atribut i pomaže zaključivanju SQL tipa i nullability-ja.
- `mapped_column()` dodaje konfiguraciju kao što su SQL tip, primarni ključ, `nullable` i dataclass opcije.
- `MappedAsDataclass` je opcioni sloj koji obezbeđuje dataclass konstruktor i prikaz objekta.
- `init=False` izbacuje primarni ključ iz dataclass konstruktora, ne iz tabele.
- `default_factory` proizvodi Python vrednost pri pravljenju objekta; nije isto što i serverski `DEFAULT`.
- `User.name` na klasi može da gradi SQL izraz, dok `user.name` na instanci vraća Python vrednost.
- Deklarativnu tabelu možemo koristiti i iz Core koda bez ORM `Session`-a.
- Transakcija daje atomarnost za grupu upisa; SQLAlchemy 2.0 ne potvrđuje ih automatski.

## Vežbe za playground

Dodaj novi fajl u `playground/sqlalchemy_2/` i radi u postojećem root `.venv`-u.

1. Napravi `MetaData` i `Table` sa `id`, `name` i opcionim `fullname` kolonama.
2. Napravi `Base(DeclarativeBase)` i ekvivalentnu klasu `User`; uporedi `User.__table__` sa ručno deklarisanim tabelama.
3. Promeni `fullname` iz `Mapped[str | None]` u `Mapped[str]`; uporedi zaključeni `nullable` metadata.
4. Dodaj `MappedAsDataclass` i `init=False` na primarni ključ. Napravi objekat pre upisa i proveri ID i `repr`.
5. Dodaj `default_factory` za vreme kreiranja. Napravi dva objekta i proveri da je factory pozvan za svaki objekat posebno.
6. Sastavi `select(User).where(User.name == "spongebob")` i posebno Core iskaz nad `User.__table__`. Za sada samo ispiši/kompajliraj iskaze; njihovo izvršavanje dolazi u narednim lekcijama.
