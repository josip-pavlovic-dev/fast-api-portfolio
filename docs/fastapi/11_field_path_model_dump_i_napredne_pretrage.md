# FastAPI Stage 1: Field, Path, model_dump i naprednije pretrage

Ovaj materijal je nastavak tvog trenutnog rada u fajlu `books2.py`.
Fokus je na 3 ključne teme:

1. `Field(...)` validacije u Pydantic modelu
2. `Path(...)` validacije path parametara
3. Kreiranje objekta preko `model_dump()`

Na kraju imas i naprednije endpoint primere za pretragu (string metode, kombinovani filteri, sortiranje, paginacija).

---

## 1) Gde si trenutno i šta je dobro

Po tvom kodu već radiš veoma bitne stvari:

- koristiš `BookRequest(BaseModel)` kao ulaznu semu
- validiraš ulaz sa `Field(...)`
- koristiš `Path(gt=0)` za `book_id`
- kreiraš novi objekat sa `Book(**book_request.model_dump())`

To je odličan temelj za sledeći korak: više kontrole nad podacima i napredniji endpoint-i.

---

## 2) `Field(...)` detaljno

`Field(...)` služi da:

- validira vrednost
- dokumentuje API (Swagger)
- postavi default vrednost
- doda metadata opis i primere

Primer iz tvog stila:

```python
from pydantic import BaseModel, Field

class BookRequest(BaseModel):
    id: int | None = Field(default=None, description="ID nije potreban pri kreiranju")
    title: str = Field(min_length=3, max_length=120)
    author: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=5, max_length=300)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(ge=2000, le=2100)
```

### Najcesci argumenti u `Field`

- `default=...` ili direktno `= ...`
- `description="..."`
- `min_length`, `max_length` za string
- `gt`, `ge`, `lt`, `le` za brojeve
- `examples` ili `json_schema_extra` za Swagger primer

### Brzo poređenje

- `gt=0` znači strogo veće od 0
- `ge=0` znači veće ili jednako 0
- `lt=6` znači strogo manje od 6
- `le=6` znači manje ili jednako 6

Ako korisnik pošalje loš payload, FastAPI automatski vraća `422 Unprocessable Entity`.

---

## 3) `Path(...)` detaljno

`Path(...)` koristiš za validaciju parametra koji dolazi iz URL putanje. U suštini, omogućava ti da definišeš ograničenja i dokumentaciju za path parametre.

Primer:

```python
from fastapi import Path

@app.get("/books/{book_id}")
async def read_book(book_id: int = Path(gt=0, description="ID knjige mora biti > 0")):
    ...
```

Ovim postižeš:

- jasnije API ponašanje
- automatsku validaciju
- bolju dokumentaciju u Swagger-u

Napredniji primer:

```python
@app.get("/books/{book_id}")
async def read_book(
    book_id: int = Path(
        ge=1,
        le=1_000_000,
        description="Dozvoljen opseg ID-ja je 1 do 1_000_000"
    )
):
    ...
```

---

## 4) `model_dump()` detaljno: zašto i kako

U Pydantic v2, `model_dump()` je standardni način da model pretvoriš u `dict`.

Tvoj obrazac:

```python
new_book = Book(**book_request.model_dump())
```

Šta se dešava:

1. `book_request` je Pydantic objekat (`BookRequest`)
2. `book_request.model_dump()` vraća rečnik
3. `**` raspakuje rečnik u argumente konstruktora `Book(...)`

Primer:

```python
payload_dict = book_request.model_dump()
# {
#   "id": None,
#   "title": "Nova",
#   "author": "Ana",
#   "description": "Opis...",
#   "rating": 5,
#   "published_date": 2026
# }

new_book = Book(**payload_dict)
```

### Česta praktična varijanta

Kada ne želiš da `None` vrednosti idu dalje:

```python
data = book_request.model_dump(exclude_none=True)
new_book = Book(**data)
```

### Napomena za tvoj slučaj

Kod tebe je `id` opciono polje (default `None`) pri kreiranju. To je okej jer posle dodeljujes ID kroz `find_book_id(...)`.

---

## 5) Važna razlika: klasa `Book` vs `BookRequest`

U tvom kodu:

- `BookRequest` je ulazni DTO (validacija request-a)
- `Book` je interni objekat koji čuvaš u listi

To je dobra praksa jer odvajas:

- kako korisnik šalje podatke
- kako tvoja aplikacija interno čuva podatke

---

## 6) Poboljšan endpoint za kreiranje knjige

Ovde je varijanta bliska tvom stilu, ali sa malo jačom kontrolom:

```python
from fastapi import HTTPException, status

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    data = book_request.model_dump(exclude_none=True)

    new_book = Book(
        id=0,
        title=data["title"],
        author=data["author"],
        description=data["description"],
        rating=data["rating"],
        published_date=data["published_date"],
    )

    new_book = find_book_id(new_book)

    # Primer dodatne biznis validacije: kombinacija title+author treba da bude jedinstvena.
    exists = any(
        b.title.strip().lower() == new_book.title.strip().lower()
        and b.author.strip().lower() == new_book.author.strip().lower()
        for b in BOOKS
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Knjiga sa istim naslovom i autorom vec postoji",
        )

    BOOKS.append(new_book)
    return new_book
```

---

## 7) Naprednije pretrage: string metode i kombinovani filteri

U realnim API-jevima pretraga često uključuje:

