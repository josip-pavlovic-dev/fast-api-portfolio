# Pydantic cheat sheet za FastAPI (po težinama)

Ovaj cheat sheet je napravljen za nivo koji si trenutno imao: početak sa FastAPI-jem, `BaseModel`, validacije, `response_model`, i bez baza. Fokus je na razumevanju, ne na “gotovom copy/paste” kodu.

---

## 1) Šta je Pydantic?

Pydantic je biblioteka za:

- validaciju podataka
- konverziju podataka u željeni tip
- definisanje strukture modela
- automatsko proveravanje ulaza i izlaza

Najviše je poznat u FastAPI-u, ali se koristi i van njega.

Osnovna ideja:

```python
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str
    pages: int
```

Ako dobijemo:

```python
Book(title="Python", author="Marko", pages=300)
```

to prođe.

Ako dobijemo:

```python
Book(title=123, author="Marko", pages="300")
```

Pydantic će pokušati da konvertuje podatke, a ako ne može — baci grešku.

---

## 2) Zašto je Pydantic važan u FastAPI?

FastAPI ume da radi sa Pydantic modelima na dva glavna načina:

1. Za prihvatanje zahteva (`request`/`body`)
2. Za definisanje odgovora (`response_model`)

Primer:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str

class BookResponse(BaseModel):
    id: int
    title: str
    author: str

@app.post("/books", response_model=BookResponse)
def create_book(book: BookCreate):
    return {
        "id": 1,
        "title": book.title,
        "author": book.author,
    }
```

Ovo znači:

- `BookCreate` opisuje što klijent šalje
- `BookResponse` opisuje što server vraća
- FastAPI automatski validira (proverava tipove i strukturu) i serijalizuje (pretvara u JSON) podatke.

---

## 3) Pydantic model = struktura podataka

Model je klasa koja nasledjuje `BaseModel`.

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    email: str
```

Sada možemo napraviti objekat:

```python
user = User(id=1, username="petar", email="petar@example.com")
print(user.username)
```

Pydantic automatski kreira atributе i validira tipove.

---

# TEŽINA 1: POČETNI NIVOE

## 3.1 Osnovni tipovi

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    is_student: bool
    height: float
```

### Primer

```python
p = Person(name="Ana", age=25, is_student=True, height=1.72)
print(p)
```

### Šta se dešava ako pošalješ pogrešan tip?

```python
Person(name="Ana", age="25", is_student="True", height="1.72")
```

Pydantic će pokušati da konvertuje, ali ako je šema jača i ne može, baciće grešku.

---

## 3.2 Optional polja

`Optional` znači: polje može da postoji, ali može da bude `None`.

```python
from typing import Optional
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
```

Znači:

- `title` obavezno
- `author` obavezno
- `description` opciono
- ako nedostaje, koristi se `None`

### Primer

```python
book1 = Book(title="Python", author="Marko")
book2 = Book(title="Python", author="Marko", description="Dobar uvod")
```

I to je potpuno validno.

### Pitanje koje često zbuni:

```python
description: str | None = None
```

To je moderni Python zapis za isto što i:

```python
from typing import Optional
description: Optional[str] = None
```

U Python 3.10+ radi oba.

---

## 3.3 Default vrednosti

```python
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str
    description: str = "Nema opis"
```

Ako ne pošalješ `description`, Pydantic će ga postaviti na default:

```python
Book(title="Python", author="Marko")
```

Rezultat:

```python
Book(title='Python', author='Marko', description='Nema opis')
```

---

## 3.4 Modeli za ulaz i izlaz

Najčešći obrazac u FastAPI:

```python
class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str | None = None
```

### Zašto je ovo dobro?

- `BookCreate` opisuje podatke koje klijent šalje
- `BookResponse` opisuje podatke koje server vraća
- ne mešamo strukture ulaza i izlaza

---

## 3.5 Lista podataka

```python
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str

class Library(BaseModel):
    books: list[Book]
