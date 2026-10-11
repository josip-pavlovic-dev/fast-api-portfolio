# 03: SQLAlchemy model kao klasa i tabela

## Jedna definicija ima dva pogleda

U `SQLAlchemy` tipizovanom deklarativnom ORM-u `klasa` istovremeno služi kao:

1. `Python klasa` od koje pravimo `ORM instance` i definišemo ponašanje objekata kroz metode.
2. Deklaracija (`Python klasa` sa anotacijama i `mapped_column()` pozivima) koju SQLAlchemy mapira na tabelu i njene kolone.

Primer je u stilu SQLAlchemy-ja 2.0:

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

- `Base` je zajednička deklarativna bazna klasa.
- `Item` je Python klasa i ORM entitet.
- `__tablename__` navodi ime tabele u bazi.
- `id`, `name` i `description` su mapirani atributi koji opisuju kolone.
- `Base.metadata` okuplja tabele koje pripadaju toj deklarativnoj bazi.
- `MetaData()` kreira objekat koji čuva SQLAlchemy opise tabela i drugih elemenata šeme. Kada se definiše `Base`, njegov `Base.metadata` je u početku prazan; definisanje ORM modela registruje tabele u taj objekat. `Base.metadata.create_all(engine)` ne registruje tabele: ono šalje DDL za tabele koje su već registrovane.

Definisanje `Base` postavlja zajednički `registry` i `MetaData`. Kada se zatim definiše ORM klasa kao `Item`, SQLAlchemy pravi njeno mapiranje (`Mapper`) i `Table` objekat i dodaje ih u odgovarajuće registre. To se dešava u Python procesu; fizička tabela u bazi se time još ne kreira.

Definicija klase (`class Item(Base): ...`) ne kreira fizičku tabelu u bazi. Kreiranje fizičke šeme obrađuje se posebno u delu kursa o metadata/DDL.

---

## `DeclarativeBase`, `MetaData` i više tabela

`DeclarativeBase` je osnova za tipizovano deklarativno mapiranje. Modeli koji nasleđuju isti `Base` dele njegov `registry` i `metadata`: `registry` vodi ORM mapiranja, a `MetaData` čuva SQLAlchemy `Table` opise. U ovom primeru obe klase pripadaju istom `Base`, pa će obe tabele biti u `Base.metadata`.

```python
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Proizvod(Base):
    __tablename__ = "proizvodi"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    naziv: Mapped[str] = mapped_column(String(50), nullable=False)
    opis: Mapped[str | None] = mapped_column(Text, nullable=True)


class Kupac(Base):
    __tablename__ = "kupci"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    ime: Mapped[str] = mapped_column(String(50), nullable=False)
    o_sebi: Mapped[str | None] = mapped_column(Text, nullable=True)
```

Definisanje ovih klasa napravi Python objekte mapiranja i registruje dve tabele u memoriji. Samo po sebi ne izvršava `CREATE TABLE` i ne pravi fizičke tabele u bazi.

---

### Pregled `MetaData` objekta

U Jupyter-u, izraz `Base.metadata` prikazuje:

```text
MetaData()
```

To je reprezentacija objekta, a ne spisak njegovog sadržaja. Pre definisanja modela taj `MetaData` objekat je prazan; i posle definisanja modela njegova kratka reprezentacija i dalje može biti `MetaData()`. Da bismo videli tabele, pregledamo `Base.metadata.tables`.

---

### Pregled tabele `Proizvod`

Izraz `Proizvod.__table__` prikazuje `Table` objekat koji SQLAlchemy je napravio za ORM klasu:

```text
Table('proizvodi', MetaData(), Column('id', Integer(), table=<proizvodi>, primary_key=True, nullable=False), Column('naziv', String(length=50), table=<proizvodi>, nullable=False), Column('opis', Text(), table=<proizvodi>), schema=None)
```

Ovaj prikaz čitamo ovako:

