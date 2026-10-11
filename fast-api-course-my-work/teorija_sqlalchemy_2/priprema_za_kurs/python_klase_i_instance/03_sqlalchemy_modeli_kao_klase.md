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

- `Item.name` je class-level SQLAlchemy descriptor/instrumentisan atribut. On predstavlja kolonu u SQL izrazima i nosi metadata kao što su tip i izvorna tabela.
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

`placeholder` je deo SQL izraza koji sprečava direktno ubacivanje vrednosti u string upita, čime se povećava bezbednost i smanjuje rizik od SQL injekcija. Za ubacivanje vrednosti u string upita koristi se parametarizacija (korišćenjem `:param_name` sintakse), gde SQLAlchemy automatski zamenjuje placeholder stvarnom vrednošću prilikom izvršavanja upita `connection.execute(statement, {"name_1": "Sveska"})` ili `session.execute(statement, {"name_1": "Sveska"})` u našem primeru, čime se obezbeđuje sigurnost i integritet podataka.

`:name_1` je placeholder za vrednost `"Sveska"` u SQL upitu. SQLAlchemy koristi ovakve parametre da bi bezbedno ubacivao vrednosti u upite, sprečavajući SQL injekcije. Kada se upit izvrši, SQLAlchemy će zameniti `:name_1` stvarnom vrednošću.

`Item.name == "Sveska"` gradi SQL uslov; to nije Python `bool` provera nad konkretnom instancom. Nasuprot tome, `item.name == "Sveska"` poredi dve Python vrednosti.

Dualni `class/instance` pogled je jedan od ključnih obrazaca ORM-a:

1. `klasa` daje strukturu za SQL tabelu.

2. `Instanca` drže podatke pojedinačnog reda tabele, ne prave novu tabelu. Ako imamo više instanci iste ORM klase, svaka će predstavljati jedan red u istoj tabeli.

---

## Konstruktor i ORM instanca

Deklarativni ORM model bez dataclass integracije i dalje može da se pravi kao Python objekat pomoću imenovanih mapiranih argumenata:

```python
item = Item(
    name="Sveska",
    description="Karirana sveska",
)
```

Posle pravljenja `item.name` i `item.description` su vrednosti u Python objektu. To samo po sebi ne znači da je tabela napravljena niti da je red upisan. U ovoj pripremi pratimo samo klase i instance; upis u bazu pripada kasnijem SQLAlchemy gradivu.

Primarni ključ često generiše baza. Zbog toga nova instanca može pre upisa imati `item.id is None`, iako je anotacija atributa `Mapped[int]`. Anotacija opisuje tip mapirane vrednosti kada je ID dodeljen; ne znači da Python objekat automatski zna budući ID.

## Klasa kao izvor kolone u Core izrazu

ORM klasa može se koristiti za Core SQL izraze čak i kada ne radimo sa ORM `Session` objektima:

```python
from sqlalchemy import select

core_statement = select(Item.name)
```

`Item.name` klasi daje SQLAlchemy-ju informaciju o koloni, tipu i tabeli. Ako iskaz izvršimo preko Core `Connection`-a, dobijamo Core `Row` rezultate; ako `select(Item)` izvršimo preko ORM `Session`-a, možemo dobiti ORM `Item` instance. Klasa sama po sebi ne nameće ORM način izvršavanja.

## Strani ključna kolona i relationship atribut nisu isto

U SQLAlchemy modelima često se sreću oba ova atributa:

```python
category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
category: Mapped["Category"] = relationship()
```

- `category_id` je mapirana SQL kolona: čuva ključ koji referencira drugi red.
- `category` je ORM relationship atribut: omogućava navigaciju kroz povezane Python objekte.

Oba su atributi klase i SQLAlchemy ih instrumentiše, ali samo `category_id` odgovara fizičkoj koloni. `relationship()` ne dodaje sam po sebi kolonu u tabelu. Detaljno modelovanje stranih ključeva i veza pripada kasnijim lekcijama.

## Dataclass integracija je opcionalna

`MappedAsDataclass` može dodati dataclass konstruktor i `repr` ponašanje ORM modelima:

```python
class Base(MappedAsDataclass, DeclarativeBase):
    pass
```

Tada `mapped_column()` može prihvatiti dataclass opcije kao `init=False` ili `default_factory`. To je dodatni izbor, ne uslov za osnovni ORM model:

- `DeclarativeBase` + `Mapped[...]` + `mapped_column()` dovoljno je za tipizovano mapiranje;
- `MappedAsDataclass` dodaje dataclass ponašanje;
- ne treba mešati Python `default_factory` sa SQLAlchemy `server_default`.

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