```

Primer:

```python
library = Library(
    books=[
        {"title": "Python", "author": "Marko"},
        {"title": "FastAPI", "author": "Ana"},
    ]
)
```

Ovo je veoma korisno za JSON response koji sadrži listu objekata.

---

## 3.6 Nested modeli

Pydantic radi i sa ugnežđenim objektima.

```python
from pydantic import BaseModel

class Author(BaseModel):
    name: str
    country: str

class Book(BaseModel):
    title: str
    author: Author
```

Primer:

```python
book = Book(
    title="Python za početnike",
    author={"name": "Marko", "country": "Srbija"}
)
```

Pydantic će automatski konvertovati rečnik u `Author` model.

---

## 3.7 `Field` za dodatna ograničenja

Ako želiš više kontrolе nad poljem, koristi `Field`.

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    age: int = Field(..., ge=0, le=120)
```

### Objašnjenje:

- `...` znači obavezno
- `min_length` minimalna dužina stringa
- `max_length` maksimalna dužina
- `ge` greater than or equal
- `le` less than or equal

Primer:

```python
User(username="pe", age=30)
```

Ovo će baciti grešku jer je username prekratak.

---

# TEŽINA 2: SREDNJI NIVOI

## 4.1 Validatori (`@validator`)

Kada želiš dodatnu custom validaciju, koristi `@validator`.

```python
from pydantic import BaseModel, validator

class User(BaseModel):
    username: str
    email: str

    @validator("email")
    def validate_email(cls, value):
        if "@" not in value:
            raise ValueError("Email mora sadržati @")
        return value
```

Primer:

```python
User(username="ana", email="ana.gmail.com")
```

baciće grešku.

### Zašto je ovo korisno?

Jer ne možeš da validiraš sve samo tipovima. Ponekad moraš custom pravilo.

---

## 4.2 Validatori na više polja

```python
from pydantic import BaseModel, validator

class User(BaseModel):
    username: str
    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, value, values):
        if "password" in values and value != values["password"]:
            raise ValueError("Lozinke se ne poklapaju")
        return value
```

### Primer korišćenja

```python
User(
    username="ana",
    password="secret123",
    confirm_password="secret456"
)
```

baciće grešku.

---

## 4.3 `EmailStr`, `HttpUrl`, `PositiveInt`, `constr`, `conint`

Pydantic ima specijalne tipove za često korišćene vrednosti.

```python
from pydantic import BaseModel, EmailStr, HttpUrl

class Contact(BaseModel):
    email: EmailStr
    website: HttpUrl
```

### Primer

```python
Contact(
    email="ana@example.com",
    website="https://example.com"
)
```

### `constr`

```python
from pydantic import BaseModel, constr

class User(BaseModel):
    username: constr(min_length=3, max_length=20)
```

### `conint`

```python
from pydantic import BaseModel, conint

class Product(BaseModel):
    quantity: conint(gt=0)
```

Ovo znači:

- `quantity` mora biti ceo broj
- veći od 0

---

## 4.4 `Enum` sa Pydantic modelima

```python
from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(BaseModel):
    status: Status
```

Primer:

```python
User(status="active")
```

radi.

```python
User(status="deleted")
```

ne radi, jer nije u `Enum`-u.

---

## 4.5 `Union` i `Literal`

### `Union`

```python
from typing import Union
from pydantic import BaseModel

class Item(BaseModel):
    value: Union[int, str]
```

Ovo znači da `value` može biti integer ili string.

### `Literal`

```python
from typing import Literal
from pydantic import BaseModel

class User(BaseModel):
    role: Literal["admin", "user", "guest"]
```

Samo određene vrednosti su validne.

---

## 4.6 Model config i JSON ponašanje

Pydantic ima `ConfigDict` ili `class Config` (zavisi od verzije i stila).

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
```

### Primer kada se koristi

Kada radimo sa SQLAlchemy modelima ili objecima koji nisu obični dict.

---

## 4.7 `response_model` u FastAPI

Najvažnije u FastAPI-u:

```python
@app.get("/books", response_model=list[BookResponse])
async def get_books():
    return books
