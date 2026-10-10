# 02: Atributi, metode i nasleđivanje

## Instance atributi: podaci jednog objekta

Atributi su imena preko kojih čitamo i menjamo podatke ili ponašanje objekta. Atributi upisani preko `self` u `__init__` obično su instance atributi:

```python
class Product:
    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price


book = Product("Python osnove", 2500)
phone = Product("Telefon", 80000)

assert book.name == "Python osnove"
assert phone.price == 80000
```

Svaka instanca ima svoje vrednosti. Promena jedne ne menja drugu:

```python
book.price = 2700
assert phone.price == 80000
```

U jednostavnim Python klasama instance atributi se često čuvaju u `objekat.__dict__`. To je koristan model za razumevanje, ali ne mora biti tačan za svaku klasu: `slots`, properties i descriptors mogu menjati način skladištenja ili pristupa.

## Metode i `self`

Metoda je funkcija definisana u klasi i pozvana preko instance:

```python
class Product:
    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price

    def describe(self) -> str:
        return f"{self.name}: {self.price} RSD"


book = Product("Python osnove", 2500)
print(book.describe())
```

Pri pozivu `book.describe()` Python automatski prosledi `book` kao prvi argument metode. Zato je običaj da taj argument zovemo `self`. Poziv se može zamisliti približno ovako:

```python
Product.describe(book)
```

U običnom kodu pišemo `book.describe()`, ne prosleđujemo `self` ručno. `self` nije rezervisana ključna reč, ali je standardno ime i treba ga koristiti.

Metoda može da čita stanje, menja stanje ili izračuna rezultat. U SQLAlchemy modelu vrednosti kao `product.name` su instance atributi, dok metode mogu organizovati ponašanje aplikacionog objekta.

## `__init__` je inicijalizator

Kada napišemo:

```python
book = Product("Python osnove", 2500)
```

Python napravi novu instancu klase `Product`, pa pozove `__init__` da inicijalizuje njena polja. Metoda `__init__` sama ne vraća instancu; njen povratni rezultat treba da bude `None`.

Tipizacija parametara pomaže čitaocu i alatima:

```python
def __init__(self, name: str, price: int) -> None:
    self.name = name
    self.price = price
```

Ali anotacija nije automatski runtime validator. Bez posebne validacije, Python i dalje može dozvoliti poziv sa pogrešnim tipom:

```python
book = Product("Python osnove", "mnogo")
```

Static type checker može ovo označiti; za runtime validaciju koriste se eksplicitna provera, Pydantic ili druga validaciona logika.

## Klasa kao vrednost i instanca kao vrednost

Ime klase je samo po sebi Python objekat:

```python
BookClass = Product
book = BookClass("Python osnove", 2500)

assert isinstance(book, Product)
```

Klasa određuje koji atributi i metode postoje; instanca sadrži konkretne vrednosti. Kada čitamo:

```python
Product.describe
book.describe
```

prvi izraz upućuje na metodu preko klase, a drugi je metoda vezana za konkretnu instancu, pa `self` biva automatski povezan sa `book`.

## Identitet i jednakost

Dve promenljive mogu da upućuju na isti objekat:

```python
first_reference = book
assert first_reference is book
```

`is` proverava identitet: da li su to dve reference ka istom objektu. Operator `==` proverava jednakost prema pravilima klase. Ako klasa ne definiše sopstveno poređenje, podrazumevano ponašanje korisničke klase uglavnom poredi identitet; dataclass, Pydantic i ORM klase mogu definisati druga pravila.

Nemoj koristiti `is` za poređenje običnih stringova ili brojeva. Za vrednosti se tipično koristi `==`; `is None` je uobičajen i ispravan test za `None`.

Kod ORM-a je identitet posebno značajan: u jednoj `Session`-i, identity map povezuje ORM klasu i primarni ključ sa instancom koja predstavlja taj red. To ćemo koristiti u kasnijoj ORM lekciji.

## Atributi klase i atributi instance

Atribut klase je definisan neposredno u telu klase, a ne preko `self`:

```python
class Product:
    currency = "RSD"

    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price
```

`currency` je zajednička podrazumevana vrednost na nivou klase. `name` i `price` su vrednosti pojedinačne instance.

Pri čitanju, Python najpre traži atribut na instanci, pa zatim u klasi i njenim baznim klasama. Dodela preko instance pravi ili menja instance atribut; ne menja automatski atribut klase:

```python
book = Product("Python osnove", 2500)
phone = Product("Telefon", 80000)

book.currency = "EUR"
assert book.currency == "EUR"
assert phone.currency == "RSD"
assert Product.currency == "RSD"
```

Ovde je `book.currency` zasenio (`shadowed`) vrednost klase samo za instancu `book`. Oprez je naročito važan za promenljive objekte: klasa sa `items = []` bi delila istu listu između svih instanci. Za podatke pojedinačnog objekta napravi novu listu u `__init__` ili koristi odgovarajući `default_factory`.

## Nasleđivanje i bazna klasa

Nasleđivanje omogućava da klasa nasledi ponašanje druge klase:

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
```

`Student` nasleđuje metodu `introduce()` i atribut `name`, a dodaje `course`. `super().__init__(name)` poziva inicijalizator bazne klase umesto da dupliramo njegov kod.

SQLAlchemy koristi ovaj princip za deklarativne modele:

```python
class Base(DeclarativeBase):
    pass


class User(Base):
    ...
```

`Base` donosi zajedničko deklarativno ponašanje i metadata registar. `User` ga nasleđuje, pa SQLAlchemy prepoznaje da treba da obradi klasu kao ORM model. To je specijalno ponašanje SQLAlchemy-ja, ne posledica nasleđivanja samog po sebi.

## Dataclass kao automatizacija obične klase

Python `dataclass` može automatski da napravi konstruktor i prikaz objekta na osnovu deklarisanih polja:

```python
from dataclasses import dataclass


@dataclass
class Book:
    title: str
    pages: int


book = Book("Python osnove", 320)
print(book)
```

To je korisno za prenos podataka, ali dataclass sama po sebi nije SQLAlchemy model i ne pravi tabelu. SQLAlchemy ima opcionu integraciju `MappedAsDataclass`; ona dodaje dataclass ponašanje ORM modelu, ali nije obavezna za deklarativno mapiranje.

## Najvažnije za sledeću celinu

- `Product` je klasa; `book = Product(...)` je instanca.
- `self` označava instancu na kojoj se poziva metoda.
- `self.name` i `self.price` su instance atributi sa vrednostima konkretnog objekta.
- Atribut klase je zajednički podrazumevani podatak; dodela preko instance može da ga zaseni.
- Nasleđivanje objašnjava kako SQLAlchemy modeli koriste zajednički `Base`.
- Anotacija `str`/`int` dokumentuje očekivanje, ali sama po sebi ne validira runtime vrednost.