- `Table('proizvodi', ...)` označava SQLAlchemy tabelu čije je ime `proizvodi`.
- `MetaData()` označava metadata objekat sa kojim je tabela povezana; obe tabele iz primera koriste isti `Base.metadata`.
- `Column('id', Integer(), ...)` opisuje kolonu `id` tipa `Integer`. `primary_key=True` označava primarni ključ, a `nullable=False` znači da kolona ne može imati SQL `NULL`. `autoincrement=True` je konfigurisan u deklaraciji, ali nije prikazan u ovom `repr`-u. Za jednu `Integer` primarnu ključnu kolonu SQLAlchemy često može da podrazumeva autoincrement i bez eksplicitne opcije.
- `Column('naziv', String(length=50), ..., nullable=False)` je tekstualna kolona sa dužinom 50 koja ne prihvata `NULL`.
- `Column('opis', Text(), ...)` je tekstualna kolona bez `nullable=False`. `nullable=True` je podrazumevana vrednost, pa je `repr` obično izostavlja; deklaracija i `Mapped[str | None]` dozvoljavaju `None`/SQL `NULL`. Prazan string `""` je i dalje tekst, ne `NULL`.
- `schema=None` znači da nije naveden poseban database schema.

U svesci, poslednji izraz `Proizvod.__table__` u ćeliji prikazuje reprezentaciju objekta. Ako napišemo `print(Proizvod.__table__)`, običan tekstualni prikaz može biti kraći, na primer `proizvodi`.

---

### Pristup istoj tabeli preko `metadata.tables`

```python
Base.metadata.tables["proizvodi"]
Proizvod.__table__ is Base.metadata.tables["proizvodi"]
```

`Base.metadata.tables` je rečniku slična mapa dostupna samo za čitanje, sa SQLAlchemy tabelama indeksiranim po njihovim imenima u bazi. Ključ `"proizvodi"` vraća tabelu `Proizvod`; to je isti `Table` objekat kao `Proizvod.__table__`, zato poređenje identiteta sa `is` daje `True`. `Table(...)` nije rečnik: to je SQLAlchemy objekat koji opisuje jednu tabelu, njene kolone i konfiguraciju.

---

### Pregled svih registrovanih tabela

```python
Base.metadata.tables
```

Za dve klase iz istog primera, prikaz sadrži obe stavke. Skraćeno, izgleda ovako:

```text
FacadeDict({
    'proizvodi': Table('proizvodi', ...),
    'kupci': Table('kupci', ...),
})
```

---

#### Šta je `FacadeDict`?

`FacadeDict` je naziv konkretne Python klase koju SQLAlchemy koristi za `Base.metadata.tables`. U verziji SQLAlchemy-ja koju koristimo, ona je podklasa ugrađenog `dict`, ali je, prema SQLAlchemy dokumentaciji izvornog tipa, „rečnik koji nije javno promenljiv“. Zato možeš da ga čitaš kao rečnik, ali ne treba direktno da dodaješ ili uklanjaš stavke iz njega.

Reč „fasada“ u imenu ne označava novu vrstu tabele niti dodatni ORM model koji treba da napraviš. Za sada je dovoljno da je razumeš kao zaštićenu, rečniku sličnu kolekciju koju SQLAlchemy izlaže za pregled svojih tabela. Ime `FacadeDict` u izlazu je tip objekta; ono što je unutar vitičastih zagrada jesu njegovi ključevi i vrednosti.

---

#### Analogija sa fasadom zgrade

U građevini, fasada je spoljašnja strana zgrade koju posmatrač vidi i koja štiti unutrašnjost. Dakle, ona ne prikazuje celu noseću konstrukciju i sve instalacije iza nje.

U `softveru` se „fasadom“ naziva `javni`, `kontrolisani` način pristupa nekom delu sistema.

Ovde je fasada (spoljašnja strana) `Base.metadata.tables`. Iz nje možeš da `pregledaš registrovane tabele kao kroz rečnik`, ali ne možeš direktno da menjaš njegov sadržaj. SQLAlchemy zadržava kontrolu nad registracijom a nove tabele dodaješ definisanjem modela na odgovarajućem `Base`-u.