- `contains` (sadrži tekst)
- `startswith` (počinje sa)
- `endswith` (završava se na)
- case-insensitive poređenje
- više filtera odjednom
- sortiranje i paginaciju

## 7.1 Pretraga po naslovu i autoru (case-insensitive)

```python
from fastapi import Query

@app.get("/books/search")
async def search_books(
    title: str | None = Query(default=None, min_length=1),
    author: str | None = Query(default=None, min_length=1),
):
    results = BOOKS

    if title:
        title_norm = title.strip().lower()
        results = [b for b in results if title_norm in b.title.lower()]

    if author:
        author_norm = author.strip().lower()
        results = [b for b in results if author_norm in b.author.lower()]

    return results
```

## 7.2 Prefix/suffix pretraga

```python
@app.get("/books/search/pattern")
async def search_books_pattern(
    starts_with: str | None = None,
    ends_with: str | None = None,
):
    results = BOOKS

    if starts_with:
        sw = starts_with.strip().lower()
        results = [b for b in results if b.title.lower().startswith(sw)]

    if ends_with:
        ew = ends_with.strip().lower()
        results = [b for b in results if b.title.lower().endswith(ew)]

    return results
```

## 7.3 Kombinovana pretraga sa opsegom godina i rating-om

```python
@app.get("/books/filter")
async def filter_books(
    min_rating: int | None = Query(default=None, ge=1, le=5),
    max_rating: int | None = Query(default=None, ge=1, le=5),
    published_from: int | None = Query(default=None, ge=2000, le=2100),
    published_to: int | None = Query(default=None, ge=2000, le=2100),
):
    results = BOOKS

    if min_rating is not None:
        results = [b for b in results if b.rating >= min_rating]

    if max_rating is not None:
        results = [b for b in results if b.rating <= max_rating]

    if published_from is not None:
        results = [b for b in results if b.published_date >= published_from]

    if published_to is not None:
        results = [b for b in results if b.published_date <= published_to]

    return results
```

## 7.4 Sortiranje + paginacija

```python
@app.get("/books/advanced")
async def advanced_books(
    sort_by: str = Query(default="id", pattern="^(id|title|rating|published_date)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    results = BOOKS[:]

    reverse = sort_order == "desc"

    if sort_by == "id":
        results.sort(key=lambda b: b.id, reverse=reverse)
    elif sort_by == "title":
        results.sort(key=lambda b: b.title.lower(), reverse=reverse)
    elif sort_by == "rating":
        results.sort(key=lambda b: b.rating, reverse=reverse)
    else:
        results.sort(key=lambda b: b.published_date, reverse=reverse)

    return {
        "total": len(results),
        "skip": skip,
        "limit": limit,
        "items": results[skip : skip + limit],
    }
```

## 7.5 Pretraga sa tokenima (svaka reč mora da postoji)

```python
@app.get("/books/search/fulltext-lite")
async def search_fulltext_lite(q: str = Query(min_length=2)):
    tokens = [t.lower() for t in q.strip().split() if t.strip()]

    def matches(book: Book) -> bool:
        haystack = f"{book.title} {book.author} {book.description}".lower()
        return all(token in haystack for token in tokens)

    return [b for b in BOOKS if matches(b)]
```

Ovaj pristup je odličan prelaz ka pravom full-text search-u u bazi kasnije.

---

## 8) Kada koristiti `Query`, a kada `Path`

- `Path`: deo URL putanje (npr. `/books/{book_id}`)
- `Query`: opcioni ili filter parametri (npr. `/books/search?title=fastapi`)

Tipičan obrazac:

- identifikator resursa (`book_id`) ide u `Path`
- kriterijumi pretrage idu u `Query`

---

## 9) Česte greške u ovoj fazi

1. Mešanje tipova u listi `BOOKS`:
   Kod tebe `BOOKS` čuva `Book` objekte. Zato u update/delete logici pazi da ne upišeš dict ili Pydantic model direktno.

2. Nepostojeći zapis:
   Za "not found" je bolje `HTTPException(404)` nego `{"error": ...}` jer daje standardan HTTP odgovor.

3. Konflikt ruta:
   Istovremeno korišćenje `/books` i `/books/` može da unese zabunu. Drži jedan jasan stil ruta.

4. Validation boundaries:
   Ako je `rating` od 1 do 5, koristi svuda isti opseg (`ge=1, le=5`) radi konzistentnosti.

---

## 10) Mini zadaci za vežbu

1. Napravi endpoint `/books/search/author-prefix` koji vraća knjige gde autor počinje zadatim stringom.
2. Napravi endpoint `/books/search/title-or-description` koji traži token u naslovu ILI opisu.
3. Dodaj `published_from` i `published_to` u postojeći rating endpoint.
4. Napravi endpoint koji vraća samo top N knjiga po rating-u, pa po godini objave.
5. Za svaki endpoint koji traži jedan zapis po ID-u uvedi `HTTPException(404)`.

---

## 11) Sledeći korak posle ovog materijala

Kada savladaš ove pretrage u listi, sledeća prirodna etapa je SQLAlchemy + baza:

- iste filtere prebacuješ na DB upite
- dobijaš efikasnost na velikim skupovima podataka
- lakše radiš paginaciju i sortiranje

Do tada je ovaj nivo više nego dovoljan da postaviš jaku logiku endpoint-a i validacije u FastAPI.
