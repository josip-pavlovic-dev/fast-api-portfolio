# 03: SQLAlchemy model kao klasa i tabela

## Jedna definicija ima dva pogleda

U SQLAlchemy tipizovanom deklarativnom ORM-u klasa istovremeno služi kao:

1. Python klasa od koje pravimo ORM instance;
2. deklaracija koju SQLAlchemy mapira na tabelu i njene kolone.

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

Definicija klase sama po sebi pravi Python metadata i ORM mapper; ne mora istog trenutka da izvrši SQL niti da napravi tabelu u bazi. Kreiranje fizičke šeme obrađuje se posebno u delu kursa o metadata/DDL.

## `DeclarativeBase` je bazna klasa

```python
class Base(DeclarativeBase):
    pass
```

SQLAlchemy-jeva deklarativna infrastruktura prati klase koje nasleđuju `Base`. Kada se izvrši definicija:

```python
class Item(Base):
    __tablename__ = "items"
    ...
```

SQLAlchemy vidi `__tablename__`, anotacije i `mapped_column()` konfiguraciju, pa registruje `Item` kao mapirani ORM model. Zato `Base` nije samo obična Python klasa sa zajedničkim metodama: ona nosi registry i metadata koje deklarativni modeli dele.

Možemo pregledati ono što je SQLAlchemy izgradio:

```python
Item.__table__
Base.metadata.tables["items"]
```

`Item.__table__` je SQLAlchemy `Table` objekat koji odgovara ORM klasi. `Base.metadata.tables` je mapa registrovanih tabela prema njihovim SQL imenima.

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

Anotacija `str | None` govori da Python atribut može imati tekst ili `None`. U bazi odgovarajuća kolona dozvoljava SQL `NULL`. To ipak ne znači da prazan tekst `""` automatski postaje zabranjen; prazninu bi validiralo zasebno pravilo.

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

print(Item.name)
print(item.name)
```

- `Item.name` je class-level SQLAlchemy descriptor/instrumentisan atribut. On predstavlja kolonu u SQL izrazima i nosi metadata kao što su tip i izvorna tabela.
- `item.name` je vrednost atributa na konkretnoj instanci, ovde `"Sveska"`.

Na primer:

```python
statement = select(Item.name).where(Item.name == "Sveska")
```

`Item.name == "Sveska"` gradi SQL uslov; to nije Python `bool` provera nad konkretnom instancom. Nasuprot tome, `item.name == "Sveska"` poredi dve Python vrednosti.

Ovaj dualni class/instance pogled je jedan od ključnih obrazaca ORM-a: klasa daje strukturu za SQL, a instance drže podatke pojedinačnih redova.

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