Analogija se odnosi na zaštićeni (kontrolisani) pristup, ne na doslovan sloj koji prekriva fizičke tabele.

`FacadeDict` predstavlja kolekciju sličnu rečniku koju `Base.metadata.tables` vraća. Možeš je koristiti za pregled registrovanih tabela, ali ne za njihovu direktnu izmenu!

```python
tables = Base.metadata.tables

list(tables.keys())
# ['proizvodi', 'kupci']

tables["proizvodi"] is Proizvod.__table__
# True
```

Ovde je `"proizvodi"` ključ, a `Proizvod.__table__` vrednost do koje tim ključem dolazimo. Izraz sa `is` potvrđuje da mapa vraća baš isti `Table` objekat koji je dostupan preko `Proizvod.__table__`, a ne neku drugu tabelu sa sličnim sadržajem.

`Redosled prikaza` u ovom primeru `prati registraciju modela`, ali sam po sebi ne znači da su tabele povezane ili da jedna zavisi od druge. Za stvarne zavisnosti između tabela koristimo `ForeignKey`, `relationship` i druge SQLAlchemy mehanizme za definisanje veza.

Direktna javna izmena nije dozvoljena. Na primer, pokušaj `tables["nova_tabela"] = Proizvod.__table__` izaziva `TypeError: FacadeDict object is immutable`. Tabele registrujemo deklarisanjem SQLAlchemy modela na odgovarajućem `Base`-u, a ne upisivanjem u ovu mapu. Ako nam treba običan rečnik za sopstvenu obradu, možemo napraviti kopiju pomoću `dict(tables)`; izmene te kopije ne menjaju `Base.metadata` i služe samo za lokalnu upotrebu npr. za analizu ili prikaz registrovanih tabela.

NAPOMENA za Jupyter: Ako je ćelija za definisanje Base (`class Base(DeclarativeBase): pass`) ponovo pokrenuta uoči definisanja tabele `Kupac`-a, kao posledica pokretanja te ćelije nastaje novi `Base` sa novim praznim `registry`/`metadata`, i prethodno registrovane tabele više nisu dostupne.

---

## `Mapped[T]`: očekivani tip Python vrednosti i mapirani atribut

```python
name: Mapped[str] = mapped_column(String(120), nullable=False)
```

- `Mapped[str]` označava da je atribut mapiran i da se na instanci očekuje Python `str` vrednost.
- `String(120)` je SQLAlchemy tip kolone; dijalekt ga prevodi u tip konkretne baze.
- `nullable=False` traži `NOT NULL` u definiciji šeme.

`Mapped[str]` i `String(120)` nisu ista vrsta informacije: prvi deo tipizuje Python ORM atribut, a drugi opisuje SQL kolonu. SQLAlchemy često može da zaključi SQL tip i nullability iz `Mapped[...]`, ali `mapped_column()` omogućava eksplicitno navođenje dodatne konfiguracije.

Za opcioni tekst:

```python
description: Mapped[str | None] = mapped_column(
    String(500),
    nullable=True,
)
```

Anotacija `str | None` govori da Python atribut može imati tekst ili `None`. U bazi odgovarajuća kolona dozvoljava SQL `NULL`. To ipak ne znači da prazan tekst `""` automatski postaje zabranjen; prazninu bi validiralo zasebno pravilo npr. pomoću Pydantic validatora ili SQLAlchemy `CheckConstraint`.

---

## `mapped_column()` nije vrednost kolone na instanci

Kada pišemo:

```python
class Item(Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
```

poziv `mapped_column(...)` je deklarativna konfiguracija za SQLAlchemy. Ne treba ga tumačiti kao da se svakoj instanci dodeljuje isti `Column` objekat kao obična vrednost.

Posle mapiranja isti atribut ima različito ponašanje zavisno od toga da li ga čitamo preko klase ili instance:

```python
item = Item(name="Sveska", description=None)

print(Item.name) # Output: <sqlalchemy.orm.attributes.InstrumentedAttribute at 0x7186f3e551c0>
print(item.name) # Output: Sveska
```

