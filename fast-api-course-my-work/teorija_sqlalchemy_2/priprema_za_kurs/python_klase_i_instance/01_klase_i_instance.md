# 01: Klase, instance i `self`

## Zašto je ovo važno za SQLAlchemy i FastAPI?

Oba alata koriste Python klase, ali im daju različite uloge:

- SQLAlchemy ORM klasa opisuje mapirani entitet i strukturu njegove tabele.
- FastAPI koristi Pydantic klase da opiše podatke zahteva i odgovora.
- U oba slučaja radni kod najčešće barata instancama tih klasa.

Pre ORM-a zato treba čvrsto razlikovati klasu od instance.

## Klasa je opis, instanca je konkretan objekat

Klasa je definicija po kojoj pravimo objekte. Instanca je jedan konkretan objekat napravljen od te definicije.

```python
class Book:
    def __init__(self, title: str, pages: int) -> None:
        self.title = title
        self.pages = pages


first_book = Book("Python osnove", 320)
second_book = Book("SQLAlchemy vodič", 240)
```

Ovde su:

- `Book` klasa;
- `first_book` i `second_book` dve različite instance;
- obe instance imaju atribute `title` i `pages`, ali njihove vrednosti nisu iste.

```python
assert first_book.title == "Python osnove"
assert first_book.pages == 320
assert second_book.title == "SQLAlchemy vodič"
assert second_book.pages == 240
```

Klasa odgovara na pitanje „kakva vrsta objekta može da postoji i šta ume da radi?“. Instanca odgovara na pitanje „koji je konkretan objekat i koje vrednosti trenutno ima?“.

## Kako nastaje instanca?

Kada pozovemo ime klase kao funkciju, Python napravi objekat te klase i pokrene njegov inicijalizator:

```python
book = Book("Python osnove", 320)
```

Pojednostavljeno, desi se sledeće:

1. Python napravi novu instancu tipa `Book`.
2. Python pozove `Book.__init__` i automatski prosledi tu instancu kao `self`.
3. `__init__` početno postavi `self.title` i `self.pages`.
4. Izraz sa leve strane dodeli gotovu instancu promenljivoj `book`.

`__init__` inicijalizuje već napravljeni objekat; sam po sebi ne vraća objekat. U takvom tipičnom kodu njegov povratni tip je `None`.

## `self` označava konkretnu instancu

```python
class Book:
    def __init__(self, title: str, pages: int) -> None:
        self.title = title
        self.pages = pages

    def description(self) -> str:
        return f"{self.title} ({self.pages} strana)"


book = Book("Python osnove", 320)
print(book.description())
```

Kada pozovemo `book.description()`, Python automatski prosleđuje `book` kao prvi argument metode. Zato je potpis metode definisan kao `description(self)`, a poziv ne piše `book.description(book)`.

Kao približan mentalni model, `book.description()` se ponaša kao `Book.description(book)`. U praksi koristi se prvi oblik. `self` je konvencionalno ime prvog parametra instance metode; nije posebna Python ključna reč.

Unutar metode `self.title` znači „pročitaj atribut `title` sa instance nad kojom je metoda pozvana“. Ako pozovemo:

```python
another_book = Book("SQLAlchemy vodič", 240)
print(another_book.description())
```

ista metoda radi nad drugim objektom jer je njen `self` sada `another_book`.

## Atributi su stanje instance

`self.title = title` napravi ili izmeni atribut na konkretnoj instanci. Zato svaka knjiga može imati svoje vrednosti:

```python
first_book.pages = 321

assert first_book.pages == 321
assert second_book.pages == 240
```

`first_book` i `second_book` su različiti objekti. Menjanje instance atributa na jednom ne menja istoimeni atribut drugog objekta.

Python klase su fleksibilne: često je moguće dodati atribut instanci i van `__init__`-a:

```python
first_book.language = "sr"
```

Ipak, za čitljivost i bolju tipizaciju korisno je jasno deklarisati očekivane atribute u `__init__`-u, dataclass poljima ili SQLAlchemy `Mapped[...]` deklaracijama.

## Tipizacija nije isto što i validacija

Anotacije pokazuju očekivane tipove i pomažu čitaocu, editoru i statičkim alatima:

```python
def __init__(self, title: str, pages: int) -> None:
    self.title = title
    self.pages = pages
```

Običan Python sam po sebi ne odbija pogrešan tip samo zbog anotacije. Bez posebne validacije sledeći poziv može da se izvrši, iako je logički pogrešan:

```python
book = Book("Python osnove", "mnogo")
```

Static type checker može ovo označiti; za runtime validaciju koriste se eksplicitna provera, Pydantic ili druga validaciona logika.

## Referenca, identitet i jednakost

Promenljiva sadrži referencu ka objektu. Dve promenljive mogu pokazivati na isti objekat:

```python
original = Book("Python osnove", 320)
alias = original

assert alias is original
```

Ovde promena preko `alias` vidi se i kroz `original`, jer su to dve reference ka istoj instanci:

```python
alias.pages = 321
assert original.pages == 321
```

Ako napravimo novi objekat sa istim podacima, to je ipak druga instanca:

```python
copy = Book("Python osnove", 320)
assert copy is not original
```

- `is` proverava da li su dve reference isti objekat.
- `==` proverava jednakost prema pravilima klase.

Ako klasa ne implementira `__eq__`, podrazumevano poređenje korisničkih objekata uglavnom se ponaša kao poređenje identiteta. Dataclass i Pydantic klase mogu definisati poređenje po vrednostima, zato uzmi u obzir vrstu klase.

## Kada koristimo ove pojmove u SQLAlchemy-ju?

U ORM kodu ista razlika je direktno važna:

```python
class User(Base):
    ...


user = User(name="sandy")
```

- `User` je klasa koju SQLAlchemy mapira na tabelu.
- `user` je konkretna instanca sa vrednostima atributa.
- `user.name` čita vrednost na instanci.
- `User.name` je class-level SQLAlchemy atribut koji može da predstavlja kolonu u SQL izrazu.

Ovaj poslednji slučaj se razlikuje od obične Python klase. SQLAlchemy instrumentiše class-level atribut da bi isti model služio i za ORM objekte i za sastavljanje SQL izraza. To detaljno obrađuje [lekcija o SQLAlchemy modelima](03_sqlalchemy_modeli_kao_klase.md).

## Česte zabune

### Klasa i instanca nisu zamenljive

U običnoj Python klasi `title` nije automatski definisan na klasi samo zato što se u `__init__`-u pojavljuje `self.title`. Atribut se pravi na instanci. SQLAlchemy kasnije dodaje posebno class-level mapped ponašanje svojim descriptor-ima.

### Promenljiva nije objekat

Promenljiva `book` je ime koje referencira instancu. Više promenljivih može referencirati isti objekat.

### Metoda koristi instancu preko `self`

Kada pozovemo `book.description()`, Python automatski veže `book` za `self`. Zato ista metoda može pristupati podacima različitih instanci.

## Sažetak

- Klasa definiše strukturu i ponašanje; instanca je konkretan objekat te klase.
- Poziv `Book(...)` pravi instancu i pokreće `__init__`.
- `self` označava instancu na kojoj metoda radi.
- `self.attribute` čuva ili čita stanje te instance.
- Tip anotacije pomaže alatima, ali običan Python ne sprovodi automatsku runtime validaciju.
- `is` proverava identitet objekta; `==` zavisi od pravila jednakosti klase.
- U SQLAlchemy-ju klasa je ORM model, a instance su konkretni objekti koji mogu predstavljati redove.
