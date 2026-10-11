# 02: Atributi, metode i nasleđivanje

## Instancni (instance) atributi: podaci jednog objekta

Atributi su imena preko kojih čitamo i menjamo podatke ili ponašanje objekta. Svaka instanca je poseban objekat sa sopstvenim stanjem. Atributi upisani preko `self` u `__init__` obično se nazivaju `instance attributes`:

```python
class Product:
    def __init__(self, name: str, price: int) -> None:
        self.name = name # Instance attribute
        self.price = price


book = Product("Python osnove", 2500)
phone = Product("Telefon", 80000)

assert book.name == "Python osnove"
assert phone.price == 80000
```

Svaka instanca je poseban Python objekat sa sopstvenim identitetom. Za dve instance koje istovremeno postoje, `id()` vraća različite vrednosti, ali `id()` nije prenosiva garancija fizičke memorijske adrese. U ovom primeru `name` i `price` su instance atributi, pa promena `book.price` ne menja `phone.price`. To nije univerzalno pravilo za sve podatke: instance mogu deliti atribute klase ili reference na isti promenljivi objekat, pa promena tog objekta može biti vidljiva kroz obe instance:

```python
book.price = 2700
assert phone.price == 80000
```

---

### Dve instance mogu da dele istu listu

Instance su različiti objekti, ali njihovi atributi mogu da upućuju na isti promenljivi objekat. To se, na primer, dešava kada isto list objekat prosledimo konstruktoru dve instance, a konstruktor ga sačuva bez kopiranja:

```python
class TaggedProduct:
    def __init__(self, name: str, tags: list[str]) -> None:
        self.name = name
        self.tags = tags


shared_tags: list[str] = []
book_with_tags = TaggedProduct("Python osnove", shared_tags)
phone_with_tags = TaggedProduct("Telefon", shared_tags)

book_with_tags.tags.append("popularno")
assert phone_with_tags.tags == ["popularno"]

book_with_tags.tags = ["programiranje"]
assert phone_with_tags.tags == ["popularno"]
```

Poziv `append()` menja zajedničku listu, pa se izmena vidi kroz obe instance. Dodela nove liste menja samo `book_with_tags.tags`; atribut `phone_with_tags.tags` i dalje upućuje na staru listu. Ako svaka instanca treba da dobije svoju listu, konstruktor može da je kopira pomoću `self.tags = list(tags)`.

U jednostavnim Python klasama instance atributi se često čuvaju u `objekat.__dict__`. To je koristan model za razumevanje, ali ne mora biti tačan za svaku klasu: `slots`, `properties` i `descriptors` mogu menjati `način` skladištenja ili pristupa.

---

## Metode i `self`

Metoda je funkcija definisana u klasi i pozvana preko instance:

```python
class Product:
    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price

    def describe(self) -> str: # Metoda instance, koristi `self`
        return f"{self.name}: {self.price} RSD"


book = Product("Python osnove", 2500)
print(book.describe())
```

Pri pozivu `book.describe()` Python automatski prosledi `book` kao prvi argument metode. Zato je običaj da taj argument zovemo `self`. Poziv se može zamisliti približno ovako:

```python
Product.describe(book)
```

U običnom kodu pišemo `book.describe()`, ne prosleđujemo `self` ručno. On se prosleđuje automatski preko instance (u ovom slučaju `book`). `self` nije rezervisana ključna reč, ali je standardno ime i treba ga koristiti.

`Metoda` može da `čita` stanje, `menja` stanje ili `izračuna` rezultat. U SQLAlchemy modelu vrednosti kao `product.name` su instance atributi, dok metode mogu organizovati ponašanje aplikacionog objekta.

---

## `__init__` je inicijalizator

Kada napišemo:

```python
book = Product("Python osnove", 2500)
```

Python napravi novu instancu klase `Product` preko `__new__` metode i, ako je kreiranje uspešno, potom poziva `__init__` da inicijalizuje polja te instance. Metoda `__init__` sama ne vraća instancu; njen povratni rezultat treba da bude `None`.

Tipizacija parametara pomaže čitaocu i alatima:

```python
def __init__(self, name: str, price: int) -> None:
    self.name = name
    self.price = price
```

Ali anotacija nije automatski `runtime validator`. Bez `posebne validacije` npr. `isinstance` provere, Python i dalje može dozvoliti poziv sa pogrešnim tipom:

```python
book = Product("Python osnove", "mnogo")
```

Static type checker može ovo označiti.

Za `runtime validaciju` koriste se eksplicitna provera, `Pydantic` ili druga validaciona logika (npr. `validators` u Pydantic modelima ili `__post_init__` u dataclass-ima ali to je naprednija tema).

---

## Klasa i instanca su Python objekti

Ime `Product` upućuje na objekat klase. Klasa je i sama Python objekat (uobičajeno instanca metaklase `type`), a `book = Product(...)` pravi instancu te klase. Dakle, i klasa i njena instanca jesu Python objekti, ali imaju različite uloge:

```python
BookClass = Product
book = BookClass("Python osnove", 2500)

assert isinstance(book, Product)
```

Klasa obično definiše atribute i metode dostupne svojim instancama; instanca je konkretan objekat tog tipa i može imati svoje vrednosti atributa. Kod obične instance metode, pristup preko klase i instance daje različite rezultate:

```python
Product.describe
book.describe
```

`Product.describe` daje funkciju definisanu u klasi. `book.describe` daje metodu vezanu za instancu `book`; Python automatski povezuje tu instancu sa prvim parametrom `self`.

---

## Identitet i jednakost

Dve promenljive mogu da upućuju na isti objekat:

```python
first_reference = book
assert first_reference is book
```

`is` proverava identitet: da li su to dve reference ka istom objektu. Operator `==` proverava jednakost prema pravilima klase. Ako klasa ne definiše sopstveno poređenje, podrazumevano ponašanje korisničke klase uglavnom poredi identitet; dataclass, Pydantic i ORM klase mogu definisati druga pravila.

Nemoj koristiti `is` za poređenje običnih stringova ili brojeva. Za vrednosti se tipično koristi `==`; `is None` je uobičajen i ispravan test za `None`.

Kod ORM-a je identitet posebno značajan: u jednoj `Session`-i, identity map povezuje ORM klasu i primarni ključ sa instancom koja predstavlja taj red. To ćemo koristiti u kasnijoj ORM lekciji.

---

## Atributi klase i atributi instance

Atribut klase je definisan neposredno u telu klase, a ne preko `self`:

```python
class Product:
    currency = "RSD" # Atribut klase, zajednički (default) za sve instance

    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price
```

`currency` je zajednička podrazumevana vrednost na nivou klase. `name` i `price` su vrednosti pojedinačne instance.

Pri čitanju, Python najpre traži atribut na instanci, pa zatim u klasi i njenim baznim klasama. Dodela preko instance pravi ili menja instance atribut; ne menja automatski atribut klase:

```python
book = Product("Python osnove", 2500)
phone = Product("Telefon", 80000)

book.currency = "EUR" # Ova dodela override-uje default vrednost atributa klase samo za instancu `book`
assert book.currency == "EUR"
assert phone.currency == "RSD"
assert Product.currency == "RSD"
```

Ovde je `book.currency` zasenio (`shadowed`) vrednost klase samo za instancu `book`. Oprez je naročito važan za promenljive objekte: klasa sa `items = []` bi delila istu listu između svih instanci. Za podatke pojedinačnog objekta napravi novu listu u `__init__` ili koristi odgovarajući `default_factory`.

---

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

`Student` nasleđuje metodu `introduce()` i atribut `name`, a dodaje `course`.

`super()` je funkcija koja omogućava pozivanje metoda bazne klase iz izvedene klase.

`super().__init__(name)` poziva inicijalizator bazne klase umesto da dupliramo njegov kod.

SQLAlchemy koristi ovaj princip za deklarativne modele:

```python
class Base(DeclarativeBase):
    pass


class User(Base):
    ...
```

`Base` donosi zajedničko deklarativno ponašanje i metadata registar. `User` ga nasleđuje, pa SQLAlchemy prepoznaje da treba da obradi klasu kao ORM model. To je specijalno ponašanje SQLAlchemy-ja, ne posledica nasleđivanja samog po sebi.

---

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

To je korisno za `prenos podataka`, ali `dataclass` sama po sebi `nije SQLAlchemy model` i `ne pravi tabelu`.

`SQLAlchemy` ima opcionu integraciju `MappedAsDataclass` koja dodaje `dataclass ponašanje` ORM modelu, ali nije obavezna za deklarativno mapiranje.

---

## Najvažnije za sledeću celinu

- `Product` je klasa; `book = Product(...)` je instanca.
- `self` označava instancu na kojoj se poziva metoda.
- `self.name` i `self.price` su instance atributi sa vrednostima konkretnog objekta.
- Atribut klase (npr. `Product.currency = "USD"`) je zajednički podrazumevani podatak za sve instance klase `Product`. Međutim, dodela preko instance (npr. `book.currency = "EUR"`) može da ga zaseni (`override`-uje) za tu konkretnu instancu.
- Nasleđivanje objašnjava kako SQLAlchemy modeli koriste zajednički `Base`.
- `super().__init__(...)` poziva inicijalizator bazne klase iz izvedene klase, kako ne bi duplirali kod bazne klase u izvedenoj klasi.
- Anotacija `str`/`int` dokumentuje očekivanje, ali sama po sebi `ne` validira runtime vrednost. Za validaciju je potrebno koristiti dodatne mehanizme (npr. `pydantic` ili ručnu proveru u `__init__`).

---