- `Item.name` je class-level SQLAlchemy `descriptor/instrumentisan` atribut. On predstavlja `kolonu` u SQL izrazima i nosi `metadata` kao što su `tip` i `izvorna tabela`.
- `class-level` atribut je atribut koji pripada klasi, a ne pojedinačnoj instanci. U kontekstu SQLAlchemy, to je obično `descriptor/instrumentisan` atribut koji upravlja pristupom vrednostima atributa na instancama (kao što je `item.name` ili `item.description`).
- `descriptor/instrumentisan` atribut je objekat koji upravlja pristupom vrednostima atributa na instancama, omogućavajući SQLAlchemy da prati promene i sinhronizuje ih sa bazom.
- `item.name` je vrednost atributa na konkretnoj instanci, ovde `"Sveska"`.

Na primer:

```python
from sqlalchemy import select
statement = select(Item.name).where(Item.name == "Sveska")

print(statement)
# Output:
# SELECT items.name
# FROM items
# WHERE items.name = :name_1

type(statement)  # Output: <class 'sqlalchemy.sql.selectable.Select'>
```

`statement` je SQLAlchemy `Select` objekat koji opisuje upit. On se može izvršiti preko Core `Connection`-a ili ORM `Session`-a da bi se dobili rezultati (na primer, `connection.execute(statement)` ili `session.execute(statement)`).

Izvršavanje SQLAlchemy `Select` objekta preko `Connection`-a:

```python
from sqlalchemy import create_engine
# Relativna putanja se računa od trenutnog radnog direktorijuma Python procesa.
# create_engine() priprema Engine; SQLite fajl se otvara/kreira pri povezivanju.
# sqlite:///example.db i sqlite:///./example.db označavaju isti relativni fajl.
engine = create_engine("sqlite:///example.db")
with engine.connect() as connection:
    result = connection.execute(statement)
    for row in result:
        print(row)
```

---

### Relativne putanje u SQLite URL-u

Za file-based SQLite bazu, SQLAlchemy URL počinje sa `sqlite:///`, a tekst posle tog prefiksa je putanja do fajla:

- `sqlite:///baza.db` koristi relativnu putanju `baza.db`.
- `sqlite:///./baza.db` koristi relativnu putanju `./baza.db`.

**Ova dva URL-a vode do istog fajla.** `./` je eksplicitan zapis „u trenutnom direktorijumu“, ali nije neophodan kada je putanja već relativna . To su dva zapisa iste lokacije, ne dve različite vrste baze.

Putanja se računa od trenutnog radnog direktorijuma procesa odakle se iz terminala pokreće Python skripta (`Path.cwd()`), koji nije nužno direktorijum u kome se nalazi Python skripta. Na primer, ako je trenutni radni direktorijum `/home/user/projekat/app`, oba URL-a iznad vode do `/home/user/projekat/app/baza.db`. U VS Code-u, radni direktorijum zavisi od načina na koji je program pokrenut.

Srodni oblici:

- `sqlite:///../baza.db` vodi do `baza.db` u roditeljskom direktorijumu trenutnog radnog direktorijuma. U prethodnom primeru to je `/home/user/projekat/baza.db`.
- `sqlite:////home/user/baza.db` koristi apsolutnu putanju na Linux/macOS sistemu. Četvrta kosa crta započinje apsolutnu putanju `/home/user/baza.db`.

Zapis `sqlite///./baza.db` bez dvotačke posle `sqlite` nije validan SQLAlchemy URL; ispravno je `sqlite:///./baza.db`.

Ovi `URL`-ovi određuju `gde` će biti fajl baze, ali `ne kreiraju` tabele.

`create_engine()` napravi `Engine` objekat, ali sam po sebi ne uspostavlja fizičku DBAPI konekciju. `Engine` povezuje konfiguraciju, kao što su URL baze i opcije prosleđene funkciji `create_engine()`, sa dve važne komponente:

- `Dialect` poznaje posebnosti konkretne baze i DBAPI drajvera, uključujući prilagođavanje SQL-a i načina povezivanja.
- `Pool` pribavlja i upravlja DBAPI konekcijama, pa ih po potrebi može ponovo koristiti.

Kada pozovemo `engine.connect()`, dobijamo SQLAlchemy `Connection` koji pribavlja `DBAPI` konekciju iz `pool`-a.

Ako koristimo ORM `Session` povezanu sa tim `Engine`-om, `Session` pribavlja konekciju kada joj `zatreba` za SQL operaciju.

U `SQLAlchemy-ju 2.0` upite izvršavamo preko `Connection`-a ili `Session`-a, ne direktno preko `Engine`-a. `Engine` je više kao fabrički objekat za konekcije koji `pravi` i `upravlja` konekcijama, dok se `stvarni SQL upiti` izvršavaju preko `Connection`-a ili `Session`-a.

SQLite fajl (npr. `baza.db`) se otvara ili kreira kada se `konekcija prvi put uspostavi`, pod uslovom da roditeljski direktorijum već postoji i da aplikacija ima odgovarajuće dozvole za pisanje u taj direktorijum.

Kreiranje tabela je zaseban korak, na primer `Base.metadata.create_all(engine)`. Njime se fizički kreiraju tabele u bazi podataka prema definicijama ORM klasa. O tome detaljnije u narednim lekcijama.

---

## Placeholder i parametarizacija SQL upita

`placeholder` je deo SQL izraza koji sprečava direktno ubacivanje vrednosti u string upita (npr. `:name_1`), čime se `povećava bezbednost` i `smanjuje rizik` od SQL `injekcija`.

Za `ubacivanje` vrednosti u string upita koristi se parametarizacija (korišćenjem `:param_name` sintakse), gde `SQLAlchemy` automatski zamenjuje `placeholder` stvarnom vrednošću prilikom izvršavanja upita. Primer:

```python
statement = text("INSERT INTO items (name) VALUES (:name_1)")
connection.execute(statement, {"name_1": "Sveska"})
session.execute(statement, {"name_1": "Sveska"})
```

`connection.execute(statement, {"name_1": "Sveska"})` ili `session.execute(statement, {"name_1": "Sveska"})` u našim primerima, obezbeđuje sigurnost i integritet podataka time što vrednosti nisu direktno ubačene u SQL string (npr., `"INSERT INTO items (name) VALUES ('Sveska')"`) već se bezbedno prosleđuju kao parametri upita zahvaljujući SQLAlchemy parametarizaciji.

`:name_1` je placeholder za vrednost `"Sveska"` u SQL upitu. SQLAlchemy koristi ovakve parametre da bi bezbedno ubacivao vrednosti u upite, sprečavajući SQL injekcije. Kada se upit izvrši, SQLAlchemy će zameniti `:name_1` stvarnom vrednošću.

`Item.name == "Sveska"` gradi SQL uslov; to nije Python `bool` provera nad konkretnom instancom. Nasuprot tome, `item.name == "Sveska"` poredi dve Python vrednosti.

Dualni `class/instance` pogled je jedan od ključnih obrazaca ORM-a:

1. `klasa` daje strukturu za SQL tabelu.
2. `Instanca` drže podatke pojedinačnog reda tabele, ne prave novu tabelu. Ako imamo više instanci iste ORM klase, svaka će predstavljati jedan red u istoj tabeli.

---

## Konstruktor i ORM instanca

Deklarativni ORM model bez dataclass integracije i dalje može da se pravi kao Python objekat pomoću `imenovanih` (`keyword`) mapiranih argumenata (npr. `name="Sveska", description="Karirana sveska"`). Pozivanje konstruktora (`Item(...)`) kreira se nova instanca ORM klase `Item`, ali se time **ne** upisuje automatski red u bazu. Da bi se upisao red u bazu, potrebno je dodati instancu u sesiju i izvršiti commit (`session.add(item); session.commit()`).