```

### Važno:

Ovo je ISPRAVNO:

```python
response_model=list[BookResponse]
```

Ovo je NETAČNO:

```python
response_model=[BookResponse]
```

Zato što je `[BookResponse]` obična Python lista, a ne validan Pydantic tip.

To je upravo tip greške koju si imao:

```python
FastAPIError: Invalid args for response field!
```

---

## 4.8 `response_model=None`

Ponekad želiš da FastAPI ne generiše model iz tipa povratne vrednosti.

```python
@app.get("/items", response_model=None)
def get_items():
    return {"message": "raw dict"}
```

Koristi se kada:

- vraćaš dict koji ne odgovara šemi
- vraćaš posebno formatiran JSON
- želiš ručno da definišeš response

---

# TEŽINA 3: NAPREDNI NIVOI

## 5.1 `root_validator` i `model_validator`

Stari način:

```python
from pydantic import BaseModel, root_validator

class User(BaseModel):
    username: str
    password: str
    confirm_password: str

    @root_validator
    def check_passwords_match(cls, values):
        if values.get("password") != values.get("confirm_password"):
            raise ValueError("Lozinke se ne poklapaju")
        return values
```

U novijem Pydantic-u koristi se `model_validator`.

```python
from pydantic import BaseModel, model_validator

class User(BaseModel):
    username: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Lozinke se ne poklapaju")
        return self
```

---

## 5.2 `computed_field`

Možeš napraviti polja koja se računaju automatski.

```python
from pydantic import BaseModel, computed_field

class Person(BaseModel):
    first_name: str
    last_name: str

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

Rezultat:

```python
Person(first_name="Ana", last_name="Markovic").model_dump()
```

daje:

```python
{'first_name': 'Ana', 'last_name': 'Markovic', 'full_name': 'Ana Markovic'}
```

---

## 5.3 `model_dump()` i `model_validate()`

Pydantic 2 koristi `model_dump()` umesto starog `dict()`.

```python
user = User(username="ana", age=25)
print(user.model_dump())
```

### Validacija iz postojećeg objekta

```python
from pydantic import TypeAdapter

adapter = TypeAdapter(list[int])
print(adapter.validate_python([1, 2, 3]))
```

To je veoma korisno kada ne želiš da praviš poseban model.

---

## 5.4 `Alias` i `populate_by_name`

Ako želiš da polja imaju drugi naziv u JSON-u:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    user_name: str = Field(alias="username")
```

Primer:

```python
User.model_validate({"username": "ana"})
```

radi, iako atribut je `user_name`.

---

## 5.5 Validacija složenih struktura

```python
from pydantic import BaseModel

class Address(BaseModel):
    city: str
    postal_code: str

class Customer(BaseModel):
    name: str
    address: Address
```

Ovo je osnovni model za ozbiljnije API-je.

---

## 5.6 Ako podaci nisu savršeni

Pydantic može da radi sa različitim tipovima, ali treba znati šta će se dogoditi.

```python
from pydantic import BaseModel

class User(BaseModel):
    age: int
```

Ovo je validno:

```python
User(age="25")
```

Pydantic će konvertovati string u int.

Ali ovo nije validno:

```python
User(age="neki tekst")
```

jer ne može da konvertuje string u int.

---

# 6) Najčešće greške i kako ih prepoznati

## Greška 1: `response_model=[BookResponse]`

```python
@app.get("/books", response_model=[BookResponse])
```

### Zašto?

Pošto je ovo Python lista, a ne tip modela.

### Kako treba?

```python
@app.get("/books", response_model=list[BookResponse])
```

---

## Greška 2: `book.get(id)` umesto `book.get("id")`

```python
if book.get(id) == book_id:
```

`id` je Python funkcija, ne ključ u rečniku.

### Ispravno:

```python
if book.get("id") == book_id:
```

ili:

```python
if book["id"] == book_id:
```

---

## Greška 3: nedostajuća polja

```python
class Book(BaseModel):
    title: str
    author: str
    description: str | None = None
```

Ako pošalješ:

```python
{"title": "Python"}
```

dobijaš grešku, jer `author` nedostaje.

---

## Greška 4: pogrešan tip

```python
class Product(BaseModel):
    price: int
