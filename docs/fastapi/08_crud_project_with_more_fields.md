# CRUD projekat sa više polja i boljom strukturom

Ovo je verzija koja pokazuje razliku između jednostavnog CRUD primera i malo ozbiljnijeg API modela.

U prethodnoj verziji imao si samo:

- id
- title
- author
- description

Sada dodajemo više polja kako bi se video pravi “real-world” API stil.

---

## 1) Šta je drugačije?

U novom modelu imamo:

- `id`
- `title`
- `author`
- `description`
- `price`
- `year`
- `genre`
- `available`
- `rating`

Ovo je već bliže realnom proizvodu ili knjizi u aplikaciji.

---

## 2) Finalni primer

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None
    price: float
    year: int
    genre: str
    available: bool = True
    rating: float | None = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str | None = None
    price: float
    year: int
    genre: str
    available: bool
    rating: float | None = None


books: list[dict] = [
    {
        "id": 1,
        "title": "Python za početnike",
        "author": "Marko",
        "description": "Dobar uvod u Python",
        "price": 19.99,
        "year": 2024,
        "genre": "programming",
        "available": True,
        "rating": 4.8,
    },
    {
        "id": 2,
        "title": "FastAPI uvod",
        "author": "Ana",
        "description": "API tutorial",
        "price": 24.50,
        "year": 2025,
        "genre": "backend",
        "available": True,
        "rating": 4.9,
    },
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


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "price": book.price,
        "year": book.year,
        "genre": book.genre,
        "available": book.available,
        "rating": book.rating,
    }
    books.append(new_book)
    return new_book


@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookCreate):
    for index, existing_book in enumerate(books):
        if existing_book["id"] == book_id:
            updated_book = {
                "id": book_id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "price": book.price,
                "year": book.year,
                "genre": book.genre,
                "available": book.available,
                "rating": book.rating,
            }
            books[index] = updated_book
            return updated_book

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")


@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            deleted_book = books.pop(index)
            return {
                "message": "Knjiga je obrisana",
                "deleted_book": deleted_book,
            }

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

---

## 3) Razlika u odnosu na jednostavni CRUD

### Jednostavno verzija

```python
class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None
```

### Naprednija verzija

```python
class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None
    price: float
    year: int
    genre: str
    available: bool = True
    rating: float | None = None
```

### Šta to znači?

- jednostavan model je dobar za učenje logike
- napredniji model je bliži realnoj aplikaciji
- više polja = veća kompleksnost, ali i realističniji API

---

## 4) Primer POST zahteva sa više polja

```json
{
  "title": "Django za početnike",
  "author": "Petar",
  "description": "Knjiga o Django framework-u",
  "price": 29.9,
  "year": 2026,
  "genre": "backend",
  "available": true,
  "rating": 4.7
}
```

Ovo su podaci koje API očekuje.

---

## 5) Primer odgovora

```json
{
  "id": 3,
  "title": "Django za početnike",
  "author": "Petar",
  "description": "Knjiga o Django framework-u",
  "price": 29.9,
  "year": 2026,
  "genre": "backend",
  "available": true,
  "rating": 4.7
}
```

---

## 6) Kako dalje da vežbaš?

Pokušaj da promeniš ovaj primer na sledeći način:

1. dodaj polje `publisher: str`
2. dodaj polje `pages: int`
3. dodaj validaciju da `year` mora biti > 1900
4. dodaj validaciju da `price` mora biti > 0
5. dodaj `PATCH` endpoint

---

## 7) Šta je najvažnije da zapamtiš?

U realnom API-ju često imaš više polja, ali logika ostaje ista:

- `BookCreate` = šta klijent šalje
- `BookResponse` = šta server vraća
- `GET` -> pročitaj
- `POST` -> kreiraj
- `PUT` -> izmeni
- `DELETE` -> obriši
- `response_model` -> validacija izlaza
- `HTTPException` -> greške

---

## 8) Zaključak

Jednostavna verzija je dobar start za razumevanje FastAPI-ja.

Naprednija verzija pokazuje kako API postaje bliži realnim projektima:

- više polja
- bolja struktura
- jasniji response model
- realniji JSON objekti

To je upravo ono što treba da vidiš da bi shvatio razliku između “mini primera” i “realnog API projekta”.