```python
item = Item(
    name="Sveska",
    description="Karirana sveska",
)
```

Posle pravljenja instance `item.name` i `item.description` su vrednosti u Python objektu `item`. To samo po sebi ne znači da je tabela napravljena niti da je red upisan. U ovoj pripremi pratimo samo `klase` i `instance`.

NAPOMENA: `Upis u bazu` pripada kasnijem SQLAlchemy gradivu!

---

## Primarni ključ i automatsko generisanje ID-a

Kod deklaracije `id: Mapped[int] = mapped_column(Integer, primary_key=True)`, `Mapped[int]` označava očekivani Python tip mapirane vrednosti. U SQLAlchemy 2.0 tipizovanom deklarativnom mapiranju anotacija bez `None` obično vodi do `nullable=False`; u ovom primeru primarni ključ je kolona koja ne prihvata SQL `NULL`.

Anotacija je tipna i mapirajuća informacija, a ne početna vrednost niti runtime provera. Ona zato ne garantuje da će atribut imati ceo broj čim Python instancu napravimo. Ako ID treba da generiše baza, nova instanca ga još ne zna: `item.id` može privremeno biti `None`, iako kolona sačuvanog reda u bazi mora biti `NOT NULL`.

---

### Kada se generisani ID pojavi?

Za uobičajeni automatski generisan celobrojni primarni ključ tok je sledeći:

1. `item = Item(...)` napravi Python ORM objekat. Red još nije poslat bazi, pa automatski generisani ID još nije dodeljen objektu.
2. `session.add(item)` registruje novu instancu kao objekat za upis. Sam poziv obično ne šalje `INSERT`, pa je `item.id` i dalje `None`.
3. `session.flush()` šalje `INSERT` u tekućoj transakciji. Ako ID generiše baza, baza proizvede vrednost, a SQLAlchemy je backend-specifičnim mehanizmom preuzme i postavi na `item.id`. `flush()` šalje SQL, ali ne potvrđuje transakciju.
4. `session.commit()` prvo flush-uje izmene koje još nisu poslate, a zatim potvrđuje transakciju. Zato se generisani ID obično može pročitati posle flush-a, pre samog commit-a.

Ne moraš ručno da pozoveš `session.flush()` da bi se on desio: Session može automatski da flush-uje pre određenih upita, a `commit()` flush-uje pending izmene pre potvrđivanja. ID se dodeljuje kada se izvrši flush koji pošalje odgovarajući `INSERT`, ne tek zato što je pozvan `add()` ili `commit()`.

---

### Ručni ID i Python `default`

Ako konstruktoru prosledimo vrednost, na primer `Item(id=7, ...)`, instanca zna ID odmah. Isto važi ako naš Python kod izračuna ID i dodeli ga atributu pre flush-a.

To ne treba mešati sa SQLAlchemy opcijom `default=neka_funkcija`. Takav client-side default se obično poziva kada SQLAlchemy priprema ili izvršava `INSERT`, tokom flush-a, a ne automatski prilikom pravljenja instance. Zato izraz „ID generiše Python“ sam po sebi ne govori da li će vrednost biti poznata pre flush-a; bitno je kada je vrednost izračunata i upisana na instancu.

Ukratko: `None` je moguće privremeno stanje ORM objekta pre `INSERT`-a i ne znači da sačuvani primarni ključ dozvoljava SQL `NULL`. U primeru sa SQLite-om, `item.id` je `None` pri pravljenju instance i posle `session.add(item)`, a posle uspešnog `flush()` može, na primer, biti `1`.

---

## Klasa kao izvor kolone u Core izrazu

ORM klasa može se koristiti za Core SQL izraze čak i kada ne radimo sa ORM `Session` objektima:

```python
from sqlalchemy import select

core_statement = select(Item.name)
```

`Item.name` klasi daje SQLAlchemy-ju informaciju o koloni, tipu i tabeli. Ako iskaz izvršimo preko Core `Connection`-a, dobijamo Core `Row` rezultate; ako `select(Item)` izvršimo preko ORM `Session`-a, možemo dobiti ORM `Item` instance. Klasa sama po sebi ne nameće ORM način izvršavanja.

