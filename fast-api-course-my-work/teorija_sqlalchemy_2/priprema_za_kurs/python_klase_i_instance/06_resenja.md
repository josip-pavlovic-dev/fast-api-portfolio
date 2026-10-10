# 06: Rešenja vežbi

Pokušaj prvo da rešiš zadatke iz [vežbi](05_vezbe.md). Rešenja prikazuju jedan mogući pristup; važnije je da umeš da objasniš razliku između klase, instance, mapiranog atributa i Pydantic šeme.

## Rešenje 1: klasa i dve instance

```python
class Book:
    def __init__(self, title: str, pages: int) -> None:
        self.title = title
        self.pages = pages


first_book = Book("Python osnove", 320)
second_book = Book("SQLAlchemy vodič", 240)

print(first_book.title, first_book.pages)
print(second_book.title, second_book.pages)

first_book.pages = 321
assert first_book.pages == 321
assert second_book.pages == 240
```

`Book` je klasa. `first_book` i `second_book` su različite instance i svaka ima sopstvene `title` i `pages` vrednosti.

## Rešenje 2: `self` i metoda

```python
class Book:
    def __init__(self, title: str, pages: int) -> None:
        self.title = title
        self.pages = pages

    def description(self) -> str:
        return f"{self.title} ({self.pages} strana)"


book = Book("Python osnove", 320)
assert book.description() == "Python osnove (320 strana)"
```

Kod `book.description()` Python automatski veže `book` kao prvi argument metode, odnosno kao `self`.

## Rešenje 3: identitet i jednakost

```python
class Book:
    def __init__(self, title: str, pages: int) -> None:
        self.title = title
        self.pages = pages


first = Book("Python osnove", 320)
second = Book("Python osnove", 320)
alias = first

assert first is alias
assert first is not second
assert first == alias
assert first != second
```

Klasa `Book` nema prilagođen `__eq__`, pa `==` koristi podrazumevano poređenje po identitetu. Dve zasebno napravljene instance nisu isti objekat, iako polja imaju iste vrednosti. Dataclass ili Pydantic klasa mogu definisati poređenje po vrednostima.

## Rešenje 4: atribut klase naspram instance

```python
class Product:
    currency = "RSD"

    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price


first = Product("Sveska", 250)
second = Product("Olovka", 80)
first.currency = "EUR"

assert first.currency == "EUR"
assert second.currency == "RSD"
assert Product.currency == "RSD"
```

Dodela `first.currency = "EUR"` postavila je instance atribut na `first`; ona nije promenila atribut klase i ne utiče na `second`.

Mutable class atribut je rizičan jer ga instance dele:

```python
class BadGroup:
    members = []
```

Bezbedniji pristup je napraviti novu listu u `__init__`:

```python
class Group:
    def __init__(self) -> None:
        self.members: list[str] = []
```

## Rešenje 5: nasleđivanje

```python
class Person:
    def __init__(self, name: str) -> None:
        self.name = name

    def introduce(self) -> str:
        return f"Ja sam {self.name}."


class Student(Person):
    def __init__(self, name: str, course: str) -> None:
        super().__init__(name)
        self.course = course


student = Student("Mina", "SQLAlchemy")
assert student.introduce() == "Ja sam Mina."
assert student.course == "SQLAlchemy"
```

`Student` nasleđuje `name` i `introduce()` od `Person`, pa `super().__init__(name)` koristi postojeću inicijalizaciju.

## Rešenje 6: deklarativni ORM model

```python
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    fullname: Mapped[str | None] = mapped_column(String(100), nullable=True)


user = User(name="sandy", fullname="Sandy Cheeks")

assert User.__tablename__ == "user_account"
assert User.__table__ is Base.metadata.tables["user_account"]
assert User.__table__.c.name.nullable is False
assert User.__table__.c.fullname.nullable is True
assert user.name == "sandy"
```

`User` je Python klasa i ORM model. `user` je instanca. Model je registrovan u `Base.metadata`, ali samo definisanje klase ne kreira fizičku tabelu u bazi.

## Rešenje 7: ORM atribut i kolona

```python
from sqlalchemy import select

statement = select(User.name).where(User.name == "sandy")
```

- `User.name` je class-level SQLAlchemy atribut koji predstavlja mapiranu kolonu i može da gradi SQL izraz.
- `user.name` je Python string vrednost konkretne instance.
- `select(User.name)` bira tu mapiranu kolonu; SQLAlchemy zna kojoj tabeli pripada.
- `Mapped[str]` tipizuje Python ORM atribut. `String(80)` je SQLAlchemy tip kolone koji dijalekt prevodi u tip baze.

## Rešenje 8: strani ključ i relationship atribut

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id"),
        nullable=False,
    )
```

`user_id` je FK kolona koja čuva `user_account.id` vrednost. Relationship bi bio zaseban ORM atribut, na primer `user: Mapped[User] = relationship()`, kojim se pristupa `User` objektu; on nije dodatna SQL kolona. U ovom zadatku relationship nije potrebno implementirati.

## Rešenje 9: Pydantic zahtev i FastAPI ruta

```python
from fastapi import FastAPI
from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str | None = None


app = FastAPI()


@app.post("/items")
def create_item(payload: ItemCreate) -> dict[str, str | None]:
    return {
        "name": payload.name,
        "description": payload.description,
    }
```

`ItemCreate` je klasa. FastAPI/Pydantic napravi `payload` instancu na osnovu JSON tela zahteva i validira njene vrednosti. Funkcija dobija instancu, ne klasu samu i ne sirovi dictionary.

## Rešenje 10: ORM objekat i izlazna šema

```python
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)


class ItemOut(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


orm_item = Item(id=1, name="Sveska", description="Karirana sveska")
response_item = ItemOut.model_validate(orm_item)

assert isinstance(orm_item, Item)
assert isinstance(response_item, ItemOut)
assert response_item.name == "Sveska"
```

`orm_item` i `response_item` su dve različite instance različitih klasa. `Item` je SQLAlchemy ORM model koji opisuje tabelu; `ItemOut` je Pydantic model koji validira i serializuje odgovor API-ja. `from_attributes=True` dozvoljava Pydantic-u da vrednosti čita sa atributa ORM objekta.
