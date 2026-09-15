# CRUD praksa 01: GET i POST

Ovo je prvi pravi praktični korak.

Cilj: napraviti API za knjige koji:

- vraća sve knjige
- dodaje novu knjigu

Bez komplikovanih detalja. Samo osnovni CRUD oblik.

---

## 1) Početni model

```python
from fastapi import FastAPI
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
    {"id": 1, "title": "Python za početnike", "author": "Marko", "description": None},
    {"id": 2, "title": "FastAPI uvod", "author": "Ana", "description": "Osnovni uvod"},
]
```

---

## 2) `GET /books`

```python
@app.get("/books", response_model=list[BookResponse])
async def get_books():
    return books
```

### Šta je tu važno?

- endpoint vraća listu knjiga
- `response_model=list[BookResponse]` znači da će odgovor biti validiran prema modelu
- sve knjige moraju imati `id`, `title`, `author`, `description`

---

## 3) `POST /books`

```python
@app.post("/books", response_model=BookResponse, status_code=201)
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

### Šta se dešava?

- klijent šalje JSON u telu zahteva
- FastAPI validira podatke prema `BookCreate`
- pravi se novi objekat
- vraća se `new_book`

---

## 4) Kompletan prvi primer

```python
from fastapi import FastAPI
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
    {"id": 1, "title": "Python za početnike", "author": "Marko", "description": None},
    {"id": 2, "title": "FastAPI uvod", "author": "Ana", "description": "Osnovni uvod"},
]

@app.get("/books", response_model=list[BookResponse])
async def get_books():
    return books

@app.post("/books", response_model=BookResponse, status_code=201)
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

---

## 5) Testiranje

### 1. GET /books

Poziv:

```http
GET /books
```

Očekivani odgovor:

```json
[
  {
    "id": 1,
    "title": "Python za početnike",
    "author": "Marko",
    "description": null
  },
  {
    "id": 2,
    "title": "FastAPI uvod",
    "author": "Ana",
    "description": "Osnovni uvod"
  }
]
```

### 2. POST /books

Poziv:

```http
POST /books
```

Telo zahteva:

```json
{
  "title": "Django za početnike",
  "author": "Petar",
  "description": "Novi uvod"
}
```

Očekivani rezultat:

```json
{
  "id": 3,
  "title": "Django za početnike",
  "author": "Petar",
  "description": "Novi uvod"
}
```

---

## 6) Najčešće greške u ovoj fazi

### Greška 1: zaboravljeno `response_model`

Ukoliko nemaš `response_model`, FastAPI neće automatski validirati odgovor.

### Greška 2: pogrešan tip polja

```python
title: int
```

To će baciti validacionu grešku ako klijent pošalje string.

### Greška 3: `description` bez default vrednosti

Ako je polje `description: str`, onda mora da postoji u svakom zahtevu.

To je pogrešno ako želiš opcionalno polje.

### Ispravno:

```python
description: str | None = None
```

---

## 7) Šta treba da zapišeš kao uvid

Nakon svakog testiranja napiši 3-5 rečenica:

- Šta radi `GET /books`?
- Šta radi `POST /books`?
- Šta je `response_model`?
- Šta znači `status_code=201`?

---

## 8) Sledeći korak

U sledećem fajlu dodajemo:

- `GET /books/{book_id}`
- `HTTPException`
- `404 Not Found`

To je prvi pravi “resurs po ID” korak.