---

## Strani ključna kolona i relationship atribut nisu isto

Primer pretpostavlja da je `Base` već definisan kao `DeclarativeBase` u prethodnom delu lekcije. Jedan artikal pripada jednoj kategoriji, a više artikala može pripadati istoj kategoriji:

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Kategorija(Base):
    __tablename__ = "kategorije"

    kategorija_id: Mapped[int] = mapped_column(primary_key=True)
    naziv: Mapped[str] = mapped_column(String(50), nullable=False)


class Artikal(Base):
    __tablename__ = "artikli"

    artikal_id: Mapped[int] = mapped_column(primary_key=True)
    naziv: Mapped[str] = mapped_column(String(100), nullable=False)
    kategorija_id: Mapped[int] = mapped_column(
        ForeignKey("kategorije.kategorija_id"),
        nullable=False,
    )
    kategorija: Mapped["Kategorija"] = relationship()
```

- `Kategorija.kategorija_id` je primarni ključ i fizička kolona tabele `kategorije`.
- `Artikal.kategorija_id` je fizička kolona tabele `artikli`. `ForeignKey("kategorije.kategorija_id")` kaže da njena vrednost referencira primarni ključ kategorije. String se piše u obliku `"ime_tabele.ime_kolone"`; ovde se ne referencira ista tabela iz koje dolazi kolona.
- `nullable=False` znači da svaki sačuvani artikal mora imati kategoriju. Više redova u `artikli` može sadržati isti `kategorija_id`, pa više artikala može pripadati jednoj kategoriji.
- `Artikal.kategorija` je ORM `relationship` atribut, a ne fizička SQL kolona. Na klasi je to SQLAlchemy instrumentisan atribut; na konkretnoj instanci, na primer `artikal.kategorija`, pristup vraća povezani `Kategorija` objekat. SQLAlchemy koristi strani ključ da zna kako da pronađe taj objekat.

Dakle, `ForeignKey` definiše vezu na nivou šeme baze, dok `relationship()` definiše ORM navigaciju između Python objekata. U ovom primeru prethodni zapis sa `ForeignKey("kategorije.kategorija_id")` unutar same klase `Kategorija` bi bio samoreferentan i ne bi predstavljao vezu artikla sa kategorijom.

Detaljno modelovanje stranih ključeva i veza pripada kasnijim lekcijama.

---

## Dataclass integracija je opcionalna

`MappedAsDataclass` uključuje Python `dataclass` ponašanje za SQLAlchemy ORM modele. Najčešće se postavlja kao bazna klasa pre `DeclarativeBase`:

```python
from dataclasses import is_dataclass

from sqlalchemy import JSON, Integer, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, Session, mapped_column


class DataclassBase(MappedAsDataclass, DeclarativeBase):
    pass

class DataclassArtikal(DataclassBase):
    __tablename__ = "dataclass_artikli"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    naziv: Mapped[str] = mapped_column(String(100))
    oznake: Mapped[list[str]] = mapped_column(JSON, default_factory=list)
    status: Mapped[str] = mapped_column(String(20), default="novo")
    poreklo: Mapped[str] = mapped_column(
        String(20),
        init=False,
        server_default=text("'baza'"),
    )
    sifra_za_upis: Mapped[int] = mapped_column(
        Integer,
        init=False,
        insert_default=123,
    )


prvi = DataclassArtikal(naziv="Knjiga")
drugi = DataclassArtikal(naziv="Sveska")
prvi.oznake.append("poklon")

print(is_dataclass(DataclassArtikal))
print(prvi)
print(prvi.oznake, drugi.oznake)
print(prvi.id, prvi.poreklo, prvi.sifra_za_upis)

engine = create_engine("sqlite://")
DataclassBase.metadata.create_all(engine)

with Session(engine) as session:
    session.add(prvi)
    session.flush()
    print(prvi.id, prvi.poreklo, prvi.sifra_za_upis)
    session.rollback()
