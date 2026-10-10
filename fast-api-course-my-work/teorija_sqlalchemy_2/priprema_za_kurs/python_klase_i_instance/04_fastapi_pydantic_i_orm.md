# 04: FastAPI, Pydantic šeme i ORM instance

## Tri klase, tri odgovornosti

U web aplikaciji isti logički podatak može proći kroz više različitih Python klasa. Te klase nisu duplikati sa istom ulogom:

| Klasa                 | Primer       | Uloga                                                             |
| --------------------- | ------------ | ----------------------------------------------------------------- |
| Pydantic ulazna šema  | `ItemCreate` | Opisuje i validira JSON podatke koje klijent šalje.               |
| SQLAlchemy ORM model  | `Item`       | Opisuje mapiranu tabelu i ORM instance koje predstavljaju redove. |
| Pydantic izlazna šema | `ItemOut`    | Opisuje i validira podatke koje API vraća klijentu.               |

Pydantic klasa nasleđuje `BaseModel`. SQLAlchemy ORM model nasleđuje deklarativni `Base`. Ne treba ih spajati u jednu klasu samo zato što oba koriste class sintaksu.

## Pydantic šema je ugovor podataka, ne tabela

Primer ulazne šeme u Pydantic-u 2:

```python
from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
```

Pravljenje instance validira primljene vrednosti:

```python
payload = ItemCreate(
    name="Sveska",
    description="Karirana sveska",
)

assert payload.name == "Sveska"
assert payload.model_dump() == {
    "name": "Sveska",
    "description": "Karirana sveska",
}
```

`ItemCreate` nije ORM model i ne opisuje SQL tabelu. To je klasa podataka/API ugovor, a `payload` je validirana Pydantic instanca.

Ako pošaljemo pogrešan tip ili nedostaje obavezno polje, Pydantic prijavljuje validacionu grešku pre nego što kod rute nastavi da obrađuje podatke. Ta validacija je različita od SQLAlchemy `Mapped[...]` tipa: `Mapped[str]` tipizuje ORM atribut, ali sama anotacija nije Pydantic-style ulazna validacija.

## SQLAlchemy ORM model opisuje tabelu i ORM objekte

Model za istu stvar može izgledati ovako:

```python
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

`Item` je ORM klasa; `item = Item(name="Sveska", description=None)` bi bio ORM objekat. `Item.name` je class-level SQLAlchemy atribut za mapiranu kolonu, a `item.name` je vrednost instance.

Pydantic i ORM klase mogu imati polja istih imena, ali se koriste za različite stvari:

```text
JSON tela zahteva -> ItemCreate instanca -> ORM Item instanca -> ItemOut -> JSON odgovor
```

Dodavanje ORM objekta u sesiju i upis u bazu slede kasnije u praktičnom toku; ovde nam je fokus uloga klasa i instanci.

## Ulazna i izlazna šema nisu nužno ista

Klijent pri kreiranju resursa obično ne šalje ID koji će baza dodeliti. Zato ulazna šema može izostaviti `id`, dok izlazna šema prikazuje ID:

```python
from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class ItemOut(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
```

Ove dve klase opisuju različite granice aplikacije:

- `ItemCreate` sadrži ono što je dozvoljeno klijentu da pošalje;
- `ItemOut` sadrži ono što API obećava da vraća.

To što obe imaju `name` ne znači da moraju da budu ista klasa. U realnoj aplikaciji ulaz i izlaz često imaju različite dozvole, obavezna polja ili strukture.

## Kako FastAPI koristi Pydantic klasu

FastAPI koristi type annotation parametra rute da zna koji model treba da napravi od JSON tela zahteva. `response_model` određuje strukturu izlaznog odgovora:

```python
from fastapi import FastAPI

app = FastAPI()


@app.post("/items", response_model=ItemOut)
def create_item(payload: ItemCreate) -> ItemOut:
    return ItemOut(
        id=1,
        name=payload.name,
        description=payload.description,
    )
```

FastAPI tokom request-a napravi `ItemCreate` instancu iz JSON-a. Funkcija dobija tu instancu, ne običan dictionary. Pri vraćanju vrednosti, FastAPI proveri/serializuje odgovor prema `ItemOut` ugovoru.

`id=1` je ovde samo vežbovni primer, da ruta pokaže tipove. U stvarnoj aplikaciji bi ID obično stigao iz ORM objekta posle upisa u bazu; taj deo pripada kasnijim lekcijama.

## Pretvaranje ORM objekta u Pydantic odgovor

Pydantic 2 može da napravi šemu čitajući atribute Python objekta kada je uključeno `from_attributes=True`:

```python
orm_item = Item(id=1, name="Sveska", description="Karirana sveska")
response_item = ItemOut.model_validate(orm_item)

assert response_item.id == 1
assert response_item.name == "Sveska"
```

Ovaj primer je demonstracija granice između klasa. `orm_item` je SQLAlchemy instanca; `response_item` je Pydantic instanca. Pydantic je pročitao vrednosti atributa i napravio drugi objekat sa izlaznim API ugovorom. Nijedna od tih klasa zbog same konverzije ne postaje druga klasa.

U FastAPI-ju `response_model=ItemOut` često omogućava FastAPI-ju da serializuje ORM objekat u izlaznu šemu, ali ORM objekat mora imati dostupne atribute koje šema zahteva. Ako ORM polje još nije dobilo ID iz baze, ne može se napraviti izlazni model koji zahteva `id: int` bez te vrednosti.

## Kako da razmišljaš o tipu parametra rute

```python
def create_item(payload: ItemCreate):
    ...
```

- `ItemCreate` je klasa koja opisuje validaciju i oblik zahteva.
- `payload` je ime parametra funkcije.
- Kada FastAPI pozove funkciju, `payload` je instanca klase `ItemCreate` napravljena iz zahteva.
- `payload.name` je Python vrednost te instance.

Ovo je ista osnovna veza klasa–instanca kao u Python-u, samo FastAPI automatizuje pravljenje Pydantic instance iz HTTP podataka.

## Granica prema narednim oblastima

Ova priprema ne obrađuje SQL `INSERT`, transakcije, dependency koji obezbeđuje `Session`, niti CRUD implementaciju. Za sada treba razumeti samo ko su klase i instance i koja klasa ima koju odgovornost. Te teme dolaze u SQL i transakcijskim pripremama i kasnijim FastAPI lekcijama.
