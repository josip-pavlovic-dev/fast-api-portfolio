# 01: Klase, instance i `self`

> U ovom poglavlju ćemo naučiti osnovne koncepte klasa i instanci u Pythonu, što je ključno za razumevanje kako SQLAlchemy i FastAPI rade sa objektima.

## Zašto je ovo važno za SQLAlchemy i FastAPI?

Oba alata koriste `Python klase`, ali im daju različite uloge:

- `SQLAlchemy ORM klasa` je Python klasa `mapirana` na tabelu ili drugi relacioni izvor (npr. baza podataka). Njeni `mapirani atributi` opisuju kolone, a `mapiranje` može da definiše i veze i ograničenja (npr. `ForeignKey`, `UniqueConstraint`, `CheckConstraint` itd.).
- `FastAPI` koristi `Pydantic modele` za opisivanje i validaciju strukturisanih podataka, na primer tela HTTP zahteva (`JSON` format) i podataka odgovora (takođe u `JSON` formatu).
- Ne predstavljaju svi ulazni podaci `Pydantic model`: putanje (`Path` parametri) i query parametri (`Query` parametri), na primer, mogu biti obične tipizovane vrednosti (`int`, `str`, `float` itd.).
- `Uvicorn` je `ASGI server` koji prima `HTTP zahteve` i poziva `FastAPI` aplikaciju preko `ASGI` interfejsa. `FastAPI` aplikacija je `ASGI aplikacija`, a ne server. Telo odgovora API-ja (`response body`) često je `JSON`, ali može biti i drugog formata (npr. `HTML`, `XML` itd.).
- Python kod `endpoint-a` može da radi sa običnim Python vrednostima, Pydantic instancama i SQLAlchemy ORM instancama, u zavisnosti od zadatka. Potrebno je samo iznad Python funkcije preko dekoratora (`@app.get`, `@app.post` itd.) definisati kako se parametri dobijaju i kako se vraćaju.
- `Instanca` je `konkretan` objekat sa `trenutnim` vrednostima. `ORM instanca` može predstavljati mapirani entitet odnosno `red u bazi`, ali može biti i `nova`, još neupisana instanca. `Pydantic instanca` sadrži strukturisane podatke (`fields` i njihove vrednosti). Ona sama `nije` HTTP zahtev (`request`) niti odgovor (`response`).

Pre rada sa ORM-om zato je važno jasno razlikovati klasu od instance.

---

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

---

## Kako nastaje instanca?

Kada pozovemo ime klase kao funkciju, Python napravi objekat te klase uz pomoć `__new__` metode koja se automatski poziva i koja vraća novu instancu a zatim se pokrene inicijalizator `__init__` koji definiše atributе (`self.title`, `self.pages`) i postavlja početne vrednosti instance (npr. konstante ili prosleđene argumente).

```python
book = Book("Python osnove", 320)
```

Pojednostavljeno, desi se sledeće:

Primer instanciranja klase `Book`:

```python
book = Book("Python osnove", 320)
```

1. Python napravi novu instancu tipa `Book` preko `Book.__new__` metode. Inicijalizator `__init__` još nije pozvan. Pozicija izraza sa leve strane (`book = ...`) još nije relevantna i tek nakon što `__init__` završi, izraz sa leve strane dobija vrednost.
2. Python pozove `Book.__init__(book, "Python osnove", 320)` i automatski mu prosledi tu instancu kao `self` argument, zajedno sa ostalim prosleđenim argumentima (`"Python osnove"`, `320`).
3. `__init__` početno postavi `self.title` i `self.pages`.
4. Tek na kraju se izrazu sa leve strane tj. promenljivoj `book`(`book = Book("Python osnove", 320)`) dodeli gotova instanca klase `Book`. I tek tada promenljiva `book` postaje referenca na tu instancu.

NAPOMENA: `__init__` inicijalizuje već napravljeni objekat; sam po sebi ne vraća objekat. U takvom tipičnom kodu njegov povratni tip je `None`. Objekat se kreira i vraća u `__init__` iz `__new__` metode, tako da je uloga `__init__`-a samo `postavljanje početnog stanja` već kreirane instance.

---

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

Kada pozovemo `book.description()`, Python automatski prosleđuje `book` kao prvi argument metode. Zato je potpis metode definisan kao `description(self)`, a poziv ne mora eksplicitno da prosleđuje `self` argument. Nepravilno bi bilo pisati `book.description(book)` ali je pravilno pisati samo `book.description()` ili `Book.description(book)`.