```

Očekivani izlaz u ovom SQLite primeru je:

```text
True
DataclassArtikal(id=None, naziv='Knjiga', oznake=['poklon'], status='novo', poreklo=None, sifra_za_upis=None)
['poklon'] []
None None None
1 baza 123
```

Šta se ovde dešava:

- SQLAlchemy i dalje mapira klasu na tabelu i njene instance na redove. `MappedAsDataclass` samo dodaje dataclass ponašanje; ne upisuje objekat automatski u bazu.
- `is_dataclass(...)` vraća `True`. Dataclass integracija generiše konstruktor i čitljiv `repr`, pa `DataclassArtikal(naziv="Knjiga")` može da se napravi bez ručnog pisanja `__init__` metode.
- `init=False` izostavlja `id`, `poreklo` i `sifra_za_upis` iz generisanog konstruktora. U primeru se `id` generiše pri INSERT-u; njegovo `None` stanje pre flush-a je privremeno, kao što smo videli ranije u ovoj lekciji.
- `default="novo"` zadaje početnu vrednost `status` atributa koju generisani konstruktor postavlja na instanci.
- `default_factory=list` poziva `list()` za svaku novu instancu. Zato `prvi.oznake` i `drugi.oznake` predstavljaju različite liste: dodavanje oznake prvoj ne menja drugu. Ovde je `JSON` SQL tip koji omogućava da se lista sačuva kao JSON vrednost.
- `insert_default=123` je SQLAlchemy client-side podrazumevana vrednost za INSERT. Ne postavlja se pri pravljenju Python objekta, već je primenjuje SQLAlchemy pri flush-u ako INSERT nema drugu vrednost.
- `server_default=text("'baza'")` definiše podrazumevanu vrednost na strani baze. Nova instanca je pre INSERT-a nema; kada se INSERT pošalje, baza popunjava kolonu tom vrednošću. U ovom primeru SQLite i SQLAlchemy vrate tu generisanu vrednost objektu tokom flush-a.

`default_factory` i `server_default` zato nisu zamenljivi: prvi pravi početnu Python vrednost za svaku instancu, a drugi postavlja SQL podrazumevanu vrednost u definiciji kolone koju primenjuje baza. Slično tome, `default` kod dataclass mapiranja daje podrazumevanu vrednost argumentu Python konstruktora, dok `insert_default` određuje SQLAlchemy client-side default za INSERT. Ako se navede `insert_default`, on određuje `Column.default`, dok `default` i dalje može da služi kao podrazumevana vrednost konstruktora.

Dataclass integracija je opciona. Za obično ORM mapiranje `DeclarativeBase` + `Mapped[...]` + `mapped_column()` je dovoljno; `MappedAsDataclass` biramo kada nam koriste generisani dataclass konstruktor, `repr` i opcije za polja kao što su `init`, `default` i `default_factory`.

---

## Česte zamene pojmova

| Ako vidiš                    | To je                                             | Nije                                        |
| ---------------------------- | ------------------------------------------------- | ------------------------------------------- |
| `class Item(Base)`           | Python ORM klasa i mapirani entitet               | Instanca ili već izvršen SQL `CREATE TABLE` |
| `Item.name`                  | Mapirani class-level atribut/kolona za SQL izraze | Python string vrednost                      |
| `item.name`                  | Vrednost atributa konkretne instance              | Class-level SQL izraz                       |
| `Mapped[str]`                | Tipizovana deklaracija mapiranog atributa         | SQL tip poput `VARCHAR(120)`                |
| `mapped_column(String(120))` | Konfiguracija ORM kolone                          | Instanca `Item`                             |
| `Item.__table__`             | SQLAlchemy `Table` metadata objekat               | Python klasa ili fizička konekcija          |

Kada vidiš ORM model, razdvoji Python tip instance, mapirani class-level atribut i SQL konfiguraciju kolone; često su zapisani u jednoj deklaraciji, ali znače različite stvari.
