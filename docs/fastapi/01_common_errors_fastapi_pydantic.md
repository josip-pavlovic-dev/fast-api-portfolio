# Najčešće greške u FastAPI + Pydantic

Ovaj file je napravljen da ti pomogne da brzo prepoznaš i razumeš najčešće probleme koje se pojavljuju u početku rada sa FastAPI-jem i Pydantic-om.

Cilj nije da ti daš “gotov fix”, nego da ti pokaže šta je tačno u pitanju i zašto se greška javlja.

---

## 1) Greška: `Invalid args for response field!`

### Primer

```python
@app.get("/books", response_model=[BookResponse])
async def get_books():
    return books
```

### Šta je problem?

`response_model` mora da bude validan Pydantic tip, a ne obična Python lista koja sadrži model.

Ovo je pogrešno:

```python
[BookResponse]
```

Ovo je ispravno:

```python
list[BookResponse]
```

### Zašto?

FastAPI očekuje da mu prosledi tip modela koji opisuje format odgovora.

`[BookResponse]` je jednostavno Python lista, a ne `Type` koji Pydantic zna da validira.

### Ispravno rešenje

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class BookResponse(BaseModel):
    id: int
    title: str
    author: str

@app.get("/books", response_model=list[BookResponse])
async def get_books():
    return [
        {"id": 1, "title": "Python", "author": "Marko"},
        {"id": 2, "title": "FastAPI", "author": "Ana"},
    ]
```

---

## 2) Greška: `book.get(id)` umesto `book.get("id")`

### Primer greške

```python
for book in books:
    if book.get(id) == book_id:
        return book
```

### Problem

`id` je Python funkcija built-in, ne ključ u rečniku.

### Ispravno

```python
for book in books:
    if book.get("id") == book_id:
        return book
```

ili:

```python
for book in books:
    if book["id"] == book_id:
        return book
```

### Zašto je ovo važno?

U Python-u `id` je funkcija koja vraća jedinstveni identifikator objekta, a ne string ključ u dict-u.

---

## 3) Greška: nedostajući polja u modelu

### Primer

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

Pydantic će baciti grešku, jer `author` je obavezno polje.

### Ispravno

```python
{"title": "Python", "author": "Marko"}
```

### Učenje

Pydantic ne “pretpostavlja” polja. Ako je polje obavezno, mora da postoji.

---

## 4) Greška: pogrešan tip podataka

### Primer

```python
class Product(BaseModel):
    price: int
```

Ako pošalješ:

```python
{"price": "10.99"}
```

Pydantic će pokušati da konvertuje, ali ako ne može — baca grešku.

### Pravilo

- `int` očekuje ceo broj
- `float` očekuje decimalni broj
- `str` očekuje string
- `bool` očekuje True/False

---

## 5) Greška: `response_model` za jedan objekat vs listu

### Pogrešno

```python
@app.get("/books/{book_id}", response_model=[BookResponse])
```

### Ispravno

```python
@app.get("/books/{book_id}", response_model=BookResponse)
```

### Pravilo

- jedan objekat => `response_model=BookResponse`
- lista objekata => `response_model=list[BookResponse]`

---

## 6) Greška: `Body`/`Form`/`Query` se ne koriste pravilno

U FastAPI-u su najčešći načini:

- `Query` => parametri u URL-u
- `Path` => path parametri
- `Body` => JSON telo

### Primer

```python
@app.post("/books")
async def create_book(book: BookCreate):
    return book
```

Ovo je normalno ako `BookCreate` dolazi u JSON body-ju.

Ali ako ti treba query param:

```python
@app.get("/books")
async def get_books(limit: int = Query(10)):
    return {"limit": limit}
```

### Zašto je ovo važno?

Ako ne znaš da li je podatak u URL-u ili u body-ju, lako napraviš pogrešan endpoint.

---

## 7) Greška: `HTTPException` se koristi pogrešno

### Primer

```python
raise HTTPException(status_code=404)
```

Ovo je validno, ali bez detalja korisniku nije baš jasno šta se dogodilo.

### Bolje

```python
raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

### Zašto?

Korisnik treba da zna šta se dogodilo, a ne samo da postoji HTTP 404.

---

## 8) Greška: modeli ne odražavaju stvarni odgovor

### Primer

```python
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
```

ali endpoint vraća:

```python
return {"id": 1, "title": "Python", "author": "Marko", "created_at": "2026-09-15"}
```

### Problem

`created_at` je dodatno polje koje model ne očekuje.

FastAPI ga često filtrira, ali može da zbuni ako ne znaš da li je odgovor tačno definisan.

### Pravilo

Model odgovora treba da odražava točno ono što endpoint vraća.

---

## 9) Greška: suviše komplikovan model bez potrebe

Ponekad počneš da praviš model sa mnogo polja previše rano.

Primer:

```python
class BookFull(BaseModel):
    id: int
    title: str
    author: str
    description: str | None
    year: int
    pages: int
    rating: float
    isbn: str
    category: str
```

Ako ti u trenutnom trenutku treba samo:

```python
id, title, author
```

onda je bolje da prvi put napraviš jednostavan model.

### Učenje

Započni jednostavno, pa dodaj polja tek kada im stvarno treba.

---

## 10) Greška: `None` se koristi kao “nema validaciju”

### Primer

```python
description: str = None
```

To nije isto što i:

```python
description: str | None = None
```

U Python-u i Pydantic-u treba da bude eksplicitno jasno da je polje opciono.

### Preporuka

Koristi:

```python
description: str | None = None
```

ili

```python
from typing import Optional

description: Optional[str] = None
```

---

## 11) Najčešća praksa koja pomaže

### Kada praviš API, idi ovim redosledom:

1. Definiši model za ulaz (`Create`)
2. Definiši model za izlaz (`Response`)
3. Poveži endpoint sa `response_model`
4. Dodaj `status_code` gde treba
5. Koristi `HTTPException` za greške
6. Testiraj sa realnim JSON-om

---

## 12) Mini primer svih najčešćih elemenata zajedno

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str | None = None

books = [
    {"id": 1, "title": "Python", "author": "Marko", "description": None}
]

@app.get("/books", response_model=list[BookResponse])
async def get_books():
    return books

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")

@app.post("/books", response_model=BookResponse)
async def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
        "description": book.description,
    }
    books.append(new_book)
    return new_book
```

Ovo je veoma dobar “reference pattern” za početak.

---

## 13) Šta treba da pamtiš

### Najbitnije pravilo

- `response_model` mora biti validan Pydantic model tip
- `list[BookResponse]` je ispravno
- `[BookResponse]` je pogrešno
- `id` u dict-u mora da se pristupa kao `"id"`
- `Optional` / `| None` znači da polje može da bude prazno
- `HTTPException` je način da vraćaš 404/400/422 i slično

---

## 14) Dobar način za učenje

Umesto da pamtiš “na slepo” sve ovo, radi ovako:

1. napiši model
2. probaj da proslediš pogrešan tip
3. vidiš koju grešku Pydantic baca
4. popraviš model i ponoviš

Na taj način ćeš razumeti logiku, a ne samo error message.

---

## 15) Kraj

Najvažnija stvar je da razumeš da su Pydantic i FastAPI povezani:

- Pydantic validira podatke
- FastAPI koristi tu validaciju za API request i response

Ako razumeš ovo, već si u dobrom delu putanje ka ozbiljnijem backend razvoju.

---

Ako želiš, nastavićemo sa sledećim temama:

- `status_code`
- `HTTPException`
- `POST/PUT/DELETE`
- `CRUD model`

i sve to ćemo obraditi kroz praktične primere sa knjigama.
