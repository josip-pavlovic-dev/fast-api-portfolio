from types import NotImplementedType

# Vežba 1: klasa i dve instance
# Pokreni ovu skriptu da vidiš klase, instance, atribute, metode i jednakost.
# Svaki blok ispod odgovara vežbi iz 05_vezbe.md.


# Vežba 1: nezavisni instance atributi
# Svaki objekat dobija svoj title i pages u konstruktoru.
class BookVezba1BezEq:
    def __init__(self, title: str, pages: int) -> None:
        self.title = title
        self.pages = pages

    def __repr__(self) -> str:
        # __repr__ utiče na prikaz objekta, ali ne definiše kako se on poredi.
        return f"BookVezba1BezEq(title={self.title!r}, pages={self.pages!r})"


book_1_1 = BookVezba1BezEq("Python 3 Deep Dive", 120)
book_2_1 = BookVezba1BezEq("FastAPI Deep Dive 1", 250)

# Ispiši obe instance da vidiš njihove vrednosti.
print(book_1_1)
print(book_2_1)

# Menjanje instance atributa prve knjige ne menja drugu knjigu.
book_1_1.pages = 200
assert book_1_1.pages == 200
assert book_2_1.pages == 250
print("Posle izmene:", book_1_1.pages, book_2_1.pages)

# Ovde se porede dva int atributa, pa se porede njihove vrednosti.
assert book_1_1.pages != book_2_1.pages


# Vežba 2: self i metoda instance
class Book:
    def __init__(self, title: str, pages: int) -> None:
        self.title = title
        self.pages = pages

    def __repr__(self) -> str:
        return f"Book(title={self.title!r}, pages={self.pages!r})"

    def description(self) -> str:
        # self je instanca nad kojom je metoda pozvana.
        return f"{self.title} ({self.pages} strana)"


book_1_2 = Book("Python 3 Deep Dive", 120)
book_2_2 = Book("FastAPI Deep Dive 1", 250)

print(book_1_2)
print(book_2_2)

# Poziv metode preko instance veže book_1_2 za parametar self.
print(book_1_2.description())
print(book_2_2.description())

# Kao mentalni model, book_1_2.description() odgovara pozivu:
# Book.description(book_1_2)
assert book_1_2.description() == "Python 3 Deep Dive (120 strana)"


# Vežba 3: identitet i jednakost objekata
# Iste vrednosti atributa ne znače automatski da su dva objekta jednaka.

# Prvo proveri klasu bez sopstvenog __eq__.
knjiga_bez_eq_1 = BookVezba1BezEq("SQLAlchemy Deep Dive 1", 200)
knjiga_bez_eq_2 = BookVezba1BezEq("SQLAlchemy Deep Dive 1", 200)
alias_knjige_bez_eq = knjiga_bez_eq_1

# is proverava identitet: da li su reference usmerene na isti objekat.
assert knjiga_bez_eq_1 is not knjiga_bez_eq_2
assert knjiga_bez_eq_1 is alias_knjige_bez_eq

# title je str, a pages je int; njihovi == operatori porede vrednosti.
assert knjiga_bez_eq_1.title == knjiga_bez_eq_2.title
assert knjiga_bez_eq_1.pages == knjiga_bez_eq_2.pages

# Klasa nije definisala __eq__, pa se == za ove odvojene objekte ponaša kao
# poređenje identiteta. Alias, međutim, upućuje na isti objekat.
assert knjiga_bez_eq_1 != knjiga_bez_eq_2
assert knjiga_bez_eq_1 == alias_knjige_bez_eq
print("Bez __eq__:", knjiga_bez_eq_1 == knjiga_bez_eq_2)


class BookVezba1SaEq:
    def __init__(self, title: str, pages: int) -> None:
        self.title = title
        self.pages = pages

    def __repr__(self) -> str:
        return f"BookVezba1SaEq(title={self.title!r}, pages={self.pages!r})"

    def __eq__(self, other: object) -> bool | NotImplementedType:
        # Za nepodržan tip, NotImplemented dozvoljava Python-u da pokuša
        # poređenje sa druge strane; za dve knjige poredimo polja po vrednosti.
        if not isinstance(other, BookVezba1SaEq):
            return NotImplemented
        return self.title == other.title and self.pages == other.pages


knjiga_sa_eq_1 = BookVezba1SaEq("SQLAlchemy Deep Dive 1", 200)
knjiga_sa_eq_2 = BookVezba1SaEq("SQLAlchemy Deep Dive 1", 200)
knjiga_sa_eq_3 = BookVezba1SaEq("SQLAlchemy Deep Dive 1", 201)

# To su i dalje dva različita objekta, ali ih __eq__ smatra jednakim po poljima.
assert knjiga_sa_eq_1 is not knjiga_sa_eq_2
assert knjiga_sa_eq_1 == knjiga_sa_eq_2
assert knjiga_sa_eq_1 != knjiga_sa_eq_3
print("Sa __eq__:", knjiga_sa_eq_1 == knjiga_sa_eq_2)

# Samostalna klasa koja definiše __eq__ nema automatski hash; Python je
# podrazumevano čini neupotrebljivom kao ključ dict-a ili element set-a.