Kao približan mentalni model, `book.description()` se ponaša kao `Book.description(book)`. U praksi koristi se prvi oblik. `self` je konvencionalno ime prvog parametra instance metode; nije posebna Python ključna reč.

Unutar metode `self.title` znači „pročitaj atribut `title` sa instance nad kojom je metoda pozvana“. Ako pozovemo:

```python
another_book = Book("SQLAlchemy vodič", 240)
print(another_book.description())
```

ista metoda radi nad drugim objektom jer je njen `self` sada `another_book`.

---

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

---

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

Static type checker-i (npr. `mypy` ili `pyright`) mogu ovo označiti. Na primer, `mypy` će prijaviti grešku ako se pokuša proslediti `string` umesto `integera` za `pages`. Ovi checker-i rade statičku analizu koda i ne utiču na runtime ponašanje.

Za `runtime validaciju` koriste se eksplicitna provera (npr. `isinstance`, `assert`, `type`, `len`, ...), Pydantic (`BaseModel`) ili druga validaciona logika.

---

## Referenca, identitet i jednakost

Promenljiva sadrži `referencu` ka objektu. Dve promenljive mogu pokazivati na isti objekat:

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

- `is` proverava da li su dve reference isti objekat, isti identitet.
- `==` proverava jednakost prema pravilima klase npr. poređenje po vrednostima atributa.

NAPOMENA: Ako klasa `ne` implementira `__eq__`, podrazumevano poređenje korisničkih objekata uglavnom se ponaša kao `poređenje po identitetu`. `Dataclass` i `Pydantic` klase mogu definisati poređenje `po vrednostima`, zato uzmi u obzir vrstu klase.

---

## Kada koristimo ove pojmove u SQLAlchemy-ju?

U ORM kodu važno je razlikovati klasu i instancu:

```python
class User(Base):
    ...


user = User(name="sandy")
```

- `User` je klasa koju SQLAlchemy mapira na tabelu.
- `user` je konkretna instanca sa vrednostima atributa.
- `user.name` čita vrednost na instanci.
- `User.name` je `class-level` SQLAlchemy atribut koji može da `predstavlja kolonu u SQL izrazu`.

Ovaj poslednji slučaj se razlikuje od obične Python klase. SQLAlchemy instrumentiše `class-level atribut` da bi isti model služio i za `ORM objekte` i za `sastavljanje SQL izraza`. To detaljno obrađuje [lekcija o SQLAlchemy modelima](03_sqlalchemy_modeli_kao_klase.md).

---

## Česte zabune

### Klasa i instanca nisu zamenljive

U običnoj Python klasi `title` nije automatski definisan na klasi samo zato što se u `__init__`-u pojavljuje `self.title`. Atribut `title` se pravi kada kreiramo instancu sa argumentima (`Book("Python osnove", 320)`). SQLAlchemy kasnije dodaje posebno `class-level mapped` ponašanje svojim descriptor-ima. Pod `class-level mapped` ponašanjem podrazumeva se da `atribut` na klasi može da predstavlja `kolonu` u SQL izrazu, dok instanca i dalje čuva konkretne vrednosti (npr. `book.title`).

---

### Promenljiva nije objekat

Promenljiva `book` je ime (`pointer`, `identifier`) koje referencira (pokazuje) na instancu objekta. Više promenljivih može referencirati isti objekat.

---

### Metoda koristi instancu preko `self`

Kada pozovemo `book.description()`, Python automatski veže `book` za `self`. Zato ista metoda može pristupati podacima različitih instanci.

---

## Sažetak

- Klasa definiše strukturu i ponašanje; instanca je konkretan objekat te klase.
- Poziv `Book(...)` pravi instancu i pokreće `__init__`.
- `self` označava instancu na kojoj metoda radi.
- `self.attribute` čuva ili čita stanje te instance.
- Tip anotacije pomaže alatima, ali običan Python ne sprovodi automatsku runtime validaciju.
- `is` proverava identitet objekta (`id(self)`)
- `==` zavisi od pravila jednakosti klase (`__eq__`). Ako klasa ne definiše `__eq__`, podrazumevano se ponaša kao `is` a ako definiše `__eq__`, koristi se to pravilo.
- U SQLAlchemy-ju klasa je `ORM model`, a `instance` su `konkretni objekti` koji mogu predstavljati redove.

---