```

Ako pošalješ:

```python
{"price": "10.99"}
```

Pydantic će možda pokušati da konvertuje, ali ne uvek će moći.

---

# 7) FastAPI + Pydantic obrazac koji trebaš da znaš

## Obrazac 1: GET - list

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str

books = [
    {"id": 1, "title": "Python", "author": "Marko"}
]

@app.get("/books", response_model=list[Book])
def get_books():
    return books
```

---

## Obrazac 2: POST - ulazni model

```python
class BookCreate(BaseModel):
    title: str
    author: str

@app.post("/books", response_model=Book)
def create_book(book: BookCreate):
    new_book = {
        "id": 2,
        "title": book.title,
        "author": book.author,
    }
    return new_book
```

---

## Obrazac 3: GET po ID

```python
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    return {"id": book_id, "title": "Python", "author": "Marko"}
```

---

# 8) Brzi pregled tipova

## Najčešći tipovi

```python
str
int
float
bool
list[str]
list[int]
dict[str, str]
Optional[str]
str | None
```

## Najčešći Pydantic modeli

```python
BaseModel
Field
validator
EmailStr
HttpUrl
constr
conint
Literal
Enum
```

---

# 9) Kratka pravila za pamćenje

1. `BaseModel` koristiš za definisanje strukture podataka.
2. `Optional` ili `| None` = polje je opciono.
3. `Field(...)` = obavezno polje sa dodatnim ograničenjima.
4. `response_model` mora biti Pydantic tip, ne obična lista sa tipom.
5. `list[Model]` je ispravno za listu objekata.
6. `validator` koristiš za custom pravila.
7. `nested models` i `list[Model]` su osnovni alati za API.
8. Pydantic je najvažniji deo FastAPI validacije i serijalizacije.

---

# 10) Mini “mentalni model”

Ako želiš da razmišljaš jednostavno:

- Pydantic je “štit” između klijenta i servera
- serveru kaže: “Ovo možeš da primiš”
- klijentu kaže: “Ovo ćeš dobiti”
- FastAPI to automatski koristi za API

To je razlog što je Pydantic toliko bitan u modernom Python web razvoju.

---

# 11) Dodatni zadaci za vežbanje

## Zadatak 1

Napravi model `Movie` sa poljima:

- title: str
- director: str
- year: int
- rating: float | None = None

## Zadatak 2

Napravi model `User` sa:

- username: str
- email: EmailStr
- age: int = Field(..., ge=0, le=120)

## Zadatak 3

Napravi model `Order` sa:

- item: str
- quantity: int
- status: Literal["pending", "paid", "shipped"]

## Zadatak 4

Napravi FastAPI endpoint:

- GET /movies -> vraća listu filmova
- POST /movies -> prima `MovieCreate` i vraća `Movie`

## Zadatak 5

Napravi validator koji proverava da `year` ne bude u futuru.

---

# 12) Preporuka za dalji tok učenja

Preporuka je da nastaviš ovim redosledom:

1. `BaseModel`
2. `Optional` i default vrednosti
3. `Field` restrikcije
4. `list[Model]` i nested models
5. `response_model` u FastAPI
6. `@validator`
7. `Enum`, `Literal`, `Union`
8. `model_dump` i naprednije validacije
9. tek posle toga baze i SQLAlchemy

To je prirodan redosled za razumijevanje Pydantic-a bez preopterećenja.

---

## Zaključak

Pydantic nije samo “dodatni modul”, nego jedna od ključnih stvari koja čini FastAPI moćnim.

On ti daje:

- bezbednost podataka
- jasnu strukturu modela
- validaciju ulaza i izlaza
- bolju dokumentaciju i jednostavnije API-ove

Ako razumeš Pydantic, razumeš i srž FastAPI-ja.

---

Ako želiš, mogu odmah da ti napravim i:

1. jedan “mini PDF/cheat sheet” u kraćem formatu za štampu,
2. jedan praktični primer sa knjigama i CRUD-om,
3. ili dodatni file sa “Pydantic + FastAPI najčešće greške i koraci za debug”.
